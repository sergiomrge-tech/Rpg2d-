"""LOTE 2 SET B: Four independent production rigged demon sprites.

Everything is drawn from geometric primitives through the game's
Cairo/Pal painted HD-cartoon pipeline. Not an AI image/concept mockup.
Black silhouettes differ radically: tripartite ant, flat roach, curled
spiked isopod and long-tailed four-winged dragonfly.
"""
import math
from core import Pal, paint, ellipse, stroke, smooth_poly, radial_glow, hx
from lote2_insects import Insect, poly, disk, limb, vein
TAU=math.tau
PI=math.pi

def path_joint(c,points,pal,w):
    limb(c,points,w,pal)
    for x,y in points[1:-1]:
        disk(c,x,y,w*.8,w*.8,pal,.4)


class AntGuard(Insect):
    name="ant_guard"
    FW=FH=288; OX=144; OY=245
    ANIMS={
        'idle':(10,10,True,-1),'move':(14,15,True,-1),
        'attack':(13,17,False,7),'cast':(16,14,False,9),
        'hurt':(7,13,False,-1),'death':(14,11,False,-1)
    }
    def __init__(self):
        self.black=Pal('#373044','#1e1b2b','#725267','#171425')
        self.chit=Pal('#995063','#573245','#d28485','#391e32')
        self.plate=Pal('#bc9364','#846142','#f6c991','#553e37')
        self.acid=Pal('#7abb79','#53814f','#d2f9a6','#36603c')
    def body(self,c,v,p):
        sview=v=='side';up=v=='up'
        g=p['step'] if p['mode']=='move' else p['flutter']*.10
        bite=p['swing'];guard=p['spell']
        c.save();c.translate(0,-2*abs(g))
        # ANT: THREE volumes (head, thorax and rear gaster), never a tall
        # person-shaped torso with a weapon.
        rearx=(-31 if sview else 0)
        poly(c,[(-30+rearx,-42),(-33+rearx,-70),(-21+rearx,-92),
                (19+rearx,-91),(36+rearx,-65),(29+rearx,-38),
                (0+rearx,-27)],self.black,4.5,2)
        for j in range(5):
            y=-40-j*9
            poly(c,[(-23+rearx,y-6),(0+rearx,y-12),(23+rearx,y-6),
                    (20+rearx,y+1),(0+rearx,y+6),(-20+rearx,y+1)],
                 self.chit if j%2 else self.black,1.35,.6)
            for k in (-1,1):
                vein(c,[(rearx+k*15,y-4),(rearx+k*21,y-8)],self.plate.light,.9,.55)
        # Pinched petiole and six articulated guard legs with unequal stride.
        for i in range(3):
            for side in (-1,1):
                q=g*(-1 if i%2 else 1)*side
                x=side*(14+i*7)
                knee=(x+side*(18+i*4),-53-i*8+q*5)
                foot=(x+side*(30+i*3+q*5),-2+i*2)
                path_joint(c,[(x,-76+i*9),knee,foot],self.black,3.8+i*.4)
                poly(c,[(foot[0]-side*7,-5),(foot[0]+side*10,-7),
                        (foot[0]+side*18,1),(foot[0]-side*4,1)],self.plate,1.2,.7)
        poly(c,[(-9,-93),(11,-93),(14,-117),
                (6,-124),(-7,-121),(-14,-112)],self.plate,1.4,.7)
        # Military head built as large broad jaw node, with compound facets.
        headx=22 if sview else 0
        poly(c,[(-26+headx,-119),(-24+headx,-153),
                (-11+headx,-171),(16+headx,-174),
                (30+headx,-153),(28+headx,-125),
                (0+headx,-111)],self.chit,3.4,1.5)
        poly(c,[(-19+headx,-142),(0+headx,-159),
                (20+headx,-142),(0+headx,-133)],self.black,1.4,.55)
        if up:
            poly(c,[(-9+headx,-151),(headx,-164),
                    (9+headx,-151),(headx,-145)],self.plate,1,.65)
        else:
            for sign in (-1,1):
                disk(c,headx+sign*17,-150,5.7,7.2,self.acid,.75)
                for row in range(3):
                    for col in range(2):
                        disk(c,headx+sign*17+col*2-1,-154+row*3,1.1,1.1,self.black,.2)
        # Anatomical defensive mandibles unfold to form a curved wedge.
        for sign in (-1,1):
            widen=16*bite+8*guard
            poly(c,[(headx+sign*14,-126),(headx+sign*(31+widen),-123),
                    (headx+sign*(40+widen),-95),
                    (headx+sign*(33+widen),-88),
                    (headx+sign*17,-104)],self.plate,2.7,1.1)
            poly(c,[(headx+sign*(31+widen),-109),
                    (headx+sign*(42+widen),-102),
                    (headx+sign*(31+widen),-98)],self.black,1.0,.4)
            path_joint(c,[(headx+sign*11,-167),
                          (headx+sign*20,-189),
                          (headx+sign*30+2*g,-199)],self.black,1.6)
            if guard:
                vein(c,[(headx+sign*17,-116),(headx+sign*(36+widen),-104)],
                     self.acid.light,2.5,.9)
                radial_glow(c,headx+sign*(38+widen),-100,15,self.acid.base,.35*guard)
        # Ribbed armored joint seams, not a colour variation of scarab.
        for yy in (-80,-69,-57,-46):
            for sign in (-1,1):
                disk(c,rearx+sign*16,yy,2,2,self.plate,.3)
        c.restore()


class RoachPlague(Insect):
    name="roach_plaguebearer"
    FW=FH=288; OX=144; OY=247
    ANIMS={
        'idle':(11,12,True,-1),'move':(15,19,True,-1),
        'attack':(12,17,False,7),'cast':(15,15,False,10),
        'hurt':(7,13,False,-1),'death':(14,11,False,-1)
    }
    def __init__(self):
        self.shell=Pal('#514348','#2d2a36','#8e685d','#221d2b')
        self.oil=Pal('#353944','#1c222e','#646875','#131923')
        self.red=Pal('#a05c58','#733b42','#d59976','#492637')
        self.sick=Pal('#86a75d','#526f48','#e0ec91','#314636')
    def body(self,c,v,p):
        side=v=='side';up=v=='up'
        g=p['step'] if p['mode']=='move' else p['flutter']*.12
        slash=p['swing'];plague=p['spell']
        c.save();c.translate(0,2.0*abs(g))
        # Six jittering legs under a HORIZONTAL flattened ellipsoid.
        for i in range(3):
            for sign in (-1,1):
                root=(sign*(19+i*7),-77+i*12)
                ph=g*(-1 if i%2 else 1)*sign
                mid=(sign*(39+i*6),-45+i*6+ph*9)
                foot=(sign*(57+i*3+ph*6),-3+i*2)
                path_joint(c,[root,mid,foot],self.oil,3.3)
                for j in (0,1):
                    x=mid[0]+sign*(4+j*5);y=mid[1]+10+j*5
                    poly(c,[(x-sign*3,y-7),(x+sign*6,y+2),
                            (x,y+11)],self.red,1,.5)
        # Broad, FLAT dorsal shield starts near the floor and extends sideways.
        shift=-20 if side else 0
        poly(c,[(-63+shift,-45),(-64+shift,-74),
                (-47+shift,-97),(0+shift,-113),
                (48+shift,-98),(67+shift,-72),
                (63+shift,-43),(22+shift,-26),
                (-24+shift,-25)],self.shell,4.5,2.4)
        for sign in (-1,1):
            poly(c,[(shift,-108),(sign*43+shift,-94),
                    (sign*58+shift,-65),(sign*45+shift,-41),
                    (sign*8+shift,-32)],self.oil,2.5,1.3)
            for k in range(5):
                yy=-49-k*10
                xx=shift+sign*(14+4*k)
                vein(c,[(shift+sign*6,yy-5),(xx,yy-13),
                        (shift+sign*43,yy-20)],self.shell.light,.8,.68)
            for k in (0,1,2):
                disk(c,shift+sign*(27+9*k),-66+k*9,1.8,1.8,self.sick,.3)
        # Segmented triangular pronotum, face mostly hidden under shield.
        headx=(34 if side else 0)+8*slash
        poly(c,[(-24+headx,-90),(-27+headx,-120),
                (0+headx,-139),(28+headx,-117),
                (23+headx,-91),(0+headx,-77)],self.red,2.8,1.3)
        poly(c,[(-16+headx,-113),(headx,-131),
                (17+headx,-112),(headx,-101)],self.oil,1.5,.8)
        if not up:
            for sign in (-1,1):
                disk(c,headx+sign*19,-111,4.5,6.0,self.sick,.9)
                disk(c,headx+sign*20,-114,1.5,2,self.oil,.3)
                poly(c,[(headx+sign*12,-88),
                        (headx+sign*(25+slash*6),-73),
                        (headx+sign*(29+slash*6),-81)],self.oil,1,.5)
        # Unmistakable 2 extraordinarily long multi-hinged antennae.
        for sign in (-1,1):
            pnts=[(headx+sign*12,-132),
                  (headx+sign*27,-161),
                  (headx+sign*58+g*2,-197),
                  (headx+sign*(77+g*3),-222)]
            path_joint(c,pnts,self.oil,1.6)
            for i in range(3):
                x=pnts[i+1][0];y=pnts[i+1][1]
                vein(c,[(x,y),(x-sign*6,y-7)],self.red.light,.9,.8)
        if plague:
            # A visible fungal spore discharge around the body.
            for i in range(11):
                a=i*TAU/11
                x=math.cos(a)*(55+plague*23)
                y=-67+math.sin(a)*(36+plague*18)
                disk(c,x,y,2.5+(i%3),3.2,self.sick,.6)
                radial_glow(c,x,y,7,self.sick.base,.26*plague)
        c.restore()


class SpikeBeetle(Insect):
    name="spike_beetle"
    FW=FH=288; OX=144; OY=245
    ANIMS={
        'idle':(10,9,True,-1),'move':(14,16,True,-1),
        'attack':(13,18,False,8),'cast':(16,18,False,10),
        'hurt':(7,12,False,-1),'death':(14,11,False,-1)
    }
    def __init__(self):
        self.iron=Pal('#52505e','#2c303e','#9495a0','#242434')
        self.plating=Pal('#9d7775','#674f5c','#d9a2a0','#3e3147')
        self.bone=Pal('#c6ba9d','#908772','#f6ebd1','#564c53')
        self.fire=Pal('#b45e55','#7c3942','#f8a381','#512f3a')
    def body(self,c,v,p):
        side=v=='side';back=v=='up'
        g=p['step'] if p['mode']=='move' else .1*p['flutter']
        slam=p['swing'];spin=p['spell']
        c.save()
        # Roll genuinely around the centre of its round body, rather than
        # using the same humanoid walking rig with swapped armor.
        c.translate(0,-62)
        c.rotate(spin*PI*1.4)
        c.translate(0,62)
        for j in range(5):
            for sign in (-1,1):
                x=sign*(9+j*7)
                sx=x+sign*(12+(j%2)*4)
                tip=(sx+sign*5*g,-4+j%2*2)
                path_joint(c,[(x,-34),(sx,-16),tip],self.iron,2.8)
                poly(c,[(tip[0]-sign*5,-5),(tip[0]+sign*8,-6),
                        (tip[0]+sign*15,2)],self.bone,.9,.5)
        # Very round jointed body: a spine ball with radial shell segments.
        disk(c,0,-82,59,60,self.iron,4.3)
        for j in range(12):
            a=j*TAU/12+PI/6
            rad=54+8*slam+7*spin
            x=math.cos(a)*rad;y=-82+math.sin(a)*rad
            xx=math.cos(a)*(rad+25+6*spin)
            yy=-82+math.sin(a)*(rad+25+6*spin)
            poly(c,[(x-5,y-5),(xx,yy),(x+6,y+6)],
                 self.bone if j%2 else self.plating,2.1,1)
            vein(c,[(x,y),(xx*.83+x*.17,yy*.83+y*.17)],
                 self.bone.light,1.2,.65)
        for j in range(10):
            a=j*TAU/10+g*.05
            x=math.cos(a)*36;y=-82+math.sin(a)*38
            poly(c,[(0,-82),(x-8,y-6),(x+8,y+6)],self.plating if j%2 else self.iron,2,.9)
            disk(c,x,y,2.4,2.4,self.fire,.5)
        disk(c,0,-82,18,21,self.plating,2.5)
        disk(c,0,-82,11,13,self.iron,1)
        poly(c,[(-5,-82),(0,-96),(6,-82),
                (0,-71)],self.fire,1.3,.7)
        if not back:
            for sign in (-1,1):
                disk(c,sign*10,-113,4,4,self.fire,.7)
        if spin or slam:
            radial_glow(c,0,-82,65,self.fire.base,.14*max(spin,slam))
        c.restore()


class Dragonfly(Insect):
    name="dragonfly_skirmisher"
    FW=FH=288; OX=144; OY=248
    ANIMS={
        'idle':(12,14,True,-1),'move':(16,21,True,-1),
        'attack':(13,20,False,7),'cast':(16,20,False,10),
        'hurt':(7,15,False,-1),'death':(14,11,False,-1)
    }
    def __init__(self):
        self.midnight=Pal('#344a5e','#233145','#67889b','#202739')
        self.lapis=Pal('#547f9e','#36546e','#86bbcb','#223d58')
        self.glass=Pal('#a4c4d2','#6b98ab','#f5fbf1','#547a91')
        self.amber=Pal('#bd745b','#824c4c','#eead82','#502f40')
        self.neon=Pal('#63c9bd','#449c9f','#d6fff1','#2c687e')
    def body(self,c,v,p):
        side=v=='side';back=v=='up';g=p['step'] if p['mode']=='move' else p['flutter']*.12
        flap=p['flutter'];slash=p['swing'];dash=p['spell']
        c.save();c.translate(0,-17-3*g-5*dash)
        # Dragonfly: longest tail of the entire insect set, nine telescopic
        # segments below a relatively tiny thorax and very wide four wings.
        tailx=10 if side else 0
        for j in range(9):
            y=-77+j*10
            bend=math.sin(j*.65+g)*2.8
            x=tailx+j*.9+bend+slash*j*.4
            disk(c,x,y,6.5-j*.37,7.1,self.lapis if j%2 else self.midnight,.7)
            disk(c,x,y+2,1.3,1.8,self.neon,.2)
            if j:
                vein(c,[(x-3,y-5),(x+4,y-5)],self.glass.light,.9,.75)
        poly(c,[(tailx+2,5),(tailx+8,17),
                (tailx,22),(tailx-7,17)],self.amber,1.4,.6)
        # Four long, independent iridescent wings in an X formation.
        for wing_index in range(2):
            for sign in (-1,1):
                wing_root=(sign*(7+wing_index*3),-120)
                far=sign*(94+16*wing_index+7*flap)
                y=-170+30*wing_index-5*flap
                poly(c,[wing_root,(sign*40,-146+wing_index*17),
                        (far,y),(far+sign*14,y+12),
                        (sign*41,-105+wing_index*9)],self.glass,1.8,1,.75)
                for k in range(4):
                    vein(c,[wing_root,
                            (sign*(35+11*k),-136+wing_index*18-k*3),
                            (far,y+4+k*2)],self.lapis.light,.8,.66)
                for k in range(3):
                    x=sign*(39+k*15)
                    vein(c,[(x,-130+wing_index*10),
                            (x+sign*10,-121+wing_index*11)],self.midnight.light,.6,.45)
        for pair in range(3):
            for sign in (-1,1):
                x=sign*(9+pair*3)
                q=g*sign*(-1 if pair%2 else 1)
                path_joint(c,[(x,-110+pair*6),
                              (x+sign*15,-89+pair*5+q*2),
                              (x+sign*(19+q*4),-67+pair*4)],self.midnight,1.9)
        # Wide compound spherical head on narrow cervical hinge, long tail.
        disk(c,0,-125,13,24,self.midnight,2.0)
        disk(c,0,-143,23,20,self.lapis,2.9)
        for sign in (-1,1):
            disk(c,sign*16,-144,10,12,self.neon,1)
            for i in range(3):
                for j in range(3):
                    disk(c,sign*16-4+i*3,-148+j*3,1.2,1.2,self.midnight,.2)
            vein(c,[(sign*5,-154),(sign*14,-170),
                    (sign*19+flap,-176)],self.amber.light,1.3,.8)
        if back:
            poly(c,[(-9,-148),(0,-158),(9,-148),
                    (0,-137)],self.midnight,1.0,.55)
        else:
            poly(c,[(-7,-132),(0,-130),(7,-132),
                    (0,-123-slash*9)],self.amber,1.1,.75)
        # Precise streaks during skill-frame zigzag.
        if dash:
            for sign in (-1,1):
                for k in range(4):
                    y=-84-k*16
                    vein(c,[(sign*(28+k*4),y),
                            (sign*(54+k*5+dash*12),y+8)],
                         self.neon.light,1.7*dash,.7*dash)
            radial_glow(c,0,-112,33,self.neon.base,.3*dash)
        c.restore()

CREATURES_B={cls.name:cls() for cls in (AntGuard,RoachPlague,SpikeBeetle,Dragonfly)}
