import { chromium, devices } from 'playwright-core';
const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome', args: ['--no-sandbox'] });
const errs = [];
// --- game over + save/load (desktop)
const p = await b.newPage({ viewport: { width: 1152, height: 648 } });
p.on('pageerror', (e) => errs.push('PAGEERROR ' + e.message));
p.on('console', (m) => { if (m.type() === 'error' && !m.text().includes('404')) errs.push(m.text()); });
await p.goto('http://localhost:5173/?debug=floresta,36,20');
await p.waitForTimeout(2500);
const ev = (f) => p.evaluate(f);
await ev(() => { __rpg.G.hp = 1; const c = __rpg.world.script.ctx; c.spawn('wolf', 37, 20); c.spawn('wolf', 35, 20); });
await p.waitForTimeout(4500);
console.log('dead?', await ev(() => ({ st: __rpg.world.player.state, mods: __rpg.world.modals.map((m) => m.constructor.name) })));
await p.screenshot({ path: '/tmp/go.png' });
await p.keyboard.press('Enter'); await p.waitForTimeout(100); await p.keyboard.press('Enter'); await p.waitForTimeout(2500);
console.log('after continue', await ev(() => ({ st: __rpg.world.player.state, hp: __rpg.G.hp, map: __rpg.world.def.id, mods: __rpg.world.modals.length })));
// save to slot 1 through the menu
await p.keyboard.press('Escape'); await p.waitForTimeout(300);
for (let i = 0; i < 5; i++) { await p.keyboard.press('r'); await p.waitForTimeout(120); }
await p.keyboard.press('Enter'); await p.waitForTimeout(300);
await p.screenshot({ path: '/tmp/save.png' });
await p.keyboard.press('Enter'); await p.waitForTimeout(300);
console.log('saved', await ev(() => !!localStorage.getItem('aetheria_save_0')));
await p.close();
// --- title -> continue
const q = await b.newPage({ viewport: { width: 1152, height: 648 } });
q.on('pageerror', (e) => errs.push('PAGEERROR ' + e.message));
await q.goto('http://localhost:5173/');
await q.evaluate(() => {});
await q.waitForTimeout(100);
await q.close();
// --- mobile
const ctx = await b.newContext({ ...devices['Pixel 7'], viewport: { width: 915, height: 412 }, hasTouch: true });
const m = await ctx.newPage();
m.on('pageerror', (e) => errs.push('MOBILE PAGEERROR ' + e.message));
await m.goto('http://localhost:5173/?debug=vila_alvorada,25,24');
await m.waitForTimeout(3000);
await m.screenshot({ path: '/tmp/mobile.png' });
console.log(errs.length ? 'ERRORS ' + errs.join('\n') : 'NO ERRORS');
await b.close();
