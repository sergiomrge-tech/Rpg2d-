class_name GuildBoard
extends Node
## Guild daily board drawn on the leather book (opens after talking to a guild receptionist / guildmaster).

var open := false
var hud: Hud
var root: Control
var page: Control
var close_button: Button
var sel := 0
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


func open_board() -> void:
	DailyBoard.refresh()
	sel = 0
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
	Game.save()
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
	if Game.consume(KEY_S) or Game.consume(KEY_DOWN):
		sel = (sel + 1) % 3
		_refresh()
	if Game.consume(KEY_W) or Game.consume(KEY_UP):
		sel = (sel + 2) % 3
		_refresh()
	if Game.consume(KEY_ENTER) or Game.consume(KEY_E):
		_act(sel)


func _act(i: int) -> void:
	var q: Dictionary = Game.daily["quests"][i]
	match int(q["state"]):
		0:
			DailyBoard.accept(i)
			Sfx.play("pickup", 0.5, 1.1)
			Fx.toast("Missão aceita", Color(1, 0.9, 0.5))
		1:
			if DailyBoard.claim(i):
				Sfx.play("coin", 0.6, 1.0)
				Sfx.play("levelup", 0.4, 1.2)
				Fx.toast("Recompensa recebida!", Color(1, 0.9, 0.5))
			else:
				Sfx.play("ui", 0.2, 0.6)
				Fx.toast("Missão ainda não cumprida", Color(1.0, .66, .51))
	_refresh()


func _bonus() -> void:
	if DailyBoard.claim_bonus():
		Sfx.play("legend", 0.5, 1.0)
		Fx.toast("Bônus diário recebido!", Color(1, 0.9, 0.5))
	else:
		Sfx.play("ui", 0.2, 0.6)
		Fx.toast("Cumpra as 3 missões do dia", Color(1.0, .66, .51))
	_refresh()


func _select(i: int) -> void:
	sel = i
	Sfx.play("ui", 0.2, 1.0)
	_refresh()


func _btn(parent: Control, label: String, pos: Vector2, size: Vector2, fn: Callable, fill: Color, fsize: int = 22) -> void:
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


func _flat(parent: Control, pos: Vector2, size: Vector2, fn: Callable) -> void:
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
	var ink := Color(0.27, 0.16, 0.1)
	var faint := Color(0.45, 0.32, 0.2)
	var gold := Color(0.6, 0.42, 0.05)
	var serif := Util.font_serif
	var sans := Util.font_sans
	var bold := Util.font_bold
	var L := HORIZONTAL_ALIGNMENT_LEFT
	var M := HORIZONTAL_ALIGNMENT_CENTER
	var R := HORIZONTAL_ALIGNMENT_RIGHT
	var left := DailyBoard.seconds_left()
	hud.txt(page, "Quadro da Guilda", serif, 40, ink, C, Vector2(-335, 318), Vector2(540, 56), M, false)
	hud.txt(page, "Missões do dia · renovam em %dh %02dmin" % [left / 3600, (left % 3600) / 60], sans, 18, faint, C, Vector2(-335, 276), Vector2(540, 28), M, false)
	var quests: Array = Game.daily["quests"]
	for i in quests.size():
		var q: Dictionary = quests[i]
		var y := 178.0 - i * 148.0
		var panel := Panel.new()
		panel.mouse_filter = Control.MOUSE_FILTER_IGNORE
		var sb := StyleBoxFlat.new()
		var st := int(q["state"])
		sb.bg_color = Color(0.4, 0.28, 0.12, 0.16 if st != 3 else 0.28)
		sb.border_color = Color(0.85, 0.6, 0.2) if i == sel else Color(0.55, 0.4, 0.22, 0.6)
		sb.set_border_width_all(4 if i == sel else 2)
		sb.set_corner_radius_all(14)
		panel.add_theme_stylebox_override("panel", sb)
		hud.ctl(page, C, Vector2(-335, y), Vector2(560, 136), panel)
		hud.txt(page, DailyBoard.title(q), bold, 23, ink if st != 3 else faint, C, Vector2(-355, y + 42), Vector2(500, 30), L, false)
		var ht := hud.txt(page, DailyBoard.hint(q), sans, 15, faint, C, Vector2(-355, y + 16), Vector2(510, 24), L, false)
		ht.clip_text = true
		hud.txt(page, DailyBoard.reward_text(q), bold, 17, gold, C, Vector2(-355, y - 10), Vector2(510, 26), L, false)
		var pr := DailyBoard.progress(q)
		var frac := clampf(float(pr) / float(q["need"]), 0.0, 1.0)
		var bar_bg := ColorRect.new()
		bar_bg.color = Color(0.3, 0.2, 0.1, 0.25)
		hud.ctl(page, C, Vector2(-450, y - 46), Vector2(220, 12), bar_bg)
		var bar := ColorRect.new()
		bar.color = Color(0.3, 0.65, 0.25) if frac >= 1.0 else Color(0.85, 0.6, 0.2)
		hud.ctl(page, C, Vector2(-560 + 110.0 * frac, y - 46), Vector2(maxf(2.0, 220.0 * frac), 12), bar)
		hud.txt(page, "%d/%d" % [pr, int(q["need"])], bold, 17, ink, C, Vector2(-300, y - 46), Vector2(70, 22), L, false)
		match st:
			0:
				_btn(page, "Aceitar", Vector2(-170, y - 40), Vector2(170, 44), _act.bind(i), Color(0.4, 0.2, 0.08, 0.95))
			1:
				if DailyBoard.ready(q):
					_btn(page, "Entregar", Vector2(-170, y - 40), Vector2(170, 44), _act.bind(i), Color(0.2, 0.45, 0.15, 0.95))
				else:
					hud.txt(page, "Em andamento", bold, 18, faint, C, Vector2(-170, y - 40), Vector2(170, 30), M, false)
			_:
				hud.txt(page, "✔ Concluída", bold, 19, Color(0.25, 0.5, 0.2), C, Vector2(-170, y - 40), Vector2(170, 30), M, false)
		_flat(page, Vector2(-400, y + 20), Vector2(320, 70), _select.bind(i))

	# ---- right page: daily bonus
	var done := DailyBoard.done_count()
	hud.txt(page, "Bônus diário", serif, 40, ink, C, Vector2(335, 318), Vector2(540, 56), M, false)
	hud.txt(page, "%d / 3" % done, serif, 80, gold if done >= 3 else faint, C, Vector2(335, 205), Vector2(400, 110), M, false)
	var tx := hud.txt(page, "Cumpra as três missões do quadro e receba um equipamento Raro ou melhor, mais ouro extra.\n\nO quadro troca todo dia — volte amanhã para novas missões.", sans, 20, ink, C, Vector2(335, -45), Vector2(500, 190), M, false, VERTICAL_ALIGNMENT_TOP)
	tx.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	if Game.daily.get("bonus", false):
		hud.txt(page, "✔ Bônus recebido hoje", bold, 24, Color(0.25, 0.5, 0.2), C, Vector2(335, -150), Vector2(420, 40), M, false)
	else:
		_btn(page, "Receber bônus", Vector2(335, -150), Vector2(300, 56), _bonus, Color(0.4, 0.2, 0.08, 0.95) if done >= 3 else Color(0.3, 0.25, 0.2, 0.7), 24)
	hud.txt(page, "Ouro: %d" % Game.state.gold, serif, 30, gold, C, Vector2(335, -250), Vector2(400, 40), M, false)
