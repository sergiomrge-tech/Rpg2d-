import { Ctx, mk, px, rect, ramp, mix, outline, ellipse, shadedEllipse } from './pixel';
import { Rng } from '../engine/util';

export const TS = 16;

export const T = {
  GRASS: 0, GRASS2: 1, FLOWER: 2, DIRT: 3, STONE: 4, WATER: 5, SAND: 6, CAVE: 7, WOOD: 8, BRIDGE: 9,
  WALL: 10, DEEP: 11, DGRASS: 12, MOSS: 13, CRYSTAL: 14, RUG: 15, COBBLE: 16, VOID: 17, ICEFLOOR: 18, DARKSTONE: 19, DSAND: 20, DCOBBLE: 21, ADOBE: 22, SNOW: 23, DWOOD: 24,
} as const;

export interface TileInfo { solid: boolean; rank: number; anim?: boolean; variants: number }
export const TILE_INFO: Record<number, TileInfo> = {
  [T.GRASS]: { solid: false, rank: 5, variants: 4 },
  [T.GRASS2]: { solid: false, rank: 5, variants: 4 },
  [T.FLOWER]: { solid: false, rank: 5, variants: 4 },
  [T.DIRT]: { solid: false, rank: 3, variants: 4 },
  [T.STONE]: { solid: false, rank: 4, variants: 4 },
  [T.WATER]: { solid: true, rank: 1, anim: true, variants: 1 },
  [T.SAND]: { solid: false, rank: 2, variants: 4 },
  [T.CAVE]: { solid: false, rank: 4, variants: 4 },
  [T.WOOD]: { solid: false, rank: 4, variants: 2 },
  [T.BRIDGE]: { solid: false, rank: 4, variants: 1 },
  [T.WALL]: { solid: true, rank: 9, variants: 4 },
  [T.DEEP]: { solid: true, rank: 0, anim: true, variants: 1 },
  [T.DGRASS]: { solid: false, rank: 5, variants: 4 },
  [T.MOSS]: { solid: false, rank: 5, variants: 4 },
  [T.CRYSTAL]: { solid: false, rank: 4, variants: 4 },
  [T.RUG]: { solid: false, rank: 6, variants: 1 },
  [T.COBBLE]: { solid: false, rank: 4, variants: 4 },
  [T.VOID]: { solid: true, rank: 9, variants: 1 },
  [T.ICEFLOOR]: { solid: false, rank: 4, variants: 4 },
  [T.DARKSTONE]: { solid: false, rank: 4, variants: 4 },
  [T.DSAND]: { solid: false, rank: 2, variants: 4 },
  [T.DCOBBLE]: { solid: false, rank: 4, variants: 4 },
  [T.ADOBE]: { solid: false, rank: 4, variants: 2 },
  [T.SNOW]: { solid: false, rank: 5, variants: 4 },
  [T.DWOOD]: { solid: true, rank: 9, variants: 4 },
};

export const TILE_BASE: Record<number, string> = {
  [T.GRASS]: '#58a84e', [T.GRASS2]: '#4c9a48', [T.FLOWER]: '#58a84e', [T.DIRT]: '#b98d5c', [T.STONE]: '#9a9aa8',
  [T.WATER]: '#3d86d8', [T.SAND]: '#e6d29a', [T.CAVE]: '#463e60', [T.WOOD]: '#a8693a', [T.BRIDGE]: '#9a6a3a',
  [T.WALL]: '#272036', [T.DEEP]: '#2a64bc', [T.DGRASS]: '#2f7a4a', [T.MOSS]: '#3f7a6a', [T.CRYSTAL]: '#463e60',
  [T.RUG]: '#b8323f', [T.COBBLE]: '#8c8a98', [T.VOID]: '#05020c', [T.ICEFLOOR]: '#a8d4f0', [T.DARKSTONE]: '#3a3550', [T.DSAND]: '#e8c56e', [T.DCOBBLE]: '#a89878', [T.ADOBE]: '#c98a58', [T.SNOW]: '#e8f0fa', [T.DWOOD]: '#4a3020',
};

const cache = new Map<string, HTMLCanvasElement>();

function speckle(ctx: Ctx, r: Rng, n: number, cols: string[], size = 1) {
  for (let i = 0; i < n; i++) rect(ctx, r.int(0, TS - size), r.int(0, TS - size), size, size, r.pick(cols));
}

function paintTile(id: number, v: number, f: number): HTMLCanvasElement {
  const [c, ctx] = mk(TS, TS);
  const r = new Rng(id * 977 + v * 131 + 7);
  const base = TILE_BASE[id];
  const rp = ramp(base, 5);
  rect(ctx, 0, 0, TS, TS, rp[2]);
  switch (id) {
    case T.GRASS: case T.GRASS2: case T.FLOWER: case T.DGRASS: case T.MOSS: {
      speckle(ctx, r, 22, [rp[1], rp[3]], 1);
      for (let i = 0; i < 5; i++) {
        const x = r.int(1, 14), y = r.int(2, 14);
        px(ctx, x, y, rp[0]); px(ctx, x, y - 1, rp[3]); px(ctx, x + 1, y - 1, rp[4]);
      }
      if (id === T.FLOWER) {
        const cols = r.pick([['#ffffff', '#ffe066'], ['#ff8fab', '#ffe066'], ['#b39dff', '#fff'], ['#ffd166', '#fff']]);
        for (let i = 0; i < 3; i++) {
          const x = r.int(2, 12), y = r.int(3, 12);
          px(ctx, x, y, cols[0]); px(ctx, x + 1, y, cols[0]); px(ctx, x, y + 1, cols[0]); px(ctx, x + 1, y + 1, cols[1]);
          px(ctx, x, y + 2, rp[0]);
        }
      }
      if (id === T.MOSS) speckle(ctx, r, 6, ['#6fd1b0'], 1);
      break;
    }
    case T.DIRT: {
      speckle(ctx, r, 26, [rp[1], rp[3]], 1);
      for (let i = 0; i < 3; i++) { const x = r.int(1, 13), y = r.int(1, 13); rect(ctx, x, y, 2, 1, rp[4]); rect(ctx, x + 1, y + 1, 2, 1, rp[1]); }
      break;
    }
    case T.SAND: speckle(ctx, r, 24, [rp[1], rp[3], rp[4]], 1); break;
    case T.DSAND: {
      speckle(ctx, r, 30, [rp[1], rp[3], rp[4]], 1);
      // wind ripples
      for (let i = 0; i < 3; i++) {
        const y = 3 + i * 5 + (v % 2), x = r.int(0, 5);
        rect(ctx, x, y, 7, 1, rp[1]); rect(ctx, x + 2, y + 1, 7, 1, rp[3]); rect(ctx, x + 8, y, 3, 1, rp[1]);
      }
      if (v === 3) { rect(ctx, 5, 9, 3, 2, '#9a8a7a'); px(ctx, 5, 9, '#c0b0a0'); }
      break;
    }
    case T.SNOW: speckle(ctx, r, 18, [rp[3], rp[4], '#cfe0f4'], 1); for (let i = 0; i < 2; i++) { const x = r.int(1, 11), y = r.int(2, 13); rect(ctx, x, y, 4, 1, '#ffffff'); rect(ctx, x, y + 1, 4, 1, '#b8cde8'); } break;
    case T.ADOBE: {
      rect(ctx, 0, 0, TS, TS, rp[2]);
      for (let y = 0; y < TS; y += 8) { rect(ctx, 0, y + 7, TS, 1, rp[1]); for (let x = (y % 16 ? 0 : 8); x < TS; x += 16) rect(ctx, x, y, 1, 8, rp[1]); }
      speckle(ctx, r, 12, [rp[3], rp[1]], 1);
      break;
    }
    case T.STONE: case T.COBBLE: case T.DARKSTONE: case T.DCOBBLE: {
      const bh = 8;
      for (let by = 0; by < 2; by++) {
        const off = by % 2 ? 4 : 0;
        for (let bx = -1; bx < 3; bx++) {
          const x0 = bx * 8 + off, y0 = by * bh;
          const sh = r.int(1, 3);
          rect(ctx, x0 + 1, y0 + 1, 7, 7, rp[sh]);
          rect(ctx, x0 + 1, y0 + 1, 7, 1, rp[Math.min(4, sh + 1)]);
          rect(ctx, x0, y0, 1, 8, rp[0]);
          rect(ctx, x0, y0 + 7, 8, 1, rp[0]);
        }
      }
      break;
    }
    case T.WATER: case T.DEEP: {
      const w = ramp(base, 5);
      rect(ctx, 0, 0, TS, TS, w[2]);
      for (let y = 0; y < TS; y++) {
        const k = Math.sin((y + f * 4) * 0.8 + v) ;
        if (k > 0.6) rect(ctx, (y * 5 + f * 3) % 12, y, 4, 1, w[3]);
      }
      for (let i = 0; i < 3; i++) {
        const x = (i * 6 + f * 4 + 2) % 15, y = (i * 5 + 3 + f * 2) % 15;
        rect(ctx, x, y, 3, 1, w[4]);
        px(ctx, x + 1, y + 1, w[3]);
      }
      if (id === T.DEEP) { rect(ctx, 0, 0, TS, TS, 'rgba(0,10,50,.18)'); }
      break;
    }
    case T.CAVE: case T.CRYSTAL: {
      speckle(ctx, r, 18, [rp[1], rp[3]], 1);
      for (let i = 0; i < 2; i++) { const x = r.int(1, 12), y = r.int(1, 12); rect(ctx, x, y, 3, 2, rp[3]); rect(ctx, x, y + 1, 3, 1, rp[1]); }
      if (id === T.CRYSTAL) {
        const cc = ramp('#66e6ff', 5);
        for (let i = 0; i < 2; i++) {
          const x = r.int(2, 12), y = r.int(5, 13);
          rect(ctx, x, y - 3, 2, 4, cc[3]); px(ctx, x, y - 4, cc[4]); px(ctx, x + 1, y, cc[1]);
        }
      }
      break;
    }
    case T.ICEFLOOR: speckle(ctx, r, 14, [rp[3], rp[4], rp[1]], 1); for (let i = 0; i < 2; i++) rect(ctx, r.int(0, 10), r.int(0, 14), 5, 1, '#ffffff66'); break;
    case T.WOOD: {
      for (let y = 0; y < TS; y += 4) {
        rect(ctx, 0, y, TS, 3, rp[v % 2 ? 2 : 3]);
        rect(ctx, 0, y + 3, TS, 1, rp[0]);
        rect(ctx, (y * 3 + v * 5) % 12, y, 1, 3, rp[1]);
      }
      break;
    }
    case T.BRIDGE: {
      for (let y = 0; y < TS; y += 4) { rect(ctx, 0, y, TS, 3, rp[2]); rect(ctx, 0, y + 3, TS, 1, rp[0]); rect(ctx, 0, y, TS, 1, rp[3]); px(ctx, (y * 3) % 14 + 1, y + 1, rp[0]); }
      break;
    }
    case T.RUG: {
      rect(ctx, 0, 0, TS, TS, rp[2]);
      rect(ctx, 0, 0, TS, 1, '#f2c94c'); rect(ctx, 0, TS - 1, TS, 1, '#f2c94c');
      for (let i = 0; i < 4; i++) px(ctx, 3 + i * 4, 8, rp[3]);
      break;
    }
    case T.WALL: {
      // rock top
      speckle(ctx, r, 20, [rp[1], rp[3]], 1);
      rect(ctx, 0, 0, TS, TS, 'rgba(0,0,0,0.0)');
      for (let i = 0; i < 3; i++) { const x = r.int(0, 11), y = r.int(0, 12); rect(ctx, x, y, 4, 2, rp[3]); rect(ctx, x, y + 2, 4, 1, rp[1]); }
      break;
    }
    case T.DWOOD: {
      for (let x = 0; x < TS; x += 4) { rect(ctx, x, 0, 3, TS, rp[v % 2 ? 2 : 1]); rect(ctx, x + 3, 0, 1, TS, rp[0]); }
      for (let i = 0; i < 5; i++) px(ctx, r.int(0, 15), r.int(0, 15), rp[3]);
      rect(ctx, 0, 0, TS, 2, rp[3]);
      break;
    }
    case T.VOID: rect(ctx, 0, 0, TS, TS, '#05020c'); break;
  }
  return c;
}

export function tileCanvas(id: number, v = 0, frame = 0): HTMLCanvasElement {
  const info = TILE_INFO[id];
  const vv = v % (info?.variants ?? 1);
  const ff = info?.anim ? frame % 4 : 0;
  const k = `${id}:${vv}:${ff}`;
  let c = cache.get(k);
  if (!c) { c = paintTile(id, vv, ff); cache.set(k, c); }
  return c;
}

/** Brick face for wall tiles directly above walkable floor. */
export function wallFace(variant: number, kind: 'cave' | 'house' | 'ice' = 'cave'): HTMLCanvasElement {
  const k = `face:${kind}:${variant % 4}`;
  let c = cache.get(k);
  if (c) return c;
  const [cv, ctx] = mk(TS, TS);
  const base = kind === 'ice' ? '#7fb6dc' : kind === 'house' ? '#a8805a' : '#3e3556';
  const rp = ramp(base, 5);
  const r = new Rng(variant * 31 + 5);
  rect(ctx, 0, 0, TS, TS, rp[2]);
  rect(ctx, 0, 0, TS, 3, rp[4]);
  rect(ctx, 0, 3, TS, 1, rp[3]);
  for (let y = 4; y < TS; y += 4) {
    rect(ctx, 0, y + 3, TS, 1, rp[0]);
    const off = (y / 4) % 2 ? 4 : 0;
    for (let x = off; x < TS + 8; x += 8) rect(ctx, x, y, 1, 3, rp[0]);
  }
  for (let i = 0; i < 8; i++) px(ctx, r.int(0, 15), r.int(4, 15), r.pick([rp[1], rp[3]]));
  rect(ctx, 0, TS - 3, TS, 3, rp[1]);
  rect(ctx, 0, TS - 1, TS, 1, rp[0]);
  cache.set(k, cv);
  return cv;
}

// ---------------- Objects ----------------
export interface ObjDef {
  w: number; h: number;       // pixel size
  ox: number; oy: number;     // offset of sprite relative to (tx*16, (ty+1)*16 - h)
  solid: [number, number][];  // footprint cells relative to (tx,ty)
  frames: number;
  draw: (f: number, v: number) => HTMLCanvasElement;
  light?: { r: number; color: string; flicker?: boolean; dy?: number };
  sortOffset?: number;
}

const objCache = new Map<string, HTMLCanvasElement>();
function memo(key: string, fn: () => HTMLCanvasElement): HTMLCanvasElement {
  let c = objCache.get(key);
  if (!c) { c = fn(); objCache.set(key, c); }
  return c;
}

function treeSprite(kind: string, v: number): HTMLCanvasElement {
  const [c, ctx] = mk(32, 48);
  const r = new Rng(v * 17 + 3);
  const trunk = ramp(kind === 'dead' ? '#6b5a50' : '#7a4a2a', 4);
  // shadow
  ctx.fillStyle = 'rgba(0,0,0,.22)'; ctx.beginPath(); ctx.ellipse(16, 44, 11, 4, 0, 0, 7); ctx.fill();
  rect(ctx, 14, 30, 5, 16, trunk[2]); rect(ctx, 14, 30, 2, 16, trunk[3]); rect(ctx, 18, 30, 1, 16, trunk[1]);
  rect(ctx, 12, 43, 9, 3, trunk[2]); rect(ctx, 12, 43, 3, 3, trunk[3]);
  if (kind === 'pine') {
    const g = ramp('#2a7a4e', 5);
    for (let i = 0; i < 4; i++) {
      const y = 28 - i * 7, w = 7 + (3 - i) * 3 + 1;
      for (let yy = 0; yy < 9; yy++) {
        const ww = Math.round(w * (0.35 + yy / 9 * 0.65));
        rect(ctx, 16 - ww, y + yy - 2, ww * 2, 1, yy < 3 ? g[3] : yy < 6 ? g[2] : g[1]);
        if (yy > 2) { px(ctx, 16 - ww + 1, y + yy - 2, g[3]); }
      }
    }
  } else if (kind === 'dead') {
    rect(ctx, 10, 14, 2, 18, trunk[2]); rect(ctx, 20, 8, 2, 22, trunk[1]); rect(ctx, 8, 14, 6, 2, trunk[2]); rect(ctx, 20, 8, 6, 2, trunk[2]); rect(ctx, 14, 4, 2, 28, trunk[2]);
  } else {
    const g = ramp(kind === 'crystal' ? '#4a9ec4' : kind === 'autumn' ? '#d9772e' : '#3f9a4a', 5);
    shadedEllipse(ctx, 9, 24, 9, 8, g, { lx: -0.6, ly: -0.5 });
    shadedEllipse(ctx, 23, 24, 9, 8, g, { lx: -0.6, ly: -0.5 });
    shadedEllipse(ctx, 16, 15, 13, 12, g, { lx: -0.5, ly: -0.7 });
    for (let i = 0; i < 14; i++) { const x = r.int(5, 26), y = r.int(6, 28); px(ctx, x, y, g[4]); px(ctx, x + 1, y + 1, g[1]); }
    if (kind === 'fruit') for (let i = 0; i < 5; i++) { const x = r.int(7, 24), y = r.int(10, 26); px(ctx, x, y, '#ff4d6d'); px(ctx, x, y + 1, '#c9184a'); }
  }
  return outline(c);
}

function houseSprite(wTiles: number, roofC: string, wallC: string, v: number): HTMLCanvasElement {
  const W = wTiles * 16, H = 80;
  const [c, ctx] = mk(W + 8, H + 8);
  const roof = ramp(roofC, 5), wall = ramp(wallC, 5), wood = ramp('#6a4a2a', 4);
  const x0 = 4;
  const roofTop = 4, roofBot = 40;
  // wall
  rect(ctx, x0, 40, W, 40, wall[3]);
  for (let y = 40; y < 80; y += 2) { if ((y / 2) % 2) rect(ctx, x0, y, W, 1, wall[2]); }
  rect(ctx, x0, 40, W, 3, wall[1]);
  // timber frame
  rect(ctx, x0, 40, 3, 40, wood[2]); rect(ctx, x0 + W - 3, 40, 3, 40, wood[1]);
  rect(ctx, x0, 76, W, 4, '#6e6a78'); rect(ctx, x0, 76, W, 1, '#9a96a8');
  rect(ctx, x0, 58, W, 2, wood[2]);
  // door
  const dx = x0 + Math.floor(wTiles / 2) * 16;
  rect(ctx, dx, 56, 16, 24, wood[0]);
  rect(ctx, dx + 1, 57, 14, 23, wood[2]);
  for (let i = 0; i < 4; i++) rect(ctx, dx + 3 + i * 3, 58, 1, 22, wood[1]);
  rect(ctx, dx + 11, 69, 2, 2, '#f2c94c');
  rect(ctx, dx - 1, 55, 18, 2, wood[3]);
  // windows
  const win = (wx: number) => {
    rect(ctx, wx, 47, 12, 10, wood[3]); rect(ctx, wx + 1, 48, 10, 8, '#ffe9a0'); rect(ctx, wx + 1, 48, 10, 3, '#fff6cf');
    rect(ctx, wx + 5, 48, 1, 8, wood[2]); rect(ctx, wx + 1, 52, 10, 1, wood[2]);
    rect(ctx, wx - 1, 57, 14, 2, wood[2]);
    for (let i = 0; i < 3; i++) px(ctx, wx + 1 + i * 4, 58, ['#ff6f91', '#ffd166', '#ff6f91'][i]);
  };
  if (wTiles >= 4) { win(x0 + 8); win(x0 + W - 20); } else win(x0 + 3);
  // roof
  for (let y = roofTop; y < roofBot; y++) {
    const t = (y - roofTop) / (roofBot - roofTop);
    const inset = Math.round((1 - t) * (W / 2 - 8));
    const row = Math.floor((y - roofTop) / 5);
    rect(ctx, x0 - 4 + inset, y, W + 8 - inset * 2, 1, row % 2 ? roof[2] : roof[3]);
    if ((y - roofTop) % 5 === 4) rect(ctx, x0 - 4 + inset, y, W + 8 - inset * 2, 1, roof[0]);
    for (let x = x0 - 4 + inset + ((row % 2) * 4); x < x0 + W + 4 - inset; x += 8) px(ctx, x, y, roof[1]);
  }
  rect(ctx, x0 - 4, roofBot - 2, W + 8, 2, roof[0]);
  rect(ctx, x0 - 4, roofBot, W + 8, 3, 'rgba(0,0,0,.28)');
  // chimney
  if (v % 2 === 0) { rect(ctx, x0 + W - 18, 0, 8, 18, '#8a7a8a'); rect(ctx, x0 + W - 19, 0, 10, 3, '#a89aa8'); }
  return outline(c);
}

function chestSprite(open: boolean): HTMLCanvasElement {
  const [c, ctx] = mk(16, 16);
  const w = ramp('#9a5a2a', 4), g = ramp('#f2c94c', 4);
  rect(ctx, 2, 6, 12, 8, w[2]); rect(ctx, 2, 6, 12, 2, w[3]); rect(ctx, 2, 13, 12, 1, w[0]);
  rect(ctx, 2, 6, 1, 8, g[2]); rect(ctx, 13, 6, 1, 8, g[1]); rect(ctx, 2, 9, 12, 1, g[2]);
  if (!open) { rect(ctx, 2, 3, 12, 4, w[3]); rect(ctx, 3, 2, 10, 1, w[3]); rect(ctx, 2, 3, 12, 1, g[3]); rect(ctx, 7, 8, 2, 3, g[3]); px(ctx, 8, 9, '#6a4a1a'); }
  else { rect(ctx, 2, 1, 12, 3, w[1]); rect(ctx, 3, 4, 10, 2, '#1a0f10'); rect(ctx, 4, 4, 8, 1, g[3]); px(ctx, 6, 3, '#fff'); }
  return outline(c);
}

function barrel(): HTMLCanvasElement {
  const [c, ctx] = mk(16, 18); const w = ramp('#a8693a', 4);
  ellipse(ctx, 8, 9, 6, 7, w[2]); rect(ctx, 3, 4, 10, 10, w[2]); rect(ctx, 3, 4, 3, 10, w[3]); rect(ctx, 11, 4, 2, 10, w[1]);
  rect(ctx, 3, 6, 10, 1, '#6e6a78'); rect(ctx, 3, 12, 10, 1, '#6e6a78'); rect(ctx, 4, 3, 8, 1, w[3]);
  return outline(c);
}
function crate(): HTMLCanvasElement {
  const [c, ctx] = mk(16, 16); const w = ramp('#b8864a', 4);
  rect(ctx, 1, 2, 14, 13, w[2]); rect(ctx, 1, 2, 14, 2, w[3]); rect(ctx, 1, 13, 14, 2, w[1]);
  rect(ctx, 1, 2, 2, 13, w[0]); rect(ctx, 13, 2, 2, 13, w[0]);
  for (let i = 0; i < 12; i++) px(ctx, 3 + i, 3 + i, w[0]);
  return outline(c);
}
function rockSprite(v: number, tone = '#8a8a9a'): HTMLCanvasElement {
  const [c, ctx] = mk(20, 18); const g = ramp(tone, 5);
  shadedEllipse(ctx, 10, 11, 8 - v % 2, 6, g, { lx: -0.5, ly: -0.7 });
  px(ctx, 6, 7, g[4]); px(ctx, 7, 6, g[4]);
  ctx.fillStyle = 'rgba(0,0,0,.2)'; ctx.fillRect(3, 16, 14, 1);
  return outline(c);
}
function bush(v: number, tone = '#3f9a4a'): HTMLCanvasElement {
  const [c, ctx] = mk(20, 16); const g = ramp(tone, 5);
  shadedEllipse(ctx, 6, 10, 6, 5, g); shadedEllipse(ctx, 14, 10, 6, 5, g); shadedEllipse(ctx, 10, 7, 7, 6, g);
  if (v % 2) for (const [x, y] of [[5, 8], [11, 5], [15, 9]]) { px(ctx, x, y, '#ff6f91'); px(ctx, x + 1, y, '#ffd6e0'); }
  return outline(c);
}
function signpost(): HTMLCanvasElement {
  const [c, ctx] = mk(16, 20); const w = ramp('#a8693a', 4);
  rect(ctx, 7, 8, 2, 12, w[1]); rect(ctx, 1, 1, 14, 9, w[2]); rect(ctx, 1, 1, 14, 2, w[3]); rect(ctx, 1, 9, 14, 1, w[0]);
  rect(ctx, 3, 4, 10, 1, w[0]); rect(ctx, 3, 6, 7, 1, w[0]);
  return outline(c);
}
function fenceH(): HTMLCanvasElement {
  const [c, ctx] = mk(16, 16); const w = ramp('#b0814e', 4);
  rect(ctx, 0, 6, 16, 2, w[3]); rect(ctx, 0, 8, 16, 1, w[1]); rect(ctx, 0, 11, 16, 2, w[2]); rect(ctx, 0, 13, 16, 1, w[0]);
  rect(ctx, 1, 4, 3, 11, w[2]); rect(ctx, 1, 4, 1, 11, w[3]); rect(ctx, 12, 4, 3, 11, w[2]); rect(ctx, 12, 4, 1, 11, w[3]);
  return outline(c);
}
function well(): HTMLCanvasElement {
  const [c, ctx] = mk(32, 40); const s = ramp('#9a9aa8', 5), w = ramp('#7a4a2a', 4);
  rect(ctx, 6, 22, 20, 14, s[2]);
  for (let y = 22; y < 36; y += 4) { rect(ctx, 6, y + 3, 20, 1, s[0]); for (let x = 6 + (y % 8 ? 0 : 5); x < 26; x += 10) rect(ctx, x, y, 1, 4, s[0]); }
  rect(ctx, 6, 22, 20, 2, s[4]); rect(ctx, 8, 24, 16, 4, '#2a62b0'); rect(ctx, 8, 24, 16, 1, '#6aa8f0');
  rect(ctx, 6, 8, 2, 20, w[2]); rect(ctx, 24, 8, 2, 20, w[1]);
  rect(ctx, 4, 4, 24, 4, '#b8323f'); rect(ctx, 6, 2, 20, 3, '#d9485a'); rect(ctx, 4, 8, 24, 1, '#7a1a28');
  rect(ctx, 15, 8, 1, 10, w[0]); rect(ctx, 13, 17, 5, 4, w[2]);
  return outline(c);
}
function fountain(f: number): HTMLCanvasElement {
  const [c, ctx] = mk(48, 48); const s = ramp('#b8b8c8', 5);
  ctx.fillStyle = 'rgba(0,0,0,.2)'; ctx.beginPath(); ctx.ellipse(24, 40, 21, 6, 0, 0, 7); ctx.fill();
  shadedEllipse(ctx, 24, 32, 21, 11, s, { dither: false });
  ellipse(ctx, 24, 31, 17, 8, '#2f78d0'); ellipse(ctx, 24, 30, 15, 6, '#4a9af0');
  for (let i = 0; i < 6; i++) rect(ctx, 12 + ((i * 7 + f * 3) % 22), 28 + (i % 3) * 2, 4, 1, '#bfe4ff');
  rect(ctx, 21, 14, 6, 17, s[3]); rect(ctx, 21, 14, 2, 17, s[4]); rect(ctx, 18, 12, 12, 3, s[3]);
  const drop = ['#bfe4ff', '#e8f6ff'];
  for (let i = 0; i < 5; i++) { const t = (f * 2 + i * 2) % 10; px(ctx, 24 + Math.round((i - 2) * t * 0.5), 10 + t, drop[i % 2]); px(ctx, 24 - Math.round((i - 2) * t * 0.5), 10 + t, drop[(i + 1) % 2]); }
  rect(ctx, 23, 6, 2, 6, '#bfe4ff');
  return outline(c);
}
function torch(f: number): HTMLCanvasElement {
  const [c, ctx] = mk(16, 28); const w = ramp('#6a4a2a', 4), fl = ramp('#ff8a2a', 5);
  rect(ctx, 7, 12, 3, 14, w[2]); rect(ctx, 7, 12, 1, 14, w[3]); rect(ctx, 5, 10, 7, 3, '#6e6a78');
  const h = [6, 8, 7, 9][f % 4];
  ellipse(ctx, 8, 8, 3, h / 2 + 1, fl[2]); ellipse(ctx, 8, 8, 2, h / 2, fl[3]); ellipse(ctx, 8, 9, 1, h / 3, fl[4]);
  px(ctx, 8 + (f % 2 ? 1 : -1), 8 - h / 2 - 1, fl[3]);
  return outline(c);
}
function campfire(f: number): HTMLCanvasElement {
  const [c, ctx] = mk(20, 20); const w = ramp('#6a4a2a', 4), fl = ramp('#ff8a2a', 5);
  rect(ctx, 3, 15, 14, 3, w[1]); rect(ctx, 5, 14, 10, 2, w[2]);
  const h = [8, 10, 9, 11][f % 4];
  ellipse(ctx, 10, 12, 5, h / 2 + 2, fl[1]); ellipse(ctx, 10, 12, 4, h / 2 + 1, fl[2]); ellipse(ctx, 10, 12, 2, h / 2, fl[3]); ellipse(ctx, 10, 13, 1, h / 3, fl[4]);
  return outline(c);
}
function lamp(f: number): HTMLCanvasElement {
  const [c, ctx] = mk(12, 36);
  rect(ctx, 5, 10, 2, 24, '#4a4a58'); rect(ctx, 3, 32, 6, 3, '#3a3a48'); rect(ctx, 3, 4, 6, 7, '#ffe9a0'); rect(ctx, 4, 5, 4, 5, f % 2 ? '#fff6cf' : '#ffd86a');
  rect(ctx, 2, 3, 8, 2, '#4a4a58'); rect(ctx, 2, 10, 8, 2, '#4a4a58');
  return outline(c);
}
function crystalCluster(v: number, f: number, col = '#66e6ff'): HTMLCanvasElement {
  const [c, ctx] = mk(24, 32); const g = ramp(col, 5);
  const shards: [number, number, number, number][] = [[12, 28, 5, 22], [6, 29, 4, 14], [18, 29, 4, 16], [9, 26, 3, 10 + v % 3 * 2]];
  for (const [x, y, w, h] of shards) {
    for (let yy = 0; yy < h; yy++) {
      const ww = Math.max(1, Math.round(w * (0.3 + 0.7 * Math.min(1, yy / (h * 0.45)))));
      rect(ctx, x - ww, y - h + yy, ww, 1, g[3]); rect(ctx, x, y - h + yy, ww, 1, g[1]);
    }
    px(ctx, x - 1, y - h + 2, '#ffffff'); px(ctx, x - 1, y - h + 3, g[4]);
  }
  ctx.globalAlpha = 0.35 + 0.25 * Math.sin(f * 1.6);
  ellipse(ctx, 12, 26, 9, 4, g[3]);
  ctx.globalAlpha = 1;
  return outline(c);
}
function stalagmite(v: number): HTMLCanvasElement {
  const [c, ctx] = mk(20, 28); const g = ramp('#5a5270', 5);
  for (let y = 0; y < 22; y++) { const w = Math.round(2 + y * 0.38); rect(ctx, 10 - w, 4 + y, w, 1, g[y < 6 ? 3 : 2]); rect(ctx, 10, 4 + y, w, 1, g[y < 6 ? 2 : 1]); }
  rect(ctx, 2, 25, 16, 2, 'rgba(0,0,0,.25)');
  return outline(c);
}
function pillar(): HTMLCanvasElement {
  const [c, ctx] = mk(20, 48); const g = ramp('#8a86a0', 5);
  rect(ctx, 2, 40, 16, 6, g[1]); rect(ctx, 2, 40, 16, 2, g[3]); rect(ctx, 4, 6, 12, 36, g[2]); rect(ctx, 4, 6, 4, 36, g[3]); rect(ctx, 13, 6, 3, 36, g[1]);
  rect(ctx, 1, 2, 18, 5, g[3]); rect(ctx, 1, 6, 18, 1, g[0]);
  for (let y = 10; y < 38; y += 7) rect(ctx, 4, y, 12, 1, g[1]);
  return outline(c);
}
function saveCrystal(f: number): HTMLCanvasElement {
  const [c, ctx] = mk(24, 40); const g = ramp('#7ae8ff', 5), s = ramp('#9a9aa8', 4);
  rect(ctx, 4, 32, 16, 6, s[2]); rect(ctx, 4, 32, 16, 2, s[3]); rect(ctx, 6, 30, 12, 3, s[1]);
  const bob = Math.round(Math.sin(f * 1.5) * 1.5);
  const y0 = 4 + bob;
  for (let yy = 0; yy < 22; yy++) { const w = Math.round(7 * (1 - Math.abs(yy - 10) / 12)); rect(ctx, 12 - w, y0 + yy, w, 1, g[3]); rect(ctx, 12, y0 + yy, w, 1, g[2]); }
  rect(ctx, 9, y0 + 5, 1, 5, '#ffffff'); px(ctx, 10, y0 + 4, '#ffffff');
  ctx.globalAlpha = 0.3; ellipse(ctx, 12, y0 + 11, 11, 13, g[3]); ctx.globalAlpha = 1;
  return outline(c);
}
function stall(color: string): HTMLCanvasElement {
  const [c, ctx] = mk(48, 44); const w = ramp('#8a5a2a', 4);
  rect(ctx, 4, 14, 3, 28, w[1]); rect(ctx, 41, 14, 3, 28, w[1]);
  rect(ctx, 4, 30, 40, 12, w[2]); rect(ctx, 4, 30, 40, 2, w[3]); rect(ctx, 4, 41, 40, 2, w[0]);
  for (let i = 0; i < 6; i++) { const col = i % 2 ? '#ffffff' : color; rect(ctx, 2 + i * 7, 4, 7, 12, col); rect(ctx, 2 + i * 7, 16, 7, 2, col === '#ffffff' ? '#d8d8e8' : '#00000033'); }
  rect(ctx, 2, 3, 44, 2, '#00000022');
  for (const [x, col] of [[10, '#ff6f91'], [18, '#ffd166'], [26, '#7ae8a0'], [34, '#8ab4ff']] as [number, string][]) { ellipse(ctx, x, 28, 3, 3, col); }
  return outline(c);
}
function haystack(): HTMLCanvasElement {
  const [c, ctx] = mk(24, 22); const g = ramp('#e0b84a', 5);
  shadedEllipse(ctx, 12, 12, 10, 9, g); rect(ctx, 2, 16, 20, 5, g[1]);
  for (let i = 0; i < 8; i++) px(ctx, 4 + i * 2, 8 + (i % 3) * 3, g[0]);
  return outline(c);
}
function tombstone(): HTMLCanvasElement {
  const [c, ctx] = mk(16, 22); const g = ramp('#8a8aa0', 4);
  rect(ctx, 3, 6, 10, 15, g[2]); rect(ctx, 4, 4, 8, 2, g[2]); rect(ctx, 5, 3, 6, 1, g[3]); rect(ctx, 3, 6, 2, 15, g[3]);
  rect(ctx, 7, 8, 2, 6, g[0]); rect(ctx, 5, 10, 6, 2, g[0]);
  return outline(c);
}
function portal(f: number): HTMLCanvasElement {
  const [c, ctx] = mk(32, 40);
  const g = ramp('#a06cff', 5), st = ramp('#8a86a0', 4);
  rect(ctx, 0, 36, 32, 4, st[1]);
  rect(ctx, 2, 4, 5, 34, st[2]); rect(ctx, 25, 4, 5, 34, st[2]); rect(ctx, 2, 4, 2, 34, st[3]); rect(ctx, 0, 0, 32, 6, st[2]); rect(ctx, 0, 0, 32, 2, st[3]);
  for (let y = 6; y < 36; y++) for (let x = 7; x < 25; x++) {
    const k = Math.sin((x * 0.5 + f * 0.9) + Math.sin(y * 0.4 + f * 0.7) * 2);
    px(ctx, x, y, k > 0.4 ? g[4] : k > -0.2 ? g[3] : g[2]);
  }
  return outline(c);
}
function bed(): HTMLCanvasElement {
  const [c, ctx] = mk(24, 36); const w = ramp('#a8693a', 4);
  rect(ctx, 0, 2, 24, 34, w[1]); rect(ctx, 1, 4, 22, 30, '#e8e8f8'); rect(ctx, 1, 18, 22, 16, '#d9485a'); rect(ctx, 1, 18, 22, 2, '#ff7a8a');
  rect(ctx, 3, 5, 18, 8, '#fff'); rect(ctx, 3, 5, 18, 1, '#d8d8e8'); rect(ctx, 0, 0, 24, 4, w[2]);
  return outline(c);
}
function table(): HTMLCanvasElement {
  const [c, ctx] = mk(32, 24); const w = ramp('#a8693a', 4);
  rect(ctx, 2, 6, 28, 8, w[3]); rect(ctx, 2, 14, 28, 2, w[1]); rect(ctx, 4, 16, 3, 6, w[1]); rect(ctx, 25, 16, 3, 6, w[1]);
  rect(ctx, 6, 3, 4, 4, '#d9d9e8'); rect(ctx, 20, 4, 5, 3, '#e86a6a');
  return outline(c);
}
function bookshelf(): HTMLCanvasElement {
  const [c, ctx] = mk(32, 40); const w = ramp('#7a4a2a', 4);
  rect(ctx, 0, 0, 32, 40, w[1]); rect(ctx, 2, 2, 28, 36, w[0]);
  const cols = ['#d9485a', '#4a9af0', '#f2c94c', '#6fd1a0', '#a06cff', '#e8703a'];
  for (let sh = 0; sh < 3; sh++) { rect(ctx, 2, 12 + sh * 12, 28, 2, w[2]); for (let i = 0; i < 9; i++) rect(ctx, 3 + i * 3, 3 + sh * 12 + (i % 3), 2, 9 - (i % 3), cols[(i + sh) % 6]); }
  return outline(c);
}
function bannerSprite(color: string): HTMLCanvasElement {
  const [c, ctx] = mk(16, 32); const w = ramp('#6a4a2a', 3);
  rect(ctx, 0, 0, 16, 3, w[2]); rect(ctx, 2, 3, 12, 24, color); rect(ctx, 2, 3, 12, 2, '#ffffff44'); rect(ctx, 7, 27, 2, 3, color);
  rect(ctx, 5, 10, 6, 6, '#f2c94c'); rect(ctx, 7, 8, 2, 10, '#f2c94c');
  return outline(c);
}
function iceSpike(): HTMLCanvasElement { return crystalCluster(1, 0, '#a8e0ff'); }

export const OBJECTS: Record<string, ObjDef> = {
  tree: { w: 32, h: 48, ox: -8, oy: 0, solid: [[0, 0]], frames: 1, draw: (_f, v) => memo(`tree${v % 3}`, () => treeSprite('oak', v % 3)) },
  fruit_tree: { w: 32, h: 48, ox: -8, oy: 0, solid: [[0, 0]], frames: 1, draw: (_f, v) => memo(`ftree${v % 3}`, () => treeSprite('fruit', v % 3)) },
  autumn_tree: { w: 32, h: 48, ox: -8, oy: 0, solid: [[0, 0]], frames: 1, draw: (_f, v) => memo(`atree${v % 3}`, () => treeSprite('autumn', v % 3)) },
  pine: { w: 32, h: 48, ox: -8, oy: 0, solid: [[0, 0]], frames: 1, draw: (_f, v) => memo(`pine${v % 3}`, () => treeSprite('pine', v % 3)) },
  dead_tree: { w: 32, h: 48, ox: -8, oy: 0, solid: [[0, 0]], frames: 1, draw: (_f, v) => memo(`dead${v % 3}`, () => treeSprite('dead', v % 3)) },
  crystal_tree: { w: 32, h: 48, ox: -8, oy: 0, solid: [[0, 0]], frames: 1, draw: (_f, v) => memo(`ctree${v % 3}`, () => treeSprite('crystal', v % 3)) },
  bush: { w: 20, h: 16, ox: -2, oy: 0, solid: [[0, 0]], frames: 1, draw: (_f, v) => memo(`bush${v % 2}`, () => bush(v)) },
  rock: { w: 20, h: 18, ox: -2, oy: 0, solid: [[0, 0]], frames: 1, draw: (_f, v) => memo(`rock${v % 2}`, () => rockSprite(v)) },
  cave_rock: { w: 20, h: 18, ox: -2, oy: 0, solid: [[0, 0]], frames: 1, draw: (_f, v) => memo(`crock${v % 2}`, () => rockSprite(v, '#5a5270')) },
  barrel: { w: 16, h: 18, ox: 0, oy: 0, solid: [[0, 0]], frames: 1, draw: () => memo('barrel', barrel) },
  crate: { w: 16, h: 16, ox: 0, oy: 0, solid: [[0, 0]], frames: 1, draw: () => memo('crate', crate) },
  sign: { w: 16, h: 20, ox: 0, oy: 0, solid: [[0, 0]], frames: 1, draw: () => memo('sign', signpost) },
  fence: { w: 16, h: 16, ox: 0, oy: 0, solid: [[0, 0]], frames: 1, draw: () => memo('fence', fenceH) },
  well: { w: 32, h: 40, ox: 0, oy: 0, solid: [[0, 0], [1, 0]], frames: 1, draw: () => memo('well', well) },
  fountain: { w: 48, h: 48, ox: 0, oy: 0, solid: [[0, 0], [1, 0], [2, 0], [0, -1], [1, -1], [2, -1]], frames: 4, draw: (f) => memo(`fountain${f % 4}`, () => fountain(f)) },
  torch: { w: 16, h: 28, ox: 0, oy: 0, solid: [[0, 0]], frames: 4, draw: (f) => memo(`torch${f % 4}`, () => torch(f)), light: { r: 58, color: '#ff9a3a', flicker: true, dy: -18 } },
  campfire: { w: 20, h: 20, ox: -2, oy: 0, solid: [[0, 0]], frames: 4, draw: (f) => memo(`camp${f % 4}`, () => campfire(f)), light: { r: 70, color: '#ff8a2a', flicker: true, dy: -8 } },
  lamp: { w: 12, h: 36, ox: 2, oy: 0, solid: [[0, 0]], frames: 2, draw: (f) => memo(`lamp${f % 2}`, () => lamp(f)), light: { r: 52, color: '#ffe080', dy: -26 } },
  crystal: { w: 24, h: 32, ox: -4, oy: 0, solid: [[0, 0]], frames: 4, draw: (f, v) => memo(`cry${v % 3}_${f % 4}`, () => crystalCluster(v, f)), light: { r: 46, color: '#66e6ff', dy: -12 } },
  red_crystal: { w: 24, h: 32, ox: -4, oy: 0, solid: [[0, 0]], frames: 4, draw: (f, v) => memo(`rcry${v % 3}_${f % 4}`, () => crystalCluster(v, f, '#ff6a8a')), light: { r: 46, color: '#ff6a8a', dy: -12 } },
  ice_spike: { w: 24, h: 32, ox: -4, oy: 0, solid: [[0, 0]], frames: 1, draw: () => memo('ice', iceSpike) },
  stalagmite: { w: 20, h: 28, ox: -2, oy: 0, solid: [[0, 0]], frames: 1, draw: (_f, v) => memo(`stal${v}`, () => stalagmite(v)) },
  pillar: { w: 20, h: 48, ox: -2, oy: 0, solid: [[0, 0]], frames: 1, draw: () => memo('pillar', pillar) },
  save_crystal: { w: 24, h: 40, ox: -4, oy: 0, solid: [[0, 0]], frames: 8, draw: (f) => memo(`save${f % 8}`, () => saveCrystal(f)), light: { r: 60, color: '#7ae8ff', dy: -16 } },
  stall_red: { w: 48, h: 44, ox: 0, oy: 0, solid: [[0, 0], [1, 0], [2, 0]], frames: 1, draw: () => memo('stallr', () => stall('#d9485a')) },
  stall_blue: { w: 48, h: 44, ox: 0, oy: 0, solid: [[0, 0], [1, 0], [2, 0]], frames: 1, draw: () => memo('stallb', () => stall('#3a7bd5')) },
  haystack: { w: 24, h: 22, ox: -4, oy: 0, solid: [[0, 0]], frames: 1, draw: () => memo('hay', haystack) },
  tombstone: { w: 16, h: 22, ox: 0, oy: 0, solid: [[0, 0]], frames: 1, draw: () => memo('tomb', tombstone) },
  portal: { w: 32, h: 40, ox: 0, oy: 0, solid: [], frames: 8, draw: (f) => memo(`portal${f % 8}`, () => portal(f)), light: { r: 60, color: '#b48cff', dy: -16 } },
  bed: { w: 24, h: 36, ox: -4, oy: 0, solid: [[0, 0], [0, -1]], frames: 1, draw: () => memo('bed', bed) },
  table: { w: 32, h: 24, ox: 0, oy: 0, solid: [[0, 0], [1, 0]], frames: 1, draw: () => memo('table', table) },
  bookshelf: { w: 32, h: 40, ox: 0, oy: 0, solid: [[0, 0], [1, 0]], frames: 1, draw: () => memo('shelf', bookshelf) },
  banner_blue: { w: 16, h: 32, ox: 0, oy: 0, solid: [], frames: 1, draw: () => memo('banb', () => bannerSprite('#3a7bd5')) },
  banner_red: { w: 16, h: 32, ox: 0, oy: 0, solid: [], frames: 1, draw: () => memo('banr', () => bannerSprite('#c9283a')) },
};

export function houseDef(wTiles: number): ObjDef {
  const solid: [number, number][] = [];
  for (let y = -4; y <= 0; y++) for (let x = 0; x < wTiles; x++) solid.push([x, y]);
  return { w: wTiles * 16 + 8, h: 88, ox: -4, oy: 0, solid, frames: 1, draw: (_f, v) => memo(`house${wTiles}_${v}`, () => houseSprite(wTiles, ['#c9483a', '#3a7bd5', '#8a5ad0', '#d9922e'][v % 4], ['#f2e4c8', '#e8d8b8', '#dcdcf0'][v % 3], v)) };
}

export function chestCanvas(open: boolean) { return memo(open ? 'chest_o' : 'chest_c', () => chestSprite(open)); }

// ---------- Extra props: desert, village clutter ----------
function cactus(v: number): HTMLCanvasElement {
  const [c, ctx] = mk(20, 32); const g = ramp('#4aa850', 5);
  rect(ctx, 8, 6, 5, 24, g[2]); rect(ctx, 8, 6, 2, 24, g[3]); rect(ctx, 12, 6, 1, 24, g[1]); rect(ctx, 9, 4, 3, 2, g[3]);
  if (v % 2 === 0) { rect(ctx, 3, 14, 5, 3, g[2]); rect(ctx, 3, 9, 3, 6, g[2]); rect(ctx, 3, 9, 1, 6, g[3]); }
  rect(ctx, 13, 18, 4, 3, g[2]); rect(ctx, 15, 12, 3, 7, g[2]); rect(ctx, 17, 12, 1, 7, g[1]);
  for (let y = 8; y < 28; y += 3) px(ctx, 10, y, g[0]);
  for (const [x, y] of [[9, 3], [13, 11], [4, 8], [16, 11]]) px(ctx, x, y, v % 3 === 0 ? '#ff6f91' : '#fff2b0');
  ctx.fillStyle = 'rgba(0,0,0,.2)'; ctx.fillRect(5, 30, 11, 2);
  return outline(c);
}
function jar(v: number): HTMLCanvasElement {
  const [c, ctx] = mk(16, 20);
  const g = ramp(['#c0643a', '#4a8ac0', '#a8693a', '#7a9a5a'][v % 4], 5);
  shadedEllipse(ctx, 8, 12, 6, 6, g, { dither: false });
  rect(ctx, 5, 4, 6, 4, g[2]); rect(ctx, 5, 4, 2, 4, g[3]); rect(ctx, 4, 3, 8, 2, g[1]);
  rect(ctx, 4, 11, 8, 1, g[0]); for (let i = 0; i < 4; i++) px(ctx, 4 + i * 2, 12, g[4]);
  return outline(c);
}
function potPlant(v: number): HTMLCanvasElement {
  const [c, ctx] = mk(16, 20); const t = ramp('#c0643a', 4), g = ramp(['#4aa850', '#6fd1a0', '#3f9a4a'][v % 3], 5);
  rect(ctx, 4, 12, 8, 7, t[2]); rect(ctx, 4, 12, 8, 1, t[3]); rect(ctx, 5, 18, 6, 1, t[0]); rect(ctx, 4, 12, 2, 7, t[3]);
  shadedEllipse(ctx, 8, 8, 6, 5, g);
  for (const [x, y] of [[5, 6], [10, 5], [8, 3]]) px(ctx, x, y, ['#ff6f91', '#ffd166', '#fff'][(x + v) % 3]);
  return outline(c);
}
function tent(color: string): HTMLCanvasElement {
  const [c, ctx] = mk(56, 48); const g = ramp(color, 5), w = ramp('#6a4a2a', 4);
  for (let y = 0; y < 40; y++) {
    const half = Math.round(4 + y * 0.62);
    rect(ctx, 28 - half, 4 + y, half, 1, g[y % 9 < 1 ? 1 : 3]);
    rect(ctx, 28, 4 + y, half, 1, g[y % 9 < 1 ? 0 : 2]);
  }
  rect(ctx, 24, 24, 9, 20, '#2a1a22'); rect(ctx, 25, 23, 7, 3, '#2a1a22');
  rect(ctx, 22, 22, 2, 22, g[1]); rect(ctx, 33, 22, 2, 22, g[0]);
  rect(ctx, 27, 0, 2, 7, w[2]); px(ctx, 29, 1, '#d9485a'); px(ctx, 30, 2, '#d9485a'); px(ctx, 31, 2, '#d9485a');
  for (const x of [1, 53]) { rect(ctx, x, 38, 2, 8, w[1]); }
  rect(ctx, 5, 44, 46, 3, 'rgba(0,0,0,.2)');
  return outline(c);
}
function palm(): HTMLCanvasElement {
  const [c, ctx] = mk(40, 56); const t = ramp('#9a6a3a', 4), g = ramp('#3fa84a', 5);
  for (let y = 0; y < 34; y++) { const x = 20 + Math.round(Math.sin(y * 0.12) * 3); rect(ctx, x, 20 + y, 4, 1, y % 4 === 0 ? t[1] : t[2]); px(ctx, x, 20 + y, t[3]); }
  const frond = (dx: number, dy: number, ln: number) => {
    for (let i = 0; i < ln; i++) {
      const x = 22 + Math.round(dx * i), y = 20 + Math.round(dy * i + i * i * 0.025);
      rect(ctx, x - 1, y, 3, 2, g[i % 3 ? 2 : 3]); px(ctx, x, y - 1, g[4]); px(ctx, x, y + 2, g[1]);
    }
  };
  frond(-1, -0.2, 16); frond(1, -0.2, 16); frond(-0.7, -0.7, 12); frond(0.7, -0.7, 12); frond(-0.3, -0.9, 9); frond(0.3, -0.9, 9); frond(-1, 0.3, 12); frond(1, 0.3, 12);
  ellipse(ctx, 21, 22, 3, 3, '#8a5a2a'); ellipse(ctx, 25, 23, 2, 2, '#8a5a2a');
  return outline(c);
}
function dryBush(): HTMLCanvasElement {
  const [c, ctx] = mk(20, 18); const w = ramp('#9a7a4a', 4);
  for (const [x, y, dx, dy] of [[10, 17, -6, -12], [10, 17, 6, -12], [10, 17, 0, -15], [10, 17, -9, -6], [10, 17, 9, -6]] as number[][]) {
    for (let i = 0; i < 12; i++) px(ctx, Math.round(x + dx * i / 12), Math.round(y + dy * i / 12), i % 3 ? w[1] : w[2]);
    px(ctx, x + dx + 1, y + dy, w[2]); px(ctx, x + dx - 1, y + dy + 1, w[2]);
  }
  return outline(c);
}
function rugObj(color: string): HTMLCanvasElement {
  const [c, ctx] = mk(32, 20); const g = ramp(color, 4);
  rect(ctx, 0, 2, 32, 16, g[1]); rect(ctx, 2, 4, 28, 12, g[2]);
  for (let i = 0; i < 6; i++) { px(ctx, 6 + i * 4, 10, '#f2c94c'); px(ctx, 8 + i * 4, 8, '#fff2b0'); px(ctx, 8 + i * 4, 12, '#fff2b0'); }
  for (let x = 0; x < 32; x += 2) { px(ctx, x, 1, '#f2e4c8'); px(ctx, x, 18, '#f2e4c8'); }
  return outline(c);
}
function camel(f: number): HTMLCanvasElement {
  const [c, ctx] = mk(40, 36); const g = ramp('#c9a060', 5);
  const lift = f % 2;
  for (const [x, ph] of [[8, 0], [13, 1], [26, 1], [31, 0]]) { rect(ctx, x, 22, 3, 12 - (ph === lift ? 2 : 0), g[1]); rect(ctx, x, 33 - (ph === lift ? 2 : 0), 3, 1, g[0]); }
  shadedEllipse(ctx, 20, 20, 13, 6, g);
  shadedEllipse(ctx, 15, 13, 4, 5, g); shadedEllipse(ctx, 24, 14, 4, 5, g);
  rect(ctx, 31, 8, 4, 12, g[2]); rect(ctx, 31, 8, 2, 12, g[3]);
  shadedEllipse(ctx, 35, 8, 4, 3, g); rect(ctx, 37, 8, 3, 3, g[3]); px(ctx, 36, 6, '#12081e');
  rect(ctx, 12, 12, 14, 4, '#3a8ac0'); rect(ctx, 12, 12, 14, 1, '#6ab0e0');
  rect(ctx, 7, 18, 3, 6, g[2]);
  return outline(c);
}
function ladder(): HTMLCanvasElement {
  const [c, ctx] = mk(16, 48); const w = ramp('#8a5a2a', 4);
  rect(ctx, 2, 0, 2, 48, w[2]); rect(ctx, 12, 0, 2, 48, w[1]);
  for (let y = 4; y < 48; y += 8) { rect(ctx, 2, y, 12, 2, w[3]); }
  return outline(c);
}
function cartSprite(): HTMLCanvasElement {
  const [c, ctx] = mk(40, 30); const w = ramp('#8a5a2a', 4);
  rect(ctx, 4, 10, 32, 12, w[2]); rect(ctx, 4, 10, 32, 2, w[3]); rect(ctx, 4, 21, 32, 1, w[0]);
  for (let x = 8; x < 36; x += 6) rect(ctx, x, 12, 1, 9, w[1]);
  for (const x of [6, 30]) { ellipse(ctx, x + 3, 24, 5, 5, w[0]); ellipse(ctx, x + 3, 24, 4, 4, w[2]); ellipse(ctx, x + 3, 24, 1, 1, w[0]); }
  for (const [x, y, col] of [[10, 7, '#e86a3a'], [16, 6, '#e8c43a'], [22, 7, '#7ac04a'], [28, 6, '#e86a3a']] as [number, number, string][]) ellipse(ctx, x, y, 3, 3, col);
  return outline(c);
}
function mailbox(): HTMLCanvasElement {
  const [c, ctx] = mk(12, 22); const w = ramp('#6a4a2a', 3);
  rect(ctx, 5, 8, 2, 14, w[1]); rect(ctx, 1, 2, 10, 7, '#c9283a'); rect(ctx, 1, 2, 10, 2, '#e8485a'); rect(ctx, 3, 5, 6, 1, '#7a1a28');
  return outline(c);
}
function flowerBed(v: number): HTMLCanvasElement {
  const [c, ctx] = mk(32, 14); const g = ramp('#3f9a4a', 4);
  rect(ctx, 0, 6, 32, 7, '#6a4a2a'); rect(ctx, 0, 6, 32, 1, '#8a6a3a'); rect(ctx, 0, 12, 32, 1, '#3a2a1a');
  const cols = [['#ff6f91', '#ffd6e0'], ['#ffd166', '#fff2b0'], ['#b39dff', '#e0d6ff'], ['#ffffff', '#ffe066']];
  for (let i = 0; i < 9; i++) { const x = 2 + i * 3, col = cols[(i + v) % 4]; px(ctx, x, 4 - (i % 3), col[0]); px(ctx, x + 1, 4 - (i % 3), col[1]); px(ctx, x, 5 - (i % 3), g[2]); px(ctx, x, 6 - (i % 3), g[1]); }
  return outline(c);
}
function statueSprite(): HTMLCanvasElement {
  const [c, ctx] = mk(24, 44); const s = ramp('#a8a8bc', 5);
  rect(ctx, 2, 34, 20, 8, s[1]); rect(ctx, 2, 34, 20, 2, s[3]); rect(ctx, 5, 28, 14, 6, s[2]);
  rect(ctx, 9, 12, 6, 17, s[2]); rect(ctx, 9, 12, 2, 17, s[3]); ellipse(ctx, 12, 8, 4, 4, s[3]); rect(ctx, 5, 14, 4, 2, s[2]); rect(ctx, 15, 8, 2, 8, s[1]); rect(ctx, 14, 2, 4, 6, '#d8e0f0'); px(ctx, 15, 2, '#fff');
  return outline(c);
}
function woodPile(): HTMLCanvasElement {
  const [c, ctx] = mk(24, 16); const w = ramp('#8a5a2a', 4);
  for (let i = 0; i < 3; i++) for (let j = 0; j < 4 - i; j++) { ellipse(ctx, 4 + j * 5 + i * 2, 12 - i * 4, 2, 2, w[2]); px(ctx, 4 + j * 5 + i * 2, 12 - i * 4, '#d9b070'); }
  return outline(c);
}
function gateArch(): HTMLCanvasElement {
  const [c, ctx] = mk(64, 56); const s = ramp('#c0a070', 5);
  rect(ctx, 0, 8, 14, 48, s[2]); rect(ctx, 50, 8, 14, 48, s[1]); rect(ctx, 0, 8, 4, 48, s[3]);
  rect(ctx, 0, 0, 64, 12, s[3]); rect(ctx, 0, 0, 64, 3, s[4]); rect(ctx, 0, 10, 64, 2, s[1]);
  for (let x = 2; x < 62; x += 8) rect(ctx, x, 3, 4, 3, s[1]);
  for (let y = 16; y < 56; y += 6) { rect(ctx, 0, y + 5, 14, 1, s[0]); rect(ctx, 50, y + 5, 14, 1, s[0]); }
  return outline(c);
}

Object.assign(OBJECTS, {
  cactus: { w: 20, h: 32, ox: -2, oy: 0, solid: [[0, 0]], frames: 1, draw: (_f: number, v: number) => memo(`cactus${v % 2}`, () => cactus(v)) },
  jar: { w: 16, h: 20, ox: 0, oy: 0, solid: [[0, 0]], frames: 1, draw: (_f: number, v: number) => memo(`jar${v % 4}`, () => jar(v)) },
  plant: { w: 16, h: 20, ox: 0, oy: 0, solid: [[0, 0]], frames: 1, draw: (_f: number, v: number) => memo(`plant${v % 3}`, () => potPlant(v)) },
  tent: { w: 56, h: 48, ox: -4, oy: 0, solid: [[0, 0], [1, 0], [2, 0], [1, -1], [2, -1]], frames: 1, draw: (_f: number, v: number) => memo(`tent${v % 3}`, () => tent(['#d8cdb0', '#c9483a', '#6a8ab8'][v % 3])) },
  palm: { w: 40, h: 56, ox: -12, oy: 0, solid: [[0, 0]], frames: 1, draw: () => memo('palm', palm) },
  dry_bush: { w: 20, h: 18, ox: -2, oy: 0, solid: [], frames: 1, draw: () => memo('dry', dryBush) },
  rug_red: { w: 32, h: 20, ox: 0, oy: 0, solid: [], frames: 1, draw: () => memo('rugr', () => rugObj('#b8323f')), sortOffset: -100 },
  rug_blue: { w: 32, h: 20, ox: 0, oy: 0, solid: [], frames: 1, draw: () => memo('rugb', () => rugObj('#3a6ac0')), sortOffset: -100 },
  camel: { w: 40, h: 36, ox: -6, oy: 0, solid: [[0, 0], [1, 0]], frames: 2, draw: (f: number) => memo(`camel${f % 2}`, () => camel(f)) },
  ladder: { w: 16, h: 48, ox: 0, oy: 0, solid: [[0, 0]], frames: 1, draw: () => memo('ladder', ladder) },
  cart: { w: 40, h: 30, ox: -4, oy: 0, solid: [[0, 0], [1, 0]], frames: 1, draw: () => memo('cart', cartSprite) },
  mailbox: { w: 12, h: 22, ox: 2, oy: 0, solid: [[0, 0]], frames: 1, draw: () => memo('mail', mailbox) },
  flowerbed: { w: 32, h: 14, ox: 0, oy: 0, solid: [[0, 0], [1, 0]], frames: 1, draw: (_f: number, v: number) => memo(`fbed${v % 4}`, () => flowerBed(v)) },
  statue: { w: 24, h: 44, ox: -4, oy: 0, solid: [[0, 0]], frames: 1, draw: () => memo('statue', statueSprite) },
  woodpile: { w: 24, h: 16, ox: -4, oy: 0, solid: [[0, 0]], frames: 1, draw: () => memo('wood', woodPile) },
  gate: { w: 64, h: 56, ox: 0, oy: 0, solid: [[0, 0], [3, 0], [0, -1], [3, -1], [0, -2], [3, -2]], frames: 1, draw: () => memo('gate', gateArch) },
} as Record<string, ObjDef>);
