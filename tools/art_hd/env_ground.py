"""Painted ground baker: terrain grid -> large HD ground image split into chunks.

Terrain codes: g grass, d dirt path, s stone plaza, w water, t tilled soil, b bridge deck (water underneath, walkable)
"""
from __future__ import annotations
import math
import random
import cairo
import numpy as np
from PIL import Image
from scipy import ndimage

T = 64


def noise(h, w, scale, seed):
    rng = np.random.default_rng(seed)
    small = rng.random((h // scale + 3, w // scale + 3)).astype(np.float32)
    big = ndimage.zoom(small, scale, order=3)[:h, :w]
    big = (big - big.min()) / max(1e-6, big.max() - big.min())
    return big


def fbm(h, w, seed, scales=(256, 96, 32, 12), weights=(0.5, 0.28, 0.15, 0.07)):
    out = np.zeros((h, w), np.float32)
    for i, (s, wt) in enumerate(zip(scales, weights)):
        out += noise(h, w, s, seed + i) * wt
    return out


SHAPES = []   # set by bake(): list of (kind, code, data)


def shape_mask(code, h, w):
    """Rasterise vector shapes (smooth paths / disks / polys) for terrain `code` at full resolution."""
    sel = [s for s in SHAPES if s[1] in code]
    if not sel:
        return None

    def draw(ctx):
        ctx.set_source_rgba(1, 1, 1, 1)
        ctx.set_line_join(cairo.LINE_JOIN_ROUND)
        for kind, _, d in sel:
            if kind == 'path':
                pts, width = d
                pts = [(x * T, y * T) for x, y in pts]
                ctx.set_line_width(width * T)
                ctx.move_to(*pts[0])
                if len(pts) == 2:
                    ctx.line_to(*pts[1])
                else:
                    for i in range(len(pts) - 1):
                        p0 = pts[max(i - 1, 0)]
                        p1, p2 = pts[i], pts[i + 1]
                        p3 = pts[min(i + 2, len(pts) - 1)]
                        c1 = (p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6)
                        c2 = (p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6)
                        ctx.curve_to(*c1, *c2, *p2)
                ctx.stroke()
            elif kind == 'disk':
                cx, cy, r = d
                ctx.arc(cx * T, cy * T, r * T, 0, math.tau)
                ctx.fill()
            elif kind == 'rect':
                x0, y0, x1, y1 = d
                ctx.rectangle(x0 * T, y0 * T, (x1 - x0) * T, (y1 - y0) * T)
                ctx.fill()
    rgb, a = cairo_layer(w, h, draw)
    return a[..., 0]


def mask_from(grid, code, h, w, seed, blur=10, jitter=0.18):
    sm = shape_mask(code, h, w)
    if sm is not None:
        up = ndimage.gaussian_filter(sm, blur * 0.6)
    else:
        m = np.isin(grid, list(code)).astype(np.float32)
        up = np.kron(m, np.ones((T, T), np.float32))[:h, :w]
        up = ndimage.gaussian_filter(up, blur)
    up += (fbm(h, w, seed, (64, 24, 8), (0.6, 0.3, 0.1)) - 0.5) * jitter * 2
    return up


def smoothstep(e0, e1, x):
    t = np.clip((x - e0) / (e1 - e0), 0, 1)
    return t * t * (3 - 2 * t)


def col(h):
    h = h.lstrip('#')
    return np.array([int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)], np.float32)


def lerp_c(a, b, t):
    return a * (1 - t[..., None]) + b * t[..., None]


def cairo_layer(w, h, draw):
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, w, h)
    ctx = cairo.Context(surf)
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    draw(ctx)
    surf.flush()
    buf = np.ndarray((h, w, 4), np.uint8, surf.get_data()).astype(np.float32) / 255
    a = buf[..., 3:4]
    rgb = buf[..., [2, 1, 0]]   # premultiplied
    return rgb, a


def over(base, rgb_pm, a, mask=None):
    if mask is not None:
        rgb_pm = rgb_pm * mask[..., None]
        a = a * mask[..., None]
    return base * (1 - a) + rgb_pm


GRASS = dict(dark='#5b9e45', mid='#73b552', light='#8cc85e', warm='#9cc660', blade_l=(0.66, 0.85, 0.42), blade_d=(0.30, 0.55, 0.26),
             flowers=True)
GRASS_VELMOOR = dict(dark='#2f5a3e', mid='#3e7048', light='#548a52', warm='#6a6a8a', blade_l=(0.42, 0.62, 0.42),
                     blade_d=(0.16, 0.32, 0.22), flowers=False)


def bake(grid: np.ndarray, seed=1, shapes=(), grass=None):
    G = grass or GRASS
    SHAPES[:] = list(shapes)
    gh, gw = grid.shape
    h, w = gh * T, gw * T
    rnd = random.Random(seed)
    # ---------------- grass
    n1 = fbm(h, w, seed)
    n2 = fbm(h, w, seed + 10, (180, 60, 20), (0.6, 0.3, 0.1))
    g_dark, g_mid, g_light, g_warm = col(G['dark']), col(G['mid']), col(G['light']), col(G['warm'])
    img = lerp_c(g_dark, g_mid, smoothstep(0.25, 0.55, n1))
    img = lerp_c(img, g_light, smoothstep(0.55, 0.8, n1) * 0.8)
    img = lerp_c(img, g_warm, smoothstep(0.6, 0.85, n2) * 0.35)

    # blade strokes
    def blades(ctx):
        for i in range(int(w * h / 900)):
            x, y = rnd.uniform(0, w), rnd.uniform(0, h)
            nv = n1[int(y) % h, int(x) % w]
            light = rnd.random() < 0.55
            c = G['blade_l'] if light else G['blade_d']
            if nv < 0.35:
                c = tuple(v * 0.88 for v in (G['blade_l'] if light else G['blade_d']))
            ctx.set_source_rgba(*c, rnd.uniform(0.35, 0.7))
            ctx.set_line_width(rnd.uniform(1.4, 2.4))
            l = rnd.uniform(5, 10)
            a = rnd.uniform(-0.5, 0.5)
            ctx.move_to(x, y)
            ctx.curve_to(x + a * l * 0.3, y - l * 0.5, x + a * l * 0.7, y - l * 0.8, x + a * l, y - l)
            ctx.stroke()
        # tiny clover/flower specks
        for i in range(int(w * h / 22000)):
            x, y = rnd.uniform(0, w), rnd.uniform(0, h)
            c = rnd.choice([(1, 1, 1), (1, 0.85, 0.3), (1, 0.55, 0.65), (0.75, 0.6, 1)] if G['flowers'] else
                           [(0.55, 1, 0.75), (0.75, 0.6, 1), (0.5, 0.85, 1)])
            for k in range(rnd.randint(2, 5)):
                xx, yy = x + rnd.uniform(-10, 10), y + rnd.uniform(-8, 8)
                ctx.set_source_rgba(*c, 0.95)
                ctx.arc(xx, yy, rnd.uniform(1.4, 2.2), 0, math.tau)
                ctx.fill()
    rgb, a = cairo_layer(w, h, blades)
    img = over(img, rgb, a)

    # ---------------- tilled soil
    mt = smoothstep(0.45, 0.55, mask_from(grid, 't', h, w, seed + 3, blur=4, jitter=0.05))
    if mt.max() > 0:
        soil = lerp_c(col('#8a5a3a'), col('#a06c46'), noise(h, w, 24, seed + 4))
        yy = np.arange(h)[:, None] % 32
        furrow = (np.sin(yy / 32 * math.tau) * 0.5 + 0.5).astype(np.float32)
        soil = lerp_c(soil, col('#6a4028'), (1 - furrow) * 0.55 * np.ones((h, w), np.float32))
        soil = lerp_c(soil, col('#b8825a'), np.clip(furrow - 0.75, 0, 1) * 2.5 * np.ones((h, w), np.float32))
        edge = mt - ndimage.grey_erosion(mt, size=(7, 7))
        img = lerp_c(img, soil, mt)
        img = lerp_c(img, col('#4a3020'), np.clip(edge, 0, 1) * 0.6)

    # ---------------- dirt paths
    md_raw = mask_from(grid, 'd', h, w, seed + 5, blur=12, jitter=0.16)
    md = smoothstep(0.46, 0.54, md_raw)
    if md.max() > 0:
        dn = fbm(h, w, seed + 6, (90, 30, 10), (0.55, 0.3, 0.15))
        dirt = lerp_c(col('#c19463'), col('#d8ae78'), smoothstep(0.3, 0.75, dn))
        dirt = lerp_c(dirt, col('#a87a4e'), smoothstep(0.6, 0.85, fbm(h, w, seed + 7, (40, 14), (0.7, 0.3))) * 0.6)
        # darker rim where grass meets dirt (AO), plus lighter worn centre
        rim = smoothstep(0.46, 0.62, md_raw)
        dirt = lerp_c(col('#9c7046'), dirt, rim)

        def pebbles(ctx):
            for i in range(int(w * h / 2600)):
                x, y = rnd.uniform(0, w), rnd.uniform(0, h)
                r = rnd.uniform(1.6, 4.0)
                ctx.set_source_rgba(0.45, 0.32, 0.22, 0.6)
                ctx.save()
                ctx.translate(x, y + 1)
                ctx.scale(r, r * 0.7)
                ctx.arc(0, 0, 1, 0, math.tau)
                ctx.restore()
                ctx.fill()
                ctx.set_source_rgba(0.93, 0.82, 0.66, 0.9)
                ctx.save()
                ctx.translate(x, y)
                ctx.scale(r * 0.85, r * 0.6)
                ctx.arc(0, 0, 1, 0, math.tau)
                ctx.restore()
                ctx.fill()
        rgb, a = cairo_layer(w, h, pebbles)
        dirt = over(dirt, rgb, a)
        img = lerp_c(img, dirt, md)
        # grass overhang shadow just inside the path edge
        sh = np.clip(ndimage.gaussian_filter(1 - md, 3) - (1 - md), 0, 1)
        img = lerp_c(img, col('#5a3e26'), sh * 0.5)

    # ---------------- stone plaza
    ms_raw = mask_from(grid, 's', h, w, seed + 8, blur=8, jitter=0.08)
    ms = smoothstep(0.47, 0.53, ms_raw)
    if ms.max() > 0:
        mortar = col('#8d8a96')
        stone_img = np.ones((h, w, 3), np.float32) * mortar

        def cobbles(ctx):
            cw, ch = 30, 22
            for row in range(h // ch + 2):
                off = (cw / 2) if row % 2 else 0
                for k in range(w // cw + 2):
                    x = k * cw + off + rnd.uniform(-2, 2)
                    y = row * ch + rnd.uniform(-1.5, 1.5)
                    gy, gx = int(min(max(y, 0), h - 1)), int(min(max(x, 0), w - 1))
                    if ms[gy, gx] < 0.05:
                        continue
                    sw, shh = cw / 2 - 2.2, ch / 2 - 2.2
                    tone = rnd.uniform(-0.06, 0.06)
                    base = (0.78 + tone, 0.76 + tone, 0.82 + tone)
                    # bottom-right shadow
                    ctx.set_source_rgba(0.42, 0.40, 0.50, 1)
                    rrect(ctx, x - sw + 1.2, y - shh + 1.6, sw * 2, shh * 2, 5)
                    ctx.fill()
                    ctx.set_source_rgba(*base, 1)
                    rrect(ctx, x - sw, y - shh, sw * 2, shh * 2, 5)
                    ctx.fill()
                    ctx.set_source_rgba(1, 1, 1, 0.35)
                    rrect(ctx, x - sw + 2, y - shh + 1.5, sw * 1.2, 3, 1.5)
                    ctx.fill()
        rgb, a = cairo_layer(w, h, cobbles)
        stone_img = over(stone_img, rgb, a)
        img = lerp_c(img, stone_img, ms)
        rim = np.clip(ms - ndimage.grey_erosion(ms, size=(9, 9)), 0, 1)
        img = lerp_c(img, col('#6a6878'), rim * 0.55)

    # ---------------- water
    mw_raw = mask_from(grid, 'wb', h, w, seed + 9, blur=14, jitter=0.12)
    mw = smoothstep(0.48, 0.52, mw_raw)
    if mw.max() > 0:
        dist = ndimage.distance_transform_edt(mw > 0.5).astype(np.float32)
        depth = np.clip(dist / 70, 0, 1)
        wn = fbm(h, w, seed + 11, (120, 40), (0.7, 0.3))
        water = lerp_c(col('#7fd3e0'), col('#3f9fc4'), smoothstep(0.0, 0.6, depth))
        water = lerp_c(water, col('#2f7fae'), smoothstep(0.5, 1.0, depth) * 0.8)
        water = lerp_c(water, col('#a5e6ee'), smoothstep(0.62, 0.8, wn) * 0.25)
        # sandy/wet shore band outside the water
        shore = smoothstep(0.30, 0.48, mw_raw) * (1 - mw)
        img = lerp_c(img, col('#d9c08a'), shore * 0.95)
        img = lerp_c(img, water, mw)
        # foam line just inside the edge
        foam = np.clip(1 - np.abs(dist - 5) / 3.5, 0, 1) * (mw > 0.5)
        img = lerp_c(img, col('#f2fbff'), foam * 0.75)

        def ripples(ctx):
            for i in range(int(w * h / 9000)):
                x, y = rnd.uniform(0, w), rnd.uniform(0, h)
                if mw[int(y) % h, int(x) % w] < 0.9 or dist[int(y) % h, int(x) % w] < 14:
                    continue
                l = rnd.uniform(8, 20)
                ctx.set_source_rgba(0.85, 0.97, 1, 0.45)
                ctx.set_line_width(2)
                ctx.move_to(x - l, y)
                ctx.curve_to(x - l / 3, y - 3, x + l / 3, y - 3, x + l, y)
                ctx.stroke()
        rgb, a = cairo_layer(w, h, ripples)
        img = over(img, rgb, a)
    return (np.clip(img, 0, 1) * 255 + 0.5).astype(np.uint8)


def rrect(ctx, x, y, w, h, r):
    r = min(r, w / 2, h / 2)
    ctx.new_sub_path()
    ctx.arc(x + w - r, y + r, r, -math.pi / 2, 0)
    ctx.arc(x + w - r, y + h - r, r, 0, math.pi / 2)
    ctx.arc(x + r, y + h - r, r, math.pi / 2, math.pi)
    ctx.arc(x + r, y + r, r, math.pi, 1.5 * math.pi)
    ctx.close_path()
