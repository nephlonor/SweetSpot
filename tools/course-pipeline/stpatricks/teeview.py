import numpy as np,math,json
G=np.load('mnt.npy')
def z(e,n): return float(G[int(round(n))+970,int(round(e))+750])
h=open('rd_head.js').read();H=json.loads(h[h.index('{'):h.rindex('}')+1])['holes']
for i,hh in enumerate(H):
    t=hh['tee'];a=hh['line'][1];L=math.dist(t,a);u=((a[0]-t[0])/L,(a[1]-t[1])/L);z0=z(*t)
    worst=max(((z(t[0]+u[0]*d,t[1]+u[1]*d)-z0-1.5)/d,d) for d in range(8,90,2))
    back=[round(z(t[0]-u[0]*d,t[1]-u[1]*d)-z0,1) for d in (10,20,30)]
    print(i+1,'slope-to-crest %.3f at %d m'%worst,'behind',back)
