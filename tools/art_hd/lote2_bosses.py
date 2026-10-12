"""Five original HD-cartoon demon BOSS rigs for Unity, not concept artwork.

Uses the project's same Cairo Pal/paint/soft-cel/colored-outline renderer.
Each species has its OWN body() anatomy and motion, not a scaled-up
normal enemy. 7 x 3 directional tracks incl. TWO DIFFERENT skills.
"""
import math
from core import Pal, stroke, radial_glow, hx
from lote2_insects import Insect, poly, disk, limb, vein

PI=math.pi
TAU=math.tau

def segmented(c, pts, color, thick=4):
    limb(c,pts,thick,color)
    for x,y in pts[1:-1]:
        disk(c,x,y,thick*.82,thick*.82,color,.55)

def rune(c,x,y,r,color,opacity=.85):
    vertices=[(x+math.cos(j*TAU/6)*r,y+math.sin(j*TAU/6)*r) for j in range(6)]
    vein(c,vertices+[vertices[0]],color,r*.075,opacity)
    for j in (0,2,4):
        a=j*TAU/6
        vein(c,[(x,y),(x+math.cos(a)*r*.74,y+math.sin(a)*r*.74)],color,.9,opacity*.55)

class Boss(Insect):
    FW=FH=384
    OX=192
    OY=304
    ANIMS={
        'idle':(8,12,True,-1),
        'move':(10,15,True,-1),
        'attack':(11,18,False,7),
        'cast':(11,16,False,7),
        'skill_2':(12,17,False,8),
        'hurt':(5,13,False,-1),
        'death':(10,12,False,-1),
    }
    def pose(self, action, t, view):
        p=super().pose(action,t,view)
        p['ultimate']=math.sin(t*PI) if action=='skill_2' else 0
        p['phase']=1.0 if action=='skill_2' else 0
        p['wingbeat']=math.sin(t*TAU*2.7)
        p['gait']=math.sin(t*TAU*2) if action=='move' else math.sin(t*TAU)*.12
        p['lunge']=math.sin(PI*t) if action=='attack' else 0
        return p
    def draw(self,c,view,p):
        c.save()
        # Natural breathing/sway across ALL boss rigs; no frozen idle frames.
        # Cosine keeps first and middle poses different, even for a heavy
        # immobile-colossus silhouette with otherwise identical armour plates.
        breath=math.cos(TAU*p['t'])
        if p['mode'] in ('idle','move'):
            c.translate(0,breath*2.0)
            c.scale(1.0+breath*.012,1.0+breath*.008)
        # Boss anatomy is drawn and shaded separately from enemy rigs.
        c.scale(1.13,1.13)
        super().draw(c,view,p)
        c.restore()


class MantisHighReaper(Boss):
    name='mantis_high_reaper'
    def __init__(self):
        self.dark=Pal('#263346','#171b2b','#5f6875','#141726')
        self.shell=Pal('#676a4c','#424834','#abb58b','#323a37')
        self.gold=Pal('#c39a72','#82694e','#ffdda2','#57443d')
        self.blood=Pal('#a94c5b','#722d45','#ef936e','#52263a')
        self.ether=Pal('#b9c375','#839b5e','#f4f3b0','#626d4b')
    def body(self,c,v,p):
        side=v=='side';up=v=='up';g=p['gait']
        slash=p['swing']+p['lunge'];burst=p['spell'];fin=p['ultimate']
        c.save();c.translate(0,-4*p['lunge'])
        # Four scissoring insect legs, not the ordinary 2-leg mantis rig.
        for j in range(2):
            for sign in (-1,1):
                x=sign*(17+15*j);swing=g*sign*(1 if j else -1)
                segmented(c,[(x,-58),(x+sign*(19+5*j),-35-swing*4),
                             (x+sign*(11+15*j+swing*4),-19),
                             (x+sign*(29+13*j+swing*5),1)],
                          self.dark,5.6+j*.8)
                poly(c,[(x+sign*10,-17),(x+sign*29,0),
                        (x+sign*43,2),(x+sign*17,-7)],self.gold,1.4,.8)
                for k in range(3):
                    vein(c,[(x+sign*(13+k*6),-12),(x+sign*(18+k*6),-3)],self.ether.light,.8,.65)
        # Tower-long thorax / mesothorax, translucent blood chitin plates.
        for j in range(9):
            y=-34-j*14
            width=18+(j%3)*3
            poly(c,[(-width,y),(0,y-8),(width,y),
                    (width-4,y+13),(0,y+16),(-width+4,y+13)],
                 self.shell if j%2 else self.gold,3,1.4)
            vein(c,[(-width+4,y+4),(0,y+1),(width-4,y+4)],self.dark.light,1.15,.66)
            for s in (-1,1):disk(c,s*(width-6),y+3,2,2,self.blood,.4)
        for sign in (-1,1):
            poly(c,[(sign*12,-78),(sign*26,-158),
                    (sign*51,-174),(sign*42,-120),
                    (sign*28,-70)],self.blood,3.3,1.4)
            for k in range(4):
                vein(c,[(sign*18,-99-k*12),(sign*44,-137-k*8)],self.gold.light,1.0,.5)
        poly(c,[(-25,-176),(0,-195),(24,-175),(19,-144),
                (-18,-145)],self.dark,3.5,2.1)
        poly(c,[(-18,-168),(0,-187),(17,-168),(0,-155)],self.shell,1.9,.9)
        # Four articulated non-handheld scythe forelimbs with DIFFERENT arcs.
        for j in range(2):
            for sign in (-1,1):
                origin=(sign*(17+5*j),-155+17*j)
                ext=21+15*j+25*slash
                elbow=(sign*(34+9*j+8*slash),-126+17*j)
                tip=(sign*(ext+40),-97-23*slash+j*14)
                segmented(c,[origin,elbow,tip],self.dark,6.2-j*.6)
                poly(c,[(tip[0]-sign*9,tip[1]-13),(tip[0]+sign*14,tip[1]-65),
                        (tip[0]+sign*29,tip[1]-70),
                        (tip[0]+sign*18,tip[1]-27),
                        (tip[0]+sign*13,tip[1]+5)],self.gold if j==0 else self.blood,3.5,1.6)
                for k in range(3):
                    xx=tip[0]+sign*(7+k*4);yy=tip[1]-20-k*9
                    poly(c,[(xx,yy),(xx+sign*8,yy-4),(xx+sign*3,yy+7)],self.shell,1.1,.5)
                if slash or fin:
                    vein(c,[(tip[0]+sign*7,tip[1]-15),
                            (tip[0]+sign*24,tip[1]-62)],self.ether.light,2.4,.45+.5*max(slash,fin))
        # Crown wedge head with no humanoid neck.
        hx0=12 if side else 0
        poly(c,[(-20+hx0,-182),(-28+hx0,-209),
                (hx0,-234),(29+hx0,-207),
                (18+hx0,-181),(hx0,-171)],self.shell,4.3,1.9)
        poly(c,[(-13+hx0,-207),(hx0,-226),
                (14+hx0,-207),(hx0,-193)],self.gold,2,.8)
        for sign in (-1,1):
            segmented(c,[(hx0+sign*9,-219),(hx0+sign*27,-242),
                         (hx0+sign*37+p['wingbeat']*2,-258)],self.dark,2.0)
            if not up:
                disk(c,hx0+sign*15,-205,5,5.7,self.ether,.6)
                disk(c,hx0+sign*15,-205,2,2,self.dark,.3)
        if burst or fin:
            rune(c,0,-130,26+18*fin,self.ether.light,.5+.45*max(fin,burst))
            for sign in (-1,1):
                radial_glow(c,sign*(59+fin*15),-133,24,self.ether.base,.4*max(burst,fin))
        c.restore()


class ScarabColossus(Boss):
    name='scarab_colossus'
    OY=259  # impact shockwaves need room below feet
    def __init__(self):
        self.iron=Pal('#3c4350','#222937','#858b95','#292a35')
        self.bronze=Pal('#9d7965','#644d4d','#dfb898','#403642')
        self.sand=Pal('#c19e72','#806c54','#efd3a0','#5e5146')
        self.core=Pal('#60c6b8','#337f86','#b6fff0','#22535e')
        self.dark=Pal('#282b3a','#161c2b','#697181','#171523')
    def body(self,c,v,p):
        side=v=='side';up=v=='up';g=p['gait']
        slam=p['lunge'];open_=p['spell']+p['ultimate']*.82;fort=p['ultimate']
        c.save();c.translate(0,5*slam)
        # Eight pillar legs: quadruped colossus + four auxiliary supports.
        for j in range(4):
            for sign in (-1,1):
                base=sign*(20+j*11)
                q=g*sign*(1 if j%2 else -1)
                segmented(c,[(base,-73-j*2),
                             (base+sign*(19+j*5),-37-j*3-q*5),
                             (base+sign*(24+j*4+q*4),0)],self.iron,8.8+(3-j)*.9)
                poly(c,[(base+sign*10,-13),(base+sign*29,-9),
                        (base+sign*44,3),(base+sign*11,3)],
                     self.bronze,2.7,1)
                disk(c,base+sign*(17+j*3),-33,3,4,self.core,.5)
        # Heavy double clamshell, visibly SPLITS on cast.
        left=-open_*21;right=open_*21
        poly(c,[(-69+left,-46),(-79+left,-94),
                (-60+left,-146),(-23+left,-169),
                (-5+left,-159),(-7+left,-43)],self.iron,7.5,3.5,2.5)
        poly(c,[(69+right,-46),(79+right,-94),
                (60+right,-146),(23+right,-169),
                (5+right,-159),(7+right,-43)],self.bronze,7.5,3.5,2.5)
        for sign,shift in ((-1,left),(1,right)):
            for row in range(6):
                y=-45-row*17
                width=56-(row%2)*7
                x=sign*(width-14)+shift
                vein(c,[(sign*7+shift,y),(x,y-8),
                        (sign*(width+5)+shift,y-14)],self.sand.light,1.2,.69)
                disk(c,x,y-7,2.3,2.3,self.core,.35)
            # Real raised crest spikes in shell, instead of the normal beetle horns.
            for k in range(4):
                x=shift+sign*(28+11*k)
                y=-149+12*(k%2)
                poly(c,[(x-sign*7,y+6),(x,y-16),(x+sign*7,y+7)],
                     self.sand,2,.85)
        # Internal machinery-glow core is occluded when shell is closed.
        if open_:
            radial_glow(c,0,-108,60,self.core.base,.30*open_)
            rune(c,0,-107,19+open_*19,self.core.light,.74)
            for a in range(8):
                th=a*TAU/8+p['t']*.5
                disk(c,math.cos(th)*28,-108+math.sin(th)*28,3,3,self.core,.45)
        # Horned armored head emerges BELOW the shell and has exposed mandibles.
        hx0=22 if side else 0
        poly(c,[(-32+hx0,-86),(-30+hx0,-112),
                (-15+hx0,-130),(17+hx0,-130),
                (34+hx0,-112),(31+hx0,-81),
                (18+hx0,-57),(-18+hx0,-58)],self.dark,3.7,1.4)
        for sign in (-1,1):
            poly(c,[(hx0+sign*15,-111),(hx0+sign*24,-157),
                    (hx0+sign*40,-170),(hx0+sign*31,-135),
                    (hx0+sign*19,-99)],self.sand,3.2,1.3)
            if not up:
                disk(c,hx0+sign*18,-101,5.6,5.6,self.core,1)
                disk(c,hx0+sign*18,-101,2,2,self.dark,.4)
        poly(c,[(-12+hx0,-68),(hx0,-56),(13+hx0,-68),
                (hx0,-80)],self.bronze,1.4,.65)
        if slam or fort:
            for r in (60,84,106):
                stroke(c,lambda cc,r=r:cc.arc(0,-4,r,PI*.18,PI*.82),
                       hx('#b6fff0'),2.0,.26*max(slam,fort))
        c.restore()


class MothOracle(Boss):
    name='moth_oracle'
    def __init__(self):
        self.wing=Pal('#54465f','#343046','#9981a5','#241e36')
        self.cream=Pal('#cfb68f','#958574','#f7e7c0','#665667')
        self.ink=Pal('#302e4e','#1e2339','#746f9b','#191b30')
        self.neon=Pal('#a973c2','#754f9c','#e5b8ed','#513570')
        self.eye=Pal('#65b3bb','#458199','#c1ffff','#2a667e')
    def body(self,c,v,p):
        side=v=='side';up=v=='up';g=p['wingbeat']
        cast=p['spell'];oracle=p['ultimate'];lash=p['swing']
        c.save();c.translate(0,-8+g*2.3)
        # Broad, layered ocelli stay INSIDE a 384px RGBA boss sprite.
        # Never silently clip the expensive feathered tips at the atlas edge.
        c.scale(.82,1.0)
        # Gigantic layered OCELLI rosette (multiple concentric wings).
        for tier in (2,1,0):
            for sign in (-1,1):
                scale=1+.2*tier
                span=(78+12*tier+9*g)*scale
                if side:span*=.65
                cy=-155+26*tier
                poly(c,[(sign*8,-123),
                        (sign*(26+9*tier),cy-10),
                        (sign*span,cy-44),
                        (sign*(span+22),cy),
                        (sign*(span-10),cy+42),
                        (sign*29,-90)],self.wing if tier%2 else self.ink,3.4,1.8,1.4)
                ex=sign*(53+11*tier)*(.7 if side else 1)
                ey=cy-5
                disk(c,ex,ey,17+2*tier,22+2*tier,self.cream,2)
                disk(c,ex,ey,12+2*tier,16+2*tier,self.neon,1.2)
                disk(c,ex,ey,6+2*tier,9+2*tier,self.eye,.9)
                disk(c,ex,ey,2,5,self.ink,.4)
                for k in range(7):
                    a=k*TAU/7
                    x=ex+math.cos(a)*(22+2*tier)
                    y=ey+math.sin(a)*(27+2*tier)
                    disk(c,x,y,2.4,3,self.cream,.4)
                for k in range(5):
                    vx=sign*(24+k*11)
                    vy=cy-26+k*13
                    vein(c,[(sign*10,-121),(vx,vy),
                            (sign*span,cy-33+k*12)],self.cream.light,.8,.54)
        # Narrow spectral core, neither ordinary moth torso nor human body.
        for j in range(7):
            y=-75+j*13
            poly(c,[(-11+j%2,y-12),(0,y-17),
                    (12-j%2,y-12),(9,y+4),(0,y+9),
                    (-9,y+4)],self.ink if j%2 else self.cream,1.7,.85)
        poly(c,[(-18,-120),(0,-137),(18,-122),
                (12,-91),(0,-86),(-13,-92)],self.neon,3,1.4)
        for sign in (-1,1):
            segmented(c,[(sign*13,-107),(sign*(30+lash*15),-78),
                         (sign*(37+lash*18),-59)],self.ink,3.4)
            # Plumose antennae shaped as ritual forks, not duplicated small moth.
            segmented(c,[(sign*7,-169),(sign*16,-202),
                         (sign*34,-223)],self.cream,2)
            for j in range(5):
                x=sign*(15+j*4);y=-198-j*5
                vein(c,[(x,y),(x+sign*9,y+3)],self.cream.light,1.2,.8)
                vein(c,[(x,y),(x-sign*8,y-4)],self.cream.light,1.2,.8)
        poly(c,[(-17,-155),(-12,-176),(0,-185),
                (17,-176),(19,-153),(0,-140)],self.cream,3.3,1.5)
        if not up:
            for sign in (-1,1):
                disk(c,sign*9,-168,5,8,self.eye,.85)
                disk(c,sign*9,-170,2,3,self.ink,.3)
        else:
            poly(c,[(-9,-165),(0,-175),(10,-165),
                    (0,-156)],self.neon,1,.55)
        if cast or oracle:
            scale=max(cast,oracle)
            rune(c,0,-118,19+48*oracle,self.eye.light,.4+.55*scale)
            radial_glow(c,0,-116,52,self.neon.base,.26*scale)
            for j in range(11):
                a=j*TAU/11+p['t']
                x=math.cos(a)*(60+oracle*20)
                y=-115+math.sin(a)*(43+oracle*10)
                disk(c,x,y,2+(j%3),3,self.neon,.4)
        c.restore()


class QueenVespara(Boss):
    name='queen_vespara'
    OY=288  # wings and long venom tail both fit inside 384px
    def __init__(self):
        self.black=Pal('#252939','#181b28','#626e7a','#171724')
        self.gold=Pal('#c49861','#856341','#ffdaa1','#563e37')
        self.blood=Pal('#a94b57','#702b42','#e88b73','#52253b')
        self.wing=Pal('#8aa9a9','#607e91','#e0e7da','#43566c')
        self.venom=Pal('#a0b86b','#617e58','#e8fbb0','#3d633e')
    def body(self,c,v,p):
        side=v=='side';up=v=='up';g=p['gait']
        dive=p['spell'];swarm=p['ultimate'];sting=p['lunge']
        c.save();c.translate(0,-12-3*g-8*dive)
        # Four paired, hinged queen wings independently flap, distinct from
        # vespa_lancer by large scalloped wing outline and broad shoulder mount.
        for tier in (1,0):
            for sign in (-1,1):
                ext=(104+19*tier+11*p['wingbeat'])*(.68 if side else 1)
                cy=-178+38*tier
                poly(c,[(sign*(9+tier*4),-136),
                        (sign*48,cy-20),
                        (sign*ext,cy-48),
                        (sign*(ext+9),cy-20),
                        (sign*(ext-6),cy+14),
                        (sign*47,cy+32),(sign*16,-104)],self.wing,2.7,1.2)
                for j in range(6):
                    yy=cy-36+j*10
                    vein(c,[(sign*12,-137),
                            (sign*(36+j*10),yy-5),
                            (sign*ext,yy)],self.wing.light,.95,.64)
                    disk(c,sign*(45+j*8),yy,1.6,1.9,self.gold,.3)
        # Six trailing legs with royal knee guards, no normal human thighs.
        for j in range(3):
            for sign in (-1,1):
                k=g*sign*(1 if j%2 else -1)
                x=sign*(11+6*j)
                segmented(c,[(x,-113+14*j),
                             (x+sign*(18+5*j),-64+9*j-5*k),
                             (x+sign*(31+6*j+k*4),-9+3*j)],self.black,3.8)
                poly(c,[(x+sign*(17+j*6),-63+9*j),
                        (x+sign*(30+j*7),-59+9*j),
                        (x+sign*(27+j*5),-45+8*j)],self.gold,1.2,.7)
        # Giant asymmetric royal abdomen of seven distinct chitin rings.
        tailx=18 if side else 0
        for j in range(7):
            y=-87+j*16
            width=11+5*j
            shift=tailx+(j*j*.8)*(1 if side else 0)
            poly(c,[(shift-width,y-10),
                    (shift+width,y-10),
                    (shift+width+3,y+5),
                    (shift,y+14),
                    (shift-width-3,y+5)],self.gold if j%2 else self.black,2.3,1.2)
            vein(c,[(shift-width+4,y-4),(shift,y-7),
                    (shift+width-4,y-4)],self.blood.light,1.3,.77)
            for sign in (-1,1):disk(c,shift+sign*(width-5),y,2.2,2.2,self.venom,.35)
        # Long articulated venom trident at the abdomen tip.
        tail_tip=tailx+(20 if side else 0)
        poly(c,[(tail_tip-9,31),(tail_tip+8,31),
                (tail_tip+11,48),(tail_tip,62),
                (tail_tip-11,47)],self.black,2,.95)
        for j in (-1,0,1):
            poly(c,[(tail_tip+j*9,47),
                    (tail_tip+j*9-3,54+sting*8),
                    (tail_tip+j*9,75+sting*12),
                    (tail_tip+j*9+3,54+sting*8)],self.venom,1.2,.75)
        # Queen's faceted crest is anatomically grown into the mandibles.
        poly(c,[(-22,-128),(-20,-165),(0,-181),
                (20,-165),(23,-131),(0,-117)],self.blood,3.5,1.7)
        for j in (-1,0,1):
            x=j*11
            poly(c,[(x-7,-166),(x-4,-186-7*(j==0)),
                    (x,-211-11*(j==0)),
                    (x+5,-185),(x+7,-167)],self.gold,2.1,.85)
        for sign in (-1,1):
            segmented(c,[(sign*10,-169),(sign*20,-198),
                         (sign*28+p['wingbeat']*2,-211)],self.black,2)
            if not up:
                disk(c,sign*15,-158,5.5,6.5,self.venom,.8)
                disk(c,sign*15,-159,2,3,self.black,.3)
        if dive or swarm:
            scale=max(dive,swarm)
            radial_glow(c,tail_tip,49,42,self.venom.base,.43*scale)
            for j in range(12):
                a=j*TAU/12+p['t']*2
                x=math.cos(a)*88;y=-113+math.sin(a)*47
                disk(c,x,y,2+j%3,3,self.venom,.6)
        c.restore()


class BroodTyrant(Boss):
    name='brood_tyrant'
    def __init__(self):
        self.husk=Pal('#5b3946','#302636','#996a68','#251c2e')
        self.bone=Pal('#bd9976','#816749','#ffdbac','#513f3e')
        self.egg=Pal('#9f9b79','#66795f','#d9dbad','#425046')
        self.dark=Pal('#2e303c','#181c2c','#686371','#191a27')
        self.ether=Pal('#a13c66','#673151','#ef81a3','#50273e')
    def body(self,c,v,p):
        side=v=='side';up=v=='up';g=p['gait']
        brood=p['spell'];rupture=p['ultimate'];slam=p['lunge']
        c.save();c.translate(0,4*slam)
        # Ten unevenly sized legs define an ASYMMETRIC mobile hive.
        for j in range(5):
            for sign in (-1,1):
                shift=9 if sign>0 else -6
                root=sign*(11+7*j)+shift
                q=g*(1 if (j+(sign>0))%2 else -1)
                knee=(root+sign*(13+4*j+q*2),-51-j*4)
                foot=(root+sign*(22+6*j+5*q),-3+j%3*2)
                segmented(c,[(root,-84+j*5),knee,foot],
                          self.dark if j%2 else self.husk,4.2+(j%3)*1.7)
                poly(c,[(foot[0]-sign*9,-7),(foot[0]+sign*8,-10),
                        (foot[0]+sign*20,1)],self.bone,1.5,.8)
        # Off-centre hive dome and hanging transparent brood pods.
        shift=22 if side else 6
        poly(c,[(-69+shift,-57),(-74+shift,-106),
                (-49+shift,-151),(-19+shift,-171),
                (32+shift,-160),(68+shift,-116),
                (74+shift,-67),(39+shift,-35),
                (-29+shift,-31)],self.husk,6.8,3.1,2.4)
        for j in range(9):
            y=-45-j*13
            width=50-(j%3)*7
            vein(c,[(shift-width,y-2),(shift,y-14),
                    (shift+width,y-2)],self.bone.light,1.1,.59)
            for sign in (-1,1):
                disk(c,shift+sign*(width-8),y-5,2,2,self.ether,.4)
        for j in range(7):
            a=j*TAU/7+p['t']*.12
            x=shift+math.cos(a)*(31+7*rupture)
            y=-86+math.sin(a)*(31+8*rupture)
            disk(c,x,y,10+3*(j%3)+5*brood,15+3*(j%2),
                 self.egg if j%2 else self.bone,1.3)
            disk(c,x+2,y+2,3.2,4.5,self.ether,.7)
            if rupture:
                radial_glow(c,x,y,16,self.ether.base,.35*rupture)
        # Two unpaired mandibular heads: boss uses no normal humanoid face.
        for j in (0,1):
            x=(-30 if j==0 else 24)+(shift*.16)
            yy=-131 if j==0 else -160
            poly(c,[(x-20,yy+4),(x-22,yy-17),
                    (x,yy-34),(x+22,yy-17),
                    (x+17,yy+9),(x,yy+16)],self.dark if j==0 else self.bone,3,1.2)
            for sign in (-1,1):
                if not up:
                    disk(c,x+sign*10,yy-16,4.3,5.2,self.ether,.8)
                poly(c,[(x+sign*11,yy+3),
                        (x+sign*(26+8*slam),yy+19),
                        (x+sign*(20+8*slam),yy+34),
                        (x+sign*7,yy+17)],self.bone if j==0 else self.husk,2.0,.9)
        # Horns and barbs make the upper silhouette a ruined hive crown.
        for j in range(6):
            x=shift-43+16*j
            y=-152-(j%3)*9
            poly(c,[(x-9,y+10),(x,y-25),(x+7,y+10)],
                 self.bone if j%2 else self.husk,2,.95)
        if brood or rupture:
            rune(c,shift,-107,24+rupture*54,self.ether.light,.48+.4*max(brood,rupture))
            for j in range(9):
                th=j*TAU/9+p['t']*.6
                x=shift+math.cos(th)*(61+rupture*19)
                y=-106+math.sin(th)*(51+rupture*17)
                disk(c,x,y,3+(j%2)*2,4,self.egg,.5)
        c.restore()


BOSSES={x.name:x() for x in
        (MantisHighReaper,ScarabColossus,MothOracle,QueenVespara,BroodTyrant)}
