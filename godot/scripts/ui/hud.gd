class_name Hud
extends CanvasLayer
## Non-boxy HUD: portrait medallion wrapped by curved HP/MP arcs, skill orbs fanned along an arc,
## loot feed without panels, cinematic dialogue band, banners, boss bar, credits, cutscene backdrop.
## Layout is authored in a 1920x1080 space with Unity-like (anchor, centre offset, y-up) coordinates.

const SIZE := Vector2(1920, 1080)
const ARC_SPAN := 240.0

var root: Control
var fan_node: Control
var medallion: Control
var gold_icon: TextureRect

var hp_fill: TextureProgressBar
var hp_trail: TextureProgressBar
var mp_fill: TextureProgressBar
var hp_text: Label
var level_text: Label
var gold_text: Label
var quest_head: Label
var quest_sub: Label
var quest_c: Control
var quest_glow: TextureRect
var quest_tag: Label
var _quest_key := ""
var _quest_head := ""
var _quest_t := 99.0
var compass: Control
var compass_arrow: Polygon2D
var compass_label: Label
var rank_text: Label
var vignette: TextureRect
var hp_shown := 1.0
var hp_trail_shown := 1.0
var mp_shown := 1.0
var hurt_amt := 0.0

var orb_cd: Array = []
var potion_count: Label

var feeds: Array = []        # {c: Control, t: float}
var plates := {}             # Enemy -> {c, fill, trail, shown}

var scene_img: TextureRect
var scene_alpha := 0.0
var scene_target := 0.0

var dlg: Control
var dlg_name: Label
var dlg_text: Label
var dlg_hint: Label
var dlg_portrait: TextureRect
var dlg_frame: TextureRect
var dlg_plate: TextureRect
var lines: Array = []
var line_idx := 0
var type_t := 0.0
var _whisper_n := 0
var _voice := 0.5
var _narr := false
var _cps := 55.0
var on_done := Callable()
var _active := false

var banner_c: Control
var banner_title: Label
var banner_sub: Label
var banner_t := -1.0

var boss_bar: Control
var boss_fill: TextureProgressBar
var boss_trail: TextureProgressBar
var boss_name: Label
var boss_title: Label
var boss_shown := 1.0

var credits: ColorRect
var credits_text: Label
var credits_y := 0.0
var credits_t := 0.0
var credits_done := Callable()


# ------------------------------------------------------------------ builders
func ctl(parent: Control, anchor: Vector2, pos: Vector2, size: Vector2, node: Control = null) -> Control:
	var c := node if node else Control.new()
	c.mouse_filter = Control.MOUSE_FILTER_IGNORE
	c.size = size
	c.position = Vector2(parent.size.x * anchor.x, parent.size.y * (1.0 - anchor.y)) + Vector2(pos.x, -pos.y) - size / 2.0
	c.pivot_offset = size / 2.0
	parent.add_child(c)
	return c


func img(parent: Control, tex: Texture2D, anchor: Vector2, pos: Vector2, size: Vector2) -> TextureRect:
	var t := TextureRect.new()
	t.texture = tex
	t.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	t.stretch_mode = TextureRect.STRETCH_SCALE
	ctl(parent, anchor, pos, size, t)
	return t


func txt(parent: Control, s: String, font: Font, fsize: int, color: Color, anchor: Vector2, pos: Vector2, box: Vector2,
		h: int = HORIZONTAL_ALIGNMENT_CENTER, outline: bool = true, v: int = VERTICAL_ALIGNMENT_CENTER) -> Label:
	var l := Util.label(s, fsize, color, font, outline)
	l.horizontal_alignment = h
	l.vertical_alignment = v
	l.mouse_filter = Control.MOUSE_FILTER_IGNORE
	ctl(parent, anchor, pos, box, l)
	return l


func _radial(parent: Control, tex_name: String, size: float, degrees: float, init_angle: float, tint: Color = Color.WHITE) -> TextureProgressBar:
	var tex := Sheets.ui(tex_name)
	var b := TextureProgressBar.new()
	b.fill_mode = TextureProgressBar.FILL_CLOCKWISE
	b.min_value = 0.0
	b.max_value = 1.0
	b.step = 0.0001
	b.value = 1.0
	b.radial_initial_angle = init_angle
	b.radial_fill_degrees = degrees
	b.texture_progress = tex
	b.tint_progress = tint
	var native := Vector2(tex.get_size())
	ctl(parent, Vector2(0.5, 0.5), Vector2.ZERO, native, b)
	b.scale = Vector2.ONE * size / native.x
	return b


func _pill(parent: Control, pos: Vector2, size: Vector2, tint: Color = Color.WHITE) -> TextureProgressBar:
	var b := TextureProgressBar.new()
	b.fill_mode = TextureProgressBar.FILL_LEFT_TO_RIGHT
	b.min_value = 0.0
	b.max_value = 1.0
	b.step = 0.0001
	b.value = 1.0
	b.nine_patch_stretch = true
	b.texture_progress = Sheets.ui("pill_fill")
	b.tint_progress = tint
	ctl(parent, Vector2(0.5, 0.5), pos, size, b)
	return b


func _ready() -> void:
	layer = 10
	process_mode = Node.PROCESS_MODE_ALWAYS
	root = Control.new()
	root.size = SIZE
	root.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(root)
	_build()


func _build() -> void:
	var C := Vector2(0.5, 0.5)
	var serif := Util.font_serif
	var sans := Util.font_sans
	var bold := Util.font_bold

	vignette = img(root, Sheets.ui("vignette"), C, Vector2.ZERO, SIZE)
	vignette.modulate = Color(0.05, 0.02, 0.08, 0.55)

	# ---- portrait medallion + arcs (bottom-left)
	var med := ctl(root, Vector2(0, 0), Vector2(190, 190), Vector2(460, 460))
	medallion = med
	img(med, Sheets.ui("smear"), C, Vector2(40, -10), Vector2(620, 420)).modulate = Color(0, 0, 0, 0.38)
	_radial(med, "arc_hp_track", 440, ARC_SPAN, 270)
	hp_trail = _radial(med, "arc_hp_fill", 440, ARC_SPAN, 270, Color(1, 0.92, 0.75, 0.9))
	hp_fill = _radial(med, "arc_hp_fill", 440, ARC_SPAN, 270)
	_radial(med, "arc_mp_track", 440, ARC_SPAN, 270)
	mp_fill = _radial(med, "arc_mp_fill", 440, ARC_SPAN, 270)
	img(med, Sheets.ui("portrait"), C, Vector2.ZERO, Vector2(196, 196))
	img(med, Sheets.ui("medallion"), C, Vector2.ZERO, Vector2(300, 300))
	level_text = txt(med, "1", serif, 30, Color(1, 0.93, 0.7), C, Vector2(0, -128), Vector2(80, 40))
	hp_text = txt(med, "", serif, 26, Color(1, 0.9, 0.85), C, Vector2(232, 72), Vector2(200, 40), HORIZONTAL_ALIGNMENT_LEFT)
	rank_text = txt(med, "Aventureiro · Rank F", bold, 22, Color(0.95, 0.88, 0.7), C, Vector2(150, 230), Vector2(380, 30), HORIZONTAL_ALIGNMENT_LEFT)

	# ---- gold (top-left)
	gold_icon = img(root, Sheets.icon("coin"), Vector2(0, 1), Vector2(58, -52), Vector2(46, 46))
	gold_text = txt(root, "0", serif, 30, Color(1, 0.88, 0.45), Vector2(0, 1), Vector2(170, -52), Vector2(160, 40), HORIZONTAL_ALIGNMENT_LEFT)

	# ---- quest tracker (top-right)
	var q := ctl(root, Vector2(1, 1), Vector2(-250, -90), Vector2(460, 140))
	quest_c = q
	img(q, Sheets.ui("smear"), C, Vector2.ZERO, Vector2(520, 200)).modulate = Color(0, 0, 0, 0.42)
	quest_glow = img(q, Util.soft_circle(), C, Vector2(0, 0), Vector2(620, 220))
	quest_glow.material = Util.additive()
	quest_glow.modulate = Color(1, 0.8, 0.35, 0.0)
	quest_tag = txt(q, "NOVA MISSÃO", Util.font_serif, 22, Color(1, 0.85, 0.4), C, Vector2(0, 92), Vector2(440, 30))
	quest_tag.modulate.a = 0.0
	img(q, Sheets.ui("flourish"), C, Vector2(0, 44), Vector2(360, 36))
	quest_head = txt(q, "", sans, 25, Color(0.98, 0.95, 0.88), C, Vector2(0, 0), Vector2(440, 34))
	quest_sub = txt(q, "", sans, 21, Color(0.92, 0.86, 0.7), C, Vector2(0, -34), Vector2(440, 30))

	# ---- compass arrow (points to off-screen objective)
	compass = Control.new()
	compass.mouse_filter = Control.MOUSE_FILTER_IGNORE
	compass_arrow = Polygon2D.new()
	compass_arrow.polygon = PackedVector2Array([Vector2(34, 0), Vector2(-20, -24), Vector2(-8, 0), Vector2(-20, 24)])
	compass_arrow.color = Color(1, 0.82, 0.3)
	var outline := Polygon2D.new()
	outline.polygon = PackedVector2Array([Vector2(44, 0), Vector2(-30, -34), Vector2(-14, 0), Vector2(-30, 34)])
	outline.color = Color(0.25, 0.12, 0.05)
	compass.add_child(outline)
	compass.add_child(compass_arrow)
	compass_label = Util.label("", 22, Color(1, 0.95, 0.75), Util.font_bold, true)
	compass_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	compass_label.size = Vector2(160, 30)
	compass.visible = false
	root.add_child(compass)
	root.add_child(compass_label)
	compass_label.visible = false

	# ---- skill orbs fanned along an arc (bottom-right)
	var fan := ctl(root, Vector2(1, 0), Vector2(-170, 150), Vector2(10, 10))
	fan_node = fan
	var icons := ["skill_sword", "skill_spark", "skill_roll", "potion"]
	var keys := ["J", "K", "Espaço", "Q"]
	for i in 4:
		var a := deg_to_rad(200.0 - i * 34.0)
		var p := Vector2(cos(a), sin(a)) * 190.0 + Vector2(120, -40)
		var sz := 132.0 if i == 0 else 104.0
		var o := img(fan, Sheets.ui("orb"), C, p, Vector2(sz, sz))
		img(o, Sheets.icon(icons[i]), C, Vector2.ZERO, Vector2(sz * 0.56, sz * 0.56))
		var cd := TextureProgressBar.new()
		cd.fill_mode = TextureProgressBar.FILL_CLOCKWISE
		cd.min_value = 0.0
		cd.max_value = 1.0
		cd.step = 0.0001
		cd.nine_patch_stretch = false
		cd.texture_progress = Sheets.ui("orb_shade")
		var nat := Vector2(cd.texture_progress.get_size())
		ctl(o, C, Vector2.ZERO, nat, cd)
		cd.scale = Vector2.ONE * sz * 0.8 / nat.x
		cd.value = 0.0
		orb_cd.append(cd)
		txt(o, keys[i], bold, 20, Color(1, 0.95, 0.8), Vector2(0.5, 0), Vector2(0, -6), Vector2(100, 24))
		if i == 3:
			potion_count = txt(o, "", serif, 24, Color.WHITE, Vector2(1, 1), Vector2(-14, -14), Vector2(40, 30))
	txt(root, "WASD mover · Shift correr · E falar · Tab grimório · Esc opções", sans, 20, Color(1, 1, 1, 0.7), Vector2(1, 0), Vector2(-250, 26), Vector2(520, 28))

	# ---- cutscene backdrop
	scene_img = img(root, null, C, Vector2.ZERO, SIZE)
	scene_img.modulate = Color(1, 1, 1, 0)
	scene_img.visible = false

	# ---- dialogue band
	dlg = ctl(root, Vector2(0.5, 0), Vector2(0, 170), Vector2(1920, 340))
	img(dlg, Sheets.ui("dialogue_band"), C, Vector2(0, -20), Vector2(1920, 380))
	dlg_portrait = img(dlg, Sheets.ui("portrait"), C, Vector2(-700, 30), Vector2(230, 230))
	dlg_frame = img(dlg, Sheets.ui("medallion"), C, Vector2(-700, 30), Vector2(340, 340))
	dlg_plate = img(dlg, Sheets.ui("nameplate"), C, Vector2(-330, 118), Vector2(480, 70))
	dlg_name = txt(dlg, "", serif, 32, Color(1, 0.92, 0.7), C, Vector2(-330, 120), Vector2(460, 50))
	dlg_text = txt(dlg, "", sans, 34, Color(1, 0.98, 0.94), C, Vector2(130, 20), Vector2(1250, 160), HORIZONTAL_ALIGNMENT_LEFT, true, VERTICAL_ALIGNMENT_TOP)
	dlg_text.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	dlg_hint = txt(dlg, "E / Enter ▸", bold, 22, Color(1, 0.9, 0.6, 0.9), C, Vector2(700, -90), Vector2(200, 30))
	dlg.visible = false

	# ---- zone banner
	banner_c = ctl(root, Vector2(0.5, 1), Vector2(0, -170), Vector2(900, 160))
	img(banner_c, Sheets.ui("flourish"), C, Vector2(0, -36), Vector2(560, 48))
	banner_title = txt(banner_c, "", serif, 64, Color(1, 0.95, 0.82), C, Vector2(0, 20), Vector2(900, 80))
	banner_sub = txt(banner_c, "", sans, 28, Color(1, 0.9, 0.7), C, Vector2(0, -78), Vector2(900, 40))
	banner_c.visible = false

	# ---- boss bar
	boss_bar = ctl(root, Vector2(0.5, 1), Vector2(0, -60), Vector2(900, 90))
	boss_name = txt(boss_bar, "", serif, 34, Color(1, 0.92, 0.78), C, Vector2(0, 26), Vector2(900, 44))
	img(boss_bar, Sheets.ui("pill_track"), C, Vector2(0, -12), Vector2(760, 30))
	boss_trail = _pill(boss_bar, Vector2(0, -12), Vector2(740, 20), Color(1, 0.9, 0.7))
	boss_fill = _pill(boss_bar, Vector2(0, -12), Vector2(740, 20))
	boss_title = txt(boss_bar, "", sans, 22, Color(1, 0.85, 0.6), C, Vector2(0, -44), Vector2(900, 28))
	boss_bar.visible = false

	# ---- credits
	credits = ColorRect.new()
	credits.color = Color(0.02, 0.01, 0.04, 1)
	credits.size = SIZE
	credits.mouse_filter = Control.MOUSE_FILTER_IGNORE
	root.add_child(credits)
	credits_text = Util.label("", 44, Color(1, 0.95, 0.82), serif, true)
	credits_text.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	credits_text.size = Vector2(1500, 100)
	credits_text.label_settings.line_spacing = 14
	credits.add_child(credits_text)
	credits.visible = false


# ------------------------------------------------------------------ api
func in_dialogue() -> bool:
	return _active


func in_credits() -> bool:
	return credits.visible


func banner(title: String, sub: String) -> void:
	banner_title.text = title
	banner_sub.text = sub
	banner_t = 0.0
	banner_c.visible = true


func quest_complete(text: String) -> void:
	Sfx.play("levelup", 0.5, 1.3)
	var c := ctl(root, Vector2(0.5, 1), Vector2(0, -330), Vector2(900, 120))
	var burst := img(c, Util.soft_circle(), Vector2(0.5, 0.5), Vector2.ZERO, Vector2(900, 260))
	burst.material = Util.additive()
	burst.modulate = Color(1, 0.8, 0.3, 0.55)
	img(c, Sheets.ui("flourish"), Vector2(0.5, 0.5), Vector2(0, -34), Vector2(520, 44))
	txt(c, "MISSÃO CONCLUÍDA", Util.font_serif, 52, Color(1, 0.9, 0.5), Vector2(0.5, 0.5), Vector2(0, 14), Vector2(900, 70))
	txt(c, text, Util.font_sans, 28, Color(1, 0.96, 0.85), Vector2(0.5, 0.5), Vector2(0, -52), Vector2(900, 36))
	c.scale = Vector2(0.6, 0.6)
	c.modulate.a = 0.0
	var tw := c.create_tween()
	tw.tween_property(c, "modulate:a", 1.0, 0.25)
	tw.parallel().tween_property(c, "scale", Vector2(1.08, 1.08), 0.3).set_trans(Tween.TRANS_BACK).set_ease(Tween.EASE_OUT)
	tw.tween_property(c, "scale", Vector2.ONE, 0.15)
	tw.tween_interval(2.4)
	tw.tween_property(c, "modulate:a", 0.0, 0.6)
	tw.tween_callback(c.queue_free)


func _quest_changed(headline_changed: bool) -> void:
	_quest_t = 0.0
	quest_tag.text = "NOVA MISSÃO" if headline_changed else "PROGRESSO"
	if headline_changed:
		Sfx.play("ui", 0.35, 1.5)


func hurt_pulse() -> void:
	hurt_amt = 1.0


func loot_feed(def: Dictionary, count: int) -> void:
	var c := ctl(root, Vector2(1, 0.5), Vector2(-230, -40), Vector2(420, 52))
	img(c, Sheets.ui("smear"), Vector2(0.5, 0.5), Vector2.ZERO, Vector2(440, 80)).modulate = Color(0, 0, 0, 0.35)
	img(c, Sheets.icon(def["icon"]), Vector2(0.5, 0.5), Vector2(-150, 0), Vector2(46, 46))
	txt(c, ("%d× " % count if count > 1 else "") + str(def["name"]), Util.font_bold, 26, Data.RARITY_COLORS[int(def["rarity"])],
		Vector2(0.5, 0.5), Vector2(30, 0), Vector2(320, 40), HORIZONTAL_ALIGNMENT_LEFT)
	for f in feeds:
		f["c"].position.y -= 56.0
	feeds.append({"c": c, "t": 0.0})


func show_dialogue(l: Array, done: Callable) -> void:
	lines = l
	line_idx = 0
	type_t = 0.0
	on_done = done
	_active = true
	dlg.visible = true
	if _skip_scenes():
		_show_line()


## Applies "@scene" markers (illustration name in text). Returns false when the script ended.
func _skip_scenes() -> bool:
	while line_idx < lines.size() and lines[line_idx][0] == "@scene":
		var t := Sheets.tex("Sprites/Cutscenes/" + str(lines[line_idx][1]))
		if t:
			scene_img.texture = t
			scene_img.visible = true
			scene_alpha = 0.0
			scene_target = 1.0
		line_idx += 1
	if line_idx >= lines.size():
		_finish_dialogue()
		return false
	return true


func _finish_dialogue() -> void:
	lines = []
	_active = false
	dlg.visible = false
	scene_target = 0.0
	var d := on_done
	on_done = Callable()
	if d.is_valid():
		d.call()


func _show_line() -> void:
	var ln: Array = lines[line_idx]
	var narr: bool = str(ln[0]) == ""
	dlg_name.text = "" if narr else Story.name_of(ln[0])
	dlg_plate.visible = not narr
	dlg_frame.visible = not narr
	dlg_portrait.visible = not narr
	if not narr:
		var pn := "portrait_" + str(ln[0])
		dlg_portrait.texture = Sheets.ui(pn) if ResourceLoader.exists("res://assets/Sprites/Ui/%s.png" % pn) else Sheets.ui("portrait")
	dlg_text.modulate = Color(0.85, 0.88, 1.0) if narr else Color.WHITE
	dlg_text.text = ln[1]
	dlg_text.visible_characters = 0
	type_t = 0.0
	_whisper_n = 0
	_narr = narr
	_cps = 30.0 if str(ln[0]) == "lumia" else (44.0 if narr else 55.0)   # the goddess speaks slowly, with weight
	_voice = 0.12 if narr else float(hash(str(ln[0])) % 1000) / 1000.0
	if str(ln[0]) in ["lumia", "receptionist", "sylra", "cleric", "witch", "elowen", "villager", "child"]:
		_voice = 0.65 + _voice * 0.35      # lighter voices
	Sfx.play("ui", 0.2, 1.2)


func advance() -> void:
	if not _active:
		return
	var full: String = lines[line_idx][1]
	if int(type_t * _cps) < full.length():
		type_t = 999.0
		return
	line_idx += 1
	if line_idx >= lines.size():
		_finish_dialogue()
		return
	if _skip_scenes():
		_show_line()


func show_credits(text: String, done: Callable) -> void:
	credits.visible = true
	credits_text.text = text
	credits_text.size = Vector2(1500, credits_text.get_combined_minimum_size().y)
	credits_y = 1100.0
	credits_t = 0.0
	credits_done = done
	credits_text.position = Vector2(210, credits_y)


# ------------------------------------------------------------------ per-frame
func _process(delta: float) -> void:
	var dt := delta / maxf(Engine.time_scale, 0.001)   # real time, unaffected by hit-stop/slow motion
	var now := Time.get_ticks_msec() / 1000.0
	var p := Player.I
	if p != null and is_instance_valid(p):
		var gs := p.gs
		var hp_n := p.hp / gs.hp_max()
		var mp_n := p.mp / gs.max_mp
		hp_shown = lerpf(hp_shown, hp_n, minf(1.0, dt * 12.0))
		hp_trail_shown = hp_shown if hp_trail_shown < hp_shown else move_toward(hp_trail_shown, hp_shown, dt * 0.35)
		mp_shown = lerpf(mp_shown, mp_n, minf(1.0, dt * 10.0))
		hp_fill.value = clampf(hp_shown, 0.0, 1.0)
		hp_trail.value = clampf(hp_trail_shown, 0.0, 1.0)
		mp_fill.value = clampf(mp_shown, 0.0, 1.0)
		var low := (0.5 + 0.5 * sin(now * 8.0)) if hp_n < 0.3 else 0.0
		hp_fill.tint_progress = Color.WHITE.lerp(Color(1, 0.6, 0.6), low)
		hp_text.text = "%d / %d" % [ceili(p.hp), roundi(gs.hp_max())]
		level_text.text = str(gs.level)
		gold_text.text = str(gs.gold)
		rank_text.text = "Aventureiro · Rank " + gs.guild_rank
		potion_count.text = str(gs.count("potion"))
		orb_cd[1].value = 1.0 - p.mp / 12.0 if p.mp < 12.0 else 0.0
		# Melee and dodge have no stamina requirement; the orbs stay ready.
		orb_cd[2].value = 0.0
		orb_cd[0].value = 0.0
	var ql := Game.quest_line().split("\n")
	quest_head.text = ql[0]
	quest_sub.text = ql[1] if ql.size() > 1 else ""
	var qk := Game.quest_line()
	if qk != _quest_key:
		if _quest_key != "":
			_quest_changed(ql[0] != _quest_head)
		_quest_key = qk
		_quest_head = ql[0]
	_quest_t += dt
	var qa := _quest_t
	# slide-in + pop + glow flash + tag, then a slow breathing glow while an objective is active
	var slide := clampf(1.0 - qa / 0.45, 0.0, 1.0)
	quest_c.position.x = (SIZE.x - 250.0 - 230.0) + slide * slide * 90.0
	var pop := 1.0 + 0.1 * maxf(0.0, 1.0 - qa / 0.35) * sin(qa * 18.0 + 1.5)
	quest_c.scale = Vector2.ONE * pop
	quest_c.modulate.a = 1.0 - slide * 0.8
	quest_glow.modulate.a = maxf(0.0, 0.7 * (1.0 - qa / 1.4)) + 0.05 + 0.04 * sin(now * 2.0)
	quest_tag.modulate.a = clampf(qa / 0.2, 0.0, 1.0) * clampf((3.0 - qa) / 0.6, 0.0, 1.0)
	quest_tag.position.y = -37.0 + 20.0 * (1.0 - minf(qa / 0.4, 1.0))
	_update_compass(now)
	hurt_amt = maxf(0.0, hurt_amt - dt * 2.2)
	vignette.modulate = Color(0.05, 0.02, 0.08, 0.5).lerp(Color(0.75, 0.05, 0.05, 0.85), hurt_amt)

	for i in range(feeds.size() - 1, -1, -1):
		var f: Dictionary = feeds[i]
		f["t"] += dt
		f["c"].modulate.a = clampf(f["t"] * 6.0, 0.0, 1.0) * clampf((3.2 - f["t"]) / 0.5, 0.0, 1.0)
		if f["t"] > 3.2:
			f["c"].queue_free()
			feeds.remove_at(i)
	_update_plates(dt, now)
	_update_boss_bar(dt, now)

	if scene_img.visible:
		scene_alpha = move_toward(scene_alpha, scene_target, dt * 2.2)
		scene_img.modulate = Color(1, 1, 1, scene_alpha)
		if scene_target == 0.0 and scene_alpha <= 0.0:
			scene_img.visible = false

	if credits.visible:
		credits_t += dt
		var fast := Input.is_physical_key_pressed(KEY_SPACE) or Input.is_physical_key_pressed(KEY_DOWN) or Game.touch_run
		credits_y -= dt * 70.0 * (4.0 if fast else 1.0)
		credits_text.position = Vector2(210, credits_y)
		var skip := credits_t > 2.0 and (Game.consume(KEY_ESCAPE) or Game.consume(KEY_ENTER))
		if credits_y + credits_text.size.y < 0.0 or skip:
			credits.visible = false
			var d := credits_done
			credits_done = Callable()
			if d.is_valid():
				d.call()

	if _active:
		type_t += dt
		var full: String = lines[line_idx][1]
		var n := mini(full.length(), int(type_t * _cps))
		dlg_text.visible_characters = n
		# whisper: a breathy syllable on every vowel / hiss as the text is revealed
		while _whisper_n < n:
			var ch := full.substr(_whisper_n, 1)
			if _whisper_n % 2 == 0 or ch in ["s", "x", "z"]:
				Sfx.whisper(ch, _voice, 0.16 if _narr else 0.28)
			_whisper_n += 1
		dlg_hint.modulate.a = (0.6 + 0.4 * sin(now * 5.0)) if n >= full.length() else 0.0
		var go := false
		for k in [KEY_E, KEY_ENTER, KEY_KP_ENTER, KEY_SPACE, -MOUSE_BUTTON_LEFT]:
			if Game.consume(k):
				go = true
		if go:
			advance()

	if banner_t >= 0.0:
		banner_t += dt
		var a := clampf(banner_t / 0.6, 0.0, 1.0) * clampf((4.0 - banner_t) / 0.8, 0.0, 1.0)
		banner_c.modulate.a = a
		banner_c.position.y = 170.0 - 80.0 + (1.0 - clampf(banner_t / 0.6, 0.0, 1.0)) * -20.0
		if banner_t > 4.0:
			banner_t = -1.0
			banner_c.visible = false


func _update_boss_bar(dt: float, _now: float) -> void:
	var boss: Enemy = null
	var p := Player.I
	if p != null:
		for e in Enemy.all:
			if is_instance_valid(e) and not e.dead and e.def["boss"]:
				var d := (e.global_position - p.global_position).length() / 64.0
				if d < 14.0 and (Game.time() - e.last_hurt < 10.0 or d < 9.0):
					boss = e
					break
	if boss == null:
		boss_bar.visible = false
		return
	boss_bar.visible = true
	boss_name.text = boss.def["name"]
	boss_title.text = str(boss.def.get("title", ""))
	var n := boss.hp / boss.max_hp
	boss_fill.value = n
	boss_shown = n if boss_shown < n else move_toward(boss_shown, n, dt * 0.35)
	boss_trail.value = boss_shown


func _update_plates(dt: float, _now: float) -> void:
	var p := Player.I
	var xf := get_viewport().get_canvas_transform()
	for e in Enemy.all:
		if not is_instance_valid(e):
			continue
		var show: bool = not e.dead and not get_tree().paused and (Game.time() - e.last_hurt < 6.0 or (p != null and (p.global_position - e.global_position).length() < 5.0 * 64.0))
		var pl: Dictionary = plates.get(e, {})
		if show and pl.is_empty():
			var c := ctl(root, Vector2(0, 0), Vector2.ZERO, Vector2(120, 30))
			img(c, Sheets.ui("pill_track"), Vector2(0.5, 0.5), Vector2.ZERO, Vector2(104, 16))
			var trail := _pill(c, Vector2.ZERO, Vector2(98, 10), Color(1, 0.9, 0.7))
			var fill := _pill(c, Vector2.ZERO, Vector2(98, 10))
			var over: bool = p != null and e.level > p.gs.level
			txt(c, "Nv %d" % e.level, Util.font_bold, 18, Color(1, 0.5, 0.4) if over else Color(1, 0.95, 0.85), Vector2(0.5, 0.5), Vector2(0, 18), Vector2(120, 22))
			pl = {"c": c, "fill": fill, "trail": trail, "shown": 1.0}
			plates[e] = pl
		if pl.is_empty():
			continue
		pl["c"].visible = show
		if not show:
			continue
		var sp: Vector2 = xf * (e.global_position + Vector2.UP * 2.1 * 64.0 * absf(e.anim.scale.y))
		pl["c"].position = sp - Vector2(60, 15)
		var n := e.hp / e.max_hp
		pl["fill"].value = n
		pl["shown"] = n if pl["shown"] < n else move_toward(pl["shown"], n, dt * 0.6)
		pl["trail"].value = pl["shown"]
	for k in plates.keys():
		if not is_instance_valid(k) or k.dead:
			if is_instance_valid(plates[k]["c"]):
				plates[k]["c"].queue_free()
			plates.erase(k)


func _update_compass(now: float) -> void:
	var show_it: bool = Game.obj_active and not _active and not Game.grimoire.open and Player.I != null
	if show_it:
		var sp: Vector2 = get_viewport().get_canvas_transform() * Game.obj_pos
		var rect := Rect2(110, 110, SIZE.x - 220, SIZE.y - 220)
		if rect.has_point(sp):
			show_it = false
		else:
			var centre := SIZE / 2.0
			var dir := (sp - centre).normalized()
			var k := 1e9
			if absf(dir.x) > 0.001:
				k = minf(k, (rect.size.x / 2.0) / absf(dir.x))
			if absf(dir.y) > 0.001:
				k = minf(k, (rect.size.y / 2.0) / absf(dir.y))
			var pos := centre + dir * k
			compass.position = pos + dir * (sin(now * 5.0) * 6.0)
			compass.rotation = dir.angle()
			compass_label.position = pos - Vector2(80, 0) - dir * Vector2(0, 0) + Vector2(0, -50 if dir.y > 0.3 else 36)
			compass_label.text = "%d m" % roundi(Game.obj_dist / 64.0 * 1.5)
	compass.visible = show_it
	compass_label.visible = show_it
