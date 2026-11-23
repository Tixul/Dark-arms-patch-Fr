"""Build the translated ROM (and the IPS patch).

    python tools/build.py --rom "Dark Arms - Beast Buster.ngc" --lang fr [--ips]

Output: out/<lang>.ngc (and out/<lang>.ips, checked by re-applying it). Steps:
1. checks the ROM (the original cartridge, hashes in README) and runs tools/controle.py ;
2. font : accented letters (tools/police.py) ; graphics : banner, HUD, place names, Day/Night (tools/graphismes.py) ;
3. text of lang/<code>/*.tsv : the leading {FAxx} codes of the English page are kept ; menus, descriptions and
   names are padded with spaces to the English line length ; a string is rewritten in place when it fits in
   the English one (and no other string starts inside it), otherwise it is moved to the free area
   0x1A6000-0x1CFFFF and its pointers (32-bit, or 24-bit "*site") are rewritten.
   The game save lives at 0x1D0000 (64 KiB flash block) : never touched."""
import os
import re
import sys
import glob
import bisect
import hashlib
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from table import decode, DEC  # noqa: E402
import extraire  # noqa: E402
import controle  # noqa: E402
import police  # noqa: E402
import graphismes  # noqa: E402
import ips  # noqa: E402

RACINE = extraire.RACINE
MD5_ORIGINE = 'fe0e58d34d650ae5174ca03d3efc67b0'
LIBRE, LIBRE_FIN = 0x1A6000, 0x1D0000
BOURRE = ('menus', 'descs', 'noms')


def encode(t, enc):
    out = []
    i = 0
    while i < len(t):
        c = t[i]
        if c == '{':
            j = t.index('}', i)
            out.append(int(t[i+1:j], 16))
            i = j + 1
            continue
        out.append(0xFE00 if c == '|' else enc[c])
        i += 1
    return b''.join(bytes([w & 0xFF, w >> 8]) for w in out + [0xFF00])


def construit(src, lang):
    rom = bytearray(src)
    police.applique(rom)
    graphismes.applique(rom)
    enc = {v: k for k, v in DEC.items() if k < 0x7F}
    enc.update(police.CODE)
    cat = extraire.catalogue(src)
    fins = {a: decode(src, a)[1] for a in cat}

    def vrai_texte(a):
        i = a
        while True:
            w = src[i] | src[i + 1] << 8
            i += 2
            if w == 0xFF00:
                return True
            if w not in DEC and (w >> 8) not in (0xF9, 0xFA, 0xFC, 0xFD):
                return False
    debuts = sorted(a for a in cat if vrai_texte(a))

    def dans_texte(i):
        k = bisect.bisect_right(debuts, i) - 1
        return k >= 0 and debuts[k] <= i < fins[debuts[k]]

    def vrais_sites(a, sites):
        # Bytes such as "2D 00 2E 00" are everywhere: keep only real pointer sites.
        dialogue = src[a + 1] == 0xFA and src[a] in (3, 4)
        ok = []
        for s in sites:
            if s.startswith('*'):
                ok.append(s)
                continue
            i = int(s, 16)
            if dialogue:
                if src[i-3:i] == b'\x40\x25\x00':
                    ok.append(s)
            elif not dans_texte(i) and (len(sites) == 1 or 0xD8000 <= i < 0xF4800):
                ok.append(s)
        return ok

    fr = {}
    for f in glob.glob(os.path.join(RACINE, 'lang', lang, '*.tsv')):
        nom = os.path.splitext(os.path.basename(f))[0]
        for k, a, t in controle.lit(f):
            fr[a] = (t, nom)
    libre = LIBRE
    n_place = n_reloge = 0
    for a, (t, nom) in sorted(fr.items()):
        en = decode(src, a)[0]
        tete = re.match(r'^(\{FA0[0-9A-F]\})*', en).group(0)
        if nom in BOURRE:
            el = en[len(tete):].split('\n')
            fl = t.split('|')
            for k in range(len(fl)):
                if k < len(el) and '{' not in fl[k] and '{' not in el[k]:
                    fl[k] = fl[k].ljust(len(el[k]))
            t = '|'.join(fl)
        b = encode(tete + t, enc)
        dedans = any(a < d < fins[a] for d in debuts)
        if len(b) <= fins[a] - a and not dedans:
            rom[a:a + len(b)] = b
            n_place += 1
            continue
        sites = vrais_sites(a, cat[a][0])
        if not sites:
            raise SystemExit('ERROR: no pointer found for %06X, cannot move it (shorten the text)' % a)
        if libre % 2 != a % 2:
            libre += 1
        if libre + len(b) > LIBRE_FIN:
            raise SystemExit('ERROR: free area full')
        rom[libre:libre + len(b)] = b
        cpu = 0x200000 + libre
        for s in sites:
            if s.startswith('*'):
                i = int(s[1:], 16)
                rom[i:i + 3] = cpu.to_bytes(3, 'little')
            else:
                i = int(s, 16)
                rom[i:i + 4] = cpu.to_bytes(4, 'little')
        libre += len(b)
        n_reloge += 1
    print('%d strings in place, %d moved (free area used 0x%06X-0x%06X)' % (n_place, n_reloge, LIBRE, libre))
    return bytes(rom)


def main():
    args = sys.argv[1:]
    if '--rom' not in args or '--lang' not in args:
        raise SystemExit(__doc__)
    src = open(args[args.index('--rom') + 1], 'rb').read()
    lang = args[args.index('--lang') + 1]
    if hashlib.md5(src).hexdigest() != MD5_ORIGINE:
        raise SystemExit('ERROR: this is not the expected ROM (see README, section 1.1)')
    erreurs, n = controle.controle(src, lang)
    if erreurs:
        for e in erreurs:
            print(e)
        raise SystemExit('ERROR: %d rule(s) broken, nothing built (python tools/controle.py ...)' % len(erreurs))
    rom = construit(src, lang)
    os.makedirs(os.path.join(RACINE, 'out'), exist_ok=True)
    sortie = os.path.join(RACINE, 'out', lang + '.ngc')
    open(sortie + '.tmp', 'wb').write(rom)
    os.replace(sortie + '.tmp', sortie)
    print('->', sortie)
    if '--ips' in args:
        p = ips.fabrique(src, rom)
        if ips.applique(src, p) != rom:
            raise SystemExit('ERROR: the patch does not give back the ROM')
        s = os.path.join(RACINE, 'out', lang + '.ips')
        open(s + '.tmp', 'wb').write(p)
        os.replace(s + '.tmp', s)
        print('-> %s (%d bytes, checked)' % (s, len(p)))


if __name__ == '__main__':
    main()
