"""Monster spritesheets (single-view creatures)."""
import math, json, os, sys
import numpy as np
from PIL import Image
sys.path.insert(0, os.path.dirname(__file__))
from pix import Canvas, Part, ramp
from objects import Pal


def sheet_from(rows, fw, fh, out_png, out_json):
    """rows: list of (anim, dir, fps, loop, [PIL frames], hit)"""
    maxf = max(len(r[4]) for r in rows)
    sheet = Image.new('RGBA', (maxf * fw, len(rows) * fh), (0, 0, 0, 0))
    meta = {'frame_w': fw, 'frame_h': fh, 'rows': []}
    for ri, (an, d, fps, loop, frames, hit) in enumerate(rows):
        for i, im in enumerate(frames):
            sheet.alpha_composite(im, (i * fw, ri * fh))
        meta['rows'].append({'anim': an, 'dir': d, 'row': ri, 'frames': len(frames), 'fps': fps, 'loop': loop, 'hit': hit})
    sheet.save(out_png)
    json.dump(meta, open(out_json, 'w'))


def ease(t):
    t = max(0, min(1, t))
    return t * t * (3 - 2 * t)


# ------------------------------------------------------------------ slime
def slime_frame(color, squash=0.0, lift=0.0, eyes='open', kind='plain', fade=1.0, tilt=0.0, mouth='smile', size=1.0, drip=0.0):
    FW = 64
    c = Canvas(FW, FW); P = Pal(c)
    cx, gy = 32, 56
    c.ellipse(P('shadow', '#000000', -9, flat=True), cx, gy + 1, 15 * size * (1 - lift * 0.01), 4 * size)
    bw = 20 * size * (1 + 0.55 * squash)
    bh = 24 * size * (1 - 0.55 * squash)
    top = gy - bh - lift
    body = P('body', color, 6); belly = P('belly', color, 7, flat=True); dark = P('dark', color, 5, flat=True)
    pts = [(cx - bw, gy - lift - 2), (cx - bw * 0.95, gy - lift - bh * 0.45), (cx - bw * 0.62, top + bh * 0.12), (cx - bw * 0.2 + tilt, top), (cx + bw * 0.2 + tilt, top),
           (cx + bw * 0.62, top + bh * 0.12), (cx + bw * 0.95, gy - lift - bh * 0.45), (cx + bw, gy - lift - 2), (cx + bw * 0.6, gy - lift + 1), (cx - bw * 0.6, gy - lift + 1)]
    c.blob(body, pts)
    if drip > 0:
        c.blob(body, [(cx - 8, gy - lift), (cx - 6, gy - lift + 8 * drip), (cx - 3, gy - lift)])
    # belly sheen + highlight
    c.ellipse(belly, cx + 2, gy - lift - bh * 0.28, bw * 0.55, bh * 0.28)
    c.ellipse(P('spark', '#ffffff', 11, flat=True), cx - bw * 0.42, top + bh * 0.28, 3.4 * size, 2.2 * size)
    c.ellipse(P('spark', '#ffffff', 11, flat=True), cx - bw * 0.2, top + bh * 0.2, 1.4 * size, 1.2 * size)
    # face
    ey = top + bh * 0.52 + tilt * 0.3
    ex = 6.2 * size
    for sx in (-1, 1):
        if eyes == 'closed':
            c.line(P('pupil', '#140a24', 10, flat=True), cx + sx * ex - 2, ey, cx + sx * ex + 2, ey, 1.2)
        elif eyes == 'angry':
            c.ellipse(P('eye_w', '#ffffff', 9, flat=True), cx + sx * ex, ey, 3.3 * size, 4.0 * size)
            c.ellipse(P('pupil', '#140a24', 10, flat=True), cx + sx * ex, ey + 0.4, 2.3 * size, 3.2 * size)
            c.ellipse(P('spark', '#ffffff', 11, flat=True), cx + sx * ex - 0.8, ey - 1, 1.0, 1.0)
            c.line(P('pupil', '#140a24', 10, flat=True), cx + sx * ex - 4 * sx * -1, ey - 5 - 0.0, cx + sx * ex + 3.6 * sx * -1, ey - 3, 1.4) if False else None
            c.line(P('pupil', '#140a24', 10, flat=True), cx + sx * (ex + 3.6), ey - 5.2, cx + sx * (ex - 3.4), ey - 3.0, 1.4)
        else:
            c.ellipse(P('eye_w', '#ffffff', 9, flat=True), cx + sx * ex, ey, 3.3 * size, 4.2 * size)
            c.ellipse(P('pupil', '#140a24', 10, flat=True), cx + sx * ex, ey + 0.5, 2.4 * size, 3.4 * size)
            c.ellipse(P('spark', '#ffffff', 11, flat=True), cx + sx * ex - 0.9, ey - 1.2, 1.1, 1.3)
    my = ey + 6.5 * size
    if mouth == 'open':
        c.ellipse(P('mouth', '#7a2030', 10, flat=True), cx, my, 2.6 * size, 2.2 * size)
    elif mouth == 'smile':
        c.line(P('mouth', '#7a2030', 10, flat=True), cx - 2.5, my - 0.5, cx, my + 0.6, 1.0)
        c.line(P('mouth', '#7a2030', 10, flat=True), cx, my + 0.6, cx + 2.5, my - 0.5, 1.0)
    # accessories
    if kind == 'crown':
        g = ramp('#f2c94c', 5)
        gp = P('gold', '#f2c94c', 9)
        cy0 = top - 1
        c.poly(gp, [(cx - 10 * size, cy0 + 4), (cx - 10 * size, cy0 - 5), (cx - 5 * size, cy0), (cx, cy0 - 8), (cx + 5 * size, cy0), (cx + 10 * size, cy0 - 5), (cx + 10 * size, cy0 + 4)])
        c.ellipse(P('ruby', '#ff4d6d', 10, flat=True), cx, cy0 + 1.5, 2, 2)
    elif kind == 'spikes':
        sp = P('spike', '#ffb04a', 9)
        for dx in (-9, -3, 3, 9):
            c.poly(sp, [(cx + dx - 3, top + 6), (cx + dx, top - 6), (cx + dx + 3, top + 6)])
    elif kind == 'frost':
        sp = P('ice', '#dff4ff', 9)
        for dx in (-8, 0, 8):
            c.poly(sp, [(cx + dx - 3, top + 5), (cx + dx, top - 7), (cx + dx + 3, top + 5)])
    img = c.render()
    if fade < 1:
        a = np.asarray(img).copy(); a[..., 3] = (a[..., 3] * fade).astype(np.uint8); img = Image.fromarray(a, 'RGBA')
    return img


def slime_sheet(name, color, kind='plain', size=1.0, angry=False):
    ey = 'angry' if angry else 'open'
    idle = [slime_frame(color, 0.10 * math.sin(i / 6 * 2 * math.pi), 0, ey, kind, size=size) for i in range(6)]
    # hop: crouch, crouch, launch, rise, peak, fall, land, recover
    hop_p = [(0.35, 0), (0.5, 0), (-0.25, 6), (-0.3, 13), (-0.1, 16), (-0.25, 10), (0.5, 0), (0.15, 0)]
    move = [slime_frame(color, s, l * size, ey, kind, size=size, mouth='open' if l > 6 else 'smile') for s, l in hop_p]
    attack = [slime_frame(color, 0.45, 0, 'angry', kind, size=size, mouth='open'), slime_frame(color, 0.6, 0, 'angry', kind, size=size, mouth='open'), slime_frame(color, -0.35, 8 * size, 'angry', kind, size=size, mouth='open'),
              slime_frame(color, -0.3, 12 * size, 'angry', kind, size=size, mouth='open'), slime_frame(color, 0.4, 0, 'angry', kind, size=size, mouth='open'), slime_frame(color, 0.1, 0, ey, kind, size=size)]
    hurt = [slime_frame(color, 0.5, 0, 'closed', kind, size=size, mouth='open', tilt=3), slime_frame(color, 0.25, 0, 'closed', kind, size=size, mouth='open', tilt=-2)]
    death = [slime_frame(color, 0.2 + 0.7 * ease(i / 5), 0, 'closed', kind, size=size, mouth='open', fade=1 - ease(max(0, i - 2) / 3) * 0.9, drip=i / 5) for i in range(6)]
    rows = [('idle', 'right', 7, True, idle, 0), ('walk', 'right', 12, True, move, 0), ('attack', 'right', 12, False, attack, 3), ('hurt', 'right', 10, False, hurt, 0), ('death', 'right', 10, False, death, 0)]
    return rows


# ------------------------------------------------------------------ bat
def bat_frame(color, flap=0.0, dive=False, eyes='open', hurt=False, lift=14, size=1.0, fade=1.0, rot=0):
    FW = 64
    c = Canvas(FW, FW); P = Pal(c)
    cx = 32
    gy = 56
    c.ellipse(P('shadow', '#000000', -9, flat=True), cx, gy, 11 * size, 3 * size)
    cy = gy - lift - 12
    body = P('body', color, 6); wing = P('wing', color, 5); mem = P('mem', color, 4); fur = P('fur', color, 7, flat=True)
    def wing_poly(sx):
        # wing from shoulder out; flap in [-1,1] (up/down)
        sh = (cx + sx * 4, cy - 1)
        tipx = cx + sx * (26 - abs(flap) * 6 * (1.2 if dive else 1))
        tipy = cy - 8 - flap * 14 + (10 if dive else 0)
        elb = (cx + sx * 15, cy - 9 - flap * 8 + (4 if dive else 0))
        pts = [sh, elb, (tipx, tipy), (cx + sx * 21, cy + 3 - flap * 2 + 3), (cx + sx * 13, cy + 5 - flap * 1), (cx + sx * 8, cy + 6)]
        c.blob(mem, pts)
        c.line(wing, sh[0], sh[1], elb[0], elb[1], 2.0)
        c.line(wing, elb[0], elb[1], tipx, tipy, 1.8)
        c.line(wing, elb[0], elb[1], cx + sx * 21, cy + 3 - flap * 2 + 3, 1.2)
        c.line(wing, elb[0], elb[1], cx + sx * 13, cy + 5 - flap, 1.2)
    wing_poly(-1); wing_poly(1)
    c.ellipse(body, cx, cy + 1, 7 * size, 8 * size)
    c.ellipse(fur, cx, cy + 4, 4.5 * size, 4.5 * size)
    c.ellipse(body, cx, cy - 6, 6 * size, 5.5 * size)
    for sx in (-1, 1):
        c.poly(body, [(cx + sx * 2, cy - 9), (cx + sx * 6, cy - 9), (cx + sx * 5.5, cy - 15), (cx + sx * 2.5, cy - 11)])
        c.poly(P('ear', '#ffb0c0', 8, flat=True), [(cx + sx * 3, cy - 10), (cx + sx * 5, cy - 10), (cx + sx * 4.8, cy - 13.5)])
        if eyes == 'closed':
            c.line(P('pupil', '#140a24', 10, flat=True), cx + sx * 2.7 - 1.5, cy - 6, cx + sx * 2.7 + 1.5, cy - 6, 1.0)
        else:
            c.ellipse(P('eye', '#ff3a5a', 10, flat=True), cx + sx * 2.7, cy - 6, 1.9, 2.1)
            c.ellipse(P('spark', '#ffffff', 11, flat=True), cx + sx * 2.7 - 0.5, cy - 6.7, 0.7, 0.7)
    c.poly(P('fang', '#ffffff', 10, flat=True), [(cx - 2.2, cy - 2), (cx - 1.0, cy - 2), (cx - 1.6, cy + 0.8)])
    c.poly(P('fang', '#ffffff', 10, flat=True), [(cx + 2.2, cy - 2), (cx + 1.0, cy - 2), (cx + 1.6, cy + 0.8)])
    img = c.render()
    if fade < 1:
        a = np.asarray(img).copy(); a[..., 3] = (a[..., 3] * fade).astype(np.uint8); img = Image.fromarray(a, 'RGBA')
    return img


def bat_sheet(color, size=1.0):
    idle = [bat_frame(color, math.sin(i / 6 * 2 * math.pi), size=size) for i in range(6)]
    atk = [bat_frame(color, -0.3, True, lift=14, size=size), bat_frame(color, -0.7, True, lift=10, size=size), bat_frame(color, 0.2, True, lift=4, size=size), bat_frame(color, 0.5, True, lift=8, size=size)]
    hurt = [bat_frame(color, 0.8, eyes='closed', size=size, lift=12), bat_frame(color, -0.5, eyes='closed', size=size, lift=16)]
    death = [bat_frame(color, 0.9 - i * 0.3, eyes='closed', lift=14 - i * 4, size=size, fade=1 - i * 0.2) for i in range(4)]
    return [('idle', 'right', 12, True, idle, 0), ('walk', 'right', 12, True, idle, 0), ('attack', 'right', 12, False, atk, 2), ('hurt', 'right', 10, False, hurt, 0), ('death', 'right', 8, False, death, 0)]


# ------------------------------------------------------------------ wolf (faces right)
def wolf_frame(color, phase=0.0, mode='run', k=1.0, eyes='open', scar=False, fade=1.0, crouch=0.0, jaw=0.0, lean=0.0, belly='#d8d0c0', eye_col='#ffd23a', FW=96, FH=64):
    c = Canvas(FW, FH); P = Pal(c)
    cx, gy = FW // 2, FH - 8
    c.ellipse(P('shadow', '#000000', -9, flat=True), cx, gy + 1, 26 * k, 4.5 * k)
    fur = P('fur', color, 6); fd = P('fur_d', color, 4); fl = P('fur_l', color, 7); bl = P('belly', belly, 6)
    s = math.sin(phase * 2 * math.pi)
    cs = math.cos(phase * 2 * math.pi)
    body_y = gy - 20 * k + crouch * 6 * k + (abs(s) * -2 * k if mode == 'run' else 0)
    bob = (s * 0.8 if mode == 'idle' else 0)
    # legs (2 segments), far legs first
    def leg(hx, side_far, off):
        sw = math.sin(phase * 2 * math.pi + off)
        lift = max(0, math.cos(phase * 2 * math.pi + off))
        if mode == 'run':
            ang = sw * 36
            kneeb = lift * 40
        elif mode == 'leap':
            ang = -40 + 70 * ease(phase) * (1 if off == 0 or off > 3 else 0.6)
            kneeb = 10
        else:
            ang = 0; kneeb = 0
        hx0, hy0 = hx, body_y + 9 * k
        kx = hx0 + math.sin(math.radians(ang)) * 9 * k
        ky = hy0 + math.cos(math.radians(ang)) * 9 * k
        fx = kx + math.sin(math.radians(ang - kneeb)) * 9 * k
        fy = ky + math.cos(math.radians(ang - kneeb)) * 9 * k
        fy = min(fy, gy)
        pid = P('leg_f', color, 3) if side_far else fur
        c.capsule(pid, hx0, hy0, kx, ky, 5 * k, 4 * k)
        c.capsule(pid, kx, ky, fx, fy - 1, 4 * k, 3.4 * k)
        c.ellipse(P('paw', color, 4 if side_far else 5), fx + 1.5 * k, fy - 0.5, 3.4 * k, 2.2 * k)
    leg(cx - 16 * k, True, 3.1)
    leg(cx + 14 * k, True, 0.2)
    # tail
    tail_sw = math.sin(phase * 2 * math.pi * (2 if mode == 'idle' else 1)) * 4
    c.blob(fur, [(cx - 20 * k, body_y + 2), (cx - 30 * k, body_y - 6 + tail_sw), (cx - 38 * k, body_y - 3 + tail_sw * 1.2), (cx - 32 * k, body_y + 3), (cx - 22 * k, body_y + 8)])
    c.blob(fl, [(cx - 30 * k, body_y - 5 + tail_sw), (cx - 38 * k, body_y - 3 + tail_sw * 1.2), (cx - 33 * k, body_y - 1)])
    # body
    c.blob(fur, [(cx - 22 * k, body_y + 4), (cx - 18 * k, body_y - 8), (cx, body_y - 11 + bob), (cx + 16 * k, body_y - 9), (cx + 22 * k, body_y), (cx + 18 * k, body_y + 10), (cx, body_y + 12), (cx - 18 * k, body_y + 11)])
    c.blob(bl, [(cx - 6 * k, body_y + 8), (cx + 6 * k, body_y + 6), (cx + 14 * k, body_y + 9), (cx, body_y + 12)])
    # mane / ridge
    c.blob(fl, [(cx - 16 * k, body_y - 8), (cx - 4 * k, body_y - 12 + bob), (cx + 10 * k, body_y - 11), (cx + 4 * k, body_y - 5), (cx - 8 * k, body_y - 4)])
    # head
    hx = cx + 26 * k
    hy = body_y - 7 * k + lean + bob - crouch * 2
    c.ellipse(fur, hx, hy, 9 * k, 8 * k)
    snout = [(hx + 4 * k, hy - 3 * k), (hx + 17 * k, hy + 0.5 * k), (hx + 17 * k, hy + 4 * k), (hx + 3 * k, hy + 6 * k)]
    c.blob(P('snout', color, 7), snout)
    c.ellipse(P('nose', '#140a24', 10, flat=True), hx + 17.5 * k, hy + 1.5 * k, 2.0 * k, 1.8 * k)
    if jaw > 0:
        c.poly(P('mouth', '#7a2030', 9, flat=True), [(hx + 4 * k, hy + 4 * k), (hx + 17 * k, hy + 3 * k), (hx + 15 * k, hy + (6 + 7 * jaw) * k), (hx + 3 * k, hy + 7 * k)])
        for fx in (hx + 9 * k, hx + 14 * k):
            c.poly(P('fang', '#ffffff', 10, flat=True), [(fx, hy + 3.5 * k), (fx + 1.6, hy + 3.5 * k), (fx + 0.8, hy + 6.2 * k)])
    # ears
    c.poly(fd, [(hx - 5 * k, hy - 6 * k), (hx - 1 * k, hy - 6 * k), (hx - 4 * k, hy - 15 * k)])
    c.poly(fur, [(hx - 1 * k, hy - 7 * k), (hx + 4 * k, hy - 6 * k), (hx + 1 * k, hy - 15 * k)])
    c.poly(P('ear_in', '#ffb0c0', 8, flat=True), [(hx, hy - 7 * k), (hx + 2.8 * k, hy - 6.5 * k), (hx + 1 * k, hy - 12 * k)])
    # eye
    if eyes == 'closed':
        c.line(P('pupil', '#140a24', 10, flat=True), hx + 4 * k, hy - 1.5 * k, hx + 8 * k, hy - 0.5 * k, 1.0)
    else:
        c.ellipse(P('eye', eye_col, 10, flat=True), hx + 6 * k, hy - 1.5 * k, 2.4 * k, 2.0 * k)
        c.ellipse(P('pupil', '#140a24', 10, flat=True), hx + 6.6 * k, hy - 1.5 * k, 1.1 * k, 1.6 * k)
        c.line(P('pupil', '#140a24', 10, flat=True), hx + 3 * k, hy - 5 * k, hx + 9 * k, hy - 2.6 * k, 1.1)
    if scar:
        c.line(P('scar', '#ffffff', 11, flat=True), hx + 1 * k, hy - 5 * k, hx + 8 * k, hy + 4 * k, 0.9)
        c.line(P('scar', '#ffffff', 11, flat=True), cx - 6 * k, body_y - 6 * k, cx + 6 * k, body_y + 6 * k, 0.9)
    # near legs
    leg(cx - 12 * k, False, 0.0)
    leg(cx + 18 * k, False, 3.3)
    img = c.render()
    if fade < 1:
        a = np.asarray(img).copy(); a[..., 3] = (a[..., 3] * fade).astype(np.uint8); img = Image.fromarray(a, 'RGBA')
    return img


def wolf_sheet(color, k=1.0, scar=False, belly='#d8d0c0', eye_col='#ffd23a', FW=96, FH=64):
    kw = dict(k=k, scar=scar, belly=belly, eye_col=eye_col, FW=FW, FH=FH)
    idle = [wolf_frame(color, i / 6, 'idle', **kw) for i in range(6)]
    run = [wolf_frame(color, i / 8, 'run', **kw) for i in range(8)]
    leap = [wolf_frame(color, 0.0, 'idle', crouch=0.9, jaw=0, lean=1, **kw), wolf_frame(color, 0.0, 'idle', crouch=1.0, jaw=0.2, lean=2, **kw), wolf_frame(color, 0.5, 'leap', jaw=0.9, **kw),
            wolf_frame(color, 0.8, 'leap', jaw=1.0, **kw), wolf_frame(color, 1.0, 'leap', jaw=0.6, **kw), wolf_frame(color, 0.0, 'idle', crouch=0.4, **kw)]
    hurt = [wolf_frame(color, 0.0, 'idle', eyes='closed', crouch=0.5, lean=3, jaw=0.6, **kw), wolf_frame(color, 0.0, 'idle', eyes='closed', crouch=0.3, lean=2, **kw)]
    death = [wolf_frame(color, 0.0, 'idle', eyes='closed', crouch=0.5 + i * 0.25, jaw=0.4, fade=1 - max(0, i - 2) * 0.3, **kw) for i in range(5)]
    return [('idle', 'right', 7, True, idle, 0), ('walk', 'right', 12, True, run[::1], 0), ('attack', 'right', 12, False, leap, 3), ('hurt', 'right', 10, False, hurt, 0), ('death', 'right', 8, False, death, 0)]


def build(outdir):
    os.makedirs(outdir, exist_ok=True)
    def save(name, rows, fw, fh):
        sheet_from(rows, fw, fh, os.path.join(outdir, name + '.png'), os.path.join(outdir, name + '.json'))
    save('slime_green', slime_sheet('g', '#5ed26a'), 64, 64)
    save('slime_blue', slime_sheet('b', '#58a8ff', 'frost'), 64, 64)
    save('slime_red', slime_sheet('r', '#ff6a5a', 'spikes', angry=True), 64, 64)
    save('slime_purple', slime_sheet('p', '#b070ff', 'plain', angry=True), 64, 64)
    save('slime_king', slime_sheet('k', '#7ae88a', 'crown', size=2.1, angry=True), 64, 64) if False else None
    save('bat', bat_sheet('#6a4a9a'), 64, 64)
    save('bat_fire', bat_sheet('#d9482e'), 64, 64)
    save('wolf', wolf_sheet('#8a8a98'), 96, 64)
    save('wolf_dark', wolf_sheet('#4a4a5e', eye_col='#ff4a6a'), 96, 64)


if __name__ == '__main__':
    out = sys.argv[1] if len(sys.argv) > 1 else '/tmp/mon'
    build(out)
    # preview
    import glob
    names = ['slime_green', 'slime_red', 'bat', 'wolf']
    sheet = Image.new('RGBA', (8 * 128, 6 * 4 * 128), (70, 110, 70, 255))
    y = 0
    for n in names:
        meta = json.load(open(f'{out}/{n}.json'))
        im = Image.open(f'{out}/{n}.png')
        for r in meta['rows']:
            strip = im.crop((0, r['row'] * meta['frame_h'], r['frames'] * meta['frame_w'], (r['row'] + 1) * meta['frame_h']))
            strip = strip.resize((strip.width * 2, strip.height * 2), Image.NEAREST)
            sheet.alpha_composite(strip, (0, y))
            y += meta['frame_h'] * 2
    sheet.crop((0, 0, 8 * 128, y)).save('/tmp/mon_prev.png')
    print('ok', y)
