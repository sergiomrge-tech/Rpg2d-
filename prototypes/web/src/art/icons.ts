import { Ctx, mk, px, rect, ramp, ellipse, shadedEllipse, outline, bitmap } from './pixel';

const cache = new Map<string, HTMLCanvasElement>();

function paint(id: string, ctx: Ctx) {
  const line = (x0: number, y0: number, x1: number, y1: number, c: string) => {
    const n = Math.max(Math.abs(x1 - x0), Math.abs(y1 - y0));
    for (let i = 0; i <= n; i++) px(ctx, Math.round(x0 + ((x1 - x0) * i) / n), Math.round(y0 + ((y1 - y0) * i) / n), c);
  };
  const steel = ramp('#c8d4e8', 5), gold = ramp('#f2c94c', 5), wood = ramp('#8a5a2a', 4);
  const sword = (c = steel) => { line(3, 12, 12, 3, c[3]); line(4, 12, 12, 4, c[2]); line(2, 11, 4, 13, gold[2]); line(2, 13, 3, 12, wood[2]); px(ctx, 12, 2, c[4]); px(ctx, 11, 3, c[4]); };
  switch (id) {
    case 'sword': sword(); break;
    case 'slash': for (let i = 0; i < 12; i++) { const a = -0.4 + i * 0.22; px(ctx, Math.round(3 + 10 * Math.cos(a)), Math.round(13 - 10 * Math.sin(a)), steel[4]); px(ctx, Math.round(3 + 9 * Math.cos(a)), Math.round(13 - 9 * Math.sin(a)), steel[2]); } break;
    case 'whirl': for (let r = 3; r <= 6; r += 3) for (let i = 0; i < 16; i++) { const a = i * 0.4 + r; px(ctx, Math.round(8 + r * Math.cos(a)), Math.round(8 + r * Math.sin(a)), r === 3 ? steel[3] : steel[4]); } sword(); break;
    case 'dash': for (let i = 0; i < 4; i++) rect(ctx, 1 + i, 4 + i * 2, 6 - i, 1, steel[2 + (i % 2)]); line(6, 12, 14, 4, steel[4]); px(ctx, 14, 3, '#fff'); break;
    case 'slam': rect(ctx, 6, 1, 4, 9, wood[2]); rect(ctx, 3, 9, 10, 4, steel[2]); rect(ctx, 3, 9, 10, 1, steel[4]); for (const x of [1, 14]) rect(ctx, x, 14, 1, 1, '#c9a070'); line(0, 14, 15, 14, '#c9a070'); break;
    case 'blades': sword(); line(3, 4, 12, 13, steel[3]); line(4, 4, 12, 12, steel[2]); break;
    case 'fire': { const f = ramp('#ff8a2a', 5); ellipse(ctx, 8, 10, 4, 5, f[2]); ellipse(ctx, 8, 11, 3, 3, f[3]); ellipse(ctx, 8, 12, 1, 2, f[4]); px(ctx, 7, 3, f[3]); px(ctx, 8, 4, f[2]); px(ctx, 8, 2, f[3]); px(ctx, 9, 5, f[2]); break; }
    case 'ice': { const f = ramp('#6ad0ff', 5); line(8, 1, 8, 14, f[3]); line(2, 4, 14, 11, f[3]); line(2, 11, 14, 4, f[3]); px(ctx, 8, 8, '#fff'); for (const [x, y] of [[8, 1], [8, 14], [2, 4], [14, 11], [2, 11], [14, 4]]) px(ctx, x, y, '#fff'); break; }
    case 'bolt': { const f = ramp('#ffe84a', 5); line(10, 1, 5, 8, f[3]); line(5, 8, 10, 8, f[3]); line(10, 8, 5, 15, f[3]); line(11, 1, 6, 8, f[4]); line(6, 9, 10, 9, f[4]); break; }
    case 'nova': { const f = ramp('#9ae8ff', 5); for (let i = 0; i < 24; i++) { const a = i * Math.PI / 12; px(ctx, Math.round(8 + 6 * Math.cos(a)), Math.round(8 + 6 * Math.sin(a)), f[3]); if (i % 3 === 0) px(ctx, Math.round(8 + 3 * Math.cos(a)), Math.round(8 + 3 * Math.sin(a)), f[4]); } ellipse(ctx, 8, 8, 1, 1, '#fff'); break; }
    case 'meteor': { const f = ramp('#ff8a2a', 5); shadedEllipse(ctx, 10, 10, 4, 4, ramp('#8a4a2a', 5)); for (let i = 0; i < 7; i++) { px(ctx, 6 - i, 6 - i, f[3]); px(ctx, 7 - i, 6 - i, f[2]); px(ctx, 6 - i, 7 - i, f[2]); } px(ctx, 9, 8, '#ffd8a0'); break; }
    case 'heal': { const f = ramp('#58e08a', 5); rect(ctx, 6, 2, 4, 12, f[3]); rect(ctx, 2, 6, 12, 4, f[3]); rect(ctx, 6, 2, 4, 1, f[4]); rect(ctx, 2, 6, 12, 1, f[4]); rect(ctx, 6, 13, 4, 1, f[1]); break; }
    case 'shield': { const f = ramp('#6a9aff', 5); for (let y = 0; y < 13; y++) { const w = y < 8 ? 6 : 6 - (y - 7); rect(ctx, 8 - w, 2 + y, w, 1, f[3]); rect(ctx, 8, 2 + y, w, 1, f[2]); } rect(ctx, 7, 4, 2, 8, '#fff2b0'); rect(ctx, 4, 6, 8, 2, '#fff2b0'); break; }
    case 'rage': { const f = ramp('#ff4a4a', 5); ellipse(ctx, 8, 9, 5, 5, f[2]); rect(ctx, 5, 7, 2, 2, '#fff'); rect(ctx, 9, 7, 2, 2, '#fff'); line(4, 5, 7, 7, '#400'); line(12, 5, 9, 7, '#400'); rect(ctx, 6, 11, 4, 1, '#400'); for (const x of [3, 8, 13]) px(ctx, x, 2, f[3]); break; }
    case 'ghost': { const f = ramp('#c8b8ff', 5); shadedEllipse(ctx, 8, 7, 5, 5, f); rect(ctx, 3, 8, 10, 6, f[2]); for (let i = 0; i < 5; i++) rect(ctx, 3 + i * 2, 14, 2, 1 + (i % 2), f[2]); rect(ctx, 5, 6, 2, 3, '#2a1a4a'); rect(ctx, 9, 6, 2, 3, '#2a1a4a'); break; }
    case 'spirit': { const f = ramp('#a0ffd8', 5); for (let i = 0; i < 3; i++) { const a = i * 2.1; ellipse(ctx, Math.round(8 + 5 * Math.cos(a)), Math.round(8 + 5 * Math.sin(a)), 2, 2, f[3]); px(ctx, Math.round(8 + 5 * Math.cos(a)) - 1, Math.round(8 + 5 * Math.sin(a)) - 1, '#fff'); } ellipse(ctx, 8, 8, 1, 1, f[4]); break; }
    case 'potion_r': case 'potion_b': case 'potion_g': case 'elixir': {
      const col = id === 'potion_r' ? '#ff4a6a' : id === 'potion_b' ? '#4a8aff' : id === 'potion_g' ? '#58e08a' : '#d86aff';
      const f = ramp(col, 5);
      rect(ctx, 6, 2, 4, 3, '#c8d4e8'); rect(ctx, 6, 1, 4, 1, '#8a5a2a'); shadedEllipse(ctx, 8, 10, 5, 5, f, { dither: false }); rect(ctx, 6, 4, 4, 3, f[2]);
      px(ctx, 6, 9, '#fff'); px(ctx, 6, 10, '#ffffffaa'); if (id === 'elixir') { px(ctx, 11, 7, '#fff2b0'); px(ctx, 4, 12, '#fff2b0'); }
      break;
    }
    case 'herb': { const f = ramp('#4aa850', 5); line(8, 14, 8, 6, f[1]); for (const [x, y, d] of [[8, 6, -1], [8, 8, 1], [8, 10, -1], [8, 4, 1]] as number[][]) { ellipse(ctx, x + d * 3, y, 3, 1, f[3]); } px(ctx, 8, 3, '#fff'); break; }
    case 'gem': { const f = ramp('#ff6ad0', 5); for (let y = 0; y < 10; y++) { const w = y < 4 ? 3 + y : 7 - (y - 4); rect(ctx, 8 - w + 1, 3 + y, w * 2 - 2, 1, y < 4 ? f[3] : f[2]); } rect(ctx, 5, 5, 2, 1, '#fff'); px(ctx, 4, 6, '#fff'); break; }
    case 'key': { ellipse(ctx, 5, 5, 3, 3, gold[3]); ellipse(ctx, 5, 5, 1, 1, '#05020c'); rect(ctx, 7, 7, 2, 7, gold[2]); line(8, 13, 11, 13, gold[2]); line(8, 10, 11, 10, gold[2]); break; }
    case 'coin': ellipse(ctx, 8, 8, 5, 5, gold[2]); ellipse(ctx, 8, 8, 4, 4, gold[3]); rect(ctx, 7, 5, 2, 6, gold[1]); px(ctx, 5, 6, '#fff'); break;
    case 'armor': { const f = ramp('#9aa8c0', 5); rect(ctx, 3, 3, 10, 11, f[2]); rect(ctx, 1, 3, 3, 4, f[3]); rect(ctx, 12, 3, 3, 4, f[3]); rect(ctx, 6, 2, 4, 2, '#05020c'); rect(ctx, 3, 3, 3, 11, f[3]); rect(ctx, 3, 10, 10, 1, gold[2]); break; }
    case 'robe': { const f = ramp('#8a6ad0', 5); rect(ctx, 4, 3, 8, 11, f[2]); rect(ctx, 2, 4, 3, 7, f[3]); rect(ctx, 11, 4, 3, 7, f[1]); rect(ctx, 7, 3, 2, 11, gold[2]); rect(ctx, 6, 2, 4, 2, '#05020c'); break; }
    case 'ring': ellipse(ctx, 8, 10, 4, 4, gold[3]); ellipse(ctx, 8, 10, 2, 2, '#05020c'); { const g = ramp('#4af0ff', 5); rect(ctx, 6, 3, 4, 4, g[3]); px(ctx, 6, 3, '#fff'); } break;
    case 'amulet': { line(3, 2, 8, 9, gold[2]); line(13, 2, 8, 9, gold[2]); const g = ramp('#ff4a6a', 5); shadedEllipse(ctx, 8, 11, 3, 3, g); px(ctx, 7, 10, '#fff'); break; }
    case 'boots': { const f = ramp('#8a5a2a', 5); rect(ctx, 4, 2, 5, 9, f[2]); rect(ctx, 4, 9, 9, 4, f[2]); rect(ctx, 4, 12, 9, 1, f[0]); rect(ctx, 4, 2, 2, 9, f[3]); rect(ctx, 4, 2, 5, 1, gold[2]); break; }
    case 'star': { for (let i = 0; i < 10; i++) { const a = -Math.PI / 2 + i * Math.PI / 5, r = i % 2 ? 3 : 7; line(8, 8, Math.round(8 + r * Math.cos(a)), Math.round(8 + r * Math.sin(a)), gold[3]); } px(ctx, 8, 8, '#fff'); break; }
    case 'scroll': rect(ctx, 3, 3, 10, 10, '#f2e4c8'); rect(ctx, 3, 3, 10, 1, '#d8c8a0'); rect(ctx, 2, 2, 12, 2, '#c0a070'); rect(ctx, 2, 12, 12, 2, '#c0a070'); for (let y = 5; y < 12; y += 2) rect(ctx, 5, y, 6, 1, '#8a6a4a'); break;
    case 'crystal': { const f = ramp('#66e6ff', 5); for (let y = 0; y < 14; y++) { const w = Math.round(5 * (1 - Math.abs(y - 6) / 8)); rect(ctx, 8 - w, 1 + y, w, 1, f[3]); rect(ctx, 8, 1 + y, w, 1, f[2]); } rect(ctx, 6, 4, 1, 4, '#fff'); break; }
    case 'fang': { rect(ctx, 6, 2, 5, 3, '#f2e8d8'); for (let y = 0; y < 9; y++) rect(ctx, 7 + (y > 4 ? 1 : 0), 5 + y, Math.max(1, 4 - Math.floor(y / 2)), 1, y % 2 ? '#d8c8b0' : '#fff6e8'); break; }
    case 'core': shadedEllipse(ctx, 8, 8, 5, 5, ramp('#58e08a', 5)); px(ctx, 6, 6, '#fff'); px(ctx, 7, 6, '#ffffffaa'); break;
    case 'cloth': { rect(ctx, 3, 4, 10, 8, '#e8e4f0'); for (let x = 3; x < 13; x += 2) px(ctx, x, 4, '#c8c4d8'); for (let y = 6; y < 12; y += 3) rect(ctx, 3, y, 10, 1, '#d0ccdc'); break; }
    case 'bow': { for (let i = 0; i < 14; i++) px(ctx, 4 + Math.round(4 * Math.sin(i / 13 * Math.PI)), 1 + i, wood[3]); line(4, 1, 4, 14, '#e8e8f8'); line(5, 8, 13, 8, steel[3]); px(ctx, 14, 8, steel[4]); break; }
    case 'staff': { line(3, 14, 11, 6, wood[2]); const f = ramp('#b48cff', 5); shadedEllipse(ctx, 12, 4, 3, 3, f); px(ctx, 11, 3, '#fff'); break; }
    case 'axe': { line(3, 14, 11, 4, wood[2]); const f = steel; rect(ctx, 8, 2, 6, 6, f[2]); rect(ctx, 8, 2, 6, 2, f[4]); rect(ctx, 12, 3, 3, 4, f[3]); break; }
    case 'lock': rect(ctx, 4, 7, 8, 7, gold[2]); rect(ctx, 5, 3, 2, 5, steel[2]); rect(ctx, 9, 3, 2, 5, steel[2]); rect(ctx, 5, 2, 6, 2, steel[3]); rect(ctx, 7, 9, 2, 3, '#05020c'); break;
    case 'book': { rect(ctx, 2, 2, 12, 12, '#6a4aa8'); rect(ctx, 2, 2, 12, 2, '#8a6ad0'); rect(ctx, 4, 4, 9, 9, '#f2e4c8'); for (let y = 6; y < 12; y += 2) rect(ctx, 5, y, 6, 1, '#8a6a4a'); break; }
    default: rect(ctx, 4, 4, 8, 8, '#888'); px(ctx, 8, 8, '#fff');
  }
}

export function icon(id: string): HTMLCanvasElement {
  let c = cache.get(id);
  if (!c) {
    const [cv, ctx] = mk(18, 18);
    const [inner, ictx] = mk(16, 16);
    paint(id, ictx);
    ctx.drawImage(inner, 1, 1);
    c = outline(cv);
    cache.set(id, c);
  }
  return c;
}
