"""Build FIVE playable Unity 2D boss atlases with two skills each.

PNG+JsonUtility JSON go directly into Unity/Assets/Resources/Sprites/Demons;
preview images show ACTUAL rendered frames, not concept art/screenshots.
"""
from __future__ import annotations
from pathlib import Path
from PIL import Image, ImageDraw
from sheet import build
from lote2_bosses import BOSSES

ROOT=Path(__file__).resolve().parents[2]
PRE=ROOT/"docs/asset_catalog/previews/lote2/bosses"
DIRECTIONS=("down","up","side")

def draw(ctx,data):
    id_,state,t,view=data
    boss=BOSSES[id_]
    boss.draw(ctx,view,boss.pose(state,t,view))

def frame_crop(sheet,meta,key):
    a=next(x for x in meta["anims"] if x["name"]==key)
    k=a["start"]+int((a["count"]-1)*(.65 if key.startswith(("attack_","cast_","skill_2_")) else .25))
    w,h,cols=meta["frameW"],meta["frameH"],meta["cols"]
    return sheet.crop(((k%cols)*w,(k//cols)*h,(k%cols+1)*w,(k//cols+1)*h)).convert("RGBA")

def build_boss(model):
    jobs=[]
    for stage,(n,fps,loop,hit) in model.ANIMS.items():
        for direction in DIRECTIONS:
            frames=[(model.name,stage,i/n if loop else i/(n-1),direction) for i in range(n)]
            jobs.append((stage+"_"+direction,frames,fps,loop,hit))
    sheet,meta,_=build(model.name,"Demons",model.FW,model.FH,
                       model.OX,model.OY,jobs,draw,outline=1.2)
    assert len(meta["anims"])==21
    assert sheet.width<=4096 and sheet.height<=8192,(model.name,sheet.size)
    PRE.mkdir(parents=True,exist_ok=True)
    tile=240; header=45; states=tuple(model.ANIMS)
    preview=Image.new("RGB",(tile*3,header+tile*len(states)),(24,22,38))
    painter=ImageDraw.Draw(preview)
    painter.text((12,10),model.name+" / SPRITES REAIS HD - NAO print Unity",
                 fill=(241,206,160))
    for row,state in enumerate(states):
        for col,view in enumerate(DIRECTIONS):
            sprite=frame_crop(sheet,meta,state+"_"+view)
            back=Image.new("RGBA",(tile-4,tile-28),(41,35,53,255))
            box=sprite.getchannel("A").getbbox()
            assert box is not None,(model.name,state,view,"empty frame")
            sprite=sprite.crop(box)
            ratio=min((back.width-12)/sprite.width,(back.height-11)/sprite.height)
            sprite=sprite.resize((max(1,round(sprite.width*ratio)),
                                  max(1,round(sprite.height*ratio))),Image.Resampling.LANCZOS)
            back.alpha_composite(sprite,((back.width-sprite.width)//2,
                                         (back.height-sprite.height)//2))
            px=col*tile+2;py=header+row*tile
            preview.paste(back.convert("RGB"),(px,py))
            painter.text((px+8,py+tile-22),state+" / "+view,fill=(226,212,189))
    preview.save(PRE/(model.name+".png"),optimize=True)
    print("BOSS READY AS ATLAS",model.name,len(meta["anims"]),"tracks",sheet.size,flush=True)

def main():
    for boss in BOSSES.values():
        build_boss(boss)
    print("All five boss atlases rendered. Real Unity runtime not yet tested.")

if __name__=="__main__":main()
