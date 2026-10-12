import type { World } from '../world/world';
import type { ScriptCtx } from '../script';
import type { Enemy } from '../entities';
import { G } from '../state';
import { Audio } from '../../engine/audio';
import { QUESTS } from './quests';
import { NpcDef } from '../world/map';

const lore = (lines: string[]) => async (c: ScriptCtx) => { for (const l of lines) await c.say('', l); };

/** Wires story/event hooks to the world's script runner. */
export function installStory(world: World) {
  const h = world.script.hooks;

  h.objectTalk['hero_shelf'] = lore(['Seus livros de aventuras favoritos. Um deles tem a capa gasta: "O Cavaleiro que Enganou a Noite".']);
  h.objectTalk['bed'] = async (c) => { await c.say('', 'Sua cama. Ainda quente.'); };
  h.objectTalk['well'] = lore(['Um poço antigo. A água reflete o céu... e, por um instante, algo brilhando no fundo.']);
  h.objectTalk['lore1'] = lore(['CRÔNICAS DOS SETE GUARDIÕES, vol. I', '"No princípio, a Noite era tudo. Então Aurora, a primeira Guardiã, acendeu uma luz que se recusou a apagar."']);
  h.objectTalk['lore2'] = lore(['CRÔNICAS DOS SETE GUARDIÕES, vol. III', '"Sete se uniram: Lâmina, Arcano, Espírito, Fera, Tempo, Tormenta e Sombra. Mas um deles não voltou da selagem de Nyxar."']);
  h.objectTalk['lore3'] = lore(['DIÁRIO DE MIRA — última página', '"Ele tem os olhos dela. Rezo para que a luz o proteja do destino que o espera. Eu sei que o outro... ainda vive."']);

  h.onMapEnter = async (c: ScriptCtx, id: string) => {
    if (id === 'floresta' && !G.has('forest_seen')) {
      c.flag('forest_seen', true);
      c.completeQuest('m1_call');
      c.startQuest('m1_forest');
      c.banner('Floresta Sussurrante', 'As árvores sussurram o seu nome...');
    }
    if (id === 'caverna' && !G.has('cave_seen')) {
      c.flag('cave_seen', true);
      c.completeQuest('m1_forest');
      c.startQuest('m1_cave');
      await c.wait(1.0);
      if (G.has('ally_lyra')) await c.say('Lyra', 'Este lugar... a energia arcana é densa. Cristais se alimentam da Aurora. Mantenha os olhos abertos!', 'lyra', 'neutral');
      await c.narrate('Dica: use habilidades com 1-4 e esquive com K/X. Salve nos cristais de salvamento!');
    }
    if (id === 'vila_alvorada' && G.has('dead_boss_cristalion') && !G.has('ch1_done')) {
      await endChapter1(c);
    }
    if (id === 'vila_alvorada' && G.has('intro_done') && !G.has('arrived_village')) {
      c.flag('arrived_village', true);
    }
    // restore music after cutscenes
    if (!G.has('dead_boss_cristalion') || id !== 'caverna') { /* noop */ }
  };

  h.onItem = (c: ScriptCtx, id: string) => {
    if (id === 'crystal_key') { c.questStep('m1_cave', 1); c.world.toast('A Chave de Cristal! Leve-a ao selo.', 'key', '#7ae8ff'); }
    if (id === 'herb' && G.quests['s_herbs']?.state === 'active') c.world.toast(`Ervas: ${G.count('herb')}/3`, 'herb');
  };

  h.onKill = (c: ScriptCtx, e: Enemy) => {
    const w = c.world;
    // tutorial battle
    if (G.has('tutorial_done') && !G.has('battle1_done') && w.def.id === 'vila_alvorada') {
      const left = w.enemies.filter((x) => x !== e && x.state !== 'dying' && !x.dead).length;
      if (left === 0) {
        G.flags['battle1_done'] = true;
        c.questStep('m1_call', 2);
        void w.script.run(async () => {
          await c.wait(0.6);
          c.music('');
          Audio.music(w.def.music);
          await c.say('Mestra Selene', 'Excelente! Você tem o reflexo dos antigos. Agora vá falar com a Anciã Mira — ela está esperando na praça.', 'mystic', 'smile');
          // reload so the conditional NPC appears
          w.loadMap('vila_alvorada', Math.floor(w.player.x / 16), Math.floor(w.player.y / 16), w.player.dir, true);
        });
      }
    }
    // slime quest
    const q = G.quests['s_slimes'];
    if (q && q.state === 'active' && q.step === 0 && e.def.id.startsWith('slime') || (q && q.state === 'active' && q.step === 0 && e.def.id === 'boss_slimeking')) {
      q.progress += e.def.boss ? 5 : 1;
      w.toast(`Slimes: ${Math.min(5, q.progress)}/5`, 'core');
      if (q.progress >= 5) c.questStep('s_slimes', 1);
    }
    // key golem drops the key
    if (e.spawnId === 'golem_key') { w.drop(e.x, e.y, 'item', 'crystal_key', 1); w.toast('O Golem deixou cair algo brilhante...', 'key'); }

    if (e.def.boss) {
      w.musicOverride = null;
      w.bossBar = null;
      void w.script.run(async () => {
        c.music('');
        Audio.music(w.def.music);
        await c.wait(1.2);
        if (e.def.id === 'boss_wolf') {
          c.questStep('m1_forest', 2);
          await c.narrate('Fenrisa solta um último uivo. A névoa negra deixa seus olhos e, por um instante, eles brilham em âmbar. Então ela some entre as árvores.');
          if (G.has('ally_lyra')) await c.say('Lyra', 'A corrupção era das Sombras, não dela. As raízes estão se abrindo... o caminho para a caverna está livre!', 'lyra', 'smile');
          await c.narrate('As lojas da vila agora têm novos estoques! (Gorim e Bento)');
        } else if (e.def.id === 'boss_slimeking') {
          await c.narrate('O Rei Slime se desfaz em uma poça brilhante. No meio dela repousa um soldadinho de madeira... e um amuleto.');
        } else if (e.def.id === 'boss_crystal') {
          await cristalionEnd(c);
        }
      });
    }
  };
}

const VELKAN: NpcDef = { id: 'velkan', name: 'Velkan', look: 'velkan', tx: 30, ty: 10, dir: 'up', talk: async () => {} };

async function cristalionEnd(c: ScriptCtx) {
  const w = c.world;
  c.questStep('m1_cave', 3);
  await c.narrate('Cristalion se desfaz em milhares de fragmentos luminosos. No ar, o Cristal Menor da Aurora flutua, pulsando em sintonia com o seu pingente.');
  c.sfx('save');
  await c.say('', 'Você obteve o Cristal Menor da Aurora!');
  await c.wait(0.5);
  c.sfx('roar'); c.shake(6);
  w.fadeColor = '#ffffff'; await c.fadeOut(5); w.fadeColor = '#000'; w.spawnNpcFn(VELKAN); await c.fadeIn(2);
  w.burst(30 * 16 + 8, 10 * 16, 40, ['#a020f0', '#fff', '#3a1060'], { speed: 100, life: 1.0, size: 3 });
  c.music('sad');
  await c.say('???', 'Impressionante. Você realmente consegue ouvi-lo. O Guardião era apenas um teste... e você passou.', 'velkan', 'smug');
  await c.hero('Quem é você? Como entrou aqui?', 'angry');
  if (G.has('ally_lyra')) await c.say('Lyra', 'Essa aura... é magia das Sombras! E tão refinada... quem é esse sujeito?', 'lyra', 'surprised');
  await c.say('Velkan', 'Meu nome é Velkan. E você, ' + G.name + '... tem o rosto de alguém que eu conheci. Há muito tempo.', 'velkan');
  await c.say('Velkan', 'Guarde o Cristal Menor. Ele será... útil. Nos veremos na Estrada Dourada, irmão.', 'velkan', 'smile');
  await c.hero('Irmão...?', 'surprised');
  c.sfx('explosion');
  w.burst(30 * 16 + 8, 10 * 16, 50, ['#a020f0', '#000', '#fff'], { speed: 120, life: 1.2, size: 3 });
  w.npcs = w.npcs.filter((n) => n.def.id !== 'velkan');
  c.music('');
  Audio.music(w.def.music);
  await c.wait(0.8);
  if (G.has('ally_lyra')) await c.say('Lyra', 'Ele sabia do seu pingente. Sabia da Aurora. ...E ele disse "irmão". Precisamos voltar à vila. Agora.', 'lyra', 'sad');
  w.addObject('portal', 29, 4, 0);
  c.toast('Um portal se abriu no fundo da câmara.', 'crystal', '#b48cff');
  await c.narrate('Um portal de luz se abre no fundo da câmara. Ele levará você de volta a Alvorada.');
}

async function endChapter1(c: ScriptCtx) {
  const w = c.world;
  w.letterbox = 1;
  w.spawnNpcFn({ id: 'mira_end', name: 'Anciã Mira', look: 'mira', tx: 25, ty: 19, dir: 'down', talk: async () => {} });
  w.spawnNpcFn({ id: 'selene_end', name: 'Selene', look: 'mystic', tx: 27, ty: 19, dir: 'down', talk: async () => {} });
  await c.wait(0.4);
  await c.moveHero(25, 21, 60);
  c.face('up');
  await c.say('Anciã Mira', 'Você voltou! E trouxe... o Cristal Menor! Pelos Sete, está intacto!', 'mira', 'surprised');
  await c.hero('Mira... na caverna, um homem apareceu. Velkan. Ele me chamou de irmão.', 'sad');
  await c.say('Anciã Mira', '...', 'mira', 'sad');
  await c.say('Anciã Mira', 'Então o dia chegou. Eu devia ter lhe contado há anos. Você nunca esteve sozinho no templo, criança. Havia outro bebê. Um gêmeo.', 'mira');
  await c.say('Mestra Selene', 'Velkan Valdrath, o "Príncipe do Eclipse". Dizem que o Culto da Noite o aclama como o receptáculo de Nyxar.', 'mystic', 'sad');
  await c.say('Anciã Mira', 'A Aurora o escolheu. A Noite também. Dois irmãos, duas metades da mesma profecia.', 'mira');
  if (G.has('ally_lyra')) await c.say('Lyra', 'Isso muda tudo. A Academia precisa saber. ' + G.name + ', eu fico com você até o fim. Não é uma pergunta.', 'lyra', 'smile');
  c.sfx('save');
  await c.say('Anciã Mira', 'O Conselho abrirá a Estrada Dourada. O próximo Cristal está além do deserto de Porto Luz. Descanse. O mundo vai precisar de você inteiro.', 'mira', 'smile');
  c.completeQuest('m1_cave');
  c.flag('ch1_done', true);
  c.heal();
  w.letterbox = 0;
  w.npcs = w.npcs.filter((n) => n.def.id !== 'mira_end' && n.def.id !== 'selene_end');
  c.music('victory');
  await c.chapterEnd('FIM DO CAPÍTULO 1', 'O Despertar  ·  Próximo: Capítulo 2 — A Estrada Dourada (em desenvolvimento)');
  c.music('');
  Audio.music(w.def.music);
  c.world.toast('Você pode continuar explorando e completando missões!', 'star', '#ffe066');
}
void QUESTS;
