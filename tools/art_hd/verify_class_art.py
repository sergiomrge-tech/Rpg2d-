"""Production asset QA for six distinct class hero rigs and a bespoke pet.

Verifies files the Godot engine actually loads, real non-static frame data,
all directional attack/move/cast clips, portrait crops and strict class IDs.
Does NOT assert a completed visual/art approval or Android playtest.
"""
from __future__ import annotations
import json
from pathlib import Path
from PIL import Image, ImageChops

ROOT=Path(__file__).resolve().parents[2]
SPR=ROOT/"godot/assets/Sprites"
SRC=ROOT/"godot/scripts"
PRE=ROOT/"docs/asset_catalog/previews/classes"
CLASSES=("warrior","mage","archer","paladin","assassin","summoner")
HERO_STATES=("idle","walk","run","attack1","attack2","attack3",
             "cast","roll","hurt","death")
PET_STATES=("idle","move","attack","cast","hurt","death")
DIRECTIONS=("down","up","side")


def changed(a,b):
    delta=ImageChops.difference(a,b)
    return delta.getchannel("A").getbbox() is not None or delta.convert("RGB").getbbox() is not None


def verify(id_,sub,states,fw,fh):
    path=SPR/sub/id_
    assert path.with_suffix(".png").is_file(),(id_,"missing sprite")
    assert path.with_suffix(".json").is_file(),(id_,"missing metadata")
    obj=json.loads(path.with_suffix(".json").read_text(encoding="utf-8"))
    assert obj["frameW"]==fw and obj["frameH"]==fh,(id_,"frame size")
    tracks=obj["anims"]
    assert len(tracks)==len(states)*len(DIRECTIONS),(id_,"track count",len(tracks))
    expected={action+"_"+view for action in states for view in DIRECTIONS}
    assert {a["name"] for a in tracks}==expected,(id_,"missing tracks")
    names={a["name"]:a for a in tracks}
    with Image.open(path.with_suffix(".png")) as im:
        assert im.mode=="RGBA",(id_,"must be transparent RGBA")
        assert im.width==fw*obj["cols"] and im.height%fh==0
        assert im.width<=4096,(id_,"Godot texture maximum")
        alpha=im.getchannel("A")
        assert alpha.getextrema()==(0,255),(id_,"transparent background lost")
        def frame(name,offset=0):
            a=names[name]
            ix=a["start"]+min(offset,a["count"]-1)
            return im.crop((ix%obj["cols"]*fw,ix//obj["cols"]*fh,
                            (ix%obj["cols"]+1)*fw,(ix//obj["cols"]+1)*fh))
        for action in states:
            for view in DIRECTIONS:
                a=names[action+"_"+view]
                assert a["count"]>=5 and a["fps"]>=8,(id_,action,view)
                assert a["start"]+a["count"]<=im.height//fh*obj["cols"]
                if action in ("cast","attack1","attack2","attack3","attack"):
                    assert 0<=a["hit"]<a["count"],(id_,action,"no frame hit")
                assert changed(frame(action+"_"+view,0),
                               frame(action+"_"+view,a["count"]//2)),(id_,action,view,"static animation")
            assert changed(frame(action+"_down",2),frame(action+"_up",2)),(id_,action,"same front/back")
            assert changed(frame(action+"_down",2),frame(action+"_side",2)),(id_,action,"same side")
        assert frame("idle_down",2).getchannel("A").getbbox(),(id_,"empty figure")
        stamp=frame("idle_down",2).tobytes()
    return stamp,len(tracks),sum(a["count"] for a in tracks)


def main():
    signatures=[]
    frames=0
    for kind in CLASSES:
        digest,count,n=verify("hero_"+kind,"Chars",HERO_STATES,192,176)
        signatures.append(digest);frames+=n
        portrait=SPR/"Ui"/"ClassPortraits"/(kind+".png")
        assert portrait.is_file(),(kind,"missing real atlas-derived portrait")
        with Image.open(portrait) as img:
            assert img.mode=="RGBA" and img.size==(148,174)
            assert img.getchannel("A").getbbox(),(kind,"empty portrait")
        assert (PRE/(kind+".png")).is_file(),(kind,"missing contact preview")
        assert count==30
    assert len(set(signatures))==6,"some class atlases share the same exact idle sprite"
    pet,tracks,pet_n=verify("astral_lynx","Pets",PET_STATES,192,176)
    assert tracks==18 and pet_n>100
    assert (PRE/"pet_astral_lynx.png").is_file()
    hero=(SRC/"game/player.gd").read_text(encoding="utf-8")
    spirit=(SRC/"game/spirit_pet.gd").read_text(encoding="utf-8")
    selector=(SRC/"ui/class_select.gd").read_text(encoding="utf-8")
    classes=(SRC/"game/hero_classes.gd").read_text(encoding="utf-8")
    assert "HeroClasses.sheet_for(state_.class_id)" in hero
    assert '"Sprites/Pets/astral_lynx"' in spirit
    assert "Sprites/Ui/ClassPortraits/" in selector
    assert '"Sprites/Chars/hero_"' in classes
    assert 'visual.hit.connect(_on_visual_hit)' in spirit
    assert 'track != "cast"' in spirit
    assert 'Projectile.spark(' in spirit
    print(f"PASS 6 class hero sprite sheets: 180 animated directional tracks, {frames} total frames.")
    print(f"PASS 1 original pet sprite atlas: 18 tracks, {pet_n} real frames.")
    print("PASS six real class-select portrait PNGs, 7 contact galleries and combat asset routes.")
    print("PENDING visual direction + actual native Godot game renders, gameplay QA and Android APK.")


if __name__=="__main__":
    main()
