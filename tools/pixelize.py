"""Pixel-art style converter for character sprite sheets.

python3 tools/pixelize.py <sheet.png> <out.png> [factor=4] [colors=28]

Every frame is shrunk by `factor`, the colours are reduced to one shared palette per sheet, a 1px dark outline is added and the
frame is scaled back up with nearest-neighbour, so the result drops into the game in place of the HD sheet (same frame size).
"""
import json
import os
import sys
import numpy as np
from PIL import Image

OUTLINE = (26, 16, 24)


def pixelize(src, fw, fh, factor=4, colors=28):
    im = Image.open(src).convert('RGBA')
    W, H = im.size
    cols, rows = W // fw, H // fh
    tw, th = round(fw / factor), round(fh / factor)
    small = Image.new('RGBA', (cols * tw, rows * th))
    for r in range(rows):
        for c in range(cols):
            fr = im.crop((c * fw, r * fh, (c + 1) * fw, (r + 1) * fh))
            # premultiplied box filter keeps edges clean
            a = np.asarray(fr, np.float32) / 255
            pm = a[..., :3] * a[..., 3:4]
            t = Image.fromarray((np.dstack([pm, a[..., 3]]) * 255).astype(np.uint8)).resize((tw, th), Image.BOX)
            b = np.asarray(t, np.float32) / 255
            alpha = b[..., 3]
            rgb = np.where(alpha[..., None] > 0.01, b[..., :3] / np.maximum(alpha[..., None], 1e-3), 0)
            out = np.dstack([np.clip(rgb, 0, 1), (alpha > 0.45).astype(np.float32)])
            small.paste(Image.fromarray((out * 255).astype(np.uint8)), (c * tw, r * th))
    # shared palette (median cut) over the opaque pixels, mild contrast/saturation lift for the pixel look
    arr = np.asarray(small, np.uint8).copy()
    mask = arr[..., 3] > 0
    rgb = arr[..., :3].astype(np.float32) / 255
    g = rgb.mean(-1, keepdims=True)
    rgb = np.clip(g + (rgb - g) * 1.18, 0, 1)
    rgb = np.clip((rgb - 0.5) * 1.12 + 0.5, 0, 1)
    flat = (rgb[mask] * 255).astype(np.uint8)
    pal_img = Image.fromarray(flat.reshape(-1, 1, 3)).quantize(colors=colors, method=Image.MEDIANCUT, dither=Image.NONE)
    pal = np.array(pal_img.getpalette()[:colors * 3], np.uint8).reshape(-1, 3)
    idx = np.asarray(pal_img).reshape(-1)
    arr[mask, :3] = pal[idx]
    # 1px outline per frame (never crossing frame borders)
    res = arr.copy()
    for r in range(rows):
        for c in range(cols):
            y0, x0 = r * th, c * tw
            fa = arr[y0:y0 + th, x0:x0 + tw, 3] > 0
            grown = np.zeros_like(fa)
            grown[1:, :] |= fa[:-1, :]
            grown[:-1, :] |= fa[1:, :]
            grown[:, 1:] |= fa[:, :-1]
            grown[:, :-1] |= fa[:, 1:]
            edge = grown & ~fa
            sub = res[y0:y0 + th, x0:x0 + tw]
            sub[edge] = (*OUTLINE, 255)
    out = Image.fromarray(res).resize((cols * fw, rows * fh), Image.NEAREST)
    return out


if __name__ == '__main__':
    src, dst = sys.argv[1], sys.argv[2]
    f = int(sys.argv[3]) if len(sys.argv) > 3 else 4
    n = int(sys.argv[4]) if len(sys.argv) > 4 else 28
    meta = json.load(open(os.path.splitext(src)[0] + '.json'))
    pixelize(src, meta['frameW'], meta['frameH'], f, n).save(dst, optimize=True)
    print('wrote', dst)
