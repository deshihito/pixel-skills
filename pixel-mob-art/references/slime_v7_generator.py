from PIL import Image, ImageDraw
import math
OUT="/home/hatch/workspace/pixel-training/001-slime"
W=H=32
O   = (38,58,44,255)
DEEP= (53,94,51,255)
SH  = (74,127,67,255)
M   = (99,158,85,255)
L   = (143,191,127,255)
SHEEN=(196,226,175,255)
BUB = (178,214,158,255)
CORE= (58,99,58,255)     # v7: nucleus softened (less contrast, no highlight -> won't read as an eye)
CORE_RING=(82,122,72,255)
EYE = (14,30,20,255)
WHT = (240,250,240,255)

cols={}
for x in range(5,26):
    dx=(x-15)/10.0
    top=round(18-8*math.sqrt(max(0.0,1-dx*dx)))
    if x in (11,12,13,14,15,16,17,18,19): b=28
    elif x in (8,9,10,20,21,22): b=27
    elif x in (6,7,23,24): b=27 if x%2==0 else 26
    else: b=26
    cols[x]=(top,b)
cols.update({2:(23,24),3:(21,25),4:(19,26),26:(20,26),27:(22,27),28:(23,27),29:(25,27),30:(26,26)})
mask=set(); bottom={}
for x,(t,b) in cols.items():
    bottom[x]=b
    for y in range(t,b+1): mask.add((x,y))
def is_outline(x,y):
    return any((x+dx,y+dy) not in mask for dx,dy in [(1,0),(-1,0),(0,1),(0,-1)])
img=Image.new("RGBA",(W,H),(0,0,0,0)); px=img.load()
for (x,y) in mask:
    if is_outline(x,y): px[x,y]=O; continue
    depth=bottom[x]-y
    s=y+max(0,x-13)*0.3
    if depth<=1: c=DEEP
    elif depth==2: c=SH
    elif s<13.5: c=L
    elif s<19: c=M
    else: c=SH
    px[x,y]=c
# nucleus: pushed low + wide/flat + soft, no highlight spot
ring=[(10,22),(11,22),(12,22),(13,22),(14,22),(15,22),(16,22),(17,22),(18,22),(19,22),
      (9,23),(20,23),(9,24),(20,24),
      (10,25),(11,25),(18,25),(19,25),
      (12,26),(13,26),(14,26),(15,26),(16,26),(17,26)]
centre=[(x,y) for y in (23,24) for x in range(10,20)]+[(x,25) for x in range(11,19)]
for x,y in ring:
    if (x,y) in mask and not is_outline(x,y): px[x,y]=CORE_RING
for x,y in centre:
    if (x,y) in mask and not is_outline(x,y): px[x,y]=CORE
# bubbles + sheen (same as v6)
for x,y in [(21,16),(22,16)]: px[x,y]=BUB
px[24,21]=BUB; px[8,21]=BUB; px[19,13]=BUB
for x,y in [(11,11),(10,12),(9,13),(10,13)]:
    if (x,y) in mask and not is_outline(x,y): px[x,y]=SHEEN
# EYES: a clearly separated PAIR, vertical ovals 2x4, gloss pixel top-left of each
for ex in (10,20):
    for y in range(14,18):
        for x in (ex,ex+1): px[x,y]=EYE
    px[ex,14]=WHT

img.save(f"{OUT}/slime_v7_32.png")
img.resize((256,256), Image.NEAREST).save(f"{OUT}/slime_v7_32@256.png")
sheet=Image.new("RGBA",(768,320),(24,24,28,255))
big=img.resize((256,256), Image.NEAREST)
for yy in range(32,288):
    for xx in range(32,288):
        sheet.putpixel((xx,yy),(58,58,64,255) if ((xx//32)+(yy//32))%2==0 else (38,38,42,255))
sheet.alpha_composite(big,(32,32))
for yy in range(32,288):
    for xx in range(288,544):
        sheet.putpixel((xx,yy),(106,170,80,255) if ((xx*7+yy*13)%29!=0) else (96,158,70,255))
d=ImageDraw.Draw(sheet,"RGBA")
d.ellipse([288+60,226,288+210,244], fill=(0,0,0,60))
sheet.alpha_composite(big,(288,16))
d.rectangle([544,32,736,288], fill=(16,24,40,255))
sheet.alpha_composite(big,(544,32))
sheet.convert("RGB").save(f"{OUT}/slime_v7_sheet.png")
print("ok")
