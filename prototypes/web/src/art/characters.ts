import { Ctx, mk, px, rect, ramp, mix, outline, flipX, silhouette } from './pixel';
import type { Dir } from '../engine/util';

export const CW = 24;
export const CH = 34;
export const FOOT_X = 12;
export const FOOT_Y = 31;
const OY = 4;

export interface Look {
  skin: string;
  hair: string;
  hairStyle: 'spiky' | 'short' | 'long' | 'bob' | 'twin' | 'ponytail' | 'bald' | 'elder' | 'messy';
  eyes: string;
  top: string;
  trim: string;
  pants: string;
  boots: string;
  scarf?: string;
  cape?: string;
  hat?: 'wizard' | 'cap' | 'band' | 'straw' | 'hood' | 'crown';
  hatColor?: string;
  beard?: string;
  fem?: boolean;
  ears?: string;
  tail?: string;
  armor?: boolean;
  big?: boolean;
}

interface Pose {
  uo: number; // upper body offset
  liftL: number;
  liftR: number;
  arms: 'down' | 'swing' | 'up' | 'fwd' | 'back';
  swing: number; // -1..1 arm swing
  eyes?: 'open' | 'closed' | 'hurt';
  mouth?: 'neutral' | 'open' | 'smile';
}

type Sheet = {
  frame: (anim: string, dir: Dir, i: number) => HTMLCanvasElement;
  flash: (anim: string, dir: Dir, i: number) => HTMLCanvasElement;
  count: (anim: string) => number;
};

const POSES: Record<string, Pose[]> = {
  idle: [
    { uo: 0, liftL: 0, liftR: 0, arms: 'down', swing: 0 },
    { uo: 1, liftL: 0, liftR: 0, arms: 'down', swing: 0 },
  ],
  walk: [
    { uo: 0, liftL: 0, liftR: 0, arms: 'swing', swing: 0 },
    { uo: 0, liftL: 2, liftR: 0, arms: 'swing', swing: 1 },
    { uo: 0, liftL: 0, liftR: 0, arms: 'swing', swing: 0 },
    { uo: 0, liftL: 0, liftR: 2, arms: 'swing', swing: -1 },
  ],
  attack: [
    { uo: 0, liftL: 0, liftR: 0, arms: 'back', swing: 0, mouth: 'neutral' },
    { uo: 1, liftL: 0, liftR: 0, arms: 'fwd', swing: 0, mouth: 'open' },
    { uo: 0, liftL: 0, liftR: 0, arms: 'fwd', swing: 0 },
  ],
  cast: [
    { uo: 0, liftL: 0, liftR: 0, arms: 'up', swing: 0, mouth: 'open' },
    { uo: 1, liftL: 0, liftR: 0, arms: 'up', swing: 1, mouth: 'open' },
  ],
  hurt: [{ uo: 1, liftL: 0, liftR: 0, arms: 'up', swing: 0, eyes: 'hurt', mouth: 'open' }],
  smile: [{ uo: 0, liftL: 0, liftR: 0, arms: 'down', swing: 0, mouth: 'smile' }],
};

function inEllipse(x: number, y: number, cx: number, cy: number, rx: number, ry: number) {
  const dx = (x - cx) / rx;
  const dy = (y - cy) / ry;
  return dx * dx + dy * dy <= 1;
}

const BANGS: Record<string, number[]> = {
  spiky: [10, 9, 8, 8, 9, 9, 8, 8, 9, 10],
  messy: [10, 9, 9, 8, 9, 8, 9, 8, 9, 10],
  short: [9, 8, 8, 9, 9, 9, 9, 8, 8, 9],
  long: [11, 10, 9, 8, 8, 8, 8, 9, 10, 11],
  bob: [11, 10, 9, 9, 9, 9, 9, 9, 10, 11],
  twin: [10, 9, 8, 8, 9, 9, 8, 8, 9, 10],
  ponytail: [10, 9, 8, 8, 9, 9, 8, 8, 9, 10],
  elder: [9, 8, 8, 8, 8, 8, 8, 8, 8, 9],
  bald: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
};
const SIDE_LEN: Record<string, number> = { spiky: 11, messy: 12, short: 10, long: 19, bob: 13, twin: 12, ponytail: 11, elder: 12, bald: 0 };

function drawHead(ctx: Ctx, L: Look, dir: 'down' | 'up' | 'left', pose: Pose) {
  const o = pose.uo + OY;
  const skin = ramp(L.skin, 4);
  const hair = ramp(L.hair, 5);
  const eye = ramp(L.eyes, 4);
  const P = (x: number, y: number, c: string) => px(ctx, x, y + o, c);
  const style = L.hairStyle;
  const bang = BANGS[style];
  const bald = style === 'bald';

  // tail & ears behind head
  if (L.ears && dir !== 'up') {
    const e = ramp(L.ears, 4);
    for (const sx of dir === 'left' ? [14] : [7, 16]) {
      P(sx, 0, e[2]); P(sx, 1, e[2]); P(sx + (sx < 12 ? 1 : -1), 1, e[1]); P(sx, 2, e[1]); P(sx + (sx < 12 ? 0 : 0), -1, e[3]);
      P(sx + (sx < 12 ? 1 : 0), 2, e[3]);
    }
  } else if (L.ears) {
    const e = ramp(L.ears, 4);
    for (const sx of [7, 16]) { P(sx, 0, e[2]); P(sx, 1, e[2]); P(sx, -1, e[3]); P(sx, 2, e[1]); }
  }

  const hairPix = (x: number, y: number): boolean => {
    if (bald) return false;
    if (dir === 'down') {
      if (inEllipse(x + 0.5, y + 0.5, 12, 7.2, 7, 6.4)) return true;
      const sl = SIDE_LEN[style];
      if ((x === 5 || x === 6 || x === 17 || x === 18) && y >= 5 && y < sl && inEllipse(x + 0.5, y + 0.5, 12, 9, 7.4, 8)) return true;
      if (style === 'twin' && (x <= 4 || x >= 19) && y >= 6 && y <= 18) return x >= 3 && x <= 5 || x >= 18 && x <= 20 ? true : false;
      return false;
    }
    if (dir === 'up') return inEllipse(x + 0.5, y + 0.5, 12, 8.2, 7, 7) || (y >= 6 && y < SIDE_LEN[style] + 1 && x >= 5 && x <= 18 && inEllipse(x + 0.5, y + 0.5, 12, 9, 7.2, 8));
    return inEllipse(x + 0.5, y + 0.5, 12.5, 7.4, 6.8, 6.4) || (y >= 6 && y < SIDE_LEN[style] && x >= 11 && x <= 17 && inEllipse(x + 0.5, y + 0.5, 14, 9, 4.2, 8));
  };

  const facePix = (x: number, y: number): boolean => {
    if (dir === 'down') return inEllipse(x + 0.5, y + 0.5, 12, 9.8, 5.2, 5.5) && y >= (bald ? 5 : (bang[Math.min(9, Math.max(0, x - 7))] ?? 9));
    if (dir === 'left') return inEllipse(x + 0.5, y + 0.5, 9.8, 9.9, 4.6, 5.5) && y >= (bald ? 5 : (style === 'spiky' || style === 'messy' ? 8 : 8)) && !(x >= 8 && y < (bald ? 5 : 7));
    return false;
  };

  // skull base (for bald/back)
  if (dir === 'up' && bald) for (let y = 3; y < 14; y++) for (let x = 5; x < 19; x++) if (inEllipse(x + 0.5, y + 0.5, 12, 8.4, 6.5, 6)) P(x, y, skin[2]);

  // hair first (back layer)
  const drawHair = () => {
    for (let y = -1; y < 22; y++) {
      for (let x = 2; x < 22; x++) {
        if (!hairPix(x, y)) continue;
        if (dir !== 'up' && facePix(x, y)) continue;
        let c = hair[2];
        const rel = y - 2;
        if (rel <= 2 && x > 6 && x < 18 && (dir !== 'left' || x < 15)) c = hair[3];
        if (rel === 2 && x >= 8 && x <= 15 && ((x - 8) % 4) < 3) c = hair[4];
        if (rel === 3 && (x === 9 || x === 14)) c = hair[3];
        if (dir === 'down' && y >= 5 && (x <= 6 || x >= 17) ) c = hair[1];
        if (dir === 'down' && y > 6 && y >= bang[Math.min(9, Math.max(0, x - 7))] - 1 && x >= 7 && x <= 16) c = hair[1];
        if (dir === 'up' && y >= 9) c = hair[1];
        if (dir === 'up' && y >= 12) c = hair[0];
        if (dir === 'left' && x >= 14 && y > 7) c = hair[1];
        if (dir === 'left' && y >= 12) c = hair[0];
        P(x, y, c);
      }
    }
    // spikes / extras
    if (style === 'spiky') {
      const sp: [number, number][] = [[8, 1], [8, 0], [9, 0], [12, 0], [12, -1], [13, 0], [15, 1], [16, 1], [16, 0], [10, 1], [11, 1], [5, 3], [18, 3]];
      if (dir === 'down' || dir === 'up') for (const [x, y] of sp) P(x, y, y <= 0 ? hair[3] : hair[2]);
      else for (const [x, y] of [[9, 0], [10, 0], [13, 0], [13, -1], [16, 1], [17, 2], [18, 3], [19, 4]]) P(x, y, hair[2]);
    }
    if (style === 'messy') {
      for (const [x, y] of [[8, 1], [9, 0], [14, 0], [15, 1], [11, 0], [18, 4], [5, 4], [19, 8]]) P(x, y, hair[2]);
    }
    if (style === 'ponytail') {
      const pts: [number, number][] = dir === 'down' ? [[19, 5], [20, 6], [20, 7], [20, 8], [19, 9], [19, 10]] :
        dir === 'up' ? [[12, 13], [12, 14], [12, 15], [11, 16], [12, 17], [12, 18], [11, 19]] : [[18, 6], [19, 7], [19, 8], [19, 9], [18, 10], [18, 11], [17, 12]];
      pts.forEach(([x, y], i) => P(x, y, hair[i % 2 ? 1 : 2]));
      P(dir === 'down' ? 19 : dir === 'up' ? 12 : 18, dir === 'down' ? 4 : dir === 'up' ? 12 : 5, '#e8506a');
    }
    if (style === 'twin' && dir !== 'up') {
      const pts: number[][] = dir === 'down' ? [[4, 6], [3, 7], [3, 8], [3, 9], [3, 10], [4, 11], [3, 12], [4, 13], [3, 14], [20, 6], [20, 7], [20, 8], [20, 9], [20, 10], [19, 11], [20, 12], [19, 13], [20, 14]] : [[17, 7], [18, 8], [19, 9], [19, 10], [18, 11], [19, 12], [18, 13], [18, 14], [17, 15]];
      pts.forEach(([x, y], i) => P(x, y, hair[i % 3 === 0 ? 3 : 2]));
      if (dir === 'down') { P(4, 5, '#ff6f91'); P(19, 5, '#ff6f91'); P(5, 6, '#ff6f91'); P(18, 6, '#ff6f91'); }
    }
    if (style === 'elder' || style === 'bob' || style === 'long') {
      // bangs highlight gloss
      if (dir === 'down') { P(9, 5, hair[4]); P(10, 4, hair[4]); P(14, 4, hair[4]); }
    }
  };

  if (dir === 'up') drawHair();

  // face
  if (dir !== 'up') {
    for (let y = 3; y < 16; y++) {
      for (let x = 4; x < 21; x++) {
        if (!facePix(x, y)) continue;
        let c = skin[2];
        if (dir === 'down' && (x <= 7 || y >= 15)) c = skin[1];
        if (dir === 'left' && y >= 15) c = skin[1];
        P(x, y, c);
      }
    }
    // ears
    if (dir === 'down' && !L.ears) { P(6, 10, skin[1]); P(17, 10, skin[1]); }
    if (dir === 'left') { P(12, 10, skin[1]); P(12, 11, skin[0]); }
  }

  if (dir !== 'up') drawHair();

  // eyes (anime: lash line, iris with highlight)
  const closed = pose.eyes === 'closed';
  const hurt = pose.eyes === 'hurt';
  const lash = hair[0];
  const dEye = (x0: number, w: number, mirror: boolean) => {
    if (closed || hurt) {
      for (let i = 0; i < w; i++) P(x0 + i, 12, lash);
      if (hurt) { P(x0 + (mirror ? w - 1 : 0), 11, lash); P(x0 + (mirror ? 0 : w - 1), 13, lash); }
      return;
    }
    for (let i = 0; i < w; i++) P(x0 + i, 10, lash);
    P(mirror ? x0 + w : x0 - 1, 10, lash);
    P(mirror ? x0 + w : x0 - 1, 11, lash);
    for (let i = 0; i < w; i++) {
      P(x0 + i, 11, eye[0]);
      P(x0 + i, 12, eye[1]);
      P(x0 + i, 13, eye[3]);
    }
    P(x0 + (mirror ? w - 1 : 0), 11, '#ffffff');
    P(x0 + (mirror ? w - 1 : 0), 12, eye[2]);
    P(x0 + (mirror ? 0 : w - 1), 13, '#ffffffaa');
  };
  if (dir === 'down') {
    dEye(8, 3, false);
    dEye(13, 3, true);
    const bl = mix(L.skin, '#ff6f91', 0.5);
    P(8, 14, bl); P(15, 14, bl);
    const m = pose.mouth ?? 'neutral';
    const mc = mix(L.skin, '#7a2030', 0.6);
    if (m === 'open') { P(11, 14, mc); P(12, 14, mc); P(11, 15, mc); P(12, 15, mc); }
    else if (m === 'smile') { P(10, 14, mc); P(11, 15, mc); P(12, 15, mc); P(13, 14, mc); }
    else { P(11, 14, mc); P(12, 14, mc); }
    if (L.beard) {
      const b = ramp(L.beard, 4);
      for (let y = 13; y < 19; y++) for (let x = 8; x < 16; x++) if (inEllipse(x + 0.5, y + 0.5, 12, 13.5, 4.2, 5.2) && !(y < 14 && x > 9 && x < 14)) P(x, y, y > 15 ? b[1] : b[2]);
      P(10, 13, b[2]); P(13, 13, b[2]);
    }
  } else if (dir === 'left') {
    dEye(7, 2, false);
    P(5, 12, skin[3]);
    P(7, 14, mix(L.skin, '#ff6f91', 0.5));
    const mc = mix(L.skin, '#7a2030', 0.6);
    P(6, 14, mc);
    if (pose.mouth === 'open') P(6, 15, mc);
    if (L.beard) { const b = ramp(L.beard, 4); for (let y = 13; y < 18; y++) for (let x = 6; x < 11; x++) if (inEllipse(x + 0.5, y + 0.5, 8.5, 13.5, 3, 4.6)) P(x, y, b[2]); }
  }

  // hats / accessories
  const hc = ramp(L.hatColor ?? '#5a3aa0', 5);
  if (L.hat === 'wizard') {
    for (let x = 3; x <= 20; x++) for (const y of [4]) P(x, y, hc[2]);
    for (let x = 3; x <= 20; x++) P(x, 5, hc[1]);
    const rows = [[8, 15], [9, 14], [9, 14], [10, 13], [10, 13], [11, 12], [11, 12]];
    rows.forEach(([a, b], i) => { for (let x = a; x <= b; x++) P(x, 3 - i, i % 2 ? hc[2] : hc[3]); });
    P(14, -4, hc[2]); P(15, -3, hc[1]);
    for (let x = 8; x <= 15; x++) P(x, 3, hc[0]);
  } else if (L.hat === 'cap') {
    for (let x = 6; x <= 17; x++) { P(x, 3, hc[3]); P(x, 4, hc[2]); }
    for (let x = 5; x <= 18; x++) P(x, 5, hc[1]);
    if (dir === 'down') for (let x = 8; x <= 15; x++) P(x, 6, hc[0]);
  } else if (L.hat === 'band') {
    const y0 = 6;
    for (let x = 5; x <= 18; x++) if (hairPix(x, y0) || x === 5 || x === 18) P(x, y0, hc[3]);
    if (dir === 'down') { P(11, y0, '#fff2b0'); P(12, y0, '#fff2b0'); }
    if (dir !== 'up') { P(19, y0 + 1, hc[2]); P(20, y0 + 2, hc[1]); }
  } else if (L.hat === 'straw') {
    const sc = ramp('#e9c46a', 5);
    for (let x = 2; x <= 21; x++) { P(x, 4, sc[2]); P(x, 5, sc[1]); }
    for (let x = 7; x <= 16; x++) { P(x, 2, sc[3]); P(x, 3, sc[2]); }
    for (let x = 7; x <= 16; x++) P(x, 4, hc[2]);
  } else if (L.hat === 'crown') {
    const g = ramp('#f2c94c', 5);
    for (let x = 7; x <= 16; x++) P(x, 3, g[2]);
    for (const x of [7, 10, 13, 16]) { P(x, 2, g[3]); P(x, 1, g[4]); }
    P(11, 3, '#ff4d6d'); P(12, 3, '#ff4d6d');
  } else if (L.hat === 'hood') {
    for (let y = 1; y < 15; y++) for (let x = 3; x < 21; x++) {
      const inH = inEllipse(x + 0.5, y + 0.5, 12, 8, 8.4, 7.6);
      const hole = dir === 'down' ? inEllipse(x + 0.5, y + 0.5, 12, 9.6, 5.2, 4.8) : dir === 'left' ? inEllipse(x + 0.5, y + 0.5, 9.4, 9.6, 4.6, 4.8) : false;
      if (inH && !hole) P(x, y, y < 7 ? hc[3] : hc[2]);
    }
  }
}

function drawBody(ctx: Ctx, L: Look, dir: 'down' | 'up' | 'left', pose: Pose) {
  const o = pose.uo + OY + 1;
  const top = ramp(L.top, 4);
  const trim = ramp(L.trim, 4);
  const pants = ramp(L.pants, 3);
  const boots = ramp(L.boots, 3);
  const skin = ramp(L.skin, 4);
  const P = (x: number, y: number, c: string) => px(ctx, x, y + o, c);
  const Pl = (x: number, y: number, c: string) => px(ctx, x, y + OY, c); // legs ignore uo
  const legTop = 23 + pose.uo;
  const sw = pose.arms === 'swing' ? pose.swing : 0;

  const leg = (x: number, w: number, lift: number, shade: number) => {
    for (let y = legTop; y <= 24 - lift; y++) for (let i = 0; i < w; i++) Pl(x + i, y, pants[shade]);
    for (let i = 0; i < w; i++) {
      Pl(x + i, 25 - lift, boots[2]);
      Pl(x + i, 26 - lift, boots[1]);
    }
  };

  // cape behind
  if (L.cape && dir !== 'down') {
    const cp = ramp(L.cape, 4);
    const x0 = dir === 'up' ? 7 : 12;
    const x1 = dir === 'up' ? 16 : 17;
    for (let y = 14; y <= 25; y++) for (let x = x0; x <= x1; x++) P(x, y, y > 22 ? cp[0] : (x + y) % 5 === 0 ? cp[1] : cp[2]);
  }
  if (L.tail) {
    const t = ramp(L.tail, 4);
    const pts: [number, number][] = dir === 'left' ? [[15, 20], [16, 19], [17, 18], [18, 17], [18, 16], [19, 16]] : dir === 'up' ? [[13, 21], [14, 20], [15, 19], [16, 18], [17, 18]] : [[16, 23], [17, 22], [17, 21], [18, 20]];
    pts.forEach(([x, y], i) => { P(x, y, t[2]); P(x, y + 1, t[1]); if (i >= pts.length - 2) P(x, y, '#ffffff'); });
  }

  if (dir === 'left') {
    leg(10, 3, pose.liftL, 1);
    leg(11, 3, pose.liftR, 2);
    if (pose.liftL) { /* shift back leg visually */ }
  } else {
    leg(8, 3, pose.liftL, dir === 'up' ? 1 : 2);
    leg(13, 3, pose.liftR, 1);
    // gap shading between legs
  }

  // torso
  const drawTorso = (x0: number, x1: number) => {
    for (let y = 14; y <= 21; y++) {
      for (let x = x0; x <= x1; x++) {
        let c = top[2];
        if (x <= x0 + 1) c = top[3];
        if (x >= x1 - 1) c = top[1];
        if (y >= 20) c = top[1];
        P(x, y, c);
      }
    }
    // belt
    for (let x = x0; x <= x1; x++) P(x, 20, trim[1]);
    if (L.fem || L.armor === undefined) { /* nothing */ }
    if (L.fem) {
      for (let x = x0 - 1; x <= x1 + 1; x++) { P(x, 21, top[1]); P(x, 22 - pose.uo, top[1]); }
    }
  };
  if (dir === 'left') {
    drawTorso(9, 14);
    for (let y = 15; y < 20; y++) P(9, y, top[3]);
    P(10, 20, '#fff2b0');
  } else {
    drawTorso(8, 15);
    if (dir === 'down') {
      // collar & chest trim
      for (let x = 10; x <= 13; x++) P(x, 14, trim[3]);
      P(11, 15, trim[2]); P(12, 15, trim[2]);
      for (let y = 15; y <= 19; y++) { P(11, y, trim[1]); P(12, y, trim[1]); }
      P(11, 20, '#fff2b0'); P(12, 20, '#fff2b0');
      if (L.armor) { for (let x = 8; x <= 15; x++) P(x, 14, trim[2]); P(8, 15, trim[3]); P(15, 15, trim[3]); }
    } else {
      for (let x = 9; x <= 14; x++) P(x, 14, top[3]);
      if (L.armor) for (let x = 8; x <= 15; x++) P(x, 14, trim[2]);
    }
  }
  if (L.scarf) {
    const s = ramp(L.scarf, 4);
    if (dir === 'down') { for (let x = 8; x <= 15; x++) P(x, 14, s[2]); for (let x = 9; x <= 14; x++) P(x, 15, s[1]); P(15, 16, s[1]); P(16, 17, s[2]); P(16, 18, s[1]); P(15, 17, s[1]); }
    else if (dir === 'left') { for (let x = 9; x <= 14; x++) { P(x, 14, s[2]); } P(14, 15, s[1]); P(15, 16, s[2]); P(16, 17, s[2]); P(16, 18, s[1]); P(17, 18, s[2]); }
    else { for (let x = 8; x <= 15; x++) P(x, 14, s[2]); P(14, 15, s[1]); P(15, 16, s[2]); P(15, 17, s[1]); }
  }

  // arms
  const sleeve = top[2];
  const arm = (x: number, mode: 'down' | 'up' | 'fwd' | 'back', off: number, left: boolean) => {
    if (mode === 'down') {
      for (let y = 15 + off; y <= 19 + off; y++) { P(x, y, sleeve); P(x + (left ? 1 : -1), y, top[1]); }
      P(x, 20 + off, skin[2]); P(x + (left ? 1 : -1), 20 + off, skin[1]);
    } else if (mode === 'up') {
      const ax = x + (left ? -1 : 1);
      for (let y = 12; y <= 16; y++) { P(ax, y, sleeve); P(ax + (left ? 1 : -1), y, top[1]); }
      P(ax, 11, skin[2]); P(ax + (left ? 1 : -1), 11, skin[2]); P(ax, 10, skin[3]);
    } else if (mode === 'fwd') {
      for (let y = 16; y <= 18; y++) { P(x, y, sleeve); P(x + (left ? -1 : 1), y, sleeve); }
      P(x + (left ? -2 : 2), 18, skin[2]); P(x + (left ? -2 : 2), 19, skin[1]);
    } else {
      for (let y = 14; y <= 18; y++) P(x + (left ? -1 : 1), y, sleeve);
      P(x + (left ? -1 : 1), 13, skin[2]);
    }
  };
  if (dir === 'left') {
    const ax = 10 + sw * 2;
    if (pose.arms === 'up') { arm(10, 'up', 0, true); }
    else if (pose.arms === 'fwd') { for (let x = 4; x <= 10; x++) { P(x, 17, sleeve); P(x, 16, top[3]); } P(3, 17, skin[2]); P(3, 18, skin[1]); }
    else if (pose.arms === 'back') { for (let y = 15; y <= 18; y++) P(14, y, sleeve); P(15, 19, skin[2]); P(15, 18, sleeve); P(16, 17, sleeve); }
    else { for (let y = 15; y <= 19; y++) { P(ax, y, sleeve); P(ax + 1, y, top[1]); } P(ax, 20, skin[2]); P(ax + 1, 20, skin[1]); }
  } else if (pose.arms === 'up') {
    arm(7, 'up', 0, true); arm(16, 'up', 0, false);
  } else if (pose.arms === 'fwd') {
    arm(7, 'down', 0, true);
    arm(16, 'fwd', 0, false);
  } else if (pose.arms === 'back') {
    arm(7, 'down', 0, true);
    arm(16, 'back', 0, false);
  } else {
    arm(7, 'down', sw, true); arm(16, 'down', -sw, false);
  }
  if (L.cape && dir === 'down') {
    const cp = ramp(L.cape, 4);
    for (let y = 14; y <= 22; y++) { P(5, y, cp[2]); P(6, y, cp[1]); P(17, y, cp[1]); P(18, y, cp[2]); }
  }
}

function renderFrame(L: Look, dirKey: 'down' | 'up' | 'left', pose: Pose, scale: number): HTMLCanvasElement {
  const [c, ctx] = mk(CW, CH);
  drawBody(ctx, L, dirKey, pose);
  drawHead(ctx, L, dirKey, pose);
  void scale;
  outline(c);
  return c;
}

const cache = new Map<string, Sheet>();

export function makeSheet(key: string, L: Look): Sheet {
  const hit = cache.get(key);
  if (hit) return hit;
  const frames = new Map<string, HTMLCanvasElement>();
  const flashes = new Map<string, HTMLCanvasElement>();
  const build = (anim: string, dir: Dir, i: number) => {
    const k = `${anim}:${dir}:${i}`;
    let f = frames.get(k);
    if (f) return f;
    const poses = POSES[anim] ?? POSES.idle;
    const pose = poses[i % poses.length];
    if (dir === 'right') f = flipX(build(anim, 'left', i));
    else f = renderFrame(L, dir, pose, 1);
    frames.set(k, f);
    return f;
  };
  const sheet: Sheet = {
    frame: build,
    flash: (anim, dir, i) => {
      const k = `${anim}:${dir}:${i}`;
      let f = flashes.get(k);
      if (!f) {
        f = silhouette(build(anim, dir, i), '#ffffff');
        flashes.set(k, f);
      }
      return f;
    },
    count: (anim) => (POSES[anim] ?? POSES.idle).length,
  };
  cache.set(key, sheet);
  return sheet;
}

// ---------- Presets ----------
export const HERO_LOOKS: Record<string, Look> = {
  kai: {
    skin: '#f6c9a0', hair: '#2f6bff', hairStyle: 'spiky', eyes: '#ffb020',
    top: '#e9eefb', trim: '#2f6bff', pants: '#2b3350', boots: '#6b3f2a', scarf: '#e8453c',
  },
  aiko: {
    skin: '#f9d3b4', hair: '#ff6f91', hairStyle: 'ponytail', eyes: '#35c6ff',
    top: '#fff1f0', trim: '#e8453c', pants: '#2b3350', boots: '#6b3f2a', scarf: '#2f6bff', fem: true,
  },
};

export const NPC_LOOKS: Record<string, Look> = {
  mira: { skin: '#f1c9a5', hair: '#e8e8f2', hairStyle: 'elder', eyes: '#7a5cff', top: '#6b4fb8', trim: '#f2c94c', pants: '#4a3a7a', boots: '#4a2f22', fem: true },
  lyra: { skin: '#fbd9c0', hair: '#9b5cff', hairStyle: 'twin', eyes: '#ff4da6', top: '#3b2a78', trim: '#f2c94c', pants: '#2a1f55', boots: '#2a1f40', hat: 'wizard', hatColor: '#5a3aa0', fem: true, cape: '#7b4fd0' },
  torren: { skin: '#d9a273', hair: '#8a8f9a', hairStyle: 'messy', eyes: '#46d17a', top: '#7d8794', trim: '#c0c6cf', pants: '#4a4f5a', boots: '#2e2e36', armor: true, ears: '#8a8f9a', tail: '#8a8f9a', cape: '#c0392b' },
  sylphie: { skin: '#fbdcc0', hair: '#ffcf70', hairStyle: 'bob', eyes: '#46d1c9', top: '#ffffff', trim: '#46d1c9', pants: '#ffe9b8', boots: '#f2c94c', ears: '#ffcf70', tail: '#ffcf70', fem: true },
  rhea: { skin: '#e9bf9b', hair: '#1c1c2e', hairStyle: 'long', eyes: '#ff3860', top: '#2a2a40', trim: '#ff3860', pants: '#1b1b2c', boots: '#141420', hat: 'hood', hatColor: '#2a2a40', scarf: '#ff3860', fem: true },
  velkan: { skin: '#e8cdb6', hair: '#e9eefb', hairStyle: 'spiky', eyes: '#d02ffb', top: '#1a1030', trim: '#a020f0', pants: '#120a22', boots: '#0a0614', cape: '#3a1060', armor: true },
  villager_m: { skin: '#f0c49a', hair: '#7a4a2a', hairStyle: 'short', eyes: '#3a2a20', top: '#c9893a', trim: '#8a5a20', pants: '#5a4a3a', boots: '#3a2a20' },
  villager_f: { skin: '#f7d2b0', hair: '#c0643a', hairStyle: 'bob', eyes: '#2d7a4a', top: '#d9577a', trim: '#fff1d0', pants: '#7a3a4a', boots: '#4a2a2a', fem: true },
  child: { skin: '#f9d3b4', hair: '#4a8a3a', hairStyle: 'messy', eyes: '#3a2a20', top: '#e9c46a', trim: '#e8703a', pants: '#4a5a8a', boots: '#6a4a2a' },
  smith: { skin: '#cf9570', hair: '#3a2a20', hairStyle: 'short', eyes: '#2a2a2a', top: '#8a5a3a', trim: '#c9a050', pants: '#3a3a44', boots: '#222', beard: '#3a2a20', armor: true },
  merchant: { skin: '#e8b88a', hair: '#9a2f2f', hairStyle: 'messy', eyes: '#2a4a8a', top: '#2f9a8a', trim: '#f2c94c', pants: '#4a3a2a', boots: '#3a2a20', hat: 'cap', hatColor: '#c0392b', scarf: '#f2c94c' },
  guard: { skin: '#e8b88a', hair: '#3a3a4a', hairStyle: 'short', eyes: '#2a2a3a', top: '#5a6a9a', trim: '#c0c6cf', pants: '#3a3f5a', boots: '#2a2a35', armor: true, hat: 'cap', hatColor: '#8a95b8' },
  innkeeper: { skin: '#f2c8a0', hair: '#d0a050', hairStyle: 'ponytail', eyes: '#5a8a3a', top: '#f2e0b0', trim: '#c0643a', pants: '#8a5a3a', boots: '#4a2a1a', fem: true },
  elder_m: { skin: '#e8c4a0', hair: '#d8d8e0', hairStyle: 'elder', eyes: '#3a4a8a', top: '#4a7a5a', trim: '#e8c872', pants: '#3a4a3a', boots: '#3a2a20', beard: '#d8d8e0', hat: 'straw', hatColor: '#6a4a2a' },
  fisher: { skin: '#e0a880', hair: '#2a2a2a', hairStyle: 'short', eyes: '#2a2a2a', top: '#4a8aaa', trim: '#e9c46a', pants: '#3a4a5a', boots: '#2a2a2a', hat: 'straw', hatColor: '#4a8aaa' },
  mystic: { skin: '#e8c9b5', hair: '#46d1c9', hairStyle: 'long', eyes: '#f2c94c', top: '#1f6f78', trim: '#f2c94c', pants: '#1a4a55', boots: '#1a3a45', hat: 'band', hatColor: '#f2c94c', fem: true, cape: '#2f9aa8' },
};
