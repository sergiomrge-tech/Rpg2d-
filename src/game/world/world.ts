import { VW, VH, Disp, text, panel, bar, measure, wrap } from '../../engine/display';
import { Input } from '../../engine/input';
import { Audio } from '../../engine/audio';
import { clamp, lerp, dist, Dir, DIR_VEC, dirFromVec, Rng } from '../../engine/util';
import { G } from '../state';
import { ENEMIES } from '../data/enemies';
import { getMap } from './maps';
import { MapDef, bakeMap, Baked, getObjDef, ObjPlace, NpcDef } from './map';
import { TS, T, TILE_INFO, tileCanvas, chestCanvas } from '../../art/tiles';
import { mk, flipX } from '../../art/pixel';
import { Player, Enemy, Npc, Ally, ChestE, Pickup, Proj, Particle, DmgText, AreaFx, drawShadow, drawChar, Body } from '../entities';
import { monsterArt } from '../../art/monsters';
import { Modal } from '../ui/modal';
import { updateEnemy } from './ai';
import * as Combat from './combat';
import { Script } from '../script';
import { drawHud, drawMinimapInit } from '../ui/hud';
import { ITEMS } from '../data/items';

export interface Light { x: number; y: number; r: number; color: string; flicker?: boolean }
interface Toast { text: string; icon?: string; t: number; color: string }
interface Banner { text: string; sub?: string; t: number }

const flipCache = new WeakMap<HTMLCanvasElement, HTMLCanvasElement>();
export function flipped(c: HTMLCanvasElement) {
  let f = flipCache.get(c);
  if (!f) { f = flipX(c); flipCache.set(c, f); }
  return f;
}

export class World {
  def!: MapDef;
  baked!: Baked;
  solid!: Uint8Array;
  player = new Player();
  enemies: Enemy[] = [];
  npcs: Npc[] = [];
  allies: Ally[] = [];
  chests: ChestE[] = [];
  pickups: Pickup[] = [];
  projs: Proj[] = [];
  areas: AreaFx[] = [];
  parts: Particle[] = [];
  texts: DmgText[] = [];
  slashes: { x: number; y: number; ang: number; t: number; dur: number; r: number; spread: number; color: string }[] = [];
  lights: Light[] = [];
  objSorted: (ObjPlace & { px: number; py: number; sortY: number; def: ReturnType<typeof getObjDef> })[] = [];
  cam = { x: 0, y: 0 };
  shake = 0;
  hitstop = 0;
  time = 0;
  modals: Modal<any>[] = [];
  locked = false;       // cutscene / scripted control
  fadeA = 1;
  fadeTo = 0;
  fadeSpeed = 2;
  fadeColor = '#000';
  flow = new Int16Array(0);
  flowT = 0;
  toasts: Toast[] = [];
  banner: Banner | null = null;
  bossBar: Enemy | null = null;
  explored = new Map<string, Uint8Array>();
  script = new Script(this);
  laters: { t: number; fn: () => void }[] = [];
  ambientParts: { x: number; y: number; vx: number; vy: number; ph: number; s: number }[] = [];
  mapTimer = 0;
  pendingWarp: { to: string; tx: number; ty: number; dir?: Dir } | null = null;
  nearTarget: { x: number; y: number; kind: string; ref?: unknown } | null = null;
  combatT = 0;           // seconds since last combat event
  musicOverride: string | null = null;
  onGameOver?: () => void;
  onWarped?: () => void;
  mini!: ReturnType<typeof drawMinimapInit>;
  rng = new Rng(Date.now() & 0xffff);
  letterbox = 0;
  lbAmt = 0;
  spawnNpcFn = (def: NpcDef): Npc => { const n = new Npc(def); this.npcs.push(n); return n; };
  chapterText: { title: string; sub: string; t: number; resolve: () => void } | null = null;
  chapterCard(title: string, sub: string): Promise<void> { return new Promise((res) => { this.chapterText = { title, sub, t: 0, resolve: res }; }); }

  // ---------------------------------------------------------------- map loading
  loadMap(id: string, tx: number, ty: number, dir: Dir = 'down', silent = false) {
    this.def = getMap(id);
    this.baked = bakeMap(this.def);
    const { w, h } = this.def;
    this.solid = new Uint8Array(w * h);
    for (let i = 0; i < w * h; i++) {
      if (TILE_INFO[this.def.ground[i]]?.solid || this.def.extraSolid[i]) this.solid[i] = 1;
    }
    this.objSorted = [];
    this.lights = [];
    for (const o of this.def.objs) {
      const d = getObjDef(o.type);
      if (o.hideFlag && G.has(o.hideFlag)) continue;
      if (o.showFlag && !G.has(o.showFlag)) continue;
      for (const [dx, dy] of d.solid) {
        const x = o.tx + dx, y = o.ty + dy;
        if (x >= 0 && y >= 0 && x < w && y < h) this.solid[y * w + x] = 1;
      }
      // doors of houses are free
      const px = o.tx * TS + d.ox, py = (o.ty + 1) * TS - d.h + d.oy;
      this.objSorted.push({ ...o, px, py, sortY: (o.ty + 1) * TS + (d.sortOffset ?? 0), def: d });
    }
    for (const o of this.def.objs) {
      if (o.type.startsWith('house')) {
        const dw = parseInt(o.type.slice(5));
        const dx = o.tx + Math.floor(dw / 2);
        if (this.def.warps.some((wp) => wp.tx === dx && wp.ty === o.ty) || this.def.signs.some((s) => s.tx === dx && s.ty === o.ty)) this.solid[o.ty * w + dx] = this.def.signs.some((s) => s.tx === dx && s.ty === o.ty) ? 1 : 0;
      }
    }
    this.objSorted.sort((a, b) => a.sortY - b.sortY);
    for (const o of this.objSorted) {
      if (o.def.light) this.lights.push({ x: o.tx * TS + 8, y: (o.ty + 1) * TS + (o.def.light.dy ?? -8), r: o.def.light.r, color: o.def.light.color, flicker: o.def.light.flicker });
    }
    for (const b of this.def.barriers) {
      if (!G.has(b.openFlag)) for (let j = 0; j < b.h; j++) for (let i = 0; i < b.w; i++) this.solid[(b.ty + j) * w + b.tx + i] = 1;
    }
    for (const s of this.def.signs) this.solid[s.ty * w + s.tx] = this.solid[s.ty * w + s.tx] || 0;

    this.enemies = []; this.projs = []; this.areas = []; this.parts = []; this.texts = []; this.pickups = []; this.slashes = []; this.laters = [];
    this.npcs = this.def.npcs.filter((n) => !n.show || n.show()).map((n) => new Npc(n));
    this.chests = this.def.chests.map((c) => { const e = new ChestE(c); e.opened = !!G.opened[this.def.id + ':' + c.id]; return e; });
    for (const c of this.chests) this.solid[c.def.ty * w + c.def.tx] = 1;
    for (const s of this.def.spawns) {
      if (s.cond && !s.cond()) continue;
      if (s.once && G.has('dead_' + s.id)) continue;
      const e = new Enemy(ENEMIES[s.enemy], s.tx * TS + 8, s.ty * TS + 12);
      e.spawnId = s.id;
      this.enemies.push(e);
    }
    this.syncAllies(tx * TS + 8, ty * TS + 12);
    const p = this.player;
    p.x = tx * TS + 8; p.y = ty * TS + 12; p.vx = p.vy = 0; p.dir = dir;
    p.state = 'idle'; p.t = 0;
    this.cam.x = p.x - VW / 2; this.cam.y = p.y - VH / 2;
    this.clampCam();
    this.flow = new Int16Array(w * h).fill(-1);
    this.flowT = 0;
    this.bossBar = null;
    G.map = id;
    // ambient particles
    this.ambientParts = [];
    const amb = this.def.ambient;
    if (amb !== 'none') for (let i = 0; i < 46; i++) this.ambientParts.push({ x: Math.random() * VW, y: Math.random() * VH, vx: (Math.random() - 0.5) * 6, vy: amb === 'leaves' || amb === 'snow' ? 8 + Math.random() * 10 : (Math.random() - 0.5) * 6, ph: Math.random() * 7, s: 0.5 + Math.random() });
    this.mini = drawMinimapInit(this);
    if (!silent) {
      Audio.music(this.musicOverride ?? this.def.music);
      this.banner = { text: this.def.name, t: 0 };
    }
    this.script.onMapEnter();
  }

  addObject(type: string, tx: number, ty: number, v = 0) {
    const d = getObjDef(type);
    const px = tx * TS + d.ox, py = (ty + 1) * TS - d.h + d.oy;
    this.objSorted.push({ type, tx, ty, v, px, py, sortY: (ty + 1) * TS + (d.sortOffset ?? 0), def: d });
    this.objSorted.sort((a, b) => a.sortY - b.sortY);
    if (d.light) this.lights.push({ x: tx * TS + 8, y: (ty + 1) * TS + (d.light.dy ?? -8), r: d.light.r, color: d.light.color, flicker: d.light.flicker });
  }

  syncAllies(x: number, y: number) {
    const want = ['lyra', 'torren', 'sylphie', 'rhea'].filter((n) => G.has('ally_' + n));
    this.allies = want.map((n, i) => { const a = new Ally(n); a.x = x - 8 * (i + 1); a.y = y; return a; });
  }

  // ---------------------------------------------------------------- helpers
  tileSolid(tx: number, ty: number) {
    if (tx < 0 || ty < 0 || tx >= this.def.w || ty >= this.def.h) return true;
    return this.solid[ty * this.def.w + tx] === 1;
  }
  boxFree(x: number, y: number, hw: number, hh: number) {
    const x0 = Math.floor((x - hw) / TS), x1 = Math.floor((x + hw - 0.01) / TS);
    const y0 = Math.floor((y - hh) / TS), y1 = Math.floor((y + hh - 0.01) / TS);
    for (let j = y0; j <= y1; j++) for (let i = x0; i <= x1; i++) if (this.tileSolid(i, j)) return false;
    return true;
  }
  moveBody(b: Body, dx: number, dy: number, fly = false) {
    if (fly) {
      const nx = clamp(b.x + dx, 8, this.def.w * TS - 8), ny = clamp(b.y + dy, 8, this.def.h * TS - 4);
      b.x = nx; b.y = ny;
      return;
    }
    if (dx !== 0) { const nx = b.x + dx; if (this.boxFree(nx, b.y, b.hw, b.hh)) b.x = nx; else { const s = Math.sign(dx); let st = Math.abs(dx); while (st > 0.1 && !this.boxFree(b.x + s * st, b.y, b.hw, b.hh)) st -= 0.5; if (st > 0.1) b.x += s * st; } }
    if (dy !== 0) { const ny = b.y + dy; if (this.boxFree(b.x, ny, b.hw, b.hh)) b.y = ny; else { const s = Math.sign(dy); let st = Math.abs(dy); while (st > 0.1 && !this.boxFree(b.x, b.y + s * st, b.hw, b.hh)) st -= 0.5; if (st > 0.1) b.y += s * st; } }
  }
  los(x0: number, y0: number, x1: number, y1: number) {
    const n = Math.ceil(dist(x0, y0, x1, y1) / 6);
    for (let i = 1; i < n; i++) {
      const f = i / n;
      if (this.tileSolid(Math.floor(lerp(x0, x1, f) / TS), Math.floor(lerp(y0, y1, f) / TS))) return false;
    }
    return true;
  }
  later(delay: number, fn: () => void) { this.laters.push({ t: delay, fn }); }

  // flow field (BFS from the player's tile)
  updateFlow() {
    const { w, h } = this.def;
    const f = this.flow;
    f.fill(-1);
    const sx = clamp(Math.floor(this.player.x / TS), 0, w - 1), sy = clamp(Math.floor(this.player.y / TS), 0, h - 1);
    const q: number[] = [sy * w + sx];
    f[sy * w + sx] = 0;
    let head = 0;
    while (head < q.length) {
      const c = q[head++];
      const cx = c % w, cy = (c / w) | 0;
      const d = f[c];
      if (d > 34) continue;
      for (const [dx, dy] of [[1, 0], [-1, 0], [0, 1], [0, -1]]) {
        const nx = cx + dx, ny = cy + dy;
        if (nx < 0 || ny < 0 || nx >= w || ny >= h) continue;
        const ni = ny * w + nx;
        if (f[ni] !== -1 || this.solid[ni]) continue;
        f[ni] = d + 1;
        q.push(ni);
      }
    }
  }
  /** Direction to step along the flow field from (x,y); returns null if none. */
  flowDir(x: number, y: number): { x: number; y: number } | null {
    const { w, h } = this.def;
    const tx = Math.floor(x / TS), ty = Math.floor(y / TS);
    if (tx < 0 || ty < 0 || tx >= w || ty >= h) return null;
    const cur = this.flow[ty * w + tx];
    if (cur < 0) return null;
    let best = cur, bx = 0, by = 0;
    for (const [dx, dy] of [[1, 0], [-1, 0], [0, 1], [0, -1], [1, 1], [-1, 1], [1, -1], [-1, -1]]) {
      const nx = tx + dx, ny = ty + dy;
      if (nx < 0 || ny < 0 || nx >= w || ny >= h) continue;
      if (dx !== 0 && dy !== 0 && (this.solid[ty * w + nx] || this.solid[ny * w + tx])) continue;
      const v = this.flow[ny * w + nx];
      if (v >= 0 && v < best) { best = v; bx = dx; by = dy; }
    }
    if (bx === 0 && by === 0) return null;
    // aim at the centre of the next tile
    const cx = (tx + bx) * TS + 8, cy = (ty + by) * TS + 8;
    const m = Math.hypot(cx - x, cy - y) || 1;
    return { x: (cx - x) / m, y: (cy - y) / m };
  }

  clampCam() {
    const mw = this.def.w * TS, mh = this.def.h * TS;
    this.cam.x = mw <= VW ? (mw - VW) / 2 : clamp(this.cam.x, 0, mw - VW);
    this.cam.y = mh <= VH ? (mh - VH) / 2 : clamp(this.cam.y, 0, mh - VH);
  }

  // ---------------------------------------------------------------- modals / UI services
  openModal<T>(m: Modal<T>): Promise<T> {
    this.modals.push(m);
    return new Promise<T>((res) => { m.resolver = res; });
  }
  get blocked() { return this.modals.some((m) => m.pauses); }
  toast(text: string, icon?: string, color = '#fff') { this.toasts.push({ text, icon, t: 0, color }); if (this.toasts.length > 5) this.toasts.shift(); }
  fade(to: number, speed = 2): Promise<void> {
    this.fadeTo = to; this.fadeSpeed = speed;
    return new Promise((res) => { const iv = setInterval(() => { if (Math.abs(this.fadeA - this.fadeTo) < 0.01) { clearInterval(iv); res(); } }, 16); });
  }
  addShake(a: number) { this.shake = Math.max(this.shake, a); }

  warp(to: string, tx: number, ty: number, dir: Dir = 'down') {
    if (this.pendingWarp) return;
    this.pendingWarp = { to, tx, ty, dir };
  }

  // ---------------------------------------------------------------- particles / fx
  burst(x: number, y: number, n: number, color: string | string[], o: { speed?: number; life?: number; size?: number; grav?: number; up?: number } = {}) {
    for (let i = 0; i < n; i++) {
      const a = Math.random() * Math.PI * 2, s = (0.4 + Math.random() * 0.6) * (o.speed ?? 50);
      const l = (o.life ?? 0.4) * (0.6 + Math.random() * 0.6);
      this.parts.push({ x, y, vx: Math.cos(a) * s, vy: Math.sin(a) * s - (o.up ?? 0), life: l, max: l, color: Array.isArray(color) ? color[(Math.random() * color.length) | 0] : color, size: o.size ?? 1, grav: o.grav ?? 0, fade: true });
    }
  }
  text(x: number, y: number, str: string, color = '#fff', big = false) { this.texts.push({ x, y, t: 0, str, color, big }); }

  drop(x: number, y: number, kind: Pickup['kind'], id: string, amount: number) { this.pickups.push(new Pickup(x, y, kind, id, amount)); }

  // ---------------------------------------------------------------- update
  update(dt: number) {
    dt = Math.max(0, Math.min(dt, 1 / 20));
    this.time += dt;
    if (Math.abs(this.fadeA - this.fadeTo) > 0.001) this.fadeA = clamp(this.fadeA + Math.sign(this.fadeTo - this.fadeA) * this.fadeSpeed * dt, Math.min(this.fadeA, this.fadeTo), Math.max(this.fadeA, this.fadeTo));

    // modals
    if (this.modals.length) {
      const top = this.modals[this.modals.length - 1];
      top.update(dt);
      this.modals = this.modals.filter((m) => !m.done);
    }
    this.lbAmt += (this.letterbox - this.lbAmt) * Math.min(1, dt * 6);
    if (this.chapterText) { this.chapterText.t += dt; if (this.chapterText.t > 6) { const r = this.chapterText.resolve; this.chapterText = null; r(); } }
    for (const t of this.toasts) t.t += dt;
    this.toasts = this.toasts.filter((t) => t.t < 3.2);
    if (this.banner) { this.banner.t += dt; if (this.banner.t > 3.4) this.banner = null; }

    if (this.pendingWarp && !this.blocked) {
      const pw = this.pendingWarp; this.pendingWarp = null;
      void this.doWarp(pw);
    }

    if (this.blocked) { this.ambient(dt); return; }
    G.playtime += dt;

    if (this.hitstop > 0) { this.hitstop -= dt; this.updateFx(dt * 0.3); this.updateCamera(dt); return; }

    for (const l of this.laters) l.t -= dt;
    const due = this.laters.filter((l) => l.t <= 0);
    this.laters = this.laters.filter((l) => l.t > 0);
    due.forEach((l) => l.fn());

    this.mapTimer += dt;
    this.combatT += dt;

    Combat.updatePlayer(this, dt);
    for (const e of this.enemies) updateEnemy(this, e, dt);
    this.enemies = this.enemies.filter((e) => !(e.dead));
    this.updateNpcs(dt);
    this.updateAllies(dt);
    Combat.updateProjectiles(this, dt);
    Combat.updateAreas(this, dt);
    this.updatePickups(dt);
    this.updateFx(dt);
    this.updateBarriers();
    this.flowT -= dt;
    if (this.flowT <= 0 && this.enemies.length) { this.updateFlow(); this.flowT = 0.3; }
    this.checkTriggers();
    this.updateCamera(dt);
    this.updateExplore();
    this.ambient(dt);
    if (this.enemies.some((e) => e.aggro && !e.def.boss && !e.dead)) this.combatT = 0;
    if (this.bossBar && (this.bossBar.dead || this.bossBar.hp <= 0)) this.bossBar = null;
    // interaction prompt
    this.nearTarget = this.findInteractable();
    if (!this.locked && (Input.pressed('interact')) && this.nearTarget) { this.interact(this.nearTarget); }
  }

  ambient(dt: number) {
    for (const p of this.ambientParts) {
      p.x += (p.vx + Math.sin(this.time + p.ph) * 4) * dt; p.y += (p.vy + Math.cos(this.time * 0.7 + p.ph) * 3) * dt;
      if (p.x < -4) p.x += VW + 8; if (p.x > VW + 4) p.x -= VW + 8;
      if (p.y < -4) p.y += VH + 8; if (p.y > VH + 4) p.y -= VH + 8;
    }
  }

  updateFx(dt: number) {
    for (const p of this.parts) { p.life -= dt; p.x += p.vx * dt; p.y += p.vy * dt; p.vy += p.grav * dt; p.vx *= 1 - Math.min(1, dt * 1.5); }
    this.parts = this.parts.filter((p) => p.life > 0);
    for (const t of this.texts) t.t += dt;
    this.texts = this.texts.filter((t) => t.t < 1.0);
    for (const s of this.slashes) s.t += dt;
    this.slashes = this.slashes.filter((s) => s.t < s.dur);
    this.shake = Math.max(0, this.shake - dt * 14);
  }

  updateCamera(dt: number) {
    const p = this.player;
    const look = DIR_VEC[p.dir];
    const tx = p.x - VW / 2 + look.x * 14, ty = p.y - 10 - VH / 2 + look.y * 10;
    const k = 1 - Math.pow(0.0008, dt);
    this.cam.x = lerp(this.cam.x, tx, k); this.cam.y = lerp(this.cam.y, ty, k);
    this.clampCam();
    const sh = this.shake;
    Disp.shakeX = sh ? (Math.random() - 0.5) * sh : 0;
    Disp.shakeY = sh ? (Math.random() - 0.5) * sh : 0;
  }

  updateExplore() {
    let ex = this.explored.get(this.def.id);
    if (!ex) { ex = new Uint8Array(this.def.w * this.def.h); this.explored.set(this.def.id, ex); }
    const cx = Math.floor(this.player.x / TS), cy = Math.floor(this.player.y / TS);
    const R = 11;
    for (let j = -R; j <= R; j++) for (let i = -R; i <= R; i++) {
      if (i * i + j * j > R * R) continue;
      const x = cx + i, y = cy + j;
      if (x < 0 || y < 0 || x >= this.def.w || y >= this.def.h) continue;
      if (!ex[y * this.def.w + x]) { ex[y * this.def.w + x] = 1; this.mini.reveal(x, y); }
    }
  }

  updateBarriers() {
    for (const b of this.def.barriers) {
      if (G.has(b.openFlag) && this.solid[b.ty * this.def.w + b.tx]) {
        for (let j = 0; j < b.h; j++) for (let i = 0; i < b.w; i++) {
          this.solid[(b.ty + j) * this.def.w + b.tx + i] = 0;
          this.burst((b.tx + i) * TS + 8, (b.ty + j) * TS + 8, 6, b.color, { speed: 60, life: 0.8, up: 20 });
        }
        Audio.sfx('slam'); this.addShake(6);
      }
    }
  }

  updateNpcs(dt: number) {
    for (const n of this.npcs) {
      n.anim += dt * 6;
      n.moving = false;
      if (n.tx !== null && n.ty !== null) {
        const dx = n.tx - n.x, dy = n.ty - n.y, d = Math.hypot(dx, dy);
        if (d < 1.5) { n.tx = n.ty = null; }
        else { n.vx = (dx / d) * 40; n.vy = (dy / d) * 40; n.dir = dirFromVec(dx, dy, n.dir); this.moveBody(n, n.vx * dt, n.vy * dt, true); n.moving = true; }
        continue;
      }
      if (n.def.wander) {
        n.wanderT -= dt;
        if (n.wanderT <= 0) {
          n.wanderT = 1.5 + Math.random() * 3;
          if (Math.random() < 0.6) { const a = Math.random() * Math.PI * 2; n.vx = Math.cos(a) * 18; n.vy = Math.sin(a) * 18; n.dir = dirFromVec(n.vx, n.vy); } else { n.vx = n.vy = 0; }
        }
        const nx = n.x + n.vx * dt, ny = n.y + n.vy * dt;
        if ((n.vx || n.vy) && this.boxFree(nx, ny, 4, 3) && dist(nx, ny, n.homeX, n.homeY) < 36 && dist(nx, ny, this.player.x, this.player.y) > 10) { n.x = nx; n.y = ny; n.moving = true; } else { n.vx *= 0.5; n.vy *= 0.5; }
      }
    }
  }

  updateAllies(dt: number) {
    const p = this.player;
    let prev: { x: number; y: number } = p;
    this.allies.forEach((a, i) => {
      a.anim += dt * 6;
      const d = dist(a.x, a.y, prev.x, prev.y);
      const want = 16 + i * 2;
      if (d > 120) { a.x = prev.x - 6; a.y = prev.y; }
      else if (d > want) {
        const dx = prev.x - a.x, dy = prev.y - a.y;
        const sp = Math.min(90, 40 + (d - want) * 3) * dt;
        this.moveBody(a, (dx / d) * sp, (dy / d) * sp);
        a.dir = dirFromVec(dx, dy, a.dir);
        a.vx = 1;
      } else a.vx = 0;
      prev = a;
      Combat.updateAlly(this, a, dt);
    });
  }

  updatePickups(dt: number) {
    const p = this.player;
    for (const k of this.pickups) {
      k.t += dt;
      if (k.z > 0 || k.vz > 0) { k.vz -= 320 * dt; k.z += k.vz * dt; if (k.z < 0) { k.z = 0; k.vz = k.vz < -40 ? -k.vz * 0.4 : 0; } k.x += k.vx * dt; k.y += k.vy * dt; k.vx *= 0.96; k.vy *= 0.96; }
      const d = dist(k.x, k.y, p.x, p.y - 6);
      if (k.t > 0.4 && d < 44) k.magnet = true;
      if (k.magnet) { const a = Math.atan2(p.y - 6 - k.y, p.x - k.x); k.x += Math.cos(a) * 140 * dt; k.y += Math.sin(a) * 140 * dt; }
      if (k.t > 0.35 && d < 9) { this.collect(k); k.dead = true; }
      if (k.t > 40) k.dead = true;
    }
    this.pickups = this.pickups.filter((k) => !k.dead);
  }

  collect(k: Pickup) {
    const s = G.stats();
    if (k.kind === 'gold') { G.gold += k.amount; Audio.sfx('coin'); this.text(this.player.x, this.player.y - 26, `+${k.amount}`, '#ffd84a'); }
    else if (k.kind === 'heart') { G.hp = Math.min(s.maxHp, G.hp + k.amount); Audio.sfx('pickup'); this.text(this.player.x, this.player.y - 26, `+${k.amount}`, '#6aff9a'); }
    else if (k.kind === 'mana') { G.mp = Math.min(s.maxMp, G.mp + k.amount); Audio.sfx('pickup'); this.text(this.player.x, this.player.y - 26, `+${k.amount} MP`, '#7ab8ff'); }
    else { G.addItem(k.id, k.amount); Audio.sfx('pickup'); this.toast(`${ITEMS[k.id]?.name ?? k.id}${k.amount > 1 ? ' x' + k.amount : ''}`, ITEMS[k.id]?.icon, '#fff'); this.script.onItem(k.id); }
  }

  // ---------------------------------------------------------------- interaction
  findInteractable() {
    const p = this.player;
    if (this.locked || p.state === 'dead') return null;
    const fv = DIR_VEC[p.dir];
    const fx = p.x + fv.x * 10, fy = p.y - 4 + fv.y * 8;
    let best: { x: number; y: number; kind: string; ref?: unknown } | null = null, bd = 26;
    for (const n of this.npcs) { const d = dist(fx, fy, n.x, n.y - 6); if (d < bd) { bd = d; best = { x: n.x, y: n.y - 26, kind: 'npc', ref: n }; } }
    for (const c of this.chests) { if (c.opened) continue; const d = dist(fx, fy, c.x, c.y - 6); if (d < bd) { bd = d; best = { x: c.x, y: c.y - 18, kind: 'chest', ref: c }; } }
    for (const s of this.def.signs) { const d = dist(fx, fy, s.tx * TS + 8, s.ty * TS + 8); if (d < Math.min(bd, 22)) { bd = d; best = { x: s.tx * TS + 8, y: s.ty * TS - 4, kind: 'sign', ref: s }; } }
    for (const o of this.objSorted) {
      if (o.type === 'save_crystal') { const d = dist(fx, fy, o.tx * TS + 8, o.ty * TS + 4); if (d < Math.min(bd, 30)) { bd = d; best = { x: o.tx * TS + 8, y: o.ty * TS - 30, kind: 'save', ref: o }; } }
      if (o.type === 'bookshelf' || o.type === 'well' || o.type === 'bed') { const d = dist(fx, fy, o.tx * TS + 16, o.ty * TS + 4); if (d < Math.min(bd, 22) && this.script.hasObjectTalk(o)) { bd = d; best = { x: o.tx * TS + 16, y: o.ty * TS - 24, kind: 'obj', ref: o }; } }
    }
    return best;
  }

  interact(t: NonNullable<World['nearTarget']>) {
    Input.consume('interact');
    if (t.kind === 'npc') { const n = t.ref as Npc; const p = this.player; n.dir = dirFromVec(p.x - n.x, p.y - n.y, n.dir); void this.script.run(() => n.def.talk(this.script.ctx)); }
    else if (t.kind === 'chest') void this.script.openChest(t.ref as ChestE);
    else if (t.kind === 'sign') { const s = t.ref as { text: string[] }; void this.script.run(async () => { for (const l of s.text) await this.script.ctx.say('', l); }); }
    else if (t.kind === 'save') void this.script.useSaveCrystal();
    else if (t.kind === 'obj') void this.script.run(() => this.script.objectTalk(t.ref as ObjPlace));
  }

  checkTriggers() {
    const p = this.player;
    const tx = Math.floor(p.x / TS), ty = Math.floor((p.y - 2) / TS);
    for (const w of this.def.warps) {
      if (tx >= w.tx && tx < w.tx + w.w && ty >= w.ty && ty < w.ty + w.h && !this.pendingWarp && !this.locked) {
        const block = w.need?.();
        if (block) { if (this.mapTimer > 0.6) { this.mapTimer = 0; void this.script.run(async () => { await this.script.ctx.say('', block); const wx = (w.tx + w.w / 2) * TS, wy = (w.ty + w.h / 2) * TS; const mx = this.def.w * TS / 2 - wx, my = this.def.h * TS / 2 - wy; const mm = Math.hypot(mx, my) || 1; p.x += (mx / mm) * 24; p.y += (my / mm) * 24; }); } continue; }
        Audio.sfx(this.def.indoor || w.dir === 'up' ? 'door' : 'pickup');
        this.warp(w.to, w.ntx, w.nty, w.dir);
        return;
      }
    }
    for (const tr of this.def.triggers) {
      if (this.locked) break;
      if (tx >= tr.tx && tx < tr.tx + tr.w && ty >= tr.ty && ty < tr.ty + tr.h) {
        if (tr.once && G.has('trg_' + tr.id)) continue;
        if (tr.cond && !tr.cond()) continue;
        if (tr.once) G.flags['trg_' + tr.id] = true;
        void this.script.run(() => tr.run(this.script.ctx));
        break;
      }
    }
  }

  async doWarp(pw: NonNullable<World['pendingWarp']>) {
    this.locked = true;
    await this.fade(1, 3.5);
    this.loadMap(pw.to, pw.tx, pw.ty, pw.dir ?? 'down');
    G.px = this.player.x; G.py = this.player.y;
    this.onWarped?.();
    this.locked = false;
    await this.fade(0, 3.5);
  }

  // ---------------------------------------------------------------- draw
  draw(g: CanvasRenderingContext2D) {
    const cx = Math.round(this.cam.x), cy = Math.round(this.cam.y);
    g.fillStyle = this.def.indoor ? '#0a0612' : '#05030a';
    g.fillRect(0, 0, VW, VH);
    // ground
    const sx = Math.max(0, cx), sy = Math.max(0, cy);
    const sw = Math.min(this.baked.canvas.width - sx, VW + Math.min(0, cx)), sh = Math.min(this.baked.canvas.height - sy, VH + Math.min(0, cy));
    if (sw > 0 && sh > 0) g.drawImage(this.baked.canvas, sx, sy, sw, sh, sx - cx, sy - cy, sw, sh);
    // animated water
    const fr = Math.floor(this.time * 3.5) % 4;
    const x0 = Math.floor(cx / TS) - 1, x1 = Math.ceil((cx + VW) / TS), y0 = Math.floor(cy / TS) - 1, y1 = Math.ceil((cy + VH) / TS);
    for (const w of this.baked.water) {
      if (w.x < x0 || w.x > x1 || w.y < y0 || w.y > y1) continue;
      // only draw the interior so baked edges are preserved
      g.drawImage(tileCanvas(w.deep ? T.DEEP : T.WATER, w.v, fr), 2, 2, 12, 12, w.x * TS + 2 - cx, w.y * TS + 2 - cy, 12, 12);
    }
    // barriers
    for (const b of this.def.barriers) if (!G.has(b.openFlag)) this.drawBarrier(g, b, cx, cy);
    // ground-level area effects (warnings)
    this.drawGroundFx(g, cx, cy);

    // y-sorted draw list
    type D = { y: number; fn: () => void };
    const list: D[] = [];
    const vis = (x: number, y: number, m = 40) => x > cx - m && x < cx + VW + m && y > cy - m - 60 && y < cy + VH + m + 20;
    const fi = Math.floor(this.time * 8);
    for (const o of this.objSorted) {
      if (o.px > cx + VW || o.px + o.def.w < cx || o.py > cy + VH || o.py + o.def.h < cy) continue;
      list.push({ y: o.sortY, fn: () => { g.drawImage(o.def.draw(fi % o.def.frames, o.v), Math.round(o.px - cx), Math.round(o.py - cy)); } });
    }
    for (const c of this.chests) list.push({ y: c.y, fn: () => { g.drawImage(chestCanvas(c.opened), Math.round(c.x - 8 - cx), Math.round(c.y - 15 - cy)); } });
    for (const n of this.npcs) if (vis(n.x, n.y)) list.push({ y: n.y, fn: () => this.drawNpc(g, n, cx, cy) });
    for (const a of this.allies) list.push({ y: a.y, fn: () => this.drawAlly(g, a, cx, cy) });
    for (const e of this.enemies) if (vis(e.x, e.y, 80)) list.push({ y: e.y, fn: () => this.drawEnemy(g, e, cx, cy) });
    list.push({ y: this.player.y, fn: () => Combat.drawPlayer(this, g, cx, cy) });
    for (const k of this.pickups) list.push({ y: k.y, fn: () => this.drawPickup(g, k, cx, cy) });
    list.sort((a, b) => a.y - b.y);
    for (const d of list) d.fn();

    Combat.drawProjectiles(this, g, cx, cy);
    this.drawAirFx(g, cx, cy);

    // particles
    for (const p of this.parts) {
      const a = p.fade ? Math.max(0, p.life / p.max) : 1;
      g.globalAlpha = a;
      g.fillStyle = p.color;
      const s = p.size * (0.5 + a * 0.5);
      g.fillRect(Math.round(p.x - cx - s / 2), Math.round(p.y - cy - s / 2), Math.max(1, Math.round(s)), Math.max(1, Math.round(s)));
    }
    g.globalAlpha = 1;
    this.drawLighting(g, cx, cy);
    this.drawAmbient(g);
    // interaction hint
    if (this.nearTarget && !this.locked) {
      const t = this.nearTarget;
      const bob = Math.round(Math.sin(this.time * 6) * 1.5);
      const x = Math.round(t.x - cx), y = Math.round(t.y - cy + bob);
      g.fillStyle = '#05020c'; g.fillRect(x - 6, y - 7, 12, 12);
      g.fillStyle = '#fff4c8'; g.fillRect(x - 5, y - 6, 10, 10);
      g.fillStyle = '#05020c'; g.fillRect(x - 1, y + 5, 3, 1);
      g.fillStyle = '#7a5a2a'; g.fillRect(x - 3, y - 4, 6, 1); g.fillRect(x - 3, y - 4, 1, 6); g.fillRect(x - 3, y - 1, 5, 1); g.fillRect(x - 3, y + 1, 6, 1);
    }
    // markers over NPCs
    for (const n of this.npcs) {
      const m = n.def.marker?.();
      if (m) { const bob = Math.round(Math.sin(this.time * 5 + n.x) * 1.5); const x = Math.round(n.x - cx), y = Math.round(n.y - 36 - cy + bob); g.fillStyle = '#05020c'; g.fillRect(x - 2, y - 1, 5, 9); g.fillStyle = m === '!' ? '#ffd84a' : '#7ad8ff'; g.fillRect(x - 1, y, 3, 5); g.fillRect(x - 1, y + 6, 3, 1); }
    }
  }

  drawBarrier(g: CanvasRenderingContext2D, b: MapDef['barriers'][0], cx: number, cy: number) {
    const x = b.tx * TS - cx, y = b.ty * TS - cy, w = b.w * TS, h = b.h * TS;
    const t = this.time;
    g.fillStyle = b.color; g.globalAlpha = 0.35 + Math.sin(t * 3) * 0.08; g.fillRect(x, y, w, h);
    g.globalAlpha = 0.9;
    for (let i = 0; i < w; i += 4) { const yy = ((i * 7 + t * 40) % h); g.fillStyle = '#ffffff'; g.fillRect(x + i, y + yy, 1, 3); }
    g.fillStyle = b.color; g.fillRect(x, y, 2, h); g.fillRect(x + w - 2, y, 2, h);
    g.globalAlpha = 1;
  }

  drawGroundFx(g: CanvasRenderingContext2D, cx: number, cy: number) {
    for (const a of this.areas) {
      if (a.kind === 'warn') {
        const f = a.t / a.dur;
        g.fillStyle = a.color; g.globalAlpha = 0.18 + 0.2 * Math.sin(this.time * 18) * Math.sin(this.time * 18) + f * 0.15;
        this.disc(g, a.x - cx, a.y - cy, a.r);
        g.globalAlpha = 0.9; g.strokeStyle = a.color; this.ring(g, a.x - cx, a.y - cy, a.r, a.color);
        g.globalAlpha = 0.5; this.disc(g, a.x - cx, a.y - cy, a.r * f);
        g.globalAlpha = 1;
      } else if (a.kind === 'slam' || a.kind === 'ring' || a.kind === 'nova') {
        const f = a.t / a.dur;
        g.globalAlpha = (1 - f) * 0.9;
        this.ring(g, a.x - cx, a.y - cy, a.r * (0.3 + f * 0.7), a.color);
        if (a.kind !== 'ring') this.ring(g, a.x - cx, a.y - cy, a.r * (0.15 + f * 0.6), '#ffffff');
        g.globalAlpha = (1 - f) * 0.25; g.fillStyle = a.color; this.disc(g, a.x - cx, a.y - cy, a.r * (0.3 + f * 0.7));
        g.globalAlpha = 1;
      }
    }
    for (const e of this.enemies) {
      const t = e.tele;
      if (!t) continue;
      const f = t.t / t.dur;
      g.fillStyle = '#ff3a4a';
      g.globalAlpha = 0.14 + 0.22 * f;
      if (t.kind === 'circle') { this.disc(g, t.x - cx, t.y - cy, t.r); g.globalAlpha = 0.8; this.ring(g, t.x - cx, t.y - cy, t.r, '#ff5a6a'); g.globalAlpha = 0.5; this.disc(g, t.x - cx, t.y - cy, t.r * f); }
      else if (t.kind === 'line') {
        const ang = t.ang ?? 0, len = t.len ?? 60;
        for (let i = 0; i < len; i += 2) { const px2 = t.x + Math.cos(ang) * i - cx, py2 = t.y + Math.sin(ang) * i - cy; g.fillRect(Math.round(px2 - t.r), Math.round(py2 - t.r), Math.round(t.r * 2), 2); }
      } else if (t.kind === 'cone') {
        const ang = t.ang ?? 0;
        for (let i = 6; i < t.r; i += 2) for (let a = -1; a <= 1; a += 0.12) { g.fillRect(Math.round(t.x + Math.cos(ang + a * 1.1) * i - cx), Math.round(t.y + Math.sin(ang + a * 1.1) * i - cy), 2, 2); }
      }
      g.globalAlpha = 1;
    }
  }
  disc(g: CanvasRenderingContext2D, x: number, y: number, r: number) {
    // squashed (isometric-ish) filled disc
    const ry = r * 0.62;
    for (let j = -Math.floor(ry); j <= ry; j++) { const w = Math.round(r * Math.sqrt(1 - (j * j) / (ry * ry))); g.fillRect(Math.round(x - w), Math.round(y + j), w * 2, 1); }
  }
  ring(g: CanvasRenderingContext2D, x: number, y: number, r: number, col: string) {
    g.fillStyle = col;
    const n = Math.max(12, Math.floor(r * 2.2));
    for (let i = 0; i < n; i++) { const a = (i / n) * Math.PI * 2; g.fillRect(Math.round(x + Math.cos(a) * r), Math.round(y + Math.sin(a) * r * 0.62), 1, 1); }
  }

  drawAirFx(g: CanvasRenderingContext2D, cx: number, cy: number) {
    for (const a of this.areas) {
      const f = a.t / a.dur;
      if (a.kind === 'meteor') {
        const fallT = Math.min(1, a.t / (a.dur * 0.8));
        if (fallT < 1) {
          const y = a.y - 140 * (1 - fallT), x = a.x - 60 * (1 - fallT);
          g.fillStyle = '#ff8a2a'; g.fillRect(Math.round(x - cx - 5), Math.round(y - cy - 5), 10, 10);
          g.fillStyle = '#ffd84a'; g.fillRect(Math.round(x - cx - 3), Math.round(y - cy - 3), 6, 6);
          g.fillStyle = '#fff'; g.fillRect(Math.round(x - cx - 1), Math.round(y - cy - 1), 3, 3);
          for (let i = 1; i < 8; i++) { g.globalAlpha = 1 - i / 8; g.fillStyle = i < 4 ? '#ff8a2a' : '#c0402a'; g.fillRect(Math.round(x + i * 4 - cx - 3), Math.round(y - i * 2.4 - cy - 3), 6 - i / 2, 6 - i / 2); }
          g.globalAlpha = 1;
        }
      } else if (a.kind === 'bolt' && a.pts) {
        g.globalAlpha = 1 - f;
        for (let k = 0; k < a.pts.length - 1; k++) {
          const [x0, y0] = a.pts[k], [x1, y1] = a.pts[k + 1];
          const n = Math.ceil(dist(x0, y0, x1, y1) / 3);
          let lx = x0, ly = y0;
          for (let i = 1; i <= n; i++) {
            const t = i / n; const nx = lerp(x0, x1, t) + (i < n ? (Math.random() - 0.5) * 8 : 0), ny = lerp(y0, y1, t) + (i < n ? (Math.random() - 0.5) * 8 : 0);
            this.lineTo(g, lx - cx, ly - cy, nx - cx, ny - cy, '#fff7a0'); this.lineTo(g, lx - cx + 1, ly - cy, nx - cx + 1, ny - cy, '#ffd84a');
            lx = nx; ly = ny;
          }
        }
        g.globalAlpha = 1;
      } else if (a.kind === 'spirits') {
        const n = 3;
        for (let i = 0; i < n; i++) {
          const ang = this.time * 3.2 + (i * Math.PI * 2) / n;
          const x = this.player.x + Math.cos(ang) * a.r - cx, y = this.player.y - 8 + Math.sin(ang) * a.r * 0.7 - cy;
          g.fillStyle = '#a0ffd8'; g.fillRect(Math.round(x - 3), Math.round(y - 3), 6, 6);
          g.fillStyle = '#ffffff'; g.fillRect(Math.round(x - 1), Math.round(y - 2), 2, 2);
          g.globalAlpha = 0.5; g.fillStyle = '#6affc0'; g.fillRect(Math.round(x - 5), Math.round(y - 1), 10, 2); g.fillRect(Math.round(x - 1), Math.round(y - 5), 2, 10); g.globalAlpha = 1;
        }
      }
    }
    for (const s of this.slashes) {
      const f = s.t / s.dur;
      const n = 22;
      for (let i = 0; i < n; i++) {
        const u = i / (n - 1);
        const a = s.ang - s.spread / 2 + s.spread * (f < 0.5 ? u * Math.min(1, f * 2.6) + 0 : u);
        const tail = Math.max(0, u - (f - 0.2) * 2);
        if (u < f * 1.2 - 0.25 || (f < 0.3 && u > f * 3.4)) continue;
        const fade = 1 - f;
        g.globalAlpha = Math.max(0, fade * (0.4 + tail * 0.6));
        for (let r = s.r - 3; r <= s.r + 1; r++) {
          g.fillStyle = r === s.r + 1 ? '#ffffff' : r === s.r ? s.color : '#ffffff55';
          g.fillRect(Math.round(s.x + Math.cos(a) * r - cx), Math.round(s.y + Math.sin(a) * r * 0.9 - cy), 1, 1);
        }
      }
      g.globalAlpha = 1;
    }
    for (const t of this.texts) {
      const f = t.t;
      const y = t.y - cy - f * 22 + (f < 0.12 ? -f * 40 : 0);
      g.save();
      g.globalAlpha = f > 0.7 ? 1 - (f - 0.7) / 0.3 : 1;
      this.pixText(g, t.str, Math.round(t.x - cx), Math.round(y), t.color, t.big);
      g.restore();
    }
  }

  pixText(g: CanvasRenderingContext2D, s: string, x: number, y: number, col: string, big: boolean) {
    // tiny bitmap-style numbers rendered with the UI font to a cached canvas
    const key = s + col + (big ? 'b' : '');
    let c = textCache.get(key);
    if (!c) {
      const sz = big ? 11 : 8;
      const [cv, cx] = mk(Math.ceil(measureText(s, sz)) + 4, sz + 4);
      cx.font = `700 ${sz}px "Pixelify Sans", monospace`; cx.textBaseline = 'top';
      cx.fillStyle = '#12081e';
      for (const [dx, dy] of [[0, 1], [1, 0], [2, 1], [1, 2], [0, 0], [2, 2], [0, 2], [2, 0]]) cx.fillText(s, 1 + dx, 1 + dy);
      cx.fillStyle = col; cx.fillText(s, 2, 2);
      c = cv; textCache.set(key, c);
    }
    g.drawImage(c, Math.round(x - c.width / 2), Math.round(y));
  }

  lineTo(g: CanvasRenderingContext2D, x0: number, y0: number, x1: number, y1: number, col: string) {
    g.fillStyle = col;
    const n = Math.max(Math.abs(x1 - x0), Math.abs(y1 - y0));
    for (let i = 0; i <= n; i++) g.fillRect(Math.round(lerp(x0, x1, i / (n || 1))), Math.round(lerp(y0, y1, i / (n || 1))), 1, 1);
  }

  drawNpc(g: CanvasRenderingContext2D, n: Npc, cx: number, cy: number) {
    drawShadow(g, n.x - cx, n.y - cy, 6);
    const frame = n.moving ? Math.floor(n.anim) % 4 : Math.floor(this.time * 1.5 + n.x) % 2;
    drawChar(g, n.sheet, n.moving ? 'walk' : 'idle', n.dir, frame, n.x - cx, n.y - cy);
  }
  drawAlly(g: CanvasRenderingContext2D, a: Ally, cx: number, cy: number) {
    drawShadow(g, a.x - cx, a.y - cy, 6);
    const moving = a.vx !== 0;
    const frame = moving ? Math.floor(a.anim) % 4 : Math.floor(this.time * 1.5) % 2;
    const anim = a.state === 'cast' ? 'cast' : moving ? 'walk' : 'idle';
    drawChar(g, a.sheet, anim, a.dir, a.state === 'cast' ? 0 : frame, a.x - cx, a.y - cy);
  }
  drawPickup(g: CanvasRenderingContext2D, k: Pickup, cx: number, cy: number) {
    const bob = k.z > 0 ? 0 : Math.sin(this.time * 5 + k.x) * 1.5;
    const x = Math.round(k.x - cx), y = Math.round(k.y - cy - k.z - 4 + bob);
    drawShadow(g, k.x - cx, k.y - cy, 3, 1.2, 0.3);
    if (k.kind === 'gold') { g.fillStyle = '#05020c'; g.fillRect(x - 3, y - 3, 6, 6); g.fillStyle = '#ffd84a'; g.fillRect(x - 2, y - 2, 4, 4); g.fillStyle = '#fff4a0'; g.fillRect(x - 2, y - 2, 2, 2); g.fillStyle = '#c0902a'; g.fillRect(x, y + 1, 2, 1); }
    else if (k.kind === 'heart') { g.fillStyle = '#05020c'; g.fillRect(x - 4, y - 3, 8, 7); g.fillStyle = '#ff4a6a'; g.fillRect(x - 3, y - 2, 3, 3); g.fillRect(x + 1, y - 2, 3, 3); g.fillRect(x - 2, y, 5, 2); g.fillRect(x - 1, y + 2, 3, 1); g.fillStyle = '#fff'; g.fillRect(x - 2, y - 2, 1, 1); }
    else if (k.kind === 'mana') { g.fillStyle = '#05020c'; g.fillRect(x - 3, y - 4, 6, 8); g.fillStyle = '#5a9aff'; g.fillRect(x - 2, y - 3, 4, 6); g.fillStyle = '#c0e0ff'; g.fillRect(x - 2, y - 3, 2, 2); }
    else { const ic = iconFor(k.id); g.drawImage(ic, x - 9, y - 12); }
  }

  drawEnemy(g: CanvasRenderingContext2D, e: Enemy, cx: number, cy: number) {
    const art = e.art;
    const frameIdx = Math.floor(e.anim) % art.frames.length;
    const atkPose = e.state === 'tele' || e.state === 'atk';
    let spr = atkPose && e.def.ai !== 'hop' ? art.atk : art.frames[frameIdx];
    let fl = e.flash > 0 || e.state === 'dying';
    if (e.def.ai === 'hop' && e.state === 'tele') spr = art.frames[1];
    const faceLeft = e.face < 0;
    const flip = art.faces === 'right' ? faceLeft : false;
    if (e.freeze > 0) fl = false;
    const bx = Math.round(e.x - cx - art.w / 2), by = Math.round(e.y - cy - art.h + 2 - e.z + (e.def.fly ? -8 + Math.sin(e.anim * 1.5) * 2 : 0));
    drawShadow(g, e.x - cx, e.y - cy + 1, Math.min(14, e.def.radius * 0.9), 2.5, e.def.fly ? 0.18 : 0.28);
    const sh = e.state === 'tele' ? (Math.random() < 0.5 ? 1 : -1) : 0;
    const alpha = e.state === 'dying' ? Math.max(0, 1 - e.deathT / 0.5) : 1;
    g.globalAlpha = alpha;
    if (flip) g.drawImage(flipped(spr), bx + sh, by); else g.drawImage(spr, bx + sh, by);
    if (fl) {
      const f = art.flash[art.frames.indexOf(spr) >= 0 ? art.frames.indexOf(spr) : 0];
      g.globalAlpha = alpha * (e.state === 'dying' ? 0.8 : 0.85);
      g.drawImage(flip ? flipped(f) : f, bx + sh, by);
    }
    if (e.state === 'tele') {
      g.globalAlpha = 0.35 + 0.25 * Math.sin(this.time * 30);
      g.fillStyle = '#ff2a3a';
      g.drawImage(tintRed(flip ? flipped(spr) : spr), bx + sh, by);
    }
    if (e.freeze > 0) { g.globalAlpha = 0.55; g.drawImage(tintBlue(flip ? flipped(spr) : spr), bx, by); }
    g.globalAlpha = 1;
    if (e.burn > 0 && Math.random() < 0.3) this.parts.push({ x: e.x + (Math.random() - 0.5) * 8, y: e.y - 8, vx: 0, vy: -20, life: 0.4, max: 0.4, color: Math.random() < 0.5 ? '#ff8a2a' : '#ffd84a', size: 2, grav: 0, fade: true });
    // hp bar for regular enemies once hurt
    if (!e.def.boss && e.hp < e.maxHp && e.state !== 'dying') {
      const w = 18, x = Math.round(e.x - cx - w / 2), y = Math.round(e.y - cy - art.h - 2 - e.z + (e.def.fly ? -8 : 0));
      g.fillStyle = '#05020c'; g.fillRect(x - 1, y - 1, w + 2, 4);
      g.fillStyle = '#4a1a2a'; g.fillRect(x, y, w, 2);
      g.fillStyle = '#ff5a6a'; g.fillRect(x, y, Math.max(1, Math.round((w * e.hp) / e.maxHp)), 2);
    }
  }

  drawLighting(g: CanvasRenderingContext2D, cx: number, cy: number) {
    const dark = this.def.dark;
    if (!dark && !this.def.tint) return;
    if (this.def.tint) { g.globalCompositeOperation = 'multiply'; g.fillStyle = this.def.tint; g.fillRect(0, 0, VW, VH); g.globalCompositeOperation = 'source-over'; }
    if (!dark) return;
    if (!lightCanvas) { [lightCanvas, lightCtx] = mk(VW, VH); }
    const lc = lightCtx!;
    lc.globalCompositeOperation = 'source-over';
    lc.clearRect(0, 0, VW, VH);
    lc.fillStyle = `rgba(6,3,20,${dark})`;
    lc.fillRect(0, 0, VW, VH);
    lc.globalCompositeOperation = 'destination-out';
    const carve = (x: number, y: number, r: number) => {
      const steps = 6;
      for (let i = 0; i < steps; i++) {
        const rr = r * (1 - i / steps * 0.8);
        lc.globalAlpha = (1 / steps) * 0.95 + (i === steps - 1 ? 0.1 : 0);
        lc.beginPath(); lc.ellipse(Math.round(x), Math.round(y), rr, rr * 0.85, 0, 0, Math.PI * 2); lc.fill();
      }
    };
    lc.fillStyle = '#000';
    const p = this.player;
    carve(p.x - cx, p.y - 10 - cy, 78 + (p.buffT > 0 ? 10 : 0));
    for (const l of this.lights) { const fl = l.flicker ? Math.sin(this.time * 12 + l.x) * 3 : 0; carve(l.x - cx, l.y - cy, l.r + fl); }
    for (const pr of this.projs) if (pr.kind === 'fire' || pr.kind === 'bolt') carve(pr.x - cx, pr.y - cy - (pr.opts.z ?? 0), 28);
    for (const a of this.areas) if (a.kind === 'meteor' || a.kind === 'nova' || a.kind === 'slam') carve(a.x - cx, a.y - cy, 30 + a.r * 0.5);
    lc.globalAlpha = 1; lc.globalCompositeOperation = 'source-over';
    g.drawImage(lightCanvas, 0, 0);
    // coloured glow
    g.globalCompositeOperation = 'lighter';
    for (const l of this.lights) {
      const fl = l.flicker ? 0.05 * Math.sin(this.time * 14 + l.x) : 0;
      g.globalAlpha = 0.16 + fl; g.fillStyle = l.color;
      g.beginPath(); g.ellipse(Math.round(l.x - cx), Math.round(l.y - cy), l.r * 0.5, l.r * 0.42, 0, 0, Math.PI * 2); g.fill();
      g.globalAlpha = 0.12; g.beginPath(); g.ellipse(Math.round(l.x - cx), Math.round(l.y - cy), l.r * 0.25, l.r * 0.2, 0, 0, Math.PI * 2); g.fill();
    }
    g.globalAlpha = 1; g.globalCompositeOperation = 'source-over';
  }

  drawAmbient(g: CanvasRenderingContext2D) {
    const amb = this.def.ambient;
    if (amb === 'none') return;
    for (const p of this.ambientParts) {
      const x = Math.round(p.x), y = Math.round(p.y);
      if (amb === 'fireflies') { const a = 0.5 + 0.5 * Math.sin(this.time * 2 + p.ph * 3); g.globalAlpha = a; g.fillStyle = '#e8ff7a'; g.fillRect(x, y, 2, 2); g.globalAlpha = a * 0.3; g.fillRect(x - 1, y - 1, 4, 4); }
      else if (amb === 'leaves') { g.globalAlpha = 0.85; g.fillStyle = p.ph > 3.5 ? '#e8a23a' : '#6fbf4a'; g.fillRect(x, y, 2, 1); g.fillRect(x + 1, y + 1, 1, 1); }
      else if (amb === 'dust') { g.globalAlpha = 0.35 + 0.25 * Math.sin(this.time + p.ph); g.fillStyle = '#9ab8ff'; g.fillRect(x, y, 1, 1); }
      else if (amb === 'snow') { g.globalAlpha = 0.9; g.fillStyle = '#fff'; g.fillRect(x, y, p.s > 1 ? 2 : 1, p.s > 1 ? 2 : 1); }
      else if (amb === 'sand') { g.globalAlpha = 0.4; g.fillStyle = '#f2d89a'; g.fillRect(x, y, 2, 1); }
      else if (amb === 'embers') { g.globalAlpha = 0.8; g.fillStyle = '#ff8a2a'; g.fillRect(x, y, 1, 2); }
    }
    g.globalAlpha = 1;
  }

  // ---------------------------------------------------------------- UI pass
  drawUI(u: CanvasRenderingContext2D) {
    if (!this.def) return;
    const hide = this.modals.some((m) => (m as unknown as { hideHud?: boolean }).hideHud);
    if (!hide && this.lbAmt < 0.5) drawHud(this, u);
    if (this.lbAmt > 0.01) { const h = Math.round(22 * this.lbAmt); u.fillStyle = '#000'; u.fillRect(0, 0, VW, h); u.fillRect(0, VH - h, VW, h); }
    for (const m of this.modals) m.drawUI(u);
    if (this.fadeA > 0.002) { u.globalAlpha = this.fadeA; u.fillStyle = this.fadeColor; u.fillRect(-2, -2, VW + 4, VH + 4); u.globalAlpha = 1; }
    if (this.chapterText) {
      const c = this.chapterText, a = c.t < 1 ? c.t : c.t > 5 ? Math.max(0, 6 - c.t) : 1;
      u.fillStyle = `rgba(4,2,12,${0.92 * a})`; u.fillRect(0, 0, VW, VH);
      u.globalAlpha = a;
      text(u, c.title, VW / 2, 80, { size: 18, align: 'center', color: '#fff4c8', bold: true });
      u.fillStyle = '#e8c872'; u.fillRect(VW / 2 - 70, 106, 140, 1);
      text(u, c.sub, VW / 2, 114, { size: 9, align: 'center', color: '#c8c0e8' });
      u.globalAlpha = 1;
    }
  }
}

function measureText(s: string, sz: number) { const c = document.createElement('canvas').getContext('2d')!; c.font = `700 ${sz}px "Pixelify Sans", monospace`; return c.measureText(s).width; }
const textCache = new Map<string, HTMLCanvasElement>();
let lightCanvas: HTMLCanvasElement | null = null;
let lightCtx: CanvasRenderingContext2D | null = null;

const iconCache = new Map<string, HTMLCanvasElement>();
import { icon } from '../../art/icons';
function iconFor(id: string) { let c = iconCache.get(id); if (!c) { c = icon(ITEMS[id]?.icon ?? 'gem'); iconCache.set(id, c); } return c; }

const redCache = new WeakMap<HTMLCanvasElement, HTMLCanvasElement>();
function tintRed(src: HTMLCanvasElement) { let c = redCache.get(src); if (!c) { const [cv, x] = mk(src.width, src.height); x.drawImage(src, 0, 0); x.globalCompositeOperation = 'source-atop'; x.fillStyle = '#ff2a3a'; x.fillRect(0, 0, cv.width, cv.height); c = cv; redCache.set(src, c); } return c; }
const blueCache = new WeakMap<HTMLCanvasElement, HTMLCanvasElement>();
function tintBlue(src: HTMLCanvasElement) { let c = blueCache.get(src); if (!c) { const [cv, x] = mk(src.width, src.height); x.drawImage(src, 0, 0); x.globalCompositeOperation = 'source-atop'; x.fillStyle = '#9ae8ff'; x.fillRect(0, 0, cv.width, cv.height); c = cv; blueCache.set(src, c); } return c; }
void monsterArt; void text; void panel; void bar; void measure; void wrap; void Rng;
