class_name SummonedSpirit
extends Node2D
## Real animated allied pet. Uses the approved bog-wraith character atlas as
## a TEMPORARY spirit body; a bespoke premium pet sprite remains an art gate.
## Its attacks are emitted only by animation hit frames, not visual mockups.

const T := 64.0
const LIMIT := 2
const DURATION := 28.0
static var all: Array[SummonedSpirit] = []

var master: Player
var anim: Anim
var life := DURATION
var shoot_cd := 0.6
var enemy: Enemy
var is_casting := false
var orbit_slot := 0


static func spawn_for(player: Player) -> SummonedSpirit:
	if player == null or player.dead or player.gs.class_id != "summoner":
		return null
	_cleanup()
	if all.size() >= LIMIT or Game.world == null:
		return null
	var pet := SummonedSpirit.new()
	pet.master = player
	pet.orbit_slot = all.size()
	Game.world.entities.add_child(pet)
	pet.global_position = player.global_position + Vector2((1 if pet.orbit_slot == 0 else -1) * T, -0.4 * T)
	pet._build_visuals()
	all.append(pet)
	Fx.magic_circle(pet.global_position, 2)
	Fx.toast("Espírito invocado!", Color(0.55, 0.96, 0.91), pet.global_position + Vector2.UP * 1.3 * T)
	Sfx.play("charge", 0.35, 1.25)
	return pet


static func _cleanup() -> void:
	for pet in all.duplicate():
		if not is_instance_valid(pet) or pet.is_queued_for_deletion():
			all.erase(pet)


static func command(player: Player) -> void:
	_cleanup()
	var focus := Enemy.nearest(player.global_position, 10.0 * T)
	for pet in all:
		if is_instance_valid(pet) and pet.master == player and focus != null:
			pet.enemy = focus
			pet.shoot_cd = minf(pet.shoot_cd, 0.12)


static func clear_all() -> void:
	for pet in all.duplicate():
		if is_instance_valid(pet):
			pet.queue_free()
	all.clear()


func _build_visuals() -> void:
	anim = Anim.new()
	anim.setup("Sprites/Demons/bog_wraith")
	anim.scale = Vector2.ONE * 0.92
	anim.modulate = Color(0.55, 0.98, 0.9, 0.86)
	add_child(anim)
	anim.hit.connect(_on_anim_hit)
	anim.ended.connect(_on_anim_end)
	anim.play("idle", true)
	Util.make_shadow(self, 0.7, 0.18, 0.23)


func _exit_tree() -> void:
	all.erase(self)


func _process(dt: float) -> void:
	life -= dt
	if life <= 0.0 or master == null or not is_instance_valid(master) or master.dead or master.gs.class_id != "summoner":
		queue_free()
		return
	if Game.world == null or get_parent() != Game.world.entities:
		queue_free()
		return
	shoot_cd = maxf(0.0, shoot_cd - dt)
	if enemy == null or not is_instance_valid(enemy) or enemy.dead or (enemy.global_position - global_position).length() > 11.0 * T:
		enemy = Enemy.nearest(global_position, 8.5 * T)
	var target_position := master.global_position + Vector2(1 if orbit_slot == 0 else -1, -0.9) * 1.3 * T
	if enemy != null and is_instance_valid(enemy) and not enemy.dead and (enemy.global_position - master.global_position).length() < 9.0 * T:
		var away := (global_position - enemy.global_position).normalized()
		target_position = enemy.global_position + away * 3.5 * T
	if is_casting:
		return
	var delta := target_position - global_position
	if delta.length_squared() > pow(0.45 * T, 2):
		global_position += delta.normalized() * minf(5.4 * T * dt, delta.length())
		anim.set_facing(Util.facing_from(delta, anim.facing))
		anim.play("move")
	else:
		anim.play("idle")
	if enemy != null and is_instance_valid(enemy) and not enemy.dead and shoot_cd <= 0.0 and (enemy.global_position - global_position).length() < 8.5 * T:
		anim.set_facing(Util.facing_from(enemy.global_position - global_position, anim.facing))
		is_casting = true
		anim.play("cast", true)
		shoot_cd = 1.35


func _on_anim_hit(track: String) -> void:
	if track != "cast" or not is_casting or enemy == null or not is_instance_valid(enemy) or enemy.dead:
		return
	if master == null or not is_instance_valid(master):
		return
	var source := global_position + Vector2.UP * 0.8 * T
	var dir := (enemy.global_position + Vector2.UP * 0.5 * T - source).normalized()
	Projectile.spark(source + dir * 0.25 * T, dir, master.gs.total_mag() * 0.62, 1, true)
	Sfx.play("spark", 0.3, 1.2)


func _on_anim_end(track: String) -> void:
	if track == "cast":
		is_casting = false
		anim.play("idle")
