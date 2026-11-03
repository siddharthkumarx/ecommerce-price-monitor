from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

import pytest

from pricemon import sheets

GOLDEN = Path(__file__).parent / "fixtures" / "golden"


def test_skips_cleanly_without_secret(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str], tmp_path: Path
) -> None:
    monkeypatch.delenv("GOOGLE_SA_JSON", raising=False)
    monkeypatch.delenv("GOOGLE_SHEET_ID", raising=False)
    assert sheets.main(["--data", str(tmp_path)]) == 0
    assert "skipped: GOOGLE_SA_JSON, GOOGLE_SHEET_ID not set" in capsys.readouterr().out


def test_failure_does_not_print_the_credential(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str], tmp_path: Path
) -> None:
    monkeypatch.setenv("GOOGLE_SA_JSON", '{"private_key": "SECRET-VALUE"}')
    monkeypatch.setenv("GOOGLE_SHEET_ID", "sheet")

    def boom(*args: object) -> None:
        raise RuntimeError("SECRET-VALUE leaked?")

    monkeypatch.setattr(sheets, "publish", boom)
    assert sheets.main(["--data", str(tmp_path), "--stores", str(tmp_path / "none.yml")]) == 1
    assert "SECRET-VALUE" not in capsys.readouterr().out


def test_latest_table_from_golden_snapshot() -> None:
    table = sheets.latest_table(
        GOLDEN / "snapshot_after_run2.csv", {"a": ("Alpha", "alpha.example")}
    )
    assert table[0][:4] == ["store", "product", "variant", "price_usd"]
    assert table[1] == [
        "Alpha",
        "Tee (organic)",
        "V1",
        "22.40",
        "28.00",
        "true",
        "https://alpha.example/products/tee",
        "2026-11-05T06:17:00Z",
    ]
    assert table[4][0] == "b"  # unknown store falls back to its id


def test_changes_table_window(tmp_path: Path) -> None:
    day = tmp_path / "changes" / "2026"
    day.mkdir(parents=True)
    header = ",".join(
        [
            "observed_at",
            "store_id",
            "product_id",
            "variant_id",
            "handle",
            "product_title",
            "variant_title",
            "event",
            "old_price_cents",
            "new_price_cents",
            "old_compare_at_cents",
            "new_compare_at_cents",
            "price_change_pct",
        ]
    )
    (day / "2026-09-01.csv").write_text(header + "\n2026-09-01T06:17:00Z,a,1,1,t,T,V,new,,100,,,\n")
    (day / "2026-11-04.csv").write_text(
        header + "\n2026-11-04T06:17:00Z,a,1,1,t,T,V,price_down,200,100,,,-50.0\n"
    )
    rows = sheets.changes_table(tmp_path, datetime(2026, 11, 5, tzinfo=UTC))
    assert len(rows) == 2
    assert rows[1][4:] == ["price_down", "2.00", "1.00", "-50.0"]
