"""Distinct anatomical remodels of rejected Lote 1 duplicates.

Eight species-specific silhouettes; never overlays/palette-swaps of the
production Imp or Humanoid.  Uses the established Cairo paint/Pal renderer.
Every view/action is procedurally posed independently and preserves metadata
specified in docs/asset_catalog/lote1_spec.json.
"""
from __future__ import annotations
import math
from core import Pal, paint, flat, stroke, ellipse, radial_glow, hx
from lote1_creatures import shape, circle, beam

TAU=math.tau

SPECS={
 'imp_scout': ('vesper_winged_scout','wing_ray', ('#564768','#6d6591','#dfbb7d','#ecdb9b')),
 'imp_raider': ('four_armed_mauler','brute_quadarm', ('#883b4b','#c66f68','#ddbb83','#f6bf68')),
 'imp_pyro': ('ember_salamander','salamander', ('#903b37','#e86c38','#dbac74','#ffe4a1')),
 'imp_howler': ('hell_bell_toad','toad', ('#4d5368','#847d86','#d1a26d','#dcfc95')),
 'oni_lancer': ('serpent_naga_lancer','naga', ('#485b6a','#769c98','#a8c4bd','#fff0b8')),
 'oni_shielder': ('basalt_shell_guard','tortoise', ('#444452','#777587','#bda375','#eae2ad')),
 'oni_executioner': ('stilt_bone_reaper','skeletal', ('#39344e','#71637b','#c3b9a2','#ed9e77')),
 'morgash_ironhorn': ('six_legged_iron_bull','bull_sixlegs', ('#573a4e','#896073','#c39a69','#ffb46e')),
}


def poly(ctx,points,mat,s=2,h=1):
    shape(ctx,points,mat,sh=s,hl=h,line=1.3)


def sym_poly(ctx,sx,points,pal,s=2,h=1):
    poly(ctx,[(sx*x,y) for x,y in points],pal,s,h)


def orb(ctx,x,y,r,mat):
    circle(ctx,x,y,r,r,mat)


class AnatomicalRemodel:
    """Independent species rigs; shared animation contract, no shared body mesh."""

    def __init__(self,name):
        self.name=name
        self.concept,self.rig,colors=SPECS[name]
        self.shell=Pal(colors[0]);self.meat=Pal(colors[1]);self.bone=Pal(colors[2]);self.light=Pal(colors[3]);
        self.ink=Pal('#292339','#1d192d','#63536b','#12101d')
        self.fire=Pal('#f68b53','#c74b44','#fff3ad','#71353c')

    def pose(self,anim,t,view):
        move=anim=='move'
        strike=anim=='attack'
        skill=anim in ('cast','skill_2')
        painful=anim=='hurt'
        death=anim=='death'
        gait=math.sin(TAU*t*(1.3 if move else .5))
        open_wing=math.sin(TAU*t*(2.0 if move else .7))
        recoil=math.sin(math.pi*t) if strike else 0
        spell=math.sin(math.pi*t) if skill else 0
        pain=math.sin(math.pi*t) if painful else 0
        d=t if death else 0
        return dict(gait=gait,flap=open_wing,hit=recoil,glow=spell,pain=pain,death=d,
                    y=(-3*math.sin(TAU*t) if move else -1.4*math.sin(TAU*t))*(1-d),
                    turn=view,anim=anim,t=t)

    def draw(self,ctx,view,p):
        ctx.save()
        ctx.translate(0,p['y']+p['death']*18)
        ctx.rotate(math.radians(p['pain']*-7+p['death']*22))
        if p['death']:
            ctx.scale(1,1-.36*p['death'])
        self._draw_species(ctx,view,p)
        self._draw_signature_details(ctx,view,p)
        ctx.restore()

    def _draw_species(self,ctx,view,p):
        getattr(self,'_draw_'+self.rig)(ctx,view,p)

    def eyes(self,c,v,x,y,spacing=8,eye=3):
        if v=='up': return
        for sx in ((1,) if v=='side' else (-1,1)):
            xx=x+sx*spacing
            orb(c,xx,y,eye,self.light)
            orb(c,xx+1,y+1,eye*.33,self.ink)

    def _draw_wing_ray(self,c,v,p):
        """Narrow body; bat-ray wings span > body, long dangling stilt legs."""
        g=p['gait'];f=p['flap'];hit=p['hit'];sp=p['glow'];
        for sx in (-1,1):
            x=sx*(22 if v!='side' else 21)
            # Two wings and open fingers have an unmistakable V silhouette.
            poly(c,[(sx*8,-47),(sx*26,-67-f*7),(sx*55,-84-f*10),
                    (sx*51,-52),(sx*44,-58),(sx*36,-34),(sx*31,-47),(sx*18,-32)],self.shell,1.9,1.2)
            for k in range(3):
                endx=sx*(39+k*6)
                beam(c,[(sx*10,-46),(endx,-68-k*7-f*4)],self.bone,1.1)
            # Two impossibly thin independent legs.
            beam(c,[(sx*8,-24),(sx*(13+4*g),-8),(sx*(15+5*g),-1)],self.ink,2.8)
            poly(c,[(sx*(11+4*g),-5),(sx*(20+4*g),-4),(sx*(17+4*g),0)],self.bone,1,.6)
        # Thin abdomen and enlarged, vertical triangular skull.
        poly(c,[(-11,-52),(0,-59),(11,-52),(9,-22),(0,-13),(-9,-22)],self.meat,2.5,1.1)
        poly(c,[(-17,-58),(-8,-75),(0,-91),(8,-75),(17,-58),(10,-49),(-10,-49)],self.shell,2.7,1.4)
        for sx in (-1,1):sym_poly(c,sx,[(10,-76),(17,-98),(21,-79)],self.bone,1,.4)
        self.eyes(c,v,0,-67,6,3)
        # Natural sting is the weapon; scout no longer carries an imp dagger.
        poly(c,[(-4,-17),(0,-3),(5,-20)],self.bone,1,.7)
        if hit>0:beam(c,[(0,-32),(28,-15),(42+hit*10,-8)],self.light,2.5)
        if sp>0:
            for sx in (-1,1):radial_glow(c,sx*46,-63,18,self.light.base,sp*.55)

    def _draw_brute_quadarm(self,c,v,p):
        """Massive humped body, four independent arms, jaw and tusks, no wings."""
        g=p['gait'];hit=p['hit'];sp=p['glow']
        for sx in (-1,1):
            xx=sx*(18+g*4)
            poly(c,[(sx*13,-26),(sx*23,-22),(xx+sx*3,-3),(xx-sx*4,0),(xx-sx*13,-3)],self.ink,1.8,.8)
            # Upper grasping arms: long knuckle walk.
            sym_poly(c,sx,[(20,-62),(34,-70),(43+hit*10,-36),(46+hit*16,-17),(31,-20),(29,-44)],self.meat,2.1,.9)
            orb(c,sx*(43+hit*12),-16,7,self.bone)
            # Lower claws are independently articulated.
            sym_poly(c,sx,[(23,-44),(36,-47),(38-sp*6,-22),(30,-15),(25,-31)],self.shell,2,.7)
            for k in (0,1,2):
                sym_poly(c,sx,[(31+k*4,-13),(36+k*4,-3),(28+k*4,-10)],self.bone,1,.4)
            sym_poly(c,sx,[(12,-70),(24,-88),(28,-73)],self.ink,1,.3)
        poly(c,[(-24,-62),(-12,-78),(8,-86),(30,-68),(35,-38),(27,-14),(-20,-12),(-32,-30)],self.shell,3.4,1.5)
        poly(c,[(-19,-55),(0,-60),(20,-56),(24,-27),(0,-18),(-23,-31)],self.meat,1.9,.7)
        poly(c,[(-26,-63),(-22,-79),(-10,-93),(10,-92),(27,-74),(25,-57),(11,-47),(-18,-49)],self.meat,2.6,1)
        self.eyes(c,v,0,-70,11,3)
        poly(c,[(-17,-61),(0,-63),(17,-61),(15,-49),(0,-42),(-15,-50)],self.ink,1,.4)
        for sx in (-1,1):sym_poly(c,sx,[(9,-53),(14,-42),(19,-56)],self.bone,1,.5)
        if sp:radial_glow(c,0,-56,23,self.light.base,sp*.4)

    def _draw_salamander(self,c,v,p):
        """Long crawling fire reptile; NO biped arms, horns or wings."""
        g=p['gait'];hit=p['hit'];sp=p['glow']
        ctx_x=30 if v=='side' else 0
        # Tail curls independently from broad body.
        poly(c,[(ctx_x-13,-25),(ctx_x-37,-30),(ctx_x-45,-42+g*3),
                (ctx_x-61,-44),(ctx_x-58,-26),(ctx_x-39,-15),(ctx_x-7,-16)],self.shell,2.2,1.2)
        for sx in (-1,1):
            for j in (0,1):
                x=ctx_x+sx*(21 if j else 30)
                gy=g*6*(1 if j else -1)*sx
                poly(c,[(x-sx*6,-28),(x+sx*11,-21),(x+sx*14+gy,-2),
                        (x+sx*2+gy,0),(x-sx*11,-10)],self.meat,2,.7)
                for k in (0,1):sym_poly(c,sx,[(abs(x)+8+gy,-5),(abs(x)+11+gy,-1),(abs(x)+15+gy,-3)],self.bone,.8,.4)
        poly(c,[(-42,-40),(-24,-57),(20,-57),(41,-40),(30,-23),(-27,-23)],self.shell,3.2,1.3)
        for i in range(6):
            x=-29+i*12
            y=-54+(i%2)*-4
            poly(c,[(x-5,y+3),(x,y-15-3*sp),(x+8,y+4)],self.fire,2,.9)
            if sp:radial_glow(c,x,y-9,10,self.fire.base,.4*sp)
        # Forward lizard head, horizontal jaw, nostrils, no ears.
        off=hit*10
        poly(c,[(-17+off,-45),(6+off,-52),(25+off,-42),(30+off,-32),
                (19+off,-25),(-9+off,-26)],self.meat,2.7,1.2)
        if v!='up':
            for sx in (-1,1):orb(c,sx*13+off,-38,3.7,self.light)
            beam(c,[(-3+off,-29),(18+off,-27),(29+off,-31)],self.ink,2)
        if sp:radial_glow(c,24+off,-35,25,self.fire.base,sp*.72)

    def _draw_toad(self,c,v,p):
        """Low horned sonic toad with inflatable throat; four squat legs."""
        g=p['gait'];sp=p['glow'];hit=p['hit']
        for sx in (-1,1):
            poly(c,[(sx*25,-29),(sx*42,-25),(sx*(47+g*5),-1),
                (sx*(37+g*5),0),(sx*32,-13)],self.meat,2,.8)
            for k in (0,1,2):sym_poly(c,sx,[(37+k*5,-8),(43+k*5,-1),(34+k*5,-2)],self.bone,.8,.3)
        poly(c,[(-37,-40),(-22,-58),(20,-58),(39,-40),(33,-16),(0,-8),(-34,-18)],self.shell,3,1.5)
        # Huge sonic resonator distorts the entire silhouette on spell cast.
        rr=19+16*sp+5*hit
        orb(c,0,-30,rr,self.meat)
        circle(c,-8,-37,6,8,self.bone);circle(c,8,-37,6,8,self.bone)
        for sx in (-1,1):
            sym_poly(c,sx,[(21,-52),(29,-74),(35,-53)],self.bone,1.4,.6)
            circle(c,sx*22,-55,8,8,self.shell)
        self.eyes(c,v,0,-55,21,4)
        if v!='up':
            beam(c,[(-10,-16),(0,-13),(11,-16)],self.ink,3.1)
        if sp:
            for rad in (47+12*sp,61+18*sp):
                stroke(c,lambda cc,rad=rad:cc.arc(0,-31,rad,-.5,math.pi+.5),self.light.base,1.8,sp*.65)

    def _draw_naga(self,c,v,p):
        """Serpentine coiled lower half (NO humanoid legs) and antlered upper torso."""
        g=p['gait'];sp=p['glow'];hit=p['hit']; side=v=='side'
        bodyx=10 if side else 0
        # Triangular tapering tail body; spiral tip tracks gait.
        poly(c,[(-40,-12),(-48,-24),(-33,-34),(3,-33),(29,-20),
                (44,-26),(56+g*7,-47),(64+g*7,-38),(50,-9),
                (24,-2),(-18,-3)],self.shell,3.1,1.4)
        circle(c,-32,-22,12,10,self.meat)
        for i in range(6):
            x=-32+i*13
            poly(c,[(x-8,-27),(x+6,-29),(x+8,-17),(x-7,-15)],self.meat,1.4,.4)
        poly(c,[(-18+bodyx,-56),(0+bodyx,-75),(19+bodyx,-59),
               (23+bodyx,-31),(0+bodyx,-28),(-22+bodyx,-34)],self.meat,2.6,1.2)
        for sx in (-1,1):
            sym_poly(c,sx,[(16,-59),(30,-57),(34,-28),(22+hit*14,-20),(12,-34)],self.shell,2,.7)
        poly(c,[(-16+bodyx,-67),(-18+bodyx,-84),(0+bodyx,-92),
                (18+bodyx,-84),(16+bodyx,-63)],self.shell,2.7,1.2)
        # Wide branching antlers, rather than the two Oni horns.
        for sx in (-1,1):
            beam(c,[(sx*12+bodyx,-82),(sx*28+bodyx,-99),(sx*40+bodyx,-102)],self.bone,3)
            beam(c,[(sx*23+bodyx,-91),(sx*17+bodyx,-107)],self.bone,2)
        self.eyes(c,v,bodyx,-76,8,3)
        # Long organic trident, slender but not primary differentiator.
        grip=34+hit*8
        beam(c,[(grip,-12),(grip,-107)],self.bone,3)
        for sx in (-1,1):
            poly(c,[(grip+sx*3,-110),(grip+sx*13,-114),(grip+sx*17,-135),(grip+sx*4,-123)],self.light,1.2,.8)
        if sp:radial_glow(c,grip,-100,27,self.light.base,.6*sp)

    def _draw_tortoise(self,c,v,p):
        """A four-footed shelled tower with shield fused to dorsal carapace."""
        g=p['gait'];sp=p['glow'];hit=p['hit'];
        for sx in (-1,1):
            for front in (False,True):
                x=sx*(24 if front else 32)
                shift=g*5*(1 if front else -1)
                poly(c,[(x-sx*9,-31),(x+sx*12,-30),(x+sx*17+shift,-4),
                        (x+sx*3+shift,0),(x-sx*8,-8)],self.meat,2.2,.8)
                poly(c,[(x-sx*9+shift,-6),(x+sx*13+shift,-6),(x+sx*18+shift,0),(x-sx*10+shift,0)],self.bone,1,.5)
        # Giant integral shell determines outline; hexagonal interlocking plates.
        poly(c,[(-48,-30),(-46,-70),(-24,-88),(22,-89),(48,-68),(51,-26),
                (34,-14),(-34,-14)],self.shell,4,1.8)
        poly(c,[(-38,-64),(0,-84),(39,-63),(30,-27),(0,-16),(-32,-27)],self.meat,2.6,.7)
        poly(c,[(-23,-62),(0,-77),(24,-62),(27,-40),(0,-26),(-27,-40)],self.shell,1.5,.6)
        poly(c,[(-14,-55),(0,-67),(14,-55),(12,-43),(0,-33),(-12,-43)],self.bone,1.2,.7)
        # Head peeks from one narrow aperture at the top.
        poly(c,[(-13,-70),(-16,-91),(0,-106),(16,-92),(15,-70),(0,-64)],self.meat,2.3,1.1)
        for sx in (-1,1):sym_poly(c,sx,[(8,-91),(17,-115),(20,-92)],self.bone,1.2,.5)
        self.eyes(c,v,0,-86,8,3)
        # On skill: giant shell spikes rise; no handheld shield prop.
        if sp:
            for sx in (-1,1):
                sym_poly(c,sx,[(34,-66),(51+sp*7,-88),(47,-55)],self.bone,1.2,.6)
            radial_glow(c,0,-45,39,self.light.base,.25*sp)

    def _draw_skeletal(self,c,v,p):
        """Long stilt bone limbs, exposed ribcage, a hooded hollow skull."""
        g=p['gait'];hit=p['hit'];sp=p['glow']
        for sx in (-1,1):
            x=sx*11
            beam(c,[(x,-43),(x+sx*9,-19),(x+sx*(11+4*g),-2)],self.bone,5.4)
            for k in (-1,0,1):beam(c,[(x+sx*(11+4*g),-2),(x+sx*(15+4*g+k*3),0)],self.ink,2)
        # Four-blade ribs show skeletal anatomy under floating cloak.
        poly(c,[(-20,-52),(-30,-85),(-18,-111),(0,-116),(19,-110),
                (30,-86),(17,-51),(0,-37)],self.shell,2.6,1.3)
        poly(c,[(-17,-88),(0,-91),(18,-86),(10,-58),(-11,-57)],self.ink,2,.6)
        for i in range(4):
            y=-80+i*8
            for sx in (-1,1):
                beam(c,[(0,y+2),(sx*(13-i*.6),y)],self.bone,2.5)
        # Skull is lower triangle under a separate sweeping hood peak.
        poly(c,[(-17,-107),(-10,-132),(0,-142),(14,-124),(17,-100),
                (0,-92)],self.shell,2,1.2)
        poly(c,[(-9,-115),(0,-123),(10,-114),(9,-101),(0,-98),(-9,-102)],self.ink,1,.3)
        self.eyes(c,v,0,-110,6,3.5)
        for sx in (-1,1):
            # Upper secondary arms sprout from spine instead of shoulders.
            beam(c,[(sx*18,-94),(sx*35,-67),(sx*38+hit*15,-37)],self.bone,4)
            poly(c,[(sx*(38+hit*15),-38),(sx*(51+hit*15),-26),
                    (sx*(44+hit*15),-46)],self.ink,1.3,.5)
            # Scythe blade is fused to one anatomical forearm.
        beam(c,[(28,-53),(41+hit*17,-25),(48+hit*18,-8)],self.bone,5)
        poly(c,[(48+hit*18,-10),(69+hit*24,-24),(75+hit*24,-48),
                (61+hit*20,-33)],self.light,2,.9)
        if sp:radial_glow(c,0,-80,43,self.light.base,.40*sp)

    def _draw_bull_sixlegs(self,c,v,p):
        """Six legs, massive hump, enormous curled horns and bovine skull."""
        g=p['gait'];hit=p['hit'];sp=p['glow']
        # Three distinct locomotion pairs, staggered gait.
        for j in range(3):
            for sx in (-1,1):
                x=sx*(22+j*15)
                lift=g*4*((-1)**j)*sx
                poly(c,[(x-sx*10,-52),(x+sx*13,-47),(x+sx*20+lift,-6),
                        (x+sx*5+lift,0),(x-sx*13,-8)],self.meat,2.1,.7)
                poly(c,[(x-sx*13+lift,-8),(x+sx*13+lift,-10),
                        (x+sx*19+lift,-1),(x-sx*15+lift,0)],self.ink,1.6,.5)
        # Whole upper body is a gigantic quadruped humped beast, not enlarged soldier.
        poly(c,[(-67,-52),(-61,-89),(-42,-115),(-11,-119),(29,-112),
                (61,-86),(70,-53),(54,-33),(0,-22),(-55,-34)],self.shell,4.2,2)
        for j in range(5):
            x=-38+j*19
            poly(c,[(x-12,-104),(x+10,-108),(x+13,-75),(x-9,-71)],self.meat,1.5,.6)
        # Huge lifted bull head, two curled crescent horns set the silhouette.
        poly(c,[(-28,-95),(-22,-124),(0,-137),(25,-125),(31,-98),
                (18,-72),(0,-63),(-20,-72)],self.meat,3.2,1.4)
        for sx in (-1,1):
            sym_poly(c,sx,[(18,-121),(39,-155),(64,-160),(69,-147),
                            (48,-142),(42,-131),(31,-112)],self.bone,2.7,1.4)
        # Pronounced muzzle with fang, bright nostrils.
        poly(c,[(-22,-84),(0,-92),(23,-85),(21,-70),(0,-62),(-22,-68)],self.bone,1.7,.7)
        self.eyes(c,v,0,-104,15,5)
        for sx in (-1,1):
            orb(c,sx*10,-75,2.8,self.ink)
        if hit:
            poly(c,[(-47,-45),(0,-60),(46,-43),(59,-25),(4,-18),(-55,-24)],self.meat,1.5,.5)
        if sp:
            for sx in (-1,1):radial_glow(c,sx*46,-84,29,self.light.base,.5*sp)
            stroke(c,lambda cc:cc.arc(0,-49,70,-.6,math.pi+.4),self.fire.base,3,sp*.7)

    def _draw_signature_details(self,c,view,p):
        """Species-specific material layers and articulated details.

        Applied on the unique anatomical rigs, not on reused humanoid/imp
        sprites. Small parts use the production Pal/paint shade gradients.
        """
        g=p['gait']; glow=p['glow'];hit=p['hit']
        if self.rig=='wing_ray':
            # Rigid bat wing veins / web seams and an asymmetric scout crest.
            for sx in (-1,1):
                for k,(ex,ey) in enumerate(((37,-66),(48,-79),(49,-49))):
                    beam(c,[(sx*12,-46),(sx*(ex+3*g),ey)],self.bone,1.2)
                    orb(c,sx*(ex+3*g),ey,1.5,self.light)
                poly(c,[(sx*8,-41),(sx*14,-38),(sx*11,-28),(sx*6,-32)],self.bone,.8,.4)
                beam(c,[(sx*11,-21),(sx*13,-14),(sx*15,-9)],self.bone,1.2)
            poly(c,[(-5,-82),(0,-87),(5,-82),(3,-75),(0,-73),(-3,-75)],self.bone,1,.6)
            orb(c,0,-79,2,self.light)
            beam(c,[(-6,-40),(0,-35),(6,-40)],self.ink,1.5)
        elif self.rig=='brute_quadarm':
            # Armoured shoulder cuffs, layered breast plate, tribal tattoos.
            poly(c,[(-16,-59),(0,-64),(18,-60),(15,-45),(0,-39),(-17,-46)],self.shell,1.4,.7)
            for sx in (-1,1):
                poly(c,[(sx*18,-60),(sx*32,-66),(sx*38,-52),(sx*30,-43),(sx*22,-49)],self.ink,1.5,.7)
                for y in (-51,-44):
                    orb(c,sx*27,y,2,self.bone)
                beam(c,[(sx*19,-31),(sx*23,-24),(sx*19,-21)],self.bone,1.4)
                orb(c,sx*12,-53,2.3,self.light)
                beam(c,[(sx*10,-78),(sx*14,-82),(sx*11,-86)],self.ink,1.5)
            poly(c,[(-8,-54),(0,-58),(9,-54),(0,-47)],self.bone,.9,.6)
            beam(c,[(-12,-47),(0,-43),(13,-47)],self.light,1)
        elif self.rig=='salamander':
            # Real plate segmentation and cracked glowing magma veins.
            for i in range(6):
                x=-29+i*12
                poly(c,[(x-7,-41),(x,-49),(x+7,-43),(x+4,-31),(x-6,-31)],self.meat,1.4,.7)
                beam(c,[(x-4,-43),(x,-38),(x+4,-43)],self.ink,1.1)
                if i%2==0:
                    beam(c,[(x,-50),(x+2,-53)],self.light,1.2)
            for sx in (-1,1):
                orb(c,sx*13,-39,5,self.shell)
                orb(c,sx*13,-38,2.3,self.light)
                poly(c,[(sx*18,-28),(sx*24,-24),(sx*22,-18)],self.bone,.7,.5)
            for k in range(4):
                x=-50+k*11
                beam(c,[(x,-31),(x+3,-28),(x+6,-32)],self.fire,1.6)
            if glow:
                radial_glow(c,0,-36,30,self.fire.base,.32*glow)
        elif self.rig=='toad':
            # Vocal skin folds and large tympanic discs: no imp ears/helmet.
            for sx in (-1,1):
                orb(c,sx*28,-40,7,self.shell)
                orb(c,sx*28,-40,4,self.bone)
                for k in range(3):
                    y=-28+k*7
                    beam(c,[(sx*19,y),(sx*(27+k*2),y+3)],self.ink,1.25)
                orb(c,sx*19,-55,3,self.light)
                orb(c,sx*20,-56,1.5,self.ink)
            for j in range(4):
                y=-28+j*7
                beam(c,[(-11+j*2,y),(0,y+2),(11-j*2,y)],self.bone,1.1)
            for sx in (-1,1):
                poly(c,[(sx*33,-12),(sx*38,-7),(sx*34,-3)],self.light,.7,.4)
        elif self.rig=='naga':
            # Repeated inlaid tail-scales, ribbed throat and fin crown.
            for i in range(6):
                x=-29+i*12
                poly(c,[(x-4,-30),(x+4,-33),(x+9,-24),(x+1,-20)],self.bone,.6,.5)
                orb(c,x,-25,1.5,self.light)
            for sx in (-1,1):
                poly(c,[(sx*11,-59),(sx*22,-54),(sx*16,-38)],self.shell,1,.6)
                poly(c,[(sx*5,-89),(sx*10,-104),(sx*15,-90)],self.bone,1,.5)
                beam(c,[(sx*7,-69),(sx*13,-66)],self.ink,1.2)
            poly(c,[(-7,-54),(0,-58),(7,-54),(6,-48),(0,-44),(-6,-49)],self.bone,.6,.5)
            orb(c,0,-51,3,self.light)
            for y in (-80,-66,-40):
                beam(c,[(31,y),(38,y-2)],self.shell,2.3)
        elif self.rig=='tortoise':
            # Interlocking tortoise shell tessellation, rim rivets, talons.
            for sx in (-1,1):
                for y in (-67,-52,-37):
                    beam(c,[(sx*25,y-7),(sx*32,y),(sx*25,y+8)],self.bone,1.3)
                    orb(c,sx*36,y,1.7,self.light)
                for x in (26,39):
                    poly(c,[(sx*x,-5),(sx*(x+4),-1),(sx*(x-4),-1)],self.bone,.9,.4)
                orb(c,sx*8,-83,4,self.ink)
                orb(c,sx*9,-84,2.0,self.light)
            poly(c,[(-11,-48),(0,-58),(11,-48),(0,-39)],self.light,1,.6)
            for rad in (17,24):
                stroke(c,lambda cc,rad=rad:cc.arc(0,-49,rad,.18,math.pi-.18),self.bone.base,1.2,.55)
            if glow:radial_glow(c,0,-47,32,self.light.base,.35*glow)
        elif self.rig=='skeletal':
            # Silver rib rivets, bone collar, facial fissures, scythe glyphs.
            for j in range(5):
                y=-83+j*8
                orb(c,0,y+2,2,self.light)
                for sx in (-1,1):
                    orb(c,sx*(10-j*.5),y,1.6,self.bone)
            for sx in (-1,1):
                poly(c,[(sx*15,-111),(sx*22,-117),(sx*20,-98)],self.shell,1.2,.6)
                beam(c,[(sx*8,-104),(sx*10,-99),(sx*6,-96)],self.bone,1)
                for y in (-39,-24):
                    orb(c,sx*31,y,2,self.bone)
            poly(c,[(-6,-91),(0,-96),(6,-91),(0,-87)],self.light,.8,.5)
            beam(c,[(50+hit*18,-21),(58+hit*18,-34),(66+hit*22,-42)],self.ink,1.5)
            orb(c,0,-91,3.4,self.fire)
            if glow:radial_glow(c,0,-84,29,self.fire.base,.31*glow)
        elif self.rig=='bull_sixlegs':
            # Layered fur plating, horn rings and ceremonial nasal armor.
            for j in range(6):
                x=-44+j*17
                poly(c,[(x-7,-105),(x+5,-105),(x+9,-95),(x,-87),(x-9,-94)],self.meat,1.1,.5)
                beam(c,[(x-2,-98),(x+4,-94)],self.bone,1.1)
            for sx in (-1,1):
                for k in (0,1):
                    yy=-130-k*9
                    beam(c,[(sx*(32+k*6),yy),(sx*(41+k*6),yy-6)],self.shell,2.2)
                orb(c,sx*15,-102,3.6,self.fire)
                poly(c,[(sx*21,-77),(sx*24,-66),(sx*18,-61)],self.shell,1.1,.6)
                beam(c,[(sx*34,-41),(sx*39,-35),(sx*35,-31)],self.bone,1.8)
            poly(c,[(-11,-84),(0,-89),(11,-84),(8,-77),(0,-74),(-8,-78)],self.shell,.9,.6)
            orb(c,0,-79,4,self.bone)
            if glow:radial_glow(c,0,-81,39,self.fire.base,.25*glow)


def remodeled_creatures():
    return {name:AnatomicalRemodel(name) for name in SPECS}