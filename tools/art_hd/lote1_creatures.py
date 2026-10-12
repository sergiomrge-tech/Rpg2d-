"""Production HD cartoon creature variants for Lote 1 (10 demons + 5 bosses).

Uses existing Aetheria Cairo cel-shading and rigs, adds original gear/silhouettes.
NO Unity AI/spawns are registered here. No approved art is rewritten.
"""
from __future__ import annotations
import math
from core import Pal, paint, flat, stroke, ellipse, capsule, smooth_poly, hx, radial_glow, keys
from demons import Imp
from extra_demons import OniSoldier, Grakk, _armor, _horns
from humanoid import Look, draw_figure

PI=math.pi
TAU=2*PI


def shape(ctx,pts,pal,sh=1.7,hl=.8,line=1):
    paint(ctx,lambda c: smooth_poly(c,pts,tension=.25),pal,sh=sh,hl=hl,line=line)


def circle(ctx,x,y,rx,ry,pal):
    paint(ctx,lambda c:ellipse(c,x,y,rx,ry),pal,sh=.9,hl=.65,line=.85)


def beam(ctx,pts,pal,width=3):
    stroke(ctx,lambda c:(c.move_to(*pts[0]),*[c.line_to(*p) for p in pts[1:]]),pal.line,width+2)
    stroke(ctx,lambda c:(c.move_to(*pts[0]),*[c.line_to(*p) for p in pts[1:]]),pal.base,width)


class ImpVariant(Imp):
    FW,FH,OX,OY=160,160,80,142
    ANIMS={'idle':(10,11,True,-1),'move':(10,13,True,-1),
           'attack':(10,16,False,5),'cast':(12,14,False,7),
           'hurt':(5,14,False,-1),'death':(11,12,False,-1)}
    def __init__(self,kind):
        self.name=self.kind=kind
        tones={
          'imp_scout':('#ac3348','#ef7761','#594062','#bd5e83','#ffe077'),
          'imp_raider':('#89314c','#d76b69','#633653','#b95470','#ffc565'),
          'imp_pyro':('#b94b40','#ff9c65','#693552','#d37a66','#fff095'),
          'imp_hexer':('#6f365e','#a56b91','#43315e','#77528e','#8cf5c5'),
          'imp_bomber':('#a2474a','#e88a66','#604455','#b76875','#ffcd64'),
          'imp_howler':('#954057','#d16b7b','#5a4165','#a45283','#ccf8a4')}
        skin,belly,wing,mem,eye=tones[kind]
        self.skin=Pal(skin)
        self.belly=Pal(belly)
        self.wing=Pal(wing)
        self.membrane=Pal(mem)
        self.horn=Pal('#e8d6b6','#baa68e','#fff2d9','#5d4541')
        self.claw=Pal('#312637','#1f1424','#72576c','#150e21')
        self.eye=hx(eye)
        self.iron=Pal('#4a485e','#2d2c43','#8c869d','#1d1b30')
        self.ochre=Pal('#a67950','#71503c','#e4b780','#4d312a')
        self.magic=Pal(eye)

    def pose(self,anim,t,view):
        p=super().pose(anim,t,view)
        if anim=='cast' and self.kind=='imp_howler': p['mouth']='open';p['sq']+=.12*math.sin(t*PI)
        if anim=='move' and self.kind=='imp_scout': p['lean']*=1.5
        if anim=='cast' and self.kind=='imp_pyro':p['glow']=max(.2,p['glow'])
        return p

    def draw(self,ctx,view,p):
        super().draw(ctx,view,p)
        if p['alpha']<.05: return
        ctx.save()
        ctx.translate(p['x'],p['y']-46)
        ctx.rotate(math.radians(p['rot']+p['lean']))
        ctx.scale(1/math.sqrt(p['sq']),p['sq'])
        armx=14 if view=='side' else 12
        head=(-0 if view!='side' else 3,-16)
        if self.kind=='imp_scout':
            # unmistakable sideways forehead band, satchel and curved dagger
            shape(ctx,[(-10,-24),(0,-26),(10,-24),(8,-19),(-8,-19)],self.iron,.6,.4,.7)
            circle(ctx,0,-23,2.2,2.0,self.ochre)
            shape(ctx,[(-8,-4),(2,-9),(7,-4),(-2,0)],self.ochre)
            circle(ctx,-8,4,4,5,self.iron)
            beam(ctx,[(armx,1),(armx+6,14)],self.ochre,2.3)
            shape(ctx,[(armx+5,12),(armx+10,14),(armx+16,6),(armx+17,-2),(armx+12,1)],self.iron)
        elif self.kind=='imp_raider':
            shape(ctx,[(-11,-7),(-18,-14),(-25,-12),(-18,-2),(-10,2)],self.iron)
            shape(ctx,[(11,-6),(17,-14),(25,-12),(20,-1),(10,3)],self.iron)
            shape(ctx,[(-5,-23),(0,-19),(4,-23),(7,-14),(-8,-14)],self.ochre)
            beam(ctx,[(armx+1,3),(armx+15,14)],self.ochre,3)
            shape(ctx,[(armx+11,10),(armx+22,11),(armx+24,1),(armx+20,-5),(armx+18,7)],self.iron)
        elif self.kind=='imp_pyro':
            shape(ctx,[(-8,-7),(-3,-14),(3,-13),(8,-6),(3,1),(-3,1)],self.ochre)
            for sx in (-1,1):
                x=sx*19
                for q in range(3):
                    yy=-4+q*7
                    shape(ctx,[(x,yy+6),(x+sx*(4+q),yy),(x+sx*2,yy-9-q*2),(x-sx*4,yy)],
                          Pal('#ff8a44','#d34b36','#ffe9a2','#8a3d36'),1,.5,.4)
                radial_glow(ctx,x,-2,13,hx('#ffa342'),.48)
            circle(ctx,2,13,5,5,Pal('#ff8b38','#c94723','#fff1a4','#7d332e'))
        elif self.kind=='imp_hexer':
            # asymmetrical hood, long rune pendant, ritual rod and drifting glyphs
            shape(ctx,[(-16,-17),(-15,-30),(-5,-37),(8,-34),(15,-23),(10,-17),(5,-20),(-5,-18)],self.iron,2,.8)
            shape(ctx,[(-9,-4),(0,-8),(9,-4),(8,15),(-11,15)],self.iron)
            shape(ctx,[(-4,-3),(0,0),(4,-3),(0,-8)],self.magic,.6,.5,.6)
            beam(ctx,[(20,20),(19,-28)],self.ochre,2.2)
            circle(ctx,19,-30,5,5,self.magic)
            if p['glow']>.1:
                radial_glow(ctx,19,-30,24,self.magic.base,.7*p['glow'])
        elif self.kind=='imp_bomber':
            for sx in (-1,1):
                x=sx*16
                circle(ctx,x,-3,7,10,self.ochre)
                circle(ctx,x,5,6,6,self.iron)
                shape(ctx,[(x-2,-7),(x+2,-9),(x+4,-4),(x-2,-3)],self.iron,.3,.2)
            beam(ctx,[(-8,-8),(8,7)],self.ochre,3)
            circle(ctx,23,5,8,8,Pal('#333a52','#25263c','#68758d','#1d1e30'))
            beam(ctx,[(21,-1),(23,-8)],self.ochre,2)
            circle(ctx,23,-10,2.5,3,Pal('#ffcf77','#ef6f30','#ffffff','#ad4a2c'))
        elif self.kind=='imp_howler':
            for sx in (-1,1):
                for j in range(3):
                    x=sx*(9+j*4)
                    shape(ctx,[(x,4-j*5),(x+sx*7,-1-j*6),(x+sx*4,10-j*5)],self.iron,1,.5,.7)
            circle(ctx,0,-6,8,7,self.ochre)
            shape(ctx,[(-5,-11),(5,-11),(2,-1),(-2,-1)],self.magic,.3,.3,.5)
            if p['glow']>.1:
                for r in (18,25,31):
                    stroke(ctx,lambda c,r=r:c.arc(0,-3,r,0,TAU),self.magic.base,1.3,.45*p['glow'])
        ctx.restore()


class OniVariant(OniSoldier):
    FW,FH,OX,OY=224,224,112,194
    ANIMS={'idle':(10,10,True,-1),'move':(10,12,True,-1),
           'attack':(12,16,False,7),'cast':(13,15,False,8),
           'hurt':(5,14,False,-1),'death':(12,12,False,-1)}
    def __init__(self,kind):
        self.name=self.kind=kind
        colors={
          'oni_lancer':('#a47c88','#55536a','#bd996a'),
          'oni_shielder':('#8d7694','#3c495f','#b78a50'),
          'oni_executioner':('#8a667e','#50465c','#b2997c'),
          'morgash_ironhorn':('#b87779','#6b4352','#df8e60'),
          'krull_chainlord':('#8b9aa2','#3f435d','#7aa9aa')
        }
        skin,metal,gold=colors[kind]
        self.LOOK=Look(skin=Pal(skin),hair=Pal('#31293e'),
           eye=hx('#f69a6f') if kind!='krull_chainlord' else hx('#8beefa'),
           tunic=Pal(metal),shirt=Pal('#685c6e'),pants=Pal('#454051'),
           boots=Pal('#473741'),belt=Pal('#40313d'),metal=Pal(gold),
           glove=Pal('#4b3b4e'),scarf_on=False,weapon=None,hair_style='spiky')
        self.blade=Pal('#59637c','#353d56','#e5d2aa','#1c2337')
        self.trim=Pal(gold)
        self.glow=hx('#f8ad55') if kind!='krull_chainlord' else hx('#84eaff')
        if kind=='morgash_ironhorn':
            self.FW=self.FH=256;self.OX=128;self.OY=222
            self.ANIMS={'idle':(12,8,True,-1),'move':(12,11,True,-1),
                 'attack':(14,16,False,8),'cast':(16,14,False,10),
                 'hurt':(7,14,False,-1),'death':(16,12,False,-1),
                 'skill_2':(16,14,False,9)}
        elif kind=='krull_chainlord':
            self.FW=self.FH=256;self.OX=128;self.OY=224
            self.ANIMS={'idle':(12,10,True,-1),'move':(12,12,True,-1),
                 'attack':(14,16,False,8),'cast':(15,14,False,9),
                 'hurt':(6,14,False,-1),'death':(15,12,False,-1),
                 'skill_2':(17,16,False,10)}
    def pose(self,anim,t,view):
        base='cast' if anim=='skill_2' and self.kind=='krull_chainlord' else 'attack' if anim=='skill_2' else anim
        p=super().pose(base,t,view)
        if anim=='skill_2':
            p['lean']+=10*math.sin(2*PI*t)
            p['glow']=self.glow
        elif anim=='cast':p['glow']=self.glow
        if self.kind=='oni_executioner' and anim=='attack':p['lean']*=1.2
        return p
    def draw(self,ctx,view,p):
        ctx.save()
        size=1.55 if self.kind=='morgash_ironhorn' else 1.34 if self.kind=='krull_chainlord' else 1.22
        ctx.scale(size,size)
        body=draw_figure(ctx,self.LOOK,view,p)
        ctx.save()
        ctx.translate(p['x'],p['y'])
        if p['rot']:
            ctx.translate(0,p['hip']);ctx.rotate(math.radians(p['rot']));ctx.translate(0,-p['hip'])
        _armor(ctx,view)
        _horns(ctx,view)
        if self.kind=='oni_lancer':
            # winged lance, dramatically taller than the soldier club
            hand=body['hand']
            beam(ctx,[(hand[0]+3,hand[1]+17),(hand[0]+6,hand[1]-68)],self.trim,2.8)
            shape(ctx,[(hand[0]+6,hand[1]-85),(hand[0],hand[1]-68),
                       (hand[0]+6,hand[1]-52),(hand[0]+12,hand[1]-68)],self.blade)
            for sx in (-1,1):
                x=hand[0]+6+sx*12;y=hand[1]-57
                shape(ctx,[(hand[0]+6,hand[1]-62),(x,y),(x+sx*5,y-5),(x-sx*2,y+7)],self.blade)
        elif self.kind=='oni_shielder':
            hand=body['hand']
            beam(ctx,[(hand[0],hand[1]-10),(hand[0]+10,hand[1]-43)],self.blade,4)
            # raised shield clearly separate from the head and weapon
            x=-21 if view=='down' else 18 if view=='side' else -12
            y=-43
            shape(ctx,[(x-16,y-23),(x+16,y-23),(x+19,y+3),(x,y+32),(x-19,y+3)],self.blade,2,.9,1.6)
            shape(ctx,[(x-11,y-18),(x+11,y-18),(x+13,y+1),(x,y+23),(x-13,y+1)],self.trim,1.2,.5,.8)
            shape(ctx,[(x,y-16),(x+6,y),(x,y+17),(x-6,y)],self.blade,.5,.4,.5)
        elif self.kind=='oni_executioner':
            hand=body['hand'];hx0,hy=(38 if view!='side' else 34),hand[1]
            # Keep the huge blade clear of the face in front/side views.
            beam(ctx,[(hand[0],hy+12),(hx0+10,hy-50)],self.trim,4.6)
            for sx in (-1,1):
                x=hx0+10;y=hy-52
                shape(ctx,[(x,y-14),(x+sx*18,y-18),(x+sx*28,y-5),
                           (x+sx*22,y+13),(x,y+13)],self.blade,2.5,1.2)
        elif self.kind=='morgash_ironhorn':
            hand=body['hand'];x=(39 if view!='side' else 35);y=hand[1]-24
            # Raise the boss hammer outside the facial silhouette.
            beam(ctx,[(hand[0],hand[1]+14),(x+2,y-30)],self.trim,7)
            shape(ctx,[(x-18,y-22),(x+18,y-22),(x+24,y+13),(x-24,y+13)],self.blade,3,1.3,2)
            for off in (-12,0,12):
                circle(ctx,x+off,y-14,3,3,self.trim)
            radial_glow(ctx,x,y,14,self.glow,.4)
        elif self.kind=='krull_chainlord':
            # living chain trailing from wrist, eerie mask and blue gems
            for sx in (-1,1):
                start=(sx*12,-29)
                pts=[]
                for i in range(9):
                    y=-30+i*7
                    xx=start[0]+sx*(i*2+5*math.sin(i*.75+p['lean']*.03))
                    pts.append((xx,y))
                beam(ctx,pts,self.trim,2.3)
                for xx,yy in pts[::2]:
                    stroke(ctx,lambda c,xx=xx,yy=yy:c.arc(xx,yy,4,0,TAU),self.glow,1.4,.85)
            shape(ctx,[(-11,-91),(-7,-99),(7,-99),(12,-91),(8,-81),(-8,-81)],self.blade,2,1.3)
            for sx in (-1,1):
                circle(ctx,sx*6,-89,2.5,2,self.trim)
            radial_glow(ctx,0,-44,21,self.glow,.21)
        ctx.restore();ctx.restore()


class Velka:
    name='velka_flamebeak'
    FW,FH,OX,OY=256,224,128,197
    ANIMS={'idle':(12,12,True,-1),'move':(12,15,True,-1),
        'attack':(14,19,False,7),'cast':(16,15,False,10),
        'hurt':(7,14,False,-1),'death':(15,12,False,-1),
        'skill_2':(15,15,False,9)}
    def __init__(self):
        self.feather=Pal('#b74751','#853442','#ed7f65','#502137')
        self.ember=Pal('#e28c51','#bc503b','#ffe19b','#742e32')
        self.gold=Pal('#e1c5a0','#a78c6b','#fff8d9','#594739')
        self.iron=Pal('#534359','#352f47','#85667b','#241c32')
        self.eye=hx('#fff1a9')
    def pose(self,anim,t,view):
        mode= 'attack' if anim=='skill_2' else anim
        flap=math.sin(t*TAU*(2 if mode=='move' else 1.0))
        y=-4*math.sin(t*TAU) if mode in ('idle','move') else 0
        lean=0
        glow=0
        if mode=='attack':lean=17*math.sin(t*PI);y+=10*math.sin(t*PI)
        if mode=='cast':glow=math.sin(PI*t);y-=8*glow
        if anim=='skill_2':flap=math.sin(t*TAU*3);glow=math.sin(PI*t)
        if mode=='hurt':lean=-12*math.sin(t*PI)
        if mode=='death':y=25*t;lean=60*t
        return dict(y=y,lean=lean,flap=flap,glow=glow,tail=t,death=t if mode=='death' else 0)
    def draw(self,ctx,view,p):
        ctx.save();ctx.translate(0,p['y']-71);ctx.rotate(math.radians(p['lean']));ctx.scale(1.23,1.23)
        for sx in (-1,1):
            f=p['flap'];spread=1+.15*f
            tipx=sx*65*spread;tipy=-56-11*f
            # two feather layers per articulated wing, silhouette distinct from imp
            shape(ctx,[(sx*11,-20),(sx*32,-47),(tipx,tipy),
                (sx*56,-18),(sx*37,7),(sx*12,0)],self.feather,3,1.6)
            for i in range(4):
                xx=sx*(33+i*8)*spread;yy=-42+i*5-8*f
                shape(ctx,[(sx*23,-25),(xx,yy),(xx+sx*9,yy+17),(sx*24,-11)],self.ember,1.2,.6,.6)
                stroke(ctx,lambda c,xx=xx,yy=yy:c.move_to(xx,yy),self.gold.base,.4)
        for sx in (-1,1):
            shape(ctx,[(sx*8,13),(sx*15,21),(sx*10,36),(sx*17,41),(sx*6,32)],self.iron)
            for j in range(3):
                shape(ctx,[(sx*12,38),(sx*(15+j*4),42),(sx*(11+j*4),33)],self.gold,.8,.5)
        shape(ctx,[(-16,-20),(-12,-36),(0,-44),(13,-34),(17,-13),(10,19),(0,26),(-12,18)],self.feather,3,1.3)
        shape(ctx,[(-11,-5),(0,-12),(12,-5),(9,18),(0,26),(-9,17)],self.ember)
        for sx in (-1,1):
            shape(ctx,[(sx*9,-12),(sx*20,-7),(sx*14,10),(sx*18,14),(sx*8,4)],self.iron)
        # crowned narrow beaked head with ember eyes
        shape(ctx,[(-13,-37),(-12,-53),(0,-63),(13,-53),(14,-39),(9,-28),(-9,-28)],self.gold,2.3,1.1)
        for sx in (-1,1):
            shape(ctx,[(sx*3,-58),(sx*8,-72),(sx*12,-51)],self.feather)
        if view!='up':
            for sx in (-1,1):
                circle(ctx,sx*6,-43,2.7,3.5,self.ember)
            shape(ctx,[(-5,-34),(8,-32),(6,-24),(0,-21)],self.iron,1,.5)
        for sx in (-1,1):
            shape(ctx,[(sx*3,-25),(sx*13,-30),(sx*19,-22),(sx*12,-6)],self.feather)
        if p['glow']>.05:
            radial_glow(ctx,0,-23,35,self.ember.base,.6*p['glow'])
            for sx in (-1,1):radial_glow(ctx,sx*29,-18,18,self.ember.base,.28*p['glow'])
        ctx.restore()


class Thornmaw:
    name='thornmaw_alpha'
    FW,FH,OX,OY=288,256,144,214
    ANIMS={'idle':(12,9,True,-1),'move':(12,14,True,-1),
           'attack':(13,16,False,7),'cast':(15,14,False,9),
           'hurt':(7,14,False,-1),'death':(17,12,False,-1),
           'skill_2':(15,16,False,10)}
    def __init__(self):
        self.hide=Pal('#594050','#412b40','#936d77','#281c2e')
        self.bone=Pal('#c3b49b','#968c79','#fff0ca','#544c4e')
        self.iron=Pal('#534c59','#322c40','#988a97','#2b273b')
        self.glow=hx('#eb9d75')
    def pose(self,anim,t,view):
        mode='attack' if anim=='skill_2' else anim
        stride=math.sin(t*TAU*(1.2 if mode=='move' else .55))
        leap=7*math.sin(t*PI) if mode=='attack' else 0
        if anim=='skill_2':leap+=12*math.sin(PI*t)
        return dict(stride=stride,leap=leap,spines=math.sin(t*PI) if mode=='cast' else 0,
                    pain=math.sin(t*PI) if mode=='hurt' else 0,fall=t if mode=='death' else 0,mode=anim)
    def draw(self,ctx,view,p):
        ctx.save();ctx.translate(0,-60+p['leap']+p['fall']*33)
        ctx.scale(1.3,1.25-p['fall']*.35)
        side=view=='side'
        bodyc=(0,-10)
        # four articulated legs and heavy talons with offset gait
        for sx in (-1,1):
            for front in (False,True):
                ix= (20 if front else -24) if side else sx*(18 if front else 23)
                iy= 12 if front else 14
                swing=p['stride']*(1 if front else -1)*(1 if sx==1 else -1)
                legx=ix+swing*5
                shape(ctx,[(ix-8,4),(ix+7,4),(legx+10,34),(legx+6,48),(legx-8,48),(legx-10,34)],self.hide,2,.8)
                shape(ctx,[(legx-10,43),(legx+9,43),(legx+16,52),(legx-12,52)],self.bone)
                for j in range(3):
                    x=legx-8+j*8
                    shape(ctx,[(x,52),(x+5,52),(x+1,58)],self.iron,.7,.3)
        # muscular body
        shape(ctx,[(-44,-23),(-28,-41),(5,-44),(37,-29),(43,-5),(30,19),(-28,23),(-47,8)],self.hide,4,1.7)
        # overlapping plates, from hips to crown
        for j in range(4):
            x=-24+j*15
            shape(ctx,[(x-8,-37),(x+10,-39),(x+9,-12),(x-7,-10)],self.iron,1.8,.9)
        for j in range(7):
            x=-36+j*12
            yy=-43+3*math.sin(j*.8)
            shape(ctx,[(x-6,yy),(x+2,yy-18-4*math.sin(j)),(x+8,yy-2)],self.bone,1.2,.8)
        # forequarters raised and skull jaw
        headx=33 if side else 0
        heady=-28
        shape(ctx,[(headx-24,heady-10),(headx-15,heady-26),(headx+10,heady-24),
            (headx+27,heady-8),(headx+22,heady+9),(headx-20,heady+10)],self.hide,3,1.5)
        for sx in (-1,1):
            circle(ctx,headx+sx*12,heady-8,4,4,Pal('#f4a56f','#bc6759','#ffe6a8','#743747'))
        shape(ctx,[(headx-20,heady+5),(headx+20,heady+4),
             (headx+15,heady+20),(headx,heady+24),(headx-15,heady+19)],self.bone,1.4,.7)
        for sx in (-1,1):
            shape(ctx,[(headx+sx*11,heady+10),(headx+sx*17,heady+23),(headx+sx*3,heady+18)],self.iron,.8,.5)
        if p['spines']>.1:
            for j in range(4):
                x=-26+j*20
                radial_glow(ctx,x,-44,18,self.glow,.4*p['spines'])
        ctx.restore()



class GrakkFull(Grakk):
    """Add the missing second boss skill while preserving Grakk's existing rig/art."""
    ANIMS=dict(Grakk.ANIMS,skill_2=(13,16,False,8))

    def pose(self,anim,t,view):
        p=super().pose('cast' if anim=='skill_2' else anim,t,view)
        if anim=='skill_2':
            p['flap']=math.sin(t*TAU*3.1)
            p['glow']=max(p['glow'],math.sin(PI*t)*.95)
            p['y']-=7*math.sin(PI*t)
            p['arm_a']=(5+90*math.sin(PI*t),-60)
            p['arm_b']=(-5-90*math.sin(PI*t),60)
            p['boss_special']=math.sin(PI*t)
        return p

    def draw(self,ctx,view,p):
        super().draw(ctx,view,p)
        special=p.get('boss_special',0)
        if special<=0.02:
            return
        ctx.save()
        ctx.translate(p['x'],p['y']-46)
        ctx.scale(1.34,1.34)
        for r,alpha in ((31,.50),(43,.36),(53,.24)):
            stroke(ctx,lambda c,r=r:c.arc(0,1,r,0,TAU),
                   hx('#9df7ff'),1.5,alpha*special)
        radial_glow(ctx,0,0,38,hx('#66dcf5'),.30*special)
        for i in range(7):
            a=i*TAU/7+p['flap']*.11
            x=math.cos(a)*46;y=math.sin(a)*32
            shape(ctx,[(x-3,y),(x,y-9),(x+3,y),(x,y+7)],
                  Pal('#74d9eb','#328caa','#e8ffff','#23647a'),.6,.6,.5)
        ctx.restore()

def build_creatures():
    items={n:ImpVariant(n) for n in ('imp_scout','imp_raider','imp_pyro','imp_hexer','imp_bomber','imp_howler')}
    items.update({n:OniVariant(n) for n in ('oni_lancer','oni_shielder','oni_executioner','morgash_ironhorn','krull_chainlord')})
    items['grakk']=GrakkFull()
    items['velka_flamebeak']=Velka()
    items['thornmaw_alpha']=Thornmaw()
    return items