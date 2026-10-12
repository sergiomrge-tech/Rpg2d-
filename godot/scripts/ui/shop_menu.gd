class_name ShopMenu
extends Node
## Blacksmith shop drawn on the leather book: stock for the hero's weapon type, armor, charms and forge embers.

const ROWS := 7

var open := false
var hud: Hud
var root: Control
var page: Control
var close_button: Button
var sel := 0
var top := 0
var stock: Array = []
var smith := "blacksmith"
var btns: Array = []


func setup(h: Hud) -> void:
	process_mode = Node.PROCESS_MODE_ALWAYS
	hud = h
	var C := Vector2(0.5, 0.5)
	root = hud.ctl(hud.root, C, Vector2.ZERO, Hud.SIZE)
	var dim := hud.img(root, Util.soft_circle(), C, Vector2.ZERO, Vector2(2600, 1800))
	dim.modulate = Color(0.02, 0.01, 0.04, 0.75)
	hud.img(root, Sheets.ui("book"), C, Vector2.ZERO, Vector2(1400, 860))
	close_button = Button.new()
	close_button.text = "X"
	close_button.focus_mode = Control.FOCUS_NONE
	hud.ctl(root, C, Vector2(620, 354), Vector2(88, 88), close_button)
	close_button.mouse_filter = Control.MOUSE_FILTER_STOP
	close_button.process_mode = Node.PROCESS_MODE_ALWAYS
	close_button.add_theme_font_override("font", Util.font_serif)
	close_button.add_theme_font_size_override("font_size", 45)
	close_button.add_theme_color_override("font_color", Color(1.0, 0.93, 0.76))
	var st := StyleBoxFlat.new()
	st.bg_color = Color(0.32, 0.12, 0.1, 0.94)
	st.border_color = Color(0.87, 0.67, 0.37)
	st.set_border_width_all(3)
	st.set_corner_radius_all(22)
	for k in ["normal", "hover", "pressed"]:
		close_button.add_theme_stylebox_override(k, st)
	close_button.pressed.connect(close)
	root.visible = false


func _build_stock() -> void:
	var gs := Game.state
	var fam: String = {"sword": "sw", "bow": "bw", "dual_daggers": "dg", "staff": "st"}.get(str(HeroClasses.info(gs.class_id)["weapon"]), "sw")
	var tiers := [0, 1] if smith == "blacksmith" else [1, 2, 3]
	stock = []
	for t in tiers:
		for f in [fam, "ar", "ch"]:
			stock.append("%s_%d" % [f, t])
	stock.append("hell_ember")
	stock.append("potion")


func price(id: String) -> int:
	var d: Dictionary = Data.items[id]
	var v := float(d.get("value", 25))
	if id == "hell_ember":
		return 90
	return roundi(v * (1.0 if int(d.get("slot", 0)) > 0 else 1.2))


func open_for(npc_id: String) -> void:
	smith = npc_id
	_build_stock()
	sel = 0
	top = 0
	open = true
	root.visible = true
	get_tree().paused = true
	if Player.I != null:
		Player.I.input_locked = true
	Sfx.play("ui", 0.3, 0.8)
	_refresh()


func close() -> void:
	if not open:
		return
	open = false
	root.visible = false
	get_tree().paused = Game.in_menu or Game.grimoire.open or (Game.options != null and Game.options.open)
	if Player.I != null:
		Player.I.input_locked = get_tree().paused
	Sfx.play("ui", 0.3, 0.8)


func _input(event: InputEvent) -> void:
	if not open:
		return
	if event is InputEventScreenTouch and event.pressed:
		if close_button.get_global_rect().grow(10.0).has_point(event.position):
			close()
			get_viewport().set_input_as_handled()
			return
		for b in btns:
			if is_instance_valid(b[0]) and b[0].get_global_rect().has_point(event.position):
				get_viewport().set_input_as_handled()
				b[1].call()
				return


func _process(_dt: float) -> void:
	if not open:
		return
	if Game.consume(KEY_ESCAPE) or Game.consume(KEY_TAB):
		close()
		return
	var n := stock.size()
	if Game.consume(KEY_S) or Game.consume(KEY_DOWN):
		sel = (sel + 1) % n
		_refresh()
	if Game.consume(KEY_W) or Game.consume(KEY_UP):
		sel = (sel + n - 1) % n
		_refresh()
	if Game.consume(KEY_ENTER) or Game.consume(KEY_E):
		_buy()


func _pick(i: int) -> void:
	sel = i
	Sfx.play("ui", 0.2, 1.0)
	_refresh()


func _buy() -> void:
	var gs := Game.state
	var id: String = stock[sel]
	var cost := price(id)
	if gs.gold < cost:
		Sfx.play("ui", 0.2, 0.6)
		Fx.toast("Ouro insuficiente", Color(1.0, .66, .51))
		return
	if int(Data.items[id].get("slot", 0)) == 1 and not HeroClasses.can_equip(gs.class_id, Data.items[id]):
		Sfx.play("ui", 0.2, 0.6)
		Fx.toast("Sua classe não usa esta arma", Color(1.0, .66, .51))
		return
	gs.gold -= cost
	gs.add(id, 1)
	Sfx.play("coin", 0.6, 1.0)
	Fx.toast("%s comprado" % Data.items[id]["name"], Color(1, 0.95, 0.8))
	_refresh()


func _btn(parent: Control, label: String, pos: Vector2, size: Vector2, fn: Callable, fill: Color) -> void:
	var b := Button.new()
	b.text = label
	b.focus_mode = Control.FOCUS_NONE
	b.process_mode = Node.PROCESS_MODE_ALWAYS
	hud.ctl(parent, Vector2(0.5, 0.5), pos, size, b)
	b.mouse_filter = Control.MOUSE_FILTER_STOP
	b.add_theme_font_override("font", Util.font_bold)
	b.add_theme_font_size_override("font_size", 26)
	b.add_theme_color_override("font_color", Color(1.0, 0.93, 0.76))
	var st := StyleBoxFlat.new()
	st.bg_color = fill
	st.border_color = Color(0.87, 0.67, 0.37)
	st.set_border_width_all(2)
	st.set_corner_radius_all(14)
	for k in ["normal", "hover", "pressed"]:
		b.add_theme_stylebox_override(k, st)
	b.pressed.connect(fn)
	btns.append([b, fn])


func _row_btn(parent: Control, pos: Vector2, size: Vector2, fn: Callable) -> void:
	var b := Button.new()
	b.flat = true
	b.focus_mode = Control.FOCUS_NONE
	b.process_mode = Node.PROCESS_MODE_ALWAYS
	hud.ctl(parent, Vector2(0.5, 0.5), pos, size, b)
	b.mouse_filter = Control.MOUSE_FILTER_STOP
	b.pressed.connect(fn)
	btns.append([b, fn])


func _refresh() -> void:
	if page:
		page.queue_free()
	btns.clear()
	var C := Vector2(0.5, 0.5)
	page = hud.ctl(root, C, Vector2.ZERO, Vector2(1400, 860))
	var gs := Game.state
	var ink := Color(0.27, 0.16, 0.1)
	var faint := Color(0.45, 0.32, 0.2)
	var serif := Util.font_serif
	var sans := Util.font_sans
	var bold := Util.font_bold
	var L := HORIZONTAL_ALIGNMENT_LEFT
	var M := HORIZONTAL_ALIGNMENT_CENTER
	var R := HORIZONTAL_ALIGNMENT_RIGHT
	sel = clampi(sel, 0, stock.size() - 1)
	if sel < top:
		top = sel
	elif sel >= top + ROWS:
		top = sel - ROWS + 1
	# ---- left page: the stock
	hud.txt(page, "Ferreiro", serif, 44, ink, C, Vector2(-335, 300), Vector2(500, 60), M, false)
	for r in mini(stock.size() - top, ROWS):
		var i := top + r
		var d: Dictionary = Data.items[stock[i]]
		var y := 220.0 - r * 56.0
		if i == sel:
			hud.img(page, Sheets.ui("smear"), C, Vector2(-335, y), Vector2(560, 70)).modulate = Color(0.85, 0.6, 0.2, 0.35)
		hud.img(page, Sheets.icon(d["icon"]), C, Vector2(-560, y), Vector2(48, 48))
		var rc: Color = Data.RARITY_COLORS[int(d["rarity"])]
		hud.txt(page, d["name"], bold, 24, ink if int(d["rarity"]) == 0 else rc.lerp(ink, 0.45), C, Vector2(-345, y), Vector2(330, 34), L, false)
		hud.txt(page, "%d" % price(stock[i]), serif, 26, Color(0.6, 0.42, 0.05) if gs.gold >= price(stock[i]) else Color(0.7, 0.2, 0.15), C, Vector2(-130, y), Vector2(80, 34), R, false)
		_row_btn(page, Vector2(-335, y), Vector2(560, 54), _pick.bind(i))
	# ---- right page: details
	var id: String = stock[sel]
	var d: Dictionary = Data.items[id]
	var rar := int(d["rarity"])
	hud.txt(page, "Ouro: %d" % gs.gold, serif, 36, Color(0.6, 0.42, 0.05), C, Vector2(335, 300), Vector2(500, 50), M, false)
	hud.img(page, Sheets.icon(d["icon"]), C, Vector2(335, 195), Vector2(110, 110))
	hud.txt(page, d["name"], bold, 30, (Data.RARITY_COLORS[rar] as Color).lerp(ink, 0.4), C, Vector2(335, 110), Vector2(520, 40), M, false)
	hud.txt(page, Data.RARITY_NAMES[rar].to_upper(), bold, 22, (Data.RARITY_COLORS[rar] as Color).lerp(ink, 0.35), C, Vector2(335, 72), Vector2(520, 30), M, false)
	var line := ""
	for kv in [["atk", "ATQ"], ["defense", "DEF"], ["mag", "MAG"], ["hp", "PV"]]:
		if float(d[kv[0]]) > 0:
			line += "%s +%d   " % [kv[1], roundi(d[kv[0]])]
	if d.has("set"):
		line += "\nConjunto %s" % d["set"]
	var det := hud.txt(page, line + ("\n" if line != "" else "") + str(d["desc"]), sans, 22, ink, C, Vector2(335, -30), Vector2(520, 180), M, false, VERTICAL_ALIGNMENT_TOP)
	det.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	_btn(page, "Comprar  %d" % price(id), Vector2(335, -250), Vector2(300, 64), _buy, Color(0.4, 0.2, 0.08, 0.95))
	if gs.count(id) > 0:
		hud.txt(page, "Na bolsa: %d" % gs.count(id), sans, 21, faint, C, Vector2(335, -310), Vector2(300, 28), M, false)
