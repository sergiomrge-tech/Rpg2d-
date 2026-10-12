class_name Npc
extends Actor
## Villager / guild staff: breathing idle, turns to face the hero, strolls a little, talks.

var id := ""
var display_name := ""
var home := Vector2.ZERO
var home_facing: int = Util.Face.DOWN
var think := 0.0
var stroll := Vector2.ZERO
var talking := false
const NIGHT_OFF := ["smith_v", "shopkeeper", "armorer", "librarian", "stable_master", "blacksmith", "villager", "child", "cleric", "noble"]


static func spawn(m: Dictionary) -> Npc:
	var n := Npc.new()
	n.name = "NPC_" + m["id"]
	n.id = m["id"]
	n.display_name = Story.name_of(n.id)
	n.collision_layer = 8
	n.collision_mask = 1
	n.build("Sprites/Chars/" + m["look"], 1.2, 0.4, 0.32)
	var at := Vector2(float(m["x"]), float(m["y"]))
	n.home = at
	var fc: String = m.get("facing", "down")
	n.home_facing = {"left": Util.Face.LEFT, "right": Util.Face.RIGHT, "up": Util.Face.UP}.get(fc, Util.Face.DOWN)
	Game.world.add_entity(n, at)
	n.face(n.home_facing)
	n.anim.play("idle")
	n.anim.speed = randf_range(0.85, 1.1)
	n.max_hp = 1.0
	n.hp = 1.0
	n.think = randf_range(2.0, 5.0)
	return n


func _physics_process(dt: float) -> void:
	# daily routine: shopkeepers and townsfolk go indoors at night (the tavern keeper and the guards stay up)
	var asleep: bool = id in NIGHT_OFF and Game.is_night() and not Game.world.data.get("interior", false)
	if asleep == visible:
		visible = not asleep
		collision_layer = 0 if asleep else 8
	if asleep:
		velocity = Vector2.ZERO
		return
	var p := Player.I
	var near := p != null and (p.global_position - global_position).length() < 2.6 * T
	if near or talking:
		velocity = Vector2.ZERO
		if p:
			face(Util.facing_from(p.global_position - global_position, facing))
		anim.play("idle")
		return
	think -= dt
	if think <= 0.0:
		think = randf_range(3.0, 7.0)
		stroll = Vector2.from_angle(randf() * TAU) if randf() < 0.4 else Vector2.ZERO
		if (global_position - home).length() > 1.5 * T:
			stroll = (home - global_position).normalized()
	if stroll.length_squared() > 0.01 and think > 1.5:
		face(Util.facing_from(stroll, facing))
		anim.play("walk")
		velocity = stroll * 1.4 * T
		move_and_slide()
	else:
		if anim.base == "walk":
			face(home_facing)
		anim.play("idle")


func hurt(_d: float, _f: Vector2, _k: float, _p: float, _c: bool = false) -> bool:
	return false


func _die() -> void:
	pass
