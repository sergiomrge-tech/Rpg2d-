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
from expand_maps import expand
import vegetation
import town_life
from env_ground import bake, T
from env_objects import PROPS
from sheet import ROOT
sys.path.insert(0, os.path.join(ROOT, 'tools'))
from interiors import patch_map as interiors_patch   # noqa: E402

OUT = os.path.join(ROOT, 'godot', 'assets', 'Maps')
CHUNK = 1024
TOWN_WALKERS = {'valemont': 16, 'village': 5}
JSON_ONLY = '--json-only' in sys.argv
EXPAND_FACTOR = {n: 0.21 for n in ['village', 'velmoor', 'kharis', 'mines', 'mirewail', 'peaks', 'castle', 'wastelands', 'citadel']}   # ring of new land on each side => ~2x area


def thin_spawns(spawns, keep=0.4, start=(72.5, 8.5), safe=16.0):
    """Starting region: no packs around the hero's spawn and roughly 2/5 of the original monsters elsewhere."""
    out = []
    for i, sp in enumerate(spawns):
        tx, ty = sp['x'] / T, sp['y'] / T
        if math.hypot(tx - start[0], ty - start[1]) < safe:
            continue
        if sp['kind'] == 'grakk' or i % 5 in (0, 2) or (i % 5 == 4 and i % 2 == 0):
            out.append(sp)
    return out


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
        if not hasattr(self, 'scatter_log'):
            self.scatter_log = []
        self.scatter_log.append((list(kinds), count, tuple(area), pad, min_d))
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
        if self.name in EXPAND_FACTOR and not getattr(self, '_expanded', False):
            f = EXPAND_FACTOR[self.name]
            expand(self, round(self.gw * f), round(self.gh * f))
        vegetation.add(self)
        if self.name in TOWN_WALKERS:
            town_life.add_walkers(self, TOWN_WALKERS[self.name])
        if self.name == 'village':
            self.spawns = thin_spawns(self.spawns)
        d = os.path.join(OUT, self.name)
        os.makedirs(d, exist_ok=True)
        if JSON_ONLY:      # keep the already-baked ground; only rewrite the map JSON (props, spawns, ...)
            h, w = self.gh * T, self.gw * T
            cx, cy = math.ceil(w / CHUNK), math.ceil(h / CHUNK)
            img = None
        else:
            img = bake(self.grid, self.seed, self.shapes, getattr(self, 'grass', None))
            h, w = img.shape[:2]
            cx, cy = math.ceil(w / CHUNK), math.ceil(h / CHUNK)
            for j in range(cy):
                for i in range(cx):
                    tile = img[j * CHUNK:(j + 1) * CHUNK, i * CHUNK:(i + 1) * CHUNK]
                    Image.fromarray(tile, 'RGB').save(os.path.join(d, f'g_{i}_{j}.png'), optimize=True)
        blocked = ''.join('1' if c in 'wx' else '0' for c in self.grid.flatten())
        data = dict(name=self.name, w=self.gw, h=self.gh, tile=T, chunk=CHUNK, chunksX=cx, chunksY=cy,
                    blocked=blocked, playerX=self.player[0], playerY=self.player[1],
                    props=sorted(self.props, key=lambda p: p['y']), spawns=self.spawns, npcs=self.npcs, exits=self.exits,
                    caches=getattr(self, 'caches', []), walkers=getattr(self, 'walkers', []))
        data = interiors_patch(data)      # door exits, NPCs moved indoors, extra Aurora buildings
        with open(os.path.join(OUT, self.name + '.json'), 'w') as fp:
            json.dump(data, fp, indent=0)
        if img is not None:
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
    m.safe_points = [(72, 8)]          # new-game start meadow (in expanded-map tile coordinates)
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
    """Cidade de Valemont (Cap. 3): circular walled capital - concentric + radial streets, a river through the west,
    cathedral and Guild HQ flanking the avenue, central fountain plaza, market, noble quarter, dark south alley."""
    m = Map('valemont', 100, 100, seed=33)
    C = (50.0, 50.0)
    RW = 31.0

    def pol(r, deg):
        return (C[0] + r * math.cos(math.radians(deg)), C[1] + r * math.sin(math.radians(deg)))

    # ---- river: enters the west wall, bends through the south-west quarter, leaves by the SW water gate
    river = [(-1, 36), (10, 39), (21, 40.5), (27, 42), (34, 45), (38, 50), (39.5, 56), (37.5, 63), (34.5, 70.7), (30, 78), (26, 90), (22, 101)]
    # ---- roads outside (dirt) and avenues inside (stone)
    m.path([(50, -1), (50, 19)], 3.2, 'd')                    # north road to Velmoor
    m.path([(81, 50), (101, 50)], 3.2, 'd')                   # east road to Kharis
    m.path([(19, 50), (-1, 52)], 3.0, 'd')                    # west road (farms)
    m.river(river, 3.2)
    m.path([(50, 19), (50, 62)], 3.4, 's')                    # north-south avenue
    m.path([(19, 50), (81, 50)], 3.4, 's')                    # west-east avenue
    # diagonals + concentric ring roads (skip the river sector)
    for ang in (-135, -45, 45):
        m.path([pol(7, ang), pol(28.5, ang)], 2.2, 's')
    for r in (16.5,):
        pts = [pol(r, a) for a in range(-100, 100, 6)] + [pol(r, 100)]
        m.path(pts, 2.2, 's')
        pts2 = [pol(r, a) for a in range(206, 262, 6)]
        if len(pts2) > 1:
            m.path(pts2, 2.2, 's')
    m.disk(C[0], C[1], 6.8, 's')                              # central plaza
    m.disk(38, 38.5, 4.6, 's')                                # cathedral square
    m.disk(62, 38.5, 4.6, 's')                                # guild forecourt
    # ---- dark south alley (dirt, dead end under the wall)
    m.path([(50, 62), (50, 74)], 2.6, 'd')
    m.disk(50, 76.4, 4.6, 'd')
    # ---- wall ring: arcs between the gates / river gaps
    gaps = [(270, 5.4), (0, 5.4), (180, 5.4), (199, 5.8), (127, 5.8)]    # N gate, E gate, W gate, river in, river out
    iv = sorted(((g - w) % 360, (g + w) % 360) for g, w in gaps)
    for i, (s0, e0) in enumerate(iv):
        nxt = iv[(i + 1) % len(iv)][0]
        a0, a1 = e0, nxt if nxt > e0 else nxt + 360
        pts = [pol(RW, a) for a in np.linspace(a0, a1, max(3, int((a1 - a0) / 4)))]
        m.path(pts, 2.5, 'x')
    # ---- wall furniture: towers, gates, banners
    for a in range(0, 360, 30):
        if any(abs((a - g + 180) % 360 - 180) < 9 for g, _ in gaps):
            continue
        x, y = pol(RW + 0.2, a)
        m.put('city_tower', x, y + 0.8)
    for x, y in [pol(RW, 270), pol(RW, 0), pol(RW, 180)]:
        m.put('city_gate', x, y + 0.9)
    for ang in (270, 0, 180):
        for dd in (-3.6, 3.6):
            x, y = pol(RW - 1.5, ang)
            m.put('banner_pole', x + (dd if ang in (270, 90) else 0), y + (dd if ang in (0, 180) else 0) + 0.6)
    m.reserve(0, 0, 100, 100)                                 # clear; re-open below
    m.reserved[:, :] = False
    # ---- landmarks
    hm = np.zeros((m.gh, m.gw), bool)

    def hres(x0, y0, x1, y1):
        hm[int(y0):int(y1) + 1, int(x0):int(x1) + 1] = True
    m.put('fountain', 50, 51.2)
    m.reserve(44, 45, 56, 53)
    hres(46.5, 48, 53.5, 53)
    m.put('cathedral', 38, 36.4)
    m.reserve(30, 26, 47, 37)
    hres(34, 29, 42, 37)
    m.put('guild', 62, 36.8)
    m.reserve(52, 28, 72, 38)
    hres(56, 31, 68, 37.5)
    m.put('quest_board', 57.6, 43.2)
    m.reserve(55, 41.5, 60, 44.2)
    m.put('bridge', 38.2, 51.4)
    for y in range(49, 53):
        for x in range(36, 41):
            if m.grid[y, x] == 'w':
                m.grid[y, x] = 'b'
    for x, y in [(46, 30), (54, 30), (46, 42), (54, 42), (46, 58), (54, 58), (30, 47.6), (70, 47.6), (30, 52.6), (70, 52.6)]:
        m.put('lamp', x, y)
    for x in (45.4, 54.6):
        m.put('banner_pole', x, 27.2)
    # market stalls south-east of the plaza
    for (x, y), k in zip([(57, 54.6), (62, 54.6), (57, 60), (62, 60), (67, 57.5)], ['stall', 'stall_blue', 'stall_green', 'stall', 'stall_blue']):
        m.put(k, x, y)
    m.reserve(54, 52, 70, 63)
    for sx, sy in [(57, 54.6), (62, 54.6), (57, 60), (62, 60), (67, 57.5)]:
        hres(sx - 2.4, sy - 1.5, sx + 2.4, sy + 0.5)
    # ---- noble quarter (east) with larger houses
    for x, y, k in [(64, 70, 'house_c'), (72, 62, 'house_c'), (58, 68.5, 'house_b')]:
        m.put(k, x, y)
        m.reserve(x - 3.2, y - 5.4, x + 3.2, y + 1.0)
        hres(x - 2.2, y - 1.5, x + 2.2, y + 0.8)
    # ---- parks (two great groves, as in the reference art)
    for gx, gy in [(34, 44.6), (66, 66.6)]:
        pass
    park = [(35.0, 60.5), (61.0, 24.5)]
    for gx, gy in park:
        for a in range(0, 360, 40):
            m.put(m.rnd.choice(['tree_oak', 'tree_round', 'tree_oak']), gx + math.cos(math.radians(a)) * 3.4, gy + math.sin(math.radians(a)) * 2.9)
        m.put('tree_oak', gx, gy)
        for k in range(5):
            m.put('flowers', gx + m.rnd.uniform(-2.5, 2.5), gy + m.rnd.uniform(-2, 2))
        m.reserve(gx - 5, gy - 5, gx + 5, gy + 4)
        hres(gx - 4, gy - 3.5, gx + 4, gy + 3.5)
    # ---- town services: placed on the nearest free ground to a desired spot (tavern, smithy, stable, shops, barracks, library)
    def place(kind, ax, ay, hw, search=12.0):
        best = None
        steps = int(search * 2)
        for iy in range(-steps, steps + 1):
            for ix in range(-steps, steps + 1):
                x, y = ax + ix * 0.5, ay + iy * 0.5
                if math.hypot(x - C[0], y - C[1]) > RW - 3.6:
                    continue
                x0, x1, y0, y1 = int(x - hw), int(x + hw) + 1, int(y - 1.4), int(y + 1.8) + 1
                if y0 < 2 or x0 < 2 or x1 >= m.gw - 2 or y1 >= m.gh - 2:
                    continue
                if (m.grid[y0:y1, x0:x1] != 'g').any() or hm[y0:y1, x0:x1].any():
                    continue
                d = math.hypot(ix, iy)
                if best is None or d < best[0]:
                    best = (d, x, y)
        if best is None:
            print('WARN: could not place', kind)
            return None
        _, x, y = best
        m.put(kind, x, y)
        hres(x - hw - 0.4, y - 1.6, x + hw + 0.4, y + 1.8)
        m.reserve(x - hw - 1, y - 5, x + hw + 1, y + 2)
        return (x, y)
    spot = {}
    for kind, ax, ay, hw in [('tavern', 70, 47.5, 3.2), ('smithy', 30, 47.5, 2.8), ('stable', 28, 59, 3.8), ('apothecary', 43, 58, 2.5),
                             ('armory', 58, 66, 2.6), ('bakery', 66, 62.5, 2.4), ('barracks', 70, 33, 3.6), ('library', 31, 36, 2.4)]:
        spot[kind] = place(kind, ax, ay, hw)
    # street furniture around the services
    sx, sy = spot.get('stable') or (28, 59)
    for dx, dy, k in [(4.6, 0.8, 'trough'), (-4.4, 1.0, 'hay_bale'), (-5.5, 1.2, 'hay_bale'), (5.8, 2.6, 'hay_cart')]:
        m.put(k, sx + dx, sy + dy)
    tx, ty = spot.get('tavern') or (70, 47.5)
    for dx, dy, k in [(-4.4, 1.6, 'bench'), (4.4, 1.6, 'bench')]:
        m.put(k, tx + dx, ty + dy)
    # plaza dressing: planters + benches around the fountain, statue of the hero, ornate lamps along the avenues
    for a in range(0, 360, 45):
        x, y = pol(7.8, a + 22)
        m.put('planter', x, y)
    for a in (45, 135, 225, 315):
        x, y = pol(6.2, a)
        m.put('bench', x, y + 0.4)
    m.put('statue_hero', 38, 41.4)
    m.put('statue_hero', 62, 41.4)
    for y in (24, 30, 36, 42, 58, 64):
        m.put('lamp_ornate', 47.6, y)
        m.put('lamp_ornate', 52.4, y)
    for x in (25, 32, 38.5, 61.5, 68, 75):
        m.put('lamp_ornate', x, 47.6)
        m.put('lamp_ornate', x, 52.6)
    # ---- residential blocks: houses along the concentric rings (skip roads, plaza, landmarks, river, wall)
    def road_near(x, y, pad=1):
        xi, yi = int(x), int(y)
        for yy in range(yi - pad, yi + pad + 1):
            for xx in range(xi - pad, xi + pad + 1):
                if 0 <= xx < m.gw and 0 <= yy < m.gh and m.grid[yy, xx] in 'sdwbx':
                    return True
        return False
    placed = []
    attempts = 0
    while len(placed) < 150 and attempts < 12000:
        attempts += 1
        r = m.rnd.uniform(9.0, RW - 3.4)
        ang = m.rnd.uniform(0, 360)
        x, y = pol(r, ang)
        if not (6 < x < 94 and 6 < y < 94):
            continue
        if 60 < y < 82 and 43 < x < 57:                            # dark alley
            continue
        # footprint (base of the house) must be clear of roads, water, walls and landmarks
        fx0, fx1, fy0, fy1 = int(x - 2), int(x + 3), int(y - 1), int(y + 2)
        if (m.grid[fy0:fy1, fx0:fx1] != 'g').any() or hm[int(y) - 1:int(y) + 2, int(x) - 2:int(x) + 3].any():
            continue
        if any(((x - a) / 4.0) ** 2 + ((y - b) / 2.8) ** 2 < 1.0 for a, b in placed):
            continue
        k = m.rnd.choice(['house_a', 'house_b', 'house_c', 'house_d', 'house_e', 'house_f', 'house_g', 'house_g', 'house_a', 'house_b'])
        m.put(k, x, y)
        placed.append((x, y))
        m.reserve(x - 2.0, y - 1.5, x + 2.0, y + 0.8)
        hres(x - 2.2, y - 1.0, x + 2.2, y + 0.8)
    for x, y, k in [(48.2, 63.6, 'barrel'), (51.8, 63.4, 'crate'), (46.6, 70, 'crate'), (53.6, 69.4, 'barrel'), (47.5, 79, 'crate'), (52.5, 78.6, 'barrel')]:
        m.put(k, x, y)
    # street dressing
    for a in range(0, 360, 20):
        for r in (13.5, 20.5):
            x, y = pol(r, a + 10)
            if m.grid[int(y), int(x)] == 's' and m.free(x, y, 0) is False and not road_near(x + 1.3, y, 0) is False:
                pass
    # ---- city greenery: avenue trees, plaza hedges and flower beds, topiary at the shops, willows along the river
    def ok(x, y, pad=0):
        return m.free(x, y, pad) and not hm[int(y) - 1:int(y) + 2, int(x) - 1:int(x) + 2].any()
    for i, y in enumerate(list(range(22, 44, 5)) + list(range(57, 63, 5))):
        for sx in (45.8, 54.2):
            if ok(sx, y):
                m.put('tree_birch' if (i + (sx > 50)) % 2 == 0 else 'tree_cherry', sx, y)
    for i, x in enumerate(list(range(23, 44, 5)) + list(range(58, 79, 5))):
        for sy in (46.0, 54.0):
            if ok(x, sy):
                m.put('tree_cherry' if (i + (sy > 50)) % 2 == 0 else 'tree_birch', x, sy)
    for a in range(0, 360, 30):
        if any(abs((a - g + 180) % 360 - 180) < 14 for g in (0, 90, 180, 270, 315, 45, 225)):
            continue
        x, y = pol(10.4, a)
        if ok(x, y):
            m.put('hedge', x, y)
    for a in range(15, 360, 45):
        x, y = pol(9.0, a)
        if ok(x, y):
            m.put('flower_bed', x, y)
    for kind, hw in [('tavern', 3.2), ('apothecary', 2.5), ('armory', 2.6), ('bakery', 2.4), ('library', 2.4), ('barracks', 3.6), ('smithy', 2.8)]:
        p = spot.get(kind)
        if p:
            for sx in (-hw - 0.9, hw + 0.9):
                if ok(p[0] + sx, p[1] + 0.8):
                    m.put('topiary', p[0] + sx, p[1] + 0.8)
    for (x0, y0), (x1, y1) in zip(river, river[1:]):
        for t in (0.25, 0.75):
            rx, ry = x0 + (x1 - x0) * t, y0 + (y1 - y0) * t
            for off in (-3.6, 3.6):
                if ok(rx + off, ry, 1) and math.hypot(rx - C[0], ry - C[1]) < RW - 2:
                    m.put('tree_willow', rx + off, ry + 0.6)
    m.scatter(['bush_flower', 'bush', 'flowers', 'tuft'], 120, (24, 24, 76, 76), pad=0, min_d=1.0)
    # ---- outside the walls: farmland, hamlets, forests
    m.rect(8, 8, 20, 14, 't')
    m.rect(8, 16, 20, 21, 't')
    m.rect(80, 8, 92, 13, 't')
    m.rect(72, 82, 90, 88, 't')
    m.rect(10, 80, 24, 86, 't')
    for x in range(8, 20):
        m.put('fence', x + 0.55, 7.5)
    for hx, hy, ks in [(84, 42, ['house_g', 'house_e']), (88, 60, ['house_f', 'house_g']), (14, 62, ['house_g', 'house_d']), (62, 90, ['house_e', 'house_g'])]:
        for i, k in enumerate(ks):
            m.put(k, hx + i * 5.6, hy + (i % 2) * 2.4)
            m.reserve(hx + i * 5.6 - 3, hy + (i % 2) * 2.4 - 5.4, hx + i * 5.6 + 3, hy + (i % 2) * 2.4 + 1)
    m.put('sign', 52.4, 10)
    m.put('sign', 95, 52.4)
    m.scatter(['tree_oak', 'tree_oak', 'tree_pine', 'tree_round'], 150, (0, 0, 100, 100), pad=1, min_d=2.7)
    m.scatter(['bush', 'bush_flower', 'rock_small', 'stump', 'rock_big'], 70, (0, 0, 100, 100), pad=0, min_d=1.5)
    m.scatter(['tuft', 'tuft', 'flowers'], 260, (0, 0, 100, 100), pad=0, min_d=0.8)
    m.player = (50 * T, 21.4 * T)
    def front(kind, dx=0.0, dy=1.9, default=(50, 50)):
        p = spot.get(kind) or default
        return (p[0] + dx) * T, (p[1] + dy) * T
    m.npcs = [
        dict(id='guildmaster', x=62 * T, y=40.6 * T, look='v_guildmaster', facing='down'),
        dict(id='guard', x=47.2 * T, y=22.4 * T, look='v_guard', facing='down'),
        dict(id='noble', x=60.2 * T, y=66.2 * T, look='v_noble', facing='left'),
        dict(id='cleric', x=38 * T, y=40.4 * T, look='v_cleric', facing='down'),
        dict(id='child', x=53.8 * T, y=52.2 * T, look='v_child', facing='left'),
        dict(id='shopkeeper', x=front('apothecary', 2.2)[0], y=front('apothecary', 2.2)[1], look='merchant', facing='left'),
        dict(id='tavern_keeper', x=front('tavern', -1.6)[0], y=front('tavern', -1.6)[1], look='villager', facing='down'),
        dict(id='smith_v', x=front('smithy', 1.6)[0], y=front('smithy', 1.6)[1], look='r_dwarf', facing='left'),
        dict(id='stable_master', x=front('stable', -2.0)[0], y=front('stable', -2.0)[1], look='x_veteran', facing='right'),
        dict(id='armorer', x=front('armory', 0)[0], y=front('armory', 0)[1], look='x_knight', facing='down'),
        dict(id='librarian', x=front('library', 0)[0], y=front('library', 0)[1], look='r_monk', facing='down'),
        dict(id='guard_captain', x=front('barracks', 2.2)[0], y=front('barracks', 2.2)[1], look='v_guard', facing='down'),
    ]
    for k, x, y, lv in [('imp_raider', 46, 75, 7), ('oni_executioner', 54, 76, 8), ('imp_howler', 49, 79, 7),
                        ('oni_lancer', 53, 79, 8), ('imp_bomber', 45.5, 78, 7)]:
        m.spawns.append(dict(kind=k, x=x * T, y=y * T, level=lv))
    m.spawns.append(dict(kind='assassin_shadow', x=50 * T, y=77.4 * T, level=9))
    # wilderness patrols outside the walls
    for k, x, y, lv in [('imp_raider', 40, 8, 7), ('oni_lancer', 70, 12, 8), ('imp_howler', 90, 30, 7), ('oni_executioner', 92, 74, 8),
                        ('imp_bomber', 70, 90, 7), ('oni_lancer', 40, 92, 8), ('imp_raider', 8, 70, 7), ('imp_howler', 8, 30, 7)]:
        m.spawns.append(dict(kind=k, x=x * T, y=y * T, level=lv))
    m.exits = [dict(to='velmoor', x=50 * T, y=0.5 * T, w=3 * T, h=T), dict(to='kharis', x=99.5 * T, y=50 * T, w=T, h=4 * T)]
    m._expanded = True      # authored at full size already
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
    which = [a for a in sys.argv[1:] if not a.startswith('--')] or ['village', 'velmoor', 'valemont', 'kharis', 'mines', 'mirewail', 'peaks', 'castle', 'wastelands', 'citadel']
    for n in which:
        globals()[n]().export()
