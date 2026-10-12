class_name ClassSelect
extends Node
## Native, touch-first class selector shown after Novo Jogo, before the prologue.
## Uses only the game's existing approved UI art, not conceptual images.

var hud: Hud
var root: Control
var active := true
var selected := 0
var cards: Array[Button] = []
var confirm_button: Button
var on_select := Callable()
var on_cancel := Callable()
var _elapsed := 0.0

const INK := Color(0.98, 0.92, 0.81)
const GOLD := Color(0.96, 0.78, 0.45)
const C := Vector2(0.5, 0.5)
const WIDTH := 555.0
const HEIGHT := 252.0


func setup(h: Hud, chosen: Callable, cancel: Callable) -> void:
	hud = h
	on_select = chosen
	on_cancel = cancel
	process_mode = Node.PROCESS_MODE_ALWAYS
	root = hud.ctl(hud.root, C, Vector2.ZERO, Hud.SIZE)
	root.mouse_filter = Control.MOUSE_FILTER_IGNORE
	hud.img(root, Sheets.tex("Sprites/Cutscenes/vista"), C, Vector2.ZERO, Hud.SIZE)
	var dark := hud.img(root, Sheets.ui("vignette"), C, Vector2.ZERO, Hud.SIZE)
	dark.modulate = Color(0.07, 0.04, 0.10, 0.96)
	hud.img(root, Sheets.ui("flourish"), C, Vector2(0, 370), Vector2(640, 55))
	hud.txt(root, "ESCOLHA SEU CAMINHO", Util.font_serif, 71, GOLD, C,
			Vector2(0, 415), Vector2(1400, 108))
	hud.txt(root, "Cada classe tem armas, poderes, vantagens e fraquezas próprias.", Util.font_sans,
			31, INK, C, Vector2(0, 325), Vector2(1600, 58))
	for i in HeroClasses.ORDER.size():
		var id: String = HeroClasses.ORDER[i]
		var d: Dictionary = HeroClasses.info(id)
		var x: float = -595 + (i % 3) * 595
		var y: float = 90 - int(i / 3) * 275
		var btn := Button.new()
		btn.text = ""
		btn.name = "Class_" + id
		hud.ctl(root, C, Vector2(x, y), Vector2(WIDTH, HEIGHT), btn)
		btn.mouse_filter = Control.MOUSE_FILTER_STOP  # ctl defaults to IGNORE
		btn.focus_mode = Control.FOCUS_NONE
		btn.process_mode = Node.PROCESS_MODE_ALWAYS
		btn.pressed.connect(_pick.bind(i))
		cards.append(btn)
		var tint: Color = d["color"]
		hud.img(btn, Sheets.icon(d["icon"]), C, Vector2(-209, 65), Vector2(70, 70)).modulate = tint
		hud.txt(btn, str(d["name"]), Util.font_serif, 40, tint, C,
				Vector2(35, 88), Vector2(390, 50))
		hud.txt(btn, str(d["role"]), Util.font_sans, 25, INK, C,
				Vector2(0, 33), Vector2(508, 39))
		var strong := hud.txt(btn, "FORTE: " + str(d["strong"]), Util.font_sans, 23,
				Color(0.64, 0.95, 0.70), C, Vector2(0, -24), Vector2(510, 47))
		strong.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
		var weak := hud.txt(btn, "FRACO: " + str(d["weak"]), Util.font_sans, 23,
				Color(0.99, 0.72, 0.65), C, Vector2(0, -82), Vector2(510, 50))
		weak.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART

	confirm_button = Button.new()
	confirm_button.name = "ConfirmarClasse"
	confirm_button.text = "INICIAR COMO GUERREIRO"
	hud.ctl(root, C, Vector2(0, -408), Vector2(640, 81), confirm_button)
	confirm_button.mouse_filter = Control.MOUSE_FILTER_STOP
	confirm_button.focus_mode = Control.FOCUS_NONE
	confirm_button.process_mode = Node.PROCESS_MODE_ALWAYS
	confirm_button.pressed.connect(_confirm)
	confirm_button.add_theme_font_override("font", Util.font_bold)
	confirm_button.add_theme_font_size_override("font_size", 32)
	confirm_button.add_theme_color_override("font_color", Color(0.18, 0.12, 0.11))
	var gold := StyleBoxFlat.new()
	gold.bg_color = GOLD
	gold.border_color = Color(1.0, 0.94, 0.67)
	gold.set_border_width_all(3)
	gold.set_corner_radius_all(24)
	confirm_button.add_theme_stylebox_override("normal", gold)
	confirm_button.add_theme_stylebox_override("hover", gold)
	confirm_button.add_theme_stylebox_override("pressed", gold)
	hud.txt(root, "Toque na classe · confirme abaixo  |  Esc: voltar", Util.font_sans,
			25, INK, C, Vector2(0, -485), Vector2(1100, 40))
	_refresh()
	Game.in_menu = true
	get_tree().paused = true


func _style(tint: Color, chosen: bool) -> StyleBoxFlat:
	var style := StyleBoxFlat.new()
	style.bg_color = Color(0.11, 0.09, 0.13, 0.95) if not chosen else Color(0.19, 0.15, 0.18, 0.98)
	style.border_color = tint if chosen else Color(tint.r, tint.g, tint.b, 0.45)
	style.set_border_width_all(4 if chosen else 2)
	style.set_corner_radius_all(23)
	style.shadow_color = Color(tint.r, tint.g, tint.b, 0.20 if chosen else 0.04)
	style.shadow_size = 11 if chosen else 4
	return style


func _refresh() -> void:
	for i in cards.size():
		var tint: Color = HeroClasses.info(HeroClasses.ORDER[i])["color"]
		var box := _style(tint, i == selected)
		cards[i].add_theme_stylebox_override("normal", box)
		cards[i].add_theme_stylebox_override("hover", box)
		cards[i].add_theme_stylebox_override("pressed", box)
	confirm_button.text = "INICIAR COMO " + str(HeroClasses.info(HeroClasses.ORDER[selected])["name"]).to_upper()


func _pick(i: int) -> void:
	if not active:
		return
	selected = clampi(i, 0, HeroClasses.ORDER.size() - 1)
	_refresh()
	Sfx.play("ui", 0.35, 1.0)


func _confirm() -> void:
	if not active:
		return
	var class_id: String = HeroClasses.ORDER[selected]
	close()
	on_select.call(class_id)


func _cancel() -> void:
	if not active:
		return
	close()
	on_cancel.call()


func close() -> void:
	active = false
	root.visible = false
	root.queue_free()
	Game.in_menu = false
	get_tree().paused = false


func _input(ev: InputEvent) -> void:
	# Android does not emulate a mouse from touches in this project.
	# Handle touch directly, in addition to native Button.pressed.
	if not active or not (ev is InputEventScreenTouch) or not ev.pressed:
		return
	for i in cards.size():
		if cards[i].get_global_rect().has_point(ev.position):
			_pick(i)
			get_viewport().set_input_as_handled()
			return
	if confirm_button.get_global_rect().has_point(ev.position):
		_confirm()
		get_viewport().set_input_as_handled()


func _process(_dt: float) -> void:
	if not active:
		return
	if Game.consume(KEY_ESCAPE):
		_cancel()
		return
	if Game.consume(KEY_LEFT) or Game.consume(KEY_A):
		_pick((selected + 2) % 3 + int(selected / 3) * 3)
	if Game.consume(KEY_RIGHT) or Game.consume(KEY_D):
		_pick((selected + 1) % 3 + int(selected / 3) * 3)
	if Game.consume(KEY_UP) or Game.consume(KEY_W) or Game.consume(KEY_DOWN) or Game.consume(KEY_S):
		_pick((selected + 3) % HeroClasses.ORDER.size())
	if Game.consume(KEY_ENTER) or Game.consume(KEY_KP_ENTER) or Game.consume(KEY_SPACE):
		_confirm()
