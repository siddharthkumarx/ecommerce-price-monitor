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
import csv
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

from pricemon import __version__, warmup
from pricemon.feed import publish as publish_feed
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
    parse_iso,
    read_runs,
    write_status,
)
from pricemon.polite import EdgeGuard, PoliteConfig, StoreSession, make_client
from pricemon.schedule import dispatch_slot
from pricemon.stores import Store, load_stores
from pricemon.summary import refresh as refresh_summary

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
    # Stores on their own hosts (WooCommerce, BigCommerce) do not share Shopify's
    # edge: each keeps the per-store pace above, and this lane only adds a small
    # run-wide gap, the time budget and the circuit breaker (D-031).
    other_concurrency: int = 6
    other_interval_s: float = 0.5
    other_jitter_s: float = 0.5
    # No new request after 52 minutes: with setup, upload and commit the job stays
    # under the owner's ~60-minute target for 100 stores (D-031, was 38 min, D-020).
    budget_s: float = 52 * 60
    only: set[str] = field(default_factory=set)


def last_prices(snapshot: Path) -> dict[str, dict[int, int]]:
    """Last good price per store and variant, for the second read on big moves."""
    out: dict[str, dict[int, int]] = {}
    if not snapshot.exists():
        return out
    with snapshot.open(newline="", encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            try:
                out.setdefault(r["store_id"], {})[int(r["variant_id"])] = int(r["price_cents"])
            except (KeyError, ValueError):
                continue
    return out


async def fetch_all(
    stores: list[Store],
    cfg: RunConfig,
    day: Any,
    edge: EdgeGuard | None = None,
    other_edge: EdgeGuard | None = None,
) -> list[StoreFetch]:
    edge = edge or EdgeGuard(
        interval_s=cfg.edge_interval_s,
        jitter_s=cfg.edge_jitter_s,
        deadline=time.monotonic() + cfg.budget_s,
    )
    other_edge = other_edge or EdgeGuard(
        interval_s=cfg.other_interval_s,
        jitter_s=cfg.other_jitter_s,
        deadline=edge.deadline,
    )
    gate = asyncio.Semaphore(cfg.concurrency)
    other_gate = asyncio.Semaphore(cfg.other_concurrency)
    prices = last_prices(cfg.data / "latest" / "snapshot.csv")
    async with make_client() as client:

        async def one(store: Store) -> StoreFetch:
            shopify = store.platform == "shopify"
            async with gate if shopify else other_gate:
                session = StoreSession(
                    client=client,
                    base_url=store.base_url,
                    config=cfg.polite,
                    edge=edge if shopify else other_edge,
                )
                result = await fetch_store(session, store, day, prices.get(store.id))
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
    meta: dict[str, Any] = {
        "trigger": os.environ.get("GITHUB_EVENT_NAME", "local"),
        "git_sha": os.environ.get("GITHUB_SHA"),
        "run_url": f"{server}/{repo}/actions/runs/{run_id}" if server and repo and run_id else None,
        "version": __version__,
    }
    # A dispatch that named its slot: the on-time trigger, or the watchdog (INC-009).
    slot = dispatch_slot(os.environ.get("DISPATCH_SLOT", ""))
    if meta["trigger"] == "workflow_dispatch" and slot:
        meta["dispatch"] = {"slot": slot, "by": os.environ.get("DISPATCH_BY") or "trigger"}
    return meta


def _hold_back(
    rows: list[VariantRow], held: dict[int, str], prev: dict[int, PrevVersion]
) -> tuple[list[VariantRow], int]:
    """Rows whose new value is held back keep their last good price; new ones wait."""
    if not held:
        return rows, 0
    out: list[VariantRow] = []
    n = 0
    for row in rows:
        if row.variant_id not in held:
            out.append(row)
            continue
        n += 1
        old = prev.get(row.variant_id)
        if old is not None:
            out.append(
                row.model_copy(
                    update={
                        "price_cents": old.price_cents,
                        "compare_at_cents": old.compare_at_cents,
                    }
                )
            )
    return out, n


def process(
    cfg: RunConfig,
    fetches: list[StoreFetch],
    run_at: datetime,
    started: float,
    edge: EdgeGuard | None = None,
) -> tuple[int, dict[str, Any]]:
    """Validate, guard, merge and write outputs. Returns (exit code, run record)."""
    data = cfg.data
    snapshot = data / "latest" / "snapshot.csv"
    con = connect()
    load_snapshot(con, snapshot)
    prev = {
        store: {vid: PrevVersion(price, compare) for vid, (price, compare) in versions.items()}
        for store, versions in previous_versions(con).items()
    }
    history = read_runs(data)
    # Canary (pricemon.warmup): stores without rows in the last good snapshot are
    # warming up; they are checked like every store but stay out of public numbers
    # until 3 clean days in a row.
    counted_ids, warming_ids = warmup.split([f.store_id for f in fetches], set(prev))
    promoted: list[str] = []
    warm_days: list[dict[str, Any]] = []

    rows: list[VariantRow] = []
    per_store: dict[str, list[VariantRow]] = {}
    rejected: dict[str, int] = {}
    compare_at_ignored = 0
    free_variants = 0
    held_back = 0
    reject_examples: dict[str, list[str]] = {}
    for f in fetches:
        warming = f.store_id in warming_ids
        store_rows: list[VariantRow] = []
        n_rejected = 0
        if f.complete:
            store_rows, stats = normalize_products(f.store_id, f.products, f.observed_at)
            n_rejected = stats.rejected
            store_rows, held = _hold_back(store_rows, f.held_variants, prev.get(f.store_id, {}))
            if not warming:
                compare_at_ignored += stats.compare_at_ignored
                free_variants += stats.free
                held_back += held
                if stats.examples:
                    reject_examples[f.store_id] = stats.examples
        if warming:
            day = warmup.judge(
                f.store_id,
                f.status,
                f.reason,
                len(store_rows),
                n_rejected,
                f.retry_causes,
                f.currencies,
                history,
            )
            n = warmup.streak(f.store_id, history, run_at.date(), day.clean)
            warm = {**day.record(), "streak": n, "promoted": n >= warmup.WARMUP_DAYS}
            warm_days.append(warm)
            if not warm["promoted"]:
                continue
            promoted.append(f.store_id)
        if not f.complete:
            continue
        per_store[f.store_id] = store_rows
        rows += store_rows
        rejected[f.store_id] = n_rejected

    public_ids = set(counted_ids) | set(promoted)
    public = [f for f in fetches if f.store_id in public_ids]
    non_usd = {
        f.store_id: sorted(f.currencies)
        for f in public
        if f.status in ("ok", "mismatch") and f.currencies and f.currencies != {"USD"}
    }
    guard = check_batch(per_store, prev, rejected, non_usd)
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
        # A promoted store's first rows are its baseline, not changes (like run one).
        result.events = [e for e in result.events if e.store_id not in promoted]
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
                committed_runs=[
                    parse_iso(r["started_at"]) for r in history if r["status"] in ("ok", "partial")
                ],
            )

    if held:
        promoted, public_ids = [], set(counted_ids)
        for w in warm_days:
            w["promoted"] = False
        public = [f for f in fetches if f.store_id in public_ids]
    failed = [f for f in public if not f.complete]
    status = "held" if held else ("partial" if failed else "ok")
    reads = [r for f in public for r in f.second_reads]
    record: dict[str, Any] = {
        "run_id": run_at.strftime("%Y%m%dT%H%M%SZ"),
        "started_at": iso(run_at),
        "finished_at": iso(datetime.now(UTC)),
        "duration_s": round(time.monotonic() - started, 1),
        "status": status,
        **_env_run_meta(),
        "stores_total": len(public),
        "stores_ok": len(public) - len(failed),
        "stores_warming": sum(1 for w in warm_days if not w["promoted"]),
        "stores_promoted": promoted,
        "warming": warm_days,
        "stores_not_updated": [
            {"store_id": f.store_id, "status": f.status, "reason": f.reason} for f in failed
        ],
        "rows_observed": len(rows),
        "rows_live": rows_live,
        "rows_rejected": sum(rejected.values()),
        "reject_examples": reject_examples,
        "compare_at_ignored": compare_at_ignored,
        "free_variants": free_variants,
        "rows_held_back": held_back,
        "second_reads": {
            "reads": sum(1 for r in reads if "reread_cents" in r),
            "confirmed": sum(1 for r in reads if r.get("verdict") == "confirmed"),
            "held": sum(1 for r in reads if str(r.get("verdict", "")).startswith("held")),
        },
        "events": events_by_type,
        "parquet_rows": parquet_rows,
        "requests": sum(f.requests for f in fetches),
        "requests_by_platform": dict(
            Counter(f.platform for f in fetches for _ in range(f.requests))
        ),
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
    warmup.write_state(
        data,
        {
            "run_id": record["run_id"],
            "counted": sorted(public_ids),
            "warming": {w["store_id"]: w for w in warm_days if not w["promoted"]},
            "promoted": promoted,
        },
    )
    try:
        refresh_summary(data, datetime.now(UTC).replace(microsecond=0))
    except Exception as exc:  # pragma: no cover - logged, never fatal
        print(f"daily summary not written: {type(exc).__name__}: {exc}", flush=True)
    # The public feed: only a published (ok or partial) run rewrites it, so a held
    # run leaves it as it was and its age shows the staleness. It is additive and
    # must never fail the run.
    if not held:
        try:
            publish_feed(data, datetime.now(UTC).replace(microsecond=0), cfg.stores)
        except Exception as exc:  # pragma: no cover - logged, never fatal
            print(f"public feed not written: {type(exc).__name__}: {exc}", flush=True)
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
        other_edge = EdgeGuard(
            interval_s=cfg.other_interval_s,
            jitter_s=cfg.other_jitter_s,
            deadline=edge.deadline,
        )
        fetches = asyncio.run(fetch_all(stores, cfg, run_at.date(), edge, other_edge))
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
