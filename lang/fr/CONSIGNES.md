# Dark Arms - Beast Buster — consignes de traduction

Jeu : action / élevage d'armes vivantes (SNK, Neo Geo Pocket Color, 1999). Le héros, un « Buster » amnésique
arrivé dans le monde des ténèbres (Dark Raom), capture des bêtes pour nourrir des Germes et en faire naître des
Armes, pour le compte d'un Maître encapuchonné dont il vaut mieux se méfier. Ton : sombre, un peu gothique,
avec des villageois hauts en couleur.

## 1. Source = le JAPONAIS, l'anglais n'est qu'une aide
- Le sens, le ton et les détails viennent du japonais (lignes `JP` de `out/src/*.txt`). L'anglais officiel
  résume et contient des contresens (exemples : ほかくだん = balles **de capture** ; おまえには ひつようじゃ =
  « tu en as besoin »).
- L'anglais donne le **découpage en pages** : une ligne traduite par adresse anglaise. Le texte d'une
  conversation peut être réparti librement entre ses pages, mais chaque page garde un texte non vide.
- Quand l'anglais a plus de pages que le japonais n'a de contenu, les pages en trop reprennent les
  informations de l'anglais officiel.

## 2. ADAPTER, pas traduire
- Chaque boîte doit avoir du sens SEULE, dite par CE personnage, comme un francophone le dirait.
- Pas de calque, pas de style télégraphique : reformuler plutôt que mutiler.
- Pas de passé simple mêlé au passé composé dans une même réplique.

## 3. Contraintes (contrôlées par `tools/controle.py`)
| Fichier | Contenu | Boîte |
|---|---|---|
| `maitre.tsv` | le Maître, Joyce, dame Raison, la fin | 3 lignes × 16 |
| `pnj.tsv` | villageois, Caso, sauvegarde | 2 lignes × 15 (invites oui/non : 16) |
| `descs.tsv` | fiches des bêtes et des armes ; origine des armes | 5 × 16 ; 3 × 14 |
| `noms.tsv` | noms d'armes et de bêtes | longueur de l'anglais (12 / 13) |
| `menus.tsv` | menus, options, mode Combat | chaque ligne ≤ la ligne anglaise, même nombre de lignes |

- Format : `ADRESSE<TAB>texte` (adresse hexadécimale de la chaîne anglaise), `|` = ligne suivante,
  `{F900}` = nom du héros (compter 6), `{FA00}` = code de l'invite oui/non, `{FDxx}{FCxx}` = positions.
  Le code `{FA03}` / `{FA04}` de début de page n'est pas à écrire : il est repris de l'anglais.
- Menus : garder les colonnes de l'anglais (`Oui`/`Non` sous `Yes`/`No`, `[A]`/`[B]` au même endroit).
- Caractères : ASCII et `é è ê ë à â ç ù û î ï ô œ É È Ê À Â Ç Î Ô`. Pas de « » ni de … (écrire `"` et `...`).
