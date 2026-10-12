"""Create Aetheria's missing Unity HUD art without changing existing character art.

Produces RGBA overlays in unity/Assets/Resources/Sprites/Ui and a named icon
sprite sheet compatible with Aetheria.Sheets/Icons. Only Pillow is required.
Rerun from any working directory: python3 tools/art_hd/ui.py
"""
from __future__ import annotations

import json
import math
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter

ROOT = Path(__file__).resolve().parents[2]
SPRITES = ROOT / 'unity' / 'Assets' / 'Resources' / 'Sprites'
OUT = SPRITES / 'Ui'
S = 2
GOLD = (216, 173, 97)
LIGHT = (255, 227, 162)
DARK = (39, 25, 43)


def rgba(rgb, a=255):
    return tuple(rgb[:3]) + (int(a),)


def canvas(w, h):
    return Image.new('RGBA', (w * S, h * S), (0, 0, 0, 0))


def xy(box):
    return tuple(int(round(n * S)) for n in box)


def ellipse(d, box, fill=None, outline=None, width=1):
    d.ellipse(xy(box), fill=fill, outline=outline, width=max(1, round(width * S)))


def line(d, points, color, width=1, joint='curve'):
    d.line([(int(x * S), int(y * S)) for x, y in points], fill=color,
           width=max(1, round(width * S)), joint=joint)


def save(img, name):
    OUT.mkdir(parents=True, exist_ok=True)
    img.resize((img.width // S, img.height // S), Image.Resampling.LANCZOS).save(OUT / (name + '.png'), optimize=True)


def ring(name, color, track=False):
    w = h = 440
    im = canvas(w, h)
    d = ImageDraw.Draw(im)
    # Circular tracks; Unity's radial fill reveals precisely the active portion.
    r = {'hp': 209, 'mp': 181, 'st': 154}[name.split('_')[1]]
    thickness = {'hp': 17, 'mp': 13, 'st': 12}[name.split('_')[1]]
    c = (57, 43, 63) if track else color
    ellipse(d, (220-r-3, 220-r-3, 220+r+3, 220+r+3), None, rgba((13, 10, 22), 190), thickness+5)
    ellipse(d, (220-r, 220-r, 220+r, 220+r), None, rgba(c, 240 if not track else 200), thickness)
    ellipse(d, (220-r+2, 220-r+2, 220+r-2, 220+r-2), None,
            rgba(LIGHT if not track else GOLD, 170 if not track else 75), 2)
    if track:
        for i in range(36):
            a = i * math.tau / 36
            x, y = 220 + r * math.cos(a), 220 + r * math.sin(a)
            line(d, [(x-2*math.cos(a), y-2*math.sin(a)),(x+2*math.cos(a), y+2*math.sin(a))], rgba(GOLD, 115), 1.2)
    save(im, name)


def medallion():
    im = canvas(300, 300); d = ImageDraw.Draw(im)
    ellipse(d, (8,8,292,292), None, rgba((12,8,23), 230), 18)
    ellipse(d, (15,15,285,285), None, rgba(GOLD, 230), 13)
    ellipse(d, (23,23,277,277), None, rgba(LIGHT, 160), 2)
    ellipse(d, (30,30,270,270), None, rgba(DARK, 210), 4)
    for i in range(24):
        a = i * math.tau / 24
        x,y = 150 + 137*math.cos(a), 150+137*math.sin(a)
        ellipse(d, (x-2.3,y-2.3,x+2.3,y+2.3), rgba(LIGHT,210))
    for a in (0,90,180,270):
        t=math.radians(a)
        pts=[(150+rr*math.cos(t),150+rr*math.sin(t)) for rr in (131,143)]
        line(d,pts,rgba(LIGHT,250),5)
    save(im,'medallion')


def orb():
    im = canvas(144,144); d=ImageDraw.Draw(im)
    ellipse(d,(10,10,134,134),rgba((17,23,42),224),rgba((19,13,28),255),8)
    ellipse(d,(13,13,131,131),None,rgba(GOLD,245),7)
    ellipse(d,(21,21,123,123),None,rgba(LIGHT,165),2)
    ellipse(d,(30,30,114,114),None,rgba((94,127,156),80),2)
    for i in range(8):
        a = i*math.pi/4
        x,y = 72+58*math.cos(a),72+58*math.sin(a)
        ellipse(d,(x-3,y-3,x+3,y+3),rgba(LIGHT,240))
    save(im,'orb')
    shade=canvas(144,144);sd=ImageDraw.Draw(shade)
    ellipse(sd,(21,21,123,123),rgba((11,9,19),190))
    save(shade,'orb_shade')


def smear():
    w,h=620,420
    im=canvas(w,h)
    d=ImageDraw.Draw(im)
    ellipse(d,(46,42,w-46,h-42),rgba((14,10,22),170))
    im=im.filter(ImageFilter.GaussianBlur(40*S))
    save(im,'smear')


def flourish():
    im=canvas(560,64);d=ImageDraw.Draw(im)
    for sign in (-1,1):
        pts=[]
        for i in range(36):
            x=280+sign*(32+i*6.4)
            y=32+math.sin(i/35*math.pi*1.4)*10
            pts.append((x,y))
        line(d,pts,rgba(GOLD,210),2.5)
        for k in (60,117,177):
            x=280+sign*k
            ellipse(d,(x-4,24,x+4,32),rgba(LIGHT,185))
    d.polygon([(280*S,14*S),(296*S,32*S),(280*S,50*S),(264*S,32*S)],fill=rgba(GOLD,220))
    ellipse(d,(273,25,287,39),rgba(LIGHT,245))
    save(im,'flourish')


def pill(name):
    im=canvas(104,22);d=ImageDraw.Draw(im)
    if name=='pill_track':
        d.rounded_rectangle(xy((1,1,103,21)),radius=10*S,fill=rgba((23,15,35),230),outline=rgba(GOLD,240),width=2*S)
        d.rounded_rectangle(xy((6,6,98,16)),radius=5*S,fill=rgba((89,44,50),210))
    else:
        d.rounded_rectangle(xy((1,1,103,21)),radius=10*S,fill=rgba((177,45,59),255),outline=rgba((255,182,147),230),width=1*S)
        d.rounded_rectangle(xy((6,4,98,8)),radius=2*S,fill=rgba((255,202,156),145))
    save(im,name)


def nameplate():
    im=canvas(480,70);d=ImageDraw.Draw(im)
    d.rounded_rectangle(xy((24,8,456,62)),radius=16*S,fill=rgba((27,17,34),235),outline=rgba(GOLD,235),width=3*S)
    line(d,[(40,20),(440,20)],rgba(LIGHT,140),1.5)
    for x in (21,459):
        d.polygon([(int(x*S),int(35*S)),(int((x+12)*S),int(10*S)),(int((x+12)*S),int(60*S))],fill=rgba(GOLD,155))
    save(im,'nameplate')


def band():
    w,h=1920,380
    # Transparent gradient, not a rectangular frame.
    im=canvas(w,h)
    pix=im.load()
    for y in range(im.height):
        yf=y/im.height
        a=int(212*min(1,yf*3.5)*min(1,(1-yf)*5.0))
        for x in range(im.width):
            xf=x/im.width
            edge=max(0,1-abs(xf-.5)*.7)
            pix[x,y]=(18,12,31,int(a*edge))
    d=ImageDraw.Draw(im)
    for ys in (48,330):
        line(d,[(90,ys),(1830,ys)],rgba(GOLD,105),2)
        line(d,[(100,ys+4),(1820,ys+4)],rgba(LIGHT,65),1)
    save(im,'dialogue_band')


def vignette():
    w,h=1920,1080
    # RGBA color remains neutral: tint is controlled dynamically by Hud.HurtPulse.
    im=canvas(w,h)
    pixels=im.load()
    for y in range(im.height):
        yn=(y/im.height-.5)*2
        for x in range(im.width):
            xn=(x/im.width-.5)*2
            dist=math.sqrt(xn*xn*.72+yn*yn*.85)
            a=int(min(210,max(0,(dist-.42)/.75)*190))
            pixels[x,y]=(255,255,255,a)
    save(im,'vignette')


def icon(d, name):
    # Named icons share the existing HUD gold outline / coloured fill style.
    def L(pts,c=LIGHT,w=5): line(d,pts,rgba(c),w)
    def E(box,c=LIGHT,outline=None,w=2):ellipse(d,box,rgba(c),rgba(outline) if outline else None,w)
    if name in ('coin',):
        E((19,19,77,77),GOLD,DARK,4);E((26,26,70,70),(245,199,92),LIGHT,2)
        L([(40,31),(55,31),(63,40),(61,57),(49,65),(35,55),(35,43),(45,41),(54,47)],(130,81,37),3)
    elif name in ('skill_sword','sword'):
        L([(27,70),(67,20)],(24,21,43),11);L([(27,70),(67,20)],(214,218,226),7)
        L([(24,49),(46,68)],GOLD,8);L([(16,80),(29,68)],GOLD,7);E((12,76,25,89),LIGHT)
    elif name=='skill_spark':
        E((25,25,71,71),(55,152,246),LIGHT,4)
        L([(50,10),(43,38),(61,42),(42,81),(46,55),(28,52)],LIGHT,6)
        for x,y in ((16,22),(76,24),(18,72),(78,72)):
            E((x-3,y-3,x+3,y+3),(97,203,255))
    elif name=='skill_roll':
        d.arc(xy((14,14,82,82)),25,295,fill=rgba((143,215,240)),width=8*S)
        L([(69,21),(83,22),(79,38)],LIGHT,6)
        E((32,38,52,58),LIGHT,(31,44,68),2)
        L([(32,61),(63,66)],(150,203,227),6)
    elif name=='potion':
        d.rounded_rectangle(xy((31,28,65,76)),radius=10*S,fill=rgba((179,39,66)),outline=rgba(GOLD),width=4*S)
        d.rectangle(xy((40,18,56,30)),fill=rgba((231,199,137)),outline=rgba(DARK),width=2*S)
        L([(37,54),(59,54)],(255,156,156),4)
    elif name=='ether':
        d.rounded_rectangle(xy((31,28,65,76)),radius=10*S,fill=rgba((34,119,212)),outline=rgba(GOLD),width=4*S)
        d.rectangle(xy((40,18,56,30)),fill=rgba((231,199,137)))
        L([(39,57),(57,39)],LIGHT,5)
    elif name=='horn':
        d.polygon([(25*S,75*S),(30*S,36*S),(40*S,15*S),(49*S,44*S),(67*S,74*S)],fill=rgba((184,156,112)),outline=rgba(DARK),width=4*S)
        L([(30,67),(62,68)],LIGHT,4)
    elif name=='ember':
        d.polygon([(48*S,11*S),(65*S,38*S),(70*S,59*S),(58*S,78*S),(35*S,78*S),(24*S,58*S),(36*S,35*S)],fill=rgba((243,95,43)),outline=rgba(DARK),width=4*S)
        d.polygon([(48*S,37*S),(58*S,59*S),(50*S,70*S),(38*S,58*S)],fill=rgba(LIGHT))
    elif name=='tome':
        d.rounded_rectangle(xy((20,19,76,78)),radius=4*S,fill=rgba((82,39,119)),outline=rgba(GOLD),width=4*S)
        L([(29,23),(29,75)],LIGHT,3); E((40,35,62,57),LIGHT)
        L([(51,31),(51,63)],GOLD,3)


def icons():
    names=['coin','skill_sword','skill_spark','skill_roll','potion','ether','horn','ember','tome']
    size=96;cols=5;rows=math.ceil(len(names)/cols)
    atlas=Image.new('RGBA',(cols*size*S,rows*size*S),(0,0,0,0))
    animations=[]
    for i,name in enumerate(names):
        im=canvas(size,size)
        icon(ImageDraw.Draw(im),name)
        atlas.alpha_composite(im,((i%cols)*size*S,(i//cols)*size*S))
        animations.append(dict(name=name,start=i,count=1,fps=1,loop=True,hit=-1))
    save(atlas,'icons')
    meta=dict(frameW=size,frameH=size,pivotX=size//2,pivotY=size//2,cols=cols,anims=animations)
    (OUT/'icons.json').write_text(json.dumps(meta,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')


def portrait_from_sheet(name, origin):
    base = canvas(256,256)
    d=ImageDraw.Draw(base)
    ellipse(d,(9,9,247,247),rgba((31,30,48),255),rgba(GOLD,255),5)
    sheet = SPRITES / origin / (name+'.png')
    info = SPRITES / origin / (name+'.json')
    if not sheet.exists() or not info.exists():
        raise FileNotFoundError('Missing existing HD character art for portrait: '+str(sheet))
    meta=json.loads(info.read_text(encoding='utf-8'))
    fw,fh=meta['frameW'],meta['frameH']
    anim=next((a for a in meta['anims'] if a['name'] in ('idle_down','idle')),meta['anims'][0])
    k=anim['start']; cols=meta['cols']
    with Image.open(sheet) as atlas:
        frame=atlas.crop(((k%cols)*fw,(k//cols)*fh,(k%cols+1)*fw,(k//cols+1)*fh)).convert('RGBA')
    bbox=frame.getbbox()
    if bbox:
        frame=frame.crop(bbox)
        scale=min(176/frame.width,195/frame.height)
        frame=frame.resize((max(1,int(frame.width*scale*S)),max(1,int(frame.height*scale*S))),Image.Resampling.LANCZOS)
        at=(base.width//2-frame.width//2,base.height//2-frame.height//2+14*S)
        layer=Image.new('RGBA',base.size,(0,0,0,0));layer.alpha_composite(frame,at)
        mask=Image.new('L',base.size);ImageDraw.Draw(mask).ellipse(xy((22,22,234,234)),fill=255)
        layer.putalpha(Image.composite(layer.getchannel('A'),Image.new('L',base.size),mask))
        base.alpha_composite(layer)
    ellipse(ImageDraw.Draw(base),(12,12,244,244),None,rgba(LIGHT,200),2)
    save(base,'portrait_'+({'hero':'hero','guild_clerk':'receptionist','merchant':'blacksmith','villager':'villager'}[name]))


def main():
    for r,c in (('hp',(225,67,81)),('mp',(67,149,238)),('st',(74,206,134))):
        ring('arc_'+r+'_track',c,True)
        ring('arc_'+r+'_fill',c)
    medallion();orb();smear();flourish();nameplate();band();vignette()
    pill('pill_track');pill('pill_fill');icons()
    for src in ('hero','guild_clerk','merchant','villager'):
        portrait_from_sheet(src,'Chars')
    # HUD uses portrait as its default character icon.
    (OUT/'portrait.png').write_bytes((OUT/'portrait_hero.png').read_bytes())
    print('Generated',len(list(OUT.glob('*.png'))),'HUD PNG textures + icons.json at',OUT)


if __name__=='__main__':
    main()
