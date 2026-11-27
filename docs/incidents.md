# Incidents

Each entry: what happened, evidence, cause, fix, and how a repeat is detected.

## INC-001 - Shared Shopify edge throttled the recon runner (2026-11-03)

- **Run:** `recon-001`, [Actions run 41723890450](https://github.com/siddharthkumarx/ecommerce-price-monitor/actions/runs/41723890450),
  results in `checks/results/recon-001/`.
- **What happened:** the first ~35 stores answered normally. From then on almost every store
  returned a Cloudflare challenge (`window._cf_chl_opt`, HTTP 429) on its very first request
  (robots.txt, 0.1 s), including stores that had never been contacted before. 55 of 92
  candidates ended as "blocked".
- **Cause:** pacing was per store only (3 s + 0-2 s jitter) with 8 stores in parallel, so the run
  as a whole sent about 1.7 requests/s to Shopify's shared edge, which throttles per client IP
  across all shops. Per-store politeness does not bound the load on a shared edge.
- **Fix:** `EdgeGuard` in `src/pricemon/polite.py`: one run-wide request interval (default
  2 s + 0-1 s jitter, about 0.4 requests/s for the whole run) and a circuit breaker that halts the
  run when 4 different stores are blocked within 120 s. Halted stores are reported as
  "not checked (run halted)" instead of being contacted. A challenge served with 429/503 is
  treated as a block and never retried.
- **Also found in the same run:** product `.js` responses were discarded because Shopify serves
  them as `text/javascript`, not `application/json`. The test fake returned `application/json`,
  which hid the bug; the fake now uses the real content type.
- **Detection:** `halted_reason` is written to the recon/run metadata; blocked stores are listed
  with their reason.

## INC-002 - Retry causes were not recorded in early recon runs (2026-11-03)

- **Runs:** `recon-001` to `recon-003`.
- **What happened:** the owner's selection rule drops stores that needed 429
  retries, but those runs stored only the number of retries per store, not the HTTP
  status that caused each one. A 429 could not be told apart from a 502 or a reset.
- **Consequence:** every retry in those runs is treated as a 429 (D-004). Several
  stores that may only have seen a transient 5xx were dropped.
- **Fix:** `StoreSession.retry_causes` records the cause of every retry
  (`http 429`, `http 503`, `network error: ConnectError`); recon results and
  `runs.jsonl` carry it from `recon-004` on.
- **Detection:** `tests/test_recon.py::test_a_429_retry_fails_even_when_the_retry_succeeds`.

## INC-003 - First full dry run held, over the time budget (2026-11-04)

- **Run:** `pipeline-001`, [Actions run 41741247983](https://github.com/siddharthkumarx/ecommerce-price-monitor/actions/runs/41741247983),
  results in `checks/results/pipeline-001/`.
- **What happened:** status `held`, 22 of 30 stores complete, 31.5 minutes.
  - Validation rejects above 2 % held the run for 4 stores. All rejects were $0
    variants (free gifts, samples), not malformed data.
  - 5 stores were stopped by the content screen. 4 of them had reviewed false
    positives that were never applied: `load_stores` dropped `screen_reviewed`
    because a scripted edit missed after a reformat (no test loaded the real
    config). Koio was screened for the first time ("Monza Leather in Tobacco",
    a colour name).
  - 67 retries, all HTTP 429, spread over 26 stores; 2 stores (Skullcandy, Year &
    Day) exhausted their retries. Stores in backoff left the run-wide pace idle,
    so the run took 8.2 s per request instead of about 4.5 s.
  - Richer Poorer: one JSON-LD offer price differed from the catalog (store
    marked `mismatch`, not updated; the run did what it should).
- **Fixes:** $0 variants skipped and counted (D-018); `load_stores` reads
  `screen_reviewed`, with a regression test over the committed config; Koio's hit
  reviewed; 5 stores in flight at the same run-wide pace (D-005); every retry now
  records request kind and Retry-After (`retry_details`), and a JSON-LD mismatch
  records its first price difference, so the next runs show which requests
  Shopify throttles.
- **Process fix:** scripted edits now assert that each replacement matched.

## INC-004 - Per-store Retry-After let the edge escalate to challenges (2026-11-04)

- **Run:** `pipeline-002`, results in `checks/results/pipeline-002/`.
- **What happened:** status `partial`, 4 of 30 stores updated, 7.3 minutes. Every
  throttled request was HTTP 429 with `Retry-After: 60` (12 on product `.js`, 10 on
  `/products.json`, 3 on product pages, from the new `retry_details`). The store
  that got a 429 waited 60 s, but the other stores kept requesting. Within minutes
  Shopify served Cloudflare challenges with HTTP 429 to 6 stores, including on
  robots.txt, and the circuit breaker halted the run after 4 blocks in 120 s.
- **Cause:** a 429 from Shopify is a per-IP limit on the shared edge, not a
  per-store one. Honouring Retry-After only for the store that received it left
  the run's total rate unchanged.
- **Fix:** `EdgeGuard.throttled()`: any 429 pauses every store for its Retry-After
  and multiplies the run-wide interval by 1.5 (up to 12 s); `succeeded()` eases it
  back after 10 successes in a row. A 27-minute budget (`deadline`) stops new
  requests so a run always ends inside 30 minutes. The witness sample is 1 product
  per store (D-010), cutting a run from 187 to 127 requests. `runs.jsonl` records
  `edge.throttle_events`, `edge.cooldown_s` and `edge.final_interval_s`.
- **Kept:** the circuit breaker did exactly its job; no store was hit after the
  halt.

## INC-005 - Runner IP throttled from the first minute; per-shop spacing did not help (2026-11-04)

- **Runs:** `pipeline-003` (00:26 UTC) and `pipeline-004` (00:56 UTC), results in
  `checks/results/pipeline-00{3,4}/`.
- **pipeline-003** (daily defaults: 4 s + 0-3 s per shop, 3 s + 0-1.5 s run-wide,
  5 shops in flight, run-wide 429 cooldown): `partial`, 21 of 30 stores, 9,437
  variants, 27.9 minutes; 36 x 429 (`Retry-After: 60`) on `/products.json`, `.js`
  and product pages alike; no challenges, no blocks; the 27-minute budget stopped
  the last 7 stores.
- **pipeline-004** tested whether Shopify throttles per shop (20 s + 0-10 s
  between requests to the same shop, 8 in flight): **0 of 30 stores**. The new
  request log shows `robots.txt` answering 200 everywhere while `/products.json`
  returned 429 for almost every shop from the first ~30 s of the run, and kept
  doing so with ~100 s between attempts for 28 minutes.
- **Reading:** the throttle is per client IP, stateful over long windows, and
  was already active when the run began. Eight live runs from GitHub's Azure IP
  pool in under four hours (recon-001 to 004, pipeline-001 to 004) are the likely
  cause; GitHub-hosted runners do not keep a stable IP. Per-shop spacing is not
  the lever.
- **Fixes:** a run that sees 8 429s in a row with no success halts ("edge
  throttling persisted") instead of knocking until the budget runs out; that
  raises the run alert. Daily settings stay at the `pipeline-003` values.
- **Decision:** no further live test runs on 2026-11-04 night; the scheduled run at
  06:17 UTC, after a five-hour pause, is the next measurement (build-progress
  item 19). If scheduled runs keep losing stores to 429s, the options in order are:
  fewer requests per run (the `.js` witness for a rotating third of the stores),
  a lower run-wide rate with a longer budget (needs the owner's agreement on the
  30-minute rule), or a smaller store list.

## INC-006 - A data commit lost a rebase race with a human push (2026-11-04)

- **Run:** the scheduled `daily` run that GitHub started at 14:35 UTC (the 06:17
  slot, queued about eight hours late), Actions run 41849075647; alert issue #2.
- **What happened:** the pipeline succeeded and uploaded the month's Parquet
  history, but `Commit data` failed: while it ran, README and visual changes were
  pushed by hand, and its `git pull --rebase` stopped on conflicts in `README.md`,
  `assets/hero.svg` and `assets/maintenance-loop.svg`. The four retries could not
  continue a rebase in progress.
- **Consequence:** the release's month file held versions opened and closed by a
  run that `runs.jsonl` and the snapshot do not know. The next run started from
  the older snapshot, so its change log covers both days.
- **Fixes:** the commit step rebases with `-X theirs` (the run's own `data/`,
  README and visuals win; every run regenerates them) and aborts a failed rebase
  before retrying. `update_month_parquet` now reverts the traces of any run missing
  from the committed run log (drops versions it opened, re-opens versions it
  closed), so the month file agrees with the snapshot again on the next run.
  Regression test: `tests/test_history.py::test_a_run_whose_commit_failed_is_reverted_in_the_month_file`.
- **Process:** do not push rendered files (`README.md`, `assets/*.svg`) while a
  `daily` run is in progress.

## INC-007 - The daily schedule did not fire on `main` (2026-11-06)

- **Slot:** 06:17 UTC on 2026-11-06, the first daily slot after the publish on
  5 Nov (public, renamed, default branch renamed to `main`, history of `main`
  rewritten and force-pushed once).
- **What happened:** GitHub created no `schedule` run for `daily.yml`: no run, no
  queued run, no record in `data/runs.jsonl`. The owner's manual run
  ([Actions run 42197509596](https://github.com/siddharthkumarx/ecommerce-price-monitor/actions/runs/42197509596),
  `workflow_dispatch` at 09:46 UTC) filled the day: ok, 25 of 25 stores.
- **Evidence** (Actions API, read 2026-11-06 12:20 UTC):
  - In the repository's whole run history there is one `schedule` run, for any
    workflow: run 41849075647, created 2026-11-04 14:35:24 UTC on the old default
    branch. It was the 06:17 slot, 8 h 18 min late (INC-006).
  - 2026-11-05 06:17 slot: no run. The repository was still private and out of
    Actions minutes; it went public later that morning.
  - 2026-11-06 06:17 slot: no run, on `main`, public, workflow state `active`.
  - The workflow `daily` (id 406332445) was disabled and enabled through the API
    on 5 Nov 09:41 UTC (`updated_at` 2026-11-05T09:41:16Z). Commit `f462ccb`
    then changed `daily.yml` on `main` (pushed 11:15 UTC). The `schedule` block
    itself was last changed by `97f954e` on 3 Nov, before the rename and rewrite.
  - Manual runs and push-triggered workflows on `main` worked throughout.
- **Cause:** not provable from outside: GitHub shows no schedule registration
  state, and its documentation says scheduled runs can be delayed or dropped at
  times of high load. The two likely causes are a schedule registration that did
  not follow the default-branch rename and history rewrite, or a dropped slot. The
  4 Nov run suggests heavy delays for this repository even before the publish.
  Either way, the setup had no same-day guard: a missing slot was noticed only
  by a person.
- **Fixes:**
  - **Watchdog.** `.github/workflows/watchdog.yml` is a separate workflow with
    its own schedule, at 08:47 and 16:47 UTC. It checks whether a run of status
    ok, partial or held started at or after the latest daily slot
    (`python -m pricemon.schedule check`, standard library only). If none did and
    no daily run is queued or running, it starts `daily.yml` by hand, opens or
    updates a `run-alert` issue and fails. A failed run also triggers GitHub's
    failure email. A rescue at 08:47 lands within the 3-hour grace, so the
    "missed runs" badge counts the slot as run.
  - **Late slots skip.** The `slot` gate job in `daily.yml` now sees every
    trigger. A scheduled run whose slot is already filled (by a manual or
    watchdog run) skips the pipeline, so a slot that GitHub starts hours late
    does not fetch every store a second time.
  - **Re-arm.** The push of these changes is a fresh push to `main` that changes
    `daily.yml` and adds a second scheduled workflow. The owner disables and
    re-enables `daily` once more in the web UI after it (the API toggle of 5 Nov
    was not enough on its own).
- **How a repeat is detected:** the watchdog issue, titled "Scheduled daily run
  missed", on the same day. If it repeats on several days while the watchdog
  itself fires, `daily.yml`'s schedule is dead. The next step is then to move the
  daily workflow to a new file name, which GitHub registers as a new workflow.
  If the watchdog does not fire either, the repository's schedules are not
  firing at all. That is a GitHub support case, and runs are started by hand
  until then.
- **Regression tests:** `tests/test_schedule.py`.

## INC-008 - Moving a tag re-ran a live check (2026-11-05)

- **Run:** `checks`, [Actions run 42038565568](https://github.com/siddharthkumarx/ecommerce-price-monitor/actions/runs/42038565568),
  13:45 UTC. It was triggered by pushing the moved tag `data-2026-11`.
- **What happened:** `checks.yml` filtered on `paths: [checks/request.yml]` only.
  GitHub matched that filter for the tag push too, and the last
  request (`pipeline-004`) ran again against all 25 stores: 8 minutes, ok, no
  429s. Its results could not be committed (the push to the tag was rejected),
  so the run left nothing behind except the load on the stores.
- **Fix:** `checks.yml` runs on branch pushes only (`branches: ["**"]`); a test
  keeps tags out (`tests/test_workflows.py`).

## INC-009 - GitHub starts every scheduled slot 7 to 10 hours late (2026-11-20)

- **Runs:** every `schedule` run of `daily` and `watchdog` from 6 to 20 Nov 2026.
- **Evidence** (public Actions API, `workflows/<file>/runs`, read 2026-11-20):
  - `daily` (cron `17 6 * * *`): the `schedule` runs of 8 to 20 Nov were created
    between 13:29 and 16:27 UTC, 7 h 12 min to 10 h 10 min after the 06:17 slot;
    6 and 7 Nov were 8 h 04 min and 6 h 51 min late. Every day still got one good
    run (`data/runs.jsonl`), so no data was lost, but none started near 06:17.
  - `watchdog` (crons `47 8 * * *` and `47 16 * * *`): the 08:47 look ran between
    15:11 and 19:11 UTC, the 16:47 look between 20:30 and 00:30 UTC the next day.
    The watchdog found the late daily run already running or done, so it never had
    to start one.
  - `status.json` counted 16 "missed runs" and the README badge showed it: the old
    rule called a slot missed when no run started within 3 hours, so a run 8 hours
    late counted as missed although the day had its data.
- **Cause:** GitHub's scheduler delays `schedule` events under load and gives no
  guarantee on start time. Every cron of this repository drifts by the same hours,
  so in Black Friday week all four slots would start hours late.
- **Fixes:**
  - **On-time trigger.** An external scheduler calls `workflow_dispatch` on
    `daily.yml` at each slot with the input `slot` (for example
    `2026-11-26T06:17Z`), using a fine-grained token that holds only Actions read
    and write on this repository. The `slot` gate (`python -m pricemon.schedule
    gate`) lets such a dispatch run only for the current slot and only if no run
    has filled it; a dispatch up to 10 minutes early waits for the slot.
    `slot=check` proves the trigger and token work without running anything.
    Since D-030 the trigger sends the fixed input `slot: auto`; it is the owner's own
    cron (D-035).
  - **Late events skip.** GitHub's own schedule event arrives hours later, finds
    the slot filled and skips, so the stores are not read twice. The schedule and
    the watchdog stay as the fallback: if the dispatch does not come, the late
    schedule event (or the watchdog, which now passes the slot too) fills it.
  - **Honest accounting.** A slot is on time when a good run (ok or partial)
    started within 2 hours after it, late when the first good run started later
    the same UTC day (before the next slot), held when only held runs started in
    that window, missed when no run did. It is computed from `data/runs.jsonl`,
    which is not rewritten: the 17 slots from 4 to 20 Nov are 0 on time, 17 late,
    0 missed. `status.json` keeps these counts for every slot under `schedule`.
  - **What readers see.** The headline is delivery: "Daily runs delivered: 17 of
    17" (slots with a good run, late or not). The on-time count, its badge and any
    on-time percentage start at the first slot dispatched by the on-time trigger
    (`on_time_since`; run records carry `dispatch.slot` and `dispatch.by`, and the
    watchdog's dispatches do not count). Until then the badge reads "on time: from
    next run". One computed note covers the earlier slots: "Before <date>, GitHub
    started the scheduled run 7-10 h late; every day was still delivered (INC-009)."
- **Regression tests:** `tests/test_schedule.py` (gate and accounting, including
  the committed run log) and `tests/test_outputs.py`.

## INC-010 - Fast-forwarding main ran recon-007 a second time (2026-11-27)

- **Runs:** `checks` on `f1-expand`,
  [Actions run 46054716147](https://github.com/siddharthkumarx/ecommerce-price-monitor/actions/runs/46054716147)
  (19:09 UTC), and `checks` on `main`,
  [Actions run 46055231440](https://github.com/siddharthkumarx/ecommerce-price-monitor/actions/runs/46055231440)
  (19:14 UTC).
- **What happened:** the recon-007 request was pushed to `f1-expand`, and `main` was
  fast-forwarded to the same history five minutes later. The push to `main` also
  changed `checks/request.yml`, so `checks.yml` started recon-007 again on `main`
  (the concurrency group is per branch). For two hours both runs read the same 320
  candidates about five minutes apart, at the recon pace: each store saw its few
  recon requests twice. The `main` run was cancelled at 21:20 UTC. It had not
  written results (they are written only at the end), so nothing was committed.
- **Fix:** the checks job first skips a request whose `checks/results/<id>/` is
  already committed, or whose exact `checks/request.yml` an earlier `checks` run is
  already reading or waiting to read (requested, queued, pending, waiting or in
  progress). Every later step runs only when the guard says `skip=false`, so a
  failing guard runs nothing.
- **Regression test:** `tests/test_workflows.py`
  (`test_a_live_check_runs_once_even_when_main_is_fast_forwarded`).

## INC-011 - A daily run on a branch ended red at the Pages step (2026-11-27)

- **Run:** `daily` dispatched on `f1-expand` at 19:09 UTC (b9cb627): slot, both fetch
  shards and run succeeded; only `pages` failed in 2 s, because the `github-pages`
  environment deploys from `main` only. The run showed as failed and sent an email.
- **Fix:** the `pages` job also needs `github.ref == 'refs/heads/main'`, so a branch
  run skips it. Regression test: `tests/test_workflows.py`
  (`test_pages_deploy_runs_on_main_only`).
