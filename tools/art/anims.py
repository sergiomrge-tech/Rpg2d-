"""Humanoid animation library -> spritesheet + manifest."""
import math, json, os, sys
from PIL import Image
sys.path.insert(0, os.path.dirname(__file__))
from humanoid import Rig, Look, Pose, FW, FH


def smooth(t):
    t = max(0.0, min(1.0, t))
    return t * t * (3 - 2 * t)


def lerp(a, b, t):
    return a + (b - a) * t


def keyframes(keys, t):
    """keys: list of (time, dict). Linear in dict values with smoothstep easing between keys."""
    if t <= keys[0][0]:
        return dict(keys[0][1])
    for (t0, k0), (t1, k1) in zip(keys, keys[1:]):
        if t <= t1:
            u = smooth((t - t0) / (t1 - t0))
            out = {}
            for n in set(k0) | set(k1):
                out[n] = lerp(k0.get(n, 0), k1.get(n, 0), u)
            return out
    return dict(keys[-1][1])


VIEWS = ['down', 'left', 'up']


# ---------------------------------------------------------------- idle / walk
def idle_pose(i, n, view):
    t = i / n
    p = Pose()
    br = math.sin(t * 2 * math.pi)
    p.bob = 1 if br > 0.3 else 0
    p.head_dy = 0
    p.sway = math.sin(t * 2 * math.pi - 0.8) * 0.5
    if view == 'left':
        p.arm_l, p.arm_r = 8 + br * 2, -6 - br * 2
        p.elbow_l, p.elbow_r = 12, 10
        p.leg_l, p.leg_r = 4, -4
    else:
        p.arm_l, p.arm_r = 5 + br * 1.5, 5 + br * 1.5
    if i == n - 1:
        p.eyes = 'closed'
    return p


def walk_pose(i, n, view, run=False):
    t = i / n
    s = math.sin(t * 2 * math.pi)
    c = math.cos(t * 2 * math.pi)
    p = Pose()
    amp = 1.35 if run else 1.0
    p.bob = 1 if abs(s) < 0.5 else 0
    p.sway = math.sin(t * 2 * math.pi - 1.0) * (1.4 if run else 1.0)
    if view == 'left':
        p.leg_l, p.leg_r = s * 40 * amp, -s * 40 * amp
        p.knee_l = max(0, math.cos(t * 2 * math.pi + 1.2)) * 42 * amp
        p.knee_r = max(0, math.cos(t * 2 * math.pi + 1.2 + math.pi)) * 42 * amp
        p.arm_l, p.arm_r = -s * 36 * amp, s * 36 * amp
        p.elbow_l, p.elbow_r = 20 + max(0, s) * 24, 20 + max(0, -s) * 24
        p.lean = -1.0 if run else 0
    else:
        p.leg_l, p.leg_r = s, -s
        p.lift_l, p.lift_r = max(0, -s) * 3.4 * amp, max(0, s) * 3.4 * amp
        p.arm_l, p.arm_r = 6 - s * 9, 6 + s * 9
    return p


# ---------------------------------------------------------------- attacks
# Keys are side-view semantics (angles from straight down, + = forward). Front/back reuse them outward.
ATTACKS = {
    'attack1': {  # overhead-diagonal slash
        'n': 6, 'fps': 20, 'hit': 3,
        'keys': [
            (0.00, dict(weapon=150, arm=140, elbow=30, arm2=20, lean=0, crouch=0, step=0)),
            (0.22, dict(weapon=235, arm=205, elbow=40, arm2=-10, lean=2.0, crouch=1, step=-8)),
            (0.40, dict(weapon=230, arm=200, elbow=40, arm2=-10, lean=2.0, crouch=1, step=-8)),
            (0.58, dict(weapon=95, arm=95, elbow=0, arm2=30, lean=-3.0, crouch=1, step=22)),
            (0.76, dict(weapon=40, arm=50, elbow=-8, arm2=40, lean=-4.0, crouch=1, step=26)),
            (1.00, dict(weapon=25, arm=20, elbow=10, arm2=10, lean=-1.0, crouch=0, step=8)),
        ]},
    'attack2': {  # rising reverse slash
        'n': 6, 'fps': 20, 'hit': 3,
        'keys': [
            (0.00, dict(weapon=25, arm=20, elbow=10, arm2=10, lean=-1.0, crouch=0, step=8)),
            (0.22, dict(weapon=310, arm=285, elbow=30, arm2=-20, lean=1.5, crouch=2, step=-10)),
            (0.40, dict(weapon=305, arm=280, elbow=30, arm2=-20, lean=1.5, crouch=2, step=-10)),
            (0.58, dict(weapon=110, arm=100, elbow=-5, arm2=40, lean=-3.5, crouch=1, step=24)),
            (0.76, dict(weapon=170, arm=150, elbow=-15, arm2=50, lean=-4.0, crouch=0, step=26)),
            (1.00, dict(weapon=30, arm=25, elbow=10, arm2=10, lean=-1.0, crouch=0, step=8)),
        ]},
    'attack3': {  # heavy two-stage overhead smash with lunge
        'n': 8, 'fps': 18, 'hit': 5,
        'keys': [
            (0.00, dict(weapon=30, arm=20, elbow=10, arm2=10, lean=0, crouch=0, step=0)),
            (0.25, dict(weapon=200, arm=185, elbow=35, arm2=150, lean=2.5, crouch=2, step=-12)),
            (0.45, dict(weapon=225, arm=200, elbow=45, arm2=160, lean=3.0, crouch=3, step=-14)),
            (0.62, dict(weapon=80, arm=90, elbow=0, arm2=70, lean=-4.5, crouch=2, step=28)),
            (0.78, dict(weapon=10, arm=40, elbow=-10, arm2=40, lean=-5.0, crouch=3, step=34)),
            (1.00, dict(weapon=25, arm=20, elbow=10, arm2=10, lean=-1.0, crouch=0, step=10)),
        ]},
    'cast': {
        'n': 6, 'fps': 14, 'hit': 3,
        'keys': [
            (0.00, dict(weapon=-1, arm=10, elbow=10, arm2=10, lean=0, crouch=0, step=0, glow=0)),
            (0.30, dict(weapon=-1, arm=130, elbow=40, arm2=130, lean=1.0, crouch=1, step=-4, glow=1.5)),
            (0.60, dict(weapon=-1, arm=170, elbow=20, arm2=170, lean=1.5, crouch=0, step=-4, glow=3)),
            (0.78, dict(weapon=-1, arm=95, elbow=0, arm2=95, lean=-3.0, crouch=1, step=14, glow=3.5)),
            (1.00, dict(weapon=-1, arm=40, elbow=10, arm2=40, lean=-1.0, crouch=0, step=6, glow=1)),
        ]},
    'roll': {
        'n': 6, 'fps': 24, 'hit': 0,
        'keys': [
            (0.00, dict(weapon=-1, arm=15, elbow=60, arm2=15, lean=-1, crouch=3, step=0)),
            (0.50, dict(weapon=-1, arm=10, elbow=100, arm2=10, lean=-2, crouch=8, step=0)),
            (1.00, dict(weapon=-1, arm=15, elbow=60, arm2=15, lean=-1, crouch=3, step=0)),
        ]},
    'hurt': {
        'n': 2, 'fps': 10, 'hit': 0,
        'keys': [
            (0.00, dict(weapon=-1, arm=70, elbow=30, arm2=60, lean=3.0, crouch=1, step=-6)),
            (1.00, dict(weapon=-1, arm=60, elbow=40, arm2=50, lean=2.0, crouch=2, step=-4)),
        ]},
}


def attack_pose(name, i, view, has_weapon=True, weapon='sword'):
    spec = ATTACKS[name]
    n = spec['n']
    t = i / (n - 1)
    k = keyframes(spec['keys'], t)
    p = Pose()
    weapon_on = k['weapon'] >= 0 and has_weapon
    p.sway = math.sin(t * 6.0 - 1.5) * 0.9
    p.glow = k.get('glow', 0)
    if name == 'hurt':
        p.eyes = 'hurt'; p.mouth = 'open'
    elif name == 'cast':
        p.mouth = 'open' if 0.3 < t < 0.9 else 'neutral'
        p.eyes = 'wide' if 0.5 < t < 0.85 else 'open'
    elif name == 'roll':
        p.eyes = 'closed'
    elif t > 0.5 and t < 0.85:
        p.mouth = 'shout' if name == 'attack3' else 'open'
    p.crouch = int(round(k['crouch']))
    p.lean = k['lean'] if view == 'left' else k['lean'] * 0.3
    p.bob = 0
    step = k['step']
    if view == 'left':
        p.leg_l = step * 0.9 - 4
        p.leg_r = -step * 0.6 + 4
        p.knee_l, p.knee_r = max(0, step * 0.5), max(0, -step * 0.2 + 12)
        p.arm_l, p.elbow_l = k['arm'], k['elbow']
        p.arm_r, p.elbow_r = k['arm2'], 15
        p.weapon_grip = 'l'
    else:
        p.leg_l = 0.5 + step * 0.01
        p.leg_r = -0.4
        p.arm_r, p.elbow_r = k['arm'] - 6, k['elbow']
        p.arm_l, p.elbow_l = k['arm2'] - 6, 15
        p.weapon_grip = 'r'
    if weapon_on:
        p.weapon_ang = k['weapon']
        p.weapon_len = 19 if weapon == 'sword' else 22
    return p


def render(rig, view, pose):
    img = rig.draw(view, pose).render()
    return img


ANIMS = [
    # name, frames, fps, loop
    ('idle', 6, 6, True), ('walk', 8, 12, True), ('run', 8, 16, True),
    ('attack1', 6, 20, False), ('attack2', 6, 20, False), ('attack3', 8, 18, False),
    ('cast', 6, 14, False), ('roll', 6, 24, False), ('hurt', 2, 10, False),
]


def build_sheet(look: Look, out_png: str, out_json: str, full=True):
    rig = Rig(look)
    anims = ANIMS if full else [a for a in ANIMS if a[0] in ('idle', 'walk')]
    maxf = max(a[1] for a in anims)
    rows = []
    for name, n, fps, loop in anims:
        for v in VIEWS:
            rows.append((name, v, n, fps, loop))
    sheet = Image.new('RGBA', (maxf * FW, len(rows) * FH), (0, 0, 0, 0))
    meta = {'frame_w': FW, 'frame_h': FH, 'rows': []}
    for r, (name, v, n, fps, loop) in enumerate(rows):
        for i in range(n):
            if name == 'idle':
                p = idle_pose(i, n, v)
            elif name == 'walk':
                p = walk_pose(i, n, v)
            elif name == 'run':
                p = walk_pose(i, n, v, run=True)
            else:
                p = attack_pose(name, i, v, has_weapon=look.weapon != 'none', weapon=look.weapon)
            img = render(rig, v, p)
            sheet.alpha_composite(img, (i * FW, r * FH))
        hit = ATTACKS[name]['hit'] if name in ATTACKS else 0
        meta['rows'].append({'anim': name, 'dir': v, 'row': r, 'frames': n, 'fps': fps, 'loop': loop, 'hit': hit})
    sheet.save(out_png)
    with open(out_json, 'w') as f:
        json.dump(meta, f)
    return sheet


if __name__ == '__main__':
    sheet = build_sheet(Look(), '/tmp/kai_sheet.png', '/tmp/kai_sheet.json')
    # contact sheet preview: all attack frames at 2x
    print(sheet.size)
