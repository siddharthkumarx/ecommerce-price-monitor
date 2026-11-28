# Recon `recon-008`

- started: 2026-11-27T22:36:02+00:00, finished: 2026-11-28T00:32:27+00:00
- run: https://github.com/siddharthkumarx/ecommerce-price-monitor/actions/runs/46069789967
- candidates: 172, passed: 70 (variant cap 3000)
- run-wide request interval: 4.0s + jitter; halted: no

| store | category | host | robots | products.json | .js | reachable | shopify | products | variants | in stock | .js check | JSON-LD cur | Shopify cur | meta country | reqs | terms | result |
|---|---|---|---|---|---|---|---|---:|---:|---:|---|---|---|---|---:|---|---|
| 3sixteen | apparel | www.3sixteen.com | ok | yes | yes | yes | yes | - | - | - | match | USD | USD | US | 9 | - | fail: blocked mid-recon, empty catalog, needed 429 retries |
| Able Carry | apparel | ablecarry.com | ok | yes | yes | yes | yes | 94 | 226 | 76% | match | USD | USD | HK | 6 | ban | PASS |
| Alo Yoga | apparel | www.aloyoga.com | ok | yes | yes | yes | yes | 228 | 1109 | 46% | match | USD | USD | US | 6 | ban | PASS |
| Beckett Simonon | apparel | www.beckettsimonon.com | ok | yes | yes | yes | yes | 228 | 10669 | 99% | match | - | USD | US | 6 | ban | fail: catalog too large |
| Beyond Yoga | apparel | beyondyoga.com | ok | yes | yes | yes | yes | 500 | 3135+ | 81% | match | USD | USD | US | 6 | none_found | fail: catalog too large, excluded category: alcohol |
| Chaser | apparel | www.chaserbrand.com | ok | yes | yes | no | no | - | - | - | - | - | - | - | 2 | - | fail: blocked |
| Chrome Industries | apparel | chromeindustries.com | ok | yes | yes | yes | yes | 93 | 637 | 53% | match | USD | USD | US | 6 | ban | PASS |
| Code of Bell | apparel | www.codeofbell.com | ok | yes | yes | yes | yes | 30 | 59 | 76% | match | - | USD | US | 6 | ban | PASS |
| Comrad | apparel | www.comradsocks.com | ok | yes | yes | yes | yes | 250 | 4681+ | 93% | match | USD | USD | US | 5 | none_found | fail: catalog too large |
| Dossier | apparel | dossier.co | ok | yes | yes | yes | no | - | - | - | - | - | - | - | 2 | - | fail: not shopify |
| Glyder | apparel | www.glyderapparel.com | ok | yes | yes | yes | yes | - | - | - | match | - | USD | US | 9 | - | fail: blocked mid-recon, empty catalog, needed 429 retries |
| Good American | apparel | www.goodamerican.com | ok | yes | yes | yes | yes | 500 | 5151+ | 59% | match | USD | USD | US | 7 | ban | fail: catalog too large, excluded category: tobacco/vape |
| Gorjana | apparel | www.gorjana.com | ok | yes | yes | yes | yes | 249 | 774 | 100% | match | USD | USD | US | 6 | ban | PASS |
| Grant Stone | apparel | www.grantstoneshoes.com | ok | yes | yes | yes | yes | 244 | 5324 | 75% | match | USD | USD | US | 6 | ban | fail: catalog too large, excluded category: tobacco/vape |
| Hanky Panky | apparel | www.hankypanky.com | ok | yes | yes | yes | yes | - | - | - | match | USD | USD | US | 9 | - | fail: blocked mid-recon, empty catalog, needed 429 retries |
| Hey Dude | apparel | www.heydude.com | ok | yes | yes | yes | no | - | - | - | - | - | - | - | 2 | - | fail: not shopify |
| Jambys | apparel | www.jambys.com | ok | yes | yes | yes | yes | 76 | 812 | 100% | match | USD | USD | US | 6 | no_ban | PASS |
| Kendra Scott | apparel | www.kendrascott.com | ok | no | yes | no | no | - | - | - | - | - | - | - | 1 | - | fail: robots disallows |
| Kinn | apparel | kinnstudio.com | ok | yes | yes | yes | yes | 750 | 3132+ | 88% | match | USD | USD | US | 8 | ban | fail: catalog too large, excluded category: tobacco/vape |
| Ledbury | apparel | www.ledbury.com | ok | yes | yes | yes | yes | - | - | - | match | USD | USD | US | 9 | - | fail: blocked mid-recon, empty catalog, needed 429 retries |
| Left Field NYC | apparel | leftfieldnyc.com | ok | yes | yes | yes | yes | 223 | 1302 | 48% | match | USD | USD | US | 6 | ban | PASS |
| MeUndies | apparel | meundies.com | unreachable | - | - | no | no | - | - | - | - | - | - | - | 4 | - | fail: blocked, needed 429 retries |
| Minus33 | apparel | minus33.com | ok | yes | yes | yes | yes | 164 | 2475 | 84% | match | USD | USD | US | 6 | ban | PASS |
| MVMT | apparel | mvmt.com | ok | yes | yes | yes | yes | 441 | 473 | 80% | match | USD | USD | US | 7 | ban | fail: excluded category: alcohol |
| Nicks Boots | apparel | nicksboots.com | ok | yes | yes | yes | yes | 514 | 1598 | 98% | match | USD | USD | US | 8 | ban | PASS |
| Nobull | apparel | nobullproject.com | ok | no | yes | no | no | - | - | - | - | - | - | - | 1 | - | fail: robots disallows |
| Oak Street Bootmakers | apparel | oakstreetbootmakers.com | ok | no | yes | no | no | - | - | - | - | - | - | - | 1 | - | fail: robots disallows |
| Original Grain | apparel | www.originalgrain.com | ok | yes | yes | yes | yes | - | - | - | match | USD | USD | US | 10 | - | fail: blocked mid-recon, empty catalog, needed 429 retries |
| Outlier | apparel | outlier.nyc | ok | yes | yes | yes | no | - | - | - | - | - | - | - | 2 | - | fail: not shopify |
| Peter Manning NYC | apparel | petermanningnyc.com | ok | yes | yes | yes | yes | 321 | 4171 | 58% | match | USD | USD | US | 7 | ban | fail: catalog too large |
| Pistol Lake | apparel | www.pistollake.com | ok | yes | yes | yes | yes | 0 | 0 | - | - | - | - | US | 4 | ban | fail: empty catalog, currency not proven USD, product .js unavailable |
| Popov Leather | apparel | www.popovleather.com | ok | yes | yes | yes | yes | 118 | 1487 | 98% | match | - | USD | CA | 6 | ban | PASS |
| Pura Vida | apparel | www.puravidabracelets.com | ok | yes | yes | yes | yes | - | - | - | match | USD | USD | US | 10 | - | fail: blocked mid-recon, empty catalog, needed 429 retries |
| Quoddy | apparel | www.quoddy.com | ok | yes | yes | yes | yes | - | - | - | match | USD | USD | US | 9 | - | fail: blocked mid-recon, empty catalog, needed 429 retries |
| Rainbow Sandals | apparel | www.rainbowsandals.com | ok | yes | yes | yes | no | - | - | - | - | - | - | - | 2 | - | fail: not shopify |
| Rancourt & Co. | apparel | www.rancourtandcompany.com | ok | yes | yes | yes | yes | 197 | 4103 | 70% | match | USD | USD | US | 6 | ban | fail: catalog too large |
| Saddleback Leather | apparel | saddlebackleather.com | ok | yes | yes | yes | yes | 699 | 2385 | 86% | match | USD | USD | US | 8 | ban | fail: excluded category: tobacco/vape, weapons |
| Set Active | apparel | setactive.co | ok | yes | yes | yes | yes | 250 | 3507+ | 59% | match | - | USD | US | 6 | ban | fail: catalog too large |
| Shinesty | apparel | shinesty.com | ok | yes | yes | yes | yes | 500 | 3261+ | 68% | match | USD | USD | US | 7 | ban | fail: catalog too large |
| Show Me Your Mumu | apparel | showmeyourmumu.com | ok | yes | yes | yes | yes | 750 | 4113+ | 73% | match | USD | USD | US | 8 | ban | fail: catalog too large, excluded category: alcohol |
| Spanx | apparel | spanx.com | ok | yes | yes | yes | no | - | - | - | - | - | - | - | 2 | - | fail: not shopify |
| Stance | apparel | www.stance.com | ok | yes | yes | yes | yes | - | - | - | match | USD | USD | US | 9 | - | fail: blocked mid-recon, empty catalog, needed 429 retries |
| Taft | apparel | taftclothing.com | ok | yes | yes | yes | yes | 253 | 2974 | 59% | match | USD | USD | US | 7 | ban | PASS |
| Tanner Goods | apparel | www.tannergoods.com | ok | yes | yes | yes | yes | 232 | 1073 | 80% | match | USD | USD | US | 6 | ban | PASS |
| Tecovas | apparel | www.tecovas.com | ok | yes | yes | yes | no | - | - | - | - | - | - | - | 2 | - | fail: not shopify |
| Thinx | apparel | www.thinx.com | ok | yes | yes | yes | yes | 33 | 558 | 99% | match | USD | USD | US | 5 | none_found | PASS |
| Thursday Boot Company | apparel | thursdayboots.com | ok | yes | yes | yes | yes | 500 | 5348+ | 81% | match | USD | USD | US | 7 | ban | fail: catalog too large |
| Tipsy Elves | apparel | www.tipsyelves.com | ok | yes | yes | yes | yes | - | - | - | match | USD | USD | US | 9 | - | fail: blocked mid-recon, empty catalog, needed 429 retries |
| Truman Boot Co. | apparel | trumanboots.com | ok | no | no | no | no | - | - | - | - | - | - | - | 1 | - | fail: robots disallows |
| UNTUCKit | apparel | www.untuckit.com | ok | yes | yes | yes | yes | - | - | - | match | USD | USD | US | 9 | - | fail: blocked mid-recon, empty catalog, needed 429 retries |
| Vincero | apparel | vincerocollective.com | ok | yes | yes | yes | yes | 688 | 1859 | 80% | match | - | USD | US | 8 | ban | PASS |
| Woolx | apparel | www.woolx.com | ok | yes | yes | yes | yes | - | - | - | match | USD | USD | US | 9 | - | fail: blocked mid-recon, empty catalog, needed 429 retries |
| Xero Shoes | apparel | xeroshoes.com | ok | yes | yes | yes | yes | 155 | 7247 | 62% | match | USD | USD | US | 6 | ban | fail: catalog too large |
| Balanced Body | fitness | www.pilates.com | ok | yes | yes | yes | no | - | - | - | - | - | - | - | 2 | - | fail: not shopify |
| Bob and Brad | fitness | www.bobandbrad.com | ok | yes | yes | yes | no | - | - | - | - | - | - | - | 2 | - | fail: not shopify |
| Bombshell Sportswear | fitness | www.bombshellsportswear.com | ok | yes | yes | yes | yes | - | - | - | match | USD | USD | US | 10 | - | fail: blocked mid-recon, empty catalog, needed 429 retries |
| CAP Barbell | fitness | capbarbell.com | ok | yes | yes | yes | yes | 356 | 1434 | 84% | match | USD | USD | US | 7 | ban | PASS |
| Compex | fitness | www.compex.com | ok | yes | yes | yes | yes | 78 | 155 | 81% | match | EUR,GBP | GBP | FR | 6 | no_ban | fail: currency not proven USD |
| Elevate Jump Ropes | fitness | www.elevaterope.com | ok | yes | yes | yes | yes | 111 | 369 | 66% | match | USD | USD | NL | 5 | none_found | PASS |
| Elliptigo | fitness | elliptigo.com | ok | yes | yes | no | no | - | - | - | - | - | - | - | 2 | - | fail: blocked |
| Ergatta | fitness | ergatta.com | ok | yes | yes | yes | yes | 66 | 189 | 87% | match | USD | USD | US | 6 | ban | PASS |
| Gamma Sports | fitness | gammasports.com | ok | yes | yes | yes | yes | 236 | 514 | 87% | match | USD | USD | US | 6 | no_ban | PASS |
| Hydrow | fitness | hydrow.com | unreachable | - | - | no | no | - | - | - | - | - | - | - | 4 | - | fail: blocked, needed 429 retries |
| Hylete | fitness | hylete.com | ok | yes | yes | yes | yes | 122 | 710 | 62% | match | USD | USD | US | 6 | ban | PASS |
| Inspire Fitness | fitness | inspirefitness.com | ok | yes | yes | yes | yes | 58 | 60 | 95% | match | USD | USD | US | 6 | ban | PASS |
| Iron Bull Strength | fitness | ironbullstrength.com | ok | yes | yes | yes | yes | 46 | 837 | 73% | match | USD | USD | CA | 6 | ban | PASS |
| Ironmaster | fitness | ironmaster.com | ok | yes | yes | yes | yes | 134 | 204 | 71% | match | USD | USD | US | 6 | ban | PASS |
| Lebert Fitness | fitness | lebertfitness.com | ok | yes | yes | yes | yes | 42 | 64 | 100% | match | USD | USD | CA | 6 | ban | PASS |
| Marc Pro | fitness | marcpro.com | ok | yes | yes | no | no | - | - | - | - | - | - | - | 2 | - | fail: blocked |
| Metolius | fitness | www.metoliusclimbing.com | ok | yes | yes | yes | yes | 187 | 594 | 89% | match | USD | USD | US | 6 | ban | PASS |
| Oko Living | fitness | okoliving.com | ok | yes | yes | yes | yes | 37 | 99 | 81% | match | USD | USD | US | 6 | ban | PASS |
| Onnit | fitness | www.onnit.com | ok | yes | yes | yes | yes | 33 | 33 | 100% | match | USD | USD | US | 6 | ban | PASS |
| Opove | fitness | www.opove.com | ok | yes | yes | yes | yes | 8 | 14 | 79% | match | USD | USD | SG | 6 | ban | PASS |
| Organic Climbing | fitness | organicclimbing.com | ok | yes | yes | yes | yes | 174 | 667 | 74% | match | USD | USD | US | 6 | ban | PASS |
| PowerDot | fitness | powerdot.com | missing-4xx | yes | yes | yes | no | - | - | - | - | - | - | - | 2 | - | fail: not shopify |
| Prime Fitness | fitness | www.primefitnessusa.com | ok | yes | yes | yes | yes | 190 | 668 | 98% | match | USD | USD | US | 6 | ban | PASS |
| Recoup Fitness | fitness | trinityurgentcare.org | ok | yes | yes | yes | no | - | - | - | - | - | - | - | 2 | - | fail: not shopify |
| Saris | fitness | saris.com | ok | yes | yes | yes | yes | 192 | 292 | 86% | match | USD | USD | US | 6 | no_ban | PASS |
| SHEFIT | fitness | shefit.com | ok | yes | yes | yes | yes | 65 | 574 | 83% | match | USD | USD | US | 6 | ban | PASS |
| Sorinex | fitness | www.sorinex.com | ok | yes | yes | yes | no | - | - | - | - | - | - | - | 2 | - | fail: not shopify |
| Stroops | fitness | stroops.com | ok | yes | yes | yes | yes | 90 | 257 | 98% | match | USD | USD | US | 6 | ban | PASS |
| TLF Apparel | fitness | tlfapparel.com | ok | yes | yes | yes | no | - | - | - | - | - | - | - | 2 | - | fail: not shopify |
| Trango | fitness | trango.com | ok | yes | yes | yes | yes | 250 | 6134+ | 36% | match | USD | USD | US | 6 | ban | fail: catalog too large |
| Tumbl Trak | fitness | www.tumbltrak.com | ok | yes | yes | yes | no | - | - | - | - | - | - | - | 2 | - | fail: not shopify |
| Ultimate Direction | fitness | ultimatedirection.com | ok | yes | yes | yes | no | - | - | - | - | - | - | - | 2 | - | fail: not shopify |
| Valor Fitness | fitness | valorfitness.com | ok | yes | yes | yes | yes | 323 | 784 | 82% | match | USD | USD | US | 7 | ban | PASS |
| XMark Fitness | fitness | xmarkfitness.com | ok | yes | yes | yes | yes | 141 | 424 | 94% | match | USD | USD | US | 6 | ban | PASS |
| Yes4All | fitness | yes4all.com | ok | yes | yes | yes | no | - | - | - | - | - | - | - | 2 | - | fail: not shopify |
| amFilm | tech_accessories | amfilm.com | unreachable | - | - | no | no | - | - | - | - | - | - | - | 4 | - | fail: blocked |
| Analogue | tech_accessories | www.analogue.co | ok | yes | yes | yes | no | - | - | - | - | - | - | - | 2 | - | fail: not shopify |
| Anker | tech_accessories | www.anker.com | ok | yes | yes | yes | no | - | - | - | - | - | - | - | 2 | - | fail: not shopify |
| Arkon | tech_accessories | arkon.com | ok | yes | yes | yes | yes | 871 | 1033 | 100% | match | USD | USD | US | 9 | ban | fail: excluded category: weapons |
| Autonomous | tech_accessories | www.autonomous.ai | ok | yes | yes | yes | no | - | - | - | - | - | - | - | 2 | - | fail: not shopify |
| Bluelounge | tech_accessories | shopadvantus.com | missing-4xx | yes | yes | yes | yes | 105 | 137 | 95% | match | USD | USD | US | 6 | none_found | PASS |
| BoxWave | tech_accessories | boxwave.com | ok | yes | yes | no | no | - | - | - | - | - | - | - | 2 | - | fail: blocked |
| Brydge | tech_accessories | brydge.com | ok | yes | yes | yes | yes | 29 | 72 | 82% | match | USD | USD | US | 6 | ban | PASS |
| Caseology | tech_accessories | caseology.com | ok | yes | yes | yes | no | - | - | - | - | - | - | - | 2 | - | fail: not shopify |
| Catalyst | tech_accessories | catalystcase.com | ok | yes | yes | yes | yes | 154 | 789 | 76% | match | USD | USD | US | 6 | ban | PASS |
| Element Case | tech_accessories | elementcase.com | ok | yes | yes | yes | no | - | - | - | - | - | - | - | 2 | - | fail: not shopify |
| ESR | tech_accessories | www.esrtech.com | ok | yes | yes | yes | yes | 247 | 247 | 100% | match | USD | USD | HK | 6 | ban | PASS |
| Finalmouse | tech_accessories | finalmouse.com | ok | yes | yes | yes | yes | 33 | 67 | 0% | match | USD | USD | US | 6 | ban | PASS |
| HyperDrive | tech_accessories | www.hypershop.com | ok | yes | yes | yes | yes | 84 | 108 | 82% | match | USD | USD | US | 6 | ban | PASS |
| Incipio | tech_accessories | incipio.com | ok | yes | yes | yes | yes | 202 | 449 | 82% | match | USD | USD | US | 6 | no_ban | PASS |
| ModRetro | tech_accessories | modretro.com | ok | yes | yes | yes | yes | 47 | 90 | 99% | match | USD | USD | US | 6 | ban | PASS |
| Moment | tech_accessories | www.shopmoment.com | ok | yes | yes | yes | yes | 311 | 2333 | 90% | match | USD | USD | US | 7 | ban | fail: excluded category: weapons |
| Nekteck | tech_accessories | nekteck.com | ok | yes | yes | yes | yes | 78 | 108 | 50% | match | USD | USD | US | 6 | ban | PASS |
| Nite Ize | tech_accessories | niteize.com | ok | no | no | no | no | - | - | - | - | - | - | - | 1 | - | fail: robots disallows |
| Nonda | tech_accessories | www.nonda.co | ok | yes | yes | yes | yes | 20 | 26 | 100% | match | - | USD | US | 6 | ban | PASS |
| PopSockets | tech_accessories | www.popsockets.com | ok | yes | yes | yes | no | - | - | - | - | - | - | - | 2 | - | fail: not shopify |
| ProClip USA | tech_accessories | www.proclipusa.com | ok | yes | yes | yes | no | - | - | - | - | - | - | - | 2 | - | fail: not shopify |
| Retro-Bit | tech_accessories | retro-bit.com | missing-4xx | yes | yes | yes | no | - | - | - | - | - | - | - | 2 | - | fail: not shopify |
| Rocketbook | tech_accessories | getrocketbook.com | ok | yes | yes | yes | yes | 52 | 276 | 59% | match | USD | USD | US | 6 | ban | PASS |
| Scosche | tech_accessories | scosche.com | ok | yes | yes | yes | yes | 658 | 732 | 92% | match | USD | USD | US | 8 | none_found | PASS |
| Spider Holster | tech_accessories | spiderholster.com | ok | yes | yes | yes | yes | 136 | 260 | 88% | match | USD | USD | US | 6 | ban | fail: excluded category: weapons |
| Tech Armor | tech_accessories | techarmor.com | ok | no | no | no | no | - | - | - | - | - | - | - | 1 | - | fail: robots disallows |
| Thinborne | tech_accessories | thinborne.com | ok | yes | yes | yes | yes | 87 | 87 | 86% | match | - | USD | US | 6 | ban | PASS |
| Think Tank Photo | tech_accessories | www.thinktankphoto.com | ok | yes | yes | yes | yes | 138 | 241 | 88% | match | - | USD | US | 6 | ban | fail: excluded category: weapons |
| Tom Bihn | tech_accessories | www.tombihn.com | ok | yes | yes | yes | yes | 159 | 2034 | 33% | match | USD | USD | US | 6 | no_ban | PASS |
| UGREEN (US) | tech_accessories | www.ugreen.com | ok | yes | yes | yes | yes | - | - | - | missing | - | - | HK | 9 | - | fail: blocked mid-recon, empty catalog, currency not proven USD, product .js unavailable, needed 429 retries |
| Ztylus | tech_accessories | ztylus.com | missing-4xx | yes | yes | yes | no | - | - | - | - | - | - | - | 2 | - | fail: not shopify |
| Allplay | toys_kids | allplay.com | ok | yes | yes | yes | no | - | - | - | - | - | - | - | 2 | - | fail: not shopify |
| Angel Dear | toys_kids | angeldear.com | ok | yes | yes | yes | yes | 249 | 712 | 56% | match | USD | USD | US | 6 | no_ban | PASS |
| Avenlur | toys_kids | avenlur.com | ok | yes | yes | yes | yes | 242 | 316 | 89% | match | USD | USD | US | 6 | ban | PASS |
| Baby Brezza | toys_kids | babybrezza.com | ok | yes | yes | yes | yes | 61 | 145 | 99% | match | USD | USD | US | 6 | no_ban | PASS |
| Babyletto | toys_kids | babyletto.com | ok | yes | yes | yes | yes | 283 | 1043 | 91% | match | USD | USD | US | 7 | ban | PASS |
| Bitsbox | toys_kids | bitsbox.com | ok | yes | yes | yes | no | - | - | - | - | - | - | - | 2 | - | fail: not shopify |
| Busy Baby | toys_kids | busybabyproducts.com | unreachable | - | - | no | no | - | - | - | - | - | - | - | 4 | - | fail: blocked |
| Coterie | toys_kids | www.coterie.com | ok | yes | yes | yes | no | - | - | - | - | - | - | - | 2 | - | fail: not shopify |
| Cuddle + Kind | toys_kids | cuddleandkind.com | ok | yes | yes | yes | yes | 368 | 584 | 76% | match | USD | USD | US | 7 | ban | PASS |
| Ergobaby | toys_kids | ergobaby.com | ok | yes | yes | no | no | - | - | - | - | - | - | - | 2 | - | fail: blocked |
| Esembly | toys_kids | esembly.com | ok | no | no | no | no | - | - | - | - | - | - | - | 1 | - | fail: robots disallows |
| Fat Brain Toys | toys_kids | fatbraintoys.com | ok | yes | yes | no | no | - | - | - | - | - | - | - | 2 | - | fail: blocked |
| Floodgate Games | toys_kids | floodgate.games | ok | yes | yes | yes | yes | 69 | 89 | 49% | match | USD | USD | US | 6 | ban | PASS |
| Four Point Puzzles | toys_kids | parksidepuzzles.com | ok | yes | yes | yes | yes | 52 | 52 | 52% | match | USD | USD | CA | 6 | ban | PASS |
| Greater Than Games | toys_kids | greaterthangames.com | ok | yes | yes | yes | no | - | - | - | - | - | - | - | 2 | - | fail: not shopify |
| GroVia | toys_kids | www.grovia.com | ok | yes | yes | yes | yes | 60 | 190 | 28% | match | USD | USD | US | 6 | no_ban | PASS |
| HABA USA | toys_kids | www.habausa.com | ok | yes | yes | yes | yes | 432 | 473 | 94% | match | USD | USD | US | 7 | no_ban | PASS |
| hand2mind | toys_kids | hand2mind.com | unreachable | - | - | no | no | - | - | - | - | - | - | - | 1 | - | fail: blocked |
| Hatch | toys_kids | www.hatch.co | ok | yes | yes | yes | no | - | - | - | - | - | - | - | 2 | - | fail: not shopify |
| Hello Bello | toys_kids | www.hellobello.com | ok | yes | yes | no | no | - | - | - | - | - | - | - | 2 | - | fail: blocked |
| Joovy | toys_kids | www.joovy.com | ok | yes | yes | yes | yes | 119 | 237 | 83% | match | USD | USD | US | 6 | ban | PASS |
| Keymaster Games | toys_kids | keymaster.fun | ok | yes | yes | yes | yes | 30 | 36 | 72% | match | USD | USD | US | 6 | ban | PASS |
| Kudos | toys_kids | mykudos.com | ok | yes | yes | yes | yes | 5 | 16 | 100% | match | USD | USD | US | 6 | ban | PASS |
| Liberty Puzzles | toys_kids | libertypuzzles.com | ok | yes | yes | yes | yes | 581 | 606 | 100% | match | USD | USD | US | 8 | ban | fail: excluded category: alcohol |
| Magnolia Baby | toys_kids | magnoliababy.com | ok | yes | yes | yes | yes | 750 | 3813+ | 65% | match | USD | USD | US | 8 | ban | fail: catalog too large |
| Maple Landmark | toys_kids | maplelandmark.com | ok | yes | yes | yes | yes | 806 | 1747 | 100% | match | USD | USD | US | 9 | none_found | fail: excluded category: alcohol |
| Mightly | toys_kids | www.mightly.com | ok | yes | yes | yes | yes | - | - | - | match | - | USD | US | 9 | - | fail: blocked mid-recon, empty catalog, needed 429 retries |
| Monti Kids | toys_kids | montikids.com | ok | no | no | no | no | - | - | - | - | - | - | - | 1 | - | fail: robots disallows |
| Munchkin | toys_kids | www.munchkin.com | ok | yes | yes | yes | no | - | - | - | - | - | - | - | 2 | - | fail: not shopify |
| Nanit | toys_kids | www.nanit.com | ok | yes | yes | yes | yes | 37 | 163 | 76% | match | USD | USD | US | 6 | no_ban | PASS |
| New York Puzzle Company | toys_kids | www.newyorkpuzzlecompany.com | ok | yes | yes | yes | yes | 423 | 426 | 86% | match | USD | USD | US | 7 | ban | fail: excluded category: alcohol |
| Osmo | toys_kids | www.playosmo.com | ok | yes | yes | yes | yes | 52 | 63 | 97% | match | USD | USD | US | 6 | ban | PASS |
| Owlet | toys_kids | owletcare.com | ok | yes | yes | yes | yes | 24 | 58 | 79% | match | USD | USD | US | 6 | no_ban | PASS |
| Pandasaurus Games | toys_kids | pandasaurusgames.com | ok | yes | yes | yes | yes | 80 | 80 | 96% | match | USD | USD | US | 6 | ban | PASS |
| Petite Plume | toys_kids | petiteplume.com | unreachable | - | - | no | no | - | - | - | - | - | - | - | 4 | - | fail: blocked |
| Pomegranate | toys_kids | www.pomegranate.com | ok | yes | yes | yes | yes | - | - | - | match | USD | USD | US | 10 | - | fail: blocked mid-recon, empty catalog, needed 429 retries |
| Primary | toys_kids | www.primary.com | ok | yes | yes | yes | yes | - | - | - | match | USD | USD | US | 9 | - | fail: blocked mid-recon, empty catalog, needed 429 retries |
| Radio Flyer | toys_kids | www.radioflyer.com | ok | yes | yes | yes | yes | - | - | - | match | USD | USD | US | 9 | - | fail: blocked mid-recon, empty catalog, needed 429 retries |
| Renegade Game Studios | toys_kids | renegadegamestudios.com | ok | yes | yes | yes | no | - | - | - | - | - | - | - | 2 | - | fail: not shopify |
| Restoration Games | toys_kids | restorationgames.com | ok | yes | yes | yes | no | - | - | - | - | - | - | - | 2 | - | fail: not shopify |
| Snap Circuits (Elenco) | toys_kids | elenco.com | ok | yes | yes | yes | no | - | - | - | - | - | - | - | 2 | - | fail: not shopify |
| Springbok Puzzles | toys_kids | www.springbok-puzzles.com | ok | yes | yes | yes | no | - | - | - | - | - | - | - | 2 | - | fail: not shopify |
| Stonemaier Games | toys_kids | stonemaiergames.com | ok | yes | yes | yes | no | - | - | - | - | - | - | - | 2 | - | fail: not shopify |
| Thames & Kosmos | toys_kids | thamesandkosmos.com | ok | yes | yes | yes | yes | 347 | 350 | 82% | match | USD | USD | US | 7 | ban | PASS |
| The Ollie World | toys_kids | theollieworld.com | ok | yes | yes | yes | yes | 12 | 149 | 96% | match | - | USD | US | 6 | ban | PASS |
| Thirsties | toys_kids | thirsties.com | ok | no | no | no | no | - | - | - | - | - | - | - | 1 | - | fail: robots disallows |
| Thunderworks Games | toys_kids | thunderworksgames.com | ok | yes | yes | yes | yes | 108 | 408 | 89% | match | - | USD | US | 6 | ban | PASS |
| Tiny Land | toys_kids | www.tinylandus.com | ok | yes | yes | yes | yes | 121 | 294 | 97% | match | USD | USD | US | 6 | ban | PASS |
| Ubbi | toys_kids | ubbiworld.com | ok | yes | yes | yes | yes | 120 | 262 | 93% | match | USD | USD | US | 6 | no_ban | PASS |
| Uncle Goose | toys_kids | unclegoose.com | ok | yes | yes | yes | yes | 196 | 268 | 85% | match | USD | USD | US | 6 | ban | PASS |
| White Mountain Puzzles | toys_kids | www.whitemountainpuzzles.com | ok | yes | yes | yes | yes | - | - | - | match | USD | USD | US | 9 | - | fail: blocked mid-recon, empty catalog, needed 429 retries |
| Wonder Workshop | toys_kids | www.makewonder.com | ok | yes | yes | no | no | - | - | - | - | - | - | - | 2 | - | fail: blocked |

## Notes

- **3sixteen**: stopped: retries exhausted: http 429
- **Allplay**: /products.json: http 404, ?
- **amFilm**: stopped: robots.txt unreachable: retries exhausted: network error: ConnectError
- **Analogue**: /products.json: http 404, text/html; charset=utf-8
- **Anker**: /products.json: http 404, text/html; charset=utf-8
- **Autonomous**: /products.json: http 404, text/html; charset=utf-8
- **Balanced Body**: /products.json: http 404, text/html; charset=utf-8
- **Beckett Simonon**: no JSON-LD offer currency on product page
- **Bitsbox**: /products.json: http 404, text/html; charset=utf-8
- **Bob and Brad**: /products.json: http 404, text/html; charset=utf-8
- **Bombshell Sportswear**: stopped: retries exhausted: http 429
- **BoxWave**: stopped: blocked: cloudflare challenge
- **Busy Baby**: stopped: robots.txt unreachable: retries exhausted: network error: ConnectError
- **Caseology**: /products.json: http 404, text/html
- **Chaser**: stopped: blocked: cloudflare challenge
- **Code of Bell**: no JSON-LD offer currency on product page
- **Coterie**: /products.json: http 404, text/html; charset=utf-8
- **Dossier**: /products.json: http 404, text/html
- **Element Case**: /products.json: http 404, text/html
- **Elliptigo**: stopped: blocked: cloudflare challenge
- **Ergobaby**: stopped: blocked: cloudflare challenge
- **Fat Brain Toys**: stopped: blocked: http 403
- **Glyder**: stopped: retries exhausted: http 429; no JSON-LD offer currency on product page
- **Greater Than Games**: /products.json: http 404, text/html;charset=utf-8
- **hand2mind**: stopped: blocked: datadome captcha (robots.txt)
- **Hanky Panky**: stopped: retries exhausted: http 429
- **Hatch**: /products.json: http 404, text/html; charset=utf-8
- **Hello Bello**: stopped: blocked: cloudflare block
- **Hey Dude**: /products.json: http 410, text/html;charset=UTF-8
- **Hydrow**: stopped: robots.txt unreachable: retries exhausted: http 429
- **Ledbury**: stopped: retries exhausted: http 429
- **Marc Pro**: stopped: blocked: cloudflare challenge
- **MeUndies**: stopped: robots.txt unreachable: retries exhausted: http 429
- **Mightly**: stopped: retries exhausted: http 429; no JSON-LD offer currency on product page
- **Munchkin**: /products.json: http 404, text/html
- **Nonda**: no JSON-LD offer currency on product page
- **Original Grain**: stopped: retries exhausted: http 429
- **Outlier**: /products.json: http 404, ?
- **Petite Plume**: stopped: robots.txt unreachable: retries exhausted: http 530
- **Pomegranate**: stopped: retries exhausted: http 429
- **Popov Leather**: no JSON-LD offer currency on product page
- **PopSockets**: /products.json: http 404, text/html;charset=UTF-8
- **PowerDot**: /products.json: http 404, ?
- **Primary**: stopped: retries exhausted: http 429
- **ProClip USA**: /products.json: http 404, text/html
- **Pura Vida**: stopped: retries exhausted: http 429
- **Quoddy**: stopped: retries exhausted: http 429
- **Radio Flyer**: stopped: retries exhausted: http 429
- **Rainbow Sandals**: /products.json: http 404, text/html; charset=utf-8
- **Recoup Fitness**: /products.json: http 404, text/html
- **Renegade Game Studios**: /products.json: http 404, text/html; charset=UTF-8
- **Restoration Games**: /products.json: http 404, text/html; charset=UTF-8
- **Retro-Bit**: /products.json: http 404, text/html; charset=UTF-8
- **Set Active**: no JSON-LD offer currency on product page
- **Snap Circuits (Elenco)**: /products.json: http 307, text/html
- **Sorinex**: /products.json: http 404, text/html; charset=utf-8
- **Spanx**: /products.json: http 404, text/html
- **Springbok Puzzles**: /products.json: http 404, text/html; charset=utf-8
- **Stance**: stopped: retries exhausted: http 429
- **Stonemaier Games**: /products.json: http 404, text/html; charset=UTF-8
- **Tecovas**: /products.json: http 404, text/html
- **The Ollie World**: no JSON-LD offer currency on product page
- **Thinborne**: no JSON-LD offer currency on product page
- **Think Tank Photo**: no JSON-LD offer currency on product page
- **Thunderworks Games**: no JSON-LD offer currency on product page
- **Tipsy Elves**: stopped: retries exhausted: http 429
- **TLF Apparel**: /products.json: http 404, text/html
- **Tumbl Trak**: /products.json: http 404, text/html; charset=UTF-8
- **UGREEN (US)**: stopped: retries exhausted: http 429; product .js: http 404; product page: http 404
- **Ultimate Direction**: /products.json: http 404, text/html; charset=UTF-8
- **UNTUCKit**: stopped: retries exhausted: http 429
- **Vincero**: no JSON-LD offer currency on product page
- **White Mountain Puzzles**: stopped: retries exhausted: http 429
- **Wonder Workshop**: stopped: blocked: cloudflare challenge
- **Woolx**: stopped: retries exhausted: http 429
- **Yes4All**: /products.json: http 404, text/html; charset=UTF-8
- **Ztylus**: /products.json: http 404, ?

## Terms of Service

`/policies/terms-of-service`, at most 2 requests per store, read only where robots.txt allows it: ban 76, no_ban 13, none_found 7.

| store | terms | source | first matching sentence |
|---|---|---|---|
| Able Carry | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the Service is provided, without express written permission by us. |
| Alo Yoga | ban | read | You also may not, without ALO’s written permission, access or collect Materials and Content using automated means or attempt to access Materials and Content that you do not have permission to access. |
| Beckett Simonon | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the service is provided, without express written permission by us. |
| Beyond Yoga | none_found | robots.txt disallows /policies/terms-of-service | - |
| Chrome Industries | ban | read | informational use, provided that you do not republish the Content and |
| Code of Bell | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the service is provided, without express written permission by us. |
| Comrad | none_found | robots.txt disallows /policies/terms-of-service | - |
| Good American | ban | read | You may not republish the Company Content on any Internet, Intranet or Extranet site or incorporate the information in any other database or compilation. |
| Gorjana | ban | read | You may not use the Website for any resale or commercial use, including without limitation, the use of any information, services or Content (as defined below) on the Website, such as product listings, descriptions, or pricing. |
| Grant Stone | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the service is provided, without express written permission by us. |
| Jambys | no_ban | read | - |
| Kinn | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the service is provided, without express written permission by us. |
| Left Field NYC | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the service is provided, without express written permission by us. |
| Minus33 | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the Service is provided, without express written permission by us. |
| MVMT | ban | read | You may access, copy, download and print the material contained on the Site for your personal and non-commercial use, provided you do not modify or delete any copyright, trademark or other proprietary notice that appears on the material you access, copy, download or print. |
| Nicks Boots | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the Service is provided, without express written permission by us. |
| Peter Manning NYC | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the service is provided, without express written permission by us. |
| Pistol Lake | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the service is provided, without express written permission by us. |
| Popov Leather | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the service is provided, without express written permission by us. |
| Rancourt & Co. | ban | read | You may not download (except as invited), or reproduce, modify, publish, distribute, transmit, transfer, sell or modify any portion of this site without express written authorization from Rancourt & Co. |
| Saddleback Leather | ban | read | You must not reproduce, distribute, modify, create derivative works of, publicly display, publicly perform, republish, download, store, or transmit any of the material on the Services without our prior written consent. |
| Set Active | ban | read | · Rent, lease, loan, sell, or resell our Services or related data without our consent; |
| Shinesty | ban | read | Further, the use of manual or automated software, devices, or other processes to “crawl”, “scrape”, or “spider” any page of the Website is strictly prohibited. |
| Show Me Your Mumu | ban | read | You must not reproduce, distribute, modify, create derivative works of, publicly display, publicly perform, republish, download, store, or transmit any of the material on our Website, except as follows: |
| Taft | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the service is provided, without express written permission by us. |
| Tanner Goods | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the service is provided, without express written permission by us. |
| Thinx | none_found | robots.txt disallows /policies/terms-of-service | - |
| Thursday Boot Company | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the service is provided, without express written permission by us. |
| Vincero | ban | read | Except as permitted above, you may not reproduce, distribute, display, sell, lease, transmit, create derivative works from, translate, modify, reverse-engineer, disassemble, decompile or otherwise exploit this Site or any portion of it unless expressly permitted by us in writing. |
| Xero Shoes | ban | read | * Republish material from our website without prior written consent. |
| CAP Barbell | ban | read | You must not reproduce, distribute, modify, create derivative works of, publicly display, publicly perform, republish, download, store, or transmit any of the material on the Services without our prior written consent. |
| Compex | no_ban | read | - |
| Elevate Jump Ropes | none_found | robots.txt disallows /policies/terms-of-service | - |
| Ergatta | ban | read | You must not reproduce, distribute, modify, create derivative works of, publicly display, publicly perform, republish, download, store or transmit any of the material on our Services. |
| Gamma Sports | no_ban | read | - |
| Hylete | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the Service is provided, without express written permission by us. |
| Inspire Fitness | ban | read | You agree that if you download any content from the Website/App you will not reproduce, distribute … in person, publish, republish, print, upload to any third party, post on any social media site or Facebook Community, or distribute or modify or otherwise deal with any content in the … |
| Iron Bull Strength | ban | read | You may not reproduce, duplicate, copy, sell, resell, or exploit any portion of the Service, access to the Service, or contact available through the website without our prior written permission. |
| Ironmaster | ban | read | Using any manual process or means to monitor or copy any of the material on this Website or for any other unauthorized purpose; |
| Lebert Fitness | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the service is provided, without express written permission by us. |
| Metolius | ban | read | Further, except as specifically permitted in these Terms, you agree that you will not directly or … rt thereof in any form or manner or by any means; (iv) harvest or scrape any content or data from the Services; (v) remove or alter any copyright or other proprietary rights' notice or restrictive … |
| Oko Living | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the service is provided, without express written permission by us. |
| Onnit | ban | read | You may not reproduce, duplicate, distribute, publish, modify, copy, decompile or reverse engineer, or transmit material, from this web site. |
| Opove | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the service is provided, without express written permission by us. |
| Organic Climbing | ban | read | You must not reproduce, distribute, modify, create derivative works of, publicly display, publicly perform, republish, download, store, or transmit any of the material on the Services without our prior written consent. |
| Prime Fitness | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the Service is provided, without express written permission by us. |
| Saris | no_ban | read | - |
| SHEFIT | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the service is provided, without express written permission by us. |
| Stroops | ban | read | Except as expressly provided in these Terms of Use, no part of the Site and no Content or Marks may … transmitted, distributed, sold, licensed, or otherwise exploited for any commercial purpose whatsoever, without our express prior written permission. |
| Trango | ban | read | Except as expressly provided in these Terms, no part of the Websites and no Content may be copied, … rver, website or other medium for publication or distribution or for any commercial enterprise, without Company’s express prior written consent. |
| Valor Fitness | ban | read | Subject to the terms and conditions of this Agreement, we hereby grant you a limited, revocable, … ly for the purpose of shopping for items sold on the Site and not for any commercial use or use on behalf of any third party, except as explicitly permitted by us in advance. |
| XMark Fitness | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the Service is provided, without express written permission by us. |
| Arkon | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the Service is provided, without express written permission by us. |
| Bluelounge | none_found | http 404 | - |
| Brydge | ban | read | You must not reproduce, retransmit, assign, sub-license, prepare derivative works, distribute, … disseminate, sell, publish, broadcast or circulate any Content from the Site to a third party or use or display the Content on any other website without first obtaining the written consent of Uinta … |
| Catalyst | ban | read | You must not reproduce, distribute, modify, create derivative works of, publicly display, publicly perform, republish, download, store, or transmit any of the material on the Services without our prior written consent. |
| ESR | ban | read | To conduct automated data collection (scraping, mining, harvesting) without written consent; |
| Finalmouse | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the Service is provided, without express written permission by us. |
| HyperDrive | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the service is provided, without express written permission by us. |
| Incipio | no_ban | read | - |
| ModRetro | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the Service is provided, without express written permission by us. |
| Moment | ban | read | The foregoing license grant is not a sale of all or any portion of the Service, including but not … mited to any Individual Features and Subscriber Features (and any copy thereof). |
| Nekteck | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the service is provided, without express written permission by us. |
| Nonda | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the service is provided, without express written permission by us. |
| Rocketbook | ban | read | You agree to not copy, modify, transmit, create any derivative works from, make use of, or … reproduce in any way any part of the Services, or any copyrighted material, content, trademarks, trade names, service marks, or other intellectual property or proprietary information accessible through … |
| Scosche | none_found | http 404 | - |
| Spider Holster | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the service is provided, without express written permission by us. |
| Thinborne | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the Service is provided, without express written permission by us. |
| Think Tank Photo | ban | read | You must not reproduce, distribute, modify, create derivative works of, publicly display, publicly perform, republish, download, store, or transmit any of the material on the Services without our prior written consent. |
| Tom Bihn | no_ban | read | - |
| Angel Dear | no_ban | read | - |
| Avenlur | ban | read | Except as expressly provided in these Terms of Use, no part of the Site and no Content may be … , transmitted, distributed, sold, licensed, or otherwise exploited for any commercial purpose whatsoever, without our express prior written permission. |
| Baby Brezza | no_ban | read | - |
| Babyletto | ban | read | You agree not to: (a) use the Service in a manner that is prohibited by any law or regulation, or … ted applications, searches, requests, or queries to (or to strip, scrape, or mine data from) the Service; or (k) use the Service for any purpose other than as expressly licensed herein. |
| Cuddle + Kind | ban | read | Any use of this Site or its Content other than for personal and non-commercial purposes is prohibited. |
| Floodgate Games | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the Service is provided, without express written permission by us. |
| Four Point Puzzles | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the service is provided, without express written permission by us. |
| GroVia | no_ban | read | - |
| HABA USA | no_ban | read | - |
| Joovy | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the Service is provided, without express written permission by us. |
| Keymaster Games | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the service is provided, without express written permission by us. |
| Kudos | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the service is provided, without express written permission by us. |
| Liberty Puzzles | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the Service is provided, without express written permission by us. |
| Magnolia Baby | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the Service is provided, without express written permission by us. |
| Maple Landmark | none_found | http 404 | - |
| Nanit | no_ban | read | - |
| New York Puzzle Company | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the service is provided, without express written permission by us. |
| Osmo | ban | read | You may not reproduce, distribute, or use any content without prior written permission. |
| Owlet | no_ban | read | - |
| Pandasaurus Games | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the service is provided, without express written permission by us. |
| Thames & Kosmos | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the service is provided, without express written permission by us. |
| The Ollie World | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the service is provided, without express written permission by us. |
| Thunderworks Games | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the Service is provided, without express written permission by us. |
| Tiny Land | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the service is provided, without express wrote permission by us. |
| Ubbi | no_ban | read | - |
| Uncle Goose | ban | read | You agree not to reproduce, duplicate, copy, sell, resell or exploit any portion of the Service, use of the Service, or access to the Service or any contact on the website through which the service is provided, without express written permission by us. |
