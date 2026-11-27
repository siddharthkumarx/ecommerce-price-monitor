# Recon `recon-007`

- started: 2026-11-27T19:09:58+00:00, finished: 2026-11-27T22:35:47+00:00
- run: https://github.com/siddharthkumarx/ecommerce-price-monitor/actions/runs/46054716147
- candidates: 320, passed: 149 (variant cap 3000)
- run-wide request interval: 4.0s + jitter; halted: no

| store | category | host | robots | products.json | .js | reachable | shopify | products | variants | in stock | .js check | JSON-LD cur | Shopify cur | meta country | reqs | terms | result |
|---|---|---|---|---|---|---|---|---:|---:|---:|---|---|---|---|---:|---|---|
| AGOLDE | apparel | agolde.com | ok | yes | yes | yes | yes | 500 | 4125+ | 82% | match | USD | USD | US | 7 | no_ban | fail: catalog too large, excluded category: alcohol, tobacco/vape |
| Alex Mill | apparel | www.alexmill.com | ok | yes | yes | yes | yes | - | - | - | match | - | USD | US | 9 | - | fail: blocked mid-recon, empty catalog, needed 429 retries |
| Aviator Nation | apparel | www.aviatornation.com | ok | yes | yes | yes | yes | - | - | - | match | USD | USD | US | 10 | - | fail: blocked mid-recon, empty catalog, needed 429 retries |
| Big Bud Press | apparel | bigbudpress.com | ok | yes | yes | yes | yes | 250 | 3456+ | 66% | match | USD | USD | US | 6 | ban | fail: catalog too large, excluded category: alcohol |
| Brixton | apparel | www.brixton.com | ok | yes | yes | yes | yes | - | - | - | match | USD | USD | US | 9 | - | fail: blocked mid-recon, empty catalog, needed 429 retries |
| Corridor | apparel | corridornyc.com | ok | yes | yes | yes | yes | 541 | 2998 | 36% | match | USD | USD | US | 8 | ban | fail: excluded category: alcohol, tobacco/vape |
| Cuup | apparel | www.shopcuup.com | ok | yes | yes | yes | no | - | - | - | - | - | - | - | 2 | - | fail: not shopify |
| DL1961 | apparel | dl1961.com | ok | yes | yes | yes | yes | 250 | 3730+ | 53% | match | USD | USD | US | 6 | ban | fail: catalog too large, excluded category: tobacco/vape |
| Dudley Stephens | apparel | dudleystephens.com | missing-4xx | yes | yes | yes | no | - | - | - | - | - | - | - | 2 | - | fail: not shopify |
| FRAME | apparel | frame-store.com | ok | yes | yes | yes | yes | 500 | 5041+ | 74% | match | USD | USD | US | 7 | ban | fail: catalog too large, excluded category: tobacco/vape |
| Freda Salvador | apparel | fredasalvador.com | ok | yes | yes | yes | yes | 494 | 4768 | 37% | match | USD | USD | US | 7 | no_ban | fail: catalog too large |
| Freenote Cloth | apparel | freenotecloth.com | ok | yes | yes | yes | yes | 500 | 3145+ | 50% | match | USD | USD | US | 7 | ban | fail: catalog too large, excluded category: tobacco/vape |
| Hackwith Design House | apparel | hackwithdesignhouse.com | ok | yes | yes | yes | no | - | - | - | - | - | - | - | 2 | - | fail: not shopify |
| Harper Wilde | apparel | harperwilde.com | ok | yes | yes | yes | yes | 352 | 3445 | 80% | match | USD | USD | US | 7 | ban | fail: catalog too large |
| Hill House Home | apparel | www.hillhousehome.com | ok | yes | yes | yes | yes | - | - | - | match | - | USD | US | 9 | - | fail: blocked mid-recon, empty catalog, needed 429 retries |
| Iron & Resin | apparel | ironandresin.com | ok | yes | yes | yes | yes | 500 | 4849+ | 38% | match | - | USD | US | 7 | ban | fail: catalog too large, excluded category: alcohol |
| Jenni Kayne | apparel | www.jennikayne.com | ok | yes | yes | yes | yes | 249 | 1418 | 62% | match | USD | USD | US | 6 | ban | fail: excluded category: alcohol |
| Joah Brown | apparel | www.joahbrown.com | ok | yes | yes | yes | yes | 219 | 910 | 70% | match | USD | USD | US | 6 | ban | fail: excluded category: tobacco/vape |
| johnnie-O | apparel | www.johnnie-o.com | ok | yes | yes | yes | no | - | - | - | - | - | - | - | 2 | - | fail: not shopify |
| Jungmaven | apparel | jungmaven.com | ok | yes | yes | yes | yes | 250 | 9238+ | 67% | match | USD | USD | US | 6 | ban | fail: catalog too large |
| Katin | apparel | katinusa.com | ok | yes | yes | yes | yes | 250 | 3346+ | 81% | match | USD | USD | US | 6 | ban | fail: catalog too large |
| Lady White Co. | apparel | ladywhiteco.com | ok | yes | yes | yes | yes | 415 | 1510 | 49% | match | USD | USD | US | 7 | no_ban | PASS |
| Leset | apparel | leset.com | ok | yes | yes | yes | yes | 723 | 3953 | 67% | match | USD | USD | US | 8 | ban | fail: catalog too large |
| Linksoul | apparel | linksoul.com | ok | yes | yes | yes | yes | 358 | 2486 | 86% | match | USD | USD | US | 7 | no_ban | PASS |
| Lisa Says Gah | apparel | lisasaysgah.com | ok | yes | yes | yes | yes | 351 | 2121 | 53% | match | USD | USD | US | 7 | ban | fail: excluded category: alcohol, tobacco/vape |
| Lively | apparel | wearlively.com | missing-4xx | yes | yes | yes | no | - | - | - | - | - | - | - | 2 | - | fail: not shopify |
| LoveShackFancy | apparel | www.loveshackfancy.com | ok | yes | yes | yes | yes | - | - | - | match | USD | USD | US | 9 | - | fail: blocked mid-recon, empty catalog, needed 429 retries |
| Madhappy | apparel | www.madhappy.com | ok | yes | yes | yes | yes | - | - | - | match | USD | USD | US | 10 | - | fail: blocked mid-recon, empty catalog, needed 429 retries |
| Mara Hoffman | apparel | marahoffman.com | ok | yes | yes | yes | yes | 77 | 82 | 98% | match | USD | USD | US | 6 | ban | PASS |
| Margaux | apparel | thisismargaux.com | unreachable | - | - | no | no | - | - | - | - | - | - | - | 4 | - | fail: blocked |
| Mate the Label | apparel | matethelabel.com | ok | yes | yes | yes | yes | 398 | 2010 | 82% | match | USD | USD | US | 7 | ban | PASS |
| MOTHER Denim | apparel | www.motherdenim.com | ok | yes | yes | yes | yes | - | - | - | match | USD | USD | US | 9 | - | fail: blocked mid-recon, empty catalog, needed 429 retries |
| Naked Cashmere | apparel | www.nakedcashmere.com | ok | yes | yes | yes | yes | - | - | - | match | USD | USD | US | 9 | - | fail: blocked mid-recon, empty catalog, needed 429 retries |
| Negative Underwear | apparel | negativeunderwear.com | ok | yes | yes | yes | yes | 500 | 3499+ | 81% | match | USD | USD | US | 7 | ban | fail: catalog too large |
| Noah | apparel | noahny.com | ok | yes | yes | yes | yes | 437 | 3448 | 52% | match | - | USD | US | 7 | ban | fail: catalog too large |
| OBEY Clothing | apparel | obeyclothing.com | ok | yes | yes | yes | yes | 750 | 3823+ | 2% | match | USD | USD | US | 8 | ban | fail: catalog too large, excluded category: alcohol |
| Pact | apparel | wearpact.com | ok | yes | yes | yes | no | - | - | - | - | - | - | - | 2 | - | fail: not shopify |
| Psycho Bunny | apparel | www.psychobunny.com | ok | yes | yes | yes | yes | - | - | - | match | USD | USD | US | 9 | - | fail: blocked mid-recon, empty catalog, needed 429 retries |
| Rails | apparel | www.rails.com | ok | yes | yes | yes | yes | 500 | 3164+ | 67% | match | USD | USD | US | 7 | ban | fail: catalog too large, excluded category: alcohol |
| Roark | apparel | roark.com | ok | yes | yes | yes | yes | 248 | 1532 | 71% | match | USD | USD | US | 6 | ban | fail: excluded category: tobacco/vape |
| Rogue Territory | apparel | www.rogueterritory.com | ok | yes | yes | yes | yes | 129 | 1070 | 50% | match | - | USD | US | 6 | ban | fail: excluded category: alcohol |
| Saturdays NYC | apparel | www.saturdaysnyc.com | ok | yes | yes | yes | yes | - | - | - | match | USD | USD | AU | 9 | - | fail: blocked mid-recon, empty catalog, needed 429 retries |
| Seea | apparel | seea.co | ok | yes | yes | yes | no | - | - | - | - | - | - | - | 2 | - | fail: not shopify |
| Southern Tide | apparel | southerntide.com | ok | yes | yes | yes | yes | 500 | 3944+ | 90% | match | USD | USD | US | 7 | ban | fail: catalog too large, excluded category: alcohol |
| Spiritual Gangster | apparel | spiritualgangster.com | ok | yes | yes | yes | yes | 750 | 3069+ | 60% | match | USD | USD | US | 8 | ban | fail: catalog too large |
| Splits59 | apparel | www.splits59.com | ok | yes | yes | yes | yes | - | - | - | match | USD | USD | US | 9 | - | fail: blocked mid-recon, empty catalog, needed 429 retries |
| Todd Shelton | apparel | toddshelton.com | ok | yes | yes | yes | no | - | - | - | - | - | - | - | 2 | - | fail: not shopify |
| TomboyX | apparel | tomboyx.com | ok | yes | yes | yes | yes | 500 | 4680+ | 66% | match | USD | USD | US | 7 | ban | fail: catalog too large |
| Tommy John | apparel | www.tommyjohn.com | ok | yes | yes | no | no | - | - | - | - | - | - | - | 2 | - | fail: blocked |
| Tradlands | apparel | tradlands.com | ok | yes | yes | yes | yes | 46 | 1067 | 67% | match | USD | USD | US | 6 | ban | PASS |
| Universal Standard | apparel | www.universalstandard.com | ok | yes | yes | yes | yes | 250 | 3158+ | 85% | match | USD | USD | US | 6 | ban | fail: catalog too large, excluded category: alcohol |
| Velvet by Graham & Spencer | apparel | velvet-tees.com | ok | yes | yes | yes | yes | 500 | 4012+ | 84% | match | USD | USD | US | 7 | ban | fail: catalog too large |
| Vissla | apparel | www.vissla.com | ok | yes | yes | yes | yes | 668 | 3314 | 90% | match | USD | USD | US | 13 | ban | fail: catalog too large, excluded category: alcohol, weapons, needed 429 retries |
| Wildfang | apparel | www.wildfang.com | ok | yes | yes | yes | yes | 230 | 2256 | 77% | match | USD | USD | US | 6 | ban | PASS |
| Year of Ours | apparel | yearofours.com | ok | yes | yes | yes | yes | 344 | 2011 | 55% | match | USD | USD | US | 7 | ban | PASS |
| Abyss Headphones | audio | abyss-headphones.com | ok | yes | yes | yes | yes | 57 | 833 | 100% | match | USD | USD | US | 6 | ban | PASS |
| C. Crane | audio | ccrane.com | ok | yes | yes | yes | no | - | - | - | - | - | - | - | 2 | - | fail: not shopify |
| Comply Foam | audio | www.complyfoam.com | ok | yes | yes | yes | yes | 68 | 506 | 99% | match | USD | USD | US | 6 | ban | PASS |
| DS18 | audio | ds18.com | ok | yes | yes | yes | yes | 2016 | 2353 | 76% | match | USD | USD | US | 14 | ban | PASS |
| Eargasm | audio | www.eargasm.com | ok | yes | yes | yes | yes | 375 | 1000 | 97% | match | USD | USD | US | 7 | ban | fail: excluded category: alcohol |
| Earthworks Audio | audio | earthworksaudio.com | ok | yes | yes | no | no | - | - | - | - | - | - | - | 2 | - | fail: blocked |
| ECOXGEAR | audio | ecoxgear.com | ok | yes | yes | yes | yes | 78 | 279 | 90% | match | USD | USD | US | 6 | ban | PASS |
| Gemini Sound | audio | www.geminisound.com | ok | yes | yes | yes | yes | 234 | 462 | 71% | match | USD | USD | US | 6 | ban | PASS |
| HeadAmp | audio | www.headamp.com | ok | yes | yes | yes | yes | - | - | - | match | USD | USD | US | 10 | - | fail: blocked mid-recon, empty catalog, needed 429 retries |
| JDS Labs | audio | jdslabs.com | ok | yes | yes | yes | no | - | - | - | - | - | - | - | 2 | - | fail: not shopify |
| Massive Audio | audio | www.massiveaudio.com | ok | yes | yes | yes | yes | 336 | 583 | 66% | match | USD | USD | US | 7 | ban | PASS |
| Memphis Car Audio | audio | memphiscaraudio.com | unreachable | - | - | no | no | - | - | - | - | - | - | - | 1 | - | fail: blocked |
| Music Hall | audio | www.musichallaudio.com | ok | yes | yes | yes | yes | 80 | 147 | 55% | match | USD | USD | US | 6 | ban | PASS |
| MusicTeck | audio | www.musicteck.com | ok | yes | yes | yes | no | - | - | - | - | - | - | - | 2 | - | fail: not shopify |
| Needle Doctor | audio | needledoctor.com | unreachable | - | - | no | no | - | - | - | - | - | - | - | 4 | - | fail: blocked |
| Outdoor Tech | audio | outdoortech.com | missing-4xx | yes | yes | yes | no | - | - | - | - | - | - | - | 2 | - | fail: not shopify |
| Puro Sound Labs | audio | purosound.com | ok | yes | yes | yes | yes | 42 | 136 | 69% | match | USD | USD | US | 6 | no_ban | PASS |
| Schiit Audio | audio | www.schiit.com | ok | yes | yes | yes | no | - | - | - | - | - | - | - | 2 | - | fail: not shopify |
| Vibes | audio | discovervibes.com | ok | yes | yes | yes | no | - | - | - | - | - | - | - | 2 | - | fail: not shopify |
| Woo Audio | audio | wooaudio.com | ok | yes | yes | yes | no | - | - | - | - | - | - | - | 2 | - | fail: not shopify |
| Ami Colé | beauty | amicole.com | unreachable | - | - | no | no | - | - | - | - | - | - | - | 4 | - | fail: blocked |
| Bounce Curl | beauty | www.bouncecurl.com | ok | yes | yes | yes | yes | 53 | 97 | 91% | match | USD | USD | US | 6 | ban | PASS |
| Camille Rose | beauty | www.camillerose.com | ok | yes | yes | yes | yes | 95 | 96 | 65% | match | USD | USD | US | 6 | no_ban | PASS |
| Danessa Myricks Beauty | beauty | danessamyricksbeauty.com | ok | yes | yes | yes | yes | 57 | 693 | 73% | match | USD | USD | US | 6 | no_ban | PASS |
| Freck Beauty | beauty | freck.com | unreachable | - | - | no | no | - | - | - | - | - | - | - | 4 | - | fail: blocked |
| Hairstory | beauty | hairstory.com | ok | yes | yes | yes | yes | 171 | 173 | 100% | match | USD | USD | US | 6 | ban | PASS |
| Half Magic | beauty | halfmagicbeauty.com | ok | yes | yes | yes | yes | 66 | 169 | 84% | match | USD | USD | US | 6 | no_ban | PASS |
| Haus Labs | beauty | www.hauslabs.com | ok | yes | yes | yes | yes | 55 | 284 | 84% | match | USD | USD | US | 6 | ban | PASS |
| ILNP | beauty | www.ilnp.com | ok | yes | yes | yes | no | - | - | - | - | - | - | - | 2 | - | fail: not shopify |
| Kristin Ess | beauty | kristiness.com | unreachable | - | - | no | no | - | - | - | - | - | - | - | 4 | - | fail: blocked |
| Kulfi | beauty | kulfibeauty.com | ok | yes | yes | yes | yes | 33 | 103 | 99% | match | - | USD | US | 6 | ban | PASS |
| Live Tinted | beauty | www.livetinted.com | ok | yes | yes | yes | yes | 67 | 589 | 96% | match | - | USD | US | 6 | ban | PASS |
| Mooncat | beauty | www.mooncat.com | ok | yes | yes | yes | yes | 333 | 333 | 55% | match | USD | USD | US | 7 | ban | fail: excluded category: alcohol |
| Olaplex | beauty | olaplex.com | ok | yes | yes | yes | yes | 140 | 140 | 99% | match | USD | USD | US | 6 | ban | PASS |
| ONE/SIZE | beauty | www.onesizebeauty.com | ok | yes | yes | yes | yes | 61 | 338 | 86% | match | USD | USD | US | 6 | ban | PASS |
| R+Co | beauty | www.randco.com | ok | yes | yes | yes | yes | 235 | 241 | 97% | match | USD | USD | US | 6 | ban | PASS |
| Rizos Curls | beauty | rizoscurls.com | ok | yes | yes | yes | yes | 133 | 363 | 92% | match | USD | USD | US | 6 | ban | PASS |
| RMS Beauty | beauty | www.rmsbeauty.com | ok | yes | yes | yes | yes | 99 | 563 | 92% | match | USD | USD | US | 6 | ban | fail: excluded category: alcohol |
| Thrive Causemetics | beauty | thrivecausemetics.com | ok | yes | yes | yes | yes | 162 | 410 | 91% | match | USD | USD | US | 6 | ban | PASS |
| Vegamour | beauty | vegamour.com | ok | yes | yes | yes | yes | 59 | 188 | 93% | match | USD | USD | US | 6 | ban | PASS |
| Art of Tea | coffee_tea | www.artoftea.com | ok | yes | yes | yes | yes | 195 | 448 | 96% | match | USD | USD | US | 6 | ban | PASS |
| Black Oak Coffee | coffee_tea | blackoakcoffee.com | ok | yes | yes | yes | yes | 76 | 443 | 98% | match | USD | USD | US | 6 | ban | PASS |
| Brandywine Coffee Roasters | coffee_tea | brandywinecoffeeroasters.com | missing-4xx | yes | yes | yes | no | - | - | - | - | - | - | - | 2 | - | fail: not shopify |
| Cafe Grumpy | coffee_tea | cafegrumpy.com | ok | yes | yes | yes | no | - | - | - | - | - | - | - | 2 | - | fail: not shopify |
| Ceremony Coffee | coffee_tea | ceremonycoffee.com | ok | yes | yes | yes | yes | 86 | 254 | 84% | match | - | USD | US | 6 | ban | fail: excluded category: alcohol |
| Dayglow | coffee_tea | dayglow.coffee | ok | yes | yes | yes | yes | 116 | 152 | 84% | match | USD | USD | US | 6 | ban | PASS |
| Driftaway Coffee | coffee_tea | driftaway.coffee | ok | yes | yes | yes | no | - | - | - | - | - | - | - | 2 | - | fail: not shopify |
| Elixr Coffee | coffee_tea | elixrcoffee.com | ok | yes | yes | yes | yes | 17 | 41 | 90% | match | - | USD | US | 6 | none_found | PASS |
| Messenger Coffee | coffee_tea | messengercoffee.com | ok | yes | yes | yes | no | - | - | - | - | - | - | - | 2 | - | fail: not shopify |
| Mostra Coffee | coffee_tea | mostracoffee.com | ok | yes | yes | yes | yes | 75 | 346 | 31% | match | USD | USD | US | 6 | ban | PASS |
| Plum Deluxe | coffee_tea | www.plumdeluxe.com | ok | yes | yes | yes | yes | 263 | 342 | 72% | match | USD | USD | US | 7 | ban | fail: excluded category: alcohol |
| Prodigal | coffee_tea | getprodigal.com | ok | yes | yes | yes | yes | 60 | 121 | 68% | match | USD | USD | US | 6 | no_ban | PASS |
| Stereoscope Coffee | coffee_tea | stereoscope.coffee | unreachable | - | - | no | no | - | - | - | - | - | - | - | 4 | - | fail: blocked |
| Sweet Bloom Coffee | coffee_tea | sweetbloomcoffee.com | ok | yes | yes | yes | yes | 105 | 293 | 39% | match | USD | USD | US | 6 | no_ban | PASS |
| Tandem Coffee | coffee_tea | www.tandemcoffee.com | ok | yes | yes | yes | yes | - | - | - | match | USD | USD | US | 9 | - | fail: blocked mid-recon, empty catalog, needed 429 retries |
| Alphalete | fitness | alphaleteathletics.com | ok | yes | yes | no | no | - | - | - | - | - | - | - | 2 | - | fail: blocked |
| American Barbell | fitness | americanbarbell.com | ok | yes | yes | yes | yes | 156 | 425 | 73% | match | USD | USD | US | 6 | no_ban | PASS |
| Amphipod | fitness | amphipod.com | ok | yes | yes | yes | no | - | - | - | - | - | - | - | 2 | - | fail: not shopify |
| Assault Fitness | fitness | assaultfitness.com | ok | yes | yes | yes | yes | 9 | 9 | 67% | match | USD | USD | US | 6 | none_found | PASS |
| Barefoot Yoga Co. | fitness | barefootyoga.com | ok | yes | yes | yes | no | - | - | - | - | - | - | - | 2 | - | fail: not shopify |
| Born Primitive | fitness | bornprimitive.com | ok | yes | yes | yes | yes | 250 | 4014+ | 89% | match | USD | USD | US | 6 | ban | fail: catalog too large, excluded category: weapons |
| Buffbunny | fitness | www.buffbunny.com | ok | yes | yes | yes | yes | 500 | 4841+ | 72% | match | USD | USD | US | 7 | ban | fail: catalog too large, excluded category: alcohol |
| Darc Sport | fitness | shop.darcsport.com | ok | yes | yes | yes | yes | 242 | 1182 | 35% | match | USD | USD | US | 6 | no_ban | PASS |
| Dark Iron Fitness | fitness | darkironfitness.com | unreachable | - | - | no | no | - | - | - | - | - | - | - | 1 | - | fail: blocked |
| Element 26 | fitness | element26.co | ok | yes | yes | yes | yes | 35 | 209 | 72% | match | USD | USD | US | 6 | ban | PASS |
| Engage Pickleball | fitness | engagepickleball.com | ok | yes | yes | yes | yes | 172 | 1288 | 39% | match | USD | USD | US | 6 | ban | PASS |
| Get RX'd | fitness | getrxd.com | ok | yes | yes | yes | yes | 726 | 742 | 95% | match | USD | USD | US | 8 | no_ban | PASS |
| Harbinger | fitness | harbingerfitness.com | ok | yes | yes | yes | yes | 56 | 173 | 94% | match | USD | USD | US | 6 | ban | PASS |
| Horizon Fitness | fitness | www.horizonfitness.com | ok | yes | yes | yes | yes | 22 | 22 | 68% | match | USD | USD | US | 6 | ban | PASS |
| Hyperwear | fitness | hyperwear.com | ok | yes | yes | yes | yes | 66 | 346 | 88% | match | USD | USD | US | 6 | no_ban | PASS |
| Indo Board | fitness | indoboard.com | ok | no | no | no | no | - | - | - | - | - | - | - | 1 | - | fail: robots disallows |
| JadeYoga | fitness | jadeyoga.com | ok | yes | yes | yes | yes | 84 | 331 | 75% | match | USD | USD | US | 6 | ban | PASS |
| Jolyn | fitness | jolyn.com | ok | yes | yes | yes | yes | 750 | 3718+ | 82% | match | - | USD | US | 8 | ban | fail: catalog too large |
| JOOLA | fitness | joola.com | ok | yes | yes | yes | yes | 415 | 2216 | 42% | match | USD | USD | US | 6 | none_found | PASS |
| LifePro | fitness | lifeprofitness.com | ok | yes | yes | no | no | - | - | - | - | - | - | - | 2 | - | fail: blocked |
| Mark Bell Slingshot | fitness | markbellslingshot.com | ok | yes | yes | yes | yes | 84 | 565 | 95% | match | USD | USD | US | 6 | ban | PASS |
| NVGTN | fitness | nvgtn.com | ok | yes | yes | no | no | - | - | - | - | - | - | - | 2 | - | fail: blocked |
| Oiselle | fitness | www.oiselle.com | ok | yes | yes | yes | yes | 93 | 1925 | 60% | match | USD | USD | US | 6 | ban | PASS |
| Paddletek | fitness | www.paddletek.com | ok | yes | yes | yes | yes | 77 | 578 | 77% | match | USD | USD | US | 5 | none_found | PASS |
| Path Projects | fitness | pathprojects.com | ok | yes | yes | yes | yes | 80 | 1242 | 60% | match | USD | USD | US | 6 | ban | PASS |
| Raskol Apparel | fitness | raskolapparel.com | ok | yes | yes | yes | yes | 381 | 2632 | 78% | match | USD | USD | CA | 7 | ban | PASS |
| Revolution Balance Boards | fitness | revbalance.com | ok | no | no | no | no | - | - | - | - | - | - | - | 1 | - | fail: robots disallows |
| Rip Toned | fitness | riptoned.com | ok | yes | yes | yes | yes | 47 | 243 | 72% | match | USD | USD | US | 6 | ban | PASS |
| Roll Recovery | fitness | rollrecovery.com | ok | yes | yes | yes | yes | 21 | 167 | 78% | match | USD | USD | US | 6 | ban | PASS |
| RumbleRoller | fitness | www.rumbleroller.com | ok | yes | yes | yes | yes | 19 | 35 | 97% | match | USD | USD | US | 6 | ban | PASS |
| RX Smart Gear | fitness | rxsmartgear.com | ok | yes | yes | yes | yes | 118 | 2717 | 97% | match | USD | USD | US | 6 | ban | PASS |
| Schiek Sports | fitness | schiek.com | ok | yes | yes | yes | yes | 113 | 1362 | 98% | match | USD | USD | US | 6 | ban | PASS |
| Senita Athletics | fitness | www.senitaathletics.com | ok | yes | yes | yes | yes | 249 | 1595 | 82% | match | USD | USD | US | 6 | ban | fail: excluded category: weapons |
| SKLZ | fitness | sklz.com | ok | yes | yes | yes | yes | 198 | 227 | 92% | match | USD | USD | US | 6 | ban | PASS |
| Stamina Products | fitness | staminaproducts.com | ok | yes | yes | yes | yes | 304 | 317 | 94% | match | USD | USD | US | 7 | no_ban | PASS |
| Swiftwick | fitness | swiftwick.com | ok | yes | yes | yes | yes | 222 | 9445 | 89% | match | - | USD | US | 6 | ban | fail: catalog too large |
| Synergee | fitness | synergeefitness.com | ok | yes | yes | yes | yes | 98 | 372 | 80% | match | USD | USD | US | 6 | ban | PASS |
| tasc Performance | fitness | www.tascperformance.com | ok | yes | yes | yes | yes | 500 | 3870+ | 79% | match | USD | USD | US | 7 | ban | fail: catalog too large |
| Titan Fitness | fitness | titan.fitness | ok | yes | yes | yes | yes | 1750 | 3004+ | 60% | match | USD | USD | US | 12 | ban | fail: catalog too large |
| TYR | fitness | tyr.com | ok | yes | yes | yes | yes | 500 | 3663+ | 68% | match | USD | USD | US | 7 | ban | fail: catalog too large |
| Vatic Pro | fitness | vaticpro.com | ok | yes | yes | yes | yes | 8 | 47 | 85% | match | USD | USD | US | 6 | no_ban | PASS |
| Victory Grips | fitness | victorygrips.com | ok | yes | yes | yes | yes | 45 | 193 | 80% | match | USD | USD | US | 6 | ban | PASS |
| Vooray | fitness | www.vooray.com | ok | yes | yes | yes | yes | 127 | 133 | 84% | match | USD | USD | US | 6 | ban | PASS |
| Vulcan Strength | fitness | vulcanstrength.com | ok | yes | yes | yes | no | - | - | - | - | - | - | - | 2 | - | fail: not shopify |
| YoungLA | fitness | www.youngla.com | ok | yes | yes | yes | yes | 250 | 4968+ | 66% | match | USD | USD | US | 6 | ban | fail: catalog too large |
| Albany Park | home_kitchen | www.albanypark.com | ok | yes | yes | yes | yes | 155 | 1925 | 100% | match | - | USD | US | 6 | no_ban | PASS |
| Bentgo | home_kitchen | bentgo.com | ok | yes | yes | yes | yes | 161 | 741 | 91% | match | USD | USD | US | 6 | ban | PASS |
| Better Life | home_kitchen | cleanhappy.com | missing-4xx | yes | yes | yes | no | - | - | - | - | - | - | - | 2 | - | fail: not shopify |
| Butter Pat Industries | home_kitchen | butterpatindustries.com | missing-4xx | yes | yes | yes | no | - | - | - | - | - | - | - | 2 | - | fail: not shopify |
| Earth Breeze | home_kitchen | earthbreeze.com | ok | yes | yes | yes | yes | 53 | 308 | 98% | match | USD | USD | US | 6 | ban | PASS |
| FINEX | home_kitchen | www.finexusa.com | ok | yes | yes | yes | yes | 24 | 38 | 90% | match | - | USD | US | 6 | ban | PASS |
| Hygge & West | home_kitchen | www.hyggeandwest.com | ok | yes | yes | yes | yes | 127 | 772 | 98% | match | USD | USD | US | 6 | ban | PASS |
| Klean Kanteen | home_kitchen | www.kleankanteen.com | ok | yes | yes | yes | yes | 146 | 1182 | 77% | match | USD | USD | US | 6 | no_ban | fail: excluded category: alcohol |
| LARQ | home_kitchen | www.livelarq.com | ok | yes | yes | yes | no | - | - | - | - | - | - | - | 2 | - | fail: not shopify |
| Lulu and Georgia | home_kitchen | www.luluandgeorgia.com | ok | yes | yes | yes | yes | 500 | 4510+ | 96% | match | USD | USD | US | 7 | ban | fail: catalog too large, excluded category: alcohol, tobacco/vape |
| Marquette Castings | home_kitchen | www.marquettecastings.com | ok | yes | yes | yes | yes | 0 | 0 | - | - | - | - | US | 4 | ban | fail: empty catalog, currency not proven USD, product .js unavailable |
| NEST New York | home_kitchen | www.nestnewyork.com | ok | yes | yes | yes | yes | 402 | 407 | 99% | match | USD | USD | US | 7 | no_ban | fail: excluded category: alcohol |
| PlanetBox | home_kitchen | www.planetbox.com | ok | yes | yes | yes | yes | 73 | 289 | 91% | match | USD | USD | US | 6 | ban | PASS |
| Puracy | home_kitchen | puracy.com | ok | yes | yes | yes | yes | 39 | 144 | 62% | match | USD | USD | US | 6 | no_ban | PASS |
| Sabai | home_kitchen | sabai.design | ok | yes | yes | yes | yes | 250 | 5034+ | 100% | match | USD | USD | US | 6 | ban | fail: catalog too large |
| Simple Modern | home_kitchen | www.simplemodern.com | ok | yes | yes | yes | yes | 1838 | 1838 | 66% | match | USD | USD | US | 13 | ban | fail: excluded category: alcohol |
| Sixpenny | home_kitchen | sixpenny.com | ok | yes | yes | yes | yes | 250 | 9645+ | 100% | match | USD | USD | US | 6 | ban | fail: catalog too large |
| Stargazer Cast Iron | home_kitchen | stargazercastiron.com | ok | yes | yes | yes | yes | 12 | 46 | 87% | match | USD | USD | US | 6 | ban | PASS |
| Sunday Citizen | home_kitchen | sundaycitizen.co | ok | yes | yes | yes | yes | 432 | 2008 | 70% | match | USD | USD | US | 7 | ban | PASS |
| Takeya | home_kitchen | takeyausa.com | ok | yes | yes | yes | yes | 1037 | 1336 | 93% | match | USD | USD | US | 10 | no_ban | PASS |
| Arbor Collective | outdoor | www.arborcollective.com | ok | yes | yes | yes | yes | 712 | 2285 | 37% | match | USD | USD | US | 11 | ban | fail: excluded category: alcohol, needed 429 retries |
| Bedrock Bags | outdoor | bedrockbags.com | ok | yes | yes | yes | no | - | - | - | - | - | - | - | 2 | - | fail: not shopify |
| BOTE | outdoor | www.boteboard.com | ok | yes | yes | yes | yes | 181 | 295 | 72% | match | USD | USD | US | 6 | ban | PASS |
| Catch Surf | outdoor | catchsurf.com | ok | yes | yes | yes | yes | 224 | 750 | 57% | match | USD | USD | US | 6 | ban | PASS |
| Crazy Creek | outdoor | crazycreek.com | ok | yes | yes | yes | yes | 35 | 138 | 68% | match | USD | USD | US | 6 | ban | PASS |
| Durston Gear | outdoor | durstongear.com | ok | yes | yes | yes | yes | 45 | 190 | 55% | match | USD | USD | CA | 6 | ban | PASS |
| Evolv | outdoor | www.evolvsports.com | ok | yes | yes | yes | no | - | - | - | - | - | - | - | 2 | - | fail: not shopify |
| Fishpond | outdoor | fishpondusa.com | ok | yes | yes | yes | yes | 347 | 481 | 81% | match | USD | USD | US | 7 | ban | fail: excluded category: cannabis/cbd, tobacco/vape, weapons |
| Hammock Gear | outdoor | hammockgear.com | ok | yes | yes | no | no | - | - | - | - | - | - | - | 2 | - | fail: blocked |
| Icelantic | outdoor | www.icelanticskis.com | ok | yes | yes | yes | yes | - | - | - | match | USD | USD | US | 10 | - | fail: blocked mid-recon, empty catalog, needed 429 retries |
| ICEMULE | outdoor | icemule.com | ok | yes | yes | yes | yes | 14 | 137 | 95% | match | USD | USD | US | 6 | ban | PASS |
| Kahtoola | outdoor | kahtoola.com | ok | yes | yes | no | no | - | - | - | - | - | - | - | 2 | - | fail: blocked |
| Moment Skis | outdoor | www.momentskis.com | ok | yes | yes | yes | yes | 159 | 628 | 64% | match | USD | USD | US | 6 | ban | PASS |
| Outdoor Vitals | outdoor | outdoorvitals.com | ok | yes | yes | yes | yes | 223 | 1757 | 84% | match | USD | USD | US | 6 | ban | PASS |
| Pa'lante Packs | outdoor | palantepacks.com | ok | yes | yes | yes | yes | 36 | 220 | 67% | match | - | USD | US | 6 | none_found | PASS |
| RovR Products | outdoor | rovrproducts.com | ok | yes | yes | yes | yes | 87 | 138 | 73% | match | USD | USD | US | 6 | ban | PASS |
| Sunday Afternoons | outdoor | www.sundayafternoons.com | ok | yes | yes | yes | yes | 139 | 604 | 94% | match | USD | USD | US | 6 | ban | PASS |
| Tarptent | outdoor | tarptent.com | unreachable | - | - | no | no | - | - | - | - | - | - | - | 1 | - | fail: blocked |
| Tower Paddle Boards | outdoor | www.towerpaddleboards.com | ok | yes | yes | yes | yes | 70 | 87 | 69% | match | - | USD | US | 6 | no_ban | PASS |
| Warbonnet Outdoors | outdoor | warbonnetoutdoors.com | ok | yes | yes | no | no | - | - | - | - | - | - | - | 2 | - | fail: blocked |
| Boxiecat | pet | boxiecat.com | ok | yes | yes | yes | yes | 14 | 30 | 53% | match | USD | USD | US | 6 | no_ban | PASS |
| Cycle Dog | pet | cycledog.com | ok | yes | yes | no | no | - | - | - | - | - | - | - | 2 | - | fail: blocked |
| Earth Animal | pet | earthanimal.com | ok | yes | yes | yes | yes | 78 | 173 | 96% | match | USD | USD | US | 6 | ban | PASS |
| Earthbath | pet | earthbath.com | ok | yes | yes | yes | yes | 98 | 280 | 100% | match | USD | USD | US | 6 | no_ban | PASS |
| Finn | pet | petfinn.com | ok | yes | yes | yes | yes | 39 | 42 | 81% | match | USD | USD | US | 6 | ban | PASS |
| Furhaven | pet | furhaven.com | ok | yes | yes | yes | no | - | - | - | - | - | - | - | 2 | - | fail: not shopify |
| Jinx | pet | www.jinx.com | ok | yes | yes | no | no | - | - | - | - | - | - | - | 2 | - | fail: blocked |
| Jones Natural Chews | pet | jonesnaturalchews.com | ok | yes | yes | yes | yes | 96 | 100 | 99% | match | - | USD | US | 6 | none_found | PASS |
| Kurgo | pet | www.kurgo.com | ok | yes | yes | yes | no | - | - | - | - | - | - | - | 2 | - | fail: not shopify |
| Lupine Pet | pet | www.lupinepet.com | ok | yes | yes | yes | yes | 250 | 8264+ | 100% | match | USD | USD | US | 6 | ban | fail: catalog too large |
| Ollydog | pet | ollydog.com | ok | yes | yes | yes | yes | 34 | 249 | 95% | match | USD | USD | US | 6 | ban | PASS |
| Pawstruck | pet | www.pawstruck.com | ok | yes | yes | yes | yes | 51 | 190 | 96% | match | - | USD | US | 6 | no_ban | PASS |
| PetHonesty | pet | www.pethonesty.com | ok | yes | yes | yes | yes | 184 | 184 | 93% | match | USD | USD | US | 6 | ban | fail: excluded category: cannabis/cbd |
| Snoozer | pet | snoozerpetproducts.com | ok | yes | yes | yes | no | - | - | - | - | - | - | - | 2 | - | fail: not shopify |
| Sundays for Dogs | pet | sundaysfordogs.com | ok | yes | yes | yes | no | - | - | - | - | - | - | - | 2 | - | fail: not shopify |
| Tuft + Paw | pet | www.tuftandpaw.com | ok | yes | yes | yes | yes | 15 | 40 | 90% | match | USD | USD | US | 6 | ban | PASS |
| Up Country | pet | upcountryinc.com | ok | yes | yes | yes | yes | 1000 | 3144+ | 100% | match | USD | USD | US | 9 | ban | fail: catalog too large, excluded category: alcohol |
| Vetnique Labs | pet | vetnique.com | ok | yes | yes | yes | yes | 40 | 105 | 100% | match | USD | USD | US | 6 | ban | PASS |
| Warren London | pet | www.warrenlondon.com | ok | yes | yes | yes | yes | 132 | 229 | 100% | match | USD | USD | US | 6 | ban | PASS |
| Wild Earth | pet | wildearth.com | ok | yes | yes | yes | yes | 7 | 19 | 79% | match | USD | USD | US | 6 | ban | PASS |
| Archer Watch Straps | tech_accessories | www.archerwatchstraps.com | ok | yes | yes | yes | yes | 244 | 846 | 94% | match | USD | USD | US | 7 | ban | PASS |
| Azio | tech_accessories | www.aziocorp.com | ok | yes | yes | yes | yes | 87 | 327 | 65% | match | USD | USD | US | 6 | no_ban | PASS |
| Barton Watch Bands | tech_accessories | www.bartonwatchbands.com | ok | yes | yes | yes | yes | - | - | - | match | USD | USD | US | 10 | - | fail: blocked mid-recon, empty catalog, needed 429 retries |
| Beastgrip | tech_accessories | beastgrip.com | ok | yes | yes | yes | yes | 99 | 119 | 82% | match | USD | USD | US | 6 | ban | PASS |
| BLUETTI | tech_accessories | www.bluettipower.com | ok | yes | yes | yes | yes | 437 | 627 | 48% | match | USD | USD | US | 7 | ban | fail: excluded category: tobacco/vape |
| Boardsource | tech_accessories | boardsource.xyz | ok | yes | yes | yes | yes | 58 | 124 | 68% | match | USD | USD | US | 6 | ban | PASS |
| BodyGuardz | tech_accessories | www.bodyguardz.com | ok | yes | yes | yes | yes | - | - | - | match | USD | USD | US | 11 | - | fail: blocked mid-recon, empty catalog, needed 429 retries |
| Branch Furniture | tech_accessories | www.branchfurniture.com | ok | yes | yes | yes | yes | 226 | 4872 | 93% | match | USD | USD | US | 5 | none_found | fail: catalog too large |
| Breakthrough Photography | tech_accessories | breakthrough.photography | ok | yes | yes | yes | yes | 57 | 1341 | 81% | match | USD | USD | US | 6 | ban | PASS |
| Brevite | tech_accessories | brevite.co | ok | yes | yes | yes | yes | 34 | 220 | 72% | match | USD | USD | US | 6 | ban | PASS |
| Cable Matters | tech_accessories | www.cablematters.com | ok | no | no | no | no | - | - | - | - | - | - | - | 1 | - | fail: robots disallows |
| Cerakey | tech_accessories | www.cerakey.com | ok | yes | yes | yes | yes | 68 | 816 | 45% | match | USD | USD | HK | 6 | ban | PASS |
| Clockwork Synergy | tech_accessories | clockworksynergy.com | ok | yes | yes | no | no | - | - | - | - | - | - | - | 2 | - | fail: unreachable |
| Dang Keebs | tech_accessories | dangkeebs.com | ok | yes | yes | yes | yes | 174 | 826 | 45% | match | USD | USD | US | 6 | ban | PASS |
| DODOcase | tech_accessories | dodocase.com | ok | yes | yes | yes | yes | 59 | 2031 | 99% | match | USD | USD | US | 6 | ban | PASS |
| EcoFlow (US) | tech_accessories | us.ecoflow.com | ok | yes | yes | yes | yes | 318 | 980 | 50% | match | - | USD | US | 7 | ban | fail: excluded category: tobacco/vape |
| Encased | tech_accessories | encased.com | ok | yes | yes | no | no | - | - | - | - | - | - | - | 2 | - | fail: blocked |
| Fuse Chicken | tech_accessories | fusechicken.com | ok | no | no | no | no | - | - | - | - | - | - | - | 1 | - | fail: robots disallows |
| Gordy's Camera Straps | tech_accessories | gordyscamerastraps.com | ok | yes | yes | yes | yes | 50 | 190 | 100% | match | - | USD | US | 6 | ban | PASS |
| Govee (US) | tech_accessories | us.govee.com | ok | yes | yes | yes | no | - | - | - | - | - | - | - | 2 | - | fail: not shopify |
| Higround | tech_accessories | higround.co | ok | yes | yes | yes | yes | 342 | 446 | 24% | match | USD | USD | US | 7 | ban | PASS |
| Holdfast Gear | tech_accessories | holdfastgear.com | ok | yes | yes | yes | yes | 163 | 2727 | 97% | match | USD | USD | US | 6 | ban | fail: excluded category: weapons |
| Hyperkin | tech_accessories | wholesale.hyperkin.com | ok | no | no | no | no | - | - | - | - | - | - | - | 1 | - | fail: robots disallows |
| iOttie | tech_accessories | www.iottie.com | ok | yes | yes | yes | no | - | - | - | - | - | - | - | 2 | - | fail: not shopify |
| Jackery | tech_accessories | www.jackery.com | ok | yes | yes | yes | yes | 177 | 498 | 45% | match | USD | USD | US | 6 | ban | PASS |
| Juuk Design | tech_accessories | juukdesign.com | ok | yes | yes | yes | yes | 18 | 114 | 92% | match | USD | USD | HK | 6 | no_ban | PASS |
| Keebio | tech_accessories | keeb.io | ok | yes | yes | no | no | - | - | - | - | - | - | - | 2 | - | fail: blocked |
| KeebsForAll | tech_accessories | keebsforall.com | ok | yes | yes | yes | yes | 452 | 2263 | 27% | match | USD | USD | US | 7 | ban | fail: excluded category: alcohol, weapons |
| Kenu | tech_accessories | www.kenu.com | ok | yes | yes | yes | yes | 33 | 46 | 67% | match | USD | USD | US | 6 | ban | PASS |
| Langly | tech_accessories | www.langly.co | ok | yes | yes | yes | yes | 22 | 119 | 85% | match | USD | USD | US | 6 | ban | PASS |
| LapGear | tech_accessories | lapgear.com | missing-4xx | yes | yes | yes | no | - | - | - | - | - | - | - | 2 | - | fail: not shopify |
| Mechcables | tech_accessories | mechcables.com | ok | yes | yes | yes | yes | 124 | 163 | 99% | match | - | USD | US | 6 | ban | PASS |
| Milktooth | tech_accessories | milktooth.com | ok | yes | yes | yes | no | - | - | - | - | - | - | - | 2 | - | fail: not shopify |
| Mobile Pixels | tech_accessories | www.mobilepixels.us | ok | yes | yes | yes | yes | 67 | 79 | 72% | match | USD | USD | US | 6 | ban | PASS |
| Monowear | tech_accessories | monowear.com | unreachable | - | - | no | no | - | - | - | - | - | - | - | 4 | - | fail: blocked |
| Omnitype | tech_accessories | omnitype.com | ok | yes | yes | yes | yes | 186 | 773 | 37% | match | USD | USD | US | 6 | ban | PASS |
| Pad & Quill | tech_accessories | padandquill.com | missing-4xx | yes | yes | yes | no | - | - | - | - | - | - | - | 2 | - | fail: not shopify |
| Pebblebee | tech_accessories | pebblebee.com | ok | yes | yes | yes | yes | 19 | 61 | 57% | match | USD | USD | US | 6 | no_ban | PASS |
| Poetic | tech_accessories | www.poeticcases.com | ok | yes | yes | yes | yes | 684 | 2139 | 46% | match | USD | USD | US | 11 | ban | fail: needed 429 retries |
| Quad Lock (US) | tech_accessories | www.quadlockcase.com | ok | yes | yes | yes | yes | 255 | 1009 | 100% | match | USD | USD | US | 7 | ban | PASS |
| Rain Design | tech_accessories | raindesigninc.com | ok | yes | yes | yes | yes | 16 | 109 | 92% | match | USD | USD | US | 6 | no_ban | PASS |
| Roost | tech_accessories | therooststand.com | unreachable | - | - | no | no | - | - | - | - | - | - | - | 4 | - | fail: blocked |
| Speck | tech_accessories | speckproducts.com | ok | yes | yes | yes | yes | 1199 | 2092 | 63% | match | USD | USD | US | 10 | ban | PASS |
| Spigen | tech_accessories | www.spigen.com | ok | yes | yes | yes | yes | - | - | - | match | USD | USD | US | 11 | - | fail: blocked mid-recon, empty catalog, needed 429 retries |
| SUPCASE | tech_accessories | supcase.com | ok | yes | yes | yes | yes | 1247 | 1619 | 97% | match | - | USD | US | 10 | ban | fail: excluded category: alcohol, weapons |
| ThocStock | tech_accessories | thocstock.com | ok | yes | yes | yes | no | - | - | - | - | - | - | - | 2 | - | fail: not shopify |
| Upgrade Keyboards | tech_accessories | upgradekeyboards.com | ok | yes | yes | yes | yes | 449 | 782 | 58% | match | - | USD | US | 7 | ban | PASS |
| Wyze | tech_accessories | www.wyze.com | ok | yes | yes | yes | yes | 201 | 418 | 53% | match | USD | USD | US | 6 | ban | PASS |
| Zack Cables | tech_accessories | zackcables.com | unreachable | - | - | no | no | - | - | - | - | - | - | - | 4 | - | fail: blocked |
| Zugu Case | tech_accessories | zugu.com | ok | yes | yes | yes | yes | 32 | 203 | 94% | match | USD | USD | US | 6 | ban | PASS |
| aden + anais | toys_kids | adenandanais.com | missing-4xx | yes | yes | no | no | - | - | - | - | - | - | - | 2 | - | fail: blocked |
| Art of Play | toys_kids | www.artofplay.com | ok | yes | yes | yes | yes | - | - | - | match | USD | USD | US | 10 | - | fail: blocked mid-recon, empty catalog, needed 429 retries |
| Bananagrams | toys_kids | bananagrams.com | ok | yes | yes | yes | no | - | - | - | - | - | - | - | 2 | - | fail: not shopify |
| Barefoot Books | toys_kids | www.barefootbooks.com | ok | no | no | no | no | - | - | - | - | - | - | - | 1 | - | fail: robots disallows |
| Begin Again Toys | toys_kids | beginagaintoys.com | ok | yes | yes | yes | no | - | - | - | - | - | - | - | 2 | - | fail: not shopify |
| Bella Tunno | toys_kids | bellatunno.com | ok | yes | yes | yes | yes | 201 | 205 | 92% | match | USD | USD | US | 6 | ban | PASS |
| Bowfish Kids | toys_kids | www.bowfishkids.com | ok | yes | yes | yes | yes | - | - | - | match | USD | USD | US | 9 | - | fail: blocked mid-recon, empty catalog, needed 429 retries |
| Bowy Made | toys_kids | bowymade.com | ok | yes | yes | yes | yes | 172 | 471 | 90% | match | USD | USD | AU | 7 | ban | PASS |
| Bunnies By The Bay | toys_kids | bunniesbythebay.com | ok | yes | yes | yes | yes | 1695 | 1892 | 22% | match | USD | USD | US | 12 | ban | PASS |
| Burt's Bees Baby | toys_kids | burtsbeesbaby.com | ok | yes | yes | yes | yes | 500 | 3377+ | 45% | match | USD | USD | US | 7 | ban | fail: catalog too large |
| Cabbage Patch Kids | toys_kids | cabbagepatchkids.com | ok | yes | yes | yes | yes | 1335 | 1335 | 41% | match | USD | USD | US | 11 | ban | PASS |
| California Baby | toys_kids | californiababy.com | ok | yes | yes | yes | yes | 241 | 385 | 94% | match | USD | USD | US | 6 | ban | PASS |
| Clixo | toys_kids | clixo.com | ok | yes | yes | yes | yes | 36 | 53 | 91% | match | USD | USD | US | 6 | no_ban | PASS |
| Dreamland Baby | toys_kids | dreamlandbabyco.com | ok | yes | yes | no | no | - | - | - | - | - | - | - | 2 | - | fail: blocked |
| Emerson and Friends | toys_kids | emersonandfriends.com | ok | yes | yes | yes | yes | 1161 | 3064 | 89% | match | USD | USD | US | 10 | ban | fail: catalog too large, excluded category: alcohol, tobacco/vape |
| Foamnasium | toys_kids | foamnasium.com | ok | yes | yes | yes | yes | 59 | 344 | 100% | match | USD | USD | US | 6 | none_found | PASS |
| Free Birdees | toys_kids | freebirdees.com | ok | no | no | no | no | - | - | - | - | - | - | - | 1 | - | fail: robots disallows |
| Gamewright | toys_kids | gamewright.com | ok | yes | yes | yes | no | - | - | - | - | - | - | - | 2 | - | fail: not shopify |
| Goumi Kids | toys_kids | goumikids.com | ok | yes | yes | yes | yes | 106 | 365 | 73% | match | USD | USD | US | 6 | ban | PASS |
| Green Toys | toys_kids | www.greentoys.com | ok | yes | yes | yes | yes | 54 | 69 | 0% | match | USD | USD | US | 6 | ban | PASS |
| Hart + Land | toys_kids | hartandland.com | unreachable | - | - | no | no | - | - | - | - | - | - | - | 4 | - | fail: blocked |
| Healthy Roots Dolls | toys_kids | healthyrootsdolls.com | ok | yes | yes | yes | yes | 14 | 20 | 90% | match | USD | USD | US | 6 | ban | PASS |
| Kozi & Co | toys_kids | kozikidsco.com | unreachable | - | - | no | no | - | - | - | - | - | - | - | 4 | - | fail: blocked |
| Lily & River | toys_kids | www.deartot.com | ok | yes | yes | yes | yes | 117 | 280 | 92% | match | USD | USD | US | 6 | ban | PASS |
| Little Partners | toys_kids | littlepartners.com | ok | yes | yes | yes | yes | 314 | 1049 | 94% | match | USD | USD | US | 6 | none_found | PASS |
| Little Unicorn | toys_kids | littleunicorn.com | ok | yes | yes | yes | yes | 779 | 935 | 92% | match | USD | USD | US | 9 | ban | PASS |
| Lou Lou & Company | toys_kids | louloucompany.com | unreachable | - | - | no | no | - | - | - | - | - | - | - | 4 | - | fail: blocked |
| Magformers | toys_kids | magformers.com | ok | yes | yes | no | no | - | - | - | - | - | - | - | 2 | - | fail: blocked |
| Micro Kickboard | toys_kids | microkickboard.com | ok | yes | yes | yes | yes | 247 | 743 | 68% | match | USD | USD | US | 6 | ban | PASS |
| Milk Snob | toys_kids | milksnob.com | ok | yes | yes | yes | yes | 270 | 456 | 94% | match | USD | USD | US | 7 | ban | PASS |
| Mockingbird | toys_kids | hellomockingbird.com | ok | yes | yes | yes | yes | 60 | 232 | 97% | match | USD | USD | US | 6 | no_ban | PASS |
| Mushie | toys_kids | mushie.com | ok | yes | yes | yes | yes | 216 | 1288 | 94% | match | USD | USD | US | 6 | ban | PASS |
| Oeuf | toys_kids | oeufnyc.com | ok | yes | yes | yes | yes | 204 | 243 | 90% | match | USD | USD | US | 6 | ban | PASS |
| Olababy | toys_kids | olababy.com | ok | yes | yes | yes | no | - | - | - | - | - | - | - | 2 | - | fail: not shopify |
| pediped | toys_kids | www.pediped.com | ok | yes | yes | yes | yes | 322 | 2707 | 80% | match | USD | USD | US | 7 | ban | PASS |
| Prevelo Bikes | toys_kids | prevelo.com | ok | yes | yes | yes | yes | 96 | 360 | 68% | match | USD | USD | US | 6 | ban | PASS |
| See Kai Run | toys_kids | seekairun.com | ok | yes | yes | yes | no | - | - | - | - | - | - | - | 2 | - | fail: not shopify |
| Snuggle Me Organic | toys_kids | snugglemeorganic.com | ok | yes | yes | yes | yes | 141 | 145 | 79% | match | USD | USD | US | 5 | none_found | PASS |
| Spearmint Love | toys_kids | spearmintlove.com | ok | yes | yes | yes | yes | 1000 | 4028+ | 71% | match | USD | USD | US | 9 | ban | fail: catalog too large |
| Speks | toys_kids | speks.com | unreachable | - | - | no | no | - | - | - | - | - | - | - | 4 | - | fail: blocked |
| Sphero | toys_kids | sphero.com | ok | yes | yes | yes | yes | 263 | 353 | 100% | match | USD | USD | US | 7 | none_found | PASS |
| Sprout Kids | toys_kids | sproutkids.com | unreachable | - | - | no | no | - | - | - | - | - | - | - | 4 | - | fail: blocked |
| Strictly Briks | toys_kids | strictlybriks.com | ok | no | no | no | no | - | - | - | - | - | - | - | 1 | - | fail: robots disallows |
| Strider Bikes | toys_kids | striderbikes.com | ok | yes | yes | yes | no | - | - | - | - | - | - | - | 2 | - | fail: not shopify |
| Tea Collection | toys_kids | teacollection.com | ok | yes | yes | yes | yes | 250 | 6595+ | 52% | match | USD | USD | US | 6 | ban | fail: catalog too large |
| The Pencil Grip | toys_kids | www.tpgcreations.com | ok | yes | yes | yes | yes | 209 | 346 | 98% | match | USD | USD | US | 6 | ban | PASS |
| The Woobles | toys_kids | thewoobles.com | ok | yes | yes | yes | yes | 659 | 708 | 84% | match | - | USD | US | 8 | ban | PASS |
| Tiny Twinkle | toys_kids | tinytwinkle.com | ok | yes | yes | yes | yes | 50 | 532 | 78% | match | USD | USD | US | 6 | ban | PASS |
| Tushbaby | toys_kids | tushbaby.com | ok | yes | yes | yes | yes | 66 | 714 | 70% | match | USD | USD | US | 6 | ban | PASS |
| WeeSprout | toys_kids | www.weesprout.com | ok | yes | yes | yes | yes | 54 | 196 | 85% | match | USD | USD | US | 6 | ban | PASS |
| Wonder Crew | toys_kids | wondercrew.com | unreachable | - | - | no | no | - | - | - | - | - | - | - | 4 | - | fail: blocked |
| Wonderfold | toys_kids | wonderfold.com | ok | yes | yes | yes | yes | 212 | 916 | 64% | match | USD | USD | US | 6 | ban | PASS |
| Woolino | toys_kids | www.woolino.com | ok | yes | yes | yes | yes | 392 | 890 | 54% | match | USD | USD | US | 7 | ban | PASS |
| Zipadee-Zip (Sleeping Baby) | toys_kids | sleepingbaby.com | missing-4xx | yes | yes | yes | no | - | - | - | - | - | - | - | 2 | - | fail: not shopify |
| Zoe Organics | toys_kids | zoeorganics.com | ok | yes | yes | yes | no | - | - | - | - | - | - | - | 2 | - | fail: not shopify |

## Notes

- **aden + anais**: stopped: blocked: http 403
- **Albany Park**: no JSON-LD offer currency on product page
- **Alex Mill**: stopped: retries exhausted: http 429; no JSON-LD offer currency on product page
- **Alphalete**: stopped: blocked: cloudflare challenge
- **Ami Colé**: stopped: robots.txt unreachable: retries exhausted: network error: ConnectError
- **Amphipod**: /products.json: http 404, text/html; charset=UTF-8
- **Art of Play**: stopped: retries exhausted: http 429
- **Aviator Nation**: stopped: retries exhausted: http 429
- **Bananagrams**: /products.json: http 200, text/html; charset=utf-8
- **Barefoot Yoga Co.**: /products.json: http 404, text/html; charset=UTF-8
- **Barton Watch Bands**: stopped: retries exhausted: http 429
- **Bedrock Bags**: /products.json: http 404, text/html;charset=utf-8
- **Begin Again Toys**: /products.json: http 200, text/html; charset=utf-8
- **Better Life**: /products.json: http 404, text/html
- **BodyGuardz**: stopped: retries exhausted: http 429
- **Bowfish Kids**: stopped: retries exhausted: http 429
- **Brandywine Coffee Roasters**: /products.json: http 404, ?
- **Brixton**: stopped: retries exhausted: http 429
- **Butter Pat Industries**: /products.json: http 404, ?
- **C. Crane**: /products.json: http 404, text/html; charset=UTF-8
- **Cafe Grumpy**: /products.json: http 404, text/html; charset=UTF-8
- **Ceremony Coffee**: no JSON-LD offer currency on product page
- **Clockwork Synergy**: error: TooManyRedirects: Exceeded maximum allowed redirects.
- **Cuup**: /products.json: http 410, text/html;charset=UTF-8
- **Cycle Dog**: stopped: blocked: cloudflare challenge
- **Dark Iron Fitness**: stopped: blocked: siteground captcha (robots.txt)
- **Dreamland Baby**: stopped: blocked: cloudflare challenge
- **Driftaway Coffee**: /products.json: http 404, text/html; charset=UTF-8
- **Dudley Stephens**: /products.json: http 404, ?
- **Earthworks Audio**: stopped: blocked: siteground captcha
- **EcoFlow (US)**: no JSON-LD offer currency on product page
- **Elixr Coffee**: no JSON-LD offer currency on product page
- **Encased**: stopped: blocked: http 403
- **Evolv**: /products.json: http 404, application/json
- **FINEX**: no JSON-LD offer currency on product page
- **Freck Beauty**: stopped: robots.txt unreachable: retries exhausted: network error: ConnectError
- **Furhaven**: /products.json: http 404, text/html
- **Gamewright**: /products.json: http 404, text/html; charset=UTF-8
- **Gordy's Camera Straps**: no JSON-LD offer currency on product page
- **Govee (US)**: /products.json: http 200, text/html
- **Hackwith Design House**: /products.json: http 404, text/html; charset=UTF-8
- **Hammock Gear**: stopped: blocked: http 403
- **Hart + Land**: stopped: robots.txt unreachable: retries exhausted: network error: ConnectError
- **HeadAmp**: stopped: retries exhausted: http 429
- **Hill House Home**: stopped: retries exhausted: http 429; no JSON-LD offer currency on product page
- **Icelantic**: stopped: retries exhausted: http 429
- **ILNP**: /products.json: http 404, text/html; charset=UTF-8
- **iOttie**: /products.json: http 404, text/html; charset=UTF-8
- **Iron & Resin**: no JSON-LD offer currency on product page
- **JDS Labs**: /products.json: http 404, text/html; charset=utf-8
- **Jinx**: stopped: blocked: http 401
- **johnnie-O**: /products.json: http 404, text/html
- **Jolyn**: no JSON-LD offer currency on product page
- **Jones Natural Chews**: no JSON-LD offer currency on product page
- **Kahtoola**: stopped: blocked: cloudflare challenge
- **Keebio**: stopped: blocked: cloudflare block
- **Kozi & Co**: stopped: robots.txt unreachable: retries exhausted: network error: ConnectError
- **Kristin Ess**: stopped: robots.txt unreachable: retries exhausted: network error: ConnectError
- **Kulfi**: no JSON-LD offer currency on product page
- **Kurgo**: /products.json: http 404, text/html; charset=utf-8
- **LapGear**: /products.json: http 404, ?
- **LARQ**: /products.json: http 404, application/json
- **LifePro**: stopped: blocked: cloudflare challenge
- **Live Tinted**: no JSON-LD offer currency on product page
- **Lively**: /products.json: http 404, ?
- **Lou Lou & Company**: stopped: robots.txt unreachable: retries exhausted: network error: ConnectError
- **LoveShackFancy**: stopped: retries exhausted: http 429
- **Madhappy**: stopped: retries exhausted: http 429
- **Magformers**: stopped: blocked: cloudflare challenge
- **Margaux**: stopped: robots.txt unreachable: retries exhausted: network error: ConnectError
- **Mechcables**: no JSON-LD offer currency on product page
- **Memphis Car Audio**: stopped: blocked: siteground captcha (robots.txt)
- **Messenger Coffee**: /products.json: http 200, text/html
- **Milktooth**: /products.json: http 404, text/html; charset=utf-8
- **Monowear**: stopped: robots.txt unreachable: retries exhausted: network error: ConnectTimeout
- **MOTHER Denim**: stopped: retries exhausted: http 429
- **MusicTeck**: /products.json: http 404, text/html; charset=utf-8
- **Naked Cashmere**: stopped: retries exhausted: http 429
- **Needle Doctor**: stopped: robots.txt unreachable: retries exhausted: network error: ConnectTimeout
- **Noah**: no JSON-LD offer currency on product page
- **NVGTN**: stopped: blocked: http 401
- **Olababy**: /products.json: http 404, text/html; charset=iso-8859-1
- **Outdoor Tech**: /products.json: http 404, ?
- **Pa'lante Packs**: no JSON-LD offer currency on product page
- **Pact**: /products.json: http 200, text/html; charset=UTF-8
- **Pad & Quill**: /products.json: http 404, ?
- **Pawstruck**: no JSON-LD offer currency on product page
- **Psycho Bunny**: stopped: retries exhausted: http 429
- **Rogue Territory**: no JSON-LD offer currency on product page
- **Roost**: stopped: robots.txt unreachable: retries exhausted: network error: ConnectTimeout
- **Saturdays NYC**: stopped: retries exhausted: http 429
- **Schiit Audio**: /products.json: http 200, text/html; charset=utf-8
- **See Kai Run**: /products.json: http 404, text/html; charset=UTF-8
- **Seea**: /products.json: http 200, text/html; charset=UTF-8
- **Snoozer**: /products.json: http 404, text/html; charset=UTF-8
- **Speks**: stopped: robots.txt unreachable: retries exhausted: network error: ConnectError
- **Spigen**: stopped: retries exhausted: http 429
- **Splits59**: stopped: retries exhausted: http 429
- **Sprout Kids**: stopped: robots.txt unreachable: retries exhausted: network error: ConnectError
- **Stereoscope Coffee**: stopped: robots.txt unreachable: retries exhausted: network error: ConnectError
- **Strider Bikes**: /products.json: http 404, text/html; charset=UTF-8
- **Sundays for Dogs**: /products.json: http 200, text/html; charset=utf-8
- **SUPCASE**: no JSON-LD offer currency on product page
- **Swiftwick**: no JSON-LD offer currency on product page
- **Tandem Coffee**: stopped: retries exhausted: http 429
- **Tarptent**: stopped: blocked: siteground captcha (robots.txt)
- **The Woobles**: no JSON-LD offer currency on product page
- **ThocStock**: /products.json: http 404, application/json; charset=utf-8
- **Todd Shelton**: /products.json: http 404, text/html; charset=utf-8
- **Tommy John**: stopped: blocked: cloudflare challenge
- **Tower Paddle Boards**: no JSON-LD offer currency on product page
- **Upgrade Keyboards**: no JSON-LD offer currency on product page
- **Vibes**: /products.json: http 404, text/html;charset=utf-8
- **Vulcan Strength**: /products.json: http 404, text/plain; charset=UTF-8
- **Warbonnet Outdoors**: stopped: blocked: http 403
- **Wonder Crew**: stopped: robots.txt unreachable: retries exhausted: network error: ConnectError
- **Woo Audio**: /products.json: http 404, text/html;charset=utf-8
- **Zack Cables**: stopped: robots.txt unreachable: retries exhausted: network error: ConnectError
- **Zipadee-Zip (Sleeping Baby)**: /products.json: http 404, ?
- **Zoe Organics**: /products.json: http 404, text/html;charset=utf-8

## Terms of Service

`/policies/terms-of-service`, at most 2 requests per store, read only where robots.txt allows it: ban 171, no_ban 31, none_found 11.

| store | terms | source | first matching sentence |
|---|---|---|---|
| AGOLDE | no_ban | read | - |
| Big Bud Press | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the service is provided, without express written permission by us. |
| Corridor | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the service is provided, without express written permission by us. |
| DL1961 | ban | read | You may not reproduce, distribute, republish or retransmit the Content or materials posted at the Website without the prior written permission of DL1961. |
| FRAME | ban | read | You may not republish the Company Content on any Internet, Intranet or Extranet site or incorporate the information in any other database or compilation. |
| Freda Salvador | no_ban | read | - |
| Freenote Cloth | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the service is provided, without express written permission by us. |
| Harper Wilde | ban | read | For example, don’t interfere with our Services, try to access them using a method other than the interface and the instructions that we provide, or extensively or automatically copy any content from the Services (in other words, no scraping). |
| Iron & Resin | ban | read | Such license is subject to your compliance with these Terms and does not include the right to … bsite and the Site Content, or any portion thereof; (e) use of any data mining, robots or similar data gathering or extraction methods; (f) downloading (other than page caching) of any portion of the … |
| Jenni Kayne | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the service is provided, without express written permission by us. |
| Joah Brown | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the service is provided, without express written permission by us. |
| Jungmaven | ban | read | Points are not valid unless earned in strict compliance with the requirements as established and … by any means (including without limitation, by using any script, bot or other automated means) that only simulates compliance with the applicable requirements; and |
| Katin | ban | read | You may not reproduce, distribute, modify, or otherwise use website content without prior written permission. |
| Lady White Co. | no_ban | read | - |
| Leset | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the service is provided, without express written permission by us. |
| Linksoul | no_ban | read | - |
| Lisa Says Gah | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the service is provided, without express written permission by us. |
| Mara Hoffman | ban | read | You may not view, reproduce, print or otherwise use any of the content of this web site for anything other than your personal, informational, noncommercial use. |
| Mate the Label | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the service is provided, without express written permission by us. |
| Negative Underwear | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the service is provided, without express written permission by us. |
| Noah | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the service is provided, without express written permission by us. |
| OBEY Clothing | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the service is provided, without express written permission by us. |
| Rails | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the service is provided, without express written permission by us. |
| Roark | ban | read | You may not modify any of the materials and you may not copy, distribute, transmit, display, perform, reproduce, publish, license, create derivative works from, transfer or sell any Content. |
| Rogue Territory | ban | read | You must not reproduce, distribute, modify, create derivative works of, publicly display, publicly perform, republish, download, store, or transmit any of the material on the Services without our prior written consent. |
| Southern Tide | ban | read | You may not modify, copy, reproduce, republish, upload, post, transmit, or distribute any portion of the Website contents without the prior express written consent of Southern Tide. |
| Spiritual Gangster | ban | read | Except as expressly provided in these Terms, you must not reproduce, distribute, modify, create derivative works of, publicly display, publicly perform, republish, download, store, or transmit any of the Content or Marks on our Services without our express written permission. |
| TomboyX | ban | read | You have no other rights in this Website or any Materials and you may not modify, edit, copy, reproduce, create derivative works of, reverse engineer, alter, enhance or in any way exploit any of this Website or Materials in any manner. |
| Tradlands | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the service is provided, without express written permission by us. |
| Universal Standard | ban | read | You shall only use the Site as permitted by these Terms, and you shall not use the Site or the Content for any commercial, political, obscene, illegal, or inappropriate purpose. |
| Velvet by Graham & Spencer | ban | read | Except where such permission is specifically granted, you may not modify, publish, transmit, participate in the transfer or sale, create derivative works, or in any way exploit, any of the Site Content, in whole or in part. |
| Vissla | ban | read | You may not otherwise reproduce, modify, create derivative works from, republish, upload, post, transmit, distribute, frame or sell any Materials without our prior written permission. |
| Wildfang | ban | read | You agree not to rent, retransmit, disclose, publish, sell, assign, lease, sublicense, market, or transfer the Website or any portion thereof or use it in any manner not expressly authorized by the Terms. |
| Year of Ours | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the service is provided, without express written permission by us. |
| Abyss Headphones | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the service is provided, without express written permission by us. |
| Comply Foam | ban | read | You must not reproduce, distribute, modify, create derivative works of, publicly display, publicly perform, republish, download, store, or transmit any of the material on the Services without our prior written consent. |
| DS18 | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the service is provided, without express written permission by us. |
| Eargasm | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the service is provided, without express written permission by us. |
| ECOXGEAR | ban | read | You must not reproduce, distribute, modify, create derivative works of, publicly display, publicly perform, republish, download, store, or transmit any of the material on the Services without our prior written consent. |
| Gemini Sound | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the service is provided, without express written permission by us. |
| Massive Audio | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the service is provided, without express written permission by us. |
| Music Hall | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the Service is provided, without express written permission by us. |
| Puro Sound Labs | no_ban | read | - |
| Bounce Curl | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the service is provided, without express written permission by us. |
| Camille Rose | no_ban | read | - |
| Danessa Myricks Beauty | no_ban | read | - |
| Hairstory | ban | read | Except as expressly authorized in advance by the Company in writing, you understand that you may not copy, modify, rent, lease, loan, sell, assign, distribute, license, reverse engineer or create derivative works based on the Site or any of its Content. |
| Half Magic | no_ban | read | - |
| Haus Labs | ban | read | This license does not include any resale or commercial use of this Site or its contents; any … ormation for the benefit of any merchant; or any making use of any data mining, robots or data gathering and extraction tools. |
| Kulfi | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the service is provided, without express written permission by us. |
| Live Tinted | ban | read | No part of the Services, including the Live Tinted Content, may be reproduced or transmitted in any … g and recording, except that Live Tinted authorizes you to view, copy, download, and print Live Tinted Content (such as press releases and FAQs) that is available on the Site, provided that: (a) … |
| Mooncat | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the service is provided, without express written permission by us. |
| Olaplex | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Site, use of the Site, or access to the Site or any contact on the Site, without express written permission by us. |
| ONE/SIZE | ban | read | YOU AGREE NOT TO SELL, LICENSE, RENT, DISTRIBUTE, COPY, REPRODUCE, TRANSMIT, PUBLICLY DISPLAY, PUBLICLY PERFORM, PUBLISH, ADAPT, EDIT, MODIFY OR CREATE DERIVATIVE WORKS FROM ANY CONTENT OR MATERIALS ON THE SITE. |
| R+Co | ban | read | You agree not to sell, license, rent, distribute, copy, reproduce, transmit, publicly display, publicly perform, publish, adapt, edit, modify or create derivative works from any content or materials on the Website. |
| Rizos Curls | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the service is provided, without express written permission by us. |
| RMS Beauty | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the service is provided, without express written permission by us. |
| Thrive Causemetics | ban | read | (C) Except as expressly permitted in these Terms of Use or as we may otherwise permit, you may not … use, reproduce, duplicate, distribute, create derivative works based upon, publicly display, publicly perform, publish, transmit, or otherwise exploit Service Content for any purpose whatsoever … |
| Vegamour | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, without express written permission from us. |
| Art of Tea | ban | read | You may not modify, copy, distribute, display, transmit, reproduce, publish, license, create derivative works from, or sell any information, products, or services obtained from this site. |
| Black Oak Coffee | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the service is provided, without express written permission by us. |
| Ceremony Coffee | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the service is provided, without express written permission by us. |
| Dayglow | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the service is provided, without express written permission by us. |
| Elixr Coffee | none_found | no policy text | - |
| Mostra Coffee | ban | read | You agree not to reproduce, duplicate, copy, sell, resell, or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the Service is provided without express written permission from us. |
| Plum Deluxe | ban | read | Attempting to access the website other than through a standard web browser unless you have been permitted to do so by Plum Deluxe through a separate, written agreement (this restriction does not apply to search engines that comply with Plum Deluxe’s robots.txt file); |
| Prodigal | no_ban | read | - |
| Sweet Bloom Coffee | no_ban | read | - |
| American Barbell | no_ban | read | - |
| Assault Fitness | none_found | redirects off the store (assaultfit.com) | - |
| Born Primitive | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the service is provided, without express written permission by us. |
| Buffbunny | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the service is provided, without express written permission by us. |
| Darc Sport | no_ban | read | - |
| Element 26 | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the service is provided, without express written permission by us. |
| Engage Pickleball | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the service is provided, without express written permission by us. |
| Get RX'd | no_ban | read | - |
| Harbinger | ban | read | You shall not, in any way, otherwise copy, distribute, transmit, display, perform, reproduce, publish, license, modify, create derivative works from, sell, or exploit the Site or Online Services. |
| Horizon Fitness | ban | read | This license does not include any resale or commercial use of the Service or its contents; any … mation for the benefit of a merchant or third party; or any use of data mining, robots, or similar data gathering and extraction tools without our express written consent. |
| Hyperwear | no_ban | read | - |
| JadeYoga | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the service is provided, without express written permission by us. |
| Jolyn | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the service is provided, without express written permission by us. |
| JOOLA | none_found | robots.txt disallows /policies/terms-of-service | - |
| Mark Bell Slingshot | ban | read | You must not reproduce, distribute, modify, create derivative works of, publicly display, publicly perform, republish, download, store, or transmit any of the material on the Services without our prior written consent. |
| Oiselle | ban | read | Except as expressly stated in these Terms, you may not use, reproduce, perform, display, create derivative works from, republish, upload, post, transmit, or distribute in any way any Materials without Oiselle’s prior written permission. |
| Paddletek | none_found | robots.txt disallows /policies/terms-of-service | - |
| Path Projects | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the service is provided, without express written permission by us. |
| Raskol Apparel | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the service is provided, without express written permission by us. |
| Rip Toned | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the service is provided, without express written permission by us. |
| Roll Recovery | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the Service is provided, without express written permission by us. |
| RumbleRoller | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the service is provided, without express written permission by us. |
| RX Smart Gear | ban | read | In summary, you must not modify, copy, reproduce, republish, frame, upload to a third party, post, transmit or distribute the content of the Website in any way except as expressly provided for by us or expressly authorized in writing by us. |
| Schiek Sports | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the Service is provided, without express written permission by us. |
| Senita Athletics | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the service is provided, without express written permission by us. |
| SKLZ | ban | read | You shall not, in any way, otherwise copy, distribute, transmit, display, perform, reproduce, publish, license, modify, create derivative works from, sell, or exploit the Site or Online Services. |
| Stamina Products | no_ban | read | - |
| Swiftwick | ban | read | By submitting or entering your information into the Website, you agree that you grant Swiftwick a … ree, worldwide license and right, but not the obligation, to use, copy, modify, display, distribute, download, store, reproduce, transmit, publish or transfer in any manner, in entirety or a … |
| Synergee | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the service is provided, without express written permission by us. |
| tasc Performance | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the service is provided, without express written permission by us. |
| Titan Fitness | ban | read | You may not use bots or automated programs to make purchases on our site. |
| TYR | ban | read | You must not reproduce, distribute, modify, create derivative works of, publicly display, publicly perform, republish, download, store, or transmit any of the material on the Services without our prior written consent. |
| Vatic Pro | no_ban | read | - |
| Victory Grips | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the service is provided, without express written permission by us. |
| Vooray | ban | read | We do not sell, trade, or otherwise transfer to outside parties your personally identifiable information. |
| YoungLA | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the service is provided, without express written permission by us. |
| Albany Park | no_ban | read | - |
| Bentgo | ban | read | If, at our request, you send certain specific submissions (for example contest entries) or without … , you agree that we may, at any time, without restriction, edit, copy, publish, distribute, translate and otherwise use in any medium any comments that you forward to us. |
| Earth Breeze | ban | read | You agree not to reproduce, duplicate, copy, sell, resell, or exploit any portion of the Service, use of the Service, or access to the Service or Site or any contact on the site through which the Service or Site is provided, without express written permission by us. |
| FINEX | ban | read | (c) Except as expressly provided in these Terms, you may not use, modify, republish, frame, print, … display, perform, reproduce, license, transfer, sell, assign, post, transmit, distribute, reverse engineer, create derivative works from, or otherwise exploit any Content or information from the … |
| Hygge & West | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the service is provided, without express written permission by us. |
| Klean Kanteen | no_ban | read | - |
| Lulu and Georgia | ban | read | Do Not Sell or Share My Information |
| Marquette Castings | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the service is provided, without express written permission by us. |
| NEST New York | no_ban | read | - |
| PlanetBox | ban | read | However, you shall not: a) reproduce, duplicate, copy, sell or otherwise exploit the Website or any … er content (“Site Content”) for any commercial purpose; b) use a robot, spider or data mining or extraction tool or process to monitor, extract or copy Site Content; c) use any meta tags, search … |
| Puracy | no_ban | read | - |
| Sabai | ban | read | Scrape the Services or use other automated or manual means to take our content without our express prior written consent; |
| Simple Modern | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the service is provided, without express written permission by us. |
| Sixpenny | ban | read | You may not download, display, reproduce, create derivative works from, transmit, sell, distribute, or in any way exploit Our Site or its Content for any public or commercial use without prior written consent of Sixpenny or the relevant Affiliate. |
| Stargazer Cast Iron | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the Service is provided, without express written permission by us. |
| Sunday Citizen | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the service is provided, without express written permission by us. |
| Takeya | no_ban | read | - |
| Arbor Collective | ban | read | ARBOR does not provide, sell, license, or lease any of the Materials other than those specifically identified as being provided by ARBOR. |
| BOTE | ban | read | Access the sites, services and content for any reason other than to conduct business with Kent Outdoors and/or for informational purposes – use of the sites, services and content for other commercial purposes is strictly prohibited; |
| Catch Surf | ban | read | You must not reproduce, distribute, modify, create derivative works of, publicly display, publicly perform, republish, download, store, or transmit any of the material on the Services without our prior written consent. |
| Crazy Creek | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the Service is provided, without express written permission by us. |
| Durston Gear | ban | read | You must not reproduce, distribute, modify, create derivative works of, publicly display, publicly perform, republish, download, store, or transmit any of the material on the Services without our prior written consent. |
| Fishpond | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the service is provided, without express written permission by us. |
| ICEMULE | ban | read | You must not reproduce, distribute, modify, create derivative works of, publicly display, publicly perform, republish, download, store, or transmit any of the material on the Services without our prior written consent. |
| Moment Skis | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the service is provided, without express written permission by us. |
| Outdoor Vitals | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the service is provided, without express written permission by us. |
| Pa'lante Packs | none_found | http 404 | - |
| RovR Products | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the service is provided, without express written permission by us. |
| Sunday Afternoons | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the service is provided, without express written permission by us. |
| Tower Paddle Boards | no_ban | read | - |
| Boxiecat | no_ban | read | - |
| Earth Animal | ban | read | You agree not to: use the Site for any unlawful purpose; violate any applicable laws or … ess to our systems; interfere with the Site’s operation or security; copy, reproduce, or exploit Site content without permission; or use the Site to harass, abuse, or harm others. |
| Earthbath | no_ban | read | - |
| Finn | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the service is provided, without express written permission by us. |
| Jones Natural Chews | none_found | http 404 | - |
| Lupine Pet | ban | read | You must not reproduce, distribute, modify, create derivative works of, publicly display, publicly perform, republish, download, store, or transmit any of the material on the Services without our prior written consent. |
| Ollydog | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the service is provided, without express written permission by us. |
| Pawstruck | no_ban | read | - |
| PetHonesty | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the service is provided, without express written permission by us. |
| Tuft + Paw | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the service is provided, without express written permission by us. |
| Up Country | ban | read | The information on this Site does not constitute a binding offer of Up Country to sell products featured on this Site. |
| Vetnique Labs | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the service is provided, without express written permission by us. |
| Warren London | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the service is provided, without express written permission by us. |
| Wild Earth | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the service is provided, without express written permission by us. |
| Archer Watch Straps | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the service is provided, without express written permission by us. |
| Azio | no_ban | read | - |
| Beastgrip | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the service is provided, without express written permission by us. |
| BLUETTI | ban | read | You agree not to reproduce, duplicate, copy, sell, resell, or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the Website through which the service is provided, without express written permission by us. |
| Boardsource | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the Service is provided, without express written permission by us. |
| Branch Furniture | none_found | robots.txt disallows /policies/terms-of-service | - |
| Breakthrough Photography | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the service is provided, without express written permission by us. |
| Brevite | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the service is provided, without express written permission by us. |
| Cerakey | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the service is provided, without express written permission by us. |
| Dang Keebs | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the service is provided, without express written permission by us. |
| DODOcase | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the service is provided, without express written permission by us. |
| EcoFlow (US) | ban | read | You must not reproduce, distribute, modify, create derivative works of, publicly display, publicly perform, republish, download, store, or transmit any of the material on our Website, except as follows: |
| Gordy's Camera Straps | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the service is provided, without express written permission by us. |
| Higround | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the Website through which the service is provided, without express written permission by us. |
| Holdfast Gear | ban | read | You may not either directly or through the use of any device, software, internet site, web-based … service, or other means copy, download, stream capture, reproduce, duplicate, archive, distribute, upload, publish, modify, translate, broadcast, perform, display, sell, transmit or retransmit the … |
| Jackery | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Website or the Service without prior express written permission by us. |
| Juuk Design | no_ban | read | - |
| KeebsForAll | ban | read | You must not reproduce, distribute, modify, create derivative works of, publicly display, publicly perform, republish, download, store, or transmit any of the material on the Services without our prior written consent. |
| Kenu | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the service is provided, without express written permission by us. |
| Langly | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the service is provided, without express written permission by us. |
| Mechcables | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the service is provided, without express written permission by us. |
| Mobile Pixels | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the service is provided, without express written permission by us. |
| Omnitype | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the service is provided, without express written permission by us. |
| Pebblebee | no_ban | read | - |
| Poetic | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the service is provided, without express written permission by us. |
| Quad Lock (US) | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the service is provided, without express written permission by us. |
| Rain Design | no_ban | read | - |
| Speck | ban | read | Please do not modify, copy, distribute, transmit, display, perform, reproduce, publish, license, or … create derivative works from information or material on this Site, except as follows: You may download and make one copy of the content and other downloadable items displayed on this Site for … |
| SUPCASE | ban | read | You must not reproduce, distribute, modify, create derivative works of, publicly display, publicly perform, republish, download, store, or transmit any of the material on the Services without our prior written consent. |
| Upgrade Keyboards | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the Service is provided, without express written permission by us. |
| Wyze | ban | read | “WYZE,” “WYZE CAM,” “WYZE CAM PLUS,” “CAM PLUS,” “WYZE SENSE,” “WYZE BAND,” “WYZE SCALE,” “WYZE … “WYZE GUN SAFE,” “WYZE WATCH,” “WYZE SPRINKLER CONTROLLER,” “WYZE ROBOT VACUUM,” “WYZE ANYTHING RECOGNITION,” our names, our logos, our other Product and Service names, our slogans and the look and … |
| Zugu Case | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the service is provided, without express written permission by us. |
| Bella Tunno | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the service is provided, without express written permission by us. |
| Bowy Made | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the service is provided, without express written permission by us. |
| Bunnies By The Bay | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the service is provided, without express written permission by us. |
| Burt's Bees Baby | ban | read | Subject to these Terms of Use and any other terms and conditions on the Website, Company hereby … the non-exclusive right to use the Website and download, install, reproduce, use and disclose the contents of the files or other media provided on the Website that are specifically identified as … |
| Cabbage Patch Kids | ban | read | You agree not to reproduce, modify, create derivative works from, display, perform, publish, … distribute, disseminate, broadcast or circulate any Material to any third party (including, without limitation, the display and distribution of the Material via a third party website) without the … |
| California Baby | ban | read | Except as expressly permitted, you agree not to use the Web Site for sale, trade or other commercial purposes, and, you may not modify, copy, publish, display, transmit, adapt or in any way exploit the content of the Web Site. |
| Clixo | no_ban | read | - |
| Emerson and Friends | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the service is provided, without express written permission by us. |
| Foamnasium | none_found | http 404 | - |
| Goumi Kids | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the service is provided, without express written permission by us. |
| Green Toys | ban | read | You may not use, reproduce, modify, or distribute any content without prior written consent. |
| Healthy Roots Dolls | ban | read | You must not reproduce, distribute, modify, create derivative works of, publicly display, publicly perform, republish, download, store, or transmit any of the material on the Services without our prior written consent. |
| Lily & River | ban | read | You agree not to reproduce, duplicate, copy, sell, resell, or exploit any portion of our website, services, or original content without our express written permission, except as permitted by law. |
| Little Partners | none_found | robots.txt disallows /policies/terms-of-service | - |
| Little Unicorn | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the service is provided, without express written permission by us. |
| Micro Kickboard | ban | read | Except as otherwise provided on the site or in these Terms, you may not use, download, upload, … copy, print, display, perform, reproduce, publish, modify, delete, add to, license, post, transmit or distribute any Materials and Content from this Site in whole or in part, for any public or … |
| Milk Snob | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the service is provided, without express written permission by us. |
| Mockingbird | no_ban | read | - |
| Mushie | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the service is provided, without express written permission by us. |
| Oeuf | ban | read | You must not reproduce, distribute, modify, create derivative works of, publicly display, publicly perform, republish, download, store, or transmit any of the material on the Services without our prior written consent. |
| pediped | ban | read | f) Unless expressly permitted in writing from pediped®, you will not frame, link, associate with advertisements (e.g., pop-ups) or commercially exploit the Site, Site Contents or the Site Code; and |
| Prevelo Bikes | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the service is provided, without express written permission by us. |
| Snuggle Me Organic | none_found | robots.txt disallows /policies/terms-of-service | - |
| Spearmint Love | ban | read | You may not modify the information or materials located on this Site in any way or reproduce or publicly display, perform, or distribute or otherwise use any such materials for any public or commercial purpose. |
| Sphero | none_found | http 404 | - |
| Tea Collection | ban | read | You may not reproduce (except as noted above), publish, transmit, distribute, display, modify, create derivative works from, sell or participate in any sale of, or exploit in any way, in whole or in part, any of the Contents, the Site, or any related software. |
| The Pencil Grip | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the service is provided, without express written permission by us. |
| The Woobles | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the service is provided, without express written permission by us. |
| Tiny Twinkle | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the service is provided, without express written permission by us. |
| Tushbaby | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the service is provided, without express written permission by us. |
| WeeSprout | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the service is provided, without express written permission by us. |
| Wonderfold | ban | read | You may not reproduce, distribute, modify, display, publish, transmit, create derivative works from, or commercially exploit any content without prior written consent from WonderFold. |
| Woolino | ban | read | Attempting to access the Website other than through a standard web browser unless you have been permitted to do so by Woolino through a separate, written agreement (this restriction does not apply to search engines that comply with Woolino’s robots.txt file); |
