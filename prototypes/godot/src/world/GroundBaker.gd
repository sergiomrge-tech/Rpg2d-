class_name GroundBaker
extends RefCounted
## Bakes the static ground layer of a MapData into one ImageTexture (+ water mask).

const T := 32

static func bake(m: MapData) -> Dictionary:
	Terrain.setup()
	var img := Image.create(m.w * T, m.h * T, false, Image.FORMAT_RGBA8)
	var wmask := Image.create(m.w, m.h, false, Image.FORMAT_R8)
	var rnd := RandomNumberGenerator.new()
	rnd.seed = hash(m.id)
	# pass 1: base tiles
	for y in m.h:
		for x in m.w:
			var n := m.name_at(x, y)
			var v := m.variant[y * m.w + x]
			var pos := Vector2i(x * T, y * T)
			if Terrain.is_water(n):
				wmask.set_pixel(x, y, Color(1.0 if n == Terrain.DEEP else 0.5, 0, 0))
				continue
			if n == Terrain.LAVA:
				wmask.set_pixel(x, y, Color(0.0, 0, 0))
				continue
			if n == Terrain.VOID:
				img.fill_rect(Rect2i(pos, Vector2i(T, T)), Color(0.02, 0.01, 0.04))
				continue
			if Terrain.WALL_KINDS.has(n):
				var wk: Dictionary = Terrain.WALL_KINDS[n]
				var below := m.name_at(x, y + 1)
				if not Terrain.is_wall(below):
					img.blit_rect(Terrain.atlas, Terrain.wall_rect(wk["face"], v), pos)
				else:
					img.blit_rect(Terrain.atlas, Terrain.tile_rect(wk["top"], v), pos)
				continue
			img.blit_rect(Terrain.atlas, Terrain.tile_rect(n, v), pos)
	# pass 2: edge overlays (higher rank spills over lower rank neighbours)
	var dirs := {
		"N": Vector2i(0, -1), "E": Vector2i(1, 0), "S": Vector2i(0, 1), "W": Vector2i(-1, 0),
		"NE": Vector2i(1, -1), "SE": Vector2i(1, 1), "SW": Vector2i(-1, 1), "NW": Vector2i(-1, -1),
	}
	var no_edge: Array = Terrain.meta["no_edge"]
	for y in m.h:
		for x in m.w:
			var n := m.name_at(x, y)
			if Terrain.is_wall(n):
				continue
			var r_self: int = Terrain.rank[n]
			var over: Array = []  # [rank, name, dir]
			for d in dirs:
				var o: Vector2i = dirs[d]
				var nn := m.name_at(x + o.x, y + o.y)
				if Terrain.is_wall(nn) or Terrain.is_water(nn) or nn == Terrain.LAVA or nn == n or nn in no_edge:
					continue
				var rn: int = Terrain.rank[nn]
				if rn <= r_self:
					continue
				if d.length() == 2:
					# corner: skip if either orthogonal neighbour is the same higher terrain (edge pieces cover it)
					if m.name_at(x + o.x, y) == nn or m.name_at(x, y + o.y) == nn:
						continue
				over.append([rn, nn, d])
			over.sort_custom(func(a, b): return a[0] < b[0])
			for o in over:
				img.blend_rect(Terrain.edges, Terrain.edge_rect(o[1], o[2]), Vector2i(x * T, y * T))
	# pass 3: ambient occlusion below walls
	var shade := Image.create(T, 12, false, Image.FORMAT_RGBA8)
	for j in 12:
		shade.fill_rect(Rect2i(0, j, T, 1), Color(0.03, 0.01, 0.1, 0.42 * (1.0 - j / 12.0)))
	for y in m.h:
		for x in m.w:
			var n := m.name_at(x, y)
			if Terrain.is_wall(n) or Terrain.is_water(n):
				continue
			if Terrain.is_wall(m.name_at(x, y - 1)) and not Terrain.is_wall(m.name_at(x, y)):
				img.blend_rect(shade, Rect2i(0, 0, T, 12), Vector2i(x * T, y * T))
	_decals(m, img, rnd)
	return {"ground": ImageTexture.create_from_image(img), "water_mask": ImageTexture.create_from_image(wmask)}

static var _decal_img: Image
static var _decal_meta: Dictionary
const DECAL_TABLE := {
	"grass": {"p": 0.5, "d": ["tuft_a", "tuft_b", "tuft_c", "tuft_a", "flower_w", "flower_y", "pebbles", "leaf_g"]},
	"meadow": {"p": 0.7, "d": ["tuft_a", "flower_w", "flower_p", "flower_y", "flower_b", "flower_p", "tuft_b"]},
	"grass_dark": {"p": 0.55, "d": ["tuft_dark", "tuft_c", "mushroom_r", "leaf_o", "leaf_g", "tuft_dark"]},
	"moss": {"p": 0.5, "d": ["tuft_dark", "mushroom_b", "mushroom_r", "leaf_g"]},
	"dirt": {"p": 0.4, "d": ["pebbles", "pebbles_b", "crack"]},
	"road": {"p": 0.35, "d": ["pebbles", "pebbles_b", "pebbles"]},
	"sand": {"p": 0.3, "d": ["shell", "pebbles_b"]},
	"dsand": {"p": 0.25, "d": ["pebbles_b", "crack", "bones"]},
	"cobble": {"p": 0.25, "d": ["crack", "pebbles", "leaf_o"]},
	"cobble_warm": {"p": 0.25, "d": ["crack", "pebbles", "leaf_o"]},
	"snow": {"p": 0.4, "d": ["snowdrift", "pebbles_dark"]},
	"cave": {"p": 0.45, "d": ["pebbles_dark", "crack_dark", "pebbles_dark", "bones", "glowshroom"]},
	"cave_dark": {"p": 0.45, "d": ["pebbles_dark", "crack_dark", "glowshroom"]},
	"slab": {"p": 0.2, "d": ["crack_dark"]},
	"slab_dark": {"p": 0.2, "d": ["crack_dark", "pebbles_dark"]},
}

static func _decals(m: MapData, img: Image, rnd: RandomNumberGenerator) -> void:
	if _decal_img == null:
		_decal_img = (load("res://assets/tiles/decals.png") as Texture2D).get_image()
		_decal_meta = JSON.parse_string(FileAccess.get_file_as_string("res://assets/tiles/decals.json"))
	var names: Array = _decal_meta["names"]
	var cols: int = _decal_meta["cols"]
	var cs: int = _decal_meta["cell"]
	for y in m.h:
		for x in m.w:
			var n := m.name_at(x, y)
			if not DECAL_TABLE.has(n):
				continue
			var tab: Dictionary = DECAL_TABLE[n]
			var count := 0
			var pr: float = tab["p"]
			while rnd.randf() < pr and count < 3:
				count += 1
				pr *= 0.5
				var dn: String = tab["d"][rnd.randi() % tab["d"].size()]
				var k: int = names.find(dn)
				var src := Rect2i((k % cols) * cs, (k / cols) * cs, cs, cs)
				var px := x * T + rnd.randi_range(-2, T - cs + 2)
				var py := y * T + rnd.randi_range(-2, T - cs + 2)
				# keep decals on valid ground: skip if the centre falls on water/wall
				var cx := (px + cs / 2) / T
				var cy := (py + cs / 2) / T
				var cn := m.name_at(cx, cy)
				if Terrain.is_solid(cn):
					continue
				img.blend_rect(_decal_img, src, Vector2i(px, py))
