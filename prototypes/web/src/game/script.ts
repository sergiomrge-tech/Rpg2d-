import { Audio } from '../engine/audio';
import { Dir, DIR_VEC } from '../engine/util';
import { G, Saves } from './state';
import { ITEMS } from './data/items';
import { QUESTS } from './data/quests';
import { ENEMIES } from './data/enemies';
import { Enemy, ChestE, Npc } from './entities';
import { levelUpFx } from './world/combat';
import { DialogModal, ChoiceModal } from './ui/dialog';
import { ShopModal } from './ui/shop';
import { SaveModal } from './ui/saveui';
import type { World } from './world/world';
import type { ObjPlace } from './world/map';
import type { Emotion } from '../art/portraits';
import { TS } from '../art/tiles';

export interface SayOpts { look?: string; emo?: Emotion }

/** API used by story scripts (all async, awaitable). */
export class ScriptCtx {
  constructor(public world: World) {}
  get gs() { return G; }
  get G() { return G; }

  async say(who: string, text: string, look?: string | SayOpts, emo?: Emotion): Promise<void> {
    let lk: string | null = null, em: Emotion = emo ?? 'neutral';
    if (typeof look === 'string') lk = look; else if (look) { lk = look.look ?? null; em = look.emo ?? em; }
    if (who === '__hero') { who = G.name; lk = 'hero'; }
    if (lk === null && who && who === G.name) lk = 'hero';
    const m = new DialogModal(who, text, lk, em);
    await this.world.openModal(m);
  }
  hero(text: string, emo: Emotion = 'neutral') { return this.say(G.name, text, 'hero', emo); }
  narrate(text: string) { return this.say('', text); }
  async choice(options: string[]): Promise<number> { return this.world.openModal(new ChoiceModal(options)); }

  async give(id: string, n = 1, silent = false) {
    G.addItem(id, n);
    if (!silent) { Audio.sfx('chest'); this.world.toast(`${ITEMS[id]?.name ?? id}${n > 1 ? ' x' + n : ''}`, ITEMS[id]?.icon, '#ffe066'); await this.say('', `Você recebeu ${ITEMS[id]?.name ?? id}${n > 1 ? ' x' + n : ''}!`); }
  }
  take(id: string, n = 1) { G.addItem(id, -n); }
  gold(n: number) { G.gold += n; if (n > 0) { Audio.sfx('coin'); this.world.toast(`+${n} G`, 'coin', '#ffd84a'); } }
  xp(n: number) { const lv = G.gainXp(n); this.world.toast(`+${n} XP`, 'star', '#9ad8ff'); if (lv) levelUpFx(this.world); }
  flag(k: string, v: number | boolean | string = true) { G.flags[k] = v; }
  has(k: string) { return G.has(k); }

  startQuest(id: string) {
    if (G.quests[id]) return;
    G.startQuest(id);
    Audio.sfx('ui_ok');
    this.world.toast(`Nova missão: ${QUESTS[id].name}`, 'scroll', '#ffe066');
  }
  questStep(id: string, step: number) { if (G.quests[id] && G.quests[id].step < step && G.questActive(id)) { G.questStep(id, step); this.world.toast(`Missão atualizada: ${QUESTS[id].name}`, 'scroll', '#9ad8ff'); } }
  completeQuest(id: string) {
    if (!G.questActive(id)) return;
    G.completeQuest(id);
    const r = QUESTS[id].reward;
    Audio.sfx('levelup');
    this.world.banner = { text: 'Missão Concluída', sub: QUESTS[id].name, t: 0 };
    if (r) {
      if (r.gold) G.gold += r.gold;
      if (r.items) for (const [i, n] of r.items) G.addItem(i, n);
      if (r.xp) { if (G.gainXp(r.xp)) levelUpFx(this.world); }
    }
  }

  async wait(sec: number) { await new Promise<void>((res) => this.world.later(sec, res)); }
  async fadeOut(speed = 2) { await this.world.fade(1, speed); }
  async fadeIn(speed = 2) { await this.world.fade(0, speed); }
  shake(a = 6) { this.world.addShake(a); }
  music(name: string) { this.world.musicOverride = name || null; Audio.music(name || this.world.def.music); }
  sfx(n: string) { Audio.sfx(n); }
  banner(text: string, sub?: string) { this.world.banner = { text, sub, t: 0 }; }
  toast(t: string, icon?: string, color = '#fff') { this.world.toast(t, icon, color); }
  lock() { this.world.locked = true; }
  unlock() { this.world.locked = false; }

  async warp(map: string, tx: number, ty: number, dir: Dir = 'down') {
    await this.world.fade(1, 3);
    this.world.loadMap(map, tx, ty, dir);
    await this.world.fade(0, 3);
  }
  face(dir: Dir) { this.world.player.dir = dir; }
  npc(id: string): Npc | undefined { return this.world.npcs.find((n) => n.def.id === id); }
  async moveNpc(id: string, tx: number, ty: number) {
    const n = this.npc(id); if (!n) return;
    n.tx = tx * TS + 8; n.ty = ty * TS + 12;
    while (n.tx !== null) await this.wait(0.05);
  }
  async moveHero(tx: number, ty: number, speed = 50) {
    const p = this.world.player;
    const gx = tx * TS + 8, gy = ty * TS + 12;
    let guard = 0;
    while (Math.hypot(gx - p.x, gy - p.y) > 2 && guard++ < 600) {
      const dx = gx - p.x, dy = gy - p.y, d = Math.hypot(dx, dy);
      p.x += (dx / d) * speed * 0.05; p.y += (dy / d) * speed * 0.05;
      p.dir = Math.abs(dx) > Math.abs(dy) ? (dx < 0 ? 'left' : 'right') : (dy < 0 ? 'up' : 'down');
      p.state = 'walk'; p.anim += 0.05 * 8.5;
      await this.wait(0.05);
    }
    p.state = 'idle';
  }
  async camTo(tx: number, ty: number, sec = 1) {
    const w = this.world;
    const startX = w.cam.x, startY = w.cam.y;
    w.locked = true;
    const steps = Math.ceil(sec / 0.03);
    const tgtX = tx * TS - 192, tgtY = ty * TS - 108;
    for (let i = 1; i <= steps; i++) { const f = i / steps; w.cam.x = startX + (tgtX - startX) * f; w.cam.y = startY + (tgtY - startY) * f; w.clampCam(); await this.wait(0.03); }
  }
  spawn(id: string, tx: number, ty: number, aggro = true): Enemy {
    const e = new Enemy(ENEMIES[id], tx * TS + 8, ty * TS + 12);
    e.aggro = aggro; e.summoned = false;
    this.world.enemies.push(e);
    this.world.burst(e.x, e.y - 8, 10, ['#c080ff', '#fff'], { speed: 60, life: 0.5 });
    return e;
  }
  async waitClear(filter?: (e: Enemy) => boolean) {
    while (this.world.enemies.some((e) => e.state !== 'dying' && !e.dead && (!filter || filter(e)))) await this.wait(0.2);
  }
  enemiesLeft() { return this.world.enemies.filter((e) => e.state !== 'dying' && !e.dead).length; }
  async shop(stock: string[], title = 'Loja') { await this.world.openModal(new ShopModal(stock, title)); }
  async allyJoin(id: string) { G.flags['ally_' + id] = true; this.world.syncAllies(this.world.player.x, this.world.player.y); this.world.toast(`${id[0].toUpperCase() + id.slice(1)} entrou no grupo!`, 'star', '#ffe066'); Audio.sfx('levelup'); }
  heal() { const s = G.stats(); G.hp = s.maxHp; G.mp = s.maxMp; }
  async save() { await this.world.openModal(new SaveModal(this.world, 'save')); }
  setSpawn() { G.spawnMap = this.world.def.id; G.spawnX = this.world.player.x; G.spawnY = this.world.player.y; }
  async cutsceneBars(on: boolean) { this.world.letterbox = on ? 1 : 0; await this.wait(0.01); }
  async chapterEnd(title: string, sub: string) { await this.world.chapterCard(title, sub); }
}

/** Event bus + story wiring lives in data/story.ts; this class glues the world to it. */
export class Script {
  ctx: ScriptCtx;
  running = false;
  hooks: { onMapEnter: (ctx: ScriptCtx, mapId: string) => Promise<void> | void; onKill: (ctx: ScriptCtx, e: Enemy) => void; onItem: (ctx: ScriptCtx, id: string) => void; objectTalk: Record<string, (ctx: ScriptCtx) => Promise<void>> } = {
    onMapEnter: () => {}, onKill: () => {}, onItem: () => {}, objectTalk: {},
  };
  constructor(public world: World) { this.ctx = new ScriptCtx(world); }

  async run(fn: () => Promise<void>) {
    if (this.running) return;
    this.running = true;
    this.world.locked = true;
    try { await fn(); } catch (e) { console.error('script error', e); }
    this.world.locked = false;
    this.running = false;
  }

  onMapEnter() {
    const d = this.world.def;
    const h = this.hooks.onMapEnter;
    void this.run(async () => { await h(this.ctx, d.id); if (d.onEnter) await d.onEnter(this.ctx); });
  }
  onKill(e: Enemy) {
    if (e.spawnId && e.def.boss) G.flags['dead_' + e.spawnId] = true;
    else if (e.spawnId && this.world.def.spawns.find((s) => s.id === e.spawnId)?.once) G.flags['dead_' + e.spawnId] = true;
    this.hooks.onKill(this.ctx, e);
  }
  onItem(id: string) { this.hooks.onItem(this.ctx, id); }

  hasObjectTalk(o: ObjPlace) { return !!this.hooks.objectTalk[o.id ?? o.type + ':' + o.tx + ',' + o.ty] || !!this.hooks.objectTalk[o.type]; }
  async objectTalk(o: ObjPlace) { const f = this.hooks.objectTalk[o.id ?? o.type + ':' + o.tx + ',' + o.ty] ?? this.hooks.objectTalk[o.type]; if (f) await f(this.ctx); }

  async openChest(c: ChestE) {
    if (c.opened) return;
    await this.run(async () => {
      c.opened = true;
      G.opened[this.world.def.id + ':' + c.def.id] = true;
      Audio.sfx('chest');
      this.world.burst(c.x, c.y - 10, 16, ['#ffd84a', '#fff'], { speed: 70, life: 0.7, up: 30 });
      await this.ctx.wait(0.35);
      if (c.def.gold) { this.ctx.gold(c.def.gold); await this.ctx.say('', `Você encontrou ${c.def.gold} G!`); }
      if (c.def.item) { await this.ctx.give(c.def.item, c.def.count ?? 1); }
    });
  }

  async useSaveCrystal() {
    await this.run(async () => {
      this.ctx.heal();
      this.ctx.setSpawn();
      Audio.sfx('save');
      this.world.burst(this.world.player.x, this.world.player.y - 10, 24, ['#7ae8ff', '#fff'], { speed: 60, life: 1, up: 50, size: 2 });
      await this.ctx.say('', 'O Cristal de Salvamento ressoa com a luz da Aurora. HP e MP restaurados. Ponto de retorno definido.');
      const c = await this.ctx.choice(['Salvar o jogo', 'Continuar']);
      if (c === 0) await this.ctx.save();
    });
  }
}
void DIR_VEC; void Saves;
