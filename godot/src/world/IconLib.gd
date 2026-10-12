class_name IconLib
extends RefCounted

static var cache := {}

static func get_icon(name: String) -> Texture2D:
	if cache.has(name):
		return cache[name]
	var p := "res://assets/icons/%s.png" % name
	var t: Texture2D = load(p) if ResourceLoader.exists(p) else null
	if t == null:
		t = Fx.glow_tex()
	cache[name] = t
	return t
