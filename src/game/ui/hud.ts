import { VW, VH, text, panel, bar, measure } from '../../engine/display';
import { G, xpToNext } from '../state';
import { SKILL_MAP, rankCd } from '../data/skills';
import { ITEMS } from '../data/items';
import { QUESTS } from '../data/quests';
import { icon } from '../../art/icons';
import { portrait } from '../../art/portraits';
import { HERO_LOOKS } from '../../art/characters';
import { mk } from '../../art/pixel';
import { T, TS } from '../../art/tiles';
import type { World } from '../world/world';

const MINI_COL: Record<number, string> = {
  [T.GRASS]: '#4a9a46', [T.GRASS2]: '#448e42', [T.FLOWER]: '#58a84e', [T.DIRT]: '#b98d5c', [T.STONE]: '#9a9aa8', [T.WATER]: '#3d86d8',
  [T.SAND]: '#e6d29a', [T.CAVE]: '#5a5078', [T.WOOD]: '#a8693a', [T.BRIDGE]: '#9a6a3a', [T.WALL]: '#1c1628', [T.DEEP]: '#1e4f9a',
  [T.DGRASS]: '#2f6e46', [T.MOSS]: '#3f7a6a', [T.CRYSTAL]: '#6a7a9a', [T.RUG]: '#b8323f', [T.COBBLE]: '#8c8a98', [T.VOID]: '#000000',
  [T.ICEFLOOR]: '#a8d4f0', [T.DARKSTONE]: '#4a4560', [T.DSAND]: '#e8c56e', [T.DCOBBLE]: '#a89878', [T.ADOBE]: '#c98a58', [T.SNOW]: '#e8f0fa',
};

export function drawMinimapInit(w: World) {
  const { def } = w;
  const [canvas, ctx] = mk(def.w, def.h);
  const color = new Array<string>(def.w * def.h);
  for (let i = 0; i < def.w * def.h; i++) color[i] = MINI_COL[def.ground[i]] ?? '#444';
  for (const o of def.objs) {
    if (o.type === 'tree' || o.type === 'pine' || o.type === 'fruit_tree' || o.type === 'autumn_tree' || o.type === 'dead_tree') { if (o.tx >= 0 && o.tx < def.w && o.ty >= 0 && o.ty < def.h) color[o.ty * def.w + o.tx] = '#1f5a34'; }
    else if (o.type.startsWith('house')) { const ww = parseInt(o.type.slice(5)); for (let j = -3; j <= 0; j++) for (let i = 0; i < ww; i++) { const x = o.tx + i, y = o.ty + j; if (x >= 0 && y >= 0 && x < def.w && y < def.h) color[y * def.w + x] = j < -1 ? '#c9483a' : '#e8d8b8'; } }
    else if (o.type === 'fountain') { for (let j = -1; j <= 0; j++) for (let i = 0; i < 3; i++) color[(o.ty + j) * def.w + o.tx + i] = '#6ab0f0'; }
  }
  return {
    canvas,
    reveal(x: number, y: number) { ctx.fillStyle = color[y * def.w + x]; ctx.fillRect(x, y, 1, 1); },
  };
}

const faceCache = new Map<string, HTMLCanvasElement>();
function hudFace(look: 'kai' | 'aiko', emo: 'neutral' | 'angry' | 'sad') {
  const k = look + emo;
  let c = faceCache.get(k);
  if (!c) {
    const p = portrait('hud_' + look, HERO_LOOKS[look], emo);
    const [cv, ctx] = mk(30, 30);
    ctx.imageSmoothingEnabled = true; ctx.imageSmoothingQuality = 'high';
    ctx.drawImage(p, 6, 8, 44, 44, 0, 0, 30, 30);
    c = cv; faceCache.set(k, c);
  }
  return c;
}

const skillKeys = ['1', '2', '3', '4'];

export function drawHud(w: World, u: CanvasRenderingContext2D) {
  const st = G.stats();
  const p = w.player;
  // ---------------- player card
  const x0 = 6, y0 = 6;
  panel(u, x0, y0, 36, 36, { fill: '#1a1030', border: '#e8c872' });
  const lowHp = G.hp < st.maxHp * 0.3;
  u.drawImage(hudFace(G.look, lowHp ? 'sad' : p.hurtT > 0 ? 'angry' : 'neutral'), x0 + 3, y0 + 3);
  // level badge
  u.fillStyle = '#05020c'; u.fillRect(x0 + 24, y0 + 26, 14, 10);
  u.fillStyle = '#e8c872'; u.fillRect(x0 + 25, y0 + 27, 12, 8);
  text(u, String(G.level), x0 + 31, y0 + 27, { size: 8, color: '#2a1a08', align: 'center', shadow: null, bold: true });
  const bx = x0 + 42, bw = 92;
  text(u, 'HP', bx, y0 - 1, { size: 8, color: '#ffb0b8' });
  bar(u, bx + 14, y0 + 2, bw - 14, 8, G.hp / st.maxHp, lowHp && Math.floor(w.time * 4) % 2 ? '#ff9aa8' : '#e8405a', '#ff7a8a', '#3a1020');
  text(u, `${Math.ceil(G.hp)}/${st.maxHp}`, bx + 14 + (bw - 14) / 2, y0 + 1.5, { size: 7, align: 'center', color: '#fff' });
  text(u, 'MP', bx, y0 + 11, { size: 8, color: '#a8c8ff' });
  bar(u, bx + 14, y0 + 14, bw - 14, 8, G.mp / st.maxMp, '#3a78e8', '#6aa8ff', '#101a3a');
  text(u, `${Math.ceil(G.mp)}/${st.maxMp}`, bx + 14 + (bw - 14) / 2, y0 + 13.5, { size: 7, align: 'center', color: '#fff' });
  bar(u, bx + 14, y0 + 26, bw - 14, 3, G.xp / xpToNext(G.level), '#e8c050', '#ffe888', '#2a2008');
  text(u, 'XP', bx, y0 + 22, { size: 8, color: '#f0d890' });
  if (p.shield > 0) { u.drawImage(icon('shield'), bx + bw + 4, y0, 12, 12); text(u, String(Math.ceil(p.shield)), bx + bw + 18, y0 + 2, { size: 7, color: '#9ad8ff' }); }
  if (p.buffT > 0) { u.drawImage(icon('rage'), bx + bw + 4, y0 + 13, 12, 12); text(u, `${Math.ceil(p.buffT)}s`, bx + bw + 18, y0 + 15, { size: 7, color: '#ff9a8a' }); }
  if (G.sp > 0) text(u, `★ ${G.sp} pts de habilidade (ESC)`, x0, y0 + 38, { size: 7, color: '#ffe066' });

  // ---------------- quest tracker
  const q = currentTracker();
  if (q) {
    const ty = G.sp > 0 ? 56 : 48;
    const lines = [q.name, q.step];
    const tw = Math.min(150, Math.max(measure(u, lines[0], 8), measure(u, lines[1], 7)) + 10);
    u.globalAlpha = 0.85;
    panel(u, 6, ty, tw + 2, 26, { fill: '#120a22', border: '#7a6aa8', accent: '#3a2a60' });
    u.globalAlpha = 1;
    text(u, lines[0], 12, ty + 3, { size: 8, color: '#ffe066' });
    text(u, lines[1], 12, ty + 14, { size: 7, color: '#d8d0f0' });
  }

  // ---------------- skill bar
  const sw = 22, gap = 3;
  const total = 4 * sw + 3 * gap + 2 * (sw - 4) + 8;
  let sx = Math.round((VW - total) / 2);
  const sy = VH - sw - 6;
  for (let i = 0; i < 4; i++) {
    const id = G.slots[i];
    const def = id ? SKILL_MAP[id] : null;
    const x = sx + i * (sw + gap);
    panel(u, x, sy, sw, sw, { fill: '#150d26', border: def ? '#e8c872' : '#4a4068', accent: '#2a2048' });
    if (def) {
      const rank = G.skillRank(def.id);
      const cd = p.cd[i], cdMax = rankCd(def, rank);
      u.globalAlpha = cd > 0 ? 0.45 : 1;
      u.drawImage(icon(def.icon), x + 2, y2(sy));
      u.globalAlpha = 1;
      if (cd > 0) {
        u.fillStyle = 'rgba(8,4,24,.75)';
        const h = Math.round((sw - 4) * (cd / cdMax));
        u.fillRect(x + 2, sy + 2 + (sw - 4) - h, sw - 4, h);
        text(u, cd.toFixed(1), x + sw / 2, sy + 7, { size: 7, align: 'center' });
      } else if (G.mp < Math.round(def.mp * (1 + 0.06 * (rank - 1)))) { u.fillStyle = 'rgba(30,60,160,.45)'; u.fillRect(x + 2, sy + 2, sw - 4, sw - 4); }
    }
    text(u, skillKeys[i], x + 3, sy + sw - 8, { size: 7, color: '#ffe8a0' });
  }
  const px0 = sx + 4 * (sw + gap) + 8;
  for (let i = 0; i < 2; i++) {
    const ids = i === 0 ? ['potion', 'hi_potion', 'herb'] : ['ether', 'hi_ether'];
    const id = ids.find((k) => G.count(k) > 0) ?? ids[0];
    const x = px0 + i * (sw - 4 + gap);
    panel(u, x, sy + 4, sw - 4, sw - 4, { fill: '#150d26', border: '#6a5a98', accent: '#2a2048' });
    u.globalAlpha = G.count(id) > 0 ? 1 : 0.35;
    u.drawImage(icon(ITEMS[id].icon), x + 1, sy + 5, 16, 16);
    u.globalAlpha = 1;
    text(u, String(G.count(ids.filter((k) => G.count(k) > 0)[0] ?? id)), x + sw - 5, sy + 15, { size: 7, align: 'right', color: '#fff' });
    text(u, i === 0 ? 'Q' : 'R', x + 2, sy + 1, { size: 6, color: '#ffe8a0' });
  }

  // ---------------- minimap
  drawMinimap(w, u);

  // ---------------- boss bar
  const b = w.bossBar;
  if (b && !b.dead) {
    const bw2 = 220, bx2 = (VW - bw2) / 2, by = 14;
    text(u, b.def.name, VW / 2, by - 11, { size: 9, align: 'center', color: '#ffd0d8', bold: true });
    panel(u, bx2 - 3, by - 3, bw2 + 6, 12, { fill: '#1a0818', border: '#c0384a', accent: '#601828' });
    bar(u, bx2, by, bw2, 6, b.hp / b.maxHp, '#d83a4a', '#ff7a8a', '#3a1020');
    if (b.phase > 1) text(u, '▲', bx2 + bw2 + 6, by - 2, { size: 8, color: '#ff8a7a' });
  }

  // ---------------- toasts
  w.toasts.forEach((t, i) => {
    const a = Math.min(1, (3.2 - t.t) * 2, t.t * 6);
    const y = VH - 36 - i * 15;
    const wd = measure(u, t.text, 8) + (t.icon ? 22 : 10);
    u.globalAlpha = a;
    panel(u, 6, y, wd, 13, { fill: '#150d26', border: '#6a5a98', accent: '#2a2048' });
    let tx = 11;
    if (t.icon) { u.drawImage(icon(t.icon), 7, y - 3, 14, 14); tx = 22; }
    text(u, t.text, tx, y + 3, { size: 8, color: t.color });
    u.globalAlpha = 1;
  });

  // ---------------- banner
  if (w.banner) {
    const b2 = w.banner, t = b2.t;
    const a = t < 0.5 ? t / 0.5 : t > 2.8 ? Math.max(0, 1 - (t - 2.8) / 0.6) : 1;
    const y = b2.sub ? 74 : 84;
    u.globalAlpha = a;
    const grad = u.createLinearGradient(0, 0, VW, 0);
    grad.addColorStop(0, 'rgba(10,4,24,0)'); grad.addColorStop(0.5, 'rgba(10,4,24,.78)'); grad.addColorStop(1, 'rgba(10,4,24,0)');
    u.fillStyle = grad; u.fillRect(0, y - 6, VW, b2.sub ? 42 : 32);
    u.fillStyle = '#e8c872'; u.fillRect(VW / 2 - 90 * a, y - 6, 180 * a, 1); u.fillRect(VW / 2 - 90 * a, y + (b2.sub ? 36 : 26), 180 * a, 1);
    text(u, b2.text, VW / 2, y + 2, { size: 16, align: 'center', color: '#fff4c8', bold: true });
    if (b2.sub) text(u, b2.sub, VW / 2, y + 22, { size: 8, align: 'center', color: '#d8d0f0' });
    u.globalAlpha = 1;
  }
}

const y2 = (sy: number) => sy + 2;

function currentTracker(): { name: string; step: string } | null {
  const order = ['m1_call', 'm1_forest', 'm1_cave'];
  for (const id of order) {
    const q = G.quests[id];
    if (q && q.state === 'active') {
      const def = QUESTS[id];
      let step = def.steps[Math.min(q.step, def.steps.length - 1)];
      if (id === 'm1_cave' && q.step === 0) step = def.steps[0];
      return { name: def.name, step };
    }
  }
  for (const id of Object.keys(QUESTS)) {
    const q = G.quests[id];
    if (q && q.state === 'active') return { name: QUESTS[id].name, step: QUESTS[id].steps[Math.min(q.step, QUESTS[id].steps.length - 1)] };
  }
  return null;
}

function drawMinimap(w: World, u: CanvasRenderingContext2D) {
  const R = 29, cx = VW - R - 8, cy = R + 8;
  const S = 2;
  const p = w.player;
  const ptx = p.x / TS, pty = p.y / TS;
  u.save();
  u.beginPath(); u.arc(cx, cy, R, 0, Math.PI * 2); u.clip();
  u.fillStyle = '#0a0614'; u.fillRect(cx - R, cy - R, R * 2, R * 2);
  u.imageSmoothingEnabled = false;
  u.drawImage(w.mini.canvas, Math.round(cx - ptx * S), Math.round(cy - pty * S), w.def.w * S, w.def.h * S);
  const dot = (tx: number, ty: number, col: string, s = 2) => { const x = cx + (tx - ptx) * S, y = cy + (ty - pty) * S; if ((x - cx) ** 2 + (y - cy) ** 2 < R * R) { u.fillStyle = '#05020c'; u.fillRect(Math.round(x - s / 2 - 0.5), Math.round(y - s / 2 - 0.5), s + 1, s + 1); u.fillStyle = col; u.fillRect(Math.round(x - s / 2), Math.round(y - s / 2), s, s); } };
  const ex = w.explored.get(w.def.id);
  const seen = (tx: number, ty: number) => ex?.[Math.floor(ty) * w.def.w + Math.floor(tx)];
  for (const n of w.npcs) if (seen(n.x / TS, n.y / TS)) dot(n.x / TS, n.y / TS, '#ffe066');
  for (const c of w.chests) if (!c.opened && seen(c.x / TS, c.y / TS)) dot(c.x / TS, c.y / TS, '#ff9a3a');
  for (const wp of w.def.warps) if (seen(wp.tx, wp.ty)) dot(wp.tx + 0.5, wp.ty + 0.5, '#9affc0', 3);
  for (const e of w.enemies) if (e.state !== 'dying' && Math.hypot(e.x - p.x, e.y - p.y) < 190) dot(e.x / TS, e.y / TS, e.def.boss ? '#ff2a4a' : '#ff6a7a', e.def.boss ? 4 : 2);
  const blink = Math.floor(w.time * 3) % 2;
  u.fillStyle = '#05020c'; u.fillRect(cx - 3, cy - 3, 6, 6);
  u.fillStyle = blink ? '#ffffff' : '#7ad8ff'; u.fillRect(cx - 2, cy - 2, 4, 4);
  u.restore();
  // ring
  u.strokeStyle = '#05020c'; u.lineWidth = 3; u.beginPath(); u.arc(cx, cy, R + 1, 0, Math.PI * 2); u.stroke();
  u.strokeStyle = '#e8c872'; u.lineWidth = 1.5; u.beginPath(); u.arc(cx, cy, R, 0, Math.PI * 2); u.stroke();
  u.strokeStyle = '#7a5a2a'; u.lineWidth = 1; u.beginPath(); u.arc(cx, cy, R - 1.5, 0, Math.PI * 2); u.stroke();
  for (const [a, lab] of [[-Math.PI / 2, 'N']] as [number, string][]) text(u, lab, cx + Math.cos(a) * (R + 5) - 2, cy + Math.sin(a) * (R + 5) - 4, { size: 6, color: '#ffe8a0' });
  // gold + area
  u.drawImage(icon('coin'), VW - 70, cy + R + 3, 12, 12);
  text(u, String(G.gold), VW - 56, cy + R + 5, { size: 8, color: '#ffd84a' });
  text(u, w.def.name, VW - 8, cy + R + 16, { size: 7, align: 'right', color: '#c8c0e8' });
}
