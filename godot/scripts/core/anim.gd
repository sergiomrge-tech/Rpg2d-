class_name Anim
extends Sprite2D
## Directional sprite-sheet animation. Plays "<name>_down|up|side" (side is mirrored for left).

signal hit(base: String)
signal ended(base: String)

var sheet: Sheets.SheetData
var facing: int = Util.Face.DOWN
var speed := 1.0
var current := ""
var base := ""
var finished := false
var frame_idx := 0

var _info: Dictionary = {}
var _t := 0.0
var _last := -1


static func suffix(f: int) -> String:
	return "_down" if f == Util.Face.DOWN else ("_up" if f == Util.Face.UP else "_side")


func setup(sheet_path: String) -> void:
	sheet = Sheets.sheet(sheet_path)
	centered = false
	if sheet:
		offset = sheet.offset


func normalized() -> float:
	if _info.is_empty():
		return 1.0
	return clampf(_t * float(_info["fps"]) / float(_info["count"]), 0.0, 1.0)


func play(name: String, restart: bool = false) -> void:
	if sheet == null:
		return
	var full := name + suffix(facing)
	if not restart and full == current:
		return
	var a = sheet.anims.get(full, sheet.anims.get(name, null))
	if a == null:
		return
	base = name
	current = full
	_info = a
	_t = 0.0
	_last = -1
	finished = false
	_apply()


func set_facing(f: int) -> void:
	if f == facing:
		return
	facing = f
	if base != "":
		var keep := _t
		var n := base
		current = ""
		play(n, true)
		_t = keep
		_apply()


func _process(delta: float) -> void:
	if _info.is_empty():
		return
	_t += delta * speed
	_apply()


func _apply() -> void:
	var cnt := int(_info["count"])
	var f := int(floor(_t * float(_info["fps"])))
	if _info["loop"]:
		f = f % cnt
	elif f >= cnt:
		f = cnt - 1
		if not finished:
			finished = true
			ended.emit(base)
	if f != _last:
		var h := int(_info["hit"])
		if h >= 0 and _last < h and f >= h:
			hit.emit(base)
		_last = f
		frame_idx = f
		texture = sheet.frames[int(_info["start"]) + f]
	flip_h = facing == Util.Face.LEFT
