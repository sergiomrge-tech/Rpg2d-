"""Lineup preview: python3 lineup.py out.png name1 name2 ... (Demons/<name>)"""
import json, os, sys
from PIL import Image, ImageDraw
from sheet import OUT
out, names = sys.argv[1], sys.argv[2:]
cells = [('idle_down', 2), ('move_up', 2), ('attack_side', 5), ('cast_down', 6)]
W, H = 170, 170
img = Image.new('RGBA', (W * len(cells) + 140, H * len(names)), '#7aa95c')
d = ImageDraw.Draw(img)
for r, n in enumerate(names):
    sh = Image.open(os.path.join(OUT, 'Demons', n + '.png'))
    m = json.load(open(os.path.join(OUT, 'Demons', n + '.json')))
    by = {a['name']: a for a in m['anims']}
    d.text((6, r * H + 70), n, fill='black')
    for c, (an, fi) in enumerate(cells):
        a = by[an]; k = a['start'] + min(fi, a['count'] - 1)
        fw, fh, cols = m['frameW'], m['frameH'], m['cols']
        fr = sh.crop(((k % cols) * fw, (k // cols) * fh, (k % cols + 1) * fw, (k // cols + 1) * fh))
        s = min(W / fw, H / fh)
        fr = fr.resize((int(fw * s), int(fh * s)), Image.LANCZOS)
        img.alpha_composite(fr, (140 + c * W, r * H))
img.save(out)
