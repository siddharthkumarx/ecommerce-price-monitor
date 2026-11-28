# Architecture

One scheduled GitHub Actions job fetches every monitored store politely,
validates and normalises the rows, merges them into an SCD2 price history with
DuckDB, derives the day's changes and publishes small files to git, the monthly
history to a Parquet release asset, an optional Google Sheet and a static
dashboard.

```
config/stores.yml ──► fetch ──► validate ──► batch guard ──► normalize ──► history (SCD2)
                        │                        │                            │
                 witnesses + currency       hold the run?                changes
                                                 │                            │
                                           keep last good          outputs: snapshot CSV,
                                                                  change log, runs.jsonl,
                                                                  status + badges, Parquet,
                                                                  Google Sheet, site/
```

## Modules (`src/pricemon/`)

| module | role |
|---|---|
| `polite.py` | `StoreSession` (robots, per-store pacing, retry rules, block detection) and `EdgeGuard` (run-wide pacing, circuit breaker). Every request to a shop goes through it. |
| `witness.py` | Parsers for the three witnesses: `/products.json`, `/products/<handle>.js`, JSON-LD offers; `price_to_cents`. |
| `screen.py` | Excluded-category content screen. |
| `recon.py`, `terms.py`, `sources.py`, `checks.py` | Recon (with the Terms of Service field), the site register and `config/stores.yml`, the live-checks runner. |
| `stores.py` | Loads `config/stores.yml` into `Store` objects (with `terms`) and its `retired` list; category titles. |
| `display.py` | How a store is named and linked on public surfaces: listed stores by name, retired stores labelled (D-046). |
| `fetch.py` | Per store: robots, all `/products.json` pages, a daily sample of `.js` and product pages, currency proof. Returns raw catalog rows plus a `StoreFetch` report. |
| `models.py` | Pydantic `VariantRow` (the validation rules). `StoreFetch` lives in `fetch.py`, `ChangeEvent` in `changes.py`. |
| `guard.py` | The batch guard (row validation itself is the Pydantic model). |
| `normalize.py` | Raw Shopify JSON to `VariantRow` (integer cents, UTC, fixed availability values). |
| `history.py` | DuckDB SCD2 merge, snapshot CSV. |
| `releases.py` | The history mirror on GitHub Releases: immutable per-day event files and month-end snapshots (D-047). |
| `retire.py` | Retire a store (with `--hide-name` for a Terms ban), or withdraw one by hand (D-044, D-049). |
| `changes.py` | Change events between the previous and new open versions. |
| `outputs.py` | Change log, `runs.jsonl`, `status.json`, shields.io badge files, snapshot aggregates (DuckDB). |
| `schedule.py` | The cron slots of `daily.yml` and `watchdog.yml` as data (tests keep them equal), the gate that decides every daily trigger (on-time dispatch with `slot`, late schedule events, the watchdog; INC-007, INC-009), and the on-time / late / missed slot accounting. |
| `feed.py` | The public feed `data/public/feed.json` (`steadydata.feed/v1`), rewritten atomically after every ok or partial run. |
| `alert.py` | Whether a run needs an alert, and the alert text. |
| `report.py` | Facts about the latest real run (sample rows, changes, quality counts) for the README, visuals and dataset card. |
| `readme.py` | Renders `README.md` and `data/README.md` from `templates/` (D-022). |
| `visuals.py` | Generates `assets/hero.svg`, `pipeline.svg`, `maintenance-loop.svg` (D-022). |
| `sheets.py` | Google Sheet publish with `GOOGLE_SA_JSON` (skips cleanly without it). |
| `site.py` | Static dashboard build into `site/`. |
| `run.py` | The daily pipeline entry point and exit codes. |

## Fetch and witnesses

For each store in `config/stores.yml`, sequentially within the store and paced
run-wide by `EdgeGuard`:

1. `GET /robots.txt` (plain). Paths used: `/products.json`, `/products/<handle>.js`,
   `/products/<handle>`. A disallowed path stops that store for the run.
2. `GET /products.json?limit=250&page=N&country=US` for N = 1, 2, ... until a page
   returns fewer than 250 products. This witness gives **all rows**.
3. Sample cross-check: `SAMPLE_PER_STORE` products (1, D-010) chosen by a stable
   hash of `(run date, store id, product id)`, so the sample rotates daily and is
   reproducible. For each: `GET /products/<handle>.js?country=US` (integer cents;
   price and availability must match `/products.json` for every shared variant)
   and `GET /products/<handle>?country=US` (JSON-LD offers: `priceCurrency`,
   `price`, `availability`; `Shopify.currency.active`).
4. **Content screen:** the catalog is screened for excluded categories; a hit not
   reviewed in `config/screen-review.yml` stops the store (`excluded`) and alerts.
5. **Currency proof:** every sampled product page must show USD (JSON-LD
   `priceCurrency`, or `Shopify.currency` when the theme has no JSON-LD offer).
   Any other currency observed means the presentment changed (geo, Markets
   config): the **run is held**. A store whose proof could not be obtained
   (block, network) is a failed store, not a held run.
6. A witness mismatch (`.js` or JSON-LD price differs from `/products.json`) marks
   the store `mismatch`; mismatched stores do not update history in that run.

Only parsed fields are kept in memory; raw bodies are never written to disk.

## Validation and batch guard

`VariantRow` (Pydantic, strict):

- `price_cents > 0`
- `compare_at_cents` is `None` or `>= price_cents`. A Shopify `compare_at_price`
  below the price is a stale merchant value: normalize sets it to `None` and
  counts it (`compare_at_ignored`), so the rule holds without losing the row.
- `availability` in the fixed list `("in_stock", "out_of_stock")`. JSON-LD
  availability URIs map through a fixed table; an unknown value fails validation.
- ids are positive integers; `observed_at` is timezone-aware UTC.

Rows failing validation are rejected and counted per store. The **batch guard**
compares the run with the last good run and **holds** it when:

- the run-wide row count falls by more than 20 %, or one store's rows fall by
  more than 50 % (minimum 20 rows before);
- more than 5 % of matched variants run-wide (at least 200), or more than 20 % in
  one store (at least 10), move by a suspicious factor (new price below 0.2x or above 5x
  the old price), which points at a unit or parsing error rather than a sale;
- more than 90 % of all matched variants (at least 200) change price with no
  compare-at price on either side (a sale explains itself, D-017);
- the currency proof fails (above) or validation rejects more than 2 % of rows.

A held run writes `runs.jsonl` and `status.json` (status `held`, reasons) but
does not touch the snapshot, change log, history or Sheet: the last good data
stays live. If the same hold reason for the same stores repeats in the next run
the condition is treated as real and accepted (recorded as
`accepted_after_repeat` in `runs.jsonl`), so a genuine catalog cut does not hold
the monitor forever. Only rows-drop holds are accepted this way (D-041): a currency,
suspicious-price, reject or mass-change hold repeats until its cause is fixed.

## History (SCD2 in DuckDB)

One row per version of a variant's observable state:

| column | type | note |
|---|---|---|
| `store_id` | VARCHAR | from `config/stores.yml` |
| `product_id`, `variant_id` | BIGINT | Shopify ids |
| `handle`, `product_title`, `variant_title` | VARCHAR | for display and links |
| `price_cents`, `compare_at_cents` | BIGINT | integer cents, USD |
| `available` | BOOLEAN | |
| `valid_from` | TIMESTAMPTZ | run start (UTC) when this version was first seen |
| `valid_to` | TIMESTAMPTZ | run start when it was replaced or the variant disappeared; `NULL` = current |

Key: `(store_id, variant_id, valid_from)`. Tracked attributes (a change opens a
new version): `price_cents`, `compare_at_cents`, `available`. Title changes are
updated in place on the open version (not a price event).

State between runs is the **open versions**, committed as
`data/latest/snapshot.csv` (sorted, no per-run timestamps, so git diffs only show
real changes). Each run loads it into DuckDB, merges the new observations
(stores that failed or mismatched keep their open versions unchanged), and
writes:

- the new snapshot CSV and the run's change events (`data/changes/YYYY/YYYY-MM-DD.csv`).

The change log is the full history: every version starts with an event (`new`,
a price, compare-at or stock change) and ends with the next one. After the data
commit, a run on `main` mirrors it to GitHub Releases (`pricemon.releases`, D-047):
release `history-YYYY-MM` gets `events-YYYY-MM-DD.parquet` for every day that is over
and `snapshot-YYYY-MM.parquet` (the committed snapshot at the end of the month, read
from git history) for every month that is over. A file is uploaded once and never
replaced or deleted, so a run that failed after its upload cannot leave the mirror
ahead of git, and a failed upload is repaired by the next run.

## Changes

Derived from the SCD2 merge (old open version vs new observation):

| event | rule |
|---|---|
| `new` | variant id not in the previous open versions (store fetched completely) |
| `removed` | previous open variant missing from a complete fetch of its store |
| `price_up` / `price_down` | `price_cents` rose / fell |
| `discount_start` / `discount_end` | discounted means `compare_at_cents > price_cents`; transition either way |
| `out_of_stock` / `back_in_stock` | `available` true to false / false to true |

One observation can raise several events (a sale is usually `price_down` +
`discount_start`). Events carry old and new values and the percentage change.

## Outputs

| output | where | size control |
|---|---|---|
| latest snapshot | `data/latest/snapshot.csv` (+ `snapshot.json` summary for the site) | only open versions |
| daily change log | `data/changes/YYYY/YYYY-MM-DD.csv` (runs of a day append) | events only |
| run log | `data/runs.jsonl`, one JSON line per run | small |
| status | `data/status.json` and `data/badges/*.json` (shields.io endpoint schema: days running, last run, on time, missed runs, rows today) | small |
| full history | the change log in git; release `history-YYYY-MM`: `events-YYYY-MM-DD.parquet`, `snapshot-YYYY-MM.parquet` | written once, from `main` only (D-047) |
| Google Sheet | tabs `changes_30d`, `runs` (no `latest` tab, D-048) | only if `GOOGLE_SA_JSON` and `GOOGLE_SHEET_ID` are set |
| dashboard | `site/` (static, Pages after publish) | built from `data/` |

A CI test fails if any tracked file is 50 MB or larger.

"Missed runs": scheduled slots (from the cron expressions) since the first run
with no `runs.jsonl` entry of status `ok`/`partial` within 3 hours after the slot.

## Workflows

| workflow | trigger | notes |
|---|---|---|
| `ci.yml` | every push | commit-message check, ruff, mypy, pytest, gitleaks, pip-audit, file-size check |
| `checks.yml` | `workflow_dispatch` only (D-051) | live checks; commits `checks/results/<id>/` |
| `daily.yml` | `17 6 * * *` (the Black Friday extra runs ended on 27 Nov 2026, D-031); `workflow_dispatch` | job `timeout-minutes: 45` (D-020), no request after 38 minutes, a `pages` job that deploys `site/` when `vars.PAGES_ENABLED` is `true` (D-026), `concurrency: daily` (no cancel), commits `data/`, uploads Parquet, publishes Sheet, builds `site/`. A failed or held run opens or updates a GitHub issue labelled `run-alert` and fails the job (GitHub's failure email). A `slot` gate job skips a scheduled run whose slot is already filled (D-027) and runs an on-time dispatch (`slot` time, or `auto` from the owner's own cron) once per slot (D-028, D-030). |
| `watchdog.yml` | `47 8 * * *`, `47 16 * * *`; `workflow_dispatch` | if no ok, partial or held run started since the latest daily slot and none is queued or running: starts `daily.yml`, opens or updates a `run-alert` issue, fails (INC-007, D-027) |

Scheduled workflows run on the default branch, `main`. GitHub can start a slot
hours late or drop it (INC-006, INC-007); the watchdog covers both.

## Exit codes of `python -m pricemon.run`

`0` ok, `2` partial (some stores failed, history updated for the rest), `3` held,
`1` crashed. The workflow commits outputs for every code and alerts on 2 only
when more than 20 % of stores failed, and always on 1 and 3.
