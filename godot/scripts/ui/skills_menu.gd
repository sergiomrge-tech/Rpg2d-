class_name SkillsMenu
extends Node
## Attributes + class skill tree drawn on the leather book (P). Pauses the game.

var open := false
var hud: Hud
var root: Control
var page: Control
var close_button: Button
var btns: Array = []
var asel := 0                       # selected attribute row (keyboard)
var sel_b := 0
var sel_t := 0

const NODE := 58.0
const COL_X := [-170.0, 0.0, 170.0]
const ROW_Y := [166.0, 74.0, -16.0, -104.0]


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


func toggle() -> void:
	if open:
		close()
		return
	open = true
	root.visible = true
	get_tree().paused = true
	if Player.I != null:
		Player.I.input_locked = true
	asel = 0
	sel_b = 0
	sel_t = 0
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
	if Game.consume(KEY_ESCAPE) or Game.consume(KEY_TAB) or Game.consume(KEY_P):
		close()
		return
	var n := SkillTree.ATTRS.size()
	if Game.consume(KEY_S) or Game.consume(KEY_DOWN):
		asel = (asel + 1) % n
		_refresh()
	if Game.consume(KEY_W) or Game.consume(KEY_UP):
		asel = (asel + n - 1) % n
		_refresh()
	if Game.consume(KEY_ENTER) or Game.consume(KEY_E):
		_add(SkillTree.ATTRS[asel])
	if Game.consume(KEY_D) or Game.consume(KEY_RIGHT):
		sel_b = (sel_b + 1) % 3
		_refresh()
	if Game.consume(KEY_A) or Game.consume(KEY_LEFT):
		sel_b = (sel_b + 2) % 3
		_refresh()


func _add(a: String) -> void:
	var gs := Game.state
	if gs.add_attr(a):
		Sfx.play("pickup", 0.5, 1.1)
		_apply()
	else:
		Sfx.play("ui", 0.2, 0.6)
		Fx.toast("Sem pontos de atributo", Color(1.0, .66, .51))
	_refresh()


func _apply() -> void:
	var p := Player.I
	if p != null:
		p.max_hp = Game.state.hp_max()
		p.hp = minf(p.hp, Game.state.hp_max())


func _select(b: int, t: int) -> void:
	sel_b = b
	sel_t = t
	Sfx.play("ui", 0.2, 1.0)
	_refresh()


func _learn() -> void:
	var gs := Game.state
	var why := gs.skill_block(sel_b, sel_t)
	if why != "":
		Sfx.play("ui", 0.2, 0.6)
		Fx.toast(why, Color(1.0, .66, .51))
		return
	gs.learn_skill(sel_b, sel_t)
	Sfx.play("levelup", 0.6, 1.1)
	var n := SkillTree.node(gs.class_id, sel_b, sel_t)
	Fx.toast("Aprendeu: " + str(n[0]), Color(1, 0.9, 0.5))
	_apply()
	_refresh()


func _reset() -> void:
	var gs := Game.state
	if gs.respec():
		Sfx.play("potion", 0.5, 0.9)
		Fx.toast("Pontos redistribuídos", Color(1, 0.95, 0.8))
		_apply()
	else:
		Sfx.play("ui", 0.2, 0.6)
		Fx.toast("Precisa de %d ouro" % gs.respec_cost(), Color(1.0, .66, .51))
	_refresh()


func _btn(parent: Control, label: String, pos: Vector2, size: Vector2, fn: Callable, fill: Color, fsize: int = 24) -> Button:
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
	return b


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

	# ---------------------------------------------------------------- left page: attributes
	hud.txt(page, "Atributos", serif, 44, ink, C, Vector2(-335, 300), Vector2(500, 60), M, false)
	hud.txt(page, "Pontos disponíveis: %d" % gs.attr_pts, bold, 26, gold if gs.attr_pts > 0 else faint, C, Vector2(-335, 252), Vector2(500, 36), M, false)
	for i in SkillTree.ATTRS.size():
		var a: String = SkillTree.ATTRS[i]
		var y := 192.0 - i * 58.0
		if i == asel:
			hud.img(page, Sheets.ui("smear"), C, Vector2(-335, y), Vector2(560, 60)).modulate = Color(0.85, 0.6, 0.2, 0.3)
		hud.txt(page, "%s" % SkillTree.ATTR_NAMES[a], bold, 25, ink, C, Vector2(-445, y + 9), Vector2(240, 30), L, false)
		hud.txt(page, SkillTree.ATTR_DESC[a], sans, 15, faint, C, Vector2(-420, y - 15), Vector2(260, 20), L, false)
		var inv := gs.attr_inv(a)
		hud.txt(page, "%d" % gs.attr(a), serif, 32, ink, C, Vector2(-215, y), Vector2(70, 40), M, false)
		if inv > 0:
			hud.txt(page, "+%d" % inv, bold, 19, Color(0.25, 0.5, 0.2), C, Vector2(-165, y - 2), Vector2(50, 24), L, false)
		var plus := _btn(page, "+", Vector2(-78, y), Vector2(56, 46), _add.bind(a), Color(0.4, 0.2, 0.08, 0.95) if gs.attr_pts > 0 else Color(0.3, 0.25, 0.2, 0.6), 32)
		plus.disabled = false
	var sum := "Ataque %d · Magia %d · Defesa %d\nVida %d · Mana %d · Regen. %.1f/s\n" % [roundi(gs.total_atk()), roundi(gs.total_mag()), roundi(gs.total_def()), roundi(gs.hp_max()), roundi(gs.max_mp), gs.mp_regen()]
	sum += "Esquiva %d%% · Crítico %d%% · Vel. ataque +%d%%" % [roundi(gs.dodge_chance() * 100.0), roundi(gs.crit_chance() * 100.0), roundi((gs.attack_speed() - 1.0) * 100.0)]
	var sm := hud.txt(page, sum, sans, 16, ink, C, Vector2(-335, -178), Vector2(560, 90), M, false)
	hud.wrap(sm, 560.0)
	var pas := hud.txt(page, "Passiva da classe: " + SkillTree.passive_text(gs.class_id, gs.level), bold, 15, Color(0.3, 0.5, 0.2), C, Vector2(-335, -246), Vector2(560, 44), M, false)
	hud.wrap(pas, 560.0)
	var cost := gs.respec_cost()
	_btn(page, "Redefinir tudo · %d ouro" % cost, Vector2(-335, -298), Vector2(360, 46), _reset, Color(0.4, 0.14, 0.1, 0.95) if gs.gold >= cost else Color(0.3, 0.25, 0.2, 0.7), 20)

	# ---------------------------------------------------------------- right page: skill tree
	var cname: String = str(HeroClasses.info(gs.class_id)["name"])
	hud.txt(page, "Árvore do %s" % cname, serif, 36, ink, C, Vector2(335, 310), Vector2(540, 50), M, false)
	hud.txt(page, "Pontos de habilidade: %d" % gs.skill_pts, bold, 24, gold if gs.skill_pts > 0 else faint, C, Vector2(335, 272), Vector2(500, 32), M, false)
	var branches := SkillTree.branches(gs.class_id)
	for b in 3:
		var cx: float = 335.0 + COL_X[b]
		hud.txt(page, str(branches[b]["name"]), bold, 21, ink, C, Vector2(cx, 232), Vector2(160, 26), M, false)
		for t in 4:
			var cy: float = ROW_Y[t]
			if t < 3:     # link to the next tier
				var ln := ColorRect.new()
				ln.color = Color(0.7, 0.5, 0.15) if gs.skill_known(b, t) else Color(0.45, 0.35, 0.25, 0.5)
				hud.ctl(page, C, Vector2(cx, cy - 41.0), Vector2(5, 26), ln)
			_node_view(page, b, t, Vector2(cx, cy), gs, bold, ink)
	# details of the selected node
	var nd := SkillTree.node(gs.class_id, sel_b, sel_t)
	hud.txt(page, "%s — nível %d" % [nd[0], int(SkillTree.TIER_LEVELS[sel_t])], bold, 24, ink, C, Vector2(335, -178), Vector2(540, 32), M, false)
	var det := hud.txt(page, SkillTree.node_text(gs.class_id, sel_b, sel_t), sans, 17, ink, C, Vector2(335, -224), Vector2(560, 60), M, false, VERTICAL_ALIGNMENT_TOP)
	hud.wrap(det, 560.0)
	var why := gs.skill_block(sel_b, sel_t)
	if gs.skill_known(sel_b, sel_t):
		hud.txt(page, "✔ Aprendida", bold, 24, Color(0.25, 0.5, 0.2), C, Vector2(335, -290), Vector2(300, 40), M, false)
	elif why == "":
		_btn(page, "Aprender · %d pt" % int(SkillTree.TIER_COST[sel_t]), Vector2(335, -290), Vector2(300, 50), _learn, Color(0.4, 0.2, 0.08, 0.95))
	else:
		hud.txt(page, why, bold, 21, Color(0.7, 0.2, 0.15), C, Vector2(335, -290), Vector2(520, 40), M, false)


func _node_view(parent: Control, b: int, t: int, pos: Vector2, gs: GameState, bold: Font, ink: Color) -> void:
	var C := Vector2(0.5, 0.5)
	var known := gs.skill_known(b, t)
	var why := gs.skill_block(b, t)
	var lvl_locked := gs.level < int(SkillTree.TIER_LEVELS[t])
	var col := Color(0.35, 0.3, 0.28)
	var bg := Color(0.2, 0.15, 0.12, 0.35)
	if known:
		col = Color(1.0, 0.78, 0.25)
		bg = Color(0.5, 0.33, 0.08, 0.85)
	elif why == "":
		col = Color(0.35, 0.8, 0.3)
		bg = Color(0.15, 0.3, 0.12, 0.6)
	elif not lvl_locked:
		col = Color(0.55, 0.45, 0.3)
	var panel := Panel.new()
	panel.mouse_filter = Control.MOUSE_FILTER_IGNORE
	var sb := StyleBoxFlat.new()
	sb.bg_color = bg
	sb.border_color = col
	sb.set_border_width_all(5 if (b == sel_b and t == sel_t) else 3)
	sb.set_corner_radius_all(14)
	if b == sel_b and t == sel_t:
		sb.border_color = col.lightened(0.35)
	panel.add_theme_stylebox_override("panel", sb)
	hud.ctl(parent, C, pos, Vector2(NODE, NODE), panel)
	var br: Dictionary = SkillTree.branches(gs.class_id)[b]
	var ic := hud.img(parent, Sheets.icon(br["icon"]), C, pos, Vector2(34, 34))
	ic.modulate = Color(1, 1, 1, 1) if (known or why == "") else Color(0.6, 0.6, 0.6, 0.55)
	var n := SkillTree.node(gs.class_id, b, t)
	if (n[1] as Dictionary).has("unlock"):
		hud.txt(parent, str(n[1]["unlock"]).to_upper(), bold, 17, Color(1, 0.95, 0.6) if known else Color(1, 0.85, 0.4), C, pos + Vector2(19, 19), Vector2(24, 20), HORIZONTAL_ALIGNMENT_CENTER, true)
	var nm := str(n[0])
	hud.txt(parent, nm, bold, 14, ink if (known or why == "") else Color(0.45, 0.35, 0.28), C, pos + Vector2(0, -43), Vector2(166, 18), HORIZONTAL_ALIGNMENT_CENTER, false)
	if lvl_locked:
		hud.txt(parent, "Nv %d" % int(SkillTree.TIER_LEVELS[t]), bold, 14, Color(0.7, 0.25, 0.2), C, pos + Vector2(-19, 19), Vector2(40, 18), HORIZONTAL_ALIGNMENT_CENTER, false)
	_flat(parent, pos, Vector2(NODE + 10, NODE + 28), _select.bind(b, t))
