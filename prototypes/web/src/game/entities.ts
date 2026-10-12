import { Dir, DIR_VEC } from '../engine/util';
import { makeSheet, Look, HERO_LOOKS, NPC_LOOKS, FOOT_X, FOOT_Y, CW, CH } from '../art/characters';
import { monsterArt, MonsterArt } from '../art/monsters';
import { EnemyDef } from './data/enemies';
import type { NpcDef, ChestDef } from './world/map';
import type { Elem } from './data/skills';

export class Body {
  x = 0; y = 0; vx = 0; vy = 0;
  hw = 5; hh = 3;       // footprint half extents for tile collision
  dir: Dir = 'down';
  dead = false;
}

export type PState = 'idle' | 'walk' | 'attack' | 'roll' | 'cast' | 'hurt' | 'dead' | 'phase';

export class Player extends Body {
  state: PState = 'idle';
  t = 0;
  anim = 0;
  combo = 0;
  comboWindow = 0;
  queued = false;
  hitSet = new Set<object>();
  swingDone = false;
  rollDx = 0; rollDy = 0; rollCd = 0;
  invuln = 0;
  flash = 0;
  cd = [0, 0, 0, 0];
  gcd = 0;
  shield = 0; shieldT = 0;
  buffT = 0; buffMul = 1;
  slowT = 0;
  burnT = 0;
  castT = 0;
  castKind = '';
  phaseT = 0;
  mpRegen = 0;
  hurtT = 0;
  sheetKey = 'hero_kai';
  look: Look = HERO_LOOKS.kai;
  setLook(k: 'kai' | 'aiko') { this.sheetKey = 'hero_' + k; this.look = HERO_LOOKS[k]; }
  get sheet() { return makeSheet(this.sheetKey, this.look); }
}

export type EState = 'idle' | 'chase' | 'tele' | 'atk' | 'rec' | 'stun' | 'dying';

export class Enemy extends Body {
  hp: number; maxHp: number;
  state: EState = 'idle';
  t = 0;
  art: MonsterArt;
  flash = 0; stun = 0; slow = 0; burn = 0; burnDmg = 0; freeze = 0;
  kx = 0; ky = 0;
  aggro = false;
  home: { x: number; y: number };
  face = 1;
  pattern = 0;
  phase = 1;
  anim = Math.random() * 10;
  tele: { kind: 'circle' | 'line' | 'cone'; x: number; y: number; r: number; ang?: number; len?: number; t: number; dur: number } | null = null;
  tx = 0; ty = 0;  // generic target storage
  spawnId?: string;
  counter = 0;
  z = 0;           // vertical offset (jumps)
  summoned = false;
  deathT = 0;
  constructor(public def: EnemyDef, x: number, y: number, lvScale = 1) {
    super();
    this.x = x; this.y = y;
    this.home = { x, y };
    this.maxHp = Math.round(def.hp * lvScale);
    this.hp = this.maxHp;
    this.art = monsterArt(def.art);
    this.hw = Math.max(4, Math.min(12, def.radius * 0.7));
    this.hh = Math.max(3, Math.min(8, def.radius * 0.4));
  }
  get cx() { return this.x; }
  get cy() { return this.y - this.def.hitH; }
}

export class Npc extends Body {
  anim = 0; wanderT = 1 + Math.random() * 3; moving = false;
  tx: number | null = null; ty: number | null = null;  // scripted move target
  homeX: number; homeY: number;
  look: Look;
  hidden = false;
  constructor(public def: NpcDef) {
    super();
    this.x = def.tx * 16 + 8; this.y = def.ty * 16 + 14;
    this.homeX = this.x; this.homeY = this.y;
    this.dir = def.dir ?? 'down';
    this.look = (NPC_LOOKS as Record<string, Look>)[def.look] ?? NPC_LOOKS.villager_m;
    this.hh = 3;
  }
  get sheet() { return makeSheet('npc_' + this.def.look, this.look); }
}

export class Ally extends Body {
  anim = 0; atkT = 1.5; trail: { x: number; y: number }[] = [];
  state: 'follow' | 'cast' = 'follow'; castT = 0; flashT = 0;
  look: Look;
  constructor(public id: string) {
    super();
    this.look = (NPC_LOOKS as Record<string, Look>)[id] ?? NPC_LOOKS.lyra;
  }
  get sheet() { return makeSheet('npc_' + this.id, this.look); }
}

export class ChestE {
  opened = false;
  constructor(public def: ChestDef) {}
  get x() { return this.def.tx * 16 + 8; }
  get y() { return this.def.ty * 16 + 15; }
}

export class Pickup {
  vz = 90; z = 0; t = 0; magnet = false; dead = false;
  vx = 0; vy = 0;
  constructor(public x: number, public y: number, public kind: 'gold' | 'item' | 'heart' | 'mana', public id: string, public amount: number) {
    const a = Math.random() * Math.PI * 2;
    this.vx = Math.cos(a) * 30; this.vy = Math.sin(a) * 20;
  }
}

export type ProjKind = 'orb' | 'arrow' | 'wave' | 'fire' | 'ice' | 'spore' | 'shard' | 'slime' | 'dark' | 'bolt';
export class Proj {
  hit = new Set<object>();
  dead = false;
  age = 0;
  constructor(
    public x: number, public y: number, public vx: number, public vy: number,
    public team: 'p' | 'e', public dmg: number, public kind: ProjKind,
    public opts: { r?: number; life?: number; pierce?: number; elem?: Elem; explode?: number; slow?: number; burn?: number; stun?: number; color?: string; kb?: number; z?: number; homing?: number } = {},
  ) {}
  get r() { return this.opts.r ?? 4; }
}

export interface Particle { x: number; y: number; vx: number; vy: number; life: number; max: number; color: string; size: number; grav: number; fade?: boolean; z?: number }
export interface DmgText { x: number; y: number; t: number; str: string; color: string; big: boolean }

export interface AreaFx {
  kind: 'ring' | 'warn' | 'slam' | 'nova' | 'meteor' | 'spirits' | 'flash' | 'beam' | 'bolt';
  x: number; y: number; r: number; t: number; dur: number; color: string;
  fire?: () => void; fired?: boolean; delay?: number;
  pts?: [number, number][];
  owner?: object;
  ang?: number;
}

export function drawShadow(g: CanvasRenderingContext2D, x: number, y: number, rx: number, ry = rx * 0.4, a = 0.28) {
  g.fillStyle = `rgba(10,4,24,${a})`;
  for (let j = -ry; j <= ry; j++) {
    const w = Math.round(rx * Math.sqrt(Math.max(0, 1 - (j * j) / (ry * ry + 0.01))));
    g.fillRect(Math.round(x - w), Math.round(y + j), w * 2, 1);
  }
}

export function drawChar(g: CanvasRenderingContext2D, sheet: ReturnType<typeof makeSheet>, anim: string, dir: Dir, frame: number, x: number, y: number, flash = false, alpha = 1) {
  const f = flash ? sheet.flash(anim, dir, frame) : sheet.frame(anim, dir, frame);
  const prev = g.globalAlpha;
  g.globalAlpha = prev * alpha;
  g.drawImage(f, Math.round(x - FOOT_X), Math.round(y - FOOT_Y));
  g.globalAlpha = prev;
}

export { DIR_VEC, CW, CH };
