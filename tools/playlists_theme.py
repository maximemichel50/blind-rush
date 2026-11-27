"""Playlists à thème : ajoute la clé "l" à ../db.json.

Chaque playlist est une liste de (titre, artiste). Le script cherche chaque morceau sur Deezer
et garde le premier résultat qui a un extrait et dont le titre correspond.
Format ajouté dans db.json :
  "l": [[clé, nom, emoji, [[artiste, titre, idDeezer, hashPochette, album], ...]], ...]
Lancé par le workflow "publier" quand le message du commit contient [playlists] (ou [reconstruire]).
Pour ajouter une playlist : copier un bloc ci-dessous, changer la clé, le nom et les morceaux.
"""
import json, os, re, sys, time, unicodedata
import requests

PLAYLISTS = [
 ('dessins', 'Génériques de dessins animés', '🧸', [
  ('Les Chevaliers du Zodiaque', 'Bernard Minet'), ('Dragon Ball Z', 'Bernard Minet'), ('Dragon Ball', 'Ariane'),
  ('Pokémon', 'Jean-Marc Anthony Kabeya'), ('Goldorak', 'Noam'), ('Albator', 'Eric Charden'),
  ('Capitaine Flam', 'Jean-Jacques Debout'), ('Les Mystérieuses Cités d\'Or', 'Noam'), ('Ulysse 31', 'Lionel Leroy'),
  ('Il était une fois la vie', 'générique'), ('Inspecteur Gadget', 'générique'), ('Olive et Tom', 'générique'),
  ('Sailor Moon', 'générique'), ('Code Lyoko', 'générique'), ('Les Razmoket', 'générique'),
  ('Totally Spies', 'générique'), ('Bob l\'éponge', 'générique'), ('Les Simpson', 'Danny Elfman'),
  ('Bioman', 'Bernard Minet'), ('Nicky Larson', 'Jean-Paul Césari'), ('Ken le survivant', 'générique'),
  ('Princesse Sarah', 'générique'), ('Rémi sans famille', 'générique'), ('Heidi', 'générique'),
  ('Les Tortues Ninja', 'générique'), ('Digimon', 'générique'), ('Yu-Gi-Oh', 'générique'),
  ('Jayce et les conquérants de la lumière', 'générique'), ('Candy', 'Dorothée'), ('Les Schtroumpfs', 'générique'),
  ('Scooby-Doo', 'générique'), ('Les Bisounours', 'générique'),
  ('Denver le dernier dinosaure', 'générique'), ('Cat\'s Eyes', 'générique'), ('Tom-Tom et Nana', 'générique'),
  ('Barbapapa', 'générique'), ('Winx Club', 'générique'), ('Kid Paddle', 'générique'), ('Titeuf', 'générique'),
  ('Wakfu', 'générique'), ('Naruto', 'générique'), ('One Piece', 'générique'), ('Spider-Man', 'générique'),
  ('Les Fous du volant', 'générique'), ('La Panthère rose', 'Henry Mancini'), ('Les Pierrafeu', 'générique'),
  ('Babar', 'générique'), ('Oui-Oui', 'générique'), ('Les Aventures de Tintin', 'générique')]),

 ('ete2010', 'Tubes des étés 2010', '☀️', [
  ('Waka Waka (This Time for Africa)', 'Shakira'), ('Bumpy Ride', 'Mohombi'), ('Hot', 'Inna'), ('Alors on danse', 'Stromae'),
  ('We No Speak Americano', 'Yolanda Be Cool'), ('I Gotta Feeling', 'Black Eyed Peas'), ('Memories', 'David Guetta'),
  ('California Gurls', 'Katy Perry'), ('Only Girl (In the World)', 'Rihanna'), ('TiK ToK', 'Kesha'),
  ('Dynamite', 'Taio Cruz'), ('I Like It', 'Enrique Iglesias'), ('Give Me Everything', 'Pitbull'),
  ('Party Rock Anthem', 'LMFAO'), ('Danza Kuduro', 'Don Omar'), ('Ai Se Eu Te Pego', 'Michel Teló'),
  ('Somebody That I Used to Know', 'Gotye'), ('Call Me Maybe', 'Carly Rae Jepsen'), ('Gangnam Style', 'PSY'),
  ('Désolé', 'Sexion d\'Assaut'), ('Même pas fatigué', 'Magic System'), ('Sun Is Up', 'Inna'),
  ('Mr. Saxobeat', 'Alexandra Stan'), ('Stereo Love', 'Edward Maya'), ('Just the Way You Are', 'Bruno Mars'),
  ('DJ Got Us Fallin\' in Love', 'Usher'), ('Club Can\'t Handle Me', 'Flo Rida'), ('Good Feeling', 'Flo Rida'),
  ('Whistle', 'Flo Rida'), ('Feel So Close', 'Calvin Harris'), ('Levels', 'Avicii'), ('Wake Me Up', 'Avicii'),
  ('Don\'t You Worry Child', 'Swedish House Mafia'), ('Get Lucky', 'Daft Punk'), ('Happy', 'Pharrell Williams'),
  ('Papaoutai', 'Stromae'), ('J\'me tire', 'Maître Gims'), ('Laisse-toi aller bébé', 'Collectif Métissé'),
  ('Je veux', 'Zaz'), ('C\'est la vie', 'Khaled'), ('Titanium', 'David Guetta'), ('On the Floor', 'Jennifer Lopez'),
  ('Rabiosa', 'Shakira'), ('Moves Like Jagger', 'Maroon 5'), ('Sexy and I Know It', 'LMFAO'),
  ('Starships', 'Nicki Minaj'), ('We Found Love', 'Rihanna'), ('Payphone', 'Maroon 5'), ('Wild Ones', 'Flo Rida'),
  ('Turn Me On', 'David Guetta'), ('Tacatà', 'Tacabro'), ('Balada (Tchê tcherere tchê tchê)', 'Gusttavo Lima')]),

 ('top50', 'Top 50 français', '🇫🇷', [
  ('Voyage, voyage', 'Desireless'), ('L\'aventurier', 'Indochine'), ('Quand la musique est bonne', 'Jean-Jacques Goldman'),
  ('Week-end à Rome', 'Etienne Daho'), ('Les démons de minuit', 'Images'), ('Capitaine abandonné', 'Gold'),
  ('Besoin de rien, envie de toi', 'Peter et Sloane'), ('Toute première fois', 'Jeanne Mas'), ('Nuit de folie', 'Début de Soirée'),
  ('Casser la voix', 'Patrick Bruel'), ('Libertine', 'Mylène Farmer'), ('Banana Split', 'Lio'), ('T\'en va pas', 'Elsa'),
  ('Joe le taxi', 'Vanessa Paradis'), ('Lambada', 'Kaoma'), ('Les valses de Vienne', 'François Feldman'),
  ('Je te survivrai', 'Jean-Pierre François'), ('Partenaire particulier', 'Partenaire Particulier'),
  ('L\'amour à la plage', 'Niagara'), ('Marcia Baila', 'Les Rita Mitsouko'), ('L\'Aziza', 'Daniel Balavoine'),
  ('Ella, elle l\'a', 'France Gall'), ('Foule sentimentale', 'Alain Souchon'), ('Oui je l\'adore', 'Pauline Ester'),
  ('Mademoiselle chante le blues', 'Patricia Kaas'), ('N\'importe quoi', 'Florent Pagny'), ('Femme libérée', 'Cookie Dingler'),
  ('Cœur de loup', 'Philippe Lafontaine'), ('On va s\'aimer', 'Gilbert Montagné'), ('Ouragan', 'Stéphanie'),
  ('Belle-Île-en-Mer, Marie-Galante', 'Laurent Voulzy'), ('Chante', 'Les Forbans'), ('Mise au point', 'Jakie Quartz'),
  ('Cargo', 'Axel Bauer'), ('Une femme avec une femme', 'Mecano'), ('Maldòn', 'Zouk Machine'),
  ('Viens boire un p\'tit coup à la maison', 'Licence IV'), ('Hélène', 'Roch Voisine'), ('Pour que tu m\'aimes encore', 'Céline Dion'),
  ('Pourvu qu\'elles soient douces', 'Mylène Farmer'), ('Aux sombres héros de l\'amer', 'Noir Désir'),
  ('Femme que j\'aime', 'Jean-Luc Lahaye'), ('Ça fait rire les oiseaux', 'La Compagnie Créole'), ('Il jouait du piano debout', 'France Gall'),
  ('Tombé pour la France', 'Etienne Daho'), ('Ville de lumière', 'Gold'), ('Nathalie', 'Gilbert Bécaud'),
  ('Ne me quitte pas', 'Jacques Brel'), ('Les Lacs du Connemara', 'Michel Sardou'), ('Le Sud', 'Nino Ferrer')]),

 ('films', 'Musiques de films', '🎬', [
  ('My Heart Will Go On', 'Céline Dion'), ('I Will Always Love You', 'Whitney Houston'), ('Eye of the Tiger', 'Survivor'),
  ('Danger Zone', 'Kenny Loggins'), ('(I\'ve Had) The Time of My Life', 'Bill Medley'), ('Ghostbusters', 'Ray Parker Jr.'),
  ('Flashdance... What a Feeling', 'Irene Cara'), ('Stayin\' Alive', 'Bee Gees'), ('(Everything I Do) I Do It for You', 'Bryan Adams'),
  ('I Don\'t Want to Miss a Thing', 'Aerosmith'), ('Don\'t You (Forget About Me)', 'Simple Minds'), ('Take My Breath Away', 'Berlin'),
  ('Footloose', 'Kenny Loggins'), ('The Power of Love', 'Huey Lewis & The News'), ('Skyfall', 'Adele'),
  ('Lose Yourself', 'Eminem'), ('Shallow', 'Lady Gaga'), ('Gangsta\'s Paradise', 'Coolio'), ('Men in Black', 'Will Smith'),
  ('See You Again', 'Wiz Khalifa'), ('Can\'t Stop the Feeling!', 'Justin Timberlake'), ('Chariots of Fire', 'Vangelis'),
  ('Comptine d\'un autre été, l\'après-midi', 'Yann Tiersen'), ('Misirlou', 'Dick Dale'), ('You Never Can Tell', 'Chuck Berry'),
  ('Oh, Pretty Woman', 'Roy Orbison'), ('Stand by Me', 'Ben E. King'), ('Let It Go', 'Idina Menzel'),
  ('Mrs. Robinson', 'Simon & Garfunkel'), ('Goldfinger', 'Shirley Bassey'), ('Live and Let Die', 'Paul McCartney'),
  ('Unchained Melody', 'The Righteous Brothers'), ('Twist and Shout', 'The Beatles'), ('Kiss from a Rose', 'Seal'),
  ('Everybody\'s Talkin\'', 'Harry Nilsson'), ('Born to Be Wild', 'Steppenwolf'), ('Mad World', 'Gary Jules'),
  ('Lady Marmalade', 'Christina Aguilera'), ('Up Where We Belong', 'Joe Cocker'), ('Writing\'s on the Wall', 'Sam Smith'),
  ('Shape of My Heart', 'Sting'), ('Little Green Bag', 'George Baker Selection'), ('Old Time Rock & Roll', 'Bob Seger'),
  ('A Thousand Years', 'Christina Perri'), ('Spirit in the Sky', 'Norman Greenbaum'), ('City of Stars', 'Ryan Gosling'),
  ('Le Temps des cerises', 'Yves Montand'), ('La Valse d\'Amélie', 'Yann Tiersen'), ('Danse avec les loups', 'John Barry'),
  ('Star Wars (Main Title)', 'John Williams'), ('The Imperial March', 'John Williams'), ('Raiders March', 'John Williams'),
  ('Theme From Jurassic Park', 'John Williams'), ('Hedwig\'s Theme', 'John Williams'), ('Flying Theme', 'John Williams'),
  ('Theme From Schindler\'s List', 'John Williams'), ('He\'s a Pirate', 'Klaus Badelt'), ('Time', 'Hans Zimmer'),
  ('Now We Are Free', 'Hans Zimmer'), ('Cornfield Chase', 'Hans Zimmer'), ('The Godfather Waltz', 'Nino Rota'),
  ('The Good, the Bad and the Ugly', 'Ennio Morricone'), ('Chi Mai', 'Ennio Morricone'), ('Gabriel\'s Oboe', 'Ennio Morricone'),
  ('Once Upon a Time in the West', 'Ennio Morricone'), ('Gonna Fly Now', 'Bill Conti'), ('Back to the Future', 'Alan Silvestri'),
  ('Concerning Hobbits', 'Howard Shore'), ('The Pink Panther Theme', 'Henry Mancini'), ('James Bond Theme', 'Monty Norman'),
  ('Hymn to the Sea', 'James Horner'), ('Axel F', 'Harold Faltermeyer'), ('Top Gun Anthem', 'Harold Faltermeyer'),
  ('Lux Aeterna', 'Clint Mansell'), ('The Batman Theme', 'Danny Elfman'), ('Married Life', 'Michael Giacchino'),
  ('Jai Ho', 'A.R. Rahman'), ('All Star', 'Smash Mouth'), ('Accidentally in Love', 'Counting Crows'), ('Happy', 'Pharrell Williams'),
  ('You\'re the One That I Want', 'John Travolta'), ('Summer Nights', 'John Travolta'), ('Hungry Eyes', 'Eric Carmen'),
  ('Son of a Preacher Man', 'Dusty Springfield'), ('Another Day of Sun', 'La La Land'), ('This Is Me', 'Keala Settle'),
  ('Rewrite the Stars', 'Zac Efron'), ('Vois sur ton chemin', 'Les Choristes'), ('Reality', 'Richard Sanderson'),
  ('Mission: Impossible Theme', 'Lalo Schifrin'), ('My Name Is Lincoln', 'Steve Jablonsky'), ('Duel of the Fates', 'John Williams'),
  ('Oogway Ascends', 'Hans Zimmer'), ('Main Theme (Pirates of the Caribbean)', 'Hans Zimmer'), ('Kung Fu Fighting', 'Carl Douglas'),
  ('What a Wonderful World', 'Louis Armstrong'), ('Holding Out for a Hero', 'Bonnie Tyler'), ('Try Everything', 'Shakira'),
  ('Ghostbusters', 'Ray Parker'), ('Old Town Road', 'Lil Nas X'), ('Bad to the Bone', 'George Thorogood'), ('Oh Yeah', 'Yello'),
  ('Ce n\'est qu\'un au revoir', 'Les Bronzés'), ('Le Grand Bleu', 'Eric Serra'), ('Il était une fois dans l\'Ouest', 'Ennio Morricone')]),

 ('series', 'Génériques de séries', '📺', [
  ('I\'ll Be There for You', 'The Rembrandts'), ('Main Title', 'Ramin Djawadi'), ('Stranger Things', 'Kyle Dixon'),
  ('The X-Files', 'Mark Snow'), ('Twin Peaks Theme', 'Angelo Badalamenti'), ('Woke Up This Morning', 'Alabama 3'),
  ('Bella Ciao', 'Manu Pilas'), ('Breaking Bad Main Title Theme', 'Dave Porter'), ('The Simpsons Theme', 'Danny Elfman'),
  ('Red Right Hand', 'Nick Cave'), ('Tuyo', 'Rodrigo Amarante'), ('The Game Is On', 'David Arnold'), ('Doctor Who Theme', 'Murray Gold'),
  ('Downton Abbey', 'John Lunn'), ('Westworld Main Title', 'Ramin Djawadi'), ('The Crown Main Title', 'Hans Zimmer'),
  ('Succession', 'Nicholas Britell'), ('Save Me', 'Remy Zero'), ('Teardrop', 'Massive Attack'), ('Bad Things', 'Jace Everett'),
  ('Far From Any Road', 'The Handsome Family'), ('Hawaii Five-O', 'The Ventures'), ('Magnum P.I.', 'Mike Post'),
  ('The A-Team', 'Mike Post'), ('Miami Vice Theme', 'Jan Hammer'), ('I\'m Always Here', 'Jimi Jamison'),
  ('How Soon Is Now?', 'Love Spit Love'), ('Sex and the City', 'Douglas J. Cuomo'), ('Desperate Housewives', 'Danny Elfman'),
  ('Cosy in the Rocket', 'Psapp'), ('California', 'Phantom Planet'), ('I Don\'t Want to Be', 'Gavin DeGraw'), ('Superman', 'Lazlo Bane'),
  ('Boss of Me', 'They Might Be Giants'), ('Hey Beautiful', 'The Solids'), ('History of Everything', 'Barenaked Ladies'),
  ('The Fresh Prince of Bel-Air', 'DJ Jazzy Jeff'), ('Happy Days', 'Pratt & McClain'), ('The Twilight Zone', 'Marius Constant'),
  ('The Walking Dead Main Title', 'Bear McCreary'), ('If I Had a Heart', 'Fever Ray'), ('Way Back Then', 'Jung Jae Il'),
  ('Goo Goo Muck', 'The Cramps'), ('Dexter Main Title', 'Rolfe Kent'), ('Lost Main Title', 'Michael Giacchino'),
  ('Prison Break Main Title', 'Ramin Djawadi'), ('Searchin\' My Soul', 'Vonda Shepard'), ('Buffy the Vampire Slayer Theme', 'Nerf Herder'),
  ('All for Us', 'Labrinth'), ('The Office', 'The Scrantones'), ('Seinfeld', 'Jonathan Wolff'), ('Better Call Saul', 'Little Barrie'),
  ('The Mandalorian', 'Ludwig Göransson'), ('House of the Dragon', 'Ramin Djawadi'), ('Enemy', 'Imagine Dragons'),
  ('A Beautiful Mine', 'RJD2'), ('Running Up That Hill', 'Kate Bush'), ('Gotham', 'générique'), ('Friends', 'générique'),
  ('Plus belle la vie', 'générique'), ('Kaamelott', 'générique'), ('Les Brigades du Tigre', 'Claude Bolling'),
  ('Pour l\'amour d\'un garçon', 'Hélène Rollès'), ('Navarro', 'générique'), ('Joséphine ange gardien', 'générique'),
  ('Dallas', 'générique'), ('Mission: Impossible', 'Lalo Schifrin'), ('MacGyver', 'générique'), ('Charmed', 'générique'),
  ('Le Bureau des légendes', 'générique'), ('Lupin', 'générique'), ('Narcos', 'générique'), ('Peaky Blinders', 'générique'),
  ('Squid Game', 'générique'), ('Mercredi', 'générique'), ('Vikings', 'générique'), ('La Casa de Papel', 'générique')]),

 ('disney', 'Chansons Disney', '✨', [
  ('Libérée, délivrée', 'Anaïs Delva'), ('Hakuna Matata', 'Le Roi Lion'), ('Je voudrais déjà être roi', 'Le Roi Lion'),
  ('L\'histoire de la vie', 'Le Roi Lion'), ('L\'amour brille sous les étoiles', 'Le Roi Lion'),
  ('Il en faut peu pour être heureux', 'Le Livre de la jungle'), ('Sous l\'océan', 'Henri Salvador'),
  ('Partir là-bas', 'La Petite Sirène'), ('Ce rêve bleu', 'Aladdin'), ('Prince Ali', 'Aladdin'), ('Je suis ton ami', 'Charlélie Couture'),
  ('Tout le monde veut devenir un cat', 'Les Aristochats'), ('Bibbidi-Bobbidi-Boo', 'Cendrillon'),
  ('Un jour mon prince viendra', 'Blanche-Neige'), ('Histoire éternelle', 'La Belle et la Bête'), ('C\'est la fête', 'La Belle et la Bête'),
  ('L\'Air du vent', 'Pocahontas'), ('Comme un homme', 'Mulan'), ('Réflexion', 'Mulan'), ('De zéro en héros', 'Hercule'),
  ('Le bleu lumière', 'Vaiana'), ('Pour les hommes', 'Vaiana'), ('Bienvenue', 'Vaiana'), ('Ne parlons pas de Bruno', 'Encanto'),
  ('Supercalifragilisticexpialidocious', 'Mary Poppins'), ('Où est la vraie vie', 'Raiponce'), ('Heigh-Ho', 'Blanche-Neige'),
  ('En été', 'La Reine des neiges'), ('Dans un autre monde', 'La Reine des neiges 2'), ('Je veux y croire', 'Raiponce'),
  ('Belle', 'La Belle et la Bête'), ('Je suis ton meilleur ami', 'Aladdin'),
  ('Il suffit d\'un peu de sucre', 'Mary Poppins'), ('Etre un homme comme vous', 'Le Livre de la jungle'),
  ('Au-delà de l\'horizon', 'Vaiana'), ('L\'Amour est un pays sans fin', 'Pocahontas'),
  ('Je veux savoir', 'Tarzan'), ('Toujours dans mon cœur', 'Tarzan'), ('Remember Me', 'Coco'), ('La Bella Notte', 'La Belle et le Clochard'),
  ('Hakuna Matata', 'The Lion King'), ('Circle of Life', 'The Lion King'), ('I Just Can\'t Wait to Be King', 'The Lion King'),
  ('Be Prepared', 'The Lion King'), ('Can You Feel the Love Tonight', 'Elton John'), ('Let It Go', 'Frozen'),
  ('Do You Want to Build a Snowman?', 'Frozen'), ('Into the Unknown', 'Frozen'), ('Show Yourself', 'Frozen'),
  ('A Whole New World', 'Aladdin'), ('Friend Like Me', 'Aladdin'), ('Prince Ali', 'Aladdin'), ('Under the Sea', 'Little Mermaid'),
  ('Part of Your World', 'Little Mermaid'), ('Kiss the Girl', 'Little Mermaid'), ('Be Our Guest', 'Beauty and the Beast'),
  ('Beauty and the Beast', 'Beauty and the Beast'), ('Gaston', 'Beauty and the Beast'), ('Go the Distance', 'Hercules'),
  ('Zero to Hero', 'Hercules'), ('Colors of the Wind', 'Pocahontas'), ('Reflection', 'Mulan'), ('I\'ll Make a Man Out of You', 'Mulan'),
  ('The Bare Necessities', 'Jungle Book'), ('I Wan\'na Be Like You', 'Jungle Book'), ('Supercalifragilisticexpialidocious', 'Mary Poppins'),
  ('Chim Chim Cher-ee', 'Mary Poppins'), ('A Spoonful of Sugar', 'Mary Poppins'), ('Bibbidi-Bobbidi-Boo', 'Cinderella'),
  ('When You Wish Upon a Star', 'Pinocchio'), ('Heigh-Ho', 'Snow White'), ('Everybody Wants to Be a Cat', 'Aristocats'),
  ('We Don\'t Talk About Bruno', 'Encanto'), ('Surface Pressure', 'Encanto'), ('How Far I\'ll Go', 'Moana'), ('You\'re Welcome', 'Moana'),
  ('Shiny', 'Moana'), ('I See the Light', 'Tangled'), ('When Will My Life Begin', 'Tangled'), ('Un Poco Loco', 'Coco'),
  ('You\'ve Got a Friend in Me', 'Randy Newman'), ('Strangers Like Me', 'Phil Collins'), ('You\'ll Be in My Heart', 'Phil Collins'),
  ('Two Worlds', 'Phil Collins'), ('Almost There', 'Princess and the Frog'), ('Cruella De Vil', '101'), ('Once Upon a Dream', 'Sleeping Beauty'),
  ('Cups', 'Anna Kendrick')]),

 ('club', 'Boîte de nuit', '🕺', [
  ('Mwaki', 'Zerb'), ('Houdini', 'Dua Lipa'), ('Training Season', 'Dua Lipa'), ('Espresso', 'Sabrina Carpenter'),
  ('Miracle', 'Calvin Harris'), ('I\'m Good (Blue)', 'David Guetta'), ('(It Goes Like) Nanana', 'Peggy Gou'),
  ('Delilah (pull me out of this)', 'Fred again..'), ('The Business', 'Tiësto'), ('10:35', 'Tiësto'),
  ('Tití Me Preguntó', 'Bad Bunny'), ('DtMF', 'Bad Bunny'), ('Bzrp Music Sessions, Vol. 53', 'Shakira'),
  ('Quevedo: Bzrp Music Sessions, Vol. 52', 'Bizarrap'), ('Provenza', 'Karol G'), ('Si Antes Te Hubiera Conocido', 'Karol G'),
  ('Calm Down', 'Rema'), ('Water', 'Tyla'), ('Pookie', 'Aya Nakamura'), ('Djadja', 'Aya Nakamura'), ('Meuda', 'Tiakola'),
  ('Bolide allemand', 'SDM'), ('Notre Dame', 'Gazo'), ('Die', 'Gazo'), ('Solitaire', 'Werenoi'), ('4 Kampé', 'Joé Dwèt Filé'),
  ('Kongolese sous BBL', 'Theodora'), ('APT.', 'ROSÉ'), ('Hot To Go!', 'Chappell Roan'), ('Not Like Us', 'Kendrick Lamar'),
  ('Head & Heart', 'Joel Corry'), ('Drugs From Amsterdam', 'Mau P'), ('One Kiss', 'Calvin Harris'), ('Greedy', 'Tate McRae'),
  ('Paint The Town Red', 'Doja Cat'), ('Strangers', 'Kenya Grace'), ('Escapism.', 'RAYE'), ('LALA', 'Myke Towers'),
  ('Last Last', 'Burna Boy'), ('Rush', 'Ayra Starr'), ('N\'y pense plus', 'Tayc'), ('La kiffance', 'Naps'),
  ('Suavemente', 'Soolking'), ('Shake It To The Max (FLY)', 'MOLIY'), ('A Bar Song (Tipsy)', 'Shaboozey'),
  ('Where Are You Now', 'Lost Frequencies'), ('DON\'T YOU WORRY', 'Black Eyed Peas'), ('Tchikita', 'Jul'),
  ('Baby Don\'t Hurt Me', 'David Guetta'), ('Padam Padam', 'Kylie Minogue'), ('Flowers', 'Miley Cyrus'),
  ('Gasolina', 'Daddy Yankee'), ('Dakiti', 'Bad Bunny'), ('Tsunami', 'DVBBS'), ('Ciel', 'GIMS'), ('Sois pas timide', 'GIMS')]),

 ('soiree', 'Tubes de soirée', '🪩', [
  ('Macarena', 'Los Del Rio'), ('Aserejé', 'Las Ketchup'), ('Dragostea din tei', 'O-Zone'), ('Saturday Night', 'Whigfield'),
  ('Mambo No. 5', 'Lou Bega'), ('Barbie Girl', 'Aqua'), ('Tic tic tac', 'Carrapicho'), ('Le lion est mort ce soir', 'Pow Woow'),
  ('Les sardines', 'Patrick Sébastien'), ('La danse des canards', 'J.J. Lionel'), ('Gasolina', 'Daddy Yankee'),
  ('Y.M.C.A.', 'Village People'), ('I Will Survive', 'Gloria Gaynor'), ('Freed from Desire', 'Gala'), ('Blue (Da Ba Dee)', 'Eiffel 65'),
  ('Rhythm Is a Dancer', 'Snap!'), ('What Is Love', 'Haddaway'), ('Cotton Eye Joe', 'Rednex'), ('Call on Me', 'Eric Prydz'),
  ('Moi... Lolita', 'Alizée'), ('Femme Like U', 'K-Maro'), ('La tribu de Dana', 'Manau'), ('Allumer le feu', 'Johnny Hallyday'),
  ('Dancing Queen', 'ABBA'), ('September', 'Earth, Wind & Fire'), ('Uptown Funk', 'Mark Ronson'), ('Despacito', 'Luis Fonsi'),
  ('Jerusalema', 'Master KG'), ('Wannabe', 'Spice Girls'), ('La chenille', 'La Bande à Basile'), ('Le bal masqué', 'La Compagnie Créole'),
  ('C\'est bon pour le moral', 'La Compagnie Créole'), ('Pour un flirt', 'Michel Delpech'), ('Le Madison', 'Claude François'),
  ('Alexandrie Alexandra', 'Claude François'), ('Born to Be Alive', 'Patrick Hernandez'), ('Daddy Cool', 'Boney M.'),
  ('Rasputin', 'Boney M.'), ('Gimme! Gimme! Gimme!', 'ABBA'), ('Mr. Brightside', 'The Killers'), ('Sex on Fire', 'Kings of Leon'),
  ('Seven Nation Army', 'The White Stripes'), ('Get Down Saturday Night', 'Oliver Cheatham'), ('Ça plane pour moi', 'Plastic Bertrand'),
  ('Tout le monde danse', 'Big Ali'), ('Bella', 'Maître Gims'), ('Djadja', 'Aya Nakamura'), ('Tchiki Tchiki', 'Jessy Matador'),
  ('Allez Ola Olé', 'Jessy Matador'), ('Zumba He Zumba Ha', 'DJ Mam\'s'), ('Danse', 'Tal')]),
]

API = 'https://api.deezer.com'
BAD = re.compile(r'karaok|instrumental|remix|8 ?-?bit|lofi|lo-fi|\brap\b|parod|made famous|in the style|originally performed|tribute|reprise de|cover|8-bit|lullaby|berceuse|piano version', re.I)
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

# chanteurs de génériques connus (pour accepter un générique sans le mot « générique »)
GEN_OK = re.compile(r'bernardminet|noam|dorothee|jacquescardona|jeanpaulcesari|ariane|lionelleroy|ericcharden|michellegrand|henriseroka|toptv80|generiques|clubdorothee|chantalgoya|jeanjacquesdebout|claudelombard|isabelleguillard|alexandra|romariclaurence|henrymancini|hiroshikitadani|ouioui|winx', re.I)
def find(title, hint):
    want = base(title)
    gen = hint == 'générique'
    queries = [f'{title} générique', f'{title} générique dessin animé'] if gen else [f'artist:"{hint}" track:"{title}"', f'{title} {hint}']
    for q in queries:
        time.sleep(0.15)
        res = get(API + '/search', {'q': q, 'limit': 15}).get('data', [])
        best = None
        for t in res:
            if not t.get('preview') or not t.get('readable', True): continue
            full = t['title'] + ' ' + t['artist']['name'] + ' ' + t.get('album', {}).get('title', '')
            if BAD.search(full): continue
            tt = base(t['title']) + norm(t.get('album', {}).get('title', ''))
            if want[:14] not in tt and base(t['title'])[:14] not in want: continue
            if gen:
                if not (re.search(r'g.n.rique|theme|opening|dessin|serie|tv', norm(full)) or GEN_OK.search(norm(t['artist']['name']))): continue
            elif norm(hint)[:6] not in norm(t['artist']['name'] + ' ' + t.get('album', {}).get('title', '')) and not (len(norm(hint)) < 6 and norm(hint) in norm(full)):
                if not GEN_OK.search(norm(t['artist']['name'])): continue
            score = (norm(hint)[:8] in norm(full)) * 2 + (base(t['title']) == want)
            if best is None or score > best[0]: best = (score, t)
        if best: return best[1]
    return None

# En plus de la liste à la main : les titres de grosses playlists Deezer du même thème (éditeurs Deezer d'abord)
EXTRA = {
 'club': ['hits club', 'boite de nuit', 'dancefloor hits', 'club hits 2025', 'afro club', 'reggaeton hits', 'rap fr club', 'dancefloor 2025'],
 'soiree': ['tubes soirée', 'soirée années 80', 'hits années 2000', 'tubes de mariage'],
 'top50': ['top france', 'hits du moment', 'top 50 france'],
 'ete2010': ['tubes été 2010', 'hits 2010', 'hits 2011', 'hits 2012'],
 'disney': ['disney chansons françaises', 'disney en français', 'disney hits', 'chansons disney', 'disney classiques', 'pixar'],
 'dessins': ['génériques dessins animés', 'génériques dessins animés années 80', 'génériques dessins animés années 90', 'club dorothée', 'génériques mangas', 'génériques enfance'],
 'series': ['génériques séries', 'séries tv', 'tv themes', 'génériques séries culte', 'series soundtrack', 'génériques séries années 80'],
 'films': ['musiques de films cultes', 'bandes originales films', 'movie themes', 'film soundtrack', 'musique de film', 'cinéma'],
}
CAP = int(os.environ.get('CAP_PLAYLIST', '200'))
# une playlist Deezer n'est prise que si son nom colle au thème
KW = {
 'club': r'club|danc|boite|nightclub|reggaeton|afrobeat|amapiano|banger|clubbing',
 'soiree': r'soiree|fete|mariage|party|annees80|annees2000|80s|tubes',
 'top50': r'top50|topfrance|top100|hitsdumoment|top',
 'ete2010': r'201[0-4]',
 'disney': r'disney|pixar',
 'dessins': r'generique|dessin|cartoon|dorothee|manga|anime',
 'series': r'serie|tv|generique|show',
 'films': r'film|movie|cinema|bandeoriginale|bandesoriginales|soundtrack',
}
def from_playlists(key, got, seen, seenb):
    pls = []
    for q in EXTRA.get(key, []):
        time.sleep(0.15)
        res = get(API + '/search/playlist', {'q': q, 'limit': 10}).get('data', [])
        res = [r for r in res if r.get('nb_tracks', 0) >= 25 and re.search(KW.get(key, '.'), norm(r.get('title', '')))]
        res.sort(key=lambda r: ('deezer' not in norm(r.get('user', {}).get('name', ''))))
        pls += [r['id'] for r in res[:3] if r['id'] not in pls]
    for pid in pls:
        if len(got) >= CAP: break
        time.sleep(0.15)
        for t in get(API + f'/playlist/{pid}/tracks', {'limit': 120}).get('data', []):
            if len(got) >= CAP: break
            if not t.get('preview') or not t.get('readable', True) or t['id'] in seen: continue
            full = t['title'] + ' ' + t['artist']['name'] + ' ' + t.get('album', {}).get('title', '')
            if BAD.search(full): continue
            if key in POPLIKE and norm(t['artist']['name']) not in KNOWN: continue  # seulement des artistes connus de la grande base
            b = base(t['title']) + '|' + norm(t['artist']['name'])
            if b in seenb: continue
            seen.add(t['id']); seenb.add(b)
            got.append([t['artist']['name'], t['title_short'] or t['title'], t['id'], t.get('md5_image', ''), t.get('album', {}).get('title', '')])

db = json.load(open('../db.json'))
KNOWN = {norm(a) for a in db['a']}
POPLIKE = {'club', 'soiree', 'top50', 'ete2010'}
out = []
for key, name, emo, items in PLAYLISTS:
    got, seen, seenb = [], set(), set()
    for title, hint in items:
        t = find(title, hint)
        if not t or t['id'] in seen:
            print('  introuvable :', name, '|', title, '|', hint); continue
        seen.add(t['id']); seenb.add(base(t['title']) + '|' + norm(t['artist']['name']))
        got.append([t['artist']['name'], t['title_short'] or t['title'], t['id'], t.get('md5_image', ''), t.get('album', {}).get('title', '')])
    n0 = len(got); from_playlists(key, got, seen, seenb)
    print(f'{name} : {n0}/{len(items)} à la main + {len(got)-n0} des playlists Deezer')
    if len(got) >= 20: out.append([key, name, emo, got])
if len(out) < len(PLAYLISTS) // 2:
    sys.exit('Deezer a sans doute mal répondu : db.json n\'est pas modifiée.')
# Films et séries : une seule catégorie (demande de Max), les deux listes mélangées
def merge_films_series(out):
    keys = [x[0] for x in out]
    if 'films' not in keys and 'series' not in keys: return out
    a = next((x[3] for x in out if x[0] == 'films'), []); b = next((x[3] for x in out if x[0] == 'series'), [])
    mix, ids = [], set()
    for i in range(max(len(a), len(b))):
        for L in (a, b):
            if i < len(L) and L[i][2] not in ids: ids.add(L[i][2]); mix.append(L[i])
    pos = min(i for i, k in enumerate(keys) if k in ('films', 'series'))
    rest = [x for x in out if x[0] not in ('films', 'series')]
    rest.insert(pos, ['films', 'Films et séries', '🎬', mix])
    return rest
out = merge_films_series(out)
db['l'] = out
# playlists faites d'une liste d'artistes (Problématique, YouTube)
import playlists_artistes
playlists_artistes.merge(db, playlists_artistes.build())
open('../db.json', 'w').write(json.dumps(db, ensure_ascii=False, separators=(',', ':')))
print(len(out), 'playlists écrites dans db.json')
