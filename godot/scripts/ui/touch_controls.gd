class_name TouchControls
extends Node
## On-screen controls for phones: floating joystick (left), action buttons (right), menu buttons (top),
## and a navigation pad while the grimoire / options are open. Tap anywhere to advance dialogue.

var hud: Hud
var layer: Control
var game_buttons: Control
var menu_pad: Control
var stick_base: TextureRect
var stick_knob: TextureRect
var _stick_id := -1
var _stick_origin := Vector2.ZERO
var _fingers := {}      # touch index -> button dict
var _buttons: Array = []   # {c: Control, center: Vector2, r: float, key: int, id: String}
const STICK_R := 140.0
const STICK_C := Vector2(270, 800)


func setup(h: Hud) -> void:
	hud = h
	process_mode = Node.PROCESS_MODE_ALWAYS
	var C := Vector2(0.5, 0.5)
	if hud.fan_node:
		hud.fan_node.visible = false
	if hud.medallion:
		hud.medallion.scale = Vector2.ONE * 0.58
		hud.medallion.position = Vector2(150, 150) - hud.medallion.size / 2.0
	for c in hud.root.get_children():
		if c is Label and c.text.begins_with("WASD"):
			c.visible = false     # keyboard hint is meaningless on a phone
	hud.gold_icon.position = Vector2(300, 30)
	hud.gold_text.position = Vector2(356, 28)
	hud.clock_label.position = Vector2(300, 74)
	hud.pts_label.position = Vector2(300, 104)
	hud.buff_label.position = Vector2(300, 136)
	hud.buff_label.size = Vector2(420, 120)
	layer = Control.new()
	layer.size = Hud.SIZE
	layer.mouse_filter = Control.MOUSE_FILTER_IGNORE
	hud.root.add_child(layer)
	game_buttons = Control.new()
	game_buttons.size = Hud.SIZE
	game_buttons.mouse_filter = Control.MOUSE_FILTER_IGNORE
	layer.add_child(game_buttons)
	# floating stick visuals (shown while a finger is down); a faint ghost marks the idle spot
	# fixed analog stick, bottom-left: ornate ring base + golden knob
	stick_base = hud.img(layer, Sheets.ui("orb"), Vector2(0, 0), Vector2.ZERO, Vector2(STICK_R * 2.3, STICK_R * 2.3))
	stick_knob = hud.img(layer, Sheets.ui("orb"), Vector2(0, 0), Vector2.ZERO, Vector2(118, 118))
	var dot := hud.img(stick_knob, Util.soft_circle(), Vector2(0.5, 0.5), Vector2.ZERO, Vector2(70, 70))
	dot.modulate = Color(1, 0.85, 0.45, 0.8)
	_stick_idle()
	# action buttons (virtual 1920x1080 coordinates)
	_add_btn("attack", Vector2(1700, 800), 105, KEY_J, "skill_sword", 1.0)
	_add_btn("spark", Vector2(1480, 905), 78, KEY_K, "skill_spark", 1.0)
	_add_btn("roll", Vector2(1530, 690), 78, KEY_SPACE, "skill_roll", 1.0)
	_add_btn("potion", Vector2(1830, 590), 68, KEY_Q, "potion", 1.0)
	_add_btn("talk", Vector2(1290, 830), 62, KEY_E, "", 1.0)
	_add_btn("lock", Vector2(1150, 770), 58, KEY_T, "", 1.0)
	_add_btn("meteor", Vector2(1330, 700), 62, KEY_R, "skill_spark", 1.0)
	_add_btn("storm", Vector2(1420, 560), 62, KEY_F, "skill_spark", 1.0)
	_add_btn("slot_g", Vector2(1240, 590), 56, KEY_G, "skill_spark", 1.0)
	_add_btn("slot_v", Vector2(1370, 430), 56, KEY_V, "skill_spark", 1.0)
	_add_btn("book", Vector2(560, 62), 46, KEY_TAB, "", 0.8)
	_add_btn("skills", Vector2(455, 62), 46, KEY_P, "", 0.8)
	_add_btn("menu", Vector2(665, 62), 46, KEY_ESCAPE, "", 0.8)
	# menu navigation pad (grimoire / options)
	menu_pad = Control.new()
	menu_pad.size = Hud.SIZE
	menu_pad.mouse_filter = Control.MOUSE_FILTER_IGNORE
	layer.add_child(menu_pad)
	var pad := [["up", Vector2(1775, 630), KEY_W, "▲"], ["down", Vector2(1775, 910), KEY_S, "▼"], ["left", Vector2(1660, 770), KEY_A, "◀"],
		["right", Vector2(1880, 770), KEY_D, "▶"], ["ok", Vector2(1775, 770), KEY_ENTER, "OK"], ["close", Vector2(1800, 470), KEY_ESCAPE, "✕"]]
	for p in pad:
		_add_btn(p[0], p[1], 56, p[2], "", 1.0, p[3], menu_pad)
	menu_pad.visible = false
	# letters on the game buttons without an icon
	_label_for("meteor", "R")
	_label_for("storm", "F")
	_label_for("slot_g", "G")
	_label_for("slot_v", "V")
	_label_for("talk", "E")
	_label_for("lock", "Alvo")
	_label_for("book", "Livro")
	_label_for("skills", "★")
	_label_for("menu", "Menu")


func _label_for(id: String, text: String) -> void:
	for b in _buttons:
		if b["id"] == id:
			var l := hud.txt(b["c"], text, Util.font_bold, 24 if id == "talk" else 18, Color(1, 0.95, 0.8), Vector2(0.5, 0.5), Vector2(0, 34 if id in ["meteor", "storm", "slot_g", "slot_v"] else 0), Vector2(120, 30))
			l.z_index = 2


func _add_btn(id: String, center: Vector2, r: float, key: int, icon: String, alpha: float, text: String = "", parent: Control = null) -> void:
	var par: Control = parent if parent else game_buttons
	var C := Vector2(0.5, 0.5)
	var c := hud.img(par, Sheets.ui("orb"), Vector2(0, 1), Vector2(center.x, -center.y), Vector2(r * 2, r * 2))
	c.modulate.a = alpha
	if icon != "":
		hud.img(c, Sheets.icon(icon), C, Vector2.ZERO, Vector2(r * 1.1, r * 1.1))
	if text != "":
		hud.txt(c, text, Util.font_bold, 34, Color(1, 0.95, 0.8), C, Vector2.ZERO, Vector2(r * 2, 50))
	_buttons.append({"c": c, "center": center, "r": r, "key": key, "id": id, "pad": parent != null})


func _stick_idle() -> void:
	stick_base.position = STICK_C - stick_base.size / 2.0
	stick_knob.position = STICK_C - stick_knob.size / 2.0
	stick_base.modulate = Color(1, 1, 1, 0.55)
	stick_knob.modulate = Color(1, 1, 1, 0.75)
	Game.touch_move = Vector2.ZERO
	Game.touch_run = false


func _menu_open() -> bool:
	return Game.grimoire.open or Game.options.open or Game.shop.open or Game.skills.open or Game.board.open or Game.tavern.open


func _process(_dt: float) -> void:
	var menu := _menu_open()
	# Keep all gameplay controls hidden through the opening cinematic and
	# prologue. Later story dialogue/cutscenes also take visual priority.
	# Modal navigation remains usable while the Grimoire/Options is paused.
	var playing := Game.flags.has("prologue") and Game.player != null and not Game.player.input_locked
	var cinematic := hud.in_dialogue() or hud.in_credits() or hud.scene_img.visible
	layer.visible = not Game.in_menu and not cinematic and (menu or playing)
	menu_pad.visible = menu and layer.visible
	game_buttons.visible = playing and not menu and layer.visible
	stick_base.visible = game_buttons.visible
	stick_knob.visible = game_buttons.visible
	if (not game_buttons.visible) and _stick_id >= 0:
		_stick_id = -1
		_stick_idle()
	var talking := hud.in_dialogue()
	for b in _buttons:
		if b["id"] == "talk":
			b["c"].modulate.a = 1.0 if _near_npc() else 0.35
		elif b["id"] in ["meteor", "storm", "slot_g", "slot_v"] and Game.player != null:
			# R / F / G / V: the skills equipped in the tree; dimmed while the slot is empty
			var which: String = {"meteor": "r", "storm": "f", "slot_g": "g", "slot_v": "v"}[b["id"]]
			var ic: TextureRect = b["c"].get_child(0)
			if Game.player.gs.has_unlock(which):
				var a: Dictionary = Game.player.gs.slot_skill(which)
				ic.texture = Sheets.icon(a["i"])
				ic.modulate = a["c"]
			b["c"].modulate.a = 1.0 if Game.player.gs.has_unlock(which) else 0.35


func _near_npc() -> bool:
	if Game.player == null:
		return false
	for n in Game.world.entities.get_children():
		if n is Npc and n.visible and (n.global_position - Game.player.global_position).length() < 2.4 * 64.0:
			return true
		if n is Furniture and n.act != "" and (n.global_position - Game.player.global_position).length() < 2.6 * 64.0:
			return true
	return false


func _virtual(p: Vector2) -> Vector2:
	# Input events already arrive in viewport (1920x1080 stretched) coordinates; the camera's canvas
	# transform must NOT be applied (the HUD lives on its own CanvasLayer).
	return p


func _button_at(v: Vector2) -> Dictionary:
	var menu := _menu_open()
	for b in _buttons:
		if not b["c"].visible:
			continue
		if b["pad"] != menu and not (not b["pad"] and menu and (b["id"] == "menu")):
			continue
		if (v - b["center"]).length() <= b["r"] * 1.15:
			return b
	return {}


func _input(ev: InputEvent) -> void:
	if Game.in_menu or hud.in_dialogue() or hud.in_credits():
		# Only tap-to-advance should be accepted inside cinematic dialogue.
		if ev is InputEventScreenTouch and ev.pressed and hud.in_dialogue():
			Game.press_key(KEY_ENTER)
		return
	if ev is InputEventScreenTouch:
		var v := _virtual(ev.position)
		if ev.pressed:
			if not layer.visible:
				return
			var b := _button_at(v)
			if not b.is_empty():
				_fingers[ev.index] = b
				Game.press_key(b["key"])
				b["c"].scale = Vector2(0.92, 0.92)
				return
			if not _menu_open() and _stick_id < 0 and v.x < 900.0 and v.y > 330.0:
				_stick_id = ev.index
				_stick_origin = STICK_C
				stick_base.modulate.a = 0.85
				stick_knob.modulate.a = 1.0
				_drag(v)
		else:
			if _fingers.has(ev.index):
				_fingers[ev.index]["c"].scale = Vector2.ONE
				_fingers.erase(ev.index)
			if ev.index == _stick_id:
				_stick_id = -1
				_stick_idle()
	elif ev is InputEventScreenDrag and ev.index == _stick_id:
		_drag(_virtual(ev.position))


func _drag(v: Vector2) -> void:
	var d := v - _stick_origin
	var m := minf(d.length(), STICK_R)
	var dir := d.normalized() if d.length() > 1.0 else Vector2.ZERO
	stick_knob.position = _stick_origin + dir * m - stick_knob.size / 2.0
	var amount := m / STICK_R
	Game.touch_move = dir * (0.0 if amount < 0.18 else minf(amount * 1.15, 1.0))
	Game.touch_run = amount > 0.92
