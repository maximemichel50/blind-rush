# Blind Rush 🎧

Blind test musical : 10 manches, 4 réponses, plus tu réponds vite plus tu marques. Seul, à deux, en soirée sur un même écran, ou en ligne avec chacun son téléphone.

**Jouer :** https://maximemichel50.github.io/blind-rush/

## Comment c'est rangé

| Fichier | Rôle |
|---|---|
| `index.html` | Toute l'appli : écrans, styles visuels (CSS), logique du jeu (JavaScript). |
| `db.json` | La base de musiques : artistes, styles, morceaux. Générée par les scripts de `tools/`, ne pas la modifier à la main. |
| `tools/` | Scripts Python qui construisent `db.json` à partir de l'API publique de Deezer. |

## Modes de jeu

La musique tourne pendant tout le chrono, dans tous les modes. La difficulté règle le temps pour répondre (20 s, 14 s, 8 s) et l'endroit du morceau où l'extrait démarre.

La difficulté par défaut est Moyen. À partir de Moyen, les 4 réponses sont des titres du même artiste ; en Facile, ce sont des artistes différents.

- **Solo** : 5 à 20 manches contre le chrono, record par difficulté et par nombre de manches.
- **Séries** (Solo et Duel) : 3 bonnes réponses d'affilée = points ×2, 5 d'affilée = ×3, une erreur remet à zéro (`MULT`).
- **Duel** (ambiance ring) : deux joueurs sur le même écran (touches 1-4 pour le rouge, 7 8 9 0 pour le bleu), ou 2 à 12 joueurs en ligne. Bonne réponse 300 à 1000 pts selon la vitesse × difficulté, +150 au premier qui trouve. Option : malus de −150 × difficulté en cas d'erreur.
- **Duel** : le dernier reçoit un gage à la fin (bouton « Autre gage » pour en tirer un autre). Liste : `GAGES` (3 niveaux).
- **Babinski** (« Là pour se détruire », ambiance soirée) : 2 à 8 joueurs répondent en même temps, chacun sur sa ligne A B C D (ou jusqu'à 12 en ligne). Chaque manche, seuls ceux qui se trompent ou ne répondent pas boivent (1, 2 ou 3 gorgées selon l'intensité). Bonne réponse = 1 point. Fin de partie : classement par bonnes réponses, égalité départagée par le temps total de réponse ; le 1er ne boit rien, le 2e 1 gorgée, le 3e 2, etc. Trois versions : avec alcool, sans alcool avec des pompes, ou sans alcool avec des gages (le 1er n'a rien, les autres un gage de plus en plus fort selon la place). À la fin, le 1er fait tourner une roulette (6 cases, autant de chances chacune : 1, 2, 3 ou 4 gorgées, cul sec, ou « ×2 » : le joueur choisi boit tout en double à la partie suivante ; des pompes ou des gages en version sans alcool) et choisit à qui donner ce qu'il a gagné, sur l'écran de l'hôte ou sur son téléphone en ligne (`WHEEL`, `spinWheel()`, `giveWheel()`). Cartes spéciales (option), joker eau par joueur.
- **Playlists à thème** : génériques de dessins animés, tubes des étés 2010, Top 50 français, musiques de films, Disney, tubes de soirée, boîte de nuit. Listes dans `tools/playlists_theme.py` ; un commit dont le message contient `[playlists]` les cherche sur Deezer et les ajoute à `db.json` (clé `l`).

## Jouer en ligne (façon Kahoot / WhoLiked)

Sur l'accueil, toucher **Créer une partie** (en haut de la page). La partie est créée tout de suite avec le mode, la playlist et la difficulté réglés sur la page (Duel si on était en Solo). Le bouton « Lancer la partie » du bas sert aux parties sur un seul écran.

1. L'écran de l'hôte affiche un **code de 4 lettres**, un lien et un QR code. La musique sort de cet appareil.
2. Les joueurs ouvrent le lien ou scannent le QR code (ou touchent « Rejoindre une partie » sur l'accueil et tapent le code), puis choisissent un prénom. Jusqu'à 12 joueurs. L'hôte peut jouer aussi depuis son écran.
3. Chaque manche, les 4 réponses s'affichent sur les téléphones en gros boutons de couleur (▲ ◆ ● ■). Le temps est mesuré sur le téléphone, sans le délai du réseau.
4. Après chaque manche : classement sur l'écran de l'hôte, et sur chaque téléphone son résultat (points, ou gorgées avec l'animation du verre et le bouton joker eau).
5. Un joueur qui perd la connexion (écran verrouillé, réseau) est reconnecté automatiquement et retrouve la partie. « Rejouer » ramène tout le monde dans la salle d'attente.

Technique : les appareils ne se connectent pas directement entre eux (ça bloquait souvent en 4G ou entre deux box). Les messages passent par trois serveurs relais publics MQTT (EMQX, HiveMQ, Mosquitto), utilisés en même temps : si l'un est en panne, les autres suffisent. Code : `brHost()` et `brJoin()` dans le premier `<script>`. Aucun compte, rien n'est stocké. Pour tester sans internet : lancer deux relais MQTT locaux en WebSocket sur les ports 8883 et 8884, et ouvrir la page avec `?peer=local`.

## Repères dans `index.html`

- **Logo** : un clic ramène à l'accueil depuis n'importe quel écran (`goHome()`).
- **En ligne (hôte)** : bouton `#createOpen` de l'accueil, objet `NET`, fonctions `openLobby()`, `hostPeer()`, `onMsg()` (messages des téléphones), `sendQ()`, `sendResults()`, `sendEnd()`, `resync()` (reconnexion).
- **En ligne (téléphone)** : dernier `<script>` du fichier, objet `C`, fonctions `joinScreen()`, `connect()`, `question()`, `result()`, `end()`.

- **Modes** : barre d'onglets en bas de l'accueil (`<nav id="games">`, icônes dans `GICON`, styles `.tabbar` / `.tb`), objets `GAMES`, `INT` (intensités Babinski) et `CARDS`, fonctions `round()`, `reveal()` et `partyRound()` (classement et peines du mode Babinski), `playFx()` (animation de fin de manche), `clubFx()` (animation boîte de nuit quand on choisit Babinski).

- **Ambiances** : objet `THEMES` (un thème par style, plus `duel` et `party` pour les modes) (couleurs `bg`, `ink`, `card`, `acc`, motif de fond `pat`, mot en filigrane `w`).
- **Difficultés** : objet `DIFF` (durée de l'extrait `clip`, temps pour répondre `limit`, multiplicateur `mult`, point de départ de l'extrait `off`).
- **Points** : fonction `answer()` — 300 à 1000 pts selon la vitesse × multiplicateur, + bonus de série.
- **Tirage des manches** : `buildRounds()` et `makeChoices()`.
- **Son** : `resolveUrl()` demande l'extrait de 30 s à Deezer au moment de jouer (Apple Music en secours). Les extraits ne sont jamais stockés dans le projet.

## Format de `db.json`

```
{ "a": ["Ninho", "Jul", ...],                 // artistes (index = position)
  "p": [3, 3, 2, ...],                          // notoriété : 3 = choisi à la main, 2 = plus d'1 million de fans, 1 = plus de 300 000, 0 = autre
  "c": [["rapfr", "Rap FR", [0, 1, ...]], ...], // styles : clé, nom, index des artistes
  "t": [[artiste, "titre", "artiste affiché si feat", idDeezer, "hashPochette", "album"], ...] }
```

## Ajouter des artistes ou un style

1. Ajouter les noms dans `tools/styles_artistes.py`, de préférence dans `AJOUTS` (et un thème dans `THEMES` si nouveau style). Les artistes choisis à la main sortent 8 fois plus souvent que les artistes ajoutés automatiquement, et les décennies ne contiennent que des artistes choisis à la main.
2. Depuis `tools/` : `python3 construire_base.py`, puis `python3 agrandir_base.py`, puis `python3 empaqueter_base.py` → régénère `db.json` (30 titres par artiste, sans les versions « feat. », live ou remix). Entre les deux, `python3 discographies.py` complète jusqu'à 150 titres (albums, singles, EP) pour tout le rap FR choisi à la main et les artistes de plus de 3 millions de fans. Ou bien sur GitHub : Actions → publier → Run workflow en cochant « reconstruire », ou un commit dont le message contient `[reconstruire]`. Si Deezer répond mal, la base n'est pas remplacée.

## Règles de travail à deux

- Une modification = un commit avec un message clair (« Ajoute le style Métal », « Corrige le chrono »…).
- Toujours récupérer la dernière version avant de modifier (l'autre a peut-être changé des choses).
- Après chaque modification, tester la page publiée (1 à 2 minutes de délai).

## Classement mondial (mode Solo)
- À la fin d'une partie Solo, le score est enregistré avec un pseudo (demandé une seule fois).
- Un classement par playlist / style, ou par artiste choisi (1 à 3 artistes), et par nombre de manches. Bouton « Classement mondial de cette playlist » sur l'accueil.
- Pas de Duel ni de Babinski dans le classement.
- Stockage : messages gardés sur les 3 relais publics déjà utilisés pour le jeu en ligne, plus une copie sur chaque appareil qui remet les scores si un relais les perd.
