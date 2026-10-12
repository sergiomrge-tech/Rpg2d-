class_name DailyBoard
extends RefCounted
## Guild daily board: three quests per real-world day (hunt X monsters / bring Y materials) plus a bonus for finishing all.
## State lives in Game.daily ({"day", "quests", "bonus"}) and is saved with the game.

const POOLS := [
	[1, ["imp", "imp_scout", "imp_raider", "oni"]],
	[5, ["oni_lancer", "oni_shielder", "imp_howler", "imp_pyro", "imp_hexer", "imp_bomber"]],
	[8, ["oni_executioner", "sand_imp", "sand_wraith", "oni_nomad"]],
	[12, ["mine_imp", "rock_oni", "frost_imp", "ice_oni", "witch_imp", "bog_wraith", "treant_demon"]],
	[16, ["ash_wraith", "demon_knight", "spirit_corrupt"]],
]
const MATS := [[1, "imp_horn", 5, 9], [6, "demon_hide", 4, 7], [10, "spirit_dust", 4, 7], [14, "hell_ember", 2, 4]]

static var _regions := {}


static func today() -> int:
	var bias := int(Time.get_time_zone_from_system().get("bias", 0)) * 60
	return int((Time.get_unix_time_from_system() + bias) / 86400.0)


static func seconds_left() -> int:
	var bias := int(Time.get_time_zone_from_system().get("bias", 0)) * 60
	var t := int(Time.get_unix_time_from_system()) + bias
	return 86400 - (t % 86400)


## Make sure the board belongs to today; rolls new quests when the day changed.
static func refresh(force_day: int = -1) -> void:
	var d := force_day if force_day >= 0 else today()
	if int(Game.daily.get("day", -1)) == d and not (Game.daily.get("quests", []) as Array).is_empty():
		return
	Game.daily = {"day": d, "quests": _roll(d), "bonus": false}


static func _roll(day: int) -> Array:
	var rng := RandomNumberGenerator.new()
	rng.seed = day * 7919 + Game.state.level * 31
	var L := maxi(1, Game.state.level)
	var out: Array = []
	# 1) hunt any monsters
	var need := mini(30, 8 + L)
	out.append(_q("hunt", "any", "", need, need * 7 + L * 10, need * 5 + L * 12, ""))
	# 2) hunt a specific kind
	var kinds: Array = []
	for p in POOLS:
		if int(p[0]) <= L + 2:
			kinds.append_array(p[1])
	var kind: String = kinds[rng.randi() % kinds.size()]
	var n2 := rng.randi_range(5, 9)
	out.append(_q("hunt", kind, "", n2, n2 * 14 + L * 14, n2 * 9 + L * 16, "potion" if rng.randf() < 0.6 else "ether"))
	# 3) deliver materials
	var mats: Array = []
	for m in MATS:
		if int(m[0]) <= L + 2:
			mats.append(m)
	var m: Array = mats[rng.randi() % mats.size()]
	var n3 := rng.randi_range(int(m[2]), int(m[3]))
	var val := int(Data.items[m[1]].get("value", 20))
	out.append(_q("deliver", "", str(m[1]), n3, n3 * val * 2 + L * 12, n3 * 10 + L * 14, ""))
	return out


static func _q(type: String, kind: String, item: String, need: int, gold: int, xp: int, reward_item: String) -> Dictionary:
	return {"type": type, "kind": kind, "item": item, "need": need, "have": 0, "state": 0, "gold": gold, "xp": xp, "reward_item": reward_item}


static func title(q: Dictionary) -> String:
	if q["type"] == "deliver":
		return "Trazer %d× %s" % [int(q["need"]), Data.items[q["item"]]["name"]]
	if q["kind"] == "any":
		return "Caçar %d monstros" % int(q["need"])
	return "Caçar %d× %s" % [int(q["need"]), Data.demons[q["kind"]]["name"]]


static func hint(q: Dictionary) -> String:
	if q["type"] == "deliver":
		return "Material comum dos demônios"
	if q["kind"] == "any":
		return "Qualquer demônio, em qualquer região"
	var r: Array = regions_of(q["kind"])
	return "Encontrado em: " + (", ".join(r) if not r.is_empty() else "várias regiões")


static func progress(q: Dictionary) -> int:
	if q["type"] == "deliver":
		return mini(Game.state.count(q["item"]), int(q["need"])) if int(q["state"]) < 3 else int(q["need"])
	return mini(int(q["have"]), int(q["need"]))


static func ready(q: Dictionary) -> bool:
	return int(q["state"]) == 1 and progress(q) >= int(q["need"])


static func reward_text(q: Dictionary) -> String:
	var s := "%d ouro · %d EXP" % [int(q["gold"]), int(q["xp"])]
	if q["reward_item"] != "":
		s += " · " + str(Data.items[q["reward_item"]]["name"])
	return s


static func regions_of(kind: String) -> Array:
	if _regions.is_empty():
		for m in Game.MAP_TITLES:
			var data = Sheets.read_json("Maps/" + m)
			if data == null:
				continue
			for sp in data["spawns"]:
				var arr: Array = _regions.get(sp["kind"], [])
				var nm: String = str(Game.MAP_TITLES[m][0])
				if not arr.has(nm):
					arr.append(nm)
				_regions[sp["kind"]] = arr
		_regions["__done"] = []
	return _regions.get(kind, [])


static func accept(i: int) -> void:
	var q: Dictionary = Game.daily["quests"][i]
	if int(q["state"]) == 0:
		q["state"] = 1
		q["have"] = 0


static func claim(i: int) -> bool:
	var q: Dictionary = Game.daily["quests"][i]
	if not ready(q):
		return false
	var gs := Game.state
	if q["type"] == "deliver":
		for k in int(q["need"]):
			gs.take(q["item"])
	q["state"] = 3
	gs.gold += int(q["gold"])
	if q["reward_item"] != "":
		gs.add(q["reward_item"], 1)
	Game.award_xp(int(q["xp"]))
	return true


static func done_count() -> int:
	var n := 0
	for q in Game.daily.get("quests", []):
		if int(q["state"]) == 3:
			n += 1
	return n


static func claim_bonus() -> bool:
	if done_count() < 3 or Game.daily.get("bonus", false):
		return false
	Game.daily["bonus"] = true
	var at: Vector2 = Player.I.global_position + Vector2(0, 40)
	Loot.gear_drop(maxi(Game.state.level, 8), true, at, 1.0)
	Game.state.gold += 150 + Game.state.level * 20
	return true


static func on_kill(e: Enemy) -> void:
	if e.arena:
		return
	for q in Game.daily.get("quests", []):
		if int(q["state"]) == 1 and q["type"] == "hunt" and (q["kind"] == "any" or q["kind"] == str(e.def["id"])):
			q["have"] = int(q["have"]) + 1
			if int(q["have"]) == int(q["need"]):
				Game.hud.banner("Missão diária cumprida", "Entregue na Guilda")


static func lines() -> Array:
	var out: Array = []
	for q in Game.daily.get("quests", []):
		if int(q["state"]) == 1:
			out.append("Diária: %s (%d/%d)" % [title(q), progress(q), int(q["need"])])
	return out


## JSON gives floats back: normalise after loading a save.
static func normalise(d: Dictionary) -> Dictionary:
	var out := {"day": int(d.get("day", -1)), "bonus": bool(d.get("bonus", false)), "quests": []}
	for q in d.get("quests", []):
		var c := _q(str(q["type"]), str(q["kind"]), str(q["item"]), int(q["need"]), int(q["gold"]), int(q["xp"]), str(q["reward_item"]))
		c["have"] = int(q["have"])
		c["state"] = int(q["state"])
		out["quests"].append(c)
	return out
