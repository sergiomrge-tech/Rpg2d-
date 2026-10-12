class_name Player
extends Actor
## The reincarnated hero. Unlimited sprint/weapon combos, i-frame roll, Spark magic that evolves.

enum St { FREE, ATTACK, CAST, ROLL, HURT, DEAD }

static var I: Player

var gs: GameState
var mp := 0.0
var input_locked := false
var scripted_move := Vector2.ZERO

var state: int = St.FREE
var combo := 0
var buffered_attack := false
var state_t := 0.0
var roll_dir := Vector2.ZERO
var move_dir := Vector2.ZERO
var step_t := 0.0
var hex_slow := 0.0
var venom := 0.0
var venom_tick := 0.0
var sonic := 0.0
var cast_action := ""
var special_strike := false
var special_cd := 0.0
var arrow_n := 0
var lock_target: Enemy = null            # target lock (T): faces, aims and homes the attacks at this enemy
var _lock_marker: LockMarker = null
const LOCK_RANGE := 13.0 * 64.0
var skill_cd := {"r": 0.0, "f": 0.0}
var skill_cd_max := {"r": 1.0, "f": 1.0}

const WALK := 4.0 * T
const RUN := 6.4 * T
const ROLL_SPD := 10.5 * T
const CAST_COST := 12.0


static func spawn(at: Vector2, state_: GameState) -> Player:
	var p := Player.new()
	p.gs = state_
	p.collision_layer = 2
	p.collision_mask = 1 | 4 | 8
	p.build(HeroClasses.sheet_for(state_.class_id), 1.25, 0.42, 0.32)
	p.max_hp = state_.hp_max()
	p.hp = p.max_hp
	p.mp = state_.max_mp
	p.anim.hit.connect(p._on_anim_hit)
	p.anim.ended.connect(p._on_anim_end)
	Game.world.add_entity(p, at)
	p.anim.play("idle")
	I = p
	return p


func apply_venom(sec: float) -> void:
	if dead:
		return
	venom = maxf(venom, sec)
	venom_tick = maxf(venom_tick, 0.85)
	Fx.toast("Veneno!", Color(0.66, 1.0, 0.48), pos() + Vector2.UP * 2.4 * T)


func apply_sonic(sec: float) -> void:
	if dead:
		return
	sonic = maxf(sonic, sec)
	Fx.toast("Atordoado!", Color(0.51, 0.9, 1.0), pos() + Vector2.UP * 2.4 * T)


func apply_hex_slow(sec: float) -> void:
	if dead:
		return
	hex_slow = maxf(hex_slow, sec)
	Fx.toast("Lentidão!", Color(0.81, 0.54, 1.0), pos() + Vector2.UP * 2.4 * T)


func _read_move() -> Vector2:
	if input_locked:
		return scripted_move
	if sonic > 0.0:
		return Vector2.ZERO
	var v := Vector2.ZERO
	if Input.is_physical_key_pressed(KEY_A) or Input.is_physical_key_pressed(KEY_LEFT): v.x -= 1
	if Input.is_physical_key_pressed(KEY_D) or Input.is_physical_key_pressed(KEY_RIGHT): v.x += 1
	if Input.is_physical_key_pressed(KEY_W) or Input.is_physical_key_pressed(KEY_UP): v.y -= 1
	if Input.is_physical_key_pressed(KEY_S) or Input.is_physical_key_pressed(KEY_DOWN): v.y += 1
	v += Game.touch_move
	return v.normalized() if v.length_squared() > 1.0 else v


func _pressed(keys: Array) -> bool:
	if input_locked or sonic > 0.0:
		return false
	for k in keys:
		if Game.consume(k):
			return true
	return false


func _physics_process(dt: float) -> void:
	if dead:
		return
	state_t += dt
	hex_slow = maxf(0.0, hex_slow - dt)
	sonic = maxf(0.0, sonic - dt)
	special_cd = maxf(0.0, special_cd - dt)
	for k in skill_cd:
		skill_cd[k] = maxf(0.0, float(skill_cd[k]) - dt)
	gs.tick_buffs(dt)
	gs.hp_frac = hp / maxf(1.0, gs.hp_max())
	_lock_upkeep()
	if gs.class_id == "paladin":
		hp = minf(gs.hp_max(), hp + gs.hp_max() * float(SkillTree.passive_v("paladin", gs.level)[0]) / 100.0 * dt)
	if venom > 0.0:
		venom = maxf(0.0, venom - dt)
		venom_tick -= dt
		if venom_tick <= 0.0:
			venom_tick = 0.85
			invuln = 0.0
			hurt(3.0, pos(), 0.0, 0.0)
			if dead:
				return
	move_dir = _read_move()
	var run := (not input_locked) and (Input.is_physical_key_pressed(KEY_SHIFT) or Game.touch_run)

	mp = minf(gs.max_mp, mp + gs.mp_regen() * dt)

	if _pressed([KEY_J, -MOUSE_BUTTON_LEFT]): _try_attack()
	if _pressed([KEY_K, -MOUSE_BUTTON_RIGHT]): _try_cast()
	if _pressed([KEY_SPACE]): _try_roll()
	if _pressed([KEY_Q]): _use_potion()
	if _pressed([KEY_T]): lock_cycle()
	if _pressed([KEY_R]): _try_skill("r")
	if _pressed([KEY_F]): _try_skill("f")
	if _pressed([KEY_E]): Game.interact(self)

	match state:
		St.FREE:
			if move_dir.length_squared() > 0.01:
				var can_run := run
				face(Util.facing_from(move_dir if not lock_ok() else lock_dir(), facing))
				anim.play("run" if can_run else "walk")
				var move_factor: float = float(HeroClasses.info(gs.class_id)["move"]) * gs.move_mult()
				velocity = move_dir * (RUN if can_run else WALK) * move_factor * (0.52 if hex_slow > 0.0 else 1.0) + knock
				step_t -= dt * (1.5 if can_run else 1.0)
				if step_t <= 0.0:
					step_t = 0.36
					Sfx.step(Game.map_name, 1.25 if can_run else 1.0)
					if can_run:
						Fx.dust(pos(), 0.5)
			else:
				anim.play("idle")
				if lock_ok():
					face(Util.facing_from(lock_dir(), facing))
				velocity = knock
		St.ATTACK:
			var n := anim.normalized()
			var lunge := ((5.5 if combo == 3 else 3.2) * (1.0 - n / 0.45) if n < 0.45 else 0.0) * T
			if n < 0.2 and move_dir.length_squared() > 0.01 and not lock_ok():
				face(Util.facing_from(move_dir, facing))
			velocity = aim_dir() * lunge + knock
			if buffered_attack and n > 0.58 and combo < 3:
				buffered_attack = false
				_start_attack(combo + 1)
		St.CAST:
			velocity = knock
		St.ROLL:
			var k := clampf(1.0 - state_t / 0.48, 0.0, 1.0)
			velocity = roll_dir * ROLL_SPD * (0.35 + 0.65 * k)
			if state_t > 0.46:
				invuln = minf(invuln, 0.0)
		St.HURT:
			velocity = knock
			if state_t > 0.32:
				_to_free()
	move_and_slide()
	knock = knock.move_toward(Vector2.ZERO, 30.0 * T * dt)


func _to_free() -> void:
	anim.speed = 1.0
	state = St.FREE
	state_t = 0.0
	anim.play("idle", true)


# ------------------------------------------------------------------ target lock
func lock_ok() -> bool:
	return lock_target != null and is_instance_valid(lock_target) and not lock_target.dead and not dead


func lock_dir() -> Vector2:
	var d := (lock_target.pos() + Vector2.UP * 0.4 * T) - (pos() + Vector2.UP * 0.55 * T)
	return d.normalized() if d.length() > 4.0 else Util.facing_vec(facing)


## Direction of the next strike: toward the locked enemy, otherwise where the hero faces.
func aim_dir() -> Vector2:
	return lock_dir() if lock_ok() else Util.facing_vec(facing)


func _set_lock(e: Enemy) -> void:
	if _lock_marker != null and is_instance_valid(_lock_marker):
		_lock_marker.queue_free()
	_lock_marker = null
	lock_target = e
	if e == null:
		return
	_lock_marker = LockMarker.new()
	var sc := absf(e.anim.scale.y)
	_lock_marker.radius = clampf(36.0 * sc, 34.0, 120.0)
	_lock_marker.head = clampf(120.0 * sc, 110.0, 300.0)
	_lock_marker.boss = bool(e.def["boss"])
	e.add_child(_lock_marker)


## T: lock the nearest enemy; press again to jump to the next one; after the last one the lock is released.
func lock_cycle() -> void:
	var c: Array = []
	for e in Enemy.all:
		if is_instance_valid(e) and not e.dead and (e.global_position - global_position).length() <= LOCK_RANGE:
			c.append(e)
	c.sort_custom(func(a, b): return (a.global_position - global_position).length() < (b.global_position - global_position).length())
	if c.is_empty():
		_set_lock(null)
		Fx.toast("Nenhum alvo por perto", Color(1, 0.8, 0.6))
		return
	if not lock_ok():
		_set_lock(c[0])
		Sfx.play("ui", 0.4, 1.4)
		return
	var i := c.find(lock_target)
	if i >= 0 and i + 1 < c.size():
		_set_lock(c[i + 1])
		Sfx.play("ui", 0.4, 1.6)
	elif i < 0:
		_set_lock(c[0])
	else:
		_set_lock(null)
		Sfx.play("ui", 0.3, 0.8)


func _lock_upkeep() -> void:
	if lock_target == null:
		return
	if not lock_ok():
		var gone := lock_target == null or not is_instance_valid(lock_target)
		var from := global_position if gone else lock_target.global_position
		_set_lock(null)
		if not dead:
			# the target died: jump to the closest living enemy near the fight, otherwise release
			var nxt := Enemy.nearest(from, 9.0 * T)
			if nxt != null and (nxt.global_position - global_position).length() <= LOCK_RANGE:
				_set_lock(nxt)
		return
	if (lock_target.global_position - global_position).length() > LOCK_RANGE * 1.3:
		_set_lock(null)


func ci_attack() -> void: _try_attack()
func ci_cast() -> void: _try_cast()


## Tiro Certeiro (archer passive): every Nth arrow volley hits much harder.
func _arrow_mult() -> float:
	if gs.class_id != "archer":
		return 1.0
	arrow_n += 1
	if arrow_n >= int(SkillTree.passive_v("archer", gs.level)[0]):
		arrow_n = 0
		Fx.toast("Tiro Certeiro!", Color(0.7, 1.0, 0.6), pos() + Vector2.UP * 1.6 * T)
		return 1.8
	return 1.0


func _try_attack() -> void:
	# Hard restrictions: Mages never strike with weapons; Archers fire bows;
	# Summoners may command pets but cannot attack directly.
	if gs.class_id == "mage":
		_begin_cast("magic_basic", 4.0)
		return
	if gs.class_id == "archer":
		_begin_cast("arrow_basic", 0.0)
		return
	if gs.class_id == "summoner":
		if SpiritPet.count_for(self) <= 0:
			Fx.toast("Invoque um familiar (K)", Color(.61, .95, .89))
			return
		_begin_cast("pet_command", 0.0)
		return
	if not HeroClasses.allows_melee(gs.class_id):
		return
	if state == St.ATTACK:
		buffered_attack = true
		return
	if state != St.FREE:
		return
	special_strike = false
	_start_attack(1)


func _start_attack(n: int) -> void:
	combo = n
	state = St.ATTACK
	state_t = 0.0
	anim.speed = gs.attack_speed()
	var target := Enemy.nearest(pos(), 2.6 * T)
	if lock_ok():
		face(Util.facing_from(lock_dir(), facing))
	elif target != null and move_dir.length_squared() < 0.01:
		face(Util.facing_from(target.pos() - pos(), facing))
	anim.play("attack%d" % n, true)
	Sfx.play("swing_heavy" if n == 3 else "swing", 0.55, randf_range(0.95, 1.08))


func _on_anim_hit(a: String) -> void:
	if a.begins_with("attack"):
		if not HeroClasses.allows_melee(gs.class_id):
			return
		var f := aim_dir()
		var c := pos() + Vector2.UP * 0.55 * T + f * (1.0 if combo == 3 else 0.85) * T
		var r := ((1.05 if gs.class_id == "assassin" else 1.55) if combo == 3 else (1.0 if gs.class_id == "assassin" else 1.25)) * T
		Fx.slash(pos() + Vector2.UP * 0.6 * T, facing, combo)
		if gs.class_id == "assassin":
			# Two close-range dagger arcs, never a magical projectile.
			Fx.slash(pos() + Vector2.UP * 0.4 * T + f * .2 * T, facing, 1)
		if combo == 3 and gs.sword_tier >= 2 and (gs.class_id == "paladin"):
			Projectile.crescent(pos() + Vector2.UP * 0.7 * T + f * 0.9 * T, f, gs.total_atk() * 1.1)
		if combo == 3:
			Fx.shockwave(c, 1.2)
			Game.camera.shake(0.22, 0.25)
		var hits := 0
		for e in Enemy.all.duplicate():
			if e.dead:
				continue
			var d: Vector2 = e.pos() + Vector2.UP * 0.4 * T - c
			if d.length() > r + 0.35 * T:
				continue
			var crit := randf() < gs.crit_chance()
			var sneak: bool = gs.class_id == "assassin" and e.hp >= e.max_hp - 0.5
			if sneak:
				crit = true
			var base_mult := 2.55 if special_strike else (1.9 if combo == 3 else (1.15 if combo == 2 else 1.0))
			var dagger_mult := 1.23 if gs.class_id == "assassin" else 1.0
			var dmg := gs.total_atk() * base_mult * dagger_mult * randf_range(0.9, 1.1) * (1.8 if crit else 1.0)
			if sneak:
				dmg *= 1.0 + float(SkillTree.passive_v("assassin", gs.level)[0]) / 100.0
				Fx.toast("Golpe Furtivo!", Color(0.8, 0.75, 1.0), e.pos() + Vector2.UP * 1.6 * T)
			if e.hurt(roundf(dmg), pos(), 9.0 if combo == 3 else 5.0, 30.0 if combo == 3 else 12.0, crit):
				hits += 1
				if gs.lifesteal() > 0.0:
					hp = minf(gs.hp_max(), hp + dmg * gs.lifesteal())
		if hits > 0:
			Game.hit_stop(0.09 if combo == 3 else 0.05)
			Sfx.play("hit", 0.7, randf_range(0.92, 1.06))
			if combo != 3:
				Game.camera.shake(0.08, 0.12)
	elif a == "cast":
		var dir := Util.facing_vec(facing)
		var target := Enemy.nearest(pos(), 10.0 * T, dir, .35)
		if lock_ok():
			target = lock_target
		if target != null:
			dir = ((target.pos() + Vector2.UP * .5 * T) - (pos() + Vector2.UP * .8 * T)).normalized()
		var origin := pos() + Vector2.UP * .8 * T + dir * .5 * T
		match cast_action:
			"arrow_basic":
				if gs.class_id == "archer":
					Projectile.arrow(origin, dir, gs.total_atk() * 1.0 * _arrow_mult())
					Sfx.play("swing", .46, 1.35)
			"arrow_burst":
				if gs.class_id == "archer":
					var mult := _arrow_mult()
					for k in [-1, 0, 1]:
						var angle: float = k * .16
						var spread := dir.rotated(angle)
						Projectile.arrow(origin + spread * 12.0, spread, gs.total_atk() * .80 * mult)
					Sfx.play("swing", .62, 1.25)
			"magic_basic":
				if gs.class_id == "mage":
					Projectile.spark(origin, dir, gs.total_mag() * .74, mini(gs.spark_tier, 3), true)
					Sfx.play("spark", .5, 1.05)
			"skill_r":
				SkillActions.cast(self, "r")
			"skill_f":
				SkillActions.cast(self, "f")
			"magic_burst":
				if gs.class_id == "mage":
					Projectile.spark(origin, dir, gs.total_mag() * (1.55 + .24 * (gs.spark_tier - 1)), mini(gs.spark_tier + 1, 3), true)
					Sfx.play("spark", .72, .80)
			"paladin_heal":
				if gs.class_id == "paladin":
					hp = minf(gs.hp_max(), hp + 16.0 + gs.total_mag() * 1.45)
					Fx.heal(pos())
					Sfx.play("potion", .60, .83)
			"pet_summon":
				if gs.class_id == "summoner":
					SpiritPet.summon(self)
			"pet_command":
				if gs.class_id == "summoner":
					SpiritPet.command(self)

func _on_anim_end(a: String) -> void:
	if state == St.ATTACK and a.begins_with("attack"):
		if buffered_attack and combo < 3:
			buffered_attack = false
			_start_attack(combo + 1)
			return
		buffered_attack = false
		combo = 0
		special_strike = false
		_to_free()
	elif state == St.CAST and a == "cast":
		_to_free()
	elif state == St.ROLL and a == "roll":
		_to_free()


func _begin_cast(action: String, cost: float, cooldown: float = 0.0) -> void:
	if state != St.FREE or (cooldown > 0.0 and special_cd > 0.0):
		return
	if mp < cost:
		Fx.toast("Mana insuficiente", Color(.5, .75, 1.0))
		return
	if action == "pet_summon" and SpiritPet.count_for(self) >= SpiritPet.MAX_ACTIVE:
		Fx.toast("Máximo de 2 familiares", Color(.63, .94, .87))
		return
	mp -= cost
	if cooldown > 0.0:
		special_cd = cooldown * gs.cooldown_mult()
	cast_action = action
	state = St.CAST
	state_t = 0.0
	anim.speed = gs.attack_speed()
	var target := Enemy.nearest(pos(), 9.0 * T)
	if lock_ok():
		face(Util.facing_from(lock_dir(), facing))
	elif target != null and move_dir.length_squared() < .01:
		face(Util.facing_from(target.pos() - pos(), facing))
	elif move_dir.length_squared() > .01:
		face(Util.facing_from(move_dir, facing))
	anim.play("cast", true)
	if action in ["magic_basic", "magic_burst", "paladin_heal", "pet_summon", "skill_r", "skill_f"]:
		Fx.magic_circle(pos(), gs.spark_tier if gs.class_id == "mage" else 1)
		Sfx.play("charge", .38, 1.0)


func _try_cast() -> void:
	if state != St.FREE:
		return
	match gs.class_id:
		"warrior":
			if special_cd > 0.0:
				return
			special_cd = 2.7 * gs.cooldown_mult()
			special_strike = true
			_start_attack(3)  # strong physical weapon hit; absolutely no magic
		"mage":
			_begin_cast("magic_burst", 17.0, 1.7)
		"archer":
			_begin_cast("arrow_burst", 0.0, 2.2)
		"paladin":
			_begin_cast("paladin_heal", 19.0, 5.5)
		"assassin":
			if special_cd > 0.0:
				return
			special_cd = 2.3 * gs.cooldown_mult()
			special_strike = true
			_start_attack(3)  # dual-dagger finisher, no mana and no spell
		"summoner":
			_begin_cast("pet_summon", 22.0, 1.6)


## R / F: class active skills, unlocked in the skill tree (P).
func _try_skill(which: String) -> void:
	if state != St.FREE or dead:
		return
	if not gs.has_unlock(which):
		Fx.toast("Habilidade bloqueada — aprenda na árvore (P)", Color(1, 0.8, 0.5))
		return
	var a: Dictionary = SkillTree.ACTIVES[gs.class_id][which]
	if float(skill_cd[which]) > 0.0:
		Fx.toast("%s recarregando %.0fs" % [a["name"], float(skill_cd[which])], Color(1, 0.7, 0.4))
		return
	if mp < float(a["mp"]):
		Fx.toast("Mana insuficiente", Color(.5, .75, 1.0))
		return
	var cd := float(a["cd"]) * gs.cooldown_mult()
	skill_cd[which] = cd
	skill_cd_max[which] = cd
	_begin_cast("skill_" + which, float(a["mp"]))


func _try_roll() -> void:
	if state == St.ROLL or state == St.DEAD:
		return
	if state == St.ATTACK and anim.normalized() < 0.5:
		return
	roll_dir = move_dir.normalized() if move_dir.length_squared() > 0.01 else Util.facing_vec(facing)
	face(Util.facing_from(roll_dir, facing))
	anim.speed = 1.0
	state = St.ROLL
	state_t = 0.0
	invuln = 0.36
	combo = 0
	buffered_attack = false
	anim.play("roll", true)
	Fx.dust(pos(), 1.0)
	Sfx.play("roll", 0.4, 1.0)


func _use_potion() -> void:
	if hp >= gs.hp_max():
		return
	if not gs.take("potion"):
		Fx.toast("Sem poções", Color(1, 0.5, 0.5))
		return
	hp = minf(gs.hp_max(), hp + maxf(float(Data.items["potion"]["heal"]), 0.35 * gs.hp_max()) * gs.heal_mult())
	Fx.heal(pos())
	Sfx.play("potion", 0.5, 1.0)


func hurt(dmg: float, from: Vector2, knockback: float, poise_dmg: float, crit: bool = false) -> bool:
	if state == St.ROLL and invuln > 0.0:
		Fx.toast("Esquiva!", Color(0.7, 0.95, 1.0))
		return false
	if randf() < gs.dodge_chance():
		Fx.toast("Esquiva!", Color(0.7, 0.95, 1.0))
		return false
	dmg *= float(HeroClasses.info(gs.class_id)["damage_taken"]) * gs.damage_taken_mult()
	dmg = maxf(1.0, roundf(dmg * 100.0 / (100.0 + gs.total_def() * 3.0)))
	var ok := super.hurt(dmg, from, knockback, poise_dmg, crit)
	if not ok:
		return false
	invuln = 0.6
	Sfx.play("hurt", 0.6, 1.0)
	Game.camera.shake(0.18, 0.2)
	if Game.hud:
		Game.hud.hurt_pulse()
	if not dead:
		state = St.HURT
		state_t = 0.0
		combo = 0
		buffered_attack = false
		anim.play("hurt", true)
	return true


func _die() -> void:
	dead = true
	state = St.DEAD
	velocity = Vector2.ZERO
	anim.play("death", true)
	Sfx.play("death", 0.7, 0.9)
	Game.on_player_died()


func revive(at: Vector2) -> void:
	dead = false
	hex_slow = 0.0
	venom = 0.0
	sonic = 0.0
	global_position = at
	hp = gs.hp_max()
	mp = gs.max_mp
	_to_free()
