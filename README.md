# Blind Rush 🎧

Blind test musical : 10 manches, 4 réponses, plus tu réponds vite plus tu marques.

**Jouer :** https://maximemichel50.github.io/blind-rush/

## Comment c'est rangé

| Fichier | Rôle |
|---|---|
| `index.html` | Toute l'appli : écrans, styles visuels (CSS), logique du jeu (JavaScript). |
| `db.json` | La base de musiques : artistes, styles, morceaux. Générée par les scripts de `tools/`, ne pas la modifier à la main. |
| `tools/` | Scripts Python qui construisent `db.json` à partir de l'API publique de Deezer. |

## Modes de jeu

- **Solo** : 10 manches contre le chrono, record par difficulté.
- **Duel** : deux joueurs sur le même écran (touches 1-4 pour le rouge, 7 8 9 0 pour le bleu). Bonne réponse 300 à 1000 pts selon la vitesse × difficulté, +150 au premier qui trouve, −150 × difficulté en cas d'erreur.
- **Babinski** (« Là pour se détruire ») : mode soirée de 2 à 8 joueurs, chacun son tour, le perdant boit. Cartes spéciales : Réflexe éclair, Tournée générale, Duel au comptoir, Quitte ou double, Le roi du comptoir, Karaoké. Plafond de 5 gorgées d'un coup, un joker eau par joueur, version sans alcool (pompes).

## Repères dans `index.html`

- **Modes** : objets `GAMES` et `CARDS`, fonctions `round()`, `reveal()` et `partyOutcome()` (règles du mode Babinski).

- **Ambiances** : objet `THEMES` (un thème par style, plus `duel` et `party` pour les modes) (couleurs `bg`, `ink`, `card`, `acc`, motif de fond `pat`, mot en filigrane `w`).
- **Difficultés** : objet `DIFF` (durée de l'extrait `clip`, temps pour répondre `limit`, multiplicateur `mult`, point de départ de l'extrait `off`).
- **Points** : fonction `answer()` — 300 à 1000 pts selon la vitesse × multiplicateur, + bonus de série.
- **Tirage des manches** : `buildRounds()` et `makeChoices()`.
- **Son** : `resolveUrl()` demande l'extrait de 30 s à Deezer au moment de jouer (Apple Music en secours). Les extraits ne sont jamais stockés dans le projet.

## Format de `db.json`

```
{ "a": ["Ninho", "Jul", ...],                 // artistes (index = position)
  "c": [["rapfr", "Rap FR", [0, 1, ...]], ...], // styles : clé, nom, index des artistes
  "t": [[artiste, "titre", "artiste affiché si feat", idDeezer, "hashPochette", "album"], ...] }
```

## Ajouter des artistes ou un style

1. Ajouter les noms dans `tools/styles_artistes.py` (et un thème dans `THEMES` si nouveau style).
2. Depuis `tools/` : `python3 construire_base.py`, puis `python3 agrandir_base.py`, puis `python3 empaqueter_base.py` → régénère `db.json`.

## Règles de travail à deux

- Une modification = un commit avec un message clair (« Ajoute le style Métal », « Corrige le chrono »…).
- Toujours récupérer la dernière version avant de modifier (l'autre a peut-être changé des choses).
- Après chaque modification, tester la page publiée (1 à 2 minutes de délai).
