"""Contact-sheet preview: python3 preview.py Chars/hero walk_side attack1_down ... -o out.png [-s 2]"""
from __future__ import annotations
import argparse
import json
import os
from PIL import Image
from sheet import OUT

ap = argparse.ArgumentParser()
ap.add_argument('sheet')
ap.add_argument('anims', nargs='+')
ap.add_argument('-o', required=True)
ap.add_argument('-s', type=float, default=2)
ap.add_argument('--bg', default='#7aa95c')
a = ap.parse_args()

img = Image.open(os.path.join(OUT, a.sheet + '.png'))
meta = json.load(open(os.path.join(OUT, a.sheet + '.json')))
fw, fh, cols = meta['frameW'], meta['frameH'], meta['cols']
by = {m['name']: m for m in meta['anims']}
sel = [by[n] for n in a.anims]
maxn = max(m['count'] for m in sel)
out = Image.new('RGBA', (maxn * fw, len(sel) * fh), a.bg)
for r, m in enumerate(sel):
    for i in range(m['count']):
        k = m['start'] + i
        fr = img.crop(((k % cols) * fw, (k // cols) * fh, (k % cols + 1) * fw, (k // cols + 1) * fh))
        out.alpha_composite(fr, (i * fw, r * fh))
out = out.resize((int(out.width * a.s), int(out.height * a.s)), Image.LANCZOS)
out.save(a.o)
