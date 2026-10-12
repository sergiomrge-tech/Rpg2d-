class_name Data
extends RefCounted
## Static game databases: items, skills, enemies, recipes.

const ELEM_COLORS := {
	"phys": Color("ffffff"), "fire": Color("ff8a2a"), "ice": Color("8ae0ff"),
	"bolt": Color("ffe84a"), "holy": Color("fff2b0"), "dark": Color("c080ff"), "nature": Color("7aff8a"),
}
const RARITY_NAMES := ["Comum", "Incomum", "Raro", "Épico", "Lendário"]
const RARITY_COLORS := [Color("d8d4e8"), Color("6aff9a"), Color("5aa8ff"), Color("c080ff"), Color("ffb040")]

# ----------------------------------------------------------------------------- items
# type: consumable | material | key | tome | weapon | armor | accessory
const ITEMS := {
	# consumables
	"herb": {"name": "Erva Curativa", "type": "consumable", "icon": "herb", "price": 14, "heal_hp": 30, "desc": "Restaura 30 de vida."},
	"potion": {"name": "Poção de Vida", "type": "consumable", "icon": "potion_r", "price": 40, "heal_hp": 60, "desc": "Restaura 60 de vida."},
	"hi_potion": {"name": "Poção Maior", "type": "consumable", "icon": "potion_r", "price": 120, "heal_hp": 160, "desc": "Restaura 160 de vida."},
	"ether": {"name": "Éter", "type": "consumable", "icon": "potion_b", "price": 50, "heal_mp": 40, "desc": "Restaura 40 de mana."},
	"hi_ether": {"name": "Éter Maior", "type": "consumable", "icon": "potion_b", "price": 140, "heal_mp": 100, "desc": "Restaura 100 de mana."},
	"elixir": {"name": "Elixir", "type": "consumable", "icon": "elixir", "price": 420, "heal_hp": 9999, "heal_mp": 9999, "desc": "Restaura toda vida e mana."},
	"whetstone": {"name": "Pedra de Amolar", "type": "consumable", "icon": "gem", "price": 60, "buff": "atk", "desc": "+25% de dano por 60 s."},
	# materials (drops)
	"slime_gel": {"name": "Gel de Slime", "type": "material", "icon": "core", "price": 8, "desc": "Substância elástica. Usada em poções e armaduras leves."},
	"wolf_fang": {"name": "Presa de Lobo", "type": "material", "icon": "fang", "price": 18, "desc": "Afiada. Ótima para lâminas."},
	"wolf_pelt": {"name": "Pelo de Lobo", "type": "material", "icon": "cloth", "price": 22, "desc": "Pelagem espessa."},
	"bat_wing": {"name": "Asa de Morcego", "type": "material", "icon": "cloth", "price": 12, "desc": "Membrana leve."},
	"goblin_ear": {"name": "Orelha de Goblin", "type": "material", "icon": "herb", "price": 12, "desc": "Troféu repugnante."},
	"goblin_scrap": {"name": "Sucata de Goblin", "type": "material", "icon": "gem", "price": 16, "desc": "Metal retorcido, reaproveitável."},
	"old_bone": {"name": "Osso Antigo", "type": "material", "icon": "fang", "price": 14, "desc": "Resquício de um guerreiro."},
	"spore_cap": {"name": "Chapéu de Esporos", "type": "material", "icon": "herb", "price": 14, "desc": "Alquimistas adoram."},
	"iron_ore": {"name": "Minério de Ferro", "type": "material", "icon": "gem", "price": 20, "desc": "Base de toda forja."},
	"iron_ingot": {"name": "Barra de Ferro", "type": "material", "icon": "gem", "price": 45, "desc": "Ferro refinado."},
	"crystal_shard": {"name": "Fragmento de Cristal", "type": "material", "icon": "crystal", "price": 55, "desc": "Vibra com energia arcana."},
	"ember": {"name": "Brasa Eterna", "type": "material", "icon": "fire", "price": 40, "desc": "Nunca se apaga."},
	"frost_core": {"name": "Núcleo Gélido", "type": "material", "icon": "ice", "price": 48, "desc": "Frio mesmo ao sol."},
	"shadow_essence": {"name": "Essência Sombria", "type": "material", "icon": "ghost", "price": 70, "desc": "Resíduo das Sombras."},
	"alpha_fang": {"name": "Presa da Alfa", "type": "material", "icon": "fang", "price": 200, "desc": "Troféu raríssimo de Fenrisa."},
	"guardian_core": {"name": "Coração do Guardião", "type": "material", "icon": "crystal", "price": 300, "desc": "Núcleo vivo de cristal puro."},
	"king_jelly": {"name": "Geleia Real", "type": "material", "icon": "core", "price": 150, "desc": "Rara e cintilante."},
	# key items
	"aurora_pendant": {"name": "Pingente da Aurora", "type": "key", "icon": "amulet", "price": 0, "desc": "Pulsa suavemente. Pertenceu aos Guardiões."},
	"crystal_key": {"name": "Chave de Cristal", "type": "key", "icon": "key", "price": 0, "desc": "Abre o selo da Câmara Profunda."},
	"lyra_letter": {"name": "Carta da Academia", "type": "key", "icon": "scroll", "price": 0, "desc": "Selada com o brasão de Celestia."},
	"aurora_shard_1": {"name": "Cristal Menor da Aurora", "type": "key", "icon": "crystal", "price": 0, "desc": "Parte da luz que protege o mundo."},
	# skill tomes
	"tome_crescent": {"name": "Tomo: Corte Crescente", "type": "tome", "skill": "crescent", "icon": "book", "price": 180, "desc": "Ensina Corte Crescente."},
	"tome_whirlwind": {"name": "Tomo: Redemoinho", "type": "tome", "skill": "whirlwind", "icon": "book", "price": 320, "desc": "Ensina Redemoinho."},
	"tome_lunge": {"name": "Tomo: Investida Relâmpago", "type": "tome", "skill": "lunge", "icon": "book", "price": 420, "desc": "Ensina Investida Relâmpago."},
	"tome_quake": {"name": "Tomo: Golpe Sísmico", "type": "tome", "skill": "quake", "icon": "book", "price": 650, "desc": "Ensina Golpe Sísmico."},
	"tome_bladedance": {"name": "Tomo: Dança das Lâminas", "type": "tome", "skill": "bladedance", "icon": "book", "price": 1100, "desc": "Ensina Dança das Lâminas."},
	"tome_fireball": {"name": "Tomo: Bola de Fogo", "type": "tome", "skill": "fireball", "icon": "book", "price": 180, "desc": "Ensina Bola de Fogo."},
	"tome_icelance": {"name": "Tomo: Lança de Gelo", "type": "tome", "skill": "icelance", "icon": "book", "price": 340, "desc": "Ensina Lança de Gelo."},
	"tome_chainbolt": {"name": "Tomo: Raio em Cadeia", "type": "tome", "skill": "chainbolt", "icon": "book", "price": 520, "desc": "Ensina Raio em Cadeia."},
	"tome_frostnova": {"name": "Tomo: Nova Glacial", "type": "tome", "skill": "frostnova", "icon": "book", "price": 800, "desc": "Ensina Nova Glacial."},
	"tome_meteor": {"name": "Tomo: Meteoro", "type": "tome", "skill": "meteor", "icon": "book", "price": 1400, "desc": "Ensina Meteoro."},
	"tome_heal": {"name": "Tomo: Luz Restauradora", "type": "tome", "skill": "heal", "icon": "book", "price": 180, "desc": "Ensina Luz Restauradora."},
	"tome_barrier": {"name": "Tomo: Escudo Etéreo", "type": "tome", "skill": "barrier", "icon": "book", "price": 380, "desc": "Ensina Escudo Etéreo."},
	"tome_fury": {"name": "Tomo: Aura de Fúria", "type": "tome", "skill": "fury", "icon": "book", "price": 600, "desc": "Ensina Aura de Fúria."},
	"tome_phantom": {"name": "Tomo: Passo Fantasma", "type": "tome", "skill": "phantom", "icon": "book", "price": 760, "desc": "Ensina Passo Fantasma."},
	"tome_guardians": {"name": "Tomo: Espíritos Guardiões", "type": "tome", "skill": "guardians", "icon": "book", "price": 1300, "desc": "Ensina Espíritos Guardiões."},
}

# ----------------------------------------------------------------------------- equipment bases
# stats are base values at Comum rarity.
const GEAR := {
	"rusty_sword": {"name": "Espada Enferrujada", "slot": "weapon", "icon": "sword", "tier": 0, "price": 10, "stats": {"atk": 4}},
	"iron_sword": {"name": "Espada de Ferro", "slot": "weapon", "icon": "sword", "tier": 1, "price": 160, "stats": {"atk": 9}},
	"hunter_blade": {"name": "Lâmina do Caçador", "slot": "weapon", "icon": "blades", "tier": 2, "price": 340, "stats": {"atk": 14, "crit": 4}},
	"fang_blade": {"name": "Lâmina Presa-de-Lobo", "slot": "weapon", "icon": "blades", "tier": 2, "price": 0, "stats": {"atk": 16, "crit": 6, "spd": 4}},
	"steel_sword": {"name": "Espada de Aço", "slot": "weapon", "icon": "sword", "tier": 3, "price": 640, "stats": {"atk": 22}},
	"crystal_edge": {"name": "Gume de Cristal", "slot": "weapon", "icon": "sword", "tier": 3, "price": 0, "stats": {"atk": 24, "mag": 10}},
	"apprentice_staff": {"name": "Cajado de Aprendiz", "slot": "weapon", "icon": "staff", "tier": 1, "price": 170, "stats": {"atk": 2, "mag": 11}},
	"mage_staff": {"name": "Cajado Arcano", "slot": "weapon", "icon": "staff", "tier": 2, "price": 420, "stats": {"atk": 3, "mag": 19, "mp": 20}},
	"linen_tunic": {"name": "Túnica de Linho", "slot": "armor", "icon": "robe", "tier": 0, "price": 20, "stats": {"def": 2}},
	"leather_armor": {"name": "Couro Reforçado", "slot": "armor", "icon": "armor", "tier": 1, "price": 140, "stats": {"def": 6, "hp": 10}},
	"mage_robe": {"name": "Manto Arcano", "slot": "armor", "icon": "robe", "tier": 1, "price": 190, "stats": {"def": 3, "mag": 6, "mp": 20}},
	"chain_mail": {"name": "Cota de Malha", "slot": "armor", "icon": "armor", "tier": 2, "price": 360, "stats": {"def": 11, "hp": 20}},
	"wolf_cloak": {"name": "Manto de Lobo", "slot": "armor", "icon": "robe", "tier": 2, "price": 0, "stats": {"def": 9, "hp": 18, "spd": 4}},
	"crystal_mail": {"name": "Armadura de Cristal", "slot": "armor", "icon": "armor", "tier": 3, "price": 0, "stats": {"def": 16, "hp": 30, "mp": 12}},
	"lucky_charm": {"name": "Amuleto da Sorte", "slot": "acc", "icon": "amulet", "tier": 1, "price": 200, "stats": {"crit": 5}},
	"vigor_ring": {"name": "Anel de Vigor", "slot": "acc", "icon": "ring", "tier": 1, "price": 220, "stats": {"hp": 40}},
	"mana_pendant": {"name": "Pingente de Mana", "slot": "acc", "icon": "amulet", "tier": 1, "price": 220, "stats": {"mp": 30}},
	"swift_boots": {"name": "Botas Ligeiras", "slot": "acc", "icon": "boots", "tier": 2, "price": 260, "stats": {"spd": 8}},
	"guardian_sigil": {"name": "Selo do Guardião", "slot": "acc", "icon": "star", "tier": 3, "price": 0, "stats": {"def": 4, "mp": 10, "hp": 20}},
}

# random modifiers rolled on drops (value ranges per tier multiplier)
const MODS := {
	"atk": {"label": "Ataque", "min": 1, "max": 3, "pct": false},
	"mag": {"label": "Magia", "min": 1, "max": 3, "pct": false},
	"def": {"label": "Defesa", "min": 1, "max": 3, "pct": false},
	"hp": {"label": "Vida", "min": 6, "max": 14, "pct": false},
	"mp": {"label": "Mana", "min": 5, "max": 12, "pct": false},
	"crit": {"label": "Crítico", "min": 2, "max": 4, "pct": true},
	"spd": {"label": "Velocidade", "min": 2, "max": 4, "pct": true},
	"lifesteal": {"label": "Roubo de vida", "min": 1, "max": 3, "pct": true},
	"fire": {"label": "Dano de fogo", "min": 3, "max": 6, "pct": true},
	"stamina": {"label": "Vigor", "min": 6, "max": 12, "pct": false},
}

# crafting recipes at the blacksmith / alchemist
const RECIPES := [
	{"id": "r_fang_blade", "result": "fang_blade", "mats": {"wolf_fang": 6, "iron_ingot": 2}, "gold": 120, "rarity": 1},
	{"id": "r_wolf_cloak", "result": "wolf_cloak", "mats": {"wolf_pelt": 6, "wolf_fang": 2}, "gold": 140, "rarity": 1},
	{"id": "r_iron_ingot", "result": "iron_ingot", "mats": {"iron_ore": 3}, "gold": 10, "item": true, "count": 1},
	{"id": "r_hunter", "result": "hunter_blade", "mats": {"iron_ingot": 3, "goblin_scrap": 4, "bat_wing": 3}, "gold": 160, "rarity": 1},
	{"id": "r_leather", "result": "leather_armor", "mats": {"wolf_pelt": 3, "slime_gel": 4}, "gold": 60, "rarity": 1},
	{"id": "r_crystal_edge", "result": "crystal_edge", "mats": {"crystal_shard": 8, "iron_ingot": 4, "guardian_core": 1}, "gold": 400, "rarity": 2},
	{"id": "r_crystal_mail", "result": "crystal_mail", "mats": {"crystal_shard": 10, "iron_ingot": 5, "guardian_core": 1}, "gold": 450, "rarity": 2},
	{"id": "r_potion", "result": "potion", "mats": {"herb": 2, "slime_gel": 1}, "gold": 8, "item": true, "count": 2},
	{"id": "r_hi_potion", "result": "hi_potion", "mats": {"potion": 2, "king_jelly": 1}, "gold": 40, "item": true, "count": 1},
	{"id": "r_ether", "result": "ether", "mats": {"spore_cap": 2, "crystal_shard": 1}, "gold": 12, "item": true, "count": 2},
]

# ----------------------------------------------------------------------------- skills
# tree: blade | arcane | spirit. scale: atk | mag. Visual tiers: rank 1-2 / 3-4 / 5.
const SKILLS := {
	"crescent": {"name": "Corte Crescente", "tree": "blade", "kind": "wave", "elem": "phys", "icon": "slash", "req": 1, "mp": 6, "cd": 1.4, "power": 1.5, "scale": "atk", "desc": "Lança uma onda cortante que atravessa inimigos."},
	"whirlwind": {"name": "Redemoinho", "tree": "blade", "kind": "whirl", "elem": "phys", "icon": "whirl", "req": 3, "mp": 12, "cd": 4.0, "power": 1.7, "range": 50.0, "scale": "atk", "desc": "Gira a lâmina em tornado cortante ao redor."},
	"lunge": {"name": "Investida Relâmpago", "tree": "blade", "kind": "dash", "elem": "phys", "icon": "dash", "req": 5, "mp": 10, "cd": 3.5, "power": 2.0, "range": 110.0, "scale": "atk", "desc": "Avança num lampejo cortando tudo."},
	"quake": {"name": "Golpe Sísmico", "tree": "blade", "kind": "slam", "elem": "phys", "icon": "slam", "req": 8, "mp": 18, "cd": 7.0, "power": 2.4, "range": 64.0, "scale": "atk", "desc": "Esmaga o chão: dano em área e atordoamento."},
	"bladedance": {"name": "Dança das Lâminas", "tree": "blade", "kind": "multi", "elem": "phys", "icon": "blades", "req": 12, "mp": 26, "cd": 10.0, "power": 0.9, "range": 90.0, "scale": "atk", "desc": "Sequência vertiginosa de cortes no alvo."},
	"fireball": {"name": "Bola de Fogo", "tree": "arcane", "kind": "bolt", "elem": "fire", "icon": "fire", "req": 1, "mp": 8, "cd": 1.3, "power": 1.6, "scale": "mag", "desc": "Esfera flamejante que explode e queima."},
	"icelance": {"name": "Lança de Gelo", "tree": "arcane", "kind": "lance", "elem": "ice", "icon": "ice", "req": 4, "mp": 9, "cd": 2.0, "power": 1.7, "scale": "mag", "desc": "Estaca de gelo veloz que reduz a velocidade."},
	"chainbolt": {"name": "Raio em Cadeia", "tree": "arcane", "kind": "chain", "elem": "bolt", "icon": "bolt", "req": 7, "mp": 16, "cd": 4.0, "power": 1.5, "range": 150.0, "scale": "mag", "desc": "Raio que salta entre inimigos."},
	"frostnova": {"name": "Nova Glacial", "tree": "arcane", "kind": "nova", "elem": "ice", "icon": "nova", "req": 10, "mp": 24, "cd": 9.0, "power": 1.9, "range": 78.0, "scale": "mag", "desc": "Explosão de gelo que congela ao redor."},
	"meteor": {"name": "Meteoro", "tree": "arcane", "kind": "meteor", "elem": "fire", "icon": "meteor", "req": 15, "mp": 40, "cd": 14.0, "power": 4.2, "range": 72.0, "scale": "mag", "desc": "Invoca um meteoro devastador."},
	"heal": {"name": "Luz Restauradora", "tree": "spirit", "kind": "heal", "elem": "holy", "icon": "heal", "req": 1, "mp": 14, "cd": 6.0, "power": 1.8, "scale": "mag", "desc": "Cura com luz sagrada."},
	"barrier": {"name": "Escudo Etéreo", "tree": "spirit", "kind": "shield", "elem": "holy", "icon": "shield", "req": 6, "mp": 18, "cd": 12.0, "power": 2.2, "scale": "mag", "desc": "Barreira que absorve dano."},
	"fury": {"name": "Aura de Fúria", "tree": "spirit", "kind": "buff", "elem": "fire", "icon": "rage", "req": 9, "mp": 20, "cd": 25.0, "power": 0.25, "scale": "mag", "desc": "Aumenta o dano por 12 s."},
	"phantom": {"name": "Passo Fantasma", "tree": "spirit", "kind": "phase", "elem": "dark", "icon": "ghost", "req": 11, "mp": 14, "cd": 8.0, "power": 0.0, "range": 130.0, "scale": "mag", "desc": "Teleporta e fica intangível."},
	"guardians": {"name": "Espíritos Guardiões", "tree": "spirit", "kind": "summon", "elem": "holy", "icon": "spirit", "req": 14, "mp": 32, "cd": 20.0, "power": 0.9, "scale": "mag", "desc": "Espíritos que orbitam e ferem."},
}
const TREE_NAMES := {"blade": "Lâmina", "arcane": "Arcano", "spirit": "Espírito"}
const START_SKILL := {"blade": "crescent", "arcane": "fireball", "spirit": "heal"}

static func skill_power(id: String, rank: int) -> float:
	return float(SKILLS[id]["power"]) * (1.0 + 0.22 * (rank - 1))
static func skill_cost(id: String, rank: int) -> int:
	return roundi(float(SKILLS[id]["mp"]) * (1.0 + 0.06 * (rank - 1)))
static func skill_cd(id: String, rank: int) -> float:
	return maxf(0.6, float(SKILLS[id]["cd"]) * (1.0 - 0.05 * (rank - 1)))
static func skill_tier(rank: int) -> int:
	return 1 if rank <= 2 else (2 if rank <= 4 else 3)

# ----------------------------------------------------------------------------- enemies
# dmg is the raw base damage of its main attack at "normal" difficulty.
const ENEMIES := {
	"slime": {"name": "Slime Verde", "sheet": "slime_green", "level": 1, "hp": 38, "dmg": 11, "def": 0, "spd": 52.0, "xp": 9, "gold": [2, 7], "ai": "hop", "r": 10, "h": 14, "weak": ["fire"],
		"loot": [{"id": "slime_gel", "p": 0.65}, {"id": "herb", "p": 0.12}]},
	"slime_blue": {"name": "Slime Gélido", "sheet": "slime_blue", "level": 3, "hp": 70, "dmg": 17, "def": 2, "spd": 56.0, "xp": 20, "gold": [5, 12], "ai": "hop", "r": 10, "h": 14, "weak": ["fire"], "resist": ["ice"],
		"loot": [{"id": "slime_gel", "p": 0.7}, {"id": "frost_core", "p": 0.12}, {"id": "potion", "p": 0.08}]},
	"slime_red": {"name": "Slime Rubro", "sheet": "slime_red", "level": 5, "hp": 110, "dmg": 24, "def": 3, "spd": 62.0, "xp": 34, "gold": [8, 18], "ai": "hop", "r": 10, "h": 14, "weak": ["ice"], "resist": ["fire"],
		"loot": [{"id": "slime_gel", "p": 0.7}, {"id": "ember", "p": 0.16}, {"id": "tome_fireball", "p": 0.015}]},
	"bat": {"name": "Morcego Sombrio", "sheet": "bat", "level": 2, "hp": 28, "dmg": 12, "def": 0, "spd": 86.0, "xp": 12, "gold": [3, 9], "ai": "bat", "r": 9, "h": 26, "fly": true, "weak": ["bolt"],
		"loot": [{"id": "bat_wing", "p": 0.45}, {"id": "herb", "p": 0.08}]},
	"bat_fire": {"name": "Morcego Ígneo", "sheet": "bat_fire", "level": 6, "hp": 62, "dmg": 24, "def": 1, "spd": 98.0, "xp": 30, "gold": [7, 16], "ai": "bat", "r": 9, "h": 26, "fly": true, "weak": ["ice"], "resist": ["fire"],
		"loot": [{"id": "bat_wing", "p": 0.45}, {"id": "ember", "p": 0.14}]},
	"wolf": {"name": "Lobo Cinzento", "sheet": "wolf", "level": 4, "hp": 86, "dmg": 20, "def": 2, "spd": 78.0, "xp": 28, "gold": [6, 14], "ai": "pounce", "r": 13, "h": 14, "weak": ["fire"],
		"loot": [{"id": "wolf_fang", "p": 0.5}, {"id": "wolf_pelt", "p": 0.45}]},
	"wolf_dark": {"name": "Lobo da Sombra", "sheet": "wolf_dark", "level": 7, "hp": 150, "dmg": 30, "def": 4, "spd": 92.0, "xp": 52, "gold": [10, 22], "ai": "pounce", "r": 13, "h": 14, "weak": ["holy", "fire"],
		"loot": [{"id": "wolf_fang", "p": 0.55}, {"id": "wolf_pelt", "p": 0.5}, {"id": "shadow_essence", "p": 0.14}, {"id": "potion", "p": 0.12}]},
}

static func enemy(id: String) -> Dictionary:
	return ENEMIES[id]
