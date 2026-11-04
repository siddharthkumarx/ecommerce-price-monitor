# Decisions

Numbered, newest last. Each: decision, why, consequences. Change a decision by
adding a new entry that supersedes it, not by editing history.

## D-001 - Stack, versions and licenses (2026-11-03)

Python 3.12 managed with uv 0.11.32 (`uv.lock` committed, CI uses
`uv sync --locked`). Versions checked on PyPI / npm / GitHub on 2026-11-03:

| package | version | license | use |
|---|---|---|---|
| httpx | 0.28.1 | BSD-3-Clause | HTTP client (async) |
| protego | 0.7.0 | BSD-3-Clause | robots.txt per RFC 9309 (wildcards, `$`, longest match) |
| pydantic | 2.14.2 | MIT | row and run models, validation |
| duckdb | 2.0.0 | MIT | SCD2 merge, CSV/Parquet IO |
| pyarrow | 26.0.1 | Apache-2.0 | Parquet schema and writing |
| gspread | 6.2.1 | MIT | Google Sheet publish |
| google-auth | 2.62.1 | Apache-2.0 | service-account credentials for gspread |
| PyYAML | 6.0.3 | MIT | config and check requests |
| ruff | 0.17.3 | MIT | lint and format (dev) |
| mypy | 2.4.1 | MIT | strict type checking (dev) |
| pytest | 9.2.0 | MIT | tests (dev) |
| pip-audit | 2.10.1 | Apache-2.0 | dependency vulnerability audit (CI) |
| gitleaks | 8.30.1 | MIT | secret scan (CI, release binary with checksum) |
| @fontsource/instrument-sans | 5.3.0 | OFL-1.1 | self-hosted font files |
| @fontsource/ibm-plex-mono | 5.3.0 | OFL-1.1 | self-hosted font files |
| actions/checkout | v7.0.1 (`3d3c42e`) | MIT | pinned by commit SHA |
| astral-sh/setup-uv | v10.3.3 (`68559e9`) | MIT | pinned by commit SHA |
| actions/upload-artifact | v7.0.2 (`cf430e0`) | MIT | dashboard artifact, pinned by commit SHA |
| Playwright for Node | pre-installed in the sandbox | Apache-2.0 | `scripts/screenshots.cjs` (dev only) |

Protego was chosen over `urllib.robotparser` because the standard library
parser does not implement `*`/`$` wildcards, which Shopify's default robots.txt
uses (`/collections/*sort_by*`, `/products/*-remote`).

## D-002 - Live checks only on GitHub Actions (2026-11-03)

The sandbox cannot reach shops, and production also runs on GitHub-hosted
runners, so recon and pipeline dry runs run there too: same network, same IP
reputation. A push that changes `checks/request.yml` triggers
`.github/workflows/checks.yml`; results are committed to `checks/results/<id>/`
and kept as evidence. The commit is made by `github-actions[bot]`.

## D-003 - robots.txt handling (2026-11-03)

RFC 9309: 2xx parsed; 4xx means no restrictions; 5xx or network failure means
disallow all; redirects followed (max 5), and the final host becomes the
canonical store host. Our group is `ecommerce-price-monitor`, falling back to
`*`. `Crawl-delay` raises the per-store delay. robots.txt is fetched without
`country=US`: it is a site policy file, not a data request. Every other store
request carries `country=US`.

## D-004 - Store selection and drop rules (2026-11-03, owner rules)

Owner rules applied to all recon evidence (`checks/results/recon-00*/`), coded
in `src/pricemon/sources.py`:

- drop a store that showed a challenge or block in **any** recon run, needed
  429 retries, or whose robots.txt disallows a path we use;
- drop adult, tobacco/vape, alcohol, cannabis/CBD and weapons stores;
- at least 4 stores per category; if fewer than 30 remain, add candidates in the
  weakest categories and recon once more, then continue with what passes
  (minimum 25).

Interpretations:

- `recon-001` counts, although its challenges were caused by our own run-wide
  pace (INC-001). The rule says "any recon run".
- `recon-001` to `recon-003` recorded the number of retries but not their HTTP
  status. Any retry in those runs is treated as a 429 (conservative). From
  `recon-004` on, retry causes are recorded and only `http 429` drops a store.
- A failed latest recon (not Shopify, more than 3,000 variants, currency not
  proven USD, witness mismatch, empty catalog) also drops the store.
- Within a category, at most 8 are selected: US shops first (`/meta.json`
  country), then larger catalogs (more observations per request). The rest are
  reserve.

Effect: after `recon-003` only 12 stores were left (audio 6, apparel 6, every
beauty, home and outdoor candidate had been challenged in `recon-001`), so
`recon-004` added 60 never-contacted candidates in those three categories, at
half the `recon-002` pace because a single 429 retry now drops a store.

Result after `recon-004` (14 of 60 passed; 24 needed 429 retries even at about
0.17 requests/s run-wide): **30 stores, 14,357 variants** (audio 6, apparel 6,
beauty 5, home & kitchen 6, outdoor 7), 142 dropped, every drop listed with its
evidence in `docs/sources.md`. Four of the 30 passed only after a reviewed
content-screen false positive (D-016).

## D-005 - Pace and run-time budget (2026-11-03)

Owner rule: one full run must finish in under 30 minutes at the polite pace.

Daily pace (defaults in `src/pricemon/run.py`): per store 4 s + 0-3 s jitter
between requests; run-wide 3 s + 0-1.5 s (`EdgeGuard`); 3 stores in flight.
That is about 0.27 requests/s for the whole run, below `recon-002` (about 0.4/s),
where many stores needed retries.

Requests per run, from the recon catalog sizes of the 30 stores: robots.txt (30)
+ `/products.json` pages (37; one page per 250 products, plus the short last
page) + 2 sampled products x (`.js` + product page) (120) = **187 requests**.

Estimate: `recon-004` measured 6.82 s per request at a 5 s mean run-wide
interval, i.e. about 1.8 s of latency and per-store waiting on top of the pace.
At the daily 3.75 s mean interval: 187 x (3.75 + 1.8) s = **about 17 minutes**,
plus about 3 minutes of retry headroom (backoff and Retry-After up to 120 s on a
few stores) = **about 20 minutes**, inside the 30-minute budget. The pipeline
step has a 32-minute timeout and the job 40 minutes.

Measured, `pipeline-001` (2026-11-03, concurrency 3): **31.5 minutes**, over budget
(INC-003). 231 requests including 67 retries, every one an HTTP 429. Stores
waiting out a backoff left the run-wide pace idle. Change: 5 stores in flight
with the same run-wide pace, so the total request rate does not rise.
`pipeline-002` (5 in flight): Shopify answers every throttled request with
`Retry-After: 60`, and honouring it per store escalated to challenges (INC-004).
Final design: a 429 pauses the whole run for its Retry-After and slows the
run-wide pace adaptively (x1.5 per 429, eased back after 10 successes); one
witness product per store (127 requests per run); and a hard 27-minute budget
after which no request starts, so a run always ends inside 30 minutes, at the
cost of a `partial` status if Shopify throttles hard. Estimate without throttling:
127 x (3.75 + 1.0) s = about 10 minutes; each 429 adds about 60 s run-wide.
`pipeline-003` measures it.

## D-006 - Currency proof holds the run (2026-11-03, owner rule)

Prices are only meaningful as USD. Each run proves the presentment currency on
sampled product pages requested with `country=US` (JSON-LD `priceCurrency`, or
`Shopify.currency.active` when the theme has no JSON-LD offer; Kosas and Ember
are such stores in recon). Any non-USD currency observed holds the whole run,
because the cause (runner geo, Markets settings) is unlikely to be confined to
one store. A store whose proof could not be fetched is a failed store instead.

## D-007 - Stale compare-at prices (2026-11-03)

Shopify merchants often leave `compare_at_price` equal to or below the price.
The validation rule is `compare_at >= price`. A `compare_at` below the price is
set to `None` during normalisation and counted (`compare_at_ignored` per store in
`runs.jsonl`) instead of rejecting the row: the price itself is valid and
dropping the row would create false `removed` events. `compare_at == price` is
kept and is not a discount.

## D-008 - Batch guard thresholds and repeat acceptance (2026-11-03)

Thresholds are in `docs/architecture.md` (Validation and batch guard). They are
set so that sitewide sales (Black Friday: many variants down 10-50 %, with a
compare-at) pass, and parse or unit errors (cents vs dollars is a 100x move) or a
half-empty catalog response hold. A hold that repeats for the same reason and
stores in the next run is accepted, so a real catalog change does not hold the
monitor indefinitely.

## D-009 - Where state lives (2026-11-03)

DuckDB is the in-run engine, not a committed database file. Between runs the
state is the open SCD2 versions in `data/latest/snapshot.csv` (git, small diffs).
The full history is the monthly Parquet release asset. This keeps git small
(every file under 50 MB) and gives a portable, columnar history.

## D-010 - Witness sample size (2026-11-03)

`products.json` covers every row. The `.js` and JSON-LD witnesses cost one
request each per product, so they are sampled: 2 products per store per run,
chosen by a stable hash of the run date, store and product id. Changed from 2 to
1 product per store after INC-004 to keep the run inside the time budget: over a
month this still covers about 30 products per store.

## D-011 - Content screen (2026-11-03)

Whole-word keyword screen over product title, type and tags (no descriptions are
read). One match flags the store; up to three matching titles are kept as
evidence. A short allow-list removes known harmless phrases ("wine glass"). The
screen runs in recon and in every daily run (a flagged store is stopped and an
alert raised).

## D-012 - Alerts (2026-11-03)

A failed or held run fails the `daily` job (GitHub emails the owner on failed
scheduled runs) and opens or comments on one open issue labelled `run-alert`.
No external alerting service, no extra secrets.

## D-013 - Schedule (2026-11-03)

Daily at `17 6 * * *` UTC (an odd minute avoids the top-of-hour queue on
GitHub-hosted runners; 06:17 UTC is 01:17 US Eastern, after most nightly price
updates). From 26 Nov to 1 Dec 2026 three more slots (00:17, 12:17, 18:17 UTC)
make 4 runs a day across the Black Friday / Cyber Monday window. The extra cron
lines name those days only, so they fire again in 2027 unless removed;
`build-progress.md` has a follow-up item for that.

## D-014 - Actions pinned by commit SHA (2026-11-03)

Third-party actions are pinned to a full commit SHA with the version in a
comment, so a moved tag cannot change what runs with `contents: write`.

## D-015 - Product titles are kept, descriptions and images are not (2026-11-03)

The dashboard and change log must say which product changed. Product and variant
titles and the handle are identifiers, not descriptive content; `body_html`,
images and media are never read into storage.

## D-016 - Reviewed content-screen hits (2026-11-03)

The content screen matched nine `recon-004` stores; every match was a false
positive (a shade name "Contour Stick - Whiskey", a pun "Bum Bums & Spirits", an
empty "Titanium Wine Flask", a car-socket "Cigarette Adapter", wine glassware and
vinegar). Stores are not dropped for a hit a person has reviewed: each review in
`config/screen-review.yml` names the store, category, the **exact** product
titles, the verdict and the reason. Only those titles are skipped, in the
register and in the daily screen (`screen_reviewed` in `config/stores.yml`); any
other matching title flags the store again and raises an alert. Five of the
nine also failed on 429 retries and stay dropped; four (Westman Atelier, Sol de
Janeiro, Six Moon Designs, Goal Zero) are selected.

## D-017 - Mass-change rule counts only unexplained changes (2026-11-03)

Found by an end-to-end test: one store's 20 % sale was 100 % of matched variants
and held the run. A Shopify sale sets a compare-at price (and its end removes
it), so changes where either side is discounted are explained. The 90 %
mass-change rule counts only unexplained changes, and run-wide shares need at
least 200 matched variants. Supersedes the mass-change line of D-008.

## D-018 - $0 variants are out of scope, not validation failures (2026-11-04)

`pipeline-001` rejected 255 rows, every one for `price_cents` = 0: free gifts,
samples and add-on variants (JLab, HydraPak, Branch Basics, Crown Affair, Shokz,
Jones Road). The owner rule `price > 0` stays; such variants are skipped before
validation and counted as `free_variants` in `runs.jsonl`. They no longer count
towards the 2 % reject share, which is meant to catch malformed data. A missing
or unparseable price is still a reject.
