"""Check a translation: box width / number of lines, known addresses, usable characters.

    python tools/controle.py --rom "Dark Arms - Beast Buster.ngc" --lang fr

Rules per file of lang/<code>/ (width counts {F900}, the hero name, as 6 characters):
  maitre.tsv  Master / Joyce / Raison dialogue box : 3 lines x 16
  pnj.tsv     villagers' box : 2 lines x 15 (yes/no prompts {FA00} : 16)
  descs.tsv   beast / weapon descriptions : 5 lines x 16 ; weapon origins (0x0F3E60+) : 3 lines x 14
  noms.tsv    weapon names <= English length (12), beast names <= 13
  menus.tsv   same number of lines as the English, each line <= the English line
Returns an error code if anything is wrong (build.py runs it first)."""
import os
import re
import sys
import glob
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import extraire  # noqa: E402
import police  # noqa: E402

RACINE = extraire.RACINE
PERMIS = set(chr(i) for i in range(0x20, 0x7F)) | set(police.CODE)
# Menu lines a bit longer than the English, checked on screen (address: reason)
VU_A_L_ECRAN = {0x040D7D: 'yes/no line, "Non" one column longer than "No", displays fine'}
REGLES = {'maitre': (16, 3), 'pnj': (15, 2), 'descs': (16, 5), 'noms': (13, 1), 'menus': (None, None)}


def largeur(ligne):
    x = re.sub(r'\{F900\}', '@' * 6, ligne)
    return len(re.sub(r'\{[0-9A-F]{4}\}', '', x))


def lit(chemin):
    d = []
    for k, l in enumerate(open(chemin, encoding='utf-8'), 1):
        l = l.rstrip('\n')
        if l.strip() and not l.startswith('#'):
            a, t = l.split('\t')[:2]
            d.append((k, int(a, 16), t))
    return d


def controle(rom, lang):
    cat = extraire.catalogue(rom)
    erreurs = []
    vus = {}
    for f in sorted(glob.glob(os.path.join(RACINE, 'lang', lang, '*.tsv'))):
        nom = os.path.splitext(os.path.basename(f))[0]
        if nom not in REGLES:
            erreurs.append('%s : unknown file (expected %s)' % (f, ', '.join(REGLES)))
            continue
        for k, a, t in lit(f):
            ou = '%s:%d %06X' % (os.path.basename(f), k, a)
            if a in vus:
                erreurs.append('%s : address already translated in %s' % (ou, vus[a]))
            vus[a] = ou
            if a not in cat or cat[a][1] != 'EN':
                erreurs.append('%s : not an English string of the ROM' % ou)
                continue
            mauvais = set(c for c in re.sub(r'\{[0-9A-F]{4}\}', '', t) if c not in PERMIS and c != '|')
            if mauvais:
                erreurs.append('%s : characters not in the font : %s' % (ou, ''.join(sorted(mauvais))))
            lignes = t.split('|')
            W, N = REGLES[nom]
            if nom == 'menus':
                en = re.sub(r'^(\{FA0[0-9A-F]\})+', '', cat[a][2]).split('\n')
                if len(lignes) > len(en):
                    erreurs.append('%s : %d lines, English has %d' % (ou, len(lignes), len(en)))
                for i, x in enumerate(lignes[:len(en)]):
                    if a in VU_A_L_ECRAN:
                        continue
                    if largeur(x) > max(largeur(en[i]), 1) and not en[i].strip() == '' or (en[i].strip() == '' and largeur(x) > 19):
                        erreurs.append('%s : line %d is %d wide, English %d' % (ou, i + 1, largeur(x), largeur(en[i])))
                continue
            if nom == 'descs' and a >= 0xF3E60:
                W, N = 14, 3
            if nom == 'noms':
                W = len(cat[a][2])
            if nom == 'pnj' and '{FA00}' in t:
                W = 16
            if len(lignes) > N:
                erreurs.append('%s : %d lines (max %d)' % (ou, len(lignes), N))
            for x in lignes:
                if largeur(x) > W:
                    erreurs.append('%s : "%s" is %d wide (max %d)' % (ou, x, largeur(x), W))
    return erreurs, len(vus)


def main():
    args = sys.argv[1:]
    if '--rom' not in args or '--lang' not in args:
        raise SystemExit(__doc__)
    rom = open(args[args.index('--rom') + 1], 'rb').read()
    lang = args[args.index('--lang') + 1]
    erreurs, n = controle(rom, lang)
    for e in erreurs:
        print(e)
    print('%d strings checked, %d error(s)' % (n, len(erreurs)))
    sys.exit(1 if erreurs else 0)


if __name__ == '__main__':
    main()
