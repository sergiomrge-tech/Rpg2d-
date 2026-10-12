class_name Fx
extends RefCounted
## Visual effect helpers (procedural vector/particle FX + sprite-sheet FX).

static var _glow: GradientTexture2D
static var _add_mat: CanvasItemMaterial
static var _sheets := {}
static var font_num: Font

static func glow_tex() -> GradientTexture2D:
	if _glow == null:
		_glow = GradientTexture2D.new()
		_glow.width = 64
		_glow.height = 64
		_glow.fill = GradientTexture2D.FILL_RADIAL
		_glow.fill_from = Vector2(0.5, 0.5)
		_glow.fill_to = Vector2(1.0, 0.5)
		var g := Gradient.new()
		g.set_color(0, Color(1, 1, 1, 1))
		g.add_point(0.35, Color(1, 1, 1, 0.55))
		g.set_color(g.get_point_count() - 1, Color(1, 1, 1, 0))
		_glow.gradient = g
	return _glow

static func add_mat() -> CanvasItemMaterial:
	if _add_mat == null:
		_add_mat = CanvasItemMaterial.new()
		_add_mat.blend_mode = CanvasItemMaterial.BLEND_MODE_ADD
	return _add_mat

static func layer(w: World) -> Node2D:
	return w.fx_layer

# ------------------------------------------------------------------ particles
static func burst(w: World, pos: Vector2, colors: Array, n := 10, speed := 90.0, life := 0.5, size := 2.0, grav := 0.0, additive := true) -> void:
	for i in n:
		var s := Sprite2D.new()
		s.texture = glow_tex()
		var c: Color = colors[randi() % colors.size()]
		s.modulate = c
		s.scale = Vector2.ONE * (size / 16.0) * randf_range(0.6, 1.3)
		if additive:
			s.material = add_mat()
		s.position = pos
		s.z_index = 20
		layer(w).add_child(s)
		var a := randf() * TAU
		var v := Vector2(cos(a), sin(a)) * speed * randf_range(0.3, 1.0)
		var tw := s.create_tween()
		var l := life * randf_range(0.6, 1.2)
		tw.set_parallel(true)
		tw.tween_property(s, "position", pos + v * l + Vector2(0, grav * l * l * 0.5), l).set_ease(Tween.EASE_OUT).set_trans(Tween.TRANS_QUAD)
		tw.tween_property(s, "modulate:a", 0.0, l).set_delay(l * 0.3)
		tw.tween_property(s, "scale", s.scale * 0.2, l)
		tw.chain().tween_callback(s.queue_free)

static func embers(w: World, pos: Vector2, n := 4) -> void:
	burst(w, pos + Vector2(randf_range(-4, 4), 0), [Color("ff8a2a"), Color("ffd84a")], n, 30.0, 0.6, 3.0, -60.0)

static func glow_flash(w: World, pos: Vector2, color: Color, size := 80.0, dur := 0.25) -> void:
	var s := Sprite2D.new()
	s.texture = glow_tex()
	s.modulate = Color(color, 0.9)
	s.material = add_mat()
	s.position = pos
	s.scale = Vector2.ONE * size / 64.0 * 0.4
	s.z_index = 22
	layer(w).add_child(s)
	var tw := s.create_tween()
	tw.set_parallel(true)
	tw.tween_property(s, "scale", Vector2.ONE * size / 64.0, dur).set_ease(Tween.EASE_OUT)
	tw.tween_property(s, "modulate:a", 0.0, dur)
	tw.chain().tween_callback(s.queue_free)

# ------------------------------------------------------------------ procedural shapes
class RingFx extends Node2D:
	var r0 := 4.0
	var r1 := 60.0
	var col := Color.WHITE
	var dur := 0.4
	var t := 0.0
	var width := 3.0
	var filled := 0.0
	func _process(dt: float) -> void:
		t += dt
		if t >= dur:
			queue_free()
		queue_redraw()
	func _draw() -> void:
		var f: float = clampf(t / dur, 0.0, 1.0)
		var e: float = 1.0 - pow(1.0 - f, 3.0)
		var r: float = lerpf(r0, r1, e)
		var a: float = (1.0 - f)
		if filled > 0.0:
			draw_circle(Vector2.ZERO, r, Color(col, filled * a * 0.5))
		draw_arc(Vector2.ZERO, r, 0, TAU, 48, Color(col, a), width * (1.0 - f * 0.6), true)
		draw_arc(Vector2.ZERO, r * 0.86, 0, TAU, 48, Color(1, 1, 1, a * 0.7), width * 0.5, true)

static func ring(w: World, pos: Vector2, r1: float, color: Color, dur := 0.45, filled := 0.0, iso := true) -> void:
	var n := RingFx.new()
	n.position = pos
	n.r1 = r1
	n.col = color
	n.dur = dur
	n.filled = filled
	n.z_index = 4
	n.material = add_mat()
	if iso:
		n.scale = Vector2(1, 0.62)
	layer(w).add_child(n)

class SlashFx extends Node2D:
	var ang := 0.0
	var radius := 40.0
	var span := 2.2
	var col := Color.WHITE
	var dur := 0.22
	var t := 0.0
	var flip := false
	var thick := 9.0
	func _process(dt: float) -> void:
		t += dt
		if t >= dur:
			queue_free()
		queue_redraw()
	func _draw() -> void:
		var f: float = clampf(t / dur, 0.0, 1.0)
		var head: float = clampf(f * 1.6, 0.0, 1.0)
		var tail: float = clampf((f - 0.25) * 1.5, 0.0, 1.0)
		var n := 20
		var pts_o := PackedVector2Array()
		var pts_i := PackedVector2Array()
		var s := -1.0 if flip else 1.0
		for i in n + 1:
			var u: float = lerpf(tail, head, float(i) / n)
			var a: float = ang + s * (u - 0.5) * span
			var wmul: float = sin(PI * float(i) / n)
			var th: float = thick * wmul * (1.0 - f * 0.5)
			pts_o.append(Vector2(cos(a), sin(a)) * (radius + th * 0.5))
			pts_i.append(Vector2(cos(a), sin(a)) * (radius - th * 0.5))
		var poly := PackedVector2Array()
		poly.append_array(pts_o)
		pts_i.reverse()
		poly.append_array(pts_i)
		if poly.size() >= 3:
			draw_colored_polygon(poly, Color(col, 0.75 * (1.0 - f * 0.7)))
		# bright core
		var core := PackedVector2Array()
		for i in n + 1:
			var u2: float = lerpf(tail, head, float(i) / n)
			var a2: float = ang + s * (u2 - 0.5) * span
			core.append(Vector2(cos(a2), sin(a2)) * radius)
		if core.size() >= 2:
			draw_polyline(core, Color(1, 1, 1, 0.95 * (1.0 - f)), 2.2, true)

static func slash(w: World, pos: Vector2, angle: float, radius := 40.0, color := Color("bfe4ff"), span := 2.2, flip := false, dur := 0.22, thick := 9.0) -> void:
	var n := SlashFx.new()
	n.position = pos
	n.ang = angle
	n.radius = radius
	n.col = color
	n.span = span
	n.flip = flip
	n.dur = dur
	n.thick = thick
	n.z_index = 21
	n.material = add_mat()
	layer(w).add_child(n)

class BoltFx extends Node2D:
	var pts: Array = []
	var col := Color("ffe84a")
	var t := 0.0
	var dur := 0.3
	var jag := 7.0
	func _process(dt: float) -> void:
		t += dt
		if t >= dur:
			queue_free()
		queue_redraw()
	func _draw() -> void:
		var f: float = clampf(t / dur, 0.0, 1.0)
		for k in range(pts.size() - 1):
			var a: Vector2 = pts[k]
			var b: Vector2 = pts[k + 1]
			var seg := PackedVector2Array([a])
			var n: int = maxi(3, int(a.distance_to(b) / 8.0))
			for i in range(1, n):
				var p: Vector2 = a.lerp(b, float(i) / n)
				var nrm: Vector2 = (b - a).orthogonal().normalized()
				seg.append(p + nrm * randf_range(-jag, jag) * (1.0 - f))
			seg.append(b)
			draw_polyline(seg, Color(col, 0.35 * (1.0 - f)), 9.0, true)
			draw_polyline(seg, Color(col, 0.9 * (1.0 - f)), 4.0, true)
			draw_polyline(seg, Color(1, 1, 1, 1.0 - f), 1.8, true)

static func bolt(w: World, pts: Array, color := Color("ffe84a"), dur := 0.3) -> void:
	var n := BoltFx.new()
	n.pts = pts
	n.col = color
	n.dur = dur
	n.z_index = 25
	n.material = add_mat()
	layer(w).add_child(n)

class RuneFx extends Node2D:
	var col := Color.WHITE
	var r := 46.0
	var dur := 0.7
	var t := 0.0
	var spin := 1.0
	var sides := 3
	func _process(dt: float) -> void:
		t += dt
		if t >= dur:
			queue_free()
		queue_redraw()
	func _draw() -> void:
		var f: float = clampf(t / dur, 0.0, 1.0)
		var a: float = sin(PI * f) * 0.95
		var grow: float = 0.55 + 0.45 * (1.0 - pow(1.0 - minf(1.0, f * 2.5), 3.0))
		var rr: float = r * grow
		var c := Color(col, a)
		draw_arc(Vector2.ZERO, rr, 0, TAU, 56, c, 2.0, true)
		draw_arc(Vector2.ZERO, rr * 0.82, 0, TAU, 56, Color(col, a * 0.7), 1.2, true)
		draw_arc(Vector2.ZERO, rr * 1.08, 0, TAU, 56, Color(col, a * 0.4), 1.0, true)
		var rot: float = t * spin * 2.4
		for k in 2:
			var pts := PackedVector2Array()
			for i in sides + 1:
				pts.append(Vector2.from_angle(rot + float(i) / sides * TAU + k * PI / sides) * rr * 0.82)
			draw_polyline(pts, Color(col, a * 0.85), 1.4, true)
		for i in 12:
			var ang: float = -rot * 0.6 + float(i) / 12.0 * TAU
			var p0 := Vector2.from_angle(ang) * rr * 0.86
			var p1 := Vector2.from_angle(ang) * rr * (1.0 if i % 3 else 1.1)
			draw_line(p0, p1, Color(col, a * 0.8), 1.2)
		draw_circle(Vector2.ZERO, rr * 0.12, Color(1, 1, 1, a * 0.6))

static func rune(w: World, pos: Vector2, color: Color, r := 46.0, dur := 0.7, sides := 3, spin := 1.0) -> void:
	var n := RuneFx.new()
	n.position = pos
	n.col = color
	n.r = r
	n.dur = dur
	n.sides = sides
	n.spin = spin
	n.z_index = 2
	n.scale = Vector2(1, 0.62)
	n.material = add_mat()
	layer(w).add_child(n)

class ShieldFx extends Node2D:
	var owner_p: Player
	func _process(_dt: float) -> void:
		visible = owner_p != null and owner_p.shield > 0.0
		if visible:
			queue_redraw()
	func _draw() -> void:
		var t: float = Time.get_ticks_msec() / 1000.0
		var a: float = clampf(owner_p.shield_t / 2.0, 0.3, 1.0)
		var c := Color("9ad8ff")
		draw_circle(Vector2(0, -22), 24.0, Color(c, 0.13 * a))
		draw_arc(Vector2(0, -22), 24.0, 0, TAU, 48, Color(c, 0.9 * a), 2.0, true)
		for i in 6:
			var ang: float = t * 1.2 + i * TAU / 6.0
			var p := Vector2(0, -22) + Vector2.from_angle(ang) * 24.0
			var q := Vector2(0, -22) + Vector2.from_angle(ang + TAU / 6.0) * 24.0
			draw_line(p, q, Color(1, 1, 1, 0.55 * a), 1.0)
			draw_circle(p, 1.6, Color(1, 1, 1, 0.9 * a))

# ------------------------------------------------------------------ floating text
class FloatText extends Node2D:
	var txt := ""
	var col := Color.WHITE
	var big := false
	var t := 0.0
	var drift := Vector2(0, -34)
	func _process(dt: float) -> void:
		t += dt
		if t > 0.9:
			queue_free()
		position += drift * dt * (1.0 - t)
		queue_redraw()
	func _draw() -> void:
		var f: Font = Fx.font_num
		var sz: int = 22 if big else 15
		var a: float = 1.0 if t < 0.55 else (1.0 - (t - 0.55) / 0.35)
		var sc: float = 1.0 + (0.5 if big else 0.2) * maxf(0.0, 1.0 - t * 6.0)
		draw_set_transform(Vector2.ZERO, 0, Vector2(sc, sc) * 0.5)
		var w: float = f.get_string_size(txt, HORIZONTAL_ALIGNMENT_LEFT, -1, sz).x
		var p := Vector2(-w / 2.0, 0)
		draw_string_outline(f, p, txt, HORIZONTAL_ALIGNMENT_LEFT, -1, sz, 6, Color(0.05, 0.02, 0.1, a))
		draw_string(f, p, txt, HORIZONTAL_ALIGNMENT_LEFT, -1, sz, Color(col, a))

static func text(w: World, pos: Vector2, s: String, color := Color.WHITE, big := false) -> void:
	if font_num == null:
		font_num = load("res://assets/fonts/cinzel-latin-700-normal.woff2")
	var n := FloatText.new()
	n.position = pos + Vector2(randf_range(-6, 6), 0)
	n.txt = s
	n.col = color
	n.big = big
	n.z_index = 60
	layer(w).add_child(n)

# ------------------------------------------------------------------ sprite-sheet FX (assets/fx/*.png + fx.json)
static func sheet(name: String) -> SpriteFrames:
	if _sheets.has(name):
		return _sheets[name]
	var meta: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("res://assets/fx/fx.json"))
	if not meta.has(name):
		return null
	var m: Dictionary = meta[name]
	var tex: Texture2D = load("res://assets/fx/%s.png" % name)
	var sf := SpriteFrames.new()
	sf.remove_animation("default")
	sf.add_animation("a")
	sf.set_animation_speed("a", float(m["fps"]))
	sf.set_animation_loop("a", bool(m.get("loop", false)))
	for i in int(m["frames"]):
		var at := AtlasTexture.new()
		at.atlas = tex
		at.region = Rect2(i * int(m["w"]), 0, int(m["w"]), int(m["h"]))
		sf.add_frame("a", at)
	_sheets[name] = sf
	return sf

static func anim(w: World, name: String, pos: Vector2, scale_f := 1.0, rot := 0.0, color := Color.WHITE, additive := true, z := 24, flip_h := false) -> AnimatedSprite2D:
	var sf := sheet(name)
	if sf == null:
		return null
	var s := AnimatedSprite2D.new()
	s.sprite_frames = sf
	s.position = pos
	s.scale = Vector2.ONE * scale_f
	s.rotation = rot
	s.modulate = color
	s.flip_h = flip_h
	s.z_index = z
	if additive:
		s.material = add_mat()
	layer(w).add_child(s)
	s.play("a")
	if not sf.get_animation_loop("a"):
		s.animation_finished.connect(s.queue_free)
	return s

# ------------------------------------------------------------------ global feel
static func hitstop(dur := 0.05) -> void:
	if Engine.time_scale < 0.5:
		return
	Engine.time_scale = 0.06
	var t: SceneTreeTimer = (Engine.get_main_loop() as SceneTree).create_timer(dur, true, false, true)
	t.timeout.connect(func(): Engine.time_scale = 1.0)

static func shake(w: World, amount := 4.0) -> void:
	w.cam_shake = maxf(w.cam_shake, amount)
