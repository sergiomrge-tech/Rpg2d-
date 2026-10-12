class_name Loot
extends RefCounted
## Drop tables scale with demon level: more gold, better odds for rare materials.


static func drop(def: Dictionary, level: int, at: Vector2) -> void:
	for d in def["drops"]:
		var item: String = d[0]
		var c := float(d[1]) * (1.0 if item == "gold" else 1.0 + 0.25 * (level - 1))
		if randf() > c:
			continue
		var n := randi_range(int(d[2]), int(d[3]))
		if item == "gold":
			n = roundi(n * (1.0 + 0.6 * (level - 1)))
		Pickup.spawn(item, n, at)
	var boss := bool(def.get("boss", false))
	gear_drop(level, boss, at)
	if boss:                     # bosses drop a second piece, 60% of the time
		gear_drop(level, true, at, 0.6)


## Random equipment (Comum → Lendário). Stronger monsters and bosses roll better rarities.
static func rarity_for(level: int, boss: bool) -> int:
	var w := [maxf(8.0, 60.0 - level * 2.5), 28.0, 4.0 + level * 0.9, maxf(0.0, (level - 7) * 0.7), maxf(0.0, (level - 15) * 0.3)]
	if boss:
		w = [0.0, 10.0, 45.0, 35.0 + level, maxf(5.0, (level - 8) * 1.2)]
	var total := 0.0
	for x in w:
		total += x
	var r := randf() * total
	for i in 5:
		r -= w[i]
		if r <= 0.0:
			return i
	return 0


static func gear_drop(level: int, boss: bool, at: Vector2, chance := -1.0) -> void:
	if chance < 0.0:
		chance = 1.0 if boss else 0.06 + 0.004 * level
	if randf() > chance:
		return
	var id := roll_gear(level, boss)
	if id != "":
		Pickup.spawn(id, 1, at + Vector2(randf_range(-20, 20), 10))


static func roll_gear(level: int, boss: bool) -> String:
	var r := rarity_for(level, boss)
	var cls := "warrior"
	if Player.I != null:
		cls = Player.I.gs.class_id
	var fam := ["ar", "ch"]
	var wt := str(HeroClasses.info(cls)["weapon"])
	if wt != "none":
		fam = ["ar", "ch", "w", "w"]       # a class that wields weapons finds them more often
	var f: String = fam[randi() % fam.size()]
	if f == "w":
		f = {"sword": "sw", "bow": "bw", "dual_daggers": "dg"}.get(wt, "sw")
	var id := "%s_%d" % [f, r]
	return id if Data.items.has(id) else ""
