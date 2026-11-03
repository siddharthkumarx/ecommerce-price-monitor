# Incidents

Each entry: what happened, evidence, cause, fix, and how a repeat is detected.

## INC-001 - Shared Shopify edge throttled the recon runner (2026-11-03)

- **Run:** `recon-001`, [Actions run 41723890450](https://github.com/siddharthkumarx/ecommerce-price-monitor-wip/actions/runs/41723890450),
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
