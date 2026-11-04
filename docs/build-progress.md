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
   generated: 30 stores, 14,357 variants, at least 5 per category.
   Regenerate: commands in `CLAUDE.md`.
5. **Docs for handover** - `done`.
   `CLAUDE.md`, `docs/architecture.md`, `docs/build-progress.md`,
   `docs/decisions.md` (D-001 to D-017), `docs/incidents.md` (INC-001, INC-002),
   `docs/readme-plan.md`.
6. **Store config loader** - `done`. `stores.py` (with `screen_reviewed` titles).
7. **Fetch with witnesses** - `done` offline, live check pending (item 19).
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
14. **Dashboard** - `in progress`. `site.py`, `site_assets/`. Remaining:
    Playwright screenshots at 360, 768 and 1440 px from the `pipeline-001` data
    (`scripts/screenshots.py`), Lighthouse-style checks, then build `site/` in
    `daily.yml`.
15. **Daily workflow** - `done`, first scheduled run pending (06:17 UTC).
    `.github/workflows/daily.yml`; `tests/test_outputs.py` keeps its crons equal to
    `schedule.CRONS`.
16. **CI hardening** - `done`. gitleaks 8.30.1 (pinned sha256), pip-audit on the
    lockfile, 50 MB file test (`tests/test_repo_hygiene.py`).
17. **Remove the 2026 Black Friday cron lines after 1 Dec 2026** - `todo` (D-013).
18. **README and animated SVGs** - `blocked` (waiting for the owner's README
    rules; notes in `docs/readme-plan.md`).
19. **Live pipeline dry run** - `in progress`. `pipeline-001` was held and took
    31.5 minutes (INC-003); fixes committed. `pipeline-002` requested: read
    `checks/results/pipeline-002/data/runs.jsonl`, confirm status `ok` or
    `partial`, duration under 30 minutes, the `retry_details`, and record the
    measured duration in D-005.
20. **GitHub Pages deploy** - `todo` after the public publish: add
    `actions/upload-pages-artifact` + `actions/deploy-pages` to `daily.yml`, gated
    on a repository variable `PAGES_ENABLED == 'true'`.
