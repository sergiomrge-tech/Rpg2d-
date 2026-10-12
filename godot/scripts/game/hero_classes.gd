class_name HeroClasses
extends RefCounted
## Six progression archetypes. New game only; saves retain their original class.
## Abilities are handled by Player at animation hit-frames, not merely labels.

const ORDER := ["warrior", "mage", "archer", "paladin", "assassin", "summoner"]

const CLASSES := {
	"warrior": {
		"name": "Guerreiro", "role": "Espada e combate corpo a corpo",
		"strong": "Muita vida, defesa e golpes fortes", "weak": "Curto alcance, lento e sem magia", "weapon": "sword",
		"move": 0.91, "defense": 8.0, "crit": 0.08, "damage_taken": 0.91,
		"skill": "Execução de Espada", "desc": "Só ataques com espada e técnicas físicas; sem conjuração.",
		"hp": 135.0, "mp": 45.0, "atk": 16.0, "mag": 9.0,
		"hp_gain": 16.0, "mp_gain": 4.0, "atk_gain": 2.8, "mag_gain": 1.1,
		"icon": "skill_sword", "color": Color(0.96, 0.69, 0.39)
	},
	"mage": {
		"name": "Mago", "role": "Magia elemental e arcana",
		"strong": "Maior dano mágico e muita mana", "weak": "Pouca vida e defesa, sem armas", "weapon": "none",
		"move": 0.97, "defense": 0.0, "crit": 0.06, "damage_taken": 1.14,
		"skill": "Explosão Arcana", "desc": "Somente magia: feitiço básico e feitiço carregado.",
		"hp": 78.0, "mp": 105.0, "atk": 7.0, "mag": 23.0,
		"hp_gain": 9.0, "mp_gain": 11.0, "atk_gain": 1.0, "mag_gain": 3.6,
		"icon": "skill_spark", "color": Color(0.53, 0.74, 1.0)
	},
	"archer": {
		"name": "Arqueiro", "role": "Alcance e precisão",
		"strong": "Longo alcance, agilidade e precisão", "weak": "Frágil de perto, não usa outras armas ou magia", "weapon": "bow",
		"move": 1.12, "defense": 1.0, "crit": 0.13, "damage_taken": 1.09,
		"skill": "Rajada de Flechas", "desc": "Somente arco: flecha simples e rajada tripla.",
		"hp": 96.0, "mp": 60.0, "atk": 14.0, "mag": 10.0,
		"hp_gain": 11.0, "mp_gain": 5.0, "atk_gain": 2.7, "mag_gain": 1.2,
		"icon": "skill_roll", "color": Color(0.62, 0.89, 0.53)
	},
	"paladin": {
		"name": "Paladino", "role": "Proteção e luz sagrada",
		"strong": "Maior proteção, autocura e resistência", "weak": "Lento, menor dano ofensivo", "weapon": "sword",
		"move": 0.85, "defense": 11.0, "crit": 0.04, "damage_taken": 0.83,
		"skill": "Luz Restauradora", "desc": "Espada e poder sagrado: golpe físico e cura.",
		"hp": 151.0, "mp": 77.0, "atk": 12.0, "mag": 17.0,
		"hp_gain": 17.0, "mp_gain": 7.0, "atk_gain": 2.2, "mag_gain": 2.4,
		"icon": "gear_armor", "color": Color(1.0, 0.85, 0.47)
	},
	"assassin": {
		"name": "Assassino", "role": "Mobilidade e golpes críticos",
		"strong": "Muito rápido, crítico e golpes consecutivos", "weak": "Pouca defesa, precisa se aproximar", "weapon": "dual_daggers",
		"move": 1.19, "defense": 0.0, "crit": 0.28, "damage_taken": 1.19,
		"skill": "Passo das Adagas", "desc": "Só duas adagas: combos duplos e ataque rápido.",
		"hp": 90.0, "mp": 64.0, "atk": 18.0, "mag": 10.0,
		"hp_gain": 10.0, "mp_gain": 5.0, "atk_gain": 3.4, "mag_gain": 1.1,
		"icon": "skill_sword", "color": Color(0.86, 0.62, 0.96)
	},
	"summoner": {
		"name": "Invocador", "role": "Aliados invocados",
		"strong": "Pets lutam e protegem à distância", "weak": "Muito frágil, depende dos pets, sem ataque próprio", "weapon": "none",
		"move": 0.95, "defense": 0.0, "crit": 0.0, "damage_taken": 1.21,
		"skill": "Espírito Guardião", "desc": "Somente invoca ou comanda pets: sem arma nem feitiços ofensivos.",
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
	# The starting equipment is part of the class rules, not a cosmetic name.
	match gs.class_id:
		"archer":
			gs.eq_weapon = "hunter_bow"
		"assassin":
			gs.eq_weapon = "twin_daggers"
		"mage", "summoner":
			gs.eq_weapon = ""
		_:
			gs.eq_weapon = "rusty_sword"


static func can_equip(class_id: String, item: Dictionary) -> bool:
	if int(item.get("slot", 0)) != 1:
		return true
	var allowed: String = str(info(class_id)["weapon"])
	if allowed == "none":
		return false
	return str(item.get("weapon_type", "sword")) == allowed


static func allows_melee(class_id: String) -> bool:
	return class_id == "warrior" or class_id == "paladin" or class_id == "assassin"


static func allows_magic(class_id: String) -> bool:
	return class_id == "mage" or class_id == "paladin"


static func allows_bow(class_id: String) -> bool:
	return class_id == "archer"


static func allows_pets(class_id: String) -> bool:
	return class_id == "summoner"
