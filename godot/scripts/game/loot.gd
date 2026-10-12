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
