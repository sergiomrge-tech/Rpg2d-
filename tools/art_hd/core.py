"""HD cartoon renderer (cairo vector paths + cel shading + silhouette outline).

Style target: soft, clean "storybook cartoon" 2D (thick coloured outline, flat base colour,
a crisp shadow crescent away from the light, a thin highlight crescent toward the light).
Everything is drawn at S x supersampling and reduced with a box/lanczos filter.
"""
from __future__ import annotations
import math
import colorsys
import cairo
import numpy as np
from PIL import Image
from scipy import ndimage

S = 2                      # supersampling factor
LIGHT = (-0.55, -0.83)     # light comes from upper-left (screen space, y down)


# ---------------------------------------------------------------- colours
def hx(h, a=1.0):
    h = h.lstrip('#')
    return (int(h[0:2], 16) / 255, int(h[2:4], 16) / 255, int(h[4:6], 16) / 255, a)


def shade(c, dl=-0.12, ds=0.06, dh=0.0):
    """Shift lightness/saturation/hue of an rgba tuple (hue shift toward purple in shadow)."""
    r, g, b, a = c
    h, l, s = colorsys.rgb_to_hls(r, g, b)
    if dl < 0 and dh == 0.0:
        dh = 0.02   # shadows drift slightly toward violet
    h = (h + dh) % 1.0
    l = min(1, max(0, l + dl))
    s = min(1, max(0, s + ds))
    r, g, b = colorsys.hls_to_rgb(h, l, s)
    return (r, g, b, a)


def mix(c1, c2, t):
    return tuple(c1[i] * (1 - t) + c2[i] * t for i in range(4))


class Pal:
    """A material: base + derived shadow / deep / light / line colours."""

    def __init__(self, base, shadow=None, light=None, line=None):
        self.base = hx(base) if isinstance(base, str) else base
        self.shadow = hx(shadow) if isinstance(shadow, str) else (shadow or shade(self.base, -0.13, 0.08))
        self.deep = shade(self.shadow, -0.10, 0.04)
        self.light = hx(light) if isinstance(light, str) else (light or shade(self.base, 0.12, -0.04, -0.01))
        self.line = hx(line) if isinstance(line, str) else (line or shade(self.base, -0.42, 0.0, 0.03))


# ---------------------------------------------------------------- canvas
class Frame:
    def __init__(self, w, h, ox, oy):
        self.w, self.h = w, h
        self.surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, w * S, h * S)
        self.ctx = cairo.Context(self.surf)
        self.ctx.scale(S, S)
        self.ctx.translate(ox, oy)
        self.ctx.set_line_join(cairo.LINE_JOIN_ROUND)
        self.ctx.set_line_cap(cairo.LINE_CAP_ROUND)

    def rgba(self) -> np.ndarray:
        """Unpremultiplied float RGBA at supersampled size."""
        self.surf.flush()
        buf = np.ndarray((self.h * S, self.w * S, 4), np.uint8, self.surf.get_data()).astype(np.float32) / 255
        b, g, r, a = buf[..., 0], buf[..., 1], buf[..., 2], buf[..., 3]
        out = np.zeros_like(buf)
        safe = np.maximum(a, 1e-6)
        out[..., 0], out[..., 1], out[..., 2], out[..., 3] = r / safe, g / safe, b / safe, a
        out[..., :3] = np.clip(out[..., :3], 0, 1)
        return out


def outline_rgba(img: np.ndarray, color, width: float) -> np.ndarray:
    """Add a silhouette outline (behind) of `width` final pixels."""
    a = img[..., 3]
    rad = max(1, int(round(width * S)))
    yy, xx = np.mgrid[-rad:rad + 1, -rad:rad + 1]
    disk = (xx * xx + yy * yy) <= rad * rad + 0.5
    grown = ndimage.grey_dilation(a, footprint=disk)
    out = np.zeros_like(img)
    out[..., 0], out[..., 1], out[..., 2] = color[0], color[1], color[2]
    out[..., 3] = grown * color[3]
    # composite img over outline
    fa = img[..., 3:4]
    res = np.empty_like(img)
    res[..., 3] = fa[..., 0] + out[..., 3] * (1 - fa[..., 0])
    safe = np.maximum(res[..., 3:4], 1e-6)
    res[..., :3] = (img[..., :3] * fa + out[..., :3] * out[..., 3:4] * (1 - fa)) / safe
    return res


def to_image(img: np.ndarray, final=True) -> Image.Image:
    """Float RGBA (supersampled) -> PIL image at final resolution (premultiplied resample)."""
    pm = img.copy()
    pm[..., :3] *= pm[..., 3:4]
    h, w = pm.shape[:2]
    if final and S > 1:
        pm = pm.reshape(h // S, S, w // S, S, 4).mean(axis=(1, 3))
    a = pm[..., 3:4]
    rgb = pm[..., :3] / np.maximum(a, 1e-6)
    out = np.concatenate([rgb, a], axis=-1)
    return Image.fromarray((np.clip(out, 0, 1) * 255 + 0.5).astype(np.uint8), 'RGBA')


# ---------------------------------------------------------------- path helpers
def rot(x, y, deg):
    r = math.radians(deg)
    c, s = math.cos(r), math.sin(r)
    return x * c - y * s, x * s + y * c


def smooth_poly(ctx, pts, closed=True, tension=0.5):
    """Catmull-Rom through points -> cubic beziers."""
    n = len(pts)
    if n < 3:
        ctx.move_to(*pts[0])
        for p in pts[1:]:
            ctx.line_to(*p)
        if closed:
            ctx.close_path()
        return
    ctx.move_to(*pts[0])
    rng = range(n) if closed else range(n - 1)
    for i in rng:
        p0 = pts[(i - 1) % n] if (closed or i > 0) else pts[i]
        p1 = pts[i]
        p2 = pts[(i + 1) % n]
        p3 = pts[(i + 2) % n] if (closed or i + 2 < n) else p2
        t = tension / 3 * 2
        c1 = (p1[0] + (p2[0] - p0[0]) * t / 2, p1[1] + (p2[1] - p0[1]) * t / 2)
        c2 = (p2[0] - (p3[0] - p1[0]) * t / 2, p2[1] - (p3[1] - p1[1]) * t / 2)
        ctx.curve_to(*c1, *c2, *p2)
    if closed:
        ctx.close_path()


def ellipse(ctx, cx, cy, rx, ry, ang=0.0):
    ctx.save()
    ctx.translate(cx, cy)
    if ang:
        ctx.rotate(math.radians(ang))
    ctx.scale(max(rx, 0.01), max(ry, 0.01))
    ctx.new_sub_path()
    ctx.arc(0, 0, 1, 0, 2 * math.pi)
    ctx.restore()


def capsule(ctx, a, b, r1, r2=None):
    """Tapered capsule from point a (radius r1) to point b (radius r2)."""
    r2 = r1 if r2 is None else r2
    dx, dy = b[0] - a[0], b[1] - a[1]
    d = math.hypot(dx, dy)
    if d < 1e-4:
        ellipse(ctx, a[0], a[1], max(r1, r2), max(r1, r2))
        return
    ang = math.atan2(dy, dx)
    # tangent offset for tapered capsule
    k = (r1 - r2) / d
    k = max(-0.99, min(0.99, k))
    off = math.acos(k)
    ctx.new_sub_path()
    ctx.arc(a[0], a[1], r1, ang + off, ang - off + 2 * math.pi)
    ctx.arc(b[0], b[1], r2, ang - off, ang + off)
    ctx.close_path()


class Shape:
    """A closure that emits a path; can be translated for crescent shading."""

    def __init__(self, fn):
        self.fn = fn

    def __call__(self, ctx, dx=0.0, dy=0.0):
        if dx or dy:
            ctx.save()
            ctx.translate(dx, dy)
            self.fn(ctx)
            ctx.restore()
        else:
            self.fn(ctx)


def paint(ctx, shape, pal: Pal, sh=2.2, hl=1.2, line=1.0, grad=True, hl_alpha=0.75, sh_alpha=1.0,
          light=LIGHT, deep=0.0, under=True):
    """Fill a shape with cel shading. sh/hl are crescent thicknesses in px (0 disables).
    under=True strokes the outline *before* filling so unions of sub-paths keep only the outer edge."""
    if callable(shape) and not isinstance(shape, Shape):
        shape = Shape(shape)
    lx, ly = light
    if line > 0 and under:
        ctx.save()
        ctx.new_path()
        shape(ctx)
        ctx.set_source_rgba(*pal.line)
        ctx.set_line_width(line * 2)
        ctx.stroke()
        ctx.restore()
    ctx.save()
    ctx.new_path()
    shape(ctx)
    ctx.clip()
    # base: soft vertical gradient top lighter -> bottom slightly darker
    x1, y1, x2, y2 = ctx.clip_extents()
    if grad:
        g = cairo.LinearGradient(0, y1, 0, y2)
        g.add_color_stop_rgba(0, *mix(pal.base, pal.light, 0.25))
        g.add_color_stop_rgba(1, *mix(pal.base, pal.shadow, 0.2))
        ctx.set_source(g)
    else:
        ctx.set_source_rgba(*pal.base)
    ctx.paint()
    if sh > 0:
        # shadow crescent = M \ (M shifted toward light)
        ctx.push_group()
        ctx.set_source_rgba(*pal.shadow)
        ctx.paint()
        ctx.set_operator(cairo.OPERATOR_CLEAR)
        ctx.new_path()
        shape(ctx, lx * sh, ly * sh)
        ctx.fill()
        ctx.pop_group_to_source()
        ctx.paint_with_alpha(sh_alpha)
        if deep > 0:
            ctx.push_group()
            ctx.set_source_rgba(*pal.deep)
            ctx.paint()
            ctx.set_operator(cairo.OPERATOR_CLEAR)
            ctx.new_path()
            shape(ctx, lx * deep, ly * deep)
            ctx.fill()
            ctx.pop_group_to_source()
            ctx.paint_with_alpha(0.8)
    if hl > 0:
        ctx.push_group()
        ctx.set_source_rgba(*pal.light)
        ctx.paint()
        ctx.set_operator(cairo.OPERATOR_CLEAR)
        ctx.new_path()
        shape(ctx, -lx * hl, -ly * hl)
        ctx.fill()
        ctx.pop_group_to_source()
        ctx.paint_with_alpha(hl_alpha)
    ctx.restore()
    if line > 0 and not under:
        ctx.save()
        ctx.new_path()
        shape(ctx)
        ctx.set_source_rgba(*pal.line)
        ctx.set_line_width(line)
        ctx.stroke()
        ctx.restore()


def flat(ctx, shape, color, alpha=1.0):
    ctx.save()
    ctx.new_path()
    shape(ctx) if not isinstance(shape, Shape) else shape(ctx)
    ctx.set_source_rgba(color[0], color[1], color[2], color[3] * alpha)
    ctx.fill()
    ctx.restore()


def stroke(ctx, fn, color, w, alpha=1.0):
    ctx.save()
    ctx.new_path()
    fn(ctx)
    ctx.set_source_rgba(color[0], color[1], color[2], color[3] * alpha)
    ctx.set_line_width(w)
    ctx.stroke()
    ctx.restore()


def radial_glow(ctx, x, y, r, color, a0=0.8):
    g = cairo.RadialGradient(x, y, 0, x, y, r)
    g.add_color_stop_rgba(0, color[0], color[1], color[2], a0)
    g.add_color_stop_rgba(1, color[0], color[1], color[2], 0)
    ctx.save()
    ctx.set_source(g)
    ctx.arc(x, y, r, 0, 2 * math.pi)
    ctx.fill()
    ctx.restore()


def lerp(a, b, t):
    return a + (b - a) * t


def ease_in_out(t):
    return t * t * (3 - 2 * t)


def ease_out(t):
    return 1 - (1 - t) ** 3


def ease_in(t):
    return t ** 3


def keys(t, kf, ease=ease_in_out):
    """Piecewise interpolation over [(t0, v0), (t1, v1), ...] (values may be tuples)."""
    if t <= kf[0][0]:
        return kf[0][1]
    for (t0, v0), (t1, v1) in zip(kf, kf[1:]):
        if t <= t1:
            u = ease((t - t0) / max(t1 - t0, 1e-6))
            if isinstance(v0, tuple):
                return tuple(lerp(a, b, u) for a, b in zip(v0, v1))
            return lerp(v0, v1, u)
    return kf[-1][1]
