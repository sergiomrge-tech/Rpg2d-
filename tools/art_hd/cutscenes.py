"""Illustrated cutscenes (1920x1080) for the prologue and the ending.
python3 cutscenes.py [name ...]   ->  unity/Assets/Resources/Sprites/Cutscenes/<name>.png
Characters reuse the in-game rigs (humanoid.py); backgrounds are drawn with cairo (gradients, glows, silhouettes)."""
from __future__ import annotations
import math
import os
import random
import sys
import cairo
import numpy as np
from PIL import Image
from core import Frame, outline_rgba, to_image, hx, radial_glow, ellipse, smooth_poly, flat, stroke, Pal, paint
from humanoid import Look, draw_figure
from anims import pose
from oni import final_npc, sylra_look, final_look
from sheet import OUT

W, H = 1920, 1080
OUT_DIR = os.path.join(OUT, 'Cutscenes')


def canvas():
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
    return surf, cairo.Context(surf)


def surf_to_pil(surf):
    surf.flush()
    buf = np.ndarray((H, W, 4), np.uint8, surf.get_data())
    return Image.fromarray(buf[..., [2, 1, 0, 3]].copy(), 'RGBA')


def sky(ctx, stops):
    g = cairo.LinearGradient(0, 0, 0, H)
    for t, c in stops:
        g.add_color_stop_rgb(t, *hx(c)[:3])
    ctx.set_source(g)
    ctx.paint()


def glow(ctx, x, y, r, color, a=0.8):
    g = cairo.RadialGradient(x, y, 0, x, y, r)
    c = hx(color)
    g.add_color_stop_rgba(0, c[0], c[1], c[2], a)
    g.add_color_stop_rgba(1, c[0], c[1], c[2], 0)
    ctx.set_source(g)
    ctx.arc(x, y, r, 0, math.tau)
    ctx.fill()


def mountains(ctx, base_y, color, amp, seed, step=60, rough=0.5):
    rnd = random.Random(seed)
    ctx.move_to(0, H)
    ctx.line_to(0, base_y)
    y = base_y
    x = 0
    while x <= W + step:
        y = base_y - amp * (0.55 + 0.45 * math.sin(x * 0.004 + seed)) - rnd.uniform(0, amp * rough)
        ctx.line_to(x, y)
        x += step
    ctx.line_to(W, H)
    ctx.close_path()
    ctx.set_source_rgb(*hx(color)[:3])
    ctx.fill()


def stars(ctx, n, seed, ymax=0.6, color='#ffffff'):
    rnd = random.Random(seed)
    for _ in range(n):
        x, y, r = rnd.uniform(0, W), rnd.uniform(0, H * ymax), rnd.uniform(0.8, 2.6)
        c = hx(color)
        ctx.set_source_rgba(c[0], c[1], c[2], rnd.uniform(0.4, 1))
        ctx.arc(x, y, r, 0, math.tau)
        ctx.fill()


def cloud(ctx, x, y, s, color, a):
    c = hx(color)
    ctx.set_source_rgba(c[0], c[1], c[2], a)
    for dx, dy, r in ((0, 0, 60), (60, -18, 76), (130, 0, 62), (190, 10, 48), (-50, 12, 44)):
        ctx.arc(x + dx * s, y + dy * s, r * s, 0, math.tau)
        ctx.fill()


def char(look, anim, t, view, scale, ox=0, oy=0):
    """Rendered character (PIL RGBA, outline) and its feet-anchor offset."""
    w, h = 220, 220
    f = Frame(w, h, w // 2, h - 20)
    f.ctx.scale(1, 1)
    draw_figure(f.ctx, look, view, pose(anim, t, view))
    im = to_image(outline_rgba(f.rgba(), hx('#22131b'), 1.0))
    im = im.resize((int(w * scale), int(h * scale)), Image.LANCZOS)
    return im, (int(w * scale / 2), int((h - 20) * scale))


def put(img, ch, x, y):
    im, (ax, ay) = ch
    img.alpha_composite(im, (int(x - ax), int(y - ay)))


def vignette(img, strength=0.55):
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    d = np.sqrt(((xx / W) * 2 - 1) ** 2 + ((yy / H) * 2 - 1) ** 2)
    a = (np.clip((d - 0.55) / 0.9, 0, 1) ** 1.6 * strength * 255).astype(np.uint8)
    v = np.zeros((H, W, 4), np.uint8)
    v[..., 3] = a
    v[..., :3] = (6, 4, 14)
    img.alpha_composite(Image.fromarray(v, 'RGBA'))


def save(img, name):
    os.makedirs(OUT_DIR, exist_ok=True)
    vignette(img)
    img.convert('RGB').save(os.path.join(OUT_DIR, name + '.png'), optimize=True)
    print('cutscene', name)


# ============================================================ scenes
def tokyo():
    surf, c = canvas()
    sky(c, [(0, '#0a0e24'), (0.55, '#1c2450'), (1, '#3a2a5a')])
    stars(c, 90, 3, 0.35)
    glow(c, 1500, 220, 240, '#ffe8b0', 0.35)
    c.set_source_rgb(*hx('#f4ecd0')[:3])
    c.arc(1500, 220, 62, 0, math.tau)
    c.fill()
    rnd = random.Random(8)
    for layer, (col, top, wmin, wmax) in enumerate((('#141a3a', 380, 90, 170), ('#0e1230', 300, 120, 220))):
        x = -40
        while x < W:
            w = rnd.uniform(wmin, wmax)
            h = rnd.uniform(top, top + 380)
            c.rectangle(x, 760 - h, w, h + 300)
            c.set_source_rgb(*hx(col)[:3])
            c.fill()
            for wy in range(int(760 - h + 20), 740, 34):
                for wx in range(int(x + 10), int(x + w - 14), 28):
                    if rnd.random() < 0.45:
                        c.set_source_rgba(1, 0.86, 0.5, rnd.uniform(0.5, 0.95))
                        c.rectangle(wx, wy, 14, 18)
                        c.fill()
            x += w + rnd.uniform(4, 16)
    # wet road
    g = cairo.LinearGradient(0, 760, 0, H)
    g.add_color_stop_rgb(0, *hx('#1a1c34')[:3])
    g.add_color_stop_rgb(1, *hx('#0a0a18')[:3])
    c.set_source(g)
    c.rectangle(0, 760, W, H - 760)
    c.fill()
    for x in range(120, W, 300):   # lamp reflections
        glow(c, x, 900, 120, '#ffd890', 0.18)
    for i in range(14):
        c.set_source_rgba(1, 1, 1, 0.16)
        c.rectangle(80 + i * 140, 960 + (i % 3) * 20, 70, 6)
        c.fill()
    # street lamps
    for x in (260, 760):
        c.set_source_rgb(*hx('#2a2a40')[:3])
        c.rectangle(x - 5, 380, 10, 420)
        c.fill()
        glow(c, x, 380, 160, '#ffd890', 0.5)
        c.set_source_rgb(*hx('#fff2c8')[:3])
        c.arc(x, 380, 12, 0, math.tau)
        c.fill()
    # truck (right) with blinding headlights
    c.set_source_rgb(*hx('#d8d8e4')[:3])
    c.rectangle(1240, 560, 700, 360)
    c.fill()
    c.set_source_rgb(*hx('#b4b4c8')[:3])
    c.rectangle(1240, 760, 700, 40)
    c.fill()
    c.set_source_rgb(*hx('#3a3a52')[:3])
    c.rectangle(1240, 520, 220, 400)
    c.fill()
    c.set_source_rgb(*hx('#8ad0ff')[:3])
    c.rectangle(1262, 548, 170, 120)
    c.fill()
    for x in (1300, 1640, 1820):
        c.set_source_rgb(*hx('#14141e')[:3])
        c.arc(x, 920, 74, 0, math.tau)
        c.fill()
        c.set_source_rgb(*hx('#6a6a7e')[:3])
        c.arc(x, 920, 30, 0, math.tau)
        c.fill()
    for y in (700, 780):
        glow(c, 1236, y, 520, '#fff4c0', 0.85)
        glow(c, 1236, y, 160, '#ffffff', 1.0)
    img = surf_to_pil(surf)
    hero = Look()
    put(img, char(hero, 'roll', 0.4, 'side', 2.8), 880, 940)           # Ren lunging
    put(img, char(final_look('demon_knight') if False else Look(hair=Pal('#c8602a', '#964214', '#f0904a', '#3a1404'), scarf_on=False, weapon=None), 'hurt', 0.4, 'side', 2.0), 1010, 960)
    save(img, 'tokyo')


def void():
    surf, c = canvas()
    sky(c, [(0, '#fff6dc'), (0.5, '#f0e0ff'), (1, '#c8d8ff')])
    glow(c, 960, 360, 800, '#ffffff', 0.9)
    for i in range(18):
        a = math.radians(i * 20)
        c.save()
        c.translate(960, 330)
        c.rotate(a)
        g = cairo.LinearGradient(0, 0, 1400, 0)
        g.add_color_stop_rgba(0, 1, 0.95, 0.7, 0.35)
        g.add_color_stop_rgba(1, 1, 0.95, 0.7, 0)
        c.set_source(g)
        c.move_to(0, -26)
        c.line_to(1400, -90)
        c.line_to(1400, 90)
        c.line_to(0, 26)
        c.close_path()
        c.fill()
        c.restore()
    rnd = random.Random(2)
    for _ in range(160):
        x, y = rnd.uniform(0, W), rnd.uniform(0, H)
        glow(c, x, y, rnd.uniform(6, 22), '#ffe8a0', rnd.uniform(0.4, 0.9))
    for k in range(6):
        cloud(c, 120 + k * 340, 880 + (k % 2) * 40, 1.6, '#ffffff', 0.55)
    img = surf_to_pil(surf)
    lum = final_npc('lumia')
    put(img, char(lum, 'idle', 0.3, 'down', 6.2), 960, 780)
    put(img, char(Look(), 'idle', 0.5, 'up', 2.4), 960, 1010)
    save(img, 'void')


def aurora_dawn():
    surf, c = canvas()
    sky(c, [(0, '#3a4a8a'), (0.35, '#ff9a6a'), (0.62, '#ffe0a0'), (1, '#9ad06a')])
    glow(c, 1300, 560, 700, '#fff0b0', 0.8)
    c.set_source_rgb(*hx('#fff8d8')[:3])
    c.arc(1300, 560, 70, 0, math.tau)
    c.fill()
    for x, y, s, a in ((200, 200, 1.4, 0.6), (900, 140, 1.8, 0.5), (1500, 260, 1.2, 0.55)):
        cloud(c, x, y, s, '#ffd8c0', a)
    mountains(c, 640, '#6a7aa8', 160, 1, 50)
    mountains(c, 700, '#4a6a78', 110, 2, 44)
    # village silhouettes
    rnd = random.Random(5)
    for x in range(100, 1850, 210):
        h = rnd.uniform(70, 110)
        yb = 770 + rnd.uniform(-10, 14)
        c.set_source_rgb(*hx('#3a3a4e')[:3])
        c.rectangle(x, yb - h, 120, h)
        c.fill()
        c.move_to(x - 12, yb - h)
        c.line_to(x + 60, yb - h - 70)
        c.line_to(x + 132, yb - h)
        c.close_path()
        c.set_source_rgb(*hx('#2a2a3e')[:3])
        c.fill()
        c.set_source_rgba(1, 0.86, 0.5, 0.95)
        c.rectangle(x + 40, yb - h + 26, 22, 26)
        c.fill()
    g = cairo.LinearGradient(0, 780, 0, H)
    g.add_color_stop_rgb(0, *hx('#8ac85a')[:3])
    g.add_color_stop_rgb(1, *hx('#3e8a3a')[:3])
    c.set_source(g)
    c.rectangle(0, 780, W, H - 780)
    c.fill()
    rnd = random.Random(9)
    for _ in range(900):
        x, y = rnd.uniform(0, W), rnd.uniform(790, H)
        c.set_source_rgba(0.2, 0.5, 0.2, 0.6)
        c.move_to(x, y)
        c.line_to(x + rnd.uniform(-4, 4), y - rnd.uniform(8, 20))
        c.set_line_width(2)
        c.stroke()
    img = surf_to_pil(surf)
    put(img, char(Look(), 'idle', 0.2, 'down', 3.6), 960, 960)
    save(img, 'aurora_dawn')


def malgrath_fall():
    surf, c = canvas()
    sky(c, [(0, '#1a0a2a'), (0.5, '#5a1a3a'), (1, '#2a1030')])
    glow(c, 960, 380, 900, '#ff5a4a', 0.35)
    # breaking light through the clouds
    for i in range(9):
        c.save()
        c.translate(960, -80)
        c.rotate(math.radians(-60 + i * 15))
        g = cairo.LinearGradient(0, 0, 0, 1300)
        g.add_color_stop_rgba(0, 1, 0.9, 0.5, 0.5)
        g.add_color_stop_rgba(1, 1, 0.9, 0.5, 0)
        c.set_source(g)
        c.move_to(-26, 0)
        c.line_to(-110, 1300)
        c.line_to(110, 1300)
        c.line_to(26, 0)
        c.close_path()
        c.fill()
        c.restore()
    for k in range(7):
        cloud(c, -80 + k * 330, 180 + (k % 3) * 80, 2.2, '#3a1a3a', 0.7)
    mountains(c, 780, '#1a0e24', 140, 6, 55)
    c.rectangle(0, 860, W, H - 860)
    c.set_source_rgb(*hx('#140a1c')[:3])
    c.fill()
    rnd = random.Random(4)
    for _ in range(220):   # golden ash rising
        x, y = rnd.uniform(0, W), rnd.uniform(60, H)
        glow(c, x, y, rnd.uniform(4, 12), '#ffd27a', rnd.uniform(0.5, 1))
    img = surf_to_pil(surf)
    put(img, char(final_look('malgrath'), 'death', 0.55, 'down', 5.4), 1130, 940)
    put(img, char(Look(), 'idle', 0.3, 'side', 4.2), 640, 960)
    save(img, 'malgrath_fall')


def sunrise_peaks():
    surf, c = canvas()
    sky(c, [(0, '#5a6ab8'), (0.4, '#ff9a8a'), (0.7, '#ffe0a8'), (1, '#fff4d0')])
    glow(c, 960, 640, 900, '#fff4c0', 0.9)
    c.set_source_rgb(*hx('#fffbe8')[:3])
    c.arc(960, 640, 90, 0, math.tau)
    c.fill()
    for x, y, s, a in ((120, 260, 1.5, 0.6), (1300, 180, 2.0, 0.5), (760, 360, 1.2, 0.5)):
        cloud(c, x, y, s, '#ffe8e0', a)
    mountains(c, 700, '#c8b8d8', 170, 3, 70)
    mountains(c, 780, '#8a7ea8', 130, 4, 60)
    mountains(c, 880, '#5a5a84', 100, 5, 52)
    c.rectangle(0, 900, W, H - 900)
    c.set_source_rgb(*hx('#2a2a48')[:3])
    c.fill()
    img = surf_to_pil(surf)
    put(img, char(Look(), 'idle', 0.1, 'up', 4.4), 760, 1000)
    put(img, char(sylra_look(), 'idle', 0.6, 'up', 4.2), 980, 1000)
    put(img, char(final_npc('lumia'), 'idle', 0.3, 'up', 4.6), 1230, 1000)
    save(img, 'sunrise_peaks')


def vista():
    surf, c = canvas()
    sky(c, [(0, '#6aa8f0'), (0.5, '#b8e0ff'), (1, '#fff4d0')])
    glow(c, 1500, 250, 600, '#fff8c0', 0.8)
    c.set_source_rgb(*hx('#fffbe0')[:3])
    c.arc(1500, 250, 70, 0, math.tau)
    c.fill()
    for x, y, s, a in ((150, 200, 1.8, 0.8), (800, 120, 2.2, 0.7), (1200, 320, 1.4, 0.7)):
        cloud(c, x, y, s, '#ffffff', a)
    mountains(c, 560, '#a8c0e0', 130, 7, 70)
    mountains(c, 640, '#78a0b8', 100, 8, 60)
    # forest + river + village below
    g = cairo.LinearGradient(0, 640, 0, H)
    g.add_color_stop_rgb(0, *hx('#6ab85a')[:3])
    g.add_color_stop_rgb(1, *hx('#2e7a38')[:3])
    c.set_source(g)
    c.rectangle(0, 640, W, H - 640)
    c.fill()
    c.set_source_rgb(*hx('#7ad0e8')[:3])
    c.move_to(1000, 640)
    c.curve_to(900, 760, 1200, 860, 1000, H)
    c.line_to(1180, H)
    c.curve_to(1380, 860, 1080, 760, 1140, 640)
    c.close_path()
    c.fill()
    rnd = random.Random(6)
    for _ in range(140):
        x, y = rnd.uniform(0, W), rnd.uniform(660, H)
        s = 0.5 + (y - 640) / 440
        c.set_source_rgb(*hx('#2a6a34')[:3])
        c.arc(x, y, 26 * s, 0, math.tau)
        c.fill()
        c.set_source_rgb(*hx('#4a9a4a')[:3])
        c.arc(x - 6 * s, y - 8 * s, 18 * s, 0, math.tau)
        c.fill()
    for x, y in ((380, 700), (520, 730), (620, 690)):
        c.set_source_rgb(*hx('#e8d8b8')[:3])
        c.rectangle(x, y, 60, 40)
        c.fill()
        c.move_to(x - 8, y)
        c.line_to(x + 30, y - 30)
        c.line_to(x + 68, y)
        c.close_path()
        c.set_source_rgb(*hx('#d0603a')[:3])
        c.fill()
    img = surf_to_pil(surf)
    put(img, char(Look(), 'idle', 0.4, 'up', 4.6), 800, 1030)
    put(img, char(sylra_look(), 'idle', 0.1, 'up', 4.4), 1010, 1030)
    save(img, 'vista')


SCENES = dict(tokyo=tokyo, void=void, aurora_dawn=aurora_dawn, malgrath_fall=malgrath_fall, sunrise_peaks=sunrise_peaks, vista=vista)

if __name__ == '__main__':
    for n in (sys.argv[1:] or list(SCENES)):
        SCENES[n]()
