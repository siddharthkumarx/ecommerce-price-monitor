# Recon `recon-009`

- started: 2026-11-28T00:32:48+00:00, finished: 2026-11-28T00:35:25+00:00
- run: https://github.com/siddharthkumarx/ecommerce-price-monitor/actions/runs/46077814280
- candidates: 5, passed: 4 (variant cap 3000)
- run-wide request interval: 4.0s + jitter; halted: no

| store | category | host | robots | products.json | .js | reachable | shopify | products | variants | in stock | .js check | JSON-LD cur | Shopify cur | meta country | reqs | terms | result |
|---|---|---|---|---|---|---|---|---:|---:|---:|---|---|---|---|---:|---|---|
| Derma E | beauty | dermae.com | ok | yes | yes | yes | yes | 136 | 136 | 92% | match | USD | USD | US | 6 | no_ban | fail: excluded category: cannabis/cbd |
| Jeffree Star Cosmetics | beauty | jeffreestarcosmetics.com | ok | yes | yes | yes | yes | 283 | 1225 | 55% | match | - | USD | US | 7 | no_ban | PASS |
| Scotch Porter | beauty | www.scotchporter.com | ok | yes | yes | yes | yes | 45 | 57 | 93% | match | USD | USD | US | 5 | none_found | PASS |
| Klean Kanteen | home_kitchen | www.kleankanteen.com | ok | yes | yes | yes | yes | 146 | 1182 | 77% | match | USD | USD | US | 6 | no_ban | PASS |
| NEST New York | home_kitchen | www.nestnewyork.com | ok | yes | yes | yes | yes | 402 | 407 | 99% | match | USD | USD | US | 7 | no_ban | PASS |

## Notes

- **Jeffree Star Cosmetics**: no JSON-LD offer currency on product page

## Terms of Service

`/policies/terms-of-service`, at most 2 requests per store, read only where robots.txt allows it: ban 0, no_ban 4, none_found 1.

| store | terms | source | first matching sentence |
|---|---|---|---|
| Derma E | no_ban | read | - |
| Jeffree Star Cosmetics | no_ban | read | - |
| Scotch Porter | none_found | robots.txt disallows /policies/terms-of-service | - |
| Klean Kanteen | no_ban | read | - |
| NEST New York | no_ban | read | - |
