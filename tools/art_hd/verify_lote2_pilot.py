"""Validate Lote 2 first-three GAME assets and their Unity spawn/ability wiring.

This script verifies real generated PNG sprites, directional anim frames and
source wiring; it is NOT a substitute for running/building Unity.
"""
import json
from pathlib import Path
from PIL import Image, ImageChops

ROOT=Path(__file__).resolve().parents[2]
RES=ROOT/'unity/Assets/Resources/Sprites/Demons'
PRE=ROOT/'docs/asset_catalog/previews'
IDS=('mantis_reaver','scarab_brute','moth_hexer')
STATES=('idle','move','attack','cast','hurt','death')
DIRS=('down','up','side')
EXPECTED_HIT={'attack':6,'cast':8}
meta_cache={}

def first_frame(sheet,meta,name):
    a=next(a for a in meta['anims'] if a['name']==name)
    n=a['start']
    fw,fh,cols=meta['frameW'],meta['frameH'],meta['cols']
    return sheet.crop(((n%cols)*fw,(n//cols)*fh,((n%cols)+1)*fw,((n//cols)+1)*fh))

def validate():
    sprites=[]
    for name in IDS:
        png=RES/(name+'.png'); j=RES/(name+'.json')
        assert png.exists() and j.exists(),name+' missing PNG/JSON'
        meta=json.loads(j.read_text(encoding='utf-8'))
        assert (meta['frameW'],meta['frameH'],meta['pivotX'],meta['pivotY'])==(192,192,96,23)
        expected={a+'_'+d for a in STATES for d in DIRS}
        anims={a['name']:a for a in meta['anims']}
        assert set(anims)==expected,(name,expected-set(anims))
        with Image.open(png) as sheet:
            sheet.load()
            assert sheet.mode=='RGBA'
            assert 0<sheet.width<=4096 and 0<sheet.height<=8192
            assert sheet.width==192*meta['cols'] and sheet.height%192==0
            seen=set()
            for stage in STATES:
                for dr in DIRS:
                    a=anims[stage+'_'+dr]
                    assert a['count']>=6 and a['fps']>=10,(name,a)
                    assert a['hit']==EXPECTED_HIT.get(stage,-1)
                    assert a['loop']==(stage in ('idle','move'))
                    assert a['start']>=0
                    assert a['start']+a['count']<=(sheet.height//192)*meta['cols']
                    for step in (0,a['count']//2,a['count']-1):
                        idx=a['start']+step
                        fr=sheet.crop(((idx%meta['cols'])*192,(idx//meta['cols'])*192,
                             ((idx%meta['cols'])+1)*192,((idx//meta['cols'])+1)*192))
                        assert fr.getchannel('A').getbbox(),(name,a['name'],'blank frame')
                        if dr=='down' and stage in ('move','attack','cast'):
                            seen.add(fr.tobytes())
            assert len(seen)>=6,(name,'no animation motion')
            sprites.append(first_frame(sheet,meta,'idle_down').getchannel('A').resize((96,96)))
        with Image.open(PRE/(name+'.png')) as im:
            im.verify()
        meta_cache[name]=meta
        print(name,'OK',len(anims),'state/direction tracks')
    # Enforce that the three approved anatomical concepts are not recolors:
    # alpha silhouette cannot be identical (independent outlines).
    for i in range(3):
        for j in range(i+1,3):
            assert ImageChops.difference(sprites[i],sprites[j]).getbbox(),(IDS[i],IDS[j],'identical silhouette')
    data=json.loads((ROOT/'unity/Assets/Resources/Maps/village.json').read_text(encoding='utf-8'))
    spawns={x['kind']:x for x in data['spawns'] if x['kind'] in IDS}
    assert set(spawns)==set(IDS)
    for name,x in spawns.items():
        cx=int(x['x']//data['tile']);cy=int(x['y']//data['tile'])
        assert data['blocked'][cy*data['w']+cx]=='0',(name,'blocked spawn')
    code=' '.join((ROOT/'unity/Assets/Scripts/Game/'+n).read_text(encoding='utf-8') for n in ('Data.cs','Enemy.cs','InsectCombat.cs'))
    for name in IDS:assert name in code,name+' missing gameplay'
    for value in ('InsectCombat.Attack(this, p)','InsectCombat.Skill(this, p)','case "mantis"','case "scarab"','case "moth"'):
        assert value in code,'Missing behavior: '+value
    print('PASS: 3 Unity-accessible insect enemy atlases, distinct silhouettes, 54 tracks, forest spawns and ability hookups.')
    print('NOT CLAIMED: Unity runtime build/QA, approved visual quality or whole Lote 2 completed.')

if __name__=='__main__':
    validate()
