import json
from styles_artistes import CATS
import os
BIG=os.path.exists('raw_big.json')
raw=json.load(open('raw_big.json' if BIG else 'raw_dz.json'))
CM=json.load(open('cats_big.json')) if BIG else {k:v[1].split('|') for k,v in CATS.items()}
artists=[];idx={};seenid={}
for a,r in raw.items():
    if r['id'] in seenid: idx[a]=seenid[r['id']]; continue
    idx[a]=seenid[r['id']]=len(artists); artists.append(a)
cats=[[k,n,list(dict.fromkeys(idx[x] for x in CM[k] if x in idx))] for k,(n,a) in CATS.items()]
tracks=[];seen=set()
for a,r in raw.items():
    i=idx[a]
    if i in seen: continue
    seen.add(i)
    for t in r['tracks']:
        if '\ufffd' in t['t']+t['a']: continue
        parts=t['a'].split(' & ')
        if len(parts)>3: t['a']=' & '.join(parts[:3])+' & co.'
        tracks.append([i,t['t'],'' if t['a']==a else t['a'],t['id'],t['c'],t['al']])
js=json.dumps({'a':artists,'c':cats,'t':tracks},ensure_ascii=False,separators=(',',':'))
html=None
open('../db.json','w').write(js)
print(len(artists),'artistes',len(tracks),'morceaux',round(len(js)/1024),'Ko')
