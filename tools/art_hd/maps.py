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
        img = bake(self.grid, self.seed, self.shapes, getattr(self, 'grass', None))
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
    m.exits = [dict(to='velmoor', x=27 * T, y=53.4 * T, w=3 * T, h=T)]
    m.put('portal', 27, 52.8)
    return m


def velmoor():
    """Floresta de Velmoor (Cap. 2): corrupted elven woods, ruins, the Profane Dryad's grove in the south."""
    from env_ground import GRASS_VELMOOR
    m = Map('velmoor', 60, 60, seed=21)
    m.grass = GRASS_VELMOOR
    m.path([(30, -1), (30, 10), (22, 18), (24, 30), (36, 38), (32, 48), (30, 55)], 2.4)
    m.path([(22, 18), (8, 22), (4, 34)], 2.0)
    m.path([(36, 38), (50, 34), (54, 22)], 2.0)
    m.river([(61, 8), (52, 14), (44, 24), (46, 30), (58, 44), (61, 46)], 3.4)
    m.disk(12, 44, 4.2, 'w')
    m.disk(30, 52, 6.0, 's')          # ruined grove floor (boss arena)
    m.disk(24, 30, 3.2, 's')          # elven shrine (Sylra)
    for y in range(28, 33):
        for x in range(44, 50):
            if m.grid[y, x] == 'w':
                m.grid[y, x] = 'b'
    m.put('bridge', 46.8, 31.6)
    m.put('portal', 30, 1.2)
    for x, y in [(21, 28.6), (27, 28.6), (21, 32.2), (27, 32.2)]:
        m.put('ruin_pillar', x, y)
    m.put('ruin_arch', 30, 46.4)
    for x, y in [(25, 50), (35, 50), (25, 55.5), (35, 55.5)]:
        m.put('ruin_pillar', x, y)
    m.reserve(18, 26, 30, 34)
    m.reserve(22, 44, 38, 58)
    trees = ['tree_twisted', 'tree_twisted', 'tree_dead', 'tree_pine']
    m.scatter(trees, 120, (0, 0, 60, 60), pad=1, min_d=2.4)
    m.scatter(['mushrooms', 'mushrooms', 'roots', 'rock_small', 'stump', 'bush'], 90, (0, 0, 60, 60), pad=0, min_d=1.4)
    m.scatter(['tuft', 'roots'], 160, (0, 0, 60, 60), pad=0, min_d=0.8)
    m.player = (30 * T, 3.4 * T)
    m.npcs = [dict(id='sylra', x=24 * T, y=30.6 * T, look='sylra', facing='down')]
    sp = [('spirit_corrupt', 26, 12, 4), ('spirit_corrupt', 34, 16, 4), ('treant_demon', 16, 20, 5), ('spirit_corrupt', 10, 28, 5),
          ('oni_lancer', 38, 26, 5), ('treant_demon', 40, 40, 6), ('spirit_corrupt', 52, 26, 5), ('imp_hexer', 8, 36, 5),
          ('oni_shielder', 20, 40, 6), ('treant_demon', 44, 48, 6), ('spirit_corrupt', 16, 50, 6), ('oni_executioner', 40, 54, 6)]
    for k, x, y, lv in sp:
        m.spawns.append(dict(kind=k, x=x * T, y=y * T, level=lv))
    m.spawns.append(dict(kind='dryad_profane', x=30 * T, y=53 * T, level=7))
    m.exits = [dict(to='village', x=30 * T, y=0.4 * T, w=3 * T, h=T), dict(to='valemont', x=59.6 * T, y=22 * T, w=T, h=3 * T)]
    m.put('sign', 57.2, 24.4)
    return m


def valemont():
    """Cidade de Valemont (Cap. 3): walled capital - cathedral, Guild HQ, market, noble houses, a dark southern alley."""
    m = Map('valemont', 72, 64, seed=33)
    m.path([(36, -1), (36, 62)], 3.4, 's')              # main avenue
    m.path([(2, 32), (70, 32)], 3.2, 's')               # cross avenue
    m.path([(18, 14), (18, 50)], 2.4, 's')
    m.path([(54, 14), (54, 50)], 2.4, 's')
    m.disk(36, 32, 7.0, 's')                            # central plaza
    m.disk(36, 15, 5.2, 's')                            # cathedral square
    m.disk(46, 18, 4.0, 's')                            # guild forecourt
    m.path([(36, 52), (36, 60)], 2.6, 'd')              # dark alley (dirt)
    m.disk(36, 57, 4.4, 'd')
    # walls: north & south runs of 4-tile segments, towers on the corners and along the sides
    for x in range(4, 70, 4):
        if abs(x - 36) > 4:
            m.put('city_wall', x, 2.6)
        m.put('city_wall', x, 62.4)
    m.put('city_gate', 36, 3.2)
    for x, y in [(2, 3), (70, 3), (2, 62), (70, 62)] + [(1.2, v) for v in range(9, 58, 6) if not 28 < v < 37] + [(70.8, v) for v in range(9, 58, 6) if not 28 < v < 37]:
        m.put('city_tower', x, y)
    m.reserve(0, 0, 72, 5)
    m.reserve(0, 60, 72, 64)
    # landmarks
    m.put('cathedral', 36, 14.4)
    m.reserve(27, 4, 45, 15)
    m.put('guild', 47, 16.6)
    m.reserve(38, 6, 56, 17)
    m.put('fountain', 36, 33.6)
    m.reserve(30, 28, 42, 35)
    m.put('quest_board', 40.6, 22.6)
    for x, y in [(30, 22), (42, 22), (30, 26), (42, 26), (29, 38), (43, 38), (36, 8), (36, 48)]:
        m.put('lamp', x, y)
    for x in (33, 39):
        for y in (8.5, 21):
            m.put('banner_pole', x, y)
    # market stalls (east of plaza) and noble houses
    for x, y in [(46, 29), (51, 29), (46, 36.6), (51, 36.6)]:
        m.put('stall', x, y)
    m.reserve(43, 26, 55, 38)
    for x, y, k in [(10, 12, 'house_c'), (24, 12, 'house_b'), (10, 26, 'house_b'), (24, 26, 'house_c'),
                    (10, 42, 'house_c'), (24, 42, 'house_b'), (60, 12, 'house_c'), (66, 26, 'house_b'),
                    (60, 42, 'house_b'), (66, 48, 'house_c'), (47, 47, 'house_c')]:
        m.put(k, x, y)
        m.reserve(x - 4.5, y - 6, x + 4.5, y + 1)
    for x, y, k in [(14, 14, 'barrel'), (28, 14, 'crate'), (28, 28, 'barrel'), (14, 44, 'crate'), (62, 14, 'barrel'),
                    (40, 54, 'crate'), (33, 55, 'barrel'), (39, 58, 'barrel'), (33, 59, 'crate')]:
        m.put(k, x, y)
    for x in range(4, 68, 3):
        for y in (4.4, 60.6):
            if m.free(x, y, 0) and abs(x - 36) > 4:
                m.put(self_rnd(m, ['bush_flower', 'bush']), x + 0.4, y)
    m.scatter(['tree_round', 'tree_oak'], 22, (3, 6, 69, 58), pad=1, min_d=3.0)
    m.scatter(['bush_flower', 'bush', 'flowers', 'tuft'], 90, (3, 6, 69, 58), pad=0, min_d=1.0)
    m.player = (36 * T, 6.4 * T)
    m.npcs = [
        dict(id='guildmaster', x=47 * T, y=19.8 * T, look='v_guildmaster', facing='down'),
        dict(id='guard', x=33 * T, y=5.6 * T, look='v_guard', facing='down'),
        dict(id='noble', x=29.5 * T, y=29.4 * T, look='v_noble', facing='right'),
        dict(id='cleric', x=36 * T, y=19.2 * T, look='v_cleric', facing='down'),
        dict(id='child', x=40.5 * T, y=36.4 * T, look='v_child', facing='left'),
        dict(id='shopkeeper', x=48.5 * T, y=31 * T, look='merchant', facing='left'),
    ]
    for i, (k, x, y, lv) in enumerate([('imp_raider', 31, 54, 7), ('oni_executioner', 41, 55, 8), ('imp_howler', 34, 58.5, 7),
                                       ('oni_lancer', 40, 59, 8), ('imp_bomber', 32, 52, 7)]):
        m.spawns.append(dict(kind=k, x=x * T, y=y * T, level=lv))
    m.spawns.append(dict(kind='assassin_shadow', x=36 * T, y=57.4 * T, level=9))
    m.exits = [dict(to='velmoor', x=36 * T, y=0.5 * T, w=3 * T, h=T), dict(to='kharis', x=71.6 * T, y=32 * T, w=T, h=4 * T)]
    m.put('sign', 68.4, 34.6)
    return m


def _edge_exits(m, back, nxt, y=None):
    y = y if y is not None else m.gh / 2
    ex = [dict(to=back, x=0.4 * T, y=y * T, w=T, h=4 * T)]
    if nxt:
        ex.append(dict(to=nxt, x=(m.gw - 0.4) * T, y=y * T, w=T, h=4 * T))
    m.exits = ex


def kharis():
    """Deserto de Kharis (Cap. 4): oasis camp, obelisk ruins, skull fields, scorpion arena."""
    from env_ground import GRASS_DESERT
    m = Map('kharis', 64, 56, seed=44)
    m.grass = GRASS_DESERT
    m.path([(0, 28), (14, 28), (30, 32), (46, 26), (63, 28)], 2.8)
    m.path([(30, 32), (30, 48)], 2.0)
    m.path([(46, 26), (50, 8)], 2.0)
    m.disk(32, 22, 5.0, 'w')
    m.disk(32, 22, 6.6, 'w') if False else None
    m.disk(50, 28, 7.0, 's')           # scorpion arena (sandstone ring floor)
    m.disk(12, 26, 4.0, 's')           # nomad camp floor
    for y in range(32, 35):
        pass
    for x, y, k in [(8, 22, 'desert_tent'), (16, 22, 'desert_tent'), (9, 31, 'adobe_house'), (17, 32, 'adobe_house'), (23, 20, 'adobe_house')]:
        m.put(k, x, y)
        m.reserve(x - 4, y - 5, x + 4, y + 1)
    for x, y in [(28, 26), (36, 26), (31, 17.5), (33, 17.5), (28, 19), (36, 19)]:
        m.put('palm', x, y)
    m.reserve(26, 16, 39, 28)
    for x, y in [(44, 22), (56, 22), (44, 34), (56, 34), (50, 20), (50, 36)]:
        m.put('obelisk', x, y)
    m.reserve(42, 19, 59, 37)
    m.put('sign', 4, 29.4)
    m.put('sign', 59, 30)
    for x, y in [(20, 40), (36, 42), (44, 46), (10, 44), (24, 10), (40, 8), (56, 12), (6, 8)]:
        m.put('skull_pile', x, y)
    m.scatter(['cactus', 'cactus', 'sandstone', 'palm'], 40, (0, 0, 64, 56), pad=1, min_d=3.0)
    m.scatter(['sandstone', 'skull_pile', 'rock_small', 'tuft'], 80, (0, 0, 64, 56), pad=0, min_d=1.5)
    m.player = (4 * T, 28 * T)
    m.npcs = [dict(id='nomad', x=12 * T, y=27 * T, look='r_nomad', facing='down')]
    sp = [('sand_imp', 22, 14, 8), ('sand_imp', 36, 38, 8), ('sand_wraith', 26, 36, 9), ('oni_nomad', 20, 34, 9), ('sand_wraith', 40, 12, 9),
          ('oni_nomad', 36, 30, 9), ('sand_imp', 10, 46, 9), ('oni_nomad', 54, 10, 10), ('sand_wraith', 46, 42, 10), ('imp_pyro', 24, 50, 9)]
    for k, x, y, lv in sp:
        m.spawns.append(dict(kind=k, x=x * T, y=y * T, level=lv))
    m.spawns.append(dict(kind='scorpion_demon', x=51 * T, y=28 * T, level=11))
    _edge_exits(m, 'valemont', 'mines', 28)
    return m


def mines():
    """Minas de Durnhold (Cap. 5): crystal caverns, dwarven camp, the Ember Golem's forge."""
    from env_ground import GRASS_MINES
    m = Map('mines', 60, 56, seed=55)
    m.grass = GRASS_MINES
    m.path([(0, 28), (14, 28), (28, 24), (40, 30), (59, 28)], 2.8)
    m.path([(28, 24), (28, 8)], 2.2)
    m.path([(40, 30), (38, 46)], 2.2)
    m.disk(16, 40, 4.6, 'w')
    m.disk(12, 26, 4.2, 's')
    m.disk(49, 28, 7.2, 's')           # golem forge floor
    m.put('mine_entrance', 4.5, 24.4)
    m.reserve(1, 18, 9, 25)
    m.put('anvil', 10, 30)
    m.put('mine_cart', 15, 31)
    for x, y in [(8, 27), (15, 25), (24, 27), (34, 27), (43, 24), (55, 24), (43, 33), (55, 33)]:
        m.put('torch_post', x, y)
    for x, y in [(44, 20), (54, 20), (44, 37), (54, 37)]:
        m.put('crystal_red', x, y)
    m.reserve(41, 20, 58, 38)
    m.put('sign', 4, 30.4)
    m.put('sign', 55.6, 31)
    m.scatter(['stalagmite', 'stalagmite', 'rock_big', 'crystal_blue'], 55, (0, 0, 60, 56), pad=1, min_d=2.6)
    m.scatter(['crystal_blue', 'crystal_red', 'rock_small', 'mine_cart'], 24, (0, 0, 60, 56), pad=0, min_d=2.0)
    m.scatter(['rock_small', 'tuft'], 70, (0, 0, 60, 56), pad=0, min_d=1.2)
    m.player = (4 * T, 28 * T)
    m.npcs = [dict(id='dwarf', x=11 * T, y=29.4 * T, look='r_dwarf', facing='right')]
    sp = [('mine_imp', 20, 14, 10), ('mine_imp', 34, 10, 10), ('rock_oni', 26, 36, 11), ('mine_imp', 12, 48, 10), ('rock_oni', 38, 44, 11),
          ('imp_bomber', 46, 12, 11), ('rock_oni', 52, 46, 12), ('mine_imp', 30, 50, 11), ('imp_howler', 20, 22, 11), ('oni_shielder', 36, 18, 12)]
    for k, x, y, lv in sp:
        m.spawns.append(dict(kind=k, x=x * T, y=y * T, level=lv))
    m.spawns.append(dict(kind='ember_golem', x=49 * T, y=28 * T, level=13))
    _edge_exits(m, 'kharis', 'mirewail', 28)
    return m


def mirewail():
    """Pântano de Mirewail (Cap. 6): flooded woods, witch's stilt hut, the succubus Mirael."""
    from env_ground import GRASS_SWAMP
    m = Map('mirewail', 60, 56, seed=66)
    m.grass = GRASS_SWAMP
    for cx, cy, r in [(14, 12, 5.0), (30, 40, 6.0), (46, 14, 5.2), (10, 42, 4.6), (52, 44, 4.4), (28, 8, 3.6)]:
        m.disk(cx, cy, r, 'w')
    m.river([(0, 22), (10, 24), (22, 20), (34, 26), (46, 24), (60, 26)], 3.0)
    m.path([(0, 30), (12, 31), (24, 32), (36, 30), (48, 32), (59, 30)], 2.8)
    m.path([(24, 32), (24, 48)], 2.0)
    m.path([(36, 30), (40, 12)], 2.0)
    for y in range(28, 34):
        for x in range(0, 60):
            if m.grid[y, x] in 'wb' and 29 <= y <= 32:
                m.grid[y, x] = 'b'
    m.disk(46, 40, 5.0, 'd')           # Mirael's island
    m.disk(14, 31, 3.6, 'd')
    for x in range(0, 60, 6):
        if any(m.grid[y, min(x, 59)] == 'b' for y in range(28, 34)):
            m.put('bridge', x + 3, 26.6) if False else None
    m.put('stilt_hut', 12, 33.5)
    m.reserve(7, 26, 17, 35)
    m.put('cauldron', 17.5, 32.5)
    m.put('sign', 3.4, 32.4)
    m.put('sign', 56, 32.4)
    m.scatter(['swamp_tree', 'swamp_tree', 'tree_dead'], 70, (0, 0, 60, 56), pad=1, min_d=2.8)
    m.scatter(['reeds', 'reeds', 'bog_light', 'mushrooms', 'stump'], 100, (0, 0, 60, 56), pad=0, min_d=1.6)
    m.scatter(['tuft', 'roots'], 120, (0, 0, 60, 56), pad=0, min_d=1.0)
    m.player = (4 * T, 31 * T)
    m.npcs = [dict(id='witch', x=15 * T, y=33 * T, look='r_witch', facing='left')]
    sp = [('witch_imp', 20, 36, 12), ('bog_wraith', 30, 22, 12), ('bog_wraith', 38, 36, 13), ('witch_imp', 8, 20, 12), ('treant_demon', 26, 12, 13),
          ('bog_wraith', 50, 22, 13), ('witch_imp', 36, 48, 13), ('treant_demon', 10, 48, 13), ('imp_hexer', 44, 8, 13), ('oni_lancer', 52, 30, 14)]
    for k, x, y, lv in sp:
        m.spawns.append(dict(kind=k, x=x * T, y=y * T, level=lv))
    m.spawns.append(dict(kind='succubus_mirael', x=46 * T, y=40 * T, level=15))
    _edge_exits(m, 'mines', 'peaks', 31)
    return m


def peaks():
    """Picos Gelados (Cap. 7): snowfields, frozen statues, the Temple of Lumia and the Ice Demon."""
    from env_ground import GRASS_SNOW
    m = Map('peaks', 60, 56, seed=77)
    m.grass = GRASS_SNOW
    m.path([(0, 30), (14, 30), (28, 24), (30, 14)], 2.6)
    m.path([(28, 24), (30, 44)], 2.4)
    m.path([(30, 36), (59, 36)], 2.2)
    m.disk(30, 14, 6.0, 's')           # temple forecourt
    m.disk(30, 44, 7.0, 's')           # ice demon arena
    m.disk(44, 22, 3.6, 'w')
    m.put('lumia_temple', 30, 11.6)
    m.reserve(20, 4, 41, 12)
    for x, y in [(23, 16), (37, 16)]:
        m.put('frozen_statue', x, y)
    for x, y in [(23, 41), (37, 41), (30, 49), (22, 46), (38, 46), (26, 38), (34, 38)]:
        m.put('ice_spire', x, y)
    m.reserve(22, 37, 39, 51)
    m.put('sign', 4, 32)
    m.scatter(['snow_pine', 'snow_pine', 'snow_rock', 'ice_crystal'], 80, (0, 0, 60, 56), pad=1, min_d=2.6)
    m.scatter(['ice_crystal', 'snow_rock', 'tuft'], 70, (0, 0, 60, 56), pad=0, min_d=1.6)
    m.player = (4 * T, 30 * T)
    m.npcs = [dict(id='monk', x=30 * T, y=15.4 * T, look='r_monk', facing='down')]
    sp = [('frost_imp', 14, 20, 14), ('frost_imp', 40, 28, 14), ('ice_oni', 12, 40, 15), ('frost_imp', 48, 12, 14), ('ice_oni', 44, 44, 15),
          ('frost_imp', 20, 48, 15), ('ice_oni', 50, 36, 15), ('imp_howler', 8, 10, 14), ('oni_shielder', 36, 30, 15), ('frost_imp', 54, 50, 15)]
    for k, x, y, lv in sp:
        m.spawns.append(dict(kind=k, x=x * T, y=y * T, level=lv))
    m.spawns.append(dict(kind='ice_demon', x=30 * T, y=44 * T, level=17))
    _edge_exits(m, 'mirewail', 'castle', 30)
    return m


def castle():
    """Castelo de Valemont (Cap. 8): the royal keep overrun by demons; General Vorath holds the courtyard."""
    from env_ground import GRASS_CASTLE
    m = Map('castle', 64, 56, seed=88)
    m.grass = GRASS_CASTLE
    m.disk(32, 31, 13.0, 's')
    m.path([(0, 28), (20, 30), (32, 31)], 3.0, 's')
    m.path([(32, 31), (63, 30)], 3.0, 's')
    m.path([(32, 31), (32, 18)], 3.4, 's')
    m.disk(2, 28, 3, 'd')
    for x in range(4, 62, 4):
        m.put('city_wall', x, 2.6)
        m.put('city_wall', x, 53.6)
    for x, y in [(2, 3), (62, 3), (2, 54), (62, 54)] + [(1.2, v) for v in range(9, 52, 6) if not 24 < v < 34] + [(62.8, v) for v in range(9, 52, 6) if not 24 < v < 34]:
        m.put('city_tower', x, y)
    m.reserve(0, 0, 64, 5)
    m.reserve(0, 51, 64, 56)
    m.put('castle_keep', 32, 14.2)
    m.reserve(18, 3, 46, 16)
    for x, y in [(22, 20), (42, 20), (22, 40), (42, 40), (14, 30), (50, 30), (32, 44)]:
        m.put('brazier', x, y)
    for x, y in [(26, 20), (38, 20), (16, 24), (48, 24), (16, 36), (48, 36)]:
        m.put('demon_banner', x, y)
    m.put('sign', 5.4, 30.4)
    m.put('sign', 58, 32.4)
    m.scatter(['rock_small', 'stump', 'tuft', 'ruin_pillar'], 40, (3, 6, 61, 50), pad=0, min_d=2.0)
    m.scatter(['crate', 'barrel', 'skull_pile'], 24, (3, 6, 61, 50), pad=0, min_d=2.4)
    m.player = (4 * T, 28 * T)
    m.npcs = [dict(id='elowen', x=6.6 * T, y=29 * T, look='x_knight', facing='right')]
    sp = [('demon_knight', 20, 24, 17), ('demon_knight', 20, 38, 17), ('demon_knight', 44, 24, 18), ('demon_knight', 44, 38, 18),
          ('oni_executioner', 28, 26, 18), ('oni_executioner', 36, 36, 18), ('ash_wraith', 12, 40, 17), ('ash_wraith', 52, 20, 18),
          ('imp_howler', 14, 20, 17), ('imp_bomber', 50, 42, 18), ('oni_shielder', 32, 24, 18)]
    for k, x, y, lv in sp:
        m.spawns.append(dict(kind=k, x=x * T, y=y * T, level=lv))
    m.spawns.append(dict(kind='vorath', x=32 * T, y=21 * T, level=20))
    _edge_exits(m, 'peaks', 'wastelands', 30)
    return m


def wastelands():
    """Terras Devastadas (Cap. 9): scorched hellscape - four generals guard four corners."""
    from env_ground import GRASS_ASH
    m = Map('wastelands', 72, 60, seed=99)
    m.grass = GRASS_ASH
    for cx, cy, r in [(36, 8, 4.0), (36, 52, 4.0), (24, 30, 3.4), (50, 30, 3.4), (6, 28, 2.6), (66, 36, 3.0)]:
        m.disk(cx, cy, r, 'w')
    m.path([(0, 30), (20, 30), (36, 30)], 3.0)
    m.path([(36, 30), (71, 30)], 3.0)
    m.path([(36, 30), (24, 20), (14, 12)], 2.6)
    m.path([(36, 30), (48, 20), (58, 12)], 2.6)
    m.path([(36, 30), (24, 40), (14, 48)], 2.6)
    m.path([(36, 30), (48, 40), (58, 48)], 2.6)
    for cx, cy in [(14, 12), (58, 12), (14, 48), (58, 48)]:
        m.disk(cx, cy, 6.4, 's')
    m.disk(36, 30, 4.6, 's')
    for cx, cy in [(14, 12), (58, 12), (14, 48), (58, 48)]:
        for a in range(0, 360, 60):
            import math as _m
            m.put('obsidian_spire', cx + _m.cos(_m.radians(a)) * 8.0, cy + _m.sin(_m.radians(a)) * 6.0 + 1.5)
        m.reserve(cx - 7, cy - 7, cx + 7, cy + 7)
    for x, y in [(33, 27), (39, 27), (33, 34), (39, 34)]:
        m.put('brazier', x, y)
    m.put('demon_banner', 36, 26)
    m.put('sign', 3.6, 31.4)
    m.put('sign', 68, 32)
    m.scatter(['tree_dead', 'obsidian_spire', 'crystal_red'], 50, (0, 0, 72, 60), pad=1, min_d=3.0)
    m.scatter(['skull_pile', 'rock_small', 'stalagmite', 'ruin_pillar'], 50, (0, 0, 72, 60), pad=0, min_d=2.0)
    m.scatter(['tuft', 'roots'], 60, (0, 0, 72, 60), pad=0, min_d=1.2)
    m.player = (4 * T, 30 * T)
    m.npcs = [dict(id='cedric', x=35 * T, y=31.4 * T, look='x_veteran', facing='down')]
    gens = [('thornmaw_alpha', 14, 12, 21), ('velka_flamebeak', 58, 12, 21), ('krull_chainlord', 14, 48, 22), ('morgash_ironhorn', 58, 48, 22)]
    for k, x, y, lv in gens:
        m.spawns.append(dict(kind=k, x=x * T, y=y * T, level=lv))
    sp = [('demon_knight', 26, 24, 19), ('demon_knight', 46, 24, 19), ('demon_knight', 26, 38, 20), ('demon_knight', 46, 38, 20),
          ('ash_wraith', 10, 22, 19), ('ash_wraith', 62, 22, 19), ('ash_wraith', 10, 38, 20), ('ash_wraith', 62, 38, 20),
          ('oni_executioner', 30, 14, 20), ('oni_executioner', 42, 46, 20), ('imp_pyro', 20, 30, 19), ('imp_pyro', 52, 30, 19)]
    for k, x, y, lv in sp:
        m.spawns.append(dict(kind=k, x=x * T, y=y * T, level=lv))
    _edge_exits(m, 'castle', 'citadel', 30)
    return m


def citadel():
    """Cidadela de Malgrath (Cap. 10): obsidian fortress, the throne hall of the Demon King."""
    from env_ground import GRASS_CITADEL
    m = Map('citadel', 60, 64, seed=111)
    m.grass = GRASS_CITADEL
    m.path([(30, 64), (30, 40)], 4.0, 's')
    m.path([(30, 40), (30, 22)], 5.0, 's')
    m.disk(30, 16, 10.0, 's')
    m.disk(30, 52, 5.0, 's')
    for cx, cy, r in [(8, 20, 4.4), (52, 20, 4.4), (8, 48, 4.0), (52, 48, 4.0), (10, 8, 3.0), (50, 8, 3.0)]:
        m.disk(cx, cy, r, 'w')
    m.put('hell_gate', 30, 60.4)
    m.reserve(22, 56, 38, 64)
    m.put('throne', 30, 10.4)
    m.reserve(24, 2, 36, 12)
    import math as _m
    for i in range(7):
        y = 22 + i * 5
        m.put('brazier', 24, y)
        m.put('brazier', 36, y)
    for x, y in [(22, 12), (38, 12), (18, 18), (42, 18)]:
        m.put('demon_banner', x, y)
    for a in range(0, 360, 45):
        m.put('obsidian_spire', 30 + _m.cos(_m.radians(a)) * 12.5, 17 + _m.sin(_m.radians(a)) * 9.0)
    m.scatter(['obsidian_spire', 'crystal_red', 'stalagmite'], 40, (0, 0, 60, 64), pad=1, min_d=3.0)
    m.scatter(['skull_pile', 'rock_small', 'ruin_pillar'], 40, (0, 0, 60, 64), pad=0, min_d=2.2)
    m.player = (30 * T, 61 * T)
    m.npcs = [dict(id='lumia', x=30 * T, y=54 * T, look='x_lumia', facing='up')]
    sp = [('demon_knight', 26, 44, 23), ('demon_knight', 34, 44, 23), ('ash_wraith', 20, 38, 23), ('ash_wraith', 40, 38, 23),
          ('oni_shielder', 26, 32, 23), ('oni_shielder', 34, 32, 23), ('oni_executioner', 22, 28, 24), ('oni_executioner', 38, 28, 24),
          ('demon_knight', 26, 24, 24), ('demon_knight', 34, 24, 24), ('imp_howler', 18, 16, 23), ('imp_howler', 42, 16, 23)]
    for k, x, y, lv in sp:
        m.spawns.append(dict(kind=k, x=x * T, y=y * T, level=lv))
    m.spawns.append(dict(kind='malgrath', x=30 * T, y=15 * T, level=26))
    m.exits = [dict(to='wastelands', x=30 * T, y=63.6 * T, w=6 * T, h=T)]
    return m


def self_rnd(m, items):
    return m.rnd.choice(items)


if __name__ == '__main__':
    import sys
    which = sys.argv[1:] or ['village', 'velmoor', 'valemont', 'kharis', 'mines', 'mirewail', 'peaks', 'castle', 'wastelands', 'citadel']
    for n in which:
        globals()[n]().export()
