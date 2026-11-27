# Recon `recon-005`

- started: 2026-11-27T11:20:16+00:00, finished: 2026-11-27T14:33:54+00:00
- run: https://github.com/siddharthkumarx/ecommerce-price-monitor/actions/runs/45989611418
- candidates: 301, passed: 188 (variant cap 3000)
- run-wide request interval: 4.0s + jitter; halted: no

| store | category | host | robots | products.json | .js | reachable | shopify | products | variants | in stock | .js check | JSON-LD cur | Shopify cur | meta country | reqs | terms | result |
|---|---|---|---|---|---|---|---|---:|---:|---:|---|---|---|---|---:|---|---|
| &Collar | apparel | andcollar.com | ok | yes | yes | yes | yes | 225 | 1546 | 78% | match | USD | USD | US | 6 | ban | PASS |
| BAGGU | apparel | baggu.com | missing-4xx | yes | yes | yes | no | - | - | - | - | - | - | - | 2 | - | fail: not shopify |
| Bandit Running | apparel | banditrunning.com | ok | yes | yes | yes | yes | 496 | 2878 | 61% | match | USD | USD | US | 7 | ban | PASS |
| Billy Reid | apparel | www.billyreid.com | ok | yes | yes | no | no | - | - | - | - | - | - | - | 2 | - | fail: blocked |
| Birdwell | apparel | www.birdwell.com | ok | yes | yes | yes | yes | 377 | 2069 | 88% | match | USD | USD | US | 7 | ban | PASS |
| CALPAK | apparel | www.calpaktravel.com | ok | yes | yes | yes | yes | 184 | 1848 | 62% | match | USD | USD | US | 6 | ban | PASS |
| Criquet Shirts | apparel | criquetshirts.com | ok | yes | yes | yes | yes | 750 | 3916+ | 85% | match | USD | USD | US | 8 | ban | fail: catalog too large, excluded category: alcohol, weapons |
| Dagne Dover | apparel | www.dagnedover.com | ok | yes | yes | yes | yes | 414 | 453 | 67% | match | - | USD | US | 7 | no_ban | PASS |
| Defy Bags | apparel | defybags.com | ok | yes | yes | yes | yes | 213 | 368 | 96% | match | USD | USD | US | 6 | ban | fail: excluded category: alcohol |
| Duck Head | apparel | www.duckhead.com | ok | yes | yes | yes | yes | 500 | 4219+ | 72% | match | USD | USD | US | 7 | ban | fail: catalog too large, excluded category: alcohol |
| Elizabeth Suzann | apparel | esmadebyme.com | ok | yes | yes | yes | yes | 149 | 345 | 46% | match | USD | USD | US | 6 | ban | PASS |
| Feat Clothing | apparel | featclothing.com | ok | yes | yes | yes | yes | 20 | 308 | 83% | match | USD | USD | US | 6 | ban | PASS |
| Free Fly Apparel | apparel | freeflyapparel.com | ok | yes | yes | yes | yes | 750 | 3919+ | 62% | match | USD | USD | US | 8 | ban | fail: catalog too large, excluded category: tobacco/vape |
| Gramicci | apparel | gramicci.com | ok | yes | yes | yes | yes | 250 | 5358+ | 40% | match | USD | USD | US | 6 | ban | fail: catalog too large |
| Greats | apparel | www.greats.com | ok | yes | yes | yes | yes | 97 | 901 | 60% | match | USD | USD | US | 6 | ban | PASS |
| Imogene + Willie | apparel | imogeneandwillie.com | ok | yes | yes | yes | yes | 715 | 3708 | 75% | match | USD | USD | US | 8 | ban | fail: catalog too large |
| Julbo USA | apparel | julbo.us | ok | yes | yes | yes | yes | 161 | 628 | 83% | match | USD | USD | US | 6 | ban | fail: excluded category: alcohol |
| Kizik | apparel | kizik.com | ok | yes | yes | yes | yes | 250 | 5519+ | 59% | match | USD | USD | US | 6 | ban | fail: catalog too large, excluded category: alcohol |
| Knockaround | apparel | knockaround.com | ok | yes | yes | yes | yes | 425 | 850 | 84% | match | USD | USD | US | 7 | ban | PASS |
| Koio | apparel | www.koio.co | ok | yes | yes | yes | yes | 116 | 850 | 75% | match | USD | USD | US | 6 | ban | fail: excluded category: tobacco/vape |
| LeSportsac | apparel | www.lesportsac.com | ok | yes | yes | yes | yes | - | - | - | match | USD | USD | US | 12 | - | fail: blocked mid-recon, empty catalog, needed 429 retries |
| Lo & Sons | apparel | www.loandsons.com | ok | yes | yes | yes | yes | 156 | 287 | 95% | match | USD | USD | US | 6 | ban | PASS |
| Lunya | apparel | lunya.co | ok | yes | yes | yes | yes | 273 | 1326 | 75% | match | USD | USD | US | 7 | ban | PASS |
| OluKai | apparel | olukai.com | ok | yes | yes | yes | yes | 476 | 4803 | 98% | match | USD | USD | US | 7 | no_ban | fail: catalog too large, excluded category: alcohol |
| Outerknown | apparel | www.outerknown.com | ok | yes | yes | yes | yes | - | - | - | match | USD | USD | US | 9 | - | fail: blocked mid-recon, empty catalog, needed 429 retries |
| Pistola Denim | apparel | www.pistoladenim.com | ok | yes | yes | yes | yes | 229 | 2068 | 75% | match | USD | USD | US | 6 | ban | fail: excluded category: alcohol |
| rabbit | apparel | www.runinrabbit.com | ok | yes | yes | yes | yes | 500 | 5869+ | 57% | match | - | USD | US | 7 | ban | fail: catalog too large |
| Richer Poorer | apparel | www.richer-poorer.com | ok | yes | yes | yes | yes | 2 | 44 | 61% | match | USD | USD | US | 6 | none_found | PASS |
| Scout Bags | apparel | scoutbags.com | ok | yes | yes | yes | yes | 1409 | 1434 | 28% | match | USD | USD | US | 11 | ban | fail: excluded category: alcohol |
| Seychelles Footwear | apparel | seychellesfootwear.com | ok | yes | yes | yes | yes | 166 | 3855 | 89% | match | USD | USD | US | 6 | ban | fail: catalog too large |
| State & Liberty | apparel | stateandliberty.com | ok | yes | yes | yes | yes | 249 | 1164 | 91% | match | USD | USD | US | 6 | ban | PASS |
| SuitShop | apparel | suitshop.com | ok | yes | yes | yes | no | - | - | - | - | - | - | - | 2 | - | fail: not shopify |
| Sunski | apparel | sunski.com | ok | yes | yes | yes | yes | 137 | 451 | 89% | match | USD | USD | US | 6 | no_ban | PASS |
| Tifosi Optics | apparel | tifosioptics.com | ok | yes | yes | yes | yes | 209 | 706 | 97% | match | - | USD | US | 6 | ban | PASS |
| 1MORE (US) | audio | usa.1more.com | ok | yes | yes | yes | yes | 31 | 59 | 95% | match | USD | USD | HK | 6 | ban | PASS |
| Altec Lansing | audio | www.alteclansing.com | ok | yes | yes | yes | yes | 79 | 216 | 50% | match | USD | USD | US | 6 | no_ban | PASS |
| Apos Audio | audio | apos.audio | ok | yes | yes | yes | yes | 490 | 1463 | 79% | match | USD | USD | US | 7 | ban | PASS |
| Audeze | audio | www.audeze.com | ok | yes | yes | yes | yes | 87 | 170 | 58% | match | USD | USD | US | 6 | no_ban | PASS |
| Audio Advice | audio | www.audioadvice.com | ok | yes | yes | yes | yes | - | - | - | match | USD | USD | US | 10 | - | fail: blocked mid-recon, empty catalog, needed 429 retries |
| Audio46 | audio | audio46.com | ok | yes | yes | yes | yes | 1750 | 3350+ | 45% | match | USD | USD | US | 12 | ban | fail: catalog too large, excluded category: alcohol |
| Bloom Audio | audio | bloomaudio.com | ok | yes | yes | yes | yes | 1185 | 3031 | 65% | match | USD | USD | US | 10 | ban | fail: catalog too large, excluded category: alcohol |
| BOSS Audio Systems | audio | bossaudio.com | ok | yes | yes | yes | yes | 245 | 245 | 64% | match | USD | USD | US | 6 | ban | PASS |
| Cleer Audio | audio | cleeraudio.com | ok | yes | yes | yes | yes | 26 | 46 | 72% | match | USD | USD | US | 6 | none_found | PASS |
| Emotiva | audio | emotiva.com | ok | yes | yes | yes | yes | 116 | 193 | 77% | match | USD | USD | US | 6 | ban | PASS |
| Fosi Audio | audio | fosiaudio.com | ok | yes | yes | yes | yes | 100 | 369 | 97% | match | USD | USD | HK | 6 | ban | PASS |
| Grado Labs | audio | gradolabs.com | ok | yes | yes | yes | yes | 64 | 115 | 96% | match | USD | USD | US | 6 | no_ban | PASS |
| Headphones.com | audio | headphones.com | ok | yes | yes | yes | yes | 718 | 1210 | 44% | match | USD | USD | US | 8 | ban | PASS |
| HyperX | audio | hyperx.com | ok | yes | yes | yes | yes | 282 | 400 | 86% | match | USD | USD | US | 7 | no_ban | PASS |
| KEF (US) | audio | us.kef.com | ok | yes | yes | yes | yes | 118 | 249 | 96% | missing | - | - | US | 6 | none_found | fail: currency not proven USD, product .js unavailable |
| Master & Dynamic | audio | www.masterdynamic.com | ok | yes | yes | yes | yes | 60 | 195 | 60% | match | USD | USD | US | 6 | ban | PASS |
| Rockford Fosgate | audio | rockfordfosgate.com | ok | yes | yes | yes | no | - | - | - | - | - | - | - | 2 | - | fail: not shopify |
| Shokz | audio | shokz.com | ok | yes | yes | yes | yes | 64 | 416 | 86% | match | USD | USD | US | 6 | ban | PASS |
| Skullcandy | audio | www.skullcandy.com | ok | yes | yes | yes | yes | 43 | 170 | 79% | match | USD | USD | US | 6 | ban | PASS |
| Soundcore (US) | audio | us.soundcore.com | ok | yes | yes | yes | yes | 540 | 1506 | 74% | match | USD | USD | US | 7 | none_found | PASS |
| Sundown Audio | audio | sundownaudio.com | ok | yes | yes | yes | yes | 414 | 876 | 70% | match | USD | USD | US | 7 | no_ban | PASS |
| SVS | audio | www.svsound.com | ok | yes | yes | yes | yes | 247 | 250 | 10% | match | USD | USD | US | 6 | ban | PASS |
| Tivoli Audio | audio | tivoliaudio.com | ok | yes | yes | yes | yes | 62 | 618 | 97% | match | USD | USD | US | 6 | no_ban | PASS |
| TREBLAB | audio | treblab.com | ok | yes | yes | yes | yes | 39 | 49 | 82% | match | USD | USD | US | 6 | ban | PASS |
| Turntable Lab | audio | www.turntablelab.com | ok | yes | yes | yes | yes | - | - | - | match | USD | USD | US | 10 | - | fail: blocked mid-recon, empty catalog, needed 429 retries |
| Turtle Beach | audio | www.turtlebeach.com | ok | yes | yes | yes | no | - | - | - | - | - | - | - | 2 | - | fail: not shopify |
| TURTLEBOX | audio | turtleboxaudio.com | ok | yes | yes | yes | yes | 42 | 232 | 85% | match | USD | USD | US | 6 | ban | PASS |
| U-Turn Audio | audio | uturnaudio.com | ok | yes | yes | yes | yes | 95 | 1417 | 100% | match | - | USD | US | 6 | ban | PASS |
| Upscale Audio | audio | upscaleaudio.com | ok | yes | yes | yes | yes | 1250 | 3111+ | 91% | match | USD | USD | US | 10 | no_ban | fail: catalog too large |
| Victrola | audio | www.victrola.com | ok | yes | yes | yes | yes | 227 | 252 | 76% | match | USD | USD | US | 6 | ban | PASS |
| Wet Sounds | audio | www.wetsounds.com | ok | yes | yes | yes | yes | 392 | 593 | 78% | match | USD | USD | US | 7 | ban | fail: excluded category: alcohol |
| WiiM | audio | wiimhome.com | ok | yes | yes | no | no | - | - | - | - | - | - | - | 2 | - | fail: blocked |
| World Wide Stereo | audio | www.worldwidestereo.com | ok | yes | yes | yes | yes | - | - | - | match | USD | USD | US | 9 | - | fail: blocked mid-recon, empty catalog, needed 429 retries |
| Arctic Fox | beauty | www.arcticfoxhaircolor.com | ok | yes | yes | yes | no | - | - | - | - | - | - | - | 2 | - | fail: not shopify |
| Beauty Bakerie | beauty | www.beautybakerie.com | ok | yes | yes | yes | yes | 89 | 108 | 86% | match | USD | USD | US | 6 | no_ban | PASS |
| Beautyblender | beauty | beautyblender.com | ok | yes | yes | yes | yes | 63 | 111 | 77% | match | USD | USD | US | 6 | no_ban | PASS |
| Besame Cosmetics | beauty | besamecosmetics.com | ok | yes | yes | yes | yes | 73 | 185 | 77% | match | USD | USD | US | 6 | ban | PASS |
| Cocokind | beauty | www.cocokind.com | ok | yes | yes | yes | yes | 77 | 133 | 86% | match | USD | USD | US | 6 | ban | PASS |
| Crown Affair | beauty | www.crownaffair.com | ok | yes | yes | yes | yes | 72 | 115 | 90% | match | USD | USD | US | 6 | ban | PASS |
| Derma E | beauty | dermae.com | ok | yes | yes | yes | yes | 136 | 136 | 92% | match | USD | USD | US | 6 | no_ban | fail: excluded category: cannabis/cbd |
| Dermalogica | beauty | www.dermalogica.com | ok | yes | yes | yes | yes | 216 | 280 | 95% | match | USD | USD | US | 6 | ban | PASS |
| Dose of Colors | beauty | doseofcolors.com | ok | yes | yes | yes | yes | 44 | 200 | 98% | match | USD | USD | US | 6 | ban | PASS |
| Dr. Dennis Gross Skincare | beauty | www.drdennisgross.com | ok | yes | yes | yes | no | - | - | - | - | - | - | - | 2 | - | fail: not shopify |
| Fenty Beauty | beauty | fentybeauty.com | ok | yes | yes | yes | yes | 1054 | 1215 | 81% | match | USD | USD | US | 10 | ban | fail: excluded category: alcohol |
| It's a 10 Haircare | beauty | itsa10haircare.com | ok | yes | yes | yes | yes | 77 | 112 | 96% | match | USD | USD | US | 6 | ban | PASS |
| Jeffree Star Cosmetics | beauty | jeffreestarcosmetics.com | ok | yes | yes | yes | yes | 283 | 1225 | 55% | match | - | USD | US | 7 | no_ban | fail: excluded category: cannabis/cbd |
| Jones Road | beauty | www.jonesroadbeauty.com | ok | yes | yes | yes | yes | 114 | 509 | 93% | match | USD | USD | US | 6 | ban | PASS |
| Juice Beauty | beauty | juicebeauty.com | ok | yes | yes | yes | yes | 73 | 105 | 90% | match | USD | USD | US | 6 | ban | PASS |
| KASH Beauty | beauty | kashbeauty.com | ok | yes | yes | yes | yes | 105 | 249 | 93% | match | USD | USD | IE | 6 | ban | PASS |
| Lashify | beauty | www.lashify.com | ok | yes | yes | yes | yes | 129 | 900 | 95% | match | - | USD | US | 6 | ban | PASS |
| Lume Deodorant | beauty | lumedeodorant.com | ok | yes | yes | yes | no | - | - | - | - | - | - | - | 2 | - | fail: not shopify |
| Makeup by Mario | beauty | www.makeupbymario.com | ok | yes | yes | yes | yes | 67 | 363 | 93% | match | USD | USD | US | 6 | ban | PASS |
| Milani Cosmetics | beauty | www.milanicosmetics.com | ok | yes | yes | yes | yes | 164 | 556 | 97% | match | USD | USD | US | 6 | no_ban | PASS |
| Murad | beauty | www.murad.com | ok | yes | yes | yes | yes | 118 | 119 | 84% | match | USD | USD | US | 6 | ban | PASS |
| Nécessaire | beauty | necessaire.com | ok | yes | yes | yes | yes | 126 | 139 | 92% | match | USD | USD | US | 6 | ban | PASS |
| Pacifica Beauty | beauty | www.pacificabeauty.com | ok | yes | yes | yes | yes | 223 | 283 | 86% | match | USD | USD | US | 6 | ban | PASS |
| Sigma Beauty | beauty | sigmabeauty.com | ok | yes | yes | yes | yes | 335 | 699 | 68% | match | USD | USD | US | 7 | no_ban | PASS |
| Soko Glam | beauty | sokoglam.com | ok | yes | yes | yes | yes | 506 | 595 | 69% | match | USD | USD | US | 8 | ban | fail: excluded category: alcohol |
| Sol de Janeiro | beauty | soldejaneiro.com | ok | yes | yes | yes | yes | 157 | 720 | 88% | match | USD | USD | US | 6 | ban | fail: excluded category: alcohol |
| Stila Cosmetics | beauty | www.stilacosmetics.com | ok | yes | yes | yes | yes | 139 | 321 | 90% | match | USD | USD | US | 6 | ban | PASS |
| Sunday Riley | beauty | sundayriley.com | ok | yes | yes | yes | yes | 55 | 78 | 99% | match | USD | USD | US | 6 | ban | PASS |
| tarte cosmetics | beauty | tartecosmetics.com | ok | yes | yes | yes | yes | 249 | 1153 | 89% | match | USD | USD | US | 6 | ban | PASS |
| Tata Harper | beauty | tataharperskincare.com | ok | yes | yes | yes | yes | 69 | 95 | 98% | match | USD | USD | US | 6 | ban | PASS |
| The INKEY List | beauty | uk.theinkeylist.com | ok | yes | yes | yes | yes | 137 | 146 | 90% | match | GBP | GBP | GB | 6 | ban | fail: currency not proven USD |
| Truly Beauty | beauty | www.trulybeauty.com | ok | yes | yes | yes | yes | 81 | 113 | 97% | match | USD | USD | US | 6 | ban | fail: excluded category: cannabis/cbd |
| Tubby Todd Bath Co. | beauty | tubbytodd.com | ok | yes | yes | yes | yes | 75 | 253 | 82% | match | USD | USD | US | 6 | ban | PASS |
| Tula Skincare | beauty | tula.com | ok | yes | yes | yes | yes | 105 | 147 | 99% | match | USD | USD | US | 6 | no_ban | PASS |
| Westman Atelier | beauty | www.westman-atelier.com | ok | yes | yes | yes | yes | 246 | 355 | 74% | match | USD | USD | US | 6 | ban | fail: excluded category: alcohol |
| Canyon Coffee | coffee_tea | canyoncoffee.co | missing-4xx | yes | yes | yes | no | - | - | - | - | - | - | - | 2 | - | fail: not shopify |
| Chamberlain Coffee | coffee_tea | chamberlaincoffee.com | ok | yes | yes | yes | no | - | - | - | - | - | - | - | 2 | - | fail: not shopify |
| Counter Culture Coffee | coffee_tea | counterculturecoffee.com | ok | yes | yes | yes | yes | 182 | 298 | 55% | match | USD | USD | US | 6 | ban | fail: excluded category: alcohol |
| Dark Matter Coffee | coffee_tea | www.darkmattercoffee.com | ok | yes | yes | yes | yes | 100 | 312 | 88% | match | USD | USD | US | 6 | ban | fail: excluded category: alcohol |
| Davidson's Organic Tea | coffee_tea | www.davidsonstea.com | ok | yes | yes | yes | yes | - | - | - | match | USD | USD | US | 9 | - | fail: blocked mid-recon, empty catalog, needed 429 retries |
| Death Wish Coffee | coffee_tea | www.deathwishcoffee.com | ok | yes | yes | yes | yes | 152 | 413 | 84% | match | USD | USD | US | 6 | ban | fail: excluded category: alcohol |
| Equator Coffees | coffee_tea | www.equatorcoffees.com | ok | yes | yes | yes | yes | 146 | 739 | 98% | match | USD | USD | US | 5 | none_found | PASS |
| Harney & Sons | coffee_tea | www.harney.com | ok | yes | yes | no | no | - | - | - | - | - | - | - | 2 | - | fail: blocked |
| Heine Brothers' Coffee | coffee_tea | heinebroscoffee.com | ok | yes | yes | yes | yes | 25 | 145 | 99% | match | USD | USD | US | 6 | no_ban | PASS |
| Intelligentsia | coffee_tea | www.intelligentsia.com | ok | yes | yes | yes | yes | 220 | 362 | 32% | match | USD | USD | US | 6 | ban | fail: excluded category: alcohol |
| Jade Leaf Matcha | coffee_tea | www.jadeleafmatcha.com | ok | yes | yes | yes | yes | 29 | 43 | 93% | match | USD | USD | US | 6 | ban | PASS |
| Kettl | coffee_tea | kettl.co | ok | yes | yes | yes | yes | 179 | 251 | 66% | match | USD | USD | US | 5 | none_found | PASS |
| La Colombe | coffee_tea | www.lacolombe.com | ok | yes | yes | yes | yes | 73 | 152 | 93% | match | USD | USD | US | 6 | ban | PASS |
| Numi Organic Tea | coffee_tea | numitea.com | ok | yes | yes | yes | yes | 67 | 175 | 89% | match | USD | USD | US | 6 | no_ban | PASS |
| Onyx Coffee Lab | coffee_tea | onyxcoffeelab.com | ok | yes | yes | yes | yes | 249 | 546 | 62% | match | - | USD | US | 6 | ban | fail: excluded category: alcohol |
| Partners Coffee | coffee_tea | www.partnerscoffee.com | ok | yes | yes | yes | yes | 85 | 282 | 71% | match | USD | USD | US | 6 | ban | PASS |
| Rishi Tea & Botanicals | coffee_tea | www.rishi-tea.com | ok | yes | yes | yes | yes | 284 | 504 | 85% | match | USD | USD | US | 7 | ban | PASS |
| SEY Coffee | coffee_tea | www.seycoffee.com | ok | yes | yes | yes | yes | - | - | - | match | - | USD | US | 10 | - | fail: blocked mid-recon, empty catalog, needed 429 retries |
| Sightglass Coffee | coffee_tea | sightglasscoffee.com | ok | yes | yes | yes | yes | 70 | 541 | 94% | match | USD | USD | US | 6 | ban | fail: excluded category: alcohol |
| Smith Teamaker | coffee_tea | www.smithtea.com | ok | yes | yes | yes | yes | 172 | 262 | 76% | match | - | USD | US | 6 | ban | fail: excluded category: alcohol |
| Snarky Tea | coffee_tea | www.snarkytea.com | ok | yes | yes | yes | yes | 135 | 250 | 88% | match | USD | USD | US | 6 | ban | PASS |
| Stumptown Coffee | coffee_tea | www.stumptowncoffee.com | ok | yes | yes | yes | yes | 127 | 858 | 96% | match | USD | USD | US | 6 | ban | fail: excluded category: alcohol |
| Temple Coffee Roasters | coffee_tea | templecoffee.com | ok | yes | yes | yes | yes | 129 | 379 | 92% | match | USD | USD | US | 6 | ban | PASS |
| The Republic of Tea | coffee_tea | www.republicoftea.com | ok | yes | yes | yes | yes | - | - | - | match | USD | USD | US | 9 | - | fail: blocked mid-recon, empty catalog, needed 429 retries |
| The Tea Spot | coffee_tea | www.theteaspot.com | ok | yes | yes | yes | yes | 175 | 516 | 76% | match | USD | USD | US | 6 | ban | PASS |
| Verve Coffee Roasters | coffee_tea | www.vervecoffee.com | ok | yes | yes | yes | yes | 177 | 1221 | 30% | match | USD | USD | US | 6 | no_ban | PASS |
| Again Faster | fitness | www.againfaster.com | ok | yes | yes | yes | yes | 293 | 1438 | 64% | match | - | USD | US | 7 | ban | PASS |
| Bala | fitness | shopbala.com | ok | yes | yes | yes | yes | 135 | 850 | 83% | match | USD | USD | US | 5 | none_found | PASS |
| Bells of Steel USA | fitness | bellsofsteel.us | ok | yes | yes | yes | yes | 472 | 1512 | 86% | match | USD | USD | US | 7 | ban | PASS |
| Crossrope | fitness | www.crossrope.com | ok | yes | yes | yes | yes | 208 | 823 | 61% | match | USD | USD | US | 6 | ban | PASS |
| Feetures | fitness | feetures.com | ok | yes | yes | yes | yes | 169 | 3807 | 93% | match | USD | USD | US | 6 | ban | fail: catalog too large |
| FlipBelt | fitness | flipbelt.com | ok | yes | yes | yes | yes | 105 | 1749 | 70% | match | USD | USD | US | 6 | ban | PASS |
| Fringe Sport | fitness | www.fringesport.com | ok | yes | yes | yes | yes | 243 | 1342 | 83% | match | USD | USD | US | 6 | no_ban | PASS |
| Gaiam | fitness | www.gaiam.com | ok | yes | yes | yes | yes | 143 | 263 | 66% | match | USD | USD | US | 6 | ban | PASS |
| Gymreapers | fitness | www.gymreapers.com | ok | yes | yes | yes | yes | 496 | 3548 | 81% | match | USD | USD | US | 7 | ban | fail: catalog too large, excluded category: alcohol |
| Hugger Mugger | fitness | www.huggermugger.com | ok | yes | yes | yes | yes | 117 | 447 | 83% | match | USD | USD | US | 6 | ban | PASS |
| Hyperice | fitness | hyperice.com | ok | yes | yes | yes | yes | 70 | 165 | 72% | match | USD | USD | US | 6 | ban | PASS |
| KANE Footwear | fitness | kanefootwear.com | ok | yes | yes | yes | yes | 228 | 2537 | 68% | match | USD | USD | US | 6 | ban | PASS |
| Kettlebell Kings | fitness | www.kettlebellkings.com | ok | no | no | no | no | - | - | - | - | - | - | - | 1 | - | fail: robots disallows |
| Life Fitness Shop | fitness | shop.lifefitness.com | ok | yes | yes | yes | yes | 346 | 907 | 93% | match | USD | USD | US | 7 | ban | PASS |
| Living.Fit | fitness | www.living.fit | ok | yes | yes | yes | yes | - | - | - | match | USD | USD | US | 10 | - | fail: blocked mid-recon, empty catalog, needed 429 retries |
| Manduka | fitness | www.manduka.com | ok | yes | yes | yes | yes | 103 | 697 | 90% | match | USD | USD | US | 6 | ban | PASS |
| Nathan Sports | fitness | nathansports.com | ok | yes | yes | yes | yes | 112 | 504 | 67% | match | USD | USD | US | 5 | none_found | PASS |
| OOFOS | fitness | www.oofos.com | ok | yes | yes | yes | yes | 158 | 1717 | 80% | match | USD | USD | US | 6 | no_ban | PASS |
| Peak Pilates | fitness | www.peakpilates.com | ok | yes | yes | yes | yes | 195 | 354 | 72% | match | USD | USD | US | 6 | none_found | PASS |
| PowerBlock | fitness | powerblock.com | ok | yes | yes | yes | yes | 115 | 362 | 90% | match | USD | USD | US | 6 | ban | PASS |
| PRx Performance | fitness | prxperformance.com | ok | yes | yes | yes | yes | 473 | 2713 | 88% | match | USD | USD | US | 7 | ban | PASS |
| REP Fitness | fitness | repfitness.com | ok | yes | yes | yes | yes | 500 | 3499+ | 84% | match | USD | USD | US | 6 | none_found | fail: catalog too large |
| SOLE Fitness | fitness | www.soletreadmills.com | ok | yes | yes | yes | yes | 24 | 24 | 92% | match | USD | USD | US | 6 | ban | PASS |
| Sunny Health & Fitness | fitness | sunnyhealthfitness.com | ok | yes | yes | yes | yes | 249 | 1000 | 97% | match | USD | USD | US | 6 | ban | PASS |
| Torque Fitness | fitness | www.torquefitness.com | ok | yes | yes | yes | yes | 204 | 383 | 77% | match | USD | USD | US | 6 | ban | PASS |
| TRX Training | fitness | www.trxtraining.com | ok | yes | yes | yes | yes | 183 | 355 | 89% | match | USD | USD | US | 6 | ban | PASS |
| Yoloha Yoga | fitness | yolohayoga.com | ok | yes | yes | yes | yes | 132 | 162 | 100% | match | USD | USD | US | 6 | ban | PASS |
| Areaware | home_kitchen | www.areaware.com | ok | yes | yes | yes | yes | 24 | 24 | 92% | match | USD | USD | US | 6 | ban | fail: excluded category: alcohol |
| Bearaby | home_kitchen | bearaby.com | ok | yes | yes | yes | yes | 90 | 1182 | 45% | match | USD | USD | US | 5 | none_found | PASS |
| Bee's Wrap | home_kitchen | www.beeswrap.com | ok | yes | yes | yes | yes | 35 | 85 | 91% | match | USD | USD | US | 6 | ban | PASS |
| Bloomist | home_kitchen | bloomist.com | ok | yes | yes | yes | yes | 710 | 1491 | 87% | match | USD | USD | US | 8 | ban | PASS |
| Branch Basics | home_kitchen | branchbasics.com | ok | yes | yes | yes | yes | 103 | 142 | 45% | match | USD | USD | US | 6 | ban | PASS |
| Candle-lite | home_kitchen | www.candle-lite.com | ok | yes | yes | yes | yes | 249 | 252 | 66% | match | USD | USD | US | 6 | ban | fail: excluded category: alcohol |
| Dirty Labs | home_kitchen | dirtylabs.com | ok | yes | yes | yes | yes | 32 | 38 | 100% | match | - | USD | US | 6 | ban | PASS |
| Dusen Dusen | home_kitchen | dusendusen.com | unreachable | - | - | no | no | - | - | - | - | - | - | - | 4 | - | fail: blocked |
| Field Company | home_kitchen | fieldcompany.com | ok | yes | yes | yes | yes | 94 | 217 | 81% | match | USD | USD | US | 6 | no_ban | PASS |
| GIR | home_kitchen | gir.co | ok | yes | yes | yes | yes | 27 | 198 | 81% | match | USD | USD | US | 6 | no_ban | PASS |
| Hawkins New York | home_kitchen | www.hawkinsnewyork.com | ok | yes | yes | yes | yes | - | - | - | match | USD | USD | US | 10 | - | fail: blocked mid-recon, empty catalog, needed 429 retries |
| Homesick | home_kitchen | homesick.com | ok | yes | yes | yes | yes | 253 | 256 | 94% | match | USD | USD | US | 7 | ban | PASS |
| Jungalow | home_kitchen | jungalow.com | ok | yes | yes | yes | no | - | - | - | - | - | - | - | 2 | - | fail: not shopify |
| Keap | home_kitchen | keapcandles.com | ok | yes | yes | yes | yes | 28 | 168 | 86% | match | - | USD | US | 6 | no_ban | PASS |
| Leeway Home | home_kitchen | leewayhome.com | ok | yes | yes | no | no | - | - | - | - | - | - | - | 2 | - | fail: blocked |
| Molly's Suds | home_kitchen | mollyssuds.com | ok | yes | yes | yes | yes | 43 | 143 | 81% | match | USD | USD | US | 6 | ban | PASS |
| Morrow Soft Goods | home_kitchen | morrowsoftgoods.com | ok | yes | yes | yes | yes | 430 | 658 | 86% | match | USD | USD | US | 7 | ban | PASS |
| Olive Ateliers | home_kitchen | oliveateliers.com | ok | yes | yes | yes | yes | 2750 | 3304+ | 36% | match | USD | USD | US | 16 | ban | fail: catalog too large, excluded category: alcohol, tobacco/vape |
| Onsen | home_kitchen | onsentowel.com | ok | yes | yes | yes | yes | 37 | 317 | 75% | match | USD | USD | US | 6 | no_ban | PASS |
| Otherland | home_kitchen | www.otherland.com | ok | yes | yes | yes | yes | 59 | 59 | 90% | match | - | USD | US | 6 | ban | PASS |
| P.F. Candle Co. | home_kitchen | pfcandleco.com | ok | yes | yes | yes | yes | 74 | 79 | 90% | match | USD | USD | US | 6 | ban | fail: excluded category: tobacco/vape |
| Peacock Alley | home_kitchen | www.peacockalley.com | ok | yes | yes | yes | yes | 254 | 2260 | 93% | match | USD | USD | US | 7 | ban | PASS |
| Pura | home_kitchen | pura.com | ok | no | yes | no | no | - | - | - | - | - | - | - | 1 | - | fail: robots disallows |
| Revival Rugs | home_kitchen | www.revivalrugs.com | ok | yes | yes | yes | no | - | - | - | - | - | - | - | 2 | - | fail: not shopify |
| Schoolhouse | home_kitchen | schoolhouse.com | ok | yes | yes | yes | yes | 285 | 1343 | 88% | match | USD | USD | US | 7 | no_ban | PASS |
| Sheets & Giggles | home_kitchen | sheetsgiggles.com | ok | yes | yes | yes | yes | 3 | 50 | 78% | match | USD | USD | US | 6 | no_ban | PASS |
| Sijo | home_kitchen | sijohome.com | ok | yes | yes | yes | yes | 67 | 1789 | 50% | match | USD | USD | US | 6 | ban | PASS |
| Slowdown Studio | home_kitchen | slowdownstudio.com | ok | yes | yes | yes | yes | 182 | 346 | 86% | missing | - | - | AU | 6 | ban | fail: currency not proven USD, product .js unavailable, excluded category: alcohol |
| Smithey Ironware | home_kitchen | smithey.com | ok | yes | yes | yes | yes | 62 | 72 | 100% | match | USD | USD | US | 6 | ban | PASS |
| Stone Candles | home_kitchen | www.stonecandles.com | ok | yes | yes | yes | yes | - | - | - | match | USD | USD | US | 10 | - | fail: blocked mid-recon, empty catalog, needed 429 retries |
| Sweet Water Decor | home_kitchen | www.sweetwaterdecor.com | ok | yes | yes | yes | yes | 799 | 1004 | 94% | missing | USD | - | - | 9 | ban | fail: product .js unavailable, excluded category: alcohol |
| Weezie | home_kitchen | weezietowels.com | ok | yes | yes | yes | yes | 249 | 3190 | 80% | match | USD | USD | US | 6 | ban | fail: catalog too large, excluded category: alcohol |
| Year & Day | home_kitchen | yearandday.com | ok | yes | yes | yes | yes | 114 | 497 | 97% | match | USD | USD | US | 6 | ban | PASS |
| Aer | outdoor | aersf.com | ok | yes | yes | yes | yes | 119 | 193 | 89% | match | USD | USD | US | 6 | none_found | PASS |
| Big Agnes | outdoor | www.bigagnes.com | ok | yes | yes | yes | yes | 279 | 716 | 94% | match | USD | USD | US | 7 | no_ban | PASS |
| BÉIS | outdoor | beistravel.com | ok | yes | yes | yes | yes | 366 | 544 | 86% | match | USD | USD | US | 7 | ban | PASS |
| Darn Tough | outdoor | darntough.com | ok | yes | yes | yes | yes | 373 | 2636 | 82% | match | USD | USD | US | 7 | ban | fail: excluded category: alcohol |
| Eagle Creek | outdoor | eaglecreek.com | ok | yes | yes | yes | yes | 173 | 1108 | 78% | match | USD | USD | US | 6 | ban | PASS |
| FrictionLabs | outdoor | shop.frictionlabs.com | ok | yes | yes | yes | yes | 62 | 306 | 44% | match | - | USD | US | 6 | ban | fail: excluded category: cannabis/cbd |
| Goal Zero | outdoor | goalzero.com | ok | yes | yes | yes | yes | 399 | 418 | 33% | match | USD | USD | US | 7 | ban | fail: excluded category: tobacco/vape |
| Gossamer Gear | outdoor | www.gossamergear.com | ok | yes | yes | yes | yes | 120 | 210 | 92% | match | USD | USD | US | 6 | ban | PASS |
| Grand Trunk | outdoor | www.grandtrunk.com | ok | yes | yes | yes | yes | 79 | 306 | 76% | match | USD | USD | US | 6 | ban | PASS |
| GSI Outdoors | outdoor | gsioutdoors.com | ok | yes | yes | yes | yes | 372 | 554 | 87% | match | USD | USD | US | 7 | ban | fail: excluded category: alcohol |
| Helinox | outdoor | helinox.com | ok | yes | yes | yes | yes | 159 | 329 | 74% | match | USD | USD | US | 6 | ban | PASS |
| HEST | outdoor | hest.com | ok | yes | yes | yes | yes | 71 | 213 | 76% | match | USD | USD | US | 6 | ban | PASS |
| HydraPak | outdoor | www.hydrapak.com | ok | yes | yes | yes | yes | 177 | 487 | 77% | match | USD | USD | US | 6 | ban | PASS |
| Hyperlite Mountain Gear | outdoor | hyperlitemountaingear.com | ok | yes | yes | yes | yes | 121 | 462 | 92% | match | USD | USD | US | 5 | none_found | PASS |
| Ibex | outdoor | ibex.com | ok | yes | yes | yes | yes | 124 | 2369 | 56% | match | USD | USD | US | 6 | ban | PASS |
| iROCKER | outdoor | irockersup.com | ok | yes | yes | yes | no | - | - | - | - | - | - | - | 2 | - | fail: not shopify |
| Janji | outdoor | janji.com | ok | yes | yes | yes | yes | 109 | 1954 | 67% | match | USD | USD | US | 6 | ban | PASS |
| Kelty | outdoor | kelty.com | ok | yes | yes | no | no | - | - | - | - | - | - | - | 2 | - | fail: blocked |
| Ornot | outdoor | www.ornotbike.com | ok | yes | yes | yes | yes | 372 | 1831 | 58% | match | USD | USD | US | 8 | ban | fail: needed 429 retries |
| Oveja Negra | outdoor | www.ovejanegrabikepacking.com | ok | yes | yes | yes | yes | 214 | 1086 | 58% | match | - | USD | US | 6 | ban | PASS |
| Pacsafe | outdoor | pacsafe.com | ok | yes | yes | yes | yes | 88 | 332 | 71% | match | USD | USD | US | 6 | ban | PASS |
| Paravel | outdoor | paravel.com | ok | yes | yes | yes | yes | 58 | 58 | 78% | match | USD | USD | US | 6 | no_ban | PASS |
| Rocky Talkie | outdoor | rockytalkie.com | ok | yes | yes | yes | yes | 47 | 85 | 94% | missing | - | - | US | 6 | ban | fail: currency not proven USD, product .js unavailable |
| Sierra Designs | outdoor | sierradesigns.com | ok | yes | yes | yes | yes | 40 | 150 | 68% | match | USD | USD | US | 6 | ban | PASS |
| Six Moon Designs | outdoor | www.sixmoondesigns.com | ok | yes | yes | yes | yes | 112 | 624 | 68% | match | USD | USD | US | 6 | ban | fail: excluded category: alcohol |
| Stio | outdoor | www.stio.com | ok | yes | yes | yes | yes | 250 | 4470+ | 80% | match | USD | USD | US | 6 | ban | fail: catalog too large |
| Timbuk2 | outdoor | www.timbuk2.com | ok | yes | yes | yes | yes | 171 | 1027 | 99% | match | - | USD | US | 6 | no_ban | PASS |
| Tortuga | outdoor | www.tortugabackpacks.com | ok | yes | yes | yes | yes | 39 | 43 | 93% | match | USD | USD | US | 6 | no_ban | PASS |
| UCO Gear | outdoor | ucogear.com | ok | yes | yes | yes | yes | 69 | 130 | 85% | match | USD | USD | US | 6 | ban | PASS |
| Velocio | outdoor | velocio.cc | unreachable | - | - | no | no | - | - | - | - | - | - | - | 4 | - | fail: blocked, needed 429 retries |
| Zenbivy | outdoor | zenbivy.com | ok | yes | yes | yes | yes | 73 | 498 | 84% | match | USD | USD | US | 6 | ban | PASS |
| Alpha Paw | pet | www.alphapaw.com | ok | yes | yes | yes | yes | 250 | 11094+ | 100% | match | USD | USD | US | 6 | no_ban | fail: catalog too large |
| Animals Matter | pet | animalsmatter.com | ok | yes | yes | yes | yes | 88 | 1187 | 75% | match | USD | USD | US | 6 | ban | PASS |
| Best Bully Sticks | pet | www.bestbullysticks.com | ok | yes | yes | yes | yes | 116 | 246 | 76% | match | USD | USD | US | 6 | ban | PASS |
| Big Barker | pet | bigbarker.com | ok | yes | yes | yes | yes | 29 | 301 | 73% | match | USD | USD | US | 6 | ban | PASS |
| Canine Styles | pet | www.caninestyles.com | ok | yes | yes | yes | yes | 1000 | 3364+ | 94% | match | USD | USD | US | 15 | ban | fail: catalog too large, excluded category: alcohol, tobacco/vape, needed 429 retries |
| Exotic Nutrition | pet | exoticnutrition.com | ok | yes | yes | yes | yes | 446 | 805 | 91% | match | USD | USD | US | 7 | no_ban | PASS |
| Fable Pets | pet | fablepets.com | ok | yes | yes | yes | yes | 67 | 400 | 80% | match | USD | USD | US | 6 | ban | PASS |
| GUNNER Kennels | pet | gunner.com | ok | yes | yes | yes | yes | 131 | 479 | 83% | match | USD | USD | US | 6 | ban | PASS |
| Impact Dog Crates | pet | www.impactdogcrates.com | ok | yes | yes | yes | yes | 63 | 1818 | 74% | match | USD | USD | US | 6 | ban | PASS |
| Jackson Galaxy | pet | www.jacksongalaxy.com | ok | yes | yes | no | no | - | - | - | - | - | - | - | 2 | - | fail: blocked |
| KOHA Pet | pet | kohapet.com | ok | yes | yes | yes | yes | 60 | 107 | 95% | match | USD | USD | US | 6 | ban | PASS |
| Little Beast | pet | littlebeast.co | ok | yes | yes | yes | yes | 181 | 947 | 67% | match | USD | USD | US | 6 | ban | PASS |
| Lucy & Co. | pet | lucyandco.com | ok | yes | yes | yes | no | - | - | - | - | - | - | - | 2 | - | fail: not shopify |
| Maxbone | pet | www.maxbone.com | ok | yes | yes | yes | yes | 105 | 491 | 90% | match | USD | USD | US | 6 | ban | PASS |
| Mighty Paw | pet | mightypaw.com | ok | yes | yes | yes | yes | 89 | 254 | 57% | match | USD | USD | US | 6 | no_ban | PASS |
| Native Pet | pet | nativepet.com | ok | yes | yes | yes | yes | 52 | 111 | 96% | match | USD | USD | US | 6 | ban | PASS |
| Nulo | pet | nulo.com | ok | yes | yes | yes | no | - | - | - | - | - | - | - | 2 | - | fail: not shopify |
| Open Farm | pet | openfarmpet.com | ok | yes | yes | yes | yes | 248 | 406 | 97% | match | USD | USD | US | 6 | ban | PASS |
| PetLab Co. | pet | thepetlabco.com | ok | yes | yes | yes | no | - | - | - | - | - | - | - | 2 | - | fail: not shopify |
| PETLIBRO | pet | petlibro.com | ok | yes | yes | yes | yes | 111 | 358 | 98% | match | USD | USD | US | 5 | none_found | PASS |
| Redbarn Pet Products | pet | www.redbarn.com | ok | yes | yes | yes | yes | 135 | 451 | 96% | match | USD | USD | US | 6 | ban | PASS |
| Small Pet Select | pet | smallpetselect.com | ok | yes | yes | yes | no | - | - | - | - | - | - | - | 2 | - | fail: not shopify |
| Tactipup | pet | www.tactipup.com | ok | yes | yes | yes | yes | 94 | 1774 | 99% | match | USD | USD | US | 6 | ban | PASS |
| The Foggy Dog | pet | www.thefoggydog.com | ok | yes | yes | yes | yes | - | - | - | match | USD | USD | US | 10 | - | fail: blocked mid-recon, empty catalog, needed 429 retries |
| The Honest Kitchen | pet | www.thehonestkitchen.com | ok | yes | yes | yes | yes | 128 | 210 | 93% | match | USD | USD | US | 6 | no_ban | PASS |
| Travel Cat | pet | yourcatbackpack.com | ok | yes | yes | yes | yes | 109 | 1954 | 85% | match | USD | USD | US | 6 | no_ban | PASS |
| West Paw | pet | www.westpaw.com | ok | yes | yes | yes | yes | 99 | 239 | 88% | match | USD | USD | US | 6 | ban | PASS |
| Wild One | pet | wildone.com | ok | yes | yes | yes | yes | 56 | 341 | 53% | match | USD | USD | US | 6 | ban | PASS |
| Bandolier | tech_accessories | www.bandolierstyle.com | ok | yes | yes | yes | yes | 484 | 2294 | 76% | match | USD | USD | US | 7 | no_ban | fail: excluded category: alcohol |
| Baseus (US) | tech_accessories | www.baseus.com | ok | yes | yes | yes | yes | 241 | 427 | 37% | match | USD | USD | US | 6 | ban | PASS |
| Case-Mate | tech_accessories | case-mate.com | ok | yes | yes | yes | yes | 1011 | 1353 | 89% | match | USD | USD | US | 10 | ban | fail: excluded category: weapons |
| Casely | tech_accessories | casely.com | unreachable | - | - | no | no | - | - | - | - | - | - | - | 4 | - | fail: blocked |
| ChubbyCable | tech_accessories | chubbycable.com | ok | yes | yes | yes | yes | 250 | 8025+ | 98% | match | USD | USD | HK | 6 | ban | fail: catalog too large |
| Elevation Lab | tech_accessories | elevationlab.com | unreachable | - | - | no | no | - | - | - | - | - | - | - | 4 | - | fail: blocked |
| Grovemade | tech_accessories | grovemade.com | ok | yes | yes | no | no | - | - | - | - | - | - | - | 2 | - | fail: blocked |
| Keychron | tech_accessories | www.keychron.com | ok | yes | yes | yes | yes | 500 | 3266+ | 40% | match | USD | USD | US | 7 | no_ban | fail: catalog too large |
| Lume Cube | tech_accessories | lumecube.com | ok | yes | yes | yes | yes | 128 | 143 | 96% | match | USD | USD | US | 6 | ban | PASS |
| MagBak | tech_accessories | magbak.com | ok | yes | yes | yes | yes | 85 | 404 | 70% | match | - | USD | US | 6 | ban | PASS |
| MOFT (US) | tech_accessories | www.moft.com | ok | yes | yes | yes | yes | 94 | 1219 | 84% | match | USD | USD | US | 6 | ban | PASS |
| Nimble | tech_accessories | www.gonimble.com | ok | yes | yes | yes | yes | 58 | 173 | 92% | match | USD | USD | US | 6 | ban | PASS |
| Nomad | tech_accessories | nomadgoods.com | ok | yes | yes | yes | no | - | - | - | - | - | - | - | 2 | - | fail: not shopify |
| Oh Snap | tech_accessories | ohsnap.com | ok | yes | yes | yes | yes | 38 | 320 | 49% | match | USD | USD | US | 6 | ban | PASS |
| Pela | tech_accessories | pelacase.com | ok | yes | yes | yes | yes | 2500 | 3204+ | 100% | match | USD | USD | US | 15 | ban | fail: catalog too large, excluded category: alcohol |
| PolarPro | tech_accessories | www.polarpro.com | ok | yes | yes | yes | yes | 267 | 899 | 69% | match | USD | USD | US | 7 | no_ban | PASS |
| Rokform | tech_accessories | www.rokform.com | ok | yes | yes | yes | yes | 184 | 195 | 97% | match | USD | USD | US | 6 | ban | PASS |
| Sabrent | tech_accessories | sabrent.com | ok | yes | yes | yes | yes | 721 | 722 | 26% | match | USD | USD | US | 8 | no_ban | fail: excluded category: tobacco/vape |
| Satechi | tech_accessories | satechi.com | ok | yes | yes | yes | yes | 146 | 321 | 65% | match | USD | USD | US | 6 | ban | PASS |
| Studio Neat | tech_accessories | www.studioneat.com | ok | yes | yes | yes | yes | 50 | 157 | 57% | match | USD | USD | US | 6 | ban | PASS |
| Totallee | tech_accessories | totallee.com | missing-4xx | yes | yes | yes | no | - | - | - | - | - | - | - | 2 | - | fail: not shopify |
| Twelve South | tech_accessories | www.twelvesouth.com | ok | yes | yes | yes | yes | 140 | 155 | 96% | match | USD | USD | US | 6 | ban | PASS |
| Ugmonk | tech_accessories | ugmonk.com | ok | yes | yes | yes | yes | 180 | 242 | 92% | match | USD | USD | US | 6 | ban | PASS |
| Velvet Caviar | tech_accessories | velvetcaviar.com | ok | yes | yes | yes | yes | 500 | 3248+ | 64% | match | USD | USD | US | 7 | ban | fail: catalog too large |
| VIVO | tech_accessories | vivo-us.com | ok | yes | yes | yes | yes | 498 | 1116 | 93% | match | USD | USD | US | 7 | no_ban | PASS |
| WANDRD | tech_accessories | www.wandrd.com | ok | yes | yes | yes | yes | 279 | 378 | 71% | match | USD | USD | US | 7 | ban | PASS |
| Wildflower Cases | tech_accessories | www.wildflowercases.com | ok | yes | yes | yes | yes | 500 | 4855+ | 75% | match | USD | USD | US | 7 | ban | fail: catalog too large |
| Workrite Ergonomics | tech_accessories | shop.workriteergo.com | ok | yes | yes | yes | yes | 146 | 619 | 99% | match | - | USD | US | 6 | no_ban | PASS |
| Bumkins | toys_kids | www.bumkins.com | ok | yes | yes | yes | yes | 486 | 490 | 76% | match | USD | USD | US | 7 | ban | PASS |
| Colugo | toys_kids | colugo.com | ok | yes | yes | yes | yes | 40 | 46 | 100% | match | USD | USD | US | 6 | ban | PASS |
| Copper Pearl | toys_kids | copperpearl.com | ok | yes | yes | yes | yes | 1250 | 3842+ | 61% | match | USD | USD | US | 10 | ban | fail: catalog too large |
| Crazy Aaron's | toys_kids | www.crazyaarons.com | ok | yes | yes | yes | yes | 225 | 235 | 32% | match | USD | USD | US | 6 | ban | PASS |
| eeBoo | toys_kids | eeboo.com | ok | yes | yes | yes | yes | 450 | 459 | 96% | match | USD | USD | US | 7 | ban | PASS |
| Exploding Kittens | toys_kids | www.explodingkittens.com | ok | yes | yes | yes | yes | 134 | 215 | 41% | match | USD | USD | US | 6 | ban | PASS |
| ezpz | toys_kids | ezpzfun.com | ok | yes | yes | yes | yes | 124 | 515 | 97% | match | - | USD | US | 6 | ban | PASS |
| Frida | toys_kids | frida.com | ok | yes | yes | yes | yes | 184 | 241 | 92% | match | - | USD | US | 6 | ban | PASS |
| Gathre | toys_kids | gathre.com | ok | yes | yes | yes | yes | 248 | 882 | 69% | match | USD | USD | US | 6 | ban | PASS |
| Guardian Bikes | toys_kids | guardianbikes.com | ok | yes | yes | yes | yes | 40 | 231 | 99% | match | - | USD | US | 6 | ban | PASS |
| Happiest Baby | toys_kids | www.happiestbaby.com | ok | yes | yes | yes | no | - | - | - | - | - | - | - | 2 | - | fail: not shopify |
| Jiggy | toys_kids | jiggypuzzles.com | ok | yes | yes | yes | yes | 619 | 646 | 98% | match | USD | USD | US | 8 | ban | PASS |
| Kids2 | toys_kids | shop.kids2.com | ok | yes | yes | yes | yes | 647 | 647 | 42% | match | USD | USD | US | 8 | ban | PASS |
| Kyte Baby | toys_kids | kytebaby.com | ok | yes | yes | yes | yes | 500 | 3044+ | 96% | match | USD | USD | US | 7 | ban | fail: catalog too large |
| Lalo | toys_kids | www.meetlalo.com | ok | yes | yes | yes | yes | 99 | 1172 | 90% | match | USD | USD | US | 6 | ban | PASS |
| Little Sleepies | toys_kids | littlesleepies.com | ok | yes | yes | yes | yes | 500 | 3210+ | 25% | match | USD | USD | US | 7 | ban | fail: catalog too large |
| Lovevery | toys_kids | lovevery.com | ok | yes | yes | yes | no | - | - | - | - | - | - | - | 2 | - | fail: not shopify |
| Nested Bean | toys_kids | www.nestedbean.com | ok | yes | yes | yes | yes | 16 | 137 | 59% | match | USD | USD | US | 6 | ban | PASS |
| Newton Baby | toys_kids | www.newtonbaby.com | ok | yes | yes | yes | yes | 81 | 428 | 86% | match | USD | USD | US | 6 | no_ban | PASS |
| Nugget | toys_kids | nuggetcomfort.com | ok | yes | yes | yes | yes | 157 | 294 | 98% | match | USD | USD | US | 6 | no_ban | PASS |
| OOLY | toys_kids | www.ooly.com | ok | yes | yes | yes | yes | 339 | 342 | 96% | match | USD | USD | US | 7 | ban | PASS |
| Piecework Puzzles | toys_kids | pieceworkpuzzles.com | ok | yes | yes | yes | yes | 732 | 966 | 75% | match | USD | USD | US | 8 | ban | fail: excluded category: alcohol |
| Plus-Plus USA | toys_kids | www.plusplususa.com | ok | yes | yes | yes | yes | 603 | 658 | 98% | match | USD | USD | US | 8 | ban | PASS |
| Posh Peanut | toys_kids | poshpeanut.com | ok | yes | yes | yes | yes | 750 | 4040+ | 67% | match | USD | USD | US | 8 | ban | fail: catalog too large |
| Solly Baby | toys_kids | sollybaby.com | ok | yes | yes | yes | yes | 151 | 474 | 68% | match | USD | USD | US | 6 | ban | PASS |
| Tegu | toys_kids | tegu.com | ok | yes | yes | yes | yes | 46 | 310 | 8% | match | - | USD | US | 6 | ban | PASS |

## Notes

- **Again Faster**: no JSON-LD offer currency on product page
- **Arctic Fox**: /products.json: http 404, text/html
- **Audio Advice**: stopped: retries exhausted: http 429
- **BAGGU**: /products.json: http 404, text/html; charset=utf-8
- **Billy Reid**: stopped: blocked: cloudflare challenge
- **Canyon Coffee**: /products.json: http 404, text/html; charset=utf-8
- **Casely**: stopped: robots.txt unreachable: retries exhausted: network error: ConnectError
- **Chamberlain Coffee**: /products.json: http 200, text/html
- **Dagne Dover**: no JSON-LD offer currency on product page
- **Davidson's Organic Tea**: stopped: retries exhausted: http 429
- **Dirty Labs**: no JSON-LD offer currency on product page
- **Dr. Dennis Gross Skincare**: /products.json: http 410, text/html;charset=UTF-8
- **Dusen Dusen**: stopped: robots.txt unreachable: retries exhausted: network error: ConnectError
- **Elevation Lab**: stopped: robots.txt unreachable: retries exhausted: network error: ConnectTimeout
- **ezpz**: no JSON-LD offer currency on product page
- **FrictionLabs**: no JSON-LD offer currency on product page
- **Frida**: no JSON-LD offer currency on product page
- **Grovemade**: stopped: blocked: cloudflare block
- **Guardian Bikes**: no JSON-LD offer currency on product page
- **Happiest Baby**: /products.json: http 200, text/html; charset=utf-8
- **Harney & Sons**: stopped: blocked: cloudflare challenge
- **Hawkins New York**: stopped: retries exhausted: http 429
- **iROCKER**: /products.json: http 404, text/html
- **Jackson Galaxy**: stopped: blocked: cloudflare challenge
- **Jeffree Star Cosmetics**: no JSON-LD offer currency on product page
- **Jungalow**: /products.json: http 404, text/html;charset=utf-8
- **Keap**: no JSON-LD offer currency on product page
- **KEF (US)**: product .js: http 404; product page: http 404
- **Kelty**: stopped: blocked: cloudflare challenge
- **Lashify**: no JSON-LD offer currency on product page
- **Leeway Home**: stopped: blocked: cloudflare challenge
- **LeSportsac**: stopped: retries exhausted: http 429
- **Living.Fit**: stopped: retries exhausted: http 429
- **Lovevery**: /products.json: http 404, text/html; charset=utf-8
- **Lucy & Co.**: /products.json: http 404, text/html
- **Lume Deodorant**: /products.json: http 200, text/html
- **MagBak**: no JSON-LD offer currency on product page
- **Nomad**: /products.json: http 404, text/html
- **Nulo**: /products.json: http 404, text/html
- **Onyx Coffee Lab**: no JSON-LD offer currency on product page
- **Otherland**: no JSON-LD offer currency on product page
- **Outerknown**: stopped: retries exhausted: http 429
- **Oveja Negra**: no JSON-LD offer currency on product page
- **PetLab Co.**: /products.json: http 404, text/html; charset=utf-8
- **rabbit**: no JSON-LD offer currency on product page
- **Revival Rugs**: /products.json: http 404, text/html
- **Rockford Fosgate**: /products.json: http 404, text/html; charset=utf-8
- **Rocky Talkie**: product .js: http 404; product page: http 404
- **SEY Coffee**: stopped: retries exhausted: http 429; no JSON-LD offer currency on product page
- **Slowdown Studio**: product .js: http 404; product page: http 404
- **Small Pet Select**: /products.json: http 404, text/html; charset=UTF-8
- **Smith Teamaker**: no JSON-LD offer currency on product page
- **Stone Candles**: stopped: retries exhausted: http 429
- **SuitShop**: /products.json: http 404, text/html; charset=utf-8
- **Sweet Water Decor**: product .js: http 404
- **Tegu**: no JSON-LD offer currency on product page
- **The Foggy Dog**: stopped: retries exhausted: http 429
- **The Republic of Tea**: stopped: retries exhausted: http 429
- **Tifosi Optics**: no JSON-LD offer currency on product page
- **Timbuk2**: no JSON-LD offer currency on product page
- **Totallee**: /products.json: http 404, text/html
- **Turntable Lab**: stopped: retries exhausted: http 429
- **Turtle Beach**: /products.json: http 404, text/html
- **U-Turn Audio**: no JSON-LD offer currency on product page
- **Velocio**: stopped: robots.txt unreachable: retries exhausted: http 429
- **WiiM**: stopped: blocked: http 403
- **Workrite Ergonomics**: no JSON-LD offer currency on product page
- **World Wide Stereo**: stopped: retries exhausted: http 429

## Terms of Service

`/policies/terms-of-service`, at most 2 requests per store, read only where robots.txt allows it: ban 197, no_ban 45, none_found 14.

| store | terms | source | first matching sentence |
|---|---|---|---|
| &Collar | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the service is provided, without express written permission by us. |
| Bandit Running | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the service is provided, without express written permission by us. |
| Birdwell | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the service is provided, without express written permission by us. |
| CALPAK | ban | read | Without limiting the foregoing, you may not use “bots,” spiders or intelligent agent software (or similar technologies) for any purposes other than accessing publicly posted portions of the Website and only for purposes consistent with these Terms. |
| Criquet Shirts | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the service is provided, without express written permission by us. |
| Dagne Dover | no_ban | read | - |
| Defy Bags | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the service is provided, without express written permission by us. |
| Duck Head | ban | read | You may not modify, copy, publish, display, transmit, adapt or in any way exploit the materials on our site. |
| Elizabeth Suzann | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the Service is provided, without express written permission by us. |
| Feat Clothing | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the service is provided, without express written permission by us. |
| Free Fly Apparel | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the service is provided, without express written permission by us. |
| Gramicci | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the service is provided, without express written permission by us. |
| Greats | ban | read | Except as expressly provided in these Terms, you must not reproduce, distribute, modify, create derivative works of, publicly display, publicly perform, republish, download, store, or transmit any of the Content or Marks on our Services without our express written permission. |
| Imogene + Willie | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the service is provided, without express written permission by us. |
| Julbo USA | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the Service is provided, without express written permission by us. |
| Kizik | ban | read | In addition to other prohibitions as set forth in the Terms of Service, you are prohibited from … rsonal information of others; (i) to spam, phish, pharm, pretext, spider, crawl, or scrape; (j) for any obscene or immoral purpose; or (k) in any manner intended to interfere with or circumvent the … |
| Knockaround | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the service is provided, without express written permission by us. |
| Koio | ban | read | You may not: (a) resell or make any commercial use of this Site or any of the contents of this … contents of this Site in any form or by any means; or (d) use any data mining, bots, spiders, automated tools or similar data gathering and extraction methods on the contents of the Site or to … |
| Lo & Sons | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the service is provided, without express written permission by us. |
| Lunya | ban | read | You may not modify, copy, reproduce, republish, upload, post, transmit, disseminate, reverse engineer, reverse assemble, sell or distribute in any way any material from this site, including, without limitation, code and software. |
| OluKai | no_ban | read | - |
| Pistola Denim | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the service is provided, without express written permission by us. |
| rabbit | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the service is provided, without express written permission by us. |
| Richer Poorer | none_found | no policy text | - |
| Scout Bags | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the Service is provided, without express written permission by us. |
| Seychelles Footwear | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the service is provided, without express written permission by us. |
| State & Liberty | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the Site through which the Service is provided, without express written permission by us. |
| Sunski | no_ban | read | - |
| Tifosi Optics | ban | read | You may not use automated means (including bots, scrapers, spiders, data mining tools, crawlers, or similar technologies) to access the Services, or circumvent any technical measures we employ to protect the Services. |
| 1MORE (US) | ban | read | You will not, nor will you assist or direct any third person to: (i) extract, separate, remove or … otherwise copy the 1MORE Content; (ii) disassemble, decompile, reverse engineer or otherwise convert any part of the 1MORE Content to source code or a human-perceivable form; (iii) adapt, modify … |
| Altec Lansing | no_ban | read | - |
| Apos Audio | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the service is provided, without express written permission by us. |
| Audeze | no_ban | read | - |
| Audio46 | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the service is provided, without express written permission by us. |
| Bloom Audio | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the service is provided, without express written permission by us. |
| BOSS Audio Systems | ban | read | You may not copy, modify, distribute or use our content or trademarks without our written permission, except as allowed by our brand assets guidelines. |
| Cleer Audio | none_found | http 404 | - |
| Emotiva | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the service is provided, without express written permission by us. |
| Fosi Audio | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the service is provided, without express written permission by us. |
| Grado Labs | no_ban | read | - |
| Headphones.com | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the service is provided, without express written permission by us. |
| HyperX | no_ban | read | - |
| KEF (US) | none_found | http 404 | - |
| Master & Dynamic | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the service is provided, without express written permission by us. |
| Shokz | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the service is provided, without express written permission by us. |
| Skullcandy | ban | read | Subject to these Terms of Use, Skullcandy hereby grants you a limited, revocable, non-transferable … rpose of shopping for personal items sold on the Website and not for any commercial use or use on behalf of any third party, except as explicitly permitted by Skullcandy in advance. |
| Soundcore (US) | none_found | robots.txt disallows /policies/terms-of-service | - |
| Sundown Audio | no_ban | read | - |
| SVS | ban | read | You hereby agree not to modify, copy, reproduce, republish, upload, post, transmit, or distribute any portion of the Website or any contents contained on the Website without the prior expressed written consent of SVS. |
| Tivoli Audio | no_ban | read | - |
| TREBLAB | ban | read | You may not reproduce, duplicate, copy, sell, resell, or exploit any portion of our services, products, or content without our prior written permission. |
| TURTLEBOX | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the service is provided, without express written permission by us. |
| U-Turn Audio | ban | read | If you send us comments, reviews, ideas, suggestions, or other materials ("submissions"), you agree that we may edit, copy, publish, distribute, translate, and otherwise use them in any medium, without restriction or payment. |
| Upscale Audio | no_ban | read | - |
| Victrola | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the service is provided, without express written permission by us. |
| Wet Sounds | ban | read | Using any manual process or means to monitor or copy any of the material on this Website or for any other unauthorized purpose; |
| Beauty Bakerie | no_ban | read | - |
| Beautyblender | no_ban | read | - |
| Besame Cosmetics | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the service is provided, without express written permission by us. |
| Cocokind | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the service is provided, without express written permission by us. |
| Crown Affair | ban | read | You may not reproduce, distribute, publicly display, or publicly perform the App or any part of the Service. |
| Derma E | no_ban | read | - |
| Dermalogica | ban | read | Unless otherwise permitted by these Terms, you may not copy, distribute, display, transmit, perform, modify, publish or create derivative works from the Site or its images, text, graphics, user interfaces, designs, photographs, trademarks, logos, sounds, music, artwork and computer code (“Content”). |
| Dose of Colors | ban | read | Engage in unauthorized spidering, scraping or harvesting of content or personal information, or use any other unauthorized automated means to compile information; |
| Fenty Beauty | ban | read | You may not download, copy, reproduce, distribute, transmit, broadcast, display, perform, … reproduce, publish, sell, license, create derivative works from, or otherwise exploit any Company Content, the Marks, software, products or service contained on the Website without the prior written … |
| It's a 10 Haircare | ban | read | You agree to not sell, license, rent, or otherwise use or exploit any Content for commercial use or in violate any third-party intellectual property ownership and rights. |
| Jeffree Star Cosmetics | no_ban | read | - |
| Jones Road | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the service is provided, without express written permission by us. |
| Juice Beauty | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the service is provided, without express written permission by us. |
| KASH Beauty | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the service is provided, without express written permission by us. |
| Lashify | ban | read | You may not commit fraud; infringe intellectual property or privacy rights; impersonate others; … interfere with security or operation; bypass access restrictions; scrape or harvest content or personal information without authorization; or send unsolicited bulk communications through the Services. |
| Makeup by Mario | ban | read | This limited license does not include the right to: (a) frame or utilize framing techniques to … hidden text" utilizing any and/or all Content; or (g) use software robots, spiders, crawlers, or similar data gathering and extraction tools, or take any other action that may impose an unreasonable … |
| Milani Cosmetics | no_ban | read | - |
| Murad | ban | read | Unless otherwise permitted by these Terms, you may not copy, distribute, display, transmit, perform, modify, publish or create derivative works from the Site or its images, text, graphics, user interfaces, designs, photographs, trademarks, logos, sounds, music, artwork and computer code (“Content”). |
| Nécessaire | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the service is provided, without express written permission by us. |
| Pacifica Beauty | ban | read | This limited license does not include the right to: (a) frame or utilize framing techniques to … any other “hidden text” utilizing any Content; or (g) use software robots, spiders, crawlers, or similar data gathering and extraction tools, or take any other action that may impose an unreasonable … |
| Sigma Beauty | no_ban | read | - |
| Soko Glam | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the service is provided, without express written permission by us. |
| Sol de Janeiro | ban | read | Except as expressly permitted in these Terms, you may not use, reproduce, distribute, reverse engineer, modify, copy, publish, display, transmit, adapt, frame, link, rent, lease, loan, sell, license or in any way exploit for profit the content of the Site. |
| Stila Cosmetics | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the service is provided, without express written permission by us. |
| Sunday Riley | ban | read | SRMS grants you permission to use the SRMS Site as set forth in these Terms, provided that and for … so long as (i) you use the Site solely for your personal, non-commercial use; (ii) except as expressly permitted in these Terms, you do not download, reproduce, redistribute, retransmit, … |
| tarte cosmetics | ban | read | Use any manual process to monitor or copy any of the material on the Website, or for any other purpose not expressly authorized in these Terms without our prior written consent. |
| Tata Harper | ban | read | Except for accessing the Website in accordance with these Terms of Use for personal and internal … purposes, you may not use, modify, copy, reproduce, republish, upload, post, transmit, decompile, reverse engineer, disassemble, distribute or otherwise exploit any of the Content, in whole or in … |
| The INKEY List | ban | read | In the unlikely event that the price and/or description of an item listed on the Website has been incorrectly advertised, we will not be under any obligation to sell or provide those Goods to you. |
| Truly Beauty | ban | read | By submitting suggestions or other feedback regarding our Services ("Contributions") in any way to … ou irrevocably non-exclusively license to Truly Beauty rights to exploit your Contributions; and (f) you are not entitled to any compensation or reimbursement of any kind from Truly Beauty under … |
| Tubby Todd Bath Co. | ban | read | Data Scraping Prohibited. |
| Tula Skincare | no_ban | read | - |
| Westman Atelier | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the service is provided, without express written permission by us. |
| Counter Culture Coffee | ban | read | However, such license is subject to these Terms and does not include any right to, and you shall … uses of the Sites or Content, or any portion thereof, (d) use any data mining, robots or similar data gathering or extraction methods, (e) download (other than the page caching) any portion of the … |
| Dark Matter Coffee | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the service is provided, without express written permission by us. |
| Death Wish Coffee | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the service is provided, without express written permission by us. |
| Equator Coffees | none_found | robots.txt disallows /policies/terms-of-service | - |
| Heine Brothers' Coffee | no_ban | read | - |
| Intelligentsia | ban | read | When you submit material to us (including comments, photographs, and other content) such as through … uding the unlimited right to sublicense to others) right to use, copy, publicly perform, display, distribute and create derivative works from any content or material you submit; (c) represent … |
| Jade Leaf Matcha | ban | read | You must not reproduce, distribute, modify, create derivative works of, publicly display, publicly perform, republish, download, store or transmit any of the material on our Website, except as follows: |
| Kettl | none_found | robots.txt disallows /policies/terms-of-service | - |
| La Colombe | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the Service is provided, without express written permission by us. |
| Numi Organic Tea | no_ban | read | - |
| Onyx Coffee Lab | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the service is provided, without express written permission by us. |
| Partners Coffee | ban | read | You may not reproduce, distribute, modify, or use any content from the Site for commercial purposes without our prior written consent. |
| Rishi Tea & Botanicals | ban | read | • Attempt to hide or direct, facilitate or assist any third party in hiding your IP address to … dropped by Seller, you are hiding or switching your IP address to scrape or collect data and content from this Site, or you have received a cease and desist or other correspondence from Seller … |
| Sightglass Coffee | ban | read | You may not reproduce, distribute, modify, or otherwise exploit any content without prior written consent. |
| Smith Teamaker | ban | read | Such Content may be displayed, reformatted, and printed by you for your personal, non-commercial use only in connection with our product offerings in accordance with the TOU and not for distribution in any medium. |
| Snarky Tea | ban | read | You agree not to reproduce, duplicate, copy, sell, resell, or exploit any portion of the Service without express written permission by us. |
| Stumptown Coffee | ban | read | When you submit material to us (including comments, photographs, and other content) such as through … uding the unlimited right to sublicense to others) right to use, copy, publicly perform, display, distribute and create derivative works from any content or material you submit; (c) represent … |
| Temple Coffee Roasters | ban | read | This is the grant of a license, not a transfer of title, and under this license you may not: modify … or copy the materials; use the materials for any commercial purpose, or for any public display (commercial or non-commercial); attempt to decompile or reverse engineer any software contained on … |
| The Tea Spot | ban | read | You must not reproduce, distribute, modify, create derivative works of, publicly display, publicly perform, republish, download, store, or transmit any of the material on the Services without our prior written consent. |
| Verve Coffee Roasters | no_ban | read | - |
| Again Faster | ban | read | Use any robot, spider, crawler, scraper or other automated means or interface not provided by us to access the Sites or to extract data; |
| Bala | none_found | robots.txt disallows /policies/terms-of-service | - |
| Bells of Steel USA | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the service is provided, without express written permission by us. |
| Crossrope | ban | read | Do Not Sell My Data |
| Feetures | ban | read | Except as otherwise expressly provided in these terms and conditions, you may not copy, distribute, … transmit, display, perform, reproduce, publish, license, modify, rewrite, create derivative works from, transfer, or sell any material contained on the Web site without the prior consent of the … |
| FlipBelt | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the service is provided, without express written permission by us. |
| Fringe Sport | no_ban | read | - |
| Gaiam | ban | read | violates any intellectual property or other proprietary right of any third party, including Content … that promotes an illegal or unauthorized copy of another person's copyrighted work, such as providing pirated computer programs or links to them, providing information to circumvent … |
| Gymreapers | ban | read | Accounts registered by bots or any other automated methods are not permitted. |
| Hugger Mugger | ban | read | Except as expressly provided in these Terms of Use, no part of the Site and no Content or Marks may … transmitted, distributed, sold, licensed, or otherwise exploited for any commercial purpose whatsoever, without our express prior written permission. |
| Hyperice | ban | read | You may not, under any circumstances, (a) modify the information on this Site or use it for any … commercial purpose, or any public display, performance, sale or rental; (b) decompile, reverse engineer, or disassemble the any part of this Site or its content; or (c) remove any copyright, … |
| KANE Footwear | ban | read | (b) Prohibited activities include sharing private info, obscene/indecent content, … icitation, spam, claiming Kane® endorsement, harvesting personal data, scraping/data-mining, IP infringement, removing notices, disrupting services, uploading malware, offering illegal/rights-violating … |
| Life Fitness Shop | ban | read | Information on the Site does not constitute a binding offer to buy or sell any products or services or to make any products or services available in your area. |
| Manduka | ban | read | You will not use any automated means – such as any robot, spider, etc. – to access the Services or extract other users’ information. |
| Nathan Sports | none_found | robots.txt disallows /policies/terms-of-service | - |
| OOFOS | no_ban | read | - |
| Peak Pilates | none_found | http 404 | - |
| PowerBlock | ban | read | Use any manual process to monitor or copy any of the material on the Site or for any other unauthorized purpose without our prior written consent. |
| PRx Performance | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the Service is provided, without express written permission by us. |
| REP Fitness | none_found | robots.txt disallows /policies/terms-of-service | - |
| SOLE Fitness | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the Service is provided, without express written permission by us. |
| Sunny Health & Fitness | ban | read | You may not circumvent, disable, alter or manipulate any content protection system or digital … to access, monitor or copy, any element of the SH&F Sites using a robot, spider, scraper or other automated means or manual process. |
| Torque Fitness | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the service is provided, without express written permission by us. |
| TRX Training | ban | read | Subject to your compliance with these Terms and solely for as long as you are permitted by us to … TRX Services to Devices you own or control for your personal, non-commercial use of the TRX Services and for no other purpose whatsoever, provided you keep intact all copyright and other … |
| Yoloha Yoga | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the service is provided, without express written permission by us. |
| Areaware | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the service is provided, without express written permission by us. |
| Bearaby | none_found | robots.txt disallows /policies/terms-of-service | - |
| Bee's Wrap | ban | read | You may not reproduce (except as noted above), publish, transmit, distribute, display, modify, create derivative works from, sell or participate in any sale of, or exploit in any way, in whole or in part, any of the Contents, the Site, or any related software. |
| Bloomist | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the service is provided, without express written permission by us. |
| Branch Basics | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the service is provided, without express written permission by us. |
| Candle-lite | ban | read | You are authorized to browse the site and print and download copies of material on the site for your personal, non-commercial use only, so long as you do not remove any copyright or other notices that appear on the material you print or download. |
| Dirty Labs | ban | read | Except as expressly authorized by Dirty Labs, you agree not to modify, copy, frame, scrape, rent, … lease, loan, sell, distribute or create derivative works based on the Service or the Service Content, in whole or in part, except that the foregoing does not apply to your own User Content (as … |
| Field Company | no_ban | read | - |
| GIR | no_ban | read | - |
| Homesick | ban | read | Use any manual process to monitor or copy any of the material on the Website, or for any other purpose not expressly authorized in these Terms of Use, without our prior written consent. |
| Keap | no_ban | read | - |
| Molly's Suds | ban | read | You may not display or reproduce the Marks in any manner without the prior written consent of Molly’s Suds, and you may not remove or otherwise modify in any manner any trademark notices from any content offered or received through the Site. |
| Morrow Soft Goods | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the service is provided, without express written permission by us. |
| Olive Ateliers | ban | read | Credit card information is always encrypted during transfer over networks.You agree not to … reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the service is provided, without … |
| Onsen | no_ban | read | - |
| Otherland | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the service is provided, without express written permission by us. |
| P.F. Candle Co. | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the service is provided, without express written permission by us. |
| Peacock Alley | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the service is provided, without express written permission by us. |
| Schoolhouse | no_ban | read | - |
| Sheets & Giggles | no_ban | read | - |
| Sijo | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the Service is provided, without express written permission by us. |
| Slowdown Studio | ban | read | You must not reproduce, distribute, modify, create derivative works of, publicly display, publicly perform, republish, download, store, or transmit any of the material on the Services without our prior written consent. |
| Smithey Ironware | ban | read | This license does not allow you reproduce, modify, duplicate, copy, sell, resell, distribute, transmit, or otherwise exploit (for any commercial purpose or otherwise) any part of the Website—including the Content of other users—unless you first obtain our written permission. |
| Sweet Water Decor | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the service is provided, without express written permission by us. |
| Weezie | ban | read | You agree not to engage in any of the following prohibited activities: (i) copying, distributing, … , including without limitation by any automated or non-automated “scraping”; (ii) using any automated system, including without limitation “robots,” “spiders,” “offline readers,” etc., to access … |
| Year & Day | ban | read | However, you shall not: a) reproduce, duplicate, copy, sell or otherwise exploit the Website or any … er content (“Site Content”) for any commercial purpose; b) use a robot, spider or data mining or extraction tool or process to monitor, extract or copy Site Content; c) use any meta tags, search … |
| Aer | none_found | http 404 | - |
| Big Agnes | no_ban | read | - |
| BÉIS | ban | read | You agree that you will not: (i) use the Site for any political or commercial purpose (including, … without limitation, for purposes of advertising, soliciting funds, collecting product prices, and selling products); (ii) use any meta tags or any other “hidden text” utilizing any Trademarks; … |
| Darn Tough | ban | read | You may not reproduce, distribute, modify, display, or create derivative works from any Site or product packaging content without CHM's prior written authorization. |
| Eagle Creek | ban | read | You agree not to engage in any of the following prohibited activities: (i) copying, distributing, … y automated or non-automated means, including without limitation “scraping”; (ii) using any automated system, including without limitation “robots,” “spiders,” “offline readers,” etc., to access … |
| FrictionLabs | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the service is provided, without express written permission by us. |
| Goal Zero | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the service is provided, without express written permission by us. |
| Gossamer Gear | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the service is provided, without express written permission by us. |
| Grand Trunk | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the service is provided, without express written permission by us. |
| GSI Outdoors | ban | read | You agree to not reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the service is provided, without written permission by us. |
| Helinox | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the service is provided, without express written permission by us. |
| HEST | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the service is provided, without express written permission by us. |
| HydraPak | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the service is provided, without express written permission by us. |
| Hyperlite Mountain Gear | none_found | robots.txt disallows /policies/terms-of-service | - |
| Ibex | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the service is provided, without express written permission by us. |
| Janji | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the service is provided, without express written permission by us. |
| Ornot | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the service is provided, without express written permission by us. |
| Oveja Negra | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the Service is provided, without express written permission by us. |
| Pacsafe | ban | read | Unless otherwise provided by applicable laws and regulations, any questions, comments, reviews, or … all be deemed non-confidential and Pacsafe shall be free to use, reproduce, disclose and distribute in any manner without limitation. |
| Paravel | no_ban | read | - |
| Rocky Talkie | ban | read | Use any manual process to monitor or copy any of the material on the Website, or for any other purpose not expressly authorized in these Terms of Service, without our prior written consent. |
| Sierra Designs | ban | read | You may not copy, modify, distribute, or commercially exploit any content without written permission. |
| Six Moon Designs | ban | read | You agree not to reproduce, duplicate, copy, sell, resell, or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the service is provided, without express written permission by us. |
| Stio | ban | read | You will not, and will not permit any third party to: (a) alter, modify, reproduce, or create … derivative works of any Content; (b) distribute, sell, resell, lend, loan, lease, license, sublicense, or transfer any Content; or (c) alter, obscure or remove any copyright, trademark, or any other … |
| Timbuk2 | no_ban | read | - |
| Tortuga | no_ban | read | - |
| UCO Gear | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the service is provided, without express written permission by us. |
| Zenbivy | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the service is provided, without express written permission by us. |
| Alpha Paw | no_ban | read | - |
| Animals Matter | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the service is provided, without express written permission by us. |
| Best Bully Sticks | ban | read | If, at our request, you send certain specific submissions (for example contest entries) or without … , you agree that we may, at any time, without restriction, edit, copy, publish, distribute, translate and otherwise use in any medium any comments that you forward to us. |
| Big Barker | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the service is provided, without express written permission by us. |
| Canine Styles | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the service is provided, without express written permission by us. |
| Exotic Nutrition | no_ban | read | - |
| Fable Pets | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the service is provided, without express written permission by us. |
| GUNNER Kennels | ban | read | in any manner transmit or submit any content to which you do not have the lawful right to copy, transmit, and display (including any content that would violate any confidentiality or fiduciary obligations that you might have with respect to the content); |
| Impact Dog Crates | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the Service is provided, without express written permission by us. |
| KOHA Pet | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the service is provided, without express written permission by us. |
| Little Beast | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the service is provided, without express written permission by us. |
| Maxbone | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the service is provided, without express written permission by us. |
| Mighty Paw | no_ban | read | - |
| Native Pet | ban | read | You agree not to sell, resell, reproduce, duplicate, distribute, copy or use for any commercial purposes any portion of the Offerings, or use of or access to this Site or Offerings provided. |
| Open Farm | ban | read | INTENDED USE OF OUR SITE: The Site is intended for personal, non-commercial use and may not be exploited in connection with any business or commercial purpose, even for non-profits, without the prior express written permission of Open Farm. |
| PETLIBRO | none_found | robots.txt disallows /policies/terms-of-service | - |
| Redbarn Pet Products | ban | read | a) Redbarn reserves the right to disqualify any contestant at any time for exhibiting any of the … rchasing votes, using backup or multiple account or using spam or bots to influence voting practices), creation of spam on contest resources, or other behaviors and abuses of contest privilege to … |
| Tactipup | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the service is provided, without express written permission by us. |
| The Honest Kitchen | no_ban | read | - |
| Travel Cat | no_ban | read | - |
| West Paw | ban | read | You hereby agree not to modify, copy, reproduce, republish, upload, post, transmit, or distribute any portion of the Website or any contents contained on the Website without the prior expressed written consent of West Paw. |
| Wild One | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the service is provided, without express written permission by us. |
| Bandolier | no_ban | read | - |
| Baseus (US) | ban | read | You must not use the Service to copy, store, host, transmit, send, use, publish or distribute any material which consists of (or is linked to) any spyware, computer virus, Trojan horse, worm, keystroke logger, rootkit or other malicious computer software. |
| Case-Mate | ban | read | You are not permitted to publish, manipulate, distribute or otherwise reproduce, in any format, any of the content or copies of the content supplied to you or which appears on this Website nor may you use any such content in connection with any business or commercial enterprise. |
| ChubbyCable | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the service is provided, without express written permission by us. |
| Keychron | no_ban | read | - |
| Lume Cube | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the Service is provided, without express written permission by us. |
| MagBak | ban | read | You agree not to reproduce, duplicate, copy, sell, resell, or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the service is provided, without express written permission by us. |
| MOFT (US) | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the service is provided, without express written permission by us. |
| Nimble | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the service is provided, without express written permission by us. |
| Oh Snap | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the service is provided, without express written permission by us. |
| Pela | ban | read | You may not modify, create derivatives of, copy, distribute, broadcast, transmit, reproduce, … publish, license, transfer, sell, download, store, or otherwise use any PCC Materials or other information or material obtained from or through the Digital Media or as part of the Services unless … |
| PolarPro | no_ban | read | - |
| Rokform | ban | read | You may not create more than one User Account for yourself, create another User Account if we have … pplications, solicit login credentials from other users, or buy, sell, rent, or lease access to your User Account, username or password. |
| Sabrent | no_ban | read | - |
| Satechi | ban | read | You may not access, use, download, copy, reproduce, publish, distribute, modify, or create derivative works from, sell, or exploit in any way the contents of the Website, or any related software, or any part thereof for any other purpose whatsoever. |
| Studio Neat | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the Service is provided, without express written permission by us. |
| Twelve South | ban | read | Any use of materials on this website, including reproduction for purposes other than those noted … ion, distribution, or replication, any form of data extraction or data mining, or other commercial exploitation of any kind, without prior written permission of an authorized officer of Twelve … |
| Ugmonk | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the service is provided, without express written permission by us. |
| Velvet Caviar | ban | read | Except as permitted in this paragraph, you may not reproduce, modify, display or otherwise make … commercial use of any content from the VELVET CAVIAR website reserves the right to refuse service to any individual at its sole discretion and without limitation if it believes that a user’s … |
| VIVO | no_ban | read | - |
| WANDRD | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the service is provided, without express written permission by us. |
| Wildflower Cases | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the service is provided, without express written permission by us. |
| Workrite Ergonomics | no_ban | read | - |
| Bumkins | ban | read | Except for the foregoing license, you have no other rights in the website, Services or any Materials and you may not modify, edit, copy, reproduce, create derivative works of, reverse engineer, alter, enhance or in any way exploit any of the website, Services or Materials in any manner. |
| Colugo | ban | read | You may not download, print, copy, distribute, or otherwise use Site Content for commercial purposes, including publication, sale, or personal gain. |
| Copper Pearl | ban | read | You must not reproduce, distribute, modify, create derivative works of, publicly display, publicly perform, republish, download, store, or transmit any of the material on the Services without our prior written consent. |
| Crazy Aaron's | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the service is provided, without express written permission by us. |
| eeBoo | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the service is provided, without express written permission by us. |
| Exploding Kittens | ban | read | copy, reproduce, distribute, display, mirror, frame or use them (or any of our other materials, intellectual property, or proprietary information) in a way that is not expressly authorized in the Terms; |
| ezpz | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the service is provided, without express written permission by us. |
| Frida | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the service is provided, without express written permission by us. |
| Gathre | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the Service is provided, without express written permission by us. |
| Guardian Bikes | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the service is provided, without express written permission by us. |
| Jiggy | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the service is provided, without express written permission by us. |
| Kids2 | ban | read | Without our prior written permission, you may not use, copy, reproduce, republish, upload, post, transmit, distribute or modify our trademarks or other proprietary information in any way. |
| Kyte Baby | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the service is provided, without express written permission by us. |
| Lalo | ban | read | Lalo does not claim any ownership rights in any User Content and nothing in these Terms will be deemed to restrict any rights that you may have to use and exploit your User Content. |
| Little Sleepies | ban | read | In addition to other prohibitions as set forth in the Terms of Service, you are prohibited from … rsonal information of others; (i) to spam, phish, pharm, pretext, spider, crawl or scrape; (j) for any obscene or immoral purpose; or (k) to interfere with or circumvent the security features of the … |
| Nested Bean | ban | read | You may not reproduce (except as noted above), publish, transmit, distribute, display, modify, create derivative works from, sell or participate in any sale of, or exploit in any way, in whole or in part, any of the Contents, the Site, or any related software. |
| Newton Baby | no_ban | read | - |
| Nugget | no_ban | read | - |
| OOLY | ban | read | You must not reproduce, distribute, modify, create derivative works of, publicly display, publicly perform, republish, download, store, or transmit any of the material on our Website, except as follows: |
| Piecework Puzzles | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the service is provided, without express written permission by us. |
| Plus-Plus USA | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the service is provided, without express written permission by us. |
| Posh Peanut | ban | read | You agree not to reproduce, duplicate, copy, frame, sell, resell or exploit any portion of the … Websites and Services, use of the Websites and Services, or access to the Website and/or Services or any contact on the Websites through which any Services are provided, without our express written … |
| Solly Baby | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the service is provided, without express written permission by us. |
| Tegu | ban | read | Except as set forth in this TOS or in the text of this Site, you may not reproduce, distribute, publish, transmit, modify, adapt, translate, display, distribute, sell, license, publicly perform, prepare derivative works based upon, or otherwise use or exploit the Content. |
