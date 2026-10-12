import { ITEMS, ItemStats } from './data/items';
import { SKILL_MAP } from './data/skills';

export interface Stats { maxHp: number; maxMp: number; atk: number; mag: number; def: number; crit: number; spd: number }

export interface QuestState { state: 'active' | 'done'; step: number; progress: number }

export interface SaveData {
  v: number;
  name: string; look: 'kai' | 'aiko';
  level: number; xp: number; hp: number; mp: number; sp: number; gold: number;
  ranks: Record<string, number>; slots: (string | null)[];
  inv: Record<string, number>;
  eq: { weapon: string | null; armor: string | null; acc: string | null };
  flags: Record<string, number | boolean | string>;
  quests: Record<string, QuestState>;
  map: string; px: number; py: number;
  spawnMap: string; spawnX: number; spawnY: number;
  playtime: number; kills: number;
  opened: Record<string, boolean>;
  saveTime: number;
}

export const MAX_LEVEL = 60;
export const xpToNext = (lv: number) => Math.floor(36 * Math.pow(lv, 1.55));

export class GameState {
  name = 'Kai';
  look: 'kai' | 'aiko' = 'kai';
  level = 1;
  xp = 0;
  hp = 100;
  mp = 40;
  sp = 2;
  gold = 40;
  ranks: Record<string, number> = { crescent: 1 };
  slots: (string | null)[] = ['crescent', null, null, null];
  inv: Record<string, number> = { potion: 3, herb: 2 };
  eq: SaveData['eq'] = { weapon: 'rusty_sword', armor: 'linen_tunic', acc: null };
  flags: Record<string, number | boolean | string> = {};
  quests: Record<string, QuestState> = {};
  map = 'casa_heroi';
  px = 5 * 16;
  py = 7 * 16;
  spawnMap = 'casa_heroi';
  spawnX = 5 * 16;
  spawnY = 7 * 16;
  playtime = 0;
  kills = 0;
  opened: Record<string, boolean> = {};
  allies: string[] = [];

  // ---- derived ----
  equipBonus(): ItemStats {
    const b: ItemStats = {};
    for (const id of Object.values(this.eq)) {
      if (!id) continue;
      const st = ITEMS[id]?.stats;
      if (!st) continue;
      for (const k of Object.keys(st) as (keyof ItemStats)[]) b[k] = (b[k] ?? 0) + (st[k] ?? 0);
    }
    return b;
  }

  stats(): Stats {
    const L = this.level;
    const b = this.equipBonus();
    return {
      maxHp: Math.round(84 + 16 * L + (b.hp ?? 0)),
      maxMp: Math.round(32 + 5 * L + (b.mp ?? 0)),
      atk: Math.round(10 + 2.7 * L + (b.atk ?? 0)),
      mag: Math.round(10 + 2.9 * L + (b.mag ?? 0)),
      def: Math.round(3 + 1.7 * L + (b.def ?? 0)),
      crit: 5 + (b.crit ?? 0),
      spd: 1 + (b.spd ?? 0) / 100,
    };
  }

  flag(k: string): number | boolean | string | undefined {
    return this.flags[k];
  }
  has(k: string) {
    return !!this.flags[k];
  }

  // ---- inventory ----
  count(id: string) {
    return this.inv[id] ?? 0;
  }
  addItem(id: string, n = 1) {
    this.inv[id] = (this.inv[id] ?? 0) + n;
    if (this.inv[id] <= 0) delete this.inv[id];
  }

  /** Adds XP; returns number of levels gained. */
  gainXp(n: number): number {
    let gained = 0;
    if (this.level >= MAX_LEVEL) return 0;
    this.xp += n;
    while (this.level < MAX_LEVEL && this.xp >= xpToNext(this.level)) {
      this.xp -= xpToNext(this.level);
      this.level++;
      this.sp += 1;
      gained++;
    }
    if (gained) {
      const s = this.stats();
      this.hp = s.maxHp;
      this.mp = s.maxMp;
    }
    return gained;
  }

  skillRank(id: string) {
    return this.ranks[id] ?? 0;
  }
  canLearn(id: string): { ok: boolean; why?: string } {
    const s = SKILL_MAP[id];
    const r = this.skillRank(id);
    if (r >= s.maxRank) return { ok: false, why: 'Nível máximo' };
    if (this.level < s.reqLevel) return { ok: false, why: `Requer nível ${s.reqLevel}` };
    if (this.sp < 1) return { ok: false, why: 'Sem pontos de habilidade' };
    return { ok: true };
  }
  learn(id: string) {
    if (!this.canLearn(id).ok) return false;
    this.sp--;
    this.ranks[id] = this.skillRank(id) + 1;
    if (this.ranks[id] === 1 && !this.slots.includes(id)) {
      const free = this.slots.indexOf(null);
      if (free >= 0) this.slots[free] = id;
    }
    return true;
  }

  // ---- quests ----
  startQuest(id: string) {
    if (!this.quests[id]) this.quests[id] = { state: 'active', step: 0, progress: 0 };
  }
  questStep(id: string, step: number) {
    const q = this.quests[id];
    if (q && q.state === 'active' && step > q.step) {
      q.step = step;
      q.progress = 0;
    }
  }
  completeQuest(id: string) {
    const q = this.quests[id];
    if (q) q.state = 'done';
  }
  questActive(id: string) {
    return this.quests[id]?.state === 'active';
  }
  questDone(id: string) {
    return this.quests[id]?.state === 'done';
  }

  // ---- save ----
  serialize(): SaveData {
    return {
      v: 1, name: this.name, look: this.look, level: this.level, xp: this.xp, hp: this.hp, mp: this.mp, sp: this.sp, gold: this.gold,
      ranks: this.ranks, slots: this.slots, inv: this.inv, eq: this.eq, flags: this.flags, quests: this.quests,
      map: this.map, px: this.px, py: this.py, spawnMap: this.spawnMap, spawnX: this.spawnX, spawnY: this.spawnY,
      playtime: this.playtime, kills: this.kills, opened: this.opened, saveTime: Date.now(),
    };
  }
  load(d: SaveData) {
    Object.assign(this, d);
    this.allies = Array.isArray((d.flags as Record<string, unknown>)['_allies']) ? [] : this.allies;
  }
}

const KEY = 'aetheria_save_';
export const Saves = {
  slots: 3,
  read(slot: number): SaveData | null {
    try {
      const s = localStorage.getItem(KEY + slot);
      return s ? (JSON.parse(s) as SaveData) : null;
    } catch {
      return null;
    }
  },
  write(slot: number, gs: GameState) {
    try {
      localStorage.setItem(KEY + slot, JSON.stringify(gs.serialize()));
      return true;
    } catch {
      return false;
    }
  },
  erase(slot: number) {
    try { localStorage.removeItem(KEY + slot); } catch { /* ignore */ }
  },
  readAuto(): SaveData | null { try { const s = localStorage.getItem('aetheria_auto'); return s ? (JSON.parse(s) as SaveData) : null; } catch { return null; } },
  writeAuto(gs: GameState) { try { localStorage.setItem('aetheria_auto', JSON.stringify(gs.serialize())); } catch { /* ignore */ } },
  latest(): SaveData | null { let best = this.readAuto(); for (let i = 0; i < this.slots; i++) { const d = this.read(i); if (d && (!best || d.saveTime > best.saveTime)) best = d; } return best; },
  anySave() {
    if (this.readAuto()) return true;
    for (let i = 0; i < this.slots; i++) if (this.read(i)) return true;
    return false;
  },
};

export const G = new GameState();
export function resetGame() {
  const fresh = new GameState();
  Object.assign(G, fresh);
}
