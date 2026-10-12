"""Small ground decals (tufts, flowers, pebbles ...) baked over terrain to break tiling."""
import numpy as np, json, os, sys
from PIL import Image
sys.path.insert(0, os.path.dirname(__file__))
from pix import ramp, hex2rgb

C = 16  # cell size


def blank():
    return np.zeros((C, C, 4), dtype=np.uint8)


def px(a, x, y, col):
    if 0 <= x < C and 0 <= y < C:
        a[y, x] = (*col, 255)


def tuft(seed, base='#4a9a40', n=4):
    a = blank(); rp = ramp(base, 6); rng = np.random.default_rng(seed)
    for k in range(n):
        x = 4 + k * 2 + int(rng.integers(-1, 2)); h = int(rng.integers(3, 7)); lean = int(rng.integers(-1, 2))
        for j in range(h):
            px(a, x + (lean if j > h // 2 else 0), 12 - j, rp[3] if j < h - 1 else rp[5])
        px(a, x, 13, rp[1])
    return a


def flower(seed, col='#ffffff', center='#ffe066'):
    a = blank(); rp = ramp('#3f8a3a', 5); c1 = hex2rgb(col); c2 = hex2rgb(center)
    for j in range(5):
        px(a, 8, 13 - j, rp[2])
    px(a, 7, 11, rp[3]); px(a, 9, 10, rp[3])
    for dx, dy in ((0, -1), (-1, 0), (1, 0), (0, 1)):
        px(a, 8 + dx, 7 + dy, c1)
    px(a, 8, 7, c2)
    return a


def pebbles(seed, base='#8a8a98', n=3):
    a = blank(); rp = ramp(base, 6); rng = np.random.default_rng(seed)
    for k in range(n):
        x, y = int(rng.integers(3, 12)), int(rng.integers(6, 12))
        w = int(rng.integers(2, 4))
        for i in range(w):
            px(a, x + i, y, rp[4]); px(a, x + i, y + 1, rp[2])
        px(a, x, y, rp[5]); px(a, x + w, y + 1, rp[0])
    return a


def leaf(seed, base='#c8782a'):
    a = blank(); rp = ramp(base, 6)
    for (x, y, c) in ((6, 8, 3), (7, 8, 4), (8, 9, 3), (9, 9, 2), (7, 9, 2), (8, 8, 4)):
        px(a, x, y, rp[c])
    return a


def mushroom(seed, cap='#d9485a'):
    a = blank(); rp = ramp(cap, 6); st = ramp('#f0e0c0', 5)
    for x in range(6, 11):
        px(a, x, 8, rp[3]); px(a, x, 9, rp[2])
    for x in range(7, 10):
        px(a, x, 7, rp[4])
    px(a, 7, 8, (255, 255, 255)); px(a, 9, 9, (255, 255, 255))
    for y in range(10, 13):
        px(a, 8, y, st[3]); px(a, 9, y, st[2])
    return a


def crack(seed, base='#2a2438'):
    a = blank(); rng = np.random.default_rng(seed); col = hex2rgb(base)
    x, y = 2, int(rng.integers(5, 10))
    for k in range(11):
        px(a, x, y, col); x += 1; y += int(rng.integers(-1, 2))
        if k % 4 == 3:
            px(a, x, y + 1, col)
    return a


def bones(seed):
    a = blank(); c = ramp('#e8e4d8', 6)
    for x in range(4, 11):
        px(a, x, 9, c[4]); px(a, x, 10, c[2])
    for (x, y) in ((3, 8), (3, 10), (11, 8), (11, 10)):
        px(a, x, y, c[5])
    return a


def glowshroom(seed):
    a = blank(); rp = ramp('#66e6ff', 6)
    for x in range(6, 11):
        px(a, x, 9, rp[4]); px(a, x, 10, rp[2])
    px(a, 7, 8, rp[5]); px(a, 8, 8, rp[5]); px(a, 8, 11, rp[1]); px(a, 8, 12, rp[1])
    return a


def shell(seed):
    a = blank(); rp = ramp('#f2c0b0', 6)
    for (x, y, c) in ((7, 9, 4), (8, 9, 5), (9, 9, 3), (7, 10, 2), (8, 10, 3), (9, 10, 2), (8, 8, 5)):
        px(a, x, y, rp[c])
    return a


def snowdrift(seed):
    a = blank(); rp = ramp('#e8f0fa', 6)
    for x in range(3, 13):
        px(a, x, 10, rp[5]); px(a, x, 11, rp[3])
    for x in range(5, 11):
        px(a, x, 9, rp[5])
    return a


DECALS = {
    'tuft_a': lambda: tuft(1), 'tuft_b': lambda: tuft(2, n=3), 'tuft_c': lambda: tuft(3, '#3a8a48', 5), 'tuft_dark': lambda: tuft(4, '#2a6a3a', 4),
    'flower_w': lambda: flower(1), 'flower_p': lambda: flower(2, '#ff8fab'), 'flower_y': lambda: flower(3, '#ffd166', '#ffffff'), 'flower_b': lambda: flower(4, '#b39dff', '#ffffff'),
    'pebbles': lambda: pebbles(1), 'pebbles_b': lambda: pebbles(2, '#a09888', 2), 'pebbles_dark': lambda: pebbles(3, '#5a5470', 3),
    'leaf_o': lambda: leaf(1), 'leaf_g': lambda: leaf(2, '#6a9a3a'),
    'mushroom_r': lambda: mushroom(1), 'mushroom_b': lambda: mushroom(2, '#6a7ad9'),
    'crack': lambda: crack(1), 'crack_dark': lambda: crack(2, '#14101e'),
    'bones': lambda: bones(1), 'glowshroom': lambda: glowshroom(1), 'shell': lambda: shell(1), 'snowdrift': lambda: snowdrift(1),
}
ORDER = list(DECALS.keys())


def build(outdir):
    os.makedirs(outdir, exist_ok=True)
    cols = 8
    rows = (len(ORDER) + cols - 1) // cols
    atlas = np.zeros((rows * C, cols * C, 4), dtype=np.uint8)
    for i, n in enumerate(ORDER):
        r, c = divmod(i, cols)
        atlas[r * C:(r + 1) * C, c * C:(c + 1) * C] = DECALS[n]()
    Image.fromarray(atlas, 'RGBA').save(os.path.join(outdir, 'decals.png'))
    json.dump({'cell': C, 'cols': cols, 'names': ORDER}, open(os.path.join(outdir, 'decals.json'), 'w'))


if __name__ == '__main__':
    build(sys.argv[1] if len(sys.argv) > 1 else '/tmp/tiles')
