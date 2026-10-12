"""Check new HD demon sprites and metadata; cannot substitute for Unity playtest."""
import json
from pathlib import Path
from PIL import Image, ImageChops

ROOT=Path(__file__).resolve().parents[2]
ART=ROOT/'unity'/'Assets'/'Resources'/'Sprites'/'Demons'
CAT=ROOT/'docs'/'asset_catalog'/'catalog.json'
VIEWS=('down','up','side')
ANIMS=('idle','move','attack','cast','hurt','death')

def check():
    cat=json.loads(CAT.read_text(encoding='utf-8'))
    assert cat['schema_version']==1
    assert {x['id'] for x in cat['assets']}=={'oni_soldier','grakk'}
    for info in cat['assets']:
        name=info['id']
        assert info['gameplay_status']=='not_registered'
        meta=json.loads((ART/(name+'.json')).read_text(encoding='utf-8'))
        with Image.open(ART/(name+'.png')) as im:
            im.load()
            assert im.mode=='RGBA'
            assert 0<im.width<=8192 and 0<im.height<=8192
            assert im.width==meta['cols']*meta['frameW']
            assert im.height%meta['frameH']==0
            assert 0<meta['pivotX']<meta['frameW']
            assert 0<meta['pivotY']<meta['frameH']
            anims=meta['anims']
            assert {a['name'] for a in anims}=={a+'_'+v for a in ANIMS for v in VIEWS}
            assert len(anims)==18
            end=0
            frames=[]
            for a in anims:
                assert a['start']==end
                assert a['count']>=4
                assert a['fps']>0
                assert a['hit']==-1 or 0<=a['hit']<a['count']
                end+=a['count']
                k=a['start'];w=meta['frameW'];h=meta['frameH'];cols=meta['cols']
                f=im.crop(((k%cols)*w,(k//cols)*h,(k%cols+1)*w,(k//cols+1)*h))
                assert f.getchannel('A').getbbox(),(name,a['name'],'empty')
                frames.append(f)
            assert (im.height//meta['frameH'])*meta['cols']>=end
            assert any(ImageChops.difference(frames[0],f).getbbox() for f in frames[1:])
        p=ROOT/info['preview']
        assert p.exists() and p.stat().st_size>4096
        with Image.open(p) as prev:
            prev.verify()
        print(name,'OK',len(anims),'animation tracks',end,'frames')
    print('HD DEMON CATALOG VERIFIED; UNITY VISUAL GATE STILL PENDING')

if __name__=='__main__':
    check()
