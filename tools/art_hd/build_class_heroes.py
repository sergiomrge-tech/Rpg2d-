"""Render six actual class-dependent character sprite atlases for Godot.

Never overwrites the approved 'hero.png'. Uses the original Aetheria
Cairo HD materials and the original 10 fully animated states in 3 views.
Run: python tools/art_hd/build_class_heroes.py [warrior mage ...]
"""
from __future__ import annotations
import os
import sys
from PIL import Image,ImageDraw
from anims import ANIMS
from sheet import build
from class_hero_rigs import IDS,draw

FW,FH,OX,OY=192,176,96,150
VIEWS=("down","up","side")
ROOT=os.path.abspath(os.path.join(os.path.dirname(__file__),"..",".."))


def jobs_for(kind):
    jobs=[]
    for anim,(n,fps,loop,hit) in ANIMS.items():
        for view in VIEWS:
            payloads=[(kind,anim,(i/n if loop else i/max(1,n-1)),view) for i in range(n)]
            jobs.append((anim+"_"+view,payloads,fps,loop,hit))
    return jobs


def _crop(img,meta,track,frame=2):
    rec=next(x for x in meta["anims"] if x["name"]==track)
    idx=rec["start"]+min(frame,rec["count"]-1)
    xx=(idx%meta["cols"])*FW
    yy=(idx//meta["cols"])*FH
    return img.crop((xx,yy,xx+FW,yy+FH))


def preview(kind,img,meta):
    labels=("idle_down","idle_up","idle_side","walk_side","attack1_down","cast_down")
    w,h=6*226,272
    board=Image.new("RGBA",(w,h),(27,28,43,255))
    d=ImageDraw.Draw(board)
    d.text((16,10),kind.upper()+" | 6 authentic frames from in-game animation atlas",fill=(243,208,145,255))
    d.text((16,30),"HD cartoon / 3 directions / weapon-silhouette gate / NOT a Godot screenshot",fill=(195,188,197,255))
    for i,name in enumerate(labels):
        crop=_crop(img,meta,name)
        # Resolution-independent aspect ratio and natural transparency.
        crop=crop.resize((212,194),Image.Resampling.LANCZOS)
        panel=Image.new("RGBA",(212,194),(38,40,57,255))
        panel.alpha_composite(crop,(0,0))
        board.alpha_composite(panel,(i*226+7,58))
        d.text((i*226+14,255),name,fill=(230,222,207,255))
    folder=os.path.join(ROOT,"docs","asset_catalog","previews","classes")
    os.makedirs(folder,exist_ok=True)
    board.convert("RGB").save(os.path.join(folder,kind+".png"),optimize=True)


def main():
    ids=tuple(sys.argv[1:]) or IDS
    assert ids and len(set(ids))==len(ids)
    for kind in ids:
        if kind not in IDS:
            raise SystemExit("Unsupported class "+kind)
        img,meta,_=build("hero_"+kind,"Chars",FW,FH,OX,OY,jobs_for(kind),draw,outline=1.0)
        preview(kind,img,meta)
        print(kind,":",len(meta["anims"]),"tracks =",sum(x["count"] for x in meta["anims"]),"frames")
    print("FINISHED: rendered class hero sheets; Unity/Godot runtime and final art approval separate gates")


if __name__=="__main__":
    main()
