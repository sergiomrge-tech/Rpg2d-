"""HD cartoon humanoid (anime proportions) rendered in 3 views: down (front), up (back), side (right).

All coordinates are final pixels, origin at the feet (pivot), y grows downward.
A pose is a dict of screen-space joint angles (see `default_pose`). Angle convention for limbs:
direction vector = (sin a, cos a) -> 0 points down, +90 points to +x, 180 points up.
Limb keys: 'a' = far / screen-right-in-front-view limb, 'b' = sword-hand limb.
"""
from __future__ import annotations
import math
import cairo
from core import (Pal, Shape, paint, flat, stroke, ellipse, capsule, smooth_poly, rot, hx, shade, mix,
                  radial_glow)

HIP_Y = -31.0
TORSO = 25.0
UA, FA = 12.5, 11.5          # upper arm / forearm
TH, SH = 14.5, 13.5          # thigh / shin


def vec(a, l):
    r = math.radians(a)
    return math.sin(r) * l, math.cos(r) * l


def add(p, q):
    return p[0] + q[0], p[1] + q[1]


class Look:
    def __init__(self, **kw):
        self.skin = Pal('#f7d6bf', '#e6ad93', '#fff0e4', '#8a4b3c')
        self.hair = Pal('#2f3352', '#1f2138', '#5b6aa0', '#151626')
        self.eye = hx('#3d7fd6')
        self.tunic = Pal('#2f78a8', '#245a85', '#5aa6d4', '#152c48')
        self.shirt = Pal('#f2e8d5', '#d2c2a8', '#ffffff', '#6b5844')
        self.pants = Pal('#4b3f4f', '#352c3a', '#6c5d70', '#1d1820')
        self.boots = Pal('#7a4b2e', '#5a341f', '#a46c45', '#2d1a10')
        self.belt = Pal('#4a3022', '#33201a', '#6d4a35', '#1d120d')
        self.metal = Pal('#e8c35a', '#b98a2c', '#fff0a8', '#5e4313')
        self.scarf = Pal('#d6453d', '#a52c33', '#f27a5f', '#5a1418')
        self.glove = Pal('#8a5a3a', '#663f27', '#b07d55', '#33200f')
        self.hair_style = 'spiky'
        self.scarf_on = True
        self.cape = None
        self.weapon = 'sword'
        self.blade = Pal('#dfe8f2', '#9aa9bf', '#ffffff', '#3b4660')
        self.dress = False
        self.apron = None
        self.beard = None
        self.hat = None
        self.__dict__.update(kw)


def default_pose():
    return dict(x=0.0, y=0.0, rot=0.0, sq=1.0, lean=0.0, hip=HIP_Y, tilt=0.0, hdy=0.0,
                arm_a=(8.0, 4.0, 1.0, 1.0), arm_b=(-8.0, -4.0, 1.0, 1.0),
                leg_a=(4.0, 2.0, 1.0, 1.0), leg_b=(-4.0, -2.0, 1.0, 1.0),
                wpn=None, wpn_front=True, eyes='open', mouth='n', scarf=0.0, glow=None,
                look_dx=0.0, trail=None)


# ============================================================== parts
def draw_leg(ctx, L: Look, hip, leg, view, far=False):
    a1, a2, s1, s2 = leg
    knee = add(hip, vec(a1, TH * s1))
    ankle = add(knee, vec(a2, SH * s2))
    pants = L.pants if not far else Pal(L.pants.shadow, L.pants.deep, L.pants.base, L.pants.line)
    boots = L.boots if not far else Pal(L.boots.shadow, L.boots.deep, L.boots.base, L.boots.line)
    paint(ctx, lambda c: (capsule(c, hip, knee, 5.6, 4.9), capsule(c, knee, ankle, 4.9, 4.2)), pants,
          sh=1.6, hl=0.8)
    # boot
    if view == 'side':
        toe = add(ankle, (7.5, 1.0))

        def boot(c):
            c.move_to(ankle[0] - 4.6, ankle[1] - 6.5)
            c.line_to(ankle[0] + 3.6, ankle[1] - 6.5)
            c.curve_to(ankle[0] + 4.0, ankle[1] - 2.0, toe[0] - 1, toe[1] - 4.5, toe[0], toe[1] - 1.5)
            c.curve_to(toe[0] + 1.2, toe[1] + 1.5, toe[0] - 1.0, toe[1] + 3.2, toe[0] - 3, toe[1] + 3.2)
            c.line_to(ankle[0] - 4.6, ankle[1] + 4.2)
            c.curve_to(ankle[0] - 6.0, ankle[1] + 2, ankle[0] - 5.4, ankle[1] - 3, ankle[0] - 4.6, ankle[1] - 6.5)
            c.close_path()
        paint(ctx, boot, boots, sh=1.5, hl=1.0)
        stroke(ctx, lambda c: (c.move_to(ankle[0] - 4.8, ankle[1] - 4.0), c.line_to(ankle[0] + 3.8, ankle[1] - 4.0)),
               boots.line, 0.9, 0.7)
    else:
        def boot(c):
            smooth_poly(c, [(ankle[0] - 4.7, ankle[1] - 6.5), (ankle[0] + 4.7, ankle[1] - 6.5),
                            (ankle[0] + 5.2, ankle[1] + 0.5), (ankle[0] + 3.8, ankle[1] + 4.6),
                            (ankle[0], ankle[1] + 5.4), (ankle[0] - 3.8, ankle[1] + 4.6),
                            (ankle[0] - 5.2, ankle[1] + 0.5)], tension=0.45)
        paint(ctx, boot, boots, sh=1.6, hl=1.0)
        stroke(ctx, lambda c: (c.move_to(ankle[0] - 4.8, ankle[1] - 3.6), c.curve_to(ankle[0] - 2, ankle[1] - 2.6,
                                                                                    ankle[0] + 2, ankle[1] - 2.6,
                                                                                    ankle[0] + 4.8, ankle[1] - 3.6)),
               boots.line, 0.9, 0.7)
    return ankle


def draw_arm(ctx, L: Look, sh_pt, arm, far=False, glow=None):
    a1, a2, s1, s2 = arm
    elbow = add(sh_pt, vec(a1, UA * s1))
    hand = add(elbow, vec(a2, FA * s2))
    tunic = L.tunic if not far else Pal(L.tunic.shadow, L.tunic.deep, L.tunic.base, L.tunic.line)
    shirt = L.shirt if not far else Pal(L.shirt.shadow, shade(L.shirt.shadow, -0.08), L.shirt.base, L.shirt.line)
    glove = L.glove if not far else Pal(L.glove.shadow, L.glove.deep, L.glove.base, L.glove.line)
    paint(ctx, lambda c: capsule(c, sh_pt, elbow, 4.9, 4.2), tunic, sh=1.5, hl=0.9)
    paint(ctx, lambda c: capsule(c, elbow, hand, 4.0, 3.5), shirt, sh=1.4, hl=0.8)
    # cuff
    cuff_c = add(elbow, vec(a2, FA * s2 * 0.62))
    paint(ctx, lambda c: ellipse(c, cuff_c[0], cuff_c[1], 4.3, 3.0, -a2), glove, sh=1.0, hl=0.6, line=0.8)
    if glow:
        radial_glow(ctx, hand[0], hand[1], 16, glow, 0.55)
    paint(ctx, lambda c: ellipse(c, hand[0], hand[1], 3.9, 3.9), glove, sh=1.3, hl=0.9)
    return hand


def draw_sword(ctx, L: Look, hand, ang, scale=1.0, trail=None):
    ctx.save()
    ctx.translate(*hand)
    ctx.rotate(math.radians(-ang))
    ctx.scale(1, scale)
    blade_len = 33

    def blade(c):
        c.move_to(-2.4, 5)
        c.line_to(-2.6, blade_len - 6)
        c.curve_to(-2.4, blade_len - 3, -0.8, blade_len - 0.5, 0, blade_len + 1.5)
        c.curve_to(0.8, blade_len - 0.5, 2.4, blade_len - 3, 2.6, blade_len - 6)
        c.line_to(2.4, 5)
        c.close_path()
    paint(ctx, blade, L.blade, sh=1.6, hl=1.0, line=0.9, grad=False)
    stroke(ctx, lambda c: (c.move_to(0, 6), c.line_to(0, blade_len - 3)), L.blade.shadow, 0.7, 0.8)
    paint(ctx, lambda c: smooth_poly(c, [(-7, 3.2), (7, 3.2), (6.6, 5.6), (-6.6, 5.6)], tension=0.2),
          L.metal, sh=0.9, hl=0.6, line=0.8)
    paint(ctx, lambda c: capsule(c, (0, -4.5), (0, 3), 1.9), L.belt, sh=0.8, hl=0.4, line=0.7)
    paint(ctx, lambda c: ellipse(c, 0, -5.6, 2.4, 2.4), L.metal, sh=0.8, hl=0.6, line=0.7)
    ctx.restore()


def scarf_tail(ctx, L, base, dirx, phase, length=16):
    """Fluttering cloth tail starting at `base`, flowing toward dirx (-1 left / +1 right)."""
    pts_top, pts_bot = [], []
    for i in range(6):
        u = i / 5
        x = base[0] + dirx * u * length
        wave = math.sin(phase * 2 * math.pi + u * 3.2) * (1.2 + u * 2.6)
        y = base[1] + u * 7 + wave
        w = 3.2 - u * 1.2
        pts_top.append((x, y - w))
        pts_bot.append((x, y + w))

    def sh(c):
        smooth_poly(c, pts_top + [(pts_top[-1][0] + dirx * 2.5, pts_top[-1][1] + 2.5)] + pts_bot[::-1], tension=0.35)
    paint(ctx, sh, L.scarf, sh=1.4, hl=0.8, line=0.9)


# ---------------------------------------------------------------- head
def hair_spikes(cx, cy, rx, ry, tips):
    """Points of a spiky hair silhouette: tips = [(angle_deg, extra_len, width_deg)]; angle 0 = up, + clockwise."""
    pts = []
    steps = 48
    for i in range(steps):
        ang = i / steps * 360
        r = 1.0
        for ta, tl, tw in tips:
            d = (ang - ta + 540) % 360 - 180
            if abs(d) < tw:
                k = 1 - abs(d) / tw
                r += tl * k ** 1.6
        rad = math.radians(ang)
        pts.append((cx + math.sin(rad) * rx * r, cy - math.cos(rad) * ry * r))
    return pts


def locks_path(c, cx, cy, rx, ry, locks):
    """Union path: head ellipse + curved anime locks. lock = (angle, length, half_width_deg, sweep_deg)."""
    ellipse(c, cx, cy, rx, ry)
    for ang, ln, hw, sw in locks:
        a0, a1 = math.radians(ang - hw), math.radians(ang + hw)
        p0 = (cx + math.sin(a0) * rx * 0.86, cy - math.cos(a0) * ry * 0.86)
        p1 = (cx + math.sin(a1) * rx * 0.86, cy - math.cos(a1) * ry * 0.86)
        at = math.radians(ang + sw)
        bx, by = cx + math.sin(math.radians(ang)) * rx, cy - math.cos(math.radians(ang)) * ry
        tip = (bx + math.sin(at) * ln, by - math.cos(at) * ln)
        mid = math.radians(ang + sw * 0.4)
        k = ln * 0.75
        c.new_sub_path()
        c.move_to(*p0)
        c.curve_to(p0[0] + math.sin(mid) * k, p0[1] - math.cos(mid) * k,
                   tip[0] - math.sin(at) * ln * 0.25, tip[1] + math.cos(at) * ln * 0.25, *tip)
        c.curve_to(tip[0] - math.sin(at) * ln * 0.2, tip[1] + math.cos(at) * ln * 0.2,
                   p1[0] + math.sin(mid) * k * 0.9, p1[1] - math.cos(mid) * k * 0.9, *p1)
        c.close_path()


LOCKS_FRONT = [(-118, 6, 30, -40), (-84, 8, 28, -38), (-50, 9.5, 27, -30), (-16, 9, 26, -18), (18, 10, 26, 14),
               (52, 9, 27, 30), (86, 8, 28, 40), (118, 6, 30, 44)]
LOCKS_BACK = LOCKS_FRONT + [(150, 6, 28, 30), (-150, 6, 28, -30), (180, 6, 26, 6)]
LOCKS_SIDE = [(-158, 7, 30, -30), (-124, 9.5, 28, -40), (-90, 10, 27, -38), (-56, 9.5, 26, -26), (-22, 8.5, 24, -10),
              (12, 7, 22, 14), (178, 6, 28, -16)]

SPIKES = [(-95, 0.18, 22), (-62, 0.30, 20), (-30, 0.36, 20), (0, 0.30, 18), (32, 0.38, 20),
          (64, 0.30, 20), (97, 0.2, 22), (140, 0.16, 25), (-140, 0.16, 25), (180, 0.10, 20)]


def draw_eye(ctx, L, x, y, s=1.0, mode='open', side=False, look_dx=0.0):
    line = hx('#2a1720')
    w = 3.6 * s * (0.75 if side else 1.0)
    h = 4.8 * s
    if mode == 'closed':
        stroke(ctx, lambda c: (c.move_to(x - w, y + 0.5), c.curve_to(x - w * 0.4, y + 2.2, x + w * 0.4, y + 2.2,
                                                                     x + w, y + 0.5)), line, 1.3)
        return
    if mode == 'squint':
        stroke(ctx, lambda c: (c.move_to(x - w, y - 0.6), c.line_to(x + w * 0.9, y + 0.8), c.line_to(x - w * 0.4, y + 2.0)),
               line, 1.3)
        return
    hh = h * (1.15 if mode == 'wide' else 1.0)
    flat(ctx, lambda c: ellipse(c, x, y + 0.4, w, hh), hx('#ffffff'))
    ix = x + look_dx * w * 0.35 + (w * 0.15 if side else 0)
    iw, ih = w * 0.86, hh * 0.86
    ctx.save()
    ellipse(ctx, x, y + 0.4, w, hh)
    ctx.clip()
    g = cairo.LinearGradient(0, y - ih, 0, y + ih)
    g.add_color_stop_rgba(0, *shade(L.eye, -0.30))
    g.add_color_stop_rgba(0.55, *L.eye)
    g.add_color_stop_rgba(1, *shade(L.eye, 0.22, -0.1))
    ctx.set_source(g)
    ellipse(ctx, ix, y + 1.0, iw, ih)
    ctx.fill()
    flat(ctx, lambda c: ellipse(c, ix, y + 1.3, iw * 0.45, ih * 0.5), shade(L.eye, -0.42))
    flat(ctx, lambda c: ellipse(c, ix - iw * 0.35, y - ih * 0.35, 1.25 * s, 1.35 * s), hx('#ffffff'))
    flat(ctx, lambda c: ellipse(c, ix + iw * 0.35, y + ih * 0.45, 0.6 * s, 0.6 * s), hx('#ffffff'), 0.9)
    ctx.restore()
    # upper lash line
    stroke(ctx, lambda c: (c.move_to(x - w - 0.6, y - hh * 0.35), c.curve_to(x - w * 0.5, y - hh - 0.7,
                                                                            x + w * 0.5, y - hh - 0.7,
                                                                            x + w + 0.8, y - hh * 0.5)),
           line, 1.5)
    stroke(ctx, lambda c: (c.move_to(x - w * 0.6, y + hh + 0.3), c.line_to(x + w * 0.4, y + hh + 0.3)), line, 0.6, 0.6)


def draw_head(ctx, L: Look, view, hc, tilt, P):
    ctx.save()
    ctx.translate(*hc)
    ctx.rotate(math.radians(tilt))
    skin, hair = L.skin, L.hair
    eyes, mouth = P['eyes'], P['mouth']
    if view == 'down':
        hair_back = hair_spikes(0, -3, 20.5, 19.5, SPIKES) if L.hair_style == 'spiky' else None
        if L.hair_style == 'long':
            paint(ctx, lambda c: smooth_poly(c, [(-21, -6), (-22, 10), (-20, 26), (-12, 30), (0, 28), (12, 30),
                                                 (20, 26), (22, 10), (21, -6), (14, -20), (0, -24), (-14, -20)]),
                  hair, sh=2.4, hl=1.2)
        elif hair_back:
            paint(ctx, lambda c: locks_path(c, 0, -3, 19.5, 18.5, LOCKS_FRONT), hair, sh=2.6, hl=1.4)
        # ears
        for sx in (-1, 1):
            paint(ctx, lambda c, sx=sx: ellipse(c, sx * 16.6, 3.5, 3.0, 4.2), skin, sh=1.0, hl=0.5, line=0.9)

        def face(c):
            smooth_poly(c, [(-16.5, -6), (-16.8, 3), (-13.6, 10.5), (-7.2, 16.2), (0, 18.2), (7.2, 16.2),
                            (13.6, 10.5), (16.8, 3), (16.5, -6), (11, -14), (0, -16), (-11, -14)], tension=0.5)
        paint(ctx, face, skin, sh=1.6, hl=0.8, line=1.0)
        # cheeks blush
        flat(ctx, lambda c: ellipse(c, -10.2, 9.2, 3.3, 1.8), hx('#f08a7e'), 0.35)
        flat(ctx, lambda c: ellipse(c, 10.2, 9.2, 3.3, 1.8), hx('#f08a7e'), 0.35)
        ld = P.get('look_dx', 0.0)
        draw_eye(ctx, L, -7.4, 3.6, 1.0, eyes, look_dx=ld)
        draw_eye(ctx, L, 7.4, 3.6, 1.0, eyes, look_dx=ld)
        # brows
        bline = hair.line
        browy = -3.6 if eyes != 'squint' else -2.4
        stroke(ctx, lambda c: (c.move_to(-10.6, browy), c.curve_to(-8.5, browy - 1.4, -6, browy - 1.2, -4.2, browy + 0.2)),
               bline, 1.1)
        stroke(ctx, lambda c: (c.move_to(10.6, browy), c.curve_to(8.5, browy - 1.4, 6, browy - 1.2, 4.2, browy + 0.2)),
               bline, 1.1)
        stroke(ctx, lambda c: (c.move_to(0.6, 9.4), c.line_to(-0.3, 10.6)), skin.line, 0.9, 0.6)
        draw_mouth(ctx, skin, 0, 13.6, mouth)
        # bangs over the forehead
        if L.hair_style == 'spiky':
            bang = [(-20, -8), (-19.5, 4), (-17.5, 10), (-15, 2.5), (-13, -3.5), (-11.5, 2.0), (-8.6, -4.5),
                    (-5.5, 1.5), (-2.5, -6), (0.5, 0.5), (3.2, -5.5), (6.6, 1.0), (9.5, -4.6), (12.2, 1.8),
                    (14.6, -3), (17.0, 4.5), (18.6, 11.5), (20.2, 3), (20.5, -8), (13, -19), (0, -22.5), (-13, -19)]
        else:
            bang = [(-20, -8), (-19.8, 6), (-17, 14), (-15.5, 0), (-10, -5.5), (-4, -3.5), (0, -7), (5, -3.6),
                    (10.5, -5.5), (15.5, 0), (17, 14), (19.8, 6), (20, -8), (13, -19), (0, -22.5), (-13, -19)]

        def bangs(c):
            c.move_to(*bang[0])
            for i in range(1, len(bang)):
                p0, p1 = bang[i - 1], bang[i]
                mx, my = (p0[0] + p1[0]) / 2, (p0[1] + p1[1]) / 2
                c.curve_to(mx - 0.4, my - 0.6, mx + 0.4, my - 0.6, *p1) if i > len(bang) - 5 else \
                    c.curve_to(p0[0] + (p1[0] - p0[0]) * 0.3, p0[1] + (p1[1] - p0[1]) * 0.1,
                               p0[0] + (p1[0] - p0[0]) * 0.7, p1[1], *p1)
            c.close_path()
        paint(ctx, bangs, hair, sh=2.0, hl=1.6, hl_alpha=0.9)
        # sheen arc
        stroke(ctx, lambda c: c.arc(0, -4, 15.5, math.radians(205), math.radians(250)), hair.light, 1.6, 0.85)
        stroke(ctx, lambda c: c.arc(0, -4, 15.5, math.radians(262), math.radians(282)), hair.light, 1.6, 0.85)
    elif view == 'up':
        if L.hair_style == 'long':
            paint(ctx, lambda c: smooth_poly(c, [(-21, -6), (-22, 10), (-20, 28), (-10, 33), (0, 31), (10, 33),
                                                 (20, 28), (22, 10), (21, -6), (14, -20), (0, -24), (-14, -20)]),
                  hair, sh=2.4, hl=1.2)
        for sx in (-1, 1):
            paint(ctx, lambda c, sx=sx: ellipse(c, sx * 16.8, 4.5, 2.8, 4.0), skin, sh=1.0, hl=0.4, line=0.9)
        paint(ctx, lambda c: smooth_poly(c, [(-7, 8), (7, 8), (6, 17), (-6, 17)], tension=0.4), skin, sh=1.0, hl=0)
        if L.hair_style == 'spiky':
            paint(ctx, lambda c: locks_path(c, 0, -2, 19.5, 19.0, LOCKS_BACK), hair, sh=2.8, hl=1.6)
            # strand lines
            for ang in (-40, 0, 40):
                stroke(ctx, lambda c, ang=ang: (c.move_to(math.sin(math.radians(ang)) * 4, -16),
                                                c.curve_to(math.sin(math.radians(ang)) * 10, -4,
                                                           math.sin(math.radians(ang)) * 14, 6,
                                                           math.sin(math.radians(ang)) * 12, 14)),
                       hair.shadow, 1.0, 0.8)
            stroke(ctx, lambda c: c.arc(0, -3, 16, math.radians(215), math.radians(265)), hair.light, 1.6, 0.8)
        else:
            stroke(ctx, lambda c: c.arc(0, -3, 16, math.radians(215), math.radians(265)), hair.light, 1.6, 0.8)
    else:  # side, facing right
        if L.hair_style == 'long':
            paint(ctx, lambda c: smooth_poly(c, [(-20, -6), (-22, 10), (-19, 28), (-8, 31), (2, 24), (4, 8),
                                                 (14, -14), (0, -23), (-14, -19)]), hair, sh=2.4, hl=1.2)
        elif L.hair_style == 'spiky':
            paint(ctx, lambda c: locks_path(c, -2.5, -3, 18.5, 18.5, LOCKS_SIDE), hair, sh=2.6, hl=1.4)

        def face(c):
            smooth_poly(c, [(-6, -14), (6, -16), (13.5, -9), (15.5, -1), (16.2, 4.5), (18.4, 8.2), (16.2, 9.6),
                            (15.6, 12.4), (13.2, 15.6), (8.6, 18.2), (2, 17.4), (-5, 12), (-7, 2)], tension=0.45)
        paint(ctx, face, skin, sh=1.6, hl=0.8, line=1.0)
        flat(ctx, lambda c: ellipse(c, 9.8, 9.6, 3.2, 1.8), hx('#f08a7e'), 0.35)
        paint(ctx, lambda c: ellipse(c, -0.8, 5.2, 2.3, 3.2), skin, sh=1.0, hl=0.3, line=0.8)
        draw_eye(ctx, L, 10.4, 3.6, 1.0, eyes, side=True, look_dx=0.6)
        browy = -3.4 if eyes != 'squint' else -2.2
        stroke(ctx, lambda c: (c.move_to(7.2, browy), c.curve_to(9.5, browy - 1.6, 12, browy - 1.2, 13.6, browy + 0.4)),
               hair.line, 1.1)
        draw_mouth(ctx, skin, 13.6, 13.6, mouth, side=True)
        if L.hair_style == 'spiky':
            bang = [(-4, -18), (6, -21), (15.5, -14), (19.5, -6), (16.5, -6.5), (17.2, 1.5), (13.2, -3.8),
                    (11.0, 0.8), (8.6, -5.2), (4.5, -2.2), (2.5, -7), (-2, -5), (-6, -10)]
            paint(ctx, lambda c: smooth_poly(c, bang, tension=0.25), hair, sh=1.8, hl=1.6, hl_alpha=0.9)
            stroke(ctx, lambda c: c.arc(0, -4, 15.5, math.radians(215), math.radians(262)), hair.light, 1.6, 0.85)
        else:
            paint(ctx, lambda c: smooth_poly(c, [(-6, -18), (6, -21), (15.5, -14), (18, -2), (14, -4), (9, -6),
                                                 (2, -5), (-4, -8)], tension=0.3), hair, sh=1.8, hl=1.6)
    if L.hat:
        L.hat(ctx, view)
    ctx.restore()


def draw_mouth(ctx, skin, x, y, mode, side=False):
    line = hx('#5a2630')
    if mode == 'open':
        paint(ctx, lambda c: ellipse(c, x, y + 0.4, 2.2 if not side else 1.5, 2.0), Pal('#7a2b3a', '#5a1e2a',
                                                                                         '#a34552', '#3a1018'),
              sh=0.6, hl=0, line=0.8)
        flat(ctx, lambda c: ellipse(c, x, y + 1.4, 1.2 if not side else 0.9, 0.7), hx('#e8797e'))
    elif mode == 'grit':
        paint(ctx, lambda c: smooth_poly(c, [(x - 2.8, y - 0.6), (x + 2.8, y - 0.6), (x + 2.2, y + 1.6),
                                             (x - 2.2, y + 1.6)], tension=0.2), Pal('#ffffff', '#dddddd', '#ffffff', '#5a2630'),
              sh=0, hl=0, line=0.8)
    elif mode == 'smile':
        stroke(ctx, lambda c: (c.move_to(x - 2.4, y - 0.4), c.curve_to(x - 1, y + 1.6, x + 1, y + 1.6, x + 2.4, y - 0.4)),
               line, 1.0)
    else:
        stroke(ctx, lambda c: (c.move_to(x - 1.6, y), c.curve_to(x - 0.5, y + 0.6, x + 0.5, y + 0.6, x + 1.6, y)), line, 0.9)


# ---------------------------------------------------------------- torso
def torso_pts(view, L):
    """Torso outline in torso-local coords: origin hip, -y up to shoulders (TORSO)."""
    if view == 'side':
        return [(-6.5, -TORSO + 1), (2, -TORSO - 0.5), (7.2, -TORSO + 3.5), (8, -14), (6.6, -6), (8.4, 2.5),
                (7, 6.5), (-7.5, 6.5), (-8.6, 2.5), (-6.8, -6), (-7.6, -15)]
    return [(-12.5, -TORSO + 2.5), (-6, -TORSO - 0.6), (6, -TORSO - 0.6), (12.5, -TORSO + 2.5), (10.6, -14),
            (9.0, -6.5), (11.6, 3), (10.8, 7), (0, 8.2), (-10.8, 7), (-11.6, 3), (-9.0, -6.5), (-10.6, -14)]


def tf(pts, origin, ang):
    return [add(origin, rot(x, y, ang)) for x, y in pts]


def draw_torso(ctx, L, view, hip, lean, P):
    pts = tf(torso_pts(view, L), hip, lean)
    paint(ctx, lambda c: smooth_poly(c, pts, tension=0.45), L.tunic, sh=2.4, hl=1.2, deep=0)
    # front details: collar V / shirt, belt
    if view == 'down':
        v = tf([(-4.5, -TORSO - 0.2), (4.5, -TORSO - 0.2), (0, -TORSO + 9)], hip, lean)
        paint(ctx, lambda c: smooth_poly(c, v, tension=0.1), L.shirt, sh=1.0, hl=0.4, line=0.8)
        # tunic stitch / center line
        cl = tf([(0, -TORSO + 9), (0, 7.5)], hip, lean)
        stroke(ctx, lambda c: (c.move_to(*cl[0]), c.line_to(*cl[1])), L.tunic.shadow, 1.0)
    if view == 'up':
        cl = tf([(-9, -TORSO + 4), (0, -TORSO + 9), (9, -TORSO + 4)], hip, lean)
        stroke(ctx, lambda c: (c.move_to(*cl[0]), c.curve_to(*cl[1], *cl[1], *cl[2])), L.tunic.shadow, 1.1)
    # belt
    bw = 11.2 if view != 'side' else 8.2
    belt = tf([(-bw, -6.8), (bw, -6.8), (bw + 0.3, -2.6), (-bw - 0.3, -2.6)], hip, lean)
    paint(ctx, lambda c: smooth_poly(c, belt, tension=0.12), L.belt, sh=1.0, hl=0.5, line=0.9)
    if view == 'down':
        bk = tf([(0, -4.7)], hip, lean)[0]
        paint(ctx, lambda c: ellipse(c, bk[0], bk[1], 2.8, 2.6), L.metal, sh=0.8, hl=0.6, line=0.8)
    elif view == 'side':
        pouch = tf([(-5.5, -4.5)], hip, lean)[0]
        paint(ctx, lambda c: smooth_poly(c, [(pouch[0] - 3, pouch[1] - 1.5), (pouch[0] + 3, pouch[1] - 1.5),
                                             (pouch[0] + 3.2, pouch[1] + 4.5), (pouch[0] - 3.2, pouch[1] + 4.5)],
                                         tension=0.3), L.boots, sh=1.0, hl=0.4, line=0.8)


def draw_scarf(ctx, L, view, neck, lean, phase):
    if not L.scarf_on:
        return
    if view == 'side':
        scarf_tail(ctx, L, add(neck, (-4, 2)), -1, phase, 15)
        paint(ctx, lambda c: ellipse(c, neck[0] + 0.5, neck[1] + 1.2, 7.2, 3.9, lean), L.scarf, sh=1.4, hl=0.8)
    elif view == 'down':
        paint(ctx, lambda c: ellipse(c, neck[0], neck[1] + 1.4, 10.5, 4.2, lean * 0.5), L.scarf, sh=1.6, hl=0.9)
        # knot + short tail on the sword side
        knot = add(neck, (-5.5, 3.6))
        paint(ctx, lambda c: ellipse(c, knot[0], knot[1], 3.0, 2.6), L.scarf, sh=1.0, hl=0.6)
        sw = math.sin(phase * 2 * math.pi) * 1.4

        def tail(c):
            smooth_poly(c, [(knot[0] - 1.5, knot[1]), (knot[0] + 2.4, knot[1] + 1), (knot[0] + 1.4 + sw, knot[1] + 10),
                            (knot[0] - 1.6 + sw, knot[1] + 11.5), (knot[0] - 3.2, knot[1] + 3)], tension=0.4)
        paint(ctx, tail, L.scarf, sh=1.2, hl=0.6)
    else:
        scarf_tail(ctx, L, add(neck, (2.5, 3)), 1, phase, 9)
        scarf_tail(ctx, L, add(neck, (-2.5, 3)), -1, phase + 0.3, 8)
        paint(ctx, lambda c: ellipse(c, neck[0], neck[1] + 1.4, 10.5, 4.2, lean * 0.5), L.scarf, sh=1.6, hl=0.9)


# ============================================================== full figure
def draw_figure(ctx, L: Look, view, P):
    ctx.save()
    ctx.translate(P['x'], P['y'])
    sq = P['sq']
    ctx.scale(1 / math.sqrt(sq), sq)
    if P['rot']:
        ctx.translate(0, P['hip'])
        ctx.rotate(math.radians(P['rot']))
        ctx.translate(0, -P['hip'])
    hip = (0.0, P['hip'])
    lean = P['lean']
    shoulder_c = add(hip, rot(0, -TORSO + 2.5, lean))
    neck = add(hip, rot(0, -TORSO - 0.5, lean))
    head_c = add(neck, rot(0, -19.5 + P['hdy'], lean * 0.6))
    tilt = P['tilt'] + lean * 0.4
    hipw = 5.4 if view != 'side' else 1.5
    hip_a = add(hip, rot(hipw if view == 'down' else -hipw, 0, lean * 0.3))
    hip_b = add(hip, rot(-hipw if view == 'down' else hipw, 0, lean * 0.3))
    if view == 'side':
        hip_a, hip_b = add(hip, (-1.5, 0)), add(hip, (1.5, 0))
    shw = 12.0
    if view == 'side':
        sh_a = add(shoulder_c, rot(-2.5, 0, lean))
        sh_b = add(shoulder_c, rot(1.0, 0, lean))
    elif view == 'down':
        sh_a = add(shoulder_c, rot(shw, 0, lean))
        sh_b = add(shoulder_c, rot(-shw, 0, lean))
    else:
        sh_a = add(shoulder_c, rot(-shw, 0, lean))
        sh_b = add(shoulder_c, rot(shw, 0, lean))

    wpn = P['wpn']
    hand_b_pos = add(add(sh_b, vec(P['arm_b'][0], UA * P['arm_b'][2])), vec(P['arm_b'][1], FA * P['arm_b'][3]))

    def weapon():
        if wpn is not None and L.weapon == 'sword':
            draw_sword(ctx, L, hand_b_pos, wpn, P.get('wscale', 1.0))
        elif wpn is not None and callable(L.weapon):
            L.weapon(ctx, L, hand_b_pos, wpn, P.get('wscale', 1.0))

    if view == 'side':
        draw_arm(ctx, L, sh_a, P['arm_a'], far=True, glow=P['glow'] if P.get('glow_hand') == 'a' else None)
        draw_leg(ctx, L, hip_a, P['leg_a'], view, far=True)
        if not P['wpn_front']:
            weapon()
        draw_torso(ctx, L, view, hip, lean, P)
        draw_leg(ctx, L, hip_b, P['leg_b'], view)
        draw_scarf(ctx, L, view, neck, lean, P['scarf'])
        draw_head(ctx, L, view, head_c, tilt, P)
        draw_arm(ctx, L, sh_b, P['arm_b'], glow=P['glow'])
        if P['wpn_front']:
            weapon()
    elif view == 'down':
        if not P['wpn_front']:
            weapon()
        draw_leg(ctx, L, hip_a, P['leg_a'], view)
        draw_leg(ctx, L, hip_b, P['leg_b'], view)
        draw_torso(ctx, L, view, hip, lean, P)
        draw_arm(ctx, L, sh_a, P['arm_a'], glow=P['glow'] if P.get('glow_hand') == 'a' else None)
        draw_scarf(ctx, L, view, neck, lean, P['scarf'])
        draw_head(ctx, L, view, head_c, tilt, P)
        draw_arm(ctx, L, sh_b, P['arm_b'], glow=P['glow'])
        if P['wpn_front']:
            weapon()
    else:  # up
        if not P['wpn_front']:
            weapon()
        draw_leg(ctx, L, hip_a, P['leg_a'], view)
        draw_leg(ctx, L, hip_b, P['leg_b'], view)
        if P.get('arms_behind'):
            draw_arm(ctx, L, sh_a, P['arm_a'])
            draw_arm(ctx, L, sh_b, P['arm_b'], glow=P['glow'])
        draw_torso(ctx, L, view, hip, lean, P)
        if not P.get('arms_behind'):
            draw_arm(ctx, L, sh_a, P['arm_a'], glow=P['glow'] if P.get('glow_hand') == 'a' else None)
            draw_arm(ctx, L, sh_b, P['arm_b'], glow=P['glow'])
        draw_head(ctx, L, view, head_c, tilt, P)
        draw_scarf(ctx, L, view, neck, lean, P['scarf'])
        if P['wpn_front']:
            weapon()
    ctx.restore()
    return dict(hand=hand_b_pos)
