"""
TorchLit share-preview generator (prototype)

Makes a short GIF for one piece: a light walks through a few opening lines and leaves
illustrative lights behind, then notification-style messages fade in and out.
Edit LINES, the lights in `path`, and `notes` for each piece, then run:

    python make_share_preview.py <output-folder>

Rules: notifications must be true at the moment the GIF is made (no invented reader
counts), and the lights are illustrative, never a map of real readers' lights.
Requires Pillow and the DejaVu fonts (installed on most Linux systems).
"""
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import math, sys, os
OUT = sys.argv[1] if len(sys.argv) > 1 else "."

LINES = [
    ("There was a secret shortcut to the candy store", 0),
    ("that only the neighbourhood kids knew.",         0),
    ("And in that garden stood a pomelo tree,",        2),
    ("its fruits impossibly large,",                   1),
    ("suspended like golden moons.",                   3),
    ("They called to us.",                             2),
    ("We never dared pluck them, but the temptation",  0),
    ("lingered, sweet and sticky",                     0),
    ("like the candies we craved.",                    1),
]
INK=(21,18,27); GLOW=(250,226,178); AMBER=(196,146,79); DIM=(135,126,146); FOOTC=(222,178,102)
SERIF="/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
ITAL ="/usr/share/fonts/truetype/dejavu/DejaVuSerif-Italic.ttf"
SANS ="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
W=H=640; x0=52; lh=40; y0=150
f_body=ImageFont.truetype(SERIF,21); f_mark=ImageFont.truetype(SANS,13); f_foot=ImageFont.truetype(ITAL,19)

def mix(a,b,t): return tuple(int(a[i]+(b[i]-a[i])*t) for i in range(3))

def paint(levels, walker=None, footer=None, falpha=0.0, breath=1.0):
    base=Image.new("RGB",(W,H),INK); glow=Image.new("RGB",(W,H),INK); gd=ImageDraw.Draw(glow)
    y=y0
    for (text,_),lvl in zip(LINES,levels):
        if lvl>0.05:
            w=gd.textlength(text,font=f_body); pad=12+lvl*6
            a={1:70,2:130,3:200}.get(round(lvl),0) if abs(lvl-round(lvl))<1e-6 else 200*lvl/3
            a*= (breath if lvl>=2.6 else 1.0)
            gold=(236,186,96) if lvl>=2.6 else GLOW
            gd.rounded_rectangle([x0-pad,y-lh*.17,x0+w+pad,y+lh*.72],radius=lh//2,fill=mix(INK,gold,a/255))
        y+=lh
    if walker is not None:
        wy=y0+walker*lh; ww=gd.textlength(LINES[walker][0],font=f_body); pad=lh*.45
        gd.rounded_rectangle([x0-pad,wy-lh*.22,x0+ww+pad,wy+lh*.78],radius=lh//2,fill=(255,252,244))
    img=Image.blend(base,glow.filter(ImageFilter.GaussianBlur(17)),0.95); d=ImageDraw.Draw(img)
    y=y0
    for i,((text,_),lvl) in enumerate(zip(LINES,levels)):
        k=min(1.0,lvl/3.0)*(breath if lvl>=2.6 else 1.0)
        col=(int(112+143*k),int(106+144*k),int(122+116*k))
        if walker is not None and i==walker: col=(255,253,248)
        d.text((x0,y),text,font=f_body,fill=col); y+=lh
    m=lh*.34
    d.ellipse([x0,y0-lh*1.95,x0+m,y0-lh*1.95+m],fill=AMBER)
    d.text((x0+m*1.75,y0-lh*2.02),"TORCHLIT",font=f_mark,fill=DIM)
    if footer and falpha>0.01:
        fy=H-lh*(1.05*len(footer)+.55)
        for k,line in enumerate(footer):
            d.text((x0,fy+k*lh*1.05),line,font=f_foot,fill=mix(INK,FOOTC,falpha))
    return img.convert("P",palette=Image.ADAPTIVE,colors=256)


# ── share preview ──────────────────────────────────────────
f_toast=ImageFont.truetype(SANS,15)

def toast(img, text, a, slide):
    """notification pill at the bottom: gold dot + text, fading and sliding up"""
    if a<=0.01: return img
    img=img.convert("RGB"); d=ImageDraw.Draw(img)
    w=d.textlength(text,font=f_toast); pw=w+58; ph=40
    x=x0; y=H-78+int((1-slide)*14)
    d.rounded_rectangle([x,y,x+pw,y+ph],radius=20,fill=mix(INK,(44,38,52),a),outline=mix(INK,(120,96,58),a))
    d.ellipse([x+16,y+15,x+26,y+25],fill=mix(INK,(226,176,92),a))
    d.text((x+38,y+11),text,font=f_toast,fill=mix(INK,(236,222,200),a))
    return img

path={2:2,4:3,5:2,8:1}            # the walk leaves these lights on
F=[];D=[]
lv=[0.0]*len(LINES)
for i in range(len(LINES)):
    F.append(paint(lv,walker=i).convert("RGB")); D.append(260+path.get(i,0)*360)
    if i in path: lv[i]=float(path[i])
notes=["New on Torchlit · Taqwa","A memoir piece · 2-minute read","Be the first to leave your light"]
for n in notes:
    for k,(a,s) in enumerate([(.33,.33),(.66,.66),(1,1),(1,1),(1,1),(1,1),(1,1),(.66,1),(.33,1),(0,1)]):
        F.append(toast(paint(lv,breath=0.82+0.18*((k%4)/3)),n,a,s)); D.append(140)
for s in (1,2,3,4):
    F.append(paint([v*(1-s/4) for v in lv]).convert("RGB")); D.append(90)
F=[f.convert("P",palette=Image.ADAPTIVE,colors=256) for f in F]
p=os.path.join(OUT,"pomelo-share.gif")
F[0].save(p,save_all=True,append_images=F[1:],duration=D,loop=0,disposal=2)
print(p, os.path.getsize(p)//1024,"KB")
