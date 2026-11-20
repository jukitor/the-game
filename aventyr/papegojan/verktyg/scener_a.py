import math, random, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "motor" / "verktyg"))
from pixelbild import *  # noqa

"""Bilder till Papegojan som visste för mycket: perrongen vid Boulevarden, torget,
västra Boulevarden och mitten av Boulevarden."""

# ======================================================================
#  EGNA TECKEN (utöver motorns TYPSNITT) och hjälpfunktioner
# ======================================================================
EXTRA_A = {
    "7": ["111", "001", "010", "010", "010"],
    ".": ["0", "0", "0", "0", "1"],
    "Ä": ["101", "010", "101", "111", "101"],
    "2": ["110", "001", "010", "100", "111"],
    "J": ["001", "001", "001", "101", "010"],
    "K": ["101", "101", "110", "101", "101"],
}


def _glyf(ch):
    return EXTRA_A.get(ch) or TYPSNITT[ch]


def skriv(d, x, y, s, c):
    """Som text() men med de extra tecknen."""
    for ch in s:
        g = _glyf(ch)
        for ry, rad in enumerate(g):
            for rx, bit in enumerate(rad):
                if bit == "1":
                    d.px(x + rx, y + ry, c)
        x += len(g[0]) + 1


def bredd(s):
    return sum(len(_glyf(ch)[0]) + 1 for ch in s) - 1


def tegel(d, x0, y0, x1, y1, bas=7, mork=0.45, fog=6):
    d.rekt(x0, y0, x1, y1, bas)
    d.ljus(d.mask_poly([(x0, y0), (x1, y0), (x1, y1), (x0, y1)]), mork, MORKARE)
    for y in range(y0 + 2, y1, 3):
        off = 0 if (y // 3) % 2 else 3
        for xx in range(x0 + off, x1, 6):
            d.px(xx, y, fog)


def fonster(d, fx, fy, b, h, tand, gardin=True):
    d.rekt(fx - 1, fy - 1, fx + b + 1, fy + h + 1, 6)
    if tand:
        d.rekt(fx, fy, fx + b, fy + h, 10)
        d.rekt(fx, fy, fx + b, fy + 2, 11)
        if gardin:
            d.rekt(fx, fy + 2, fx + 1, fy + h, 9)
            d.rekt(fx + b - 1, fy + 2, fx + b, fy + h, 9)
        d.rekt(fx, fy + h - 2, fx + b, fy + h, 9)
    else:
        d.rekt(fx, fy, fx + b, fy + h, 1)
        d.px(fx + 1, fy + 1, 3)
    d.rekt(fx - 1, fy + h, fx + b + 1, fy + h + 1, 4)


def gatubas(d, ytr=92, yk=100):
    """Trottoar, kantsten och blank kullerstensgata."""
    d.vgrad(0, ytr, W, yk, [2, 3, 3])
    for xx in range(0, W, 12):
        d.rekt(xx, ytr, xx + 1, yk, 2)
    d.rekt(0, yk, W, yk + 1, 5)
    d.rekt(0, yk + 1, W, yk + 2, 4)
    d.vgrad(0, yk + 2, W, H, [0, 1, 1, 2])
    rad = (YY - yk - 4) // 3
    sten = (YY > yk + 3) & ((YY - yk - 4) % 3 == 0) & (((XX + (rad % 2) * 3) % 6) < 4)
    d.ljus(sten, 0.55)


def spegel(d, x0, x1, f, y0=102):
    for y in range(y0, H):
        s = f * (1 - (y - y0) / (H - y0))
        m = (XX >= x0) & (XX < x1) & (YY == y) & ((XX + y) % 2 == 0)
        d.ljus(m, s * 2)


def gatlykta(d, x, ytop, ybas=96, glod=True):
    """Gatlykta i art deco med varmt sken."""
    d.rekt(x, ytop, x + 2, ybas, 0)
    d.rekt(x - 1, ybas - 3, x + 3, ybas, 0)
    d.rekt(x - 1, ytop + 10, x + 3, ytop + 11, 0)
    d.rekt(x - 2, ytop - 8, x + 4, ytop - 7, 0)
    d.rekt(x - 1, ytop - 9, x + 3, ytop - 8, 0)
    d.rekt(x - 2, ytop - 7, x + 4, ytop - 1, 11 if glod else 4)
    d.rekt(x - 2, ytop - 2, x + 4, ytop - 1, 10)
    d.rekt(x - 1, ytop - 1, x + 3, ytop, 0)
    if glod:
        d.radial(x + 1, ytop - 4, 16, 0.55, mask=(d.a < 5) & (YY < ytop + 20))
        d.radial(x + 1, ybas, 24, 0.55, mask=(YY >= ybas - 4) & (YY < ybas + 5))
        spegel(d, x - 2, x + 5, 0.7)


def pilskylt(d, x, y, vanster):
    """Liten grön gatuskylt med pil på en stolpe, x = stolpens x."""
    d.rekt(x, y, x + 1, 97, 0)
    d.rekt(x - 1, 95, x + 2, 97, 0)
    sx0, sx1 = x - 6, x + 7
    d.rekt(sx0 - 1, y - 1, sx1 + 1, y + 8, 15)
    d.rekt(sx0, y, sx1, y + 7, 12)
    cy = y + 3
    d.rekt(sx0 + 2, cy, sx1 - 2, cy + 1, 15)
    for k in range(3):
        if vanster:
            d.rekt(sx0 + 2 + k, cy - k, sx0 + 3 + k, cy + 1 + k, 15)
        else:
            d.rekt(sx1 - 3 - k, cy - k, sx1 - 2 - k, cy + 1 + k, 15)


def regn(d, fas, antal=80, fro=7):
    regn_over(d, random.Random(fro), antal, fas)


# ======================================================================
#  PERRONGEN VID BOULEVARDEN
# ======================================================================
def linjekarta5(d, x, y, aktiv, rubrik="LINJE 2"):
    """Linjekarta med fem stationer på en linje. aktiv = 0..4 markerar var man är."""
    b = 44
    d.rekt(x - 1, y - 1, x + b + 1, y + 20, 0)
    d.rekt(x, y, x + b, y + 19, 15)
    d.rekt(x, y, x + b, y + 7, 12)
    skriv(d, x + (b - bredd(rubrik)) // 2 + 1, y + 1, rubrik, 15)
    ly = y + 12
    d.rekt(x + 3, ly, x + b - 3, ly + 1, 13)
    for i in range(5):
        sx = x + 4 + i * 9
        d.rekt(sx - 1, ly - 1, sx + 2, ly + 2, 0)
        c = 11 if i == aktiv else 15
        d.rekt(sx, ly, sx + 2 - 1, ly + 1, c)
        d.rekt(sx - 1, ly + 4, sx + 3, ly + 5, 4)
    ax = x + 4 + aktiv * 9
    d.rekt(ax - 1, ly - 3, ax + 3, ly - 2, 13)     # "Du är här"
    d.px(ax, ly - 2, 13)
    d.px(ax + 1, ly - 2, 13)


def spar(d, rnd, y0=96, slipers=6, rals=4):
    d.rekt(0, y0, W, H, 0)
    for x in range(rnd.randint(0, 5), W, 9):
        d.rekt(x, y0 + 6, x + 5, H, slipers)
        d.rekt(x, y0 + 6, x + 5, y0 + 7, 7)
    for ry in (y0 + 9, y0 + 18):
        d.rekt(0, ry, W, ry + 2, rals)
        d.rekt(0, ry, W, ry + 1, 5)


def plattformskant(d, y=92):
    d.rekt(0, y, W, y + 3, 10)
    for x in range(0, W, 4):
        d.px(x, y + 1, 9)
    d.rekt(0, y + 3, W, y + 4, 0)


def perrong_blvd(v=None):
    v = v or {}
    lampa = v.get("lampa", 1)       # glappande glob i taket
    fladder = v.get("fladder", 0)   # affischens lösa hörn 0..2
    rnd = random.Random(3101)
    d = Duk(15)

    # Krämvitt kakel
    d.rekt(0, 0, W, 76, 15)
    for y in range(8, 76, 4):
        d.rekt(0, y, W, y + 1, 9)
        for x in range(((y // 4) % 2) * 4, W, 8):
            d.rekt(x, y, x + 1, y + 4, 9)
    d.ljus(d.mask_poly([(0, 0), (W, 0), (W, 76), (0, 76)]), 0.3, MORKARE)
    for _ in range(12):
        sx, sy = rnd.randint(0, W - 8), rnd.randint(36, 70)
        d.ljus(d.mask_ellips(sx, sy, sx + rnd.randint(4, 10), sy + rnd.randint(6, 14)), 0.5, MORKARE)
    d.rekt(0, 0, W, 8, 1)
    d.rekt(0, 7, W, 8, 0)
    # Art deco-frisar i turkos med guldvinklar
    for (fy0, fy1) in ((9, 14), (62, 70)):
        d.rekt(0, fy0, W, fy1, 12)
        d.rekt(0, fy0, W, fy0 + 1, 10)
        d.rekt(0, fy1 - 1, W, fy1, 0)
        mid = (fy0 + fy1) // 2
        for x in range(0, W, 6):
            for k in range(3):
                d.px(x + k, mid - k + 1, 4)
                d.px(x + 5 - k, mid - k + 1, 4)
            d.px(x + 2, mid + 1, 15)
            d.px(x + 3, mid + 1, 15)
    # Kakelband med rutmönster under frisen
    for x in range(0, W, 4):
        d.rekt(x, 70, x + 2, 72, 12 if (x // 4) % 2 else 15)
    d.rekt(0, 72, W, 73, 0)

    # Emaljskylt BOULEVARDEN med solfjädrar
    cx = 96
    d.rekt(cx - 30, 17, cx + 30, 34, 12)
    d.rekt(cx - 29, 18, cx + 29, 33, 0)
    with d.yta("skylt_blvd"):
        x0, x1 = skylt(d, cx, 21, "BOULEVARDEN", 1, 15, 15, pad=3)
        for side, sx in ((-1, x0 - 3), (1, x1 + 2)):
            for k in range(4):
                d.linje(sx, 25, sx + side * 3, 19 + k * 3, 10)
            d.px(sx, 25, 11)
    # Stålpelare inklädda i kakel
    for bx in (60, 140):
        d.rekt(bx, 8, bx + 6, 92, 12)
        d.rekt(bx + 1, 8, bx + 2, 92, 4)
        d.rekt(bx + 5, 8, bx + 6, 92, 0)
        for ny in range(14, 90, 10):
            d.px(bx + 3, ny, 10)
        d.rekt(bx - 1, 8, bx + 7, 10, 10)

    # Linjekartan
    with d.yta("karta"):
        linjekarta5(d, 10, 18, 3)

    # Globlampor i taket
    for i, lx in enumerate((30, 100, 168)):
        d.rekt(lx, 8, lx + 1, 11, 0)
        tand = lampa if i == 1 else 1
        d.a[d.mask_ellips(lx - 3, 11, lx + 4, 17)] = 11 if tand else 4
        d.rekt(lx - 1, 11, lx + 2, 12, 10)
        if tand:
            d.radial(lx, 28, 34, 0.35, mask=(YY > 17) & (YY < 92), tabell=LJUSARE)

    # Golv
    d.rekt(0, 76, W, 92, 3)
    d.vgrad(0, 76, W, 92, [2, 3, 4])
    for y in range(78, 92, 4):
        d.rekt(0, y, W, y + 1, 2)
    d.rekt(0, 73, W, 76, 1)
    for _ in range(14):
        d.px(rnd.randint(4, W - 4), rnd.randint(80, 90), rnd.choice([13, 14, 15]))   # tuggummifläckar
    plattformskant(d)
    spar(d, rnd)

    # Tuggummiautomat på fot
    with d.yta("automat"):
        ax = 31
        d.rekt(ax - 1, 73, ax + 2, 88, 0)
        d.rekt(ax - 5, 87, ax + 6, 90, 0)
        d.rekt(ax - 6, 59, ax + 7, 73, 13)
        d.rekt(ax - 6, 59, ax + 7, 60, 14)
        d.rekt(ax + 5, 60, ax + 7, 73, 6)
        d.rekt(ax - 2, 62, ax + 3, 66, 9)     # myntvred
        d.rekt(ax - 1, 63, ax + 2, 65, 10)
        d.px(ax, 64, 11)
        d.rekt(ax - 2, 68, ax + 3, 72, 0)      # luckan
        d.rekt(ax - 1, 70, ax + 2, 71, 6)
        glob = d.mask_ellips(ax - 7, 42, ax + 8, 60)
        d.a[glob] = 2
        for _ in range(40):
            gx, gy = rnd.randint(ax - 6, ax + 6), rnd.randint(48, 59)
            if glob[gy, gx]:
                d.px(gx, gy, rnd.choice([13, 10, 14, 12, 15, 11]))
        d.px(ax - 4, 46, 11)
        d.px(ax - 5, 47, 5)
        d.px(ax - 5, 48, 5)
        d.rekt(ax - 3, 40, ax + 4, 43, 13)
        d.rekt(ax - 1, 39, ax + 2, 40, 13)
        d.rekt(ax - 3, 40, ax + 4, 41, 14)

    # Affischen: LOLA LARUE på Blue Oyster
    with d.yta("affisch"):
        px0, px1, py0, py1 = 74, 128, 37, 73
        d.rekt(px0 - 1, py0 - 1, px1 + 1, py1 + 1, 0)
        d.vgrad(px0, py0, px1, py1, [1, 1, 2, 1])
        # Strålkastarkägla över sångerskan
        d.ljus(d.mask_poly([(80, py0), (88, py0), (96, py1), (74, py1)]), 0.55)
        # Sångerskan i lång klänning vid mikrofonen
        d.a[d.mask_ellips(82, 41, 89, 49)] = 13           # håret
        d.a[d.mask_ellips(84, 43, 88, 48)] = 10           # ansiktet
        d.px(86, 46, 13)
        d.px(85, 44, 0)
        d.poly([(83, 49), (89, 49), (93, py1 - 1), (78, py1 - 1)], 13)
        d.linje(84, 50, 81, py1 - 2, 14)
        d.linje(85, 50, 83, 60, 14)
        d.rekt(84, 49, 88, 50, 10)                         # axlarna
        d.linje(89, 51, 92, 47, 10)                        # armen mot mikrofonen
        d.linje(94, 48, 94, py1 - 1, 4)                    # mikrofonstativ
        d.rekt(93, 45, 96, 48, 5)
        d.px(93, 45, 15)
        d.rekt(91, py1 - 2, 98, py1 - 1, 4)
        # Texten
        text_stor(d, 97, 40, "LOLA", 14, 2)
        text(d, 101, 52, "LARUE", 14)
        d.rekt(99, 59, 125, 60, 10)
        text(d, 104, 61, "BLUE", 10)
        text(d, 100, 67, "OYSTER", 10)
        # Lös hörn som fladdrar i draget
        if fladder == 1:
            d.poly([(px1, py1 - 6), (px1, py1), (px1 - 6, py1)], 15)
            d.linje(px1 - 6, py1, px1, py1 - 6, 9)
        elif fladder == 2:
            d.poly([(px1, py1 - 7), (px1 + 2, py1 - 1), (px1 - 7, py1 + 1)], 15)
            d.linje(px1 - 7, py1 + 1, px1, py1 - 7, 9)
        else:
            d.px(px1 - 1, py1 - 1, 15)
    # En sodaaffisch där någon ritat mustasch på flickan
    d.rekt(147, 37, 171, 63, 0)
    d.rekt(148, 38, 170, 62, 15)
    d.rekt(148, 38, 170, 45, 13)
    text(d, 152, 39, "SODA", 15)
    d.a[d.mask_ellips(153, 47, 165, 59)] = 9
    d.a[d.mask_ellips(155, 48, 163, 58)] = 10
    d.px(157, 51, 0)
    d.px(161, 51, 0)
    d.rekt(157, 55, 162, 56, 13)
    d.linje(155, 54, 159, 53, 0)                            # mustaschen
    d.linje(160, 53, 164, 54, 0)
    d.rekt(149, 59, 169, 61, 12)

    # Bänk vid väggen
    d.rekt(150, 78, 168, 80, 8)
    d.rekt(150, 78, 168, 79, 9)
    for lx in (152, 165):
        d.rekt(lx, 80, lx + 1, 88, 0)
    d.rekt(156, 76, 162, 78, 15)              # glömd tidning
    d.linje(157, 77, 161, 77, 4)

    # Trappan upp till gatan (utgång)
    with d.yta("utgang:upp"):
        x0, x1 = 174, 191
        d.rekt(x0, 40, x1, 92, 0)
        for k, y in enumerate(range(44, 92, 5)):
            d.rekt(x0 + 1, y, x1 - 1, y + 2, 2 + (k % 2))
            d.rekt(x0 + 1, y, x1 - 1, y + 1, 4)
        d.radial(182, 40, 18, 0.5, mask=(XX > x0) & (XX < x1) & (YY < 70))
        d.rekt(x0 - 1, 39, x0 + 1, 92, 12)
        d.rekt(x1 - 1, 39, x1 + 1, 92, 12)
        d.rekt(x0 - 1, 37, x1 + 1, 39, 12)
        d.rekt(x0 - 1, 37, x1 + 1, 38, 10)
        d.rekt(x0 + 1, 28, x1 - 1, 35, 1)
        text(d, x0 + 3, 29, "UPP", 15)
    d.markera("spar", 0, 97, W, H)
    d.vinjett(0.4)
    return d


# ======================================================================
#  TORGET (Boulevardens västra ände)
# ======================================================================
DUVA_UPP = ["......gg..", ".....gkgy.", "......n...", "dsssssn...", ".gddssgg..", "..ggggg...", "...r.r...."]
DUVA_NER = ["..........", "..........", "..sss.....", "dssssssg..", ".gddssgggg", "..gggg..gk", "...r.r...y"]


def duva(d, x, y, pick, vand=False, c=4):
    """Duva 10 x 7 px. pick: huvudet nere och pickar."""
    rader = DUVA_NER if pick else DUVA_UPP
    if vand:
        rader = [r[::-1] for r in rader]
    farg = {"g": c, "s": 5 if c != 15 else 15, "d": 3 if c != 15 else 5, "k": 0, "y": 10, "n": 12, "r": 13}
    t = Duk(16)
    sprite(t, x, y, rader, farg)
    kontur(d, t)


def staty(d):
    """Stadsgrundaren i brons med trekantig hatt, pekar dramatiskt mot nordost. Ritas med kontur."""
    t = Duk(16)
    t.poly([(98, 64), (100, 60), (107, 60), (109, 64)], 3)            # sten
    t.poly([(94, 38), (83, 60), (88, 61), (92, 52)], 7)               # fladdrande cape
    t.linje(94, 39, 84, 59, 8)
    t.rekt(93, 52, 96, 63, 7)                                         # bakre benet
    t.rekt(92, 62, 97, 64, 6)
    t.poly([(98, 52), (101, 52), (104, 58), (101, 59)], 7)            # främre benet på stenen
    t.rekt(101, 57, 104, 61, 7)
    t.rekt(101, 59, 106, 61, 6)
    t.poly([(91, 56), (93, 38), (101, 38), (104, 56)], 8)             # rocken
    t.linje(92, 55, 94, 39, 9)
    t.rekt(97, 46, 98, 56, 7)
    t.rekt(92, 47, 104, 48, 6)                                        # bälte
    t.px(99, 41, 10)
    t.px(99, 44, 10)
    t.poly([(92, 39), (88, 45), (90, 50), (93, 46)], 8)               # handen i sidan
    t.px(89, 46, 9)
    for off in range(3):                                              # pekande arm
        t.linje(100, 39 + off, 115, 26 + off, 8)
    t.linje(100, 39, 115, 26, 9)
    t.rekt(115, 24, 118, 28, 8)
    t.linje(117, 24, 121, 20, 8)
    t.px(116, 24, 9)
    t.rekt(95, 35, 100, 38, 7)                                        # hals
    t.a[t.mask_ellips(94, 29, 101, 37)] = 8                           # huvud
    t.px(101, 32, 9)
    t.px(102, 33, 9)
    t.px(100, 31, 0)
    t.rekt(93, 32, 95, 36, 7)
    t.poly([(90, 29), (105, 29), (101, 24), (94, 24)], 7)             # trekantig hatt
    t.linje(90, 29, 105, 29, 8)
    t.px(89, 28, 7)
    t.px(106, 28, 7)
    for (gx, gy, n) in ((94, 39, 8), (101, 41, 7), (96, 30, 4), (104, 50, 5)):   # ärg
        t.rekt(gx, gy, gx + 1, gy + n, 12)
    t.a[t.mask_ellips(94, 20, 100, 24)] = 5                           # duva på hatten
    t.rekt(99, 18, 102, 21, 5)
    t.px(101, 19, 0)
    t.px(102, 20, 9)
    t.rekt(92, 22, 95, 23, 4)
    t.px(96, 21, 4)
    for (sx, sy) in ((96, 25), (98, 26), (97, 27), (102, 39), (103, 40), (95, 33)):   # spillning
        t.px(sx, sy, 15)
    kontur(d, t)


def kontur(d, t, c=0):
    """Kopierar det som ritats på hjälpduken t (bakgrund 16) till d med en mörk kontur runt."""
    m = t.a != 16
    kant = m.copy()
    kant[1:, :] |= m[:-1, :]
    kant[:-1, :] |= m[1:, :]
    kant[:, 1:] |= m[:, :-1]
    kant[:, :-1] |= m[:, 1:]
    d.a[kant & ~m] = c
    d.a[m] = t.a[m]


def torget(v=None):
    v = v or {}
    regnfas = v.get("regn", 0)
    vatten = v.get("vatten", 0)     # fontänens fas 0..3
    pick = v.get("duvor", 0)        # duvornas pickande 0..5
    rnd = random.Random(3201)
    d = Duk(1)

    # --- Himmel med måne bakom moln ---
    d.vgrad(0, 0, W, 60, [0, 0, 1, 1, 2])
    d.a[d.mask_ellips(156, 2, 165, 11)] = 15
    d.px(159, 5, 5)
    d.px(161, 8, 5)
    d.ljus(d.mask_ellips(151, -2, 170, 15), 0.3)
    d.poly([(136, 10), (168, 7), (188, 10), (146, 12)], 1)
    # Avlägsna hus bakom fontänen
    x = 64
    while x < 134:
        b = rnd.randint(8, 14)
        topp = rnd.randint(30, 46)
        d.rekt(x, topp, x + b, 90, 1 + (x // 10) % 2)
        for wy in range(topp + 3, 84, 5):
            for wx in range(x + 2, x + b - 2, 4):
                if rnd.random() < 0.22:
                    d.rekt(wx, wy, wx + 2, wy + 2, 9)
        x += b

    # --- Rådhuset med klocktornet ---
    d.rekt(0, 34, 66, 90, 3)
    d.ljus(d.mask_poly([(0, 34), (66, 34), (66, 90), (0, 90)]), 0.35, MORKARE)
    for y in range(38, 90, 4):
        d.rekt(0, y, 66, y + 1, 2)
    d.rekt(0, 33, 66, 36, 4)
    d.rekt(0, 33, 66, 34, 5)
    d.rekt(8, 37, 58, 45, 2)
    text(d, 15, 39, "CITY HALL", 15)
    # Kolonner och höga fönster
    for kx in (4, 20, 42, 58):
        d.rekt(kx, 46, kx + 4, 84, 4)
        d.rekt(kx, 46, kx + 1, 84, 5)
        d.rekt(kx - 1, 45, kx + 5, 47, 5)
        d.rekt(kx - 1, 83, kx + 5, 85, 5)
    for fx in (10, 48):
        d.a[d.mask_ellips(fx - 1, 48, fx + 7, 56)] = 6
        d.a[d.mask_ellips(fx, 49, fx + 6, 55)] = 10
        d.rekt(fx - 1, 52, fx + 7, 70, 6)
        d.rekt(fx, 52, fx + 6, 69, 10)
        d.rekt(fx, 52, fx + 6, 54, 11)
        d.rekt(fx + 3, 49, fx + 4, 69, 9)
        d.rekt(fx, 60, fx + 6, 61, 9)
    # Portal
    d.a[d.mask_ellips(26, 50, 40, 64)] = 2
    d.rekt(26, 57, 40, 86, 2)
    d.a[d.mask_ellips(28, 52, 38, 62)] = 6
    d.rekt(28, 57, 38, 86, 6)
    d.rekt(32, 57, 34, 86, 7)
    d.px(31, 72, 10)
    d.px(34, 72, 10)
    for k, sy in enumerate((86, 88)):
        d.rekt(22 - k * 2, sy, 44 + k * 2, sy + 2, 4)
        d.rekt(22 - k * 2, sy, 44 + k * 2, sy + 1, 5)
    # Klocktornet
    d.rekt(17, 0, 45, 34, 3)
    d.rekt(17, 0, 18, 34, 4)
    d.rekt(44, 0, 45, 34, 2)
    d.rekt(15, 30, 47, 33, 4)
    d.rekt(15, 30, 47, 31, 5)
    with d.yta("radhusklocka"):
        cx, cy, r = 31, 16, 11
        d.a[d.mask_ellips(cx - r - 1, cy - r - 1, cx + r + 1, cy + r + 1)] = 9
        d.a[d.mask_ellips(cx - r, cy - r, cx + r, cy + r)] = 10
        d.a[d.mask_ellips(cx - r + 2, cy - r + 2, cx + r - 2, cy + r - 2)] = 11
        for i in range(12):
            a = i * math.pi / 6
            tx, ty = cx + 0.5 + (r - 2) * math.sin(a), cy + 0.5 - (r - 2) * math.cos(a)
            d.px(int(tx), int(ty), 0 if i % 3 == 0 else 9)
        # Visarna står på tio i tolv
        d.linje(cx, cy, cx, cy - 7, 0)
        d.linje(cx, cy, cx - 4, cy - 3, 0)
        d.px(cx, cy, 13)
    d.radial(31, 16, 24, 0.5, mask=(d.a < 5))

    # --- Pantbanken i hörnet ---
    tegel(d, 130, 20, 180, 92, 7, 0.5)
    for fy in (26, 40):
        for fx in (136, 152, 168):
            fonster(d, fx, fy, 7, 9, rnd.random() < 0.3)
    d.rekt(130, 52, 180, 54, 4)
    d.rekt(130, 52, 180, 53, 5)
    d.rekt(130, 54, 132, 92, 6)
    # Skyltfönster med pantade saker bakom galler
    d.rekt(134, 66, 150, 88, 6)
    d.rekt(135, 67, 149, 87, 9)
    d.vgrad(135, 67, 149, 87, [9, 8, 7])
    d.poly([(137, 76), (141, 70), (142, 71), (139, 77)], 10)     # saxofon
    d.rekt(138, 77, 141, 80, 10)
    d.a[d.mask_ellips(143, 76, 148, 81)] = 15                   # fickur
    d.px(145, 78, 0)
    d.rekt(136, 83, 148, 86, 6)                                 # hylla med ringar
    for rx in (137, 140, 144):
        d.px(rx, 82, 11)
    for gx in range(136, 150, 3):
        d.rekt(gx, 67, gx + 1, 87, 0)
    d.rekt(134, 88, 150, 90, 4)
    with d.yta("pantskylt"):
        d.rekt(134, 56, 178, 64, 0)
        d.rekt(134, 56, 178, 57, 10)
        d.rekt(134, 63, 178, 64, 9)
        skriv(d, 140, 58, "PANTBANK", 10)
        # Tre gyllene kulor på en konsol
        d.rekt(118, 36, 130, 37, 0)
        d.linje(126, 37, 130, 41, 0)
        d.rekt(123, 37, 124, 41, 0)
        for (kx, ky) in ((120, 42), (126, 42), (123, 48)):
            d.a[d.mask_ellips(kx - 3, ky - 3, kx + 3, ky + 3)] = 10
            d.px(kx - 1, ky - 1, 11)
            d.px(kx - 2, ky, 11)
            d.rekt(kx - 1, ky + 2, kx + 2, ky + 3, 9)
        d.linje(120, 37, 120, 39, 0)
        d.linje(126, 37, 126, 39, 0)
        d.linje(123, 37, 123, 45, 0)
    with d.yta("utgang:in"):
        d.rekt(154, 66, 172, 92, 6)
        d.rekt(156, 68, 170, 92, 7)
        d.rekt(157, 69, 169, 80, 9)
        d.vgrad(157, 69, 169, 80, [10, 9])
        d.rekt(162, 69, 164, 92, 6)
        d.rekt(157, 82, 162, 90, 8)
        d.rekt(164, 82, 169, 90, 8)
        d.px(160, 86, 11)
        d.px(166, 86, 11)
        d.rekt(157, 72, 169, 76, 15)
        d.rekt(152, 92, 174, 94, 4)
    d.radial(163, 76, 22, 0.35, mask=(YY > 60) & (YY < 100) & (d.a < 9))

    # --- Gatan fortsätter österut ---
    d.rekt(180, 20, W, 92, 1)
    d.vgrad(180, 20, W, 92, [0, 1, 2])
    for wy in range(30, 86, 6):
        d.px(186, wy, 9 if rnd.random() < 0.4 else 2)
    with d.yta("utgang:ö"):
        pilskylt(d, 185, 58, False)
        d.rekt(180, 88, W, 92, 2)
    d.markera("utgang:ö", 180, 50, W, 104)

    # --- Kullerstenstorget ---
    d.vgrad(0, 90, W, H, [2, 2, 1, 1])
    for i, y in enumerate(range(91, H, 3)):
        off = (i % 2) * 3
        stor = 6 if y < 100 else 7
        for xx in range(off - 6, W, stor):
            d.rekt(xx, y, xx + stor - 2, y + 2, 2)
            d.rekt(xx, y, xx + stor - 2, y + 1, 3)
    d.ljus(d.mask_poly([(0, 90), (W, 90), (W, H), (0, H)]), 0.35, MORKARE)
    d.radial(66, 106, 40, 0.5, mask=YY > 99)
    # Pölar som speglar klockan och pantbanken
    d.a[d.mask_ellips(18, 104, 46, 112)] = 1
    d.ljus(d.mask_ellips(24, 105, 40, 110), 0.5)
    d.a[d.mask_ellips(140, 106, 176, 116)] = 1
    spegel(d, 156, 170, 0.8, 106)
    d.ljus(d.mask_ellips(142, 107, 174, 115) & ((XX + YY) % 2 == 0), 0.35)

    # --- Gatlykta ---
    gatlykta(d, 66, 54, 96)
    gatlykta(d, 128, 60, 98)

    # --- Fontänen med stadsgrundaren ---
    with d.yta("fontan"):
        cx = 97
        d.a[d.mask_ellips(70, 86, 124, 106)] = 4
        d.a[d.mask_ellips(71, 86, 123, 103)] = 5
        d.a[d.mask_ellips(73, 87, 121, 100)] = 2
        d.ljus(d.mask_ellips(76, 88, 118, 99) & ((XX + YY) % 3 == 0), 0.6)
        # Sockel
        d.rekt(89, 64, 105, 95, 4)
        d.rekt(89, 64, 91, 95, 5)
        d.rekt(103, 64, 105, 95, 3)
        d.rekt(87, 62, 107, 65, 5)
        d.rekt(87, 64, 107, 65, 3)
        d.rekt(93, 70, 101, 76, 9)          # plakett
        d.rekt(94, 72, 100, 73, 8)
        d.rekt(94, 74, 99, 75, 8)
        for lx in (88, 105):                # lejonhuvuden
            d.rekt(lx - 1, 80, lx + 2, 84, 8)
            d.px(lx, 82, 0)
        staty(d)
        # Vattenstrålar
        for side in (-1, 1):
            x0 = 87 if side < 0 else 107
            for k in range(14):
                t = k / 13
                xx = x0 + side * t * 15
                yy = 82 - 6 * t + 18 * t * t
                if (k + vatten) % 4 == 3:
                    continue
                d.px(int(xx), int(yy), 15 if (k + vatten) % 4 == 0 else 5)
            sx = x0 + side * 15
            ring = [(0, 1), (1, 2), (2, 2), (1, 1)][vatten]
            d.rekt(sx - 1 - ring[0], 95, sx + 2 + ring[0], 96, 5)
            if ring[1] > 1:
                d.px(sx - 3 - ring[0], 96, 4)
                d.px(sx + 3 + ring[0], 96, 4)
        d.a[d.mask_ellips(71, 98, 123, 106) & ~d.mask_ellips(71, 86, 123, 103)] = 3
    d.radial(80, 40, 30, 0.35, mask=(YY < 66) & ((d.a == 7) | (d.a == 8)))

    # --- Bänken med damen som matar duvor ---
    with d.yta("dam"):
        d.rekt(6, 88, 44, 90, 6)         # ryggstöd
        d.rekt(6, 88, 44, 89, 7)
        d.rekt(6, 91, 44, 92, 6)
        d.rekt(6, 97, 44, 99, 6)         # sits
        d.rekt(6, 97, 44, 98, 7)
        for lx in (8, 41):
            d.rekt(lx, 92, lx + 1, 104, 0)
        # Damen sitter i profil och strör smulor
        dx = 18
        d.rekt(dx - 6, 92, dx - 1, 96, 13)    # handväskan bredvid henne
        d.rekt(dx - 5, 91, dx - 2, 92, 0)
        d.rekt(dx, 85, dx + 9, 97, 9)        # kappan
        d.rekt(dx + 1, 85, dx + 9, 86, 15)
        d.rekt(dx, 85, dx + 1, 97, 8)
        d.rekt(dx + 4, 86, dx + 5, 97, 8)
        d.px(dx + 8, 88, 10)
        d.px(dx + 8, 91, 10)
        d.rekt(dx + 3, 93, dx + 14, 97, 8)   # knän
        d.rekt(dx + 3, 93, dx + 14, 94, 9)
        d.rekt(dx + 11, 97, dx + 13, 103, 15)  # strumpor
        d.rekt(dx + 11, 103, dx + 16, 105, 0)  # skor
        d.rekt(dx + 3, 78, dx + 9, 85, 10)   # ansikte
        d.rekt(dx + 1, 78, dx + 4, 86, 15)   # vitt hår med knut
        d.rekt(dx, 81, dx + 2, 84, 15)
        d.px(dx + 7, 80, 0)                  # öga
        d.px(dx + 9, 81, 9)                  # näsa
        d.px(dx + 9, 82, 9)
        d.rekt(dx + 6, 83, dx + 8, 84, 14)   # rouge
        d.rekt(dx + 1, 74, dx + 9, 78, 13)   # hatt
        d.rekt(dx - 1, 77, dx + 11, 79, 13)
        d.rekt(dx - 1, 78, dx + 11, 79, 6)
        d.px(dx + 3, 74, 14)                 # blomma på hatten
        d.px(dx + 2, 73, 14)
        d.px(dx + 4, 73, 11)
        d.px(dx + 3, 72, 12)
        d.rekt(dx + 5, 90, dx + 9, 94, 15)   # brödpåsen i knät
        d.rekt(dx + 5, 90, dx + 9, 91, 9)
        d.linje(dx + 7, 87, dx + 15, 89, 8)  # armen som strör
        d.linje(dx + 7, 88, dx + 15, 90, 8)
        d.rekt(dx + 15, 88, dx + 17, 90, 10)
        for (sx, sy) in ((dx + 19, 88), (dx + 21, 90), (dx + 23, 87), (dx + 25, 91), (dx + 20, 93)):
            d.px(sx, sy, 15)
    # Brödsmulor
    for _ in range(12):
        d.px(rnd.randint(38, 96), rnd.randint(103, 118), 10)

    # --- Duvor som pickar ---
    with d.yta("duvor"):
        flock = [(40, 106, False), (54, 103, True), (60, 111, False), (72, 106, True),
                 (80, 112, False), (46, 113, True), (90, 107, True)]
        for i, (x, y, vand) in enumerate(flock):
            p = ((pick + i * 2) % 6) in (0, 1) if i % 2 == 0 else ((pick + i) % 6) == 3
            duva(d, x, y, p, vand, 15 if i == 3 else (4 if i % 2 else 5))
    d.markera("duvor", 40, 102, 96, 120)

    regn(d, regnfas, 75, 11)
    d.vinjett(0.4)
    return d


# ======================================================================
#  VÄSTRA BOULEVARDEN
# ======================================================================
def blvd_v(v=None):
    v = v or {}
    regnfas = v.get("regn", 0)
    visare = v.get("visare", 0)     # fasadklockans minutvisare som rycker 0..1
    lampa = v.get("fonster", 1)     # ett fönster som tänds och släcks
    rnd = random.Random(3301)
    d = Duk(1)

    d.vgrad(0, 0, W, 40, [0, 0, 1])

    # --- Huset längst till vänster (bara en flik) ---
    d.rekt(0, 10, 14, 92, 2)
    for fy in range(14, 84, 12):
        d.rekt(3, fy, 9, fy + 8, 9 if rnd.random() < 0.3 else 1)
    d.ljus(d.mask_poly([(0, 10), (14, 10), (14, 92), (0, 92)]), 0.4, MORKARE)

    # --- Urmakarens hus ---
    hx0, hx1 = 14, 110
    tegel(d, hx0, 0, hx1, 92, 8, 0.55)
    d.rekt(hx0, 0, hx0 + 2, 92, 6)
    d.rekt(hx1 - 2, 0, hx1, 92, 6)
    rader = [2, 14, 26, 38]
    kolumner = [20, 36, 52, 68, 86, 98]
    tanda = {(0, 1), (1, 4), (2, 0), (3, 3), (3, 5), (2, 5)}
    for r, fy in enumerate(rader):
        for k, fx in enumerate(kolumner):
            if r == 3 and k in (2, 3):
                continue                   # här sitter fasadklockan
            t = (r, k) in tanda
            if (r, k) == (1, 1):
                t = bool(lampa)
            fonster(d, fx, fy, 7, 8, t)
            if (r, k) == (0, 1):
                d.rekt(fx + 2, fy + 3, fx + 5, fy + 8, 7)   # någon som tittar ut
                d.rekt(fx + 3, fy + 2, fx + 5, fy + 4, 7)
    # Murkrön mellan bottenvåning och våningarna
    d.rekt(hx0, 50, hx1, 53, 15)
    d.rekt(hx0, 52, hx1, 53, 9)
    d.ljus(d.mask_poly([(hx0, 50), (hx1, 50), (hx1, 53), (hx0, 53)]), 0.5, MORKARE)

    # --- Urmakarbutiken ---
    d.rekt(16, 54, 72, 92, 12)
    d.rekt(16, 54, 72, 55, 4)
    d.ljus(d.mask_poly([(16, 54), (72, 54), (72, 92), (16, 92)]), 0.3, MORKARE)
    d.rekt(18, 55, 70, 68, 0)
    d.rekt(18, 55, 70, 56, 10)
    d.rekt(18, 67, 70, 68, 9)
    skriv(d, 32, 57, "O. TICK", 11)
    skriv(d, 28, 62, "URMAKARE", 10)
    for kx in (21, 66):
        d.px(kx, 58, 11)
        d.px(kx, 64, 11)
    with d.yta("skyltfonster_ur"):
        fx0, fx1, fy0, fy1 = 19, 51, 70, 88
        d.rekt(fx0 - 1, fy0 - 1, fx1 + 1, fy1 + 1, 9)
        d.rekt(fx0, fy0, fx1, fy1, 10)
        d.vgrad(fx0, fy0, fx1, fy1, [11, 10, 9])
        d.rekt(fx0, 81, fx1, 82, 7)               # hylla
        d.rekt(fx0, fy1 - 1, fx1, fy1, 7)
        # Klockor i alla storlekar, alla på olika tid
        for (kx, ky, r) in ((24, 76, 3), (31, 77, 2), (38, 76, 3), (46, 77, 2), (23, 85, 2), (35, 85, 2), (43, 85, 2)):
            d.a[d.mask_ellips(kx - r - 1, ky - r - 1, kx + r + 1, ky + r + 1)] = 7 if r < 4 else 6
            d.a[d.mask_ellips(kx - r, ky - r, kx + r, ky + r)] = 15
            a = rnd.random() * 2 * math.pi
            d.linje(kx, ky, int(round(kx + (r - 1) * math.sin(a))), int(round(ky - (r - 1) * math.cos(a))), 0)
            d.px(kx, ky - r + 1 if r > 2 else ky, 0)
        # Golvur i hörnet
        d.rekt(48, 76, 51, 88, 6)
        d.px(49, 78, 15)
        # Ficklur som hänger i kedjor
        for (ux, uy) in ((29, 83), (40, 83)):
            d.rekt(ux, 82, ux + 1, uy + 1, 9)
        d.px(fx0 + 1, fy0 + 1, 11)
    d.radial(35, 80, 28, 0.5, mask=(YY > 86) & (YY < 100))
    spegel(d, 19, 51, 0.6)
    with d.yta("utgang:in"):
        d.rekt(54, 66, 70, 92, 6)
        d.rekt(56, 68, 68, 92, 7)
        d.rekt(57, 69, 67, 79, 10)
        d.vgrad(57, 69, 67, 79, [10, 9])
        d.rekt(57, 81, 67, 90, 8)
        d.px(66, 84, 11)
        d.rekt(59, 71, 65, 75, 15)             # liten skylt i dörren
        d.rekt(60, 72, 64, 73, 13)
        d.rekt(60, 74, 63, 75, 13)
        d.rekt(54, 92, 70, 94, 4)

    # --- Fasadklockan på konsol ---
    with d.yta("fasadklocka"):
        cx, cy, r = 62, 41, 8
        d.rekt(54, 49, 70, 51, 0)                 # konsol
        d.linje(56, 51, 62, 49, 0)
        d.linje(68, 51, 62, 49, 0)
        d.rekt(61, 49, 63, 52, 9)
        d.a[d.mask_ellips(cx - r - 3, cy - r - 1, cx + r + 3, cy + r + 1)] = 0
        for (ox, oy) in ((cx - r - 3, cy), (cx + r + 3, cy), (cx, cy - r - 3)):
            d.a[d.mask_ellips(ox - 2, oy - 2, ox + 2, oy + 2)] = 9   # krusiduller
            d.px(ox, oy, 10)
        d.a[d.mask_ellips(cx - r - 1, cy - r - 1, cx + r + 1, cy + r + 1)] = 9
        d.a[d.mask_ellips(cx - r, cy - r, cx + r, cy + r)] = 10
        d.a[d.mask_ellips(cx - r + 1, cy - r + 1, cx + r - 1, cy + r - 1)] = 15
        d.a[d.mask_ellips(cx - r + 2, cy - r + 2, cx + r - 2, cy + r - 2)] = 11
        for i in range(12):
            a = i * math.pi / 6
            d.px(int(cx + 0.5 + (r - 2) * math.sin(a)), int(cy + 0.5 - (r - 2) * math.cos(a)), 0 if i % 3 == 0 else 9)
        d.linje(cx, cy, cx + 3, cy + 2, 0)      # timvisaren
        mv = [(cx - 2, cy - 6), (cx - 3, cy - 5)][visare]
        d.linje(cx, cy, mv[0], mv[1], 13)       # minutvisaren
        d.px(cx, cy, 0)
    d.radial(62, 41, 20, 0.35, mask=d.a < 9)

    # --- Porten nummer 7 och porttelefonen ---
    d.rekt(74, 56, 94, 92, 15)
    d.ljus(d.mask_poly([(74, 56), (94, 56), (94, 92), (74, 92)]), 0.55, MORKARE)
    d.a[d.mask_ellips(77, 58, 91, 72)] = 6
    d.rekt(77, 65, 91, 92, 6)
    d.a[d.mask_ellips(78, 59, 90, 71)] = 2
    d.rekt(78, 66, 90, 92, 7)
    d.rekt(78, 64, 90, 66, 6)
    d.a[d.mask_ellips(80, 60, 88, 68)] = 9                    # överljus
    d.rekt(80, 64, 88, 65, 9)
    for sx in (82, 84, 86):
        d.linje(84, 64, sx + (sx - 84), 60, 6)
    d.rekt(79, 67, 84, 90, 8)
    d.rekt(84, 67, 89, 90, 8)
    d.rekt(84, 67, 85, 90, 6)
    d.rekt(80, 69, 83, 77, 6)
    d.rekt(85, 69, 88, 77, 6)
    d.px(83, 80, 10)
    d.px(85, 80, 10)
    d.rekt(76, 92, 92, 94, 4)
    # Husnummer 7 på emaljskylt
    d.rekt(79, 46, 90, 58, 15)
    d.rekt(80, 47, 89, 57, 1)
    d.rekt(82, 49, 88, 51, 15)
    for k, sx in enumerate((86, 86, 85, 85, 84, 84)):
        d.rekt(sx, 51 + k, sx + 2, 52 + k, 15)
    with d.yta("porttelefon"):
        tx0, tx1, ty0, ty1 = 95, 106, 66, 84
        d.rekt(tx0 - 1, ty0 - 1, tx1 + 1, ty1 + 1, 0)
        d.rekt(tx0, ty0, tx1, ty1, 9)
        d.rekt(tx0 + 1, ty0 + 1, tx1 - 1, ty1 - 1, 8)
        for i in range(4):
            y = ty0 + 2 + i * 3
            d.rekt(tx0 + 2, y, tx0 + 7, y + 2, 15)
            d.rekt(tx0 + 3, y, tx0 + 6, y + 1, 4)
            d.rekt(tx0 + 8, y, tx0 + 10, y + 2, 6)
            d.px(tx0 + 8, y, 11)
        for gx in range(tx0 + 2, tx1 - 1, 2):     # högtalargaller
            d.px(gx, ty0 + 15, 0)
            d.px(gx + 1, ty0 + 16, 0)
    d.radial(100, 74, 10, 0.3, mask=d.a < 9)

    # --- Gränden ---
    with d.yta("utgang:n"):
        d.rekt(110, 18, 126, 96, 0)
        d.poly([(110, 96), (126, 96), (121, 70), (115, 70)], 1)
        d.rekt(115, 40, 121, 70, 1)
        d.rekt(116, 56, 120, 70, 2)
        d.radial(118, 62, 10, 0.8, mask=(XX > 114) & (XX < 122) & (YY > 50) & (YY < 80))
        d.rekt(117, 54, 119, 56, 11)             # avlägsen lampa
        for y in range(30, 90, 8):              # brandstege
            d.rekt(110, y, 114, y + 1, 2)
        d.linje(113, 30, 113, 90, 2)
        d.rekt(121, 84, 125, 94, 3)              # soptunna
        d.rekt(120, 83, 126, 84, 4)
        d.px(122, 82, 15)
        d.px(124, 89, 10)                        # kattögon
        d.px(123, 89, 10)
    d.markera("utgang:n", 110, 46, 127, 96)

    # --- Grannhuset i art deco ---
    gx0, gx1 = 126, 182
    d.rekt(gx0, 4, gx1, 92, 3)
    d.vgrad(gx0, 4, gx1, 92, [3, 2, 2])
    for px_ in range(gx0 + 2, gx1, 12):
        d.rekt(px_, 4, px_ + 2, 92, 4)
        d.rekt(px_ + 2, 4, px_ + 3, 92, 2)
    for fy in (8, 22, 36, 50):
        for fx in range(gx0 + 6, gx1 - 6, 12):
            fonster(d, fx, fy, 5, 9, rnd.random() < 0.3, gardin=False)
    d.rekt(gx0, 62, gx1, 64, 10)
    d.rekt(gx0, 64, gx1, 65, 9)
    # Barberare med stängd jalusi och strandad stolpe
    d.rekt(132, 68, 170, 92, 2)
    for y in range(69, 92, 2):
        d.rekt(133, y, 169, y + 1, 3)
    d.rekt(132, 66, 170, 68, 0)
    d.rekt(172, 68, 176, 84, 15)
    for y in range(68, 84, 3):
        d.linje(172, y, 175, y + 3, 13)
    d.rekt(172, 66, 176, 68, 9)
    d.rekt(172, 84, 176, 86, 9)

    # Skylt GRÄND på hörnet
    with d.yta("utgang:n"):
        d.rekt(105, 44, 131, 55, 15)
        d.rekt(106, 45, 130, 54, 12)
        text(d, 108, 48, "GRAND", 15)
        d.px(116, 46, 15)
        d.px(118, 46, 15)
        d.rekt(117, 55, 119, 57, 0)

    # --- Huset till höger och gatan österut ---
    d.rekt(182, 14, W, 92, 1)
    for fy in range(18, 84, 11):
        d.rekt(185, fy, 190, fy + 7, 9 if rnd.random() < 0.3 else 2)

    gatubas(d)
    spegel(d, 57, 67, 0.5)
    spegel(d, 80, 88, 0.3)
    gatlykta(d, 140, 48, 96)
    # Utgångar åt sidorna
    with d.yta("utgang:v"):
        pilskylt(d, 4, 74, True)
    d.markera("utgang:v", 0, 70, 12, H)
    with d.yta("utgang:ö"):
        pilskylt(d, 186, 74, False)
    d.markera("utgang:ö", 180, 70, W, H)

    regn(d, regnfas, 85, 13)
    d.vinjett(0.4)
    return d


# ======================================================================
#  MITTEN AV BOULEVARDEN
# ======================================================================
def blvd_m(v=None):
    v = v or {}
    regnfas = v.get("regn", 0)
    anga = v.get("anga", 0)        # ånga från gallret 0..5
    vift = v.get("vift", 0)        # tidningsförsäljaren viftar 0..2
    rnd = random.Random(3401)
    d = Duk(1)

    d.vgrad(0, 0, W, 40, [0, 0, 1])

    # --- Fasader ---
    tegel(d, 0, 6, 62, 92, 7, 0.55)
    for fy in (10, 26, 42):
        for fx in (6, 20, 34, 48):
            fonster(d, fx, fy, 7, 10, rnd.random() < 0.35)
    # Kaféhuset i ljus sten
    d.rekt(62, 0, 122, 92, 4)
    d.vgrad(62, 0, 122, 92, [3, 4, 3])
    d.ljus(d.mask_poly([(62, 0), (122, 0), (122, 92), (62, 92)]), 0.35, MORKARE)
    for fy in (2, 18, 34):
        for fx in (68, 84, 100):
            fonster(d, fx, fy, 9, 11, rnd.random() < 0.45)
            d.rekt(fx - 2, fy + 12, fx + 11, fy + 13, 5)
    # Huset med tunnelbanan
    d.rekt(122, 2, W, 92, 2)
    for px_ in range(124, W, 14):
        d.rekt(px_, 2, px_ + 1, 92, 3)
    for fy in (6, 20, 34, 48):
        for fx in range(128, W - 4, 14):
            fonster(d, fx, fy, 6, 9, rnd.random() < 0.3, gardin=False)
    d.ljus(d.mask_poly([(122, 2), (W, 2), (W, 92), (122, 92)]), 0.3, MORKARE)
    # Neon för ett hotell högt upp

    # --- Kaféet ---
    with d.yta("kafe"):
        d.rekt(64, 66, 120, 92, 10)
        d.vgrad(64, 66, 120, 92, [11, 10, 10, 9])
        d.rekt(64, 80, 120, 81, 8)                  # disk
        for (gx, gh) in ((70, 0), (86, 1), (104, 0)):  # gäster
            d.rekt(gx, 72 - gh, gx + 5, 80, 7)
            d.rekt(gx + 1, 69 - gh, gx + 4, 72 - gh, 7)
            d.rekt(gx, 68 - gh, gx + 5, 69 - gh, 6)
        d.rekt(95, 74, 99, 77, 15)                   # kaffekopp på disken
        d.px(96, 72, 5)
        d.px(97, 71, 5)
        d.rekt(64, 66, 66, 92, 6)
        d.rekt(118, 66, 120, 92, 6)
        d.rekt(91, 66, 92, 92, 6)
        d.rekt(64, 88, 120, 92, 6)
        # Markis med ränder
        for i, xx in enumerate(range(62, 122, 4)):
            d.poly([(xx, 55), (xx + 4, 55), (xx + 5, 62), (xx + 1, 62)], 12 if i % 2 == 0 else 15)
        d.rekt(63, 62, 123, 66, 12)
        d.rekt(63, 65, 123, 66, 6)
        for xx in range(64, 122, 4):
            d.px(xx + 1, 66, 12)
        # Neonskylt CAFÉ ovanför markisen
        d.rekt(80, 46, 105, 55, 0)
        d.rekt(80, 46, 105, 47, 13)
        d.rekt(80, 54, 105, 55, 13)
        text(d, 85, 48, "CAFE", 14)
        d.px(98, 46, 14)                             # akut accent
        d.px(99, 45, 14)
        d.radial(92, 50, 22, 0.45, mask=(d.a < 6) & ((YY < 46) | (YY > 54) | (XX < 80) | (XX > 104)))
        # Bord och stolar på trottoaren
        d.rekt(100, 88, 110, 89, 15)
        d.rekt(104, 89, 106, 97, 0)
        d.rekt(102, 96, 108, 97, 0)
        for sx in (96, 112):
            d.rekt(sx, 90, sx + 1, 97, 0)
            d.rekt(sx, 92, sx + 3, 93, 0) if sx == 96 else d.rekt(sx - 2, 92, sx + 1, 93, 0)
            d.rekt(sx + (2 if sx == 96 else -2), 93, sx + (3 if sx == 96 else -1), 97, 0)
    d.radial(92, 80, 40, 0.5, mask=(YY > 91) & (YY < 102))
    spegel(d, 66, 118, 0.55)

    # --- Tidningskiosken med försäljaren ---
    with d.yta("tidningsforsaljare"):
        kx0, kx1 = 14, 46
        d.poly([(kx0 - 3, 58), (kx1 + 3, 58), (kx1, 52), (kx0, 52)], 12)   # tak
        d.rekt(kx0 - 3, 58, kx1 + 3, 60, 6)
        d.rekt(kx0, 60, kx1, 96, 8)
        d.rekt(kx0, 60, kx1, 61, 9)
        d.rekt(kx0 + 3, 62, kx1 - 3, 74, 0)                                # luckan
        d.rekt(kx0 + 4, 63, kx1 - 4, 74, 6)
        d.radial(30, 66, 14, 0.6, mask=(XX > kx0 + 3) & (XX < kx1 - 3) & (YY > 61) & (YY < 75))
        for i, mx in enumerate(range(kx0 + 6, kx1 - 5, 5)):                # tidskrifter
            d.rekt(mx, 66, mx + 4, 72, [13, 10, 14, 5, 12][i % 5])
            d.rekt(mx + 1, 67, mx + 3, 68, 15)
        d.rekt(28, 62, 31, 64, 11)                                         # glödlampa
        d.rekt(kx0 - 1, 74, kx1 + 1, 76, 7)
        d.rekt(kx0 - 1, 74, kx1 + 1, 75, 9)
        # Tidningar i stack och på klädnypor
        for i, tx in enumerate(range(kx0 + 2, kx1 - 2, 7)):
            d.rekt(tx, 78, tx + 6, 86, 15)
            d.rekt(tx, 78, tx + 6, 80, 13 if i % 2 else 1)
            d.rekt(tx + 1, 82, tx + 5, 83, 4)
            d.rekt(tx + 1, 84, tx + 4, 85, 4)
        d.rekt(kx0 + 2, 88, kx1 - 2, 96, 7)
        d.rekt(kx0 + 2, 88, kx1 - 2, 90, 15)
        text(d, 22, 53, "NEWS", 15)
        # Försäljaren med keps
        fx = 48
        d.rekt(fx + 1, 74, fx + 7, 76, 2)          # keps
        d.rekt(fx, 75, fx + 9, 76, 2)
        d.rekt(fx + 2, 76, fx + 7, 81, 10)          # ansikte
        d.px(fx + 5, 77, 0)
        d.px(fx + 2, 79, 9)
        d.rekt(fx + 3, 80, fx + 7, 81, 9)            # öppen mun som ropar
        d.px(fx + 6, 80, 0)
        d.rekt(fx + 1, 81, fx + 9, 92, 7)            # jacka
        d.rekt(fx + 4, 81, fx + 5, 92, 6)
        d.rekt(fx + 1, 82, fx + 3, 86, 15)           # väska med tidningar
        d.rekt(fx + 1, 92, fx + 4, 97, 2)
        d.rekt(fx + 5, 92, fx + 8, 97, 2)
        d.rekt(fx, 97, fx + 4, 98, 0)
        d.rekt(fx + 5, 97, fx + 9, 98, 0)
        # Armen med tidningen som viftas
        hand = [(fx + 11, 78), (fx + 12, 74), (fx + 11, 71)][vift]
        d.linje(fx + 8, 83, hand[0], hand[1], 7)
        d.linje(fx + 9, 83, hand[0] + 1, hand[1], 7)
        tx, ty = hand[0] - 1, hand[1] - 6
        d.rekt(tx, ty, tx + 6, ty + 6, 15)
        d.rekt(tx, ty, tx + 6, ty + 1, 13)
        d.rekt(tx + 1, ty + 2, tx + 5, ty + 3, 0)
        d.rekt(tx + 1, ty + 4, tx + 4, ty + 5, 4)
        d.px(hand[0], hand[1], 10)

    # --- Tunnelbaneingången ---
    with d.yta("utgang:ner"):
        sx0, sx1 = 128, 166
        d.rekt(sx0, 80, sx1, 96, 0)
        for y in range(82, 96, 3):
            d.rekt(sx0 + 2, y, sx1 - 2, y + 1, 1)
        d.rekt(sx0 - 2, 76, sx1 + 2, 78, 12)
        for xx in range(sx0, sx1 + 1, 4):
            d.rekt(xx, 78, xx + 1, 80, 12)
        for px_ in (sx0 - 2, sx1):
            d.rekt(px_, 56, px_ + 2, 96, 12)
            d.rekt(px_ - 1, 51, px_ + 3, 56, 10)
            d.rekt(px_, 50, px_ + 2, 51, 11)
            d.radial(px_ + 1, 53, 9, 0.6, mask=d.a < 5)
        d.rekt(sx0 + 1, 61, sx1 - 1, 70, 15)
        d.rekt(sx0 + 2, 62, sx1 - 2, 69, 1)
        d.rekt(sx0 + 1, 61, sx1 - 1, 62, 10)
        text(d, 136, 63, "SUBWAY", 15)
        d.px(sx0 + 3, 65, 13)
        d.px(sx1 - 4, 65, 13)

    gatubas(d)
    d.radial(30, 66, 30, 0.35, mask=(YY > 91) & (YY < 101))

    # --- Brandposten ---
    with d.yta("brandpost"):
        bx = 174
        d.rekt(bx, 84, bx + 7, 98, 13)
        d.rekt(bx + 5, 84, bx + 7, 98, 6)
        d.rekt(bx + 1, 84, bx + 2, 98, 14)
        d.a[d.mask_ellips(bx, 79, bx + 7, 87)] = 13
        d.rekt(bx + 3, 78, bx + 4, 80, 13)
        d.rekt(bx - 2, 87, bx + 9, 90, 13)
        d.rekt(bx - 2, 87, bx + 9, 88, 14)
        d.rekt(bx - 2, 88, bx - 1, 90, 9)
        d.rekt(bx + 8, 88, bx + 9, 90, 9)
        d.rekt(bx - 1, 97, bx + 8, 99, 6)
        d.px(bx + 1, 81, 14)
        # En hund har gjort sitt
        d.rekt(bx - 4, 98, bx, 99, 2)
    spegel(d, 174, 181, 0.4)

    # --- Gatlyktor ---
    gatlykta(d, 120, 48, 96)

    # --- Galler med ånga ---
    d.rekt(78, 108, 104, 112, 0)
    for gx in range(79, 104, 2):
        d.rekt(gx, 109, gx + 1, 111, 3)
    for k in range(7):
        fas = (anga + k * 6 / 7) % 6
        cy = 106 - fas * 4.2
        cx = 91 + 3 * math.sin(fas * 1.3 + k)
        r = 3 + fas * 0.9
        styrka = 0.95 - fas * 0.14
        puff = d.mask_ellips(cx - r * 1.4, cy - r, cx + r * 1.4, cy + r)
        d.ljus(puff, styrka)
        d.ljus(puff, styrka * 0.6)

    # --- Utgångar åt sidorna ---
    with d.yta("utgang:v"):
        pilskylt(d, 5, 74, True)
    d.markera("utgang:v", 0, 70, 12, H)
    with d.yta("utgang:ö"):
        pilskylt(d, 186, 74, False)
    d.markera("utgang:ö", 182, 70, W, H)

    regn(d, regnfas, 85, 17)
    d.vinjett(0.4)
    return d


SCENER_A = {
    "p_blvd": (perrong_blvd, [
        ("lampa", "lampa", [(1, 2600), (0, 90), (1, 70), (0, 260), (1, 1800), (0, 110)]),
        ("fladder", "fladder", [(0, 1600), (1, 180), (2, 220), (1, 180), (0, 900), (1, 200), (0, 2400)]),
    ]),
    "torget": (torget, [
        ("regn", "regn", [(i, 90) for i in range(10)]),
        ("vatten", "vatten", [(i, 150) for i in range(4)]),
        ("duvor", "duvor", [(i, 260) for i in range(6)]),
    ]),
    "blvd_v": (blvd_v, [
        ("regn", "regn", [(i, 90) for i in range(10)]),
        ("visare", "visare", [(0, 1100), (1, 140), (0, 900), (1, 160), (0, 2000)]),
        ("fonster", "fonster", [(1, 4800), (0, 3600)]),
    ]),
    "blvd_m": (blvd_m, [
        ("regn", "regn", [(i, 90) for i in range(10)]),
        ("anga", "anga", [(i, 200) for i in range(6)]),
        ("vift", "vift", [(0, 500), (1, 160), (2, 220), (1, 160), (2, 220), (1, 160), (0, 1400)]),
    ]),
}
