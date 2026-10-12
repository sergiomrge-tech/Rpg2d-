"""Builds the hero sheet (and NPC variants) for Unity."""
from __future__ import annotations
import sys
from humanoid import Look, draw_figure
from anims import ANIMS, pose
from sheet import build

FW, FH, OX, OY = 192, 176, 96, 150
VIEWS = ('down', 'up', 'side')


def draw(ctx, payload):
    look, anim, t, view = payload
    draw_figure(ctx, look, view, pose(anim, t, view))


def jobs_for(look, anims=ANIMS):
    jobs = []
    for an, (n, fps, loop, hit) in anims.items():
        for v in VIEWS:
            frames = [(look, an, (i / n) if loop else (i / (n - 1) if n > 1 else 0), v) for i in range(n)]
            jobs.append((f'{an}_{v}', frames, fps, loop, hit))
    return jobs


def build_hero():
    return build('hero', 'Chars', FW, FH, OX, OY, jobs_for(Look()), draw)


if __name__ == '__main__':
    build_hero()
