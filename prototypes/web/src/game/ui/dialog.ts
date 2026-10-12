import { VW, VH, text, panel, wrap } from '../../engine/display';
import { Input } from '../../engine/input';
import { Audio } from '../../engine/audio';
import { Modal } from './modal';
import { portrait, Emotion } from '../../art/portraits';
import { HERO_LOOKS, NPC_LOOKS, Look } from '../../art/characters';
import { G } from '../state';

export function lookFor(key: string): Look | null {
  if (key === 'hero') return HERO_LOOKS[G.look];
  return (HERO_LOOKS as Record<string, Look>)[key] ?? (NPC_LOOKS as Record<string, Look>)[key] ?? null;
}

export class DialogModal extends Modal<void> {
  shown = 0;
  t = 0;
  lines: string[] = [];
  page = 0;
  pages: string[][] = [];
  ready = false;
  private full: string;
  constructor(public who: string, txt: string, public look: string | null, public emo: Emotion = 'neutral', u?: CanvasRenderingContext2D) {
    super();
    this.full = txt;
    const ctx = u ?? document.createElement('canvas').getContext('2d')!;
    const maxW = (look ? VW - 24 - 66 - 12 : VW - 24 - 16) - 6;
    const all = wrap(ctx, txt, maxW, 8);
    for (let i = 0; i < all.length; i += 3) this.pages.push(all.slice(i, i + 3));
    if (!this.pages.length) this.pages.push(['']);
  }
  private get chars() { return this.pages[this.page].join('\n').length; }
  update(dt: number) {
    this.t += dt;
    const before = Math.floor(this.shown);
    if (this.shown < this.chars) {
      this.shown = Math.min(this.chars, this.shown + dt * 55);
      if (Math.floor(this.shown) !== before && Math.floor(this.shown) % 2 === 0 && this.look) Audio.sfx('talk');
    } else this.ready = true;
    if (Input.pressed('confirm') || Input.pressed('interact') || Input.pressed('attack')) {
      Input.consume('attack'); Input.consume('interact');
      if (this.shown < this.chars) this.shown = this.chars;
      else if (this.page < this.pages.length - 1) { this.page++; this.shown = 0; this.ready = false; Audio.sfx('ui_move'); }
      else { Audio.sfx('ui_move'); this.close(); }
    }
  }
  drawUI(u: CanvasRenderingContext2D) {
    const bx = 12, bh = 58, by = VH - bh - 8, bw = VW - 24;
    const hasP = !!this.look;
    if (hasP) {
      const L = lookFor(this.look!);
      if (L) {
        const pic = portrait(this.look!, L, this.emo);
        panel(u, bx + 2, by - 14, 66, 74, { fill: '#1c1236', border: '#e8c872', alpha: 0.98 });
        u.drawImage(pic, bx + 7, by - 9);
      }
    }
    const tx0 = hasP ? bx + 72 : bx;
    panel(u, tx0, by, bw - (tx0 - bx), bh, { fill: '#150d26' });
    if (this.who) {
      const name = this.who;
      const w = Math.max(40, name.length * 5 + 16);
      panel(u, tx0 + 6, by - 8, w, 14, { fill: '#2a1a4a', border: '#ffe066', accent: '#7a5a2a' });
      text(u, name, tx0 + 6 + w / 2, by - 5, { size: 8, align: 'center', color: '#fff4c8', bold: true });
    }
    const lines = this.pages[this.page].join('\n').slice(0, Math.floor(this.shown)).split('\n');
    lines.forEach((l, i) => text(u, l, tx0 + 10, by + 10 + i * 12, { size: 8, color: '#f4efff' }));
    if (this.ready && Math.floor(this.t * 3) % 2 === 0) {
      const lastPage = this.page === this.pages.length - 1;
      text(u, lastPage ? '▼' : '▶', bx + bw - 12, by + bh - 12, { size: 8, color: '#ffe066' });
    }
    void this.full;
  }
}

export class ChoiceModal extends Modal<number> {
  sel = 0;
  constructor(public options: string[], public prompt?: string) { super(); }
  update() {
    if (Input.rep('up')) { this.sel = (this.sel + this.options.length - 1) % this.options.length; Audio.sfx('ui_move'); }
    if (Input.rep('down')) { this.sel = (this.sel + 1) % this.options.length; Audio.sfx('ui_move'); }
    if (Input.pressed('confirm') || Input.pressed('interact')) { Input.consume('attack'); Input.consume('interact'); Audio.sfx('ui_ok'); this.close(this.sel); }
  }
  drawUI(u: CanvasRenderingContext2D) {
    const w = Math.max(...this.options.map((o) => o.length)) * 5 + 30;
    const h = this.options.length * 14 + 10;
    const x = VW - w - 16, y = VH - 66 - h - 14;
    panel(u, x, y, w, h, { fill: '#1c1236', border: '#ffe066' });
    this.options.forEach((o, i) => {
      const sel = i === this.sel;
      if (sel) { u.fillStyle = 'rgba(255,224,102,.18)'; u.fillRect(x + 4, y + 5 + i * 14, w - 8, 13); text(u, '▶', x + 7, y + 7 + i * 14, { size: 8, color: '#ffe066' }); }
      text(u, o, x + 18, y + 7 + i * 14, { size: 8, color: sel ? '#fff4c8' : '#c8c0e8' });
    });
  }
}
