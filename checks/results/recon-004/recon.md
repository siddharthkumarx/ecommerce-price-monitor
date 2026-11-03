# Recon `recon-004`

- started: 2026-11-03T23:02:34+00:00, finished: 2026-11-03T23:38:23+00:00
- run: https://github.com/siddharthkumarx/ecommerce-price-monitor-wip/actions/runs/41735886504
- candidates: 60, passed: 14 (variant cap 3000)
- run-wide request interval: 4.0s + jitter; halted: no

| store | category | host | robots | products.json | .js | reachable | shopify | products | variants | in stock | .js check | JSON-LD cur | Shopify cur | meta country | reqs | result |
|---|---|---|---|---|---|---|---|---:|---:|---:|---|---|---|---|---:|---|
| Act+Acre | beauty | actandacre.com | ok | yes | yes | yes | yes | 50 | 54 | 98% | missing | - | - | US | 6 | fail: currency not proven USD, product .js unavailable, needed 429 retries |
| Billie | beauty | mybillie.com | missing-4xx | yes | yes | no | no | - | - | - | - | - | - | - | 2 | fail: blocked |
| Bubble | beauty | hellobubble.com | ok | yes | yes | no | no | - | - | - | - | - | - | - | 2 | fail: blocked |
| Ceremonia | beauty | ceremonia.com | ok | yes | yes | yes | yes | 66 | 74 | 90% | match | USD | USD | US | 6 | fail: needed 429 retries |
| Crown Affair | beauty | www.crownaffair.com | ok | yes | yes | yes | yes | 73 | 116 | 89% | match | USD | USD | US | 5 | PASS |
| Hero Cosmetics | beauty | www.herocosmetics.us | ok | yes | yes | yes | yes | 47 | 49 | 96% | match | USD | USD | US | 6 | fail: needed 429 retries |
| Jones Road | beauty | www.jonesroadbeauty.com | ok | yes | yes | yes | yes | 96 | 446 | 94% | match | USD | USD | US | 5 | PASS |
| Kinship | beauty | lovekinship.com | ok | yes | yes | yes | yes | 26 | 33 | 55% | match | USD | USD | US | 6 | fail: needed 429 retries |
| Nécessaire | beauty | necessaire.com | ok | yes | yes | yes | yes | 125 | 138 | 94% | match | USD | USD | US | 5 | PASS |
| Peach & Lily | beauty | www.peachandlily.com | ok | yes | yes | yes | yes | 142 | 177 | 91% | match | USD | USD | US | 6 | fail: excluded category: alcohol, needed 429 retries |
| Saie | beauty | saiehello.com | ok | yes | yes | yes | yes | 68 | 244 | 82% | match | USD | USD | US | 7 | fail: needed 429 retries |
| Soft Services | beauty | buysoftservices.com | unreachable | - | - | no | no | - | - | - | - | - | - | - | 4 | fail: blocked |
| Sol de Janeiro | beauty | soldejaneiro.com | ok | yes | yes | yes | yes | 150 | 714 | 99% | match | USD | USD | US | 5 | fail: excluded category: alcohol |
| Starface | beauty | starface.world | ok | yes | yes | yes | yes | 51 | 56 | 98% | match | USD | USD | US | 6 | fail: needed 429 retries |
| Topicals | beauty | mytopicals.com | ok | yes | yes | yes | no | - | - | - | - | - | - | - | 2 | fail: not shopify |
| Touchland | beauty | touchland.com | ok | yes | yes | yes | yes | 103 | 108 | 100% | match | USD | USD | US | 7 | fail: needed 429 retries |
| Vacation | beauty | vacation.inc | ok | yes | yes | no | no | - | - | - | - | - | - | - | 2 | fail: blocked |
| Versed | beauty | versedskin.com | ok | yes | yes | yes | yes | 74 | 959 | 77% | match | USD | USD | US | 8 | fail: needed 429 retries |
| Volition Beauty | beauty | volitionbeauty.com | ok | no | no | no | no | - | - | - | - | - | - | - | 1 | fail: robots disallows |
| Westman Atelier | beauty | www.westman-atelier.com | ok | yes | yes | yes | yes | 245 | 345 | 76% | match | USD | USD | US | 5 | fail: excluded category: alcohol |
| Bee's Wrap | home_kitchen | www.beeswrap.com | ok | yes | yes | yes | yes | 29 | 80 | 94% | match | USD | USD | US | 5 | PASS |
| Boy Smells | home_kitchen | boysmells.com | ok | yes | yes | yes | yes | 126 | 130 | 81% | match | USD | USD | US | 7 | fail: needed 429 retries |
| Branch Basics | home_kitchen | branchbasics.com | ok | yes | yes | yes | yes | 103 | 143 | 45% | match | USD | USD | US | 5 | PASS |
| Brooklyn Candle Studio | home_kitchen | brooklyncandlestudio.com | ok | yes | yes | yes | yes | 193 | 214 | 92% | match | USD | USD | US | 6 | fail: needed 429 retries |
| Coyuchi | home_kitchen | www.coyuchi.com | ok | yes | yes | yes | yes | 750 | 3885+ | 89% | match | USD | USD | US | 8 | fail: catalog too large, excluded category: alcohol, needed 429 retries |
| Cozy Earth | home_kitchen | cozyearth.com | ok | yes | yes | yes | yes | 250 | 5498+ | 78% | match | USD | USD | US | 6 | fail: catalog too large, needed 429 retries |
| East Fork | home_kitchen | eastfork.com | ok | yes | yes | yes | yes | 529 | 1798 | 85% | match | USD | USD | US | 8 | fail: excluded category: alcohol, needed 429 retries |
| Equal Parts | home_kitchen | equalparts.com | missing-4xx | yes | yes | yes | no | - | - | - | - | - | - | - | 2 | fail: not shopify |
| Estelle Colored Glass | home_kitchen | estellecoloredglass.com | ok | yes | yes | yes | yes | 442 | 506 | 97% | match | USD | USD | US | 7 | fail: excluded category: alcohol, needed 429 retries |
| Floyd | home_kitchen | floydhome.com | ok | yes | yes | yes | yes | 164 | 2525 | 96% | match | - | USD | US | 6 | fail: needed 429 retries |
| Heath Ceramics | home_kitchen | www.heathceramics.com | ok | yes | yes | yes | yes | 249 | 271 | 68% | match | - | USD | US | 6 | fail: needed 429 retries |
| Hedley & Bennett | home_kitchen | www.hedleyandbennett.com | ok | yes | yes | yes | no | - | - | - | - | - | - | - | 2 | fail: not shopify |
| Homesick | home_kitchen | homesick.com | ok | yes | yes | yes | yes | 252 | 255 | 96% | match | USD | USD | US | 6 | PASS |
| Otherland | home_kitchen | www.otherland.com | ok | yes | yes | yes | yes | 54 | 54 | 96% | match | - | USD | US | 5 | PASS |
| Sheets & Giggles | home_kitchen | sheetsgiggles.com | ok | yes | yes | yes | yes | 2 | 25 | 76% | match | USD | USD | US | 5 | PASS |
| Snowe | home_kitchen | snowehome.com | ok | yes | yes | yes | yes | 70 | 339 | 73% | match | - | USD | US | 6 | fail: needed 429 retries |
| Stasher | home_kitchen | www.stasherbag.com | ok | yes | yes | yes | yes | 97 | 140 | 66% | match | USD | USD | US | 9 | fail: needed 429 retries |
| W&P | home_kitchen | wpdesign.com | missing-4xx | yes | yes | yes | no | - | - | - | - | - | - | - | 2 | fail: not shopify |
| Xtrema | home_kitchen | xtrema.com | ok | yes | yes | yes | yes | 50 | 180 | 86% | match | USD | USD | US | 6 | fail: needed 429 retries |
| Year & Day | home_kitchen | yearandday.com | ok | yes | yes | yes | yes | 116 | 511 | 95% | match | USD | USD | US | 5 | PASS |
| Big Agnes | outdoor | www.bigagnes.com | ok | yes | yes | yes | yes | 282 | 724 | 95% | match | USD | USD | US | 6 | PASS |
| Chums | outdoor | chums.com | ok | yes | yes | yes | yes | 103 | 709 | 96% | match | USD | USD | US | 7 | fail: needed 429 retries |
| Coalatree | outdoor | coalatree.com | ok | yes | yes | yes | yes | 78 | 728 | 84% | match | USD | USD | US | 7 | fail: needed 429 retries |
| Enlightened Equipment | outdoor | enlightenedequipment.com | ok | yes | yes | yes | no | - | - | - | - | - | - | - | 2 | fail: not shopify |
| ENO | outdoor | eaglesnestoutfitters.com | ok | yes | yes | yes | no | - | - | - | - | - | - | - | 4 | fail: not shopify |
| Goal Zero | outdoor | goalzero.com | ok | yes | yes | yes | yes | 394 | 413 | 33% | match | USD | USD | US | 6 | fail: excluded category: tobacco/vape |
| Gossamer Gear | outdoor | www.gossamergear.com | ok | yes | yes | yes | yes | 125 | 233 | 93% | match | USD | USD | US | 5 | PASS |
| HydraPak | outdoor | www.hydrapak.com | ok | yes | yes | yes | yes | 176 | 494 | 85% | match | USD | USD | US | 5 | PASS |
| Hyperlite Mountain Gear | outdoor | hyperlitemountaingear.com | ok | yes | yes | yes | yes | 118 | 437 | 90% | match | USD | USD | US | 5 | PASS |
| Miir | outdoor | www.miir.com | ok | yes | yes | yes | yes | 168 | 1051 | 86% | match | USD | USD | US | 7 | fail: excluded category: alcohol, needed 429 retries |
| Mountainsmith | outdoor | mountainsmith.com | ok | yes | yes | yes | yes | - | - | - | - | - | - | - | 8 | fail: blocked mid-recon, empty catalog, currency not proven USD, product .js unavailable, needed 429 retries |
| Mystery Ranch | outdoor | www.mysteryranch.com | ok | yes | yes | yes | no | - | - | - | - | - | - | - | 2 | fail: not shopify |
| Oveja Negra | outdoor | www.ovejanegrabikepacking.com | ok | yes | yes | yes | yes | 214 | 1079 | 59% | match | - | USD | US | 5 | PASS |
| Poler | outdoor | polerstuff.com | ok | yes | yes | yes | no | - | - | - | - | - | - | - | 2 | fail: not shopify |
| Sawyer | outdoor | www.sawyer.com | ok | yes | yes | yes | no | - | - | - | - | - | - | - | 2 | fail: not shopify |
| Sea to Summit | outdoor | seatosummit.com | ok | yes | yes | yes | yes | 438 | 1677 | 55% | match | USD | USD | US | 8 | fail: needed 429 retries |
| Showers Pass | outdoor | showerspass.com | ok | yes | yes | yes | yes | 50 | 748 | 64% | match | USD | USD | US | 9 | fail: needed 429 retries |
| Six Moon Designs | outdoor | www.sixmoondesigns.com | ok | yes | yes | yes | yes | 121 | 633 | 78% | match | USD | USD | US | 5 | fail: excluded category: alcohol |
| ULA Equipment | outdoor | www.ula-equipment.com | ok | yes | yes | yes | no | - | - | - | - | - | - | - | 2 | fail: not shopify |
| Zpacks | outdoor | zpacks.com | ok | yes | yes | yes | yes | 500 | 4954+ | 89% | match | - | USD | US | 10 | fail: catalog too large, needed 429 retries |

## Notes

- **Act+Acre**: product .js: http 404; product page: http 404
- **Billie**: stopped: blocked: http 403
- **Bubble**: stopped: blocked: cloudflare block
- **Enlightened Equipment**: /products.json: http 404, text/html; charset=UTF-8
- **ENO**: /products.json: http 200, text/html; charset=utf-8
- **Equal Parts**: /products.json: http 404, text/html
- **Floyd**: no JSON-LD offer currency on product page
- **Heath Ceramics**: no JSON-LD offer currency on product page
- **Hedley & Bennett**: /products.json: http 200, text/html
- **Mountainsmith**: stopped: retries exhausted: http 429
- **Mystery Ranch**: /products.json: http 404, text/html;charset=utf-8
- **Otherland**: no JSON-LD offer currency on product page
- **Oveja Negra**: no JSON-LD offer currency on product page
- **Poler**: /products.json: http 404, text/html
- **Sawyer**: /products.json: http 404, text/html; charset=utf-8
- **Snowe**: no JSON-LD offer currency on product page
- **Soft Services**: stopped: robots.txt unreachable: retries exhausted: network error: ConnectError
- **Topicals**: /products.json: http 404, text/html
- **ULA Equipment**: /products.json: http 404, text/html; charset=UTF-8
- **Vacation**: stopped: blocked: cloudflare challenge
- **W&P**: /products.json: http 404, text/html; charset=iso-8859-1
- **Zpacks**: no JSON-LD offer currency on product page
