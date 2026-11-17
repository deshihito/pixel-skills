from PIL import Image, ImageDraw
import math, os
OUT="/home/hatch/workspace/pixel-training/001-slime/motion"
os.makedirs(OUT, exist_ok=True)
W=H=32
O=(38,58,44,255); DEEP=(53,94,51,255); SH=(74,127,67,255); M=(99,158,85,255); L=(143,191,127,255)
SHEEN=(196,226,175,255); BUB=(178,214,158,255); CORE=(58,99,58,255); CORE_RING=(82,122,72,255)
EYE=(14,30,20,255); WHT=(240,250,240,255)

def frame(dy, creep):
    """dy: dome vertical shift (+ squash / - stretch). creep: -1 retract, 0 base, +1 spread. Bottom always anchored."""
    cols={}
    for x in range(5,26):
        dx=(x-15)/10.0
        top=round(18-8*math.sqrt(max(0.0,1-dx*dx)))+dy
        if x in (11,12,13,14,15,16,17,18,19): b=28
        elif x in (8,9,10,20,21,22): b=27
        elif x in (6,7,23,24): b=27 if x%2==0 else 26
        else: b=26
        cols[x]=(top,b)
    base_creep={2:(23,24),3:(21,25),4:(19,26),26:(20,26),27:(22,27),28:(23,27),29:(25,27),30:(26,26)}
    if creep==0:
        cols.update(base_creep)
    elif creep==1:  # squashed: gel spreads sideways along the ground
        cols.update(base_creep); cols[1]=(24,24); cols[31]=(26,26)
        cols[2]=(23,25); cols[30]=(26,27)
    else:           # stretched: tips pull in
        cols.update({3:(21,25),4:(19,26),26:(20,26),27:(22,27),28:(24,27),29:(25,26)})
    mask=set(); bottom={}
    for x,(t,b) in cols.items():
        bottom[x]=b
        for y in range(t,b+1): mask.add((x,y))
    def is_outline(x,y):
        return any((x+dx,y+dy) not in mask for dx,dy in [(1,0),(-1,0),(0,1),(0,-1)])
    img=Image.new("RGBA",(W,H),(0,0,0,0)); px=img.load()
    for (x,y) in mask:
        if is_outline(x,y): px[x,y]=O; continue
        depth=bottom[x]-y; s=y+max(0,x-13)*0.3
        if depth<=1: c=DEEP
        elif depth==2: c=SH
        elif s<13.5+dy: c=L
        elif s<19+dy: c=M
        else: c=SH
        px[x,y]=c
    ring=[(10,22),(11,22),(12,22),(13,22),(14,22),(15,22),(16,22),(17,22),(18,22),(19,22),
          (9,23),(20,23),(9,24),(20,24),(10,25),(11,25),(18,25),(19,25),
          (12,26),(13,26),(14,26),(15,26),(16,26),(17,26)]
    centre=[(x,y) for y in (23,24) for x in range(10,20)]+[(x,25) for x in range(11,19)]
    for x,y in ring:
        if (x,y) in mask and not is_outline(x,y): px[x,y]=CORE_RING
    for x,y in centre:
        if (x,y) in mask and not is_outline(x,y): px[x,y]=CORE
    for x,y in [(21,16+dy),(22,16+dy)]: 
        if (x,y) in mask: px[x,y]=BUB
    for x,y in [(24,21),(8,21),(19,13+dy)]:
        if (x,y) in mask and not is_outline(x,y): px[x,y]=BUB
    for x,y in [(11,11+dy),(10,12+dy),(9,13+dy),(10,13+dy)]:
        if (x,y) in mask and not is_outline(x,y): px[x,y]=SHEEN
    for ex in (10,20):
        for y in range(14+dy,18+dy):
            for x in (ex,ex+1): px[x,y]=EYE
        px[ex,14+dy]=WHT
    return img

A=frame(0,0); B=frame(1,1); C=frame(-1,-1)
for name,im in [("frame0_base",A),("frame1_squash",B),("frame2_stretch",C)]:
    im.save(f"{OUT}/{name}_32.png")
    im.resize((256,256), Image.NEAREST).save(f"{OUT}/{name}@256.png")
# frames sheet
sheet=Image.new("RGBA",(96,32),(0,0,0,0))
sheet.alpha_composite(A,(0,0)); sheet.alpha_composite(B,(32,0)); sheet.alpha_composite(C,(64,0))
sheet.save(f"{OUT}/slime_motion_sheet_32.png")
sheet.resize((768,256), Image.NEAREST).save(f"{OUT}/slime_motion_sheet@256.png")
# GIF: loop A -> B -> A -> C on grass background (in-game feel), 256px
def on_grass(im):
    bg=Image.new("RGBA",(256,256),(106,170,80,255))
    d=ImageDraw.Draw(bg,"RGBA"); d.ellipse([60,226,210,244], fill=(0,0,0,60))
    bg.alpha_composite(im.resize((256,256), Image.NEAREST),(0,0))
    return bg.convert("RGB")
seq=[on_grass(A),on_grass(B),on_grass(A),on_grass(C)]
seq[0].save(f"{OUT}/slime_idle.gif", save_all=True, append_images=seq[1:], duration=320, loop=0)
print("done", os.listdir(OUT))
