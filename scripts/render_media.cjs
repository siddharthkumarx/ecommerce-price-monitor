// Media for the README and for sharing, rendered with Playwright (Chromium).
//
//   node scripts/render_media.cjs dashboard <site-dir> <out.png>    real dashboard, 2x
//   node scripts/render_media.cjs social <fonts-dir> <stores> <out.png>   1280x640 preview
//   node scripts/render_media.cjs frames <square.svg> <frames-dir>  30 fps frames of a 9 s loop
//
// Frames are encoded by ffmpeg (see scripts/make_media.sh).
const fs = require("fs");
const path = require("path");
const { chromium } = require("playwright");

const [cmd, ...args] = process.argv.slice(2);

async function dashboard(siteDir, out) {
  const browser = await chromium.launch();
  const page = await (await browser.newContext({ viewport: { width: 1280, height: 1000 }, deviceScaleFactor: 2 })).newPage();
  await page.goto("file://" + path.resolve(siteDir, "index.html"));
  await page.evaluate(() => document.fonts.ready);
  await page.screenshot({ path: out, clip: { x: 0, y: 0, width: 1280, height: 1000 } });
  await browser.close();
}

async function social(fontsDir, stores, out) {
  const font = (f) => "data:font/woff2;base64," + fs.readFileSync(path.join(fontsDir, f)).toString("base64");
  const html = `<!doctype html><html><head><style>
    @font-face{font-family:IS;font-weight:400;src:url(${font("instrument-sans-latin-400-normal.woff2")})}
    @font-face{font-family:IS;font-weight:600;src:url(${font("instrument-sans-latin-600-normal.woff2")})}
    @font-face{font-family:PM;font-weight:500;src:url(${font("ibm-plex-mono-latin-500-normal.woff2")})}
    body{margin:0;width:1280px;height:640px;background:#0B1416;color:#EAF2F0;font-family:IS}
    .wrap{padding:84px 96px;height:100%;box-sizing:border-box;display:flex;flex-direction:column;justify-content:center;gap:28px}
    .kicker{font:500 30px PM;color:#2FBFAE}
    h1{font-size:84px;line-height:1.02;margin:0;font-weight:600;letter-spacing:-.01em}
    p{font-size:36px;color:#C9D8D5;margin:0;max-width:980px;line-height:1.3}
    .foot{margin-top:24px;font-size:28px;color:#7E9996;display:flex;gap:28px}
    .bar{position:absolute;left:96px;top:64px;width:120px;height:8px;border-radius:4px;background:#2FBFAE}
    .amber{color:#E9A93C}
  </style></head><body><div class="bar"></div><div class="wrap">
    <div class="kicker">${stores} US online stores · every day</div>
    <h1>Shopify price monitor</h1>
    <p>Every price, <span class="amber">sale</span> and stock change, checked against a second source and delivered as a clean spreadsheet.</p>
    <div class="foot"><span>Siddharth Kumar</span><span>·</span><span>siddharthkumar.com</span></div>
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
  await page.setContent(`<!doctype html><body style="margin:0;background:#0B1416">${svg}</body>`);
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
