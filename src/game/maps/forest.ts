import { MB } from '../world/map';
import { registerMap } from '../world/maps';
import { T } from '../../art/tiles';
import { G } from '../state';
import type { ScriptCtx } from '../script';
import type { NpcDef } from '../world/map';

const LYRA: NpcDef = { id: 'lyra_scene', name: 'Lyra', look: 'lyra', tx: 38, ty: 26, dir: 'left', talk: async () => {} };

export function buildForest() {
  const W = 70, H = 60;
  const m = new MB('floresta', 'Floresta Sussurrante', W, H, T.DGRASS, 303);
  const rng = m.rng;
  m.patches(T.MOSS, 16, 2.5, 6, [T.DGRASS]);
  m.patches(T.GRASS, 14, 3, 7, [T.DGRASS, T.MOSS]);
  m.patches(T.GRASS2, 8, 2, 5, [T.GRASS]);
  m.patches(T.FLOWER, 22, 1.2, 3, [T.GRASS, T.GRASS2]);
  // stream with bridge
  m.path(T.WATER, [[0, 14], [14, 15], [28, 13], [44, 15], [58, 13], [69, 14]], 3, 1.6);
  // main path
  const main: [number, number][] = [[35, 1], [36, 10], [31, 18], [36, 26], [42, 32], [34, 38], [35, 44], [35, 52], [35, 59]];
  m.path(T.DIRT, main, 3, 1.4);
  for (let y = 9; y <= 19; y++) for (let x = 31; x <= 35; x++) if (m.get(x, y) === T.WATER) m.set(T.BRIDGE, x, y);
  m.path(T.DIRT, [[35, 1], [35, 5]], 3);
  // branches
  m.path(T.DIRT, [[38, 22], [48, 22], [58, 20]], 2, 1);
  m.path(T.DIRT, [[31, 30], [20, 34], [12, 44]], 2, 1.2);
  // clearings
  m.blob(T.GRASS, 36, 26, 8, 5.5, 0.3);
  m.blob(T.DIRT, 36, 26, 4.5, 3, 0.3);
  m.blob(T.GRASS, 35, 38, 5, 4, 0.3);
  m.blob(T.GRASS, 35, 48, 10, 8, 0.2);           // boss arena
  m.blob(T.DIRT, 35, 48, 7.5, 6, 0.3);
  m.blob(T.GRASS, 58, 20, 8, 6, 0.3);               // goblin camp
  m.blob(T.DIRT, 58, 20, 6, 4.5, 0.3);
  m.blob(T.GRASS, 12, 46, 9, 7, 0.3);               // slime king glade
  m.blob(T.MOSS, 12, 46, 6.5, 5, 0.3);
  m.fill(T.DIRT, 34, 50, 3, 10);
  // tiny pond
  m.blob(T.SAND, 54, 38, 5.5, 4, 0.3); m.blob(T.WATER, 54, 38, 4, 2.8, 0.3);
  m.blob(T.SAND, 18, 24, 4.5, 3.5, 0.3); m.blob(T.WATER, 18, 24, 3, 2.2, 0.3);
  m.scatterTiles(T.DIRT, 30, [T.DIRT]);

  // set pieces
  m.obj('campfire', 36, 26, 0);
  m.obj('crate', 34, 25, 0); m.obj('barrel', 39, 27, 0); m.obj('tent', 31, 26, 2);
  m.obj('save_crystal', 38, 5, 0);
  m.obj('save_crystal', 38, 39, 0);
  m.obj('torch', 33, 43, 0); m.obj('torch', 37, 43, 0);
  m.obj('sign', 37, 3, 0); m.signs.push({ tx: 37, ty: 3, text: ['FLORESTA SUSSURRANTE', 'Cuidado: lobos e criaturas sombrias. Não saia da trilha após o anoitecer.'] });
  m.obj('sign', 33, 41, 0); m.signs.push({ tx: 33, ty: 41, text: ['Adiante: clareira da Alfa. Apenas caçadores experientes.'] });
  m.obj('tent', 55, 17, 1); m.obj('tent', 61, 22, 1); m.obj('campfire', 58, 21, 0); m.obj('crate', 57, 18, 0); m.obj('barrel', 62, 19, 0); m.obj('banner_red', 59, 16, 0);
  m.obj('crystal', 8, 50, 0); m.obj('crystal', 16, 42, 1);
  for (const [x, y] of [[29, 47], [41, 47], [29, 51], [41, 51]]) m.obj('rock', x, y, 1);
  m.chests.push({ id: 'f_c1', tx: 62, ty: 17, item: 'vigor_ring' });
  m.chests.push({ id: 'f_c2', tx: 9, ty: 44, item: 'mage_robe' });
  m.chests.push({ id: 'f_c3', tx: 25, ty: 8, gold: 80 });
  m.chests.push({ id: 'f_c4', tx: 54, ty: 43, item: 'hi_potion', count: 2 });
  m.chests.push({ id: 'f_c5', tx: 47, ty: 5, item: 'ether', count: 3 });

  // trees
  const edgeGaps = [{ x0: 33, y0: 0, x1: 37, y1: 3 }, { x0: 33, y0: 56, x1: 37, y1: 59 }];
  m.treeBorder(2, edgeGaps, ['tree', 'tree', 'pine', 'pine', 'dead_tree']);
  const forestG = [T.DGRASS, T.MOSS];
  const avoid = [{ x: 36, y: 26, r: 9 }, { x: 35, y: 48, r: 11 }, { x: 58, y: 20, r: 9 }, { x: 12, y: 46, r: 10 }, { x: 35, y: 38, r: 6 }];
  m.scatter(['tree', 'tree', 'pine', 'pine', 'fruit_tree', 'autumn_tree', 'dead_tree'], 330, 2, 2, W - 3, H - 3, { grounds: forestG, gap: 1, avoid });
  m.scatter(['bush'], 70, 2, 2, W - 3, H - 3, { grounds: [T.DGRASS, T.MOSS, T.GRASS], gap: 1, vmax: 1 });
  m.scatter(['rock'], 22, 2, 2, W - 3, H - 3, { grounds: [T.DGRASS, T.MOSS, T.GRASS], gap: 1, vmax: 1 });
  m.scatter(['plant'], 14, 2, 2, W - 3, H - 3, { grounds: [T.MOSS, T.GRASS], gap: 1, vmax: 2 });
  m.scatter(['woodpile', 'barrel'], 6, 2, 2, W - 3, H - 3, { grounds: [T.DGRASS, T.GRASS], gap: 2 });
  for (const a of avoid) void a;

  // ---------------- spawns
  const walk: number[] = [T.DGRASS, T.MOSS, T.GRASS, T.GRASS2, T.FLOWER, T.DIRT];
  const spawnRand = (id: string, n: number, x0: number, y0: number, x1: number, y1: number, minFromStart = 14) => {
    let placed = 0, tries = 0;
    while (placed < n && tries < 400) {
      tries++;
      const x = rng.int(x0, x1), y = rng.int(y0, y1);
      if (!m.free(x, y) || !walk.includes(m.get(x, y))) continue;
      if (Math.hypot(x - 35, y - 3) < minFromStart) continue;
      if (Math.hypot(x - 35, y - 48) < 9 || Math.hypot(x - 35, y - 38) < 5) continue;
      m.spawns.push({ enemy: id, tx: x, ty: y });
      placed++;
    }
  };
  spawnRand('slime', 9, 4, 5, 66, 56, 10);
  spawnRand('bat', 6, 4, 18, 66, 56);
  spawnRand('mushroom', 6, 4, 8, 66, 56);
  spawnRand('wolf', 5, 25, 20, 50, 40);
  spawnRand('goblin', 3, 52, 15, 64, 25, 5);
  spawnRand('goblin_archer', 2, 52, 15, 64, 25, 5);
  spawnRand('slime_blue', 3, 4, 38, 24, 56);
  m.spawns.push({ enemy: 'boss_wolf', tx: 35, ty: 47, id: 'boss_fenrisa', once: true });
  m.spawns.push({ enemy: 'boss_slimeking', tx: 12, ty: 46, id: 'boss_slimeking', once: true });

  // ---------------- barrier (roots) until boss defeated
  m.barriers.push({ id: 'roots', tx: 34, ty: 54, w: 3, h: 1, openFlag: 'dead_boss_fenrisa', color: '#8a5a2a' });
  m.obj('tree', 33, 54, 0); m.obj('tree', 37, 54, 1);

  // ---------------- warps
  m.warps.push({ tx: 33, ty: 0, w: 5, h: 1, to: 'vila_alvorada', ntx: 25, nty: 34, dir: 'up' });
  m.warps.push({ tx: 33, ty: 58, w: 5, h: 2, to: 'caverna', ntx: 30, nty: 46, dir: 'up', need: () => (G.has('dead_boss_fenrisa') ? null : 'As raízes selvagens bloqueiam o caminho. A Alfa deve ser derrotada primeiro.') });

  // ---------------- events
  m.triggers.push({
    id: 'lyra_scene', tx: 33, ty: 24, w: 7, h: 4, once: true,
    run: async (c: ScriptCtx) => {
      await c.hero('Esse grito... Alguém está em perigo!', 'surprised');
      c.music('battle');
      c.world.spawnNpcFn(LYRA);
      await c.camTo(38, 26, 0.8);
      const w1 = c.spawn('wolf', 41, 25), w2 = c.spawn('wolf', 40, 28), w3 = c.spawn('wolf', 36, 29);
      void w1; void w2; void w3;
      await c.say('???', 'Afastem-se, vira-latas! Eu avisei... eu sou uma aprendiz de Celestia, sabiam?!', 'lyra', 'angry');
      await c.say('???', 'Ei, você aí! Sim, você! Pare de olhar e me ajude!', 'lyra', 'surprised');
      c.world.locked = false;
      await c.wait(0.2);
      c.unlock();
      await c.waitClear((e) => e.def.id === 'wolf');
      c.lock();
      c.music('');
      await c.wait(0.5);
      await c.say('Lyra', 'Hmpf... eu teria vencido sozinha. Mas... obrigada.', 'lyra', 'smug');
      await c.say('Lyra', 'Sou Lyra Valenne, aprendiz da Academia de Celestia. Fui enviada investigar as rachaduras na Aurora.', 'lyra');
      await c.hero(`${G.name}. Vim da Vila Alvorada. Estou indo à Caverna de Cristal, pelo Cristal Menor.`, 'neutral');
      await c.say('Lyra', 'O quê? Esse... pingente! Ele brilha com a luz da Aurora! Então a lenda é real!', 'lyra', 'surprised');
      await c.say('Lyra', 'Está decidido: vou com você. Preciso estudar esse Fragmento — e, claro, alguém precisa impedir que você morra por ser desastrado.', 'lyra', 'smug');
      await c.hero('...Eu acabei de salvar a sua vida.', 'angry');
      await c.say('Lyra', 'Detalhes! Vamos logo!', 'lyra', 'smile');
      c.world.npcs = c.world.npcs.filter((n) => n.def.id !== 'lyra_scene');
      await c.allyJoin('lyra');
      c.questStep('m1_forest', 1);
      c.world.musicOverride = null; c.music('');
      await c.give('lyra_letter', 1, true);
      await c.say('', 'Lyra, a Maga Aprendiz, agora luta ao seu lado! Ela conjura Bolas de Fogo e Lanças de Gelo automaticamente.');
    },
  });
  m.triggers.push({
    id: 'fenrisa_intro', tx: 31, ty: 43, w: 9, h: 2, once: true,
    run: async (c: ScriptCtx) => {
      c.music('');
      await c.camTo(35, 48, 1.0);
      c.sfx('roar'); c.shake(6);
      await c.say('', 'Um uivo gutural ecoa pela clareira. Entre as raízes retorcidas, uma loba gigante de pelagem cinzenta ergue a cabeça.');
      if (G.has('ally_lyra')) await c.say('Lyra', 'Fenrisa, a Alfa Cinzenta! As lendas dizem que ela já foi guardiã da floresta... antes das Sombras a corromperem.', 'lyra', 'surprised');
      await c.hero('Então ela é a causa de tudo. Vamos acabar com isso!', 'angry');
      c.questStep('m1_forest', 1);
      c.world.musicOverride = 'boss'; c.music('boss');
      c.world.cam.x = c.world.player.x - 192; c.world.cam.y = c.world.player.y - 108;
    },
  });
  return m.build({ music: 'forest', ambient: 'fireflies', tint: '#d8e6d8', start: { tx: 35, ty: 3 }, saveSpots: [{ tx: 38, ty: 5 }, { tx: 38, ty: 39 }] });
}
registerMap('floresta', buildForest);
