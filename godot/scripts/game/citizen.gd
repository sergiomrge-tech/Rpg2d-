class_name Citizen
extends Actor
## Ambient townsperson who walks a patrol route through the streets, pauses, greets the hero and steps aside.

const BARKS := {
	"valemont": ["Bom dia, herói!", "A Guilda anda movimentada...", "Cuidado com o beco ao sul.", "Que dia lindo em Valemont!", "Viu o ferreiro? Anda de martelo em punho.",
		"A cerveja do Javali Dourado é a melhor!", "Dizem que você derrotou a Dríade!", "Os guardas dobraram a ronda."],
	"village": ["Bom dia!", "Os diabretes andam ousados.", "A Guilda precisa de gente corajosa.", "Boa sorte no bosque!"],
}
var route: Array = []
var idx := 0
var wait := 0.0
var map_key := "valemont"
var look := ""
var bark_cd := 0.0
var stuck_t := 0.0
var _last := Vector2.ZERO
var mode := "patrol"          # patrol | market | tavern | shelter | asleep
var _goal := Vector2.ZERO
var _inside := false
var _mine := 0.0
var _chat_cd := 5.0
var _lantern: Sprite2D              # per-citizen dice so not everybody follows the same routine


static func spawn(w: Dictionary, map: String) -> Citizen:
	var c := Citizen.new()
	c.name = "Citizen_" + str(w["look"])
	c.collision_layer = 8
	c.collision_mask = 1
	c.map_key = map
	c.add_to_group("citizens")
	c.look = str(w["look"])
	for p in w["route"]:
		c.route.append(Vector2(float(p[0]), float(p[1])))
	c.build("Sprites/Chars/" + str(w["look"]), 1.2, 0.4, 0.3)
	Game.world.add_entity(c, c.route[0])
	c.anim.play("idle")
	c.anim.speed = randf_range(0.9, 1.1)
	c.max_hp = 1.0
	c.hp = 1.0
	c.idx = 1 % c.route.size()
	c.wait = randf_range(0.0, 3.0)
	c.bark_cd = randf_range(2.0, 8.0)
	c._mine = randf()
	if c.look == "v_guard":
		c._lantern = Util.glow(c, Color(1.0, 0.72, 0.36), 2.8, 0.0)
		c._lantern.position = Vector2(16, -58)
	return c


## Daily routine: market stalls in the morning, the tavern in the evening, sleep at night, shelter from the rain.
func _pick_mode() -> String:
	if look == "v_guard":
		# two shifts: day guards are off duty at night, night guards only walk the walls in the dark
		return "patrol" if Game.is_night() == (_mine >= 0.5) else "asleep"
	if Game.is_night():
		return "asleep"
	if Game.weather > 0.45 and _mine < 0.85:
		return "shelter"
	var ph := Game.day_phase()
	if ph > 0.2 and ph < 0.32 and _mine < 0.6 and _find("tavern") != Vector2.ZERO:
		return "tavern"
	if ph > 0.68 and ph < 0.9 and _mine > 0.35 and _find("stall") != Vector2.ZERO:
		return "market"
	return "patrol"


func _farewell(next: String) -> void:
	var p := Player.I
	if p == null or (p.global_position - global_position).length() > 6.0 * T or not visible:
		return
	var line := ""
	if look == "v_guard" and next == "asleep":
		line = "Fim do turno. Boa vigília aos outros!"
	elif next == "asleep":
		line = "Boa noite, herói!"
	elif next == "tavern":
		line = "Vou tomar uma caneca na taverna!"
	elif next == "shelter":
		line = "Que chuvarada! Vou me abrigar."
	elif next == "market":
		line = "Hora da feira! Até mais!"
	if line != "":
		Fx.toast(line, Color(1, 0.96, 0.8), global_position + Vector2.UP * 2.0 * T)


## Two neighbours at the market chat or haggle.
func _market_chat(dt: float) -> void:
	_chat_cd -= dt
	if _chat_cd > 0.0:
		return
	_chat_cd = randf_range(7.0, 14.0)
	for o in get_tree().get_nodes_in_group("citizens"):
		if o != self and o.visible and o.mode == "market" and o.global_position.distance_to(global_position) < 2.8 * T:
			var p := Player.I
			if p != null and (p.global_position - global_position).length() < 7.0 * T:
				var lines := ["Quanto custa essa maçã?", "Fresquinha, colhida hoje!", "Levo duas, então.", "Fechado! Aqui está o ouro.", "Que dia bonito para a feira!", "Ouvi que o herói limpou o bosque."]
				var li := randi() % lines.size()
				Fx.toast(lines[li], Color(1, 0.94, 0.78), global_position + Vector2.UP * 2.0 * T)
				if li == 3:       # the deal closes: coins change hands over the neighbour's head
					Fx.toast("🪙 −%d" % (2 + randi() % 6), Color(1, 0.85, 0.3), o.global_position + Vector2.UP * 2.6 * T)
					Fx.toast("🛒 " + ["maçãs", "pão", "frutas", "queijo", "legumes"][randi() % 5], Color(0.8, 1, 0.8), global_position + Vector2.UP * 2.6 * T)
			return


func _find(what: String) -> Vector2:
	var best := Vector2.ZERO
	var bd := 1e9
	var w := Game.world
	if what == "stall":
		for p in w.data["props"]:
			if str(p["kind"]).begins_with("stall"):
				var at := Vector2(float(p["x"]) + (_mine - 0.5) * 120.0, float(p["y"]) + 70.0)
				var d := at.distance_to(global_position)
				if d < bd and (_mine * 7.0 < 3.5 or d > 400.0):
					bd = d
					best = at
		return best
	for e in w.data["exits"]:
		var k := str(e.get("kind", ""))
		if (what == "tavern" and k == "tavern") or (what == "shelter" and str(e["to"]).begins_with("int_")):
			var at := Vector2(float(e["x"]), float(e["y"]) + 40.0)
			var d := at.distance_to(global_position)
			if d < bd:
				bd = d
				best = at
	return best


func _physics_process(dt: float) -> void:
	# townsfolk go home at night; the guards keep patrolling
	if _lantern != null:
		var nn: float = Game.world.night_amount() if Game.world != null else 0.0
		_lantern.modulate.a = 0.5 * nn * (0.9 + 0.1 * sin(Game._time * 9.0 + _mine * 20.0))
	var want := _pick_mode()
	if want != mode:
		_farewell(want)
		mode = want
		_goal = Vector2.ZERO
		if mode in ["market", "tavern", "shelter"]:
			_goal = _find("stall" if mode == "market" else mode)
		if _inside and mode in ["patrol", "market"]:
			_inside = false          # comes back out of the door
		if mode == "patrol" and _inside:
			_inside = false
	var hidden := mode == "asleep" or _inside
	if hidden == visible:
		visible = not hidden
		collision_layer = 0 if hidden else 8
	if hidden:
		velocity = Vector2.ZERO
		return
	if _goal != Vector2.ZERO and mode != "patrol":
		var gd := _goal - global_position
		if gd.length() < 0.6 * T or stuck_t > 3.0:
			velocity = Vector2.ZERO
			anim.play("idle")
			if mode == "market":
				_market_chat(dt)
			if mode in ["tavern", "shelter"]:
				_inside = true
			stuck_t = 0.0
			return
		face(Util.facing_from(gd, facing))
		anim.play("walk")
		velocity = gd.normalized() * 1.8 * T
		move_and_slide()
		if (global_position - _last).length() < 4.0 * dt * T * 0.2:
			stuck_t += dt
		else:
			stuck_t = 0.0
		_last = global_position
		return
	var p := Player.I
	bark_cd -= dt
	var near := p != null and (p.global_position - global_position).length() < 2.0 * T
	if near and not (Game.hud and Game.hud.in_dialogue()):
		velocity = Vector2.ZERO
		face(Util.facing_from(p.global_position - global_position, facing))
		anim.play("idle")
		if bark_cd <= 0.0:
			bark_cd = randf_range(7.0, 12.0)
			var list: Array = BARKS.get(map_key, BARKS["valemont"])
			Fx.toast(list[randi() % list.size()], Color(1, 0.96, 0.8), global_position + Vector2.UP * 2.0 * T)
		return
	if wait > 0.0:
		wait -= dt
		velocity = Vector2.ZERO
		anim.play("idle")
		return
	var target: Vector2 = route[idx]
	var d := target - global_position
	if d.length() < 0.5 * T:
		idx = (idx + 1) % route.size()
		wait = randf_range(1.5, 5.0)
		return
	var dir := d.normalized()
	face(Util.facing_from(dir, facing))
	anim.play("walk")
	velocity = dir * 1.5 * T
	move_and_slide()
	# stuck on a prop/other walker: give up on this waypoint
	if (global_position - _last).length() < 4.0 * dt * T * 0.2:
		stuck_t += dt
		if stuck_t > 2.5:
			stuck_t = 0.0
			idx = (idx + 1) % route.size()
	else:
		stuck_t = 0.0
	_last = global_position


func hurt(_d: float, _f: Vector2, _k: float, _p: float, _c: bool = false) -> bool:
	return false


func _die() -> void:
	pass
