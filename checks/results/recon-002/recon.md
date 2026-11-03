# Recon `recon-002`

- started: 2026-11-03T21:49:05+00:00, finished: 2026-11-03T22:13:47+00:00
- run: https://github.com/siddharthkumarx/ecommerce-price-monitor-wip/actions/runs/41725141533
- candidates: 92, passed: 54 (variant cap 3000)
- run-wide request interval: 2.0s + jitter; halted: no

| store | category | host | robots | products.json | .js | reachable | shopify | products | variants | in stock | .js check | JSON-LD cur | Shopify cur | meta country | reqs | result |
|---|---|---|---|---|---|---|---|---:|---:|---:|---|---|---|---|---:|---|
| Allbirds | apparel | www.allbirds.com | ok | yes | yes | yes | yes | 250 | 3009+ | 57% | match | USD | USD | US | 6 | fail: catalog too large |
| Bombas | apparel | bombas.com | unreachable | - | - | no | no | - | - | - | - | - | - | - | 4 | fail: blocked |
| Buck Mason | apparel | www.buckmason.com | ok | no | no | no | no | - | - | - | - | - | - | - | 1 | fail: robots disallows |
| Chubbies | apparel | www.chubbiesshorts.com | ok | yes | yes | yes | no | - | - | - | - | - | - | - | 2 | fail: not shopify |
| Cuts Clothing | apparel | www.cutsclothing.com | ok | yes | yes | yes | no | - | - | - | - | - | - | - | 2 | fail: not shopify |
| Faherty | apparel | fahertybrand.com | ok | yes | yes | yes | yes | 750 | 4654+ | 77% | match | USD | USD | US | 8 | fail: catalog too large |
| Girlfriend Collective | apparel | girlfriend.com | ok | yes | yes | yes | yes | 163 | 2525 | 67% | match | USD | USD | US | 5 | PASS |
| Mack Weldon | apparel | mackweldon.com | ok | yes | yes | yes | yes | 250 | 16279+ | 92% | match | USD | USD | US | 6 | fail: catalog too large |
| Marine Layer | apparel | www.marinelayer.com | ok | yes | yes | yes | yes | 750 | 4098+ | 84% | match | USD | USD | US | 7 | fail: catalog too large |
| Ministry of Supply | apparel | www.ministryofsupply.com | ok | yes | yes | no | no | - | - | - | - | - | - | - | 2 | fail: blocked |
| Outdoor Voices | apparel | www.outdoorvoices.com | ok | yes | yes | yes | yes | 413 | 2776 | 68% | match | USD | USD | US | 8 | PASS |
| Public Rec | apparel | publicrec.com | ok | yes | yes | yes | no | - | - | - | - | - | - | - | 2 | fail: not shopify |
| Rhone | apparel | rhone.com | unreachable | - | - | no | no | - | - | - | - | - | - | - | 1 | fail: blocked |
| Rothy's | apparel | rothys.com | ok | yes | yes | yes | yes | 250 | 4253+ | 93% | match | USD | USD | US | 7 | fail: catalog too large |
| Taylor Stitch | apparel | www.taylorstitch.com | ok | yes | yes | yes | yes | 500 | 3157+ | 64% | match | USD | USD | US | 7 | fail: catalog too large |
| Ten Thousand | apparel | www.tenthousand.cc | ok | yes | yes | yes | yes | 88 | 2985 | 58% | match | USD | USD | US | 6 | PASS |
| True Classic | apparel | www.trueclassictees.com | ok | yes | yes | yes | yes | 500 | 4101+ | 73% | match | USD | USD | US | 8 | fail: catalog too large |
| Vuori | apparel | vuoriclothing.com | ok | yes | yes | yes | no | - | - | - | - | - | - | - | 2 | fail: not shopify |
| Western Rise | apparel | westernrise.com | ok | yes | yes | no | no | - | - | - | - | - | - | - | 2 | fail: blocked |
| Audioengine | audio | audioengine.com | ok | yes | yes | yes | no | - | - | - | - | - | - | - | 2 | fail: not shopify |
| Campfire Audio | audio | www.campfireaudio.com | ok | yes | yes | yes | yes | 77 | 174 | 83% | match | USD | USD | US | 6 | PASS |
| Dekoni Audio | audio | dekoniaudio.com | ok | yes | yes | yes | yes | 167 | 515 | 67% | match | USD | USD | US | 5 | PASS |
| EarFun | audio | www.myearfun.com | ok | yes | yes | yes | no | - | - | - | - | - | - | - | 2 | fail: not shopify |
| Fluance | audio | www.fluance.com | ok | no | no | no | no | - | - | - | - | - | - | - | 1 | fail: robots disallows |
| Grado Labs | audio | gradolabs.com | ok | yes | yes | yes | yes | 64 | 115 | 96% | match | USD | USD | US | 5 | PASS |
| House of Marley | audio | thehouseofmarley.com | ok | yes | yes | yes | yes | 62 | 114 | 60% | match | - | USD | US | 7 | PASS |
| JLab | audio | www.jlab.com | ok | yes | yes | yes | yes | 434 | 438 | 70% | match | USD | USD | US | 6 | PASS |
| Kanto Audio | audio | kantoaudio.com | ok | yes | yes | yes | yes | 44 | 112 | 50% | match | USD | USD | CA | 5 | PASS |
| Master & Dynamic | audio | www.masterdynamic.com | ok | yes | yes | yes | yes | 60 | 195 | 57% | match | USD | USD | US | 5 | PASS |
| Nothing (US) | audio | us.nothing.tech | ok | yes | yes | yes | no | - | - | - | - | - | - | - | 2 | fail: not shopify |
| Raycon | audio | rayconglobal.com | ok | yes | yes | yes | yes | 37 | 128 | 66% | match | USD | USD | US | 6 | PASS |
| Shokz | audio | shokz.com | ok | yes | yes | yes | yes | 66 | 426 | 85% | match | USD | USD | US | 5 | PASS |
| Skullcandy | audio | www.skullcandy.com | ok | yes | yes | yes | yes | 50 | 177 | 84% | match | USD | USD | US | 5 | PASS |
| Soundcore (US) | audio | us.soundcore.com | ok | yes | yes | yes | yes | 521 | 1436 | 74% | match | USD | USD | US | 7 | PASS |
| Soundpeats | audio | soundpeats.com | ok | yes | yes | yes | yes | 20 | 138 | 92% | match | USD | USD | HK | 6 | PASS |
| Status Audio | audio | www.status.co | ok | yes | yes | yes | yes | 17 | 49 | 96% | match | USD | USD | US | 5 | PASS |
| Tribit | audio | tribitaudio.com | unreachable | - | - | no | no | - | - | - | - | - | - | - | 4 | fail: blocked |
| Beardbrand | beauty | www.beardbrand.com | ok | yes | yes | yes | yes | 67 | 105 | 90% | match | USD | USD | US | 5 | PASS |
| Briogeo | beauty | www.briogeohair.com | missing-4xx | yes | yes | yes | no | - | - | - | - | - | - | - | 2 | fail: not shopify |
| ColourPop | beauty | colourpop.com | ok | yes | yes | yes | yes | 1077 | 1077 | 96% | match | USD | USD | US | 11 | PASS |
| Dr. Squatch | beauty | www.drsquatch.com | ok | yes | yes | yes | no | - | - | - | - | - | - | - | 3 | fail: not shopify |
| Glossier | beauty | www.glossier.com | ok | yes | yes | yes | yes | 115 | 359 | 99% | match | USD | USD | US | 5 | PASS |
| Glow Recipe | beauty | www.glowrecipe.com | ok | yes | yes | yes | yes | 130 | 214 | 90% | match | USD | USD | US | 6 | PASS |
| Herbivore Botanicals | beauty | www.herbivorebotanicals.com | ok | yes | yes | yes | yes | 50 | 65 | 42% | match | USD | USD | US | 5 | PASS |
| ILIA | beauty | iliabeauty.com | ok | yes | yes | yes | yes | 76 | 333 | 94% | match | USD | USD | US | 6 | PASS |
| Kosas | beauty | kosas.com | ok | yes | yes | yes | yes | 76 | 330 | 86% | match | - | USD | US | 5 | PASS |
| Kylie Cosmetics | beauty | kyliecosmetics.com | ok | yes | yes | yes | yes | 258 | 708 | 78% | match | USD | USD | US | 8 | PASS |
| Merit | beauty | www.meritbeauty.com | ok | yes | yes | yes | yes | 175 | 253 | 97% | match | USD | USD | US | 6 | PASS |
| Milk Makeup | beauty | milkmakeup.com | ok | yes | yes | yes | yes | 74 | 318 | 80% | match | USD | USD | US | 6 | PASS |
| Native | beauty | www.nativecos.com | ok | yes | yes | yes | yes | 95 | 508 | 95% | match | USD | USD | US | 6 | PASS |
| OUAI | beauty | theouai.com | ok | yes | yes | yes | yes | 138 | 149 | 99% | match | USD | USD | US | 7 | PASS |
| Rare Beauty | beauty | www.rarebeauty.com | ok | yes | yes | yes | yes | 152 | 547 | 72% | match | USD | USD | US | 9 | PASS |
| Summer Fridays | beauty | summerfridays.com | ok | yes | yes | yes | yes | 177 | 212 | 81% | match | USD | USD | US | 5 | PASS |
| Supergoop! | beauty | supergoop.com | ok | yes | yes | yes | yes | 94 | 199 | 92% | match | USD | USD | US | 5 | PASS |
| Tower 28 | beauty | www.tower28beauty.com | ok | yes | yes | yes | yes | 69 | 246 | 90% | match | USD | USD | US | 7 | PASS |
| Youth To The People | beauty | www.youthtothepeople.com | ok | yes | yes | no | no | - | - | - | - | - | - | - | 2 | fail: blocked |
| Blueland | home_kitchen | www.blueland.com | ok | yes | yes | yes | no | - | - | - | - | - | - | - | 2 | fail: not shopify |
| Boll & Branch | home_kitchen | www.bollandbranch.com | ok | yes | yes | yes | no | - | - | - | - | - | - | - | 2 | fail: not shopify |
| Brightland | home_kitchen | brightland.co | ok | yes | yes | yes | yes | 34 | 61 | 98% | match | USD | USD | US | 5 | PASS |
| Brooklinen | home_kitchen | www.brooklinen.com | ok | yes | yes | yes | yes | 250 | 3018+ | 85% | match | - | USD | US | 5 | fail: catalog too large |
| Buffy | home_kitchen | buffy.co | ok | yes | yes | yes | yes | 50 | 1217 | 69% | match | USD | USD | US | 5 | PASS |
| Burrow | home_kitchen | burrow.com | ok | yes | yes | yes | no | - | - | - | - | - | - | - | 2 | fail: not shopify |
| Caraway | home_kitchen | carawayhome.com | ok | yes | yes | yes | no | - | - | - | - | - | - | - | 2 | fail: not shopify |
| Ember | home_kitchen | ember.com | ok | yes | yes | yes | yes | 122 | 551 | 74% | match | - | USD | US | 6 | PASS |
| Fellow | home_kitchen | fellowproducts.com | ok | yes | yes | yes | yes | 444 | 1047 | 75% | match | USD | USD | US | 7 | PASS |
| Graza | home_kitchen | www.graza.co | ok | yes | yes | yes | yes | 81 | 148 | 99% | match | USD | USD | US | 6 | PASS |
| Great Jones | home_kitchen | greatjonesgoods.com | ok | yes | yes | yes | yes | 59 | 323 | 70% | match | USD | USD | US | 5 | PASS |
| HexClad | home_kitchen | hexclad.com | ok | yes | yes | yes | yes | 189 | 320 | 98% | match | USD | USD | US | 6 | PASS |
| Made In | home_kitchen | madeincookware.com | ok | yes | yes | no | no | - | - | - | - | - | - | - | 2 | fail: blocked |
| Material Kitchen | home_kitchen | materialkitchen.com | ok | yes | yes | yes | yes | 54 | 171 | 73% | match | USD | USD | US | 7 | PASS |
| Misen | home_kitchen | misen.com | ok | yes | yes | yes | yes | 469 | 710 | 98% | match | USD | USD | US | 7 | PASS |
| Our Place | home_kitchen | fromourplace.com | ok | yes | yes | yes | yes | 133 | 635 | 73% | match | USD | USD | US | 5 | PASS |
| Parachute | home_kitchen | parachutehome.com | ok | yes | yes | yes | yes | 1250 | 3573+ | 82% | match | USD | USD | US | 10 | fail: catalog too large |
| Public Goods | home_kitchen | www.publicgoods.com | ok | yes | yes | yes | yes | 160 | 265 | 98% | match | USD | USD | US | 6 | PASS |
| BioLite | outdoor | www.bioliteenergy.com | ok | yes | yes | yes | yes | 92 | 117 | 86% | match | USD | USD | US | 6 | PASS |
| Cotopaxi | outdoor | www.cotopaxi.com | ok | yes | yes | yes | yes | 500 | 4536+ | 40% | match | USD | USD | US | 7 | fail: catalog too large |
| GRAYL | outdoor | grayl.com | ok | yes | yes | yes | yes | 95 | 365 | 85% | match | USD | USD | US | 7 | PASS |
| Kammok | outdoor | kammok.com | ok | yes | yes | yes | yes | 90 | 279 | 77% | match | USD | USD | US | 6 | PASS |
| Klymit | outdoor | klymit.com | ok | yes | yes | yes | yes | 85 | 114 | 92% | match | USD | USD | US | 5 | PASS |
| LifeStraw | outdoor | lifestraw.com | ok | yes | yes | yes | yes | 93 | 241 | 73% | match | USD | USD | US | 5 | PASS |
| Matador | outdoor | www.matadorequipment.com | ok | yes | yes | yes | yes | 191 | 211 | 56% | match | USD | USD | US | 5 | PASS |
| NEMO Equipment | outdoor | www.nemoequipment.com | ok | yes | yes | yes | yes | 96 | 353 | 40% | match | USD | USD | US | 5 | PASS |
| Nomatic | outdoor | www.nomatic.com | ok | yes | yes | yes | yes | 114 | 746 | 87% | match | USD | USD | US | 6 | PASS |
| Oru Kayak | outdoor | www.orukayak.com | ok | yes | yes | yes | no | - | - | - | - | - | - | - | 2 | fail: not shopify |
| Peak Design | outdoor | www.peakdesign.com | ok | yes | yes | yes | no | - | - | - | - | - | - | - | 2 | fail: not shopify |
| Ruffwear | outdoor | ruffwear.com | ok | yes | yes | yes | yes | 143 | 3184 | 38% | match | USD | USD | US | 5 | fail: catalog too large |
| Rumpl | outdoor | www.rumpl.com | ok | yes | yes | yes | yes | 160 | 220 | 96% | match | USD | USD | US | 5 | PASS |
| Snow Peak | outdoor | www.snowpeak.com | unreachable | - | - | no | no | - | - | - | - | - | - | - | 1 | fail: blocked |
| Solo Stove | outdoor | www.solostove.com | unreachable | - | - | no | no | - | - | - | - | - | - | - | 1 | fail: blocked |
| Stanley | outdoor | www.stanley1913.com | ok | yes | yes | yes | yes | 377 | 2467 | 66% | match | USD | USD | US | 6 | PASS |
| Topo Designs | outdoor | topodesigns.com | ok | yes | yes | yes | yes | 551 | 2167 | 64% | match | USD | USD | US | 9 | PASS |
| United By Blue | outdoor | unitedbyblue.com | ok | yes | yes | no | no | - | - | - | - | - | - | - | 2 | fail: blocked |

## Notes

- **Audioengine**: /products.json: http 404, text/html; charset=UTF-8
- **Blueland**: /products.json: http 404, text/html
- **Boll & Branch**: /products.json: http 404, text/html
- **Bombas**: stopped: robots.txt unreachable: retries exhausted: http 429
- **Briogeo**: /products.json: http 404, text/html; charset=utf-8
- **Brooklinen**: no JSON-LD offer currency on product page
- **Burrow**: /products.json: http 404, text/plain;charset=UTF-8
- **Caraway**: /products.json: http 404, text/html
- **Chubbies**: /products.json: http 404, text/html
- **Cuts Clothing**: /products.json: http 404, text/html
- **Dr. Squatch**: /products.json: http 404, text/html
- **EarFun**: /products.json: http 404, application/json
- **Ember**: no JSON-LD offer currency on product page
- **House of Marley**: no JSON-LD offer currency on product page
- **Kosas**: no JSON-LD offer currency on product page
- **Made In**: stopped: blocked: http 403
- **Ministry of Supply**: stopped: blocked: cloudflare challenge
- **Nothing (US)**: /products.json: http 404, text/html
- **Oru Kayak**: /products.json: http 404, text/html
- **Peak Design**: /products.json: http 404, text/html
- **Public Rec**: /products.json: http 200, application/json; charset=utf-8
- **Rhone**: stopped: blocked: cloudflare challenge (robots.txt)
- **Snow Peak**: stopped: blocked: cloudflare challenge (robots.txt)
- **Solo Stove**: stopped: blocked: cloudflare challenge (robots.txt)
- **Tribit**: stopped: robots.txt unreachable: retries exhausted: network error: ConnectTimeout
- **United By Blue**: stopped: blocked: cloudflare challenge
- **Vuori**: /products.json: http 404, text/html; charset=utf-8
- **Western Rise**: stopped: blocked: http 401
- **Youth To The People**: stopped: blocked: cloudflare challenge
