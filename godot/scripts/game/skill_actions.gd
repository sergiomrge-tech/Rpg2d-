class_name SkillActions
extends RefCounted
## Effects of the class active skills (R / F) unlocked in the skill tree.

const T := 64.0


static func cast(p: Player, which: String) -> void:
	var gs := p.gs
	var info: Dictionary = SkillTree.ACTIVES[gs.class_id][which]
	var col: Color = info["color"]
	var crit := gs.crit_chance()
	var at := p.pos()
	var tier := mini(gs.spark_tier, 3)
	match gs.class_id:
		"mage":
			if which == "r":
				AreaSpell.meteor_rain(AreaSpell.pick_center(p, 9.0), gs.total_mag() * (1.0 + 0.2 * (tier - 1)), crit)
			else:
				AreaSpell.lightning_storm(AreaSpell.pick_center(p, 9.0), gs.total_mag() * (1.0 + 0.2 * (tier - 1)), crit)
		"warrior":
			if which == "r":
				gs.add_buff("grito", 10.0, {"atk_pct": 35.0}, "Grito de Guerra")
				_aura(p, col, 10.0)
				Fx.shockwave(at, 1.4)
				Sfx.play("boom", 0.4, 1.3)
			else:
				AreaSpell.nova(at, 3.4 * T, gs.total_atk() * 2.4, crit, 11.0, 70.0, col)
		"paladin":
			if which == "r":
				p.invuln = 3.0
				_aura(p, col, 3.0)
				Fx.heal(at)
			else:
				AreaSpell.nova(at, 3.8 * T, (gs.total_atk() + gs.total_mag()) * 1.5, crit, 8.0, 60.0, col)
				p.hp = minf(gs.hp_max(), p.hp + gs.hp_max() * 0.15)
				Fx.heal(at)
		"archer":
			if which == "r":
				gs.add_buff("foco", 8.0, {"crit": 40.0, "aspd": 30.0}, "Foco Mortal")
				_aura(p, col, 8.0)
			else:
				var origin := at + Vector2.UP * 0.8 * T
				for k in 12:
					var dir := Vector2.from_angle(TAU * k / 12.0)
					Projectile.arrow(origin + dir * 14.0, dir, gs.total_atk() * 0.9)
				Sfx.play("swing", 0.6, 1.4)
		"assassin":
			if which == "r":
				gs.add_buff("veu", 6.0, {"dodge": 50.0, "mspd": 30.0}, "Véu das Sombras")
				_aura(p, col, 6.0)
				Fx.dust(at, 1.5)
			else:
				AreaSpell.nova(at, 2.5 * T, gs.total_atk() * 2.2, crit, 6.0, 50.0, col)
				p.get_tree().create_timer(0.25).timeout.connect(func():
					if is_instance_valid(p) and not p.dead:
						AreaSpell.nova(p.pos(), 2.5 * T, gs.total_atk() * 2.2, crit, 6.0, 50.0, col))
		"summoner":
			if which == "r":
				gs.add_buff("vinculo", 10.0, {"mag_pct": 30.0, "regen": 2.0}, "Vínculo Espiritual")
				p.hp = minf(gs.hp_max(), p.hp + gs.hp_max() * 0.25)
				_aura(p, col, 10.0)
				Fx.heal(at)
			else:
				AreaSpell.nova(at, 3.6 * T, gs.total_mag() * 2.6, crit, 7.0, 55.0, col)
	Fx.toast(str(info["name"]) + "!", col, at + Vector2.UP * 2.2 * T)


## Glow that follows the hero while a buff / shield lasts.
static func _aura(p: Player, col: Color, secs: float) -> void:
	var g := Util.glow(p, col, 2.4, 0.38)
	var tw := g.create_tween()
	tw.tween_property(g, "modulate:a", 0.0, secs).set_delay(maxf(0.0, secs - 1.0)).from(0.38)
	tw.tween_callback(g.queue_free)
