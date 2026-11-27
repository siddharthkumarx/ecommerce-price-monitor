# Build progress

## Continue here (f1-expand)

Status: **RUNNING** (27 Nov 2026). Task F1-EXPAND (owner decisions D-031 to D-037): grow the
daily monitor, freeze lifted, only stores whose terms do not ban robots (D-036). Work
happens on branch `f1-expand`; `main` is fast-forwarded when the gate is green and a run
has published.

1. JLab retired (`config/retired.yml`), history kept, shown "retired on 27 Nov 2026" - `done`.
2. Candidates: 1,218 in `checks/candidates.yml` (recon-005: 272, recon-006: 282,
   recon-007: 320, recon-008: 172 in the thin categories) - `done`.
3. Recon with the Terms field: recon-005 and recon-006 committed; recon-007 - `in progress`
   (running on Actions), recon-008 queued after it. Verify: `checks/results/recon-00N/recon.md`.
4. Store list: 71 stores (56 `no_ban`, 15 `none_found`) from recon-001..006, regenerated
   with `python -m pricemon.sources --stores-yml` - `done`. Next batch from recon-007 -
   `todo`: regenerate, gate, push.
5. Public data holds only listed and retired stores (`pricemon.publicdata`, D-036) - `done`;
   the first 71-store run withdrew 18 earlier stores from data and the release asset.
6. One run a day at 06:17 UTC, sequential shards planned per 60 stores (D-033) - `done`.
   First sharded run `20261127T184909Z`: 71 of 71 stores, 303 requests, 0 retries, no
   429, 19.5 min.
7. Feed contract (additive fields), README, dataset card, media, docs - `done`.
8. `main` fast-forwarded on 27 Nov 19:14 UTC - `done`. The dashboard on Pages deploys
   only from `main`: one run dispatched on `main` after recon-007 publishes it - `todo`.
9. Fresh review, High and Medium fixed (D-038) - `done`.
10. Grow toward about 150 stores (about 15 per category), never a `ban`: recon-008 on for
    the thin categories (apparel, toys & kids, tech accessories) - `todo`.

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
17. **Remove the 2026 Black Friday cron lines after 1 Dec 2026** - `done` early, on
    27 Nov 2026 (D-031): `daily.yml` has one cron line; the extra slots that were due
    are kept in `schedule.past_extra_slots` for the accounting, so nothing fires in 2027.
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
20. **GitHub Pages deploy** - `done` in the workflow (D-026): `pages` job in
    `daily.yml`, gated on the repository variable `PAGES_ENABLED`. Owner: set Pages
    source to "GitHub Actions" and `PAGES_ENABLED=true`, then run a Lighthouse audit
    on the live URL and record it in `docs/decisions.md`.
21. **45-minute budget and 25-store list** - `done` (D-020). `sources.py` trims to
    25 stores (at least 4 per category); `docs/sources.md` and `config/stores.yml`
    regenerated; request budget 38 min, step 41, job 45.
22. **BFCM flag** - `done` (D-021, D-026). `env.BFCM_RUNS_PER_DAY` is "4": the repo
    has been public since 5 Nov 2026.
23. **First real daily run** - `done`. First scheduled run 2026-11-04 (8 h late,
    INC-006); daily since then, see `data/runs.jsonl`.
24. **Public publish** - `done`, see item 25.
25. **Published in place** - `done` (2026-11-05). Public, renamed, `main`; history
    rewritten once (no `docs/private/`, no signatures); maintainers' guide at
    `docs/maintainers.md`. Remaining owner steps: `docs/publish-checklist.md`.
26. **INC-006 fixes** - `done`. Rebase with `-X theirs` in the data commit; the month
    Parquet file reverts runs whose commit did not land. The next good run repairs
    the 4 November file.
27. **Same-day watchdog** - `done` (INC-007, D-027). `.github/workflows/watchdog.yml`
    (08:47 and 16:47 UTC) starts a missed daily slot and raises a `run-alert` issue;
    the `slot` gate in `daily.yml` skips a scheduled run whose slot is filled.
    Verify: `uv run pytest tests/test_schedule.py`; on GitHub, the 2026-11-07 06:17
    UTC `schedule` run, or else the 08:47 watchdog rescue and its issue.
28. **Live checks never run on tag pushes** - `done` (INC-008).
29. **On-time dispatch and honest slot accounting** - `done` on branch `light-feed`
    (INC-009, D-028). `daily.yml` takes the `slot` input; `pricemon.schedule gate`
    decides every trigger; `status.json` has `schedule` counts and the README an
    "on time" badge. Verify: `uv run pytest tests/test_schedule.py`; on GitHub, a
    `daily, slot <time>` run started at the slot and the late `daily, schedule`
    run of the same day skipped ("already filled").
30. **Public feed** - `done` on branch `light-feed`. `src/pricemon/feed.py` writes
    `data/public/feed.json` (`steadydata.feed/v1`) atomically at the end of every ok or
    partial run; fields documented in the dataset card. Verify:
    `uv run pytest tests/test_feed.py`.
31. **SteadyData light look** - `done` on branch `light-feed` (D-029). Dashboard
    (`site.py`, `style.css`, Plus Jakarta Sans), README visuals, social preview,
    LinkedIn video and dashboard image re-rendered with `scripts/make_media.sh`.
    Verify: `node scripts/screenshots.cjs site` and `REQUIRE_PLAYWRIGHT=1 uv run pytest
    tests/test_visuals_render.py`.
32. **SteadyData contact and author line** - `done` on branch `light-feed`.
    `config/public.yml` (`email: hello@steadydata.co`, `contact`), README call to
    action, SECURITY.md, CITATION.cff, pyproject. Owner: confirm that
    hello@steadydata.co receives mail before the merge.
33. **On-time trigger with a fixed body (`slot: auto`)** - `done` (D-030).
    `pricemon.schedule.gate` resolves `auto` to the active slot within 10 minutes;
    `daily.yml` records the resolved slot. Trigger settings (the owner's own cron, D-035) in
    `docs/maintainers.md`, "On-time trigger". Verify: `uv run pytest
    tests/test_schedule.py`; on GitHub, a `daily, slot auto` run at 06:17 UTC that
    ran, and the late `daily, schedule` run of the same day skipped.
