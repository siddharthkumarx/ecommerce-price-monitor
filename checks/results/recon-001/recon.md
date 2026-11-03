# Recon `recon-001`

- started: 2026-11-03T21:40:28+00:00, finished: 2026-11-03T21:45:24+00:00
- run: https://github.com/siddharthkumarx/ecommerce-price-monitor-wip/actions/runs/41723890450
- candidates: 92, passed: 0 (variant cap 3000)

| store | category | host | robots | products.json | .js | reachable | shopify | products | variants | in stock | .js check | JSON-LD cur | Shopify cur | meta country | reqs | result |
|---|---|---|---|---|---|---|---|---:|---:|---:|---|---|---|---|---:|---|
| Allbirds | apparel | www.allbirds.com | ok | yes | yes | yes | yes | 250 | 3009+ | 57% | missing | USD | USD | US | 5 | fail: catalog too large, product .js unavailable |
| Bombas | apparel | bombas.com | unreachable | - | - | no | no | - | - | - | - | - | - | - | 4 | fail: blocked |
| Buck Mason | apparel | www.buckmason.com | ok | no | no | no | no | - | - | - | - | - | - | - | 1 | fail: robots disallows |
| Chubbies | apparel | www.chubbiesshorts.com | ok | yes | yes | yes | no | - | - | - | - | - | - | - | 2 | fail: not shopify |
| Cuts Clothing | apparel | www.cutsclothing.com | ok | yes | yes | yes | no | - | - | - | - | - | - | - | 2 | fail: not shopify |
| Faherty | apparel | fahertybrand.com | ok | yes | yes | yes | yes | - | - | - | missing | USD | USD | US | 8 | fail: blocked mid-recon, empty catalog, product .js unavailable |
| Girlfriend Collective | apparel | girlfriend.com | ok | yes | yes | yes | yes | 163 | 2525 | 67% | missing | USD | USD | US | 6 | fail: product .js unavailable |
| Mack Weldon | apparel | mackweldon.com | ok | yes | yes | yes | yes | - | - | - | - | - | - | - | 3 | fail: blocked mid-recon, empty catalog, currency not proven USD, product .js unavailable |
| Marine Layer | apparel | www.marinelayer.com | ok | yes | yes | yes | yes | - | - | - | missing | - | - | - | 6 | fail: blocked mid-recon, empty catalog, currency not proven USD, product .js unavailable |
| Ministry of Supply | apparel | www.ministryofsupply.com | ok | yes | yes | no | no | - | - | - | - | - | - | - | 2 | fail: blocked |
| Outdoor Voices | apparel | www.outdoorvoices.com | ok | yes | yes | yes | yes | 413 | 2776 | 68% | missing | USD | USD | US | 6 | fail: product .js unavailable |
| Public Rec | apparel | publicrec.com | ok | yes | yes | yes | no | - | - | - | - | - | - | - | 2 | fail: not shopify |
| Rhone | apparel | rhone.com | not-fetched | - | - | no | no | - | - | - | - | - | - | - | 1 | fail: blocked |
| Rothy's | apparel | rothys.com | ok | yes | yes | yes | yes | 250 | 4253+ | 93% | missing | USD | USD | US | 8 | fail: catalog too large, product .js unavailable |
| Taylor Stitch | apparel | www.taylorstitch.com | ok | yes | yes | yes | yes | 500 | 3157+ | 64% | missing | USD | USD | US | 6 | fail: catalog too large, product .js unavailable |
| Ten Thousand | apparel | www.tenthousand.cc | ok | yes | yes | yes | yes | 88 | 2985 | 58% | missing | USD | USD | US | 6 | fail: product .js unavailable |
| True Classic | apparel | www.trueclassictees.com | ok | yes | yes | yes | yes | 500 | 4101+ | 73% | missing | USD | USD | US | 7 | fail: catalog too large, product .js unavailable |
| Vuori | apparel | vuoriclothing.com | ok | yes | yes | yes | no | - | - | - | - | - | - | - | 2 | fail: not shopify |
| Western Rise | apparel | westernrise.com | ok | yes | yes | no | no | - | - | - | - | - | - | - | 2 | fail: blocked |
| Audioengine | audio | audioengine.com | ok | yes | yes | yes | no | - | - | - | - | - | - | - | 2 | fail: not shopify |
| Campfire Audio | audio | www.campfireaudio.com | ok | yes | yes | yes | yes | 77 | 174 | 83% | missing | USD | USD | US | 5 | fail: product .js unavailable |
| Dekoni Audio | audio | dekoniaudio.com | ok | yes | yes | yes | yes | 167 | 515 | 67% | missing | USD | USD | US | 6 | fail: product .js unavailable |
| EarFun | audio | www.myearfun.com | ok | yes | yes | yes | no | - | - | - | - | - | - | - | 2 | fail: not shopify |
| Fluance | audio | www.fluance.com | ok | no | no | no | no | - | - | - | - | - | - | - | 1 | fail: robots disallows |
| Grado Labs | audio | gradolabs.com | ok | yes | yes | yes | yes | 64 | 115 | 96% | missing | USD | USD | US | 5 | fail: product .js unavailable |
| House of Marley | audio | thehouseofmarley.com | ok | yes | yes | yes | yes | 62 | 114 | 60% | missing | - | USD | US | 6 | fail: product .js unavailable |
| JLab | audio | www.jlab.com | ok | yes | yes | yes | yes | 434 | 438 | 70% | missing | USD | USD | US | 6 | fail: product .js unavailable |
| Kanto Audio | audio | kantoaudio.com | ok | yes | yes | yes | yes | 44 | 112 | 50% | missing | USD | USD | CA | 7 | fail: product .js unavailable |
| Master & Dynamic | audio | www.masterdynamic.com | ok | yes | yes | yes | yes | 60 | 195 | 57% | missing | USD | USD | US | 5 | fail: product .js unavailable |
| Nothing (US) | audio | us.nothing.tech | ok | yes | yes | yes | no | - | - | - | - | - | - | - | 2 | fail: not shopify |
| Raycon | audio | rayconglobal.com | ok | yes | yes | yes | yes | 37 | 128 | 66% | missing | USD | USD | US | 7 | fail: product .js unavailable |
| Shokz | audio | shokz.com | ok | yes | yes | yes | yes | 66 | 426 | 85% | missing | USD | USD | US | 5 | fail: product .js unavailable |
| Skullcandy | audio | www.skullcandy.com | ok | yes | yes | yes | yes | 50 | 177 | 84% | missing | USD | USD | US | 5 | fail: product .js unavailable |
| Soundcore (US) | audio | us.soundcore.com | ok | yes | yes | yes | yes | 521 | 1436 | 74% | missing | USD | USD | US | 7 | fail: product .js unavailable |
| Soundpeats | audio | soundpeats.com | ok | yes | yes | yes | yes | 20 | 138 | 92% | missing | USD | USD | HK | 5 | fail: product .js unavailable |
| Status Audio | audio | www.status.co | ok | yes | yes | yes | yes | 17 | 49 | 96% | missing | USD | USD | US | 6 | fail: product .js unavailable |
| Tribit | audio | tribitaudio.com | unreachable | - | - | no | no | - | - | - | - | - | - | - | 4 | fail: blocked |
| Beardbrand | beauty | beardbrand.com | unreachable | - | - | no | no | - | - | - | - | - | - | - | 1 | fail: blocked |
| Briogeo | beauty | www.briogeohair.com | missing-4xx | yes | yes | yes | no | - | - | - | - | - | - | - | 2 | fail: not shopify |
| ColourPop | beauty | colourpop.com | ok | yes | yes | yes | yes | - | - | - | - | - | - | - | 3 | fail: blocked mid-recon, empty catalog, currency not proven USD, product .js unavailable |
| Dr. Squatch | beauty | drsquatch.com | unreachable | - | - | no | no | - | - | - | - | - | - | - | 1 | fail: blocked |
| Glossier | beauty | glossier.com | unreachable | - | - | no | no | - | - | - | - | - | - | - | 1 | fail: blocked |
| Glow Recipe | beauty | glowrecipe.com | unreachable | - | - | no | no | - | - | - | - | - | - | - | 1 | fail: blocked |
| Herbivore Botanicals | beauty | herbivorebotanicals.com | unreachable | - | - | no | no | - | - | - | - | - | - | - | 1 | fail: blocked |
| ILIA | beauty | iliabeauty.com | unreachable | - | - | no | no | - | - | - | - | - | - | - | 1 | fail: blocked |
| Kosas | beauty | kosas.com | unreachable | - | - | no | no | - | - | - | - | - | - | - | 1 | fail: blocked |
| Kylie Cosmetics | beauty | kyliecosmetics.com | unreachable | - | - | no | no | - | - | - | - | - | - | - | 1 | fail: blocked |
| Merit | beauty | meritbeauty.com | unreachable | - | - | no | no | - | - | - | - | - | - | - | 1 | fail: blocked |
| Milk Makeup | beauty | milkmakeup.com | ok | yes | yes | yes | yes | - | - | - | missing | USD | USD | - | 5 | fail: blocked mid-recon, empty catalog, product .js unavailable |
| Native | beauty | nativecos.com | unreachable | - | - | no | no | - | - | - | - | - | - | - | 1 | fail: blocked |
| OUAI | beauty | theouai.com | unreachable | - | - | no | no | - | - | - | - | - | - | - | 1 | fail: blocked |
| Rare Beauty | beauty | rarebeauty.com | unreachable | - | - | no | no | - | - | - | - | - | - | - | 1 | fail: blocked |
| Summer Fridays | beauty | summerfridays.com | unreachable | - | - | no | no | - | - | - | - | - | - | - | 1 | fail: blocked |
| Supergoop! | beauty | supergoop.com | unreachable | - | - | no | no | - | - | - | - | - | - | - | 1 | fail: blocked |
| Tower 28 | beauty | tower28beauty.com | unreachable | - | - | no | no | - | - | - | - | - | - | - | 1 | fail: blocked |
| Youth To The People | beauty | www.youthtothepeople.com | ok | yes | yes | no | no | - | - | - | - | - | - | - | 2 | fail: blocked |
| Blueland | home_kitchen | blueland.com | unreachable | - | - | no | no | - | - | - | - | - | - | - | 1 | fail: blocked |
| Boll & Branch | home_kitchen | bollandbranch.com | unreachable | - | - | no | no | - | - | - | - | - | - | - | 1 | fail: blocked |
| Brightland | home_kitchen | brightland.co | unreachable | - | - | no | no | - | - | - | - | - | - | - | 1 | fail: blocked |
| Brooklinen | home_kitchen | brooklinen.com | unreachable | - | - | no | no | - | - | - | - | - | - | - | 1 | fail: blocked |
| Buffy | home_kitchen | buffy.co | unreachable | - | - | no | no | - | - | - | - | - | - | - | 1 | fail: blocked |
| Burrow | home_kitchen | burrow.com | ok | yes | yes | yes | no | - | - | - | - | - | - | - | 2 | fail: not shopify |
| Caraway | home_kitchen | carawayhome.com | ok | yes | yes | yes | no | - | - | - | - | - | - | - | 2 | fail: not shopify |
| Ember | home_kitchen | ember.com | unreachable | - | - | no | no | - | - | - | - | - | - | - | 1 | fail: blocked |
| Fellow | home_kitchen | fellowproducts.com | unreachable | - | - | no | no | - | - | - | - | - | - | - | 1 | fail: blocked |
| Graza | home_kitchen | graza.co | unreachable | - | - | no | no | - | - | - | - | - | - | - | 1 | fail: blocked |
| Great Jones | home_kitchen | greatjonesgoods.com | unreachable | - | - | no | no | - | - | - | - | - | - | - | 1 | fail: blocked |
| HexClad | home_kitchen | hexclad.com | ok | yes | yes | no | no | - | - | - | - | - | - | - | 2 | fail: blocked |
| Made In | home_kitchen | madeincookware.com | ok | yes | yes | no | no | - | - | - | - | - | - | - | 2 | fail: blocked |
| Material Kitchen | home_kitchen | materialkitchen.com | ok | yes | yes | no | no | - | - | - | - | - | - | - | 3 | fail: blocked |
| Misen | home_kitchen | misen.com | unreachable | - | - | no | no | - | - | - | - | - | - | - | 1 | fail: blocked |
| Our Place | home_kitchen | fromourplace.com | unreachable | - | - | no | no | - | - | - | - | - | - | - | 1 | fail: blocked |
| Parachute | home_kitchen | parachutehome.com | unreachable | - | - | no | no | - | - | - | - | - | - | - | 1 | fail: blocked |
| Public Goods | home_kitchen | publicgoods.com | unreachable | - | - | no | no | - | - | - | - | - | - | - | 1 | fail: blocked |
| BioLite | outdoor | bioliteenergy.com | unreachable | - | - | no | no | - | - | - | - | - | - | - | 1 | fail: blocked |
| Cotopaxi | outdoor | cotopaxi.com | unreachable | - | - | no | no | - | - | - | - | - | - | - | 1 | fail: blocked |
| GRAYL | outdoor | grayl.com | unreachable | - | - | no | no | - | - | - | - | - | - | - | 1 | fail: blocked |
| Kammok | outdoor | kammok.com | ok | yes | yes | no | no | - | - | - | - | - | - | - | 2 | fail: blocked |
| Klymit | outdoor | klymit.com | unreachable | - | - | no | no | - | - | - | - | - | - | - | 1 | fail: blocked |
| LifeStraw | outdoor | lifestraw.com | unreachable | - | - | no | no | - | - | - | - | - | - | - | 1 | fail: blocked |
| Matador | outdoor | matadorup.com | unreachable | - | - | no | no | - | - | - | - | - | - | - | 1 | fail: blocked |
| NEMO Equipment | outdoor | nemoequipment.com | unreachable | - | - | no | no | - | - | - | - | - | - | - | 1 | fail: blocked |
| Nomatic | outdoor | nomatic.com | unreachable | - | - | no | no | - | - | - | - | - | - | - | 1 | fail: blocked |
| Oru Kayak | outdoor | orukayak.com | unreachable | - | - | no | no | - | - | - | - | - | - | - | 1 | fail: blocked |
| Peak Design | outdoor | peakdesign.com | unreachable | - | - | no | no | - | - | - | - | - | - | - | 1 | fail: blocked |
| Ruffwear | outdoor | ruffwear.com | unreachable | - | - | no | no | - | - | - | - | - | - | - | 1 | fail: blocked |
| Rumpl | outdoor | rumpl.com | unreachable | - | - | no | no | - | - | - | - | - | - | - | 1 | fail: blocked |
| Snow Peak | outdoor | snowpeak.com | unreachable | - | - | no | no | - | - | - | - | - | - | - | 1 | fail: blocked |
| Solo Stove | outdoor | www.solostove.com | not-fetched | - | - | no | no | - | - | - | - | - | - | - | 1 | fail: blocked |
| Stanley | outdoor | stanley1913.com | unreachable | - | - | no | no | - | - | - | - | - | - | - | 1 | fail: blocked |
| Topo Designs | outdoor | topodesigns.com | unreachable | - | - | no | no | - | - | - | - | - | - | - | 1 | fail: blocked |
| United By Blue | outdoor | unitedbyblue.com | ok | yes | yes | no | no | - | - | - | - | - | - | - | 2 | fail: blocked |

## Notes

- **Allbirds**: product .js: http 200
- **Audioengine**: /products.json: http 404, text/html; charset=UTF-8
- **Beardbrand**: stopped: robots.txt unreachable: blocked: cloudflare challenge (http 429)
- **BioLite**: stopped: robots.txt unreachable: blocked: cloudflare challenge (http 429)
- **Blueland**: stopped: robots.txt unreachable: blocked: cloudflare challenge (http 429)
- **Boll & Branch**: stopped: robots.txt unreachable: blocked: cloudflare challenge (http 429)
- **Bombas**: stopped: robots.txt unreachable: retries exhausted: http 429
- **Brightland**: stopped: robots.txt unreachable: blocked: cloudflare challenge (http 429)
- **Briogeo**: /products.json: http 404, text/html; charset=utf-8
- **Brooklinen**: stopped: robots.txt unreachable: blocked: cloudflare challenge (http 429)
- **Buffy**: stopped: robots.txt unreachable: blocked: cloudflare challenge (http 429)
- **Burrow**: /products.json: http 404, text/plain;charset=UTF-8
- **Campfire Audio**: product .js: http 200
- **Caraway**: /products.json: http 404, text/html
- **Chubbies**: /products.json: http 404, text/html
- **ColourPop**: stopped: blocked: cloudflare challenge (http 429)
- **Cotopaxi**: stopped: robots.txt unreachable: blocked: cloudflare challenge (http 429)
- **Cuts Clothing**: /products.json: http 404, text/html
- **Dekoni Audio**: product .js: http 200
- **Dr. Squatch**: stopped: robots.txt unreachable: blocked: cloudflare challenge (http 429)
- **EarFun**: /products.json: http 404, application/json
- **Ember**: stopped: robots.txt unreachable: blocked: cloudflare challenge (http 429)
- **Faherty**: stopped: blocked: cloudflare challenge (http 429); product .js: http 200
- **Fellow**: stopped: robots.txt unreachable: blocked: cloudflare challenge (http 429)
- **Girlfriend Collective**: product .js: http 200
- **Glossier**: stopped: robots.txt unreachable: blocked: cloudflare challenge (http 429)
- **Glow Recipe**: stopped: robots.txt unreachable: blocked: cloudflare challenge (http 429)
- **Grado Labs**: product .js: http 200
- **GRAYL**: stopped: robots.txt unreachable: blocked: cloudflare challenge (http 429)
- **Graza**: stopped: robots.txt unreachable: blocked: cloudflare challenge (http 429)
- **Great Jones**: stopped: robots.txt unreachable: blocked: cloudflare challenge (http 429)
- **Herbivore Botanicals**: stopped: robots.txt unreachable: blocked: cloudflare challenge (http 429)
- **HexClad**: stopped: blocked: cloudflare challenge (http 429)
- **House of Marley**: product .js: http 200; no JSON-LD offer currency on product page
- **ILIA**: stopped: robots.txt unreachable: blocked: cloudflare challenge (http 429)
- **JLab**: product .js: http 200
- **Kammok**: stopped: blocked: cloudflare challenge (http 429)
- **Kanto Audio**: product .js: http 200
- **Klymit**: stopped: robots.txt unreachable: blocked: cloudflare challenge (http 429)
- **Kosas**: stopped: robots.txt unreachable: blocked: cloudflare challenge (http 429)
- **Kylie Cosmetics**: stopped: robots.txt unreachable: blocked: cloudflare challenge (http 429)
- **LifeStraw**: stopped: robots.txt unreachable: blocked: cloudflare challenge (http 429)
- **Mack Weldon**: stopped: blocked: cloudflare challenge (http 429)
- **Made In**: stopped: blocked: http 403
- **Marine Layer**: stopped: blocked: cloudflare challenge (http 429); product .js: http 200
- **Master & Dynamic**: product .js: http 200
- **Matador**: stopped: robots.txt unreachable: blocked: cloudflare challenge (http 429)
- **Material Kitchen**: stopped: blocked: cloudflare challenge (http 429)
- **Merit**: stopped: robots.txt unreachable: blocked: cloudflare challenge (http 429)
- **Milk Makeup**: stopped: blocked: cloudflare challenge (http 429); product .js: http 200
- **Ministry of Supply**: stopped: blocked: cloudflare challenge
- **Misen**: stopped: robots.txt unreachable: blocked: cloudflare challenge (http 429)
- **Native**: stopped: robots.txt unreachable: blocked: cloudflare challenge (http 429)
- **NEMO Equipment**: stopped: robots.txt unreachable: blocked: cloudflare challenge (http 429)
- **Nomatic**: stopped: robots.txt unreachable: blocked: cloudflare challenge (http 429)
- **Nothing (US)**: /products.json: http 404, text/html
- **Oru Kayak**: stopped: robots.txt unreachable: blocked: cloudflare challenge (http 429)
- **OUAI**: stopped: robots.txt unreachable: blocked: cloudflare challenge (http 429)
- **Our Place**: stopped: robots.txt unreachable: blocked: cloudflare challenge (http 429)
- **Outdoor Voices**: product .js: http 200
- **Parachute**: stopped: robots.txt unreachable: blocked: cloudflare challenge (http 429)
- **Peak Design**: stopped: robots.txt unreachable: blocked: cloudflare challenge (http 429)
- **Public Goods**: stopped: robots.txt unreachable: blocked: cloudflare challenge (http 429)
- **Public Rec**: /products.json: http 200, application/json; charset=utf-8
- **Rare Beauty**: stopped: robots.txt unreachable: blocked: cloudflare challenge (http 429)
- **Raycon**: product .js: http 200
- **Rhone**: stopped: blocked: cloudflare challenge (robots.txt)
- **Rothy's**: product .js: http 200
- **Ruffwear**: stopped: robots.txt unreachable: blocked: cloudflare challenge (http 429)
- **Rumpl**: stopped: robots.txt unreachable: blocked: cloudflare challenge (http 429)
- **Shokz**: product .js: http 200
- **Skullcandy**: product .js: http 200
- **Snow Peak**: stopped: robots.txt unreachable: blocked: cloudflare challenge (http 429)
- **Solo Stove**: stopped: blocked: cloudflare challenge (robots.txt)
- **Soundcore (US)**: product .js: http 200
- **Soundpeats**: product .js: http 200
- **Stanley**: stopped: robots.txt unreachable: blocked: cloudflare challenge (http 429)
- **Status Audio**: product .js: http 200
- **Summer Fridays**: stopped: robots.txt unreachable: blocked: cloudflare challenge (http 429)
- **Supergoop!**: stopped: robots.txt unreachable: blocked: cloudflare challenge (http 429)
- **Taylor Stitch**: product .js: http 200
- **Ten Thousand**: product .js: http 200
- **Topo Designs**: stopped: robots.txt unreachable: blocked: cloudflare challenge (http 429)
- **Tower 28**: stopped: robots.txt unreachable: blocked: cloudflare challenge (http 429)
- **Tribit**: stopped: robots.txt unreachable: retries exhausted: network error: ConnectTimeout
- **True Classic**: product .js: http 200
- **United By Blue**: stopped: blocked: cloudflare challenge
- **Vuori**: /products.json: http 404, text/html; charset=utf-8
- **Western Rise**: stopped: blocked: http 401
- **Youth To The People**: stopped: blocked: cloudflare challenge
