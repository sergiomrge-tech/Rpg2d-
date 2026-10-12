import { VW, VH, text, panel, bar, measure, wrap } from '../../engine/display';
import { Input } from '../../engine/input';
import { Audio } from '../../engine/audio';
import { Modal } from './modal';
import { G, xpToNext } from '../state';
import { ITEMS, ItemDef, ItemStats } from '../data/items';
import { SKILLS, SKILL_MAP, TREE_INFO, Tree, rankPower, rankCost, rankCd } from '../data/skills';
import { QUESTS } from '../data/quests';
import { icon } from '../../art/icons';
import { portrait } from '../../art/portraits';
import { HERO_LOOKS } from '../../art/characters';
import { fmtTime } from '../../engine/util';
import { useItem } from '../world/combat';
import type { World } from '../world/world';
import { SaveModal } from './saveui';

const TABS = ['Itens', 'Equipar', 'Habilidades', 'Missões', 'Status', 'Sistema'];

const STAT_LABEL: [keyof ItemStats, string][] = [['atk', 'ATK'], ['mag', 'MAG'], ['def', 'DEF'], ['hp', 'HP'], ['mp', 'MP'], ['crit', 'CRIT%'], ['spd', 'VEL%']];

export class MenuModal extends Modal<void> {
  tab = 0;
  cur = 0;
  scroll = 0;
  sub: 'list' | 'equipPick' | 'slotPick' = 'list';
  eqSlot = 0;
  eqList: (string | null)[] = [];
  pickSkill = '';
  slotSel = 0;
  sysCur = 0;
  hideHud = true;
  t = 0;
  msg = '';
  msgT = 0;
  constructor(public world: World, public onTitle: () => void) { super(); }

  private flash(m: string) { this.msg = m; this.msgT = 1.6; }

  items(): ItemDef[] {
    return Object.keys(G.inv).map((id) => ITEMS[id]).filter(Boolean).sort((a, b) => ['consumable', 'weapon', 'armor', 'accessory', 'material', 'key'].indexOf(a.type) - ['consumable', 'weapon', 'armor', 'accessory', 'material', 'key'].indexOf(b.type));
  }

  update(dt: number) {
    this.t += dt; this.msgT -= dt;
    const switching = this.sub === 'list';
    if (switching) {
      if (Input.pressed('tabL')) { this.tab = (this.tab + TABS.length - 1) % TABS.length; this.cur = 0; this.scroll = 0; Audio.sfx('ui_move'); }
      if (Input.pressed('tabR')) { this.tab = (this.tab + 1) % TABS.length; this.cur = 0; this.scroll = 0; Audio.sfx('ui_move'); }
      if (Input.pressed('cancel') || Input.pressed('menu')) { Audio.sfx('ui_back'); this.close(); return; }
    }
    switch (this.tab) {
      case 0: this.updItems(); break;
      case 1: this.updEquip(); break;
      case 2: this.updSkills(); break;
      case 3: this.updQuests(); break;
      case 4: break;
      case 5: this.updSystem(); break;
    }
  }

  nav(len: number, cols = 1) {
    if (len === 0) return;
    if (Input.rep('up')) { this.cur = (this.cur - cols + len) % len; Audio.sfx('ui_move'); }
    if (Input.rep('down')) { this.cur = (this.cur + cols) % len; Audio.sfx('ui_move'); }
    if (cols > 1) {
      if (Input.rep('left')) { this.cur = (this.cur + len - 1) % len; Audio.sfx('ui_move'); }
      if (Input.rep('right')) { this.cur = (this.cur + 1) % len; Audio.sfx('ui_move'); }
    }
    const vis = 11;
    if (this.cur < this.scroll) this.scroll = this.cur;
    if (this.cur >= this.scroll + vis) this.scroll = this.cur - vis + 1;
  }

  updItems() {
    const list = this.items();
    this.cur = Math.min(this.cur, Math.max(0, list.length - 1));
    this.nav(list.length);
    if (Input.pressed('confirm') && list[this.cur]) {
      const it = list[this.cur];
      if (it.type === 'consumable') { if (useItem(this.world, it.id)) this.flash(`${it.name} usado.`); else this.flash('Sem efeito agora.'); }
      else if (it.type === 'weapon' || it.type === 'armor' || it.type === 'accessory') {
        const slot = it.type === 'weapon' ? 'weapon' : it.type === 'armor' ? 'armor' : 'acc';
        const prev = G.eq[slot]; G.eq[slot] = it.id; G.addItem(it.id, -1); if (prev) G.addItem(prev, 1);
        Audio.sfx('ui_ok'); this.flash(`${it.name} equipado.`);
      }
    }
  }

  slotKey(i: number): 'weapon' | 'armor' | 'acc' { return (['weapon', 'armor', 'acc'] as const)[i]; }
  updEquip() {
    if (this.sub === 'list') {
      if (Input.rep('up')) { this.eqSlot = (this.eqSlot + 2) % 3; Audio.sfx('ui_move'); }
      if (Input.rep('down')) { this.eqSlot = (this.eqSlot + 1) % 3; Audio.sfx('ui_move'); }
      if (Input.pressed('confirm')) {
        const want = this.slotKey(this.eqSlot) === 'acc' ? 'accessory' : this.slotKey(this.eqSlot);
        this.eqList = [null, ...Object.keys(G.inv).filter((id) => ITEMS[id]?.type === want)];
        this.sub = 'equipPick'; this.cur = 0; this.scroll = 0; Audio.sfx('ui_ok');
      }
    } else if (this.sub === 'equipPick') {
      this.nav(this.eqList.length);
      if (Input.pressed('cancel')) { this.sub = 'list'; Audio.sfx('ui_back'); Input.consume('cancel'); }
      if (Input.pressed('confirm')) {
        const slot = this.slotKey(this.eqSlot);
        const prev = G.eq[slot];
        const nid = this.eqList[this.cur];
        if (prev) G.addItem(prev, 1);
        if (nid) G.addItem(nid, -1);
        G.eq[slot] = nid;
        const st = G.stats(); G.hp = Math.min(G.hp, st.maxHp); G.mp = Math.min(G.mp, st.maxMp);
        Audio.sfx('ui_ok'); this.sub = 'list';
      }
    }
  }

  skillList() {
    const trees: Tree[] = ['blade', 'arcane', 'spirit'];
    return trees.map((t) => SKILLS.filter((s) => s.tree === t));
  }
  skCol = 0;
  updSkills() {
    const cols = this.skillList();
    if (this.sub === 'list') {
      if (Input.rep('left')) { this.skCol = (this.skCol + 2) % 3; this.cur = Math.min(this.cur, cols[this.skCol].length - 1); Audio.sfx('ui_move'); }
      if (Input.rep('right')) { this.skCol = (this.skCol + 1) % 3; this.cur = Math.min(this.cur, cols[this.skCol].length - 1); Audio.sfx('ui_move'); }
      const col = cols[this.skCol];
      if (Input.rep('up')) { this.cur = (this.cur + col.length - 1) % col.length; Audio.sfx('ui_move'); }
      if (Input.rep('down')) { this.cur = (this.cur + 1) % col.length; Audio.sfx('ui_move'); }
      const s = col[this.cur];
      for (let i = 0; i < 4; i++) if (Input.pressed((['skill1', 'skill2', 'skill3', 'skill4'] as const)[i]) && G.skillRank(s.id) > 0) { this.assign(s.id, i); }
      if (Input.pressed('confirm')) {
        const rank = G.skillRank(s.id);
        const can = G.canLearn(s.id);
        if (can.ok) { G.learn(s.id); Audio.sfx('levelup'); this.flash(`${s.name} → nível ${G.skillRank(s.id)}`); }
        else if (rank > 0 && can.why !== undefined && (can.why === 'Nível máximo' || can.why === 'Sem pontos de habilidade')) { this.sub = 'slotPick'; this.pickSkill = s.id; this.slotSel = Math.max(0, G.slots.indexOf(s.id)); Audio.sfx('ui_ok'); }
        else { Audio.sfx('error'); this.flash(can.why ?? ''); }
      }
      if (Input.pressed('attack') && G.skillRank(s.id) > 0) { this.sub = 'slotPick'; this.pickSkill = s.id; this.slotSel = Math.max(0, G.slots.indexOf(s.id)); Audio.sfx('ui_ok'); }
    } else if (this.sub === 'slotPick') {
      if (Input.rep('left')) { this.slotSel = (this.slotSel + 3) % 4; Audio.sfx('ui_move'); }
      if (Input.rep('right')) { this.slotSel = (this.slotSel + 1) % 4; Audio.sfx('ui_move'); }
      if (Input.pressed('cancel')) { this.sub = 'list'; Input.consume('cancel'); Audio.sfx('ui_back'); }
      if (Input.pressed('confirm')) { this.assign(this.pickSkill, this.slotSel); this.sub = 'list'; }
    }
  }
  assign(id: string, slot: number) {
    const old = G.slots.indexOf(id);
    const prev = G.slots[slot];
    if (old >= 0) G.slots[old] = prev;
    G.slots[slot] = id;
    Audio.sfx('ui_ok'); this.flash(`${SKILL_MAP[id].name} → slot ${slot + 1}`);
  }

  questList() {
    return Object.keys(G.quests).filter((id) => QUESTS[id]).sort((a, b) => (G.quests[a].state === G.quests[b].state ? (QUESTS[b].main ? 1 : 0) - (QUESTS[a].main ? 1 : 0) : G.quests[a].state === 'active' ? -1 : 1));
  }
  updQuests() { this.nav(this.questList().length); }

  updSystem() {
    const n = 6;
    if (Input.rep('up')) { this.sysCur = (this.sysCur + n - 1) % n; Audio.sfx('ui_move'); }
    if (Input.rep('down')) { this.sysCur = (this.sysCur + 1) % n; Audio.sfx('ui_move'); }
    const adj = (Input.rep('left') ? -1 : 0) + (Input.rep('right') ? 1 : 0);
    if (this.sysCur === 2 && adj) { Audio.setVolumes(Math.max(0, Math.min(1, Math.round((Audio.musicVol + adj * 0.1) * 10) / 10)), Audio.sfxVol); Audio.sfx('ui_move'); }
    if (this.sysCur === 3 && adj) { Audio.setVolumes(Audio.musicVol, Math.max(0, Math.min(1, Math.round((Audio.sfxVol + adj * 0.1) * 10) / 10))); Audio.sfx('ui_ok'); }
    if (Input.pressed('confirm')) {
      if (this.sysCur === 0) { Input.eat('confirm', 'cancel', 'menu'); void this.world.openModal(new SaveModal(this.world, 'save')); }
      else if (this.sysCur === 1) { Input.eat('confirm', 'cancel', 'menu'); void this.world.openModal(new SaveModal(this.world, 'load')); }
      else if (this.sysCur === 4) { Audio.toggleMute(); }
      else if (this.sysCur === 5) { this.close(); this.onTitle(); }
    }
  }

  drawUI(u: CanvasRenderingContext2D) {
    u.fillStyle = 'rgba(6,3,16,.93)'; u.fillRect(0, 0, VW, VH);
    // bg pattern
    u.fillStyle = 'rgba(120,90,200,.05)';
    for (let i = 0; i < VH; i += 6) u.fillRect(0, i + ((this.t * 8) % 6), VW, 1);
    // tabs
    let x = 10;
    TABS.forEach((t, i) => {
      const w = measure(u, t, 9) + 14;
      panel(u, x, 6, w, 15, { fill: i === this.tab ? '#3a2a6a' : '#150d26', border: i === this.tab ? '#ffe066' : '#4a4068', accent: '#2a2048' });
      text(u, t, x + w / 2, 10, { size: 9, align: 'center', color: i === this.tab ? '#fff4c8' : '#8a80a8', bold: i === this.tab });
      x += w + 3;
    });
    text(u, 'Q / R  trocar aba', VW - 8, 9, { size: 7, align: 'right', color: '#8a80a8' });
    // gold
    text(u, `${G.gold} G`, VW - 8, VH - 12, { size: 8, align: 'right', color: '#ffd84a' });
    text(u, `${G.name}  ·  ${fmtTime(G.playtime)}`, 10, VH - 12, { size: 8, color: '#8a80a8' });
    switch (this.tab) {
      case 0: this.drawItems(u); break;
      case 1: this.drawEquip(u); break;
      case 2: this.drawSkills(u); break;
      case 3: this.drawQuests(u); break;
      case 4: this.drawStatus(u); break;
      case 5: this.drawSystem(u); break;
    }
    if (this.msgT > 0) { const w = measure(u, this.msg, 8) + 16; panel(u, (VW - w) / 2, VH - 30, w, 14, { fill: '#2a1a4a', border: '#ffe066' }); text(u, this.msg, VW / 2, VH - 27, { size: 8, align: 'center', color: '#fff4c8' }); }
  }

  drawList(u: CanvasRenderingContext2D, rows: { name: string; icon?: string; right?: string; dim?: boolean; color?: string }[], x: number, y: number, w: number, active: boolean) {
    const vis = 11;
    panel(u, x, y, w, vis * 14 + 8);
    for (let i = 0; i < vis; i++) {
      const r = rows[this.scroll + i];
      if (!r) break;
      const yy = y + 5 + i * 14;
      const sel = this.scroll + i === this.cur && active;
      if (sel) { u.fillStyle = 'rgba(255,224,102,.2)'; u.fillRect(x + 4, yy - 1, w - 8, 14); u.fillStyle = '#ffe066'; u.fillRect(x + 4, yy - 1, 2, 14); }
      if (r.icon) { u.globalAlpha = r.dim ? 0.5 : 1; u.drawImage(icon(r.icon), x + 8, yy - 2, 14, 14); u.globalAlpha = 1; }
      text(u, r.name, x + 26, yy + 1, { size: 8, color: r.color ?? (r.dim ? '#7a7098' : sel ? '#fff4c8' : '#d8d0f0') });
      if (r.right) text(u, r.right, x + w - 8, yy + 1, { size: 8, align: 'right', color: r.dim ? '#7a7098' : '#c8c0e8' });
    }
    if (rows.length > vis) {
      const th = (vis * 14) * (vis / rows.length), ty = y + 5 + (vis * 14 - th) * (this.scroll / (rows.length - vis));
      u.fillStyle = '#4a4068'; u.fillRect(x + w - 4, y + 5, 2, vis * 14); u.fillStyle = '#e8c872'; u.fillRect(x + w - 4, ty, 2, th);
    }
  }

  statDelta(u: CanvasRenderingContext2D, a: ItemStats | undefined, b: ItemStats | undefined, x: number, y: number) {
    let i = 0;
    for (const [k, lab] of STAT_LABEL) {
      const va = a?.[k] ?? 0, vb = b?.[k] ?? 0;
      if (!va && !vb) continue;
      const d = va - vb;
      text(u, `${lab} ${va}`, x, y + i * 10, { size: 8, color: '#d8d0f0' });
      if (d !== 0) text(u, `${d > 0 ? '▲' : '▼'}${Math.abs(d)}`, x + 62, y + i * 10, { size: 8, color: d > 0 ? '#6aff9a' : '#ff8a8a' });
      i++;
    }
  }

  drawItems(u: CanvasRenderingContext2D) {
    const list = this.items();
    this.drawList(u, list.map((it) => ({ name: it.name, icon: it.icon, right: `x${G.inv[it.id]}`, dim: it.type === 'key' || it.type === 'material' })), 10, 28, 190, true);
    const it = list[this.cur];
    panel(u, 206, 28, VW - 216, 162);
    if (it) {
      u.drawImage(icon(it.icon), 214, 36, 28, 28);
      text(u, it.name, 248, 38, { size: 10, color: '#fff4c8', bold: true });
      const typeName = { consumable: 'Consumível', weapon: 'Arma', armor: 'Armadura', accessory: 'Acessório', key: 'Item-chave', material: 'Material' }[it.type];
      text(u, typeName, 248, 51, { size: 7, color: '#9a90b8' });
      wrap(u, it.desc, VW - 244, 8).forEach((l, i) => text(u, l, 214, 74 + i * 11, { size: 8, color: '#d8d0f0' }));
      if (it.stats) {
        const slot = it.type === 'weapon' ? 'weapon' : it.type === 'armor' ? 'armor' : 'acc';
        const cur = G.eq[slot] ? ITEMS[G.eq[slot]!].stats : undefined;
        text(u, 'Comparado ao equipado:', 214, 112, { size: 7, color: '#9a90b8' });
        this.statDelta(u, it.stats, cur, 214, 123);
      }
      if (it.price) text(u, `Valor: ${Math.floor(it.price / 2)} G`, 214, 176, { size: 7, color: '#9a90b8' });
      if (it.type === 'consumable' || it.type === 'weapon' || it.type === 'armor' || it.type === 'accessory') text(u, '[Confirmar] ' + (it.type === 'consumable' ? 'Usar' : 'Equipar'), VW - 12, 176, { size: 8, align: 'right', color: '#ffe066' });
    } else text(u, 'Mochila vazia.', 214, 40, { size: 8, color: '#9a90b8' });
  }

  drawEquip(u: CanvasRenderingContext2D) {
    const slots = [['Arma', 'weapon'], ['Armadura', 'armor'], ['Acessório', 'acc']] as const;
    panel(u, 10, 28, 190, 70);
    slots.forEach(([lab, key], i) => {
      const id = G.eq[key];
      const y = 34 + i * 20;
      const sel = this.eqSlot === i && this.sub === 'list';
      if (sel) { u.fillStyle = 'rgba(255,224,102,.2)'; u.fillRect(14, y - 2, 182, 19); u.fillStyle = '#ffe066'; u.fillRect(14, y - 2, 2, 19); }
      text(u, lab, 20, y + 3, { size: 8, color: '#9a90b8' });
      if (id) { u.drawImage(icon(ITEMS[id].icon), 70, y - 1, 16, 16); text(u, ITEMS[id].name, 90, y + 3, { size: 8, color: sel ? '#fff4c8' : '#d8d0f0' }); } else text(u, '— vazio —', 70, y + 3, { size: 8, color: '#6a6088' });
    });
    // portrait + stats
    panel(u, 10, 102, 190, 88);
    u.drawImage(portrait('menu_' + G.look, HERO_LOOKS[G.look], 'smile'), 16, 108);
    const s = G.stats();
    const rows: [string, number][] = [['HP', s.maxHp], ['MP', s.maxMp], ['ATK', s.atk], ['MAG', s.mag], ['DEF', s.def], ['CRIT', s.crit]];
    rows.forEach(([l, v], i) => { text(u, l, 82 + (i % 2) * 58, 112 + Math.floor(i / 2) * 16, { size: 8, color: '#9a90b8' }); text(u, String(v) + (l === 'CRIT' ? '%' : ''), 108 + (i % 2) * 58, 112 + Math.floor(i / 2) * 16, { size: 8, color: '#fff4c8' }); });
    panel(u, 206, 28, VW - 216, 162);
    if (this.sub === 'equipPick') {
      const want = slots[this.eqSlot][1];
      const cur = G.eq[want] ? ITEMS[G.eq[want]!].stats : undefined;
      this.drawList(u, this.eqList.map((id) => ({ name: id ? ITEMS[id].name : 'Remover', icon: id ? ITEMS[id].icon : undefined, right: id ? `x${G.inv[id]}` : '' })), 206, 28, VW - 216, true);
      const id = this.eqList[this.cur];
      if (id) this.statDelta(u, ITEMS[id].stats, cur, 214, 28 + 11 * 14 + 14);
    } else {
      text(u, 'Selecione um slot e confirme', 214, 36, { size: 8, color: '#9a90b8' });
      const id = G.eq[slots[this.eqSlot][1]];
      if (id) {
        const it = ITEMS[id];
        u.drawImage(icon(it.icon), 214, 52, 28, 28);
        text(u, it.name, 248, 54, { size: 10, color: '#fff4c8', bold: true });
        wrap(u, it.desc, VW - 244, 8).forEach((l, i) => text(u, l, 214, 90 + i * 11, { size: 8, color: '#d8d0f0' }));
        this.statDelta(u, it.stats, undefined, 214, 120);
      }
    }
  }

  drawSkills(u: CanvasRenderingContext2D) {
    const cols = this.skillList();
    const trees: Tree[] = ['blade', 'arcane', 'spirit'];
    text(u, `Pontos de habilidade: ${G.sp}`, 10, 24, { size: 8, color: G.sp > 0 ? '#ffe066' : '#8a80a8' });
    const cw = 118;
    trees.forEach((tr, ci) => {
      const x = 10 + ci * (cw + 4);
      const info = TREE_INFO[tr];
      panel(u, x, 34, cw, 104, { fill: '#150d26', border: ci === this.skCol ? '#ffe066' : '#4a4068' });
      text(u, info.name.toUpperCase(), x + cw / 2, 37, { size: 8, align: 'center', color: info.color, bold: true });
      cols[ci].forEach((s, i) => {
        const y = 49 + i * 17;
        const sel = ci === this.skCol && i === this.cur && this.sub === 'list';
        const rank = G.skillRank(s.id);
        const locked = G.level < s.reqLevel && rank === 0;
        if (sel) { u.fillStyle = 'rgba(255,224,102,.2)'; u.fillRect(x + 3, y - 2, cw - 6, 17); }
        u.globalAlpha = locked ? 0.35 : 1; u.drawImage(icon(s.icon), x + 4, y - 2, 15, 15); u.globalAlpha = 1;
        text(u, s.name, x + 22, y - 1, { size: 7, color: locked ? '#6a6088' : sel ? '#fff4c8' : '#d8d0f0' });
        for (let r = 0; r < s.maxRank; r++) { u.fillStyle = '#05020c'; u.fillRect(x + 22 + r * 6, y + 8, 5, 4); u.fillStyle = r < rank ? info.color : '#2a2048'; u.fillRect(x + 23 + r * 6, y + 9, 3, 2); }
        const slotIdx = G.slots.indexOf(s.id);
        if (slotIdx >= 0) text(u, `[${slotIdx + 1}]`, x + cw - 6, y - 1, { size: 7, align: 'right', color: '#ffe066' });
        else if (locked) text(u, `Nv${s.reqLevel}`, x + cw - 6, y - 1, { size: 7, align: 'right', color: '#6a6088' });
      });
    });
    const s = cols[this.skCol][this.cur];
    const rank = G.skillRank(s.id);
    panel(u, 10, 142, VW - 20, 48);
    text(u, s.name, 18, 146, { size: 9, color: '#fff4c8', bold: true });
    text(u, `Nv ${rank}/${s.maxRank}  ·  MP ${rankCost(s, Math.max(1, rank))}  ·  Recarga ${rankCd(s, Math.max(1, rank)).toFixed(1)}s  ·  Poder ${Math.round(rankPower(s, Math.max(1, rank)) * 100)}%`, 18, 158, { size: 7, color: '#c8c0e8' });
    wrap(u, s.desc, VW - 160, 8).forEach((l, i) => text(u, l, 18, 169 + i * 10, { size: 8, color: '#d8d0f0' }));
    text(u, G.canLearn(s.id).ok ? '[Confirmar] Aprender (1 pt)' : rank > 0 ? '[Confirmar/J] Equipar' : (G.canLearn(s.id).why ?? ''), VW - 14, 168, { size: 7, align: 'right', color: '#ffe066' });
    text(u, '1-4: atalho direto', VW - 14, 178, { size: 7, align: 'right', color: '#8a80a8' });
    if (this.sub === 'slotPick') {
      u.fillStyle = 'rgba(0,0,0,.6)'; u.fillRect(0, 0, VW, VH);
      panel(u, VW / 2 - 100, 70, 200, 70, { fill: '#1c1236', border: '#ffe066' });
      text(u, `Equipar ${SKILL_MAP[this.pickSkill].name} em:`, VW / 2, 76, { size: 8, align: 'center', color: '#fff4c8' });
      for (let i = 0; i < 4; i++) {
        const x = VW / 2 - 88 + i * 46, id = G.slots[i];
        panel(u, x, 92, 40, 38, { fill: '#150d26', border: i === this.slotSel ? '#ffe066' : '#4a4068' });
        if (id) u.drawImage(icon(SKILL_MAP[id].icon), x + 11, 96, 18, 18);
        text(u, String(i + 1), x + 20, 117, { size: 8, align: 'center', color: '#ffe8a0' });
      }
    }
  }

  drawQuests(u: CanvasRenderingContext2D) {
    const ids = this.questList();
    this.cur = Math.min(this.cur, Math.max(0, ids.length - 1));
    this.drawList(u, ids.map((id) => ({ name: QUESTS[id].name, icon: QUESTS[id].main ? 'star' : 'scroll', right: G.quests[id].state === 'done' ? '✔' : '', dim: G.quests[id].state === 'done', color: QUESTS[id].main ? '#ffe066' : undefined })), 10, 28, 190, true);
    panel(u, 206, 28, VW - 216, 162);
    const id = ids[this.cur];
    if (!id) { text(u, 'Nenhuma missão ainda.', 214, 40, { size: 8, color: '#9a90b8' }); return; }
    const q = QUESTS[id], st = G.quests[id];
    text(u, q.name, 214, 36, { size: 10, color: '#fff4c8', bold: true });
    text(u, q.main ? 'Missão Principal' : 'Missão Secundária', 214, 49, { size: 7, color: q.main ? '#ffe066' : '#9ad8ff' });
    wrap(u, q.desc, VW - 236, 8).forEach((l, i) => text(u, l, 214, 64 + i * 11, { size: 8, color: '#d8d0f0' }));
    q.steps.forEach((s, i) => {
      const done = st.state === 'done' || i < st.step;
      const cur = i === st.step && st.state === 'active';
      if (i > st.step && st.state === 'active') return;
      const y = 112 + i * 14;
      text(u, done ? '✔' : '◆', 214, y, { size: 8, color: done ? '#6aff9a' : '#ffe066' });
      text(u, s, 226, y, { size: 8, color: done ? '#7a9a88' : cur ? '#fff4c8' : '#d8d0f0' });
    });
    if (q.reward) text(u, `Recompensa: ${q.reward.xp ?? 0} XP · ${q.reward.gold ?? 0} G${q.reward.items ? ' · ' + q.reward.items.map(([i, n]) => `${ITEMS[i].name} x${n}`).join(', ') : ''}`, 214, 178, { size: 7, color: '#9a90b8' });
  }

  drawStatus(u: CanvasRenderingContext2D) {
    const s = G.stats();
    panel(u, 10, 28, 150, 162);
    u.drawImage(portrait('status_' + G.look, HERO_LOOKS[G.look], 'smile'), 57, 34);
    text(u, G.name, 85, 100, { size: 11, align: 'center', color: '#fff4c8', bold: true });
    text(u, `Nível ${G.level}`, 85, 114, { size: 8, align: 'center', color: '#ffe066' });
    bar(u, 24, 128, 122, 5, G.xp / xpToNext(G.level), '#e8c050', '#ffe888');
    text(u, `${G.xp} / ${xpToNext(G.level)} XP`, 85, 136, { size: 7, align: 'center', color: '#c8c0e8' });
    text(u, `Tempo de jogo  ${fmtTime(G.playtime)}`, 85, 154, { size: 7, align: 'center', color: '#9a90b8' });
    text(u, `Inimigos derrotados  ${G.kills}`, 85, 166, { size: 7, align: 'center', color: '#9a90b8' });
    panel(u, 166, 28, VW - 176, 162);
    const rows: [string, string, string][] = [
      ['HP máximo', String(s.maxHp), '#ff8a9a'], ['MP máximo', String(s.maxMp), '#8ab8ff'], ['Ataque (ATK)', String(s.atk), '#ffb08a'], ['Magia (MAG)', String(s.mag), '#b8a0ff'],
      ['Defesa (DEF)', String(s.def), '#9ad8ff'], ['Crítico', `${s.crit}%`, '#ffe066'], ['Velocidade', `${Math.round(s.spd * 100)}%`, '#9affc0'],
    ];
    rows.forEach(([l, v, c], i) => { text(u, l, 176, 38 + i * 15, { size: 8, color: '#9a90b8' }); text(u, v, VW - 20, 38 + i * 15, { size: 9, align: 'right', color: c, bold: true }); u.fillStyle = '#2a2048'; u.fillRect(176, 48 + i * 15, VW - 196, 1); });
    text(u, 'Elementos: Fogo > Gelo > Raio > Fogo?  Cada inimigo tem fraquezas diferentes.', 176, 148, { size: 7, color: '#8a80a8' });
    text(u, 'Dica: use esquiva (K/X) para atravessar ataques!', 176, 160, { size: 7, color: '#8a80a8' });
    const allies = ['lyra', 'torren', 'sylphie', 'rhea'].filter((n) => G.has('ally_' + n));
    text(u, allies.length ? 'Aliados: ' + allies.map((a) => a[0].toUpperCase() + a.slice(1)).join(', ') : 'Aliados: —', 176, 174, { size: 8, color: '#c8c0e8' });
  }

  drawSystem(u: CanvasRenderingContext2D) {
    panel(u, 90, 36, VW - 180, 130);
    const rows = ['Salvar jogo', 'Carregar jogo', `Volume da música  ◀ ${Math.round(Audio.musicVol * 10)} ▶`, `Volume dos efeitos  ◀ ${Math.round(Audio.sfxVol * 10)} ▶`, `Som: ${Audio.muted ? 'DESLIGADO' : 'LIGADO'}`, 'Voltar ao título'];
    rows.forEach((r, i) => {
      const y = 46 + i * 18;
      const sel = i === this.sysCur;
      if (sel) { u.fillStyle = 'rgba(255,224,102,.2)'; u.fillRect(96, y - 3, VW - 192, 16); u.fillStyle = '#ffe066'; u.fillRect(96, y - 3, 2, 16); }
      text(u, r, VW / 2, y, { size: 9, align: 'center', color: sel ? '#fff4c8' : '#c8c0e8' });
    });
    text(u, 'Controles: Setas/WASD mover · J/Z atacar · K/X esquivar · 1-4 habilidades · E interagir · Q/R poção/éter', VW / 2, 176, { size: 7, align: 'center', color: '#8a80a8' });
  }
}
