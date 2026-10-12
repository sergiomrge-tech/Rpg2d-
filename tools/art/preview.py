import sys, math
from PIL import Image
sys.path.insert(0, '.')
from humanoid import *

def walk_pose(t, side=False):
    s = math.sin(t * 2 * math.pi)
    c = math.cos(t * 2 * math.pi)
    p = Pose()
    p.bob = 1 if abs(s) < 0.45 else 0
    if side:
        p.leg_l, p.leg_r = s * 38, -s * 38
        p.knee_l = max(0, math.cos(t * 2 * math.pi + 1.2)) * 40
        p.knee_r = max(0, math.cos(t * 2 * math.pi + 1.2 + math.pi)) * 40
        p.arm_l, p.arm_r = -s * 34, s * 34
        p.elbow_l, p.elbow_r = 18 + max(0, s) * 20, 18 + max(0, -s) * 20
    else:
        p.leg_l, p.leg_r = s, -s
        p.lift_l, p.lift_r = max(0, -s) * 3.2, max(0, s) * 3.2
        p.arm_l, p.arm_r = 6 - s * 8, 6 + s * 8
    p.sway = math.sin(t * 2 * math.pi - 1)
    return p

rig = Rig(Look())
sheet = Image.new('RGBA', (128 * 8, 128 * 3), (70, 110, 70, 255))
for row, view in enumerate(['down', 'left', 'up']):
    for i in range(8):
        img = rig.draw(view, walk_pose(i / 8, side=(view == 'left'))).render()
        sheet.alpha_composite(img.resize((128, 128), Image.NEAREST), (i * 128, row * 128))
sheet.save('/tmp/hero_walk.png')
print('ok')
