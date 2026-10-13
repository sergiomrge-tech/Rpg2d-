"""Quick preview of the ground textures on a small synthetic map (grass, path, plaza, wall, water)."""
import numpy as np
from PIL import Image
import env_ground as eg

T = 64
gw, gh = 24, 16
grid = np.full((gh, gw), 'g', dtype='<U1')
shapes = []
def rect(x0, y0, x1, y1, c):
    shapes.append(('rect', c, (x0, y0, x1, y1))); grid[y0:y1, x0:x1] = c
def path(pts, wd, c):
    shapes.append(('path', c, (pts, wd)))
    # coarse grid marking
    for (x0, y0), (x1, y1) in zip(pts[:-1], pts[1:]):
        for t in np.linspace(0, 1, 40):
            x, y = x0 + (x1 - x0) * t, y0 + (y1 - y0) * t
            for dy in range(-2, 3):
                for dx in range(-2, 3):
                    if (dx * dx + dy * dy) ** 0.5 <= wd / 2 and 0 <= int(y) + dy < gh and 0 <= int(x) + dx < gw:
                        grid[int(y) + dy, int(x) + dx] = c
path([(0, 13), (24, 13)], 2.0, 'd')
shapes.append(('disk', 's', (6, 7, 3.4)))
for yy in range(gh):
    for xx in range(gw):
        if (xx + 0.5 - 6) ** 2 + (yy + 0.5 - 7) ** 2 <= 3.4 ** 2:
            grid[yy, xx] = 's'
# wall: horizontal run on top, then vertical run on the right
path([(1, 2), (23, 2)], 2.5, 'x')
path([(20, 2), (20, 11)], 2.5, 'x')
shapes.append(('rect', 'w', (14, 6, 18, 11)))
grid[6:11, 14:18] = 'w'
img = eg.bake(grid, seed=5, shapes=shapes)
Image.fromarray(img).save('/tmp/tex_test.png')
print(img.shape)
