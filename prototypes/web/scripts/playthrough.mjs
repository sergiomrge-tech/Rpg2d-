// Automated Chapter-1 smoke test: node scripts/playthrough.mjs
import { chromium } from 'playwright-core';
const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome', args: ['--no-sandbox', '--use-gl=swiftshader'] });
const p = await b.newPage({ viewport: { width: 1152, height: 648 } });
const errs = [];
p.on('console', (m) => { if (m.type() === 'error' && !m.text().includes('404')) errs.push(m.text()); });
p.on('pageerror', (e) => errs.push('PAGEERROR: ' + e.message + '\n' + (e.stack || '').split('\n').slice(0, 8).join('\n')));
const ev = (f) => p.evaluate(f);
const sleep = (ms) => p.waitForTimeout(ms);
const log = (...a) => console.log(...a);
async function press(k, ms = 90) { await p.keyboard.press(k); await sleep(ms); }
async function advance(max = 60, shot) {
  let n = 0;
  while (n++ < max) {
    const open = await ev(() => __rpg.world.modals.length + (__rpg.world.script.running ? 1 : 0) + (__rpg.world.fadeA > 0.05 ? 1 : 0) + (__rpg.world.chapterText ? 1 : 0));
    if (!open) break;
    await press('Enter', 140);
    if (shot && n === shot[0]) await p.screenshot({ path: shot[1] });
  }
}
async function until(cond, max = 80, step = 150) { for (let i = 0; i < max; i++) { if (await ev(cond)) return true; await sleep(step); } return false; }
const tp = (x, y) => ev(`(()=>{const w=__rpg.world;w.player.x=${x}*16+8;w.player.y=${y}*16+8;w.player.vx=w.player.vy=0;w.cam.x=w.player.x-192;w.cam.y=w.player.y-108;})()`);
const killAll = (filter = 'true') => ev(`(()=>{const w=__rpg.world;for(const e of [...w.enemies]) if(${filter}) w.script.ctx.world.enemies.includes(e) && (e.hp=1, import('/src/game/world/combat.ts').then(m=>m.damageEnemy(w,e,99999,{noCrit:true,silent:true})));})()`);

await p.goto('http://localhost:5173/');
await sleep(2500);
// --- new game
await press('Enter'); await sleep(300); await press('Enter'); await sleep(300); await press('Enter'); await sleep(300);
await p.keyboard.type('Rin'); await press('Enter', 600);
await sleep(2500);
log('1. intro flags before', await ev(() => ({ map: __rpg.G.map, intro: __rpg.G.flags.intro_done })));
await advance(80, [6, '/tmp/pt_intro.png']);
await sleep(800);
log('1. after intro', await ev(() => ({ intro: __rpg.G.flags.intro_done, q: __rpg.G.quests.m1_call, inv: __rpg.G.inv.aurora_pendant, name: __rpg.G.name })));
// --- leave house
await ev(() => __rpg.world.warp('vila_alvorada', 10, 14, 'down'));
await sleep(1500);
log('2. in village', await ev(() => __rpg.world.def.id));
// --- Selene tutorial
await tp(28, 22); await sleep(400);
await ev(() => { __rpg.world.player.dir = 'up'; });
await press('e', 200);
await advance(40, [5, '/tmp/pt_selene.png']);
await sleep(600);
log('3. enemies spawned', await ev(() => ({ n: __rpg.world.enemies.length, tut: __rpg.G.flags.tutorial_done })));
await p.screenshot({ path: '/tmp/pt_tut_battle.png' });
await killAll();
await sleep(500);
await advance(30);
await sleep(1500);
await advance(10);
log('4. battle done', await ev(() => ({ b1: __rpg.G.flags.battle1_done, step: __rpg.G.quests.m1_call.step, miraNpc: __rpg.world.npcs.some((n) => n.def.id === 'mira_plaza') })));
// --- Mira
await ev(() => { const n = __rpg.world.npcs.find((n) => n.def.id === 'mira_plaza'); if (n) { const w = __rpg.world; w.player.x = n.x; w.player.y = n.y + 14; w.player.dir = 'up'; } });
await sleep(300); await press('e', 200);
await advance(60);
log('5. briefed', await ev(() => ({ b: __rpg.G.flags.mira_briefed, gold: __rpg.G.gold, step: __rpg.G.quests.m1_call.step })));
// --- shop
await ev(() => { const n = __rpg.world.npcs.find((n) => n.def.id === 'bento'); const w = __rpg.world; w.player.x = n.x; w.player.y = n.y + 14; w.player.dir = 'up'; });
await sleep(300); await press('e', 200); await advance(3);
await press('Enter', 200); await p.screenshot({ path: '/tmp/pt_shop.png' });
await press('Escape', 200); await advance(8);
log('6. inv after shop', await ev(() => ({ gold: __rpg.G.gold, inv: JSON.stringify(__rpg.G.inv), open: __rpg.world.modals.length })));
// --- menu
await press('Escape', 300); await p.screenshot({ path: '/tmp/pt_menu0.png' });
await press('r', 200); await press('r', 200);
await press('Enter', 200); await p.screenshot({ path: '/tmp/pt_menu_sk.png' });
await press('Escape', 300);
log('7. menu closed', await ev(() => __rpg.world.modals.length));
// --- forest
await advance(20);
await ev(() => __rpg.world.warp('floresta', 35, 3, 'down'));
await sleep(2000); await advance(5);
log('8. forest', await ev(() => ({ map: __rpg.world.def.id, q: __rpg.G.quests.m1_forest?.state, call: __rpg.G.quests.m1_call.state })));
await ev(() => { __rpg.world.enemies = []; });
await tp(36, 25); await sleep(500);
await advance(30, [4, '/tmp/pt_lyra.png']);
await sleep(500);
log('9. lyra fight', await ev(() => ({ wolves: __rpg.world.enemies.filter((e) => e.def.id === 'wolf').length, locked: __rpg.world.locked })));
await p.screenshot({ path: '/tmp/pt_lyra_fight.png' });
await killAll(`e.def.id==='wolf'`);
await sleep(1200);
await advance(40);
log('10. ally', await ev(() => ({ lyra: __rpg.G.flags.ally_lyra, allies: __rpg.world.allies.length, step: __rpg.G.quests.m1_forest.step })));
// --- boss fenrisa
await tp(35, 44); await sleep(500);
await advance(20, [3, '/tmp/pt_fenrisa_intro.png']);
await sleep(800);
await p.screenshot({ path: '/tmp/pt_fenrisa.png' });
log('11. boss alive', await ev(() => __rpg.world.enemies.some((e) => e.def.id === 'boss_wolf')));
await killAll(`e.def.id==='boss_wolf'`);
await sleep(2500); await advance(20);
log('12. boss dead', await ev(() => ({ dead: __rpg.G.flags.dead_boss_fenrisa, step: __rpg.G.quests.m1_forest.step, bar: !!__rpg.world.bossBar })));
// --- cave
await ev(() => __rpg.world.warp('caverna', 30, 46, 'up'));
await sleep(2200); await advance(30);
log('13. cave', await ev(() => ({ map: __rpg.world.def.id, q: __rpg.G.quests.m1_cave?.state })));
await killAll(`e.spawnId==='golem_key'`);
await sleep(800);
await ev(() => { const w = __rpg.world; const k = w.pickups.find((k) => k.id === 'crystal_key'); if (k) { w.player.x = k.x; w.player.y = k.y; } });
await sleep(900);
log('14. key', await ev(() => ({ key: __rpg.G.inv.crystal_key, step: __rpg.G.quests.m1_cave.step })));
await tp(30, 16); await sleep(600); await advance(20);
log('15. seal', await ev(() => ({ open: __rpg.G.flags.cave_seal_open, step: __rpg.G.quests.m1_cave.step })));
await sleep(500);
await tp(30, 10); await sleep(500); await advance(20, [3, '/tmp/pt_cristalion_intro.png']);
await sleep(800); await p.screenshot({ path: '/tmp/pt_cristalion.png' });
await killAll(`e.def.id==='boss_crystal'`);
await sleep(2000); await advance(60, [8, '/tmp/pt_velkan.png']);
await sleep(1500);
log('16. after boss', await ev(() => ({ dead: __rpg.G.flags.dead_boss_cristalion, step: __rpg.G.quests.m1_cave.step, shard: __rpg.G.inv.aurora_shard_1 })));
// --- return to village
await ev(() => { const w = __rpg.world; w.pickups.forEach((k) => { k.x = w.player.x; k.y = w.player.y; k.magnet = true; k.t = 1; }); });
await sleep(800);
await ev(() => __rpg.world.warp('vila_alvorada', 25, 22, 'down'));
await sleep(2500);
await advance(80, [10, '/tmp/pt_end1.png']);
await sleep(1000);
await p.screenshot({ path: '/tmp/pt_end.png' });
await sleep(4000); await advance(10);
log('17. chapter end', await ev(() => ({ done: __rpg.G.flags.ch1_done, q: __rpg.G.quests.m1_cave.state, lvl: __rpg.G.level, gold: __rpg.G.gold })));
await p.screenshot({ path: '/tmp/pt_final.png' });
console.log(errs.length ? 'ERRORS:\n' + errs.slice(0, 15).join('\n') : 'NO ERRORS');
await b.close();
