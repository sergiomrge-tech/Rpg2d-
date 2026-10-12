"""Effect animations (sheet Sprites/Fx/fx). Pivot = frame centre. Most are drawn for additive blending."""
from __future__ import annotations
import math
import random
import cairo
from core import hx, radial_glow, ellipse, smooth_poly, keys, ease_out, ease_in, Pal, paint, flat, stroke
from sheet import build

FW = FH = 192
C = 96
TAU = math.tau


def rgba(c, a):
    return (c[0], c[1], c[2], a)


def arc_band(ctx, r, a0, a1, w0, w1, col, alpha, steps=40):
    """Crescent band from angle a0..a1 (deg), width tapering w0 -> w1."""
    pts_o, pts_i = [], []
    for i in range(steps + 1):
        u = i / steps
        a = math.radians(a0 + (a1 - a0) * u)
        w = w0 + (w1 - w0) * u
        # crescent: widest in the middle
        w *= math.sin(u * math.pi) ** 0.6
        pts_o.append((math.cos(a) * (r + w / 2), math.sin(a) * (r + w / 2)))
        pts_i.append((math.cos(a) * (r - w / 2), math.sin(a) * (r - w / 2)))
    ctx.save()
    ctx.new_path()
    ctx.move_to(*pts_o[0])
    for p in pts_o[1:]:
        ctx.line_to(*p)
    for p in reversed(pts_i):
        ctx.line_to(*p)
    ctx.close_path()
    ctx.set_source_rgba(*rgba(col, alpha))
    ctx.fill()
    ctx.restore()


def slash(ctx, t, heavy=False):
    # sweep from top (-80) to bottom (+80) in front (to the right)
    r = 64 if not heavy else 74
    head = keys(t, [(0, -95), (0.45, 85), (1, 95)], ease=ease_out)
    tail = keys(t, [(0, -100), (0.3, -95), (1, 90)], ease=ease_in)
    fade = keys(t, [(0, 1), (0.5, 1), (1, 0)])
    ctx.translate(18, 0)
    outer = hx('#7fd6ff') if not heavy else hx('#ffb340')
    mid = hx('#c8f0ff') if not heavy else hx('#ffe08a')
    if head - tail > 2:
        arc_band(ctx, r, tail, head, 30 if heavy else 22, 34 if heavy else 26, outer, 0.45 * fade)
        arc_band(ctx, r + 2, tail + (head - tail) * 0.25, head, 16, 20, mid, 0.85 * fade)
        arc_band(ctx, r + 4, tail + (head - tail) * 0.55, head, 6, 8, hx('#ffffff'), 1.0 * fade)
        # speed lines
        rnd = random.Random(int(t * 100))
        for i in range(6 if heavy else 4):
            a = math.radians(rnd.uniform(tail, head))
            rr = r + rnd.uniform(-14, 18)
            l = rnd.uniform(10, 22)
            stroke(ctx, lambda c, a=a, rr=rr, l=l: (c.move_to(math.cos(a) * rr, math.sin(a) * rr),
                                                   c.line_to(math.cos(a + l / rr) * rr, math.sin(a + l / rr) * rr)),
                   rgba(mid, 1), 1.6, 0.8 * fade)
    if heavy and t > 0.35:
        for i in range(8):
            rnd = random.Random(i * 13)
            a = math.radians(rnd.uniform(-60, 60))
            d = r * 0.6 + (t - 0.35) * rnd.uniform(60, 110)
            radial_glow(ctx, math.cos(a) * d, math.sin(a) * d, 7, hx('#ffd27a'), 0.9 * fade)


def claw(ctx, t):
    fade = keys(t, [(0, 0.2), (0.2, 1), (0.6, 1), (1, 0)])
    grow = keys(t, [(0, 0.2), (0.35, 1), (1, 1)], ease=ease_out)
    for i, off in enumerate((-16, 0, 16)):
        ctx.save()
        ctx.translate(22, off)
        ctx.rotate(math.radians(-35))
        l = 70 * grow

        def mark(c):
            c.move_to(-l / 2, 0)
            c.curve_to(-l / 4, -5, l / 4, -5, l / 2, 0)
            c.curve_to(l / 4, -1.5, -l / 4, -1.5, -l / 2, 0)
            c.close_path()
        flat(ctx, mark, hx('#5a0a14'), 0.9 * fade)
        ctx.scale(0.9, 0.55)
        flat(ctx, mark, hx('#ff4a4a'), 0.95 * fade)
        ctx.restore()


def burst(ctx, t, col, core, rays=10, size=1.0, ring=False, seed=1):
    rnd = random.Random(seed)
    k = ease_out(t)
    fade = 1 - t
    radial_glow(ctx, 0, 0, 60 * size * (0.5 + k), col, 0.55 * fade)
    for i in range(rays):
        a = i / rays * TAU + rnd.uniform(-0.2, 0.2)
        l0 = 10 * size + 50 * size * k
        l1 = l0 + 26 * size * (1 - t) * rnd.uniform(0.6, 1.2)
        w = 5 * size * (1 - t)
        ctx.save()
        ctx.rotate(a)
        flat(ctx, lambda c: smooth_poly(c, [(l0, 0), ((l0 + l1) / 2, -w), (l1, 0), ((l0 + l1) / 2, w)], tension=0.1),
             rgba(core, 1), fade)
        ctx.restore()
    flat(ctx, lambda c: ellipse(c, 0, 0, 22 * size * (1 - k * 0.7), 22 * size * (1 - k * 0.7)), rgba(core, 1), fade)
    if ring:
        stroke(ctx, lambda c: c.arc(0, 0, 20 * size + 60 * size * k, 0, TAU), rgba(col, 1), 5 * (1 - t), fade)


def electric(ctx, t, size=1.0, seed=3):
    rnd = random.Random(seed + int(t * 50))
    k = ease_out(t)
    fade = 1 - t
    radial_glow(ctx, 0, 0, 70 * size, hx('#5ac8ff'), 0.6 * fade)
    for i in range(7):
        a = rnd.uniform(0, TAU)
        r = 70 * size * (0.4 + k * 0.6)
        pts = [(0, 0)]
        for s in range(1, 6):
            u = s / 5
            pts.append((math.cos(a) * r * u + rnd.uniform(-8, 8), math.sin(a) * r * u + rnd.uniform(-8, 8)))
        stroke(ctx, lambda c, pts=pts: (c.move_to(*pts[0]), [c.line_to(*p) for p in pts[1:]]), hx('#9fe6ff'), 4 * fade + 0.5, 0.8)
        stroke(ctx, lambda c, pts=pts: (c.move_to(*pts[0]), [c.line_to(*p) for p in pts[1:]]), hx('#ffffff'), 1.6, fade)
    flat(ctx, lambda c: ellipse(c, 0, 0, 18 * (1 - k), 18 * (1 - k)), hx('#ffffff'), fade)


def explosion(ctx, t, seed=5):
    rnd = random.Random(seed)
    k = ease_out(t)
    fade = 1 - t ** 1.5
    radial_glow(ctx, 0, 0, 80, hx('#ff7a1a'), 0.7 * fade)
    for i in range(12):
        a = rnd.uniform(0, TAU)
        d = 50 * k * rnd.uniform(0.4, 1.0)
        r = rnd.uniform(14, 26) * (1 - t * 0.6)
        col = hx('#ffd25a') if i % 3 else hx('#ff5a1a')
        flat(ctx, lambda c, a=a, d=d, r=r: ellipse(c, math.cos(a) * d, math.sin(a) * d, r, r), col, 0.8 * fade)
    flat(ctx, lambda c: ellipse(c, 0, 0, 26 * (1 - k * 0.8), 26 * (1 - k * 0.8)), hx('#fff6d0'), fade)
    for i in range(9):
        a = rnd.uniform(0, TAU)
        d = 20 + 70 * k
        flat(ctx, lambda c, a=a, d=d: ellipse(c, math.cos(a) * d, math.sin(a) * d, 3, 3), hx('#ffe08a'), fade)


def dust(ctx, t):
    rnd = random.Random(2)
    k = ease_out(t)
    fade = (1 - t) * 0.85
    for i in range(6):
        a = rnd.uniform(math.pi * 0.9, math.pi * 2.1)
        d = 8 + 26 * k * rnd.uniform(0.6, 1.0)
        r = (9 + 9 * k) * rnd.uniform(0.7, 1.1)
        x, y = math.cos(a) * d, math.sin(a) * d * 0.5 + 10
        paint(ctx, lambda c, x=x, y=y, r=r: ellipse(c, x, y - k * 6, r, r * 0.85),
              Pal('#e8d8bc', '#c8b090', '#fff4e0', '#a08868'), sh=r * 0.3, hl=0, line=0)
    # alpha by drawing over with clear -> handled by global fade: use paint_with_alpha via group
    return fade


def shock(ctx, t):
    k = ease_out(t)
    fade = 1 - t
    r = 20 + 80 * k
    stroke(ctx, lambda c: c.arc(0, 0, r, 0, TAU), hx('#ffe6a0'), 14 * (1 - t) + 1, 0.5 * fade)
    stroke(ctx, lambda c: c.arc(0, 0, r, 0, TAU), hx('#ffffff'), 4 * (1 - t) + 0.5, fade)
    for i in range(12):
        a = i / 12 * TAU
        stroke(ctx, lambda c, a=a: (c.move_to(math.cos(a) * r * 0.8, math.sin(a) * r * 0.8),
                                    c.line_to(math.cos(a) * (r + 12), math.sin(a) * (r + 12))), hx('#ffd27a'), 3, fade * 0.8)


def magic_circle(ctx, t, col, col2):
    fade = keys(t, [(0, 0), (0.2, 1), (0.7, 1), (1, 0)])
    rot = t * 120
    scale = keys(t, [(0, 0.6), (0.25, 1.0), (1, 1.05)], ease=ease_out)
    ctx.scale(scale, scale)
    radial_glow(ctx, 0, 0, 90, col, 0.35 * fade)
    for r, w in ((82, 3), (70, 1.6), (40, 2)):
        stroke(ctx, lambda c, r=r: c.arc(0, 0, r, 0, TAU), col2, w, 0.95 * fade)
    ctx.save()
    ctx.rotate(math.radians(rot))
    # rune ticks + hexagram
    for i in range(24):
        a = i / 24 * TAU
        l = 7 if i % 3 == 0 else 3.5
        stroke(ctx, lambda c, a=a, l=l: (c.move_to(math.cos(a) * 72, math.sin(a) * 72),
                                         c.line_to(math.cos(a) * (72 + l), math.sin(a) * (72 + l))), col2, 1.6, fade)
    for k in range(2):
        pts = [(math.cos(i / 3 * TAU + k * math.pi / 3 - math.pi / 2) * 66, math.sin(i / 3 * TAU + k * math.pi / 3 - math.pi / 2) * 66)
               for i in range(3)]
        stroke(ctx, lambda c, pts=pts: (c.move_to(*pts[0]), c.line_to(*pts[1]), c.line_to(*pts[2]), c.close_path()),
               col2, 1.8, 0.9 * fade)
    ctx.restore()
    ctx.save()
    ctx.rotate(math.radians(-rot * 1.6))
    for i in range(8):
        a = i / 8 * TAU
        flat(ctx, lambda c, a=a: ellipse(c, math.cos(a) * 40, math.sin(a) * 40, 3.2, 3.2), (1, 1, 1, 1), fade)
    ctx.restore()


def heal(ctx, t):
    rnd = random.Random(4)
    for i in range(12):
        x = rnd.uniform(-40, 40)
        start = rnd.uniform(0, 0.4)
        u = (t - start) / 0.6
        if not 0 <= u <= 1:
            continue
        y = 30 - u * 90
        a = math.sin(u * math.pi)
        if i % 3 == 0:
            s = 6
            flat(ctx, lambda c, x=x, y=y: (c.rectangle(x - s, y - 1.8, 2 * s, 3.6), c.rectangle(x - 1.8, y - s, 3.6, 2 * s)),
                 hx('#b6ff9a'), a)
        else:
            radial_glow(ctx, x, y, 9, hx('#7dff8a'), 0.9 * a)
            flat(ctx, lambda c, x=x, y=y: ellipse(c, x, y, 2, 2), hx('#ffffff'), a)
    radial_glow(ctx, 0, 20, 70, hx('#6aff7a'), 0.3 * math.sin(t * math.pi))


def poof(ctx, t):
    rnd = random.Random(8)
    k = ease_out(t)
    fade = 1 - t ** 1.3
    for i in range(10):
        a = rnd.uniform(0, TAU)
        d = 6 + 44 * k * rnd.uniform(0.5, 1.0)
        r = (14 + 16 * k) * rnd.uniform(0.6, 1.1)
        x, y = math.cos(a) * d, math.sin(a) * d * 0.8 - k * 18
        pal = Pal('#5a2a6a', '#3a1648', '#8a4aa0', '#1a0822') if i % 2 else Pal('#3a2a44', '#241830', '#5a4a66', '#100818')
        paint(ctx, lambda c, x=x, y=y, r=r: ellipse(c, x, y, r, r), pal, sh=r * 0.35, hl=r * 0.15, line=0)
    for i in range(8):
        a = rnd.uniform(0, TAU)
        d = 20 + 60 * k
        radial_glow(ctx, math.cos(a) * d, math.sin(a) * d - 20 * k, 6, hx('#ff6ad0'), fade)
    return fade


def alert(ctx, t):
    pop = keys(t, [(0, 0.3), (0.2, 1.25), (0.35, 1.0), (1, 1.0)], ease=ease_out)
    fade = keys(t, [(0, 1), (0.8, 1), (1, 0)])
    ctx.scale(pop, pop)
    pal = Pal('#ff4a3a', '#c42a2a', '#ff9a80', '#3a0808')

    def mark(c):
        c.move_to(-7, -34)
        c.line_to(7, -34)
        c.line_to(4, 0)
        c.line_to(-4, 0)
        c.close_path()
        c.new_sub_path()
        c.arc(0, 10, 6, 0, TAU)
    paint(ctx, mark, pal, sh=2, hl=1.5, line=2.2)
    return fade


def projectile(ctx, t, kind):
    ph = t * TAU
    if kind == 'spark1':
        radial_glow(ctx, 0, 0, 34, hx('#4ab8ff'), 0.75)
        for i in range(4):
            rnd = random.Random(int(t * 60) * 7 + i)
            a = rnd.uniform(0, TAU)
            pts = [(0, 0)] + [(math.cos(a) * 9 * s + rnd.uniform(-4, 4), math.sin(a) * 9 * s + rnd.uniform(-4, 4)) for s in (1, 2, 3)]
            stroke(ctx, lambda c, pts=pts: (c.move_to(*pts[0]), [c.line_to(*p) for p in pts[1:]]), hx('#c8f2ff'), 1.6, 0.9)
        # tail
        for i in range(8):
            x = -8 - i * 7
            radial_glow(ctx, x, math.sin(ph + i) * 2, 12 - i, hx('#7fd6ff'), 0.5 * (1 - i / 8))
        flat(ctx, lambda c: ellipse(c, 0, 0, 9 + math.sin(ph * 2), 9 + math.sin(ph * 2)), hx('#ffffff'))
    elif kind in ('spark2', 'fireball'):
        big = kind == 'spark2'
        core, mid, outer = (hx('#fff6c8'), hx('#ffb340'), hx('#ff5a1a'))
        L = 70 if big else 46
        radial_glow(ctx, 0, 0, 40 if big else 30, outer, 0.7)
        # flame tongues trailing behind
        for i in range(7):
            u = i / 6
            w = (12 if big else 10) * (1 - u * 0.8)
            x = -u * L
            y = math.sin(ph * 2 + i * 1.3) * 4 * u
            flat(ctx, lambda c, x=x, y=y, w=w: ellipse(c, x, y, w * 1.4, w), outer, 0.6 * (1 - u * 0.6))
            flat(ctx, lambda c, x=x, y=y, w=w: ellipse(c, x + 3, y, w * 0.9, w * 0.6), mid, 0.8 * (1 - u))
        if big:
            flat(ctx, lambda c: smooth_poly(c, [(26, 0), (-6, -9), (-30, 0), (-6, 9)], tension=0.2), core)
        flat(ctx, lambda c: ellipse(c, 2, 0, 11 if big else 9, 9 if big else 8), core)
    elif kind == 'spark3':
        radial_glow(ctx, 0, 0, 46, hx('#a84aff'), 0.75)
        for i in range(10):
            u = i / 9
            x = -u * 80
            r = 14 * (1 - u * 0.85)
            flat(ctx, lambda c, x=x, r=r, i=i: ellipse(c, x, math.sin(ph + i * 0.9) * 5 * u, r, r), hx('#d08aff'), 0.55 * (1 - u))
        for i in range(5):
            a = ph + i / 5 * TAU
            flat(ctx, lambda c, a=a: ellipse(c, math.cos(a) * 18, math.sin(a) * 9, 3, 3), hx('#ffffff'), 0.9)
        flat(ctx, lambda c: ellipse(c, 0, 0, 13, 13), hx('#fff0ff'))


def arrow(ctx, t):
    radial_glow(ctx, 10, 0, 20, hx('#c8ffe0'), 0.35)
    for i in range(5):
        stroke(ctx, lambda c, i=i: (c.move_to(-14 - i * 7, 0), c.line_to(-20 - i * 7, 0)), hx('#c8ffe0'), 2 - i * 0.3, 0.6 - i * 0.1)
    stroke(ctx, lambda c: (c.move_to(-16, 0), c.line_to(14, 0)), hx('#3a2410'), 3.4)
    stroke(ctx, lambda c: (c.move_to(-16, 0), c.line_to(14, 0)), hx('#c89060'), 1.8)
    flat(ctx, lambda c: smooth_poly(c, [(12, -4), (22, 0), (12, 4)], tension=0), hx('#e8f0ff'))
    for sy in (-1, 1):
        flat(ctx, lambda c, sy=sy: smooth_poly(c, [(-16, 0), (-22, sy * 6), (-12, 0)], tension=0), hx('#3fc87a'))


ANIMS = {
    'arrow': (2, 12, True, arrow),
    # name: (frames, fps, loop, fn, additive_alpha_fn?)
    'slash': (7, 26, False, lambda c, t: slash(c, t)),
    'slash_heavy': (9, 24, False, lambda c, t: slash(c, t, True)),
    'claw': (6, 22, False, claw),
    'hit': (6, 24, False, lambda c, t: burst(c, t, hx('#ffd27a'), hx('#ffffff'), 8, 0.8)),
    'hit_crit': (8, 24, False, lambda c, t: burst(c, t, hx('#ffb340'), hx('#fff6d0'), 12, 1.1, ring=True)),
    'hit_spark': (7, 22, False, lambda c, t: electric(c, t)),
    'hit_fire': (9, 22, False, lambda c, t: explosion(c, t)),
    'dust': (7, 16, False, dust),
    'shock': (8, 22, False, shock),
    'circle1': (12, 20, False, lambda c, t: magic_circle(c, t, hx('#4ab8ff'), hx('#c8f2ff'))),
    'circle2': (12, 20, False, lambda c, t: magic_circle(c, t, hx('#ff7a1a'), hx('#ffe08a'))),
    'circle3': (12, 20, False, lambda c, t: magic_circle(c, t, hx('#a84aff'), hx('#f0c8ff'))),
    'heal': (12, 16, False, heal),
    'poof': (10, 16, False, poof),
    'alert': (10, 14, False, alert),
    'spark1': (6, 20, True, lambda c, t: projectile(c, t, 'spark1')),
    'spark2': (6, 20, True, lambda c, t: projectile(c, t, 'spark2')),
    'spark3': (6, 20, True, lambda c, t: projectile(c, t, 'spark3')),
    'fireball': (6, 18, True, lambda c, t: projectile(c, t, 'fireball')),
}


def draw(ctx, payload):
    name, t = payload
    fn = ANIMS[name][3]
    ctx.push_group()
    r = fn(ctx, t)
    ctx.pop_group_to_source()
    ctx.paint_with_alpha(r if isinstance(r, float) else 1.0)


def build_fx():
    jobs = []
    for name, (n, fps, loop, fn) in ANIMS.items():
        frames = [(name, (i / n) if loop else i / (n - 1)) for i in range(n)]
        jobs.append((name, frames, fps, loop, -1))
    return build('fx', 'Fx', FW, FH, C, C, jobs, draw, outline=0)


if __name__ == '__main__':
    build_fx()
