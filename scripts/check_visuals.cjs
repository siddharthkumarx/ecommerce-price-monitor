// Check that every README visual shows its final frame when motion is reduced.
//
//   node scripts/check_visuals.cjs <dir-with-svgs>
//
// For each of hero, pipeline, maintenance-loop:
//   final    the animated SVG inline, every animation paused at the end of the loop
//   reduced  the animated SVG inline with prefers-reduced-motion: reduce
//   still    <name>-still.svg loaded as <img>, the way the README's <picture> shows it
// "reduced" and "still" must match "final": compared at quarter size, so text
// anti-aliasing (which differs between composited animated layers and static
// text) averages out, fewer than 1 % of pixels may differ. As a control, the
// first frame must differ clearly from the final frame, so the comparison can
// catch a wrong frame. "reduced" must run no animation, and the hero's result
// number must be visible.
// Prints a JSON report; exits 1 on any failure.
const fs = require("fs");
const path = require("path");
const { chromium } = require("playwright");

const NAMES = ["hero", "pipeline", "maintenance-loop"];
const LOOP_MS = 9000;

async function shoot(browser, html, motion, pause, size) {
  const ctx = await browser.newContext({ viewport: size, deviceScaleFactor: 1, reducedMotion: motion });
  const page = await ctx.newPage();
  await page.setContent(`<!doctype html><body style="margin:0;background:#000">${html}</body>`);
  // Wait until every embedded font is really loaded and every image decoded:
  // document.fonts.ready alone resolves before an SVG's fonts start loading.
  await page.evaluate(async () => {
    await Promise.all([...document.fonts].map((f) => f.load().catch(() => null)));
    await document.fonts.ready;
    await Promise.all([...document.images].map((i) => i.decode().catch(() => null)));
  });
  await page.waitForTimeout(500);
  if (pause !== null) {
    await page.evaluate((ms) => document.getAnimations().forEach((a) => { a.pause(); a.currentTime = ms; }), pause);
  }
  const info = await page.evaluate(() => {
    const op = (sel) => { const el = document.querySelector(sel); return el ? getComputedStyle(el).opacity : null; };
    return { running: document.getAnimations().filter((a) => a.playState === "running").length, b1: op(".b1"), b3: op(".b3") };
  });
  const png = await page.screenshot({ clip: { x: 0, y: 0, ...size } });
  await ctx.close();
  return { png, info };
}

async function diff(browser, a, b) {
  const page = await browser.newPage();
  const ratio = await page.evaluate(async ([x, y]) => {
    const load = (src) => new Promise((ok) => { const i = new Image(); i.onload = () => ok(i); i.src = src; });
    const [ia, ib] = await Promise.all([load(x), load(y)]);
    const c = document.createElement("canvas");
    c.width = Math.round(ia.width / 4); c.height = Math.round(ia.height / 4);
    const g = c.getContext("2d");
    g.imageSmoothingQuality = "high";
    g.drawImage(ia, 0, 0, c.width, c.height); const da = g.getImageData(0, 0, c.width, c.height).data;
    g.clearRect(0, 0, c.width, c.height);
    g.drawImage(ib, 0, 0, c.width, c.height); const db = g.getImageData(0, 0, c.width, c.height).data;
    let bad = 0;
    for (let k = 0; k < da.length; k += 4) {
      if (Math.abs(da[k] - db[k]) > 32 || Math.abs(da[k + 1] - db[k + 1]) > 32 || Math.abs(da[k + 2] - db[k + 2]) > 32) bad++;
    }
    return bad / (da.length / 4);
  }, ["data:image/png;base64," + a.toString("base64"), "data:image/png;base64," + b.toString("base64")]);
  await page.close();
  return ratio;
}

(async () => {
  const dir = process.argv[2];
  const browser = await chromium.launch();
  const report = [];
  let ok = true;
  for (const name of NAMES) {
    const animated = fs.readFileSync(path.join(dir, `${name}.svg`), "utf8");
    const still = fs.readFileSync(path.join(dir, `${name}-still.svg`), "utf8");
    const [, w, h] = animated.match(/viewBox="0 0 (\d+) (\d+)"/);
    const size = { width: Number(w), height: Number(h) };
    const final = await shoot(browser, animated, "no-preference", LOOP_MS - 100, size);
    const first = await shoot(browser, animated, "no-preference", 1200, size);
    const reduced = await shoot(browser, animated, "reduce", null, size);
    const img = `<img src="data:image/svg+xml;base64,${Buffer.from(still).toString("base64")}" width="${w}" height="${h}" style="display:block">`;
    const stillShot = await shoot(browser, img, "no-preference", null, size);
    const keep = process.env.CHECK_VISUALS_OUT;
    if (keep) {
      fs.mkdirSync(keep, { recursive: true });
      fs.writeFileSync(path.join(keep, `${name}-final.png`), final.png);
      fs.writeFileSync(path.join(keep, `${name}-reduced.png`), reduced.png);
      fs.writeFileSync(path.join(keep, `${name}-still.png`), stillShot.png);
    }
    const r = {
      name,
      reduced_vs_final: await diff(browser, reduced.png, final.png),
      still_img_vs_final: await diff(browser, stillShot.png, final.png),
      first_vs_final: await diff(browser, first.png, final.png),
      reduced_running_animations: reduced.info.running,
      hero_result_opacity: reduced.info.b3,
      hero_first_beat_opacity: reduced.info.b1,
    };
    const pass =
      r.first_vs_final > 0.03 &&
      r.reduced_vs_final < 0.01 &&
      r.still_img_vs_final < 0.01 &&
      r.reduced_running_animations === 0 &&
      (name !== "hero" || (r.hero_result_opacity === "1" && r.hero_first_beat_opacity === "0"));
    r.pass = pass;
    ok = ok && pass;
    report.push(r);
  }
  await browser.close();
  console.log(JSON.stringify(report, null, 2));
  process.exit(ok ? 0 : 1);
})();
