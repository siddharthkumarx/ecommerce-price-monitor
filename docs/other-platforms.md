# Stores on other platforms (for later)

The monitor reads Shopify's public `/products.json` only (D-031: no other platform is
collected now). This page lists stores that would fit the monitor but that it cannot
read today, so a later platform reader has a starting list. Nothing here is monitored.

## Found by recon

Recon asked these stores for `/products.json` and got no Shopify product list. Some run
another platform; some are Shopify shops with a custom (headless) storefront that does
not serve the endpoint. Which one is not checked: recon stops at the first answer.

| Category | Store | Domain | Recon | Answer to `/products.json` |
|---|---|---|---|---|
| Apparel | BAGGU | baggu.com | recon-005 | http 404, text/html |
| Apparel | Birddogs | birddogs.com | recon-003 | http 200, text/html |
| Apparel | Chubbies | chubbiesshorts.com | recon-002 | http 404, text/html |
| Apparel | Cuts Clothing | cutsclothing.com | recon-002 | http 404, text/html |
| Apparel | Public Rec | publicrec.com | recon-002 | http 200, application/json |
| Apparel | SuitShop | suitshop.com | recon-005 | http 404, text/html |
| Apparel | Tracksmith | tracksmith.com | recon-003 | http 404, text/html |
| Apparel | Vuori | vuoriclothing.com | recon-002 | http 404, text/html |
| Audio | Audioengine | audioengine.com | recon-002 | http 404, text/html |
| Audio | EarFun | myearfun.com | recon-002 | http 404, application/json |
| Audio | Nothing (US) | us.nothing.tech | recon-002 | http 404, text/html |
| Audio | Rockford Fosgate | rockfordfosgate.com | recon-005 | http 404, text/html |
| Audio | Turtle Beach | turtlebeach.com | recon-005 | http 404, text/html |
| Beauty | Arctic Fox | arcticfoxhaircolor.com | recon-005 | http 404, text/html |
| Beauty | Briogeo | briogeohair.com | recon-002 | http 404, text/html |
| Beauty | Dr. Dennis Gross Skincare | drdennisgross.com | recon-005 | http 410, text/html |
| Beauty | Dr. Squatch | drsquatch.com | recon-002 | http 404, text/html |
| Beauty | Lume Deodorant | lumedeodorant.com | recon-005 | http 200, text/html |
| Beauty | Topicals | mytopicals.com | recon-004 | http 404, text/html |
| Coffee & tea | Canyon Coffee | canyoncoffee.co | recon-005 | http 404, text/html |
| Coffee & tea | Chamberlain Coffee | chamberlaincoffee.com | recon-005 | http 200, text/html |
| Home & kitchen | Blueland | blueland.com | recon-002 | http 404, text/html |
| Home & kitchen | Boll & Branch | bollandbranch.com | recon-002 | http 404, text/html |
| Home & kitchen | Burrow | burrow.com | recon-002 | http 404, text/plain |
| Home & kitchen | Caraway | carawayhome.com | recon-002 | http 404, text/html |
| Home & kitchen | Equal Parts | equalparts.com | recon-004 | http 404, text/html |
| Home & kitchen | Hedley & Bennett | hedleyandbennett.com | recon-004 | http 200, text/html |
| Home & kitchen | Jungalow | jungalow.com | recon-005 | http 404, text/html |
| Home & kitchen | Revival Rugs | revivalrugs.com | recon-005 | http 404, text/html |
| Home & kitchen | W&P | wpdesign.com | recon-004 | http 404, text/html |
| Outdoor | Enlightened Equipment | enlightenedequipment.com | recon-004 | http 404, text/html |
| Outdoor | ENO | eaglesnestoutfitters.com | recon-004 | http 200, text/html |
| Outdoor | iROCKER | irockersup.com | recon-005 | http 404, text/html |
| Outdoor | Mystery Ranch | mysteryranch.com | recon-004 | http 404, text/html |
| Outdoor | Oru Kayak | orukayak.com | recon-002 | http 404, text/html |
| Outdoor | Peak Design | peakdesign.com | recon-002 | http 404, text/html |
| Outdoor | Poler | polerstuff.com | recon-004 | http 404, text/html |
| Outdoor | Sawyer | sawyer.com | recon-004 | http 404, text/html |
| Outdoor | ULA Equipment | ula-equipment.com | recon-004 | http 404, text/html |
| Pet | Lucy & Co. | lucyandco.com | recon-005 | http 404, text/html |
| Pet | Nulo | nulo.com | recon-005 | http 404, text/html |
| Pet | PetLab Co. | thepetlabco.com | recon-005 | http 404, text/html |
| Pet | Small Pet Select | smallpetselect.com | recon-005 | http 404, text/html |
| Tech accessories | Nomad | nomadgoods.com | recon-005 | http 404, text/html |
| Tech accessories | Totallee | totallee.com | recon-005 | http 404, text/html |
| Toys & kids | Happiest Baby | happiestbaby.com | recon-005 | http 200, text/html |
| Toys & kids | Lovevery | lovevery.com | recon-005 | http 404, text/html |

## Leads from desk research, not checked

Mid-size US brands that fit the categories and are believed to run WooCommerce or
BigCommerce. No request has been sent to them; confirm the platform, robots.txt and
Terms of Service before any reader is built.

| Category | Store | Domain | Believed platform |
|---|---|---|---|
| Outdoor | CamelBak | camelbak.com | BigCommerce |
| Tech accessories | Kinesis | kinesis-ergo.com | WooCommerce |
| Tech accessories | CalDigit | caldigit.com | WooCommerce |
| Tech accessories | Plugable | plugable.com | WooCommerce |
| Audio | iFi audio | ifi-audio.com | WooCommerce |
| Audio | Etymotic | etymotic.com | BigCommerce |

## Before a reader for another platform

- WooCommerce exposes `/wp-json/wc/store/v1/products` on many shops; BigCommerce has
  no public catalog endpoint, so its storefront pages would have to be read.
- The same rules apply: robots.txt, the per-shop and run-wide pace, the Terms field and
  the D-004 drop rules. A new reader is an owner decision, recorded in `decisions.md`.
