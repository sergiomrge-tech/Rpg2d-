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
	entities = Node2D.new()
	entities.y_sort_enabled = true
	add_child(entities)
	fx_layer = Node2D.new()
	fx_layer.z_index = 100
	add_child(fx_layer)

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
	var am: Array = AMBIENT.get(d["name"], [Color.WHITE, false])
	_base_tint = am[0]
	_outdoor = am[1]
	_mod = CanvasModulate.new()
	_mod.color = _base_tint
	add_child(_mod)


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
	if kind == "bridge" or kind == "flowers":
		s.position = pos
		flat_layer.add_child(s)
	else:
		s.position = pos
		entities.add_child(s)
		if info.has("colW") and int(info["colW"]) > 0:
			var cw := float(info["colW"])
			var ch := float(info["colH"])
			var cy := float(info["colY"])
			_box(pos + Vector2(0, -(ch * 0.5 - cy)), Vector2(cw, ch))
	if kind.begins_with("tree") or kind.begins_with("bush") or kind == "tuft" or kind == "swamp_tree" or kind == "snow_pine":
		_swaying.append(s)
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
	return 0.5 - 0.5 * cos(Game.time() / DAY_LENGTH * TAU)


func _process(dt: float) -> void:
	_t += dt
	var n := night_amount()
	_mod.color = _base_tint.lerp(_base_tint * NIGHT_TINT, n * 0.85)
	for l in _lights:
		var fl := 1.0 + float(l["flick"]) * (sin(_t * 9.0 + l["ph"]) * 0.5 + sin(_t * 23.0 + l["ph"] * 2.0) * 0.5)
		l["g"].modulate.a = float(l["a"]) * fl * (1.0 + 1.6 * n)
	for s in _swaying:
		var ph := s.position.x * 0.0055 + s.position.y * 0.003
		var a := sin(_t * 1.3 + ph) * 0.9 + sin(_t * 2.9 + ph * 1.7) * 0.35
		s.rotation = deg_to_rad(a)


func exit_at(w: Vector2) -> Dictionary:
	for e in data.get("exits", []):
		var r := Rect2(float(e["x"]) - float(e["w"]) / 2.0, float(e["y"]) - float(e["h"]) / 2.0, float(e["w"]), float(e["h"]))
		if r.has_point(w):
			return e
	return {}


func spawn_actors() -> void:
	for s in data["spawns"]:
		Enemy.spawn(s["kind"], Vector2(float(s["x"]), float(s["y"])), int(s["level"]))
	for n in data["npcs"]:
		if n["id"] == "sylra" and Game.flags.has("sylra_joined"):
			continue
		Npc.spawn(n)


func respawn_enemies() -> void:
	for s in data["spawns"]:
		var at := Vector2(float(s["x"]), float(s["y"]))
		var alive := false
		for e in Enemy.all:
			if not e.dead and (e.global_position - at).length() < 4.0 * T:
				alive = true
		if not alive:
			Enemy.spawn(s["kind"], at, int(s["level"]))
