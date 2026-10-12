"""Two original HD-cartoon demons sharing Aetheria's Cairo cel-shading rigs.

Oni: horned armoured soldier with an animated iron club, based on the
production humanoid skeleton (NOT a palette-swap of the hero sprite).
Grakk: armoured, runic, winged imp chieftain, based on the production
demon skeleton with boss-specific silhouette details.

Catalogued art only: the spawn/AI/loot table must NOT be changed before
screenshots from the running Unity build pass the visual gate.
"""
from __future__ import annotations

import math

from anims import pose as human_pose
from core import Pal, paint, flat, stroke, ellipse, capsule, smooth_poly, hx, radial_glow
from demons import Imp, slit_eye
from humanoid import Look, draw_figure, HIP_Y, TORSO, UA, FA, vec, add

TAU = math.tau


def _armor(ctx, view):
    steel = Pal('#485169', '#2b3046', '#8490a8', '#1b2033')
    rim = Pal('#bc9663', '#806145', '#efcc91', '#493129')
    ember = Pal('#da5b4c', '#9d303e', '#ffab78', '#541a26')
    w = 12 if view != 'side' else 8
    # Raised plate segments, painted with exactly the same shading engine.
    for side in (-1, 1) if view != 'side' else (1,):
        x = side * w
        paint(ctx, lambda c, x=x: smooth_poly(c, [
            (x-6,-55),(x+4,-58),(x+9,-52),(x+7,-44),(x-3,-44),(x-8,-49)
        ], tension=.3), steel, sh=1.7, hl=1.1, line=1)
        stroke(ctx, lambda c,x=x:(c.move_to(x-5,-54),c.line_to(x+5,-53)),
               rim.light,1.5,.85)
    if view != 'up':
        paint(ctx, lambda c:smooth_poly(c, [
            (-8,-52),(0,-55),(8,-52),(7,-37),(0,-30),(-7,-37)
        ],tension=.4),steel,sh=2,hl=1.4,line=1)
        paint(ctx,lambda c:smooth_poly(c,[
            (0,-48),(5,-44),(0,-37),(-5,-44)
        ],tension=.16),ember,sh=.8,hl=.7,line=1)
        stroke(ctx,lambda c:(c.move_to(-7,-39),c.line_to(0,-34),c.line_to(7,-39)),rim.light,1.3)
    else:
        paint(ctx, lambda c:smooth_poly(c, [
            (-9,-52),(0,-54),(9,-52),(8,-34),(0,-30),(-8,-34)
        ],tension=.4),steel,sh=1.6,hl=.9,line=1)


def _horns(ctx, view):
    # Distinct two-horn silhouette for each facing; drawn on top of the
    # humanoid head (never baked onto or replacing any original sprite).
    horn = Pal('#e8d6ad','#ab9473','#fff4dd','#54443a')
    crown = Pal('#522a39','#391b2e','#865068','#24111d')
    if view == 'side':
        horns=[(-6,-84), (6,-85)]
    else:
        horns=[(-13,-82), (13,-82)]
    for side,(x,y) in enumerate(horns):
        sx=-1 if x<0 else 1
        paint(ctx, lambda c,x=x,y=y,sx=sx:smooth_poly(c,[
            (x-4,y+7),(x-6,y-5),(x+sx*5,y-19),(x+sx*1,y-6),(x+4,y+6)
        ],tension=.25),horn,sh=2.2,hl=1.5,line=1.1)
    paint(ctx,lambda c:smooth_poly(c,[(-10,-81),(-5,-88),(5,-88),(10,-81),(6,-76),(-6,-76)],tension=.3),
          crown,sh=1.5,hl=.7,line=1)
    if view != 'up':
        radial_glow(ctx,0,-71,7,hx('#f66e4f'),.4)
        paint(ctx,lambda c:ellipse(c,0,-73,2.2,3),Pal('#ff985d','#bd453c','#fff1ad','#66262e'),
              sh=.6,hl=.7,line=.6)


def _club(ctx, at, angle):
    # Iron studded war club in the sword hand, follows attack pose angle.
    shaft=Pal('#74503c','#4a2d2a','#ae7953','#271a21')
    steel=Pal('#454b60','#282d40','#8d9aae','#141826')
    gold=Pal('#bc9263','#79583c','#f1c88a','#443027')
    ctx.save()
    ctx.translate(*at)
    ctx.rotate(math.radians(-angle))
    paint(ctx,lambda c:capsule(c,(0,-8),(0,33),3.5,3.1),shaft,sh=1.1,hl=.5,line=1)
    paint(ctx,lambda c:smooth_poly(c,[
        (-8,17),(-11,23),(-10,46),(-5,52),(5,52),(10,46),(11,23),(8,17)
    ],tension=.28),steel,sh=2.5,hl=1.5,line=1.3)
    for y in (27,43):
        stroke(ctx,lambda c,y=y:(c.move_to(-8,y),c.line_to(8,y)),gold.light,1.6,.9)
    for y in (26,39,47):
        for sx in (-1,1):
            paint(ctx,lambda c,sx=sx,y=y:smooth_poly(c,[
                (sx*8,y-3),(sx*15,y-2),(sx*18,y+2),(sx*9,y+4)
            ],tension=.22),steel,sh=1,hl=.8,line=.9)
    paint(ctx,lambda c:ellipse(c,0,32,3.2,3.2),
          Pal('#eb754f','#af3b43','#ffd3a0','#713039'),sh=.7,hl=.7,line=.6)
    ctx.restore()


class OniSoldier:
    name='oni_soldier'
    FW,FH,OX,OY=192,192,96,166
    ANIMS={
        'idle':(10,10,True,-1),
        'move':(10,13,True,-1),
        'attack':(11,17,False,6),
        'cast':(10,14,False,6),
        'hurt':(5,14,False,-1),
        'death':(12,12,False,-1),
    }
    LOOK=Look(
        skin=Pal('#a47891','#79526f','#cba7b3','#402c48'),
        hair=Pal('#272a3e','#151726','#555771','#141421'),
        eye=hx('#e8914a'),
        tunic=Pal('#3c465c','#252c43','#626d87','#1c2031'),
        shirt=Pal('#5f4655','#40303f','#906977','#241a2b'),
        pants=Pal('#423845','#2c2538','#6b5a65','#221a27'),
        boots=Pal('#49383a','#2c242d','#745657','#211923'),
        belt=Pal('#443036','#30232c','#6f4c4a','#1c1722'),
        metal=Pal('#bb9265','#86643d','#f0cc8e','#4e3227'),
        glove=Pal('#423544','#2a2436','#766178','#191725'),
        scarf_on=False, weapon=None, hair_style='spiky',
    )
    POSE_MAP={'idle':'idle','move':'run','attack':'attack3',
              'cast':'cast','hurt':'hurt','death':'death'}

    def pose(self, anim, t, view):
        p=human_pose(self.POSE_MAP[anim],t,view)
        # Heavy soldier is deliberate: broad anticipation and recoil.
        if anim=='idle':
            p['y']+=math.sin(t*TAU)*.9
        if anim=='move':
            p['lean']*=.58
            p['y']*=.65
        if anim=='cast':
            p['glow']=hx('#ff895f')
        return p

    def draw(self,ctx,view,p):
        ctx.save()
        # Larger than the main humanoid; feet remain fixed at (0,0).
        ctx.scale(1.20,1.20)
        # The humanoid body rig ensures full 3-view poses, smooth cel shading.
        result=draw_figure(ctx,self.LOOK,view,p)
        ctx.translate(p['x'],p['y'])
        if p['rot']:
            ctx.translate(0,p['hip'])
            ctx.rotate(math.radians(p['rot']))
            ctx.translate(0,-p['hip'])
        # Armour tracks the breathing and lean of the underlying rig.
        ctx.translate(0,p['hip']-HIP_Y)
        ctx.rotate(math.radians(p['lean']*.55))
        ctx.translate(0,-p['hip']+HIP_Y)
        _armor(ctx,view)
        _horns(ctx,view)
        if p.get('wpn') is not None:
            _club(ctx,result['hand'],p['wpn'])
        else:
            _club(ctx,result['hand'],25 if view=='side' else -24)
        ctx.restore()


class Grakk(Imp):
    name='grakk'
    FW,FH,OX,OY=192,192,96,160
    ANIMS={
        'idle':(10,11,True,-1),
        'move':(10,13,True,-1),
        'attack':(11,16,False,6),
        'cast':(11,14,False,7),
        'hurt':(6,14,False,-1),
        'death':(12,12,False,-1),
    }
    def __init__(self):
        self.skin=Pal('#92344f','#662142','#d45b67','#35112f')
        self.belly=Pal('#d59075','#965766','#f1bba4','#522639')
        self.wing=Pal('#383257','#262340','#66618d','#19162b')
        self.membrane=Pal('#77456f','#51294e','#a66c97','#2e1b32')
        self.horn=Pal('#e6c99e','#a88a67','#fff1d0','#574236')
        self.claw=Pal('#222334','#131322','#515169','#0e0b19')
        self.eye=hx('#8af2ff')

    def draw(self,ctx,view,p):
        ctx.save()
        ctx.scale(1.34,1.34)
        super().draw(ctx,view,p)
        ctx.save()
        ctx.translate(p['x'],p['y']-46)
        ctx.rotate(math.radians(p['rot']*.25+p['lean']*.45))
        bronze=Pal('#a77850','#6e4939','#edc08b','#3e2628')
        iron=Pal('#4a3b58','#30283d','#85647e','#221928')
        crystal=Pal('#5fe3e9','#218c9e','#d1ffff','#1d546d')
        # Boss-only breastplate with prominent glowing inverted rune.
        if view != 'up':
            paint(ctx,lambda c:smooth_poly(c,[
                (-9,-6),(0,-9),(9,-6),(10,6),(2,13),(-2,13),(-10,6)
            ],tension=.3),iron,sh=1.8,hl=.9,line=1.0)
            stroke(ctx,lambda c:(c.move_to(-7,-5),c.line_to(0,-1),c.line_to(7,-5)),bronze.light,1.7)
            paint(ctx,lambda c:smooth_poly(c,[
                (0,-3),(-4,3),(0,10),(4,3)
            ],tension=.2),crystal,sh=.9,hl=.6,line=.7)
            radial_glow(ctx,0,3,11,hx('#73efff'),.26)
        # Spiked golden pauldrons, a distinctly boss-like silhouette.
        for sx in (-1,1):
            x=sx*11
            paint(ctx,lambda c,x=x,sx=sx:smooth_poly(c,[
                (x-sx*8,-10),(x,-14),(x+sx*5,-23),(x+sx*9,-10),
                (x+sx*10,0),(x,1)
            ],tension=.3),bronze,sh=1.3,hl=.85,line=1.0)
        # A broken crown and inset glowing crest; retain animated imp head.
        for x,h in ((-9,8),(0,15),(9,10)):
            paint(ctx,lambda c,x=x,h=h:smooth_poly(c,[
                (x-4,-29),(x-3,-30-h*.6),(x,-29-h),(x+3,-30-h*.6),(x+4,-29)
            ],tension=.2),bronze,sh=.8,hl=.6,line=.8)
        stroke(ctx,lambda c:(c.move_to(-12,-28),c.curve_to(-4,-25,5,-25,12,-28)),bronze.light,2.6)
        paint(ctx,lambda c:ellipse(c,0,-29,2.6,2.2),crystal,sh=.4,hl=.4,line=.5)
        ctx.restore()
        ctx.restore()


EXTRA_DEMONS=(OniSoldier(),Grakk())
