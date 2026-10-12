"""Etapa 3 demons (desert / mines / swamp / peaks) on the animated Imp rig. Imported via demons._late()."""
from __future__ import annotations
import math
import demons as D
import demons_lote1 as L1
from core import Pal, paint, flat, stroke, ellipse, capsule, smooth_poly, hx, radial_glow

Imp = D.Imp
add, vec = D.add, D.vec
GOLD = Pal('#f0c860', '#b8862c', '#fff2b0', '#4a300c')
BONEP = Pal('#f2e2c0', '#c9ab84', '#ffffff', '#5b4127')


class SandImp(Imp):
    name = 'sand_imp'
    skin = Pal('#c8884a', '#a0642c', '#e8b070', '#4a2808')
    belly = Pal('#f0d4a0', '#d0a870', '#fff0d0', '#5a3a18')
    wing = Pal('#8a4a2a', '#5e2e18', '#b86a40', '#2a1006')
    membrane = Pal('#e0a060', '#b87a3a', '#f8c888', '#5a3010')
    eye = hx('#4aff9a')
    fire = ('#fff0a0', '#ffb340', '#ffffff', '#a04a0a')

    def extra_front(self, ctx, view, P, hand, hc):
        wrap = Pal('#d6453d', '#a52c33', '#f27a5f', '#5a1418')
        if view == 'up':
            paint(ctx, lambda c: smooth_poly(c, [add(hc, (-13, -8)), add(hc, (13, -8)), add(hc, (11, 0)), add(hc, (-11, 0))], tension=0.3), wrap, sh=1, hl=0.6, line=0.8)
        elif view == 'down':
            paint(ctx, lambda c: smooth_poly(c, [add(hc, (-13, -2)), add(hc, (13, -2)), add(hc, (13, 3)), add(hc, (-13, 3))], tension=0.2), wrap, sh=1, hl=0.6, line=0.8)
            paint(ctx, lambda c: smooth_poly(c, [add(hc, (6, 2)), add(hc, (12, 14)), add(hc, (7, 12)), add(hc, (3, 4))], tension=0.3), wrap, sh=0.8, hl=0.5, line=0.7)
        else:
            paint(ctx, lambda c: smooth_poly(c, [add(hc, (-11, -4)), add(hc, (10, -4)), add(hc, (11, 2)), add(hc, (-11, 2))], tension=0.2), wrap, sh=1, hl=0.6, line=0.8)
            paint(ctx, lambda c: smooth_poly(c, [add(hc, (-10, 0)), add(hc, (-20, 10)), add(hc, (-14, 12)), add(hc, (-8, 3))], tension=0.3), wrap, sh=0.8, hl=0.5, line=0.7)


class SandWraith(L1.SpiritCorrupt):
    name = 'sand_wraith'
    skin = Pal('#d8a860', '#b08040', '#f8d890', '#4a3010')
    belly = Pal('#fff0c8', '#e8c890', '#ffffff', '#5a4020')
    wing = Pal('#ffd27a', '#e0a040', '#fff4c0', '#5a3a10')
    membrane = Pal('#e8b868', '#c08a38', '#ffe0a0', '#5a3a10')
    eye = hx('#fff0c8')
    fire = ('#fff0c8', '#ffd27a', '#ffffff', '#6a4010')
    fire_glow = '#ffd27a'

    def extra_back(self, ctx, view, P):
        radial_glow(ctx, 0, -4, 34, hx('#ffd27a'), 0.28)


class ScorpionDemon(Imp):
    """Chapter-4 boss: carapace demon with giant pincers and an arched stinger tail."""
    name = 'scorpion_demon'
    skin = Pal('#8a3a28', '#62241a', '#b8604a', '#2a0c06')
    belly = Pal('#d8a070', '#b07a48', '#f8d0a0', '#4a2a10')
    eye = hx('#ff4a2a')
    wing_span = 0
    body_scale = 1.45
    hover = 34
    FW, FH, OX, OY = 160, 160, 80, 144
    fire = ('#ff8a5a', '#d02a1a', '#ffd0b8', '#4a0a04')
    fire_glow = '#ff5a2a'

    def extra_back(self, ctx, view, P):
        t = P.get('tail', 0)
        sway = math.sin(t * math.tau) * 3
        pts = [(0, 16), (-6, 26), (-14, 24), (-18, 8), (-14, -12), (-4, -28 + sway), (8, -32 + sway)] if view != 'side' else [(-8, 14), (-20, 20), (-28, 4), (-26, -14), (-14, -30 + sway), (-2, -32 + sway)]
        stroke(ctx, lambda c: smooth_poly(c, pts, closed=False), self.skin.line, 8)
        stroke(ctx, lambda c: smooth_poly(c, pts, closed=False), self.skin.base, 5.4)
        tip = pts[-1]
        paint(ctx, lambda c: smooth_poly(c, [(tip[0] - 3, tip[1] + 2), (tip[0] + 10, tip[1] + 6), (tip[0] - 1, tip[1] - 6)], tension=0.1), BONEP, sh=0.8, hl=0.5, line=0.8)

    def extra_front(self, ctx, view, P, hand, hc):
        sides = (-1, 1) if view != 'side' else (1,)
        for sx in sides:
            base = (sx * 12, -2) if view != 'side' else (6, 0)
            open_ = 14 + 10 * abs(math.sin(P.get('flap', 0) * 1.5))
            tip = (base[0] + sx * 18, base[1] + 10)
            for k in (-1, 1):
                paint(ctx, lambda c, sx=sx, base=base, tip=tip, k=k, open_=open_: smooth_poly(
                    c, [(base[0], base[1] + 2), (tip[0] + sx * 2, tip[1] + k * open_ * 0.3 - 4), (tip[0] + sx * 8, tip[1] + k * open_ * 0.5), (tip[0], tip[1] + 4)], tension=0.2),
                    Pal('#a84a30', '#7a2e1c', '#d07a5a', '#2a0c06'), sh=1.2, hl=0.8, line=0.9)


class MineImp(Imp):
    name = 'mine_imp'
    skin = Pal('#6a7a98', '#4a5874', '#92a4c4', '#141a28')
    belly = Pal('#c0cce0', '#98a8c4', '#eef4ff', '#2a3448')
    wing = Pal('#3a3a4a', '#22222e', '#5a5a70', '#0a0a10')
    membrane = Pal('#5a5a78', '#3e3e58', '#7e7e9c', '#16161e')
    eye = hx('#ffe24a')
    wing_span = 0.6
    body_scale = 1.1

    def extra_front(self, ctx, view, P, hand, hc):
        helmet = Pal('#e8c030', '#b08a10', '#fff0a0', '#4a3800')
        paint(ctx, lambda c: smooth_poly(c, [add(hc, (-12, -4)), add(hc, (-10, -14)), add(hc, (0, -17)), add(hc, (10, -14)), add(hc, (12, -4))], tension=0.4),
              helmet, sh=1.5, hl=1, line=0.9)
        if view != 'up':
            radial_glow(ctx, hc[0] + (0 if view == 'down' else 6), hc[1] - 12, 14, hx('#fff0a0'), 0.7)
            flat(ctx, lambda c: ellipse(c, hc[0] + (0 if view == 'down' else 6), hc[1] - 12, 3, 3), hx('#ffffff'))
        if view != 'down':
            ang = -30
        else:
            ang = 20
        a = add(hand, vec(ang + 180, 2))
        top = add(hand, vec(ang + 180, 18))
        stroke(ctx, lambda c: (c.move_to(*hand), c.line_to(*top)), hx('#2a1a10'), 3)
        stroke(ctx, lambda c: (c.move_to(*hand), c.line_to(*top)), hx('#a07a50'), 1.8)
        paint(ctx, lambda c: smooth_poly(c, [add(top, (-9, 3)), add(top, (0, -5)), add(top, (9, 3)), add(top, (0, 0))], tension=0.1),
              Pal('#8a96b0', '#5e6a88', '#b8c4dc', '#1a2034'), sh=1, hl=0.6, line=0.8)


class EmberGolem(Imp):
    """Chapter-5 boss: living slag with glowing magma cracks and molten fists."""
    name = 'ember_golem'
    skin = Pal('#4a3e44', '#2e262c', '#6e6068', '#0e0a0c')
    belly = Pal('#ff8a2a', '#d04a14', '#ffd27a', '#4a1004')
    eye = hx('#ffb340')
    wing_span = 0
    body_scale = 1.7
    hover = 34
    FW, FH, OX, OY = 160, 160, 80, 144
    fire = ('#fff0a0', '#ff8a2a', '#ffffff', '#a02a04')
    fire_glow = '#ff6a1a'
    horn = Pal('#4a3e44', '#2e262c', '#6e6068', '#0e0a0c')

    def extra_front(self, ctx, view, P, hand, hc):
        pulse = 0.6 + 0.4 * math.sin(P.get('tail', 0) * math.tau * 2)
        glow = hx('#ffb340')
        for pts in (((-6, -2), (-3, 6), (-7, 12), (-3, 18)), ((6, 0), (4, 8), (8, 14)), ((-10, 18), (-4, 22), (-8, 28))):
            if view == 'up':
                continue
            stroke(ctx, lambda c, pts=pts: smooth_poly(c, list(pts), closed=False), (1, 0.4, 0.05, 1), 3.2, 0.5 * pulse)
            stroke(ctx, lambda c, pts=pts: smooth_poly(c, list(pts), closed=False), glow, 1.5, 0.95 * pulse)
        radial_glow(ctx, hand[0], hand[1], 12, hx('#ff6a1a'), 0.6 * pulse)
        flat(ctx, lambda c: ellipse(c, hand[0], hand[1], 4, 4), hx('#ffd27a'), 0.9)
        if view != 'up':
            radial_glow(ctx, hc[0], hc[1] - 2, 16, hx('#ff8a2a'), 0.35 * pulse)


class WitchImp(L1.ImpHexer):
    name = 'witch_imp'
    skin = Pal('#6a9a52', '#4a7a38', '#98c47a', '#16300c')
    belly = Pal('#d8e8a8', '#b0c880', '#f4ffd0', '#2a3a14')
    eye = hx('#ff7ae8')
    fire = ('#d8a8ff', '#a050e8', '#f4e8ff', '#3a0a6a')
    fire_glow = '#b060ff'

    def extra_front(self, ctx, view, P, hand, hc):
        super().extra_front(ctx, view, P, hand, hc)
        hat = Pal('#3a2a5a', '#241840', '#5a4488', '#0c0818')
        paint(ctx, lambda c: smooth_poly(c, [add(hc, (-17, -10)), add(hc, (-6, -14)), add(hc, (-2, -34)), add(hc, (10, -42)), add(hc, (6, -14)), add(hc, (17, -10)), add(hc, (0, -6))], tension=0.2),
              hat, sh=1.5, hl=1, line=0.9)
        paint(ctx, lambda c: smooth_poly(c, [add(hc, (-9, -13)), add(hc, (9, -13)), add(hc, (9, -10)), add(hc, (-9, -10))], tension=0.1), GOLD, sh=0.6, hl=0.4, line=0.6)


class BogWraith(L1.SpiritCorrupt):
    name = 'bog_wraith'
    skin = Pal('#4a6a48', '#324e32', '#6c9068', '#101e10')
    belly = Pal('#a8d090', '#80a868', '#d4f4b8', '#1e3a16')
    wing = Pal('#9aff6a', '#5ac83a', '#e8ffc0', '#14380a')
    membrane = Pal('#6a8a50', '#46663a', '#90b070', '#142010')
    eye = hx('#e8ffc0')
    fire = ('#d8ffa0', '#7aff4a', '#ffffff', '#1a5a0a')
    fire_glow = '#7aff4a'

    def extra_back(self, ctx, view, P):
        radial_glow(ctx, 0, -4, 34, hx('#9aff6a'), 0.3)


class FrostImp(Imp):
    name = 'frost_imp'
    skin = Pal('#7ab8e8', '#4a88c0', '#b0e0ff', '#102a4a')
    belly = Pal('#e0f4ff', '#b0d8f0', '#ffffff', '#2a4a68')
    wing = Pal('#bfe8f8', '#7ab8dc', '#f4fdff', '#1a4a6a')
    membrane = Pal('#a8d8f4', '#78b0d8', '#e0f4ff', '#1a4a6a')
    horn = Pal('#e0f8ff', '#a8d8f0', '#ffffff', '#2a5a7a')
    eye = hx('#2a5aff')
    fire = ('#c8f4ff', '#5ac8ff', '#ffffff', '#0a3a6a')
    fire_glow = '#5ac8ff'
    wing_span = 1.1

    def extra_back(self, ctx, view, P):
        radial_glow(ctx, 0, -6, 30, hx('#9ae8ff'), 0.2)


class IceDemon(Imp):
    """Chapter-7 boss: frost demon lord with crystal wings and an ice-shard crown."""
    name = 'ice_demon'
    skin = Pal('#5a8ac8', '#3a62a0', '#8ab4f0', '#0c1c3a')
    belly = Pal('#d8f0ff', '#a8d0f0', '#ffffff', '#2a4a70')
    wing = Pal('#bfe8f8', '#7ab8dc', '#f4fdff', '#1a4a6a')
    membrane = Pal('#8ac8f0', '#5a98d0', '#c8ecff', '#14407a')
    horn = Pal('#e8fbff', '#a8d8f4', '#ffffff', '#2a5a7a')
    eye = hx('#ffffff')
    fire = ('#e8fbff', '#5ac8ff', '#ffffff', '#0a3a6a')
    fire_glow = '#7ad8ff'
    wing_span = 1.5
    body_scale = 1.5
    hover = 40
    FW, FH, OX, OY = 160, 160, 80, 144

    def extra_front(self, ctx, view, P, hand, hc):
        for i, a in enumerate((-40, -20, 0, 20, 40)):
            base = add(hc, (0, -13))
            tip = add(base, vec(180 + a, 14 + (6 if i == 2 else 0)))
            paint(ctx, lambda c, tip=tip, base=base: smooth_poly(c, [add(base, (-3, 0)), tip, add(base, (3, 0))], tension=0.05),
                  Pal('#d8f4ff', '#8ac8f0', '#ffffff', '#1a4a6a'), sh=0.8, hl=0.8, line=0.8)
        radial_glow(ctx, 0, 6, 26, hx('#7ad8ff'), 0.25)


REGION_IMPS = [SandImp(), SandWraith(), ScorpionDemon(), MineImp(), EmberGolem(), WitchImp(), BogWraith(), FrostImp(), IceDemon()]


class AshWraith(L1.SpiritCorrupt):
    name = 'ash_wraith'
    skin = Pal('#6a4a4a', '#4a3030', '#9a7070', '#1e1010')
    belly = Pal('#d8a090', '#b07868', '#f4d0c0', '#3a1a14')
    wing = Pal('#ff6a3a', '#c8280a', '#ffb070', '#4a0a04')
    membrane = Pal('#8a3a2a', '#5a2018', '#b8604a', '#2a0c08')
    eye = hx('#ffb340')
    fire = ('#ffd27a', '#ff6a1a', '#ffffff', '#8a1a04')
    fire_glow = '#ff6a1a'

    def extra_back(self, ctx, view, P):
        radial_glow(ctx, 0, -4, 36, hx('#ff6a1a'), 0.26)


REGION_IMPS.append(AshWraith())
