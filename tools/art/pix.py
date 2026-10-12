"""Index-map pixel renderer.

Shapes are drawn at SxS supersampling into an id map (uint8); the map is then reduced to 1x by
majority vote (crisp pixel art with sub-pixel motion), shaded by neighbour rules and outlined.
"""
from __future__ import annotations
import math
import colorsys
import numpy as np
from PIL import Image, ImageDraw

S = 4


def hex2rgb(h):
    h = h.lstrip('#')
    if len(h) == 3:
        h = ''.join(c * 2 for c in h)
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def ramp(base, n=5):
    """Hue-shifted ramp: index 0 darkest ... n-1 lightest."""
    r, g, b = [v / 255 for v in hex2rgb(base)]
    h, l, s = colorsys.rgb_to_hls(r, g, b)
    out = []
    mid = (n - 1) / 2
    for i in range(n):
        t = (i - mid) / mid
        nl = min(0.97, max(0.05, l + t * (0.26 if t < 0 else 0.24)))
        nh = (h + (0.03 if t < 0 else -0.022) * abs(t)) % 1
        ns = min(1, max(0, s * (1 - abs(t) * 0.08) + (0.05 if t < 0 else -0.06) * abs(t)))
        rr, gg, bb = colorsys.hls_to_rgb(nh, nl, ns)
        out.append((int(rr * 255), int(gg * 255), int(bb * 255)))
    return out


class Part:
    def __init__(self, name, base, rank=0, flat=False, rim=True):
        self.name = name
        self.ramp = ramp(base, 5)
        self.rank = rank
        self.flat = flat    # no automatic rim/shadow
        self.rim = rim


class Canvas:
    """Painter's-algorithm canvas of part ids at S x supersampling."""

    def __init__(self, w, h):
        self.w, self.h = w, h
        self.img = Image.new('L', (w * S, h * S), 0)
        self.d = ImageDraw.Draw(self.img)
        self.parts: dict[int, Part] = {}
        self._next = 1

    def part(self, p: Part) -> int:
        pid = self._next
        self._next += 1
        self.parts[pid] = p
        return pid

    # ---- primitives (coordinates in final pixels, floats allowed)
    def poly(self, pid, pts):
        self.d.polygon([(x * S, y * S) for x, y in pts], fill=pid)

    def ellipse(self, pid, cx, cy, rx, ry):
        self.d.ellipse([(cx - rx) * S, (cy - ry) * S, (cx + rx) * S - 1, (cy + ry) * S - 1], fill=pid)

    def rect(self, pid, x0, y0, x1, y1):
        self.d.rectangle([x0 * S, y0 * S, x1 * S - 1, y1 * S - 1], fill=pid)

    def line(self, pid, x0, y0, x1, y1, w):
        self.d.line([(x0 * S, y0 * S), (x1 * S, y1 * S)], fill=pid, width=max(1, int(w * S)))
        r = w * S / 2
        for x, y in ((x0, y0), (x1, y1)):
            self.d.ellipse([x * S - r, y * S - r, x * S + r - 1, y * S + r - 1], fill=pid)

    def capsule(self, pid, x0, y0, x1, y1, w0, w1=None):
        """Tapered limb between two joints."""
        w1 = w0 if w1 is None else w1
        dx, dy = x1 - x0, y1 - y0
        L = math.hypot(dx, dy) or 1e-6
        nx, ny = -dy / L, dx / L
        pts = [(x0 + nx * w0 / 2, y0 + ny * w0 / 2), (x1 + nx * w1 / 2, y1 + ny * w1 / 2),
               (x1 - nx * w1 / 2, y1 - ny * w1 / 2), (x0 - nx * w0 / 2, y0 - ny * w0 / 2)]
        self.poly(pid, pts)
        self.ellipse(pid, x0, y0, w0 / 2, w0 / 2)
        self.ellipse(pid, x1, y1, w1 / 2, w1 / 2)

    def blob(self, pid, pts):
        """Smooth closed shape through points (Catmull-Rom)."""
        out = []
        n = len(pts)
        for i in range(n):
            p0, p1, p2, p3 = pts[(i - 1) % n], pts[i], pts[(i + 1) % n], pts[(i + 2) % n]
            for t in np.linspace(0, 1, 8, endpoint=False):
                t2, t3 = t * t, t * t * t
                x = 0.5 * ((2 * p1[0]) + (-p0[0] + p2[0]) * t + (2 * p0[0] - 5 * p1[0] + 4 * p2[0] - p3[0]) * t2 + (-p0[0] + 3 * p1[0] - 3 * p2[0] + p3[0]) * t3)
                y = 0.5 * ((2 * p1[1]) + (-p0[1] + p2[1]) * t + (2 * p0[1] - 5 * p1[1] + 4 * p2[1] - p3[1]) * t2 + (-p0[1] + 3 * p1[1] - 3 * p2[1] + p3[1]) * t3)
                out.append((x, y))
        self.poly(pid, out)

    def clear_rect(self, x0, y0, x1, y1):
        self.d.rectangle([x0 * S, y0 * S, x1 * S - 1, y1 * S - 1], fill=0)

    # ---- reduction + shading
    def ids(self):
        a = np.asarray(self.img)
        h, w = self.h, self.w
        blocks = a.reshape(h, S, w, S).transpose(0, 2, 1, 3).reshape(h, w, S * S)
        best = np.zeros((h, w), dtype=np.uint8)
        bestc = np.zeros((h, w), dtype=np.int32)
        for pid in self.parts:
            c = (blocks == pid).sum(-1)
            # later parts win ties (they are painted on top)
            m = c >= bestc
            m &= c > 0
            best = np.where(m, pid, best)
            bestc = np.where(m, c, bestc)
        # coverage threshold: drop faint pixels
        cover = (blocks != 0).sum(-1)
        best = np.where(cover >= 6, best, 0)
        return best

    def render(self, outline=True, outline_dark=0.72, shade=True, extra=None):
        ids = self.ids()
        h, w = ids.shape
        rgba = np.zeros((h, w, 4), dtype=np.uint8)
        pad = np.pad(ids, 2)
        def sh(dy, dx):
            return pad[2 + dy:2 + dy + h, 2 + dx:2 + dx + w]
        up, left, upl = sh(-1, 0), sh(0, -1), sh(-1, -1)
        down, right, dnr = sh(1, 0), sh(0, 1), sh(1, 1)
        up2 = sh(-2, 0)
        rank_of = np.zeros(256, dtype=np.int32)
        for pid, p in self.parts.items():
            rank_of[pid] = p.rank
        rk = rank_of[ids]
        for pid, p in self.parts.items():
            m = ids == pid
            if not m.any():
                continue
            tone = np.full((h, w), 2, dtype=np.int32)
            if shade and not p.flat:
                lit = ((up != pid) | (left != pid) | (upl != pid)) if p.rim else np.zeros_like(m)
                dark = (down != pid) | (right != pid) | (dnr != pid)
                occl = (up != pid) & (up != 0) & (rank_of[up] > p.rank) | ((up2 != pid) & (up2 != 0) & (rank_of[up2] > p.rank) & (up == pid))
                tone = np.where(lit, 3, tone)
                tone = np.where(dark & ~lit, 1, tone)
                tone = np.where(occl, 1, tone)
                tone = np.where(lit & dark, 2, tone)
            for t in range(5):
                mm = m & (tone == t)
                if mm.any():
                    rgba[mm, :3] = p.ramp[t]
            rgba[m, 3] = 255
        if extra is not None:
            extra(rgba, ids)
        for pid, p in self.parts.items():
            if p.name == 'shadow':
                m = ids == pid
                rgba[m] = (10, 4, 24, 96)
        if outline:
            rgba = add_outline(rgba, outline_dark)
        return Image.fromarray(rgba, 'RGBA')


def add_outline(rgba, dark=0.72, color=None):
    h, w = rgba.shape[:2]
    a = rgba[..., 3] > 200
    pad = np.pad(rgba, ((1, 1), (1, 1), (0, 0)))
    pa = np.pad(a, 1)
    out = rgba.copy()
    a_any = rgba[..., 3] > 0
    best = np.zeros((h, w), dtype=bool)
    col = np.zeros((h, w, 3), dtype=np.float32)
    for dy, dx in ((1, 0), (0, 1), (0, -1), (-1, 0)):  # prefer pixel below / sides for colour
        nb = pa[1 + dy:1 + dy + h, 1 + dx:1 + dx + w]
        c = pad[1 + dy:1 + dy + h, 1 + dx:1 + dx + w, :3].astype(np.float32)
        take = nb & ~best
        col[take] = c[take]
        best |= nb
    edge = best & ~a_any
    base = np.array([20, 10, 36], dtype=np.float32)
    if color is not None:
        base = np.array(color, dtype=np.float32)
        res = np.broadcast_to(base, col.shape)
    else:
        res = col * (1 - dark) + base * dark
    out[edge, :3] = res[edge].astype(np.uint8)
    out[edge, 3] = 255
    return out
