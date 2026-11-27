"""Sequential shards of the daily run (D-033): each shard reads a slice of the stores
and writes a file; one process step turns the files into every output."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import pytest
import yaml

import pricemon.run as run_mod
from pricemon.fetch import StoreFetch
from pricemon.polite import EdgeGuard
from pricemon.run import RunConfig, run, shard_stores
from pricemon.stores import Store, load_stores
from tests.test_outputs import catalog, fetched

ROOT = Path(__file__).resolve().parents[1]
RUN_AT = datetime(2026, 11, 28, 6, 17, 30, tzinfo=UTC)


def _stores(n: int) -> list[Store]:
    return [Store(f"s{i:03d}", f"S{i}", "audio", f"s{i}.example") for i in range(n)]


def test_shards_split_every_store_exactly_once_and_evenly() -> None:
    stores = _stores(275)
    parts = [shard_stores(stores, RUN_AT.date(), k, 3) for k in (1, 2, 3)]
    ids = [s.id for part in parts for s in part]
    assert sorted(ids) == sorted(s.id for s in stores)
    assert {len(p) for p in parts} <= {91, 92}
    # Deterministic for the day, different on another day.
    assert parts[0] == shard_stores(stores, RUN_AT.date(), 1, 3)
    other = shard_stores(stores, datetime(2026, 11, 29, tzinfo=UTC).date(), 1, 3)
    assert other != parts[0]
    with pytest.raises(ValueError, match="out of range"):
        shard_stores(stores, RUN_AT.date(), 4, 3)


def test_store_fetch_round_trips_through_json() -> None:
    f = fetched("a", catalog(3), RUN_AT)
    f.request_log = [(1.5, "robots.txt", "200")]
    back = StoreFetch.from_json(json.loads(json.dumps(f.to_json())))
    assert back == f


def _write_stores(path: Path, n: int) -> list[Store]:
    path.write_text(
        yaml.safe_dump(
            {
                "stores": [
                    {"id": f"s{i}", "name": f"S{i}", "category": "audio", "host": f"s{i}.example"}
                    for i in range(n)
                ]
            }
        )
    )
    return load_stores(path)


@pytest.fixture
def fake_fetch(monkeypatch: pytest.MonkeyPatch) -> list[list[str]]:
    """Replace the network fetch: every store returns a small catalog."""
    calls: list[list[str]] = []

    async def fake(
        stores: list[Store], cfg: RunConfig, day: Any, edge: EdgeGuard | None = None
    ) -> list[StoreFetch]:
        calls.append([s.id for s in stores])
        if edge is not None:
            edge.throttle_events += 1
        return [fetched(s.id, catalog(2), RUN_AT) for s in stores]

    monkeypatch.setattr(run_mod, "fetch_all", fake)
    return calls


def test_shards_then_process_publish_every_store_once(
    tmp_path: Path, fake_fetch: list[list[str]]
) -> None:
    stores_path = tmp_path / "stores.yml"
    stores = _write_stores(stores_path, 7)
    files = []
    for k in (1, 2, 3):
        out = tmp_path / f"fetch-{k}.json"
        cfg = RunConfig(
            stores=stores_path, data=tmp_path / "data", shard=(k, 3), fetch_out=out, run_at=RUN_AT
        )
        assert run(cfg) == 0
        files.append(out)
    # A shard writes nothing but its file.
    assert not (tmp_path / "data").exists()
    assert sorted(i for call in fake_fetch for i in call) == sorted(s.id for s in stores)

    cfg = RunConfig(stores=stores_path, data=tmp_path / "data", fetch_in=files, run_at=RUN_AT)
    assert run(cfg) == 0
    assert len(fake_fetch) == 3  # the process step reads no store
    record = json.loads((tmp_path / "data" / "runs.jsonl").read_text().splitlines()[-1])
    assert record["status"] == "ok"
    assert record["stores_ok"] == 7
    assert record["started_at"] == "2026-11-28T06:17:30Z"
    assert [s["shard"] for s in record["shards"]] == [[1, 3], [2, 3], [3, 3]]
    assert record["edge"]["throttle_events"] == 3


def test_a_missing_shard_leaves_its_stores_not_updated(
    tmp_path: Path, fake_fetch: list[list[str]]
) -> None:
    stores_path = tmp_path / "stores.yml"
    _write_stores(stores_path, 6)
    out = tmp_path / "fetch-1.json"
    run(
        RunConfig(
            stores=stores_path, data=tmp_path / "x", shard=(1, 2), fetch_out=out, run_at=RUN_AT
        )
    )
    cfg = RunConfig(
        stores=stores_path,
        data=tmp_path / "data",
        fetch_in=[out, tmp_path / "fetch-2.json"],
        run_at=RUN_AT,
    )
    assert run(cfg) == 2
    record = json.loads((tmp_path / "data" / "runs.jsonl").read_text().splitlines()[-1])
    assert record["status"] == "partial"
    assert {s["reason"] for s in record["stores_not_updated"]} == {
        "not read: its shard did not finish"
    }
    assert record["stores_ok"] == 3


def test_no_shard_at_all_is_a_crash(tmp_path: Path, fake_fetch: list[list[str]]) -> None:
    stores_path = tmp_path / "stores.yml"
    _write_stores(stores_path, 2)
    cfg = RunConfig(
        stores=stores_path, data=tmp_path / "data", fetch_in=[tmp_path / "none.json"], run_at=RUN_AT
    )
    assert run(cfg) == 1
    assert fake_fetch == []
    record = json.loads((tmp_path / "data" / "runs.jsonl").read_text().splitlines()[-1])
    assert record["status"] == "crashed"


def test_a_shard_file_of_another_run_is_refused(
    tmp_path: Path, fake_fetch: list[list[str]]
) -> None:
    stores_path = tmp_path / "stores.yml"
    _write_stores(stores_path, 2)
    out = tmp_path / "fetch-1.json"
    run(
        RunConfig(
            stores=stores_path, data=tmp_path / "x", shard=(1, 1), fetch_out=out, run_at=RUN_AT
        )
    )
    later = RUN_AT.replace(day=29)
    cfg = RunConfig(stores=stores_path, data=tmp_path / "data", fetch_in=[out], run_at=later)
    assert run(cfg) == 1


def test_the_workflow_runs_shards_one_after_another() -> None:
    wf = yaml.safe_load((ROOT / ".github" / "workflows" / "daily.yml").read_text())
    fetch = wf["jobs"]["fetch"]
    assert fetch["strategy"]["max-parallel"] == 1
    assert fetch["timeout-minutes"] <= 45
    assert wf["jobs"]["run"]["needs"] == ["slot", "fetch"]
    step = next(s for s in wf["jobs"]["run"]["steps"] if s.get("id") == "run")
    assert "--fetch-in" in step["run"]
