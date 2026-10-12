class_name GameState
extends RefCounted
## Persistent player progress (serialised to the save file).

var level := 1
var class_id := "warrior"  # legacy saves default to Ren's original style
var xp := 0
var gold := 10
var max_hp := 100.0
var base_mp := 50.0
var max_mp: float:
	get: return base_mp + bonus("mp")
	set(v): base_mp = v
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
var attr_pts := 0              # unspent attribute points
var skill_pts := 0             # unspent skill-tree points
var attrs := {}                # attribute -> points invested above the class base
var skills: Array = []         # learned tree nodes ("branch_tier")
var buffs := {}                # transient: name -> {"t": seconds, "eff": {...}}
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


func total_atk() -> float: return (atk + _gear("atk")) * (1.0 + bonus("atk_pct") / 100.0) + bonus("atk")
func total_mag() -> float: return (mag + _gear("mag")) * (1.0 + bonus("mag_pct") / 100.0) + bonus("mag")
func total_def() -> float: return float(HeroClasses.info(class_id)["defense"]) + _gear("defense") + bonus("def")
func hp_max() -> float: return max_hp + _gear("hp") + bonus("hp")


# ---------------------------------------------------------------- attributes and skill tree
func attr_inv(a: String) -> int:
	return int(attrs.get(a, 0))


func attr(a: String) -> int:
	return int(SkillTree.base(class_id)[a]) + attr_inv(a)


func _node_eff(sid: String) -> Dictionary:
	var parts := sid.split("_")
	return SkillTree.node(class_id, int(parts[0]), int(parts[1]))[1]


## Sum of one bonus key from attributes, learned skills and active buffs.
## Percent keys (atk_pct, crit, dodge, aspd...) are in percent points.
func bonus(key: String) -> float:
	var t := 0.0
	match key:
		"atk": t += attr_inv("str") * 1.6
		"mag": t += attr_inv("int") * 1.6
		"def": t += attr_inv("con") * 1.2
		"hp": t += attr_inv("con") * 7.0
		"mp": t += attr_inv("man") * 5.0
		"regen": t += attr_inv("int") * 0.06
		"dodge": t += attr_inv("agi") * 0.6
		"aspd": t += attr_inv("agi") * 1.0
		"mspd": t += attr_inv("agi") * 0.4
		"crit": t += attr_inv("sor") * 0.5
	for sid in skills:
		var eff := _node_eff(sid)
		if eff.has(key):
			t += float(eff[key])
	for b in buffs.values():
		if b["eff"].has(key):
			t += float(b["eff"][key])
	return t


func has_unlock(which: String) -> bool:
	for sid in skills:
		if _node_eff(sid).get("unlock", "") == which:
			return true
	return false


func crit_chance() -> float: return float(HeroClasses.info(class_id)["crit"]) + bonus("crit") / 100.0
func dodge_chance() -> float: return minf(0.35, bonus("dodge") / 100.0)
func attack_speed() -> float: return 1.0 + minf(0.8, bonus("aspd") / 100.0)
func move_mult() -> float: return 1.0 + minf(0.4, bonus("mspd") / 100.0)
func mp_regen() -> float: return 1.2 + bonus("regen")
func cooldown_mult() -> float: return 1.0 - minf(0.5, bonus("cdr") / 100.0)
func lifesteal() -> float: return bonus("lifesteal") / 100.0
func damage_taken_mult() -> float: return 1.0 - minf(0.6, bonus("dmg_red") / 100.0)
func xp_mult() -> float: return 1.0 + bonus("xp_pct") / 100.0
func heal_mult() -> float: return 1.0 + bonus("heal_pct") / 100.0


func add_attr(a: String) -> bool:
	if attr_pts <= 0:
		return false
	attr_pts -= 1
	attrs[a] = attr_inv(a) + 1
	return true


func skill_known(branch: int, tier: int) -> bool:
	return skills.has(SkillTree.node_id(branch, tier))


## "" when the node can be learned now, otherwise the reason.
func skill_block(branch: int, tier: int) -> String:
	if skill_known(branch, tier):
		return "Já aprendida"
	if level < int(SkillTree.TIER_LEVELS[tier]):
		return "Requer nível %d" % int(SkillTree.TIER_LEVELS[tier])
	if tier > 0 and not skill_known(branch, tier - 1):
		return "Aprenda a habilidade anterior"
	if skill_pts < int(SkillTree.TIER_COST[tier]):
		return "Faltam pontos de habilidade"
	return ""


func learn_skill(branch: int, tier: int) -> bool:
	if skill_block(branch, tier) != "":
		return false
	skill_pts -= int(SkillTree.TIER_COST[tier])
	skills.append(SkillTree.node_id(branch, tier))
	return true


func respec_cost() -> int:
	return 100 * level


## Refund every attribute and skill point (costs gold); gear that no longer fits is taken off.
func respec() -> bool:
	if gold < respec_cost():
		return false
	gold -= respec_cost()
	attrs = {}
	skills = []
	buffs = {}
	attr_pts = (level - 1) * SkillTree.ATTR_PER_LEVEL
	skill_pts = level - 1
	for slot in [1, 2, 3]:
		var id := equipped(slot)
		if id != "" and req_block(id) != "":
			unequip(slot)
	return true


func req_of(id: String) -> Dictionary:
	return Data.items[id].get("req", {}) if Data.items.has(id) else {}


## "" when the hero meets the item's attribute requirements, else e.g. "Requer FOR 20, CON 14".
func req_block(id: String) -> String:
	var miss := PackedStringArray()
	var r := req_of(id)
	for a in r:
		if attr(a) < int(r[a]):
			miss.append("%s %d" % [SkillTree.ATTR_ABBR[a], int(r[a])])
	return "" if miss.is_empty() else "Requer " + ", ".join(miss)


func add_buff(name: String, secs: float, eff: Dictionary) -> void:
	buffs[name] = {"t": secs, "eff": eff}


func tick_buffs(dt: float) -> void:
	for k in buffs.keys():
		buffs[k]["t"] = float(buffs[k]["t"]) - dt
		if float(buffs[k]["t"]) <= 0.0:
			buffs.erase(k)


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
	if not HeroClasses.can_equip(class_id, Data.items[id]) or req_block(id) != "":
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
		base_mp += float(growth["mp_gain"])
		attr_pts += SkillTree.ATTR_PER_LEVEL
		skill_pts += 1
		# Legacy max_st is retained solely for backwards-compatible save files.
		atk += float(growth["atk_gain"])
		mag += float(growth["mag_gain"])
		up = true
	return up


func to_dict() -> Dictionary:
	return {"level": level, "class_id": class_id, "xp": xp, "gold": gold, "max_hp": max_hp, "max_mp": base_mp, "max_st": max_st, "atk": atk, "mag": mag,
		"spark_tier": spark_tier, "sword_tier": sword_tier, "guild_rank": guild_rank, "eq_weapon": eq_weapon, "eq_armor": eq_armor,
		"eq_charm": eq_charm, "inv_ids": inv_ids, "inv_counts": inv_counts, "enh": enh, "ng_plus": ng_plus,
		"attr_pts": attr_pts, "skill_pts": skill_pts, "attrs": attrs, "skills": skills, "stats_v": 1}


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
	attrs = {}
	for k in d.get("attrs", {}):
		attrs[k] = int(d["attrs"][k])
	skills = []
	for k in d.get("skills", []):
		skills.append(str(k))
	buffs = {}
	if not d.has("stats_v"):      # save from before attributes/skills: grant what the levels would have given
		attr_pts = (level - 1) * SkillTree.ATTR_PER_LEVEL
		skill_pts = level - 1
	if not HeroClasses.valid(class_id):
		class_id = "warrior"
