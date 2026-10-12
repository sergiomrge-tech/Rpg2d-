"""Oni soldier: humanoid demon built on the hero rig (red skin, horns, spiked club, armour)."""
from __future__ import annotations
import math
from core import Pal, paint, flat, stroke, ellipse, capsule, smooth_poly, hx
from humanoid import Look

SKIN = Pal('#d24a3c', '#a02c2c', '#f2806a', '#3e0c0c')
HORN = Pal('#f2e2c0', '#c9ab84', '#ffffff', '#5b4127')
IRON = Pal('#5a5f74', '#3e4256', '#8a90a8', '#14161f')


def horns(ctx, view):
    if view == 'side':
        pts = [[(-2, -14), (4, -30), (10, -40), (8, -26), (6, -14)]]
    else:
        pts = [[(sx * 8, -14), (sx * 14, -30), (sx * 22, -40), (sx * 18, -26), (sx * 14, -12)] for sx in (-1, 1)]
    for p in pts:
        paint(ctx, lambda c, p=p: smooth_poly(c, p, tension=0.4), HORN, sh=1.5, hl=1, line=1.0)


def club(ctx, L, hand, ang, scale=1.0):
    ctx.save()
    ctx.translate(*hand)
    ctx.rotate(math.radians(-ang))
    ctx.scale(1, scale)
    paint(ctx, lambda c: capsule(c, (0, -5), (0, 10), 2.4, 2.8), Pal('#6a4030', '#4a2a1e', '#8a5a40', '#1e0c06'),
          sh=1, hl=0.5, line=0.9)

    def head(c):
        smooth_poly(c, [(-4, 8), (4, 8), (8.5, 22), (9.5, 36), (0, 42), (-9.5, 36), (-8.5, 22)], tension=0.45)
    paint(ctx, head, IRON, sh=3, hl=1.5, line=1.1)
    for y, x in ((18, -8), (26, 9), (34, -9), (22, 8.5), (30, -9.5), (38, 7)):
        paint(ctx, lambda c, x=x, y=y: smooth_poly(c, [(x, y - 2.5), (x + (5 if x > 0 else -5), y), (x, y + 2.5)], tension=0),
              Pal('#dfe2ee', '#9aa0b8', '#ffffff', '#1a1c28'), sh=0, hl=0, line=0.7)
    stroke(ctx, lambda c: (c.move_to(-7, 14), c.line_to(7, 14)), Pal('#c09040', '#8a6020', '#f0c060', '#3a2408').base, 2.4)
    ctx.restore()


def oni_look(boss=False):
    return Look(
        skin=SKIN,
        hair=Pal('#262036', '#16121f', '#4a4060', '#08060c'),
        eye=hx('#ffd23f'),
        tunic=IRON if not boss else Pal('#3a2a4a', '#24182e', '#5a4670', '#0a0610'),
        shirt=SKIN,
        pants=Pal('#3a2a2a', '#241818', '#5a4040', '#0c0606'),
        boots=Pal('#2a2430', '#18141c', '#463e50', '#08060a'),
        belt=Pal('#c09040', '#8a6020', '#f0c060', '#3a2408'),
        glove=SKIN,
        scarf_on=False,
        weapon=club,
        hat=horns,
    )


# ---------------------------------------------------------------- Lote 1 variants
GOLD = Pal('#f0c860', '#b8862c', '#fff2b0', '#4a300c')
STEEL = Pal('#c8d0e0', '#8a94ac', '#ffffff', '#1e2434')
SHAFT = Pal('#6a4030', '#4a2a1e', '#8a5a40', '#1e0c06')


def _xf(ctx, hand, ang, scale):
    ctx.save()
    ctx.translate(*hand)
    ctx.rotate(math.radians(-ang))
    ctx.scale(1, scale)


def spear(ctx, L, hand, ang, scale=1.0):
    _xf(ctx, hand, ang, scale)
    paint(ctx, lambda c: capsule(c, (0, -22), (0, 40), 1.8), SHAFT, sh=0.8, hl=0.4, line=0.8)
    paint(ctx, lambda c: smooth_poly(c, [(-4, 38), (0, 56), (4, 38), (0, 34)], tension=0.3), STEEL, sh=1.5, hl=1, line=0.9)
    paint(ctx, lambda c: smooth_poly(c, [(-4, 32), (4, 32), (3, 36), (-3, 36)], tension=0.1), GOLD, sh=0.6, hl=0.4, line=0.7)
    ctx.restore()


def axe(ctx, L, hand, ang, scale=1.0):
    _xf(ctx, hand, ang, scale)
    paint(ctx, lambda c: capsule(c, (0, -8), (0, 38), 2.2), SHAFT, sh=0.8, hl=0.4, line=0.8)

    def blade(c):
        c.move_to(1, 22)
        c.curve_to(14, 16, 22, 26, 20, 42)
        c.curve_to(14, 38, 8, 38, 1, 40)
        c.close_path()
    paint(ctx, blade, STEEL, sh=2.5, hl=1.5, line=1.0)
    stroke(ctx, lambda c: (c.move_to(19, 26), c.curve_to(21, 32, 21, 36, 20, 41)), (1, 1, 1, 1), 1.2, 0.8)
    paint(ctx, lambda c: smooth_poly(c, [(-2, 34), (-7, 30), (-2, 26)], tension=0.1), STEEL, sh=0.8, hl=0.5, line=0.8)
    ctx.restore()


def hammer(ctx, L, hand, ang, scale=1.0):
    _xf(ctx, hand, ang, scale)
    paint(ctx, lambda c: capsule(c, (0, -6), (0, 30), 2.4), SHAFT, sh=0.8, hl=0.4, line=0.8)
    paint(ctx, lambda c: smooth_poly(c, [(-13, 26), (13, 26), (14, 44), (-14, 44)], tension=0.12), IRON, sh=3, hl=1.5, line=1.1)
    for x in (-8, 0, 8):
        paint(ctx, lambda c, x=x: ellipse(c, x, 35, 2.2, 2.2), GOLD, sh=0.6, hl=0.4, line=0.6)
    ctx.restore()


def flail(ctx, L, hand, ang, scale=1.0):
    _xf(ctx, hand, ang, scale)
    paint(ctx, lambda c: capsule(c, (0, -4), (0, 12), 2.2), SHAFT, sh=0.8, hl=0.4, line=0.8)
    ctx.restore()
    # chain hangs with gravity, ball lags behind the swing
    r = math.radians(ang)
    tip = (hand[0] + math.sin(r) * 12, hand[1] + math.cos(r) * 12)
    ball = (tip[0] + math.sin(r) * 16, tip[1] + math.cos(r) * 16 + 8)
    for i in range(1, 6):
        u = i / 6
        p = (tip[0] + (ball[0] - tip[0]) * u, tip[1] + (ball[1] - tip[1]) * u + math.sin(u * math.pi) * 3)
        paint(ctx, lambda c, p=p: ellipse(c, p[0], p[1], 1.8, 1.8), STEEL, sh=0.4, hl=0.3, line=0.6)
    for k in range(8):
        a = k / 8 * math.tau
        paint(ctx, lambda c, a=a: smooth_poly(c, [(ball[0] + math.cos(a - 0.3) * 6, ball[1] + math.sin(a - 0.3) * 6),
                                                  (ball[0] + math.cos(a) * 11, ball[1] + math.sin(a) * 11),
                                                  (ball[0] + math.cos(a + 0.3) * 6, ball[1] + math.sin(a + 0.3) * 6)], tension=0),
              STEEL, sh=0, hl=0, line=0.6)
    paint(ctx, lambda c: ellipse(c, ball[0], ball[1], 7.5, 7.5), IRON, sh=2, hl=1.2, line=0.9)


def shield_mace(ctx, L, hand, ang, scale=1.0):
    # tower shield carried in front of the weapon hand, angled with the swing
    ctx.save()
    ctx.translate(*hand)
    ctx.rotate(math.radians(-ang * 0.25))
    paint(ctx, lambda c: smooth_poly(c, [(-13, -16), (13, -16), (14, 8), (0, 22), (-14, 8)], tension=0.3), IRON, sh=3, hl=1.5, line=1.1)
    paint(ctx, lambda c: smooth_poly(c, [(-9, -11), (9, -11), (10, 6), (0, 16), (-10, 6)], tension=0.3),
          Pal('#8a2a2a', '#5a1616', '#b84a4a', '#2a0606'), sh=2, hl=1, line=0.8)
    paint(ctx, lambda c: smooth_poly(c, [(0, -6), (6, 2), (0, 10), (-6, 2)], tension=0.1), GOLD, sh=1, hl=0.8, line=0.8)
    ctx.restore()


class make_horns:
    """Picklable horn/helmet drawer (Look.hat)."""

    def __init__(self, size=1.0, count=2, curve=0.0, pal=HORN, helmet=None):
        self.size, self.count, self.curve, self.pal, self.helmet = size, count, curve, pal, helmet

    def __call__(self, ctx, view):
        size, count, curve, pal, helmet = self.size, self.count, self.curve, self.pal, self.helmet
        if helmet is not None:
            if view == 'side':
                paint(ctx, lambda c: smooth_poly(c, [(-20, -2), (-18, -18), (0, -24), (16, -16), (18, -4), (6, -6), (-6, -4)],
                                                 tension=0.4), helmet, sh=2.5, hl=1.5, line=1.0)
            else:
                paint(ctx, lambda c: smooth_poly(c, [(-21, -2), (-19, -18), (0, -25), (19, -18), (21, -2), (10, -5), (-10, -5)],
                                                 tension=0.4), helmet, sh=2.5, hl=1.5, line=1.0)
                if view == 'down':
                    stroke(ctx, lambda c: (c.move_to(0, -24), c.line_to(0, -6)), helmet.light, 1.4, 0.8)
        sides = (-1, 1) if (view != 'side' and count == 2) else ((0,) if count == 1 else (1,))
        for sx in sides:
            if view == 'side':
                b = (-2, -14)
                d = 1
            else:
                b = (sx * 8, -14) if sx else (0, -18)
                d = sx if sx else 1
            l = 22 * size
            tip = (b[0] + d * (8 + curve * 10) * size, b[1] - l)
            mid = (b[0] + d * (16 * curve + 4) * size, b[1] - l * 0.55)
            paint(ctx, lambda c, b=b, tip=tip, mid=mid, d=d: smooth_poly(
                c, [(b[0] - 3.5 * size, b[1] + 1), mid, tip, (mid[0] + d * 3, mid[1] + 3), (b[0] + 4 * size, b[1] + 1)], tension=0.4),
                pal, sh=1.5, hl=1, line=1.0)


def oni_variant(kind):
    L = oni_look()
    if kind == 'oni_lancer':
        L.skin = Pal('#3a8a8a', '#266666', '#6ab8b0', '#0a2424')
        L.shirt = L.glove = L.skin
        L.tunic = Pal('#2a3a4a', '#1a2634', '#46586a', '#08101a')
        L.weapon = spear
        L.hat = make_horns(0.8, 2, 0.6)
    elif kind == 'oni_shielder':
        L.skin = Pal('#7a6a8a', '#5a4a6a', '#a090b0', '#1a1424')
        L.shirt = L.glove = L.skin
        L.tunic = IRON
        L.weapon = shield_mace
        L.hat = make_horns(0.9, 2, 0.0, helmet=IRON)
    elif kind == 'oni_executioner':
        L.skin = Pal('#3a2a3a', '#241824', '#5a465a', '#0a060a')
        L.shirt = L.glove = L.skin
        L.tunic = Pal('#2a1a1a', '#180c0c', '#4a2e2e', '#060202')
        L.eye = hx('#ff4a3a')
        L.weapon = axe
        L.hat = make_horns(1.25, 1, 0.3)
    elif kind == 'morgash_ironhorn':
        L.skin = Pal('#8a4a6a', '#6a2e4c', '#b87a98', '#24081a')
        L.shirt = L.glove = L.skin
        L.tunic = Pal('#4a3a3a', '#2e2222', '#6a5656', '#100808')
        L.weapon = hammer
        L.hat = make_horns(1.5, 2, 1.0, pal=GOLD)
    elif kind == 'krull_chainlord':
        L.skin = Pal('#4a5a7a', '#34405a', '#72829e', '#0c1220')
        L.shirt = L.glove = L.skin
        L.tunic = IRON
        L.eye = hx('#7ae8ff')
        L.weapon = flail
        L.hat = make_horns(1.0, 2, 0.4, helmet=STEEL)
    return L


# ---------------------------------------------------------------- Etapa 2: Velmoor humanoids
class Antlers:
    """Branch antlers + leaves (Dríade)."""

    def __call__(self, ctx, view):
        bark = Pal('#6a5040', '#4a362a', '#8e7058', '#1e120a')
        sides = (-1, 1) if view != 'side' else (-1,)
        for sx in sides:
            b = (sx * 9, -12) if view != 'side' else (-4, -14)
            pts = [b, (b[0] + sx * 8, b[1] - 14), (b[0] + sx * 18, b[1] - 22)]
            stroke(ctx, lambda c, pts=pts: (c.move_to(*pts[0]), c.curve_to(*pts[1], *pts[1], *pts[2])), bark.line, 4)
            stroke(ctx, lambda c, pts=pts: (c.move_to(*pts[0]), c.curve_to(*pts[1], *pts[1], *pts[2])), bark.base, 2.4)
            br = (b[0] + sx * 6, b[1] - 10)
            stroke(ctx, lambda c, br=br: (c.move_to(*br), c.line_to(br[0] - sx * 4, br[1] - 12)), bark.base, 2.2)
            for lx, ly in ((pts[2][0], pts[2][1]), (br[0] - sx * 4, br[1] - 12)):
                paint(ctx, lambda c, lx=lx, ly=ly: ellipse(c, lx, ly, 4, 2.6, 30 * sx),
                      Pal('#8a4aa0', '#5e2a78', '#b87ad0', '#200830'), sh=0.8, hl=0.6, line=0.7)


class ElfEars:
    def __call__(self, ctx, view):
        skin = Pal('#f7d6bf', '#e6ad93', '#fff0e4', '#8a4b3c')
        if view == 'side':
            paint(ctx, lambda c: smooth_poly(c, [(-2, 2), (-12, -8), (-1, 7)], tension=0.2), skin, sh=0.8, hl=0.4, line=0.8)
            return
        for sx in (-1, 1):
            paint(ctx, lambda c, sx=sx: smooth_poly(c, [(sx * 16, 1), (sx * 27, -9), (sx * 17, 7)], tension=0.2), skin,
                  sh=0.8, hl=0.4, line=0.8)


def bow(ctx, L, hand, ang, scale=1.0):
    ctx.save()
    ctx.translate(*hand)
    ctx.rotate(math.radians(-ang + 90))
    wood = Pal('#a06a3a', '#7a4a24', '#c89060', '#2a160a')
    stroke(ctx, lambda c: (c.move_to(0, -20), c.curve_to(10, -10, 10, 10, 0, 20)), wood.line, 4.2)
    stroke(ctx, lambda c: (c.move_to(0, -20), c.curve_to(10, -10, 10, 10, 0, 20)), wood.base, 2.6)
    stroke(ctx, lambda c: (c.move_to(0, -20), c.line_to(0, 20)), (0.95, 0.92, 0.85, 1), 0.8)
    ctx.restore()


def dryad_look():
    from humanoid import Look
    L = Look(hair_style='long', hair=Pal('#4a8a4a', '#2e6a36', '#7ab86a', '#0e2a12'), eye=hx('#ff5ad0'),
             skin=Pal('#c8b89a', '#a8957a', '#e8dcc4', '#3a2e1e'), tunic=Pal('#5a3a6a', '#3e2450', '#7e5a90', '#160a20'),
             shirt=Pal('#c8b89a', '#a8957a', '#e8dcc4', '#3a2e1e'), glove=Pal('#6a5040', '#4a362a', '#8e7058', '#1e120a'),
             pants=Pal('#3e2a32', '#2a1a20', '#5a4048', '#0e0608'), boots=Pal('#6a5040', '#4a362a', '#8e7058', '#1e120a'),
             scarf_on=False, weapon=None)
    L.hat = Antlers()
    return L


def sylra_look():
    from humanoid import Look
    L = Look(hair_style='long', hair=Pal('#e0e4f0', '#b0b8d0', '#ffffff', '#4a5068'), eye=hx('#3fc87a'),
             tunic=Pal('#3a7a4a', '#285c36', '#5aa068', '#0e2a16'), shirt=Pal('#f2e8d5', '#d2c2a8', '#ffffff', '#6b5844'),
             scarf=Pal('#e8c060', '#b88a30', '#fff0a0', '#4a3008'), scarf_on=True, weapon=bow)
    L.hat = ElfEars()
    return L
