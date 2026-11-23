# Dark Arms - Beast Buster — notes techniques sur la ROM

ROM d'origine : 2 Mio, en-tête « BEAST BUSTER », SNK 1999. **Une seule ROM pour les deux langues** : le réglage
de langue de la console choisit le japonais ou l'anglais. Le patch remplace la version anglaise (le japonais
de la ROM traduite n'est plus garanti : ses katakana ont cédé leur place aux accents).
Adresses = positions dans le fichier ; adresse processeur = fichier + 0x200000.

## Texte
- Mots de **16 bits** petit-boutiens : 0x0020-0x007E ASCII ; 0x00A1-0x00DF katakana demi-largeur (SJIS) ;
  0x00E0-0x00EE ガ..ド ; 0x00F4-0x00FD バ..ポ ; 0x0106 を ; 0x0107-0x010F petits kana ; 0x0111-0x013D あ..ん ;
  0x0140-0x014E が..ど ; 0x0154-0x015D ば..ぽ ; 0x0014-0x001B 年月日火水木金土. Table : `tools/table.py`.
- Codes : 0xFF00 fin ; 0xFE00 ligne suivante ; 0xFA03 / 0xFA04 en tête des pages de dialogue (type de boîte) ;
  0xF900 nom du héros ; 0xFA00 invite oui/non ; 0xFDxx / 0xFCxx positionnement (menus du mode Combat).
- Tout le texte est entre 0xD8000 et 0xF4800 (plus quelques chaînes vers 0x22F61-0x2387D et 0x408EE-0x428BB).
  Pointeurs : 32 bits (valeur processeur) ou 24 bits dans une instruction « F2 aa bb cc 3x ».
  ⚠ Les octets « 2D 00 2E 00 » sont partout : beaucoup de faux pointeurs ; `tools/build.py` ne garde que les
  vrais sites (enregistrement de script `40 25 00 <ptr>` pour les dialogues, ou site hors du texte).
- **Dialogues = script** : une page = enregistrement de 15 octets « … 84 93 00 00 00 40 25 00 <ptr texte> » ;
  une conversation = liste de pointeurs vers des enregistrements ; tables de conversations japonaises et
  anglaises **parallèles** (même numéro) : Maître 0xDA00A… / 0xDCC04…, villageois 0xE1F19… / 0xE66F6….
- Descriptions : tables [ptrEN, ptrJP, EN × N, JP × N] en 0xEE574 (bêtes), 0xF152C (armes), 0xF3594 (origines).
- Noms d'armes / de bêtes : 0xE0B85-0xE36C2, chaînes bourrées d'espaces à longueur fixe.
- Menu titre (0xD8896) : les flèches du curseur sont à x = 32 + 8·i et 119 − 8·i (entonnoir de 10 / 8 / 6
  cases) ; les libellés doivent tenir dedans.

## Police
- 2 bits par pixel, 8×8, chasse fixe : glyphe(code) = 0x8C4A4 + 16·code ; seconde copie (fond blanc) au code
  + 0x160. Pas d'accents d'origine : 21 lettres accentuées dessinées à la main (`tools/police.py`) dans les
  cases katakana 0xC0-0xD4 des deux copies.

## Images traduites (tuiles 2 bits par pixel non compressées)
| Adresse | Contenu | Format |
|---|---|---|
| 0x5D0E2 | bandeau STORY MODE → HISTOIRE | sprites 11×2 tuiles |
| 0x5D302 | bandeau OPTION (gardé) | sprites 11×2 tuiles |
| 0x5D462 | bandeau STAGE SELECT → TERRAIN | sprites 11×2 tuiles |
| 0x8F0AC | HUD LIFE / POW / CATCH → VIE / PUIS / PRISES (tuiles 0x1D0-0x1D7) | mini-police 3×5 |
| 0x558AE-0x55DAE | 6 noms de lieux de la carte | sprites 8×2 tuiles chacun (64×16) |
| 0x553CE / 0x5542E | Day / Night → Jour / Nuit | sprites 3×2 tuiles |
Les noms de lieux japonais (0x55EAE-0x563AE) et les deux logos ne sont pas modifiés.

## Place et sauvegarde
- Zone libre utilisée pour le texte déplacé : 0x1A6000-0x1CFFFF (le patch v1.0 en occupe ~20 Kio).
- **Sauvegarde** : bloc flash de 64 Kio en **0x1D0000** (mesuré : la sauvegarde écrit 0x1D0000-0x1D00BB).
  Ne jamais rien y mettre. La taille de la ROM est inchangée (2 Mio), donc les sauvegardes restent au même
  endroit.
