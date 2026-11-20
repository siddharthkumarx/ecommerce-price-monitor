---
pretty_name: US Shopify store prices, daily
license: cc-by-4.0
language:
- en
tags:
- e-commerce
- prices
- retail
- shopify
- time-series
- web-scraping
size_categories:
- 10K<n<100K
task_categories:
- tabular-classification
- time-series-forecasting
configs:
- config_name: latest
  data_files: latest/snapshot.csv
- config_name: changes
  data_files: changes/*/*.csv
---

# US Shopify store prices, daily

Daily prices, sale ("compare-at") prices and stock for every product option of 25 US direct-to-consumer brands on Shopify, with a change log and a monthly price history. Collected by [siddharthkumarx/ecommerce-price-monitor](https://github.com/siddharthkumarx/ecommerce-price-monitor); this card is re-rendered after every run.

## Dataset summary

- **Latest run:** 20 November 2026, 15:30 UTC, status `ok`, 25 of 25 stores updated.
- **Rows in the latest snapshot:** 11,767 product options.
- **Stores by category:** apparel 5, audio 6, beauty 4, home_kitchen 5, outdoor 5. The list and the evidence for every included and excluded store: [docs/sources.md](https://github.com/siddharthkumarx/ecommerce-price-monitor/blob/main/docs/sources.md).
- **Cadence:** one run a day at 06:17 UTC (4 a day from 26 Nov to 1 Dec 2026).

## Files

| File | Rows | Content |
|---|---|---|
| `latest/snapshot.csv` | one per product option | current price, compare-at price, stock, and since when |
| `changes/YYYY/YYYY-MM-DD.csv` | one per change | price up/down, sale start/end, sold out, back in stock, new, removed |
| `runs.jsonl` | one per run | run status, stores updated, quality counts, request counts |
| `public/feed.json` | one summary | the public feed: latest good run, its checks, totals, daily change counts |
| `price_history_YYYY-MM.parquet` (release asset) | one per version | full history, SCD2 with `valid_from` / `valid_to` |

Field definitions with real examples: the data dictionary in the [README](https://github.com/siddharthkumarx/ecommerce-price-monitor#data-dictionary).

## Public feed

`public/feed.json` (schema `steadydata.feed/v1`) is a small summary for other sites to read: no product names, no prices. Every ok or partial run rewrites it atomically at its end; a held run never does, so the age of `generated_at` shows how stale the published data is. Fields are only ever added, never removed or renamed.

| Field | Meaning |
|---|---|
| `schema` | `steadydata.feed/v1` |
| `generated_at` | UTC time the feed was written |
| `monitor.id`, `title`, `repo`, `dashboard` | What this monitor is and where to see it |
| `monitor.first_run` | UTC start of the first good run |
| `monitor.stores_total`, `categories` | Stores monitored and their categories (`category_ids`: the ids in `config/stores.yml`) |
| `last_run.run_id`, `started_at`, `finished_at` | The latest good (ok or partial) run |
| `last_run.status` | `ok` (every store updated) or `partial` (some kept their last good prices) |
| `last_run.stores_ok`, `stores_total` | Stores updated in that run, of all stores |
| `last_run.rows_live` | Product options in the published snapshot after that run |
| `last_run.run_url` | The GitHub Actions run |
| `checks.rows_validated` | Catalog rows checked by row validation in that run (accepted plus rejected) |
| `checks.rows_rejected` | Rows that broke a validation rule and were set aside |
| `checks.held_back` | Rows read but not published because a check stopped them: stores whose `.js` re-read disagreed with `/products.json`, plus every row of a held run (so 0 or the mismatch stores' rows in a published feed) |
| `checks.second_source_checks` | Second-source re-reads of the daily sample product that were compared: one `.js` and one product-page JSON-LD re-read per store (a page without offers is not counted); split in `checks.second_source` |
| `checks.second_source_matches` | Those comparisons that agreed exactly |
| `checks.rows_compared_with_last_run`, `suspicious_price_moves`, `guard_holds` | The batch guard: rows matched with the last good data, prices that moved below 0.2x or above 5x, hold reasons raised |
| `totals.days_running` | Days from the first good run to today, inclusive |
| `totals.runs_total`, `runs_good`, `runs_held` | All runs, ok or partial runs, held runs |
| `schedule` | Due run slots so far: `on_time` (a good run started within `on_time_window_h` hours), `late` (later the same day), `held`, `missed` |
| `daily[]` | Up to 60 UTC dates, oldest first: `runs` (good runs that started that day), `rows_live` (after the day's last good run) and the change counts `price_down`, `price_up`, `discount_start`, `discount_end`, `out_of_stock`, `back_in_stock`, `new`, `removed`, summed over the day's runs. The first run is the baseline (every row `new`) and is left out |

## Collection

- Public catalog endpoints only (`/products.json`, `/products/<handle>.js`, product pages), requested with `country=US`.
- robots.txt respected (RFC 9309); one run-wide pace for Shopify's shared edge; any `429` pauses the whole run; a challenge page stops a store; no proxies, no anti-bot bypass.
- Honest user agent: `ecommerce-price-monitor/0.1 (+https://siddharthkumar.com)`.

## Quality checks (latest run)

- Second-source check: 25 of 25 sampled products matched the product `.js` feed exactly.
- Currency proof: 25 stores proved USD on a product page.
- Rows rejected by validation: 0; $0 variants (free gifts, samples) left out: 270; stale compare-at prices below the price ignored: 551.
- A run that fails the batch guard is held and not published; the previous good data stays live.

## Limitations

- Prices are list prices shown to a US visitor; cart-level promotions, codes and shipping are not included.
- A store that could not be read keeps its last good rows (see `stores_not_updated` in `runs.jsonl`).
- Some themes publish wrong JSON-LD prices; those differences are recorded, not used (decision D-019).

## Personal data and opt-out

No personal data. No images or product descriptions. Store owners can request removal at [hello@siddharthkumar.com](mailto:hello@siddharthkumar.com); removal within 24 hours.

## License and citation

Compilation of public facts shared under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/); store and product names belong to their owners. Code under MIT. Cite with [CITATION.cff](https://github.com/siddharthkumarx/ecommerce-price-monitor/blob/main/CITATION.cff).
