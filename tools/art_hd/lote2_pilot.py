"""Production sprites for the first three Lote 2 insectoid enemies.

Uses THE GAME'S Cairo/Pal/paint/sheet pipeline, not image prompts or concept art.
Every species draws its own body plan; 3 facing directions x 6 actionable states.
Output Resources/Sprites/Demons/<id>.png + <id>.json consumed by Unity Sheets.
"""
from __future__ import annotations
import math
from pathlib import Path
from PIL import Image, ImageDraw
from core import Pal, paint, ellipse, smooth_poly, stroke, radial_glow, hx
from sheet import build

PI=math.pi
TAU=math.tau
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'docs/asset_catalog/previews'

STATES={
 'idle':(8,11,True,-1),
 'move':(12,14,True,-1),
 'attack':(12,16,False,6),
 'cast':(14,14,False,8),
 'hurt':(6,14,False,-1),
 'death':(12,12,False,-1)
}
DIRECTIONS=('down','up','side')
CREATURES={
 'mantis_reaver':{'shell':Pal('#536447','#39483d','#8a9b63','#24352f'),
   'bone':Pal('#b3a074','#77684c','#eddfa1','#493c36'),
   'glow':Pal('#ec5b45','#b62c3f','#ffb76f','#792235'),'role':'scythe'},
 'scarab_brute':{'shell':Pal('#3f5970','#2b3c58','#779eb0','#1b2b3b'),
   'bone':Pal('#9e815b','#5e4b47','#dcc9a0','#393145'),
   'glow':Pal('#e39b46','#ad563a','#ffe394','#69352e'),'role':'tank'},
 'moth_hexer':{'shell':Pal('#65527b','#483952','#a588bd','#2a233c'),
   'bone':Pal('#c5b7aa','#998b9d','#fff2e3','#65546c'),
   'glow':Pal('#74cecf','#376e9b','#c6ffff','#224c6f'),'role':'caster'}
}

def poly(c,pts,pal,shadow=2.6,highlight=1.2,width=1.25):
    paint(c,lambda p:smooth_poly(p,pts,tension=.25),pal,sh=shadow,hl=highlight,line=width)

def oval(c,x,y,rx,ry,pal,w=1.05):
    paint(c,lambda p:ellipse(p,x,y,rx,ry),pal,sh=1.65,hl=1.0,line=w)

def ln(c,pts,pal,w=3):
    stroke(c,lambda p:(p.move_to(*pts[0]),*[p.line_to(*q) for q in pts[1:]]),pal.line,w+1.6)
    stroke(c,lambda p:(p.move_to(*pts[0]),*[p.line_to(*q) for q in pts[1:]]),pal.base,w)

def mantis(c,p,m):
    sh,bo,gl=m['shell'],m['bone'],m['glow']
    v,g,a,s=p['view'],p['gait'],p['attack'],p['skill']
    side=v=='side'; back=v=='up'
    # Rear abdomen / flight covers (behind limbs) and biological leaf texture.
    poly(c,[(-18,-46),(-28,-22),(-15,-2),(0,8),(17,-6),(29,-26),(15,-48)],sh,3.5,1.4)
    for sx in (-1,1):
        poly(c,[(sx*7,-45),(sx*26,-28),(sx*19,-10),(sx*5,-19)],bo,1.1,.6,.8)
        # Mechanical insect hind legs have reverse-angle knees.
        x=sx*(11 if not side else 9)
        step=g*9*sx
        ln(c,[(x,-42),(x+sx*21+step,-23),(x+sx*12+step,-3)],bo,5.5)
        oval(c,x+sx*21+step,-23,5.2,5.0,sh)
        poly(c,[(x+sx*(12)+step,-3),(x+sx*(23)+step,-2),(x+sx*(26)+step,2),(x+sx*(9)+step,2)],sh,1,.65)
    # Small vestigial wings, no reused humanoid proportions.
    if not side:
        for sx in (-1,1):
            poly(c,[(sx*9,-82),(sx*31,-75-p['flap']*5),(sx*27,-42),(sx*6,-58)],sh,1.3,.8)
    poly(c,[(-12,-85),(-4,-93),(9,-88),(15,-62),(12,-35),(0,-28),(-13,-39),(-15,-63)],sh,3.4,1.8)
    for j in range(4):
        y=-75+j*10
        poly(c,[(-9,y),(0,y-4),(10,y),(7,y+5),(0,y+8),(-8,y+4)],bo,1.2,.8,.7)
    # Two organic scythe arms: attack sweeps independent from gait/idle.
    for sx in (-1,1):
        reach=(17+32*a)*sx
        x=sx*(16+10*s)
        shoulder=(x,-79)
        elbow=(sx*(33+10*a),-62+15*a)
        wrist=(reach,-38+24*a)
        ln(c,[shoulder,elbow,wrist],sh,7.2)
        oval(c,*elbow,5.0,5.2,bo)
        tip=(sx*(64+12*a),-90+60*a)
        blade=[(wrist[0],wrist[1]),(sx*(53+7*a),-58+31*a),tip,
               (sx*(50+7*a),-71+46*a),(sx*(41+13*a),-47+25*a)]
        poly(c,blade,bo,2.8,1.5)
        poly(c,[blade[0],blade[1],blade[2],(sx*(53+5*a),-61+41*a)],gl,1,.6,.5)
    if back:
        poly(c,[(-20,-108),(0,-119),(20,-108),(8,-91),(-7,-93)],sh,2,.8)
    else:
        poly(c,[(-19,-105),(-3,-117),(21,-104),(10,-87),(-12,-86)],bo,3.0,1.5)
        for sx in (-1,1):oval(c,sx*(9 if not side else 8),-104,3.7,4.5,gl)
        poly(c,[(-5,-94),(1,-84),(8,-95)],sh,1,.4)
    for sx in (-1,1):
        ln(c,[(sx*9,-112),(sx*12,-128+p['flap']*2),(sx*28,-139)],bo,1.5)
    if s>0:
        radial_glow(c,0,-65,32,hx('#ff653d'),.4*s)
        for sx in (-1,1):
            ln(c,[(sx*36,-62),(sx*63,-63-20*s)],gl,2.2)

def scarab(c,p,m):
    sh,bo,gl=m['shell'],m['bone'],m['glow']
    v,g,a,s=p['view'],p['gait'],p['attack'],p['skill']
    side=v=='side'; back=v=='up'
    # Six independent legs, heavily jointed, driven by opposing gait phase.
    for sx in (-1,1):
        for i in range(3):
            cy=-58+i*23
            step=math.sin(i*2.1+g*1.8)*8
            x=sx*(42 if not side else 35)
            ln(c,[(sx*29,cy),(x+sx*12,cy+9+step),(x+sx*19,cy+29+step)],bo,7.0)
            oval(c,x+sx*12,cy+9+step,6,6,sh)
            poly(c,[(x+sx*16,cy+24+step),(x+sx*25,cy+30+step),(x+sx*21,cy+36+step)],bo,1,.7)
    # Chest lower plates distinct from domed upper elytra.
    poly(c,[(-31,-70),(0,-85),(31,-70),(36,-27),(20,-5),(-19,-5),(-36,-27)],bo,3.6,1.5)
    for i in range(4):
        yy=-47+i*10
        poly(c,[(-27,yy),(0,yy-5),(27,yy),(24,yy+8),(0,yy+12),(-24,yy+8)],sh,1.3,.7,.6)
    # Pronounced shield dome, NOT humanoid torso.
    dome_y=-83+10*a
    poly(c,[(-46,dome_y+15),(-49,dome_y-20),(-30,dome_y-48),(0,dome_y-57),
           (31,dome_y-48),(49,dome_y-20),(46,dome_y+15),(20,dome_y+29),(-21,dome_y+29)],sh,5,2)
    for sx in (-1,1):
        poly(c,[(0,dome_y-48),(sx*23,dome_y-42),(sx*40,dome_y-13),
                (sx*31,dome_y+13),(sx*3,dome_y+21)],bo,2,.9,.7)
        for j in range(3):
            y=dome_y-31+j*14
            oval(c,sx*(12+j*7),y,2.1,2.8,gl,.5)
    # Head projects in FRONT of shell only for down/side.
    if not back:
        oval(c,0,-93+10*a,22,22,bo,1.5)
        for sx in (-1,1):
            oval(c,sx*11,-98+10*a,4.4,3.8,gl)
            poly(c,[(sx*12,-86+10*a),(sx*23,-76+10*a),(sx*7,-82+10*a)],sh,1,.6)
    # Beetle's own bifurcated horn, horn-strike rears forward on attack.
    for sx in (-1,1):
        poly(c,[(sx*7,-111+10*a),(sx*13,-141+12*a),
                (sx*24,-145+15*a),(sx*19,-129+14*a),(sx*10,-122+10*a)],bo,2.5,1.1)
    if s:
        for r in (20,38,54):
            stroke(c,lambda q,r=r:q.arc(0,-30,r,0,TAU),gl.base,2,s*.58)
        radial_glow(c,0,-35,50,hx('#ffd06b'),s*.32)

def moth(c,p,m):
    sh,bo,gl=m['shell'],m['bone'],m['glow']
    v,g,a,s=p['view'],p['gait'],p['attack'],p['skill']
    side=v=='side'; back=v=='up'
    spread=1+.20*p['flap']+.21*s
    # Giant wing-panels are the BODY silhouette; narrow hovering core, not a biped.
    for sx in (-1,1):
        tip=sx*75*spread
        poly(c,[(sx*10,-97),(sx*44,-128),(tip,-100),
                (sx*66,-65),(sx*88*spread,-33),
                (sx*58,-7),(sx*32,-28),(sx*15,-55)],sh,4.2,2.2)
        poly(c,[(sx*20,-86),(sx*47,-110),(sx*64*spread,-83),
                (sx*47,-50),(sx*70,-24),(sx*29,-38)],bo,2,.8,.9)
        for j in range(5):
            theta=j*.62+.1
            x=sx*(40+math.sin(theta)*18)*spread
            y=-78+math.cos(theta)*32
            oval(c,x,y,5+j%2*2,7,gl,.5)
        for j in range(4):
            ln(c,[(sx*15,-72),(sx*(44+j*7)*spread,-96+j*17)],sh,1.2)
    # Two antennae resemble combs; distinct from mantis thin whip antennae.
    for sx in (-1,1):
        ln(c,[(sx*8,-114),(sx*19,-130),(sx*30,-136)],bo,2.4)
        for i in range(5):
            x=sx*(17+i*3)
            y=-126-i*2
            ln(c,[(x,y),(x+sx*7,y-6)],bo,1.2)
    # Flowing tapered thorax/abdomen with ritual banding.
    poly(c,[(-9,-109),(-17,-93),(-13,-57),(-5,-29),(0,-16),
            (6,-29),(15,-58),(17,-90),(9,-108)],sh,3.1,1.4)
    for i in range(5):
        y=-66+i*10
        poly(c,[(-9,y),(0,y-4),(9,y),(8,y+4),(0,y+8),(-8,y+4)],bo,1,.7,.5)
    for sx in (-1,1):
        # Delicate claw-arms separate from wing shapes
        j=sx*(12+8*a)
        ln(c,[(sx*9,-88),(j,-69+8*a),(sx*25,-51+12*a)],bo,2.8)
        oval(c,sx*25,-50+12*a,3.4,4,gl,.6)
    oval(c,0,-113,15,18,bo,1.3)
    if not back:
        for sx in (-1,1):oval(c,sx*6,-113,5,5,gl)
        poly(c,[(-5,-104),(0,-96),(5,-104)],sh,1,.4)
    if s:
        radial_glow(c,0,-76,52,hx('#86eaf2'),s*.42)
        for j in range(7):
            a0=TAU*j/7+p['t']*TAU
            x=math.cos(a0)*58;y=-72+math.sin(a0)*42
            oval(c,x,y,2.1+s*1.8,2.1+s*1.8,gl,.5)

def draw(c,payload):
    name,stage,t,direction=payload
    mats=CREATURES[name]
    loop=stage in ('idle','move')
    gait=math.sin(t*TAU*1.4) if loop else 0
    fl=math.sin(t*TAU*2)
    attack=math.sin(t*PI) if stage=='attack' else 0.
    skill=math.sin(t*PI) if stage=='cast' else 0.
    pain=math.sin(t*PI) if stage=='hurt' else 0.
    death=t if stage=='death' else 0.
    p=dict(gait=gait,flap=fl,attack=attack,skill=skill,
           view=direction,t=t)
    c.save()
    c.translate(0,(-3 if stage=='move' else -1)*math.sin(t*TAU)+death*34)
    c.rotate(math.radians(-9*pain+death*42+(8*attack if name=='mantis_reaver' else 0)))
    c.scale(1,1-.56*death)
    if name=='mantis_reaver':mantis(c,p,mats)
    elif name=='scarab_brute':scarab(c,p,mats)
    else:moth(c,p,mats)
    c.restore()

def preview(name,image,meta):
    OUT.mkdir(parents=True,exist_ok=True)
    fw,fh,cols=meta['frameW'],meta['frameH'],meta['cols']
    sw,sh=fw*3,fh*4
    sheet=Image.new('RGB',(sw,sh+32),(23,22,35))
    d=ImageDraw.Draw(sheet)
    d.text((9,10),name+' | sprite frames - NOT a Unity screenshot',fill=(236,216,170))
    for row,an in enumerate(('idle','move','attack','cast')):
        for col,direction in enumerate(DIRECTIONS):
            entry=next(x for x in meta['anims'] if x['name']==an+'_'+direction)
            idx=entry['start']+ (entry['count']//2 if an in ('attack','cast') else 1)
            frame=image.crop(((idx%cols)*fw,(idx//cols)*fh,((idx%cols)+1)*fw,((idx//cols)+1)*fh))
            bg=Image.new('RGBA',(fw,fh),(37,34,52,255))
            bg.alpha_composite(frame)
            sheet.paste(bg.convert('RGB'),(col*fw,row*fh+32))
    sheet.save(OUT/(name+'.png'),optimize=True)

def main():
    for name in CREATURES:
        jobs=[]
        for stage,(count,fps,loop,hit) in STATES.items():
            for direction in DIRECTIONS:
                payloads=[(name,stage,i/count if loop else i/max(1,count-1),direction) for i in range(count)]
                jobs.append((stage+'_'+direction,payloads,fps,loop,hit))
        image,meta,_=build(name,'Demons',192,192,96,169,jobs,draw,outline=1.3)
        preview(name,image,meta)
        print(name,'rendered',sum(x['count'] for x in meta['anims']),'frames,',len(meta['anims']),'tracks')
if __name__=='__main__':
    main()
