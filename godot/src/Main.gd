extends Node

func _ready() -> void:
	Terrain.setup()
	var m := MapData.new("test", "Teste", 40, 24, "grass", 7)
	m.patches("meadow", 10, 2, 4, ["grass"])
	m.patches("grass_dark", 6, 2, 5, ["grass"])
	m.fill_rect("cobble", 12, 6, 12, 8)
	m.path("road", [Vector2(0, 10), Vector2(12, 10)], 3)
	m.path("road", [Vector2(24, 10), Vector2(39, 12)], 3, 1.0)
	m.path("dirt", [Vector2(18, 14), Vector2(18, 23)], 3, 1.0)
	m.blob("sand", 8, 19, 6, 4, 0.3)
	m.blob("water", 8, 19, 4.5, 2.8, 0.3)
	m.blob("deep", 8, 19, 2, 1.2, 0.2)
	m.fill_rect("wall_stone", 28, 3, 8, 3)
	m.fill_rect("slab", 28, 6, 8, 4)
	m.fill_rect("carpet", 31, 6, 2, 4)
	m.fill_rect("wall_cave", 2, 2, 6, 3)
	m.fill_rect("cave", 2, 5, 6, 3)
	m.add_obj("house5_timber_c9483a", 3, 6, 0) if false else null
	m.add_obj("fountain", 17, 11, 0)
	m.add_obj("tree_oak_0", 26, 14, 0)
	m.add_obj("tree_pine_1", 29, 15, 0)
	m.add_obj("campfire", 20, 14, 0)
	m.add_obj("torch", 11, 6, 0)
	m.add_obj("well", 6, 13, 0)
	m.add_obj("stall_red", 33, 14, 0)
	m.add_obj("house6_timber_3a7bd5", 22, 6, 0)
	m.add_obj("bush_1_f", 15, 15, 0)
	m.add_obj("crystal_c", 30, 18, 0)
	Game.new_game("Kai", "kai", "arcane")
	Game.skill_ranks["whirlwind"] = 3
	Game.skill_ranks["icelance"] = 2
	Game.skill_ranks["crescent"] = 5
	Game.slots = ["fireball", "icelance", "whirlwind", "crescent"]
	Game.level = 8
	Game.inv["potion"] = 5
	var w := World.new()
	add_child(w)
	w.load_map(m, Vector2i(14, 8))
	w.player.world = w
	for i in 3:
		w.spawn_enemy("slime", Vector2(520 + i * 40, 260 + i * 20))
	w.spawn_enemy("wolf", Vector2(640, 280))
	w.spawn_enemy("bat", Vector2(600, 200))
	w.spawn_enemy("slime_red" if false else "slime_blue", Vector2(560, 320), true)
	var args := OS.get_cmdline_user_args()
	await get_tree().create_timer(1.0).timeout
	get_viewport().get_texture().get_image().save_png("/tmp/g_world.png")
	Input.action_press("move_right")
	await get_tree().create_timer(0.7).timeout
	Input.action_release("move_right")
	Input.action_press("skill1")
	await get_tree().create_timer(0.1).timeout
	Input.action_release("skill1")
	await get_tree().create_timer(0.35).timeout
	get_viewport().get_texture().get_image().save_png("/tmp/g_world2.png")
	Input.action_press("attack")
	await get_tree().create_timer(0.1).timeout
	Input.action_release("attack")
	await get_tree().create_timer(0.2).timeout
	Input.action_press("skill3")
	await get_tree().create_timer(0.1).timeout
	Input.action_release("skill3")
	await get_tree().create_timer(0.45).timeout
	get_viewport().get_texture().get_image().save_png("/tmp/g_world3.png")
	await get_tree().create_timer(1.5).timeout
	get_viewport().get_texture().get_image().save_png("/tmp/g_world4.png")
	get_tree().quit()
