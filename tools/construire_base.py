import requests, json, time, re, unicodedata, os
from concurrent.futures import ThreadPoolExecutor
from styles_artistes import CATS
CA=os.path.expanduser('~/.ccr/ca-bundle.crt')
S=requests.Session(); S.verify=CA if os.path.exists(CA) else True
def norm(s): return re.sub(r'[^a-z0-9]','',unicodedata.normalize('NFD',s.lower()).encode('ascii','ignore').decode())
BAD=re.compile(r'\b(live|karaok[eé]|instrumental|remix|acapella|a cappella|medley|interlude|intro|skit|sped up|slowed|version)\b',re.I)
def clean(t):
    t=re.sub(r'\s*[\(\[][^\)\]]*(remaster|version|mono|stereo|edit|radio)[^\)\]]*[\)\]]','',t,flags=re.I)
    t=re.sub(r'\s+-\s+.*(remaster|version|edit).*$','',t,flags=re.I); return t.strip()
def get(url,params=None):
    for i in range(5):
        try:
            r=S.get(url,params=params,timeout=20); d=r.json()
            if 'error' in d and d['error'].get('code')==4: time.sleep(2); continue
            return d
        except Exception as e: time.sleep(2)
    return {}
ALT={'Matthieu Chedid':'-M-','The Jackson 5':'Jackson 5','Cat Stevens':'Yusuf / Cat Stevens'}
artists=[]
for k,(n,a) in CATS.items():
    for x in a.split('|'):
        if x not in artists: artists.append(x)
def work(a):
    q=norm(ALT.get(a,a))
    d=get('https://api.deezer.com/search/artist',{'q':ALT.get(a,a),'limit':10}).get('data',[])
    exact=[x for x in d if norm(x['name'])==q]
    cand=(exact or d[:1])
    if not cand: return a,None
    art=max(cand,key=lambda x:x.get('nb_fan',0))
    top=get(f"https://api.deezer.com/artist/{art['id']}/top",{'limit':25}).get('data',[])
    res=[];seen=set()
    for t in top:
        if not t.get('readable',True) or BAD.search(t['title']): continue
        title=clean(t.get('title_short') or t['title']); k=norm(title)
        if not k or k in seen: continue
        seen.add(k)
        contrib=[c['name'] for c in t.get('contributors',[])] or [t['artist']['name']]
        disp=' & '.join(dict.fromkeys(contrib)) if len(contrib)>1 else t['artist']['name']
        res.append({'t':title,'a':disp,'id':t['id'],'c':t['album'].get('md5_image',''),'al':t['album'].get('title','')})
        if len(res)>=12: break
    return a,{'name':art['name'],'id':art['id'],'tracks':res}
out={}
with ThreadPoolExecutor(4) as ex:
    for i,(a,r) in enumerate(ex.map(work,artists)):
        out[a]=r
        if i%50==0: print(i,a,len(r['tracks']) if r else None,flush=True)
out={a:r for a,r in out.items() if r and len(r['tracks'])>=3}
json.dump(out,open('raw_dz.json','w'),ensure_ascii=False)
miss=[a for a,r in out.items() if not r or len(r['tracks'])<3]
print('DONE',len(out),'missing',miss)
