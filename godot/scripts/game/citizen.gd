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


static func spawn(w: Dictionary, map: String) -> Citizen:
	var c := Citizen.new()
	c.name = "Citizen_" + str(w["look"])
	c.collision_layer = 8
	c.collision_mask = 1
	c.map_key = map
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
	return c


func _physics_process(dt: float) -> void:
	# townsfolk go home at night; the guards keep patrolling
	var asleep: bool = Game.is_night() and look != "v_guard"
	if asleep == visible:
		visible = not asleep
		collision_layer = 0 if asleep else 8
	if asleep:
		velocity = Vector2.ZERO
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
