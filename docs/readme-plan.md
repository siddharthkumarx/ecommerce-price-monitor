# README plan (notes only)

The README and animated SVGs are written last, from real run data, following the
owner's README rules (not received yet). Until then, collect here what the
README should be able to show, and where the numbers will come from.

## Candidate content

- One-line pitch: daily price, discount and stock monitor for US D2C brands on
  Shopify; N stores, M variants (from `data/status.json`).
- Live badges (shields.io endpoint, `data/badges/*.json`): days running, last
  run, missed runs, rows today.
- What it tracks: price up/down, discount start/end, out of stock / back in
  stock, new / removed variants (counts from `data/changes/`).
- Black Friday / Cyber Monday window (26 Nov to 1 Dec 2026, 4 runs a day): share
  of variants discounted per category per day; biggest moves. Source: Parquet
  history.
- How it stays polite: robots.txt, per-store delay, run-wide pace, Retry-After,
  stop on challenge; INC-001 as an honest example of learning from a run.
- Data quality: three witnesses, currency proof, batch guard, holds (counts from
  `runs.jsonl`).
- Outputs: snapshot CSV, change log, Parquet, Google Sheet, dashboard
  screenshots.

## Animated SVG ideas (data from real runs only)

- Pipeline flow (fetch, validate, guard, history, outputs) with run counts.
- Discount share per category over the BF/CM window.
- Stock flips per day.

## Facts to keep handy

- Recon funnel: candidates, selected, dropped by reason (`docs/sources.md`).
- First scheduled run date and days running (`data/runs.jsonl`).
