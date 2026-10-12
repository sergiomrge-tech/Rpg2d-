class_name Projectile
extends Node2D
## Projectile (player spells / enemy shots) with simple wall + target collision.

var world: World
var vel := Vector2.ZERO
var team := "enemy"
var dmg := 10.0
var kind := "orb"
var elem := "phys"
var life := 3.0
var radius := 5.0
var pierce := 0
var hit_set: Array = []
var opts: Dictionary = {}
var t := 0.0
var trail_t := 0.0
var color := Color.WHITE
var tier := 1
var spr: Sprite2D
var base_scale := 1.0

func setup(w: World, pos: Vector2, v: Vector2, p_team: String, p_dmg: float, p_kind: String, p_elem: String, p_opts := {}) -> void:
	world = w
	position = pos
	vel = v
	team = p_team
	dmg = p_dmg
	kind = p_kind
	elem = p_elem
	opts = p_opts
	life = float(opts.get("life", 3.0))
	pierce = int(opts.get("pierce", 0))
	radius = float(opts.get("r", 5.0))
	tier = int(opts.get("tier", 1))
	color = Data.ELEM_COLORS.get(elem, Color.WHITE)
	z_index = 22
	spr = Sprite2D.new()
	spr.texture = Fx.glow_tex()
	spr.material = Fx.add_mat()
	base_scale = (radius * 3.4) / 64.0
	spr.scale = Vector2.ONE * base_scale
	spr.modulate = color
	add_child(spr)

func _process(dt: float) -> void:
	t += dt
	life -= dt
	var d := vel * dt
	position += d
	var o := Vector2(0, -16)
	trail_t -= dt
	if trail_t <= 0.0:
		trail_t = 0.03 if kind in ["fire", "ice", "wave"] else 0.06
		var cols: Array = [color, Color.WHITE]
		Fx.burst(world, global_position + o * 0.0, cols, 1 + tier, 18.0, 0.35, 2.0 + tier)
	spr.scale = Vector2.ONE * base_scale * (1.0 + 0.12 * sin(t * 30.0))
	queue_redraw()
	if world.is_solid_at(global_position + Vector2(0, 6)) and kind != "wave":
		_impact()
		return
	if team == "enemy":
		var p := world.player
		if p and not p.dead and (p.hit_center() - global_position).length() < radius + 8.0:
			var h := {"dmg": dmg, "src": global_position - vel * 0.1, "kb": 110.0, "elem": elem}
			if kind == "spore":
				h["status"] = "slow"
				h["status_t"] = 2.5
			if p.take_hit(h) > 0.0 or p.iframes > 0.0:
				_impact()
				return
	else:
		for e in world.enemies:
			if e.dead or hit_set.has(e):
				continue
			if (e.hit_center() - global_position).length() < radius + e.radius * 0.8:
				hit_set.append(e)
				if opts.has("explode"):
					_impact()
					return
				var h: Dictionary = world.player.make_hit(dmg, elem)
				h["kb"] = float(opts.get("kb", 60.0))
				h["src"] = global_position - vel
				h["poise"] = 1.2
				for k in ["slow", "burn", "freeze", "stun"]:
					if opts.has(k):
						h[k] = opts[k]
				e.take_hit(h)
				if hit_set.size() > pierce:
					_impact()
					return
	if life <= 0.0:
		_impact()

func _impact() -> void:
	if opts.has("explode"):
		world.explosion(global_position, float(opts["explode"]), dmg, elem, opts, team == "player")
	else:
		Fx.burst(world, global_position, [color, Color.WHITE], 6, 60.0, 0.25, 2.5)
	queue_free()

func _draw() -> void:
	var o := Vector2.ZERO
	match kind:
		"arrow":
			var dir := vel.normalized()
			draw_line(o - dir * 9.0, o + dir * 5.0, Color("c8b890"), 2.0)
			draw_colored_polygon(PackedVector2Array([o + dir * 8.0, o + dir * 3.0 + dir.orthogonal() * 2.5, o + dir * 3.0 - dir.orthogonal() * 2.5]), Color("e8e8f8"))
			draw_line(o - dir * 9.0, o - dir * 11.0 + dir.orthogonal() * 2.5, Color("d9485a"), 1.5)
		"wave":
			var a := vel.angle()
			var pts := PackedVector2Array()
			for i in 11:
				var u := -0.9 + 1.8 * i / 10.0
				pts.append(Vector2.from_angle(a + u) * (10.0 + tier * 4.0) - Vector2.from_angle(a) * 8.0)
			draw_polyline(pts, Color(color, 0.9), 3.0 + tier, true)
			draw_polyline(pts, Color(1, 1, 1, 0.95), 1.4, true)
		"ice", "lance":
			var dir2 := vel.normalized()
			var n := dir2.orthogonal()
			var L := 12.0 + tier * 5.0
			draw_colored_polygon(PackedVector2Array([o + dir2 * L, o + n * 3.5, o - dir2 * 6.0, o - n * 3.5]), Color("9ae8ff"))
			draw_colored_polygon(PackedVector2Array([o + dir2 * L, o + n * 1.5, o - dir2 * 3.0, o - n * 1.5]), Color.WHITE)
		"fire":
			draw_circle(o, 5.0 + tier * 1.5, Color("ff6a1a"))
			draw_circle(o, 3.5 + tier, Color("ffb02a"))
			draw_circle(o, 1.8 + tier * 0.5, Color("fff2b0"))
		"slime":
			draw_circle(o, 5.0, Color("5ed26a"))
			draw_circle(o + Vector2(-1.5, -1.5), 2.0, Color("d8ffe0"))
		"spore":
			draw_circle(o, 5.0, Color("c8e86a"))
			draw_circle(o + Vector2(-1.5, -1.5), 2.0, Color("f8ffd0"))
		"shard":
			draw_colored_polygon(PackedVector2Array([o + Vector2(0, -6), o + Vector2(4, 0), o + Vector2(0, 6), o + Vector2(-4, 0)]), Color("8af0ff"))
			draw_colored_polygon(PackedVector2Array([o + Vector2(0, -4), o + Vector2(2, 0), o + Vector2(0, 2), o + Vector2(-2, 0)]), Color.WHITE)
		_:
			draw_circle(o, 4.0, color)
			draw_circle(o, 2.0, Color.WHITE)
