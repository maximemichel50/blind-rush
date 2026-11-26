"""Assemble db.json. Format : a = artistes, p = notoriété (0 à 3), c = styles, t = titres."""
import json, os, sys
from styles_artistes import CATS
BIG=os.path.exists('raw_big.json')
raw=json.load(open('raw_big.json' if BIG else 'raw_dz.json'))
CM=json.load(open('cats_big.json')) if BIG else {k:v[1].split('|') for k,v in CATS.items()}
MAIN=set(x for _,a in CATS.values() for x in a.split('|'))  # artistes choisis à la main
def tier(a,r):
    if a in MAIN and not r.get('auto'): return 3
    f=r.get('fans',0)
    return 2 if f>=1000000 else 1 if f>=300000 else 0
artists=[];pop=[];idx={};seenid={}
for a,r in raw.items():
    if r['id'] in seenid: idx[a]=seenid[r['id']]; pop[idx[a]]=max(pop[idx[a]],tier(a,r)); continue
    idx[a]=seenid[r['id']]=len(artists); artists.append(a); pop.append(tier(a,r))
cats=[[k,n,list(dict.fromkeys(idx[x] for x in CM[k] if x in idx))] for k,(n,a) in CATS.items()]
tracks=[];seen=set();done=set()
# un même morceau (featuring) n'est gardé qu'une fois : chez son artiste principal d'abord
for main in (True,False):
    for a,r in raw.items():
        i=idx[a]
        if (i,main) in done: continue
        done.add((i,main))
        for t in r['tracks']:
            if t.get('m',True)!=main or t['id'] in seen: continue
            if '�' in t['t']+t['a']: continue
            seen.add(t['id'])
            parts=t['a'].split(' & ')
            if len(parts)>3: t['a']=' & '.join(parts[:3])+' & co.'
            tracks.append([i,t['t'],'' if t['a']==a else t['a'],t['id'],t['c'],t['al']])
js=json.dumps({'a':artists,'p':pop,'c':cats,'t':tracks},ensure_ascii=False,separators=(',',':'))
print(len(artists),'artistes',len(tracks),'morceaux',round(len(js)/1024),'Ko','| connus :',sum(1 for p in pop if p>=2))
if len(artists)<int(os.environ.get('MIN_ARTISTES','1800')) or len(tracks)<int(os.environ.get('MIN_TITRES','30000')):
    sys.exit('Base trop petite : Deezer a sans doute mal répondu. db.json n\'est pas modifiée.')
open('../db.json','w').write(js)
