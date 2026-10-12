"""HD cartoon environment props (3/4 top-down). Each prop is drawn around its base point (0,0).

Output: unity/Assets/Resources/Sprites/Env/<name>.png  + Env/props.json (pivot + collider per prop).
"""
from __future__ import annotations
import json
import math
import os
import random
import cairo
import numpy as np
from concurrent.futures import ProcessPoolExecutor
from PIL import Image
from scipy import ndimage
from core import (Frame, Pal, paint, flat, stroke, ellipse, capsule, smooth_poly, hx, shade, mix, outline_rgba,
                  to_image, radial_glow, S)
from sheet import OUT

OUTLINE = hx('#2a1a1c')
PROPS = {}


def prop(name, w, h, px, py, col=None, shadow=None, outline=1.0):
    """Register a prop. (px,py)= base point inside canvas; col=(w,h,offy) collider box in px around base;
    shadow=(cx,cy,rx,ry,alpha) soft ground shadow (relative to base)."""
    def deco(fn):
        PROPS[name] = dict(fn=fn, w=w, h=h, px=px, py=py, col=col, shadow=shadow, outline=outline)
        return fn
    return deco


def blob(c, circles):
    for x, y, r in circles:
        c.new_sub_path()
        c.arc(x, y, r, 0, 2 * math.pi)


# ------------------------------------------------------------------ palettes
LEAF = Pal('#5fae4a', '#3f8a3d', '#93d063', '#1f4a2a')
LEAF_DK = Pal('#3f8a3d', '#2c6a34', '#5fae4a', '#173b22')
PINE = Pal('#2f8a5a', '#216a48', '#55b07a', '#0f3626')
BARK = Pal('#8a5a3c', '#66402b', '#b07a52', '#2e1a10')
STONE = Pal('#a7a6b5', '#7f7d92', '#d3d2de', '#3b3848')
WOOD = Pal('#b37a4c', '#8a5634', '#d9a06a', '#3d2312')
WOOD_DK = Pal('#7f5236', '#5d3a25', '#a06c48', '#2c180c')
PLASTER = Pal('#f3e3c6', '#d8c19e', '#fff6e2', '#6b5038')
ROOF_O = Pal('#e0703f', '#b9502f', '#ff9b62', '#5a2014')
ROOF_B = Pal('#4f78b8', '#3a5b94', '#7aa2dc', '#182a4a')
ROOF_S = Pal('#5c6380', '#454a66', '#838aa8', '#1d2036')
GLASS = Pal('#9fd8f0', '#6fb0d6', '#e2f6ff', '#2a4a66')
METAL = Pal('#e8c35a', '#b98a2c', '#fff0a8', '#5e4313')
CLOTH_R = Pal('#d6453d', '#a52c33', '#f27a5f', '#5a1418')
CLOTH_B = Pal('#3d6fc2', '#2c5196', '#6b9be6', '#142650')


# ------------------------------------------------------------------ trees
def canopy(ctx, cx, cy, rx, ry, pal, seed, n=11, top_light=True):
    rnd = random.Random(seed)
    circles = []
    for i in range(n):
        a = i / n * math.tau
        circles.append((cx + math.cos(a) * rx * 0.72, cy + math.sin(a) * ry * 0.72, (rx + ry) * 0.5 * rnd.uniform(0.36, 0.46)))
    circles.append((cx, cy, (rx + ry) * 0.5 * 0.72))
    paint(ctx, lambda c: blob(c, circles), pal, sh=(rx * 0.16), hl=2.0, line=1.2, deep=rx * 0.30)
    # inner clumps (lighter, toward the light)
    if top_light:
        inner = []
        for i in range(6):
            a = rnd.uniform(math.pi * 0.95, math.pi * 1.75)
            d = rnd.uniform(0.25, 0.55)
            inner.append((cx + math.cos(a) * rx * d, cy + math.sin(a) * ry * d, (rx + ry) * 0.5 * rnd.uniform(0.2, 0.3)))
        flat(ctx, lambda c: blob(c, inner), pal.light, 0.55)
        # leaf ticks
        for i in range(14):
            a = rnd.uniform(0, math.tau)
            d = rnd.uniform(0.2, 0.8)
            x, y = cx + math.cos(a) * rx * d, cy + math.sin(a) * ry * d
            stroke(ctx, lambda c, x=x, y=y: (c.move_to(x - 2.5, y), c.curve_to(x - 1, y + 2, x + 1, y + 2, x + 2.5, y)),
                   pal.shadow, 1.1, 0.7)


@prop('tree_oak', 200, 230, 100, 214, col=(26, 14, 0), shadow=(6, 0, 70, 20, 0.35))
def tree_oak(ctx):
    def trunk(c):
        smooth_poly(c, [(-14, 0), (-9, -10), (-8, -50), (-16, -70), (-4, -62), (0, -78), (5, -62), (17, -72),
                        (9, -48), (10, -10), (16, 0), (4, 3), (-4, 3)], tension=0.4)
    paint(ctx, trunk, BARK, sh=3, hl=1.5)
    for y in (-18, -32):
        stroke(ctx, lambda c, y=y: (c.move_to(-3, y), c.curve_to(-1, y - 4, 1, y - 6, 2, y - 10)), BARK.shadow, 1.2)
    canopy(ctx, -36, -116, 40, 34, LEAF_DK, 3, n=9)
    canopy(ctx, 36, -112, 40, 34, LEAF_DK, 4, n=9)
    canopy(ctx, 0, -138, 62, 52, LEAF, 7, n=12)


@prop('tree_round', 170, 200, 85, 186, col=(22, 12, 0), shadow=(5, 0, 58, 17, 0.35))
def tree_round(ctx):
    def trunk(c):
        smooth_poly(c, [(-11, 0), (-7, -10), (-6, -55), (6, -55), (8, -10), (12, 0), (0, 3)], tension=0.4)
    paint(ctx, trunk, BARK, sh=2.5, hl=1.2)
    canopy(ctx, 0, -112, 58, 52, Pal('#6cbc52', '#4b9a43', '#a2dc6c', '#21502c'), 11, n=11)
    rnd = random.Random(5)
    for i in range(9):   # fruit
        a = rnd.uniform(0, math.tau)
        d = rnd.uniform(0.25, 0.75)
        x, y = math.cos(a) * 52 * d, -112 + math.sin(a) * 46 * d
        paint(ctx, lambda c, x=x, y=y: ellipse(c, x, y, 4.2, 4.2), Pal('#f05a4a', '#c23a3a', '#ff9a80', '#5a1418'),
              sh=1.2, hl=0.8, line=0.8)


@prop('tree_pine', 140, 240, 70, 226, col=(18, 12, 0), shadow=(5, 0, 46, 15, 0.35))
def tree_pine(ctx):
    paint(ctx, lambda c: smooth_poly(c, [(-8, 0), (-6, -40), (6, -40), (8, 0), (0, 3)], tension=0.3), BARK, sh=2, hl=1)
    for i, (y, w) in enumerate([(-40, 58), (-80, 48), (-118, 38), (-152, 27), (-180, 15)]):
        def tier(c, y=y, w=w):
            pts = [(-w, y)]
            n = 5
            for k in range(1, n):
                pts.append((-w + 2 * w * k / n - w / n, y + 8))
                pts.append((-w + 2 * w * k / n, y + 1))
            pts += [(w, y), (w * 0.25, y - 52 + i * 3), (0, y - 60 + i * 3), (-w * 0.25, y - 52 + i * 3)]
            smooth_poly(c, pts, tension=0.25)
        paint(ctx, tier, PINE, sh=w * 0.18, hl=2, line=1.2, deep=w * 0.35)
        stroke(ctx, lambda c, y=y, w=w: (c.move_to(-w * 0.4, y - 16), c.line_to(-w * 0.15, y - 30)), PINE.light, 1.5, 0.7)


@prop('bush', 90, 70, 45, 62, col=(40, 12, 0), shadow=(3, 0, 38, 10, 0.3))
def bush(ctx):
    canopy(ctx, 0, -24, 36, 22, LEAF, 21, n=8)


@prop('bush_flower', 90, 70, 45, 62, col=(40, 12, 0), shadow=(3, 0, 38, 10, 0.3))
def bush_flower(ctx):
    canopy(ctx, 0, -24, 36, 22, Pal('#4fa04a', '#36803c', '#7fc85a', '#1a4424'), 22, n=8)
    rnd = random.Random(9)
    for i in range(10):
        x, y = rnd.uniform(-28, 28), -24 + rnd.uniform(-16, 14)
        col = rnd.choice([Pal('#ff8fb0', '#e0608a', '#ffd0e0', '#6a1e3a'), Pal('#fff2a0', '#e8c860', '#ffffff', '#6a5010')])
        for k in range(5):
            a = k / 5 * math.tau
            flat(ctx, lambda c, a=a, x=x, y=y: ellipse(c, x + math.cos(a) * 2.2, y + math.sin(a) * 2.2, 1.8, 1.8),
                 col.base)
        flat(ctx, lambda c, x=x, y=y: ellipse(c, x, y, 1.2, 1.2), hx('#ffcf40'))


@prop('rock_big', 110, 80, 55, 68, col=(70, 22, -4), shadow=(3, 0, 48, 12, 0.32))
def rock_big(ctx):
    paint(ctx, lambda c: smooth_poly(c, [(-44, 0), (-46, -18), (-30, -40), (-4, -50), (24, -44), (44, -24), (46, -2),
                                         (20, 6), (-20, 6)], tension=0.4), STONE, sh=8, hl=2.5, deep=14)
    stroke(ctx, lambda c: (c.move_to(-10, -46), c.curve_to(-6, -30, 4, -22, 12, -16)), STONE.shadow, 1.3)
    flat(ctx, lambda c: blob(c, [(-18, -36, 7), (-6, -42, 6)]), hx('#7fbf5a'), 0.85)   # moss


@prop('rock_small', 56, 40, 28, 34, col=(30, 10, -2), shadow=(2, 0, 24, 7, 0.3))
def rock_small(ctx):
    paint(ctx, lambda c: smooth_poly(c, [(-22, 0), (-20, -14), (-6, -24), (12, -22), (22, -8), (18, 3), (-10, 4)],
                                     tension=0.4), STONE, sh=4, hl=1.6, deep=8)


@prop('stump', 60, 50, 30, 42, col=(36, 12, 0), shadow=(2, 0, 26, 8, 0.3))
def stump(ctx):
    paint(ctx, lambda c: smooth_poly(c, [(-20, 0), (-18, -20), (18, -20), (20, 0), (8, 4), (-8, 4)], tension=0.3), BARK,
          sh=3, hl=1.2)
    paint(ctx, lambda c: ellipse(c, 0, -20, 18, 7), Pal('#e0b47a', '#c08d58', '#f8d6a0', '#5a3418'), sh=1.5, hl=1)
    for r in (4, 9, 13):
        stroke(ctx, lambda c, r=r: ellipse(c, 0, -20, r, r * 0.38), hx('#b07c4a'), 0.9, 0.8)


@prop('tuft', 40, 30, 20, 26, outline=0.8)
def tuft(ctx):
    for i, a in enumerate((-30, -14, 0, 14, 28)):
        r = math.radians(a)
        tip = (math.sin(r) * 18, -math.cos(r) * 20 + abs(a) * 0.15)
        pal = LEAF if i % 2 else LEAF_DK
        paint(ctx, lambda c, tip=tip, a=a: smooth_poly(c, [(a * 0.12 - 3, 0), tip, (a * 0.12 + 3, 0)], tension=0.2),
              pal, sh=1, hl=0.6, line=0.8)


@prop('flowers', 60, 40, 30, 32, outline=0)
def flowers(ctx):
    rnd = random.Random(31)
    cols = ['#ff6f91', '#ffd84a', '#ffffff', '#9a7bff', '#ff9a4a']
    for i in range(7):
        x, y = rnd.uniform(-22, 22), rnd.uniform(-14, 0)
        stroke(ctx, lambda c, x=x, y=y: (c.move_to(x, y + 6), c.line_to(x, y)), LEAF_DK.base, 1.4)
        col = hx(rnd.choice(cols))
        for k in range(5):
            a = k / 5 * math.tau
            paint(ctx, lambda c, a=a, x=x, y=y: ellipse(c, x + math.cos(a) * 2.4, y + math.sin(a) * 2.2, 2.0, 2.0),
                  Pal(col, shade(col, -0.12), shade(col, 0.1), shade(col, -0.45)), sh=0.5, hl=0, line=0.6)
        flat(ctx, lambda c, x=x, y=y: ellipse(c, x, y, 1.3, 1.3), hx('#ffb020'))


# ------------------------------------------------------------------ village props
@prop('fence', 72, 60, 36, 50, col=(64, 8, 0), shadow=(0, 0, 34, 5, 0.25))
def fence(ctx):
    for x in (-30, 30):
        paint(ctx, lambda c, x=x: smooth_poly(c, [(x - 4.5, 2), (x - 4.5, -36), (x, -41), (x + 4.5, -36), (x + 4.5, 2)],
                                              tension=0.1), WOOD, sh=2, hl=1)
    for y in (-30, -14):
        paint(ctx, lambda c, y=y: smooth_poly(c, [(-34, y - 4), (34, y - 4), (34, y + 4), (-34, y + 4)], tension=0.05),
              WOOD, sh=2, hl=1)


@prop('fence_v', 30, 90, 15, 80, col=(10, 64, 32), shadow=(0, -30, 8, 34, 0.22))
def fence_v(ctx):
    paint(ctx, lambda c: smooth_poly(c, [(-3, -8), (3, -8), (3, -70), (-3, -70)], tension=0.05), WOOD_DK, sh=1.5, hl=0.6)
    for y in (2, -64):
        paint(ctx, lambda c, y=y: smooth_poly(c, [(-4.5, y), (-4.5, y - 34), (0, y - 39), (4.5, y - 34), (4.5, y)],
                                              tension=0.1), WOOD, sh=2, hl=1)


@prop('barrel', 50, 64, 25, 58, col=(36, 14, 0), shadow=(2, 0, 22, 7, 0.3))
def barrel(ctx):
    paint(ctx, lambda c: smooth_poly(c, [(-17, 0), (-20, -20), (-17, -42), (17, -42), (20, -20), (17, 0), (0, 3)],
                                     tension=0.45), WOOD, sh=4, hl=1.5)
    for y in (-8, -34):
        stroke(ctx, lambda c, y=y: (c.move_to(-19, y), c.curve_to(-8, y + 3, 8, y + 3, 19, y)), WOOD.line, 3.2)
        stroke(ctx, lambda c, y=y: (c.move_to(-19, y), c.curve_to(-8, y + 3, 8, y + 3, 19, y)), hx('#8a8aa0'), 1.8)
    paint(ctx, lambda c: ellipse(c, 0, -42, 17, 6), WOOD_DK, sh=1.2, hl=0.8)


@prop('crate', 56, 60, 28, 54, col=(46, 16, 0), shadow=(3, 0, 26, 7, 0.3))
def crate(ctx):
    paint(ctx, lambda c: smooth_poly(c, [(-22, 0), (-22, -30), (22, -30), (22, 0)], tension=0.02), WOOD, sh=3, hl=1)
    paint(ctx, lambda c: smooth_poly(c, [(-22, -30), (-16, -42), (26, -42), (22, -30)], tension=0.02),
          Pal(WOOD.light, WOOD.base, shade(WOOD.light, 0.06), WOOD.line), sh=1, hl=0.5)
    paint(ctx, lambda c: smooth_poly(c, [(22, 0), (22, -30), (26, -42), (26, -10)], tension=0.02),
          Pal(WOOD.shadow, WOOD.deep, WOOD.base, WOOD.line), sh=0, hl=0)
    stroke(ctx, lambda c: (c.move_to(-20, -2), c.line_to(20, -28)), WOOD_DK.base, 3)
    stroke(ctx, lambda c: (c.move_to(-20, -28), c.line_to(20, -2)), WOOD_DK.base, 3)


@prop('well', 120, 150, 60, 132, col=(80, 30, 0), shadow=(4, 0, 50, 13, 0.32))
def well(ctx):
    # base ring of stones
    paint(ctx, lambda c: smooth_poly(c, [(-42, 0), (-44, -30), (44, -30), (42, 0), (0, 8)], tension=0.3), STONE, sh=5,
          hl=2)
    rnd = random.Random(4)
    for row, y in enumerate((-6, -18)):
        for i in range(7):
            x = -36 + i * 12 + (6 if row else 0)
            if abs(x) < 42:
                stroke(ctx, lambda c, x=x, y=y: (c.move_to(x, y - 5), c.line_to(x, y + 5)), STONE.shadow, 1.1)
    paint(ctx, lambda c: ellipse(c, 0, -30, 44, 13), STONE, sh=2, hl=1.5)
    paint(ctx, lambda c: ellipse(c, 0, -30, 34, 9), Pal('#2c4a6a', '#1c3048', '#4a7aa0', '#0c1a2a'), sh=3, hl=0, line=1)
    # posts and roof
    for x in (-36, 36):
        paint(ctx, lambda c, x=x: smooth_poly(c, [(x - 4, -26), (x - 4, -96), (x + 4, -96), (x + 4, -26)], tension=0.02),
              WOOD, sh=2, hl=1)
    stroke(ctx, lambda c: (c.move_to(-36, -78), c.line_to(36, -78)), WOOD_DK.line, 4)
    stroke(ctx, lambda c: (c.move_to(0, -78), c.line_to(0, -48)), hx('#c8b48a'), 1.2)
    paint(ctx, lambda c: smooth_poly(c, [(-8, -48), (8, -48), (7, -36), (-7, -36)], tension=0.1), WOOD, sh=1.5, hl=0.6)
    paint(ctx, lambda c: smooth_poly(c, [(-54, -88), (0, -124), (54, -88), (46, -84), (0, -112), (-46, -84)],
                                     tension=0.05), ROOF_O, sh=4, hl=2)


@prop('lamp', 40, 130, 20, 122, col=(12, 8, 0), shadow=(2, 0, 12, 4, 0.3))
def lamp(ctx):
    paint(ctx, lambda c: smooth_poly(c, [(-8, 0), (-5, -8), (-3, -86), (3, -86), (5, -8), (8, 0)], tension=0.2),
          Pal('#4a4a5e', '#33334a', '#6e6e88', '#16161f'), sh=1.5, hl=0.8)
    radial_glow(ctx, 0, -98, 28, hx('#ffd27a'), 0.5)
    paint(ctx, lambda c: smooth_poly(c, [(-9, -88), (9, -88), (11, -108), (-11, -108)], tension=0.1), GLASS, sh=1, hl=1)
    flat(ctx, lambda c: ellipse(c, 0, -98, 6, 8), hx('#fff1b0'), 0.95)
    paint(ctx, lambda c: smooth_poly(c, [(-14, -108), (0, -118), (14, -108)], tension=0.1),
          Pal('#4a4a5e', '#33334a', '#6e6e88', '#16161f'), sh=1, hl=0.6)


@prop('sign', 60, 80, 30, 72, col=(10, 8, 0), shadow=(2, 0, 16, 5, 0.3))
def sign(ctx):
    paint(ctx, lambda c: smooth_poly(c, [(-3, 0), (-3, -56), (3, -56), (3, 0)], tension=0.02), WOOD_DK, sh=1.2, hl=0.5)
    paint(ctx, lambda c: smooth_poly(c, [(-24, -60), (18, -60), (26, -52), (18, -44), (-24, -44)], tension=0.05), WOOD,
          sh=2, hl=1)
    for y in (-55, -49):
        stroke(ctx, lambda c, y=y: (c.move_to(-18, y), c.line_to(12, y)), WOOD.line, 1.3, 0.6)


@prop('quest_board', 130, 120, 65, 108, col=(100, 14, 0), shadow=(3, 0, 54, 10, 0.32))
def quest_board(ctx):
    for x in (-48, 48):
        paint(ctx, lambda c, x=x: smooth_poly(c, [(x - 5, 0), (x - 5, -92), (x + 5, -92), (x + 5, 0)], tension=0.02),
              WOOD_DK, sh=2, hl=1)
    paint(ctx, lambda c: smooth_poly(c, [(-52, -88), (52, -88), (52, -26), (-52, -26)], tension=0.02), WOOD, sh=3, hl=1.5)
    paint(ctx, lambda c: smooth_poly(c, [(-60, -88), (0, -104), (60, -88), (56, -82), (-56, -82)], tension=0.05),
          ROOF_O, sh=2.5, hl=1.4)
    rnd = random.Random(12)
    for i in range(6):
        x = -38 + (i % 3) * 32 + rnd.uniform(-3, 3)
        y = -76 + (i // 3) * 26 + rnd.uniform(-2, 2)
        a = rnd.uniform(-8, 8)
        ctx.save()
        ctx.translate(x, y)
        ctx.rotate(math.radians(a))
        paint(ctx, lambda c: smooth_poly(c, [(-11, 0), (11, 0), (11, 20), (-11, 20)], tension=0.02),
              Pal('#fff6dc', '#e6d4a8', '#ffffff', '#6b5038'), sh=1, hl=0, line=0.8)
        for k in range(3):
            stroke(ctx, lambda c, k=k: (c.move_to(-7, 6 + k * 4), c.line_to(7 - (k == 2) * 5, 6 + k * 4)), hx('#8a7458'),
                   1.0, 0.8)
        flat(ctx, lambda c: ellipse(c, 0, 2, 1.8, 1.8), hx('#d6453d'))
        ctx.restore()


@prop('stall', 170, 160, 85, 146, col=(140, 30, 0), shadow=(4, 0, 74, 14, 0.32))
def stall(ctx):
    paint(ctx, lambda c: smooth_poly(c, [(-70, 0), (-70, -44), (70, -44), (70, 0)], tension=0.02), WOOD, sh=4, hl=1.5)
    for x in (-66, 66):
        paint(ctx, lambda c, x=x: smooth_poly(c, [(x - 4, -40), (x - 4, -110), (x + 4, -110), (x + 4, -40)],
                                              tension=0.02), WOOD_DK, sh=2, hl=1)
    # goods
    rnd = random.Random(2)
    for i in range(9):
        x = -54 + i * 13.5
        col = rnd.choice([Pal('#f05a4a', '#c23a3a', '#ff9a80', '#5a1418'), Pal('#ffcf40', '#e0a020', '#fff0a0', '#6a4a10'),
                          Pal('#8ccf4a', '#5fa032', '#c0f080', '#2a4a10')])
        paint(ctx, lambda c, x=x: ellipse(c, x, -50, 6.5, 6), col, sh=1.5, hl=1, line=0.8)
    # awning with stripes + scalloped edge
    def awning(c):
        c.move_to(-80, -104)
        c.line_to(-62, -138)
        c.line_to(62, -138)
        c.line_to(80, -104)
        for i in range(8):
            x0 = 80 - i * 20
            c.curve_to(x0 - 4, -94, x0 - 16, -94, x0 - 20, -104)
        c.close_path()
    paint(ctx, awning, Pal('#fff2dc', '#e6d2b0', '#ffffff', '#6a4630'), sh=3, hl=1.2)
    ctx.save()
    ctx.new_path()
    awning(ctx)
    ctx.clip()
    for i in range(8):
        x0 = -80 + i * 20

        def stripe(c, x0=x0):
            c.move_to(x0, -104)
            c.line_to(x0 * 0.775, -138)
            c.line_to(x0 * 0.775 + 10, -138)
            c.line_to(x0 + 10, -104)
            c.line_to(x0 + 10, -90)
            c.line_to(x0, -90)
            c.close_path()
        if i % 2 == 0:
            flat(ctx, stripe, CLOTH_R.base)
    ctx.restore()


@prop('bridge', 260, 150, 130, 120, col=None, outline=1.0)
def bridge(ctx):
    # horizontal planked bridge (walkable); railings top and bottom
    paint(ctx, lambda c: smooth_poly(c, [(-128, -76), (128, -76), (128, 6), (-128, 6)], tension=0.02), WOOD, sh=0, hl=0,
          grad=True)
    for i in range(16):
        x = -128 + i * 16
        stroke(ctx, lambda c, x=x: (c.move_to(x, -76), c.line_to(x, 6)), WOOD.shadow, 1.6)
    for y in (-80, 4):
        paint(ctx, lambda c, y=y: smooth_poly(c, [(-130, y - 4), (130, y - 4), (130, y + 4), (-130, y + 4)],
                                              tension=0.02), WOOD_DK, sh=2, hl=1)
    for x in (-124, -62, 0, 62, 124):
        for y in (-80, 4):
            paint(ctx, lambda c, x=x, y=y: smooth_poly(c, [(x - 5, y + 4), (x - 5, y - 22), (x + 5, y - 22), (x + 5, y + 4)],
                                                       tension=0.02), WOOD_DK, sh=2, hl=1)
    for y in (-98, -14):
        paint(ctx, lambda c, y=y: smooth_poly(c, [(-130, y - 3), (130, y - 3), (130, y + 3), (-130, y + 3)],
                                              tension=0.02), WOOD, sh=1.5, hl=0.8)


# ------------------------------------------------------------------ buildings
def roof_tiles(ctx, quad, pal, rows=6, cols=10):
    """Scalloped clay/slate tiles inside a quad (tl, tr, br, bl)."""
    tl, tr, br, bl = quad

    def L(p, q, t):
        return p[0] + (q[0] - p[0]) * t, p[1] + (q[1] - p[1]) * t
    ctx.save()
    ctx.new_path()
    ctx.move_to(*tl)
    ctx.line_to(*tr)
    ctx.line_to(*br)
    ctx.line_to(*bl)
    ctx.close_path()
    ctx.clip()
    for r in range(rows + 1):
        t = r / rows
        a, b = L(tl, bl, t), L(tr, br, t)
        h = (bl[1] - tl[1]) / rows
        n = cols
        for k in range(n + 1):
            u = (k + (0.5 if r % 2 else 0)) / n
            x, y = L(a, b, u)
            w = (b[0] - a[0]) / n
            def tile(c, x=x, y=y, w=w, h=h):
                c.move_to(x - w / 2, y - h)
                c.line_to(x - w / 2, y - h * 0.15)
                c.curve_to(x - w / 2, y + h * 0.25, x + w / 2, y + h * 0.25, x + w / 2, y - h * 0.15)
                c.line_to(x + w / 2, y - h)
            stroke(ctx, tile, pal.shadow, 1.4)
            stroke(ctx, lambda c, x=x, y=y, w=w, h=h: (c.move_to(x - w * 0.32, y - h * 0.55),
                                                       c.line_to(x - w * 0.32, y - h * 0.2)), pal.light, 1.2, 0.6)
    ctx.restore()


def window(ctx, x, y, w=22, h=26, shutters=True, box=True, lit=False):
    paint(ctx, lambda c: smooth_poly(c, [(x - w / 2 - 3, y - h - 3), (x + w / 2 + 3, y - h - 3), (x + w / 2 + 3, y + 3),
                                         (x - w / 2 - 3, y + 3)], tension=0.02), WOOD_DK, sh=1, hl=0.5, line=1)
    g = GLASS if not lit else Pal('#ffe08a', '#f0b040', '#fff6c8', '#6a4010')
    paint(ctx, lambda c: smooth_poly(c, [(x - w / 2, y - h), (x + w / 2, y - h), (x + w / 2, y), (x - w / 2, y)],
                                     tension=0.02), g, sh=3, hl=0, line=0.8, light=(-0.6, -0.8))
    stroke(ctx, lambda c: (c.move_to(x, y - h), c.line_to(x, y), c.move_to(x - w / 2, y - h / 2), c.line_to(x + w / 2, y - h / 2)),
           WOOD_DK.base, 2.2)
    stroke(ctx, lambda c: (c.move_to(x - w / 2 + 3, y - 5), c.line_to(x - 3, y - h + 3)), hx('#ffffff'), 1.6, 0.6)
    if shutters:
        for sx in (-1, 1):
            xx = x + sx * (w / 2 + 3 + 6)
            paint(ctx, lambda c, xx=xx: smooth_poly(c, [(xx - 6, y - h - 3), (xx + 6, y - h - 3), (xx + 6, y + 3),
                                                        (xx - 6, y + 3)], tension=0.02), CLOTH_B, sh=1.5, hl=0.6)
            for k in range(4):
                stroke(ctx, lambda c, xx=xx, k=k: (c.move_to(xx - 4, y - h + 3 + k * 7), c.line_to(xx + 4, y - h + 3 + k * 7)),
                       CLOTH_B.shadow, 1.1)
    if box:
        paint(ctx, lambda c: smooth_poly(c, [(x - w / 2 - 5, y + 3), (x + w / 2 + 5, y + 3), (x + w / 2 + 3, y + 11),
                                             (x - w / 2 - 3, y + 11)], tension=0.02), WOOD, sh=1.5, hl=0.6)
        rnd = random.Random(int(x * 7 + y))
        for i in range(6):
            fx = x - w / 2 + 1 + i * (w / 5)
            col = rnd.choice(['#ff6f91', '#ffd84a', '#ffffff', '#ff8a4a'])
            flat(ctx, lambda c, fx=fx: blob(c, [(fx, y + 1, 3.6)]), LEAF.base)
            flat(ctx, lambda c, fx=fx: blob(c, [(fx + 1, y - 0.5, 2.2)]), hx(col))


def door(ctx, x, y, w=30, h=46, pal=WOOD_DK, arch=True):
    def d(c):
        c.move_to(x - w / 2, y)
        c.line_to(x - w / 2, y - h + w / 2)
        if arch:
            c.arc(x, y - h + w / 2, w / 2, math.pi, 2 * math.pi)
        else:
            c.line_to(x - w / 2, y - h)
            c.line_to(x + w / 2, y - h)
        c.line_to(x + w / 2, y)
        c.close_path()
    paint(ctx, lambda c: (c.save(), c.translate(0, 0), d(c), c.restore()), Pal('#9a8a7a', '#7a6a5a', '#c0b0a0', '#3a2a20'),
          sh=0, hl=0, line=1)
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(0.86, 0.94)
    ctx.translate(-x, -y)
    paint(ctx, d, pal, sh=4, hl=1.2)
    for k in (-1, 0, 1):
        stroke(ctx, lambda c, k=k: (c.move_to(x + k * w / 4, y - 2), c.line_to(x + k * w / 4, y - h + 8)), pal.shadow, 1.3)
    ctx.restore()
    flat(ctx, lambda c: ellipse(c, x + w / 2 - 7, y - h / 2 + 2, 2, 2), METAL.base)


@prop('house_a', 260, 300, 130, 268, col=(210, 70, 26), shadow=(6, 0, 118, 22, 0.35))
def house_a(ctx):
    W, H = 100, 104
    # stone foundation + walls
    paint(ctx, lambda c: smooth_poly(c, [(-W, 0), (-W, -H), (W, -H), (W, 0)], tension=0.01), PLASTER, sh=0, hl=0)
    # wall shading from roof eave
    flat(ctx, lambda c: smooth_poly(c, [(-W, -H), (W, -H), (W, -H + 16), (-W, -H + 10)], tension=0.01), PLASTER.shadow, 0.9)
    # timber frame
    for x in (-W + 4, -34, 34, W - 4):
        paint(ctx, lambda c, x=x: smooth_poly(c, [(x - 4, -16), (x - 4, -H), (x + 4, -H), (x + 4, -16)], tension=0.01),
              WOOD_DK, sh=1.5, hl=0.6, line=0.9)
    paint(ctx, lambda c: smooth_poly(c, [(-W, -60), (W, -60), (W, -52), (-W, -52)], tension=0.01), WOOD_DK, sh=1.5,
          hl=0.6, line=0.9)
    # foundation stones
    paint(ctx, lambda c: smooth_poly(c, [(-W - 4, 2), (-W - 4, -18), (W + 4, -18), (W + 4, 2)], tension=0.02), STONE,
          sh=3, hl=1.2)
    for i in range(11):
        x = -W + 6 + i * 19
        stroke(ctx, lambda c, x=x: (c.move_to(x, -16), c.line_to(x, 0)), STONE.shadow, 1.2)
    door(ctx, 0, -2, 34, 52)
    window(ctx, -66, -66, 24, 26)
    window(ctx, 66, -66, 24, 26)
    window(ctx, -66, -24, 18, 16, shutters=False, box=False)
    # step
    paint(ctx, lambda c: smooth_poly(c, [(-24, 6), (24, 6), (22, -2), (-22, -2)], tension=0.02), STONE, sh=1.5, hl=1)
    # roof (front slope seen from above): quad + overhang
    quad = ((-W - 6, -H - 104), (W + 6, -H - 104), (W + 22, -H + 6), (-W - 22, -H + 6))
    paint(ctx, lambda c: smooth_poly(c, list(quad), tension=0.0), ROOF_O, sh=0, hl=0)
    roof_tiles(ctx, quad, ROOF_O, rows=7, cols=11)
    # eave shading + ridge
    stroke(ctx, lambda c: (c.move_to(-W - 22, -H + 6), c.line_to(W + 22, -H + 6)), ROOF_O.line, 2)
    paint(ctx, lambda c: smooth_poly(c, [(-W - 10, -H - 110), (W + 10, -H - 110), (W + 6, -H - 100), (-W - 6, -H - 100)],
                                     tension=0.02), Pal('#c9583a', '#a1402a', '#e87a50', '#4a1810'), sh=1.5, hl=1)
    # chimney
    paint(ctx, lambda c: smooth_poly(c, [(46, -H - 84), (46, -H - 130), (70, -H - 130), (70, -H - 92)], tension=0.02),
          STONE, sh=3, hl=1.5)
    paint(ctx, lambda c: smooth_poly(c, [(43, -H - 130), (73, -H - 130), (73, -H - 138), (43, -H - 138)], tension=0.02),
          Pal('#8a8898', '#6a687a', '#b0aec0', '#2a2836'), sh=1.5, hl=1)
    # dormer window
    paint(ctx, lambda c: smooth_poly(c, [(-30, -H - 30), (-30, -H - 64), (0, -H - 84), (30, -H - 64), (30, -H - 30)],
                                     tension=0.02), PLASTER, sh=2, hl=1)
    window(ctx, 0, -H - 38, 20, 22, shutters=False, box=False)
    paint(ctx, lambda c: smooth_poly(c, [(-38, -H - 60), (0, -H - 92), (38, -H - 60), (32, -H - 56), (0, -H - 82),
                                         (-32, -H - 56)], tension=0.02), ROOF_O, sh=2, hl=1.2)


@prop('house_b', 230, 280, 115, 250, col=(186, 62, 24), shadow=(6, 0, 104, 20, 0.35))
def house_b(ctx):
    W, H = 86, 92
    stonew = Pal('#d8cbb6', '#b8a890', '#f2e8d6', '#5a4a38')
    paint(ctx, lambda c: smooth_poly(c, [(-W, 0), (-W, -H), (W, -H), (W, 0)], tension=0.01), stonew, sh=0, hl=0)
    rnd = random.Random(6)
    for row in range(6):
        y = -6 - row * 15
        off = 12 if row % 2 else 0
        for i in range(8):
            x = -W + off + i * 24
            if -W < x < W:
                stroke(ctx, lambda c, x=x, y=y: (c.move_to(x, y), c.line_to(x, y - 13)), stonew.shadow, 1.1, 0.8)
        stroke(ctx, lambda c, y=y: (c.move_to(-W, y - 14), c.line_to(W, y - 14)), stonew.shadow, 1.0, 0.6)
    flat(ctx, lambda c: smooth_poly(c, [(-W, -H), (W, -H), (W, -H + 14), (-W, -H + 9)], tension=0.01), stonew.shadow, 0.9)
    door(ctx, -36, -1, 30, 48, pal=Pal('#4f78b8', '#3a5b94', '#7aa2dc', '#182a4a'))
    window(ctx, 30, -40, 34, 30, shutters=True, box=True, lit=True)
    quad = ((-W - 4, -H - 92), (W + 4, -H - 92), (W + 20, -H + 6), (-W - 20, -H + 6))
    paint(ctx, lambda c: smooth_poly(c, list(quad), tension=0.0), ROOF_B, sh=0, hl=0)
    roof_tiles(ctx, quad, ROOF_B, rows=6, cols=9)
    stroke(ctx, lambda c: (c.move_to(-W - 20, -H + 6), c.line_to(W + 20, -H + 6)), ROOF_B.line, 2)
    paint(ctx, lambda c: smooth_poly(c, [(-W - 8, -H - 98), (W + 8, -H - 98), (W + 4, -H - 88), (-W - 4, -H - 88)],
                                     tension=0.02), Pal('#3a5b94', '#2c4678', '#5a80c0', '#142040'), sh=1.5, hl=1)
    paint(ctx, lambda c: smooth_poly(c, [(-62, -H - 70), (-62, -H - 118), (-40, -H - 118), (-40, -H - 76)], tension=0.02),
          STONE, sh=3, hl=1.5)


@prop('guild', 420, 400, 210, 360, col=(360, 90, 30), shadow=(8, 0, 190, 30, 0.38))
def guild(ctx):
    W, H = 170, 160
    wall = Pal('#efe0c2', '#d2bd98', '#fff6e0', '#6b5038')
    # wings
    paint(ctx, lambda c: smooth_poly(c, [(-W, 0), (-W, -H), (W, -H), (W, 0)], tension=0.01), wall, sh=0, hl=0)
    flat(ctx, lambda c: smooth_poly(c, [(-W, -H), (W, -H), (W, -H + 18), (-W, -H + 12)], tension=0.01), wall.shadow, 0.9)
    for x in (-W + 5, -110, -60, 60, 110, W - 5):
        paint(ctx, lambda c, x=x: smooth_poly(c, [(x - 5, -20), (x - 5, -H), (x + 5, -H), (x + 5, -20)], tension=0.01),
              WOOD_DK, sh=1.5, hl=0.6, line=0.9)
    for y in (-86, -92):
        pass
    paint(ctx, lambda c: smooth_poly(c, [(-W, -92), (W, -92), (W, -82), (-W, -82)], tension=0.01), WOOD_DK, sh=1.5,
          hl=0.6, line=0.9)
    paint(ctx, lambda c: smooth_poly(c, [(-W - 5, 3), (-W - 5, -22), (W + 5, -22), (W + 5, 3)], tension=0.02), STONE,
          sh=3, hl=1.2)
    for i in range(18):
        x = -W + 8 + i * 20
        stroke(ctx, lambda c, x=x: (c.move_to(x, -20), c.line_to(x, 1)), STONE.shadow, 1.2)
    for x in (-136, -86, 86, 136):
        window(ctx, x, -36, 26, 30, shutters=False, box=True, lit=True)
        window(ctx, x, -112, 24, 26, shutters=False, box=False)
    # central tower/gable
    paint(ctx, lambda c: smooth_poly(c, [(-56, 0), (-56, -H - 40), (56, -H - 40), (56, 0)], tension=0.01),
          Pal('#e2cfa8', '#c4ad84', '#f6e8c8', '#5b4630'), sh=4, hl=1.5)
    for x in (-52, 52):
        paint(ctx, lambda c, x=x: smooth_poly(c, [(x - 5, -20), (x - 5, -H - 40), (x + 5, -H - 40), (x + 5, -20)],
                                              tension=0.01), WOOD_DK, sh=1.5, hl=0.6, line=0.9)
    door(ctx, 0, -2, 56, 80, pal=Pal('#8a4a2e', '#6a3420', '#b06a44', '#2e140a'))
    # steps
    for i, w in enumerate((44, 38)):
        paint(ctx, lambda c, i=i, w=w: smooth_poly(c, [(-w, 8 - i * 6), (w, 8 - i * 6), (w - 2, 2 - i * 6), (-w + 2, 2 - i * 6)],
                                                   tension=0.02), STONE, sh=1.5, hl=1)
    # emblem: shield + crossed swords
    ey = -H + 6
    for s in (-1, 1):
        stroke(ctx, lambda c, s=s: (c.move_to(-s * 26, ey + 22), c.line_to(s * 26, ey - 26)), hx('#3b4660'), 5)
        stroke(ctx, lambda c, s=s: (c.move_to(-s * 26, ey + 22), c.line_to(s * 26, ey - 26)), hx('#dfe8f2'), 3)
    paint(ctx, lambda c: smooth_poly(c, [(-20, ey - 22), (20, ey - 22), (20, ey + 2), (0, ey + 24), (-20, ey + 2)],
                                     tension=0.3), CLOTH_R, sh=3, hl=1.5)
    paint(ctx, lambda c: smooth_poly(c, [(0, ey - 14), (6, ey - 2), (0, ey + 12), (-6, ey - 2)], tension=0.1), METAL,
          sh=1.2, hl=0.8)
    # sign board
    paint(ctx, lambda c: smooth_poly(c, [(-50, -104), (50, -104), (50, -86), (-50, -86)], tension=0.1), WOOD, sh=2, hl=1)
    # main roofs
    quad = ((-W - 8, -H - 96), (W + 8, -H - 96), (W + 26, -H + 8), (-W - 26, -H + 8))
    paint(ctx, lambda c: smooth_poly(c, list(quad), tension=0.0), ROOF_S, sh=0, hl=0)
    roof_tiles(ctx, quad, ROOF_S, rows=7, cols=16)
    stroke(ctx, lambda c: (c.move_to(-W - 26, -H + 8), c.line_to(W + 26, -H + 8)), ROOF_S.line, 2)
    # tower gable roof (triangle facing front)
    paint(ctx, lambda c: smooth_poly(c, [(-70, -H - 30), (0, -H - 150), (70, -H - 30)], tension=0.0), ROOF_S, sh=6, hl=2)
    roof_tiles(ctx, ((-6, -H - 150), (6, -H - 150), (70, -H - 30), (-70, -H - 30)), ROOF_S, rows=6, cols=7)
    paint(ctx, lambda c: smooth_poly(c, [(-76, -H - 26), (0, -H - 158), (76, -H - 26), (68, -H - 24), (0, -H - 142),
                                         (-68, -H - 24)], tension=0.0), Pal('#7a4a30', '#5a3420', '#a06a48', '#2a140a'),
          sh=1.5, hl=1)
    # gable round window
    paint(ctx, lambda c: ellipse(c, 0, -H - 70, 16, 16), WOOD_DK, sh=1, hl=0.5)
    paint(ctx, lambda c: ellipse(c, 0, -H - 70, 12, 12), Pal('#ffe08a', '#f0b040', '#fff6c8', '#6a4010'), sh=2.5, hl=0)
    stroke(ctx, lambda c: (c.move_to(-12, -H - 70), c.line_to(12, -H - 70), c.move_to(0, -H - 82), c.line_to(0, -H - 58)),
           WOOD_DK.base, 2)
    # banners
    for x in (-82, 82):
        paint(ctx, lambda c, x=x: smooth_poly(c, [(x - 13, -H + 14), (x + 13, -H + 14), (x + 13, -H + 66), (x, -H + 58),
                                                  (x - 13, -H + 66)], tension=0.05), CLOTH_R, sh=3, hl=1.2)
        paint(ctx, lambda c, x=x: smooth_poly(c, [(x, -H + 26), (x + 5, -H + 36), (x, -H + 46), (x - 5, -H + 36)],
                                              tension=0.1), METAL, sh=1, hl=0.6, line=0.8)
        stroke(ctx, lambda c, x=x: (c.move_to(x - 16, -H + 14), c.line_to(x + 16, -H + 14)), WOOD_DK.base, 3)
    # flag on top
    stroke(ctx, lambda c: (c.move_to(0, -H - 156), c.line_to(0, -H - 200)), hx('#3a2a20'), 2.4)
    paint(ctx, lambda c: smooth_poly(c, [(1, -H - 200), (34, -H - 194), (24, -H - 186), (34, -H - 178), (1, -H - 182)],
                                     tension=0.2), CLOTH_R, sh=2, hl=1)


# ------------------------------------------------------------------ Velmoor (corrupted elven forest)
LEAF_CURSE = Pal('#4a6a5a', '#33504a', '#6a9070', '#122420')
LEAF_VIOLET = Pal('#5a4a7a', '#3e3260', '#7e6aa0', '#1a1030')
BARK_DK = Pal('#5a4048', '#3e2a32', '#7a5a62', '#1a0e12')
RUIN = Pal('#b8c0b0', '#8a9488', '#e0e6da', '#3a4038')


@prop('tree_twisted', 210, 240, 105, 224, col=(26, 14, 0), shadow=(6, 0, 72, 20, 0.4))
def tree_twisted(ctx):
    def trunk(c):
        smooth_poly(c, [(-16, 0), (-8, -14), (-14, -44), (-30, -66), (-12, -58), (-2, -84), (6, -60), (26, -76), (12, -46),
                        (10, -14), (18, 0), (2, 4)], tension=0.45)
    paint(ctx, trunk, BARK_DK, sh=3.5, hl=1.5)
    for y in (-14, -30, -46):
        stroke(ctx, lambda c, y=y: (c.move_to(-6, y), c.curve_to(-2, y - 6, 4, y - 4, 6, y - 12)), BARK_DK.shadow, 1.3)
    canopy(ctx, -42, -118, 40, 30, LEAF_VIOLET, 31, n=9)
    canopy(ctx, 40, -112, 38, 30, LEAF_CURSE, 32, n=9)
    canopy(ctx, 0, -142, 60, 46, LEAF_CURSE, 33, n=12)
    for i, (x, y) in enumerate(((-30, -130), (26, -150), (6, -112), (-8, -160))):   # hanging glow spores
        radial_glow(ctx, x, y, 9, hx('#8affc0'), 0.7)
        flat(ctx, lambda c, x=x, y=y: ellipse(c, x, y, 2.2, 2.2), hx('#e8fff0'))


@prop('tree_dead', 160, 220, 80, 206, col=(20, 12, 0), shadow=(5, 0, 50, 15, 0.35))
def tree_dead(ctx):
    def trunk(c):
        smooth_poly(c, [(-12, 0), (-7, -40), (-24, -96), (-40, -120), (-20, -104), (-6, -70), (-2, -140), (6, -96), (30, -130),
                        (12, -78), (8, -40), (14, 0), (0, 3)], tension=0.35)
    paint(ctx, trunk, BARK_DK, sh=3, hl=1.4)
    for (x0, y0, x1, y1) in ((-24, -96, -46, -100), (6, -96, 22, -150), (-2, -130, -14, -170), (24, -124, 44, -118)):
        stroke(ctx, lambda c, a=(x0, y0, x1, y1): (c.move_to(a[0], a[1]), c.line_to(a[2], a[3])), BARK_DK.line, 4.5)
        stroke(ctx, lambda c, a=(x0, y0, x1, y1): (c.move_to(a[0], a[1]), c.line_to(a[2], a[3])), BARK_DK.base, 2.6)


@prop('mushrooms', 70, 60, 35, 52, col=None, shadow=(2, 0, 26, 7, 0.3))
def mushrooms(ctx):
    cap = Pal('#5ac8d0', '#3a90a8', '#a8f0f0', '#0a2a3a')
    for x, y, r in ((-14, -2, 9), (6, 0, 12), (20, -4, 7)):
        paint(ctx, lambda c, x=x, y=y, r=r: smooth_poly(c, [(x - 2.5, y), (x - 2, y - r), (x + 2, y - r), (x + 2.5, y)], tension=0.2),
              Pal('#f0e8d8', '#cfc4b0', '#ffffff', '#4a4030'), sh=1, hl=0.5, line=0.8)
        radial_glow(ctx, x, y - r - 2, r * 1.8, hx('#5affe0'), 0.45)
        paint(ctx, lambda c, x=x, y=y, r=r: smooth_poly(c, [(x - r, y - r + 1), (x - r * 0.6, y - r * 1.7), (x, y - r * 1.95),
                                                            (x + r * 0.6, y - r * 1.7), (x + r, y - r + 1)], tension=0.4),
              cap, sh=2, hl=1.4, line=0.9)
        for k in (-0.4, 0.3):
            flat(ctx, lambda c, x=x, y=y, r=r, k=k: ellipse(c, x + k * r, y - r * 1.5, 1.6, 1.3), hx('#e8ffff'))


@prop('roots', 120, 50, 60, 38, col=None, outline=0.8)
def roots(ctx):
    for i, (a, l) in enumerate(((-160, 50), (-20, 46), (170, 34), (10, 30))):
        r = math.radians(a)
        tip = (math.cos(r) * l, math.sin(r) * l * 0.35)
        mid = (tip[0] * 0.5, tip[1] * 0.5 - 6)
        paint(ctx, lambda c, tip=tip, mid=mid: (capsule(c, (0, 0), mid, 6, 4), capsule(c, mid, tip, 4, 1.5)), BARK_DK, sh=1.5, hl=0.8)


@prop('ruin_pillar', 80, 170, 40, 156, col=(44, 18, 0), shadow=(4, 0, 32, 9, 0.35))
def ruin_pillar(ctx):
    paint(ctx, lambda c: smooth_poly(c, [(-26, 4), (-26, -10), (26, -10), (26, 4)], tension=0.02), RUIN, sh=2, hl=1)
    paint(ctx, lambda c: smooth_poly(c, [(-18, -10), (-18, -110), (-8, -124), (2, -112), (10, -130), (18, -116), (18, -10)],
                                     tension=0.05), RUIN, sh=5, hl=2)
    for x in (-10, 0, 10):
        stroke(ctx, lambda c, x=x: (c.move_to(x, -14), c.line_to(x, -104)), RUIN.shadow, 1.4)
    paint(ctx, lambda c: smooth_poly(c, [(-8, -60), (0, -72), (8, -60), (0, -48)], tension=0.1),
          Pal('#8affc0', '#3ad090', '#e8fff0', '#0a3a20'), sh=1, hl=1, line=0.8)
    radial_glow(ctx, 0, -60, 16, hx('#8affc0'), 0.45)
    flat(ctx, lambda c: blob(c, [(-14, -40, 8), (-16, -28, 6), (12, -90, 7)]), hx('#5a8a4a'), 0.9)


@prop('ruin_arch', 260, 230, 130, 214, col=None, shadow=(6, 0, 110, 16, 0.32))
def ruin_arch(ctx):
    for sx in (-1, 1):
        paint(ctx, lambda c, sx=sx: smooth_poly(c, [(sx * 120, 4), (sx * 120, -150), (sx * 92, -150), (sx * 92, 4)], tension=0.02),
              RUIN, sh=5, hl=2)
    def arch(c):
        c.move_to(-124, -146)
        c.curve_to(-110, -230, 110, -230, 124, -146)
        c.line_to(96, -146)
        c.curve_to(84, -200, -84, -200, -96, -146)
        c.close_path()
    paint(ctx, arch, RUIN, sh=5, hl=2)
    paint(ctx, lambda c: smooth_poly(c, [(-10, -206), (0, -220), (10, -206), (0, -194)], tension=0.1),
          Pal('#8affc0', '#3ad090', '#e8fff0', '#0a3a20'), sh=1, hl=1, line=0.8)
    radial_glow(ctx, 0, -206, 22, hx('#8affc0'), 0.5)
    flat(ctx, lambda c: blob(c, [(-108, -120, 10), (-104, -100, 8), (106, -60, 9), (60, -196, 8)]), hx('#5a8a4a'), 0.9)


@prop('portal', 180, 120, 90, 96, col=None, outline=0)
def portal(ctx):
    for r, a in ((70, 0.25), (52, 0.45), (34, 0.7)):
        ctx.save(); ctx.scale(1, 0.45)
        radial_glow(ctx, 0, -40 / 0.45 * 0.45, r, hx('#8affc0'), a)
        ctx.restore()
    stroke(ctx, lambda c: ellipse(c, 0, -18, 62, 26), hx('#c8ffe0'), 2.5, 0.9)
    stroke(ctx, lambda c: ellipse(c, 0, -18, 44, 18), hx('#8affc0'), 1.6, 0.8)



# ------------------------------------------------------------------ Valemont (capital)
CITY_STONE = Pal('#c9c2b4', '#9e978a', '#ece6d8', '#443e34')
CITY_PLASTER = Pal('#e8d8b8', '#c8b490', '#fff4d8', '#5a4630')
ROOF_TEAL = Pal('#3a8a8a', '#276a6a', '#62b4ae', '#0e2a2a')


@prop('city_wall', 256, 170, 128, 150, col=(256, 40, 0), shadow=(0, 0, 124, 12, 0.35))
def city_wall(ctx):
    paint(ctx, lambda c: smooth_poly(c, [(-128, 0), (-128, -110), (128, -110), (128, 0)], tension=0.01), CITY_STONE, sh=0, hl=0)
    for row in range(7):
        y = -8 - row * 15
        off = 14 if row % 2 else 0
        for i in range(10):
            x = -128 + off + i * 28
            stroke(ctx, lambda c, x=x, y=y: (c.move_to(x, y), c.line_to(x, y - 15)), CITY_STONE.shadow, 1.1, 0.8)
        stroke(ctx, lambda c, y=y: (c.move_to(-128, y - 15), c.line_to(128, y - 15)), CITY_STONE.shadow, 1.0, 0.6)
    for i in range(8):   # battlements
        x = -128 + i * 34
        paint(ctx, lambda c, x=x: smooth_poly(c, [(x, -110), (x, -128), (x + 22, -128), (x + 22, -110)], tension=0.02), CITY_STONE, sh=2, hl=1)
    flat(ctx, lambda c: smooth_poly(c, [(-128, -110), (128, -110), (128, -96), (-128, -100)], tension=0.01), CITY_STONE.shadow, 0.8)


@prop('city_tower', 130, 260, 65, 240, col=(100, 50, 0), shadow=(4, 0, 58, 14, 0.35))
def city_tower(ctx):
    paint(ctx, lambda c: smooth_poly(c, [(-46, 0), (-46, -150), (46, -150), (46, 0)], tension=0.01), CITY_STONE, sh=6, hl=2)
    for row in range(9):
        y = -8 - row * 16
        for i in range(4):
            x = -46 + (10 if row % 2 else 0) + i * 24
            stroke(ctx, lambda c, x=x, y=y: (c.move_to(x, y), c.line_to(x, y - 16)), CITY_STONE.shadow, 1.1, 0.8)
    paint(ctx, lambda c: smooth_poly(c, [(-8, -100), (8, -100), (8, -124), (-8, -124)], tension=0.4), Pal('#2a2a3a', '#14141e', '#4a4a5e', '#06060a'), sh=1, hl=0)
    paint(ctx, lambda c: smooth_poly(c, [(-56, -150), (0, -236), (56, -150)], tension=0.0), ROOF_TEAL, sh=6, hl=2)
    roof_tiles(ctx, ((-4, -236), (4, -236), (56, -150), (-56, -150)), ROOF_TEAL, rows=5, cols=6)
    stroke(ctx, lambda c: (c.move_to(0, -236), c.line_to(0, -258)), hx('#3a2a20'), 2.2)
    paint(ctx, lambda c: smooth_poly(c, [(1, -258), (24, -252), (1, -244)], tension=0.2), CLOTH_B, sh=1.5, hl=0.8)


@prop('city_gate', 300, 240, 150, 220, col=None, shadow=(0, 0, 140, 12, 0.3))
def city_gate(ctx):
    for sx in (-1, 1):
        paint(ctx, lambda c, sx=sx: smooth_poly(c, [(sx * 140, 0), (sx * 140, -150), (sx * 70, -150), (sx * 70, 0)], tension=0.01), CITY_STONE, sh=6, hl=2)
        for row in range(8):
            y = -8 - row * 18
            for i in range(3):
                x = sx * (72 + i * 24 + (10 if row % 2 else 0))
                stroke(ctx, lambda c, x=x, y=y: (c.move_to(x, y), c.line_to(x, y - 18)), CITY_STONE.shadow, 1.1, 0.8)
    def arch(c):
        c.move_to(-146, -146)
        c.line_to(146, -146)
        c.line_to(146, -190)
        c.line_to(-146, -190)
        c.close_path()
    paint(ctx, arch, CITY_STONE, sh=4, hl=2)
    for i in range(8):
        x = -140 + i * 36
        paint(ctx, lambda c, x=x: smooth_poly(c, [(x, -190), (x, -206), (x + 22, -206), (x + 22, -190)], tension=0.02), CITY_STONE, sh=2, hl=1)
    paint(ctx, lambda c: smooth_poly(c, [(-34, -90), (-34, -150), (34, -150), (34, -90)], tension=0.02), CLOTH_R, sh=3, hl=1.2)
    paint(ctx, lambda c: smooth_poly(c, [(0, -130), (8, -116), (0, -100), (-8, -116)], tension=0.1), METAL, sh=1, hl=0.8, line=0.8)
    for sx in (-1, 1):
        paint(ctx, lambda c, sx=sx: smooth_poly(c, [(sx * 70, 0), (sx * 70, -140), (sx * 46, -140), (sx * 46, 0)], tension=0.02), Pal('#2a2a3a', '#14141e', '#4a4a5e', '#06060a'), sh=0, hl=0)


@prop('fountain', 180, 170, 90, 150, col=(130, 34, 0), shadow=(2, 0, 80, 18, 0.3))
def fountain(ctx):
    paint(ctx, lambda c: ellipse(c, 0, -14, 70, 28), CITY_STONE, sh=4, hl=2)
    paint(ctx, lambda c: ellipse(c, 0, -20, 58, 21), Pal('#6ac8e8', '#3a98c0', '#b0f0ff', '#0c3a50'), sh=3, hl=0, line=1)
    paint(ctx, lambda c: smooth_poly(c, [(-12, -20), (-9, -64), (9, -64), (12, -20)], tension=0.3), CITY_STONE, sh=2, hl=1)
    paint(ctx, lambda c: ellipse(c, 0, -66, 30, 11), CITY_STONE, sh=2, hl=1)
    paint(ctx, lambda c: ellipse(c, 0, -69, 24, 8), Pal('#6ac8e8', '#3a98c0', '#b0f0ff', '#0c3a50'), sh=2, hl=0, line=0.8)
    for dx in (-1, 0, 1):
        stroke(ctx, lambda c, dx=dx: (c.move_to(dx * 3, -70), c.curve_to(dx * 14, -110, dx * 26, -92, dx * 34, -66)), hx('#c8f4ff'), 2.2, 0.8)
    radial_glow(ctx, 0, -86, 26, hx('#b0f0ff'), 0.3)


@prop('house_c', 250, 310, 125, 274, col=(200, 66, 26), shadow=(6, 0, 112, 20, 0.35))
def house_c(ctx):
    W, H = 94, 116
    paint(ctx, lambda c: smooth_poly(c, [(-W, 0), (-W, -H), (W, -H), (W, 0)], tension=0.01), CITY_PLASTER, sh=0, hl=0)
    flat(ctx, lambda c: smooth_poly(c, [(-W, -H), (W, -H), (W, -H + 16), (-W, -H + 10)], tension=0.01), CITY_PLASTER.shadow, 0.9)
    paint(ctx, lambda c: smooth_poly(c, [(-W - 4, 2), (-W - 4, -20), (W + 4, -20), (W + 4, 2)], tension=0.02), CITY_STONE, sh=3, hl=1.2)
    for y in (-62,):
        paint(ctx, lambda c, y=y: smooth_poly(c, [(-W - 6, y), (W + 6, y), (W + 6, y + 8), (-W - 6, y + 8)], tension=0.01), WOOD_DK, sh=1.5, hl=0.6, line=0.9)
    door(ctx, 0, -2, 32, 54, pal=Pal('#3a8a8a', '#276a6a', '#62b4ae', '#0e2a2a'))
    for x in (-60, 60):
        window(ctx, x, -34, 22, 24, shutters=False, box=True, lit=True)
        window(ctx, x, -92, 22, 24, shutters=True, box=False)
    window(ctx, 0, -92, 22, 24, shutters=False, box=False)
    quad = ((-W - 6, -H - 98), (W + 6, -H - 98), (W + 22, -H + 6), (-W - 22, -H + 6))
    paint(ctx, lambda c: smooth_poly(c, list(quad), tension=0.0), ROOF_TEAL, sh=0, hl=0)
    roof_tiles(ctx, quad, ROOF_TEAL, rows=7, cols=11)
    stroke(ctx, lambda c: (c.move_to(-W - 22, -H + 6), c.line_to(W + 22, -H + 6)), ROOF_TEAL.line, 2)
    paint(ctx, lambda c: smooth_poly(c, [(-W - 10, -H - 104), (W + 10, -H - 104), (W + 6, -H - 94), (-W - 6, -H - 94)], tension=0.02),
          Pal('#276a6a', '#1c5050', '#3a8a8a', '#0a2020'), sh=1.5, hl=1)
    paint(ctx, lambda c: smooth_poly(c, [(40, -H - 82), (40, -H - 130), (62, -H - 130), (62, -H - 88)], tension=0.02), STONE, sh=3, hl=1.5)


@prop('cathedral', 440, 470, 220, 430, col=(380, 100, 30), shadow=(8, 0, 200, 30, 0.38))
def cathedral(ctx):
    W, H = 170, 180
    paint(ctx, lambda c: smooth_poly(c, [(-W, 0), (-W, -H), (W, -H), (W, 0)], tension=0.01), CITY_STONE, sh=0, hl=0)
    for row in range(11):
        y = -8 - row * 16
        for i in range(14):
            x = -W + (12 if row % 2 else 0) + i * 26
            stroke(ctx, lambda c, x=x, y=y: (c.move_to(x, y), c.line_to(x, y - 16)), CITY_STONE.shadow, 1.1, 0.7)
    flat(ctx, lambda c: smooth_poly(c, [(-W, -H), (W, -H), (W, -H + 18), (-W, -H + 12)], tension=0.01), CITY_STONE.shadow, 0.9)
    door(ctx, 0, -2, 64, 100, pal=Pal('#6a3a2a', '#4a2418', '#8e5a44', '#1e0c06'))
    for x in (-110, -60, 60, 110):
        paint(ctx, lambda c, x=x: smooth_poly(c, [(x - 11, -60), (x - 11, -118), (x, -136), (x + 11, -118), (x + 11, -60)], tension=0.02),
              Pal('#6a8ae0', '#3e58b0', '#a8c0ff', '#14204a'), sh=3, hl=0, line=1.2)
        stroke(ctx, lambda c, x=x: (c.move_to(x, -136), c.line_to(x, -60)), CITY_STONE.shadow, 2)
    paint(ctx, lambda c: ellipse(c, 0, -150, 26, 26), Pal('#ffd27a', '#e0a040', '#fff4c0', '#5a3a10'), sh=3, hl=1.5, line=1.4)
    for k in range(8):
        a = k / 8 * math.tau
        stroke(ctx, lambda c, a=a: (c.move_to(0, -150), c.line_to(math.cos(a) * 24, -150 + math.sin(a) * 24)), CITY_STONE.shadow, 1.4)
    for sx in (-1, 1):   # twin spires
        px = sx * 140
        paint(ctx, lambda c, px=px: smooth_poly(c, [(px - 36, -H + 10), (px - 36, -H - 110), (px + 36, -H - 110), (px + 36, -H + 10)], tension=0.01), CITY_STONE, sh=5, hl=2)
        paint(ctx, lambda c, px=px: smooth_poly(c, [(px - 44, -H - 108), (px, -H - 230), (px + 44, -H - 108)], tension=0.0), ROOF_TEAL, sh=5, hl=2)
        roof_tiles(ctx, ((px - 4, -H - 230), (px + 4, -H - 230), (px + 44, -H - 108), (px - 44, -H - 108)), ROOF_TEAL, rows=6, cols=6)
        paint(ctx, lambda c, px=px: smooth_poly(c, [(px - 9, -H - 60), (px - 9, -H - 92), (px, -H - 100), (px + 9, -H - 92), (px + 9, -H - 60)], tension=0.2),
              Pal('#2a2a3a', '#14141e', '#4a4a5e', '#06060a'), sh=1, hl=0)
        paint(ctx, lambda c, px=px: smooth_poly(c, [(px - 2, -H - 230), (px - 2, -H - 252), (px + 2, -H - 252), (px + 2, -H - 230)], tension=0.1), METAL, sh=0.6, hl=0.4, line=0.7)
    quad = ((-W + 20, -H - 70), (W - 20, -H - 70), (W + 14, -H + 6), (-W - 14, -H + 6))
    paint(ctx, lambda c: smooth_poly(c, list(quad), tension=0.0), ROOF_S, sh=0, hl=0)
    roof_tiles(ctx, quad, ROOF_S, rows=5, cols=14)
    paint(ctx, lambda c: smooth_poly(c, [(-60, -H - 70), (0, -H - 150), (60, -H - 70)], tension=0.0), CITY_STONE, sh=4, hl=1.5)
    paint(ctx, lambda c: ellipse(c, 0, -H - 94, 14, 14), Pal('#ffd27a', '#e0a040', '#fff4c0', '#5a3a10'), sh=2, hl=1, line=1.2)
    radial_glow(ctx, 0, -150, 40, hx('#ffd27a'), 0.18)


@prop('banner_pole', 50, 190, 25, 176, col=(12, 8, 0), shadow=(2, 0, 14, 5, 0.3))
def banner_pole(ctx):
    paint(ctx, lambda c: smooth_poly(c, [(-3, 0), (-3, -150), (3, -150), (3, 0)], tension=0.02), WOOD_DK, sh=1.2, hl=0.5)
    stroke(ctx, lambda c: (c.move_to(0, -148), c.line_to(18, -148)), WOOD_DK.base, 3)
    paint(ctx, lambda c: smooth_poly(c, [(2, -146), (22, -146), (22, -92), (12, -100), (2, -92)], tension=0.05), CLOTH_R, sh=3, hl=1.2)
    paint(ctx, lambda c: smooth_poly(c, [(12, -134), (17, -124), (12, -114), (7, -124)], tension=0.1), METAL, sh=0.8, hl=0.6, line=0.7)


# ------------------------------------------------------------------ render
def render_prop(name):
    p = PROPS[name]
    f = Frame(p['w'], p['h'], p['px'], p['py'])
    p['fn'](f.ctx)
    img = f.rgba()
    if p['outline']:
        img = outline_rgba(img, OUTLINE, p['outline'])
    if p['shadow']:
        cx, cy, rx, ry, al = p['shadow']
        sf = Frame(p['w'], p['h'], p['px'], p['py'])
        ellipse(sf.ctx, cx, cy, rx, ry)
        sf.ctx.set_source_rgba(0.12, 0.16, 0.10, 1)
        sf.ctx.fill()
        sh = sf.rgba()
        a = ndimage.gaussian_filter(sh[..., 3], sigma=6 * S) * al
        under = np.zeros_like(img)
        under[..., 0], under[..., 1], under[..., 2], under[..., 3] = 0.10, 0.14, 0.12, a
        fa = img[..., 3:4]
        res = np.empty_like(img)
        res[..., 3] = fa[..., 0] + under[..., 3] * (1 - fa[..., 0])
        safe = np.maximum(res[..., 3:4], 1e-6)
        res[..., :3] = (img[..., :3] * fa + under[..., :3] * under[..., 3:4] * (1 - fa)) / safe
        img = res
    return name, to_image(img)


def build_all():
    d = os.path.join(OUT, 'Env')
    os.makedirs(d, exist_ok=True)
    meta = []
    with ProcessPoolExecutor() as ex:
        for name, im in ex.map(render_prop, list(PROPS)):
            im.save(os.path.join(d, name + '.png'), optimize=True)
            p = PROPS[name]
            col = p['col']
            meta.append(dict(name=name, w=p['w'], h=p['h'], pivotX=p['px'], pivotY=p['h'] - p['py'],
                             colW=col[0] if col else 0, colH=col[1] if col else 0, colY=col[2] if col else 0))
    with open(os.path.join(d, 'props.json'), 'w') as fp:
        json.dump(dict(props=meta), fp, indent=1)
    print('props:', len(meta))


if __name__ == '__main__':
    build_all()
