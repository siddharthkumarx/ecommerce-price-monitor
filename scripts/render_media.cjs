// Media for the README and for sharing, rendered with Playwright (Chromium).
//
//   node scripts/render_media.cjs dashboard <site-dir> <out.png>    real dashboard, 2x
//   node scripts/render_media.cjs social <fonts-dir> <stores> <date:drops,...> <out.png>   1280x640 preview
//   node scripts/render_media.cjs frames <square.svg> <frames-dir>  30 fps frames of a 9 s loop
//
// Frames are encoded by ffmpeg (see scripts/make_media.sh).
//
// Canvas rule: every image's outermost background is #F3F8F7; cards inside are
// #FFFFFF with border #E2EAE8, radius 14px. The dashboard shot is framed: the
// white page as a card on 40 px of canvas. scripts/check_canvas.cjs checks it.
const fs = require("fs");
const path = require("path");
const { chromium } = require("playwright");

const [cmd, ...args] = process.argv.slice(2);

// Lays a page screenshot (CSS size w x h, taken at scale dpr) on the canvas as a card.
async function frame(browser, png, w, h, dpr) {
  const ctx = await browser.newContext({ viewport: { width: w + 82, height: h + 82 }, deviceScaleFactor: dpr });
  const page = await ctx.newPage();
  await page.setContent(`<!doctype html><body style="margin:0;padding:40px;background:#F3F8F7">
    <div style="border:1px solid #E2EAE8;border-radius:14px;overflow:hidden;background:#FFFFFF;width:${w}px;height:${h}px">
    <img style="display:block;width:${w}px;height:${h}px" src="data:image/png;base64,${png.toString("base64")}"></div></body>`);
  await page.waitForFunction(() => document.images[0].complete);
  const framed = await page.screenshot({ fullPage: true });
  await ctx.close();
  return framed;
}

async function dashboard(siteDir, out) {
  const browser = await chromium.launch();
  const page = await (await browser.newContext({ viewport: { width: 1280, height: 1000 }, deviceScaleFactor: 2, reducedMotion: "reduce" })).newPage();
  await page.goto("file://" + path.resolve(siteDir, "index.html"));
  await page.evaluate(() => document.fonts.ready);
  const png = await page.screenshot({ clip: { x: 0, y: 0, width: 1280, height: 1000 } });
  fs.writeFileSync(out, await frame(browser, png, 1280, 1000, 2));
  await browser.close();
}

async function social(fontsDir, stores, drops, out) {
  // drops: "YYYY-MM-DD:n,..." price drops per day from data/public/feed.json (real runs).
  const days = drops.split(",").filter(Boolean).map((d) => { const [date, n] = d.split(":"); return { date, n: Number(n) }; });
  const top = Math.max(1, ...days.map((d) => d.n));
  const label = (iso) => new Date(iso + "T00:00:00Z").toLocaleDateString("en-GB", { day: "numeric", month: "short", timeZone: "UTC" });
  const bars = days.map((d) => `<div class="b"><span class="v">${d.n.toLocaleString("en-US")}</span><i style="height:${Math.max(2, (230 * d.n) / top)}px"></i></div>`).join("");
  const caption = days.length ? `Price drops per day, ${label(days[0].date)} to ${label(days[days.length - 1].date)}` : "";
  const font = (f) => "data:font/woff2;base64," + fs.readFileSync(path.join(fontsDir, f)).toString("base64");
  const html = `<!doctype html><html><head><style>
    @font-face{font-family:PJ;font-weight:400;src:url(${font("plus-jakarta-sans-latin-400-normal.woff2")})}
    @font-face{font-family:PJ;font-weight:600;src:url(${font("plus-jakarta-sans-latin-600-normal.woff2")})}
    @font-face{font-family:PJ;font-weight:700;src:url(${font("plus-jakarta-sans-latin-700-normal.woff2")})}
    body{margin:0;width:1280px;height:640px;background:#F3F8F7;color:#0B1416;font-family:PJ;font-variant-numeric:tabular-nums}
    .wrap{position:absolute;left:40px;top:40px;width:840px;height:560px;padding:0 56px;background:#FFFFFF;border:1px solid #E2EAE8;border-radius:14px;
      box-sizing:border-box;display:flex;flex-direction:column;justify-content:center;gap:24px}
    .kicker{display:inline-flex;align-self:flex-start;align-items:center;gap:12px;font-weight:600;font-size:28px;color:#0B1416;
      background:#E3F3F0;border-radius:999px;padding:10px 22px}
    .dot{width:14px;height:14px;border-radius:50%;background:#0E8A7D}
    h1{font-size:80px;line-height:1.02;margin:0;font-weight:700;letter-spacing:-.02em}
    p{font-size:33px;color:#3D4B49;margin:0;line-height:1.3}
    .foot{margin-top:14px;font-size:27px;color:#3D4B49;display:flex;gap:20px;font-weight:600}
    .foot .acc{color:#0B7468}
    .bars{position:absolute;right:40px;top:170px;width:290px;display:flex;align-items:flex-end;justify-content:space-between;height:270px;border-bottom:2px solid #0B1416}
    .b{display:flex;flex-direction:column;align-items:center;gap:6px;flex:1}
    .b i{display:block;width:70%;border-radius:4px 4px 0 0;background:#0E8A7D}
    .v{font-size:15px;font-weight:700;color:#0B1416}
    .cap{position:absolute;right:40px;top:458px;width:290px;font-size:20px;line-height:1.3;color:#3D4B49;font-weight:600}
  </style></head><body>
  <div class="bars">${bars}</div><div class="cap">${caption}</div>
  <div class="wrap">
    <div class="kicker"><span class="dot"></span>${stores} US online stores · every day</div>
    <h1>Shopify price monitor</h1>
    <p>Every price, sale and stock change, checked against a second source and delivered as a clean spreadsheet.</p>
    <div class="foot"><span>Siddharth Kumar</span><span>·</span><span>SteadyData</span><span>·</span><span class="acc">steadydata.co</span></div>
  </div></body></html>`;
  const browser = await chromium.launch();
  const page = await (await browser.newContext({ viewport: { width: 1280, height: 640 }, deviceScaleFactor: 1 })).newPage();
  await page.setContent(html);
  await page.evaluate(() => document.fonts.ready);
  await page.screenshot({ path: out });
  await browser.close();
}

async function frames(svgFile, dir) {
  fs.mkdirSync(dir, { recursive: true });
  const svg = fs.readFileSync(svgFile, "utf8");
  const browser = await chromium.launch();
  const page = await (await browser.newContext({ viewport: { width: 1080, height: 1080 }, deviceScaleFactor: 1 })).newPage();
  await page.setContent(`<!doctype html><body style="margin:0;background:#F3F8F7">${svg}</body>`);
  await page.evaluate(() => document.fonts.ready);
  const fps = 30, loop = 9, hold = 1;
  let n = 0;
  for (let i = 0; i < (loop + hold) * fps; i++) {
    const t = Math.min(i / fps, loop - 0.001) * 1000;
    await page.evaluate((ms) => document.getAnimations().forEach((a) => { a.pause(); a.currentTime = ms; }), t);
    await page.screenshot({ path: path.join(dir, `f${String(n++).padStart(4, "0")}.png`), clip: { x: 0, y: 0, width: 1080, height: 1080 } });
  }
  await browser.close();
  console.log(`${n} frames`);
}

(async () => {
  if (cmd === "dashboard") await dashboard(...args);
  else if (cmd === "social") await social(...args);
  else if (cmd === "frames") await frames(...args);
  else { console.error("usage: dashboard|social|frames"); process.exit(2); }
})();
