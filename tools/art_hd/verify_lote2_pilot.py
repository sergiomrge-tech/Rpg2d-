"""Validate real animated pilot sprite outputs, never claim Unity runtime tested."""
from __future__ import annotations
import json,hashlib
from pathlib import Path
from PIL import Image,ImageChops

ROOT=Path(__file__).resolve().parents[2]
ART=ROOT/'unity/Assets/Resources/Sprites/Demons'
PRE=ROOT/'docs/asset_catalog/previews/lote2'
IDS=('mantis_reaver','scarab_brute','moth_hexer')
STATES=('idle','move','attack','cast','hurt','death')
DIRECTIONS=('down','up','side')

def main():
    def actually_different(a, b):
        # RGBA.getbbox on ImageChops.difference can return None even if RGB
        # changes when the alpha-difference channel is zero (Pillow semantics).
        delta = ImageChops.difference(a, b)
        return (delta.getchannel('A').getbbox() is not None or
                delta.convert('RGB').getbbox() is not None)

    digests=[]
    for id_ in IDS:
        png=ART/(id_+'.png');meta=ART/(id_+'.json')
        assert png.exists() and meta.exists(),('file missing',id_)
        obj=json.loads(meta.read_text(encoding='utf-8'))
        assert obj['frameW']==288 and obj['frameH']==288
        assert 0<obj['pivotX']<288 and 0<obj['pivotY']<288
        anims=obj['anims'];expected={s+'_'+v for s in STATES for v in DIRECTIONS}
        assert {a['name'] for a in anims}==expected
        assert len(anims)==18
        total=0
        with Image.open(png) as im:
            im.load();assert im.mode=='RGBA'
            assert im.width==obj['cols']*288 and im.width<=4096 and im.height<=8192
            assert im.height%288==0
            # Frames must actually move; not recolored still images.
            stage_frames={}
            for a in anims:
                frameid=lambda offset: a['start']+offset
                def frame_at(offset):
                    k=frameid(offset)
                    x=(k%obj['cols'])*288;y=(k//obj['cols'])*288
                    return im.crop((x,y,x+288,y+288))
                first=frame_at(0)
                middle=frame_at(a['count']//2)
                assert actually_different(first,middle), (id_,a['name'],'static animation')
                stage_frames[a['name']]=middle
            for state in STATES:
                assert actually_different(stage_frames[state+'_down'],stage_frames[state+'_up']), (id_,state,'no back view')
                assert actually_different(stage_frames[state+'_down'],stage_frames[state+'_side']), (id_,state,'no side view')
            for a in anims:
                assert a['start']==total
                assert a['count']>=6 and a['fps']>0
                if a['name'].startswith(('attack_','cast_')):
                    assert 0<=a['hit']<a['count']
                else: assert a['hit']==-1
                k=a['start']+a['count']//2
                x=(k%obj['cols'])*288;y=(k//obj['cols'])*288
                frame=im.crop((x,y,x+288,y+288))
                assert frame.getchannel('A').getbbox(),(id_,a['name'],'empty')
                total+=a['count']
            assert im.height//288*obj['cols']>=total
        with Image.open(PRE/(id_+'.png')) as preview:preview.verify()
        digests.append(hashlib.sha256(png.read_bytes()).hexdigest())
        print('OK',id_,total,'frames',len(anims),'tracks')
    assert len(set(digests))==3,'species assets identical'
    print('PILOT VERIFIED: actual 3 PNG + JSON animated atlases, 3 contact previews; no Unity runtime claim')

if __name__=='__main__':main()