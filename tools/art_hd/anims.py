"""Animation curves for the HD humanoid. pose(anim, t, view) -> pose dict.

Every animation is authored per view so silhouettes read well in a 3/4 top-down camera.
"""
from __future__ import annotations
import math
from humanoid import default_pose
from core import keys, ease_out, ease_in, ease_in_out

TAU = math.tau

# name: (frames, fps, loop, hit_frame)
ANIMS = {
    'idle': (10, 8, True, -1),
    'walk': (10, 13, True, -1),
    'run': (8, 15, True, -1),
    'attack1': (8, 20, False, 3),
    'attack2': (8, 20, False, 3),
    'attack3': (11, 18, False, 6),
    'cast': (10, 16, False, 5),
    'roll': (8, 18, False, -1),
    'hurt': (5, 14, False, -1),
    'death': (12, 12, False, -1),
}


def mirror_arm(a):
    return (-a[0], -a[1], a[2], a[3])


def legs_side(P, ph, amp, bend):
    for key, off in (('leg_b', 0.0), ('leg_a', math.pi)):
        p = ph + off
        th = amp * math.sin(p)
        kb = bend * max(0.0, math.cos(p)) ** 1.4 + 6
        P[key] = (th, th - kb, 1.0, 1.0)


def legs_front(P, ph, amp, view):
    # foot moving toward the camera drops lower; lifted leg foreshortens the thigh
    for key, off, sx in (('leg_b', 0.0, -1), ('leg_a', math.pi, 1)):
        p = ph + off
        lift = max(0.0, math.cos(p))
        stride = math.sin(p) * (1 if view == 'down' else -1)
        P[key] = (sx * 3.0, sx * 1.5, 1.0 - 0.45 * lift * amp + 0.06 * stride * amp,
                  1.0 + 0.16 * stride * amp - 0.12 * lift * amp)


def arms_walk(P, ph, amp, view):
    if view == 'side':
        for key, off in (('arm_b', math.pi), ('arm_a', 0.0)):
            s = math.sin(ph + off)
            P[key] = (amp * 24 * s, amp * 24 * s + 18 + 10 * amp * max(0, s), 1.0, 1.0)
    else:
        sgn = 1 if view == 'down' else -1
        for key, off, sx in (('arm_b', math.pi, -1), ('arm_a', 0.0, 1)):
            s = math.sin(ph + off) * sgn
            sx2 = sx if view == 'down' else -sx
            P[key] = (sx2 * (9 + 3 * amp), sx2 * (6 - 2 * s * amp), 1.0 - 0.12 * max(0, s) * amp,
                      1.0 - 0.18 * max(0, s) * amp)


def rest_arms(P, view, breathe=0.0):
    if view == 'side':
        P['arm_a'] = (-6 + breathe, 10 + breathe, 1, 1)
        P['arm_b'] = (8 - breathe, 26 - breathe, 1, 1)
    elif view == 'down':
        P['arm_a'] = (10 + breathe, 4 + breathe, 1, 1)
        P['arm_b'] = (-10 - breathe, -4 - breathe, 1, 1)
    else:
        P['arm_a'] = (-10 - breathe, -4 - breathe, 1, 1)
        P['arm_b'] = (10 + breathe, 4 + breathe, 1, 1)


def rest_wpn(P, view):
    # sword held low, blade angled outward and slightly up
    if view == 'side':
        P['wpn'] = 152
        P['wpn_front'] = True
    elif view == 'down':
        P['wpn'] = 205
        P['wpn_front'] = True
    else:
        P['wpn'] = 160
        P['wpn_front'] = True


def legs_rest(P, view):
    if view == 'side':
        P['leg_a'] = (-3, -5, 1, 1)
        P['leg_b'] = (4, 2, 1, 1)
    elif view == 'down':
        P['leg_a'] = (3, 1.5, 1, 1)
        P['leg_b'] = (-3, -1.5, 1, 1)
    else:
        P['leg_a'] = (-3, -1.5, 1, 1)
        P['leg_b'] = (3, 1.5, 1, 1)


def pose(anim, t, view):
    P = default_pose()
    legs_rest(P, view)
    rest_arms(P, view)
    rest_wpn(P, view)
    side = view == 'side'
    if anim == 'idle':
        b = math.sin(t * TAU)
        P['y'] = 0.0
        P['hip'] += 0.6 * b
        P['sq'] = 1.0 - 0.012 * b
        P['hdy'] = 0.5 * b
        rest_arms(P, view, breathe=2.0 * b)
        P['scarf'] = t
        P['tilt'] = 1.2 * math.sin(t * TAU + 0.6)
        if 0.62 < t < 0.74:
            P['eyes'] = 'closed'
        P['look_dx'] = 0.4 * math.sin(t * TAU * 0.5)
    elif anim in ('walk', 'run'):
        run = anim == 'run'
        ph = t * TAU
        amp = 1.0 if not run else 1.35
        P['hip'] += -abs(math.sin(ph)) * (1.6 if not run else 3.2) + (0.8 if not run else 2.4)
        P['lean'] = (4 if not run else 11) if side else 0
        if not side:
            P['hdy'] = 0.6 if run and view == 'down' else 0
            P['sq'] = 1.0 - 0.02 * math.cos(2 * ph)
        if side:
            legs_side(P, ph, 28 if not run else 40, 42 if not run else 70)
        else:
            legs_front(P, ph, amp, view)
        arms_walk(P, ph, amp, view)
        if run and side:
            P['arm_b'] = (P['arm_b'][0] * 1.2 - 10, P['arm_b'][1] + 40, 1, 1)
            P['arm_a'] = (P['arm_a'][0] * 1.2 - 10, P['arm_a'][1] + 40, 1, 1)
        P['scarf'] = t * 2
        P['tilt'] = 1.5 * math.sin(ph) if not side else 0
        P['wpn'] = P['wpn'] + (12 * math.sin(ph) if side else 6 * math.sin(ph))
        if run:
            P['mouth'] = 'open' if t < 0.5 else 'n'
    elif anim in ('attack1', 'attack2'):
        rev = anim == 'attack2'
        P['scarf'] = t * 1.5
        P['mouth'] = 'grit' if 0.25 < t < 0.75 else 'n'
        P['eyes'] = 'open'
        if side:
            if not rev:
                kf_a1 = [(0, 30), (0.22, -55), (0.42, 105), (0.6, 80), (1, 30)]
                kf_a2 = [(0, 60), (0.22, -20), (0.42, 100), (0.6, 70), (1, 60)]
                kf_w = [(0, 140), (0.22, 205), (0.42, 85), (0.6, 30), (1, 130)]
            else:
                kf_a1 = [(0, 60), (0.22, 120), (0.42, 40), (0.6, 20), (1, 30)]
                kf_a2 = [(0, 80), (0.22, 150), (0.42, 70), (0.6, 30), (1, 60)]
                kf_w = [(0, 60), (0.22, 30), (0.42, 140), (0.6, 175), (1, 130)]
            P['arm_b'] = (keys(t, kf_a1), keys(t, kf_a2), 1, 1)
            P['wpn'] = keys(t, kf_w)
            P['lean'] = keys(t, [(0, 2), (0.22, -8), (0.42, 14), (0.7, 8), (1, 2)])
            P['x'] = keys(t, [(0, 0), (0.22, -2), (0.45, 5), (1, 0)])
            P['arm_a'] = (keys(t, [(0, -6), (0.22, 30), (0.42, -40), (1, -6)]), keys(t, [(0, 10), (0.22, 50), (0.42, -10), (1, 10)]), 1, 1)
            P['leg_b'] = (keys(t, [(0, 4), (0.3, 20), (0.6, 22), (1, 4)]), keys(t, [(0, 2), (0.3, 0), (0.6, 4), (1, 2)]), 1, 1)
            P['leg_a'] = (keys(t, [(0, -3), (0.3, -18), (1, -3)]), keys(t, [(0, -5), (0.3, -28), (1, -5)]), 1, 1)
            P['wpn_front'] = True
        else:
            d = 1 if view == 'down' else -1
            # horizontal sweep across the body; blade points away from the camera in 'up'
            if not rev:
                kf_w = [(0, 200), (0.22, 230), (0.42, 100), (0.6, 50), (1, 200)] if view == 'down' else \
                       [(0, 160), (0.22, 120), (0.42, 220), (0.6, 260), (1, 160)]
                kf_a1 = [(0, -10), (0.22, -70), (0.42, 40), (0.6, 50), (1, -10)] if view == 'down' else \
                        [(0, 10), (0.22, 80), (0.42, -30), (0.6, -50), (1, 10)]
            else:
                kf_w = [(0, 50), (0.22, 30), (0.42, 210), (0.6, 250), (1, 200)] if view == 'down' else \
                       [(0, 260), (0.22, 280), (0.42, 150), (0.6, 110), (1, 160)]
                kf_a1 = [(0, 50), (0.22, 70), (0.42, -50), (0.6, -70), (1, -10)] if view == 'down' else \
                        [(0, -50), (0.22, -70), (0.42, 40), (0.6, 60), (1, 10)]
            a1 = keys(t, kf_a1)
            P['arm_b'] = (a1, a1 * 1.15, keys(t, [(0, 1), (0.42, 0.8), (1, 1)]), keys(t, [(0, 1), (0.42, 0.7), (1, 1)]))
            P['wpn'] = keys(t, kf_w)
            P['wscale'] = keys(t, [(0, 1), (0.42, 0.85 if view == 'down' else 0.8), (1, 1)])
            P['y'] = keys(t, [(0, 0), (0.42, 3 * d), (1, 0)])
            P['tilt'] = keys(t, [(0, 0), (0.22, -4), (0.42, 5), (1, 0)]) * (1 if not rev else -1)
            P['lean'] = keys(t, [(0, 0), (0.22, -5), (0.42, 7), (1, 0)]) * (1 if not rev else -1)
            P['wpn_front'] = view == 'down' or (0.18 < t < 0.3)
            if view == 'up':
                P['arms_behind'] = 0.3 < t < 0.75
    elif anim == 'attack3':
        P['scarf'] = t * 2
        P['mouth'] = 'open' if t > 0.35 else 'grit'
        jump = keys(t, [(0, 0), (0.18, 2), (0.42, -12), (0.55, 0), (0.62, 2), (1, 0)])
        P['y'] = jump
        P['sq'] = keys(t, [(0, 1), (0.18, 0.9), (0.3, 1.08), (0.55, 1.0), (0.6, 0.86), (0.75, 1.0), (1, 1)])
        if side:
            P['arm_b'] = (keys(t, [(0, 30), (0.18, 10), (0.42, 175), (0.56, 80), (0.75, 60), (1, 30)]),
                          keys(t, [(0, 60), (0.18, 40), (0.42, 185), (0.56, 70), (0.75, 50), (1, 60)]), 1, 1)
            P['arm_a'] = (keys(t, [(0, -6), (0.42, 160), (0.56, 60), (1, -6)]), keys(t, [(0, 10), (0.42, 170), (0.56, 60), (1, 10)]), 1, 1)
            P['wpn'] = keys(t, [(0, 130), (0.18, 150), (0.42, 200), (0.56, 75), (0.62, 60), (1, 130)])
            P['lean'] = keys(t, [(0, 0), (0.18, -6), (0.42, -10), (0.56, 22), (0.75, 16), (1, 0)])
            P['x'] = keys(t, [(0, 0), (0.42, 3), (0.56, 7), (1, 0)])
            P['leg_b'] = (keys(t, [(0, 4), (0.42, 30), (0.56, 26), (1, 4)]), keys(t, [(0, 2), (0.42, -20), (0.56, 0), (1, 2)]), 1, 1)
            P['leg_a'] = (keys(t, [(0, -3), (0.42, -10), (0.56, -24), (1, -3)]), keys(t, [(0, -5), (0.42, -50), (0.56, -30), (1, -5)]), 1, 1)
        else:
            dn = view == 'down'
            sx = -1 if dn else 1
            up = 180
            P['arm_b'] = (keys(t, [(0, sx * 10), (0.18, sx * 30), (0.42, sx * 170), (0.56, sx * 10), (1, sx * 10)]),
                          keys(t, [(0, sx * 6), (0.18, sx * 40), (0.42, sx * 175), (0.56, sx * 2), (1, sx * 6)]),
                          1, keys(t, [(0, 1), (0.42, 1), (0.56, 0.6), (1, 1)]))
            P['arm_a'] = (keys(t, [(0, -sx * 10), (0.42, -sx * 160), (0.56, -sx * 12), (1, -sx * 10)]),
                          keys(t, [(0, -sx * 4), (0.42, -sx * 170), (0.56, -sx * 4), (1, -sx * 4)]), 1,
                          keys(t, [(0, 1), (0.56, 0.6), (1, 1)]))
            if dn:
                P['wpn'] = keys(t, [(0, 205), (0.18, 200), (0.42, up + 2), (0.5, 90), (0.56, 2), (0.75, 4), (1, 205)])
                P['wscale'] = keys(t, [(0, 1), (0.42, 1), (0.56, 0.75), (0.8, 0.8), (1, 1)])
                P['wpn_front'] = not (0.3 < t < 0.48)
            else:
                P['wpn'] = keys(t, [(0, 160), (0.18, 160), (0.42, 2), (0.5, 90), (0.56, up), (0.75, up), (1, 160)])
                P['wscale'] = keys(t, [(0, 1), (0.42, 0.8), (0.56, 1.05), (1, 1)])
                P['wpn_front'] = t < 0.46
            P['hdy'] = keys(t, [(0, 0), (0.56, 2), (1, 0)])
    elif anim == 'cast':
        P['scarf'] = t * 2
        P['eyes'] = 'open' if t < 0.4 else 'wide'
        P['mouth'] = 'n' if t < 0.4 else 'open'
        g = keys(t, [(0, 0), (0.35, 0.5), (0.5, 1.0), (0.7, 0.7), (1, 0)])
        P['glow'] = (0.45, 0.85, 1.0, g) if g > 0.05 else None
        if side:
            P['arm_b'] = (keys(t, [(0, 8), (0.35, -30), (0.5, 92), (0.75, 85), (1, 8)]),
                          keys(t, [(0, 26), (0.35, 10), (0.5, 95), (0.75, 92), (1, 26)]), 1, 1)
            P['arm_a'] = (keys(t, [(0, -6), (0.35, 40), (0.5, -30), (1, -6)]), keys(t, [(0, 10), (0.35, 80), (0.5, -10), (1, 10)]), 1, 1)
            P['lean'] = keys(t, [(0, 0), (0.35, -8), (0.5, 9), (0.75, 6), (1, 0)])
            P['wpn'] = keys(t, [(0, 120), (0.35, 160), (0.5, 100), (1, 120)])
            P['wpn_front'] = False
        else:
            dn = view == 'down'
            sx = -1 if dn else 1
            P['arm_b'] = (keys(t, [(0, sx * 10), (0.35, sx * 60), (0.5, sx * 20), (0.75, sx * 20), (1, sx * 10)]),
                          keys(t, [(0, sx * 6), (0.35, sx * 120), (0.5, -sx * 40), (0.75, -sx * 40), (1, sx * 6)]),
                          keys(t, [(0, 1), (0.5, 0.75), (1, 1)]), keys(t, [(0, 1), (0.5, 0.65), (1, 1)]))
            P['lean'] = 0
            P['hdy'] = keys(t, [(0, 0), (0.35, -1), (0.5, 1), (1, 0)])
            P['wpn_front'] = not dn
            P['arms_behind'] = not dn and t > 0.4
        P['x'] = keys(t, [(0, 0), (0.35, -1.5), (0.5, 1.5), (1, 0)]) if side else 0
    elif anim == 'roll':
        P['eyes'] = 'closed'
        P['scarf'] = t * 3
        tuck = keys(t, [(0, 0), (0.15, 1), (0.85, 1), (1, 0)])
        P['hip'] = -31 + 12 * tuck
        P['hdy'] = 6 * tuck
        if side:
            P['rot'] = keys(t, [(0, 0), (0.12, 10), (0.85, 360), (1, 360)], ease=lambda u: u)
            P['leg_b'] = (60 * tuck + 4, -30 * tuck + 2, 1, 1)
            P['leg_a'] = (50 * tuck - 3, -40 * tuck - 5, 1, 1)
            P['arm_b'] = (60 * tuck + 8, 140 * tuck + 26 * (1 - tuck), 1, 1)
            P['arm_a'] = (50 * tuck - 6, 120 * tuck, 1, 1)
            P['wpn'] = 120 + 60 * tuck
            P['lean'] = 30 * tuck
        else:
            dn = view == 'down'
            P['sq'] = 1 - 0.25 * tuck
            P['rot'] = 8 * math.sin(t * TAU) * tuck
            P['y'] = 0
            for key, sx in (('leg_a', 1 if dn else -1), ('leg_b', -1 if dn else 1)):
                P[key] = (sx * (3 + 25 * tuck), sx * (1.5 - 10 * tuck), 1 - 0.45 * tuck, 1 - 0.2 * tuck)
            for key, sx in (('arm_a', 1 if dn else -1), ('arm_b', -1 if dn else 1)):
                P[key] = (sx * (10 + 30 * tuck), sx * (4 - 60 * tuck), 1, 1 - 0.3 * tuck)
            P['wpn_front'] = dn
    elif anim == 'hurt':
        k = keys(t, [(0, 0), (0.25, 1), (1, 0)], ease=ease_out)
        P['eyes'] = 'squint'
        P['mouth'] = 'grit'
        P['tilt'] = -8 * k if view != 'side' else -10 * k
        P['lean'] = -12 * k if side else 0
        P['x'] = -4 * k if side else 0
        P['y'] = -2 * k if view == 'down' else (2 * k if view == 'up' else 0)
        P['sq'] = 1 - 0.06 * k
        P['hdy'] = -1 * k
        if side:
            P['arm_b'] = (8 + 30 * k, 26 + 60 * k, 1, 1)
            P['arm_a'] = (-6 - 30 * k, 10 - 20 * k, 1, 1)
        P['scarf'] = t
    elif anim == 'death':
        P['eyes'] = 'closed' if t > 0.5 else 'squint'
        P['mouth'] = 'open' if t < 0.5 else 'n'
        kneel = keys(t, [(0, 0), (0.3, 1), (1, 1)])
        fall = keys(t, [(0, 0), (0.35, 0), (0.7, 1), (1, 1)], ease=ease_in)
        bounce = keys(t, [(0, 0), (0.7, 0), (0.78, -2), (0.86, 0), (1, 0)])
        P['hip'] = -31 + 10 * kneel
        P['scarf'] = t * 0.5
        if side:
            P['leg_b'] = (40 * kneel + 4, -70 * kneel + 2, 1, 1)
            P['leg_a'] = (10 * kneel - 3, -80 * kneel - 5, 1, 1)
            P['rot'] = -88 * fall
            P['y'] = bounce
            P['x'] = -6 * fall
            P['arm_b'] = (8 + 120 * fall, 26 + 130 * fall, 1, 1)
            P['arm_a'] = (-6 + 100 * fall, 10 + 120 * fall, 1, 1)
            P['wpn'] = 120 + 60 * fall
        else:
            P['sq'] = 1 - 0.1 * kneel
            P['rot'] = 82 * fall * (1 if view == 'down' else -1)
            P['y'] = bounce
            P['tilt'] = 10 * kneel
            for key, sx in (('leg_a', 1), ('leg_b', -1)):
                P[key] = (sx * 6, sx * 2, 1 - 0.5 * kneel, 1)
        P['hdy'] = 2 * kneel
    return P
