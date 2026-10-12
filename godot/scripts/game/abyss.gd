class_name Abyss
extends Node
## Endgame challenge (after the story): five waves of demons around the hero, a general on the last one.

const T := 64.0
const WAVES := 5
const POOL := ["oni_executioner", "ash_wraith", "demon_knight", "imp_howler", "oni_shielder", "imp_pyro", "oni_lancer"]
const GENERAL := "vorath"

static var active := false
static var wave := 0
static var runs_done := 0
static var _node: Abyss
var _gap := 0.0
var _map := ""


static func start() -> void:
	if active or Game.world == null:
		return
	active = true
	wave = 0
	_node = Abyss.new()
	Game.add_child(_node)
	Game.hud.banner("O Abismo", "Cinco ondas · resista!")
	_node._gap = 3.5
	_node._map = Game.map_name


static func cancel(msg := "") -> void:
	if not active:
		return
	active = false
	for e in Enemy.all.duplicate():
		if is_instance_valid(e) and e.arena and not e.dead:
			e.queue_free()
	if is_instance_valid(_node):
		_node.queue_free()
	if msg != "":
		Game.hud.banner("O Abismo se fechou", msg)


static func alive() -> int:
	var n := 0
	for e in Enemy.all:
		if is_instance_valid(e) and e.arena and not e.dead:
			n += 1
	return n


func _process(dt: float) -> void:
	if not active:
		return
	var p := Player.I
	if p == null or p.dead:
		cancel("Você caiu. Volte quando estiver pronto.")
		return
	if Game.map_name != _map:
		cancel("Você deixou o Abismo.")
		return
	if alive() > 0:
		return
	_gap -= dt
	if _gap > 0.0:
		return
	if wave >= WAVES:
		_reward()
		return
	_spawn_wave()


func _spawn_wave() -> void:
	wave += 1
	var gs := Game.state
	var p := Player.I
	var lv := maxi(8, gs.level) + wave
	var count := 3 + wave * 2
	Game.hud.banner("Onda %d de %d" % [wave, WAVES], "Última onda: o General!" if wave == WAVES else "%d demônios" % count)
	Sfx.play("boom", 0.5, 0.6)
	for i in count:
		var a := TAU * float(i) / count + randf() * 0.4
		var at := p.global_position + Vector2(cos(a), sin(a) * 0.7) * randf_range(6.0, 8.5) * T
		var e := Enemy.spawn(POOL[randi() % POOL.size()], at, lv)
		e.arena = true
	if wave == WAVES and Data.demons.has(GENERAL):
		var g := Enemy.spawn(GENERAL, p.global_position + Vector2(0, -7.5 * T), lv + 2)
		g.arena = true
	_gap = 2.0


func _reward() -> void:
	active = false
	runs_done += 1
	var gs := Game.state
	var p := Player.I
	var gold := 900 * (1 + gs.ng_plus)
	gs.gold += gold
	Game.hud.banner("Abismo conquistado!", "+%d ouro e tesouros lendários" % gold)
	Sfx.play("levelup", 0.7, 0.9)
	Sfx.play("legend", 0.5, 1.0)
	for i in 3:
		Loot.gear_drop(maxi(gs.level, 18), true, p.global_position + Vector2(randf_range(-100, 100), randf_range(-60, 80)), 1.0)
	Game.flags["abyss_clear"] = true
	Game.save()
	queue_free()
