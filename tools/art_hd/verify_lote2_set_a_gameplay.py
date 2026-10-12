"""Static QA: six REAL forest enemies with Unity combat and status wiring.

Requires all six render-produced files to be in Resources. Does not claim
runtime playtesting or visual approval.
"""
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
SCRIPTS=ROOT/'unity/Assets/Scripts/Game'
ART=ROOT/'unity/Assets/Resources/Sprites/Demons'
MAP=ROOT/'unity/Assets/Resources/Maps/village.json'
IDS={
    'mantis_reaver':'mantis_dash',
    'scarab_brute':'scarab_shockwave',
    'moth_hexer':'moth_hex',
    'termite_burrower':'termite_burrow',
    'vespa_lancer':'vespa_sting',
    'cicada_screecher':'cicada_sonic'
}
ACTIONS=('idle','move','attack','cast','hurt','death')
DIRECTIONS=('down','up','side')

def main():
    map_data=json.loads(MAP.read_text(encoding='utf-8'))
    spawns=map_data['spawns']
    for id_,behavior in IDS.items():
        entries=[s for s in spawns if s['kind']==id_]
        assert len(entries)==1,(id_,len(entries))
        sp=entries[0]
        ix=sp['x']//map_data['tile']
        iy=sp['y']//map_data['tile']
        assert 0<=ix<map_data['w'] and 0<=iy<map_data['h']
        assert map_data['blocked'][iy*map_data['w']+ix]=='0',(id_,'blocked tile')
        assert (ART/(id_+'.png')).exists(),(id_,'missing PNG')
        meta=json.loads((ART/(id_+'.json')).read_text(encoding='utf-8'))
        assert set(z['name'] for z in meta['anims'])=={a+'_'+d for a in ACTIONS for d in DIRECTIONS}
        assert len(meta['anims'])==18
        for a in meta['anims']:
            if a['name'].startswith(('attack_','cast_')):
                assert 0<=a['hit']<a['count']
    assert sum(s['kind']=='imp' for s in spawns)==8,'main story quest must keep 8 original imps'
    assert len(spawns)==14,'wrong total count'
    code={name:(SCRIPTS/name).read_text(encoding='utf-8') for name in
          ('Data.cs','Enemy.cs','Player.cs','Projectile.cs','Game.cs')}
    for id_,behavior in IDS.items():
        assert 'Demons["'+id_+'"]' in code['Data.cs']
        assert 'behavior = "'+behavior+'"' in code['Data.cs']
        assert 'def.behavior == "'+behavior+'"' in code['Enemy.cs']
        assert '"'+id_+'"' in code['Game.cs'],'missing real Unity screenshot tour inclusion'
    assert 'p.ApplyVenom(3.2f)' in code['Enemy.cs']
    assert 'public void ApplyVenom(float seconds)' in code['Player.cs']
    assert 'public void ApplySonicDisrupt(float seconds)' in code['Player.cs']
    assert 'p.ApplySonicDisrupt(.65f)' in code['Enemy.cs']
    assert 'Projectile.HexSpore(' in code['Enemy.cs']
    assert 'skillDirection * burst' in code['Enemy.cs'],'missing directional dig/wasp movement'
    assert 'Fx.Shockwave(' in code['Enemy.cs']
    print('PASSED: 6 insects with real atlas tracks, 6 distinct AI profiles and forest spawns.')
    print('PASSED: venom DOT, sonic disruption, moving attack, hex projectile and screenshot hooks.')
    print('UNITY GAMEPLAY, FPS, ART APPROVAL AND COLLISION STILL NEED ACTUAL EDITOR VALIDATION.')

if __name__=='__main__':
    main()
