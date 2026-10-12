"""World maps: layout -> baked ground chunks + map JSON for Unity.

Output: unity/Assets/Resources/Maps/<name>/g_<cx>_<cy>.png + Maps/<name>.json
Coordinates in JSON are pixels, origin top-left, y down (Unity converts with PPU=64, y flipped).
"""
from __future__ import annotations
import json
import math
import os
import random
import sys
import numpy as np
from PIL import Image
from env_ground import bake, T
from env_objects import PROPS
from sheet import ROOT

OUT = os.path.join(ROOT, 'unity', 'Assets', 'Resources', 'Maps')
CHUNK = 1024


class Map:
    def __init__(self, name, gw, gh, seed=1):
        self.name, self.gw, self.gh, self.seed = name, gw, gh, seed
        self.grid = np.full((gh, gw), 'g', dtype='<U1')
        self.props = []
        self.spawns = []
        self.npcs = []
        self.exits = []
        self.player = (gw * T / 2, gh * T / 2)
        self.rnd = random.Random(seed)
        self.reserved = np.zeros((gh, gw), bool)   # no random scatter here
        self.shapes = []

    # -------- terrain painting
    def rect(self, x0, y0, x1, y1, code):
        self.shapes.append(('rect', code, (x0, y0, x1, y1)))
        self.grid[max(0, y0):min(self.gh, y1), max(0, x0):min(self.gw, x1)] = code

    def disk(self, cx, cy, r, code):
        self.shapes.append(('disk', code, (cx, cy, r)))
        for y in range(self.gh):
            for x in range(self.gw):
                if (x + 0.5 - cx) ** 2 + (y + 0.5 - cy) ** 2 <= r * r:
                    self.grid[y, x] = code

    def path(self, pts, width, code='d'):
        self.shapes.append(('path', code, (pts, width)))
        for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
            n = int(max(abs(x1 - x0), abs(y1 - y0)) * 3) + 1
            for i in range(n + 1):
                t = i / n
                x, y = x0 + (x1 - x0) * t, y0 + (y1 - y0) * t
                for yy in range(int(y - width / 2), int(y + width / 2 + 0.999)):
                    for xx in range(int(x - width / 2), int(x + width / 2 + 0.999)):
                        if 0 <= xx < self.gw and 0 <= yy < self.gh and self.grid[yy, xx] not in 'wb':
                            self.grid[yy, xx] = code

    def river(self, pts, width):
        self.shapes.append(('path', 'w', (pts, width)))
        for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
            n = int(max(abs(x1 - x0), abs(y1 - y0)) * 3) + 1
            for i in range(n + 1):
                t = i / n
                x, y = x0 + (x1 - x0) * t, y0 + (y1 - y0) * t
                for yy in range(int(y - width / 2), int(y + width / 2 + 0.999)):
                    for xx in range(int(x - width / 2), int(x + width / 2 + 0.999)):
                        if 0 <= xx < self.gw and 0 <= yy < self.gh:
                            self.grid[yy, xx] = 'w'

    # -------- objects (positions in tiles, base point)
    def put(self, kind, tx, ty, reserve=0):
        self.props.append(dict(kind=kind, x=round(tx * T, 1), y=round(ty * T, 1)))
        if reserve:
            self.reserve(tx - reserve, ty - reserve, tx + reserve, ty + 1)

    def reserve(self, x0, y0, x1, y1):
        self.reserved[max(0, int(y0)):max(0, int(math.ceil(y1))), max(0, int(x0)):max(0, int(math.ceil(x1)))] = True

    def free(self, tx, ty, pad=1):
        x, y = int(tx), int(ty)
        for yy in range(y - pad, y + pad + 1):
            for xx in range(x - pad, x + pad + 1):
                if not (0 <= xx < self.gw and 0 <= yy < self.gh):
                    return False
                if self.grid[yy, xx] != 'g' or self.reserved[yy, xx]:
                    return False
        return True

    def scatter(self, kinds, count, area, pad=1, min_d=1.6):
        x0, y0, x1, y1 = area
        placed = []
        tries = 0
        while len(placed) < count and tries < count * 40:
            tries += 1
            tx, ty = self.rnd.uniform(x0, x1), self.rnd.uniform(y0, y1)
            if not self.free(tx, ty, pad):
                continue
            if any((tx - px) ** 2 + (ty - py) ** 2 < min_d ** 2 for px, py in placed):
                continue
            k = self.rnd.choice(kinds)
            placed.append((tx, ty))
            self.put(k, tx, ty)
            if pad:
                self.reserve(tx - 0.5, ty - 0.5, tx + 0.5, ty + 0.5)
        return placed

    # -------- export
    def export(self):
        d = os.path.join(OUT, self.name)
        os.makedirs(d, exist_ok=True)
        img = bake(self.grid, self.seed, self.shapes)
        h, w = img.shape[:2]
        cx, cy = math.ceil(w / CHUNK), math.ceil(h / CHUNK)
        for j in range(cy):
            for i in range(cx):
                tile = img[j * CHUNK:(j + 1) * CHUNK, i * CHUNK:(i + 1) * CHUNK]
                Image.fromarray(tile, 'RGB').save(os.path.join(d, f'g_{i}_{j}.png'), optimize=True)
        blocked = ''.join('1' if c == 'w' else '0' for c in self.grid.flatten())
        data = dict(name=self.name, w=self.gw, h=self.gh, tile=T, chunk=CHUNK, chunksX=cx, chunksY=cy,
                    blocked=blocked, playerX=self.player[0], playerY=self.player[1],
                    props=sorted(self.props, key=lambda p: p['y']), spawns=self.spawns, npcs=self.npcs, exits=self.exits)
        with open(os.path.join(OUT, self.name + '.json'), 'w') as fp:
            json.dump(data, fp, indent=0)
        Image.fromarray(img, 'RGB').resize((w // 4, h // 4)).save(os.path.join(ROOT, 'tools', 'art_hd', f'_{self.name}_ground_small.png'))
        print(f'map {self.name}: {self.gw}x{self.gh} tiles, {len(self.props)} props, {len(self.spawns)} spawns')
        return img


def village():
    """Vila de Aurora (start) — north: Guild plaza; south: Bosque dos Chifres (imps)."""
    m = Map('village', 56, 54, seed=7)
    # river from the north-east down the east side, a pond in the south-west
    m.river([(45, -1), (44, 8), (46, 16), (45, 24), (47, 33), (46, 42), (48, 55)], 4)
    m.disk(9, 44, 3.6, 'w')
    # plaza and paths
    m.path([(27, 19), (27, 54)], 2.6)
    m.path([(27, 19), (3, 21), (-1, 21)], 2.4)
    m.path([(27, 19), (50, 20), (57, 20)], 2.4)
    m.path([(16, 20), (16, 13)], 2.0)
    m.path([(37, 19), (38, 26)], 2.0)
    m.path([(27, 30), (14, 31), (12, 34)], 2.0)
    m.path([(27, 40), (36, 46), (40, 48)], 2.0)
    m.disk(27, 19, 6.2, 's')
    # bridge over the river (walkable)
    for y in range(19, 22):
        for x in range(41, 50):
            if m.grid[y, x] == 'w':
                m.grid[y, x] = 'b'
    m.put('bridge', 45.5, 21.7)
    # farm plots
    m.rect(4, 26, 11, 30, 't')
    m.rect(4, 31, 11, 34, 't')
    for x in range(4, 11):
        m.put('fence', x + 0.55, 25.5)
    m.reserve(3, 25, 12, 35)

    # buildings
    m.put('guild', 27, 13.2, reserve=0)
    m.reserve(20, 6, 34, 14)
    m.put('quest_board', 32.6, 14.6)
    m.reserve(31, 13.5, 34.5, 15)
    m.put('house_a', 15.8, 12.6)
    m.reserve(12, 7, 20, 13.5)
    m.put('house_b', 38.6, 25.5)
    m.reserve(35.5, 21, 42, 26.2)
    m.put('house_a', 15.0, 30.3)
    m.reserve(11, 25, 19.5, 31)
    m.put('house_b', 8.0, 12.8)
    m.reserve(5, 8, 11, 13.5)
    m.put('house_a', 37.5, 12.3)
    m.reserve(33.5, 7, 42, 13)
    m.put('well', 27, 20.4)
    m.reserve(25.5, 18.5, 28.5, 21)
    for (x, y) in [(21.5, 15.8), (32.5, 15.8), (21.5, 23.6), (32.5, 23.6)]:
        m.put('lamp', x, y)
    m.put('stall', 31.6, 21.8)
    m.put('stall', 22.2, 21.6)
    m.put('sign', 29.6, 30.0)
    m.put('sign', 49.5, 18.6)
    for x, y, k in [(18.5, 12.9, 'barrel'), (19.4, 13.2, 'crate'), (11.2, 31.0, 'barrel'), (41.3, 25.9, 'crate'),
                    (34.6, 12.7, 'barrel'), (24.0, 22.4, 'crate'), (20.6, 22.0, 'barrel')]:
        m.put(k, x, y)
    for x, y in [(19.5, 12.8), (12.4, 13.4), (41.2, 13.0), (35.0, 26.2), (19.0, 31.0)]:
        m.put('bush_flower', x, y)
    m.reserve(18, 11, 21, 14)

    # forest border north + south woods
    trees = ['tree_oak', 'tree_oak', 'tree_pine', 'tree_round']
    m.scatter(trees, 26, (0, 0.6, 56, 6), pad=1, min_d=2.6)
    m.scatter(['tree_pine', 'tree_oak'], 14, (0, 6, 4, 26), pad=1, min_d=2.4)
    m.scatter(['tree_pine', 'tree_oak', 'tree_round'], 12, (49, 6, 56, 40), pad=1, min_d=2.4)
    m.scatter(['tree_oak', 'tree_pine', 'tree_pine'], 60, (0, 36, 56, 54), pad=1, min_d=2.5)
    m.scatter(['bush', 'bush', 'bush_flower', 'rock_small', 'rock_big', 'stump'], 60, (0, 0, 56, 54), pad=0, min_d=1.5)
    m.scatter(['tuft', 'tuft', 'flowers'], 220, (0, 0, 56, 54), pad=0, min_d=0.7)

    m.player = (27 * T, 26 * T)
    m.npcs = [
        dict(id='receptionist', x=27 * T, y=15.0 * T, look='guild_clerk', facing='down'),
        dict(id='blacksmith', x=34.0 * T, y=22.4 * T, look='merchant', facing='left'),
        dict(id='villager', x=20.0 * T, y=26.0 * T, look='villager', facing='right'),
    ]
    # imps in the southern woods; tougher pack near the pond
    for i, (x, y) in enumerate([(24, 42), (31, 44), (20, 47), (35, 49), (12, 40), (15, 49), (40, 41), (29, 51)]):
        m.spawns.append(dict(kind='imp', x=x * T, y=y * T, level=1 + (i % 3)))
    for i, (x, y) in enumerate([(33, 47), (18, 44), (38, 51)]):
        m.spawns.append(dict(kind='oni', x=x * T, y=y * T, level=2 + i % 2))
    for k, x, y, lv in [('imp_scout', 14, 38, 2), ('imp_raider', 30, 40, 2), ('imp_pyro', 8, 48, 2), ('imp_hexer', 36, 44, 3), ('imp_bomber', 25, 46, 2), ('imp_howler', 42, 46, 3), ('oni_lancer', 16, 52, 3), ('oni_shielder', 31, 52, 3), ('oni_executioner', 44, 52, 4)]:
        m.spawns.append(dict(kind=k, x=x * T, y=y * T, level=lv))
    m.spawns.append(dict(kind='grakk', x=22 * T, y=51.5 * T, level=4))
    m.exits = [dict(to='forest', x=27 * T, y=53.5 * T, w=3 * T, h=T)]
    return m


if __name__ == '__main__':
    village().export()
