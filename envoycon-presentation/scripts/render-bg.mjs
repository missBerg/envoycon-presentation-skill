// Renders the "out-of-focus lights" slide backgrounds from backgrounds.html at 2x, text off.
// Output: assets/{dark,light}/bg-<name>@2x.png and assets/bg-section@2x.png (then downscale to 1920 JPEG).
import { chromium } from 'playwright';
import fs from 'fs';
const base = 'file://' + new URL('./backgrounds.html', import.meta.url).pathname;
const SET = { title: 'hero2', photo: 'speakerR', speaker: 'speaker', content: 'content', statement: 'statement', break: 'break' };
const jobs = [];
for (const th of ['dark', 'light']) { fs.mkdirSync(`assets/${th}`, { recursive: true });
  for (const [name, v] of Object.entries(SET)) if (!process.env.ONLY || process.env.ONLY.split(',').includes(name)) jobs.push([`v=${v}&th=${th}&txt=0`, `assets/${th}/bg-${name}@2x.png`]); }
if (!process.env.ONLY || process.env.ONLY.includes('section')) jobs.push(['v=section&th=pink&txt=0', 'assets/bg-section@2x.png']);
const b = await chromium.launch();
for (const [q, out] of jobs) { const p = await b.newPage({ viewport: { width: 1920, height: 1080 }, deviceScaleFactor: 2 });
  await p.goto(`${base}?${q}`); await p.waitForTimeout(200); await p.screenshot({ path: out }); await p.close(); }
await b.close();
