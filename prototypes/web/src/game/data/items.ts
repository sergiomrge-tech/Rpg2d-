export type ItemType = 'consumable' | 'weapon' | 'armor' | 'accessory' | 'key' | 'material';

export interface ItemStats { atk?: number; mag?: number; def?: number; hp?: number; mp?: number; crit?: number; spd?: number }

export interface ItemDef {
  id: string;
  name: string;
  desc: string;
  type: ItemType;
  icon: string;
  price: number;
  stats?: ItemStats;
  heal?: { hp?: number; mp?: number; pct?: boolean };
  reqLevel?: number;
}

const I: ItemDef[] = [
  // consumables
  { id: 'herb', name: 'Erva Curativa', desc: 'Restaura 30 HP.', type: 'consumable', icon: 'herb', price: 12, heal: { hp: 30 } },
  { id: 'potion', name: 'Poção de Vida', desc: 'Restaura 80 HP.', type: 'consumable', icon: 'potion_r', price: 35, heal: { hp: 80 } },
  { id: 'hi_potion', name: 'Poção Maior', desc: 'Restaura 220 HP.', type: 'consumable', icon: 'potion_r', price: 110, heal: { hp: 220 } },
  { id: 'ether', name: 'Éter', desc: 'Restaura 35 MP.', type: 'consumable', icon: 'potion_b', price: 45, heal: { mp: 35 } },
  { id: 'hi_ether', name: 'Éter Maior', desc: 'Restaura 90 MP.', type: 'consumable', icon: 'potion_b', price: 130, heal: { mp: 90 } },
  { id: 'elixir', name: 'Elixir', desc: 'Restaura todo o HP e MP.', type: 'consumable', icon: 'elixir', price: 400, heal: { hp: 100, mp: 100, pct: true } },
  // materials
  { id: 'slime_gel', name: 'Gel de Slime', desc: 'Substância viscosa e brilhante.', type: 'material', icon: 'core', price: 6 },
  { id: 'wolf_fang', name: 'Presa de Lobo', desc: 'Afiada e resistente.', type: 'material', icon: 'fang', price: 14 },
  { id: 'bat_wing', name: 'Asa de Morcego', desc: 'Membrana leve e escura.', type: 'material', icon: 'cloth', price: 9 },
  { id: 'goblin_ear', name: 'Orelha de Goblin', desc: 'Troféu repugnante.', type: 'material', icon: 'herb', price: 10 },
  { id: 'old_bone', name: 'Osso Antigo', desc: 'Resquício de um guerreiro.', type: 'material', icon: 'fang', price: 12 },
  { id: 'spore_cap', name: 'Chapéu de Esporos', desc: 'Cheira mal. Alquimistas adoram.', type: 'material', icon: 'herb', price: 11 },
  { id: 'crystal_shard', name: 'Fragmento de Cristal', desc: 'Vibra com energia arcana.', type: 'material', icon: 'crystal', price: 40 },
  { id: 'ember', name: 'Brasa Eterna', desc: 'Nunca se apaga.', type: 'material', icon: 'fire', price: 30 },
  // key items
  { id: 'aurora_pendant', name: 'Pingente da Aurora', desc: 'Pulsa suavemente. Pertenceu aos Guardiões.', type: 'key', icon: 'amulet', price: 0 },
  { id: 'crystal_key', name: 'Chave de Cristal', desc: 'Abre o selo da Câmara Profunda.', type: 'key', icon: 'key', price: 0 },
  { id: 'lyra_letter', name: 'Carta da Academia', desc: 'Selada com o brasão de Celestia.', type: 'key', icon: 'scroll', price: 0 },
  { id: 'aurora_shard_1', name: 'Cristal Menor da Aurora', desc: 'Parte da luz que protege o mundo.', type: 'key', icon: 'crystal', price: 0 },
  // weapons
  { id: 'rusty_sword', name: 'Espada Enferrujada', desc: 'Melhor que nada.', type: 'weapon', icon: 'sword', price: 10, stats: { atk: 3 } },
  { id: 'iron_sword', name: 'Espada de Ferro', desc: 'Lâmina confiável de ferreiro.', type: 'weapon', icon: 'sword', price: 140, stats: { atk: 8 } },
  { id: 'hunter_blade', name: 'Lâmina do Caçador', desc: 'Leve e rápida. +4% crítico.', type: 'weapon', icon: 'blades', price: 260, stats: { atk: 13, crit: 4 } },
  { id: 'apprentice_staff', name: 'Cajado de Aprendiz', desc: 'Amplifica magia.', type: 'weapon', icon: 'staff', price: 150, stats: { atk: 2, mag: 10 } },
  { id: 'wolf_fang_blade', name: 'Lâmina Presa-de-Lobo', desc: 'Forjada com a presa da Alfa.', type: 'weapon', icon: 'blades', price: 0, stats: { atk: 16, crit: 6, spd: 4 } },
  { id: 'crystal_edge', name: 'Gume de Cristal', desc: 'Corta como luz.', type: 'weapon', icon: 'sword', price: 0, stats: { atk: 20, mag: 8 } },
  // armor
  { id: 'linen_tunic', name: 'Túnica de Linho', desc: 'Roupa de viajante.', type: 'armor', icon: 'robe', price: 20, stats: { def: 2 } },
  { id: 'leather_armor', name: 'Couro Reforçado', desc: 'Flexível e resistente.', type: 'armor', icon: 'armor', price: 120, stats: { def: 6, hp: 10 } },
  { id: 'mage_robe', name: 'Manto Arcano', desc: 'Costurado com fios de mana.', type: 'armor', icon: 'robe', price: 170, stats: { def: 3, mag: 6, mp: 20 } },
  { id: 'chain_mail', name: 'Cota de Malha', desc: 'Pesada, mas segura.', type: 'armor', icon: 'armor', price: 320, stats: { def: 11, hp: 20 } },
  { id: 'crystal_mail', name: 'Armadura de Cristal', desc: 'Reflete golpes sombrios.', type: 'armor', icon: 'armor', price: 0, stats: { def: 15, hp: 30, mp: 10 } },
  // accessories
  { id: 'lucky_charm', name: 'Amuleto da Sorte', desc: '+5% de chance crítica.', type: 'accessory', icon: 'amulet', price: 180, stats: { crit: 5 } },
  { id: 'vigor_ring', name: 'Anel de Vigor', desc: '+40 HP máximo.', type: 'accessory', icon: 'ring', price: 200, stats: { hp: 40 } },
  { id: 'mana_pendant', name: 'Pingente de Mana', desc: '+30 MP máximo.', type: 'accessory', icon: 'amulet', price: 200, stats: { mp: 30 } },
  { id: 'swift_boots', name: 'Botas Ligeiras', desc: '+8% de velocidade.', type: 'accessory', icon: 'boots', price: 240, stats: { spd: 8 } },
  { id: 'guardian_sigil', name: 'Selo do Guardião', desc: '+4 DEF, +10 MP.', type: 'accessory', icon: 'star', price: 0, stats: { def: 4, mp: 10 } },
];

export const ITEMS: Record<string, ItemDef> = Object.fromEntries(I.map((i) => [i.id, i]));
export const itemName = (id: string) => ITEMS[id]?.name ?? id;
