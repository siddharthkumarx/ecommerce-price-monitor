# Recon `recon-101`

- started: 2026-11-23T13:37:27+00:00, finished: 2026-11-23T14:15:08+00:00
- run: https://github.com/siddharthkumarx/ecommerce-price-monitor/actions/runs/45185737724
- candidates: 96, passed: 69 (variant cap 5000)
- run-wide request interval: 3.5s + jitter; halted: no

| store | category | host | robots | products.json | .js | reachable | shopify | products | variants | in stock | .js check | JSON-LD cur | Shopify cur | meta country | reqs | result |
|---|---|---|---|---|---|---|---|---:|---:|---:|---|---|---|---|---:|---|
| Aventon | bikes | www.aventon.com | ok | yes | yes | yes | yes | 249 | 939 | 92% | match | USD | USD | US | 5 | PASS |
| Brooks England | bikes | www.brooksengland.com | ok | yes | yes | yes | yes | 238 | 290 | 86% | match | USD | USD | IT | 5 | PASS |
| Chris King | bikes | chrisking.com | ok | yes | yes | yes | yes | 303 | 4367 | 98% | match | - | USD | US | 6 | fail: excluded category: alcohol |
| Crankbrothers | bikes | www.crankbrothers.com | ok | yes | yes | yes | yes | 268 | 1557 | 61% | match | USD | USD | US | 6 | fail: excluded category: tobacco/vape |
| Dakine | bikes | www.dakine.com | ok | yes | yes | yes | yes | 1367 | 3197 | 70% | match | USD | USD | US | 10 | PASS |
| EVOC | bikes | evocsports.com | ok | yes | yes | yes | yes | 347 | 913 | 75% | match | EUR | EUR | DE | 6 | fail: currency not proven USD, excluded category: weapons |
| Fairdale Bikes | bikes | fairdalebikes.com | ok | yes | yes | yes | no | - | - | - | - | - | - | - | 2 | fail: not shopify |
| Finish Line | bikes | finishlineusa.com | ok | yes | yes | yes | yes | 51 | 94 | 81% | match | - | USD | US | 5 | PASS |
| Juiced Bikes | bikes | juicedbikes.com | ok | yes | yes | yes | yes | 14 | 34 | 91% | match | USD | USD | US | 5 | PASS |
| Lectric eBikes | bikes | lectricebikes.com | ok | yes | yes | yes | yes | 428 | 596 | 99% | match | USD | USD | US | 6 | PASS |
| Orange Seal | bikes | orangeseal.com | ok | yes | yes | yes | yes | 9 | 42 | 93% | match | USD | USD | US | 5 | PASS |
| Paul Components | bikes | www.paulcomp.com | ok | yes | yes | yes | yes | 129 | 1636 | 100% | match | USD | - | - | 5 | PASS |
| Rene Herse Cycles | bikes | www.renehersecycles.com | ok | yes | yes | yes | yes | 563 | 1126 | 90% | missing | USD | - | - | 5 | fail: product .js unavailable |
| Ride1Up | bikes | ride1up.com | ok | yes | yes | yes | yes | 102 | 709 | 88% | match | - | - | - | 5 | PASS |
| Rockgeist | bikes | rockgeist.com | ok | yes | yes | yes | yes | 135 | 658 | 87% | match | - | - | - | 5 | PASS |
| Stan's NoTubes | bikes | stans.com | ok | yes | yes | yes | yes | 393 | 1049 | 58% | match | USD | USD | US | 6 | PASS |
| Art of Tea | coffee_tea | www.artoftea.com | ok | yes | yes | yes | yes | 192 | 443 | 93% | match | USD | USD | US | 5 | PASS |
| Atlas Coffee Club | coffee_tea | atlascoffeeclub.com | ok | yes | yes | yes | yes | 262 | 2413 | 99% | match | - | USD | US | 6 | PASS |
| Bird Rock Coffee | coffee_tea | www.birdrockcoffee.com | ok | yes | yes | yes | yes | 97 | 918 | 82% | match | USD | USD | US | 5 | fail: excluded category: alcohol |
| Bones Coffee | coffee_tea | www.bonescoffee.com | ok | yes | yes | yes | yes | 234 | 460 | 88% | match | USD | USD | US | 5 | fail: excluded category: alcohol |
| Chameleon Coffee | coffee_tea | chameleoncoffee.com | ok | yes | yes | yes | yes | 21 | 21 | 52% | match | USD | USD | US | 5 | PASS |
| Clevr Blends | coffee_tea | clevrblends.com | ok | yes | yes | yes | yes | 35 | 47 | 100% | match | USD | USD | US | 5 | PASS |
| Cometeer | coffee_tea | cometeer.com | ok | yes | yes | yes | yes | 249 | 276 | 63% | match | USD | USD | US | 5 | fail: excluded category: alcohol |
| Counter Culture Coffee | coffee_tea | counterculturecoffee.com | ok | yes | yes | yes | yes | 182 | 298 | 55% | match | USD | USD | US | 5 | fail: excluded category: alcohol |
| Death Wish Coffee | coffee_tea | www.deathwishcoffee.com | ok | yes | yes | yes | yes | 155 | 426 | 88% | match | USD | USD | US | 5 | fail: excluded category: alcohol |
| Driftaway Coffee | coffee_tea | driftaway.coffee | ok | yes | yes | yes | no | - | - | - | - | - | - | - | 2 | fail: not shopify |
| Eight Ounce Coffee | coffee_tea | eightouncecoffee.com | ok | yes | yes | yes | yes | 123 | 123 | 74% | match | USD | USD | CA | 5 | fail: excluded category: alcohol |
| Encha | coffee_tea | encha.com | ok | yes | yes | yes | yes | 5 | 14 | 71% | match | USD | USD | US | 5 | PASS |
| Four Sigmatic | coffee_tea | us.foursigmatic.com | ok | yes | yes | yes | yes | 90 | 287 | 94% | match | USD | USD | US | 5 | PASS |
| George Howell Coffee | coffee_tea | georgehowellcoffee.com | ok | yes | yes | yes | yes | 111 | 311 | 83% | match | - | USD | US | 5 | PASS |
| Grounds & Hounds Coffee | coffee_tea | groundsandhoundscoffee.com | ok | yes | yes | yes | yes | 248 | 403 | 81% | match | USD | USD | US | 5 | fail: excluded category: alcohol |
| Trade Coffee | coffee_tea | www.drinktrade.com | ok | yes | yes | yes | yes | 636 | 1276 | 100% | match | USD | USD | US | 7 | PASS |
| American Barbell | fitness | americanbarbell.com | ok | yes | yes | yes | yes | 156 | 425 | 73% | match | USD | USD | US | 5 | PASS |
| Amphipod | fitness | amphipod.com | ok | yes | yes | yes | yes | 86 | 86 | - | match | USD | - | - | 4 | PASS |
| Balega | fitness | balega.com | ok | yes | yes | yes | yes | 46 | 557 | 92% | match | USD | USD | US | 5 | PASS |
| Bandit Running | fitness | banditrunning.com | ok | yes | yes | yes | yes | 486 | 2804 | 60% | match | USD | USD | US | 6 | PASS |
| Bells of Steel | fitness | bellsofsteel.us | ok | yes | yes | yes | yes | 476 | 1516 | 85% | match | USD | USD | US | 6 | PASS |
| BOCO Gear | fitness | bocogear.com | ok | yes | yes | yes | yes | 144 | 147 | 100% | match | USD | - | - | 5 | PASS |
| BowFlex | fitness | www.bowflex.com | ok | yes | yes | yes | yes | 59 | 67 | 67% | match | USD | USD | US | 5 | PASS |
| Ciele Athletics | fitness | cieleathletics.com | ok | yes | yes | yes | yes | 588 | 1989 | 89% | match | USD | USD | CA | 7 | PASS |
| Crossrope | fitness | www.crossrope.com | ok | yes | yes | yes | yes | 208 | 823 | 61% | match | USD | USD | US | 5 | PASS |
| Echelon | fitness | echelonfit.com | ok | yes | yes | yes | yes | 482 | 2641 | 94% | match | USD | USD | US | 6 | PASS |
| Elite Jump Ropes | fitness | elitejumps.co | ok | yes | yes | yes | yes | 109 | 838 | 84% | match | - | USD | US | 5 | PASS |
| Ergatta | fitness | ergatta.com | ok | yes | yes | yes | yes | 66 | 189 | 87% | match | USD | USD | US | 5 | PASS |
| FlipBelt | fitness | flipbelt.com | ok | yes | yes | yes | yes | 104 | 1734 | 72% | match | USD | USD | US | 5 | PASS |
| Gaiam | fitness | www.gaiam.com | ok | yes | yes | yes | yes | 143 | 263 | 66% | match | USD | USD | US | 5 | PASS |
| Gornation | fitness | www.gornation.com | ok | yes | yes | yes | yes | 125 | 642 | 89% | match | USD | USD | DE | 5 | PASS |
| Ultimate Direction | fitness | ultimatedirection.com | ok | yes | yes | yes | no | 106 | 106 | - | missing | - | - | - | 4 | fail: not bigcommerce |
| 2 Hounds Design | pets | 2houndsdesign.com | ok | yes | yes | yes | yes | 500 | 6511+ | 100% | match | USD | USD | US | 6 | fail: catalog too large |
| Big Barker | pets | bigbarker.com | ok | yes | yes | yes | yes | 27 | 305 | 67% | match | USD | USD | US | 5 | PASS |
| Bixbi | pets | bixbipet.com | ok | yes | yes | yes | yes | 82 | 271 | 94% | match | - | - | - | 5 | PASS |
| Bocce's Bakery | pets | www.boccesbakery.com | ok | yes | yes | yes | yes | 146 | 148 | 99% | match | USD | USD | US | 5 | PASS |
| Earth Rated | pets | www.earthrated.com | ok | yes | yes | yes | yes | 16 | 46 | 100% | match | USD | USD | US | 5 | PASS |
| Fable Pets | pets | fablepets.com | ok | yes | yes | yes | yes | 67 | 397 | 79% | match | USD | USD | US | 5 | PASS |
| Found My Animal | pets | www.foundmyanimal.com | ok | yes | yes | yes | yes | 959 | 4314 | 83% | match | USD | USD | US | 8 | PASS |
| FurHaven | pets | furhaven.com | ok | yes | yes | yes | no | - | - | - | - | - | - | - | 2 | fail: not shopify |
| Fussie Cat | pets | fussiecat.com | ok | yes | yes | yes | yes | 99 | 101 | 96% | match | - | - | - | 5 | PASS |
| Grandma Lucy's | pets | www.grandmalucys.com | ok | yes | yes | yes | yes | 79 | 109 | 97% | match | USD | USD | US | 5 | PASS |
| Harry Barker | pets | harrybarker.com | ok | yes | yes | yes | yes | 34 | 156 | 55% | match | USD | USD | US | 5 | PASS |
| Herbsmith | pets | herbsmithinc.com | ok | yes | yes | yes | yes | 66 | 269 | 100% | match | USD | USD | US | 5 | PASS |
| Jinx | pets | www.jinx.com | ok | yes | yes | no | no | - | - | - | - | - | - | - | 2 | fail: blocked |
| Jolly Pets | pets | jollypets.com | ok | yes | yes | yes | yes | 50 | 394 | 71% | missing | - | - | US | 5 | fail: currency not proven USD, product .js unavailable |
| Leash Boss | pets | leashboss.com | ok | yes | yes | yes | yes | 30 | 152 | 57% | match | USD | USD | US | 5 | PASS |
| Maxbone | pets | www.maxbone.com | ok | yes | yes | yes | yes | 105 | 491 | 91% | match | USD | USD | US | 5 | PASS |
| Appointed | stationery_edc | appointed.co | ok | yes | yes | yes | yes | 138 | 504 | 74% | match | USD | USD | US | 5 | PASS |
| ban.do | stationery_edc | www.bando.com | ok | yes | yes | yes | yes | 2183 | 4634 | 79% | match | USD | USD | US | 13 | fail: excluded category: alcohol |
| Baronfig | stationery_edc | baronfig.com | ok | yes | yes | yes | yes | 47 | 231 | 78% | match | USD | USD | US | 5 | PASS |
| BaubleBar | stationery_edc | www.baublebar.com | ok | yes | yes | yes | yes | 1750 | 6739+ | 98% | match | USD | USD | US | 11 | fail: catalog too large, excluded category: alcohol, tobacco/vape |
| Big Idea Design | stationery_edc | bigidesign.com | ok | yes | yes | yes | yes | 146 | 570 | 39% | match | USD | USD | US | 5 | PASS |
| Branch Furniture | stationery_edc | www.branchfurniture.com | ok | yes | yes | yes | yes | 226 | 4873 | 93% | match | USD | USD | US | 5 | PASS |
| Craighill | stationery_edc | craighill.co | ok | yes | yes | yes | yes | 42 | 103 | 82% | match | USD | USD | US | 5 | fail: excluded category: alcohol |
| Cuyana | stationery_edc | cuyana.com | ok | yes | yes | yes | yes | 960 | 5832 | 25% | match | USD | USD | US | 8 | fail: catalog too large |
| Dagne Dover | stationery_edc | www.dagnedover.com | ok | yes | yes | yes | yes | 417 | 456 | 72% | match | - | USD | US | 6 | PASS |
| Everyman | stationery_edc | everyman.co | ok | yes | yes | yes | yes | 136 | 290 | 90% | match | USD | USD | US | 5 | fail: excluded category: tobacco/vape |
| Faber-Castell | stationery_edc | fabercastell.com | ok | yes | yes | yes | yes | 1301 | 2141 | 82% | match | - | USD | US | 10 | PASS |
| Fenix Lighting | stationery_edc | www.fenixlighting.com | ok | yes | yes | yes | yes | 477 | 758 | 61% | match | USD | USD | US | 6 | fail: excluded category: weapons |
| Gorjana | stationery_edc | www.gorjana.com | ok | yes | yes | yes | yes | 249 | 775 | 100% | match | USD | USD | US | 5 | PASS |
| Goulet Pens | stationery_edc | www.gouletpens.com | ok | yes | yes | yes | yes | 3250 | 5136+ | 75% | match | USD | USD | US | 17 | fail: catalog too large, excluded category: alcohol |
| Ink+Volt | stationery_edc | inkandvolt.com | ok | yes | yes | yes | yes | 111 | 273 | 68% | match | USD | USD | US | 5 | PASS |
| Rocketbook | stationery_edc | getrocketbook.com | ok | yes | yes | yes | yes | 52 | 276 | 60% | match | USD | USD | US | 5 | PASS |
| Babyletto | toys_baby | babyletto.com | ok | yes | yes | yes | yes | 284 | 1046 | 92% | match | USD | USD | US | 6 | PASS |
| Boba | toys_baby | boba.com | ok | yes | yes | yes | yes | 63 | 66 | 77% | match | USD | USD | US | 5 | PASS |
| Bumkins | toys_baby | www.bumkins.com | ok | yes | yes | yes | yes | 495 | 499 | 77% | match | USD | USD | US | 6 | PASS |
| Comotomo | toys_baby | comotomo.com | ok | yes | yes | yes | yes | 14 | 28 | 86% | match | - | USD | US | 5 | PASS |
| Crazy Forts | toys_baby | crazyforts.com | ok | yes | yes | yes | yes | 10 | 10 | 100% | match | - | CAD | CA | 5 | fail: currency not proven USD |
| Doona | toys_baby | www.doona.com | ok | yes | yes | yes | no | - | - | - | - | - | - | - | 2 | fail: not shopify |
| Dr. Brown's | toys_baby | drbrownsbaby.com | ok | yes | yes | yes | yes | 373 | 373 | 93% | match | USD | USD | US | 6 | PASS |
| Evenflo | toys_baby | www.evenflo.com | ok | yes | yes | yes | yes | 103 | 223 | 78% | match | USD | USD | US | 5 | PASS |
| ezpz | toys_baby | ezpzfun.com | ok | yes | yes | yes | yes | 124 | 515 | 97% | match | - | USD | US | 5 | PASS |
| Frida | toys_baby | frida.com | ok | yes | yes | yes | yes | 184 | 241 | 92% | match | - | USD | US | 5 | PASS |
| GoldieBlox | toys_baby | goldieblox.com | ok | yes | yes | yes | yes | 1 | 1 | 100% | match | USD | USD | US | 5 | PASS |
| Guardian Bikes | toys_baby | guardianbikes.com | ok | yes | yes | yes | yes | 39 | 211 | 100% | match | - | USD | US | 5 | PASS |
| Guidecraft | toys_baby | guidecraft.com | ok | yes | yes | yes | yes | 632 | 845 | 63% | match | USD | USD | US | 7 | PASS |
| HABA USA | toys_baby | www.habausa.com | ok | yes | yes | yes | yes | 419 | 460 | 95% | match | USD | USD | US | 6 | PASS |
| HALO Sleep | toys_baby | www.halosleep.com | ok | yes | yes | yes | yes | 777 | 1050 | 90% | match | USD | USD | US | 8 | PASS |
| Strider Bikes | toys_baby | striderbikes.com | ok | yes | yes | yes | yes | 55 | 55 | - | match | USD | - | - | 4 | PASS |

## Notes

- **Atlas Coffee Club**: no JSON-LD offer currency on product page
- **Chris King**: no JSON-LD offer currency on product page
- **Comotomo**: no JSON-LD offer currency on product page
- **Crazy Forts**: no JSON-LD offer currency on product page
- **Dagne Dover**: no JSON-LD offer currency on product page
- **Doona**: /products.json: http 404, text/html; charset=utf-8
- **Driftaway Coffee**: /products.json: http 404, text/html; charset=UTF-8
- **Elite Jump Ropes**: no JSON-LD offer currency on product page
- **ezpz**: no JSON-LD offer currency on product page
- **Faber-Castell**: no JSON-LD offer currency on product page
- **Fairdale Bikes**: /products.json: http 404, text/html; charset=UTF-8
- **Finish Line**: no JSON-LD offer currency on product page
- **Frida**: no JSON-LD offer currency on product page
- **FurHaven**: /products.json: http 404, text/html
- **George Howell Coffee**: no JSON-LD offer currency on product page
- **Guardian Bikes**: no JSON-LD offer currency on product page
- **Jinx**: stopped: blocked: http 401
- **Jolly Pets**: product .js: http 404; product page: http 404
- **Ultimate Direction**: sample page is not a priced BigCommerce product page
