class_name Pickup
extends Node2D
## Dropped gold / items / hearts with arc physics & magnet pickup.

var kind := "gold"
var item_id := ""
var amount := 1
var gear: Dictionary = {}
var world: World
var z := 0.0
var vz := 130.0
var vel := Vector2.ZERO
var age := 0.0
var magnet := false
var icon: Sprite2D
var glow: Sprite2D
var bob_ph := randf() * 6.0

func _ready() -> void:
	vel = Vector2.from_angle(randf() * TAU) * randf_range(25, 55)
	glow = Sprite2D.new()
	glow.texture = Fx.glow_tex()
	glow.material = Fx.add_mat()
	glow.scale = Vector2(0.55, 0.55)
	glow.z_index = -1
	add_child(glow)
	icon = Sprite2D.new()
	icon.texture = IconLib.get_icon(_icon_name())
	icon.scale = Vector2(0.5, 0.5)
	add_child(icon)
	var col := Color("ffd84a")
	match kind:
		"heart": col = Color("ff5a7a")
		"mana": col = Color("5aa8ff")
		"item": col = Color("ffffff")
		"gear": col = Data.RARITY_COLORS[int(gear.get("rar", 0))]
	glow.modulate = Color(col, 0.55)

func _icon_name() -> String:
	match kind:
		"gold": return "coin"
		"heart": return "heart"
		"mana": return "mana_orb"
		"gear": return str(Data.GEAR[item_id]["icon"])
		_: return str(Game.item_def(item_id)["icon"])

func _process(dt: float) -> void:
	age += dt
	if z > 0.0 or vz > 0.0:
		vz -= 420.0 * dt
		z += vz * dt
		if z < 0.0:
			z = 0.0
			vz = -vz * 0.4 if vz < -50.0 else 0.0
		position += vel * dt
		vel *= 0.96
	var p := world.player
	if p == null or p.dead:
		return
	var d := p.global_position + Vector2(0, -10) - global_position
	if age > 0.45 and d.length() < (60.0 if kind != "gear" else 34.0):
		magnet = true
	if magnet:
		position += d.normalized() * 220.0 * dt
	icon.position = Vector2(0, -8 - z + sin(age * 4.0 + bob_ph) * (2.0 if z <= 0.0 else 0.0))
	glow.position = icon.position
	glow.scale = Vector2.ONE * (0.5 + 0.08 * sin(age * 5.0 + bob_ph))
	if age > 0.4 and d.length() < 14.0:
		_collect()
	if age > 90.0:
		queue_free()

func _collect() -> void:
	match kind:
		"gold":
			Game.gold += amount
			Sfx.play("coin", -4.0, randf_range(0.95, 1.15))
			Fx.text(world, global_position + Vector2(0, -20), "+%d" % amount, Color("ffd84a"))
		"heart":
			world.player.heal(float(amount))
			Sfx.play("pickup", -4.0)
		"mana":
			Game.mp = minf(float(Game.stats()["mp"]), Game.mp + amount)
			Fx.text(world, global_position + Vector2(0, -20), "+%d MP" % amount, Color("7ab8ff"))
			Sfx.play("pickup", -4.0)
		"gear":
			var g := Game.add_gear(item_id, int(gear["rar"]), gear.get("mods", {}))
			var nm := Game.gear_name(g)
			Game.toast.emit("%s (%s)" % [nm, Data.RARITY_NAMES[int(g["rar"])]], str(Data.GEAR[item_id]["icon"]), Data.RARITY_COLORS[int(g["rar"])])
			Sfx.play("chest" if int(g["rar"]) >= 2 else "pickup", -3.0)
			if int(g["rar"]) >= 2:
				Fx.glow_flash(world, global_position, Data.RARITY_COLORS[int(g["rar"])], 120.0, 0.5)
		_:
			Game.add_item(item_id, amount)
			Game.toast.emit("%s%s" % [Game.item_def(item_id)["name"], (" x%d" % amount) if amount > 1 else ""], str(Game.item_def(item_id)["icon"]), Color.WHITE)
			Sfx.play("pickup", -3.0)
			world.story_item_picked(item_id)
	queue_free()
