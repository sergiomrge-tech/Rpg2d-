"""Builds demon sprite sheets: python3 build_demons.py [name ...]"""
from __future__ import annotations
import sys
from demons import DEMONS
from sheet import build

VIEWS = ('down', 'up', 'side')
_BY = {d.name: d for d in DEMONS}


def draw(ctx, payload):
    name, anim, t, view = payload
    d = _BY[name]
    d.draw(ctx, view, d.pose(anim, t, view))


def build_demon(d):
    jobs = []
    for an, (n, fps, loop, hit) in d.ANIMS.items():
        for v in VIEWS:
            frames = [(d.name, an, (i / n) if loop else i / (n - 1), v) for i in range(n)]
            jobs.append((f'{an}_{v}', frames, fps, loop, hit))
    return build(d.name, 'Demons', d.FW, d.FH, d.OX, d.OY, jobs, draw)


if __name__ == '__main__':
    names = sys.argv[1:] or list(_BY)
    for n in names:
        build_demon(_BY[n])
