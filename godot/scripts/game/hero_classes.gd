class_name HeroClasses
extends RefCounted
## Six progression archetypes. New game only; saves retain their original class.
## Abilities are handled by Player at animation hit-frames, not merely labels.

const ORDER := ["warrior", "mage", "archer", "paladin", "assassin", "summoner"]

const CLASSES := {
	"warrior": {
		"name": "Guerreiro", "role": "Espada e combate corpo a corpo",
		"skill": "Corte Crescente", "desc": "Combos de espada, lâmina de energia e resistência.",
		"hp": 135.0, "mp": 45.0, "atk": 16.0, "mag": 9.0,
		"hp_gain": 16.0, "mp_gain": 4.0, "atk_gain": 2.8, "mag_gain": 1.1,
		"icon": "skill_sword", "color": Color(0.96, 0.69, 0.39)
	},
	"mage": {
		"name": "Mago", "role": "Magia elemental e arcana",
		"skill": "Centelha Arcana", "desc": "Disparos mágicos e alto poder de feitiço.",
		"hp": 78.0, "mp": 105.0, "atk": 7.0, "mag": 23.0,
		"hp_gain": 9.0, "mp_gain": 11.0, "atk_gain": 1.0, "mag_gain": 3.6,
		"icon": "skill_spark", "color": Color(0.53, 0.74, 1.0)
	},
	"archer": {
		"name": "Arqueiro", "role": "Alcance e precisão",
		"skill": "Rajada de Flechas", "desc": "Flechas à distância e uma rajada tripla.",
		"hp": 96.0, "mp": 60.0, "atk": 14.0, "mag": 10.0,
		"hp_gain": 11.0, "mp_gain": 5.0, "atk_gain": 2.7, "mag_gain": 1.2,
		"icon": "skill_roll", "color": Color(0.62, 0.89, 0.53)
	},
	"paladin": {
		"name": "Paladino", "role": "Proteção e luz sagrada",
		"skill": "Luz Restauradora", "desc": "Cura própria e punição luminosa em área.",
		"hp": 151.0, "mp": 77.0, "atk": 12.0, "mag": 17.0,
		"hp_gain": 17.0, "mp_gain": 7.0, "atk_gain": 2.2, "mag_gain": 2.4,
		"icon": "gear_armor", "color": Color(1.0, 0.85, 0.47)
	},
	"assassin": {
		"name": "Assassino", "role": "Mobilidade e golpes críticos",
		"skill": "Passo Sombrio", "desc": "Ataques rápidos, crítico elevado e deslocamento.",
		"hp": 90.0, "mp": 64.0, "atk": 18.0, "mag": 10.0,
		"hp_gain": 10.0, "mp_gain": 5.0, "atk_gain": 3.4, "mag_gain": 1.1,
		"icon": "skill_sword", "color": Color(0.86, 0.62, 0.96)
	},
	"summoner": {
		"name": "Invocador", "role": "Aliados e magia espiritual",
		"skill": "Espírito Guardião", "desc": "Invoca um familiar temporário que protege Ren.",
		"hp": 84.0, "mp": 108.0, "atk": 8.0, "mag": 22.0,
		"hp_gain": 9.0, "mp_gain": 10.0, "atk_gain": 1.0, "mag_gain": 3.4,
		"icon": "ether", "color": Color(0.49, 0.93, 0.86)
	}
}


static func valid(id: String) -> bool:
	return CLASSES.has(id)


static func info(id: String) -> Dictionary:
	return CLASSES.get(id, CLASSES["warrior"])


static func apply_new_game(gs: GameState, id: String) -> void:
	var d := info(id)
	gs.class_id = id if valid(id) else "warrior"
	gs.max_hp = float(d["hp"])
	gs.max_mp = float(d["mp"])
	gs.atk = float(d["atk"])
	gs.mag = float(d["mag"])
