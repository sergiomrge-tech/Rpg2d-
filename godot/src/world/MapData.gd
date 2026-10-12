class_name MapData
extends RefCounted
## Tile grid + object lists for one map; includes procedural-building helpers.

var id := ""
var title := ""
var w := 0
var h := 0
var ground := PackedInt32Array()
var variant := PackedInt32Array()
var extra_solid := PackedByteArray()     # collision without visuals / blocked cells
var occ := PackedByteArray()             # object occupancy (for scatter)
var objs: Array = []                     # {type, tx, ty, v, ...}
var npcs: Array = []
var chests: Array = []
var warps: Array = []
var triggers: Array = []
var spawns: Array = []
var barriers: Array = []
var signs: Array = []
var lights: Array = []
var rng := RandomNumberGenerator.new()
var music := ""
var dark := 0.0
var ambient := "none"
var tint := Color.WHITE
var indoor := false
var start := Vector2i.ZERO
var region := "field"

func _init(p_id: String, p_title: String, p_w: int, p_h: int, fill: String, seed_v: int = 1) -> void:
	Terrain.setup()
	id = p_id
	title = p_title
	w = p_w
	h = p_h
	rng.seed = seed_v
	ground.resize(w * h)
	variant.resize(w * h)
	extra_solid.resize(w * h)
	occ.resize(w * h)
	ground.fill(Terrain.id(fill))
	for i in w * h:
		variant[i] = rng.randi_range(0, 3)

func inb(x: int, y: int) -> bool:
	return x >= 0 and y >= 0 and x < w and y < h

func name_at(x: int, y: int) -> String:
	if not inb(x, y):
		return Terrain.VOID
	return Terrain.names[ground[y * w + x]]

func set_t(t: String, x: int, y: int) -> void:
	if inb(x, y):
		ground[y * w + x] = Terrain.id(t)

func fill_rect(t: String, x: int, y: int, ww: int, hh: int) -> void:
	for j in hh:
		for i in ww:
			set_t(t, x + i, y + j)

func outline(t: String, x: int, y: int, ww: int, hh: int) -> void:
	for i in ww:
		set_t(t, x + i, y)
		set_t(t, x + i, y + hh - 1)
	for j in hh:
		set_t(t, x, y + j)
		set_t(t, x + ww - 1, y + j)

func blob(t: String, cx: float, cy: float, rx: float, ry: float, jitter := 0.25, only_on: Array = []) -> void:
	for y in range(int(cy - ry - 2), int(cy + ry + 3)):
		for x in range(int(cx - rx - 2), int(cx + rx + 3)):
			var dx := (x - cx) / rx
			var dy := (y - cy) / ry
			var n := (rng.randf() - 0.5) * jitter
			if dx * dx + dy * dy + n <= 1.0 and inb(x, y):
				if only_on.is_empty() or name_at(x, y) in only_on:
					set_t(t, x, y)

func path(t: String, pts: Array, width := 2, wobble := 0.0) -> void:
	for i in pts.size() - 1:
		var a: Vector2 = pts[i]
		var b: Vector2 = pts[i + 1]
		var n: int = int(maxf(absf(b.x - a.x), absf(b.y - a.y)) * 2.0)
		for k in n + 1:
			var f: float = float(k) / float(maxi(1, n))
			var wv: float = sin(f * 6.0 + i) * wobble
			var vertical: bool = abs(b.x - a.x) < abs(b.y - a.y)
			var x: float = a.x + (b.x - a.x) * f + (wv if vertical else 0.0)
			var y: float = a.y + (b.y - a.y) * f + (0.0 if vertical else wv)
			for aa in width:
				for bb in width:
					set_t(t, roundi(x - width / 2.0 + aa + 0.5), roundi(y - width / 2.0 + bb + 0.5))

func patches(t: String, n: int, rmin: float, rmax: float, only_on: Array = []) -> void:
	for i in n:
		blob(t, rng.randf_range(2, w - 2), rng.randf_range(2, h - 2), rng.randf_range(rmin, rmax), rng.randf_range(rmin, rmax) * 0.8, 0.6, only_on)

func scatter_tiles(t: String, n: int, only_on: Array) -> void:
	for i in n:
		var x := rng.randi_range(0, w - 1)
		var y := rng.randi_range(0, h - 1)
		if name_at(x, y) in only_on:
			set_t(t, x, y)

func is_free(tx: int, ty: int) -> bool:
	if not inb(tx, ty):
		return false
	if Terrain.is_solid(name_at(tx, ty)):
		return false
	return occ[ty * w + tx] == 0 and extra_solid[ty * w + tx] == 0

## Place an object. footprint cells come from ObjectLib.
func add_obj(type: String, tx: int, ty: int, v := 0, opts := {}) -> Dictionary:
	var d := ObjectLib.get_def(type)
	var fp: Array = d.get("cells", [[0, 0]])
	for c in fp:
		var x: int = tx + int(c[0])
		var y: int = ty + int(c[1])
		if inb(x, y):
			occ[y * w + x] = 1
	var o := {"type": type, "tx": tx, "ty": ty, "v": v}
	o.merge(opts, true)
	objs.append(o)
	return o

func block(x: int, y: int, ww: int, hh: int) -> void:
	for j in hh:
		for i in ww:
			if inb(x + i, y + j):
				extra_solid[(y + j) * w + x + i] = 1

func unblock(x: int, y: int, ww := 1, hh := 1) -> void:
	for j in hh:
		for i in ww:
			if inb(x + i, y + j):
				extra_solid[(y + j) * w + x + i] = 0
				occ[(y + j) * w + x + i] = 0

func scatter(types: Array, n: int, x0: int, y0: int, x1: int, y1: int, opts := {}) -> void:
	var placed := 0
	var tries := 0
	var gap: int = opts.get("gap", 1)
	var grounds: Array = opts.get("grounds", [])
	var avoid: Array = opts.get("avoid", [])
	var open: bool = opts.get("open", false)
	var vmax: int = opts.get("vmax", 2)
	while placed < n and tries < n * 30:
		tries += 1
		var x := rng.randi_range(x0, x1)
		var y := rng.randi_range(y0, y1)
		if not is_free(x, y):
			continue
		if not grounds.is_empty() and not (name_at(x, y) in grounds):
			continue
		var bad := false
		for a in avoid:
			if Vector2(a.x, a.y).distance_to(Vector2(x, y)) < a.r:
				bad = true
				break
		if bad:
			continue
		for j in range(-gap, gap + 1):
			for i in range(-gap, gap + 1):
				if inb(x + i, y + j) and occ[(y + j) * w + x + i] != 0:
					bad = true
		if bad:
			continue
		if open:
			for j in range(-1, 2):
				for i in range(-1, 2):
					if not is_free(x + i, y + j):
						bad = true
			if bad:
				continue
		add_obj(types[rng.randi() % types.size()], x, y, rng.randi_range(0, vmax))
		placed += 1

## Tree wall around the map (visual trees + solid ring) with gaps.
func tree_border(thick: int, gaps: Array, kinds: Array = ["tree", "tree", "pine"]) -> void:
	for y in h:
		for x in w:
			var edge := x < thick or y < thick or x >= w - thick or y >= h - thick
			if edge and not _in_gap(gaps, x, y):
				extra_solid[y * w + x] = 1
	var y := 0
	while y < h:
		var x := 0
		while x < w:
			var edge := x < thick + 1 or y < thick + 1 or x >= w - thick - 1 or y >= h - thick - 1
			if edge and not (_in_gap(gaps, x, y) or _in_gap(gaps, x + 1, y) or _in_gap(gaps, x - 1, y) or _in_gap(gaps, x, y + 1) or _in_gap(gaps, x, y - 1)):
				var o := {"type": kinds[rng.randi() % kinds.size()], "tx": mini(w - 1, x + rng.randi_range(0, 1)), "ty": mini(h - 1, y + rng.randi_range(0, 1) + 1), "v": rng.randi_range(0, 2), "deco": true}
				objs.append(o)
			x += 2
		y += 2

func _in_gap(gaps: Array, x: int, y: int) -> bool:
	for g in gaps:
		if x >= g[0] and y >= g[1] and x <= g[2] and y <= g[3]:
			return true
	return false

func house(tx: int, ty: int, ww: int, v: int, warp := {}, sign_text: Array = []) -> void:
	add_obj("house%d" % ww, tx, ty, v)
	var dx := tx + ww / 2
	unblock(dx, ty)
	if not warp.is_empty():
		warps.append({"tx": dx, "ty": ty, "w": 1, "h": 1, "to": warp.to, "ntx": warp.ntx, "nty": warp.nty, "dir": "up"})
	else:
		signs.append({"tx": dx, "ty": ty, "text": sign_text if not sign_text.is_empty() else ["A porta está trancada."]})
	for i in range(-1, 2):
		if name_at(dx + i, ty + 1) != Terrain.WATER:
			set_t("road", dx + i, ty + 1)
