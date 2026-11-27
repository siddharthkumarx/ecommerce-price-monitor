#!/bin/sh
# Render every visual and media file from the committed data (offline, no shop requests).
#
#   scripts/make_media.sh            # uses data/, writes assets/ and media/
#
# Needs: uv, Node with Playwright (Chromium), ffmpeg with libx264.
set -eu
root="$(cd "$(dirname "$0")/.." && pwd)"
cd "$root"
work="$(mktemp -d)"
trap 'rm -rf "$work"' EXIT

uv run python -m pricemon.visuals --data data --stores config/stores.yml --out assets
uv run python -m pricemon.readme
uv run python -m pricemon.site --data data --stores config/stores.yml --out "$work/site"
node scripts/render_media.cjs dashboard "$work/site" assets/dashboard.png
stores="$(uv run python -c "
from pathlib import Path
from pricemon.stores import load_stores
print(len(load_stores(Path('config/stores.yml'))))
")"
drops="$(uv run python -c "
import json
rows = json.load(open('data/public/feed.json'))['daily'][-8:]
print(','.join(f\"{r['date']}:{r['price_down']}\" for r in rows))
")"
node scripts/render_media.cjs social src/pricemon/site_assets/fonts "$stores" "$drops" assets/social-preview.png
uv run python -c "
from pathlib import Path
from pricemon.report import collect
from pricemon.visuals import hero_square
Path('$work/hero-square.svg').write_text(hero_square(collect(Path('data'), Path('config/stores.yml'))).render())
"
node scripts/render_media.cjs frames "$work/hero-square.svg" "$work/frames"
mkdir -p media
ffmpeg -loglevel error -y -framerate 30 -i "$work/frames/f%04d.png" \
  -c:v libx264 -pix_fmt yuv420p -crf 20 -preset slow -movflags +faststart media/linkedin-hero.mp4
ls -la assets/*.svg assets/*.png media/linkedin-hero.mp4
