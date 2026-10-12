import { Rng } from '../engine/util';

export type Ctx = CanvasRenderingContext2D;

export function mk(w: number, h: number): [HTMLCanvasElement, Ctx] {
  const c = document.createElement('canvas');
  c.width = w;
  c.height = h;
  const x = c.getContext('2d', { willReadFrequently: true })!;
  x.imageSmoothingEnabled = false;
  return [c, x];
}

export function hex2rgb(h: string): [number, number, number] {
  let s = h.replace('#', '');
  if (s.length === 3) s = s.split('').map((c) => c + c).join('');
  const n = parseInt(s, 16);
  return [(n >> 16) & 255, (n >> 8) & 255, n & 255];
}
export function rgb2hex(r: number, g: number, b: number): string {
  const f = (v: number) => Math.max(0, Math.min(255, Math.round(v))).toString(16).padStart(2, '0');
  return '#' + f(r) + f(g) + f(b);
}
export function mix(a: string, b: string, t: number): string {
  const A = hex2rgb(a);
  const B = hex2rgb(b);
  return rgb2hex(A[0] + (B[0] - A[0]) * t, A[1] + (B[1] - A[1]) * t, A[2] + (B[2] - A[2]) * t);
}

function rgb2hsl(r: number, g: number, b: number): [number, number, number] {
  r /= 255; g /= 255; b /= 255;
  const mx = Math.max(r, g, b), mn = Math.min(r, g, b);
  let h = 0, s = 0;
  const l = (mx + mn) / 2;
  if (mx !== mn) {
    const d = mx - mn;
    s = l > 0.5 ? d / (2 - mx - mn) : d / (mx + mn);
    if (mx === r) h = (g - b) / d + (g < b ? 6 : 0);
    else if (mx === g) h = (b - r) / d + 2;
    else h = (r - g) / d + 4;
    h /= 6;
  }
  return [h, s, l];
}
function hsl2rgb(h: number, s: number, l: number): [number, number, number] {
  if (s === 0) return [l * 255, l * 255, l * 255];
  const q = l < 0.5 ? l * (1 + s) : l + s - l * s;
  const p = 2 * l - q;
  const f = (t: number) => {
    if (t < 0) t += 1;
    if (t > 1) t -= 1;
    if (t < 1 / 6) return p + (q - p) * 6 * t;
    if (t < 1 / 2) return q;
    if (t < 2 / 3) return p + (q - p) * (2 / 3 - t) * 6;
    return p;
  };
  return [f(h + 1 / 3) * 255, f(h) * 255, f(h - 1 / 3) * 255];
}

/** Hue-shifted colour ramp: index 0 = darkest, n-1 = lightest. Shadows go cool, lights go warm. */
export function ramp(base: string, n = 5): string[] {
  const [r, g, b] = hex2rgb(base);
  const [h, s, l] = rgb2hsl(r, g, b);
  const out: string[] = [];
  const mid = (n - 1) / 2;
  for (let i = 0; i < n; i++) {
    const t = (i - mid) / mid; // -1..1
    const nl = Math.max(0.05, Math.min(0.96, l + t * (t < 0 ? 0.3 : 0.26)));
    const nh = (h + (t < 0 ? 0.035 : -0.025) * Math.abs(t) + 1) % 1;
    const ns = Math.max(0, Math.min(1, s * (1 - Math.abs(t) * 0.1) + (t < 0 ? 0.05 : -0.05) * Math.abs(t)));
    const [rr, gg, bb] = hsl2rgb(nh, ns, nl);
    out.push(rgb2hex(rr, gg, bb));
  }
  return out;
}

export function px(ctx: Ctx, x: number, y: number, c: string) {
  ctx.fillStyle = c;
  ctx.fillRect(x, y, 1, 1);
}
export function rect(ctx: Ctx, x: number, y: number, w: number, h: number, c: string) {
  ctx.fillStyle = c;
  ctx.fillRect(x, y, w, h);
}

/** Draw ASCII bitmap; `pal` maps characters to colours ('.' or ' ' transparent). */
export function bitmap(ctx: Ctx, x: number, y: number, rows: string[], pal: Record<string, string>) {
  for (let j = 0; j < rows.length; j++) {
    for (let i = 0; i < rows[j].length; i++) {
      const ch = rows[j][i];
      const col = pal[ch];
      if (col) px(ctx, x + i, y + j, col);
    }
  }
}

/** Filled ellipse (pixel-exact). */
export function ellipse(ctx: Ctx, cx: number, cy: number, rx: number, ry: number, c: string) {
  ctx.fillStyle = c;
  for (let y = -ry; y <= ry; y++) {
    const w = Math.round(rx * Math.sqrt(Math.max(0, 1 - (y * y) / (ry * ry + 0.0001))));
    ctx.fillRect(Math.round(cx - w), Math.round(cy + y), w * 2 + 1, 1);
  }
}

/** Toon-shaded ellipse using a ramp (light from upper-left) with optional ordered dithering between bands. */
export function shadedEllipse(
  ctx: Ctx, cx: number, cy: number, rx: number, ry: number, rp: string[],
  opts: { lx?: number; ly?: number; dither?: boolean; bands?: number } = {},
) {
  const lx = opts.lx ?? -0.45;
  const ly = opts.ly ?? -0.6;
  const bands = opts.bands ?? 4;
  const bayer = [[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]];
  for (let y = -ry; y <= ry; y++) {
    for (let x = -rx; x <= rx; x++) {
      const nx = x / (rx + 0.5);
      const ny = y / (ry + 0.5);
      const d = nx * nx + ny * ny;
      if (d > 1) continue;
      const nz = Math.sqrt(1 - d);
      let li = nx * lx + ny * ly + nz * 0.65; // -?..1
      li = (li + 0.2) / 1.2;
      let v = li * bands;
      if (opts.dither !== false) {
        const th = bayer[(y + 64) & 3][(x + 64) & 3] / 16 - 0.5;
        v += th * 0.7;
      }
      const idx = Math.max(0, Math.min(rp.length - 1, Math.round(v * ((rp.length - 1) / bands))));
      px(ctx, Math.round(cx + x), Math.round(cy + y), rp[idx]);
    }
  }
}

/** Adds a 1px outline around opaque pixels using a darkened version of the adjacent colour. */
export function outline(canvas: HTMLCanvasElement, color?: string, dark = 0.65): HTMLCanvasElement {
  const w = canvas.width, h = canvas.height;
  const ctx = canvas.getContext('2d', { willReadFrequently: true })!;
  const src = ctx.getImageData(0, 0, w, h);
  const out = ctx.createImageData(w, h);
  out.data.set(src.data);
  const fixed = color ? hex2rgb(color) : null;
  const A = (x: number, y: number) => (x < 0 || y < 0 || x >= w || y >= h ? 0 : src.data[(y * w + x) * 4 + 3]);
  for (let y = 0; y < h; y++) {
    for (let x = 0; x < w; x++) {
      const i = (y * w + x) * 4;
      if (src.data[i + 3] > 20) continue;
      let best = -1;
      for (const [dx, dy] of [[0, 1], [-1, 0], [1, 0], [0, -1]]) {
        if (A(x + dx, y + dy) > 200) {
          best = ((y + dy) * w + (x + dx)) * 4;
          if (dy === 1 || dy === 0) break;
        }
      }
      if (best < 0) continue;
      let r: number, g: number, b: number;
      if (fixed) [r, g, b] = fixed;
      else {
        r = src.data[best] * (1 - dark) + 18 * dark;
        g = src.data[best + 1] * (1 - dark) + 8 * dark;
        b = src.data[best + 2] * (1 - dark) + 32 * dark;
      }
      out.data[i] = r; out.data[i + 1] = g; out.data[i + 2] = b; out.data[i + 3] = 255;
    }
  }
  ctx.putImageData(out, 0, 0);
  return canvas;
}

export function flipX(src: HTMLCanvasElement): HTMLCanvasElement {
  const [c, x] = mk(src.width, src.height);
  x.translate(src.width, 0);
  x.scale(-1, 1);
  x.drawImage(src, 0, 0);
  return c;
}

/** Solid-colour silhouette (for hit flashes). */
export function silhouette(src: HTMLCanvasElement, color = '#ffffff'): HTMLCanvasElement {
  const [c, x] = mk(src.width, src.height);
  x.drawImage(src, 0, 0);
  x.globalCompositeOperation = 'source-in';
  x.fillStyle = color;
  x.fillRect(0, 0, c.width, c.height);
  return c;
}

export function copy(src: HTMLCanvasElement, dx = 0, dy = 0, w = src.width, h = src.height): HTMLCanvasElement {
  const [c, x] = mk(w, h);
  x.drawImage(src, dx, dy);
  return c;
}

/** Cheap value-noise helper for textures. */
export function noiseGrid(w: number, h: number, seed: number): number[][] {
  const r = new Rng(seed);
  const g: number[][] = [];
  for (let y = 0; y < h; y++) {
    g[y] = [];
    for (let x = 0; x < w; x++) g[y][x] = r.next();
  }
  return g;
}
