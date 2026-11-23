"""Catalogue of every pointed string of the ROM -> out/catalogue.tsv

    python tools/extraire.py "Dark Arms - Beast Buster.ngc"

Pointers: 32-bit (CPU value 0x200000-0x3FFFFF) or 24-bit inside an instruction "F2 aa bb cc 3x"
(24-bit absolute addressing; such sites are written *XXXXXX = address of the 3 bytes).
A string start is accepted if it follows "00 FF" (end of the previous string) or begins with FA03/FA04
(first page of a conversation, right after the script). The whole string must decode.
Columns: address | sites | JP/EN | text (\\n = new line)."""
import os
import sys
import collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from table import decode, est_jp, DEC  # noqa: E402

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ZONE_DIALOGUES = (0xD8000, 0xF4800)


def references(rom):
    refs = collections.defaultdict(list)
    for i in range(len(rom) - 3):
        v = rom[i] | rom[i+1] << 8 | rom[i+2] << 16 | rom[i+3] << 24
        if 0x200000 <= v < 0x400000:
            refs[v - 0x200000].append('%06X' % i)
    for i in range(len(rom) - 4):
        if rom[i] == 0xF2 and 0x20 <= rom[i+3] < 0x40 and 0x30 <= rom[i+4] < 0x40:
            v = rom[i+1] | rom[i+2] << 8 | rom[i+3] << 16
            refs[v - 0x200000].append('*%06X' % (i + 1))
    return refs


def valide(rom, a):
    """Number of letters of the string at a, or None if it is not a real string start."""
    if a < 2 or a >= len(rom) - 2:
        return None
    if not (rom[a-2:a] == b'\x00\xff' or (rom[a+1] == 0xFA and rom[a] in (3, 4))):
        return None
    n = 0
    i = a
    while i - a < 1200:
        w = rom[i] | rom[i+1] << 8
        i += 2
        if w == 0xFF00:
            return n
        if w in DEC:
            n += DEC[w].isalpha()
        elif (w >> 8) not in (0xF9, 0xFA, 0xFC, 0xFD) and w != 0:
            if not (ZONE_DIALOGUES[0] <= a < ZONE_DIALOGUES[1]):
                return None
    return None


def catalogue(rom):
    """{address: (sites, 'JP'|'EN', text)}"""
    refs = references(rom)
    ok = {}
    for a in sorted(refs):
        n = valide(rom, a)
        if n is None:
            continue
        t = decode(rom, a)[0]
        if ZONE_DIALOGUES[0] <= a < ZONE_DIALOGUES[1]:
            if t.count('{') * 4 > len(t) + 4:
                continue
        elif n < 2:
            continue
        ok[a] = (refs[a], 'JP' if est_jp(t) else 'EN', t)
    return ok


def main():
    if len(sys.argv) != 2:
        raise SystemExit(__doc__)
    rom = open(sys.argv[1], 'rb').read()
    cat = catalogue(rom)
    os.makedirs(os.path.join(RACINE, 'out'), exist_ok=True)
    sortie = os.path.join(RACINE, 'out', 'catalogue.tsv')
    with open(sortie + '.tmp', 'w', encoding='utf-8', newline='\n') as f:
        for a, (sites, lang, t) in cat.items():
            f.write('%06X\t%s\t%s\t%s\n' % (a, ','.join(sites), lang, t.replace(chr(10), chr(92) + 'n')))
    os.replace(sortie + '.tmp', sortie)
    print('%d strings -> %s' % (len(cat), sortie))


if __name__ == '__main__':
    main()
