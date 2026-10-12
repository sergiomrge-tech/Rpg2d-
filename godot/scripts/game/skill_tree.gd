class_name SkillTree
extends RefCounted
## Attributes (Força, Constituição, Mana, Inteligência, Agilidade, Sorte) and one 3-branch skill tree per hero class.
## Every level grants ATTR_PER_LEVEL attribute points and 1 skill point; tree tiers unlock with the hero's level.

const ATTR_PER_LEVEL := 3
const TIER_LEVELS := [2, 5, 9, 14]
const TIER_COST := [1, 1, 1, 2]

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

# Active skills unlocked from the tree (R / F keys): name, mana, cooldown, kind
const ACTIVES := {
	"mage": {"r": {"name": "Chuva de Meteoros", "mp": 38.0, "cd": 11.0, "icon": "skill_spark", "color": Color(1.0, 0.55, 0.25)},
		"f": {"name": "Tempestade de Raios", "mp": 30.0, "cd": 9.0, "icon": "skill_spark", "color": Color(0.55, 0.8, 1.0)}},
	"warrior": {"r": {"name": "Grito de Guerra", "mp": 15.0, "cd": 18.0, "icon": "skill_sword", "color": Color(1.0, 0.6, 0.3)},
		"f": {"name": "Terremoto", "mp": 20.0, "cd": 11.0, "icon": "skill_sword", "color": Color(0.85, 0.7, 0.45)}},
	"paladin": {"r": {"name": "Escudo Sagrado", "mp": 25.0, "cd": 25.0, "icon": "gear_armor", "color": Color(1.0, 0.95, 0.6)},
		"f": {"name": "Julgamento Divino", "mp": 30.0, "cd": 14.0, "icon": "skill_spark", "color": Color(1.0, 0.9, 0.5)}},
	"archer": {"r": {"name": "Foco Mortal", "mp": 15.0, "cd": 20.0, "icon": "skill_roll", "color": Color(0.7, 1.0, 0.6)},
		"f": {"name": "Salva Total", "mp": 22.0, "cd": 10.0, "icon": "skill_roll", "color": Color(0.6, 0.95, 0.5)}},
	"assassin": {"r": {"name": "Véu das Sombras", "mp": 15.0, "cd": 18.0, "icon": "skill_roll", "color": Color(0.6, 0.5, 0.9)},
		"f": {"name": "Dança das Lâminas", "mp": 18.0, "cd": 9.0, "icon": "skill_sword", "color": Color(0.8, 0.75, 1.0)}},
	"summoner": {"r": {"name": "Vínculo Espiritual", "mp": 20.0, "cd": 24.0, "icon": "skill_spark", "color": Color(0.6, 0.95, 0.9)},
		"f": {"name": "Explosão Espiritual", "mp": 28.0, "cd": 12.0, "icon": "skill_spark", "color": Color(0.5, 0.9, 0.85)}},
}

# Trees: 3 branches x 4 tiers. Node = [name, effects]. "unlock": "r"/"f" grants the active skill.
const TREES := {
	"warrior": [
		{"name": "Fúria", "icon": "skill_sword", "nodes": [
			["Golpe Pesado", {"atk_pct": 6}], ["Grito de Guerra", {"unlock": "r", "crit": 2}],
			["Sede de Sangue", {"atk_pct": 8, "lifesteal": 3}], ["Mestre da Lâmina", {"atk_pct": 12, "crit": 5}]]},
		{"name": "Muralha", "icon": "gear_armor", "nodes": [
			["Pele de Ferro", {"def": 4, "hp": 20}], ["Fôlego de Guerra", {"hp": 30, "heal_pct": 15}],
			["Resistência", {"dmg_red": 6, "def": 4}], ["Inabalável", {"hp": 60, "dmg_red": 8}]]},
		{"name": "Tremor", "icon": "skill_roll", "nodes": [
			["Passos Firmes", {"mspd": 4, "aspd": 4}], ["Terremoto", {"unlock": "f", "aspd": 3}],
			["Veterano", {"xp_pct": 8, "cdr": 6}], ["Lenda da Guilda", {"cdr": 12, "aspd": 8}]]}],
	"mage": [
		{"name": "Piromancia", "icon": "skill_spark", "nodes": [
			["Chama Viva", {"mag_pct": 6}], ["Chuva de Meteoros", {"unlock": "r", "mag_pct": 3}],
			["Brasa Ardente", {"mag_pct": 8, "crit": 3}], ["Apocalipse", {"mag_pct": 14, "cdr": 8}]]},
		{"name": "Tempestade", "icon": "skill_spark", "nodes": [
			["Fluxo Arcano", {"regen": 0.6, "mp": 10}], ["Tempestade de Raios", {"unlock": "f", "regen": 0.4}],
			["Condutor", {"mag_pct": 6, "cdr": 6}], ["Olho da Tormenta", {"mag_pct": 10, "regen": 1.0}]]},
		{"name": "Sabedoria", "icon": "tome", "nodes": [
			["Mente Aberta", {"mp": 15, "xp_pct": 4}], ["Escudo Arcano", {"def": 3, "hp": 15}],
			["Concentração", {"crit": 4, "regen": 0.5}], ["Arquimago", {"mp": 40, "mag_pct": 8}]]}],
	"archer": [
		{"name": "Precisão", "icon": "skill_roll", "nodes": [
			["Mira Firme", {"atk_pct": 6}], ["Foco Mortal", {"unlock": "r", "crit": 3}],
			["Olhar de Águia", {"crit": 6, "atk_pct": 4}], ["Tiro de Mestre", {"atk_pct": 12, "crit": 6}]]},
		{"name": "Chuva", "icon": "skill_roll", "nodes": [
			["Dedos Ágeis", {"aspd": 6}], ["Salva Total", {"unlock": "f", "aspd": 4}],
			["Aljava Cheia", {"cdr": 8, "atk_pct": 4}], ["Tempestade de Flechas", {"atk_pct": 10, "cdr": 10}]]},
		{"name": "Caçador", "icon": "gear_charm", "nodes": [
			["Pés Leves", {"mspd": 5, "dodge": 2}], ["Instinto", {"dodge": 3, "hp": 20}],
			["Camuflagem", {"dodge": 4, "mspd": 4}], ["Predador", {"xp_pct": 10, "dodge": 4, "crit": 3}]]}],
	"paladin": [
		{"name": "Luz", "icon": "skill_spark", "nodes": [
			["Fé Ardente", {"mag_pct": 5, "atk_pct": 3}], ["Julgamento Divino", {"unlock": "f", "mag_pct": 3}],
			["Martelo Sagrado", {"atk_pct": 8, "mag_pct": 6}], ["Avatar da Luz", {"atk_pct": 10, "mag_pct": 10}]]},
		{"name": "Bastião", "icon": "gear_armor", "nodes": [
			["Armadura Bendita", {"def": 5, "hp": 25}], ["Escudo Sagrado", {"unlock": "r", "def": 3}],
			["Vontade de Aço", {"dmg_red": 6, "hp": 30}], ["Guardião de Aetheria", {"dmg_red": 10, "def": 8}]]},
		{"name": "Redenção", "icon": "potion", "nodes": [
			["Mãos Curativas", {"heal_pct": 15, "regen": 0.4}], ["Bênção", {"hp": 30, "mp": 12}],
			["Vigor Divino", {"lifesteal": 3, "regen": 0.5}], ["Milagre", {"heal_pct": 30, "lifesteal": 5}]]}],
	"assassin": [
		{"name": "Lâminas", "icon": "skill_sword", "nodes": [
			["Corte Preciso", {"atk_pct": 6, "crit": 2}], ["Dança das Lâminas", {"unlock": "f", "aspd": 4}],
			["Veneno Letal", {"atk_pct": 8, "crit": 4}], ["Mestre Assassino", {"atk_pct": 12, "crit": 8}]]},
		{"name": "Sombras", "icon": "skill_roll", "nodes": [
			["Passo Sombrio", {"dodge": 3, "mspd": 4}], ["Véu das Sombras", {"unlock": "r", "dodge": 3}],
			["Fantasma", {"dodge": 5, "aspd": 5}], ["Sombra Eterna", {"dodge": 8, "mspd": 8}]]},
		{"name": "Ladrão", "icon": "coin", "nodes": [
			["Mãos Rápidas", {"xp_pct": 5, "aspd": 3}], ["Olho no Ouro", {"xp_pct": 5, "hp": 15}],
			["Sede de Sangue", {"lifesteal": 4, "crit": 3}], ["Rei dos Ladrões", {"lifesteal": 6, "cdr": 10}]]}],
	"summoner": [
		{"name": "Espíritos", "icon": "skill_spark", "nodes": [
			["Elo Espiritual", {"mag_pct": 6}], ["Explosão Espiritual", {"unlock": "f", "mag_pct": 3}],
			["Legião", {"mag_pct": 8, "cdr": 6}], ["Senhor dos Espíritos", {"mag_pct": 14, "cdr": 8}]]},
		{"name": "Vínculo", "icon": "potion", "nodes": [
			["Aura Protetora", {"def": 3, "hp": 20}], ["Vínculo Espiritual", {"unlock": "r", "regen": 0.4}],
			["Comunhão", {"hp": 30, "heal_pct": 15}], ["Alma Gêmea", {"dmg_red": 8, "hp": 40}]]},
		{"name": "Mente", "icon": "tome", "nodes": [
			["Foco Calmo", {"mp": 15, "regen": 0.5}], ["Reservatório", {"mp": 25}],
			["Sabedoria Antiga", {"xp_pct": 8, "regen": 0.6}], ["Eco Infinito", {"mp": 40, "regen": 1.0, "cdr": 8}]]}],
}


static func base(class_id: String) -> Dictionary:
	return BASE.get(class_id, BASE["warrior"])


static func branches(class_id: String) -> Array:
	return TREES.get(class_id, TREES["warrior"])


static func node_id(branch: int, tier: int) -> String:
	return "%d_%d" % [branch, tier]


static func node(class_id: String, branch: int, tier: int) -> Array:
	return branches(class_id)[branch]["nodes"][tier]


static func describe(eff: Dictionary) -> String:
	var parts := PackedStringArray()
	for k in eff:
		if k == "unlock":
			continue
		var t: Array = EFF_TEXT[k]
		var v: float = float(eff[k])
		var txt := ("%d" % roundi(v)) if (v == floorf(v)) else ("%.1f" % v)
		parts.append("%s%s%s %s" % ["-" if k == "dmg_red" else "+", txt, t[1], t[0]])
	return ", ".join(parts)


static func node_text(class_id: String, branch: int, tier: int) -> String:
	var n := node(class_id, branch, tier)
	var eff: Dictionary = n[1]
	var out := ""
	if eff.has("unlock"):
		var a: Dictionary = ACTIVES[class_id][eff["unlock"]]
		out = "Ativa [%s] %s · %d mana · %ds" % [str(eff["unlock"]).to_upper(), a["name"], roundi(a["mp"]), roundi(a["cd"])]
		if eff.size() > 1:
			out += "\n"
	return out + describe(eff)
