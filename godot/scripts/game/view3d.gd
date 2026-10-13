class_name View3D
extends Node3D
## HD-2D view: the 2D game keeps running as the simulation (physics, AI, combat) while this node draws it in a real 3D scene —
## tilted perspective camera, ground chunks as lit planes, props / heroes / monsters as upright sprites that cast real sun shadows.
## 1 world metre = 64 px (one tile). 2D x -> 3D X, 2D y -> 3D Z (south = towards the camera).

const T := 64.0
const PITCH := 52.0            # camera angle above the horizon (degrees)
const FOV := 34.0
const LEAN := 36.0             # sprites lean towards the camera so they are not squashed by the tilt

var world: World
var cam: Camera3D
var sun: DirectionalLight3D
var env: Environment
var _static := {}              # 2D node id -> Sprite3D (props never move)
var _dyn: Array = []           # [{n: Node2D, src: Sprite2D, s: Sprite3D}]
var _mats := {}
var dist := 22.0


static func attach(w: World) -> View3D:
	var v := View3D.new()
	v.name = "View3D"
	v.world = w
	w.add_child(v)
	v.build()
	return v


func build() -> void:
	# --- environment, sun, camera
	env = Environment.new()
	env.background_mode = Environment.BG_COLOR
	env.background_color = Color(0.06, 0.05, 0.09)
	env.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR
	env.ambient_light_color = Color(0.62, 0.62, 0.7)
	env.ambient_light_energy = 1.0
	var we := WorldEnvironment.new()
	we.environment = env
	add_child(we)
	sun = DirectionalLight3D.new()
	sun.shadow_enabled = Game.quality >= 1
	sun.directional_shadow_mode = DirectionalLight3D.SHADOW_ORTHOGONAL
	sun.directional_shadow_max_distance = 36.0
	sun.shadow_bias = 0.06
	sun.shadow_normal_bias = 1.0
	sun.shadow_opacity = 0.7
	sun.light_energy = 0.9
	add_child(sun)
	cam = Camera3D.new()
	cam.fov = FOV
	cam.near = 1.0
	cam.far = 160.0
	cam.current = true
	add_child(cam)
	# --- the 2D layers that are redrawn in 3D are hidden; fx (hit sparks, numbers, spells) stay as a 2D overlay
	world.ground.visible = false
	world.shadow_layer.visible = false
	world._flat.visible = false
	world.entities.visible = false
	_build_ground()
	for c in world._flat.get_children():
		_add_static(c as Node2D, true)
	for c in world.entities.get_children():
		_on_added(c)
	world.entities.child_entered_tree.connect(_on_added)
	world.entities.child_exiting_tree.connect(_on_removed)
	world._flat.child_entered_tree.connect(func(n): _add_static(n as Node2D, true))
	_update(0.0)


func _build_ground() -> void:
	for s in world.ground.get_children():
		var sp := s as Sprite2D
		if sp == null or sp.texture == null or sp.is_in_group("water_fx"):
			continue
		var sz := sp.texture.get_size() / T
		var mi := MeshInstance3D.new()
		var q := QuadMesh.new()
		q.size = sz
		mi.mesh = q
		var m := StandardMaterial3D.new()
		m.albedo_texture = sp.texture
		m.roughness = 1.0
		m.metallic_specular = 0.0
		m.texture_filter = BaseMaterial3D.TEXTURE_FILTER_LINEAR_WITH_MIPMAPS
		mi.material_override = m
		mi.rotation_degrees = Vector3(-90, 0, 0)
		mi.position = Vector3(sp.position.x / T + sz.x * 0.5, 0.0, sp.position.y / T + sz.y * 0.5)
		mi.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
		add_child(mi)


func _sprite3d(tex: Texture2D, off2: Vector2, scl: Vector2 = Vector2.ONE) -> Sprite3D:
	var s := Sprite3D.new()
	s.pixel_size = 1.0 / T
	s.texture = tex
	s.centered = false
	s.shaded = true
	s.double_sided = false
	s.alpha_cut = SpriteBase3D.ALPHA_CUT_DISCARD
	s.alpha_scissor_threshold = 0.5
	s.texture_filter = BaseMaterial3D.TEXTURE_FILTER_LINEAR_WITH_MIPMAPS
	s.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_ON
	s.scale = Vector3(scl.x, scl.y, 1.0)
	_set_offset(s, tex, off2)
	return s


## 2D offset = top-left of the image relative to the feet (y down); Sprite3D offset = bottom-left (y up).
func _set_offset(s: Sprite3D, tex: Texture2D, off2: Vector2) -> void:
	var h := tex.get_height() if tex != null else 0
	s.offset = Vector2(off2.x, -(off2.y + h))


func _place(s: Sprite3D, p2: Vector2, lean := -LEAN) -> void:
	s.position = Vector3(p2.x / T, 0.0, p2.y / T)
	s.rotation_degrees = Vector3(lean, 0, 0)


func _add_static(n: Node2D, flat: bool) -> void:
	var sp := n as Sprite2D
	if sp == null or sp.texture == null:
		return
	var s := _sprite3d(sp.texture, sp.offset, sp.scale)
	s.modulate = sp.modulate
	if flat:      # decals lying on the ground (flowers, bridge, wall cracks)
		s.rotation_degrees = Vector3(-90, 0, 0)
		s.position = Vector3(sp.global_position.x / T, 0.02, sp.global_position.y / T)
		s.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
		s.offset = Vector2(sp.offset.x, -(sp.offset.y + sp.texture.get_height()))
	else:
		_place(s, sp.global_position)
		var kind := str(sp.get_meta("kind", ""))
		if sp.texture.get_height() < 70:        # small ground clutter casts no shadow
			s.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	add_child(s)
	_static[sp.get_instance_id()] = s


func _on_added(n: Node) -> void:
	var n2 := n as Node2D
	if n2 == null:
		return
	if n2 is Sprite2D and not (n2 is Anim):
		_add_static(n2, false)
		return
	var src: Sprite2D = null
	if n2 is Actor and (n2 as Actor).anim != null:
		src = (n2 as Actor).anim
	else:
		for c in n2.get_children():
			if c is Sprite2D and (c as Sprite2D).texture != null:
				src = c
				break
	if src == null:
		return
	var s := _sprite3d(src.texture, src.offset, src.scale) if src.texture != null else Sprite3D.new()
	s.pixel_size = 1.0 / T
	add_child(s)
	_dyn.append({"n": n2, "src": src, "s": s})


func _on_removed(n: Node) -> void:
	var id := n.get_instance_id()
	if _static.has(id):
		(_static[id] as Sprite3D).queue_free()
		_static.erase(id)
		return
	for i in range(_dyn.size() - 1, -1, -1):
		if _dyn[i]["n"] == n:
			(_dyn[i]["s"] as Sprite3D).queue_free()
			_dyn.remove_at(i)


func _process(dt: float) -> void:
	_update(dt)


func _update(_dt: float) -> void:
	# animated bodies
	for d in _dyn:
		var n: Node2D = d["n"]
		var src: Sprite2D = d["src"]
		var s: Sprite3D = d["s"]
		if not is_instance_valid(n) or not is_instance_valid(src):
			continue
		var vis := n.visible and src.visible
		s.visible = vis
		if not vis:
			continue
		if s.texture != src.texture:
			s.texture = src.texture
			_set_offset(s, src.texture, src.offset)
		s.flip_h = src.flip_h
		s.scale = Vector3(src.scale.x * n.scale.x, src.scale.y * n.scale.y, 1.0)
		s.modulate = src.modulate * src.self_modulate
		_place(s, n.global_position)
	# camera: follows the 2D camera (already smoothed, with look-ahead and shake)
	var c2 := Game.camera
	if c2 != null:
		var t := c2.global_position + c2.offset
		var look := Vector3(t.x / T, 0.0, t.y / T)
		var pr := deg_to_rad(PITCH)
		cam.look_at_from_position(look + Vector3(0, sin(pr), cos(pr)) * dist, look, Vector3.UP)
	_update_light()


func _update_light() -> void:
	var m := world._mod.color if world._mod != null else Color.WHITE
	var outdoor: bool = world._outdoor
	var n := world.night_amount()
	var ang := Game.clock / World.DAY_LENGTH * TAU
	var elev := cos(ang)                                   # 1 noon .. -1 midnight
	var day := clampf(smoothstep(-0.15, 0.35, elev), 0.0, 1.0) if outdoor else 1.0
	sun.rotation_degrees = Vector3(-(24.0 + 40.0 * maxf(elev, 0.1)), (sin(ang) * 80.0) - 20.0, 0.0) if outdoor else Vector3(-58, -20, 0)
	sun.light_color = Color(1.0, 0.72, 0.5).lerp(Color(1.0, 0.97, 0.9), clampf(elev * 1.4, 0.0, 1.0)) if outdoor else Color(0.9, 0.9, 1.0)
	sun.light_energy = lerpf(0.2, 0.7, day)
	env.ambient_light_color = m.lerp(Color(0.5, 0.55, 0.85), n * 0.4) * lerpf(0.6, 0.62, day)
	env.ambient_light_energy = 1.0
