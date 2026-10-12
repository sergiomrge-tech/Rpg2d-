class_name Companion
extends Actor
## Sylra, elven archer: follows the hero, keeps distance from demons and shoots arrows.

static var I: Companion
var shoot_cd := 1.0
var shoot_t := -1.0
var target: Enemy


static func spawn(at: Vector2) -> Companion:
	var c := Companion.new()
	c.name = "Sylra"
	c.collision_layer = 0
	c.collision_mask = 1
	c.build("Sprites/Chars/sylra", 1.2, 0.4, 0.28)
	c.max_hp = 1.0
	c.hp = 1.0
	Game.world.add_entity(c, at)
	c.anim.play("idle")
	I = c
	return c


func _exit_tree() -> void:
	if I == self:
		I = null


func _physics_process(dt: float) -> void:
	var p := Player.I
	if p == null:
		return
	shoot_cd -= dt
	var to_p := p.global_position - global_position
	if to_p.length() > 14.0 * T:
		global_position = p.global_position + Vector2.from_angle(randf() * TAU) * 1.5 * T
		return
	target = Enemy.nearest(global_position, 8.5 * T)
	if shoot_t >= 0.0:
		shoot_t += dt
		velocity = Vector2.ZERO
		if shoot_t > 0.32 and target != null and not target.dead:
			var dir := (target.global_position + Vector2.UP * 0.5 * T - (global_position + Vector2.UP * 0.8 * T)).normalized()
			Projectile.arrow(global_position + Vector2.UP * 0.8 * T + dir * 0.4 * T, dir, 9.0 + 2.4 * p.gs.level)
			Sfx.play("swing", 0.25, 1.6)
			shoot_t = -1.0
		elif shoot_t > 0.6:
			shoot_t = -1.0
		return
	if target != null and shoot_cd <= 0.0 and not p.dead:
		shoot_cd = 1.35
		shoot_t = 0.0
		face(Util.facing_from(target.global_position - global_position, facing))
		anim.play("cast", true)
		return
	var fv := Util.facing_vec(p.facing)
	var want := p.global_position - fv * 1.6 * T + Vector2(-fv.y, fv.x) * 0.9 * T
	var to := want - global_position
	if to.length() > 0.5 * T:
		var run := to.length() > 3.5 * T
		face(Util.facing_from(to, facing))
		anim.play("run" if run else "walk")
		velocity = to.normalized() * (6.6 if run else 4.1) * T
		move_and_slide()
	else:
		velocity = Vector2.ZERO
		anim.play("idle")


func hurt(_d: float, _f: Vector2, _k: float, _p: float, _c: bool = false) -> bool:
	return false


func _die() -> void:
	pass
