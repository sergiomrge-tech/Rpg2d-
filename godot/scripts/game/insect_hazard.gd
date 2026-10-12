class_name InsectHazard
extends Node2D
## Timed, visible poison cloud (plague roach, Vespara, Brood Tyrant). Poisons the hero while inside.

const T := 64.0
var life := 3.0
var total := 3.0
var radius := 1.5 * T
var damage := 3.0
var tick := 0.2
var _cloud: Sprite2D
var _clock := 0.0


static func spawn_poison(at: Vector2, size_tiles: float, seconds: float, tick_damage: float) -> InsectHazard:
	var h := InsectHazard.new()
	h.radius = size_tiles * T
	h.life = seconds
	h.total = seconds
	h.damage = tick_damage
	h._cloud = Util.glow(h, Color(0.32, 0.72, 0.29), size_tiles * 2.0, 0.32)
	h._cloud.scale = Vector2(size_tiles * 2.0, size_tiles * 1.15) * T / 128.0
	h._cloud.show_behind_parent = false
	h.z_index = -5
	Game.world.fx_layer.add_child(h)
	h.global_position = at
	return h


func _process(dt: float) -> void:
	life -= dt
	if life <= 0.0:
		queue_free()
		return
	_cloud.modulate.a = 0.32 * clampf(life / maxf(0.01, total), 0.0, 1.0)
	var p := Player.I
	tick -= dt
	if tick <= 0.0:
		tick = 0.85
		if p != null and not p.dead and (p.global_position - global_position).length() < radius:
			if p.hurt(damage, global_position, 0.0, 0.0):
				p.apply_venom(1.15)
	_clock -= dt
	if _clock <= 0.0:
		_clock = 0.2
		var e := Fx.ember(global_position + Vector2.from_angle(randf() * TAU) * randf() * radius * 0.65, Color(0.48, 0.83, 0.32))
		if e:
			e.vel = Vector2.UP * 0.5 * T + Vector2.from_angle(randf() * TAU) * 0.3 * T
