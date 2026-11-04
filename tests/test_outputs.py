from __future__ import annotations

import json
import time
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import pytest
import yaml

from pricemon.fetch import StoreFetch, WitnessResult
from pricemon.outputs import build_status, read_runs, snapshot_summary
from pricemon.run import EXIT_HELD, EXIT_OK, EXIT_PARTIAL, RunConfig, process
from pricemon.schedule import BFCM_EXTRA_CRONS, CRONS, active_crons, missed_slots, slots

ROOT = Path(__file__).resolve().parents[1]
DAY1 = datetime(2026, 11, 4, 6, 17, tzinfo=UTC)
DAY2 = datetime(2026, 11, 5, 6, 17, tzinfo=UTC)


def product(pid: int, prices: list[tuple[int, str, str | None, bool]]) -> dict[str, Any]:
    return {
        "id": pid,
        "handle": f"p{pid}",
        "title": f"Product {pid}",
        "product_type": "Gear",
        "tags": [],
        "variants": [
            {"id": vid, "title": "Default", "price": p, "compare_at_price": c, "available": a}
            for vid, p, c, a in prices
        ],
    }


def fetched(
    store: str,
    products: list[dict[str, Any]],
    at: datetime,
    status: str = "ok",
    currency: str = "USD",
) -> StoreFetch:
    f = StoreFetch(store_id=store, host=f"{store}.example", observed_at=at, products=products)
    f.status = status  # type: ignore[assignment]
    f.witnesses = [
        WitnessResult(product_id=1, handle="p1", js="match", jsonld="match", currencies=[currency])
    ]
    if status != "ok":
        f.reason = "blocked: http 403"
        f.products = []
    return f


def catalog(n: int, price: str = "50.00", compare: str | None = None) -> list[dict[str, Any]]:
    return [product(i, [(i * 10, price, compare, True)]) for i in range(1, n + 1)]


def test_two_runs_end_to_end(tmp_path: Path) -> None:
    cfg = RunConfig(
        stores=tmp_path / "stores.yml",
        data=tmp_path / "data",
        history_out=tmp_path / "work" / "h.parquet",
    )
    code, rec = process(
        cfg,
        [fetched("a", catalog(30), DAY1), fetched("b", catalog(5), DAY1)],
        DAY1,
        time.monotonic(),
    )
    assert code == EXIT_OK
    assert rec["status"] == "ok"
    assert rec["events"]["new"] == 35
    assert rec["rows_live"] == 35

    # Day 2: a sale at store a (20% off with compare-at), store b blocked.
    cfg.history_in = cfg.history_out
    code, rec = process(
        cfg,
        [
            fetched("a", catalog(30, "40.00", "50.00"), DAY2),
            fetched("b", [], DAY2, status="failed"),
        ],
        DAY2,
        time.monotonic(),
    )
    assert code == EXIT_PARTIAL
    assert rec["events"]["price_down"] == 30
    assert rec["events"]["discount_start"] == 30
    assert rec["rows_live"] == 35  # store b carried over
    assert rec["parquet_rows"] == 65  # 35 open + 30 closed
    changes = (cfg.data / "changes" / "2026" / "2026-11-05.csv").read_text().splitlines()
    assert len(changes) == 61  # header + 60 events
    summary = {s["store_id"]: s for s in snapshot_summary(cfg.data / "latest" / "snapshot.csv")}
    assert summary["a"]["discounted"] == 30
    assert summary["a"]["avg_discount_pct"] == 20.0
    badges = {p.name: json.loads(p.read_text()) for p in (cfg.data / "badges").iterdir()}
    assert set(badges) == {
        "days-running.json",
        "last-run.json",
        "missed-runs.json",
        "rows-today.json",
    }
    assert all(b["schemaVersion"] == 1 for b in badges.values())


def test_unit_error_holds_and_keeps_last_good_data(tmp_path: Path) -> None:
    cfg = RunConfig(stores=tmp_path / "stores.yml", data=tmp_path / "data")
    process(cfg, [fetched("a", catalog(30), DAY1)], DAY1, time.monotonic())
    before = (cfg.data / "latest" / "snapshot.csv").read_text()
    code, rec = process(cfg, [fetched("a", catalog(30, "0.50"), DAY2)], DAY2, time.monotonic())
    assert code == EXIT_HELD
    assert rec["status"] == "held"
    assert "suspicious:a" in rec["guard"]["keys"]
    assert (cfg.data / "latest" / "snapshot.csv").read_text() == before
    assert not (cfg.data / "changes" / "2026" / "2026-11-05.csv").exists()
    status = json.loads((cfg.data / "status.json").read_text())
    assert status["last_run"]["status"] == "held"
    assert status["last_run"]["hold_reasons"]

    # The same hold in the next run is accepted as real.
    day3 = DAY2.replace(day=6)
    code, rec = process(cfg, [fetched("a", catalog(30, "0.50"), day3)], day3, time.monotonic())
    assert code == EXIT_OK
    assert rec["guard"]["accepted_after_repeat"] is True


def test_non_usd_currency_holds(tmp_path: Path) -> None:
    cfg = RunConfig(stores=tmp_path / "stores.yml", data=tmp_path / "data")
    code, rec = process(
        cfg, [fetched("a", catalog(3), DAY1, currency="CAD")], DAY1, time.monotonic()
    )
    assert code == EXIT_HELD
    assert rec["guard"]["keys"] == ["currency:a"]


# -- schedule and status ----------------------------------------------------------
def test_crons_match_daily_workflow() -> None:
    wf = yaml.safe_load((ROOT / ".github" / "workflows" / "daily.yml").read_text())
    triggers = wf.get("on") or wf.get(True)  # PyYAML reads the key `on` as True
    assert tuple(s["cron"] for s in triggers["schedule"]) == CRONS


@pytest.mark.parametrize("runs_per_day", [2, 4])
def test_black_friday_window_follows_the_flag(runs_per_day: int) -> None:
    start = datetime(2026, 11, 25, tzinfo=UTC)
    end = datetime(2026, 12, 3, tzinfo=UTC)
    per_day: dict[str, int] = {}
    for s in slots(start, end, active_crons(runs_per_day)):
        per_day[s.date().isoformat()] = per_day.get(s.date().isoformat(), 0) + 1
    bfcm = ["2026-11-26", "2026-11-27", "2026-11-28", "2026-11-29", "2026-11-30", "2026-12-01"]
    assert per_day == {"2026-11-25": 1, **dict.fromkeys(bfcm, runs_per_day), "2026-12-02": 1}


def test_workflow_flag_is_valid_and_gates_the_extra_slots() -> None:
    wf = yaml.safe_load((ROOT / ".github" / "workflows" / "daily.yml").read_text())
    assert wf["env"]["BFCM_RUNS_PER_DAY"] in ("2", "4")
    gate = wf["jobs"]["slot"]["if"]
    assert all(c in gate for c in BFCM_EXTRA_CRONS)


def test_missed_slots_and_status(tmp_path: Path) -> None:
    first = DAY1
    runs = [first, DAY1.replace(day=6, minute=40)]  # 5 Nov missed, 6 Nov late but within grace
    now = datetime(2026, 11, 6, 12, 0, tzinfo=UTC)
    assert missed_slots(runs, first, now) == [DAY2]
    records = [
        {"run_id": "x", "started_at": "2026-11-04T06:17:00Z", "status": "ok", "rows_observed": 10},
        {"run_id": "y", "started_at": "2026-11-06T06:40:00Z", "status": "ok", "rows_observed": 12},
    ]
    status = build_status(records, now)
    assert status["days_running"] == 3
    assert status["missed_runs"] == 1
    assert status["rows_today"] == 12


def test_read_runs_empty(tmp_path: Path) -> None:
    assert read_runs(tmp_path) == []


def test_alert_rules() -> None:
    from pricemon.alert import needs_alert, render

    partial_small = {"stores_total": 10, "stores_not_updated": [{}]}
    partial_big = {"stores_total": 10, "stores_not_updated": [{}, {}, {}]}
    assert not needs_alert(0, {"status": "ok"})
    assert not needs_alert(2, partial_small)
    assert needs_alert(2, partial_big)
    assert needs_alert(3, {"status": "held"})
    assert needs_alert(1, {"status": "crashed"})
    assert needs_alert(None, None)  # step killed or timed out
    text = render(
        3,
        {
            "run_id": "r",
            "status": "held",
            "guard": {
                "holds": [{"key": "currency:a", "message": "a: currency proof shows ['CAD']"}]
            },
        },
        "https://x",
    )
    assert "hold `currency:a`" in text
