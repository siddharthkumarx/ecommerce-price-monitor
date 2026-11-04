// Print an HTML file to PDF with Chromium: node scripts/html_to_pdf.cjs in.html out.pdf
const path = require("path");
const { chromium } = require("playwright");
(async () => {
  const [src, out] = process.argv.slice(2);
  const browser = await chromium.launch();
  const page = await browser.newPage();
  await page.goto("file://" + path.resolve(src));
  await page.evaluate(() => document.fonts.ready);
  await page.pdf({ path: out, format: "A4", printBackground: true, preferCSSPageSize: true });
  await browser.close();
})();
