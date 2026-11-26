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

- **Solo** : 5 à 20 manches contre le chrono, record par difficulté et par nombre de manches.
- **Duel** (ambiance ring) : deux joueurs sur le même écran (touches 1-4 pour le rouge, 7 8 9 0 pour le bleu), ou 2 à 12 joueurs en ligne. Bonne réponse 300 à 1000 pts selon la vitesse × difficulté, +150 au premier qui trouve. Option : malus de −150 × difficulté en cas d'erreur.
- **Babinski** (« Là pour se détruire », ambiance soirée) : 2 à 8 joueurs répondent en même temps, chacun sur sa ligne A B C D (ou jusqu'à 12 en ligne, chacun sur son téléphone). À la fin du chrono, classement de la manche : ceux qui ont trouvé (du plus rapide au plus lent), puis les mauvaises réponses, puis ceux qui n'ont pas répondu. Le 1er ne boit rien, le dernier prend la plus grosse peine (cul sec en intensité « Là pour se détruire », 5 gorgées en « Soirée », 3 en « Tranquille »), ceux du milieu une peine qui monte avec le rang. Mauvaise réponse ou pas de réponse : au moins 2 gorgées ; si personne ne trouve, tout le monde boit 2. Animation de fin de manche pour le premier et pour chaque joueur qui boit. Cartes spéciales (option) : Réflexe éclair, Double ou rien, Tournée générale, Le roi de la soirée, Karaoké. Un joker eau par joueur, version sans alcool (pompes).

## Jouer en ligne (façon Kahoot / WhoLiked)

Sur l'accueil, toucher **Créer une partie** (ou, pour Duel et Babinski, choisir « Chacun son téléphone »), régler la playlist et la difficulté, puis **Créer la partie** :

1. L'écran de l'hôte affiche un **code de 4 lettres**, un lien et un QR code. La musique sort de cet appareil.
2. Les joueurs ouvrent le lien ou scannent le QR code (ou touchent « Rejoindre une partie » sur l'accueil et tapent le code), puis choisissent un prénom. Jusqu'à 12 joueurs. L'hôte peut jouer aussi depuis son écran.
3. Chaque manche, les 4 réponses s'affichent sur les téléphones en gros boutons de couleur (▲ ◆ ● ■). Le temps est mesuré sur le téléphone, sans le délai du réseau.
4. Après chaque manche : classement sur l'écran de l'hôte, et sur chaque téléphone son résultat (points, ou gorgées avec l'animation du verre et le bouton joker eau).
5. Un joueur qui perd la connexion (écran verrouillé, réseau) est reconnecté automatiquement et retrouve la partie. « Rejouer » ramène tout le monde dans la salle d'attente.

Technique : connexion directe entre appareils avec [PeerJS](https://peerjs.com/) (serveur de mise en relation gratuit de PeerJS, relais TURN si les réseaux bloquent). Aucun compte, aucune donnée stockée. Pour tester sans internet : lancer un serveur PeerJS local (`npx peer --port 9000`) et ouvrir la page avec `?peer=local`.

## Repères dans `index.html`

- **En ligne (hôte)** : bouton `#createOpen` de l'accueil, objet `NET`, fonctions `openLobby()`, `hostPeer()`, `onMsg()` (messages des téléphones), `sendQ()`, `sendResults()`, `sendEnd()`, `resync()` (reconnexion).
- **En ligne (téléphone)** : dernier `<script>` du fichier, objet `C`, fonctions `joinScreen()`, `connect()`, `question()`, `result()`, `end()`.

- **Modes** : objets `GAMES`, `INT` (intensités Babinski) et `CARDS`, fonctions `round()`, `reveal()` et `partyRound()` (classement et peines du mode Babinski), `playFx()` (animation de fin de manche).

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
2. Depuis `tools/` : `python3 construire_base.py`, puis `python3 agrandir_base.py`, puis `python3 empaqueter_base.py` → régénère `db.json` (30 titres par artiste, sans les versions « feat. », live ou remix). Ou bien sur GitHub : Actions → publier → Run workflow en cochant « reconstruire », ou un commit dont le message contient `[reconstruire]`. Si Deezer répond mal, la base n'est pas remplacée.

## Règles de travail à deux

- Une modification = un commit avec un message clair (« Ajoute le style Métal », « Corrige le chrono »…).
- Toujours récupérer la dernière version avant de modifier (l'autre a peut-être changé des choses).
- Après chaque modification, tester la page publiée (1 à 2 minutes de délai).
