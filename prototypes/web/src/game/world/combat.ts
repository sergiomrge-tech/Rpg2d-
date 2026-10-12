import { Input } from '../../engine/input';
import { Audio } from '../../engine/audio';
import { clamp, dist, DIR_VEC, dirFromVec, Dir } from '../../engine/util';
import { G, xpToNext } from '../state';
import { SKILL_MAP, rankPower, rankCost, rankCd, SkillDef, Elem } from '../data/skills';
import { ITEMS } from '../data/items';
import { Enemy, Proj, Ally, drawShadow, drawChar, AreaFx } from '../entities';
import type { World } from './world';
import { TS } from '../../art/tiles';

const ELEM_COL: Record<Elem, string> = { phys: '#ffffff', fire: '#ff8a2a', ice: '#9ae8ff', bolt: '#ffe84a', holy: '#fff2b0', dark: '#c080ff' };
const ELEM_TXT: Record<Elem, string> = { phys: '#ffffff', fire: '#ffb060', ice: '#a8f0ff', bolt: '#fff070', holy: '#fff6c0', dark: '#d8a8ff' };

// ------------------------------------------------------------------ damage helpers
export interface HitOpts { elem?: Elem; kb?: number; stun?: number; slow?: number; burn?: number; freeze?: number; noCrit?: boolean; src?: { x: number; y: number }; heavy?: boolean; silent?: boolean; dot?: boolean }

export function damageEnemy(w: World, e: Enemy, raw: number, o: HitOpts = {}): number {
  if (e.state === 'dying' || e.dead) return 0;
  const st = G.stats();
  const elem = o.elem ?? 'phys';
  let dmg = raw * (0.92 + Math.random() * 0.16) - e.def.def * 0.5;
  let tag = '';
  if (e.def.weak?.includes(elem)) { dmg *= 1.5; tag = '!'; }
  if (e.def.resist?.includes(elem)) { dmg *= 0.6; tag = '-'; }
  const crit = !o.noCrit && Math.random() * 100 < st.crit;
  if (crit) dmg *= 1.6;
  dmg = Math.max(1, Math.round(dmg));
  e.hp -= dmg;
  e.flash = 0.1;
  e.aggro = true;
  if (!e.def.boss || o.stun) { /* bosses resist stun */ }
  if (o.stun && !e.def.boss) { e.stun = Math.max(e.stun, o.stun); e.state = 'stun'; e.tele = null; e.t = 0; }
  if (o.freeze && !e.def.boss) { e.freeze = Math.max(e.freeze, o.freeze); e.stun = Math.max(e.stun, o.freeze); e.state = 'stun'; e.tele = null; }
  if (o.slow) e.slow = Math.max(e.slow, o.slow);
  if (o.burn) { e.burn = Math.max(e.burn, o.burn); e.burnDmg = Math.max(e.burnDmg, Math.round(raw * 0.12)); }
  if (o.kb && !e.def.boss && e.state !== 'tele') {
    const sx = o.src?.x ?? w.player.x, sy = o.src?.y ?? w.player.y;
    const a = Math.atan2(e.y - sy, e.x - sx);
    e.kx = Math.cos(a) * o.kb; e.ky = Math.sin(a) * o.kb;
    if (e.state === 'atk' || e.state === 'rec') { /* interrupt */ }
  }
  const tc = crit ? '#ffd84a' : ELEM_TXT[elem];
  w.text(e.x + (Math.random() - 0.5) * 6, e.y - e.def.hitH - 8, `${dmg}${tag}${crit ? '!' : ''}`, tc, !o.dot && (crit || tag === '!'));
  if (!o.dot) {
    w.burst(e.x, e.y - e.def.hitH, crit ? 9 : 5, [ELEM_COL[elem], '#ffffff'], { speed: crit ? 90 : 60, life: 0.3, size: 2 });
    if (!o.silent) Audio.sfx(crit ? 'crit' : 'hit');
    w.hitstop = Math.max(w.hitstop, o.heavy || crit ? 0.07 : 0.035);
    w.addShake(crit || o.heavy ? 3 : 1.2);
  } else e.flash = 0.05;
  w.combatT = 0;
  if (e.def.boss) w.bossBar = e;
  if (e.hp <= 0) killEnemy(w, e);
  return dmg;
}

export function killEnemy(w: World, e: Enemy) {
  if (e.state === 'dying') return;
  e.state = 'dying'; e.deathT = 0; e.tele = null; e.hp = 0;
  Audio.sfx('die');
  w.burst(e.x, e.y - e.def.hitH, 14, ['#ffffff', ELEM_COL[e.def.elem ?? 'phys'], '#ffd84a'], { speed: 80, life: 0.6, size: 2 });
  G.kills++;
  if (!e.summoned) {
    const lf = clamp(1 - (G.level - e.def.level) * 0.12, 0.15, 1.3);
    const xp = Math.max(1, Math.round(e.def.xp * lf));
    const gained = G.gainXp(xp);
    w.text(e.x, e.y - e.def.hitH - 20, `+${xp} XP`, '#9ad8ff');
    if (gained) levelUpFx(w);
    const gold = Math.round(e.def.gold[0] + Math.random() * (e.def.gold[1] - e.def.gold[0]));
    const bags = e.def.boss ? 8 : Math.min(3, 1 + Math.floor(gold / 12));
    for (let i = 0; i < bags; i++) w.drop(e.x, e.y - 4, 'gold', 'gold', Math.max(1, Math.round(gold / bags)));
    for (const d of e.def.drops) if (Math.random() < d.chance) w.drop(e.x, e.y - 4, 'item', d.id, 1);
    if (Math.random() < 0.1) w.drop(e.x, e.y - 4, 'heart', 'heart', 18 + G.level * 2);
    if (Math.random() < 0.07) w.drop(e.x, e.y - 4, 'mana', 'mana', 10 + G.level);
  }
  w.script.onKill(e);
  if (e.def.boss) { w.addShake(8); w.hitstop = 0.25; w.burst(e.x, e.y - 10, 40, ['#fff', '#ffd84a'], { speed: 150, life: 1.0, size: 3 }); }
}

export function levelUpFx(w: World) {
  Audio.sfx('levelup');
  const p = w.player;
  w.areas.push({ kind: 'nova', x: p.x, y: p.y, r: 60, t: 0, dur: 0.8, color: '#ffe066' });
  w.burst(p.x, p.y - 10, 30, ['#ffe066', '#fff'], { speed: 90, life: 0.9, size: 2, up: 40 });
  w.banner = { text: `NÍVEL ${G.level}!`, sub: '+1 ponto de habilidade  ·  HP e MP restaurados', t: 0 };
  w.toast(`Você alcançou o nível ${G.level}!`, 'star', '#ffe066');
}

export function hurtPlayer(w: World, amount: number, sx: number, sy: number, kb = 70, elem: Elem = 'phys'): boolean {
  const p = w.player;
  if (p.state === 'dead' || p.invuln > 0 || p.state === 'roll' || p.state === 'phase' || w.locked) return false;
  const st = G.stats();
  let dmg = Math.max(1, Math.round((amount * (0.92 + Math.random() * 0.16)) - st.def * 0.6));
  if (p.shield > 0) {
    const ab = Math.min(p.shield, dmg);
    p.shield -= ab; dmg -= ab;
    w.text(p.x, p.y - 28, `-${ab}`, '#9ad8ff');
    Audio.sfx('shield');
    w.burst(p.x, p.y - 10, 8, '#9ad8ff', { speed: 60, life: 0.3 });
    if (dmg <= 0) { p.invuln = 0.3; return false; }
  }
  G.hp -= dmg;
  p.invuln = 0.9; p.flash = 0.15;
  p.hurtT = 0.2;
  w.text(p.x, p.y - 28, `-${dmg}`, '#ff6a7a', true);
  w.burst(p.x, p.y - 10, 8, ['#ff5a6a', '#fff'], { speed: 70, life: 0.35, size: 2 });
  Audio.sfx('hurt');
  w.addShake(4); w.hitstop = 0.06; w.combatT = 0;
  const a = Math.atan2(p.y - sy, p.x - sx);
  p.vx = Math.cos(a) * kb; p.vy = Math.sin(a) * kb;
  if (p.state !== 'attack' || dmg > st.maxHp * 0.12) { p.state = 'hurt'; p.t = 0; p.combo = 0; }
  void elem;
  if (G.hp <= 0) { G.hp = 0; p.state = 'dead'; p.t = 0; Audio.sfx('die'); Audio.music(''); }
  return true;
}

// ------------------------------------------------------------------ targeting
function nearestEnemy(w: World, x: number, y: number, range: number, filter?: (e: Enemy) => boolean): Enemy | null {
  let best: Enemy | null = null, bd = range;
  for (const e of w.enemies) {
    if (e.state === 'dying' || e.dead || (filter && !filter(e))) continue;
    const d = dist(x, y, e.x, e.y - e.def.hitH * 0.6) - e.def.radius * 0.5;
    if (d < bd) { bd = d; best = e; }
  }
  return best;
}

function aimAngle(w: World, range = 110): number {
  const p = w.player;
  const f = DIR_VEC[p.dir];
  const facing = Math.atan2(f.y, f.x);
  const ax = Input.axis();
  const useInput = ax.x !== 0 || ax.y !== 0;
  const base = useInput ? Math.atan2(ax.y, ax.x) : facing;
  let best: Enemy | null = null, bs = 1e9;
  for (const e of w.enemies) {
    if (e.state === 'dying') continue;
    const dx = e.x - p.x, dy = e.y - e.def.hitH * 0.5 - (p.y - 8);
    const d = Math.hypot(dx, dy);
    if (d > range) continue;
    let da = Math.abs(Math.atan2(dy, dx) - base);
    if (da > Math.PI) da = Math.PI * 2 - da;
    if (da > 1.0) continue;
    const s = d + da * 40;
    if (s < bs) { bs = s; best = e; }
  }
  if (best) return Math.atan2(best.y - best.def.hitH * 0.5 - (p.y - 8), best.x - p.x);
  return base;
}

// ------------------------------------------------------------------ player
const ATK_DUR = [0.26, 0.26, 0.44];
const ATK_MULT = [1.0, 1.1, 1.65];

export function updatePlayer(w: World, dt: number) {
  const p = w.player;
  const st = G.stats();
  p.invuln = Math.max(0, p.invuln - dt);
  p.flash = Math.max(0, p.flash - dt);
  p.rollCd = Math.max(0, p.rollCd - dt);
  p.gcd = Math.max(0, p.gcd - dt);
  p.comboWindow = Math.max(0, p.comboWindow - dt);
  p.buffT = Math.max(0, p.buffT - dt); if (p.buffT === 0) p.buffMul = 1;
  p.shieldT = Math.max(0, p.shieldT - dt); if (p.shieldT === 0) p.shield = 0;
  p.slowT = Math.max(0, p.slowT - dt);
  for (let i = 0; i < 4; i++) p.cd[i] = Math.max(0, p.cd[i] - dt);
  p.hurtT = Math.max(0, p.hurtT - dt);
  p.t += dt;
  if (G.hp > st.maxHp) G.hp = st.maxHp;
  if (G.mp > st.maxMp) G.mp = st.maxMp;
  if (p.state !== 'dead') {
    G.mp = Math.min(st.maxMp, G.mp + dt * (1.6 + st.maxMp * 0.012));
    if (w.combatT > 5 && G.hp < st.maxHp) G.hp = Math.min(st.maxHp, G.hp + dt * st.maxHp * 0.008);
  }

  if (p.state === 'dead') {
    p.vx *= 0.9; p.vy *= 0.9;
    if (p.t > 1.6 && !w.modals.length) w.onGameOver?.();
    return;
  }
  if (w.locked) { p.vx = p.vy = 0; if ((p.state as string) === 'walk') p.state = 'idle'; if ((p.state as string) === 'idle' || (p.state as string) === 'walk') p.anim += dt * 2; return; }

  const ax = Input.axis();
  const moving = ax.x !== 0 || ax.y !== 0;
  const baseSpd = 62 * st.spd * (p.slowT > 0 ? 0.6 : 1);

  switch (p.state) {
    case 'idle': case 'walk': {
      p.state = moving ? 'walk' : 'idle';
      if (moving) {
        p.dir = dirFromVec(ax.x, ax.y, p.dir);
        w.moveBody(p, ax.x * baseSpd * dt, ax.y * baseSpd * dt);
        p.anim += dt * 8.5;
        if (Math.floor(p.anim) % 4 === 1 && Math.random() < 0.05) w.burst(p.x, p.y, 1, '#c0b090', { speed: 10, life: 0.3 });
      } else p.anim += dt * 2;
      // knockback residual
      if (Math.abs(p.vx) + Math.abs(p.vy) > 2) { w.moveBody(p, p.vx * dt, p.vy * dt); p.vx *= 0.85; p.vy *= 0.85; }
      if (Input.buffered('attack', 0.12) && p.gcd <= 0) { Input.consume('attack'); startAttack(w); break; }
      if (Input.buffered('dodge', 0.12) && p.rollCd <= 0) { Input.consume('dodge'); startRoll(w, ax); break; }
      for (let i = 0; i < 4; i++) {
        const a = (['skill1', 'skill2', 'skill3', 'skill4'] as const)[i];
        if (Input.buffered(a, 0.1)) { Input.consume(a); if (castSlot(w, i)) break; }
      }
      if (Input.pressed('tabL')) quickUse(w, 'potion');
      if (Input.pressed('tabR')) quickUse(w, 'ether');
      break;
    }
    case 'attack': {
      const dur = ATK_DUR[p.combo - 1];
      const v = DIR_VEC[p.dir];
      if (p.t < dur * 0.45) w.moveBody(p, v.x * 55 * dt * (p.combo === 3 ? 1.4 : 1), v.y * 55 * dt * (p.combo === 3 ? 1.4 : 1));
      if (!p.swingDone && p.t >= dur * 0.28) { p.swingDone = true; swingHit(w); }
      if (Input.buffered('attack', 0.2) && p.t > dur * 0.4) p.queued = true;
      if (Input.buffered('dodge', 0.12) && p.rollCd <= 0 && p.t > dur * 0.5) { Input.consume('dodge'); startRoll(w, ax); break; }
      if (p.t >= dur) {
        p.state = 'idle';
        p.comboWindow = 0.28;
        if (p.queued && p.combo < 3) { p.queued = false; Input.consume('attack'); startAttack(w); }
        else { if (p.combo >= 3) { p.combo = 0; p.gcd = 0.12; } p.queued = false; }
      }
      break;
    }
    case 'roll': {
      const sp = 150;
      w.moveBody(p, p.rollDx * sp * dt, p.rollDy * sp * dt);
      if (Math.random() < 0.5) w.parts.push({ x: p.x, y: p.y - 2, vx: 0, vy: 0, life: 0.25, max: 0.25, color: '#c8c0e8', size: 2, grav: 0, fade: true });
      if (p.t >= 0.28) { p.state = 'idle'; p.invuln = Math.max(p.invuln, 0.1); }
      break;
    }
    case 'cast': {
      w.moveBody(p, ax.x * baseSpd * 0.3 * dt, ax.y * baseSpd * 0.3 * dt);
      if (p.t >= p.castT) p.state = 'idle';
      break;
    }
    case 'hurt': {
      w.moveBody(p, p.vx * dt, p.vy * dt); p.vx *= 0.88; p.vy *= 0.88;
      if (p.t >= 0.2) p.state = 'idle';
      break;
    }
    case 'phase': {
      if (p.t >= p.phaseT) p.state = 'idle';
      break;
    }
  }
}

function startAttack(w: World) {
  const p = w.player;
  p.combo = p.comboWindow > 0 && p.combo < 3 && p.combo > 0 ? p.combo + 1 : p.combo >= 3 || p.combo === 0 ? 1 : p.combo + 1;
  p.state = 'attack'; p.t = 0; p.swingDone = false; p.queued = false; p.hitSet.clear();
  const ang = aimAngle(w, 60);
  p.dir = dirFromVec(Math.cos(ang), Math.sin(ang), p.dir);
  p.rollDx = Math.cos(ang); p.rollDy = Math.sin(ang);
  Audio.sfx('swing');
}

function swingHit(w: World) {
  const p = w.player;
  const st = G.stats();
  const ang = Math.atan2(p.rollDy, p.rollDx);
  const reach = p.combo === 3 ? 30 : 24;
  const spread = p.combo === 3 ? 2.6 : 2.0;
  const cx = p.x + Math.cos(ang) * 6, cy = p.y - 8 + Math.sin(ang) * 6;
  w.slashes.push({ x: p.x, y: p.y - 8, ang, t: 0, dur: 0.2, r: reach - 2, spread, color: p.combo === 3 ? '#ffd84a' : '#bfe4ff' });
  let hit = false;
  for (const e of w.enemies) {
    if (e.state === 'dying') continue;
    const ex = e.x - cx, ey = e.y - e.def.hitH * 0.6 - cy;
    const d = Math.hypot(ex, ey);
    if (d > reach + e.def.radius) continue;
    let da = Math.abs(Math.atan2(ey, ex) - ang); if (da > Math.PI) da = Math.PI * 2 - da;
    if (d > e.def.radius + 8 && da > spread / 2) continue;
    if (p.hitSet.has(e)) continue;
    p.hitSet.add(e);
    damageEnemy(w, e, st.atk * ATK_MULT[p.combo - 1] * p.buffMul, { kb: p.combo === 3 ? 150 : 90, heavy: p.combo === 3, src: p });
    hit = true;
  }
  // break nothing else for now
  if (hit && p.combo === 3) w.addShake(3);
}

function startRoll(w: World, ax: { x: number; y: number }) {
  const p = w.player;
  const v = ax.x || ax.y ? { x: ax.x, y: ax.y } : DIR_VEC[p.dir];
  const m = Math.hypot(v.x, v.y) || 1;
  p.rollDx = v.x / m; p.rollDy = v.y / m;
  p.state = 'roll'; p.t = 0; p.invuln = 0.34; p.rollCd = 0.6; p.combo = 0;
  p.dir = dirFromVec(p.rollDx, p.rollDy, p.dir);
  Audio.sfx('dodge');
  w.burst(p.x, p.y, 6, '#c8c0e8', { speed: 40, life: 0.3 });
}

function quickUse(w: World, kind: 'potion' | 'ether') {
  const ids = kind === 'potion' ? ['potion', 'hi_potion', 'herb'] : ['ether', 'hi_ether'];
  const id = ids.find((i) => G.count(i) > 0);
  if (!id) { Audio.sfx('error'); w.toast(kind === 'potion' ? 'Sem poções!' : 'Sem éteres!', undefined, '#ff8a8a'); return; }
  useItem(w, id);
}

export function useItem(w: World, id: string): boolean {
  const it = ITEMS[id];
  if (!it || it.type !== 'consumable' || G.count(id) <= 0) return false;
  const st = G.stats();
  const h = it.heal ?? {};
  if (h.hp && G.hp >= st.maxHp && !h.mp) { Audio.sfx('error'); return false; }
  if (h.mp && !h.hp && G.mp >= st.maxMp) { Audio.sfx('error'); return false; }
  G.addItem(id, -1);
  const p = w.player;
  if (h.hp) { const amt = h.pct ? st.maxHp : h.hp; const before = G.hp; G.hp = Math.min(st.maxHp, G.hp + amt); w.text(p.x, p.y - 28, `+${Math.round(G.hp - before)}`, '#6aff9a', true); }
  if (h.mp) { const amt = h.pct ? st.maxMp : h.mp; const before = G.mp; G.mp = Math.min(st.maxMp, G.mp + amt); w.text(p.x + 8, p.y - 36, `+${Math.round(G.mp - before)} MP`, '#7ab8ff'); }
  Audio.sfx('heal');
  w.burst(p.x, p.y - 10, 10, h.hp ? ['#6aff9a', '#fff'] : ['#7ab8ff', '#fff'], { speed: 40, life: 0.6, up: 30 });
  return true;
}

// ------------------------------------------------------------------ skills
function castSlot(w: World, slot: number): boolean {
  const p = w.player;
  const id = G.slots[slot];
  if (!id) return false;
  const def = SKILL_MAP[id];
  const rank = G.skillRank(id);
  if (!def || rank < 1) return false;
  if (p.cd[slot] > 0) { return false; }
  const cost = rankCost(def, rank);
  if (G.mp < cost) { Audio.sfx('error'); w.toast('MP insuficiente!', undefined, '#8ab8ff'); return false; }
  const ok = castSkill(w, def, rank);
  if (!ok) return false;
  G.mp -= cost;
  p.cd[slot] = rankCd(def, rank);
  w.combatT = 0;
  return true;
}

function skillBase(def: SkillDef, rank: number) {
  const st = G.stats();
  const p = def.scale === 'atk' ? st.atk : st.mag;
  return p * rankPower(def, rank);
}

function castSkill(w: World, def: SkillDef, rank: number): boolean {
  const p = w.player;
  const base = skillBase(def, rank) * p.buffMul;
  const ang = aimAngle(w, 150);
  const dirv = { x: Math.cos(ang), y: Math.sin(ang) };
  const setCast = (t: number) => { p.state = 'cast'; p.t = 0; p.castT = t; p.dir = dirFromVec(dirv.x, dirv.y, p.dir); p.combo = 0; };
  const ox = p.x, oy = p.y - 8;
  switch (def.kind) {
    case 'wave': {
      setCast(0.22); Audio.sfx('swing');
      const pr = new Proj(ox + dirv.x * 10, oy + dirv.y * 10, dirv.x * 170, dirv.y * 170, 'p', base, 'wave', { r: 9, life: 0.55, pierce: 99, elem: 'phys', kb: 90, color: '#bfe4ff', z: 0 });
      (pr.opts as Record<string, unknown>).ang = ang;
      w.projs.push(pr); w.slashes.push({ x: ox, y: oy, ang, t: 0, dur: 0.2, r: 20, spread: 2.2, color: '#bfe4ff' });
      return true;
    }
    case 'whirl': {
      setCast(0.5); Audio.sfx('swing');
      const R = def.range! + rank * 2;
      for (let i = 0; i < 3; i++) w.later(0.08 + i * 0.12, () => {
        Audio.sfx('swing');
        w.slashes.push({ x: p.x, y: p.y - 8, ang: i * 2.1, t: 0, dur: 0.22, r: R - 4, spread: 4.2, color: '#ffd8b0' });
        for (const e of [...w.enemies]) if (e.state !== 'dying' && dist(p.x, p.y - 8, e.x, e.y - e.def.hitH * 0.5) < R + e.def.radius) damageEnemy(w, e, base * (i === 2 ? 1.2 : 0.9) / 1.0, { kb: 110, src: p, heavy: i === 2 });
      });
      w.areas.push({ kind: 'ring', x: p.x, y: p.y, r: R, t: 0, dur: 0.5, color: '#ffd8b0' });
      p.invuln = Math.max(p.invuln, 0.25);
      return true;
    }
    case 'dash': {
      setCast(0.3); Audio.sfx('dodge');
      const len = def.range! + rank * 4;
      const hitSet = new Set<Enemy>();
      let travelled = 0;
      const steps = 14;
      p.invuln = Math.max(p.invuln, 0.35);
      p.dir = dirFromVec(dirv.x, dirv.y, p.dir);
      for (let i = 0; i < steps; i++) w.later(i * 0.016, () => {
        const sx = len / steps;
        const nx = p.x + dirv.x * sx, ny = p.y + dirv.y * sx;
        if (w.boxFree(nx, ny, p.hw, p.hh)) { p.x = nx; p.y = ny; travelled += sx; }
        w.parts.push({ x: p.x, y: p.y - 6, vx: 0, vy: 0, life: 0.3, max: 0.3, color: '#bfe4ff', size: 3, grav: 0, fade: true });
        for (const e of w.enemies) if (!hitSet.has(e) && e.state !== 'dying' && dist(p.x, p.y - 8, e.x, e.y - e.def.hitH * 0.5) < 14 + e.def.radius) { hitSet.add(e); damageEnemy(w, e, base, { kb: 130, src: p, heavy: true, stun: 0.4 }); w.slashes.push({ x: e.x, y: e.y - 8, ang: ang + 1.5, t: 0, dur: 0.18, r: 14, spread: 2.6, color: '#fff' }); }
      });
      void travelled;
      return true;
    }
    case 'slam': {
      setCast(0.5); Audio.sfx('swing');
      const R = def.range! + rank * 2;
      w.later(0.28, () => {
        const cx = p.x + dirv.x * 16, cy = p.y + dirv.y * 12;
        Audio.sfx('slam'); w.addShake(7);
        w.areas.push({ kind: 'slam', x: cx, y: cy, r: R, t: 0, dur: 0.45, color: '#ffcf8a' });
        w.burst(cx, cy, 24, ['#c9a070', '#fff', '#8a6a3a'], { speed: 90, life: 0.5, size: 2, up: 30, grav: 120 });
        for (const e of [...w.enemies]) if (e.state !== 'dying' && dist(cx, cy, e.x, e.y) < R + e.def.radius) damageEnemy(w, e, base, { kb: 160, stun: 1.0, src: { x: cx, y: cy }, heavy: true });
      });
      return true;
    }
    case 'multi': {
      const tgt = nearestEnemy(w, p.x, p.y, def.range! + 40);
      if (!tgt) { w.toast('Nenhum alvo próximo!', undefined, '#ffb0b0'); return false; }
      setCast(0.9); p.invuln = 0.95;
      const n = 6;
      Audio.sfx('swing');
      for (let i = 0; i < n; i++) w.later(i * 0.1, () => {
        if (tgt.state === 'dying' || tgt.dead) return;
        const a = (i / n) * Math.PI * 2 + 0.7;
        p.x = tgt.x + Math.cos(a) * 18; p.y = tgt.y + Math.sin(a) * 10;
        if (!w.boxFree(p.x, p.y, 3, 2)) { p.x = tgt.x; p.y = tgt.y + 10; }
        p.dir = dirFromVec(tgt.x - p.x, tgt.y - p.y, p.dir);
        w.slashes.push({ x: tgt.x, y: tgt.y - 10, ang: a + Math.PI, t: 0, dur: 0.16, r: 16, spread: 2.4, color: i === n - 1 ? '#ffd84a' : '#ffffff' });
        Audio.sfx('swing');
        damageEnemy(w, tgt, base * (i === n - 1 ? 1.8 : 1), { kb: 0, heavy: i === n - 1, src: p, stun: 0.2 });
      });
      return true;
    }
    case 'bolt': {
      setCast(0.2); Audio.sfx('fire');
      w.projs.push(new Proj(ox + dirv.x * 8, oy + dirv.y * 8, dirv.x * 125, dirv.y * 125, 'p', base, 'fire', { r: 5, life: 1.4, elem: 'fire', explode: 24 + rank * 2, burn: 3, kb: 70, color: '#ff8a2a' }));
      return true;
    }
    case 'lance': {
      setCast(0.2); Audio.sfx('ice');
      const pr = new Proj(ox + dirv.x * 8, oy + dirv.y * 8, dirv.x * 200, dirv.y * 200, 'p', base, 'ice', { r: 5, life: 0.9, pierce: 1 + Math.floor(rank / 3), elem: 'ice', slow: 2.5, kb: 50, color: '#9ae8ff' });
      (pr.opts as Record<string, unknown>).ang = ang;
      w.projs.push(pr);
      return true;
    }
    case 'chain': {
      const first = nearestEnemy(w, ox + dirv.x * 40, oy + dirv.y * 40, def.range!);
      if (!first) { w.toast('Nenhum alvo!', undefined, '#ffb0b0'); return false; }
      setCast(0.25); Audio.sfx('bolt');
      const pts: [number, number][] = [[ox, oy]];
      const hitSet = new Set<Enemy>();
      let cur: Enemy | null = first, dmg = base;
      for (let i = 0; i < 3 + Math.floor(rank / 2) && cur; i++) {
        hitSet.add(cur);
        pts.push([cur.x, cur.y - cur.def.hitH * 0.6]);
        const tgt: Enemy = cur, d = dmg;
        w.later(i * 0.06, () => damageEnemy(w, tgt, d, { elem: 'bolt', kb: 30, stun: 0.3, src: p }));
        dmg *= 0.86;
        cur = nearestEnemy(w, cur.x, cur.y, 75, (e) => !hitSet.has(e));
      }
      w.areas.push({ kind: 'bolt', x: ox, y: oy, r: 0, t: 0, dur: 0.35, color: '#ffe84a', pts });
      return true;
    }
    case 'nova': {
      setCast(0.4); Audio.sfx('ice');
      const R = def.range! + rank * 3;
      w.areas.push({ kind: 'nova', x: p.x, y: p.y, r: R, t: 0, dur: 0.5, color: '#9ae8ff' });
      w.burst(p.x, p.y - 8, 28, ['#9ae8ff', '#fff', '#5ac8ff'], { speed: 110, life: 0.6, size: 2 });
      w.later(0.12, () => { for (const e of [...w.enemies]) if (e.state !== 'dying' && dist(p.x, p.y, e.x, e.y) < R + e.def.radius) damageEnemy(w, e, base, { elem: 'ice', freeze: 1.4 + rank * 0.2, kb: 60, src: p, heavy: true }); w.addShake(4); });
      return true;
    }
    case 'meteor': {
      const tgt = nearestEnemy(w, p.x + dirv.x * 50, p.y + dirv.y * 50, 140);
      let mx = tgt ? tgt.x : p.x + dirv.x * 70, my = tgt ? tgt.y : p.y + dirv.y * 70;
      if (!w.boxFree(mx, my, 2, 2)) { mx = p.x + dirv.x * 40; my = p.y + dirv.y * 40; }
      setCast(0.5); Audio.sfx('meteor');
      const R = def.range! + rank * 3;
      w.areas.push({ kind: 'warn', x: mx, y: my, r: R, t: 0, dur: 0.9, color: '#ff8a2a' });
      w.areas.push({ kind: 'meteor', x: mx, y: my, r: R, t: 0, dur: 0.9, color: '#ff8a2a' });
      w.later(0.9, () => {
        Audio.sfx('explosion'); w.addShake(9);
        w.areas.push({ kind: 'slam', x: mx, y: my, r: R + 6, t: 0, dur: 0.6, color: '#ff8a2a' });
        w.burst(mx, my - 4, 40, ['#ff8a2a', '#ffd84a', '#fff', '#c0402a'], { speed: 140, life: 0.8, size: 3, up: 30 });
        for (const e of [...w.enemies]) if (e.state !== 'dying' && dist(mx, my, e.x, e.y) < R + e.def.radius) damageEnemy(w, e, base, { elem: 'fire', burn: 4, kb: 160, src: { x: mx, y: my }, heavy: true });
      });
      return true;
    }
    case 'heal': {
      setCast(0.4); Audio.sfx('heal');
      const st = G.stats();
      const amt = Math.round(base * 3 + 12);
      const before = G.hp;
      G.hp = Math.min(st.maxHp, G.hp + amt);
      w.text(p.x, p.y - 28, `+${Math.round(G.hp - before)}`, '#6aff9a', true);
      w.areas.push({ kind: 'ring', x: p.x, y: p.y, r: 28, t: 0, dur: 0.6, color: '#6aff9a' });
      w.burst(p.x, p.y - 8, 20, ['#6aff9a', '#fff', '#c8ffd8'], { speed: 40, life: 0.9, up: 60, size: 2 });
      return true;
    }
    case 'shield': {
      setCast(0.35); Audio.sfx('shield');
      p.shield = Math.round(base * 2.2 + 20); p.shieldT = 9;
      w.areas.push({ kind: 'ring', x: p.x, y: p.y, r: 24, t: 0, dur: 0.5, color: '#9ad8ff' });
      w.toast(`Escudo: ${p.shield}`, 'shield', '#9ad8ff');
      return true;
    }
    case 'buff': {
      setCast(0.4); Audio.sfx('buff');
      p.buffMul = 1.25 + rank * 0.04; p.buffT = 12;
      w.areas.push({ kind: 'nova', x: p.x, y: p.y, r: 36, t: 0, dur: 0.6, color: '#ff6a5a' });
      w.burst(p.x, p.y - 8, 18, ['#ff6a5a', '#ffd84a'], { speed: 50, life: 0.8, up: 50, size: 2 });
      w.toast(`Fúria! +${Math.round((p.buffMul - 1) * 100)}% de dano`, 'rage', '#ff8a7a');
      return true;
    }
    case 'phase': {
      Audio.sfx('spirit');
      const len = def.range! + rank * 6;
      let tx = p.x, ty = p.y;
      for (let d = 4; d <= len; d += 4) { const nx = p.x + dirv.x * d, ny = p.y + dirv.y * d; if (w.boxFree(nx, ny, p.hw, p.hh)) { tx = nx; ty = ny; } else break; }
      w.burst(p.x, p.y - 8, 14, ['#c8a8ff', '#fff'], { speed: 60, life: 0.5, size: 2 });
      p.x = tx; p.y = ty;
      w.burst(p.x, p.y - 8, 14, ['#c8a8ff', '#fff'], { speed: 60, life: 0.5, size: 2 });
      p.state = 'phase'; p.t = 0; p.phaseT = 0.7; p.invuln = 0.8;
      return true;
    }
    case 'summon': {
      setCast(0.4); Audio.sfx('spirit');
      const dur = 10;
      const a: AreaFx = { kind: 'spirits', x: p.x, y: p.y, r: 30, t: 0, dur, color: '#a0ffd8' };
      (a as unknown as Record<string, number>).dmg = base; (a as unknown as Record<string, number>).tick = 0;
      w.areas.push(a);
      w.toast('Espíritos Guardiões invocados', 'spirit', '#a0ffd8');
      return true;
    }
  }
  return false;
}

// ------------------------------------------------------------------ projectiles & areas
export function updateProjectiles(w: World, dt: number) {
  const p = w.player;
  for (const pr of w.projs) {
    pr.age += dt;
    pr.opts.life = (pr.opts.life ?? 2) - dt;
    if (pr.opts.homing && pr.team === 'p') {
      const t = nearestEnemy(w, pr.x, pr.y, 90);
      if (t) { const a = Math.atan2(t.y - 8 - pr.y, t.x - pr.x), sp = Math.hypot(pr.vx, pr.vy); pr.vx += Math.cos(a) * 200 * dt; pr.vy += Math.sin(a) * 200 * dt; const m = Math.hypot(pr.vx, pr.vy); pr.vx = (pr.vx / m) * sp; pr.vy = (pr.vy / m) * sp; }
    }
    const nx = pr.x + pr.vx * dt, ny = pr.y + pr.vy * dt;
    if (w.tileSolid(Math.floor(nx / TS), Math.floor((ny + (pr.opts.z ?? 0)) / TS)) && pr.kind !== 'wave') { explode(w, pr); pr.dead = true; continue; }
    pr.x = nx; pr.y = ny;
    if (Math.random() < 0.5) {
      const col = pr.opts.color ?? '#fff';
      w.parts.push({ x: pr.x, y: pr.y - (pr.opts.z ?? 0), vx: (Math.random() - 0.5) * 12, vy: (Math.random() - 0.5) * 12, life: 0.25, max: 0.25, color: col, size: pr.kind === 'wave' ? 2 : 2, grav: 0, fade: true });
    }
    if (pr.team === 'p') {
      for (const e of w.enemies) {
        if (pr.hit.has(e) || e.state === 'dying') continue;
        if (dist(pr.x, pr.y, e.x, e.y - e.def.hitH * 0.6) < pr.r + e.def.radius * 0.8) {
          pr.hit.add(e);
          const o = pr.opts;
          if (o.explode) { explode(w, pr); pr.dead = true; break; }
          damageEnemy(w, e, pr.dmg, { elem: o.elem, kb: o.kb, slow: o.slow, burn: o.burn, stun: o.stun, src: pr, heavy: pr.kind === 'wave' });
          if (pr.hit.size > (o.pierce ?? 0)) { pr.dead = true; break; }
        }
      }
    } else if (dist(pr.x, pr.y, p.x, p.y - 8) < pr.r + 5) {
      if (hurtPlayer(w, pr.dmg, pr.x - pr.vx * 0.1, pr.y - pr.vy * 0.1, pr.opts.kb ?? 60, pr.opts.elem)) { if (pr.opts.slow) p.slowT = pr.opts.slow; pr.dead = true; w.burst(pr.x, pr.y, 6, pr.opts.color ?? '#fff', { speed: 40, life: 0.3 }); }
    }
    if (pr.opts.life! <= 0) { if (pr.opts.explode) explode(w, pr); pr.dead = true; }
  }
  w.projs = w.projs.filter((x) => !x.dead);
}

function explode(w: World, pr: Proj) {
  const R = pr.opts.explode;
  if (!R) { w.burst(pr.x, pr.y, 5, pr.opts.color ?? '#fff', { speed: 40, life: 0.25 }); return; }
  Audio.sfx('explosion');
  w.areas.push({ kind: 'slam', x: pr.x, y: pr.y, r: R, t: 0, dur: 0.35, color: pr.opts.color ?? '#ff8a2a' });
  w.burst(pr.x, pr.y, 20, ['#ff8a2a', '#ffd84a', '#fff'], { speed: 100, life: 0.5, size: 2 });
  w.addShake(3);
  for (const e of [...w.enemies]) if (e.state !== 'dying' && dist(pr.x, pr.y, e.x, e.y - 4) < R + e.def.radius) damageEnemy(w, e, pr.dmg, { elem: pr.opts.elem, burn: pr.opts.burn, kb: pr.opts.kb, src: pr, silent: false });
}

export function updateAreas(w: World, dt: number) {
  for (const a of w.areas) {
    a.t += dt;
    if (a.kind === 'spirits') {
      const p = w.player;
      const d = (a as unknown as Record<string, number>);
      d.tick -= dt;
      if (d.tick <= 0) {
        d.tick = 0.45;
        for (let i = 0; i < 3; i++) {
          const ang = w.time * 3.2 + (i * Math.PI * 2) / 3;
          const sx = p.x + Math.cos(ang) * a.r, sy = p.y - 8 + Math.sin(ang) * a.r * 0.7;
          for (const e of [...w.enemies]) if (e.state !== 'dying' && dist(sx, sy, e.x, e.y - e.def.hitH * 0.5) < 14 + e.def.radius) damageEnemy(w, e, d.dmg, { elem: 'holy', kb: 60, src: p, noCrit: true, silent: true });
        }
      }
    }
    if (a.fire && !a.fired && a.t >= (a.delay ?? a.dur)) { a.fired = true; a.fire(); }
  }
  w.areas = w.areas.filter((a) => a.t < a.dur);
}

// ------------------------------------------------------------------ allies
const ALLY_CFG: Record<string, { cd: number; range: number; dmg: number; elem: Elem; kind: 'proj' | 'melee' | 'heal'; color: string }> = {
  lyra: { cd: 2.2, range: 130, dmg: 2.0, elem: 'fire', kind: 'proj', color: '#ff8a2a' },
  torren: { cd: 1.4, range: 36, dmg: 2.4, elem: 'phys', kind: 'melee', color: '#fff' },
  sylphie: { cd: 5, range: 0, dmg: 0, elem: 'holy', kind: 'heal', color: '#6aff9a' },
  rhea: { cd: 1.1, range: 110, dmg: 1.4, elem: 'dark', kind: 'proj', color: '#c080ff' },
};

export function updateAlly(w: World, a: Ally, dt: number) {
  const cfg = ALLY_CFG[a.id];
  if (!cfg) return;
  a.atkT -= dt;
  a.castT -= dt;
  if (a.castT <= 0) a.state = 'follow';
  if (a.atkT > 0) return;
  const p = w.player;
  if (cfg.kind === 'heal') {
    const st = G.stats();
    if (G.hp < st.maxHp * 0.6) {
      a.atkT = cfg.cd * 3; a.state = 'cast'; a.castT = 0.5;
      const amt = Math.round(st.maxHp * 0.2);
      G.hp = Math.min(st.maxHp, G.hp + amt);
      w.text(p.x, p.y - 28, `+${amt}`, '#6aff9a', true); Audio.sfx('heal');
      w.areas.push({ kind: 'ring', x: p.x, y: p.y, r: 26, t: 0, dur: 0.6, color: '#6aff9a' });
      w.burst(p.x, p.y - 8, 14, ['#6aff9a', '#fff'], { speed: 40, up: 50, life: 0.8 });
    } else a.atkT = 0.5;
    return;
  }
  const tgt = nearestEnemy(w, a.x, a.y, cfg.range + 30, (e) => w.los(a.x, a.y, e.x, e.y));
  if (!tgt) { a.atkT = 0.3; return; }
  const lv = G.level;
  const dmg = (8 + lv * 2.6) * cfg.dmg;
  a.dir = dirFromVec(tgt.x - a.x, tgt.y - a.y, a.dir);
  a.state = 'cast'; a.castT = 0.35; a.atkT = cfg.cd;
  if (cfg.kind === 'proj') {
    const ang = Math.atan2(tgt.y - tgt.def.hitH * 0.5 - (a.y - 8), tgt.x - a.x);
    const elem: Elem = a.id === 'lyra' ? (Math.random() < 0.4 ? 'ice' : 'fire') : cfg.elem;
    Audio.sfx(elem === 'ice' ? 'ice' : elem === 'fire' ? 'fire' : 'swing');
    w.projs.push(new Proj(a.x, a.y - 8, Math.cos(ang) * 130, Math.sin(ang) * 130, 'p', dmg, elem === 'fire' ? 'fire' : elem === 'ice' ? 'ice' : 'dark', { r: 4, life: 1.2, elem, explode: elem === 'fire' ? 18 : 0, slow: elem === 'ice' ? 2 : 0, color: elem === 'fire' ? '#ff8a2a' : elem === 'ice' ? '#9ae8ff' : '#c080ff', kb: 40 }));
  } else {
    const d = dist(a.x, a.y, tgt.x, tgt.y);
    if (d > cfg.range) { a.atkT = 0.2; const ang = Math.atan2(tgt.y - a.y, tgt.x - a.x); w.moveBody(a, Math.cos(ang) * 60 * dt * 6, Math.sin(ang) * 60 * dt * 6); return; }
    Audio.sfx('swing'); w.slashes.push({ x: a.x, y: a.y - 8, ang: Math.atan2(tgt.y - a.y, tgt.x - a.x), t: 0, dur: 0.2, r: 22, spread: 2.4, color: '#fff' });
    for (const e of [...w.enemies]) if (e.state !== 'dying' && dist(a.x, a.y, e.x, e.y) < 36 + e.def.radius) damageEnemy(w, e, dmg, { kb: 90, src: a, noCrit: true });
  }
}

// ------------------------------------------------------------------ drawing the player
export function drawPlayer(w: World, g: CanvasRenderingContext2D, cx: number, cy: number) {
  const p = w.player;
  const x = p.x - cx, y = p.y - cy;
  drawShadow(g, x, y, 6.5);
  const sheet = p.sheet;
  let anim = 'idle', frame = Math.floor(w.time * 1.8) % 2;
  if (p.state === 'walk') { anim = 'walk'; frame = Math.floor(p.anim) % 4; }
  else if (p.state === 'idle') { anim = 'idle'; frame = Math.floor(p.anim) % 2; }
  else if (p.state === 'attack') { anim = 'attack'; const f = p.t / ATK_DUR[Math.max(0, p.combo - 1)]; frame = f < 0.28 ? 0 : f < 0.7 ? 1 : 2; }
  else if (p.state === 'cast') { anim = 'cast'; frame = p.t < 0.2 ? 0 : 1; }
  else if (p.state === 'hurt' || p.state === 'dead') { anim = 'hurt'; frame = 0; }
  const blink = p.invuln > 0 && p.state !== 'roll' && p.state !== 'hurt' && Math.floor(w.time * 20) % 2 === 0;
  let alpha = blink ? 0.45 : 1;
  if (p.state === 'phase') alpha = 0.35;
  const flash = p.flash > 0;

  // aura / shield
  if (p.buffT > 0 && Math.random() < 0.4) w.parts.push({ x: p.x + (Math.random() - 0.5) * 10, y: p.y - 4, vx: 0, vy: -24, life: 0.5, max: 0.5, color: '#ff8a5a', size: 2, grav: 0, fade: true });

  if (p.state === 'dead') {
    const f = sheet.frame('hurt', 'down', 0);
    g.save(); g.translate(Math.round(x), Math.round(y - 4)); g.rotate(Math.min(1, p.t * 3) * (Math.PI / 2)); g.globalAlpha = Math.max(0.2, 1 - Math.max(0, p.t - 1) * 0.8); g.drawImage(f, -12, -27); g.restore(); g.globalAlpha = 1;
    return;
  }
  const weapon = () => {
    if (p.state !== 'attack') return;
    const dur = ATK_DUR[p.combo - 1];
    const f = clamp(p.t / dur, 0, 1);
    const dirAng = Math.atan2(p.rollDy, p.rollDx);
    const sweep = (f - 0.28) / 0.45;
    const sgn = p.combo % 2 === 1 ? 1 : -1;
    const ang = dirAng + sgn * (clamp(sweep, 0, 1) - 0.5) * 2.4 + (f < 0.28 ? -sgn * 0.7 : 0);
    const hx = x + (p.dir === 'left' ? -4 : p.dir === 'right' ? 4 : 3), hy = y - 11;
    for (let i = 3; i < 17; i++) { g.fillStyle = i < 5 ? '#c9a050' : i === 16 ? '#fff' : i % 2 ? '#dfe8ff' : '#aab8d8'; g.fillRect(Math.round(hx + Math.cos(ang) * i), Math.round(hy + Math.sin(ang) * i * 0.9), 2, 2); }
  };
  if (p.state === 'roll') {
    const spin = (p.t / 0.28) * Math.PI * 2 * (p.rollDx >= 0 ? 1 : -1);
    g.save(); g.translate(Math.round(x), Math.round(y - 10)); g.rotate(spin); g.globalAlpha = alpha;
    g.drawImage(sheet.frame('idle', p.dir, 0), -12, -21); g.restore(); g.globalAlpha = 1;
  } else {
    if (p.dir === 'up') weapon();
    drawChar(g, sheet, anim, p.dir, frame, x, y, flash, alpha);
    if (p.dir !== 'up') weapon();
  }
  if (p.shield > 0) {
    g.globalAlpha = 0.25 + 0.1 * Math.sin(w.time * 8); g.fillStyle = '#9ad8ff';
    for (let j = -14; j <= 12; j++) { const ww = Math.round(11 * Math.sqrt(1 - (j * j) / 200)); g.fillRect(Math.round(x - ww), Math.round(y - 12 + j), ww * 2, 1); }
    g.globalAlpha = 0.7; g.fillStyle = '#e8f8ff';
    for (let a = 0; a < 20; a++) { const an = (a / 20) * Math.PI * 2; g.fillRect(Math.round(x + Math.cos(an) * 11), Math.round(y - 12 + Math.sin(an) * 14), 1, 1); }
    g.globalAlpha = 1;
  }
}

export function drawProjectiles(w: World, g: CanvasRenderingContext2D, cx: number, cy: number) {
  for (const pr of w.projs) {
    const x = Math.round(pr.x - cx), y = Math.round(pr.y - cy - (pr.opts.z ?? 0));
    const col = pr.opts.color ?? '#fff';
    switch (pr.kind) {
      case 'wave': {
        const ang = (pr.opts as unknown as Record<string, number>).ang ?? 0;
        for (let i = -9; i <= 9; i++) { const a = ang + i * 0.12; const r = 8 + Math.abs(i) * -0.2 + 6; g.fillStyle = Math.abs(i) < 3 ? '#fff' : col; g.globalAlpha = 1 - Math.abs(i) / 12; g.fillRect(Math.round(x + Math.cos(a) * r - Math.cos(ang) * 6), Math.round(y + Math.sin(a) * r * 0.9 - Math.sin(ang) * 6), 2, 2); }
        g.globalAlpha = 1; break;
      }
      case 'ice': {
        const ang = (pr.opts as unknown as Record<string, number>).ang ?? Math.atan2(pr.vy, pr.vx);
        for (let i = 0; i < 9; i++) { g.fillStyle = i > 6 ? '#fff' : i > 3 ? '#9ae8ff' : '#5ac8ff'; g.fillRect(Math.round(x + Math.cos(ang) * (i - 4)), Math.round(y + Math.sin(ang) * (i - 4)), 2, 2); }
        break;
      }
      case 'arrow': {
        const ang = Math.atan2(pr.vy, pr.vx);
        for (let i = -4; i < 5; i++) { g.fillStyle = i > 2 ? '#e8e8f8' : i < -2 ? '#c05050' : '#a07040'; g.fillRect(Math.round(x + Math.cos(ang) * i), Math.round(y + Math.sin(ang) * i), 1, 1); }
        break;
      }
      case 'shard': { g.fillStyle = '#05020c'; g.fillRect(x - 3, y - 3, 6, 6); g.fillStyle = '#8af0ff'; g.fillRect(x - 2, y - 2, 4, 4); g.fillStyle = '#fff'; g.fillRect(x - 2, y - 2, 2, 2); break; }
      case 'slime': { g.fillStyle = '#05020c'; g.fillRect(x - 4, y - 4, 8, 8); g.fillStyle = '#7ae88a'; g.fillRect(x - 3, y - 3, 6, 6); g.fillStyle = '#d8ffe0'; g.fillRect(x - 3, y - 3, 3, 2); break; }
      default: {
        const r = pr.r;
        g.fillStyle = '#05020c'; g.fillRect(x - r - 1, y - r - 1, r * 2 + 2, r * 2 + 2);
        g.fillStyle = col; g.fillRect(x - r, y - r, r * 2, r * 2);
        g.fillStyle = '#fff'; g.fillRect(x - r + 1, y - r + 1, Math.max(1, r - 1), Math.max(1, r - 1));
      }
    }
  }
}
