"""Adds the rarity-tiered equipment families (Comum → Lendário) to godot/data/items.json. Idempotent."""
import json, os
P = os.path.join(os.path.dirname(__file__), '..', 'godot', 'data', 'items.json')
d = json.load(open(P))

def base(id, name, desc, icon, slot, rarity, value, **st):
    it = dict(id=id, name=name, desc=desc, slot=slot, rarity=rarity, atk=0, defense=0, mag=0, hp=0, icon=icon,
              heal=0, mana=0, consumable=False, value=value)
    it.update(st)
    d[id] = it

TIER_TXT = ['Equipamento comum.', 'Bem trabalhado.', 'Artesanato raro, de brilho azulado.',
            'Peça épica; runas pulsam no metal.', 'LENDÁRIO — forjado para heróis antigos.']
VAL = [40, 120, 320, 900, 2400]

SW = [('Espada de Ferro', 5), ('Espada de Aço Temperado', 11), ('Lâmina Rúnica', 18), ('Espada do Alvorecer', 27), ('Excalibur de Aetheria', 40)]
BW = [('Arco de Freixo', 4), ('Arco Composto', 10), ('Arco do Vento Norte', 16), ('Arco Estelar', 25), ('Falcão Dourado, Arco Lendário', 37)]
DG = [('Adagas de Ferro', 4), ('Adagas Serrilhadas', 9), ('Presas da Víbora', 15), ('Lâminas da Lua Nova', 23), ('Duo Eclipse, Adagas Lendárias', 34)]
ST = [('Cajado de Carvalho', 6), ('Cajado de Ébano', 13), ('Cajado Arcano', 21), ('Cajado das Tempestades', 31), ('Cetro da Centelha Eterna', 46)]
SETS = ['Aventureiro', 'Veterano', 'Rúnico', 'Alvorecer', 'Lendário']
AR = [('Gibão Reforçado', 6), ('Cota de Malha', 12), ('Armadura de Escamas', 19), ('Couraça Drácônica', 28), ('Égide do Último Rei', 38)]
CH = [('Amuleto de Madeira', dict(hp=12)), ('Anel de Prata', dict(mag=6, hp=10)), ('Talismã do Guardião', dict(mag=10, hp=24)),
      ('Olho de Aetheria', dict(mag=15, hp=40)), ('Coração da Centelha', dict(mag=24, hp=70))]
for i in range(5):
    base(f'sw_{i}', SW[i][0], TIER_TXT[i] + f'', 'gear_sword', 1, i, VAL[i], atk=SW[i][1])
    base(f'bw_{i}', BW[i][0], TIER_TXT[i] + f' Só arqueiros.', 'skill_roll', 1, i, VAL[i], atk=BW[i][1], weapon_type='bow')
    base(f'dg_{i}', DG[i][0], TIER_TXT[i] + f' Só assassinos.', 'skill_sword', 1, i, VAL[i], atk=DG[i][1], weapon_type='dual_daggers')
    base(f'st_{i}', ST[i][0], TIER_TXT[i] + ' Só magos e invocadores.', 'skill_spark', 1, i, VAL[i], mag=ST[i][1], weapon_type='staff')
    base(f'ar_{i}', AR[i][0], TIER_TXT[i] + f'', 'gear_armor', 2, i, VAL[i], defense=AR[i][1])
    base(f'ch_{i}', CH[i][0], TIER_TXT[i], 'gear_charm', 3, i, VAL[i], **CH[i][1])
for fam in ('sw', 'bw', 'dg', 'st', 'ar', 'ch'):
    for i in range(5):
        d[f'{fam}_{i}']['set'] = SETS[i]
        d[f'{fam}_{i}']['set_tier'] = i
# plain values for the older gear / materials so everything can be sold
for k, it in d.items():
    it.setdefault('value', [40, 120, 320, 900, 2400][it['rarity']] if it['slot'] else 1)
json.dump(d, open(P, 'w'), indent=2, ensure_ascii=False)
print(len(d), 'items')
