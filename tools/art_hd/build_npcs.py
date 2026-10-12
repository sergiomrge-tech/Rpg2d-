"""NPC sheets (idle + walk, 3 views) reusing the hero rig with different looks."""
from humanoid import Look
from core import Pal, hx
from build_hero import jobs_for, draw, FW, FH, OX, OY
from anims import ANIMS
from sheet import build

SUB = {k: ANIMS[k] for k in ('idle', 'walk')}
LOOKS = {
    'guild_clerk': Look(hair_style='long', hair=Pal('#a8502e', '#7e3820', '#d47a4a', '#3a160a'), eye=hx('#3fa86a'),
                        tunic=Pal('#8a2f45', '#6a2035', '#b24a62', '#2e0a16'), scarf_on=False, weapon=None),
    'merchant': Look(hair=Pal('#5a4a40', '#3e322b', '#7e6a5c', '#1c1410'), tunic=Pal('#7a5236', '#5a3a24', '#9e7050', '#2a180c'),
                     shirt=Pal('#9a9aa8', '#76768a', '#c0c0cc', '#2a2a36'), scarf_on=False, weapon=None),
    'villager': Look(hair_style='long', hair=Pal('#b8b0a8', '#8e8680', '#e0dad4', '#3a3632'),
                     tunic=Pal('#4e8a4a', '#386a36', '#72ae6a', '#163016'), scarf_on=False, weapon=None),
}
if __name__ == '__main__':
    for n, L in LOOKS.items():
        build(n, 'Chars', FW, FH, OX, OY, jobs_for(L, SUB), draw)
