class_name Enemy
extends Combatant
## Enemy with telegraphed attacks, poise/stagger, elite & boss variants.

var def: Dictionary = {}
var id := ""
var is_boss := false
var is_elite := false
var extra_loot: Array = []
var spawn_id := ""
var summoned := false
var state := "idle"
var st := 0.0
var aggro := false
var home := Vector2.ZERO
var poise := 0.0
var tele: Dictionary = {}
var wander_t := 0.0
var wander_to := Vector2.ZERO
var lock_dir := Vector2.RIGHT
var target_pos := Vector2.ZERO
var counter := 0.0
var pattern := 0
var phase := 1
var contact_cd := 0.0
var bar_t := 0.0
var humanoid := false
var path: Array = []
var path_t := 0.0
var fly := false
var scale_f := 1.0
var dmg_mul := 1.0
var tele_node: Node2D
var bar_node: Node2D
var hit_frame := 3
var anim_t := 0.0
var shoot_cd := 1.5

static var _sb_bg: StyleBoxFlat
static var _sb_fg: StyleBoxFlat

func setup(w: World, def_id: String, elite := false, boss := false) -> void:
	world = w
	id = def_id
	def = Data.ENEMIES[def_id]
	team = "enemy"
	is_boss = boss or bool(def.get("boss", false))
	is_elite = elite and not is_boss
	fly = bool(def.get("fly", false))
	radius = float(def.get("r", 10)) 
	hit_h = float(def.get("h", 14))
	max_hp = float(def["hp"]) * (2.2 if is_elite else 1.0)
	hp = max_hp
	dmg_mul = 1.25 if is_elite else 1.0
	scale_f = float(def.get("scale", 1.0)) * (1.18 if is_elite else 1.0)
	collision_layer = 4
	collision_mask = 0 if fly else 1
	motion_mode = CharacterBody2D.MOTION_MODE_FLOATING
	var sf := SpriteLib.load_frames(def["sheet"])
	humanoid = sf.has_animation("idle_down")
	setup_sprite(sf, SpriteLib.offset_y(sf) * scale_f, scale_f)
	if is_elite:
		mat.set_shader_parameter("outline", 0.9)
		mat.set_shader_parameter("outline_color", Color("ffd84a"))
	var cs := CollisionShape2D.new()
	var shp := CircleShape2D.new()
	shp.radius = maxf(5.0, radius * 0.6)
	cs.shape = shp
	cs.position = Vector2(0, -shp.radius)
	add_child(cs)
	home = global_position
	sprite.frame_changed.connect(_on_frame)
	sprite.animation_finished.connect(_on_anim_done)
	tele_node = TeleNode.new()
	tele_node.top_level = true
	tele_node.z_index = 3
	add_child(tele_node)
	bar_node = BarNode.new()
	bar_node.z_index = 70
	add_child(bar_node)
	add_to_group("enemies")
	if _sb_bg == null:
		_sb_bg = StyleBoxFlat.new()
		_sb_bg.bg_color = Color(0.05, 0.02, 0.1, 0.85)
		_sb_bg.set_corner_radius_all(4)
		_sb_fg = StyleBoxFlat.new()
		_sb_fg.set_corner_radius_all(4)
	play("idle")
	wander_to = home
	sprite.frame = randi() % 3

func name_text() -> String:
	return ("★ " if is_elite else "") + str(def["name"])

# ------------------------------------------------------------------ animation
func play(base: String, restart := false) -> void:
	var an := ""
	if humanoid:
		var d := "down"
		if abs(face.x) > abs(face.y):
			d = "left"
			sprite.flip_h = face.x > 0
		else:
			sprite.flip_h = false
			d = "down" if face.y > 0 else "up"
		an = "%s_%s" % [base, d]
	else:
		an = "%s_right" % base
		if absf(face.x) > 0.1:
			sprite.flip_h = face.x < 0
	if not sprite.sprite_frames.has_animation(an):
		an = "idle_right" if not humanoid else "idle_down"
	if sprite.animation != an or restart:
		sprite.play(an)

func _on_frame() -> void:
	pass

func _on_anim_done() -> void:
	if state == "dead":
		sprite.pause()

# ------------------------------------------------------------------ helpers
func player() -> Player:
	return world.player

func to_player() -> Vector2:
	return world.player.global_position - global_position

func los_to(p: Vector2) -> bool:
	return world.has_los(global_position + Vector2(0, -8), p + Vector2(0, -8))

func move_toward_pos(target: Vector2, speed: float, dt: float, use_path := true) -> void:
	var dest := target
	if use_path and not fly and not los_to(target):
		path_t -= dt
		if path.is_empty() or path_t <= 0.0:
			path = world.find_path(global_position, target)
			path_t = 0.35
		while not path.is_empty() and global_position.distance_to(path[0]) < 8.0:
			path.pop_front()
		if not path.is_empty():
			dest = path[0]
	var dir := (dest - global_position).normalized()
	velocity = dir * speed + kb_vel
	if absf(dir.x) > 0.2 or absf(dir.y) > 0.2:
		face = dir
	move_and_slide()

func hit_player(mult := 1.0, kb := 130.0, status_name := "", status_t := 1.5) -> void:
	var h := {"dmg": float(def["dmg"]) * mult * dmg_mul, "src": global_position, "kb": kb, "elem": str(def.get("elem", "phys"))}
	if status_name != "":
		h["status"] = status_name
		h["status_t"] = status_t
	world.player.take_hit(h)

func contact_check(r: float, mult := 1.0, kb := 140.0) -> void:
	if contact_cd > 0.0:
		return
	var d := world.player.hit_center() - hit_center()
	if d.length() < r + 8.0:
		hit_player(mult, kb)
		contact_cd = 0.6

func set_tele(kind: String, pos: Vector2, r: float, dur: float, ang := 0.0, length := 0.0) -> void:
	tele = {"kind": kind, "pos": pos, "r": r, "t": 0.0, "dur": dur, "ang": ang, "len": length}
	Sfx.play("tele", -10.0)

func clear_tele() -> void:
	tele = {}

func go(s: String) -> void:
	state = s
	st = 0.0

# ------------------------------------------------------------------ main loop
func _physics_process(dt: float) -> void:
	_tick_common(dt)
	if world == null or dead:
		return
	st += dt
	contact_cd = maxf(0.0, contact_cd - dt)
	if bar_t > 0.0:
		bar_t -= dt
	if not tele.is_empty():
		tele["t"] += dt
	var p := world.player
	if state == "stagger":
		velocity = kb_vel
		kb_vel *= 0.86
		move_and_slide()
		if st > 0.45 and not has_status("freeze") and not has_status("stun"):
			go("chase")
			clear_tele()
		return
	if has_status("freeze") or has_status("stun"):
		velocity = kb_vel
		kb_vel *= 0.86
		move_and_slide()
		sprite.pause() if has_status("freeze") else null
		return
	elif not sprite.is_playing() and state != "dead":
		sprite.play()
	if absf(kb_vel.x) + absf(kb_vel.y) > 5.0 and state != "leap":
		kb_vel *= 0.86
	var dd := to_player().length()
	if not aggro and p != null and not p.dead and not world.player.locked:
		var aggro_r: float = float(def.get("aggro", 150.0))
		if dd < aggro_r and (dd < 70.0 or los_to(p.global_position)):
			_wake()
	elif aggro and (p == null or p.dead):
		aggro = false
		go("idle")
	if not aggro:
		_idle(dt)
		return
	if dd > 520.0 and not is_boss:
		aggro = false
		go("idle")
		return
	var spd_m := 0.55 if has_status("slow") else 1.0
	match str(def["ai"]):
		"hop": _ai_hop(dt, spd_m, dd)
		"bat": _ai_bat(dt, spd_m, dd)
		"pounce": _ai_pounce(dt, spd_m, dd)
		"melee": _ai_melee(dt, spd_m, dd)
		"archer": _ai_ranged(dt, spd_m, dd, "arrow")
		"caster": _ai_ranged(dt, spd_m, dd, "orb")
		_: _ai_melee(dt, spd_m, dd)
	_separate(dt)

func _wake() -> void:
	aggro = true
	go("chase")
	Sfx.play("alert", -8.0)
	for e in world.enemies:
		if e != self and not e.aggro and not e.dead and e.global_position.distance_to(global_position) < 130.0:
			e.aggro = true
			e.go("chase")

func _idle(dt: float) -> void:
	wander_t -= dt
	if wander_t <= 0.0:
		wander_t = randf_range(1.5, 3.5)
		wander_to = home + Vector2(randf_range(-40, 40), randf_range(-30, 30))
	if state != "idle":
		go("idle")
	var d := wander_to - global_position
	if d.length() > 6.0 and not is_boss:
		velocity = d.normalized() * float(def["spd"]) * 0.35
		face = d.normalized()
		move_and_slide()
		play("walk")
	else:
		velocity = Vector2.ZERO
		play("idle")

func _separate(_dt: float) -> void:
	for e in world.enemies:
		if e == self or e.dead:
			continue
		var d: Vector2 = global_position - e.global_position
		var m: float = radius + e.radius
		if d.length() < m and d.length() > 0.01:
			global_position += d.normalized() * (m - d.length()) * 0.15

# ------------------------------------------------------------------ AI: slimes
func _ai_hop(dt: float, spd_m: float, dd: float) -> void:
	match state:
		"chase":
			velocity = Vector2.ZERO
			face = to_player().normalized()
			play("idle")
			if st > randf_range(0.7, 1.3):
				go("windup")
				lock_dir = to_player().normalized()
				var land: Vector2 = global_position + lock_dir * minf(dd, 110.0)
				target_pos = land
				set_tele("circle", land, 22.0, 0.5)
				play("attack", true)
				sprite.pause()
				sprite.frame = 0
		"windup":
			velocity = Vector2.ZERO
			sprite.frame = 0 if st < 0.3 else 1
			if st >= 0.5:
				clear_tele()
				go("leap")
				play("walk", true)
				sprite.frame = 2
				sprite.play()
				sprite.speed_scale = 1.0
		"leap":
			# hop frames: 0-1 crouch, 2 launch, 3-5 air, 6-7 land
			if st < 0.4:
				var dir := (target_pos - global_position)
				var sp := minf(dir.length() / 0.38, float(def["spd"]) * 3.4 * spd_m)
				velocity = dir.normalized() * sp if dir.length() > 3.0 else Vector2.ZERO
				move_and_slide()
				if st > 0.1:
					contact_check(radius + 8.0, 1.0, 150.0)
			else:
				velocity = Vector2.ZERO
			if st >= 0.62:
				go("recover")
				play("idle")
		"recover":
			velocity = Vector2.ZERO
			if st >= 0.5:
				go("chase")
		_:
			go("chase")

# ------------------------------------------------------------------ AI: bat
func _ai_bat(dt: float, spd_m: float, dd: float) -> void:
	var p := world.player.global_position
	match state:
		"chase":
			var ang := Time.get_ticks_msec() / 1000.0 * 1.6 + float(get_instance_id() % 7)
			var orbit := p + Vector2(cos(ang), sin(ang) * 0.6) * 62.0
			move_toward_pos(orbit, float(def["spd"]) * spd_m, dt, false)
			play("walk")
			if st > 2.0 and dd < 200.0:
				go("windup")
				lock_dir = to_player().normalized()
				set_tele("line", global_position, 8.0, 0.4, lock_dir.angle(), minf(dd + 40.0, 220.0))
				play("attack", true)
				sprite.pause()
				sprite.frame = 0
		"windup":
			velocity = Vector2.ZERO
			if st >= 0.4:
				clear_tele()
				go("dive")
				sprite.play()
				Sfx.play("swoosh", -6.0)
		"dive":
			velocity = lock_dir * 240.0 * spd_m
			move_and_slide()
			contact_check(radius + 6.0, 1.0, 120.0)
			if st >= 0.38:
				go("retreat")
				play("walk", true)
		"retreat":
			velocity = -lock_dir * 70.0 + Vector2(0, -20)
			move_and_slide()
			if st >= 0.7:
				go("chase")
		_:
			go("chase")

# ------------------------------------------------------------------ AI: wolf-like pouncers
func _ai_pounce(dt: float, spd_m: float, dd: float) -> void:
	var p := world.player.global_position
	match state:
		"chase":
			# circle at distance, then commit
			if dd > 110.0:
				move_toward_pos(p, float(def["spd"]) * spd_m, dt)
				play("walk")
			else:
				var side := Vector2(-to_player().y, to_player().x).normalized() * (1.0 if int(get_instance_id()) % 2 == 0 else -1.0)
				velocity = (side * 0.7 - to_player().normalized() * 0.15) * float(def["spd"]) * 0.55 * spd_m
				face = to_player().normalized()
				move_and_slide()
				play("walk")
			if dd < 135.0 and st > 0.9 and los_to(p):
				go("windup")
				lock_dir = to_player().normalized()
				face = lock_dir
				set_tele("line", global_position, 10.0, 0.55, lock_dir.angle(), 150.0)
				play("attack", true)
				sprite.pause()
				sprite.frame = 0
				Sfx.play("growl", -6.0)
		"windup":
			velocity = Vector2.ZERO
			sprite.frame = 0 if st < 0.3 else 1
			if st >= 0.55:
				clear_tele()
				go("leap")
				sprite.frame = 2
				sprite.play()
				Sfx.play("swoosh", -5.0)
		"leap":
			velocity = lock_dir * 290.0 * spd_m
			move_and_slide()
			contact_check(radius + 8.0, 1.0, 190.0)
			if st >= 0.36:
				go("recover")
				play("idle")
		"recover":
			velocity = Vector2.ZERO
			if st >= 0.75:
				go("chase")
		_:
			go("chase")

# ------------------------------------------------------------------ AI: melee fighters (goblins, skeletons, soldiers)
func _ai_melee(dt: float, spd_m: float, dd: float) -> void:
	var p := world.player.global_position
	var reach: float = float(def.get("reach", 34.0))
	match state:
		"chase":
			if dd > reach - 6.0:
				move_toward_pos(p, float(def["spd"]) * spd_m, dt)
				play("walk")
			else:
				velocity = Vector2.ZERO
				face = to_player().normalized()
				play("idle")
			if dd < reach + 4.0 and st > 0.55:
				go("windup")
				lock_dir = to_player().normalized()
				face = lock_dir
				set_tele("cone", global_position + Vector2(0, -8), reach + 8.0, 0.5, lock_dir.angle())
				play("attack", true)
				sprite.speed_scale = 0.3
		"windup":
			velocity = Vector2.ZERO
			if st >= 0.5:
				clear_tele()
				go("strike")
				sprite.speed_scale = 1.4
				_melee_strike(reach)
				Sfx.play("swing", -6.0, 0.8)
		"strike":
			velocity = lock_dir * 40.0
			move_and_slide()
			if st >= 0.3:
				go("recover")
				sprite.speed_scale = 1.0
				play("idle")
		"recover":
			velocity = Vector2.ZERO
			if st >= 0.5:
				go("chase")
		_:
			go("chase")

func _melee_strike(reach: float) -> void:
	Fx.slash(world, global_position + Vector2(0, -14), lock_dir.angle(), reach * 0.8, Color("ff7a8a"), 2.0, false, 0.22, 7.0)
	var d := world.player.hit_center() - (global_position + Vector2(0, -8))
	if d.length() < reach + 8.0 and absf(lock_dir.angle_to(d)) < 1.2:
		hit_player(1.0, 150.0)

# ------------------------------------------------------------------ AI: ranged (archers, casters)
func _ai_ranged(dt: float, spd_m: float, dd: float, kind: String) -> void:
	var p := world.player.global_position
	match state:
		"chase":
			var want: float = float(def.get("keep", 150.0))
			if dd < want - 40.0:
				move_toward_pos(global_position - to_player(), float(def["spd"]) * spd_m, dt, false)
				play("walk")
			elif dd > want + 40.0:
				move_toward_pos(p, float(def["spd"]) * spd_m, dt)
				play("walk")
			else:
				velocity = Vector2.ZERO
				face = to_player().normalized()
				play("idle")
			shoot_cd -= dt
			if shoot_cd <= 0.0 and dd < 260.0 and los_to(p):
				go("windup")
				lock_dir = to_player().normalized()
				face = lock_dir
				set_tele("line", global_position + Vector2(0, -12), 3.0, 0.55, lock_dir.angle(), minf(dd, 220.0))
				play("attack", true)
				sprite.speed_scale = 0.3
		"windup":
			velocity = Vector2.ZERO
			if st >= 0.55:
				clear_tele()
				go("recover")
				sprite.speed_scale = 1.0
				_fire_shot(kind)
				shoot_cd = randf_range(1.8, 2.8)
		"recover":
			velocity = Vector2.ZERO
			if st >= 0.5:
				go("chase")
		_:
			go("chase")

func _fire_shot(kind: String) -> void:
	var origin := global_position + Vector2(0, -16)
	var dir := (world.player.hit_center() - origin).normalized()
	var spread: Array = [0.0]
	if str(def.get("pattern", "")) == "triple":
		spread = [-0.28, 0.0, 0.28]
	for sp in spread:
		var pr := Projectile.new()
		pr.setup(world, origin, dir.rotated(sp) * float(def.get("shot_speed", 170.0)), "enemy", float(def["dmg"]) * dmg_mul, kind, str(def.get("elem", "phys")))
		world.entities.add_child(pr)
	Sfx.play("arrow" if kind == "arrow" else "magic", -6.0)

# ------------------------------------------------------------------ damage
func take_hit(h: Dictionary) -> float:
	if dead:
		return 0.0
	var elem: String = str(h.get("elem", "phys"))
	var dmg: float = float(h["dmg"])
	var tag := ""
	if elem in def.get("weak", []):
		dmg *= 1.5
		tag = "!"
	if elem in def.get("resist", []):
		dmg *= 0.6
		tag = "-"
	dmg = maxf(1.0, dmg - float(def.get("def", 0)) * 0.5)
	var crit: bool = bool(h.get("crit", false))
	hp -= dmg
	flash_t = 0.1
	bar_t = 3.5
	if not aggro:
		_wake()
	var col: Color = Data.ELEM_COLORS.get(elem, Color.WHITE)
	if crit:
		col = Color("ffd84a")
	Fx.text(world, global_position + Vector2(0, -hit_h - 14), "%d%s" % [int(dmg), tag], col, crit or tag == "!" or bool(h.get("heavy", false)))
	Fx.burst(world, hit_center(), [col, Color.WHITE], 8 if crit else 5, 100.0 if crit else 70.0, 0.3, 3.0)
	Sfx.play("crit" if crit else "hit", -3.0, randf_range(0.92, 1.1))
	Fx.hitstop(0.075 if (crit or h.get("heavy", false)) else 0.04)
	Fx.shake(world, 3.0 if crit else 1.3)
	var ls: float = float(h.get("lifesteal", 0.0))
	if ls > 0.0:
		world.player.heal(maxf(1.0, dmg * ls / 100.0))
	if not is_boss:
		var kbf: float = float(h.get("kb", 0.0))
		if kbf > 0.0:
			var from: Vector2 = h.get("src", world.player.global_position)
			kb_vel = (global_position - from).normalized() * kbf
	var thresh := max_hp * (0.5 if is_elite else 0.3) if not is_boss else max_hp * 2.0
	poise += float(h.get("poise", 0.0)) * (dmg / maxf(1.0, max_hp)) * 3.2 + (dmg / max_hp if h.get("heavy", false) else 0.0)
	if not is_boss and (poise >= 0.25 or h.get("stagger", false)) and state not in ["stagger", "leap", "dive"]:
		poise = 0.0
		go("stagger")
		clear_tele()
		play("hurt", true)
		sprite.speed_scale = 1.0
	if h.has("freeze"):
		if not is_boss:
			apply_status("freeze", float(h["freeze"]))
			clear_tele()
	if h.has("stun") and not is_boss:
		apply_status("stun", float(h["stun"]))
		clear_tele()
	if h.has("slow"):
		apply_status("slow", float(h["slow"]))
	if h.has("burn"):
		apply_status("burn", float(h["burn"]), maxf(1.0, dmg * 0.18))
	if hp <= 0.0:
		die()
	thresh = thresh
	return dmg

func on_dot(amount: float, elem: String) -> void:
	if dead:
		return
	hp -= amount
	bar_t = 3.0
	Fx.text(world, global_position + Vector2(0, -hit_h - 10), "%d" % int(amount), Data.ELEM_COLORS.get(elem, Color.WHITE))
	if hp <= 0.0:
		die()

func die() -> void:
	if dead:
		return
	dead = true
	state = "dead"
	aggro = false
	clear_tele()
	velocity = Vector2.ZERO
	collision_layer = 0
	world.enemies.erase(self)
	remove_from_group("enemies")
	Game.kills += 1
	Sfx.play("die", -2.0)
	if not summoned:
		var lv_diff: int = Game.level - int(def["level"])
		var factor := clampf(1.0 - lv_diff * 0.14, 0.1, 1.3)
		var xp := int(float(def["xp"]) * factor * (2.5 if is_elite else 1.0))
		Fx.text(world, global_position + Vector2(0, -hit_h - 30), "+%d XP" % xp, Color("9ad8ff"))
		Game.gain_xp(xp)
		Loot.drop_for(world, self)
	Fx.burst(world, hit_center(), [Color.WHITE, Color("ffd84a"), Data.ELEM_COLORS.get(str(def.get("elem", "phys")), Color.WHITE)], 14, 130.0, 0.6, 3.0)
	if is_boss:
		Fx.shake(world, 9.0)
		Fx.hitstop(0.25)
		Fx.glow_flash(world, hit_center(), Color.WHITE, 220.0, 0.6)
	world.on_enemy_killed(self)
	if sprite.sprite_frames.has_animation("death_right") or sprite.sprite_frames.has_animation("death_down"):
		play("death", true)
	var tw := create_tween()
	tw.tween_interval(0.5)
	tw.tween_method(func(v: float): mat.set_shader_parameter("dissolve", v), 0.0, 1.0, 0.55)
	tw.tween_callback(queue_free)

# ------------------------------------------------------------------ inner draw nodes
class TeleNode extends Node2D:
	func _process(_dt: float) -> void:
		queue_redraw()
	func _draw() -> void:
		var e: Enemy = get_parent()
		var t: Dictionary = e.tele
		if t.is_empty():
			return
		var f: float = clampf(float(t["t"]) / float(t["dur"]), 0.0, 1.0)
		var pulse: float = 0.18 + 0.12 * sin(float(t["t"]) * 26.0)
		var col := Color(1.0, 0.2, 0.28)
		var pos: Vector2 = t["pos"]
		match t["kind"]:
			"circle":
				draw_set_transform(pos, 0, Vector2(1, 0.62))
				draw_circle(Vector2.ZERO, float(t["r"]), Color(col, pulse + 0.1))
				draw_circle(Vector2.ZERO, float(t["r"]) * f, Color(col, 0.35))
				draw_arc(Vector2.ZERO, float(t["r"]), 0, TAU, 40, Color(1, 0.4, 0.45, 0.9), 2.0, true)
			"line":
				var a: float = t["ang"]
				var len: float = t["len"]
				var w: float = t["r"]
				var dir := Vector2.from_angle(a)
				var nrm := dir.orthogonal() * w
				var pts := PackedVector2Array([pos + nrm, pos + dir * len + nrm, pos + dir * len - nrm, pos - nrm])
				draw_colored_polygon(pts, Color(col, pulse))
				var fl: float = len * f
				var pts2 := PackedVector2Array([pos + nrm, pos + dir * fl + nrm, pos + dir * fl - nrm, pos - nrm])
				draw_colored_polygon(pts2, Color(col, 0.3))
				draw_polyline(PackedVector2Array([pos + nrm, pos + dir * len + nrm, pos + dir * len - nrm, pos - nrm, pos + nrm]), Color(1, 0.4, 0.45, 0.8), 1.5)
			"cone":
				var a2: float = t["ang"]
				var r: float = t["r"]
				var pts3 := PackedVector2Array([pos])
				for i in 13:
					pts3.append(pos + Vector2.from_angle(a2 - 1.1 + 2.2 * i / 12.0) * r)
				draw_colored_polygon(pts3, Color(col, pulse))
				var pts4 := PackedVector2Array([pos])
				for i in 13:
					pts4.append(pos + Vector2.from_angle(a2 - 1.1 + 2.2 * i / 12.0) * r * f)
				draw_colored_polygon(pts4, Color(col, 0.3))

class BarNode extends Node2D:
	func _process(_dt: float) -> void:
		var e: Enemy = get_parent()
		visible = (e.bar_t > 0.0 or e.is_elite) and not e.dead and not e.is_boss
		if visible:
			queue_redraw()
	func _draw() -> void:
		var e: Enemy = get_parent()
		var w := 38.0 if not e.is_elite else 48.0
		var y := -(e.hit_h * 2.0 + 22.0) * e.scale_f * 0.8
		var frac: float = clampf(e.hp / e.max_hp, 0.0, 1.0)
		draw_style_box(Enemy._sb_bg, Rect2(-w / 2 - 1, y - 1, w + 2, 7))
		var fg: StyleBoxFlat = Enemy._sb_fg
		fg.bg_color = Color("ff5a6a").lerp(Color("ffd84a"), 1.0 - frac) if not e.is_elite else Color("ffb040")
		if frac > 0.02:
			draw_style_box(fg, Rect2(-w / 2, y, maxf(4.0, w * frac), 5))
		if e.is_elite:
			var f := Fx.font_num if Fx.font_num else ThemeDB.fallback_font
			draw_string(f, Vector2(-w / 2, y - 3), e.name_text(), HORIZONTAL_ALIGNMENT_LEFT, -1, 9, Color("ffd84a"))
