"""Validate actual rendered PNG + animation metadata for all Lote 1 creatures.

No Unity license required. Rendering and static metadata checks are not a runtime
playtest or a substitute for visual review.
"""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
from PIL import Image, ImageChops

ROOT=Path(__file__).resolve().parents[2]
SPEC=json.loads((ROOT/'docs/asset_catalog/lote1_spec.json').read_text(encoding='utf-8'))
DIR=ROOT/'unity/Assets/Resources/Sprites/Demons'
PRE=ROOT/'docs/asset_catalog/previews'

def verify():
    expected=set()
    fingerprints={}
    for item in SPEC['roster']:
        name=item['id']
        v=item['visual']
        p=DIR/(name+'.png')
        j=DIR/(name+'.json')
        assert p.is_file() and j.is_file(),(name,'missing sprite or JSON')
        meta=json.loads(j.read_text(encoding='utf-8'))
        assert (meta['frameW'],meta['frameH'],meta['pivotX'],meta['pivotY'])==(v['frameW'],v['frameH'],v['pivotX'],v['pivotY'])
        anims={x['name']:x for x in meta['anims']}
        required={a['id']+'_'+direction for a in item['animations']['tracks'] if name!='grakk' or a['id']!='skill_2' for direction in ('down','up','side')}
        assert set(anims)==required,(name,sorted(required-set(anims)),sorted(set(anims)-required))
        prev=PRE/(name+'.png')
        assert prev.is_file() and prev.stat().st_size>3000,(name,'missing preview')
        with Image.open(prev) as pi:
            pi.verify()
        with Image.open(p) as image:
            image.load()
            assert image.mode=='RGBA'
            assert image.width==v['frameW']*meta['cols'] and image.height%v['frameH']==0
            assert image.width<=8192 and image.height<=8192
            assert image.getchannel('A').getbbox(),(name,'transparent whole sheet')
            fps_checks=0
            for stage in item['animations']['tracks']:
                if stage['id']=='skill_2' and name=='grakk': continue
                for dr in ('down','up','side'):
                    m=anims[stage['id']+'_'+dr]
                    assert m['count']==stage['frames_per_direction']
                    assert m['fps']==stage['fps']
                    assert m['hit']==stage['event_frame']
                    assert m['loop']==stage['loop']
                    k=m['start'];w=v['frameW'];h=v['frameH']
                    fr=image.crop(((k%meta['cols'])*w,(k//meta['cols'])*h,((k%meta['cols'])+1)*w,((k//meta['cols'])+1)*h))
                    assert fr.getchannel('A').getbbox(),(name,stage['id'],dr,'empty')
                    fps_checks+=1
            print('VALIDATED',name,'size=',image.size,'tracks=',fps_checks,flush=True)
        fingerprint=hashlib.sha256(p.read_bytes()).hexdigest()
        assert fingerprint not in fingerprints,(name,'duplicate sprite sheet of',fingerprints.get(fingerprint))
        fingerprints[fingerprint]=name
    for name in ('LOTE1_DEMONIOS','LOTE1_CHEFES'):
        png=PRE/(name+'.png')
        assert png.is_file() and png.stat().st_size>10000,name
        with Image.open(png) as im: im.verify()
    print('SUCCESS: 15 unique creature sprites, JSONs and 15 previews; both gallery sheets verified.')
    print('PENDING: Unity real gameplay, visual approval, AI, distinct VFX and Grakk skill_2.')

if __name__=='__main__':
    verify()
