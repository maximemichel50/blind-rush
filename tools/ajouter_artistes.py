"""Ajout rapide d'artistes dans db.json, sans tout reconstruire (quelques minutes).
Liste dans ajouts.txt : une ligne « style|Nom de l'artiste » (ex. rapfr|Kikesa).
Prend ses titres les plus écoutés puis ceux de ses albums, jusqu'à DISCO titres."""
import json, os, re
from construire_base import get, clean, base, BAD
DISCO=int(os.environ.get('DISCO','120'))
db=json.load(open('../db.json'))
cats={c[0]:c for c in db['c']}
have={t[3] for t in db['t']}
for line in open('ajouts.txt',encoding='utf-8'):
    line=line.strip()
    if not line or line.startswith('#'): continue
    style,name=line.split('|',1)
    res=get('https://api.deezer.com/search/artist',{'q':name,'limit':5}).get('data',[])
    art=next((x for x in res if x['name'].lower()==name.lower()),res[0] if res else None)
    if not art: print('introuvable :',name); continue
    aid=art['id']
    if name in db['a']: i=db['a'].index(name)
    else: i=len(db['a']); db['a'].append(name); db['p'].append(3)
    if 'f' in db:
        while len(db['f'])<len(db['a']): db['f'].append(0)
        db['f'][i]=round(art.get('nb_fan',0)/1000)
    if style in cats and i not in cats[style][2]: cats[style][2].append(i)
    seen={base(t[1]) for t in db['t'] if t[0]==i}; out=[]
    def add(x,alb,cov):
        if len(out)>=DISCO or x['id'] in have or not x.get('readable',True): return
        if x.get('artist',{}).get('id')!=aid or BAD.search(x['title']): return
        title=clean(x.get('title_short') or x['title']);k=base(title)
        if not k or k in seen: return
        seen.add(k);have.add(x['id'])
        out.append([i,title,'',x['id'],cov,alb])
    for x in get(f'https://api.deezer.com/artist/{aid}/top',{'limit':50}).get('data',[]):
        add(x,x.get('album',{}).get('title',''),x.get('album',{}).get('md5_image',''))
    albs=get(f'https://api.deezer.com/artist/{aid}/albums',{'limit':100}).get('data',[])
    albs=[a for a in albs if not re.search(r'live|karaok|instrumental|remix|acoustic',a.get('title',''),re.I)]
    albs.sort(key=lambda a:(a.get('record_type')!='album',-a.get('fans',0)))
    for al in albs[:40]:
        if len(out)>=DISCO: break
        for x in get(f"https://api.deezer.com/album/{al['id']}/tracks",{'limit':100}).get('data',[]):
            add(x,al.get('title',''),al.get('md5_image',''))
    db['t'].extend(out)
    print(name,'(Deezer',art['name'],aid,') :',len(out),'titres ajoutés',flush=True)
open('../db.json','w').write(json.dumps(db,ensure_ascii=False,separators=(',',':')))
