class_name Furniture
extends Node2D
## Interior furniture drawn procedurally in a front-above (2.5D) view: every piece has a front face and a visible top face.
## Origin = bottom-centre of the footprint, so the node y-sorts with the hero. `act` makes it interactable (E).

const T := 64.0
const OL := Color(0.16, 0.09, 0.07)
const WOOD := Color(0.70, 0.46, 0.27)
const WOOD_LT := Color(0.85, 0.62, 0.40)
const WOOD_DK := Color(0.47, 0.30, 0.19)
const STONE := Color(0.62, 0.62, 0.70)
const STONE_DK := Color(0.42, 0.42, 0.52)
const IRON := Color(0.30, 0.30, 0.38)
const CLOTH_R := Color(0.78, 0.25, 0.22)
const CLOTH_B := Color(0.25, 0.42, 0.75)
const CLOTH_W := Color(0.93, 0.89, 0.80)
const ANIMATED := ["fireplace", "forge", "cauldron", "oven", "torch_stand"]

var kind := "crate"
var w := 1.0              # width in tiles
var act := ""             # "", "board", "rooms", "food"
var deco := ""            # small items on top
var tint := Color.WHITE
var seed_v := 1
var _t := 0.0
var _glow: Sprite2D


## Footprint (tiles) used for the collider: Vector2(width, depth)
static func footprint(k: String, wt: float) -> Vector2:
	match k:
		"counter": return Vector2(wt, 0.9)
		"table": return Vector2(wt, 1.0)
		"round_table": return Vector2(1.2, 0.9)
		"chair": return Vector2(0.5, 0.45)
		"stool": return Vector2(0.45, 0.4)
		"bench": return Vector2(wt, 0.5)
		"barrel": return Vector2(0.75, 0.6)
		"crate": return Vector2(0.85, 0.7)
		"sack": return Vector2(0.7, 0.5)
		"fireplace": return Vector2(wt, 0.8)
		"bed": return Vector2(1.25, 1.7)
		"cot": return Vector2(1.0, 1.6)
		"bookshelf", "potion_shelf": return Vector2(wt, 0.6)
		"desk": return Vector2(wt, 0.9)
		"anvil": return Vector2(0.9, 0.6)
		"forge": return Vector2(wt, 1.0)
		"weapon_rack": return Vector2(wt, 0.4)
		"armor_stand": return Vector2(0.8, 0.5)
		"cauldron": return Vector2(0.95, 0.7)
		"stall": return Vector2(wt, 1.1)
		"oven": return Vector2(wt, 1.0)
		"bread_rack": return Vector2(wt, 0.5)
		"board": return Vector2(wt, 0.35)
		"plant": return Vector2(0.5, 0.4)
		"pillar": return Vector2(0.7, 0.6)
		"hay": return Vector2(1.0, 0.7)
		"trough": return Vector2(wt, 0.5)
		"door_room": return Vector2(1.1, 0.3)
	return Vector2(0.8, 0.6)


func _ready() -> void:
	z_index = 0
	if kind in ANIMATED:
		var col := Color(1.0, 0.62, 0.25) if kind != "cauldron" else Color(0.5, 1.0, 0.55)
		_glow = Util.glow(self, col, 3.4 if kind != "cauldron" else 1.8, 0.0)
		_glow.position = Vector2(0, -34)
		set_process(true)
	else:
		set_process(false)


func _process(dt: float) -> void:
	_t += dt
	if _glow != null:
		_glow.modulate.a = 0.22 + 0.06 * sin(_t * 9.0 + seed_v) + 0.04 * sin(_t * 23.0)
	queue_redraw()


# ------------------------------------------------------------------ drawing helpers
func _poly(pts: Array, col: Color, outline: bool = true) -> void:
	var p := PackedVector2Array(pts)
	draw_colored_polygon(p, col)
	if outline:
		var loop := PackedVector2Array(pts)
		loop.append(pts[0])
		draw_polyline(loop, OL, 2.0)


func _fill(r: Rect2, c: Color) -> void:
	draw_rect(r, c)
	draw_rect(r, OL, false, 2.0)


func _ell(c: Vector2, rx: float, ry: float, col: Color, outline: bool = true) -> void:
	var pts := PackedVector2Array()
	for i in 24:
		var a := TAU * i / 24.0
		pts.append(c + Vector2(cos(a) * rx, sin(a) * ry))
	draw_colored_polygon(pts, col)
	if outline:
		pts.append(pts[0])
		draw_polyline(pts, OL, 2.0)


const HEIGHT := {"bookshelf": 140.0, "potion_shelf": 140.0, "fireplace": 128.0, "forge": 140.0, "pillar": 140.0, "weapon_rack": 120.0,
	"armor_stand": 130.0, "board": 136.0, "door_room": 118.0, "barrel": 46.0, "crate": 42.0, "anvil": 42.0, "plant": 60.0, "counter": 52.0,
	"table": 40.0, "round_table": 36.0, "cauldron": 60.0, "oven": 90.0, "bread_rack": 100.0, "stall": 86.0, "bed": 60.0, "torch_stand": 98.0,
	"desk": 44.0, "chair": 44.0, "stool": 24.0, "bench": 24.0, "sack": 36.0, "hay": 30.0, "cot": 26.0}


func _shadow(wpx: float) -> void:
	_ell(Vector2(0, -3), wpx * 0.5 + 8.0, 9.0, Color(0, 0, 0, 0.26), false)
	# long directional shadow on the floor, away from the light (upper-left)
	var hh: float = HEIGHT.get(kind, 40.0)
	var run := hh * 0.42
	var drop := hh * 0.17
	draw_colored_polygon(PackedVector2Array([Vector2(-wpx * 0.5, -2), Vector2(wpx * 0.5, -2), Vector2(wpx * 0.5 + run, drop), Vector2(-wpx * 0.5 + run, drop)]), Color(0, 0, 0, 0.17))


## Wood grain lines inside a rectangle (only for brown surfaces).
func _grain(r: Rect2, col: Color) -> void:
	if not (col.r > col.b * 1.2 and col.r >= col.g):
		return
	var rnd := RandomNumberGenerator.new()
	rnd.seed = int(r.position.x * 7.0 + r.position.y * 13.0 + r.size.x)
	var y := r.position.y + 5.0
	while y < r.end.y - 3.0:
		var x0 := r.position.x + rnd.randf_range(3, 14)
		var x1 := r.end.x - rnd.randf_range(3, 14)
		draw_line(Vector2(x0, y), Vector2(x1, y + rnd.randf_range(-1.2, 1.2)), Color(0.18, 0.1, 0.06, 0.22), 1.2)
		if rnd.randf() < 0.35:
			draw_line(Vector2(x0 + 6, y + 2.2), Vector2(x1 - 10, y + 2.2), Color(1, 0.9, 0.7, 0.10), 1.0)
		y += rnd.randf_range(6.0, 10.0)


## Box seen from the front and above: front face (w x h) topped by a top face (w x depth * 0.5).
func _box(cx: float, wpx: float, depth: float, h: float, front: Color, top: Color, base_y: float = 0.0) -> void:
	var dd := depth * 0.5
	_fill(Rect2(cx - wpx * 0.5, base_y - h - dd, wpx, dd), top)
	_fill(Rect2(cx - wpx * 0.5, base_y - h, wpx, h), front)
	_grain(Rect2(cx - wpx * 0.5, base_y - h - dd, wpx, dd), top)
	_grain(Rect2(cx - wpx * 0.5, base_y - h, wpx, h), front)
	draw_line(Vector2(cx - wpx * 0.5 + 3, base_y - h + 4), Vector2(cx + wpx * 0.5 - 3, base_y - h + 4), top.lightened(0.2), 2.0)


func _items(wpx: float, top_y: float) -> void:
	# little things on a counter / table
	var rnd := RandomNumberGenerator.new()
	rnd.seed = seed_v * 977
	match deco:
		"mugs":
			for i in int(wpx / 70.0):
				var x := -wpx * 0.5 + 34.0 + i * 70.0 + rnd.randf_range(-6, 6)
				_fill(Rect2(x - 7, top_y - 16, 14, 16), Color(0.85, 0.75, 0.5))
				draw_arc(Vector2(x + 8, top_y - 9), 5.0, -1.4, 1.4, 8, OL, 2.0)
		"bottles":
			for i in int(wpx / 52.0):
				var x := -wpx * 0.5 + 26.0 + i * 52.0
				var c: Color = [Color(0.35, 0.8, 0.45), Color(0.8, 0.35, 0.5), Color(0.4, 0.55, 0.9)][i % 3]
				_ell(Vector2(x, top_y - 10), 8, 10, c)
				_fill(Rect2(x - 3, top_y - 26, 6, 10), c.darkened(0.2))
		"papers":
			_fill(Rect2(-wpx * 0.5 + 24, top_y - 8, 34, 10), CLOTH_W)
			_fill(Rect2(-wpx * 0.5 + 32, top_y - 12, 30, 10), Color(0.96, 0.92, 0.8))
			_ell(Vector2(wpx * 0.5 - 40, top_y - 8), 7, 5, Color(0.2, 0.2, 0.45))
		"bread":
			for i in int(wpx / 60.0):
				_ell(Vector2(-wpx * 0.5 + 30.0 + i * 60.0, top_y - 8), 18, 9, Color(0.82, 0.55, 0.25))
		"plates":
			for i in int(wpx / 80.0):
				_ell(Vector2(-wpx * 0.5 + 40.0 + i * 80.0, top_y - 4), 16, 6, Color(0.93, 0.93, 0.95))
		"gems":
			for i in int(wpx / 64.0):
				var c: Color = [Color(0.9, 0.3, 0.4), Color(0.3, 0.7, 0.95), Color(0.95, 0.85, 0.3)][i % 3]
				_poly([Vector2(-wpx * 0.5 + 30 + i * 64, top_y - 18), Vector2(-wpx * 0.5 + 40 + i * 64, top_y - 8), Vector2(-wpx * 0.5 + 30 + i * 64, top_y), Vector2(-wpx * 0.5 + 20 + i * 64, top_y - 8)], c)
		"map":
			_poly([Vector2(-wpx * 0.5 + 20, top_y - 4), Vector2(wpx * 0.5 - 20, top_y - 4), Vector2(wpx * 0.5 - 30, top_y - 22), Vector2(-wpx * 0.5 + 30, top_y - 22)], Color(0.92, 0.84, 0.62))
			draw_line(Vector2(-wpx * 0.25, top_y - 14), Vector2(wpx * 0.2, top_y - 10), Color(0.7, 0.2, 0.2), 2.0)


func _draw() -> void:
	var wpx := footprint(kind, w).x * T
	var dpx := footprint(kind, w).y * T
	_shadow(wpx)
	var tn := tint
	match kind:
		"counter":
			_box(0, wpx, dpx, 52, WOOD.darkened(0.05) * tn, WOOD_LT * tn)
			for i in int(wpx / 64.0):
				_fill(Rect2(-wpx * 0.5 + 8 + i * 64, -46, 48, 34), WOOD_DK * tn)
				_fill(Rect2(-wpx * 0.5 + 14 + i * 64, -40, 36, 22), WOOD * tn)
			_items(wpx, -52.0 - dpx * 0.25)
		"table", "round_table":
			var is_round := kind == "round_table"
			for x in [-wpx * 0.5 + 10, wpx * 0.5 - 10]:
				_fill(Rect2(x - 5, -30, 10, 30), WOOD_DK * tn)
			if is_round:
				_ell(Vector2(0, -36), wpx * 0.5, dpx * 0.32, WOOD_LT * tn)
				_fill(Rect2(-wpx * 0.5, -36, wpx, 7), WOOD * tn)
			else:
				_fill(Rect2(-wpx * 0.5, -40, wpx, 9), WOOD * tn)
				_fill(Rect2(-wpx * 0.5, -40 - dpx * 0.5, wpx, dpx * 0.5), WOOD_LT * tn)
				_grain(Rect2(-wpx * 0.5, -40 - dpx * 0.5, wpx, dpx * 0.5), WOOD_LT)
			_items(wpx, -40.0 - dpx * 0.18)
		"chair":
			_fill(Rect2(-14, -44, 28, 24), WOOD_DK * tn)
			_fill(Rect2(-16, -22, 32, 10), WOOD * tn)
			for x in [-12, 12]:
				_fill(Rect2(x - 3, -14, 6, 14), WOOD_DK * tn)
		"stool":
			_ell(Vector2(0, -22), 15, 7, WOOD_LT * tn)
			_fill(Rect2(-15, -22, 30, 6), WOOD * tn)
			for x in [-9, 9]:
				_fill(Rect2(x - 3, -16, 6, 16), WOOD_DK * tn)
		"bench":
			_fill(Rect2(-wpx * 0.5, -24, wpx, 9), WOOD_LT * tn)
			_grain(Rect2(-wpx * 0.5, -24, wpx, 9), WOOD_LT)
			_fill(Rect2(-wpx * 0.5 + 6, -15, 8, 15), WOOD_DK * tn)
			_fill(Rect2(wpx * 0.5 - 14, -15, 8, 15), WOOD_DK * tn)
		"barrel":
			_fill(Rect2(-24, -46, 48, 46), WOOD * tn)
			_ell(Vector2(0, -46), 24, 9, WOOD_LT * tn)
			for y in [-34, -14]:
				draw_line(Vector2(-24, y), Vector2(24, y), IRON, 4.0)
			_ell(Vector2(0, 0), 24, 7, WOOD_DK * tn, false)
		"crate":
			_box(0, wpx * 0.9, dpx, 42, WOOD * tn, WOOD_LT * tn)
			draw_line(Vector2(-wpx * 0.45, -40), Vector2(wpx * 0.45, -4), WOOD_DK, 3.0)
		"sack":
			_ell(Vector2(0, -18), 24, 20, Color(0.82, 0.72, 0.5) * tn)
			draw_line(Vector2(-8, -36), Vector2(8, -36), OL, 3.0)
		"hay":
			_ell(Vector2(0, -16), 34, 18, Color(0.9, 0.78, 0.35))
			for i in 8:
				draw_line(Vector2(-26 + i * 7, -10), Vector2(-20 + i * 7, -30), Color(0.75, 0.6, 0.2), 2.0)
		"trough":
			_box(0, wpx, dpx, 26, WOOD_DK * tn, Color(0.35, 0.55, 0.8))
		"fireplace":
			_box(0, wpx, dpx, 118, STONE * tn, STONE_DK * tn)
			_fill(Rect2(-wpx * 0.5 + 22, -92, wpx - 44, 82), Color(0.1, 0.06, 0.05))
			_fill(Rect2(-wpx * 0.5 - 4, -128, wpx + 8, 12), WOOD_DK * tn)
			var f := 0.0
			for i in 5:
				f = sin(_t * 8.0 + i * 1.7)
				var x := -wpx * 0.5 + 40 + i * (wpx - 80) / 4.0
				_poly([Vector2(x - 12, -10), Vector2(x + f * 4, -48 - 12 * f - (i % 2) * 14), Vector2(x + 12, -10)], Color(1.0, 0.55 + 0.1 * f, 0.15), false)
				_poly([Vector2(x - 6, -10), Vector2(x + f * 2, -30 - 6 * f), Vector2(x + 6, -10)], Color(1.0, 0.9, 0.4), false)
			_fill(Rect2(-wpx * 0.5 + 30, -14, wpx - 60, 8), WOOD_DK)
		"bed":
			_fill(Rect2(-wpx * 0.5, -48, wpx, 48), WOOD_DK * tn)
			_fill(Rect2(-wpx * 0.5, -48 - dpx * 0.5, wpx, dpx * 0.5), (tint if tint != Color.WHITE else CLOTH_R))
			_fill(Rect2(-wpx * 0.5, -48 - dpx * 0.5, wpx, 16), Color(0.95, 0.93, 0.88))
			_ell(Vector2(-wpx * 0.2, -48 - dpx * 0.4), 18, 8, Color(0.98, 0.97, 0.94))
			_ell(Vector2(wpx * 0.2, -48 - dpx * 0.4), 18, 8, Color(0.98, 0.97, 0.94))
			draw_line(Vector2(-wpx * 0.5, -60), Vector2(wpx * 0.5, -60), Color(1, 1, 1, 0.25), 3.0)
			_fill(Rect2(-wpx * 0.5 - 4, -48 - dpx * 0.5 - 22, 10, 46 + 22), WOOD * tn)
			_fill(Rect2(wpx * 0.5 - 6, -48 - dpx * 0.5 - 22, 10, 46 + 22), WOOD * tn)
		"cot":
			_fill(Rect2(-wpx * 0.5, -26, wpx, 26), IRON)
			_fill(Rect2(-wpx * 0.5, -26 - dpx * 0.45, wpx, dpx * 0.45), Color(0.45, 0.5, 0.62))
			_ell(Vector2(0, -26 - dpx * 0.38), 16, 7, CLOTH_W)
		"bookshelf":
			var rnd := RandomNumberGenerator.new()
			rnd.seed = seed_v * 31
			_box(0, wpx, dpx, 140, WOOD_DK * tn, WOOD * tn)
			for r in 3:
				var y := -118.0 + r * 40.0
				_fill(Rect2(-wpx * 0.5 + 6, y, wpx - 12, 34), Color(0.16, 0.1, 0.08))
				var x := -wpx * 0.5 + 10.0
				while x < wpx * 0.5 - 16.0:
					var bw := rnd.randf_range(7.0, 13.0)
					var bh := rnd.randf_range(22.0, 32.0)
					var c := Color.from_hsv(rnd.randf(), 0.55, 0.78)
					draw_rect(Rect2(x, y + 34 - bh, bw, bh), c)
					draw_rect(Rect2(x, y + 34 - bh, bw, bh), OL, false, 1.0)
					x += bw + 1.5
		"potion_shelf":
			var rnd2 := RandomNumberGenerator.new()
			rnd2.seed = seed_v * 17
			_box(0, wpx, dpx, 140, Color(0.25, 0.42, 0.36) * tn, Color(0.35, 0.55, 0.47) * tn)
			for r in 3:
				var y2 := -118.0 + r * 40.0
				_fill(Rect2(-wpx * 0.5 + 6, y2, wpx - 12, 34), Color(0.1, 0.16, 0.14))
				var x2 := -wpx * 0.5 + 16.0
				while x2 < wpx * 0.5 - 12.0:
					var c2 := Color.from_hsv(rnd2.randf(), 0.6, 0.9)
					_ell(Vector2(x2, y2 + 24), 8, 9, c2)
					_fill(Rect2(x2 - 3, y2 + 8, 6, 8), c2.darkened(0.25))
					x2 += 22.0
		"desk":
			_box(0, wpx, dpx, 44, WOOD * tn, WOOD_LT * tn)
			_fill(Rect2(wpx * 0.5 - 40, -40, 32, 32), WOOD_DK * tn)
			_items(wpx, -44.0 - dpx * 0.25)
		"anvil":
			_poly([Vector2(-26, -34), Vector2(26, -34), Vector2(40, -42), Vector2(-40, -42)], Color(0.45, 0.45, 0.55))
			_fill(Rect2(-20, -34, 40, 14), IRON)
			_fill(Rect2(-26, -20, 52, 20), Color(0.24, 0.24, 0.3))
			_fill(Rect2(-34, 0, 68, 4), WOOD_DK)
		"forge":
			_box(0, wpx, dpx, 96, Color(0.4, 0.28, 0.25) * tn, STONE_DK * tn)
			_fill(Rect2(-wpx * 0.5 + 24, -78, wpx - 48, 50), Color(0.12, 0.05, 0.04))
			for i in 6:
				var x3 := -wpx * 0.5 + 38 + i * (wpx - 76) / 5.0
				var f3 := sin(_t * 7.0 + i * 2.3)
				_poly([Vector2(x3 - 10, -30), Vector2(x3 + f3 * 3, -52 - 8 * f3), Vector2(x3 + 10, -30)], Color(1.0, 0.45 + 0.15 * f3, 0.1), false)
			_fill(Rect2(wpx * 0.5 - 30, -140, 22, 50), STONE * tn)
		"weapon_rack":
			_fill(Rect2(-wpx * 0.5, -22, wpx, 8), WOOD_DK * tn)
			_fill(Rect2(-wpx * 0.5 + 6, -120, 8, 100), WOOD_DK * tn)
			_fill(Rect2(wpx * 0.5 - 14, -120, 8, 100), WOOD_DK * tn)
			_fill(Rect2(-wpx * 0.5, -110, wpx, 8), WOOD * tn)
			for i in int(wpx / 26.0):
				var x4 := -wpx * 0.5 + 22.0 + i * 26.0
				draw_line(Vector2(x4, -26), Vector2(x4 + 4, -104), Color(0.8, 0.82, 0.9), 5.0)
				draw_line(Vector2(x4 - 8, -50), Vector2(x4 + 10, -50), Color(0.8, 0.6, 0.2), 4.0)
		"armor_stand":
			_fill(Rect2(-4, -40, 8, 40), WOOD_DK)
			_fill(Rect2(-22, -4, 44, 6), WOOD_DK)
			_poly([Vector2(-24, -110), Vector2(24, -110), Vector2(18, -62), Vector2(-18, -62)], Color(0.62, 0.66, 0.78))
			_poly([Vector2(-14, -110), Vector2(14, -110), Vector2(10, -88), Vector2(-10, -88)], Color(0.78, 0.8, 0.9))
			_ell(Vector2(0, -126), 13, 14, Color(0.7, 0.72, 0.82))
			draw_rect(Rect2(-9, -130, 18, 5), Color(0.1, 0.1, 0.14))
		"cauldron":
			_ell(Vector2(0, -26), 38, 28, IRON)
			_ell(Vector2(0, -42), 32, 12, Color(0.3, 0.75, 0.4))
			for i in 4:
				_ell(Vector2(-14 + i * 10, -46 - abs(sin(_t * 3 + i * 1.9)) * 8), 4, 4, Color(0.7, 1.0, 0.7, 0.8), false)
			for x5 in [-30, 30]:
				_fill(Rect2(x5 - 4, -6, 8, 8), WOOD_DK)
		"stall":
			_fill(Rect2(-wpx * 0.5, -86, 10, 86), WOOD_DK * tn)
			_fill(Rect2(wpx * 0.5 - 10, -86, 10, 86), WOOD_DK * tn)
			for y6 in [-70, -44]:
				_fill(Rect2(-wpx * 0.5, y6, wpx, 10), WOOD * tn)
			_ell(Vector2(0, -12), wpx * 0.36, 16, Color(0.9, 0.78, 0.35), false)
		"oven":
			_box(0, wpx, dpx, 90, Color(0.65, 0.35, 0.28) * tn, Color(0.5, 0.28, 0.22) * tn)
			_ell(Vector2(0, -52), 38, 32, Color(0.15, 0.06, 0.05))
			for i in 4:
				var f7 := sin(_t * 8.0 + i * 2.0)
				_poly([Vector2(-20 + i * 13, -30), Vector2(-16 + i * 13 + f7 * 2, -52 - 7 * f7), Vector2(-8 + i * 13, -30)], Color(1.0, 0.6, 0.15), false)
		"bread_rack":
			_box(0, wpx, dpx, 100, WOOD * tn, WOOD_LT * tn)
			for r in 3:
				for i in int(wpx / 40.0):
					_ell(Vector2(-wpx * 0.5 + 24 + i * 40, -88 + r * 28), 15, 8, Color(0.84, 0.58, 0.28))
		"board":
			_fill(Rect2(-wpx * 0.5, -136, wpx, 96), WOOD_DK * tn)
			_fill(Rect2(-wpx * 0.5 + 8, -128, wpx - 16, 80), Color(0.82, 0.66, 0.42))
			var rnd3 := RandomNumberGenerator.new()
			rnd3.seed = seed_v
			for i in 7:
				var px := -wpx * 0.5 + 16.0 + (i % 4) * (wpx - 40) / 4.0 + rnd3.randf_range(-3, 3)
				var py := -122.0 + int(i / 4) * 40.0 + rnd3.randf_range(-3, 3)
				_fill(Rect2(px, py, 26, 32), Color(0.96, 0.92, 0.8))
				draw_circle(Vector2(px + 13, py + 3), 3.0, Color(0.8, 0.2, 0.2))
			_fill(Rect2(-wpx * 0.5 + 4, -40, 8, 40), WOOD_DK * tn)
			_fill(Rect2(wpx * 0.5 - 12, -40, 8, 40), WOOD_DK * tn)
			if act != "":
				var bob := sin(_t * 3.0 if is_inside_tree() else 0.0)
				draw_circle(Vector2(0, -156 + bob * 3), 4.0, Color(1, 0.85, 0.3))
		"plant":
			_fill(Rect2(-14, -22, 28, 22), Color(0.72, 0.4, 0.28))
			for i in 5:
				var a := -1.1 + i * 0.55
				_ell(Vector2(sin(a) * 18, -38 - cos(a) * 20), 11, 16, Color(0.3, 0.65, 0.3))
		"pillar":
			_box(0, wpx * 0.8, dpx, 140, STONE * tn, STONE_DK * tn)
		"torch_stand":
			_fill(Rect2(-4, -70, 8, 70), IRON)
			var f8 := sin(_t * 9.0 + seed_v)
			_poly([Vector2(-10, -70), Vector2(f8 * 3, -98 - 6 * f8), Vector2(10, -70)], Color(1.0, 0.6, 0.15), false)
		"door_room":
			_fill(Rect2(-wpx * 0.5, -118, wpx, 118), WOOD_DK * tn)
			_fill(Rect2(-wpx * 0.5 + 8, -108, wpx - 16, 98), WOOD * tn)
			_grain(Rect2(-wpx * 0.5 + 8, -108, wpx - 16, 98), WOOD)
			draw_circle(Vector2(wpx * 0.25, -56), 4.0, Color(0.95, 0.8, 0.3))
			_fill(Rect2(-14, -150, 28, 26), Color(0.9, 0.8, 0.55))
			draw_circle(Vector2(0, -137), 4.0, OL)
		_:
			_box(0, wpx, dpx, 40, WOOD * tn, WOOD_LT * tn)
