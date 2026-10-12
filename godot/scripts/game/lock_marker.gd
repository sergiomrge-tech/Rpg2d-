class_name LockMarker
extends Node2D
## Reticle drawn around the locked-on enemy: rotating corner brackets, a pulsing ring and a chevron above its head.

var radius := 44.0
var head := 120.0
var boss := false
var _t := 0.0


func _ready() -> void:
	z_index = 60
	material = Util.additive()


func _process(dt: float) -> void:
	_t += dt
	queue_redraw()


func _draw() -> void:
	var col := Color(1.0, 0.35, 0.28) if not boss else Color(1.0, 0.7, 0.2)
	var r := radius * (1.0 + 0.05 * sin(_t * 6.0))
	var c := Vector2(0, -radius * 0.6)
	var rot := _t * 1.3
	for i in 4:
		var a := rot + i * PI * 0.5
		draw_arc(c, r, a - 0.32, a + 0.32, 10, col, 5.0)
	draw_arc(c, r * 0.72, 0.0, TAU, 28, Color(col, 0.35), 2.0)
	var bob := sin(_t * 5.0) * 4.0
	draw_colored_polygon(PackedVector2Array([Vector2(-12, -head + bob), Vector2(12, -head + bob), Vector2(0, -head + 16 + bob)]), col)
	draw_polyline(PackedVector2Array([Vector2(-12, -head + bob), Vector2(12, -head + bob), Vector2(0, -head + 16 + bob), Vector2(-12, -head + bob)]), Color(1, 1, 1, 0.7), 2.0)
