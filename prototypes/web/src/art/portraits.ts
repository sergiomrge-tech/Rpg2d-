import { Ctx, mk, px, rect, ramp, mix, outline } from './pixel';
import type { Look } from './characters';

export type Emotion = 'neutral' | 'smile' | 'angry' | 'sad' | 'surprised' | 'smug';
const PW = 56;
const PH = 64;
const cache = new Map<string, HTMLCanvasElement>();

function inE(x: number, y: number, cx: number, cy: number, rx: number, ry: number) {
  const dx = (x - cx) / rx, dy = (y - cy) / ry;
  return dx * dx + dy * dy <= 1;
}

/** Procedural anime bust portrait (56x64). */
export function portrait(key: string, L: Look, emo: Emotion = 'neutral'): HTMLCanvasElement {
  const ck = `${key}:${emo}`;
  let c = cache.get(ck);
  if (c) return c;
  const [cv, ctx] = mk(PW, PH);
  const skin = ramp(L.skin, 5), hair = ramp(L.hair, 6), eye = ramp(L.eyes, 5), top = ramp(L.top, 4), trim = ramp(L.trim, 4);
  const cx = 28;
  const P = (x: number, y: number, col: string) => px(ctx, x, y, col);
  const style = L.hairStyle;

  // back hair (long / twin / bob)
  const longBack = style === 'long' || style === 'bob' || style === 'twin' || style === 'ponytail' || style === 'elder';
  if (longBack) {
    const bottom = style === 'long' ? 62 : style === 'bob' ? 46 : style === 'elder' ? 56 : 54;
    for (let y = 8; y < bottom; y++) for (let x = 4; x < 52; x++) {
      const w = style === 'twin' ? (y > 30 ? 25 : 21) : 21;
      if (inE(x + 0.5, y + 0.5, cx, 24, w, 17) || (y > 24 && y < bottom && Math.abs(x + 0.5 - cx) < (style === 'bob' ? 19 : 21))) {
        P(x, y, y > 40 ? hair[1] : y > 28 ? hair[2] : hair[3]);
      }
    }
    if (style === 'twin') for (const sx of [-1, 1]) for (let y = 26; y < 60; y++) for (let x = 0; x < 9; x++) {
      if (inE(x + 0.5, y + 0.5, 4.5, 43, 4.6, 17)) P(sx < 0 ? x : PW - 1 - x, y, y % 6 < 2 ? hair[4] : hair[2]);
    }
  }
  // torso
  for (let y = 48; y < PH; y++) for (let x = 6; x < 50; x++) {
    const sh = inE(x + 0.5, y + 0.5, cx, 72, 24, 25);
    if (sh) P(x, y, x < 22 ? top[3] : x > 36 ? top[1] : top[2]);
  }
  // neck
  rect(ctx, cx - 4, 42, 8, 8, skin[1]);
  rect(ctx, cx - 4, 42, 8, 3, skin[0]);
  // collar / trim
  for (let i = 0; i < 12; i++) { P(cx - 6 + i, 50 + Math.abs(i - 6) / 2 | 0, trim[3]); P(cx - 6 + i, 51 + Math.abs(i - 6) / 2 | 0, trim[2]); }
  if (L.scarf) { const s = ramp(L.scarf, 4); for (let x = 14; x < 42; x++) { rect(ctx, x, 46 + Math.round(Math.sin((x - 14) / 28 * Math.PI) * 4), 1, 5, (x % 6 < 3) ? s[2] : s[3]); } }
  if (L.armor) { for (let x = 6; x < 50; x++) { P(x, 54 + (Math.abs(x - cx) > 14 ? 2 : 0), trim[3]); } }

  // face
  for (let y = 14; y < 46; y++) for (let x = 10; x < 46; x++) {
    if (!inE(x + 0.5, y + 0.5, cx, 29, 15.5, 16.5)) continue;
    // chin taper
    if (y > 38 && Math.abs(x + 0.5 - cx) > 15 - (y - 38) * 1.5) continue;
    let col = skin[3];
    if (x < 15) col = skin[2];
    if (x > 40 || y > 42) col = skin[2];
    if (y > 44) col = skin[1];
    P(x, y, col);
  }
  // ears
  if (!L.ears) for (const sx of [10, 45]) { rect(ctx, sx - 1, 28, 3, 5, skin[2]); P(sx, 30, skin[1]); }

  // eyes
  const eyeW = 10, eyeH = 11;
  const ey = 27;
  const drawEye = (x0: number, mirror: boolean) => {
    const mx = (i: number) => (mirror ? x0 + eyeW - 1 - i : x0 + i);
    const e = emo;
    const h = e === 'surprised' ? eyeH + 2 : e === 'smug' ? eyeH - 3 : e === 'angry' ? eyeH - 2 : eyeH;
    // white
    for (let j = 0; j < h; j++) for (let i = 0; i < eyeW; i++) {
      const inside = inE(i + 0.5, j + 0.5, eyeW / 2, h / 2, eyeW / 2, h / 2 + 0.3);
      if (inside) P(mx(i), ey + j, '#f4f2ff');
    }
    // iris
    const ix = 2, iw = 6;
    for (let j = 1; j < h; j++) for (let i = 0; i < iw; i++) {
      if (!inE(i + 0.5, j + 0.5, iw / 2, h / 2 + 0.5, iw / 2, h / 2 - 0.2)) continue;
      const t = j / h;
      const col = t < 0.3 ? eye[0] : t < 0.55 ? eye[1] : t < 0.8 ? eye[2] : eye[3];
      P(mx(ix + i), ey + j, col);
    }
    // pupil
    rect(ctx, mirror ? x0 + eyeW - 1 - (ix + 4) : x0 + ix + 2, ey + Math.floor(h / 2) - 2, 2, 4, '#12081e');
    // highlights
    const hx = mirror ? x0 + eyeW - 1 - (ix + 1) : x0 + ix + 1;
    rect(ctx, hx, ey + 2, 2, 2, '#ffffff'); P(mirror ? hx - 2 : hx + 2, ey + h - 3, '#ffffffcc');
    // upper lash
    const top0 = e === 'smug' ? ey + 2 : ey;
    for (let i = -1; i < eyeW + 1; i++) { P(mirror ? x0 + eyeW - 1 - i : x0 + i, top0 - (i > 1 && i < eyeW - 2 ? 0 : 1) + (e === 'angry' ? (mirror ? (i * 0.25) | 0 : ((eyeW - i) * 0.25) | 0) : 0), hair[0]); }
    rect(ctx, mirror ? x0 - 1 : x0 + eyeW - 1, ey, 2, 1, hair[0]);
    // lower lid
    for (let i = 1; i < eyeW - 1; i++) P(mx(i), ey + h, skin[1]);
    if (e === 'sad') { P(mx(eyeW - 1), ey + h + 1, '#8ad0ff'); P(mx(eyeW - 1), ey + h + 2, '#cdeeff'); }
  };
  drawEye(16, false);
  drawEye(30, true);
  // brows
  const browY = emo === 'angry' ? 22 : emo === 'surprised' ? 18 : emo === 'sad' ? 22 : 21;
  for (let i = 0; i < 8; i++) {
    const a = emo === 'angry' ? i * 0.3 : emo === 'sad' ? -i * 0.2 + 1.5 : 0;
    P(16 + i, Math.round(browY + a - (emo === 'angry' ? 0 : 0)), hair[1]);
    P(39 - i, Math.round(browY + a), hair[1]);
  }
  // nose + blush
  P(cx, 37, skin[1]); P(cx, 38, skin[0]);
  const bl = mix(L.skin, '#ff5f8f', 0.5);
  for (const bx of [15, 35]) { rect(ctx, bx, 38, 5, 1, bl); rect(ctx, bx + 1, 39, 3, 1, bl); }
  // mouth
  const my = 42;
  const mc = mix(L.skin, '#6a1a2a', 0.7);
  if (emo === 'smile') { rect(ctx, cx - 3, my, 7, 1, mc); P(cx - 4, my - 1, mc); P(cx + 4, my - 1, mc); rect(ctx, cx - 2, my + 1, 5, 1, '#ff8aa0'); }
  else if (emo === 'surprised') { rect(ctx, cx - 1, my, 3, 3, mc); P(cx, my + 1, '#ff6a8a'); }
  else if (emo === 'angry') { rect(ctx, cx - 3, my, 7, 1, mc); P(cx - 4, my + 1, mc); P(cx + 4, my + 1, mc); }
  else if (emo === 'sad') { rect(ctx, cx - 2, my + 1, 5, 1, mc); P(cx - 3, my + 2, mc); P(cx + 3, my + 2, mc); }
  else if (emo === 'smug') { rect(ctx, cx - 2, my, 5, 1, mc); P(cx + 3, my - 1, mc); P(cx + 4, my - 2, mc); }
  else { rect(ctx, cx - 2, my, 4, 1, mc); }
  if (L.beard) { const b = ramp(L.beard, 4); for (let y = 38; y < 56; y++) for (let x = 14; x < 42; x++) if (inE(x + 0.5, y + 0.5, cx, 44, 13, 12) && !inE(x + 0.5, y + 0.5, cx, 38, 8, 5)) P(x, y, y > 48 ? b[1] : (x < 24 ? b[3] : b[2])); }

  // front hair (cap + bangs)
  const bangs = (x: number): number => {
    const t = (x - cx) / 15;
    switch (style) {
      case 'spiky': case 'messy': return 22 + Math.abs(Math.sin(t * 6)) * 5 + Math.abs(t) * 6;
      case 'long': case 'bob': case 'ponytail': case 'twin': return 18 + Math.abs(t) * 12 + (Math.abs(t) < 0.12 ? 4 : 0) + Math.abs(Math.sin(t * 5)) * 2;
      case 'elder': case 'short': return 19 + Math.abs(t) * 8 + Math.abs(Math.sin(t * 4)) * 3;
      default: return 0;
    }
  };
  if (style !== 'bald') {
    for (let y = 2; y < 40; y++) for (let x = 6; x < 50; x++) {
      const inCap = inE(x + 0.5, y + 0.5, cx, 26, 21.5, 24);
      const spikes = style === 'spiky' && y < 14 && inE(x + 0.5, y + 0.5, cx, 18, 24, 18) && ((x * 3 + y) % 7 < 5 || y > 8);
      if (!(inCap || spikes)) continue;
      const bl2 = bangs(x);
      const sideLen = style === 'long' ? 54 : style === 'bob' ? 44 : style === 'twin' ? 40 : 34;
      const onFace = x > 11 && x < 45 && y >= bl2;
      const onSide = (x <= 11 || x >= 45) && y < sideLen;
      if (y >= bl2 && !onSide && inE(x + 0.5, y + 0.5, cx, 29, 15.5, 16.5)) continue;
      if (y > 36 && !onSide) continue;
      if (y >= 34 && !onSide && !onFace) continue;
      let col = hair[3];
      const edge = y - bl2;
      if (y >= bl2 - 2 && y < bl2) col = hair[1];
      else if (y < 12 && x > 14 && x < 30 && (y + x) % 6 < 3) col = hair[4];
      else if (y > 10 && y < 14 && x > 12 && x < 44) col = hair[5];
      else if (x < 18) col = hair[4];
      else if (x > 38) col = hair[2];
      void edge;
      P(x, y, col);
    }
    // gloss streaks
    for (let i = 0; i < 12; i++) { P(18 + i, 9 + Math.round(Math.sin(i / 11 * Math.PI) * -2) + 3, hair[5]); }
    if (style === 'spiky') for (const [x, y] of [[20, 1], [24, 0], [32, 0], [38, 2], [16, 4], [42, 4], [28, 1], [12, 8], [46, 8]]) { rect(ctx, x, y, 4, 4, hair[3]); rect(ctx, x, y, 2, 2, hair[4]); }
  }
  // ears (beastkin)
  if (L.ears) { const e = ramp(L.ears, 4); for (const sx of [12, 44]) for (let j = 0; j < 14; j++) rect(ctx, sx - Math.round((14 - j) / 4) + (sx > 28 ? 0 : 0), 4 + j - 4, 6 - Math.round(j / 4), 1, j < 4 ? e[3] : e[2]); }
  // hat
  if (L.hat === 'wizard') {
    const h = ramp(L.hatColor ?? '#5a3aa0', 5);
    for (let x = 2; x < 54; x++) { rect(ctx, x, 14, 1, 4, h[2]); P(x, 14, h[3]); }
    for (let y = 0; y < 14; y++) { const w = 8 + y * 1.6; rect(ctx, Math.round(cx - w / 2), y, Math.round(w), 1, y % 5 === 0 ? h[3] : h[2]); }
    rect(ctx, 10, 11, 36, 2, '#f2c94c');
  } else if (L.hat === 'band') {
    const h = ramp(L.hatColor ?? '#f2c94c', 5);
    for (let x = 8; x < 48; x++) rect(ctx, x, 14 + Math.round(Math.abs(x - cx) / 10), 1, 3, h[3]);
    rect(ctx, cx - 2, 13, 5, 5, '#ff4a6a'); P(cx - 1, 14, '#fff');
  } else if (L.hat === 'hood') {
    const h = ramp(L.hatColor ?? '#2a2a40', 5);
    for (let y = 0; y < 50; y++) for (let x = 0; x < PW; x++) {
      if (inE(x + 0.5, y + 0.5, cx, 24, 26, 25) && !inE(x + 0.5, y + 0.5, cx, 30, 17, 18) && y < 50) P(x, y, y < 14 ? h[3] : x < cx ? h[2] : h[1]);
    }
  } else if (L.hat === 'straw') {
    const h = ramp('#e9c46a', 5);
    for (let x = 0; x < PW; x++) rect(ctx, x, 14, 1, 4, h[2]);
    for (let x = 12; x < 44; x++) rect(ctx, x, 6, 1, 8, h[3]);
    rect(ctx, 12, 12, 32, 2, L.hatColor ?? '#6a4a2a');
  }
  return outline(cv, undefined, 0.7) && (cache.set(ck, cv), cv);
}
