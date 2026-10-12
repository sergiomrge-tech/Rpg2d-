class_name TreasureCache
extends Node2D
## Treasure chest hidden at the points of interest of the expanded maps. Opens when the hero steps next to it, once.

const T := 64.0
const TABLES := {
	1: [["gold", 1.0, 25, 45], ["potion", 0.7, 1, 2]],
	2: [["gold", 1.0, 45, 80], ["potion", 0.8, 1, 2], ["ether", 0.6, 1, 1], ["hell_ember", 0.4, 1, 1]],
	3: [["gold", 1.0, 80, 130], ["potion", 1.0, 2, 3], ["ether", 0.8, 1, 2], ["hell_ember", 0.7, 1, 2]],
}
var cid := ""
var tier := 1
var level := 1
var opened := false
var _t := randf() * 10.0
var _glow: Sprite2D
var _lid := 0.0


static func spawn(c: Dictionary, lv: int) -> TreasureCache:
	var key: String = "cache_" + str(c["id"])
	if Game.flags.has(key):
		return null
	var n := TreasureCache.new()
	n.cid = str(c["id"])
	n.tier = int(c["tier"])
	n.level = lv
	n.z_as_relative = true
	Game.world.add_entity(n, Vector2(float(c["x"]), float(c["y"])))
	return n


func _ready() -> void:
	_glow = Util.glow(self, Color(1, 0.82, 0.35), 2.4, 0.3)
	_glow.position = Vector2(0, -0.35 * T)


func _process(dt: float) -> void:
	_t += dt
	if opened:
		_lid = minf(1.0, _lid + dt * 4.0)
		_glow.modulate.a = maxf(0.0, _glow.modulate.a - dt * 0.8)
		if _glow.modulate.a <= 0.01:
			queue_free()
		queue_redraw()
		return
	_glow.modulate.a = 0.22 + 0.12 * sin(_t * 3.0)
	queue_redraw()
	var p := Player.I
	if p != null and not p.dead and (p.global_position - global_position).length() < 1.15 * T:
		_open()


func _open() -> void:
	opened = true
	Game.flags["cache_" + cid] = true
	Sfx.play("coin", 0.6, 0.9)
	Sfx.play("pickup", 0.5, 1.2)
	Fx.heal(global_position + Vector2.UP * 0.3 * T)
	Fx.toast("Baú encontrado!", Color(1, 0.9, 0.5), global_position + Vector2.UP * 1.4 * T)
	var lv := maxi(1, level / 2)
	Loot.drop({"drops": TABLES[clampi(tier, 1, 3)]}, lv, global_position + Vector2(0, 0.4 * T))
	Loot.gear_drop(level, tier >= 3, global_position + Vector2(0.5 * T, 0.5 * T), 0.45 if tier >= 2 else 0.2)
	Game.save()


func _draw() -> void:
	var wood := Color(0.52, 0.3, 0.14)
	var dark := Color(0.28, 0.15, 0.07)
	var gold := Color(1.0, 0.8, 0.28)
	# soft shadow
	draw_rect(Rect2(-22, -4, 44, 8), Color(0, 0, 0, 0.25))
	# body
	draw_rect(Rect2(-20, -26, 40, 24), dark)
	draw_rect(Rect2(-18, -24, 36, 20), wood)
	draw_rect(Rect2(-18, -16, 36, 3), gold)
	# lid: lifts when opened
	var lift := _lid * 16.0
	draw_colored_polygon(PackedVector2Array([Vector2(-21, -26 - lift), Vector2(21, -26 - lift), Vector2(18, -38 - lift), Vector2(-18, -38 - lift)]), dark)
	draw_colored_polygon(PackedVector2Array([Vector2(-19, -27 - lift), Vector2(19, -27 - lift), Vector2(16, -36 - lift), Vector2(-16, -36 - lift)]), wood.lightened(0.1))
	draw_rect(Rect2(-3, -22, 6, 8), dark)
	draw_rect(Rect2(-2, -21, 4, 6), gold)
	if _lid > 0.2:
		draw_circle(Vector2(0, -28), 10.0 * _lid, Color(1, 0.9, 0.5, 0.5 * (1.0 - _lid * 0.5)))
