class_name AmbientEmitter
extends Node2D
## Positional life for the town: forge hammering with sparks, tavern/market murmur, fountain water, chimney smoke.

const T := 64.0
var kind := "forge"
var _t := randf() * 3.0
var _player: AudioStreamPlayer2D
var _next := 0.0


static func spawn(k: String, at: Vector2, parent: Node) -> AmbientEmitter:
	var e := AmbientEmitter.new()
	e.kind = k
	parent.add_child(e)
	e.global_position = at
	return e


func _ready() -> void:
	match kind:
		"crowd", "market", "water":
			_player = AudioStreamPlayer2D.new()
			_player.stream = Sfx.clip({"crowd": "murmur", "market": "murmur", "water": "water"}[kind])
			_player.bus = "Sfx"
			_player.max_distance = 9.0 * T if kind != "water" else 6.0 * T
			_player.attenuation = 1.6
			_player.volume_db = linear_to_db({"crowd": 0.32, "market": 0.2, "water": 0.22}[kind])
			_player.pitch_scale = 1.0 if kind == "crowd" else (1.25 if kind == "market" else 1.0)
			add_child(_player)
		"forge":
			_player = AudioStreamPlayer2D.new()
			_player.stream = Sfx.clip("clang")
			_player.bus = "Sfx"
			_player.max_distance = 11.0 * T
			_player.attenuation = 1.4
			_player.volume_db = linear_to_db(0.55)
			add_child(_player)


func _process(dt: float) -> void:
	var p := Player.I
	if p == null:
		return
	var dist := (p.global_position - global_position).length()
	if dist > 14.0 * T:
		if _player and _player.playing and kind != "forge":
			_player.stop()
		return
	_t += dt
	match kind:
		"crowd", "market", "water":
			if not _player.playing:
				_player.play()
			if kind == "market" and _t >= _next:
				_next = _t + randf_range(3.5, 8.0)
				Sfx.play("coin", 0.18, randf_range(0.9, 1.3))
		"forge":
			if _t >= _next:
				_next = _t + randf_range(0.85, 1.35)
				_player.pitch_scale = randf_range(0.92, 1.1)
				_player.play()
				for i in 7:
					var e := Fx.ember(global_position + Vector2(randf_range(-10, 10), -8), Color(1, 0.6, 0.2))
					if e:
						e.vel = Vector2(randf_range(-70, 70), randf_range(-90, -20))
		"smoke":
			if _t >= _next:
				_next = _t + randf_range(0.7, 1.3)
				_puff()


func _puff() -> void:
	var s := Sprite2D.new()
	s.texture = Util.soft_circle()
	s.modulate = Color(0.82, 0.82, 0.88, 0.5)
	s.scale = Vector2.ONE * 0.1
	s.z_index = 150
	Game.world.fx_layer.add_child(s)
	s.global_position = global_position + Vector2(randf_range(-4, 4), 0)
	var tw := s.create_tween().set_parallel(true)
	tw.tween_property(s, "position:y", s.position.y - 1.4 * T, 2.4)
	tw.tween_property(s, "position:x", s.position.x + randf_range(10, 40), 2.4)
	tw.tween_property(s, "scale", Vector2.ONE * 0.42, 2.4)
	tw.tween_property(s, "modulate:a", 0.0, 2.4).set_delay(0.6)
	tw.chain().tween_callback(s.queue_free)
