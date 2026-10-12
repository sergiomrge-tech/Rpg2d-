"""Procedural chibi-anime humanoid rig: 3 views (front/back/side-left), posed from joint angles."""
from __future__ import annotations
import math
from dataclasses import dataclass
from pix import Canvas, Part

FW = FH = 64
CX = 32
GROUND = 58


@dataclass
class Look:
    skin: str = '#f6c9a0'
    hair: str = '#2f6bff'
    hair_style: str = 'spiky'
    eyes: str = '#ffb020'
    top: str = '#e9eefb'
    trim: str = '#2f6bff'
    pants: str = '#2b3350'
    boots: str = '#6b3f2a'
    scarf: str | None = '#e8453c'
    cape: str | None = None
    hat: str | None = None
    hat_color: str = '#5a3aa0'
    beard: str | None = None
    fem: bool = False
    ears: str | None = None
    tail: str | None = None
    armor: bool = False
    metal: str = '#cdd8ee'
    weapon: str = 'sword'
    scale: float = 1.0
    name: str = 'kai'


@dataclass
class Pose:
    bob: int = 0
    lean: float = 0.0
    head_dy: int = 0
    torso_squash: float = 1.0
    leg_l: float = 0.0
    leg_r: float = 0.0
    lift_l: float = 0.0
    lift_r: float = 0.0
    knee_l: float = 0.0
    knee_r: float = 0.0
    arm_l: float = 0.0
    arm_r: float = 0.0
    elbow_l: float = 0.0
    elbow_r: float = 0.0
    sway: float = 0.0
    eyes: str = 'open'
    mouth: str = 'neutral'
    weapon_ang: float | None = None
    weapon_len: float = 17
    weapon_grip: str = 'r'
    glow: float = 0.0
    crouch: int = 0


def joint(x, y, ang_deg, length, facing=1):
    a = math.radians(ang_deg)
    return x + math.sin(a) * length * facing, y + math.cos(a) * length


class Rig:
    def __init__(self, look: Look):
        self.L = look

    def parts(self, c: Canvas):
        L = self.L
        P = {}
        def add(name, col, rank=0, **kw):
            P[name] = c.part(Part(name, col, rank, **kw))
        add('shadow', '#000000', -5, flat=True)
        add('skin', L.skin, 5)
        add('skin_far', L.skin, 1)
        add('hair', L.hair, 7)
        add('hair_back', L.hair, 1)
        add('hair_hi', L.hair, 8, flat=True)
        add('hair_lo', L.hair, 7, flat=True)
        add('top', L.top, 4)
        add('top_far', L.top, 2)
        add('trim', L.trim, 5)
        add('pants', L.pants, 3)
        add('pants_far', L.pants, 1)
        add('boots', L.boots, 4)
        add('boots_far', L.boots, 2)
        add('iris', L.eyes, 9, flat=True)
        add('iris_dk', L.eyes, 9, flat=True)
        add('eye_w', '#f4f2ff', 9, flat=True)
        add('lash', L.hair, 10, flat=True)
        add('pupil', '#140a24', 10, flat=True)
        add('spark', '#ffffff', 11, flat=True)
        add('blush', '#ff7a98', 9, flat=True)
        add('mouth', '#9a3a4a', 9, flat=True)
        add('belt', '#8a5a2a', 5)
        add('metal', L.metal, 8)
        add('metal_dk', L.metal, 6)
        add('hilt', '#c9a050', 8)
        add('scarf', L.scarf or '#ffffff', 6)
        add('cape', L.cape or '#ffffff', 1)
        add('hat', L.hat_color, 9)
        add('hat_trim', '#f2c94c', 10)
        add('beard', L.beard or '#ffffff', 8)
        add('ears', L.ears or '#ffffff', 6)
        add('ears_in', '#ffb0c0', 7, flat=True)
        add('tail', L.tail or '#ffffff', 1)
        add('glow', '#9ae8ff', 12, flat=True)
        return P

    def draw(self, view: str, pose: Pose) -> Canvas:
        c = Canvas(FW, FH)
        P = self.parts(c)
        if view == 'down':
            self.front(c, P, pose, back=False)
        elif view == 'up':
            self.front(c, P, pose, back=True)
        else:
            self.side(c, P, pose)
        return c

    def hat_front(self, c, P, hx, hy, view):
        L = self.L
        if not L.hat:
            return
        if L.hat == 'wizard':
            c.ellipse(P['hat'], hx, hy - 6.5, 14.5, 3.2)
            c.poly(P['hat'], [(hx - 8, hy - 7), (hx + 7, hy - 7), (hx + 3, hy - 17), (hx + 9, hy - 22), (hx + 1, hy - 20), (hx - 4, hy - 16)])
            c.rect(P['hat_trim'], hx - 8.5, hy - 9, hx + 8, hy - 7.2)
        elif L.hat == 'cap':
            c.ellipse(P['hat'], hx, hy - 6.5, 11.5, 5)
            if view != 'back':
                c.ellipse(P['hat'], hx, hy - 3.3, 12, 1.8)
        elif L.hat == 'band':
            c.rect(P['hat'], hx - 10, hy - 4.6, hx + 10, hy - 2.6)
            if view == 'front':
                c.ellipse(P['hat_trim'], hx, hy - 3.6, 2.2, 2.2)
        elif L.hat == 'straw':
            c.ellipse(P['hat'], hx, hy - 5.5, 16, 3.8)
            c.ellipse(P['hat'], hx, hy - 8.8, 8.5, 5)
        elif L.hat == 'crown':
            c.poly(P['hat'], [(hx - 8, hy - 6), (hx - 8, hy - 12), (hx - 4, hy - 8), (hx, hy - 13), (hx + 4, hy - 8), (hx + 8, hy - 12), (hx + 8, hy - 6)])

    # ------------------------------------------------------------ FRONT / BACK
    def front(self, c: Canvas, P, p: Pose, back: bool):
        L = self.L
        cx = CX + p.lean
        b = p.bob + p.crouch
        hip_y = 43 + p.crouch
        sh_y = 29 + b
        c.ellipse(P['shadow'], CX, GROUND + 0.5, 11, 3)
        if L.cape and not back:
            c.poly(P['cape'], [(cx - 9, sh_y), (cx + 9, sh_y), (cx + 12 + p.sway * 2, hip_y + 8), (cx - 12 + p.sway * 2, hip_y + 9)])
        hy = 16.5 + b + p.head_dy
        self.hair_behind(c, P, cx, hy, back, p)
        legs = []
        for side, sx in (('l', -1), ('r', 1)):
            sw = getattr(p, 'leg_' + side)
            lift = getattr(p, 'lift_' + side)
            hx = cx + sx * 3.4
            fy = GROUND - 1.0 - lift + sw * 2.2 + p.crouch * 0.3
            fx = hx + sx * (0.8 + abs(sw) * 0.3)
            legs.append((sw, sx, hx, fx, fy, lift))
        legs.sort(key=lambda t: t[0] if not back else -t[0])
        for sw, sx, hx, fx, fy, lift in legs:
            far = (sw < 0) if not back else (sw > 0)
            pa, bo = (P['pants_far'], P['boots_far']) if far else (P['pants'], P['boots'])
            kneex, kneey = (hx + fx) / 2 + sx * 0.6, (hip_y + fy) / 2 - lift * 0.15
            c.capsule(pa, hx, hip_y, kneex, kneey, 5.2, 4.8)
            c.capsule(pa, kneex, kneey, fx, fy - 3.2, 4.8, 4.4)
            c.ellipse(bo, fx, fy - 1.3, 3.4, 2.9)
            c.rect(bo, fx - 3.0, fy - 3.8, fx + 3.0, fy - 1.8)
            if not back:
                c.ellipse(bo, fx, fy + 0.2, 3.6, 1.6)
        tw_top, tw_bot = 7.2, 5.8
        ty0, ty1 = sh_y, hip_y + 1
        c.poly(P['top'], [(cx - tw_top, ty0), (cx + tw_top, ty0), (cx + tw_bot, ty1), (cx - tw_bot, ty1)])
        if L.fem:
            c.poly(P['top'], [(cx - 6, ty1 - 3), (cx + 6, ty1 - 3), (cx + 8.5, ty1 + 3.5), (cx - 8.5, ty1 + 3.5)])
        c.rect(P['belt'], cx - tw_bot - 0.4, ty1 - 3, cx + tw_bot + 0.4, ty1 - 1.4)
        if not back:
            c.rect(P['hilt'], cx - 1.2, ty1 - 3.1, cx + 1.2, ty1 - 1.3)
            c.poly(P['trim'], [(cx - 2.2, ty0), (cx + 2.2, ty0), (cx + 1.0, ty1 - 3), (cx - 1.0, ty1 - 3)])
            if L.armor:
                c.rect(P['trim'], cx - tw_top, ty0, cx + tw_top, ty0 + 2)
        else:
            c.rect(P['trim'], cx - tw_top, ty0, cx + tw_top, ty0 + 1.4)
            if L.cape:
                c.poly(P['cape'], [(cx - 8.5, sh_y), (cx + 8.5, sh_y), (cx + 12 + p.sway * 2, hip_y + 10), (cx - 12 + p.sway * 2, hip_y + 11)])
        for side, sx in (('l', -1), ('r', 1)):
            a = getattr(p, 'arm_' + side)
            e = getattr(p, 'elbow_' + side)
            shx, shy = cx + sx * 7.6, sh_y + 1.2
            ex, ey = joint(shx, shy, 6 + a, 7.5, sx)
            hxp, hyp = joint(ex, ey, 6 + a + e, 7.0, sx)
            c.capsule(P['top'], shx, shy, ex, ey, 4.6, 4.2)
            c.capsule(P['skin'], ex + (hxp - ex) * 0.25, ey + (hyp - ey) * 0.25, hxp, hyp, 3.6, 3.2)
            c.ellipse(P['skin'], hxp, hyp + 0.4, 2.0, 2.0)
            if p.glow > 0:
                c.ellipse(P['glow'], hxp, hyp + 0.4, 2.4 + p.glow, 2.4 + p.glow)
            if p.weapon_ang is not None and side == p.weapon_grip and not back:
                self.weapon(c, P, hxp, hyp, p, facing=sx)
        if back and p.weapon_ang is None and L.weapon == 'sword':
            c.line(P['metal_dk'], cx - 6, sh_y + 3, cx + 6, hip_y + 2, 1.6)
            c.line(P['hilt'], cx - 7, sh_y + 1.5, cx - 5, sh_y + 4, 1.8)
        c.rect(P['skin'], cx - 2.2, sh_y - 2.5, cx + 2.2, sh_y + 1)
        if L.scarf:
            self.scarf(c, P, cx, sh_y, p, back)
        self.head_front(c, P, cx, hy, p, back)
        self.hat_front(c, P, cx, hy, 'back' if back else 'front')

    def head_front(self, c, P, cx, hy, p: Pose, back: bool):
        L = self.L
        if L.ears:
            for sx in (-1, 1):
                ex = cx + sx * 7.2
                c.poly(P['ears'], [(ex - 2.8, hy - 6), (ex + 2.8, hy - 6), (ex + sx * 1.0, hy - 14.5 - abs(p.sway) * 0.6)])
                if not back:
                    c.poly(P['ears_in'], [(ex - 1.2, hy - 6.8), (ex + 1.2, hy - 6.8), (ex + sx * 0.4, hy - 11.2)])
        H = P['hair']
        if back:
            c.ellipse(P['skin'], cx, hy + 1.2, 9.6, 9.3)
            self.hair_cap(c, P, cx, hy, p, 'back')
            return
        # hair mass (skull) first, then face on top, then fringe
        c.ellipse(H, cx, hy - 0.4, 11.4, 10.2)
        c.rect(H, cx - 11.4, hy - 0.4, cx + 11.4, hy + 5.5)
        self.spikes(c, P, cx, hy, L.hair_style, False, p)
        face_top = hy - 1.5 if L.hair_style == 'bald' else hy + 0.2
        c.ellipse(P['skin'], cx, hy + 3.9, 8.9, 7.7)
        c.ellipse(P['skin'], cx, hy + 6.3, 7.0, 5.9)
        if L.hair_style == 'bald':
            c.ellipse(P['skin'], cx, hy - 0.4, 11.4, 10.2)
        if not L.ears:
            c.ellipse(P['skin'], cx - 9.6, hy + 3.6, 1.4, 2.0)
            c.ellipse(P['skin'], cx + 9.6, hy + 3.6, 1.4, 2.0)
        c.ellipse(P['blush'], cx - 6.4, hy + 9.4, 1.8, 0.9)
        c.ellipse(P['blush'], cx + 6.4, hy + 9.4, 1.8, 0.9)
        self.eyes_front(c, P, cx, hy, p)
        c.rect(P['skin_far'], cx - 0.5, hy + 9.0, cx + 0.5, hy + 9.8)
        my = hy + 11.1
        m = p.mouth
        if m == 'open':
            c.ellipse(P['mouth'], cx, my, 1.6, 1.4)
        elif m == 'shout':
            c.ellipse(P['mouth'], cx, my + 0.2, 2.4, 2.0)
            c.rect(P['eye_w'], cx - 1.6, my - 1.2, cx + 1.6, my - 0.4)
        elif m == 'smile':
            c.line(P['mouth'], cx - 2, my - 0.4, cx - 0.8, my + 0.5, 0.9)
            c.line(P['mouth'], cx - 0.8, my + 0.5, cx + 0.8, my + 0.5, 0.9)
            c.line(P['mouth'], cx + 0.8, my + 0.5, cx + 2, my - 0.4, 0.9)
        else:
            c.line(P['mouth'], cx - 1.3, my, cx + 1.3, my, 0.9)
        if L.beard:
            c.blob(P['beard'], [(cx - 7.5, hy + 5), (cx - 5, hy + 12), (cx, hy + 15.5), (cx + 5, hy + 12), (cx + 7.5, hy + 5), (cx + 3, hy + 8.5), (cx - 3, hy + 8.5)])
        self.fringe(c, P, cx, hy, p)

    def eyes_front(self, c, P, cx, hy, p: Pose):
        ec = hy + 6.5
        for sx in (-1, 1):
            ex = cx + sx * 4.7
            if p.eyes == 'closed':
                c.line(P['lash'], ex - 2.6, ec + 1.0, ex + 2.6, ec + 1.0, 1.0)
                continue
            if p.eyes == 'hurt':
                c.line(P['lash'], ex - 2.4, ec - 1.8, ex + 2.4, ec + 1.8, 1.0)
                c.line(P['lash'], ex - 2.4, ec + 1.8, ex + 2.4, ec - 1.8, 1.0)
                continue
            h = 3.7 if p.eyes == 'wide' else 3.3
            c.ellipse(P['eye_w'], ex, ec, 2.8, h)
            c.ellipse(P['iris_dk'], ex + sx * 0.1, ec + 0.3, 2.3, h - 0.2)
            c.ellipse(P['iris'], ex + sx * 0.1, ec + 1.3, 2.0, h - 1.4)
            c.ellipse(P['pupil'], ex + sx * 0.1, ec + 0.5, 0.95, 1.5)
            c.rect(P['spark'], ex - 1.9 + (0.5 if sx > 0 else 0), ec - 2.4, ex - 0.3 + (0.5 if sx > 0 else 0), ec - 0.9)
            c.rect(P['spark'], ex + 0.8, ec + 1.6, ex + 1.8, ec + 2.5)
            c.line(P['lash'], ex - 2.9, ec - 3.0, ex + 2.9, ec - 3.2, 1.05)
            c.line(P['lash'], ex + sx * 2.8, ec - 3.1, ex + sx * 3.8, ec - 3.7, 0.85)

    def hair_behind(self, c, P, cx, hy, back, p):
        L = self.L
        st = L.hair_style
        sw = p.sway * 1.6
        if st in ('long', 'elder'):
            c.blob(P['hair_back'], [(cx - 11.5, hy - 2), (cx - 12.5, hy + 12), (cx - 10 + sw, hy + 24), (cx + 10 + sw, hy + 24), (cx + 12.5, hy + 12), (cx + 11.5, hy - 2)])
        elif st == 'bob':
            c.blob(P['hair_back'], [(cx - 11.5, hy - 2), (cx - 12, hy + 8), (cx - 9.5, hy + 13), (cx + 9.5, hy + 13), (cx + 12, hy + 8), (cx + 11.5, hy - 2)])
        elif st == 'twin':
            for sx in (-1, 1):
                x0 = cx + sx * 12
                c.blob(P['hair_back'], [(x0 - 3, hy), (x0 + 3, hy), (x0 + sx * 4.5 + sw * sx, hy + 12), (x0 + sx * 3.5 + sw * 1.6, hy + 21), (x0 - sx * 1 + sw * 1.6, hy + 22), (x0 - sx * 3, hy + 11)])
        elif st == 'ponytail':
            if back:
                c.blob(P['hair'], [(cx - 3, hy + 2), (cx + 3, hy + 2), (cx + 5 + sw, hy + 14), (cx + 1 + sw * 1.5, hy + 22), (cx - 4 + sw, hy + 13)])
            else:
                c.blob(P['hair_back'], [(cx + 9, hy - 6), (cx + 15 + sw, hy + 2), (cx + 14 + sw * 1.4, hy + 14), (cx + 10 + sw, hy + 8)])

    def hair_cap(self, c, P, cx, hy, p, view):
        L = self.L
        st = L.hair_style
        H, Hh = P['hair'], P['hair_hi']
        if st == 'bald':
            return
        c.ellipse(H, cx, hy + 0.8, 11.4, 10.6)
        c.rect(H, cx - 9.8, hy + 4, cx + 9.8, hy + 8.5)
        if st in ('long', 'elder'):
            c.rect(H, cx - 9.8, hy + 4, cx + 9.8, hy + 22 + p.sway)
        self.spikes(c, P, cx, hy, st, True, p)
        c.ellipse(Hh, cx - 3.5, hy - 5, 4.6, 1.5)
        for dx in (-5, -1.5, 2, 5.5):
            c.line(P['hair_lo'], cx + dx, hy - 3 + abs(dx) * 0.3, cx + dx * 1.2, hy + 6.5, 0.75)

    def fringe(self, c, P, cx, hy, p):
        L = self.L
        st = L.hair_style
        H, Hh, Hl = P['hair'], P['hair_hi'], P['hair_lo']
        if st == 'bald':
            return
        by = hy - 1.0
        if st in ('spiky', 'messy'):
            pts = [(cx - 10.8, hy - 3), (cx - 10, by + 3), (cx - 7.2, by - 0.8), (cx - 4.6, by + 3.2), (cx - 1.4, by - 1.2), (cx + 1.4, by + 3.0), (cx + 4.2, by - 0.8), (cx + 7.0, by + 2.8), (cx + 10, by + 2.6), (cx + 10.8, hy - 3)]
        elif st in ('short', 'ponytail'):
            pts = [(cx - 10.8, hy - 3), (cx - 9.8, by + 3.4), (cx - 5, by + 0.4), (cx - 1, by + 3.0), (cx + 2.5, by + 0.4), (cx + 6, by + 2.8), (cx + 9.8, by + 2.4), (cx + 10.8, hy - 3)]
        elif st in ('long', 'bob', 'twin'):
            pts = [(cx - 10.9, hy - 3), (cx - 10.6, by + 8.5), (cx - 8.6, by + 3.4), (cx - 6, by + 0.6), (cx - 2.5, by + 3.2), (cx - 0.3, by - 0.6), (cx + 2.5, by + 3.2), (cx + 6, by + 0.6), (cx + 8.6, by + 3.4), (cx + 10.6, by + 8.5), (cx + 10.9, hy - 3)]
        else:
            pts = [(cx - 10.8, hy - 3), (cx - 10, by + 4.5), (cx - 6, by + 1), (cx - 1, by + 2.4), (cx + 5, by + 0.4), (cx + 10, by + 4.5), (cx + 10.8, hy - 3)]
        c.poly(H, pts)
        c.line(Hl, cx - 6.0, hy - 6.0, cx - 7.5, by + 0.4, 0.9)
        c.line(Hl, cx + 5.5, hy - 6.2, cx + 7.0, by + 0.4, 0.9)
        c.line(Hl, cx + 0.2, hy - 7.4, cx, by - 0.4, 0.8)
        c.ellipse(Hh, cx - 3.8, hy - 5.8, 4.2, 1.3)
        c.ellipse(Hh, cx + 4.8, hy - 5.2, 2.2, 0.9)

    def spikes(self, c, P, cx, hy, st, back, p):
        H = P['hair']
        if st == 'spiky':
            sp = [(-9, -3, -12, -11, -4, -9), (-4, -8, -6, -16, 0, -9), (0, -8.5, 4, -16.5, 6, -8), (5, -8, 12, -13, 9.5, -3), (-10.5, 0, -13.5, -4, -10, -5.5)]
            for a, b, x2, y2, x3, y3 in sp:
                c.poly(H, [(cx + a, hy + b), (cx + x2, hy + y2), (cx + x3, hy + y3)])
        elif st == 'messy':
            for dx, dy, l in ((-8, -7, 5), (-3, -9, 6), (3, -9, 5), (8, -6, 5), (0, -9, 4)):
                c.poly(H, [(cx + dx - 2.5, hy + dy + 1), (cx + dx + 2.5, hy + dy + 1), (cx + dx + 1, hy + dy - l)])
        elif st == 'ponytail' and not back:
            c.ellipse(P['trim'], cx + 9.2, hy - 5.6, 1.4, 1.4)

    def scarf(self, c, P, cx, sh_y, p: Pose, back):
        sw = p.sway
        c.poly(P['scarf'], [(cx - 6.4, sh_y - 2.0), (cx + 6.4, sh_y - 2.0), (cx + 7.0, sh_y + 1.6), (cx - 7.0, sh_y + 1.6)])
        base_x = cx + (5 if not back else -5)
        c.poly(P['scarf'], [(base_x - 2.2, sh_y + 1), (base_x + 2.2, sh_y + 1), (base_x + 3.4 + sw * 3, sh_y + 10), (base_x - 1.2 + sw * 3, sh_y + 11)])
        c.poly(P['scarf'], [(base_x - 1.6, sh_y + 8), (base_x + 3.8 + sw * 3.5, sh_y + 9), (base_x + 5.5 + sw * 4, sh_y + 13), (base_x + sw * 3.5, sh_y + 13)])

    def weapon(self, c, P, hx, hy, p: Pose, facing=1):
        L = self.L
        ang = p.weapon_ang or 0
        ln = p.weapon_len
        if L.weapon == 'sword':
            tx, ty = joint(hx, hy, ang, ln, facing)
            bx, by = joint(hx, hy, ang, -3.0, facing)
            c.line(P['metal_dk'], hx, hy, tx, ty, 3.4)
            c.line(P['metal'], hx, hy, tx, ty, 2.0)
            c.line(P['spark'], hx, hy - 0.2, tx, ty - 0.2, 0.9)
            gx0, gy0 = joint(hx, hy, ang + 90, 3.4, facing)
            gx1, gy1 = joint(hx, hy, ang - 90, 3.4, facing)
            c.line(P['hilt'], gx0, gy0, gx1, gy1, 1.6)
            c.line(P['hilt'], hx, hy, bx, by, 1.8)
        elif L.weapon == 'staff':
            tx, ty = joint(hx, hy, ang, ln + 4, facing)
            bx, by = joint(hx, hy, ang, -10, facing)
            c.line(P['belt'], bx, by, tx, ty, 1.6)
            c.ellipse(P['glow'], tx, ty, 2.8, 2.8)
            c.ellipse(P['spark'], tx - 0.6, ty - 0.6, 1.0, 1.0)

    # ------------------------------------------------------------ SIDE (facing left)
    def side(self, c: Canvas, P, p: Pose):
        L = self.L
        f = -1
        cx = CX + p.lean
        b = p.bob + p.crouch
        hip_y = 43 + p.crouch
        sh_y = 29 + b
        c.ellipse(P['shadow'], CX, GROUND + 0.5, 11, 3)
        hy = 16.5 + b + p.head_dy
        if L.cape:
            c.poly(P['cape'], [(cx + 2, sh_y), (cx + 5, sh_y + 1), (cx + 11 + p.sway * 3, hip_y + 8), (cx + 5 + p.sway * 3, hip_y + 10)])
        if L.tail:
            c.blob(P['tail'], [(cx + 4, hip_y), (cx + 11, hip_y - 4 + p.sway * 2), (cx + 15, hip_y - 10 + p.sway * 3), (cx + 11, hip_y - 6), (cx + 6, hip_y + 3)])

        def leg(sw, lift, knee, far):
            hx = cx + 0.5 + (0.8 if far else -0.4)
            kx, ky = joint(hx, hip_y, sw, 7.2, f)
            a2 = sw - knee - max(0, lift) * 4.5
            fx, fy = joint(kx, ky, a2, 7.0, f)
            fy = min(fy, GROUND - 3.0)
            pa, bo = (P['pants_far'], P['boots_far']) if far else (P['pants'], P['boots'])
            c.capsule(pa, hx, hip_y, kx, ky, 5.2, 4.8)
            c.capsule(pa, kx, ky, fx, fy, 4.8, 4.2)
            c.ellipse(bo, fx + f * 1.2, fy + 1.6, 4.2, 2.6)
            c.rect(bo, fx - 2.4, fy - 1.0, fx + 2.4, fy + 1.2)

        def arm(a, e, far):
            shx, shy = cx + (0.8 if far else -0.4), sh_y + 1.5
            ex, ey = joint(shx, shy, a, 7.2, f)
            hxp, hyp = joint(ex, ey, a + e, 6.6, f)
            c.capsule(P['top_far'] if far else P['top'], shx, shy, ex, ey, 4.6, 4.2)
            sk = P['skin_far'] if far else P['skin']
            c.capsule(sk, ex + (hxp - ex) * 0.2, ey + (hyp - ey) * 0.2, hxp, hyp, 3.4, 3.0)
            c.ellipse(sk, hxp, hyp + 0.3, 2.0, 2.0)
            if p.glow > 0 and not far:
                c.ellipse(P['glow'], hxp, hyp + 0.3, 2.4 + p.glow, 2.4 + p.glow)
            return hxp, hyp
        leg(p.leg_r, p.lift_r, p.knee_r, True)
        far_hand = arm(p.arm_r, p.elbow_r, True)
        if p.weapon_ang is not None and p.weapon_grip == 'r':
            self.weapon(c, P, far_hand[0], far_hand[1], p, facing=f)
        tw = 6.2
        c.poly(P['top'], [(cx - tw, sh_y), (cx + tw, sh_y), (cx + tw - 0.6, hip_y + 1), (cx - tw + 0.6, hip_y + 1)])
        if L.fem:
            c.poly(P['top'], [(cx - 5.8, hip_y - 3), (cx + 5.8, hip_y - 3), (cx + 8, hip_y + 3.5), (cx - 8, hip_y + 3.5)])
        c.rect(P['belt'], cx - tw, hip_y - 3, cx + tw, hip_y - 1.4)
        c.rect(P['trim'], cx - tw, sh_y, cx + tw, sh_y + 1.5)
        if L.weapon == 'sword' and p.weapon_ang is None:
            c.line(P['metal_dk'], cx + 4, sh_y + 2, cx - 4, hip_y + 4, 1.5)
        leg(p.leg_l, p.lift_l, p.knee_l, False)
        c.rect(P['skin'], cx - 2.0, sh_y - 2.5, cx + 2.2, sh_y + 1)
        if L.scarf:
            sw = p.sway
            c.poly(P['scarf'], [(cx - 6.5, sh_y - 1.8), (cx + 6.2, sh_y - 1.8), (cx + 6.5, sh_y + 2.4), (cx - 6.5, sh_y + 2.4)])
            c.poly(P['scarf'], [(cx + 4, sh_y), (cx + 7, sh_y + 0.5), (cx + 15 + sw * 4, sh_y + 4 + sw * 2), (cx + 14 + sw * 4, sh_y + 8 + sw * 2), (cx + 6, sh_y + 4)])
            c.poly(P['scarf'], [(cx + 8, sh_y + 3), (cx + 16 + sw * 5, sh_y + 8 + sw * 3), (cx + 12 + sw * 4, sh_y + 11 + sw * 3)])
        self.head_side(c, P, cx, hy, p)
        self.hat_front(c, P, cx, hy, 'side')
        near_hand = arm(p.arm_l, p.elbow_l, False)
        if p.weapon_ang is not None and p.weapon_grip == 'l':
            self.weapon(c, P, near_hand[0], near_hand[1], p, facing=f)

    def head_side(self, c, P, cx, hy, p: Pose):
        L = self.L
        st = L.hair_style
        sw = p.sway * 1.6
        if st in ('long', 'elder'):
            c.blob(P['hair_back'], [(cx + 2, hy - 7), (cx + 11, hy - 3), (cx + 12 + sw, hy + 12), (cx + 8 + sw, hy + 24), (cx - 2, hy + 22), (cx - 1, hy + 6)])
        elif st == 'bob':
            c.blob(P['hair_back'], [(cx + 2, hy - 7), (cx + 11, hy - 3), (cx + 12, hy + 8), (cx + 7, hy + 14), (cx - 2, hy + 12)])
        elif st == 'twin':
            c.blob(P['hair_back'], [(cx + 7, hy - 3), (cx + 13, hy + 1), (cx + 14 + sw * 1.4, hy + 12), (cx + 11 + sw * 1.5, hy + 22), (cx + 6 + sw, hy + 20), (cx + 8, hy + 8)])
        elif st == 'ponytail':
            c.blob(P['hair_back'], [(cx + 6, hy - 6), (cx + 14 + sw, hy), (cx + 16 + sw * 1.5, hy + 12), (cx + 12 + sw * 1.5, hy + 22), (cx + 9 + sw, hy + 10), (cx + 6, hy + 2)])
        if L.ears:
            c.poly(P['ears'], [(cx + 1.5, hy - 6.5), (cx + 7, hy - 6.5), (cx + 5.5, hy - 14.5 - abs(p.sway) * 0.6)])
            c.poly(P['ears_in'], [(cx + 3, hy - 7), (cx + 5.8, hy - 7), (cx + 5.2, hy - 11.5)])
        H, Hh, Hl = P['hair'], P['hair_hi'], P['hair_lo']
        if st != 'bald':
            c.ellipse(H, cx + 2.2, hy - 0.6, 10.8, 10.0)
            c.rect(H, cx + 1, hy - 0.6, cx + 12, hy + 6.5)
            if st == 'spiky':
                for a2, b2, x2, y2, x3, y3 in ((-5, -8, -9, -15, -1, -9), (-1, -8.5, 1, -17, 4, -8), (3, -8, 10, -14, 8.5, -4), (6.5, -4, 14, -6, 9.5, 0)):
                    c.poly(H, [(cx + a2, hy + b2), (cx + x2, hy + y2), (cx + x3, hy + y3)])
            elif st == 'messy':
                for dx, dy, l in ((-5, -8, 5), (0, -9, 6), (6, -7, 5)):
                    c.poly(H, [(cx + dx - 2.5, hy + dy + 1), (cx + dx + 2.5, hy + dy + 1), (cx + dx + 1, hy + dy - l)])
        else:
            c.ellipse(P['skin'], cx + 1, hy - 0.4, 10, 10)
        c.ellipse(P['skin'], cx - 1.0, hy + 4.0, 8.2, 7.4)
        c.ellipse(P['skin'], cx - 2.5, hy + 6.0, 6.2, 5.8)
        c.ellipse(P['skin'], cx - 9.2, hy + 5.8, 1.1, 1.0)
        c.ellipse(P['skin_far'], cx + 3.0, hy + 3.4, 1.5, 2.0)
        ex, ec = cx - 5.6, hy + 6.5
        if p.eyes == 'closed':
            c.line(P['lash'], ex - 2.4, ec + 1.0, ex + 2.2, ec + 1.0, 1.0)
        elif p.eyes == 'hurt':
            c.line(P['lash'], ex - 2.2, ec - 1.8, ex + 2.2, ec + 1.8, 1.0)
            c.line(P['lash'], ex - 2.2, ec + 1.8, ex + 2.2, ec - 1.8, 1.0)
        else:
            c.ellipse(P['eye_w'], ex, ec, 2.5, 3.3)
            c.ellipse(P['iris_dk'], ex - 0.5, ec + 0.3, 2.0, 3.1)
            c.ellipse(P['iris'], ex - 0.5, ec + 1.3, 1.8, 1.9)
            c.ellipse(P['pupil'], ex - 0.6, ec + 0.5, 0.9, 1.4)
            c.rect(P['spark'], ex - 1.8, ec - 2.4, ex - 0.4, ec - 0.9)
            c.line(P['lash'], ex - 2.7, ec - 3.0, ex + 2.5, ec - 3.1, 1.05)
            c.line(P['lash'], ex - 2.7, ec - 3.0, ex - 3.7, ec - 3.6, 0.85)
        c.ellipse(P['blush'], cx - 4.6, hy + 9.6, 1.6, 0.8)
        my = hy + 11.1
        if p.mouth in ('open', 'shout'):
            c.ellipse(P['mouth'], cx - 6.4, my, 1.4, 1.3)
        elif p.mouth == 'smile':
            c.line(P['mouth'], cx - 7.4, my - 0.3, cx - 5.0, my + 0.5, 0.9)
        else:
            c.line(P['mouth'], cx - 7.2, my, cx - 5.2, my, 0.9)
        if L.beard:
            c.blob(P['beard'], [(cx - 7, hy + 6), (cx - 4, hy + 13), (cx + 1, hy + 15), (cx + 4, hy + 8), (cx - 3, hy + 8.5)])
        if st != 'bald':
            fy = hy - 1.0
            c.poly(H, [(cx - 8.2, hy - 3), (cx - 9.4, fy + 2.6), (cx - 5.5, fy + 0.2), (cx - 2.5, fy + 3.2), (cx + 1, fy + 0.2), (cx + 5, hy - 3)])
            c.line(Hl, cx + 3, hy - 6, cx + 6, hy + 4, 0.9)
            c.line(Hl, cx - 2, hy - 7, cx - 4, fy, 0.8)
            c.ellipse(Hh, cx - 2, hy - 6, 4, 1.3)
