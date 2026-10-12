import { MB } from '../world/map';
import { registerMap } from '../world/maps';
import { T } from '../../art/tiles';
import { G } from '../state';
import type { ScriptCtx } from '../script';

export function buildCave() {
  const W = 64, H = 52;
  const m = new MB('caverna', 'Caverna de Cristal', W, H, T.WALL, 505);
  const rng = m.rng;
  // cellular automaton
  let grid: boolean[][] = [];
  for (let y = 0; y < H; y++) { grid[y] = []; for (let x = 0; x < W; x++) grid[y][x] = x < 3 || y < 3 || x >= W - 3 || y >= H - 3 ? true : rng.next() < 0.43; }
  for (let it = 0; it < 4; it++) {
    const ng: boolean[][] = [];
    for (let y = 0; y < H; y++) { ng[y] = []; for (let x = 0; x < W; x++) {
      let n = 0;
      for (let j = -1; j <= 1; j++) for (let i = -1; i <= 1; i++) { if (!i && !j) continue; const yy = y + j, xx = x + i; if (yy < 0 || xx < 0 || yy >= H || xx >= W || grid[yy][xx]) n++; }
      ng[y][x] = x < 3 || y < 3 || x >= W - 3 || y >= H - 3 ? true : n >= 5;
    } }
    grid = ng;
  }
  for (let y = 0; y < H; y++) for (let x = 0; x < W; x++) if (!grid[y][x]) m.set(T.CAVE, x, y);
  // guaranteed route: entrance -> west chamber -> east chamber (key golem) -> north -> boss door
  const route: [number, number][] = [[30, 49], [30, 42], [14, 38], [14, 28], [32, 26], [50, 28], [48, 18], [30, 17], [30, 14]];
  m.path(T.CAVE, route, 5, 1.2);
  // rooms
  m.blob(T.CAVE, 30, 45, 6, 4, 0.2);   // entrance hall
  m.blob(T.CAVE, 14, 33, 7, 6, 0.3);   // west chamber
  m.blob(T.CAVE, 50, 26, 8, 6, 0.3);   // east chamber (golem + key)
  m.blob(T.CAVE, 32, 24, 6, 4, 0.3);
  m.blob(T.CAVE, 48, 14, 6, 4, 0.3);   // side nook (chest)
  m.path(T.CAVE, [[48, 18], [48, 14]], 4);
  m.blob(T.CAVE, 10, 14, 6, 5, 0.3);   // hidden chest room
  m.path(T.CAVE, [[14, 28], [10, 18]], 4, 1);
  // boss chamber (rectangular, north)
  m.fill(T.DARKSTONE, 21, 2, 19, 11);
  m.fill(T.CRYSTAL, 28, 5, 5, 5);
  m.outline(T.DARKSTONE, 21, 2, 19, 11);
  m.fill(T.CAVE, 29, 13, 3, 2);      // doorway (behind barrier)
  // variety
  m.patches(T.MOSS, 14, 1.5, 3.5, [T.CAVE]);
  m.patches(T.DARKSTONE, 10, 1.5, 4, [T.CAVE]);
  m.patches(T.CRYSTAL, 12, 1, 2.5, [T.CAVE]);
  // water pools (not on route)
  for (const [cx, cy, rx, ry] of [[22, 36, 3, 2], [40, 36, 3.5, 2.5], [9, 44, 3, 2], [56, 40, 3, 2]] as number[][]) m.blob(T.WATER, cx, cy, rx, ry, 0.3, [T.CAVE, T.MOSS, T.CRYSTAL, T.DARKSTONE]);

  // set pieces
  m.obj('save_crystal', 33, 47, 0);
  m.obj('save_crystal', 33, 16, 0);
  m.obj('torch', 27, 49, 0); m.obj('torch', 33, 49, 0);
  m.obj('sign', 28, 46, 0); m.signs.push({ tx: 28, ty: 46, text: ['"Aqui repousa a luz esquecida. Quem a procura, que ouça o coração da pedra."', '— inscrição antiga'] });
  m.chests.push({ id: 'c_c1', tx: 12, ty: 14, item: 'swift_boots' });
  m.chests.push({ id: 'c_c2', tx: 49, ty: 13, item: 'hi_ether', count: 2 });
  m.chests.push({ id: 'c_c3', tx: 9, ty: 35, item: 'chain_mail' });
  m.chests.push({ id: 'c_c4', tx: 54, ty: 29, gold: 220 });
  m.chests.push({ id: 'c_c5', tx: 30, ty: 40, item: 'potion', count: 3 });
  // boss room dressing
  for (const [x, y] of [[23, 4], [37, 4], [23, 9], [37, 9], [26, 6], [34, 6]]) m.obj('pillar', x, y, 0);
  m.obj('torch', 25, 3, 0); m.obj('torch', 35, 3, 0); m.obj('torch', 30, 3, 0);
  m.obj('banner_blue', 22, 3, 0); m.obj('banner_blue', 38, 3, 0);
  m.obj('portal', 29, 4, 0, { showFlag: 'dead_boss_cristalion' });
  // decoration
  const floor: number[] = [T.CAVE, T.MOSS, T.CRYSTAL, T.DARKSTONE];
  m.scatter(['crystal', 'crystal', 'red_crystal', 'stalagmite', 'cave_rock'], 120, 4, 16, W - 4, H - 4, { grounds: floor, gap: 1, open: true, vmax: 2, avoid: [{ x: 30, y: 47, r: 6 }] });
  m.scatter(['stalagmite', 'cave_rock'], 30, 4, 16, W - 4, H - 4, { grounds: floor, gap: 1, open: true });

  // enemies
  const walk: number[] = floor;
  const sp = (id: string, n: number, x0: number, y0: number, x1: number, y1: number) => {
    let placed = 0, tries = 0;
    while (placed < n && tries < 500) { tries++; const x = rng.int(x0, x1), y = rng.int(y0, y1); if (!m.free(x, y) || !walk.includes(m.get(x, y))) continue; if (Math.hypot(x - 30, y - 46) < 11) continue; if (y < 14 && x > 20 && x < 41) continue; m.spawns.push({ enemy: id, tx: x, ty: y }); placed++; }
  };
  sp('bat', 7, 4, 16, 60, 46); sp('slime_blue', 6, 4, 16, 60, 46); sp('skeleton', 5, 4, 20, 60, 46); sp('mushroom', 3, 4, 20, 60, 46);
  sp('wisp', 3, 4, 16, 60, 40); sp('skeleton_mage', 2, 8, 16, 56, 36);
  m.spawns.push({ enemy: 'golem', tx: 52, ty: 27, id: 'golem_key', once: true });
  m.spawns.push({ enemy: 'golem', tx: 13, ty: 33, id: 'golem_west', once: true });
  m.spawns.push({ enemy: 'boss_crystal', tx: 30, ty: 7, id: 'boss_cristalion', once: true });

  // seal barrier
  m.barriers.push({ id: 'seal', tx: 29, ty: 13, w: 3, h: 1, openFlag: 'cave_seal_open', color: '#7ae8ff' });
  m.triggers.push({
    id: 'seal', tx: 27, ty: 15, w: 7, h: 3, once: false,
    cond: () => !G.has('cave_seal_open'),
    run: async (c: ScriptCtx) => {
      if (G.count('crystal_key') > 0) {
        await c.narrate('A Chave de Cristal vibra e flutua em direção ao selo...');
        c.take('crystal_key', 1);
        c.sfx('save'); c.shake(4);
        c.flag('cave_seal_open', true);
        c.questStep('m1_cave', 2);
        await c.wait(0.8);
        await c.narrate('O selo da Câmara Profunda se dissolve em partículas de luz.');
      } else if (!G.has('seal_hint')) {
        c.flag('seal_hint', true);
        await c.narrate('Um selo de cristal bloqueia a passagem. Há uma fechadura em formato de losango. Uma chave deve estar nas profundezas da caverna.');
      }
    },
  });
  m.triggers.push({
    id: 'cristalion_intro', tx: 26, ty: 9, w: 9, h: 4, once: true,
    run: async (c: ScriptCtx) => {
      c.music('');
      await c.camTo(30, 6, 1.0);
      c.sfx('roar'); c.shake(8);
      await c.say('', 'Uma presença colossal desperta. O cristal no centro da câmara se parte e um gigante de pedra azul se ergue.');
      await c.say('Cristalion', 'QUEM... PERTURBA... O SONO... DA AURORA...?', undefined);
      if (G.has('ally_lyra')) await c.say('Lyra', 'Um Guardião de Cristal! Ele ainda protege o Cristal Menor — mas as Sombras o corromperam. Ele não vai nos ouvir!', 'lyra', 'surprised');
      await c.hero('Então vamos libertá-lo!', 'angry');
      c.world.musicOverride = 'boss'; c.music('boss');
    },
  });
  m.warps.push({ tx: 29, ty: 50, w: 3, h: 2, to: 'floresta', ntx: 35, nty: 55, dir: 'up' });
  m.warps.push({ tx: 29, ty: 4, w: 2, h: 1, to: 'vila_alvorada', ntx: 25, nty: 22, dir: 'down', need: () => (G.has('dead_boss_cristalion') ? null : 'O portal está dormente.') });
  m.def = { start: { tx: 30, ty: 48 } };
  return m.build({ music: 'cave', dark: 0.6, ambient: 'dust', wallKind: 'cave', tint: '#dcd8ff' });
}
registerMap('caverna', buildCave);
