"""Places the optional insectoid encounters on free tiles of every map (run after tools/art_hd/maps.py).
Writes godot/data/insect_spawns.json. Deterministic (seeded)."""
import json
import os
import random

ROOT = os.path.join(os.path.dirname(__file__), '..')
D = json.load(open(os.path.join(ROOT, 'godot', 'data', 'demons.json')))
M = {
    'velmoor': [('mantis_reaver', 5), ('moth_hexer', 5), ('termite_burrower', 6), ('moth_oracle', 8)],
    'valemont': [('roach_plaguebearer', 8), ('spike_beetle', 8)],
    'kharis': [('scarab_brute', 9), ('vespa_lancer', 9), ('cicada_screecher', 10), ('termite_burrower', 10), ('scarab_colossus', 12)],
    'mines': [('ant_guard', 11), ('spike_beetle', 11), ('roach_plaguebearer', 12), ('brood_tyrant', 14)],
    'mirewail': [('roach_plaguebearer', 13), ('dragonfly_skirmisher', 13), ('moth_hexer', 13), ('mantis_reaver', 14)],
    'peaks': [('vespa_lancer', 15), ('dragonfly_skirmisher', 15), ('cicada_screecher', 15), ('queen_vespara', 18)],
    'castle': [('mantis_reaver', 18), ('spike_beetle', 18), ('ant_guard', 18)],
    'wastelands': [('scarab_brute', 20), ('vespa_lancer', 20), ('mantis_high_reaper', 23)],
    'citadel': [('dragonfly_skirmisher', 24), ('cicada_screecher', 24)],
}
out = {}
rng = random.Random(5)
for m, lst in M.items():
    md = json.load(open(os.path.join(ROOT, 'godot', 'assets', 'Maps', m + '.json')))
    w, h, t = md['w'], md['h'], md['tile']
    bl = md['blocked']
    anchors = [(md['playerX'], md['playerY'])] + [(e['x'], e['y']) for e in md['exits']] + [(n['x'], n['y']) for n in md['npcs']]
    taken = [(s['x'], s['y']) for s in md['spawns']]

    def free(tx, ty, r):
        for dy in range(-r, r + 1):
            for dx in range(-r, r + 1):
                x, y = tx + dx, ty + dy
                if not (0 <= x < w and 0 <= y < h) or bl[y * w + x] == '1':
                    return False
        return True
    res = []
    for kind, lv in lst:
        boss = D[kind]['boss']
        for _ in range(6000):
            tx, ty = rng.randrange(4, w - 4), rng.randrange(4, h - 4)
            px, py = (tx + .5) * t, (ty + .5) * t
            if not free(tx, ty, 3 if boss else 2):
                continue
            if any(abs(px - a) < 14 * t and abs(py - b) < 14 * t for a, b in anchors):
                continue
            if any(((px - a) ** 2 + (py - b) ** 2) ** .5 < (9 if boss else 5) * t for a, b in taken):
                continue
            res.append(dict(kind=kind, x=round(px), y=round(py), level=lv))
            taken.append((px, py))
            break
        else:
            print('no spot', m, kind)
    out[m] = res
json.dump(out, open(os.path.join(ROOT, 'godot', 'data', 'insect_spawns.json'), 'w'), indent=1)
print({m: len(v) for m, v in out.items()})
