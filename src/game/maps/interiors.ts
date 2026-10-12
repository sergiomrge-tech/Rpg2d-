import { MB } from '../world/map';
import { registerMap } from '../world/maps';
import { T } from '../../art/tiles';
import { G } from '../state';
import type { ScriptCtx } from '../script';

function room(id: string, name: string, w: number, h: number, seed: number) {
  const m = new MB(id, name, w, h, T.WOOD, seed);
  m.fill(T.DWOOD, 0, 0, w, 2);
  for (let y = 2; y < h; y++) { m.set(T.DWOOD, 0, y); m.set(T.DWOOD, w - 1, y); }
  m.fill(T.DWOOD, 0, h - 1, w, 1);
  return m;
}

export function buildHeroHouse() {
  const m = room('casa_heroi', 'Casa do Herói', 12, 9, 7);
  const door = 5;
  m.set(T.WOOD, door, 8);
  m.fill(T.RUG, 4, 4, 4, 3);
  m.obj('bed', 2, 3, 0);
  m.obj('table', 8, 4, 0);
  m.obj('bookshelf', 8, 2, 0, { id: 'hero_shelf' });
  m.obj('plant', 1, 6, 1); m.obj('jar', 10, 6, 0); m.obj('barrel', 10, 3, 0);
  m.obj('torch', 3, 2, 0); m.obj('torch', 7, 2, 0);
  m.obj('banner_blue', 5, 2, 0);
  m.chests.push({ id: 'hero_chest', tx: 1, ty: 5, item: 'herb', count: 3 });
  m.warps.push({ tx: door, ty: 8, w: 1, h: 1, to: 'vila_alvorada', ntx: 10, nty: 14, dir: 'down' });
  m.npcs.push({
    id: 'mira_intro', name: 'Anciã Mira', look: 'mira', tx: 5, ty: 7, dir: 'up',
    show: () => !G.has('intro_done'),
    talk: async () => {},
  });
  return m.build({
    music: 'sad', indoor: true, wallKind: 'house', tint: '#ffe8cc',
    onEnter: async (c: ScriptCtx) => {
      if (G.has('intro_done')) return;
      c.world.letterbox = 1;
      c.world.fadeA = 1;
      c.world.player.x = 3 * 16 + 14; c.world.player.y = 4 * 16 + 14; c.world.player.dir = 'down';
      c.music('sad');
      await c.wait(0.6);
      await c.fadeIn(0.5);
      await c.say('', '...A luz era dourada. Quente. E então, um som de vidro quebrando ecoou por todo o céu.');
      await c.say('', 'No sonho, uma silhueta de cabelos brancos estendeu a mão em minha direção. Seus olhos eram... violeta.');
      await c.wait(0.4);
      c.sfx('explosion'); c.shake(8);
      await c.say('', 'BOOM! A casa inteira estremece!');
      await c.hero('— Ugh! O que foi isso?!', 'surprised');
      c.world.letterbox = 0;
      await c.moveNpc('mira_intro', 5, 5);
      await c.say('Anciã Mira', `${G.name}! Acorde! Depressa!`, 'mira', 'surprised');
      await c.say('Anciã Mira', 'O Cristal da Aurora... rachou. Eu senti. As Sombras vão descer sobre a vila ao amanhecer.', 'mira', 'sad');
      await c.hero('Mira? Do que está falando? O Cristal é só uma lenda...', 'surprised');
      await c.say('Anciã Mira', 'É por isso que lhe dei este pingente, criança. Ele pulsa quando o Cristal sofre. Ele está pulsando agora, não está?', 'mira');
      c.world.toast('Pingente da Aurora', 'amulet');
      c.sfx('chest');
      G.addItem('aurora_pendant', 1);
      await c.hero('...Está. Queima, como se estivesse vivo.', 'sad');
      await c.say('Anciã Mira', 'Vá à praça, encontre a Mestra Selene. Ela vai prepará-lo. E, por favor... tenha coragem.', 'mira', 'smile');
      await c.moveNpc('mira_intro', 5, 7);
      c.flag('intro_done', true);
      c.startQuest('m1_call');
      c.banner('Capítulo 1', 'O Despertar');
      c.world.npcs = c.world.npcs.filter((n) => n.def.id !== 'mira_intro');
    },
  });
}
registerMap('casa_heroi', buildHeroHouse);

export function buildMiraHouse() {
  const m = room('casa_mira', 'Casa da Anciã Mira', 14, 9, 17);
  const door = 6;
  m.set(T.WOOD, door, 8);
  m.fill(T.RUG, 4, 4, 6, 3);
  m.obj('bookshelf', 2, 2, 0, { id: 'lore1' }); m.obj('bookshelf', 4, 2, 0, { id: 'lore2' }); m.obj('bookshelf', 10, 2, 0, { id: 'lore3' });
  m.obj('table', 8, 5, 0);
  m.obj('plant', 1, 6, 2); m.obj('plant', 12, 6, 0); m.obj('jar', 12, 3, 1);
  m.obj('torch', 7, 2, 0); m.obj('banner_red', 9, 2, 0);
  m.chests.push({ id: 'mira_chest', tx: 11, ty: 6, item: 'ether', count: 2 });
  m.warps.push({ tx: door, ty: 8, w: 1, h: 1, to: 'vila_alvorada', ntx: 39, nty: 12, dir: 'down' });
  m.npcs.push({
    id: 'mira_home', name: 'Anciã Mira', look: 'mira', tx: 8, ty: 3, dir: 'down',
    talk: async (c) => {
      if (G.has('ch1_done')) { await c.say('Anciã Mira', 'Descanse, criança. O destino pode esperar uma noite.', 'mira', 'smile'); c.heal(); return; }
      await c.say('Anciã Mira', 'Meus livros guardam as Crônicas dos Sete Guardiões. Se tiver curiosidade, leia as estantes.', 'mira', 'smile');
    },
  });
  return m.build({ music: 'village', indoor: true, wallKind: 'house', tint: '#ffe8cc' });
}
registerMap('casa_mira', buildMiraHouse);

export function buildInn() {
  const m = room('estalagem', 'Estalagem do Cervo Dourado', 14, 9, 27);
  const door = 6;
  m.set(T.WOOD, door, 8);
  m.fill(T.RUG, 5, 5, 4, 2);
  m.obj('table', 3, 4, 0); m.obj('table', 10, 4, 0); m.obj('table', 2, 7, 0);
  m.obj('barrel', 12, 2, 0); m.obj('barrel', 13, 2, 0); m.obj('crate', 1, 3, 0);
  m.obj('bed', 11, 7, 0);
  m.obj('torch', 4, 2, 0); m.obj('torch', 9, 2, 0); m.obj('banner_red', 6, 2, 0);
  m.obj('plant', 1, 5, 1);
  m.warps.push({ tx: door, ty: 8, w: 1, h: 1, to: 'vila_alvorada', ntx: 39, nty: 26, dir: 'down' });
  m.npcs.push({
    id: 'rosa', name: 'Dona Rosa', look: 'innkeeper', tx: 6, ty: 3, dir: 'down',
    marker: () => (!G.quests['s_herbs'] ? '!' : null),
    talk: async (c) => {
      const q = G.quests['s_herbs'];
      await c.say('Dona Rosa', 'Bem-vindo ao Cervo Dourado, querido! Um quarto custa 15 de ouro e você acorda novinho em folha.', 'innkeeper', 'smile');
      const opts = ['Descansar (15 G)', 'Falar sobre ervas', 'Sair'];
      const k = await c.choice(opts);
      if (k === 0) {
        if (G.gold < 15) { await c.say('Dona Rosa', 'Ah, querido... você está sem ouro. Volte quando puder.', 'innkeeper', 'sad'); return; }
        G.gold -= 15;
        await c.fadeOut(1.5); c.heal(); c.sfx('save'); await c.wait(0.6); await c.fadeIn(1.5);
        c.setSpawn();
        await c.say('Dona Rosa', 'Dormiu como um anjo! HP e MP restaurados.', 'innkeeper', 'smile');
      } else if (k === 1) {
        if (!q) {
          await c.say('Dona Rosa', 'Estou precisando de 3 Ervas Curativas para o meu ensopado especial. As melhores crescem na floresta!', 'innkeeper');
          c.startQuest('s_herbs');
        } else if (q.state === 'active') {
          if (G.count('herb') >= 3) { c.take('herb', 3); await c.say('Dona Rosa', 'Que cheirinho! Muito obrigada, querido. Pegue isto como pagamento!', 'innkeeper', 'smile'); c.completeQuest('s_herbs'); }
          else await c.say('Dona Rosa', `Você tem ${G.count('herb')}/3 Ervas Curativas.`, 'innkeeper');
        } else await c.say('Dona Rosa', 'O ensopado está uma delícia, graças a você!', 'innkeeper', 'smile');
      }
    },
  });
  m.npcs.push({
    id: 'bardo', name: 'Bardo Lúcio', look: 'villager_m', tx: 10, ty: 6, dir: 'left',
    talk: async (c) => {
      await c.say('Bardo Lúcio', '♪ Sete Guardiões, sete luzes no céu... um caiu, outro dormiu, e o resto se perdeu... ♪', 'villager_m', 'smile');
      await c.say('Bardo Lúcio', 'Dizem que o herdeiro tem o cachecol da cor do sangue e a coragem de quem não sabe o que o espera!', 'villager_m');
    },
  });
  return m.build({ music: 'village', indoor: true, wallKind: 'house', tint: '#ffe8cc' });
}
registerMap('estalagem', buildInn);
