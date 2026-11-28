"""Fixes from the fresh review of F1-EXPAND (D-036, D-033, D-037)."""

from __future__ import annotations

import json
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import pytest
import yaml

import pricemon.run as run_mod
from pricemon.normalize import normalize_products
from pricemon.run import RunConfig, carried_edge, run
from pricemon.sources import collect
from pricemon.stores import Store
from tests.test_outputs import catalog, fetched

ROOT = Path(__file__).resolve().parents[1]
RUN_AT = datetime(2026, 11, 28, 6, 17, 30, tzinfo=UTC)


def _row(store: str, rid: str, **extra: Any) -> tuple[str, dict[str, Any]]:
    row: dict[str, Any] = {"store": store, "category": "audio", "passed": True, **extra}
    return rid, row


def test_a_failed_read_does_not_lift_a_proven_ban() -> None:
    def rec(*runs: tuple[str, dict[str, Any]]) -> str:
        payloads = [(f"{rid}.json", {"meta": {"id": rid}, "results": [r]}) for rid, r in runs]
        (record,) = collect(payloads)
        return record.terms

    ban = _row("A", "recon-005", terms="ban", terms_source="read")
    assert rec(ban, _row("A", "recon-007", terms="none_found", terms_source="http 404")) == "ban"
    assert rec(ban, _row("A", "recon-007", terms="no_ban", terms_source="read")) == "no_ban"
    unknown = _row("A", "recon-005", terms="none_found", terms_source="http 404")
    assert rec(unknown, _row("A", "recon-007", terms="ban", terms_source="read")) == "ban"


def _write_stores(path: Path, n: int) -> None:
    path.write_text(
        yaml.safe_dump(
            {
                "stores": [
                    {
                        "id": f"s{i}",
                        "name": f"S{i}",
                        "category": "audio",
                        "host": f"s{i}.example",
                        "terms": "no_ban",
                    }
                    for i in range(n)
                ]
            }
        )
    )


def test_pace_and_halt_carry_to_the_next_shard(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    seen: list[float] = []

    async def fake(stores: list[Store], cfg: RunConfig, day: Any, edge: Any = None) -> Any:
        seen.append(edge.current_interval_s)
        edge.current_interval_s = 6.75
        return [fetched(s.id, catalog(1), RUN_AT) for s in stores]

    monkeypatch.setattr(run_mod, "fetch_all", fake)
    stores = tmp_path / "stores.yml"
    _write_stores(stores, 4)
    one = tmp_path / "fetch-1.json"
    cfg = RunConfig(stores=stores, data=tmp_path / "d", shard=(1, 2), fetch_out=one, run_at=RUN_AT)
    run(cfg)
    assert carried_edge([one], RUN_AT) == (6.75, None)
    two = tmp_path / "fetch-2.json"
    run(
        RunConfig(
            stores=stores,
            data=tmp_path / "d",
            shard=(2, 2),
            fetch_out=two,
            run_at=RUN_AT,
            edge_from=[one, tmp_path / "none.json"],
        )
    )
    assert seen[1] == 6.75  # the second shard starts at the slowed pace
    # A halt in shard 1 (not the time budget): shard 2 sends no request.
    payload = json.loads(one.read_text())
    payload["edge"]["halted_reason"] = "run halted: 8 429s in a row"
    one.write_text(json.dumps(payload))
    calls = len(seen)
    run(
        RunConfig(
            stores=stores,
            data=tmp_path / "d",
            shard=(2, 2),
            fetch_out=two,
            run_at=RUN_AT,
            edge_from=[one],
        )
    )
    assert len(seen) == calls
    out = json.loads(two.read_text())
    assert out["edge"]["halted_reason"].startswith("halted in an earlier shard")
    assert {f["reason"] for f in out["fetches"]} == {"not read: the run halted in an earlier shard"}
    # The time budget of one shard is its own.
    payload["edge"]["halted_reason"] = "run halted: time budget reached"
    one.write_text(json.dumps(payload))
    assert carried_edge([one], RUN_AT)[1] is None


def test_a_repeated_variant_is_a_duplicate_whatever_its_first_copy_was() -> None:
    v = {"id": 7, "title": "A", "price": "0.00", "available": True}
    products = [{"id": 1, "handle": "p", "title": "P", "variants": [v, {**v, "price": "5.00"}]}]
    rows, stats = normalize_products("s", products, RUN_AT)
    assert (stats.free, stats.duplicates, stats.rejected, len(rows)) == (1, 1, 0, 0)


def test_shards_read_the_commit_the_slot_job_planned() -> None:
    wf = yaml.safe_load((ROOT / ".github" / "workflows" / "daily.yml").read_text())
    assert "sha" in wf["jobs"]["slot"]["outputs"]
    checkout = wf["jobs"]["fetch"]["steps"][0]
    assert checkout["with"]["ref"].startswith("${{ needs.slot.outputs.sha")
    read = next(
        s for s in wf["jobs"]["fetch"]["steps"] if s.get("name") == "Read this shard's stores"
    )
    assert "--edge-from" in read["run"]
    names = [s.get("name") for s in wf["jobs"]["run"]["steps"]]
    assert Counter(names)["Mirror the history to Releases"] == 1
    assert "Withdraw from earlier months" not in names  # D-049: no per-run withdrawal
