import sys,colorsys,numpy as np
from PIL import Image
SRC='/mnt/user-data/uploads/c803a4ca-image.png'
def point_color(p1):
    im=Image.open(p1).convert('RGB');best=None
    for y in range(16,40):
        for x in (300,540,780):
            r,g,b=im.getpixel((x,y));h,s,v=colorsys.rgb_to_hsv(r/255,g/255,b/255)
            if best is None or s*v>best[0]: best=(s*v,(r,g,b))
    return best[1]
def recolor(rgb,out,src=SRC):
    th,ts,tv=colorsys.rgb_to_hsv(*[c/255 for c in rgb])
    im=Image.open(src).convert('RGB');a=np.asarray(im).astype(float)/255
    hsv=np.asarray(im.convert('HSV')).astype(float)/255
    H,S,V=hsv[...,0],hsv[...,1],hsv[...,2]
    m=(V<0.45)&(H>100/360)&(H<210/360)
    S2=np.clip(S*(max(ts,0.35)*0.95/0.26),0,1)
    H2=np.full_like(H,th)
    out_hsv=np.stack([np.where(m,H2,H),np.where(m,S2,S),V],-1)
    res=Image.fromarray((out_hsv*255).astype('uint8'),'HSV').convert('RGB')
    a2=np.asarray(res).copy();orig=np.asarray(im)
    a2[~m]=orig[~m]
    Image.fromarray(a2).save(out,quality=93)
if __name__=='__main__':
    recolor(point_color(sys.argv[1]),sys.argv[2])
