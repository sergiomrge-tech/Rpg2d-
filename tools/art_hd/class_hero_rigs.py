"""Original in-game HD cartoon class rigs, compatible with the Godot animator.

Uses precisely the existing Aetheria Cairo renderer (Look, painted
materials, heroic anatomy, pose curves). This is source for REAL PNG
animation atlases, NOT standalone concept art or AI mockups.
The original Sprites/Chars/hero.png is never overwritten.
"""
from __future__ import annotations

import math
from core import Pal, paint, flat, stroke, ellipse, capsule, smooth_poly, radial_glow, hx
from humanoid import Look, draw_figure, vec, add, rot, TH, UA, FA, TORSO
from anims import pose as hero_pose

TAU = math.tau
PI = math.pi
IDS = ("warrior", "mage", "archer", "paladin", "assassin", "summoner")


def _poly(ctx, pts, pal, sh=1.2, hl=.7, alpha=1):
    ctx.save()
    ctx.push_group()
    paint(ctx, lambda c: smooth_poly(c, pts, tension=.26), pal, sh=sh, hl=hl)
    ctx.pop_group_to_source()
    ctx.paint_with_alpha(alpha)
    ctx.restore()


def _line(ctx, pts, col, width=1.0, alpha=.8):
    def path(c):
        c.move_to(*pts[0])
        for xy in pts[1:]:
            c.line_to(*xy)
    stroke(ctx, path, col, width, alpha)


def _pal(code):
    return Pal(*code)


# The same hero's face/hair remain recognisable through every outfit.
COLORS = {
    "warrior": dict(tunic=_pal(("#576c85","#344760","#8c9eb0","#233348")),
                    pants=_pal(("#494654","#2e2d40","#827784","#211e2d")),
                    metal=_pal(("#d5b47c","#977748","#ffe0a8","#554331")),
                    scarf=_pal(("#bd4b3d","#832d2b","#ed8868","#5c252a")),
                    blade=_pal(("#d8e4f1","#869cb5","#ffffff","#40516b"))),
    "mage": dict(tunic=_pal(("#4f6bb5","#303f87","#96baf2","#212958")),
                 pants=_pal(("#343d6f","#232b54","#626cab","#191e3d")),
                 metal=_pal(("#9fc7ee","#6086c3","#e2f9ff","#345883")),
                 scarf=_pal(("#b1c9ff","#6a82bc","#e9f0ff","#3e5a96"))),
    "archer": dict(tunic=_pal(("#467e64","#2a583f","#8dc6a0","#1d3e34")),
                   pants=_pal(("#57513f","#36362d","#877e61","#2c2928")),
                   metal=_pal(("#c9ad71","#927a44","#f5e0a6","#534936")),
                   scarf=_pal(("#b1ad75","#727a4f","#ebdfaa","#45482d"))),
    "paladin": dict(tunic=_pal(("#ded5c0","#9d9385","#fff6df","#635344")),
                    pants=_pal(("#5a667e","#374358","#aab7c5","#292f42")),
                    metal=_pal(("#e8c65d","#aa833b","#fff1ad","#5b432b")),
                    scarf=_pal(("#b58a42","#8f662e","#ffe19a","#533b23")),
                    blade=_pal(("#e1eaf1","#aeb9c6","#fffdf0","#6c7285"))),
    "assassin": dict(tunic=_pal(("#45425e","#2a2944","#716c8d","#191c2c")),
                     pants=_pal(("#252d40","#1c2235","#4c526a","#171a28")),
                     metal=_pal(("#ab82bb","#765185","#e0bfea","#483350")),
                     scarf=_pal(("#703f72","#4e2d59","#b97fb4","#2c1d3e")),
                     blade=_pal(("#ced5ea","#8794b5","#eafaff","#485471"))),
    "summoner": dict(tunic=_pal(("#477b80","#2b5663","#95ced1","#20404a")),
                     pants=_pal(("#2a4156","#243045","#638b91","#1b2e3a")),
                     metal=_pal(("#b1d5bb","#73ad9f","#e4ffe9","#395d67")),
                     scarf=_pal(("#8a7ab5","#544d8c","#cfcbf1","#3c3261"))),
}


def _dagger(ctx, look, hand, ang, scale=1.0):
    """Carved short dagger, distinct from the long sword weapon geometry."""
    ctx.save()
    ctx.translate(*hand)
    ctx.rotate(math.radians(-ang))
    ctx.scale(.94, max(.75,scale))
    _poly(ctx,[(-2,2),(-3,10),(-2.2,16),(0,22.4),(2.6,16),(3,10),(2,2)],look.blade,1.0,.8)
    _line(ctx,[(-.15,4),(0,17)],look.blade.light,.85,.9)
    _poly(ctx,[(-6,0),(-2,3),(2,3),(6,0),(3,-2),(-3,-2)],look.metal,.7,.4)
    _poly(ctx,[(-2,-1),(2,-1),(2,-9),(-2,-9)],look.glove,.65,.35)
    paint(ctx,lambda c: ellipse(c,0,-9.2,2.6,2.6),look.metal,sh=.4,hl=.2)
    ctx.restore()


def _bow(ctx, look, hand, ang, scale=1.0):
    """Three-layer laminated recurved bow and bowstring (not a reskinned sword)."""
    ctx.save()
    ctx.translate(*hand)
    ctx.rotate(math.radians(-ang))
    ctx.scale(1.1, max(.9,scale))
    wood=Pal("#9e744d","#71492e","#d8b285","#4b3028")
    brass=look.metal
    # Asymmetric string and recurve limbs, inset carved wood grooves.
    def bow(c):
        c.move_to(0,-31)
        c.curve_to(12,-19,16,-10,10,0)
        c.curve_to(16,10,12,19,0,31)
    stroke(ctx,bow,wood.line,6.4,.94)
    stroke(ctx,bow,wood.base,4.0)
    stroke(ctx,bow,wood.light,1.6,.9)
    _line(ctx,[(0,-31),(-1,0),(0,31)],hx("#e9dfc0"),.95,.9)
    for y in (-29,29):
        _poly(ctx,[(-3,y-2),(4,y-3),(4,y+2),(-3,y+3)],brass,.5,.3)
    _poly(ctx,[(7,-8),(12,-6),(12,6),(7,8),(5,2),(5,-2)],look.glove,.8,.45)
    ctx.restore()


def _mage_hat(ctx,view):
    hood=Pal("#3e559c","#28396d","#91a8e1","#1a2752")
    rim=Pal("#b4cfe3","#6d8daf","#f1fff7","#44608a")
    if view=="up":
        _poly(ctx,[(-22,-6),(-23,-23),(-9,-34),(8,-34),(22,-20),(23,9),(12,19),(0,22),(-12,19)],hood,2.2,1.0)
        _line(ctx,[(-12,0),(-2,15),(12,0)],rim.light,1.3,.7)
    elif view=="side":
        _poly(ctx,[(-18,-8),(-18,-24),(1,-34),(19,-21),(21,-7),(17,-2),(7,-13),(-3,-7),(-9,0)],hood,2,1.0)
        _line(ctx,[(-12,-17),(3,-29),(18,-17)],rim.light,1.3,.8)
    else:
        _poly(ctx,[(-23,-8),(-21,-23),(-7,-34),(7,-34),(21,-23),(23,-8),(16,-6),(8,-17),(0,-20),(-8,-17),(-16,-6)],hood,2.0,1.0)
        _line(ctx,[(-15,-13),(-7,-26),(0,-28),(7,-26),(15,-13)],rim.light,1.1,.8)
    for xx,yy in ((0,-30),):
        paint(ctx,lambda c,x=xx,y=yy:ellipse(c,x,y,2.6,2.8),rim,sh=.5,hl=.5)


def _assassin_hat(ctx,view):
    cloth=Pal("#2c3049","#1c2034","#626482","#111724")
    edge=hx("#b094c8")
    if view=="up":
        _poly(ctx,[(-24,-12),(-19,-27),(0,-35),(18,-28),(24,-12),(14,19),(-14,19)],cloth,1.5,.9)
    else:
        _poly(ctx,[(-23,-11),(-18,-30),(0,-38),(19,-30),(22,-11),(14,-7),(9,-16),(-10,-17),(-17,-7)],cloth,1.7,.9)
        _line(ctx,[(-18,-12),(-8,-21),(7,-21),(18,-12)],edge,1.5,.7)
        # Mask below eyes but above scarf, dark enough not to erase Ren's gaze.
        _poly(ctx,[(-14,10),(-8,8),(10,8),(15,10),(9,19),(-7,19)],cloth,1,.5,.85)


def _paladin_hat(ctx,view):
    helm=Pal("#e0d4bd","#a59b8d","#fff7e8","#67606b")
    gold=Pal("#ebc269","#ab8241","#fff1b0","#66502f")
    _poly(ctx,[(-22,-15),(-18,-26),(-8,-30),(9,-30),(18,-26),(23,-14),(16,-8),(11,-18),(0,-22),(-11,-18),(-16,-8)],helm,1.4,.9)
    _poly(ctx,[(-3,-38),(0,-43),(3,-38),(4,-25),(0,-20),(-4,-25)],gold,1,.6)
    if view=="up":
        _line(ctx,[(-17,-12),(0,-23),(18,-12)],gold.light,1.5,.9)


def _warrior_hat(ctx,view):
    steel=Pal("#67758a","#415066","#a5b7cb","#2c3949")
    _poly(ctx,[(-23,-7),(-22,-23),(-8,-31),(8,-31),(22,-23),(23,-7),(16,-9),(9,-20),(0,-21),(-9,-20),(-16,-9)],steel,1.6,1)
    if view!="up":_line(ctx,[(-17,-18),(0,-27),(16,-18)],steel.light,1.1,.9)


def _make_looks():
    result={}
    for id in IDS:
        L=Look(**COLORS[id])
        if id=="warrior":
            L.hat=_warrior_hat
        elif id=="mage":
            L.weapon=None
            L.hat=_mage_hat
            L.scarf_on=False
        elif id=="archer":
            L.weapon=_bow
            L.scarf_on=False
        elif id=="paladin":
            L.hat=_paladin_hat
        elif id=="assassin":
            L.weapon=_dagger
            L.hat=_assassin_hat
            L.scarf_on=False
        else:
            L.weapon=None
            L.scarf_on=False
        result[id]=L
    return result


LOOKS=_make_looks()


def _hands(P,view):
    shoulder=add((0,P["hip"]),rot(0,-TORSO+2.5,P["lean"]))
    sx=(-2.5 if view=="side" else 12 if view=="down" else -12)
    sh_a=add(shoulder,rot(sx,0,P["lean"]))
    a1,a2,sc1,sc2=P["arm_a"]
    return add(add(sh_a,vec(a1,UA*sc1)),vec(a2,FA*sc2))


def _update_class_pose(P,kind,anim,t,view):
    # No free-hand sword gesture on ranged/magic actions.
    if kind=="archer":
        if anim=="cast":
            p=math.sin(min(1,t)*PI)
            P["arm_b"]=(-42+44*p,-25+60*p,1,1) if view!="side" else (32+44*p,10+60*p,1,1)
            P["arm_a"]=(36-36*p,-35-40*p,1,1) if view!="side" else (-18,-10-25*p,1,1)
            P["wpn"]=(-11+4*p if view=="side" else 15+5*p)
            P["glow"]=None
        else:
            if anim in ("attack1","attack2","attack3"):
                P["wpn"]=(10 if view!="side" else 0)
            elif anim not in ("hurt","death","roll"):
                P["wpn"]=8 if view=="side" else 20
    if kind in ("mage","summoner"):
        P["wpn"]=None
        if anim=="cast":
            ph=math.sin(t*PI)
            P["arm_a"]=(-48-50*ph,-60-25*ph,1,1) if view=="side" else (64+20*ph,85+30*ph,1,1)
            P["arm_b"]=(48+38*ph,55+70*ph,1,1) if view=="side" else (-64-20*ph,-85-30*ph,1,1)
            P["glow"]=(.48,.92,.98,ph) if kind=="summoner" else (.49,.72,1.0,ph)
            P["glow_hand"]="b"
    if kind=="assassin":
        if anim.startswith("attack"):
            P["arm_a"]=tuple((-v if i<2 else v) for i,v in enumerate(P["arm_b"]))
        P["wpn"]=145 if anim=="cast" else P["wpn"]
    if kind=="paladin" and anim=="cast":
        P["wpn"]=None
        P["glow"]=(1.0,.87,.52,math.sin(PI*t))
        P["arm_a"]=(-55,-85,1,1) if view=="side" else (52,110,1,1)


def _frame_transform(ctx,P):
    ctx.translate(P["x"],P["y"])
    ctx.scale(1 / math.sqrt(P["sq"]),P["sq"])
    if P["rot"]:
        ctx.translate(0,P["hip"])
        ctx.rotate(math.radians(P["rot"]))
        ctx.translate(0,-P["hip"])


def _cape(ctx,kind,view,P):
    if kind not in ("mage","paladin","summoner","assassin"):
        return
    palette={
        "mage":Pal("#3b539c","#253b7a","#768cbd","#182757"),
        "paladin":Pal("#d8cbaf","#b7a483","#f0e1c5","#80745e"),
        "summoner":Pal("#305e66","#244751","#5ca0a1","#183847"),
        "assassin":Pal("#323247","#202337","#606076","#191c30"),
    }[kind]
    flow=math.sin(P["scarf"]*TAU+P["lean"]*.1)*4
    breadth=22 if kind=="mage" else 18
    xx=12 if view=="side" else 0
    _poly(ctx,[(-breadth+xx,-53),(breadth+xx,-53),
             (breadth+xx+flow*.5,-42),
             (breadth+10+flow+xx,8),(-breadth-12+flow+xx,9),
             (-breadth+xx,-42)],palette,2.4,1.3)
    for side in (-1,1):
        _line(ctx,[(xx+side*(breadth-4),-45),(xx+side*(breadth+4)+flow,4)],
              palette.light,1.4,.68)


def _finish_armor(ctx,kind,view,P,look):
    hip=(0,P["hip"])
    shoulder=add(hip,rot(0,-TORSO+2.5,P["lean"]))
    x,y=shoulder
    if kind in ("warrior","paladin"):
        armour=look.metal if kind=="paladin" else look.tunic
        for side in (-1,1):
            cx=x+(side*16 if view!="side" else side*6)
            _poly(ctx,[(cx-side*6,y-7),(cx+side*6,y-5),
                       (cx+side*10,y+5),(cx,y+10),(cx-side*7,y+3)],armour,1.1,.7)
            _line(ctx,[(cx-side*4,y-4),(cx+side*5,y)],armour.light,1.2,.8)
            if kind=="paladin":
                paint(ctx,lambda c,sx=cx: ellipse(c,sx,y+1,1.6,2.5),look.metal,sh=.5,hl=.5)
        # breastplate and inset crest
        _poly(ctx,[(-8,y+7),(0,y+4),(8,y+7),(7,y+19),(0,y+25),(-7,y+19)],
              look.tunic if kind=="paladin" else look.metal,1.4,.7,.85)
        if kind=="paladin":
            _line(ctx,[(-3,y+13),(3,y+13)],look.metal.light,1.8)
            _line(ctx,[(0,y+9),(0,y+20)],look.metal.light,1.8)
    elif kind=="archer":
        # Independent diagonal leather bow quiver; always on the back.
        qx=-17 if view=="side" else 17 if view=="up" else -19
        qy=y+13
        _poly(ctx,[(qx-7,qy-12),(qx+6,qy-14),(qx+7,qy+12),(qx-5,qy+13)],look.boots,1.1,.65)
        for k in range(4):
            _line(ctx,[(qx-4+k*3,qy-16),(qx-7+k*3,qy-29)],look.metal.light,.95,.8)
            _poly(ctx,[(qx-8+k*3,qy-28),(qx-5+k*3,qy-36),(qx-2+k*3,qy-28)],look.scarf,.6,.45)
        _line(ctx,[(qx-6,qy-8),(8,y+16)],look.belt.light,1.5,.8)
    elif kind=="mage":
        for sx in (-11,11):
            disk=look.metal
            paint(ctx,lambda c,v=sx:ellipse(c,v,y+7,3.2,3.2),disk,sh=.7,hl=.45)
        for off in (-1,1):
            _line(ctx,[(off*10,y+12),(off*14,y+34)],look.metal.light,1.1,.85)
    elif kind=="assassin":
        # Asymmetric belts and forearm blade-guards for dagger technique.
        _line(ctx,[(-16,y+19),(9,y+29)],look.metal.light,1.6,.8)
        _line(ctx,[(14,y+19),(-8,y+29)],look.glove.light,1.6,.85)
        hand_a=_hands(P,view)
        ang=-P.get("wpn",150) if view!="up" else 140
        _dagger(ctx,look,hand_a,ang,.96)
    elif kind=="summoner":
        # No weapon, only rotating small runic focus over the hands.
        phase=P["scarf"]*TAU
        for j in range(5):
            angle=j*TAU/5+phase*.2
            px=math.cos(angle)*18
            py=y+16+math.sin(angle)*7
            _poly(ctx,[(px,py-3),(px+2.8,py),(px,py+3),(px-2.8,py)],look.metal,.5,.4,.85)
        paint(ctx,lambda c:ellipse(c,0,y+15,5,5),look.metal,sh=1.0,hl=.9)
        if P.get("glow") is not None:
            radial_glow(ctx,0,y+15,21,look.metal.base,.33)


def draw(ctx,payload):
    """Render class-specific, rig-attached silhouette and equipment per frame."""
    kind,anim,t,view=payload
    look=LOOKS[kind]
    P=hero_pose(anim,t,view)
    _update_class_pose(P,kind,anim,t,view)
    ctx.save()
    _frame_transform(ctx,P)
    _cape(ctx,kind,view,P)
    ctx.restore()
    draw_figure(ctx,look,view,P)
    ctx.save()
    _frame_transform(ctx,P)
    _finish_armor(ctx,kind,view,P,look)
    ctx.restore()
