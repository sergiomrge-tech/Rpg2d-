// Renders art sheets to PNG for visual inspection: node scripts/preview-art.mjs <page> <out>
import { chromium } from 'playwright-core';
const [, , url = 'http://localhost:5173/?artpreview=1', out = '/tmp/art.png'] = process.argv;
const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome', args: ['--no-sandbox'] });
const p = await b.newPage({ viewport: { width: 1280, height: 720 } });
p.on('console', (m) => console.log('console:', m.text()));
p.on('pageerror', (e) => console.log('pageerror:', e.message));
await p.goto(url);
await p.waitForTimeout(1500);
await p.screenshot({ path: out });
await b.close();
