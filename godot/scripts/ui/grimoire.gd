class_name Grimoire
extends Node
## Inventory / skills menu drawn as an open leather book (Tab). Pauses the game.

const SPARK_NAMES := ["", "Centelha", "Lança de Chamas", "Cometa Arcano"]
const SPARK_DESC := [
	"",
	"Uma faísca elétrica. Fraca, rápida, sua.",
	"A centelha vira fogo: dano maior e explosão.",
	"Magia arcana pura que atravessa demônios.",
]

var open := false
var hud: Hud
var root: Control
var page: Control
var close_button: Button
var sel := 0


func setup(h: Hud) -> void:
	process_mode = Node.PROCESS_MODE_ALWAYS
	hud = h
	var C := Vector2(0.5, 0.5)
	root = hud.ctl(hud.root, C, Vector2.ZERO, Hud.SIZE)
	var dim := hud.img(root, Util.soft_circle(), C, Vector2.ZERO, Vector2(2600, 1800))
	dim.modulate = Color(0.02, 0.01, 0.04, 0.75)
	hud.img(root, Sheets.ui("book"), C, Vector2.ZERO, Vector2(1400, 860))
	# Real clickable X: the leather-book texture previously had no close control.
	# Inherit ALWAYS processing from Hud so the button still works while paused.
	close_button = Button.new()
	close_button.name = "CloseGrimoire"
	close_button.text = "X"
	close_button.tooltip_text = "Fechar grimório (Esc ou Tab)"
	close_button.focus_mode = Control.FOCUS_NONE
	hud.ctl(root, C, Vector2(620, 354), Vector2(88, 88), close_button)
	close_button.mouse_filter = Control.MOUSE_FILTER_STOP
	close_button.process_mode = Node.PROCESS_MODE_ALWAYS
	close_button.add_theme_font_override("font", Util.font_serif)
	close_button.add_theme_font_size_override("font_size", 45)
	close_button.add_theme_color_override("font_color", Color(1.0, 0.93, 0.76))
	close_button.add_theme_color_override("font_hover_color", Color.WHITE)
	close_button.add_theme_color_override("font_pressed_color", Color(1.0, 0.86, 0.47))
	var normal := StyleBoxFlat.new()
	normal.bg_color = Color(0.32, 0.12, 0.1, 0.94)
	normal.border_color = Color(0.87, 0.67, 0.37)
	normal.set_border_width_all(3)
	normal.set_corner_radius_all(22)
	close_button.add_theme_stylebox_override("normal", normal)
	var hover := normal.duplicate() as StyleBoxFlat
	hover.bg_color = Color(0.49, 0.18, 0.12, 1.0)
	close_button.add_theme_stylebox_override("hover", hover)
	var pressed := normal.duplicate() as StyleBoxFlat
	pressed.bg_color = Color(0.2, 0.08, 0.07)
	close_button.add_theme_stylebox_override("pressed", pressed)
	close_button.pressed.connect(_on_close_pressed)
	root.visible = false


func toggle() -> void:
	open = not open
	root.visible = open
	# When closing, preserve any other modal/menu pause state.
	get_tree().paused = open or Game.in_menu or (Game.options != null and Game.options.open)
	if open:
		sel = 0
		_refresh()
	Sfx.play("ui", 0.3, 0.8)
	if Player.I != null:
		Player.I.input_locked = get_tree().paused


func _on_close_pressed() -> void:
	if open:
		toggle()


func _input(event: InputEvent) -> void:
	# Android has mouse emulation disabled. Handle touch directly as well as
	# the native Button.pressed signal used by mouse clicks.
	if not open or close_button == null:
		return
	if event is InputEventScreenTouch and event.pressed:
		if Game.ui_smoke:
			print("[ui-smoke] book touch position=", event.position, " X rect=", close_button.get_global_rect(), " open=", open)
		if close_button.get_global_rect().grow(10.0).has_point(event.position):
			_on_close_pressed()
			get_viewport().set_input_as_handled()


func _process(_dt: float) -> void:
	if not open:
		return
	var gs := Player.I.gs
	var n := gs.inv_ids.size()
	if Game.consume(KEY_TAB) or Game.consume(KEY_ESCAPE):
		toggle()
		return
	if n > 0 and (Game.consume(KEY_S) or Game.consume(KEY_DOWN)):
		sel = (sel + 1) % n
		_refresh()
	if n > 0 and (Game.consume(KEY_W) or Game.consume(KEY_UP)):
		sel = (sel + n - 1) % n
		_refresh()
	if n > 0 and (Game.consume(KEY_ENTER) or Game.consume(KEY_E)):
		_use(gs.inv_ids[sel])
		_refresh()


func _name(id: String) -> String:
	return "—" if id == "" else str(Data.items[id]["name"])


func _use(id: String) -> void:
	var p := Player.I
	var gs := p.gs
	var d: Dictionary = Data.items[id]
	if id == "sword_tome":
		if gs.sword_tier >= 2:
			Fx.toast("O Corte Crescente já foi aprendido", Color.WHITE)
			return
		gs.take(id)
		gs.sword_tier = 2
		Sfx.play("levelup", 0.6, 1.2)
		hud.banner("Corte Crescente", "O 3º golpe lança uma lâmina de energia")
		return
	if int(d["slot"]) > 0:
		gs.equip(id)
		Sfx.play("pickup", 0.5, 0.9)
		p.hp = minf(p.hp, gs.hp_max())
		return
	if id == "spark_tome":
		if gs.spark_tier >= 3:
			Fx.toast("A Centelha já está no máximo", Color.WHITE)
			return
		gs.take(id)
		gs.spark_tier += 1
		Sfx.play("levelup", 0.6, 1.1)
		hud.banner("A Centelha evoluiu", SPARK_NAMES[gs.spark_tier])
		return
	if not d["consumable"]:
		Sfx.play("ui", 0.2, 0.6)
		return
	var heal := float(d["heal"])
	var mana := float(d["mana"])
	if heal > 0 and p.hp >= gs.hp_max():
		return
	if mana > 0 and p.mp >= gs.max_mp:
		return
	gs.take(id)
	p.hp = minf(gs.hp_max(), p.hp + (maxf(heal, 0.35 * gs.hp_max()) if heal > 0 else 0.0))
	p.mp = minf(gs.max_mp, p.mp + (maxf(mana, 0.4 * gs.max_mp) if mana > 0 else 0.0))
	Sfx.play("potion", 0.5, 1.0)


func _refresh() -> void:
	if page:
		page.queue_free()
	var C := Vector2(0.5, 0.5)
	page = hud.ctl(root, C, Vector2.ZERO, Vector2(1400, 860))
	var gs := Player.I.gs
	var p := Player.I
	var ink := Color(0.27, 0.16, 0.1)
	var faint := Color(0.45, 0.32, 0.2)
	var serif := Util.font_serif
	var sans := Util.font_sans
	var bold := Util.font_bold
	var L := HORIZONTAL_ALIGNMENT_LEFT
	var M := HORIZONTAL_ALIGNMENT_CENTER
	var R := HORIZONTAL_ALIGNMENT_RIGHT

	# ---- left page: the hero
	hud.txt(page, "Ren Takamura", serif, 44, ink, C, Vector2(-335, 300), Vector2(500, 60), M, false)
	hud.txt(page, "Nível %d  ·  Aventureiro Rank %s" % [gs.level, gs.guild_rank], sans, 26, faint, C, Vector2(-335, 236), Vector2(500, 40), M, false)
	hud.img(page, Sheets.ui("portrait"), C, Vector2(-535, 150), Vector2(110, 110))
	hud.img(page, Sheets.ui("medallion"), C, Vector2(-535, 150), Vector2(170, 170))
	var stats := "Vida          %d / %d\n" % [ceili(p.hp), roundi(gs.hp_max())]
	stats += "Mana          %d / %d\n" % [floori(p.mp), roundi(gs.max_mp)]
	stats += "Ataque        %d   Defesa  %d\n" % [roundi(gs.total_atk()), roundi(gs.total_def())]
	stats += "Magia          %d\n" % roundi(gs.total_mag())
	stats += "Experiência  %d / %d\n" % [gs.xp, Data.xp_to_next(gs.level)]
	stats += "Ouro            %d\n" % gs.gold
	stats += "Arma: %s\nArmadura: %s\nAmuleto: %s" % [_name(gs.eq_weapon), _name(gs.eq_armor), _name(gs.eq_charm)]
	hud.txt(page, stats, bold, 22, ink, C, Vector2(-250, 62), Vector2(360, 320), L, false)
	hud.img(page, Sheets.ui("flourish"), C, Vector2(-335, -60), Vector2(380, 30))
	hud.txt(page, "Grimório de Magias", serif, 30, ink, C, Vector2(-335, -100), Vector2(500, 40), M, false)
	var tints := [Color(0.6, 0.85, 1.0), Color(1.0, 0.6, 0.3), Color(0.8, 0.55, 1.0)]
	for t in range(1, 4):
		var have: bool = gs.spark_tier >= t
		var y := -150.0 - (t - 1) * 62.0
		var ic := hud.img(page, Sheets.icon("skill_spark"), C, Vector2(-560, y), Vector2(52, 52))
		ic.modulate = tints[t - 1] if have else Color(0.3, 0.25, 0.2, 0.5)
		hud.txt(page, SPARK_NAMES[t] + ("  ◆" if gs.spark_tier == t else ""), bold, 26, ink if have else faint, C, Vector2(-300, y + 12), Vector2(440, 30), L, false)
		hud.txt(page, SPARK_DESC[t] if have else "Requer um Tomo da Centelha", sans, 21, faint, C, Vector2(-300, y - 14), Vector2(440, 26), L, false)

	# ---- right page: the bag
	hud.txt(page, "Bolsa", serif, 44, ink, C, Vector2(335, 300), Vector2(500, 60), M, false)
	if gs.inv_ids.is_empty():
		hud.txt(page, "Vazia. Os demônios carregam coisas valiosas...", sans, 24, faint, C, Vector2(335, 150), Vector2(500, 40), M, false)
	sel = clampi(sel, 0, maxi(0, gs.inv_ids.size() - 1))
	for i in mini(gs.inv_ids.size(), 9):
		var d: Dictionary = Data.items[gs.inv_ids[i]]
		var y := 220.0 - i * 56.0
		if i == sel:
			hud.img(page, Sheets.ui("smear"), C, Vector2(335, y), Vector2(560, 70)).modulate = Color(0.85, 0.6, 0.2, 0.35)
			hud.txt(page, "◆", serif, 22, Color(0.75, 0.5, 0.15), C, Vector2(100, y), Vector2(30, 30), M, false)
		hud.img(page, Sheets.icon(d["icon"]), C, Vector2(150, y), Vector2(48, 48))
		var rc: Color = Data.RARITY_COLORS[int(d["rarity"])]
		var name_col := ink if int(d["rarity"]) == 0 else rc.lerp(ink, 0.45)
		hud.txt(page, d["name"], bold, 27, name_col, C, Vector2(370, y), Vector2(380, 34), L, false)
		hud.txt(page, "×%d" % int(gs.inv_counts[i]), serif, 26, faint, C, Vector2(590, y), Vector2(80, 34), R, false)
	if not gs.inv_ids.is_empty():
		var d: Dictionary = Data.items[gs.inv_ids[sel]]
		hud.img(page, Sheets.ui("flourish"), C, Vector2(335, -250), Vector2(380, 30))
		var stat := ""
		if int(d["slot"]) > 0:
			stat = "\n"
			if float(d["atk"]) > 0: stat += "ATQ +%d  " % roundi(d["atk"])
			if float(d["defense"]) > 0: stat += "DEF +%d  " % roundi(d["defense"])
			if float(d["mag"]) > 0: stat += "MAG +%d  " % roundi(d["mag"])
			if float(d["hp"]) > 0: stat += "PV +%d  " % roundi(d["hp"])
			stat += "· Enter: equipar"
		var desc := hud.txt(page, str(d["desc"]) + stat, sans, 22, ink, C, Vector2(335, -292), Vector2(520, 60), M, false, VERTICAL_ALIGNMENT_TOP)
		desc.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	hud.txt(page, "W/S escolher  ·  Enter usar  ·  Tab fechar", sans, 21, faint, C, Vector2(335, -340), Vector2(560, 30), M, false)
	# The information page is rebuilt after item use; keep X above it.
	root.move_child(close_button, root.get_child_count() - 1)
