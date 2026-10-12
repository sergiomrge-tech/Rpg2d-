"""World objects (trees, buildings, props) -> godot/assets/obj/*.png + objects.json"""
import math, json, os, sys
import numpy as np
from PIL import Image
sys.path.insert(0, os.path.dirname(__file__))
from pix import Canvas, Part, ramp, hex2rgb

OBJ = {}   # name -> dict(meta)
IMGS = {}  # name -> Image (RGBA)  (frames stacked horizontally for animated)


class Pal:
    """Lazy part registry for a canvas."""
    def __init__(self, c: Canvas):
        self.c = c
        self.ids = {}

    def __call__(self, name, color=None, rank=0, **kw):
        if name not in self.ids:
            self.ids[name] = self.c.part(Part(name, color or '#888888', rank, **kw))
        return self.ids[name]


def reg(name, img, cells=None, anchor=None, frames=1, fps=0, light=None, extra=None):
    w, h = img.size
    fw = w // frames
    d = {'w': fw, 'h': h, 'anchor': list(anchor) if anchor else [fw // 2, h], 'cells': cells if cells is not None else [[0, 0]], 'frames': frames, 'fps': fps}
    if light:
        d['light'] = light
    if extra:
        d.update(extra)
    OBJ[name] = d
    IMGS[name] = img


def shadow(c, P, cx, cy, rx, ry):
    c.ellipse(P('shadow', '#000000', -9, flat=True), cx, cy, rx, ry)


def trunk(c, P, x, base_y, top_y, w, color='#7a4a2a'):
    t = P('trunk', color, 3)
    td = P('bark', color, 3, flat=True)
    c.poly(t, [(x - w / 2, base_y), (x - w / 2 + 1, top_y), (x + w / 2 - 1, top_y), (x + w / 2, base_y)])
    c.poly(t, [(x - w / 2 - 3, base_y + 1), (x - w / 2, base_y - 6), (x + w / 2, base_y - 6), (x + w / 2 + 3, base_y + 1)])
    for k in range(4):
        yy = top_y + 4 + k * (base_y - top_y) / 5
        c.line(td, x - w / 4 + (k % 2), yy, x - w / 4 + (k % 2), yy + 4, 0.9)


def leaf_cluster(c, P, rng, cx, cy, rx, ry, base, n=16, tones=('leaf_d', 'leaf_m', 'leaf_l')):
    ids = [P(tones[0], base, 6), P(tones[1], base, 7), P(tones[2], base, 8)]
    # dark base mass
    c.ellipse(ids[0], cx, cy, rx, ry)
    for k in range(n):
        a = rng.random() * 2 * math.pi
        r = rng.random() ** 0.6
        x = cx + math.cos(a) * rx * 0.72 * r
        y = cy + math.sin(a) * ry * 0.72 * r - ry * 0.05
        # lighter toward the top-left
        light = 0.5 + (-(x - cx) / rx * 0.35 - (y - cy) / ry * 0.5)
        tone = ids[2] if light > 0.78 else ids[1] if light > 0.38 else ids[0]
        c.ellipse(tone, x, y, rx * 0.34, ry * 0.30)


def tree(kind='oak', variant=0):
    rng = np.random.default_rng(variant * 13 + hash(kind) % 1000)
    W, H = 80, 112
    c = Canvas(W, H)
    P = Pal(c)
    cx = 40
    shadow(c, P, cx + 4, 106, 20, 5)
    if kind == 'pine':
        trunk(c, P, cx, 106, 80, 6, '#6a4228')
        g = '#2a7a4e'
        ids = [P('leaf_d', g, 6), P('leaf_m', g, 7), P('leaf_l', g, 8)]
        y0 = 92
        for k in range(5):
            half = 11 + (4 - k) * 3.2
            yb = y0 - k * 14
            c.poly(ids[0], [(cx - half - 2, yb), (cx + half + 2, yb), (cx, yb - 22)])
            c.poly(ids[1], [(cx - half, yb - 1), (cx + half * 0.15, yb - 1), (cx, yb - 20)])
            c.poly(ids[2], [(cx - half * 0.7, yb - 3), (cx - half * 0.05, yb - 3), (cx - 1, yb - 17)])
        c.poly(ids[2], [(cx - 3, 22), (cx + 3, 22), (cx, 8)])
    elif kind == 'dead':
        trunk(c, P, cx, 106, 40, 7, '#6b5a50')
        b = P('bark', '#6b5a50', 4)
        for (x0, y0, x1, y1) in ((cx, 60, cx - 18, 36), (cx, 52, cx + 17, 28), (cx - 18, 36, cx - 24, 24), (cx + 17, 28, cx + 22, 14), (cx, 44, cx + 4, 18)):
            c.line(b, x0, y0, x1, y1, 3.2)
    elif kind == 'palm':
        tx = P('trunk', '#9a6a3a', 3)
        for k in range(30):
            c.ellipse(tx, cx + math.sin(k * 0.15) * 4 + k * 0.3, 106 - k * 2.2, 4.2, 2.4)
        top = (cx + 9, 40)
        g = P('leaf_m', '#3fa84a', 7); gd = P('leaf_d', '#2a7a3a', 6); gl = P('leaf_l', '#6fd05a', 8)
        for ang, ln in ((-170, 30), (-130, 28), (-90, 22), (-50, 28), (-10, 30), (30, 26), (150, 26), (110, 22)):
            a = math.radians(ang)
            pts = []
            for k in range(14):
                f = k / 13
                x = top[0] + math.cos(a) * ln * f
                y = top[1] + math.sin(a) * ln * f + f * f * 14
                pts.append((x, y))
            for i2, (x, y) in enumerate(pts):
                w = 3.6 * (1 - i2 / 16)
                c.ellipse(gd if i2 % 3 == 0 else g, x, y, w + 1.5, w)
                c.ellipse(gl, x - 0.6, y - 0.8, w * 0.5, w * 0.35)
        c.ellipse(P('coco', '#7a4a2a', 5), top[0] - 2, top[1] + 4, 3, 3)
        c.ellipse(P('coco', '#7a4a2a', 5), top[0] + 3, top[1] + 5, 3, 3)
    else:
        base = {'oak': '#3f9a4a', 'autumn': '#d9772e', 'fruit': '#3f9a4a', 'crystal': '#4a9ec4', 'willow': '#4a9a6a'}[kind]
        trunk(c, P, cx, 106, 62, 8 + variant % 2, '#7a4a2a')
        pts = [(cx, 32, 26, 22), (cx - 18, 46, 18, 16), (cx + 18, 46, 18, 16), (cx - 8, 58, 18, 13), (cx + 9, 58, 18, 13), (cx, 44, 24, 18)]
        for (x, y, rx, ry) in pts:
            leaf_cluster(c, P, rng, x, y, rx, ry, base, 14)
        if kind == 'fruit':
            fr = P('fruit', '#ff4d6d', 9, flat=True)
            for _ in range(9):
                c.ellipse(fr, cx + rng.uniform(-24, 24), 36 + rng.uniform(-6, 30), 1.7, 1.7)
        if kind == 'crystal':
            cr = P('cry', '#a8f0ff', 10, flat=True)
            for _ in range(8):
                c.ellipse(cr, cx + rng.uniform(-24, 24), 30 + rng.uniform(0, 28), 1.4, 1.4)
    img = c.render()
    reg(f'tree_{kind}_{variant}', img, cells=[[0, 0]], anchor=(40, 106), extra={'foot': [-8, -10, 16, 10], 'sway': 1})


def bush(variant=0, base='#3f9a4a', flowers=False):
    rng = np.random.default_rng(variant + 5)
    c = Canvas(48, 40); P = Pal(c)
    shadow(c, P, 24, 35, 16, 4)
    for (x, y, rx, ry) in ((14, 26, 11, 9), (34, 26, 11, 9), (24, 20, 14, 11)):
        leaf_cluster(c, P, rng, x, y, rx, ry, base, 8)
    if flowers:
        for k, col in enumerate(('#ff8fab', '#ffd166', '#ffffff', '#b39dff')):
            fp = P('fl%d' % k, col, 10, flat=True)
            for _ in range(3):
                c.ellipse(fp, 24 + rng.uniform(-14, 14), 20 + rng.uniform(-8, 8), 1.5, 1.5)
    reg(f'bush_{variant}{"_f" if flowers else ""}', c.render(), anchor=(24, 35), extra={'foot': [-14, -10, 28, 10]})


def rock(name, base='#8a8a9a', w=44, h=36, variant=0):
    rng = np.random.default_rng(variant + 9)
    c = Canvas(w, h); P = Pal(c)
    shadow(c, P, w / 2, h - 4, w * 0.38, 4)
    r = P('rock', base, 5); rd = P('rock_d', base, 4); rl = P('rock_l', base, 6)
    cx, cy = w / 2, h - 12
    pts = [(cx - w * 0.38, cy + 4), (cx - w * 0.3, cy - h * 0.2), (cx - w * 0.1, cy - h * 0.38), (cx + w * 0.15, cy - h * 0.34), (cx + w * 0.36, cy - h * 0.1), (cx + w * 0.4, cy + 4), (cx + w * 0.1, cy + 8), (cx - w * 0.2, cy + 8)]
    c.blob(r, pts)
    c.blob(rl, [(cx - w * 0.28, cy - h * 0.15), (cx - w * 0.1, cy - h * 0.32), (cx + w * 0.1, cy - h * 0.28), (cx, cy - h * 0.12)])
    for k in range(3):
        x0 = cx + rng.uniform(-w * 0.2, w * 0.2); y0 = cy + rng.uniform(-6, 3)
        c.line(rd, x0, y0, x0 + rng.uniform(-5, 5), y0 + rng.uniform(3, 7), 0.9)
    reg(name, c.render(), anchor=(w / 2, h - 4), extra={'foot': [-w * 0.35, -9, w * 0.7, 9]})


def crystal(name, color='#66e6ff', variant=0, w=48, h=64):
    rng = np.random.default_rng(variant + 3)
    c = Canvas(w, h); P = Pal(c)
    shadow(c, P, w / 2, h - 6, 18, 4)
    ids = [P('c_d', color, 5), P('c_m', color, 6), P('c_l', color, 8)]
    shards = [(w / 2, h - 8, 7, 44 + variant * 4), (w / 2 - 12, h - 8, 5, 28), (w / 2 + 12, h - 8, 5, 32), (w / 2 - 5, h - 8, 4, 20), (w / 2 + 6, h - 8, 4, 18)]
    for (x, y, ww, hh) in shards:
        c.poly(ids[1], [(x - ww, y), (x - ww * 0.7, y - hh * 0.72), (x, y - hh), (x + ww * 0.7, y - hh * 0.72), (x + ww, y)])
        c.poly(ids[0], [(x, y), (x, y - hh), (x + ww * 0.7, y - hh * 0.72), (x + ww, y)])
        c.poly(ids[2], [(x - ww * 0.6, y - 3), (x - ww * 0.45, y - hh * 0.65), (x - ww * 0.15, y - hh * 0.8), (x - ww * 0.15, y - 3)])
    img = c.render()
    reg(name, img, anchor=(w / 2, h - 6), extra={'foot': [-14, -8, 28, 8], 'light': {'r': 90, 'color': color, 'dy': -26}})


def stalagmite(variant=0):
    c = Canvas(40, 56); P = Pal(c)
    shadow(c, P, 20, 51, 13, 3)
    a = P('s', '#5a5270', 5); d = P('sd', '#5a5270', 4); l = P('sl', '#5a5270', 6)
    c.poly(a, [(6, 50), (14, 20), (20, 4), (26, 22), (34, 50)])
    c.poly(l, [(9, 48), (14, 24), (20, 8), (18, 30), (14, 48)])
    c.poly(d, [(20, 4), (26, 22), (34, 50), (24, 50)])
    reg(f'stalagmite_{variant}', c.render(), anchor=(20, 52), extra={'foot': [-9, -8, 18, 8]})


def barrel():
    c = Canvas(28, 34); P = Pal(c)
    shadow(c, P, 14, 30, 10, 3)
    w = P('w', '#a8693a', 5); h = P('hoop', '#6e6a78', 6)
    c.blob(w, [(4, 10), (6, 4), (14, 2), (22, 4), (24, 10), (24, 24), (22, 30), (14, 32), (6, 30), (4, 24)])
    c.ellipse(P('top', '#c88a4a', 7), 14, 6, 9, 3)
    for y in (10, 24):
        c.rect(h, 4, y, 24, y + 2)
    for x in (9, 14, 19):
        c.line(P('gr', '#7a4a2a', 5, flat=True), x, 11, x, 23, 0.7)
    reg('barrel', c.render(), anchor=(14, 31), extra={'foot': [-10, -8, 20, 8]})


def crate(stack=1):
    c = Canvas(32, 28 + 22 * (stack - 1)); P = Pal(c)
    H = 28 + 22 * (stack - 1)
    shadow(c, P, 16, H - 3, 12, 3)
    w = P('w', '#b8864a', 5); d = P('wd', '#7a5028', 4, flat=True)
    for s in range(stack):
        y0 = H - 24 - s * 22
        c.rect(w, 3, y0, 29, y0 + 22)
        c.rect(d, 3, y0, 6, y0 + 22); c.rect(d, 26, y0, 29, y0 + 22); c.rect(d, 3, y0, 29, y0 + 3); c.rect(d, 3, y0 + 19, 29, y0 + 22)
        c.line(d, 6, y0 + 3, 26, y0 + 19, 1.6); c.line(d, 26, y0 + 3, 6, y0 + 19, 1.6)
    reg(f'crate{stack}', c.render(), anchor=(16, H - 3), extra={'foot': [-12, -8, 24, 8]})


def jar(variant=0):
    cols = ['#c0643a', '#4a8ac0', '#a8693a', '#7a9a5a']
    c = Canvas(24, 32); P = Pal(c)
    shadow(c, P, 12, 28, 8, 3)
    p = P('j', cols[variant % 4], 5)
    c.blob(p, [(8, 6), (16, 6), (19, 14), (20, 22), (16, 28), (8, 28), (4, 22), (5, 14)])
    c.rect(p, 8, 2, 16, 8); c.ellipse(P('lip', cols[variant % 4], 7), 12, 3, 5, 1.8)
    c.line(P('band', '#f2c94c', 8, flat=True), 6, 15, 18, 15, 1.2)
    reg(f'jar_{variant}', c.render(), anchor=(12, 29), extra={'foot': [-8, -7, 16, 7]})


def sign():
    c = Canvas(32, 44); P = Pal(c)
    shadow(c, P, 16, 40, 9, 3)
    w = P('w', '#a8693a', 5); d = P('wd', '#6a4228', 4, flat=True)
    c.rect(w, 14, 18, 18, 40)
    c.blob(w, [(3, 5), (29, 5), (30, 20), (2, 20)])
    c.line(d, 7, 10, 25, 10, 1.1); c.line(d, 7, 14, 20, 14, 1.1)
    reg('sign', c.render(), anchor=(16, 40), extra={'foot': [-6, -6, 12, 6]})


def fence(kind='h'):
    c = Canvas(32, 32); P = Pal(c)
    w = P('w', '#b0814e', 5); d = P('wd', '#6a4228', 4, flat=True)
    if kind == 'h':
        c.rect(w, 0, 12, 32, 17); c.rect(w, 0, 20, 32, 25)
        for x in (3, 25):
            c.rect(w, x, 7, x + 5, 30)
            c.rect(P('cap', '#c89a60', 6), x - 1, 6, x + 6, 9)
        reg('fence_h', c.render(), anchor=(16, 28), extra={'foot': [-16, -8, 32, 8]})
    else:
        c.rect(w, 13, 0, 19, 32)
        c.rect(w, 8, 6, 24, 10); c.rect(w, 8, 16, 24, 20)
        reg('fence_v', c.render(), anchor=(16, 28), extra={'foot': [-6, -28, 12, 32]})


def lamp(frames=2):
    imgs = []
    for f in range(frames):
        c = Canvas(24, 72); P = Pal(c)
        shadow(c, P, 12, 68, 8, 3)
        m = P('m', '#4a4a58', 5)
        c.rect(m, 10, 18, 14, 66); c.rect(m, 6, 62, 18, 68)
        c.rect(m, 5, 6, 19, 10); c.rect(m, 5, 22, 19, 26)
        c.poly(P('glass', '#ffd86a', 9, flat=True), [(7, 10), (17, 10), (18, 22), (6, 22)])
        c.ellipse(P('flame', '#fff2b0' if f == 0 else '#ffe080', 10, flat=True), 12, 16, 3 + f * 0.6, 4)
        imgs.append(c.render())
    sheet = Image.new('RGBA', (24 * frames, 72), (0, 0, 0, 0))
    for i, im in enumerate(imgs):
        sheet.alpha_composite(im, (i * 24, 0))
    reg('lamp', sheet, anchor=(12, 68), frames=frames, fps=3, extra={'foot': [-6, -6, 12, 6]}, light={'r': 120, 'color': '#ffd070', 'dy': -52})


def torch(frames=4):
    imgs = []
    for f in range(frames):
        c = Canvas(24, 56); P = Pal(c)
        shadow(c, P, 12, 52, 7, 2)
        w = P('w', '#6a4a2a', 5)
        c.rect(w, 10, 22, 14, 50); c.rect(P('br', '#6e6a78', 6), 7, 20, 17, 25)
        fl = ramp('#ff8a2a', 6)
        h = [12, 15, 13, 16][f]
        sway = [0, 1, -1, 0.5][f]
        c.blob(P('f1', '#ff8a2a', 8, flat=True), [(12 + sway, 20 - h), (17, 14), (16, 20), (12, 22), (8, 20), (7, 14)])
        c.blob(P('f2', '#ffd84a', 9, flat=True), [(12 + sway, 22 - h * 0.7), (15, 17), (14, 21), (12, 22), (10, 21), (9, 17)])
        c.ellipse(P('f3', '#ffffff', 10, flat=True), 12, 19, 1.6, 2.4)
        imgs.append(c.render())
    sheet = Image.new('RGBA', (24 * frames, 56), (0, 0, 0, 0))
    for i, im in enumerate(imgs):
        sheet.alpha_composite(im, (i * 24, 0))
    reg('torch', sheet, anchor=(12, 52), frames=frames, fps=8, extra={'foot': [-5, -5, 10, 5]}, light={'r': 130, 'color': '#ff9a3a', 'dy': -38, 'flicker': True})


def campfire(frames=4):
    imgs = []
    for f in range(frames):
        c = Canvas(48, 48); P = Pal(c)
        shadow(c, P, 24, 42, 16, 4)
        w = P('w', '#6a4a2a', 5)
        c.line(w, 10, 38, 38, 32, 5); c.line(w, 12, 32, 36, 38, 5)
        c.ellipse(P('st', '#8a8a9a', 6), 12, 40, 4, 3); c.ellipse(P('st', '#8a8a9a', 6), 36, 40, 4, 3); c.ellipse(P('st', '#8a8a9a', 6), 24, 43, 4, 2.6)
        h = [20, 24, 22, 26][f]
        s = [0, 1.5, -1.5, 1][f]
        c.blob(P('f1', '#ff6a1a', 8, flat=True), [(24 + s, 34 - h), (32, 26), (30, 36), (24, 38), (18, 36), (16, 26)])
        c.blob(P('f2', '#ffa82a', 9, flat=True), [(24 + s * 0.6, 36 - h * 0.78), (29, 29), (27, 36), (24, 38), (21, 36), (19, 29)])
        c.blob(P('f3', '#ffe888', 10, flat=True), [(24, 36 - h * 0.45), (27, 32), (24, 37), (21, 32)])
        imgs.append(c.render())
    sheet = Image.new('RGBA', (48 * frames, 48), (0, 0, 0, 0))
    for i, im in enumerate(imgs):
        sheet.alpha_composite(im, (i * 48, 0))
    reg('campfire', sheet, anchor=(24, 42), frames=frames, fps=8, extra={'foot': [-14, -10, 28, 10]}, light={'r': 170, 'color': '#ff8a2a', 'dy': -16, 'flicker': True})


def well():
    c = Canvas(72, 88); P = Pal(c)
    shadow(c, P, 36, 80, 28, 6)
    s = P('s', '#9a9aa8', 5); sd = P('sd', '#9a9aa8', 4, flat=True)
    c.blob(s, [(10, 44), (14, 38), (36, 34), (58, 38), (62, 44), (62, 74), (52, 80), (20, 80), (10, 74)])
    for yy in (50, 58, 66, 74):
        c.line(sd, 11, yy, 61, yy, 0.8)
    for xx in (20, 32, 44, 54):
        c.line(sd, xx, 44, xx, 80, 0.8)
    c.ellipse(P('water', '#2a62b0', 7, flat=True), 36, 42, 22, 6)
    c.ellipse(P('wl', '#6aa8f0', 8, flat=True), 30, 41, 10, 2)
    w = P('w', '#7a4a2a', 5)
    c.rect(w, 12, 12, 17, 50); c.rect(w, 55, 12, 60, 50)
    c.poly(P('roof', '#b8323f', 6), [(4, 18), (36, 2), (68, 18), (62, 22), (36, 10), (10, 22)])
    c.rect(P('roof2', '#d9485a', 7), 8, 18, 64, 24)
    c.line(P('rope', '#d8c8a0', 8, flat=True), 36, 24, 36, 38, 1.2)
    c.rect(P('bucket', '#8a5a2a', 6), 31, 36, 41, 44)
    reg('well', c.render(), cells=[[-1, 0], [0, 0], [-1, -1], [0, -1]], anchor=(36, 80), extra={'foot': [-26, -34, 52, 34]})


def fountain(frames=4):
    imgs = []
    for f in range(frames):
        c = Canvas(128, 112); P = Pal(c)
        shadow(c, P, 64, 100, 54, 9)
        s = P('s', '#c0c0d0', 5); sd = P('sd', '#c0c0d0', 4, flat=True)
        c.ellipse(s, 64, 82, 54, 22)
        c.ellipse(P('in', '#2f78d0', 7, flat=True), 64, 78, 46, 17)
        c.ellipse(P('in2', '#4a9af0', 8, flat=True), 64, 76, 40, 13)
        for k in range(9):
            x = 30 + ((k * 11 + f * 6) % 70)
            c.line(P('sp', '#dff4ff', 10, flat=True), x, 76 + (k % 3) * 2, x + 5, 76 + (k % 3) * 2, 1.0)
        c.rect(s, 56, 30, 72, 76)
        c.ellipse(s, 64, 34, 18, 6)
        c.ellipse(s, 64, 50, 10, 4)
        c.rect(s, 61, 12, 67, 34)
        dr = P('drop', '#dff4ff', 10, flat=True)
        for k in range(10):
            t = ((f * 3 + k * 2) % 16) / 16
            c.ellipse(dr, 64 + (k - 4.5) * 4 * t, 14 + t * 26 + (1 - t) * (-2), 1.6, 2)
        c.rect(P('jet', '#dff4ff', 10, flat=True), 62.5, 2, 65.5, 14)
        imgs.append(c.render())
    sheet = Image.new('RGBA', (128 * frames, 112), (0, 0, 0, 0))
    for i, im in enumerate(imgs):
        sheet.alpha_composite(im, (i * 128, 0))
    reg('fountain', sheet, cells=[[-2, 0], [-1, 0], [0, 0], [1, 0], [-2, -1], [-1, -1], [0, -1], [1, -1]], anchor=(64, 100), frames=frames, fps=5, extra={'foot': [-50, -40, 100, 40]})


def banner(color='#3a7bd5', name='banner_blue', long=False):
    h = 96 if long else 80
    c = Canvas(40, h); P = Pal(c)
    pole = P('pole', '#6a4a2a', 5)
    c.rect(pole, 4, 4, 36, 8)
    cl = P('cl', color, 6)
    c.poly(cl, [(7, 8), (33, 8), (33, h - 16), (20, h - 6), (7, h - 16)])
    c.line(P('gold', '#f2c94c', 9, flat=True), 7, 12, 33, 12, 1.2)
    c.ellipse(P('gold', '#f2c94c', 9, flat=True), 20, 30, 7, 7)
    c.poly(P('gold', '#f2c94c', 9, flat=True), [(20, 20), (24, 30), (20, 42), (16, 30)])
    reg(name, c.render(), cells=[], anchor=(20, h - 6), extra={'foot': [0, 0, 0, 0], 'wall': True})


def stall(color='#d9485a', name='stall_red'):
    c = Canvas(112, 96); P = Pal(c)
    shadow(c, P, 56, 86, 46, 6)
    w = P('w', '#8a5a2a', 5)
    c.rect(w, 8, 30, 14, 84); c.rect(w, 98, 30, 104, 84)
    c.rect(w, 8, 58, 104, 84)
    c.rect(P('top', '#b8864a', 7), 8, 56, 104, 62)
    for i in range(7):
        col = '#ffffff' if i % 2 else color
        c.poly(P('awn_' + str(i % 2), col, 6), [(4 + i * 14, 6), (18 + i * 14, 6), (18 + i * 14, 32), (11 + i * 14, 38), (4 + i * 14, 32)])
    for x, col in ((26, '#ff6f91'), (44, '#ffd166'), (62, '#7ae8a0'), (80, '#8ab4ff')):
        c.ellipse(P('g' + col, col, 8, flat=False), x, 52, 7, 6)
    reg(name, c.render(), cells=[[-1, 0], [0, 0], [1, 0]], anchor=(56, 84), extra={'foot': [-48, -30, 96, 30]})


def tent(color='#d8cdb0', name='tent_a'):
    c = Canvas(128, 112); P = Pal(c)
    shadow(c, P, 64, 102, 52, 7)
    t = P('t', color, 6); td = P('td', color, 5); tl = P('tl', color, 7)
    c.poly(t, [(8, 100), (64, 8), (120, 100)])
    c.poly(td, [(64, 8), (120, 100), (74, 100)])
    c.poly(tl, [(10, 98), (64, 12), (56, 98)])
    c.poly(P('door', '#2a1a22', 3, flat=True), [(48, 100), (56, 56), (72, 56), (80, 100)])
    c.poly(P('flap', color, 7), [(48, 100), (56, 58), (52, 100)])
    c.line(P('pole', '#6a4a2a', 5), 64, 0, 64, 12, 2)
    c.poly(P('flag', '#d9485a', 8), [(65, 2), (80, 6), (65, 11)])
    reg(name, c.render(), cells=[[-1, 0], [0, 0], [1, 0], [0, -1]], anchor=(64, 100), extra={'foot': [-46, -30, 92, 30]})


def cactus(variant=0):
    c = Canvas(48, 80); P = Pal(c)
    shadow(c, P, 24, 74, 12, 4)
    g = P('g', '#4aa850', 6); gd = P('gd', '#4aa850', 5, flat=True)
    c.blob(g, [(18, 74), (17, 20), (24, 8), (31, 20), (30, 74)])
    if variant % 2 == 0:
        c.blob(g, [(18, 52), (8, 50), (6, 30), (12, 28), (14, 44), (18, 44)])
    c.blob(g, [(30, 44), (40, 42), (42, 24), (36, 22), (34, 36), (30, 36)])
    for y in range(14, 70, 6):
        c.line(gd, 24, y, 24, y + 3, 0.8)
    fl = P('fl', '#ff6f91', 9, flat=True)
    c.ellipse(fl, 24, 8, 2.5, 2)
    reg(f'cactus_{variant}', c.render(), anchor=(24, 74), extra={'foot': [-8, -8, 16, 8]})


def haystack():
    c = Canvas(64, 56); P = Pal(c)
    shadow(c, P, 32, 50, 24, 5)
    g = P('g', '#e0b84a', 6); d = P('gd', '#b88a28', 5, flat=True)
    c.blob(g, [(6, 48), (8, 28), (20, 12), (32, 8), (44, 12), (56, 28), (58, 48)])
    for k in range(10):
        x = 12 + k * 4.4
        c.line(d, x, 22 + abs(k - 5) * 2, x - 2, 46, 0.9)
    reg('haystack', c.render(), cells=[[0, 0], [1, 0]], anchor=(32, 50), extra={'foot': [-26, -14, 52, 14]})


def chest(open_=False):
    c = Canvas(40, 36); P = Pal(c)
    shadow(c, P, 20, 32, 15, 3)
    w = P('w', '#9a5a2a', 5); g = P('g', '#f2c94c', 8)
    c.rect(w, 4, 14, 36, 30)
    c.rect(g, 4, 14, 8, 30); c.rect(g, 32, 14, 36, 30); c.rect(g, 4, 20, 36, 23)
    if not open_:
        c.blob(w, [(4, 14), (6, 6), (20, 3), (34, 6), (36, 14)])
        c.rect(g, 4, 10, 36, 13)
        c.rect(P('lock', '#f2c94c', 9), 17, 14, 23, 22); c.ellipse(P('key', '#3a2a1a', 10, flat=True), 20, 18, 1.4, 1.4)
    else:
        c.blob(P('lid', '#7a4a1a', 4), [(4, 12), (6, 3), (20, 0), (34, 3), (36, 12)])
        c.ellipse(P('in', '#1a0a10', 3, flat=True), 20, 14, 15, 4)
        c.ellipse(P('gl', '#ffe888', 10, flat=True), 20, 12, 10, 2.4)
    reg('chest_open' if open_ else 'chest', c.render(), anchor=(20, 31), extra={'foot': [-14, -8, 28, 8]})


def save_crystal(frames=8):
    imgs = []
    for f in range(frames):
        c = Canvas(64, 112); P = Pal(c)
        shadow(c, P, 32, 100, 22, 5)
        s = P('s', '#9a9aa8', 5)
        c.blob(s, [(10, 98), (14, 86), (50, 86), (54, 98), (46, 104), (18, 104)])
        c.ellipse(P('rune', '#7ae8ff', 9, flat=True), 32, 94, 14, 3)
        bob = math.sin(f / frames * 2 * math.pi) * 3
        cy = 46 + bob
        ids = [P('cd', '#7ae8ff', 5), P('cm', '#7ae8ff', 6), P('cl', '#7ae8ff', 8)]
        c.poly(ids[1], [(32, cy - 34), (46, cy - 6), (32, cy + 32), (18, cy - 6)])
        c.poly(ids[0], [(32, cy - 34), (46, cy - 6), (32, cy + 32)])
        c.poly(ids[2], [(32, cy - 30), (22, cy - 6), (26, cy + 6), (30, cy - 8)])
        c.ellipse(P('sp', '#ffffff', 10, flat=True), 26, cy - 14, 2, 3)
        for k in range(4):
            a = f / frames * 2 * math.pi + k * 1.57
            c.ellipse(P('orb', '#bff4ff', 10, flat=True), 32 + math.cos(a) * 22, cy + math.sin(a) * 8 - 4, 1.8, 1.8)
        imgs.append(c.render())
    sheet = Image.new('RGBA', (64 * frames, 112), (0, 0, 0, 0))
    for i, im in enumerate(imgs):
        sheet.alpha_composite(im, (i * 64, 0))
    reg('save_crystal', sheet, anchor=(32, 100), frames=frames, fps=8, extra={'foot': [-18, -12, 36, 12], 'save': True}, light={'r': 150, 'color': '#7ae8ff', 'dy': -48})


def portal(frames=8):
    imgs = []
    for f in range(frames):
        c = Canvas(96, 128); P = Pal(c)
        shadow(c, P, 48, 118, 36, 6)
        st = P('st', '#8a86a0', 5)
        c.rect(st, 6, 20, 20, 116); c.rect(st, 76, 20, 90, 116)
        c.blob(st, [(0, 24), (4, 6), (48, -2), (92, 6), (96, 24), (80, 26), (48, 12), (16, 26)])
        c.rect(st, 0, 112, 96, 124)
        for k in range(32):
            y = 24 + k * 3
            for xx in range(20, 76, 4):
                v = math.sin(xx * 0.18 + f / frames * 6.28 + math.sin(y * 0.12 + f * 0.8) * 2)
                col = '#e0c8ff' if v > 0.55 else '#a06cff' if v > -0.1 else '#6a3ac8'
                c.rect(P('pt' + col, col, 8, flat=True), xx, y, xx + 4, y + 3)
        for k in range(5):
            a = f / frames * 6.28 + k * 1.26
            c.ellipse(P('pp', '#ffffff', 10, flat=True), 48 + math.cos(a) * 18, 70 + math.sin(a * 1.3) * 34, 1.6, 1.6)
        imgs.append(c.render())
    sheet = Image.new('RGBA', (96 * frames, 128), (0, 0, 0, 0))
    for i, im in enumerate(imgs):
        sheet.alpha_composite(im, (i * 96, 0))
    reg('portal', sheet, cells=[], anchor=(48, 118), frames=frames, fps=8, extra={'foot': [-40, -8, 80, 8]}, light={'r': 170, 'color': '#b48cff', 'dy': -56})


def statue():
    c = Canvas(56, 112); P = Pal(c)
    shadow(c, P, 28, 102, 18, 4)
    s = P('s', '#a8a8bc', 5)
    c.rect(s, 6, 88, 50, 104); c.rect(s, 10, 78, 46, 90)
    c.blob(s, [(18, 78), (20, 44), (28, 34), (36, 44), (38, 78)])
    c.ellipse(s, 28, 28, 8, 9)
    c.line(s, 36, 46, 44, 24, 4); c.line(P('sw', '#e0e8f8', 8), 44, 24, 44, 4, 3)
    reg('statue', c.render(), anchor=(28, 102), extra={'foot': [-20, -18, 40, 18]})


def bed():
    c = Canvas(52, 84); P = Pal(c)
    w = P('w', '#a8693a', 5)
    c.rect(w, 0, 2, 52, 84)
    c.rect(P('mat', '#e8e8f8', 7), 3, 8, 49, 80)
    c.rect(P('bl', '#d9485a', 6), 3, 40, 49, 80)
    c.rect(P('pil', '#ffffff', 8), 8, 12, 44, 28)
    reg('bed', c.render(), cells=[[0, 0], [0, -1]], anchor=(26, 84), extra={'foot': [-26, -76, 52, 76]})


def table():
    c = Canvas(72, 56); P = Pal(c)
    shadow(c, P, 36, 52, 28, 4)
    w = P('w', '#a8693a', 5)
    c.blob(w, [(4, 22), (68, 22), (70, 32), (2, 32)])
    for x in (8, 60):
        c.rect(P('leg', '#7a4a2a', 4), x, 32, x + 5, 50)
    c.ellipse(P('cup', '#d9d9e8', 9), 22, 20, 5, 3); c.ellipse(P('ap', '#e86a6a', 8), 50, 20, 4, 3)
    reg('table', c.render(), cells=[[0, 0], [1, 0]], anchor=(36, 52), extra={'foot': [-30, -16, 60, 16]})


def bookshelf():
    c = Canvas(72, 100); P = Pal(c)
    w = P('w', '#7a4a2a', 5); d = P('d', '#4a2a18', 3, flat=True)
    c.rect(w, 0, 0, 72, 98)
    c.rect(d, 4, 4, 68, 94)
    cols = ['#d9485a', '#4a9af0', '#f2c94c', '#6fd1a0', '#a06cff', '#e8703a']
    rng = np.random.default_rng(3)
    for sh in range(3):
        y0 = 6 + sh * 30
        x = 6
        while x < 64:
            wd = int(rng.integers(4, 8)); hh = int(rng.integers(18, 25))
            c.rect(P('b%d' % int(rng.integers(0, 6)), cols[int(rng.integers(0, 6))], 6), x, y0 + 26 - hh, x + wd, y0 + 26)
            x += wd + 1
        c.rect(w, 4, y0 + 26, 68, y0 + 30)
    reg('bookshelf', c.render(), cells=[[0, 0], [1, 0]], anchor=(36, 98), extra={'foot': [-34, -14, 68, 14], 'wall': True})


def gate_arch():
    c = Canvas(160, 128); P = Pal(c)
    s = P('s', '#c0a070', 5); sd = P('sd', '#c0a070', 4, flat=True)
    c.rect(s, 0, 20, 40, 124); c.rect(s, 120, 20, 160, 124)
    c.rect(s, 0, 0, 160, 34)
    for x in range(4, 156, 18):
        c.rect(P('mer', '#c0a070', 6), x, -2, x + 10, 10)
    for y in range(40, 124, 12):
        c.line(sd, 0, y, 40, y, 0.8); c.line(sd, 120, y, 160, y, 0.8)
    reg('gate_arch', c.render(), cells=[[-2, 0], [2, 0], [-2, -1], [2, -1], [-2, -2], [2, -2], [-1, -3], [0, -3], [1, -3], [-2, -3], [2, -3]], anchor=(80, 124), extra={'foot': [0, 0, 0, 0]})


def woodpile():
    c = Canvas(48, 40); P = Pal(c)
    shadow(c, P, 24, 36, 18, 3)
    w = P('w', '#8a5a2a', 5); e = P('e', '#d9b070', 8, flat=True)
    for r in range(3):
        for k in range(4 - r):
            x = 8 + k * 9 + r * 4.5; y = 30 - r * 8
            c.ellipse(w, x, y, 5, 4.2); c.ellipse(e, x, y, 2.6, 2.2)
    reg('woodpile', c.render(), anchor=(24, 36), extra={'foot': [-18, -10, 36, 10]})


def mailbox():
    c = Canvas(24, 44); P = Pal(c)
    shadow(c, P, 12, 40, 7, 2)
    c.rect(P('post', '#6a4a2a', 5), 10, 20, 14, 40)
    c.blob(P('box', '#c9283a', 6), [(2, 8), (22, 8), (22, 20), (2, 20)])
    c.rect(P('flag', '#f2c94c', 8), 20, 4, 23, 12)
    reg('mailbox', c.render(), anchor=(12, 40), extra={'foot': [-5, -5, 10, 5]})


def flowerbed(variant=0):
    c = Canvas(64, 36); P = Pal(c)
    soil = P('soil', '#6a4a2a', 4)
    c.blob(soil, [(2, 16), (6, 8), (58, 8), (62, 16), (58, 28), (6, 28)])
    rng = np.random.default_rng(variant + 20)
    cols = ['#ff6f91', '#ffd166', '#b39dff', '#ffffff']
    gr = P('stem', '#3f8a3a', 5)
    for k in range(14):
        x = 6 + k * 4 + rng.uniform(-1, 1); y = 12 + rng.uniform(0, 10)
        c.line(gr, x, y + 3, x, y + 7, 0.9)
        c.ellipse(P('f%d' % (k % 4), cols[(k + variant) % 4], 9), x, y, 2.4, 2.4)
    reg(f'flowerbed_{variant}', c.render(), cells=[[0, 0], [1, 0]], anchor=(32, 28), extra={'foot': [-28, -14, 56, 14]})


def cart():
    c = Canvas(80, 64); P = Pal(c)
    shadow(c, P, 40, 58, 30, 4)
    w = P('w', '#8a5a2a', 5)
    c.blob(w, [(6, 28), (74, 28), (72, 48), (8, 48)])
    for x in (16, 30, 44, 58):
        c.line(P('gr', '#5a3a1a', 4, flat=True), x, 29, x, 47, 0.8)
    for x in (16, 62):
        c.ellipse(P('wh', '#4a2a10', 4), x, 50, 9, 9); c.ellipse(P('wh2', '#8a5a2a', 6), x, 50, 6.5, 6.5); c.ellipse(P('hub', '#4a2a10', 4), x, 50, 2, 2)
    for x, col in ((22, '#e86a3a'), (36, '#e8c43a'), (50, '#7ac04a'), (62, '#e86a3a')):
        c.ellipse(P('g' + col, col, 7), x, 24, 8, 7)
    reg('cart', c.render(), cells=[[0, 0], [1, 0]], anchor=(40, 58), extra={'foot': [-34, -16, 68, 16]})


def sack(variant=0):
    c = Canvas(32, 36); P = Pal(c)
    shadow(c, P, 16, 32, 11, 3)
    s = P('s', '#c8b088', 6)
    c.blob(s, [(6, 28), (5, 16), (11, 8), (21, 8), (27, 16), (26, 28), (16, 31)])
    c.line(P('tie', '#8a6a3a', 4, flat=True), 11, 9, 21, 9, 2)
    reg(f'sack_{variant}', c.render(), anchor=(16, 31), extra={'foot': [-10, -8, 20, 8]})


def anvil():
    c = Canvas(48, 40); P = Pal(c)
    shadow(c, P, 24, 36, 16, 3)
    m = P('m', '#6a6a7a', 6)
    c.blob(m, [(6, 14), (42, 14), (36, 20), (30, 22), (30, 30), (36, 34), (12, 34), (18, 30), (18, 22), (12, 20)])
    c.rect(P('t', '#8a8a9a', 8), 8, 10, 42, 15)
    reg('anvil', c.render(), anchor=(24, 34), extra={'foot': [-16, -10, 32, 10]})


def bench():
    c = Canvas(64, 36); P = Pal(c)
    shadow(c, P, 32, 32, 24, 3)
    w = P('w', '#a8693a', 5)
    c.rect(w, 4, 12, 60, 20); c.rect(w, 4, 22, 60, 26)
    for x in (8, 52):
        c.rect(P('l', '#6a4228', 4), x, 20, x + 4, 32)
    reg('bench', c.render(), cells=[[0, 0], [1, 0]], anchor=(32, 32), extra={'foot': [-26, -12, 52, 12]})


def ladder_prop():
    pass


# --------------------------------------------------------------- buildings
def house(wt=5, roof='#c9483a', wall='#f2e4c8', style='timber', name=None, door=True, chimney=True, seed=1):
    rng = np.random.default_rng(seed)
    W = wt * 32 + 16
    H = 176
    c = Canvas(W, H); P = Pal(c)
    x0 = 8
    bw = wt * 32
    top_wall = 76
    base = H - 6
    shadow(c, P, W / 2, base - 1, bw / 2 + 4, 6)
    # --- walls
    wl = P('wall', wall, 5); wd = P('wall_d', wall, 4, flat=True); wh = P('wall_h', wall, 6, flat=True)
    c.rect(wl, x0, top_wall, x0 + bw, base - 6)
    # plaster stripes / timber frame
    timber = P('timber', '#6a4228', 6)
    stone = P('stone', '#7a7888', 4)
    c.rect(stone, x0 - 1, base - 18, x0 + bw + 1, base - 4)
    for i in range(0, bw, 12):
        c.line(P('stone_j', '#4a4858', 3, flat=True), x0 + i, base - 18, x0 + i, base - 4, 0.8)
    c.line(P('stone_j', '#4a4858', 3, flat=True), x0 - 1, base - 11, x0 + bw + 1, base - 11, 0.8)
    if style == 'timber':
        for i in range(wt + 1):
            c.rect(timber, x0 + i * 32 - 2, top_wall, x0 + i * 32 + 2, base - 18)
        c.rect(timber, x0, top_wall, x0 + bw, top_wall + 4)
        c.rect(timber, x0, base - 52, x0 + bw, base - 48)
        for i in range(wt):
            if i % 2 == 0:
                c.line(timber, x0 + i * 32 + 2, base - 52, x0 + i * 32 + 30, top_wall + 4, 2)
    for y in range(top_wall + 6, base - 20, 8):
        c.line(wd, x0, y, x0 + bw, y, 0.7)
    # --- door
    dc = x0 + (wt // 2) * 32 + 16
    if door:
        c.blob(P('door', '#6a4228', 5), [(dc - 12, base - 6), (dc - 12, base - 42), (dc - 8, base - 52), (dc, base - 56), (dc + 8, base - 52), (dc + 12, base - 42), (dc + 12, base - 6)])
        c.blob(P('door_in', '#8a5a30', 6), [(dc - 9, base - 7), (dc - 9, base - 41), (dc, base - 52), (dc + 9, base - 41), (dc + 9, base - 7)])
        for x in (dc - 4, dc + 1, dc + 5):
            c.line(P('dg', '#5a3a1a', 4, flat=True), x, base - 12, x, base - 44, 0.7)
        c.ellipse(P('knob', '#f2c94c', 9, flat=True), dc + 6, base - 24, 1.4, 1.4)
        c.rect(P('step', '#9a98a8', 6), dc - 15, base - 5, dc + 15, base)
        c.line(P('lamp', '#ffe9a0', 9, flat=True), dc - 18, base - 46, dc - 18, base - 40, 2)
    # --- windows
    def window(wx, wy):
        c.rect(P('wfr', '#4a2a18', 3), wx - 11, wy - 2, wx + 11, wy + 26)
        c.rect(P('glass', '#ffe9a0', 9, flat=True), wx - 9, wy, wx + 9, wy + 24)
        c.rect(P('glass2', '#fff6cf', 10, flat=True), wx - 9, wy, wx + 9, wy + 8)
        c.line(P('mull', '#4a2a18', 3, flat=True), wx, wy, wx, wy + 24, 1.2)
        c.line(P('mull', '#4a2a18', 3, flat=True), wx - 9, wy + 12, wx + 9, wy + 12, 1.2)
        c.rect(P('sill', '#6a4228', 5), wx - 13, wy + 25, wx + 13, wy + 29)
        for k, col in enumerate(('#ff6f91', '#ffd166', '#ff6f91', '#b39dff')):
            c.ellipse(P('fb%d' % k, col, 9, flat=True), wx - 9 + k * 6, wy + 27, 2.2, 2.2)
        shut = P('shut', '#3a7bd5' if roof != '#3a7bd5' else '#c9483a', 6)
        c.rect(shut, wx - 17, wy - 1, wx - 12, wy + 25); c.rect(shut, wx + 12, wy - 1, wx + 17, wy + 25)
    wxs = [x0 + 32 * k + 16 for k in range(wt) if (k != wt // 2)]
    for wx in wxs[:: 1 if wt > 4 else 2]:
        window(wx, base - 56) if False else window(wx, top_wall + 18)
    # --- roof
    rd = P('r_d', roof, 5); rm = P('r_m', roof, 6); rl = P('r_l', roof, 7); rk = P('r_k', roof, 4, flat=True)
    roof_top = 8
    roof_bot = top_wall + 6
    over = 10
    rows = 9
    for r in range(rows):
        t0 = r / rows; t1 = (r + 1) / rows
        y0 = roof_top + (roof_bot - roof_top) * t0
        y1 = roof_top + (roof_bot - roof_top) * t1
        inset0 = (1 - t0) * (bw / 2 - 18) + 0
        inset1 = (1 - t1) * (bw / 2 - 18) + 0
        xl0, xr0 = x0 - over + inset0, x0 + bw + over - inset0
        xl1, xr1 = x0 - over + inset1, x0 + bw + over - inset1
        c.poly(rm if r % 2 == 0 else rd, [(xl0, y0), (xr0, y0), (xr1, y1 + 1), (xl1, y1 + 1)])
        # shingles
        n = max(4, int((xr1 - xl1) / 10))
        for k in range(n):
            xs = xl1 + (xr1 - xl1) * (k + (0.5 if r % 2 else 0)) / n
            c.blob(rl if (k + r) % 3 == 0 else rm, [(xs - 4, y0 + 1), (xs + 4, y0 + 1), (xs + 4.5, y1 - 1), (xs, y1 + 1.5), (xs - 4.5, y1 - 1)]) if False else None
            c.line(rk, xs, y0, xs, y1, 0.7)
        c.line(rk, xl1, y1, xr1, y1, 0.9)
    c.poly(rl, [(x0 + bw / 2 - 18, roof_top), (x0 + bw / 2 + 18, roof_top), (x0 + bw / 2 + 24, roof_top + 6), (x0 + bw / 2 - 24, roof_top + 6)])
    # eaves shadow
    c.rect(P('eave', '#000000', 5, flat=True), x0 - over, roof_bot, x0 + bw + over, roof_bot + 3)
    if chimney:
        cx2 = x0 + bw - 40
        c.rect(P('chim', '#8a7a8a', 6), cx2, 0, cx2 + 16, 46)
        c.rect(P('chim_t', '#a89aa8', 8), cx2 - 2, 0, cx2 + 18, 5)
    img = c.render()
    cells = [[xx, yy] for yy in range(-3, 1) for xx in range(wt)]
    nm = name or f'house{wt}_{style}_{roof.strip("#")}'
    reg(nm, img, cells=cells, anchor=(W // 2, base), extra={'door': [wt // 2, 0], 'foot': [0, 0, 0, 0]})
    return nm


def build(outdir):
    os.makedirs(outdir, exist_ok=True)
    for v in range(3):
        tree('oak', v)
    for v in range(2):
        tree('pine', v); tree('autumn', v); tree('dead', v); tree('fruit', v)
    tree('crystal', 0); tree('palm', 0); tree('willow', 0)
    bush(0); bush(1, flowers=True); bush(2, '#5aa84a'); bush(3, '#2f7a4a')
    rock('rock_s', '#8a8a9a', 36, 30, 1); rock('rock_m', '#8a8a9a', 52, 42, 2); rock('rock_l', '#7a7a8a', 72, 58, 3); rock('cave_rock', '#5a5270', 44, 36, 4)
    rock('sand_rock', '#b09a70', 48, 38, 5); rock('snow_rock', '#b8c8d8', 48, 38, 6)
    crystal('crystal_c', '#66e6ff'); crystal('crystal_r', '#ff6a8a', 1); crystal('crystal_v', '#b48cff', 2)
    stalagmite(0); stalagmite(1)
    barrel(); crate(1); crate(2); crate(3)
    for v in range(4):
        jar(v)
    sack(0); sack(1)
    sign(); fence('h'); fence('v')
    lamp(); torch(); campfire(); well(); fountain()
    banner('#3a7bd5', 'banner_blue'); banner('#c9283a', 'banner_red'); banner('#2f7a4a', 'banner_green', True)
    stall('#d9485a', 'stall_red'); stall('#3a7bd5', 'stall_blue')
    tent('#d8cdb0', 'tent_a'); tent('#c9483a', 'tent_b'); tent('#6a8ab8', 'tent_c')
    cactus(0); cactus(1); haystack(); chest(False); chest(True)
    save_crystal(); portal(); statue(); bed(); table(); bookshelf(); gate_arch()
    woodpile(); mailbox(); flowerbed(0); flowerbed(1); flowerbed(2); cart(); anvil(); bench()
    # houses
    for (wt, roof, wall, seed) in ((5, '#c9483a', '#f2e4c8', 1), (6, '#3a7bd5', '#e8d8b8', 2), (4, '#8a5ad0', '#dcdcf0', 3), (5, '#d9922e', '#f0e0c0', 4), (6, '#2f9a6a', '#e8e0d0', 5), (4, '#c9483a', '#e8d8b8', 6)):
        house(wt, roof, wall, 'timber', seed=seed)
    for n, im in IMGS.items():
        im.save(os.path.join(outdir, n + '.png'))
    json.dump(OBJ, open(os.path.join(outdir, 'objects.json'), 'w'), indent=0)
    return OBJ


if __name__ == '__main__':
    out = sys.argv[1] if len(sys.argv) > 1 else '/tmp/obj'
    o = build(out)
    print(len(o), 'objects')
