import { Ctx, mk, px, rect, ramp, mix, outline, ellipse, shadedEllipse, silhouette, flipX } from './pixel';

export interface MonsterArt {
  frames: HTMLCanvasElement[];   // idle/move cycle
  atk: HTMLCanvasElement;        // wind-up/attack pose
  flash: HTMLCanvasElement[];    // white silhouettes of frames
  w: number; h: number;          // canvas size (feet at bottom centre)
  faces: 'right' | 'front';      // whether sprite is side-facing (flip needed)
}

function finalize(frames: HTMLCanvasElement[], atk: HTMLCanvasElement | null, faces: 'right' | 'front'): MonsterArt {
  frames.forEach((f) => outline(f));
  const a = atk ?? frames[0];
  if (atk) outline(atk);
  return { frames, atk: a, flash: frames.map((f) => silhouette(f)), w: frames[0].width, h: frames[0].height, faces };
}

function eye(ctx: Ctx, x: number, y: number, col = '#12081e', big = false) {
  rect(ctx, x, y, big ? 3 : 2, big ? 4 : 3, col);
  px(ctx, x, y, '#ffffff');
}

function slime(color: string, scale = 1, crown = false, angry = false): MonsterArt {
  const W = Math.round(24 * scale), H = Math.round(20 * scale);
  const mkF = (squash: number) => {
    const [c, ctx] = mk(W + 4, H + 6);
    const rp = ramp(color, 5);
    const cx = (W + 4) / 2, rx = Math.round(W / 2 - 2 + squash), ry = Math.round(H / 2 - 1 - squash);
    ctx.fillStyle = 'rgba(0,0,0,.22)'; ctx.fillRect(cx - rx, H + 3, rx * 2, 2);
    shadedEllipse(ctx, cx, H - ry + 3, rx, ry, rp, { lx: -0.5, ly: -0.7 });
    // highlight blob
    rect(ctx, Math.round(cx - rx * 0.55), Math.round(H - ry * 1.7 + 3), Math.max(2, Math.round(2 * scale)), Math.max(1, Math.round(scale)), '#ffffffcc');
    const ey = Math.round(H - ry * 1.05 + 3);
    const ex = Math.round(3 * scale);
    eye(ctx, cx - ex - 1, ey, '#12081e', scale >= 1);
    eye(ctx, cx + ex - 1, ey, '#12081e', scale >= 1);
    if (angry) { rect(ctx, cx - ex - 2, ey - 2, 4, 1, '#12081e'); rect(ctx, cx + ex - 1, ey - 2, 4, 1, '#12081e'); }
    rect(ctx, cx - 1, ey + 4 * Math.min(2, scale), Math.max(2, Math.round(2 * scale)), 1, '#12081e');
    if (crown) {
      const g = ramp('#f2c94c', 4);
      const cy = Math.round(H - ry * 2 + 4);
      rect(ctx, cx - 8, cy, 16, 4, g[2]);
      for (const dx of [-8, -3, 2, 7]) { rect(ctx, cx + dx, cy - 4, 2, 4, g[3]); px(ctx, cx + dx, cy - 5, g[3]); }
      rect(ctx, cx - 1, cy + 1, 2, 2, '#ff4d6d');
    }
    return c;
  };
  return finalize([mkF(0), mkF(1.5)], mkF(-1.5), 'front');
}

function bat(color: string, big = false): MonsterArt {
  const S = big ? 1.5 : 1;
  const mkF = (up: boolean) => {
    const [c, ctx] = mk(Math.round(30 * S), Math.round(22 * S));
    const rp = ramp(color, 5), cx = c.width / 2, cy = Math.round(12 * S);
    const wing = (dir: number) => {
      for (let i = 0; i < Math.round(10 * S); i++) {
        const x = cx + dir * (4 + i);
        const yy = cy + (up ? -Math.round(i * 0.7) : Math.round(i * 0.3));
        const h = Math.round((7 - i * 0.4) * S);
        rect(ctx, Math.min(x, x), yy - Math.round(h / 2), 1, h, i % 3 === 0 ? rp[1] : rp[2]);
      }
      rect(ctx, cx + dir * (4 + Math.round(10 * S)), cy + (up ? -7 : 3), 1, 2, rp[1]);
    };
    wing(-1); wing(1);
    shadedEllipse(ctx, cx, cy, Math.round(5 * S), Math.round(5 * S), rp);
    px(ctx, cx - 4 * S, cy - 6 * S, rp[1]); px(ctx, cx + 4 * S, cy - 6 * S, rp[1]); px(ctx, cx - 4 * S, cy - 5 * S, rp[1]); px(ctx, cx + 4 * S, cy - 5 * S, rp[1]);
    rect(ctx, cx - 3, cy - 1, 2, 2, '#ff4d6d'); rect(ctx, cx + 1, cy - 1, 2, 2, '#ff4d6d');
    px(ctx, cx - 2, cy + 3, '#ffffff'); px(ctx, cx + 1, cy + 3, '#ffffff');
    return c;
  };
  return finalize([mkF(true), mkF(false)], mkF(true), 'front');
}

function wolf(color: string, scale = 1, scarred = false): MonsterArt {
  const W = Math.round(34 * scale), H = Math.round(24 * scale);
  const mkF = (step: number, atk = false) => {
    const [c, ctx] = mk(W, H);
    const rp = ramp(color, 5);
    const s = (n: number) => Math.round(n * scale);
    const legs = [[8, 0], [12, 1], [21, 1], [25, 0]];
    legs.forEach(([lx, ph], i) => {
      const lift = step === 0 ? (i % 2 ? 2 : 0) : step === 1 ? (i % 2 ? 0 : 2) : 0;
      rect(ctx, s(lx), s(16) - (ph ? 0 : 0), s(3), s(5) - Math.round(lift * scale * 0.6), i < 2 ? rp[1] : rp[2]);
      rect(ctx, s(lx), s(20) - Math.round(lift * scale * 0.6), s(3), 1, rp[0]);
    });
    shadedEllipse(ctx, s(16), s(12), s(11), s(6), rp, { lx: -0.2, ly: -0.8 });
    // tail
    for (let i = 0; i < s(7); i++) { rect(ctx, s(4) - i, s(9) - Math.round(i * 0.6) , 2, s(3), rp[i % 3 ? 2 : 3]); }
    // head
    const hx = s(24), hy = s(7) + (atk ? -2 : 0);
    shadedEllipse(ctx, hx, hy + s(2), s(6), s(5), rp, { lx: -0.4, ly: -0.7 });
    rect(ctx, hx + s(4), hy + s(3), s(5), s(3), rp[3]); // snout
    rect(ctx, hx + s(8), hy + s(3), 2, 2, '#12081e');
    px(ctx, hx - 3, hy - s(2), rp[1]); px(ctx, hx - 3, hy - s(3), rp[1]); px(ctx, hx, hy - s(3), rp[1]); px(ctx, hx, hy - s(4), rp[2]); px(ctx, hx - 2, hy - s(4), rp[2]);
    rect(ctx, hx + 2, hy + 1, 3, 2, scarred ? '#ff3a3a' : '#ffd23a'); px(ctx, hx + 2, hy + 1, '#ffffff');
    if (atk) { rect(ctx, hx + s(5), hy + s(6), s(4), 2, '#ff4d6d'); px(ctx, hx + s(5), hy + s(5), '#fff'); px(ctx, hx + s(8), hy + s(5), '#fff'); }
    if (scarred) { for (let i = 0; i < 6; i++) px(ctx, hx - 2 + i, hy + i - 1, '#ffffff99'); rect(ctx, s(14), s(8), 6, 1, rp[0]); }
    return c;
  };
  return finalize([mkF(0), mkF(1)], mkF(2, true), 'right');
}

function humanoid(opts: { skin: string; cloth: string; weapon?: 'club' | 'bow' | 'sword' | 'staff' | 'none'; ears?: boolean; eyes?: string; bone?: boolean; helmet?: string; big?: boolean }): MonsterArt {
  const mkF = (step: number, atk = false) => {
    const [c, ctx] = mk(26, 32);
    const sk = ramp(opts.skin, 5), cl = ramp(opts.cloth, 4);
    const lift = step === 1 ? 1 : 0;
    // legs
    rect(ctx, 9, 21, 3, 6 - lift, opts.bone ? sk[3] : cl[1]); rect(ctx, 14, 21, 3, 6 - (step === 1 ? 0 : lift), opts.bone ? sk[3] : cl[1]);
    rect(ctx, 8, 27 - lift, 4, 2, opts.bone ? sk[2] : '#4a3020'); rect(ctx, 14, 27 - (step === 1 ? 0 : lift), 4, 2, opts.bone ? sk[2] : '#4a3020');
    // body
    rect(ctx, 8, 14, 10, 8, opts.bone ? sk[2] : cl[2]); rect(ctx, 8, 14, 3, 8, opts.bone ? sk[3] : cl[3]); rect(ctx, 8, 20, 10, 2, cl[1]);
    if (opts.bone) { for (let y = 15; y < 21; y += 2) rect(ctx, 10, y, 6, 1, sk[0]); rect(ctx, 12, 14, 2, 7, sk[1]); }
    // arms
    rect(ctx, 5, 15, 3, 6, opts.bone ? sk[3] : opts.skin); rect(ctx, 18, 15, 3, 6, opts.bone ? sk[3] : opts.skin);
    // head
    shadedEllipse(ctx, 13, 8, 7, 7, sk, { lx: -0.4, ly: -0.6 });
    if (opts.helmet) { const h = ramp(opts.helmet, 4); rect(ctx, 6, 2, 14, 5, h[2]); rect(ctx, 6, 2, 14, 2, h[3]); rect(ctx, 6, 7, 14, 1, h[0]); rect(ctx, 12, 2, 2, 8, h[1]); }
    if (opts.ears) { rect(ctx, 3, 7, 4, 2, sk[2]); rect(ctx, 1, 6, 3, 1, sk[3]); rect(ctx, 19, 7, 4, 2, sk[2]); rect(ctx, 22, 6, 3, 1, sk[3]); }
    const ec = opts.eyes ?? '#ffdd33';
    rect(ctx, 9, 8, 3, 3, '#12081e'); rect(ctx, 14, 8, 3, 3, '#12081e'); rect(ctx, 10, 9, 2, 2, ec); rect(ctx, 14, 9, 2, 2, ec);
    if (opts.bone) { rect(ctx, 11, 12, 4, 2, '#12081e'); for (let i = 0; i < 4; i++) px(ctx, 11 + i, 12, '#fff'); }
    else { rect(ctx, 11, 12, 4, 1, '#3a1010'); px(ctx, 11, 11, '#fff'); px(ctx, 14, 11, '#fff'); }
    // weapon
    const wp = opts.weapon ?? 'none';
    const wy = atk ? 8 : 16;
    if (wp === 'club') { rect(ctx, 21, wy - 2, 3, 12, '#7a4a2a'); rect(ctx, 20, wy - 6, 5, 6, '#9a6a3a'); px(ctx, 21, wy - 5, '#c0a070'); }
    if (wp === 'sword') { rect(ctx, 22, wy - 8, 2, 12, '#d8e0f0'); rect(ctx, 20, wy + 3, 6, 2, '#7a4a2a'); px(ctx, 22, wy - 8, '#fff'); }
    if (wp === 'bow') { for (let i = 0; i < 12; i++) px(ctx, 22 + (i < 6 ? i / 3 : (12 - i) / 3 | 0), 8 + i, '#9a6a3a'); rect(ctx, 22, 8, 1, 12, '#e8e8f8'); if (atk) rect(ctx, 14, 14, 9, 1, '#e8e8f8'); }
    if (wp === 'staff') { rect(ctx, 22, 4, 2, 24, '#6a4a2a'); ellipse(ctx, 23, 3, 3, 3, '#b48cff'); px(ctx, 22, 2, '#fff'); }
    return c;
  };
  return finalize([mkF(0), mkF(1)], mkF(0, true), 'front');
}

function mushroom(color: string): MonsterArt {
  const mkF = (b: number) => {
    const [c, ctx] = mk(24, 26);
    const cap = ramp(color, 5), stem = ramp('#f0e0c0', 4);
    rect(ctx, 8, 14 + b, 8, 8, stem[2]); rect(ctx, 8, 14 + b, 3, 8, stem[3]); rect(ctx, 8, 20 + b, 8, 2, stem[1]);
    rect(ctx, 6, 22 + b, 3, 2, stem[2]); rect(ctx, 15, 22 + b, 3, 2, stem[2]);
    shadedEllipse(ctx, 12, 9 + b, 10, 8, cap, { lx: -0.5, ly: -0.7 });
    for (const [x, y, r] of [[7, 6, 2], [14, 5, 2], [11, 11, 1], [17, 10, 1]]) ellipse(ctx, x, y + b, r, r, '#fff6ee');
    rect(ctx, 9, 15 + b, 2, 3, '#12081e'); rect(ctx, 13, 15 + b, 2, 3, '#12081e'); px(ctx, 9, 15 + b, '#fff'); px(ctx, 13, 15 + b, '#fff');
    return c;
  };
  return finalize([mkF(0), mkF(1)], mkF(-1), 'front');
}

function golem(color: string, scale = 1, crystals = false): MonsterArt {
  const s = scale;
  const W = Math.round(34 * s), H = Math.round(40 * s);
  const mkF = (step: number, atk = false) => {
    const [c, ctx] = mk(W, H);
    const rp = ramp(color, 5);
    const S = (n: number) => Math.round(n * s);
    rect(ctx, S(8), S(28) - (step ? 1 : 0), S(6), S(10), rp[1]); rect(ctx, S(20), S(28) - (step ? 0 : 1), S(6), S(10), rp[1]);
    rect(ctx, S(6), S(37), S(9), S(3), rp[0]); rect(ctx, S(19), S(37), S(9), S(3), rp[0]);
    shadedEllipse(ctx, S(17), S(21), S(11), S(11), rp, { lx: -0.4, ly: -0.7 });
    // arms
    const ay = atk ? S(6) : S(16);
    shadedEllipse(ctx, S(4), ay + S(6), S(4), S(7), rp, {}); shadedEllipse(ctx, S(30), ay + S(6), S(4), S(7), rp, {});
    shadedEllipse(ctx, S(4), ay + S(14), S(5), S(5), rp, {}); shadedEllipse(ctx, S(30), ay + S(14), S(5), S(5), rp, {});
    // head
    shadedEllipse(ctx, S(17), S(8), S(7), S(6), rp, { lx: -0.4, ly: -0.7 });
    const glow = crystals ? '#66e6ff' : '#ffb03a';
    rect(ctx, S(13), S(7), S(3), S(2), glow); rect(ctx, S(19), S(7), S(3), S(2), glow);
    ellipse(ctx, S(17), S(22), S(3), S(3), glow); px(ctx, S(16), S(21), '#fff');
    for (let i = 0; i < 6; i++) { px(ctx, S(8) + i * S(3), S(15) + (i % 2) * S(6), rp[0]); px(ctx, S(9) + i * S(3), S(27) - (i % 2) * S(3), rp[3]); }
    if (crystals) for (const [x, y, h] of [[10, 6, 8], [24, 5, 10], [17, 0, 8], [6, 14, 6], [29, 13, 7]]) { rect(ctx, S(x), S(y) - S(h) + S(6), S(3), S(h), '#8af0ff'); rect(ctx, S(x), S(y) - S(h) + S(6), 1, S(h), '#ffffff'); px(ctx, S(x) + 1, S(y) - S(h) + S(5), '#8af0ff'); }
    return c;
  };
  return finalize([mkF(0), mkF(1)], mkF(0, true), 'front');
}

function wisp(color: string): MonsterArt {
  const mkF = (b: number) => {
    const [c, ctx] = mk(20, 26);
    const rp = ramp(color, 5);
    // flame tail
    for (let i = 0; i < 9; i++) { const w = Math.max(1, 6 - i); ellipse(ctx, 10 + (i % 2 ? b : -b) * (i > 4 ? 1 : 0), 14 + i, w, 1, rp[Math.max(0, 3 - Math.floor(i / 3))]); }
    shadedEllipse(ctx, 10, 11, 7, 8, rp, { lx: 0, ly: -0.5 });
    ellipse(ctx, 10, 10, 4, 5, rp[4]);
    px(ctx, 8, 3, rp[3]); px(ctx, 12, 2, rp[3]); px(ctx, 10, 1, rp[4]);
    rect(ctx, 7, 9, 2, 3, '#12081e'); rect(ctx, 12, 9, 2, 3, '#12081e'); px(ctx, 7, 9, '#fff'); px(ctx, 12, 9, '#fff');
    return c;
  };
  return finalize([mkF(0), mkF(1)], mkF(0), 'front');
}

function shadowKnight(): MonsterArt {
  const base = humanoid({ skin: '#2a2040', cloth: '#1c1430', weapon: 'sword', eyes: '#ff3adf', helmet: '#3a2a60' });
  return base;
}

export const MONSTER_ART: Record<string, () => MonsterArt> = {
  slime_green: () => slime('#5ed26a'),
  slime_blue: () => slime('#58a8ff'),
  slime_red: () => slime('#ff6a5a', 1, false, true),
  slime_king: () => slime('#7ae88a', 2.6, true, true),
  bat: () => bat('#6a4a9a'),
  bat_fire: () => bat('#d9482e'),
  wolf: () => wolf('#8a8a98'),
  wolf_dark: () => wolf('#4a4a5e'),
  wolf_alpha: () => wolf('#d8d8e8', 1.6, true),
  goblin: () => humanoid({ skin: '#6fbf5a', cloth: '#8a5a2a', weapon: 'club', ears: true }),
  goblin_archer: () => humanoid({ skin: '#6fbf5a', cloth: '#4a7a3a', weapon: 'bow', ears: true }),
  skeleton: () => humanoid({ skin: '#e8e4d8', cloth: '#4a4060', weapon: 'sword', bone: true, eyes: '#ff4d4d' }),
  skeleton_mage: () => humanoid({ skin: '#e8e4d8', cloth: '#3a2a70', weapon: 'staff', bone: true, eyes: '#b48cff' }),
  mushroom: () => mushroom('#d9485a'),
  mushroom_blue: () => mushroom('#5a7ad9'),
  golem: () => golem('#8a8a98'),
  golem_crystal: () => golem('#6a6a90', 1, true),
  crystal_guardian: () => golem('#5a6aa8', 1.7, true),
  wisp_fire: () => wisp('#ff8a2a'),
  wisp_ice: () => wisp('#6ad0ff'),
  wisp_dark: () => wisp('#a06cff'),
  shadow_knight: () => shadowKnight(),
};

const cache = new Map<string, MonsterArt>();
export function monsterArt(key: string): MonsterArt {
  let a = cache.get(key);
  if (!a) {
    const fn = MONSTER_ART[key] ?? MONSTER_ART.slime_green;
    a = fn();
    cache.set(key, a);
  }
  return a;
}
export { flipX, mix };
