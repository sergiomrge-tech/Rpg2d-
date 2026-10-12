"""Oni soldier: humanoid demon built on the hero rig (red skin, horns, spiked club, armour)."""
from __future__ import annotations
import math
from core import Pal, paint, flat, stroke, ellipse, capsule, smooth_poly, hx, radial_glow
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


# ---------------------------------------------------------------- Etapa 2: Valemont
def dagger(ctx, L, hand, ang, scale=1.0):
    _xf(ctx, hand, ang, scale)
    paint(ctx, lambda c: capsule(c, (0, -4), (0, 3), 2.0), SHAFT, sh=0.6, hl=0.3, line=0.7)
    paint(ctx, lambda c: smooth_poly(c, [(-3, 3), (3, 3), (2, 20), (0, 25), (-2, 20)], tension=0.1),
          Pal('#b8f0e0', '#6ac0a8', '#ffffff', '#10382c'), sh=1.2, hl=0.8, line=0.8)
    paint(ctx, lambda c: smooth_poly(c, [(-6, 2), (6, 2), (5, 5), (-5, 5)], tension=0.1), GOLD, sh=0.6, hl=0.4, line=0.6)
    ctx.restore()


class Hood:
    """Hooded cowl with a shadowed face (Assassino Sombrio) - picklable Look.hat."""

    def __call__(self, ctx, view):
        cloth = Pal('#2a2038', '#181224', '#463a5c', '#08040e')
        if view == 'up':
            paint(ctx, lambda c: smooth_poly(c, [(-22, 6), (-22, -14), (0, -30), (22, -14), (22, 6), (0, 14)], tension=0.4), cloth, sh=2.5, hl=1.2, line=1.0)
            return
        w = 22 if view == 'down' else 20
        paint(ctx, lambda c: smooth_poly(c, [(-w, 8), (-w, -14), (0, -30), (w, -14), (w, 8), (w * 0.5, 2), (0, -4), (-w * 0.5, 2)], tension=0.4),
              cloth, sh=2.5, hl=1.2, line=1.0)
        flat(ctx, lambda c: smooth_poly(c, [(-14, -2), (14, -2), (12, 12), (-12, 12)], tension=0.3), (0.03, 0.02, 0.06, 1), 0.85)
        for sx in ((-1, 1) if view == 'down' else (1,)):
            x = sx * 6 if view == 'down' else 7
            radial_glow(ctx, x, 3, 6, hx('#ff3a6a'), 0.6)
            flat(ctx, lambda c, x=x: ellipse(c, x, 3, 2.4, 1.6), hx('#ff7a9a'))


def assassin_look():
    from humanoid import Look
    cl = Pal('#2a2038', '#181224', '#463a5c', '#08040e')
    L = Look(skin=Pal('#c8b0a8', '#9a8078', '#e8d8d0', '#3a2a28'), tunic=cl, shirt=cl, pants=Pal('#1c1626', '#100c18', '#322a42', '#040208'),
             boots=Pal('#1c1626', '#100c18', '#322a42', '#040208'), glove=Pal('#2a2038', '#181224', '#463a5c', '#08040e'),
             belt=Pal('#6a1a3a', '#480e26', '#8a3a5a', '#1a0410'), scarf=Pal('#8a1a4a', '#5e0e30', '#b84a78', '#2a0410'),
             scarf_on=True, weapon=dagger, eye=hx('#ff5a7a'))
    L.hat = Hood()
    return L


def valemont_look(kind):
    from humanoid import Look
    P = Pal
    if kind == 'guard':
        return Look(hair=P('#5a4030', '#3e2a1e', '#7e5a44', '#1c1008'), tunic=P('#5a6a8a', '#3e4a66', '#7e8eae', '#141a2a'),
                    shirt=P('#c8d0e0', '#8a94ac', '#ffffff', '#1e2434'), scarf=P('#2a4a8a', '#1a3266', '#4a72c0', '#08122a'), weapon=spear)
    if kind == 'noble':
        return Look(hair_style='long', hair=P('#e8c860', '#b8962c', '#fff0a0', '#4a3808'), eye=hx('#6a5ae0'),
                    tunic=P('#7a2a8a', '#561a66', '#a456b8', '#240a2e'), shirt=P('#fff4e0', '#e0d0b0', '#ffffff', '#6a5a40'),
                    scarf=P('#f0c860', '#b8862c', '#fff2b0', '#4a300c'), weapon=None)
    if kind == 'cleric':
        return Look(hair=P('#d8d0c0', '#a8a090', '#fffaf0', '#4a4438'), tunic=P('#f4f0e8', '#d0c8b8', '#ffffff', '#6a6050'),
                    shirt=P('#f4f0e8', '#d0c8b8', '#ffffff', '#6a6050'), scarf=P('#e8b840', '#b8862c', '#fff0a0', '#4a300c'), weapon=None)
    if kind == 'child':
        return Look(hair=P('#c8602a', '#964214', '#f0904a', '#3a1404'), eye=hx('#3a9ae0'), tunic=P('#e0b040', '#b88a20', '#ffe080', '#4a3408'),
                    scarf_on=False, weapon=None)
    if kind == 'guildmaster':
        return Look(hair=P('#8a8a98', '#62626e', '#b8b8c8', '#22222a'), hair_style='spiky', eye=hx('#b8862c'),
                    tunic=P('#6a1a2a', '#480e1a', '#963a4a', '#1e0408'), shirt=P('#e8d8b8', '#c8b490', '#fff4d8', '#5a4630'),
                    scarf=P('#f0c860', '#b8862c', '#fff2b0', '#4a300c'), weapon=None)
    raise KeyError(kind)


# ---------------------------------------------------------------- Etapa 3 humanoids
def scimitar(ctx, L, hand, ang, scale=1.0):
    _xf(ctx, hand, ang, scale)
    paint(ctx, lambda c: capsule(c, (0, -4), (0, 4), 2.0), SHAFT, sh=0.6, hl=0.3, line=0.7)

    def blade(c):
        c.move_to(-2.5, 4)
        c.curve_to(-4, 24, 2, 40, 14, 46)
        c.curve_to(8, 36, 5, 22, 2.5, 4)
        c.close_path()
    paint(ctx, blade, STEEL, sh=1.6, hl=1, line=0.9)
    paint(ctx, lambda c: smooth_poly(c, [(-7, 2), (7, 2), (6, 6), (-6, 6)], tension=0.1), GOLD, sh=0.6, hl=0.4, line=0.6)
    ctx.restore()


class WitchHat:
    """Pointed witch hat (Look.hat), picklable."""

    def __call__(self, ctx, view):
        hat = Pal('#3a2a5a', '#241840', '#5a4488', '#0c0818')
        paint(ctx, lambda c: smooth_poly(c, [(-26, -12), (-12, -18), (-6, -42), (14, -62), (12, -20), (26, -12), (0, -6)], tension=0.2), hat, sh=2, hl=1.2, line=1.0)
        paint(ctx, lambda c: smooth_poly(c, [(-13, -17), (13, -19), (13, -13), (-13, -11)], tension=0.1), GOLD, sh=0.8, hl=0.5, line=0.7)


def region_oni(kind):
    L = oni_look()
    if kind == 'oni_nomad':
        L.skin = Pal('#d8a060', '#b07a38', '#f8cc90', '#4a2c0c')
        L.shirt = L.glove = L.skin
        L.tunic = Pal('#e8d0a0', '#c8aa78', '#fff0cc', '#5a4628')
        L.belt = Pal('#d6453d', '#a52c33', '#f27a5f', '#5a1418')
        L.weapon = scimitar
        L.hat = make_horns(0.9, 2, 0.5)
    elif kind == 'rock_oni':
        L.skin = Pal('#7a7488', '#585268', '#a09ab4', '#1a1624')
        L.shirt = L.glove = L.skin
        L.tunic = Pal('#4a3e34', '#32281e', '#6e5e4e', '#12100a')
        L.eye = hx('#4ab8ff')
        L.weapon = hammer
        L.hat = make_horns(1.0, 2, 0.1, pal=Pal('#6a6478', '#4a4458', '#948eaa', '#1a1624'), helmet=Pal('#e8c030', '#b08a10', '#fff0a0', '#4a3800'))
    elif kind == 'ice_oni':
        L.skin = Pal('#9ac8e8', '#6a98c4', '#cce8ff', '#1a3a5a')
        L.shirt = L.glove = L.skin
        L.tunic = Pal('#5a7aa8', '#3e5a84', '#82a2d0', '#10203a')
        L.eye = hx('#ffffff')
        L.weapon = spear
        L.hat = make_horns(1.1, 2, 0.8, pal=Pal('#e8fbff', '#a8d8f4', '#ffffff', '#2a5a7a'), helmet=STEEL)
    elif kind == 'succubus_mirael':
        from humanoid import Look
        L = Look(hair_style='long', hair=Pal('#c8307a', '#8e1a58', '#f06aa8', '#3a0620'), eye=hx('#ffd23f'),
                 skin=Pal('#a888c8', '#7a5ea0', '#d0b8e8', '#2a1a40'), tunic=Pal('#2a1a3a', '#180e28', '#463268', '#08040e'),
                 shirt=Pal('#a888c8', '#7a5ea0', '#d0b8e8', '#2a1a40'), glove=Pal('#2a1a3a', '#180e28', '#463268', '#08040e'),
                 pants=Pal('#2a1a3a', '#180e28', '#463268', '#08040e'), boots=Pal('#2a1a3a', '#180e28', '#463268', '#08040e'),
                 belt=Pal('#f0c860', '#b8862c', '#fff2b0', '#4a300c'), scarf=Pal('#c8307a', '#8e1a58', '#f06aa8', '#3a0620'),
                 scarf_on=True, weapon=None)
        L.hat = make_horns(1.1, 2, 1.0, pal=Pal('#3a1a3a', '#220e22', '#5e3a5e', '#0c040c'))
    return L


def region_npc(kind):
    from humanoid import Look
    P = Pal
    if kind == 'nomad':
        return Look(hair=P('#3a2a20', '#241810', '#5a4434', '#0c0806'), eye=hx('#6a4a1a'), skin=P('#d8a870', '#b08048', '#f4cc98', '#5a3818'),
                    tunic=P('#e8d0a0', '#c8aa78', '#fff0cc', '#5a4628'), shirt=P('#e8d0a0', '#c8aa78', '#fff0cc', '#5a4628'),
                    scarf=P('#2a8aa8', '#1a6480', '#52b4d0', '#08283a'), weapon=None)
    if kind == 'dwarf':
        return Look(hair=P('#b8602a', '#8a4214', '#e08a4a', '#3a1804'), eye=hx('#3a7ac8'), tunic=P('#7a3a2a', '#56241a', '#a85c48', '#240c06'),
                    shirt=P('#d0c8b8', '#a8a090', '#f4efe4', '#4a4438'), pants=P('#4a3e34', '#32281e', '#6e5e4e', '#12100a'),
                    scarf=P('#e8c030', '#b08a10', '#fff0a0', '#4a3800'), weapon=None)
    if kind == 'witch':
        L = Look(hair_style='long', hair=P('#a8a8b8', '#7e7e90', '#d4d4e4', '#2e2e3c'), eye=hx('#9aff6a'), skin=P('#c8d0a8', '#a0a880', '#e8f0cc', '#3a4020'),
                 tunic=P('#3a6a4a', '#264c34', '#5a9068', '#0c2214'), shirt=P('#c8d0a8', '#a0a880', '#e8f0cc', '#3a4020'),
                 scarf=P('#7a3a8a', '#56246a', '#a45cb8', '#240a2e'), weapon=None)
        L.hat = WitchHat()
        return L
    if kind == 'monk':
        return Look(hair=P('#e8e8f0', '#b8b8cc', '#ffffff', '#4a4a5e'), eye=hx('#6a9ae8'), tunic=P('#f4f0e8', '#d0c8b8', '#ffffff', '#6a6050'),
                    shirt=P('#f4f0e8', '#d0c8b8', '#ffffff', '#6a6050'), scarf=P('#3a6ac8', '#264a98', '#6a92e8', '#0c1a3a'), weapon=None)
    raise KeyError(kind)


# ---------------------------------------------------------------- Chapters 8-10
DARK_STEEL = Pal('#2e2a3e', '#1a1624', '#524a6a', '#08060e')
CRIMSON = Pal('#a01c34', '#6a0e22', '#d84a64', '#2a040c')


def greatsword(ctx, L, hand, ang, scale=1.0):
    _xf(ctx, hand, ang, scale)
    paint(ctx, lambda c: capsule(c, (0, -6), (0, 6), 2.4), SHAFT, sh=0.6, hl=0.3, line=0.8)
    paint(ctx, lambda c: smooth_poly(c, [(-11, 5), (11, 5), (9, 10), (-9, 10)], tension=0.1), GOLD, sh=0.8, hl=0.6, line=0.8)

    def blade(c):
        c.move_to(-5, 10)
        c.line_to(-6.5, 52)
        c.line_to(0, 66)
        c.line_to(6.5, 52)
        c.line_to(5, 10)
        c.close_path()
    radial_glow(ctx, 0, 36, 24, hx('#ff3a6a'), 0.35)
    paint(ctx, blade, DARK_STEEL, sh=2, hl=1.4, line=1.0)
    stroke(ctx, lambda c: (c.move_to(0, 12), c.line_to(0, 58)), (1, 0.25, 0.4, 1), 1.6, 0.9)
    ctx.restore()


class CrownHorns:
    """Crown of horns (Malgrath) / spiked helm; size scales the crown. Picklable Look.hat."""

    def __init__(self, size=1.0, helmet=None, glow=False):
        self.size, self.helmet, self.glow = size, helmet, glow

    def __call__(self, ctx, view):
        s = self.size
        if self.helmet is not None:
            w = 21 if view != 'side' else 19
            paint(ctx, lambda c: smooth_poly(c, [(-w, 2), (-w + 1, -16), (0, -25), (w - 1, -16), (w, 2), (w * 0.55, -3), (-w * 0.55, -3)], tension=0.35),
                  self.helmet, sh=2.5, hl=1.5, line=1.0)
            if view == 'down':
                stroke(ctx, lambda c: (c.move_to(0, -24), c.line_to(0, -2)), self.helmet.light, 1.4, 0.8)
                for sx in (-1, 1):
                    flat(ctx, lambda c, sx=sx: ellipse(c, sx * 6, 4, 2.4, 1.4), hx('#ff3a5a'))
                    radial_glow(ctx, sx * 6, 4, 6, hx('#ff3a5a'), 0.55)
        offs = [(-1, 10), (1, 10), (-1, 3), (1, 3)] if view != 'side' else [(1, 8), (1, 2)]
        for k, (sx, dx) in enumerate(offs):
            big = k < 2
            b = (sx * (dx if view != 'side' else 0) + (0 if view != 'side' else -2), -13)
            d = sx if view != 'side' else 1
            l = (26 if big else 16) * s
            tip = (b[0] + d * (10 if big else 6) * s, b[1] - l)
            mid = (b[0] + d * (18 if big else 8) * s, b[1] - l * 0.5)
            paint(ctx, lambda c, b=b, tip=tip, mid=mid, d=d: smooth_poly(
                c, [(b[0] - 3.5 * s, b[1] + 1), mid, tip, (mid[0] + d * 3, mid[1] + 3), (b[0] + 4 * s, b[1] + 1)], tension=0.4),
                Pal('#3a2a3a', '#220e22', '#5e3a5e', '#0c040c') if not self.glow else Pal('#f2e2c0', '#c9ab84', '#ffffff', '#5b4127'), sh=1.5, hl=1, line=1.0)
        if self.glow and view != 'up':
            radial_glow(ctx, 0, -20, 24, hx('#ff3a6a'), 0.35)


def final_look(kind):
    L = oni_look()
    if kind == 'demon_knight':
        L.skin = Pal('#6a3a4a', '#4a2432', '#8e5a6c', '#1e0c14')
        L.shirt = L.glove = L.skin
        L.tunic = DARK_STEEL
        L.pants = Pal('#1c1626', '#100c18', '#322a42', '#040208')
        L.boots = Pal('#1c1626', '#100c18', '#322a42', '#040208')
        L.belt = CRIMSON
        L.eye = hx('#ff4a5a')
        L.weapon = 'sword'
        L.blade = Pal('#5a526e', '#34304a', '#8a82a4', '#0c0a14')
        L.hat = CrownHorns(0.6, helmet=DARK_STEEL)
    elif kind == 'vorath':
        L.skin = Pal('#8a2a3a', '#5e1624', '#b85064', '#2a060e')
        L.shirt = L.glove = L.skin
        L.tunic = Pal('#2a1a2e', '#160c1a', '#4a3250', '#08040a')
        L.pants = Pal('#1c1626', '#100c18', '#322a42', '#040208')
        L.boots = Pal('#2a1a2e', '#160c1a', '#4a3250', '#08040a')
        L.belt = GOLD
        L.eye = hx('#ffd23f')
        L.scarf = CRIMSON
        L.scarf_on = True
        L.weapon = greatsword
        L.hat = CrownHorns(1.25, helmet=Pal('#2a1a2e', '#160c1a', '#4a3250', '#08040a'))
    elif kind == 'malgrath':
        from humanoid import Look
        black = Pal('#1a1020', '#0c0610', '#382a48', '#04020a')
        L = Look(skin=Pal('#7a1a3a', '#500e26', '#a8406a', '#240410'), hair=Pal('#2a1a3a', '#160c20', '#4a3262', '#08040e'), hair_style='spiky',
                 eye=hx('#ffffff'), tunic=black, shirt=Pal('#7a1a3a', '#500e26', '#a8406a', '#240410'), glove=black,
                 pants=black, boots=black, belt=GOLD, scarf=Pal('#5a1a8a', '#36105a', '#8a4ac0', '#16062a'), scarf_on=True,
                 weapon=greatsword)
        L.hat = CrownHorns(1.7, glow=True)
    return L


class Halo:
    """Golden halo above the head (Lumia). Picklable Look.hat."""

    def __call__(self, ctx, view):
        radial_glow(ctx, 0, -34, 36, hx('#ffe08a'), 0.5)
        stroke(ctx, lambda c: ellipse(c, 0, -34, 18, 5), hx('#ffd27a'), 3.4, 0.95)
        stroke(ctx, lambda c: ellipse(c, 0, -34, 18, 5), hx('#fffbe0'), 1.4, 1)


def final_npc(kind):
    from humanoid import Look
    P = Pal
    if kind == 'knight':
        return Look(hair_style='long', hair=P('#a8502e', '#7e3820', '#d47a4a', '#3a160a'), eye=hx('#3a7ac8'),
                    tunic=P('#8a98b8', '#5a688a', '#b8c6e0', '#1a2236'), shirt=P('#c8d0e0', '#8a94ac', '#ffffff', '#1e2434'),
                    scarf=P('#2a4a8a', '#1a3266', '#4a72c0', '#08122a'), weapon=None)
    if kind == 'veteran':
        return Look(hair=P('#9a9aa8', '#70707e', '#c8c8d4', '#2a2a34'), hair_style='spiky', eye=hx('#6a5a3a'),
                    tunic=P('#4a5a3a', '#32402a', '#6a7e52', '#121a0c'), shirt=P('#d8c8a8', '#b0a080', '#f4e8cc', '#4a3c24'),
                    scarf=P('#c8402a', '#962a18', '#f07a5a', '#3a0c04'), weapon=None)
    if kind == 'lumia':
        L = Look(hair_style='long', hair=P('#fff0c8', '#e0c890', '#ffffff', '#8a6a30'), eye=hx('#f0b030'),
                 tunic=P('#f8f4ff', '#d4ccec', '#ffffff', '#6a6090'), shirt=P('#f8f4ff', '#d4ccec', '#ffffff', '#6a6090'),
                 scarf=P('#f0c860', '#b8862c', '#fff2b0', '#4a300c'), scarf_on=True, weapon=None)
        L.hat = Halo()
        return L
    raise KeyError(kind)
