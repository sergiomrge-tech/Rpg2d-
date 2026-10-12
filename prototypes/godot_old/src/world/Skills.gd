class_name Skills
extends RefCounted
## Skill implementations. begin() starts a cast (returns cast time or -1), release() resolves the effect.

static func def(id: String) -> Dictionary:
	return Data.SKILLS[id]

static func anim_for(id: String) -> String:
	return "attack1" if str(def(id)["tree"]) == "blade" else "cast"

static func elem_color(id: String) -> Color:
	return Data.ELEM_COLORS.get(str(def(id)["elem"]), Color.WHITE)

static func base_damage(p: Player, id: String, rank: int) -> float:
	var d := def(id)
	var stat: float = float(p.stats_cache["atk"]) if str(d["scale"]) == "atk" else float(p.stats_cache["mag"])
	return stat * Data.skill_power(id, rank)

## Called when the cast starts. Return cast duration, or -1 to abort without cost.
static func begin(w: World, p: Player, id: String, rank: int) -> float:
	var d := def(id)
	var col := elem_color(id)
	var tier := Data.skill_tier(rank)
	match str(d["kind"]):
		"multi":
			if _nearest(w, p.global_position, float(d["range"]) + 40.0) == null:
				Game.toast.emit("Nenhum alvo próximo!", "", Color("ffb0b0"))
				return -1.0
		"chain":
			if _nearest(w, p.global_position + p.aim_vector(150.0) * 40.0, float(d["range"])) == null:
				Game.toast.emit("Nenhum alvo!", "", Color("ffb0b0"))
				return -1.0
	var sides := 3 if tier == 1 else (4 if tier == 2 else 6)
	if str(d["tree"]) != "blade":
		Fx.rune(w, p.global_position, col, 38.0 + tier * 10.0, 0.62, sides, 1.0)
		Fx.burst(w, p.global_position + Vector2(0, -12), [col, Color.WHITE], 5 + tier * 3, 50.0, 0.45, 2.5, -30.0)
		Sfx.play("charge", -8.0)
	else:
		Fx.burst(w, p.global_position + Vector2(0, -16), [col, Color.WHITE], 4 + tier * 2, 40.0, 0.3, 2.0)
	return 0.5

static func _nearest(w: World, from: Vector2, range_px: float, exclude: Array = []) -> Enemy:
	var best: Enemy = null
	var bd := range_px
	for e in w.enemies:
		if e.dead or exclude.has(e):
			continue
		var dist := from.distance_to(e.hit_center()) - e.radius * 0.5
		if dist < bd:
			bd = dist
			best = e
	return best

static func _hit(w: World, p: Player, e: Enemy, dmg: float, elem: String, extra := {}) -> void:
	var h := p.make_hit(dmg, elem)
	h["src"] = p.global_position
	for k in extra:
		h[k] = extra[k]
	e.take_hit(h)

# ------------------------------------------------------------------------------------------------
static func release(w: World, p: Player, id: String, rank: int) -> void:
	var d := def(id)
	var col := elem_color(id)
	var elem := str(d["elem"])
	var tier := Data.skill_tier(rank)
	var dmg := base_damage(p, id, rank)
	var aim := p.face_aim
	var o := p.global_position + Vector2(0, -16)
	match str(d["kind"]):
		"wave":
			Sfx.play("swing2", -2.0)
			var n := 1 if tier < 3 else 3
			for i in n:
				var a := aim.rotated((i - (n - 1) / 2.0) * 0.32)
				var pr := Projectile.new()
				pr.setup(w, o + a * 14.0, a * 280.0, "player", dmg * (1.0 if n == 1 else 0.7), "wave", elem, {"pierce": 99, "r": 12 + tier * 4, "life": 0.75, "kb": 110.0, "tier": tier})
				w.entities.add_child(pr)
			Fx.slash(w, o, aim.angle(), 30.0 + tier * 6.0, Color("bfe4ff"), 2.4, false, 0.26, 10.0 + tier * 3.0)
			if tier >= 2:
				Fx.slash(w, o, aim.angle(), 22.0, Color.WHITE, 2.0, true, 0.2, 6.0)
		"whirl":
			var R: float = float(d["range"]) + rank * 3.0
			var pulses := 3 if tier == 1 else (4 if tier == 2 else 6)
			p.iframes = maxf(p.iframes, 0.1 * pulses + 0.1)
			Sfx.play("whirl", -2.0)
			for i in pulses:
				w.later(0.07 * i, func():
					if p.dead: return
					Fx.slash(w, p.global_position + Vector2(0, -16), i * 2.1, R - 6.0, Color("ffe0b0") if tier < 3 else Color("fff2a0"), 5.0, false, 0.22, 9.0)
					Sfx.play("swing", -6.0, 1.0 + i * 0.05)
					for e in w.enemies.duplicate():
						if not e.dead and (e.hit_center() - o).length() < R + e.radius:
							_hit(w, p, e, dmg * (1.1 if i == pulses - 1 else 0.8), elem, {"kb": 130.0, "poise": 1.5})
					Fx.burst(w, p.global_position, [Color("ffe0b0"), Color.WHITE], 6, 90.0, 0.3, 2.0, 0.0))
			Fx.ring(w, p.global_position, R, Color("ffe0b0"), 0.5, 0.1)
			if tier >= 2:
				Fx.ring(w, p.global_position, R * 0.7, Color.WHITE, 0.4)
		"dash":
			var len: float = float(d["range"]) + rank * 6.0
			var hit_list: Array = []
			p.iframes = 0.45
			Sfx.play("dash", -2.0)
			_dash(w, p, aim, len, dmg, elem, tier, hit_list)
		"slam":
			var R2: float = float(d["range"]) + rank * 3.0
			var c := p.global_position + aim * 30.0
			Sfx.play("swing2", -3.0)
			Fx.rune(w, c, Color("ffcf8a"), R2, 0.34, 4, 0.0)
			w.later(0.22, func():
				Sfx.play("slam", 0.0)
				Fx.shake(w, 8.0)
				Fx.ring(w, c, R2, Color("ffcf8a"), 0.5, 0.2)
				Fx.ring(w, c, R2 * 0.6, Color.WHITE, 0.35)
				Fx.burst(w, c, [Color("c9a070"), Color("ffffff"), Color("8a6a3a")], 22 + tier * 8, 130.0, 0.6, 3.0, 220.0, false)
				w.crack_decal(c, R2 * 0.85)
				for e in w.enemies.duplicate():
					if not e.dead and e.global_position.distance_to(c) < R2 + e.radius:
						_hit(w, p, e, dmg, elem, {"kb": 170.0, "stun": 1.0 + tier * 0.3, "heavy": true, "poise": 3.0})
				if tier >= 2:
					w.later(0.2, func():
						Fx.ring(w, c, R2 * 1.3, Color("ffcf8a"), 0.5)
						for e in w.enemies.duplicate():
							if not e.dead and e.global_position.distance_to(c) < R2 * 1.3 + e.radius:
								_hit(w, p, e, dmg * 0.6, elem, {"kb": 120.0}))
			)
		"multi":
			var tgt := _nearest(w, p.global_position, float(d["range"]) + 40.0)
			if tgt == null:
				return
			var n := 6 + (tier - 1) * 2
			p.iframes = 0.12 * n + 0.15
			Sfx.play("dash", -2.0)
			for i in n:
				w.later(0.09 * i, func():
					if tgt == null or tgt.dead or not is_instance_valid(tgt) or p.dead:
						return
					var a := float(i) / n * TAU + 0.7
					var np := tgt.global_position + Vector2(cos(a) * 24.0, sin(a) * 14.0)
					if w.is_solid_at(np):
						np = tgt.global_position + Vector2(0, 12)
					p.global_position = np
					p.face = (tgt.global_position - np).normalized()
					Fx.slash(w, tgt.hit_center(), a + PI, 26.0, Color.WHITE if i < n - 1 else Color("ffd84a"), 2.6, i % 2 == 0, 0.18, 8.0)
					Sfx.play("swing", -6.0, 1.1)
					_hit(w, p, tgt, dmg * (1.9 if i == n - 1 else 1.0), elem, {"kb": 0.0, "stun": 0.2, "heavy": i == n - 1}))
		"bolt":
			Sfx.play("fire", -2.0)
			var pr := Projectile.new()
			pr.setup(w, o + aim * 12.0, aim * (210.0 + tier * 10.0), "player", dmg, "fire", elem, {"r": 5 + tier * 1.5, "life": 1.6, "explode": 34.0 + rank * 5.0, "burn": 3.0 + tier, "kb": 90.0, "tier": tier})
			w.entities.add_child(pr)
			Fx.glow_flash(w, o + aim * 12.0, Color("ff8a2a"), 60.0, 0.2)
			if tier >= 3:
				for s in [-0.3, 0.3]:
					var q := Projectile.new()
					q.setup(w, o + aim * 12.0, aim.rotated(s) * 190.0, "player", dmg * 0.5, "fire", elem, {"r": 4, "life": 1.4, "explode": 26.0, "burn": 2.0, "tier": 1})
					w.entities.add_child(q)
		"lance":
			Sfx.play("ice", -2.0)
			var n2 := 1 if tier < 3 else 3
			for i in n2:
				var a2 := aim.rotated((i - (n2 - 1) / 2.0) * 0.2)
				var pr2 := Projectile.new()
				pr2.setup(w, o + a2 * 12.0, a2 * 340.0, "player", dmg * (1.0 if n2 == 1 else 0.7), "ice", elem, {"r": 6, "life": 1.0, "pierce": 1 + tier, "slow": 2.5 + tier, "kb": 70.0, "tier": tier})
				w.entities.add_child(pr2)
			Fx.glow_flash(w, o + aim * 12.0, Color("8ae0ff"), 50.0, 0.18)
		"chain":
			var first := _nearest(w, p.global_position + aim * 40.0, float(d["range"]))
			if first == null:
				return
			Sfx.play("bolt", -1.0)
			var jumps := 3 + (tier - 1) * 2
			var pts: Array = [o]
			var hit_set: Array = []
			var cur: Enemy = first
			var dm := dmg
			for i in jumps:
				if cur == null:
					break
				hit_set.append(cur)
				pts.append(cur.hit_center())
				var tgt2 := cur
				var dm2 := dm
				w.later(0.07 * i, func():
					if is_instance_valid(tgt2) and not tgt2.dead:
						_hit(w, p, tgt2, dm2, elem, {"kb": 40.0, "stun": 0.3 + tier * 0.15, "poise": 1.0})
						Fx.glow_flash(w, tgt2.hit_center(), Color("ffe84a"), 56.0, 0.25))
				dm *= 0.86
				cur = _nearest(w, cur.hit_center(), 100.0, hit_set)
			Fx.bolt(w, pts, Color("ffe84a"), 0.4)
			Fx.bolt(w, pts, Color("ffffaa"), 0.28)
		"nova":
			var R3: float = float(d["range"]) + rank * 4.0
			Sfx.play("ice", 0.0)
			Fx.ring(w, p.global_position, R3, Color("8ae0ff"), 0.55, 0.15)
			Fx.ring(w, p.global_position, R3 * 0.6, Color.WHITE, 0.4)
			Fx.burst(w, p.global_position + Vector2(0, -10), [Color("8ae0ff"), Color.WHITE, Color("5ac8ff")], 26 + tier * 8, 130.0, 0.6, 3.0)
			Fx.shake(w, 4.0)
			w.later(0.12, func():
				for e in w.enemies.duplicate():
					if not e.dead and e.global_position.distance_to(p.global_position) < R3 + e.radius:
						_hit(w, p, e, dmg, elem, {"freeze": 1.4 + rank * 0.2, "kb": 70.0, "heavy": true, "poise": 2.0})
				if tier >= 2:
					Fx.ring(w, p.global_position, R3 * 1.35, Color("8ae0ff"), 0.5)
					for e in w.enemies.duplicate():
						if not e.dead and e.global_position.distance_to(p.global_position) < R3 * 1.35 + e.radius:
							_hit(w, p, e, dmg * 0.5, elem, {"slow": 3.0})
				if tier >= 3:
					w.ice_spikes(p.global_position, R3))
		"meteor":
			var R4: float = float(d["range"]) + rank * 4.0
			var tg := _nearest(w, p.global_position + aim * 60.0, 170.0)
			var mp: Vector2 = tg.global_position if tg else p.global_position + aim * 80.0
			if w.is_solid_at(mp):
				mp = p.global_position + aim * 40.0
			Sfx.play("meteor", -1.0)
			Fx.rune(w, mp, Color("ff8a2a"), R4, 0.95, 5, -1.0)
			var count := 1 if tier < 3 else 3
			for i in count:
				var tp := mp + (Vector2.ZERO if i == 0 else Vector2.from_angle(i * 2.1) * R4 * 0.9)
				w.later(0.15 * i, func(): w.meteor_strike(tp, R4 if i == 0 else R4 * 0.7, dmg if i == 0 else dmg * 0.6, tier, p))
		"heal":
			var amt := dmg * 3.0 + 14.0 + tier * 8.0
			Sfx.play("heal", 0.0)
			p.heal(amt)
			Fx.ring(w, p.global_position, 34.0 + tier * 6.0, Color("6aff9a"), 0.7, 0.2)
			Fx.burst(w, p.global_position + Vector2(0, -12), [Color("6aff9a"), Color.WHITE, Color("c8ffd8")], 20 + tier * 8, 50.0, 1.0, 3.0, -90.0)
			Fx.glow_flash(w, p.global_position + Vector2(0, -16), Color("9affc0"), 120.0, 0.5)
			if tier >= 3:
				p.apply_status("regen", 6.0, amt * 0.04)
		"shield":
			p.shield = roundf(dmg * 2.2 + 24.0)
			p.shield_t = 9.0 + tier * 2.0
			Sfx.play("shield", 0.0)
			Fx.ring(w, p.global_position, 36.0, Color("9ad8ff"), 0.55, 0.25)
			Fx.glow_flash(w, p.global_position + Vector2(0, -20), Color("9ad8ff"), 100.0, 0.4)
			Game.toast.emit("Escudo: %d" % int(p.shield), "shield", Color("9ad8ff"))
		"buff":
			p.buff_mul = 1.25 + rank * 0.04
			p.buff_t = 12.0 + tier * 2.0
			Sfx.play("buff", 0.0)
			Fx.ring(w, p.global_position, 50.0, Color("ff6a3a"), 0.6, 0.2)
			Fx.burst(w, p.global_position + Vector2(0, -10), [Color("ff6a3a"), Color("ffd84a")], 20, 80.0, 0.8, 3.0, -60.0)
			Game.toast.emit("Fúria! +%d%% de dano" % int((p.buff_mul - 1.0) * 100.0), "rage", Color("ff8a6a"))
		"phase":
			var L: float = float(d["range"]) + rank * 8.0
			var tp2 := p.global_position
			var step := 6.0
			var dist := step
			while dist <= L:
				var np := p.global_position + aim * dist
				if w.is_solid_at(np):
					break
				tp2 = np
				dist += step
			Fx.burst(w, p.global_position + Vector2(0, -16), [Color("c8a8ff"), Color.WHITE], 16, 90.0, 0.5, 3.0)
			p.global_position = tp2
			Fx.burst(w, p.global_position + Vector2(0, -16), [Color("c8a8ff"), Color.WHITE], 16, 90.0, 0.5, 3.0)
			p.iframes = 0.8
			p.invis_t = 0.75
			Sfx.play("spirit", -2.0)
		"summon":
			Sfx.play("spirit", 0.0)
			var n3 := 2 + tier
			var orb := Orbiters.new()
			orb.setup(w, p, n3, dmg, 10.0 + tier * 2.0, tier)
			p.add_child(orb)
			Game.toast.emit("Espíritos Guardiões invocados", "spirit", Color("a0ffd8"))

static func _dash(w: World, p: Player, dir: Vector2, length: float, dmg: float, elem: String, tier: int, hit_list: Array) -> void:
	var steps := 12
	var step_len := length / steps
	for i in steps:
		w.later(0.018 * i, func():
			if p.dead:
				return
			var col := p.move_and_collide(dir * step_len)
			Fx.burst(w, p.global_position + Vector2(0, -14), [Color("bfe4ff"), Color.WHITE], 2, 20.0, 0.3, 4.0)
			if i % 2 == 0:
				p._ghost()
			for e in w.enemies.duplicate():
				if e.dead or hit_list.has(e):
					continue
				if p.global_position.distance_to(e.hit_center() + Vector2(0, e.hit_h)) < 24.0 + e.radius or (p.global_position + Vector2(0, -16)).distance_to(e.hit_center()) < 22.0 + e.radius:
					hit_list.append(e)
					_hit(w, p, e, dmg, elem, {"kb": 140.0, "stun": 0.4, "heavy": true, "poise": 2.0})
					Fx.slash(w, e.hit_center(), dir.angle() + 1.5, 18.0, Color.WHITE, 2.4, false, 0.18, 7.0)
			if col != null and i > 2:
				return
			if tier >= 3 and i % 3 == 0:
				Fx.glow_flash(w, p.global_position + Vector2(0, -14), Color("ffe84a"), 50.0, 0.3))

class Orbiters extends Node2D:
	var w: World
	var p: Player
	var n := 3
	var dmg := 10.0
	var life := 10.0
	var tier := 1
	var t := 0.0
	var tick := 0.0
	func setup(world_: World, player_: Player, count: int, d: float, dur: float, tr: int) -> void:
		w = world_
		p = player_
		n = count
		dmg = d
		life = dur
		tier = tr
		z_index = 30
		material = Fx.add_mat()
	func _process(dt: float) -> void:
		t += dt
		life -= dt
		tick -= dt
		if life <= 0.0 or p.dead:
			queue_free()
			return
		if tick <= 0.0:
			tick = 0.45
			for i in n:
				var pos := _orb_pos(i)
				for e in w.enemies.duplicate():
					if not e.dead and pos.distance_to(e.hit_center()) < 16.0 + e.radius:
						var h := p.make_hit(dmg, "holy")
						h["kb"] = 70.0
						h["poise"] = 0.8
						h["crit"] = false
						e.take_hit(h)
		queue_redraw()
	func _orb_pos(i: int) -> Vector2:
		var a: float = t * 3.4 + float(i) * TAU / float(n)
		return global_position + Vector2(cos(a) * 38.0, sin(a) * 24.0 - 20.0)
	func _draw() -> void:
		for i in n:
			var lp := to_local(_orb_pos(i))
			for k in 5:
				var a2: float = t * 3.4 + float(i) * TAU / float(n) - k * 0.18
				var q := Vector2(cos(a2) * 38.0, sin(a2) * 24.0 - 20.0)
				draw_circle(q, 4.5 - k * 0.7, Color(0.6, 1.0, 0.85, 0.55 - k * 0.1))
			draw_circle(lp, 5.0, Color("a0ffd8"))
			draw_circle(lp, 2.4, Color.WHITE)
