extends Node
## Global game state (autoload "Game"): hero progression, inventory, flags, quests, save/load.

signal toast(text: String, icon: String, color: Color)
signal leveled_up(level: int)
signal state_changed

const Sprites := preload("res://src/SpriteLib.gd")

var hero_name := "Kai"
var look := "kai"
var level := 1
var xp := 0
var hp := 80.0
var mp := 40.0
var stamina := 100.0
var gold := 30
var sp := 0
var skill_ranks := {}               # id -> rank
var slots: Array = ["", "", "", ""]
var inv := {}                       # id -> count
var gear: Array = []                # [{uid,id,rar,mods:{}}]
var equipped := {"weapon": -1, "armor": -1, "acc": -1}
var flags := {}
var quests := {}                    # id -> {state, step, progress}
var map_id := ""
var spawn_map := ""
var spawn_tile := Vector2i.ZERO
var playtime := 0.0
var kills := 0
var opened := {}                    # "map:chest" -> true
var allies: Array = []
var _uid := 1
var difficulty := 1.0               # multiplier on incoming damage (1 = normal/challenging)

func _ready() -> void:
	_setup_input()
	process_mode = Node.PROCESS_MODE_ALWAYS

func _process(dt: float) -> void:
	playtime += dt

# ------------------------------------------------------------------ input map
func _setup_input() -> void:
	var map := {
		"move_up": [KEY_W, KEY_UP], "move_down": [KEY_S, KEY_DOWN],
		"move_left": [KEY_A, KEY_LEFT], "move_right": [KEY_D, KEY_RIGHT],
		"attack": [KEY_J, KEY_Z], "dodge": [KEY_K, KEY_X, KEY_SHIFT],
		"interact": [KEY_E, KEY_SPACE, KEY_ENTER],
		"skill1": [KEY_1, KEY_U], "skill2": [KEY_2, KEY_I], "skill3": [KEY_3, KEY_O], "skill4": [KEY_4, KEY_P],
		"menu": [KEY_ESCAPE, KEY_TAB], "potion": [KEY_Q], "ether": [KEY_R], "cancel": [KEY_ESCAPE, KEY_K, KEY_X, KEY_BACKSPACE],
		"tab_left": [KEY_Q, KEY_PAGEUP], "tab_right": [KEY_R, KEY_PAGEDOWN],
	}
	for action in map:
		if not InputMap.has_action(action):
			InputMap.add_action(action)
		for k in map[action]:
			var ev := InputEventKey.new()
			ev.physical_keycode = k
			InputMap.action_add_event(action, ev)
	var pad := {"attack": JOY_BUTTON_X, "dodge": JOY_BUTTON_B, "interact": JOY_BUTTON_A, "cancel": JOY_BUTTON_B,
		"skill1": JOY_BUTTON_Y, "skill2": JOY_BUTTON_RIGHT_SHOULDER, "skill3": JOY_BUTTON_LEFT_SHOULDER, "menu": JOY_BUTTON_START}
	for action in pad:
		var ev := InputEventJoypadButton.new()
		ev.button_index = pad[action]
		InputMap.action_add_event(action, ev)

# ------------------------------------------------------------------ new game
func new_game(p_name: String, p_look: String, path: String) -> void:
	hero_name = p_name
	look = p_look
	level = 1
	xp = 0
	sp = 0
	gold = 30
	skill_ranks = {}
	slots = ["", "", "", ""]
	inv = {"potion": 2, "herb": 2}
	gear = []
	equipped = {"weapon": -1, "armor": -1, "acc": -1}
	flags = {}
	quests = {}
	opened = {}
	kills = 0
	playtime = 0.0
	allies = []
	var sk: String = Data.START_SKILL[path]
	skill_ranks[sk] = 1
	slots[0] = sk
	var w := add_gear("rusty_sword", 0)
	var a := add_gear("linen_tunic", 0)
	equip(w["uid"])
	equip(a["uid"])
	var s := stats()
	hp = s["hp"]
	mp = s["mp"]
	stamina = s["stamina"]
	map_id = "casa_heroi"
	spawn_map = "casa_heroi"
	spawn_tile = Vector2i(5, 7)

# ------------------------------------------------------------------ stats
func xp_to_next(lv: int) -> int:
	return int(46.0 * pow(float(lv), 1.62))

func gear_by_uid(uid: int) -> Dictionary:
	for g in gear:
		if g["uid"] == uid:
			return g
	return {}

func gear_stats(g: Dictionary) -> Dictionary:
	var base: Dictionary = Data.GEAR[g["id"]]["stats"]
	var mult: float = [1.0, 1.12, 1.26, 1.45, 1.7][int(g["rar"])]
	var out := {}
	for k in base:
		out[k] = out.get(k, 0.0) + roundf(float(base[k]) * mult)
	for k in g.get("mods", {}):
		out[k] = out.get(k, 0.0) + float(g["mods"][k])
	return out

func stats() -> Dictionary:
	var L := float(level)
	var s := {
		"hp": 70.0 + 12.0 * L, "mp": 30.0 + 4.0 * L, "stamina": 100.0,
		"atk": 8.0 + 2.2 * L, "mag": 8.0 + 2.4 * L, "def": 2.0 + 1.3 * L,
		"crit": 5.0, "spd": 0.0, "lifesteal": 0.0, "fire": 0.0,
	}
	for slot in equipped:
		var uid: int = equipped[slot]
		if uid < 0:
			continue
		var g := gear_by_uid(uid)
		if g.is_empty():
			continue
		var gs := gear_stats(g)
		for k in gs:
			s[k] = s.get(k, 0.0) + gs[k]
	return s

func gain_xp(n: int) -> int:
	xp += n
	var gained := 0
	while xp >= xp_to_next(level) and level < 60:
		xp -= xp_to_next(level)
		level += 1
		sp += 1
		gained += 1
	if gained > 0:
		var s := stats()
		hp = s["hp"]
		mp = s["mp"]
		stamina = s["stamina"]
		leveled_up.emit(level)
	return gained

# ------------------------------------------------------------------ inventory
func count(id: String) -> int:
	return int(inv.get(id, 0))

func add_item(id: String, n: int = 1) -> void:
	inv[id] = count(id) + n
	if inv[id] <= 0:
		inv.erase(id)
	state_changed.emit()

func item_def(id: String) -> Dictionary:
	if Data.ITEMS.has(id):
		return Data.ITEMS[id]
	if Data.GEAR.has(id):
		return Data.GEAR[id]
	return {"name": id, "type": "material", "icon": "gem", "price": 0, "desc": ""}

func add_gear(id: String, rarity: int, mods: Dictionary = {}) -> Dictionary:
	var g := {"uid": _uid, "id": id, "rar": rarity, "mods": mods}
	_uid += 1
	gear.append(g)
	state_changed.emit()
	return g

func equip(uid: int) -> void:
	var g := gear_by_uid(uid)
	if g.is_empty():
		return
	equipped[Data.GEAR[g["id"]]["slot"]] = uid
	var s := stats()
	hp = minf(hp, s["hp"])
	mp = minf(mp, s["mp"])
	state_changed.emit()

func gear_name(g: Dictionary) -> String:
	return Data.GEAR[g["id"]]["name"]

func gear_equipped(uid: int) -> bool:
	return uid in equipped.values()

func skill_rank(id: String) -> int:
	return int(skill_ranks.get(id, 0))

func learn_skill(id: String) -> void:
	skill_ranks[id] = maxi(1, skill_rank(id))
	if not (id in slots):
		var free := slots.find("")
		if free >= 0:
			slots[free] = id
	state_changed.emit()

func can_upgrade(id: String) -> String:
	var d: Dictionary = Data.SKILLS[id]
	var r := skill_rank(id)
	if r <= 0:
		return "Habilidade não aprendida"
	if r >= 5:
		return "Nível máximo"
	if level < int(d["req"]):
		return "Requer nível %d" % int(d["req"])
	if sp < 1:
		return "Sem pontos de habilidade"
	return ""

func upgrade_skill(id: String) -> bool:
	if can_upgrade(id) != "":
		return false
	sp -= 1
	skill_ranks[id] = skill_rank(id) + 1
	state_changed.emit()
	return true

# ------------------------------------------------------------------ flags / quests
func flag(k: String) -> bool:
	return bool(flags.get(k, false))

func set_flag(k: String, v: Variant = true) -> void:
	flags[k] = v

func quest_active(id: String) -> bool:
	return quests.has(id) and quests[id]["state"] == "active"

func quest_done(id: String) -> bool:
	return quests.has(id) and quests[id]["state"] == "done"

func start_quest(id: String) -> void:
	if not quests.has(id):
		quests[id] = {"state": "active", "step": 0, "progress": 0}
		toast.emit("Nova missão: " + str(Quests.QUESTS[id]["name"]), "scroll", Color("ffe066"))

func quest_step(id: String, step: int) -> void:
	if quest_active(id) and quests[id]["step"] < step:
		quests[id]["step"] = step
		quests[id]["progress"] = 0
		toast.emit("Missão atualizada: " + str(Quests.QUESTS[id]["name"]), "scroll", Color("9ad8ff"))

# ------------------------------------------------------------------ save / load
func serialize() -> Dictionary:
	return {
		"v": 1, "name": hero_name, "look": look, "level": level, "xp": xp, "hp": hp, "mp": mp, "gold": gold, "sp": sp,
		"ranks": skill_ranks, "slots": slots, "inv": inv, "gear": gear, "equipped": equipped, "flags": flags, "quests": quests,
		"map": map_id, "spawn_map": spawn_map, "spawn_tile": [spawn_tile.x, spawn_tile.y], "playtime": playtime, "kills": kills,
		"opened": opened, "uid": _uid, "allies": allies, "time": Time.get_unix_time_from_system(),
	}

func load_data(d: Dictionary) -> void:
	hero_name = d["name"]
	look = d["look"]
	level = int(d["level"])
	xp = int(d["xp"])
	hp = float(d["hp"])
	mp = float(d["mp"])
	gold = int(d["gold"])
	sp = int(d["sp"])
	skill_ranks = d["ranks"]
	slots = d["slots"]
	inv = d["inv"]
	gear = d["gear"]
	equipped = d["equipped"]
	flags = d["flags"]
	quests = d["quests"]
	map_id = d["map"]
	spawn_map = d["spawn_map"]
	spawn_tile = Vector2i(int(d["spawn_tile"][0]), int(d["spawn_tile"][1]))
	playtime = float(d["playtime"])
	kills = int(d["kills"])
	opened = d["opened"]
	_uid = int(d["uid"])
	allies = d.get("allies", [])
	# JSON turns ints into floats: normalise key fields
	for g in gear:
		g["uid"] = int(g["uid"])
		g["rar"] = int(g["rar"])
	for k in equipped:
		equipped[k] = int(equipped[k])
	for k in skill_ranks:
		skill_ranks[k] = int(skill_ranks[k])
	for k in inv:
		inv[k] = int(inv[k])
	stamina = float(stats()["stamina"])

func save_slot(slot: int, pos: Vector2i) -> bool:
	var d := serialize()
	d["pos"] = [pos.x, pos.y]
	var f := FileAccess.open("user://save_%s.json" % str(slot), FileAccess.WRITE)
	if f == null:
		return false
	f.store_string(JSON.stringify(d))
	return true

func read_slot(slot: Variant) -> Dictionary:
	var p := "user://save_%s.json" % str(slot)
	if not FileAccess.file_exists(p):
		return {}
	var v: Variant = JSON.parse_string(FileAccess.get_file_as_string(p))
	return v if v is Dictionary else {}
