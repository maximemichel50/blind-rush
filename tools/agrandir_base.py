"""Agrandit chaque style avec des artistes proches (Deezer « related »), en ne gardant que des artistes connus.
Les décennies ne sont pas agrandies : un artiste « proche » n'est pas forcément de la même époque."""
import json, os
from concurrent.futures import ThreadPoolExecutor
from styles_artistes import CATS
from construire_base import get, top
raw=json.load(open('raw_dz.json'))
TARGET=int(os.environ.get('TARGET','450'))      # artistes visés par style
MINFAN=int(os.environ.get('MINFAN','150000'))   # fans Deezer minimum pour un artiste ajouté automatiquement
SANS=('y70','y80','y90','y2000')                 # styles gardés à la main
known={r['id']:a for a,r in raw.items()}
catmem={k:[a for a in v[1].split('|') if a in raw] for k,v in CATS.items()}
def rel(a): return get(f"https://api.deezer.com/artist/{raw[a]['id']}/related",{'limit':40}).get('data',[])
def mk(x): return x,top(x['id'])
for k,(n,_) in CATS.items():
    members=catmem[k]
    if k in SANS or len(members)>=TARGET: print(k,len(members),flush=True); continue
    seeds=list(members); fresh=[]
    for rnd in range(3):
        if len(members)>=TARGET or not seeds: break
        cand={}
        with ThreadPoolExecutor(5) as ex:
            for lst in ex.map(rel,seeds):
                for x in lst:
                    if x.get('nb_fan',0)<MINFAN: continue
                    c=cand.setdefault(x['id'],[x,0]); c[1]+=1
        # il faut être « proche » d'au moins 2 artistes du style (ou 3 au 2e tour), sauf les très gros artistes
        need=2
        ranked=sorted(cand.values(),key=lambda c:(-c[1],-c[0]['nb_fan']))
        add=[]
        for x,score in ranked:
            if len(members)+len(add)>=TARGET: break
            if score<need and x.get('nb_fan',0)<3000000: continue
            if x['id'] in known:
                nm=known[x['id']]
                if nm not in members and nm not in add and score>=need: add.append(nm)
                continue
            add.append(('new',x))
        newones=[x for _,x in (a for a in add if isinstance(a,tuple))]
        with ThreadPoolExecutor(5) as ex:
            for x,tr in ex.map(mk,newones):
                if len(tr)<8 or x['name'] in raw: continue
                raw[x['name']]={'name':x['name'],'id':x['id'],'fans':x.get('nb_fan',0),'tracks':tr,'auto':True}
                known[x['id']]=x['name']; members.append(x['name']); fresh.append(x['name'])
        members+=[a for a in add if isinstance(a,str)]
        seeds=fresh; fresh=[]
        members=list(dict.fromkeys(members))
    catmem[k]=members
    print(k,len(catmem[k]),flush=True)
json.dump(raw,open('raw_big.json','w'),ensure_ascii=False)
json.dump(catmem,open('cats_big.json','w'),ensure_ascii=False)
print('DONE',len(raw),sum(len(r['tracks']) for r in raw.values()),flush=True)
