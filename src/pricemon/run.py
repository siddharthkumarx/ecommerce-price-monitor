"""The daily pipeline.

    python -m pricemon.run --stores config/stores.yml --data data \\
        --history-in work/price_history_2026-11.parquet \\
        --history-out work/price_history_2026-11.parquet

Exit codes: 0 ok, 2 partial (some stores not updated), 3 held (nothing published,
last good data stays live), 1 crashed. Outputs are written for every code.

Sharded run (D-031): the daily workflow reads the stores in ``n`` shards, **one
after another** (never in parallel, so the run-wide request rate stays that of one
runner, D-020), then processes them once:

    python -m pricemon.run --shard 1/3 --run-at 2026-11-28T06:17:30Z --fetch-out work/fetch-1.json
    ...
    python -m pricemon.run --run-at 2026-11-28T06:17:30Z --fetch-in work/fetch-1.json ... \
        --history-in ... --history-out ...

A shard writes only its fetch file; the process step writes every output. A store
whose shard file is missing (the shard job failed or timed out) is "not updated"
and keeps its last good rows, as for any failed store.
"""

from __future__ import annotations

import argparse
import asyncio
import hashlib
import json
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
from pricemon.stores import Store, load_retired, load_stores

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
    # Sharded runs (D-031): this shard of n, its output file, or the shard files to process.
    shard: tuple[int, int] | None = None
    fetch_out: Path | None = None
    fetch_in: list[Path] = field(default_factory=list)
    run_at: datetime | None = None


def daily_order(stores: list[Store], day: Any) -> list[Store]:
    """A daily rotating order: a budget cut never hits the same stores every day."""
    return sorted(stores, key=lambda s: hashlib.sha256(f"{day}|{s.id}".encode()).hexdigest())


def shard_stores(stores: list[Store], day: Any, k: int, n: int) -> list[Store]:
    """Shard ``k`` of ``n`` (1-based): every n-th store of the day's order, so each
    shard gets a mix of stores and the shards are about equally long."""
    if not 1 <= k <= n:
        raise ValueError(f"shard {k}/{n} out of range")
    order = daily_order(stores, day)
    chosen = {s.id for s in order[k - 1 :: n]}
    return [s for s in stores if s.id in chosen]


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

        order = daily_order(stores, day)
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


def process(
    cfg: RunConfig,
    fetches: list[StoreFetch],
    run_at: datetime,
    started: float,
    edge: EdgeGuard | None = None,
    shards: list[dict[str, Any]] | None = None,
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
    retired_closed = 0
    stores_added: list[str] = []
    baseline_rows = 0
    parquet_rows = None
    if not held:
        retired = {r.id for r in load_retired(cfg.stores)}
        result = merge(con, rows, set(per_store), run_at, retired)
        retired_closed = result.retired_closed
        write_snapshot(con, result.open_versions, snapshot)
        append_changes(data, result.events, run_at)
        events_by_type = event_counts(result.events)
        # Stores read for the first time (added to the list): every option is "new",
        # a starting point, not a change (D-031).
        stores_added = sorted(set(per_store) - set(prev))
        baseline_rows = sum(
            1 for e in result.events if e.event == "new" and e.store_id in stores_added
        )
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
        "retired_rows_closed": retired_closed,
        "stores_added": stores_added,
        "baseline_rows": baseline_rows,
        "events": events_by_type,
        "parquet_rows": parquet_rows,
        "requests": sum(f.requests for f in fetches),
        "retries": sum(f.retries for f in fetches),
        "retry_causes": dict(Counter(c for f in fetches for c in f.retry_causes)),
        "edge": _edge_json(edge) if edge is not None else None,
        # Sequential shards of a sharded run (D-031); [] for a single-job run.
        "shards": shards or [],
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


def _edge_json(edge: EdgeGuard) -> dict[str, Any]:
    return {
        "throttle_events": edge.throttle_events,
        "cooldown_s": round(edge.cooldown_s, 1),
        "final_interval_s": round(edge.current_interval_s, 2),
        "halted_reason": edge.halted_reason,
    }


def write_shard(cfg: RunConfig, run_at: datetime) -> int:
    """Fetch this shard's stores and write them for the process step; no other output."""
    assert cfg.shard is not None
    assert cfg.fetch_out is not None
    k, n = cfg.shard
    started = time.monotonic()
    stores = shard_stores(load_stores(cfg.stores), run_at.date(), k, n)
    edge = EdgeGuard(
        interval_s=cfg.edge_interval_s,
        jitter_s=cfg.edge_jitter_s,
        deadline=time.monotonic() + cfg.budget_s,
    )
    fetches = asyncio.run(fetch_all(stores, cfg, run_at.date(), edge))
    payload = {
        "run_at": iso(run_at),
        "shard": [k, n],
        "stores": [s.id for s in stores],
        "duration_s": round(time.monotonic() - started, 1),
        "edge": _edge_json(edge),
        "fetches": [f.to_json() for f in fetches],
    }
    cfg.fetch_out.parent.mkdir(parents=True, exist_ok=True)
    tmp = cfg.fetch_out.with_name(cfg.fetch_out.name + ".tmp")
    tmp.write_text(json.dumps(payload), encoding="utf-8")
    tmp.replace(cfg.fetch_out)
    ok = sum(1 for f in fetches if f.complete)
    print(
        f"shard {k}/{n}: {ok}/{len(fetches)} stores complete, "
        f"{sum(f.requests for f in fetches)} requests, {payload['duration_s']}s",
        flush=True,
    )
    return EXIT_OK


def read_shards(
    cfg: RunConfig, stores: list[Store], run_at: datetime
) -> tuple[list[StoreFetch], EdgeGuard, list[dict[str, Any]]]:
    """The fetches of every shard file, in store-list order; stores of a missing shard
    are failed fetches. Returns the fetches, the combined edge counters and the shards."""
    by_id: dict[str, StoreFetch] = {}
    edge = EdgeGuard(interval_s=cfg.edge_interval_s, jitter_s=cfg.edge_jitter_s)
    edge.current_interval_s = 0.0
    shards: list[dict[str, Any]] = []
    halted: list[str] = []
    for path in cfg.fetch_in:
        if not path.exists():
            continue
        payload = json.loads(path.read_text(encoding="utf-8"))
        if payload.get("run_at") != iso(run_at):
            raise ValueError(f"{path} belongs to run {payload.get('run_at')}, not {iso(run_at)}")
        for f in payload["fetches"]:
            fetch = StoreFetch.from_json(f)
            by_id[fetch.store_id] = fetch
        e = payload["edge"]
        edge.throttle_events += int(e["throttle_events"])
        edge.cooldown_s += float(e["cooldown_s"])
        edge.current_interval_s = max(edge.current_interval_s, float(e["final_interval_s"]))
        if e.get("halted_reason"):
            halted.append(f"shard {payload['shard'][0]}: {e['halted_reason']}")
        shards.append(
            {
                "shard": payload["shard"],
                "stores": len(payload["stores"]),
                "duration_s": payload["duration_s"],
                "requests": sum(int(f.get("requests") or 0) for f in payload["fetches"]),
            }
        )
    if not shards:
        # Every shard failed (or none was downloaded): a crash, not a quiet run in
        # which every store keeps its old prices.
        raise RuntimeError("no shard file to process")
    edge.current_interval_s = edge.current_interval_s or cfg.edge_interval_s
    edge.halted_reason = "; ".join(halted) or None
    fetches = []
    for s in stores:
        found = by_id.get(s.id)
        if found is None:
            found = StoreFetch(store_id=s.id, host=s.host, observed_at=run_at)
            found.reason = "not read: its shard did not finish"
        fetches.append(found)
    return fetches, edge, sorted(shards, key=lambda x: int(x["shard"][0]))


def run(cfg: RunConfig, now: datetime | None = None) -> int:
    started = time.monotonic()
    run_at = (cfg.run_at or now or datetime.now(UTC)).replace(microsecond=0)
    if cfg.shard is not None:
        return write_shard(cfg, run_at)
    if cfg.fetch_in:
        # The run started with its first shard: duration and record time from there.
        started -= max(0.0, (datetime.now(UTC) - run_at).total_seconds())
    stores = load_stores(cfg.stores)
    if cfg.only:
        stores = [s for s in stores if s.id in cfg.only]
    try:
        edge = EdgeGuard(
            interval_s=cfg.edge_interval_s,
            jitter_s=cfg.edge_jitter_s,
            deadline=time.monotonic() + cfg.budget_s,
        )
        shards: list[dict[str, Any]] = []
        if cfg.fetch_in:
            fetches, edge, shards = read_shards(cfg, stores, run_at)
        else:
            fetches = asyncio.run(fetch_all(stores, cfg, run_at.date(), edge))
        code, record = process(cfg, fetches, run_at, started, edge, shards)
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
    p.add_argument("--shard", help="k/n: fetch shard k of n and write --fetch-out only")
    p.add_argument("--fetch-out", type=Path, help="this shard's fetch file")
    p.add_argument("--fetch-in", type=Path, nargs="*", default=[], help="shard files to process")
    p.add_argument("--run-at", help="the run's start (UTC ISO), shared by its shards")
    a = p.parse_args(argv)
    shard = None
    if a.shard:
        k, n = (int(x) for x in a.shard.split("/"))
        shard = (k, n)
        if a.fetch_out is None:
            p.error("--shard needs --fetch-out")
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
        shard=shard,
        fetch_out=a.fetch_out,
        fetch_in=list(a.fetch_in),
        run_at=parse_iso(a.run_at) if a.run_at else None,
    )
    return run(cfg)


if __name__ == "__main__":
    sys.exit(main())
