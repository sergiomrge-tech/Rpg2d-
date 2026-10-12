"""Offline scene composite (what the Unity scene should look like) for art review.
python3 compose_preview.py village cx cy out.png   (cx, cy in tiles = camera centre)"""
from __future__ import annotations
import json
import os
import sys
from PIL import Image
from sheet import OUT as SPR

MAPS = os.path.join(os.path.dirname(SPR), 'Maps')


def frame_of(sheet, meta, anim, i):
    m = next(a for a in meta['anims'] if a['name'] == anim)
    k = m['start'] + i % m['count']
    fw, fh, cols = meta['frameW'], meta['frameH'], meta['cols']
    return sheet.crop(((k % cols) * fw, (k // cols) * fh, (k % cols + 1) * fw, (k // cols + 1) * fh)), meta


def main(name, cx, cy, out, W=1920, H=1080):
    data = json.load(open(os.path.join(MAPS, name + '.json')))
    T, C = data['tile'], data['chunk']
    x0, y0 = int(cx * T - W / 2), int(cy * T - H / 2)
    img = Image.new('RGBA', (W, H))
    for j in range(data['chunksY']):
        for i in range(data['chunksX']):
            g = Image.open(os.path.join(MAPS, name, f'g_{i}_{j}.png')).convert('RGBA')
            img.alpha_composite(g, (i * C - x0, j * C - y0)) if -C < i * C - x0 < W and -C < j * C - y0 < H else None
    props = {p['name']: p for p in json.load(open(os.path.join(SPR, 'Env', 'props.json')))['props']}
    hero = Image.open(os.path.join(SPR, 'Chars', 'hero.png'))
    hmeta = json.load(open(os.path.join(SPR, 'Chars', 'hero.json')))
    imp = Image.open(os.path.join(SPR, 'Demons', 'imp.png'))
    imeta = json.load(open(os.path.join(SPR, 'Demons', 'imp.json')))
    items = []
    for p in data['props']:
        items.append((p['y'], 'prop', p))
    items.append((data['playerY'], 'hero', None))
    for s in data['spawns']:
        items.append((s['y'], 'imp', s))
    extra = [(cx * T + 220, cy * T + 60, 'imp', 'idle_side'), (cx * T - 260, cy * T + 120, 'imp', 'attack_down')]
    for x, y, k, an in extra:
        items.append((y, 'imp', dict(x=x, y=y, anim=an)))
    items.sort(key=lambda t: t[0])
    for y, kind, p in items:
        if kind == 'prop':
            pm = props[p['kind']]
            spr = Image.open(os.path.join(SPR, 'Env', p['kind'] + '.png'))
            px, py = p['x'] - pm['w'] / 2 - x0, p['y'] - (pm['h'] - pm['pivotY']) - y0
            # pivot: base point at (w/2? no -> pivotX) ; use pivotX
            px = p['x'] - pm['pivotX'] - x0
            if -600 < px < W + 100 and -600 < py < H + 100:
                img.alpha_composite(spr, (int(px), int(py)))
        elif kind == 'hero':
            fr, m = frame_of(hero, hmeta, 'idle_down', 0)
            img.alpha_composite(fr, (int(data['playerX'] - m['pivotX'] - x0), int(data['playerY'] - (m['frameH'] - m['pivotY']) - y0)))
        else:
            fr, m = frame_of(imp, imeta, p.get('anim', 'idle_down'), 3)
            px, py = int(p['x'] - m['pivotX'] - x0), int(p['y'] - (m['frameH'] - m['pivotY']) - y0)
            if -200 < px < W and -200 < py < H:
                img.alpha_composite(fr, (px, py))
    img.convert('RGB').save(out)


if __name__ == '__main__':
    main(sys.argv[1], float(sys.argv[2]), float(sys.argv[3]), sys.argv[4])
