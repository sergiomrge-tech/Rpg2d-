extends Node
## Loads PNG+JSON sprite sheets produced by tools/art_hd and slices them into AtlasTexture frames.

class SheetData:
	var frame_w := 0
	var frame_h := 0
	var pivot_x := 0
	var pivot_y := 0   # from bottom
	var cols := 1
	var frames: Array[AtlasTexture] = []
	var anims := {}    # name -> {start,count,fps,loop,hit}
	var offset := Vector2.ZERO   # Sprite2D offset (centered=false) that puts the pivot at the node origin

var _sheets := {}
var _tex := {}
var _props := {}
var _props_loaded := false


func tex(path: String) -> Texture2D:
	if _tex.has(path):
		return _tex[path]
	var p := "res://assets/%s.png" % path
	var t: Texture2D = load(p) if ResourceLoader.exists(p) else null
	if t == null:
		push_warning("missing texture " + path)
	_tex[path] = t
	return t


func read_json(path: String) -> Variant:
	var f := FileAccess.open("res://assets/%s.json" % path, FileAccess.READ)
	if f == null:
		push_warning("missing json " + path)
		return null
	return JSON.parse_string(f.get_as_text())


func sheet(path: String) -> SheetData:
	if _sheets.has(path):
		return _sheets[path]
	var d = read_json(path)
	var t := tex(path)
	if d == null or t == null:
		return null
	var s := SheetData.new()
	s.frame_w = int(d["frameW"])
	s.frame_h = int(d["frameH"])
	s.pivot_x = int(d["pivotX"])
	s.pivot_y = int(d["pivotY"])
	s.cols = int(d["cols"])
	s.offset = Vector2(-s.pivot_x, -(s.frame_h - s.pivot_y))
	var total := 0
	for a in d["anims"]:
		s.anims[a["name"]] = a
		total = maxi(total, int(a["start"]) + int(a["count"]))
	s.frames.resize(total)
	for i in total:
		var at := AtlasTexture.new()
		at.atlas = t
		at.region = Rect2((i % s.cols) * s.frame_w, (i / s.cols) * s.frame_h, s.frame_w, s.frame_h)
		s.frames[i] = at
	_sheets[path] = s
	return s


func prop_info(name: String) -> Dictionary:
	if not _props_loaded:
		_props_loaded = true
		var d = read_json("Sprites/Env/props")
		if d:
			for p in d["props"]:
				_props[p["name"]] = p
	return _props.get(name, {})


func prop_texture(name: String) -> Texture2D:
	return tex("Sprites/Env/" + name)


## Icon from the Ui/icons sheet by id (first frame of the animation named like the icon).
func icon(id: String) -> Texture2D:
	var s := sheet("Sprites/Ui/icons")
	if s == null or not s.anims.has(id):
		return Util.soft_circle()
	return s.frames[int(s.anims[id]["start"])]


func ui(name: String) -> Texture2D:
	return tex("Sprites/Ui/" + name)
