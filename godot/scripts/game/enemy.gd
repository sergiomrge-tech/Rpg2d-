class_name Enemy
extends Actor
## Demon AI: wander -> aggro -> telegraphed melee lunge / ranged fireball, staggers when poise breaks.

static var all: Array[Enemy] = []
const MINIONS := {
	"dryad_profane": "spirit_corrupt", "grakk": "imp", "assassin_shadow": "imp_scout", "scorpion_demon": "sand_imp",
	"ember_golem": "mine_imp", "succubus_mirael": "bog_wraith", "ice_demon": "frost_imp",
}
enum St { IDLE, CHASE, TELEGRAPH, ATTACK, CAST, HURT, DEAD }

var def: Dictionary
var level := 1
var dmg := 0.0
var speed := 0.0
var last_hurt := -99.0

var home := Vector2.ZERO
var state: int = St.IDLE
var state_t := 0.0
var think := 0.0
var cast_cd := 0.0
var attack_cd := 0.0
var wander := Vector2.ZERO
var hit_done := false
var next_is_cast := false
var summoned := false
var tp_cd := 3.0
var phase := 1
var _seed := 0.0


static func spawn(kind: String, at: Vector2, lv: int) -> Enemy:
	var d: Dictionary = Data.demons[kind]
	var e := Enemy.new()
	e.name = "%s Nv%d" % [d["name"], lv]
	e.def = d
	e.level = lv
	var s := Data.hp_scale(lv)
	var sd := Data.dmg_scale(lv)
	e.collision_layer = 4
	e.collision_mask = 1 | 2 | 8
	e.build(d["sheet"], 0.9, 0.3, 0.3, float(d["scale"]) + 0.05 * (lv - 1))
	e.max_hp = roundf(float(d["hp"]) * s)
	e.hp = e.max_hp
	e.dmg = float(d["dmg"]) * sd
	e.speed = float(d["speed"]) * T
	e.max_poise = float(d["poise"]) * sqrt(s)
	e.poise = e.max_poise
	e.home = at
	e.cast_cd = randf_range(1.5, 3.0)
	e._seed = randf() * 100.0
	e.anim.hit.connect(e._on_anim_hit)
	e.anim.ended.connect(e._on_anim_end)
	Game.world.add_entity(e, at)
	e.anim.play("idle")
	e.anim.speed = randf_range(0.92, 1.08)
	all.append(e)
	return e


func _exit_tree() -> void:
	all.erase(self)


static func nearest(p: Vector2, max_dist: float, dir: Vector2 = Vector2.ZERO, min_dot: float = -2.0) -> Enemy:
	var best: Enemy = null
	var bd := max_dist
	for e in all:
		if e.dead:
			continue
		var d := e.global_position - p
		var m := d.length()
		if m > bd:
			continue
		if dir != Vector2.ZERO and m > 0.01 and (d / m).dot(dir) < min_dot:
			continue
		bd = m
		best = e
	return best


func _go(s: int) -> void:
	state = s
	state_t = 0.0


func _physics_process(dt: float) -> void:
	if dead:
		return
	state_t += dt
	cast_cd -= dt
	attack_cd -= dt
	var p := Player.I
	var to_p := (p.pos() - pos()) if p else Vector2.ZERO
	var dist := to_p.length()
	var player_ok := p != null and not p.dead

	match state:
		St.IDLE:
			think -= dt
			if think <= 0.0:
				think = randf_range(1.2, 2.8)
				wander = Vector2.from_angle(randf() * TAU) * 0.9 if randf() < 0.55 else Vector2.ZERO
				if (pos() - home).length() > 3.0 * T:
					wander = (home - pos()).normalized() * 0.9
			_move(wander, speed * 0.4)
			if player_ok and dist < float(def["aggro"]) * T:
				_go(St.CHASE)
				Fx.alert(self)
				if def["boss"]:
					Game.hud.banner(def["name"], def["title"])
					Game.camera.shake(0.25, 0.4)
				Sfx.play("imp_cry", 0.35, randf_range(1.0, 1.2))
		St.CHASE:
			if not player_ok or dist > float(def["aggro"]) * T * 1.8:
				_go(St.IDLE)
			else:
				face(Util.facing_from(to_p, facing))
				tp_cd -= dt
				if (def["id"] == "assassin_shadow" or (def["id"] == "malgrath" and phase >= 2)) and tp_cd <= 0.0 and dist > 1.8 * T:
					# shadow step: vanish and reappear behind the hero, then strike after a short tell
					tp_cd = randf_range(3.6, 5.0)
					Fx.demon_poof(pos() + Vector2.UP * 0.7 * T)
					var behind := p.pos() - Util.facing_vec(p.facing) * 1.3 * T
					global_position = behind
					Fx.demon_poof(behind + Vector2.UP * 0.7 * T)
					Sfx.play("roll", 0.4, 0.7)
					next_is_cast = false
					attack_cd = 0.0
					_go(St.TELEGRAPH)
				elif def["caster"] and cast_cd <= 0.0 and dist > 2.6 * T and dist < 7.5 * T:
					next_is_cast = true
					_go(St.TELEGRAPH)
				elif dist < 1.55 * T and attack_cd <= 0.0:
					next_is_cast = false
					_go(St.TELEGRAPH)
				else:
					var want := to_p.normalized()
					var side := Vector2(-want.y, want.x) * sin(Game.time() * 1.3 + _seed) * 0.45
					var sp := 0.0 if dist < 1.3 * T else speed
					_move((want + side).normalized(), sp)
					_separate()
		St.TELEGRAPH:
			velocity = knock
			face(Util.facing_from(to_p, facing))
			# coloured pulse warns the player; the window is the time to roll
			var pulse := pingpong(state_t * 8.0, 1.0)
			flash(Color(1, 0.6, 0.2) if next_is_cast else Color(1, 0.15, 0.15), 0.55 * pulse)
			if state_t > (0.35 if next_is_cast else 0.42):
				hit_done = false
				if next_is_cast:
					_go(St.CAST)
					anim.play("cast", true)
					cast_cd = randf_range(3.2, 4.6)
				else:
					_go(St.ATTACK)
					anim.play("attack", true)
					attack_cd = randf_range(1.0, 1.6)
		St.ATTACK:
			var n := anim.normalized()
			var f := Util.facing_vec(facing)
			velocity = (f * 7.5 * T if (n > 0.3 and n < 0.6) else Vector2.ZERO) + knock
		St.CAST:
			velocity = knock
		St.HURT:
			velocity = knock
			if state_t > 0.38:
				_go(St.CHASE)
				anim.play("move")
	move_and_slide()
	knock = knock.move_toward(Vector2.ZERO, 26.0 * T * dt)


func _move(dir: Vector2, sp: float) -> void:
	if dir.length_squared() > 0.01 and sp > 0.01:
		face(Util.facing_from(dir, facing))
		anim.play("move")
	else:
		anim.play("idle")
	velocity = dir * sp + knock


func _separate() -> void:
	for o in all:
		if o == self or o.dead:
			continue
		var d := global_position - o.global_position
		var m := d.length()
		if m < 0.9 * T and m > 0.001:
			velocity += d / m * (0.9 * T - m) * 4.0


func _on_anim_hit(a: String) -> void:
	var p := Player.I
	if p == null or p.dead:
		return
	if a == "attack" and not hit_done:
		hit_done = true
		var c := pos() + Util.facing_vec(facing) * 0.7 * T
		Fx.claw(c + Vector2.UP * 0.6 * T, facing)
		if (p.pos() - c).length() < 1.05 * T:
			p.hurt(roundf(dmg * randf_range(0.9, 1.1)), pos(), 7.0, 20.0)
		Sfx.play("claw", 0.5, randf_range(1.0, 1.15))
	elif a == "cast":
		var from := pos() + Vector2.UP * 0.9 * T
		var aim := (p.pos() + p.velocity * 0.25 + Vector2.UP * 0.5 * T - from).normalized()
		if def["boss"]:
			var fan := 3
			if def["id"] == "malgrath":
				fan = 3 if phase == 1 else (5 if phase == 2 else 7)
			var half := fan / 2
			for k in range(-half, half + 1):
				var a2 := aim.rotated(deg_to_rad(k * (12.0 if fan > 5 else 18.0)))
				Projectile.fireball(from + a2 * 0.5 * T, a2, dmg * 0.7)
			if def["id"] == "malgrath" and phase == 3 and randf() < 0.45:   # fire ring
				for k in 12:
					var a3 := Vector2.RIGHT.rotated(deg_to_rad(k * 30.0 + 15.0))
					Projectile.fireball(from + a3 * 0.7 * T, a3, dmg * 0.55)
		elif def["caster"]:
			Projectile.fireball(from + aim * 0.4 * T, aim, dmg * 0.8)
		Sfx.play("fireball", 0.5, randf_range(0.95, 1.1))


func _on_anim_end(a: String) -> void:
	if a == "attack" or a == "cast":
		_go(St.CHASE)
		anim.play("move")
	elif a == "death":
		get_tree().create_timer(0.1).timeout.connect(queue_free)


func hurt(d: float, from: Vector2, knockback: float, poise_dmg: float, crit: bool = false) -> bool:
	if not super.hurt(d, from, knockback, poise_dmg, crit):
		return false
	last_hurt = Game.time()
	if def["boss"] and not summoned and hp < max_hp * 0.5 and hp > 0.0:
		summoned = true
		var minion = MINIONS.get(def["id"], null)
		if minion != null:
			Game.hud.banner(def["name"] + " se enfurece", "Reforços demoníacos!")
			Game.camera.shake(0.3, 0.5)
			for k in 3:
				Enemy.spawn(minion, pos() + Vector2.RIGHT.rotated(deg_to_rad(k * 120.0)) * 2.2 * T, maxi(1, level - 2))
			speed *= 1.25
	if def["id"] == "malgrath" and not dead:
		_update_malgrath_phase()
	Sfx.play("imp_hurt", 0.4, randf_range(1.0, 1.25))
	if dead:
		return true
	if state == St.IDLE:
		_go(St.CHASE)
	if poise <= 0.0:
		# poise break: stagger + interrupts telegraph
		poise = max_poise
		_go(St.HURT)
		anim.play("hurt", true)
		Fx.toast("Quebra!", Color(1, 0.9, 0.5), pos() + Vector2.UP * 2.1 * T)
	return true


## Final boss: 3 phases (66 % / 33 %). P2 = shadow steps + reinforcements, P3 = enrage with 7-way fans and fire rings.
func _update_malgrath_phase() -> void:
	var want := 3 if hp < max_hp * 0.33 else (2 if hp < max_hp * 0.66 else 1)
	if want <= phase:
		return
	phase = want
	Game.camera.shake(0.4, 0.6)
	flash(Color(0.7, 0.3, 1.0) if phase == 2 else Color(1, 0.2, 0.2), 1.0)
	Fx.shockwave(pos(), 3.0)
	Fx.demon_poof(pos() + Vector2.UP * T)
	Sfx.play("boom", 0.7, 0.6)
	if phase == 2:
		Game.hud.banner("Malgrath — Fase II", "As sombras obedecem ao Rei")
		var kinds := ["demon_knight", "ash_wraith", "demon_knight", "ash_wraith"]
		for k in kinds.size():
			Enemy.spawn(kinds[k], pos() + Vector2.RIGHT.rotated(deg_to_rad(k * 90.0 + 45.0)) * 3.2 * T, maxi(1, level - 3))
		speed *= 1.15
		tp_cd = 2.0
	else:
		Game.hud.banner("Malgrath — Fase III", "A fúria do Rei Demônio")
		speed *= 1.2
		dmg *= 1.15
		cast_cd = 0.5
	poise = max_poise


func _die() -> void:
	dead = true
	_go(St.DEAD)
	velocity = Vector2.ZERO
	collision_layer = 0
	collision_mask = 0
	anim.play("death", true)
	start_dissolve()
	Sfx.play("imp_die", 0.5, randf_range(0.95, 1.1))
	Fx.demon_poof(pos() + Vector2.UP * 0.7 * T)
	Loot.drop(def, level, pos())
	Game.on_enemy_killed(self)
