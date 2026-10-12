import { makeSheet, HERO_LOOKS, NPC_LOOKS, CW, CH } from '../art/characters';
import type { Dir } from '../engine/util';

export function artPreview(extra: (ctx: CanvasRenderingContext2D, y: number) => number = (_c, y) => y) {
  const c = document.createElement('canvas');
  c.width = 1280; c.height = 720;
  c.style.background = '#3a5a3a';
  document.body.innerHTML = '';
  document.body.appendChild(c);
  const ctx = c.getContext('2d')!;
  ctx.imageSmoothingEnabled = false;
  ctx.fillStyle = '#3a5a3a'; ctx.fillRect(0, 0, 1280, 720);
  const S = 3;
  let y = 4;
  const all = { ...HERO_LOOKS, ...NPC_LOOKS };
  const names = Object.keys(all);
  const dirs: Dir[] = ['down', 'up', 'left', 'right'];
  let col = 0;
  for (const n of names) {
    const sh = makeSheet('prev_' + n, all[n]);
    let x = 4 + col * (CW * S * 4 + 12);
    for (const d of dirs) { ctx.drawImage(sh.frame('walk', d, 0), x, y, CW * S, CH * S); x += CW * S; }
    ctx.drawImage(sh.frame('walk', 'down', 1), x - CW * S * 4, y + CH * S, CW * S, CH * S);
    ctx.drawImage(sh.frame('attack', 'down', 1), x - CW * S * 3, y + CH * S, CW * S, CH * S);
    ctx.drawImage(sh.frame('cast', 'down', 0), x - CW * S * 2, y + CH * S, CW * S, CH * S);
    ctx.drawImage(sh.frame('attack', 'left', 1), x - CW * S * 1, y + CH * S, CW * S, CH * S);
    col++;
    if (col === 3) { col = 0; y += CH * S * 2 + 4; }
  }
  extra(ctx, y);
}

export function artZoom(names: string[], S = 10) {
  const c = document.createElement('canvas');
  c.width = 1280; c.height = 720;
  document.body.innerHTML = '';
  document.body.appendChild(c);
  const ctx = c.getContext('2d')!;
  ctx.imageSmoothingEnabled = false;
  ctx.fillStyle = '#3a5a3a'; ctx.fillRect(0, 0, 1280, 720);
  const all = { ...HERO_LOOKS, ...NPC_LOOKS } as Record<string, any>;
  let x = 4;
  for (const n of names) {
    const sh = makeSheet('z_' + n, all[n]);
    for (const [d, a, i] of [['down', 'walk', 1], ['left', 'walk', 1], ['up', 'walk', 0], ['down', 'attack', 1]] as const) {
      ctx.drawImage(sh.frame(a, d, i), x, 4, CW * S, CH * S); x += CW * S * 0.8;
    }
  }
}

import { portrait } from '../art/portraits';
import { icon } from '../art/icons';
import { monsterArt, MONSTER_ART } from '../art/monsters';
import { OBJECTS, houseDef, tileCanvas, TILE_INFO } from '../art/tiles';

export function portraitPreview() {
  const c = document.createElement('canvas');
  c.width = 1280; c.height = 720;
  document.body.innerHTML = '';
  document.body.appendChild(c);
  const ctx = c.getContext('2d')!;
  ctx.imageSmoothingEnabled = false;
  ctx.fillStyle = '#2a2040'; ctx.fillRect(0, 0, 1280, 720);
  const all = { ...HERO_LOOKS, ...NPC_LOOKS } as Record<string, any>;
  const names = ['kai', 'aiko', 'mira', 'lyra', 'torren', 'sylphie', 'rhea', 'velkan'];
  const emos = ['neutral', 'smile', 'angry', 'sad'] as const;
  names.forEach((n, i) => { ctx.drawImage(portrait(n, all[n], emos[i % 4]), 4 + (i % 8) * 150, 4, 56 * 2.6, 64 * 2.6); });
  // icons
  const ids = ['sword','slash','whirl','dash','slam','blades','fire','ice','bolt','nova','meteor','heal','shield','rage','ghost','spirit','potion_r','potion_b','elixir','herb','gem','key','coin','armor','robe','ring','amulet','boots','star','scroll','crystal','fang','core','cloth','bow','staff','axe','book'];
  ids.forEach((id, i) => ctx.drawImage(icon(id), 4 + i * 40, 190, 36, 36));
  // monsters
  let x = 4;
  for (const k of Object.keys(MONSTER_ART)) { const m = monsterArt(k); const S = m.w > 60 ? 2 : 3; ctx.drawImage(m.frames[0], x, 240, m.w * S, m.h * S); x += m.w * S + 6; if (x > 1200) break; }
}

export function worldPreview() {
  const c = document.createElement('canvas');
  c.width = 1280; c.height = 720;
  document.body.innerHTML = '';
  document.body.appendChild(c);
  const ctx = c.getContext('2d')!;
  ctx.imageSmoothingEnabled = false;
  ctx.fillStyle = '#2a2040'; ctx.fillRect(0, 0, 1280, 720);
  let x = 4, y = 4;
  for (const id of Object.keys(TILE_INFO).map(Number)) { for (let v = 0; v < Math.min(2, TILE_INFO[id].variants); v++) { ctx.drawImage(tileCanvas(id, v, 0), x, y, 32, 32); x += 34; } }
  x = 4; y = 80;
  let rowH = 0;
  const names = Object.keys(OBJECTS);
  for (const n of names) { const o = OBJECTS[n]; const cv = o.draw(0, 1); const S = 2; if (x + cv.width * S > 1270) { x = 4; y += rowH + 6; rowH = 0; } ctx.drawImage(cv, x, y, cv.width * S, cv.height * S); x += cv.width * S + 6; rowH = Math.max(rowH, cv.height * S); }
  const h = houseDef(5).draw(0, 0); if (x + h.width * 2 > 1270) { x = 4; y += rowH + 6; } ctx.drawImage(h, x, y, h.width * 2, h.height * 2);
}
