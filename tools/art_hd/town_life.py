"""Ambient walkers: patrol routes through the streets of a town (stored in the map JSON as 'walkers')."""
from __future__ import annotations
import math

T = 64
LOOKS = ['villager', 'merchant', 'v_child', 'v_noble', 'v_cleric', 'r_nomad', 'x_veteran', 'guild_clerk', 'v_guard', 'villager', 'merchant']


def _walkable(m, x, y):
    xi, yi = int(x), int(y)
    return 0 <= xi < m.gw and 0 <= yi < m.gh and m.grid[yi, xi] in 'sdgb' and not m.reserved[yi, xi] or (0 <= xi < m.gw and 0 <= yi < m.gh and m.grid[yi, xi] in 'sd')


def _segment_ok(m, a, b):
    n = int(math.hypot(b[0] - a[0], b[1] - a[1]) * 2) + 1
    for i in range(n + 1):
        t = i / n
        x, y = a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t
        xi, yi = int(x), int(y)
        if not (0 <= xi < m.gw and 0 <= yi < m.gh) or m.grid[yi, xi] in 'wx':
            return False
    return True


def add_walkers(m, count, radius=15.0):
    rnd = m.rnd
    roads = [(x + 0.5, y + 0.5) for y in range(m.gh) for x in range(m.gw) if m.grid[y, x] in 'sd']
    if not roads:
        return
    walkers = []
    tries = 0
    while len(walkers) < count and tries < count * 200:
        tries += 1
        a = rnd.choice(roads)
        pts = [a]
        for _ in range(rnd.randint(2, 3)):
            cand = [r for r in rnd.sample(roads, min(len(roads), 60)) if 5 < math.hypot(r[0] - pts[-1][0], r[1] - pts[-1][1]) < radius
                    and _segment_ok(m, pts[-1], r)]
            if not cand:
                break
            pts.append(rnd.choice(cand))
        if len(pts) < 2:
            continue
        walkers.append(dict(look=rnd.choice(LOOKS), route=[[round(x * T), round(y * T)] for x, y in pts]))
    m.walkers = walkers
