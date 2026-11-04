# docs/maintainers.md

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
- `git config core.hooksPath .githooks`. The `commit-msg` hook strips
  `Co-Authored-By`, `Reviewed-by` and "Generated with" lines; the `ci` workflow
  job `commit-messages` fails if any commit still has one. Never add them.
- Never open a pull request. Work on the designated branch and push it.
- The working branch is the repository's default branch, so scheduled runs commit
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
2. Commit and push to the working branch. `.github/workflows/checks.yml` runs on
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

### Run budget and schedule

- One daily run must finish in under 45 minutes on a single runner (D-020). Never
  split a run over several jobs or runners: that would spread requests over more
  IPs and work around Shopify's per-IP limit. Keep it inside the budget with the
  store list (25 stores, at least 4 per category, `MAX_STORES` in `sources.py`).
- Actions minutes are a private budget (2,000 a month, shared with another repo)
  until the public publish: request live checks only when they answer a question.
- Black Friday / Cyber Monday (26 Nov to 1 Dec 2026): **one flag**,
  `env.BFCM_RUNS_PER_DAY` in `.github/workflows/daily.yml`. Set it to `"4"` only if
  the repository is public by 26 Nov; otherwise leave `"2"` (06:17 and 18:17 UTC).
  D-021.

### Dashboard look

Background `#0B1416`; panels `#0F1C1E` with border `#1D3331`; main text
`#EAF2F0`; body text `#C9D8D5`; quiet text `#7E9996`; teal `#2FBFAE` = good / in
stock; amber `#E9A93C` = look here / out of stock / price change. Instrument Sans
for headings and text, IBM Plex Mono for data and tables, both self-hosted. No
external scripts, text contrast at least 4.5:1, 360 to 1920 px, reduced motion
respected, aim for Lighthouse 100. GitHub Pages is switched on only after the
public publish; until then verify with Playwright screenshots at 360, 768 and
1440 px.

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
docs/           sources, architecture, build-progress, decisions, incidents, publish-checklist,
                repo-settings, private/ (call explainer, removed at publish)
templates/      README.md.j2, DATASET_CARD.md.j2 (sources of the generated READMEs)
assets/         generated visuals, icons (Simple Icons, CC0), LICENSES.md
tests/          pytest with golden fixtures in tests/fixtures/
```

## Continue here

Open `docs/build-progress.md` and take the first item that is not `done`.
Its notes say what is already in place and how to verify it.
