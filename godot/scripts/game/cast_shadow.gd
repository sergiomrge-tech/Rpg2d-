class_name CastShadow
extends Sprite2D
## Directional cast shadow of a sprite. Lives in the World's shadow layer (above the ground, below every entity) and follows its
## source; the sun direction / length / strength come from the shared material, driven by the time of day (World._update_sun).

var source: Sprite2D
var static_shadow := false
var scale_k := 1.0
var _done := false


## Attach a shadow to `src` (an Anim of an Actor or a prop sprite). Returns null when there is no world yet.
static func attach(src: Sprite2D, static_: bool = false, k: float = 1.0) -> CastShadow:
	var w: Node = src
	while w != null and not (w is World):
		w = w.get_parent()
	if w == null:
		return null
	var cs := CastShadow.new()
	cs.source = src
	cs.static_shadow = static_
	cs.scale_k = k
	cs.centered = false
	cs.material = Util.shadow_material()
	cs.self_modulate = Color(1, 1, 1, clampf(k, 0.2, 1.0))
	(w as World).shadow_layer.add_child(cs)
	cs._sync()
	return cs


func _process(_dt: float) -> void:
	if not is_instance_valid(source) or not source.is_inside_tree():
		queue_free()
		return
	if _done:
		return
	_sync()
	if static_shadow:
		_done = true


func _sync() -> void:
	if not is_instance_valid(source):
		return
	var owner_actor := source.get_parent() as Actor
	visible = source.is_visible_in_tree() and not (owner_actor != null and owner_actor.dead)
	texture = source.texture
	offset = source.offset
	flip_h = source.flip_h
	global_transform = source.global_transform
