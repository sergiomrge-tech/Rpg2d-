"""Map expansion: wraps an authored Map in a ring of new land (~2x area).

The authored centre is kept exactly as designed (shifted by the margin); roads and rivers are extended to the new outer
edges so exits still sit on the border; the ring is filled with the same props/enemy density as the original,
plus points of interest (camps, stone circles, ruins, groves) with elite packs and treasure caches.
"""
from __future__ import annotations
import math
import numpy as np

T = 64
EXIT_PROPS = ('portal', 'hell_gate')


def _outer(v, size, margin, edge=4.0):
    """Coordinate near an old edge goes to the new outer edge; everything else shifts inward by the margin."""
    if v < edge:
        return v
    if v > size - edge:
        return v + 2 * margin
    return v + margin


def expand(m, mx, my):
    og, oreserved = m.grid, m.reserved
    oh, ow = og.shape
    nh, nw = oh + 2 * my, ow + 2 * mx
    old_shapes = m.shapes
    m.gw, m.gh = nw, nh
    m.grid = np.full((nh, nw), 'g', dtype='<U1')
    m.reserved = np.zeros((nh, nw), bool)
    m.reserved[my:my + oh, mx:mx + ow] = oreserved
    m.shapes = []

    def ext(p):
        x, y = p
        nx = -1.0 if x <= 0.5 else (nw + 1.0 if x >= ow - 0.5 else x + mx)
        ny = -1.0 if y <= 0.5 else (nh + 1.0 if y >= oh - 0.5 else y + my)
        return (nx, ny)

    # repaint the vector shapes (terrain) in the larger grid, extending edge-touching roads/rivers outward
    for kind, code, d in old_shapes:
        if kind == 'rect':
            x0, y0, x1, y1 = d
            m.rect(x0 + mx, y0 + my, x1 + mx, y1 + my, code)
        elif kind == 'disk':
            cx, cy, r = d
            m.disk(cx + mx, cy + my, r, code)
        else:
            pts, width = d
            pts2 = [ext(p) for p in pts]
            if code == 'w':
                m.river(pts2, width)
            else:
                m.path(pts2, width, code)
    # bridges were painted straight on the grid: carry them over
    ys, xs = np.where(og == 'b')
    for y, x in zip(ys, xs):
        m.grid[y + my, x + mx] = 'b'

    # props / actors / exits
    for p in m.props:
        tx, ty = p['x'] / T, p['y'] / T
        if p['kind'] in EXIT_PROPS:
            p['x'], p['y'] = round(_outer(tx, ow, mx) * T, 1), round(_outer(ty, oh, my) * T, 1)
        else:
            p['x'], p['y'] = round((tx + mx) * T, 1), round((ty + my) * T, 1)
    for lst in (m.spawns, m.npcs):
        for a in lst:
            a['x'] = (a['x'] / T + mx) * T
            a['y'] = (a['y'] / T + my) * T
    for e in m.exits:
        e['x'] = _outer(e['x'] / T, ow, mx, 1.5) * T
        e['y'] = _outer(e['y'] / T, oh, my, 1.5) * T
    px, py = m.player
    m.player = (_outer(px / T, ow, mx, 6) * T, _outer(py / T, oh, my, 6) * T)
    m.inner = (mx, my, ow, oh)
    m._expanded = True
    _fill_ring(m, mx, my, ow, oh)
    _points_of_interest(m, mx, my, ow, oh)
    _ring_spawns(m, mx, my, ow, oh, [dict(a) for a in m.spawns])


def _in_ring(tx, ty, mx, my, ow, oh):
    return not (mx <= tx < mx + ow and my <= ty < my + oh)


def _fill_ring(m, mx, my, ow, oh):
    """Replay every authored scatter over the ring, using the density of the nearest authored tile."""
    nw, nh = m.gw, m.gh
    for kinds, count, (x0, y0, x1, y1), pad, min_d in getattr(m, 'scatter_log', []):
        area = max(1.0, (x1 - x0) * (y1 - y0))
        dens = count / area

        def covered(tx, ty):
            ox = min(max(tx - mx, 0), ow - 1)
            oy = min(max(ty - my, 0), oh - 1)
            return x0 <= ox < x1 and y0 <= oy < y1
        cells = [(x, y) for y in range(nh) for x in range(nw) if _in_ring(x, y, mx, my, ow, oh) and covered(x, y)]
        n = int(dens * len(cells))
        placed = []
        tries = 0
        while len(placed) < n and tries < n * 40 and cells:
            tries += 1
            cx, cy = m.rnd.choice(cells)
            tx, ty = cx + m.rnd.random(), cy + m.rnd.random()
            if not m.free(tx, ty, pad):
                continue
            if any((tx - a) ** 2 + (ty - b) ** 2 < min_d ** 2 for a, b in placed[-60:]):
                continue
            placed.append((tx, ty))
            m.put(m.rnd.choice(kinds), tx, ty)
            if pad:
                m.reserve(tx - 0.5, ty - 0.5, tx + 0.5, ty + 0.5)


def _free_spot(m, mx, my, ow, oh, radius, avoid, min_avoid, tries=3000):
    for _ in range(tries):
        tx = m.rnd.uniform(radius + 2, m.gw - radius - 2)
        ty = m.rnd.uniform(radius + 2, m.gh - radius - 2)
        if not _in_ring(int(tx), int(ty), mx, my, ow, oh):
            continue
        if not all(m.free(tx + dx, ty + dy, 1) for dx, dy in ((0, 0), (radius, 0), (-radius, 0), (0, radius), (0, -radius))):
            continue
        if any(math.hypot(tx - a, ty - b) < min_avoid for a, b in avoid):
            continue
        return tx, ty
    return None


def _points_of_interest(m, mx, my, ow, oh):
    """Camps, stone circles, ruins and groves scattered through the ring, linked by dirt trails."""
    ring_area = m.gw * m.gh - ow * oh
    n_poi = max(5, int(ring_area / 520))
    pois = []
    avoid = [(m.player[0] / T, m.player[1] / T)] + [(e['x'] / T, e['y'] / T) for e in m.exits] + list(getattr(m, 'safe_points', []))
    types = ['camp', 'circle', 'ruins', 'grove', 'camp', 'ruins']
    caches = []
    for i in range(n_poi):
        kind = types[i % len(types)]
        spot = _free_spot(m, mx, my, ow, oh, 3.2, avoid + [(a, b) for a, b, _ in pois], 14.0)
        if spot is None:
            continue
        x, y = spot
        pois.append((x, y, kind))
        m.reserve(x - 4, y - 4, x + 4, y + 4)
        if kind == 'camp':
            for dx, dy, k in [(-1.6, 0.4, 'barrel'), (-0.9, 0.9, 'crate'), (1.4, 0.5, 'crate'), (0.0, -0.4, 'stump'), (1.0, -1.3, 'sign')]:
                m.put(k, x + dx, y + dy)
            m.put('torch_post', x - 2.3, y - 0.8)
            m.put('torch_post', x + 2.3, y - 0.8)
        elif kind == 'circle':
            for a in range(0, 360, 60):
                m.put('rock_big', x + math.cos(math.radians(a)) * 2.6, y + math.sin(math.radians(a)) * 2.2)
            m.put('brazier', x, y + 0.3)
        elif kind == 'ruins':
            for dx, dy in [(-2.4, -1.2), (2.4, -1.2), (-2.4, 1.8), (2.4, 1.8)]:
                m.put('ruin_pillar', x + dx, y + dy)
            m.put('ruin_arch', x, y - 2.2)
            m.put('skull_pile', x + 0.8, y + 1.2)
        else:   # grove
            for a in range(0, 360, 45):
                m.put(m.rnd.choice(['tree_oak', 'tree_pine', 'tree_round', 'tree_twisted']), x + math.cos(math.radians(a)) * 3.0,
                      y + math.sin(math.radians(a)) * 2.6)
            m.put('mushrooms', x, y + 0.4)
            m.put('flowers', x + 0.9, y + 0.6)
        caches.append(dict(id=f'{m.name}_{i}', x=round(x * T), y=round((y + 0.2) * T), tier=1 + i % 3))
    # dirt trails: Prim-style tree. Each point of interest links to the nearest already-connected point or road cell.
    road_cells = [(x + 0.5, y + 0.5) for y, x in zip(*np.where(np.isin(m.grid, list('ds'))))][::7]
    connected = list(road_cells)
    remaining = [(x, y) for x, y, _ in pois]
    while remaining and connected:
        best = None
        for (x, y) in remaining:
            for (cx, cy) in connected:
                d = math.hypot(x - cx, y - cy)
                if best is None or d < best[0]:
                    best = (d, (x, y), (cx, cy))
        _, (x, y), (cx, cy) = best
        remaining.remove((x, y))
        bend = (((x + cx) / 2) + m.rnd.uniform(-2.5, 2.5), ((y + 1.8 + cy) / 2) + m.rnd.uniform(-2.5, 2.5))
        m.path([(x, y + 1.8), bend, (cx, cy)], 1.6, 'd')
        connected.append((x, y + 1.8))
    m.pois = pois
    m.caches = caches


def _ring_spawns(m, mx, my, ow, oh, old_spawns):
    regular = [s for s in old_spawns if s['kind'] not in ('grakk',) and not _is_boss(s['kind'])]
    if not regular:
        return
    kinds = sorted({s['kind'] for s in regular})
    lvls = [s['level'] for s in regular]
    lo, hi = min(lvls), max(lvls)
    ring_area = m.gw * m.gh - ow * oh
    dens = max(0.0034, len(regular) / float(ow * oh))
    n = int(dens * ring_area)
    avoid = [(m.player[0] / T, m.player[1] / T)] + [(e['x'] / T, e['y'] / T) for e in m.exits] + [(n_['x'] / T, n_['y'] / T) for n_ in m.npcs]
    avoid += list(getattr(m, 'safe_points', []))      # e.g. the new-game start: no monsters within 12 tiles
    taken = [(s['x'] / T, s['y'] / T) for s in m.spawns]
    placed = 0
    tries = 0
    while placed < n and tries < n * 60:
        tries += 1
        tx, ty = m.rnd.uniform(3, m.gw - 3), m.rnd.uniform(3, m.gh - 3)
        if not _in_ring(int(tx), int(ty), mx, my, ow, oh) or not m.free(tx, ty, 1):
            continue
        if any(math.hypot(tx - a, ty - b) < 12 for a, b in avoid) or any(math.hypot(tx - a, ty - b) < 5 for a, b in taken):
            continue
        taken.append((tx, ty))
        m.spawns.append(dict(kind=m.rnd.choice(kinds), x=tx * T, y=ty * T, level=min(hi + 1, m.rnd.randint(lo, hi + 1))))
        placed += 1
    # camps hold an elite pack
    for x, y, kind in getattr(m, 'pois', []):
        if kind == 'camp':
            for k in range(3):
                m.spawns.append(dict(kind=m.rnd.choice(kinds), x=(x + m.rnd.uniform(-2.5, 2.5)) * T, y=(y + 2.4 + m.rnd.uniform(-0.8, 1)) * T, level=hi + 1))


def _is_boss(kind):
    import json, os
    try:
        d = json.load(open(os.path.join(os.path.dirname(__file__), '..', '..', 'godot', 'data', 'demons.json')))
        return bool(d[kind]['boss'])
    except Exception:
        return False
