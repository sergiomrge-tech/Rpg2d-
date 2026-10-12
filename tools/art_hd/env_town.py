"""Town props for the circular capital: tavern, smithy, stable, apothecary, armory, bakery, barracks, library,
four more house types and street furniture. Registered into env_objects.PROPS (imported at the end of env_objects)."""
from __future__ import annotations
import math
import random
from core import Pal, paint, flat, stroke, ellipse, smooth_poly, hx, radial_glow
from env_objects import (prop, roof_tiles, window, door, blob, WOOD, WOOD_DK, STONE, PLASTER, ROOF_O, ROOF_B, ROOF_S, GLASS, METAL,
                         CLOTH_R, CLOTH_B, LEAF, BARK)

ROOF_BRN = Pal('#9a5a3a', '#744028', '#c07c52', '#3a1e10')
ROOF_GRN = Pal('#4f9a6a', '#3a7850', '#7cc896', '#16301f')
ROOF_VIO = Pal('#7a58b0', '#5a3f8a', '#a07ee0', '#261a46')
ROOF_RED = Pal('#c24a3a', '#962f2a', '#e87a62', '#4a1410')
ROOF_THATCH = Pal('#d8b45a', '#b08a38', '#f2d27c', '#5a4318')
PLASTER_Y = Pal('#f6df9c', '#dcc07a', '#fff2c0', '#6b5530')
PLASTER_G = Pal('#d4e6c6', '#b2cda0', '#eefae0', '#3f5a38')
PLASTER_P = Pal('#f4d2cc', '#d8aaa4', '#ffeae4', '#6a4440')
PLASTER_W = Pal('#f3e3c6', '#d8c19e', '#fff6e2', '#6b5038')
STONE_DK = Pal('#8c8a9c', '#6a687c', '#b4b2c4', '#2a2836')
PLANK_RED = Pal('#b8493a', '#8f332c', '#dc7058', '#3e1210')
IRON = Pal('#5a5a6e', '#3e3e52', '#8a8aa2', '#14141e')
TEAL = Pal('#3a8a8a', '#276a6a', '#62b4ae', '#0e2a2a')
GOLD = METAL


def poly(pts, t=0.01):
    return lambda c: smooth_poly(c, list(pts), tension=t)


def wall(ctx, W, H, pal, shade_h=16):
    paint(ctx, poly([(-W, 0), (-W, -H), (W, -H), (W, 0)]), pal, sh=0, hl=0)
    flat(ctx, poly([(-W, -H), (W, -H), (W, -H + shade_h), (-W, -H + shade_h - 6)]), pal.shadow, 0.9)


def base_stones(ctx, W, h=18, pal=STONE):
    paint(ctx, poly([(-W - 4, 2), (-W - 4, -h), (W + 4, -h), (W + 4, 2)], 0.02), pal, sh=3, hl=1.2)
    for i in range(int(W / 9)):
        x = -W + 6 + i * 19
        stroke(ctx, lambda c, x=x: (c.move_to(x, -h + 2), c.line_to(x, 0)), pal.shadow, 1.2)


def timber(ctx, W, H, xs=(), bands=(), z=4):
    for x in xs:
        paint(ctx, poly([(x - z, -16), (x - z, -H), (x + z, -H), (x + z, -16)]), WOOD_DK, sh=1.5, hl=0.6, line=0.9)
    for y in bands:
        paint(ctx, poly([(-W, y), (W, y), (W, y + 8), (-W, y + 8)]), WOOD_DK, sh=1.5, hl=0.6, line=0.9)


def roof(ctx, W, H, rise, pal, ridge, over=22, rows=7, cols=11):
    quad = ((-W - 6, -H - rise), (W + 6, -H - rise), (W + over, -H + 6), (-W - over, -H + 6))
    paint(ctx, poly(quad, 0.0), pal, sh=0, hl=0)
    roof_tiles(ctx, quad, pal, rows=rows, cols=cols)
    stroke(ctx, lambda c: (c.move_to(-W - over, -H + 6), c.line_to(W + over, -H + 6)), pal.line, 2)
    paint(ctx, poly([(-W - 10, -H - rise - 6), (W + 10, -H - rise - 6), (W + 6, -H - rise + 4), (-W - 6, -H - rise + 4)], 0.02),
          ridge, sh=1.5, hl=1)


def chimney(ctx, x, H, rise, w=24, top=40):
    y0 = -H - rise * 0.55
    paint(ctx, poly([(x - w / 2, y0), (x - w / 2, y0 - top), (x + w / 2, y0 - top), (x + w / 2, y0 + 6)], 0.02), STONE, sh=3, hl=1.5)
    paint(ctx, poly([(x - w / 2 - 3, y0 - top), (x + w / 2 + 3, y0 - top), (x + w / 2 + 3, y0 - top - 8), (x - w / 2 - 3, y0 - top - 8)], 0.02),
          Pal('#8a8898', '#6a687a', '#b0aec0', '#2a2836'), sh=1.5, hl=1)


def hanging_sign(ctx, x, y, icon, arm=34, w=34, h=30, pal=WOOD):
    stroke(ctx, lambda c: (c.move_to(x - arm, y - 6), c.line_to(x + 2, y - 6)), IRON.base, 4)
    for dx in (-w / 2 + 6, w / 2 - 6):
        stroke(ctx, lambda c, dx=dx: (c.move_to(x - arm / 2 + dx, y - 6), c.line_to(x - arm / 2 + dx, y + 4)), IRON.shadow, 1.4)
    paint(ctx, poly([(x - arm / 2 - w / 2, y + 2), (x - arm / 2 + w / 2, y + 2), (x - arm / 2 + w / 2, y + h), (x - arm / 2 - w / 2, y + h)], 0.04),
          pal, sh=2, hl=1)
    ctx.save()
    ctx.translate(x - arm / 2, y + h / 2 + 2)
    icon(ctx)
    ctx.restore()


def awning(ctx, x0, x1, y, depth=26, stripe=CLOTH_R, n=6):
    def shape(c):
        c.move_to(x0, y)
        c.line_to(x0 + 8, y - depth)
        c.line_to(x1 - 8, y - depth)
        c.line_to(x1, y)
        step = (x1 - x0) / n
        for i in range(n):
            xs = x1 - i * step
            c.curve_to(xs - step * 0.2, y + 10, xs - step * 0.8, y + 10, xs - step, y)
        c.close_path()
    paint(ctx, shape, Pal('#fff2dc', '#e6d2b0', '#ffffff', '#6a4630'), sh=3, hl=1.2)
    ctx.save()
    ctx.new_path()
    shape(ctx)
    ctx.clip()
    step = (x1 - x0) / n
    for i in range(n):
        if i % 2 == 0:
            xa = x0 + i * step
            flat(ctx, lambda c, xa=xa: (c.move_to(xa, y + 12), c.line_to(xa + 2, y - depth), c.line_to(xa + step + 2, y - depth),
                                        c.line_to(xa + step, y + 12), c.close_path()), stripe.base)
    ctx.restore()


def glow_win(ctx, x, y, w=22, h=26, **kw):
    window(ctx, x, y, w, h, lit=True, **kw)
    radial_glow(ctx, x, y - h / 2, w * 1.2, hx('#ffd27a'), 0.18)


# ------------------------------------------------------------------ icons for signs
def icon_mug(c):
    paint(c, poly([(-9, -9), (7, -9), (6, 10), (-8, 10)], 0.05), Pal('#e8c35a', '#b98a2c', '#fff0a8', '#5e4313'), sh=1.5, hl=0.8)
    flat(c, poly([(-9, -10), (7, -10), (7, -6), (-9, -6)], 0.05), hx('#fff6e6'))
    stroke(c, lambda cc: (cc.move_to(7, -4), cc.curve_to(15, -4, 15, 6, 6, 6)), GOLD.shadow, 2.4)


def icon_horseshoe(c):
    stroke(c, lambda cc: (cc.move_to(-9, 9), cc.curve_to(-14, -12, 14, -12, 9, 9)), IRON.light, 4.5)
    stroke(c, lambda cc: (cc.move_to(-9, 9), cc.curve_to(-14, -12, 14, -12, 9, 9)), IRON.base, 2.4)


def icon_bottle(c):
    paint(c, poly([(-7, 10), (-9, -2), (-3, -6), (-3, -11), (3, -11), (3, -6), (9, -2), (7, 10)], 0.08),
          Pal('#6fd08a', '#3fa062', '#b8f4c8', '#14442a'), sh=1.5, hl=0.9)
    flat(c, poly([(-7, 4), (7, 4), (6, 10), (-6, 10)], 0.05), hx('#d6453d'))


def icon_swords(c):
    for s in (-1, 1):
        stroke(c, lambda cc, s=s: (cc.move_to(-10 * s, 10), cc.line_to(10 * s, -10)), IRON.light, 4)
        stroke(c, lambda cc, s=s: (cc.move_to(-10 * s, 10), cc.line_to(10 * s, -10)), IRON.base, 2)
    flat(c, lambda cc: ellipse(cc, 0, 0, 3, 3), GOLD.base)


def icon_bread(c):
    paint(c, lambda cc: ellipse(cc, 0, 2, 12, 7), Pal('#e0a04a', '#b87a2a', '#f8c878', '#5a3510'), sh=1.5, hl=0.9)
    for x in (-5, 0, 5):
        stroke(c, lambda cc, x=x: (cc.move_to(x - 2, -1), cc.line_to(x + 2, 5)), hx('#b87a2a'), 1.6)


# ------------------------------------------------------------------ buildings
@prop('tavern', 380, 360, 190, 320, col=(240, 70, 26), shadow=(6, 0, 160, 26, 0.35))
def tavern(ctx):
    W, H = 118, 108
    wall(ctx, W, H, PLASTER_Y)
    timber(ctx, W, H, xs=(-W + 4, -60, 0, 60, W - 4), bands=(-62,))
    base_stones(ctx, W, 20)
    # double door under a porch roof
    door(ctx, 0, -2, 46, 58, pal=Pal('#7a3a2a', '#5a2a1e', '#a05a42', '#2a120c'))
    for x in (-34, 34):
        paint(ctx, poly([(x - 4, 0), (x - 4, -64), (x + 4, -64), (x + 4, 0)], 0.02), WOOD_DK, sh=1.5, hl=0.6)
    awning(ctx, -52, 52, -64, 24, CLOTH_R, 6)
    for x in (-84, 80):
        glow_win(ctx, x, -40, 26, 28, shutters=True, box=True)
    for x in (-84, -30, 30, 84):
        glow_win(ctx, x, -92, 22, 24, shutters=(x in (-84, 84)), box=False)
    roof(ctx, W, H, 100, ROOF_BRN, Pal('#744028', '#5a3020', '#9a5a3a', '#2a140c'), over=26, rows=7, cols=13)
    chimney(ctx, -80, H, 100, 26, 44)
    # dormers
    for dx in (-44, 44):
        paint(ctx, poly([(dx - 24, -H - 28), (dx - 24, -H - 60), (dx, -H - 78), (dx + 24, -H - 60), (dx + 24, -H - 28)], 0.02), PLASTER_Y, sh=2, hl=1)
        glow_win(ctx, dx, -H - 36, 18, 20, shutters=False, box=False)
        paint(ctx, poly([(dx - 32, -H - 56), (dx, -H - 86), (dx + 32, -H - 56), (dx + 26, -H - 52), (dx, -H - 76), (dx - 26, -H - 52)], 0.02), ROOF_BRN, sh=2, hl=1.2)
    hanging_sign(ctx, 118, -86, icon_mug, arm=46, w=40, h=34)
    # barrels by the door
    for x, y in ((-104, 2), (-90, 6)):
        paint(ctx, lambda c, x=x, y=y: ellipse(c, x, y - 12, 12, 16), WOOD, sh=2.5, hl=1)
        stroke(ctx, lambda c, x=x, y=y: (c.move_to(x - 12, y - 18), c.line_to(x + 12, y - 18)), IRON.base, 1.6)


@prop('smithy', 320, 330, 160, 292, col=(210, 70, 26), shadow=(6, 0, 140, 24, 0.35))
def smithy(ctx):
    W, H = 100, 92
    wall(ctx, W, H, Pal('#bcbac8', '#8f8da2', '#e0deea', '#3b3848'))
    for row in range(5):
        y = -8 - row * 17
        for i in range(8):
            x = -W + (12 if row % 2 else 0) + i * 26
            if -W < x < W:
                stroke(ctx, lambda c, x=x, y=y: (c.move_to(x, y), c.line_to(x, y - 15)), STONE_DK.shadow, 1.1, 0.8)
        stroke(ctx, lambda c, y=y: (c.move_to(-W, y - 16), c.line_to(W, y - 16)), STONE_DK.shadow, 1.0, 0.6)
    base_stones(ctx, W, 14, STONE_DK)
    door(ctx, -38, -1, 32, 50, pal=Pal('#4a3a30', '#322620', '#6a5444', '#18100c'))
    window(ctx, -38, -76, 20, 20, shutters=True, box=False)
    # open forge bay (right)
    paint(ctx, poly([(18, 0), (18, -62), (86, -62), (86, 0)], 0.02), Pal('#2a1c18', '#1a100e', '#3a2822', '#0a0605'), sh=0, hl=0)
    radial_glow(ctx, 54, -26, 54, hx('#ff8a30'), 0.7)
    flat(ctx, lambda c: ellipse(c, 54, -14, 26, 12), hx('#ff6a1c'), 0.9)
    flat(ctx, lambda c: ellipse(c, 54, -16, 16, 6), hx('#ffd27a'), 0.9)
    for x in (14, 90):
        paint(ctx, poly([(x - 5, 2), (x - 5, -66), (x + 5, -66), (x + 5, 2)], 0.02), WOOD_DK, sh=2, hl=1)
    paint(ctx, poly([(10, -62), (94, -62), (100, -52), (4, -52)], 0.03), WOOD, sh=2, hl=1)
    # anvil
    paint(ctx, poly([(-22, 8), (-14, -4), (14, -4), (22, 8)], 0.05), IRON, sh=2, hl=1)
    paint(ctx, poly([(-26, -4), (-26, -14), (20, -14), (30, -8), (14, -4)], 0.05), IRON, sh=2, hl=1.2)
    roof(ctx, W, H, 78, ROOF_S, Pal('#454a66', '#33375a', '#6a708e', '#14162a'), over=22, rows=6, cols=10)
    # big stone chimney with glow
    paint(ctx, poly([(46, -H - 42), (46, -H - 128), (88, -H - 128), (88, -H - 50)], 0.02), STONE_DK, sh=3, hl=1.5)
    paint(ctx, poly([(42, -H - 128), (92, -H - 128), (92, -H - 138), (42, -H - 138)], 0.02), IRON, sh=1.5, hl=1)
    radial_glow(ctx, 67, -H - 132, 22, hx('#ff9a40'), 0.5)
    hanging_sign(ctx, -100, -84, icon_horseshoe, arm=-32, w=32, h=30) if False else hanging_sign(ctx, 112, -78, icon_horseshoe, arm=40, w=34, h=32, pal=WOOD_DK)


@prop('stable', 400, 300, 200, 262, col=(280, 66, 24), shadow=(6, 0, 170, 22, 0.35))
def stable(ctx):
    W, H = 130, 72
    wall(ctx, W, H, PLANK_RED, 14)
    for i in range(0, 2 * W, 14):
        stroke(ctx, lambda c, i=i: (c.move_to(-W + i, 0), c.line_to(-W + i, -H)), PLANK_RED.shadow, 1.2, 0.7)
    base_stones(ctx, W, 12, STONE)
    # white trim posts
    for x in (-W + 6, -52, 52, W - 6):
        paint(ctx, poly([(x - 4, 0), (x - 4, -H), (x + 4, -H), (x + 4, 0)]), Pal('#f4ecd8', '#d8ccb0', '#ffffff', '#6a5a40'), sh=1.2, hl=0.6)
    # double barn doors with X braces
    paint(ctx, poly([(-34, 0), (-34, -62), (34, -62), (34, 0)], 0.02), WOOD_DK, sh=3, hl=1)
    stroke(ctx, lambda c: (c.move_to(0, 0), c.line_to(0, -62)), WOOD_DK.deep, 2)
    for s in (-1, 1):
        stroke(ctx, lambda c, s=s: (c.move_to(s * 3, -4), c.line_to(s * 31, -58), c.move_to(s * 31, -4), c.line_to(s * 3, -58)),
               Pal('#f4ecd8', '#d8ccb0', '#ffffff', '#6a5a40').base, 3)
    # side half-door windows
    for x in (-92, 92):
        paint(ctx, poly([(x - 16, -2), (x - 16, -50), (x + 16, -50), (x + 16, -2)], 0.02), WOOD_DK, sh=2, hl=1)
        flat(ctx, poly([(x - 12, -30), (x + 12, -30), (x + 12, -6), (x - 12, -6)]), hx('#2a1c14'))
    roof(ctx, W, H, 84, ROOF_BRN, Pal('#744028', '#5a3020', '#9a5a3a', '#2a140c'), over=28, rows=7, cols=14)
    # hay loft hatch
    paint(ctx, poly([(-26, -H - 24), (-26, -H - 58), (26, -H - 58), (26, -H - 24)], 0.02), WOOD_DK, sh=2, hl=1)
    flat(ctx, poly([(-20, -H - 30), (20, -H - 30), (20, -H - 52), (-20, -H - 52)]), hx('#d8b45a'))
    for k in range(-2, 3):
        stroke(ctx, lambda c, k=k: (c.move_to(k * 8, -H - 32), c.line_to(k * 8 + 3, -H - 50)), hx('#b08a38'), 1.4)
    paint(ctx, poly([(-34, -H - 54), (0, -H - 80), (34, -H - 54), (30, -H - 50), (0, -H - 72), (-30, -H - 50)], 0.02), ROOF_BRN, sh=2, hl=1.2)
    # weathervane
    stroke(ctx, lambda c: (c.move_to(0, -H - 84), c.line_to(0, -H - 112)), IRON.base, 3)
    paint(ctx, poly([(-14, -H - 104), (14, -H - 110), (14, -H - 98), (-14, -H - 100)], 0.05), GOLD, sh=1, hl=0.6)


@prop('apothecary', 280, 330, 140, 292, col=(170, 64, 26), shadow=(6, 0, 118, 22, 0.35))
def apothecary(ctx):
    W, H = 84, 100
    wall(ctx, W, H, PLASTER_G)
    timber(ctx, W, H, xs=(-W + 4, W - 4), bands=(-58,))
    base_stones(ctx, W, 16)
    door(ctx, 0, -2, 32, 52, pal=TEAL)
    window(ctx, -52, -34, 24, 26, shutters=True, box=True)
    window(ctx, 52, -34, 24, 26, shutters=True, box=True)
    # round upper window
    paint(ctx, lambda c: ellipse(c, 0, -80, 18, 18), WOOD_DK, sh=1, hl=0.5)
    paint(ctx, lambda c: ellipse(c, 0, -80, 14, 14), GLASS, sh=2, hl=0, line=0.6)
    stroke(ctx, lambda c: (c.move_to(-14, -80), c.line_to(14, -80), c.move_to(0, -94), c.line_to(0, -66)), WOOD_DK.base, 2)
    roof(ctx, W, H, 92, ROOF_GRN, Pal('#3a7850', '#2c5e3e', '#5ea878', '#10281a'), over=22, rows=6, cols=9)
    chimney(ctx, 52, H, 92, 22, 40)
    # herb bundles hanging under the eave
    rnd = random.Random(4)
    for i in range(6):
        x = -60 + i * 24
        stroke(ctx, lambda c, x=x: (c.move_to(x, -H + 2), c.line_to(x, -H + 14)), WOOD_DK.base, 1.4)
        flat(ctx, lambda c, x=x: blob(c, [(x, -H + 20, 6), (x - 3, -H + 26, 4), (x + 3, -H + 26, 4)]), rnd.choice([LEAF.base, hx('#8ccf4a'), hx('#b078d8')]))
    hanging_sign(ctx, 84, -86, icon_bottle, arm=34, w=30, h=34)
    # potion bottles on a crate
    paint(ctx, poly([(-100, 2), (-100, -18), (-72, -18), (-72, 2)], 0.02), WOOD, sh=2, hl=1)
    for x, col in ((-94, '#d6453d'), (-86, '#4a8fe0'), (-78, '#6fd08a')):
        paint(ctx, lambda c, x=x: ellipse(c, x, -26, 4.5, 6), Pal(col, shade_c(col), '#ffffff', '#222222'), sh=1, hl=0.6, line=0.7)


def shade_c(h):
    from core import shade
    return shade(hx(h), -0.12, 0.05)


@prop('armory', 300, 330, 150, 292, col=(190, 66, 26), shadow=(6, 0, 128, 22, 0.35))
def armory(ctx):
    W, H = 92, 98
    wall(ctx, W, H, Pal('#d4d2de', '#aaa8bc', '#f0eef8', '#44425a'))
    for row in range(5):
        y = -8 - row * 18
        stroke(ctx, lambda c, y=y: (c.move_to(-W, y - 17), c.line_to(W, y - 17)), STONE_DK.shadow, 1.0, 0.6)
        for i in range(7):
            x = -W + (14 if row % 2 else 0) + i * 28
            if -W < x < W:
                stroke(ctx, lambda c, x=x, y=y: (c.move_to(x, y), c.line_to(x, y - 16)), STONE_DK.shadow, 1.0, 0.7)
    base_stones(ctx, W, 14, STONE_DK)
    door(ctx, 0, -2, 36, 54, pal=Pal('#3a4a7a', '#2a3860', '#5a6aa0', '#10182a'))
    window(ctx, -58, -40, 24, 28, shutters=False, box=False)
    window(ctx, 58, -40, 24, 28, shutters=False, box=False)
    # crest above the door
    paint(ctx, poly([(-18, -66), (18, -66), (18, -88), (0, -100), (-18, -88)], 0.05), CLOTH_B, sh=2, hl=1)
    ctx.save()
    ctx.translate(0, -82)
    ctx.scale(0.9, 0.9)
    icon_swords(ctx)
    ctx.restore()
    roof(ctx, W, H, 84, ROOF_B, Pal('#3a5b94', '#2c4678', '#5a80c0', '#142040'), over=22, rows=6, cols=9)
    for x in (-W - 4, W + 4):          # banners
        stroke(ctx, lambda c, x=x: (c.move_to(x, -H - 40), c.line_to(x, -H + 10)), WOOD_DK.base, 3)
        paint(ctx, poly([(x - 9, -H - 36), (x + 9, -H - 36), (x + 9, -H + 4), (x, -H - 6), (x - 9, -H + 4)], 0.03), CLOTH_R, sh=1.5, hl=0.8)
    # weapon rack outside
    paint(ctx, poly([(66, 6), (66, -34), (104, -34), (104, 6)], 0.02), WOOD_DK, sh=1.5, hl=0.6)
    for i, x in enumerate((72, 82, 92, 100)):
        stroke(ctx, lambda c, x=x: (c.move_to(x, -30), c.line_to(x - 2, -64)), IRON.light, 3)
        flat(ctx, lambda c, x=x: ellipse(c, x - 2, -66, 3, 4), GOLD.base)


@prop('bakery', 270, 320, 135, 282, col=(170, 64, 26), shadow=(6, 0, 116, 22, 0.35))
def bakery(ctx):
    W, H = 84, 96
    wall(ctx, W, H, PLASTER_P)
    timber(ctx, W, H, xs=(-W + 4, W - 4), bands=(-56,))
    base_stones(ctx, W, 14)
    door(ctx, 40, -2, 30, 50, pal=Pal('#c24a3a', '#962f2a', '#e87a62', '#4a1410'))
    # shop window with bread
    paint(ctx, poly([(-64, -22), (-64, -62), (14, -62), (14, -22)], 0.02), WOOD_DK, sh=1.5, hl=0.6)
    paint(ctx, poly([(-60, -26), (-60, -58), (10, -58), (10, -26)], 0.02), GLASS, sh=3, hl=0, line=0.8)
    for x in (-48, -28, -8):
        paint(ctx, lambda c, x=x: ellipse(c, x, -33, 9, 5), Pal('#e0a04a', '#b87a2a', '#f8c878', '#5a3510'), sh=1, hl=0.7, line=0.7)
    awning(ctx, -74, 24, -64, 26, Pal('#e0703f', '#b9502f', '#ff9b62', '#5a2014'), 6)
    window(ctx, 40, -86, 20, 20, shutters=True, box=True, lit=True)
    roof(ctx, W, H, 88, ROOF_O, Pal('#c9583a', '#a1402a', '#e87a50', '#4a1810'), over=22, rows=6, cols=9)
    chimney(ctx, -48, H, 88, 24, 46)
    hanging_sign(ctx, 84, -80, icon_bread, arm=36, w=34, h=30)


@prop('barracks', 400, 330, 200, 292, col=(260, 70, 26), shadow=(6, 0, 170, 24, 0.36))
def barracks(ctx):
    W, H = 124, 100
    wall(ctx, W, H, Pal('#c8c6d4', '#9a98b0', '#e8e6f2', '#3b3a50'))
    for row in range(5):
        y = -8 - row * 19
        stroke(ctx, lambda c, y=y: (c.move_to(-W, y - 18), c.line_to(W, y - 18)), STONE_DK.shadow, 1.0, 0.6)
        for i in range(10):
            x = -W + (15 if row % 2 else 0) + i * 30
            if -W < x < W:
                stroke(ctx, lambda c, x=x, y=y: (c.move_to(x, y), c.line_to(x, y - 17)), STONE_DK.shadow, 1.0, 0.7)
    base_stones(ctx, W, 14, STONE_DK)
    door(ctx, 0, -2, 44, 62, pal=Pal('#4a3a30', '#322620', '#6a5444', '#18100c'))
    for x in (-80, 80):
        paint(ctx, poly([(x - 10, -50), (x - 10, -78), (x + 10, -78), (x + 10, -50)], 0.02), STONE_DK, sh=2, hl=1)
        flat(ctx, poly([(x - 5, -56), (x + 5, -56), (x + 5, -74), (x - 5, -74)]), hx('#10101a'))
    # crenellated parapet instead of a roof
    paint(ctx, poly([(-W - 10, -H - 6), (W + 10, -H - 6), (W + 10, -H - 34), (-W - 10, -H - 34)], 0.01), Pal('#b0aec0', '#8a889e', '#d8d6e6', '#32304a'), sh=3, hl=1.4)
    for i in range(-5, 6):
        x = i * 24
        paint(ctx, poly([(x - 8, -H - 34), (x + 8, -H - 34), (x + 8, -H - 50), (x - 8, -H - 50)], 0.01), Pal('#b0aec0', '#8a889e', '#d8d6e6', '#32304a'), sh=2, hl=1)
    # towers' flagpoles + big banner above the door
    for x in (-W + 10, W - 10):
        stroke(ctx, lambda c, x=x: (c.move_to(x, -H - 50), c.line_to(x, -H - 120)), WOOD_DK.base, 4)
        paint(ctx, poly([(x, -H - 118), (x + 34, -H - 108), (x, -H - 96)], 0.03), CLOTH_R, sh=1.5, hl=0.8)
    paint(ctx, poly([(-16, -H - 28), (16, -H - 28), (16, -H - 4), (0, -H + 8), (-16, -H - 4)], 0.03), CLOTH_R, sh=1.5, hl=0.8)
    flat(ctx, lambda c: ellipse(c, 0, -H - 14, 5, 5), GOLD.base)


@prop('library', 260, 420, 130, 380, col=(160, 60, 26), shadow=(6, 0, 110, 22, 0.35))
def library(ctx):
    """Mage library: tall tower with a violet cone roof and a glowing star window."""
    W, H = 76, 160
    wall(ctx, W, H, Pal('#d8d0ea', '#b4a8d0', '#f2ecfc', '#4a3f66'), 18)
    base_stones(ctx, W, 18)
    door(ctx, 0, -2, 36, 56, pal=Pal('#5a3f8a', '#3f2a68', '#7e5eb0', '#1a1030'))
    for y in (-72, -118):
        window(ctx, 0, y, 22, 28, shutters=False, box=False, lit=True)
    radial_glow(ctx, 0, -118, 40, hx('#b898ff'), 0.35)
    for x in (-50, 50):
        window(ctx, x, -92, 16, 22, shutters=False, box=False, lit=True)
    # star crest
    flat(ctx, lambda c: [c.move_to(0 + 12 * math.cos(math.radians(a)) * (1 if i % 2 == 0 else 0.45),
                                   -146 + 12 * math.sin(math.radians(a)) * (1 if i % 2 == 0 else 0.45)) if i == 0 else
                         c.line_to(12 * math.cos(math.radians(a)) * (1 if i % 2 == 0 else 0.45), -146 + 12 * math.sin(math.radians(a)) * (1 if i % 2 == 0 else 0.45))
                         for i, a in enumerate(range(-90, 270, 36))] and c.close_path(), GOLD.base)
    # cone roof
    paint(ctx, poly([(-W - 14, -H + 8), (0, -H - 150), (W + 14, -H + 8)], 0.0), ROOF_VIO, sh=3, hl=1.5)
    for k in range(1, 6):
        t = k / 6
        y = -H + 8 - t * 150
        w = (W + 14) * (1 - t)
        stroke(ctx, lambda c, y=y, w=w: (c.move_to(-w, y), c.curve_to(-w / 2, y + 8, w / 2, y + 8, w, y)), ROOF_VIO.shadow, 1.6)
    flat(ctx, lambda c: ellipse(c, 0, -H - 156, 6, 6), GOLD.base)


# ------------------------------------------------------------------ house variants
@prop('house_d', 200, 360, 100, 322, col=(124, 60, 26), shadow=(4, 0, 90, 18, 0.35))
def house_d(ctx):
    """Tall narrow townhouse (3 storeys, green roof)."""
    W, H = 60, 170
    wall(ctx, W, H, PLASTER_W, 18)
    timber(ctx, W, H, xs=(-W + 4, W - 4), bands=(-70, -118))
    base_stones(ctx, W, 18)
    door(ctx, 0, -2, 30, 50)
    for y in (-92, -144):
        for x in (-30, 30):
            window(ctx, x, y + 10, 20, 24, shutters=True, box=(y == -92))
    window(ctx, -30, -34, 18, 20, shutters=False, box=False)
    window(ctx, 30, -34, 18, 20, shutters=False, box=False, lit=True)
    roof(ctx, W, H, 70, ROOF_GRN, Pal('#3a7850', '#2c5e3e', '#5ea878', '#10281a'), over=18, rows=5, cols=8)
    chimney(ctx, -30, H, 70, 20, 36)


@prop('house_e', 340, 300, 170, 262, col=(260, 66, 26), shadow=(6, 0, 150, 22, 0.35))
def house_e(ctx):
    """Long row house with two doors, yellow plaster and a red roof."""
    W, H = 130, 88
    wall(ctx, W, H, PLASTER_Y, 14)
    timber(ctx, W, H, xs=(-W + 4, 0, W - 4), bands=(-54,))
    base_stones(ctx, W, 16)
    door(ctx, -64, -2, 28, 46, pal=Pal('#3d6fc2', '#2c5196', '#6b9be6', '#142650'))
    door(ctx, 64, -2, 28, 46, pal=Pal('#3a8a8a', '#276a6a', '#62b4ae', '#0e2a2a'))
    for x in (-98, -30, 30, 98):
        window(ctx, x, -34, 20, 22, shutters=True, box=(x in (-98, 98)), lit=(x == 30))
    for x in (-98, -30, 30, 98):
        window(ctx, x, -78, 18, 18, shutters=False, box=False)
    roof(ctx, W, H, 74, ROOF_RED, Pal('#962f2a', '#7a2422', '#c24a3a', '#3a0e0c'), over=24, rows=6, cols=13)
    chimney(ctx, -80, H, 74, 22, 36)
    chimney(ctx, 70, H, 74, 22, 36)


@prop('house_f', 260, 350, 130, 312, col=(200, 66, 26), shadow=(6, 0, 118, 22, 0.35))
def house_f(ctx):
    """Half-timbered house with a purple-roofed corner turret."""
    W, H = 80, 100
    wall(ctx, W, H, PLASTER_W, 16)
    timber(ctx, W, H, xs=(-W + 4, -26, 26, W - 4), bands=(-60,))
    for sx in (-1, 1):
        stroke(ctx, lambda c, sx=sx: (c.move_to(sx * 26, -16), c.line_to(sx * 66, -58)), WOOD_DK.base, 4)
    base_stones(ctx, W, 16)
    door(ctx, -10, -2, 30, 50)
    window(ctx, 40, -36, 24, 26, shutters=True, box=True, lit=True)
    window(ctx, -50, -84, 20, 22, shutters=True, box=False)
    roof(ctx, W, H, 84, ROOF_VIO, Pal('#5a3f8a', '#432e6e', '#7a58b0', '#1e1236'), over=20, rows=6, cols=9)
    # turret
    paint(ctx, poly([(52, -H - 4), (52, -H - 96), (96, -H - 96), (96, -H - 4)], 0.02), PLASTER_W, sh=2.5, hl=1)
    window(ctx, 74, -H - 40, 16, 20, shutters=False, box=False, lit=True)
    paint(ctx, poly([(46, -H - 92), (74, -H - 150), (102, -H - 92)], 0.0), ROOF_VIO, sh=3, hl=1.4)
    flat(ctx, lambda c: ellipse(c, 74, -H - 152, 4, 4), GOLD.base)


@prop('house_g', 190, 230, 95, 192, col=(118, 56, 22), shadow=(4, 0, 86, 16, 0.35))
def house_g(ctx):
    """Small cottage with a thatched roof."""
    W, H = 58, 62
    wall(ctx, W, H, PLASTER_W, 12)
    base_stones(ctx, W, 14)
    timber(ctx, W, H, xs=(-W + 4, W - 4), bands=())
    door(ctx, -12, -2, 26, 42, pal=Pal('#8a5a3c', '#66402b', '#b07a52', '#2e1a10'))
    window(ctx, 30, -34, 18, 20, shutters=True, box=True)
    roof(ctx, W, H, 66, ROOF_THATCH, Pal('#b08a38', '#8a6a24', '#d8b45a', '#4a3410'), over=20, rows=5, cols=8)
    chimney(ctx, -32, H, 66, 18, 30)


# ------------------------------------------------------------------ street furniture
@prop('hay_bale', 70, 60, 35, 52, col=(46, 22, 0), shadow=(2, 0, 30, 8, 0.3))
def hay_bale(ctx):
    paint(ctx, poly([(-26, 0), (-28, -22), (26, -22), (28, 0)], 0.1), Pal('#e0c068', '#b89a40', '#f8e090', '#5a4818'), sh=2.5, hl=1)
    for x in (-14, 14):
        stroke(ctx, lambda c, x=x: (c.move_to(x, 0), c.line_to(x, -22)), hx('#7a5a24'), 1.6)
    for i in range(6):
        stroke(ctx, lambda c, i=i: (c.move_to(-22 + i * 8, -4), c.line_to(-19 + i * 8, -17)), hx('#f8e090'), 1.2, 0.8)


@prop('trough', 120, 70, 60, 58, col=(90, 20, 0), shadow=(2, 0, 50, 9, 0.3))
def trough(ctx):
    paint(ctx, poly([(-46, 0), (-50, -24), (50, -24), (46, 0)], 0.04), WOOD, sh=3, hl=1.2)
    flat(ctx, poly([(-46, -22), (46, -22), (44, -14), (-44, -14)], 0.04), hx('#6fb0d6'), 0.95)
    for x in (-40, 40):
        paint(ctx, poly([(x - 4, 2), (x - 4, -14), (x + 4, -14), (x + 4, 2)], 0.02), WOOD_DK, sh=1, hl=0.5)


@prop('hay_cart', 200, 150, 100, 130, col=(130, 36, 0), shadow=(4, 0, 84, 14, 0.32))
def hay_cart(ctx):
    for x in (-52, 52):
        paint(ctx, lambda c, x=x: ellipse(c, x, -26, 24, 26), WOOD_DK, sh=3, hl=1.2)
        paint(ctx, lambda c, x=x: ellipse(c, x, -26, 17, 19), WOOD, sh=2, hl=0.8, line=0.6)
        for a in range(0, 180, 45):
            stroke(ctx, lambda c, x=x, a=a: (c.move_to(x - 17 * math.cos(math.radians(a)), -26 - 19 * math.sin(math.radians(a))),
                                            c.line_to(x + 17 * math.cos(math.radians(a)), -26 + 19 * math.sin(math.radians(a)))), WOOD_DK.base, 2)
    paint(ctx, poly([(-76, -30), (-80, -64), (80, -64), (76, -30)], 0.04), WOOD, sh=3, hl=1.2)
    paint(ctx, poly([(-72, -60), (-52, -96), (52, -96), (72, -60)], 0.15), Pal('#e0c068', '#b89a40', '#f8e090', '#5a4818'), sh=3, hl=1.4)
    for i in range(12):
        stroke(ctx, lambda c, i=i: (c.move_to(-64 + i * 11, -62), c.line_to(-60 + i * 10, -90)), hx('#f8e090'), 1.3, 0.8)
    stroke(ctx, lambda c: (c.move_to(76, -44), c.line_to(112, -34)), WOOD_DK.base, 5)


@prop('planter', 70, 90, 35, 80, col=(40, 20, 0), shadow=(2, 0, 28, 7, 0.28))
def planter(ctx):
    paint(ctx, poly([(-20, 0), (-26, -34), (26, -34), (20, 0)], 0.06), Pal('#c07c52', '#9a5a3a', '#e0a070', '#4a2a18'), sh=2.5, hl=1)
    rnd = random.Random(8)
    flat(ctx, lambda c: blob(c, [(-14, -42, 11), (0, -48, 13), (14, -42, 11), (0, -38, 12)]), LEAF.base)
    for i in range(7):
        x, y = rnd.uniform(-18, 18), rnd.uniform(-58, -40)
        flat(ctx, lambda c, x=x, y=y: blob(c, [(x, y, 4)]), hx(rnd.choice(['#ff6f91', '#ffd84a', '#ffffff', '#b078d8'])))


@prop('bench', 110, 70, 55, 60, col=(90, 18, 0), shadow=(2, 0, 48, 8, 0.28))
def bench(ctx):
    for x in (-40, 40):
        paint(ctx, poly([(x - 4, 0), (x - 4, -26), (x + 4, -26), (x + 4, 0)], 0.02), WOOD_DK, sh=1, hl=0.5)
    paint(ctx, poly([(-48, -24), (48, -24), (48, -32), (-48, -32)], 0.02), WOOD, sh=2, hl=1)
    paint(ctx, poly([(-46, -34), (46, -34), (46, -46), (-46, -46)], 0.02), WOOD, sh=2, hl=1)


@prop('statue_hero', 140, 260, 70, 232, col=(70, 40, 0), shadow=(2, 0, 58, 12, 0.34))
def statue_hero(ctx):
    pal = Pal('#c8c6d4', '#9a98b0', '#eceaf6', '#3b3a50')
    paint(ctx, poly([(-46, 0), (-40, -26), (40, -26), (46, 0)], 0.03), pal, sh=3, hl=1.2)
    paint(ctx, poly([(-32, -26), (-28, -62), (28, -62), (32, -26)], 0.03), pal, sh=3, hl=1.2)
    # heroic figure with a raised sword
    paint(ctx, poly([(-14, -62), (-18, -118), (18, -118), (14, -62)], 0.05), pal, sh=2.5, hl=1)
    paint(ctx, lambda c: ellipse(c, 0, -128, 11, 12), pal, sh=2, hl=1)
    stroke(ctx, lambda c: (c.move_to(14, -104), c.line_to(34, -150), c.line_to(36, -196)), pal.light, 6)
    stroke(ctx, lambda c: (c.move_to(14, -104), c.line_to(34, -150), c.line_to(36, -196)), pal.base, 3)
    flat(ctx, poly([(26, -150), (44, -150), (44, -146), (26, -146)]), GOLD.base)
    paint(ctx, poly([(-18, -112), (-30, -80), (-14, -72)], 0.05), Pal('#d6453d', '#a52c33', '#f27a5f', '#5a1418'), sh=1.5, hl=0.8)


@prop('stall_blue', 170, 160, 85, 146, col=(140, 30, 0), shadow=(4, 0, 70, 12, 0.3))
def stall_blue(ctx):
    paint(ctx, poly([(-70, 0), (-70, -44), (70, -44), (70, 0)], 0.02), WOOD, sh=4, hl=1.5)
    for x in (-66, 66):
        paint(ctx, poly([(x - 4, -40), (x - 4, -110), (x + 4, -110), (x + 4, -40)], 0.02), WOOD_DK, sh=2, hl=1)
    rnd = random.Random(5)
    for i in range(7):                                  # cloth bolts and jars
        x = -54 + i * 18
        col = rnd.choice(['#4a8fe0', '#d6453d', '#ffcf40', '#8a5ad0'])
        paint(ctx, poly([(x - 7, -42), (x - 7, -62), (x + 7, -62), (x + 7, -42)], 0.1), Pal(col, shade_c(col), '#ffffff', '#222222'), sh=1.5, hl=1, line=0.8)
    awning(ctx, -80, 80, -104, 34, CLOTH_B, 8)


@prop('stall_green', 170, 160, 85, 146, col=(140, 30, 0), shadow=(4, 0, 70, 12, 0.3))
def stall_green(ctx):
    paint(ctx, poly([(-70, 0), (-70, -44), (70, -44), (70, 0)], 0.02), WOOD, sh=4, hl=1.5)
    for x in (-66, 66):
        paint(ctx, poly([(x - 4, -40), (x - 4, -110), (x + 4, -110), (x + 4, -40)], 0.02), WOOD_DK, sh=2, hl=1)
    rnd = random.Random(9)
    for i in range(8):                                  # vegetables
        x = -56 + i * 16
        col = rnd.choice(['#6fbf4a', '#e0703f', '#f0e060', '#a05ac0'])
        paint(ctx, lambda c, x=x: ellipse(c, x, -50, 7, 6), Pal(col, shade_c(col), '#ffffff', '#222222'), sh=1.2, hl=0.8, line=0.7)
    awning(ctx, -80, 80, -104, 34, Pal('#4f9a6a', '#3a7850', '#7cc896', '#16301f'), 8)


@prop('lamp_ornate', 70, 170, 35, 160, col=(14, 10, 0), shadow=(2, 0, 16, 5, 0.3))
def lamp_ornate(ctx):
    pal = Pal('#3a3a4e', '#26263a', '#5e5e78', '#101018')
    paint(ctx, poly([(-9, 0), (-6, -10), (-3, -110), (3, -110), (6, -10), (9, 0)], 0.2), pal, sh=1.5, hl=0.8)
    stroke(ctx, lambda c: (c.move_to(0, -96), c.curve_to(-30, -96, -34, -118, -30, -128), c.move_to(0, -96), c.curve_to(30, -96, 34, -118, 30, -128)), pal.base, 3)
    for x in (-30, 30):
        radial_glow(ctx, x, -140, 30, hx('#ffd27a'), 0.5)
        paint(ctx, poly([(x - 8, -126), (x + 8, -126), (x + 10, -148), (x - 10, -148)], 0.1), GLASS, sh=1, hl=1)
        flat(ctx, lambda c, x=x: ellipse(c, x, -138, 5, 7), hx('#fff1b0'), 0.95)
        paint(ctx, poly([(x - 14, -148), (x, -158), (x + 14, -148)], 0.1), pal, sh=1, hl=0.6)
