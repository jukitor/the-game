import math, random, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "motor" / "verktyg"))
from pixelbild import *  # noqa

"""Scener C: pantbanken, gränden bakom urmakaren, brandtrappan och gömstället."""


def _ellips(d, x0, y0, x1, y1, c):
    d.a[d.mask_ellips(x0, y0, x1, y1)] = c


# ======================================================================
#  PANTBANKEN (Mr. Pickles)
# ======================================================================
def pantbank(v=None):
    v = v or {}
    flakt = v.get("flakt", 0)            # takfläktens läge 0..3
    paraply = v.get("paraply", True)     # paraplyet står i stället
    batterier = v.get("batterier", True)  # kartongen ligger på disken
    rnd = random.Random(1947)
    d = Duk(6)

    # --- Bakvägg: mörk tapet med ränder, golvlist ---
    d.vgrad(0, 0, W, 90, [0, 6, 6, 7])
    for x in range(2, W, 8):
        for y in range(4, 88, 2):
            if (y // 2 + x // 8) % 3 == 0:
                d.px(x, y, 7 if y > 30 else 6)
    d.rekt(0, 86, W, 90, 6)
    d.rekt(0, 86, W, 87, 8)
    # Golv av slitna plankor i perspektiv
    d.rekt(0, 90, W, H, 7)
    d.vgrad(0, 90, W, H, [6, 7, 7, 6])
    for i in range(-12, 14):
        d.linje(96 + i * 6, 90, 96 + i * 20, H, 6)
    for y in (97, 106, 117):
        d.rekt(0, y, W, y + 1, 6)

    # --- Hyllor på bakväggen, bakom gallret, fulla med bråte ---
    for hy in (22, 44):
        d.rekt(58, hy, 156, hy + 2, 8)
        d.rekt(58, hy + 2, 156, hy + 3, 6)
    saker = [(62, 4, 15), (68, 6, 4), (76, 3, 9), (82, 5, 13), (88, 7, 3), (120, 6, 10), (128, 4, 4),
             (134, 5, 12), (141, 3, 15), (146, 6, 9), (151, 4, 3)]
    for hy in (22, 44):
        for (sx, sb, sc) in saker:
            h = rnd.randint(4, 9)
            d.rekt(sx, hy - h, sx + sb, hy, sc)
            d.rekt(sx, hy - h, sx + 1, hy, LJUSARE[sc])
            d.ljus(d.mask_poly([(sx, hy - h), (sx + sb, hy - h), (sx + sb, hy), (sx, hy)]), 0.5, MORKARE)
    # En väggklocka som stannat
    _ellips(d, 140, 50, 152, 62, 8)
    _ellips(d, 141, 51, 151, 61, 15)
    d.linje(146, 56, 146, 52, 0)
    d.linje(146, 56, 149, 57, 0)

    # --- Takfläkten (loopar) ---
    d.rekt(103, 0, 105, 6, 0)
    _ellips(d, 100, 5, 108, 10, 7)
    blad = [[(86, 7), (122, 9)], [(90, 11), (118, 4)], [(96, 12), (112, 3)], [(118, 11), (90, 4)]][flakt]
    for (bx, by) in blad:
        d.linje(104, 7, bx, by, 8)
        d.linje(104, 8, bx, by + 1, 6)
    d.rekt(103, 10, 105, 14, 0)
    # Lampa under fläkten
    _ellips(d, 99, 13, 109, 19, 12)
    d.rekt(101, 18, 107, 19, 11)
    d.radial(104, 34, 70, 0.55, mask=(YY > 14))

    # --- Pantlånaren Mr. Pickles bakom gallret ---
    with d.yta("pantlanare"):
        # Kropp: vit skjorta, mörk väst, ärmhållare
        d.a[d.mask_ellips(86, 46, 122, 82) & (YY < 72)] = 15
        d.poly([(94, 50), (114, 50), (118, 70), (90, 70)], 6)
        d.poly([(101, 50), (107, 50), (104, 60)], 15)
        d.rekt(103, 50, 105, 58, 13)               # fluga och slips
        d.rekt(100, 50, 108, 52, 13)
        for kx in (98, 110):
            d.px(kx, 60, 10)
            d.px(kx, 64, 10)
        d.rekt(104, 66, 105, 67, 10)               # klockkedja
        d.linje(98, 64, 104, 66, 10)
        # Armar med röda ärmhållare
        d.rekt(84, 54, 92, 70, 15)
        d.rekt(116, 54, 124, 70, 15)
        d.rekt(84, 58, 92, 60, 13)
        d.rekt(116, 58, 124, 60, 13)
        d.rekt(86, 66, 92, 70, 10)                 # händer på disken
        d.rekt(116, 66, 122, 70, 10)
        # Huvudet: runt och flintskalligt
        _ellips(d, 92, 26, 116, 50, 10)
        _ellips(d, 92, 30, 116, 50, 9)
        _ellips(d, 93, 26, 115, 47, 10)
        d.rekt(98, 28, 102, 30, 11)                # blank flint
        d.px(97, 31, 11)
        for (hx, hy) in [(92, 36), (92, 38), (93, 40), (115, 36), (115, 38), (114, 40)]:
            d.rekt(hx, hy, hx + 1, hy + 2, 4)       # grå hårkrans
        d.px(91, 38, 9)
        d.px(116, 38, 9)                           # öron
        # Ögonbryn, små ögon och glasögon på nästippen
        d.rekt(97, 34, 101, 35, 7)
        d.rekt(107, 34, 111, 35, 7)
        d.px(99, 37, 0)
        d.px(109, 37, 0)
        d.rekt(103, 36, 105, 42, 9)               # näsa
        d.px(104, 41, 14)
        for gx in (99, 106):
            d.rekt(gx, 41, gx + 4, 44, 5)
            d.rekt(gx + 1, 42, gx + 3, 43, 4)
        d.rekt(103, 41, 106, 42, 5)
        d.rekt(100, 46, 108, 47, 7)               # mun
        d.px(99, 45, 7)
        d.px(108, 45, 7)

    # --- Disken med mässingsgaller ---
    d.rekt(56, 70, 158, 100, 7)
    for px_ in range(60, 156, 16):
        d.rekt(px_, 74, px_ + 13, 96, 6)
        d.rekt(px_, 74, px_ + 13, 75, 8)
        d.rekt(px_, 74, px_ + 1, 96, 8)
    d.rekt(54, 68, 160, 72, 9)
    d.rekt(54, 68, 160, 69, 10)
    d.rekt(54, 72, 160, 73, 6)
    # Gallret: ram och ståltrådar, öppning framför Pickles
    d.rekt(56, 24, 158, 26, 9)
    d.rekt(56, 24, 158, 25, 10)
    for gx in (56, 156):
        d.rekt(gx, 24, gx + 2, 68, 9)
        d.px(gx, 24, 11)
    for gx in range(60, 156, 5):
        if 84 <= gx <= 124:
            continue
        d.rekt(gx, 26, gx + 1, 68, 9)
    for gy in (36, 52):
        for gx in range(58, 156):
            if not (84 <= gx <= 125):
                d.px(gx, gy, 8)
    # Bågen över luckan
    for i in range(0, 41):
        ax = 84 + i
        ay = 30 - int(5 * math.sin(math.pi * i / 40))
        d.px(ax, ay, 10)
        d.px(ax, ay + 1, 8)
    d.rekt(84, 30, 86, 68, 9)
    d.rekt(124, 30, 126, 68, 9)
    d.rekt(78, 18, 130, 24, 6)
    d.rekt(79, 19, 129, 23, 9)
    text(d, 96, 19, "PANT", 6)

    # Ringklocka på disken
    _ellips(d, 128, 63, 135, 69, 10)
    d.px(131, 62, 11)
    d.rekt(127, 68, 136, 69, 8)

    # --- Kristallkulan (på disken, vänster) ---
    with d.yta("kristallkula"):
        d.poly([(62, 68), (78, 68), (76, 64), (64, 64)], 0)
        d.rekt(63, 64, 77, 65, 13)
        _ellips(d, 62, 49, 78, 65, 3)
        _ellips(d, 63, 50, 77, 64, 4)
        _ellips(d, 66, 54, 74, 62, 5)
        _ellips(d, 68, 56, 72, 60, 14)
        d.rekt(65, 51, 68, 53, 11)
        d.px(66, 54, 15)
        d.radial(70, 57, 12, 0.35, mask=(YY < 68))

    # --- Kartongen med ficklampsbatterier (på disken, höger) ---
    with d.yta("batterier"):
        if batterier:
            d.rekt(138, 58, 154, 68, 8)
            d.rekt(138, 58, 154, 60, 9)
            d.rekt(138, 58, 139, 68, 9)
            d.rekt(140, 61, 152, 64, 13)
            for bx in (141, 145, 149):             # batterierna sticker upp
                d.rekt(bx, 54, bx + 3, 58, 0)
                d.rekt(bx, 54, bx + 3, 55, 4)
                d.px(bx + 1, 53, 5)
                d.rekt(bx, 56, bx + 3, 57, 13)
            # Prislapp på snöre
            d.linje(153, 60, 157, 63, 15)
            d.rekt(155, 62, 162, 68, 15)
            d.rekt(155, 62, 156, 63, 4)
            text(d, 157, 63, "1", 13)
        else:
            d.rekt(138, 66, 154, 68, 8)            # ljusare fyrkant där kartongen stod
            d.markera("batterier", 138, 60, 156, 68)

    # --- Älghuvudet med damhatt (höger vägg) ---
    with d.yta("algskalle"):
        d.poly([(168, 30), (182, 30), (180, 36), (170, 36)], 8)     # sköld
        d.rekt(168, 30, 182, 31, 9)
        d.poly([(170, 14), (180, 14), (181, 24), (178, 32), (172, 32), (169, 24)], 7)
        d.poly([(172, 26), (178, 26), (179, 34), (171, 34)], 7)       # mule
        d.rekt(172, 32, 178, 35, 6)
        d.px(173, 33, 0)
        d.px(177, 33, 0)
        d.px(171, 19, 0)
        d.px(179, 19, 0)
        d.px(171, 18, 11)
        d.px(179, 18, 11)
        # Skovlar
        for s in (-1, 1):
            bas = 175 + s * 6
            d.linje(bas, 15, bas + s * 6, 12, 8)
            d.poly([(bas + s * 4, 13), (bas + s * 12, 6), (bas + s * 14, 10), (bas + s * 9, 14)], 9)
            for t in range(3):
                d.px(bas + s * (8 + t * 2), 5 + t, 9)
                d.px(bas + s * (8 + t * 2), 4 + t, 10)
        # Fånig damhatt med fjäder
        _ellips(d, 168, 9, 182, 14, 14)
        d.rekt(171, 6, 179, 11, 14)
        d.rekt(171, 9, 179, 10, 13)
        d.linje(179, 8, 185, 1, 15)
        d.linje(180, 8, 186, 2, 15)
        d.px(185, 1, 11)

    # --- Saxofonen på väggen ---
    with d.yta("saxofon"):
        d.rekt(170, 40, 172, 42, 0)              # krok
        d.linje(174, 42, 180, 38, 10)            # munstycke
        d.px(180, 37, 0)
        d.rekt(172, 42, 176, 70, 9)
        d.rekt(172, 42, 173, 70, 10)
        _ellips(d, 170, 66, 182, 76, 9)
        _ellips(d, 176, 60, 186, 70, 10)
        _ellips(d, 178, 61, 185, 67, 6)          # klockan
        d.rekt(176, 68, 180, 72, 9)
        for ky in range(46, 66, 4):
            d.px(175, ky, 11)
            d.px(176, ky + 1, 7)

    # --- Dörren ut med tre gyllene kulor ---
    with d.yta("utgang:ut"):
        d.rekt(4, 14, 36, 90, 6)
        d.rekt(6, 16, 34, 90, 7)
        d.rekt(8, 18, 32, 56, 2)                 # glas mot gatan
        d.vgrad(8, 18, 32, 56, [1, 2, 3])
        regn_over(d, random.Random(4), 10, 0, 8, 18, 32, 56)
        d.rekt(19, 18, 21, 56, 7)
        # Tre gyllene kulor i spegelvänd guldtext
        for (kx, ky) in [(13, 26), (25, 26), (19, 34)]:
            _ellips(d, kx - 3, ky - 3, kx + 3, ky + 3, 10)
            d.px(kx - 1, ky - 1, 11)
            d.px(kx + 1, ky + 1, 9)
        for (kx, ky) in [(13, 26), (25, 26)]:
            d.linje(kx, ky - 3, 19, 21, 9)
        text(d, 12, 46, "PANT", 10)
        d.rekt(8, 56, 32, 58, 6)
        for py in (62, 76):
            d.rekt(9, py, 31, py + 11, 6)
            d.rekt(9, py, 31, py + 1, 8)
        d.rekt(29, 68, 32, 70, 10)               # handtag
        d.rekt(14, 12, 26, 14, 10)               # ringklocka över dörren
        d.px(20, 15, 11)
        d.radial(20, 36, 22, 0.25, mask=(XX > 7) & (XX < 33) & (YY > 17) & (YY < 56))

    # --- Paraplyställ med svart herrparaply ---
    with d.yta("paraply"):
        if paraply:
            d.poly([(43, 92), (47, 62), (51, 92)], 0)   # hopfällt tyg
            d.linje(45, 70, 47, 62, 2)
            d.linje(47, 62, 49, 80, 1)
            d.rekt(46, 46, 48, 63, 0)            # skaft
            d.rekt(46, 54, 48, 55, 10)           # mässingsring
            # Stor krokformad handtagskrok
            for (hx, hy) in [(46, 46), (46, 44), (47, 42), (48, 41), (50, 40), (52, 40), (54, 41), (55, 42),
                             (56, 44), (56, 46), (56, 48), (55, 50)]:
                d.rekt(hx, hy, hx + 2, hy + 2, 8)
            for (hx, hy) in [(47, 43), (49, 41), (52, 41), (55, 43)]:
                d.px(hx, hy, 9)
            d.px(54, 50, 9)
            d.rekt(54, 50, 56, 52, 8)
        d.rekt(40, 74, 54, 98, 3)                # stället (zinkhink)
        d.rekt(40, 74, 54, 76, 5)
        d.rekt(40, 76, 41, 98, 4)
        d.rekt(52, 76, 54, 98, 2)
        for ry in (82, 92):
            d.rekt(40, ry, 54, ry + 1, 2)
        if not paraply:
            d.rekt(42, 75, 52, 76, 1)            # tomt hål
        d.markera("paraply", 40, 40, 58, 98)

    # --- Bråte i högra hörnet: resväskor och en skräddardocka ---
    d.rekt(160, 96, 190, 110, 6)
    d.rekt(160, 96, 190, 97, 8)
    d.rekt(174, 95, 178, 96, 9)
    d.rekt(164, 86, 186, 96, 13)
    d.ljus(d.mask_poly([(164, 86), (186, 86), (186, 96), (164, 96)]), 0.6, MORKARE)
    d.rekt(164, 86, 186, 87, 9)
    # Damm som svävar i lampskenet
    for (sx, sy) in [(70, 30), (130, 38), (90, 16), (118, 26), (150, 30)]:
        d.px(sx, sy, 15)

    d.vinjett(0.5)
    return d


# ======================================================================
#  GRÄNDEN BAKOM URMAKARENS HUS
# ======================================================================
# Avsatsernas höjd (våning 1..4, nerifrån) och marken
AVSATS = [80, 60, 40, 20]
MARK = 106


def _brandstege(d, x0, x1, nere, sida=1):
    """Brandstege i järn med en avsats vid varje våning. nere = nedersta stegen nedfälld."""
    for i, ay in enumerate(AVSATS):
        # Avsats och räcke
        d.rekt(x0, ay, x1, ay + 2, 0)
        d.rekt(x0, ay, x1, ay + 1, 3)
        d.rekt(x0, ay - 7, x1, ay - 6, 0)
        for px_ in range(x0, x1 + 1, 4):
            d.rekt(px_, ay - 7, px_ + 1, ay, 0)
        d.rekt(x0, ay - 7, x0 + 1, ay + 2, 0)
        d.rekt(x1 - 1, ay - 7, x1, ay + 2, 0)
        # Konsoler mot väggen
        d.linje(x0 + 2, ay + 2, x0 + 6, ay + 6, 0)
        d.linje(x1 - 3, ay + 2, x1 - 7, ay + 6, 0)
        # Trappa upp till nästa avsats (växlande håll)
        if i + 1 < len(AVSATS):
            ny = AVSATS[i + 1]
            if (i % 2 == 0) == (sida > 0):
                a, b = (x0 + 3, ay), (x1 - 8, ny + 2)
            else:
                a, b = (x1 - 3, ay), (x0 + 8, ny + 2)
            d.linje(a[0], a[1], b[0], b[1], 0)
            d.linje(a[0], a[1] - 1, b[0], b[1] - 1, 2)
            d.linje(a[0], a[1] - 6, b[0], b[1] - 6, 0)
            for t in range(1, 6):
                sx = a[0] + (b[0] - a[0]) * t // 6
                sy = a[1] + (b[1] - a[1]) * t // 6
                d.rekt(sx - 1, sy - 1, sx + 2, sy, 3)
    # Nedersta stegen: uppdragen (slutar högt över marken) eller nedfälld
    lx = x0 + 2 if sida > 0 else x1 - 7
    if nere:
        y0, y1 = AVSATS[0] + 2, MARK
    else:
        y0, y1 = AVSATS[0] - 12, AVSATS[0] + 6
    d.rekt(lx, y0, lx + 1, y1, 0)
    d.rekt(lx + 4, y0, lx + 5, y1, 0)
    for sy in range(y0 + 2, y1, 3):
        d.rekt(lx + 1, sy, lx + 4, sy + 1, 4)
    if not nere:
        d.rekt(lx - 1, y1 - 1, lx + 6, y1, 0)


def _tegel(d, x0, y0, x1, y1, bas, fog, morker):
    d.rekt(x0, y0, x1, y1, bas)
    d.ljus(d.mask_poly([(x0, y0), (x1, y0), (x1, y1), (x0, y1)]), morker, MORKARE)
    for y in range(y0 + 2, y1, 3):
        off = 0 if (y // 3) % 2 else 3
        for xx in range(x0 + off, x1, 6):
            d.px(xx, y, fog)


def grand(v=None):
    v = v or {}
    regn = v.get("regn", 0)          # 0..9
    anga = v.get("anga", 0)          # 0..5
    svans = v.get("svans", 0)        # 0..3
    stege_ur = v.get("stege_ur", False)
    stege_tvatt = v.get("stege_tvatt", False)
    rnd = random.Random(1923)
    d = Duk(1)

    d.vgrad(0, 0, W, 30, [0, 0, 1, 2])

    # --- Urmakarens hus (vänster), tegel ---
    _tegel(d, 0, 0, 90, MARK, 7, 6, 0.55)
    d.rekt(88, 0, 90, MARK, 6)
    d.rekt(0, 2, 90, 4, 6)
    d.rekt(0, 4, 90, 5, 8)
    for rad, ay in enumerate(AVSATS):
        for kol, fx in enumerate((6, 26, 48, 66)):
            fy = ay - 14
            d.rekt(fx - 1, fy - 1, fx + 11, fy + 13, 6)
            if (rad, kol) == (1, 0):
                d.rekt(fx, fy, fx + 10, fy + 12, 9)    # någon är vaken
                d.rekt(fx, fy, fx + 10, fy + 5, 10)
                d.rekt(fx + 4, fy + 6, fx + 7, fy + 12, 7)
            elif (rad, kol) == (2, 2):
                d.rekt(fx, fy, fx + 10, fy + 12, 0)    # det mörka fönstret på glänt
                d.rekt(fx, fy + 6, fx + 10, fy + 12, 2)
                d.rekt(fx, fy + 6, fx + 10, fy + 7, 4)
                d.rekt(fx + 1, fy + 7, fx + 3, fy + 12, 15)
            else:
                d.rekt(fx, fy, fx + 10, fy + 12, 1)
                d.rekt(fx, fy + 6, fx + 10, fy + 7, 2)
                d.px(fx + 1, fy + 1, 3)
            d.rekt(fx - 1, fy + 12, fx + 11, fy + 13, 4)
    # Bakdörren med skylten O TICK
    d.rekt(8, 88, 26, MARK, 6)
    d.rekt(10, 90, 24, MARK, 2)
    d.rekt(11, 91, 23, MARK, 3)
    d.ljus(d.mask_poly([(11, 91), (23, 91), (23, MARK), (11, MARK)]), 0.5, MORKARE)
    d.px(21, 98, 10)
    d.rekt(4, 80, 30, 87, 9)
    d.rekt(5, 81, 29, 86, 15)
    text(d, 5, 81, "O TICK", 0)
    _ellips(d, 32, 82, 42, 92, 10)              # klocksymbol
    _ellips(d, 33, 83, 41, 91, 15)
    d.linje(37, 87, 37, 84, 0)
    d.linje(37, 87, 40, 87, 0)
    d.rekt(36, 80, 38, 82, 0)
    # Lampa vid dörren
    d.rekt(28, 92, 31, 93, 0)
    d.rekt(28, 93, 31, 95, 11)
    d.radial(20, 96, 22, 0.55, mask=(XX < 88))

    # --- Passagen mellan husen ---
    d.rekt(90, 0, 102, MARK, 0)
    d.vgrad(90, 50, 102, MARK, [0, 1, 1])
    for y in range(20, 90, 9):
        d.rekt(92, y, 100, y + 1, 1)             # tvättlina
    d.rekt(91, 14, 101, 15, 4)
    for (tx, tc) in [(92, 15), (96, 13), (99, 4)]:
        d.rekt(tx, 15, tx + 2, 20, tc)

    # --- Ångtvätteriet (höger), ljus puts ---
    d.rekt(102, 0, W, MARK, 4)
    d.vgrad(102, 0, W, MARK, [3, 3, 4, 3])
    d.ljus(d.mask_poly([(102, 0), (W, 0), (W, MARK), (102, MARK)]), 0.35, MORKARE)
    for y in range(6, MARK, 7):
        for x in range(104 + (y % 3), W, 9):
            if rnd.random() < 0.5:
                d.px(x, y, 2)
    d.rekt(102, 0, 104, MARK, 2)
    d.rekt(102, 2, W, 4, 2)
    for rad, ay in enumerate(AVSATS):
        for kol, fx in enumerate((112, 132, 156, 176)):
            fy = ay - 14
            d.rekt(fx - 1, fy - 1, fx + 11, fy + 13, 2)
            if (rad + kol) % 3 == 0 or (rad, kol) == (0, 3):
                d.rekt(fx, fy, fx + 10, fy + 12, 10)  # ånga och lampljus inne
                d.rekt(fx, fy, fx + 10, fy + 4, 15)
                d.ljus(d.mask_poly([(fx, fy), (fx + 10, fy), (fx + 10, fy + 12), (fx, fy + 12)]), 0.4, MORKARE)
            else:
                d.rekt(fx, fy, fx + 10, fy + 12, 1)
                d.px(fx + 1, fy + 1, 3)
            d.rekt(fx, fy + 6, fx + 10, fy + 7, 2)
            d.rekt(fx - 1, fy + 12, fx + 11, fy + 13, 5)
    # Skylt STEAM LAUNDRY på fasaden (bottenvåningen)
    d.rekt(128, 86, 186, 96, 12)
    d.rekt(129, 87, 185, 95, 0)
    text(d, 131, 89, "STEAM LAUNDRY", 15)
    d.rekt(128, 86, 186, 87, 10)
    # Tvätteriets bakdörr, upplyst
    d.rekt(106, 88, 120, MARK, 2)
    d.rekt(108, 90, 118, MARK, 10)
    d.vgrad(108, 90, 118, MARK, [11, 10, 9])
    d.rekt(108, 96, 118, 97, 9)
    d.radial(113, 100, 18, 0.5, mask=(YY > MARK))
    # Ångröret
    d.rekt(186, 78, W, 82, 4)
    d.rekt(186, 78, W, 79, 5)
    d.rekt(184, 77, 187, 83, 3)
    for sp in range(3):
        sx = 183 - sp
        for y in range(80, 40, -1):
            st = ((y + 2 * anga + sp * 5) // 3) % 6
            sx += [0, -1, 0, 0, 1, -1][st]
            if (y + 2 * anga + sp) % 3 == 0:
                continue
            d.px(sx, y, 15 if y > 66 else 5)
        sx = 183

    # --- Marken: blöt asfalt med pölar ---
    d.rekt(0, MARK, W, H, 2)
    d.vgrad(0, MARK, W, H, [1, 2, 1])
    d.rekt(0, MARK, W, MARK + 1, 3)
    for (x0, x1, f) in [(8, 28, 0.6), (106, 120, 0.7), (128, 186, 0.25)]:
        for y in range(MARK + 1, H):
            s = f * (1 - (y - MARK) / (H - MARK))
            m = (XX >= x0) & (XX < x1) & (YY == y) & ((XX + y) % 2 == 0)
            d.ljus(m, s * 2)
    d.rekt(56, 112, 70, 113, 3)
    d.rekt(150, 115, 172, 116, 3)

    # --- Brandstegarna ---
    with d.yta("brandstege_ur"):
        _brandstege(d, 46, 82, stege_ur, 1)
    d.markera("brandstege_ur", 46, AVSATS[-1] - 8, 81, AVSATS[0] + 10)
    with d.yta("brandstege_tvatt"):
        _brandstege(d, 128, 166, stege_tvatt, -1)
    d.markera("brandstege_tvatt", 128, AVSATS[-1] - 8, 167, AVSATS[0] + 10)

    # --- Soptunnorna med katten ---
    with d.yta("soptunnor"):
        for (tx, tf) in [(72, 3), (88, 4)]:
            d.rekt(tx, 92, tx + 14, 110, tf)
            d.rekt(tx, 92, tx + 1, 110, LJUSARE[tf])
            for ry in (96, 103):
                d.rekt(tx, ry, tx + 14, ry + 1, MORKARE[tf])
            d.rekt(tx - 1, 90, tx + 15, 92, 5 if tf == 4 else 4)
            d.rekt(tx + 5, 89, tx + 9, 90, 3)
        d.rekt(86, 104, 90, 106, 15)             # skräp på marken
        d.rekt(68, 108, 72, 110, 8)
        d.px(102, 108, 9)
    with d.yta("grandkatt"):
        kx, ky = 74, 80
        d.rekt(kx + 2, ky + 3, kx + 9, ky + 10, 0)
        _ellips(d, kx + 1, ky + 5, kx + 10, ky + 11, 0)
        d.rekt(kx + 3, ky, kx + 8, ky + 4, 0)
        d.px(kx + 3, ky - 1, 0)
        d.px(kx + 7, ky - 1, 0)
        d.px(kx + 4, ky + 2, 10)
        d.px(kx + 6, ky + 2, 10)
        svansar = [[(10, 9), (12, 8), (13, 6), (13, 4)], [(10, 9), (12, 9), (14, 8), (15, 6)],
                   [(10, 9), (12, 9), (14, 10), (16, 9)], [(10, 9), (12, 8), (14, 7), (15, 5)]][svans]
        for (sx, sy) in svansar:
            d.rekt(kx + sx, ky + sy, kx + sx + 2, ky + sy + 1, 0)
    d.markera("grandkatt", 74, 78, 92, 91)

    # --- Utgången mot Boulevarden (söderut, nederkanten) ---
    with d.yta("utgang:s"):
        d.rekt(116, 108, 166, 117, 2)
        d.rekt(117, 109, 165, 116, 12)
        text(d, 120, 110, "BOULEVARDEN", 15)
        d.rekt(116, 108, 166, 109, 10)
        # pil nedåt
        d.rekt(171, 104, 173, 110, 10)
        for i in range(4):
            d.rekt(168 + i, 110 + i, 176 - i, 111 + i, 10)
        d.rekt(140, 117, 142, H, 0)
    d.markera("utgang:s", 112, 106, 178, H)
    # Gatljuset från Boulevarden faller in nerifrån
    d.radial(140, H + 6, 40, 0.65, mask=(YY > MARK - 4) & (YY < 108))

    regn_over(d, random.Random(11), 90, regn)
    d.vinjett(0.4)
    return d


# ======================================================================
#  BRANDTRAPPAN, AVSATSEN PÅ TREDJE VÅNINGEN
# ======================================================================
def brandtrappa(v=None):
    v = v or {}
    regn = v.get("regn", 0)
    gardin = v.get("gardin", 0)       # 0..3
    rnd = random.Random(33)
    d = Duk(1)

    # --- Himmel och hustak ---
    d.vgrad(0, 0, W, 60, [0, 0, 1, 1, 2])
    for _ in range(18):
        d.px(rnd.randint(0, 100), rnd.randint(0, 20), 4)
    x = 0
    while x < 110:
        b = rnd.randint(10, 22)
        topp = rnd.randint(46, 62)
        d.rekt(x, topp, x + b, 90, 1)
        d.rekt(x, topp, x + b, topp + 1, 3)
        if rnd.random() < 0.7:
            cx = x + rnd.randint(2, max(3, b - 6))
            ch = rnd.randint(5, 10)
            d.rekt(cx, topp - ch, cx + 4, topp, 6)
            d.rekt(cx - 1, topp - ch, cx + 5, topp - ch + 1, 7)
        for wy in range(topp + 4, 90, 5):
            for wx in range(x + 2, x + b - 2, 4):
                if rnd.random() < 0.12:
                    d.rekt(wx, wy, wx + 2, wy + 2, 10)
        x += b
    # Rök ur en skorsten
    for (sx, sy) in [(30, 40), (31, 37), (33, 34), (34, 31), (36, 28)]:
        d.px(sx, sy, 3)

    # --- Fasadklockan bakifrån (vänster) ---
    with d.yta("klockbaksida"):
        d.rekt(0, 18, 46, 80, 2)                 # klocktornets sida
        d.rekt(44, 18, 46, 80, 1)
        d.rekt(0, 16, 48, 18, 3)
        cx, cy, r = 20, 44, 22
        _ellips(d, cx - r - 2, cy - r - 2, cx + r + 2, cy + r + 2, 0)
        _ellips(d, cx - r, cy - r, cx + r, cy + r, 10)    # upplyst glas bakifrån
        _ellips(d, cx - r + 3, cy - r + 3, cx + r - 3, cy + r - 3, 15)
        d.ljus(d.mask_ellips(cx - r, cy - r, cx + r, cy + r), 0.35, MORKARE)
        # Spegelvända timstreck
        for t in range(12):
            a = t * math.pi / 6
            for rr in (r - 4, r - 3):
                d.px(int(cx + rr * math.cos(a)), int(cy + rr * math.sin(a)), 8)
        # Visarna i silhuett (spegelvänt)
        d.linje(cx, cy, cx + 8, cy - 9, 7)
        d.linje(cx, cy, cx - 12, cy + 2, 7)
        # Maskineriet: kugghjul och axel
        for (gx, gy, gr, gc) in [(cx, cy, 8, 6), (cx + 10, cy + 10, 6, 7), (cx - 9, cy + 12, 5, 6)]:
            for t in range(12):
                a = t * math.pi / 6
                d.rekt(int(gx + (gr + 1) * math.cos(a)) - 1, int(gy + (gr + 1) * math.sin(a)) - 1,
                       int(gx + (gr + 1) * math.cos(a)) + 1, int(gy + (gr + 1) * math.sin(a)) + 1, gc)
            _ellips(d, gx - gr, gy - gr, gx + gr, gy + gr, gc)
            _ellips(d, gx - gr + 2, gy - gr + 2, gx + gr - 2, gy + gr - 2, 8 if gc == 7 else 7)
            _ellips(d, gx - 1, gy - 1, gx + 1, gy + 1, 9)
        d.rekt(cx - 1, cy - r - 4, cx + 2, cy, 6)    # axel upp i tornet
        d.rekt(cx - 1, cy - r - 4, cx, cy, 8)
        d.rekt(0, cy + r + 3, 46, cy + r + 6, 0)     # balk
        d.radial(cx, cy, 34, 0.35, mask=d.a < 4)

    # --- Husväggen med fönstret (höger) ---
    _tegel(d, 98, 0, W, 98, 7, 6, 0.45)
    d.rekt(98, 0, 100, 98, 6)
    fx0, fy0, fx1, fy1 = 112, 12, 176, 84
    with d.yta("fonster3"):
        d.rekt(fx0 - 4, fy0 - 4, fx1 + 4, fy1 + 2, 6)   # karm
        d.rekt(fx0 - 6, fy1, fx1 + 6, fy1 + 4, 4)       # fönsterbleck
        d.rekt(fx0 - 6, fy1, fx1 + 6, fy1 + 1, 5)
        d.rekt(fx0, fy0, fx1, fy1, 0)
        # Fördragna gardiner (mörkröda) bakom rutorna
        for gx in range(fx0, fx1):
            veck = (gx - fx0) % 6
            c = 13 if veck == 1 else (7 if veck in (0, 2) else 6)
            d.rekt(gx, fy0, gx + 1, fy1 - 10, c)
        d.ljus(d.mask_poly([(fx0, fy0), (fx1, fy0), (fx1, fy1), (fx0, fy1)]), 0.55, MORKARE)
        # Rutor: blänk av regnhimlen
        d.rekt(fx0, fy0, fx1, fy0 + 1, 3)
        for (gx, gy) in [(fx0 + 4, fy0 + 4), (fx0 + 36, fy0 + 6)]:
            d.linje(gx, gy + 6, gx + 6, gy, 4)
        # Spröjsar och den uppskjutna nedre bågen
        d.rekt(fx0, (fy0 + fy1) // 2 - 4, fx1, (fy0 + fy1) // 2 - 1, 6)
        d.rekt((fx0 + fx1) // 2 - 1, fy0, (fx0 + fx1) // 2 + 1, fy1 - 10, 6)
        d.rekt(fx0, fy1 - 12, fx1, fy1 - 10, 8)          # nedre bågens kant
        d.rekt(fx0, fy1 - 12, fx1, fy1 - 11, 9)
        # Springan: mörker inne och gardinen som fladdrar ut
        d.rekt(fx0, fy1 - 10, fx1, fy1, 0)
        flikar = [[2, 3, 4, 4, 3], [3, 5, 6, 5, 3], [4, 6, 7, 7, 5], [3, 4, 5, 6, 4]][gardin]
        for i, h in enumerate(flikar):
            gx = fx0 + 6 + i * 10
            d.rekt(gx, fy1 - 10, gx + 8, fy1 - 10 + h, 13)
            d.rekt(gx, fy1 - 10 + h - 1, gx + 8, fy1 - 10 + h, 6)
            d.px(gx + 2, fy1 - 10 + h, 6)
    d.markera("fonster3", fx0 - 4, fy0 - 4, fx1 + 4, fy1 + 2)

    # --- Avsatsen: galler, räcke ---
    d.rekt(0, 98, W, H, 0)
    for y in range(99, H, 3):
        d.rekt(0, y, W, y + 1, 2)
    for x in range(0, W, 4):
        d.rekt(x, 98, x + 1, H, 1)
    d.rekt(0, 96, W, 99, 3)
    d.rekt(0, 96, W, 97, 4)
    # Räcket i förgrunden mot gränden
    d.rekt(0, 74, 98, 76, 0)
    d.rekt(0, 74, 98, 75, 3)
    for px_ in range(2, 98, 6):
        d.rekt(px_, 74, px_ + 1, 98, 0)
    d.rekt(0, 86, 98, 87, 0)

    # --- Blomkrukan med den vissna pelargonen ---
    with d.yta("blomkruka"):
        d.poly([(82, 84), (98, 84), (96, 98), (84, 98)], 8)
        d.rekt(81, 82, 99, 85, 9)
        d.rekt(84, 86, 86, 96, 9)
        d.rekt(86, 82, 94, 83, 6)
        # Vissna stjälkar som hänger
        d.linje(88, 82, 86, 68, 7)
        d.linje(86, 68, 82, 70, 7)
        d.linje(91, 82, 93, 66, 7)
        d.linje(93, 66, 98, 70, 7)
        d.linje(90, 82, 90, 74, 7)
        for (lx, ly, lc) in [(81, 70, 8), (98, 70, 6), (88, 72, 12), (84, 76, 8), (95, 75, 9)]:
            d.rekt(lx - 1, ly, lx + 2, ly + 2, lc)
        d.rekt(98, 71, 100, 73, 13)                # en sista röd blomma, hängande
        d.px(84, 97, 9)                            # nedfallet blad
        d.px(80, 97, 8)

    # --- Stegen ner (genom luckan i gallret) ---
    with d.yta("utgang:ner"):
        d.rekt(22, 100, 56, H, 0)
        d.rekt(20, 99, 58, 101, 4)
        d.rekt(30, 100, 32, H, 3)
        d.rekt(46, 100, 48, H, 3)
        for sy in range(104, H, 5):
            d.rekt(30, sy, 48, sy + 1, 4)
        d.rekt(38, 102, 40, 108, 10)                 # pil nedåt
        for i in range(4):
            d.rekt(35 + i, 108 + i, 43 - i, 109 + i, 10)
        # handledare som sticker upp
        d.rekt(28, 82, 30, 100, 0)
        d.rekt(48, 82, 50, 100, 0)
        d.rekt(28, 82, 50, 84, 0)
        d.rekt(28, 82, 50, 83, 3)
    d.markera("utgang:ner", 20, 80, 58, H)

    # Fönsterljus från fastigheten mittemot mot väggen
    d.radial(150, 50, 60, 0.2, mask=(XX > 98) & (YY < 98))
    regn_over(d, random.Random(21), 100, regn)
    d.vinjett(0.45)
    return d


# ======================================================================
#  GÖMSTÄLLET: EN MÖRK LÄGENHET I FICKLAMPSSKEN
# ======================================================================
def gomstalle(v=None):
    v = v or {}
    ljus_ = v.get("ljus", 0)            # ljuskäglans darrning 0..3
    hattask_oppen = v.get("hattask", False)
    brev = v.get("brev", True)
    d = Duk(2)

    # --- Rummet (ritas i "upplysta" färger, mörkas sedan ner) ---
    d.vgrad(0, 0, W, 84, [3, 4, 4])
    for x in range(4, W, 10):                    # tapet med blommor
        for y in range(6, 82, 10):
            off = 5 if (y // 10) % 2 else 0
            d.px(x + off, y, 13)
            d.px(x + off + 1, y + 1, 12)
    for (fx, fy) in [(120, 30), (140, 52), (66, 60)]:   # fuktfläckar
        d.ljus(d.mask_ellips(fx, fy, fx + 14, fy + 10), 0.5, MORKARE)
    d.rekt(0, 80, W, 84, 7)
    d.rekt(0, 80, W, 81, 8)
    d.rekt(0, 84, W, H, 8)
    for y in range(86, H, 5):
        d.rekt(0, y, W, y + 1, 7)
    for i in range(-8, 12):
        d.linje(96 + i * 14, 84, 96 + i * 26, H, 7)
    d.poly([(110, 92), (150, 92), (158, 102), (104, 102)], 13)   # trasig matta
    d.poly([(112, 94), (148, 94), (154, 100), (108, 100)], 14)
    d.ljus(d.mask_poly([(110, 92), (158, 102), (104, 102)]), 0.4, MORKARE)

    # --- Garderoben med hattasken ---
    d.rekt(36, 22, 66, 88, 7)
    d.rekt(36, 22, 66, 24, 8)
    d.rekt(38, 26, 50, 84, 8)
    d.rekt(52, 26, 64, 84, 8)
    d.rekt(39, 27, 49, 83, 7)
    d.rekt(53, 27, 63, 83, 7)
    d.px(49, 54, 10)
    d.px(53, 54, 10)
    d.rekt(36, 86, 38, 90, 6)
    d.rekt(64, 86, 66, 90, 6)
    with d.yta("hattask"):
        hx0, hx1, hy = 39, 63, 10
        d.rekt(hx0, hy + 2, hx1, 22, 15)
        for sx in range(hx0, hx1, 4):
            d.rekt(sx, hy + 2, sx + 2, 22, 13)
        _ellips(d, hx0, 19, hx1 - 1, 23, 15)
        for sx in range(hx0 + 1, hx1, 4):
            d.rekt(sx, 20, sx + 2, 23, 13)
        if hattask_oppen:
            _ellips(d, hx0, hy, hx1 - 1, hy + 5, 6)          # öppen: mörkt inuti
            _ellips(d, hx0 + 2, hy + 1, hx1 - 3, hy + 5, 0)
            d.px(50, hy + 3, 15)                             # silkespapper
            d.px(52, hy + 2, 15)
            # Locket ligger snett på garderobens kant
            d.poly([(64, 18), (78, 14), (80, 18), (66, 22)], 15)
            d.poly([(64, 18), (78, 14), (78, 15), (64, 19)], 13)
            d.linje(66, 22, 80, 18, 9)
            d.rekt(70, 16, 73, 17, 10)
        else:
            _ellips(d, hx0 - 1, hy - 1, hx1, hy + 5, 15)     # locket
            _ellips(d, hx0 + 3, hy, hx1 - 4, hy + 3, 11)
            d.rekt(hx0 - 1, hy + 3, hx1, hy + 4, 13)
            d.rekt(49, hy - 2, 53, hy, 10)                   # knuten snodd
    d.markera("hattask", 38, 6, 64, 24)

    # --- Grammofonen på ett pallbord ---
    d.rekt(70, 66, 92, 68, 8)
    d.rekt(72, 68, 74, 88, 7)
    d.rekt(88, 68, 90, 88, 7)
    with d.yta("grammofon"):
        d.rekt(72, 56, 90, 66, 7)
        d.rekt(72, 56, 90, 57, 9)
        d.rekt(73, 58, 89, 59, 0)                # skivan
        d.px(90, 61, 10)
        d.rekt(90, 60, 93, 61, 10)               # vev
        d.rekt(92, 60, 93, 64, 10)
        d.linje(84, 56, 86, 46, 10)              # tonarm
        # Tratten
        d.poly([(86, 46), (82, 30), (96, 22), (100, 36)], 10)
        d.poly([(84, 30), (95, 24), (98, 34), (88, 40)], 9)
        _ellips(d, 80, 20, 100, 38, 10)
        _ellips(d, 83, 23, 97, 35, 8)
        _ellips(d, 86, 26, 94, 32, 6)
        d.linje(83, 33, 92, 22, 11)

    # --- Bordet med brevet ---
    d.rekt(96, 66, 132, 70, 8)
    d.rekt(96, 66, 132, 67, 9)
    d.rekt(98, 70, 100, 90, 7)
    d.rekt(128, 70, 130, 90, 7)
    d.rekt(110, 70, 112, 86, 6)
    d.rekt(122, 58, 126, 66, 15)             # en kopp kallt kaffe
    d.rekt(126, 60, 128, 63, 15)
    d.rekt(123, 59, 125, 60, 6)
    d.rekt(100, 62, 106, 66, 4)              # askkopp
    d.px(104, 61, 15)
    with d.yta("brev_f"):
        if brev:
            d.poly([(108, 63), (120, 61), (122, 66), (110, 67)], 15)
            d.linje(108, 63, 115, 65, 9)
            d.linje(115, 65, 120, 61, 9)
            d.rekt(117, 64, 119, 66, 13)     # röd frimärksfläck
        else:
            d.px(114, 66, 9)                 # bara en fläck på bordet
    d.markera("brev_f", 106, 58, 122, 68)

    # --- Kavajen på galge (vägghake) ---
    with d.yta("kavaj"):
        d.rekt(152, 12, 154, 15, 0)
        d.linje(153, 15, 146, 20, 9)
        d.linje(153, 15, 160, 20, 9)
        d.poly([(144, 20), (162, 20), (166, 52), (140, 52)], 9)
        for x in range(140, 167, 4):             # rutmönster
            for y in range(20, 52):
                if 0 <= x < W:
                    d.px(x, y, 13) if d.a[y, x] == 9 else None
        for y in range(22, 52, 4):
            for x in range(140, 167):
                if d.a[y, x] == 9:
                    d.px(x, y, 7)
        d.poly([(150, 20), (156, 20), (153, 34)], 6)   # slag
        d.rekt(140, 22, 143, 50, 8)
        d.rekt(163, 22, 166, 50, 8)
        d.px(153, 38, 10)
        d.px(153, 44, 10)
        d.rekt(156, 40, 161, 41, 15)             # näsduk i bröstfickan

    # --- Sängen, obäddad ---
    with d.yta("sang"):
        d.rekt(140, 60, 144, 98, 6)              # huvudgavel
        d.rekt(140, 58, 145, 60, 7)
        d.rekt(144, 74, 192, 90, 15)
        d.rekt(144, 88, 192, 92, 7)
        d.rekt(186, 70, 190, 98, 6)
        _ellips(d, 145, 68, 160, 78, 15)          # kudde
        _ellips(d, 147, 70, 158, 76, 11)
        # Hopkorvat täcke
        d.poly([(158, 76), (170, 70), (182, 74), (190, 80), (186, 90), (162, 90)], 5)
        d.linje(162, 82, 176, 76, 4)
        d.linje(172, 88, 186, 80, 4)
        d.poly([(176, 90), (184, 90), (182, 100), (174, 98)], 5)   # täcket hasar ner
        d.rekt(146, 92, 150, 98, 0)               # sko under sängen

    # --- Pianot av papp på golvet, noter utspridda ---
    with d.yta("piano"):
        d.poly([(56, 98), (102, 98), (106, 112), (52, 112)], 8)
        d.poly([(56, 98), (102, 98), (102, 100), (56, 100)], 6)
        d.poly([(58, 101), (101, 101), (103, 110), (55, 110)], 15)
        for i in range(12):
            x = 57 + i * 4
            d.linje(x, 110, x + 1, 101, 9)
        for i in range(11):
            if i % 7 in (2, 6):
                continue
            x = 60 + i * 4
            d.rekt(x, 101, x + 2, 105, 0)
        text(d, 70, 113, "PIANO", 7)              # pappen är textad för hand
        # Noter
        for (nx, ny, rot) in [(30, 100, 0), (112, 106, 1), (128, 98, 2), (40, 112, 1)]:
            d.poly([(nx, ny), (nx + 10, ny - rot), (nx + 11, ny + 8 - rot), (nx + 1, ny + 8)], 15)
            for k in range(3):
                d.linje(nx + 1, ny + 2 + k * 2, nx + 9, ny + 2 + k * 2 - rot, 4)
            d.px(nx + 4, ny + 3, 0)
            d.px(nx + 7, ny + 4 - rot, 0)

    # --- Ficklampans ljuskägla: mörka ned allt utanför ---
    dx, dy = [(0, 0), (1, 0), (1, 1), (0, 1)][ljus_]
    cx, cy, r = 116 + dx, 74 + dy, 48
    avst = np.sqrt((XX - cx) ** 2 + ((YY - cy) * 1.3) ** 2)
    kant = np.clip((avst - r) / 7, 0, 1)
    d.ljus(np.ones((H, W), bool), kant, MORKARE)
    d.ljus(avst > r + 7, 1.0, MORKARE)
    d.ljus(avst > r + 7, 0.3, MORKARE)
    d.ljus(avst < r - 18, np.clip((r - 18 - avst) / 10, 0, 0.5))

    # --- Fönstret man klev in genom (stadens blå sken) ---
    with d.yta("utgang:ut"):
        d.rekt(4, 12, 30, 64, 6)
        d.rekt(6, 14, 28, 62, 1)
        d.vgrad(6, 14, 28, 62, [1, 2, 3])
        for (bx, by, bh) in [(6, 40, 22), (14, 46, 16), (20, 36, 26)]:
            d.rekt(bx, by, bx + 6, by + bh, 0)
            d.px(bx + 2, by + 4, 10)
        d.rekt(6, 36, 28, 38, 6)                 # nedre båge uppskjuten
        regn_over(d, random.Random(5), 8, 0, 6, 14, 28, 62)
        d.rekt(16, 14, 18, 36, 6)
        # Gardinen som fladdrar in
        d.poly([(6, 14), (12, 14), (14, 40), (10, 58), (6, 60)], 3)
        d.linje(8, 16, 10, 56, 2)
        d.rekt(2, 62, 32, 65, 4)                 # fönsterbräda
        d.rekt(2, 62, 32, 63, 5)
        d.radial(17, 66, 18, 0.35, mask=(YY > 64) & (YY < 96) & (XX < 40))

    d.vinjett(0.3)
    return d


SCENER_C = {
    "pantbank": (pantbank, [
        ("flakt", "flakt", [(i, 140) for i in range(4)]),
        ("paraply", "paraply", [(True, 1000), (False, 1000)], 1),
        ("batterier", "batterier", [(True, 1000), (False, 1000)], 1),
    ]),
    "grand": (grand, [
        ("regn", "regn", [(i, 90) for i in range(10)]),
        ("anga", "anga", [(i, 200) for i in range(6)]),
        ("svans", "svans", [(0, 700), (1, 250), (2, 400), (1, 250), (0, 900), (3, 300)]),
        ("stege_ur", "stege_ur", [(False, 1000), (True, 1000)], 1),
        ("stege_tvatt", "stege_tvatt", [(False, 1000), (True, 1000)], 1),
    ]),
    "brandtrappa": (brandtrappa, [
        ("regn", "regn", [(i, 90) for i in range(10)]),
        ("gardin", "gardin", [(0, 900), (1, 300), (2, 400), (3, 300), (1, 300), (0, 1400)]),
    ]),
    "gomstalle": (gomstalle, [
        ("ljus", "ljus", [(0, 300), (1, 120), (0, 500), (2, 140), (3, 220), (0, 900)]),
        ("hattask", "hattask", [(False, 1000), (True, 1000)], 1),
        ("brev", "brev", [(True, 1000), (False, 1000)], 1),
    ]),
}
