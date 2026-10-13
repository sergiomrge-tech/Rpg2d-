"""Seamless 256x256 grey-scale surface textures for the interiors (tinted per room style at runtime).

Writes godot/assets/Sprites/Tex/{floor_wood,floor_stone,floor_dirt,wall_plaster,wall_brick,wall_wood}.png
"""
import os
import numpy as np
from PIL import Image
from scipy import ndimage

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'godot', 'assets', 'Sprites', 'Tex')
N = 256


def noise(sigma, seed, shape=(N, N)):
    rng = np.random.default_rng(seed)
    n = ndimage.gaussian_filter(rng.standard_normal(shape).astype(np.float32), sigma, mode='wrap')
    return n / (n.std() + 1e-6)


def finish(img, name, mean=0.80, contrast=1.9):
    img = img / img.mean() * mean
    img = mean + (img - mean) * contrast
    img = np.clip(img, 0.12, 1.0)
    Image.fromarray((img * 255).astype(np.uint8), 'L').convert('RGB').save(os.path.join(OUT, name + '.png'), optimize=True)


def wood_floor():
    img = np.ones((N, N), np.float32) * 0.9
    rng = np.random.default_rng(3)
    ph = 32
    grain = noise((0.8, 20), 11)
    fine = noise(0.8, 12)
    for r in range(N // ph):
        y0 = r * ph
        tone = rng.uniform(-0.07, 0.07)
        # plank end seams
        cuts = sorted(rng.integers(20, N - 20, size=2).tolist())
        xs = [0] + cuts + [N]
        for a, b in zip(xs[:-1], xs[1:]):
            t2 = rng.uniform(-0.05, 0.05)
            seg = (slice(y0, y0 + ph), slice(a, b))
            img[seg] += tone + t2 + grain[seg] * 0.045 + fine[seg] * 0.012
            # bevel: light top edge, dark bottom edge, dark end seams
            img[y0:y0 + 2, a:b] += 0.10
            img[y0 + ph - 3:y0 + ph, a:b] -= 0.16
            img[y0:y0 + ph, a:a + 2] -= 0.14
            if rng.random() < 0.5:
                kx, ky = rng.integers(a + 8, max(a + 9, b - 8)), y0 + rng.integers(8, ph - 8)
                yy, xx = np.ogrid[:N, :N]
                d = ((xx - kx) ** 2 / 36.0 + (yy - ky) ** 2 / 16.0)
                img -= np.exp(-d) * 0.12
            # nails near the plank ends
            for nx in (a + 5, b - 6):
                if 0 <= nx < N:
                    img[y0 + ph // 2 - 1:y0 + ph // 2 + 1, nx - 1:nx + 1] -= 0.18
    finish(img, 'floor_wood')


def stone_floor():
    img = np.ones((N, N), np.float32) * 0.9
    rng = np.random.default_rng(5)
    tile = 64
    spk = noise(0.9, 21)
    mott = noise(7, 22)
    for ty in range(N // tile):
        for tx in range(N // tile):
            y0, x0 = ty * tile, tx * tile
            seg = (slice(y0, y0 + tile), slice(x0, x0 + tile))
            img[seg] += rng.uniform(-0.06, 0.06) + mott[seg] * 0.025 + spk[seg] * 0.03
            img[y0:y0 + 3, x0:x0 + tile] += 0.10
            img[y0:y0 + tile, x0:x0 + 3] += 0.08
            img[y0 + tile - 3:y0 + tile, x0:x0 + tile] -= 0.20
            img[y0:y0 + tile, x0 + tile - 3:x0 + tile] -= 0.17
            if rng.random() < 0.35:       # hairline crack
                x, y = x0 + rng.integers(8, 40), y0 + rng.integers(8, 40)
                for k in range(rng.integers(14, 30)):
                    img[y % N, x % N] -= 0.14
                    x += rng.integers(0, 2)
                    y += rng.integers(0, 2) if rng.random() < 0.8 else -1
    finish(img, 'floor_stone')


def dirt_floor():
    img = 0.88 + noise(9, 31) * 0.05 + noise(2.5, 32) * 0.04 + noise(0.8, 33) * 0.03
    rng = np.random.default_rng(7)
    for _ in range(90):       # pebbles
        x, y = rng.integers(0, N), rng.integers(0, N)
        r = rng.uniform(1.5, 3.2)
        yy, xx = np.ogrid[:N, :N]
        dx = np.minimum(np.abs(xx - x), N - np.abs(xx - x))
        dy = np.minimum(np.abs(yy - y), N - np.abs(yy - y))
        d = (dx ** 2 + dy ** 2) / (r * r)
        img += np.exp(-d * 1.4) * 0.10 - np.exp(-((dx - 1.2) ** 2 + (dy - 1.5) ** 2) / (r * r) * 1.4) * 0.06
    finish(img, 'floor_dirt')


def plaster_wall():
    img = 0.95 + noise(14, 41) * 0.03 + noise(3.5, 42) * 0.025 + noise((1.2, 6), 43) * 0.02 + noise(0.8, 44) * 0.015
    finish(img, 'wall_plaster')


def brick_wall():
    img = np.ones((N, N), np.float32) * 0.9
    rng = np.random.default_rng(9)
    bw, bh = 64, 32
    spk = noise(0.9, 51)
    for r in range(N // bh):
        off = bw // 2 if r % 2 else 0
        for c in range(-1, N // bw + 1):
            x0, y0 = (c * bw + off), r * bh
            tone = rng.uniform(-0.07, 0.07)
            ys = np.arange(y0, y0 + bh) % N
            xs = np.arange(x0, x0 + bw) % N
            seg = np.ix_(ys, xs)
            img[seg] += tone + spk[seg] * 0.018
            img[np.ix_(ys[:3], xs)] += 0.10
            img[np.ix_(ys[-4:], xs)] -= 0.22
            img[np.ix_(ys, xs[:3])] -= 0.10
            img[np.ix_(ys, xs[-3:])] -= 0.24
    finish(img, 'wall_brick')


def wood_wall():
    img = np.ones((N, N), np.float32) * 0.9
    rng = np.random.default_rng(13)
    pw = 32
    grain = noise((22, 0.8), 61)
    for c in range(N // pw):
        x0 = c * pw
        img[:, x0:x0 + pw] += rng.uniform(-0.06, 0.06) + grain[:, x0:x0 + pw] * 0.05
        img[:, x0:x0 + 2] += 0.08
        img[:, x0 + pw - 3:x0 + pw] -= 0.22
    finish(img, 'wall_wood')


if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    for f in (wood_floor, stone_floor, dirt_floor, plaster_wall, brick_wall, wood_wall):
        f()
    print('textures ->', OUT, sorted(os.listdir(OUT)))
