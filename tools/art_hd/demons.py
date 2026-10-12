"""Demon enemies (HD cartoon). Each demon: draw(ctx, view, pose) + anim table + pose fn."""
from __future__ import annotations
import math
import cairo
from core import (Pal, paint, flat, stroke, ellipse, capsule, smooth_poly, rot, hx, shade, radial_glow, keys,
                  ease_out, ease_in)

TAU = math.tau


def vec(a, l):
    r = math.radians(a)
    return math.sin(r) * l, math.cos(r) * l


def add(p, q):
    return p[0] + q[0], p[1] + q[1]


def slit_eye(ctx, x, y, rx, ry, iris, angry=True, mode='open', look=0.0):
    if mode == 'closed':
        stroke(ctx, lambda c: (c.move_to(x - rx, y), c.line_to(x + rx, y + 0.8)), hx('#2a0f18'), 1.2)
        return
    radial_glow(ctx, x, y, rx * 2.6, iris, 0.35)
    paint(ctx, lambda c: ellipse(c, x, y, rx, ry), Pal(iris, shade(iris, -0.18), shade(iris, 0.15), hx('#2a0f18')),
          sh=0.8, hl=0.5, line=0.8, grad=False)
    flat(ctx, lambda c: ellipse(c, x + look * rx * 0.3, y + 0.2, rx * 0.22, ry * 0.8), hx('#1a0710'))
    flat(ctx, lambda c: ellipse(c, x - rx * 0.4, y - ry * 0.4, rx * 0.22, rx * 0.22), hx('#ffffff'), 0.9)
    if angry:
        stroke(ctx, lambda c: (c.move_to(x - rx * 1.3, y - ry * 1.1 - 0.6), c.line_to(x + rx * 1.2, y - ry * 0.45)),
               hx('#2a0f18'), 1.4)


# ====================================================================== IMP
class Imp:
    name = 'imp'
    FW, FH, OX, OY = 144, 144, 72, 128
    skin = Pal('#d8424f', '#a42645', '#ff7a6e', '#4a0d1e')
    belly = Pal('#f2a07a', '#d0705e', '#ffd0a8', '#5a1a20')
    wing = Pal('#6b2f6e', '#4a1d52', '#9b4c94', '#24092a')
    membrane = Pal('#a8457a', '#7c2c63', '#d470a0', '#3a0d2a')
    horn = Pal('#f2e2c0', '#c9ab84', '#ffffff', '#5b4127')
    claw = Pal('#2e1a2e', '#1a0d1a', '#5a3c5a', '#0c040c')
    eye = hx('#ffd23f')
    wing_span = 1.0          # 0 = wingless
    hover = 46
    fire = ('#ffd25a', '#ff8a2a', '#fff6c8', '#b23a10')
    fire_glow = '#ff8a2a'
    body_scale = 1.0         # chunkier body/head
    FW, FH, OX, OY = 144, 144, 72, 128
    ANIMS = {
        'idle': (10, 12, True, -1),
        'move': (8, 14, True, -1),
        'attack': (10, 16, False, 5),
        'cast': (10, 14, False, 6),
        'hurt': (5, 14, False, -1),
        'death': (10, 12, False, -1),
    }

    def pose(self, anim, t, view):
        P = dict(y=0.0, x=0.0, lean=0.0, flap=math.sin(t * TAU * 2), tail=t, arm_a=(25, 50), arm_b=(-25, -50),
                 mouth='grin', eyes='open', sq=1.0, rot=0.0, glow=0.0, alpha=1.0, legs=0.0)
        if view == 'side':
            P['arm_a'], P['arm_b'] = (40, 80), (20, 70)
        if anim == 'idle':
            P['y'] = -2.5 * math.sin(t * TAU * 2 + 0.6)
            P['legs'] = math.sin(t * TAU * 2 + 1.2)
        elif anim == 'move':
            P['flap'] = math.sin(t * TAU * 2)
            P['y'] = -3 * math.sin(t * TAU * 2 + 0.6)
            P['lean'] = 16 if view == 'side' else 0
            P['legs'] = 1
            P['tail'] = t * 1.5
        elif anim == 'attack':
            wind = keys(t, [(0, 0), (0.35, 1), (0.5, 0), (1, 0)])
            hit = keys(t, [(0, 0), (0.35, 0), (0.5, 1), (0.7, 1), (1, 0)])
            P['flap'] = math.sin(t * TAU * 3)
            P['mouth'] = 'open' if t > 0.4 else 'grin'
            if view == 'side':
                P['lean'] = -15 * wind + 28 * hit
                P['x'] = -5 * wind + 14 * hit
                P['arm_b'] = (20 - 140 * wind + 120 * hit, 70 - 150 * wind + 60 * hit)
                P['arm_a'] = (40 - 100 * wind + 70 * hit, 80 - 100 * wind + 40 * hit)
            else:
                s = 1 if view == 'down' else -1
                P['y'] = -4 * wind + 8 * hit * s
                P['sq'] = 1 + 0.08 * wind - 0.08 * hit
                P['arm_a'] = (25 + 120 * wind - 100 * hit, 50 + 120 * wind - 80 * hit)
                P['arm_b'] = (-25 - 120 * wind + 100 * hit, -50 - 120 * wind + 80 * hit)
        elif anim == 'cast':
            g = keys(t, [(0, 0), (0.5, 1), (0.65, 1), (0.75, 0), (1, 0)])
            P['glow'] = g
            P['mouth'] = 'open' if 0.55 < t < 0.8 else 'grin'
            P['y'] = -4 * g
            P['flap'] = math.sin(t * TAU * 2.5)
            if view == 'side':
                P['arm_b'] = (20 + 70 * g, 70 + 40 * g)
                P['arm_a'] = (40 + 60 * g, 80 + 40 * g)
                P['lean'] = -8 * g + keys(t, [(0, 0), (0.65, 0), (0.72, 18), (1, 0)])
            else:
                P['arm_a'] = (25 + 40 * g, 50 - 110 * g)
                P['arm_b'] = (-25 - 40 * g, -50 + 110 * g)
        elif anim == 'hurt':
            k = keys(t, [(0, 0), (0.2, 1), (1, 0)], ease=ease_out)
            P['eyes'] = 'closed' if k > 0.3 else 'open'
            P['mouth'] = 'open'
            P['lean'] = -20 * k if view == 'side' else 0
            P['x'] = -6 * k if view == 'side' else 0
            P['y'] = -4 * k * (1 if view == 'down' else -1) if view != 'side' else 0
            P['sq'] = 1 - 0.12 * k
            P['rot'] = 8 * k if view != 'side' else 0
        elif anim == 'death':
            P['eyes'] = 'closed'
            P['mouth'] = 'open'
            spin = keys(t, [(0, 0), (0.6, 1), (1, 1)], ease=ease_in)
            P['rot'] = 200 * spin * (-1 if view == 'side' else 1)
            P['y'] = keys(t, [(0, 0), (0.15, -8), (0.6, 30), (1, 30)])
            P['sq'] = keys(t, [(0, 1), (0.6, 0.85), (1, 0.4)])
            P['flap'] = math.sin(t * TAU * 1.2) * (1 - t)
            P['alpha'] = keys(t, [(0, 1), (0.6, 1), (1, 0)])
        return P

    # ------------------------------------------------------------------ drawing
    def wing_path(self, c, root, sx, flap, span=1.0, view='down'):
        """Bat wing: root at shoulder, finger bones radiating; flap -1..1 rotates and stretches."""
        a = -70 * sx - flap * 32 * sx
        k = (0.75 + 0.25 * (1 + flap) / 2) * span
        tip_len = [30 * k, 34 * k, 27 * k, 18 * k]
        angs = [a + sx * d for d in (0, 28, 58, 88)]
        tips = [add(root, vec(180 - an * -1 if False else 180 + an, l)) for an, l in zip(angs, tip_len)]
        return tips

    def draw_wing(self, ctx, root, sx, flap, far=False, span=1.0):
        # angles measured from 'up'; sx=+1 right wing, -1 left wing
        base = 180 - sx * (55 + flap * 35)
        lens = [33 * span, 35 * span, 27 * span, 17 * span]
        offs = [0, 26, 52, 80]
        tips = [add(root, vec(base - sx * o * -1 + 0 if False else base + sx * o, l)) for o, l in zip(offs, lens)]
        # membrane: scalloped edge between tips back to the body
        memb = self.membrane if not far else Pal(self.membrane.shadow, self.membrane.deep, self.membrane.base,
                                                 self.membrane.line)
        bone = self.wing if not far else Pal(self.wing.shadow, self.wing.deep, self.wing.base, self.wing.line)
        body_pt = add(root, (sx * -3, 14))

        def membrane(c):
            c.move_to(*root)
            c.line_to(*tips[0])
            for i in range(1, len(tips)):
                p0, p1 = tips[i - 1], tips[i]
                mx, my = (p0[0] + p1[0]) / 2, (p0[1] + p1[1]) / 2
                # scallop inward toward root
                ix, iy = mx + (root[0] - mx) * 0.28, my + (root[1] - my) * 0.28
                c.curve_to(ix, iy, ix, iy, *p1)
            ix, iy = (tips[-1][0] + body_pt[0]) / 2, (tips[-1][1] + body_pt[1]) / 2
            c.curve_to(ix + (root[0] - ix) * 0.3, iy + (root[1] - iy) * 0.3, ix, iy, *body_pt)
            c.close_path()
        paint(ctx, membrane, memb, sh=2.0, hl=0.8, line=0.9)
        for tp in tips:
            stroke(ctx, lambda c, tp=tp: (c.move_to(*root), c.line_to(*tp)), bone.line, 2.2)
            stroke(ctx, lambda c, tp=tp: (c.move_to(*root), c.line_to(*tp)), bone.base, 1.2)
        paint(ctx, lambda c: ellipse(c, tips[0][0], tips[0][1], 1.6, 1.6), self.claw, sh=0, hl=0.4, line=0.6)

    def draw_tail(self, ctx, base, dirx, phase, far=False):
        pts = []
        for i in range(9):
            u = i / 8
            x = base[0] + dirx * (u * 22)
            y = base[1] + u * 8 - math.sin(u * 3.0) * 10 + math.sin(phase * TAU + u * 4) * 3.5 * u
            pts.append((x, y))
        stroke(ctx, lambda c: smooth_poly(c, pts, closed=False), self.skin.line, 4.6)
        stroke(ctx, lambda c: smooth_poly(c, pts, closed=False), self.skin.shadow if far else self.skin.base, 2.8)
        tip = pts[-1]
        d = (pts[-1][0] - pts[-2][0], pts[-1][1] - pts[-2][1])
        ang = math.degrees(math.atan2(d[1], d[0]))
        ctx.save()
        ctx.translate(*tip)
        ctx.rotate(math.radians(ang))
        paint(ctx, lambda c: smooth_poly(c, [(-1, -1.5), (3, -5), (9, 0), (3, 5), (-1, 1.5)], tension=0.25),
              self.wing, sh=1.0, hl=0.6, line=0.9)
        ctx.restore()

    def draw_arm(self, ctx, sh, arm, sx, far=False):
        a1, a2 = arm
        el = add(sh, vec(a1, 7.5))
        hd = add(el, vec(a2, 7))
        skin = self.skin if not far else Pal(self.skin.shadow, self.skin.deep, self.skin.base, self.skin.line)
        paint(ctx, lambda c: (capsule(c, sh, el, 3.4, 2.8), capsule(c, el, hd, 2.8, 2.4)), skin, sh=1.0, hl=0.6)
        # claws
        for k in (-30, 0, 30):
            tip = add(hd, vec(a2 + k, 5))
            paint(ctx, lambda c, tip=tip: smooth_poly(c, [add(hd, vec(a2 + k + 70, 1.4)), tip,
                                                         add(hd, vec(a2 + k - 70, 1.4))], tension=0.0),
                  self.claw, sh=0, hl=0.4, line=0.5)
        paint(ctx, lambda c: ellipse(c, hd[0], hd[1], 3.0, 3.0), skin, sh=0.8, hl=0.5)
        return hd

    def draw_head(self, ctx, view, P, hc):
        sk = self.skin
        if view == 'side':
            # horns (far first)
            paint(ctx, lambda c: smooth_poly(c, [add(hc, (-6, -10)), add(hc, (-14, -21)), add(hc, (-11, -27)),
                                                 add(hc, (-4, -14))], tension=0.4),
                  Pal(self.horn.shadow, self.horn.deep, self.horn.base, self.horn.line), sh=1, hl=0.5, line=0.9)
            # ear
            paint(ctx, lambda c: smooth_poly(c, [add(hc, (-6, -3)), add(hc, (-19, -9)), add(hc, (-8, 3))], tension=0.2),
                  sk, sh=1.0, hl=0.6, line=0.9)

            def head(c):
                smooth_poly(c, [add(hc, p) for p in [(-11, -6), (-5, -14), (6, -13), (13, -5), (17, 1), (15, 4),
                                                     (14, 8), (8, 12), (-2, 12), (-10, 7)]], tension=0.5)
            paint(ctx, head, sk, sh=2.2, hl=1.2)
            paint(ctx, lambda c: smooth_poly(c, [add(hc, (0, -11)), add(hc, (8, -22)), add(hc, (15, -28)),
                                                 add(hc, (10, -18)), add(hc, (6, -10))], tension=0.4),
                  self.horn, sh=1.2, hl=0.7, line=0.9)
            slit_eye(ctx, hc[0] + 8, hc[1] - 2, 3.0, 3.6, self.eye, mode=P['eyes'], look=1)
            if P['mouth'] == 'open':
                paint(ctx, lambda c: smooth_poly(c, [add(hc, (5, 5)), add(hc, (15, 4)), add(hc, (11, 11)),
                                                     add(hc, (5, 9))], tension=0.3),
                      Pal('#5a0f22', '#3a0816', '#7a2033', '#1a0408'), sh=0.6, hl=0, line=0.8)
                for fx in (8, 12):
                    flat(ctx, lambda c, fx=fx: smooth_poly(c, [add(hc, (fx - 1.2, 4.6)), add(hc, (fx + 1.2, 4.6)),
                                                               add(hc, (fx, 7.4))], tension=0), hx('#ffffff'))
            else:
                stroke(ctx, lambda c: (c.move_to(*add(hc, (5, 6))), c.curve_to(*add(hc, (9, 9)), *add(hc, (12, 8)),
                                                                                *add(hc, (15, 4)))),
                       hx('#3a0816'), 1.1)
                flat(ctx, lambda c: smooth_poly(c, [add(hc, (11, 7.3)), add(hc, (13, 6.2)), add(hc, (12.4, 9))],
                                                tension=0), hx('#ffffff'))
            return
        back = view == 'up'
        # horns
        for sx in (-1, 1):
            paint(ctx, lambda c, sx=sx: smooth_poly(c, [add(hc, (sx * 6, -10)), add(hc, (sx * 13, -20)),
                                                        add(hc, (sx * 20, -27)), add(hc, (sx * 17, -16)),
                                                        add(hc, (sx * 12, -7))], tension=0.4),
                  self.horn, sh=1.2, hl=0.7, line=0.9)
        # ears
        for sx in (-1, 1):
            paint(ctx, lambda c, sx=sx: smooth_poly(c, [add(hc, (sx * 11, -3)), add(hc, (sx * 23, -9)),
                                                        add(hc, (sx * 12, 4))], tension=0.2), sk, sh=1.0, hl=0.6,
                  line=0.9)

        def head(c):
            smooth_poly(c, [add(hc, p) for p in [(-13, -4), (-9, -12), (0, -14.5), (9, -12), (13, -4), (12.5, 4),
                                                 (7, 10.5), (0, 12), (-7, 10.5), (-12.5, 4)]], tension=0.5)
        paint(ctx, head, sk, sh=2.2, hl=1.2)
        if back:
            stroke(ctx, lambda c: (c.move_to(*add(hc, (0, -12))), c.curve_to(*add(hc, (-1, -4)), *add(hc, (1, 4)),
                                                                              *add(hc, (0, 10)))),
                   sk.shadow, 1.2)
            return
        for sx in (-1, 1):
            slit_eye(ctx, hc[0] + sx * 5.6, hc[1] - 1, 3.4, 3.8, self.eye, mode=P['eyes'])
        if P['mouth'] == 'open':
            paint(ctx, lambda c: smooth_poly(c, [add(hc, (-6, 4)), add(hc, (6, 4)), add(hc, (4, 10)), add(hc, (-4, 10))],
                                             tension=0.35), Pal('#5a0f22', '#3a0816', '#7a2033', '#1a0408'),
                  sh=0.6, hl=0, line=0.8)
            for fx in (-3.5, 3.5):
                flat(ctx, lambda c, fx=fx: smooth_poly(c, [add(hc, (fx - 1.3, 4.3)), add(hc, (fx + 1.3, 4.3)),
                                                           add(hc, (fx, 7.4))], tension=0), hx('#ffffff'))
        else:
            stroke(ctx, lambda c: (c.move_to(*add(hc, (-6, 4.5))), c.curve_to(*add(hc, (-3, 8.5)), *add(hc, (3, 8.5)),
                                                                                *add(hc, (6.5, 4)))),
                   hx('#3a0816'), 1.1)
            for fx in (-3, 3):
                flat(ctx, lambda c, fx=fx: smooth_poly(c, [add(hc, (fx - 1.1, 6.6)), add(hc, (fx + 1.1, 6.4)),
                                                           add(hc, (fx, 9))], tension=0), hx('#ffffff'))

    def draw(self, ctx, view, P):
        if P['alpha'] < 1:
            ctx.push_group()
        ctx.save()
        ctx.translate(P['x'], P['y'] - self.hover)
        ctx.rotate(math.radians(P['rot'] + P['lean']))
        ctx.scale(1 / math.sqrt(P['sq']), P['sq'])
        ctx.scale(self.body_scale, self.body_scale)
        flap = P['flap']
        self.extra_back(ctx, view, P)
        hc = (0, -16)
        body_c = (0, 2)
        sk = self.skin
        if view == 'side':
            self.wing_span and self.draw_wing(ctx, (-3, -4), -1, flap, far=True, span=0.95 * self.wing_span)
            self.draw_tail(ctx, (-6, 10), -1, P['tail'])
            self.draw_arm(ctx, (-2, -3), P['arm_a'], 1, far=True)
            # legs
            for i, ph in enumerate((0, 1.4)):
                a = 10 + 20 * math.sin(P['legs'] + ph)
                kn = add((0 + i * 2, 11), vec(a, 6))
                ft = add(kn, vec(a - 30, 6))
                paint(ctx, lambda c, kn=kn, ft=ft, i=i: (capsule(c, (i * 2, 11), kn, 3.0, 2.4), capsule(c, kn, ft, 2.4, 2.0)),
                      sk if i else Pal(sk.shadow, sk.deep, sk.base, sk.line), sh=0.8, hl=0.4)

            def body(c):
                smooth_poly(c, [(-7, -6), (4, -7), (8, 0), (6, 10), (0, 14), (-7, 11), (-9, 2)], tension=0.5)
            paint(ctx, body, sk, sh=2.0, hl=1.0)
            paint(ctx, lambda c: smooth_poly(c, [(1, -4), (6, -2), (6, 8), (1, 12), (-2, 6)], tension=0.5), self.belly,
                  sh=1.0, hl=0.5, line=0)
            self.wing_span and self.draw_wing(ctx, (-5, -2), -1, flap * 0.9 + 0.1, span=0.9 * self.wing_span)
            self.draw_head(ctx, view, P, (2, -16))
            hd = self.draw_arm(ctx, (2, -2), P['arm_b'], 1)
            self.extra_front(ctx, view, P, hd, (2, -16))
            if P['glow'] > 0.02:
                self.fireball(ctx, add(hd, (6, -2)), P['glow'])
        else:
            back = view == 'up'
            if not back:
                self.draw_tail(ctx, (3, 10), 1, P['tail'])
                for sx in (-1, 1):
                    self.wing_span and self.draw_wing(ctx, (sx * 5, -4), sx, flap, span=self.wing_span)
            # legs
            for sx in (-1, 1):
                a = sx * (12 + 10 * math.sin(P['legs'] + sx))
                kn = add((sx * 4, 11), vec(a, 6))
                ft = add(kn, vec(a * 0.3, 5.5))
                paint(ctx, lambda c, kn=kn, ft=ft, sx=sx: (capsule(c, (sx * 4, 11), kn, 3.0, 2.4), capsule(c, kn, ft, 2.4, 2.0)),
                      sk, sh=0.8, hl=0.4)

            def body(c):
                smooth_poly(c, [(-9, -6), (0, -8), (9, -6), (10, 4), (6, 13), (0, 15), (-6, 13), (-10, 4)], tension=0.5)
            paint(ctx, body, sk, sh=2.0, hl=1.0)
            if not back:
                paint(ctx, lambda c: smooth_poly(c, [(-5, -3), (5, -3), (6, 7), (0, 12.5), (-6, 7)], tension=0.5),
                      self.belly, sh=1.0, hl=0.5, line=0)
            arms = []
            for sx, key in ((1, 'arm_a'), (-1, 'arm_b')):
                a1, a2 = P[key]
                if back:
                    a1, a2 = -a1, -a2
                arms.append(self.draw_arm(ctx, (sx * 8, -4), (a1, a2), sx))
            self.draw_head(ctx, view, P, hc)
            self.extra_front(ctx, view, P, arms[1], hc)
            if back:
                self.draw_tail(ctx, (-2, 10), -1, P['tail'])
                for sx in (-1, 1):
                    self.wing_span and self.draw_wing(ctx, (sx * 5, -4), sx, flap, span=self.wing_span)
            if P['glow'] > 0.02 and not back:
                mid = ((arms[0][0] + arms[1][0]) / 2, (arms[0][1] + arms[1][1]) / 2 + 3)
                self.fireball(ctx, mid, P['glow'])
        ctx.restore()
        if P['alpha'] < 1:
            ctx.pop_group_to_source()
            ctx.paint_with_alpha(P['alpha'])

    def extra_back(self, ctx, view, P):
        pass

    def extra_front(self, ctx, view, P, hand, hc):
        pass

    def fireball(self, ctx, p, g):
        radial_glow(ctx, p[0], p[1], 14 * g + 4, hx(self.fire_glow), 0.7 * g)
        paint(ctx, lambda c: ellipse(c, p[0], p[1], 4.5 * g + 1, 4.5 * g + 1), Pal(*self.fire), sh=1.2, hl=1.0, line=0.6)


class Grakk(Imp):
    """Chapter 1 boss: an elder imp chieftain (dark violet, gold horns, ember eyes)."""
    name = 'grakk'
    skin = Pal('#6a3a8a', '#482466', '#9a64b8', '#1a0828')
    belly = Pal('#c86a5a', '#9a4a44', '#f0a090', '#3a1014')
    wing = Pal('#2a1a3a', '#180e24', '#4a3460', '#08040e')
    membrane = Pal('#a8283a', '#7a1628', '#d85a6a', '#2a040c')
    horn = Pal('#f0c860', '#b8862c', '#fff2b0', '#4a300c')
    eye = hx('#ff7a2a')


DEMONS = [Imp(), Grakk()]


def _late():
    from demons_lote1 import LOTE1_IMPS
    DEMONS.extend(LOTE1_IMPS)
