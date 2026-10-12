"""Seamless 32x32 terrain tiles, animated water, edge overlays, wall tiles."""
import numpy as np, json, os, sys
from PIL import Image
sys.path.insert(0, os.path.dirname(__file__))
from pix import ramp, hex2rgb

T = 32
BAYER = np.array([[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]], dtype=np.float32) / 16.0 - 0.5


def bayer(w=T, h=T):
    return np.tile(BAYER, (h // 4 + 1, w // 4 + 1))[:h, :w]


def pnoise(cells, seed, size=T):
    rng = np.random.default_rng(seed)
    lat = rng.random((cells, cells)).astype(np.float32)
    xs = np.linspace(0, cells, size, endpoint=False)
    i0 = np.floor(xs).astype(int)
    f = xs - i0
    f = f * f * (3 - 2 * f)
    i1 = (i0 + 1) % cells
    a = lat[np.ix_(i0, i0)] * (1 - f)[None, :] + lat[np.ix_(i0, i1)] * f[None, :]
    b = lat[np.ix_(i1, i0)] * (1 - f)[None, :] + lat[np.ix_(i1, i1)] * f[None, :]
    return a * (1 - f)[:, None] + b * f[:, None]


def fbm(seed, octs=((2, 0.5), (4, 0.3), (8, 0.15), (16, 0.05)), size=T):
    v = np.zeros((size, size), dtype=np.float32)
    for k, (c, w) in enumerate(octs):
        v += pnoise(c, seed * 31 + k * 7, size) * w
    return v


def quant(v, rp, spread=0.9):
    n = len(rp)
    idx = np.clip(np.floor(v * n + bayer(v.shape[1], v.shape[0]) * spread), 0, n - 1).astype(int)
    arr = np.array(rp, dtype=np.uint8)
    return arr[idx]


def to_img(rgb, alpha=None):
    h, w, _ = rgb.shape
    out = np.zeros((h, w, 4), dtype=np.uint8)
    out[..., :3] = rgb
    out[..., 3] = 255 if alpha is None else alpha
    return out


def stamp(rgb, x, y, col, w=1, h=1):
    for j in range(h):
        for i in range(w):
            rgb[(y + j) % T, (x + i) % T] = col


# ---------------------------------------------------------------- terrains
def grass(seed, base='#5aa84e', flowers=False, dark=False):
    rp = ramp(base, 6)
    v = fbm(seed, ((2, 0.5), (4, 0.3), (8, 0.15), (16, 0.05)))
    v = np.clip((v - 0.5) * 0.9 + 0.5, 0, 1)
    rgb = quant(v * 0.5 + 0.28, rp, 0.7)
    rng = np.random.default_rng(seed + 99)
    for _ in range(14):
        x, y = rng.integers(0, T, 2)
        h = int(rng.integers(2, 5))
        for k in range(h):
            stamp(rgb, x + (k // 3), y - k, rp[4] if k >= h - 1 else rp[3])
        stamp(rgb, x + 1, y, rp[1])
    for _ in range(5):
        x, y = rng.integers(0, T, 2)
        stamp(rgb, x, y, rp[1])
    if flowers:
        cols = [('#ffffff', '#ffe066'), ('#ff8fab', '#ffe066'), ('#b39dff', '#ffffff'), ('#ffd166', '#ffffff')]
        for k in range(int(rng.integers(3, 6))):
            x, y = rng.integers(2, T - 3, 2)
            c1, c2 = cols[int(rng.integers(0, 4))]
            c1, c2 = hex2rgb(c1), hex2rgb(c2)
            stamp(rgb, x, y + 1, rp[1], 1, 2)
            for dx, dy in ((0, 0), (-1, 0), (1, 0), (0, -1)):
                stamp(rgb, x + dx, y + dy, c1)
            stamp(rgb, x, y, c2)
    return to_img(rgb)


def dirt(seed, base='#b98d5c', ruts=False):
    rp = ramp(base, 6)
    v = fbm(seed, ((3, 0.5), (6, 0.3), (12, 0.2)))
    rgb = quant(np.clip((v - 0.5) * 0.9 + 0.5, 0, 1) * 0.5 + 0.28, rp, 0.7)
    rng = np.random.default_rng(seed + 5)
    for _ in range(14):
        x, y = rng.integers(0, T, 2)
        w = int(rng.integers(2, 4))
        stamp(rgb, x, y, rp[5], w, 1)
        stamp(rgb, x + 1, y + 1, rp[1], w, 1)
    for _ in range(8):
        x, y = rng.integers(0, T, 2)
        stamp(rgb, x, y, rp[0])
    if ruts:
        for cx in (9, 22):
            for y in range(T):
                for dx in (0, 1):
                    rgb[y, (cx + dx + int(1.2 * np.sin(y / 5.0 + seed))) % T] = rp[1] if dx == 0 else rp[2]
    return to_img(rgb)


def sand(seed, base='#e6d29a'):
    rp = ramp(base, 6)
    v = fbm(seed, ((2, 0.5), (4, 0.3), (8, 0.2)))
    ys, xs = np.mgrid[0:T, 0:T].astype(np.float32)
    rip = np.sin((ys + v * 14) * (2 * np.pi / 8) * 1.0 + seed) * 0.5 + 0.5
    val = 0.55 + 0.25 * (rip > 0.82) - 0.22 * (rip < 0.12) + (v - 0.5) * 0.4
    rgb = quant(np.clip(val, 0, 0.99), rp, 0.6)
    rng = np.random.default_rng(seed)
    for _ in range(18):
        x, y = rng.integers(0, T, 2)
        stamp(rgb, x, y, rp[5] if rng.random() < 0.5 else rp[1])
    return to_img(rgb)


def cobble(seed, base='#9a98a8', cells=4, joint='#4a4658'):
    rp = ramp(base, 6)
    rng = np.random.default_rng(seed)
    n = cells
    pts = []
    cs = T / n
    for j in range(n):
        for i in range(n):
            pts.append(((i + 0.5 + (rng.random() - 0.5) * 0.7) * cs, (j + 0.5 + (rng.random() - 0.5) * 0.7) * cs, rng.random()))
    ys, xs = np.mgrid[0:T, 0:T].astype(np.float32)
    best = np.full((T, T), 1e9, dtype=np.float32)
    second = np.full((T, T), 1e9, dtype=np.float32)
    bid = np.zeros((T, T), dtype=np.int32)
    for k, (px, py, _) in enumerate(pts):
        for ox in (-T, 0, T):
            for oy in (-T, 0, T):
                d = np.hypot(xs - (px + ox), ys - (py + oy))
                m = d < best
                second = np.where(m, best, np.minimum(second, d))
                bid = np.where(m, k, bid)
                best = np.where(m, d, best)
    edge = second - best
    tone = np.array([p[2] for p in pts])[bid]
    # bevel: lighter toward top-left of each stone
    px_arr = np.array([p[0] for p in pts])[bid]
    py_arr = np.array([p[1] for p in pts])[bid]
    lighting = ((px_arr - xs) * -0.5 + (py_arr - ys) * -0.5) / (cs * 0.5)
    val = 0.42 + tone * 0.28 + np.clip(lighting, -1, 1) * 0.1 + (fbm(seed + 3, ((8, 0.6), (16, 0.4))) - 0.5) * 0.15
    rgb = quant(np.clip(val, 0, 0.99), rp, 0.5)
    jc = np.array(hex2rgb(joint), dtype=np.uint8)
    rgb[edge < 1.5] = jc
    rgb[(edge >= 1.5) & (edge < 2.6)] = np.array(rp[1], dtype=np.uint8)
    # highlight top-left rim
    hl = (edge >= 1.5) & (edge < 2.5) & (lighting > 0.35)
    rgb[hl] = np.array(rp[5], dtype=np.uint8)
    return to_img(rgb)


def slab(seed, base='#8c8aa0', big=16):
    rp = ramp(base, 6)
    rng = np.random.default_rng(seed)
    rgb = np.zeros((T, T, 3), dtype=np.uint8)
    n = T // big
    for j in range(n):
        for i in range(n):
            tone = 0.4 + rng.random() * 0.25
            for y in range(big):
                for x in range(big):
                    v = tone + (0.18 if (x == 1 or y == 1) else 0) - (0.2 if (x == big - 1 or y == big - 1) else 0)
                    rgb[j * big + y, i * big + x] = quant(np.array([[min(0.99, max(0, v))]]), rp, 0)[0, 0]
            rgb[j * big, i * big:(i + 1) * big] = rp[0]
            rgb[j * big:(j + 1) * big, i * big] = rp[0]
    nz = fbm(seed + 2, ((8, 0.6), (16, 0.4)))
    mask = nz > 0.62
    rgb[mask & (rgb.sum(-1) > 150)] = (rgb[mask & (rgb.sum(-1) > 150)] * 0.88).astype(np.uint8)
    for _ in range(3):
        x, y = rng.integers(0, T, 2)
        for k in range(int(rng.integers(4, 9))):
            rgb[(y + k) % T, (x + int(np.sin(k) * 1.5)) % T] = rp[0]
    return to_img(rgb)


def planks(seed, base='#a8693a', horizontal=True):
    rp = ramp(base, 6)
    rng = np.random.default_rng(seed)
    rgb = np.zeros((T, T, 3), dtype=np.uint8)
    ph = 8
    for k in range(T // ph):
        tone = 0.38 + rng.random() * 0.25
        shift = int(rng.integers(0, T))
        for y in range(ph):
            for x in range(T):
                grain = np.sin((x + shift) * 0.5 + y * 0.9 + k) * 0.06
                v = tone + grain + (0.14 if y == 1 else 0) - (0.2 if y == ph - 1 else 0)
                rgb[k * ph + y, x] = quant(np.array([[min(0.99, max(0, v))]]), rp, 0)[0, 0]
        rgb[k * ph] = rp[0]
        jx = (shift + k * 13) % T
        rgb[k * ph:(k + 1) * ph, jx] = rp[0]
        rgb[k * ph + 3, (jx + 12) % T] = rp[0]
    return to_img(rgb if horizontal else rgb.transpose(1, 0, 2))


def cave_floor(seed, base='#4a4262', crystals=False):
    rp = ramp(base, 6)
    v = fbm(seed, ((3, 0.4), (6, 0.35), (12, 0.25)))
    v = (v - v.min()) / (v.max() - v.min() + 1e-6)
    rgb = quant(v * 0.8 + 0.05, rp)
    rng = np.random.default_rng(seed)
    for _ in range(3):
        x, y = rng.integers(0, T, 2)
        for k in range(int(rng.integers(5, 12))):
            rgb[(y + k // 2) % T, (x + k) % T] = rp[0]
    for _ in range(10):
        x, y = rng.integers(0, T, 2)
        stamp(rgb, x, y, rp[5])
    if crystals:
        cr = ramp('#66e6ff', 6)
        for _ in range(2):
            x, y = rng.integers(4, T - 4, 2)
            for k in range(6):
                stamp(rgb, x, y - k, cr[4], 2 if k < 4 else 1, 1)
            stamp(rgb, x, y - 6, cr[5])
            stamp(rgb, x + 1, y, cr[2])
    return to_img(rgb)


def snow(seed):
    rp = ramp('#e8f0fa', 6)
    v = fbm(seed, ((2, 0.5), (5, 0.3), (10, 0.2)))
    rgb = quant(np.clip(v * 0.5 + 0.5, 0, 0.99), rp, 0.5)
    rng = np.random.default_rng(seed)
    for _ in range(8):
        x, y = rng.integers(0, T, 2)
        stamp(rgb, x, y, (255, 255, 255), 2, 1)
        stamp(rgb, x + 1, y + 1, rp[1], 2, 1)
    return to_img(rgb)


def carpet(seed, base='#a8283a'):
    rp = ramp(base, 6)
    rgb = np.zeros((T, T, 3), dtype=np.uint8)
    v = fbm(seed, ((8, 0.6), (16, 0.4)))
    rgb[:] = quant(0.4 + v * 0.3, rp, 0.3)
    return to_img(rgb)


def lava(seed, frame=0, n=8):
    ys, xs = np.mgrid[0:T, 0:T].astype(np.float32)
    ph = frame / n * 2 * np.pi
    v = np.sin((xs * 2 * np.pi / 16) + ph) * 0.3 + np.sin((ys * 2 * np.pi / 32) * 2 + ph) * 0.3 + np.sin(((xs + ys) * 2 * np.pi / 32) * 2 - ph) * 0.4
    v = (v + 1) / 2
    return to_img(quant(v, ramp('#e8541a', 6), 0.7))


def water(seed, frame, n=8, base='#3a86d8', deep=False):
    rp = ramp(base if not deep else '#2456a8', 6)
    ph = frame / n * 2 * np.pi
    ys, xs = np.mgrid[0:T, 0:T].astype(np.float32)
    k = 2 * np.pi / T
    v = (np.sin(xs * k * 2 + ph + np.sin(ys * k * 3) * 1.2) * 0.35 + np.sin(ys * k * 3 - ph + np.sin(xs * k * 2) * 1.0) * 0.35 + np.sin((xs + ys) * k * 2 + ph * 2) * 0.3)
    v = (v + 1) / 2
    val = 0.38 + v * 0.4
    rgb = quant(np.clip(val, 0, 0.99), rp, 0.5)
    sp = v > 0.93
    rgb[sp] = (235, 248, 255)
    sp2 = (v > 0.86) & ~sp & ((xs.astype(int) + ys.astype(int)) % 2 == 0)
    rgb[sp2] = np.array(rp[5], dtype=np.uint8)
    return to_img(rgb)


# ---------------------------------------------------------------- walls
def wall_top(seed, base='#2a2438'):
    rp = ramp(base, 6)
    v = fbm(seed, ((3, 0.5), (6, 0.3), (12, 0.2)))
    rgb = quant(np.clip(v * 0.7 + 0.1, 0, 0.99), rp)
    return to_img(rgb)


def wall_face(seed, base='#4a4064', brick=(16, 8), top_light=True, mossy=False):
    rp = ramp(base, 6)
    rng = np.random.default_rng(seed)
    bw, bh = brick
    rgb = np.zeros((T, T, 3), dtype=np.uint8)
    for j in range(T // bh):
        off = (bw // 2) if j % 2 else 0
        for i in range(-1, T // bw + 1):
            tone = 0.42 + rng.random() * 0.22
            x0 = i * bw + off
            for y in range(bh):
                for x in range(bw):
                    xx = (x0 + x) % T
                    v = tone + (0.14 if y == 1 else 0) + (0.08 if x == 1 else 0) - (0.2 if y == bh - 1 else 0) - (0.1 if x == bw - 1 else 0)
                    rgb[j * bh + y, xx] = quant(np.array([[min(0.99, max(0, v))]]), rp, 0)[0, 0]
            rgb[j * bh + bh - 1, :] = rp[0]
            rgb[j * bh:(j + 1) * bh, x0 % T] = rp[0]
    if top_light:
        rgb[0:3] = np.array(rp[5], dtype=np.uint8)
        rgb[3] = np.array(rp[3], dtype=np.uint8)
    rgb[T - 4:T] = (rgb[T - 4:T] * 0.78).astype(np.uint8)
    if mossy:
        mp = ramp('#4a8a4a', 6)
        for _ in range(12):
            x, y = rng.integers(0, T, 2)
            stamp(rgb, x, y, mp[3], 2, 2)
    return to_img(rgb)


def battlement(seed, base='#9a98ac'):
    """Castle wall face with crenellated top row (merlons) – transparent gaps."""
    rp = ramp(base, 6)
    img = wall_face(seed, base, brick=(16, 8), top_light=True)
    img[0:8, :, 3] = 0
    for x0 in (0, 16):
        for y in range(8):
            for x in range(10):
                img[y, x0 + 3 + x] = np.array([*rp[3], 255], dtype=np.uint8) if y > 1 else np.array([*rp[5], 255], dtype=np.uint8)
            img[y, x0 + 3] = np.array([*rp[1], 255], dtype=np.uint8)
            img[y, x0 + 12] = np.array([*rp[1], 255], dtype=np.uint8)
    return img


# ---------------------------------------------------------------- edge overlays
def edge_masks(seed=1):
    """Return dict dir -> alpha mask (T,T) for a terrain spilling over its neighbour on that side."""
    rng = np.random.default_rng(seed)
    ys, xs = np.mgrid[0:T, 0:T].astype(np.float32)
    n1 = pnoise(4, seed + 1)
    n2 = pnoise(8, seed + 2)
    jit = (n1 - 0.5) * 7 + (n2 - 0.5) * 3
    depth = 6.0
    masks = {}
    masks['N'] = (ys + jit) < depth      # neighbour to the north is higher: spill from top edge
    masks['S'] = ((T - 1 - ys) + jit) < depth
    masks['W'] = (xs + jit.T) < depth
    masks['E'] = ((T - 1 - xs) + jit.T) < depth
    r = 9.0
    for name, cx, cy in (('NW', 0, 0), ('NE', T - 1, 0), ('SE', T - 1, T - 1), ('SW', 0, T - 1)):
        d = np.hypot(xs - cx, ys - cy) + jit
        masks[name] = d < r
    return masks


def make_edge(tile_img, mask, rim_dark=0.78):
    """Apply mask to tile texture; add darker rim along mask boundary."""
    out = tile_img.copy()
    m = mask
    out[..., 3] = np.where(m, 255, 0)
    # boundary pixels = mask pixels with a non-mask 4-neighbour
    pm = np.pad(m, 1)
    border = m & (~pm[:-2, 1:-1] | ~pm[2:, 1:-1] | ~pm[1:-1, :-2] | ~pm[1:-1, 2:])
    out[border, :3] = (out[border, :3] * rim_dark).astype(np.uint8)
    return out


TERRAINS = {
    # name: (generator, rank)   – higher rank spills over lower rank
    'grass':      (lambda s: grass(s, '#5ca84c'), 50),
    'grass_dark': (lambda s: grass(s, '#356f48', dark=True), 51),
    'meadow':     (lambda s: grass(s, '#62b050', flowers=True), 52),
    'moss':       (lambda s: grass(s, '#3f7a6a'), 49),
    'dirt':       (lambda s: dirt(s), 30),
    'road':       (lambda s: dirt(s, '#a87c4e', ruts=True), 31),
    'cobble':     (lambda s: cobble(s, '#a09eb0', cells=3), 40),
    'cobble_warm': (lambda s: cobble(s, '#b09878', cells=3, joint='#5a4a38'), 41),
    'sand':       (lambda s: sand(s), 20),
    'dsand':      (lambda s: sand(s, '#e8c070'), 21),
    'snow':       (lambda s: snow(s), 55),
    'cave':       (lambda s: cave_floor(s), 45),
    'cave_crystal': (lambda s: cave_floor(s, '#4a4a70', crystals=True), 46),
    'cave_dark':  (lambda s: cave_floor(s, '#33304a'), 44),
    'wood':       (lambda s: planks(s), 60),
    'wood_dark':  (lambda s: planks(s, '#6a4228'), 61),
    'slab':       (lambda s: slab(s), 62),
    'slab_dark':  (lambda s: slab(s, '#5a586e'), 63),
    'marble':     (lambda s: slab(s, '#cfd0e0'), 64),
    'carpet':     (lambda s: carpet(s), 65),
    'carpet_blue': (lambda s: carpet(s, '#2a4aa8'), 66),
    'wall_top':   (lambda s: wall_top(s), 99),
    'wall_top_house': (lambda s: planks(s, '#3a2418', horizontal=False), 99),
    'wall_top_stone': (lambda s: wall_top(s, '#5a586e'), 99),
}
VARIANTS = 4
NO_EDGE = {'wood', 'wood_dark', 'slab', 'slab_dark', 'marble', 'carpet', 'carpet_blue', 'wall_top', 'wall_top_house', 'wall_top_stone', 'cave_crystal'}
WATER_FRAMES = 8


def build(outdir):
    os.makedirs(outdir, exist_ok=True)
    names = list(TERRAINS.keys())
    meta = {'tile': T, 'variants': VARIANTS, 'terrains': names, 'rank': {n: TERRAINS[n][1] for n in names}, 'water_frames': WATER_FRAMES}
    atlas = np.zeros((T * (len(names) + 12), T * VARIANTS, 4), dtype=np.uint8)
    for r, n in enumerate(names):
        for v in range(VARIANTS):
            atlas[r * T:(r + 1) * T, v * T:(v + 1) * T] = TERRAINS[n][0](v * 17 + r * 101 + 3)
    row = len(names)
    # walls (face variants)
    walls = {
        'face_cave': lambda s: wall_face(s, '#4a4064'),
        'face_stone': lambda s: wall_face(s, '#8a88a0', brick=(16, 8)),
        'face_house': lambda s: planks(s, '#a87040', horizontal=False),
        'face_ice': lambda s: wall_face(s, '#7fb6dc'),
        'face_adobe': lambda s: wall_face(s, '#c98a58', brick=(32, 16)),
        'battlement': lambda s: battlement(s),
        'face_stone_dark': lambda s: wall_face(s, '#5a586e'),
        'face_mossy': lambda s: wall_face(s, '#5a5a78', mossy=True),
    }
    meta['walls'] = {}
    for k, (n, fn) in enumerate(walls.items()):
        meta['walls'][n] = row + k
        for v in range(VARIANTS):
            atlas[(row + k) * T:(row + k + 1) * T, v * T:(v + 1) * T] = fn(v * 13 + k * 7 + 1)
    row += len(walls)
    # water + lava frames (rows of 8 frames; use first 4 columns x2 rows?) -> separate atlas
    Image.fromarray(atlas[:row * T], 'RGBA').save(os.path.join(outdir, 'terrain.png'))
    meta['rows'] = row
    wat = np.zeros((T * 3, T * WATER_FRAMES, 4), dtype=np.uint8)
    for f in range(WATER_FRAMES):
        wat[0:T, f * T:(f + 1) * T] = water(1, f)
        wat[T:2 * T, f * T:(f + 1) * T] = water(2, f, deep=True)
        wat[2 * T:3 * T, f * T:(f + 1) * T] = lava(3, f)
    Image.fromarray(wat, 'RGBA').save(os.path.join(outdir, 'water.png'))
    # edges: for each terrain, 8 overlay pieces
    dirs = ['N', 'E', 'S', 'W', 'NE', 'SE', 'SW', 'NW']
    edge = np.zeros((T * len(names), T * 8, 4), dtype=np.uint8)
    masks = edge_masks(5)
    for r, n in enumerate(names):
        if n in NO_EDGE:
            continue
        base = atlas[r * T:(r + 1) * T, 0:T]
        for k, d in enumerate(dirs):
            edge[r * T:(r + 1) * T, k * T:(k + 1) * T] = make_edge(base, masks[d])
    Image.fromarray(edge, 'RGBA').save(os.path.join(outdir, 'edges.png'))
    meta['edge_dirs'] = dirs
    meta['no_edge'] = sorted(NO_EDGE)
    with open(os.path.join(outdir, 'terrain.json'), 'w') as f:
        json.dump(meta, f)
    return meta


if __name__ == '__main__':
    out = sys.argv[1] if len(sys.argv) > 1 else '/tmp/tiles'
    m = build(out)
    print(m['terrains'])
