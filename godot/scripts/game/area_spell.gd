class_name AreaSpell
extends Node2D
## Mage area magic: Meteor Rain (telegraphed zone, meteors fall over ~2.4 s) and Lightning Storm (dark cloud, bolts strike enemies).

const T := 64.0
var kind := "meteor"
var center := Vector2.ZERO
var radius := 3.2 * T
var dmg := 30.0
var crit := 0.06
var _t := 0.0
var _dur := 2.8
var _next := 0.0
var _cloud: Sprite2D
var _sk := ""
var _knock := 8.0
var _poise := 50.0
var _col := Color.WHITE


## Densest enemy cluster in range of the hero; falls back to a spot ahead of the hero.
static func pick_center(p: Node2D, range_tiles: float) -> Vector2:
	var best := Vector2.ZERO
	var best_n := 0
	for e in Enemy.all:
		if not is_instance_valid(e) or e.dead:
			continue
		if (e.global_position - p.global_position).length() > range_tiles * T:
			continue
		var n := 0
		for o in Enemy.all:
			if is_instance_valid(o) and not o.dead and (o.global_position - e.global_position).length() < 3.0 * T:
				n += 1
		if n > best_n:
			best_n = n
			best = e.global_position
	if best_n > 0:
		return best
	return p.global_position + Util.facing_vec(p.facing) * 4.5 * T


static func meteor_rain(at: Vector2, damage: float, crit_chance: float) -> AreaSpell:
	return _spawn("meteor", at, damage, crit_chance, 3.3 * T, 2.9)


static func lightning_storm(at: Vector2, damage: float, crit_chance: float) -> AreaSpell:
	return _spawn("storm", at, damage, crit_chance, 4.0 * T, 3.4)


## One-shot bolt / meteor on a point (set powers).
static func strike(k: String, at: Vector2, damage: float) -> void:
	var s := _spawn("strike", at, damage, 0.1, 1.6 * T, 0.2)
	s._sk = k


## Expanding ring that damages everything around a point (class active skills).
static func nova(at: Vector2, rad: float, damage: float, crit_chance: float, knock: float, poise: float, color: Color) -> void:
	var s := _spawn("strike", at, damage, crit_chance, rad, 0.2)
	s._sk = "nova"
	s._knock = knock
	s._poise = poise
	s._col = color


static func _spawn(k: String, at: Vector2, d: float, c: float, r: float, dur: float) -> AreaSpell:
	var s := AreaSpell.new()
	s.kind = k
	s.center = at
	s.dmg = d
	s.crit = c
	s.radius = r
	s._dur = dur
	s.z_index = 120
	Game.world.fx_layer.add_child(s)
	s.global_position = at
	return s


func _ready() -> void:
	if kind == "strike":
		_fire.call_deferred()
		return
	if kind == "storm":
		_cloud = Sprite2D.new()
		_cloud.texture = Util.soft_circle()
		_cloud.modulate = Color(0.1, 0.12, 0.25, 0.0)
		_cloud.scale = Vector2(radius * 2.6, radius * 1.5) / 128.0
		_cloud.position = Vector2(0, -3.2 * T)
		_cloud.z_index = 60
		add_child(_cloud)
		Sfx.play("boom", 0.5, 0.45)
	else:
		Sfx.play("charge", 0.55, 0.6)


func _fire() -> void:
	if _sk == "nova":
		var ring := Ring.new()
		ring.r_max = radius
		ring.col = _col
		Game.world.fx_layer.add_child(ring)
		ring.global_position = center
		blast(center, radius, dmg, _knock, _poise, true)
		Fx.shockwave(center, radius / T * 0.5)
		Sfx.play("boom", 0.5, 0.7)
		Game.camera.shake(0.14, 0.2)
		return
	if _sk == "storm":
		var b := Bolt.new()
		b.target = center
		Game.world.fx_layer.add_child(b)
		b.global_position = center
		blast(center, 1.3 * T, dmg, 7.0, 45.0, true)
		Sfx.play("spark", 0.6, 0.8)
		Game.camera.shake(0.06, 0.1)
	else:
		var m := Meteor.new()
		m.target = center
		m.owner_spell = self
		Game.world.fx_layer.add_child(m)
		m.global_position = center + Vector2(-5.5 * T, -10.5 * T)


func _process(dt: float) -> void:
	_t += dt
	if kind == "strike":
		if _t > 1.6:
			queue_free()
		return
	if kind == "storm":
		var a := clampf(minf(_t / 0.5, (_dur + 0.4 - _t) / 0.6), 0.0, 1.0)
		_cloud.modulate.a = 0.62 * a
		if _t > 0.35 and _t < _dur and _t >= _next:
			_next = _t + randf_range(0.2, 0.34)
			_bolt()
	else:
		if _t > 0.7 and _t < _dur and _t >= _next:
			_next = _t + randf_range(0.14, 0.26)
			_meteor()
	queue_redraw()
	if _t > _dur + 0.7:
		queue_free()


func _target_point() -> Vector2:
	var cands: Array = []
	for e in Enemy.all:
		if is_instance_valid(e) and not e.dead and (e.global_position - center).length() < radius:
			cands.append(e.global_position)
	if not cands.is_empty() and randf() < 0.62:
		return cands[randi() % cands.size()] + Vector2(randf_range(-30, 30), randf_range(-20, 20))
	var a := randf() * TAU
	return center + Vector2(cos(a), sin(a) * 0.62) * radius * sqrt(randf())


func _draw() -> void:
	if kind == "strike":
		return
	var col := Color(1.0, 0.45, 0.15) if kind == "meteor" else Color(0.55, 0.75, 1.0)
	var fade := clampf(minf(_t / 0.3, (_dur + 0.6 - _t) / 0.5), 0.0, 1.0)
	var pulse := 0.55 + 0.45 * sin(_t * 8.0)
	draw_arc(Vector2.ZERO, radius, 0, TAU, 56, Color(col.r, col.g, col.b, 0.55 * fade * pulse), 4.0)
	draw_arc(Vector2.ZERO, radius * 0.62, 0, TAU, 40, Color(col.r, col.g, col.b, 0.25 * fade), 2.0)
	draw_circle(Vector2.ZERO, radius, Color(col.r, col.g, col.b, 0.06 * fade))


func _meteor() -> void:
	var tgt := _target_point()
	var m := Meteor.new()
	m.target = tgt
	m.owner_spell = self
	Game.world.fx_layer.add_child(m)
	m.global_position = tgt + Vector2(-5.5 * T, -10.5 * T)
	Sfx.play("swing_heavy", 0.25, 0.5)


func _bolt() -> void:
	var tgt := _target_point()
	var b := Bolt.new()
	b.target = tgt
	Game.world.fx_layer.add_child(b)
	b.global_position = tgt
	blast(tgt, 1.15 * T, dmg * 0.85, 7.0, 45.0, true)
	Sfx.play("spark", 0.6, randf_range(0.6, 0.85))
	Sfx.play("boom", 0.3, randf_range(0.5, 0.8))
	Game.camera.shake(0.06, 0.1)


## Area damage around a point (used by both spells).
func blast(at: Vector2, r: float, d: float, knock: float, poise: float, stun_fx: bool = false) -> void:
	for e in Enemy.all.duplicate():
		if not is_instance_valid(e) or e.dead:
			continue
		if (e.global_position - at).length() < r + 0.3 * T:
			var is_crit := randf() < crit
			e.hurt(roundf(d * randf_range(0.9, 1.1) * (1.7 if is_crit else 1.0)), at, knock, poise, is_crit)
			if stun_fx:
				Fx.hit_spark(e.global_position + Vector2.UP * 0.7 * T, true)


class Meteor extends Node2D:
	var target := Vector2.ZERO
	var owner_spell: AreaSpell
	var _t := 0.0
	var _from := Vector2.ZERO
	const FALL := 0.62

	func _ready() -> void:
		_from = global_position
		z_index = 130
		var g := Util.glow(self, Color(1, 0.55, 0.2), 2.4, 0.7)
		g.position = Vector2.ZERO

	func _process(dt: float) -> void:
		_t += dt
		var u := clampf(_t / FALL, 0.0, 1.0)
		global_position = _from.lerp(target, u * u)
		var e := Fx.ember(global_position, Color(1, 0.6, 0.2))
		if e:
			e.vel = Vector2(randf_range(-20, 20), randf_range(-30, 10))
		queue_redraw()
		if u >= 1.0:
			_impact()

	func _draw() -> void:
		var dir := (_from - target).normalized()
		draw_line(Vector2.ZERO, dir * 90.0, Color(1, 0.55, 0.15, 0.55), 12.0)
		draw_line(Vector2.ZERO, dir * 60.0, Color(1, 0.85, 0.5, 0.8), 6.0)
		draw_circle(Vector2.ZERO, 15.0, Color(1, 0.4, 0.1))
		draw_circle(Vector2.ZERO, 9.0, Color(1, 0.9, 0.55))

	func _impact() -> void:
		if is_instance_valid(owner_spell):
			owner_spell.blast(target, 1.7 * T, owner_spell.dmg * 1.15, 9.0, 60.0)
		Fx.play("hit_fire", target + Vector2.UP * 0.4 * T, 0.0, 2.0, true)
		Fx.shockwave(target, 1.3)
		for i in 9:
			var e := Fx.ember(target, Color(1, 0.55, 0.15))
			if e:
				e.vel = Vector2.from_angle(randf() * TAU) * randf_range(60, 190)
		var sc := Sprite2D.new()
		sc.texture = Util.soft_circle()
		sc.modulate = Color(0.06, 0.04, 0.04, 0.55)
		sc.scale = Vector2(1.7, 0.9) * T / 128.0 * 1.2
		sc.z_index = -45
		Game.world.fx_layer.add_child(sc)
		sc.global_position = target
		var tw := sc.create_tween()
		tw.tween_property(sc, "modulate:a", 0.0, 3.0)
		tw.tween_callback(sc.queue_free)
		Sfx.play("boom", 0.6, randf_range(0.55, 0.8))
		Game.camera.shake(0.12, 0.14)
		Game.hit_stop(0.03)
		queue_free()


class Bolt extends Node2D:
	var target := Vector2.ZERO
	var _t := 0.0
	var _pts := PackedVector2Array()

	func _ready() -> void:
		z_index = 140
		var top := Vector2(randf_range(-30, 30), -11.0 * T)
		_pts.append(top)
		var segs := 9
		for i in range(1, segs):
			var f := float(i) / segs
			_pts.append(top.lerp(Vector2.ZERO, f) + Vector2(randf_range(-26, 26), 0))
		_pts.append(Vector2.ZERO)
		var g := Util.glow(self, Color(0.7, 0.85, 1.0), 3.2, 0.9)
		g.position = Vector2.ZERO
		g.name = "flash"
		Fx.play("hit_spark", global_position, 0.0, 1.6, true)
		for i in 5:
			var e := Fx.ember(global_position, Color(0.7, 0.9, 1.0))
			if e:
				e.vel = Vector2.from_angle(randf() * TAU) * randf_range(50, 160)

	func _process(dt: float) -> void:
		_t += dt
		queue_redraw()
		var fl := get_node_or_null("flash")
		if fl:
			fl.modulate.a = maxf(0.0, 0.9 - _t * 5.0)
		if _t > 0.22:
			queue_free()

	func _draw() -> void:
		var a := clampf(1.0 - _t / 0.22, 0.0, 1.0)
		draw_polyline(_pts, Color(0.5, 0.7, 1.0, 0.45 * a), 16.0)
		draw_polyline(_pts, Color(0.8, 0.9, 1.0, 0.8 * a), 7.0)
		draw_polyline(_pts, Color(1, 1, 1, a), 3.0)


class Ring extends Node2D:
	var r_max := 200.0
	var col := Color.WHITE
	var t := 0.0

	func _ready() -> void:
		material = Util.additive()
		z_index = 90

	func _process(dt: float) -> void:
		t += dt
		queue_redraw()
		if t > 0.55:
			queue_free()

	func _draw() -> void:
		var u := clampf(t / 0.45, 0.0, 1.0)
		var r := r_max * (1.0 - pow(1.0 - u, 3.0))
		var a := 1.0 - u
		draw_arc(Vector2.ZERO, r, 0.0, TAU, 64, Color(col, 0.9 * a), 10.0 * a + 2.0)
		draw_arc(Vector2.ZERO, r * 0.82, 0.0, TAU, 64, Color(1, 1, 1, 0.5 * a), 4.0)
		draw_circle(Vector2.ZERO, r, Color(col, 0.12 * a))
