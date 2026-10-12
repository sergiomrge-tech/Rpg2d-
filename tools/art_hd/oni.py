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
