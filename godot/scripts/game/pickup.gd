class_name Pickup
extends Node2D
## Loot on the ground: bounces out, bobs, magnetises to the hero.

const T := 64.0
var item := ""
var count := 1
var t := 0.0
var z := 0.0
var vz := 0.0
var vxy := Vector2.ZERO
var icon: Sprite2D
var collecting := false


static func spawn(item_: String, count_: int, at: Vector2) -> void:
	var p := Pickup.new()
	p.item = item_
	p.count = count_
	p.vxy = Vector2.from_angle(randf() * TAU) * randf() * 1.6 * T
	p.vz = randf_range(5.0, 7.0)
	var def: Dictionary = Data.items[item_]
	var rar := int(def["rarity"])
	p.icon = Sprite2D.new()
	p.icon.texture = Sheets.icon(def["icon"])
	p.icon.scale = Vector2.ONE * 0.7
	p.add_child(p.icon)
	Util.glow(p, Data.RARITY_COLORS[rar], 2.2 if rar >= 2 else 1.2, 0.6 if rar >= 2 else 0.3)
	Util.make_shadow(p, 0.45, 0.16, 0.28)
	Game.world.add_entity(p, at)
	if rar >= 3:
		var beam := LightBeam.new()
		beam.color = Data.RARITY_COLORS[rar]
		beam.tall = 7.0 if rar >= 4 else 4.5
		p.add_child(beam)
		Sfx.play("legend" if rar >= 4 else "epic", 0.55, 1.0)
	if rar >= 2:
		Fx.toast(def["name"] + "!", Data.RARITY_COLORS[rar], at + Vector2.UP * 2.0 * T)


func _process(dt: float) -> void:
	t += dt
	if vz != 0.0 or z > 0.0:
		vz -= 22.0 * dt
		z += vz * dt
		global_position += vxy * dt
		if z <= 0.0:
			z = 0.0
			vz = -vz * 0.35 if absf(vz) > 2.0 else 0.0
			vxy *= 0.5
	icon.position = Vector2(0, -(z + 0.12 + sin(t * 3.0) * 0.06 + 0.35) * T)
	var p := Player.I
	if p == null or p.dead or t < 0.6:
		return
	var d := p.global_position + Vector2.UP * 0.4 * T - global_position
	if d.length() < 2.2 * T:
		collecting = true
	if collecting:
		global_position += d.normalized() * minf(d.length(), (6.0 + t * 4.0) * T * dt)
		if d.length() < 0.3 * T:
			p.gs.add(item, count)
			var def: Dictionary = Data.items[item]
			if Game.hud:
				Game.hud.loot_feed(def, count)
			Sfx.play("coin" if item == "gold" else "pickup", 0.45, randf_range(0.95, 1.1))
			queue_free()


## Column of light over epic / legendary drops so they can be spotted from afar.
class LightBeam extends Node2D:
	var color := Color.WHITE
	var tall := 5.0
	var t := 0.0

	func _ready() -> void:
		material = Util.additive()
		z_index = 5

	func _process(dt: float) -> void:
		t += dt
		queue_redraw()

	func _draw() -> void:
		var h := tall * 64.0
		var w := 26.0 + 5.0 * sin(t * 3.0)
		var a := 0.5 + 0.12 * sin(t * 4.0)
		var pts := PackedVector2Array([Vector2(-w, 0), Vector2(w, 0), Vector2(w * 0.35, -h), Vector2(-w * 0.35, -h)])
		var cols := PackedColorArray([Color(color, a), Color(color, a), Color(color, 0.0), Color(color, 0.0)])
		draw_polygon(pts, cols)
		var pts2 := PackedVector2Array([Vector2(-w * 0.35, 0), Vector2(w * 0.35, 0), Vector2(w * 0.1, -h * 0.8), Vector2(-w * 0.1, -h * 0.8)])
		var c2 := Color(1, 1, 1)
		draw_polygon(pts2, PackedColorArray([Color(c2, a), Color(c2, a), Color(c2, 0.0), Color(c2, 0.0)]))
