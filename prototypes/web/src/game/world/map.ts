import { Rng, Dir } from '../../engine/util';
import { T, TS, TILE_INFO, TILE_BASE, tileCanvas, wallFace, OBJECTS, houseDef, ObjDef } from '../../art/tiles';
import { mk, ramp, rect, px } from '../../art/pixel';
import type { ScriptCtx } from '../script';

export interface ObjPlace { type: string; tx: number; ty: number; v: number; id?: string; hideFlag?: string; showFlag?: string }
export interface NpcDef {
  id: string; name: string; look: string; tx: number; ty: number; dir?: Dir; wander?: boolean;
  talk: (c: ScriptCtx) => Promise<void>;
  show?: () => boolean;
  marker?: () => '!' | '?' | null;
  portrait?: string;
}
export interface ChestDef { id: string; tx: number; ty: number; item?: string; count?: number; gold?: number }
export interface WarpDef { tx: number; ty: number; w: number; h: number; to: string; ntx: number; nty: number; dir?: Dir; need?: () => string | null }
export interface TriggerDef { id: string; tx: number; ty: number; w: number; h: number; once: boolean; run: (c: ScriptCtx) => Promise<void>; cond?: () => boolean }
export interface SpawnDef { enemy: string; tx: number; ty: number; id?: string; once?: boolean; cond?: () => boolean }
export interface BarrierDef { id: string; tx: number; ty: number; w: number; h: number; openFlag: string; color: string }
export interface SignDef { tx: number; ty: number; text: string[] }

export type Ambient = 'none' | 'fireflies' | 'leaves' | 'dust' | 'snow' | 'sand' | 'embers';

export interface MapDef {
  id: string; name: string; w: number; h: number;
  ground: Uint8Array; variant: Uint8Array;
  objs: ObjPlace[];
  extraSolid: Uint8Array;
  npcs: NpcDef[]; chests: ChestDef[]; warps: WarpDef[]; triggers: TriggerDef[]; spawns: SpawnDef[]; barriers: BarrierDef[]; signs: SignDef[];
  music: string; dark: number; ambient: Ambient; tint?: string;
  wallKind: 'cave' | 'house' | 'ice';
  indoor?: boolean;
  start?: { tx: number; ty: number };
  onEnter?: (c: ScriptCtx) => Promise<void>;
  saveSpots?: { tx: number; ty: number }[];
}

export function getObjDef(type: string): ObjDef {
  if (type.startsWith('house')) return houseDef(parseInt(type.slice(5)) || 5);
  const d = OBJECTS[type];
  if (!d) throw new Error('unknown object ' + type);
  return d;
}

export class MB {
  w: number; h: number;
  ground: Uint8Array; variant: Uint8Array; extraSolid: Uint8Array;
  objs: ObjPlace[] = [];
  npcs: NpcDef[] = []; chests: ChestDef[] = []; warps: WarpDef[] = []; triggers: TriggerDef[] = []; spawns: SpawnDef[] = []; barriers: BarrierDef[] = []; signs: SignDef[] = [];
  rng: Rng;
  private occ: Uint8Array;
  def: Partial<MapDef> = {};

  constructor(public id: string, public name: string, w: number, h: number, fill: number, seed = 1) {
    this.w = w; this.h = h;
    this.ground = new Uint8Array(w * h).fill(fill);
    this.variant = new Uint8Array(w * h);
    this.extraSolid = new Uint8Array(w * h);
    this.occ = new Uint8Array(w * h);
    this.rng = new Rng(seed);
    for (let i = 0; i < w * h; i++) this.variant[i] = this.rng.int(0, 3);
  }
  inb(x: number, y: number) { return x >= 0 && y >= 0 && x < this.w && y < this.h; }
  get(x: number, y: number) { return this.inb(x, y) ? this.ground[y * this.w + x] : T.VOID; }
  set(t: number, x: number, y: number) { if (this.inb(x, y)) this.ground[y * this.w + x] = t; }
  fill(t: number, x: number, y: number, w: number, h: number) { for (let j = 0; j < h; j++) for (let i = 0; i < w; i++) this.set(t, x + i, y + j); }
  outline(t: number, x: number, y: number, w: number, h: number) {
    for (let i = 0; i < w; i++) { this.set(t, x + i, y); this.set(t, x + i, y + h - 1); }
    for (let j = 0; j < h; j++) { this.set(t, x, y + j); this.set(t, x + w - 1, y + j); }
  }
  blob(t: number, cx: number, cy: number, rx: number, ry: number, jitter = 0.25, onlyOn?: number[]) {
    for (let y = Math.floor(cy - ry - 2); y <= cy + ry + 2; y++) for (let x = Math.floor(cx - rx - 2); x <= cx + rx + 2; x++) {
      const dx = (x - cx) / rx, dy = (y - cy) / ry;
      const n = (this.rng.next() - 0.5) * jitter;
      if (dx * dx + dy * dy + n <= 1 && this.inb(x, y) && (!onlyOn || onlyOn.includes(this.get(x, y)))) this.set(t, x, y);
    }
  }
  /** Winding path between points with given width (tiles). */
  path(t: number, pts: [number, number][], width = 2, wobble = 0) {
    for (let i = 0; i < pts.length - 1; i++) {
      const [x0, y0] = pts[i], [x1, y1] = pts[i + 1];
      const n = Math.max(Math.abs(x1 - x0), Math.abs(y1 - y0)) * 2;
      for (let k = 0; k <= n; k++) {
        const f = k / n;
        const w = wobble ? Math.sin(f * 6 + i) * wobble : 0;
        const x = x0 + (x1 - x0) * f + (Math.abs(x1 - x0) < Math.abs(y1 - y0) ? w : 0);
        const y = y0 + (y1 - y0) * f + (Math.abs(x1 - x0) >= Math.abs(y1 - y0) ? w : 0);
        for (let a = 0; a < width; a++) for (let b = 0; b < width; b++) this.set(t, Math.round(x - width / 2 + a + 0.5), Math.round(y - width / 2 + b + 0.5));
      }
    }
  }
  patches(t: number, n: number, rmin: number, rmax: number, onlyOn?: number[]) {
    for (let i = 0; i < n; i++) this.blob(t, this.rng.range(2, this.w - 2), this.rng.range(2, this.h - 2), this.rng.range(rmin, rmax), this.rng.range(rmin, rmax) * 0.8, 0.6, onlyOn);
  }
  scatterTiles(t: number, n: number, onlyOn: number[]) {
    for (let i = 0; i < n; i++) { const x = this.rng.int(0, this.w - 1), y = this.rng.int(0, this.h - 1); if (onlyOn.includes(this.get(x, y))) this.set(t, x, y); }
  }

  free(tx: number, ty: number) {
    if (!this.inb(tx, ty)) return false;
    if (TILE_INFO[this.get(tx, ty)]?.solid) return false;
    return !this.occ[ty * this.w + tx] && !this.extraSolid[ty * this.w + tx];
  }
  /** Place a decorative/solid object. */
  obj(type: string, tx: number, ty: number, v = 0, opts: { id?: string; hideFlag?: string; showFlag?: string } = {}): ObjPlace {
    const d = getObjDef(type);
    for (const [dx, dy] of d.solid) if (this.inb(tx + dx, ty + dy)) this.occ[(ty + dy) * this.w + tx + dx] = 1;
    const o = { type, tx, ty, v, ...opts };
    this.objs.push(o);
    return o;
  }
  /** Occupy cells without drawing (e.g. for large ground decorations). */
  block(x: number, y: number, w: number, h: number) { for (let j = 0; j < h; j++) for (let i = 0; i < w; i++) if (this.inb(x + i, y + j)) this.extraSolid[(y + j) * this.w + x + i] = 1; }
  unblock(x: number, y: number, w = 1, h = 1) { for (let j = 0; j < h; j++) for (let i = 0; i < w; i++) if (this.inb(x + i, y + j)) { this.extraSolid[(y + j) * this.w + x + i] = 0; this.occ[(y + j) * this.w + x + i] = 0; } }

  house(tx: number, ty: number, w: number, v: number, warp?: { to: string; ntx: number; nty: number }, sign?: string[]) {
    this.obj('house' + w, tx, ty, v);
    const dx = tx + Math.floor(w / 2);
    this.unblock(dx, ty);
    if (warp) this.warps.push({ tx: dx, ty, w: 1, h: 1, to: warp.to, ntx: warp.ntx, nty: warp.nty, dir: 'up' });
    else this.signs.push({ tx: dx, ty, text: sign ?? ['A porta está trancada.'] });
    // path under door
    for (let i = -1; i <= 1; i++) if (this.get(dx + i, ty + 1) !== T.WATER) this.set(T.DIRT, dx + i, ty + 1);
  }

  /** Scatter objects randomly over free tiles inside a region, honouring spacing. */
  scatter(types: string[], n: number, x0: number, y0: number, x1: number, y1: number, opts: { grounds?: number[]; gap?: number; vmax?: number; open?: boolean; avoid?: { x: number; y: number; r: number }[] } = {}) {
    let placed = 0, tries = 0;
    const gap = opts.gap ?? 1;
    while (placed < n && tries < n * 30) {
      tries++;
      const x = this.rng.int(x0, x1), y = this.rng.int(y0, y1);
      if (!this.free(x, y)) continue;
      if (opts.grounds && !opts.grounds.includes(this.get(x, y))) continue;
      if (opts.avoid && opts.avoid.some((a) => Math.hypot(a.x - x, a.y - y) < a.r)) continue;
      if (opts.open) { let bad = false; for (let j = -1; j <= 1 && !bad; j++) for (let i = -1; i <= 1; i++) if (!this.free(x + i, y + j)) { bad = true; break; } if (bad) continue; }
      let ok = true;
      for (let j = -gap; j <= gap && ok; j++) for (let i = -gap; i <= gap; i++) if (this.occ[(y + j) * this.w + x + i] && this.inb(x + i, y + j)) { ok = false; break; }
      if (!ok) continue;
      this.obj(this.rng.pick(types), x, y, this.rng.int(0, opts.vmax ?? 2));
      placed++;
    }
  }

  /** Draw a visual border of trees (and make the outer ring solid) except for the listed gaps. */
  treeBorder(thick: number, gaps: { x0: number; y0: number; x1: number; y1: number }[], kinds = ['tree', 'tree', 'pine']) {
    const inGap = (x: number, y: number) => gaps.some((g) => x >= g.x0 && x <= g.x1 && y >= g.y0 && y <= g.y1);
    for (let y = 0; y < this.h; y++) for (let x = 0; x < this.w; x++) {
      const edge = x < thick || y < thick || x >= this.w - thick || y >= this.h - thick;
      if (!edge || inGap(x, y)) continue;
      this.extraSolid[y * this.w + x] = 1;
    }
    for (let y = 0; y < this.h; y += 2) for (let x = 0; x < this.w; x += 2) {
      const edge = x < thick + 1 || y < thick + 1 || x >= this.w - thick - 1 || y >= this.h - thick - 1;
      if (!edge) continue;
      const near = (px2: number, py2: number) => inGap(px2, py2);
      if (near(x, y) || near(x + 1, y) || near(x - 1, y) || near(x, y + 1) || near(x, y - 1)) continue;
      const jx = this.rng.int(0, 1), jy = this.rng.int(0, 1);
      this.objs.push({ type: this.rng.pick(kinds), tx: Math.min(this.w - 1, x + jx), ty: Math.min(this.h - 1, y + jy + 1), v: this.rng.int(0, 2) });
    }
  }

  build(extra: Partial<MapDef> & { music: string }): MapDef {
    return {
      id: this.id, name: this.name, w: this.w, h: this.h,
      ground: this.ground, variant: this.variant, objs: this.objs, extraSolid: this.extraSolid,
      npcs: this.npcs, chests: this.chests, warps: this.warps, triggers: this.triggers, spawns: this.spawns, barriers: this.barriers, signs: this.signs,
      dark: 0, ambient: 'none', wallKind: 'cave',
      ...this.def, ...extra,
    };
  }
}

// -------- baking --------
export interface Baked { canvas: HTMLCanvasElement; water: { x: number; y: number; deep: boolean; v: number }[] }

export function bakeMap(def: MapDef): Baked {
  const [cv, ctx] = mk(def.w * TS, def.h * TS);
  const water: Baked['water'] = [];
  const rng = new Rng(hash(def.id));
  const g = (x: number, y: number) => (x < 0 || y < 0 || x >= def.w || y >= def.h ? T.VOID : def.ground[y * def.w + x]);
  const isWall = (t: number) => t === T.WALL || t === T.VOID || t === T.DWOOD;
  for (let y = 0; y < def.h; y++) {
    for (let x = 0; x < def.w; x++) {
      const t = g(x, y);
      const v = def.variant[y * def.w + x];
      const info = TILE_INFO[t];
      if (t === T.WALL || t === T.DWOOD) {
        const below = g(x, y + 1);
        if (!isWall(below)) ctx.drawImage(wallFace(v, def.wallKind), x * TS, y * TS);
        else ctx.drawImage(tileCanvas(def.wallKind === 'house' ? T.DWOOD : T.WALL, v), x * TS, y * TS);
        continue;
      }
      ctx.drawImage(tileCanvas(t, v, 0), x * TS, y * TS);
      if (info?.anim) water.push({ x, y, deep: t === T.DEEP, v });
      // ambient occlusion below walls
      if (isWall(g(x, y - 1)) && !isWall(t)) {
        ctx.fillStyle = 'rgba(8,4,24,.32)'; ctx.fillRect(x * TS, y * TS, TS, 4);
        ctx.fillStyle = 'rgba(8,4,24,.16)'; ctx.fillRect(x * TS, y * TS + 4, TS, 3);
      }
      if (def.wallKind !== 'house' || !def.indoor) {
        if (isWall(g(x - 1, y)) && !isWall(t)) { ctx.fillStyle = 'rgba(8,4,24,.2)'; ctx.fillRect(x * TS, y * TS, 3, TS); }
        if (isWall(g(x + 1, y)) && !isWall(t)) { ctx.fillStyle = 'rgba(8,4,24,.2)'; ctx.fillRect(x * TS + TS - 3, y * TS, 3, TS); }
      }
      // organic terrain edges: neighbours with higher rank spill over
      if (!info || info.rank >= 9) continue;
      const dirs: [number, number][] = [[0, -1], [0, 1], [-1, 0], [1, 0]];
      for (const [dx, dy] of dirs) {
        const nt = g(x + dx, y + dy);
        const ni = TILE_INFO[nt];
        if (!ni || ni.rank >= 9 || ni.rank <= info.rank || nt === t) continue;
        if (info.anim && ni.anim) continue;
        if ((t === T.BRIDGE || nt === T.BRIDGE || t === T.WOOD || nt === T.WOOD || t === T.RUG || nt === T.RUG)) continue;
        const col = ramp(TILE_BASE[nt], 5);
        for (let k = 0; k < TS; k++) {
          const depth = 1 + (rng.next() < 0.5 ? 1 : 0) + (rng.next() < 0.25 ? 1 : 0);
          for (let d = 0; d < depth; d++) {
            const ex = dx === 0 ? x * TS + k : dx < 0 ? x * TS + d : x * TS + TS - 1 - d;
            const ey = dy === 0 ? y * TS + k : dy < 0 ? y * TS + d : y * TS + TS - 1 - d;
            px(ctx, ex, ey, d === depth - 1 ? col[1] : rng.next() < 0.3 ? col[3] : col[2]);
          }
        }
        // foam / bank line on water edges
        if (info.anim) {
          for (let k = 0; k < TS; k += 2) {
            const ex = dx === 0 ? x * TS + k : dx < 0 ? x * TS + 3 : x * TS + TS - 4;
            const ey = dy === 0 ? y * TS + k : dy < 0 ? y * TS + 3 : y * TS + TS - 4;
            px(ctx, ex, ey, '#dff4ff');
          }
        }
      }
    }
  }
  return { canvas: cv, water };
}

function hash(s: string) { let h = 5381; for (let i = 0; i < s.length; i++) h = ((h << 5) + h + s.charCodeAt(i)) | 0; return h >>> 0; }
void rect;
