class_name World
extends Node2D
## Renders a MapData: baked ground, animated water, colliders, objects, entities, camera.

const T := 32
var map: MapData
var ground_sprite: Sprite2D
var water_sprite: Sprite2D
var entities: Node2D
var walls: StaticBody2D
var cam: Camera2D
var player: Player
var fx_layer: Node2D
var enemies: Array[Enemy] = []
var pickups_node: Node2D
var cam_shake := 0.0
var astar: AStarGrid2D
var story_hook: Callable = Callable()

func load_map(m: MapData, spawn_tile: Vector2i) -> void:
	for c in get_children():
		c.queue_free()
	map = m
	var baked := GroundBaker.bake(m)
	water_sprite = Sprite2D.new()
	water_sprite.centered = false
	water_sprite.z_index = -20
	var white := GradientTexture2D.new()
	white.width = 4
	white.height = 4
	white.gradient = Gradient.new()
	white.gradient.set_color(0, Color.WHITE)
	white.gradient.set_color(1, Color.WHITE)
	water_sprite.texture = white
	water_sprite.scale = Vector2(m.w * T / 4.0, m.h * T / 4.0)
	var sm := ShaderMaterial.new()
	sm.shader = load("res://src/world/water.gdshader")
	sm.set_shader_parameter("water_atlas", Terrain.water_tex)
	sm.set_shader_parameter("mask", baked["water_mask"])
	sm.set_shader_parameter("map_cells", Vector2(m.w, m.h))
	water_sprite.material = sm
	add_child(water_sprite)
	ground_sprite = Sprite2D.new()
	ground_sprite.centered = false
	ground_sprite.texture = baked["ground"]
	ground_sprite.z_index = -19
	ground_sprite.material = _ground_material(m)
	add_child(ground_sprite)
	_build_colliders()
	entities = Node2D.new()
	entities.y_sort_enabled = true
	add_child(entities)
	fx_layer = Node2D.new()
	fx_layer.z_index = 10
	add_child(fx_layer)
	_build_objects()
	_build_astar()
	enemies.clear()
	player = Player.new()
	player.world = self
	player.position = Vector2(spawn_tile.x * T + 16, spawn_tile.y * T + 28)
	entities.add_child(player)
	var sh := Fx.ShieldFx.new()
	sh.owner_p = player
	player.add_child(sh)
	cam = Camera2D.new()
	cam.zoom = Vector2(2, 2)
	cam.position_smoothing_enabled = true
	cam.position_smoothing_speed = 8.0
	cam.limit_left = 0
	cam.limit_top = 0
	cam.limit_right = m.w * T
	cam.limit_bottom = m.h * T
	player.add_child(cam)
	cam.make_current()

func _ground_material(m: MapData) -> ShaderMaterial:
	var noise := FastNoiseLite.new()
	noise.noise_type = FastNoiseLite.TYPE_SIMPLEX_SMOOTH
	noise.frequency = 0.02
	noise.fractal_octaves = 3
	noise.seed = hash(m.id)
	var img := noise.get_image(256, 256, false, true, true)
	var sm := ShaderMaterial.new()
	sm.shader = load("res://src/world/ground.gdshader")
	sm.set_shader_parameter("noise_tex", ImageTexture.create_from_image(img))
	sm.set_shader_parameter("map_px", Vector2(m.w * T, m.h * T))
	sm.set_shader_parameter("clouds", 0.0 if m.indoor or m.dark > 0.2 else 0.12)
	return sm

func _solid_grid() -> PackedByteArray:
	var g := PackedByteArray()
	g.resize(map.w * map.h)
	for y in map.h:
		for x in map.w:
			var i := y * map.w + x
			if Terrain.is_solid(map.name_at(x, y)) or map.extra_solid[i] != 0:
				g[i] = 1
	for o in map.objs:
		if o.get("deco", false):
			continue
		var d := ObjectLib.get_def(o["type"])
		if _has_foot(d):
			continue
		for c in d.get("cells", [[0, 0]]):
			if d.has("door") and int(c[0]) == int(d["door"][0]) and int(c[1]) == int(d["door"][1]):
				continue
			var x: int = o["tx"] + int(c[0])
			var y: int = o["ty"] + int(c[1])
			if map.inb(x, y):
				g[y * map.w + x] = 1
	return g

func _has_foot(d: Dictionary) -> bool:
	return d.has("foot") and float(d["foot"][2]) > 0.0

func _build_colliders() -> void:
	walls = StaticBody2D.new()
	walls.collision_layer = 1
	walls.collision_mask = 0
	add_child(walls)
	var g := _solid_grid()
	# merge horizontal runs
	for y in map.h:
		var x := 0
		while x < map.w:
			if g[y * map.w + x] == 1:
				var x1 := x
				while x1 + 1 < map.w and g[y * map.w + x1 + 1] == 1:
					x1 += 1
				var cs := CollisionShape2D.new()
				var r := RectangleShape2D.new()
				r.size = Vector2((x1 - x + 1) * T, T)
				cs.shape = r
				cs.position = Vector2((x + (x1 - x + 1) / 2.0) * T, y * T + T / 2.0)
				walls.add_child(cs)
				x = x1 + 1
			else:
				x += 1

var anim_objs: Array = []
var light_tex: GradientTexture2D

func _get_light_tex() -> GradientTexture2D:
	if light_tex == null:
		light_tex = GradientTexture2D.new()
		light_tex.width = 256
		light_tex.height = 256
		light_tex.fill = GradientTexture2D.FILL_RADIAL
		light_tex.fill_from = Vector2(0.5, 0.5)
		light_tex.fill_to = Vector2(1.0, 0.5)
		var g := Gradient.new()
		g.set_color(0, Color(1, 1, 1, 1))
		g.add_point(0.5, Color(1, 1, 1, 0.45))
		g.set_color(g.get_point_count() - 1, Color(1, 1, 1, 0))
		light_tex.gradient = g
	return light_tex

func _build_objects() -> void:
	anim_objs.clear()
	for o in map.objs:
		var tex := ObjectLib.texture(o["type"])
		if tex == null:
			continue
		var d := ObjectLib.get_def(o["type"])
		var frames: int = int(d.get("frames", 1))
		var s := Sprite2D.new()
		s.texture = tex
		s.hframes = frames
		var anchor: Array = d.get("anchor", [tex.get_width() / frames / 2.0, tex.get_height()])
		s.centered = false
		s.offset = Vector2(-anchor[0], -anchor[1])
		var base := Vector2(o["tx"] * T + T / 2.0, (o["ty"] + 1) * T)
		if d.has("anchor_off"):
			base += Vector2(d["anchor_off"][0], d["anchor_off"][1])
		s.position = base
		entities.add_child(s)
		if frames > 1:
			s.frame = randi() % frames
			anim_objs.append({"s": s, "fps": float(d.get("fps", 6)), "frames": frames, "t": randf() * 3.0})
		if _has_foot(d):
			var f: Array = d["foot"]
			var cs := CollisionShape2D.new()
			var r := RectangleShape2D.new()
			r.size = Vector2(f[2], f[3])
			cs.shape = r
			cs.position = base + Vector2(f[0] + f[2] / 2.0, f[1] + f[3] / 2.0)
			walls.add_child(cs)
		if d.has("light"):
			var L: Dictionary = d["light"]
			var glow := Sprite2D.new()
			glow.texture = _get_light_tex()
			var sc: float = float(L["r"]) * 2.0 / 256.0
			glow.scale = Vector2(sc, sc)
			glow.modulate = Color(Color(L["color"]), 0.38)
			var mat := CanvasItemMaterial.new()
			mat.blend_mode = CanvasItemMaterial.BLEND_MODE_ADD
			glow.material = mat
			glow.position = base + Vector2(0, float(L.get("dy", -16)))
			glow.z_index = 5
			add_child(glow)
			if L.get("flicker", false):
				anim_objs.append({"glow": glow, "t": randf() * 6.0, "sc": sc})

func _build_astar() -> void:
	astar = AStarGrid2D.new()
	astar.region = Rect2i(0, 0, map.w, map.h)
	astar.cell_size = Vector2(T, T)
	astar.diagonal_mode = AStarGrid2D.DIAGONAL_MODE_ONLY_IF_NO_OBSTACLES
	astar.update()
	var g := _solid_grid()
	for o in map.objs:
		if o.get("deco", false):
			continue
		var d := ObjectLib.get_def(o["type"])
		if _has_foot(d):
			var f: Array = d["foot"]
			var cx := int((o["tx"] * T + T / 2.0 + f[0] + f[2] / 2.0) / T)
			var cy := int(((o["ty"] + 1) * T + f[1] + f[3] / 2.0) / T)
			if map.inb(cx, cy):
				g[cy * map.w + cx] = 1
	for y in map.h:
		for x in map.w:
			if g[y * map.w + x] == 1:
				astar.set_point_solid(Vector2i(x, y), true)

func find_path(from: Vector2, to: Vector2) -> Array:
	var a := Vector2i(clampi(int(from.x / T), 0, map.w - 1), clampi(int(from.y / T), 0, map.h - 1))
	var b := Vector2i(clampi(int(to.x / T), 0, map.w - 1), clampi(int(to.y / T), 0, map.h - 1))
	if astar.is_point_solid(b):
		return []
	if astar.is_point_solid(a):
		return []
	var pts := astar.get_point_path(a, b)
	var out: Array = []
	for p in pts:
		out.append(p + Vector2(T / 2.0, T / 2.0 + 6.0))
	if not out.is_empty():
		out.pop_front()
	return out

func has_los(a: Vector2, b: Vector2) -> bool:
	var q := PhysicsRayQueryParameters2D.create(a, b, 1)
	return get_world_2d().direct_space_state.intersect_ray(q).is_empty()

func is_solid_at(p: Vector2) -> bool:
	var cx := int(floorf(p.x / T))
	var cy := int(floorf(p.y / T))
	if not map.inb(cx, cy):
		return true
	return astar.is_point_solid(Vector2i(cx, cy))

func later(delay: float, fn: Callable) -> void:
	get_tree().create_timer(delay).timeout.connect(fn)

func spawn_enemy(id: String, pos: Vector2, elite := false, boss := false, spawn_id := "") -> Enemy:
	var e := Enemy.new()
	e.position = pos
	e.spawn_id = spawn_id
	entities.add_child(e)
	e.setup(self, id, elite, boss)
	enemies.append(e)
	return e

func spawn_pickup(kind: String, id: String, amount: int, pos: Vector2, gear := {}) -> void:
	var p := Pickup.new()
	p.kind = kind
	p.item_id = id
	p.amount = amount
	p.gear = gear
	p.world = self
	p.position = pos
	entities.add_child(p)

func explosion(pos: Vector2, r: float, dmg: float, elem: String, opts: Dictionary, from_player: bool) -> void:
	var col: Color = Data.ELEM_COLORS.get(elem, Color.WHITE)
	Fx.glow_flash(self, pos + Vector2(0, -8), col, r * 3.2, 0.3)
	Fx.ring(self, pos, r, col, 0.4, 0.25)
	Fx.ring(self, pos, r * 0.6, Color.WHITE, 0.3)
	Fx.burst(self, pos + Vector2(0, -6), [col, Color("ffd84a"), Color.WHITE], 22, 150.0, 0.55, 3.5, 80.0)
	Fx.shake(self, 4.0)
	Sfx.play("explosion", -3.0)
	if from_player:
		for e in enemies.duplicate():
			if not e.dead and e.global_position.distance_to(pos) < r + e.radius:
				var h: Dictionary = player.make_hit(dmg, elem)
				h["kb"] = float(opts.get("kb", 90.0))
				h["src"] = pos
				h["heavy"] = true
				h["poise"] = 1.5
				for k in ["burn", "slow", "freeze"]:
					if opts.has(k):
						h[k] = opts[k]
				e.take_hit(h)
		if int(opts.get("tier", 1)) >= 2 and elem == "fire":
			burn_patch(pos, r * 0.8, 3.0, dmg * 0.12)
	else:
		if player.global_position.distance_to(pos) < r + 8.0:
			player.take_hit({"dmg": dmg, "src": pos, "kb": 140.0, "elem": elem})

class BurnPatch extends Node2D:
	var r := 30.0
	var life := 3.0
	var dps := 4.0
	var w: World
	var tick := 0.0
	var t := 0.0
	func _process(dt: float) -> void:
		t += dt
		life -= dt
		tick -= dt
		if life <= 0.0:
			queue_free()
			return
		if tick <= 0.0:
			tick = 0.5
			for e in w.enemies.duplicate():
				if not e.dead and e.global_position.distance_to(global_position) < r + e.radius:
					e.on_dot(dps, "fire")
					e.apply_status("burn", 2.0, dps)
		if randf() < 0.6:
			Fx.embers(w, global_position + Vector2(randf_range(-r, r), randf_range(-r, r) * 0.6), 1)
		queue_redraw()
	func _draw() -> void:
		var a: float = clampf(life / 1.0, 0.0, 1.0)
		draw_set_transform(Vector2.ZERO, 0, Vector2(1, 0.62))
		draw_circle(Vector2.ZERO, r, Color(1.0, 0.4, 0.1, 0.18 * a))
		draw_arc(Vector2.ZERO, r, 0, TAU, 36, Color(1.0, 0.6, 0.2, 0.6 * a), 2.0, true)

func burn_patch(pos: Vector2, r: float, life: float, dps: float) -> void:
	var b := BurnPatch.new()
	b.w = self
	b.r = r
	b.life = life
	b.dps = dps
	b.position = pos
	b.z_index = 2
	b.material = Fx.add_mat()
	fx_layer.add_child(b)

func meteor_strike(pos: Vector2, r: float, dmg: float, tier: int, p: Player) -> void:
	var m := Sprite2D.new()
	m.texture = Fx.glow_tex()
	m.material = Fx.add_mat()
	m.modulate = Color("ff8a2a")
	m.scale = Vector2.ONE * 1.8
	m.position = pos + Vector2(-120, -260)
	m.z_index = 40
	fx_layer.add_child(m)
	var tw := m.create_tween()
	tw.tween_property(m, "position", pos + Vector2(0, -6), 0.6).set_ease(Tween.EASE_IN)
	tw.tween_callback(func():
		m.queue_free()
		Fx.shake(self, 10.0)
		explosion(pos, r, dmg, "fire", {"burn": 4.0, "kb": 170.0, "tier": tier}, true)
		for i in 3:
			Fx.ring(self, pos, r * (1.0 + i * 0.3), Color("ff8a2a"), 0.5 + i * 0.1)
		crack_decal(pos, r * 0.9))
	# trail while falling
	var trail := func():
		if is_instance_valid(m):
			Fx.burst(self, m.position, [Color("ff8a2a"), Color("ffd84a")], 3, 25.0, 0.4, 5.0)
	for i in 12:
		later(0.05 * i, trail)

class CrackFx extends Node2D:
	var r := 40.0
	var t := 0.0
	var seeds: Array = []
	func _ready() -> void:
		for i in 7:
			seeds.append([randf() * TAU, randf_range(0.6, 1.0), randf_range(-0.4, 0.4)])
	func _process(dt: float) -> void:
		t += dt
		if t > 4.0:
			queue_free()
		queue_redraw()
	func _draw() -> void:
		var f: float = clampf(t / 0.18, 0.0, 1.0)
		var a: float = 1.0 if t < 3.0 else (4.0 - t)
		draw_set_transform(Vector2.ZERO, 0, Vector2(1, 0.62))
		for s in seeds:
			var pts := PackedVector2Array([Vector2.ZERO])
			var ang: float = s[0]
			var cur := Vector2.ZERO
			for i in 5:
				ang += s[2] * (1 if i % 2 == 0 else -1)
				cur += Vector2.from_angle(ang) * r * s[1] * 0.2 * f
				pts.append(cur)
			draw_polyline(pts, Color(0.12, 0.06, 0.04, 0.9 * a), 3.0, true)
			draw_polyline(pts, Color(1.0, 0.55, 0.2, 0.7 * a), 1.2, true)

func crack_decal(pos: Vector2, r: float) -> void:
	var c := CrackFx.new()
	c.r = r
	c.position = pos
	c.z_index = -5
	fx_layer.add_child(c)

func ice_spikes(pos: Vector2, r: float) -> void:
	for i in 9:
		var a := TAU * i / 9.0 + randf() * 0.4
		var p := pos + Vector2.from_angle(a) * r * randf_range(0.5, 1.0)
		later(0.04 * i, func():
			Fx.burst(self, p, [Color("8ae0ff"), Color.WHITE], 6, 60.0, 0.5, 3.0, 80.0)
			Fx.glow_flash(self, p + Vector2(0, -10), Color("8ae0ff"), 40.0, 0.3))

func on_enemy_killed(e: Enemy) -> void:
	if story_hook.is_valid():
		story_hook.call("kill", e)

func on_player_died() -> void:
	if story_hook.is_valid():
		story_hook.call("player_died", null)

func story_item_picked(id: String) -> void:
	if story_hook.is_valid():
		story_hook.call("item", id)

func _process(dt: float) -> void:
	# camera shake
	if cam_shake > 0.01:
		cam.offset = Vector2(randf_range(-1, 1), randf_range(-1, 1)) * cam_shake
		cam_shake = maxf(0.0, cam_shake - dt * 18.0)
	elif cam:
		cam.offset = Vector2.ZERO
	for a in anim_objs:
		a["t"] += dt
		if a.has("s"):
			a["s"].frame = int(a["t"] * a["fps"]) % int(a["frames"])
		elif a.has("glow"):
			var k: float = a["sc"] * (1.0 + sin(a["t"] * 11.0) * 0.04 + sin(a["t"] * 27.0) * 0.03)
			a["glow"].scale = Vector2(k, k)
