import { Audio } from '../../engine/audio';
import { clamp, dist } from '../../engine/util';
import { Enemy, Proj } from '../entities';
import { ENEMIES } from '../data/enemies';
import { damageEnemy, hurtPlayer } from './combat';
import type { World } from './world';
import { G } from '../state';

function moveToward(w: World, e: Enemy, tx: number, ty: number, spd: number, dt: number) {
  let dx = tx - e.x, dy = ty - e.y;
  const d = Math.hypot(dx, dy) || 1;
  dx /= d; dy /= d;
  if (!e.def.fly && !w.los(e.x, e.y, tx, ty)) {
    const f = w.flowDir(e.x, e.y);
    if (f) { dx = f.x; dy = f.y; }
  }
  w.moveBody(e, dx * spd * dt, dy * spd * dt, e.def.fly);
  if (Math.abs(dx) > 0.2) e.face = dx < 0 ? -1 : 1;
}

function shootAt(w: World, e: Enemy, kind: Proj['kind'], speed: number, dmgMul = 1, spread = 0, opts: Proj['opts'] = {}) {
  const p = w.player;
  const ang = Math.atan2(p.y - 8 - (e.y - e.def.hitH * 0.7), p.x - e.x) + spread;
  w.projs.push(new Proj(e.x, e.y - e.def.hitH * 0.7, Math.cos(ang) * speed, Math.sin(ang) * speed, 'e', e.def.atk * dmgMul, kind, { r: 3, life: 3, kb: 50, color: '#fff', ...opts }));
}

function tele(e: Enemy, kind: 'circle' | 'line' | 'cone', dur: number, o: { x?: number; y?: number; r?: number; ang?: number; len?: number } = {}) {
  e.tele = { kind, x: o.x ?? e.x, y: o.y ?? e.y, r: o.r ?? 20, ang: o.ang, len: o.len, t: 0, dur };
  e.state = 'tele'; e.t = 0;
  Audio.sfx('telegraph');
}

function contact(w: World, e: Enemy, mul = 1, kb = 80) {
  const p = w.player;
  if (dist(p.x, p.y - 8, e.x, e.y - e.def.hitH * 0.5) < e.def.radius * 0.8 + 6) hurtPlayer(w, e.def.atk * mul, e.x, e.y, kb);
}

function arcHit(w: World, e: Enemy, ang: number, reach: number, spread: number, mul = 1, kb = 100) {
  const p = w.player;
  const dx = p.x - e.x, dy = p.y - 8 - (e.y - 8);
  const d = Math.hypot(dx, dy);
  w.slashes.push({ x: e.x, y: e.y - 8, ang, t: 0, dur: 0.2, r: reach - 4, spread, color: '#ff8a9a' });
  if (d > reach + 4) return;
  let da = Math.abs(Math.atan2(dy, dx) - ang); if (da > Math.PI) da = Math.PI * 2 - da;
  if (da <= spread / 2 + 0.2 || d < 12) hurtPlayer(w, e.def.atk * mul, e.x, e.y, kb);
}

function slamAt(w: World, x: number, y: number, r: number, dmg: number, col = '#ff8a5a') {
  Audio.sfx('slam'); w.addShake(6);
  w.areas.push({ kind: 'slam', x, y, r, t: 0, dur: 0.45, color: col });
  w.burst(x, y, 16, ['#c9a070', '#fff', col], { speed: 80, life: 0.5, size: 2, up: 20, grav: 100 });
  const p = w.player;
  if (dist(p.x, p.y, x, y) < r) hurtPlayer(w, dmg, x, y, 140);
}

function delayedBlast(w: World, x: number, y: number, r: number, delay: number, dmg: number, col: string) {
  w.areas.push({ kind: 'warn', x, y, r, t: 0, dur: delay, color: col, delay, fire: () => slamAt(w, x, y, r, dmg, col) });
}

export function updateEnemy(w: World, e: Enemy, dt: number) {
  const d = e.def;
  const p = w.player;
  e.anim += dt * (e.state === 'chase' ? 6 : e.state === 'idle' ? 2.5 : 4);
  e.flash = Math.max(0, e.flash - dt);
  if (e.state === 'dying') { e.deathT += dt; if (e.deathT > 0.5) e.dead = true; return; }
  if (e.burn > 0) { e.burn -= dt; e.counter += dt; if (e.counter >= 0.5) { e.counter = 0; damageEnemy(w, e, e.burnDmg, { elem: 'fire', noCrit: true, dot: true }); if ((e.state as string) === 'dying') return; } }
  if (e.freeze > 0) e.freeze -= dt;
  if (e.slow > 0) e.slow -= dt;
  if (Math.abs(e.kx) + Math.abs(e.ky) > 3) { w.moveBody(e, e.kx * dt, e.ky * dt, d.fly); e.kx *= 0.84; e.ky *= 0.84; }
  if (e.stun > 0) { e.stun -= dt; if (e.stun <= 0) { e.state = 'chase'; e.t = 0; } return; }
  e.t += dt;
  if (e.tele) { e.tele.t += dt; if (e.tele.t >= e.tele.dur) e.tele = null; }

  const dx = p.x - e.x, dy = p.y - e.y, dd = Math.hypot(dx, dy);
  const dead = p.state === 'dead';
  const spdM = e.slow > 0 ? 0.5 : 1;
  if (!e.aggro && !dead && dd < (d.aggro ?? 105) && (dd < 56 || w.los(e.x, e.y, p.x, p.y))) { e.aggro = true; if (d.boss) { w.bossBar = e; Audio.sfx('roar'); w.addShake(5); if (w.musicOverride !== 'boss') { w.musicOverride = 'boss'; Audio.music('boss'); } } }
  if (e.aggro && (dd > 280 || dead) && !d.boss) { e.aggro = false; e.state = 'idle'; }
  if (d.boss && e.aggro) w.bossBar = e;
  if (!e.aggro) {
    // idle wander
    if (e.state === 'idle' && e.t > 1.5 + (e.anim % 2)) { e.t = 0; e.tx = e.home.x + (Math.random() - 0.5) * 40; e.ty = e.home.y + (Math.random() - 0.5) * 30; }
    if (e.tx && e.ty && dist(e.x, e.y, e.tx, e.ty) > 3 && !d.boss) moveToward(w, e, e.tx, e.ty, d.spd * 0.35, dt);
    return;
  }
  if (e.state === 'idle') { e.state = 'chase'; e.t = 0; }
  if (dx !== 0 && e.state === 'chase') e.face = dx < 0 ? -1 : 1;

  switch (d.ai) {
    // ---------------------------------------------------------------- slimes
    case 'hop': {
      if (e.state === 'chase') {
        if (e.t > 1.0 + (e.anim % 0.5)) { e.state = 'tele'; e.t = 0; e.tx = dx / (dd || 1); e.ty = dy / (dd || 1); }
      } else if (e.state === 'tele') {
        if (e.t > 0.3) { e.state = 'atk'; e.t = 0; }
      } else if (e.state === 'atk') {
        const f = e.t / 0.42;
        w.moveBody(e, e.tx * d.spd * 3.4 * spdM * dt, e.ty * d.spd * 3.4 * spdM * dt);
        e.z = Math.sin(clamp(f, 0, 1) * Math.PI) * 7;
        contact(w, e, 1, 90);
        if (e.t > 0.42) { e.state = 'rec'; e.t = 0; e.z = 0; }
      } else if (e.state === 'rec') { if (e.t > 0.5) { e.state = 'chase'; e.t = 0; } }
      break;
    }
    // ---------------------------------------------------------------- bats
    case 'bat': {
      if (e.state === 'chase') {
        const ox = Math.cos(e.anim * 0.9) * 28, oy = Math.sin(e.anim * 1.3) * 18;
        moveToward(w, e, p.x + ox, p.y + oy, d.spd * 0.9 * spdM, dt);
        if (e.t > 2.2 && dd < 110) { tele(e, 'line', 0.4, { x: e.x, y: e.y, r: 4, ang: Math.atan2(dy, dx), len: dd + 20 }); e.tx = dx / dd; e.ty = dy / dd; }
      } else if (e.state === 'tele') {
        if (e.t > 0.4) { e.state = 'atk'; e.t = 0; }
      } else if (e.state === 'atk') {
        w.moveBody(e, e.tx * 150 * spdM * dt, e.ty * 150 * spdM * dt, true);
        contact(w, e, 1, 80);
        if (e.t > 0.4) { e.state = 'rec'; e.t = 0; }
      } else if (e.state === 'rec') { moveToward(w, e, e.x - e.tx * 30, e.y - 20, d.spd * 0.7, dt); if (e.t > 0.8) { e.state = 'chase'; e.t = 0; } }
      break;
    }
    // ---------------------------------------------------------------- wolves
    case 'pounce': {
      if (e.state === 'chase') {
        moveToward(w, e, p.x, p.y, d.spd * spdM, dt);
        if (dd < 80 && e.t > 0.6 && w.los(e.x, e.y, p.x, p.y)) { const ang = Math.atan2(dy, dx); tele(e, 'line', 0.5, { x: e.x, y: e.y - 4, r: 6, ang, len: 100 }); e.tx = Math.cos(ang); e.ty = Math.sin(ang); }
      } else if (e.state === 'tele') {
        if (e.t > 0.5) { e.state = 'atk'; e.t = 0; Audio.sfx('swing'); }
      } else if (e.state === 'atk') {
        w.moveBody(e, e.tx * 200 * dt, e.ty * 200 * dt);
        contact(w, e, 1, 110);
        if (e.t > 0.32) { e.state = 'rec'; e.t = 0; }
      } else if (e.state === 'rec') { if (e.t > 0.8) { e.state = 'chase'; e.t = 0; } }
      break;
    }
    // ---------------------------------------------------------------- melee
    case 'melee': case 'shadow': {
      const reach = d.ai === 'shadow' ? 26 : 22;
      if (e.state === 'chase') {
        moveToward(w, e, p.x, p.y, d.spd * spdM, dt);
        if (dd < reach + 4 && e.t > 0.4) { const ang = Math.atan2(dy, dx); tele(e, 'cone', 0.45, { x: e.x, y: e.y - 8, r: reach, ang }); e.tx = ang; }
        else if (d.ai === 'shadow' && dd < 70 && dd > 36 && e.t > 1.4) { const ang = Math.atan2(dy, dx); tele(e, 'line', 0.4, { x: e.x, y: e.y - 4, r: 6, ang, len: 60 }); e.tx = Math.cos(ang); e.ty = Math.sin(ang); e.counter = 1; }
      } else if (e.state === 'tele') {
        if (e.t > (e.tele?.dur ?? 0.45) - 0.02) {
          if (e.counter === 1) { e.state = 'atk'; e.t = 0; Audio.sfx('swing'); } else { arcHit(w, e, e.tx, reach, 2.0, 1, 100); Audio.sfx('swing'); e.state = 'rec'; e.t = 0; }
        }
      } else if (e.state === 'atk') {
        w.moveBody(e, e.tx * 170 * dt, e.ty * 170 * dt); contact(w, e, 1.2, 100);
        if (e.t > 0.25) { e.state = 'rec'; e.t = 0; e.counter = 0; }
      } else if (e.state === 'rec') { if (e.t > 0.6) { e.state = 'chase'; e.t = 0; } }
      break;
    }
    // ---------------------------------------------------------------- ranged
    case 'archer': {
      if (e.state === 'chase') {
        if (dd < 70) moveToward(w, e, e.x - dx, e.y - dy, d.spd * spdM, dt);
        else if (dd > 130) moveToward(w, e, p.x, p.y, d.spd * spdM, dt);
        if (e.t > 2.0 && dd < 150 && w.los(e.x, e.y, p.x, p.y)) tele(e, 'line', 0.5, { x: e.x, y: e.y - 8, r: 2, ang: Math.atan2(dy, dx), len: 130 });
      } else if (e.state === 'tele') {
        if (e.t > 0.5) { shootAt(w, e, 'arrow', 140, 1, 0, { r: 3, color: '#e8e8f8' }); Audio.sfx('swing'); e.state = 'rec'; e.t = 0; }
      } else if (e.state === 'rec') { if (e.t > 0.6) { e.state = 'chase'; e.t = 0; } }
      break;
    }
    case 'caster': {
      if (e.state === 'chase') {
        if (dd < 60) moveToward(w, e, e.x - dx, e.y - dy, d.spd * spdM, dt);
        else if (dd > 110) moveToward(w, e, p.x, p.y, d.spd * spdM, dt);
        if (e.t > 2.4 && dd < 140 && w.los(e.x, e.y, p.x, p.y)) tele(e, 'circle', 0.6, { x: e.x, y: e.y, r: 10 });
      } else if (e.state === 'tele') {
        if (e.t > 0.6) {
          if (d.id === 'skeleton_mage') { for (const s of [-0.3, 0, 0.3]) shootAt(w, e, 'dark', 85, 1, s, { r: 4, color: '#c080ff', elem: 'dark' }); Audio.sfx('bolt'); }
          else { shootAt(w, e, 'spore', 60, 1, 0, { r: 4, color: '#c8e86a', slow: 2 }); Audio.sfx('swing'); }
          e.state = 'rec'; e.t = 0;
        }
      } else if (e.state === 'rec') { if (e.t > 0.7) { e.state = 'chase'; e.t = 0; } }
      break;
    }
    case 'wisp': {
      if (e.state === 'chase') {
        const a = e.anim * 0.35;
        moveToward(w, e, p.x + Math.cos(a) * 80, p.y + Math.sin(a) * 50, d.spd * spdM, dt);
        if (e.t > 2.0 && dd < 150) tele(e, 'circle', 0.5, { x: e.x, y: e.y, r: 8 });
      } else if (e.state === 'tele') {
        if (e.t > 0.5) { for (const s of [-0.25, 0.25]) shootAt(w, e, 'fire', 95, 1, s, { r: 4, color: '#ff8a2a', elem: 'fire' }); Audio.sfx('fire'); e.state = 'rec'; e.t = 0; }
      } else if (e.state === 'rec') { if (e.t > 0.5) { e.state = 'chase'; e.t = 0; } }
      break;
    }
    case 'golem': {
      if (e.state === 'chase') {
        moveToward(w, e, p.x, p.y, d.spd * spdM, dt);
        if (dd < 44 && e.t > 0.8) tele(e, 'circle', 0.9, { x: e.x, y: e.y, r: 40 });
      } else if (e.state === 'tele') {
        if (e.t > 0.9) { slamAt(w, e.x, e.y, 40, d.atk, '#ffb03a'); e.state = 'rec'; e.t = 0; }
      } else if (e.state === 'rec') { if (e.t > 1.0) { e.state = 'chase'; e.t = 0; } }
      break;
    }
    case 'boss_wolf': bossWolf(w, e, dt, dx, dy, dd, spdM); break;
    case 'boss_slimeking': bossSlime(w, e, dt, dx, dy, dd, spdM); break;
    case 'boss_crystal': bossCrystal(w, e, dt, dx, dy, dd, spdM); break;
  }
}

// ------------------------------------------------------------------ bosses
function enrage(w: World, e: Enemy, msg: string) {
  e.phase = 2;
  Audio.sfx('roar'); w.addShake(8);
  w.banner = { text: msg, t: 0 };
  w.burst(e.x, e.y - 10, 30, ['#ff5a6a', '#fff'], { speed: 120, life: 0.8, size: 3 });
}

function bossWolf(w: World, e: Enemy, dt: number, dx: number, dy: number, dd: number, spdM: number) {
  const d = e.def;
  const p = w.player;
  if (e.phase === 1 && e.hp < e.maxHp * 0.5) enrage(w, e, 'Fenrisa enfurece!');
  const sp = d.spd * (e.phase === 2 ? 1.25 : 1) * spdM;
  const moves = e.phase === 1 ? ['lunge', 'swipe', 'lunge', 'howl'] : ['lunge', 'lunge', 'swipe', 'howl', 'lunge'];
  if (e.state === 'chase') {
    moveToward(w, e, p.x, p.y, sp * 0.8, dt);
    const want = moves[e.pattern % moves.length];
    const ready = e.t > (e.phase === 2 ? 0.7 : 1.1);
    if (ready) {
      const ang = Math.atan2(dy, dx);
      if (want === 'lunge') { tele(e, 'line', 0.65, { x: e.x, y: e.y - 6, r: 8, ang, len: 150 }); e.tx = Math.cos(ang); e.ty = Math.sin(ang); e.counter = 1; e.pattern++; }
      else if (want === 'swipe') { if (dd < 46) { tele(e, 'cone', 0.5, { x: e.x, y: e.y - 8, r: 44, ang }); e.tx = ang; e.counter = 2; e.pattern++; } else if (e.t > 2) { e.pattern++; } }
      else if (want === 'howl') { tele(e, 'circle', 1.0, { x: e.x, y: e.y, r: 54 }); e.counter = 3; e.pattern++; }
    }
  } else if (e.state === 'tele') {
    if (e.t >= (e.tele?.dur ?? 0.5) - 0.02) {
      if (e.counter === 1) { e.state = 'atk'; e.t = 0; Audio.sfx('swing'); }
      else if (e.counter === 2) { arcHit(w, e, e.tx, 46, 2.4, 1.3, 140); Audio.sfx('swing'); e.state = 'rec'; e.t = 0; }
      else {
        Audio.sfx('roar'); w.addShake(6);
        w.areas.push({ kind: 'ring', x: e.x, y: e.y, r: 54, t: 0, dur: 0.5, color: '#ffffff' });
        if (dist(p.x, p.y, e.x, e.y) < 54) hurtPlayer(w, d.atk * 0.8, e.x, e.y, 160);
        const alive = w.enemies.filter((x) => x.summoned && x.state !== 'dying').length;
        if (alive < 3) for (let i = 0; i < 2; i++) {
          const a = Math.random() * Math.PI * 2;
          const sx = clamp(e.x + Math.cos(a) * 50, 32, w.def.w * 16 - 32), sy = clamp(e.y + Math.sin(a) * 40, 32, w.def.h * 16 - 32);
          if (!w.boxFree(sx, sy, 5, 3)) continue;
          const wolf = new Enemy(ENEMIES[e.phase === 2 ? 'wolf_dark' : 'wolf'], sx, sy);
          wolf.summoned = true; wolf.aggro = true; wolf.hp = Math.round(wolf.maxHp * 0.5); wolf.maxHp = wolf.hp;
          w.enemies.push(wolf); w.burst(sx, sy, 8, '#aaa', { speed: 50, life: 0.4 });
        }
        e.state = 'rec'; e.t = 0;
      }
    }
  } else if (e.state === 'atk') {
    w.moveBody(e, e.tx * 235 * dt, e.ty * 235 * dt);
    contact(w, e, 1.2, 160);
    if (Math.random() < 0.5) w.burst(e.x, e.y, 1, '#bbb', { speed: 20, life: 0.3 });
    if (e.t > 0.42) { e.state = 'rec'; e.t = 0; }
  } else if (e.state === 'rec') { if (e.t > (e.phase === 2 ? 0.55 : 0.85)) { e.state = 'chase'; e.t = 0; } }
}

function bossSlime(w: World, e: Enemy, dt: number, dx: number, dy: number, dd: number, spdM: number) {
  const d = e.def;
  const p = w.player;
  const spawnBabies = (n: number) => {
    for (let i = 0; i < n; i++) {
      const a = (i / n) * Math.PI * 2 + Math.random();
      const sx = clamp(e.x + Math.cos(a) * 36, 24, w.def.w * 16 - 24), sy = clamp(e.y + Math.sin(a) * 30, 24, w.def.h * 16 - 24);
      if (!w.boxFree(sx, sy, 5, 3)) continue;
      const s = new Enemy(ENEMIES.slime, sx, sy); s.summoned = true; s.aggro = true; w.enemies.push(s); w.burst(sx, sy, 6, '#7ae88a', { speed: 40, life: 0.4 });
    }
  };
  if (e.phase === 1 && e.hp < e.maxHp * 0.66) { e.phase = 2; w.banner = { text: 'O Rei Slime se divide!', t: 0 }; Audio.sfx('roar'); spawnBabies(3); }
  if (e.phase === 2 && e.hp < e.maxHp * 0.33) { e.phase = 3; w.banner = { text: 'O Rei Slime enfurece!', t: 0 }; Audio.sfx('roar'); spawnBabies(4); }
  e.counter = Math.max(0, e.counter - dt);
  if (e.state === 'chase') {
    moveToward(w, e, p.x, p.y, d.spd * (1 + (e.phase - 1) * 0.2) * spdM, dt);
    if (e.counter <= 0 && dd < e.def.radius + 10) { contact(w, e, 0.7, 120); e.counter = 1.0; }
    if (e.t > 1.8 / (1 + (e.phase - 1) * 0.2)) {
      if (e.pattern++ % 3 === 2) { tele(e, 'circle', 0.5, { x: e.x, y: e.y, r: 10 }); e.tx = 0; }
      else { tele(e, 'circle', 0.9, { x: p.x, y: p.y, r: 40 }); e.tx = p.x; e.ty = p.y; e.counter = 0; (e as unknown as Record<string, number>).jump = 1; }
    }
  } else if (e.state === 'tele') {
    const jump = (e as unknown as Record<string, number>).jump === 1;
    if (e.t > (e.tele?.dur ?? 0.5) - 0.02) {
      if (!jump) {
        Audio.sfx('swing');
        const n = 4 + e.phase;
        for (let i = 0; i < n; i++) shootAt(w, e, 'slime', 80, 0.9, (i - (n - 1) / 2) * 0.28, { r: 5, color: '#7ae88a' });
        e.state = 'rec'; e.t = 0;
      } else { e.state = 'atk'; e.t = 0; e.hp = e.hp; (e as unknown as Record<string, number>).sx = e.x; (e as unknown as Record<string, number>).sy = e.y; Audio.sfx('swing'); }
    }
  } else if (e.state === 'atk') {
    const f = clamp(e.t / 0.65, 0, 1);
    const sx = (e as unknown as Record<string, number>).sx, sy = (e as unknown as Record<string, number>).sy;
    const nx = sx + (e.tx - sx) * f, ny = sy + (e.ty - sy) * f;
    if (w.boxFree(nx, ny, e.hw, e.hh)) { e.x = nx; e.y = ny; }
    e.z = Math.sin(f * Math.PI) * 46;
    if (f >= 1) {
      e.z = 0; slamAt(w, e.x, e.y, 40, d.atk * 1.6, '#7ae88a');
      if (e.phase >= 2) spawnBabies(e.phase === 3 ? 2 : 1);
      (e as unknown as Record<string, number>).jump = 0;
      e.state = 'rec'; e.t = 0;
    }
  } else if (e.state === 'rec') { if (e.t > 0.9) { e.state = 'chase'; e.t = 0; } }
}

function bossCrystal(w: World, e: Enemy, dt: number, dx: number, dy: number, dd: number, spdM: number) {
  const d = e.def;
  const p = w.player;
  if (e.phase === 1 && e.hp < e.maxHp * 0.5) enrage(w, e, 'Cristalion libera seu poder!');
  const fast = e.phase === 2 ? 0.7 : 1;
  const moves = e.phase === 1 ? ['slam', 'shards', 'ring', 'shards'] : ['slam', 'spiral', 'shards', 'ring', 'spiral'];
  if (e.state === 'chase') {
    if (dd > 56) moveToward(w, e, p.x, p.y, d.spd * spdM * (e.phase === 2 ? 1.4 : 1), dt);
    if (e.t > 1.5 * fast) {
      const m = moves[e.pattern++ % moves.length];
      e.counter = m === 'slam' ? 1 : m === 'shards' ? 2 : m === 'ring' ? 3 : 4;
      if (m === 'slam') tele(e, 'circle', 0.9 * fast + 0.2, { x: e.x, y: e.y, r: 52 });
      else tele(e, 'circle', 0.7 * fast + 0.2, { x: e.x, y: e.y, r: 14 });
    }
  } else if (e.state === 'tele') {
    if (e.t >= (e.tele?.dur ?? 0.6) - 0.02) {
      if (e.counter === 1) { slamAt(w, e.x, e.y, 52, d.atk * 1.2, '#8af0ff'); e.state = 'rec'; e.t = 0; }
      else if (e.counter === 2) {
        Audio.sfx('spirit');
        const n = e.phase === 2 ? 7 : 5;
        for (let i = 0; i < n; i++) {
          const a = Math.random() * Math.PI * 2, r = i === 0 ? 0 : 30 + Math.random() * 60;
          const tx = clamp(p.x + Math.cos(a) * r, 24, w.def.w * 16 - 24), ty = clamp(p.y + Math.sin(a) * r * 0.7, 24, w.def.h * 16 - 24);
          w.later(i * 0.18, () => delayedBlast(w, tx, ty, 22, 0.9, d.atk * 0.9, '#8af0ff'));
        }
        e.state = 'rec'; e.t = 0;
      } else if (e.counter === 3) {
        Audio.sfx('bolt');
        const n = 14;
        for (let i = 0; i < n; i++) { const a = (i / n) * Math.PI * 2; w.projs.push(new Proj(e.x, e.y - 16, Math.cos(a) * 85, Math.sin(a) * 85, 'e', d.atk * 0.7, 'shard', { r: 4, life: 3, kb: 60, color: '#8af0ff' })); }
        w.later(0.6, () => { if (e.state === 'dying') return; for (let i = 0; i < n; i++) { const a = ((i + 0.5) / n) * Math.PI * 2; w.projs.push(new Proj(e.x, e.y - 16, Math.cos(a) * 85, Math.sin(a) * 85, 'e', d.atk * 0.7, 'shard', { r: 4, life: 3, kb: 60, color: '#8af0ff' })); } });
        e.state = 'rec'; e.t = 0;
      } else {
        e.state = 'atk'; e.t = 0; e.tx = 0;
        Audio.sfx('roar');
      }
    }
  } else if (e.state === 'atk') {
    // spiral barrage
    e.tx += dt;
    if (e.tx > 0.09) { e.tx = 0; const a = e.t * 5; for (let k = 0; k < 2; k++) { const aa = a + k * Math.PI; w.projs.push(new Proj(e.x, e.y - 16, Math.cos(aa) * 80, Math.sin(aa) * 80, 'e', d.atk * 0.6, 'shard', { r: 4, life: 3, kb: 60, color: '#8af0ff' })); } }
    if (e.t > 2.6) { e.state = 'rec'; e.t = 0; }
  } else if (e.state === 'rec') { if (e.t > 0.9 * fast) { e.state = 'chase'; e.t = 0; } }
  G.flags['_boss_active'] = true;
}
