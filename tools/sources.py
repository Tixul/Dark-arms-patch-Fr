"""Working files for the translator, extracted from YOUR ROM (never distributed) -> out/src/

    python tools/sources.py "Dark Arms - Beast Buster.ngc"

- out/src/maitre.txt, out/src/pnj.txt : every conversation, Japanese pages (the meaning) followed by the
  English pages to fill (same number of pages as the English: one translated line per English address).
- out/src/descs.txt : beast / weapon descriptions and weapon origins, Japanese and English side by side.
- out/catalogue.tsv : every string (see extraire.py), menus included.

How the dialogue is stored: a page is a 15-byte script record "... 84 93 00 00 00 40 25 00 <text pointer>";
a conversation is a list of 32-bit pointers to records; Japanese and English conversation tables are
parallel (same index)."""
import os
import sys
import re
import collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from table import decode  # noqa: E402
import extraire  # noqa: E402

RACINE = extraire.RACINE
FAMILLES = {   # name: (first Japanese table entry, first English table entry, size of the table area, box)
    # Japanese and English tables have the same layout (gaps included): pages are paired by offset.
    'maitre': (0xDA00A, 0xDCC04, 0x130, '3 lines x 16'),
    'pnj': (0xE1F19, 0xE66F6, 0x800, '2 lines x 15'),
}
DESCS = (('betes', 0xEE574), ('armes', 0xF152C), ('origines', 0xF3594))


def dw(rom, i):
    return int.from_bytes(rom[i:i+4], 'little')


def tables(rom, cat):
    rec = {}
    for a, (sites, lang, t) in cat.items():
        for s in sites:
            if s.startswith('*'):
                continue
            s = int(s, 16)
            if rom[s-3:s] == b'\x40\x25\x00':
                rec[s - 8] = (s, a, lang)
    zones = []
    for r in sorted(rec):
        if zones and r - zones[-1][1] < 0x400:
            zones[-1][1] = r + 15
        else:
            zones.append([r - 0x40, r + 15])
    def dans(o):
        return any(lo <= o < hi for lo, hi in zones)
    ptr_to = collections.defaultdict(list)
    for i in range(len(rom) - 3):
        v = dw(rom, i)
        if 0x200000 <= v < 0x400000:
            ptr_to[v - 0x200000].append(i)
    items = sorted(i for i in range(len(rom) - 3)
                   if 0x2D0000 <= dw(rom, i) < 0x300000 and dans(dw(rom, i) - 0x200000))
    listes, cur = [], []
    for i in items:
        if cur and i == cur[-1] + 4:
            cur.append(i)
        else:
            if cur:
                listes.append(cur)
            cur = [i]
    if cur:
        listes.append(cur)
    listes = [l for l in listes if any(dw(rom, x) - 0x200000 in rec for x in l)]
    debuts = {}
    for l in listes:
        debuts[l[0]] = l
        debuts[l[0] - 2] = l
    tops = sorted(set(i for d in debuts for i in ptr_to.get(d, [])))
    tabs, cur = [], []
    for i in tops:
        if cur and i == cur[-1] + 4:
            cur.append(i)
        else:
            if cur:
                tabs.append(cur)
            cur = [i]
    if cur:
        tabs.append(cur)
    res = []   # (site of the table entry, pages)
    for tb in tabs:
        for e in tb:
            res.append((e, [rec[dw(rom, x) - 0x200000] for x in debuts[dw(rom, e) - 0x200000]
                            if dw(rom, x) - 0x200000 in rec]))
    return res


def txt(rom, a):
    t = decode(rom, a)[0]
    return re.sub(r'^(\{FA0[0-9A-F]\})+', '', t).replace('\n', '|')


def main():
    if len(sys.argv) != 2:
        raise SystemExit(__doc__)
    rom = open(sys.argv[1], 'rb').read()
    cat = extraire.catalogue(rom)
    dossier = os.path.join(RACINE, 'out', 'src')
    os.makedirs(dossier, exist_ok=True)
    T = tables(rom, cat)
    for nom, (jp0, en0, taille, boite) in FAMILLES.items():
        cj = {e - jp0: c for e, c in T if 0 <= e - jp0 < taille}
        ce = {e - en0: c for e, c in T if 0 <= e - en0 < taille}
        cles = sorted(set(cj) | set(ce))
        vus = set()
        out = ['# %s: %d conversations; box %s. Translate each "EN address" line.' % (nom, len(cles), boite), '']
        for k, d in enumerate(cles):
            pj, pe = cj.get(d, []), ce.get(d, [])
            out.append('=== %s %03d ===' % (nom, k))
            out += ['JP  ' + txt(rom, a) for s, a, lang in pj]
            for s, a, lang in pe:
                marque = '(seen) ' if a in vus else '(empty, nothing to translate) ' if not txt(rom, a).strip() else ''
                out.append('%sEN %06X  %s' % (marque, a, txt(rom, a)))
                vus.add(a)
            out.append('')
        open(os.path.join(dossier, nom + '.txt'), 'w', encoding='utf-8', newline='\n').write('\n'.join(out))
    out = []
    for nom, a0 in DESCS:
        p, i = [], a0
        while 0x2D0000 <= dw(rom, i) < 0x300000:
            p.append(dw(rom, i) - 0x200000)
            i += 4
        n = (len(p) - 2) // 2
        out.append('##### %s: %d entries' % (nom, n))
        for k in range(n):
            out.append('--- %s %02d' % (nom, k))
            out.append('JP  ' + decode(rom, p[2 + n + k])[0].replace('\n\n', '|').replace('\n', '|'))
            out.append('EN %06X  %s' % (p[2 + k], decode(rom, p[2 + k])[0].replace('\n', '|')))
    open(os.path.join(dossier, 'descs.txt'), 'w', encoding='utf-8', newline='\n').write('\n'.join(out) + '\n')
    sortie = os.path.join(RACINE, 'out', 'catalogue.tsv')
    with open(sortie, 'w', encoding='utf-8', newline='\n') as f:
        for a, (sites, lang, t) in cat.items():
            f.write('%06X\t%s\t%s\t%s\n' % (a, ','.join(sites), lang, t.replace(chr(10), chr(92) + 'n')))
    print('written: out/src/maitre.txt, out/src/pnj.txt, out/src/descs.txt, out/catalogue.tsv')


if __name__ == '__main__':
    main()
