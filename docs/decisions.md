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
| Jinja2 | 3.1.6 | BSD-3-Clause | README and dataset-card templates |
| Markdown | 3.11.2 | BSD-3-Clause | private explainer PDF (dev only) |
| Simple Icons | 16.36.0 | CC0-1.0 | tool logos in `assets/pipeline.svg` |
| ffmpeg (system, libx264) | sandbox build | LGPL/GPL | `media/linkedin-hero.mp4` encoding (dev only) |
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
interval, i.e. about 1.8 s of latency and per-store waiting on top of the pace
(that run also included 429 backoffs, so the true overhead is lower).
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
`pipeline-003` measured **27.9 minutes**, 21 of 30 stores, 36 x 429 with
`Retry-After: 60` and no challenges; the budget cut the last 7 stores. The
daily run uses these settings. Stores start in a daily rotating order so a
budget cut is spread across stores over the days. `pipeline-004` showed the
throttle is per IP and long-lived (INC-005).

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
alert raised). Superseded in part by D-039: since screen v2, tags are not read and a
match counts only when the product is the excluded thing.

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

## D-019 - JSON-LD is a soft witness for prices (2026-11-04)

`pipeline-003`: Richer Poorer's JSON-LD showed $8.00 where `/products.json` and
`.js` both showed $3.00, and Sol de Janeiro's $26.00 against $39.00. Both stores'
catalog and `.js` (the same Shopify backend) agreed. Themes build JSON-LD
themselves and some get variant offers wrong. Rule: a `.js` mismatch blocks the
store (status `mismatch`, not updated); a JSON-LD price difference alone is
recorded per store as `jsonld_disagrees` in `runs.jsonl` and does not block.
JSON-LD stays the currency proof (D-006).

## D-020 - 45-minute run on one runner, 25 stores (2026-11-04, owner decision)

Owner rule: one daily run must finish in under 45 minutes on a single runner,
reached with a smaller store list. Parallel jobs are ruled out: spreading requests
over several runners' IPs would work around Shopify's per-IP limit (INC-005),
which this project never does. Until the public publish, Actions minutes are a
private budget of 2,000 a month shared with another repository.

- **Store list:** the best 25 stores, at least 4 per category (`MAX_STORES`,
  `MIN_PER_CATEGORY` in `src/pricemon/sources.py`). Ranking inside a category:
  US shops first, then fewest recon caveats (shop not registered in the US;
  USD proven by the theme only, no JSON-LD offer; needed a reviewed content-screen
  hit), then larger catalogs. Trimming moves the weakest store (most caveats,
  from the largest category, smallest catalog) to reserve until 25 remain.
  Result: audio 6, apparel 5, beauty 4, home & kitchen 5, outdoor 5; 12,037
  variants. Reserve: Koio, Westman Atelier, Goal Zero, Six Moon Designs (reviewed
  screen hits) and Otherland (theme-only currency proof). All in `docs/sources.md`.
- **Budget:** no new store request after 38 minutes (`RunConfig.budget_s`); the
  pipeline step times out at 41 minutes and the job at 45, which covers setup,
  the Parquet upload and the data commit.
- **Requests per run:** 25 robots.txt + 31 `/products.json` pages + 25 `.js` + 25
  product pages = 106. Estimate: about 8-9 minutes without throttling; about 27
  minutes at the throttling `pipeline-003` saw (15.3 s per successful request
  including 429 cooldowns).
- **`.js` sample not reduced further:** it is already 1 product per store per run
  (D-010). Fewer would leave some stores without a `.js` cross-check on a given
  day, which weakens the witness check, so the saving (at most 25 requests) is
  not taken.
- **Minutes:** a daily run bills about 10-30 minutes plus setup; a CI push bills
  about 4 minutes (4 jobs, rounded up per job); a `checks` run bills its duration.
  Live checks are therefore requested only when they answer a question.

## D-021 - BFCM runs per day are one workflow flag (2026-11-04, owner decision)

From 26 Nov to 1 Dec 2026: 4 runs a day only if the repository is public by
26 Nov, otherwise 2. The switch is `env.BFCM_RUNS_PER_DAY` ("2" or "4") at the
top of `.github/workflows/daily.yml`. Slots: 06:17 every day, 18:17 on BFCM days,
and 00:17 and 12:17 on BFCM days only when the flag is "4". Those two extra slots
pass through a 2-minute `slot` job that reads the flag; every other trigger skips
that job, so it costs nothing on normal days. The pipeline reads the same
variable (`schedule.active_crons`), so "missed runs" counts only slots meant to
run. Supersedes the BFCM part of D-013.

## D-022 - The README and its visuals are generated from every run (2026-11-04, owner rules)

The README is a portfolio page whose readers are clients first. Every number, row
and change in it comes from the latest real run, so it is rendered, not written:

- `templates/README.md.j2` (Jinja2) is the source; `python -m pricemon.readme`
  renders `README.md` and the dataset card (`data/README.md`) from
  `pricemon.report.collect()`: `runs.jsonl`, the snapshot, the run's change log
  and `config/stores.yml`. The daily workflow renders both after every run and
  commits them with `data/`. Growing numbers (days running, runs, missed runs,
  rows today) are shields.io endpoint badges reading `data/badges/*.json`.
- `python -m pricemon.visuals` writes `assets/hero.svg` (problem, the run with
  three real rows, the result as one number), `assets/pipeline.svg` (the five
  steps with the logos of the tools this repo uses) and
  `assets/maintenance-loop.svg` (a drawn timeline labelled EXAMPLE around the real
  INC-004, ending on the real count of daily runs). SVG rules: fonts embedded as
  base64 WOFF2, CSS animation only, a 9 s loop holding the final frame, final frame
  as the default state (still images and `prefers-reduced-motion`), at least 22 px
  text in a 1000 px viewBox, under 1 MB. `tests/test_readme.py` enforces them.
- Static media are rendered by `scripts/make_media.sh` (Playwright and ffmpeg):
  `assets/dashboard.png` (2x), `assets/social-preview.png` (1280 x 640, no growing
  numbers since it is uploaded once) and `media/linkedin-hero.mp4` (1080 x 1080,
  10 s, H.264, text at least 40 px).
- Plain words above "For engineers": no protocol names or status codes in the client
  sections and visuals.

## D-023 - Data license (2026-11-04)

Prices and stock levels are facts; the dataset is shared as a compilation under CC
BY 4.0 with attribution, while store and product names remain their owners'. No
images or descriptions are stored, so no store content is republished. The code is
MIT. Opt-out: email, removal within 24 hours (README, dataset card).

## D-024 - Portfolio additions beyond the brief (2026-11-04)

Added because a top-tier data or scraping portfolio repository is expected to have
them:

- **Dataset card** (`data/README.md`, Hugging Face format, re-rendered every run)
  and **CITATION.cff**: the data is reusable and citable.
- **Downloadable CSV in the release**: the month's release also carries
  `latest-prices.csv`, and it is marked as the latest release, so "Download the
  data" gives a non-technical reader a spreadsheet, not only Parquet.
- **LICENSE** (MIT) and a stated data license (D-023).
- **SECURITY.md**: a private reporting address and what secrets exist.
- **Dependabot** (`.github/dependabot.yml`): monthly updates for pinned Actions and
  uv dependencies.
- **Internal link check** in pytest (every relative link and heading anchor in the
  repository's Markdown resolves).
- **Publish checklist** (`docs/publish-checklist.md`): the ordered steps from this
  private repository to the public one, including removing `docs/private/` and
  stopping this repository's schedule so two copies never collect the same stores.

## D-025 - Review fixes: still frames, phone sizes, offer, commit policy (2026-11-04)

From an independent review that rendered every SVG:

- **Still frame.** Browsers do not pass the viewer's motion preference into an
  SVG loaded as `<img>`, so the SVG's own `prefers-reduced-motion` rule never
  fires in the README: a still or reduced-motion view showed the hero's first beat
  and an almost empty timeline. Now every visual is written twice: animated
  (`name.svg`) and as its final frame (`name-still.svg`, no animation). The README
  uses `<picture><source media="(prefers-reduced-motion: reduce)"
  srcset="name-still.svg">`, which the page itself evaluates. Inside the animated
  SVG the final frame is the default style and, under reduced motion, is forced
  with `!important` (opacity, stroke dashes), not only `animation: none`.
  `scripts/check_visuals.cjs` (Playwright) checks that the reduced-motion render
  and the still `<img>` match the final frame (compared at quarter size, because
  Chromium anti-aliases text in animated layers differently from static text) and
  that the hero's result number is visible; as a control, the first frame must
  differ clearly from the final one; `tests/test_visuals_render.py` runs it, and the
  `visuals` workflow runs it on GitHub with Playwright installed.
- **Phone size.** In the 1000 px viewBox: headings at least 36 px, every other
  text at least 30 px (the small EXAMPLE label excepted); hero rows are
  "store · short product" and the price. Enforced in `tests/test_readme.py`.
- **Offer.** The README offers daily or weekly delivery as CSV, Excel, Google
  Sheets or a database; nothing faster and no API until proven on a real job.
- **Commit-message policy, tool-neutral.** No trailers except `Signed-off-by`, and
  no "Generated with" footer. Trailers are found with `git interpret-trailers`, after
  dropping `---` lines (git stops reading trailers there). No tool names in the
  hook, its pattern file (`.githooks/forbidden-footer`), the CI check, the tests or
  the README.
- **Publishing** goes to a fresh public repository with a clean `main`; this one
  is never renamed (`docs/publish-checklist.md`).

## D-026 - GitHub Pages deploy, and BFCM at 4 runs a day (2026-11-05, owner decisions)

- **Pages.** The `daily` workflow packages `site/` with
  `actions/upload-pages-artifact` (v5.0.0) and a separate `pages` job deploys it
  with `actions/deploy-pages` (v5.0.1), both pinned by commit SHA. The deploy job
  holds only `pages: write` and `id-token: write` and runs in the `github-pages`
  environment. Both are skipped unless the repository variable `PAGES_ENABLED` is
  `true`, so nothing deploys before Pages is switched on. A held run is deployed
  too: the dashboard shows the held status, with the last good data.
- **BFCM.** The repository has been public since 5 Nov 2026, so under D-021
  `BFCM_RUNS_PER_DAY` is `"4"`: 00:17, 06:17, 12:17 and 18:17 UTC from 26 Nov to
  1 Dec 2026. "Missed runs" counts those four slots on those days.

## D-027 - Same-day watchdog and late-slot skip (2026-11-06, INC-007)

- **Watchdog, not a second daily cron.** A backup cron inside `daily.yml` would
  share the schedule that failed, so the guard is a separate workflow,
  `watchdog.yml`, at 08:47 and 16:47 UTC (`WATCHDOG_CRONS` in `schedule.py`,
  tested against the file). These are not run slots: "missed runs" still counts
  only the `daily.yml` slots.
- **What counts as run:** a `runs.jsonl` record of status ok, partial or held that
  started at or after the latest slot. A held run counts, because a second run
  hours later would accept the hold before the owner looked at it (D-008). A
  crashed run does not, so the watchdog retries once; the crash already raised
  its own alert.
- **No double runs:** the watchdog does nothing while a daily run is queued or
  running. A scheduled run that finds its slot already filled skips the pipeline.
  At most one extra run per slot, and only when no run has filled the slot.
- **Notice:** a `run-alert` issue (a comment if one is open) and a failed
  workflow run, the same channel as a failed daily run.

## D-028 - On-time dispatch per slot, honest slot accounting (2026-11-20, INC-009)

- **The schedule is a fallback, not the clock.** Each slot is started by an
  external `workflow_dispatch` with input `slot`; GitHub's `schedule` event and
  the watchdog remain, and skip once the slot is filled. One gate decides for
  every trigger (`pricemon.schedule.gate`), so a dispatch, a late schedule event
  and a watchdog rescue all follow the same rule: at most one pipeline run per
  slot unless someone starts a manual run (no `slot`), which always runs.
- **The trigger's token** is a fine-grained personal access token limited to this
  repository with only "Actions: read and write" (plus the implied metadata read),
  90-day expiry. It is never stored in the repository.
- **Accounting:** on time = a good run started within 2 h after the slot; late =
  the first good run started later the same UTC day; missed = no run. A run
  belongs to the latest slot at or before its start, so one late run never fills
  two slots. "Missed runs" now means exactly that.
- **Shown to readers** (owner decision, design check of 2026-11-20): delivery
  ("daily runs delivered", every slot) is the headline; on time is counted only
  from the first slot the on-time trigger dispatched, so it measures the trigger,
  not GitHub's late scheduler. Earlier slots stay in `status.json` and the run
  history, with a one-sentence note computed from the run log.

## D-030 - On-time trigger with `slot: auto` (2026-11-22, owner decision; trigger corrected by D-035)

- **Trigger:** an external scheduler (recorded here as cron-job.org; it is the owner's
  own cron, D-035) calls `POST
  https://api.github.com/repos/siddharthkumarx/ecommerce-price-monitor/actions/workflows/daily.yml/dispatches`
  with headers `Authorization: Bearer <token>` and `Accept:
  application/vnd.github+json` and the fixed body
  `{"ref":"main","inputs":{"slot":"auto"}}`, in UTC at `17 6 * * *`, plus
  `17 0,12,18` on 26-30 Nov and 1 Dec. The token is as
  in D-028 (fine-grained, this repository only, Actions read and write, 90 days).
- **Why `auto`:** a simple cron service cannot put the slot time in the body, and
  the explicit form (`2026-11-26T06:17Z`) needs it. `auto` means the active slot
  (`active_crons()`, so the BFCM slots follow `BFCM_RUNS_PER_DAY`) within 10
  minutes of now, before or after; none means skip with a one-line reason and no
  run. A resolved slot then takes exactly the explicit-slot path of the gate:
  EARLY wait, at most one pipeline run per slot, `dispatch.by` "" = the on-time
  trigger. The run records the resolved slot, not `auto`. `check` and empty keep
  their meaning.

## D-029 - SteadyData light look for the dashboard and README visuals (2026-11-20, owner decision)

- **Palette and type** as in `docs/maintainers.md`, "Dashboard look". The dark theme
  (D-022) is retired. Teal `#0E8A7D` and amber `#D98E14` are below 4.5:1 on white,
  so they colour marks only; every mark carries a text label and every chart's
  numbers are also in a table.
- **Charts without script:** the daily charts are HTML and CSS bars built by
  `site.py` from the same daily rows as the public feed (baseline run excluded),
  diverging around one axis on one shared scale: price rises over drops, sales
  started over ended, back in stock over sold out.
- **Links:** "Built by SteadyData · Get a free sample" and the contact call to
  action go to https://steadydata.co/contact/.


## D-031 - F1-EXPAND: 250-300 stores, freeze lifted, JLab retired, terms field, display rule, one run a day (2026-11-27, owner decision)

- **Freeze lifted.** The Black Friday freeze (25 Nov 18:00 UTC to 2 Dec) ends on
  27 Nov 2026: Black Friday data is not needed for outreach (cold email starts after
  15 Dec), and the bigger store set needs its first days of history before then.
- **Store set.** From 25 stores to 250-300 in 10 categories of 20-25 stores, each a
  demo competitor set (audio, apparel, beauty, home & kitchen, outdoor, coffee & tea,
  fitness, pet, tech accessories, toys & kids). 554 new candidates in
  `checks/candidates.yml` (`since: recon-005` and `since: recon-006`); the drop rules
  of D-004 apply unchanged. Stores on other platforms are listed for later in
  `docs/other-platforms.md`; no other platform is collected.
- **JLab retired.** `jlab` leaves the list (`config/retired.yml`, owner decision):
  its history stays in `data/` as written, the next run closes its open rows without
  change events, and every surface shows it as "retired on 27 Nov 2026".
- **Terms field.** Recon reads `/policies/terms-of-service` once per store (at most 2
  requests, one retry or one same-host redirect, and only where robots.txt allows it)
  and records `terms`: `ban` (a sentence forbids robots, spiders, scrapers, crawlers,
  automated access, data mining or commercial reuse of the content), `no_ban` (read,
  no such sentence) or `none_found` (not read: disallowed by robots.txt, missing, or
  no policy text), with the first matching sentence (at most 300 characters) in the
  recon results. Liability, warranty, purchase-for-personal-use and privacy lines are
  not bans. Shopify's default robots.txt disallows `/policies/`, so most stores are
  `none_found`; Shopify's default terms template forbids "spider, crawl, or scrape",
  so most readable pages are `ban`.
- **Selection.** Inside a category `no_ban` first, then `none_found`, then `ban` only
  to fill it (HQ review A4); at most 25 per category, 300 in all. *Superseded by
  D-036: a `ban` store is never selected.*
- **Display rule.** *The "every kept store is monitored" part is superseded by D-036;
  the display rule stays as a safety net.* Every kept store is monitored and counts in every total. A store
  whose `terms` value is in `anonymise_terms` (`config/public.yml`, now `[ban]`) is
  shown on the README, dashboard, feed and media as "Store #<n> (<category>)", with
  no name, host or product links (`pricemon.display`); public data files follow D-034.
- **Schedule.** One run a day at 06:17 UTC again. The extra slots due before the lift
  (26 Nov 00:17, 12:17, 18:17; 27 Nov 00:17, 12:17, 18:17) stay in the slot accounting
  (`BFCM_2026_END`); no cron line names them, so nothing fires in 2027. The on-time
  trigger keeps `slot: auto` and needs only its 06:17 UTC line (D-035).
- **Capacity.** Sequential shards (D-033).

## D-032 - Code under PolyForm Noncommercial 1.0.0, data under CC BY-NC 4.0 (2026-11-27, owner decision)

From the commit that adds `LICENSE-HISTORY.md` on, the code is licensed under the
PolyForm Noncommercial License 1.0.0 (`LICENSE`, with the owner's `Required Notice`
line) and everything under `data/` under CC BY-NC 4.0 (`data/LICENSE`, the official
legal code). Commits before that were MIT (code) and CC BY 4.0 (data); copies taken
from them keep those licenses (`LICENSE-HISTORY.md`). The README license section and
badges, the dataset card and `CITATION.cff` say the same. Supersedes the license part
of D-001, D-023 and D-024. Commercial use: ask the owner.

## D-033 - Sequential shards inside the daily workflow (2026-11-27, owner decision)

With 250-300 stores one run needs more requests than one job's 38-minute request
budget allows at the unchanged pace. The daily workflow therefore reads the stores
in shard jobs that run **one after another** (`max-parallel: 1`), then one process
job merges the shard files and writes every output once. The per-shop spacing, the
run-wide pace and the run-wide 429 cooldown are unchanged; at any moment only one
runner sends requests, so the run-wide rate is that of a single runner. Parallel
shards stay ruled out (D-020): they would spread requests over several IPs at once.
Each shard is a job under 45 minutes with its own 38-minute budget; a shard that
fails leaves its stores "not updated" (partial run); no shard file at all is a crash.
The stores of a shard are every n-th store of the day's rotating order. Supersedes
the "single runner" part of D-020; the 45-minute limit now holds per job. The shard
count follows the store list: one shard per 60 stores (`STORES_PER_SHARD` in
`schedule.py`), planned by the slot job (D-036). recon-005 and recon-006 spent about
a third of their time in run-wide 429 cooldowns; 60 stores take about 20 minutes at
the unchanged pace, which leaves room for that inside each 38-minute budget.

## D-034 - Public data never names a store shown without its name (2026-11-27, HQ review)

- **Fixed numbers:** every listed store gets a public number once, in
  `config/aliases.yml` (written by `python -m pricemon.sources --stores-yml`, never
  changed, removed or reused), and `public_no` in `config/stores.yml`. "Store #n"
  and the alias id `store-<nnn>` follow from it, so they stay with the same store
  when the list is regenerated or stores leave.
- **Public data files:** a store whose `terms` value is in `anonymise_terms` is keyed
  by its alias id in the snapshot, the change logs, the run log (and so
  `status.json`), the monthly Parquet history and its CSV copy, and the shard
  artifacts, with an empty handle and its name taken out of product and variant
  titles, tags and evidence strings (`pricemon.publicdata`). Every run first rekeys
  files written under an earlier config (idempotent). Run logs on Actions print
  alias ids too.
- **Not covered, by design:** `config/stores.yml`, `config/aliases.yml`, the recon
  evidence in `checks/results/` and `docs/sources.md` must name stores and hosts for
  the collector and the drop rules to work, and git history keeps earlier commits.
  A reader of the repository can therefore still match an alias to a store; only a
  private store list would close that.

## D-035 - On-time trigger is the owner's own cron (2026-11-27, owner correction)

The external on-time trigger of D-028 and D-030 is the owner's own cron, not
cron-job.org; the request (URL, headers, fixed body `{"ref":"main","inputs":{"slot":"auto"}}`)
and the token rules are unchanged. Since D-031 it needs one line, `17 6 * * *` (UTC).

## D-036 - Only stores whose terms do not ban robots are monitored (2026-11-27, owner decision)

Supersedes the "every kept store is monitored" part of D-031 and the 250-store list
of 27 Nov (never published on `main`).

- **Rule.** The public monitor carries only stores whose recon `terms` value is
  `no_ban` or `none_found`. A store whose Terms of Service ban robots, scrapers or
  automated access (`ban`) is dropped by `pricemon.sources` ("terms ban, not
  monitored") and is never fetched by the daily run. It is not in
  `config/stores.yml`, not in `config/aliases.yml`, and not in any data file, the
  feed, the README, the media or the release assets.
- **Start.** 71 stores from recon-001..006: 56 `no_ban`, 15 `none_found`. Inside a
  category a store already monitored keeps its place over a new one with the same
  terms value; at most 25 per category. Scotch Porter (beauty) was listed first
  and then left again: the content screen matches "Scotch" in its brand name on
  every product, which a review of exact titles cannot cover, so its review was
  taken out and the store is dropped (excluded category).
- **Public data holds only monitored and retired stores.** Every run withdraws any
  other store from the snapshot, the change logs, the monthly Parquet history (and
  so `latest-prices.csv`) and the run log (`pricemon.publicdata`). Run-log totals
  of earlier runs are reduced by what a withdrawn store contributed: store counts,
  requests and change events exactly, observed and live rows by its variant count
  (an approximation within that run's `free_variants`); other totals
  (`free_variants`, `compare_at_ignored`, `parquet_rows`, guard counts) stay as
  measured. A record names how many stores it lost in `withdrawn_stores`. The first
  run under this rule withdrew 18 of the 24 stores monitored before. A store that
  should keep its history when it leaves must be retired (`config/retired.yml`);
  with no store list at all nothing is withdrawn.
- **What stays.** Git history before this decision still holds the earlier data and
  lists; the recon evidence (`checks/results/`) and the site register
  (`docs/sources.md`) keep naming every candidate checked, with its drop reason.
- **Numbers.** `config/aliases.yml` lists only monitored stores; its `next` value is
  the lowest number never given, so a number is never reused.
- **Safety net.** `anonymise_terms: [ban]` in `config/public.yml` and
  `pricemon.display` stay: a `ban` store that reached the list by mistake would
  still be shown by number only.
- **Shards.** The slot job plans one shard per 60 listed stores (D-033): 2 shards
  for 71 stores.
- **Measured (first run, `20261127T184909Z`).** 71 of 71 stores in 2 shards of
  9.5 and 9.2 minutes, 19.5 minutes of reading and 20 minutes wall time, 303
  requests, 0 retries, no 429 and no run-wide cooldown; 38,317 rows. Actions minutes
  are free on the public repository (about 20 runner-minutes per run).
- **Repository growth.** The first run added 1.05 MB packed, once: 35,424 baseline
  rows in the change log and the snapshot. A normal run at 25 stores added 6 to 14 KB
  packed; at 71 stores (3.2 times the rows) about 20 to 50 KB a day is expected, and
  about 40 to 100 KB at 150 stores, plus about 1 MB once for each batch of 70 or so
  new stores. `.git` is 12 MB today, so about 20 to 25 MB is projected at 90 days;
  `snapshot.csv` is 5.9 MB (about 12 MB at 150 stores), far under the 50 MB file
  limit. Storage stays in git (owner); the 06:17 run of 28 Nov gives the first
  steady-state figure.
- **Growth.** Toward about 150 stores (about 15 per category, at most 25), never a
  `ban`: new candidate lists from recon-007 on, US Shopify stores not contacted
  before, weighted to the thin categories (apparel, toys & kids, tech accessories,
  fitness first), same recon pace and terms field as recon-005. Passing `no_ban` and
  `none_found` stores join in batches after each recon.
- **Batch 2 (28 Nov).** 129 stores from recon-001..009 (98 `no_ban`, 31
  `none_found`), 58 new, none dropped: 37 from recon-007, 16 from recon-008, 4
  recovered by the re-check under D-039 (recon-009) and Maple Landmark (one reviewed
  title, `config/screen-review.yml`). Per category, `no_ban`/`none_found`: apparel 6/2,
  audio 9/2, beauty 11/1, coffee & tea 9/4, fitness 12/8, home & kitchen 11/2,
  outdoor 7/3, pet 10/2, tech accessories 11/2, toys & kids 12/5. Scotch Porter is
  back: screen v3 finds no excluded product in its catalog. 3 shards (one per 60
  stores). Of recon-008's 172 candidates 70 passed, 54 of them `ban` (not added).
- **Measured (batch 2, `20261128T004003Z`, manual run on `main`).** 128 of 129
  stores in 3 shards of 43 (11.6, 11.7 and 11.8 minutes), 36 minutes wall time, 555
  requests, 0 retries, no 429 and no cooldown; 68,311 rows, 30,004 of them new
  baseline rows. Dagne Dover (monitored since batch 1) was not updated: the product
  it sampled as a witness answered 404 on `.js` and on its page, so US dollars were
  not proven; it keeps its last good prices and is read again on the next run.

## D-037 - A duplicated variant is not a validation reject (2026-11-27)

The first 72-store run was held: Barebones Living lists some variants under two
products in a single `/products.json` page (17 of 454 rows), which the validation
counted as rejects, above the 2 % share that holds a run (D-008 guard). The first
copy of such a variant is kept and nothing is missing, so a repeated variant id is
now counted apart (`duplicate_variants` in the run log, a new field), as $0 variants
are since D-018, and the reject share does not see it. A variant that is really lost
because pages shifted shows up as falling rows, which the rows-drop guard still holds.

## D-038 - Fresh review of F1-EXPAND: fixes (2026-11-27)

One fresh-reviewer pass over the whole change (c3acc62 to the review); every High and
Medium finding is fixed, with tests in `tests/test_review_fixes.py`.

- **Withdrawal needs a real store list (High).** Retired stores alone no longer allow
  a withdrawal, and a run never withdraws more stores than are listed: a wrong or
  truncated `config/stores.yml` leaves public data alone and says so in the log.
- **A withdrawn store counts once (High).** A failed store is in both `stores` and
  `stores_not_updated`; it was subtracted twice from `stores_total`. Fixed, and the
  two affected run records (`20261108T132952Z`, `20261127T182554Z`) were repaired
  from their originals in git history.
- **Failure reasons of a store shown by number (High).** A reason can hold a store
  URL or product handles; for such a store it is scrubbed in shard files, the run
  log and the Actions log (`Display.reason`).
- **A failed read does not lift a ban (High).** A proven `ban` stands until a later
  run reads the Terms page and finds no ban.
- **The run-wide pace carries across shards (Medium).** Each shard downloads the
  earlier shards' files of its run and starts at their slowest run-wide interval; if
  an earlier shard halted for anything but its own time budget (the edge refusing
  this IP), the later shards send no request.
- **Earlier months (Medium).** After uploading this month's history, the run brings
  every earlier `data-YYYY-MM` release asset (Parquet and `latest-prices.csv`) to the
  current keys with `python -m pricemon.publicdata`, so a store that left also leaves
  them.
- **One store list per run (Medium).** The slot job records the commit it planned
  the shards from; every shard checks out that commit.
- **Low findings fixed:** a store whose terms ban robots is never read at run time,
  even if it reached the list (`fetch_all`); a repeated variant id is a duplicate
  before validation, whatever its first copy was; guard holds naming a store with a
  non-ASCII id are matched. Not changed: a store that leaves the list and later
  returns gets a new number (numbers are never reused, D-036); retired stores are
  matched by config id, which is enough while no store is shown by number.


## D-039 - Content screen v2: a store is excluded only for a product it really sells (2026-11-27, owner request)

Evidence from `recon-005` and `recon-006` (`content_flags` in `recon.json`): safe-Terms
stores were excluded because a word matched inside a title that is not an excluded
product, a colour ("Pouch - Wine/Gold", "Hiapo - Rum / Dark Wood"), a scent
("Sandalwood & Tobacco Musk"), merch ("Black Seal Rum T-Shirt", "Rifle Patch ...
Snapback Hat", "THC Black Tee"), a homeware or tech object ("Wine Coaster", "Cigarette
Lighter Socket Splitter"), a dog toy ("Barking Beer"); and Derma E and Scotch Porter
were flagged on titles with no excluded word at all ("Ultra Hydrating Day Cream", "Leave-In
Beard Conditioner"). Those matches came from product **tags**, which v1 read and did not
record: Shopify tags carry colour filters ("Tobacco" for brown suede, the same cause
as Nisolo's "Huarache Slip On Brown") and marketing terms such as "CBD-free".

The rule (`src/pricemon/screen.py`), simplest that fits every case above:

- **Fields:** title and `product_type`. Tags are read for cannabis/CBD words only
  (negations stripped): `recon-007` showed a store titling its chews "Hemp Calming"
  and naming CBD only in a tag, while colour filters never name cannabis.
- **Negations never count:** "CBD-free", "non-alcoholic", "Non-CBD".
- **Colourway:** a word only in the short variant tail of a title (after " - ", " | ",
  "{" or " in ", at most four words, no quantity such as "750 ml" or "40%") does not
  count.
- **Merch:** a tee, shirt, hat, cap, sticker, patch, poster, toy and the like carrying
  the word does not count.
- **Objects:** for alcohol, tobacco and weapons words, a coaster, glass, flask,
  stopper, candle, scent, lotion, coffee, charger, socket, cable, case, strap, boot,
  leather and the like does not count. The noun must sit outside the matched phrase,
  so "Pepper Spray" is not excused by "spray".
- **Always counts:** adult phrases (no exemption at all); CBD and cannabis words and
  the strict words nicotine, e-liquid, vape and vaping on any object ("CBD Body
  Lotion", "Nicotine Pouches"), excused only by merch and negations.
- **Plurals match** ("Premium Cigars", "Rifles"): v1 missed them.
- One real product is still enough to exclude a store; there is no catalog-share
  threshold.

Real titles from the evidence are regression tests in both directions
(`tests/test_screen.py`): 28 false positives pass, 23 real alcohol, tobacco/vape,
CBD, weapons and adult products are still flagged, and one real product among false
positives still flags its store.

Screen versions: 1 up to `recon-007`; 2 in `recon-008`, which started before the
cannabis-tag rule (tags not read at all); 3 from `recon-009`. Every daily run
screens each store's whole catalog with the current version and stops a flagged
store, so a store added from a v2 row is screened with tags on its first run.

Recon rows now record `screen_version` and `content_evidence` (the field and word
that fired), and a later row screened by a newer version supersedes the content flags
of earlier rows (`sources.StoreRecord.drop_reasons`); flags from runs of the same
version still drop a store if any run has them. Reviews in `config/screen-review.yml`
(D-016) stay valid and are still honoured.

Scope, by the owner: only `no_ban` and `none_found` stores whose sole drop reason was
"excluded category" are re-checked, by a recon run with the same politeness and the
Terms field. A store that also failed on something else stays out: "catalog too
large" (Kiel James Patrick, OluKai, Kassatex, Bear KompleX; the variant cap is not
changed, F1-SCALE) or a 429 retry (D-004). A store whose terms are `ban` is never
added (D-036). On the stores monitored today, v2 over their current titles finds only
one hit, which is already reviewed, so the daily run excludes no store it did not
exclude before.

Result (`recon-009`, 28 Nov, 31 requests, no retries): Jeffree Star Cosmetics,
Klean Kanteen, NEST New York (`no_ban`) and Scotch Porter (`none_found`) pass and
join the list. Derma E stays out: `content_evidence` shows the word "CBD" in the
`product_type` of three products (the day cream, a vitamin C serum, the DMAE
moisturizer), which counts as the product's own type; whether that is a mislabel is
for a person to check on the store, not for the screen to guess. Recon-008 (screen
v2) excluded one safe store for a false positive, Maple Landmark ("Wine Decorative
Block", a wooden letter block), now reviewed by exact title; Beyond Yoga ("Lift Your
Spirits Bra") is also "catalog too large" and stays out. The safe-store count went
from 108 to 113 for recon-001..007 with the re-check, then to 129 with recon-008.

## D-040 - The Terms classifier fails closed (2026-11-28, owner, F1 deep review)

The F1 deep review (read-only, at `39bd35b`) found that `pricemon.terms` split a page
at every `<li>` and `<br>` and then needed the prohibition word in the same sentence
as the automation word, so "You agree not to:" followed by a bullet "use any robot,
spider, scraper" read as `no_ban`.

- **Rule.** `no_ban` only when no automation word appears anywhere in the policy text:
  robot, spider, scraper, crawl, bot, data mining, data harvesting, automated or
  automatic means, access, tools, programs and the like. Otherwise `ban`, unless that
  sentence clearly permits it ("is permitted", "you may", "we allow"), forbids
  nothing and is not about search engines. A sentence that forbids commercial reuse
  of the site's content is still a ban.
- **Evidence.** The first sentence that names automated access and forbids
  something; else the first that names it. A list item is shown after the line that
  introduces it ("You agree not to: use any robot, spider, scraper").
- **Cost, accepted.** A page that names automation for another reason (a liability
  line about automated systems, a product called a robot) is a ban. A store page
  (`/pages/...`, D-043) is read from its `<main>` element, so menus and footers do
  not count.
- Tests: three list-style ban pages (the example above among them), the fail-closed
  cases, a permission sentence (`tests/test_terms.py`).

## D-041 - Only a rows drop is accepted by repeating (2026-11-28, owner, F1 deep review)

A held run was accepted when the next run had the same hold keys (D-008). The keys
`currency:`, `suspicious:`, `rejects:` and `mass_change:` qualified, so a store
showing CAD prices on two days in a row would have been published as US dollars on
day 2. Now `guard.accept_repeat` accepts a repeat only when every key is
`rows_drop:*` (a store or the run really shrank). Any other hold repeats until its
cause is fixed or the store leaves the list. Test: two CAD runs in a row publish
nothing for that store (`tests/test_outputs.py`).

## D-042 - The store loader refuses a missing terms value and a ban (2026-11-28, owner, F1 deep review)

`stores.Store` defaulted `terms` to `none_found` and `load_stores` turned a missing
field into `none_found`, so a store with unread terms could look safe. `terms` is now
required, and `load_stores` raises on a store without it or with `ban` (D-036): a run
with such a list fails before any request.

## D-043 - Terms check and full Terms search (2026-11-28, owner)

- **Search.** Recon and the Terms check read `/policies/terms-of-service` and, when
  it is missing, disallowed or has no policy text, `/pages/terms-of-service`,
  `/pages/terms-and-conditions`, `/pages/terms-conditions`, `/pages/terms` and
  `/pages/tos`, each where robots.txt allows it, at most 2 requests each, and stop at
  the first page with policy text. `none_found` now means no page of that search
  could be read; the reason of the first page is kept.
- **Terms check** (`check: terms` in `checks/request.yml`). Reads robots.txt and the
  Terms search of the listed stores, nothing else, at the recon pace. A store
  stopped before the end (a block, a 429 past its retries) is `unread` and keeps the
  value recon gave it. `pricemon.sources` takes a Terms check row as the newest terms
  reading of a store already in the recon evidence; the drop rules (D-004) read recon
  rows only. Sources are ordered by the time their run started, not by their name.

## D-044 - Retiring a store, and a store whose Terms turn out to ban robots (2026-11-28, owner)

A store leaves the monitor on purpose by `python -m pricemon.retire --id <id>
--reason "<why>"`: an entry in `config/retired.yml` with the date and the reason
(new field `reason`), then `config/stores.yml` is regenerated. No run reads it again;
its rows leave the live snapshot in the next run (`retired_rows_closed`) and its
history stays in `data/`.

A store whose Terms now ban robots (D-040) is retired with `--hide-name`: it is
retired under its fixed number (`store-017`, the `public_no` it had while listed,
shown as "Store #17") and the command rewrites the committed public data once: the
snapshot, the change logs and the run log are keyed by the number, product handles
and the host are emptied, and the store's name is taken out of product titles and
failure reasons. It then searches `data/` for the name and lists any file that still
holds it. The next published run regenerates the feed, the status, the README, the
dashboard and the visuals from that data. The recon evidence (`checks/results/`) and
the site register (`docs/sources.md`) keep naming every store checked, as before.
