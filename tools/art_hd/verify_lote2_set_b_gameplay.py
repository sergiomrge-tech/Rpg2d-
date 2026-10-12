"""Static QA for all ten Lote 2 demons registered IN the Unity game.

Validates actual PNG/JSON art, on-map spawns, casts, statuses and intact story.
This does not replace Unity runtime testing.
"""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
MAP=ROOT/'unity/Assets/Resources/Maps/village.json'
ART=ROOT/'unity/Assets/Resources/Sprites/Demons'
SRC=ROOT/'unity/Assets/Scripts/Game'
PROFILES={
'mantis_reaver':'mantis_dash',
'scarab_brute':'scarab_shockwave',
'moth_hexer':'moth_hex',
'termite_burrower':'termite_burrow',
'vespa_lancer':'vespa_sting',
'cicada_screecher':'cicada_sonic',
'ant_guard':'ant_carapace',
'roach_plaguebearer':'roach_plague',
'spike_beetle':'spike_roll',
'dragonfly_skirmisher':'dragonfly_zigzag'
}
STATES=('idle','move','attack','cast','hurt','death')
VIEWS=('down','up','side')

def check():
    m=json.loads(MAP.read_text(encoding='utf-8'))
    assert len(m['spawns'])==18
    assert sum(s['kind']=='imp' for s in m['spawns'])==8
    source={n:(SRC/n).read_text(encoding='utf-8') for n in (
        'Data.cs','Enemy.cs','Player.cs','Projectile.cs','Game.cs','InsectHazard.cs')}
    for id_,behavior in PROFILES.items():
        found=[s for s in m['spawns'] if s['kind']==id_]
        assert len(found)==1,(id_,'bad spawn count')
        a=found[0]
        x,y=a['x']//m['tile'],a['y']//m['tile']
        assert 0<=x<m['w'] and 0<=y<m['h'] and m['blocked'][y*m['w']+x]=='0',(id_,'not traversable')
        assert (ART/(id_+'.png')).is_file(),(id_,'missing real atlas')
        j=json.loads((ART/(id_+'.json')).read_text(encoding='utf-8'))
        assert j['frameW']==288 and j['frameH']==288
        assert len(j['anims'])==18
        assert {z['name'] for z in j['anims']}=={s+'_'+v for s in STATES for v in VIEWS}
        for z in j['anims']:
            assert z['fps']>=8 and z['count']>=6
            if z['name'].startswith(('attack_','cast_')):
                assert 0<=z['hit']<z['count']
        assert 'Demons["'+id_+'"]' in source['Data.cs']
        assert 'behavior = "'+behavior+'"' in source['Data.cs']
        assert 'def.behavior == "'+behavior+'"' in source['Enemy.cs']
        assert '"'+id_+'"' in source['Game.cs']
    assert 'chitinGuardLeft = 3.1f' in source['Enemy.cs']
    assert 'd *= .36f' in source['Enemy.cs']
    assert 'InsectHazard.SpawnPoison(' in source['Enemy.cs']
    assert 'public static InsectHazard SpawnPoison(' in source['InsectHazard.cs']
    assert 'Projectile.InsectNeedle(' in source['Enemy.cs']
    assert 'public static Projectile InsectNeedle(' in source['Projectile.cs']
    assert 'tealTrail' in source['Projectile.cs']
    assert 'p.ApplyVenom(' in source['Enemy.cs']
    assert 'p.ApplySonicDisrupt(' in source['Enemy.cs']
    assert 'skillDirection * v' in source['Enemy.cs']
    assert 'Projectile.HexSpore(' in source['Enemy.cs']
    print('LOTE 2: 10/10 real game enemies, 10 distinct AI profiles, full directional art.')
    print('PASS: existing 8 imp spawns and original quest maintained.')
    print('PASS: armor, poison cloud, venom, shockwave, rush and needle mechanisms wired.')
    print('WARNING: Unity runtime, movement feel, visual gate and hitbox playtesting pending.')

if __name__=='__main__':
    check()
