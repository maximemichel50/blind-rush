"""Playlists « œuvres » : Films et séries, Dessins animés, Disney, Manga.
On ne devine pas l'artiste ni le titre, mais le film / la série / le dessin animé / le manga d'où vient le son.
Chaque son a un 6e champ : le nom de l'œuvre.  [artiste, titre, idDeezer, hashPochette, album, œuvre]
Sources : 1) les listes à la main ci-dessous (œuvre, titre, artiste ou 'générique')
          2) les sons des anciennes playlists dont l'album dit clairement de quel film / quelle série il vient.
Lancé seul (modifie ../db.json) par l'étape [ajout], et à la fin de playlists_theme.py."""
import json, re, time, unicodedata, requests
API = 'https://api.deezer.com'
BAD = re.compile(r'karaok|instrumental version|remix|8 ?-?bit|lofi|lo-fi|parod|made famous|in the style|originally performed|tribute|cover|lullaby|berceuse|piano version', re.I)
def norm(s):
    s = unicodedata.normalize('NFD', str(s).lower())
    return re.sub(r'[^a-z0-9]', '', ''.join(c for c in s if unicodedata.category(c) != 'Mn'))
def base(s): return norm(re.sub(r'\s*[(\[][^)\]]*[)\]]', '', s)) or norm(s)
def get(url, params):
    for i in range(4):
        try:
            r = requests.get(url, params=params, timeout=15).json()
            if 'error' in r and r['error'].get('code') == 4: time.sleep(2 + i * 2); continue
            return r
        except Exception: time.sleep(1 + i)
    return {}
G = 'générique'
FILMS = [
 ('Moi, moche et méchant 2','Happy','Pharrell Williams'),('Titanic','My Heart Will Go On','Celine Dion'),
 ('Top Gun','Take My Breath Away','Berlin'),('Top Gun','Danger Zone','Kenny Loggins'),('Rocky III','Eye of the Tiger','Survivor'),
 ('SOS Fantômes','Ghostbusters','Ray Parker Jr.'),('Dirty Dancing','(I\'ve Had) The Time of My Life','Bill Medley'),
 ('Grease','You\'re the One That I Want','John Travolta'),('Pulp Fiction','Misirlou','Dick Dale'),('Footloose','Footloose','Kenny Loggins'),
 ('La Fièvre du samedi soir','Stayin\' Alive','Bee Gees'),('Bodyguard','I Will Always Love You','Whitney Houston'),
 ('Retour vers le futur','The Power of Love','Huey Lewis'),('Star Wars','Main Title','John Williams'),
 ('Jurassic Park','Theme From Jurassic Park','John Williams'),('Harry Potter','Hedwig\'s Theme','John Williams'),
 ('Indiana Jones','Raiders March','John Williams'),('Les Dents de la mer','Main Title','John Williams'),
 ('E.T. l\'extra-terrestre','Flying Theme','John Williams'),('Superman','Theme','John Williams'),
 ('Pirates des Caraïbes','He\'s a Pirate','Klaus Badelt'),('Gladiator','Now We Are Free','Hans Zimmer'),
 ('Interstellar','Cornfield Chase','Hans Zimmer'),('Inception','Time','Hans Zimmer'),('Skyfall','Skyfall','Adele'),
 ('James Bond','James Bond Theme','Monty Norman'),('Mission impossible','Mission: Impossible','Lalo Schifrin'),
 ('Le Parrain','Speak Softly Love','Nino Rota'),('Le Bon, la Brute et le Truand','The Good, the Bad and the Ugly','Ennio Morricone'),
 ('Il était une fois dans l\'Ouest','Man with a Harmonica','Ennio Morricone'),('Le Professionnel','Chi Mai','Ennio Morricone'),
 ('Le Fabuleux Destin d\'Amélie Poulain','Comptine d\'un autre été','Yann Tiersen'),('Intouchables','Una Mattina','Ludovico Einaudi'),
 ('Les Choristes','Vois sur ton chemin','Les Petits Chanteurs de Saint-Marc'),('Rocky','Gonna Fly Now','Bill Conti'),
 ('8 Mile','Lose Yourself','Eminem'),('Black Panther','All the Stars','Kendrick Lamar'),('A Star Is Born','Shallow','Lady Gaga'),
 ('Barbie','What Was I Made For?','Billie Eilish'),('Barbie','Dance The Night','Dua Lipa'),('The Greatest Showman','This Is Me','Keala Settle'),
 ('La La Land','City of Stars','Ryan Gosling'),('Les Gardiens de la Galaxie','Hooked on a Feeling','Blue Swede'),
 ('Shrek','All Star','Smash Mouth'),('Shrek','I\'m a Believer','Smash Mouth'),('Les Trolls','Can\'t Stop the Feeling!','Justin Timberlake'),
 ('Fast & Furious 7','See You Again','Wiz Khalifa'),('Men in Black','Men in Black','Will Smith'),
 ('Armageddon','I Don\'t Want to Miss a Thing','Aerosmith'),('Flashdance','Flashdance... What a Feeling','Irene Cara'),
 ('Le Flic de Beverly Hills','Axel F','Harold Faltermeyer'),('Pretty Woman','Oh, Pretty Woman','Roy Orbison'),
 ('Le Seigneur des anneaux','Concerning the Hobbits','Howard Shore'),('Kill Bill','Bang Bang (My Baby Shot Me Down)','Nancy Sinatra'),
 ('Trainspotting','Born Slippy','Underworld'),('Matrix','Clubbed to Death','Rob Dougan'),('Purple Rain','Purple Rain','Prince'),
 ('Spider-Man : New Generation','Sunflower','Post Malone'),('Space Jam','Space Jam','Quad City DJ\'s'),('Twilight','Decode','Paramore'),
 ('Ghost','Unchained Melody','The Righteous Brothers'),('Le Dernier des Mohicans','Promentory','Trevor Jones'),
 ('Requiem for a Dream','Lux Aeterna','Clint Mansell'),('Les Chariots de feu','Chariots of Fire','Vangelis'),
 ('The Breakfast Club','Don\'t You (Forget About Me)','Simple Minds'),('Top Gun : Maverick','Hold My Hand','Lady Gaga'),
 ('Oppenheimer','Can You Hear The Music','Ludwig Göransson'),('Le Livre de la jungle','Il en faut peu pour être heureux','Le Livre de la jungle'),
 ('Forrest Gump','Feather Theme','Alan Silvestri'),('Avengers','The Avengers','Alan Silvestri'),('Batman','The Dark Knight','Hans Zimmer'),
 ('Le Roi lion','Circle of Life','Elton John'),('Rocky IV','Burning Heart','Survivor'),('Rasta Rockett','Rise Up','Cliff'),
 ('Sister Act','I Will Follow Him','Sister Act'),('Mamma Mia!','Dancing Queen','Mamma Mia'),('Wayne\'s World','Bohemian Rhapsody','Queen'),
 ('Highlander','Princes of the Universe','Queen'),('Flash Gordon','Flash','Queen'),('Les Aventuriers de l\'arche perdue','Raiders March','John Williams'),
 ('Le Grand Bleu','The Big Blue Overture','Eric Serra'),('Taxi','Pump Up the Jam','Technotronic'),('Fame','Fame','Irene Cara'),
 ('Pocahontas','Colors of the Wind','Vanessa Williams'),('Robin des Bois','(Everything I Do) I Do It for You','Bryan Adams'),
 ('Love Actually','Christmas Is All Around','Bill Nighy'),('Le Loup de Wall Street','Mrs. Robinson','Simon & Garfunkel'),
 ('Le Lauréat','Mrs. Robinson','Simon & Garfunkel'),('Les Bronzés','Just Because of You','Les Bronzés'),
]
SERIES = [
 ('Friends','I\'ll Be There for You','The Rembrandts'),('Game of Thrones','Main Title','Ramin Djawadi'),
 ('Stranger Things','Stranger Things','Kyle Dixon'),('La Casa de Papel','Bella Ciao','Manu Pilas'),('Breaking Bad','Main Title Theme','Dave Porter'),
 ('X-Files','The X-Files','Mark Snow'),('Twin Peaks','Twin Peaks Theme','Angelo Badalamenti'),('Dr House','Teardrop','Massive Attack'),
 ('Grey\'s Anatomy','Cosy in the Rocket','Psapp'),('The Office','The Office Theme','The Scrantones'),
 ('How I Met Your Mother','Hey Beautiful','The Solids'),('Le Prince de Bel-Air','Yo Home to Bel-Air','DJ Jazzy Jeff'),
 ('Dexter','Blood Theme','Daniel Licht'),('Peaky Blinders','Red Right Hand','Nick Cave'),('Mercredi','Goo Goo Muck','The Cramps'),
 ('The Big Bang Theory','Big Bang Theory Theme','Barenaked Ladies'),('Scrubs','Superman','Lazlo Bane'),
 ('Malcolm','Boss of Me','They Might Be Giants'),('Les Soprano','Woke Up This Morning','Alabama 3'),('Mad Men','A Beautiful Mine','RJD2'),
 ('Narcos','Tuyo','Rodrigo Amarante'),('Squid Game','Way Back Then','Jung Jae Il'),('Vikings','If I Had a Heart','Fever Ray'),
 ('The Walking Dead','Main Title','Bear McCreary'),('Desperate Housewives','Main Title','Danny Elfman'),
 ('Charmed','How Soon Is Now?','Love Spit Love'),('Buffy contre les vampires','Buffy','Nerf Herder'),
 ('Dawson','I Don\'t Want to Wait','Paula Cole'),('Les Frères Scott','I Don\'t Want to Be','Gavin DeGraw'),
 ('Prison Break','Prison Break Main Title','Ramin Djawadi'),('24 heures chrono','24 Main Title','Sean Callery'),
 ('Alerte à Malibu','I\'m Always Here','Jimi Jamison'),('The Witcher','Toss a Coin to Your Witcher','Joey Batey'),
 ('Succession','Succession (Main Title Theme)','Nicholas Britell'),('The Last of Us','The Last of Us','Gustavo Santaolalla'),
 ('True Detective','Far From Any Road','The Handsome Family'),('Westworld','Main Title Theme','Ramin Djawadi'),
 ('Sherlock','Sherlock','David Arnold'),('Downton Abbey','Downton Abbey','John Lunn'),('Le Trône de fer','Main Title','Ramin Djawadi'),
 ('K 2000','K 2000',G),('Magnum','Magnum',G),('MacGyver','MacGyver',G),('Dallas','Dallas',G),('Columbo','Columbo',G),
 ('Hélène et les Garçons','Hélène et les Garçons',G),('Plus belle la vie','Plus belle la vie',G),('Kaamelott','Kaamelott',G),
 ('Camping Paradis','Camping Paradis',G),('Joséphine ange gardien','Joséphine ange gardien',G),('Les Feux de l\'amour','Les Feux de l\'amour',G),
 ('Le Bureau des légendes','Le Bureau des légendes',G),('Lupin','Lupin',G),('Sex Education','Sex Education',G),('Euphoria','All for Us','Labrinth'),
 ('Bridgerton','Bridgerton',G),('The Crown','The Crown Main Title','Hans Zimmer'),('Lost','Lost Main Title','Michael Giacchino'),
 ('Gossip Girl','Gossip Girl',G),('Skins','Skins',G),('Hannah Montana','The Best of Both Worlds','Hannah Montana'),
]
DESSINS = [
 ('Les Simpson','The Simpsons Main Title Theme','Danny Elfman'),('Bob l\'éponge','Bob l\'éponge',G),('Les Razmoket','Les Razmoket',G),
 ('Totally Spies','Totally Spies',G),('Code Lyoko','Un monde sans danger','Code Lyoko'),('Inspecteur Gadget','Inspecteur Gadget',G),
 ('Il était une fois la vie','Il était une fois la vie',G),('Les Mystérieuses Cités d\'or','Les Mystérieuses Cités d\'or','Noam'),
 ('Ulysse 31','Ulysse 31','Lionel Leroy'),('Capitaine Flam','Capitaine Flam','Jean-Jacques Debout'),('Les Schtroumpfs','Les Schtroumpfs',G),
 ('Scooby-Doo','Scooby-Doo',G),('Les Tortues Ninja','Les Tortues Ninja',G),('Spider-Man','Spider-Man',G),
 ('La Panthère rose','The Pink Panther Theme','Henry Mancini'),('Les Pierrafeu','Les Pierrafeu',G),('Babar','Babar',G),('Oui-Oui','Oui-Oui',G),
 ('Les Aventures de Tintin','Les Aventures de Tintin',G),('Denver, le dernier dinosaure','Denver le dernier dinosaure',G),
 ('Barbapapa','Barbapapa',G),('Kid Paddle','Kid Paddle',G),('Titeuf','Titeuf',G),('Wakfu','Wakfu',G),('Winx Club','Winx Club',G),
 ('Les Bisounours','Les Bisounours',G),('Les Fous du volant','Les Fous du volant',G),('Jayce et les Conquérants de la lumière','Jayce et les conquérants de la lumière',G),
 ('Tom-Tom et Nana','Tom-Tom et Nana',G),('Martin Mystère','Martin Mystère',G),('Oggy et les Cafards','Oggy et les Cafards',G),
 ('Kim Possible','Kim Possible',G),('Phinéas et Ferb','Phinéas et Ferb',G),('Miraculous','Miraculous',G),('La Pat\' Patrouille','Pat Patrouille',G),
 ('Peppa Pig','Peppa Pig',G),('Garfield','Garfield',G),('Lucky Luke','Lucky Luke',G),('Les Mondes engloutis','Les mondes engloutis','Vladimir Cosma'),
 ('Galactik Football','Galactik Football',G),('Foot 2 Rue','Foot 2 Rue',G),('Caliméro','Caliméro',G),('Rantanplan','Rantanplan',G),
 ('Les Minikeums','Les Minikeums',G),('Diabolik','Diabolik',G),('Batman, la série animée','Batman',G),('Ratz','Ratz',G),
 ('Les Zinzins de l\'espace','Les Zinzins de l\'espace',G),('Gravity Falls','Gravity Falls',G),('Arthur','Arthur',G),('Petit Ours Brun','Petit Ours Brun',G),
 ('Tchoupi','Tchoupi',G),('Trotro','Trotro',G),('Bob le bricoleur','Bob le bricoleur',G),('Les Looney Tunes','Merrie Melodies',G),
 ('Les Tiny Toons','Tiny Toons',G),('Animaniacs','Animaniacs',G),('Les Gummi','Les Gummi',G),('Tic et Tac','Tic et Tac',G),
 ('La Bande à Picsou','La Bande à Picsou',G),('Super Mario Bros','Super Mario',G),('Sonic','Sonic',G),('Les Daltons','Les Daltons',G),
 ('Cobra','Cobra','Olivier Constantin'),('Il était une fois l\'homme','Il était une fois l\'homme',G),
]
MANGA = [
 ('Dragon Ball Z','Dragon Ball Z','Bernard Minet'),('Dragon Ball','Dragon Ball','Ariane'),('Les Chevaliers du Zodiaque','Les Chevaliers du Zodiaque','Bernard Minet'),
 ('Pokémon','Pokémon',G),('Goldorak','Goldorak','Noam'),('Albator','Albator','Eric Charden'),('Sailor Moon','Sailor Moon',G),
 ('Olive et Tom','Olive et Tom',G),('Nicky Larson','Nicky Larson','Jean-Paul Césari'),('Ken le survivant','Ken le survivant',G),
 ('Cat\'s Eyes','Signé Cat\'s Eyes','Isabelle Guillard'),('Princesse Sarah','Princesse Sarah',G),('Candy','Candy','Dorothée'),
 ('Naruto Shippuden','Blue Bird','Ikimono-gakari'),('Naruto','Haruka Kanata','Asian Kung-Fu Generation'),('One Piece','We Are!','Hiroshi Kitadani'),
 ('Yu-Gi-Oh!','Yu-Gi-Oh',G),('Digimon','Digimon',G),('Dr. Slump','Dr Slump',G),('L\'Attaque des Titans','Guren no Yumiya','Linked Horizon'),
 ('Demon Slayer','Gurenge','LiSA'),('Death Note','the WORLD','Nightmare'),('Fullmetal Alchemist','Again','YUI'),
 ('My Hero Academia','The Day','Porno Graffitti'),('Tokyo Ghoul','unravel','TK from Ling tosite sigure'),('Jujutsu Kaisen','Kaikai Kitan','Eve'),
 ('Bleach','Asterisk','Orange Range'),('Hunter x Hunter','departure!','Masatoshi Ono'),('Neon Genesis Evangelion','A Cruel Angel\'s Thesis','Yoko Takahashi'),
 ('Cowboy Bebop','Tank!','Seatbelts'),('Sword Art Online','crossing field','LiSA'),('Spy x Family','Mixed Nuts','Official HIGE DANdism'),
 ('Chainsaw Man','KICK BACK','Kenshi Yonezu'),('Oshi no Ko','Idol','YOASOBI'),('Your Name','Zenzenzense','RADWIMPS'),
 ('Le Voyage de Chihiro','One Summer\'s Day','Joe Hisaishi'),('Mon voisin Totoro','My Neighbor Totoro','Joe Hisaishi'),
 ('Le Château ambulant','Merry-Go-Round of Life','Joe Hisaishi'),('Princesse Mononoké','Princess Mononoke','Joe Hisaishi'),
 ('Haikyū!!','Imagination','SPYAIR'),('Lupin III','Theme from Lupin III','Yuji Ohno'),('Détective Conan','Détective Conan',G),
 ('Beyblade','Beyblade',G),('Hamtaro','Hamtaro',G),('Inazuma Eleven','Inazuma Eleven',G),('Dragon Ball Super','Dragon Ball Super',G),
 ('Captain Harlock','Albator 84',G),('Bioman','Bioman','Bernard Minet'),('Rémi sans famille','Rémi sans famille',G),('Heidi','Heidi',G),
 ('Astro, le petit robot','Astro le petit robot',G),('Les Mystérieuses Cités d\'or (manga)','',''),('Dragon Quest','Fly',G),
 ('Black Clover','Black Clover',G),('Fairy Tail','Fairy Tail',G),('Solo Leveling','LEveL','SawanoHiroyuki[nZk]'),
 ('Frieren','Yuusha','YOASOBI'),('Blue Lock','Chaos ga Kiwamaru','UNISON SQUARE GARDEN'),('Dandadan','Otonoke','Creepy Nuts'),
]
DISNEY = [
 ('Le Roi lion','L\'histoire de la vie','Le Roi Lion'),('Le Roi lion','Hakuna Matata','Le Roi Lion'),('Le Roi lion','L\'amour brille sous les étoiles','Le Roi Lion'),
 ('La Reine des neiges','Libérée, délivrée','Anaïs Delva'),('La Reine des neiges 2','Dans un autre monde','Charlotte Hervieux'),
 ('Aladdin','Ce rêve bleu','Aladdin'),('Aladdin','Je suis ton meilleur ami','Aladdin'),('La Petite Sirène','Sous l\'océan','La Petite Sirène'),
 ('La Petite Sirène','Partir là-bas','La Petite Sirène'),('La Belle et la Bête','Histoire éternelle','La Belle et la Bête'),
 ('Le Livre de la jungle','Il en faut peu pour être heureux','Le Livre de la jungle'),('Hercule','De zéro en héros','Hercule'),
 ('Mulan','Comme un homme','Mulan'),('Pocahontas','L\'air du vent','Pocahontas'),('Tarzan','Toujours dans mon cœur','Phil Collins'),
 ('Vaiana','Le bleu lumière','Cerise Calixte'),('Raiponce','Je veux y croire','Raiponce'),('Raiponce','Où est la vraie vie ?','Maeva Méline'),
 ('Encanto','Ne parlons pas de Bruno','Encanto'),('Coco','Ne m\'oublie pas','Coco'),('Toy Story','Je suis ton ami','Toy Story'),
 ('Les Aristochats','Tout le monde veut devenir un cat','Les Aristochats'),('Mary Poppins','Supercalifragilisticexpialidocious','Mary Poppins'),
 ('Cendrillon','Bibbidi-Bobbidi-Boo','Cendrillon'),('Blanche-Neige et les Sept Nains','Heigh-Ho','Blanche Neige'),
 ('Zootopie','Try Everything','Shakira'),('Ratatouille','Le Festin','Camille'),('Cars','Life is a Highway','Rascal Flatts'),
 ('High School Musical','Breaking Free','High School Musical'),('La Princesse et la Grenouille','Au bout du rêve','La Princesse et la Grenouille'),
 ('Le Bossu de Notre-Dame','Les Cloches de Notre-Dame','Le Bossu de Notre Dame'),('Peter Pan','Tu t\'envoles','Peter Pan'),
 ('Lilo & Stitch','Hawaiian Roller Coaster Ride','Lilo & Stitch'),('Rebelle','Libre et sauvage','Rebelle'),('Wish','Un vœu','Wish'),
 ('Les 101 Dalmatiens','Cruella d\'Enfer','101 Dalmatiens'),('La Belle au bois dormant','J\'en ai rêvé','La Belle au bois dormant'),
 ('Le Roi lion 2','Nous sommes un','Le Roi Lion 2'),('Frère des ours','Au loin','Phil Collins'),('Kuzco','Perfect World','Kuzco'),
 ('Monstres & Cie','Ensemble','Monstres et Cie'),('Toy Story 2','Quand elle m\'aimait','Toy Story 2'),('Vaiana','Pour les hommes','Vaiana'),
 ('Encanto','Sous pression','Encanto'),('La Reine des neiges','Le renne est bien meilleur que l\'homme','La Reine des Neiges'),
]
# noms anglais / espagnols des albums -> nom français de l'œuvre
ALIAS = {'frozen':'La Reine des neiges','frozen2':'La Reine des neiges 2','thelionking':'Le Roi lion','tangled':'Raiponce','moana':'Vaiana',
 'beautyandthebeast':'La Belle et la Bête','thelittlemermaid':'La Petite Sirène','hercules':'Hercule','thejunglebook':'Le Livre de la jungle',
 'zootopia':'Zootopie','despicableme':'Moi, moche et méchant','despicableme2':'Moi, moche et méchant 2','theprincessandthefrog':'La Princesse et la Grenouille',
 'backtothefuture':'Retour vers le futur','guardiansofthegalaxy':'Les Gardiens de la Galaxie','thelordoftherings':'Le Seigneur des anneaux',
 'piratesofthecaribbean':'Pirates des Caraïbes','jaws':'Les Dents de la mer','thegodfather':'Le Parrain','ghostbusters':'SOS Fantômes',
 'sleepingbeauty':'La Belle au bois dormant','snowwhiteandthesevendwarfs':'Blanche-Neige et les Sept Nains','cinderella':'Cendrillon',
 'thearistocats':'Les Aristochats','monstersinc':'Monstres & Cie','brave':'Rebelle','thehunchbackofnotredame':'Le Bossu de Notre-Dame',
 'onehundredandonedalmatians':'Les 101 Dalmatiens','101dalmatians':'Les 101 Dalmatiens','insideout':'Vice-versa','up':'Là-haut',
 'theincredibles':'Les Indestructibles','findingnemo':'Le Monde de Nemo','wreckitralph':'Les Mondes de Ralph','bigherosix':'Les Nouveaux Héros',
 'thepinkpanther':'La Panthère rose','onceuponatimeinthewest':'Il était une fois dans l\'Ouest','thegoodthebadandtheugly':'Le Bon, la Brute et le Truand',
 'harrypotterandthesorcerersstone':'Harry Potter','beverlyhillscop':'Le Flic de Beverly Hills','thebodyguard':'Bodyguard','trolls':'Les Trolls',
 'thetwilightsaga':'Twilight','wednesday':'Mercredi','etheextraterrestrial':'E.T. l\'extra-terrestre','thesilenceofthelambs':'Le Silence des agneaux',
 'house':'Dr House','thewalkingdead':'The Walking Dead','blancheneige':'Blanche-Neige et les Sept Nains','signecatseyes':'Cat\'s Eyes','thewizardofoz':'Le Magicien d\'Oz','thesoundofmusic':'La Mélodie du bonheur','starwars':'Star Wars'}
SOUND = re.compile(r'\s*[\(\[\-–:]*\s*(?:the\s+)?(?:original\s+(?:motion\s+picture\s+|television\s+|tv\s+|series\s+|broadway\s+|film\s+|amazon\s+original\s+series\s+|netflix\s+series\s+)?soundtrack|music\s+from\s+(?:the\s+)?(?:original\s+)?(?:motion\s+picture|film|series|television\s+series|netflix\s+series)|bande\s+originale|banda\s+sonora|soundtrack|b\.?o\.?f?\b|g[ée]n[ée]rique).*$', re.I)
GENERIC = re.compile(r'g[ée]n[ée]riques|best|themes?\b|hits|collection|greatest|\btop\b|\btv\b|s[ée]ries t[ée]l[ée]|ann[ée]es|\bvol\b|compil|music|songs|chansons|classics|anthology|essential|disney\s*(?:records|hits)?$|^disney|pixar$|movies?$|film$|cinema', re.I)
def clean_work(w):
    w = re.sub(r'^walt disney records the legacy collection:\s*', '', w, flags=re.I)
    w = re.sub(r'\s*[:\-–]\s*(season|saison|vol\.?|volume|part|partie)\s*\d+.*$', '', w, flags=re.I)
    w = re.sub(r'\s*[\(\[][^)\]]*[\)\]]\s*$', '', w).strip(' -–:,.')
    w = re.split(r'\s+[-–]\s+|\s*:\s+|,\s+une\s', w, maxsplit=1, flags=re.I)[0].strip(' -–:,.')  # sous-titre
    k = norm(w)
    return ALIAS.get(k, w)
def wkey(w): return norm(re.sub(r'\d+', '', w))
def derive(t):
    """œuvre d'un son des anciennes playlists, seulement si c'est clair (album « X (Original Motion Picture Soundtrack) », titre « … (from "X") »)"""
    m = re.search(r'from (?:the )?(?:\w+ )?["“«]\s*([^"”»]{2,40})\s*["”»]', t[1], re.I)
    if m: return clean_work(m.group(1))
    al = t[4] or ''
    m = SOUND.search(al)
    if not m or m.start() < 2: return None
    w = clean_work(al[:m.start()])
    if not (3 <= len(w) <= 40) or len(norm(w)) < 4 or GENERIC.search(w) or JUNK.search(w) or '(' in w or norm(w) == norm(t[0]): return None
    return w
JUNK = re.compile(r'^les?$|^les meilleur|^\\d|pegi|chanson|^le vrai|club du mercredi|special edition', re.I)
GEN_OK = re.compile(r'bernardminet|noam|dorothee|jeanpaulcesari|ariane|lionelleroy|ericcharden|toptv80|generiques|clubdorothee|jeanjacquesdebout|isabelleguillard|henrymancini|hiroshikitadani', re.I)
def find(title, hint, work):
    want = base(title); gen = hint == G
    queries = [f'{title} générique', f'{work} générique'] if gen else [f'artist:"{hint}" track:"{title}"', f'{title} {hint}', f'{title} {work}']
    for q in queries:
        time.sleep(0.12)
        best = None
        for t in get(API + '/search', {'q': q, 'limit': 15}).get('data', []):
            if not t.get('preview') or not t.get('readable', True): continue
            full = t['title'] + ' ' + t['artist']['name'] + ' ' + t.get('album', {}).get('title', '')
            if BAD.search(full): continue
            tt = base(t['title']) + norm(t.get('album', {}).get('title', ''))
            if want[:12] not in tt and base(t['title'])[:12] not in want: continue
            if gen and not (re.search(r'generique|theme|opening|dessinanime|serie|tv|ost|anime', norm(full)) or GEN_OK.search(norm(t['artist']['name']))): continue
            if not gen and norm(hint)[:6] not in norm(full) and norm(work)[:6] not in norm(full): continue
            score = (norm(hint)[:8] in norm(full)) * 2 + (base(t['title']) == want) + (norm(work)[:8] in norm(full))
            if best is None or score > best[0]: best = (score, t)
        if best: return best[1]
    return None
DKEYS = {wkey(w) for w, _, _ in DESSINS}
MKEYS = {wkey(w) for w, _, _ in MANGA} | {'dragonballz', 'goldorak', 'catseyes', 'naruto', 'albator'}
def build(old):
    """old : {clé: anciens sons} ; renvoie les playlists œuvres"""
    spec = [('films', 'Films et séries', '🎬', FILMS + SERIES, ['films']), ('dessins', 'Dessins animés', '🧸', DESSINS, ['dessins']),
            ('manga', 'Manga et animés', '🍥', MANGA, []), ('disney', 'Disney', '✨', DISNEY, ['disney'])]
    out = []
    for key, name, emo, items, olds in spec:
        got, ids = [], set()
        for work, title, hint in items:
            if not title: continue
            t = find(title, hint, work)
            if not t or t['id'] in ids: print('  introuvable :', name, '|', work, '|', title); continue
            ids.add(t['id'])
            got.append([t['artist']['name'], t['title_short'] or t['title'], t['id'], t.get('md5_image', ''), t.get('album', {}).get('title', ''), work])
        n0 = len(got)
        per = {}
        for x in got: per[wkey(x[5])] = per.get(wkey(x[5]), 0) + 1
        for k in olds:
            for t in old.get(k, []):
                if t[2] in ids or len(got) >= 400: continue
                w = derive(t)
                if not w: continue
                kw = wkey(w)
                # dessins : seulement les œuvres connues de la liste (les séries télé « live » des compilations sont écartées)
                if key == 'dessins' and kw not in DKEYS: continue
                if key != 'manga' and kw in MKEYS: continue  # les animés japonais vont dans Manga
                if kw in ('wicked', 'zombies', 'freedom', 'retrospective', 'theisland', 'bangbangluckyluke'): continue
                if per.get(kw, 0) >= (6 if key == 'disney' else 3): continue  # pas 28 sons du même film
                per[kw] = per.get(kw, 0) + 1
                ids.add(t[2]); got.append(t[:5] + [w])
        canon = {}
        for x in got: x[5] = canon.setdefault(wkey(x[5]) + str(re.findall(r'\d+', x[5])), x[5])  # même nom partout
        works = {wkey(x[5]) for x in got}
        print(f'{name} : {n0} à la main + {len(got)-n0} des anciennes playlists, {len(works)} œuvres', flush=True)
        if len(got) >= 20 and len(works) >= 8: out.append([key, name, emo, got])
    return out
def merge(db, extra):
    keys = {x[0] for x in extra}; pos = {x[0]: i for i, x in enumerate(db.get('l', []))}
    l = list(db.get('l', []))
    for x in extra:
        if x[0] in pos: l[pos[x[0]]] = x
        else: l.append(x)
    db['l'] = l
if __name__ == '__main__':
    db = json.load(open('../db.json'))
    old = {x[0]: x[3] for x in db.get('l', [])}
    merge(db, build(old))
    open('../db.json', 'w').write(json.dumps(db, ensure_ascii=False, separators=(',', ':')))
