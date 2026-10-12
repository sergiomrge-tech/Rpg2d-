"""Validate FIVE actual 2-skill boss atlases and frame motion; no mockups.

PNG/JSON assets must be in Unity Resources. 7 states * 3 directions =21
tracks per boss, 105 distinct real atlas animation tracks total.
This test is NOT a Unity Editor runtime test.
"""
from pathlib import Path
import hashlib,json
from PIL import Image,ImageChops
ROOT=Path(__file__).resolve().parents[2]
ATLAS=ROOT/"unity/Assets/Resources/Sprites/Demons"
PREVIEW=ROOT/"docs/asset_catalog/previews/lote2/bosses"
IDS=("mantis_high_reaper","scarab_colossus","moth_oracle",
     "queen_vespara","brood_tyrant")
STATES=("idle","move","attack","cast","skill_2","hurt","death")
VIEWS=("down","up","side")

def changed(a,b):
    dif=ImageChops.difference(a,b)
    return dif.getchannel("A").getbbox() is not None or dif.convert("RGB").getbbox() is not None

def verify():
    digests=[]
    for id_ in IDS:
        image_file=ATLAS/(id_+".png")
        json_file=ATLAS/(id_+".json")
        preview_file=PREVIEW/(id_+".png")
        assert image_file.is_file() and json_file.is_file() and preview_file.is_file(),id_
        meta=json.loads(json_file.read_text(encoding="utf-8"))
        assert (meta["frameW"],meta["frameH"])==(384,384),id_
        assert 0<meta["pivotX"]<384 and 0<meta["pivotY"]<384
        assert len(meta["anims"])==21
        mapped={entry["name"]:entry for entry in meta["anims"]}
        assert set(mapped)=={state+"_"+view for state in STATES for view in VIEWS}
        count=0
        with Image.open(image_file) as im:
            im.load()
            assert im.mode=="RGBA"
            assert im.width<=4096 and im.height<=8192 and im.width==384*meta["cols"] and im.height%384==0
            assert (im.width//384)*(im.height//384)>=sum(x["count"] for x in meta["anims"])
            def grab(index):
                x=(index%meta["cols"])*384;y=(index//meta["cols"])*384
                return im.crop((x,y,x+384,y+384))
            for entry in meta["anims"]:
                assert entry["start"]==count,(id_,entry["name"],count,entry["start"])
                assert entry["count"]>=5 and 8<=entry["fps"]<=25
                assert entry["loop"]==(entry["name"].startswith(("idle_","move_")))
                if entry["name"].startswith(("attack_","cast_","skill_2_")):
                    assert 0<=entry["hit"]<entry["count"]
                else: assert entry["hit"]==-1
                first=grab(entry["start"])
                later=grab(entry["start"]+entry["count"]//2)
                assert first.getchannel("A").getbbox() and later.getchannel("A").getbbox()
                assert changed(first,later),(id_,entry["name"],"static motion")
                count+=entry["count"]
            for state in STATES:
                front=mapped[state+"_down"]
                back=mapped[state+"_up"]
                side=mapped[state+"_side"]
                im1=grab(front["start"]+front["count"]//2)
                im2=grab(back["start"]+back["count"]//2)
                im3=grab(side["start"]+side["count"]//2)
                assert changed(im1,im2),(id_,state,"back matches front")
                assert changed(im1,im3),(id_,state,"side matches front")
            # Detect severe clipping, including the longest antennae and sting.
            for state in ("idle","attack","cast","skill_2","death"):
                entry=mapped[state+"_down"]
                frame=grab(entry["start"]+entry["count"]//2)
                bounds=frame.getchannel("A").getbbox()
                assert bounds is not None
                assert bounds[0]>=1 and bounds[1]>=1 and bounds[2]<=383 and bounds[3]<=383,(id_,state,"edge clipping",bounds)
        with Image.open(preview_file) as prev:prev.verify()
        digests.append(hashlib.sha256(image_file.read_bytes()).hexdigest())
        print("BOSS VERIFIED",id_,"21 states, 3 directions, two frame-based skills",flush=True)
    assert len(set(digests))==len(IDS),"Two bosses have identical atlases"
    print("ALL FIVE REAL BOSS ATLASES PASS. UNITY EDITOR VALIDATION PENDING.")

if __name__=="__main__":verify()
