"""Live checks runner used by .github/workflows/checks.yml.

The sandbox used for development cannot reach shops, so every live check is
described in ``checks/request.yml`` and executed on a GitHub Actions runner.
Results are written to ``checks/results/<id>/`` and committed back to the
branch by the workflow.

Usage::

    python -m pricemon.checks checks/request.yml
"""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import platform
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import yaml

from pricemon.polite import USER_AGENT, EdgeGuard, PoliteConfig
from pricemon.recon import VARIANT_CAP, Candidate, ReconResult, run_recon

RESULTS_DIR = Path("checks/results")


def load_candidates(path: Path) -> list[Candidate]:
    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    out: list[Candidate] = []
    for category, stores in raw["categories"].items():
        for item in stores:
            out.append(Candidate(store=item["store"], domain=item["domain"], category=category))
    return out


def _run_meta(request: dict[str, Any], started: datetime) -> dict[str, Any]:
    return {
        "id": request["id"],
        "check": request["check"],
        "started_utc": started.isoformat(timespec="seconds"),
        "finished_utc": datetime.now(UTC).isoformat(timespec="seconds"),
        "git_sha": os.environ.get("GITHUB_SHA"),
        "run_url": (
            f"{os.environ['GITHUB_SERVER_URL']}/{os.environ['GITHUB_REPOSITORY']}"
            f"/actions/runs/{os.environ['GITHUB_RUN_ID']}"
            if "GITHUB_RUN_ID" in os.environ
            else None
        ),
        "runner": f"{platform.system()} {platform.machine()} / Python {platform.python_version()}",
        "user_agent": USER_AGENT,
    }


def _fmt(value: object) -> str:
    if value is None:
        return "-"
    if isinstance(value, bool):
        return "yes" if value else "no"
    if isinstance(value, list):
        return ",".join(str(v) for v in value) or "-"
    return str(value)


def render_recon_md(meta: dict[str, Any], results: list[ReconResult]) -> str:
    passed = [r for r in results if r.verdict()[0]]
    lines = [
        f"# Recon `{meta['id']}`",
        "",
        f"- started: {meta['started_utc']}, finished: {meta['finished_utc']}",
        f"- run: {meta['run_url'] or 'local'}",
        f"- candidates: {len(results)}, passed: {len(passed)} (variant cap {VARIANT_CAP})",
        f"- run-wide request interval: {meta.get('edge_interval_s')}s + jitter; "
        f"halted: {meta.get('halted_reason') or 'no'}",
        "",
        "| store | category | host | robots | products.json | .js | reachable | shopify "
        "| products | variants | in stock | .js check | JSON-LD cur | Shopify cur "
        "| meta country | reqs | result |",
        "|---|---|---|---|---|---|---|---|---:|---:|---:|---|---|---|---|---:|---|",
    ]
    for r in sorted(results, key=lambda x: (x.category, x.store.lower())):
        ok, fails = r.verdict()
        variants = _fmt(r.variants) + ("+" if r.variants_capped else "")
        share = f"{r.available_share:.0%}" if r.available_share is not None else "-"
        lines.append(
            f"| {r.store} | {r.category} | {r.host} | {r.robots_status} "
            f"| {_fmt(r.robots_products_json)} | {_fmt(r.robots_product_js)} "
            f"| {_fmt(r.reachable)} | {_fmt(r.shopify)} | {_fmt(r.products)} | {variants} "
            f"| {share} | {_fmt(r.js_crosscheck)} | {_fmt(r.jsonld_currency)} "
            f"| {_fmt(r.shopify_currency)} | {_fmt(r.meta_country)} | {r.requests} "
            f"| {'PASS' if ok else 'fail: ' + ', '.join(fails)} |"
        )
    notes = [r for r in results if r.notes or r.stopped_reason]
    if notes:
        lines += ["", "## Notes", ""]
        for r in sorted(notes, key=lambda x: x.store.lower()):
            bits = ([f"stopped: {r.stopped_reason}"] if r.stopped_reason else []) + r.notes
            lines.append(f"- **{r.store}**: " + "; ".join(bits))
    return "\n".join(lines) + "\n"


def run_request(request_path: Path) -> int:
    request = yaml.safe_load(request_path.read_text(encoding="utf-8"))
    check = request["check"]
    out_dir = RESULTS_DIR / str(request["id"])
    out_dir.mkdir(parents=True, exist_ok=True)
    started = datetime.now(UTC)

    if check == "recon":
        candidates = load_candidates(Path(request.get("candidates", "checks/candidates.yml")))
        only = set(request.get("only") or [])
        if only:
            candidates = [c for c in candidates if c.store in only]
        config = PoliteConfig(
            delay_s=float(request.get("delay_s", 3.0)),
            jitter_s=float(request.get("jitter_s", 2.0)),
        )
        edge = EdgeGuard(
            interval_s=float(request.get("edge_interval_s", 2.0)),
            jitter_s=float(request.get("edge_jitter_s", 1.0)),
        )
        results = asyncio.run(
            run_recon(candidates, config, edge, concurrency=int(request.get("concurrency", 4)))
        )
        meta = _run_meta(request, started)
        meta["edge_interval_s"] = edge.interval_s
        meta["halted_reason"] = edge.halted_reason
        payload = {"meta": meta, "results": [r.to_dict() for r in results]}
        (out_dir / "recon.json").write_text(
            json.dumps(payload, indent=2, sort_keys=False) + "\n", encoding="utf-8"
        )
        (out_dir / "recon.md").write_text(render_recon_md(meta, results), encoding="utf-8")
        return 0

    if check == "pipeline":
        # Full dry run of the daily pipeline. Outputs go to checks/results/<id>/data,
        # never to data/; the Parquet file stays in work/ (not committed).
        from pricemon.run import RunConfig
        from pricemon.run import run as run_pipeline

        cfg = RunConfig(
            stores=Path(request.get("stores", "config/stores.yml")),
            data=out_dir / "data",
            history_out=Path("work") / f"{request['id']}.parquet",
            concurrency=int(request.get("concurrency", 3)),
            polite=PoliteConfig(
                delay_s=float(request.get("delay_s", 4.0)),
                jitter_s=float(request.get("jitter_s", 3.0)),
            ),
            edge_interval_s=float(request.get("edge_interval_s", 3.0)),
            edge_jitter_s=float(request.get("edge_jitter_s", 1.5)),
            only=set(request.get("only") or []),
        )
        code = run_pipeline(cfg)
        meta = _run_meta(request, started)
        meta["exit_code"] = code
        (out_dir / "meta.json").write_text(json.dumps(meta, indent=2) + "\n", encoding="utf-8")
        return 0

    print(f"unknown check: {check}", file=sys.stderr)
    return 2


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("request", type=Path, help="path to checks/request.yml")
    args = parser.parse_args(argv)
    return run_request(args.request)


if __name__ == "__main__":
    raise SystemExit(main())
