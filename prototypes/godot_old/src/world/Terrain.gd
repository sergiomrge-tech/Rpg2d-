class_name Terrain
extends RefCounted
## Terrain registry: names, ranks, flags and tile images.

const T := 32

# pseudo-terrains (no atlas row): water, walls
const WATER := "water"
const DEEP := "deep"
const LAVA := "lava"
const VOID := "void"
const WALL_KINDS := {
	"wall_cave": {"top": "wall_top", "face": "face_cave"},
	"wall_stone": {"top": "wall_top_stone", "face": "face_stone"},
	"wall_dstone": {"top": "wall_top_stone", "face": "face_stone_dark"},
	"wall_house": {"top": "wall_top_house", "face": "face_house"},
	"wall_ice": {"top": "wall_top", "face": "face_ice"},
	"wall_adobe": {"top": "wall_top", "face": "face_adobe"},
	"wall_mossy": {"top": "wall_top", "face": "face_mossy"},
	"wall_battle": {"top": "wall_top_stone", "face": "battlement"},
}

static var meta: Dictionary
static var atlas: Image
static var edges: Image
static var water_tex: Texture2D
static var names: Array = []      # all terrain names, index = id
static var idx: Dictionary = {}   # name -> id
static var rank: Dictionary = {}
static var row_of: Dictionary = {}
static var ready := false

static func setup() -> void:
	if ready:
		return
	meta = JSON.parse_string(FileAccess.get_file_as_string("res://assets/tiles/terrain.json"))
	atlas = (load("res://assets/tiles/terrain.png") as Texture2D).get_image()
	edges = (load("res://assets/tiles/edges.png") as Texture2D).get_image()
	water_tex = load("res://assets/tiles/water.png")
	for n in meta["terrains"]:
		row_of[n] = names.size()
		_add(n, int(meta["rank"][n]))
	for n in [WATER, DEEP, LAVA, VOID]:
		_add(n, 0)
	for n in WALL_KINDS:
		_add(n, 99)
	ready = true

static func _add(n: String, r: int) -> void:
	idx[n] = names.size()
	names.append(n)
	rank[n] = r

static func id(n: String) -> int:
	return idx[n]

static func is_water(n: String) -> bool:
	return n == WATER or n == DEEP

static func is_wall(n: String) -> bool:
	return WALL_KINDS.has(n) or n == VOID

static func is_solid(n: String) -> bool:
	return is_wall(n) or n == WATER or n == DEEP or n == LAVA

static func tile_rect(n: String, variant: int) -> Rect2i:
	return Rect2i((variant % int(meta["variants"])) * T, int(row_of[n]) * T, T, T)

static func wall_rect(face: String, variant: int) -> Rect2i:
	return Rect2i((variant % int(meta["variants"])) * T, int(meta["walls"][face]) * T, T, T)

static func edge_rect(n: String, dir: String) -> Rect2i:
	var k: int = (meta["edge_dirs"] as Array).find(dir)
	return Rect2i(k * T, int(row_of[n]) * T, T, T)
