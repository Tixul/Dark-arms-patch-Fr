"""Graphismes traduits (tuiles 2 bpp en clair dans la ROM).
- Bandeau « STORY MODE » (sprites 16 px, 2 rangées de 11 tuiles, 0x5D0E2) -> « HISTOIRE »
  (lettres S T O R E reprises de l'original, H et I dessinés dans le même style).
- HUD (0x8F0AC, tuiles 0x1D0-0x1D7) : LIFE -> VIE, POW -> PUIS, CATCH -> PRISES (mini-police 3x5).
    import graphismes ; graphismes.applique(bytearray_rom)"""
BANNIERE = 0x5D0E2
HUD = 0x8F0AC


def lit_tuile(rom, o):
    return [[(rom[o + 2*r] | rom[o + 2*r + 1] << 8) >> (14 - 2*x) & 3 for x in range(8)] for r in range(8)]


def ecrit_tuile(rom, o, px):
    for r in range(8):
        w = 0
        for x in range(8):
            w |= px[r][x] << (14 - 2*x)
        rom[o + 2*r] = w & 0xFF
        rom[o + 2*r + 1] = w >> 8


def lit_bande(rom, o, larg_t, haut_t):
    b = [[0] * (8 * larg_t) for _ in range(8 * haut_t)]
    for ty in range(haut_t):
        for tx in range(larg_t):
            t = lit_tuile(rom, o + 16 * (ty * larg_t + tx))
            for r in range(8):
                for x in range(8):
                    b[ty*8 + r][tx*8 + x] = t[r][x]
    return b


def ecrit_bande(rom, o, b, larg_t, haut_t):
    for ty in range(haut_t):
        for tx in range(larg_t):
            ecrit_tuile(rom, o + 16 * (ty * larg_t + tx), [row[tx*8:tx*8 + 8] for row in b[ty*8:ty*8 + 8]])


def motif(lignes):
    return [[{'.': 0, '1': 1, '2': 2, '3': 3}[c] for c in l] for l in lignes]


H = motif(['...........', '3331...3331', '3331...3331', '1331...1331', '.331....331', '.331....331',
           '.3333333331', '.3333333331', '.331....331', '.331....331', '.331....331', '33331.33331',
           '33331.33331', '11111.11111', '...........', '...........'])
I = motif(['.....', '33331', '33331', '13311', '.331.', '.331.', '.331.', '.331.', '.331.', '.331.',
           '.331.', '33331', '33331', '11111', '.....', '.....'])


def banniere(rom):
    b = lit_bande(rom, BANNIERE, 11, 2)
    def tranche(c0, c1):
        return [row[c0:c1 + 1] for row in b]
    S, T, O, R, E = tranche(5, 11), tranche(12, 20), tranche(21, 29), tranche(30, 38), tranche(81, 87)
    vide = [[0] for _ in range(16)]
    seq = [H, vide, I, vide, S, T, O, I, vide, R, E]
    larg = sum(len(x[0]) for x in seq)
    x0 = (88 - larg) // 2 + 2
    n = [[0] * 88 for _ in range(16)]
    x = x0
    for lettre in seq:
        for r in range(16):
            for k, v in enumerate(lettre[r]):
                n[r][x + k] = v
        x += len(lettre[0])
    ecrit_bande(rom, BANNIERE, n, 11, 2)


P3 = {'P': ['111', '1.1', '111', '1..', '1..'], 'R': ['111', '1.1', '11.', '1.1', '1.1'],
      'S': ['111', '1..', '111', '..1', '111'], 'E': ['111', '1..', '111', '1..', '111'],
      'U': ['1.1', '1.1', '1.1', '1.1', '111'], 'V': ['1.1', '1.1', '1.1', '1.1', '.1.'],
      'I': ['1', '1', '1', '1', '1']}


def mot_hud(rom, tuile0, ntuiles, mot):
    """Écrit le mot (mini-police) en tuiles HUD : fond 3, encre 1, lignes 2-6, à partir de x=1."""
    b = [[3] * (8 * ntuiles) for _ in range(8)]
    x = 1
    for ch in mot:
        g = P3[ch]
        for r in range(5):
            for k, c in enumerate(g[r]):
                if c == '1':
                    b[2 + r][x + k] = 1
        x += len(g[0]) + 1
    assert x - 1 <= 8 * ntuiles, mot
    for t in range(ntuiles):
        ecrit_tuile(rom, HUD + 16 * (tuile0 - 0x1D0 + t), [row[t*8:t*8 + 8] for row in b])


TERRAIN = 0x5D462   # bandeau « STAGE SELECT » (mode Combat), même format 11x2 tuiles, lettres 13 lignes
I13 = motif(['33331', '33331', '13311', '.331.', '.331.', '.331.', '.331.', '.331.', '.331.', '.331.',
             '33331', '33331', '11111', '.....', '.....', '.....'])
R13 = motif(['3333331.', '33333331', '1331.331', '.331.331', '.3333311', '.333311.', '.331331.', '.331.331',
             '.331.331', '.331.331', '3331.331', '3331.331', '1111.111', '........', '........', '........'])
N13 = motif(['3331...331', '33331..331', '.33331.331', '.331331331', '.331.33331', '.331..3331', '.331...331',
             '.331...331', '.331...331', '.331...331', '33331..331', '33331..331', '11111..111', '..........',
             '..........', '..........'])


def terrain(rom):
    b = lit_bande(rom, TERRAIN, 11, 2)
    def tranche(c0, c1):
        return [row[c0:c1 + 1] for row in b]
    T, A, E = tranche(8, 16), tranche(16, 24), tranche(33, 39)
    vide = [[0] for _ in range(16)]
    seq = [T, E, vide, R13, vide, R13, vide, A, vide, I13, vide, N13]
    larg = sum(len(x[0]) for x in seq)
    n = [[0] * 88 for _ in range(16)]
    x = (88 - larg) // 2
    for lettre in seq:
        for r in range(16):
            for k, v in enumerate(lettre[r]):
                if v:
                    n[r][x + k] = v
        x += len(lettre[0])
    ecrit_bande(rom, TERRAIN, n, 11, 2)


OPTION = 0x5D302


def options(rom):
    """« OPTION » -> « OPTIONS » : S pris dans le bandeau STAGE SELECT d'origine (à appeler AVANT terrain)."""
    s = [row[1:8] for row in lit_bande(rom, TERRAIN, 11, 2)]
    b = lit_bande(rom, OPTION, 11, 2)
    cols = [x for x in range(88) if any(b[r][x] for r in range(16))]
    mot = [row[cols[0]:cols[-1] + 1] for row in b]
    mot = [mot[r] + [0] + s[r] for r in range(16)]
    larg = len(mot[0])
    x0 = (88 - larg) // 2
    n = [[0] * 88 for _ in range(16)]
    for r in range(16):
        for k, v in enumerate(mot[r]):
            n[r][x0 + k] = v
    ecrit_bande(rom, OPTION, n, 11, 2)


# Noms de lieux de la carte (sprites 8x2 tuiles = 64x16 px, lettres lignes 6-12, ombre ligne 13)
LIEUX = {0x558AE: 'MAISON DU MAÎTRE', 0x559AE: 'CIMETIÈRE', 0x55AAE: 'VILLAGE ÉVEILLÉ',
         0x55BAE: 'SCHATTENVILLE', 0x55CAE: 'TOUR DU DESTIN', 0x55DAE: 'VILLE ERRANTE'}
F37 = {'A': ['.1.', '1.1', '1.1', '111', '1.1', '1.1', '1.1'], 'C': ['.11', '1..', '1..', '1..', '1..', '1..', '.11'],
       'D': ['11.', '1.1', '1.1', '1.1', '1.1', '1.1', '11.'], 'E': ['111', '1..', '1..', '11.', '1..', '1..', '111'],
       'G': ['.11', '1..', '1..', '1.1', '1.1', '1.1', '.11'], 'I': ['1', '1', '1', '1', '1', '1', '1'],
       'L': ['1..', '1..', '1..', '1..', '1..', '1..', '111'],
       'M': ['1...1', '11.11', '1.1.1', '1...1', '1...1', '1...1', '1...1'],
       'N': ['1..1', '11.1', '11.1', '1.11', '1.11', '1..1', '1..1'],
       'O': ['.1.', '1.1', '1.1', '1.1', '1.1', '1.1', '.1.'], 'R': ['11.', '1.1', '1.1', '11.', '1.1', '1.1', '1.1'],
       'S': ['.11', '1..', '1..', '.1.', '..1', '..1', '11.'], 'T': ['111', '.1.', '.1.', '.1.', '.1.', '.1.', '.1.'],
       'U': ['1.1', '1.1', '1.1', '1.1', '1.1', '1.1', '111'], 'V': ['1.1', '1.1', '1.1', '1.1', '1.1', '.1.', '.1.'],
       'H': ['1.1', '1.1', '1.1', '111', '1.1', '1.1', '1.1']}
ACC37 = {'È': ('E', ['1..', '.1.']), 'É': ('E', ['..1', '.1.']), 'Î': (None, ['.1.', '1.1'])}


def glyphe37(ch):
    """-> (accent 2 lignes ou None, corps 7 lignes)"""
    if ch in ACC37:
        base, acc = ACC37[ch]
        corps = F37[base] if base else ['.1.'] * 7
        return acc, corps
    return None, F37[ch]


def lieu(rom, adr, mot):
    ink = [[0] * 64 for _ in range(16)]
    esp = 3
    while True:
        larg = 0
        elems = []
        for ch in mot:
            if ch == ' ':
                elems.append(None); larg += esp; continue
            acc, corps = glyphe37(ch)
            elems.append((acc, corps)); larg += len(corps[0]) + 1
        if larg <= 62 or esp == 1:
            break
        esp -= 1
    assert larg <= 62, (mot, larg)   # colonnes 0 et 63 cachées par le cadre de la carte
    x = 1 + (62 - larg) // 2
    for e in elems:
        if e is None:
            x += esp; continue
        acc, corps = e
        for r, l in enumerate(corps):
            for k, c in enumerate(l):
                if c == '1': ink[6 + r][x + k] = 1
        if acc:
            for r, l in enumerate(acc):
                for k, c in enumerate(l):
                    if c == '1': ink[4 + r][x + k] = 1
        x += len(corps[0]) + 1
    assert x <= 64, (mot, x)
    n = [[0] * 64 for _ in range(16)]
    for r in range(16):
        for c in range(64):
            if ink[r][c]:
                n[r][c] = 3 if r <= 6 or (r > 0 and not ink[r - 1][c]) else 2
    for r in range(16):
        for c in range(64):
            if not ink[r][c] and ((c > 0 and ink[r][c - 1]) or (r > 0 and ink[r - 1][c])):
                n[r][c] = 1
    ecrit_bande(rom, adr, n, 8, 2)


# Jour / Nuit (carte, en bas à droite) : sprites 3x2 tuiles (24x16), Day 0x553CE, Night 0x5542E
JN = {0x553CE: [('J', 3, ['...1', '...1', '...1', '...1', '...1', '1..1', '1..1', '.11.']),
                ('o', 5, ['.11.', '1..1', '1..1', '1..1', '1..1', '.11.']),
                ('u', 5, ['1..1', '1..1', '1..1', '1..1', '1..1', '.111']),
                ('r', 5, ['1.11', '11..', '1...', '1...', '1...', '1...'])],
      0x5542E: [('N', 3, ['1...1', '11..1', '11..1', '1.1.1', '1.1.1', '1..11', '1..11', '1...1']),
                ('u', 5, ['1..1', '1..1', '1..1', '1..1', '1..1', '.111']),
                ('i', 3, ['1', '.', '1', '1', '1', '1', '1', '1']),
                ('t', 4, ['.1.', '111', '.1.', '.1.', '.1.', '.1.', '..1'])]}


def jour_nuit(rom, adr, lettres):
    ink = [[0] * 24 for _ in range(16)]
    x = 0
    for _, r0, g in lettres:
        for r, l in enumerate(g):
            for k, c in enumerate(l):
                if c == '1': ink[r0 + r][x + k] = 1
        x += len(g[0]) + 1
    n = [[0] * 24 for _ in range(16)]
    for r in range(16):
        for c in range(24):
            if ink[r][c]:
                n[r][c] = 3 if r <= 6 else 2
            elif (c > 0 and ink[r][c - 1]) or (r > 0 and ink[r - 1][c]):
                n[r][c] = 1
    # rangement : 3 tuiles du haut puis 3 du bas
    for ty in range(2):
        for tx in range(3):
            ecrit_tuile(rom, adr + 16 * (ty * 3 + tx), [row[tx*8:tx*8 + 8] for row in n[ty*8:ty*8 + 8]])


def applique(rom):
    for adr, lettres in JN.items():
        jour_nuit(rom, adr, lettres)
    for adr, mot in LIEUX.items():
        lieu(rom, adr, mot)
    banniere(rom)
    # options(rom)  # retiré 23/11 : le menu titre n'a que 6 cases en 3e ligne -> « OPTION » partout
    terrain(rom)
    mot_hud(rom, 0x1D0, 2, 'VIE')
    mot_hud(rom, 0x1D2, 2, 'PUIS')
    mot_hud(rom, 0x1D5, 3, 'PRISES')
    return rom
