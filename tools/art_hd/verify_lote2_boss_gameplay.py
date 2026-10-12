"""Static contract for five scripted boss fights in the real Unity project.

Does not pretend Unity 2022.3 was opened; compile and sprite render have
their own CI jobs and genuine editor screenshots are still required.
"""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[2]
MAP=ROOT/"unity/Assets/Resources/Maps/village.json"
DIR=ROOT/"unity/Assets/Scripts/Game"
IDS=("mantis_high_reaper","scarab_colossus","moth_oracle",
     "queen_vespara","brood_tyrant")
BEHAVIOR=("boss_reaper","boss_scarab","boss_moth","boss_vespara","boss_brood")
TRIO=("down","up","side")
def main():
    m=json.loads(MAP.read_text(encoding="utf-8"))
    assert len(m["spawns"])==23
    assert sum(p["kind"]=="imp" for p in m["spawns"])==8
    assert len([x for x in m["spawns"] if x["kind"] in IDS])==5
    old=("mantis_reaver","scarab_brute","moth_hexer",
         "termite_burrower","vespa_lancer","cicada_screecher",
         "ant_guard","roach_plaguebearer","spike_beetle","dragonfly_skirmisher")
    for id_ in old:
        assert sum(p["kind"]==id_ for p in m["spawns"])==1,id_
    data=(DIR/"Data.cs").read_text()
    enemy=(DIR/"Enemy.cs").read_text()
    abilities=(DIR/"InsectBossSkills.cs").read_text()
    proj=(DIR/"Projectile.cs").read_text()
    script=(DIR/"Game.cs").read_text()
    for id_,behavior in zip(IDS,BEHAVIOR):
        sp=[p for p in m["spawns"] if p["kind"]==id_]
        assert len(sp)==1,(id_,"not spawned exactly once")
        p=sp[0]
        gx=p["x"]//m["tile"]
        gy=p["y"]//m["tile"]
        assert 0<=gx<m["w"] and 0<=gy<m["h"]
        assert m["blocked"][gy*m["w"]+gx]=="0",(id_,"blocked tile")
        assert '"'+id_+'"' in data and '"'+id_+'"' in abilities and '"'+id_+'"' in script
        assert 'behavior = "'+behavior+'"' in data
        assert 'boss = true' in data
    assert enemy.count('anim.Play("skill_2", true)')>=2
    assert 'a == "skill_2" && state == St.Cast2' in enemy
    assert 'InsectBossSkills.Execute(this, 1, skillDirection)' in enemy
    assert 'InsectBossSkills.Execute(this, 2, skillDirection)' in enemy
    assert 'ActivateBossGuard(3.8f)' in abilities
    assert 'Enemy.Spawn("ant_guard"' in abilities
    assert 'InsectHazard.SpawnPoison' in abilities
    assert 'Projectile.VenomDart(' in abilities and 'public static Projectile VenomDart' in proj
    assert 'Player.I.ApplyVenom(3.0f)' in proj
    assert 'CiCastSkill2' in enemy
    assert 'CameraRig.Shake(' in abilities
    assert 'InsectBossAtlasImporter' in (ROOT/"unity/Assets/Editor/InsectBossAtlasImporter.cs").read_text()
    print("QA PASS: all 5 optional bosses on free tiles; 10 existing demons and story imps untouched.")
    print("QA PASS: 10 individual abilities, keyed animations, venom, summons, shell defence, AOE, CI screenshots.")
    print("WARNING: Real Unity Editor/Windows build, animation feel, FPS and visual quality pending.")

if __name__=="__main__":main()
