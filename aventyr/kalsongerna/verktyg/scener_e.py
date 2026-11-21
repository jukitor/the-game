import math, random, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "motor" / "verktyg"))
from pixelbild import *  # noqa

"""Scener E: fiskmarknaden på kajen, entrén till nöjespiren, nöjespiren och spöktåget."""

# ======================================================================
#  EGNA TECKEN OCH HJÄLPFUNKTIONER
# ======================================================================
EXTRA_E = {
    "J": ["001", "001", "001", "101", "010"],
    "X": ["101", "101", "010", "101", "101"],
    "0": ["111", "101", "101", "101", "111"],
    "2": ["110", "001", "010", "100", "111"],
    "4": ["101", "101", "111", "001", "001"],
    "5": ["111", "100", "110", "001", "110"],
    "6": ["011", "100", "111", "101", "111"],
    "7": ["111", "001", "010", "010", "010"],
    "8": ["111", "101", "111", "101", "111"],
    ".": ["0", "0", "0", "0", "1"],
    "!": ["1", "1", "1", "0", "1"],
    "-": ["00", "00", "11", "00", "00"],
    "^": ["00100", "01110", "10101", "00100", "00100"],
    "v": ["00100", "00100", "10101", "01110", "00100"],
}
PRICK = {"Å": "A", "Ä": "A", "Ö": "O"}


def _glyf(ch):
    ch = PRICK.get(ch, ch)
    return EXTRA_E.get(ch) or TYPSNITT[ch]


def skriv(d, x, y, s, c, skala=1):
    """Text med extratecken. Å/Ä/Ö får sina prickar/ring ovanför raden (lämna plats)."""
    for ch in s:
        g = _glyf(ch)
        for ry, rad in enumerate(g):
            for rx, bit in enumerate(rad):
                if bit == "1":
                    d.rekt(x + rx * skala, y + ry * skala, x + (rx + 1) * skala, y + (ry + 1) * skala, c)
        if ch in ("Ä", "Ö"):
            for rx in (0, 2):
                d.rekt(x + rx * skala, y - 2 * skala, x + (rx + 1) * skala, y - skala, c)
        elif ch == "Å":
            d.rekt(x + skala, y - 3 * skala, x + 2 * skala, y - 2 * skala, c)
            d.rekt(x, y - 2 * skala, x + skala, y - skala, c)
            d.rekt(x + 2 * skala, y - 2 * skala, x + 3 * skala, y - skala, c)
        x += (len(g[0]) + 1) * skala


def bredd(s, skala=1):
    return (sum(len(_glyf(ch)[0]) + 1 for ch in s) - 1) * skala


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


def fyll(d, x0, y0, x1, y1, c):
    d.a[d.mask_ellips(x0, y0, x1, y1)] = c


def spegel(d, x0, x1, f, y0):
    for y in range(y0, H):
        s = f * (1 - (y - y0) / (H - y0))
        m = (XX >= x0) & (XX < x1) & (YY == y) & ((XX + y) % 2 == 0)
        d.ljus(m, s * 2)


def pilskylt(d, x, y, vanster, ybas=97):
    """Liten grön skylt med pil på en stolpe, x = stolpens x."""
    d.rekt(x, y, x + 1, ybas, 0)
    d.rekt(x - 1, ybas - 2, x + 2, ybas, 0)
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


def textskylt(d, cx, y, s, bg=12, fg=15, ram=15):
    """Skylt med centrerad text (klarar extratecknen)."""
    b = bredd(s)
    x0, x1 = cx - b // 2 - 3, cx - b // 2 + b + 3
    d.rekt(x0 - 1, y - 1, x1 + 1, y + 10, ram)
    d.rekt(x0, y, x1, y + 9, bg)
    skriv(d, x0 + 3, y + 2, s, fg)
    return x0, x1


def planka_golv(d, y0, bas=7, fog=6, steg=4, fro=1):
    rnd = random.Random(fro)
    d.rekt(0, y0, W, H, bas)
    for y in range(y0, H, steg):
        d.rekt(0, y, W, y + 1, fog)
        off = rnd.randint(0, 20)
        for x in range(off, W, 26):
            d.rekt(x, y + 1, x + 1, y + steg, fog)


def fotogenlampa(d, x, y, dx=0):
    """Hängande fotogenlampa: krok vid (x, y), glaset nedanför. dx = gungning."""
    d.linje(x, y, x + dx, y + 4, 0)
    lx = x + dx
    d.rekt(lx - 1, y + 4, lx + 2, y + 5, 0)
    d.rekt(lx - 2, y + 5, lx + 3, y + 6, 0)
    d.rekt(lx - 2, y + 6, lx + 3, y + 11, 11)
    d.rekt(lx - 2, y + 6, lx - 1, y + 11, 10)
    d.px(lx, y + 8, 15)
    d.px(lx + 1, y + 9, 10)
    d.rekt(lx - 3, y + 11, lx + 4, y + 12, 0)
    d.rekt(lx - 1, y + 12, lx + 2, y + 13, 9)


def mas(d, x, y, vand=False, huvud=0, vingar=0):
    """Fiskmås 16 x 10 px, tittar åt höger. huvud 1 = skriker, vingar 1 = lyfter vingarna."""
    if vingar:
        rader = ["..k.............", "..44......55....", "...44....5k55...", "....44...5555aa.",
                 "....4445555.....", "....445555555...", "....44455555....", ".....4445555....",
                 "......3..3......", "......a..a......"]
    else:
        rader = ["...........55...", "..........5k55..", "..........5555aa", ".k4.......555...",
                 ".k444...55555...", "..444445555555..", "...4444455555...", "....44445555....",
                 "......3..3......", "......a..a......"]
        if huvud:
            rader[0] = "..........55..a."
            rader[1] = ".........5k55a.."
            rader[2] = ".........5555.aa"
    if vand:
        rader = [r[::-1] for r in rader]
    t = Duk(16)
    sprite(t, x, y, rader, {"4": 4, "5": 15, "k": 0, "a": 10, "3": 9})
    kontur(d, t, 0)


# ======================================================================
#  FISKMARKNADEN PÅ KAJEN
# ======================================================================
def fisk_liggande(d, x, y, l, c=4, rygg=3, vand=False):
    """En fisk på isen, l lång."""
    m = d.mask_ellips(x, y, x + l, y + 4)
    d.a[m] = c
    d.a[m & (YY <= y + 1)] = rygg
    d.px(x + l - 1 if not vand else x + 1, y + 2, 0)
    tx = x - 1 if not vand else x + l + 1
    s = -1 if not vand else 1
    d.poly([(tx, y + 2), (tx + s * 3, y), (tx + s * 3, y + 4)], c)
    d.px(x + l // 2, y + 3, 15)


def fiskmarknad(v=None):
    v = v or {}
    masfas = v.get("masar", 0)       # 0..5
    gung = [0, 1, 0, -1][v.get("lampor", 0)]
    rnd = random.Random(5101)
    d = Duk(1)

    # --- Himmel och hav ---
    d.vgrad(0, 0, W, 46, [0, 0, 1, 1, 2])
    for _ in range(22):
        sx, sy = rnd.randint(0, W - 1), rnd.randint(0, 28)
        d.px(sx, sy, rnd.choice([3, 4, 4, 5]))
    d.vgrad(0, 44, W, 76, [1, 2, 2, 1])
    for y in range(46, 76, 3):
        for x in range(rnd.randint(0, 8), W, 11):
            d.rekt(x, y, x + rnd.randint(2, 5), y + 1, 3 if y < 60 else 2)
    # Nöjespirens färgglada ljus långt borta i öster
    d.radial(172, 40, 34, 0.45, mask=(YY < 44))
    d.rekt(142, 42, W, 44, 0)
    for x in range(144, W, 3):
        d.px(x, 41, [13, 10, 14, 12, 11][(x // 3) % 5])
    hx, hy, hr = 184, 27, 10
    for i in range(12):
        a = i * math.pi / 6
        d.linje(hx, hy, int(hx + hr * math.cos(a)), int(hy + hr * math.sin(a)), 2)
    for i in range(12):
        a = i * math.pi / 6
        d.px(int(round(hx + hr * math.cos(a))), int(round(hy + hr * math.sin(a))), [14, 10, 13, 11][i % 4])
    d.linje(hx, hy, hx - 6, 42, 0)
    d.linje(hx, hy, hx + 6, 42, 0)
    d.px(hx, hy, 11)
    for x in range(144, W, 5):           # ljusens spegling i vattnet
        for y in range(46, 60, 2):
            if rnd.random() < 0.5:
                d.px(x, y, [13, 10, 14, 12, 11][(x // 3) % 5] if y < 52 else 3)
    # Fyren långt ute till havs
    fx = 6
    d.poly([(fx - 6, 46), (fx - 3, 42), (fx + 7, 42), (fx + 10, 46)], 0)
    d.rekt(fx, 22, fx + 4, 43, 15)
    for y in range(24, 43, 5):
        d.rekt(fx, y, fx + 4, y + 2, 13)
    d.rekt(fx - 1, 19, fx + 5, 22, 0)
    d.rekt(fx, 17, fx + 4, 19, 11)
    d.rekt(fx + 1, 15, fx + 3, 17, 0)
    d.radial(fx + 2, 18, 12, 0.6, mask=YY < 44)
    d.ljus(d.mask_poly([(fx + 2, 18), (70, 10), (70, 22)]) & ((XX + YY) % 2 == 0), 0.3)

    # --- Kajen ---
    planka_golv(d, 76, 7, 6, 4, 5101)
    d.vgrad(0, 76, W, 82, [6, 7])
    d.ljus(d.mask_poly([(0, 76), (W, 76), (W, H), (0, H)]), 0.35, MORKARE)
    d.rekt(0, 76, W, 77, 0)

    # --- Gången norrut ut på piren (utgång) ---
    with d.yta("utgang:n"):
        d.poly([(76, 78), (110, 78), (96, 46), (91, 46)], 7)
        for y in range(48, 78, 2):
            t = (y - 46) / 32
            xa, xb = 91 - 15 * t, 96 + 14 * t
            if y % 4 == 0:
                d.linje(int(xa), y, int(xb), y, 6)
        d.vgrad(76, 46, 111, 56, [1, 6])
        d.a[(d.mask_poly([(76, 78), (110, 78), (96, 46), (91, 46)])) & (YY < 56) & (d.a == 1)] = 6
        # Räcken och lyktor längs gången
        for k, t in enumerate((0.15, 0.45, 1.0)):
            yb = int(46 + 32 * t)
            hh = int(3 + 10 * t)
            for xx in (int(91 - 15 * t) - 1, int(96 + 14 * t) + 1):
                d.rekt(xx, yb - hh, xx + 1, yb, 0)
                d.px(xx, yb - hh - 1, 10)
        d.linje(90, 44, 74, 64, 0)
        d.linje(97, 44, 112, 64, 0)
        d.rekt(90, 41, 98, 46, 0)          # skjulet längst ut
        d.px(93, 43, 10)
        d.px(94, 43, 10)
        # Portalen med skylten PIREN
        for gx in (78, 108):
            d.rekt(gx, 30, gx + 3, 80, 6)
            d.rekt(gx, 30, gx + 1, 80, 8)
        d.rekt(76, 29, 113, 31, 6)
        d.rekt(76, 29, 113, 30, 9)
        d.rekt(84, 31, 85, 33, 0)
        d.rekt(102, 31, 103, 33, 0)
        textskylt(d, 94, 34, "PIREN ^", 12, 15, 15)
    d.markera("utgang:n", 80, 30, 108, 78)

    # --- Vänstra ståndet: fisk på is ---
    with d.yta("fisklador"):
        for px_ in (3, 57):
            d.rekt(px_, 40, px_ + 3, 92, 6)
            d.rekt(px_, 40, px_ + 1, 92, 7)
        d.rekt(5, 48, 58, 70, 6)
        d.ljus(d.mask_poly([(5, 48), (58, 48), (58, 70), (5, 70)]), 0.5, MORKARE)
        # Torkad fisk och nät på bakväggen
        for i, fx in enumerate(range(12, 54, 7)):
            d.linje(fx, 50, fx, 53, 0)
            d.rekt(fx - 1, 53, fx + 2, 61, 8 if i % 2 else 9)
            d.poly([(fx - 2, 61), (fx + 3, 61), (fx + 1, 59)], 7)
            d.px(fx, 54, 0)
        for x in range(8, 56, 3):
            d.px(x, 63, 4)
            d.px(x + 1, 64, 4)
        # Markisen
        for i, x in enumerate(range(1, 63, 4)):
            c = 13 if i % 2 == 0 else 15
            d.rekt(x, 38, x + 4, 46, c)
            fyll(d, x, 44, x + 3, 49, c)
        d.rekt(1, 38, 63, 39, 14)
        d.ljus(d.mask_poly([(1, 38), (63, 38), (63, 50), (1, 50)]), 0.3, MORKARE)
        # Skylten
        d.rekt(14, 26, 61, 37, 0)
        d.rekt(15, 27, 60, 36, 15)
        d.rekt(15, 27, 60, 28, 10)
        skriv(d, 18, 30, "FRESH FISH", 13)
        d.rekt(19, 37, 20, 38, 0)
        d.rekt(55, 37, 56, 38, 0)
        # Isdisken
        d.poly([(4, 70), (60, 70), (62, 80), (2, 80)], 5)
        d.ljus(d.mask_poly([(4, 70), (60, 70), (62, 80), (2, 80)]) & ((XX * 3 + YY) % 5 == 0), 0.9)
        for (fx, fy, l, c, r) in ((6, 71, 11, 4, 3), (19, 70, 12, 4, 3), (34, 71, 11, 13, 6),
                                  (47, 70, 10, 4, 3), (10, 75, 12, 13, 6), (26, 75, 13, 4, 3),
                                  (42, 75, 14, 4, 2)):
            fisk_liggande(d, fx, fy, l, c, r, vand=(fx // 10) % 2 == 1)
        # En hummer
        fyll(d, 54, 74, 60, 78, 13)
        d.linje(54, 75, 51, 72, 13)
        d.linje(59, 75, 61, 72, 13)
        d.px(56, 75, 0)
        # Disken framifrån
        d.rekt(2, 80, 62, 92, 8)
        for x in range(2, 62, 6):
            d.rekt(x, 80, x + 1, 92, 7)
        d.rekt(2, 80, 62, 81, 9)
        for (kx, s) in ((8, "5C"), (26, "8C"), (44, "2C")):
            d.rekt(kx, 83, kx + 10, 90, 15)
            skriv(d, kx + 2, 84, s, 0)
        # Lådor på marken
        for (bx, by) in ((4, 90), (20, 92)):
            d.rekt(bx, by, bx + 14, by + 8, 8)
            d.rekt(bx, by, bx + 14, by + 1, 9)
            d.rekt(bx, by + 4, bx + 14, by + 5, 7)
            d.rekt(bx + 1, by - 2, bx + 13, by, 5)
            d.px(bx + 4, by - 2, 4)
            d.px(bx + 9, by - 2, 15)
            d.px(bx + 3, by - 1, 0)
        fotogenlampa(d, 32, 46, gung)
    d.radial(32, 58, 40, 0.6, mask=(XX < 80) & (d.a != 11))

    # --- Två pålar med måsar ---
    with d.yta("masar2"):
        for px_, top in ((63, 42), (72, 52)):
            d.rekt(px_, top, px_ + 5, 86, 7)
            d.rekt(px_, top, px_ + 1, 86, 8)
            d.rekt(px_ + 4, top, px_ + 5, 86, 6)
            d.rekt(px_, top, px_ + 5, top + 1, 9)
            for y in range(top + 4, 86, 7):
                d.px(px_ + 2, y, 6)
        d.rekt(61, 62, 77, 64, 9)          # rep runt pålarna
        d.rekt(61, 63, 77, 64, 8)
        mas(d, 57, 32, True, huvud=masfas in (2, 3), vingar=0)
        mas(d, 66, 42, False, huvud=0, vingar=masfas == 4)
        for (sx, sy) in ((64, 46), (63, 51), (73, 56), (74, 60)):   # spillning
            d.px(sx, sy, 15)
    d.markera("masar2", 58, 32, 80, 64)

    # --- Högra ståndet med hängvågen ---
    for px_ in (126, 172):
        d.rekt(px_, 42, px_ + 3, 98, 6)
        d.rekt(px_, 42, px_ + 1, 98, 7)
    for i, x in enumerate(range(122, 178, 4)):
        c = 12 if i % 2 == 0 else 15
        d.rekt(x, 38, x + 4, 46, c)
        fyll(d, x, 44, x + 3, 49, c)
    d.rekt(122, 38, 178, 39, 4)
    d.ljus(d.mask_poly([(122, 38), (178, 38), (178, 50), (122, 50)]), 0.3, MORKARE)
    d.rekt(128, 50, 172, 80, 6)
    d.ljus(d.mask_poly([(128, 50), (172, 50), (172, 80), (128, 80)]), 0.55, MORKARE)
    d.rekt(132, 28, 170, 37, 0)
    d.rekt(133, 29, 169, 36, 12)
    skriv(d, 136, 31, "OYSTERS", 15)
    # Tunnor med ostron och is
    for (tx, tw) in ((146, 12), (160, 11)):
        d.rekt(tx, 82, tx + tw, 98, 7)
        d.rekt(tx + 1, 82, tx + 3, 98, 8)
        d.rekt(tx, 85, tx + tw, 86, 0)
        d.rekt(tx, 94, tx + tw, 95, 0)
        fyll(d, tx, 79, tx + tw, 84, 5)
        for k in range(3):
            d.px(tx + 2 + k * 3, 80 + k % 2, 3)
    fotogenlampa(d, 150, 46, -gung)
    d.radial(150, 58, 34, 0.55, mask=(XX > 112) & (d.a != 11))

    with d.yta("fiskvag"):
        vx, vy = 164, 54
        d.rekt(vx, 48, vx + 1, vy, 0)
        d.px(vx, 49, 4)
        d.px(vx, 51, 4)
        fyll(d, vx - 5, vy, vx + 6, vy + 11, 0)
        fyll(d, vx - 4, vy + 1, vx + 5, vy + 10, 15)
        d.a[d.mask_ellips(vx - 4, vy + 1, vx + 5, vy + 10) & (YY > vy + 7)] = 5
        for i in range(8):
            a = math.pi + i * math.pi / 7
            d.px(int(round(vx + 0.5 + 3.4 * math.cos(a))), int(round(vy + 5.5 + 3.4 * math.sin(a))), 0)
        d.linje(vx, vy + 6, vx + 3, vy + 3, 13)
        d.px(vx, vy + 6, 0)
        d.rekt(vx, vy + 11, vx + 1, vy + 14, 0)
        d.linje(vx, vy + 14, vx - 7, vy + 21, 4)
        d.linje(vx, vy + 14, vx + 7, vy + 21, 4)
        d.a[d.mask_ellips(vx - 8, vy + 20, vx + 8, vy + 24) & (YY >= vy + 21)] = 4
        d.rekt(vx - 8, vy + 21, vx + 9, vy + 22, 5)
        fisk_liggande(d, vx - 5, vy + 17, 10, 13, 6)

    # --- Fiskhandlaren ---
    with d.yta("fiskhandlare"):
        fx = 106
        t = Duk(16)
        t.rekt(fx + 4, 92, fx + 10, 102, 0)          # stövlar
        t.rekt(fx + 12, 92, fx + 18, 102, 0)
        t.rekt(fx + 3, 100, fx + 10, 102, 0)
        t.rekt(fx + 12, 100, fx + 19, 102, 0)
        t.rekt(fx + 5, 93, fx + 6, 99, 2)
        t.rekt(fx + 13, 93, fx + 14, 99, 2)
        t.rekt(fx + 4, 84, fx + 18, 93, 2)           # byxor
        t.rekt(fx + 2, 62, fx + 20, 84, 15)          # randig tröja
        for y in range(63, 84, 3):
            t.rekt(fx + 2, y, fx + 20, y + 1, 3)
        t.rekt(fx + 4, 64, fx + 18, 94, 12)          # gummiförkläde
        t.rekt(fx + 5, 64, fx + 6, 94, 4)
        t.px(fx + 7, 70, 5)
        t.px(fx + 15, 80, 4)
        t.rekt(fx + 4, 62, fx + 5, 65, 12)
        t.rekt(fx + 17, 62, fx + 18, 65, 12)
        t.rekt(fx + 6, 86, fx + 9, 89, 13)            # fläck
        t.px(fx + 14, 74, 6)
        # Vänster arm i sidan
        t.rekt(fx, 63, fx + 3, 72, 15)
        t.rekt(fx - 1, 72, fx + 3, 77, 9)
        t.rekt(fx + 1, 76, fx + 4, 79, 10)
        # Höger arm ut åt sidan, håller fisken i stjärten
        t.rekt(fx + 19, 63, fx + 26, 67, 15)
        t.rekt(fx + 19, 64, fx + 26, 65, 3)
        t.rekt(fx + 25, 63, fx + 30, 67, 9)
        t.rekt(fx + 29, 61, fx + 33, 66, 10)
        # Fisken
        fiskx = fx + 31
        t.poly([(fiskx - 3, 60), (fiskx + 4, 60), (fiskx + 1, 64)], 4)   # stjärt
        t.a[t.mask_ellips(fiskx - 4, 64, fiskx + 5, 92)] = 4
        t.a[t.mask_ellips(fiskx - 4, 64, fiskx + 5, 92) & (XX <= fiskx - 2)] = 3
        t.a[t.mask_ellips(fiskx - 4, 64, fiskx + 5, 92) & (XX >= fiskx + 3)] = 5
        for y in range(68, 88, 3):
            t.px(fiskx + 1, y, 5)
            t.px(fiskx - 1, y + 1, 5)
        t.px(fiskx + 2, 87, 0)                       # öga
        t.px(fiskx + 2, 86, 15)
        t.rekt(fiskx - 1, 90, fiskx + 2, 93, 13)     # öppen mun
        t.px(fiskx, 91, 0)
        t.linje(fiskx + 4, 76, fiskx + 6, 74, 4)     # fena
        # Huvudet
        t.rekt(fx + 8, 58, fx + 14, 62, 9)           # hals
        t.rekt(fx + 5, 47, fx + 17, 59, 10)
        t.rekt(fx + 5, 55, fx + 17, 59, 9)           # skäggstubb
        t.rekt(fx + 4, 50, fx + 5, 54, 9)            # öron
        t.rekt(fx + 17, 50, fx + 18, 54, 9)
        t.px(fx + 8, 51, 0)
        t.px(fx + 14, 51, 0)
        t.rekt(fx + 7, 49, fx + 10, 50, 7)           # buskiga ögonbryn
        t.rekt(fx + 13, 49, fx + 16, 50, 7)
        t.rekt(fx + 10, 51, fx + 13, 55, 9)          # stor näsa
        t.rekt(fx + 11, 53, fx + 13, 55, 14)
        t.rekt(fx + 6, 54, fx + 9, 55, 14)           # röda kinder
        t.rekt(fx + 14, 54, fx + 17, 55, 14)
        t.rekt(fx + 7, 55, fx + 16, 57, 15)          # grå mustasch
        t.rekt(fx + 9, 57, fx + 14, 58, 6)           # mun
        t.rekt(fx + 4, 42, fx + 18, 48, 13)          # stickad mössa
        t.rekt(fx + 4, 46, fx + 18, 48, 6)
        for x in range(fx + 5, fx + 18, 2):
            t.px(x, 44, 14)
        t.rekt(fx + 9, 41, fx + 13, 42, 13)
        t.rekt(fx + 4, 59, fx + 18, 62, 15)          # krage
        kontur(d, t)
    d.radial(126, 70, 30, 0.35, mask=(XX > 100) & (XX < 150) & (YY > 40) & (YY < 104) & (d.a != 11))

    # --- Trappan söderut ner mot fyrbåten (utgång) ---
    with d.yta("utgang:s"):
        d.rekt(60, 106, 96, H, 0)
        for k, y in enumerate(range(108, H, 3)):
            d.rekt(62, y, 94, y + 1, 3 if k % 2 == 0 else 2)
            d.rekt(62, y + 1, 94, y + 2, 1)
        for gx in (58, 95):
            d.rekt(gx, 98, gx + 3, H, 6)
            d.rekt(gx, 98, gx + 1, H, 8)
            d.rekt(gx - 1, 96, gx + 4, 98, 9)
        d.rekt(58, 99, 98, 101, 8)
        textskylt(d, 78, 100, "TILL FYREN v", 12, 15, 15)
    d.markera("utgang:s", 58, 98, 98, H)

    # --- Kajen fortsätter österut (utgång) ---
    with d.yta("utgang:ö"):
        d.rekt(178, 76, W, 78, 8)
        pilskylt(d, 184, 66, False, 98)
    d.markera("utgang:ö", 176, 52, W, 104)

    d.radial(32, 94, 30, 0.45, mask=(YY >= 80) & (d.a < 10))
    d.radial(150, 100, 28, 0.4, mask=(YY >= 98) & (d.a < 10))
    # Våta plankor speglar lamporna
    spegel(d, 26, 40, 0.5, 96)
    spegel(d, 144, 156, 0.45, 99)
    d.vinjett(0.4)
    return d


# ======================================================================
#  ENTRÉN TILL NÖJESPIREN
# ======================================================================
def glodlampa(d, x, y, tand):
    d.px(x, y, 11 if tand else 9)
    if tand:
        d.px(x, y - 1, 10)


def nojespir_entre(v=None):
    v = v or {}
    jakt = v.get("lampor", 0)       # glödlamporna jagar 0..2
    vift = v.get("vift", 0)         # utroparens megafon 0..2
    rnd = random.Random(5201)
    d = Duk(1)

    # --- Himmel ---
    d.vgrad(0, 0, W, 70, [0, 0, 1, 1, 2])
    for _ in range(26):
        sx, sy = rnd.randint(0, W - 1), rnd.randint(0, 40)
        d.px(sx, sy, rnd.choice([3, 4, 5]))
    d.a[d.mask_ellips(10, 6, 19, 15)] = 15          # månen
    d.a[d.mask_ellips(13, 5, 22, 14)] = 0
    d.radial(14, 10, 14, 0.4, mask=d.a < 4)

    # --- Planket längs piren ---
    d.rekt(0, 62, W, 96, 7)
    for x in range(0, W, 5):
        d.rekt(x, 62, x + 4, 96, 8)
        d.rekt(x + 4, 62, x + 5, 96, 6)
        d.poly([(x, 62), (x + 4, 62), (x + 2, 59)], 8)
    d.rekt(0, 70, W, 72, 6)
    d.rekt(0, 88, W, 90, 6)
    d.ljus(d.mask_poly([(0, 58), (W, 58), (W, 96), (0, 96)]), 0.55, MORKARE)
    # En gammal affisch på planket
    d.rekt(152, 64, 168, 84, 15)
    d.rekt(153, 65, 167, 70, 13)
    skriv(d, 154, 66, "WOW!", 15)
    d.a[d.mask_ellips(156, 71, 164, 81)] = 9
    d.px(158, 75, 0)
    d.px(162, 75, 0)
    d.rekt(158, 78, 163, 79, 13)
    d.ljus(d.mask_poly([(152, 64), (168, 64), (168, 84), (152, 84)]), 0.4, MORKARE)

    # --- Bryggans plankor ---
    planka_golv(d, 96, 7, 6, 4, 5202)
    d.vgrad(0, 96, W, 101, [0, 6])
    d.ljus(d.mask_poly([(0, 96), (W, 96), (W, H), (0, H)]), 0.4, MORKARE)

    # --- Genom bågen: nöjespiren i fjärran (utgång in) ---
    with d.yta("utgang:in"):
        ox0, ox1 = 52, 140
        d.vgrad(ox0, 30, ox1, 96, [1, 2, 3, 3])
        d.radial(96, 70, 50, 0.4, mask=(XX >= ox0) & (XX < ox1) & (YY < 96))
        # Pariserhjulet långt bort
        hx, hy, hr = 120, 50, 16
        for i in range(8):
            a = i * math.pi / 4
            d.linje(hx, hy, int(hx + hr * math.cos(a)), int(hy + hr * math.sin(a)), 1)
        m = d.mask_ellips(hx - hr, hy - hr, hx + hr, hy + hr) & ~d.mask_ellips(hx - hr + 1, hy - hr + 1, hx + hr - 1, hy + hr - 1)
        d.a[m] = 1
        for i in range(16):
            a = i * math.pi / 8
            d.px(int(round(hx + hr * math.cos(a))), int(round(hy + hr * math.sin(a))), [14, 11, 13, 10][i % 4])
        d.linje(hx, hy, hx - 8, 74, 1)
        d.linje(hx, hy, hx + 8, 74, 1)
        # Stånd och tält i fjärran
        for (bx0, bx1, top) in ((52, 70, 70), (70, 84, 66), (84, 102, 72), (128, 140, 68)):
            d.rekt(bx0, top, bx1, 80, 1)
            d.poly([(bx0, top), (bx1, top), ((bx0 + bx1) // 2, top - 5)], 1)
            for x in range(bx0 + 2, bx1 - 2, 4):
                d.px(x, top + 3, 10)
            d.px((bx0 + bx1) // 2, top - 6, 13)
        # Ljusslingor
        for (xa, ya, xb, yb) in ((ox0, 38, 96, 48), (96, 48, ox1, 36)):
            for k in range(0, 45, 3):
                t = k / 44
                x = int(xa + (xb - xa) * t)
                y = int(ya + (yb - ya) * t + 4 * math.sin(t * math.pi))
                d.px(x, y, [13, 10, 14, 12, 11][(k // 3) % 5])
        # Plankgången in
        d.poly([(ox0, 96), (ox1, 96), (110, 80), (82, 80)], 7)
        for y in range(82, 96, 3):
            d.rekt(ox0, y, ox1, y + 1, 6)
        d.a[(YY >= 80) & (YY < 96) & (XX >= ox0) & (XX < ox1) & ~d.mask_poly([(ox0, 96), (ox1, 96), (110, 80), (82, 80)])] = 2
        d.radial(96, 92, 34, 0.4, mask=(YY >= 80) & (YY < 96) & (XX >= ox0) & (XX < ox1))
        # Räcken vid vändkorset
        for (xa, xb) in ((ox0, 87), (105, ox1)):
            d.rekt(xa, 80, xb, 81, 5)
            d.rekt(xa, 86, xb, 87, 4)
            for x in range(xa + 3, xb, 10):
                d.rekt(x, 80, x + 1, 97, 4)
        # Vändkorset
        d.rekt(92, 74, 100, 98, 3)
        d.rekt(92, 74, 93, 98, 5)
        d.rekt(99, 74, 100, 98, 2)
        d.rekt(91, 72, 101, 75, 4)
        d.rekt(91, 72, 101, 73, 5)
        d.rekt(94, 77, 98, 80, 15)                 # myntskylt
        d.px(95, 78, 0)
        d.px(96, 78, 0)
        d.rekt(78, 80, 92, 82, 5)                  # vändkorsets armar
        d.rekt(78, 80, 92, 81, 15)
        d.rekt(78, 82, 92, 83, 3)
        d.linje(100, 81, 108, 87, 5)
        d.linje(100, 82, 108, 88, 4)
        d.linje(100, 79, 106, 72, 5)
        d.linje(101, 79, 107, 72, 4)
        d.rekt(78, 79, 80, 84, 5)
        d.rekt(90, 96, 102, 98, 2)
    d.markera("utgang:in", 82, 40, 112, 98)

    # --- Bågen med glödlampor ---
    bulbs = []
    for pxa in (40, 140):
        d.rekt(pxa, 30, pxa + 12, 98, 13)
        d.rekt(pxa, 30, pxa + 2, 98, 14)
        d.rekt(pxa + 10, 30, pxa + 12, 98, 6)
        d.rekt(pxa + 4, 34, pxa + 8, 94, 6)
        for y in range(36, 94, 4):
            bulbs.append((pxa + 6, y))
        d.rekt(pxa - 2, 92, pxa + 14, 98, 9)
        d.rekt(pxa - 2, 92, pxa + 14, 93, 10)
        d.rekt(pxa - 1, 30, pxa + 13, 33, 10)
    # Krönet med solfjäder och stjärna
    krona = d.mask_ellips(54, -6, 138, 26) & (YY < 12)
    d.a[krona] = 13
    for k in range(-6, 7):
        d.linje(96, 12, 96 + k * 7, -4, 9)
    d.a[krona & ~d.mask_ellips(56, -4, 136, 24)] = 10
    d.poly([(96, 0), (98, 4), (102, 4), (99, 6), (100, 10), (96, 8), (92, 10), (93, 6), (90, 4), (94, 4)], 11)
    # Skylten
    d.rekt(36, 10, 156, 32, 10)
    d.rekt(37, 11, 155, 31, 0)
    d.rekt(39, 13, 153, 29, 1)
    d.rekt(39, 13, 153, 14, 2)
    tx = 96 - bredd("NÖJESPIREN", 2) // 2
    skriv(d, tx + 1, 18, "NÖJESPIREN", 13, 2)
    skriv(d, tx, 17, "NÖJESPIREN", 11, 2)
    for x in range(38, 156, 4):
        bulbs.append((x, 11))
        bulbs.append((x + 2, 30))
    for y in range(15, 30, 4):
        bulbs.append((37, y))
        bulbs.append((154, y))
    for x in range(58, 136, 5):
        y = int(10 - 15 * math.sqrt(max(0, 1 - ((x - 96) / 42) ** 2)))
        if y >= 0:
            bulbs.append((x, y + 1))
    for i, (bx, by) in enumerate(bulbs):
        glodlampa(d, bx, by, (i + jakt) % 3 != 0)
    d.radial(96, 20, 70, 0.35, mask=(d.a < 9) & (YY < 40))
    for pxa in (46, 146):
        d.radial(pxa, 64, 18, 0.35, mask=(d.a < 9) & (YY < 96))

    # --- Biljettkiosken ---
    with d.yta("biljettkiosk"):
        kx0, kx1 = 13, 41
        d.rekt(kx0, 46, kx1, 98, 8)
        for x in range(kx0, kx1, 4):
            d.rekt(x, 46, x + 2, 98, 13)
        d.rekt(kx0, 46, kx0 + 1, 98, 6)
        d.poly([(kx0 - 3, 46), (kx1 + 3, 46), (27, 36)], 13)
        for k in range(4):
            d.poly([(kx0 - 3 + k * 9, 46), (27, 36), (kx0 + 1 + k * 9, 46)], 15)
        d.rekt(kx0 - 3, 45, kx1 + 3, 47, 10)
        d.rekt(26, 33, 28, 36, 10)
        d.px(27, 32, 11)
        # Fönstret med biljettdamen
        d.rekt(kx0 + 3, 54, kx1 - 3, 74, 6)
        d.rekt(kx0 + 4, 55, kx1 - 4, 73, 10)
        d.vgrad(kx0 + 4, 55, kx1 - 4, 73, [11, 10, 9])
        d.a[d.mask_ellips(22, 56, 32, 66)] = 7            # håret i knut
        d.rekt(23, 60, 31, 68, 15)
        d.rekt(23, 59, 31, 61, 7)
        d.rekt(24, 62, 27, 63, 0)                        # glasögon
        d.rekt(28, 62, 31, 63, 0)
        d.px(25, 62, 5)
        d.px(29, 62, 5)
        d.rekt(26, 65, 29, 66, 13)
        d.rekt(21, 68, 33, 73, 4)
        d.rekt(26, 68, 28, 73, 15)
        for x in range(kx0 + 4, kx1 - 4, 3):
            d.rekt(x, 55, x + 1, 73, 9)
        d.rekt(kx0 + 1, 73, kx1 - 1, 76, 9)
        d.rekt(kx0 + 1, 73, kx1 - 1, 74, 10)
        d.rekt(kx0 - 2, 48, kx1 + 2, 54, 0)
        skriv(d, kx0 + 1, 49, "TICKETS", 11)
        d.rekt(kx0 + 6, 80, kx1 - 6, 89, 15)
        skriv(d, kx0 + 8, 82, "10C", 13)
        d.rekt(kx0 - 1, 96, kx1 + 1, 98, 6)
    d.radial(27, 64, 22, 0.45, mask=(d.a < 9))

    # --- Popcornvagnen ---
    with d.yta("popcornvagn"):
        cx0, cx1 = 158, 188
        d.rekt(cx0, 78, cx1, 92, 13)
        d.rekt(cx0, 78, cx1, 79, 10)
        d.rekt(cx0, 91, cx1, 92, 10)
        d.rekt(cx1 - 3, 79, cx1, 91, 6)
        skriv(d, cx0 + 2, 82, "POPCORN", 11)
        d.rekt(cx0 + 1, 60, cx1 - 1, 78, 2)
        d.rekt(cx0 + 2, 61, cx1 - 2, 77, 10)
        for y in range(66, 77):
            for x in range(cx0 + 2, cx1 - 2):
                if (x * 7 + y * 3) % 5 < 3 and y > 66 + abs(x - 173) // 5:
                    d.px(x, y, 15 if (x + y) % 3 else 11)
        d.rekt(cx0 + 2, 61, cx0 + 3, 77, 5)
        d.rekt(cx0, 60, cx1, 61, 4)
        for gx in (cx0, cx1 - 1):
            d.rekt(gx, 52, gx + 1, 78, 4)
        d.rekt(170, 62, 176, 66, 4)                # kittel
        d.rekt(172, 66, 174, 68, 4)
        for i, x in enumerate(range(cx0 - 2, cx1 + 2, 4)):
            c = 13 if i % 2 == 0 else 15
            d.rekt(x, 48, x + 4, 54, c)
            fyll(d, x, 52, x + 3, 57, c)
        d.rekt(cx0 - 2, 47, cx1 + 2, 48, 10)
        d.rekt(172, 44, 174, 47, 10)
        d.px(173, 43, 13)
        for wx in (163, 183):
            fyll(d, wx - 5, 89, wx + 5, 99, 0)
            fyll(d, wx - 4, 90, wx + 4, 98, 9)
            fyll(d, wx - 2, 92, wx + 2, 96, 0)
            d.linje(wx - 3, 94, wx + 3, 94, 9)
            d.linje(wx, 91, wx, 97, 9)
            d.px(wx, 94, 10)
        d.rekt(cx0 - 6, 82, cx0, 83, 4)            # handtag
        d.rekt(cx0 - 7, 80, cx0 - 5, 85, 0)
        d.px(178, 63, 15)                           # popcorn som hoppar
        d.px(167, 64, 11)
    d.radial(173, 70, 22, 0.5, mask=(d.a < 9))

    # --- Utgång västerut ---
    with d.yta("utgang:v"):
        d.rekt(0, 96, 12, 98, 8)
        pilskylt(d, 6, 66, True, 99)
    d.markera("utgang:v", 0, 52, 12, 106)

    # --- Utroparen Lou ---
    with d.yta("lou"):
        lx = 58
        t = Duk(16)
        t.rekt(lx + 4, 97, lx + 11, 101, 0)          # skor
        t.rekt(lx + 13, 97, lx + 20, 101, 0)
        t.px(lx + 6, 98, 4)
        t.px(lx + 18, 98, 4)
        t.rekt(lx + 5, 80, lx + 11, 98, 2)           # byxor med röd rand
        t.rekt(lx + 13, 80, lx + 19, 98, 2)
        t.rekt(lx + 5, 80, lx + 6, 98, 13)
        t.rekt(lx + 18, 80, lx + 19, 98, 13)
        t.rekt(lx + 3, 58, lx + 21, 84, 13)          # röd uniformsjacka
        t.rekt(lx + 3, 58, lx + 5, 84, 14)
        t.rekt(lx + 19, 58, lx + 21, 84, 6)
        t.rekt(lx + 11, 58, lx + 13, 84, 6)
        for y in range(62, 82, 4):                   # mässingsknappar
            t.px(lx + 9, y, 11)
            t.px(lx + 15, y, 11)
        t.rekt(lx + 3, 76, lx + 21, 78, 10)          # guldbälte
        t.rekt(lx + 11, 76, lx + 13, 78, 11)
        t.rekt(lx + 1, 57, lx + 6, 60, 10)           # epåletter
        t.rekt(lx + 18, 57, lx + 23, 60, 10)
        t.px(lx + 2, 60, 9)
        t.px(lx + 4, 60, 9)
        t.px(lx + 20, 60, 9)
        t.px(lx + 22, 60, 9)
        # Högra armen pekar mot grinden
        t.rekt(lx + 21, 60, lx + 27, 64, 13)
        t.rekt(lx + 26, 58, lx + 31, 63, 13)
        t.rekt(lx + 30, 57, lx + 35, 62, 15)
        t.rekt(lx + 34, 58, lx + 37, 60, 15)
        t.rekt(lx + 30, 61, lx + 31, 62, 10)
        # Huvudet med brett leende
        t.rekt(lx + 9, 54, lx + 15, 58, 10)
        t.rekt(lx + 6, 41, lx + 18, 55, 10)
        t.rekt(lx + 6, 41, lx + 7, 55, 9)
        t.rekt(lx + 5, 46, lx + 6, 50, 9)
        t.rekt(lx + 18, 46, lx + 19, 50, 9)
        t.px(lx + 9, 45, 0)
        t.px(lx + 15, 45, 0)
        t.rekt(lx + 8, 43, lx + 11, 44, 7)
        t.rekt(lx + 14, 43, lx + 17, 44, 7)
        t.rekt(lx + 11, 46, lx + 13, 49, 9)
        t.rekt(lx + 7, 49, lx + 9, 50, 14)
        t.rekt(lx + 16, 49, lx + 18, 50, 14)
        t.rekt(lx + 8, 50, lx + 17, 51, 7)           # tunn mustasch
        t.px(lx + 7, 49, 7)
        t.px(lx + 17, 49, 7)
        t.rekt(lx + 8, 51, lx + 17, 54, 0)           # grinet
        t.rekt(lx + 9, 51, lx + 16, 52, 15)
        t.px(lx + 8, 51, 6)
        t.px(lx + 16, 53, 13)
        t.px(lx + 12, 53, 13)
        t.rekt(lx + 8, 55, lx + 16, 58, 15)          # krage
        t.rekt(lx + 11, 56, lx + 13, 58, 13)
        # Stråhatten
        t.rekt(lx + 2, 39, lx + 22, 41, 9)
        t.rekt(lx + 2, 39, lx + 22, 40, 10)
        t.rekt(lx + 6, 32, lx + 18, 39, 10)
        t.rekt(lx + 6, 32, lx + 18, 33, 11)
        t.rekt(lx + 6, 36, lx + 18, 38, 13)
        for x in range(lx + 7, lx + 18, 2):
            t.px(x, 34, 9)
        # Vänstra armen med megafonen
        hx, hy = lx + 1, [60, 54, 50][vift]
        t.rekt(lx, 59, lx + 4, 66, 13)
        t.linje(lx + 1, 60, hx - 1, hy, 13)
        t.linje(lx + 2, 60, hx, hy, 13)
        t.linje(lx + 3, 61, hx + 1, hy + 1, 13)
        t.rekt(hx - 2, hy - 1, hx + 2, hy + 2, 15)
        dx, dy = [(-0.95, -0.3), (-0.75, -0.66), (-0.4, -0.92)][vift]
        pxv, pyv = -dy, dx
        L = 15
        ex, ey = hx + dx * L, hy + dy * L
        t.poly([(hx + pxv * 1.2, hy + pyv * 1.2), (ex + pxv * 5, ey + pyv * 5),
                (ex - pxv * 5, ey - pyv * 5), (hx - pxv * 1.2, hy - pyv * 1.2)], 10)
        t.poly([(hx, hy), (ex, ey), (ex - pxv * 5, ey - pyv * 5), (hx - pxv * 1.2, hy - pyv * 1.2)], 9)
        t.linje(int(round(hx + pxv)), int(round(hy + pyv)), int(round(ex + pxv * 4)), int(round(ey + pyv * 4)), 11)
        t.linje(int(round(ex + pxv * 5)), int(round(ey + pyv * 5)), int(round(ex - pxv * 5)), int(round(ey - pyv * 5)), 11)
        t.linje(int(round(ex - dx + pxv * 4)), int(round(ey - dy + pyv * 4)),
                int(round(ex - dx - pxv * 4)), int(round(ey - dy - pyv * 4)), 6)
        t.rekt(hx - 2, hy - 1, hx + 2, hy + 2, 15)
        kontur(d, t)
    d.radial(72, 60, 26, 0.3, mask=(XX > 50) & (XX < 100) & (YY > 30) & (YY < 100) & (d.a < 11))

    # Glödlamporna speglas i de våta plankorna
    for (bx, by) in bulbs:
        if by > 60:
            ry = 96 + (96 - by) // 3
            if ry < H:
                d.px(bx, ry, 9)
    spegel(d, 40, 52, 0.35, 99)
    spegel(d, 140, 152, 0.35, 99)
    spegel(d, 160, 186, 0.3, 101)
    d.vinjett(0.4)
    return d


# ======================================================================
#  INNE PÅ NÖJESPIREN
# ======================================================================
def hast(d, x, y, c=15, sadel=13):
    """Karusellhäst 12 x 8 px, tittar åt höger."""
    t = Duk(16)
    rader = ["........cc..", ".......cccm.", ".cc..sscccc.", "ccccccccc...",
             ".ccccccc....", ".c.c..c.c...", ".c..c.c..c..", "............"]
    sprite(t, x, y, rader, {"c": c, "s": sadel, "m": 0})
    t.px(x + 9, y + 1, 0)
    kontur(d, t, 0)


def nojespir(v=None):
    v = v or {}
    hjul = v.get("hjul", 0)          # pariserhjulets vridning 0..3
    kar = v.get("karusell", 0)       # karusellhästarna 0..3
    lampor = v.get("lampor", 0)      # ljusslingorna 0..1
    snark = v.get("snark", 0)        # Macks snarkningar 0..2
    rnd = random.Random(5301)
    d = Duk(1)

    # --- Himmel ---
    d.vgrad(0, 0, W, 80, [0, 0, 1, 1, 2, 2])
    for _ in range(24):
        sx, sy = rnd.randint(0, W - 1), rnd.randint(0, 36)
        d.px(sx, sy, rnd.choice([3, 4, 5]))
    d.radial(96, 80, 90, 0.3, mask=YY < 96)

    # --- Pariserhjulet ---
    with d.yta("pariserhjul"):
        hx, hy, hr = 40, 37, 29
        for (xa, xb) in ((20, 24), (56, 60)):
            d.linje(hx, hy, xa, 96, 3)
            d.linje(hx, hy, xa + 1, 96, 4)
            d.linje(hx, hy, xb, 96, 3)
        d.linje(24, 74, 56, 74, 3)
        off = hjul * (math.pi / 4) / 4
        for i in range(8):
            a = off + i * math.pi / 4
            d.linje(hx, hy, int(round(hx + hr * math.cos(a))), int(round(hy + hr * math.sin(a))), 3)
        for rr, c in ((hr, 4), (hr - 1, 3), (hr - 9, 3)):
            m = d.mask_ellips(hx - rr, hy - rr, hx + rr, hy + rr) & ~d.mask_ellips(hx - rr + 1, hy - rr + 1, hx + rr - 1, hy + rr - 1)
            d.a[m] = c
        for i in range(24):
            a = off + i * math.pi / 12
            d.px(int(round(hx + hr * math.cos(a))), int(round(hy + hr * math.sin(a))),
                 [11, 14, 10, 13][(i + lampor) % 4] if i % 2 == 0 else 4)
        fyll(d, hx - 3, hy - 3, hx + 3, hy + 3, 4)
        d.px(hx, hy, 11)
        for i in range(8):
            a = off + i * math.pi / 4
            gx, gy = int(round(hx + hr * math.cos(a))), int(round(hy + hr * math.sin(a)))
            c = [13, 12, 10, 14][i % 4]
            d.rekt(gx, gy, gx + 1, gy + 3, 0)
            d.rekt(gx - 3, gy + 3, gx + 4, gy + 4, c)
            d.rekt(gx - 3, gy + 4, gx + 4, gy + 8, LJUSARE[c] if c != 14 else 15)
            d.rekt(gx - 2, gy + 4, gx + 3, gy + 6, 0)
            d.rekt(gx - 3, gy + 8, gx + 4, gy + 9, MORKARE[c])
    d.markera("pariserhjul", 12, 8, 69, 68)
    d.radial(40, 37, 36, 0.25, mask=(d.a < 6) & (YY < 70))

    # --- Bryggan ---
    planka_golv(d, 96, 7, 6, 4, 5302)
    d.vgrad(0, 96, W, 101, [0, 6])
    d.ljus(d.mask_poly([(0, 96), (W, 96), (W, H), (0, H)]), 0.35, MORKARE)
    d.rekt(62, 84, 192, 96, 2)
    d.vgrad(62, 84, 192, 96, [1, 2])

    # --- Spöktåget (utgång in) ---
    with d.yta("utgang:in"):
        fx0, fx1 = 68, 132
        d.rekt(fx0, 30, fx1, 98, 2)
        d.vgrad(fx0, 30, fx1, 98, [1, 2, 1])
        for x in range(fx0, fx1, 8):              # tornspiror
            d.rekt(x, 24, x + 5, 30, 1)
            d.poly([(x - 1, 24), (x + 6, 24), (x + 2, 18)], 1)
        d.rekt(fx0, 30, fx1, 31, 3)
        for x in range(fx0 + 3, fx1, 9):          # slemmiga droppar
            n = rnd.randint(3, 9)
            d.rekt(x, 31, x + 2, 31 + n, 12)
            d.px(x, 31 + n, 12)
        # Skylten
        d.rekt(fx0 + 6, 32, fx1 - 6, 45, 13)
        d.rekt(fx0 + 7, 33, fx1 - 7, 44, 0)
        tx = 100 - bredd("SPÖKTÅGET") // 2
        skriv(d, tx, 38, "SPÖKTÅGET", 14)
        d.px(tx + 1, 43, 14)
        d.px(tx + 17, 43, 14)
        d.px(tx + 30, 43, 14)
        # Den målade dödskallen
        d.a[d.mask_ellips(88, 46, 112, 66)] = 15
        d.rekt(92, 60, 108, 70, 15)
        d.ljus(d.mask_ellips(88, 46, 112, 66) & (XX > 104), 0.6, MORKARE)
        fyll(d, 91, 53, 98, 60, 0)
        fyll(d, 102, 53, 109, 60, 0)
        d.px(94, 56, 13)
        d.px(105, 56, 13)
        d.poly([(100, 60), (98, 64), (102, 64)], 0)
        d.rekt(93, 66, 107, 70, 0)
        for x in range(94, 107, 2):
            d.rekt(x, 66, x + 1, 69, 15)
        d.linje(108, 48, 104, 52, 3)              # spricka
        for (bx, by) in ((76, 52), (120, 56)):    # fladdermöss på fasaden
            d.poly([(bx - 6, by), (bx - 2, by + 1), (bx, by + 3), (bx + 2, by + 1), (bx + 6, by),
                    (bx + 3, by + 3), (bx, by + 5), (bx - 3, by + 3)], 0)
            d.px(bx - 1, by + 2, 13)
            d.px(bx + 1, by + 2, 13)
        # Pendeldörrarna
        d.rekt(84, 72, 116, 98, 0)
        d.rekt(86, 74, 99, 98, 6)
        d.rekt(101, 74, 114, 98, 6)
        for x0 in (86, 101):
            d.rekt(x0, 74, x0 + 13, 75, 7)
            d.linje(x0 + 3, 78, x0 + 9, 86, 13)
            d.linje(x0 + 9, 86, x0 + 4, 88, 13)
            d.linje(x0 + 4, 88, x0 + 10, 96, 13)
        d.rekt(99, 74, 101, 98, 0)
        d.ljus(d.mask_poly([(86, 74), (114, 74), (114, 98), (86, 98)]), 0.4, MORKARE)
        # Rälsen ut på bryggan
        for (xa, xb) in ((88, 80), (111, 119)):
            d.linje(xa, 98, xb, H - 1, 4)
            d.linje(xa + 1, 98, xb + 1, H - 1, 5)
        for y in range(100, H, 4):
            t = (y - 98) / (H - 98)
            d.rekt(int(88 - 8 * t), y, int(113 + 8 * t), y + 1, 6)
    d.markera("utgang:in", 84, 46, 116, 98)
    d.radial(100, 58, 30, 0.3, mask=(XX >= 68) & (XX < 132) & (YY < 98) & (d.a < 15))

    # --- Skjutbanan ---
    with d.yta("skjutbana"):
        sx0, sx1 = 138, 190
        for gx in (sx0, sx1 - 3):
            d.rekt(gx, 40, gx + 3, 98, 6)
            d.rekt(gx, 40, gx + 1, 98, 8)
        d.rekt(sx0 + 3, 50, sx1 - 3, 84, 1)
        d.vgrad(sx0 + 3, 50, sx1 - 3, 84, [6, 1, 0])
        # Plåtankor på en skena
        d.rekt(sx0 + 3, 63, sx1 - 3, 64, 4)
        for i, ax in enumerate(range(sx0 + 6, sx1 - 8, 9)):
            d.rekt(ax, 58, ax + 6, 62, 10)
            d.rekt(ax + 4, 55, ax + 7, 59, 10)
            d.px(ax + 7, 57, 13)
            d.px(ax + 8, 57, 13)
            d.px(ax + 5, 56, 0)
            d.rekt(ax + 1, 58, ax + 4, 59, 9)
            d.rekt(ax, 61, ax + 6, 62, 9)
            if i == 2:                              # en anka som redan är nerskjuten
                d.rekt(ax, 55, ax + 9, 63, 1)
                d.rekt(ax, 61, ax + 7, 63, 9)
        # Måltavlor
        for tx_ in range(sx0 + 8, sx1 - 6, 12):
            fyll(d, tx_ - 4, 67, tx_ + 4, 75, 15)
            fyll(d, tx_ - 2, 69, tx_ + 2, 73, 13)
            d.px(tx_, 71, 15)
        # Priser: nallar i taket
        for (nx, c) in ((sx0 + 6, 8), (sx1 - 11, 14)):
            d.rekt(nx + 2, 50, nx + 3, 52, 0)
            fyll(d, nx, 52, nx + 5, 57, c)
            fyll(d, nx - 1, 56, nx + 6, 63, c)
            d.px(nx, 52, c)
            d.px(nx + 5, 52, c)
            d.px(nx + 2, 54, 0)
            d.px(nx + 4, 54, 0)
        # Disken med geväret
        d.rekt(sx0, 82, sx1, 98, 8)
        d.rekt(sx0, 82, sx1, 84, 9)
        for x in range(sx0, sx1, 7):
            d.rekt(x, 85, x + 1, 98, 7)
        d.rekt(sx0 + 4, 80, sx0 + 26, 81, 0)
        d.rekt(sx0 + 18, 80, sx0 + 28, 83, 7)
        d.rekt(sx0 + 8, 81, sx0 + 10, 83, 0)
        d.rekt(sx0 + 4, 86, sx0 + 22, 93, 13)
        skriv(d, sx0 + 6, 87, "WIN!", 11)
        d.rekt(sx0 + 28, 86, sx0 + 42, 93, 15)
        skriv(d, sx0 + 31, 87, "5C", 13)
        # Markis och skylt
        for i, x in enumerate(range(sx0 - 2, sx1 + 2, 4)):
            c = 13 if i % 2 == 0 else 10
            d.rekt(x, 42, x + 4, 50, c)
            fyll(d, x, 48, x + 3, 53, c)
        d.rekt(sx0 - 2, 41, sx1 + 2, 42, 11)
        d.rekt(sx0 + 2, 30, sx1 - 2, 40, 0)
        d.rekt(sx0 + 3, 31, sx1 - 3, 39, 12)
        skriv(d, 164 - bredd("SKJUTBANA") // 2, 33, "SKJUTBANA", 11)
        for x in range(sx0 - 1, sx1 + 2, 4):
            glodlampa(d, x, 41, (x // 4 + lampor) % 2 == 0)
    d.radial(164, 66, 30, 0.45, mask=(XX > 140) & (XX < 188) & (YY > 50) & (YY < 84) & (d.a < 10))

    # --- Mack som sover på sin pall, med skylten STÄNGT ---
    with d.yta("mack"):
        t = Duk(16)
        # Skylten på en krok på fasaden
        t.linje(116, 46, 122, 42, 4)
        t.linje(128, 46, 122, 42, 4)
        t.px(122, 41, 10)
        t.rekt(108, 46, 136, 56, 15)
        t.rekt(109, 47, 135, 55, 13)
        kontur(d, t)
        skriv(d, 122 - bredd("STÄNGT") // 2, 50, "STÄNGT", 15)
        t = Duk(16)
        mx = 116
        # Pallen
        t.rekt(mx + 1, 90, mx + 17, 92, 8)
        t.rekt(mx + 1, 90, mx + 17, 91, 9)
        t.linje(mx + 3, 92, mx + 1, 101, 8)
        t.linje(mx + 15, 92, mx + 17, 101, 8)
        t.rekt(mx + 4, 96, mx + 15, 97, 7)
        # Ben och skor
        t.rekt(mx + 2, 84, mx + 14, 90, 4)
        t.rekt(mx - 2, 86, mx + 4, 99, 4)
        t.rekt(mx - 2, 86, mx - 1, 99, 5)
        t.rekt(mx - 5, 98, mx + 4, 101, 0)
        t.rekt(mx + 6, 88, mx + 11, 99, 3)
        t.rekt(mx + 6, 98, mx + 13, 101, 0)
        # Kroppen: sliten röd kavaj, hopsjunken
        t.rekt(mx + 3, 71, mx + 18, 88, 13)
        t.rekt(mx + 3, 71, mx + 5, 88, 14)
        t.rekt(mx + 16, 71, mx + 18, 88, 6)
        t.rekt(mx + 9, 73, mx + 12, 86, 15)
        t.px(mx + 13, 76, 10)
        t.px(mx + 13, 80, 10)
        t.rekt(mx + 12, 80, mx + 14, 82, 7)        # lapp på armbågen
        t.rekt(mx + 2, 82, mx + 10, 86, 13)
        t.rekt(mx, 82, mx + 4, 86, 10)             # händer i knät
        # Huvudet hänger framåt
        t.rekt(mx + 4, 62, mx + 15, 73, 10)
        t.rekt(mx + 4, 62, mx + 5, 73, 9)
        t.rekt(mx + 2, 64, mx + 4, 70, 15)         # vita hårtestar
        t.rekt(mx + 15, 64, mx + 17, 70, 15)
        t.rekt(mx + 5, 70, mx + 15, 74, 15)        # vitt skägg
        t.rekt(mx + 6, 66, mx + 9, 67, 0)          # slutna ögon
        t.rekt(mx + 11, 66, mx + 14, 67, 0)
        t.rekt(mx + 6, 64, mx + 9, 65, 15)         # yviga bryn
        t.rekt(mx + 11, 64, mx + 14, 65, 15)
        t.rekt(mx + 9, 67, mx + 11, 70, 14)        # röd näsa
        t.rekt(mx + 8, 71, mx + 12, 73, 0)         # öppen mun
        t.rekt(mx + 3, 58, mx + 16, 62, 4)         # skärmmössa
        t.rekt(mx + 3, 58, mx + 16, 59, 5)
        t.rekt(mx + 2, 61, mx + 17, 63, 1)
        t.rekt(mx + 8, 59, mx + 11, 61, 10)        # mössmärke
        kontur(d, t)
        # Zzz
        zx, zy = mx + 17 + snark, 62 - snark * 2
        for k, (ox, oy) in enumerate(((0, 0), (5, -6))):
            sz = 3 + k
            x0, y0 = zx + ox, zy + oy
            d.rekt(x0, y0, x0 + sz, y0 + 1, 15)
            d.linje(x0 + sz - 1, y0 + 1, x0, y0 + sz - 1, 15)
            d.rekt(x0, y0 + sz - 1, x0 + sz, y0 + sz, 15)
    d.markera("mack", 108, 42, 136, 102)

    # --- Karusellen ---
    with d.yta("karusell"):
        cx = 32
        d.a[d.mask_ellips(2, 94, 62, 106)] = 6
        d.a[d.mask_ellips(2, 92, 62, 103)] = 8
        d.a[d.mask_ellips(4, 93, 60, 101)] = 7
        d.rekt(cx - 1, 72, cx + 2, 98, 10)
        d.rekt(cx - 1, 72, cx, 98, 11)
        # Inre trumma med speglar
        d.rekt(cx - 7, 76, cx + 8, 92, 13)
        for x in range(cx - 6, cx + 8, 4):
            d.rekt(x, 78, x + 2, 90, 5)
            d.px(x, 79, 15)
        # Hästar på stänger
        for i, hx_ in enumerate((5, 18, 36, 49)):
            upp = [0, 1, 2, 1][(kar + i * 2) % 4]
            hy_ = 84 - upp * 2 + (2 if i in (1, 2) else 0)
            d.rekt(hx_ + 5, 72, hx_ + 6, 98, 10)
            hast(d, hx_, hy_, [15, 9, 15, 5][i], [13, 12, 14, 13][i])
        # Taket
        d.poly([(0, 74), (cx, 54), (64, 74)], 13)
        for k in range(8):
            d.poly([(k * 8, 74), (cx, 54), (k * 8 + 4, 74)], 15)
        d.rekt(0, 73, 64, 76, 10)
        for i, x in enumerate(range(0, 64, 4)):
            fyll(d, x, 75, x + 4, 79, 13 if i % 2 == 0 else 15)
            glodlampa(d, x + 2, 74, (i + lampor) % 2 == 0)
        d.rekt(cx - 1, 50, cx + 2, 54, 10)
        d.poly([(cx + 1, 46), (cx + 7, 48), (cx + 1, 50)], 14)    # flagga
        d.rekt(cx, 46, cx + 1, 54, 0)
    d.radial(32, 86, 30, 0.4, mask=(XX < 64) & (YY > 74) & (YY < 104) & (d.a < 11))

    # --- Ljusslingor över piren ---
    for (xa, ya, xb, yb) in ((60, 14, 130, 20), (130, 20, 192, 10)):
        n = int(abs(xb - xa))
        for k in range(n):
            t_ = k / n
            x = int(xa + (xb - xa) * t_)
            y = int(ya + (yb - ya) * t_ + 6 * math.sin(t_ * math.pi))
            d.px(x, y, 0)
            if k % 4 == 0:
                c = [13, 10, 14, 12, 11][(k // 4) % 5]
                d.px(x, y + 1, c if (k // 4 + lampor) % 2 == 0 else MORKARE[c])

    # --- Utgången tillbaka genom grinden ---
    with d.yta("utgang:ut"):
        gx0, gx1 = 140, 190
        d.rekt(gx0, 110, gx1, 112, 5)
        d.rekt(gx0, 116, gx1, 118, 4)
        for x in range(gx0, gx1 + 1, 8):
            d.rekt(x, 108, x + 2, H, 4)
            d.rekt(x, 108, x + 1, H, 5)
        d.rekt(160, 112, 170, H, 3)
        d.rekt(160, 112, 161, H, 5)
        d.rekt(158, 110, 172, 113, 4)
        d.rekt(150, 116, 160, 118, 15)
        d.rekt(170, 116, 180, 118, 15)
        textskylt(d, 165, 99, "UTGÅNG v", 12, 15, 15)
    d.markera("utgang:ut", 140, 98, 191, H)

    spegel(d, 4, 60, 0.3, 104)
    spegel(d, 140, 188, 0.25, 104)
    d.vinjett(0.4)
    return d


# ======================================================================
#  INNE I SPÖKTÅGETS TUNNEL
# ======================================================================
def pappspoke(d, x, y, c=15):
    """Ett spöke i papp, 14 x 18 px, hänger i ett snöre från taket."""
    t = Duk(16)
    t.a[t.mask_ellips(x, y, x + 13, y + 12)] = c
    t.rekt(x, y + 6, x + 14, y + 15, c)
    for k in range(4):
        fyll(t, x + k * 4 - 1, y + 13, x + k * 4 + 2, y + 17, c)
        t.rekt(x + k * 4 + 2, y + 15, x + k * 4 + 3, y + 18, 16)
    t.rekt(x + 3, y + 5, x + 6, y + 9, 0)
    t.rekt(x + 8, y + 5, x + 11, y + 9, 0)
    t.a[t.mask_ellips(x + 5, y + 10, x + 9, y + 14)] = 0
    t.rekt(x + 1, y + 4, x + 2, y + 12, 5)
    t.rekt(x - 3, y + 8, x, y + 10, c)              # viftande armar
    t.rekt(x + 14, y + 7, x + 17, y + 9, c)
    kontur(d, t)


def fladdermus(d, x, y, upp=False):
    """Fladdermus 13 x 6 px."""
    if upp:
        d.poly([(x, y), (x + 4, y + 3), (x + 6, y + 2), (x + 8, y + 3), (x + 12, y), (x + 10, y + 5), (x + 6, y + 4), (x + 2, y + 5)], 0)
    else:
        d.poly([(x, y + 4), (x + 4, y + 2), (x + 6, y + 1), (x + 8, y + 2), (x + 12, y + 4), (x + 9, y + 3), (x + 6, y + 5), (x + 3, y + 3)], 0)
    d.rekt(x + 5, y, x + 8, y + 3, 0)
    d.px(x + 5, y + 1, 13)
    d.px(x + 7, y + 1, 13)


def hangande_fladdermus(d, x, y):
    """Fladdermus som hänger upp och ner i taket."""
    d.rekt(x, y, x + 1, y + 1, 0)
    d.rekt(x + 3, y, x + 4, y + 1, 0)
    d.a[d.mask_ellips(x - 2, y + 1, x + 6, y + 10)] = 0
    d.rekt(x - 1, y + 9, x + 5, y + 12, 0)
    d.px(x, y + 10, 13)
    d.px(x + 3, y + 10, 13)
    d.px(x - 1, y + 12, 0)
    d.px(x + 4, y + 12, 0)


def spoktag(v=None):
    v = v or {}
    pa = v.get("kalsonger", True)                    # kalsongerna hänger på skelettet
    darr = [(0, 0), (1, 0), (0, 1), (-1, 0), (0, 0), (1, 1)][v.get("ljus", 0)]
    gung = [0, 1, 2, 1, 0, -1, -2, -1][v.get("spoke", 0)]
    rnd = random.Random(5401)
    d = Duk(0)

    # --- Tunneln i perspektiv ---
    bx0, by0, bx1, by1 = 84, 32, 120, 68              # tunnelns mörka bortre ände
    d.poly([(0, 0), (W, 0), (bx1, by0), (bx0, by0)], 1)             # tak
    d.poly([(0, 0), (bx0, by0), (bx0, by1), (0, 112)], 6)           # vänster vägg
    d.poly([(W, 0), (bx1, by0), (bx1, by1), (W, 112)], 6)           # höger vägg
    d.poly([(0, 112), (bx0, by1), (bx1, by1), (W, 112), (W, H), (0, H)], 1)   # golv
    # Plankor på väggarna
    for k in range(1, 12):
        t = k / 12
        for (x0, x1) in ((0, bx0), (W, bx1)):
            x = int(x0 + (x1 - x0) * t)
            ytop = int(0 + by0 * t)
            ybot = int(112 + (by1 - 112) * t)
            d.linje(x, ytop, x, ybot, 0 if k % 3 else 7)
    for k in range(1, 9):
        f = k / 9
        d.linje(0, int(112 * f), bx0, int(by0 + (by1 - by0) * f), 7)
        d.linje(W - 1, int(112 * f), bx1, int(by0 + (by1 - by0) * f), 7)
    # Takbjälkar
    for t in (0.0, 0.35, 0.65):
        xa = int(0 + bx0 * t)
        xb = int(W + (bx1 - W) * t)
        ya = int(by0 * t)
        d.rekt(xa, ya, xb, ya + max(1, int(5 * (1 - t))), 7)
        d.rekt(xa, ya, xb, ya + 1, 8)
    d.rekt(bx0, by0, bx1, by1, 0)
    # Spindelväv i hörnen
    for (cx, cy, sx, sy) in ((0, 0, 1, 1), (W - 1, 0, -1, 1)):
        for k in range(5):
            a = k * math.pi / 8
            d.linje(cx, cy, int(cx + sx * 26 * math.cos(a)), int(cy + sy * 26 * math.sin(a)), 4)
        for r in (8, 15, 22):
            for k in range(4):
                a0, a1 = k * math.pi / 8, (k + 1) * math.pi / 8
                d.linje(int(cx + sx * r * math.cos(a0)), int(cy + sy * r * math.sin(a0)),
                        int(cx + sx * r * math.cos(a1)), int(cy + sy * r * math.sin(a1)), 4)
    # Rälsen
    for y in range(by1 + 2, H, 1):
        t = (y - by1) / (H - by1)
        if int(t * 30) % 3 == 0:
            d.rekt(int(96 - 4 - 34 * t), y, int(108 + 4 + 34 * t), y + 1, 6)
    for (xa, xb) in ((97, 66), (107, 140)):
        d.linje(xa, by1, xb, H - 1, 4)
        d.linje(xa + (1 if xb > xa else -1), by1, xb + (2 if xb > xa else -2), H - 1, 3)
    for _ in range(30):
        d.px(rnd.randint(0, W - 1), rnd.randint(100, H - 1), rnd.choice([2, 6]))

    # --- Dörrarna tillbaka ut ---
    with d.yta("utgang:ut"):
        d.poly([(4, 38), (30, 44), (30, 98), (4, 104)], 7)
        d.poly([(6, 40), (16, 42), (16, 101), (6, 102)], 6)
        d.poly([(18, 42), (28, 45), (28, 97), (18, 100)], 6)
        d.linje(17, 42, 17, 100, 11)                     # ljusspringa
        d.linje(6, 103, 28, 98, 10)
        d.linje(9, 60, 13, 68, 13)
        d.linje(21, 62, 25, 70, 13)
        d.rekt(6, 26, 26, 35, 0)
        d.rekt(7, 27, 25, 34, 12)
        skriv(d, 12, 29, "UT", 15)
        d.rekt(15, 35, 16, 39, 0)

    # --- Den lilla vagnen ---
    with d.yta("spoktagvagn"):
        vx0, vx1 = 80, 124
        d.rekt(vx0 + 4, 70, vx1 - 4, 80, 13)           # ryggstöd
        d.rekt(vx0 + 4, 70, vx1 - 4, 71, 14)
        d.rekt(vx0, 78, vx1, 98, 13)
        d.rekt(vx0, 78, vx1, 80, 14)
        d.rekt(vx0, 78, vx0 + 2, 98, 14)
        d.rekt(vx1 - 2, 78, vx1, 98, 6)
        d.rekt(vx0, 96, vx1, 98, 10)
        # Djävulsansikte på fronten
        d.poly([(vx0 + 6, 80), (vx0 + 10, 84), (vx0 + 8, 84)], 10)
        d.poly([(vx1 - 6, 80), (vx1 - 10, 84), (vx1 - 8, 84)], 10)
        d.poly([(vx0 + 12, 84), (vx0 + 19, 86), (vx0 + 12, 88)], 11)
        d.poly([(vx1 - 12, 84), (vx1 - 19, 86), (vx1 - 12, 88)], 11)
        d.px(vx0 + 14, 86, 0)
        d.px(vx1 - 15, 86, 0)
        d.rekt(vx0 + 12, 90, vx1 - 12, 94, 0)
        for x in range(vx0 + 13, vx1 - 12, 3):
            d.poly([(x, 90), (x + 2, 90), (x + 1, 92)], 15)
        for wx in (vx0 + 3, vx1 - 9):
            d.rekt(wx, 98, wx + 6, 103, 0)
            d.rekt(wx + 1, 99, wx + 5, 102, 3)
        d.rekt(vx0 + 6, 66, vx0 + 9, 70, 7)            # säkerhetsbygel
        d.rekt(vx1 - 9, 66, vx1 - 6, 70, 7)
        d.rekt(vx0 + 6, 66, vx1 - 6, 68, 4)

    # --- Skelettet på stolen ---
    with d.yta("skelett"):
        t = Duk(16)
        sx = 140
        # Stolen
        t.rekt(sx + 16, 40, sx + 20, 98, 7)
        t.rekt(sx + 16, 40, sx + 17, 98, 8)
        t.rekt(sx + 14, 38, sx + 22, 41, 8)
        t.rekt(sx - 4, 80, sx + 20, 83, 8)
        t.rekt(sx - 4, 80, sx + 20, 81, 9)
        t.rekt(sx - 3, 83, sx - 1, 102, 7)
        t.rekt(sx + 8, 83, sx + 10, 100, 6)
        t.rekt(sx + 17, 83, sx + 19, 98, 7)
        # Bäcken och lårben
        t.rekt(sx + 2, 74, sx + 14, 80, 15)
        t.rekt(sx + 5, 76, sx + 7, 78, 0)
        t.rekt(sx + 10, 76, sx + 12, 78, 0)
        for ky in (76, 79):
            t.rekt(sx - 10, ky, sx + 4, ky + 2, 15)
            t.rekt(sx - 12, ky - 1, sx - 9, ky + 3, 15)
        # Underben och fötter
        for (lx, f) in ((sx - 12, 0), (sx - 7, 1)):
            t.rekt(lx, 80, lx + 2, 100 - f, 15)
            t.rekt(lx - 4, 100 - f, lx + 2, 102 - f, 15)
            t.px(lx - 4, 100 - f, 5)
        # Ryggrad och revben
        t.rekt(sx + 7, 52, sx + 9, 74, 5)
        for k, y in enumerate(range(54, 71, 3)):
            w = 9 - abs(k - 2)
            t.rekt(sx + 8 - w, y, sx + 9 + w, y + 1, 15)
            t.px(sx + 8 - w, y + 1, 15)
            t.px(sx + 8 + w, y + 1, 15)
        t.rekt(sx, 52, sx + 17, 54, 15)                # nyckelben
        # Armar som hänger, ena handen på knät
        t.linje(sx, 53, sx - 4, 66, 15)
        t.linje(sx - 4, 66, sx - 8, 76, 15)
        t.rekt(sx - 10, 74, sx - 6, 77, 15)
        t.linje(sx + 17, 53, sx + 19, 66, 15)
        t.linje(sx + 19, 66, sx + 18, 78, 15)
        t.rekt(sx + 17, 78, sx + 20, 82, 15)
        # Skallen, lite på sne
        t.rekt(sx + 6, 47, sx + 10, 52, 5)
        t.a[t.mask_ellips(sx + 1, 32, sx + 16, 46)] = 15
        t.rekt(sx + 3, 42, sx + 13, 48, 15)
        t.a[t.mask_ellips(sx + 3, 37, sx + 7, 42)] = 0
        t.a[t.mask_ellips(sx + 9, 37, sx + 13, 42)] = 0
        t.px(sx + 5, 39, 13)
        t.px(sx + 11, 39, 13)
        t.rekt(sx + 7, 42, sx + 9, 44, 0)
        t.rekt(sx + 4, 46, sx + 13, 47, 0)
        for x in range(sx + 4, sx + 13, 2):
            t.px(x, 47, 0)
        t.rekt(sx + 4, 47, sx + 13, 49, 15)
        t.px(sx + 13, 35, 5)
        t.px(sx + 12, 34, 5)
        # Hatt: en gammal kubb
        t.rekt(sx + 3, 27, sx + 14, 33, 2)
        t.rekt(sx, 32, sx + 17, 34, 2)
        t.rekt(sx + 3, 31, sx + 14, 32, 13)
        kontur(d, t)

    # --- De röda långkalsongerna över axlarna ---
    if pa:
        with d.yta("kalsonger"):
            t = Duk(16)
            # Över axlarna och bakom nacken
            t.rekt(sx - 9, 50, sx + 21, 54, 13)
            t.rekt(sx - 9, 50, sx + 21, 51, 14)
            t.rekt(sx - 8, 52, sx - 2, 57, 6)          # bakluckan
            t.rekt(sx - 7, 52, sx - 3, 56, 13)
            t.px(sx - 7, 53, 15)
            t.px(sx - 4, 53, 15)
            # Vänster sida: två ben som dinglar, med muddar
            for (lx, lang) in ((sx - 11, 90), (sx - 4, 84)):
                t.rekt(lx, 52, lx + 5, lang, 13)
                t.rekt(lx, 52, lx + 1, lang, 14)
                t.rekt(lx + 4, 54, lx + 5, lang, 6)
                t.rekt(lx - 1, lang - 3, lx + 6, lang, 14)
                t.rekt(lx - 1, lang - 2, lx + 6, lang - 1, 15)
            t.rekt(sx - 9, 66, sx - 7, 68, 6)          # lagning på knät
            # Höger sida: kroppen med knappslå, och en ärm
            t.rekt(sx + 16, 52, sx + 24, 78, 13)
            t.rekt(sx + 16, 52, sx + 17, 78, 14)
            t.rekt(sx + 20, 54, sx + 21, 76, 6)
            for y in range(56, 76, 4):
                t.px(sx + 22, y, 15)
            t.rekt(sx + 15, 76, sx + 25, 79, 14)
            t.rekt(sx + 25, 53, sx + 29, 72, 13)
            t.rekt(sx + 28, 53, sx + 29, 72, 6)
            t.rekt(sx + 24, 71, sx + 30, 74, 14)
            kontur(d, t)
        d.markera("kalsonger", sx - 13, 48, sx + 31, 91)

    # --- Spöken och fladdermöss i taket ---
    fore = d.a.copy()
    with d.yta("spoken"):
        for (gx, gy, langd, sv) in ((58, 0, 14, 0), (100, 0, 6, 1), (162, 0, 18, 0)):
            dx = gung if sv else 0
            d.linje(gx + 6, gy, gx + 6 + dx, gy + langd, 5)
            pappspoke(d, gx + dx, gy + langd, 15)
        hangande_fladdermus(d, 32, 2)
        hangande_fladdermus(d, 42, 4)
        hangande_fladdermus(d, 134, 3)
        fladdermus(d, 120, 16, upp=False)
    spokmask = (d.a != fore) & (d.a == 15)
    d.markera("spoken", 30, 0, 50, 17)

    # --- Mörker och ficklampans ljuskägla ---
    cx, cy = 132 + darr[0], 60 + darr[1]
    avst = np.sqrt(((XX - cx) / 58.0) ** 2 + ((YY - cy) / 46.0) ** 2)
    d.ljus(np.ones((H, W), bool), np.clip((avst - 0.75) / 0.45, 0, 1) * 0.9, MORKARE)
    d.ljus(np.ones((H, W), bool), np.clip((avst - 1.05) / 0.5, 0, 1) * 0.8, MORKARE)
    d.ljus((avst < 0.55) & (d.a != 13), np.clip(0.55 - avst, 0, 1) * 0.6, LJUSARE)
    ring = (avst > 0.68) & (avst < 0.78) & (d.a != 13)
    d.ljus(ring, 0.25, LJUSARE)
    d.a[spokmask] = np.where(TROSKEL[spokmask] < 0.7, 15, 5)
    # Dörrarna i mörkret, med ljus från springan och skylten
    d.poly([(4, 38), (30, 44), (30, 98), (4, 104)], 1)
    d.poly([(6, 40), (16, 42), (16, 101), (6, 102)], 2)
    d.poly([(18, 42), (28, 45), (28, 97), (18, 100)], 2)
    d.linje(15, 42, 15, 101, 3)
    d.linje(19, 43, 19, 99, 3)
    d.linje(9, 60, 13, 68, 6)
    d.linje(21, 62, 25, 70, 6)
    d.radial(16, 30, 20, 0.6, mask=(XX < 36))
    d.radial(17, 104, 26, 0.5, mask=(XX < 44) & (YY > 98))
    d.linje(16, 42, 16, 101, 10)
    d.linje(17, 42, 17, 100, 11)
    d.linje(6, 103, 28, 98, 10)
    d.rekt(7, 27, 25, 34, 12)
    skriv(d, 12, 29, "UT", 15)
    d.vinjett(0.3)
    return d


SCENER_E = {
    "fiskmarknad": (fiskmarknad, [
        ("masar", "masar", [(0, 900), (1, 400), (2, 220), (3, 260), (1, 700), (4, 180), (0, 600)]),
        ("lampor", "lampor", [(0, 500), (1, 500), (2, 500), (3, 500)]),
    ]),
    "nojespir_entre": (nojespir_entre, [
        ("lampor", "lampor", [(0, 220), (1, 220), (2, 220)]),
        ("vift", "vift", [(0, 900), (1, 220), (2, 380), (1, 220), (2, 380), (1, 220), (0, 1500)]),
    ]),
    "nojespir": (nojespir, [
        ("hjul", "hjul", [(0, 260), (1, 260), (2, 260), (3, 260)]),
        ("karusell", "karusell", [(0, 200), (1, 200), (2, 200), (3, 200)]),
        ("lampor", "lampor", [(0, 450), (1, 450)]),
        ("snark", "snark", [(0, 700), (1, 700), (2, 900)]),
    ]),
    "spoktag": (spoktag, [
        ("ljus", "ljus", [(0, 160), (1, 90), (2, 120), (3, 80), (4, 300), (5, 90)]),
        ("spoke", "spoke", [(i, 180) for i in range(8)]),
        ("kalsonger", "kalsonger", [(True, 1000), (False, 1000)], 1),
    ]),
}
