import type { Elem } from './skills';

export type AI = 'hop' | 'bat' | 'pounce' | 'melee' | 'archer' | 'caster' | 'golem' | 'wisp' | 'shadow' | 'boss_wolf' | 'boss_slimeking' | 'boss_crystal';

export interface EnemyDef {
  id: string;
  name: string;
  art: string;
  level: number;
  hp: number;
  atk: number;
  def: number;
  spd: number;
  xp: number;
  gold: [number, number];
  ai: AI;
  radius: number;      // hurtbox radius
  hitH: number;        // hurtbox centre height above feet
  drops: { id: string; chance: number }[];
  weak?: Elem[];
  resist?: Elem[];
  fly?: boolean;
  boss?: boolean;
  aggro?: number;
  elem?: Elem;
}

const E: EnemyDef[] = [
  { id: 'slime', name: 'Slime Verde', art: 'slime_green', level: 1, hp: 26, atk: 7, def: 0, spd: 26, xp: 7, gold: [2, 6], ai: 'hop', radius: 8, hitH: 7, drops: [{ id: 'slime_gel', chance: 0.5 }, { id: 'herb', chance: 0.15 }], weak: ['fire'] },
  { id: 'slime_blue', name: 'Slime Gélido', art: 'slime_blue', level: 3, hp: 44, atk: 11, def: 1, spd: 28, xp: 14, gold: [4, 10], ai: 'hop', radius: 8, hitH: 7, drops: [{ id: 'slime_gel', chance: 0.6 }, { id: 'potion', chance: 0.1 }], weak: ['fire'], resist: ['ice'], elem: 'ice' },
  { id: 'slime_red', name: 'Slime Rubro', art: 'slime_red', level: 5, hp: 62, atk: 16, def: 2, spd: 32, xp: 22, gold: [6, 14], ai: 'hop', radius: 8, hitH: 7, drops: [{ id: 'slime_gel', chance: 0.6 }, { id: 'ember', chance: 0.12 }], weak: ['ice'], resist: ['fire'], elem: 'fire' },
  { id: 'bat', name: 'Morcego Sombrio', art: 'bat', level: 2, hp: 20, atk: 8, def: 0, spd: 58, xp: 9, gold: [3, 8], ai: 'bat', radius: 7, hitH: 12, drops: [{ id: 'bat_wing', chance: 0.4 }], fly: true, weak: ['bolt'] },
  { id: 'bat_fire', name: 'Morcego Ígneo', art: 'bat_fire', level: 6, hp: 40, atk: 16, def: 1, spd: 66, xp: 20, gold: [6, 14], ai: 'bat', radius: 7, hitH: 12, drops: [{ id: 'bat_wing', chance: 0.4 }, { id: 'ember', chance: 0.1 }], fly: true, weak: ['ice'], resist: ['fire'] },
  { id: 'wolf', name: 'Lobo Cinzento', art: 'wolf', level: 4, hp: 58, atk: 13, def: 2, spd: 56, xp: 20, gold: [5, 12], ai: 'pounce', radius: 9, hitH: 8, drops: [{ id: 'wolf_fang', chance: 0.45 }], weak: ['fire'] },
  { id: 'wolf_dark', name: 'Lobo da Sombra', art: 'wolf_dark', level: 7, hp: 98, atk: 22, def: 4, spd: 64, xp: 36, gold: [9, 20], ai: 'pounce', radius: 9, hitH: 8, drops: [{ id: 'wolf_fang', chance: 0.5 }, { id: 'potion', chance: 0.15 }], weak: ['holy', 'fire'] },
  { id: 'goblin', name: 'Goblin Saqueador', art: 'goblin', level: 3, hp: 46, atk: 11, def: 1, spd: 40, xp: 15, gold: [8, 18], ai: 'melee', radius: 8, hitH: 12, drops: [{ id: 'goblin_ear', chance: 0.5 }, { id: 'potion', chance: 0.12 }] },
  { id: 'goblin_archer', name: 'Goblin Arqueiro', art: 'goblin_archer', level: 4, hp: 38, atk: 13, def: 1, spd: 38, xp: 18, gold: [8, 18], ai: 'archer', radius: 8, hitH: 12, drops: [{ id: 'goblin_ear', chance: 0.5 }, { id: 'ether', chance: 0.1 }] },
  { id: 'mushroom', name: 'Cogumelo Espora', art: 'mushroom', level: 3, hp: 40, atk: 10, def: 2, spd: 22, xp: 14, gold: [3, 9], ai: 'caster', radius: 8, hitH: 10, drops: [{ id: 'spore_cap', chance: 0.55 }, { id: 'herb', chance: 0.2 }], weak: ['fire'] },
  { id: 'skeleton', name: 'Esqueleto Guerreiro', art: 'skeleton', level: 7, hp: 92, atk: 21, def: 5, spd: 42, xp: 34, gold: [10, 24], ai: 'melee', radius: 8, hitH: 12, drops: [{ id: 'old_bone', chance: 0.5 }, { id: 'potion', chance: 0.15 }], weak: ['holy', 'fire'], resist: ['dark', 'ice'] },
  { id: 'skeleton_mage', name: 'Esqueleto Mago', art: 'skeleton_mage', level: 8, hp: 70, atk: 24, def: 3, spd: 34, xp: 40, gold: [12, 28], ai: 'caster', radius: 8, hitH: 12, drops: [{ id: 'old_bone', chance: 0.4 }, { id: 'ether', chance: 0.2 }], weak: ['holy'], elem: 'dark' },
  { id: 'wisp', name: 'Fogo-Fátuo', art: 'wisp_fire', level: 7, hp: 56, atk: 20, def: 2, spd: 40, xp: 30, gold: [8, 20], ai: 'wisp', radius: 7, hitH: 12, drops: [{ id: 'ember', chance: 0.4 }], fly: true, weak: ['ice'], resist: ['fire'], elem: 'fire' },
  { id: 'shadow', name: 'Soldado das Sombras', art: 'shadow_knight', level: 9, hp: 130, atk: 28, def: 7, spd: 46, xp: 54, gold: [14, 30], ai: 'shadow', radius: 8, hitH: 12, drops: [{ id: 'potion', chance: 0.25 }, { id: 'hi_potion', chance: 0.05 }], weak: ['holy'], elem: 'dark' },
  { id: 'golem', name: 'Golem de Cristal', art: 'golem_crystal', level: 8, hp: 210, atk: 30, def: 9, spd: 22, xp: 70, gold: [20, 40], ai: 'golem', radius: 12, hitH: 16, drops: [{ id: 'crystal_shard', chance: 0.6 }], weak: ['bolt'], resist: ['phys'] },
  // bosses
  { id: 'boss_slimeking', name: 'Rei Slime Gelatino', art: 'slime_king', level: 5, hp: 420, atk: 16, def: 2, spd: 30, xp: 140, gold: [60, 90], ai: 'boss_slimeking', radius: 22, hitH: 20, drops: [{ id: 'hi_potion', chance: 1 }, { id: 'lucky_charm', chance: 1 }], boss: true, weak: ['fire'] },
  { id: 'boss_wolf', name: 'Fenrisa, a Alfa Cinzenta', art: 'wolf_alpha', level: 6, hp: 640, atk: 22, def: 4, spd: 62, xp: 220, gold: [80, 120], ai: 'boss_wolf', radius: 16, hitH: 14, drops: [{ id: 'wolf_fang_blade', chance: 1 }, { id: 'wolf_fang', chance: 1 }], boss: true, weak: ['fire', 'bolt'] },
  { id: 'boss_crystal', name: 'Cristalion, Guardião da Câmara', art: 'crystal_guardian', level: 9, hp: 1300, atk: 32, def: 8, spd: 24, xp: 520, gold: [200, 260], ai: 'boss_crystal', radius: 24, hitH: 30, drops: [{ id: 'crystal_edge', chance: 1 }, { id: 'aurora_shard_1', chance: 1 }], boss: true, weak: ['bolt'], resist: ['ice'] },
];

export const ENEMIES: Record<string, EnemyDef> = Object.fromEntries(E.map((e) => [e.id, e]));
