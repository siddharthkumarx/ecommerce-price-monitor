"""The daily pipeline.

    python -m pricemon.run --stores config/stores.yml --data data \\
        --history-in work/price_history_2026-11.parquet \\
        --history-out work/price_history_2026-11.parquet

Exit codes: 0 ok, 2 partial (some stores not updated), 3 held (nothing published,
last good data stays live), 1 crashed. Outputs are written for every code.
"""

from __future__ import annotations

import argparse
import asyncio
import hashlib
import os
import sys
import time
import traceback
from collections import Counter
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from pricemon import __version__
from pricemon.fetch import StoreFetch, fetch_store
from pricemon.guard import PrevVersion, accept_repeat, check_batch
from pricemon.history import (
    connect,
    load_snapshot,
    merge,
    previous_versions,
    update_month_parquet,
    write_snapshot,
)
from pricemon.models import VariantRow
from pricemon.normalize import normalize_products
from pricemon.outputs import (
    append_changes,
    append_run,
    build_status,
    event_counts,
    iso,
    read_runs,
    write_status,
)
from pricemon.polite import EdgeGuard, PoliteConfig, StoreSession, make_client
from pricemon.stores import Store, load_stores

EXIT_OK, EXIT_CRASHED, EXIT_PARTIAL, EXIT_HELD = 0, 1, 2, 3


@dataclass
class RunConfig:
    stores: Path
    data: Path
    history_in: Path | None = None
    history_out: Path | None = None
    concurrency: int = 5
    polite: PoliteConfig = field(default_factory=lambda: PoliteConfig(delay_s=4.0, jitter_s=3.0))
    edge_interval_s: float = 3.0
    edge_jitter_s: float = 1.5
    # No new request after 38 minutes: with setup, upload and commit the job stays
    # under the owner's 45-minute limit (D-020).
    budget_s: float = 38 * 60
    only: set[str] = field(default_factory=set)


async def fetch_all(
    stores: list[Store], cfg: RunConfig, day: Any, edge: EdgeGuard | None = None
) -> list[StoreFetch]:
    edge = edge or EdgeGuard(
        interval_s=cfg.edge_interval_s,
        jitter_s=cfg.edge_jitter_s,
        deadline=time.monotonic() + cfg.budget_s,
    )
    gate = asyncio.Semaphore(cfg.concurrency)
    async with make_client() as client:

        async def one(store: Store) -> StoreFetch:
            async with gate:
                session = StoreSession(
                    client=client, base_url=store.base_url, config=cfg.polite, edge=edge
                )
                result = await fetch_store(session, store, day)
                print(
                    f"{store.id:<24} {result.status:<8} products={len(result.products):<5} "
                    f"reqs={result.requests:<3} {result.reason or ''}",
                    flush=True,
                )
                return result

        # A daily rotating start order: a budget cut never hits the same stores daily.
        order = sorted(stores, key=lambda s: hashlib.sha256(f"{day}|{s.id}".encode()).hexdigest())
        results = {r.store_id: r for r in await asyncio.gather(*(one(s) for s in order))}
        return [results[s.id] for s in stores]


def _env_run_meta() -> dict[str, Any]:
    server, repo, run_id = (
        os.environ.get("GITHUB_SERVER_URL"),
        os.environ.get("GITHUB_REPOSITORY"),
        os.environ.get("GITHUB_RUN_ID"),
    )
    return {
        "trigger": os.environ.get("GITHUB_EVENT_NAME", "local"),
        "git_sha": os.environ.get("GITHUB_SHA"),
        "run_url": f"{server}/{repo}/actions/runs/{run_id}" if server and repo and run_id else None,
        "version": __version__,
    }


def process(
    cfg: RunConfig,
    fetches: list[StoreFetch],
    run_at: datetime,
    started: float,
    edge: EdgeGuard | None = None,
) -> tuple[int, dict[str, Any]]:
    """Validate, guard, merge and write outputs. Returns (exit code, run record)."""
    data = cfg.data
    rows: list[VariantRow] = []
    per_store: dict[str, list[VariantRow]] = {}
    rejected: dict[str, int] = {}
    compare_at_ignored = 0
    free_variants = 0
    reject_examples: dict[str, list[str]] = {}
    for f in fetches:
        if not f.complete:
            continue
        store_rows, stats = normalize_products(f.store_id, f.products, f.observed_at)
        per_store[f.store_id] = store_rows
        rows += store_rows
        rejected[f.store_id] = stats.rejected
        compare_at_ignored += stats.compare_at_ignored
        free_variants += stats.free
        if stats.examples:
            reject_examples[f.store_id] = stats.examples

    snapshot = data / "latest" / "snapshot.csv"
    con = connect()
    load_snapshot(con, snapshot)
    prev = {
        store: {vid: PrevVersion(price, compare) for vid, (price, compare) in versions.items()}
        for store, versions in previous_versions(con).items()
    }
    non_usd = {
        f.store_id: sorted(f.currencies)
        for f in fetches
        if f.status in ("ok", "mismatch") and f.currencies and f.currencies != {"USD"}
    }
    guard = check_batch(per_store, prev, rejected, non_usd)
    history = read_runs(data)
    last = history[-1] if history else None
    accepted = guard.held and accept_repeat(
        guard.keys, last["status"] if last else None, (last or {}).get("guard", {}).get("keys", [])
    )
    held = guard.held and not accepted

    events_by_type: dict[str, int] = {}
    rows_live = sum(len(v) for v in prev.values())
    parquet_rows = None
    if not held:
        result = merge(con, rows, set(per_store), run_at)
        write_snapshot(con, result.open_versions, snapshot)
        append_changes(data, result.events, run_at)
        events_by_type = event_counts(result.events)
        rows_live = len(result.open_versions)
        if cfg.history_out is not None:
            month_start = run_at.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            parquet_rows = update_month_parquet(
                con,
                cfg.history_in,
                result.open_versions,
                result.closed_versions,
                month_start,
                run_at,
                cfg.history_out,
            )

    failed = [f for f in fetches if not f.complete]
    status = "held" if held else ("partial" if failed else "ok")
    record: dict[str, Any] = {
        "run_id": run_at.strftime("%Y%m%dT%H%M%SZ"),
        "started_at": iso(run_at),
        "finished_at": iso(datetime.now(UTC)),
        "duration_s": round(time.monotonic() - started, 1),
        "status": status,
        **_env_run_meta(),
        "stores_total": len(fetches),
        "stores_ok": len(fetches) - len(failed),
        "stores_not_updated": [
            {"store_id": f.store_id, "status": f.status, "reason": f.reason} for f in failed
        ],
        "rows_observed": len(rows),
        "rows_live": rows_live,
        "rows_rejected": sum(rejected.values()),
        "reject_examples": reject_examples,
        "compare_at_ignored": compare_at_ignored,
        "free_variants": free_variants,
        "events": events_by_type,
        "parquet_rows": parquet_rows,
        "requests": sum(f.requests for f in fetches),
        "retries": sum(f.retries for f in fetches),
        "retry_causes": dict(Counter(c for f in fetches for c in f.retry_causes)),
        "edge": (
            {
                "throttle_events": edge.throttle_events,
                "cooldown_s": round(edge.cooldown_s, 1),
                "final_interval_s": round(edge.current_interval_s, 2),
                "halted_reason": edge.halted_reason,
            }
            if edge is not None
            else None
        ),
        "guard": {
            "keys": guard.keys,
            "holds": [{"key": h.key, "message": h.message} for h in guard.holds],
            "accepted_after_repeat": accepted,
            "matched": guard.matched,
            "price_changed": guard.price_changed,
            "unexplained": guard.unexplained,
            "suspicious": guard.suspicious,
        },
        "stores": [f.report() for f in fetches],
    }
    append_run(data, record)
    write_status(data, build_status(read_runs(data), datetime.now(UTC)))
    code = EXIT_HELD if held else (EXIT_PARTIAL if failed else EXIT_OK)
    return code, record


def run(cfg: RunConfig, now: datetime | None = None) -> int:
    started = time.monotonic()
    run_at = (now or datetime.now(UTC)).replace(microsecond=0)
    stores = load_stores(cfg.stores)
    if cfg.only:
        stores = [s for s in stores if s.id in cfg.only]
    try:
        edge = EdgeGuard(
            interval_s=cfg.edge_interval_s,
            jitter_s=cfg.edge_jitter_s,
            deadline=time.monotonic() + cfg.budget_s,
        )
        fetches = asyncio.run(fetch_all(stores, cfg, run_at.date(), edge))
        code, record = process(cfg, fetches, run_at, started, edge)
    except Exception as exc:
        append_run(
            cfg.data,
            {
                "run_id": run_at.strftime("%Y%m%dT%H%M%SZ"),
                "started_at": iso(run_at),
                "finished_at": iso(datetime.now(UTC)),
                "duration_s": round(time.monotonic() - started, 1),
                "status": "crashed",
                **_env_run_meta(),
                "error": f"{type(exc).__name__}: {exc}"[:500],
            },
        )
        write_status(cfg.data, build_status(read_runs(cfg.data), datetime.now(UTC)))
        traceback.print_exc()
        return EXIT_CRASHED
    print(
        f"status={record['status']} stores_ok={record['stores_ok']}/{record['stores_total']} "
        f"rows_live={record['rows_live']} events={record['events']} "
        f"duration_s={record['duration_s']}",
        flush=True,
    )
    return code


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawTextHelpFormatter)
    p.add_argument("--stores", type=Path, default=Path("config/stores.yml"))
    p.add_argument("--data", type=Path, default=Path("data"))
    p.add_argument("--history-in", type=Path)
    p.add_argument("--history-out", type=Path)
    p.add_argument("--concurrency", type=int, default=5, help="stores in flight")
    # Daily pace (docs/decisions.md, D-005).
    p.add_argument("--delay", type=float, default=4.0, help="per-store delay, seconds")
    p.add_argument("--jitter", type=float, default=3.0, help="per-store jitter, seconds")
    p.add_argument("--edge-interval", type=float, default=3.0, help="run-wide interval, seconds")
    p.add_argument("--edge-jitter", type=float, default=1.5, help="run-wide jitter, seconds")
    p.add_argument("--only", action="append", default=[], help="store id (repeatable)")
    a = p.parse_args(argv)
    cfg = RunConfig(
        stores=a.stores,
        data=a.data,
        history_in=a.history_in,
        history_out=a.history_out,
        concurrency=a.concurrency,
        polite=PoliteConfig(delay_s=a.delay, jitter_s=a.jitter),
        edge_interval_s=a.edge_interval,
        edge_jitter_s=a.edge_jitter,
        only=set(a.only),
    )
    return run(cfg)


if __name__ == "__main__":
    sys.exit(main())
