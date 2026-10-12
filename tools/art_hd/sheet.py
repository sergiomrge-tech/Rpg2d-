"""Sprite-sheet packer shared by all HD characters.

Output (for Unity, loaded through Resources):  <name>.png + <name>.json
JSON (JsonUtility-friendly):
{ "frameW":..,"frameH":..,"pivotX":..,"pivotY":..(from bottom),"cols":..,
  "anims":[{"name":"walk_down","start":0,"count":10,"fps":13,"loop":true,"hit":-1}, ...] }
"""
from __future__ import annotations
import json
import math
import os
from concurrent.futures import ProcessPoolExecutor
from PIL import Image
from core import Frame, outline_rgba, to_image, hx

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
OUT = os.path.join(ROOT, 'godot', 'assets', 'Sprites')
OUTLINE = hx('#22131b')


def render_one(args):
    draw_fn, fw, fh, ox, oy, payload, outline = args
    f = Frame(fw, fh, ox, oy)
    draw_fn(f.ctx, payload)
    img = f.rgba()
    if outline:
        img = outline_rgba(img, OUTLINE, outline)
    return to_image(img)


def build(name, sub, fw, fh, ox, oy, jobs, draw_fn, outline=1.0, max_w=4096):
    """jobs: list of (anim_name, frames(list of payloads), fps, loop, hit)."""
    flat = []
    meta = []
    for an, payloads, fps, loop, hit in jobs:
        meta.append(dict(name=an, start=len(flat), count=len(payloads), fps=fps, loop=loop, hit=hit))
        flat.extend(payloads)
    cols = max(1, min(len(flat), max_w // fw))
    rows = math.ceil(len(flat) / cols)
    with ProcessPoolExecutor() as ex:
        imgs = list(ex.map(render_one, [(draw_fn, fw, fh, ox, oy, p, outline) for p in flat], chunksize=4))
    sheet = Image.new('RGBA', (cols * fw, rows * fh), (0, 0, 0, 0))
    for i, im in enumerate(imgs):
        sheet.paste(im, ((i % cols) * fw, (i // cols) * fh))
    d = os.path.join(OUT, sub)
    os.makedirs(d, exist_ok=True)
    sheet.save(os.path.join(d, name + '.png'), optimize=True)
    data = dict(frameW=fw, frameH=fh, pivotX=ox, pivotY=fh - oy, cols=cols, anims=meta)
    with open(os.path.join(d, name + '.json'), 'w') as fp:
        json.dump(data, fp, indent=1)
    print(f'{sub}/{name}: {len(flat)} frames, sheet {sheet.size}')
    return sheet, data, imgs
