class_name TavernMenu
extends Node
## Inn / bakery menu: rent a room for the night (restores HP and MP, skips to morning, optional rested buff) and buy food
## with special effects. Opens after talking to an innkeeper or baker (or by interacting with the room doors).

const ROOMS := [
	{"name": "Quarto Simples", "price": 40, "desc": "Cama de palha e um cobertor. Restaura toda a vida e mana e avança para a manhã.", "buff": {}},
	{"name": "Quarto Confortável", "price": 100, "desc": "Colchão macio e janela para o jardim. Restaura tudo e deixa você Descansado por 15 min: +10% EXP e +0,6 mana/s.",
		"buff": {"xp_pct": 10.0, "regen": 0.6}, "secs": 900.0, "label": "Descansado"},
	{"name": "Suíte Real", "price": 220, "desc": "Lençóis de seda e café da manhã. Restaura tudo e concede a Bênção do Repouso por 20 min: +12% ataque, +12% magia, +10% EXP e +25 vida.",
		"buff": {"atk_pct": 12.0, "mag_pct": 12.0, "xp_pct": 10.0, "hp": 25.0}, "secs": 1200.0, "label": "Bênção do Repouso"},
]

const FOODS := [
	{"id": "pao_mel", "name": "Pão de Mel", "price": 12, "icon": "horn", "heal": 30, "mana": 0, "secs": 300.0, "label": "Pão de Mel",
		"eff": {"regen": 0.6}, "desc": "Doce e quentinho. Cura 30 de vida; +0,6 mana/s por 5 min."},
	{"id": "torta", "name": "Torta de Frutas Silvestres", "price": 28, "icon": "ether", "heal": 0, "mana": 40, "secs": 600.0, "label": "Torta de Frutas",
		"eff": {"mag_pct": 8.0, "regen": 0.4}, "desc": "Recupera 40% da mana; +8% magia e +0,4 mana/s por 10 min."},
	{"id": "ensopado", "name": "Ensopado de Javali", "price": 35, "icon": "ember", "heal": 40, "mana": 0, "secs": 600.0, "label": "Ensopado de Javali",
		"eff": {"hp": 60.0, "def": 3.0}, "desc": "Cura 40% da vida; +60 vida máxima e +3 defesa por 10 min."},
	{"id": "espetinho", "name": "Espetinho de Diabrete", "price": 30, "icon": "ember", "heal": 0, "mana": 0, "secs": 600.0, "label": "Espetinho de Diabrete",
		"eff": {"atk_pct": 10.0, "crit": 3.0}, "desc": "Apimentado! +10% ataque e +3% crítico por 10 min."},
	{"id": "sopa", "name": "Sopa de Cogumelos", "price": 26, "icon": "potion", "heal": 15, "mana": 0, "secs": 600.0, "label": "Sopa de Cogumelos",
		"eff": {"dodge": 6.0, "mspd": 6.0}, "desc": "Leve e aromática. +6% esquiva e +6% velocidade por 10 min."},
	{"id": "hidromel", "name": "Hidromel Dourado", "price": 40, "icon": "potion", "heal": 0, "mana": 0, "secs": 600.0, "label": "Hidromel Dourado",
		"eff": {"xp_pct": 20.0, "atk_pct": 4.0}, "desc": "A casa recomenda. +20% EXP e +4% ataque por 10 min."},
	{"id": "banquete", "name": "Banquete do Rei", "price": 120, "icon": "gear_charm", "heal": 100, "mana": 100, "secs": 900.0, "label": "Banquete do Rei",
		"eff": {"hp": 100.0, "atk_pct": 12.0, "mag_pct": 12.0, "xp_pct": 15.0, "regen": 1.0, "def": 5.0}, "desc": "Assado, queijos e vinho. Restaura tudo; +100 vida, +12% ataque/magia, +15% EXP, +1 mana/s e +5 defesa por 15 min."},
	{"id": "biscoito", "name": "Biscoito da Sorte", "price": 18, "icon": "coin", "heal": 10, "mana": 0, "secs": 600.0, "label": "Biscoito da Sorte",
		"eff": {"crit": 4.0, "dodge": 3.0}, "desc": "Crocante, com um bilhete dentro. +4% crítico e +3% esquiva por 10 min."},
]
const BAKERY_FOODS := ["pao_mel", "torta", "biscoito"]

var open := false
var hud: Hud
var root: Control
var page: Control
var close_button: Button
var fade: ColorRect
var fade_label: Label
var tab := 0                      # 0 = rooms, 1 = food
var inn := true
var sel := 0
var btns: Array = []
var _sleeping := false


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
	# full-screen fade used while sleeping
	fade = ColorRect.new()
	fade.color = Color(0, 0, 0, 0)
	fade.mouse_filter = Control.MOUSE_FILTER_IGNORE
	hud.ctl(hud.root, C, Vector2.ZERO, Hud.SIZE, fade)
	fade.visible = false
	fade.z_index = 200
	fade_label = hud.txt(fade, "", Util.font_serif, 54, Color(0.85, 0.88, 1.0), C, Vector2.ZERO, Vector2(1400, 120))


func foods() -> Array:
	var out: Array = []
	for f in FOODS:
		if inn and f["id"] != "biscoito":
			out.append(f)
		elif not inn and f["id"] in BAKERY_FOODS:
			out.append(f)
	return out


func open_for(kind: String, start_tab: int = 0) -> void:
	inn = kind == "inn"
	tab = start_tab if inn else 1
	sel = 0
	open = true
	root.visible = true
	get_tree().paused = true
	if Player.I != null:
		Player.I.input_locked = true
	Sfx.play("ui", 0.3, 0.8)
	_refresh()


func close() -> void:
	if not open or _sleeping:
		return
	open = false
	root.visible = false
	get_tree().paused = Game.in_menu or Game.grimoire.open or (Game.options != null and Game.options.open)
	if Player.I != null:
		Player.I.input_locked = get_tree().paused
	Game.save()
	Sfx.play("ui", 0.3, 0.8)


func _input(event: InputEvent) -> void:
	if not open or _sleeping:
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


func _list() -> Array:
	return ROOMS if tab == 0 else foods()


func _process(_dt: float) -> void:
	if not open or _sleeping:
		return
	if Game.consume(KEY_ESCAPE) or Game.consume(KEY_TAB):
		close()
		return
	var n := maxi(1, _list().size())
	if Game.consume(KEY_S) or Game.consume(KEY_DOWN):
		sel = (sel + 1) % n
		_refresh()
	if Game.consume(KEY_W) or Game.consume(KEY_UP):
		sel = (sel + n - 1) % n
		_refresh()
	if inn and (Game.consume(KEY_A) or Game.consume(KEY_D) or Game.consume(KEY_LEFT) or Game.consume(KEY_RIGHT) or Game.consume(KEY_Q)):
		_set_tab(1 - tab)
	if Game.consume(KEY_ENTER) or Game.consume(KEY_E):
		_confirm()


func _set_tab(t: int) -> void:
	tab = t
	sel = 0
	Sfx.play("ui", 0.2, 1.0)
	_refresh()


func _pick(i: int) -> void:
	sel = i
	Sfx.play("ui", 0.2, 1.0)
	_refresh()


func _confirm() -> void:
	if tab == 0:
		_rent(sel)
	else:
		_eat(sel)


func _eat(i: int) -> void:
	var gs := Game.state
	var f: Dictionary = foods()[i]
	if gs.gold < int(f["price"]):
		Sfx.play("ui", 0.2, 0.6)
		Fx.toast("Ouro insuficiente", Color(1.0, .66, .51))
		return
	gs.gold -= int(f["price"])
	var p := Player.I
	if int(f["heal"]) > 0:
		p.hp = minf(gs.hp_max(), p.hp + (gs.hp_max() * float(f["heal"]) / 100.0 if int(f["heal"]) >= 40 else float(f["heal"])))
	if int(f["mana"]) > 0:
		p.mp = minf(gs.max_mp, p.mp + gs.max_mp * float(f["mana"]) / 100.0)
	gs.add_buff("food", float(f["secs"]), f["eff"], str(f["label"]))
	p.max_hp = gs.hp_max()
	if str(f["id"]) == "banquete":
		p.hp = gs.hp_max()
		p.mp = gs.max_mp
	Sfx.play("potion", 0.6, 1.1)
	Sfx.play("coin", 0.4, 1.0)
	Fx.heal(p.pos())
	Fx.toast("Delicioso! %s" % f["name"], Color(1, 0.9, 0.5))
	_refresh()


func _rent(i: int) -> void:
	var gs := Game.state
	var r: Dictionary = ROOMS[i]
	if gs.gold < int(r["price"]):
		Sfx.play("ui", 0.2, 0.6)
		Fx.toast("Ouro insuficiente", Color(1.0, .66, .51))
		return
	gs.gold -= int(r["price"])
	_sleep(i)


func _sleep(i: int) -> void:
	_sleeping = true
	root.visible = false
	var gs := Game.state
	var r: Dictionary = ROOMS[i]
	fade.visible = true
	fade.color.a = 0.0
	fade_label.text = ""
	var tw := create_tween().set_pause_mode(Tween.TWEEN_PAUSE_PROCESS)
	tw.tween_property(fade, "color:a", 1.0, 0.9)
	await tw.finished
	fade_label.text = "Zzz..."
	Sfx.play("potion", 0.4, 0.7)
	await get_tree().create_timer(1.4, true, false, true).timeout
	# rest: full HP/MP, skip to the next morning, optional buff
	var p := Player.I
	var day := floorf(Game.clock / World.DAY_LENGTH)
	Game.clock = (day + 1.0) * World.DAY_LENGTH + 0.02 * World.DAY_LENGTH
	gs.buffs.erase("rest")
	if not (r["buff"] as Dictionary).is_empty():
		gs.add_buff("rest", float(r["secs"]), r["buff"], str(r["label"]))
	p.max_hp = gs.hp_max()
	p.hp = gs.hp_max()
	p.mp = gs.max_mp
	p.venom = 0.0
	p.hex_slow = 0.0
	fade_label.text = "Você acordou revigorado."
	Sfx.play("levelup", 0.5, 1.2)
	Game.save()
	await get_tree().create_timer(1.6, true, false, true).timeout
	var tw2 := create_tween().set_pause_mode(Tween.TWEEN_PAUSE_PROCESS)
	tw2.tween_property(fade, "color:a", 0.0, 0.9)
	await tw2.finished
	fade.visible = false
	fade_label.text = ""
	_sleeping = false
	Fx.heal(p.pos())
	Fx.toast("Vida e mana restauradas", Color(0.7, 1.0, 0.8), p.pos() + Vector2.UP * 2.0 * 64.0)
	open = true
	root.visible = true
	_refresh()


func _btn(parent: Control, label: String, pos: Vector2, size: Vector2, fn: Callable, fill: Color, fsize: int = 24) -> void:
	var b := Button.new()
	b.text = label
	b.focus_mode = Control.FOCUS_NONE
	b.process_mode = Node.PROCESS_MODE_ALWAYS
	hud.ctl(parent, Vector2(0.5, 0.5), pos, size, b)
	b.mouse_filter = Control.MOUSE_FILTER_STOP
	b.add_theme_font_override("font", Util.font_bold)
	b.add_theme_font_size_override("font_size", fsize)
	b.add_theme_color_override("font_color", Color(1.0, 0.93, 0.76))
	var st := StyleBoxFlat.new()
	st.bg_color = fill
	st.border_color = Color(0.87, 0.67, 0.37)
	st.set_border_width_all(2)
	st.set_corner_radius_all(12)
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
	var gold := Color(0.6, 0.42, 0.05)
	var serif := Util.font_serif
	var sans := Util.font_sans
	var bold := Util.font_bold
	var L := HORIZONTAL_ALIGNMENT_LEFT
	var M := HORIZONTAL_ALIGNMENT_CENTER
	var R := HORIZONTAL_ALIGNMENT_RIGHT
	var items: Array = _list()
	sel = clampi(sel, 0, maxi(0, items.size() - 1))
	hud.txt(page, "Taverna" if inn else "Padaria", serif, 40, ink, C, Vector2(-335, 322), Vector2(500, 52), M, false)
	if inn:
		_btn(page, "Quartos", Vector2(-450, 272), Vector2(190, 44), _set_tab.bind(0), Color(0.4, 0.2, 0.08, 0.95) if tab == 0 else Color(0.3, 0.25, 0.2, 0.6))
		_btn(page, "Comida", Vector2(-240, 272), Vector2(190, 44), _set_tab.bind(1), Color(0.4, 0.2, 0.08, 0.95) if tab == 1 else Color(0.3, 0.25, 0.2, 0.6))
	else:
		hud.txt(page, "Pães e doces com efeitos especiais", sans, 20, faint, C, Vector2(-335, 272), Vector2(540, 30), M, false)
	var top := 0
	if sel >= 7:
		top = sel - 6
	for r in mini(items.size() - top, 7):
		var i := top + r
		var y := 212.0 - r * 54.0
		var nm := ""
		var price := 0
		var icon := "gear_charm"
		if tab == 0:
			nm = str(items[i]["name"])
			price = int(items[i]["price"])
			icon = "potion"
		else:
			nm = str(items[i]["name"])
			price = int(items[i]["price"])
			icon = str(items[i]["icon"])
		if i == sel:
			hud.img(page, Sheets.ui("smear"), C, Vector2(-335, y), Vector2(560, 66)).modulate = Color(0.85, 0.6, 0.2, 0.35)
		hud.img(page, Sheets.icon(icon), C, Vector2(-560, y), Vector2(46, 46))
		hud.txt(page, nm, bold, 22, ink, C, Vector2(-345, y), Vector2(330, 34), L, false)
		hud.txt(page, "%d" % price, serif, 26, gold if gs.gold >= price else Color(0.7, 0.2, 0.15), C, Vector2(-130, y), Vector2(80, 34), R, false)
		_row_btn(page, Vector2(-335, y), Vector2(560, 52), _pick.bind(i))
	# right page
	hud.txt(page, "Ouro: %d" % gs.gold, serif, 36, gold, C, Vector2(335, 300), Vector2(500, 50), M, false)
	if items.is_empty():
		return
	var it: Dictionary = items[sel]
	hud.txt(page, str(it["name"]), bold, 30, ink, C, Vector2(335, 215), Vector2(540, 40), M, false)
	var det := hud.txt(page, str(it["desc"]), sans, 22, ink, C, Vector2(335, 80), Vector2(520, 200), M, false, VERTICAL_ALIGNMENT_TOP)
	hud.wrap(det, 520.0)
	if tab == 0:
		_btn(page, "Pagar %d e dormir" % int(it["price"]), Vector2(335, -250), Vector2(360, 60), _rent.bind(sel), Color(0.4, 0.2, 0.08, 0.95))
		hud.txt(page, "O jogo é salvo ao acordar.", sans, 18, faint, C, Vector2(335, -310), Vector2(400, 26), M, false)
	else:
		_btn(page, "Comprar e comer · %d" % int(it["price"]), Vector2(335, -250), Vector2(380, 60), _eat.bind(sel), Color(0.4, 0.2, 0.08, 0.95))
		var cur: Dictionary = gs.buffs.get("food", {})
		if not cur.is_empty():
			hud.txt(page, "Efeito atual: %s (%d s)" % [str(cur.get("label", "comida")), roundi(float(cur["t"]))], sans, 18, faint, C, Vector2(335, -312), Vector2(500, 26), M, false)
