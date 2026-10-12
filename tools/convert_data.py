"""One-off converter: Unity Data.cs -> godot/data/{items,demons,recipes}.json (JSON is now the source of truth)."""
import json, re, os
src = open('prototypes/unity/Assets/Scripts/Game/Data.cs', encoding='utf-8').read()
R = {'Common': 0, 'Uncommon': 1, 'Rare': 2, 'Epic': 3, 'Legendary': 4}
items = {}

def num(s):
    return float(s.rstrip('f'))

for m in re.finditer(r'Add\(new ItemDef \{(.*?)\}\);', src):
    body = m.group(1)
    d = {}
    for k, v in re.findall(r'(\w+) = ("[^"]*"|[\w.]+)', body):
        if v.startswith('"'): d[k] = v.strip('"')
        elif v in ('true', 'false'): d[k] = v == 'true'
        elif v.startswith('Rarity.'): d[k] = R[v[7:]]
        else: d[k] = num(v)
    items[d['id']] = d
for m in re.finditer(r'Gear\("(\w+)", "([^"]*)", "([^"]*)", (\d), Rarity\.(\w+)((?:, \w+: [\d.]+)*)\);', src):
    i, n, desc, slot, r, rest = m.groups()
    d = dict(id=i, name=n, desc=desc, slot=int(slot), rarity=R[r], atk=0, defense=0, mag=0, hp=0)
    for k, v in re.findall(r', (\w+): ([\d.]+)', rest):
        d['defense' if k == 'def' else k] = float(v)
    d['icon'] = {1: 'gear_sword', 2: 'gear_armor', 3: 'gear_charm'}[int(slot)]
    items[i] = d
for d in items.values():
    d.setdefault('slot', 0); d.setdefault('desc', ''); d.setdefault('rarity', 0)
    d.setdefault('heal', 0); d.setdefault('mana', 0); d.setdefault('consumable', False)
    d.setdefault('atk', 0); d.setdefault('defense', 0); d.setdefault('mag', 0); d.setdefault('hp', 0)

demons = {}
for m in re.finditer(r'Demons\["(\w+)"\] = new DemonDef\s*\{(.*?)\n            \};', src, re.S):
    i, body = m.groups()
    d = {}
    drops = re.search(r'drops = new\[\] \{(.*?)\}\s*$', body, re.S)
    for k, v in re.findall(r'(\w+) = ("[^"]*"|true|false|[\d.]+f?)', body.split('drops =')[0]):
        d[k] = v.strip('"') if v.startswith('"') else (v == 'true' if v in ('true', 'false') else num(v))
    d['drops'] = [[a, num(b), int(c), int(e)] for a, b, c, e in re.findall(r'\("(\w+)", ([\d.]+f?), (\d+), (\d+)\)', drops.group(1))]
    demons[i] = d
for m in re.finditer(r'\n\s+D\("(\w+)", "([^"]*)", "([^"]*)", ([\d.f]+), ([\d.f]+), ([\d.f]+), ([\d.f]+), ([\d.f]+), ([\d.f]+), ([\d.f]+), (true|false)(?:, "([^"]*)")?\);', src):
    i, n, sh, hp, dmg, sp, ag, xp, po, sc, ca, title = m.groups()
    boss = title is not None
    demons[i] = dict(id=i, name=n, sheet='Sprites/' + sh, hp=num(hp), dmg=num(dmg), speed=num(sp), aggro=num(ag), xp=num(xp), poise=num(po),
                     scale=num(sc), caster=ca == 'true', boss=boss, title=title or '',
                     drops=([['gold', 1, 150, 220], ['hell_ember', 1, 2, 4], ['potion', 1, 2, 3], ['spark_tome', 0.5, 1, 1]] if boss else
                            [['gold', 1, 4, 12], ['imp_horn', 0.35, 1, 1], ['potion', 0.12, 1, 1], ['hell_ember', 0.06, 1, 1], ['spark_tome', 0.012, 1, 1]]))
def add_drop(k, item, ch, mn=1, mx=1):
    if k in demons: demons[k]['drops'].append([item, ch, mn, mx])
for k in list(demons):
    if k == 'oni' or k.startswith('oni_'): add_drop(k, 'demon_hide', 0.4, 1, 2)
    if k == 'spirit_corrupt': add_drop(k, 'spirit_dust', 0.5, 1, 2)
    if k == 'treant_demon': add_drop(k, 'spirit_dust', 0.7, 1, 3)
for k, it, ch, mn, mx in re.findall(r'AddDrop\("(\w+)", "(\w+)", ([\d.]+)f(?:, (\d+), (\d+))?\);', src):
    add_drop(k, it, float(ch), int(mn or 1), int(mx or 1))
for d in demons.values():
    d.setdefault('title', ''); d.setdefault('boss', False); d.setdefault('caster', False)

rec = []
for m in re.finditer(r'new Recipe \{ result = "(\w+)", gold = (\d+), needs = new\[\] \{(.*?)\} \}', src):
    r, g, needs = m.groups()
    rec.append(dict(result=r, gold=int(g), needs=[[a, int(b)] for a, b in re.findall(r'\("(\w+)", (\d+)\)', needs)]))
os.makedirs('godot/data', exist_ok=True)
for name, obj in (('items', items), ('demons', demons), ('recipes', rec)):
    json.dump(obj, open(f'godot/data/{name}.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(len(items), 'items', len(demons), 'demons', len(rec), 'recipes')
