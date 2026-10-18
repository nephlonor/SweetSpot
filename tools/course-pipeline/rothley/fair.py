import json, math, numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage as ndi
F=json.load(open('feat.json')); E0,N1,RES=-650,750,0.5
I=np.array(Image.open('course.jpg').convert('RGB')).astype(float); Hh,Ww=I.shape[:2]
CHM=np.load('mnh.npy')
L=I.mean(2); Ls=ndi.gaussian_filter(L,3)
var=np.sqrt(ndi.gaussian_filter((L-ndi.gaussian_filter(L,1.5))**2,4))
def samp(a,e,n):
    x=(np.asarray(e)-E0)/RES-.5; y=(N1-np.asarray(n))/RES-.5
    return ndi.map_coordinates(a,[y,x],order=1,mode='nearest')
def chm(e,n):
    return ndi.map_coordinates(CHM,[np.asarray(n)+900-.5,np.asarray(e)+800-.5],order=1,mode='nearest')
PAR={1:4,2:4,3:4,4:3,5:4,6:4,7:3,8:4,9:4,10:4,11:4,12:3,13:4,14:4,15:5,16:4,17:4,18:5}
res={}
for h in sorted(F['holes'],key=lambda h:int(h['tags']['ref'])):
    ref=int(h['tags']['ref']); P=np.array(h['pts'])
    seg=np.r_[0,np.cumsum(np.hypot(*np.diff(P,axis=0).T))]; Lh=seg[-1]
    st=np.arange(0,Lh,4.0)
    C=np.c_[np.interp(st,seg,P[:,0]),np.interp(st,seg,P[:,1])]
    D=np.gradient(C,axis=0); D/=np.linalg.norm(D,axis=1)[:,None]; N=np.c_[-D[:,1],D[:,0]]
    off=np.arange(-30,30.1,1.0)
    E=C[:,0][:,None]+N[:,0][:,None]*off; Nn=C[:,1][:,None]+N[:,1][:,None]*off
    Lv=samp(Ls,E,Nn); Vv=samp(var,E,Nn); Tv=chm(E,Nn)
    # a fairway cell: bright, smooth, no canopy
    ok=Tv<1.5
    ref_L=np.median(Lv[ok]); 
    sc=(Lv-np.percentile(Lv[ok],35))/(np.percentile(Lv[ok],90)-np.percentile(Lv[ok],35)+1e-6) - (Vv-np.percentile(Vv[ok],30))/(np.percentile(Vv[ok],85)-np.percentile(Vv[ok],30)+1e-6)*.6
    sc=ndi.uniform_filter1d(sc,5,axis=0)
    good=(sc>0.25)&ok
    lw=[];rw=[];cen=len(off)//2
    for i in range(len(st)):
        g=good[i]; 
        # start from the best cell near the line
        win=range(cen-8,cen+9); s=max(win,key=lambda k:sc[i,k] if g[k] else -9)
        if not g[s]: lw.append(np.nan); rw.append(np.nan); continue
        a=s
        while a-1>=0 and (good[i,a-1] or (a-2>=0 and good[i,a-2])): a-=1
        b=s
        while b+1<len(off) and (good[i,b+1] or (b+2<len(off) and good[i,b+2])): b+=1
        lw.append(off[a]); rw.append(off[b])
    lw=np.array(lw,float); rw=np.array(rw,float)
    res[ref]={'st':st.tolist(),'C':C.tolist(),'N':N.tolist(),'l':lw.tolist(),'r':rw.tolist(),'L':Lh}
    print(ref,'L %.0f'%Lh,'valid %.2f'%np.mean(~np.isnan(lw)),'w med %.1f'%np.nanmedian(rw-lw))
json.dump(res,open('fair_prof.json','w'))
