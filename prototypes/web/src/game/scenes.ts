import { VW, VH, text, panel, measure } from '../engine/display';
import { Input } from '../engine/input';
import { Audio } from '../engine/audio';
import { mk } from '../art/pixel';
import { makeSheet, HERO_LOOKS, FOOT_X, FOOT_Y, NPC_LOOKS } from '../art/characters';
import { portrait } from '../art/portraits';
import { World } from './world/world';
import { installStory } from './data/story';
import { G, resetGame, Saves } from './state';
import { MenuModal } from './ui/menu';
import { SaveModal, GameOverModal } from './ui/saveui';
import { Rng, fmtTime } from '../engine/util';
import { getMap } from './world/maps';
import './maps';

export interface Scene {
  enter?(): void;
  update(dt: number): void;
  draw(g: CanvasRenderingContext2D): void;
  drawUI(u: CanvasRenderingContext2D): void;
}

export const SceneMgr = {
  current: null as Scene | null,
  go(s: Scene) { this.current = s; s.enter?.(); },
};

// ------------------------------------------------------------------ Game
export class GameScene implements Scene {
  world = new World();
  constructor(public mode: 'new' | 'load') {}
  enter() {
    const w = this.world;
    installStory(w);
    w.player.setLook(G.look);
    w.onGameOver = () => this.gameOver();
    w.onWarped = () => Saves.writeAuto(G);
    w.fadeA = 1; w.fadeTo = 0;
    w.loadMap(G.map, Math.floor(G.px / 16), Math.floor(G.py / 16), 'down');
    if (this.mode === 'new') { w.fadeA = 1; w.fadeTo = 0; }
    (window as unknown as { __rpg: unknown }).__rpg = { G, world: w };
  }
  gameOverOpen = false;
  async gameOver() {
    if (this.gameOverOpen) return;
    this.gameOverOpen = true;
    const w = this.world;
    const r = await w.openModal(new GameOverModal());
    this.gameOverOpen = false;
    if (r === 1) { SceneMgr.go(new TitleScene()); return; }
    const s = G.stats();
    G.hp = s.maxHp; G.mp = s.maxMp; G.gold = Math.floor(G.gold * 0.9);
    w.player.state = 'idle'; w.player.invuln = 1.5;
    w.musicOverride = null;
    await w.fade(1, 3);
    w.loadMap(G.spawnMap, Math.floor(G.spawnX / 16), Math.floor(G.spawnY / 16), 'down');
    w.locked = false;
    await w.fade(0, 3);
  }
  update(dt: number) {
    const w = this.world;
    if (!w.modals.length && !w.locked && w.player.state !== 'dead' && Input.pressed('menu')) {
      Audio.sfx('ui_ok');
      Input.eat('menu', 'cancel', 'confirm');
      void w.openModal(new MenuModal(w, () => SceneMgr.go(new TitleScene())));
    }
    w.update(dt);
  }
  draw(g: CanvasRenderingContext2D) { this.world.draw(g); }
  drawUI(u: CanvasRenderingContext2D) { this.world.drawUI(u); }
}

export function startNewGame(name: string, look: 'kai' | 'aiko') {
  resetGame();
  G.name = name || (look === 'kai' ? 'Kai' : 'Aiko');
  G.look = look;
  const s = G.stats();
  G.hp = s.maxHp; G.mp = s.maxMp;
  Audio.stopMusic();
  SceneMgr.go(new GameScene('new'));
}
export function continueGame(d: ReturnType<typeof Saves.latest>) {
  if (!d) return;
  resetGame();
  G.load(d);
  Audio.stopMusic();
  SceneMgr.go(new GameScene('load'));
}

// ------------------------------------------------------------------ Title
type TState = 'press' | 'menu' | 'select' | 'name' | 'load' | 'options' | 'credits';

export class TitleScene implements Scene {
  t = 0;
  st: TState = 'press';
  cur = 0;
  heroSel = 0;
  nameBuf = '';
  stars: { x: number; y: number; s: number; ph: number }[] = [];
  parts: { x: number; y: number; vx: number; vy: number; ph: number }[] = [];
  bg!: HTMLCanvasElement;
  loadSel = 0;
  private keyHandler = (e: KeyboardEvent) => this.onKey(e);
  private nameDone = false;

  enter() {
    const r = new Rng(9);
    for (let i = 0; i < 110; i++) this.stars.push({ x: r.int(0, VW), y: r.int(0, 120), s: r.next() < 0.15 ? 2 : 1, ph: r.range(0, 7) });
    for (let i = 0; i < 40; i++) this.parts.push({ x: r.range(0, VW), y: r.range(0, VH), vx: r.range(-4, 4), vy: -r.range(6, 18), ph: r.range(0, 7) });
    this.bg = this.paintBg();
    Audio.music('title');
    window.addEventListener('keydown', this.keyHandler);
  }
  leave() { window.removeEventListener('keydown', this.keyHandler); }

  paintBg() {
    const [c, g] = mk(VW, VH);
    const bands = ['#07031a', '#0a0522', '#0e0830', '#150a3e', '#1e0e4c', '#2c1458', '#431a66', '#612270', '#8a2e78', '#b83f7a', '#e0587a', '#f58a7a', '#ffb88a'];
    const bh = 150 / bands.length;
    bands.forEach((col, i) => { g.fillStyle = col; g.fillRect(0, Math.floor(i * bh), VW, Math.ceil(bh) + 1); });
    // dithered band transitions
    for (let i = 1; i < bands.length; i++) { const y = Math.floor(i * bh); g.fillStyle = bands[i]; for (let x = 0; x < VW; x += 2) g.fillRect(x + (i % 2), y - 1, 1, 1); for (let x = 0; x < VW; x += 4) g.fillRect(x, y - 2, 1, 1); }
    // mountains (3 layers)
    const layer = (base: number, amp: number, col: string, seed: number, f1: number) => {
      g.fillStyle = col;
      for (let x = 0; x < VW; x++) {
        const h = base - Math.abs(Math.sin(x * f1 + seed)) * amp - Math.sin(x * 0.011 + seed * 2) * amp * 0.7;
        g.fillRect(x, Math.floor(h), 1, VH - Math.floor(h));
      }
    };
    layer(148, 22, '#3a1a5a', 1, 0.03); layer(160, 20, '#251048', 2.5, 0.045); layer(176, 14, '#150a30', 4, 0.06);
    // far lights (village)
    for (let i = 0; i < 9; i++) { g.fillStyle = '#ffd88a'; g.fillRect(40 + i * 17 + (i % 3) * 3, 162 + (i % 2) * 3, 1, 1); }
    // foreground cliff with grass
    g.fillStyle = '#0b0618'; g.fillRect(0, 186, VW, 30);
    g.fillStyle = '#0b0618';
    for (let x = 0; x < 150; x++) { const h = 182 - Math.floor(Math.sin(x * 0.04) * 4 + (x < 120 ? 0 : (x - 120) * 0.4)); g.fillRect(x, h, 1, VH - h); }
    g.fillStyle = '#1b4a3a'; for (let x = 0; x < 128; x += 2) { const h = 182 - Math.floor(Math.sin(x * 0.04) * 4); g.fillRect(x, h, 2, 1 + (x % 3 === 0 ? 1 : 0)); if (x % 5 === 0) g.fillRect(x, h - 1, 1, 1); }
    g.fillStyle = '#2f7a4a'; for (let x = 1; x < 126; x += 3) { const h = 182 - Math.floor(Math.sin(x * 0.04) * 4); g.fillRect(x, h - 1, 1, 1); }
    return c;
  }

  onKey(e: KeyboardEvent) {
    if (this.st !== 'name') return;
    if (e.key === 'Enter') { this.nameDone = true; return; }
    if (e.key === 'Backspace') { this.nameBuf = this.nameBuf.slice(0, -1); e.preventDefault(); }
    else if (e.key.length === 1 && /[\p{L}\p{N} '-]/u.test(e.key) && this.nameBuf.length < 10) { this.nameBuf += e.key; Audio.sfx('ui_move'); e.preventDefault(); }
  }

  update(dt: number) {
    this.t += dt;
    for (const p of this.parts) { p.x += p.vx * dt + Math.sin(this.t + p.ph) * 0.2; p.y += p.vy * dt; if (p.y < -4) { p.y = VH + 4; p.x = Math.random() * VW; } }
    const n = (len: number) => {
      if (Input.rep('up')) { this.cur = (this.cur + len - 1) % len; Audio.sfx('ui_move'); }
      if (Input.rep('down')) { this.cur = (this.cur + 1) % len; Audio.sfx('ui_move'); }
    };
    switch (this.st) {
      case 'press':
        if (Input.pressed('confirm') || Input.pressed('attack') || Input.pressed('menu') || Input.pressed('interact')) { Audio.sfx('ui_ok'); this.st = 'menu'; this.cur = Saves.anySave() ? 1 : 0; }
        break;
      case 'menu': {
        const items = this.menuItems();
        n(items.length);
        if (Input.pressed('confirm')) {
          Audio.sfx('ui_ok');
          const it = items[this.cur];
          if (it === 'Novo Jogo') { this.st = 'select'; this.heroSel = 0; }
          else if (it === 'Continuar') { const d = Saves.latest(); this.leave(); continueGame(d); }
          else if (it === 'Carregar') { this.st = 'load'; this.loadSel = 0; }
          else if (it === 'Opções') { this.st = 'options'; this.cur = 0; }
          else if (it === 'Créditos') this.st = 'credits';
        }
        break;
      }
      case 'select':
        if (Input.rep('left') || Input.rep('right')) { this.heroSel = 1 - this.heroSel; Audio.sfx('ui_move'); }
        if (Input.pressed('cancel')) { this.st = 'menu'; Audio.sfx('ui_back'); }
        if (Input.pressed('confirm')) { Audio.sfx('ui_ok'); this.st = 'name'; this.nameBuf = ''; this.nameDone = false; Input.clearAll(); }
        break;
      case 'name':
        if (Input.pressed('cancel') && this.nameBuf === '' && !this.nameDone) { this.st = 'select'; }
        if (this.nameDone) {
          this.nameDone = false;
          if ('ontouchstart' in window && !this.nameBuf) { const v = window.prompt('Nome do herói:', this.heroSel === 0 ? 'Kai' : 'Aiko'); if (v) this.nameBuf = v.slice(0, 10); }
          Audio.sfx('ui_ok'); this.leave(); startNewGame(this.nameBuf.trim(), this.heroSel === 0 ? 'kai' : 'aiko');
        }
        break;
      case 'load': {
        if (Input.rep('up')) { this.loadSel = (this.loadSel + 3) % 4; Audio.sfx('ui_move'); }
        if (Input.rep('down')) { this.loadSel = (this.loadSel + 1) % 4; Audio.sfx('ui_move'); }
        if (Input.pressed('cancel')) { this.st = 'menu'; Audio.sfx('ui_back'); }
        if (Input.pressed('confirm')) { const d = this.loadSel === 3 ? Saves.readAuto() : Saves.read(this.loadSel); if (d) { Audio.sfx('ui_ok'); this.leave(); continueGame(d); } else Audio.sfx('error'); }
        break;
      }
      case 'options': {
        n(3);
        const adj = (Input.rep('left') ? -1 : 0) + (Input.rep('right') ? 1 : 0);
        if (this.cur === 0 && adj) Audio.setVolumes(Math.max(0, Math.min(1, Math.round((Audio.musicVol + adj * 0.1) * 10) / 10)), Audio.sfxVol);
        if (this.cur === 1 && adj) { Audio.setVolumes(Audio.musicVol, Math.max(0, Math.min(1, Math.round((Audio.sfxVol + adj * 0.1) * 10) / 10))); Audio.sfx('ui_ok'); }
        if (this.cur === 2 && Input.pressed('confirm')) Audio.toggleMute();
        if (Input.pressed('cancel')) { this.st = 'menu'; this.cur = 0; Audio.sfx('ui_back'); }
        break;
      }
      case 'credits':
        if (Input.pressed('cancel') || Input.pressed('confirm')) { this.st = 'menu'; Audio.sfx('ui_back'); }
        break;
    }
  }

  menuItems() {
    const a = ['Novo Jogo'];
    if (Saves.anySave()) a.unshift('Continuar');
    if (Saves.anySave()) a.push('Carregar');
    a.push('Opções', 'Créditos');
    return a;
  }

  draw(g: CanvasRenderingContext2D) {
    g.drawImage(this.bg, 0, 0);
    // stars
    for (const s of this.stars) { const a = 0.4 + 0.6 * Math.abs(Math.sin(this.t * 1.5 + s.ph)); g.globalAlpha = a * (1 - s.y / 150); g.fillStyle = '#fff'; g.fillRect(s.x, s.y, s.s, s.s); }
    g.globalAlpha = 1;
    // aurora ribbons
    for (let i = 0; i < 3; i++) for (let x = 0; x < VW; x += 2) {
      const y = 40 + i * 14 + Math.sin(x * 0.02 + this.t * 0.5 + i) * 10;
      g.globalAlpha = 0.07 + 0.04 * Math.sin(this.t + x * 0.03); g.fillStyle = ['#5af0c8', '#a07aff', '#ff7ac8'][i]; g.fillRect(x, y, 2, 16 + Math.sin(x * 0.05 + i) * 6);
    }
    g.globalAlpha = 1;
    // the crystal
    const cx = 306, cy = 92 + Math.sin(this.t * 1.1) * 4;
    for (let r = 46; r > 6; r -= 6) { g.globalAlpha = 0.05 + (46 - r) * 0.0035 + Math.sin(this.t * 2) * 0.015; g.fillStyle = '#9ae8ff'; g.beginPath(); g.ellipse(cx, cy, r, r * 1.15, 0, 0, 7); g.fill(); }
    g.globalAlpha = 1;
    const crystal = (x: number, y: number, w: number, h: number, c1: string, c2: string, c3: string) => {
      for (let j = 0; j < h; j++) { const t = j / h; const ww = Math.round(w * (t < 0.35 ? t / 0.35 : (1 - t) / 0.65)); g.fillStyle = c1; g.fillRect(x - ww, y + j, ww, 1); g.fillStyle = c2; g.fillRect(x, y + j, ww, 1); }
      g.fillStyle = c3; g.fillRect(x - Math.round(w * 0.35), y + Math.round(h * 0.18), 2, Math.round(h * 0.3));
    };
    crystal(cx, cy - 34, 17, 70, '#7ae8ff', '#3a9ad8', '#ffffff');
    crystal(cx - 26, cy - 4 + Math.sin(this.t * 1.4) * 2, 8, 30, '#6ad0ff', '#2a78c0', '#ffffff');
    crystal(cx + 24, cy + 2 + Math.sin(this.t * 1.2 + 1) * 2, 7, 26, '#6ad0ff', '#2a78c0', '#ffffff');
    // crack
    g.fillStyle = '#1a0a30'; let ky = cy - 22, kx = cx - 2; for (let i = 0; i < 24; i++) { g.fillRect(kx, ky, 1, 2); ky += 2; kx += (i % 3 === 0 ? (i % 2 ? 1 : -1) : 0); }
    g.fillStyle = '#ff7ac8'; ky = cy - 22; kx = cx - 2; for (let i = 0; i < 24; i += 2) { g.globalAlpha = 0.5 + 0.5 * Math.sin(this.t * 4 + i); g.fillRect(kx + 1, ky, 1, 1); ky += 4; kx += (i % 3 === 0 ? 1 : 0); }
    g.globalAlpha = 1;
    // shards drifting
    for (let i = 0; i < 6; i++) { const a = this.t * 0.4 + i * 1.05; const x = cx + Math.cos(a) * (46 + i * 3), y = cy + Math.sin(a) * 20; g.fillStyle = '#bff4ff'; g.fillRect(Math.round(x), Math.round(y), 2, 3); }
    // hero on cliff
    const sheet = makeSheet('hero_kai_t', HERO_LOOKS.kai);
    g.drawImage(sheet.frame('idle', 'right', Math.floor(this.t * 1.6) % 2), Math.round(104 - FOOT_X), Math.round(182 - FOOT_Y + 4));
    // scarf streamers (wind)
    for (let i = 0; i < 6; i++) { g.fillStyle = i % 2 ? '#e8453c' : '#ff6a5a'; g.fillRect(96 - i * 3, 163 + Math.round(Math.sin(this.t * 6 + i * 0.7) * 1.5) + i * 0.4, 3, 2); }
    // particles
    for (const p of this.parts) { g.globalAlpha = 0.5 + 0.5 * Math.sin(this.t * 2 + p.ph); g.fillStyle = '#9ae8ff'; g.fillRect(Math.round(p.x), Math.round(p.y), 1, 1); }
    g.globalAlpha = 1;
    // vignette
    const grad = g.createRadialGradient(VW / 2, VH / 2, 70, VW / 2, VH / 2, 240);
    grad.addColorStop(0, 'rgba(0,0,0,0)'); grad.addColorStop(1, 'rgba(0,0,0,.55)');
    g.fillStyle = grad; g.fillRect(0, 0, VW, VH);
  }

  drawUI(u: CanvasRenderingContext2D) {
    // title logo
    const logoY = this.st === 'select' || this.st === 'name' ? 6 : 14;
    if (this.st === 'press' || this.st === 'menu' || this.st === 'options' || this.st === 'credits' || this.st === 'load') {
      text(u, 'CRÔNICAS DE', 192, logoY, { size: 11, align: 'center', color: '#e8d8ff', bold: true });
      u.save();
      u.font = '700 30px "Pixelify Sans", monospace'; u.textAlign = 'center'; u.textBaseline = 'top';
      const grad = u.createLinearGradient(0, logoY + 12, 0, logoY + 44);
      grad.addColorStop(0, '#fff6c8'); grad.addColorStop(0.5, '#ffd86a'); grad.addColorStop(1, '#e8802a');
      u.fillStyle = '#2a0a40'; for (const [dx, dy] of [[-1, 0], [1, 0], [0, 2], [0, -1], [2, 2], [-1, 2], [1, 2]]) u.fillText('AETHERIA', 192 + dx, logoY + 12 + dy);
      u.fillStyle = grad; u.fillText('AETHERIA', 192, logoY + 12);
      u.restore();
      text(u, '— Fragmentos da Aurora —', 192, logoY + 46, { size: 9, align: 'center', color: '#c8b8ff' });
    }
    switch (this.st) {
      case 'press':
        if (Math.floor(this.t * 1.6) % 2 === 0) text(u, 'Pressione ENTER / toque para começar', 232, 168, { size: 9, align: 'center', color: '#fff4c8' });
        text(u, 'v0.1 · Capítulo 1: O Despertar', VW - 6, VH - 11, { size: 7, align: 'right', color: '#8a80a8' });
        break;
      case 'menu': {
        const items = this.menuItems();
        const h = items.length * 15 + 10;
        panel(u, 192 - 52, 100, 104, h, { fill: '#150d26', border: '#e8c872', alpha: 0.9 });
        items.forEach((it, i) => {
          const sel = i === this.cur;
          if (sel) { u.fillStyle = 'rgba(255,224,102,.22)'; u.fillRect(192 - 48, 105 + i * 15, 96, 14); }
          text(u, it, 192, 107 + i * 15, { size: 9, align: 'center', color: sel ? '#fff4c8' : '#b8aed8', bold: sel });
          if (sel) { text(u, '▶', 192 - 44, 107 + i * 15, { size: 8, color: '#ffe066' }); }
        });
        break;
      }
      case 'select': {
        text(u, 'ESCOLHA SEU HERÓI', VW / 2, 8, { size: 12, align: 'center', color: '#fff4c8', bold: true });
        const heroes = [
          { id: 'kai', name: 'Kai', desc: 'Espadachim de cabelos azuis.\nDeterminado e impulsivo.', look: HERO_LOOKS.kai },
          { id: 'aiko', name: 'Aiko', desc: 'Lâmina veloz de rabo-de-cavalo.\nCorajosa e perspicaz.', look: HERO_LOOKS.aiko },
        ];
        heroes.forEach((h, i) => {
          const x = 36 + i * 160, sel = i === this.heroSel;
          panel(u, x, 28, 148, 150, { fill: sel ? '#2a1a4a' : '#150d26', border: sel ? '#ffe066' : '#4a4068' });
          u.globalAlpha = sel ? 1 : 0.55;
          u.drawImage(portrait('sel_' + h.id, h.look, sel ? 'smile' : 'neutral'), x + 46, 36, 56 * 1.0, 64 * 1.0);
          u.globalAlpha = 1;
          text(u, h.name, x + 74, 104, { size: 12, align: 'center', color: sel ? '#fff4c8' : '#8a80a8', bold: true });
          h.desc.split('\n').forEach((l, j) => text(u, l, x + 74, 122 + j * 11, { size: 8, align: 'center', color: '#c8c0e8' }));
          if (sel) text(u, '▲ selecionado', x + 74, 160, { size: 7, align: 'center', color: '#ffe066' });
        });
        text(u, '←/→ escolher   [Confirmar] seguir   [Cancelar] voltar', VW / 2, VH - 16, { size: 7, align: 'center', color: '#8a80a8' });
        break;
      }
      case 'name': {
        panel(u, 84, 70, 216, 76, { fill: '#150d26', border: '#ffe066' });
        text(u, 'Qual é o seu nome?', VW / 2, 80, { size: 10, align: 'center', color: '#fff4c8', bold: true });
        panel(u, 124, 100, 136, 18, { fill: '#0a0614', border: '#6a5a98' });
        const shown = this.nameBuf || (this.heroSel === 0 ? 'Kai' : 'Aiko');
        text(u, shown + (Math.floor(this.t * 2) % 2 === 0 ? '_' : ''), VW / 2, 105, { size: 10, align: 'center', color: this.nameBuf ? '#fff' : '#7a7098' });
        text(u, 'Digite o nome e pressione ENTER', VW / 2, 128, { size: 7, align: 'center', color: '#8a80a8' });
        break;
      }
      case 'load': {
        panel(u, 40, 74, VW - 80, 120, { fill: '#150d26', border: '#e8c872', alpha: 0.95 });
        for (let i = 0; i < 4; i++) {
          const d = i === 3 ? Saves.readAuto() : Saves.read(i);
          const y = 80 + i * 28;
          const sel = i === this.loadSel;
          if (sel) { u.fillStyle = 'rgba(255,224,102,.2)'; u.fillRect(46, y - 2, VW - 92, 26); }
          text(u, i === 3 ? 'Auto' : `Slot ${i + 1}`, 52, y + 1, { size: 7, color: '#9a90b8' });
          if (d) { let area = d.map; try { area = getMap(d.map).name; } catch { /* */ } text(u, `${d.name} Nv${d.level}  ·  ${area}`, 52, y + 11, { size: 8, color: sel ? '#fff4c8' : '#d8d0f0' }); text(u, `${fmtTime(d.playtime)}`, VW - 52, y + 11, { size: 8, align: 'right', color: '#ffd84a' }); }
          else text(u, '— vazio —', 52, y + 11, { size: 8, color: '#6a6088' });
        }
        break;
      }
      case 'options': {
        panel(u, 100, 96, 192, 62, { fill: '#150d26', border: '#e8c872', alpha: 0.95 });
        const rows = [`Música   ◀ ${Math.round(Audio.musicVol * 10)} ▶`, `Efeitos  ◀ ${Math.round(Audio.sfxVol * 10)} ▶`, `Som: ${Audio.muted ? 'DESLIGADO' : 'LIGADO'}`];
        rows.forEach((r, i) => text(u, r, 192, 104 + i * 16, { size: 9, align: 'center', color: i === this.cur ? '#fff4c8' : '#b8aed8', bold: i === this.cur }));
        break;
      }
      case 'credits': {
        panel(u, 50, 80, VW - 100, 100, { fill: '#150d26', border: '#e8c872', alpha: 0.95 });
        ['Crônicas de Aetheria — Fragmentos da Aurora', 'Um RPG de ação em pixel art estilo anime.', 'Arte, música e efeitos gerados proceduralmente por código.', 'Fonte: Pixelify Sans (SIL OFL).', '', 'Obrigado por jogar!'].forEach((l, i) => text(u, l, VW / 2, 90 + i * 13, { size: 8, align: 'center', color: i === 0 ? '#fff4c8' : '#c8c0e8' }));
        break;
      }
    }
    void measure; void NPC_LOOKS;
  }
}

void SaveModal;
