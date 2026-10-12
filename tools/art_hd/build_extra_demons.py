"""Build the catalog-only Oni Soldier and Grakk, using the existing HD sheet builder.

This script intentionally does not register enemies in Data.Demons or spawn them:
new combat characters are kept separate until Unity screenshot/playtesting.
"""
from __future__ import annotations

import json
import math
from pathlib import Path

from PIL import Image, ImageDraw

from extra_demons import EXTRA_DEMONS
from sheet import OUT, build

VIEWS=('down','up','side')
BY_NAME={d.name:d for d in EXTRA_DEMONS}
ROOT=Path(__file__).resolve().parents[2]


def draw(ctx,payload):
    demon_id,anim,t,view=payload
    demon=BY_NAME[demon_id]
    demon.draw(ctx,view,demon.pose(anim,t,view))


def preview(demon,atlas,meta):
    """Contact sheet of actual generated animation frames; NOT a game screenshot."""
    w,h=meta['frameW'],meta['frameH']
    out=Image.new('RGB',(w*3,h*4+32),(26,24,38))
    painter=ImageDraw.Draw(out)
    painter.text((12,8),demon.name+' - original HD animation previews - NOT a Unity screenshot',
                 fill=(234,205,160))
    for row,an in enumerate(('idle','move','attack','cast')):
        for col,view in enumerate(VIEWS):
            a=next(x for x in meta['anims'] if x['name']==an+'_'+view)
            index=a['start']+max(0,(a['count']//2 if an in ('attack','cast') else 1))
            sx=(index%meta['cols'])*w
            sy=(index//meta['cols'])*h
            frame=atlas.crop((sx,sy,sx+w,sy+h))
            rgba=Image.new('RGBA',(w,h),(38,38,53,255))
            rgba.alpha_composite(frame)
            out.paste(rgba.convert('RGB'),(col*w,32+row*h))
    d=ROOT/'docs'/'asset_catalog'/'previews'
    d.mkdir(parents=True,exist_ok=True)
    out.save(d/(demon.name+'.png'),optimize=True)


def main():
    selected=list(BY_NAME)
    for name in selected:
        d=BY_NAME[name]
        jobs=[]
        for anim,(n,fps,loop,hit) in d.ANIMS.items():
            for view in VIEWS:
                frames=[(d.name,anim,i/n if loop else i/max(1,n-1),view) for i in range(n)]
                jobs.append((anim+'_'+view,frames,fps,loop,hit))
        image,meta,_=build(name,'Demons',d.FW,d.FH,d.OX,d.OY,jobs,draw)
        preview(d,image,meta)


if __name__=='__main__':
    main()
