# Recon `recon-006`

- started: 2026-11-27T14:37:18+00:00, finished: 2026-11-27T17:46:08+00:00
- run: https://github.com/siddharthkumarx/ecommerce-price-monitor/actions/runs/46017537149
- candidates: 282, passed: 120 (variant cap 3000)
- run-wide request interval: 4.0s + jitter; halted: no

| store | category | host | robots | products.json | .js | reachable | shopify | products | variants | in stock | .js check | JSON-LD cur | Shopify cur | meta country | reqs | terms | result |
|---|---|---|---|---|---|---|---|---:|---:|---:|---|---|---|---|---:|---|---|
| American Giant | apparel | www.american-giant.com | ok | yes | yes | yes | yes | 201 | 4097 | 65% | match | USD | USD | US | 6 | ban | fail: catalog too large |
| Ana Luisa | apparel | www.analuisa.com | ok | yes | yes | yes | no | - | - | - | - | - | - | - | 2 | - | fail: not shopify |
| Andie | apparel | andieswim.com | ok | yes | yes | yes | yes | 669 | 3729 | 76% | match | USD | USD | US | 8 | ban | fail: catalog too large, excluded category: alcohol |
| Anson Belt & Buckle | apparel | ansonbelt.com | ok | yes | yes | yes | yes | 503 | 939 | 90% | match | USD | USD | US | 8 | ban | fail: excluded category: alcohol |
| Bearbottom | apparel | bearbottomclothing.com | ok | yes | yes | yes | yes | 170 | 4835 | 86% | match | - | USD | US | 6 | ban | fail: catalog too large |
| Birdies | apparel | birdies.com | ok | yes | yes | yes | yes | 200 | 2418 | 81% | match | USD | USD | US | 6 | ban | PASS |
| Blenders Eyewear | apparel | www.blenderseyewear.com | ok | yes | yes | yes | yes | - | - | - | match | USD | USD | US | 10 | - | fail: blocked mid-recon, empty catalog, needed 429 retries |
| Bluffworks | apparel | shop.bluffworks.com | ok | yes | yes | yes | yes | 136 | 2903 | 69% | match | USD | USD | US | 6 | ban | PASS |
| BYLT Basics | apparel | byltbasics.com | ok | yes | yes | yes | no | - | - | - | - | - | - | - | 2 | - | fail: not shopify |
| Cariuma | apparel | www.cariuma.com | ok | yes | yes | no | no | - | - | - | - | - | - | - | 2 | - | fail: blocked |
| Christy Dawn | apparel | christydawn.com | ok | yes | yes | yes | yes | 508 | 2728 | 47% | match | USD | USD | US | 8 | ban | PASS |
| Cuyana | apparel | cuyana.com | ok | yes | yes | yes | yes | 500 | 3026+ | 30% | match | USD | USD | US | 7 | ban | fail: catalog too large |
| DIFF Eyewear | apparel | www.diffeyewear.com | ok | yes | yes | yes | yes | - | - | - | match | USD | USD | US | 10 | - | fail: blocked mid-recon, empty catalog, needed 429 retries |
| Doen | apparel | www.shopdoen.com | ok | yes | yes | yes | yes | - | - | - | match | USD | USD | US | 9 | - | fail: blocked mid-recon, empty catalog, needed 429 retries |
| Felix Gray | apparel | felixgray.com | ok | yes | yes | yes | yes | 158 | 1792 | 94% | match | USD | USD | US | 6 | ban | PASS |
| Fresh Clean Threads | apparel | freshcleantees.com | ok | yes | yes | yes | yes | 250 | 3021+ | 59% | match | USD | USD | US | 6 | ban | fail: catalog too large |
| goodr | apparel | goodr.com | ok | yes | yes | yes | yes | 418 | 628 | 70% | match | USD | USD | US | 7 | ban | fail: excluded category: alcohol |
| Greyson Clothiers | apparel | greysonclothiers.com | ok | yes | yes | yes | yes | 750 | 3435+ | 64% | match | USD | USD | US | 8 | ban | fail: catalog too large |
| Hari Mari | apparel | www.harimari.com | ok | yes | yes | yes | yes | 138 | 704 | 86% | match | USD | USD | US | 6 | ban | fail: excluded category: alcohol, tobacco/vape |
| Holderness & Bourne | apparel | holdernessandbourne.com | ok | yes | yes | yes | yes | 750 | 4062+ | 89% | match | USD | USD | US | 8 | ban | fail: catalog too large |
| Kiel James Patrick | apparel | kieljamespatrick.com | ok | yes | yes | yes | yes | 500 | 3842+ | 70% | match | USD | USD | US | 7 | no_ban | fail: catalog too large, excluded category: alcohol |
| Lems Shoes | apparel | www.lemsshoes.com | ok | yes | yes | yes | yes | 135 | 4303 | 68% | match | USD | USD | US | 6 | no_ban | fail: catalog too large |
| Mission Belt | apparel | missionbelt.com | ok | yes | yes | yes | yes | 250 | 5843+ | 79% | match | USD | USD | US | 6 | ban | fail: catalog too large |
| Mizzen+Main | apparel | mizzenandmain.com | unreachable | - | - | no | no | - | - | - | - | - | - | - | 4 | - | fail: blocked, needed 429 retries |
| Naadam | apparel | naadam.co | ok | yes | yes | yes | yes | 250 | 4493+ | 58% | match | USD | USD | US | 6 | no_ban | fail: catalog too large |
| Nisolo | apparel | nisolo.com | ok | yes | yes | yes | yes | 147 | 1337 | 74% | match | USD | USD | US | 6 | ban | fail: excluded category: alcohol, tobacco/vape |
| Pair of Thieves | apparel | pairofthieves.com | ok | yes | yes | yes | yes | 175 | 799 | 58% | match | USD | USD | US | 6 | no_ban | PASS |
| Parade | apparel | paradeorganics.com | ok | yes | yes | yes | yes | 44 | 2019 | 42% | match | USD | USD | CA | 6 | ban | PASS |
| Pit Viper | apparel | www.pitviper.com | ok | yes | yes | yes | yes | 233 | 546 | 69% | match | USD | USD | US | 6 | ban | fail: excluded category: alcohol |
| Rhoback | apparel | rhoback.com | ok | yes | yes | yes | no | - | - | - | - | - | - | - | 2 | - | fail: not shopify |
| Ridge | apparel | ridge.com | ok | yes | yes | no | no | - | - | - | - | - | - | - | 2 | - | fail: blocked |
| Summersalt | apparel | www.summersalt.com | ok | yes | yes | yes | no | - | - | - | - | - | - | - | 2 | - | fail: not shopify |
| Wool& | apparel | wooland.com | ok | yes | yes | yes | yes | 500 | 4163+ | 79% | match | USD | USD | US | 7 | ban | fail: catalog too large |
| 64 Audio | audio | www.64audio.com | ok | yes | yes | yes | yes | 138 | 1457 | 98% | match | USD | USD | US | 6 | no_ban | PASS |
| AIAIAI | audio | aiaiai.audio | ok | yes | yes | yes | no | - | - | - | - | - | - | - | 2 | - | fail: not shopify |
| Andover Audio | audio | www.andoveraudio.com | ok | yes | yes | yes | yes | 195 | 395 | 94% | match | USD | USD | US | 6 | ban | PASS |
| beyerdynamic North America | audio | north-america.beyerdynamic.com | ok | yes | yes | yes | no | - | - | - | - | - | - | - | 2 | - | fail: not shopify |
| Como Audio | audio | comoaudio.com | missing-4xx | yes | yes | yes | no | - | - | - | - | - | - | - | 2 | - | fail: not shopify |
| Crosley | audio | www.crosleyradio.com | ok | yes | yes | yes | yes | 210 | 406 | 81% | match | USD | USD | US | 6 | no_ban | PASS |
| CT Sounds | audio | www.ctsounds.com | ok | yes | yes | yes | yes | 144 | 182 | 81% | match | USD | USD | US | 6 | ban | PASS |
| Dan Clark Audio | audio | danclarkaudio.com | ok | yes | yes | yes | no | - | - | - | - | - | - | - | 2 | - | fail: not shopify |
| DJ TechTools | audio | djtechtools.com | ok | yes | yes | yes | no | - | - | - | - | - | - | - | 2 | - | fail: not shopify |
| Down4Sound | audio | down4sound.com | unreachable | - | - | no | no | - | - | - | - | - | - | - | 4 | - | fail: blocked |
| ELAC | audio | elac.com | ok | yes | yes | yes | no | - | - | - | - | - | - | - | 2 | - | fail: not shopify |
| Empire Ears | audio | empireears.com | ok | no | no | no | no | - | - | - | - | - | - | - | 1 | - | fail: robots disallows |
| Klipsch | audio | www.klipsch.com | ok | yes | yes | yes | no | - | - | - | - | - | - | - | 2 | - | fail: not shopify |
| Koss | audio | koss.com | ok | yes | yes | yes | yes | 144 | 222 | 93% | match | USD | USD | US | 6 | ban | PASS |
| Moon Audio | audio | www.moon-audio.com | ok | yes | yes | yes | yes | - | - | - | match | USD | USD | US | 10 | - | fail: blocked mid-recon, empty catalog, needed 429 retries |
| Noble Audio | audio | nobleaudio.com | ok | yes | yes | yes | yes | 254 | 487 | 97% | match | USD | USD | US | 7 | ban | PASS |
| Peachtree Audio | audio | www.peachtreeaudio.com | ok | yes | yes | yes | yes | 72 | 144 | 43% | match | USD | USD | US | 6 | ban | PASS |
| Periodic Audio | audio | periodicaudio.com | ok | yes | yes | yes | no | - | - | - | - | - | - | - | 2 | - | fail: not shopify |
| Skar Audio | audio | www.skaraudio.com | ok | yes | yes | yes | no | - | - | - | - | - | - | - | 2 | - | fail: not shopify |
| SOUNDBOKS | audio | soundboks.com | ok | yes | yes | yes | yes | 20 | 37 | 70% | match | USD | USD | US | 6 | ban | PASS |
| Thinksound | audio | thinksound.com | ok | yes | yes | yes | yes | 10 | 13 | 23% | match | USD | USD | CA | 6 | ban | PASS |
| Vanatoo | audio | vanatoo.com | ok | no | no | no | no | - | - | - | - | - | - | - | 1 | - | fail: robots disallows |
| Westone Audio | audio | westoneaudio.com | ok | yes | yes | yes | yes | 49 | 52 | 85% | match | USD | USD | US | 6 | ban | PASS |
| ZMF Headphones | audio | zmfheadphones.com | unreachable | - | - | no | no | - | - | - | - | - | - | - | 4 | - | fail: blocked |
| Amika | beauty | loveamika.com | ok | yes | yes | yes | no | - | - | - | - | - | - | - | 2 | - | fail: not shopify |
| BH Cosmetics | beauty | bhcosmetics.com | ok | yes | yes | yes | yes | 57 | 80 | 94% | match | GBP | GBP | GB | 6 | ban | fail: currency not proven USD |
| Brickell Men's Products | beauty | brickellmensproducts.com | ok | yes | yes | yes | yes | 179 | 306 | 98% | match | USD | USD | US | 6 | ban | PASS |
| Cirque Colors | beauty | www.cirquecolors.com | ok | yes | yes | yes | yes | 434 | 440 | 70% | match | USD | USD | US | 7 | ban | fail: excluded category: alcohol |
| Duke Cannon | beauty | dukecannon.com | ok | yes | yes | yes | yes | 183 | 189 | 91% | match | USD | USD | US | 6 | ban | fail: excluded category: alcohol |
| Every Man Jack | beauty | www.everymanjack.com | ok | yes | yes | yes | yes | 74 | 189 | 91% | match | USD | USD | US | 6 | ban | PASS |
| Glamnetic | beauty | www.glamnetic.com | ok | yes | yes | no | no | - | - | - | - | - | - | - | 2 | - | fail: blocked |
| Good Dye Young | beauty | gooddyeyoung.com | ok | yes | yes | yes | yes | 71 | 82 | 96% | match | USD | USD | US | 6 | ban | PASS |
| Holo Taco | beauty | www.holotaco.com | ok | yes | yes | yes | yes | - | - | - | match | USD | USD | US | 10 | - | fail: blocked mid-recon, empty catalog, needed 429 retries |
| Innersense Organic Beauty | beauty | innersensebeauty.com | ok | yes | yes | yes | yes | 158 | 276 | 88% | match | USD | USD | US | 6 | no_ban | PASS |
| Juvia's Place | beauty | www.juviasplace.com | ok | yes | yes | yes | yes | 176 | 793 | 89% | match | USD | USD | US | 6 | no_ban | PASS |
| K18 | beauty | www.k18hair.com | ok | yes | yes | yes | yes | 40 | 40 | 100% | match | USD | USD | US | 6 | ban | PASS |
| Kitsch | beauty | www.mykitsch.com | ok | yes | yes | yes | yes | - | - | - | match | USD | USD | US | 10 | - | fail: blocked mid-recon, empty catalog, needed 429 retries |
| Kopari | beauty | kopari.com | missing-4xx | yes | yes | yes | no | - | - | - | - | - | - | - | 2 | - | fail: not shopify |
| Krave Beauty | beauty | kravebeauty.com | ok | yes | yes | yes | yes | 36 | 56 | 73% | match | USD | USD | US | 6 | ban | PASS |
| Laura Geller Beauty | beauty | www.laurageller.com | ok | yes | yes | yes | yes | 248 | 967 | 90% | match | USD | USD | US | 6 | ban | PASS |
| Lime Crime | beauty | limecrime.com | ok | yes | yes | yes | yes | 6 | 25 | 84% | match | USD | USD | US | 6 | ban | PASS |
| Mario Badescu | beauty | www.mariobadescu.com | ok | yes | yes | yes | yes | 344 | 542 | 97% | match | USD | USD | US | 7 | ban | PASS |
| Megababe | beauty | megababe.com | unreachable | - | - | no | no | - | - | - | - | - | - | - | 4 | - | fail: blocked |
| Melt Cosmetics | beauty | www.meltcosmetics.com | ok | yes | yes | yes | yes | 101 | 106 | 95% | match | USD | USD | US | 6 | ban | PASS |
| Morphe | beauty | www.morphe.com | ok | yes | yes | yes | yes | 169 | 1654 | 81% | match | USD | USD | US | 6 | ban | PASS |
| Natasha Denona | beauty | natashadenona.com | ok | yes | yes | yes | yes | 125 | 1348 | 97% | match | - | USD | US | 6 | ban | PASS |
| Naturium | beauty | naturium.com | ok | yes | yes | yes | yes | 134 | 138 | 96% | match | USD | USD | US | 6 | ban | PASS |
| Olive & June | beauty | oliveandjune.com | ok | yes | yes | yes | yes | 1777 | 1825 | 68% | match | USD | USD | US | 13 | ban | PASS |
| OSEA | beauty | oseamalibu.com | ok | yes | yes | yes | yes | 103 | 126 | 100% | match | USD | USD | US | 6 | ban | PASS |
| Overtone | beauty | overtone.co | ok | yes | yes | yes | yes | 138 | 278 | 79% | match | USD | USD | US | 6 | ban | PASS |
| Pat McGrath Labs | beauty | www.patmcgrath.com | ok | yes | yes | yes | yes | 152 | 585 | 64% | match | USD | USD | US | 6 | ban | PASS |
| Pattern Beauty | beauty | patternbeauty.com | ok | yes | yes | yes | yes | 170 | 283 | 98% | match | USD | USD | US | 6 | ban | PASS |
| Scotch Porter | beauty | www.scotchporter.com | ok | yes | yes | yes | yes | 45 | 57 | 93% | match | USD | USD | US | 5 | none_found | fail: excluded category: alcohol, tobacco/vape |
| The Detox Market | beauty | www.thedetoxmarket.com | ok | yes | yes | yes | yes | - | - | - | match | USD | USD | US | 10 | - | fail: blocked mid-recon, empty catalog, needed 429 retries |
| Ursa Major | beauty | www.ursamajorvt.com | ok | yes | yes | yes | yes | 61 | 71 | 97% | match | USD | USD | US | 6 | ban | PASS |
| Verb | beauty | www.verbproducts.com | ok | yes | yes | yes | yes | 97 | 293 | 93% | match | USD | USD | US | 6 | ban | PASS |
| AeroPress | coffee_tea | aeropress.com | ok | yes | yes | yes | yes | 248 | 362 | 63% | match | USD | USD | US | 6 | no_ban | PASS |
| Bellocq Tea Atelier | coffee_tea | www.bellocqtea.com | ok | yes | yes | yes | yes | 419 | 1087 | 54% | match | - | USD | US | 7 | ban | fail: excluded category: alcohol |
| Big Shoulders Coffee | coffee_tea | bigshoulderscoffee.com | ok | yes | yes | yes | yes | 41 | 555 | 35% | match | USD | USD | US | 6 | ban | fail: excluded category: alcohol |
| Bird Rock Coffee Roasters | coffee_tea | www.birdrockcoffee.com | ok | yes | yes | yes | yes | 93 | 926 | 82% | match | USD | USD | US | 6 | ban | fail: excluded category: alcohol |
| Black & White Coffee Roasters | coffee_tea | www.blackwhiteroasters.com | ok | yes | yes | yes | yes | 248 | 666 | 42% | match | USD | USD | US | 6 | ban | fail: excluded category: alcohol |
| Coava Coffee | coffee_tea | coavacoffee.com | ok | yes | yes | yes | no | - | - | - | - | - | - | - | 2 | - | fail: not shopify |
| Corvus Coffee | coffee_tea | www.corvuscoffee.com | ok | yes | yes | yes | yes | 88 | 212 | 95% | match | USD | USD | US | 6 | ban | fail: excluded category: alcohol |
| Cuvee Coffee | coffee_tea | cuveecoffee.com | ok | yes | yes | yes | yes | 43 | 147 | 93% | match | USD | USD | US | 6 | ban | PASS |
| Devocion | coffee_tea | www.devocion.com | ok | yes | yes | yes | yes | 35 | 242 | 99% | match | USD | USD | US | 6 | ban | PASS |
| Dogwood Coffee | coffee_tea | www.dogwoodcoffee.com | ok | yes | yes | yes | yes | 42 | 129 | 88% | match | - | USD | US | 6 | none_found | PASS |
| Encha | coffee_tea | encha.com | ok | yes | yes | yes | yes | 5 | 13 | 77% | match | USD | USD | US | 6 | ban | PASS |
| Four Barrel Coffee | coffee_tea | www.fourbarrelcoffee.com | ok | yes | yes | yes | yes | 113 | 352 | 98% | match | USD | USD | US | 6 | no_ban | PASS |
| George Howell Coffee | coffee_tea | georgehowellcoffee.com | ok | yes | yes | yes | yes | 113 | 305 | 81% | match | - | USD | US | 6 | ban | PASS |
| Greater Goods Coffee | coffee_tea | greatergoodsroasting.com | ok | yes | yes | yes | yes | 71 | 829 | 97% | match | USD | USD | US | 6 | ban | fail: excluded category: alcohol |
| Heart Coffee Roasters | coffee_tea | www.heartroasters.com | ok | yes | yes | yes | yes | 38 | 81 | 94% | match | USD | USD | US | 6 | ban | PASS |
| Huckleberry Roasters | coffee_tea | www.huckleberryroasters.com | ok | yes | yes | yes | no | - | - | - | - | - | - | - | 2 | - | fail: not shopify |
| Irving Farm | coffee_tea | irvingfarmcoffee.com | ok | yes | yes | yes | yes | 38 | 428 | 98% | match | USD | USD | US | 6 | ban | PASS |
| Joe Coffee Company | coffee_tea | joecoffeecompany.com | ok | yes | yes | yes | yes | 91 | 716 | 96% | match | USD | USD | US | 6 | ban | PASS |
| Kuma Coffee | coffee_tea | www.kumacoffee.com | ok | yes | yes | yes | yes | 52 | 118 | 78% | match | - | USD | US | 6 | ban | PASS |
| Little Wolf Coffee | coffee_tea | littlewolf.coffee | ok | yes | yes | yes | yes | 37 | 137 | 65% | match | USD | USD | US | 6 | ban | PASS |
| Madcap Coffee | coffee_tea | www.madcapcoffee.com | ok | yes | yes | yes | yes | 124 | 295 | 86% | match | USD | USD | US | 6 | no_ban | PASS |
| Methodical Coffee | coffee_tea | methodicalcoffee.com | ok | yes | yes | yes | yes | 171 | 348 | 95% | match | USD | USD | US | 6 | ban | fail: excluded category: alcohol |
| Metric Coffee | coffee_tea | metriccoffee.com | ok | yes | yes | yes | yes | 58 | 426 | 100% | match | - | USD | US | 6 | ban | PASS |
| Olympia Coffee | coffee_tea | olympiacoffee.com | unreachable | - | - | no | no | - | - | - | - | - | - | - | 4 | - | fail: blocked |
| Passenger Coffee | coffee_tea | drinkpassenger.com | ok | yes | yes | yes | no | - | - | - | - | - | - | - | 2 | - | fail: not shopify |
| PERC Coffee | coffee_tea | perccoffee.com | ok | yes | yes | yes | yes | 163 | 675 | 26% | match | USD | USD | US | 6 | ban | fail: excluded category: alcohol |
| Pique | coffee_tea | www.piquelife.com | ok | yes | yes | yes | yes | 75 | 81 | 96% | match | USD | USD | US | 6 | no_ban | PASS |
| Ratio Coffee | coffee_tea | ratiocoffee.com | ok | yes | yes | yes | yes | 102 | 358 | 84% | match | USD | USD | US | 6 | ban | PASS |
| Ritual Coffee Roasters | coffee_tea | ritualcoffee.com | missing-4xx | yes | yes | no | no | - | - | - | - | - | - | - | 2 | - | fail: blocked |
| Ruby Coffee Roasters | coffee_tea | rubycoffeeroasters.com | ok | yes | yes | yes | yes | 239 | 796 | 84% | missing | - | - | US | 6 | ban | fail: currency not proven USD, product .js unavailable, excluded category: alcohol |
| Song Tea & Ceramics | coffee_tea | songtea.com | ok | yes | yes | yes | yes | 293 | 533 | 48% | match | USD | USD | US | 7 | ban | PASS |
| Wonderstate Coffee | coffee_tea | wonderstate.com | ok | yes | yes | yes | yes | 112 | 347 | 98% | match | USD | USD | US | 6 | ban | PASS |
| Bear Grips | fitness | www.beargrips.com | ok | yes | yes | yes | yes | 250 | 4564+ | 100% | match | USD | USD | US | 6 | ban | fail: catalog too large |
| Bear KompleX | fitness | bearkomplex.com | ok | yes | yes | yes | yes | 500 | 3948+ | 69% | match | USD | USD | US | 7 | no_ban | fail: catalog too large, excluded category: alcohol, weapons |
| Bodylastics | fitness | bodylastics.com | ok | yes | yes | yes | no | - | - | - | - | - | - | - | 2 | - | fail: not shopify |
| Chirp | fitness | chirpwheel.com | unreachable | - | - | no | no | - | - | - | - | - | - | - | 4 | - | fail: blocked |
| CRBN Pickleball | fitness | crbnpickleball.com | ok | yes | yes | yes | yes | 92 | 363 | 93% | match | USD | USD | US | 6 | ban | PASS |
| Ekrin Athletics | fitness | www.ekrin.com | ok | yes | yes | yes | yes | 19 | 66 | 65% | match | USD | USD | US | 6 | ban | PASS |
| EliteSRS | fitness | elitejumps.co | ok | yes | yes | yes | yes | 109 | 838 | 84% | match | - | USD | US | 6 | ban | PASS |
| Feedback Sports | fitness | feedbacksports.com | ok | yes | yes | yes | yes | 358 | 373 | 74% | match | USD | USD | US | 7 | no_ban | PASS |
| FINIS | fitness | finisinc.com | unreachable | - | - | no | no | - | - | - | - | - | - | - | 4 | - | fail: blocked |
| FLYBIRD Fitness | fitness | www.fedfitness.com | ok | yes | yes | yes | yes | 115 | 350 | 91% | match | USD | USD | US | 6 | ban | PASS |
| GoSports | fitness | www.playgosports.com | ok | yes | yes | yes | yes | 734 | 1258 | 88% | match | USD | USD | US | 8 | ban | fail: excluded category: alcohol, tobacco/vape, weapons |
| Kabuki Strength | fitness | kabukistrength.com | ok | no | no | no | no | - | - | - | - | - | - | - | 1 | - | fail: robots disallows |
| Kinetic | fitness | kurtkinetic.com | ok | yes | yes | yes | no | - | - | - | - | - | - | - | 2 | - | fail: not shopify |
| Major Fitness | fitness | www.majorfitness.com | ok | yes | yes | yes | yes | 46 | 113 | 97% | match | USD | USD | US | 6 | ban | PASS |
| MERACH | fitness | www.merach.com | ok | yes | yes | yes | no | - | - | - | - | - | - | - | 2 | - | fail: not shopify |
| RitFit | fitness | www.ritfitsports.com | ok | yes | yes | yes | yes | 145 | 696 | 95% | match | USD | USD | US | 6 | ban | PASS |
| Rukket Sports | fitness | rukketsports.com | ok | yes | yes | yes | no | - | - | - | - | - | - | - | 2 | - | fail: not shopify |
| Sanabul | fitness | sanabulsports.com | ok | yes | yes | yes | yes | 152 | 1619 | 30% | match | USD | USD | US | 6 | ban | PASS |
| Selkirk Sport | fitness | www.selkirk.com | ok | yes | yes | yes | yes | 206 | 2906 | 57% | match | USD | USD | US | 6 | ban | PASS |
| SPIbelt | fitness | spibelt.com | ok | yes | yes | yes | yes | 53 | 161 | 98% | match | USD | USD | US | 6 | no_ban | PASS |
| Spikeball | fitness | www.spikeball.com | ok | yes | yes | yes | yes | 114 | 217 | 65% | match | USD | USD | US | 6 | ban | PASS |
| WODFitters | fitness | wodfitters.com | missing-4xx | yes | yes | yes | no | - | - | - | - | - | - | - | 2 | - | fail: not shopify |
| Yoga Design Lab | fitness | yogadesignlab.com | ok | yes | yes | yes | yes | 138 | 224 | 88% | match | USD | USD | US | 5 | none_found | PASS |
| Apotheke | home_kitchen | apothekeco.com | ok | yes | yes | yes | yes | 277 | 283 | 95% | match | USD | USD | US | 7 | ban | PASS |
| Authenticity50 | home_kitchen | authenticity50.com | ok | yes | yes | yes | yes | 13 | 109 | 65% | match | USD | USD | US | 6 | ban | PASS |
| Baloo Living | home_kitchen | baloosleep.com | unreachable | - | - | no | no | - | - | - | - | - | - | - | 4 | - | fail: blocked |
| Capri Blue | home_kitchen | capri-blue.com | ok | yes | yes | yes | yes | 437 | 437 | 78% | match | USD | USD | US | 7 | ban | PASS |
| Cleancult | home_kitchen | www.cleancult.com | ok | yes | yes | yes | no | - | - | - | - | - | - | - | 2 | - | fail: not shopify |
| Coming Soon | home_kitchen | comingsoonnewyork.com | ok | yes | yes | yes | yes | 391 | 1082 | 79% | match | - | USD | US | 7 | ban | fail: excluded category: alcohol, tobacco/vape |
| Crow Canyon Home | home_kitchen | www.crowcanyonhome.com | ok | yes | yes | yes | yes | - | - | - | match | USD | USD | US | 9 | - | fail: blocked mid-recon, empty catalog, needed 429 retries |
| Dropps | home_kitchen | www.dropps.com | ok | yes | yes | yes | yes | 38 | 73 | 90% | match | USD | USD | US | 6 | ban | PASS |
| Fishs Eddy | home_kitchen | www.fishseddy.com | ok | yes | yes | yes | yes | 369 | 380 | 86% | match | USD | USD | US | 7 | ban | PASS |
| Force of Nature | home_kitchen | www.forceofnatureclean.com | ok | yes | yes | yes | no | - | - | - | - | - | - | - | 2 | - | fail: not shopify |
| Gravity Blanket | home_kitchen | gravityblankets.com | ok | yes | yes | yes | yes | 11 | 105 | 59% | match | USD | USD | US | 5 | none_found | PASS |
| Heritage Steel | home_kitchen | www.heritagesteel.us | ok | yes | yes | yes | yes | 173 | 216 | 93% | match | USD | USD | US | 6 | ban | PASS |
| Homecourt | home_kitchen | homecourt.co | ok | yes | yes | no | no | - | - | - | - | - | - | - | 2 | - | fail: blocked |
| Kassatex | home_kitchen | kassatex.com | ok | yes | yes | yes | yes | 531 | 3138 | 87% | match | - | USD | US | 8 | no_ban | fail: catalog too large, excluded category: alcohol |
| KINTO USA | home_kitchen | kinto-usa.com | ok | yes | yes | yes | yes | 469 | 988 | 96% | match | USD | USD | US | 7 | ban | fail: excluded category: alcohol |
| LAFCO | home_kitchen | www.lafco.com | ok | yes | yes | yes | no | - | - | - | - | - | - | - | 2 | - | fail: not shopify |
| Lodge Cast Iron | home_kitchen | www.lodgecastiron.com | ok | yes | yes | yes | yes | - | - | - | match | USD | USD | US | 9 | - | fail: blocked mid-recon, empty catalog, needed 429 retries |
| Lostine | home_kitchen | lostine.com | ok | yes | yes | yes | yes | 250 | 4370+ | 99% | match | USD | USD | US | 6 | ban | fail: catalog too large |
| Matouk | home_kitchen | www.matouk.com | ok | yes | yes | yes | yes | - | - | - | match | - | USD | US | 9 | - | fail: blocked mid-recon, empty catalog, needed 429 retries |
| Meliora Cleaning Products | home_kitchen | meliorameansbetter.com | ok | yes | yes | yes | yes | 23 | 78 | 97% | match | USD | USD | US | 6 | ban | PASS |
| Nordic Ware | home_kitchen | nordicware.com | unreachable | - | - | no | no | - | - | - | - | - | - | - | 1 | - | fail: blocked |
| Notary Ceramics | home_kitchen | www.notaryceramics.com | ok | yes | yes | yes | yes | - | - | - | match | USD | USD | US | 10 | - | fail: blocked mid-recon, empty catalog, needed 429 retries |
| Open Spaces | home_kitchen | www.patternbrands.com | ok | yes | yes | yes | no | - | - | - | - | - | - | - | 2 | - | fail: not shopify |
| Paddywax | home_kitchen | paddywax.com | ok | yes | yes | yes | yes | 469 | 471 | 80% | match | USD | USD | US | 7 | ban | fail: excluded category: tobacco/vape |
| Proclamation Goods | home_kitchen | www.proclamationgoods.com | ok | yes | yes | yes | yes | 1 | 3 | 0% | match | - | USD | US | 6 | ban | PASS |
| Riley Home | home_kitchen | rileyhome.com | ok | yes | yes | yes | yes | 121 | 4028 | 78% | match | USD | USD | US | 6 | no_ban | fail: catalog too large |
| Slow North | home_kitchen | www.slownorth.com | ok | yes | yes | yes | yes | 219 | 317 | 95% | match | USD | USD | US | 6 | ban | PASS |
| USA Pan | home_kitchen | usapan.com | missing-4xx | yes | yes | no | no | - | - | - | - | - | - | - | 2 | - | fail: blocked |
| Voluspa | home_kitchen | voluspa.com | ok | yes | yes | yes | yes | 1050 | 1059 | 94% | match | USD | USD | US | 10 | ban | fail: excluded category: alcohol |
| Yamazaki Home | home_kitchen | yamazakihome.com | unreachable | - | - | no | no | - | - | - | - | - | - | - | 4 | - | fail: blocked |
| Yield Design | home_kitchen | yield-design-llc.myshopify.com | ok | yes | yes | yes | yes | 0 | 0 | - | - | - | - | US | 4 | no_ban | fail: empty catalog, currency not proven USD, product .js unavailable |
| Airblaster | outdoor | airblaster.com | ok | yes | yes | yes | no | - | - | - | - | - | - | - | 2 | - | fail: not shopify |
| Barebones Living | outdoor | barebonesliving.com | ok | yes | yes | yes | yes | 181 | 454 | 66% | match | USD | USD | US | 6 | no_ban | PASS |
| Cabeau | outdoor | cabeau.com | ok | yes | yes | yes | yes | 29 | 68 | 76% | match | USD | USD | US | 6 | no_ban | PASS |
| Dutchware Gear | outdoor | dutchwaregear.com | ok | yes | yes | no | no | - | - | - | - | - | - | - | 2 | - | fail: blocked |
| Evergoods | outdoor | evergoods.us | ok | yes | yes | yes | yes | 43 | 104 | 93% | match | USD | USD | US | 6 | ban | PASS |
| Feathered Friends | outdoor | featheredfriends.com | ok | yes | yes | yes | yes | 500 | 4780+ | 33% | match | USD | USD | US | 7 | ban | fail: catalog too large |
| Flylow | outdoor | flylowgear.com | ok | yes | yes | yes | yes | 247 | 3845 | 79% | match | USD | USD | US | 5 | none_found | fail: catalog too large |
| Garage Grown Gear | outdoor | www.garagegrowngear.com | ok | yes | yes | no | no | - | - | - | - | - | - | - | 2 | - | fail: blocked |
| Give'r | outdoor | giver.com | ok | yes | yes | yes | no | - | - | - | - | - | - | - | 2 | - | fail: not shopify |
| GORUCK | outdoor | www.goruck.com | ok | yes | yes | yes | yes | - | - | - | match | USD | USD | US | 9 | - | fail: blocked mid-recon, empty catalog, needed 429 retries |
| Granite Gear | outdoor | granitegear.com | ok | yes | yes | yes | no | - | - | - | - | - | - | - | 2 | - | fail: not shopify |
| Injinji | outdoor | www.injinji.com | ok | yes | yes | yes | no | - | - | - | - | - | - | - | 2 | - | fail: not shopify |
| ISLE Surf & SUP | outdoor | islesurfandsup.com | ok | yes | yes | yes | no | - | - | - | - | - | - | - | 2 | - | fail: not shopify |
| Jones Snowboards | outdoor | www.jonessnowboards.com | ok | yes | yes | yes | yes | 261 | 1591 | 69% | match | USD | USD | US | 7 | none_found | fail: needed 429 retries |
| Kokopelli Packraft | outdoor | kokopellipackraft.com | unreachable | - | - | no | no | - | - | - | - | - | - | - | 4 | - | fail: blocked |
| KUHL | outdoor | www.kuhl.com | ok | yes | yes | yes | no | - | - | - | - | - | - | - | 2 | - | fail: not shopify |
| Minaal | outdoor | www.minaal.com | ok | yes | yes | yes | yes | 36 | 68 | 72% | match | USD | USD | US | 6 | ban | PASS |
| Mission Workshop | outdoor | missionworkshop.com | ok | yes | yes | yes | yes | 156 | 1262 | 49% | match | USD | USD | US | 6 | ban | PASS |
| Nomad Lane | outdoor | nomadlane.com | ok | yes | yes | no | no | - | - | - | - | - | - | - | 2 | - | fail: blocked |
| Orange Mud | outdoor | www.orangemud.com | ok | yes | yes | yes | yes | 129 | 463 | 86% | match | USD | USD | US | 6 | ban | PASS |
| Paria Outdoor Products | outdoor | www.pariaoutdoorproducts.com | ok | yes | yes | yes | yes | 61 | 159 | 94% | match | USD | USD | US | 6 | ban | PASS |
| Revelate Designs | outdoor | revelatedesigns.com | ok | yes | yes | no | no | - | - | - | - | - | - | - | 2 | - | fail: blocked |
| Silca | outdoor | silca.cc | ok | yes | yes | yes | yes | 178 | 347 | 77% | match | USD | USD | US | 6 | ban | fail: excluded category: alcohol |
| So iLL | outdoor | soillholds.com | ok | yes | yes | yes | yes | 250 | 4999+ | 96% | match | USD | USD | US | 6 | ban | fail: catalog too large |
| Strafe Outerwear | outdoor | www.strafeouterwear.com | ok | yes | yes | yes | yes | 163 | 2105 | 27% | match | USD | USD | US | 6 | ban | PASS |
| Tension Climbing | outdoor | tensionclimbing.com | ok | yes | yes | yes | yes | 128 | 1892 | 97% | match | USD | USD | US | 6 | ban | PASS |
| Vargo Outdoors | outdoor | vargooutdoors.com | ok | yes | yes | yes | yes | 115 | 198 | 98% | match | USD | USD | US | 6 | ban | PASS |
| Weston Backcountry | outdoor | westonbackcountry.com | ok | yes | yes | yes | yes | 106 | 580 | 81% | match | - | USD | US | 6 | ban | PASS |
| Aquarium Co-Op | pet | www.aquariumcoop.com | ok | yes | yes | yes | yes | - | - | - | match | USD | USD | US | 9 | - | fail: blocked mid-recon, empty catalog, needed 429 retries |
| Benebone | pet | www.benebone.com | ok | yes | yes | yes | yes | 53 | 154 | 91% | match | USD | USD | US | 6 | ban | PASS |
| Bocce's Bakery | pet | www.boccesbakery.com | ok | yes | yes | yes | yes | 146 | 148 | 81% | match | USD | USD | US | 6 | ban | PASS |
| Buce Plant | pet | buceplant.com | ok | yes | yes | yes | yes | 1750 | 3424+ | 57% | match | USD | USD | US | 12 | ban | fail: catalog too large |
| Diggs | pet | www.diggs.pet | ok | yes | yes | yes | yes | 48 | 225 | 81% | match | USD | USD | US | 6 | ban | PASS |
| Found My Animal | pet | www.foundmyanimal.com | ok | yes | yes | yes | yes | 750 | 3418+ | 84% | match | USD | USD | US | 8 | ban | fail: catalog too large |
| Glass Aqua | pet | glassaqua.com | ok | yes | yes | yes | no | - | - | - | - | - | - | - | 2 | - | fail: not shopify |
| Goughnuts | pet | goughnuts.com | missing-4xx | yes | yes | yes | no | - | - | - | - | - | - | - | 2 | - | fail: not shopify |
| Harry Barker | pet | harrybarker.com | ok | yes | yes | yes | yes | 34 | 156 | 55% | match | USD | USD | US | 6 | ban | PASS |
| Hepper | pet | hepper.com | ok | yes | yes | no | no | - | - | - | - | - | - | - | 2 | - | fail: blocked |
| Lambwolf Collective | pet | lambwolf.com | missing-4xx | yes | yes | yes | no | - | - | - | - | - | - | - | 2 | - | fail: not shopify |
| Mau Pets | pet | www.maupets.com | ok | yes | yes | yes | yes | 70 | 458 | 98% | match | USD | USD | US | 6 | ban | PASS |
| Max and Neo | pet | www.maxandneo.com | ok | yes | yes | yes | yes | 114 | 969 | 77% | match | USD | USD | US | 6 | ban | PASS |
| Modkat | pet | modkat.com | ok | yes | yes | yes | yes | 57 | 106 | 98% | match | USD | USD | US | 6 | no_ban | PASS |
| Molly Mutt | pet | www.mollymutt.com | ok | yes | yes | no | no | - | - | - | - | - | - | - | 2 | - | fail: blocked |
| Neko Flies | pet | nekoflies.com | unreachable | - | - | no | no | - | - | - | - | - | - | - | 4 | - | fail: blocked |
| P.L.A.Y. Pet Lifestyle and You | pet | www.playpetbrands.com | ok | yes | yes | yes | yes | 418 | 1010 | 82% | match | USD | USD | US | 7 | no_ban | fail: excluded category: alcohol |
| Paw.com | pet | www.paw.com | ok | yes | yes | yes | yes | 85 | 201 | 61% | match | USD | USD | US | 6 | ban | PASS |
| Pawz | pet | pawz.com | ok | yes | yes | yes | yes | 750 | 4426+ | 95% | match | USD | USD | US | 8 | ban | fail: catalog too large, excluded category: alcohol |
| Pet Krewe | pet | petkrewe.com | ok | yes | yes | yes | yes | 0 | 0 | - | - | - | - | US | 4 | ban | fail: empty catalog, currency not proven USD, product .js unavailable |
| Planet Dog | pet | planetdog.com | ok | no | no | no | no | - | - | - | - | - | - | - | 1 | - | fail: robots disallows |
| Polkadog Bakery | pet | www.polkadog.com | ok | yes | yes | yes | yes | 508 | 941 | 96% | match | USD | USD | US | 10 | no_ban | fail: needed 429 retries |
| Pupford | pet | pupford.com | ok | yes | yes | yes | yes | 317 | 517 | 78% | match | USD | USD | US | 7 | no_ban | PASS |
| Rabbit Hole Hay | pet | www.rabbitholehay.com | ok | yes | yes | yes | yes | 170 | 325 | 93% | match | - | USD | US | 6 | ban | PASS |
| Shameless Pets | pet | shamelesspets.com | ok | yes | yes | yes | yes | 52 | 60 | 95% | match | USD | USD | US | 6 | ban | PASS |
| Sleepypod | pet | sleepypod.com | ok | yes | yes | yes | yes | 33 | 286 | 85% | match | - | USD | US | 6 | ban | PASS |
| Wolfgang Man & Beast | pet | wolfgangmanandbeast.com | unreachable | - | - | no | no | - | - | - | - | - | - | - | 4 | - | fail: blocked |
| Zee.Dog | pet | www.zeedog.com | ok | yes | yes | yes | yes | 455 | 1096 | 72% | match | USD | USD | US | 7 | ban | PASS |
| CannonKeys | tech_accessories | cannonkeys.com | ok | yes | yes | yes | yes | 500 | 4667+ | 12% | match | - | USD | US | 7 | ban | fail: catalog too large, excluded category: alcohol |
| Caudabe | tech_accessories | caudabe.com | ok | yes | yes | yes | yes | 135 | 881 | 95% | match | USD | USD | US | 6 | ban | PASS |
| Courant | tech_accessories | www.courant.com | ok | yes | yes | yes | no | - | - | - | - | - | - | - | 2 | - | fail: not shopify |
| Das Keyboard | tech_accessories | www.daskeyboard.com | ok | yes | yes | yes | no | - | - | - | - | - | - | - | 2 | - | fail: not shopify |
| Divinikey | tech_accessories | divinikey.com | ok | yes | yes | yes | yes | 500 | 4512+ | 17% | match | USD | USD | US | 7 | ban | fail: catalog too large |
| Freewell | tech_accessories | freewellgear.com | ok | yes | yes | yes | yes | 443 | 839 | 100% | match | USD | USD | HK | 7 | ban | PASS |
| Glorious | tech_accessories | www.gloriousgaming.com | ok | yes | yes | yes | yes | 236 | 614 | 70% | match | USD | USD | US | 6 | ban | PASS |
| Incase | tech_accessories | www.incase.com | ok | yes | yes | yes | yes | 71 | 144 | 76% | match | USD | USD | US | 6 | ban | PASS |
| Kinetic Labs | tech_accessories | kineticlabs.com | ok | yes | yes | yes | no | - | - | - | - | - | - | - | 2 | - | fail: not shopify |
| KONO | tech_accessories | kono.store | ok | yes | yes | yes | no | - | - | - | - | - | - | - | 2 | - | fail: not shopify |
| Lander | tech_accessories | landercase.com | unreachable | - | - | no | no | - | - | - | - | - | - | - | 4 | - | fail: blocked |
| Loopy Cases | tech_accessories | www.loopycases.com | ok | yes | yes | yes | yes | 237 | 5732 | 75% | match | USD | USD | US | 6 | ban | fail: catalog too large, excluded category: alcohol |
| Mode Designs | tech_accessories | modedesigns.com | ok | yes | yes | yes | yes | 76 | 391 | 60% | match | USD | USD | US | 6 | ban | PASS |
| Native Union | tech_accessories | www.nativeunion.com | ok | yes | yes | yes | yes | 199 | 3901 | 45% | match | USD | USD | HK | 6 | ban | fail: catalog too large |
| NovelKeys | tech_accessories | novelkeys.com | ok | yes | yes | yes | yes | 412 | 1883 | 23% | match | USD | USD | US | 7 | ban | fail: excluded category: cannabis/cbd |
| Pulsar Gaming Gears | tech_accessories | www.pulsar.gg | ok | yes | yes | yes | yes | 311 | 626 | 51% | match | - | USD | KR | 7 | ban | PASS |
| SANDMARC | tech_accessories | www.sandmarc.com | ok | yes | yes | yes | yes | 719 | 904 | 92% | match | USD | USD | US | 9 | ban | fail: needed 429 retries |
| Shimoda Designs | tech_accessories | shimodadesigns.com | ok | yes | yes | yes | no | - | - | - | - | - | - | - | 2 | - | fail: not shopify |
| Smartish | tech_accessories | smartish.com | ok | yes | yes | yes | yes | 674 | 1422 | 82% | match | USD | USD | US | 8 | ban | fail: excluded category: alcohol |
| Sonix | tech_accessories | www.sonix.com | ok | yes | yes | yes | no | - | - | - | - | - | - | - | 2 | - | fail: not shopify |
| Statik | tech_accessories | getstatik.com | ok | yes | yes | yes | no | - | - | - | - | - | - | - | 2 | - | fail: not shopify |
| Avanchy | toys_kids | avanchy.com | ok | yes | yes | yes | yes | 29 | 364 | 56% | match | USD | USD | US | 6 | ban | PASS |
| Bannor Toys | toys_kids | bannortoys.com | ok | yes | yes | yes | yes | 169 | 317 | 99% | match | USD | USD | US | 6 | ban | PASS |
| Bella Luna Toys | toys_kids | www.bellalunatoys.com | ok | yes | yes | yes | yes | - | - | - | match | USD | USD | US | 9 | - | fail: blocked mid-recon, empty catalog, needed 429 retries |
| Bellabu Bear | toys_kids | www.bellabubear.com | ok | yes | yes | yes | yes | 500 | 3016+ | 78% | match | - | USD | US | 7 | ban | fail: catalog too large |
| Boba | toys_kids | boba.com | ok | yes | yes | yes | yes | 64 | 67 | 75% | match | USD | USD | US | 6 | ban | PASS |
| Buffalo Games | toys_kids | www.buffalogames.com | ok | yes | yes | yes | yes | - | - | - | match | USD | USD | US | 9 | - | fail: blocked mid-recon, empty catalog, needed 429 retries |
| Comotomo | toys_kids | comotomo.com | ok | yes | yes | yes | yes | 14 | 28 | 89% | match | - | USD | US | 6 | ban | PASS |
| Finn + Emma | toys_kids | www.finnandemma.com | ok | yes | yes | no | no | - | - | - | - | - | - | - | 2 | - | fail: blocked |
| Freshly Picked | toys_kids | freshlypicked.com | ok | yes | yes | yes | yes | 244 | 1211 | 54% | match | USD | USD | US | 6 | ban | PASS |
| Galison | toys_kids | www.galison.com | ok | yes | yes | yes | yes | - | - | - | match | USD | USD | US | 13 | - | fail: blocked mid-recon, empty catalog, needed 429 retries |
| Hazel Village | toys_kids | hazelvillage.com | ok | yes | yes | yes | yes | 378 | 425 | 71% | match | USD | USD | US | 7 | ban | PASS |
| Itzy Ritzy | toys_kids | itzyritzy.com | unreachable | - | - | no | no | - | - | - | - | - | - | - | 1 | - | fail: blocked |
| Kate Quinn | toys_kids | katequinnorganics.com | missing-4xx | yes | yes | yes | no | - | - | - | - | - | - | - | 2 | - | fail: not shopify |
| Kickee Pants | toys_kids | www.kickeepants.com | ok | yes | yes | yes | yes | - | - | - | match | USD | USD | US | 9 | - | fail: blocked mid-recon, empty catalog, needed 429 retries |
| Kid Made Modern | toys_kids | kidmademodern.com | ok | yes | yes | yes | yes | 14 | 18 | 28% | match | USD | USD | US | 6 | ban | PASS |
| Leder Games | toys_kids | ledergames.com | ok | yes | yes | yes | yes | 139 | 2325 | 98% | match | USD | USD | US | 6 | ban | PASS |
| Magna-Tiles | toys_kids | magnatiles.com | ok | yes | yes | yes | yes | 84 | 84 | 100% | match | USD | USD | US | 6 | ban | PASS |
| Magnetic Me | toys_kids | magneticme.com | ok | yes | yes | yes | yes | 750 | 4135+ | 88% | match | - | USD | US | 8 | ban | fail: catalog too large |
| Manhattan Toy | toys_kids | www.manhattantoy.com | ok | yes | yes | yes | yes | 318 | 321 | 90% | match | USD | USD | US | 7 | ban | PASS |
| Monica + Andy | toys_kids | monicaandandy.com | ok | yes | yes | yes | no | - | - | - | - | - | - | - | 2 | - | fail: not shopify |
| Mudpuppy | toys_kids | www.mudpuppy.com | ok | yes | yes | yes | yes | 498 | 500 | 96% | match | USD | USD | US | 9 | ban | fail: needed 429 retries |
| Pehr | toys_kids | pehr.com | ok | yes | yes | yes | yes | 951 | 3684 | 68% | match | USD | USD | US | 9 | ban | fail: catalog too large |
| PicassoTiles | toys_kids | www.picassotiles.com | ok | yes | yes | yes | yes | - | - | - | match | USD | USD | US | 10 | - | fail: blocked mid-recon, empty catalog, needed 429 retries |
| Piccalio | toys_kids | piccalio.com | ok | yes | yes | yes | yes | 41 | 157 | 96% | match | USD | USD | US | 6 | ban | PASS |
| Quincy Mae | toys_kids | ryleeandcru.com | ok | yes | yes | no | no | - | - | - | - | - | - | - | 2 | - | fail: blocked |
| Rylee + Cru | toys_kids | ryleeandcru.com | ok | yes | yes | no | no | - | - | - | - | - | - | - | 2 | - | fail: blocked |
| The Beaufort Bonnet Company | toys_kids | www.thebeaufortbonnetcompany.com | ok | yes | yes | yes | yes | 500 | 4451+ | 80% | match | USD | USD | US | 9 | ban | fail: catalog too large, excluded category: alcohol, needed 429 retries |
| Unstable Games | toys_kids | teeturtle.com | ok | yes | yes | yes | yes | 250 | 3686+ | 89% | match | USD | USD | US | 6 | ban | fail: catalog too large |
| Wee Gallery | toys_kids | weegallery.com | ok | yes | yes | yes | yes | 256 | 276 | 75% | match | USD | USD | US | 7 | ban | PASS |
| WildBird | toys_kids | wildbird.co | ok | yes | yes | yes | yes | 553 | 1309 | 84% | match | USD | USD | US | 8 | no_ban | PASS |

## Notes

- **AIAIAI**: /products.json: http 200, text/html; charset=utf-8
- **Airblaster**: /products.json: http 404, text/html; charset=UTF-8
- **Amika**: /products.json: http 404, text/html
- **Ana Luisa**: /products.json: http 404, text/html; charset=utf-8
- **Aquarium Co-Op**: stopped: retries exhausted: http 429
- **Baloo Living**: stopped: robots.txt unreachable: retries exhausted: network error: ConnectError
- **Bearbottom**: no JSON-LD offer currency on product page
- **Bella Luna Toys**: stopped: retries exhausted: http 429
- **Bellabu Bear**: no JSON-LD offer currency on product page
- **Bellocq Tea Atelier**: no JSON-LD offer currency on product page
- **beyerdynamic North America**: /products.json: http 404, text/html; charset=utf-8
- **Blenders Eyewear**: stopped: retries exhausted: http 429
- **Bodylastics**: /products.json: http 404, text/plain
- **Buffalo Games**: stopped: retries exhausted: http 429
- **BYLT Basics**: /products.json: http 404, text/html
- **CannonKeys**: no JSON-LD offer currency on product page
- **Cariuma**: stopped: blocked: http 401
- **Chirp**: stopped: robots.txt unreachable: retries exhausted: network error: ConnectError
- **Cleancult**: /products.json: http 404, text/html; charset=utf-8
- **Coava Coffee**: /products.json: http 404, application/json; charset=UTF-8
- **Coming Soon**: no JSON-LD offer currency on product page
- **Como Audio**: /products.json: http 404, ?
- **Comotomo**: no JSON-LD offer currency on product page
- **Courant**: /products.json: http 404, text/html; charset=utf-8
- **Crow Canyon Home**: stopped: retries exhausted: http 429
- **Dan Clark Audio**: /products.json: http 404, text/html; charset=UTF-8
- **Das Keyboard**: /products.json: http 404, text/html; charset=utf-8
- **DIFF Eyewear**: stopped: retries exhausted: http 429
- **DJ TechTools**: /products.json: http 404, text/html; charset=UTF-8
- **Doen**: stopped: retries exhausted: http 429
- **Dogwood Coffee**: no JSON-LD offer currency on product page
- **Down4Sound**: stopped: robots.txt unreachable: retries exhausted: network error: ConnectTimeout
- **Dutchware Gear**: stopped: blocked: cloudflare challenge
- **ELAC**: /products.json: http 404, text/html; charset=UTF-8
- **EliteSRS**: no JSON-LD offer currency on product page
- **FINIS**: stopped: robots.txt unreachable: retries exhausted: network error: ConnectTimeout
- **Finn + Emma**: stopped: blocked: http 401
- **Force of Nature**: /products.json: http 404, text/html; charset=UTF-8
- **Galison**: stopped: retries exhausted: http 429
- **Garage Grown Gear**: stopped: blocked: cloudflare challenge
- **George Howell Coffee**: no JSON-LD offer currency on product page
- **Give'r**: /products.json: http 404, text/html; charset=iso-8859-1
- **Glamnetic**: stopped: blocked: cloudflare challenge
- **Glass Aqua**: /products.json: http 404, text/html; charset=UTF-8
- **GORUCK**: stopped: retries exhausted: http 429
- **Goughnuts**: /products.json: http 404, ?
- **Granite Gear**: /products.json: http 200, text/html; charset=UTF-8
- **Hepper**: stopped: blocked: cloudflare challenge
- **Holo Taco**: stopped: retries exhausted: http 429
- **Homecourt**: stopped: blocked: cloudflare challenge
- **Huckleberry Roasters**: /products.json: http 404, text/html
- **Injinji**: /products.json: http 404, text/html; charset=UTF-8
- **ISLE Surf & SUP**: /products.json: http 404, text/html
- **Itzy Ritzy**: stopped: blocked: cloudflare challenge (robots.txt)
- **Kassatex**: no JSON-LD offer currency on product page
- **Kate Quinn**: /products.json: http 404, ?
- **Kickee Pants**: stopped: retries exhausted: http 429
- **Kinetic**: /products.json: http 200, text/html
- **Kinetic Labs**: /products.json: http 200, text/html; charset=utf-8
- **Kitsch**: stopped: retries exhausted: http 429
- **Klipsch**: /products.json: http 404, text/html
- **Kokopelli Packraft**: stopped: robots.txt unreachable: retries exhausted: network error: ConnectError
- **KONO**: /products.json: http 200, text/html
- **Kopari**: /products.json: http 404, ?
- **KUHL**: /products.json: http 404, text/html; charset=utf-8
- **Kuma Coffee**: no JSON-LD offer currency on product page
- **LAFCO**: /products.json: http 404, text/html; charset=utf-8
- **Lambwolf Collective**: /products.json: http 404, text/html
- **Lander**: stopped: robots.txt unreachable: retries exhausted: network error: ConnectError
- **Lodge Cast Iron**: stopped: retries exhausted: http 429
- **Magnetic Me**: no JSON-LD offer currency on product page
- **Matouk**: stopped: retries exhausted: http 429; no JSON-LD offer currency on product page
- **Megababe**: stopped: robots.txt unreachable: retries exhausted: network error: ConnectError
- **MERACH**: /products.json: http 404, text/html; charset=utf-8
- **Metric Coffee**: no JSON-LD offer currency on product page
- **Mizzen+Main**: stopped: robots.txt unreachable: retries exhausted: http 429
- **Molly Mutt**: stopped: blocked: cloudflare challenge
- **Monica + Andy**: /products.json: http 404, text/html; charset=utf-8
- **Moon Audio**: stopped: retries exhausted: http 429
- **Natasha Denona**: no JSON-LD offer currency on product page
- **Neko Flies**: stopped: robots.txt unreachable: retries exhausted: network error: ConnectError
- **Nomad Lane**: stopped: blocked: cloudflare challenge
- **Nordic Ware**: stopped: blocked: imperva challenge (robots.txt)
- **Notary Ceramics**: stopped: retries exhausted: http 429
- **Olympia Coffee**: stopped: robots.txt unreachable: retries exhausted: network error: ConnectTimeout
- **Open Spaces**: /products.json: http 404, text/html; charset=utf-8
- **Passenger Coffee**: /products.json: http 404, text/html
- **Periodic Audio**: /products.json: http 404, text/html; charset=UTF-8
- **PicassoTiles**: stopped: retries exhausted: http 429
- **Proclamation Goods**: no JSON-LD offer currency on product page
- **Pulsar Gaming Gears**: no JSON-LD offer currency on product page
- **Quincy Mae**: stopped: blocked: cloudflare challenge
- **Rabbit Hole Hay**: no JSON-LD offer currency on product page
- **Revelate Designs**: stopped: blocked: cloudflare challenge
- **Rhoback**: /products.json: http 404, text/html
- **Ridge**: stopped: blocked: cloudflare block
- **Ritual Coffee Roasters**: stopped: blocked: http 403
- **Ruby Coffee Roasters**: product .js: http 404; product page: http 404
- **Rukket Sports**: /products.json: http 200, text/html
- **Rylee + Cru**: stopped: blocked: cloudflare challenge
- **Shimoda Designs**: /products.json: http 404, text/html; charset=UTF-8
- **Skar Audio**: /products.json: http 404, text/html; charset=utf-8
- **Sleepypod**: no JSON-LD offer currency on product page
- **Sonix**: /products.json: http 404, text/html; charset=UTF-8
- **Statik**: /products.json: http 404, text/html
- **Summersalt**: /products.json: http 200, text/html
- **The Detox Market**: stopped: retries exhausted: http 429
- **USA Pan**: stopped: blocked: http 403
- **Weston Backcountry**: no JSON-LD offer currency on product page
- **WODFitters**: /products.json: http 404, ?
- **Wolfgang Man & Beast**: stopped: robots.txt unreachable: retries exhausted: network error: ConnectError
- **Yamazaki Home**: stopped: robots.txt unreachable: retries exhausted: network error: ConnectError
- **ZMF Headphones**: stopped: robots.txt unreachable: retries exhausted: network error: ConnectError

## Terms of Service

`/policies/terms-of-service`, at most 2 requests per store, read only where robots.txt allows it: ban 154, no_ban 25, none_found 6.

| store | terms | source | first matching sentence |
|---|---|---|---|
| American Giant | ban | read | Such license is subject to these Site Terms and does not include: (a) any resale or commercial use … e and the Site Materials, or any portion thereof; (e) use of any data mining, robots or similar data gathering or extraction methods; (f) downloading (other than page caching) of any portion of … |
| Andie | ban | read | You may not copy, modify, distribute, or reverse-engineer any part of our website or content. |
| Anson Belt & Buckle | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the service is provided, without express written permission by us. |
| Bearbottom | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the service is provided, without express written permission by us. |
| Birdies | ban | read | In addition to other prohibitions as set forth in the Terms of Service, you are prohibited from … rsonal information of others; (i) to spam, phish, pharm, pretext, spider, crawl, or scrape; (j) for any obscene or immoral purpose; or (k) to interfere with or circumvent the security features of … |
| Bluffworks | ban | read | If you send us creative ideas, suggestions, customer reviews, photographs, proposals, plans, or … ree that the Company may, at any time, without restriction, edit, copy, publish, distribute, translate, and otherwise use in any medium any Comments that you forward to the Company is and shall be … |
| Christy Dawn | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the service is provided, without express written permission by us. |
| Cuyana | ban | read | Any unauthorized use of the Service, including without limitation, any commercial use (such as, for example, resale to third parties), is expressly prohibited. |
| Felix Gray | ban | read | If you choose to submit, either directly or indirectly, any Content or Submissions to the Service … sub-licensable, non-exclusive, worldwide, royalty-free license to reproduce, use, modify, display, perform, transmit, distribute, translate and create derivative works from any such Submissions or … |
| Fresh Clean Threads | ban | read | You promise to abide by all copyright notices, trademark rules, information, and restrictions … in any Content you access through the Services, and you won’t use, copy, reproduce, modify, translate, publish, broadcast, transmit, distribute, perform, upload, display, license, sell, commercialize … |
| goodr | ban | read | For companies or organizations providing corporate logos or trademarked images, it is your responsibility to ensure that any material supplied in any medium is not protected by any copyright law, or that any necessary permission for Company to reproduce the images has been obtained. |
| Greyson Clothiers | ban | read | To use any robot, spider, or other automatic device, process, or other means to crawl, scrape, or … otherwise access the Services, or use any means to reproduce or alter the navigational structure or presentation of the Services, for any purpose, including monitoring or copying any of the … |
| Hari Mari | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the service is provided, without express written permission by us. |
| Holderness & Bourne | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the service is provided, without express written permission by us. |
| Kiel James Patrick | no_ban | read | - |
| Lems Shoes | no_ban | read | - |
| Mission Belt | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the service is provided, without express written permission by us. |
| Naadam | no_ban | read | - |
| Nisolo | ban | read | Except for your Submitted Materials (as that term is defined below), the Company and our licensors … applets, other distributable applications, other visuals, video, copy and software), code, data and other materials thereon (collectively, the “Website Content”), the look and feel, design and … |
| Pair of Thieves | no_ban | read | - |
| Parade | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the service is provided, without express written permission by us. |
| Pit Viper | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the service is provided, without express written permission by us. |
| Wool& | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the service is provided, without express written permission by us. |
| 64 Audio | no_ban | read | - |
| Andover Audio | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the service is provided, without express written permission by us. |
| Crosley | no_ban | read | - |
| CT Sounds | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the service is provided, without express written permission by us. |
| Koss | ban | read | Without Koss’ prior written consent, you may not (a) use any automated means to access this Site or … t any information from this Site (including, without limitation, robots, spiders, scripts, or other automatic devices or programs), or (b) frame this Site, utilize framing techniques to enclose … |
| Noble Audio | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the Service is provided, without express written permission by us. |
| Peachtree Audio | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the Service is provided, without express written permission by us. |
| SOUNDBOKS | ban | read | You agree not to engage in any of the following prohibited activities: (i) copying, distributing, … , including without limitation by any automated or non-automated “scraping”; (ii) using any automated system, including without limitation “robots,” “spiders,” “offline readers,” etc., to access … |
| Thinksound | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the service is provided, without express written permission by us. |
| Westone Audio | ban | read | You may not reproduce (except as expressly provided hereunder), publish, transmit, distribute, display, modify, create derivative works from, sell, or exploit in any way any of such content or the Platform. |
| BH Cosmetics | ban | read | (There are separate terms which apply to your use of our site.) Please print or save these terms for future use as we will not keep a file copy specifically for the transaction with you and we cannot guarantee that they will remain accessible on our website in future. |
| Brickell Men's Products | ban | read | Material from this or any World Wide Web site owned, operated, licensed, or controlled by Brickell … ritten consent of Brickell, except that you may download one (1) copy of the material on one computer for your personal, non-commercial home use only. |
| Cirque Colors | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the Service is provided, without express written permission by us. |
| Duke Cannon | ban | read | Notwithstanding the foregoing, and subject to compliance with any instructions posted in the … robots.txt file located in the Site’s root directory, Company grants to the operators of public search engines permission to use spiders to copy materials from the Site for the sole purpose of (and … |
| Every Man Jack | ban | read | You must not reproduce, distribute, modify, create derivative works of, publicly display, publicly perform, republish, download, store, or transmit any of the material on our Website, except as follows: |
| Good Dye Young | ban | read | You will not modify, publish, transmit, reverse engineer, participate in the transfer or sale, create derivative works, or in any way exploit any of the content, in whole or in part, found on the Site. |
| Innersense Organic Beauty | no_ban | read | - |
| Juvia's Place | no_ban | read | - |
| K18 | ban | read | You may not modify the information or materials located on this website in any way or reproduce or publicly display, perform, or distribute or otherwise use any such materials for any public or commercial purpose. |
| Krave Beauty | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the Service is provided, without express written permission by us. |
| Laura Geller Beauty | ban | read | (b) In connection with the posting of Feedback, your use of the Interactive Services and/or your … r commercial purposes, without their express consent; (x) use any robot, spider, search/retrieval application or other manual or automatic device or process to retrieve, index, “data mine” or in … |
| Lime Crime | ban | read | You are prohibited from reproducing, copying, publishing, displaying, performing, modifying, creating derivative works from, transmitting, redistributing or in any way exploiting materials on the Platform for commercial purposes. |
| Mario Badescu | ban | read | We do not claim any ownership rights in any User Content and nothing in these Terms will be deemed to restrict any rights a User may have to use and exploit their own User Content. |
| Melt Cosmetics | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the service is provided, without express written permission by us. |
| Morphe | ban | read | Except as expressly authorized by Morphe, you agree not to modify , copy, frame, scrape, rent, lease, loan, sell, distribute, or create derivative works based on the Website, the Content or the Software, in whole or in part. |
| Natasha Denona | ban | read | You hereby further agree that you will not, directly or indirectly: (i) make any copies of, modify, … Services; (vi) use, access or attempt to access the Services via automated means; (vii) use the Company’s name, logo or trademarks without our prior written consent; or (viii) extract, collect … |
| Naturium | ban | read | Except as permitted by applicable law, you are not granted any rights in the Platform or its content and you may not reproduce, modify, create derivative works from, display, perform, publish, distribute or otherwise use any content without our prior written consent. |
| Olive & June | ban | read | Except as otherwise provided on the Site or in these Terms, you may not use, download, upload, … copy, print, display, perform, reproduce, publish, modify, delete, add to, license, post, transmit or distribute any Materials and Content from this Site in whole or in part, for any public or … |
| OSEA | ban | read | You must not reproduce, distribute, modify, create derivative works of, publicly display, publicly perform, republish, download, store, or transmit any of the material on the Services without our prior written consent. |
| Overtone | ban | read | Neither you, nor any other person or entity, will have the right to (i) receive any royalty or … ant to these Terms of Use or (ii) inspect or approve the editorial copy or other material that may be used in connection with the User Content. oVertone will be free to use any ideas, concepts, … |
| Pat McGrath Labs | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the service is provided, without express written permission by us. |
| Pattern Beauty | ban | read | You agree that you will not: (i) use the Site for any political or commercial purpose (including, … without limitation, for purposes of advertising, soliciting funds, collecting product prices, and selling products); (ii) use any meta tags or any other “hidden text” utilizing any Trademarks; … |
| Scotch Porter | none_found | robots.txt disallows /policies/terms-of-service | - |
| Ursa Major | ban | read | (b) You must not reproduce, distribute, modify, create derivative works of, publicly display, … publicly perform, republish, download, store or transmit any of the material on our Website, except as follows: (i) you may store files that are automatically cached by your web browser for display … |
| Verb | ban | read | You must not modify, copy, distribute, transmit, display, perform, reproduce, publish, license, create derivative works from, transfer, or sell any information, software, products or services obtained from the VERB PRODUCTS Websites, unless this is done for noncommercial purposes. |
| AeroPress | no_ban | read | - |
| Bellocq Tea Atelier | ban | read | 12.3 Subject to Clause 12.2 above, You may not copy, modify, alter, distribute, publish, sell or otherwise use any material on the Bellocq Website in whole or in part, unless You have obtained the prior written consent of Bellocq. |
| Big Shoulders Coffee | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the Service is provided, without express written permission by us. |
| Bird Rock Coffee Roasters | ban | read | You must not reproduce, distribute, modify, create derivative works of, publicly display, publicly perform, republish, download, store, or transmit any of the material on the Services without our prior written consent. |
| Black & White Coffee Roasters | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the service is provided, without express written permission by us. |
| Corvus Coffee | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the service is provided, without express written permission by us. |
| Cuvee Coffee | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the service is provided, without express written permission by us. |
| Devocion | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the service is provided, without express written permission by us. |
| Dogwood Coffee | none_found | no policy text | - |
| Encha | ban | read | The current version of these Terms is always available on our Website, however, we instruct you to save a copy of these Terms to your files as the past versions of the Terms may not be publicly available. |
| Four Barrel Coffee | no_ban | read | - |
| George Howell Coffee | ban | read | You may not modify, copy, distribute, transmit, display, perform, reproduce, publish, license, create derivative works from, transfer or sell any information, material, software, products and services or services from this Website. |
| Greater Goods Coffee | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the service is provided, without express written permission by us. |
| Heart Coffee Roasters | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the service is provided, without express written permission by us. |
| Irving Farm | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the service is provided, without express written permission by us. |
| Joe Coffee Company | ban | read | You must not reproduce, distribute, modify, create derivative works of, publicly display, publicly perform, republish, download, store, or transmit any of the material on the Services without our prior written consent. |
| Kuma Coffee | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the service is provided, without express written permission by us. |
| Little Wolf Coffee | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the Service is provided, without express written permission by us. |
| Madcap Coffee | no_ban | read | - |
| Methodical Coffee | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the service is provided, without express written permission by us. |
| Metric Coffee | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the service is provided, without express written permission by us. |
| PERC Coffee | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the Service is provided, without express written permission by us. |
| Pique | no_ban | read | - |
| Ratio Coffee | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the service is provided, without express written permission by us. |
| Ruby Coffee Roasters | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the service is provided, without express written permission by us. |
| Song Tea & Ceramics | ban | read | Users of the site are prohibited from: (i) modifying or otherwise making any derivative uses of the … Service or any portion thereof; (ii) using any data mining, robots or similar data gathering or extraction methods; (iii) reverse engineering or accessing the Service in order to build a … |
| Wonderstate Coffee | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the service is provided, without express written permission by us. |
| Bear Grips | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the service is provided, without express written permission by us. |
| Bear KompleX | no_ban | read | - |
| CRBN Pickleball | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the service is provided, without express written permission by us. |
| Ekrin Athletics | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the service is provided, without express written permission by us. |
| EliteSRS | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the service is provided, without express written permission by us. |
| Feedback Sports | no_ban | read | - |
| FLYBIRD Fitness | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the Service is provided, without express written permission by us. |
| GoSports | ban | read | You may download and/or copy certain portions of the Content for such purposes, provided that you … (a) retain all copyright, trademark or other proprietary notices contained on the Content, (b) do not modify or alter the Content in any way, and (c) do not distribute, modify, transmit, reuse, … |
| Major Fitness | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the service is provided, without express written permission by us. |
| RitFit | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the service is provided, without express written permission by us. |
| Sanabul | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the Service is provided, without express written permission by us. |
| Selkirk Sport | ban | read | Except as expressly authorized by Selkirk, you agree not to sell, license, distribute, copy, modify, publicly perform or display, transmit, publish, edit, adapt, create derivative works from, infringe upon, or otherwise make unauthorized use of the Selkirk Materials. |
| SPIbelt | no_ban | read | - |
| Spikeball | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the service is provided, without express written permission by us. |
| Yoga Design Lab | none_found | robots.txt disallows /policies/terms-of-service | - |
| Apotheke | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the service is provided, without express written permission by us. |
| Authenticity50 | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the service is provided, without express written permission by us. |
| Capri Blue | ban | read | Limited Access: You agree you will not use, directly or indirectly, any bot, spider, or other automatic method or means, nor any manual processes to copy any part or content of this Site. |
| Coming Soon | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the service is provided, without express written permission by us. |
| Dropps | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the service is provided, without express written permission by us. |
| Fishs Eddy | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the Service is provided, without express written permission by us. |
| Gravity Blanket | none_found | robots.txt disallows /policies/terms-of-service | - |
| Heritage Steel | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the service is provided, without express written permission by us. |
| Kassatex | no_ban | read | - |
| KINTO USA | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the service is provided, without express written permission by us. |
| Lostine | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the service is provided, without express written permission by us. |
| Meliora Cleaning Products | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the service is provided, without express written permission by us. |
| Paddywax | ban | read | The information on this site does not constitute a binding offer to sell products described on the site or to make such products available in your area. |
| Proclamation Goods | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the service is provided, without express written permission by us. |
| Riley Home | no_ban | read | - |
| Slow North | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the service is provided, without express written permission by us. |
| Voluspa | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the Service is provided, without express written permission by us. |
| Yield Design | no_ban | read | - |
| Barebones Living | no_ban | read | - |
| Cabeau | no_ban | read | - |
| Evergoods | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the Service is provided, without express written permission by us. |
| Feathered Friends | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the service is provided, without express written permission by us. |
| Flylow | none_found | robots.txt disallows /policies/terms-of-service | - |
| Jones Snowboards | none_found | robots.txt disallows /policies/terms-of-service | - |
| Minaal | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the service is provided, without express written permission by us. |
| Mission Workshop | ban | read | You must not reproduce, distribute, modify, create derivative works of, publicly display, publicly perform, republish, download, store, or transmit any of the material on the Services without our prior written consent. |
| Orange Mud | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the service is provided, without express written permission by us. |
| Paria Outdoor Products | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the service is provided, without express written permission by us. |
| Silca | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the service is provided, without express written permission by us. |
| So iLL | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the service is provided, without express written permission by us. |
| Strafe Outerwear | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the service is provided, without express written permission by us. |
| Tension Climbing | ban | read | You will not modify, publish, transmit, reverse engineer, participate in the transfer or sale, create derivative works, or in any way exploit any of the content, in whole or in part, found on the Site. |
| Vargo Outdoors | ban | read | You must not reproduce, distribute, modify, create derivative works of, publicly display, publicly perform, republish, download, store, or transmit any of the material on the Services without our prior written consent. |
| Weston Backcountry | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the service is provided, without express written permission by us. |
| Benebone | ban | read | You agree not to reproduce, duplicate, copy, sell, resell, or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the Service is provided, without express written permission by us. |
| Bocce's Bakery | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the service is provided, without express written permission by us. |
| Buce Plant | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the service is provided, without express written permission by us. |
| Diggs | ban | read | You agree not to: (i) use the Site to upload, transmit, display, or distribute any User Content … enerate automated searches, requests, or queries to (or to strip, scrape, or mine data from) the Site (provided, however, that we conditionally grant to the operators of public search engines … |
| Found My Animal | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the Service is provided, without express written permission by us. |
| Harry Barker | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the service is provided, without express written permission by us. |
| Mau Pets | ban | read | You agree not to reproduce, duplicate, copy, sell, resell, or exploit the Service without our written permission. |
| Max and Neo | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the service is provided, without express written permission by us. |
| Modkat | no_ban | read | - |
| P.L.A.Y. Pet Lifestyle and You | no_ban | read | - |
| Paw.com | ban | read | Unless otherwise agreed to in writing by Paw.com, you agree that you will not use the Services, or duplicate, download, publish, modify or otherwise distribute or use any material in the Services for any purpose, except for your personal, non-commercial use. |
| Pawz | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the service is provided, without express written permission by us. |
| Pet Krewe | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the service is provided, without express written permission by us. |
| Polkadog Bakery | no_ban | read | - |
| Pupford | no_ban | read | - |
| Rabbit Hole Hay | ban | read | You may not distribute, modify, transmit, reuse, repost, or use the Site’s content (including text, images, audio, or video) for public or commercial purposes without Rabbit Hole Hay’s prior written permission. |
| Shameless Pets | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the service is provided, without express written permission by us. |
| Sleepypod | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the Service is provided, without express written permission by us. |
| Zee.Dog | ban | read | You must not reproduce, distribute, modify, create derivative works of, publicly display, publicly perform, republish, download, store, or transmit any of the material on the Services without our prior written consent. |
| CannonKeys | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the service is provided, without express written permission by us. |
| Caudabe | ban | read | 1.3 You may not use the Service: (a) to infringe our intellectual property rights or those of … t or track the personal information of others; (f) to spam, phish, scrape, crawl or use automated tools to access the Service without our written permission; or (g) to interfere with or get around the … |
| Divinikey | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the service is provided, without express written permission by us. |
| Freewell | ban | read | Misuse of Content: The user is prohibited from using the website's content for non-personal or commercial purposes, including reproduction, distribution, display, sale, lease, transmission, and modification, without express written permission. |
| Glorious | ban | read | You may not copy, reproduce, modify, republish, upload, post, transmit, or distribute any documents … or information from this site in any form or by any means without prior written permission from us or the specific content provider, and you are solely responsible for obtaining permission … |
| Incase | ban | read | You may not reproduce (except as noted above), publish, transmit, distribute, display, modify, create derivative works of, sell or participate in any sale of, or exploit in any way, in whole or in part, any of the Contents or the Site. |
| Loopy Cases | ban | read | You agree not to reproduce, duplicate, copy, sell, resell, or exploit any portion of the Service, use of the Service, or access to the Service, or any contact on the website through which the service is provided, without our express written permission. |
| Mode Designs | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the service is provided, without express written permission by us. |
| Native Union | ban | read | 6.4 - You must not copy, modify, distribute, sell, lease, loan or trade any access to the Website or any data or information on it. |
| NovelKeys | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the service is provided, without express written permission by us. |
| Pulsar Gaming Gears | ban | read | You agree not to reproduce, duplicate, copy, sell, resell, or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the service is provided, without express written permission by us. |
| SANDMARC | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the service is provided, without express written permission by us. |
| Smartish | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the service is provided, without express written permission by us. |
| Avanchy | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the service is provided, without express written permission by us. |
| Bannor Toys | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the service is provided, without express written permission by us. |
| Bellabu Bear | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the service is provided, without express written permission by us. |
| Boba | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the service is provided, without express written permission by us. |
| Comotomo | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the service is provided, without express written permission by us. |
| Freshly Picked | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the service is provided, without express written permission by us. |
| Hazel Village | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the service is provided, without express written permission by us. |
| Kid Made Modern | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the service is provided, without express written permission by us. |
| Leder Games | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the service is provided, without express written permission by us. |
| Magna-Tiles | ban | read | If you submit content (e.g., contest entries, creative ideas, suggestions, proposals, plans, or other materials), you agree that we may edit, copy, publish, distribute, translate and otherwise use any comments that you forward to us without restriction. |
| Magnetic Me | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the service is provided, without express written permission by us. |
| Manhattan Toy | ban | read | You agree not to reproduce, duplicate, copy, sell, resell, or exploit any portion of the Service without our express written permission. |
| Mudpuppy | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the service is provided, without express written permission by us. |
| Pehr | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the service is provided, without express written permission by us. |
| Piccalio | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the service is provided, without express written permission by us. |
| The Beaufort Bonnet Company | ban | read | You may not modify, copy, reproduce, republish, upload, post, transmit, or distribute any portion of the Website contents without the prior express written consent of The Beaufort Bonnet Company. |
| Unstable Games | ban | read | You are not authorized to reproduce, republish, distribute, transmit, modify, sell or otherwise use the Content, or to create derivative works based on the Content, in whole or in part, without our express written authorization. |
| Wee Gallery | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the service is provided, without express written permission by us. |
| WildBird | no_ban | read | - |
