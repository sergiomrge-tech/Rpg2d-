import { VW, VH, text, panel, wrap } from '../../engine/display';
import { Input } from '../../engine/input';
import { Audio } from '../../engine/audio';
import { Modal } from './modal';
import { G } from '../state';
import { ITEMS, ItemStats } from '../data/items';
import { icon } from '../../art/icons';

export class ShopModal extends Modal<void> {
  mode: 'buy' | 'sell' = 'buy';
  cur = 0;
  scroll = 0;
  msg = '';
  msgT = 0;
  hideHud = true;
  constructor(public stock: string[], public title = 'Loja') { super(); }
  list(): string[] {
    if (this.mode === 'buy') return this.stock;
    return Object.keys(G.inv).filter((id) => ITEMS[id] && ITEMS[id].price > 0 && ITEMS[id].type !== 'key');
  }
  update(dt: number) {
    this.msgT -= dt;
    const l = this.list();
    if (Input.pressed('tabL') || Input.pressed('tabR') || Input.pressed('left') || Input.pressed('right')) { this.mode = this.mode === 'buy' ? 'sell' : 'buy'; this.cur = 0; this.scroll = 0; Audio.sfx('ui_move'); }
    if (Input.rep('up') && l.length) { this.cur = (this.cur + l.length - 1) % l.length; Audio.sfx('ui_move'); }
    if (Input.rep('down') && l.length) { this.cur = (this.cur + 1) % l.length; Audio.sfx('ui_move'); }
    if (this.cur < this.scroll) this.scroll = this.cur;
    if (this.cur >= this.scroll + 9) this.scroll = this.cur - 8;
    if (Input.pressed('cancel') || Input.pressed('menu')) { Audio.sfx('ui_back'); this.close(); Input.consume('cancel'); return; }
    if (Input.pressed('confirm') && l[this.cur]) {
      const it = ITEMS[l[this.cur]];
      if (this.mode === 'buy') {
        if (G.gold >= it.price) {
          if ((it.type === 'weapon' || it.type === 'armor' || it.type === 'accessory') && (G.count(it.id) > 0 || Object.values(G.eq).includes(it.id))) { Audio.sfx('error'); this.flash('Você já possui este item.'); return; }
          G.gold -= it.price; G.addItem(it.id, 1); Audio.sfx('coin'); this.flash(`Comprou ${it.name}!`);
        } else { Audio.sfx('error'); this.flash('Ouro insuficiente.'); }
      } else {
        const v = Math.floor(it.price / 2);
        G.gold += v; G.addItem(it.id, -1); Audio.sfx('coin'); this.flash(`Vendeu ${it.name} por ${v} G.`);
        if (this.cur >= this.list().length) this.cur = Math.max(0, this.list().length - 1);
      }
    }
  }
  flash(m: string) { this.msg = m; this.msgT = 1.5; }
  drawUI(u: CanvasRenderingContext2D) {
    u.fillStyle = 'rgba(6,3,16,.92)'; u.fillRect(0, 0, VW, VH);
    text(u, this.title, 12, 8, { size: 12, color: '#fff4c8', bold: true });
    ['buy', 'sell'].forEach((m, i) => {
      const x = 130 + i * 56;
      panel(u, x, 6, 52, 15, { fill: this.mode === m ? '#3a2a6a' : '#150d26', border: this.mode === m ? '#ffe066' : '#4a4068' });
      text(u, m === 'buy' ? 'Comprar' : 'Vender', x + 26, 10, { size: 8, align: 'center', color: this.mode === m ? '#fff4c8' : '#8a80a8' });
    });
    text(u, `${G.gold} G`, VW - 12, 9, { size: 10, align: 'right', color: '#ffd84a', bold: true });
    const l = this.list();
    panel(u, 10, 28, 200, 9 * 15 + 10);
    for (let i = 0; i < 9; i++) {
      const id = l[this.scroll + i];
      if (!id) break;
      const it = ITEMS[id];
      const y = 34 + i * 15;
      const sel = this.scroll + i === this.cur;
      if (sel) { u.fillStyle = 'rgba(255,224,102,.2)'; u.fillRect(14, y - 2, 192, 15); u.fillStyle = '#ffe066'; u.fillRect(14, y - 2, 2, 15); }
      const afford = this.mode === 'sell' || G.gold >= it.price;
      u.drawImage(icon(it.icon), 20, y - 2, 14, 14);
      text(u, it.name, 38, y + 1, { size: 8, color: afford ? (sel ? '#fff4c8' : '#d8d0f0') : '#7a7098' });
      text(u, this.mode === 'buy' ? `${it.price} G` : `${Math.floor(it.price / 2)} G  x${G.inv[id]}`, 202, y + 1, { size: 8, align: 'right', color: afford ? '#ffd84a' : '#7a6030' });
    }
    if (!l.length) text(u, this.mode === 'sell' ? 'Nada para vender.' : 'Sem estoque.', 24, 40, { size: 8, color: '#8a80a8' });
    panel(u, 216, 28, VW - 226, 145);
    const id = l[this.cur];
    if (id) {
      const it = ITEMS[id];
      u.drawImage(icon(it.icon), 224, 36, 28, 28);
      text(u, it.name, 258, 38, { size: 10, color: '#fff4c8', bold: true });
      text(u, `Em posse: ${G.count(id)}`, 258, 51, { size: 7, color: '#9a90b8' });
      wrap(u, it.desc, VW - 246, 8).forEach((s, i) => text(u, s, 224, 74 + i * 11, { size: 8, color: '#d8d0f0' }));
      if (it.stats) {
        const slot = it.type === 'weapon' ? 'weapon' : it.type === 'armor' ? 'armor' : 'acc';
        const cur: ItemStats | undefined = G.eq[slot] ? ITEMS[G.eq[slot]!].stats : undefined;
        const labels: [keyof ItemStats, string][] = [['atk', 'ATK'], ['mag', 'MAG'], ['def', 'DEF'], ['hp', 'HP'], ['mp', 'MP'], ['crit', 'CRIT%'], ['spd', 'VEL%']];
        let i = 0;
        for (const [k, lab] of labels) {
          const a = it.stats[k] ?? 0, b = cur?.[k] ?? 0;
          if (!a && !b) continue;
          text(u, `${lab} ${a}`, 224, 108 + i * 10, { size: 8, color: '#d8d0f0' });
          if (a !== b) text(u, `${a > b ? '▲' : '▼'}${Math.abs(a - b)}`, 286, 108 + i * 10, { size: 8, color: a > b ? '#6aff9a' : '#ff8a8a' });
          i++;
        }
      }
    }
    if (this.msgT > 0) text(u, this.msg, VW / 2, VH - 28, { size: 9, align: 'center', color: '#fff4c8' });
    text(u, '←/→ Comprar/Vender   [Confirmar] Selecionar   [Cancelar] Sair', VW / 2, VH - 14, { size: 7, align: 'center', color: '#8a80a8' });
  }
}
