"""The public feed, data/public/feed.json (steadydata.feed/v1)."""

from __future__ import annotations

import csv
import json
import time
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import pytest

from pricemon.feed import MAX_BYTES, SCHEMA, build_feed, daily, dumps, publish, write_feed
from pricemon.outputs import build_status, read_runs
from pricemon.run import EXIT_HELD, EXIT_OK, RunConfig, process
from pricemon.schedule import trigger_since
from tests.test_outputs import DAY1, DAY2, catalog, fetched

ROOT = Path(__file__).resolve().parents[1]
NOW = datetime(2026, 11, 21, 7, 0, tzinfo=UTC)
ISO = "%Y-%m-%dT%H:%M:%SZ"

CONTRACT: dict[str, Any] = {
    "schema": str,
    "generated_at": str,
    "monitor": {
        "id": str,
        "title": str,
        "repo": str,
        "dashboard": str,
        "first_run": str,
        "stores_total": int,
        "categories": list,
    },
    "last_run": {
        "run_id": str,
        "finished_at": str,
        "status": str,
        "stores_ok": int,
        "rows_live": int,
        "run_url": str,
    },
    "checks": {
        "rows_validated": int,
        "rows_rejected": int,
        "held_back": int,
        "second_source_checks": int,
        "second_source_matches": int,
    },
    "totals": {"days_running": int, "runs_total": int, "runs_good": int, "runs_held": int},
    "daily": list,
}
# Fields added by D-031 (the contract only grows): every feed built from now on has
# them; a feed committed by a run before D-031 does not.
CONTRACT_D031: dict[str, Any] = {
    "monitor": {"platforms": list},
    "delivery": {
        "since": str,
        "runs_due": int,
        "runs_delivered": int,
        "on_time_runs_due": int,
        "on_time_runs": int,
    },
    "history_url": str,
}
DAILY_KEYS = {
    "date": str,
    "runs": int,
    "rows_live": int,
    "price_down": int,
    "price_up": int,
    "discount_start": int,
    "discount_end": int,
    "out_of_stock": int,
    "back_in_stock": int,
    "new": int,
    "removed": int,
}


def conforms(value: Any, shape: Any, path: str = "") -> None:
    if isinstance(shape, dict):
        assert isinstance(value, dict), path
        for key, sub in shape.items():
            assert key in value, f"missing {path}.{key}"
            conforms(value[key], sub, f"{path}.{key}")
    else:
        assert isinstance(value, shape), f"{path}: {value!r}"
        assert not isinstance(value, bool), f"{path}: {value!r}"


def rec(started: str, status: str = "ok", **events: int) -> dict[str, Any]:
    return {
        "run_id": started.replace("-", "").replace(":", ""),
        "started_at": started,
        "finished_at": started,
        "status": status,
        "stores_ok": 2,
        "stores_total": 2,
        "rows_observed": 10,
        "rows_rejected": 1,
        "rows_live": 10,
        "run_url": "https://github.com/x/y/actions/runs/1",
        "events": events,
        "stores": [],
    }


def test_committed_feed_follows_the_contract() -> None:
    path = ROOT / "data" / "public" / "feed.json"
    feed = json.loads(path.read_text())
    conforms(feed, CONTRACT)
    assert feed["schema"] == SCHEMA
    assert feed["monitor"]["id"] == "ecommerce-price-monitor"
    assert feed["monitor"]["repo"] == "https://github.com/siddharthkumarx/ecommerce-price-monitor"
    assert feed["last_run"]["status"] in ("ok", "partial")
    assert feed["last_run"]["run_url"].startswith("https://github.com/")
    for key in ("generated_at", "last_run.finished_at", "monitor.first_run"):
        obj: Any = feed
        for part in key.split("."):
            obj = obj[part]
        datetime.strptime(obj, ISO)
    assert 0 < len(feed["daily"]) <= 60
    for row in feed["daily"]:
        conforms(row, DAILY_KEYS)
    dates = [r["date"] for r in feed["daily"]]
    assert dates == sorted(dates)
    assert len(set(dates)) == len(dates)
    assert path.stat().st_size < MAX_BYTES


def test_committed_feed_has_no_product_names() -> None:
    text = (ROOT / "data" / "public" / "feed.json").read_text().lower()
    with (ROOT / "data" / "latest" / "snapshot.csv").open(encoding="utf-8") as fh:
        titles = {r["product_title"].strip().lower() for r in csv.DictReader(fh)}
    leaked = [t for t in titles if len(t) > 6 and t in text]
    assert not leaked, leaked[:5]


def test_baseline_run_is_excluded_and_runs_on_one_date_are_summed() -> None:
    runs = [
        rec("2026-11-04T08:46:55Z", new=11769),  # the baseline
        rec("2026-11-05T06:18:00Z", price_down=3, new=1),
        rec("2026-11-05T18:18:00Z", price_down=2, out_of_stock=4),
        rec("2026-11-06T06:18:00Z", status="held", price_down=99),
        rec("2026-11-06T07:00:00Z", status="crashed"),
        rec("2026-11-07T06:18:00Z", status="partial", discount_start=5),
    ]
    rows = daily(runs)
    assert [r["date"] for r in rows] == ["2026-11-05", "2026-11-07"]
    assert rows[0]["runs"] == 2
    assert (rows[0]["price_down"], rows[0]["new"], rows[0]["out_of_stock"]) == (5, 1, 4)
    assert rows[1]["discount_start"] == 5
    assert all(r["new"] < 11769 for r in rows)


def test_daily_keeps_the_newest_60_dates_oldest_first() -> None:
    runs = [rec("2026-09-01T06:18:00Z", new=1)]
    for i in range(80):
        day = datetime(2026, 9, 2, 6, 18, tzinfo=UTC).timestamp() + i * 86400
        runs.append(rec(datetime.fromtimestamp(day, UTC).strftime(ISO), price_up=i))
    rows = daily(runs)
    assert len(rows) == 60
    assert rows[0]["price_up"] == 20
    assert rows[-1]["price_up"] == 79


def test_feed_stays_under_30_kb_with_60_busy_days(tmp_path: Path) -> None:
    runs = [rec("2026-09-01T06:18:00Z", new=1)]
    for i in range(240):  # four runs a day
        t = datetime(2026, 9, 2, tzinfo=UTC).timestamp() + i * 6 * 3600
        r = rec(datetime.fromtimestamp(t, UTC).strftime(ISO))
        r["events"] = dict.fromkeys(DAILY_KEYS.keys() - {"date", "runs", "rows_live"}, 99_999)
        runs.append(r)
    feed = build_feed(runs, build_status(runs, NOW), NOW)
    assert feed is not None
    assert len(dumps(feed).encode()) < MAX_BYTES
    write_feed(tmp_path, feed)
    assert json.loads((tmp_path / "public" / "feed.json").read_text()) == feed


def test_checks_count_the_guard_and_the_witnesses() -> None:
    run = rec("2026-11-05T06:18:00Z")
    run["guard"] = {"matched": 8, "suspicious": 1, "holds": []}
    run["stores"] = [
        {"status": "ok", "variants": 6, "witnesses": [{"js": "match", "jsonld": "match"}]},
        {"status": "ok", "variants": 4, "witnesses": [{"js": "match", "jsonld": "no_offers"}]},
        {"status": "mismatch", "variants": 7, "witnesses": [{"js": "mismatch", "jsonld": "match"}]},
        {"status": "failed", "variants": 0, "witnesses": []},
    ]
    feed = build_feed([run], build_status([run], NOW), NOW)
    assert feed is not None
    assert feed["checks"]["rows_validated"] == 11
    assert feed["checks"]["rows_rejected"] == 1
    assert feed["checks"]["held_back"] == 7
    assert feed["checks"]["second_source_checks"] == 5
    assert feed["checks"]["second_source_matches"] == 4
    assert feed["checks"]["rows_compared_with_last_run"] == 8


def test_no_feed_without_a_good_run(tmp_path: Path) -> None:
    assert build_feed([rec("2026-11-04T06:18:00Z", status="held")], {}, NOW) is None
    assert publish(tmp_path, NOW) is None
    assert not (tmp_path / "public").exists()


def test_pipeline_writes_the_feed_and_a_held_run_leaves_it_alone(tmp_path: Path) -> None:
    cfg = RunConfig(stores=tmp_path / "stores.yml", data=tmp_path / "data")
    code, _ = process(cfg, [fetched("a", catalog(30), DAY1)], DAY1, time.monotonic())
    assert code == EXIT_OK
    feed_file = cfg.data / "public" / "feed.json"
    first = json.loads(feed_file.read_text())
    conforms(first, CONTRACT)
    conforms(first, CONTRACT_D031)
    assert first["daily"] == []  # only the baseline so far
    code, _ = process(
        cfg, [fetched("a", catalog(30, "40.00", "50.00"), DAY2)], DAY2, time.monotonic()
    )
    assert code == EXIT_OK
    second = json.loads(feed_file.read_text())
    assert second["daily"][0]["date"] == "2026-11-05"
    assert second["daily"][0]["price_down"] == 30
    before = feed_file.read_bytes()
    day3 = DAY2.replace(day=6)
    code, rec3 = process(cfg, [fetched("a", catalog(30, "0.50"), day3)], day3, time.monotonic())
    assert code == EXIT_HELD
    assert feed_file.read_bytes() == before  # a held run never writes the feed
    assert read_runs(cfg.data)[-1]["run_id"] == rec3["run_id"]
    assert not list(feed_file.parent.glob(".feed-*"))  # no temp file left behind


@pytest.mark.parametrize("status", ["held", "crashed"])
def test_only_good_runs_feed_last_run(status: str) -> None:
    runs = [rec("2026-11-04T06:18:00Z"), rec("2026-11-05T06:18:00Z", status=status)]
    feed = build_feed(runs, build_status(runs, NOW), NOW)
    assert feed is not None
    assert feed["last_run"]["run_id"] == runs[0]["run_id"]
    assert feed["totals"]["runs_total"] == 2


def test_feed_counts_on_time_only_from_the_trigger_in_the_committed_run_log() -> None:
    # The committed feed agrees with the committed run log: on time is counted only
    # from the first slot the on-time trigger dispatched (none before 22 Nov 2026).
    feed = json.loads((ROOT / "data" / "public" / "feed.json").read_text())
    runs = [json.loads(x) for x in (ROOT / "data" / "runs.jsonl").read_text().splitlines() if x]
    since = trigger_since(runs)
    sched = feed["schedule"]
    assert sched["delivered"] == sched["slots"]
    if since is None:
        assert (sched["on_time_since"], sched["on_time_pct"]) == (None, None)
    else:
        assert sched["on_time_since"] == since.strftime("%Y-%m-%dT%H:%M:%SZ")
        assert sched["on_time_since"] >= "2026-11-22"
        assert sched["on_time_pct"] is not None
    assert sched["note"].endswith("(INC-009).")
