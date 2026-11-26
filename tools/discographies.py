"""Ajoute une grosse partie de la discographie des plus grands artistes et de tout le rap FR choisi à la main.
Lancé entre agrandir_base.py et empaqueter_base.py. Modifie raw_big.json (ou raw_dz.json).
Pour chaque artiste choisi : ses titres les plus écoutés d'abord (déjà là), puis les titres de ses albums,
singles et EP, du plus écouté au moins écouté, sans les live, remix, versions et doublons, jusqu'à DISCO titres."""
import json, os, re
from concurrent.futures import ThreadPoolExecutor
from styles_artistes import CATS
from construire_base import get, clean, base, BAD
F='raw_big.json' if os.path.exists('raw_big.json') else 'raw_dz.json'
raw=json.load(open(F))
DISCO=int(os.environ.get('DISCO','150'))       # titres maximum par artiste choisi
BIGFAN=int(os.environ.get('BIGFAN','3000000')) # « plus grands artistes du monde » : au moins 3 millions de fans Deezer
MAXALB=int(os.environ.get('MAXALB','60'))      # albums / singles regardés au maximum par artiste
RAPFR=set(CATS['rapfr'][1].split('|'))
pick=[a for a,r in raw.items() if (a in RAPFR and not r.get('auto')) or r.get('fans',0)>=BIGFAN]
print(len(pick),'artistes à compléter',flush=True)
def work(a):
    r=raw[a];aid=r['id'];have=list(r['tracks']);seen={base(t['t']) for t in have};ids={t['id'] for t in have}
    albs=get(f"https://api.deezer.com/artist/{aid}/albums",{'limit':200}).get('data',[])
    albs=[x for x in albs if not re.search(r'live|karaok|instrumental|remix|acoustic|deluxe edition remaster|best of|greatest hits|anthology|collection',x.get('title',''),re.I)]
    albs.sort(key=lambda x:(x.get('record_type')!='album',-x.get('fans',0)))
    for al in albs[:MAXALB]:
        if len(have)>=DISCO: break
        for x in get(f"https://api.deezer.com/album/{al['id']}/tracks",{'limit':100}).get('data',[]):
            if len(have)>=DISCO: break
            if not x.get('readable',True) or x['id'] in ids or x.get('artist',{}).get('id')!=aid: continue
            if BAD.search(x['title']): continue
            title=clean(x.get('title_short') or x['title']);k=base(title)
            if not k or k in seen: continue
            seen.add(k);ids.add(x['id'])
            have.append({'t':title,'a':x['artist']['name'],'id':x['id'],'c':al.get('md5_image',''),'al':al.get('title',''),'m':True})
    return a,have
tot0=sum(len(raw[a]['tracks']) for a in pick)
with ThreadPoolExecutor(4) as ex:
    for i,(a,tr) in enumerate(ex.map(work,pick)):
        raw[a]['tracks']=tr
        if i%50==0: print(i,a,len(tr),flush=True)
print('titres des artistes complétés :',tot0,'->',sum(len(raw[a]['tracks']) for a in pick),flush=True)
json.dump(raw,open(F,'w'),ensure_ascii=False)
