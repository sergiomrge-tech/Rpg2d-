"""Lote 2 / Set A — independently built HD 2D insectoids for Unity.

Production sprites, NOT concept art. Same Cairo paint()/Pal()/outline
technique as all existing Aetheria characters. Body plans do not share
the mantis, scarab, moth, imp or humanoid skeleton.
"""
import math
from core import Pal, paint, ellipse, smooth_poly, stroke, radial_glow, hx
from lote2_insects import Insect, poly, disk, limb, vein
TAU=math.tau
PI=math.pi


def segmented(c, pts, pal, size=2.3):
    """Hand-painted articulated chitin with raised socket joints."""
    limb(c,pts,size,pal)
    for x,y in pts[1:-1]:
        disk(c,x,y,size*.88,size*.88,pal,.7)


class Termite(Insect):
    name="termite_burrower"
    FW=FH=288; OX=144; OY=245
    ANIMS={
        "idle":(10,10,True,-1), "move":(14,13,True,-1),
        "attack":(12,15,False,7), "cast":(16,14,False,10),
        "hurt":(7,14,False,-1), "death":(14,11,False,-1)
    }

    def __init__(self):
        self.chitin=Pal("#9f7a57","#675148","#d5b386","#43353c")
        self.clay=Pal("#514a49","#2a2d34","#8c7971","#241f29")
        self.ochre=Pal("#ba8b52","#835b42","#efcd89","#514035")
        self.bone=Pal("#d6c29a","#988772","#f9ebc9","#635046")
        self.ember=Pal("#d36d3d","#a34636","#ffbc6d","#73342b")

    def body(self,c,v,p):
        side=v=="side";back=v=="up";g=p["step"] if p["mode"]=="move" else p["flutter"]*.14
        dig=p["spell"];bite=p["swing"]
        c.save()
        # It stays low: a burrowing six-legged quadruped, NEVER an upright soldier.
        c.translate(0,15*dig)
        c.scale(1,1-.25*dig)
        # Hinged third pair of broad digging paddles, every pair moves separately.
        for pair in range(3):
            for s in (-1,1):
                bx=s*(17+pair*12)
                phase=g*(1 if pair%2 else -1)*s
                knee=(bx+s*(12+pair*4),-30+2*pair-6*phase)
                tip=(bx+s*(20+pair*7+phase*5),-7+2*phase)
                segmented(c,[(bx,-52+pair*5),knee,tip],self.clay,5.5+pair*.5)
                poly(c,[(tip[0]-s*12,-9),(tip[0]+s*9,-14),
                        (tip[0]+s*20,0),(tip[0]-s*8,2)],self.bone,1.6,.9)
                for tooth in range(3):
                    vein(c,[(tip[0]+s*(tooth*6),-4),(tip[0]+s*(tooth*6+4),2)],self.ochre.light,1.0,.68)
        # Tapered abdomen with segment seams; not the domed beetle shell.
        tailx=-36 if side else 0
        poly(c,[(-40+tailx,-47),(-39+tailx,-79),(-24+tailx,-105),
                (3+tailx,-109),(34+tailx,-82),(43+tailx,-52),
                (19+tailx,-31),(-21+tailx,-33)],self.chitin,4.4,2)
        for band in range(5):
            y=-48-band*12
            width=30-(band%2)*5
            poly(c,[(-width+tailx,y-6),(-width+tailx+6,y-10),
                    (width+tailx-6,y-10),(width+tailx,y-6),
                    (width+tailx-3,y+2),(-width+tailx+3,y+2)],self.ochre if band%2 else self.chitin,1.3,.7,.8)
            vein(c,[(-width+tailx+5,y-6),(tailx,y-9),(width+tailx-5,y-6)],self.bone.light,.7,.55)
            for s in (-1,1):
                disk(c,tailx+s*(width-6),y-3,2.2,2.2,self.clay,.4)
        # Dark spade-shaped cephalothorax; back shows chitin armor rather than eyes.
        hx0=(26 if side else 0)+4*bite
        poly(c,[(-29+hx0,-66),(-30+hx0,-96),(-15+hx0,-120),
                (14+hx0,-119),(31+hx0,-95),(28+hx0,-69),
                (16+hx0,-52),(-17+hx0,-54)],self.clay,3.5,1.8)
        poly(c,[(-20+hx0,-94),(hx0,-110),(22+hx0,-94),
                (18+hx0,-77),(hx0,-72),(-18+hx0,-79)],self.chitin,1.9,.8)
        if back:
            poly(c,[(-14+hx0,-98),(hx0,-109),(15+hx0,-98),
                    (hx0,-88)],self.ochre,1.4,.8)
        else:
            for s in (-1,1):
                disk(c,hx0+s*15,-87,3.5,4.4,self.ember,.6)
                disk(c,hx0+s*15-1,-89,1.2,1.4,self.bone,.2)
        # Distinctive paired shovel-mandibles used for tunneling/ambush.
        for s in (-1,1):
            spread=12*bite
            poly(c,[(hx0+s*15,-69),(hx0+s*(33+spread),-66),
                    (hx0+s*(40+spread),-34),(hx0+s*(22+spread),-31),
                    (hx0+s*7,-49)],self.bone,2.2,1.2)
            poly(c,[(hx0+s*(30+spread),-45),(hx0+s*(44+spread),-38),
                    (hx0+s*(39+spread),-26)],self.ochre,1.1,.7)
            for j in range(3):
                x=hx0+s*(19+j*6+spread)
                vein(c,[(x,-57+j*5),(x+s*4,-52+j*5)],self.clay.light,1,.7)
        # High fidelity etched quarry patterns, asymmetric clay deposits and vents.
        for i in range(7):
            xx=tailx+(-21+i*7)
            yy=-58-(i%3)*15
            poly(c,[(xx-4,yy),(xx,yy-5),(xx+5,yy),
                    (xx+2,yy+5)],self.clay if i%2 else self.chitin,.7,.35,.65)
        for s in (-1,1):
            segmented(c,[(hx0+s*21,-91),(hx0+s*32,-111),(hx0+s*36,-123)],self.chitin,1.7)
            if dig:
                radial_glow(c,hx0+s*23,-34,19,self.ember.base,.4*dig)
        if dig:
            for k in range(5):
                rad=22+9*k+8*dig
                stroke(c,lambda cc,r=rad:cc.arc(0,-1,r,PI*.9,PI*2.1),
                       hx("#d8ae72"),1.2+dig,.4*dig)
        c.restore()


class Vespa(Insect):
    name="vespa_lancer"
    FW=FH=288; OX=144; OY=251
    ANIMS={
        "idle":(10,12,True,-1),"move":(14,19,True,-1),
        "attack":(13,20,False,8),"cast":(16,19,False,10),
        "hurt":(7,15,False,-1),"death":(14,12,False,-1)
    }

    def __init__(self):
        self.gold=Pal("#cf9b57","#8c603f","#ffe2a1","#52353a")
        self.black=Pal("#292d38","#151b2a","#555963","#151522")
        self.ruby=Pal("#ad4550","#742d42","#f49b69","#4c2132")
        self.wing=Pal("#7b9ba1","#4d6474","#c5dfe0","#394257")
        self.venom=Pal("#8fbb6c","#57834b","#e5f8a3","#395a3d")

    def body(self,c,v,p):
        side=v=="side";back=v=="up"
        g=p["step"] if p["mode"]=="move" else p["flutter"]*.16
        beat=p["flutter"]*(.8 if p["mode"] in ("idle","move") else .25)
        sting=p["swing"];dive=p["spell"]
        c.save();c.translate(0,-10-2.5*g-4*dive)
        c.scale(.97,1.0)
        # Four fully separate membranous wings rooted in a slim thorax.
        for s in (-1,1):
            for k in (0,1):
                sy=-115-k*16
                extension=(67+13*k+7*beat) if not side else 44+7*k+5*beat
                end=(s*extension,sy-38-k*11+beat*4)
                poly(c,[(s*(8+k*3),-114),(s*(34+k*5),sy-10),
                        end,(end[0]+s*9,sy+15),
                        (s*(22+k*4),sy+22)],self.wing,2.0,.9,.9)
                for j in range(3):
                    vein(c,[(s*12,-113),(s*(31+j*9),sy-16-j*6),end],
                         self.wing.light,.85,.67)
                vein(c,[(end[0]-s*3,end[1]+7),(s*23,sy+18)],self.black.light,.8,.35)
        # Slender hanging legs, NOT the mantis' high reverse knees.
        for pair in range(3):
            for s in (-1,1):
                q=g*(-1 if pair%2 else 1)*s
                x=s*(11+pair*6)
                knee=(x+s*(10+pair*2),-55+pair*6+q*3)
                tip=(x+s*(15+pair*3+q*4),-11+pair*4)
                segmented(c,[(x,-98+pair*11),knee,tip],self.black,2.4+pair*.1)
                poly(c,[(tip[0]-s*3,tip[1]-3),(tip[0]+s*6,tip[1]-6),
                        (tip[0]+s*11,tip[1]+3)],self.gold,.9,.5,.6)
        # Enormous four-segment abdomen dangling from needle waist.
        bend=(14 if side else 0)+10*sting
        poly(c,[(-8,-100),(8,-100),(7,-86),(-7,-86)],self.black,1.5,.65)
        for k in range(5):
            y=-84+k*12
            width=10+((k+1)//2)*4
            x=bend*k/5
            poly(c,[(x-width,y-12),(x+width,y-12),(x+width+2,y),
                    (x+width-3,y+5),(x-width+3,y+5),(x-width-2,y)],self.gold if k%2 else self.black,1.6,.8)
            vein(c,[(x-width+3,y-8),(x,y-11),(x+width-3,y-8)],
                 self.ruby.light,1.25,.73)
            for s in (-1,1):disk(c,x+s*(width-3),y-2,2,2,self.ruby,.4)
        # Flexible organic spear/venom sting; never a handheld weapon.
        tailx=bend+8*sting
        poly(c,[(tailx-8,-20),(tailx+6,-26),
                (tailx+6,-3),(tailx,-1),(tailx-5,-4)],self.black,2.0,1)
        poly(c,[(tailx-4,-7),(tailx,-1),(tailx+6,-7),
                (tailx+2,18+9*sting)],self.venom,2,.9)
        # Multi-faceted long head and thin waist are dominant differences.
        poly(c,[(-15,-134),(0,-153),(15,-135),(13,-108),
                (0,-98),(-13,-109)],self.black,2.8,1.2)
        poly(c,[(-12,-133),(0,-143),(12,-131),(0,-119)],self.gold,1.5,.9)
        poly(c,[(-19,-156),(-10,-173),(4,-178),
                (17,-159),(15,-143),(-13,-144)],self.gold,3,1.4)
        poly(c,[(-9,-156),(4,-166),(9,-153),(4,-143),(-9,-146)],self.black,1.2,.5)
        for s in (-1,1):
            segmented(c,[(s*9,-160),(s*22,-183),(s*34+beat*2,-193)],self.black,1.2)
            if not back:
                disk(c,s*11,-158,4.4,6,self.ruby,.5)
                disk(c,s*12,-160,1.2,1.4,self.gold,.2)
            # Chest side grooves and vivid arcane venom chambers.
            vein(c,[(s*13,-131),(s*18,-117),(s*14,-103)],self.gold.light,1,.7)
            disk(c,s*10,-116,2.7,3.6,self.venom,.5)
        for j in range(3):
            x=-8+j*8
            vein(c,[(x,-125),(x+3,-119),(x,-113)],self.ruby.light,.9,.62)
        if dive:
            for s in (-1,1):
                radial_glow(c,s*38,-116,19,self.venom.base,.5*dive)
            radial_glow(c,tailx,-1,26,self.venom.base,.65*dive)
        c.restore()


class Cicada(Insect):
    name="cicada_screecher"
    FW=FH=288; OX=144; OY=250
    ANIMS={
        "idle":(11,12,True,-1),"move":(13,16,True,-1),
        "attack":(12,17,False,6),"cast":(17,15,False,10),
        "hurt":(7,14,False,-1),"death":(14,11,False,-1)
    }
    def __init__(self):
        self.dark=Pal("#3c4053","#252b3c","#696c83","#1a1d2c")
        self.chitin=Pal("#8d5a58","#5d3b4b","#d79578","#382735")
        self.copper=Pal("#af865d","#765847","#e6c197","#49353b")
        self.wing=Pal("#7790ac","#495e7c","#cfdfeb","#293e51")
        self.sound=Pal("#60c7cc","#398993","#c7ffff","#245c76")

    def body(self,c,v,p):
        side=v=="side";back=v=="up"
        g=p["step"] if p["mode"]=="move" else p["flutter"]*.1
        tremor=p["flutter"]*.5
        shriek=p["spell"];jab=p["swing"]
        c.save();c.translate(0,-5+g*2)
        # The cicada is a rounded sound amplifier with FOUR triangular glass wings.
        # Wings have an independent vibration pattern and multi-branch vein network.
        for s in (-1,1):
            for k in range(2):
                root=(s*10,-117+k*22)
                endx=s*(76+13*k+5*tremor)
                endy=-180+45*k-5*tremor
                poly(c,[root,(s*(41+10*k),-155+k*15),(endx,endy),
                        (endx+s*(16-5*k),endy+34),
                        (s*(40+10*k),-81+k*10)],self.wing,2.2,1.4,.95)
                for stripe in range(4):
                    x=s*(28+stripe*12)
                    vein(c,[root,(x,-140+k*15+stripe*4),
                            (endx+s*3,endy+8+stripe*4)],self.wing.light,.95,.7)
                for stripe in range(3):
                    x=s*(39+stripe*11)
                    vein(c,[(x,-115+k*17),(x+s*9,-123+k*17)],
                         self.copper.light,.8,.5)
        # Six articulated clinging legs; elbow-hinges differ from the long vespa.
        for pair in range(3):
            for s in (-1,1):
                x=s*(13+pair*7)
                phase=g*(-1 if pair%2 else 1)*s
                segmented(c,[(x,-93+pair*10),
                             (x+s*(20+4*phase),-51+pair*6),
                             (x+s*(28+8*phase),-8+pair*2)],
                          self.dark,2.8)
                vein(c,[(x+s*(27+8*phase),-9),
                        (x+s*(37+8*phase),-3)],self.copper.light,1.1,.8)
        # Large domed thorax, with visible segmented sound chambers.
        poly(c,[(-26,-128),(-39,-106),(-35,-75),(-21,-52),
                (24,-53),(36,-76),(37,-110),(24,-131),
                (0,-141)],self.chitin,4.5,2.2)
        for s in (-1,1):
            poly(c,[(s*10,-120),(s*26,-116),(s*30,-91),
                    (s*22,-67),(s*8,-72),(s*4,-104)],self.copper,1.5,.8,.9)
            for j in range(4):
                yy=-77-j*12
                vein(c,[(s*13,yy),(s*25,yy-5),(s*28,yy-11)],
                     self.dark.light,1.1,.75)
            disk(c,s*22,-90,7,13,self.dark,1.0)
            disk(c,s*22,-90,2.5,8,self.sound,.4)
        # Chest resonator visibly enlarges and pulses on skill frame.
        radius=16+12*shriek+2*jab
        disk(c,0,-91,radius,radius*.92,self.dark,2.4)
        disk(c,0,-91,radius*.70,radius*.70,self.sound,1.3)
        disk(c,0,-91,radius*.42,radius*.42,self.copper,.75)
        for s in (-1,1):
            disk(c,s*9,-92,2.2,2.2,self.dark,.4)
        # Broad rectangular head with lateral large compound eyes;
        # not the wasp's needle face or moth's feathery head.
        poly(c,[(-25,-143),(-21,-165),(-10,-178),
                (10,-178),(23,-164),(23,-142),
                (11,-132),(-12,-131)],self.copper,3.3,1.5)
        for s in (-1,1):
            disk(c,s*22,-157,9.5,14,self.sound,1.8)
            for i in range(3):
                for j in range(3):
                    disk(c,s*22-4+i*3,-162+j*4,1.0,1.0,self.dark,.2)
            segmented(c,[(s*9,-175),(s*20,-186),(s*25+tremor,-195)],self.chitin,1.4)
        if back:
            # Back shows thoracic dorsal split, not a mirrored smiling face.
            poly(c,[(-12,-156),(0,-169),(12,-156),
                    (8,-144),(0,-139),(-8,-143)],self.chitin,1,.55)
        else:
            poly(c,[(-12,-143),(0,-147),(13,-142),
                    (6,-131-jab*9),(0,-127),(-6,-131-jab*9)],
                 self.dark,1.4,.9)
        # Wave rings on the actual cast keyframes, linked to gameplay shockwave.
        if shriek:
            for j in range(3):
                radius=43+j*21+10*shriek
                stroke(c,lambda cc,r=radius:cc.arc(0,-91,r,.08,TAU-.08),
                       hx("#9af1f4"),1.5+j*.35,(.4-j*.08)*shriek)
                for side_sign in (-1,1):
                    radial_glow(c,side_sign*(42+j*12),-91,12+j*4,
                                self.sound.base,.20*shriek)
        # Fine, intentionally different barcodes on dorsal sound plates.
        for j in range(8):
            yy=-61-j*7
            length=11+j%3*3
            vein(c,[(-length,yy),(0,yy-3),(length,yy)],
                 self.copper.light,.65,.47)
        c.restore()

CREATURES_A={cls.name:cls() for cls in (Termite,Vespa,Cicada)}
