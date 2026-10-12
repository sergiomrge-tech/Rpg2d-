"""Render the original HD cartoon Astral Lynx summoned ally and a TRUE preview."""
from __future__ import annotations
import os
from PIL import Image,ImageDraw
from astral_lynx import build_spirit,FW,FH

ROOT=os.path.abspath(os.path.join(os.path.dirname(__file__),"..",".."))


def main():
    sheet,meta,_=build_spirit()
    labels=("idle_down","idle_up","idle_side","move_side","cast_down","cast_side")
    board=Image.new("RGBA",(6*216,264),(24,31,48,255))
    d=ImageDraw.Draw(board)
    d.text((14,13),"ASTRAL LYNX - summoned ally made from production sprite frames",fill=(194,249,223))
    d.text((14,32),"6 real atlas frames / no concepts / battle animations are in the PNG",fill=(190,197,207))
    for i,name in enumerate(labels):
        a=next(x for x in meta["anims"] if x["name"]==name)
        idx=a["start"]+min(3,a["count"]-1)
        left=(idx%meta["cols"])*FW;top=(idx//meta["cols"])*FH
        frame=sheet.crop((left,top,left+FW,top+FH))
        backdrop=Image.new("RGBA",(205,190),(39,45,60,255))
        backdrop.alpha_composite(frame.resize((205,190),Image.Resampling.LANCZOS))
        board.alpha_composite(backdrop,(i*216+5,57))
        d.text((i*216+9,251),name,fill=(238,233,222))
    dest=os.path.join(ROOT,"docs","asset_catalog","previews","classes")
    os.makedirs(dest,exist_ok=True)
    board.convert("RGB").save(os.path.join(dest,"pet_astral_lynx.png"),optimize=True)
    print("REAL pet atlas:",sum(a["count"] for a in meta["anims"]),"frames,",
          len(meta["anims"]),"animation tracks")


if __name__=="__main__":
    main()
