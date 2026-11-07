from PIL import Image,ImageDraw,ImageFont
from pathlib import Path
D=256;T=D//2;root=Path(__file__).resolve().parent
font=ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf',18)
small=ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf',15)
big=ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf',25)
rows=[('XOR: fixed v = 1',[2,6,10,130,134,138,258],1),('XOR: increasing v',[2,4,8,16,32,64,128],1),('Fourth-power OR',[1,2,4,8,16,32,64],4)]
sheet=Image.new('RGB',(1140,650),'#f4f0e8');draw=ImageDraw.Draw(sheet)
draw.text((20,18),'Post-power structure: D = 256',font=big,fill='#252820')
draw.text((20,56),'Grayscale shows A = (z^p mod M − 1) / 2^v, normalized by D; channel colors are excluded.',font=small,fill='#55594e')
for row,(label,powers,pre) in enumerate(rows):
 y=100+row*180;draw.text((20,y+45),label,font=font,fill='#252820')
 for col,p in enumerate(powers):
  v=(p&-p).bit_length()-1;M=D<<v;pixels=[]
  for i in range(T):
   for j in range(T):
    u=(i-j-1)%D;w=(i+j)%D
    a=pow(u,pre,D);b=pow(w,pre,D);z=a^b if pre==1 else a|b
    A=(pow(z,p,M)-1)//(1<<v)
    pixels.append(round(255*A/D))
  tile=Image.new('L',(T,T));tile.putdata(pixels)
  x=230+col*129;sheet.paste(tile,(x,y))
  draw.text((x,y+132),f'p={p} · v={v}',font=small,fill='#252820')
draw.text((20,632),'Equal tiles are exact arithmetic matches. High-v matches here omit the changing 1/M offset.',font=small,fill='#55594e')
sheet.save(root/'2026-10-11-post-power-structure.png')
