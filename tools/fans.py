"""Ajoute à db.json le nombre de fans Deezer de chaque artiste (clé "f", en milliers, même ordre que "a").
Sert à choisir les artistes selon la difficulté : Facile et Moyen = les plus populaires du style, Difficile = les moins connus.
Lancer depuis tools/ : python3 fans.py"""
import json, re, time, unicodedata
from concurrent.futures import ThreadPoolExecutor
import requests
S=requests.Session()
def norm(s): s=unicodedata.normalize('NFD',str(s).lower());s=''.join(c for c in s if not unicodedata.combining(c));return re.sub(r'[^a-z0-9]','',s)
def get(url,params):
    for i in range(8):
        try:
            d=S.get(url,params=params,timeout=20).json()
            if 'error' in d: time.sleep(2+i);continue
            return d
        except Exception: time.sleep(2)
    return {}
db=json.load(open('../db.json'))
old=db.get('f') or [None]*len(db['a'])
def work(i):
    n=db['a'][i]
    if old[i] is not None and len(old)==len(db['a']): return old[i]
    d=get('https://api.deezer.com/search/artist',{'q':n,'limit':10}).get('data',[])
    ex=[x for x in d if norm(x['name'])==norm(n)] or d[:1]
    return round(max((x.get('nb_fan',0) for x in ex),default=0)/1000)
with ThreadPoolExecutor(3) as ex: f=list(ex.map(work,range(len(db['a']))))
db['f']=f
print('artistes',len(f),'sans fans',sum(1 for x in f if not x))
json.dump(db,open('../db.json','w'),ensure_ascii=False,separators=(',',':'))
