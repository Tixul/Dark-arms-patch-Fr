"""Table de caractères de Dark Arms (mots 16 bits petit-boutiens)."""
HIRA = 'あいうえおかきくけこさしすせそたちつてとなにぬねのはひふへほまみむめもやゆよらりるれろわん'
KATA = ('。「」、・ヲァィゥェォャュョッーアイウエオカキクケコサシスセソタチツテトナニヌネノハヒフヘホマミムメモヤユヨラリルレロワン゛゜')
DEC = {}
for i in range(0x20, 0x7F):
    DEC[i] = chr(i)
for i, c in enumerate(KATA):
    DEC[0xA1 + i] = c
for i, c in enumerate('ガギグゲゴザジズゼゾダヂヅデド'):
    DEC[0xE0 + i] = c
for i, c in enumerate('バビブベボパピプペポ'):
    DEC[0xF4 + i] = c
DEC[0x106] = 'を'
for i, c in enumerate('ぁぃぅぇぉゃゅょっ'):
    DEC[0x107 + i] = c
for i, c in enumerate(HIRA):
    DEC[0x111 + i] = c
for i, c in enumerate('がぎぐげござじずぜぞだぢづでど'):
    DEC[0x140 + i] = c
for i, c in enumerate('ばびぶべぼぱぴぷぺぽ'):
    DEC[0x154 + i] = c
for i, c in enumerate('年月日火水木金土'):
    DEC[0x14 + i] = c
DEC[0xFE00] = '\n'
ENC = {v: k for k, v in DEC.items()}


def decode(rom, a):
    """-> (texte, adresse de fin exclusive). {XXXX} = mot inconnu/commande."""
    out = []
    while True:
        w = rom[a] | rom[a + 1] << 8
        a += 2
        if w == 0xFF00:
            return ''.join(out), a
        if w in DEC:
            out.append(DEC[w])
        else:
            out.append('{%04X}' % w)


def est_jp(t):
    return any(0x3000 <= ord(c) < 0x3100 for c in t)
