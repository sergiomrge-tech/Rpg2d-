export interface QuestDef {
  id: string;
  name: string;
  main: boolean;
  steps: string[];          // objective text per step
  desc: string;
  reward?: { xp?: number; gold?: number; items?: [string, number][] };
}

export const QUESTS: Record<string, QuestDef> = {
  m1_call: {
    id: 'm1_call', name: 'O Chamado do Cristal', main: true,
    desc: 'O Cristal da Aurora, que protege Alvorada, começou a rachar. Mira pediu sua ajuda.',
    steps: ['Fale com a Mestra Selene na praça.', 'Derrote as Sombras na praça.', 'Fale com a Anciã Mira.', 'Atravesse a Floresta Sussurrante rumo à Caverna de Cristal.'],
  },
  m1_forest: {
    id: 'm1_forest', name: 'Uivos na Floresta', main: true,
    desc: 'Lobos corrompidos pelas sombras dominam a Floresta Sussurrante.',
    steps: ['Procure a origem dos uivos.', 'Derrote Fenrisa, a Alfa Cinzenta.', 'Entre na Caverna de Cristal.'],
    reward: { xp: 120, gold: 60 },
  },
  m1_cave: {
    id: 'm1_cave', name: 'O Coração da Caverna', main: true,
    desc: 'O Cristal Menor da Aurora repousa na Câmara Profunda, protegido por um Guardião.',
    steps: ['Encontre a Chave de Cristal.', 'Abra o selo da Câmara Profunda.', 'Derrote Cristalion e recupere o Cristal Menor.', 'Volte a Alvorada e entregue o cristal a Mira.'],
    reward: { xp: 300, gold: 150 },
  },
  s_slimes: {
    id: 's_slimes', name: 'Praga de Gosma', main: false,
    desc: 'Pipo, o menino da vila, perdeu o brinquedo para os slimes da floresta.',
    steps: ['Derrote 5 slimes na floresta.', 'Volte a falar com Pipo.'],
    reward: { xp: 60, gold: 40, items: [['potion', 2]] },
  },
  s_herbs: {
    id: 's_herbs', name: 'Ervas para a Estalagem', main: false,
    desc: 'Dona Rosa precisa de 3 Ervas Curativas para o ensopado especial.',
    steps: ['Colete 3 Ervas Curativas.', 'Entregue as ervas a Dona Rosa.'],
    reward: { xp: 50, gold: 30, items: [['ether', 2]] },
  },
  s_fisher: {
    id: 's_fisher', name: 'A Isca Perfeita', main: false,
    desc: 'Tio Zé jura que Gel de Slime é a melhor isca do mundo.',
    steps: ['Traga 3 Géis de Slime para Tio Zé.'],
    reward: { xp: 45, gold: 25, items: [['lucky_charm', 1]] },
  },
};
