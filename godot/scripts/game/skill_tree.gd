class_name SkillTree
extends RefCounted
## Attributes (Força, Constituição, Mana, Inteligência, Agilidade, Sorte) and one 3-branch skill tree per hero class.
## Every level grants ATTR_PER_LEVEL attribute points and 1 skill point; tree tiers unlock with the hero's level.

const ATTR_PER_LEVEL := 3
const TIER_LEVELS := [2, 5, 9, 14]
const TIER_COST := [1, 2, 2, 3]

const ATTRS := ["str", "con", "man", "int", "agi", "sor"]
const ATTR_NAMES := {"str": "Força", "con": "Constituição", "man": "Mana", "int": "Inteligência", "agi": "Agilidade", "sor": "Sorte"}
const ATTR_ABBR := {"str": "FOR", "con": "CON", "man": "MAN", "int": "INT", "agi": "AGI", "sor": "SOR"}
const ATTR_DESC := {
	"str": "+1,6 ataque físico",
	"con": "+1,2 defesa · +7 vida",
	"man": "+5 mana máxima",
	"int": "+1,6 magia · regen. mana",
	"agi": "esquiva · velocidade",
	"sor": "crítico · itens raros",
}

# starting attributes per class (bonuses count only the points invested above these)
const BASE := {
	"warrior": {"str": 14, "con": 12, "man": 5, "int": 4, "agi": 6, "sor": 5},
	"mage": {"str": 3, "con": 5, "man": 14, "int": 15, "agi": 6, "sor": 6},
	"archer": {"str": 8, "con": 7, "man": 7, "int": 6, "agi": 14, "sor": 8},
	"paladin": {"str": 11, "con": 14, "man": 8, "int": 9, "agi": 4, "sor": 4},
	"assassin": {"str": 10, "con": 5, "man": 5, "int": 5, "agi": 15, "sor": 10},
	"summoner": {"str": 3, "con": 6, "man": 12, "int": 13, "agi": 6, "sor": 8},
}

const EFF_TEXT := {
	"atk_pct": ["ataque", "%"], "mag_pct": ["poder mágico", "%"], "def": ["defesa", ""], "hp": ["vida máxima", ""], "mp": ["mana máxima", ""],
	"regen": ["mana/s", ""], "crit": ["crítico", "%"], "dodge": ["esquiva", "%"], "aspd": ["vel. de ataque", "%"], "mspd": ["vel. de movimento", "%"],
	"lifesteal": ["roubo de vida", "%"], "cdr": ["recarga menor", "%"], "xp_pct": ["EXP", "%"], "dmg_red": ["dano recebido", "%"], "heal_pct": ["cura de poções", "%"],
}
const PERCENT := ["atk_pct", "mag_pct", "crit", "dodge", "aspd", "mspd", "lifesteal", "cdr", "xp_pct", "dmg_red", "heal_pct"]

# 10 active skills per class in 3 branches (4 + 3 + 3). Each skill is cast from one of 4 slots (R F G V) and also grants a small
# passive bonus once learned. Skill: n name, mp, cd, k kind (nova / meteor / storm / volley / dash / summon / none), p params, pas passive, i icon, c colour.
# Params: r radius (tiles) · m damage multiplier · s stat (atk/mag/mix) · kb knock-back · at "t" = centred on the target · twice · heal (fraction of max HP) ·
#         shield (seconds invulnerable) · buff {id, t, eff} · summon n · volley n/arc/waves · dash dist (tiles, negative = backwards).
const SLOTS := ["r", "f", "g", "v"]
const LAYOUT := [4, 3, 3]

const TREES := {
	"warrior": [
		{"name": "Fúria", "icon": "skill_sword", "nodes": [
			{"n": "Golpe Rachante", "mp": 10, "cd": 6, "k": "nova", "p": {"r": 2.4, "m": 1.9, "s": "atk", "kb": 9}, "pas": {"atk_pct": 4}, "i": "skill_sword", "c": Color(1.0, 0.6, 0.3)},
			{"n": "Grito de Guerra", "mp": 15, "cd": 18, "k": "none", "p": {"buff": {"id": "grito", "t": 10, "eff": {"atk_pct": 35}}}, "pas": {"crit": 2}, "i": "skill_sword", "c": Color(1.0, 0.6, 0.3)},
			{"n": "Redemoinho", "mp": 22, "cd": 10, "k": "nova", "p": {"r": 3.0, "m": 2.7, "s": "atk", "kb": 13, "twice": true}, "pas": {"atk_pct": 6}, "i": "skill_sword", "c": Color(1.0, 0.75, 0.4)},
			{"n": "Execução Brutal", "mp": 30, "cd": 16, "k": "nova", "p": {"r": 2.0, "m": 5.5, "s": "atk", "kb": 16, "at": "t", "rng": 3.2}, "pas": {"atk_pct": 10, "crit": 4}, "i": "skill_sword", "c": Color(1.0, 0.4, 0.4)},
		]},
		{"name": "Muralha", "icon": "gear_armor", "nodes": [
			{"n": "Postura de Ferro", "mp": 12, "cd": 16, "k": "none", "p": {"buff": {"id": "postura", "t": 8, "eff": {"def": 12, "dmg_red": 15}}}, "pas": {"def": 3, "hp": 15}, "i": "gear_armor", "c": Color(0.95, 0.95, 1.0)},
			{"n": "Investida", "mp": 14, "cd": 9, "k": "dash", "p": {"dist": 5, "r": 2.2, "m": 2.2, "s": "atk"}, "pas": {"mspd": 3}, "i": "skill_roll", "c": Color(1.0, 0.6, 0.3)},
			{"n": "Bastião Inabalável", "mp": 28, "cd": 28, "k": "none", "p": {"shield": 3, "heal": 0.1}, "pas": {"hp": 40}, "i": "gear_armor", "c": Color(1.0, 0.9, 0.5)},
		]},
		{"name": "Tremor", "icon": "skill_roll", "nodes": [
			{"n": "Pisão", "mp": 8, "cd": 5, "k": "nova", "p": {"r": 2.4, "m": 1.6, "s": "atk", "kb": 14}, "pas": {"aspd": 3}, "i": "skill_roll", "c": Color(0.85, 0.7, 0.45)},
			{"n": "Terremoto", "mp": 20, "cd": 11, "k": "nova", "p": {"r": 3.4, "m": 2.4, "s": "atk", "kb": 11}, "pas": {"aspd": 3}, "i": "skill_roll", "c": Color(0.85, 0.7, 0.45)},
			{"n": "Fúria Berserker", "mp": 24, "cd": 30, "k": "none", "p": {"buff": {"id": "berserk", "t": 10, "eff": {"atk_pct": 30, "aspd": 30, "lifesteal": 10}}}, "pas": {"lifesteal": 3}, "i": "skill_sword", "c": Color(1.0, 0.4, 0.4)},
		]},
	],
	"mage": [
		{"name": "Piromancia", "icon": "skill_spark", "nodes": [
			{"n": "Bola de Fogo", "mp": 14, "cd": 5, "k": "nova", "p": {"r": 1.9, "m": 2.3, "s": "mag", "kb": 7, "at": "t", "rng": 9}, "pas": {"mag_pct": 4}, "i": "skill_spark", "c": Color(1.0, 0.55, 0.25)},
			{"n": "Chuva de Meteoros", "mp": 38, "cd": 11, "k": "meteor", "p": {"m": 1.0}, "pas": {"mag_pct": 3}, "i": "skill_spark", "c": Color(1.0, 0.55, 0.25)},
			{"n": "Muralha de Chamas", "mp": 26, "cd": 12, "k": "nova", "p": {"r": 3.2, "m": 2.1, "s": "mag", "kb": 6, "twice": true}, "pas": {"crit": 3}, "i": "skill_spark", "c": Color(1.0, 0.4, 0.2)},
			{"n": "Apocalipse", "mp": 60, "cd": 28, "k": "meteor", "p": {"m": 1.6, "extra": {"r": 4.5, "m": 3.0, "s": "mag", "kb": 14}}, "pas": {"mag_pct": 12, "cdr": 6}, "i": "skill_spark", "c": Color(1.0, 0.4, 0.4)},
		]},
		{"name": "Tempestade", "icon": "skill_spark", "nodes": [
			{"n": "Raio em Cadeia", "mp": 16, "cd": 6, "k": "nova", "p": {"r": 2.5, "m": 2.7, "s": "mag", "kb": 4, "at": "t", "rng": 9}, "pas": {"regen": 0.4, "mp": 10}, "i": "skill_spark", "c": Color(0.55, 0.8, 1.0)},
			{"n": "Tempestade de Raios", "mp": 30, "cd": 9, "k": "storm", "p": {"m": 1.0}, "pas": {"regen": 0.4}, "i": "skill_spark", "c": Color(0.55, 0.8, 1.0)},
			{"n": "Nova Gélida", "mp": 24, "cd": 13, "k": "nova", "p": {"r": 3.7, "m": 2.3, "s": "mag", "kb": 4}, "pas": {"cdr": 6}, "i": "skill_spark", "c": Color(0.6, 0.85, 1.0)},
		]},
		{"name": "Sabedoria", "icon": "tome", "nodes": [
			{"n": "Escudo Arcano", "mp": 20, "cd": 24, "k": "none", "p": {"shield": 3}, "pas": {"def": 3, "hp": 15}, "i": "tome", "c": Color(0.95, 0.95, 1.0)},
			{"n": "Meditação", "mp": 0, "cd": 30, "k": "none", "p": {"buff": {"id": "medita", "t": 8, "eff": {"regen": 6}}}, "pas": {"mp": 15}, "i": "tome", "c": Color(0.55, 0.95, 0.9)},
			{"n": "Pulso Arcano", "mp": 30, "cd": 16, "k": "nova", "p": {"r": 5.0, "m": 1.9, "s": "mag", "kb": 16}, "pas": {"mag_pct": 6, "mp": 25}, "i": "tome", "c": Color(0.7, 0.6, 1.0)},
		]},
	],
	"archer": [
		{"name": "Precisão", "icon": "skill_roll", "nodes": [
			{"n": "Tiro Perfurante", "mp": 10, "cd": 5, "k": "volley", "p": {"n": 3, "arc": 14, "m": 1.6}, "pas": {"atk_pct": 4}, "i": "skill_roll", "c": Color(0.7, 1.0, 0.6)},
			{"n": "Foco Mortal", "mp": 15, "cd": 20, "k": "none", "p": {"buff": {"id": "foco", "t": 8, "eff": {"crit": 40, "aspd": 30}}}, "pas": {"crit": 3}, "i": "skill_roll", "c": Color(0.7, 1.0, 0.6)},
			{"n": "Tiro Explosivo", "mp": 22, "cd": 10, "k": "nova", "p": {"r": 2.2, "m": 3.3, "s": "atk", "kb": 10, "at": "t", "rng": 9}, "pas": {"crit": 4, "atk_pct": 4}, "i": "skill_roll", "c": Color(1.0, 0.55, 0.25)},
			{"n": "Tiro de Mestre", "mp": 34, "cd": 18, "k": "volley", "p": {"n": 1, "arc": 0, "m": 6.5}, "pas": {"atk_pct": 12, "crit": 6}, "i": "skill_roll", "c": Color(1.0, 0.9, 0.5)},
		]},
		{"name": "Chuva", "icon": "skill_roll", "nodes": [
			{"n": "Leque de Flechas", "mp": 12, "cd": 7, "k": "volley", "p": {"n": 7, "arc": 70, "m": 1.0}, "pas": {"aspd": 4}, "i": "skill_roll", "c": Color(0.7, 1.0, 0.6)},
			{"n": "Salva Total", "mp": 22, "cd": 10, "k": "volley", "p": {"n": 12, "arc": 360, "m": 0.9}, "pas": {"aspd": 4}, "i": "skill_roll", "c": Color(0.7, 1.0, 0.6)},
			{"n": "Tempestade de Flechas", "mp": 40, "cd": 24, "k": "volley", "p": {"n": 20, "arc": 360, "m": 0.9, "waves": 2}, "pas": {"atk_pct": 10, "cdr": 10}, "i": "skill_roll", "c": Color(0.5, 1.0, 0.7)},
		]},
		{"name": "Caçador", "icon": "gear_charm", "nodes": [
			{"n": "Salto Evasivo", "mp": 8, "cd": 6, "k": "dash", "p": {"dist": -4, "r": 0, "m": 0, "s": "atk"}, "pas": {"mspd": 5, "dodge": 2}, "i": "gear_charm", "c": Color(0.95, 0.95, 1.0)},
			{"n": "Armadilha", "mp": 16, "cd": 12, "k": "nova", "p": {"r": 2.7, "m": 2.4, "s": "atk", "kb": 6, "at": "t", "rng": 7}, "pas": {"dodge": 3, "hp": 20}, "i": "gear_charm", "c": Color(0.85, 0.7, 0.45)},
			{"n": "Instinto Predador", "mp": 20, "cd": 26, "k": "none", "p": {"buff": {"id": "predador", "t": 8, "eff": {"mspd": 25, "dodge": 15, "aspd": 15}}}, "pas": {"xp_pct": 10, "dodge": 4}, "i": "gear_charm", "c": Color(0.7, 1.0, 0.6)},
		]},
	],
	"paladin": [
		{"name": "Luz", "icon": "skill_spark", "nodes": [
			{"n": "Golpe Sagrado", "mp": 10, "cd": 6, "k": "nova", "p": {"r": 2.4, "m": 2.0, "s": "mix", "kb": 8}, "pas": {"atk_pct": 3, "mag_pct": 3}, "i": "skill_spark", "c": Color(1.0, 0.9, 0.5)},
			{"n": "Julgamento Divino", "mp": 30, "cd": 14, "k": "nova", "p": {"r": 3.8, "m": 1.5, "s": "mix", "kb": 8, "heal": 0.15}, "pas": {"mag_pct": 3}, "i": "skill_spark", "c": Color(1.0, 0.9, 0.5)},
			{"n": "Martelo da Justiça", "mp": 28, "cd": 14, "k": "nova", "p": {"r": 2.2, "m": 4.6, "s": "mix", "kb": 15, "at": "t", "rng": 3.2}, "pas": {"atk_pct": 8, "mag_pct": 6}, "i": "skill_sword", "c": Color(0.95, 0.95, 1.0)},
			{"n": "Avatar da Luz", "mp": 40, "cd": 34, "k": "none", "p": {"buff": {"id": "avatar", "t": 12, "eff": {"atk_pct": 25, "mag_pct": 25, "dmg_red": 15}}}, "pas": {"atk_pct": 10, "mag_pct": 10}, "i": "skill_spark", "c": Color(1.0, 0.9, 0.5)},
		]},
		{"name": "Bastião", "icon": "gear_armor", "nodes": [
			{"n": "Armadura Bendita", "mp": 12, "cd": 15, "k": "none", "p": {"buff": {"id": "armadura", "t": 8, "eff": {"def": 10}}}, "pas": {"def": 5, "hp": 25}, "i": "gear_armor", "c": Color(0.95, 0.95, 1.0)},
			{"n": "Escudo Sagrado", "mp": 25, "cd": 25, "k": "none", "p": {"shield": 3}, "pas": {"def": 3}, "i": "gear_armor", "c": Color(1.0, 0.9, 0.5)},
			{"n": "Guardião de Aetheria", "mp": 30, "cd": 24, "k": "nova", "p": {"r": 3.6, "m": 1.2, "s": "mix", "kb": 14, "buff": {"id": "guardiao", "t": 10, "eff": {"dmg_red": 10}}}, "pas": {"dmg_red": 6, "hp": 30}, "i": "gear_armor", "c": Color(0.95, 0.95, 1.0)},
		]},
		{"name": "Redenção", "icon": "potion", "nodes": [
			{"n": "Mãos Curativas", "mp": 22, "cd": 14, "k": "none", "p": {"heal": 0.25}, "pas": {"heal_pct": 15, "regen": 0.4}, "i": "potion", "c": Color(0.7, 1.0, 0.6)},
			{"n": "Bênção", "mp": 18, "cd": 25, "k": "none", "p": {"heal": 0.1, "buff": {"id": "bencao", "t": 12, "eff": {"regen": 3, "crit": 10}}}, "pas": {"hp": 30, "mp": 12}, "i": "potion", "c": Color(1.0, 0.9, 0.5)},
			{"n": "Milagre", "mp": 50, "cd": 60, "k": "none", "p": {"heal": 0.6, "shield": 1.5}, "pas": {"lifesteal": 3, "heal_pct": 15}, "i": "potion", "c": Color(1.0, 1.0, 0.8)},
		]},
	],
	"assassin": [
		{"name": "Lâminas", "icon": "skill_sword", "nodes": [
			{"n": "Corte Preciso", "mp": 8, "cd": 4, "k": "nova", "p": {"r": 2.1, "m": 2.4, "s": "atk", "kb": 5}, "pas": {"atk_pct": 6, "crit": 2}, "i": "skill_sword", "c": Color(0.7, 0.6, 1.0)},
			{"n": "Dança das Lâminas", "mp": 18, "cd": 9, "k": "nova", "p": {"r": 2.5, "m": 2.2, "s": "atk", "kb": 6, "twice": true}, "pas": {"aspd": 4}, "i": "skill_sword", "c": Color(0.7, 0.6, 1.0)},
			{"n": "Veneno Letal", "mp": 18, "cd": 9, "k": "nova", "p": {"r": 2.8, "m": 2.4, "s": "atk", "kb": 4, "buff": {"id": "veneno", "t": 6, "eff": {"atk_pct": 12}}}, "pas": {"atk_pct": 8, "crit": 4}, "i": "skill_sword", "c": Color(0.7, 1.0, 0.6)},
			{"n": "Execução", "mp": 32, "cd": 18, "k": "nova", "p": {"r": 1.9, "m": 7.0, "s": "atk", "kb": 14, "at": "t", "rng": 3.2}, "pas": {"atk_pct": 12, "crit": 8}, "i": "skill_sword", "c": Color(1.0, 0.4, 0.4)},
		]},
		{"name": "Sombras", "icon": "skill_roll", "nodes": [
			{"n": "Passo Sombrio", "mp": 10, "cd": 6, "k": "dash", "p": {"dist": 4, "r": 1.9, "m": 1.5, "s": "atk"}, "pas": {"dodge": 3, "mspd": 4}, "i": "skill_roll", "c": Color(0.7, 0.6, 1.0)},
			{"n": "Véu das Sombras", "mp": 15, "cd": 18, "k": "none", "p": {"buff": {"id": "veu", "t": 6, "eff": {"dodge": 50, "mspd": 30}}}, "pas": {"dodge": 3}, "i": "skill_roll", "c": Color(0.7, 0.6, 1.0)},
			{"n": "Sombra Eterna", "mp": 30, "cd": 32, "k": "none", "p": {"buff": {"id": "sombra", "t": 10, "eff": {"dodge": 40, "crit": 30, "aspd": 30}}}, "pas": {"dodge": 8, "mspd": 8}, "i": "skill_roll", "c": Color(0.5, 0.4, 0.9)},
		]},
		{"name": "Ladrão", "icon": "coin", "nodes": [
			{"n": "Bomba de Fumaça", "mp": 12, "cd": 12, "k": "nova", "p": {"r": 3.0, "m": 0.6, "s": "atk", "kb": 16, "buff": {"id": "fumaca", "t": 4, "eff": {"dodge": 25}}}, "pas": {"xp_pct": 5, "aspd": 3}, "i": "coin", "c": Color(0.95, 0.95, 1.0)},
			{"n": "Roubo Vital", "mp": 18, "cd": 12, "k": "nova", "p": {"r": 2.5, "m": 2.0, "s": "atk", "kb": 5, "heal": 0.12}, "pas": {"lifesteal": 4, "crit": 3}, "i": "coin", "c": Color(1.0, 0.4, 0.4)},
			{"n": "Mercador de Mortes", "mp": 20, "cd": 24, "k": "none", "p": {"buff": {"id": "mercador", "t": 8, "eff": {"lifesteal": 15, "crit": 20}}}, "pas": {"lifesteal": 6, "cdr": 10}, "i": "coin", "c": Color(1.0, 0.9, 0.5)},
		]},
	],
	"summoner": [
		{"name": "Espíritos", "icon": "skill_spark", "nodes": [
			{"n": "Chamar Familiares", "mp": 24, "cd": 20, "k": "summon", "p": {"n": 2}, "pas": {"mag_pct": 6}, "i": "skill_spark", "c": Color(0.55, 0.95, 0.9)},
			{"n": "Explosão Espiritual", "mp": 28, "cd": 12, "k": "nova", "p": {"r": 3.6, "m": 2.6, "s": "mag", "kb": 7}, "pas": {"mag_pct": 3}, "i": "skill_spark", "c": Color(0.55, 0.95, 0.9)},
			{"n": "Legião Espectral", "mp": 34, "cd": 18, "k": "nova", "p": {"r": 4.0, "m": 2.3, "s": "mag", "kb": 8, "summon": 1}, "pas": {"mag_pct": 8, "cdr": 6}, "i": "skill_spark", "c": Color(0.6, 1.0, 0.95)},
			{"n": "Senhor dos Espíritos", "mp": 55, "cd": 32, "k": "nova", "p": {"r": 5.0, "m": 3.2, "s": "mag", "kb": 14, "buff": {"id": "senhor", "t": 12, "eff": {"mag_pct": 40, "regen": 3}}}, "pas": {"mag_pct": 14, "cdr": 8}, "i": "skill_spark", "c": Color(0.95, 0.95, 1.0)},
		]},
		{"name": "Vínculo", "icon": "potion", "nodes": [
			{"n": "Aura Protetora", "mp": 14, "cd": 18, "k": "none", "p": {"buff": {"id": "aura", "t": 10, "eff": {"def": 8, "dmg_red": 10}}}, "pas": {"def": 3, "hp": 20}, "i": "potion", "c": Color(0.55, 0.95, 0.9)},
			{"n": "Vínculo Espiritual", "mp": 20, "cd": 24, "k": "none", "p": {"heal": 0.25, "buff": {"id": "vinculo", "t": 10, "eff": {"mag_pct": 30, "regen": 2}}}, "pas": {"regen": 0.4}, "i": "potion", "c": Color(0.55, 0.95, 0.9)},
			{"n": "Alma Gêmea", "mp": 40, "cd": 45, "k": "none", "p": {"heal": 0.4, "shield": 2}, "pas": {"dmg_red": 8, "hp": 40}, "i": "potion", "c": Color(1.0, 0.9, 0.5)},
		]},
		{"name": "Mente", "icon": "tome", "nodes": [
			{"n": "Foco Calmo", "mp": 0, "cd": 25, "k": "none", "p": {"buff": {"id": "calmo", "t": 8, "eff": {"regen": 5}}}, "pas": {"mp": 15, "regen": 0.5}, "i": "tome", "c": Color(0.95, 0.95, 1.0)},
			{"n": "Raio Espiritual", "mp": 16, "cd": 6, "k": "nova", "p": {"r": 1.9, "m": 3.1, "s": "mag", "kb": 5, "at": "t", "rng": 9}, "pas": {"mp": 25}, "i": "tome", "c": Color(0.55, 0.95, 0.9)},
			{"n": "Eco Infinito", "mp": 10, "cd": 40, "k": "none", "p": {"buff": {"id": "eco", "t": 8, "eff": {"cdr": 40, "mag_pct": 20}}}, "pas": {"mp": 40, "regen": 1.0, "cdr": 8}, "i": "tome", "c": Color(0.7, 0.6, 1.0)},
		]},
	],
}


# One signature passive per class; it strengthens at levels 10 and 20 (ranks I, II, III).
const PASSIVES := {
	"warrior": {"name": "Sangue de Ferro", "desc": "Abaixo de 40%% de vida: +%d%% de ataque e -%d%% de dano recebido", "v": [[20, 10], [30, 15], [40, 20]]},
	"mage": {"name": "Fluxo Arcano", "desc": "Ao abater um inimigo, recupera %d%% da mana", "v": [[6], [9], [12]]},
	"archer": {"name": "Tiro Certeiro", "desc": "A cada %d flechas, a próxima causa +80%% de dano", "v": [[5], [4], [3]]},
	"paladin": {"name": "Aura Sagrada", "desc": "Regenera %.1f%% da vida por segundo", "v": [[0.6], [0.9], [1.2]]},
	"assassin": {"name": "Golpe Furtivo", "desc": "O primeiro golpe em um inimigo ileso causa +%d%% de dano", "v": [[50], [80], [110]]},
	"summoner": {"name": "Laço Espiritual", "desc": "Familiares causam +%d%% de dano; +%.1f mana/s para você", "v": [[20, 0.8], [35, 1.2], [50, 1.6]]},
}


static func passive_rank(level: int) -> int:
	return 1 + (1 if level >= 10 else 0) + (1 if level >= 20 else 0)


static func passive_v(class_id: String, level: int) -> Array:
	return PASSIVES[class_id]["v"][passive_rank(level) - 1]


static func passive_text(class_id: String, level: int) -> String:
	var p: Dictionary = PASSIVES[class_id]
	var v: Array = passive_v(class_id, level)
	var d: String = p["desc"]
	match v.size():
		1: d = d % v[0]
		2: d = d % [v[0], v[1]]
	return "%s %s — %s" % [p["name"], ["I", "II", "III"][passive_rank(level) - 1], d]


static func base(class_id: String) -> Dictionary:
	return BASE.get(class_id, BASE["warrior"])


static func branches(class_id: String) -> Array:
	return TREES.get(class_id, TREES["warrior"])


static func node_id(branch: int, tier: int) -> String:
	return "%d_%d" % [branch, tier]


static func node(class_id: String, branch: int, tier: int) -> Dictionary:
	return branches(class_id)[branch]["nodes"][tier]


## Skill by node id ("branch_tier").
static func skill(class_id: String, sid: String) -> Dictionary:
	var parts := sid.split("_")
	return node(class_id, int(parts[0]), int(parts[1]))


static func describe(eff: Dictionary) -> String:
	var parts := PackedStringArray()
	for k in eff:
		var t: Array = EFF_TEXT[k]
		var v: float = float(eff[k])
		var txt := ("%d" % roundi(v)) if (v == floorf(v)) else ("%.1f" % v)
		parts.append("%s%s%s %s" % ["-" if k == "dmg_red" else "+", txt, t[1], t[0]])
	return ", ".join(parts)


const STAT_NAME := {"atk": "ataque", "mag": "magia", "mix": "ataque + magia"}


## Plain-language effect of an active skill (generated from its parameters).
static func active_text(sk: Dictionary) -> String:
	var p: Dictionary = sk["p"]
	var parts := PackedStringArray()
	match str(sk["k"]):
		"nova":
			var where := "no alvo" if p.get("at", "") == "t" else "ao redor"
			parts.append("Golpe %s (%d m): %d%% de %s%s" % [where, roundi(float(p["r"])), roundi(float(p["m"]) * 100.0), STAT_NAME[p["s"]], " ×2" if p.get("twice", false) else ""])
		"meteor": parts.append("Chuva de meteoros: %d%% de magia" % roundi(float(p["m"]) * 100.0) + (" + explosão final" if p.has("extra") else ""))
		"storm": parts.append("Tempestade de raios: %d%% de magia" % roundi(float(p["m"]) * 100.0))
		"volley": parts.append("%d flecha%s%s: %d%% de ataque cada" % [int(p["n"]) * int(p.get("waves", 1)), "s" if int(p["n"]) > 1 else "", " em leque" if 0 < int(p["arc"]) and int(p["arc"]) < 360 else (" em círculo" if int(p["arc"]) == 360 else ""), roundi(float(p["m"]) * 100.0)])
		"dash": parts.append(("Avança %d m" if float(p["dist"]) > 0.0 else "Recua %d m") % roundi(absf(float(p["dist"]))) + (", golpeando: %d%% de ataque" % roundi(float(p["m"]) * 100.0) if float(p["m"]) > 0.0 else "") + " · invulnerável um instante")
		"summon": parts.append("Invoca %d familiar%s espiritual%s" % [int(p["n"]), "es" if int(p["n"]) > 1 else "", "is" if int(p["n"]) > 1 else ""])
	if p.has("extra"):
		parts.append("Explosão final: %d%% de magia" % roundi(float((p["extra"] as Dictionary)["m"]) * 100.0))
	if p.has("summon") and str(sk["k"]) != "summon":
		parts.append("Invoca um familiar")
	if p.has("heal"):
		parts.append("Cura %d%% da vida" % roundi(float(p["heal"]) * 100.0))
	if p.has("shield"):
		parts.append("Invulnerável por %s s" % ("%.1f" % float(p["shield"]) if float(p["shield"]) != floorf(float(p["shield"])) else str(int(p["shield"]))))
	if p.has("buff"):
		var bf: Dictionary = p["buff"]
		parts.append("%s por %d s" % [describe(bf["eff"]), int(bf["t"])])
	return "\n".join(parts)


static func node_text(class_id: String, branch: int, tier: int) -> String:
	var sk := node(class_id, branch, tier)
	var out := "%d mana · recarga %d s\n%s" % [roundi(float(sk["mp"])), roundi(float(sk["cd"])), active_text(sk)]
	var pas := describe(sk["pas"])
	if pas != "":
		out += "\nPassivo ao aprender: " + pas
	return out
