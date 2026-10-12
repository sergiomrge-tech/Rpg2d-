class_name Loot
extends RefCounted
## Drop tables: gold, materials, tomes, rolled equipment with rarity & mods.

static func roll_rarity(level: int, boss := false, elite := false) -> int:
	var r := randf()
	var bonus := 0.0 + (0.25 if boss else 0.0) + (0.1 if elite else 0.0) + level * 0.004
	if r < 0.02 + bonus * 0.2:
		return 3
	if r < 0.1 + bonus * 0.5:
		return 2
	if r < 0.4 + bonus:
		return 1
	return 0

static func roll_mods(rar: int, slot: String) -> Dictionary:
	var pool := ["crit", "hp", "mp", "spd", "lifesteal", "fire", "stamina"]
	if slot == "weapon":
		pool += ["atk", "mag", "fire", "lifesteal"]
	elif slot == "armor":
		pool += ["def", "hp", "stamina"]
	else:
		pool += ["def", "atk", "mag"]
	var mods := {}
	var n := rar  # uncommon: 1, rare: 2, epic: 3
	for i in n:
		var k: String = pool[randi() % pool.size()]
		var d: Dictionary = Data.MODS[k]
		var v := float(randi_range(int(d["min"]), int(d["max"]))) * (1.0 + 0.25 * rar)
		mods[k] = mods.get(k, 0.0) + roundf(v)
	return mods

static func roll_gear(level: int, boss := false, elite := false) -> Dictionary:
	var tier := clampi(level / 3, 0, 3)
	var cands: Array = []
	for id in Data.GEAR:
		var g: Dictionary = Data.GEAR[id]
		if int(g["price"]) > 0 and absi(int(g["tier"]) - tier) <= 1 and int(g["tier"]) >= 1:
			cands.append(id)
	if cands.is_empty():
		return {}
	var id: String = cands[randi() % cands.size()]
	var rar := roll_rarity(level, boss, elite)
	return {"id": id, "rar": rar, "mods": roll_mods(rar, Data.GEAR[id]["slot"])}

## Spawns pickups for a defeated enemy (called by World).
static func drop_for(w: World, e: Enemy) -> void:
	var d: Dictionary = e.def
	var pos := e.global_position
	var g_range: Array = d["gold"]
	var gold := randi_range(int(g_range[0]), int(g_range[1]))
	if e.is_boss:
		gold *= 6
	var bags := clampi(1 + gold / 14, 1, 6)
	for i in bags:
		w.spawn_pickup("gold", "gold", maxi(1, gold / bags), pos)
	for l in d.get("loot", []):
		if randf() < float(l["p"]) * (1.6 if e.is_elite else 1.0):
			w.spawn_pickup("item", l["id"], 1, pos)
	for l in e.extra_loot:
		if randf() < float(l["p"]):
			w.spawn_pickup("item", l["id"], int(l.get("n", 1)), pos)
	var pg := 0.045 + (0.08 if e.is_elite else 0.0)
	if e.is_boss:
		pg = 1.0
	if randf() < pg:
		var g := roll_gear(int(d["level"]), e.is_boss, e.is_elite)
		if not g.is_empty():
			w.spawn_pickup("gear", g["id"], 1, pos, g)
	if randf() < 0.08:
		w.spawn_pickup("heart", "heart", int(18 + Game.level * 3), pos)
	if randf() < 0.06:
		w.spawn_pickup("mana", "mana", int(10 + Game.level), pos)
