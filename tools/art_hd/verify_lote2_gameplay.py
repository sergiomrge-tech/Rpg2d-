"""Validate live Lote 2 gameplay wiring (static contract, not a Unity runtime test)."""
from __future__ import annotations
import json,re
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
SCR=ROOT/'unity/Assets/Scripts/Game'
MAP=ROOT/'unity/Assets/Resources/Maps/village.json'
ART=ROOT/'unity/Assets/Resources/Sprites/Demons'
IDS=('mantis_reaver','scarab_brute','moth_hexer')
BEHAVIORS={'mantis_reaver':'mantis_dash','scarab_brute':'scarab_shockwave','moth_hexer':'moth_hex'}

def test():
    m=json.loads(MAP.read_text(encoding='utf-8'))
    spawns=[s for s in m['spawns'] if s['kind'] in IDS]
    assert len(spawns)==3 and len({x['kind'] for x in spawns})==3
    for s in spawns:
        x,y=s['x']//m['tile'],s['y']//m['tile']
        assert 0<=x<m['w'] and 0<=y<m['h']
        assert m['blocked'][y*m['w']+x]=='0',(s['kind'],'blocked map tile')
        assert (ART/(s['kind']+'.png')).exists()
        assert (ART/(s['kind']+'.json')).exists()
    data=(SCR/'Data.cs').read_text(encoding='utf-8')
    enemy=(SCR/'Enemy.cs').read_text(encoding='utf-8')
    player=(SCR/'Player.cs').read_text(encoding='utf-8')
    proj=(SCR/'Projectile.cs').read_text(encoding='utf-8')
    for kind,behavior in BEHAVIORS.items():
        assert 'Demons["'+kind+'"]' in data
        assert 'behavior = "'+behavior+'"' in data
        assert 'def.behavior == "'+behavior+'"' in enemy
    assert 'Projectile.HexSpore(' in enemy and 'public static Projectile HexSpore(' in proj
    assert 'ApplyHexSlow' in player and 'Player.I.ApplyHexSlow' in proj
    assert 'Fx.Shockwave(' in enemy and 'skillDirection * 10.5f' in enemy
    assert 'anim.Play("cast", true)' in enemy
    assert 'if ((a == "attack" && state == St.Attack)' in enemy
    assert sum(s['kind']=='imp' for s in m['spawns'])==8,'original imps changed'
    print('GAMEPLAY WIRING VERIFIED: 3 on-map enemies, unique abilities, slow effect, no original quest disruption')
    print('Unity runtime, timing, collision, actual gameplay and visual fidelity still unverified')

if __name__=='__main__':test()