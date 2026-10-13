class_name InteriorView
extends Node2D
## Floor, walls and wall decor of an interior room, drawn procedurally (front-above 2.5D view).
## The back wall occupies the top WALL_ROWS tiles; side walls are one tile wide; the bottom row is the doorway threshold.

const T := 64.0
const WALL_ROWS := 3
const OL := Color(0.16, 0.09, 0.07)

var data: Dictionary
var style := "tavern"
var tex_floor: Texture2D
var tex_wall: Texture2D
var tex_wain: Texture2D

# style -> [floor A, floor B, wall, wainscot, trim, floor kind]
const STYLES := {
	"tavern": [Color(0.66, 0.45, 0.28), Color(0.60, 0.40, 0.25), Color(0.93, 0.84, 0.62), Color(0.55, 0.36, 0.22), Color(0.42, 0.26, 0.16), "wood"],
	"guild": [Color(0.50, 0.52, 0.60), Color(0.45, 0.47, 0.56), Color(0.62, 0.62, 0.72), Color(0.38, 0.30, 0.42), Color(0.30, 0.24, 0.34), "stone"],
	"smithy": [Color(0.34, 0.32, 0.38), Color(0.30, 0.28, 0.34), Color(0.45, 0.36, 0.34), Color(0.30, 0.24, 0.24), Color(0.20, 0.16, 0.16), "stone"],
	"shop": [Color(0.64, 0.46, 0.30), Color(0.58, 0.41, 0.27), Color(0.62, 0.82, 0.70), Color(0.34, 0.52, 0.45), Color(0.24, 0.40, 0.34), "wood"],
	"armory": [Color(0.44, 0.45, 0.54), Color(0.40, 0.41, 0.50), Color(0.55, 0.57, 0.68), Color(0.34, 0.35, 0.46), Color(0.24, 0.25, 0.34), "stone"],
	"stable": [Color(0.62, 0.50, 0.30), Color(0.56, 0.45, 0.27), Color(0.66, 0.50, 0.34), Color(0.48, 0.34, 0.22), Color(0.36, 0.25, 0.16), "dirt"],
	"library": [Color(0.46, 0.30, 0.22), Color(0.42, 0.27, 0.20), Color(0.46, 0.34, 0.30), Color(0.32, 0.22, 0.20), Color(0.22, 0.15, 0.14), "wood"],
	"barracks": [Color(0.46, 0.46, 0.52), Color(0.42, 0.42, 0.48), Color(0.58, 0.55, 0.58), Color(0.38, 0.32, 0.34), Color(0.26, 0.22, 0.24), "stone"],
	"bakery": [Color(0.88, 0.76, 0.58), Color(0.80, 0.66, 0.48), Color(0.96, 0.84, 0.72), Color(0.70, 0.50, 0.38), Color(0.52, 0.36, 0.28), "check"],
}


func setup(d: Dictionary) -> void:
	data = d
	style = str(d.get("style", "tavern"))
	z_index = -100
	var fk: String = (STYLES.get(style, STYLES["tavern"]) as Array)[5]
	tex_floor = Sheets.tex("Sprites/Tex/" + {"wood": "floor_wood", "stone": "floor_stone", "check": "floor_stone", "dirt": "floor_dirt"}.get(fk, "floor_wood"))
	var brick := style in ["guild", "smithy", "armory", "barracks"]
	var wooden := style in ["stable", "library"]
	tex_wall = Sheets.tex("Sprites/Tex/" + ("wall_brick" if brick else ("wall_wood" if wooden else "wall_plaster")))
	tex_wain = Sheets.tex("Sprites/Tex/" + ("wall_brick" if brick else "wall_wood"))


func _tint(c: Color, k: float = 1.3) -> Color:
	return Color(c.r * k, c.g * k, c.b * k, 1.0)


func _ready() -> void:
	# warm glows for torches / windows
	for dc in data.get("decor", []):
		var k := str(dc["k"])
		if k == "torch":
			var g := Util.glow(self, Color(1.0, 0.65, 0.3), 3.2, 0.3)
			g.position = Vector2(float(dc["x"]), float(dc["y"]))
		elif k == "window":
			var g2 := Util.glow(self, Color(1.0, 0.95, 0.7), 3.6, 0.14)
			g2.position = Vector2(float(dc["x"]), float(dc["y"]) + 150.0)


func _draw() -> void:
	var st: Array = STYLES.get(style, STYLES["tavern"])
	var fa: Color = st[0]
	var fb: Color = st[1]
	var wall: Color = st[2]
	var wains: Color = st[3]
	var trim: Color = st[4]
	var fk: String = st[5]
	var w := int(data["w"])
	var h := int(data["h"])
	var W := w * T
	var H := h * T
	draw_rect(Rect2(-200, -200, W + 400, H + 400), Color(0.05, 0.03, 0.03))
	# ---------------------------------------------------------- floor (tiled surface texture, tinted per room)
	var rnd := RandomNumberGenerator.new()
	rnd.seed = hash(str(data["name"]))
	var fr := Rect2(T, WALL_ROWS * T, W - 2 * T, H - WALL_ROWS * T)
	if tex_floor != null:
		draw_texture_rect(tex_floor, fr, true, _tint(fa))
	else:
		draw_rect(fr, fa)
	for j in range(WALL_ROWS, h):
		for i in range(1, w - 1):
			var x := i * T
			var y := j * T
			match fk:
				"wood":
					if (j + i) % 3 == 0:
						draw_rect(Rect2(x, y, T, T), Color(0, 0, 0, 0.05))
				"stone", "check":
					if (i + j) % 2 == 0:
						draw_rect(Rect2(x, y, T, T), Color(0, 0, 0, 0.12 if fk == "check" else 0.07))
				_:
					for k in 3:
						var sx := x + rnd.randf_range(4, 56)
						var sy := y + rnd.randf_range(4, 56)
						draw_line(Vector2(sx, sy), Vector2(sx + rnd.randf_range(6, 14), sy + rnd.randf_range(-3, 3)), Color(0.85, 0.72, 0.35, 0.8), 2.0)
	# rugs and floor decor
	for dc in data.get("decor", []):
		_floor_decor(dc)
	# ---------------------------------------------------------- back wall
	var wh := WALL_ROWS * T
	if tex_wall != null:
		draw_texture_rect(tex_wall, Rect2(0, 0, W, wh), true, _tint(wall))
	else:
		draw_rect(Rect2(0, 0, W, wh), wall)
	if tex_wain != null:
		draw_texture_rect(tex_wain, Rect2(0, wh - 78, W, 78), true, _tint(wains, 1.25))
	else:
		draw_rect(Rect2(0, wh - 78, W, 78), wains)
	if fk != "stone" and style != "smithy":
		for i in range(0, w, 4):
			draw_rect(Rect2(i * T - 6, 0, 12, wh), trim)
			draw_rect(Rect2(i * T - 6, 0, 3, wh), trim.lightened(0.18))
		draw_line(Vector2(0, 72), Vector2(W, 72), wall.darkened(0.12), 2.0)
	# light falling from the window side: soft vertical gradient on the wall
	for gi in 6:
		draw_rect(Rect2(0, gi * 32.0, W, 32.0), Color(1, 0.97, 0.85, 0.08 - gi * 0.012))
	draw_rect(Rect2(0, wh - 82, W, 8), trim)
	draw_rect(Rect2(0, 0, W, 14), trim)
	draw_rect(Rect2(0, wh - 8, W, 8), trim.darkened(0.25))
	draw_rect(Rect2(0, wh, W, 3), OL)
	# soft shadow under the wall
	for s in 6:
		draw_rect(Rect2(T, wh + s * 5.0, W - 2 * T, 5.0), Color(0, 0, 0, 0.20 - s * 0.03))
	for dc in data.get("decor", []):
		_wall_decor(dc, wall, trim)
	# ---------------------------------------------------------- side walls
	for side in 2:
		var x0 := 0.0 if side == 0 else W - T
		draw_rect(Rect2(x0, 0, T, H), wains.darkened(0.15))
		var inner := T - 8.0 if side == 0 else 0.0
		draw_rect(Rect2(x0 + (T - 10.0 if side == 0 else 0.0), WALL_ROWS * T - 6.0, 10.0, H), OL)
		for s2 in 5:
			var a := 0.22 - s2 * 0.04
			var sx2 := (T + s2 * 6.0) if side == 0 else (W - T - (s2 + 1) * 6.0)
			draw_rect(Rect2(sx2, wh, 6.0, H - wh), Color(0, 0, 0, a))
		draw_rect(Rect2(x0, 0, T, 14), trim)
	# ---------------------------------------------------------- threshold row + doorway
	var by := (h - 1) * T
	draw_rect(Rect2(T, by, W - 2 * T, T), fa.darkened(0.30))
	draw_rect(Rect2(0, by, T, T), wains.darkened(0.3))
	draw_rect(Rect2(W - T, by, T, T), wains.darkened(0.3))
	var dx0 := W * 0.5 - T
	for blk in 2:
		var bx := T if blk == 0 else dx0 + 2 * T
		var bw := (dx0 - T) if blk == 0 else (W - T - (dx0 + 2 * T))
		draw_rect(Rect2(bx, by, bw, T), wains.darkened(0.35))
		draw_rect(Rect2(bx, by, bw, 8), trim)
		draw_rect(Rect2(bx, by, bw, T), OL, false, 2.0)
	# door opening: warm daylight spilling in
	draw_rect(Rect2(dx0, by, 2 * T, T), Color(1.0, 0.96, 0.78))
	for s3 in 8:
		draw_rect(Rect2(dx0 - s3 * 4.0, by - (s3 + 1) * 6.0, 2 * T + s3 * 8.0, 6.0), Color(1.0, 0.95, 0.75, 0.12 - s3 * 0.012))
	draw_rect(Rect2(dx0 - 8, by, 8, T), trim)
	draw_rect(Rect2(dx0 + 2 * T, by, 8, T), trim)
	draw_rect(Rect2(dx0 + 14, by - 4, 2 * T - 28, 22), Color(0.58, 0.28, 0.22))
	draw_rect(Rect2(dx0 + 14, by - 4, 2 * T - 28, 22), OL, false, 2.0)


func _floor_decor(dc: Dictionary) -> void:
	var k := str(dc["k"])
	var x := float(dc["x"])
	var y := float(dc["y"])
	var rw := float(dc.get("w", 3)) * T
	var rh := float(dc.get("d", 2)) * T
	var col := Color(str(dc.get("c", "#a8332f")))
	match k:
		"rug":
			draw_rect(Rect2(x - rw * 0.5, y - rh * 0.5, rw, rh), col)
			draw_rect(Rect2(x - rw * 0.5 + 8, y - rh * 0.5 + 8, rw - 16, rh - 16), col.lightened(0.18), false, 4.0)
			draw_rect(Rect2(x - rw * 0.5 + 18, y - rh * 0.5 + 18, rw - 36, rh - 36), col.darkened(0.2), false, 2.0)
			draw_rect(Rect2(x - rw * 0.5, y - rh * 0.5, rw, rh), col.darkened(0.45), false, 2.0)
			for i in int(rw / 40.0):
				var cx := x - rw * 0.5 + 24.0 + i * 40.0
				draw_circle(Vector2(cx, y), 7.0, col.lightened(0.3))
		"round_rug":
			var pts := PackedVector2Array()
			for i in 28:
				var a := TAU * i / 28.0
				pts.append(Vector2(x + cos(a) * rw * 0.5, y + sin(a) * rh * 0.5))
			draw_colored_polygon(pts, col)
			pts.append(pts[0])
			draw_polyline(pts, col.darkened(0.4), 2.0)
		"runner":
			draw_rect(Rect2(x - rw * 0.5, y - rh * 0.5, rw, rh), col)
			draw_rect(Rect2(x - rw * 0.5, y - rh * 0.5, rw, 6), Color(0.95, 0.8, 0.35))
			draw_rect(Rect2(x - rw * 0.5, y + rh * 0.5 - 6, rw, 6), Color(0.95, 0.8, 0.35))


func _wall_decor(dc: Dictionary, wall: Color, trim: Color) -> void:
	var k := str(dc["k"])
	var x := float(dc["x"])
	var y := float(dc["y"])
	match k:
		"window":
			draw_rect(Rect2(x - 38, y - 4, 76, 92), trim)
			draw_rect(Rect2(x - 32, y + 2, 64, 80), Color(0.66, 0.84, 0.95))
			draw_rect(Rect2(x - 32, y + 2, 64, 36), Color(0.82, 0.93, 1.0))
			draw_line(Vector2(x, y + 2), Vector2(x, y + 82), trim, 4.0)
			draw_line(Vector2(x - 32, y + 42), Vector2(x + 32, y + 42), trim, 4.0)
			draw_rect(Rect2(x - 38, y - 4, 76, 92), OL, false, 2.0)
			draw_rect(Rect2(x - 44, y + 86, 88, 8), trim.lightened(0.15))
			# sunbeam on the floor
			draw_colored_polygon(PackedVector2Array([Vector2(x - 28, 200), Vector2(x + 28, 200), Vector2(x + 78, 330), Vector2(x - 6, 330)]), Color(1, 0.96, 0.7, 0.10))
		"banner":
			var c := Color(str(dc.get("c", "#a8332f")))
			draw_rect(Rect2(x - 3, y - 8, 56, 8), trim)
			draw_colored_polygon(PackedVector2Array([Vector2(x, y), Vector2(x + 50, y), Vector2(x + 50, y + 96), Vector2(x + 25, y + 78), Vector2(x, y + 96)]), c)
			draw_polyline(PackedVector2Array([Vector2(x, y), Vector2(x + 50, y), Vector2(x + 50, y + 96), Vector2(x + 25, y + 78), Vector2(x, y + 96), Vector2(x, y)]), OL, 2.0)
			draw_circle(Vector2(x + 25, y + 34), 12.0, Color(0.96, 0.82, 0.35))
		"torch":
			draw_rect(Rect2(x - 4, y + 4, 8, 34), Color(0.3, 0.28, 0.33))
			draw_colored_polygon(PackedVector2Array([Vector2(x - 8, y + 6), Vector2(x, y - 24), Vector2(x + 8, y + 6)]), Color(1.0, 0.6, 0.15))
			draw_colored_polygon(PackedVector2Array([Vector2(x - 4, y + 6), Vector2(x, y - 10), Vector2(x + 4, y + 6)]), Color(1.0, 0.9, 0.45))
		"shelf_wall":
			var n := int(dc.get("w", 3))
			draw_rect(Rect2(x - n * 32.0, y, n * 64.0, 8), trim)
			var rnd := RandomNumberGenerator.new()
			rnd.seed = int(x) * 7 + int(y)
			var itm := str(dc.get("items", "plates"))
			for i in n * 2:
				var ix := x - n * 32.0 + 16.0 + i * 32.0
				match itm:
					"bottles":
						var cc := Color.from_hsv(rnd.randf(), 0.55, 0.9)
						draw_circle(Vector2(ix, y - 10), 9.0, cc)
						draw_rect(Rect2(ix - 3, y - 28, 6, 12), cc.darkened(0.2))
					"books":
						var cb := Color.from_hsv(rnd.randf(), 0.5, 0.75)
						draw_rect(Rect2(ix - 7, y - 30, 14, 30), cb)
						draw_rect(Rect2(ix - 7, y - 30, 14, 30), OL, false, 1.5)
					_:
						draw_circle(Vector2(ix, y - 12), 12.0, Color(0.93, 0.93, 0.96))
						draw_circle(Vector2(ix, y - 12), 12.0, OL, 1.5)
		"swords":
			draw_line(Vector2(x - 26, y + 10), Vector2(x + 26, y + 70), Color(0.82, 0.84, 0.92), 6.0)
			draw_line(Vector2(x + 26, y + 10), Vector2(x - 26, y + 70), Color(0.82, 0.84, 0.92), 6.0)
			draw_colored_polygon(PackedVector2Array([Vector2(x - 16, y + 18), Vector2(x + 16, y + 18), Vector2(x + 16, y + 56), Vector2(x, y + 70), Vector2(x - 16, y + 56)]), Color(0.7, 0.22, 0.2))
			draw_circle(Vector2(x, y + 40), 7.0, Color(0.96, 0.82, 0.35))
		"clock":
			draw_circle(Vector2(x, y + 30), 24.0, Color(0.95, 0.9, 0.78))
			draw_arc(Vector2(x, y + 30), 24.0, 0, TAU, 24, OL, 3.0)
			draw_line(Vector2(x, y + 30), Vector2(x, y + 14), OL, 3.0)
			draw_line(Vector2(x, y + 30), Vector2(x + 12, y + 34), OL, 3.0)
		"painting":
			draw_rect(Rect2(x - 34, y, 68, 54), Color(0.55, 0.38, 0.2))
			draw_rect(Rect2(x - 28, y + 6, 56, 42), Color(0.45, 0.7, 0.85))
			draw_colored_polygon(PackedVector2Array([Vector2(x - 28, y + 48), Vector2(x - 8, y + 24), Vector2(x + 10, y + 40), Vector2(x + 28, y + 20), Vector2(x + 28, y + 48)]), Color(0.35, 0.6, 0.35))
		"sign":
			draw_rect(Rect2(x - 56, y, 112, 34), Color(0.55, 0.36, 0.2))
			draw_rect(Rect2(x - 56, y, 112, 34), OL, false, 2.0)
			draw_string(ThemeDB.fallback_font, Vector2(x - 50, y + 24), str(dc.get("t", "")), HORIZONTAL_ALIGNMENT_CENTER, 100, 18, Color(1, 0.92, 0.7))
