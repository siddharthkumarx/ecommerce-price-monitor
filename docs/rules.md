# Current rules

The rules the monitor follows today, in one place (D-054). `decisions.md` stays the
history of how each rule came about; where a decision there and this page differ,
this page is current. It replaces the overlapping parts of D-020, D-031, D-033, D-034
and D-036.

## Which stores

- US Shopify stores read through their public `/products.json`, in 10 categories,
  at most 25 per category (`MAX_STORES`, `MIN_PER_CATEGORY` in `sources.py`).
  Stores on other platforms are only listed (`docs/other-platforms.md`).
- A candidate enters only through recon evidence (`checks/results/`), regenerated
  into `config/stores.yml` by `python -m pricemon.sources --stores-yml --out ...`
  (`docs/maintainers.md`). A store listed now keeps its place over a new one.
- **Drop rules (D-004).** A run with a 429, a challenge or a block drops a store. A
  store dropped for 429s may be checked again once, at least 24 hours later, at the
  normal recon pace; a 429 in that retry keeps it out for good (D-052).
- **Content (D-039).** A store is excluded when it really sells adult, tobacco/vape,
  alcohol, cannabis/CBD or weapons products; reviewed false positives are listed by
  exact title in `config/screen-review.yml`.
- **Terms (D-040, D-043, D-045).** Recon and the Terms check read the store's Terms
  (`/policies/terms-of-service`, then the usual `/pages/` handles). The classifier
  fails closed: a page that names robots, scrapers, crawling, data mining or
  automated access anywhere is `ban`, unless that sentence clearly permits it; a
  sentence forbidding commercial reuse is `ban` too. Only `no_ban` and `none_found`
  stores are listed (D-036); `none_found` means no page of the search could be read,
  and such a store is shown by name.
- **Hard check (D-042).** `load_stores` refuses a store without a terms value or with
  `ban`; the run fails before any request.

## How a store leaves

- Only by being retired (D-044, D-049): `python -m pricemon.retire --id <id> --reason
  "<why>"`, then the store list is regenerated. The next run closes its open rows
  without change events; its history stays; every surface shows "retired on
  <date>".
- A store whose Terms turn out to ban robots is retired with `--hide-name`: it gets a
  number ("Store #309"), and the committed data is rewritten once, keyed by the
  number, without its name, host or product handles.
- A run whose snapshot holds a store that is neither listed nor retired stops with
  an error. `--withdraw` takes a store out of the committed data by hand; past run
  totals are never rewritten.
- A store quarantined 14 days in a row is retired with the reason; a replacement is
  proposed in a GitHub issue and goes live only with the owner's approval (D-053; no
  quarantine exists yet, it comes with F1-SCALE).

## How the stores are read

- One run a day at 06:17 UTC, started by the owner's own cron (D-035) with the
  scheduled run and the watchdog as fallbacks; never more than one run a day.
- Sequential shards, one per 60 stores, one after another (D-033): only one runner
  sends requests at a time. Parallel shards stay ruled out (D-020); so do proxies, a
  faster pace and more witness requests.
- Every job stays under 45 minutes; no new store request after 38 minutes (D-020).
- Per shop: robots.txt respected, a delay with jitter between requests, retries only
  on 429, 5xx and network errors with `Retry-After` honoured. Run-wide: one shared
  pace and a 429 cooldown (INC-004) across all shards of a run.
- Every store's US-dollar prices are proven each run, and one product per store is
  checked against a second source (`.js` and the product page, D-010).

## What is published

- Git: `data/latest/snapshot.csv` (open versions), `data/changes/` (every change
  event: the full history), `data/runs.jsonl`, `data/status.json`, badges and
  `data/public/feed.json` (fields only added, never removed or renamed).
- GitHub Releases (D-047): release `history-YYYY-MM` with `events-YYYY-MM-DD.parquet`
  and `snapshot-YYYY-MM.parquet`, built from committed data, uploaded from `main`
  only, once, never replaced or deleted.
- Google Sheet (optional): tabs `changes_30d` and `runs` (D-048).
- The dashboard on Pages, deployed from `main` only (INC-011); the README and its
  visuals, re-rendered by every run.
- A held run publishes nothing (D-006). Only a rows-drop hold is accepted by
  repeating; any other hold repeats until its cause is fixed (D-041).

## Live checks

- Described in `checks/request.yml`, started by hand only (`workflow_dispatch`,
  D-051); pushing the file starts nothing. One checks run at a time (INC-010).
- Results are committed evidence in `checks/results/<id>/`.

## Not built (owner)

Capped product subsets, parallel shards beyond the current sequential ones,
proxies, a faster pace, more witness requests, more than one run a day, a database,
a server, per-product JSON files.
