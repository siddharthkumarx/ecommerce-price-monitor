# Maintainers' guide

Working notes for any agent continuing this build. Read this file, then
`docs/build-progress.md` ("Continue here" below points at the next item).

## Goal

A daily price, discount and stock monitor for US direct-to-consumer brands on
Shopify (the store list is `docs/sources.md`, machine copy `config/stores.yml`).
It will become the public portfolio repo `ecommerce-price-monitor` of Siddharth
Kumar (web scraping freelancer, siddharthkumar.com), so it must look and work like
production-grade expert work, and **every number shown anywhere must come from a
real run** (recon results, `data/runs.jsonl`, Parquet history). Never type a
number by hand into docs, README, dashboard or SVGs.

## Hard rules

### Git

- Identity (already set in this clone): `user.name "Siddharth Kumar"`,
  `user.email 273157498+siddharthkumarx@users.noreply.github.com`. Set it again in
  a fresh clone before the first commit.
- `git config core.hooksPath .githooks`. Commit-message policy: no trailers except
  `Signed-off-by`, and no "Generated with" footer. The `commit-msg` hook removes
  them; the `ci` workflow job `commit-messages` fails on any commit that has one.
- Never open a pull request. Work on `main` and push it.
- `main` is the repository's default branch, and scheduled runs commit
  `data/` to it too. Always `git pull --rebase` before you push. The workflows'
  own commits retry their push with `git pull --rebase` (up to 4 times).
- Small, meaningful commits (`area: what and why`). Update
  `docs/build-progress.md` after every item.
- Every file in git stays under 50 MB. Full price history lives only in the
  monthly Parquet release assets, not in git.

### Live checks

The development sandbox cannot reach shops. Never request a shop from the
sandbox. Every live check runs on GitHub Actions:

1. Edit `checks/request.yml` (new `id`, a `check` type, arguments).
2. Commit and push to `main`. `.github/workflows/checks.yml` runs on
   any push that changes that file (`permissions: contents: write`).
3. The workflow commits results to `checks/results/<id>/` on the same branch.
4. `git pull` and read them. Results are evidence: keep them committed.

Check types: `recon` (store recon, see `src/pricemon/recon.py`), `pipeline`
(full dry run of the daily pipeline into `checks/results/<id>/`, never into
`data/`).

### Scraping

- robots.txt is respected (RFC 9309, Protego). Unreachable robots.txt (5xx or
  network) means disallow all; 4xx means no rules.
- `country=US` on every store request (robots.txt itself is fetched plain).
- Per-store delay with jitter; one run-wide pace for the shared Shopify edge
  (`EdgeGuard`, see INC-001); Crawl-delay wins when larger.
- Retries only for HTTP 429, 5xx and network errors; honour `Retry-After`
  (longer than 120 s stops the store).
- A block or challenge page stops that store for the run. Several blocked stores
  within 2 minutes halt the whole run.
- No proxies, no anti-bot bypass, no browser automation against shops, no
  personal data. Honest user agent:
  `ecommerce-price-monitor/0.1 (+https://siddharthkumar.com)`.
- Store prices, compare-at prices, availability and identifiers (ids, handle,
  product and variant title). **Never** images or product descriptions.
- Stores selling adult, tobacco/vape, alcohol, cannabis/CBD or weapons products
  are excluded (content screen in `src/pricemon/screen.py`).
- Terms of Service (D-031): recon reads `/policies/terms-of-service` once per store
  (at most 2 requests, only where robots.txt allows it) and records `terms`: `ban`,
  `no_ban` or `none_found`. Only `no_ban` and `none_found` stores are monitored
  (D-036): a `ban` store never enters `config/stores.yml`, and every run withdraws
  from public data any store that is neither listed nor retired. As a safety net, a
  store whose value is in `anonymise_terms` (`config/public.yml`, `[ban]`) would be
  shown as "Store #<n> (<category>)" through `pricemon.display`; never format a
  store name or host for a public file any other way.
- Retired stores: `config/retired.yml` (id, name, category, date). `sources.py`
  keeps them out of `config/stores.yml` and copies the list into it; the next run
  closes their open rows without change events; every surface says "retired on
  <date>".

### Run budget and schedule

- One daily run must finish in under 45 minutes on a single runner (D-020). Never
  split a run over several jobs or runners at the same time: that would spread
  requests over more IPs and work around Shopify's per-IP limit. Keep it inside the
  budget with the store list (`MAX_STORES` and `MIN_PER_CATEGORY` in `sources.py`;
  at least 100 stores since D-031). Never raise the request rate per shop or the
  run-wide pace to make a bigger list fit.
- The repository is public, so Actions minutes on standard runners are free; still
  request live checks only when they answer a question, because each one adds load
  on the stores (INC-005).
- One run a day at 06:17 UTC. The Black Friday extra runs (D-021, D-026) ended when
  the owner lifted the freeze on 27 Nov 2026 (D-031); the slots that were due before
  the lift stay in the accounting (`BFCM_2026_END` in `schedule.py`).
- On-time slots: GitHub starts scheduled runs 7 to 10 hours late (INC-009), so an
  external trigger dispatches `daily.yml` at each slot with the input `slot`
  (D-028, D-030; set-up in "On-time trigger" below). The `slot` gate
  (`python -m pricemon.schedule gate`) runs a dispatch only for the current,
  unfilled slot; the late schedule event then skips. `slot=check` tests the
  trigger without running anything.
- Missed slots: `watchdog.yml` (08:47 and 16:47 UTC) starts the daily run if the
  latest slot has no ok, partial or held run, and opens a `run-alert` issue. A
  scheduled run whose slot was already filled skips (INC-007, D-027). Accounting:
  on time = a good run within 2 h of the slot, late = later that day, missed = no
  run (`status.json` `schedule`). If
  `daily` shows no `schedule` runs for days, disable and re-enable it in the
  web UI (Actions, daily, the "..." menu); if that fails, rename the file.
- GitHub Pages: the `pages` job in `daily.yml` deploys `site/` when the repository
  variable `PAGES_ENABLED` is `true` (D-026).

### On-time trigger

The owner's own cron (D-030, corrected by D-035) calls the `workflow_dispatch` API
with a **fixed** body; `slot: auto` makes the gate pick the active slot
(`active_crons()`, 06:17 UTC only since D-031) within 10 minutes of now, before or after.
With no such slot the run skips with a one-line reason. Otherwise it is an explicit
slot: a dispatch up to 10 minutes early waits for the slot, at most one pipeline
run per slot, and the run records `dispatch.by` "trigger" (on-time accounting).

- URL: `https://api.github.com/repos/siddharthkumarx/ecommerce-price-monitor/actions/workflows/daily.yml/dispatches`
- Method: `POST`
- Headers: `Authorization: Bearer <token>`, `Accept: application/vnd.github+json`.
  The token is fine-grained, this repository only, Actions read and write, 90-day
  expiry; it lives only on the machine that runs the cron, never in the repository.
  Renew it before
  it expires.
- Body: `{"ref":"main","inputs":{"slot":"auto"}}`
- Schedule, time zone UTC: one line, `17 6 * * *` (every day). The Black Friday slots
  are gone since D-031: a call at 00:17, 12:17 or 18:17 now skips with a one-line
  reason, so replace any multi-slot line with the single 06:17 line.
- Success is HTTP 204. Test the token with the body
  `{"ref":"main","inputs":{"slot":"check"}}` (runs nothing). A call at any other
  time skips, so an extra or mistimed call is harmless.

### Dashboard look

SteadyData light system (D-029). Page `#FFFFFF`, alternate band `#F3F8F7`; cards
`#FFFFFF` with a `#E2EAE8` border and 14 px radius; headings `#0B1416`, body
`#3D4B49`, muted `#5F716E`; accent `#0B7468` (hover `#095E55`, soft `#E3F3F0`);
drops / good `#0E8A7D` and rises / look here `#D98E14`, used for marks only (bars,
dots), never for text, and always with a direct text label. Plus Jakarta Sans
(self-hosted Latin subset, tabular numbers) for all text, IBM Plex Mono for IDs;
`theme-color` `#FFFFFF`. No external scripts, text contrast at least 4.5:1, 360 to
1920 px, motion only where it explains (the daily bars grow in date order) and
reduced motion shows the final state. Check with `node scripts/screenshots.cjs site`
(360, 390, 768, 1280 and 1440 px).

### Canvas rule (owner decision, 22 Nov 2026)

Every image's outermost background is `#F3F8F7`: never pure white `#FFFFFF`, never
dark `#0B1416`, never transparent with dark text. Cards inside stay `#FFFFFF` with
border `#E2EAE8` and radius 14 px. A screenshot of a white page is shown framed: the
page as a card (radius 14, border `#E2EAE8`) on about 40 px of `#F3F8F7`.

- `scripts/render_media.cjs` draws the social preview on the canvas (text in a white
  card, chart on the canvas) and frames the dashboard shot (with reduced motion, so
  the charts show their final state). `scripts/screenshots.cjs` frames its shots
  (`--raw` for the bare page).
- `src/pricemon/site_assets/og.png` is the steadydata.co case-study picture, copied
  from `assets/img/og/case-studies-ecommerce-price-monitor.png` there (rendered by
  its `_dev/render_assets.js`, already on the canvas).
- Exceptions: the dashboard page itself (`#FFFFFF` with `#F3F8F7` bands), the
  favicon and app-icon tiles in `src/pricemon/site_assets/icons/`, and the Simple
  Icons logos drawn inside the README visuals.
- `node scripts/check_canvas.cjs` (run by `tests/test_canvas_rule.py`) checks every
  edge pixel of every tracked PNG and the first `<rect>` fill of every SVG, and fails
  on anything else outside the exceptions.

### README

`README.md` and `data/README.md` are **generated**: edit `templates/*.md.j2`,
never the rendered files (the daily run overwrites them). Rules: D-022 in
`docs/decisions.md`. Client sections in plain words; every number from a real run.

## Commands

```bash
uv sync                                   # install (Python 3.12, uv.lock)
uv run ruff check . && uv run ruff format --check .
uv run mypy
uv run pytest
uv run python -m pricemon.sources checks/results/recon-00*/recon.json > docs/sources.md
uv run python -m pricemon.sources --stores-yml checks/results/recon-00*/recon.json > config/stores.yml
uv run python -m pricemon.checks checks/request.yml   # what the checks workflow runs (runner only)
uv run python -m pricemon.run --out data             # the daily pipeline (runner only)
uv run python -m pricemon.site --data data --out site # build the dashboard (offline)
uv run python -m pricemon.visuals                     # README visuals from data/ (offline)
uv run python -m pricemon.readme                      # README.md + data/README.md from templates/
uv run python -m pricemon.feed                        # data/public/feed.json from runs.jsonl + status.json
scripts/make_media.sh                                # dashboard PNG, social preview, LinkedIn video
```

`UV_SYSTEM_CERTS=1` may be needed in the sandbox for uv to trust the proxy CA.

## Layout

```
src/pricemon/   polite.py (HTTP rules), witness.py (parsers), recon.py, screen.py,
                sources.py (register), checks.py (live checks runner), and the
                pipeline modules listed in docs/architecture.md
config/         stores.yml (generated from recon evidence), screen-review.yml
checks/         candidates.yml, request.yml, results/<id>/ (committed evidence)
data/           pipeline outputs committed by the daily workflow
site/           built dashboard
docs/           maintainers (this guide), sources, architecture, build-progress, decisions,
                incidents, publish-checklist, repo-settings
templates/      README.md.j2, DATASET_CARD.md.j2 (sources of the generated READMEs)
assets/         generated visuals, icons (Simple Icons, CC0), LICENSES.md
tests/          pytest with golden fixtures in tests/fixtures/
```

## Continue here

Open `docs/build-progress.md` and take the first item that is not `done`.
Its notes say what is already in place and how to verify it.
