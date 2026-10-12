class_name Fx
extends RefCounted
## Visual effects facade (sheet "Sprites/Fx/fx") + floating world text.

const T := 64.0


class FxSprite extends Node2D:
	var anim: Anim
	var spr: Sprite2D
	var vel := Vector2.ZERO
	var fade_after := -1.0
	var life := -1.0
	var spin := 0.0
	var grow := 0.0
	var _t := 0.0

	func _process(dt: float) -> void:
		_t += dt
		global_position += vel * dt
		vel *= maxf(0.0, 1.0 - 3.0 * dt)
		if spin != 0.0:
			rotation += spin * dt
		if grow != 0.0:
			scale *= 1.0 + grow * dt
		if fade_after >= 0.0 and life > 0.0 and _t > fade_after:
			modulate.a = 1.0 - clampf((_t - fade_after) / maxf(0.01, life - fade_after), 0.0, 1.0)
		if life > 0.0 and _t >= life:
			queue_free()
		elif life < 0.0 and anim != null and anim.finished:
			queue_free()


static func _layer() -> Node:
	return Game.world.fx_layer if Game.world else null


static func play(name: String, at: Vector2, angle: float = 0.0, scl: float = 1.0, additive: bool = false, parent: Node = null) -> FxSprite:
	var layer := parent if parent else _layer()
	if layer == null:
		return null
	var f := FxSprite.new()
	f.rotation = deg_to_rad(angle)
	f.scale = Vector2.ONE * scl
	var a := Anim.new()
	a.setup("Sprites/Fx/fx")
	if additive:
		a.material = Util.additive()
	f.add_child(a)
	f.anim = a
	layer.add_child(f)
	f.global_position = at
	a.play(name, true)
	return f


static func _angle_of(f: int) -> float:
	return 0.0 if f == Util.Face.RIGHT else (-90.0 if f == Util.Face.UP else (180.0 if f == Util.Face.LEFT else 90.0))


static func slash(at: Vector2, f: int, combo: int) -> void:
	var n := "slash_heavy" if combo == 3 else "slash"
	var fx := play(n, at + Util.facing_vec(f) * 0.25 * T, _angle_of(f), 1.25 if combo == 3 else 1.05, true)
	if fx and combo == 2:
		fx.scale = Vector2(1.05, -1.05)


static func claw(at: Vector2, f: int) -> void:
	play("claw", at, _angle_of(f), 0.9, false)


static func hit_spark(at: Vector2, crit: bool) -> void:
	play("hit_crit" if crit else "hit", at, randf() * 360.0, 1.3 if crit else 1.0, true)


static func dust(at: Vector2, amount: float) -> void:
	var f := play("dust", at + Vector2(randf_range(-6, 6), randf_range(-6, 6)), 0.0, 0.7 + amount * 0.4, false)
	if f:
		f.vel = Vector2(randf_range(-25, 25), randf_range(-25, 25))


static func shockwave(at: Vector2, scl: float) -> void:
	var f := play("shock", at, 0.0, scl, true)
	if f:
		f.scale = Vector2(scl, scl * 0.55)


static func magic_circle(at: Vector2, tier: int) -> void:
	var f := play("circle%d" % clampi(tier, 1, 3), at, 0.0, 1.0, true)
	if f:
		f.scale = Vector2(1.1, 0.55)
		f.z_index = -50


static func heal(at: Vector2) -> void:
	play("heal", at + Vector2.UP * 0.8 * T, 0.0, 1.2, true)


static func demon_poof(at: Vector2) -> void:
	play("poof", at, 0.0, 1.3, false)
	for i in 10:
		var e := ember(at + Vector2(randf_range(-26, 26), randf_range(-26, 26)), Color(0.85, 0.35, 1.0))
		if e:
			e.vel = Vector2(randf_range(-160, 160), randf_range(-160, 100)) + Vector2.UP * 90.0


static func ember(at: Vector2, c: Color) -> FxSprite:
	var layer := _layer()
	if layer == null:
		return null
	var f := FxSprite.new()
	var s := Sprite2D.new()
	s.texture = Util.soft_circle()
	s.material = Util.additive()
	s.modulate = c
	f.add_child(s)
	f.spr = s
	f.scale = Vector2.ONE * randf_range(0.12, 0.24) * T / 128.0
	f.life = randf_range(0.3, 0.55)
	f.fade_after = 0.05
	f.vel = Vector2(randf_range(-38, 38), randf_range(-38, 38)) + Vector2.UP * 25.0
	f.grow = -1.2
	layer.add_child(f)
	f.global_position = at
	return f


static func alert(a: Actor) -> void:
	var f := play("alert", Vector2.ZERO, 0.0, 0.8, false, a)
	if f:
		f.position = Vector2(0, -2.0 * T)
		f.z_index = 100


static func _float_label(text: String, at: Vector2, size: int, color: Color, rise: float, life: float, serif: bool) -> void:
	var layer := _layer()
	if layer == null:
		return
	var l := Util.label(text, size, color, Util.font_serif if serif else Util.font_bold)
	l.custom_minimum_size = Vector2(400, 60)
	l.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	l.pivot_offset = Vector2(200, 30)
	layer.add_child(l)
	l.global_position = at - Vector2(200, 30)
	l.scale = Vector2.ONE * 1.5
	l.z_index = 200
	var tw := l.create_tween()
	tw.set_parallel(true)
	tw.tween_property(l, "scale", Vector2.ONE, 0.12)
	tw.tween_property(l, "position:y", l.position.y - rise, life).set_ease(Tween.EASE_OUT)
	tw.tween_property(l, "position:x", l.position.x + randf_range(-30, 30), life)
	tw.tween_property(l, "modulate:a", 0.0, life * 0.35).set_delay(life * 0.65)
	tw.chain().tween_callback(l.queue_free)


static func damage_number(at: Vector2, dmg: float, crit: bool, on_player: bool) -> void:
	var c := Color(1, 0.38, 0.35) if on_player else (Color(1, 0.82, 0.25) if crit else Color.WHITE)
	_float_label(str(roundi(dmg)), at, 54 if crit else 38, c, 90.0, 0.9, true)


static func toast(text: String, color: Color, at: Variant = null) -> void:
	var p: Vector2 = at if at != null else (Player.I.global_position + Vector2.UP * 2.4 * T if Player.I else Vector2.ZERO)
	_float_label(text, p, 28, color, 70.0, 1.3, false)
