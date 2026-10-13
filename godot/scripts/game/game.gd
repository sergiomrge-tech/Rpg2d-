extends Node
## Top-level orchestrator (autoload): world, player, HUD, quests, travel, saves, key queue, CI screenshot tour.

const SAVE_PATH := "user://aetheria_save.json"
const NEW_GAME_START := Vector2(4640, 544)   # meadow across the river, far from Aurora; follow the compass to the Guild

const MAP_TITLES := {
	"village": ["Vila de Aurora", "Capítulo I — A Centelha"],
	"velmoor": ["Floresta de Velmoor", "Capítulo II — Raízes Profanas"],
	"valemont": ["Cidade de Valemont", "Capítulo III — Sombras na Capital"],
	"kharis": ["Deserto de Kharis", "Capítulo IV — O Ferrão do Deserto"],
	"mines": ["Minas de Durnhold", "Capítulo V — O Coração da Forja"],
	"mirewail": ["Pântano de Mirewail", "Capítulo VI — A Rainha do Brejo"],
	"peaks": ["Picos Gelados", "Capítulo VII — A Nascente Congelada"],
	"castle": ["Castelo de Valemont", "Capítulo VIII — O Castelo Tomado"],
	"wastelands": ["Terras Devastadas", "Capítulo IX — Os Quatro Generais"],
	"citadel": ["Cidadela de Malgrath", "Capítulo X — O Rei Demônio"],
}

const GATES := {
	"velmoor": ["rank_e", "O portal rejeita você. A Guilda exige Rank E."],
	"valemont": ["rank_d", "Os guardas barram você. Valemont exige Rank D."],
	"kharis": ["rank_c", "A caravana recusa: o deserto exige Rank C (derrote o Assassino Sombrio)."],
	"mines": ["kharis_done", "O túnel está bloqueado. Ajude Hasim contra o Escorpião primeiro."],
	"mirewail": ["mines_done", "A bruma repele você. Ajude Durnok contra o Golem primeiro."],
	"peaks": ["mirewail_done", "A nevasca é forte demais. Ajude Morgana contra Mirael primeiro."],
	"castle": ["peaks_done", "A estrada para Valemont está bloqueada. Termine a missão nos Picos Gelados primeiro."],
	"wastelands": ["castle_done", "Os portões do castelo estão selados. Fale com Elowen e derrote Vorath."],
	"citadel": ["wastelands_done", "O portão do inferno está selado. Derrote os quatro Generais (Cedric explica)."],
}

var state := GameState.new()
var flags := {}                 # used as a set
var quests := {}
var player: Player
var world: World
var camera: CameraRig
var hud: Hud
var grimoire: Grimoire
var shop: ShopMenu
var skills: SkillsMenu
var board: GuildBoard
var tavern: TavernMenu
var options: OptionsMenu
var marker: ObjectiveMarker
var main: Node2D
var map_name := "village"
var ci_dir := ""
var class_shots := false
var ui_smoke := false
var touch_mode := false
var touch_move := Vector2.ZERO
var touch_run := false
var touch: TouchControls
var menu: MainMenu
var class_select: ClassSelect
var in_menu := false

var _time := 0.0
var _int_npc := {}                # npc id -> interior map (data/interiors.json)
var show_fps := false
var wet := 0.0                     # 0 dry .. 1 soaked: rain wets the hero, rooms and time dry them
var weather := 0.0                 # 0 clear .. 1 heavy rain (eased toward weather_target)
var weather_target := 0.0
var weather_auto := true
var _wx_timer := 240.0
var quality_auto := true           # no explicit choice saved yet: the game lowers the tier by itself if the frame rate stays low
var _fps_acc := 0.0
var _fps_n := 0
var quality := 2                 # graphics: 0 low (no cast shadows / wind / water fx / room lights), 1 medium, 2 high
var daily := {"day": -1, "quests": [], "bonus": false}   # guild daily board (see DailyBoard)
var clock := 0.0               # world clock in seconds (day length = World.DAY_LENGTH); starts at midday
var _hit_until := 0
var _slowmo := false
var _ts := 1.0
var _travel_cd := 1.0
var _saved_pos := Vector2.ZERO
var _has_saved_pos := false
var _keys := {}                 # key code -> msec of press (negative codes: mouse buttons)
var _bestiary: Array = []
var _bestiary_idx := 0


func _ready() -> void:
	var f_q: FileAccess = FileAccess.open("user://graphics.json", FileAccess.READ) if FileAccess.file_exists("user://graphics.json") else null
	if f_q:
		var qd: Variant = JSON.parse_string(f_q.get_as_text())
		if qd is Dictionary:
			quality = clampi(int(qd.get("quality", 2)), 0, 2)
			quality_auto = bool(qd.get("auto", false))
	var f_int := FileAccess.open("res://data/interiors.json", FileAccess.READ)
	if f_int:
		_int_npc = JSON.parse_string(f_int.get_as_text())
	process_mode = Node.PROCESS_MODE_ALWAYS
	var args := OS.get_cmdline_user_args()
	for i in args.size() - 1:
		if args[i] == "-ciShots":
			ci_dir = args[i + 1]
		if args[i] == "-classShots":
			ci_dir = args[i + 1]
			class_shots = true
	ui_smoke = "-uiSmoke" in args
	touch_mode = OS.has_feature("mobile") or "-touch" in args
	if not FileAccess.file_exists("user://graphics.json") and OS.has_feature("mobile"):
		quality = 1                    # phones start on Medium
	if touch_mode:
		get_window().content_scale_aspect = Window.CONTENT_SCALE_ASPECT_KEEP   # keep 16:9 layout on tall/wide phones


func time() -> float:
	return _time


# ------------------------------------------------------------------ input queue
func _input(ev: InputEvent) -> void:
	if ev is InputEventKey and ev.pressed and not ev.echo:
		_keys[ev.physical_keycode] = Time.get_ticks_msec()
		_keys[ev.keycode] = Time.get_ticks_msec()
	elif ev is InputEventMouseButton and ev.pressed:
		_keys[-ev.button_index] = Time.get_ticks_msec()


## Virtual key press (touch buttons): queued exactly like a keyboard press.
func press_key(k: int) -> void:
	_keys[k] = Time.get_ticks_msec()


## True once per key press (within 180 ms); removes it from the queue.
func consume(k: int) -> bool:
	if _keys.has(k) and Time.get_ticks_msec() - int(_keys[k]) < 180:
		_keys.erase(k)
		return true
	return false


# ------------------------------------------------------------------ start
func start(m: Node2D) -> void:
	main = m
	if ci_dir == "" and not ui_smoke:
		_load()
	world = World.load_map(map_name)
	main.add_child(world)
	camera = CameraRig.new()
	main.add_child(camera)
	camera.set_world(world)
	var spawn := Vector2(float(world.data["playerX"]), float(world.data["playerY"]))
	if _has_saved_pos and world.bounds.has_point(_saved_pos):
		spawn = _saved_pos
	elif not flags.has("prologue") and map_name == "village":
		spawn = NEW_GAME_START
	player = Player.spawn(spawn, state)
	world.spawn_actors()
	if flags.has("sylra_joined"):
		Companion.spawn(spawn + Vector2.LEFT * 64.0)
	camera.target = player
	camera.snap()
	marker = ObjectiveMarker.new()
	main.add_child(marker)
	hud = Hud.new()
	main.add_child(hud)
	grimoire = Grimoire.new()
	hud.add_child(grimoire)
	grimoire.setup(hud)
	shop = ShopMenu.new()
	hud.add_child(shop)
	shop.setup(hud)
	skills = SkillsMenu.new()
	hud.add_child(skills)
	skills.setup(hud)
	board = GuildBoard.new()
	hud.add_child(board)
	board.setup(hud)
	tavern = TavernMenu.new()
	hud.add_child(tavern)
	tavern.setup(hud)
	options = OptionsMenu.new()
	hud.add_child(options)
	options.setup(hud)
	for k in COMPLETE_FLAGS:
		if flags.has(k):
			_announced[k] = true
	_announced["__init"] = true
	if touch_mode:
		touch = TouchControls.new()
		hud.add_child(touch)
		touch.setup(hud)
	# Lower environmental hiss: leave room for the new soft-flute soundtrack.
	Sfx.region_ambience(map_name)
	Music.play(map_name)
	if ui_smoke:
		_ui_smoke_test()
		return
	if class_shots:
		_ci_class_shots()
		return
	if ci_dir != "":
		_ci_shots()
		return
	menu = MainMenu.new()
	hud.root.add_child(menu)     # keep the menu under the options/touch layers' z-order handling
	menu.setup(hud, FileAccess.file_exists(SAVE_PATH) or FileAccess.file_exists(SAVE_PATH + ".bak"), flags.has("game_complete"))
	menu.on_continue = _begin
	menu.on_new = _open_class_select
	menu.on_ngplus = new_game_plus
	player.input_locked = true
	if false:
		player.input_locked = true
		hud.show_dialogue(Story.prologue, func():
			flags["prologue"] = true
			player.input_locked = false
			hud.banner("Vila de Aurora", "Capítulo I — A Centelha")
			save())
	else:
		var t: Array = MAP_TITLES.get(map_name, ["", ""])
		hud.banner(t[0], "Rank " + state.guild_rank)


## Continue: the loaded save is already in memory; just start playing (prologue only if never seen).
func _begin() -> void:
	if not flags.has("prologue"):
		player.input_locked = true
		hud.show_dialogue(Story.prologue, func():
			flags["prologue"] = true
			player.input_locked = false
			hud.banner("Vila de Aurora", "Capítulo I — A Centelha")
			save())
	else:
		player.input_locked = false
		var t: Array = MAP_TITLES.get(map_name, ["", ""])
		hud.banner(t[0], "Rank " + state.guild_rank)


## New game: the chosen class is locked in before the story begins.
func _open_class_select() -> void:
	player.input_locked = true
	class_select = ClassSelect.new()
	hud.add_child(class_select)
	class_select.setup(hud, _start_selected_class, _cancel_class_select)


func _cancel_class_select() -> void:
	class_select = null
	menu.reopen()


func _start_selected_class(class_id: String) -> void:
	class_select = null
	new_game(class_id)


## Novo Jogo+: keep level, gear, bag and forge levels; the story, quests and map restart with tougher monsters.
func new_game_plus() -> void:
	state.ng_plus += 1
	for old_pet in SpiritPet.active_pets.duplicate():
		if is_instance_valid(old_pet):
			old_pet.queue_free()
	SpiritPet.active_pets.clear()
	flags.clear()
	quests.clear()
	flags["prologue"] = true
	clock = 0.0
	_announced = {"__init": true}
	player.anim.setup(HeroClasses.sheet_for(state.class_id))
	player.anim.play("idle", true)
	_load_map_now("village")
	world.spawn_actors()
	player.max_hp = state.hp_max()
	player.hp = player.max_hp
	player.mp = state.max_mp
	player.dead = false
	player.global_position = NEW_GAME_START
	player.face(Util.Face.DOWN)
	if Companion.I:
		Companion.I.queue_free()
	camera.snap()
	_travel_cd = 3.0
	player.input_locked = false
	hud.banner("Novo Jogo+ %d" % state.ng_plus, "Monstros mais fortes · tesouros melhores")
	save()


## New game: wipe progress, apply class restrictions, then play the prologue.
func new_game(class_id: String = "warrior") -> void:
	state.from_dict(GameState.new().to_dict())
	HeroClasses.apply_new_game(state, class_id)
	# Player was spawned before the menu, so switch its real sprite atlas
	# immediately on confirmation (not only when loading a saved game).
	player.anim.setup(HeroClasses.sheet_for(state.class_id))
	player.anim.play("idle", true)
	# New Game must not retain temporary summons from the previous save.
	for old_pet in SpiritPet.active_pets.duplicate():
		if is_instance_valid(old_pet):
			old_pet.queue_free()
	SpiritPet.active_pets.clear()
	flags.clear()
	quests.clear()
	clock = 0.0
	_announced = {"__init": true}
	_load_map_now("village")
	world.spawn_actors()
	player.max_hp = state.hp_max()
	player.hp = player.max_hp
	player.mp = state.max_mp
	player.dead = false
	player.global_position = NEW_GAME_START
	player.face(Util.Face.DOWN)
	if Companion.I:
		Companion.I.queue_free()
	camera.snap()
	_travel_cd = 3.0
	_begin()


func is_night() -> bool:
	return world != null and world.night_amount() > 0.72


## Day phase for the HUD: Dia / Entardecer / Noite / Amanhecer (caves and fortresses are always "Interior").
func phase_name() -> String:
	if world == null or not world._outdoor:
		return "Interior"
	var f := fmod(clock / World.DAY_LENGTH, 1.0)
	var n := world.night_amount()
	if n < 0.25:
		return "Dia"
	if n > 0.75:
		return "Noite"
	return "Entardecer" if f < 0.5 else "Amanhecer"


## Rain comes and goes on its own (outdoor maps only); tests pin it by turning weather_auto off.
func _update_weather(dt: float) -> void:
	if weather_auto and ci_dir == "" and not get_tree().paused:
		_wx_timer -= dt
		if _wx_timer <= 0.0:
			if weather_target > 0.0:
				weather_target = 0.0
				_wx_timer = randf_range(220.0, 480.0)
			else:
				weather_target = randf_range(0.6, 1.0)
				_wx_timer = randf_range(70.0, 150.0)
	weather = move_toward(weather, weather_target, dt * 0.12)
	var was_wet := wet
	if world != null and is_instance_valid(world) and player != null:
		var indoors: bool = bool(world.data.get("interior", false))
		if not indoors and weather > 0.3 and str(world.data.get("name", "")) in World.RAIN_MAPS:
			wet = minf(1.0, wet + dt / 22.0)
		else:
			wet = maxf(0.0, wet - dt / (5.0 if indoors else 16.0))
		player.anim.self_modulate = Color.WHITE.lerp(Color(0.68, 0.78, 0.95), wet * 0.85)
	if was_wet < 0.8 and wet >= 0.8:
		Fx.toast("Você está ensopado… procure um abrigo com lareira", Color(0.75, 0.88, 1.0))
	elif was_wet > 0.0 and wet <= 0.0 and was_wet > 0.02:
		Fx.toast("Você secou", Color(1, 0.9, 0.7))


## Fraction of the day (0 = noon, 0.5 = midnight).
func day_phase() -> float:
	return fposmod(clock / World.DAY_LENGTH, 1.0)


func _auto_quality(dt: float) -> void:
	if not quality_auto or ci_dir != "" or quality == 0 or get_tree().paused or world == null:
		return
	_fps_acc += dt
	_fps_n += 1
	if _fps_acc < 8.0:
		return
	var fps := float(_fps_n) / _fps_acc * Engine.time_scale
	_fps_acc = 0.0
	_fps_n = 0
	if fps < 38.0:
		set_quality(quality - 1, false)
		Fx.toast("Desempenho baixo: gráficos ajustados para %s" % ["Baixa", "Média"][quality], Color(1, 0.9, 0.6))


func _process(dt: float) -> void:
	_auto_quality(dt)
	_update_weather(dt)
	_time += dt
	if not get_tree().paused:
		clock += dt
	var want := 1.0
	if Time.get_ticks_msec() < _hit_until:
		want = 0.05
	elif _slowmo:
		want = 0.35
	if want != _ts:
		_ts = want
		Engine.time_scale = want
	if player == null:
		return
	# Modal-first input: never consume Esc/Tab before the open overlay sees it.
	# These keys used to be stolen from Grimoire/Options during pause.
	if not in_menu and not grimoire.open and not shop.open and not skills.open and not board.open and not tavern.open and not options.open and not hud.in_dialogue() and not hud.in_credits() and not player.dead and consume(KEY_ESCAPE):
		options.toggle()
	if not in_menu and not options.open and not grimoire.open and not shop.open and not skills.open and not board.open and not tavern.open and not hud.in_dialogue() and not player.dead and not player.input_locked and consume(KEY_TAB):
		grimoire.toggle()
	if not in_menu and not options.open and not grimoire.open and not shop.open and not skills.open and not board.open and not tavern.open and not hud.in_dialogue() and not player.dead and not player.input_locked and consume(KEY_P):
		skills.toggle()
	_travel_cd -= dt
	Music.play("boss" if hud.boss_bar.visible else map_name)
	_update_objective()
	marker.refresh(obj_active and not hud.in_dialogue() and not grimoire.open, obj_pos, obj_kind)
	_watch_quest_flags()
	if not player.dead and _travel_cd <= 0.0:
		var ex := world.exit_at(player.global_position)
		if not ex.is_empty():
			travel(ex["to"])
	if consume(KEY_F9) and not player.dead:
		_spawn_bestiary()
	if consume(KEY_F5):
		save()
		Fx.toast("Jogo salvo", Color.WHITE)


func save_settings_note() -> void:
	pass   # volumes are saved as they change (Sfx.set_level)


## How battered the Valemont wall is (0 intact .. 5 breached); follows the story and is mended after the Demon King falls.
func wall_stage() -> int:
	if flags.has("game_complete"):
		return 1
	var done := 0
	for r in Story.regions:
		if flags.has(r["done"]):
			done += 1
	if done >= 6 or flags.has("lumia_blessed"):
		return 5
	if done >= 4:
		return 4
	if done >= 2:
		return 3
	if flags.has("rank_c"):
		return 2
	return 1 if flags.has("val_started") else 0


func set_quality(q: int, user_choice := true) -> void:
	quality = clampi(q, 0, 2)
	if user_choice:
		quality_auto = false
	var f := FileAccess.open("user://graphics.json", FileAccess.WRITE)
	if f:
		f.store_string(JSON.stringify({"quality": quality, "auto": quality_auto}))
	if world != null and is_instance_valid(world):
		world.apply_quality()


## Tavern rest: pay, restore HP/MP, save the game.
func rest(cost: int) -> void:
	state.gold -= cost
	player.hp = player.max_hp
	player.mp = state.max_mp
	Fx.heal(player.pos())
	Sfx.play("potion", 0.5, 0.9)
	save()


func hit_stop(t: float) -> void:
	_hit_until = maxi(_hit_until, Time.get_ticks_msec() + int(t * 1000.0))


func _spawn_bestiary() -> void:
	if _bestiary.is_empty():
		_bestiary = Data.demons.keys()
		_bestiary.sort()
	var id: String = _bestiary[_bestiary_idx % _bestiary.size()]
	_bestiary_idx += 1
	var e := Enemy.spawn(id, player.global_position + Util.facing_vec(player.facing) * 3.5 * 64.0, maxi(1, state.level))
	Fx.toast("Bestiário %d/%d: %s" % [_bestiary_idx, _bestiary.size(), e.def["name"]], Color(1, 0.9, 0.6), e.global_position + Vector2.UP * 2.8 * 64.0)


# ------------------------------------------------------------------ travel
## Clock-based night (works inside buildings, where the world itself is not "outdoor").
func clock_night() -> bool:
	return 0.5 - 0.5 * cos(clock / World.DAY_LENGTH * TAU) > 0.72


func travel(to: String) -> void:
	if to.begins_with("int_") and clock_night():
		var idata = Sheets.read_json("Maps/" + to)
		if idata != null and idata.get("closed_at_night", false):
			Fx.toast("Fechado à noite — volte pela manhã", Color(1, 0.88, 0.55))
			_travel_cd = 2.0
			player.global_position += Vector2.DOWN * 1.3 * 64.0
			return
	if GATES.has(to) and not flags.has(GATES[to][0]):
		Fx.toast(GATES[to][1], Color(1, 0.88, 0.55))
		_travel_cd = 2.0
		var centre := world.bounds.get_center()
		player.global_position += (centre - player.global_position).normalized() * 1.6 * 64.0
		return
	var from := map_name
	map_name = to
	var old := world
	var comp: Node2D = Companion.I
	old.entities.remove_child(player)
	if comp:
		old.entities.remove_child(comp)
	main.remove_child(old)
	old.free()
	world = World.load_map(to)
	main.add_child(world)
	camera.set_world(world)
	var at := Vector2(float(world.data["playerX"]), float(world.data["playerY"]))
	for e in world.data["exits"]:
		if e["to"] == from:
			var ep := Vector2(float(e["x"]), float(e["y"]))
			at = ep + (world.bounds.get_center() - ep).normalized() * 2.4 * 64.0
			if e.has("ax"):
				at = Vector2(float(e["ax"]), float(e["ay"]))
	world.add_entity(player, at)
	if comp:
		world.add_entity(comp, at + Vector2.LEFT * 64.0)
	world.spawn_actors()
	camera.snap()
	_travel_cd = 1.5
	Sfx.region_ambience(to)
	if MAP_TITLES.has(to):
		hud.banner(MAP_TITLES[to][0], MAP_TITLES[to][1])
	elif world.data.get("interior", false):
		hud.banner(str(world.data.get("title", "")), "Interior")
	save()


# ------------------------------------------------------------------ dialogue / npcs
func interact(p: Player) -> void:
	if hud.in_dialogue():
		return
	var best: Npc = null
	var bd := 2.2 * 64.0
	for n in world.entities.get_children():
		if n is Npc and n.visible:
			var d: float = (n.global_position - p.global_position).length()
			if d < bd:
				bd = d
				best = n
	var fur: Furniture = null
	var fd := 2.1 * 64.0
	for n in world.entities.get_children():
		if n is Furniture and n.act != "":
			var fp := Furniture.footprint(n.kind, n.w) * 64.0
			var c: Vector2 = n.global_position + Vector2(0, -fp.y * 0.5)
			var dd := maxf(0.0, absf(c.x - p.global_position.x) - fp.x * 0.5) + absf(c.y - p.global_position.y) * 0.8
			if dd < fd:
				fd = dd
				fur = n
	if fur != null and (best == null or fd < bd):
		_furniture_act(fur)
		return
	if best == null:
		return
	var npc := best
	var was_member := flags.has("guild_joined")
	npc.talking = true
	p.input_locked = true
	p.velocity = Vector2.ZERO
	hud.show_dialogue(Story.talk(npc.id), func():
		npc.talking = false
		p.input_locked = false
		if (npc.id == "receptionist" or npc.id == "guildmaster") and was_member and not board.open:
			board.open_board()
		if npc.id in ["blacksmith", "smith_v", "shopkeeper", "armorer"] and not shop.open:
			shop.open_for(npc.id)
		if npc.id in ["tavern_keeper", "inn_aurora"] and not tavern.open:
			tavern.open_for("inn")
		if npc.id == "baker" and not tavern.open:
			tavern.open_for("bakery")
		if npc.id == "guard_captain" and (flags.has("game_complete") or state.ng_plus > 0) and not Abyss.active:
			Abyss.start()
		if npc.id == "sylra" and flags.has("sylra_joined") and Companion.I == null:
			Companion.spawn(npc.global_position)
			npc.queue_free()
			hud.banner("Sylra entrou no grupo", "Arqueira de Velmoor")
		save())


func _furniture_act(fu: Furniture) -> void:
	match fu.act:
		"board":
			if flags.has("guild_joined"):
				board.open_board()
			else:
				Fx.toast("Registre-se na Guilda falando com a recepção", Color(1, 0.88, 0.55))
		"rooms":
			tavern.open_for("inn", 0)


func cache_count() -> int:
	var n := 0
	for k in flags:
		if str(k).begins_with("cache_"):
			n += 1
	return n


## Short progress lines for the active side quests (HUD, under the main objective).
func side_lines() -> Array:
	var out: Array = []
	if flags.has("sq_horns_on") and not flags.has("sq_horns_done"):
		out.append("Marta: Chifres %d/3" % mini(state.count("imp_horn"), 3))
	if flags.has("sq_forge_on") and not flags.has("sq_forge_done"):
		out.append("Hargrim: Brasas %d/4" % mini(state.count("hell_ember"), 4))
	if flags.has("sq_herbs_on") and not flags.has("sq_herbs_done"):
		out.append("Dorna: Insetoides %d/6" % mini(quest_progress("q_insects"), 6))
	if flags.has("sq_mead_on") and not flags.has("sq_mead_done"):
		out.append("Levar o hidromel ao Capitão Brandt")
	if flags.has("sq_relics_on") and not flags.has("sq_relics_done"):
		out.append("Orrin: Baús %d/3" % mini(cache_count() - quest_progress("q_relic_base"), 3))
	out.append_array(DailyBoard.lines())
	return out


func start_quest(id: String) -> void:
	if not quests.has(id):
		quests[id] = 0


func quest_progress(id: String) -> int:
	return int(quests.get(id, 0))


## Objective = [headline, detail, map, kind ("npc" | "boss" | "enemy" | ""), id]
func _o(head: String, detail: String, map: String = "", kind: String = "", id: String = "") -> Array:
	if kind == "npc" and _int_npc.has(id):      # that NPC works inside a building
		map = str(_int_npc[id])
	return [head, detail, map, kind, id]


var smith_until := 0.0
var smith_obj: Array = []


## Points the compass at the nearest blacksmith for a while (used by the forge buttons).
func smith_hint() -> void:
	var here := ""
	for n in world.data["npcs"]:
		if n["id"] == "blacksmith" or n["id"] == "smith_v":
			here = str(n["id"])
	if here != "":
		smith_obj = _o("Visite o ferreiro", "forjar e comprar equipamentos", map_name, "npc", here)
	else:
		var to_valemont := map_name in ["valemont", "kharis", "mines", "mirewail", "peaks", "castle", "wastelands", "citadel"]
		smith_obj = _o("Visite o ferreiro de %s" % ("Valemont" if to_valemont else "Aurora"), "forjar e comprar equipamentos",
			"valemont" if to_valemont else "village", "npc", "smith_v" if to_valemont else "blacksmith")
	smith_until = time() + 40.0
	hud.banner("Ferreiro marcado", "siga a bússola · 40 s")


func objective() -> Array:
	if time() < smith_until:
		return smith_obj
	if not flags.has("guild_joined"):
		return _o("Procure a Guilda dos Aventureiros", "ao norte da praça", "village", "npc", "receptionist")
	if not flags.has("q_imps_done"):
		var n := mini(quest_progress(Story.QUEST_IMPS), Story.QUEST_IMPS_GOAL)
		if n >= Story.QUEST_IMPS_GOAL:
			return _o("Volte à Guilda e fale com Elina", "", "village", "npc", "receptionist")
		return _o("Purgar o Bosque dos Chifres", "Diabretes %d/%d" % [n, Story.QUEST_IMPS_GOAL], "village", "enemy", "imp")
	if not flags.has("grakk_dead"):
		return _o("Derrote Grakk, Chefe dos Diabretes", "sul do Bosque dos Chifres", "village", "boss", "grakk")
	if not flags.has("rank_e"):
		return _o("Volte à Guilda e fale com Elina", "", "village", "npc", "receptionist")
	if not flags.has("sylra_joined"):
		return _o("Entre no portal ao sul do Bosque", "e encontre o santuário élfico de Velmoor", "velmoor", "npc", "sylra")
	if not flags.has("dryad_profane_dead"):
		return _o("Purifique o bosque sagrado", "derrote a Dríade Profanada (sul de Velmoor)", "velmoor", "boss", "dryad_profane")
	if not flags.has("rank_d"):
		return _o("Volte à Guilda de Aurora", "", "village", "npc", "receptionist")
	if not flags.has("val_started"):
		return _o("Viaje a Valemont", "saída leste de Velmoor — fale com o Mestre da Guilda", "valemont", "npc", "guildmaster")
	if not flags.has("assassin_shadow_dead"):
		return _o("Cace o Assassino Sombrio", "beco ao sul de Valemont", "valemont", "boss", "assassin_shadow")
	if not flags.has("rank_c"):
		return _o("Volte ao Mestre Aldric, na Guilda", "", "valemont", "npc", "guildmaster")
	for r in Story.regions:
		if flags.has(r["done"]):
			continue
		if not flags.has(r["start"]):
			return _o("Viaje a %s" % r["title"], "fale com %s" % Story.name_of(r["npc"]), r["map"], "npc", r["npc"])
		if not Story.region_all_dead(r):
			var next_boss := ""
			for bid in String(r["boss"]).split(","):
				if not flags.has(bid + "_dead"):
					next_boss = bid
					break
			return _o("Derrote %s" % r["bossName"], r["title"], r["map"], "boss", next_boss)
		return _o("Volte a %s" % Story.name_of(r["npc"]), r["title"], r["map"], "npc", r["npc"])
	if flags.has("game_complete"):
		return _o("Desafie o Abismo", "fale com o Capitão Brandt, em Valemont · ou explore livremente", "valemont", "npc", "guard_captain")
	if not flags.has("lumia_blessed"):
		return _o("Entre na Cidadela de Malgrath", "leste das Terras Devastadas — fale com Lumia", "citadel", "npc", "lumia")
	return _o("Derrote Malgrath, o Rei Demônio", "salão do trono, ao norte da Cidadela", "citadel", "boss", "malgrath")


func quest_line() -> String:
	var o := objective()
	return o[0] + ("\n" + o[1] if o[1] != "" else "")


# ---- objective guidance: world position of the current target (or the exit leading toward its map)
var obj_active := false
var obj_pos := Vector2.ZERO
var obj_kind := ""        # "target" | "exit"
var obj_dist := 0.0
var _graph := {}


func _exits_of(m: String) -> Array:
	if not _graph.has(m):
		var d = Sheets.read_json("Maps/" + m)
		_graph[m] = d["exits"] if d else []
	return _graph[m]


## First hop (exit dictionary) on the shortest path from `from` to `to`, or {}.
func _next_hop(from: String, to: String) -> Dictionary:
	var prev := {from: null}
	var q := [from]
	while not q.is_empty():
		var cur: String = q.pop_front()
		if cur == to:
			break
		for e in _exits_of(cur):
			if not prev.has(e["to"]):
				prev[e["to"]] = [cur, e]
				q.append(e["to"])
	if not prev.has(to) or to == from:
		return {}
	var node: String = to
	var hop := {}
	while prev[node] != null:
		hop = prev[node][1]
		node = prev[node][0]
	return hop


func _update_objective() -> void:
	obj_active = false
	var o := objective()
	if o[2] == "" or player == null or player.dead:
		return
	if o[2] != map_name:
		var hop := _next_hop(map_name, o[2])
		if hop.is_empty():
			return
		obj_pos = Vector2(float(hop["x"]), float(hop["y"]))
		obj_kind = "exit"
		obj_active = true
	else:
		var best := INF
		if o[3] == "npc":
			for n in world.entities.get_children():
				if n is Npc and n.id == o[4]:
					obj_pos = n.global_position
					best = 0.0
		else:
			for e in Enemy.all:
				if is_instance_valid(e) and not e.dead and e.def["id"] == o[4]:
					var d := e.global_position.distance_to(player.global_position)
					if d < best:
						best = d
						obj_pos = e.global_position
		if best == INF:
			return
		obj_kind = "target"
		obj_active = true
	obj_dist = obj_pos.distance_to(player.global_position)


const COMPLETE_FLAGS := {
	"q_imps_done": "Os diabretes recuaram", "rank_e": "Promovido ao Rank E", "dryad_profane_dead": "A floresta respira de novo",
	"rank_d": "Promovido ao Rank D", "rank_c": "Promovido ao Rank C", "kharis_done": "Rank B conquistado", "mines_done": "As forjas ardem de novo",
	"mirewail_done": "Rank A conquistado", "peaks_done": "A nascente descongelou", "castle_done": "O castelo foi libertado",
	"wastelands_done": "Rank S conquistado",
}
var _announced := {}


func _watch_quest_flags() -> void:
	for k in COMPLETE_FLAGS:
		if flags.has(k) and not _announced.has(k):
			_announced[k] = true
			if _announced.has("__init"):
				hud.quest_complete(COMPLETE_FLAGS[k])


# ------------------------------------------------------------------ combat callbacks
var _proc_cd := 0.0


## Set powers that trigger when the hero (or an ally) lands a hit.
func set_proc(e: Enemy) -> void:
	if player == null or time() < _proc_cd:
		return
	var sp := state.set_power()
	if sp == "bolt" and randf() < 0.12:
		_proc_cd = time() + 1.5
		AreaSpell.strike("storm", e.global_position, state.total_atk() * 1.2 + state.total_mag() * 0.8)
	elif sp == "meteor" and randf() < 0.10:
		_proc_cd = time() + 2.5
		AreaSpell.strike("meteor", e.global_position, state.total_atk() * 1.4 + state.total_mag() * 1.4)


func on_enemy_killed(e: Enemy) -> void:
	if quests.has(Story.QUEST_IMPS) and e.def["id"] == "imp":
		quests[Story.QUEST_IMPS] = int(quests[Story.QUEST_IMPS]) + 1
	if quests.has("q_insects") and String(e.def.get("behavior", "")) != "" and not e.def["boss"]:
		quests["q_insects"] = int(quests["q_insects"]) + 1
	if e.def["id"] == "malgrath":
		flags["malgrath_dead"] = true
		save()
		_ending()
		return
	if e.def["boss"] and not e.arena:
		flags[str(e.def["id"]) + "_dead"] = true
		hud.banner(str(e.def["name"]) + " foi derrotado", "Volte à Guilda")
		save()
	var sp := state.set_power()
	var xp := roundi(float(e.def["xp"]) * Data.hp_scale(e.level) * (1.1 if sp == "xp" else 1.0) * state.xp_mult())
	if sp == "heal" and not player.dead:
		player.hp = minf(state.hp_max(), player.hp + state.hp_max() * 0.04)
		Fx.heal(player.pos())
	if state.class_id == "mage" and not player.dead:
		player.mp = minf(state.max_mp, player.mp + state.max_mp * float(SkillTree.passive_v("mage", state.level)[0]) / 100.0)
	Fx.toast("+%d EXP" % xp, Color(0.75, 0.95, 1.0), e.global_position + Vector2.UP * 2.6 * 64.0)
	award_xp(xp)
	DailyBoard.on_kill(e)


func award_xp(xp: int) -> void:
	if state.gain_xp(xp):
		player.max_hp = state.hp_max()
		player.hp = player.max_hp
		player.mp = state.max_mp
		Fx.heal(player.pos())
		Sfx.play("levelup", 0.6, 1.0)
		hud.banner("Nível %d" % state.level, "+%d atributos · +1 habilidade — abra com P" % SkillTree.ATTR_PER_LEVEL)


func _wait(sec: float) -> void:
	await get_tree().create_timer(sec, true, false, true).timeout


func _ending() -> void:
	player.input_locked = true
	player.scripted_move = Vector2.ZERO
	_slowmo = true
	await _wait(0.8)    # real time: 2.2 s of slow motion at 0.35x
	_slowmo = false
	for e in Enemy.all.duplicate():
		if is_instance_valid(e) and not e.dead:
			e.hurt(99999, e.global_position + Vector2.DOWN, 0, 999)
	hud.show_dialogue(Story.ending, func():
		hud.show_credits(Story.credits, func():
			flags["game_complete"] = true
			player.input_locked = false
			hud.banner("Aetheria em paz", "Continue explorando — F5 salva")
			save()))


func on_player_died() -> void:
	await _wait(1.6)
	hud.banner("Você caiu", "A deusa Lumia o traz de volta... mas metade do ouro ficou para trás")
	await _wait(1.8)
	state.gold /= 2
	player.revive(Vector2(float(world.data["playerX"]), float(world.data["playerY"])))
	camera.snap()
	world.respawn_enemies()
	save()


# ------------------------------------------------------------------ fast Godot native regression (no mockups)
## Launch with -- -uiSmoke -touch. Exercises actual dialogue/UI/touch input.
func _ui_smoke_test() -> void:
	if touch == null:
		push_error("[ui-smoke] touch controls missing")
		get_tree().quit(1)
		return
	# Opening cutscene: nothing playable is on screen yet.
	player.input_locked = true
	hud.show_dialogue(Story.prologue, Callable())
	await _wait(0.12)
	if touch.layer.visible or touch.game_buttons.visible or touch.stick_base.visible:
		push_error("[ui-smoke] gameplay controls visible during prologue")
		get_tree().quit(1)
		return
	print("[ui-smoke] PASS controls hidden in prologue")
	# Simulate completion without consuming the entire narrative in the test.
	hud._finish_dialogue()
	await _wait(0.62)  # allow the illustrated cutscene fade to finish
	flags["prologue"] = true
	player.input_locked = false
	await _wait(0.09)
	if not touch.layer.visible or not touch.game_buttons.visible or not touch.stick_base.visible:
		push_error("[ui-smoke] controls did not appear after prologue")
		get_tree().quit(1)
		return
	print("[ui-smoke] PASS controls appear when gameplay begins")
	grimoire.toggle()
	await _wait(0.07)
	if not grimoire.open or not touch.menu_pad.visible or not get_tree().paused:
		push_error("[ui-smoke] grimoire did not open with paused touch navigation")
		get_tree().quit(1)
		return
	# Real Godot virtual touch on the X, without emulating a mouse click.
	var ev := InputEventScreenTouch.new()
	ev.index = 23
	ev.pressed = true
	# parse_input_event expects device/window pixels; Godot scales to the
	# logical 1920x1080 canvas before delivering InputEventScreenTouch.
	# Passing global_rect directly here double-scaled the synthetic tap.
	var logical_pos := grimoire.close_button.get_global_rect().get_center()
	ev.position = logical_pos * (Vector2(get_window().size) / Hud.SIZE)
	print("[ui-smoke] dispatch X device touch at ", ev.position, " for canvas rect ", grimoire.close_button.get_global_rect())
	Input.parse_input_event(ev)
	await _wait(0.10)
	print("[ui-smoke] after tap open=", grimoire.open, " paused=", get_tree().paused, " locked=", player.input_locked)
	if grimoire.open or get_tree().paused or player.input_locked:
		push_error("[ui-smoke] X tap failed to close and unpause the book")
		get_tree().quit(1)
		return
	print("[ui-smoke] PASS X touchscreen closes and unpauses grimoire")
	ev.pressed = false
	Input.parse_input_event(ev)
	grimoire.toggle()
	press_key(KEY_ESCAPE)
	await _wait(0.10)
	if grimoire.open or get_tree().paused:
		push_error("[ui-smoke] Escape key swallowed while book open")
		get_tree().quit(1)
		return
	print("[ui-smoke] PASS Escape closes book")
	grimoire.toggle()
	press_key(KEY_TAB)
	await _wait(0.10)
	if grimoire.open or get_tree().paused:
		push_error("[ui-smoke] Tab key swallowed while book open")
		get_tree().quit(1)
		return
	print("[ui-smoke] PASS Tab closes book")
	# Subsequent cinematic dialogues must also hide controls.
	player.input_locked = true
	hud.show_dialogue(Story.prologue, Callable())
	await _wait(0.06)
	if touch.layer.visible:
		push_error("[ui-smoke] controls visible during later cinematic")
		get_tree().quit(1)
		return
	hud._finish_dialogue()
	print("[ui-smoke] PASS cutscenes hide controls after prologue")
	# Gameplay regression: zero-valued legacy stamina must NEVER prevent
	# running, consecutive melee combos, or dodge rolls.
	player.input_locked = false
	player.gs.max_st = 0.0
	for i in 16:
		player._to_free()
		player._try_attack()
		if player.state != Player.St.ATTACK:
			push_error("[ui-smoke] attack blocked by removed stamina mechanic")
			get_tree().quit(1)
			return
		player._to_free()
		player._try_roll()
		if player.state != Player.St.ROLL:
			push_error("[ui-smoke] roll blocked by removed stamina mechanic")
			get_tree().quit(1)
			return
	player._to_free()
	print("[ui-smoke] PASS unlimited attack and dodge with zero legacy stamina")
	touch_run = true
	touch_move = Vector2.RIGHT
	await _wait(0.13)
	if player.anim.base != "run":
		push_error("[ui-smoke] sprint is not available without stamina")
		get_tree().quit(1)
		return
	touch_move = Vector2.ZERO
	touch_run = false
	print("[ui-smoke] PASS unlimited sprint animation at zero legacy stamina")
	# Six-class regression: the selection screen is real touch UI and each
	# selected class governs stats, weapon rules and allowed actions.
	var chosen := [""]
	var selector := ClassSelect.new()
	hud.add_child(selector)
	selector.setup(hud, func(id): chosen[0] = id, func(): chosen[0] = "cancel")
	await _wait(.1)
	if selector.cards.size() != 6 or not in_menu or not get_tree().paused:
		push_error("[class-smoke] class selector not displayed after New Game")
		get_tree().quit(1)
		return
	var tap := InputEventScreenTouch.new()
	tap.index = 24
	tap.pressed = true
	tap.position = selector.cards[5].get_global_rect().get_center() * (Vector2(get_window().size) / Hud.SIZE)
	Input.parse_input_event(tap)
	await _wait(.06)
	tap.pressed = false
	Input.parse_input_event(tap)
	if selector.selected != 5:
		push_error("[class-smoke] summoner could not be chosen via touch")
		get_tree().quit(1)
		return
	tap.pressed = true
	tap.position = selector.confirm_button.get_global_rect().get_center() * (Vector2(get_window().size) / Hud.SIZE)
	Input.parse_input_event(tap)
	await _wait(.06)
	tap.pressed = false
	Input.parse_input_event(tap)
	if str(chosen[0]) != "summoner" or in_menu or get_tree().paused:
		push_error("[class-smoke] confirmation did not return chosen class")
		get_tree().quit(1)
		return
	print("[class-smoke] PASS touchscreen select and confirm without starting gameplay")
	var legacy := GameState.new()
	legacy.from_dict({"level": 3, "atk": 18.0})
	if legacy.class_id != "warrior":
		push_error("[class-smoke] existing save class was not preserved")
		get_tree().quit(1)
		return
	for id in HeroClasses.ORDER:
		var trial := GameState.new()
		HeroClasses.apply_new_game(trial, id)
		player.gs = trial
		player.mp = trial.max_mp
		player.hp = trial.hp_max()
		player.input_locked = false
		# Switch the REAL production sprite rig as the class changes.
		# Every clip must exist, with a non-empty texture in all three views.
		player.anim.setup(HeroClasses.sheet_for(id))
		player.anim.play("idle", true)
		if player.anim.sheet == null or player.anim.texture == null:
			push_error("[class-smoke] in-game class sprite failed to load: " + id)
			get_tree().quit(1)
			return
		for facing_dir in [Util.Face.DOWN, Util.Face.UP, Util.Face.RIGHT]:
			player.anim.set_facing(facing_dir)
			for track in ["idle", "walk", "run", "attack1", "cast", "roll", "hurt", "death"]:
				player.anim.play(track, true)
				if player.anim.texture == null or player.anim.current == "":
					push_error("[class-smoke] missing directional frame: " + id + " / " + track)
					get_tree().quit(1)
					return
		player.anim.set_facing(Util.Face.DOWN)
		player.anim.play("idle", true)
		# Class switches here are test-only. Reset cooldowns that would
		# never carry across separately created new-game characters.
		player.special_cd = 0.0
		player.special_strike = false
		player._to_free()
		if trial.class_id != id or trial.to_dict()["class_id"] != id:
			push_error("[class-smoke] class not applied or saved: " + id)
			get_tree().quit(1)
			return
		for weapon_id in ["rusty_sword", "hunter_bow", "twin_daggers"]:
			var weapon: Dictionary = Data.items[weapon_id]
			var expected := str(HeroClasses.info(id)["weapon"]) == str(weapon.get("weapon_type", "sword"))
			if HeroClasses.can_equip(id, weapon) != expected:
				push_error("[class-smoke] wrong equipment restriction: " + id + "/" + weapon_id)
				get_tree().quit(1)
				return
		player._try_attack()
		var expected_attack: int = Player.St.FREE if id == "summoner" else (Player.St.CAST if id in ["mage", "archer"] else Player.St.ATTACK)
		if player.state != expected_attack:
			push_error("[class-smoke] invalid primary combat: " + id)
			get_tree().quit(1)
			return
		player._to_free()
		player._try_cast()
		var expected_skill: int = Player.St.ATTACK if id in ["warrior", "assassin"] else Player.St.CAST
		if player.state != expected_skill:
			push_error("[class-smoke] invalid skill channel: " + id)
			get_tree().quit(1)
			return
		if id == "summoner":
			player._on_anim_hit("cast")
			if SpiritPet.count_for(player) != 1:
				push_error("[class-smoke] summoner skill did not create a real AI pet")
				get_tree().quit(1)
				return
			var real_pet: SpiritPet = SpiritPet.active_pets.back()
			if real_pet == null or real_pet.visual == null or real_pet.visual.sheet == null or real_pet.visual.texture == null:
				push_error("[class-smoke] bespoke animated pet asset not loaded")
				get_tree().quit(1)
				return
			for view in [Util.Face.DOWN, Util.Face.UP, Util.Face.RIGHT]:
				real_pet.visual.set_facing(view)
				real_pet.visual.play("cast", true)
				if real_pet.visual.texture == null:
					push_error("[class-smoke] pet spell frame missing direction")
					get_tree().quit(1)
					return
			real_pet.visual.set_facing(Util.Face.DOWN)
			real_pet.visual.play("idle", true)
			player._to_free()
			player._try_attack()
			if player.state != Player.St.CAST:
				push_error("[class-smoke] summoner cannot command pet")
				get_tree().quit(1)
				return
		player._to_free()
	player.gs = state
	for pet in SpiritPet.active_pets.duplicate():
		if is_instance_valid(pet):
			pet.queue_free()
	print("[class-smoke] PASS six distinct classes, restrictions, stats, save and pet AI")
	print("[ui-smoke] PASS all tests")
	get_tree().quit(0)


# ------------------------------------------------------------------ save / load
func save() -> void:
	if ci_dir != "":
		return
	var d := {"state": state.to_dict(), "flags": flags.keys(), "quests": quests, "map": map_name, "clock": clock, "daily": daily}
	if player:
		d["px"] = player.global_position.x
		d["py"] = player.global_position.y
	var text := JSON.stringify(d)
	# write to a temp file first, validate it, keep the previous save as .bak, then promote
	var tmp := SAVE_PATH + ".tmp"
	var f := FileAccess.open(tmp, FileAccess.WRITE)
	if f == null:
		push_warning("save failed")
		return
	f.store_string(text)
	f.close()
	if _read_save(tmp).is_empty():
		push_warning("save validation failed; keeping previous save")
		DirAccess.remove_absolute(tmp)
		return
	if FileAccess.file_exists(SAVE_PATH):
		DirAccess.rename_absolute(SAVE_PATH, SAVE_PATH + ".bak")
	DirAccess.rename_absolute(tmp, SAVE_PATH)


func _read_save(path: String) -> Dictionary:
	if not FileAccess.file_exists(path):
		return {}
	var f := FileAccess.open(path, FileAccess.READ)
	if f == null:
		return {}
	var d = JSON.parse_string(f.get_as_text())
	if typeof(d) != TYPE_DICTIONARY or not d.has("state") or typeof(d["state"]) != TYPE_DICTIONARY:
		return {}
	return d


func _load() -> void:
	var d := _read_save(SAVE_PATH)
	if d.is_empty():
		d = _read_save(SAVE_PATH + ".bak")   # main save missing or corrupt: recover the backup
	if d.is_empty():
		return
	state.from_dict(d["state"])
	clock = float(d.get("clock", 0.0))
	daily = DailyBoard.normalise(d.get("daily", {}))
	for k in d.get("flags", []):
		flags[k] = true
	for k in d.get("quests", {}):
		quests[k] = int(d["quests"][k])
	var m: String = d.get("map", "village")
	if ResourceLoader.exists("res://assets/Maps/%s.json" % m):
		map_name = m
		_saved_pos = Vector2(float(d.get("px", 0)), float(d.get("py", 0)))
		_has_saved_pos = d.has("px")


func _notification(what: int) -> void:
	if what == NOTIFICATION_WM_CLOSE_REQUEST or what == NOTIFICATION_APPLICATION_PAUSED:
		save()


# ------------------------------------------------------------------ real Godot class presentation (never mockups)
## -classShots <output_dir>: captures the actual viewport, live actors and real
## ability keyframes for all six class rigs and the original summoned pet.
func _ci_class_shots() -> void:
	# The screenshots come directly from RenderingServer.frame_post_draw.
	# Keep the existing map/camera and true user HUD art intact.
	var selector := ClassSelect.new()
	hud.add_child(selector)
	selector.setup(hud, func(_id): pass, func(): pass)
	await _wait(.40)
	await shot("00_class_selection_in_game")
	selector.close()
	flags["prologue"] = true
	player.input_locked = true
	player.invuln = 60.0
	for foe in Enemy.all.duplicate():
		if is_instance_valid(foe):
			foe.queue_free()
	# Genuine scenic clearing; the original plaza well otherwise covers the
	# character. Camera zoom is screenshot-only, not a gameplay setting.
	player.global_position = Vector2(1664, 2176)
	camera.zoom = Vector2.ONE * 1.9
	camera.snap()
	await _wait(.22)
	for class_id in HeroClasses.ORDER:
		HeroClasses.apply_new_game(state, class_id)
		player.anim.setup(HeroClasses.sheet_for(class_id))
		player.max_hp = state.hp_max()
		player.hp = player.max_hp
		player.mp = state.max_mp
		player.special_cd = 0.0
		player.special_strike = false
		player._to_free()
		player.anim.set_facing(Util.Face.DOWN)
		await _wait(.26)
		await shot("01_" + class_id + "_idle_in_game")
		player._try_cast()
		await _wait(.42)
		await shot("02_" + class_id + "_skill_in_game")
		if class_id == "summoner":
			await _wait(.36)
			if SpiritPet.count_for(player) < 1:
				push_error("[class-shots] summoner failed to create physical animated familiar")
				get_tree().quit(1)
				return
			var pet: SpiritPet = SpiritPet.active_pets.back()
			pet.global_position = player.global_position + Vector2(62,-12)
			await _wait(.36)
			await shot("03_astral_lynx_in_game")
		player._to_free()
	for pet in SpiritPet.active_pets.duplicate():
		if is_instance_valid(pet):
			pet.queue_free()
	print("[class-shots] PASS 6 in-engine hero sprites, 6 real skill screenshots, original spirit.")
	get_tree().quit(0)


# ------------------------------------------------------------------ CI: scripted tour + screenshots
func shot(n: String) -> void:
	await RenderingServer.frame_post_draw
	DirAccess.make_dir_recursive_absolute(ci_dir)
	get_viewport().get_texture().get_image().save_png("%s/%s.png" % [ci_dir, n])
	print("[ci] shot ", n)


func _ci_shots() -> void:
	if "-ciShadows" in OS.get_cmdline_user_args():
		flags["prologue"] = true
		await _ci_shadows()
		print("[ci] done")
		get_tree().quit()
		return
	if "-ciSkillsUI" in OS.get_cmdline_user_args():
		flags["prologue"] = true
		_tour_to("village")
		state.class_id = "warrior"
		state.level = 12
		state.skill_pts = 4
		state.skills = ["0_0", "0_1", "1_0", "2_0", "2_1"]
		state.slots = ["0_1", "0_0", "2_1", ""]
		skills.toggle()
		skills.sel_b = 0
		skills.sel_t = 2
		skills._refresh()
		await _wait(0.5)
		await shot("77_arvore_a")
		skills.sel_b = 2
		skills.sel_t = 1
		skills._refresh()
		await _wait(0.3)
		await shot("77_arvore_b")
		state.evolve("0_1", "a")
		skills.sel_b = 0
		skills.sel_t = 1
		skills._refresh()
		await _wait(0.3)
		await shot("77_arvore_evo")
		skills.toggle()
		state.slots = ["0_1", "0_0", "2_1", "1_0"]
		state.skill_pts = 4
		player.input_locked = false
		player.mp = 99.0
		await _wait(0.5)
		player.skill_cd["r"] = 7.0
		player.skill_cd["g"] = 3.0
		await _wait(0.3)
		await shot("77_toque_slots")
		player._try_skill("v")
		await _wait(0.25)
		await shot("77_efeito_buff")
		options.toggle()
		await _wait(0.4)
		await shot("77_opcoes")
		options.toggle()
		print("[ci] done")
		get_tree().quit()
		return
	if "-ciFx" in OS.get_cmdline_user_args():
		flags["prologue"] = true
		await _ci_fx()
		print("[ci] done")
		get_tree().quit()
		return
	if "-ciBuildings" in OS.get_cmdline_user_args():
		flags["prologue"] = true
		await _ci_buildings()
		print("[ci] done")
		get_tree().quit()
		return
	if "-ciLock" in OS.get_cmdline_user_args():
		flags["prologue"] = true
		await _ci_lock()
		print("[ci] done")
		get_tree().quit()
		return
	if "-ciInteriors" in OS.get_cmdline_user_args():
		state.gold = 2000
		flags["prologue"] = true
		flags["guild_joined"] = true
		await _ci_interiors()
		print("[ci] done")
		get_tree().quit()
		return
	menu = MainMenu.new()
	hud.root.add_child(menu)
	menu.setup(hud, true, true)
	await _wait(0.5)
	await shot("00_menu")
	menu.close()
	var keep := player.global_position
	player.global_position = NEW_GAME_START
	camera.snap()
	await _wait(0.6)
	await shot("00b_new_game_start")
	player.global_position = keep
	camera.snap()
	player.input_locked = true
	hud.banner("Vila de Aurora", "Capítulo I — A Centelha")
	await _wait(1.5)
	await shot("01_village")
	hud.show_dialogue(Story.talk("receptionist"), Callable())
	await _wait(2.5)
	await shot("02_dialogue")
	while hud.in_dialogue():
		hud.advance()
		hud.advance()
		await get_tree().process_frame
	await _wait(0.3)
	await shot("02b_quest_update")
	if touch_mode:
		await _ci_touch()
	grimoire.toggle()
	await _wait(0.5)
	await shot("03_grimoire")
	grimoire.toggle()
	player.global_position = Vector2(39 * 64, 50 * 64)
	camera.snap()
	player.scripted_move = Vector2.DOWN
	await _wait(1.2)
	player.scripted_move = Vector2.ZERO
	await _wait(1.2)
	await shot("04_woods")
	var e := Enemy.nearest(player.global_position, 30.0 * 64.0)
	if e:
		player.global_position = e.global_position + Vector2.UP * 1.3 * 64.0
		camera.snap()
		await _wait(0.8)
	player.ci_attack()
	await _wait(0.12)
	await shot("05_combat")
	await _wait(0.6)
	player.ci_cast()
	await _wait(0.35)
	await shot("06_combat2")
	options.toggle()
	await _wait(0.4)
	await shot("08_options")
	options.toggle()
	hud.quest_complete("Promovido ao Rank E")
	await _wait(0.7)
	await shot("07_quest_complete")
	# a tour of every other map: teleport, wait a beat, shoot
	for m in MAP_TITLES.keys():
		if m == "village":
			continue
		_tour_to(m)
		await _wait(1.0)
		await shot("10_" + m)
		if m == "valemont":
			var cits: Array = []
			var ems := 0
			for n in world.entities.get_children():
				if n is Citizen:
					cits.append([n, n.global_position])
				elif n is AmbientEmitter:
					ems += 1
			await _wait(3.0)
			var moved := 0
			for c in cits:
				if is_instance_valid(c[0]) and (c[0].global_position - c[1]).length() > 20.0:
					moved += 1
			print("[ci] citizens moved ", moved, "/", cits.size(), " emitters ", ems)
			for spot in [["plaza", Vector2(50, 54)], ["taverna", Vector2(68, 51)], ["ferraria", Vector2(33, 52)], ["catedral", Vector2(38, 43)], ["estabulo", Vector2(30, 61)]]:
				player.global_position = spot[1] * 64.0
				camera.snap()
				await _wait(0.6)
				await shot("11_valemont_" + spot[0])
	await _ci_mage()
	await _ci_life()
	await _ci_gear()
	await _ci_endgame()
	await _ci_stats()
	await _ci_passives()
	await _ci_interiors()
	await _ci_lock()
	await _ci_buildings()
	await _ci_insects()
	await _ci_bosses()
	print("[ci] done")
	await _wait(0.3)
	get_tree().quit()


func _tour_to(m: String) -> void:
	_load_map_now(m)
	world.spawn_actors()
	var t: Array = MAP_TITLES.get(m, [str(world.data.get("title", m)), ""])
	hud.banner(t[0], t[1])


func _load_map_now(m: String) -> void:
	var old := world
	old.entities.remove_child(player)
	main.remove_child(old)
	old.free()
	map_name = m
	world = World.load_map(m)
	main.add_child(world)
	camera.set_world(world)
	world.add_entity(player, Vector2(float(world.data["playerX"]), float(world.data["playerY"])))
	camera.snap()


const BOSS_TOUR := [
	["village", "grakk"], ["velmoor", "dryad_profane"], ["valemont", "assassin_shadow"], ["kharis", "scorpion_demon"],
	["mines", "ember_golem"], ["mirewail", "succubus_mirael"], ["peaks", "ice_demon"], ["castle", "vorath"],
	["wastelands", "thornmaw_alpha"], ["citadel", "malgrath"],
]


func _find_boss(id: String) -> Enemy:
	for e in Enemy.all:
		if is_instance_valid(e) and e.def["id"] == id and not e.dead:
			return e
	return null


## Long tour: fights (auto-played) and kills every boss, with Sylra in the party, then the ending.
func _ci_bosses() -> void:
	_travel_cd = 999.0
	for entry in BOSS_TOUR:
		var m: String = entry[0]
		var id: String = entry[1]
		if m != map_name:
			_tour_to(m)
			_travel_cd = 999.0
			await _wait(0.5)
		var boss := _find_boss(id)
		if boss == null:
			# already defeated earlier in the tour (the starting area has fewer monsters now): bring a fresh one
			Enemy.spawn(id, player.global_position + Vector2(4 * 64, 0), 5)
			boss = _find_boss(id)
		if boss == null:
			print("[ci] boss not found ", id)
			continue
		while state.level < boss.level - 1:
			state.gain_xp(Data.xp_to_next(state.level))
		player.max_hp = state.hp_max()
		player.hp = player.max_hp
		player.mp = state.max_mp
		if m == "velmoor":
			flags["sylra_joined"] = true
			if Companion.I == null:
				Companion.spawn(player.global_position)
		player.global_position = boss.global_position + Vector2(0, 3.4 * 64.0)
		if Companion.I:
			Companion.I.global_position = player.global_position + Vector2(-64, 30)
		camera.snap()
		player.input_locked = true
		await _wait(0.9)
		var t := 0.0
		while t < 3.0:
			player.invuln = 99.0
			var to := boss.global_position - player.global_position
			player.scripted_move = to.normalized() if to.length() > 2.2 * 64.0 else Vector2.ZERO
			player.face(Util.facing_from(to, player.facing))
			player.ci_attack()
			if int(t * 2.0) % 3 == 2:
				player.ci_cast()
			await _wait(0.35)
			t += 0.35
		await shot("20_boss_" + id)
		boss.hp = boss.max_hp * 0.3
		boss.hurt(1.0, player.global_position, 0, 0)
		await _wait(0.8)
		await shot("21_boss_phase_" + id)
		player.scripted_move = Vector2.ZERO
		boss.hurt(99999, player.global_position, 0, 999)
		await _wait(1.4)
		if id != "malgrath":
			await shot("22_boss_dead_" + id)
	# ending: dialogue then credits
	await _wait(1.0)
	await shot("30_ending_dialogue")
	var guard := 0
	while hud.in_dialogue() and guard < 200:
		hud.advance()
		hud.advance()
		guard += 1
		if guard == 3:
			await _wait(1.2)
			await shot("31_ending_scene")
		await _wait(0.1)
	await _wait(2.0)
	await shot("32_credits")
	print("[ci] credits visible: ", hud.in_credits())


const INSECTS := ["mantis_reaver", "scarab_brute", "moth_hexer", "termite_burrower", "vespa_lancer", "cicada_screecher", "ant_guard",
	"roach_plaguebearer", "spike_beetle", "dragonfly_skirmisher", "mantis_high_reaper", "scarab_colossus", "moth_oracle", "queen_vespara", "brood_tyrant"]


## Spawns each insectoid next to the (invulnerable) hero in the village square and lets the real AI fight.
func _ci_insects() -> void:
	_tour_to("village")
	_travel_cd = 999.0
	for e in Enemy.all.duplicate():
		e.queue_free()
	player.input_locked = true
	player.global_position = Vector2(2496, 1954)
	camera.snap()
	await _wait(0.5)
	for id in INSECTS:
		var lv := 8
		var e := Enemy.spawn(id, player.global_position + Vector2(4.2 * 64.0, 0), lv)
		var t := 0.0
		var shots := 0
		while t < (6.0 if e.def["boss"] else 3.6) and not e.dead:
			player.invuln = 99.0
			player.hp = player.max_hp
			var to := e.global_position - player.global_position
			player.face(Util.facing_from(to, player.facing))
			await _wait(0.3)
			t += 0.3
			if (t > 2.4 and shots == 0) or (e.def["boss"] and t > 4.8 and shots == 1):
				await shot("40_insect_%s_%d" % [id, shots])
				shots += 1
		e.hurt(99999, player.global_position, 0, 999)
		await _wait(0.4)
		for o in Enemy.all.duplicate():
			if is_instance_valid(o) and o != e:
				o.queue_free()


## Touch test: injects real screen-touch events (window pixels) and checks the stick and buttons react.
func _ci_touch() -> void:
	player.input_locked = false
	var k := float(get_window().size.x) / 1920.0
	var stick := Vector2(270, 800)
	var t0 := InputEventScreenTouch.new()
	t0.index = 3
	t0.pressed = true
	t0.position = (stick + Vector2(30, 0)) * k
	Input.parse_input_event(t0)
	await _wait(0.1)
	var d := InputEventScreenDrag.new()
	d.index = 3
	d.position = (stick + Vector2(130, 0)) * k
	Input.parse_input_event(d)
	await _wait(0.4)
	print("[ci] touch_move after drag right: ", touch_move, " run=", touch_run)
	var p0 := player.global_position
	await _wait(0.6)
	await shot("09_touch_stick")
	print("[ci] hero moved dx=", player.global_position.x - p0.x)
	var t1 := InputEventScreenTouch.new()
	t1.index = 3
	t1.pressed = false
	t1.position = d.position
	Input.parse_input_event(t1)
	await _wait(0.2)
	print("[ci] touch_move after release: ", touch_move)
	var b := InputEventScreenTouch.new()
	b.index = 4
	b.pressed = true
	b.position = Vector2(1700, 800) * k
	Input.parse_input_event(b)
	await _wait(0.15)
	print("[ci] attack button -> player state ", player.state, " (1 = ATTACK)")
	var b2 := InputEventScreenTouch.new()
	b2.index = 4
	b2.pressed = false
	b2.position = b.position
	Input.parse_input_event(b2)
	player.input_locked = true
	player.scripted_move = Vector2.ZERO


## Mage area spells: casts Meteor Rain and Lightning Storm on a pack of demons and reports the damage dealt.
func _ci_mage() -> void:
	_tour_to("village")
	_travel_cd = 999.0
	state.class_id = "mage"
	state.skills = ["0_1", "1_1"]       # Chuva de Meteoros + Tempestade de Raios
	state.slots = ["0_1", "1_1", "", ""]
	state.max_mp = 999.0
	player.mp = 999.0
	player.anim.setup(HeroClasses.sheet_for("mage"))
	player.input_locked = false
	player.invuln = 99.0
	var pack: Array = []
	for i in 7:
		pack.append(Enemy.spawn("imp", Vector2(2496, 3000) + Vector2(randf_range(-150, 150), randf_range(-110, 110)), 8))
	player.global_position = Vector2(2496, 3000) + Vector2(-4.2 * 64.0, 3.4 * 64.0)
	player.face(Util.Face.RIGHT)
	camera.snap()
	await _wait(0.6)
	var hp0 := 0.0
	for e in pack:
		hp0 += e.hp
	player._try_skill("r")
	await _wait(1.6)
	await shot("50_mage_meteor_a")
	await _wait(1.2)
	await shot("51_mage_meteor_b")
	await _wait(1.6)
	var hp1 := 0.0
	var alive := 0
	for e in pack:
		if is_instance_valid(e) and not e.dead:
			hp1 += e.hp
			alive += 1
	print("[ci] meteor rain: pack hp ", roundi(hp0), " -> ", roundi(hp1), " alive ", alive, "/", pack.size())
	var pack2: Array = []
	for e in Enemy.all.duplicate():
		if is_instance_valid(e) and not e.dead:
			e.queue_free()
	for i in 7:
		pack2.append(Enemy.spawn("oni", Vector2(2496, 3000) + Vector2(randf_range(-170, 170), randf_range(-120, 120)), 8))
	player.mp = 999.0
	await _wait(0.5)
	var hp2 := 0.0
	for e in pack2:
		hp2 += e.hp
	player._try_skill("f")
	await _wait(1.5)
	await shot("52_mage_storm_a")
	await _wait(1.0)
	await shot("53_mage_storm_b")
	await _wait(2.4)
	var hp3 := 0.0
	var alive2 := 0
	for e in pack2:
		if is_instance_valid(e) and not e.dead:
			hp3 += e.hp
			alive2 += 1
	print("[ci] lightning storm: pack hp ", roundi(hp2), " -> ", roundi(hp3), " alive ", alive2, "/", pack2.size())
	for e in Enemy.all.duplicate():
		if is_instance_valid(e):
			e.queue_free()
	state.class_id = "warrior"
	player.anim.setup(HeroClasses.sheet_for("warrior"))
	player.input_locked = true


## Side quests and the day/night routine.
func _ci_endgame() -> void:
	var tmp := GameState.new()
	HeroClasses.apply_new_game(tmp, "mage")
	print("[ci] mage starts with: ", tmp.eq_weapon)
	for t in 5:
		for i in 3:
			pass
	var saved_w := state.eq_weapon
	var saved_a := state.eq_armor
	var saved_c := state.eq_charm
	for t in 5:
		state.eq_weapon = "sw_%d" % t
		state.eq_armor = "ar_%d" % t
		state.eq_charm = "ch_%d" % t
		print("[ci] set power tier ", t, ": ", state.set_power())
	state.eq_weapon = "sw_2"
	state.eq_armor = "ar_2"
	state.eq_charm = "ch_2"
	_tour_to("valemont")
	_travel_cd = 999.0
	player.input_locked = false
	smith_hint()
	var ob := objective()
	print("[ci] smith hint: ", ob[0], " / ", ob[2], " / ", ob[4])
	await _wait(0.6)
	await shot("73_ferreiro_bussola")
	smith_until = 0.0
	shop.open_for("smith_v")
	state.gold = 3000
	shop._refresh()
	await _wait(0.4)
	await shot("74_loja_ferreiro")
	var g0 := state.gold
	shop.sel = 1
	shop._buy()
	print("[ci] shop buy: gold ", g0, " -> ", state.gold)
	shop.close()
	flags["game_complete"] = true
	Story.talk("guard_captain")
	Abyss.start()
	await _wait(6.5)
	print("[ci] abyss wave ", Abyss.wave, " alive ", Abyss.alive())
	await shot("75_abismo_onda")
	Abyss.cancel("teste")
	print("[ci] abyss cancelled, alive ", Abyss.alive(), " active ", Abyss.active)
	flags.erase("game_complete")
	state.eq_weapon = saved_w
	state.eq_armor = saved_a
	state.eq_charm = saved_c
	player.input_locked = true


func _ci_gear() -> void:
	var dist := [0, 0, 0, 0, 0]
	for i in 600:
		dist[Loot.rarity_for(8, false)] += 1
	var bd := [0, 0, 0, 0, 0]
	for i in 200:
		bd[Loot.rarity_for(18, true)] += 1
	print("[ci] rarity lv8 mob ", dist, " lv18 boss ", bd)
	var bad := 0
	for i in 300:
		var id := Loot.roll_gear(10, i % 2 == 0)
		if id == "" or not Data.items.has(id):
			bad += 1
	print("[ci] gear rolls invalid: ", bad)
	for id in ["sw_0", "sw_2", "sw_4", "ar_1", "ar_3", "ch_2", "ch_4", "bw_3", "dg_1", "potion"]:
		state.add(id, 1)
	print("[ci] staff: mage ", HeroClasses.can_equip("mage", Data.items["st_2"]), " summoner ", HeroClasses.can_equip("summoner", Data.items["st_2"]), " warrior ", HeroClasses.can_equip("warrior", Data.items["st_2"]))
	state.attrs = {"str": 20, "con": 20, "man": 20}      # meet the gear requirements
	state.add("ar_2", 1)
	state.add("ch_2", 1)
	state.equip("sw_2")
	state.equip("ar_2")
	state.equip("ch_2")
	var base_atk := state.total_atk()
	print("[ci] set bonus: ", state.set_bonus())
	state.gold = 5000
	state.add("hell_ember", 3)
	var forged := 0
	for i in 6:
		if state.forge("sw_2"):
			forged += 1
	print("[ci] forged ", forged, " levels (max 5); sword +", state.enh_level("sw_2"), " atk ", base_atk, " -> ", state.total_atk(), " gold left ", state.gold)
	var ng_old := state.ng_plus
	var bn := [0, 0, 0, 0, 0]
	state.ng_plus = 2
	for i in 300:
		bn[Loot.rarity_for(18, true)] += 1
	state.ng_plus = ng_old
	print("[ci] boss rarity NG+2 ", bn)
	Pickup.spawn("sw_4", 1, player.global_position + Vector2(160, 40))
	Pickup.spawn("ar_3", 1, player.global_position + Vector2(-160, 40))
	await _wait(1.2)
	await shot("72_drop_lendario")
	for pk in get_tree().get_nodes_in_group("__none"):
		pk.queue_free()
	state.equip("ar_3")
	grimoire.toggle()
	grimoire.sel = state.inv_ids.find("sw_4")
	grimoire._refresh()
	await _wait(0.5)
	await shot("70_bolsa_raridades")
	var g0 := state.gold
	var n0 := state.inv_ids.size()
	grimoire._sell("sw_0")
	print("[ci] sold: gold ", g0, " -> ", state.gold, " bag ", n0, " -> ", state.inv_ids.size())
	grimoire.toggle()
	hud.show_dialogue([["elowen", "Teste de legenda grande para celular: a lendária lâmina repousa onde a luz nunca chega, jovem herói."]], Callable())
	await _wait(1.5)
	await shot("71_legenda")
	while hud.in_dialogue():
		hud.advance()
		hud.advance()
		await get_tree().process_frame


func _ci_life() -> void:
	_tour_to("valemont")
	_travel_cd = 999.0
	player.input_locked = false
	# side quests: offer, then complete by granting the requirements
	var before := side_lines().size()
	for who in ["smith_v", "shopkeeper", "librarian", "tavern_keeper", "villager"]:
		Story.talk(who)
	print("[ci] side quests active: ", side_lines().size(), " (before ", before, ")")
	state.add("hell_ember", 4)
	state.add("imp_horn", 3)
	quests["q_insects"] = 6
	for k in ["cache_a", "cache_b", "cache_c"]:
		flags[k] = true
	var lines := 0
	for who in ["smith_v", "shopkeeper", "librarian", "guard_captain", "villager"]:
		lines += Story.talk(who).size()
	print("[ci] side quest rewards given, remaining active: ", side_lines().size(), " gold ", state.gold, " spark_tome ", state.count("spark_tome"))
	# night routine
	clock = World.DAY_LENGTH * 0.5
	await _wait(1.5)
	var hidden := 0
	var total := 0
	for n in world.entities.get_children():
		if n is Npc or n is Citizen:
			total += 1
			if not n.visible:
				hidden += 1
	print("[ci] night: ", phase_name(), " hidden townsfolk ", hidden, "/", total)
	player.global_position = Vector2(50, 54) * 64.0
	camera.snap()
	await _wait(0.8)
	await shot("60_valemont_noite")
	clock = 0.0
	await _wait(1.0)
	player.input_locked = true


## Attributes, skill tree, requirements and class actives (run late in the tour).
func _ci_stats() -> void:
	var gs := GameState.new()
	HeroClasses.apply_new_game(gs, "warrior")
	var atk0 := gs.total_atk()
	gs.attr_pts = 10
	for i in 5:
		gs.add_attr("str")
	for i in 3:
		gs.add_attr("agi")
	gs.add_attr("sor")
	print("[ci] str+5 agi+3: atk ", atk0, " -> ", gs.total_atk(), " dodge ", gs.dodge_chance(), " aspd ", gs.attack_speed(), " crit ", gs.crit_chance())
	var h0 := gs.hp_max()
	var mp0 := gs.max_mp
	gs.attr_pts = 4
	gs.add_attr("con")
	gs.add_attr("con")
	gs.add_attr("man")
	gs.add_attr("int")
	print("[ci] con+2 man+1 int+1: hp ", h0, " -> ", gs.hp_max(), " mp ", mp0, " -> ", gs.max_mp, " regen ", gs.mp_regen())
	# requirements
	gs.gold = 0
	print("[ci] req legendary sword (str 28) with str ", gs.attr("str"), ": '", gs.req_block("sw_4"), "' equip: ", gs.equip("sw_4"))
	gs.add("sw_1", 1)
	print("[ci] req sw_1 (str 10) ok: ", gs.req_block("sw_1") == "", " equip: ", gs.equip("sw_1"))
	# tree
	gs.level = 6
	gs.skill_pts = 3
	print("[ci] tree: tier0 ", gs.skill_block(0, 0) == "", " tier1 w/o tier0: ", gs.skill_block(0, 1), " tier3 lvl: ", gs.skill_block(0, 3))
	gs.learn_skill(0, 0)
	gs.learn_skill(0, 1)
	print("[ci] learned ", gs.skills, " slots ", gs.slots, " unlock r: ", gs.has_unlock("r"), " f: ", gs.has_unlock("f"), " pts left ", gs.skill_pts)
	gs.gold = 5000
	print("[ci] respec: ", gs.respec(), " attrs ", gs.attrs, " skills ", gs.skills, " attr_pts ", gs.attr_pts, " skill_pts ", gs.skill_pts)
	# every class tree is well-formed: 10 skills, each with a description and a valid kind
	var bad := 0
	for c in HeroClasses.CLASSES:
		var total := 0
		for b in 3:
			for t in int(SkillTree.LAYOUT[b]):
				var n := SkillTree.node(c, b, t)
				total += 1
				if SkillTree.active_text(n) == "" and SkillTree.describe(n["pas"]) == "" or not (str(n["k"]) in ["nova", "meteor", "storm", "volley", "dash", "summon", "none"]):
					bad += 1
		if total != 10:
			bad += 1
	print("[ci] trees malformed: ", bad)
	# live hero: unlock everything, cast every class active
	_tour_to("village")
	_travel_cd = 999.0
	player.input_locked = false
	player.invuln = 99.0
	var classes := ["warrior", "mage", "paladin", "archer", "assassin", "summoner"]
	for c in classes:
		state.class_id = c
		state.skills = []
		for b in 3:
			for t in int(SkillTree.LAYOUT[b]):
				state.skills.append(SkillTree.node_id(b, t))
		state.slots = ["0_0", "0_1", "1_0", "2_2"]
		state.base_mp = 999.0
		player.mp = 999.0
		player.anim.setup(HeroClasses.sheet_for(c))
		player.state = Player.St.FREE
		var pack: Array = []
		for i in 4:
			pack.append(Enemy.spawn("imp", player.global_position + Vector2(randf_range(-110, 110), randf_range(-90, 90)), 6))
		await _wait(0.3)
		var report := []
		for b2 in 3:
			for t2 in int(SkillTree.LAYOUT[b2]):
				var sid := SkillTree.node_id(b2, t2)
				state.equip_skill("r", sid)
				player.skill_cd["r"] = 0.0
				player.state = Player.St.FREE
				player.mp = 999.0
				var hp0 := 0.0
				for e in pack:
					if is_instance_valid(e) and not e.dead:
						hp0 += e.hp
				player._try_skill("r")
				await _wait(1.2)
				var hp1 := 0.0
				for e in pack:
					if is_instance_valid(e) and not e.dead:
						hp1 += e.hp
				report.append("%s:%d" % [SkillTree.node(c, b2, t2)["n"].substr(0, 8), roundi(hp0 - hp1)])
				player.state = Player.St.FREE
				if hp1 < 40.0:
					for e in pack:
						if is_instance_valid(e):
							e.queue_free()
					pack = []
					for i in 4:
						pack.append(Enemy.spawn("imp", player.global_position + Vector2(randf_range(-110, 110), randf_range(-90, 90)), 6))
		print("[ci] active skills ", c, ": ", report)
		if c == "paladin" or c == "summoner":
			await shot("76_skill_" + c)
		for e in pack:
			if is_instance_valid(e):
				e.queue_free()
		player.state = Player.St.FREE
		state.buffs = {}
	# skill menu screenshots
	state.class_id = "mage"
	state.level = 9
	state.attr_pts = 5
	state.skill_pts = 2
	state.attrs = {"int": 4, "man": 2}
	state.skills = ["0_0", "1_0"]
	state.slots = ["0_0", "1_0", "", ""]
	skills.toggle()
	skills.sel_b = 0
	skills.sel_t = 1
	skills._refresh()
	await _wait(0.5)
	await shot("77_arvore_habilidades")
	skills.toggle()
	state.class_id = "warrior"
	state.skills = []
	state.attrs = {}
	player.input_locked = true


## Class passives, guild daily board, shop selling.
func _ci_passives() -> void:
	for c in HeroClasses.CLASSES:
		for lv in [1, 10, 20]:
			if SkillTree.passive_text(c, lv).length() < 10 or SkillTree.passive_text(c, lv).contains("%"):
				print("[ci] passive text problem ", c, " ", lv, ": ", SkillTree.passive_text(c, lv))
	print("[ci] passives: ", SkillTree.passive_text("warrior", 1), " | ", SkillTree.passive_text("paladin", 20))
	# warrior: low life boosts attack
	var gs := GameState.new()
	HeroClasses.apply_new_game(gs, "warrior")
	var a_full := gs.total_atk()
	gs.hp_frac = 0.2
	print("[ci] Sangue de Ferro atk ", a_full, " -> ", gs.total_atk(), " dmg_taken ", gs.damage_taken_mult())
	# daily board
	DailyBoard.refresh(1000)
	print("[ci] daily: ", Game.daily["quests"].map(func(q): return DailyBoard.title(q) + " [" + DailyBoard.reward_text(q) + "]"))
	print("[ci] daily regions for imp: ", DailyBoard.regions_of("imp"), " seconds left ", DailyBoard.seconds_left() > 0)
	_tour_to("village")
	_travel_cd = 999.0
	player.input_locked = false
	state.class_id = "warrior"
	state.level = 4
	DailyBoard.refresh(1001)
	for i in 3:
		DailyBoard.accept(i)
	var q0: Dictionary = daily["quests"][0]
	var q1: Dictionary = daily["quests"][1]
	var q2: Dictionary = daily["quests"][2]
	var imp := Enemy.spawn("imp", player.global_position + Vector2(200, 0), 1)
	for i in int(q0["need"]):
		DailyBoard.on_kill(imp)
	print("[ci] hunt any progress ", DailyBoard.progress(q0), "/", q0["need"], " ready ", DailyBoard.ready(q0))
	state.add(str(q2["item"]), int(q2["need"]))
	print("[ci] deliver ready ", DailyBoard.ready(q2))
	var g0 := state.gold
	var xp0 := state.xp
	print("[ci] claim hunt: ", DailyBoard.claim(0), " claim deliver: ", DailyBoard.claim(2), " gold ", g0, " -> ", state.gold, " bag left ", state.count(str(q2["item"])))
	var js := JSON.stringify(daily)
	daily = DailyBoard.normalise(JSON.parse_string(js))
	print("[ci] daily save roundtrip: done ", DailyBoard.done_count(), " bonus ", daily["bonus"])
	board.open_board()
	board.sel = 1
	board._refresh()
	await _wait(0.4)
	await shot("78_quadro_guilda")
	board.close()
	# shop: sell tab
	state.add("sw_0", 2)
	state.add("ar_1", 1)
	state.add("ch_3", 1)
	shop.open_for("blacksmith")
	shop._set_mode(1)
	await _wait(0.4)
	await shot("79_loja_vender")
	var gold_before := state.gold
	shop._sell_one(true)
	shop._sell_junk()
	print("[ci] shop sell: gold ", gold_before, " -> ", state.gold, " sell list ", shop.sell_list.size())
	shop.close()
	skills.toggle()
	await _wait(0.3)
	await shot("80_passiva")
	skills.toggle()
	player.input_locked = true


## Interiors: every room renders, doors lead in and out, shops close at night, the inn rents rooms and sells food.
func _ci_interiors() -> void:
	var names := ["int_guild_aurora", "int_smithy_aurora", "int_tavern_aurora", "int_guild_valemont", "int_tavern_valemont", "int_smithy_valemont",
		"int_shop_valemont", "int_armory_valemont", "int_stable_valemont", "int_library_valemont", "int_barracks_valemont", "int_bakery_valemont"]
	for n in names:
		_tour_to(n)
		_travel_cd = 999.0
		player.input_locked = false
		var npcs: Array = []
		var furn := 0
		for e in world.entities.get_children():
			if e is Npc:
				npcs.append(e.id)
			elif e is Furniture:
				furn += 1
		print("[ci] interior ", n, " npcs ", npcs, " furniture ", furn)
		await _wait(0.4)
		await shot("90_" + n)
	# doors both ways
	for outdoor in ["village", "valemont"]:
		await _ci_doors(outdoor)
	# shops close at night
	_tour_to("valemont")
	player.input_locked = false
	clock = World.DAY_LENGTH * 0.5
	_travel_cd = 0.0
	travel("int_shop_valemont")
	print("[ci] night shop: map ", map_name, " tavern: ")
	_travel_cd = 0.0
	travel("int_tavern_valemont")
	print("[ci] night tavern: map ", map_name)
	# inn: rent a room + food
	state.gold = 3000
	state.level = 5
	player.hp = 10.0
	player.mp = 0.0
	tavern.open_for("inn")
	await _wait(0.3)
	await shot("91_taverna_quartos")
	tavern._set_tab(1)
	tavern.sel = 2
	tavern._refresh()
	await _wait(0.3)
	await shot("92_taverna_comida")
	tavern._eat(2)
	print("[ci] food buffs: ", state.buffs.keys(), " hp ", player.hp)
	var c0 := clock
	tavern._rent(1)
	await _wait(0.6)
	await shot("93_dormindo")
	await _wait(5.5)
	print("[ci] slept: clock ", c0, " -> ", clock, " hp ", player.hp, "/", state.hp_max(), " mp ", player.mp, " buffs ", state.buffs.keys(), " open ", tavern.open)
	await _wait(0.5)
	await shot("94_taverna_apos_dormir")
	tavern.close()
	clock = 0.0
	player.input_locked = true


## Target lock: T locks the nearest enemy, cycles, releases; attacks and spells go to the locked enemy even when facing away.
func _ci_lock() -> void:
	_tour_to("village")
	_travel_cd = 999.0
	player.input_locked = false
	player.invuln = 99.0
	state.class_id = "warrior"
	state.level = 12
	player.anim.setup(HeroClasses.sheet_for("warrior"))
	for old_e in Enemy.all.duplicate():
		if is_instance_valid(old_e):
			old_e.queue_free()
	await _wait(0.2)
	player.global_position = Vector2(2496, 3300)
	camera.snap()
	var a := Enemy.spawn("imp", player.global_position + Vector2(1.3 * 64, -0.9 * 64), 3)
	var b := Enemy.spawn("oni", player.global_position + Vector2(-5.0 * 64, 1.0 * 64), 3)
	var c := Enemy.spawn("imp", player.global_position + Vector2(7.0 * 64, -3.0 * 64), 3)
	for e in [a, b, c]:
		e.speed = 0.0
		e.max_hp = 9999.0
		e.hp = 9999.0
	await _wait(0.4)
	player.lock_cycle()
	var first := player.lock_target
	print("[ci] lock 1: nearest ", first == a)
	player.lock_cycle()
	print("[ci] lock 2: next ", player.lock_target == b)
	player.lock_cycle()
	print("[ci] lock 3: next ", player.lock_target == c)
	player.lock_cycle()
	print("[ci] lock 4: released ", player.lock_target == null)
	player.lock_cycle()
	await _wait(0.5)
	await shot("95_trava_de_mira")
	# melee strike while facing the opposite way: must still hit the locked imp
	player.face(Util.Face.LEFT)
	var hp0 := a.hp
	player._try_attack()
	await _wait(0.9)
	print("[ci] lock melee: facing away, hit ", a.hp < hp0, " facing now ", player.facing)
	# lock the far one and shoot as archer: projectile heads for it
	player._set_lock(c)
	state.class_id = "archer"
	player.anim.setup(HeroClasses.sheet_for("archer"))
	player.state = Player.St.FREE
	var hc0 := c.hp
	player.face(Util.Face.LEFT)
	player._try_attack()
	await _wait(1.6)
	print("[ci] lock arrow: far target hit ", c.hp < hc0)
	# the target dies: lock moves to the nearest neighbour
	c.hurt(99999.0, c.global_position + Vector2.RIGHT, 0.0, 999.0)
	await _wait(0.6)
	print("[ci] dbg nearest from c: ", Enemy.nearest(c.global_position, 7.0 * 64.0), " dist a-c ", a.global_position.distance_to(c.global_position) / 64.0, " player dead ", player.dead, " all ", Enemy.all.size())
	print("[ci] lock after kill: ", player.lock_target != null and player.lock_target != c, " c.dead ", c.dead, " lock ", player.lock_target, " a.dead ", a.dead, " b.dead ", b.dead)
	for e in [a, b, c]:
		if is_instance_valid(e):
			e.queue_free()
	await _wait(0.4)
	print("[ci] lock cleared when none left: ", player.lock_target == null)
	state.class_id = "warrior"
	player.input_locked = true


## 2.5D exteriors: front + side wall + roof volume.
func _ci_buildings() -> void:
	_tour_to("valemont")
	_travel_cd = 999.0
	player.input_locked = false
	player.invuln = 99.0
	clock = 0.0
	for spot in [["tavern", Vector2(4576, 3200)], ["guild", Vector2(3968, 2660)], ["smithy", Vector2(1920, 3690)], ["plaza", Vector2(3300, 3300)], ["muralha_ne", Vector2(4470, 1960)], ["muralha_sul", Vector2(2700, 5050)], ["muralha_oeste", Vector2(1450, 2400)]]:
		player.global_position = spot[1]
		camera.snap()
		await _wait(0.5)
		await shot("96_predio_" + spot[0])
	_tour_to("village")
	player.input_locked = false
	player.global_position = Vector2(2496, 1900)
	camera.snap()
	await _wait(0.5)
	await shot("96_predio_aurora")


func _ci_doors(outdoor: String) -> void:
	if GATES.has(outdoor):
		flags[GATES[outdoor][0]] = true       # the test walks through the town gate rule
	_tour_to(outdoor)
	_travel_cd = 0.0
	player.input_locked = false
	var seen_house := false
	for e in world.data["exits"]:
		if str(e["to"]).begins_with("int_"):
			var want: String = e["to"]
			if str(e.get("kind", "")) == "house":
				if seen_house and want != "int_house_aurora_3":
					continue
				seen_house = true
			var ax := float(e["ax"])
			var ay := float(e["ay"])
			player.global_position = Vector2(float(e["x"]), float(e["y"]))
			_travel_cd = 0.0
			await _wait(0.5)
			var inside := map_name == want
			var ex: Dictionary = world.data["exits"][0]
			player.global_position = Vector2(float(ex["x"]), float(ex["y"]))
			_travel_cd = 0.0
			await _wait(0.5)
			print("[ci] door ", outdoor, " -> ", want, ": entered ", inside, " back in ", map_name, " at ", player.global_position.distance_to(Vector2(ax, ay)) < 80.0)


## Directional cast shadows follow the sun through the day.
func _ci_fx() -> void:
	# water + wind (village river), wall damage stages (Valemont), room lights (tavern), quality tiers
	for q in [2, 0]:
		quality = q
		_tour_to("village")
		_travel_cd = 999.0
		player.input_locked = false
		player.invuln = 99.0
		player.global_position = Vector2(3450, 2330)
		for e in Enemy.all.duplicate():
			if is_instance_valid(e):
				e.queue_free()
		camera.snap()
		await _wait(0.8)
		await shot("98_agua_q%d" % q)
	quality = 2
	for st in [1, 3, 5]:
		flags.erase("game_complete")
		flags["val_started"] = true
		flags["rank_c"] = st >= 2
		if st >= 3:
			for r in Story.regions:
				flags[str(r["done"])] = st >= 5 or str(r["map"]) in ["kharis", "mines"]
		_tour_to("valemont")
		_travel_cd = 999.0
		player.input_locked = false
		player.invuln = 99.0
		var a := deg_to_rad(20.0)
		player.global_position = Vector2((50.0 + 31.0 * cos(a)) * 64.0 - 20.0, (50.0 + 31.0 * sin(a)) * 64.0 - 200.0)
		camera.snap()
		print("[ci] wall stage ", wall_stage())
		await _wait(4.0)
		await shot("98_muralha_%d" % st)
	_tour_to("village")
	_travel_cd = 999.0
	player.input_locked = false
	player.invuln = 99.0
	player.global_position = Vector2(1350, 3330)
	for e in Enemy.all.duplicate():
		if is_instance_valid(e):
			e.queue_free()
	camera.snap()
	await _wait(0.8)
	await shot("98_reflexo_lago")
	# rain: dark sky, streaks, windows lit, townsfolk run for shelter
	weather_auto = false
	weather_target = 1.0
	weather = 1.0
	clock = 0.0
	_tour_to("village")
	_travel_cd = 999.0
	player.input_locked = false
	player.invuln = 99.0
	player.global_position = Vector2(2496, 2250)
	for e in Enemy.all.duplicate():
		if is_instance_valid(e):
			e.queue_free()
	camera.snap()
	await _wait(1.5)
	var modes := {}
	for c in get_tree().get_nodes_in_group("citizens"):
		modes[c.mode] = int(modes.get(c.mode, 0)) + 1
	print("[ci] rain citizen modes ", modes, " weather ", weather, " outdoor ", world._outdoor, " mod ", world._mod.color, " rain node ", world._rain)
	await shot("98_chuva")
	await _wait(2.0)
	await shot("98_chuva_poças")
	world._strike_tree()
	world._flash = 1.0
	await _wait(0.12)
	await shot("98_raio")
	await _wait(1.0)
	print("[ci] wet ", wet, " player tint ", player.anim.self_modulate)
	flags["rank_d"] = true
	flags["sq_res_nina_done"] = true
	var q2 := Story.talk("res_nina")
	print("[ci] quest2 offer ", q2.size(), " ", q2[0][1].substr(0, 30))
	weather = 0.0
	weather_target = 0.0
	# house quests
	for who in ["res_nina", "res_lucia"]:
		var l1 := Story.talk(who)
		var l2 := Story.talk(who)
		state.add("imp_horn", 2)
		state.add("demon_hide", 4)
		var l3 := Story.talk(who)
		print("[ci] house quest ", who, " offer ", l1.size(), " again ", l2[0][1].substr(0, 20), " done ", l3[0][1].substr(0, 24), " gold ", state.gold)
	# guard shifts in Valemont
	for ph in [0.0, 0.5]:
		clock = World.DAY_LENGTH * ph
		_tour_to("valemont")
		_travel_cd = 999.0
		await _wait(0.8)
		var gv := 0
		var cv := 0
		for c in get_tree().get_nodes_in_group("citizens"):
			if c.visible:
				if c.look == "v_guard":
					gv += 1
				else:
					cv += 1
		print("[ci] valemont phase ", ph, " visible guards ", gv, " citizens ", cv)
	clock = 0.0
	# inside a house
	_tour_to("int_house_aurora_0")
	_travel_cd = 999.0
	player.input_locked = false
	await _wait(0.7)
	await shot("98_casa_interior")
	# night windows + leaves in Aurora
	_tour_to("village")
	_travel_cd = 999.0
	player.input_locked = false
	player.invuln = 99.0
	player.global_position = Vector2(2496, 2250)
	for e in Enemy.all.duplicate():
		if is_instance_valid(e):
			e.queue_free()
	camera.snap()
	clock = World.DAY_LENGTH * 0.5
	await _wait(1.0)
	await shot("98_noite_janelas")
	# live wall collapse: story advances while in Valemont
	flags.erase("val_started")
	flags.erase("rank_c")
	for r in Story.regions:
		flags.erase(str(r["done"]))
	flags.erase("lumia_blessed")
	flags.erase("game_complete")
	_tour_to("valemont")
	_travel_cd = 999.0
	var a2 := deg_to_rad(20.0)
	player.global_position = Vector2((50.0 + 31.0 * cos(a2)) * 64.0 - 20.0, (50.0 + 31.0 * sin(a2)) * 64.0 - 200.0)
	camera.snap()
	flags["val_started"] = true
	await _wait(1.0)
	flags["rank_c"] = true
	for r in Story.regions:
		flags[str(r["done"])] = true
	await _wait(1.2)
	print("[ci] live wall stage ", wall_stage(), " pending ", world._stage_pending.size())
	await shot("98_muralha_ao_vivo")
	for n in ["int_tavern_aurora", "int_smithy_aurora"]:
		for q in [2, 0]:
			quality = q
			_tour_to(n)
			_travel_cd = 999.0
			player.input_locked = false
			await _wait(0.6)
			await shot("98_luz_%s_q%d" % [n, q])
	quality = 2


func _ci_shadows() -> void:
	_tour_to("village")
	_travel_cd = 999.0
	player.input_locked = false
	player.invuln = 99.0
	player.global_position = Vector2(2496, 2250)
	for e in Enemy.all.duplicate():
		if is_instance_valid(e):
			e.queue_free()
	camera.snap()
	for t in [["meio_dia", 0.0], ["fim_tarde", 0.18], ["por_do_sol", 0.26], ["noite", 0.5], ["amanhecer", 0.78]]:
		clock = World.DAY_LENGTH * float(t[1])
		await _wait(0.6)
		await shot("97_sombra_" + t[0])
