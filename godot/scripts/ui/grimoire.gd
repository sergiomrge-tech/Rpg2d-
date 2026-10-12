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
var top := 0                       # first visible bag row
const ROWS := 7
var btns: Array = []              # [Button, Callable] rebuilt on every refresh (touch + mouse)


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
		top = 0
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
		for b in btns:
			if is_instance_valid(b[0]) and b[0].get_global_rect().has_point(event.position):
				get_viewport().set_input_as_handled()
				b[1].call()
				return
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
	for k in 3:
		if Game.consume([KEY_1, KEY_2, KEY_3][k]):
			_unequip(k + 1)
	if n > 0 and Game.consume(KEY_Q):
		_sell(gs.inv_ids[sel])
		_refresh()


func sell_price(id: String) -> int:
	var d: Dictionary = Data.items[id]
	if id == "rusty_sword" or id.ends_with("_tome") or float(d.get("value", 0)) <= 0:
		return 0
	return maxi(1, roundi(float(d["value"]) * 0.5))


func _sell(id: String) -> void:
	var gs := Player.I.gs
	var price := sell_price(id)
	if price <= 0:
		Sfx.play("ui", 0.2, 0.6)
		Fx.toast("Este item não pode ser vendido", Color(1.0, .66, .51))
		return
	gs.take(id)
	gs.gold += price
	Sfx.play("coin", 0.6, 1.0)
	Fx.toast("+%d ouro" % price, Color(1, 0.9, 0.5))


func _btn(parent: Control, label: String, pos: Vector2, size: Vector2, fn: Callable, fill: Color, fsize := 24) -> void:
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


## Equipment slot on the hero page: shows the worn piece (rarity-coloured frame); tap / press 1-3 to take it off.
func _slot(parent: Control, pos: Vector2, slot: int, label: String) -> void:
	var gs := Player.I.gs
	var id := gs.equipped(slot)
	var C := Vector2(0.5, 0.5)
	var col := Color(0.55, 0.4, 0.22)
	var panel := Panel.new()
	panel.mouse_filter = Control.MOUSE_FILTER_IGNORE
	var sb := StyleBoxFlat.new()
	sb.bg_color = Color(0.22, 0.14, 0.09, 0.28)
	sb.set_corner_radius_all(12)
	sb.set_border_width_all(4)
	if id != "":
		col = Data.RARITY_COLORS[int(Data.items[id]["rarity"])]
		sb.bg_color = col.darkened(0.55)
		sb.bg_color.a = 0.55
	sb.border_color = col
	panel.add_theme_stylebox_override("panel", sb)
	hud.ctl(parent, C, pos, Vector2(112, 92), panel)
	hud.txt(parent, label, Util.font_bold, 15, Color(0.45, 0.32, 0.2), C, pos + Vector2(0, 54), Vector2(130, 20), HORIZONTAL_ALIGNMENT_CENTER, false)
	if id != "":
		hud.img(parent, Sheets.icon(Data.items[id]["icon"]), C, pos + Vector2(0, 2), Vector2(62, 62))
		var nm := hud.txt(parent, str(Data.items[id]["name"]) + (" +%d" % gs.enh_level(id) if gs.enh_level(id) > 0 else ""), Util.font_bold, 14, col.lerp(Color(0.27, 0.16, 0.1), 0.5), C, pos + Vector2(0, -60), Vector2(150, 34), HORIZONTAL_ALIGNMENT_CENTER, false)
		nm.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
		_row_btn(parent, pos, Vector2(112, 92), _unequip.bind(slot))
	else:
		hud.txt(parent, "—", Util.font_serif, 40, Color(0.45, 0.32, 0.2, 0.6), C, pos, Vector2(60, 50), HORIZONTAL_ALIGNMENT_CENTER, false)


func _forge_btn(parent: Control, pos: Vector2, slot: int) -> void:
	var gs := Player.I.gs
	var id := gs.equipped(slot)
	if id == "":
		return
	var lv := gs.enh_level(id)
	var c := gs.forge_cost(id)
	var label := "MÁX +%d" % lv if c.is_empty() else "Forjar +%d · %dg" % [lv + 1, int(c["gold"])]
	var fill := Color(0.3, 0.25, 0.12, 0.9) if c.is_empty() else (Color(0.45, 0.25, 0.08, 0.95) if gs.can_forge(id) else Color(0.3, 0.2, 0.18, 0.8))
	if not c.is_empty():
		_btn(parent, label, pos, Vector2(124, 32), _forge.bind(slot), fill, 16)
	else:
		hud.txt(parent, label, Util.font_bold, 17, Color(0.7, 0.5, 0.1), Vector2(0.5, 0.5), pos, Vector2(124, 30), HORIZONTAL_ALIGNMENT_CENTER, false)


func _blacksmith_near() -> bool:
	var p := Player.I
	for n in Game.world.entities.get_children():
		if n is Npc and (n.id == "blacksmith" or n.id == "smith_v") and n.visible and (n.global_position - p.global_position).length() < 7.0 * 64.0:
			return true
	return false


func _forge(slot: int) -> void:
	var gs := Player.I.gs
	var id := gs.equipped(slot)
	if id == "":
		return
	if not _blacksmith_near():
		Sfx.play("ui", 0.2, 0.6)
		Fx.toast("Procure um ferreiro para forjar — marcado na bússola", Color(1.0, .66, .51))
		Game.smith_hint()
		return
	var c := gs.forge_cost(id)
	if not gs.can_forge(id):
		Sfx.play("ui", 0.2, 0.6)
		var need := "%d ouro" % int(c["gold"])
		if int(c["ember"]) > 0:
			need += " e %d Brasa Infernal" % int(c["ember"])
		Fx.toast("Precisa de " + need, Color(1.0, .66, .51))
		return
	gs.forge(id)
	Sfx.play("clang", 0.7, 1.0)
	Sfx.play("levelup", 0.4, 1.3)
	Fx.toast("%s +%d" % [Data.items[id]["name"], gs.enh_level(id)], Color(1, 0.85, 0.4))
	Player.I.hp = minf(Player.I.hp, gs.hp_max())
	_refresh()


func _unequip(slot: int) -> void:
	var gs := Player.I.gs
	var id := gs.equipped(slot)
	if gs.unequip(slot):
		Sfx.play("pickup", 0.5, 0.8)
		Fx.toast("%s guardado na bolsa" % Data.items[id]["name"], Color(1, 0.95, 0.8))
		Player.I.hp = minf(Player.I.hp, gs.hp_max())
		_refresh()


func _pick(i: int) -> void:
	sel = i
	Sfx.play("ui", 0.2, 1.0)
	_refresh()


func _act_use() -> void:
	var gs := Player.I.gs
	if not gs.inv_ids.is_empty():
		_use(gs.inv_ids[sel])
		_refresh()


func _act_sell() -> void:
	var gs := Player.I.gs
	if not gs.inv_ids.is_empty():
		_sell(gs.inv_ids[sel])
		_refresh()


func _name(id: String) -> String:
	return "—" if id == "" else str(Data.items[id]["name"])


func _use(id: String) -> void:
	var p := Player.I
	var gs := p.gs
	var d: Dictionary = Data.items[id]
	if id == "sword_tome":
		if gs.class_id != "warrior" and gs.class_id != "paladin":
			Fx.toast("Apenas espadachins dominam este tomo", Color(1.0, .66, .51))
			return
		if gs.sword_tier >= 2:
			Fx.toast("O Corte Crescente já foi aprendido", Color.WHITE)
			return
		gs.take(id)
		gs.sword_tier = 2
		Sfx.play("levelup", 0.6, 1.2)
		hud.banner("Corte Crescente", "O 3º golpe lança uma lâmina de energia")
		return
	if int(d["slot"]) > 0:
		if not gs.equip(id):
			Fx.toast("Equipamento incompatível com sua classe!", Color(1.0, 0.65, 0.52))
			return
		Sfx.play("pickup", 0.5, 0.9)
		p.hp = minf(p.hp, gs.hp_max())
		return
	if id == "spark_tome":
		if gs.class_id != "mage":
			Fx.toast("Apenas magos aprendem esta magia", Color(1.0, .66, .51))
			return
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
	hud.txt(page, "Nível %d  ·  %s  ·  Rank %s" % [gs.level, HeroClasses.info(gs.class_id)["name"], gs.guild_rank], sans, 26, faint, C, Vector2(-335, 236), Vector2(500, 40), M, false)
	hud.img(page, Sheets.ui("portrait"), C, Vector2(-535, 150), Vector2(110, 110))
	hud.img(page, Sheets.ui("medallion"), C, Vector2(-535, 150), Vector2(170, 170))
	var stats := "Vida %d/%d   Mana %d/%d\n" % [ceili(p.hp), roundi(gs.hp_max()), floori(p.mp), roundi(gs.max_mp)]
	stats += "Ataque %d  Defesa %d  Magia %d\n" % [roundi(gs.total_atk()), roundi(gs.total_def()), roundi(gs.total_mag())]
	stats += "XP %d/%d   Ouro %d" % [gs.xp, Data.xp_to_next(gs.level), gs.gold]
	if gs.ng_plus > 0:
		stats += "   NJ+%d" % gs.ng_plus
	hud.txt(page, stats, bold, 22, ink, C, Vector2(-250, 150), Vector2(380, 130), L, false)
	var slot_names := ["ARMA", "ARMADURA", "AMULETO"]
	for k in 3:
		_slot(page, Vector2(-470 + k * 135, 20), k + 1, slot_names[k])
		_forge_btn(page, Vector2(-470 + k * 135, -58), k + 1)
	var sbn := gs.set_bonus()
	if int(sbn["count"]) >= 2:
		var parts := PackedStringArray()
		for key in sbn["stats"]:
			parts.append("%s +%d" % [{"hp": "PV", "atk": "ATQ", "mag": "MAG", "defense": "DEF"}[key], roundi(sbn["stats"][key])])
		var set_txt := "Conjunto %s (%d/3): %s" % [sbn["name"], sbn["count"], ", ".join(parts)]
		if gs.set_power() != "":
			set_txt += "\nPoder: " + str(GameState.SET_POWER_TEXT[gs.set_power()])
		hud.txt(page, set_txt, bold, 17, Color(0.3, 0.5, 0.2), C, Vector2(-335, -92), Vector2(540, 46), M, false)
	var class_info := HeroClasses.info(gs.class_id)
	hud.txt(page, "Habilidades de " + str(class_info["name"]), serif, 29, ink, C, Vector2(-335, -132), Vector2(500, 40), M, false)
	hud.txt(page, str(class_info["skill"]), bold, 26, ink, C, Vector2(-335, -182), Vector2(485, 40), M, false)
	var benefit := hud.txt(page, "FORTE: " + str(class_info["strong"]), sans, 22, Color(.25, .42, .22), C, Vector2(-335, -228), Vector2(485, 46), M, false)
	benefit.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	var frailty := hud.txt(page, "FRACO: " + str(class_info["weak"]), sans, 22, faint, C, Vector2(-335, -295), Vector2(485, 56), M, false)
	frailty.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART

	# ---- right page: the bag
	hud.txt(page, "Bolsa", serif, 44, ink, C, Vector2(335, 300), Vector2(500, 60), M, false)
	if gs.inv_ids.is_empty():
		hud.txt(page, "Vazia. Os demônios carregam coisas valiosas...", sans, 24, faint, C, Vector2(335, 150), Vector2(500, 40), M, false)
	sel = clampi(sel, 0, maxi(0, gs.inv_ids.size() - 1))
	btns.clear()
	if sel < top:
		top = sel
	elif sel >= top + ROWS:
		top = sel - ROWS + 1
	top = clampi(top, 0, maxi(0, gs.inv_ids.size() - ROWS))
	if gs.inv_ids.size() > ROWS:
		hud.txt(page, "%d/%d" % [sel + 1, gs.inv_ids.size()], sans, 22, faint, C, Vector2(560, 300), Vector2(120, 30), R, false)
	for r in mini(gs.inv_ids.size() - top, ROWS):
		var i := top + r
		var d: Dictionary = Data.items[gs.inv_ids[i]]
		var y := 220.0 - r * 56.0
		if i == sel:
			hud.img(page, Sheets.ui("smear"), C, Vector2(335, y), Vector2(560, 70)).modulate = Color(0.85, 0.6, 0.2, 0.35)
			hud.txt(page, "◆", serif, 22, Color(0.75, 0.5, 0.15), C, Vector2(100, y), Vector2(30, 30), M, false)
		hud.img(page, Sheets.icon(d["icon"]), C, Vector2(150, y), Vector2(48, 48))
		var rc: Color = Data.RARITY_COLORS[int(d["rarity"])]
		var name_col := ink if int(d["rarity"]) == 0 else rc.lerp(ink, 0.45)
		hud.txt(page, d["name"], bold, 25, name_col, C, Vector2(370, y), Vector2(380, 34), L, false)
		hud.txt(page, "×%d" % int(gs.inv_counts[i]), serif, 26, faint, C, Vector2(590, y), Vector2(80, 34), R, false)
		_row_btn(page, Vector2(335, y), Vector2(560, 54), _pick.bind(i))
	if not gs.inv_ids.is_empty():
		var d: Dictionary = Data.items[gs.inv_ids[sel]]
		var rar := int(d["rarity"])
		hud.img(page, Sheets.ui("flourish"), C, Vector2(335, -138), Vector2(380, 30))
		var kind := "Equipamento" if int(d["slot"]) > 0 else ("Consumível" if d["consumable"] else "Material")
		var rl := hud.txt(page, "%s · %s" % [Data.RARITY_NAMES[rar].to_upper(), kind], bold, 23, (Data.RARITY_COLORS[rar] as Color).lerp(ink, 0.35), C, Vector2(335, -166), Vector2(520, 30), M, false)
		rl.name = "RarityLabel"
		if int(d["slot"]) > 0:
			# comparison with the piece currently worn in that slot (green = better, red = worse)
			var cur := gs.equipped(int(d["slot"]))
			var shown := 0
			for kv in [["atk", "ATQ"], ["defense", "DEF"], ["mag", "MAG"], ["hp", "PV"]]:
				var nv := gs.item_stat(gs.inv_ids[sel], kv[0])
				var ov := gs.item_stat(cur, kv[0])
				if nv == 0.0 and ov == 0.0:
					continue
				var diff := roundi(nv - ov)
				var col := Color(0.2, 0.55, 0.2) if diff > 0 else (Color(0.75, 0.2, 0.15) if diff < 0 else faint)
				var arrow := "▲" if diff > 0 else ("▼" if diff < 0 else "=")
				hud.txt(page, "%s %d %s%s" % [kv[1], roundi(nv), arrow, ("%+d" % diff) if diff != 0 else ""], bold, 21, col, C, Vector2(120 + shown * 138, -196), Vector2(136, 26), M, false)
				shown += 1
		var desc := hud.txt(page, str(d["desc"]), sans, 19, ink, C, Vector2(335, -243), Vector2(540, 56), M, false, VERTICAL_ALIGNMENT_TOP)
		desc.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
		var act := "Equipar" if int(d["slot"]) > 0 else "Usar"
		_btn(page, act, Vector2(190, -300), Vector2(230, 56), _act_use, Color(0.32, 0.2, 0.1, 0.95))
		var price := sell_price(gs.inv_ids[sel])
		if price > 0:
			_btn(page, "Vender %d (Q)" % price, Vector2(450, -300), Vector2(290, 56), _act_sell, Color(0.4, 0.14, 0.1, 0.95))
	# The information page is rebuilt after item use; keep X above it.
	root.move_child(close_button, root.get_child_count() - 1)
