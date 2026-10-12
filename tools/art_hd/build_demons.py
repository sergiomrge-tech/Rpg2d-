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


# --- humanoid demons reuse the hero animation set under enemy anim names
from oni import oni_look
from build_hero import draw as hero_draw, FW as HFW, FH as HFH, OX as HOX, OY as HOY
from anims import ANIMS as HANIMS

HUMANOID = {'oni': oni_look()}
REMAP = [('idle', 'idle'), ('move', 'walk'), ('attack', 'attack3'), ('cast', 'attack1'), ('hurt', 'hurt'), ('death', 'death')]


def build_humanoid(name, look):
    jobs = []
    for enemy_name, src in REMAP:
        n, fps, loop, hit = HANIMS[src]
        if enemy_name == 'move':
            fps = 10
        for v in VIEWS:
            frames = [(look, src, (i / n) if loop else i / (n - 1), v) for i in range(n)]
            jobs.append((f'{enemy_name}_{v}', frames, fps * (0.8 if enemy_name == 'attack' else 1), loop, hit))
    return build(name, 'Demons', HFW, HFH, HOX, HOY, jobs, hero_draw)


if __name__ == '__main__':
    import sys as _s
    for n, L in HUMANOID.items():
        if len(_s.argv) == 1 or n in _s.argv[1:]:
            build_humanoid(n, L)
    names = [n for n in (sys.argv[1:] or list(_BY)) if n in _BY]
    for n in names:
        build_demon(_BY[n])
