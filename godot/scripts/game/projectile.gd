class_name Projectile
extends Node2D
## Fireballs, sparks, arrows and crescent blades.

const T := 64.0
var vel := Vector2.ZERO
var dmg := 0.0
var life := 2.2
var radius := 0.35
var friendly := false
var tier := 0
var hit_fx := "hit"
var pierce := false
var slows := false
var venomous := false
var trail_col := Color(1, 0.6, 0.2)
var _hit_set := {}
var _glow: Sprite2D
var _trail_t := 0.0


static func _make(anim_name: String, at: Vector2, dir: Vector2, speed: float, dmg_: float, friendly_: bool, scl: float, glow_col: Color) -> Projectile:
	var p := Projectile.new()
	p.vel = dir.normalized() * speed * T
	p.dmg = dmg_
	p.friendly = friendly_
	var a := Anim.new()
	a.setup("Sprites/Fx/fx")
	a.material = Util.additive()
	a.scale = Vector2.ONE * scl
	a.rotation = dir.angle()
	p.add_child(a)
	a.play(anim_name, true)
	p._glow = Util.glow(p, glow_col, 1.8 * scl, 0.55)
	var sh := Util.make_shadow(p, 0.5, 0.18, 0.25)
	sh.position = Vector2(0, 0.8 * T)
	Game.world.fx_layer.add_child(p)
	p.global_position = at
	return p


static func spark(at: Vector2, dir: Vector2, dmg_: float, tier_: int, friendly_: bool) -> Projectile:
	var col := Color(0.45, 0.8, 1.0) if tier_ == 1 else (Color(1, 0.55, 0.15) if tier_ == 2 else Color(0.75, 0.45, 1.0))
	var p := _make("spark%d" % clampi(tier_, 1, 3), at, dir, 13.0 + tier_, dmg_, friendly_, 1.0 + 0.15 * tier_, col)
	p.tier = tier_
	p.hit_fx = "hit_spark" if tier_ == 1 else "hit_fire"
	p.radius = 0.4 + 0.1 * tier_
	p.pierce = tier_ >= 3
	return p


static func crescent(at: Vector2, dir: Vector2, dmg_: float) -> Projectile:
	var p := _make("crescent", at, dir, 11.0, dmg_, true, 1.25, Color(0.5, 0.85, 1.0))
	p.hit_fx = "hit_spark"
	p.pierce = true
	p.life = 0.75
	p.radius = 0.75
	return p


static func arrow(at: Vector2, dir: Vector2, dmg_: float) -> Projectile:
	var p := _make("arrow", at, dir, 16.0, dmg_, true, 0.9, Color(0.6, 1.0, 0.8))
	p.hit_fx = "hit"
	p.life = 1.2
	p.radius = 0.3
	return p


static func fireball(at: Vector2, dir: Vector2, dmg_: float) -> Projectile:
	var p := _make("fireball", at, dir, 6.2, dmg_, false, 0.9, Color(1, 0.5, 0.15))
	p.hit_fx = "hit_fire"
	p.life = 2.6
	return p


## Moth curse bolt: slows the hero.
static func hex_spore(at: Vector2, dir: Vector2, dmg_: float) -> Projectile:
	var p := _make("fireball", at, dir, 4.4, dmg_, false, 0.78, Color(0.73, 0.39, 0.88))
	p.hit_fx = "hit_spark"
	p.life = 3.1
	p.radius = 0.46
	p.slows = true
	p.trail_col = Color(0.72, 0.39, 0.94)
	return p


## Dragonfly lancet: fast, thin, teal.
static func insect_needle(at: Vector2, dir: Vector2, dmg_: float) -> Projectile:
	var p := _make("spark1", at, dir, 15.5, dmg_, false, 0.67, Color(0.37, 0.9, 0.87))
	p.hit_fx = "hit_spark"
	p.radius = 0.25
	p.life = 1.3
	p.trail_col = Color(0.36, 0.96, 0.9)
	return p


## Queen's venom bolt: poisons the hero.
static func venom_dart(at: Vector2, dir: Vector2, dmg_: float) -> Projectile:
	var p := _make("spark2", at, dir, 10.4, dmg_, false, 0.86, Color(0.67, 0.95, 0.33))
	p.radius = 0.34
	p.hit_fx = "hit_spark"
	p.life = 2.3
	p.venomous = true
	p.trail_col = Color(0.67, 0.95, 0.36)
	return p


func _process(dt: float) -> void:
	global_position += vel * dt
	life -= dt
	_trail_t -= dt
	if _trail_t <= 0.0:
		_trail_t = 0.035
		Fx.ember(global_position, Color(0.6, 0.9, 1.0) if (friendly and tier == 1) else trail_col)
	if _glow:
		_glow.scale = Vector2.ONE * (1.8 + sin(Game.time() * 30.0) * 0.15) * T / 128.0
	var p := global_position
	if friendly:
		for e in Enemy.all:
			if e.dead:
				continue
			if (e.global_position + Vector2.UP * 0.6 * T - p).length() < (radius + 0.4) * T:
				if pierce and _hit_set.has(e):
					continue
				if pierce:
					_hit_set[e] = true
				var crit := randf() < 0.1
				e.hurt(roundf(dmg * randf_range(0.92, 1.08) * (1.7 if crit else 1.0)), p - vel.normalized(), 6.0, 16.0, crit)
				if pierce:
					Fx.play(hit_fx, e.global_position + Vector2.UP * 0.7 * T, 0.0, 0.9, true)
					continue
				_explode()
				return
	elif Player.I != null and not Player.I.dead:
		if (Player.I.global_position + Vector2.UP * 0.6 * T - p).length() < (radius + 0.3) * T:
			if Player.I.hurt(roundf(dmg), p - vel.normalized(), 6.0, 15.0):
				if slows:
					Player.I.apply_hex_slow(2.1)
				if venomous:
					Player.I.apply_venom(3.0)
				_explode()
				return
	if not Game.world.bounds.has_point(p):
		_explode()
		return
	if life <= 0.0:
		_explode()


func _explode() -> void:
	Fx.play(hit_fx, global_position, 0.0, 1.1 + 0.15 * tier, true)
	if not friendly or tier > 1:
		Game.camera.shake(0.07, 0.1)
	Sfx.play("boom", 0.35, randf_range(0.9, 1.15))
	queue_free()
