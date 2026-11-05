# Build progress

Status: `done`, `in progress`, `todo`, `blocked`. Update after every item. Each
item says how to verify it.

1. **Scaffold, git hooks, CI** - `done`.
   uv project (`pyproject.toml`, `uv.lock`), `.githooks/commit-msg`,
   `scripts/check-commit-messages.sh`, `.github/workflows/ci.yml`.
   Verify: `uv run pytest tests/test_commit_hook.py`.
2. **Polite HTTP layer** - `done`.
   `src/pricemon/polite.py`: robots (Protego), per-store delay and jitter,
   retries on 429/5xx/network only, Retry-After, block detection, `EdgeGuard`
   run-wide pace and circuit breaker (INC-001), retry causes (INC-002).
   Verify: `uv run pytest tests/test_polite.py`.
3. **Live checks on Actions** - `done`.
   `src/pricemon/checks.py` (`recon`, `pipeline`), `.github/workflows/checks.yml`.
4. **Recon and site register** - `done`.
   `recon-001` to `recon-004` committed; owner drop rules (D-004) and reviewed
   screen hits (D-016) applied; `docs/sources.md` and `config/stores.yml`
   generated (since trimmed to 25 stores, item 21).
   Regenerate: commands in `docs/maintainers.md`.
5. **Docs for handover** - `done`.
   `docs/maintainers.md`, `docs/architecture.md`, `docs/build-progress.md`,
   `docs/decisions.md`, `docs/incidents.md`. (`docs/readme-plan.md` was folded
   into the generated README, item 18.)
6. **Store config loader** - `done`. `stores.py` (with `screen_reviewed` titles).
7. **Fetch with witnesses** - `done`, verified live in `pipeline-003` (21 stores, all witnesses matched or recorded).
   `fetch.py`; tests `tests/test_fetch.py` on fixtures in `tests/fixtures/shop/`.
8. **Models, validation, batch guard** - `done`.
   `models.py`, `normalize.py`, `guard.py`; `tests/test_models_normalize_guard.py`.
9. **Normalize and SCD2 history** - `done`.
   `history.py`; golden two-run scenario `tests/test_history.py` with
   `tests/fixtures/golden/` (`UPDATE_GOLDEN=1` to regenerate, then review).
10. **Change detection** - `done`. `changes.py`, covered by the golden scenario.
11. **Outputs** - `done`. `outputs.py`, `schedule.py`; `tests/test_outputs.py`.
    Parquet release upload is in `daily.yml` and is verified by the first
    scheduled run.
12. **Pipeline entry point** - `done`. `run.py` (exit codes 0/2/3/1), `alert.py`.
13. **Google Sheet publish** - `done`. `sheets.py`; skips without
    `GOOGLE_SA_JSON` / `GOOGLE_SHEET_ID` (not configured yet: the owner adds the
    secret and variable when wanted).
14. **Dashboard** - `done`. `site.py`, `site_assets/`; built from the
    `pipeline-003` data and checked with `node scripts/screenshots.cjs site` at
    360, 768 and 1440 px (no page scroll, no external requests, contrast >= 4.5:1,
    fonts loaded, reduced motion). `daily.yml` builds `site/` as an artifact.
15. **Daily workflow** - `done`, first scheduled run pending (06:17 UTC).
    `.github/workflows/daily.yml`; `tests/test_outputs.py` keeps its crons equal to
    `schedule.CRONS`.
16. **CI hardening** - `done`. gitleaks 8.30.1 (pinned sha256), pip-audit on the
    lockfile, 50 MB file test (`tests/test_repo_hygiene.py`).
17. **Remove the 2026 Black Friday cron lines after 1 Dec 2026** - `todo` (D-013,
    D-021): the BFCM lines name days, not a year, and would fire again in 2027.
18. **README, visuals and repo polish** - `done` (D-022 to D-024).
    `templates/README.md.j2`, `pricemon.readme`, `pricemon.visuals`,
    `scripts/make_media.sh`; dataset card, CITATION.cff, LICENSE, SECURITY.md,
    Dependabot, publish checklist, private explainer (`docs/private/`).
19. **Live pipeline dry runs** - `done`; follow-up open. `pipeline-001` held
    (INC-003); `pipeline-002` halted by the breaker (INC-004); `pipeline-003`
    partial, 21/30 stores in 27.9 min (daily settings); `pipeline-004` 0/30, IP
    throttled from the start (INC-005). **Next:** read the first scheduled run in
    `data/runs.jsonl` (06:17 UTC on 2026-11-04): stores updated,
    `edge.throttle_events`, duration. Then follow the options at the end of
    INC-005 if stores keep being lost to 429s. Do not start live checks just to
    retry: each adds load to the same throttle.
20. **GitHub Pages deploy** - `todo` after the public publish: add
    `actions/upload-pages-artifact` + `actions/deploy-pages` to `daily.yml`, gated
    on a repository variable `PAGES_ENABLED == 'true'`. Then run a Lighthouse
    audit on the live URL (target 100 in all four categories) and record it in
    `docs/decisions.md`. Already in place for it: no JavaScript, inline CSS,
    preloaded self-hosted fonts with `font-display: swap`, `lang`, meta
    description, inline favicon, focusable scroll regions, contrast >= 4.5:1.
21. **45-minute budget and 25-store list** - `done` (D-020). `sources.py` trims to
    25 stores (at least 4 per category); `docs/sources.md` and `config/stores.yml`
    regenerated; request budget 38 min, step 41, job 45.
22. **BFCM flag** - `done` (D-021). `env.BFCM_RUNS_PER_DAY` in `daily.yml`, "2"
    until the repo is public; set "4" only if public by 26 Nov 2026.
23. **First real daily run** - `in progress`. Neither the 06:17 UTC schedule nor
    the owner's manual run on 2026-11-04 had appeared in the Actions run list by
    08:40 UTC. Read the first run's `data/runs.jsonl` line when it lands.
24. **Public publish** - `done`, see item 25.
25. **Published in place** - `done` (2026-11-05). Public, renamed, `main`; history
    rewritten once (no `docs/private/`, no signatures); maintainers' guide at
    `docs/maintainers.md`. Remaining owner steps: `docs/publish-checklist.md`.
26. **INC-006 fixes** - `done`. Rebase with `-X theirs` in the data commit; the month
    Parquet file reverts runs whose commit did not land. The next good run repairs
    the 4 November file.
