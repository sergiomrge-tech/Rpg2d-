class_name CameraRig
extends Camera2D
## Smooth follow with look-ahead, trauma-based shake, clamped to map bounds.

var target: Node2D
var _look := Vector2.ZERO
var _trauma := 0.0
var _decay := 1.0
var _noise := FastNoiseLite.new()


func _ready() -> void:
	make_current()
	position_smoothing_enabled = false
	_noise.frequency = 1.0


func shake(amount: float, duration: float) -> void:
	_trauma = minf(1.0, _trauma + amount * 2.2)
	_decay = 1.0 / maxf(0.05, duration * 2.5)


func set_world(w: World) -> void:
	limit_left = 0
	limit_top = 0
	limit_right = int(w.bounds.size.x)
	limit_bottom = int(w.bounds.size.y)


func snap() -> void:
	if target:
		global_position = target.global_position + Vector2.UP * 0.8 * 64.0
		reset_smoothing()


func _process(dt: float) -> void:
	if target == null:
		return
	var vel := Vector2.ZERO
	if target is CharacterBody2D:
		vel = (target as CharacterBody2D).velocity
	_look = _look.lerp((vel * 0.18).limit_length(1.2 * 64.0), clampf(dt * 2.5, 0.0, 1.0))
	var want := target.global_position + Vector2.UP * 0.8 * 64.0 + _look
	global_position = global_position.lerp(want, clampf(dt * 7.0, 0.0, 1.0))
	_trauma = maxf(0.0, _trauma - _decay * dt)
	var s := _trauma * _trauma * 22.0
	var t := Game.time() * 25.0
	offset = Vector2(_noise.get_noise_2d(t, 0.0), _noise.get_noise_2d(0.0, t + 50.0)) * s
