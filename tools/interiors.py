"""Interior rooms for the main buildings (guild, tavern, shops...).

`python3 tools/interiors.py` writes godot/assets/Maps/int_*.json and patches the outdoor maps (village, valemont):
  * adds a door exit in front of every building that has an interior (exit.ax/ay = where the hero reappears outside)
  * moves the shopkeepers / guild staff inside (their NPC entries leave the street)
  * writes godot/data/interiors.json (npc id -> interior map, used by the objective compass)
Idempotent: safe to run again after regenerating the maps.
"""
import json
import os

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
MAPS = os.path.join(ROOT, 'godot', 'assets', 'Maps')
T = 64


def F(k, x, y, w=1.0, **kw):
    d = dict(k=k, x=round(x * T, 1), y=round(y * T, 1), w=w)
    d.update(kw)
    return d


def D(k, x, y, **kw):
    d = dict(k=k, x=round(x * T, 1), y=round(y * T, 1))
    d.update(kw)
    return d


def N(id_, look, x, y, facing='down'):
    return dict(id=id_, look=look, x=round(x * T, 1), y=round(y * T, 1), facing=facing)


def room(name, title, style, w, h, outdoor, furniture, decor, npcs, kind):
    return dict(name=name, title=title, style=style, w=w, h=h, outdoor=outdoor, furniture=furniture, decor=decor, npcs=npcs, kind=kind)


def windows(xs):
    return [D('window', x, 0.45) for x in xs]


def tavern(name, outdoor, keeper_id, keeper_look, title):
    W, H = 28, 15
    f = [
        F('fireplace', 5.5, 3.95, 3),
        F('counter', 21.5, 5.3, 7, deco='mugs'),
        F('barrel', 16.9, 4.4), F('barrel', 15.9, 4.9),
        F('door_room', 8.4, 3.7, 1.1, act='rooms'), F('door_room', 11.0, 3.7, 1.1, act='rooms'), F('door_room', 13.6, 3.7, 1.1, act='rooms'),
        F('round_table', 6.0, 8.2), F('stool', 4.6, 8.2), F('stool', 7.4, 8.4), F('stool', 6.0, 9.4),
        F('round_table', 10.0, 10.0), F('stool', 8.6, 10.1), F('stool', 11.4, 10.2), F('stool', 10.0, 11.2),
        F('table', 17.5, 9.2, 2.2, deco='plates'), F('bench', 17.5, 7.9, 2.4), F('bench', 17.5, 10.8, 2.4),
        F('round_table', 23.5, 9.6), F('stool', 22.0, 9.7), F('stool', 25.0, 9.8), F('stool', 23.5, 10.9),
        F('round_table', 6.5, 12.2), F('stool', 5.0, 12.3), F('stool', 8.0, 12.4),
        F('plant', 2.1, 4.6), F('plant', 25.9, 4.6), F('barrel', 25.4, 12.7), F('crate', 24.4, 12.9),
        F('sack', 2.4, 12.8), F('plant', 2.4, 11.0),
    ]
    dc = windows([3.2, 17.5, 25.0]) + [
        D('sign', 14, 0.35 + 0.25, t='QUARTOS'),
        D('shelf_wall', 21.5, 1.65, w=5, items='bottles'), D('shelf_wall', 21.5, 2.45, w=5, items='plates'),
        D('torch', 8.0, 0.75), D('torch', 14.8, 0.75), D('painting', 1.6 + 0.0, 0.7),
        D('round_rug', 6.0, 8.6, w=4.4, d=2.8, c='#8a3a32'), D('rug', 11.5, 10.3, w=4.2, d=2.8, c='#3a5a8a'),
        D('rug', 14.0, 12.8, w=2.6, d=1.4, c='#6a4a2a'),
    ]
    npcs = [N(keeper_id, keeper_look, 21.3, 3.95)]
    return room(name, title, 'tavern', W, H, outdoor, f, dc, npcs, 'tavern')


def guild(name, outdoor, staff_id, staff_look, title):
    W, H = 26, 15
    f = [
        F('counter', 13.0, 5.4, 6, deco='papers'),
        F('board', 6.0, 3.85, 2.6, act='board', seed_v=3), F('board', 20.0, 3.85, 2.6, seed_v=9),
        F('weapon_rack', 2.9, 5.3, 1.6), F('armor_stand', 23.3, 4.6),
        F('table', 5.0, 9.4, 2.2, deco='map'), F('bench', 5.0, 8.1, 2.2), F('bench', 5.0, 10.9, 2.2),
        F('table', 21.0, 9.4, 2.2, deco='mugs'), F('bench', 21.0, 8.1, 2.2), F('bench', 21.0, 10.9, 2.2),
        F('table', 5.5, 12.6, 1.8, deco='plates'), F('chair', 4.2, 13.3), F('chair', 6.8, 13.3),
        F('plant', 2.2, 8.0), F('plant', 23.8, 8.0), F('barrel', 23.6, 12.6), F('crate', 22.6, 12.8),
        F('pillar', 9.0, 7.0), F('pillar', 17.0, 7.0),
    ]
    dc = windows([9.9, 16.1]) + [
        D('banner', 3.2, 0.5, c='#a8332f'), D('banner', 11.0, 0.5, c='#2f5aa8'), D('banner', 14.2, 0.5, c='#2f5aa8'), D('banner', 22.2, 0.5, c='#a8332f'),
        D('swords', 13.0, 0.55), D('torch', 8.0, 0.75), D('torch', 18.0, 0.75),
        D('runner', 13.0, 9.9, w=2.4, d=7.0, c='#9a2a30'), D('rug', 5.0, 9.4, w=4.0, d=2.4, c='#3a4a6a'), D('rug', 21.0, 9.4, w=4.0, d=2.4, c='#3a4a6a'),
    ]
    npcs = [N(staff_id, staff_look, 13.0, 4.1)]
    return room(name, title, 'guild', W, H, outdoor, f, dc, npcs, 'guild')


def smithy(name, outdoor, smith_id, smith_look, title):
    W, H = 24, 14
    f = [
        F('forge', 5.0, 4.3, 3), F('anvil', 9.5, 6.4), F('anvil', 3.4, 7.6),
        F('counter', 17.0, 5.3, 5, deco='gems'),
        F('weapon_rack', 11.5, 3.8, 2.0), F('weapon_rack', 21.5, 4.4, 1.6), F('armor_stand', 14.5, 4.0),
        F('barrel', 2.4, 10.8), F('crate', 3.4, 11.3), F('sack', 21.6, 11.6), F('barrel', 21.8, 12.6),
        F('crate', 9.0, 11.6), F('plant', 22.0, 7.4),
    ]
    dc = windows([13.8 + 3.0]) + [
        D('torch', 8.2, 0.8), D('torch', 12.6, 0.8), D('swords', 20.0, 0.55), D('clock', 2.7, 0.7),
        D('round_rug', 12.0, 8.8, w=4.6, d=3.0, c='#6a3a2a'), D('rug', 17.0, 6.4, w=4.4, d=1.2, c='#5a2a22'),
    ]
    npcs = [N(smith_id, smith_look, 17.0, 4.0)]
    return room(name, title, 'smithy', W, H, outdoor, f, dc, npcs, 'smithy')


def apothecary(name, outdoor, shop_id, shop_look, title):
    W, H = 24, 14
    f = [
        F('potion_shelf', 4.5, 3.8, 3, seed_v=2), F('potion_shelf', 8.5, 3.8, 3, seed_v=5), F('potion_shelf', 20.3, 5.0, 2),
        F('counter', 14.5, 5.5, 5, deco='bottles'), F('cauldron', 20.5, 8.8),
        F('table', 5.5, 9.4, 2.0, deco='bottles'), F('stool', 4.4, 10.4), F('stool', 6.7, 10.4),
        F('plant', 2.2, 4.8), F('plant', 12.0, 4.0), F('plant', 22.0, 11.6), F('barrel', 2.3, 12.4), F('crate', 3.3, 12.6),
    ]
    dc = windows([13.9, 17.8]) + [
        D('shelf_wall', 14.5, 1.7, w=4, items='bottles'), D('torch', 11.0, 0.8), D('torch', 18.9, 0.8),
        D('round_rug', 14.0, 9.4, w=4.4, d=2.8, c='#3a6a4a'), D('rug', 5.5, 9.4, w=3.6, d=2.4, c='#6a3a6a'),
    ]
    npcs = [N(shop_id, shop_look, 14.4, 4.2)]
    return room(name, title, 'shop', W, H, outdoor, f, dc, npcs, 'shop')


def armory(name, outdoor, id_, look, title):
    W, H = 24, 14
    f = [
        F('armor_stand', 4.0, 4.5), F('armor_stand', 6.2, 4.5), F('armor_stand', 8.4, 4.5),
        F('weapon_rack', 20.5, 4.4, 2.2), F('weapon_rack', 2.6, 8.6, 1.6),
        F('counter', 14.0, 5.5, 5, deco='gems'),
        F('table', 6.5, 9.6, 2.2), F('bench', 6.5, 8.3, 2.2),
        F('crate', 21.8, 10.4), F('barrel', 22.0, 11.6), F('crate', 3.0, 12.4), F('plant', 12.0, 4.0),
        F('armor_stand', 18.2, 9.6), F('armor_stand', 20.2, 9.6),
    ]
    dc = windows([12.4, 17.2]) + [
        D('banner', 10.6 + 0.2, 0.5, c='#2f5aa8'), D('swords', 14.0, 0.55), D('torch', 11.0, 0.8), D('torch', 18.0, 0.8),
        D('rug', 14.0, 8.6, w=5.0, d=2.2, c='#3a4a6a'),
    ]
    npcs = [N(id_, look, 14.0, 4.2)]
    return room(name, title, 'armory', W, H, outdoor, f, dc, npcs, 'shop')


def stable(name, outdoor, id_, look, title):
    W, H = 24, 14
    f = [
        F('stall', 4.5, 5.2, 3), F('stall', 8.5, 5.2, 3), F('stall', 12.5, 5.2, 3),
        F('trough', 18.2, 5.0, 2.2), F('hay', 21.0, 5.0), F('hay', 21.0, 7.2), F('hay', 3.0, 10.4),
        F('barrel', 20.8, 11.2), F('crate', 19.4, 11.6), F('sack', 3.0, 12.4), F('sack', 4.0, 12.6),
        F('weapon_rack', 8.2, 11.8, 1.8), F('bench', 16.6, 9.4, 2.4),
    ]
    dc = windows([17.0, 20.5]) + [
        D('torch', 3.3, 0.8), D('torch', 15.0, 0.8), D('swords', 21.0 + 0.0, 0.55),
        D('rug', 12.0, 9.0, w=6.0, d=2.0, c='#7a5a30'),
    ]
    npcs = [N(id_, look, 12.0, 7.0, 'down')]
    return room(name, title, 'stable', W, H, outdoor, f, dc, npcs, 'stable')


def library(name, outdoor, id_, look, title):
    W, H = 24, 14
    f = [
        F('bookshelf', 4.0, 4.2, 3, seed_v=1), F('bookshelf', 7.2, 4.2, 3, seed_v=2), F('bookshelf', 16.8, 4.2, 3, seed_v=3), F('bookshelf', 20.0, 4.2, 3, seed_v=4),
        F('desk', 12.0, 5.4, 3, deco='papers'),
        F('bookshelf', 2.0, 8.0, 1.5, seed_v=6), F('bookshelf', 22.0, 8.0, 1.5, seed_v=7),
        F('table', 6.5, 9.6, 2.6, deco='papers'), F('chair', 5.5, 10.6), F('chair', 7.6, 10.6),
        F('table', 17.5, 9.6, 2.6, deco='map'), F('chair', 16.5, 10.6), F('chair', 18.6, 10.6),
        F('plant', 2.4, 12.6), F('plant', 21.6, 12.6), F('torch_stand', 9.6, 8.6, seed_v=1), F('torch_stand', 14.4, 8.6, seed_v=2),
    ]
    dc = windows([10.2, 13.8]) + [
        D('clock', 12.0, 0.7), D('painting', 1.9 + 0.0, 0.7),
        D('round_rug', 12.0, 9.8, w=6.0, d=3.4, c='#5a3a7a'), D('rug', 12.0, 6.6, w=3.6, d=1.2, c='#7a3a5a'),
    ]
    npcs = [N(id_, look, 12.0, 4.25)]
    return room(name, title, 'library', W, H, outdoor, f, dc, npcs, 'library')


def barracks(name, outdoor, id_, look, title):
    W, H = 24, 14
    f = [
        F('cot', 3.5, 5.3), F('cot', 5.3, 5.3), F('cot', 7.1, 5.3), F('cot', 3.5, 9.0), F('cot', 5.3, 9.0), F('cot', 7.1, 9.0),
        F('table', 16.0, 8.6, 3.0, deco='map'), F('bench', 16.0, 7.3, 3.0), F('bench', 16.0, 10.0, 3.0),
        F('weapon_rack', 12.0, 3.8, 2.2), F('weapon_rack', 21.0, 4.4, 1.8), F('armor_stand', 22.2, 8.2), F('barrel', 21.8, 12.4), F('crate', 3.0, 12.4),
        F('counter', 18.0, 5.0, 3, deco='papers'),
    ]
    dc = windows([8.8, 20.3]) + [
        D('banner', 10.3, 0.5, c='#2f5aa8'), D('banner', 15.0, 0.5, c='#2f5aa8'), D('swords', 12.6, 0.55), D('torch', 9.6, 0.8), D('torch', 18.0, 0.8),
        D('runner', 12.0, 10.0, w=2.2, d=6.0, c='#5a2a2a'),
    ]
    npcs = [N(id_, look, 18.0, 3.95)]
    return room(name, title, 'barracks', W, H, outdoor, f, dc, npcs, 'barracks')


def bakery(name, outdoor, id_, look, title):
    W, H = 24, 14
    f = [
        F('oven', 5.0, 4.3, 3), F('bread_rack', 9.8, 4.0, 2.4),
        F('counter', 16.0, 5.3, 5, deco='bread'),
        F('round_table', 6.5, 9.2), F('stool', 5.2, 9.3), F('stool', 7.8, 9.4),
        F('round_table', 8.5, 11.2), F('stool', 7.2, 11.3), F('stool', 9.8, 11.4),
        F('plant', 2.3, 6.8), F('plant', 22.0, 4.6), F('barrel', 21.6, 11.6), F('sack', 22.4, 12.6),
        F('crate', 3.0, 12.4),
    ]
    dc = windows([13.2, 19.0]) + [
        D('shelf_wall', 17.0, 1.7, w=3, items='plates'), D('torch', 8.0, 0.8), D('clock', 2.6, 0.7),
        D('round_rug', 6.5, 9.4, w=4.0, d=2.6, c='#c24a3a'), D('rug', 16.0, 7.2, w=4.0, d=1.2, c='#d09a50'),
    ]
    npcs = [N(id_, look, 16.0, 4.0)]
    return room(name, title, 'bakery', W, H, outdoor, f, dc, npcs, 'bakery')


def house(name, outdoor, variant, resident, title):
    """Small cottage: hearth, bed, table and a few belongings; variant 0..3 changes the layout and the rug colours."""
    W, H = 14, 11
    flip = variant % 2 == 1
    mx = (lambda x: W - x) if flip else (lambda x: x)
    f = [
        F('fireplace', mx(3.4), 3.95, 2.4), F('bed', mx(11.2), 4.9), F('bookshelf', mx(8.0), 3.85, 1.6, seed_v=variant + 1),
        F('table', mx(3.9), 7.6, 2.0, deco='plates' if variant < 2 else 'mugs'), F('chair', mx(2.9), 8.7), F('chair', mx(4.9), 8.7),
        F('barrel', mx(1.9), 6.0), F('crate', mx(12.0), 9.9), F('plant', mx(12.0), 8.0),
    ]
    if variant >= 2:
        f.append(F('sack', mx(10.8), 9.8))
    cols = ['#8a3a32', '#3a5a8a', '#4a7a4a', '#7a5a2a'][variant % 4]
    dc = windows([mx(5.6), mx(10.0)]) + [D('torch', mx(1.7), 0.8), D('painting', mx(11.9), 0.7),
        D('round_rug', mx(4.1), 8.0, w=4.0, d=2.6, c=cols)]
    npcs = [N(resident[0], resident[1], mx(5.5), 5.6, 'down')] if resident else []
    return room(name, title, 'house', W, H, outdoor, f, dc, npcs, 'house')


RESIDENTS = [('res_lucia', 'villager'), ('res_tomas', 'r_monk'), ('res_nina', 'v_child'), ('res_bento', 'merchant')]
HOUSE_DOOR_X = {'house_a': 0, 'house_b': -30}


def village_houses(data):
    hs = [p for p in data['props'] if p['kind'] in HOUSE_DOOR_X and 'stage' not in p]
    hs.sort(key=lambda p: (round(p['y']), p['x']))
    return hs


def house_name(i):
    return 'int_house_aurora_%d' % i


# interior name -> (building prop kind in the outdoor map, which one if several: index by x order)
INTERIORS = [
    ('village', 'guild', guild('int_guild_aurora', 'village', 'receptionist', 'guild_clerk', 'Guilda de Aurora')),
    ('village', 'smithy', smithy('int_smithy_aurora', 'village', 'blacksmith', 'merchant', 'Ferraria de Aurora')),
    ('village', 'tavern', tavern('int_tavern_aurora', 'village', 'inn_aurora', 'villager', 'Taverna da Lanterna')),
    ('valemont', 'guild', guild('int_guild_valemont', 'valemont', 'guildmaster', 'v_guildmaster', 'Guilda de Valemont')),
    ('valemont', 'tavern', tavern('int_tavern_valemont', 'valemont', 'tavern_keeper', 'villager', 'Taverna do Javali Dourado')),
    ('valemont', 'smithy', smithy('int_smithy_valemont', 'valemont', 'smith_v', 'r_dwarf', 'Forja de Valemont')),
    ('valemont', 'apothecary', apothecary('int_shop_valemont', 'valemont', 'shopkeeper', 'merchant', 'Boticário de Valemont')),
    ('valemont', 'armory', armory('int_armory_valemont', 'valemont', 'armorer', 'x_knight', 'Armaria Real')),
    ('valemont', 'stable', stable('int_stable_valemont', 'valemont', 'stable_master', 'x_veteran', 'Estábulo de Valemont')),
    ('valemont', 'library', library('int_library_valemont', 'valemont', 'librarian', 'r_monk', 'Biblioteca de Valemont')),
    ('valemont', 'barracks', barracks('int_barracks_valemont', 'valemont', 'guard_captain', 'v_guard', 'Quartel da Guarda')),
    ('valemont', 'bakery', bakery('int_bakery_valemont', 'valemont', 'baker', 'villager', 'Padaria Pão Dourado')),
]
DOOR_X = {'smithy': -38, 'bakery': 40}
# shops that close when it is night (the guild, the tavern and the barracks stay open)
CLOSED_AT_NIGHT = ['smithy', 'shop', 'armory', 'stable', 'library', 'bakery']
# buildings added to Aurora (the starting village only had the guild): [kind, x, y]
EXTRA_BUILDINGS = {'village': [['smithy', 2992.0, 2200.0], ['tavern', 2000.0, 1960.0]]}


def build_interior(r):
    w, h = r['w'], r['h']
    blocked = []
    door_cols = (w // 2 - 1, w // 2)
    for j in range(h):
        for i in range(w):
            wall = j < 3 or i == 0 or i == w - 1 or (j == h - 1 and i not in door_cols)
            blocked.append('1' if wall else '0')
    ex = dict(to=r['outdoor'], x=(w // 2) * T, y=(h - 1) * T + T / 2, w=2 * T, h=T)
    return dict(name=r['name'], title=r['title'], interior=True, style=r['style'], kind=r['kind'], w=w, h=h, tile=T, chunk=512, chunksX=0, chunksY=0,
                blocked=''.join(blocked), playerX=(w // 2) * T, playerY=(h - 3) * T, props=[], spawns=[], npcs=r['npcs'], exits=[ex], caches=[], walkers=[],
                furniture=r['furniture'], decor=r['decor'], outdoor=r['outdoor'], closed_at_night=r['kind'] in CLOSED_AT_NIGHT)


def patch_map(data):
    """Add the door exits (and extra buildings) to an outdoor map dict; remove the NPCs that moved indoors."""
    m = data['name']
    mine = [(b, r) for (mm, b, r) in INTERIORS if mm == m]
    if not mine:
        return data
    existing = {p['kind'] for p in data['props']}
    for kind, x, y in EXTRA_BUILDINGS.get(m, []):
        if not any(p['kind'] == kind and abs(p['x'] - x) < 8 and abs(p['y'] - y) < 8 for p in data['props']):
            if not any(p['kind'] == kind for p in data['props']):
                data['props'].append(dict(kind=kind, x=x, y=y))
    data['props'].sort(key=lambda p: p['y'])
    data['exits'] = [e for e in data['exits'] if not str(e['to']).startswith('int_')]
    inside = set()
    for b, r in mine:
        cand = [p for p in data['props'] if p['kind'] == b]
        if not cand:
            print('  no building', b, 'in', m)
            continue
        bp = cand[0]
        dx = DOOR_X.get(b, 0)
        data['exits'].append(dict(to=r['name'], x=bp['x'] + dx, y=bp['y'] + 54, w=76, h=56, ax=bp['x'] + dx, ay=bp['y'] + 118, kind=r['kind']))
        for n in r['npcs']:
            inside.add(n['id'])
    data['npcs'] = [n for n in data['npcs'] if n['id'] not in inside]
    if m == 'village':
        for i, hp in enumerate(village_houses(data)):
            dx = HOUSE_DOOR_X[hp['kind']]
            data['exits'].append(dict(to=house_name(i), x=hp['x'] + dx, y=hp['y'] + 54, w=64, h=56, ax=hp['x'] + dx, ay=hp['y'] + 118, kind='house'))
    return data


FOOT = {'counter': (None, 0.9), 'table': (None, 1.0), 'round_table': (1.2, 0.9), 'chair': (0.5, 0.45), 'stool': (0.45, 0.4), 'bench': (None, 0.5),
        'barrel': (0.75, 0.6), 'crate': (0.85, 0.7), 'sack': (0.7, 0.5), 'fireplace': (None, 0.8), 'bed': (1.25, 1.7), 'cot': (1.0, 1.6),
        'bookshelf': (None, 0.6), 'potion_shelf': (None, 0.6), 'desk': (None, 0.9), 'anvil': (0.9, 0.6), 'forge': (None, 1.0),
        'weapon_rack': (None, 0.4), 'armor_stand': (0.8, 0.5), 'cauldron': (0.95, 0.7), 'stall': (None, 1.1), 'oven': (None, 1.0),
        'bread_rack': (None, 0.5), 'board': (None, 0.35), 'plant': (0.5, 0.4), 'pillar': (0.7, 0.6), 'hay': (1.0, 0.7), 'trough': (None, 0.5),
        'door_room': (1.1, 0.3), 'torch_stand': (0.4, 0.3)}


def rect_of(f):
    fw, fd = FOOT.get(f['k'], (0.8, 0.6))
    fw = f['w'] if fw is None else fw
    x, y = f['x'] / T, f['y'] / T
    return (x - fw / 2, y - fd, x + fw / 2, y)


def validate(r):
    w, h = r['w'], r['h']
    cx = w / 2.0
    lane = (cx - 1.3, h - 5.5, cx + 1.3, h - 1.0)        # doorway corridor must stay free
    bad = []
    for f in r['furniture']:
        a = rect_of(f)
        if f['k'] in ('door_room',):
            continue
        if not (a[2] < lane[0] or a[0] > lane[2] or a[3] < lane[1] or a[1] > lane[3]):
            bad.append(('corridor', f['k'], f['x'] / T, f['y'] / T))
        if a[0] < 1.0 or a[2] > w - 1.0 or a[3] > h - 1.0:
            bad.append(('outside', f['k'], f['x'] / T, f['y'] / T))
    for n in r['npcs']:
        for f in r['furniture']:
            a = rect_of(f)
            nx, ny = n['x'] / T, n['y'] / T
            if a[0] - 0.3 < nx < a[2] + 0.3 and a[1] < ny < a[3] + 0.05 and f['k'] not in ('counter',):
                bad.append(('npc-inside', n['id'], f['k']))
    fs = r['furniture']
    for i in range(len(fs)):
        for j in range(i + 1, len(fs)):
            a, b = rect_of(fs[i]), rect_of(fs[j])
            if fs[i]['k'] in ('door_room',) or fs[j]['k'] in ('door_room',):
                continue
            ox = min(a[2], b[2]) - max(a[0], b[0])
            oy = min(a[3], b[3]) - max(a[1], b[1])
            if ox > 0.12 and oy > 0.12:
                bad.append(('overlap', fs[i]['k'], fs[j]['k'], round(fs[i]['x'] / T, 1), round(fs[i]['y'] / T, 1)))
    return bad


def main():
    for m, b, r in INTERIORS:
        for x in validate(r):
            print('WARN', r['name'], x)
    index = {}
    for m, b, r in INTERIORS:
        d = build_interior(r)
        with open(os.path.join(MAPS, r['name'] + '.json'), 'w') as fp:
            json.dump(d, fp)
        for n in r['npcs']:
            index[n['id']] = r['name']
    vil = json.load(open(os.path.join(MAPS, 'village.json')))
    for i, hp in enumerate(village_houses(vil)):
        d = build_interior(house(house_name(i), 'village', i % 4, RESIDENTS[i // 3] if i % 3 == 0 and i // 3 < len(RESIDENTS) else None, 'Casa de Aurora'))
        with open(os.path.join(MAPS, house_name(i) + '.json'), 'w') as fp:
            json.dump(d, fp)
    for m in sorted({m for m, _, _ in INTERIORS}):
        p = os.path.join(MAPS, m + '.json')
        data = json.load(open(p))
        data = patch_map(data)
        json.dump(data, open(p, 'w'), indent=0)
        print('patched', m, 'exits', [e['to'] for e in data['exits']])
    json.dump(index, open(os.path.join(ROOT, 'godot', 'data', 'interiors.json'), 'w'), indent=1)
    print('wrote', len(INTERIORS), 'interiors')


if __name__ == '__main__':
    main()
