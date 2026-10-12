"""Original astral lynx familiar rig, animated in three directions.

The Summoner's real production ally, not the reused bog_wraith or
concept artwork. Quadruple hind/front paw gait, split spectral tails,
antler-ear crown, layered moonstone fur, bright rune chest, and spell
casts at animation hit frame. Same HD cartoon shading as the hero.
"""
from __future__ import annotations
import math
from core import Pal, paint, stroke, ellipse, smooth_poly, radial_glow, hx
from sheet import build
TAU=math.tau
PI=math.pi
FW,FH,OX,OY=192,176,96,151
VIEWS=("down","up","side")
ANIMS={
    "idle":(12,11,True,-1),
    "move":(16,16,True,-1),
    "attack":(13,17,False,8),
    "cast":(16,16,False,9),
    "hurt":(7,14,False,-1),
    "death":(16,11,False,-1),
}
FUR=Pal("#79a8a9","#486b84","#d2e8de","#34516b")
DARK=Pal("#354966","#25374e","#6984a0","#1a2c40")
GOLD=Pal("#d8ba86","#a58c6d","#fbebc0","#6c5a4a")
ENERGY=Pal("#75d9c9","#379caa","#dbfff2","#287582")
CRYSTAL=Pal("#9bc8d9","#6191ba","#f4f8fd","#516795")
PAW=Pal("#5d7e90","#3f5c74","#9eb1bf","#304758")


def poly(c,points,pal,sh=1.5,hl=.8,alpha=1):
    c.save();c.push_group()
    paint(c,lambda ctx:smooth_poly(ctx,points,tension=.26),pal,sh=sh,hl=hl)
    c.pop_group_to_source();c.paint_with_alpha(alpha);c.restore()


def joint(c,p1,p2,pal,width):
    paint(c,lambda ctx:ctx.arc(p1[0],p1[1],width*.52,0,TAU),pal,sh=.55,hl=.45)
    def p(ctx):
        ctx.move_to(*p1);ctx.line_to(*p2)
    stroke(c,p,pal.line,width+2,.8)
    stroke(c,p,pal.base,width)
    stroke(c,p,pal.light,width*.3,.7)


def dot(c,x,y,r,pal):
    paint(c,lambda ctx:ellipse(ctx,x,y,r,r*.83),pal,sh=.7,hl=.5)


def draw(c,data):
    action,t,view=data
    side=view=="side";back=view=="up"
    ph=t*TAU
    stride=math.sin(ph) if action=="move" else 0
    breath=math.sin(ph)*(1 if action=="idle" else .25)
    arc=math.sin(PI*t)
    cast=arc if action=="cast" else 0
    strike=arc if action=="attack" else 0
    fall=t if action=="death" else 0
    hurt=arc if action=="hurt" else 0
    # All organs pivot together. Death collapses naturally; idle floats.
    c.save()
    c.translate((2 if side else 0)+5*strike-4*hurt,(-2*breath if action=="idle" else -5*abs(stride) if action=="move" else 0)+13*fall)
    if fall:
        c.scale(1+.10*fall,max(.28,1-.62*fall))
    # Distinct two-pronged flame/ethereal tails, separately articulated.
    tail_anchor=(-21 if side else 0,-56)
    for sign in (-1,1):
        tail=sign if not side else -1+sign*.22
        wave=math.sin(ph+sign*PI*.6)*8+cast*7
        points=[(tail_anchor[0]+sign*8,-54),
                (tail_anchor[0]+tail*31,-67+wave*.2),
                (tail_anchor[0]+tail*(47+9*cast),-84+wave),
                (tail_anchor[0]+tail*(36+10*cast),-105+wave)]
        poly(c,[points[0],(points[1][0]+tail*8,points[1][1]+6),
                points[2],points[3],(points[2][0]-tail*11,points[2][1]+6),
                (points[1][0]-tail*12,points[1][1]+9)],DARK,2.1,1.2,.9)
        poly(c,[points[1],(points[2][0]-tail*6,points[2][1]+4),
                points[3],(points[2][0]-tail*8,points[2][1]+15)],ENERGY,.9,.5,.78)
        if cast:
            radial_glow(c,points[3][0],points[3][1],19,ENERGY.light,.24*cast)
    # Four legs, with alternate gait so the pet DOES NOT glide without feet.
    for pair in range(2):
        for sign in (-1,1):
            x=sign*(14+pair*9)
            vx=9 if side else 0
            phase=stride*(1 if pair else -1)*sign
            hip=(x+vx,-44-4*pair)
            knee=(x+sign*8+vx,-23-3*pair-8*phase)
            ankle=(x+sign*12+vx,-4-3*max(0,phase))
            joint(c,hip,knee,DARK if pair else FUR,7.0)
            joint(c,knee,ankle,PAW,5.2)
            poly(c,[(ankle[0]-7,ankle[1]-4),(ankle[0]+7,ankle[1]-4),
                    (ankle[0]+10,ankle[1]+1),(ankle[0]-10,ankle[1]+2)],PAW,1.4,.6)
            for k in (-1,0,1):
                dot(c,ankle[0]+k*4,ankle[1],.9,GOLD)
    # Feline chest wedge and sternum crystal, layered rather than flat recolor.
    bx=9 if side else 0
    poly(c,[(-34+bx,-47),(-31+bx,-71),(-19+bx,-82),
            (9+bx,-90),(28+bx,-71),(36+bx,-43),
            (23+bx,-29),(-21+bx,-29)],FUR,3.0,1.5)
    for sign in (-1,1):
        poly(c,[(bx+sign*14,-77),(bx+sign*29,-65),
                (bx+sign*21,-50),(bx+sign*9,-40)],DARK,1.0,.5,.7)
        for j in range(3):
            y=-47-j*11
            stroke(c,lambda ctx,s=sign,yy=y:(
                ctx.move_to(bx+s*11,yy),
                ctx.line_to(bx+s*(19+j*3),yy-7)),FUR.light,1.2,.6)
    # Moonstone heart with internal luminous cleavage.
    poly(c,[(bx,-71),(bx+8,-61),(bx+6,-45),
            (bx,-40),(bx-7,-49),(bx-8,-62)],CRYSTAL,1.6,1.2)
    poly(c,[(bx,-68),(bx+3,-58),(bx,-47),(bx-3,-58)],ENERGY,.7,.6)
    # Head: two long branching antler-ears; back faces away, not mirrored front.
    hx0=bx+(15 if side else 0)-5*hurt
    hy=-99-5*cast
    poly(c,[(hx0-19,hy+14),(hx0-23,hy-3),(hx0-13,hy-19),
            (hx0+13,hy-19),(hx0+23,hy-4),
            (hx0+18,hy+15),(hx0,hy+22)],DARK,2.3,1.25)
    poly(c,[(hx0-18,hy+3),(hx0-12,hy-15),(hx0,hy-21),
            (hx0+12,hy-14),(hx0+17,hy+3),
            (hx0+9,hy+11),(hx0-8,hy+11)],FUR,1.4,.8)
    for sign in (-1,1):
        # Crown horns shaped like lunar branches rather than generic long ears.
        poly(c,[(hx0+sign*12,hy-9),(hx0+sign*22,hy-37),
                (hx0+sign*37,hy-49),(hx0+sign*34,hy-36),
                (hx0+sign*39,hy-25),(hx0+sign*29,hy-29),
                (hx0+sign*17,hy-5)],GOLD,1.65,.9)
        stroke(c,lambda ctx,s=sign:(
            ctx.move_to(hx0+s*19,hy-11),
            ctx.line_to(hx0+s*29,hy-35),
            ctx.line_to(hx0+s*37,hy-48)),GOLD.light,1.0,.85)
        if not back:
            dot(c,hx0+sign*10,hy-2,4.7,ENERGY)
            dot(c,hx0+sign*11,hy-4,1.7,CRYSTAL)
    if back:
        for k in range(4):
            dot(c,hx0,hy-12+k*7,2.1,GOLD)
    else:
        poly(c,[(hx0-7,hy+11),(hx0,hy+18),
                (hx0+7,hy+11),(hx0,hy+7)],GOLD,.8,.3)
        if side:
            poly(c,[(hx0+14,hy+7),(hx0+26,hy+15),
                    (hx0+12,hy+20)],PAW,.9,.5)
    # Sparkle runes carved into the shoulders/crown.
    for sign in (-1,1):
        dot(c,bx+sign*23,-66,2.6,GOLD)
        stroke(c,lambda ctx,s=sign:(
            ctx.move_to(bx+s*21,-70),
            ctx.line_to(bx+s*26,-63)),GOLD.light,.9,.8)
    if cast:
        radial_glow(c,hx0,hy-6,38,ENERGY.light,.36*cast)
        for i in range(6):
            a=i*TAU/6+ph*.25
            x=hx0+math.cos(a)*(34+cast*10)
            y=hy+math.sin(a)*(25+cast*8)
            poly(c,[(x,y-4),(x+3,y),(x,y+4),(x-3,y)],CRYSTAL,.7,.5,.85)
    if strike:
        radial_glow(c,bx,hy+29,17,ENERGY.base,.28*strike)
    c.restore()


def build_spirit():
    jobs=[]
    for action,(n,fps,loop,hit) in ANIMS.items():
        for view in VIEWS:
            frames=[(action,i/n if loop else i/(n-1),view) for i in range(n)]
            jobs.append((action+"_"+view,frames,fps,loop,hit))
    return build("astral_lynx","Pets",FW,FH,OX,OY,jobs,draw,outline=1.1)
