"""Lote 1 (concepts from the asset catalog) rebuilt on the animated Imp rig: real per-view drawings and
per-state poses. Imported at the end of demons.py."""
from __future__ import annotations
import math
import demons as D
from core import Pal, paint, flat, stroke, ellipse, capsule, smooth_poly, hx, radial_glow

Imp = D.Imp
add, vec = D.add, D.vec
GOLD = Pal('#f0c860', '#b8862c', '#fff2b0', '#4a300c')
IRON = Pal('#5a5f74', '#3e4256', '#8a90a8', '#14161f')
WOOD = Pal('#8a5a3a', '#663f27', '#b07d55', '#2a160a')


class ImpScout(Imp):
    """Fast aerial scout: oversized gold-ribbed wings, violet hide."""
    name = 'imp_scout'
    skin = Pal('#5a4a8a', '#3e3068', '#8a78b8', '#140c28')
    belly = Pal('#b8a8e0', '#8a78c0', '#e6dcff', '#2a2048')
    wing = Pal('#e0b040', '#a87a20', '#fff0a0', '#3a2408')
    membrane = Pal('#4a3a6a', '#2e2248', '#6a5a90', '#120a20')
    eye = hx('#ffe24a')
    wing_span = 1.4

    def extra_front(self, ctx, view, P, hand, hc):
        if view != 'up':
            x = 0 if view == 'down' else 3
            paint(ctx, lambda c: smooth_poly(c, [(x, -2), (x + 3.5, 2), (x, 6), (x - 3.5, 2)], tension=0.1), GOLD,
                  sh=0.8, hl=0.6, line=0.7)


class ImpRaider(Imp):
    """Ground brute: stubby wings, iron jaw-guard, gold shoulder studs."""
    name = 'imp_raider'
    skin = Pal('#c0504a', '#923636', '#e8806a', '#3a0c0c')
    belly = Pal('#e8b090', '#c08470', '#ffd8c0', '#4a2018')
    wing_span = 0.45
    body_scale = 1.3
    hover = 30

    def extra_front(self, ctx, view, P, hand, hc):
        if view == 'down':
            paint(ctx, lambda c: smooth_poly(c, [add(hc, (-8, 3)), add(hc, (8, 3)), add(hc, (6, 11)), add(hc, (0, 13)),
                                                 add(hc, (-6, 11))], tension=0.3), IRON, sh=1.5, hl=0.8, line=0.9)
            for sx in (-1, 1):
                paint(ctx, lambda c, sx=sx: ellipse(c, sx * 9, -5, 4.5, 3.5), GOLD, sh=1, hl=0.6, line=0.8)
        elif view == 'side':
            paint(ctx, lambda c: smooth_poly(c, [add(hc, (4, 3)), add(hc, (16, 3)), add(hc, (13, 11)), add(hc, (5, 10))],
                                             tension=0.3), IRON, sh=1.5, hl=0.8, line=0.9)
            paint(ctx, lambda c: ellipse(c, 1, -5, 4.5, 3.5), GOLD, sh=1, hl=0.6, line=0.8)


class ImpPyro(Imp):
    """Fire imp: crest of flame spikes on the back, spits bigger fireballs."""
    name = 'imp_pyro'
    skin = Pal('#e8743a', '#b84a24', '#ffa86a', '#4a1404')
    belly = Pal('#ffd27a', '#e8a040', '#fff0c0', '#5a3008')
    wing = Pal('#8a2a1a', '#5a160c', '#b84a2a', '#2a0604')
    membrane = Pal('#c83a1a', '#8a200c', '#f06a3a', '#3a0804')
    wing_span = 0.7
    eye = hx('#fff27a')

    def extra_back(self, ctx, view, P):
        t = P.get('tail', 0)
        n = 5
        for i in range(n):
            u = i / (n - 1)
            x = (u - 0.5) * 22 if view != 'side' else -10 + u * 10
            y = -34 + abs(u - 0.5) * 10 if view != 'side' else -30 + u * 4
            h = 14 + 4 * math.sin(t * math.tau * 2 + i)
            paint(ctx, lambda c, x=x, y=y, h=h: smooth_poly(c, [(x - 3.5, y + 6), (x, y - h), (x + 3.5, y + 6)], tension=0.2),
                  Pal('#ffb340', '#ff6a1a', '#fff0a0', '#5a1404'), sh=1.2, hl=0.8, line=0.8)
            radial_glow(ctx, x, y - h * 0.6, 6, hx('#ff8a2a'), 0.35)


class ImpHexer(Imp):
    """Caster: bone staff with a green soul orb, casts hex bolts."""
    name = 'imp_hexer'
    skin = Pal('#6a3a8a', '#4a2466', '#9a64b8', '#1a0828')
    belly = Pal('#c8a8e0', '#a080c0', '#efe0ff', '#2a1a3a')
    eye = hx('#7dffb0')
    fire = ('#9dffb0', '#3ad070', '#e8fff0', '#0a4a20')
    fire_glow = '#4aff8a'

    def extra_front(self, ctx, view, P, hand, hc):
        top = add(hand, (2, -24)) if view != 'up' else add(hand, (-2, -22))
        bot = add(hand, (-1, 10))
        stroke(ctx, lambda c: (c.move_to(*bot), c.line_to(*top)), hx('#2a1a10'), 3.6)
        stroke(ctx, lambda c: (c.move_to(*bot), c.line_to(*top)), hx('#e8dcc0'), 2.0)
        radial_glow(ctx, top[0], top[1] - 3, 12, hx('#4aff8a'), 0.55)
        paint(ctx, lambda c: ellipse(c, top[0], top[1] - 3, 4, 4), Pal('#9dffb0', '#3ad070', '#e8fff0', '#0a4a20'),
              sh=1, hl=0.8, line=0.7)


class ImpBomber(Imp):
    """Throws bombs: carries a lit black bomb, red hide, goggles."""
    name = 'imp_bomber'
    skin = Pal('#c83a3a', '#922428', '#f07060', '#3a0408')
    fire = ('#4a4a5a', '#2a2a36', '#8a8aa0', '#0a0a10')
    fire_glow = '#ffb340'

    def extra_front(self, ctx, view, P, hand, hc):
        b = add(hand, (0, 4))
        paint(ctx, lambda c: ellipse(c, b[0], b[1], 6, 6), Pal('#3a3a48', '#22222c', '#6a6a80', '#08080c'),
              sh=1.5, hl=1.2, line=0.8)
        fz = add(b, (3, -7))
        stroke(ctx, lambda c: (c.move_to(b[0] + 2, b[1] - 5), c.curve_to(b[0] + 3, b[1] - 7, fz[0], fz[1] + 1, *fz)),
               hx('#c8a060'), 1.2)
        flick = 0.6 + 0.4 * math.sin(P.get('tail', 0) * math.tau * 4)
        radial_glow(ctx, fz[0], fz[1], 6 * flick + 2, hx('#ffd25a'), 0.9)
        if view != 'up':
            stroke(ctx, lambda c: (c.move_to(*add(hc, (-11, -4))), c.line_to(*add(hc, (11, -4)))), hx('#3a2a20'), 2.2)


class ImpHowler(Imp):
    """Shrieker: slate hide, huge green eyes, spiked collar; its cast is a sonic burst."""
    name = 'imp_howler'
    skin = Pal('#4a5468', '#323a4c', '#6e7a90', '#10141c')
    belly = Pal('#8a96aa', '#6a7488', '#b0bccc', '#1a202a')
    eye = hx('#7dff4a')
    wing_span = 0.75
    body_scale = 1.15
    fire = ('#c8ffb0', '#7dff4a', '#ffffff', '#1a4a08')
    fire_glow = '#7dff4a'

    def extra_front(self, ctx, view, P, hand, hc):
        if view == 'up':
            return
        cy = hc[1] + 12
        for i in range(5):
            x = (i - 2) * 4.5 if view == 'down' else -4 + i * 2.5
            paint(ctx, lambda c, x=x: smooth_poly(c, [(x - 2, cy), (x, cy + 5), (x + 2, cy)], tension=0.1), IRON,
                  sh=0.5, hl=0.4, line=0.6)


class VelkaFlamebeak(Imp):
    """Boss: harpy-demon queen of the cliffs - flame wings, beak, feather crest."""
    name = 'velka_flamebeak'
    skin = Pal('#c8384a', '#922236', '#f0706a', '#3a0410')
    belly = Pal('#ffc07a', '#e09050', '#fff0c8', '#5a2a08')
    wing = Pal('#ffb340', '#d07a1a', '#fff0a0', '#4a2004')
    membrane = Pal('#ff7a2a', '#d04a14', '#ffb070', '#4a1004')
    eye = hx('#fff27a')
    wing_span = 1.6
    FW, FH, OX, OY = 160, 160, 80, 144

    def extra_front(self, ctx, view, P, hand, hc):
        beak = Pal('#f0c860', '#b8862c', '#fff2b0', '#4a300c')
        if view == 'down':
            paint(ctx, lambda c: smooth_poly(c, [add(hc, (-4, 3)), add(hc, (4, 3)), add(hc, (0, 11))], tension=0.2), beak,
                  sh=1, hl=0.6, line=0.8)
        elif view == 'side':
            paint(ctx, lambda c: smooth_poly(c, [add(hc, (11, 0)), add(hc, (22, 5)), add(hc, (12, 7))], tension=0.2), beak,
                  sh=1, hl=0.6, line=0.8)
        for i, a in enumerate((-30, 0, 30)):
            base = add(hc, (0, -13))
            tip = add(base, vec(180 + a, 16))
            paint(ctx, lambda c, tip=tip, base=base: smooth_poly(c, [add(base, (-3, 0)), tip, add(base, (3, 0))], tension=0.3),
                  Pal('#ff7a2a', '#d04a14', '#ffd080', '#4a1004'), sh=1, hl=0.8, line=0.8)


class ThornmawAlpha(Imp):
    """Boss: wingless thorn-backed demon beast with an iron jaw."""
    name = 'thornmaw_alpha'
    skin = Pal('#6a3a4a', '#4a2434', '#9a5a6a', '#1a0810')
    belly = Pal('#b07a7a', '#8a5a5a', '#d8a8a8', '#2a1414')
    eye = hx('#ff7a2a')
    wing_span = 0
    body_scale = 1.45
    hover = 34
    FW, FH, OX, OY = 160, 160, 80, 144

    def extra_back(self, ctx, view, P):
        for i in range(6):
            u = i / 5
            x = (u - 0.5) * 30 if view != 'side' else -14 + u * 16
            y = -10 - math.sin(u * math.pi) * 10
            paint(ctx, lambda c, x=x, y=y: smooth_poly(c, [(x - 3, y + 4), (x + (2 if view == 'side' else 0), y - 13), (x + 3, y + 4)],
                                                       tension=0.15), Pal('#f2e2c0', '#c9ab84', '#ffffff', '#5b4127'),
                  sh=1, hl=0.6, line=0.8)

    def extra_front(self, ctx, view, P, hand, hc):
        bone = Pal('#f2e2c0', '#c9ab84', '#ffffff', '#5b4127')
        sides = (-1, 1) if view != 'side' else (-1,)
        for sx in sides:
            for k, (dx, dy, l) in enumerate(((10, -6, 12), (13, 0, 9))):
                bx, by = sx * dx, dy
                ang = 180 + sx * (40 + k * 25)
                tip = add((bx, by), vec(ang, l))
                paint(ctx, lambda c, bx=bx, by=by, tip=tip: smooth_poly(c, [(bx - 2.5, by), tip, (bx + 2.5, by)], tension=0.15),
                      bone, sh=1, hl=0.6, line=0.8)
        if view == 'up':
            for i in range(5):
                y = -6 + i * 4
                paint(ctx, lambda c, y=y: smooth_poly(c, [(-3, y + 3), (0, y - 7), (3, y + 3)], tension=0.1), bone,
                      sh=0.8, hl=0.5, line=0.7)
        elif view == 'down':
            for sx in (-1, 1):
                paint(ctx, lambda c, sx=sx: smooth_poly(c, [add(hc, (sx * 5, 5)), add(hc, (sx * 3, 12)), add(hc, (sx * 1.5, 5))],
                                                        tension=0.1), bone, sh=0.5, hl=0.4, line=0.7)


LOTE1_IMPS = [ImpScout(), ImpRaider(), ImpPyro(), ImpHexer(), ImpBomber(), ImpHowler(), VelkaFlamebeak(), ThornmawAlpha()]
