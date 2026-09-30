// Renders every raster asset for both themes into assets/<theme>/ (shared ones into assets/).
// Usage: node render.mjs            (needs playwright + @fontsource files next to assets.html)
import { chromium } from 'playwright';
import fs from 'fs';
const base = 'file://' + new URL('./assets.html', import.meta.url).pathname;
const jobs = [];
for (const th of ['dark', 'light']) {
  fs.mkdirSync(`assets/${th}`, { recursive: true });
  jobs.push(['bg-hero', `${th}/bg-hero@2x.png`, { th }, 1, true],
            ['bg-quiet', `${th}/bg-quiet@2x.png`, { th }, 1, true],
            ['bg-photo', `${th}/bg-photo@2x.png`, { th }, 1, true],
            ['photoph', `${th}/photo-placeholder.png`, { th }, 1],
            ['lockup', `${th}/lockup.png`, { th }, 3],
            ['ten', `${th}/ten-lockup.png`, { th }, 2],
            ['hexglow', `${th}/hex-glow.png`, { th }, 1]);
}
jobs.push(['bg-section', 'bg-section@2x.png', {}, 1, true], ['lockup-white', 'lockup-white.png', {}, 3]);
jobs.push(['bar-v', 'bar-v.png', {}, 4], ['bar-h', 'bar-h.png', {}, 4]);
for (const n of ['01','02','03','04','05','06','07','08','09','10']) jobs.push(['num', `num-${n}.png`, { t: n }, 1]);
for (const t of (process.env.NUMS || '').split(',').filter(Boolean)) jobs.push(['num', `num-custom-${t.replace(/[^\w]/g, '_')}.png`, { t }, 1]);
const browser = await chromium.launch();
for (const [a, out, extra, dpr, bg] of jobs) {
  const page = await browser.newPage({ viewport: { width: 1920, height: 1080 }, deviceScaleFactor: bg ? 2 : dpr });
  await page.goto(`${base}?${new URLSearchParams({ a, ...extra })}`);
  await page.evaluate(() => document.fonts.ready);
  await page.waitForTimeout(120);
  if (bg) await page.screenshot({ path: `assets/${out}` });
  else await page.locator('#el').screenshot({ path: `assets/${out}`, omitBackground: true });
  await page.close();
}
await browser.close();
