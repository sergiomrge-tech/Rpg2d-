class_name SpriteLib
extends RefCounted
## Builds SpriteFrames from a sheet (PNG) + manifest (JSON) produced by tools/art.

static var _cache := {}

static func load_frames(name: String) -> SpriteFrames:
	if _cache.has(name):
		return _cache[name]
	var tex: Texture2D = load("res://assets/sprites/%s.png" % name)
	var meta = JSON.parse_string(FileAccess.get_file_as_string("res://assets/sprites/%s.json" % name))
	var sf := SpriteFrames.new()
	sf.remove_animation("default")
	var fw: int = meta["frame_w"]
	var fh: int = meta["frame_h"]
	var hits := {}
	for r in meta["rows"]:
		var an: String = "%s_%s" % [r["anim"], r["dir"]]
		sf.add_animation(an)
		sf.set_animation_speed(an, r["fps"])
		sf.set_animation_loop(an, r["loop"])
		hits[an] = int(r.get("hit", 0))
		for i in r["frames"]:
			var at := AtlasTexture.new()
			at.atlas = tex
			at.region = Rect2(i * fw, r["row"] * fh, fw, fh)
			sf.add_frame(an, at)
	sf.set_meta("hit", hits)
	sf.set_meta("fw", fw)
	sf.set_meta("fh", fh)
	sf.set_meta("ground", int(meta.get("ground", fh - 8)))
	_cache[name] = sf
	return sf

## Vertical sprite offset so the sheet's ground line sits on the node origin.
static func offset_y(sf: SpriteFrames) -> float:
	return float(sf.get_meta("fh")) / 2.0 - float(sf.get_meta("ground"))
