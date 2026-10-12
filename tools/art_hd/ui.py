"""HUD textures (no boxes): medallion, curved gauges, orbs, dialogue band, ribbons, pills, vignette,
portraits and the icon sheet.  Output: unity/Assets/Resources/Sprites/Ui/"""
from __future__ import annotations
import math
import os
import cairo
import numpy as np
from PIL import Image
from scipy import ndimage
from core import (Frame, Pal, paint, flat, stroke, ellipse, capsule, smooth_poly, hx, shade, radial_glow,
                  outline_rgba, to_image)
from humanoid import Look, draw_head, default_pose
from build_npcs import LOOKS
from sheet import OUT, build

UI = os.path.join(OUT, 'Ui')
TAU = math.tau
GOLD = Pal('#f0c860', '#b8862c', '#fff2b0', '#4a300c')
DARK = (0.08, 0.05, 0.10, 1)


def save(fr: Frame, name, outline=None):
    img = fr.rgba()
    if outline:
        img = outline_rgba(img, hx('#1c1018'), outline)
    to_image(img).save(os.path.join(UI, name + '.png'), optimize=True)


def canvas(w, h):
    return Frame(w, h, w / 2, h / 2)


# ---------------------------------------------------------------- medallion
def medallion():
    f = canvas(300, 300)
    c = f.ctx
    # outer ring (thick gold band with engraved groove)
    def ring(cx):
        cx.new_sub_path()
        cx.arc(0, 0, 146, 0, TAU)
        cx.new_sub_path()
        cx.arc_negative(0, 0, 100, TAU, 0)
    c.set_fill_rule(cairo.FILL_RULE_EVEN_ODD)
    paint(c, ring, GOLD, sh=5, hl=3, line=2)
    stroke(c, lambda x: x.arc(0, 0, 123, 0, TAU), GOLD.shadow, 2.4)
    stroke(c, lambda x: x.arc(0, 0, 127, 0, TAU), GOLD.light, 1.0, 0.8)
    # leaf filigree around
    for i in range(16):
        a = i / 16 * TAU
        c.save()
        c.rotate(a)
        flat(c, lambda x: smooth_poly(x, [(0, -138), (7, -126), (0, -112), (-7, -126)], tension=0.4), GOLD.shadow, 0.9)
        flat(c, lambda x: smooth_poly(x, [(0, -135), (4, -126), (0, -116), (-4, -126)], tension=0.4), GOLD.light, 0.8)
        c.restore()
    # wings / crest on top
    for sx in (-1, 1):
        paint(c, lambda x, sx=sx: smooth_poly(x, [(sx * 20, -138), (sx * 70, -150), (sx * 110, -128), (sx * 74, -132),
                                                  (sx * 96, -112), (sx * 58, -122), (sx * 30, -112)], tension=0.35),
              GOLD, sh=2.5, hl=1.5, line=1.4)
    # gems at sides
    gem = Pal('#3fb0ff', '#1a6ac0', '#c8f0ff', '#0a2040')
    for a in (TAU * 0.25, TAU * 0.75):
        x, y = math.cos(a) * 123, math.sin(a) * 123
        paint(c, lambda cx, x=x, y=y: ellipse(cx, x, y, 9, 9), gem, sh=2.5, hl=2, line=1.2)
    # top crest gem
    paint(c, lambda x: smooth_poly(x, [(0, -158), (14, -140), (0, -120), (-14, -140)], tension=0.1),
          Pal('#ff4a5a', '#b81a30', '#ffc0c8', '#40060e'), sh=3, hl=2, line=1.5)
    # level plate at bottom
    paint(c, lambda x: ellipse(x, 0, 128, 30, 26), GOLD, sh=3, hl=2, line=1.8)
    paint(c, lambda x: ellipse(x, 0, 128, 23, 19), Pal('#3a1a40', '#24102a', '#5a3060', '#0c040e'), sh=3, hl=1, line=1)
    save(f, 'medallion', outline=1.2)


def arc_tex(name, r, w, fill_cols=None, track=False):
    """Ring band from cairo angle 180 (left) clockwise 240 deg, round caps."""
    f = canvas(440, 440)
    c = f.ctx
    a0, a1 = math.radians(180), math.radians(420)
    c.set_line_cap(cairo.LINE_CAP_BUTT)
    if track:
        stroke(c, lambda x: x.arc(0, 0, r, a0, a1), (0.05, 0.03, 0.08, 1), w + 6, 0.85)
        stroke(c, lambda x: x.arc(0, 0, r, a0, a1), (0.18, 0.12, 0.2, 1), w, 0.9)
        # gold edges
        stroke(c, lambda x: x.arc(0, 0, r + w / 2 + 2, a0, a1), GOLD.base, 1.6, 0.9)
        stroke(c, lambda x: x.arc(0, 0, r - w / 2 - 2, a0, a1), GOLD.shadow, 1.2, 0.8)
        # notches every 10%
        for i in range(1, 10):
            a = a0 + (a1 - a0) * i / 10
            stroke(c, lambda x, a=a: (x.move_to(math.cos(a) * (r - w / 2), math.sin(a) * (r - w / 2)),
                                      x.line_to(math.cos(a) * (r + w / 2), math.sin(a) * (r + w / 2))), (0, 0, 0, 1), 1.2, 0.5)
    else:
        lo, mid, hi = fill_cols
        g = cairo.RadialGradient(0, 0, r - w / 2, 0, 0, r + w / 2)
        g.add_color_stop_rgba(0, *hx(lo))
        g.add_color_stop_rgba(0.55, *hx(mid))
        g.add_color_stop_rgba(1, *hx(hi))
        c.save()
        c.set_source(g)
        c.set_line_width(w)
        c.arc(0, 0, r, a0, a1)
        c.stroke()
        c.restore()
        stroke(c, lambda x: x.arc(0, 0, r + w * 0.22, a0, a1), (1, 1, 1, 1), max(1.2, w * 0.18), 0.45)
        for i in range(1, 10):
            a = a0 + (a1 - a0) * i / 10
            stroke(c, lambda x, a=a: (x.move_to(math.cos(a) * (r - w / 2), math.sin(a) * (r - w / 2)),
                                      x.line_to(math.cos(a) * (r + w / 2), math.sin(a) * (r + w / 2))), (0, 0, 0, 1), 1.0, 0.25)
    save(f, name)


def orb():
    f = canvas(128, 128)
    c = f.ctx
    g = cairo.RadialGradient(-14, -18, 4, 0, 0, 56)
    g.add_color_stop_rgba(0, 0.32, 0.22, 0.42, 0.95)
    g.add_color_stop_rgba(1, 0.06, 0.03, 0.1, 0.95)
    c.save()
    c.set_source(g)
    c.arc(0, 0, 52, 0, TAU)
    c.fill()
    c.restore()
    c.set_fill_rule(cairo.FILL_RULE_EVEN_ODD)
    paint(c, lambda x: (x.new_sub_path(), x.arc(0, 0, 60, 0, TAU), x.new_sub_path(), x.arc_negative(0, 0, 51, TAU, 0)),
          GOLD, sh=2.5, hl=1.5, line=1.4)
    stroke(c, lambda x: x.arc(0, 0, 44, math.radians(200), math.radians(260)), (1, 1, 1, 1), 3, 0.35)
    for a in (0, 90, 180, 270):
        r = math.radians(a)
        paint(c, lambda x, r=r: ellipse(x, math.cos(r) * 56, math.sin(r) * 56, 4, 4), GOLD, sh=1, hl=1, line=1)
    save(f, 'orb', outline=1)
    f = canvas(128, 128)
    flat(f.ctx, lambda x: x.arc(0, 0, 52, 0, TAU), (0.02, 0.01, 0.04, 1), 0.72)
    save(f, 'orb_shade')


def soft(name, w, h, kind):
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    nx, ny = (xx + 0.5) / w * 2 - 1, (yy + 0.5) / h * 2 - 1
    if kind == 'smear':
        d = np.sqrt(nx ** 2 + ny ** 2)
        a = np.clip(1 - d, 0, 1) ** 1.6
        rgb = 0
    elif kind == 'vignette':
        d = np.sqrt((nx * 0.9) ** 2 + (ny * 1.0) ** 2)
        a = np.clip((d - 0.55) / 0.75, 0, 1) ** 1.8
        rgb = 0
    elif kind == 'band':
        t = (yy + 0.5) / h
        a = np.clip((t - 0.18) / 0.45, 0, 1) ** 1.2 * 0.82
        edge = np.clip(1 - np.abs(nx) ** 6, 0, 1)
        a = a * (0.55 + 0.45 * edge)
        rgb = 0
    img = np.zeros((h, w, 4), np.uint8)
    img[..., 3] = (a * 255).astype(np.uint8)
    im = Image.fromarray(img, 'RGBA')
    if kind == 'band':
        fr = Frame(w, h, w / 2, 0)
        c = fr.ctx
        y = 76
        stroke(c, lambda x: (x.move_to(-760, y), x.line_to(760, y)), GOLD.base, 2.2, 0.9)
        stroke(c, lambda x: (x.move_to(-640, y + 6), x.line_to(640, y + 6)), GOLD.shadow, 1.0, 0.7)
        for sx in (-1, 1):
            stroke(c, lambda x, sx=sx: (x.move_to(sx * 760, y), x.curve_to(sx * 800, y - 16, sx * 830, y + 10, sx * 812, y + 18)),
                   GOLD.base, 2.2, 0.9)
        paint(c, lambda x: smooth_poly(x, [(0, y - 12), (12, y), (0, y + 12), (-12, y)], tension=0.1), GOLD, sh=1.5, hl=1, line=1)
        deco = to_image(fr.rgba())
        im.alpha_composite(deco)
    im.save(os.path.join(UI, name + '.png'), optimize=True)


def flourish():
    f = canvas(512, 48)
    c = f.ctx
    for sx in (-1, 1):
        stroke(c, lambda x, sx=sx: (x.move_to(sx * 18, 0), x.curve_to(sx * 80, -4, sx * 160, 4, sx * 236, 0)), GOLD.base, 2.4)
        stroke(c, lambda x, sx=sx: (x.move_to(sx * 236, 0), x.curve_to(sx * 252, -12, sx * 230, -18, sx * 222, -8)), GOLD.base, 2)
        stroke(c, lambda x, sx=sx: (x.move_to(sx * 40, 6), x.curve_to(sx * 70, 14, sx * 100, 8, sx * 120, 4)), GOLD.shadow, 1.4)
    paint(c, lambda x: smooth_poly(x, [(0, -14), (14, 0), (0, 14), (-14, 0)], tension=0.1), GOLD, sh=2, hl=1.5, line=1.4)
    paint(c, lambda x: ellipse(x, 0, 0, 4, 4), Pal('#ff4a5a', '#b81a30', '#ffc0c8', '#40060e'), sh=1, hl=1, line=0.8)
    save(f, 'flourish', outline=0.8)


def nameplate():
    f = canvas(480, 70)
    red = Pal('#8a1e2e', '#5e1220', '#b8404e', '#2a060c')

    def ribbon(x):
        x.move_to(-232, 0)
        x.line_to(-206, -24)
        x.curve_to(-80, -28, 80, -28, 206, -24)
        x.line_to(232, 0)
        x.line_to(206, 24)
        x.curve_to(80, 20, -80, 20, -206, 24)
        x.close_path()
    paint(f.ctx, ribbon, red, sh=4, hl=2, line=1.6)
    stroke(f.ctx, lambda x: (x.move_to(-200, -18), x.curve_to(-80, -22, 80, -22, 200, -18)), GOLD.base, 1.8)
    stroke(f.ctx, lambda x: (x.move_to(-200, 18), x.curve_to(-80, 14, 80, 14, 200, 18)), GOLD.base, 1.8)
    save(f, 'nameplate', outline=1)


def pills():
    f = canvas(104, 16)
    paint(f.ctx, lambda x: capsule(x, (-44, 0), (44, 0), 6.5), Pal('#2a1a2e', '#180e1c', '#3e2a44', '#0a040c'),
          sh=1, hl=0.6, line=1.2)
    save(f, 'pill_track')
    f = canvas(98, 10)
    c = f.ctx
    g = cairo.LinearGradient(0, -5, 0, 5)
    g.add_color_stop_rgba(0, *hx('#ff8a7a'))
    g.add_color_stop_rgba(0.5, *hx('#e0393e'))
    g.add_color_stop_rgba(1, *hx('#9a1a2a'))
    c.set_source(g)
    capsule(c, (-44, 0), (44, 0), 4.5)
    c.fill()
    save(f, 'pill_fill')


# ---------------------------------------------------------------- portraits
def portrait(name, look, bg=('#5aa0d8', '#24406a')):
    f = canvas(256, 256)
    c = f.ctx
    c.save()
    c.arc(0, 0, 124, 0, TAU)
    c.clip()
    g = cairo.RadialGradient(-30, -50, 10, 0, 0, 150)
    g.add_color_stop_rgba(0, *hx(bg[0]))
    g.add_color_stop_rgba(1, *hx(bg[1]))
    c.set_source(g)
    c.paint()
    radial_glow(c, -40, -60, 90, (1, 1, 1, 1), 0.25)
    c.scale(3.0, 3.0)
    c.translate(0, 18)
    # shoulders
    paint(c, lambda x: smooth_poly(x, [(-30, 40), (-24, 16), (-10, 10), (10, 10), (24, 16), (30, 40)], tension=0.4),
          look.tunic, sh=3, hl=1.5, line=1)
    paint(c, lambda x: smooth_poly(x, [(-5, 9), (5, 9), (0, 20)], tension=0.1), look.shirt, sh=1, hl=0.5, line=0.8)
    if look.scarf_on:
        paint(c, lambda x: ellipse(x, 0, 11, 13, 5), look.scarf, sh=1.6, hl=0.9)
    P = default_pose()
    P['mouth'] = 'smile'
    draw_head(c, look, 'down', (0, -12), 0, P)
    c.restore()
    save(f, name)


def icon_draw(ctx, name):
    c = ctx
    if name == 'coin':
        for dx, dy in ((8, 10), (-6, 4), (2, -6)):
            paint(c, lambda x, dx=dx, dy=dy: ellipse(x, dx, dy, 17, 13), GOLD, sh=3, hl=2, line=1.6)
            stroke(c, lambda x, dx=dx, dy=dy: ellipse(x, dx, dy, 11, 8), GOLD.shadow, 1.4)
    elif name in ('potion', 'ether'):
        liquid = Pal('#ff4a5a', '#c01a30', '#ffb0b8', '#40060e') if name == 'potion' else Pal('#3fa8ff', '#1a5ac0', '#c0e8ff', '#081c40')
        glass = Pal('#e8f4ff', '#a8c0d8', '#ffffff', '#2a3a50')
        paint(c, lambda x: (x.new_sub_path(), x.arc(0, 10, 22, 0, TAU), x.rectangle(-8, -26, 16, 22)), glass, sh=2, hl=1, line=1.6)
        c.save()
        c.arc(0, 10, 19, 0, TAU)
        c.clip()
        paint(c, lambda x: x.rectangle(-30, 2, 60, 40), liquid, sh=4, hl=0, line=0)
        c.restore()
        flat(c, lambda x: ellipse(x, -8, 4, 4, 6), (1, 1, 1, 1), 0.7)
        paint(c, lambda x: x.rectangle(-10, -34, 20, 10), Pal('#a06a3a', '#7a4a24', '#c89060', '#2a160a'), sh=1.5, hl=1, line=1.2)
    elif name == 'horn':
        paint(c, lambda x: smooth_poly(x, [(-20, 26), (-6, 30), (8, 12), (16, -10), (14, -32), (4, -10), (-10, 8)], tension=0.4),
              Pal('#f2e2c0', '#c9ab84', '#ffffff', '#5b4127'), sh=4, hl=2, line=1.6)
        for y in (14, 2, -10):
            stroke(c, lambda x, y=y: (x.move_to(-6 + y * 0.3, y + 6), x.line_to(8 + y * 0.3, y + 2)), hx('#a88a64'), 1.4)
    elif name == 'ember':
        radial_glow(c, 0, 4, 34, hx('#ff6a1a'), 0.8)
        paint(c, lambda x: smooth_poly(x, [(0, -30), (14, -6), (18, 14), (0, 26), (-18, 14), (-14, -6)], tension=0.5),
              Pal('#ff8a2a', '#d0401a', '#ffe08a', '#4a0e04'), sh=4, hl=3, line=1.4)
        flat(c, lambda x: ellipse(x, 0, 10, 7, 9), hx('#fff4c0'))
    elif name == 'tome':
        paint(c, lambda x: smooth_poly(x, [(-24, -28), (22, -30), (24, 28), (-22, 30)], tension=0.05),
              Pal('#7a3aa8', '#52207a', '#a868d8', '#1e0830'), sh=4, hl=2, line=1.6)
        paint(c, lambda x: smooth_poly(x, [(-24, 22), (24, 20), (24, 28), (-22, 30)], tension=0.05),
              Pal('#f6ecd4', '#d8c8a8', '#ffffff', '#4a3a28'), sh=1, hl=0.5, line=1)
        paint(c, lambda x: ellipse(x, 0, -4, 9, 9), GOLD, sh=1.5, hl=1, line=1.2)
        radial_glow(c, 0, -4, 16, hx('#ffb340'), 0.6)
    elif name == 'skill_sword':
        c.save()
        c.rotate(math.radians(-45))
        paint(c, lambda x: smooth_poly(x, [(-4, 16), (-4, -28), (0, -36), (4, -28), (4, 16)], tension=0.05),
              Pal('#dfe8f2', '#9aa9bf', '#ffffff', '#3b4660'), sh=2, hl=1, line=1.4)
        paint(c, lambda x: x.rectangle(-13, 14, 26, 6), GOLD, sh=1, hl=1, line=1.2)
        paint(c, lambda x: capsule(x, (0, 22), (0, 32), 3), Pal('#6a4030', '#4a2a1e', '#8a5a40', '#1e0c06'), sh=1, hl=0, line=1)
        c.restore()
    elif name == 'skill_spark':
        radial_glow(c, 0, 0, 34, hx('#4ab8ff'), 0.85)
        paint(c, lambda x: smooth_poly(x, [(4, -32), (-12, 2), (0, 2), (-6, 32), (14, -6), (2, -6)], tension=0.0),
              Pal('#c8f2ff', '#5ac8ff', '#ffffff', '#0a2a50'), sh=2, hl=1, line=1.4)
    elif name == 'skill_roll':
        for i in range(3):
            stroke(c, lambda x, i=i: x.arc(0, 0, 26 - i * 8, math.radians(200), math.radians(500 - i * 40)),
                   hx('#c8f0ff') if i == 0 else hx('#7fd6ff'), 5 - i, 0.95)
        paint(c, lambda x: smooth_poly(x, [(18, -26), (30, -14), (14, -10)], tension=0.0), Pal('#c8f0ff', '#7fd6ff', '#ffffff', '#0a2a50'),
              sh=1, hl=0.5, line=1)


def book():
    f = canvas(1400, 860)
    c = f.ctx
    leather = Pal('#6a2a24', '#4a1a16', '#8e443a', '#1e0806')
    paint(c, lambda x: smooth_poly(x, [(-690, -400), (-10, -380), (10, -380), (690, -400), (680, 410), (10, 390), (-10, 390),
                                       (-680, 410)], tension=0.05), leather, sh=8, hl=3, line=2.4)
    for sx in (-1, 1):
        for cx, cy in ((sx * 650, -362), (sx * 650, 372)):
            paint(c, lambda x, cx=cx, cy=cy: smooth_poly(x, [(cx - 30, cy), (cx, cy - 30), (cx + 30, cy), (cx, cy + 30)], tension=0.1),
                  GOLD, sh=2, hl=1.5, line=1.4)
    page = Pal('#f6ead0', '#e2cfa6', '#fffaee', '#7a5a34')
    for sx in (-1, 1):
        def pg(x, sx=sx):
            x.move_to(sx * 14, -360)
            x.curve_to(sx * 200, -385, sx * 450, -385, sx * 655, -365)
            x.line_to(sx * 645, 375)
            x.curve_to(sx * 450, 355, sx * 200, 355, sx * 14, 372)
            x.close_path()
        paint(c, pg, page, sh=0, hl=0, line=1.2)
        g = cairo.LinearGradient(0, 0, sx * 120, 0)
        g.add_color_stop_rgba(0, 0.45, 0.32, 0.18, 0.45)
        g.add_color_stop_rgba(1, 0.45, 0.32, 0.18, 0)
        c.save(); pg(c); c.clip(); c.set_source(g); c.paint(); c.restore()
        # ornamental frame lines on page
        stroke(c, lambda x, sx=sx: x.rectangle(min(sx * 60, sx * 610), -320, 550, 650), hx('#b8945a'), 1.4, 0.7)
    for sx in (-1, 1):
        stroke(c, lambda x, sx=sx: (x.move_to(sx * 335 - 120, -262), x.line_to(sx * 335 + 120, -262)), hx('#b8945a'), 1.6, 0.8)
    save(f, 'book')


ICONS = ['coin', 'potion', 'ether', 'horn', 'ember', 'tome', 'skill_sword', 'skill_spark', 'skill_roll']


def _icon(ctx, payload):
    icon_draw(ctx, payload)


def build_icons():
    jobs = [(n, [n], 1, False, -1) for n in ICONS]
    build('icons', 'Ui', 96, 96, 48, 48, jobs, _icon, outline=1.2)


if __name__ == '__main__':
    os.makedirs(UI, exist_ok=True)
    medallion()
    arc_tex('arc_hp_track', 200, 20, track=True)
    arc_tex('arc_hp_fill', 200, 20, ('#9a1a2a', '#e0393e', '#ff8a7a'))
    arc_tex('arc_mp_track', 174, 13, track=True)
    arc_tex('arc_mp_fill', 174, 13, ('#1a4aa0', '#3a8ae8', '#9ad0ff'))
    arc_tex('arc_st_track', 156, 8, track=True)
    arc_tex('arc_st_fill', 156, 8, ('#a07a1a', '#e8c040', '#fff0a0'))
    orb()
    soft('smear', 512, 256, 'smear')
    soft('vignette', 960, 540, 'vignette')
    soft('dialogue_band', 1920, 380, 'band')
    flourish()
    nameplate()
    pills()
    portrait('portrait', Look())
    portrait('portrait_receptionist', LOOKS['guild_clerk'], ('#e8a0a8', '#6a2a40'))
    portrait('portrait_blacksmith', LOOKS['merchant'], ('#e0a060', '#5a2a14'))
    portrait('portrait_villager', LOOKS['villager'], ('#a8d890', '#2a5a30'))
    lumia = Look(hair_style='long', hair=Pal('#fff0c8', '#e0c890', '#ffffff', '#8a6a30'), eye=hx('#f0b030'),
                 tunic=Pal('#f4f0ff', '#c8c0e8', '#ffffff', '#4a4070'), scarf_on=False)
    portrait('portrait_lumia', lumia, ('#fff6d0', '#c8a0f0'))
    book()
    build_icons()
    print('ui done')
