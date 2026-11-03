"""Decide whether the last run needs an alert, and write its text.

    python -m pricemon.alert --data data --code 3 --out alert.md

Alert when the run crashed (1) or was held (3), when the pipeline step produced
no exit code (killed, timed out), or when a partial run (2) left more than
``PARTIAL_ALERT_SHARE`` of stores not updated. Writes ``--out`` only when an alert
is needed; the workflow opens or comments on the ``run-alert`` issue from it.
"""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

from pricemon.outputs import read_runs

PARTIAL_ALERT_SHARE = 0.20


def needs_alert(code: int | None, record: dict[str, Any] | None) -> bool:
    if code in (None, 1, 3) or record is None:
        return True
    if code == 2:
        total = record.get("stores_total") or 0
        not_updated = len(record.get("stores_not_updated") or [])
        return bool(total) and not_updated / total > PARTIAL_ALERT_SHARE
    return False


def render(code: int | None, record: dict[str, Any] | None, run_url: str | None) -> str:
    lines = [f"Pipeline exit code: `{code if code is not None else 'none (step did not finish)'}`"]
    if run_url:
        lines.append(f"Workflow run: {run_url}")
    if record:
        lines += [
            "",
            f"- run: `{record['run_id']}`, status **{record['status']}**",
            f"- stores updated: {record.get('stores_ok', '?')} of "
            f"{record.get('stores_total', '?')}",
        ]
        if record.get("error"):
            lines.append(f"- error: `{record['error']}`")
        for hold in record.get("guard", {}).get("holds", []):
            lines.append(f"- hold `{hold['key']}`: {hold['message']}")
        for s in record.get("stores_not_updated") or []:
            lines.append(f"- not updated `{s['store_id']}` ({s['status']}): {s['reason']}")
    lines += ["", "The last good data stays live until a run succeeds."]
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--data", type=Path, default=Path("data"))
    p.add_argument("--code", default="")
    p.add_argument("--run-url")
    p.add_argument("--out", type=Path, default=Path("alert.md"))
    a = p.parse_args(argv)
    code = int(a.code) if a.code.strip().isdigit() else None
    runs = read_runs(a.data)
    record = runs[-1] if runs else None
    if needs_alert(code, record):
        a.out.write_text(render(code, record, a.run_url), encoding="utf-8")
        print(f"alert written to {a.out}")
    else:
        print("no alert")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
