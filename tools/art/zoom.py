import sys
from PIL import Image
sys.path.insert(0, '.')
from humanoid import *
from preview import walk_pose
rig = Rig(Look())
sheet = Image.new('RGBA', (3 * 512, 512), (70, 110, 70, 255))
for i, v in enumerate(['down', 'left', 'up']):
    img = rig.draw(v, walk_pose(0.12, v == 'left')).render().crop((8, 0, 56, 64)).resize((384, 512), Image.NEAREST)
    sheet.alpha_composite(img, (i * 512, 0))
sheet.save('/tmp/hero_zoom.png')
