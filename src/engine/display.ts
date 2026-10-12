export const VW = 384;
export const VH = 216;

/**
 * Two-layer renderer:
 *  - `g`  : low-res (384x216) pixel buffer for the world, blitted with integer scaling
 *  - `ui` : screen-resolution context pre-scaled to virtual coordinates, used for HUD & text
 */
class Display {
  canvas!: HTMLCanvasElement;
  screen!: CanvasRenderingContext2D;
  buf!: HTMLCanvasElement;
  g!: CanvasRenderingContext2D;
  ui!: CanvasRenderingContext2D;
  scale = 1;
  ox = 0;
  oy = 0;
  shakeX = 0;
  shakeY = 0;

  init(root: HTMLElement) {
    this.canvas = document.createElement('canvas');
    root.appendChild(this.canvas);
    this.screen = this.canvas.getContext('2d', { alpha: false })!;
    this.ui = this.screen;
    this.buf = document.createElement('canvas');
    this.buf.width = VW;
    this.buf.height = VH;
    this.g = this.buf.getContext('2d', { alpha: false })!;
    this.g.imageSmoothingEnabled = false;
    this.resize();
    window.addEventListener('resize', () => this.resize());
  }

  resize() {
    const dpr = window.devicePixelRatio || 1;
    const W = Math.floor(window.innerWidth * dpr);
    const H = Math.floor(window.innerHeight * dpr);
    this.canvas.width = W;
    this.canvas.height = H;
    this.canvas.style.width = window.innerWidth + 'px';
    this.canvas.style.height = window.innerHeight + 'px';
    const fit = Math.min(W / VW, H / VH);
    this.scale = fit >= 2 ? Math.floor(fit) : Math.max(fit, 0.5);
    this.ox = Math.floor((W - VW * this.scale) / 2);
    this.oy = Math.floor((H - VH * this.scale) / 2);
  }

  /** Begin UI pass: virtual coords, clipped to the game rectangle. */
  beginFrame() {
    const s = this.screen;
    s.setTransform(1, 0, 0, 1, 0, 0);
    s.imageSmoothingEnabled = false;
    s.fillStyle = '#000';
    s.fillRect(0, 0, this.canvas.width, this.canvas.height);
  }

  blitWorld() {
    const s = this.screen;
    s.setTransform(1, 0, 0, 1, 0, 0);
    s.imageSmoothingEnabled = false;
    s.drawImage(
      this.buf,
      this.ox + Math.round(this.shakeX * this.scale),
      this.oy + Math.round(this.shakeY * this.scale),
      VW * this.scale,
      VH * this.scale,
    );
  }

  beginUI() {
    const s = this.screen;
    s.setTransform(this.scale, 0, 0, this.scale, this.ox, this.oy);
    s.save();
    s.beginPath();
    s.rect(0, 0, VW, VH);
    s.clip();
  }
  endUI() {
    this.screen.restore();
  }
}

export const Disp = new Display();

export const FONT = '"Pixelify Sans", "Press Start 2P", monospace';

export interface TextOpts {
  size?: number;
  color?: string;
  shadow?: string | null;
  align?: CanvasTextAlign;
  bold?: boolean;
  alpha?: number;
}

export function text(ctx: CanvasRenderingContext2D, str: string, x: number, y: number, o: TextOpts = {}) {
  const size = o.size ?? 8;
  ctx.font = `${o.bold ? '700 ' : ''}${size}px ${FONT}`;
  ctx.textBaseline = 'top';
  ctx.textAlign = o.align ?? 'left';
  const prev = ctx.globalAlpha;
  if (o.alpha !== undefined) ctx.globalAlpha = prev * o.alpha;
  const sh = o.shadow === undefined ? '#120a1e' : o.shadow;
  if (sh) {
    ctx.fillStyle = sh;
    ctx.fillText(str, x + 1, y + 1);
    ctx.fillText(str, x, y + 1);
    ctx.fillText(str, x + 1, y);
  }
  ctx.fillStyle = o.color ?? '#fff';
  ctx.fillText(str, x, y);
  ctx.globalAlpha = prev;
}

export function measure(ctx: CanvasRenderingContext2D, str: string, size = 8): number {
  ctx.font = `${size}px ${FONT}`;
  return ctx.measureText(str).width;
}

export function wrap(ctx: CanvasRenderingContext2D, str: string, maxW: number, size = 8): string[] {
  ctx.font = `${size}px ${FONT}`;
  const out: string[] = [];
  for (const para of str.split('\n')) {
    let line = '';
    for (const word of para.split(' ')) {
      const test = line ? line + ' ' + word : word;
      if (ctx.measureText(test).width > maxW && line) {
        out.push(line);
        line = word;
      } else line = test;
    }
    out.push(line);
  }
  return out;
}

/** Pixel-art framed panel in virtual coordinates. */
export function panel(
  ctx: CanvasRenderingContext2D,
  x: number,
  y: number,
  w: number,
  h: number,
  o: { fill?: string; border?: string; accent?: string; alpha?: number } = {},
) {
  const fill = o.fill ?? '#150d26';
  const border = o.border ?? '#e8c872';
  const accent = o.accent ?? '#7a5a2a';
  const prev = ctx.globalAlpha;
  ctx.globalAlpha = prev * (o.alpha ?? 0.94);
  ctx.fillStyle = fill;
  ctx.fillRect(x + 1, y + 1, w - 2, h - 2);
  ctx.globalAlpha = prev;
  ctx.fillStyle = '#05020c';
  ctx.fillRect(x, y + 1, 1, h - 2);
  ctx.fillRect(x + w - 1, y + 1, 1, h - 2);
  ctx.fillRect(x + 1, y, w - 2, 1);
  ctx.fillRect(x + 1, y + h - 1, w - 2, 1);
  ctx.fillStyle = accent;
  ctx.fillRect(x + 1, y + 1, w - 2, 1);
  ctx.fillRect(x + 1, y + h - 2, w - 2, 1);
  ctx.fillRect(x + 1, y + 1, 1, h - 2);
  ctx.fillRect(x + w - 2, y + 1, 1, h - 2);
  ctx.fillStyle = border;
  ctx.fillRect(x + 2, y + 2, w - 4, 1);
  ctx.fillRect(x + 2, y + h - 3, w - 4, 1);
  ctx.fillRect(x + 2, y + 2, 1, h - 4);
  ctx.fillRect(x + w - 3, y + 2, 1, h - 4);
  // corner studs
  ctx.fillStyle = '#fff4c8';
  for (const [cx, cy] of [[2, 2], [w - 3, 2], [2, h - 3], [w - 3, h - 3]]) ctx.fillRect(x + cx, y + cy, 1, 1);
}

export function bar(
  ctx: CanvasRenderingContext2D,
  x: number,
  y: number,
  w: number,
  h: number,
  frac: number,
  c1: string,
  c2: string,
  bg = '#1a0f26',
) {
  ctx.fillStyle = '#05020c';
  ctx.fillRect(x - 1, y - 1, w + 2, h + 2);
  ctx.fillStyle = bg;
  ctx.fillRect(x, y, w, h);
  const fw = Math.max(0, Math.round(w * Math.min(1, Math.max(0, frac))));
  if (fw > 0) {
    ctx.fillStyle = c1;
    ctx.fillRect(x, y, fw, h);
    ctx.fillStyle = c2;
    ctx.fillRect(x, y, fw, Math.max(1, Math.floor(h / 2)));
    ctx.fillStyle = 'rgba(255,255,255,.35)';
    ctx.fillRect(x, y, fw, 1);
  }
}
