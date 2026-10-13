class_name World
extends Node2D
## Builds a map: baked ground chunks, y-sorted props with colliders, water blockers, exits, spawns.

const T := 64.0

var data: Dictionary
var bounds: Rect2
var ground: Node2D
var entities: Node2D
var fx_layer: Node2D
var walls: StaticBody2D
var _blocked := PackedByteArray()
var _t := 0.0
var _lights: Array = []
var _tall: Array = []     # [{n: Sprite2D, w, h}] big sprites that fade when the hero walks behind them
var _mod: CanvasModulate
var _base_tint := Color.WHITE
var _outdoor := false
var _flat: Node2D
var _has_water := false
var _rain: CPUParticles2D
var _thunder_t := 8.0
var _flash := 0.0
var _puddles: Array = []
const RAIN_MAPS := ["village", "valemont", "velmoor", "kharis", "mirewail", "wastelands"]
var _water_atlas: Image
var _reflect_mat: ShaderMaterial
var _last_prop: Node2D
var _stage_pending: Array = []     # wall-damage props not yet visible: spawned live when the story reaches their stage
var _wall_seen := 0
var _wall_cd := 0.0
var _night_glows: Array = []       # [{g: Sprite2D, a: float}] lit windows / door light, fade in at night
var _leaves: CPUParticles2D
var _splash_cd := 0.0
var _room_lights: Array = []   # [{l: PointLight2D, e: base energy, ph: phase}] interior lamps (flicker)

const NIGHT_WINDOWS := ["house_a", "house_b", "house_c", "house_e", "house_f", "tavern", "bakery", "apothecary", "guild", "smithy", "armory", "library", "stable", "barracks", "cathedral"]
const REFLECTED := ["tavern", "guild", "smithy", "bakery", "apothecary", "lamp", "stall", "well", "swamp_tree", "snow_pine", "palm", "city_tower", "bridge_lamp"]
const LEAF_MAPS := {
	"village": [Color(0.45, 0.78, 0.30), Color(1.0, 0.72, 0.82)], "valemont": [Color(0.55, 0.80, 0.32), Color(1.0, 0.82, 0.88)],
	"velmoor": [Color(0.40, 0.72, 0.38), Color(0.75, 0.95, 0.65)], "kharis": [Color(0.62, 0.74, 0.30), Color(0.95, 0.85, 0.50)],
	"mirewail": [Color(0.35, 0.50, 0.28), Color(0.55, 0.70, 0.40)], "peaks": [Color(0.95, 0.97, 1.0), Color(0.85, 0.92, 1.0)],
	"wastelands": [Color(0.55, 0.42, 0.30), Color(0.35, 0.30, 0.28)],
}

# furniture kind -> [color, radius (tiles), energy, height of the flame above the feet (px)]
const ROOM_LIGHTS := {
	"fireplace": [Color(1.0, 0.60, 0.28), 8.0, 1.25, 46.0], "forge": [Color(1.0, 0.48, 0.20), 7.5, 1.3, 50.0],
	"torch_stand": [Color(1.0, 0.76, 0.40), 5.5, 1.0, 84.0], "oven": [Color(1.0, 0.58, 0.26), 5.0, 1.0, 36.0],
	"cauldron": [Color(0.55, 1.0, 0.65), 3.8, 0.8, 34.0], "board": [Color(1.0, 0.85, 0.55), 4.0, 0.55, 70.0],
}

# kind -> [color, size (tiles), alpha, height above feet (tiles), flicker]
const LIGHTS := {
	"lamp": [Color(1, 0.82, 0.45), 2.8, 0.24, 1.55, 0.05],
	"torch_post": [Color(1, 0.65, 0.3), 3.2, 0.3, 1.3, 0.25],
	"brazier": [Color(1, 0.55, 0.2), 3.6, 0.34, 0.9, 0.3],
	"crystal_blue": [Color(0.4, 0.75, 1), 3.0, 0.3, 0.7, 0.08],
	"crystal_red": [Color(1, 0.4, 0.35), 3.0, 0.3, 0.7, 0.08],
	"bog_light": [Color(0.5, 1, 0.6), 2.6, 0.32, 1.0, 0.2],
	"mushrooms": [Color(0.5, 0.9, 1), 1.8, 0.2, 0.3, 0.1],
	"portal": [Color(0.6, 0.55, 1), 4.5, 0.35, 1.2, 0.1],
	"hell_gate": [Color(1, 0.3, 0.2), 6.0, 0.4, 1.5, 0.2],
	"mine_entrance": [Color(1, 0.7, 0.4), 3.4, 0.25, 1.0, 0.1],
	"cauldron": [Color(0.5, 1, 0.5), 2.4, 0.3, 0.7, 0.2],
	"anvil": [Color(1, 0.6, 0.3), 1.8, 0.2, 0.5, 0.2],
	"fountain": [Color(0.6, 0.85, 1), 3.0, 0.1, 1.0, 0.05],
	"glow_fern": [Color(0.4, 1, 0.85), 2.4, 0.2, 0.5, 0.15],
	"lamp_ornate": [Color(1, 0.82, 0.45), 3.4, 0.3, 2.2, 0.05],
	"tavern": [Color(1, 0.72, 0.32), 5.0, 0.22, 1.3, 0.1],
	"smithy": [Color(1, 0.5, 0.18), 4.2, 0.34, 0.9, 0.3],
	"library": [Color(0.7, 0.55, 1), 3.8, 0.24, 1.9, 0.1],
	"apothecary": [Color(0.5, 1, 0.6), 3.0, 0.16, 1.1, 0.1],
	"bakery": [Color(1, 0.75, 0.4), 3.0, 0.18, 1.0, 0.08],
	"armory": [Color(0.6, 0.75, 1), 2.8, 0.12, 1.0, 0.05],
	"house_f": [Color(1, 0.78, 0.4), 2.6, 0.14, 1.1, 0.06],
	"house_e": [Color(1, 0.78, 0.4), 3.0, 0.12, 1.0, 0.06],
}
# map -> [ambient tint, outdoor (follows the day/night cycle)]
const AMBIENT := {
	"village": [Color(1, 0.98, 0.93), true],
	"velmoor": [Color(0.8, 0.88, 0.98), true],
	"valemont": [Color(0.97, 0.97, 1.0), true],
	"kharis": [Color(1.0, 0.94, 0.82), true],
	"mines": [Color(0.55, 0.57, 0.72), false],
	"mirewail": [Color(0.72, 0.84, 0.78), false],
	"peaks": [Color(0.9, 0.95, 1.0), true],
	"castle": [Color(0.78, 0.78, 0.92), false],
	"wastelands": [Color(0.92, 0.66, 0.58), false],
	"citadel": [Color(0.56, 0.46, 0.74), false],
}
const DAY_LENGTH := 360.0
const NIGHT_TINT := Color(0.42, 0.5, 0.85)


static func load_map(name: String) -> World:
	var w := World.new()
	w.name = "World_" + name
	w.data = Sheets.read_json("Maps/" + name)
	w.build()
	return w


var shadow_layer: Node2D


func build() -> void:
	var d := data
	var tile := float(d["tile"])
	bounds = Rect2(0, 0, d["w"] * tile, d["h"] * tile)
	ground = Node2D.new()
	ground.z_index = -100
	add_child(ground)
	walls = StaticBody2D.new()
	walls.collision_layer = 1
	walls.collision_mask = 0
	add_child(walls)
	var flat_layer := Node2D.new()
	flat_layer.z_index = -90
	add_child(flat_layer)
	_flat = flat_layer
	shadow_layer = Node2D.new()
	shadow_layer.z_index = -80
	add_child(shadow_layer)
	shadow_layer.visible = Game.quality >= 1
	entities = Node2D.new()
	entities.y_sort_enabled = true
	add_child(entities)
	fx_layer = Node2D.new()
	fx_layer.z_index = 100
	add_child(fx_layer)

	if d.get("interior", false):
		_build_interior()
	for j in int(d["chunksY"]):
		for i in int(d["chunksX"]):
			var tx := Sheets.tex("Maps/%s/g_%d_%d" % [d["name"], i, j])
			if tx == null:
				continue
			var s := Sprite2D.new()
			s.texture = tx
			s.centered = false
			s.position = Vector2(i * d["chunk"], j * d["chunk"])
			ground.add_child(s)

	_build_water_fx(d)

	_blocked.resize(int(d["w"]) * int(d["h"]))
	var bs: String = d["blocked"]
	for k in mini(_blocked.size(), bs.length()):
		_blocked[k] = 1 if bs[k] == "1" else 0
	_build_water_colliders()
	var b := bounds
	_box(Vector2(b.get_center().x, -T * 0.5), Vector2(b.size.x + 2 * T, T))
	_box(Vector2(b.get_center().x, b.size.y + T * 0.5), Vector2(b.size.x + 2 * T, T))
	_box(Vector2(-T * 0.5, b.get_center().y), Vector2(T, b.size.y + 2 * T))
	_box(Vector2(b.size.x + T * 0.5, b.get_center().y), Vector2(T, b.size.y + 2 * T))

	for p in d["props"]:
		_spawn_prop(p, flat_layer)
	_wall_seen = Game.wall_stage() if str(d["name"]) == "valemont" else 0
	var am: Array = AMBIENT.get(d["name"], [Color(1.0, 0.94, 0.84), false] if d.get("interior", false) else [Color.WHITE, false])
	_base_tint = am[0]
	_outdoor = am[1]
	if d.get("interior", false) and Game.quality >= 1:
		_base_tint *= Color(0.66, 0.64, 0.72)      # dim rooms; the lamps and the hearth light them up
	_mod = CanvasModulate.new()
	_mod.color = _base_tint
	add_child(_mod)


## Interior room: procedural floor/walls plus furniture entities (y-sorted with the hero) and their colliders.
func _build_interior() -> void:
	var view := InteriorView.new()
	view.setup(data)
	ground.add_child(view)
	for f in data.get("furniture", []):
		var fu := Furniture.new()
		fu.kind = str(f["k"])
		fu.w = float(f.get("w", 1.0))
		fu.act = str(f.get("act", ""))
		fu.deco = str(f.get("deco", ""))
		fu.seed_v = int(f.get("seed_v", int(float(f["x"]) + float(f["y"]))))
		if f.has("tint"):
			fu.tint = Color(str(f["tint"]))
		fu.position = Vector2(float(f["x"]), float(f["y"]))
		entities.add_child(fu)
		if Game.quality >= 1 and ROOM_LIGHTS.has(fu.kind) and _room_lights.size() < 10:
			var rl: Array = ROOM_LIGHTS[fu.kind]
			var pl := PointLight2D.new()
			pl.texture = Util.soft_circle()
			pl.texture_scale = float(rl[1]) * T * 2.0 / 128.0
			pl.color = rl[0]
			pl.energy = float(rl[2])
			pl.position = Vector2(0, -float(rl[3]))
			fu.add_child(pl)
			_room_lights.append({"l": pl, "e": float(rl[2]), "ph": randf() * 20.0})
		if not f.get("nocol", false):
			var fp := Furniture.footprint(fu.kind, fu.w) * T
			_box(fu.position + Vector2(0, -fp.y * 0.5), fp)


func _box(center: Vector2, size: Vector2) -> void:
	var cs := CollisionShape2D.new()
	var r := RectangleShape2D.new()
	r.size = size
	cs.shape = r
	cs.position = center
	walls.add_child(cs)


func _build_water_colliders() -> void:
	var w := int(data["w"])
	var h := int(data["h"])
	var tile := float(data["tile"])
	for y in h:
		var x := 0
		while x < w:
			if _blocked[y * w + x] == 0:
				x += 1
				continue
			var x0 := x
			while x < w and _blocked[y * w + x] == 1:
				x += 1
			_box(Vector2((x0 + x) * 0.5 * tile, (y + 0.5) * tile), Vector2((x - x0) * tile * 0.92, tile * 0.92))


func _spawn_prop(p: Dictionary, flat_layer: Node2D) -> void:
	var kind: String = p["kind"]
	if p.has("stage") and Game.wall_stage() < int(p["stage"]):
		_stage_pending.append(p)
		return
	var info := Sheets.prop_info(kind)
	var tx := Sheets.prop_texture(kind)
	if tx == null:
		return
	var s := Sprite2D.new()
	_last_prop = s
	s.texture = tx
	s.centered = false
	s.offset = Vector2(-float(info.get("pivotX", tx.get_width() / 2)), -(float(info.get("h", tx.get_height())) - float(info.get("pivotY", 0))))
	var pos := Vector2(float(p["x"]), float(p["y"]))
	if kind in ["bridge", "flowers", "flower_bed", "wall_crack", "wall_cracks2", "wall_hole_s", "wall_hole_m", "wall_breach"]:
		s.position = pos
		flat_layer.add_child(s)
	else:
		s.position = pos
		entities.add_child(s)
		if info.has("colW") and int(info["colW"]) > 0:
			var cw := float(info["colW"])
			var ch := float(info["colH"])
			var cy := float(info["colY"])
			_box(pos + Vector2(float(info.get("colX", 0)), -(ch * 0.5 - cy)), Vector2(cw, ch))
	if Game.quality >= 1 and not kind.begins_with("wall_") and float(info.get("h", 0)) >= 110.0 and kind not in ["bridge", "flowers", "flower_bed", "tall_grass", "reeds", "fence", "city_gate"]:
		CastShadow.attach(s, true, clampf(float(info.get("h", 0)) / 260.0, 0.45, 1.0))
	if Game.quality >= 1:
		if kind.begins_with("tree") or kind in ["swamp_tree", "snow_pine", "palm"]:
			s.material = Util.wind_material("tree")
		elif kind.begins_with("bush") or kind in ["dry_shrub", "berry_bush", "hedge", "frost_shrub", "cactus"]:
			s.material = Util.wind_material("shrub")
		elif kind in ["tuft", "fern", "glow_fern", "tall_grass", "reeds"]:
			s.material = Util.wind_material("grass")
	if float(info.get("h", 0)) >= 200.0 and not (kind.begins_with("tree") or kind.begins_with("snow_pine") or kind == "swamp_tree"):
		_tall.append({"n": s, "w": float(info.get("w", 200)), "h": float(info.get("h", 200)), "px": float(info.get("pivotX", 100))})
	_ambient_for(kind, pos, info)
	if kind in REFLECTED or kind.begins_with("tree") or kind.begins_with("house"):
		_add_reflection(s, kind, pos)
	if Game.quality >= 1 and kind in NIGHT_WINDOWS:
		var h2 := float(info.get("h", 160))
		var w2 := float(info.get("w", 200))
		var win := Util.glow(s, Color(1.0, 0.72, 0.36), w2 * 0.0042, 0.0)
		win.position = Vector2(-w2 * 0.05, -h2 * 0.30)
		var spill := Util.glow(s, Color(1.0, 0.66, 0.30), w2 * 0.011, 0.0)
		spill.position = Vector2(w2 * 0.04, 26)
		spill.scale.y *= 0.45
		_night_glows.append({"g": win, "a": 0.75})
		_night_glows.append({"g": spill, "a": 0.42})
	if LIGHTS.has(kind):
		var L: Array = LIGHTS[kind]
		var g := Util.glow(s, L[0], L[1], L[2])
		g.position = Vector2(0, -float(L[3]) * T)
		_lights.append({"g": g, "a": L[2], "flick": L[4], "ph": randf() * 20.0})


## Animated water on top of the baked ground, from the 1/4-res masks (w_i_j.png) made by tools/art_hd/maps.py.
func _build_water_fx(d: Dictionary) -> void:
	var mat: ShaderMaterial = null
	var atlas := Image.create(maxi(1, int(d["chunksX"]) * 256), maxi(1, int(d["chunksY"]) * 256), false, Image.FORMAT_RGB8)
	for j in int(d["chunksY"]):
		for i in int(d["chunksX"]):
			if not ResourceLoader.exists("res://assets/Maps/%s/w_%d_%d.png" % [d["name"], i, j]):
				continue
			var tx := Sheets.tex("Maps/%s/w_%d_%d" % [d["name"], i, j])
			if mat == null:
				mat = ShaderMaterial.new()
				mat.shader = load("res://shaders/water_fx.gdshader")
			var mimg := tx.get_image()
			if mimg != null:
				if mimg.is_compressed():
					mimg.decompress()
				mimg.convert(Image.FORMAT_RGB8)
				atlas.blit_rect(mimg, Rect2i(Vector2i.ZERO, mimg.get_size()), Vector2i(i * 256, j * 256))
				_has_water = true
			var s := Sprite2D.new()
			s.texture = tx
			s.centered = false
			s.scale = Vector2(4, 4)
			s.position = Vector2(i * d["chunk"], j * d["chunk"])
			s.material = mat
			s.texture_filter = CanvasItem.TEXTURE_FILTER_LINEAR
			s.visible = Game.quality >= 2
			s.add_to_group("water_fx")
			ground.add_child(s)
	if _has_water:
		_water_atlas = atlas
		_reflect_mat = ShaderMaterial.new()
		_reflect_mat.shader = load("res://shaders/reflect.gdshader")
		_reflect_mat.set_shader_parameter("mask", ImageTexture.create_from_image(atlas))
		_reflect_mat.set_shader_parameter("world_px", Vector2(atlas.get_width() * 4.0, atlas.get_height() * 4.0))


func _water_south_of(pos: Vector2) -> bool:
	if _water_atlas == null:
		return false
	for k in [24.0, 56.0, 96.0, 140.0]:
		var px := Vector2i(int(pos.x / 4.0), int((pos.y + k) / 4.0))
		if px.x >= 0 and px.y >= 0 and px.x < _water_atlas.get_width() and px.y < _water_atlas.get_height():
			if _water_atlas.get_pixelv(px).r > 0.6:
				return true
	return false


func _add_reflection(s: Sprite2D, kind: String, pos: Vector2) -> void:
	if Game.quality < 2 or _reflect_mat == null or not _water_south_of(pos):
		return
	var r := Sprite2D.new()
	r.texture = s.texture
	r.centered = false
	r.offset = s.offset
	r.scale = Vector2(1.0, -0.72)
	r.z_index = -1
	r.material = _reflect_mat
	r.add_to_group("water_fx")
	s.add_child(r)


## Valemont wall: when the story advances while the hero is in the city the wall breaks live (rumble, dust, new cracks).
func _refresh_wall() -> void:
	if str(data.get("name", "")) != "valemont":
		return
	var st := Game.wall_stage()
	if st <= _wall_seen:
		return
	var from := _wall_seen
	_wall_seen = st
	var spawned: Array = []
	for p in _stage_pending.duplicate():
		if int(p["stage"]) <= st:
			_stage_pending.erase(p)
			_spawn_prop(p, _flat)
			spawned.append(Vector2(float(p["x"]), float(p["y"])))
	if from > 0 and not spawned.is_empty():
		if Game.camera != null:
			Game.camera.shake(0.9, 1.6)
		Sfx.play("boom", 0.6, 0.6)
		Fx.toast("Um estrondo ecoa das muralhas…", Color(1, 0.85, 0.6))
		for at in spawned:
			for k in 4:
				Fx.dust((at as Vector2) + Vector2(randf_range(-60, 60), randf_range(-40, 20)), 2.0)


## Puddles on the ground while it rains: pooled soft ellipses around the hero with small rings splashing in them.
func _update_puddles(rain: float, dt: float) -> void:
	if Game.quality < 1 or Player.I == null or bool(data.get("interior", false)) or not (str(data.get("name", "")) in RAIN_MAPS):
		return
	if _puddles.is_empty():
		if rain < 0.2:
			return
		for i in 16:
			var sp := Sprite2D.new()
			sp.texture = Util.soft_circle()
			sp.scale = Vector2(randf_range(0.8, 1.6), randf_range(0.28, 0.5))
			sp.z_index = -85
			sp.modulate = Color(0.72, 0.84, 1.0, 0.0)
			add_child(sp)
			_puddles.append({"n": sp, "s": randf()})
	var pp := Player.I.global_position
	for pd in _puddles:
		var n: Sprite2D = pd["n"]
		if n.global_position.distance_to(pp) > 1100.0 or n.global_position == Vector2.ZERO:
			for tries in 6:
				var at := pp + Vector2(randf_range(-950, 950), randf_range(-560, 560))
				var tx := int(at.x / T)
				var ty := int(at.y / T)
				if tx > 0 and ty > 0 and tx < int(data["w"]) - 1 and ty < int(data["h"]) - 1 and _blocked[ty * int(data["w"]) + tx] == 0:
					n.global_position = at
					break
		n.modulate.a = clampf((rain - 0.2) * 1.1, 0.0, 0.85) * (0.6 + 0.4 * sin(_t * 0.6 + float(pd["s"]) * 9.0))
		if rain > 0.4 and randf() < dt * 0.6 and n.modulate.a > 0.1 and Game.quality >= 2:
			Fx.shockwave(n.global_position + Vector2(randf_range(-30, 30), randf_range(-8, 8)), 0.12)


## Rain streaks around the hero + stronger wind; only on outdoor maps that can rain.
func _update_rain(rain: float) -> void:
	Sfx.set_rain(rain if _outdoor and not bool(data.get("interior", false)) else 0.0)
	_thunder_t -= get_process_delta_time()
	if rain > 0.6 and _outdoor and _thunder_t <= 0.0:
		_thunder_t = randf_range(14.0, 32.0)
		_flash = 1.0
		get_tree().create_timer(randf_range(0.3, 1.4)).timeout.connect(func(): Sfx.play("thunder", 0.55, randf_range(0.85, 1.05)))
	_flash = maxf(0.0, _flash - get_process_delta_time() * 3.0)
	for kind in ["tree", "shrub", "grass"]:
		Util.wind_material(kind).set_shader_parameter("boost", 1.0 + 1.3 * rain)
	if _rain == null and rain > 0.01 and Game.quality >= 1 and Player.I != null and str(data.get("name", "")) in RAIN_MAPS:
		_rain = CPUParticles2D.new()
		var img := Image.create(3, 30, false, Image.FORMAT_RGBA8)
		for y in 30:
			for x in 3:
				img.set_pixel(x, y, Color(1, 1, 1, float(y) / 30.0 * (1.0 if x == 1 else 0.6)))
		_rain.texture = ImageTexture.create_from_image(img)
		_rain.amount = 520
		_rain.lifetime = 0.55
		_rain.local_coords = false
		_rain.emission_shape = CPUParticles2D.EMISSION_SHAPE_RECTANGLE
		_rain.emission_rect_extents = Vector2(1100, 40)
		_rain.position = Vector2(0, -620)
		_rain.direction = Vector2(0.22, 1)
		_rain.spread = 3.0
		_rain.initial_velocity_min = 1100.0
		_rain.initial_velocity_max = 1300.0
		_rain.gravity = Vector2.ZERO
		_rain.angle_min = -12.0
		_rain.angle_max = -12.0
		_rain.color = Color(0.82, 0.92, 1.0, 0.85)
		_rain.z_index = 95
		_rain.add_to_group("rain_fx")
		Player.I.add_child(_rain)
	if _rain != null and is_instance_valid(_rain):
		_rain.emitting = rain > 0.05
		_rain.modulate.a = clampf(rain * 1.2, 0.0, 1.0)
		_rain.visible = Game.quality >= 1


## Drifting leaves / petals / snow carried by the wind (follows the hero; quality >= Medium).
func _setup_leaves() -> void:
	for old in Game.get_tree().get_nodes_in_group("rain_fx"):
		old.queue_free()
	for old in Game.get_tree().get_nodes_in_group("leaves_fx"):
		old.queue_free()
	if Game.quality < 1 or not LEAF_MAPS.has(str(data.get("name", ""))) or Player.I == null:
		return
	var cols: Array = LEAF_MAPS[str(data["name"])]
	var snow := str(data["name"]) == "peaks"
	_leaves = CPUParticles2D.new()
	_leaves.add_to_group("leaves_fx")
	_leaves.texture = Util.soft_circle()
	_leaves.amount = 22 if not snow else 40
	_leaves.lifetime = 7.0
	_leaves.preprocess = 7.0
	_leaves.local_coords = false
	_leaves.emission_shape = CPUParticles2D.EMISSION_SHAPE_RECTANGLE
	_leaves.emission_rect_extents = Vector2(1100, 640)
	_leaves.direction = Vector2(1, 0.25)
	_leaves.spread = 14.0
	_leaves.initial_velocity_min = 60.0
	_leaves.initial_velocity_max = 150.0
	_leaves.gravity = Vector2(0, 14)
	_leaves.angular_velocity_min = -160.0
	_leaves.angular_velocity_max = 160.0
	_leaves.scale_amount_min = 0.045
	_leaves.scale_amount_max = 0.11 if not snow else 0.07
	var g := Gradient.new()
	g.colors = PackedColorArray([cols[0], cols[1]])
	_leaves.color_initial_ramp = g
	_leaves.z_index = 90
	Player.I.add_child(_leaves)


func _update_leaves() -> void:
	if _leaves == null or not is_instance_valid(_leaves):
		return
	_leaves.visible = Game.quality >= 1
	var gust := 0.6 + 0.4 * sin(_t * 0.33)
	gust += Game.weather * 0.8
	_leaves.initial_velocity_min = 40.0 + 70.0 * gust
	_leaves.initial_velocity_max = 90.0 + 120.0 * gust
	_leaves.direction = Vector2(1, 0.25 + 0.2 * sin(_t * 0.5))


## Ripples and droplets when the hero walks along a bank.
func _water_splash(dt: float) -> void:
	_splash_cd -= dt
	if _splash_cd > 0.0 or Game.quality < 2 or Player.I == null or bool(data.get("interior", false)):
		return
	if Player.I.velocity.length() < 40.0 or str(data["name"]) not in ["village", "valemont", "velmoor", "kharis", "mirewail"]:
		return
	if str(data["name"]) == "valemont":
		var rr: float = (Player.I.global_position / T - Vector2(50, 50)).length()
		if rr > 28.0:
			return          # the city wall ring is blocked terrain too, not water
	var tw := int(data["w"])
	var th := int(data["h"])
	var tx := int(Player.I.global_position.x / T)
	var ty := int(Player.I.global_position.y / T)
	var near := false
	for dy in range(-1, 2):
		for dx in range(-1, 2):
			var x := tx + dx
			var y := ty + dy
			if x >= 0 and y >= 0 and x < tw and y < th and _blocked[y * tw + x] == 1:
				near = true
	if near:
		_splash_cd = 0.38
		Fx.shockwave(Player.I.global_position + Vector2(0, -4), 0.16)


func apply_quality() -> void:
	if shadow_layer != null:
		shadow_layer.visible = Game.quality >= 1
	for n in get_tree().get_nodes_in_group("water_fx"):
		n.visible = Game.quality >= 2


func add_entity(n: Node2D, at: Vector2) -> void:
	entities.add_child(n)
	n.global_position = at


## 0 = full day, 1 = deep night. Starts at day.
func night_amount() -> float:
	if not _outdoor:
		return 0.0
	return 0.5 - 0.5 * cos(Game.clock / DAY_LENGTH * TAU)


func _process(dt: float) -> void:
	_t += dt
	_fade_tall(dt)
	_update_sun()
	var n := night_amount()
	_mod.color = _base_tint.lerp(_base_tint * NIGHT_TINT, n * 0.85)
	var rain := Game.weather if _outdoor else 0.0
	if rain > 0.01:
		_mod.color *= Color(1.0 - 0.30 * rain, 1.0 - 0.22 * rain, 1.0 - 0.08 * rain)
	_update_rain(rain)
	if _flash > 0.0:
		var fl := _flash * (0.6 + 0.4 * sin(_flash * 40.0))
		_mod.color = Color(minf(_mod.color.r + fl * 0.8, 1.6), minf(_mod.color.g + fl * 0.8, 1.6), minf(_mod.color.b + fl, 1.8))
	_update_puddles(rain, dt)
	for ng in _night_glows:
		(ng["g"] as Sprite2D).modulate.a = float(ng["a"]) * maxf(n, (Game.weather if _outdoor else 0.0) * 0.65) * (0.92 + 0.08 * sin(_t * 3.1 + float(ng["g"].get_instance_id() % 17)))
	_wall_cd -= dt
	if _wall_cd <= 0.0:
		_wall_cd = 0.5
		_refresh_wall()
	_update_leaves()
	_water_splash(dt)
	for rl in _room_lights:
		var ph: float = rl["ph"]
		rl["l"].energy = float(rl["e"]) * (0.88 + 0.12 * sin(_t * 8.0 + ph) + 0.06 * sin(_t * 21.0 + ph * 2.0))
	for l in _lights:
		var fl := 1.0 + float(l["flick"]) * (sin(_t * 9.0 + l["ph"]) * 0.5 + sin(_t * 23.0 + l["ph"] * 2.0) * 0.5)
		l["g"].modulate.a = float(l["a"]) * fl * (1.0 + 1.6 * n)


## Sun for the cast shadows: noon = short shadows, sunrise / sunset = long ones pointing west / east, night = faint moon shadows.
func _update_sun() -> void:
	var m := Util.shadow_material()
	if bool(data.get("interior", false)):
		m.set_shader_parameter("shear", 0.42)
		m.set_shader_parameter("flat_k", 0.22)
		m.set_shader_parameter("strength", 0.30)
		return
	var ang := Game.clock / DAY_LENGTH * TAU
	var elev := cos(ang)                      # 1 at noon, -1 at midnight
	var day := smoothstep(-0.12, 0.35, elev)
	var shear_day := 0.18 + 0.95 * sin(ang)
	m.set_shader_parameter("shear", lerpf(-0.32, shear_day, day))
	m.set_shader_parameter("flat_k", lerpf(0.34, 0.20 + 0.42 * (1.0 - maxf(elev, 0.0)), day))
	m.set_shader_parameter("strength", lerpf(0.14, 0.42, day))
	if not _outdoor:
		m.set_shader_parameter("shear", 0.36)
		m.set_shader_parameter("flat_k", 0.24)
		m.set_shader_parameter("strength", 0.28)


func exit_at(w: Vector2) -> Dictionary:
	for e in data.get("exits", []):
		var r := Rect2(float(e["x"]) - float(e["w"]) / 2.0, float(e["y"]) - float(e["h"]) / 2.0, float(e["w"]), float(e["h"]))
		if r.has_point(w):
			return e
	return {}


## Regular spawns of the map plus the optional insectoid encounters (data/insect_spawns.json).
func all_spawns() -> Array:
	var list: Array = data["spawns"].duplicate()
	var f := FileAccess.open("res://data/insect_spawns.json", FileAccess.READ)
	if f:
		var extra = JSON.parse_string(f.get_as_text())
		list.append_array(extra.get(data["name"], []))
	return list


func spawn_actors() -> void:
	_setup_leaves()
	for s in all_spawns():
		Enemy.spawn(s["kind"], Vector2(float(s["x"]), float(s["y"])), int(s["level"]))
	for n in data["npcs"]:
		if n["id"] == "sylra" and Game.flags.has("sylra_joined"):
			continue
		Npc.spawn(n)
	for wk in data.get("walkers", []):
		Citizen.spawn(wk, str(data["name"]))
	var lvls := 0
	var cnt := 0
	for s in data["spawns"]:
		lvls += int(s["level"])
		cnt += 1
	for c in data.get("caches", []):
		TreasureCache.spawn(c, int(lvls / maxi(cnt, 1)))


func respawn_enemies() -> void:
	for s in all_spawns():
		var at := Vector2(float(s["x"]), float(s["y"]))
		var alive := false
		for e in Enemy.all:
			if not e.dead and (e.global_position - at).length() < 4.0 * T:
				alive = true
		if not alive:
			Enemy.spawn(s["kind"], at, int(s["level"]))


## Buildings turn translucent while the hero stands behind them, so roofs never hide the player.
func _fade_tall(dt: float) -> void:
	var p := Player.I
	if p == null:
		return
	var pp := p.global_position
	for t in _tall:
		var n: Sprite2D = t["n"]
		var d := pp - n.global_position
		var behind: bool = d.y < -8.0 and d.y > -float(t["h"]) * 0.92 and absf(d.x) < float(t["w"]) * 0.45
		var target := 0.42 if behind else 1.0
		if absf(n.modulate.a - target) > 0.01:
			n.modulate.a = move_toward(n.modulate.a, target, dt * 4.0)


var _emit_spots: Array = []     # [kind, Vector2] to avoid stacking identical emitters on neighbouring props


func _ambient_for(kind: String, pos: Vector2, info: Dictionary) -> void:
	var h := float(info.get("h", 100.0))
	var spec := ""
	var off := Vector2.ZERO
	match kind:
		"smithy": spec = "forge"; off = Vector2(40, -20)
		"tavern": spec = "crowd"; off = Vector2(0, -60)
		"fountain": spec = "water"; off = Vector2(0, -30)
		"stall", "stall_blue", "stall_green": spec = "market"; off = Vector2(0, -40)
		"bakery", "apothecary", "house_a", "house_b", "house_c", "house_e", "house_f":
			if randf() < 0.3 or kind == "bakery":
				spec = "smoke"; off = Vector2(0, -h * 0.86)
	if spec == "":
		return
	if spec == "market" or spec == "smoke":
		for s in _emit_spots:
			if s[0] == spec and spec == "market" and (s[1] as Vector2).distance_to(pos) < 9.0 * T:
				return
	_emit_spots.append([spec, pos])
	AmbientEmitter.spawn(spec, pos + off, entities)
