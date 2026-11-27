"""Playlists faites d'une liste d'artistes : on prend leurs titres les plus écoutés sur Deezer.
Lancé seul (python3 playlists_artistes.py, modifie ../db.json) ou à la fin de playlists_theme.py.
« Problématique » : seulement des artistes condamnés ou ayant plaidé coupable, affaires publiques et très médiatisées.
Aucun texte sur ces affaires n'est affiché dans le jeu."""
import json, os, time
from construire_base import get, clean, base, BAD
ARTPL = [
 ('probleme', 'Problématique', '⚖️', 9, ['Chris Brown', 'R. Kelly', '6ix9ine', 'Tory Lanez', 'Lil Wayne', 'T.I.', 'Gucci Mane',
   'Kodak Black', 'Meek Mill', 'DMX', 'Ms. Lauryn Hill', 'James Brown', 'Gary Glitter', 'Diddy', 'Sean Kingston', 'Young Thug',
   'Booba', 'Kaaris', 'Rohff', 'MHD', 'Noir Désir', 'A$AP Rocky']),
 ('youtube', 'YouTube', '▶️', 12, ['Squeezie', 'McFly & Carlito', 'Mister V', 'Cyprien', 'Michou', 'Inoxtag', 'Lebouseuh', 'Tibo InShape',
   'Natoo', 'KSI', 'Logan Paul', 'Jake Paul', 'PewDiePie', 'Sidemen', 'Pentatonix', 'Lindsey Stirling', 'Boyce Avenue',
   'Epic Rap Battles of History', 'Bo Burnham', 'Rice Gum']),
]
def norm(s): return ''.join(c for c in s.lower() if c.isalnum())
def build():
    out = []
    for key, name, emo, per, artists in ARTPL:
        got, ids, seen = [], set(), set()
        for a in artists:
            time.sleep(0.1)
            res = get('https://api.deezer.com/search/artist', {'q': a, 'limit': 10}).get('data', [])
            art = next((x for x in res if norm(x['name']) == norm(a)), None)
            if not art: print('  introuvable :', name, '|', a); continue
            n = 0
            for t in get(f"https://api.deezer.com/artist/{art['id']}/top", {'limit': 40}).get('data', []):
                if n >= per: break
                if not t.get('preview') or not t.get('readable', True) or t['id'] in ids or BAD.search(t['title']): continue
                title = clean(t.get('title_short') or t['title']); k = base(title) + '|' + norm(art['name'])
                if k in seen: continue
                ids.add(t['id']); seen.add(k); n += 1
                got.append([art['name'], title, t['id'], t.get('album', {}).get('md5_image', ''), t.get('album', {}).get('title', '')])
            print(f'  {name} | {art["name"]} : {n} titres')
        print(name, ':', len(got), 'titres', flush=True)
        if len(got) >= 30: out.append([key, name, emo, got])
    return out
def merge(db, extra):
    keys = {x[0] for x in extra}
    db['l'] = [x for x in db.get('l', []) if x[0] not in keys] + extra
if __name__ == '__main__':
    db = json.load(open('../db.json'))
    merge(db, build())
    open('../db.json', 'w').write(json.dumps(db, ensure_ascii=False, separators=(',', ':')))
