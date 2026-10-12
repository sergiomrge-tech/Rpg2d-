class_name Insect
extends RefCounted
## Insectoid (Lote 2) combat archetypes: each species has its own range, tell, skill window and effect.
## Called from Enemy for every demon whose def has a non-empty "behavior".

const T := 64.0

const CAST_COOLDOWN := {
	"scarab_shockwave": 6.2, "termite_burrow": 5.1, "cicada_sonic": 6.0, "vespa_sting": 4.0, "ant_carapace": 7.2,
	"roach_plague": 6.3, "spike_roll": 5.2, "dragonfly_zigzag": 4.4, "mantis_dash": 4.2,
}
const TELL := {
	"scarab_shockwave": 0.72, "termite_burrow": 0.78, "cicada_sonic": 0.72, "moth_hex": 0.65, "vespa_sting": 0.35,
	"spike_roll": 0.57, "roach_plague": 0.55, "ant_carapace": 0.48, "dragonfly_zigzag": 0.37,
}
const BURST := {
	"scarab_shockwave": 3.5, "termite_burrow": 4.0, "vespa_sting": 8.0, "dragonfly_zigzag": 8.7, "roach_plague": 6.3, "mantis_dash": 9.0,
}
const MELEE_RADIUS := {
	"scarab_shockwave": 1.55, "spike_roll": 1.38, "ant_carapace": 1.35, "termite_burrow": 1.3, "vespa_sting": 1.25, "mantis_dash": 1.35,
}
## [radius, shadow-radius] collision per species
const BODY_RADIUS := {
	"scarab_shockwave": 0.56, "termite_burrow": 0.46, "ant_carapace": 0.43, "spike_roll": 0.48, "roach_plague": 0.42, "cicada_sonic": 0.38,
}


static func is_boss(e: Enemy) -> bool:
	return e.def["boss"]


static func dir_of(e: Enemy, v: Vector2) -> Vector2:
	return v.normalized() if v.length_squared() > 0.001 else Util.facing_vec(e.facing)


static func _can_cast(e: Enemy, b: String, d: float) -> bool:
	var t := d / T
	match b:
		"mantis_dash": return t > 1.9 and t < 5.3
		"scarab_shockwave": return t < 3.2
		"moth_hex": return t > 2.2 and t < 9.0
		"termite_burrow": return t > 1.5 and t < 5.1
		"vespa_sting": return t > 2.1 and t < 6.4
		"cicada_sonic": return t < 3.8
		"ant_carapace": return t < 2.7 and e.chitin_guard <= 0.0
		"roach_plague": return t > 1.2 and t < 5.4
		"spike_roll": return t > 1.8 and t < 5.5
		"dragonfly_zigzag": return t > 2.8 and t < 8.4
	return false


## Decision + movement while the demon chases the hero.
static func chase(e: Enemy, to_p: Vector2, dist: float) -> void:
	var b: String = e.def["behavior"]
	var dir := dir_of(e, to_p)
	if is_boss(e):
		var far := dist > 3.0 * T
		if e.secondary_cd <= 0.0 and dist < 9.0 * T:
			e.next_is_cast = true
			e.next_is_skill2 = true
			e.skill_dir = dir
			e._go(Enemy.St.TELEGRAPH)
			return
		if e.cast_cd <= 0.0 and dist < 8.3 * T:
			e.next_is_cast = true
			e.next_is_skill2 = false
			e.skill_dir = dir
			e._go(Enemy.St.TELEGRAPH)
			return
		if dist < 2.5 * T and e.attack_cd <= 0.0:
			e.next_is_cast = false
			e.next_is_skill2 = false
			e._go(Enemy.St.TELEGRAPH)
			return
		var ranged := b == "boss_moth" or b == "boss_vespara"
		var arc := Vector2(-dir.y, dir.x) * sin(Game.time() * 1.1 + e._seed)
		var steer := -dir if (ranged and dist < 4.2 * T) else (arc if (ranged and not far) else dir)
		e._move(steer, e.speed * (0.25 if (dist < 2.5 * T and not ranged) else 1.0))
		e._separate()
		return
	if e.cast_cd <= 0.0 and (_can_cast(e, b, dist) or (e.def["caster"] and b != "moth_hex" and dist > 2.6 * T and dist < 7.5 * T)):
		e.next_is_cast = true
		e.skill_dir = dir
		e._go(Enemy.St.TELEGRAPH)
		return
	if dist < (1.85 if b == "scarab_shockwave" else 1.55) * T and e.attack_cd <= 0.0:
		e.next_is_cast = false
		e._go(Enemy.St.TELEGRAPH)
		return
	var want := dir
	var side := Vector2(-want.y, want.x) * sin(Game.time() * 1.3 + e._seed) * 0.45
	if b == "moth_hex" or b == "cicada_sonic" or b == "roach_plague" or b == "dragonfly_zigzag":
		var too_near := (2.0 if b == "cicada_sonic" else (2.1 if b == "roach_plague" else (3.3 if b == "dragonfly_zigzag" else 4.0))) * T
		var too_far := (3.2 if b == "cicada_sonic" else (4.1 if b == "roach_plague" else (7.1 if b == "dragonfly_zigzag" else 6.5))) * T
		var kite := -want if dist < too_near else (want if dist > too_far else side.normalized())
		e._move(kite, e.speed)
	else:
		var stop := (1.7 if b == "scarab_shockwave" else (1.0 if b == "termite_burrow" else (1.45 if b == "spike_roll" else 1.3))) * T
		var sp := 0.0 if dist < stop else e.speed
		e._move((want + side * (0.8 if b == "mantis_dash" else 0.45)).normalized(), sp)
	e._separate()


static func tell_time(e: Enemy) -> float:
	var b: String = e.def["behavior"]
	if is_boss(e):
		return 0.90 if e.next_is_skill2 else (0.68 if e.next_is_cast else 0.48)
	if e.next_is_cast:
		return TELL.get(b, 0.46)
	return 0.52 if b == "scarab_shockwave" else 0.42


## Telegraph finished: enter the right attack state.
static func begin(e: Enemy) -> void:
	var b: String = e.def["behavior"]
	if is_boss(e) and e.next_is_skill2:
		e._go(Enemy.St.CAST2)
		e.anim.play("skill_2", true)
		e.secondary_cd = 10.2 if b == "boss_brood" else 8.5
	elif e.next_is_cast:
		e._go(Enemy.St.CAST)
		e.anim.play("cast", true)
		e.cast_cd = 4.2 if is_boss(e) else float(CAST_COOLDOWN.get(b, randf_range(3.6, 5.4)))
	else:
		e._go(Enemy.St.ATTACK)
		e.anim.play("attack", true)
		e.attack_cd = randf_range(1.0, 1.6)


static func attack_velocity(e: Enemy, n: float) -> Vector2:
	var b: String = e.def["behavior"]
	var burst := float(BURST.get(b, 5.0))
	return Util.facing_vec(e.facing) * burst * T if (n > 0.3 and n < 0.6) else Vector2.ZERO


## Movement during CAST (skill 1) animation.
static func cast_velocity(e: Enemy, n: float) -> Vector2:
	var b: String = e.def["behavior"]
	var d := e.skill_dir
	if is_boss(e):
		return d * 6.8 * T if (b == "boss_reaper" and n > 0.20 and n < 0.64) else Vector2.ZERO
	match b:
		"mantis_dash":
			return d * 10.5 * T if (n > 0.18 and n < 0.65) else Vector2.ZERO
		"termite_burrow", "vespa_sting":
			var v := 12.5 if b == "vespa_sting" else 6.0
			var st := 0.20 if b == "vespa_sting" else 0.29
			return d * v * T if (n > st and n < 0.70) else Vector2.ZERO
		"spike_roll", "dragonfly_zigzag":
			if n > 0.22 and n < 0.70:
				var v := (12.2 if b == "spike_roll" else 7.5) * T
				var cross := Vector2(-d.y, d.x)
				return d * v + (cross * sin(Game.time() * 27.0) * 4.0 * T if b == "dragonfly_zigzag" else Vector2.ZERO)
	return Vector2.ZERO


static func skill2_velocity(e: Enemy, n: float) -> Vector2:
	var b: String = e.def["behavior"]
	if is_boss(e) and (b == "boss_reaper" or b == "boss_vespara"):
		return e.skill_dir * (10.6 if b == "boss_vespara" else 8.3) * T if (n > 0.20 and n < 0.68) else Vector2.ZERO
	return Vector2.ZERO


## Animation hit frame. Returns true when handled here.
static func on_hit(e: Enemy, a: String, p: Player) -> bool:
	var b: String = e.def["behavior"]
	if is_boss(e):
		if e.hit_done:
			return true
		if a == "attack" and e.state == Enemy.St.ATTACK:
			e.hit_done = true
			Fx.claw(e.pos() + Util.facing_vec(e.facing) * 1.1 * T + Vector2.UP * 0.7 * T, e.facing)
			if (p.pos() - (e.pos() + Util.facing_vec(e.facing) * 1.0 * T)).length() < 2.0 * T:
				p.hurt(e.dmg, e.pos(), 8.0, 24.0)
			Sfx.play("swing_heavy", 0.55, 0.83)
		elif a == "cast" and e.state == Enemy.St.CAST:
			e.hit_done = true
			boss_skill(e, 1, e.skill_dir)
		elif a == "skill_2" and e.state == Enemy.St.CAST2:
			e.hit_done = true
			boss_skill(e, 2, e.skill_dir)
		return true
	if a == "attack" and not e.hit_done:
		e.hit_done = true
		var c := e.pos() + Util.facing_vec(e.facing) * (1.05 if b == "mantis_dash" else 0.7) * T
		Fx.claw(c + Vector2.UP * 0.6 * T, e.facing)
		var radius := float(MELEE_RADIUS.get(b, 1.05)) * T
		if (p.pos() - c).length() < radius:
			p.hurt(roundf(e.dmg * randf_range(0.9, 1.1)), e.pos(), 7.0, 20.0)
		Sfx.play("claw", 0.5, randf_range(1.0, 1.15))
		return true
	if a == "cast" and not e.hit_done:
		e.hit_done = true
		_cast_hit(e, b, p)
		return true
	return false


static func _cast_hit(e: Enemy, b: String, p: Player) -> void:
	var pos := e.pos()
	var d := dir_of(e, e.skill_dir)
	var dmg := e.dmg
	match b:
		"mantis_dash":
			var center := pos + d * 0.7 * T
			Fx.claw(center + Vector2.UP * 0.65 * T, e.facing)
			Fx.slash(center + Vector2.UP * 0.3 * T, e.facing, 3)
			if (p.pos() - center).length() < 1.65 * T:
				p.hurt(roundf(dmg * 1.45), pos, 8.0, 25.0)
			Sfx.play("swing_heavy", 0.65, 1.1)
		"scarab_shockwave":
			Fx.shockwave(pos + Vector2.UP * 0.18 * T, 2.35)
			Game.camera.shake(0.16, 0.18)
			if (p.pos() - pos).length() <= 2.35 * T:
				p.hurt(roundf(dmg * 1.15), pos, 10.0, 30.0)
			Sfx.play("boom", 0.55, 0.85)
		"termite_burrow":
			Fx.dust(pos, 1.9)
			Fx.shockwave(pos, 1.35)
			if (p.pos() - pos).length() < 1.55 * T:
				p.hurt(roundf(dmg * 1.2), pos, 7.0, 25.0)
			Sfx.play("boom", 0.48, 0.75)
		"vespa_sting":
			var center := pos + d * 0.6 * T
			Fx.claw(center + Vector2.UP * 0.5 * T, e.facing)
			for i in 6:
				var em := Fx.ember(center + Vector2.from_angle(randf() * TAU) * randf() * 0.28 * T, Color(0.55, 0.95, 0.4))
				if em:
					em.vel = Vector2.from_angle(randf() * TAU) * 1.6 * T
			if (p.pos() - center).length() < 1.6 * T and p.hurt(roundf(dmg * 1.05), pos, 6.0, 20.0):
				p.apply_venom(3.2)
			Sfx.play("claw", 0.62, 1.4)
		"cicada_sonic":
			Fx.shockwave(pos + Vector2.UP * 0.45 * T, 2.8)
			for i in 9:
				var dd := Vector2.from_angle(i * TAU / 9.0)
				var em := Fx.ember(pos + Vector2.UP * 0.55 * T + dd * 0.9 * T, Color(0.36, 0.86, 0.95))
				if em:
					em.vel = dd * 2.9 * T
			if (p.pos() - pos).length() < 2.8 * T and p.hurt(roundf(dmg * 0.65), pos, 4.0, 18.0):
				p.apply_sonic(0.65)
			Sfx.play("boom", 0.45, 1.55)
		"ant_carapace":
			e.chitin_guard = 3.1
			Fx.magic_circle(pos, 1)
			Fx.shockwave(pos, 1.5)
			if (p.pos() - pos).length() < 1.5 * T:
				p.hurt(roundf(dmg * 0.85), pos, 8.0, 18.0)
			Sfx.play("claw", 0.54, 0.70)
		"roach_plague":
			var center := pos + d * 1.25 * T
			if not Game.world.bounds.has_point(center):
				center = pos
			InsectHazard.spawn_poison(center, 2.25, 3.6, 3.4)
			Fx.demon_poof(center)
			Sfx.play("fireball", 0.44, 0.68)
		"spike_roll":
			Fx.shockwave(pos + Vector2.UP * 0.23 * T, 1.75)
			Fx.claw(pos + Vector2.UP * 0.4 * T, e.facing)
			if (p.pos() - pos).length() < 1.72 * T:
				p.hurt(roundf(dmg * 1.30), pos, 8.0, 22.0)
			Sfx.play("boom", 0.47, 1.16)
		"dragonfly_zigzag":
			var start := pos + Vector2.UP * 0.6 * T
			var aim := (p.pos() + Vector2.UP * 0.5 * T - start).normalized()
			for k in range(-1, 2):
				var dir := aim.rotated(k * 0.13)
				Projectile.insect_needle(start + dir * 0.35 * T, dir, dmg * 0.70)
			Sfx.play("spark", 0.56, 1.5)
		"moth_hex":
			var from := pos + Vector2.UP * 0.9 * T
			var aim := (p.pos() + p.velocity * 0.25 + Vector2.UP * 0.5 * T - from).normalized()
			Fx.magic_circle(pos, 2)
			Projectile.hex_spore(from + aim * 0.4 * T, aim, dmg * 0.7)
			Sfx.play("fireball", 0.5, randf_range(0.95, 1.1))


## The five optional bosses: two mechanically different skills each (slot 1 = cast, slot 2 = skill_2).
static func boss_skill(e: Enemy, slot: int, forward: Vector2) -> void:
	var p := Player.I
	if e.dead or p == null or p.dead:
		return
	var pos := e.pos()
	var d := dir_of(e, forward)
	var dmg := e.dmg
	match e.def["id"]:
		"mantis_high_reaper":
			if slot == 1:
				Fx.slash(pos + Vector2.UP * 0.65 * T, e.facing, 3)
				Fx.claw(pos + d * 1.0 * T + Vector2.UP * 0.7 * T, e.facing)
				var toward := p.pos() - pos
				var dot := d.dot(toward.normalized()) if toward.length_squared() > 1.0 else 1.0
				if toward.length() < 3.1 * T and dot > 0.30:
					p.hurt(dmg * 1.40, pos, 9.0, 30.0)
			else:
				Fx.shockwave(pos, 2.15)
				Fx.slash(pos + d * 1.3 * T + Vector2.UP * 0.5 * T, e.facing, 3)
				if (p.pos() - pos).length() < 2.45 * T:
					if p.hurt(dmg * 1.75, pos, 11.0, 35.0):
						p.apply_sonic(0.36)
				Game.camera.shake(0.28, 0.24)
		"scarab_colossus":
			if slot == 1:
				Fx.shockwave(pos, 3.2)
				for i in 10:
					Fx.dust(pos + Vector2.from_angle(i * TAU / 10.0) * 2.0 * T, 1.0)
				if (p.pos() - pos).length() < 3.2 * T:
					p.hurt(dmg * 1.15, pos, 9.0, 35.0)
				Game.camera.shake(0.3, 0.30)
			else:
				e.boss_guard = maxf(e.boss_guard, 3.8)
				Fx.magic_circle(pos, 2)
				for i in 8:
					var s := Vector2.from_angle(i * TAU / 8.0)
					Projectile.insect_needle(pos + s * 1.0 * T + Vector2.UP * 0.55 * T, s, dmg * 0.42)
				Fx.shockwave(pos, 1.6)
		"moth_oracle":
			if slot == 1:
				Fx.magic_circle(pos, 3)
				var from := pos + Vector2.UP * 0.95 * T
				for i in range(-1, 2):
					var aim := d.rotated(i * 0.18)
					Projectile.hex_spore(from + aim * 0.5 * T, aim, dmg * 0.65)
			else:
				Fx.magic_circle(pos, 3)
				Fx.shockwave(pos, 3.65)
				if (p.pos() - pos).length() < 3.65 * T:
					if p.hurt(dmg * 1.0, pos, 5.0, 15.0):
						p.apply_hex_slow(2.8)
						p.apply_sonic(0.45)
				Game.camera.shake(0.11, 0.20)
		"queen_vespara":
			if slot == 1:
				for i in range(-1, 2):
					var aim := d.rotated(i * 0.17)
					Projectile.venom_dart(pos + Vector2.UP * 0.85 * T + aim * 0.5 * T, aim, dmg * 0.56)
				for i in 5:
					var em := Fx.ember(pos + Vector2.UP * 0.8 * T + Vector2.from_angle(randf() * TAU) * randf() * 0.35 * T, Color(0.54, 0.93, 0.42))
					if em:
						em.vel = Vector2.from_angle(randf() * TAU) * 2.0 * T
			else:
				Fx.claw(pos + Vector2.UP * 0.8 * T, e.facing)
				Fx.shockwave(pos, 1.8)
				if (p.pos() - pos).length() < 2.1 * T:
					if p.hurt(dmg * 1.5, pos, 8.0, 25.0):
						p.apply_venom(3.8)
				InsectHazard.spawn_poison(pos, 1.6, 2.4, 2.3)
		"brood_tyrant":
			if slot == 1:
				Fx.magic_circle(pos, 1)
				var living := 0
				for o in Enemy.all:
					if not o.dead and o.def["id"] == "ant_guard" and (o.global_position - pos).length() < 11.0 * T:
						living += 1
				for i in mini(2, maxi(0, 4 - living)):
					var where := pos + Vector2(-1.7 if i == 0 else 1.7, 1.15) * T
					if not Game.world.bounds.has_point(where):
						where = pos
					Enemy.spawn("ant_guard", where, maxi(1, e.level - 1))
					Fx.demon_poof(where)
			else:
				Fx.shockwave(pos, 3.6)
				if (p.pos() - pos).length() < 3.4 * T:
					if p.hurt(dmg * 1.2, pos, 10.0, 35.0):
						p.apply_venom(2.1)
				for i in 4:
					var at := pos + Vector2.from_angle(i * PI / 2.0 + 0.28) * 2.0 * T
					if Game.world.bounds.has_point(at):
						InsectHazard.spawn_poison(at, 1.4, 2.8, 2.0)
				Game.camera.shake(0.36, 0.32)
	Sfx.play("boom" if slot == 2 else "swing_heavy", 0.54, 0.92 if slot == 2 else 1.07)
