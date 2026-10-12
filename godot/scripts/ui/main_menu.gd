class_name MainMenu
extends Node
## Title screen: Continue / New game / Options / Quit. Keyboard (W/S + Enter), mouse and touch.

var hud: Hud
var root: Control
var items: Array = []        # {id, label(Label), mark(Label), center(Vector2), enabled}
var sel := 0
var active := true
var _t := 0.0
var _glow: TextureRect
var _hero: TextureRect
var on_continue := Callable()
var on_new := Callable()
var on_ngplus := Callable()


func setup(h: Hud, has_save: bool, ngp: bool = false) -> void:
	hud = h
	process_mode = Node.PROCESS_MODE_ALWAYS
	var C := Vector2(0.5, 0.5)
	root = hud.ctl(hud.root, C, Vector2.ZERO, Hud.SIZE)
	hud.img(root, Sheets.tex("Sprites/Cutscenes/vista"), C, Vector2.ZERO, Hud.SIZE)
	hud.img(root, Sheets.ui("vignette"), C, Vector2.ZERO, Hud.SIZE).modulate = Color(0, 0, 0, 0.9)
	var shade := hud.img(root, Util.soft_circle(), C, Vector2(-420, -80), Vector2(1500, 1500))
	shade.modulate = Color(0.03, 0.01, 0.06, 0.75)
	_glow = hud.img(root, Util.soft_circle(), C, Vector2(-420, 170), Vector2(1000, 420))
	_glow.material = Util.additive()
	_glow.modulate = Color(1, 0.75, 0.3, 0.18)
	hud.txt(root, "CRÔNICAS DE", Util.font_serif, 54, Color(1, 0.9, 0.7), C, Vector2(-420, 370), Vector2(900, 70))
	hud.txt(root, "AETHERIA", Util.font_serif, 130, Color(1, 0.93, 0.72), C, Vector2(-420, 270), Vector2(1100, 160))
	hud.img(root, Sheets.ui("flourish"), C, Vector2(-420, 180), Vector2(640, 54))
	hud.txt(root, "A Centelha", Util.font_sans, 48, Color(1, 0.82, 0.5), C, Vector2(-420, 120), Vector2(700, 60))
	_hero = hud.img(root, Sheets.ui("portrait"), C, Vector2(560, 30), Vector2(430, 430))
	hud.img(root, Sheets.ui("medallion"), C, Vector2(560, 30), Vector2(640, 640))
	var entries := []
	if has_save:
		entries.append(["continue", "Continuar"])
	if ngp:
		entries.append(["ngplus", "Novo Jogo+"])
	entries.append(["new", "Novo Jogo"])
	entries.append(["options", "Opções"])
	if OS.has_feature("pc"):
		entries.append(["quit", "Sair"])
	for i in entries.size():
		var y := -20.0 - i * 92.0
		var mark := hud.txt(root, "◆", Util.font_serif, 34, Color(1, 0.8, 0.3), C, Vector2(-640, y), Vector2(50, 50))
		var l := hud.txt(root, entries[i][1], Util.font_bold, 52, Color(1, 0.96, 0.86), C, Vector2(-420, y), Vector2(560, 70))
		items.append({"id": entries[i][0], "label": l, "mark": mark, "center": Vector2(960 - 420, 540 - y)})
	hud.txt(root, "W/S escolher  ·  Enter confirmar  ·  ou toque na opção", Util.font_sans, 24, Color(1, 1, 1, 0.6), C, Vector2(-420, -430), Vector2(1000, 34))
	Game.in_menu = true
	get_tree().paused = true
	_refresh()


func _refresh() -> void:
	for i in items.size():
		items[i]["mark"].modulate.a = 1.0 if i == sel else 0.0
		items[i]["label"].modulate = Color(1, 0.88, 0.5) if i == sel else Color(1, 1, 1, 0.85)


func close() -> void:
	active = false
	root.visible = false
	Game.in_menu = false
	get_tree().paused = false


func reopen() -> void:
	active = true
	root.visible = true
	Game.in_menu = true
	get_tree().paused = true
	_refresh()


func _activate() -> void:
	Sfx.play("ui", 0.4, 1.0)
	match items[sel]["id"]:
		"continue":
			close()
			on_continue.call()
		"new":
			close()
			on_new.call()
		"ngplus":
			close()
			on_ngplus.call()
		"options":
			Game.options.toggle()
		"quit":
			get_tree().quit()


func _process(dt: float) -> void:
	if not active:
		return
	_t += dt
	_glow.modulate.a = 0.14 + 0.06 * sin(_t * 1.6)
	_hero.position.y += sin(_t * 1.4) * 0.12
	if Game.options.open:
		return
	if Game.consume(KEY_S) or Game.consume(KEY_DOWN):
		sel = (sel + 1) % items.size()
		Sfx.play("ui", 0.2, 1.3)
		_refresh()
	if Game.consume(KEY_W) or Game.consume(KEY_UP):
		sel = (sel + items.size() - 1) % items.size()
		Sfx.play("ui", 0.2, 1.3)
		_refresh()
	if Game.consume(KEY_ENTER) or Game.consume(KEY_KP_ENTER) or Game.consume(KEY_SPACE):
		_activate()


func _input(ev: InputEvent) -> void:
	if not active or Game.options.open:
		return
	var p := Vector2.ZERO
	if ev is InputEventScreenTouch and ev.pressed:
		p = ev.position
	elif ev is InputEventMouseButton and ev.pressed and ev.button_index == MOUSE_BUTTON_LEFT:
		p = ev.position
	else:
		return
	for i in items.size():
		var c: Vector2 = items[i]["center"]
		if absf(p.x - c.x) < 300.0 and absf(p.y - c.y) < 46.0:
			sel = i
			_refresh()
			_activate()
			return
