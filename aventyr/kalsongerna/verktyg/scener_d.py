import math, random, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "motor" / "verktyg"))
from pixelbild import *  # noqa

"""Scener D: ångtvätteriet, radiostationen WGHR, bakgatan i Chinatown, örtapoteket
och den hemliga spelhålan."""

# ======================================================================
#  EGNA TECKEN OCH HJÄLPFUNKTIONER
# ======================================================================
EXTRA_D = {
    "X": ["101", "101", "010", "101", "101"],
    "2": ["110", "001", "010", "100", "111"],
    "0": ["010", "101", "101", "101", "010"],
    "4": ["101", "101", "111", "001", "001"],
    "5": ["111", "100", "110", "001", "110"],
    "6": ["011", "100", "110", "101", "010"],
    "7": ["111", "001", "010", "010", "010"],
    "8": ["010", "101", "010", "101", "010"],
    ".": ["0", "0", "0", "0", "1"],
    "<": ["001", "010", "100", "010", "001"],
    ">": ["100", "010", "001", "010", "100"],
}


def _glyf(ch):
    return EXTRA_D.get(ch) or TYPSNITT[ch]


def skriv(d, x, y, s, c):
    for ch in s:
        g = _glyf(ch)
        for ry, rad in enumerate(g):
            for rx, bit in enumerate(rad):
                if bit == "1":
                    d.px(x + rx, y + ry, c)
        x += len(g[0]) + 1


def bredd(s):
    return sum(len(_glyf(ch)[0]) + 1 for ch in s) - 1


def ell(d, x0, y0, x1, y1, c):
    d.a[d.mask_ellips(x0, y0, x1, y1)] = c


def ring(d, x0, y0, x1, y1, c, tjock=1):
    m = d.mask_ellips(x0, y0, x1, y1) & ~d.mask_ellips(x0 + tjock, y0 + tjock, x1 - tjock, y1 - tjock)
    d.a[m] = c


def ruta(x0, y0, x1, y1):
    return (XX >= x0) & (XX < x1) & (YY >= y0) & (YY < y1)


def tegel(d, x0, y0, x1, y1, bas=7, mork=0.45, fog=6):
    d.rekt(x0, y0, x1, y1, bas)
    d.ljus(ruta(x0, y0, x1, y1), mork, MORKARE)
    for y in range(y0 + 2, y1, 3):
        off = 0 if (y // 3) % 2 else 3
        for xx in range(x0 + off, x1, 6):
            d.px(xx, y, fog)


def lykta(d, x, y, sving=0, c=13, ljus=14):
    """Papperslykta som hänger i punkten (x, y)."""
    x += sving
    d.rekt(x - 1, y, x + 2, y + 1, 10)
    ell(d, x - 3, y + 1, x + 4, y + 8, c)
    d.rekt(x - 2, y + 3, x + 3, y + 4, ljus)
    d.px(x - 1, y + 2, ljus)
    d.rekt(x - 1, y + 8, x + 2, y + 9, 10)
    d.px(x, y + 9, 10)
    d.px(x, y + 10, c)


def puff(d, cx, cy, r, s=0.55):
    """Ett moln av ånga eller rök (ljusar upp det som ligger under)."""
    m = d.mask_ellips(cx - r, cy - r * 0.7, cx + r, cy + r * 0.7)
    dd = np.sqrt((XX - cx) ** 2 + ((YY - cy) * 1.4) ** 2)
    d.ljus(m, np.clip(1 - dd / (r + 0.5), 0, 1) * s + 0.08)


def hand(d, x, y, c=10):
    d.rekt(x, y, x + 3, y + 3, c)


# ======================================================================
#  ÅNGTVÄTTERIET
# ======================================================================
def tvatteri(v=None):
    v = v or {}
    anga = v.get("anga", 0)        # 0..5
    mangel = v.get("mangel", 0)    # 0..3
    rnd = random.Random(1947)
    d = Duk(2)

    # Kakelvägg, fuktig, vitkaklad upptill och mörk nertill
    d.vgrad(0, 0, W, 86, [1, 2, 3, 3])
    for y in range(4, 86, 6):
        d.rekt(0, y, W, y + 1, 2)
    for y in range(4, 86, 6):
        off = 0 if (y // 6) % 2 else 4
        for x in range(off, W, 8):
            d.rekt(x, y, x + 1, y + 6, 2)
    d.rekt(0, 60, W, 62, 6)
    d.rekt(0, 60, W, 61, 8)
    # Golv av klinkers, vått
    d.rekt(0, 86, W, H, 3)
    d.vgrad(0, 86, W, H, [1, 2, 3, 2])
    for y in range(86, H):
        for x in range(W):
            if ((x + (y - 86) * 2) // 10 + (y - 86) // 6) % 2 == 0:
                d.a[y, x] = MORKARE[int(d.a[y, x])]
    d.rekt(0, 86, W, 87, 0)
    # Rör längs taket
    d.rekt(0, 3, W, 6, 4)
    d.rekt(0, 3, W, 4, 5)
    d.rekt(0, 6, W, 7, 1)
    for x in (40, 104, 150):
        d.rekt(x, 2, x + 3, 8, 3)
    d.rekt(186, 6, 189, 60, 4)
    d.rekt(186, 6, 187, 60, 5)
    # Taklampa
    d.rekt(110, 7, 111, 14, 0)
    d.poly([(104, 14), (117, 14), (120, 19), (101, 19)], 12)
    d.rekt(106, 19, 115, 20, 11)
    d.radial(110, 36, 80, 0.55, mask=(YY > 18))

    # Skylt på väggen ovanför mangeln
    d.rekt(36, 37, 70, 45, 6)
    d.rekt(37, 38, 69, 44, 15)
    skriv(d, 40, 39, "LAUNDRY", 13)

    # Kalsonglinan tvärs över rummet
    with d.yta("kalsonglina"):
        pts = [(x, int(12 + 5 * math.sin(math.pi * (x - 40) / 150))) for x in range(40, 191)]
        for x, y in pts:
            d.px(x, y, 15)
        d.rekt(38, 9, 41, 14, 0)
        # Vita, grå, blå, en randig och en med hjärtan. Längst till vänster ett tomt mellanrum
        # med två ensamma klädnypor, där de röda hängde.
        farger = [None, 15, 5, 4, "randig", 15, "hjartan"]
        for i, lx in enumerate(range(46, 186, 20)):
            if 128 < lx < 160:
                continue
            ly = pts[lx - 40][1] + 1
            c = farger[i % len(farger)]
            if c is None:
                d.px(lx + 1, ly - 1, 8)
                d.px(lx + 9, ly - 1, 8)
                d.px(lx + 1, ly, 8)
                d.px(lx + 9, ly, 8)
                continue
            monster = c
            if c == "randig":
                c = 15
            elif c == "hjartan":
                c = 9
            # Långkalsonger: midja, två ben, knappar, fickflik
            d.rekt(lx, ly, lx + 10, ly + 6, c)
            d.rekt(lx, ly + 6, lx + 4, ly + 22, c)
            d.rekt(lx + 6, ly + 6, lx + 10, ly + 22, c)
            d.rekt(lx, ly, lx + 10, ly + 1, LJUSARE[c])
            d.rekt(lx, ly + 20, lx + 4, ly + 22, MORKARE[c])
            d.rekt(lx + 6, ly + 20, lx + 10, ly + 22, MORKARE[c])
            d.rekt(lx + 4, ly + 6, lx + 6, ly + 7, c)
            for ky in (2, 4):
                d.px(lx + 5, ly + ky, 0 if c != 0 else 15)
            if i == 3:  # en har en lucka bak
                d.rekt(lx + 2, ly + 2, lx + 5, ly + 5, MORKARE[c])
            if monster == "randig":
                for ry in range(ly + 2, ly + 22, 3):
                    for rx in range(lx, lx + 11):
                        if d.a[ry, rx] == 15:
                            d.px(rx, ry, 4)
            if monster == "hjartan":                       # hjärtan
                for hx, hy in ((lx + 2, ly + 9), (lx + 8, ly + 13), (lx + 2, ly + 17), (lx + 5, ly + 3)):
                    d.px(hx, hy, 13)
                    d.px(hx - 1, hy - 1, 13)
                    d.px(hx + 1, hy - 1, 13)
            d.px(lx + 1, ly - 1, 8)
            d.px(lx + 9, ly - 1, 8)
            d.ljus(ruta(lx + 7, ly + 1, lx + 10, ly + 22), 0.5, MORKARE)

    # Hyllorna med inslagna paket
    with d.yta("paket"):
        d.rekt(80, 34, 138, 84, 6)
        for hy in (46, 60, 74):
            d.rekt(80, hy, 138, hy + 2, 8)
            d.rekt(80, hy, 138, hy + 1, 9)
        d.rekt(80, 34, 82, 84, 7)
        d.rekt(136, 34, 138, 84, 7)
        for hy in (46, 60, 74):
            x = 84
            while x < 132:
                b = rnd.randint(7, 11)
                h = rnd.randint(7, 10)
                if x + b > 134:
                    break
                c = rnd.choice([15, 15, 9, 8, 15])
                d.rekt(x, hy - h, x + b, hy, c)
                d.rekt(x, hy - h, x + b, hy - h + 1, LJUSARE[c])
                d.rekt(x + b // 2, hy - h, x + b // 2 + 1, hy, 13 if c != 13 else 15)   # snöre
                d.rekt(x, hy - h // 2, x + b, hy - h // 2 + 1, 13 if c != 13 else 15)
                # Lapp med nummer
                d.rekt(x + 1, hy - 4, x + 4, hy - 1, 11)
                d.px(x + 2, hy - 3, 0)
                d.ljus(ruta(x + b - 2, hy - h, x + b, hy), 0.6, MORKARE)
                x += b + 2

    d.ytkarta[(YY >= 74) & (d.ytkarta == d.ytnamn.index("paket") + 1)] = 0

    # Bakdörren ut (vänster)
    with d.yta("utgang:ut"):
        d.rekt(4, 22, 26, 86, 6)
        d.rekt(6, 24, 24, 86, 7)
        d.rekt(8, 27, 22, 46, 1)
        d.rekt(8, 27, 22, 28, 3)
        d.rekt(14, 27, 15, 46, 6)
        regn_over(d, random.Random(9), 5, 0, 8, 28, 22, 46)
        for py in (52, 68):
            d.rekt(8, py, 22, py + 12, 6)
            d.rekt(8, py, 22, py + 1, 8)
        d.rekt(20, 60, 23, 62, 10)
        d.rekt(7, 16, 23, 22, 12)
        d.rekt(8, 17, 22, 21, 1)
        skriv(d, 11, 17, "UT", 10)

    # Mangeln
    with d.yta("mangel"):
        # Järnställ
        d.poly([(28, 96), (34, 52), (38, 52), (34, 96)], 0)
        d.poly([(70, 96), (66, 52), (70, 52), (76, 96)], 0)
        d.rekt(30, 92, 76, 96, 0)
        d.rekt(32, 50, 72, 54, 3)
        d.rekt(32, 50, 72, 51, 4)
        # Två valsar
        for (vy0, vy1) in [(55, 63), (64, 72)]:
            d.vgrad(34, vy0, 70, vy1, [4, 15, 5, 3, 2])
            d.rekt(33, vy0 + 1, 35, vy1 - 1, 0)
            d.rekt(69, vy0 + 1, 71, vy1 - 1, 0)
            for k in range(4):
                sx = 38 + ((k * 9 + mangel * 2) % 30)
                d.rekt(sx, vy0 + 1, sx + 1, vy1 - 1, 4)
        # Lakan som matas in och kommer ut
        d.poly([(36, 72), (68, 72), (74, 88), (40, 88)], 15)
        d.poly([(40, 86), (74, 86), (76, 90), (38, 90)], 5)
        d.ljus(d.mask_poly([(36, 72), (68, 72), (74, 88), (40, 88)]), 0.25, MORKARE)
        d.rekt(36, 46, 68, 50, 5)
        d.rekt(36, 46, 68, 47, 15)
        # Korg under
        d.rekt(42, 88, 64, 96, 8)
        for x in range(43, 64, 3):
            d.rekt(x, 89, x + 1, 96, 7)
        d.rekt(42, 88, 64, 89, 9)
        # Svänghjulet med vev
        cx, cy, r = 24, 62, 11
        ring(d, cx - r, cy - r, cx + r, cy + r, 0, 2)
        ring(d, cx - r + 1, cy - r + 1, cx + r - 1, cy + r - 1, 3, 1)
        for k in range(4):
            a = mangel * math.pi / 8 + k * math.pi / 2
            d.linje(cx, cy, int(round(cx + math.cos(a) * (r - 1))), int(round(cy + math.sin(a) * (r - 1))), 0)
        ell(d, cx - 2, cy - 2, cx + 2, cy + 2, 4)
        a = mangel * math.pi / 8
        hx, hy = int(round(cx + math.cos(a) * (r - 1))), int(round(cy + math.sin(a) * (r - 1)))
        d.rekt(hx - 1, hy - 1, hx + 2, hy + 2, 13)
        d.rekt(cx, cy - 1, 34, cy + 1, 0)

    # Tvätterskan Grubb
    with d.yta("grubb"):
        bx = 146
        # Kropp: bred, förkläde
        d.a[d.mask_ellips(bx - 18, 44, bx + 18, 100) & (YY < 75)] = 3
        d.poly([(bx - 10, 50), (bx + 10, 50), (bx + 12, 75), (bx - 12, 75)], 15)
        d.rekt(bx - 10, 50, bx + 10, 52, 5)
        d.rekt(bx - 2, 58, bx + 2, 62, 5)            # ficka
        # Armar i kors över magen, uppkavlade ärmar
        d.rekt(bx - 21, 50, bx - 13, 62, 3)
        d.rekt(bx + 13, 50, bx + 21, 62, 3)
        d.rekt(bx - 21, 59, bx - 13, 62, 4)
        d.rekt(bx + 13, 59, bx + 21, 62, 4)
        d.rekt(bx - 20, 62, bx + 12, 67, 10)       # underarm
        d.rekt(bx - 12, 67, bx + 20, 72, 9)        # underarm
        d.rekt(bx - 20, 62, bx + 12, 63, 11)
        d.rekt(bx - 12, 67, bx + 20, 68, 10)
        d.rekt(bx - 20, 66, bx + 12, 67, 8)
        for k in range(3):
            d.px(bx + 9 + k * 2, 64, 8)            # fingrar
            d.px(bx - 11 + k * 2, 69, 7)
        # Huvud
        ell(d, bx - 9, 26, bx + 9, 48, 10)
        ell(d, bx - 9, 34, bx + 9, 48, 9)
        ell(d, bx - 8, 26, bx + 8, 46, 10)
        d.rekt(bx - 6, 46, bx + 6, 50, 9)            # tjock hals/dubbelhaka
        # Hår med hårnät och papiljotter
        ell(d, bx - 10, 20, bx + 10, 34, 7)
        for (hx, hy) in [(bx - 10, 30), (bx + 8, 30), (bx - 6, 21), (bx + 4, 21)]:
            ell(d, hx - 1, hy - 1, hx + 3, hy + 3, 8)
        for x in range(bx - 9, bx + 10, 2):
            for y in range(21, 33, 2):
                if d.mask_ellips(bx - 10, 20, bx + 10, 34)[y, x]:
                    d.px(x + (y // 2) % 2, y, 6)
        # Arga ögonbryn, små ögon, sur mun, vårta
        d.linje(bx - 6, 34, bx - 2, 36, 0)
        d.linje(bx + 6, 34, bx + 2, 36, 0)
        d.px(bx - 4, 37, 0)
        d.px(bx + 4, 37, 0)
        d.rekt(bx - 1, 37, bx + 1, 42, 9)
        d.rekt(bx - 4, 44, bx + 4, 45, 6)
        d.px(bx - 5, 45, 6)
        d.px(bx + 4, 45, 6)
        d.px(bx + 6, 41, 7)
        # En hårnål i munnen
        d.rekt(bx + 2, 44, bx + 8, 45, 4)

    # Disken
    d.rekt(96, 76, 184, 102, 7)
    d.rekt(94, 74, 186, 78, 8)
    d.rekt(94, 74, 186, 75, 9)
    d.rekt(94, 78, 186, 79, 6)
    for x in range(100, 184, 14):
        d.rekt(x, 82, x + 11, 98, 6)
        d.rekt(x, 82, x + 11, 83, 8)
    # Ringklocka och en hög kalsonger på disken
    ell(d, 170, 70, 177, 75, 10)
    d.px(173, 69, 11)

    # Tvättboken (liggaren) på disken
    with d.yta("tvattbok"):
        d.poly([(102, 75), (134, 75), (132, 69), (104, 69)], 7)
        d.poly([(104, 70), (118, 70), (118, 74), (103, 74)], 15)
        d.poly([(118, 70), (132, 70), (133, 74), (118, 74)], 15)
        d.rekt(117, 69, 119, 75, 6)
        for y in (71, 72, 73):
            for x in range(105, 117, 2):
                if (x * 3 + y) % 5:
                    d.px(x, y, 3)
            for x in range(120, 131, 2):
                if (x + y * 2) % 4:
                    d.px(x, y, 3)
        d.linje(126, 68, 131, 63, 0)                 # penna i boken
        d.px(131, 63, 10)
        d.rekt(100, 75, 136, 76, 6)
        # Bläckhorn
        d.rekt(136, 70, 140, 75, 0)
        d.rekt(136, 70, 140, 71, 4)

    # Ånga som bolmar från mangeln och golvbrunnen
    d.ljus(YY < 50, 0.18)
    for i, (bx0, by0) in enumerate([(52, 46), (40, 44), (60, 42), (90, 88), (168, 30), (30, 80)]):
        t = (anga + i) % 6
        cx = bx0 + int(3 * math.sin((t + i) * 1.1))
        cy = by0 - t * 3
        puff(d, cx, cy, 5 + t // 2, 0.55 - t * 0.06)
    d.vinjett(0.45)
    return d


# ======================================================================
#  RADIOSTATIONEN WGHR
# ======================================================================
def radiohus(v=None):
    v = v or {}
    onair = v.get("onair", True)
    visare = v.get("visare", 0)    # 0..5
    rnd = random.Random(1946)
    d = Duk(6)

    # Akustikpanelade väggar: mörkt trä med perforerade plattor
    d.vgrad(0, 0, W, 90, [0, 6, 7, 6])
    for px0 in range(0, W, 24):
        d.rekt(px0 + 2, 26, px0 + 22, 86, 7)
        d.ljus(ruta(px0 + 2, 26, px0 + 22, 86), 0.35, MORKARE)
        for y in range(29, 84, 3):
            for x in range(px0 + 4, px0 + 21, 3):
                d.px(x, y, 6)
        d.rekt(px0 + 2, 26, px0 + 22, 27, 8)
    d.rekt(0, 22, W, 25, 8)
    d.rekt(0, 22, W, 23, 9)
    # Matta på golvet
    d.rekt(0, 90, W, H, 6)
    d.vgrad(0, 90, W, H, [0, 6, 6, 7])
    for y in range(92, H, 4):
        for x in range((y // 4) % 2 * 4, W, 8):
            d.px(x, y, 13)
            d.px(x + 1, y, 13 if y > 104 else 6)
    d.rekt(0, 90, W, 91, 0)
    # Taklampa
    d.radial(60, 40, 90, 0.55, mask=(YY > 0))

    # WGHR-skylten
    d.rekt(126, 3, 190, 21, 0)
    d.rekt(127, 4, 189, 20, 1)
    d.rekt(127, 4, 189, 5, 3)
    text_stor(d, 133, 7, "WGHR", 10, 2)
    text_stor(d, 132, 6, "WGHR", 11, 2)
    # Blixtar runt antennen
    d.rekt(184, 6, 185, 18, 9)
    d.px(186, 8, 10)
    d.px(183, 8, 10)

    # APPLAUSE-skylten (släckt)
    d.rekt(70, 6, 110, 16, 0)
    d.rekt(71, 7, 109, 15, 6)
    skriv(d, 73, 9, "APPLAUSE", 7)

    # ON AIR
    with d.yta("onair"):
        d.rekt(8, 3, 62, 20, 0)
        d.rekt(9, 4, 61, 19, 13 if onair else 6)
        d.rekt(9, 4, 61, 5, 14 if onair else 7)
        text_stor(d, 12, 7, "ON AIR", 11 if onair else 7, 2)
        d.rekt(20, 0, 21, 3, 0)
        d.rekt(50, 0, 51, 3, 0)
    if onair:
        d.radial(35, 12, 34, 0.4, mask=~ruta(8, 3, 62, 20) & (YY < 26))

    # Fönstret mot kontrollrummet
    wx0, wy0, wx1, wy1 = 70, 28, 164, 64
    d.rekt(wx0 - 3, wy0 - 3, wx1 + 3, wy1 + 3, 8)
    d.rekt(wx0 - 3, wy0 - 3, wx1 + 3, wy0 - 2, 9)
    d.vgrad(wx0, wy0, wx1, wy1, [2, 3, 3, 2])
    # Kontrollrummet: hyllor med bandspelare
    for x in range(wx0 + 4, wx1 - 4, 18):
        d.rekt(x, wy0 + 3, x + 14, wy0 + 15, 1)
        ell(d, x + 1, wy0 + 4, x + 6, wy0 + 9, 4)
        ell(d, x + 8, wy0 + 4, x + 13, wy0 + 9, 4)
        d.px(x + 3, wy0 + 6, 0)
        d.px(x + 10, wy0 + 6, 0)
        d.rekt(x + 2, wy0 + 11, x + 12, wy0 + 13, 2)
    with d.yta("tekniker"):
        tx = 122
        d.rekt(tx - 9, 46, tx + 9, 64, 15)           # skjorta
        d.rekt(tx - 9, 46, tx - 6, 64, 5)
        d.rekt(tx - 1, 46, tx + 1, 56, 12)           # slips
        ell(d, tx - 6, 32, tx + 6, 46, 10)          # huvud
        d.rekt(tx - 6, 32, tx + 6, 36, 7)            # hår
        d.px(tx - 3, 40, 0)
        d.px(tx + 3, 40, 0)
        d.rekt(tx - 2, 43, tx + 2, 44, 8)
        ring(d, tx - 8, 29, tx + 8, 44, 0, 1)        # hörlurar
        d.rekt(tx - 9, 37, tx - 6, 43, 0)
        d.rekt(tx + 6, 37, tx + 9, 43, 0)
        d.rekt(tx - 9, 38, tx - 7, 42, 3)
        d.rekt(tx + 7, 38, tx + 9, 42, 3)
        # Armar mot rattarna
        d.rekt(tx - 15, 52, tx - 8, 56, 15)
        d.rekt(tx + 8, 52, tx + 15, 56, 15)
        hand(d, tx - 17, 55)
        hand(d, tx + 14, 55)
    # Kontrollbordet med rattar och visarinstrument
    d.poly([(wx0, 58), (wx1, 58), (wx1, wy1), (wx0, wy1)], 3)
    d.rekt(wx0, 57, wx1, 58, 4)
    for x in range(wx0 + 3, wx1 - 2, 6):
        if 100 < x < 144:
            continue
        ell(d, x, 59, x + 3, 62, 0)
        d.px(x + 1, 59, 10)
    for i, mx in enumerate((76, 88, 148)):
        d.rekt(mx, 45, mx + 10, 54, 0)
        d.rekt(mx + 1, 46, mx + 9, 53, 10)
        d.rekt(mx + 1, 46, mx + 9, 47, 11)
        d.rekt(mx + 6, 46, mx + 9, 48, 13)
        vin = [-0.9, -0.3, 0.4, 0.9, 0.2, -0.5][(visare + i * 2) % 6]
        d.linje(mx + 5, 53, int(round(mx + 5 + 5 * math.sin(vin))), int(round(53 - 5 * math.cos(vin))), 0)
    d.rekt(110, 60, 116, 62, 13)                     # röd lampa på bordet
    # Glasreflex
    for k in (0, 2):
        d.linje(wx0 + 6 + k * 3, wy1 - 1, wx0 + 26 + k * 3, wy0, 5)
    d.ljus(ruta(wx0, wy0, wx1, wy1), 0.25, MORKARE)
    d.rekt(wx0 - 3, wy1, wx1 + 3, wy1 + 3, 8)
    d.rekt(wx0 - 3, wy1, wx1 + 3, wy1 + 1, 9)

    # Dörren ut (höger) med lampa över
    with d.yta("utgang:s"):
        d.rekt(170, 30, 190, 90, 6)
        d.rekt(172, 32, 188, 90, 8)
        d.rekt(174, 36, 186, 56, 7)
        d.rekt(174, 60, 186, 86, 7)
        d.rekt(174, 36, 186, 37, 9)
        d.rekt(174, 60, 186, 61, 9)
        ell(d, 177, 40, 184, 47, 0)
        ell(d, 178, 41, 183, 46, 3)
        d.rekt(173, 64, 176, 66, 10)
        ell(d, 176, 24, 184, 30, 10)
        d.rekt(175, 28, 185, 30, 0)

    # Rex, programledaren
    with d.yta("rex"):
        rx = 50
        # Kostym
        d.a[d.mask_ellips(rx - 16, 50, rx + 16, 100) & (YY < 80)] = 1
        d.poly([(rx - 6, 52), (rx + 6, 52), (rx, 66)], 15)  # skjortbröst
        d.poly([(rx - 6, 52), (rx - 2, 52), (rx - 1, 64), (rx - 8, 56)], 2)  # slag
        d.poly([(rx + 6, 52), (rx + 2, 52), (rx + 1, 64), (rx + 8, 56)], 2)
        d.rekt(rx - 4, 52, rx + 5, 55, 13)           # fluga
        d.rekt(rx - 1, 52, rx + 2, 55, 14)
        d.px(rx - 5, 52, 13)
        d.px(rx + 5, 54, 13)
        d.px(rx - 7, 58, 14)                         # nejlika
        d.px(rx - 8, 58, 13)
        # Armar på bordet
        d.rekt(rx + 12, 62, rx + 20, 70, 1)
        d.poly([(rx + 16, 68), (rx + 26, 72), (rx + 26, 77), (rx + 14, 74)], 1)
        hand(d, rx + 25, 71)
        d.rekt(rx - 22, 66, rx - 12, 78, 1)
        hand(d, rx - 22, 75)
        d.rekt(rx - 22, 74, rx - 18, 75, 15)
        # Huvud: brett leende, fyrkantig haka
        d.rekt(rx - 3, 48, rx + 4, 53, 9)
        ell(d, rx - 8, 28, rx + 9, 50, 10)
        d.rekt(rx - 7, 42, rx + 8, 49, 10)
        d.rekt(rx - 6, 49, rx + 7, 50, 9)
        # Blankt, slickat hår med bena
        ell(d, rx - 9, 23, rx + 10, 36, 0)
        d.rekt(rx - 9, 30, rx - 7, 39, 0)
        d.rekt(rx + 8, 30, rx + 10, 39, 0)
        d.linje(rx - 6, 27, rx + 7, 26, 3)
        d.linje(rx - 6, 29, rx + 2, 28, 2)
        d.linje(rx - 2, 25, rx + 6, 24, 4)
        d.px(rx + 1, 24, 11)
        d.px(rx + 2, 24, 5)
        d.rekt(rx - 3, 24, rx - 2, 34, 1)            # benan
        # Ansikte
        d.rekt(rx - 5, 36, rx - 1, 37, 0)            # ögonbryn
        d.rekt(rx + 3, 36, rx + 7, 37, 0)
        d.px(rx - 3, 39, 0)
        d.px(rx + 5, 39, 0)
        d.rekt(rx + 1, 39, rx + 3, 43, 9)            # näsa
        d.linje(rx - 4, 45, rx + 7, 45, 6)           # leende
        d.rekt(rx - 3, 46, rx + 7, 47, 15)
        d.px(rx - 5, 44, 6)
        d.px(rx + 8, 44, 6)
        d.rekt(rx - 3, 47, rx + 7, 48, 6)
        # Hörlurar
        ring(d, rx - 11, 21, rx + 12, 46, 3, 1)
        d.rekt(rx - 12, 34, rx - 8, 43, 0)
        d.rekt(rx + 9, 34, rx + 13, 43, 0)
        d.rekt(rx - 12, 35, rx - 10, 42, 4)
        d.rekt(rx + 11, 35, rx + 13, 42, 4)
        d.linje(rx - 11, 43, rx - 15, 66, 0)
        # Ett glitter på tänderna
        d.px(rx + 4, 46, 11)

    # Programledarens bord (stort, rundat)
    d.poly([(4, 80), (112, 80), (118, 100), (0, 100)], 7)
    d.rekt(2, 78, 114, 82, 8)
    d.rekt(2, 78, 114, 79, 9)
    d.ljus(d.mask_poly([(4, 82), (112, 82), (118, 100), (0, 100)]), 0.4, MORKARE)
    for x in range(10, 110, 16):
        d.rekt(x, 86, x + 1, 100, 6)

    # Manus och ett glas vatten på bordet
    d.poly([(10, 78), (28, 78), (26, 74), (12, 74)], 15)
    d.rekt(14, 75, 25, 76, 4)
    d.rekt(13, 76, 22, 77, 4)
    d.rekt(96, 70, 101, 78, 5)
    d.rekt(97, 72, 100, 77, 4)
    d.px(97, 71, 15)

    # Den stora mikrofonen på bordsstativ
    with d.yta("studiomikrofon"):
        mx = 80
        d.rekt(mx - 6, 76, mx + 7, 79, 0)
        d.rekt(mx - 6, 76, mx + 7, 77, 4)
        d.rekt(mx, 54, mx + 2, 77, 0)
        d.linje(mx + 1, 60, mx - 6, 56, 0)
        ring(d, mx - 7, 33, mx + 9, 56, 4, 2)        # upphängningsring
        ell(d, mx - 4, 36, mx + 6, 54, 3)
        ell(d, mx - 3, 37, mx + 5, 53, 5)
        for y in range(38, 53, 2):
            d.rekt(mx - 3, y, mx + 6, y + 1, 4)
        d.rekt(mx - 1, 38, mx + 1, 41, 15)
        d.rekt(mx - 6, 44, mx - 4, 46, 0)
        d.rekt(mx + 6, 44, mx + 8, 46, 0)
        d.rekt(mx - 5, 52, mx + 7, 54, 13)

    d.vinjett(0.45)
    return d


# ======================================================================
#  BAKGATAN I CHINATOWN
# ======================================================================
def bakgata(v=None):
    v = v or {}
    regn = v.get("regn", 0)     # 0..9
    sving = v.get("sving", 0)   # 0..3
    fladder = v.get("fladder", 0)  # 0..3
    rnd = random.Random(1938)
    d = Duk(1)

    # Smal himmelsremsa, mörkblå
    d.vgrad(0, 0, W, 40, [0, 0, 1, 2])
    for _ in range(6):
        d.px(rnd.randint(70, 120), rnd.randint(0, 12), 4)

    # Gränden fortsätter långt bort (mitten)
    d.vgrad(72, 10, 124, 86, [1, 2, 2, 3])
    for i in range(4):
        x0, x1, top = 74 + i * 5, 122 - i * 5, 14 + i * 9
        d.rekt(x0, top, x0 + 6, 86, [1, 1, 2, 2][i])
        d.rekt(x1 - 6, top, x1, 86, [1, 1, 2, 2][i])
        for wy in range(top + 3, 80, 5):
            if rnd.random() < 0.45:
                d.px(x0 + 2 + rnd.randint(0, 2), wy, rnd.choice([10, 13, 9]))
            if rnd.random() < 0.45:
                d.px(x1 - 3 - rnd.randint(0, 2), wy, rnd.choice([10, 13, 9]))
    d.rekt(92, 52, 104, 86, 1)                       # gränden svänger bort
    d.radial(98, 70, 14, 0.4)
    # Ett tänt fönster längst bort
    d.rekt(95, 62, 99, 67, 10)
    d.rekt(95, 62, 99, 63, 11)

    # Vänster hus (örtapoteket), tegel
    tegel(d, 0, 0, 72, 96, 7, 0.5)
    d.poly([(72, 0), (80, 0), (80, 96), (72, 96)], 6)  # husets sida i perspektiv
    for fy in (4, 22):
        for fx in (8, 30, 52):
            d.rekt(fx - 1, fy - 1, fx + 12, fy + 13, 6)
            lit = (fy, fx) in [(4, 30), (22, 8)]
            d.rekt(fx, fy, fx + 11, fy + 12, 10 if lit else 1)
            if lit:
                d.rekt(fx, fy, fx + 11, fy + 2, 11)
                d.rekt(fx, fy + 2, fx + 2, fy + 12, 13)
                d.rekt(fx + 9, fy + 2, fx + 11, fy + 12, 13)
            else:
                d.px(fx + 1, fy + 1, 3)
            d.rekt(fx - 1, fy + 12, fx + 12, fy + 13, 4)
    # Brandtrappa
    d.rekt(0, 38, 66, 39, 0)
    for x in range(0, 66, 3):
        d.rekt(x, 33, x + 1, 38, 0)
    d.rekt(0, 33, 66, 34, 0)

    # Höger hus, mörkt putsat, med den röda dörren
    d.rekt(122, 0, W, 96, 2)
    d.ljus(ruta(122, 0, W, 96), 0.4, MORKARE)
    for y in range(3, 96, 7):
        d.rekt(122, y, W, y + 1, 1)
    d.poly([(116, 0), (122, 0), (122, 96), (116, 96)], 1)
    for fy in (6,):
        for fx in (132, 160):
            d.rekt(fx - 1, fy - 1, fx + 14, fy + 15, 0)
            d.rekt(fx, fy, fx + 13, fy + 14, 1)
            d.rekt(fx + 6, fy, fx + 7, fy + 14, 0)
            d.rekt(fx, fy + 7, fx + 13, fy + 8, 0)
    # Galler för fönstret
    for x in range(160, 174, 3):
        d.rekt(x, 5, x + 1, 21, 4)

    # Gatan: våta stenar i perspektiv
    d.poly([(80, 86), (116, 86), (W, 112), (W, H), (0, H), (0, 112)], 2)
    d.vgrad(0, 86, W, H, [1, 2, 3, 2])
    d.rekt(0, 96, 80, 112, 3)
    for y in range(88, H, 3):
        off = (y // 3) % 2 * 4
        for x in range(off, W, 8):
            d.px(x, y, 1)
    d.ljus(YY >= 86, 0.15)
    # Rännsten i mitten
    d.linje(98, 86, 96, H, 1)
    d.linje(99, 86, 97, H, 3)

    # Torklinorna mellan husen
    with d.yta("torklina"):
        for (y0, y1, x0, x1, n) in [(28, 34, 80, 118, 3), (42, 46, 72, 122, 4)]:
            pts = []
            for x in range(x0, x1 + 1):
                t = (x - x0) / (x1 - x0)
                pts.append((x, int(y0 + (y1 - y0) * t + 3 * math.sin(math.pi * t))))
            for x, y in pts:
                d.px(x, y, 15 if y0 > 30 else 4)
            farger = [15, 13, 4, 12, 9, 5]
            for k in range(n):
                lx = x0 + 4 + k * (x1 - x0 - 6) // n
                ly = pts[lx - x0][1] + 1
                c = farger[(k + y0) % len(farger)]
                b = 5 + (k % 2) * 2
                h = 7 + (k % 3)
                f = (fladder + k) % 4
                sk = [0, 1, 2, 1][f]
                d.poly([(lx, ly), (lx + b, ly), (lx + b + sk, ly + h), (lx + sk, ly + h)], c)
                d.rekt(lx, ly, lx + b, ly + 1, LJUSARE[c])
                if k % 2 == 0:  # en skjorta med ärmar
                    d.poly([(lx - 2, ly), (lx, ly), (lx + sk // 2, ly + 3), (lx - 2 + sk // 2, ly + 3)], c)
                    d.poly([(lx + b, ly), (lx + b + 2, ly), (lx + b + 2 + sk // 2, ly + 3), (lx + b + sk // 2, ly + 3)], c)
                d.px(lx + 1, ly - 1, 8)
                d.px(lx + b - 1, ly - 1, 8)
                d.ljus(d.mask_poly([(lx, ly + h // 2), (lx + b, ly + h // 2), (lx + b + sk, ly + h), (lx + sk, ly + h)]), 0.4, MORKARE)

    # Örtapoteket: skyltfönster med burkar och skylt
    d.rekt(6, 52, 70, 96, 6)
    d.rekt(4, 50, 72, 52, 12)
    # Lodrät skylt med tecken
    d.rekt(2, 40, 10, 74, 12)
    d.rekt(3, 41, 9, 73, 6)
    for yy in range(44, 70, 7):
        d.rekt(4, yy, 8, yy + 1, 10)
        d.rekt(5, yy + 1, 7, yy + 4, 10)
        d.px(4, yy + 3, 10)
        d.px(8, yy + 4, 10)
    # Skylt HERBS ovanför
    d.rekt(14, 42, 46, 50, 13)
    d.rekt(15, 43, 45, 49, 6)
    skriv(d, 21, 44, "HERBS", 10)
    d.rekt(12, 42, 14, 50, 10)
    d.rekt(46, 42, 48, 50, 10)
    # Fönstret
    d.rekt(12, 56, 46, 88, 0)
    d.vgrad(13, 57, 45, 87, [9, 10, 9, 8])
    for hy in (66, 76, 86):
        d.rekt(13, hy, 45, hy + 1, 7)
        for k, bx in enumerate(range(14, 44, 6)):
            c = [12, 15, 13, 8, 4][(k + hy) % 5]
            d.rekt(bx, hy - 7, bx + 4, hy, c)
            d.rekt(bx, hy - 8, bx + 4, hy - 7, 6)
            d.rekt(bx + 1, hy - 5, bx + 3, hy - 3, 15)
            d.px(bx, hy - 6, LJUSARE[c])
    d.rekt(28, 57, 29, 87, 7)
    d.radial(29, 72, 30, 0.45, mask=~ruta(12, 56, 46, 88) & (YY < 112))
    # Ljuskast på gatan framför fönstret
    for y in range(98, 112, 2):
        d.ljus(ruta(10 + (y - 98), y, 50 + (y - 98), y + 1) & ((XX + y) % 2 == 0), 0.9)
    # Apotekets dörr (utgång in)
    with d.yta("utgang:in"):
        d.rekt(50, 54, 68, 96, 6)
        d.rekt(52, 56, 66, 96, 12)
        d.rekt(54, 58, 64, 74, 10)
        d.vgrad(54, 58, 64, 74, [11, 10, 9])
        d.rekt(58, 58, 60, 74, 12)
        d.rekt(54, 78, 64, 92, 6)
        d.rekt(54, 78, 64, 79, 12)
        d.rekt(62, 82, 64, 84, 10)
        # Liten skylt OPEN i fönstret
        d.rekt(54, 66, 64, 72, 15)
        d.rekt(55, 68, 63, 69, 13)
        d.rekt(55, 70, 61, 71, 13)
        d.rekt(48, 96, 70, 98, 4)
        d.rekt(48, 96, 70, 97, 5)
    d.markera("utgang:in", 50, 54, 68, 98)

    # Den röda dörren med lucka
    with d.yta("utgang:ö"):
        d.rekt(136, 48, 162, 96, 0)
        d.rekt(138, 50, 160, 96, 13)
        d.a[d.mask_ellips(136, 40, 162, 60)] = 0
        d.a[d.mask_ellips(138, 42, 160, 58)] = 13
        d.rekt(138, 50, 160, 96, 13)
        d.rekt(149, 44, 150, 96, 6)
        for (ry, rh) in [(60, 14), (78, 14)]:
            for (rx0, rx1) in [(141, 147), (152, 158)]:
                d.rekt(rx0, ry, rx1, ry + rh, 6)
                d.rekt(rx0, ry, rx1, ry + 1, 14)
        for (nx, ny) in [(140, 52), (158, 52), (140, 94), (158, 94)]:
            d.px(nx, ny, 10)
        d.rekt(146, 84, 148, 86, 10)
        d.rekt(151, 84, 153, 86, 10)
        # Tröskel
        d.rekt(134, 96, 164, 99, 4)
        d.rekt(134, 96, 164, 97, 5)
        # Ett par gula drakögon målade ovanför
        d.rekt(134, 36, 164, 40, 12)
        d.rekt(135, 37, 163, 39, 6)
        for x in range(137, 162, 4):
            d.px(x, 38, 10)
    d.markera("utgang:ö", 136, 42, 162, 99)

    # Luckan i dörren och gonggongen bredvid (titthal)
    with d.yta("titthal"):
        d.rekt(143, 52, 157, 58, 0)
        d.rekt(144, 53, 156, 57, 6)
        d.rekt(144, 53, 156, 54, 8)
        d.rekt(147, 55, 153, 56, 0)                  # springan
        d.px(149, 55, 10)                            # ett öga som glimmar?
        # Mässingsgonggong på en krok
        d.rekt(166, 52, 178, 54, 7)
        d.rekt(166, 52, 167, 56, 7)
        d.rekt(177, 52, 178, 56, 7)
        ell(d, 165, 56, 179, 70, 9)
        ell(d, 166, 57, 178, 69, 10)
        ell(d, 169, 60, 175, 66, 9)
        d.px(168, 59, 11)
        d.px(169, 58, 11)
        d.rekt(171, 62, 173, 64, 8)
        # Klubba som hänger bredvid
        d.rekt(181, 56, 182, 70, 8)
        ell(d, 179, 69, 184, 74, 13)
        d.radial(172, 63, 10, 0.3, mask=ruta(164, 50, 186, 76) & (d.a < 9))

    # Papperslyktor över gränden
    pts = [(x, int(16 + 10 * (1 - ((x - 96) / 96) ** 2))) for x in range(W)]
    for x, y in pts:
        d.px(x, y, 0)
    gung = [0, 1, 0, -1][sving]
    for lx in (20, 54, 88, 122, 156, 184):
        ly = pts[lx][1]
        lykta(d, lx, ly + 1, gung)
        d.radial(lx + gung, ly + 6, 10, 0.5, mask=(d.a < 5))
    lykta(d, 132, 44, [0, -1, 0, 1][sving])
    lykta(d, 166, 44, [0, 1, 0, -1][sving])
    d.radial(149, 60, 30, 0.35, mask=(d.a < 5))

    # Soptunnan med katten
    d.rekt(104, 84, 124, 102, 3)
    d.rekt(104, 84, 106, 102, 4)
    d.rekt(122, 84, 124, 102, 2)
    for y in (88, 95):
        d.rekt(104, y, 124, y + 1, 2)
    d.poly([(102, 82), (126, 82), (124, 85), (104, 85)], 4)
    d.rekt(108, 80, 120, 82, 5)
    # Fiskben som sticker ut
    d.linje(119, 83, 123, 77, 15)
    for k in range(3):
        d.px(120 + k, 80 - k, 15)
        d.px(122 + k, 81 - k, 15)
    # Katten
    sprite(d, 107, 71, [
        "k...k.....",
        "kk.kk.....",
        "kkkkk.....",
        "kckck.....",
        "kkpkk...k.",
        ".kkk....k.",
        "kkkkkkkkk.",
        "kkkkkkkk..",
        "kkkkkkkk..",
        "k.k..k.k..",
    ])
    d.rekt(107, 82, 116, 83, 0)

    # Utgång söderut: huvudgatan i nederkanten
    with d.yta("utgang:s"):
        d.poly([(64, 120), (132, 120), (126, 108), (70, 108)], 3)
        d.ljus(d.mask_poly([(64, 120), (132, 120), (126, 108), (70, 108)]), 0.6)
        # Skylt på stolpe med pil nedåt
        d.rekt(97, 112, 99, 120, 0)
        d.rekt(76, 102, 124, 112, 15)
        d.rekt(77, 103, 123, 111, 12)
        skriv(d, 74, 105, "CHINATOWN", 15)
        d.rekt(117, 104, 119, 107, 15)
        d.rekt(115, 107, 121, 108, 15)
        d.rekt(116, 108, 120, 109, 15)
        d.px(118, 109, 15)

    # Vattenpölar som speglar lyktorna och den röda dörren
    for (px0, py0, px1, py1, rc) in [(132, 104, 168, 110, 13), (10, 112, 44, 118, 10), (150, 114, 186, 119, 13)]:
        m = d.mask_ellips(px0, py0, px1, py1)
        d.a[m] = 1
        d.a[m & (YY == py0 + 1)] = 3
        d.a[m & (np.abs(XX - (px0 + px1) // 2) < 4) & (YY % 2 == 0)] = MORKARE[rc] if rc != 10 else 9
        d.a[m & (np.abs(XX - (px0 + px1) // 2) < 2) & (YY % 2 == 0)] = rc

    # Blanka reflexer på gatan
    for (x0, x1, f) in [(14, 46, 0.5), (138, 160, 0.4), (20, 26, 0.4), (152, 160, 0.3)]:
        for y in range(100, H):
            s = f * (1 - (y - 100) / (H - 100))
            d.ljus(ruta(x0, y, x1, y + 1) & ((XX + y) % 2 == 0) & (d.a < 5), s * 2)

    regn_over(d, random.Random(17), 70, regn)
    d.vinjett(0.45)
    return d


# ======================================================================
#  ÖRTAPOTEKET
# ======================================================================
def apotek(v=None):
    v = v or {}
    rok = v.get("rok", 0)    # 0..5
    vag = v.get("vag", 0)    # 0..3
    rnd = random.Random(1912)
    d = Duk(6)

    d.vgrad(0, 0, W, 90, [0, 6, 6, 7])
    # Golv
    d.rekt(0, 90, W, H, 7)
    d.vgrad(0, 90, W, H, [6, 7, 6])
    for i in range(-10, 12):
        d.linje(96 + i * 8, 90, 96 + i * 22, H, 6)
    d.rekt(0, 90, W, 91, 0)

    # Väggarna med hundratals små lådor och burkar
    with d.yta("burkar"):
        for (x0, x1) in [(30, 192)]:
            d.rekt(x0, 14, x1, 90, 6)
            for y in range(16, 88, 7):
                for x in range(x0 + 2, x1 - 2, 8):
                    if 60 <= x <= 128 and y < 42:
                        continue
                    d.rekt(x, y, x + 7, y + 6, 8)
                    d.rekt(x, y, x + 7, y + 1, 9)
                    d.px(x + 3, y + 3, 10)
                    if rnd.random() < 0.6:
                        d.rekt(x + 1, y + 1, x + 6, y + 2, 15)   # pappersetikett
                        d.px(x + 2 + rnd.randint(0, 2), y + 1, 0)
                    if rnd.random() < 0.06:  # en låda står ute
                        d.rekt(x, y + 1, x + 7, y + 6, 0)
                        d.rekt(x + 1, y + 5, x + 6, y + 7, 9)
        # Hylla med porslinsburkar i mitten upptill
        d.rekt(60, 14, 130, 42, 6)
        for hy in (27, 41):
            d.rekt(60, hy, 130, hy + 2, 9)
            d.rekt(60, hy, 130, hy + 1, 10)
            for k, bx in enumerate(range(63, 128, 9)):
                c = [15, 12, 13, 4, 15, 10, 12, 15][(k + hy) % 8]
                ell(d, bx, hy - 10, bx + 7, hy, c)
                d.rekt(bx + 1, hy - 7, bx + 7, hy, c)
                d.rekt(bx + 2, hy - 12, bx + 6, hy - 9, MORKARE[c] if c != 15 else 3)
                d.rekt(bx + 2, hy - 5, bx + 6, hy - 3, 3 if c == 15 else 15)
                d.px(bx + 1, hy - 7, LJUSARE[c])
        d.ljus(ruta(30, 14, W, 90), np.clip((XX - 30) / 260.0, 0, 0.4) + 0.05 * (YY < 30), MORKARE)
    # Det som döljs bakom disken räknas inte till lådväggen
    d.ytkarta[(YY >= 77) & (XX >= 34) & (XX < 172) & (d.ytkarta == d.ytnamn.index("burkar") + 1)] = 0

    # Dörren ut (vänster)
    with d.yta("utgang:ut"):
        d.rekt(4, 24, 26, 90, 0)
        d.rekt(6, 26, 24, 90, 13)
        d.rekt(8, 28, 22, 54, 2)
        d.vgrad(8, 28, 22, 54, [1, 2, 3])
        regn_over(d, random.Random(3), 6, 0, 8, 28, 22, 54)
        d.rekt(14, 28, 16, 54, 13)
        d.rekt(8, 60, 22, 86, 6)
        d.rekt(8, 60, 22, 61, 14)
        d.rekt(20, 64, 23, 66, 10)
        # Klocka på dörren
        d.rekt(14, 20, 16, 24, 0)
        ell(d, 12, 22, 18, 27, 10)

    # Torkade sjöhästar och rötter från taket
    with d.yta("torkade"):
        d.rekt(0, 0, W, 3, 0)
        d.rekt(0, 3, W, 4, 7)
        for k, x in enumerate(range(34, 190, 11)):
            lang = 4 + (k * 7) % 9
            d.rekt(x, 4, x + 1, 4 + lang, 0)
            y = 4 + lang
            typ = k % 3
            if typ == 0:   # sjöhäst
                sprite(d, x - 2, y, [".dd.", "ddf.", ".dd.", "..d.", ".dd.", ".d..", "..d.", ".d.."],
                       {"d": 9, "f": 0})
            elif typ == 1:  # rot
                d.rekt(x - 1, y, x + 2, y + 5, 8)
                d.linje(x, y + 5, x - 3, y + 11, 8)
                d.linje(x + 1, y + 5, x + 3, y + 10, 7)
                d.linje(x, y + 6, x, y + 12, 9)
                d.px(x - 2, y + 2, 9)
            else:          # knippe örter
                d.poly([(x - 3, y + 9), (x + 4, y + 9), (x + 1, y), (x, y)], 12)
                d.rekt(x - 1, y, x + 2, y + 2, 13)
                for t in range(3):
                    d.px(x - 2 + t * 2, y + 8, 9)
        # En torkad ödla på väggen som skämt
        sprite(d, 176, 30, ["..d..", "ddddd", "..d..", ".ddd.", "d.d.d", "..d..", "..d.."], {"d": 9})

    # Lampa: rund papperslykta
    d.radial(100, 40, 80, 0.6, mask=(YY > 4))

    # Apotekaren
    with d.yta("apotekare"):
        ax = 98
        # Mörkblå sidenrock
        d.a[d.mask_ellips(ax - 16, 48, ax + 16, 100) & (YY < 77)] = 2
        d.poly([(ax - 4, 50), (ax + 4, 50), (ax + 8, 76), (ax - 8, 76)], 3)
        for y in range(54, 74, 5):
            d.rekt(ax + 2, y, ax + 6, y + 1, 10)    # knutknappar
        d.rekt(ax - 16, 66, ax + 16, 67, 10)
        # Händer i vida ärmar
        d.rekt(ax - 22, 62, ax - 12, 74, 2)
        d.rekt(ax + 12, 62, ax + 22, 74, 2)
        d.rekt(ax - 22, 70, ax - 12, 72, 4)
        hand(d, ax - 20, 72)
        hand(d, ax + 15, 72)
        # Huvud
        ell(d, ax - 8, 28, ax + 8, 48, 10)
        ell(d, ax - 7, 26, ax + 7, 40, 10)
        d.rekt(ax - 8, 24, ax + 8, 30, 0)            # kalott
        ell(d, ax - 8, 21, ax + 8, 30, 0)
        d.px(ax, 21, 13)
        d.rekt(ax - 8, 28, ax + 8, 29, 13)
        # Långt vitt skägg och mustasch
        d.poly([(ax - 7, 40), (ax + 7, 40), (ax + 4, 58), (ax + 1, 66), (ax - 2, 60), (ax - 5, 54)], 15)
        d.linje(ax - 2, 41, ax - 9, 50, 15)
        d.linje(ax + 2, 41, ax + 9, 50, 15)
        d.linje(ax - 1, 44, ax, 64, 5)
        d.px(ax - 9, 51, 15)
        d.px(ax + 9, 51, 15)
        d.rekt(ax - 3, 44, ax + 3, 45, 7)            # mun i skägget
        # Vita ögonbryn, runda glasögon
        d.rekt(ax - 7, 32, ax - 2, 33, 15)
        d.rekt(ax + 2, 32, ax + 7, 33, 15)
        ring(d, ax - 7, 33, ax - 1, 39, 0)
        ring(d, ax + 1, 33, ax + 7, 39, 0)
        d.px(ax - 4, 36, 0)
        d.px(ax + 4, 36, 0)
        d.px(ax - 5, 35, 11)
        d.px(ax + 3, 35, 11)
        d.rekt(ax - 1, 35, ax + 1, 36, 0)
        d.rekt(ax - 1, 37, ax + 1, 41, 9)

    # Disken
    d.rekt(36, 78, 170, 104, 7)
    d.rekt(34, 76, 172, 80, 8)
    d.rekt(34, 76, 172, 77, 9)
    d.rekt(34, 80, 172, 81, 6)
    for x in range(40, 168, 12):
        d.rekt(x, 84, x + 10, 100, 6)
        d.rekt(x, 84, x + 10, 85, 8)
        d.px(x + 5, 92, 10)
    # Mortel och ett abakus på disken
    ell(d, 64, 70, 76, 78, 4)
    ell(d, 65, 70, 75, 74, 1)
    d.linje(72, 72, 78, 64, 15)
    d.rekt(140, 70, 166, 77, 8)
    d.rekt(141, 71, 165, 76, 6)
    for r in (72, 74):
        d.rekt(141, r, 165, r + 1, 9)
        for x in range(143, 164, 3):
            d.px(x, r, 13)

    # Rökelse i en skål (vänster på disken)
    ell(d, 44, 72, 56, 78, 10)
    ell(d, 45, 72, 55, 75, 6)
    d.rekt(47, 62, 48, 74, 13)
    d.rekt(51, 64, 52, 74, 13)
    d.px(47, 62, 11)
    d.px(51, 64, 11)
    for spar, sx0 in enumerate((47, 51)):
        sx = sx0
        for y in range(61 - spar * 2, 26, -1):
            sx += [0, 1, 1, 0, -1, -1][((y + rok * 2 + spar * 3) // 3) % 6]
            if (y + rok + spar) % 4:
                d.px(sx, y, 15 if y > 46 else 4)

    # Balansvågen i mässing
    with d.yta("vag2"):
        vx = 134
        d.rekt(vx - 7, 75, vx + 8, 77, 9)
        d.rekt(vx - 5, 73, vx + 6, 75, 10)
        d.rekt(vx, 52, vx + 2, 74, 9)
        d.rekt(vx, 52, vx + 1, 74, 10)
        ell(d, vx - 1, 49, vx + 3, 53, 10)
        lut = [0, 1, 0, -1][vag]
        d.linje(vx - 12, 54 + lut * 2, vx + 13, 54 - lut * 2, 10)
        d.linje(vx - 12, 55 + lut * 2, vx + 13, 55 - lut * 2, 9)
        for s in (-1, 1):
            ex = vx + 1 + s * 12
            ey = 55 - s * lut * 2
            d.linje(ex, ey, ex - 5, ey + 10, 8)
            d.linje(ex, ey, ex + 5, ey + 10, 8)
            ell(d, ex - 6, ey + 9, ex + 6, ey + 13, 9)
            d.rekt(ex - 5, ey + 9, ex + 6, ey + 10, 10)
        # Lite pulver i ena skålen
        ell(d, vx - 14, 61 + lut * 2, vx - 8, 64 + lut * 2, 15)
        d.px(vx + 1, 50, 11)

    # Damm och rökdis
    for (sx, sy) in [(60, 30), (140, 22), (120, 40), (80, 18)]:
        d.px(sx, sy, 15)
    d.vinjett(0.5)
    return d


# ======================================================================
#  SPELHÅLAN
# ======================================================================
def spelhala(v=None):
    v = v or {}
    sedel = v.get("sedel", True)
    rok = v.get("rok", 0)      # 0..5
    hjul = v.get("hjul", 0)    # 0..3
    rnd = random.Random(1929)
    d = Duk(0)

    # Mörka väggar med sliten tapet
    d.vgrad(0, 0, W, 86, [0, 0, 1, 6])
    for x in range(3, W, 10):
        for y in range(6, 84, 4):
            if (x // 10 + y // 4) % 2:
                d.px(x, y, 6 if y > 40 else 1)
    d.rekt(0, 84, W, 86, 6)
    # Golv
    d.rekt(0, 86, W, H, 6)
    d.vgrad(0, 86, W, H, [0, 6, 6])
    for y in range(88, H, 5):
        d.rekt(0, y, W, y + 1, 0)
    # Väggdetaljer: ett gammalt reklamplakat och en klocka
    d.rekt(118, 16, 142, 39, 15)
    d.rekt(119, 17, 141, 38, 13)
    ell(d, 124, 19, 136, 30, 10)
    skriv(d, 120, 32, "LUCKY", 11)
    d.ljus(ruta(118, 16, 142, 39), 0.35, MORKARE)
    d.rekt(46, 14, 64, 34, 6)                        # dragonbild
    d.rekt(47, 15, 63, 33, 12)
    d.linje(49, 30, 61, 18, 10)
    d.linje(49, 31, 61, 19, 13)
    d.ljus(ruta(46, 14, 64, 34), 0.5, MORKARE)

    # Dörren ut (vänster) med ett titthål och en bom
    with d.yta("utgang:ut"):
        d.rekt(2, 28, 24, 88, 0)
        d.rekt(4, 30, 22, 88, 8)
        d.rekt(6, 32, 20, 56, 7)
        d.rekt(6, 60, 20, 85, 7)
        d.rekt(6, 32, 20, 33, 9)
        d.rekt(6, 60, 20, 61, 9)
        d.rekt(10, 38, 16, 42, 0)
        d.rekt(11, 39, 15, 41, 10)
        d.rekt(18, 62, 21, 65, 10)
        d.rekt(3, 50, 23, 53, 3)                     # bom
        d.rekt(3, 50, 23, 51, 4)
        d.rekt(2, 20, 24, 27, 0)
        d.rekt(3, 21, 23, 26, 12)
        skriv(d, 10, 21, "UT", 11)
        ell(d, 10, 14, 16, 19, 10)                   # glödlampa
        d.px(12, 15, 11)
        d.radial(13, 30, 26, 0.5, mask=(YY > 13))

    # Gröna lampor över borden
    for (lx, r) in [(52, 44), (146, 50)]:
        d.rekt(lx, 0, lx + 1, 12, 0)
        d.poly([(lx - 10, 18), (lx + 11, 18), (lx + 5, 11), (lx - 4, 11)], 12)
        d.rekt(lx - 10, 17, lx + 11, 18, 3)
        d.rekt(lx - 7, 18, lx + 8, 19, 11)
        cone = d.mask_poly([(lx - 9, 19), (lx + 10, 19), (lx + r, 100), (lx - r, 100)])
        d.radial(lx, 60, 60, 0.6, mask=cone)

    # Mahjongbordet med spelare
    with d.yta("mahjong"):
        # Spelaren bakom bordet (läser sina brickor)
        sx = 52
        d.rekt(sx - 9, 46, sx + 9, 66, 3)
        ell(d, sx - 6, 32, sx + 6, 46, 10)
        d.rekt(sx - 7, 30, sx + 7, 34, 0)            # keps
        d.rekt(sx - 9, 33, sx + 2, 35, 0)
        d.rekt(sx - 3, 39, sx - 1, 40, 0)
        d.rekt(sx + 2, 39, sx + 4, 40, 0)
        d.linje(sx + 4, 44, sx + 11, 42, 15)         # cigarett
        d.px(sx + 11, 42, 13)
        # Den tomma stolen till vänster
        d.rekt(26, 50, 30, 80, 7)
        d.rekt(26, 50, 30, 51, 8)
        d.rekt(26, 64, 36, 67, 7)
        # Spelaren till höger (rund, väst)
        rx = 82
        ell(d, rx - 9, 52, rx + 9, 86, 15)
        d.poly([(rx - 8, 58), (rx + 8, 58), (rx + 8, 80), (rx - 8, 80)], 13)
        d.rekt(rx - 1, 58, rx + 1, 80, 15)
        ell(d, rx - 6, 40, rx + 6, 54, 10)
        d.rekt(rx - 7, 39, rx + 7, 42, 7)            # pläd-hatt
        d.rekt(rx - 5, 34, rx + 5, 40, 7)
        d.rekt(rx - 5, 37, rx + 5, 38, 0)
        d.px(rx - 4, 46, 0)
        d.px(rx - 1, 46, 0)
        d.rekt(rx - 5, 50, rx - 1, 51, 6)
        d.rekt(rx - 14, 62, rx - 6, 66, 15)
        hand(d, rx - 16, 63)
        # Bordet
        d.poly([(14, 66), (90, 66), (96, 80), (8, 80)], 12)
        d.rekt(8, 80, 96, 83, 7)
        d.rekt(8, 80, 96, 81, 8)
        for bx in (14, 88):
            d.rekt(bx, 83, bx + 3, 100, 6)
        # Brickmurar
        for (y, x0, x1) in [(68, 24, 80), (77, 20, 84)]:
            for x in range(x0, x1, 4):
                d.rekt(x, y, x + 3, y + 2, 15)
                d.rekt(x, y + 2, x + 3, y + 3, 12 if y < 70 else 9)
        for (bx, by, cc) in [(40, 72, 13), (48, 73, 4), (58, 71, 13), (64, 73, 12)]:
            d.rekt(bx, by, bx + 3, by + 2, 15)
            d.px(bx + 1, by, cc)
        # Tärningar och en hög med mynt
        d.rekt(30, 72, 32, 74, 15)
        d.px(31, 73, 0)
        for k in range(3):
            d.rekt(70, 74 - k, 74, 75 - k, 10)

    # Den nervösa spelaren med kort i hattbandet
    with d.yta("spelare"):
        px_ = 104
        d.rekt(px_ - 6, 88, px_ - 2, 104, 1)
        d.rekt(px_ + 2, 88, px_ + 6, 104, 1)
        d.rekt(px_ - 7, 102, px_ - 1, 105, 0)
        d.rekt(px_ + 1, 102, px_ + 7, 105, 0)
        d.poly([(px_ - 9, 58), (px_ + 9, 58), (px_ + 10, 90), (px_ - 10, 90)], 9)   # rock, rutig
        for y in range(60, 90, 4):
            d.rekt(px_ - 9, y, px_ + 9, y + 1, 8)
        for x in range(px_ - 8, px_ + 9, 4):
            d.rekt(x, 58, x + 1, 90, 8)
        d.poly([(px_ - 3, 58), (px_ + 3, 58), (px_, 70)], 15)
        d.rekt(px_ - 1, 60, px_ + 1, 70, 13)
        # Armar: biter på naglarna
        d.rekt(px_ - 12, 60, px_ - 7, 76, 9)
        d.linje(px_ + 8, 62, px_ + 4, 54, 9)
        d.linje(px_ + 9, 62, px_ + 5, 54, 9)
        hand(d, px_ + 2, 51)
        hand(d, px_ - 13, 75)
        # Huvud
        ell(d, px_ - 6, 42, px_ + 6, 58, 10)
        d.rekt(px_ - 3, 46, px_ - 1, 47, 15)         # stora oroliga ögon
        d.rekt(px_ + 2, 46, px_ + 4, 47, 15)
        d.px(px_ - 2, 47, 0)
        d.px(px_ + 3, 47, 0)
        d.rekt(px_, 48, px_ + 2, 51, 9)              # näsa
        for k in range(5):                           # darrig mun
            d.px(px_ - 2 + k, 53 + k % 2, 6)
        d.px(px_ + 6, 46, 5)                         # svettdroppe
        d.px(px_ + 6, 47, 5)
        d.px(px_ - 6, 49, 5)
        # Hatten med kort i bandet
        d.rekt(px_ - 10, 41, px_ + 10, 43, 4)
        d.rekt(px_ - 7, 32, px_ + 7, 41, 4)
        d.rekt(px_ - 7, 32, px_ + 7, 33, 5)
        d.rekt(px_ - 7, 38, px_ + 7, 40, 0)
        for (kx, ky, kc) in [(px_ + 2, 31, 13), (px_ + 5, 30, 0)]:
            d.rekt(kx, ky, kx + 4, ky + 7, 15)
            d.px(kx + 1, ky + 1, kc)
            d.px(kx + 2, ky + 3, kc)

    # Roulettbordet
    with d.yta("roulett"):
        d.poly([(120, 74), (188, 74), (192, 92), (114, 92)], 12)
        d.rekt(114, 92, 192, 96, 7)
        d.rekt(114, 92, 192, 93, 8)
        for bx in (118, 186):
            d.rekt(bx, 96, bx + 3, 112, 6)
        # Nummerfält
        for i, x in enumerate(range(156, 186, 5)):
            for j, y in enumerate((77, 81, 85)):
                c = 13 if (i + j) % 2 else 0
                d.rekt(x + (y - 77) // 4, y, x + 4 + (y - 77) // 4, y + 3, c)
        d.linje(153, 76, 157, 90, 15)
        # Jetonger
        for (cx, cy, cc) in [(160, 79, 15), (176, 83, 13), (166, 87, 10)]:
            for k in range(3):
                ell(d, cx, cy - k, cx + 4, cy + 2 - k, cc)
            d.px(cx + 2, cy - 2, 11 if cc != 15 else 4)
    # Croupieren (bakom bordet, ritad före bordskanten)
    with d.yta("croupier"):
        cx = 166
        d.rekt(cx - 10, 46, cx + 10, 74, 15)
        d.poly([(cx - 10, 50), (cx - 3, 48), (cx - 3, 74), (cx - 10, 74)], 0)   # väst
        d.poly([(cx + 10, 50), (cx + 3, 48), (cx + 3, 74), (cx + 10, 74)], 0)
        for y in (56, 62, 68):
            d.px(cx - 4, y, 10)
            d.px(cx + 3, y, 10)
        d.rekt(cx - 3, 46, cx + 4, 48, 0)            # fluga
        d.rekt(cx - 14, 48, cx - 9, 70, 15)
        d.rekt(cx + 9, 48, cx + 14, 70, 15)
        d.rekt(cx - 14, 54, cx - 9, 56, 13)          # armhållare
        d.rekt(cx + 9, 54, cx + 14, 56, 13)
        hand(d, cx - 14, 69)
        hand(d, cx + 11, 69)
        # Räfsa
        d.linje(cx - 13, 71, cx - 30, 80, 8)
        d.rekt(cx - 34, 79, cx - 27, 81, 8)
        # Huvud med mittbena och smal mustasch
        ell(d, cx - 6, 28, cx + 6, 46, 10)
        ell(d, cx - 7, 26, cx + 7, 36, 0)
        d.px(cx, 27, 3)
        d.px(cx, 28, 3)
        d.rekt(cx - 6, 32, cx - 5, 36, 0)
        d.rekt(cx + 5, 32, cx + 6, 36, 0)
        d.rekt(cx - 4, 37, cx - 2, 38, 0)
        d.rekt(cx + 2, 37, cx + 4, 38, 0)
        d.rekt(cx - 1, 38, cx + 1, 41, 9)
        d.rekt(cx - 4, 42, cx + 5, 43, 0)            # mustasch
        d.rekt(cx - 2, 44, cx + 3, 45, 7)
        # Grön skärm (visir)
        d.poly([(cx - 8, 31), (cx + 8, 31), (cx + 10, 34), (cx - 10, 34)], 12)
        d.rekt(cx - 10, 33, cx + 10, 34, 3)

    # Rouletthjulet (ovanpå bordet, vänster del)
    with d.yta("roulett"):
        hx, hy = 132, 82
        ell(d, hx - 13, hy - 6, hx + 13, hy + 6, 7)
        ell(d, hx - 12, hy - 5, hx + 12, hy + 5, 8)
        ell(d, hx - 11, hy - 4, hx + 11, hy + 4, 0)
        for k in range(16):
            a = k * math.pi / 8 + hjul * math.pi / 32
            c = 13 if k % 2 else 0
            if k == 0:
                c = 12
            for rr in (7, 9):
                d.px(int(round(hx + math.cos(a) * rr)), int(round(hy + math.sin(a) * rr * 0.45)), c)
                d.px(int(round(hx + math.cos(a) * (rr + 1))), int(round(hy + math.sin(a) * (rr + 1) * 0.45)), c)
        ell(d, hx - 5, hy - 2, hx + 5, hy + 2, 9)
        ell(d, hx - 3, hy - 1, hx + 3, hy + 1, 10)
        d.rekt(hx, hy - 4, hx + 1, hy, 10)
        d.rekt(hx - 2, hy - 4, hx + 3, hy - 3, 11)
        # Kulan
        a = hjul * math.pi / 2 + 0.4
        d.px(int(round(hx + math.cos(a) * 10)), int(round(hy + math.sin(a) * 4)), 11)

    # Skuldsedeln på bordet
    with d.yta("skuldsedel"):
        if sedel:
            d.poly([(141, 87), (151, 85), (153, 91), (143, 93)], 15)
            d.linje(146, 86, 148, 92, 5)
            for (nx, ny, nc) in [(143, 89, 0), (144, 89, 0), (149, 88, 13), (150, 88, 0), (144, 91, 4), (145, 91, 4), (150, 90, 4)]:
                d.px(nx, ny, nc)
            d.linje(143, 94, 153, 92, 0)             # skugga

    # Sigarettrök i lager
    d.ljus(YY < 30, 0.2)
    for i, (bx0, by0) in enumerate([(60, 38), (100, 24), (150, 26), (30, 30), (176, 20), (80, 14)]):
        t = (rok + i * 2) % 6
        cx = bx0 + t * 3
        cy = by0 - (t // 2)
        puff(d, cx, cy, 6 + (i % 3), 0.35)

    d.vinjett(0.55)
    return d


# ======================================================================
SCENER_D = {
    "tvatteri": (tvatteri, [
        ("anga", "anga", [(i, 220) for i in range(6)]),
        ("mangel", "mangel", [(i, 160) for i in range(4)]),
    ]),
    "radiohus": (radiohus, [
        ("onair", "onair", [(True, 1400), (False, 500)]),
        ("visare", "visare", [(i, 180) for i in range(6)]),
    ]),
    "bakgata": (bakgata, [
        ("regn", "regn", [(i, 90) for i in range(10)]),
        ("sving", "sving", [(i, 450) for i in range(4)]),
        ("fladder", "fladder", [(i, 300) for i in range(4)]),
    ]),
    "apotek": (apotek, [
        ("rok", "rok", [(i, 260) for i in range(6)]),
        ("vag", "vag", [(i, 600) for i in range(4)]),
    ]),
    "spelhala": (spelhala, [
        ("sedel", "sedel", [(True, 1000), (False, 1000)], 1),
        ("rok", "rok", [(i, 300) for i in range(6)]),
        ("hjul", "hjul", [(i, 90) for i in range(4)]),
    ]),
}
