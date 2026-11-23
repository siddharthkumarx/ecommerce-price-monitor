# Recon `recon-005`

- started: 2026-11-23T12:01:23+00:00, finished: 2026-11-23T12:07:35+00:00
- run: https://github.com/siddharthkumarx/ecommerce-price-monitor/actions/runs/45170358916
- candidates: 6, passed: 3 (variant cap 3000, retailers 25000)
- run-wide request interval: 3.0s + jitter; halted: no

| store | category | host | robots | products.json | .js | reachable | shopify | products | variants | in stock | .js check | JSON-LD cur | Shopify cur | meta country | reqs | result |
|---|---|---|---|---|---|---|---|---:|---:|---:|---|---|---|---|---:|---|
| Whole Latte Love | coffee_retail | www.wholelattelove.com | ok | yes | yes | yes | yes | 249 | 662 | 60% | match | USD | USD | US | 5 | PASS |
| Backcountry Essentials | outdoor_retail | backcountryessentials.net | ok | yes | yes | yes | yes | 1963 | 4103 | 82% | match | USD | USD | US | 12 | fail: excluded category: alcohol, tobacco/vape |
| Black Flag Outfitters | outdoor_retail | www.blackflagoutfitters.com | ok | yes | yes | yes | yes | - | - | - | match | USD | USD | US | 15 | fail: blocked mid-recon, empty catalog, needed 429 retries |
| Gearonimo Sports | outdoor_retail | gearonimosports.com | ok | yes | yes | yes | yes | 247 | 302 | 74% | match | USD | USD | US | 5 | PASS |
| How NOT 2 | outdoor_retail | hownot2.com | ok | yes | yes | yes | yes | 1508 | 7581 | 86% | match | USD | USD | US | 11 | PASS |
| Idaho Mountain Touring | outdoor_retail | www.idahomountaintouring.com | ok | yes | yes | yes | yes | - | - | - | match | USD | USD | US | 14 | fail: blocked mid-recon, empty catalog, needed 429 retries |

## Notes

- **Black Flag Outfitters**: stopped: retries exhausted: http 429
- **Idaho Mountain Touring**: stopped: retries exhausted: http 429
