"""Static integrity checks for generated Aetheria HUD art. No Unity license required."""
from __future__ import annotations

import json
from pathlib import Path
from PIL import Image

BASE = Path(__file__).resolve().parents[2] / 'unity/Assets/Resources/Sprites/Ui'
EXPECTED = {
    'arc_hp_track': (440, 440), 'arc_hp_fill': (440, 440),
    'arc_mp_track': (440, 440), 'arc_mp_fill': (440, 440),
    'arc_st_track': (440, 440), 'arc_st_fill': (440, 440),
    'medallion': (300, 300), 'orb': (144, 144),
    'orb_shade': (144, 144), 'smear': (620, 420),
    'flourish': (560, 64), 'nameplate': (480, 70),
    'dialogue_band': (1920, 380), 'vignette': (1920, 1080),
    'pill_track': (104, 22), 'pill_fill': (104, 22),
    'portrait': (256, 256), 'portrait_hero': (256, 256),
    'portrait_receptionist': (256, 256), 'portrait_blacksmith': (256, 256),
    'portrait_villager': (256, 256), 'icons': (480, 192),
}
ICON_IDS = {
    'coin', 'skill_sword', 'skill_spark', 'skill_roll',
    'potion', 'ether', 'horn', 'ember', 'tome'
}


def check():
    for name, size in EXPECTED.items():
        path = BASE / (name + '.png')
        if not path.is_file():
            raise AssertionError('Missing PNG: ' + str(path))
        with Image.open(path) as image:
            image.verify()
        with Image.open(path) as image:
            if image.size != size or image.mode != 'RGBA':
                raise AssertionError(f'{name}: unexpected mode/size {image.mode} {image.size}')
            if image.getchannel('A').getbbox() is None:
                raise AssertionError(f'{name}: empty alpha channel')
    meta = json.loads((BASE / 'icons.json').read_text(encoding='utf-8'))
    assert (meta['frameW'], meta['frameH'], meta['cols']) == (96, 96, 5)
    anims = meta['anims']
    assert len(anims) == len(ICON_IDS)
    assert {a['name'] for a in anims} == ICON_IDS
    assert {a['start'] for a in anims} == set(range(len(ICON_IDS)))
    assert all(a['count'] == 1 for a in anims)
    print(f'HUD ART OK: {len(EXPECTED)} verified RGBA textures, {len(ICON_IDS)} icons')


if __name__ == '__main__':
    check()
