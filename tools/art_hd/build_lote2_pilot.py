"""Render three truly different insectoid enemies as real Unity Resources atlases.

Output: 3 PNG + 3 JSON + 3 isolated frame previews (not game screenshots).
No AI-generated poster or image used as a runtime sprite.
"""
from __future__ import annotations
import json
from pathlib import Path
from PIL import Image,ImageDraw
from sheet import build
from lote2_insects import CREATURES

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'docs/asset_catalog/previews/lote2'
VIEW=('down','up','side')

def draw(c,payload):
    id_,act,t,view=payload
    model=CREATURES[id_]
    model.draw(c,view,model.pose(act,t,view))

def crop_at(im,meta,name):
    stage=next(z for z in meta['anims'] if z['name']==name)
    idx=stage['start']+int((stage['count']-1)*(.4 if name.startswith(('cast','attack')) else .1))
    w,h,cols=meta['frameW'],meta['frameH'],meta['cols']
    return im.crop(((idx%cols)*w,(idx//cols)*h,(idx%cols+1)*w,(idx//cols+1)*h))

def build_one(model):
    jobs=[]
    for state,(count,fps,loop,hit) in model.ANIMS.items():
        for view in VIEW:
            frames=[(model.name,state,i/count if loop else i/(count-1),view) for i in range(count)]
            jobs.append((state+'_'+view,frames,fps,loop,hit))
    sheet,meta,_=build(model.name,'Demons',model.FW,model.FH,model.OX,model.OY,jobs,draw)
    OUT.mkdir(parents=True,exist_ok=True)
    tile=224;header=40
    canvas=Image.new('RGB',(tile*3,header+tile*6),(26,23,39))
    painter=ImageDraw.Draw(canvas)
    painter.text((12,10),model.name+' / FRAMES REAIS DO ATLAS HD; NAO screenshot Unity',fill=(247,210,159))
    for row,state in enumerate(model.ANIMS):
        for col,view in enumerate(VIEW):
            frame=crop_at(sheet,meta,state+'_'+view).convert('RGBA')
            bg=Image.new('RGBA',(tile-4,tile-27),(39,35,56,255))
            f=frame.copy()
            ratio=min((tile-14)/f.width,(tile-38)/f.height)
            f=f.resize((round(f.width*ratio),round(f.height*ratio)),Image.Resampling.LANCZOS)
            bg.alpha_composite(f,((bg.width-f.width)//2,(bg.height-f.height)//2))
            x=col*tile+2;y=header+row*tile
            canvas.paste(bg.convert('RGB'),(x,y))
            painter.text((x+8,y+tile-22),state+' / '+view,fill=(225,204,178))
    canvas.save(OUT/(model.name+'.png'),optimize=True)
    print('REAL ANIMATED SPRITE',model.name,len(meta['anims']),'directional tracks')

def main():
    for model in CREATURES.values():build_one(model)
    print('Lote 2 pilot sheets and preview frames generated. Unity validation pending.')

if __name__=='__main__':main()