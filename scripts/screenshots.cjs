// Screenshot the built dashboard at 360, 390, 768, 1280 and 1440 px and run layout checks.
//
//   uv run python -m pricemon.site --data <data dir> --out site
//   node scripts/screenshots.cjs site
//
// Needs Playwright for Node with Chromium (pre-installed in the cloud sandbox).
// Checks per width: no horizontal page scroll, no request leaves file://, every
// visible text node meets 4.5:1 contrast on its effective background, both font
// families load, and reduced motion is honoured. Screenshots: site/screenshots/
// (not committed), framed by the canvas rule: the white page as a card (radius
// 14px, border #E2EAE8) on 40 px of #F3F8F7. Pass --raw for the bare page.
const path = require("path");
const fs = require("fs");
const { chromium } = require("playwright");

const WIDTHS = [360, 390, 768, 1280, 1440];
const RAW = process.argv.includes("--raw");

async function frame(browser, png, w, h) {
  const ctx = await browser.newContext({ viewport: { width: w + 82, height: 200 }, deviceScaleFactor: 2 });
  const page = await ctx.newPage();
  await page.setContent(`<!doctype html><body style="margin:0;padding:40px;background:#F3F8F7;width:${w + 2}px">
    <div style="border:1px solid #E2EAE8;border-radius:14px;overflow:hidden;background:#FFFFFF;width:${w}px;height:${h}px">
    <img style="display:block;width:${w}px;height:${h}px" src="data:image/png;base64,${png.toString("base64")}"></div></body>`);
  await page.waitForFunction(() => document.images[0].complete);
  const framed = await page.screenshot({ fullPage: true });
  await ctx.close();
  return framed;
}

function contrastProblems() {
  const lum = (r, g, b) => {
    const f = (c) => { c /= 255; return c <= 0.03928 ? c / 12.92 : ((c + 0.055) / 1.055) ** 2.4; };
    return 0.2126 * f(r) + 0.7152 * f(g) + 0.0722 * f(b);
  };
  const rgb = (s) => (s.match(/[\d.]+/g) || []).map(Number);
  const bgOf = (el) => {
    for (let e = el; e; e = e.parentElement) {
      const c = rgb(getComputedStyle(e).backgroundColor);
      if (c.length >= 3 && (c.length < 4 || c[3] > 0)) return c;
    }
    return [255, 255, 255];
  };
  const bad = [];
  for (const el of document.querySelectorAll("body *")) {
    const hasText = [...el.childNodes].some((n) => n.nodeType === 3 && n.textContent.trim());
    if (!hasText || el.closest(".sr-only")) continue;
    const st = getComputedStyle(el);
    if (st.visibility === "hidden" || st.display === "none") continue;
    const fg = rgb(st.color), bg = bgOf(el);
    const a = lum(...fg.slice(0, 3)), b = lum(...bg.slice(0, 3));
    const ratio = (Math.max(a, b) + 0.05) / (Math.min(a, b) + 0.05);
    if (ratio < 4.5) bad.push({ tag: el.tagName, text: el.textContent.trim().slice(0, 40), ratio: +ratio.toFixed(2) });
  }
  return bad;
}

(async () => {
  const site = path.resolve(process.argv.slice(2).find((a) => a !== "--raw") || "site");
  const url = "file://" + path.join(site, "index.html");
  const out = path.join(site, "screenshots");
  fs.mkdirSync(out, { recursive: true });
  const problems = [];
  const browser = await chromium.launch();
  for (const width of WIDTHS) {
    const ctx = await browser.newContext({ viewport: { width, height: 900 }, deviceScaleFactor: 2, reducedMotion: "reduce" });
    const page = await ctx.newPage();
    const external = [];
    page.on("request", (r) => { if (!r.url().startsWith("file:")) external.push(r.url()); });
    await page.goto(url);
    await page.waitForLoadState("networkidle");
    await page.evaluate(() => document.fonts.ready);
    const scrollW = await page.evaluate(() => document.documentElement.scrollWidth);
    if (scrollW > width) problems.push(`${width}px: horizontal page scroll (${scrollW}px)`);
    if (external.length) problems.push(`${width}px: external requests ${external.join(", ")}`);
    const low = await page.evaluate(contrastProblems);
    if (low.length) problems.push(`${width}px: low contrast ${JSON.stringify(low.slice(0, 5))}`);
    const fonts = await page.evaluate(() => [...document.fonts].filter((f) => f.status === "loaded").map((f) => `${f.family} ${f.weight}`));
    const families = new Set(fonts.map((f) => f.replace(/ \d+$/, "").replace(/"/g, "")));
    for (const fam of ["Plus Jakarta Sans", "IBM Plex Mono"]) if (!families.has(fam)) problems.push(`${width}px: font ${fam} not loaded`);
    const transition = await page.evaluate(() => getComputedStyle(document.querySelector("a") || document.body).transitionDuration);
    if (transition !== "0s") problems.push(`${width}px: transitions active under reduced motion`);
    const shot = await page.screenshot({ fullPage: true });
    const fullH = await page.evaluate(() => document.documentElement.scrollHeight);
    fs.writeFileSync(path.join(out, `dashboard-${width}.png`), RAW ? shot : await frame(browser, shot, width, fullH));
    console.log(`${width}px: scrollWidth=${scrollW} fonts=${[...new Set(fonts)].sort().join("; ")}`);
    await ctx.close();
  }
  await browser.close();
  for (const p of problems) console.log("PROBLEM " + p);
  process.exit(problems.length ? 1 : 0);
})();
