export type Tree = 'blade' | 'arcane' | 'spirit';
export type Elem = 'phys' | 'fire' | 'ice' | 'bolt' | 'holy' | 'dark';

export type SkillKind =
  | 'wave' | 'whirl' | 'dash' | 'slam' | 'multi'
  | 'bolt' | 'lance' | 'chain' | 'nova' | 'meteor'
  | 'heal' | 'shield' | 'buff' | 'phase' | 'summon';

export interface SkillDef {
  id: string;
  name: string;
  tree: Tree;
  kind: SkillKind;
  elem: Elem;
  icon: string;
  desc: string;
  reqLevel: number;
  mp: number;
  cd: number;
  power: number;   // damage multiplier (of ATK for blade, MAG for others)
  range?: number;
  maxRank: number;
  scale: 'atk' | 'mag';
}

export const TREE_INFO: Record<Tree, { name: string; color: string; desc: string }> = {
  blade: { name: 'Lâmina', color: '#ff7a5a', desc: 'Técnicas de espada. Dano físico com ATK.' },
  arcane: { name: 'Arcano', color: '#7ab8ff', desc: 'Magias elementais. Dano com MAG.' },
  spirit: { name: 'Espírito', color: '#7ae8a8', desc: 'Cura, proteção e invocações.' },
};

export const SKILLS: SkillDef[] = [
  // ----- Lâmina -----
  { id: 'crescent', name: 'Corte Crescente', tree: 'blade', kind: 'wave', elem: 'phys', icon: 'slash', desc: 'Lança uma onda cortante que atravessa inimigos.', reqLevel: 1, mp: 6, cd: 1.6, power: 1.5, maxRank: 5, scale: 'atk' },
  { id: 'whirlwind', name: 'Redemoinho', tree: 'blade', kind: 'whirl', elem: 'phys', icon: 'whirl', desc: 'Gira a lâmina atingindo todos ao redor.', reqLevel: 3, mp: 12, cd: 4, power: 1.7, range: 38, maxRank: 5, scale: 'atk' },
  { id: 'lunge', name: 'Investida Relâmpago', tree: 'blade', kind: 'dash', elem: 'phys', icon: 'dash', desc: 'Avança velozmente cortando tudo pelo caminho.', reqLevel: 5, mp: 10, cd: 3.5, power: 2.0, range: 80, maxRank: 5, scale: 'atk' },
  { id: 'quake', name: 'Golpe Sísmico', tree: 'blade', kind: 'slam', elem: 'phys', icon: 'slam', desc: 'Esmaga o chão, causando dano em área e atordoando.', reqLevel: 8, mp: 18, cd: 7, power: 2.4, range: 46, maxRank: 5, scale: 'atk' },
  { id: 'bladedance', name: 'Dança das Lâminas', tree: 'blade', kind: 'multi', elem: 'phys', icon: 'blades', desc: 'Sequência de 6 cortes rápidos no alvo mais próximo.', reqLevel: 12, mp: 26, cd: 10, power: 0.9, range: 60, maxRank: 5, scale: 'atk' },
  // ----- Arcano -----
  { id: 'fireball', name: 'Bola de Fogo', tree: 'arcane', kind: 'bolt', elem: 'fire', icon: 'fire', desc: 'Projétil flamejante que explode e queima.', reqLevel: 2, mp: 8, cd: 1.4, power: 1.6, maxRank: 5, scale: 'mag' },
  { id: 'icelance', name: 'Lança de Gelo', tree: 'arcane', kind: 'lance', elem: 'ice', icon: 'ice', desc: 'Estaca de gelo veloz que reduz a velocidade.', reqLevel: 4, mp: 9, cd: 2, power: 1.7, maxRank: 5, scale: 'mag' },
  { id: 'chainbolt', name: 'Raio em Cadeia', tree: 'arcane', kind: 'chain', elem: 'bolt', icon: 'bolt', desc: 'Raio que salta entre até 4 inimigos.', reqLevel: 7, mp: 16, cd: 4, power: 1.5, range: 110, maxRank: 5, scale: 'mag' },
  { id: 'frostnova', name: 'Nova Glacial', tree: 'arcane', kind: 'nova', elem: 'ice', icon: 'nova', desc: 'Explosão de gelo que congela os inimigos próximos.', reqLevel: 10, mp: 24, cd: 9, power: 1.9, range: 56, maxRank: 5, scale: 'mag' },
  { id: 'meteor', name: 'Meteoro', tree: 'arcane', kind: 'meteor', elem: 'fire', icon: 'meteor', desc: 'Invoca um meteoro devastador na direção alvo.', reqLevel: 15, mp: 40, cd: 14, power: 4.2, range: 48, maxRank: 5, scale: 'mag' },
  // ----- Espírito -----
  { id: 'heal', name: 'Luz Restauradora', tree: 'spirit', kind: 'heal', elem: 'holy', icon: 'heal', desc: 'Recupera HP com energia sagrada.', reqLevel: 2, mp: 14, cd: 6, power: 1.8, maxRank: 5, scale: 'mag' },
  { id: 'barrier', name: 'Escudo Etéreo', tree: 'spirit', kind: 'shield', elem: 'holy', icon: 'shield', desc: 'Barreira que absorve dano por alguns segundos.', reqLevel: 6, mp: 18, cd: 12, power: 2.2, maxRank: 5, scale: 'mag' },
  { id: 'fury', name: 'Aura de Fúria', tree: 'spirit', kind: 'buff', elem: 'holy', icon: 'rage', desc: 'Aumenta ATK e MAG por 12 segundos.', reqLevel: 9, mp: 20, cd: 25, power: 0.25, maxRank: 5, scale: 'mag' },
  { id: 'phantom', name: 'Passo Fantasma', tree: 'spirit', kind: 'phase', elem: 'dark', icon: 'ghost', desc: 'Teleporta e ganha invulnerabilidade breve.', reqLevel: 11, mp: 14, cd: 8, power: 0, range: 90, maxRank: 5, scale: 'mag' },
  { id: 'guardians', name: 'Espíritos Guardiões', tree: 'spirit', kind: 'summon', elem: 'holy', icon: 'spirit', desc: 'Invoca espíritos que orbitam e ferem inimigos.', reqLevel: 14, mp: 32, cd: 20, power: 0.9, maxRank: 5, scale: 'mag' },
];

export const SKILL_MAP: Record<string, SkillDef> = Object.fromEntries(SKILLS.map((s) => [s.id, s]));

export const rankPower = (s: SkillDef, rank: number) => s.power * (1 + 0.22 * (rank - 1));
export const rankCost = (s: SkillDef, rank: number) => Math.round(s.mp * (1 + 0.06 * (rank - 1)));
export const rankCd = (s: SkillDef, rank: number) => Math.max(0.6, s.cd * (1 - 0.05 * (rank - 1)));
