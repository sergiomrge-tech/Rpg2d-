"""48x48 item/skill icons."""
import math, os, sys
import numpy as np
from PIL import Image
sys.path.insert(0, os.path.dirname(__file__))
from pix import Canvas, Part, ramp
from objects import Pal

N = 48
ICONS = {}


def icon(name):
    def deco(fn):
        ICONS[name] = fn
        return fn
    return deco


def mk():
    c = Canvas(N, N)
    return c, Pal(c)


def sword_shape(c, P, x0, y0, x1, y1, blade='#cfd8ec', hilt='#c9a050'):
    c.line(P('bd', blade, 6), x0, y0, x1, y1, 5.5)
    c.line(P('bl', '#ffffff', 9, flat=True), x0 + 0.5, y0 - 0.5, x1 + 0.5, y1 - 0.5, 1.6)
    dx, dy = x1 - x0, y1 - y0
    L = math.hypot(dx, dy)
    ux, uy = dx / L, dy / L
    gx, gy = x0 + ux * 3, y0 + uy * 3
    c.line(P('hl', hilt, 8), gx - uy * 8, gy + ux * 8, gx + uy * 8, gy - ux * 8, 3.0)
    c.line(P('hd', '#7a4a2a', 6), x0 - ux * 1, y0 - uy * 1, x0 - ux * 9, y0 - uy * 9, 4)
    c.ellipse(P('pm', hilt, 8), x0 - ux * 10, y0 - uy * 10, 3, 3)


@icon('sword')
def _():
    c, P = mk(); sword_shape(c, P, 14, 34, 38, 10); return c


@icon('blades')
def _():
    c, P = mk(); sword_shape(c, P, 12, 34, 34, 12); sword_shape(c, P, 36, 34, 14, 12, '#aebde0'); return c


@icon('slash')
def _():
    c, P = mk()
    for k, col in enumerate(('#6ab0ff', '#bfe4ff', '#ffffff')):
        pts = []
        for i in range(21):
            a = -0.5 + i * 0.075
            r = 22 - k * 3
            pts.append((10 + r * math.cos(a) * 1.2, 36 - r * math.sin(a) * 1.5))
        for i in range(20, -1, -1):
            a = -0.5 + i * 0.075
            r = 22 - k * 3 - 5 * math.sin(math.pi * i / 20) * (1 - k * 0.3)
            pts.append((10 + r * math.cos(a) * 1.2, 36 - r * math.sin(a) * 1.5))
        c.poly(P('s%d' % k, col, 6 + k, flat=k > 0), pts)
    return c


@icon('whirl')
def _():
    c, P = mk()
    for k in range(3):
        a0 = k * 2.1
        pts = [(24 + 18 * math.cos(a0 + t * 0.12), 24 + 18 * math.sin(a0 + t * 0.12)) for t in range(14)]
        pts += [(24 + 11 * math.cos(a0 + t * 0.12), 24 + 11 * math.sin(a0 + t * 0.12)) for t in range(13, -1, -1)]
        c.poly(P('w%d' % k, '#bfe4ff', 6), pts)
    c.ellipse(P('wc', '#ffffff', 9, flat=True), 24, 24, 3, 3)
    return c


@icon('dash')
def _():
    c, P = mk()
    for i, (y, w) in enumerate(((14, 18), (22, 24), (30, 16))):
        c.poly(P('d%d' % i, '#8ac8ff', 5 + i), [(4, y), (4 + w, y - 2), (4 + w + 6, y + 2), (4, y + 3)])
    sword_shape(c, P, 20, 36, 42, 10)
    return c


@icon('slam')
def _():
    c, P = mk()
    c.line(P('h', '#7a4a2a', 5), 24, 6, 24, 30, 4)
    c.blob(P('hm', '#9aa4b8', 7), [(10, 24), (14, 16), (34, 16), (38, 24), (34, 32), (14, 32)])
    c.line(P('cr', '#c9a070', 6), 4, 42, 44, 42, 3)
    for x in (10, 20, 30, 40):
        c.line(P('cr2', '#c9a070', 6), x, 42, x + 2, 36, 2)
    return c


@icon('fire')
def _():
    c, P = mk()
    c.blob(P('f1', '#ff6a1a', 7), [(24, 4), (34, 18), (38, 30), (30, 42), (18, 42), (10, 30), (14, 18), (20, 24)])
    c.blob(P('f2', '#ffa82a', 8), [(24, 16), (30, 26), (31, 34), (24, 42), (17, 34), (18, 26)])
    c.blob(P('f3', '#fff2b0', 10, flat=True), [(24, 28), (27, 34), (24, 40), (21, 34)])
    return c


@icon('ice')
def _():
    c, P = mk()
    for a in range(0, 180, 60):
        r = math.radians(a)
        c.line(P('i1', '#8ae0ff', 7), 24 - 20 * math.cos(r), 24 - 20 * math.sin(r), 24 + 20 * math.cos(r), 24 + 20 * math.sin(r), 3.4)
    for a in range(0, 360, 60):
        r = math.radians(a)
        c.line(P('i2', '#dff4ff', 9), 24 + 11 * math.cos(r), 24 + 11 * math.sin(r), 24 + 17 * math.cos(r + 0.5), 24 + 17 * math.sin(r + 0.5), 2)
    c.ellipse(P('ic', '#ffffff', 10, flat=True), 24, 24, 3, 3)
    return c


@icon('bolt')
def _():
    c, P = mk()
    c.poly(P('b1', '#ffd84a', 8), [(30, 3), (12, 26), (22, 26), (16, 45), (38, 20), (27, 20), (34, 3)])
    c.poly(P('b2', '#fff6a0', 10, flat=True), [(28, 8), (17, 25), (25, 25), (21, 37), (33, 21), (25, 21), (30, 8)])
    return c


@icon('nova')
def _():
    c, P = mk()
    for r, col in ((20, '#5ac8ff'), (14, '#8ae0ff'), (8, '#dff4ff')):
        c.ellipse(P('n%d' % r, col, 6), 24, 24, r, r)
        c.ellipse(P('x%d' % r, '#0d1840', 0, flat=True), 24, 24, r - 3, r - 3) if r > 8 else None
    for a in range(0, 360, 45):
        t = math.radians(a)
        c.poly(P('sp', '#ffffff', 9), [(24 + 8 * math.cos(t - 0.15), 24 + 8 * math.sin(t - 0.15)), (24 + 22 * math.cos(t), 24 + 22 * math.sin(t)), (24 + 8 * math.cos(t + 0.15), 24 + 8 * math.sin(t + 0.15))])
    return c


@icon('meteor')
def _():
    c, P = mk()
    c.poly(P('t1', '#ff8a2a', 6), [(4, 4), (30, 22), (22, 30)])
    c.poly(P('t2', '#ffd84a', 8), [(8, 8), (26, 22), (22, 26)])
    c.ellipse(P('m', '#7a4a3a', 6), 31, 31, 13, 13)
    c.ellipse(P('mh', '#c08a60', 8), 27, 27, 5, 4)
    c.ellipse(P('mc', '#3a2418', 4, flat=True), 35, 33, 3, 3)
    return c


@icon('heal')
def _():
    c, P = mk()
    c.blob(P('h', '#58e08a', 6), [(18, 4), (30, 4), (30, 18), (44, 18), (44, 30), (30, 30), (30, 44), (18, 44), (18, 30), (4, 30), (4, 18), (18, 18)])
    c.rect(P('hh', '#c8ffd8', 9, flat=True), 20, 8, 24, 20)
    for (x, y) in ((8, 8), (40, 10), (38, 40)):
        c.poly(P('st', '#ffffff', 10, flat=True), [(x, y - 3), (x + 1, y), (x + 3, y), (x + 1, y + 1), (x, y + 3), (x - 1, y + 1), (x - 3, y), (x - 1, y)])
    return c


@icon('shield')
def _():
    c, P = mk()
    c.blob(P('s', '#5a8aff', 6), [(24, 3), (42, 9), (42, 26), (24, 45), (6, 26), (6, 9)])
    c.blob(P('s2', '#9ac0ff', 8), [(24, 9), (36, 13), (36, 25), (24, 38), (12, 25), (12, 13)])
    c.rect(P('sx', '#fff2b0', 9), 22, 12, 26, 34); c.rect(P('sx', '#fff2b0', 9), 15, 20, 33, 24)
    return c


@icon('rage')
def _():
    c, P = mk()
    c.ellipse(P('r', '#e8453c', 6), 24, 26, 16, 16)
    c.ellipse(P('rh', '#ff8a6a', 8), 20, 20, 6, 4)
    for x in (13, 24, 35):
        c.poly(P('fl', '#ffb04a', 8), [(x - 4, 14), (x, 2), (x + 4, 14)])
    c.line(P('br', '#2a0a10', 5), 14, 20, 22, 24, 2.4); c.line(P('br', '#2a0a10', 5), 34, 20, 26, 24, 2.4)
    c.rect(P('mo', '#2a0a10', 5), 18, 33, 30, 36)
    return c


@icon('ghost')
def _():
    c, P = mk()
    c.blob(P('g', '#d8c8ff', 6), [(24, 4), (38, 10), (40, 30), (44, 44), (36, 40), (30, 44), (24, 40), (18, 44), (12, 40), (4, 44), (8, 30), (10, 10)])
    c.ellipse(P('e', '#2a1a4a', 4, flat=True), 18, 20, 3, 4); c.ellipse(P('e', '#2a1a4a', 4, flat=True), 30, 20, 3, 4)
    c.ellipse(P('m', '#2a1a4a', 4, flat=True), 24, 30, 3, 3)
    return c


@icon('spirit')
def _():
    c, P = mk()
    for i in range(3):
        a = i * 2.1
        x, y = 24 + 12 * math.cos(a), 24 + 12 * math.sin(a)
        c.poly(P('tr', '#6affc0', 6), [(x, y), (x - 8 * math.cos(a + 0.8), y - 8 * math.sin(a + 0.8)), (x - 10 * math.cos(a + 1.5), y - 10 * math.sin(a + 1.5))])
        c.ellipse(P('o', '#a0ffd8', 8), x, y, 6, 6)
        c.ellipse(P('oc', '#ffffff', 10, flat=True), x - 1.5, y - 1.5, 2, 2)
    return c


def potion(color, name, elixir=False):
    @icon(name)
    def _():
        c, P = mk()
        c.rect(P('cork', '#8a5a2a', 5), 19, 4, 29, 11)
        c.rect(P('neck', '#cfe0f0', 7), 20, 10, 28, 20)
        c.blob(P('glass', '#cfe0f0', 7), [(24, 16), (38, 28), (38, 38), (30, 45), (18, 45), (10, 38), (10, 28)])
        c.blob(P('liq', color, 6), [(24, 22), (35, 31), (35, 38), (29, 43), (19, 43), (13, 38), (13, 31)])
        c.ellipse(P('hl', '#ffffff', 10, flat=True), 17, 31, 2.5, 4)
        if elixir:
            for (x, y) in ((32, 28), (20, 38), (28, 40)):
                c.ellipse(P('sp', '#fff2b0', 10, flat=True), x, y, 1.6, 1.6)
        return c
potion('#ff4a6a', 'potion_r'); potion('#4a8aff', 'potion_b'); potion('#d86aff', 'elixir', True)


@icon('herb')
def _():
    c, P = mk()
    c.line(P('st', '#3f8a3a', 5), 24, 44, 24, 10, 2.4)
    for i, (y, s) in enumerate(((14, -1), (22, 1), (30, -1), (38, 1))):
        c.blob(P('lf', '#5aa84a', 7), [(24, y), (24 + s * 14, y - 6), (24 + s * 18, y + 2), (24 + s * 8, y + 5)])
    c.ellipse(P('fl', '#ffffff', 10, flat=True), 24, 7, 3, 3)
    return c


@icon('gem')
def _():
    c, P = mk()
    c.poly(P('g1', '#ff6ad0', 6), [(24, 44), (6, 20), (14, 8), (34, 8), (42, 20)])
    c.poly(P('g2', '#ff9ae0', 8), [(14, 8), (24, 20), (34, 8)])
    c.poly(P('g3', '#c0309a', 5), [(24, 44), (24, 20), (42, 20)])
    c.ellipse(P('gs', '#ffffff', 10, flat=True), 15, 15, 2, 3)
    return c


@icon('key')
def _():
    c, P = mk()
    c.ellipse(P('k', '#f2c94c', 8), 15, 15, 9, 9); c.ellipse(P('kh', '#1a0f2a', 2, flat=True), 15, 15, 4, 4)
    c.line(P('k2', '#f2c94c', 7), 22, 22, 40, 40, 4)
    c.line(P('k2', '#f2c94c', 7), 34, 34, 40, 28, 4); c.line(P('k2', '#f2c94c', 7), 38, 38, 44, 32, 4)
    return c


@icon('coin')
def _():
    c, P = mk()
    c.ellipse(P('c1', '#c0902a', 5), 24, 24, 19, 19)
    c.ellipse(P('c2', '#ffd84a', 8), 24, 24, 16, 16)
    c.ellipse(P('c3', '#f2b82a', 6), 24, 24, 11, 11)
    c.rect(P('c4', '#c0902a', 5), 22, 14, 26, 34)
    c.ellipse(P('c5', '#ffffff', 10, flat=True), 16, 14, 3, 2)
    return c


def armor(color, name, robe=False):
    @icon(name)
    def _():
        c, P = mk()
        if robe:
            c.blob(P('r', color, 6), [(16, 6), (32, 6), (40, 16), (36, 44), (12, 44), (8, 16)])
            c.rect(P('rb', '#f2c94c', 8), 22, 6, 26, 44)
            c.rect(P('bl', '#8a5a2a', 6), 12, 28, 36, 31)
        else:
            c.blob(P('a', color, 6), [(12, 8), (36, 8), (46, 16), (40, 26), (38, 42), (10, 42), (8, 26), (2, 16)])
            c.blob(P('a2', color, 8), [(14, 10), (22, 10), (20, 38), (12, 38), (10, 24)])
            c.rect(P('bt', '#f2c94c', 8), 10, 28, 38, 32)
            c.ellipse(P('hole', '#1a0f2a', 1, flat=True), 24, 9, 6, 3)
        return c
armor('#9aa8c0', 'armor'); armor('#8a6ad0', 'robe', True)


@icon('ring')
def _():
    c, P = mk()
    c.ellipse(P('b', '#f2c94c', 7), 24, 28, 14, 14); c.ellipse(P('i', '#0d0820', 0, flat=True), 24, 28, 9, 9)
    c.poly(P('g', '#4af0ff', 9), [(24, 6), (30, 12), (24, 18), (18, 12)])
    c.ellipse(P('gs', '#ffffff', 10, flat=True), 22, 10, 1.6, 1.6)
    return c


@icon('amulet')
def _():
    c, P = mk()
    c.line(P('ch', '#f2c94c', 7), 8, 4, 24, 30, 2.2); c.line(P('ch', '#f2c94c', 7), 40, 4, 24, 30, 2.2)
    c.blob(P('fr', '#f2c94c', 8), [(24, 24), (34, 32), (24, 46), (14, 32)])
    c.blob(P('gm', '#ff4a6a', 7), [(24, 28), (30, 33), (24, 42), (18, 33)])
    c.ellipse(P('gs', '#ffffff', 10, flat=True), 22, 31, 1.6, 2)
    return c


@icon('boots')
def _():
    c, P = mk()
    c.blob(P('b', '#8a5a2a', 6), [(14, 4), (28, 4), (28, 28), (42, 34), (44, 42), (10, 42), (10, 28)])
    c.rect(P('c', '#f2c94c', 8), 14, 4, 28, 9)
    c.rect(P('s', '#4a2a10', 4), 8, 40, 44, 45)
    return c


@icon('star')
def _():
    c, P = mk()
    pts = []
    for i in range(10):
        a = -math.pi / 2 + i * math.pi / 5
        r = 21 if i % 2 == 0 else 9
        pts.append((24 + r * math.cos(a), 25 + r * math.sin(a)))
    c.poly(P('s', '#ffd84a', 8), pts)
    c.ellipse(P('sc', '#fff6b0', 10, flat=True), 24, 25, 5, 5)
    return c


@icon('scroll')
def _():
    c, P = mk()
    c.rect(P('p', '#f2e4c8', 8), 8, 8, 40, 40)
    c.blob(P('r1', '#c0a070', 6), [(4, 6), (44, 6), (44, 11), (4, 11)]); c.blob(P('r1', '#c0a070', 6), [(4, 37), (44, 37), (44, 42), (4, 42)])
    for y in range(15, 36, 5):
        c.line(P('t', '#8a6a4a', 4, flat=True), 12, y, 36, y, 1.4)
    return c


@icon('crystal')
def _():
    c, P = mk()
    c.poly(P('c1', '#66e6ff', 6), [(24, 3), (38, 18), (24, 45), (10, 18)])
    c.poly(P('c2', '#3a9ad8', 5), [(24, 3), (38, 18), (24, 45)])
    c.poly(P('c3', '#bff4ff', 9, flat=True), [(24, 8), (14, 18), (18, 28), (22, 14)])
    return c


@icon('fang')
def _():
    c, P = mk()
    c.poly(P('f1', '#f2e8d8', 7), [(14, 6), (34, 6), (30, 22), (22, 44), (16, 22)])
    c.poly(P('f2', '#c8b8a0', 5), [(26, 6), (34, 6), (30, 22), (22, 44)])
    c.rect(P('fb', '#8a5a2a', 5), 12, 4, 36, 10)
    return c


@icon('core')
def _():
    c, P = mk()
    c.ellipse(P('o', '#58e08a', 6), 24, 25, 18, 18)
    c.ellipse(P('o2', '#a0ffc0', 9, flat=True), 24, 25, 10, 10)
    c.ellipse(P('oh', '#ffffff', 10, flat=True), 17, 17, 3.5, 2.5)
    return c


@icon('cloth')
def _():
    c, P = mk()
    c.blob(P('c', '#e8e4f0', 7), [(6, 10), (40, 6), (44, 38), (10, 42)])
    for y in (16, 24, 32):
        c.line(P('f', '#c8c4d8', 5, flat=True), 8, y, 40, y + 1, 1.2)
    return c


@icon('staff')
def _():
    c, P = mk()
    c.line(P('s', '#8a5a2a', 5), 10, 44, 32, 16, 4)
    c.ellipse(P('o', '#b48cff', 8), 36, 12, 8, 8); c.ellipse(P('oc', '#ffffff', 10, flat=True), 34, 10, 2.4, 2.4)
    return c


@icon('book')
def _():
    c, P = mk()
    c.rect(P('b', '#6a4aa8', 6), 6, 6, 42, 42)
    c.rect(P('b2', '#8a6ad0', 8), 6, 6, 42, 11)
    c.rect(P('pg', '#f2e4c8', 8), 10, 12, 40, 40)
    c.line(P('t', '#8a6a4a', 4, flat=True), 14, 20, 34, 20, 1.4); c.line(P('t', '#8a6a4a', 4, flat=True), 14, 26, 34, 26, 1.4); c.line(P('t', '#8a6a4a', 4, flat=True), 14, 32, 28, 32, 1.4)
    c.ellipse(P('gm', '#f2c94c', 9), 38, 38, 4, 4)
    return c


@icon('heart')
def _():
    c, P = mk()
    c.blob(P('h', '#ff4a6a', 6), [(24, 40), (6, 24), (6, 12), (16, 6), (24, 14), (32, 6), (42, 12), (42, 24)])
    c.ellipse(P('hh', '#ffb0c0', 10, flat=True), 14, 13, 3, 2)
    return c


@icon('mana_orb')
def _():
    c, P = mk()
    c.ellipse(P('o', '#5a9aff', 6), 24, 25, 17, 17)
    c.ellipse(P('o2', '#a8d0ff', 8, flat=True), 24, 28, 10, 8)
    c.ellipse(P('oh', '#ffffff', 10, flat=True), 17, 17, 3.5, 2.5)
    return c


def build(outdir):
    os.makedirs(outdir, exist_ok=True)
    for n, fn in ICONS.items():
        fn().render().save(os.path.join(outdir, n + '.png'))
    return list(ICONS)


if __name__ == '__main__':
    out = sys.argv[1] if len(sys.argv) > 1 else '/tmp/icons'
    names = build(out)
    sheet = Image.new('RGBA', (8 * 56, ((len(names) + 7) // 8) * 56), (40, 30, 70, 255))
    for i, n in enumerate(names):
        sheet.alpha_composite(Image.open(f'{out}/{n}.png'), ((i % 8) * 56 + 4, (i // 8) * 56 + 4))
    sheet.resize((sheet.width * 2, sheet.height * 2), Image.NEAREST).save('/tmp/icons_prev.png')
    print(len(names))
