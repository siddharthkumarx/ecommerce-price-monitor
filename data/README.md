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

- **Latest run:** 9 November 2026, 16:27 UTC, status `partial`, 22 of 25 stores updated.
- **Rows in the latest snapshot:** 11,810 product options.
- **Stores by category:** apparel 5, audio 6, beauty 4, home_kitchen 5, outdoor 5. The list and the evidence for every included and excluded store: [docs/sources.md](https://github.com/siddharthkumarx/ecommerce-price-monitor/blob/main/docs/sources.md).
- **Cadence:** one run a day at 06:17 UTC (4 a day from 26 Nov to 1 Dec 2026).

## Files

| File | Rows | Content |
|---|---|---|
| `latest/snapshot.csv` | one per product option | current price, compare-at price, stock, and since when |
| `changes/YYYY/YYYY-MM-DD.csv` | one per change | price up/down, sale start/end, sold out, back in stock, new, removed |
| `runs.jsonl` | one per run | run status, stores updated, quality counts, request counts |
| `price_history_YYYY-MM.parquet` (release asset) | one per version | full history, SCD2 with `valid_from` / `valid_to` |

Field definitions with real examples: the data dictionary in the [README](https://github.com/siddharthkumarx/ecommerce-price-monitor#data-dictionary).

## Collection

- Public catalog endpoints only (`/products.json`, `/products/<handle>.js`, product pages), requested with `country=US`.
- robots.txt respected (RFC 9309); one run-wide pace for Shopify's shared edge; any `429` pauses the whole run; a challenge page stops a store; no proxies, no anti-bot bypass.
- Honest user agent: `ecommerce-price-monitor/0.1 (+https://siddharthkumar.com)`.

## Quality checks (latest run)

- Second-source check: 25 of 25 sampled products matched the product `.js` feed exactly.
- Currency proof: 22 stores proved USD on a product page.
- Rows rejected by validation: 0; $0 variants (free gifts, samples) left out: 269; stale compare-at prices below the price ignored: 446.
- A run that fails the batch guard is held and not published; the previous good data stays live.

## Limitations

- Prices are list prices shown to a US visitor; cart-level promotions, codes and shipping are not included.
- A store that could not be read keeps its last good rows (see `stores_not_updated` in `runs.jsonl`).
- Some themes publish wrong JSON-LD prices; those differences are recorded, not used (decision D-019).

## Personal data and opt-out

No personal data. No images or product descriptions. Store owners can request removal at [hello@siddharthkumar.com](mailto:hello@siddharthkumar.com); removal within 24 hours.

## License and citation

Compilation of public facts shared under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/); store and product names belong to their owners. Code under MIT. Cite with [CITATION.cff](https://github.com/siddharthkumarx/ecommerce-price-monitor/blob/main/CITATION.cff).
