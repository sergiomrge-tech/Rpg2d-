extends Node
## Top-level orchestrator (autoload): world, player, HUD, quests, travel, saves, key queue, CI screenshot tour.

const SAVE_PATH := "user://aetheria_save.json"

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
var main: Node2D
var map_name := "village"
var ci_dir := ""

var _time := 0.0
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
	process_mode = Node.PROCESS_MODE_ALWAYS
	var args := OS.get_cmdline_user_args()
	for i in args.size() - 1:
		if args[i] == "-ciShots":
			ci_dir = args[i + 1]


func time() -> float:
	return _time


# ------------------------------------------------------------------ input queue
func _input(ev: InputEvent) -> void:
	if ev is InputEventKey and ev.pressed and not ev.echo:
		_keys[ev.physical_keycode] = Time.get_ticks_msec()
		_keys[ev.keycode] = Time.get_ticks_msec()
	elif ev is InputEventMouseButton and ev.pressed:
		_keys[-ev.button_index] = Time.get_ticks_msec()


## True once per key press (within 180 ms); removes it from the queue.
func consume(k: int) -> bool:
	if _keys.has(k) and Time.get_ticks_msec() - int(_keys[k]) < 180:
		_keys.erase(k)
		return true
	return false


# ------------------------------------------------------------------ start
func start(m: Node2D) -> void:
	main = m
	if ci_dir == "":
		_load()
	world = World.load_map(map_name)
	main.add_child(world)
	camera = CameraRig.new()
	main.add_child(camera)
	camera.set_world(world)
	var spawn := Vector2(float(world.data["playerX"]), float(world.data["playerY"]))
	if _has_saved_pos and world.bounds.has_point(_saved_pos):
		spawn = _saved_pos
	player = Player.spawn(spawn, state)
	world.spawn_actors()
	if flags.has("sylra_joined"):
		Companion.spawn(spawn + Vector2.LEFT * 64.0)
	camera.target = player
	camera.snap()
	hud = Hud.new()
	main.add_child(hud)
	grimoire = Grimoire.new()
	hud.add_child(grimoire)
	grimoire.setup(hud)
	Sfx.loop("ambience", 0.2)
	Music.play(map_name)
	if ci_dir != "":
		_ci_shots()
		return
	if not flags.has("prologue"):
		player.input_locked = true
		hud.show_dialogue(Story.prologue, func():
			flags["prologue"] = true
			player.input_locked = false
			hud.banner("Vila de Aurora", "Capítulo I — A Centelha")
			save())
	else:
		var t: Array = MAP_TITLES.get(map_name, ["", ""])
		hud.banner(t[0], "Rank " + state.guild_rank)


func _process(dt: float) -> void:
	_time += dt
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
	if consume(KEY_TAB) and not grimoire.open and not hud.in_dialogue() and not player.dead and not player.input_locked:
		grimoire.toggle()
	_travel_cd -= dt
	Music.play("boss" if hud.boss_bar.visible else map_name)
	if not player.dead and _travel_cd <= 0.0:
		var ex := world.exit_at(player.global_position)
		if not ex.is_empty():
			travel(ex["to"])
	if consume(KEY_F9) and not player.dead:
		_spawn_bestiary()
	if consume(KEY_F5):
		save()
		Fx.toast("Jogo salvo", Color.WHITE)


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
func travel(to: String) -> void:
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
	world.add_entity(player, at)
	if comp:
		world.add_entity(comp, at + Vector2.LEFT * 64.0)
	world.spawn_actors()
	camera.snap()
	_travel_cd = 1.5
	if MAP_TITLES.has(to):
		hud.banner(MAP_TITLES[to][0], MAP_TITLES[to][1])
	save()


# ------------------------------------------------------------------ dialogue / npcs
func interact(p: Player) -> void:
	if hud.in_dialogue():
		return
	var best: Npc = null
	var bd := 2.2 * 64.0
	for n in world.entities.get_children():
		if n is Npc:
			var d: float = (n.global_position - p.global_position).length()
			if d < bd:
				bd = d
				best = n
	if best == null:
		return
	var npc := best
	npc.talking = true
	p.input_locked = true
	p.velocity = Vector2.ZERO
	hud.show_dialogue(Story.talk(npc.id), func():
		npc.talking = false
		p.input_locked = false
		if npc.id == "sylra" and flags.has("sylra_joined") and Companion.I == null:
			Companion.spawn(npc.global_position)
			npc.queue_free()
			hud.banner("Sylra entrou no grupo", "Arqueira de Velmoor")
		save())


func start_quest(id: String) -> void:
	if not quests.has(id):
		quests[id] = 0


func quest_progress(id: String) -> int:
	return int(quests.get(id, 0))


## First line = headline, second line (optional) = detail.
func quest_line() -> String:
	if not flags.has("guild_joined"):
		return "◆ Procure a Guilda dos Aventureiros\nao norte da praça"
	if not flags.has("q_imps_done"):
		var n := mini(quest_progress(Story.QUEST_IMPS), Story.QUEST_IMPS_GOAL)
		if n >= Story.QUEST_IMPS_GOAL:
			return "◆ Volte à Guilda e fale com Elina"
		return "◆ Purgar o Bosque dos Chifres\nDiabretes %d/%d" % [n, Story.QUEST_IMPS_GOAL]
	if not flags.has("grakk_dead"):
		return "◆ Derrote Grakk, Chefe dos Diabretes\nsul do Bosque dos Chifres"
	if not flags.has("rank_e"):
		return "◆ Volte à Guilda e fale com Elina"
	if not flags.has("sylra_joined"):
		return "◆ Entre no portal ao sul do Bosque\ne encontre o santuário élfico de Velmoor"
	if not flags.has("dryad_profane_dead"):
		return "◆ Purifique o bosque sagrado\nderrote a Dríade Profanada (sul de Velmoor)"
	if not flags.has("rank_d"):
		return "◆ Volte à Guilda de Aurora"
	if not flags.has("val_started"):
		return "◆ Viaje a Valemont\nsaída leste de Velmoor — fale com o Mestre da Guilda"
	if not flags.has("assassin_shadow_dead"):
		return "◆ Cace o Assassino Sombrio\nbeco ao sul de Valemont"
	if not flags.has("rank_c"):
		return "◆ Volte ao Mestre Aldric, na Guilda"
	for r in Story.regions:
		if flags.has(r["done"]):
			continue
		if not flags.has(r["start"]):
			return "◆ Viaje a %s\nfale com %s" % [r["title"], Story.name_of(r["npc"])]
		if not Story.region_all_dead(r):
			return "◆ Derrote %s\n%s" % [r["bossName"], r["title"]]
		return "◆ Volte a %s\n%s" % [Story.name_of(r["npc"]), r["title"]]
	if flags.has("game_complete"):
		return "◆ Aetheria está em paz\nexplore livremente · F5 salva"
	if not flags.has("lumia_blessed"):
		return "◆ Entre na Cidadela de Malgrath\nleste das Terras Devastadas — fale com Lumia"
	return "◆ Derrote Malgrath, o Rei Demônio\nsalão do trono, ao norte da Cidadela"


# ------------------------------------------------------------------ combat callbacks
func on_enemy_killed(e: Enemy) -> void:
	if quests.has(Story.QUEST_IMPS) and e.def["id"] == "imp":
		quests[Story.QUEST_IMPS] = int(quests[Story.QUEST_IMPS]) + 1
	if e.def["id"] == "malgrath":
		flags["malgrath_dead"] = true
		save()
		_ending()
		return
	if e.def["boss"]:
		flags[str(e.def["id"]) + "_dead"] = true
		hud.banner(str(e.def["name"]) + " foi derrotado", "Volte à Guilda")
		save()
	var xp := roundi(float(e.def["xp"]) * Data.hp_scale(e.level))
	Fx.toast("+%d EXP" % xp, Color(0.75, 0.95, 1.0), e.global_position + Vector2.UP * 2.6 * 64.0)
	if state.gain_xp(xp):
		player.max_hp = state.hp_max()
		player.hp = player.max_hp
		player.mp = state.max_mp
		Fx.heal(player.pos())
		Sfx.play("levelup", 0.6, 1.0)
		hud.banner("Nível %d" % state.level, "Sua centelha arde mais forte")


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


# ------------------------------------------------------------------ save / load
func save() -> void:
	if ci_dir != "":
		return
	var d := {"state": state.to_dict(), "flags": flags.keys(), "quests": quests, "map": map_name}
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


# ------------------------------------------------------------------ CI: scripted tour + screenshots
func shot(n: String) -> void:
	await RenderingServer.frame_post_draw
	DirAccess.make_dir_recursive_absolute(ci_dir)
	get_viewport().get_texture().get_image().save_png("%s/%s.png" % [ci_dir, n])
	print("[ci] shot ", n)


func _ci_shots() -> void:
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
	grimoire.toggle()
	await _wait(0.5)
	await shot("03_grimoire")
	grimoire.toggle()
	player.global_position = Vector2(27 * 64, 39 * 64)
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
	# a tour of every other map: teleport, wait a beat, shoot
	for m in MAP_TITLES.keys():
		if m == "village":
			continue
		_tour_to(m)
		await _wait(1.0)
		await shot("10_" + m)
	await _ci_bosses()
	print("[ci] done")
	await _wait(0.3)
	get_tree().quit()


func _tour_to(m: String) -> void:
	var old := world
	old.entities.remove_child(player)
	main.remove_child(old)
	old.free()
	map_name = m
	world = World.load_map(m)
	main.add_child(world)
	camera.set_world(world)
	world.add_entity(player, Vector2(float(world.data["playerX"]), float(world.data["playerY"])))
	world.spawn_actors()
	camera.snap()
	hud.banner(MAP_TITLES[m][0], MAP_TITLES[m][1])


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
