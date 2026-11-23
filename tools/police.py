"""Accents FR dans la police (2 copies : codes c et c+0x160). Glyphe(c) = 0x8C4A4 + 16*c, 2 bpp.
Encre = 1 ; fond = 3 (copie 0, fond noir) ou 0 (copie 0x160, fond blanc) — lu dans le coin de 'e'.
Cases utilisées : katakana demi-largeur 0xC0.. (ne servent qu'en japonais).
Glyphes dessinés à la main : minuscules = corps lignes 2-6, accent lignes 0-1.
    import police ; police.applique(bytearray_rom) ; police.CODE['é'] -> code"""
BASE = 0x8C4A4
COPIES = (0, 0x160)
ACCENT = {'aigu': ['....1...', '...1....'], 'grave': ['..1.....', '...1....'],
          'circ': ['...1....', '..1.1...'], 'trema': ['........', '..1.1...']}
CORPS = {
    'e': ['..111...', '.1...1..', '.11111..', '.1......', '..1111..'],
    'a': ['..111...', '.....1..', '..1111..', '.1...1..', '..1111..'],
    'u': ['.1...1..', '.1...1..', '.1...1..', '.1..11..', '..11.1..'],
    'o': ['..111...', '.1...1..', '.1...1..', '.1...1..', '..111...'],
    'i': ['...1....', '...1....', '...1....', '...1....', '...1....'],
    'E': ['.11111..', '.1......', '.1111...', '.1......', '.11111..'],
    'A': ['...1....', '..1.1...', '.1...1..', '.11111..', '.1...1..'],
    'I': ['..111...', '...1....', '...1....', '...1....', '..111...'],
    'O': ['..111...', '.1...1..', '.1...1..', '.1...1..', '..111...'],
}
SPECIAL = {
    'ç': ['........', '..111...', '.1...1..', '.1......', '.1...1..', '.1...1..', '..111...', '...1....'],
    'Ç': ['..1111..', '.1....1.', '1.......', '1.......', '1.......', '.1....1.', '..1111..', '...1....'],
    'œ': ['........', '........', '.11.11..', '1..1..1.', '1..1111.', '1..1....', '.11.111.', '........'],
}
ACC = [('é', 'e', 'aigu'), ('è', 'e', 'grave'), ('ê', 'e', 'circ'), ('ë', 'e', 'trema'),
       ('à', 'a', 'grave'), ('â', 'a', 'circ'), ('ç', None, None), ('ù', 'u', 'grave'),
       ('û', 'u', 'circ'), ('î', 'i', 'circ'), ('ï', 'i', 'trema'), ('ô', 'o', 'circ'),
       ('œ', None, None), ('É', 'E', 'aigu'), ('È', 'E', 'grave'), ('Ê', 'E', 'circ'),
       ('À', 'A', 'grave'), ('Â', 'A', 'circ'), ('Ç', None, None), ('Î', 'I', 'circ'),
       ('Ô', 'O', 'circ')]
CODE = {c: 0xC0 + i for i, (c, b, a) in enumerate(ACC)}


def dessin(c, b, a):
    if c in SPECIAL:
        return SPECIAL[c]
    return ACCENT[a] + CORPS[b] + ['........']


def ecrit(rom, code, lignes, fond):
    o = BASE + 16 * code
    for r in range(8):
        w = 0
        for x in range(8):
            w |= (1 if lignes[r][x] == '1' else fond) << (14 - 2*x)
        rom[o + 2*r] = w & 0xFF
        rom[o + 2*r + 1] = w >> 8


def applique(rom):
    for off in COPIES:
        o = BASE + 16 * (ord('e') + off)
        fond = (rom[o] | rom[o + 1] << 8) >> 14 & 3
        for (c, b, a) in ACC:
            ecrit(rom, CODE[c] + off, dessin(c, b, a), fond)
    return rom
