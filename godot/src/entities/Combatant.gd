class_name Combatant
extends CharacterBody2D
## Base for player & enemies: hp, hit flash, knockback, status effects.

var max_hp := 100.0
var hp := 100.0
var team := ""
var sprite: AnimatedSprite2D
var mat: ShaderMaterial
var flash_t := 0.0
var kb_vel := Vector2.ZERO
var status := {}      # name -> {t: float, p: float}
var dead := false
var radius := 10.0
var hit_h := 20.0
var world: World
var face := Vector2.DOWN

static var _shader: Shader

func setup_sprite(frames: SpriteFrames, offset_y: float, scale_f := 1.0) -> void:
	sprite = AnimatedSprite2D.new()
	sprite.sprite_frames = frames
	sprite.centered = true
	sprite.offset = Vector2(0, offset_y)
	sprite.scale = Vector2(scale_f, scale_f)
	if _shader == null:
		_shader = load("res://src/entities/char.gdshader")
	mat = ShaderMaterial.new()
	mat.shader = _shader
	sprite.material = mat
	add_child(sprite)

func hit_center() -> Vector2:
	return global_position + Vector2(0, -hit_h)

func has_status(n: String) -> bool:
	return status.has(n)

func apply_status(n: String, dur: float, power := 0.0) -> void:
	if status.has(n):
		status[n]["t"] = maxf(status[n]["t"], dur)
		status[n]["p"] = maxf(status[n]["p"], power)
	else:
		status[n] = {"t": dur, "p": power, "tick": 0.0}

func _tick_common(dt: float) -> void:
	if flash_t > 0.0:
		flash_t -= dt
	if mat:
		mat.set_shader_parameter("flash", clampf(flash_t * 9.0, 0.0, 1.0))
		var tint := Color.WHITE
		var add := Color(0, 0, 0, 0)
		if status.has("freeze"):
			tint = Color(0.6, 0.85, 1.0)
			add = Color(0.0, 0.08, 0.18, 0)
		elif status.has("burn"):
			add = Color(0.16, 0.05, 0.0, 0)
		elif status.has("slow"):
			tint = Color(0.8, 0.85, 1.0)
		mat.set_shader_parameter("tint", tint)
		mat.set_shader_parameter("add_color", add)
	var rm: Array = []
	for n in status:
		status[n]["t"] -= dt
		if n == "burn":
			status[n]["tick"] += dt
			if status[n]["tick"] >= 0.5:
				status[n]["tick"] = 0.0
				on_dot(float(status[n]["p"]), "fire")
				if world:
					Fx.embers(world, hit_center(), 3)
		if status[n]["t"] <= 0.0:
			rm.append(n)
	for n in rm:
		status.erase(n)

func on_dot(_amount: float, _elem: String) -> void:
	pass

func take_hit(_h: Dictionary) -> float:
	return 0.0
