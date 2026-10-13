class_name OptionsMenu
extends Node
## Pause / options (Esc): music, effects and voice volumes, save, resume. Pauses the game.

const ROWS := ["Music", "Sfx", "Voice", "Gfx", "save", "resume"]
const LABELS := {"Music": "Música", "Sfx": "Efeitos", "Voice": "Vozes", "Gfx": "Gráficos", "save": "Salvar jogo", "resume": "Continuar"}

var open := false
var hud: Hud
var root: Control
var sel := 0
var _fills := {}
var _marks := []
var _vals := {}
var _gfx: Label
const GFX_NAMES := ["Baixa", "Média", "Alta"]


func setup(h: Hud) -> void:
	process_mode = Node.PROCESS_MODE_ALWAYS
	hud = h
	var C := Vector2(0.5, 0.5)
	root = hud.ctl(hud.root, C, Vector2.ZERO, Hud.SIZE)
	var dim := hud.img(root, Util.soft_circle(), C, Vector2.ZERO, Vector2(2600, 1800))
	dim.modulate = Color(0.02, 0.01, 0.04, 0.8)
	hud.img(root, Sheets.ui("smear"), C, Vector2.ZERO, Vector2(900, 700)).modulate = Color(0, 0, 0, 0.55)
	hud.img(root, Sheets.ui("flourish"), C, Vector2(0, 250), Vector2(520, 44))
	hud.txt(root, "Opções", Util.font_serif, 60, Color(1, 0.93, 0.7), C, Vector2(0, 310), Vector2(700, 80))
	for i in ROWS.size():
		var r: String = ROWS[i]
		var y := 160.0 - i * 90.0
		if i >= 4:
			y -= 20.0
		_marks.append(hud.txt(root, "◆", Util.font_serif, 30, Color(1, 0.8, 0.3), C, Vector2(-330, y), Vector2(40, 40)))
		hud.txt(root, LABELS[r], Util.font_bold, 36, Color(1, 0.96, 0.86), C, Vector2(-170 if i < 4 else 0, y), Vector2(240, 44),
			HORIZONTAL_ALIGNMENT_LEFT if i < 4 else HORIZONTAL_ALIGNMENT_CENTER)
		if r == "Gfx":
			_gfx = hud.txt(root, "", Util.font_bold, 34, Color(1, 0.9, 0.7), C, Vector2(150, y), Vector2(360, 44))
		if i < 3:
			hud.img(root, Sheets.ui("pill_track"), C, Vector2(150, y), Vector2(360, 30))
			var f := TextureProgressBar.new()
			f.fill_mode = TextureProgressBar.FILL_LEFT_TO_RIGHT
			f.min_value = 0.0
			f.max_value = 1.0
			f.step = 0.01
			f.nine_patch_stretch = true
			f.texture_progress = Sheets.ui("pill_fill")
			hud.ctl(root, C, Vector2(150, y), Vector2(344, 20), f)
			_fills[r] = f
			_vals[r] = hud.txt(root, "", Util.font_serif, 24, Color(1, 0.9, 0.7), C, Vector2(380, y), Vector2(90, 30))
	hud.txt(root, "W/S escolher  ·  A/D ajustar  ·  Enter confirmar  ·  Esc voltar", Util.font_sans, 24, Color(1, 1, 1, 0.7), C, Vector2(0, -300), Vector2(1000, 34))
	root.visible = false


func toggle() -> void:
	open = not open
	root.visible = open
	get_tree().paused = open or Game.in_menu
	if open:
		sel = 0
		_refresh()
		Sfx.play("ui", 0.3, 0.8)
	else:
		Game.save_settings_note()
	if Player.I != null:
		Player.I.input_locked = open or Game.in_menu


func _refresh() -> void:
	for r in _fills:
		_fills[r].value = Sfx.levels[r]
		_vals[r].text = "%d%%" % roundi(Sfx.levels[r] * 100.0)
	_gfx.text = "◀  %s  ▶" % GFX_NAMES[Game.quality]
	for i in _marks.size():
		_marks[i].modulate.a = 1.0 if i == sel else 0.0


func _process(_dt: float) -> void:
	if not open:
		return
	if Game.consume(KEY_ESCAPE):
		toggle()
		return
	if Game.consume(KEY_S) or Game.consume(KEY_DOWN):
		sel = (sel + 1) % ROWS.size()
		Sfx.play("ui", 0.2, 1.3)
		_refresh()
	if Game.consume(KEY_W) or Game.consume(KEY_UP):
		sel = (sel + ROWS.size() - 1) % ROWS.size()
		Sfx.play("ui", 0.2, 1.3)
		_refresh()
	var step := 0.0
	if Game.consume(KEY_D) or Game.consume(KEY_RIGHT):
		step = 0.1
	if Game.consume(KEY_A) or Game.consume(KEY_LEFT):
		step = -0.1
	var r: String = ROWS[sel]
	if step != 0.0 and sel < 3:
		Sfx.set_level(r, snappedf(Sfx.levels[r] + step, 0.1))
		if r == "Voice":
			Sfx.whisper("a", 0.5, 0.4)
		elif r == "Sfx":
			Sfx.play("hit", 0.4, 1.0)
		_refresh()
	if r == "Gfx" and (step != 0.0 or Game.consume(KEY_ENTER) or Game.consume(KEY_KP_ENTER)):
		Game.set_quality((Game.quality + (1 if step <= 0.0 and step == 0.0 else int(signf(step))) + 3) % 3)
		Sfx.play("ui", 0.3, 1.1)
		_refresh()
		return
	if Game.consume(KEY_ENTER) or Game.consume(KEY_KP_ENTER) or Game.consume(KEY_SPACE):
		if r == "save":
			Game.save()
			Fx.toast("Jogo salvo", Color.WHITE)
			Sfx.play("pickup", 0.4, 1.0)
		elif r == "resume":
			toggle()
