# Recon `recon-003`

- started: 2026-11-03T22:15:55+00:00, finished: 2026-11-03T22:21:19+00:00
- run: https://github.com/siddharthkumarx/ecommerce-price-monitor-wip/actions/runs/41729230981
- candidates: 20, passed: 10 (variant cap 3000)
- run-wide request interval: 2.0s + jitter; halted: no

| store | category | host | robots | products.json | .js | reachable | shopify | products | variants | in stock | .js check | JSON-LD cur | Shopify cur | meta country | reqs | result |
|---|---|---|---|---|---|---|---|---:|---:|---:|---|---|---|---|---:|---|
| Ably Apparel | apparel | ablyapparel.com | ok | yes | yes | yes | yes | 250 | 3604+ | 87% | match | USD | USD | US | 6 | fail: catalog too large |
| Atoms | apparel | atoms.com | ok | yes | no | yes | no | - | - | - | - | - | - | - | 2 | fail: robots disallows |
| Birddogs | apparel | www.birddogs.com | ok | yes | yes | yes | no | - | - | - | - | - | - | - | 2 | fail: not shopify |
| Fair Harbor | apparel | www.fairharborclothing.com | ok | yes | yes | no | no | - | - | - | - | - | - | - | 2 | fail: blocked |
| Feat Clothing | apparel | featclothing.com | ok | yes | yes | yes | yes | 20 | 308 | 87% | match | USD | USD | US | 5 | PASS |
| Greats | apparel | www.greats.com | ok | yes | yes | yes | yes | 97 | 901 | 64% | match | USD | USD | US | 5 | PASS |
| Howler Brothers | apparel | howlerbros.com | ok | yes | yes | yes | yes | 750 | 4539+ | 80% | match | USD | USD | US | 7 | fail: catalog too large |
| Kirrin Finch | apparel | kirrinfinch.com | ok | yes | yes | yes | yes | 74 | 3169 | 48% | match | USD | USD | US | 7 | fail: catalog too large |
| Knickey | apparel | wearsubset.com | ok | yes | yes | yes | yes | 277 | 1544 | 42% | match | USD | USD | US | 7 | PASS |
| Koio | apparel | www.koio.co | ok | yes | yes | yes | yes | 122 | 875 | 77% | match | USD | USD | US | 5 | PASS |
| Kule | apparel | www.kule.com | ok | yes | yes | yes | yes | 0 | 0 | - | - | - | - | US | 3 | fail: empty catalog, currency not proven USD, product .js unavailable |
| Lunya | apparel | lunya.co | ok | yes | yes | yes | yes | 289 | 1379 | 77% | match | USD | USD | US | 6 | PASS |
| Mott & Bow | apparel | www.mottandbow.com | ok | yes | yes | yes | yes | 500 | 4427+ | 73% | match | USD | USD | US | 7 | fail: catalog too large |
| Olivers Apparel | apparel | oliversapparel.com | unreachable | - | - | no | no | - | - | - | - | - | - | - | 4 | fail: blocked |
| Paka | apparel | www.pakaapparel.com | ok | yes | yes | yes | yes | 107 | 2857 | 53% | match | USD | USD | US | 6 | PASS |
| Richer Poorer | apparel | www.richer-poorer.com | ok | yes | yes | yes | yes | 2 | 44 | 61% | match | USD | USD | US | 5 | PASS |
| State & Liberty | apparel | stateandliberty.com | ok | yes | yes | yes | yes | 249 | 1223 | 92% | match | USD | USD | US | 5 | PASS |
| Thousand Fell | apparel | www.thousandfell.com | ok | yes | yes | yes | yes | 139 | 1225 | 78% | match | USD | USD | US | 6 | PASS |
| Tracksmith | apparel | www.tracksmith.com | ok | yes | yes | yes | no | - | - | - | - | - | - | - | 2 | fail: not shopify |
| Wolf & Shepherd | apparel | wolfandshepherd.com | ok | yes | yes | yes | yes | 81 | 1602 | 62% | match | USD | USD | US | 7 | PASS |

## Notes

- **Atoms**: /products.json: http 404, text/html
- **Birddogs**: /products.json: http 200, text/html
- **Fair Harbor**: stopped: blocked: cloudflare challenge
- **Olivers Apparel**: stopped: robots.txt unreachable: retries exhausted: network error: ConnectError
- **Tracksmith**: /products.json: http 404, text/html
