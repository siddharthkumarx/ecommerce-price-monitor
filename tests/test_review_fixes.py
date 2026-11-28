"""Fixes from the fresh review of F1-EXPAND (D-036, D-033, D-037)."""

from __future__ import annotations

import asyncio
import json
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import duckdb
import pytest
import yaml

import pricemon.run as run_mod
from pricemon.display import Display
from pricemon.fetch import StoreFetch
from pricemon.normalize import normalize_products
from pricemon.publicdata import (
    _withdraw_run,
    public_fetch,
    rekey_files,
    rekey_month_file,
)
from pricemon.run import RunConfig, carried_edge, run
from pricemon.sources import collect
from pricemon.stores import RetiredStore, Store
from tests.test_outputs import catalog, fetched

ROOT = Path(__file__).resolve().parents[1]
RUN_AT = datetime(2026, 11, 28, 6, 17, 30, tzinfo=UTC)
SNAP = "store_id,handle,product_title,variant_title\nkeep,h,T,V\ngone,h2,T2,V2\nold,h3,T3,V3\n"


def _data(tmp_path: Path) -> Path:
    data = tmp_path / "data"
    (data / "latest").mkdir(parents=True)
    (data / "latest" / "snapshot.csv").write_text(SNAP)
    return data


def test_retired_stores_alone_never_allow_a_withdrawal(tmp_path: Path) -> None:
    data = _data(tmp_path)
    retired = [RetiredStore("old", "Old", "audio", RUN_AT.date())]
    assert rekey_files(data, Display([], retired)) == []
    assert (data / "latest" / "snapshot.csv").read_text() == SNAP


def test_a_list_far_shorter_than_the_data_withdraws_nothing(tmp_path: Path) -> None:
    data = _data(tmp_path)
    one = [Store("keep", "Keep", "audio", "keep.example", terms="no_ban")]
    # Two stores would leave with one listed: refused (a truncated list, not a decision).
    snap = data / "latest" / "snapshot.csv"
    snap.write_text(SNAP + "other,h4,T4,V4\n")
    assert rekey_files(data, Display(one, [])) == []
    assert "gone,h2" in snap.read_text()
    # One store leaving with one listed is a withdrawal.
    snap.write_text(SNAP)
    retired = [RetiredStore("old", "Old", "audio", RUN_AT.date())]
    assert rekey_files(data, Display(one, retired)) == [snap]
    assert "gone" not in snap.read_text()
    assert "old,h3" in snap.read_text()


def test_a_failed_store_that_leaves_is_counted_once() -> None:
    record: dict[str, Any] = {
        "started_at": "2026-11-08T13:29:52Z",
        "stores_total": 3,
        "stores_ok": 2,
        "stores": [
            {"store_id": "a", "status": "ok", "variants": 5, "requests": 3},
            {"store_id": "b", "status": "ok", "variants": 4, "requests": 3},
            {"store_id": "x", "status": "failed", "variants": 0, "requests": 1},
        ],
        "stores_not_updated": [{"store_id": "x", "reason": "blocked"}],
        "guard": {"holds": [{"key": "rejects:nécessaire", "message": "nécessaire"}]},
    }
    _withdraw_run(record, {"a", "b"}, {})
    assert record["stores_total"] == 2
    assert record["stores_ok"] == 2
    assert record["withdrawn_stores"] == 1
    # A non-ASCII store id in a guard hold is matched too.
    _withdraw_run({"stores": [{"store_id": "nécessaire"}], "guard": record["guard"]}, {"a"}, {})
    assert record["guard"]["holds"] == []


def test_reasons_of_a_store_shown_by_number_name_no_url_or_handle() -> None:
    s = Store("acme", "Acme Audio", "audio", "acmeaudio.com", terms="ban", public_no=17)
    d = Display([s], [], ("ban",))
    f = StoreFetch(store_id="acme", host="acmeaudio.com", observed_at=RUN_AT)
    f.reason = "robots.txt disallows https://acmeaudio.com/products/acme-pro.js?country=US"
    out = public_fetch(d, f)
    assert out.reason == "robots.txt disallows a store URL"
    assert d.reason("acme", "acme-pro-headphones: .js mismatch; acme-buds: .js mismatch") == (
        "a product: .js mismatch; a product: .js mismatch"
    )
    assert d.reason("acme", "excluded category: alcohol") == "excluded category: alcohol"
    plain = Store("b", "B", "audio", "b.example", terms="no_ban")
    assert Display([plain]).reason("b", "x: y https://b.example/") == "x: y https://b.example/"


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


def test_a_store_whose_terms_ban_robots_is_never_read(monkeypatch: pytest.MonkeyPatch) -> None:
    called: list[str] = []

    async def fake_fetch_store(session: Any, store: Store, day: Any) -> StoreFetch:
        called.append(store.id)
        return fetched(store.id, catalog(1), RUN_AT)

    monkeypatch.setattr(run_mod, "fetch_store", fake_fetch_store)
    stores = [
        Store("ok", "Ok", "audio", "ok.example", terms="no_ban"),
        Store("no", "No", "audio", "no.example", terms="ban", public_no=3),
    ]
    cfg = RunConfig(stores=Path("x"), data=Path("y"))
    out = asyncio.run(run_mod.fetch_all(stores, cfg, RUN_AT.date()))
    assert called == ["ok"]
    assert out[1].reason == "not read: its terms ban automated access (D-036)"
    assert out[1].requests == 0


def test_an_earlier_month_file_loses_stores_that_left(tmp_path: Path) -> None:
    path = tmp_path / "price_history_2026-10.parquet"
    con = duckdb.connect()
    con.execute(
        "COPY (SELECT * FROM (VALUES ('keep', 1, 1, 'h', 'T', 'V', 100, NULL, true, "
        "TIMESTAMPTZ '2026-10-01 06:17:00+00', NULL), ('gone', 2, 2, 'h2', 'T2', 'V2', 200, "
        "NULL, true, TIMESTAMPTZ '2026-10-01 06:17:00+00', NULL)) t(store_id, product_id, "
        "variant_id, handle, product_title, variant_title, price_cents, compare_at_cents, "
        "available, valid_from, valid_to)) TO '" + str(path) + "' (FORMAT parquet)"
    )
    keep = [Store("keep", "Keep", "audio", "keep.example", terms="no_ban")]
    assert rekey_month_file(path, Display(keep, [])) == 1
    ids = duckdb.connect().execute("SELECT store_id FROM read_parquet(?)", [str(path)]).fetchall()
    assert ids == [("keep",)]
    assert rekey_month_file(path, Display(keep, [])) == 0


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
    assert "Withdraw from earlier months" in names
    assert Counter(names)["Withdraw from earlier months"] == 1
