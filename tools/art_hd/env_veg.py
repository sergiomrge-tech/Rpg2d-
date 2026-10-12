"""Extra vegetation props: birch, cherry, willow, hedge, topiary, fern, flower bed, berry bush, tall grass, fallen log,
dry shrub, frost shrub, glow fern. Registered into env_objects.PROPS (imported at the end of env_objects)."""
from __future__ import annotations
import math
import random
from core import Pal, paint, flat, stroke, ellipse, smooth_poly, hx, shade, radial_glow
from env_objects import prop, canopy, blob, BARK, LEAF, LEAF_DK, STONE, WOOD, WOOD_DK

BIRCH_BARK = Pal('#efe9de', '#c9c0b0', '#ffffff', '#5a5040')
BIRCH_LEAF = Pal('#a8d860', '#7fb248', '#d4f08c', '#3a5a22')
CHERRY = Pal('#f6aac8', '#d47ea4', '#ffd8e8', '#6a2a48')
WILLOW = Pal('#7fc060', '#58a048', '#b4e084', '#244a28')
FERN = Pal('#4fae5a', '#3a8a46', '#86d68a', '#164a26')
BERRY = Pal('#4a9a4a', '#33803a', '#7cc060', '#1a4422')
DRY = Pal('#c8a45a', '#a08038', '#e8c880', '#5a4418')
FROST = Pal('#c8dcec', '#98b4cc', '#f0f8ff', '#40566e')
GLOW = Pal('#3ac8b0', '#25a090', '#7af0d8', '#0c4a44')


def poly(pts, t=0.02):
    return lambda c: smooth_poly(c, list(pts), tension=t)


@prop('tree_birch', 170, 250, 85, 236, col=(18, 12, 0), shadow=(5, 0, 52, 15, 0.35))
def tree_birch(ctx):
    paint(ctx, poly([(-7, 0), (-5, -50), (-4, -110), (4, -110), (5, -50), (7, 0), (0, 3)], 0.2), BIRCH_BARK, sh=2, hl=1)
    rnd = random.Random(3)
    for i in range(7):
        y = -12 - i * 14
        x = rnd.uniform(-3, 3)
        stroke(ctx, lambda c, x=x, y=y: (c.move_to(x - 4, y), c.line_to(x + 4, y)), hx('#3a3228'), 2.2)
    canopy(ctx, -26, -140, 34, 40, BIRCH_LEAF, 2, n=8)
    canopy(ctx, 28, -146, 30, 42, BIRCH_LEAF, 5, n=8)
    canopy(ctx, 0, -176, 42, 46, Pal('#b8e070', '#8cbc50', '#e0f89c', '#3e5c24'), 8, n=10)


@prop('tree_cherry', 190, 230, 95, 214, col=(22, 12, 0), shadow=(6, 0, 66, 18, 0.35))
def tree_cherry(ctx):
    def trunk(c):
        smooth_poly(c, [(-12, 0), (-8, -10), (-7, -46), (-20, -66), (-6, -58), (0, -74), (6, -58), (20, -68), (8, -44), (9, -10), (13, 0), (0, 3)], tension=0.4)
    paint(ctx, trunk, Pal('#7a5a4a', '#573c32', '#a07a64', '#2a1812'), sh=3, hl=1.2)
    canopy(ctx, -38, -112, 42, 34, CHERRY, 3, n=9)
    canopy(ctx, 38, -108, 42, 34, CHERRY, 6, n=9)
    canopy(ctx, 0, -138, 62, 50, Pal('#f9b8d2', '#da88ae', '#ffe2ee', '#702c4c'), 9, n=12)
    rnd = random.Random(7)
    for i in range(16):
        a, d = rnd.uniform(0, math.tau), rnd.uniform(0.2, 0.85)
        flat(ctx, lambda c, x=math.cos(a) * 62 * d, y=-138 + math.sin(a) * 48 * d: ellipse(c, x, y, 3, 2.4), hx('#ffffff'), 0.85)


@prop('tree_willow', 220, 250, 110, 232, col=(24, 14, 0), shadow=(6, 0, 78, 20, 0.35))
def tree_willow(ctx):
    paint(ctx, poly([(-12, 0), (-8, -12), (-8, -60), (-16, -86), (0, -76), (16, -88), (8, -58), (9, -12), (13, 0), (0, 3)], 0.4), BARK, sh=3, hl=1.2)
    canopy(ctx, 0, -128, 74, 40, WILLOW, 4, n=12)
    rnd = random.Random(11)
    for i in range(30):                        # hanging strands
        x = -86 + i * 5.8 + rnd.uniform(-2, 2)
        top = -118 + abs(x) * 0.12
        ln = rnd.uniform(46, 92)
        sway = rnd.uniform(-5, 5)
        stroke(ctx, lambda c, x=x, top=top, ln=ln, s=sway: (c.move_to(x, top), c.curve_to(x + s, top + ln * 0.4, x - s, top + ln * 0.8, x + s * 0.4, top + ln)),
               rnd.choice([WILLOW.base, WILLOW.shadow, WILLOW.light]), 2.4, 0.95)


@prop('hedge', 150, 90, 75, 78, col=(130, 16, 0), shadow=(3, 0, 66, 10, 0.3))
def hedge(ctx):
    paint(ctx, poly([(-64, 0), (-66, -30), (-52, -50), (-20, -56), (20, -56), (52, -50), (66, -30), (64, 0)], 0.3), Pal('#4a9a46', '#35803a', '#74c05a', '#183e22'), sh=5, hl=2, deep=8)
    rnd = random.Random(13)
    for i in range(40):
        x, y = rnd.uniform(-58, 58), rnd.uniform(-48, -6)
        stroke(ctx, lambda c, x=x, y=y: (c.move_to(x - 3, y), c.curve_to(x - 1, y + 2.5, x + 1, y + 2.5, x + 3, y)), hx('#2a6a30'), 1.2, 0.7)
    for i in range(10):
        x, y = rnd.uniform(-54, 54), rnd.uniform(-46, -12)
        flat(ctx, lambda c, x=x, y=y: ellipse(c, x, y, 2.4, 2.4), hx(rnd.choice(['#ff8fb0', '#fff2a0', '#ffffff'])))


@prop('topiary', 70, 130, 35, 118, col=(24, 12, 0), shadow=(2, 0, 28, 8, 0.28))
def topiary(ctx):
    paint(ctx, poly([(-18, 0), (-22, -26), (22, -26), (18, 0)], 0.06), Pal('#c07c52', '#9a5a3a', '#e0a070', '#4a2a18'), sh=2.5, hl=1)
    stroke(ctx, lambda c: (c.move_to(0, -26), c.line_to(0, -40)), BARK.base, 4)
    paint(ctx, lambda c: ellipse(c, 0, -62, 26, 24), Pal('#4a9a46', '#35803a', '#74c05a', '#183e22'), sh=4, hl=1.5, deep=6)
    paint(ctx, lambda c: ellipse(c, 0, -96, 16, 16), Pal('#4a9a46', '#35803a', '#74c05a', '#183e22'), sh=3, hl=1.2, deep=4)


@prop('fern', 80, 60, 40, 52, outline=0.8)
def fern(ctx):
    for a in range(-80, 81, 20):
        r = math.radians(a)
        tip = (math.sin(r) * 34, -math.cos(r) * 32 - 4)
        paint(ctx, lambda c, tip=tip, a=a: smooth_poly(c, [(0, 0), (tip[0] * 0.5 - 4, tip[1] * 0.55), tip, (tip[0] * 0.5 + 4, tip[1] * 0.5)], tension=0.25), FERN, sh=1, hl=0.6, line=0.8)


@prop('flower_bed', 120, 60, 60, 46, outline=0)
def flower_bed(ctx):
    flat(ctx, lambda c: ellipse(c, 0, -8, 52, 18), hx('#6a4a32'), 0.9)
    rnd = random.Random(17)
    cols = ['#ff6f91', '#ffd84a', '#ffffff', '#9a7bff', '#ff9a4a', '#ff4a6a']
    for i in range(26):
        x, y = rnd.uniform(-46, 46), rnd.uniform(-20, 2)
        stroke(ctx, lambda c, x=x, y=y: (c.move_to(x, y + 6), c.line_to(x, y)), LEAF_DK.base, 1.4)
        col = hx(rnd.choice(cols))
        for k in range(5):
            a = k / 5 * math.tau
            flat(ctx, lambda c, a=a, x=x, y=y: ellipse(c, x + math.cos(a) * 2.6, y + math.sin(a) * 2.3, 2.2, 2.2), col)
        flat(ctx, lambda c, x=x, y=y: ellipse(c, x, y, 1.4, 1.4), hx('#ffb020'))


@prop('berry_bush', 90, 70, 45, 62, col=(34, 12, 0), shadow=(3, 0, 38, 10, 0.3))
def berry_bush(ctx):
    canopy(ctx, 0, -24, 36, 22, BERRY, 31, n=8)
    rnd = random.Random(19)
    for i in range(12):
        x, y = rnd.uniform(-28, 28), -24 + rnd.uniform(-14, 12)
        col = rnd.choice([Pal('#d6453d', '#a52c33', '#f27a5f', '#5a1418'), Pal('#5a6ad0', '#3a469e', '#8a9af0', '#141a4a')])
        paint(ctx, lambda c, x=x, y=y: ellipse(c, x, y, 3.4, 3.4), col, sh=1, hl=0.6, line=0.7)


@prop('tall_grass', 80, 80, 40, 72, outline=0.8)
def tall_grass(ctx):
    rnd = random.Random(23)
    for i in range(17):
        x = rnd.uniform(-26, 26)
        h = rnd.uniform(30, 62)
        bend = rnd.uniform(-14, 14)
        pal = [LEAF, LEAF_DK, Pal('#8cc85a', '#64a43c', '#bfe888', '#2a5a22')][i % 3]
        paint(ctx, lambda c, x=x, h=h, b=bend: smooth_poly(c, [(x - 3.2, 0), (x + b * 0.6, -h * 0.6), (x + b, -h), (x + b * 0.6 + 3, -h * 0.6), (x + 3.2, 0)], tension=0.2), pal, sh=1, hl=0.6, line=0.8)


@prop('log', 130, 70, 65, 58, col=(100, 16, 0), shadow=(3, 0, 56, 9, 0.3))
def log(ctx):
    paint(ctx, poly([(-52, 0), (-56, -22), (52, -26), (56, -4), (40, 4), (-40, 4)], 0.15), BARK, sh=4, hl=1.5)
    paint(ctx, lambda c: ellipse(c, 54, -14, 8, 12), Pal('#e0b47a', '#c08d58', '#f8d6a0', '#5a3418'), sh=1, hl=0.8)
    stroke(ctx, lambda c: ellipse(c, 54, -14, 4, 6), hx('#b07c4a'), 0.9)
    flat(ctx, lambda c: blob(c, [(-30, -22, 9), (-16, -26, 8), (4, -28, 7)]), hx('#7fbf5a'), 0.9)
    for x, y in ((-6, -30), (8, -32)):
        paint(ctx, lambda c, x=x, y=y: ellipse(c, x, y, 5, 3.4), Pal('#e8dcc8', '#c8b898', '#ffffff', '#5a4a30'), sh=1, hl=0.5, line=0.6)


@prop('dry_shrub', 90, 70, 45, 62, col=(30, 12, 0), shadow=(3, 0, 36, 9, 0.28))
def dry_shrub(ctx):
    rnd = random.Random(29)
    for i in range(26):
        a = rnd.uniform(-1.3, 1.3)
        ln = rnd.uniform(24, 44)
        x1, y1 = math.sin(a) * ln, -math.cos(a) * ln * 0.8 - 6
        stroke(ctx, lambda c, x1=x1, y1=y1: (c.move_to(0, 0), c.curve_to(x1 * 0.3, y1 * 0.6, x1 * 0.8, y1 * 0.7, x1, y1)), rnd.choice([DRY.base, DRY.shadow, DRY.light]), 2.0, 0.95)
    flat(ctx, lambda c: blob(c, [(-10, -22, 8), (6, -28, 9), (16, -20, 7), (-2, -14, 9)]), DRY.base, 0.7)


@prop('frost_shrub', 90, 70, 45, 62, col=(30, 12, 0), shadow=(3, 0, 36, 9, 0.28))
def frost_shrub(ctx):
    rnd = random.Random(37)
    for i in range(18):
        a = rnd.uniform(-1.2, 1.2)
        ln = rnd.uniform(26, 46)
        x1, y1 = math.sin(a) * ln, -math.cos(a) * ln * 0.85 - 4
        stroke(ctx, lambda c, x1=x1, y1=y1: (c.move_to(0, 0), c.curve_to(x1 * 0.2, y1 * 0.6, x1 * 0.7, y1 * 0.7, x1, y1)), FROST.shadow, 2.2)
        flat(ctx, lambda c, x1=x1, y1=y1: blob(c, [(x1, y1 - 2, 4.5)]), hx('#f4fbff'), 0.95)
    flat(ctx, lambda c: blob(c, [(-14, -8, 10), (4, -12, 12), (18, -6, 9)]), hx('#f4fbff'), 0.9)


@prop('glow_fern', 90, 70, 45, 60, outline=0.8)
def glow_fern(ctx):
    radial_glow(ctx, 0, -24, 34, hx('#5affd8'), 0.35)
    for a in range(-80, 81, 20):
        r = math.radians(a)
        tip = (math.sin(r) * 36, -math.cos(r) * 36 - 4)
        paint(ctx, lambda c, tip=tip: smooth_poly(c, [(0, 0), (tip[0] * 0.5 - 4, tip[1] * 0.55), tip, (tip[0] * 0.5 + 4, tip[1] * 0.5)], tension=0.25), GLOW, sh=1, hl=0.6, line=0.8)
