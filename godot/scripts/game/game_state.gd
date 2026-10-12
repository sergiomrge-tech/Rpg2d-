class_name GameState
extends RefCounted
## Persistent player progress (serialised to the save file).

var level := 1
var xp := 0
var gold := 10
var max_hp := 100.0
var max_mp := 50.0
var max_st := 100.0
var atk := 11.0
var mag := 14.0
var spark_tier := 1
var sword_tier := 1
var guild_rank := "F"
var eq_weapon := "rusty_sword"
var eq_armor := ""
var eq_charm := ""
var inv_ids: Array = ["potion"]
var inv_counts: Array = [2]


func _gear(key: String) -> float:
	var t := 0.0
	for id in [eq_weapon, eq_armor, eq_charm]:
		if id != "" and Data.items.has(id):
			t += float(Data.items[id].get(key, 0))
	return t


func total_atk() -> float: return atk + _gear("atk")
func total_mag() -> float: return mag + _gear("mag")
func total_def() -> float: return _gear("defense")
func hp_max() -> float: return max_hp + _gear("hp")


func equipped(slot: int) -> String:
	return eq_weapon if slot == 1 else (eq_armor if slot == 2 else eq_charm)


func count(id: String) -> int:
	var n := 0
	for i in inv_ids.size():
		if inv_ids[i] == id:
			n += int(inv_counts[i])
	return n


func add(id: String, n: int) -> void:
	if id == "gold":
		gold += n
		return
	var i := inv_ids.find(id)
	if i < 0:
		inv_ids.append(id)
		inv_counts.append(n)
	else:
		inv_counts[i] = int(inv_counts[i]) + n


func take(id: String) -> bool:
	var i := inv_ids.find(id)
	if i < 0:
		return false
	inv_counts[i] = int(inv_counts[i]) - 1
	if int(inv_counts[i]) <= 0:
		inv_ids.remove_at(i)
		inv_counts.remove_at(i)
	return true


## Equip a bag item; the previous piece goes back to the bag.
func equip(id: String) -> bool:
	if not Data.items.has(id) or int(Data.items[id]["slot"]) == 0 or not take(id):
		return false
	var slot := int(Data.items[id]["slot"])
	var old := equipped(slot)
	if slot == 1: eq_weapon = id
	elif slot == 2: eq_armor = id
	else: eq_charm = id
	if old != "" and old != "rusty_sword":
		add(old, 1)
	return true


func can_craft(r: Dictionary) -> bool:
	if gold < int(r["gold"]):
		return false
	for n in r["needs"]:
		if count(n[0]) < int(n[1]):
			return false
	return true


func craft(r: Dictionary) -> void:
	gold -= int(r["gold"])
	for n in r["needs"]:
		for i in int(n[1]):
			take(n[0])
	add(r["result"], 1)


## @return true when leveled up
func gain_xp(amount: int) -> bool:
	xp += amount
	var up := false
	while xp >= Data.xp_to_next(level):
		xp -= Data.xp_to_next(level)
		level += 1
		max_hp += 14.0
		max_mp += 6.0
		max_st += 4.0
		atk += 2.2
		mag += 2.6
		up = true
	return up


func to_dict() -> Dictionary:
	return {"level": level, "xp": xp, "gold": gold, "max_hp": max_hp, "max_mp": max_mp, "max_st": max_st, "atk": atk, "mag": mag,
		"spark_tier": spark_tier, "sword_tier": sword_tier, "guild_rank": guild_rank, "eq_weapon": eq_weapon, "eq_armor": eq_armor,
		"eq_charm": eq_charm, "inv_ids": inv_ids, "inv_counts": inv_counts}


func from_dict(d: Dictionary) -> void:
	for k in d:
		if k in self:
			set(k, d[k])
