from __future__ import annotations

import json
import time
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import yaml

from pricemon.fetch import StoreFetch, WitnessResult
from pricemon.outputs import build_status, read_runs, snapshot_summary, write_status
from pricemon.run import EXIT_HELD, EXIT_OK, EXIT_PARTIAL, RunConfig, process
from pricemon.schedule import CRONS, active_crons, due_slots, gate

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
        "on-time-runs.json",
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

    # The same hold in the next run is not accepted: only a rows drop is (D-041).
    day3 = DAY2.replace(day=6)
    code, rec = process(cfg, [fetched("a", catalog(30, "0.50"), day3)], day3, time.monotonic())
    assert code == EXIT_HELD
    assert rec["guard"]["accepted_after_repeat"] is False
    assert (cfg.data / "latest" / "snapshot.csv").read_text() == before


def test_non_usd_currency_holds(tmp_path: Path) -> None:
    cfg = RunConfig(stores=tmp_path / "stores.yml", data=tmp_path / "data")
    code, rec = process(
        cfg, [fetched("a", catalog(3), DAY1, currency="CAD")], DAY1, time.monotonic()
    )
    assert code == EXIT_HELD
    assert rec["guard"]["keys"] == ["currency:a"]


def test_two_cad_runs_in_a_row_publish_nothing_for_that_store(tmp_path: Path) -> None:
    cfg = RunConfig(stores=tmp_path / "stores.yml", data=tmp_path / "data")
    process(cfg, [fetched("a", catalog(30), DAY1)], DAY1, time.monotonic())
    snapshot = cfg.data / "latest" / "snapshot.csv"
    before = snapshot.read_text()
    for day in (DAY2, DAY2.replace(day=6)):
        code, rec = process(
            cfg,
            [fetched("a", catalog(30, "45.00"), day, currency="CAD")],
            day,
            time.monotonic(),
        )
        assert code == EXIT_HELD
        assert rec["guard"]["keys"] == ["currency:a"]
        assert rec["guard"]["accepted_after_repeat"] is False
        assert snapshot.read_text() == before  # the USD prices of day 1 stay
        assert not (cfg.data / "changes" / "2026" / f"{day:%Y-%m-%d}.csv").exists()


# -- schedule and status ----------------------------------------------------------
def test_crons_match_daily_workflow() -> None:
    wf = yaml.safe_load((ROOT / ".github" / "workflows" / "daily.yml").read_text())
    triggers = wf.get("on") or wf.get(True)  # PyYAML reads the key `on` as True
    assert tuple(s["cron"] for s in triggers["schedule"]) == CRONS


def test_one_slot_a_day_after_the_black_friday_runs() -> None:
    start = datetime(2026, 11, 25, tzinfo=UTC)
    end = datetime(2026, 12, 3, tzinfo=UTC)
    per_day: dict[str, int] = {}
    for s in due_slots(start, end, active_crons()):
        per_day[s.date().isoformat()] = per_day.get(s.date().isoformat(), 0) + 1
    later = ["2026-11-28", "2026-11-29", "2026-11-30", "2026-12-01", "2026-12-02"]
    assert per_day == {"2026-11-25": 1, "2026-11-26": 4, "2026-11-27": 4, **dict.fromkeys(later, 1)}


def test_the_workflow_has_no_black_friday_flag_and_gates_every_trigger() -> None:
    wf = yaml.safe_load((ROOT / ".github" / "workflows" / "daily.yml").read_text())
    assert "BFCM_RUNS_PER_DAY" not in (wf.get("env") or {})
    decide = next(st["run"] for st in wf["jobs"]["slot"]["steps"] if st.get("id") == "decide")
    assert "pricemon.schedule gate" in decide
    now = datetime(2026, 11, 27, 13, 0, tzinfo=UTC)
    assert gate("schedule", [], now, cron="17 0,12 26-30 11 *")["slot"] == "2026-11-27T06:17:00Z"


def test_status_counts_on_time_late_and_missed_slots(tmp_path: Path) -> None:
    now = datetime(2026, 11, 7, 12, 0, tzinfo=UTC)
    records = [
        {"run_id": "x", "started_at": "2026-11-04T06:17:40Z", "status": "ok", "rows_observed": 10},
        # 5 Nov: no run (missed). 6 Nov: 7 h late. 7 Nov: on time.
        {"run_id": "y", "started_at": "2026-11-06T13:40:00Z", "status": "ok", "rows_observed": 12},
        {"run_id": "z", "started_at": "2026-11-07T06:19:00Z", "status": "ok", "rows_observed": 13},
    ]
    status = build_status(records, now, active_crons())
    assert status["days_running"] == 4
    assert status["missed_runs"] == 1
    assert status["missed_slots"] == ["2026-11-05T06:17:00Z"]
    sched = status["schedule"]
    assert (sched["slots"], sched["on_time"], sched["late"], sched["missed"]) == (4, 2, 1, 1)
    assert sched["late_slots"] == ["2026-11-06T06:17:00Z"]
    assert status["rows_today"] == 13
    write_status(tmp_path, status)
    assert sched["delivered"] == 3
    # No run came from the on-time trigger yet: no on-time count is shown.
    assert sched["on_time_since"] is None
    assert sched["on_time_pct"] is None
    badge = json.loads((tmp_path / "badges" / "on-time-runs.json").read_text())
    assert (badge["label"], badge["message"]) == ("on time", "from next run")


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


def test_on_time_badge_and_text_start_with_the_trigger(tmp_path: Path) -> None:
    from pricemon.outputs import on_time_text

    before = {"on_time_since": None, "since": {"slots": 0, "on_time": 0}}
    assert on_time_text(before) == ("on time", "from next run")
    after = {"on_time_since": "2026-11-22T06:17:00Z", "since": {"slots": 3, "on_time": 2}}
    assert on_time_text(after) == ("on time since 22 Nov", "2 of 3")
    records: list[dict[str, Any]] = [
        {
            "run_id": "a",
            "started_at": "2026-11-21T13:29:00Z",
            "status": "ok",
            "trigger": "schedule",
        },
        {
            "run_id": "b",
            "started_at": "2026-11-22T06:18:00Z",
            "status": "ok",
            "trigger": "workflow_dispatch",
            "dispatch": {"slot": "2026-11-22T06:17:00Z", "by": "trigger"},
        },
    ]
    for r in records:
        r["rows_observed"] = 1
    write_status(
        tmp_path, build_status(records, datetime(2026, 11, 22, 9, tzinfo=UTC), active_crons())
    )
    badge = json.loads((tmp_path / "badges" / "on-time-runs.json").read_text())
    assert (badge["label"], badge["message"], badge["color"]) == (
        "on time since 22 Nov",
        "1 of 1",
        "0E8A7D",
    )
