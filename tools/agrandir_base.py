import json, time, os, re, requests, unicodedata
from concurrent.futures import ThreadPoolExecutor
from styles_artistes import CATS
src=open('construire_base.py').read().split('out={}')[0]; ns={}; exec(src,ns)
get,norm,BAD,clean=ns['get'],ns['norm'],ns['BAD'],ns['clean']
raw=json.load(open('raw_dz.json'))
TARGET=int(os.environ.get('TARGET','260')); MINFAN=int(os.environ.get('MINFAN','40000'))
known={r['id']:a for a,r in raw.items()}
catmem={k:[a for a in v[1].split('|') if a in raw] for k,v in CATS.items()}
def top(aid):
    t=get(f"https://api.deezer.com/artist/{aid}/top",{'limit':50}).get('data',[])
    res=[];seen=set()
    for x in t:
        if not x.get('readable',True) or BAD.search(x['title']): continue
        title=clean(x.get('title_short') or x['title']);k=norm(title)
        if not k or k in seen: continue
        seen.add(k)
        c=[y['name'] for y in x.get('contributors',[])] or [x['artist']['name']]
        disp=' & '.join(dict.fromkeys(c)) if len(c)>1 else x['artist']['name']
        res.append({'t':title,'a':disp,'id':x['id'],'c':x['album'].get('md5_image',''),'al':x['album'].get('title','')})
        if len(res)>=20: break
    return res
# 1) more tracks for existing artists (15 instead of 12)
def refill(a):
    r=raw[a]; t=top(r['id']); 
    if len(t)>len(r['tracks']): r['tracks']=t
with ThreadPoolExecutor(5) as ex: list(ex.map(refill,list(raw)))
print('refilled',sum(len(r['tracks']) for r in raw.values()),flush=True)
# 2) expand each category via related artists (2 passes: seeds, then the newcomers)
def rel(a): return get(f"https://api.deezer.com/artist/{raw[a]['id']}/related",{'limit':40}).get('data',[])
def mk(t):
    x=t[1]; tr=top(x['id']); return x,tr
for k,(n,_) in CATS.items():
    members=catmem[k]; seeds=list(members); fresh=[]
    for rnd in range(2):
        if len(members)>=TARGET or not seeds: break
        cand={}
        with ThreadPoolExecutor(5) as ex:
            for lst in ex.map(rel,seeds):
                for x in lst:
                    if x.get('nb_fan',0)<MINFAN: continue
                    c=cand.setdefault(x['id'],[x,0]); c[1]+=1
        ranked=sorted(cand.values(),key=lambda c:(-c[1],-c[0]['nb_fan']))
        need=2 if rnd==0 else 1
        add=[]
        for x,score in ranked:
            if len(members)+len(add)>=TARGET: break
            if x['id'] in known:
                nm=known[x['id']]
                if rnd==0 and nm not in members and nm not in add and score>=2: add.append(nm)
                continue
            if score<need and not (rnd==1 and x.get('nb_fan',0)>=150000): continue
            if rnd==1 and score<2 and x.get('nb_fan',0)<150000: continue
            add.append(('new',x))
        newones=[x for x in add if isinstance(x,tuple)]
        with ThreadPoolExecutor(5) as ex:
            for x,tr in ex.map(mk,newones):
                if len(tr)<5: continue
                raw[x['name']]={'name':x['name'],'id':x['id'],'tracks':tr}; known[x['id']]=x['name']; members.append(x['name']); fresh.append(x['name'])
        members+=[a for a in add if isinstance(a,str)]
        seeds=fresh; fresh=[]
        members=list(dict.fromkeys(members))
    catmem[k]=members
    print(k,len(catmem[k]),flush=True)
json.dump(raw,open('raw_big.json','w'),ensure_ascii=False)
json.dump(catmem,open('cats_big.json','w'),ensure_ascii=False)
print('DONE',len(raw),sum(len(r['tracks']) for r in raw.values()),flush=True)
