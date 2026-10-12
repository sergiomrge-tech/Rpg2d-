// usage: node scripts/shot.mjs <url> <out.png> [waitMs] [keys...]   keys like "down:300" "press:Enter" "wait:500"
import { chromium } from 'playwright-core';
const [, , url, out = '/tmp/shot.png', wait = '1500', ...acts] = process.argv;
const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome', args: ['--no-sandbox', '--use-gl=swiftshader', '--autoplay-policy=no-user-gesture-required'] });
const p = await b.newPage({ viewport: { width: 1152, height: 648 } });
const errs = [];
p.on('console', (m) => { if (m.type() === 'error' || m.type() === 'warning') errs.push(m.type() + ': ' + m.text()); });
p.on('pageerror', (e) => errs.push('PAGEERROR: ' + e.message + '\n' + (e.stack || '').split('\n').slice(0, 12).join('\n')));
await p.goto(url);
await p.waitForTimeout(parseInt(wait));
for (const a of acts) {
  const i0 = a.indexOf(':'); const k = a.slice(0, i0), v = a.slice(i0 + 1);
  if (k === 'wait') await p.waitForTimeout(parseInt(v));
  else if (k === 'press') { await p.keyboard.press(v); await p.waitForTimeout(120); }
  else if (k === 'down') { await p.keyboard.down(v.split('@')[0]); await p.waitForTimeout(parseInt(v.split('@')[1] ?? '300')); await p.keyboard.up(v.split('@')[0]); }
  else if (k === 'eval') { const r = await p.evaluate(v); if (r !== undefined) console.log('eval:', JSON.stringify(r)); }
  else if (k === 'shot') await p.screenshot({ path: v });
}
await p.screenshot({ path: out });
if (errs.length) console.log(errs.slice(0, 12).join('\n'));
await b.close();
