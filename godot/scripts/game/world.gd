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
var _swaying: Array[Node2D] = []
var _t := 0.0
var _lights: Array = []
var _tall: Array = []     # [{n: Sprite2D, w, h}] big sprites that fade when the hero walks behind them
var _mod: CanvasModulate
var _base_tint := Color.WHITE
var _outdoor := false

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
	shadow_layer = Node2D.new()
	shadow_layer.z_index = -80
	add_child(shadow_layer)
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
	var am: Array = AMBIENT.get(d["name"], [Color(1.0, 0.94, 0.84), false] if d.get("interior", false) else [Color.WHITE, false])
	_base_tint = am[0]
	_outdoor = am[1]
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
	var info := Sheets.prop_info(kind)
	var tx := Sheets.prop_texture(kind)
	if tx == null:
		return
	var s := Sprite2D.new()
	s.texture = tx
	s.centered = false
	s.offset = Vector2(-float(info.get("pivotX", tx.get_width() / 2)), -(float(info.get("h", tx.get_height())) - float(info.get("pivotY", 0))))
	var pos := Vector2(float(p["x"]), float(p["y"]))
	if kind == "bridge" or kind == "flowers" or kind == "flower_bed":
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
	if float(info.get("h", 0)) >= 110.0 and kind not in ["bridge", "flowers", "flower_bed", "tall_grass", "reeds", "fence", "city_gate"]:
		CastShadow.attach(s, true, clampf(float(info.get("h", 0)) / 260.0, 0.45, 1.0))
	if kind.begins_with("tree") or kind.begins_with("bush") or kind in ["tuft", "swamp_tree", "snow_pine", "fern", "glow_fern", "tall_grass", "dry_shrub", "berry_bush", "hedge", "frost_shrub"]:
		_swaying.append(s)
	if float(info.get("h", 0)) >= 200.0 and not (kind.begins_with("tree") or kind.begins_with("snow_pine") or kind == "swamp_tree"):
		_tall.append({"n": s, "w": float(info.get("w", 200)), "h": float(info.get("h", 200)), "px": float(info.get("pivotX", 100))})
	_ambient_for(kind, pos, info)
	if LIGHTS.has(kind):
		var L: Array = LIGHTS[kind]
		var g := Util.glow(s, L[0], L[1], L[2])
		g.position = Vector2(0, -float(L[3]) * T)
		_lights.append({"g": g, "a": L[2], "flick": L[4], "ph": randf() * 20.0})


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
	for l in _lights:
		var fl := 1.0 + float(l["flick"]) * (sin(_t * 9.0 + l["ph"]) * 0.5 + sin(_t * 23.0 + l["ph"] * 2.0) * 0.5)
		l["g"].modulate.a = float(l["a"]) * fl * (1.0 + 1.6 * n)
	for s in _swaying:
		var ph := s.position.x * 0.0055 + s.position.y * 0.003
		var a := sin(_t * 1.3 + ph) * 0.9 + sin(_t * 2.9 + ph * 1.7) * 0.35
		s.rotation = deg_to_rad(a)


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
