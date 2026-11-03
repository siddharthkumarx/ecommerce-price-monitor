// Screenshot the built dashboard at 360, 768 and 1440 px and run layout checks.
//
//   uv run python -m pricemon.site --data <data dir> --out site
//   node scripts/screenshots.cjs site
//
// Needs Playwright for Node with Chromium (pre-installed in the cloud sandbox).
// Checks per width: no horizontal page scroll, no request leaves file://, every
// visible text node meets 4.5:1 contrast on its effective background, both font
// families load, and reduced motion is honoured. Screenshots: site/screenshots/
// (not committed).
const path = require("path");
const fs = require("fs");
const { chromium } = require("playwright");

const WIDTHS = [360, 768, 1440];

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
  const site = path.resolve(process.argv[2] || "site");
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
    for (const fam of ["Instrument Sans", "IBM Plex Mono"]) if (!families.has(fam)) problems.push(`${width}px: font ${fam} not loaded`);
    const transition = await page.evaluate(() => getComputedStyle(document.querySelector("a") || document.body).transitionDuration);
    if (transition !== "0s") problems.push(`${width}px: transitions active under reduced motion`);
    await page.screenshot({ path: path.join(out, `dashboard-${width}.png`), fullPage: true });
    console.log(`${width}px: scrollWidth=${scrollW} fonts=${[...new Set(fonts)].sort().join("; ")}`);
    await ctx.close();
  }
  await browser.close();
  for (const p of problems) console.log("PROBLEM " + p);
  process.exit(problems.length ? 1 : 0);
})();
