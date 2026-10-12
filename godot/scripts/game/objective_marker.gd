class_name ObjectiveMarker
extends Node2D
## World-space quest marker: bobbing gold diamond with a pulsing glow over the target,
## or a bouncing chevron + ground ring at the map exit that leads toward it.

const T := 64.0
var kind := "target"
var _t := 0.0
var _glow: Sprite2D


func _ready() -> void:
	z_index = 180
	_glow = Util.glow(self, Color(1, 0.85, 0.4), 3.2, 0.5)


func refresh(show_it: bool, at: Vector2, k: String) -> void:
	visible = show_it
	kind = k
	if show_it:
		global_position = at


func _process(dt: float) -> void:
	_t += dt
	var pulse := 0.5 + 0.5 * sin(_t * 3.0)
	_glow.modulate.a = 0.28 + 0.22 * pulse
	_glow.scale = Vector2.ONE * (3.0 + 0.5 * pulse) * T / 128.0
	_glow.position = Vector2(0, -2.5 * T if kind == "target" else -0.2 * T)
	queue_redraw()


func _draw() -> void:
	var gold := Color(1.0, 0.82, 0.3)
	var ink := Color(0.25, 0.12, 0.05)
	if kind == "target":
		var y := -2.9 * T + sin(_t * 4.0) * 7.0
		var d := PackedVector2Array([Vector2(0, y - 22), Vector2(15, y), Vector2(0, y + 22), Vector2(-15, y)])
		var o := PackedVector2Array([Vector2(0, y - 27), Vector2(20, y), Vector2(0, y + 27), Vector2(-20, y)])
		draw_colored_polygon(o, ink)
		draw_colored_polygon(d, gold)
		draw_colored_polygon(PackedVector2Array([Vector2(0, y - 22), Vector2(15, y), Vector2(0, y)]), Color(1, 0.95, 0.7))
		# ground ring that expands and fades
		var r := fmod(_t * 0.8, 1.0)
		draw_arc(Vector2.ZERO, (0.4 + r * 1.3) * T, 0, TAU, 40, Color(gold.r, gold.g, gold.b, 0.7 * (1.0 - r)), 4.0)
	else:
		var y := -1.5 * T + absf(sin(_t * 4.0)) * 14.0
		for i in 2:
			var yy := y - i * 20.0
			var c := Color(gold.r, gold.g, gold.b, 1.0 - i * 0.45)
			draw_polyline(PackedVector2Array([Vector2(-22, yy - 14), Vector2(0, yy + 6), Vector2(22, yy - 14)]), ink, 12.0)
			draw_polyline(PackedVector2Array([Vector2(-22, yy - 14), Vector2(0, yy + 6), Vector2(22, yy - 14)]), c, 7.0)
		var r := fmod(_t * 0.8, 1.0)
		draw_arc(Vector2.ZERO, (0.6 + r * 1.5) * T, 0, TAU, 40, Color(gold.r, gold.g, gold.b, 0.7 * (1.0 - r)), 4.0)
