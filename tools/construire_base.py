import requests, json, time, re, unicodedata, os
from concurrent.futures import ThreadPoolExecutor
from styles_artistes import CATS
CA=os.path.expanduser('~/.ccr/ca-bundle.crt')
S=requests.Session(); S.verify=CA if os.path.exists(CA) else True
NB=int(os.environ.get('TITRES','50'))  # titres gardés par artiste
def norm(s): return re.sub(r'[^a-z0-9]','',unicodedata.normalize('NFD',s.lower()).encode('ascii','ignore').decode())
BAD=re.compile(r'\b(live|karaok[eé]|instrumental|remix|acapella|a cappella|medley|interlude|intro|outro|skit|sped up|slowed|version|demo|acoustic|acoustique|unplugged|reprise|nightcore)\b',re.I)
def clean(t):
    # enlève les « (feat. X) », « [with X] », « - Remastered 2011 », « (from the series …) »
    t=re.sub(r'\s*[\(\[](feat\.?|ft\.?|featuring|with|avec|prod\.?)\s[^\)\]]*[\)\]]','',t,flags=re.I)
    t=re.sub(r'\s+(feat\.?|ft\.|featuring)\s.*$','',t,flags=re.I)
    t=re.sub(r'\s*[\(\[][^\)\]]*(remaster|version|mono|stereo|edit|radio|from |tiré|bande originale|soundtrack|original motion)[^\)\]]*[\)\]]','',t,flags=re.I)
    t=re.sub(r'\s+-\s+.*(remaster|version|edit|from |mix).*$','',t,flags=re.I); return t.strip()
def base(t): return norm(re.sub(r'\s*[\(\[][^\)\]]*[\)\]]','',t)) or norm(t)
def get(url,params=None):
    for i in range(6):
        try:
            r=S.get(url,params=params,timeout=20); d=r.json()
            if 'error' in d and d['error'].get('code')==4: time.sleep(2+i); continue
            return d
        except Exception as e: time.sleep(2)
    return {}
def top(aid):
    """les titres les plus écoutés d'un artiste, nettoyés et sans doublons (versions, feat.)"""
    t=get(f"https://api.deezer.com/artist/{aid}/top",{'limit':100}).get('data',[])
    res=[];seen=set()
    for x in t:
        if not x.get('readable',True) or BAD.search(x['title']): continue
        title=clean(x.get('title_short') or x['title']);k=base(title)
        if not k or k in seen: continue
        seen.add(k)
        c=[y['name'] for y in x.get('contributors',[])] or [x['artist']['name']]
        disp=' & '.join(dict.fromkeys(c)) if len(c)>1 else x['artist']['name']
        res.append({'t':title,'a':disp,'id':x['id'],'c':x['album'].get('md5_image',''),'al':x['album'].get('title',''),'m':x['artist']['id']==aid})
        if len(res)>=NB: break
    return res
ALT={'Matthieu Chedid':'-M-','The Jackson 5':'Jackson 5','Cat Stevens':'Yusuf / Cat Stevens'}
artists=[]
for k,(n,a) in CATS.items():
    for x in a.split('|'):
        if x not in artists: artists.append(x)
out={}
def work(a):
    q=norm(ALT.get(a,a))
    d=get('https://api.deezer.com/search/artist',{'q':ALT.get(a,a),'limit':10}).get('data',[])
    exact=[x for x in d if norm(x['name'])==q]
    cand=(exact or d[:1])
    if not cand: return a,None
    art=max(cand,key=lambda x:x.get('nb_fan',0))
    return a,{'name':art['name'],'id':art['id'],'fans':art.get('nb_fan',0),'tracks':top(art['id'])}
if __name__=='__main__':
    with ThreadPoolExecutor(4) as ex:
        for i,(a,r) in enumerate(ex.map(work,artists)):
            out[a]=r
            if i%100==0: print(i,a,len(r['tracks']) if r else None,flush=True)
    miss=[a for a,r in out.items() if not r or len(r['tracks'])<3]
    out={a:r for a,r in out.items() if r and len(r['tracks'])>=3}
    json.dump(out,open('raw_dz.json','w'),ensure_ascii=False)
    print('DONE',len(out),'missing',miss)
