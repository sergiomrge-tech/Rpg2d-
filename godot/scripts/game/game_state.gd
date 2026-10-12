class_name GameState
extends RefCounted
## Persistent player progress (serialised to the save file).

var level := 1
var class_id := "warrior"  # legacy saves default to Ren's original style
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
var enh := {}                  # item id -> forge level (+0..+5)
var ng_plus := 0               # completed playthroughs (Novo Jogo+)

const MAX_ENH := 5
const ENH_BONUS := 0.12
const SET_NAMES := ["Aventureiro", "Veterano", "Rúnico", "Alvorecer", "Lendário"]


func enh_level(id: String) -> int:
	return int(enh.get(id, 0))


## Stat of one item including its forge level.
func item_stat(id: String, key: String) -> float:
	if id == "" or not Data.items.has(id):
		return 0.0
	return float(Data.items[id].get(key, 0)) * (1.0 + ENH_BONUS * enh_level(id))


func _gear(key: String) -> float:
	var t := 0.0
	for id in [eq_weapon, eq_armor, eq_charm]:
		t += item_stat(id, key)
	var sb := set_bonus()
	return t + float(sb["stats"].get(key, 0.0))


## Equipped pieces from the same family (same rarity tier): 2 pieces +PV, 3 pieces +ATQ/MAG/DEF.
func set_bonus() -> Dictionary:
	var counts := {}
	for id in [eq_weapon, eq_armor, eq_charm]:
		if id != "" and Data.items.has(id) and Data.items[id].has("set_tier"):
			var t := int(Data.items[id]["set_tier"])
			counts[t] = int(counts.get(t, 0)) + 1
	var best := -1
	var n := 0
	for t in counts:
		if int(counts[t]) > n:
			n = int(counts[t])
			best = int(t)
	var stats := {}
	if best >= 0 and n >= 2:
		stats["hp"] = 10.0 * (best + 1)
	if best >= 0 and n >= 3:
		stats["atk"] = 3.0 * (best + 1)
		stats["mag"] = 3.0 * (best + 1)
		stats["defense"] = 2.0 * (best + 1)
	return {"name": SET_NAMES[best] if best >= 0 else "", "count": n, "tier": best, "stats": stats}


## Special power of a complete (3-piece) set.
const SET_POWERS := ["xp", "gold", "bolt", "heal", "meteor"]
const SET_POWER_TEXT := {
	"xp": "+10% EXP", "gold": "+15% ouro", "bolt": "12% de chance de raio ao acertar",
	"heal": "cura 4% da vida ao abater", "meteor": "10% de chance de meteoro ao acertar",
}


func set_power() -> String:
	var sb := set_bonus()
	if int(sb["count"]) >= 3 and int(sb["tier"]) >= 0:
		return SET_POWERS[int(sb["tier"])]
	return ""


## Blacksmith: gold (+ embers from +4) to raise a piece one forge level.
func forge_cost(id: String) -> Dictionary:
	var lv := enh_level(id)
	if id == "" or lv >= MAX_ENH:
		return {}
	var value := float(Data.items[id].get("value", 40))
	return {"gold": roundi(maxf(15.0, value * 0.35) * (lv + 1)), "ember": maxi(0, lv - 2)}


func can_forge(id: String) -> bool:
	var c := forge_cost(id)
	return not c.is_empty() and gold >= int(c["gold"]) and count("hell_ember") >= int(c["ember"])


func forge(id: String) -> bool:
	if not can_forge(id):
		return false
	var c := forge_cost(id)
	gold -= int(c["gold"])
	for i in int(c["ember"]):
		take("hell_ember")
	enh[id] = enh_level(id) + 1
	return true


func total_atk() -> float: return atk + _gear("atk")
func total_mag() -> float: return mag + _gear("mag")
func total_def() -> float: return float(HeroClasses.info(class_id)["defense"]) + _gear("defense")
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
	if not Data.items.has(id) or int(Data.items[id]["slot"]) == 0:
		return false
	if not HeroClasses.can_equip(class_id, Data.items[id]):
		return false
	if not take(id):
		return false
	var slot := int(Data.items[id]["slot"])
	var old := equipped(slot)
	if slot == 1: eq_weapon = id
	elif slot == 2: eq_armor = id
	else: eq_charm = id
	if old != "" and old != "rusty_sword":
		add(old, 1)
	return true


## Take a piece off and put it back in the bag.
func unequip(slot: int) -> bool:
	var id := equipped(slot)
	if id == "":
		return false
	if slot == 1: eq_weapon = ""
	elif slot == 2: eq_armor = ""
	else: eq_charm = ""
	add(id, 1)
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
		var growth := HeroClasses.info(class_id)
		max_hp += float(growth["hp_gain"])
		max_mp += float(growth["mp_gain"])
		# Legacy max_st is retained solely for backwards-compatible save files.
		atk += float(growth["atk_gain"])
		mag += float(growth["mag_gain"])
		up = true
	return up


func to_dict() -> Dictionary:
	return {"level": level, "class_id": class_id, "xp": xp, "gold": gold, "max_hp": max_hp, "max_mp": max_mp, "max_st": max_st, "atk": atk, "mag": mag,
		"spark_tier": spark_tier, "sword_tier": sword_tier, "guild_rank": guild_rank, "eq_weapon": eq_weapon, "eq_armor": eq_armor,
		"eq_charm": eq_charm, "inv_ids": inv_ids, "inv_counts": inv_counts, "enh": enh, "ng_plus": ng_plus}


func from_dict(d: Dictionary) -> void:
	# Old saves have no class_id. They continue as the original Warrior.
	class_id = "warrior"
	for k in d:
		if k in self:
			set(k, d[k])
	enh = {}
	for k in d.get("enh", {}):
		enh[k] = int(d["enh"][k])
	ng_plus = int(d.get("ng_plus", 0))
	if not HeroClasses.valid(class_id):
		class_id = "warrior"
