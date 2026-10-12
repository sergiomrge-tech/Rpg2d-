"""Create truthful pre/post sprite galleries and test that shapes really changed.

Run before while old PNGs are checked out; re-render; run after.
All panels are frames from original animation atlases, NOT screenshots.
"""
import json
import io
import subprocess
import sys
from pathlib import Path
from PIL import Image, ImageDraw

ROOT=Path(__file__).resolve().parents[2]
SHEETS=ROOT/'unity/Assets/Resources/Sprites/Demons'
PRE=ROOT/'docs/asset_catalog/previews'
STAGE=ROOT/'docs/asset_catalog/.before_temp'
IDS=['imp_scout','imp_raider','imp_pyro','imp_howler',
     'oni_lancer','oni_shielder','oni_executioner','morgash_ironhorn']
NAMES=['Batedor','Saqueador','Piromante','Uivador',
       'Lanceiro','Escudeiro','Carrasco','Morgash']

def frame(id_):
    j=json.loads((SHEETS/(id_+'.json')).read_text(encoding='utf-8'))
    a=next(a for a in j['anims'] if a['name']=='idle_down')
    k=a['start']+min(2,a['count']-1)
    w,h,cols=j['frameW'],j['frameH'],j['cols']
    with Image.open(SHEETS/(id_+'.png')) as sheet:
        return sheet.crop(((k%cols)*w,(k//cols)*h,(k%cols+1)*w,(k//cols+1)*h)).convert('RGBA')

def original_frame(id_):
    """Read the original PR4 atlas, never the already-remodeled worktree PNG."""
    upstream='origin/gpt6-lote1-all-sprites-20261012'
    base='unity/Assets/Resources/Sprites/Demons/'+id_
    j=json.loads(subprocess.check_output(
        ['git','show',upstream+':'+base+'.json'],cwd=ROOT).decode('utf-8'))
    image_bytes=subprocess.check_output(
        ['git','show',upstream+':'+base+'.png'],cwd=ROOT)
    a=next(a for a in j['anims'] if a['name']=='idle_down')
    k=a['start']+min(2,a['count']-1)
    w,h,cols=j['frameW'],j['frameH'],j['cols']
    with Image.open(io.BytesIO(image_bytes)) as sheet:
        return sheet.crop(((k%cols)*w,(k//cols)*h,(k%cols+1)*w,(k//cols+1)*h)).convert('RGBA')


def crop(f):
    box=f.getchannel('A').getbbox()
    assert box, 'empty alpha'
    return f.crop(box)

def tile(f,w=190,h=190):
    f=crop(f)
    s=min((w-12)/f.width,(h-12)/f.height)
    f=f.resize((max(1,int(f.width*s)),max(1,int(f.height*s))),Image.Resampling.LANCZOS)
    dest=Image.new('RGBA',(w,h),(35,34,53,255))
    dest.alpha_composite(f,((w-f.width)//2,(h-f.height)//2))
    return dest.convert('RGB')

def after():
    PRE.mkdir(parents=True,exist_ok=True)
    cw,ch=398,254
    comp=Image.new('RGB',(cw*4,ch*2+55),(23,21,34))
    d=ImageDraw.Draw(comp)
    d.text((12,11),'LOTE 1 - ANATOMIAS REFEITAS: quadros reais de sprite',fill=(248,212,169))
    d.text((12,31),'ANTES e NOVO. Nao sao screenshots do Unity.',fill=(188,190,204))
    atlas=Image.new('RGB',(4*225,2*260+48),(23,21,34))
    ad=ImageDraw.Draw(atlas)
    ad.text((10,12),'OITO SILHUETAS UNICAS - tecnica HD cartoon original',fill=(240,216,170))
    scores={}
    for i,(id_,title) in enumerate(zip(IDS,NAMES)):
        with Image.open(STAGE/(id_+'.png')) as old:
            before=old.convert('RGBA')
        new=frame(id_)
        x=(i%4)*cw;y=55+(i//4)*ch
        comp.paste(tile(before),(x+4,y+9))
        comp.paste(tile(new),(x+200,y+9))
        d.text((x+9,y),title+' ANTES',fill=(231,201,165))
        d.text((x+204,y),title+' NOVO',fill=(143,227,193))
        xx=(i%4)*225+4;yy=(i//4)*260+38
        atlas.paste(tile(new,216,216),(xx,yy))
        ad.text((xx+3,yy+219),id_,fill=(226,211,183))
        # Normalized silhouette intersection over union is a warning,
        # not a substitute for visual review or Unity screenshots.
        a=crop(before).getchannel('A').resize((128,128),Image.Resampling.LANCZOS)
        b=crop(new).getchannel('A').resize((128,128),Image.Resampling.LANCZOS)
        ab=a.tobytes();bb=b.tobytes()
        both=sum(u>70 and v>70 for u,v in zip(ab,bb))
        either=sum(u>70 or v>70 for u,v in zip(ab,bb))
        scores[id_]=round(both/max(1,either),3)
        box=new.getchannel('A').getbbox()
        assert box is not None,(id_,'empty frame')
        assert box[0]>1 and box[1]>1 and box[2]<new.width-1 and box[3]<new.height-1,(id_,'frame clipped',box,new.size)
    comp.save(PRE/'LOTE1_REMODEL_COMPARACAO.png',optimize=True)
    atlas.save(PRE/'LOTE1_REMODEL_OITO.png',optimize=True)
    print('Old/new silhouette IoU (visual diagnostic):',scores)
    for id_,score in scores.items():
        assert score<0.89,(id_,'too close to previous silhouette',score)
    print('All eight silhouettes distinct; frame boundary check OK; Unity runtime not tested')

def main():
    if len(sys.argv)!=2 or sys.argv[1] not in ('before','after'):
        raise SystemExit('usage: rework_gallery.py before|after')
    if sys.argv[1]=='before':
        STAGE.mkdir(parents=True,exist_ok=True)
        for id_ in IDS:
            original_frame(id_).save(STAGE/(id_+'.png'),optimize=True)
        print('Staged eight pre-rework original frames from PR4 base')
    else:
        after()

if __name__=='__main__':
    main()
