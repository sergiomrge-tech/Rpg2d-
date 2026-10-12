"""Three anatomically independent HD-cartoon insectoid demon rigs for Aetheria.

Real deterministic Cairo-cel-shaded frames; not image-generation mockups.
Each rig has physically distinctive legs/head/thorax, facing-specific silhouettes,
and animated idle/move/attack/cast/hurt/death. No reuse of humanoid or imp rig.
"""
import math
from core import Pal, paint, smooth_poly, ellipse, capsule, stroke, radial_glow, hx

PI=math.pi
TAU=math.tau


def poly(c,points,pal,shadow=3,highlight=1.2,line=1.4):
    paint(c,lambda p:smooth_poly(p,points,tension=.33),pal,sh=shadow,hl=highlight,line=line)


def disk(c,x,y,rx,ry,pal,s=1.5):
    paint(c,lambda p:ellipse(p,x,y,rx,ry),pal,sh=s,hl=s*.55,line=1.0)


def limb(c,points,width,pal):
    for a,b in zip(points,points[1:]):
        paint(c,lambda p,a=a,b=b:capsule(p,a,b,width,width*.72),pal,sh=1.7,hl=.8,line=1.0)
        disk(c,b[0],b[1],width*.65,width*.65,pal,.6)


def vein(c,points,col,w=1.4,alpha=.85):
    def path(p):
        p.move_to(*points[0]);[p.line_to(*pt) for pt in points[1:]]
    stroke(c,path,col,w,alpha)


def spot(c,x,y,r,pal):
    disk(c,x,y,r,r,pal,.6)


class Insect:
    FW=256; FH=256; OX=128; OY=223
    ANIMS={
        'idle':(9,11,True,-1),'move':(12,15,True,-1),
        'attack':(12,18,False,7),'cast':(13,14,False,8),
        'hurt':(6,14,False,-1),'death':(12,12,False,-1)
    }
    def pose(self,action,t,view):
        loop=action in ('move','idle')
        step=math.sin(TAU*t*(1.5 if action=='move' else .5))
        action_s=math.sin(PI*t) if not loop else 0
        return dict(mode=action,t=t,step=step,flutter=math.sin(TAU*t*2.4),
                    swing=action_s if action=='attack' else 0,
                    spell=action_s if action=='cast' else 0,
                    hurt=action_s if action=='hurt' else 0,
                    dead=t if action=='death' else 0,view=view)
    def draw(self,c,view,p):
        c.save()
        c.translate(0,(1-p['dead'])*math.sin(TAU*p['t'])*1.1+p['dead']*25)
        if p['hurt']: c.translate(-6*p['hurt'],0)
        if p['dead']:
            c.rotate(math.radians(31*p['dead']))
            c.scale(1,1-.52*p['dead'])
        if view=='side':
            c.translate(7,0)
            c.scale(.78,1)
        self.body(c,view,p)
        c.restore()

class Mantis(Insect):
    name='mantis_reaver'
    FW=FH=288; OX=144; OY=243
    def __init__(self):
        self.car=Pal('#626845','#373d34','#a7aa70','#282b2e')
        self.bone=Pal('#b8aa7b','#83745a','#f4e2ab','#51483e')
        self.red=Pal('#a83f42','#6a2838','#ee8058','#491e2a')
        self.dark=Pal('#363643','#1a2530','#747577','#171a27')
        self.ember=Pal('#f16c45','#bc3739','#ffdf91','#703239')
    def body(self,c,v,p):
        side=v=='side'; back=v=='up'
        gait=p['step'] if p['mode']=='move' else .1*p['flutter']
        slash=p['swing']; cast=p['spell']
        c.save();c.scale(1.12,1.12)
        # Articulated reversed digitigrade legs, with independently animated ankles.
        for i,s in enumerate((-1,1)):
            bx=(s*15 if not side else 7+i*13)
            tx=bx+s*(12+8*gait*(-s))
            limb(c,[(bx,-57),(bx+s*20,-34),(tx,-18),(tx+s*11,0)],5.8,self.dark)
            poly(c,[(tx-6,-15),(tx+6,-19),(tx+s*11,-3),(tx+s*21,1),(tx-2,1)],self.car,2,.8)
            for k in (0,1,2):
                vein(c,[(tx+s*(6+k*5),-2),(tx+s*(13+k*5),3)],self.bone.light,1)
        # Long asymmetric abdominal scutes and fan of secondary folded wing plates.
        for i in range(7):
            y=-49-i*9
            x=(i%2)*3
            poly(c,[(-15+x,y+8),(-18+x,y-7),(0+x,y-17),(18+x,y-7),(14+x,y+9)],
                self.car if i%2 else self.bone,2.3,1.3)
            vein(c,[(-9+x,y-5),(0+x,y-11),(9+x,y-5)],self.dark.light,1.0,.7)
        for s in (-1,1):
            if back or v=='down':
                poly(c,[(s*8,-66),(s*15,-109),(s*38,-126),(s*41,-97),(s*22,-71)],self.red,3,1.2)
                poly(c,[(s*16,-88),(s*37,-114),(s*29,-93)],self.car,1.3,.8)
            else:
                poly(c,[(-2,-84),(20,-120),(25,-89),(8,-68)],self.red,2,1.1)
        # Pentagonal upper torso and layered thorax under its weapon arms.
        poly(c,[(-18,-106),(0,-126),(21,-109),(19,-72),(0,-60),(-20,-75)],self.car,4,1.7)
        poly(c,[(-13,-105),(0,-120),(14,-105),(10,-91),(-8,-92)],self.bone,1.3,.9)
        poly(c,[(-6,-91),(0,-84),(7,-92),(0,-103)],self.red,1.3,.7)
        if cast:radial_glow(c,0,-92,22,hx('#ff533d'),.7*cast)
        # Slash arms are organically grown scythes, in different poses (not equipment swaps).
        for s in (-1,1):
            sx=s*20 if not side else s*12+9
            reach=(11+26*slash)*s
            shoulder=(sx,-107)
            elbow=(sx+s*(23+9*slash),-79-12*slash)
            claw=(elbow[0]+reach,-59-25*slash)
            limb(c,[shoulder,elbow,claw],7.2,self.dark)
            poly(c,[(claw[0]-s*8,claw[1]-13),(claw[0]+s*21,claw[1]-56),
                    (claw[0]+s*33,claw[1]-61),(claw[0]+s*21,claw[1]-26),
                    (claw[0]+s*15,claw[1]+5)],self.bone,3.7,1.7)
            poly(c,[(claw[0]+s*4,claw[1]-20),(claw[0]+s*23,claw[1]-56),
                    (claw[0]+s*19,claw[1]-25)],self.red,1.4,.8)
            for k in range(3):
                x=claw[0]+s*(8+k*5); y=claw[1]-21-k*8
                poly(c,[(x,y),(x+s*10,y-4),(x+s*4,y+10)],self.dark,1,.6)
            if slash:
                vein(c,[(claw[0]+s*10,claw[1]-51),(claw[0]+s*27,claw[1]-66)],self.ember.light,3*slash)
        # Angular head, serrated mandibles, two extra-long antennae.
        headx=8 if side else 0
        poly(c,[(-17+headx,-126),(-22+headx,-149),(-2+headx,-173),
                (19+headx,-157),(17+headx,-132),(2+headx,-123)],self.car,3.5,1.7)
        poly(c,[(-10+headx,-147),(0+headx,-165),(11+headx,-147),
                (4+headx,-135),(-8+headx,-135)],self.bone,1.8,.7)
        for s in (-1,1):
            x=headx+s*11
            limb(c,[(x,-161),(x+s*15,-184),(x+s*21+p['flutter']*2,-207)],1.4,self.dark)
            poly(c,[(x-s*3,-136),(x+s*5,-132),(x+s*10,-121)],self.dark,1,.5)
            if not back:
                spot(c,x,-148,4,self.ember)
                spot(c,x+s*1,-148,1.2,self.bone)
        if cast:
            for s in (-1,1):
                x=s*(30+cast*17)
                radial_glow(c,x,-76,16,self.ember.base,.45*cast)
        # Final plate engraving and emissive scythe veins: species-specific material pass.
        for j in range(6):
            yy=-64-j*9
            vein(c,[(-10,yy),(0,yy-3),(10,yy)],self.bone.light,.85,.68)
            for sidecar in (-1,1):
                disk(c,sidecar*11,yy,1.5,1.9,self.dark,.3)
        for s in (-1,1):
            for j in range(4):
                x=s*(21+j*5)
                vein(c,[(x,-115-j*3),(x+s*2,-118-j*5)],self.bone.light,.9,.65)
            # Bioluminescent joints on the six-segmented limbs.
            disk(c,s*19,-34,2.2,2.2,self.ember,.3)
            for k in range(3):
                yy=-71+k*9
                poly(c,[(s*(25+k*2),yy),(s*(34+k*2),yy-5),(s*(29+k*2),yy+5)],self.bone,.8,.4,.65)
        for s in (-1,1):
            disk(c,s*13,-101,2.4,2.7,self.ember,.3)
            vein(c,[(s*7,-106),(0,-111),(-s*7,-106)],self.bone.light,1.0,.55)
        c.restore()

class Scarab(Insect):
    name='scarab_brute'
    FW=FH=288; OX=144; OY=242
    ANIMS={'idle':(9,9,True,-1),'move':(12,11,True,-1),
           'attack':(13,16,False,7),'cast':(13,13,False,9),
           'hurt':(7,12,False,-1),'death':(12,10,False,-1)}
    def __init__(self):
        self.shell=Pal('#4d4147','#272935','#8e6c58','#261e2b')
        self.gold=Pal('#af875a','#6e5046','#f1cb82','#3e3033')
        self.lava=Pal('#bf4835','#772d33','#ffa55c','#542834')
        self.black=Pal('#302d3a','#1d202b','#655a5b','#161724')
    def body(self,c,v,p):
        step=p['step'] if p['mode']=='move' else 0
        plunge=p['swing'];cast=p['spell']
        side=v=='side';back=v=='up'
        c.save();c.scale(1.05,1.02)
        # Three independently articulated pairs of legs on each side.
        for pair in range(3):
            for s in (-1,1):
                ax=s*(23+pair*11)
                by=-55+pair*8
                gait=step*(1 if pair%2 else -1)*(1 if s>0 else -1)
                limb(c,[(ax,by),(ax+s*(18+4*gait),-31),(ax+s*(25+8*gait),-5)],8,self.black)
                poly(c,[(ax+s*(16+8*gait),-11),(ax+s*(33+8*gait),-13),
                        (ax+s*(40+8*gait),1),(ax+s*(16+8*gait),1)],self.gold,2,.6)
                disk(c,ax,-44,7,7,self.gold)
        # Dorsal carapace spans more than all other insect enemy torsos.
        shellshift=(8*plunge if side else 0)
        poly(c,[(-63+shellshift,-56),(-67+shellshift,-100),(-54+shellshift,-136),
                (-25+shellshift,-153),(23+shellshift,-153),(58+shellshift,-137),
                (72+shellshift,-99),(59+shellshift,-55),(29+shellshift,-35),(-33+shellshift,-36)],
             self.shell,6.5,3,2.5)
        # Overlapping plates with engraved basalt fissures.
        for s in (-1,1):
            poly(c,[(s*7+shellshift,-146),(s*31+shellshift,-147),
                    (s*56+shellshift,-109),(s*46+shellshift,-68),
                    (s*11+shellshift,-56)],self.gold,2.5,1.3,1.0)
            for off in (0,9,17):
                vein(c,[(s*(14+off)+shellshift,-133),(s*(22+off)+shellshift,-111),
                        (s*(19+off)+shellshift,-85)],self.lava.light,1.2,0.83)
        for k in range(5):
            y=-60-k*17
            disk(c,shellshift,y,6+k*.22,5,self.lava)
            if cast:radial_glow(c,shellshift,y,11,self.lava.base,.24*cast)
        # Beetle head is placed lower than shell and has an organic brow horn.
        headx=(25 if side else 0)+plunge*6
        poly(c,[(-34+headx,-67),(-29+headx,-93),(-8+headx,-106),
                (23+headx,-96),(34+headx,-72),(19+headx,-49),(-20+headx,-48)],self.black,3.2,1.4)
        for s in (-1,1):
            poly(c,[(s*12+headx,-91),(s*23+headx,-132),
                    (s*38+headx,-145),(s*30+headx,-110),
                    (s*18+headx,-83)],self.gold,3.4,1.5)
            if not back:
                disk(c,headx+s*20,-74,4.1,5.2,self.lava)
                poly(c,[(headx+s*10,-52),(headx+s*23,-41),(headx+s*29,-48)],self.gold,1,.5)
        if plunge:
            for s in (-1,1):
                vein(c,[(headx+s*37,-51),(headx+s*53,-35)],self.lava.light,2.7*plunge)
        if cast:
            for s in (-1,1):
                radial_glow(c,s*42,-26,22,self.lava.base,.32*cast)
        # Runic basalt carving over the dorsal plates, riveted chitin seams.
        for sign in (-1,1):
            for j in range(4):
                xx=sign*(21+j*7)+shellshift
                yy=-126+j*13
                vein(c,[(xx,yy),(xx+sign*3,yy+7),(xx+sign*1,yy+13)],self.lava.light,1.45,.76)
                disk(c,xx+sign*3,yy+7,1.8,1.8,self.gold,.4)
            for j in range(3):
                yy=-102+j*19
                poly(c,[(sign*46+shellshift,yy-6),(sign*54+shellshift,yy),
                        (sign*47+shellshift,yy+11)],self.shell,1.4,.65,.8)
        # Encrusted infernal center crest instead of a plain repeated circle.
        poly(c,[(-6+shellshift,-97),(shellshift,-115),(6+shellshift,-97),
                (shellshift,-81)],self.gold,1.3,.75,.85)
        poly(c,[(-2+shellshift,-97),(shellshift,-105),(3+shellshift,-97),
                (shellshift,-88)],self.lava,.7,.35,.5)
        for xx in (-24,24):
            for yy in (-59,-81,-103):disk(c,xx+shellshift,yy,1.6,2.2,self.lava,.3)
        c.restore()

class Moth(Insect):
    name='moth_hexer'
    FW=FH=288; OX=144; OY=247
    ANIMS={'idle':(10,10,True,-1),'move':(12,14,True,-1),
           'attack':(11,16,False,6),'cast':(14,14,False,9),
           'hurt':(6,12,False,-1),'death':(13,10,False,-1)}
    def __init__(self):
        self.wing=Pal('#6e5867','#403546','#af8c90','#2b2936')
        self.cream=Pal('#b4a28a','#776a72','#efe1bf','#564b4b')
        self.violet=Pal('#7b526c','#513d64','#b18ab3','#37273f')
        self.mana=Pal('#c95b70','#893c66','#f9b68e','#673348')
        self.dark=Pal('#333343','#242535','#706979','#211c2a')
    def body(self,c,v,p):
        side=v=='side';back=v=='up'
        flap=p['flutter'] if p['mode'] in ('move','idle') else math.sin(p['t']*PI)
        attack=p['swing'];cast=p['spell'];gait=p['step']
        c.save();c.translate(0,-12+(2.0*flap))
        # Wide feathered eyespot wing mantles; four membranes, not arms with scythes.
        for s in (-1,1):
            span=60+10*flap+14*cast
            if side: span=38+7*flap
            tipx=s*span+(8 if side else 0)
            poly(c,[(s*8,-105),(s*26,-140),(tipx,-168+flap*4),
                    (tipx+s*21,-136),(s*62,-91),(s*38,-66),(s*14,-65)],self.wing,5,2.5)
            for j in range(5):
                x=s*(26+j*9); y=-145+j*13+flap*2
                poly(c,[(s*20,-107),(x,y),(x+s*13,y+12)],self.cream,1.5,.7,.7)
                vein(c,[(s*19,-109),(x,y)],self.wing.light,1.3,.5)
            # Ocelli distinguish from a bat even without color.
            ex=s*(47 if not side else 33)
            disk(c,ex,-117,15,18,self.cream)
            disk(c,ex,-117,10,12,self.violet)
            disk(c,ex,-117,4,6,self.mana)
            # Secondary lower wings independently fold as moving character.
            poly(c,[(s*14,-74),(s*50,-90),(s*(54+4*flap),-40),
                    (s*29,-28),(s*11,-51)],self.violet,2.4,.9)
            vein(c,[(s*17,-69),(s*41,-57),(s*48,-43)],self.cream.light,1.3,.75)
        # Long distinct waist and trailing abdomen segments.
        poly(c,[(-11,-108),(10,-111),(16,-64),(9,-31),(-8,-26),(-15,-60)],self.dark,2.7,1.3)
        for k in range(5):
            y=-52+k*8
            poly(c,[(-9,y-9),(0,y-13),(10,y-9),(7,y+3),(0,y+5),(-8,y+3)],
                 self.cream if k%2 else self.violet,1.3,.5)
        # Four thin clawed limbs with separate motion, below mantle.
        for s in (-1,1):
            limb(c,[(s*7,-43),(s*(17+6*gait),-18),(s*(24+8*gait),-4)],2.4,self.dark)
            poly(c,[(s*(20+8*gait),-8),(s*(28+8*gait),-2),(s*(18+8*gait),1)],self.cream,1,.5)
            limb(c,[(s*10,-99),(s*(18+12*attack),-65),(s*(22+20*attack),-50)],3.2,self.violet)
        # Plumose antennae drawn as fine forked paths; skull has 2 giant facet eyes.
        hx0=6 if side else 0
        poly(c,[(-14+hx0,-134),(-17+hx0,-156),(-4+hx0,-170),
                (14+hx0,-160),(15+hx0,-140),(0+hx0,-127)],self.cream,2.8,1.4)
        for s in (-1,1):
            x=hx0+s*8
            vein(c,[(x,-159),(x+s*18,-182),(x+s*27,-194)],self.cream.light,2)
            for j in range(4):
                xx=x+s*(11+j*4);yy=-173-j*5
                vein(c,[(xx,yy),(xx-s*5,yy-5)],self.cream.light,1.1,.75)
                vein(c,[(xx,yy),(xx+s*4,yy+5)],self.cream.light,1.1,.75)
            if not back:
                disk(c,x,-149,6,8,self.mana)
                disk(c,x+s*1,-151,2.1,3,self.cream)
        if cast:
            for s in (-1,1):
                ex=s*58
                radial_glow(c,ex,-101,26,self.mana.base,.54*cast)
                for i in range(3):
                    x=ex+s*(i*9-10); y=-70-i*9
                    disk(c,x,y,2.3+i*.3,2.8,self.mana,.7)
            radial_glow(c,0,-88,34,self.mana.base,.42*cast)
        # Hand-painted moth-scale highlights, branching wing veins and occult pupils.
        for wing_side in (-1,1):
            for j in range(5):
                yy=-144+j*13
                x=wing_side*(25+j*6)
                vein(c,[(wing_side*19,-117),(x,yy)],self.cream.light,.7,.50)
                vein(c,[(x,yy),(x+wing_side*8,yy-5)],self.cream.light,.7,.42)
            for j in range(4):
                x=wing_side*(20+j*11)
                y=-75+(j%2)*6
                disk(c,x,y,1.6,2.2,self.mana,.3)
            eye_x=wing_side*(47 if not side else 33)
            disk(c,eye_x,-117,2.8,4.5,self.dark,.4)
            disk(c,eye_x-wing_side*1.1,-120,1,1.2,self.cream,.1)
            for k in range(3):
                x=wing_side*(25+k*7)
                poly(c,[(x,-56),(x+wing_side*4,-39),(x+wing_side*8,-56)],self.cream,.8,.5,.7)
        # Segmented ritual sigil embedded into moth thorax.
        poly(c,[(-7,-104),(0,-114),(7,-104),(0,-95)],self.mana,1.0,.7,.7)
        disk(c,0,-104,2.7,3.6,self.cream,.3)
        if cast:
            for j in range(6):
                angle=TAU*j/6+cast*.3
                x=math.cos(angle)*36;y=-100+math.sin(angle)*21
                disk(c,x,y,1.5+cast,1.5+cast,self.mana,.4)
        c.restore()

CREATURES={d.name:d() for d in (Mantis,Scarab,Moth)}