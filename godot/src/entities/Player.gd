class_name Player
extends Combatant
## The hero: movement, 3-hit combo, dodge roll, stamina, skills, potions.

enum S { IDLE, MOVE, ATTACK, ROLL, CAST, HURT, DEAD }
var state: int = S.IDLE
var combo := 0
var queued := false
var iframes := 0.0
var roll_dir := Vector2.DOWN
var roll_t := 0.0
var cd: Array = [0.0, 0.0, 0.0, 0.0]
var cd_max: Array = [1.0, 1.0, 1.0, 1.0]
var potion_cd := 0.0
var shield := 0.0
var shield_t := 0.0
var buff_mul := 1.0
var buff_t := 0.0
var combat_t := 99.0
var stamina_delay := 0.0
var locked := false
var cast_t := 0.0
var hurt_t := 0.0
var stats_cache := {}
var strike_done := false
var lunge_t := 0.0
var cur_hit := 3
var afterimage_t := 0.0
var invis_t := 0.0

const ATK_COST := [8.0, 8.0, 14.0]
const ATK_MULT := [1.0, 1.12, 1.85]
const ATK_REACH := [38.0, 40.0, 52.0]
const ATK_HALF := [1.0, 1.1, 1.5]

func _ready() -> void:
	team = "player"
	collision_layer = 2
	collision_mask = 1
	motion_mode = CharacterBody2D.MOTION_MODE_FLOATING
	radius = 9.0
	hit_h = 24.0
	var sf := SpriteLib.load_frames("hero_" + Game.look)
	setup_sprite(sf, SpriteLib.offset_y(sf))
	var cs := CollisionShape2D.new()
	var shp := RectangleShape2D.new()
	shp.size = Vector2(14, 8)
	cs.shape = shp
	cs.position = Vector2(0, -4)
	add_child(cs)
	sprite.frame_changed.connect(_on_frame)
	sprite.animation_finished.connect(_on_anim_done)
	add_to_group("player")
	refresh_stats()
	_play("idle")

func refresh_stats() -> void:
	stats_cache = Game.stats()
	max_hp = stats_cache["hp"]

func dir_name() -> String:
	if abs(face.x) > abs(face.y):
		return "left" if face.x < 0 else "right"
	return "down" if face.y > 0 else "up"

func _play(base: String, restart := false) -> void:
	var d := dir_name()
	var an := "%s_%s" % [base, "left" if d == "right" else d]
	sprite.flip_h = d == "right"
	if sprite.animation != an or restart:
		sprite.play(an)

func _physics_process(dt: float) -> void:
	_tick_common(dt)
	if world == null:
		return
	refresh_stats()
	max_hp = stats_cache["hp"]
	iframes = maxf(0.0, iframes - dt)
	potion_cd = maxf(0.0, potion_cd - dt)
	combat_t += dt
	for i in 4:
		cd[i] = maxf(0.0, cd[i] - dt)
	if shield_t > 0.0:
		shield_t -= dt
		if shield_t <= 0.0:
			shield = 0.0
	if buff_t > 0.0:
		buff_t -= dt
		if buff_t <= 0.0:
			buff_mul = 1.0
	if invis_t > 0.0:
		invis_t -= dt
		sprite.modulate.a = 0.35
		afterimage_t -= dt
		if afterimage_t <= 0.0:
			afterimage_t = 0.05
			_ghost()
		if invis_t <= 0.0:
			sprite.modulate.a = 1.0
	# resources
	var s := stats_cache
	stamina_delay = maxf(0.0, stamina_delay - dt)
	if stamina_delay <= 0.0:
		Game.stamina = minf(float(s["stamina"]), Game.stamina + 38.0 * dt)
	Game.mp = minf(float(s["mp"]), Game.mp + (1.4 + float(s["mp"]) * 0.012) * dt)
	Game.hp = minf(Game.hp, max_hp)
	if state == S.DEAD:
		velocity = kb_vel
		kb_vel *= 0.9
		move_and_slide()
		return
	if locked:
		velocity = Vector2.ZERO
		if state != S.IDLE:
			state = S.IDLE
		_play("idle")
		return
	var in_vec := Input.get_vector("move_left", "move_right", "move_up", "move_down")
	var spd := 98.0 * (1.0 + float(s["spd"]) / 100.0) * (0.6 if has_status("slow") else 1.0)
	if has_status("freeze") or has_status("stun"):
		velocity = Vector2.ZERO
		return
	match state:
		S.IDLE, S.MOVE:
			if in_vec.length() > 0.1:
				state = S.MOVE
				if abs(in_vec.x) > abs(in_vec.y) * 1.05 or abs(in_vec.y) > abs(in_vec.x) * 1.05:
					face = in_vec.normalized()
				velocity = in_vec * spd + kb_vel
				_play("walk")
			else:
				state = S.IDLE
				velocity = kb_vel
				_play("idle")
			kb_vel *= 0.82
			move_and_slide()
			if Input.is_action_just_pressed("attack") and Game.stamina >= ATK_COST[0] * 0.5:
				_start_attack()
			elif Input.is_action_just_pressed("dodge"):
				_start_roll(in_vec)
			else:
				for i in 4:
					if Input.is_action_just_pressed("skill%d" % (i + 1)):
						_try_skill(i)
				if Input.is_action_just_pressed("potion"):
					use_potion()
		S.ATTACK:
			lunge_t -= dt
			velocity = face_aim * (95.0 if lunge_t > 0.0 else 0.0) * (1.4 if combo == 3 else 1.0) + kb_vel
			kb_vel *= 0.8
			move_and_slide()
			if Input.is_action_just_pressed("attack"):
				queued = true
			if Input.is_action_just_pressed("dodge") and strike_done and Game.stamina >= 14.0:
				_start_roll(in_vec)
		S.ROLL:
			roll_t += dt
			velocity = roll_dir * 215.0 * (1.0 - roll_t / 0.5 * 0.35)
			move_and_slide()
			var f: float = clampf(roll_t / 0.32, 0.0, 1.0)
			sprite.rotation = f * TAU * (1.0 if roll_dir.x >= 0.0 else -1.0) * 0.95
			afterimage_t -= dt
			if afterimage_t <= 0.0:
				afterimage_t = 0.045
				_ghost()
			if roll_t >= 0.32:
				sprite.rotation = 0.0
				state = S.IDLE
		S.CAST:
			cast_t -= dt
			velocity = in_vec * spd * 0.35 + kb_vel
			kb_vel *= 0.8
			move_and_slide()
			if cast_t <= 0.0:
				state = S.IDLE
		S.HURT:
			hurt_t -= dt
			velocity = kb_vel
			kb_vel *= 0.88
			move_and_slide()
			if hurt_t <= 0.0:
				state = S.IDLE

var face_aim := Vector2.DOWN

func aim_vector(range_px := 90.0) -> Vector2:
	var in_vec := Input.get_vector("move_left", "move_right", "move_up", "move_down")
	var base: Vector2 = in_vec if in_vec.length() > 0.1 else face
	var best: Enemy = null
	var bs := 1e9
	for e in world.enemies:
		if e.dead:
			continue
		var d: Vector2 = e.hit_center() - (global_position + Vector2(0, -16))
		var dist := d.length()
		if dist > range_px:
			continue
		var da := absf(base.angle_to(d))
		if da > 1.1:
			continue
		var sc := dist + da * 40.0
		if sc < bs:
			bs = sc
			best = e
	if best:
		return (best.hit_center() - (global_position + Vector2(0, -16))).normalized()
	return base.normalized()

func _start_attack() -> void:
	if combo >= 3 or combo == 0 or not queued:
		combo = 1
	else:
		combo += 1
	combo = clampi(combo, 1, 3)
	Game.stamina = maxf(0.0, Game.stamina - ATK_COST[combo - 1])
	stamina_delay = 0.55
	state = S.ATTACK
	queued = false
	strike_done = false
	face_aim = aim_vector()
	if abs(face_aim.x) > abs(face_aim.y):
		face = Vector2(signf(face_aim.x), 0)
	else:
		face = Vector2(0, signf(face_aim.y))
	lunge_t = 0.16
	combat_t = 0.0
	sprite.speed_scale = 1.0
	var an := "attack%d_%s" % [combo, "left" if dir_name() == "right" else dir_name()]
	sprite.flip_h = dir_name() == "right"
	sprite.play(an)
	cur_hit = int(sprite.sprite_frames.get_meta("hit").get(an, 3))
	Sfx.play("swing", -2.0, randf_range(0.95, 1.1))

func _on_frame() -> void:
	if state == S.ATTACK and not strike_done and sprite.frame >= cur_hit:
		strike_done = true
		_strike()
	elif state == S.CAST and sprite.frame == 3 and pending_cast != "":
		var id := pending_cast
		pending_cast = ""
		Skills.release(world, self, id, Game.skill_rank(id))

func _on_anim_done() -> void:
	if state == S.ATTACK:
		if queued and combo < 3 and Game.stamina >= ATK_COST[mini(combo, 2)] * 0.5:
			_start_attack()
		else:
			if combo >= 3:
				combo = 0
			state = S.IDLE
			queued = false
			stamina_delay = 0.4

func _strike() -> void:
	var o := global_position + Vector2(0, -16)
	var ang := face_aim.angle()
	var reach: float = ATK_REACH[combo - 1]
	var half: float = ATK_HALF[combo - 1]
	var col := Color("bfe4ff") if combo < 3 else Color("ffd84a")
	var flip := combo == 2
	Fx.slash(world, o + face_aim * 6.0, ang, reach * 0.82, col, half * 2.1, flip, 0.24 if combo < 3 else 0.32, 8.0 + combo * 2.0)
	if combo == 3:
		Fx.burst(world, o + face_aim * reach * 0.7, [Color("ffd84a"), Color("ffffff")], 10, 120.0, 0.35, 3.0)
	Sfx.play("swing2" if combo == 3 else "swing", -3.0, 0.9 + combo * 0.08)
	var hit_any := false
	for e in world.enemies.duplicate():
		if e.dead:
			continue
		var d: Vector2 = e.hit_center() - o
		if d.length() > reach + e.radius:
			continue
		if d.length() > e.radius + 8.0 and absf(face_aim.angle_to(d)) > half:
			continue
		var h := make_hit(float(stats_cache["atk"]) * ATK_MULT[combo - 1], "phys")
		h["kb"] = 150.0 if combo == 3 else 80.0
		h["heavy"] = combo == 3
		h["poise"] = 1.0 + combo * 0.8
		h["src"] = global_position
		e.take_hit(h)
		hit_any = true
	if hit_any:
		combat_t = 0.0
		if combo == 3:
			Fx.shake(world, 4.0)

func make_hit(base: float, elem: String) -> Dictionary:
	var s := stats_cache
	var dmg := base * buff_mul * randf_range(0.93, 1.07)
	var crit := randf() * 100.0 < float(s["crit"])
	if crit:
		dmg *= 1.65
	var fire_bonus: float = float(s.get("fire", 0.0))
	if elem == "fire":
		dmg *= 1.0 + fire_bonus / 100.0
	return {"dmg": dmg, "elem": elem, "crit": crit, "src": global_position, "from_player": true, "lifesteal": float(s.get("lifesteal", 0.0))}

func _start_roll(in_vec: Vector2) -> void:
	if Game.stamina < 24.0:
		Sfx.play("error", -6.0)
		return
	Game.stamina -= 24.0
	stamina_delay = 0.7
	roll_dir = in_vec.normalized() if in_vec.length() > 0.1 else face
	if abs(roll_dir.x) > abs(roll_dir.y):
		face = Vector2(signf(roll_dir.x), 0)
	else:
		face = Vector2(0, signf(roll_dir.y))
	state = S.ROLL
	roll_t = 0.0
	queued = false
	combo = 0
	iframes = 0.36
	_play("roll", true)
	Sfx.play("dodge", -4.0)
	Fx.burst(world, global_position, [Color("c8c0e8")], 6, 40.0, 0.3, 3.0, 0.0, false)

func _ghost() -> void:
	var g := Sprite2D.new()
	var tex := sprite.sprite_frames.get_frame_texture(sprite.animation, sprite.frame)
	g.texture = tex
	g.flip_h = sprite.flip_h
	g.offset = sprite.offset
	g.global_position = global_position
	g.rotation = sprite.rotation
	g.modulate = Color(0.6, 0.8, 1.0, 0.45) if invis_t <= 0.0 else Color(0.7, 0.5, 1.0, 0.5)
	g.z_index = 1
	world.fx_layer.add_child(g)
	var tw := g.create_tween()
	tw.tween_property(g, "modulate:a", 0.0, 0.3)
	tw.tween_callback(g.queue_free)

var pending_cast := ""

func _try_skill(slot: int) -> void:
	var id: String = Game.slots[slot]
	if id == "":
		return
	var rank := Game.skill_rank(id)
	if rank < 1 or cd[slot] > 0.0:
		return
	var cost := Data.skill_cost(id, rank)
	if Game.mp < cost:
		Sfx.play("error", -6.0)
		Game.toast.emit("Mana insuficiente!", "", Color("8ab8ff"))
		return
	var ct := Skills.begin(world, self, id, rank)
	if ct < 0.0:
		return
	Game.mp -= cost
	cd[slot] = Data.skill_cd(id, rank)
	cd_max[slot] = cd[slot]
	combat_t = 0.0
	if ct > 0.0:
		state = S.CAST
		cast_t = ct
		queued = false
		combo = 0
		face_aim = aim_vector(140.0)
		if abs(face_aim.x) > abs(face_aim.y):
			face = Vector2(signf(face_aim.x), 0)
		else:
			face = Vector2(0, signf(face_aim.y))
		pending_cast = id
		_play("cast", true)

func use_potion() -> bool:
	if potion_cd > 0.0:
		Sfx.play("error", -8.0)
		return false
	for id in ["potion", "hi_potion", "herb"]:
		if Game.count(id) > 0:
			if Game.hp >= max_hp - 1.0:
				return false
			Game.add_item(id, -1)
			var amt: float = float(Data.ITEMS[id]["heal_hp"])
			Game.hp = minf(max_hp, Game.hp + amt)
			potion_cd = 6.0
			Fx.text(world, global_position + Vector2(0, -44), "+%d" % int(amt), Color("6aff9a"), true)
			Fx.burst(world, global_position + Vector2(0, -20), [Color("6aff9a"), Color("ffffff")], 12, 40.0, 0.8, 3.0, -50.0)
			Sfx.play("heal", -3.0)
			return true
	Game.toast.emit("Sem poções!", "potion_r", Color("ff8a8a"))
	Sfx.play("error", -6.0)
	return false

func take_hit(h: Dictionary) -> float:
	if dead or iframes > 0.0 or state == S.ROLL or locked:
		return 0.0
	var s := stats_cache
	var dmg: float = maxf(1.0, float(h["dmg"]) * Game.difficulty * randf_range(0.93, 1.07) - float(s["def"]) * 0.5)
	if shield > 0.0:
		var ab := minf(shield, dmg)
		shield -= ab
		dmg -= ab
		Fx.text(world, global_position + Vector2(0, -44), "-%d" % int(ab), Color("9ad8ff"))
		Sfx.play("shield", -4.0)
		if dmg <= 0.0:
			iframes = 0.3
			return 0.0
	Game.hp -= dmg
	iframes = 0.8
	flash_t = 0.14
	hurt_t = 0.28
	combat_t = 0.0
	Fx.text(world, global_position + Vector2(0, -46), "-%d" % int(dmg), Color("ff6a7a"), true)
	Fx.burst(world, hit_center(), [Color("ff5a6a"), Color("ffffff")], 10, 110.0, 0.35, 3.0)
	Fx.shake(world, 5.0)
	Fx.hitstop(0.07)
	Sfx.play("hurt", -2.0)
	var src: Vector2 = h.get("src", global_position + Vector2(0, 8))
	var kbf: float = float(h.get("kb", 120.0))
	kb_vel = (global_position - src).normalized() * kbf * 1.4
	if state != S.ATTACK or dmg > max_hp * 0.14:
		state = S.HURT
		combo = 0
		sprite.rotation = 0.0
		_play("hurt", true)
	if h.has("status"):
		apply_status(h["status"], float(h.get("status_t", 1.5)))
	if Game.hp <= 0.0:
		Game.hp = 0.0
		die()
	return dmg

func heal(amount: float) -> void:
	Game.hp = minf(max_hp, Game.hp + amount)
	Fx.text(world, global_position + Vector2(0, -44), "+%d" % int(amount), Color("6aff9a"), true)

func die() -> void:
	dead = true
	state = S.DEAD
	_play("hurt", true)
	Sfx.play("die")
	var tw := create_tween()
	tw.tween_property(sprite, "rotation", PI / 2.0, 0.5).set_trans(Tween.TRANS_QUAD)
	world.on_player_died()
