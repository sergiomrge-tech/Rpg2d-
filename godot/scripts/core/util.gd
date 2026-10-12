extends Node
## Shared helpers: facing, soft-circle texture, shadows, materials.

const TILE := 64.0
enum Face { DOWN, UP, LEFT, RIGHT }

var fx_shader: Shader = preload("res://shaders/fx.gdshader")
var font_serif: FontFile = load("res://assets/Fonts/Cinzel-700.ttf")
var font_sans: FontFile = load("res://assets/Fonts/Inter-Medium.otf")
var font_bold: FontFile = load("res://assets/Fonts/Inter-Bold.otf")

var _soft: GradientTexture2D
var _add_mat: CanvasItemMaterial


func facing_from(d: Vector2, fallback: int) -> int:
	if d.length_squared() < 0.0001:
		return fallback
	if absf(d.x) > absf(d.y) * 0.9:
		return Face.RIGHT if d.x > 0.0 else Face.LEFT
	return Face.DOWN if d.y > 0.0 else Face.UP


func facing_vec(f: int) -> Vector2:
	match f:
		Face.UP: return Vector2.UP
		Face.LEFT: return Vector2.LEFT
		Face.RIGHT: return Vector2.RIGHT
	return Vector2.DOWN


func soft_circle() -> GradientTexture2D:
	if _soft == null:
		var g := Gradient.new()
		g.colors = PackedColorArray([Color(1, 1, 1, 1), Color(1, 1, 1, 0)])
		g.offsets = PackedFloat32Array([0.0, 1.0])
		_soft = GradientTexture2D.new()
		_soft.gradient = g
		_soft.fill = GradientTexture2D.FILL_RADIAL
		_soft.fill_from = Vector2(0.5, 0.5)
		_soft.fill_to = Vector2(1.0, 0.5)
		_soft.width = 128
		_soft.height = 128
	return _soft


func additive() -> CanvasItemMaterial:
	if _add_mat == null:
		_add_mat = CanvasItemMaterial.new()
		_add_mat.blend_mode = CanvasItemMaterial.BLEND_MODE_ADD
	return _add_mat


func make_shadow(parent: Node, w: float, h: float, alpha: float = 0.32) -> Sprite2D:
	var s := Sprite2D.new()
	s.texture = soft_circle()
	s.scale = Vector2(w * TILE / 128.0, h * TILE / 128.0)
	s.modulate = Color(0.08, 0.12, 0.1, alpha)
	s.z_index = -1
	s.show_behind_parent = true
	parent.add_child(s)
	return s


func glow(parent: Node, color: Color, size_tiles: float, alpha: float) -> Sprite2D:
	var s := Sprite2D.new()
	s.texture = soft_circle()
	s.scale = Vector2.ONE * size_tiles * TILE / 128.0
	s.modulate = Color(color.r, color.g, color.b, alpha)
	s.material = additive()
	parent.add_child(s)
	return s


func make_fx_material() -> ShaderMaterial:
	var m := ShaderMaterial.new()
	m.shader = fx_shader
	return m


func approach(v: float, target: float, delta: float) -> float:
	return minf(v + delta, target) if v < target else maxf(v - delta, target)


func label(text: String, size: int, color: Color, font: Font = null, outline: bool = true) -> Label:
	var l := Label.new()
	l.text = text
	var ls := LabelSettings.new()
	ls.font = font if font else font_sans
	# Inter is wider than the old condensed face: keep the layouts, gain legibility from the heavier strokes
	if ls.font == font_sans or ls.font == font_bold:
		size = roundi(size * 0.92)
	# phones: small screen, same 1920x1080 canvas -> bigger text everywhere
	ls.font_size = roundi(size * 1.3) if Game.touch_mode else size
	ls.font_color = color
	if outline:
		ls.outline_size = 5
		ls.outline_color = Color(0.12, 0.06, 0.08, 0.95)
		ls.shadow_color = Color(0, 0, 0, 0.45)
		ls.shadow_offset = Vector2(2, 3)
	l.label_settings = ls
	return l
