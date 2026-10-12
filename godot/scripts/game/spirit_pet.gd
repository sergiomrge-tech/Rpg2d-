class_name SpiritPet
extends Node2D
## Real AI ally for the Summoner: follows Ren and attacks enemies automatically.
## Original Astral Lynx: independently drawn HD cartoon quadruped rig.
## Movement and spell-hit animations use real in-game directional sprite frames.

const T := 64.0
const MAX_ACTIVE := 2
static var active_pets: Array[SpiritPet] = []

var summoner: Node2D
var life := 38.0
var attack_cd := 0.5
var desired_target: Enemy
var visual: Anim
var glow: Sprite2D
var orbit_phase := 0.0
var casting := false


static func count_for(p: Node2D) -> int:
	var total := 0
	for spirit in active_pets:
		if is_instance_valid(spirit) and spirit.summoner == p and not spirit.is_queued_for_deletion():
			total += 1
	return total


static func summon(p: Node2D) -> bool:
	if p == null or p.dead or p.gs.class_id != "summoner":
		return false
	if count_for(p) >= MAX_ACTIVE:
		Fx.toast("Máximo de 2 familiares", Color(.76, .92, 1.0))
		return false
	var pet := SpiritPet.new()
	pet.summoner = p
	pet.orbit_phase = count_for(p) * PI
	Game.world.fx_layer.add_child(pet)
	pet.global_position = p.pos() + Vector2(60.0 if count_for(p) == 0 else -60.0, -50.0)
	active_pets.append(pet)
	Fx.magic_circle(pet.global_position, 1)
	Sfx.play("charge", .48, 1.25)
	return true


static func command(p: Node2D) -> void:
	var dir := Util.facing_vec(p.facing)
	var target := Enemy.nearest(p.pos(), 12.0 * T, dir, .25)
	if target == null:
		target = Enemy.nearest(p.pos(), 12.0 * T)
	if target == null:
		return
	for spirit in active_pets:
		if is_instance_valid(spirit) and spirit.summoner == p:
			spirit.desired_target = target
			spirit.attack_cd = minf(spirit.attack_cd, .1)
	Fx.toast("Atacar!", Color(.66, 1.0, .87), p.pos() + Vector2.UP * 1.9 * T)


func _ready() -> void:
	set_process(true)
	visual = Anim.new()
	visual.setup("Sprites/Pets/astral_lynx")
	visual.scale = Vector2.ONE * .90
	visual.modulate = Color.WHITE  # preserve refined paint/shading of original pet art
	add_child(visual)
	visual.hit.connect(_on_visual_hit)
	visual.ended.connect(_on_visual_end)
	visual.play("idle")
	glow = Util.glow(self, Color(.41, .91, .83), 1.30, .38)
	glow.position.y = -18.0
	Util.make_shadow(self, .50, .17, .21)


func _process(dt: float) -> void:
	if summoner == null or not is_instance_valid(summoner) or summoner.dead or summoner.gs.class_id != "summoner":
		queue_free()
		return
	life -= dt
	if life <= 0.0:
		Fx.demon_poof(global_position)
		queue_free()
		return
	orbit_phase += dt * 2.0
	visual.position.y = -8.0 + sin(orbit_phase * 2.5) * 7.0
	glow.modulate.a = .37 + .15 * sin(orbit_phase * 3.0)
	var target: Enemy = desired_target
	if target == null or not is_instance_valid(target) or target.dead or target.is_queued_for_deletion():
		target = Enemy.nearest(global_position, 8.0 * T)
		desired_target = target
	var destination: Vector2 = summoner.pos() + Vector2(cos(orbit_phase * .6) * 72, -54 + sin(orbit_phase * .6) * 48)
	if target != null:
		destination = target.pos() + Vector2(0, -50)
	var delta_pos: Vector2 = destination - global_position
	var speed := (390.0 if target != null else 315.0) * dt
	if not casting:
		if delta_pos.length() > (2.5 * T if target != null else 40.0):
			global_position += delta_pos.normalized() * minf(speed, delta_pos.length())
			visual.set_facing(Util.facing_from(delta_pos, visual.facing))
			visual.play("move")
		else:
			visual.play("idle")
	attack_cd -= dt
	if not casting and target != null and (target.pos() - global_position).length() < 8.0 * T and attack_cd <= 0.0:
		attack_cd = 1.12
		visual.set_facing(Util.facing_from(target.pos() - global_position, visual.facing))
		casting = true
		visual.play("cast", true)


func _on_visual_hit(track: String) -> void:
	if track != "cast" or not casting or summoner == null or not is_instance_valid(summoner):
		return
	if desired_target == null or not is_instance_valid(desired_target) or desired_target.dead:
		return
	var source := global_position + Vector2.UP * .75 * T
	var dir := (desired_target.chest(.6) - source).normalized()
	# Pet fires on the keyframe (never the summoner), from a real animated body.
	Projectile.spark(source + dir * .25 * T, dir, summoner.gs.total_mag() * .62 * (1.0 + float(SkillTree.passive_v("summoner", summoner.gs.level)[0]) / 100.0), 1, true)
	Fx.ember(source, Color(.48, 1.0, .88))


func _on_visual_end(track: String) -> void:
	if track == "cast":
		casting = false
		visual.play("idle")


func _exit_tree() -> void:
	active_pets.erase(self)
