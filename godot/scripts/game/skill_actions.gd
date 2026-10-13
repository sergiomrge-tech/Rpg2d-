class_name SkillActions
extends RefCounted
## Effects of the class active skills equipped on R / F / G / V. Skills are data (SkillTree.TREES): this interprets their kind and parameters.

const T := 64.0


static func _base(gs: GameState, stat: String) -> float:
	match stat:
		"mag": return gs.total_mag()
		"mix": return gs.total_atk() + gs.total_mag()
	return gs.total_atk()


static func cast(p: Player, which: String) -> void:
	var gs := p.gs
	var sk := gs.slot_skill(which)
	if sk.is_empty():
		return
	var col: Color = sk["c"]
	var prm: Dictionary = sk["p"]
	var crit := gs.crit_chance()
	var at := p.pos()
	var tier := mini(gs.spark_tier, 3)
	match str(sk["k"]):
		"nova":
			var centre := at
			if prm.get("at", "") == "t":
				centre = AreaSpell.pick_center(p, float(prm.get("rng", 3.0)))
			var dmg := _base(gs, str(prm["s"])) * float(prm["m"])
			AreaSpell.nova(centre, float(prm["r"]) * T, dmg, crit, float(prm.get("kb", 8.0)), 55.0, col)
			if prm.get("twice", false):
				p.get_tree().create_timer(0.25).timeout.connect(func():
					if is_instance_valid(p) and not p.dead:
						AreaSpell.nova(p.pos() if prm.get("at", "") != "t" else centre, float(prm["r"]) * T, dmg, crit, float(prm.get("kb", 8.0)), 55.0, col))
			if prm.get("at", "") != "t":
				Fx.shockwave(at, float(prm["r"]) * 0.45)
			Sfx.play("boom", 0.35, 1.4)
			_burst(centre, col, 26, 60.0 + float(prm["r"]) * 70.0)
		"meteor":
			var centre2 := AreaSpell.pick_center(p, 9.0)
			AreaSpell.meteor_rain(centre2, gs.total_mag() * (1.0 + 0.2 * (tier - 1)) * float(prm["m"]), crit)
			if prm.has("extra"):
				var ex: Dictionary = prm["extra"]
				p.get_tree().create_timer(2.4).timeout.connect(func():
					AreaSpell.nova(centre2, float(ex["r"]) * T, gs.total_mag() * float(ex["m"]), crit, float(ex["kb"]), 70.0, col))
		"storm":
			AreaSpell.lightning_storm(AreaSpell.pick_center(p, 9.0), gs.total_mag() * (1.0 + 0.2 * (tier - 1)) * float(prm["m"]), crit)
		"volley":
			var origin := at + Vector2.UP * 0.8 * T
			var n := int(prm["n"])
			var arc := deg_to_rad(float(prm["arc"]))
			var aim := p.aim_dir()
			var waves := int(prm.get("waves", 1))
			var dmg_v := gs.total_atk() * float(prm["m"])
			for w in waves:
				var fire := func():
					if not is_instance_valid(p) or p.dead:
						return
					for k in n:
						var dir: Vector2
						if arc >= TAU - 0.01:
							dir = Vector2.from_angle(TAU * k / float(n) + (0.13 if w > 0 else 0.0))
						elif n == 1:
							dir = aim
						else:
							dir = aim.rotated(lerpf(-arc * 0.5, arc * 0.5, k / float(n - 1)))
						Projectile.arrow(origin + dir * 14.0, dir, dmg_v)
					Sfx.play("swing", 0.6, 1.4)
					_burst(origin + aim * 24.0, col, 10, 200.0)
				if w == 0:
					fire.call()
				else:
					p.get_tree().create_timer(0.35 * w).timeout.connect(fire)
		"dash":
			var dir2 := p.aim_dir() if float(prm["dist"]) > 0.0 else -p.aim_dir()
			p.move_and_collide(dir2 * absf(float(prm["dist"])) * T)
			for k in 5:       # afterimage trail between start and landing
				_burst(at.lerp(p.pos(), k / 4.0), col, 6, 90.0)
			p.invuln = maxf(p.invuln, 0.4)
			Fx.dust(at, 1.2)
			if float(prm["m"]) > 0.0:
				AreaSpell.nova(p.pos(), float(prm["r"]) * T, _base(gs, str(prm["s"])) * float(prm["m"]), crit, 10.0, 55.0, col)
			Sfx.play("roll", 0.5, 1.2)
		"summon":
			for i in int(prm["n"]):
				SpiritPet.summon(p)
	if prm.has("summon") and str(sk["k"]) != "summon":
		SpiritPet.summon(p)
	if prm.has("heal"):
		p.hp = minf(gs.hp_max(), p.hp + gs.hp_max() * float(prm["heal"]) * gs.heal_mult())
		Fx.heal(at)
		_burst(at, Color(0.6, 1.0, 0.7), 16, 120.0, true)
		_icon_pop(p, sk)
	if prm.has("shield"):
		p.invuln = maxf(p.invuln, float(prm["shield"]))
		_aura(p, col, float(prm["shield"]))
		_burst(at, col, 20, 160.0)
		_icon_pop(p, sk)
	if prm.has("buff"):
		var bf: Dictionary = prm["buff"]
		gs.add_buff(str(bf["id"]), float(bf["t"]), bf["eff"], str(sk["n"]))
		_aura(p, col, float(bf["t"]))
		_icon_pop(p, sk)
		if str(sk["k"]) == "none":
			Fx.shockwave(at, 1.1)
			Sfx.play("boom", 0.3, 1.5)
	Fx.toast(str(sk["n"]) + "!", col, at + Vector2.UP * 2.2 * T)


## One-shot particle burst (sparks in the skill colour).
static func _burst(at: Vector2, col: Color, n: int, speed: float = 220.0, up: bool = false) -> void:
	if Game.world == null:
		return
	var pr := CPUParticles2D.new()
	pr.texture = Util.soft_circle()
	pr.one_shot = true
	pr.amount = n
	pr.lifetime = 0.7
	pr.explosiveness = 0.95
	pr.direction = Vector2.UP if up else Vector2.ZERO
	pr.spread = 40.0 if up else 180.0
	pr.initial_velocity_min = speed * 0.5
	pr.initial_velocity_max = speed
	pr.gravity = Vector2(0, -30 if up else 60)
	pr.scale_amount_min = 0.04
	pr.scale_amount_max = 0.1
	pr.color = col
	pr.z_index = 90
	pr.material = Util.additive()
	Game.world.fx_layer.add_child(pr)
	pr.global_position = at
	pr.emitting = true
	pr.get_tree().create_timer(1.2).timeout.connect(pr.queue_free)


## The skill icon pops above the hero and drifts up (buffs, heals, shields).
static func _icon_pop(p: Player, sk: Dictionary) -> void:
	var ic := Sprite2D.new()
	ic.texture = Sheets.icon(str(sk["i"]))
	ic.modulate = sk["c"]
	ic.scale = Vector2(0.5, 0.5)
	ic.z_index = 95
	ic.position = Vector2(0, -150)
	p.add_child(ic)
	var tw := ic.create_tween().set_parallel(true)
	tw.tween_property(ic, "position:y", -230.0, 0.9)
	tw.tween_property(ic, "modulate:a", 0.0, 0.9).set_delay(0.3)
	tw.chain().tween_callback(ic.queue_free)


## Glow that follows the hero while a buff / shield lasts.
static func _aura(p: Player, col: Color, secs: float) -> void:
	var g := Util.glow(p, col, 2.4, 0.38)
	var tw := g.create_tween()
	tw.tween_property(g, "modulate:a", 0.0, secs).set_delay(maxf(0.0, secs - 1.0)).from(0.38)
	tw.tween_callback(g.queue_free)
