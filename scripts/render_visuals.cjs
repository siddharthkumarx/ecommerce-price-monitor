// Render README visuals at phone and desktop widths, at chosen animation times.
//
//   node scripts/render_visuals.cjs <out-dir> assets/hero.svg [more.svg ...]
//
// Each SVG is inlined in a page so its CSS animations can be paused and seeked
// (document.getAnimations). Frames: beats at 1.2 s, 4.5 s and 8.6 s of the 9 s loop,
// plus the reduced-motion still. Widths: 390 px (phone) and 1280 px (desktop).
const fs = require("fs");
const path = require("path");
const { chromium } = require("playwright");

(async () => {
  const [outDir, ...files] = process.argv.slice(2);
  fs.mkdirSync(outDir, { recursive: true });
  const browser = await chromium.launch();
  for (const file of files) {
    const svg = fs.readFileSync(file, "utf8");
    const name = path.basename(file, ".svg");
    for (const width of [390, 1280]) {
      for (const motion of ["no-preference", "reduce"]) {
        const ctx = await browser.newContext({ viewport: { width, height: 800 }, deviceScaleFactor: 1, reducedMotion: motion });
        const page = await ctx.newPage();
        await page.setContent(`<!doctype html><body style="margin:0;padding:12px;background:#0d1117">
          <div style="max-width:${width - 24}px">${svg.replace(/width="\d+" height="\d+"/, 'style="width:100%;height:auto;display:block"')}</div></body>`);
        await page.evaluate(() => document.fonts.ready);
        const times = motion === "reduce" ? [0] : [1.2, 4.5, 8.6];
        for (const t of times) {
          await page.evaluate((ms) => document.getAnimations().forEach((a) => { a.pause(); a.currentTime = ms; }), t * 1000);
          const el = await page.$("svg");
          await el.screenshot({ path: path.join(outDir, `${name}-${width}-${motion === "reduce" ? "still" : t + "s"}.png`) });
        }
        await ctx.close();
      }
    }
  }
  await browser.close();
})();
