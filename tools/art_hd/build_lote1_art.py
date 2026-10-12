"""Renders 13 additional HD cartoon creatures in the Lote 1 catalog.

All images come directly from the existing Cairo renderer and humanoid / imp
rigs. Previews are sprite contact sheets, NEVER Unity screenshots.
"""
from __future__ import annotations
import json
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
sys.path.insert(0,str(HERE))
from lote1_creatures import build_creatures
from sheet import build

SPEC=ROOT/'docs/asset_catalog/lote1_spec.json'
SHEET_DIR=ROOT/'unity/Assets/Resources/Sprites/Demons'
PREVIEW_DIR=ROOT/'docs/asset_catalog/previews'

CREATURES=build_creatures()


def draw(ctx,payload):
    creature_id,anim,t,view=payload
    creature=CREATURES[creature_id]
    creature.draw(ctx,view,creature.pose(anim,t,view))


def anim_frame(sheet,meta,anim,view,progress=.5):
    item=next(a for a in meta['anims'] if a['name']==anim+'_'+view)
    k=item['start']+min(item['count']-1,int((item['count']-1)*progress))
    fw,fh,cols=meta['frameW'],meta['frameH'],meta['cols']
    x=k%cols*fw;y=k//cols*fh
    return sheet.crop((x,y,x+fw,y+fh)).convert('RGBA')


def thumb(src,w,h):
    ratio=min((w-8)/src.width,(h-8)/src.height)
    return src.resize((max(1,int(src.width*ratio)),max(1,int(src.height*ratio))),Image.Resampling.LANCZOS)


def main():
    SPEC_DATA=json.loads(SPEC.read_text(encoding='utf-8'))
    roster=SPEC_DATA['roster']
    PREVIEW_DIR.mkdir(parents=True,exist_ok=True)
    for entry in roster:
        id_=entry['id']
        if id_ not in CREATURES:
            continue  # Oni and Grakk are already generated in a separate audited pipeline.
        character=CREATURES[id_]
        a=entry['animations']['tracks']
        jobs=[]
        for stage in a:
            name=stage['id'];n=stage['frames_per_direction']
            for view in entry['animations']['directions']:
                data=[(id_,name,i/n if stage['loop'] else i/max(n-1,1),view) for i in range(n)]
                jobs.append((name+'_'+view,data,stage['fps'],stage['loop'],stage['event_frame']))
        v=entry['visual']
        print('Generating',id_,'with',sum(a['frames_per_direction']*3 for a in entry['animations']['tracks']),'frames',flush=True)
        sheet,meta,_=build(id_,'Demons',v['frameW'],v['frameH'],v['pivotX'],v['frameH']-v['pivotY'],jobs,draw)
        preview_states=['idle','move','attack','cast']+(['skill_2'] if entry['kind']=='boss' else [])
        cellw=208;cellh=220
        contact=Image.new('RGB',(cellw*3,cellh*len(preview_states)+26),(26,23,38))
        pen=ImageDraw.Draw(contact)
        pen.text((12,6),id_+' - frames do atlas HD (NAO e screenshot do Unity)',fill=(248,214,173))
        for row,action in enumerate(preview_states):
            for col,view in enumerate(('down','up','side')):
                frame=anim_frame(sheet,meta,action,view,.45 if action in ('attack','cast','skill_2') else .16)
                tile=Image.new('RGBA',(cellw,cellh-20),(37,33,54,255))
                img=thumb(frame,cellw-4,cellh-23)
                tile.alpha_composite(img,((cellw-img.width)//2,(tile.height-img.height)//2))
                at=(col*cellw,26+row*cellh)
                contact.paste(tile.convert('RGB'),at)
                ImageDraw.Draw(contact).text((at[0]+8,at[1]+cellh-16),action+' / '+view,fill=(219,197,163))
        contact.save(PREVIEW_DIR/(id_+'.png'),optimize=True)
    def draw_overview(group,filename,columns,w=225,h=232):
        rows=(len(group)+columns-1)//columns
        image=Image.new('RGB',(columns*w,rows*h+64),(25,23,39))
        d=ImageDraw.Draw(image)
        d.text((15,10),'LOTE 1 - '+filename+' | sprites gerados no pipeline HD cartoon',fill=(242,212,171))
        d.text((15,29),'Previas de frames do atlas. NAO sao screenshots do jogo.',fill=(183,176,168))
        for i,item in enumerate(group):
            path=SHEET_DIR/(item['id']+'.png')
            if not path.exists():
                raise FileNotFoundError(path)
            meta=json.loads((SHEET_DIR/(item['id']+'.json')).read_text(encoding='utf-8'))
            with Image.open(path) as im:frame=anim_frame(im,meta,'idle','down',0.0)
            bg=Image.new('RGBA',(w-8,h-29),(39,36,57,255))
            mini=thumb(frame,w-25,h-38)
            bg.alpha_composite(mini,((bg.width-mini.width)//2,(bg.height-mini.height)//2))
            x=(i%columns)*w+4;y=64+(i//columns)*h
            image.paste(bg.convert('RGB'),(x,y))
            d.text((x+4,y+h-23),item['id'],fill=(241,209,168))
        image.save(PREVIEW_DIR/(filename+'.png'),optimize=True)
    draw_overview(roster[:10],'LOTE1_DEMONIOS',5)
    draw_overview(roster[10:],'LOTE1_CHEFES',5,w=245,h=254)
    print('Completed all 13 creature atlases and 2 overview galleries')

if __name__=='__main__':
    main()