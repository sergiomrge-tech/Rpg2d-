import { MB } from '../world/map';
import { registerMap } from '../world/maps';
import { T } from '../../art/tiles';
import { G } from '../state';
import type { ScriptCtx } from '../script';

const sayAll = async (c: ScriptCtx, who: string, look: string, lines: string[]) => { for (const l of lines) await c.say(who, l, look); };

export function buildVillage() {
  const m = new MB('vila_alvorada', 'Vila Alvorada', 50, 38, T.GRASS, 101);
  const rng = m.rng;
  m.patches(T.GRASS2, 16, 3, 6, [T.GRASS]);
  m.patches(T.FLOWER, 26, 1.2, 3, [T.GRASS, T.GRASS2]);
  // darker rim for depth
  for (let y = 0; y < m.h; y++) for (let x = 0; x < m.w; x++) if (x < 3 || y < 3 || x > m.w - 4 || y > m.h - 4) if (rng.chance(0.85)) m.set(T.DGRASS, x, y);
  // pond (south-west) with sand rim and pier
  m.blob(T.SAND, 8, 31, 7.5, 5.5, 0.3);
  m.blob(T.WATER, 8, 31, 5.5, 3.8, 0.3);
  m.blob(T.DEEP, 8, 31, 2.8, 1.8, 0.3);
  m.fill(T.WOOD, 12, 31, 4, 1);
  // plaza + roads
  m.fill(T.COBBLE, 19, 14, 13, 7);
  m.fill(T.DIRT, 24, 21, 3, 17);          // south road
  m.fill(T.DIRT, 24, 4, 3, 10);           // north road
  m.fill(T.DIRT, 32, 16, 18, 2);          // east road
  m.fill(T.DIRT, 3, 16, 16, 2);           // west road
  m.fill(T.DIRT, 10, 14, 1, 2);           // hero door path
  m.fill(T.DIRT, 39, 12, 1, 4);           // Mira door path
  m.fill(T.DIRT, 19, 10, 1, 4);           // house A path
  m.fill(T.DIRT, 31, 10, 1, 4);           // house B path
  m.fill(T.DIRT, 27, 27, 14, 2);          // inn road
  m.fill(T.DIRT, 39, 26, 1, 1);
  m.fill(T.DIRT, 12, 22, 12, 2);          // market lane west
  // cobble borders on the plaza edge for richness
  m.outline(T.STONE, 19, 14, 13, 7);
  m.fill(T.COBBLE, 20, 15, 11, 5);
  m.scatterTiles(T.STONE, 18, [T.COBBLE]);
  m.scatterTiles(T.DCOBBLE, 10, [T.DIRT]);
  m.scatterTiles(T.STONE, 40, [T.DIRT]);

  // ------------------------------------------------ buildings
  m.house(8, 13, 5, 0, { to: 'casa_heroi', ntx: 5, nty: 7 });
  m.house(36, 11, 6, 1, { to: 'casa_mira', ntx: 6, nty: 7 });
  m.house(36, 25, 6, 3, { to: 'estalagem', ntx: 6, nty: 7 });
  m.house(17, 9, 4, 2, undefined, ['A porta está trancada. Parece que a família viajou para a feira de Porto Luz.']);
  m.house(29, 9, 4, 1, undefined, ['"Ateliê de Tecidos Marta & Filhos — Volto logo."']);
  m.signs.push({ tx: 38, ty: 26, text: ['Estalagem do Cervo Dourado', 'Quartos confortáveis • Ensopados • Notícias frescas'] });
  m.obj('sign', 38, 26, 0);
  m.signs.push({ tx: 12, ty: 14, text: ['Casa do Herói — "Aqui mora quem ainda não sabe que é especial."'] });
  m.obj('sign', 12, 14, 0);
  m.signs.push({ tx: 23, ty: 13, text: ['VILA ALVORADA', 'Onde a luz da Aurora toca o mundo primeiro.'] });
  m.obj('sign', 23, 13, 0);

  // plaza centrepiece
  m.obj('fountain', 24, 18, 0);
  for (const [x, y] of [[19, 14], [31, 14], [19, 20], [31, 20]]) m.obj('lamp', x, y, 0);
  m.obj('flowerbed', 20, 15, 0); m.obj('flowerbed', 28, 15, 1);
  m.obj('statue', 22, 16, 0); m.obj('statue', 28, 19, 0);
  m.obj('save_crystal', 22, 19, 0);
  m.obj('banner_blue', 20, 13, 0); m.obj('banner_red', 30, 13, 0);

  // gate to the northern pass (closed)
  m.obj('gate', 23, 6, 0);
  m.block(24, 4, 2, 3);
  m.signs.push({ tx: 22, ty: 6, text: ['PASSAGEM DAS MONTANHAS CINZENTAS', 'Fechada devido a deslizamentos. Aguarde ordens do Conselho.'] });
  m.obj('sign', 22, 6, 0);
  m.obj('banner_red', 22, 5, 0); m.obj('banner_red', 27, 5, 0);

  // market (west lane): stalls, crates, jars
  m.obj('stall_blue', 14, 21, 0);
  m.obj('stall_red', 18, 21, 0);
  m.obj('barrel', 12, 21, 0); m.obj('crate', 12, 20, 0); m.obj('jar', 13, 20, 1); m.obj('jar', 21, 21, 2); m.obj('crate', 21, 22, 0);
  m.obj('cart', 28, 23, 0);
  m.obj('plant', 33, 23, 0); m.obj('jar', 34, 24, 3); m.obj('barrel', 35, 24, 0);
  m.obj('woodpile', 6, 12, 0); m.obj('barrel', 14, 14, 0);
  m.obj('well', 14, 11, 0);
  // house yards
  for (const [x, y, v] of [[7, 14, 0], [13, 14, 1], [35, 12, 1], [35, 26, 2], [42, 26, 0], [42, 12, 2]] as number[][]) m.obj('plant', x, y, v);
  m.obj('mailbox', 6, 14, 0); m.obj('mailbox', 34, 13, 0);
  m.obj('flowerbed', 8, 15, 2); m.obj('flowerbed', 37, 13, 3); m.obj('flowerbed', 37, 27, 1);
  // fence line around hero's garden & farm
  for (let x = 5; x <= 14; x++) if (x < 9 || x > 11) m.obj('fence', x, 8, 0);
  for (let y = 9; y <= 13; y++) { if (y !== 12) m.obj('fence', 5, y, 0); }
  // farm (south-east)
  m.fill(T.DIRT, 31, 31, 15, 5);
  for (let x = 30; x <= 46; x++) { m.obj('fence', x, 30, 0); if (x < 37 || x > 38) m.obj('fence', x, 36, 0); }
  for (let y = 31; y <= 35; y++) { m.obj('fence', 30, y, 0); m.obj('fence', 46, y, 0); }
  m.unblock(37, 36, 2, 1);
  m.set(T.DIRT, 37, 36); m.set(T.DIRT, 38, 36); m.set(T.DIRT, 37, 37); m.set(T.DIRT, 38, 37);
  m.obj('flowerbed', 32, 32, 1); m.obj('flowerbed', 35, 32, 0); m.obj('flowerbed', 38, 32, 2); m.obj('flowerbed', 41, 32, 3);
  m.obj('flowerbed', 32, 34, 3); m.obj('flowerbed', 41, 34, 1);
  m.obj('haystack', 44, 33, 0); m.obj('haystack', 33, 35, 0); m.obj('cart', 42, 35, 0);
  // trees, bushes, rocks
  m.treeBorder(2, [{ x0: 24, y0: 34, x1: 26, y1: 37 }, { x0: 47, y0: 15, x1: 49, y1: 18 }, { x0: 24, y0: 0, x1: 26, y1: 4 }]);
  const gr = [T.GRASS, T.GRASS2, T.DGRASS, T.FLOWER];
  m.scatter(['tree', 'tree', 'fruit_tree', 'autumn_tree'], 30, 3, 3, 47, 34, { grounds: gr, gap: 2, avoid: [{ x: 25, y: 18, r: 12 }, { x: 39, y: 18, r: 6 }] });
  m.scatter(['bush'], 34, 3, 3, 47, 34, { grounds: gr, gap: 1, vmax: 1 });
  m.scatter(['rock'], 10, 3, 3, 47, 34, { grounds: gr, gap: 1, vmax: 1 });
  m.scatter(['plant', 'jar'], 8, 3, 3, 47, 34, { grounds: gr, gap: 1, vmax: 3 });
  m.scatter(['dry_bush'], 4, 3, 3, 12, 8, { grounds: gr });

  // ------------------------------------------------ exits
  m.warps.push({ tx: 24, ty: 36, w: 3, h: 2, to: 'floresta', ntx: 35, nty: 3, dir: 'down', need: () => (G.has('mira_briefed') ? null : 'Você deveria falar com a Anciã Mira antes de partir.') });
  m.warps.push({ tx: 48, ty: 16, w: 2, h: 2, to: 'vila_alvorada', ntx: 46, nty: 16, dir: 'left', need: () => (G.has('ch1_done') ? 'A Estrada Dourada se estende além do horizonte... mas esta jornada continua no próximo capítulo. Aguarde!' : 'Guardas bloqueiam a estrada leste. "Ordens do Conselho: ninguém sai da vila durante a crise."') });

  // ------------------------------------------------ NPCs
  m.npcs.push({
    id: 'selene', name: 'Mestra Selene', look: 'mystic', tx: 28, ty: 21, dir: 'up',
    marker: () => (G.questActive('m1_call') && G.quests['m1_call'].step === 0 ? '!' : null),
    talk: async (c) => {
      const q = G.quests['m1_call'];
      if (q && q.step === 0 && !G.has('tutorial_done')) {
        await c.say('Mestra Selene', `Ah, ${G.name}. Você veio. Senti o Pingente da Aurora despertar esta noite.`, 'mystic', 'smile');
        await c.say('Mestra Selene', 'O Cristal rachou e as Sombras já rondam a vila. Antes de qualquer jornada, você precisa dominar o básico.', 'mystic');
        await c.say('Mestra Selene', 'Mova-se com as SETAS ou WASD. Ataque com J (ou Z): três golpes em sequência formam um combo. Esquive com K (ou X) — há invulnerabilidade na rolagem!', 'mystic');
        await c.say('Mestra Selene', 'Habilidades usam MP: teclas 1 a 4. Abra o menu (ESC) para gastar pontos de habilidade e equipar novas técnicas. Q usa poção, R usa éter.', 'mystic');
        c.gs.sp += 1; c.toast('+1 ponto de habilidade!', 'star');
        await c.say('Mestra Selene', 'Pronto! Eis um ponto extra. Agora... prepare-se. Elas estão chegando!', 'mystic', 'surprised');
        c.flag('tutorial_done', true);
        c.questStep('m1_call', 1);
        c.shake(5); c.sfx('roar');
        await c.wait(0.4);
        c.spawn('slime', 23, 22); c.spawn('slime', 27, 23); c.spawn('slime', 21, 18); c.spawn('bat', 26, 24);
        c.music('battle');
        await c.say('', 'Sombras brotam da terra! Derrote-as!');
        return;
      }
      if (G.has('tutorial_done') && !G.has('battle1_done')) { await c.say('Mestra Selene', 'Concentre-se! Desvie dos golpes e ataque quando abrirem a guarda!', 'mystic'); return; }
      if (!G.has('ch1_done')) {
        await c.say('Mestra Selene', 'Cada habilidade pode ser aprimorada até o nível 5. Três escolas existem: Lâmina, Arcano e Espírito — combine-as!', 'mystic', 'smile');
        const k = await c.choice(['Revisar controles', 'Sair']);
        if (k === 0) await c.say('Mestra Selene', 'J/Z ataque · K/X esquiva · 1-4 habilidades · E interagir · Q poção · R éter · ESC menu.', 'mystic');
      } else {
        await c.say('Mestra Selene', 'As Sombras recuaram... mas sinto uma presença antiga despertando além das montanhas.', 'mystic', 'sad');
      }
    },
  });

  m.npcs.push({
    id: 'mira_plaza', name: 'Anciã Mira', look: 'mira', tx: 25, ty: 22, dir: 'up',
    show: () => G.has('battle1_done') && !G.has('mira_briefed'),
    marker: () => '!',
    talk: async (c) => {
      await c.say('Anciã Mira', 'Você sobreviveu... Bom. Eu temia por esta noite desde que o encontrei, bebê, na escadaria do templo.', 'mira', 'sad');
      await c.say('Anciã Mira', 'O Cristal da Aurora sustenta o amanhecer do mundo. Há mil anos, os Sete Guardiões o forjaram para selar Nyxar, o Deus da Noite Eterna.', 'mira');
      await c.say('Anciã Mira', 'Agora o Cristal racha. Seu pingente é um Fragmento da Aurora — a única coisa capaz de ressoar com os Cristais Menores escondidos pelo mundo.', 'mira');
      await c.say('Anciã Mira', 'O mais próximo repousa na Caverna de Cristal, ao sul, atravessando a Floresta Sussurrante. Lobos e criaturas sombrias a dominam.', 'mira');
      await c.hero('Eu vou. Se o Cristal precisa de mim, não vou ficar parado.', 'angry');
      await c.say('Anciã Mira', 'Eu sabia que diria isso. Leve isto — ouro e poções. Compre equipamentos com Gorim e Bento antes de partir.', 'mira', 'smile');
      c.gold(120);
      await c.give('potion', 3, true); await c.give('ether', 2, true);
      c.toast('Poção x3, Éter x2', 'potion_r');
      await c.say('Anciã Mira', 'Quando estiver pronto, siga a estrada ao sul. E, filho... volte vivo.', 'mira', 'smile');
      c.flag('mira_briefed', true);
      c.questStep('m1_call', 3);
    },
  });

  m.npcs.push({
    id: 'bento', name: 'Bento', look: 'merchant', tx: 15, ty: 23, dir: 'up',
    talk: async (c) => {
      await c.say('Bento', 'Bem-vindo à Barraca do Bento! Poções fresquinhas, éteres borbulhantes... tudo para quem não quer morrer hoje!', 'merchant', 'smile');
      const stock = ['herb', 'potion', 'ether'];
      if (G.has('dead_boss_fenrisa')) stock.push('hi_potion', 'hi_ether');
      await c.shop(stock, 'Barraca do Bento');
      await c.say('Bento', 'Volte sempre! Aliás... traga Géis de Slime. Sempre dá para revender.', 'merchant');
    },
  });
  m.npcs.push({
    id: 'gorim', name: 'Gorim', look: 'smith', tx: 19, ty: 23, dir: 'up',
    talk: async (c) => {
      await c.say('Gorim', 'Hmpf. Aço bom não nasce em árvore. O que vai ser?', 'smith');
      const stock = ['iron_sword', 'apprentice_staff', 'leather_armor', 'mage_robe', 'lucky_charm'];
      if (G.has('dead_boss_fenrisa')) stock.push('hunter_blade', 'chain_mail', 'vigor_ring', 'mana_pendant', 'swift_boots');
      await c.shop(stock, 'Forja do Gorim');
    },
  });
  m.npcs.push({
    id: 'pipo', name: 'Pipo', look: 'child', tx: 27, ty: 25, wander: true,
    marker: () => (!G.quests['s_slimes'] ? '!' : null),
    talk: async (c) => {
      const q = G.quests['s_slimes'];
      if (!q) {
        await c.say('Pipo', 'Moço! Moço! Os slimes da floresta roubaram meu soldadinho de madeira!', 'child', 'sad');
        await c.say('Pipo', 'Se você derrotar uns 5 slimes lá, aposto que ele aparece. Por favor?', 'child');
        c.startQuest('s_slimes');
      } else if (q.state === 'active' && q.step === 0) {
        await c.say('Pipo', `Já derrotou os slimes? Faltam ${Math.max(0, 5 - q.progress)}.`, 'child');
      } else if (q.state === 'active' && q.step === 1) {
        await c.say('Pipo', 'Meu soldadinho! Estava dentro de um slime gigante! Obrigado, obrigado!', 'child', 'smile');
        c.completeQuest('s_slimes');
      } else await c.say('Pipo', 'Agora meu soldadinho é o general da vila!', 'child', 'smile');
    },
  });
  m.npcs.push({
    id: 'rosa_out', name: 'Marta', look: 'villager_f', tx: 21, ty: 12, wander: true,
    talk: async (c) => { await sayAll(c, 'Marta', 'villager_f', ['Dizem que a luz do Cristal está falhando. Ontem à noite, vi o céu tremer!', 'Minha avó dizia: "Quando a Aurora vacilar, um herdeiro despertará." Será você?']); },
  });
  m.npcs.push({
    id: 'orlando', name: 'Orlando', look: 'villager_m', tx: 33, ty: 21, wander: true,
    talk: async (c) => { await sayAll(c, 'Orlando', 'villager_m', ['A floresta ao sul era tão tranquila... agora há lobos do tamanho de bois!', 'Dizem que uma "Alfa" comanda a matilha. Tome cuidado, rapaz.']); },
  });
  m.npcs.push({
    id: 'teo', name: 'Vovô Teo', look: 'elder_m', tx: 15, ty: 12, dir: 'right',
    talk: async (c) => { await sayAll(c, 'Vovô Teo', 'elder_m', ['Eu vi o último Guardião, sabia? Era jovem... vestia um cachecol vermelho como o seu.', 'Ele sorria muito. Estranho — para quem carregava o fim do mundo nos ombros.']); },
  });
  m.npcs.push({
    id: 'dario', name: 'Capitão Dario', look: 'guard', tx: 46, ty: 15, dir: 'down',
    talk: async (c) => {
      if (G.has('ch1_done')) await sayAll(c, 'Capitão Dario', 'guard', ['O Conselho abrirá a Estrada Dourada em breve. Você merece descanso, herói.']);
      else await sayAll(c, 'Capitão Dario', 'guard', ['Ordens do Conselho: ninguém passa pela estrada leste até o Cristal ser estabilizado.', 'Se quiser ajudar, vá ao sul. A floresta é perigosa, mas é a única saída aberta.']);
    },
  });
  m.npcs.push({
    id: 'tioze', name: 'Tio Zé', look: 'fisher', tx: 11, ty: 31, dir: 'right',
    marker: () => (!G.quests['s_fisher'] ? '!' : null),
    talk: async (c) => {
      const q = G.quests['s_fisher'];
      if (!q) {
        await c.say('Tio Zé', 'Shhh! Está assustando os peixes! ...Ah, é você. Sabe do que eu preciso? Gel de Slime. Isca perfeita!', 'fisher', 'smile');
        await c.say('Tio Zé', 'Traga 3 Géis de Slime e te dou meu amuleto da sorte de estimação.', 'fisher');
        c.startQuest('s_fisher');
      } else if (q.state === 'active') {
        if (G.count('slime_gel') >= 3) { c.take('slime_gel', 3); await c.say('Tio Zé', 'Hohoho! Que gosma magnífica! Aqui, é seu!', 'fisher', 'smile'); c.completeQuest('s_fisher'); }
        else await c.say('Tio Zé', `Ainda preciso de Gel de Slime. Você tem ${G.count('slime_gel')}/3.`, 'fisher');
      } else await c.say('Tio Zé', 'Hoje está mordendo! Obrigado pela isca, rapaz.', 'fisher', 'smile');
    },
  });
  m.npcs.push({
    id: 'kid2', name: 'Lia', look: 'child', tx: 20, ty: 17, wander: true,
    talk: async (c) => { await sayAll(c, 'Lia', 'child', ['Você é o herói da Selene? Mostra o pingente! ...Uau, brilha!', 'Quando eu crescer, vou ser uma maga de Celestia!']); },
  });
  return m.build({ music: 'village', ambient: 'leaves', tint: '#fff2dc', start: { tx: 25, ty: 22 } });
}
registerMap('vila_alvorada', buildVillage);
