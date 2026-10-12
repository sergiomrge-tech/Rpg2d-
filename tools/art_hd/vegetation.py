"""Vegetation pass: clustered themed flora on every map + shoreline planting (runs inside Map.export, after the authored layout).
Uses Map.free() (plain ground, not reserved) so it never blocks roads, plazas, buildings or water."""
from __future__ import annotations
import math

T = 64

THEMES = {
    # name: (tree kinds+weights, tree density per 100 tiles, low kinds+weights, low density per 100 tiles)
    'village': ([('tree_birch', 3), ('tree_cherry', 2), ('tree_willow', 1), ('tree_oak', 2), ('tree_round', 2)], 1.1,
                [('berry_bush', 2), ('fern', 2), ('tall_grass', 4), ('flower_bed', 3), ('log', 1), ('bush_flower', 2)], 5.0),
    'velmoor': ([('tree_willow', 2), ('tree_birch', 1)], 0.9, [('glow_fern', 4), ('fern', 3), ('tall_grass', 2), ('log', 2)], 4.5),
    'valemont': ([('tree_birch', 3), ('tree_cherry', 3), ('tree_willow', 1), ('tree_oak', 2)], 1.0,
                 [('berry_bush', 2), ('fern', 2), ('tall_grass', 3), ('flower_bed', 3), ('bush_flower', 2)], 4.0),
    'kharis': ([('palm', 2)], 0.4, [('dry_shrub', 5), ('cactus', 2)], 3.5),
    'mines': ([], 0.0, [('glow_fern', 2), ('dry_shrub', 1)], 2.0),
    'mirewail': ([('tree_willow', 3), ('swamp_tree', 2)], 1.2, [('fern', 3), ('glow_fern', 4), ('reeds', 3), ('log', 2)], 5.0),
    'peaks': ([('snow_pine', 3)], 0.9, [('frost_shrub', 5)], 3.5),
    'castle': ([], 0.0, [('dry_shrub', 2), ('tall_grass', 2), ('fern', 1)], 2.0),
    'wastelands': ([], 0.0, [('dry_shrub', 4), ('log', 1)], 2.0),
    'citadel': ([], 0.0, [('dry_shrub', 2)], 1.0),
}
SHORE = {'village': ['reeds', 'fern', 'tall_grass'], 'velmoor': ['glow_fern', 'reeds', 'fern'], 'valemont': ['reeds', 'fern', 'tall_grass', 'flower_bed'],
         'mirewail': ['reeds', 'glow_fern', 'fern'], 'peaks': ['frost_shrub'], 'citadel': ['dry_shrub'], 'kharis': ['reeds', 'dry_shrub'],
         'mines': ['glow_fern'], 'castle': ['reeds'], 'wastelands': ['dry_shrub']}


def _pick(rnd, table):
    tot = sum(w for _, w in table)
    r = rnd.uniform(0, tot)
    for k, w in table:
        r -= w
        if r <= 0:
            return k
    return table[-1][0]


def _cluster(m, table, count, pad, radius, min_d):
    if not table or count <= 0:
        return 0
    rnd = m.rnd
    placed = []
    n_clusters = max(3, count // 9)
    centers = [(rnd.uniform(3, m.gw - 3), rnd.uniform(3, m.gh - 3)) for _ in range(n_clusters)]
    tries = 0
    while len(placed) < count and tries < count * 30:
        tries += 1
        cx, cy = rnd.choice(centers)
        a, d = rnd.uniform(0, math.tau), abs(rnd.gauss(0, radius))
        tx, ty = cx + math.cos(a) * d, cy + math.sin(a) * d
        if not (2 <= tx < m.gw - 2 and 2 <= ty < m.gh - 2) or not m.free(tx, ty, pad):
            continue
        if any((tx - px) ** 2 + (ty - py) ** 2 < min_d ** 2 for px, py in placed[-80:]):
            continue
        placed.append((tx, ty))
        m.put(_pick(rnd, table), tx, ty)
        m.reserve(tx - 0.4, ty - 0.4, tx + 0.4, ty + 0.4)
    return len(placed)


def shoreline(m, kinds, prob=0.16):
    rnd = m.rnd
    n = 0
    for y in range(1, m.gh - 1):
        for x in range(1, m.gw - 1):
            if m.grid[y, x] != 'g' or m.reserved[y, x]:
                continue
            near = any(m.grid[y + dy, x + dx] == 'w' for dx in (-1, 0, 1) for dy in (-1, 0, 1))
            if near and rnd.random() < prob:
                m.put(rnd.choice(kinds), x + rnd.uniform(0.2, 0.8), y + rnd.uniform(0.4, 0.9))
                n += 1
    return n


def add(m):
    th = THEMES.get(m.name)
    if th is None:
        return
    trees, tdens, low, ldens = th
    area = m.gw * m.gh / 100.0
    nt = _cluster(m, trees, int(tdens * area), 1, 6.5, 3.0)
    nl = _cluster(m, low, int(ldens * area), 0, 7.5, 1.1)
    ns = shoreline(m, SHORE.get(m.name, ['fern'])) if (m.grid == 'w').any() else 0
    print(f'  vegetation {m.name}: +{nt} trees, +{nl} low, +{ns} shore')
