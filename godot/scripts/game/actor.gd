class_name Actor
extends CharacterBody2D
## Shared body for player / demons / NPCs: animated sprite, shadow, collision, hp, hit flash / dissolve.

const T := 64.0

var anim: Anim
var hp := 1.0
var max_hp := 1.0
var dead := false
var facing: int = Util.Face.DOWN
var invuln := 0.0
var poise := 0.0
var max_poise := 0.0
var knock := Vector2.ZERO

var _flash := 0.0
var _flash_color := Color.WHITE
var _dissolve := 0.0
var _mat: ShaderMaterial


func build(sheet_path: String, shadow_w: float, shadow_h: float, radius: float, scl: float = 1.0) -> void:
	motion_mode = CharacterBody2D.MOTION_MODE_FLOATING
	anim = Anim.new()
	anim.setup(sheet_path)
	anim.scale = Vector2.ONE * scl
	_mat = Util.make_fx_material()
	anim.material = _mat
	add_child(anim)
	Util.make_shadow(self, shadow_w * scl, shadow_h * scl)
	var cs := CollisionShape2D.new()
	var c := CircleShape2D.new()
	c.radius = radius * T
	cs.shape = c
	cs.position = Vector2(0, -radius * 0.6 * T)
	add_child(cs)


func pos() -> Vector2:
	return global_position


func chest(h: float = 0.6) -> Vector2:
	return global_position + Vector2.UP * h * T


func flash(c: Color, amount: float = 1.0) -> void:
	_flash_color = c
	_flash = amount


func start_dissolve() -> void:
	_dissolve = 0.001


func _process(delta: float) -> void:
	if invuln > 0.0:
		invuln -= delta
	if _flash > 0.0:
		_flash = maxf(0.0, _flash - delta * 7.0)
	if _dissolve > 0.0:
		_dissolve = minf(1.0, _dissolve + delta * 0.9)
	if _mat:
		_mat.set_shader_parameter("flash", _flash)
		_mat.set_shader_parameter("flash_color", _flash_color)
		_mat.set_shader_parameter("dissolve", _dissolve)


func face(f: int) -> void:
	facing = f
	anim.set_facing(f)


## Apply damage. Returns true if the hit landed.
func hurt(dmg: float, from: Vector2, knockback: float, poise_dmg: float, crit: bool = false) -> bool:
	if dead or invuln > 0.0:
		return false
	hp -= dmg
	flash(Color.WHITE)
	var dir := (global_position - from).normalized()
	if dir.length_squared() < 0.01:
		dir = Vector2.DOWN
	knock = dir * knockback * T
	poise -= poise_dmg
	Fx.damage_number(global_position + Vector2.UP * 1.6 * T, dmg, crit, self is Player)
	Fx.hit_spark(global_position + Vector2.UP * 0.8 * T - dir * 0.2 * T, crit)
	if hp <= 0.0:
		hp = 0.0
		_die()
	return true


func _die() -> void:
	pass
