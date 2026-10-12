import { VW, VH, text, panel } from '../../engine/display';
import { Input } from '../../engine/input';
import { Audio } from '../../engine/audio';
import { Modal } from './modal';
import { G, Saves } from '../state';
import { fmtTime } from '../../engine/util';
import { getMap } from '../world/maps';
import type { World } from '../world/world';

export class SaveModal extends Modal<void> {
  sel = 0;
  msg = '';
  msgT = 0;
  hideHud = true;
  constructor(public world: World, public mode: 'save' | 'load') { super(); }
  update(dt: number) {
    this.msgT -= dt;
    if (Input.rep('up')) { this.sel = (this.sel + 2) % 3; Audio.sfx('ui_move'); }
    if (Input.rep('down')) { this.sel = (this.sel + 1) % 3; Audio.sfx('ui_move'); }
    if (Input.pressed('cancel') || Input.pressed('menu')) { Audio.sfx('ui_back'); this.close(); Input.consume('cancel'); return; }
    if (Input.pressed('confirm')) {
      if (this.mode === 'save') {
        G.px = this.world.player.x; G.py = this.world.player.y;
        if (Saves.write(this.sel, G)) { Audio.sfx('save'); this.msg = 'Jogo salvo!'; this.msgT = 1.5; } else { Audio.sfx('error'); this.msg = 'Falha ao salvar.'; this.msgT = 1.5; }
      } else {
        const d = Saves.read(this.sel);
        if (!d) { Audio.sfx('error'); return; }
        Audio.sfx('ui_ok');
        G.load(d);
        this.world.player.setLook(G.look);
        this.close();
        for (const m of this.world.modals) m.close();
        this.world.locked = false;
        this.world.warp(G.map, Math.floor(G.px / 16), Math.floor(G.py / 16));
      }
    }
  }
  drawUI(u: CanvasRenderingContext2D) {
    u.fillStyle = 'rgba(6,3,16,.9)'; u.fillRect(0, 0, VW, VH);
    text(u, this.mode === 'save' ? 'SALVAR JOGO' : 'CARREGAR JOGO', VW / 2, 14, { size: 12, align: 'center', color: '#fff4c8', bold: true });
    for (let i = 0; i < 3; i++) {
      const y = 40 + i * 44, d = Saves.read(i);
      panel(u, 50, y, VW - 100, 38, { fill: '#150d26', border: i === this.sel ? '#ffe066' : '#4a4068' });
      text(u, `Slot ${i + 1}`, 60, y + 5, { size: 8, color: '#9a90b8' });
      if (d) {
        text(u, `${d.name}  Nv ${d.level}`, 60, y + 16, { size: 9, color: '#fff4c8' });
        let area = d.map; try { area = getMap(d.map).name; } catch { /* ignore */ }
        text(u, area, 60, y + 27, { size: 7, color: '#c8c0e8' });
        text(u, `${fmtTime(d.playtime)}   ${d.gold} G`, VW - 60, y + 16, { size: 8, align: 'right', color: '#ffd84a' });
        text(u, new Date(d.saveTime).toLocaleString('pt-BR'), VW - 60, y + 27, { size: 7, align: 'right', color: '#8a80a8' });
      } else text(u, '— vazio —', 60, y + 18, { size: 9, color: '#6a6088' });
    }
    text(u, '[Confirmar] selecionar   [Cancelar] voltar', VW / 2, VH - 18, { size: 7, align: 'center', color: '#8a80a8' });
    if (this.msgT > 0) text(u, this.msg, VW / 2, VH - 32, { size: 9, align: 'center', color: '#6aff9a' });
  }
}

export class GameOverModal extends Modal<number> {
  sel = 0;
  t = 0;
  hideHud = true;
  update(dt: number) {
    this.t += dt;
    if (this.t < 1) return;
    if (Input.rep('up') || Input.rep('down')) { this.sel = 1 - this.sel; Audio.sfx('ui_move'); }
    if (Input.pressed('confirm')) { Audio.sfx('ui_ok'); this.close(this.sel); }
  }
  drawUI(u: CanvasRenderingContext2D) {
    const a = Math.min(1, this.t * 0.8);
    u.fillStyle = `rgba(20,0,8,${0.85 * a})`; u.fillRect(0, 0, VW, VH);
    u.globalAlpha = a;
    text(u, 'VOCÊ CAIU...', VW / 2, 60, { size: 20, align: 'center', color: '#ff6a7a', bold: true });
    text(u, 'A luz da Aurora ainda não se apagou.', VW / 2, 88, { size: 8, align: 'center', color: '#d8c0d0' });
    if (this.t > 1) ['Continuar do último cristal (-10% ouro)', 'Voltar ao título'].forEach((o, i) => {
      const sel = i === this.sel;
      text(u, (sel ? '▶ ' : '  ') + o, VW / 2, 120 + i * 16, { size: 9, align: 'center', color: sel ? '#fff4c8' : '#a890b0' });
    });
    u.globalAlpha = 1;
  }
}
