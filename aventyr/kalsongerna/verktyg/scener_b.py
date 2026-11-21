import math, random, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "motor" / "verktyg"))
from pixelbild import *  # noqa

"""Scener B: Hotel Majestics lobby och bar, rådhusets marmorhall och borgmästarens kontor."""

# Egna extratecken (motorns typsnitt saknar dem).
EXTRA = {
    "X": ["101", "101", "010", "101", "101"],
    "J": ["001", "001", "001", "101", "010"],
    "0": ["111", "101", "101", "101", "111"],
    "2": ["110", "001", "010", "100", "111"],
    "4": ["101", "101", "111", "001", "001"],
    "5": ["111", "100", "110", "001", "110"],
    "6": ["011", "100", "111", "101", "111"],
    "7": ["111", "001", "010", "010", "010"],
    "8": ["111", "101", "111", "101", "111"],
    ".": ["0", "0", "0", "0", "1"],
    "Ö": ["101", "010", "101", "101", "010"],
}


def _glyf(ch):
    return EXTRA.get(ch) or TYPSNITT[ch]


def txt(d, x, y, s, c):
    """Som text(), men med extratecknen ovan."""
    for ch in s:
        g = _glyf(ch)
        for ry, rad in enumerate(g):
            for rx, bit in enumerate(rad):
                if bit == "1":
                    d.px(x + rx, y + ry, c)
        x += len(g[0]) + 1


def bredd(s):
    return sum(len(_glyf(ch)[0]) + 1 for ch in s) - 1


def fyll(d, x0, y0, x1, y1, c):
    d.a[d.mask_ellips(x0, y0, x1, y1)] = c


def ring(d, x0, y0, x1, y1, c, tjock=1):
    m = d.mask_ellips(x0, y0, x1, y1) & ~d.mask_ellips(x0 + tjock, y0 + tjock, x1 - tjock, y1 - tjock)
    d.a[m] = c


def rutmask(x0, y0, x1, y1):
    return (XX >= x0) & (XX < x1) & (YY >= y0) & (YY < y1)


def dither(d, mask, c1, c2):
    """Schackrutigt raster av två färger (ger t.ex. lila av rött och blått)."""
    jamn = (XX + YY) % 2 == 0
    d.a[mask & jamn] = c1
    d.a[mask & ~jamn] = c2


def schackgolv(d, y0, c1, c2, skala=1.6, rad_k=260):
    """Rutigt golv i perspektiv från y0 till bildens nederkant."""
    d.rekt(0, y0, W, H, c1)
    for y in range(y0, H):
        z = y - y0 + 10
        rad = int(rad_k / z)
        for x in range(W):
            kol = int((x - W // 2) * skala / z + 100)
            if (kol + rad) % 2:
                d.a[y, x] = c2


class forgrund:
    """Det som ritas i blocket skymmer klickytor bakom sig (t.ex. en disk framför en person)."""
    def __init__(self, d):
        self.d = d

    def __enter__(self):
        self.fore = self.d.a.copy()

    def __exit__(self, *a):
        self.d.ytkarta[self.d.a != self.fore] = 0


def pil_ner(d, cx, y, c):
    for i in range(4):
        d.rekt(cx - 3 + i, y + i, cx + 4 - i, y + i + 1, c)
    d.rekt(cx - 1, y - 3, cx + 2, y, c)


# ======================================================================
#  HOTEL MAJESTIC: LOBBYN
# ======================================================================
def hotell_lobby(v=None):
    v = v or {}
    borta = v.get("borta", False)   # tillstånd: conciergen har gått
    hiss = v.get("hiss", 0)         # våningsvisarens läge 0..5
    palm = v.get("palm", 0)         # palmens svaj 0..3
    rnd = random.Random(1929)
    d = Duk(1)

    # --- Väggen: varmt trä med förgyllda art deco-lister ---
    d.vgrad(0, 0, W, 80, [6, 6, 7, 7])
    for x in range(0, W, 16):
        d.rekt(x + 7, 8, x + 9, 62, 6)
        d.rekt(x + 7, 8, x + 8, 62, 8)
    # Fris upptill med sicksack i guld
    d.rekt(0, 0, W, 8, 0)
    for x in range(0, W, 6):
        d.linje(x, 6, x + 3, 2, 9)
        d.linje(x + 3, 2, x + 6, 6, 9)
    d.rekt(0, 7, W, 8, 10)
    # Sockel i svart marmor med ådror
    d.rekt(0, 62, W, 80, 0)
    d.rekt(0, 62, W, 63, 9)
    for i in range(14):
        x = rnd.randint(0, W - 10)
        d.linje(x, 64 + rnd.randint(0, 8), x + rnd.randint(4, 12), 66 + rnd.randint(0, 12), 2)
    d.rekt(0, 79, W, 80, 9)

    # --- Marmorgolv i schackmönster ---
    schackgolv(d, 80, 15, 2)
    d.ljus(rutmask(0, 80, W, 92), 0.55, MORKARE)
    d.ljus(rutmask(0, 80, W, 86), 0.5, MORKARE)
    # Rund röd matta med kompassros
    fyll(d, 66, 98, 130, 122, 10)
    fyll(d, 68, 99, 128, 121, 13)
    ring(d, 72, 101, 124, 119, 10)
    d.poly([(98, 102), (101, 110), (98, 118), (95, 110)], 10)
    d.poly([(80, 110), (98, 108), (116, 110), (98, 112)], 10)
    d.px(98, 110, 11)

    # --- Vägglampor: solfjädrar i mässing ---
    for lx in (58, 146):
        d.poly([(lx - 4, 26), (lx + 4, 26), (lx + 2, 32), (lx - 2, 32)], 10)
        d.rekt(lx - 1, 32, lx + 1, 36, 9)
        d.rekt(lx - 3, 25, lx + 3, 26, 11)
        d.radial(lx, 26, 26, 0.55, mask=(YY < 80) & (d.a < 10))

    # --- Roterdörren ut mot gatan ---
    with d.yta("utgang:ut"):
        d.rekt(2, 20, 34, 86, 9)
        d.rekt(3, 21, 33, 30, 10)
        d.rekt(4, 22, 32, 29, 0)
        txt(d, 18 - bredd("HOTEL") // 2, 24, "HOTEL", 10)
        # Glaset: gatan utanför i regnet
        d.vgrad(4, 31, 32, 84, [1, 2, 2, 3])
        for i in range(4):
            d.rekt(4 + i * 7, 52 + (i % 2) * 3, 9 + i * 7, 84, 1)
        d.px(26, 48, 10)
        d.radial(26, 49, 6, 0.5)
        r2 = random.Random(5)
        for _ in range(26):
            x, y = r2.randint(5, 31), r2.randint(32, 82)
            d.px(x, y, 4)
            d.px(x, y + 1, 5 if y % 3 else 4)
        # Dörrbladen
        d.rekt(17, 31, 19, 86, 10)
        d.rekt(17, 31, 18, 86, 11)
        d.rekt(8, 31, 9, 84, 9)
        d.rekt(27, 31, 28, 84, 9)
        d.rekt(4, 64, 32, 66, 9)
        d.rekt(9, 58, 17, 59, 11)
        d.rekt(19, 58, 27, 59, 11)
        for i in range(6):
            d.px(6 + i // 2, 33 + i, 5)
            d.px(21 + i // 2, 33 + i, 5)
        # Golvtrumman
        d.poly([(1, 84), (35, 84), (37, 89), (-1, 89)], 9)
        d.rekt(0, 84, 36, 85, 10)
        d.ljus(rutmask(0, 86, 37, 89), 0.4, MORKARE)

    # --- Hylla med nyckelfack bakom disken ---
    d.rekt(66, 9, 118, 19, 0)
    d.rekt(66, 9, 118, 10, 9)
    d.rekt(66, 18, 118, 19, 9)
    txt(d, 92 - bredd("MAJESTIC") // 2, 11, "MAJESTIC", 10)
    d.radial(92, 13, 20, 0.3, mask=rutmask(67, 10, 117, 18) & (d.a == 10))
    d.rekt(68, 22, 116, 52, 6)
    d.rekt(69, 23, 115, 51, 7)
    for ry, y in enumerate(range(24, 50, 6)):
        for rx, x in enumerate(range(70, 114, 5)):
            d.rekt(x, y, x + 4, y + 5, 0)
            if (rx * 3 + ry * 5) % 4:
                d.px(x + 1, y + 1, 10)
                d.px(x + 1, y + 2, 9)
            if (rx + ry * 2) % 5 == 0:
                d.rekt(x + 1, y + 3, x + 4, y + 5, 15)
    d.radial(92, 40, 30, 0.35, mask=rutmask(68, 22, 116, 52))

    # --- Conciergen: spenslig, mittbena och pincené ---
    if not borta:
        with d.yta("concierge"):
            cx = 92
            # Frack och skjortbröst
            d.poly([(cx - 7, 50), (cx + 7, 50), (cx + 8, 66), (cx - 8, 66)], 0)
            d.rekt(cx - 7, 51, cx - 6, 66, 2)
            d.poly([(cx - 3, 50), (cx + 3, 50), (cx + 2, 66), (cx - 2, 66)], 15)
            d.poly([(cx - 3, 50), (cx - 1, 50), (cx, 58)], 2)
            d.poly([(cx + 1, 50), (cx + 3, 50), (cx, 58)], 2)
            d.rekt(cx - 2, 50, cx + 3, 52, 0)
            d.px(cx, 51, 3)
            d.px(cx, 56, 0)
            d.px(cx, 60, 0)
            d.px(cx - 5, 54, 13)          # nejlika i knapphålet
            d.px(cx - 4, 54, 14)
            # Lång smal hals och huvud
            d.rekt(cx - 1, 46, cx + 2, 50, 10)
            d.px(cx - 1, 49, 9)
            fyll(d, cx - 5, 33, cx + 5, 47, 10)
            d.rekt(cx - 5, 33, cx + 6, 37, 0)
            d.px(cx - 5, 38, 0)
            d.px(cx + 5, 38, 0)
            d.rekt(cx, 33, cx + 1, 37, 10)   # mittbenan
            d.px(cx - 3, 34, 3)
            d.px(cx + 3, 34, 3)
            d.px(cx - 6, 40, 9)
            d.px(cx + 6, 40, 9)
            # Pincené och uppdragna ögonbryn
            d.rekt(cx - 4, 38, cx - 1, 39, 0)
            d.rekt(cx + 2, 38, cx + 5, 39, 0)
            ring(d, cx - 4, 39, cx - 1, 42, 11)
            ring(d, cx + 1, 39, cx + 4, 42, 11)
            d.px(cx, 40, 11)
            d.px(cx - 3, 40, 0)
            d.px(cx + 2, 40, 0)
            d.linje(cx + 4, 41, cx + 6, 47, 9)   # kedjan
            d.linje(cx + 6, 47, cx + 5, 53, 9)
            d.px(cx, 43, 9)
            d.rekt(cx - 2, 45, cx + 3, 46, 8)    # tunn mun
            d.px(cx + 3, 44, 8)
            d.radial(cx, 40, 9, 0.3, mask=(d.a == 10))

    # --- Receptionsdisken ---
    fd = forgrund(d)
    fd.__enter__()
    d.rekt(60, 64, 124, 68, 15)
    d.rekt(60, 64, 124, 65, 11)
    d.rekt(60, 67, 124, 68, 9)
    d.rekt(62, 68, 122, 92, 6)
    for x in (62, 120):
        d.rekt(x, 68, x + 2, 92, 9)
    d.rekt(62, 88, 122, 92, 0)
    d.rekt(62, 88, 122, 89, 9)
    # Solfjädersintarsia
    for k in range(-5, 6):
        d.linje(92, 88, 92 + k * 4, 72, 8)
    d.a[d.mask_ellips(84, 80, 100, 96) & (YY < 88)] = 9
    d.a[d.mask_ellips(87, 83, 97, 93) & (YY < 88)] = 10
    for x in (70, 78, 106, 114):
        d.rekt(x, 70, x + 1, 87, 7)
    d.ljus(rutmask(62, 68, 122, 88), 0.35, MORKARE)
    fd.__exit__()

    # --- Gästboken ---
    with d.yta("gastbok"):
        d.poly([(64, 64), (82, 64), (84, 60), (66, 60)], 7)
        d.poly([(65, 63), (73, 63), (74, 59), (67, 59)], 15)
        d.poly([(74, 63), (82, 63), (83, 59), (75, 59)], 15)
        d.linje(74, 63, 74, 59, 9)
        for y in (60, 61, 62):
            d.linje(67, y, 72, y, 4)
            d.linje(76, y, 81, y, 4)
        d.rekt(64, 63, 83, 64, 6)
        # Bläckhorn med gåsfjäder
        d.rekt(84, 61, 87, 64, 0)
        d.px(85, 61, 3)
        d.linje(86, 61, 89, 53, 15)
        d.linje(87, 61, 90, 54, 5)
        d.px(89, 52, 15)

    # --- Ringklockan i mässing ---
    with d.yta("ringklocka"):
        d.rekt(107, 63, 118, 65, 8)
        d.rekt(107, 63, 118, 64, 9)
        fyll(d, 108, 57, 117, 66, 10)
        d.rekt(108, 62, 118, 64, 9)
        d.rekt(107, 63, 118, 64, 8)
        d.rekt(112, 54, 114, 57, 9)
        d.px(112, 54, 11)
        d.px(110, 59, 11)
        d.px(111, 58, 11)
        d.rekt(116, 59, 117, 62, 8)
    d.markera("ringklocka", 106, 53, 119, 66)

    # --- Dörröppningen till baren ---
    with d.yta("utgang:n"):
        d.rekt(126, 34, 144, 80, 9)
        fyll(d, 126, 26, 144, 44, 9)
        d.rekt(128, 36, 142, 80, 0)
        fyll(d, 128, 28, 142, 44, 0)
        # Glimt av baren: rött sken och flaskor
        d.vgrad(128, 44, 142, 80, [0, 1, 6])
        d.rekt(128, 62, 142, 66, 7)
        d.rekt(128, 62, 142, 63, 8)
        for i, x in enumerate(range(130, 141, 3)):
            d.rekt(x, 52 + i % 2, x + 2, 58, [12, 13, 10, 7][i % 4])
        d.rekt(128, 58, 142, 59, 8)
        d.radial(135, 50, 12, 0.5, mask=rutmask(128, 30, 142, 80))
        # Neonskylt BAR
        d.rekt(124, 16, 146, 26, 0)
        d.rekt(124, 16, 146, 17, 13)
        d.rekt(124, 25, 146, 26, 13)
        for i, ch in enumerate("BAR"):
            g = TYPSNITT[ch]
            for ry, rad in enumerate(g):
                for rx, bit in enumerate(rad):
                    if bit == "1":
                        d.px(128 + i * 6 + rx, 19 + ry, 14)
        d.radial(135, 21, 16, 0.4, mask=(YY < 34) & (d.a < 9) & ~rutmask(124, 16, 146, 26))
        d.ljus(rutmask(126, 80, 144, 92), 0.3)

    # --- Hissen med våningsvisare ---
    d.rekt(150, 28, 176, 80, 10)
    d.rekt(151, 29, 175, 80, 9)
    d.rekt(153, 31, 173, 80, 8)
    d.rekt(163, 31, 164, 80, 6)
    for (x0, x1) in ((153, 163), (164, 173)):
        d.rekt(x0 + 1, 33, x1 - 1, 78, 9)
        mx = (x0 + x1) // 2
        for k in range(-2, 3):
            d.linje(mx, 52, mx + k * 2, 36, 8)
        d.rekt(x0 + 1, 52, x1 - 1, 53, 10)
        d.rekt(x0 + 2, 60, x1 - 2, 76, 8)
        d.rekt(x0 + 1, 33, x0 + 2, 78, 10)
    d.ljus(rutmask(153, 31, 173, 80), 0.3, MORKARE)
    d.rekt(176, 50, 178, 56, 10)
    d.px(177, 52, 13)
    # Visaren: halvcirkel med siffror
    d.a[d.mask_ellips(150, 10, 176, 36) & (YY < 24)] = 10
    d.a[d.mask_ellips(152, 12, 174, 34) & (YY < 24)] = 0
    d.rekt(150, 23, 176, 26, 10)
    for k in range(6):
        a = math.pi + k * math.pi / 5
        d.px(int(163 + 9 * math.cos(a)), int(23 + 9 * math.sin(a)), 15)
    a = math.pi + [0, 1, 2, 3, 4, 5][hiss] * math.pi / 5
    d.linje(163, 23, int(round(163 + 7 * math.cos(a))), int(round(23 + 7 * math.sin(a))), 13)
    d.px(163, 23, 11)

    # --- Krukpalmen ---
    with d.yta("hotellpalm"):
        sv = [0, 1, 0, -1][palm]
        tx, ty = 46, 40
        d.linje(46, 76, 45, 50, 7)
        d.linje(47, 76, 46, 50, 8)
        d.linje(45, 50, tx, ty + 2, 7)
        for y in range(52, 76, 3):
            d.px(46, y, 6)
        blad = [(-22, 8), (-19, -4), (-12, -12), (-3, -16), (6, -15), (14, -10), (21, -2), (22, 10),
                (-16, 16), (14, 16), (0, -10)]
        for i, (bx, by) in enumerate(blad):
            s_ = sv * (1 if i % 2 else -1) if abs(bx) > 10 else 0
            ex, ey = tx + bx + s_, ty + by + abs(bx) // 2
            mx, my = tx + bx * 0.55, ty + by * 0.6 - 4
            for t in range(17):
                f = t / 16
                x = (1 - f) ** 2 * tx + 2 * (1 - f) * f * mx + f * f * ex
                y = (1 - f) ** 2 * ty + 2 * (1 - f) * f * my + f * f * ey
                xi, yi = int(round(x)), int(round(y))
                d.px(xi, yi, 12)
                if 2 < t < 16:
                    ln = 3 if t < 12 else 2
                    for k in range(1, ln + 1):
                        d.px(xi - k, yi + k, 12 if k < ln else 6)
                        d.px(xi + k, yi + k, 12 if k < ln else 6)
            d.px(int(ex), int(ey), 6)
        d.radial(50, 32, 20, 0.4, mask=(d.a == 12) & (XX > 40))
        # Krukan: mässing med deco-band
        d.poly([(36, 74), (56, 74), (53, 92), (39, 92)], 9)
        d.rekt(35, 72, 57, 76, 10)
        d.rekt(35, 72, 57, 73, 11)
        d.rekt(37, 82, 55, 84, 13)
        d.rekt(38, 77, 39, 91, 10)
        d.ljus(d.mask_poly([(48, 76), (56, 76), (53, 92), (48, 92)]), 0.5, MORKARE)
        d.poly([(38, 92), (54, 92), (55, 94), (37, 94)], 0)

    # --- Piccolon vid hissen ---
    with d.yta("piccolo"):
        px_ = 170
        # Ben och skor
        d.rekt(px_ + 2, 88, px_ + 6, 102, 0)
        d.rekt(px_ + 8, 88, px_ + 12, 102, 0)
        d.rekt(px_ + 5, 88, px_ + 6, 102, 13)
        d.rekt(px_ + 8, 88, px_ + 9, 102, 13)
        d.rekt(px_ + 1, 101, px_ + 6, 103, 0)
        d.rekt(px_ + 8, 101, px_ + 13, 103, 0)
        d.px(px_ + 2, 101, 4)
        d.px(px_ + 12, 101, 4)
        # Röd jacka med guldknappar
        d.rekt(px_, 72, px_ + 14, 89, 13)
        d.rekt(px_, 72, px_ + 1, 89, 14)
        d.rekt(px_ + 13, 72, px_ + 14, 89, 6)
        for y in range(74, 88, 3):
            d.px(px_ + 5, y, 10)
            d.px(px_ + 9, y, 10)
        d.rekt(px_, 86, px_ + 14, 87, 10)
        d.rekt(px_ + 4, 72, px_ + 10, 73, 10)   # krage
        # Armar och vita handskar
        d.rekt(px_ - 2, 73, px_, 86, 13)
        d.rekt(px_ + 14, 73, px_ + 16, 86, 13)
        d.rekt(px_ - 2, 86, px_ + 1, 89, 15)
        d.rekt(px_ + 14, 86, px_ + 17, 89, 15)
        # Huvud
        d.rekt(px_ + 5, 70, px_ + 9, 72, 9)
        fyll(d, px_ + 2, 60, px_ + 12, 71, 10)
        d.px(px_ + 5, 65, 0)
        d.px(px_ + 9, 65, 0)
        d.px(px_ + 7, 66, 9)
        d.rekt(px_ + 6, 68, px_ + 9, 69, 8)
        d.px(px_ + 5, 67, 8)
        d.px(px_ + 9, 67, 8)
        d.px(px_ + 3, 67, 13)                    # rosiga kinder
        d.px(px_ + 11, 67, 13)
        d.px(px_ + 1, 65, 9)
        d.px(px_ + 12, 65, 9)
        d.rekt(px_ + 3, 61, px_ + 11, 63, 7)     # lugg
        # Den lilla runda mössan, på sned
        d.rekt(px_ + 4, 56, px_ + 11, 61, 13)
        d.rekt(px_ + 4, 56, px_ + 11, 57, 14)
        d.rekt(px_ + 4, 59, px_ + 11, 60, 10)
        d.rekt(px_ + 3, 60, px_ + 12, 61, 6)
        d.px(px_ + 7, 55, 10)
        d.linje(px_ + 3, 61, px_ + 4, 69, 0)    # hakrem
        d.radial(px_ + 7, 66, 9, 0.25, mask=(d.a == 10))

    # Ljusreflexer i det blanka golvet
    for lx in (58, 92, 135, 146):
        d.ljus(rutmask(lx - 3, 82, lx + 3, 98) & ((XX + YY) % 2 == 0) & (d.a != 13), 0.5)
    d.vinjett(0.35)
    return d


# ======================================================================
#  HOTEL MAJESTIC: COCKTAILBAREN
# ======================================================================
def lila(d, mask, ton=1):
    """Lila genom raster: ton 0 mörk, 1 mellan, 2 ljus."""
    c1, c2 = [(6, 3), (13, 3), (14, 4)][ton]
    dither(d, mask, c1, c2)


def hotell_bar(v=None):
    v = v or {}
    shake = v.get("shake", 0)       # shakerns läge 0..3
    rok = v.get("rok", 0)           # röken 0..5
    flimmer = v.get("flimmer", 0)   # lampans flimmer 0..3
    rnd = random.Random(1933)
    d = Duk(0)

    # --- Väggar: mörk sammet med deco-ränder ---
    d.vgrad(0, 0, W, 76, [0, 0, 1, 1])
    for x in range(0, W, 12):
        d.rekt(x + 5, 10, x + 6, 70, 1 if x % 24 else 2)
    d.rekt(0, 8, W, 10, 6)
    d.rekt(0, 9, W, 10, 9)
    d.rekt(0, 70, W, 76, 6)
    d.rekt(0, 70, W, 71, 8)
    # Golv: mörka trätiljor
    d.rekt(0, 76, W, H, 6)
    for y in range(78, H, 4):
        d.rekt(0, y, W, y + 1, 0)
        off = (y * 7) % 22
        for x in range(off, W, 22):
            d.rekt(x, y - 3, x + 1, y, 0)
    d.vgrad(0, 76, W, 84, [0, 6])

    # --- Dörren tillbaka till lobbyn ---
    with d.yta("utgang:s"):
        d.rekt(4, 26, 28, 78, 8)
        d.rekt(6, 28, 26, 78, 6)
        d.rekt(8, 30, 24, 76, 7)
        fyll(d, 10, 36, 22, 48, 9)
        fyll(d, 11, 37, 21, 47, 10)
        d.rekt(14, 39, 16, 41, 11)
        d.rekt(10, 54, 22, 74, 6)
        d.rekt(22, 56, 24, 60, 10)
        d.rekt(3, 15, 29, 24, 12)
        d.rekt(3, 15, 29, 16, 15)
        txt(d, 16 - bredd("LOBBY") // 2, 18, "LOBBY", 15)
        d.radial(16, 20, 14, 0.45, mask=(d.a < 3))
        d.ljus(rutmask(6, 78, 26, 90), 0.3)

    # --- Hyllor med flaskor bakom baren ---
    d.rekt(118, 12, W, 64, 6)
    d.vgrad(120, 14, W, 62, [2, 1, 1])
    for hy in (26, 40, 54):
        d.rekt(118, hy, W, hy + 2, 8)
        d.rekt(118, hy, W, hy + 1, 9)
        x = 121
        while x < W - 2:
            c = rnd.choice([12, 13, 10, 9, 5, 7, 12, 15])
            hh = rnd.randint(6, 10)
            d.rekt(x, hy - hh + 3, x + 3, hy, c)
            d.rekt(x + 1, hy - hh, x + 2, hy - hh + 3, c)
            d.px(x, hy - hh + 4, 11 if c in (10, 5, 9, 15) else LJUSARE[c])
            if c != 15 and rnd.random() < 0.4:
                d.rekt(x, hy - 5, x + 3, hy - 3, 15)
            x += rnd.randint(4, 6)
    # Hänglampor över baren
    for lx in (136, 176):
        d.rekt(lx, 0, lx + 1, 6, 0)
        d.poly([(lx - 4, 6), (lx + 5, 6), (lx + 3, 3), (lx - 2, 3)], 12)
        d.rekt(lx - 1, 6, lx + 2, 7, 11)
        d.radial(lx, 12, 30, 0.5, mask=rutmask(118, 7, W, 64))

    # --- Bartendern med fluga och shaker ---
    with d.yta("hotellbartender"):
        bx = 154
        d.rekt(bx - 8, 46, bx + 9, 68, 15)            # vit kavaj
        d.rekt(bx - 8, 46, bx - 7, 68, 5)
        d.rekt(bx + 8, 46, bx + 9, 68, 5)
        d.poly([(bx - 2, 46), (bx + 3, 46), (bx, 54)], 0)
        d.rekt(bx - 3, 46, bx + 4, 49, 0)             # svart fluga
        d.px(bx, 47, 2)
        d.px(bx - 3, 46, 0)
        d.rekt(bx - 2, 44, bx + 3, 46, 9)
        fyll(d, bx - 5, 32, bx + 6, 45, 10)
        d.rekt(bx - 5, 32, bx + 6, 36, 0)
        d.px(bx - 5, 37, 0)
        d.px(bx + 5, 37, 0)
        d.px(bx - 1, 33, 3)
        d.px(bx - 2, 38, 0)
        d.px(bx + 2, 38, 0)
        d.rekt(bx - 3, 41, bx + 4, 42, 7)             # tunn mustasch
        d.px(bx, 40, 9)
        d.radial(bx, 38, 10, 0.3, mask=(d.a == 10))
        # Armarna och shakern ovanför axeln
        sx, sy = [(bx + 12, 38), (bx + 13, 35), (bx + 11, 39), (bx + 14, 36)][shake]
        d.linje(bx + 7, 50, sx - 1, sy + 10, 15)
        d.linje(bx + 8, 50, sx, sy + 10, 15)
        d.linje(bx - 6, 50, sx - 3, sy + 4, 15)
        d.linje(bx - 5, 51, sx - 2, sy + 5, 15)
        d.rekt(sx - 2, sy - 3, sx + 3, sy + 9, 5)
        d.rekt(sx - 1, sy - 5, sx + 2, sy - 3, 4)
        d.px(sx, sy - 6, 5)
        d.rekt(sx - 2, sy + 2, sx + 3, sy + 3, 4)
        d.rekt(sx - 2, sy - 3, sx - 1, sy + 9, 15)
        d.rekt(sx - 3, sy + 8, sx + 1, sy + 11, 10)   # händer
        d.rekt(sx - 4, sy + 3, sx - 1, sy + 6, 10)
        # Skakstreck
        if shake % 2:
            d.px(sx + 4, sy - 2, 4)
            d.px(sx + 5, sy, 4)
        else:
            d.px(sx - 4, sy - 3, 4)
            d.px(sx + 4, sy + 1, 4)

    # --- Bardisken och barstolar ---
    d.rekt(112, 66, W, 71, 8)
    d.rekt(112, 66, W, 67, 9)
    d.rekt(114, 71, W, 102, 6)
    for x in range(118, W, 12):
        d.rekt(x, 74, x + 9, 96, 7)
        d.rekt(x, 74, x + 9, 75, 8)
        d.linje(x + 1, 95, x + 8, 76, 6)
    d.rekt(114, 98, W, 99, 10)
    d.rekt(114, 101, W, 102, 0)
    d.rekt(126, 62, 131, 66, 5)                       # glas på disken
    d.rekt(127, 63, 130, 66, 4)
    d.px(126, 62, 15)
    d.rekt(176, 63, 178, 66, 10)
    for sx in (130, 168):
        d.rekt(sx - 5, 84, sx + 6, 87, 13)
        d.rekt(sx - 5, 84, sx + 6, 85, 14)
        d.rekt(sx, 87, sx + 1, 106, 10)
        d.rekt(sx - 4, 105, sx + 5, 107, 10)

    # --- Kvinnans stol (bakom bordet) ---
    d.a[d.mask_ellips(80, 50, 110, 76)] = 6
    d.a[d.mask_ellips(82, 52, 108, 74)] = 7
    d.rekt(84, 64, 108, 94, 7)
    d.rekt(106, 64, 108, 94, 6)
    d.rekt(104, 94, 106, 106, 0)

    # --- Kvinnan i lila ---
    with d.yta("vane"):
        wx = 94
        # Kjol (syns under bordet) och överkropp
        kjol = d.mask_poly([(wx - 8, 74), (wx + 8, 74), (wx + 7, 99), (wx - 10, 100), (wx - 12, 94)])
        lila(d, kjol, 1)
        d.ljus(kjol & (XX > wx + 1), 0.5, MORKARE)
        kropp = d.mask_poly([(wx - 5, 56), (wx + 5, 56), (wx + 6, 76), (wx - 6, 76)])
        lila(d, kropp, 1)
        lila(d, rutmask(wx - 5, 57, wx - 3, 76), 2)
        d.poly([(wx - 2, 56), (wx + 2, 56), (wx, 60)], 15)   # urringning med pärlor
        d.px(wx - 2, 57, 15)
        d.px(wx + 2, 57, 15)
        d.px(wx + 1, 59, 15)
        # Korslagda ben i nylon, högklackat
        d.linje(wx - 9, 99, wx - 15, 106, 9)
        d.linje(wx - 8, 99, wx - 14, 106, 9)
        d.rekt(wx - 19, 106, wx - 13, 108, 13)
        d.px(wx - 13, 108, 13)
        d.linje(wx - 3, 100, wx - 2, 107, 9)
        d.linje(wx - 2, 100, wx - 1, 107, 8)
        d.rekt(wx - 5, 107, wx + 1, 109, 13)
        # Hals och ansikte (vänt åt vänster)
        d.rekt(wx - 1, 52, wx + 2, 56, 15)
        fyll(d, wx - 5, 41, wx + 4, 53, 15)
        d.px(wx - 4, 47, 0)
        d.px(wx - 3, 47, 0)
        d.px(wx - 4, 46, 0)
        d.px(wx - 6, 49, 15)
        d.rekt(wx - 5, 51, wx - 2, 52, 13)
        d.px(wx - 3, 50, 13)
        d.rekt(wx + 1, 44, wx + 5, 54, 0)
        d.px(wx + 3, 54, 0)
        d.px(wx, 50, 9)
        d.px(wx, 51, 10)
        # Hatten med slöja
        lila(d, rutmask(wx - 11, 41, wx + 8, 43), 0)
        lila(d, d.mask_ellips(wx - 5, 34, wx + 5, 44) & (YY < 42), 1)
        d.rekt(wx - 4, 39, wx + 5, 40, 14)
        d.px(wx + 5, 36, 14)
        d.px(wx + 6, 35, 15)
        d.px(wx + 7, 34, 15)
        d.px(wx + 8, 34, 5)
        for y in range(43, 49):
            for x in range(wx - 7, wx + 2):
                if (x + y) % 3 == 0 and d.a[y, x] in (15, 0):
                    d.px(x, y, 3)
        # Armen som vilar på bordet, vid glaset
        lila(d, d.mask_poly([(wx + 1, 60), (wx + 5, 60), (wx - 2, 80), (wx - 6, 80)]), 1)
        d.rekt(wx - 10, 78, wx - 4, 81, 15)
        # Armen med cigarettmunstycket
        lila(d, d.mask_poly([(wx - 5, 58), (wx - 2, 60), (wx - 8, 67), (wx - 10, 65)]), 2)
        d.rekt(wx - 12, 63, wx - 8, 67, 15)
        d.radial(wx - 2, 48, 12, 0.35, mask=(d.a == 15))

    # --- Cigarettmunstycket och röken ---
    d.linje(82, 64, 73, 57, 0)
    d.px(73, 57, 13)
    d.px(72, 56, 10)
    for i in range(7):
        y = 55 - i * 3 - (rok % 2)
        x = 72 + int(round(2 * math.sin((i + rok * 0.5) * 1.3)))
        if y > 18:
            d.px(x, y, 5 if i < 2 else 4 if i < 5 else 3)
            if i % 2:
                d.px(x + 1, y - 1, 4 if i < 4 else 3)

    # --- Bordet (framför henne) ---
    with forgrund(d):
        d.rekt(78, 92, 82, 111, 0)
        d.rekt(70, 110, 90, 112, 0)
        d.rekt(71, 110, 89, 111, 9)
        fyll(d, 52, 82, 108, 95, 0)
        fyll(d, 52, 81, 108, 93, 15)
        d.ljus(d.mask_ellips(52, 81, 108, 93), 0.4, MORKARE)
        d.a[d.mask_ellips(52, 81, 108, 95) & ~d.mask_ellips(52, 81, 108, 93)] = 9
        # Askkopp
        d.rekt(96, 86, 101, 88, 4)
        d.px(98, 86, 13)
        # Handen ligger på bordskanten
        d.rekt(wx - 10, 80, wx - 4, 83, 15)

    # --- Bordslampan ---
    with d.yta("bordslampa"):
        lx = 64
        lyse = [0.6, 0.55, 0.6, 0.38][flimmer]
        d.rekt(lx - 3, 84, lx + 4, 87, 9)
        d.rekt(lx - 3, 84, lx + 4, 85, 10)
        d.rekt(lx, 68, lx + 1, 84, 9)
        d.poly([(lx - 9, 72), (lx + 10, 72), (lx + 6, 60), (lx - 5, 60)], 10)
        d.poly([(lx - 9, 72), (lx + 10, 72), (lx + 9, 70), (lx - 8, 70)], 11 if flimmer != 3 else 10)
        d.linje(lx - 5, 60, lx + 6, 60, 9)
        for x in range(lx - 6, lx + 8, 3):
            d.px(x, 73, 9)
        d.ljus(d.mask_poly([(lx + 2, 72), (lx + 10, 72), (lx + 6, 60), (lx + 2, 60)]), 0.4, MORKARE)
        d.radial(lx, 78, 48, lyse, mask=(YY > 54) & (YY < 114) & (XX < 114) & ~rutmask(lx - 9, 60, lx + 11, 74))
    d.radial(64, 64, 22, 0.3 if flimmer != 3 else 0.15, mask=(YY < 60) & (d.a < 3))

    # --- Cocktailen ---
    with d.yta("cocktail"):
        gx, gy = 80, 78
        d.poly([(gx - 4, gy), (gx + 5, gy), (gx + 1, gy + 4), (gx, gy + 4)], 4)
        lila(d, d.mask_poly([(gx - 3, gy + 1), (gx + 4, gy + 1), (gx + 1, gy + 4), (gx, gy + 4)]), 2)
        d.rekt(gx - 4, gy, gx + 5, gy + 1, 5)
        d.rekt(gx, gy + 4, gx + 1, gy + 8, 5)
        d.rekt(gx - 2, gy + 8, gx + 3, gy + 9, 5)
        d.px(gx + 3, gy - 1, 13)
        d.linje(gx + 3, gy - 1, gx + 5, gy - 4, 12)
    d.markera("cocktail", 76, 74, 85, 87)

    # Rökslöjor under taket
    for i in range(36):
        x, y = rnd.randint(20, 190), rnd.randint(12, 34)
        if d.a[y, x] < 2:
            d.px(x, y, 2)
    d.vinjett(0.45)
    return d


# ======================================================================
#  RÅDHUSETS MARMORHALL
# ======================================================================
def borgmastarportratt(d, x, y, typ):
    """Litet porträtt 14 x 18 i guldram. typ 0..4 ger olika borgmästare."""
    d.rekt(x, y, x + 14, y + 18, 9)
    d.rekt(x, y, x + 14, y + 1, 10)
    d.rekt(x, y, x + 1, y + 18, 10)
    d.rekt(x + 2, y + 2, x + 12, y + 16, [12, 6, 13, 12, 6][typ] if typ != 2 else 6)
    d.rekt(x + 2, y + 2, x + 12, y + 16, [12, 6, 1, 12, 6][typ])
    cx = x + 7
    d.rekt(x + 3, y + 12, x + 11, y + 16, 0)          # rock
    d.rekt(cx - 1, y + 12, cx + 1, y + 14, 15)
    fyll(d, cx - 3, y + 4, cx + 3, y + 12, 9)
    if typ == 0:      # skäggig med polisonger
        d.rekt(cx - 3, y + 8, cx + 4, y + 12, 5)
        d.rekt(cx - 2, y + 4, cx + 3, y + 5, 5)
    elif typ == 1:    # skallig med monokel
        d.px(cx + 1, y + 7, 11)
        d.px(cx - 1, y + 7, 0)
        d.rekt(cx - 2, y + 9, cx + 3, y + 10, 7)
    elif typ == 2:    # hög hatt
        d.rekt(cx - 3, y + 2, cx + 4, y + 6, 0)
        d.rekt(cx - 4, y + 5, cx + 5, y + 6, 0)
        d.rekt(cx - 2, y + 9, cx + 3, y + 10, 0)
    elif typ == 3:    # stor mustasch
        d.rekt(cx - 4, y + 8, cx + 5, y + 10, 7)
        d.rekt(cx - 3, y + 4, cx + 4, y + 6, 7)
    else:             # rund och rödbrusig (känns igen?)
        fyll(d, cx - 4, y + 4, cx + 4, y + 13, 9)
        d.px(cx - 2, y + 9, 13)
        d.px(cx + 2, y + 9, 13)
        d.rekt(cx - 3, y + 10, cx + 4, y + 11, 15)
        d.rekt(x + 3, y + 13, x + 11, y + 16, 0)
        d.rekt(cx - 2, y + 13, cx + 3, y + 14, 10)
    d.px(cx - 1, y + 7, 0)
    d.px(cx + 1, y + 7, 0)
    # Mässingsskylt
    d.rekt(cx - 3, y + 19, cx + 4, y + 21, 10)


def radhus_hall(v=None):
    v = v or {}
    skriv = v.get("skriv", 0)    # skrivmaskinen 0..3
    vikt = v.get("vikt", 0)      # mannen i kön skiftar vikt 0..1
    rnd = random.Random(1912)
    d = Duk(3)

    # --- Väggar i ljus marmor med ådror ---
    d.vgrad(0, 0, W, 82, [2, 3, 3, 4])
    for i in range(30):
        x, y = rnd.randint(0, W - 8), rnd.randint(10, 76)
        d.linje(x, y, x + rnd.randint(3, 10), y + rnd.randint(-3, 5), 5 if i % 3 else 3)
    d.rekt(0, 0, W, 6, 2)
    d.rekt(0, 5, W, 6, 15)
    for x in range(0, W, 8):
        d.rekt(x, 1, x + 4, 4, 3)
    d.rekt(0, 72, W, 82, 3)
    d.rekt(0, 72, W, 73, 15)
    d.rekt(0, 81, W, 82, 2)
    # Pelare
    for px_ in (30, 128):
        d.rekt(px_, 6, px_ + 6, 82, 15)
        d.rekt(px_ + 4, 6, px_ + 6, 82, 5)
        d.rekt(px_ + 1, 6, px_ + 2, 82, 11)
        d.rekt(px_ - 1, 6, px_ + 7, 9, 5)
        d.rekt(px_ - 1, 78, px_ + 7, 82, 5)

    # --- Golv: marmor i schack ---
    schackgolv(d, 82, 5, 3, skala=1.4, rad_k=220)
    d.ljus(rutmask(0, 82, W, 92), 0.45, MORKARE)

    # --- Entrédörrarna ---
    with d.yta("utgang:ut"):
        d.rekt(2, 18, 28, 88, 15)
        d.rekt(4, 20, 26, 88, 6)
        fyll(d, 4, 12, 26, 30, 15)
        d.a[d.mask_ellips(6, 14, 24, 28) & (YY < 21)] = 5     # solfjäderfönster
        for k in range(-2, 3):
            d.linje(15, 21, 15 + k * 4, 14, 15)
        d.rekt(4, 21, 26, 22, 15)
        for (x0, x1) in ((5, 15), (15, 25)):
            d.rekt(x0, 22, x1, 88, 7)
            d.rekt(x0 + 2, 25, x1 - 2, 52, 8)
            d.rekt(x0 + 2, 56, x1 - 2, 84, 8)
            d.rekt(x0 + 3, 26, x1 - 3, 51, 2)
            d.vgrad(x0 + 3, 26, x1 - 3, 51, [4, 3, 2])
            d.px(x0 + 4, 30, 5)
            d.px(x0 + 5, 36, 5)
        d.rekt(14, 22, 16, 88, 6)
        d.rekt(12, 58, 14, 61, 10)
        d.rekt(16, 58, 18, 61, 10)
        d.rekt(8, 8, 22, 15, 0)
        txt(d, 15 - bredd("UT") // 2, 9, "UT", 10)
        d.ljus(rutmask(2, 88, 28, 96), 0.35)

    # --- Porträtt av forna borgmästare ---
    with d.yta("portratt_rad"):
        for i, x in enumerate(range(40, 124, 17)):
            borgmastarportratt(d, x, 12, i)
        d.radial(82, 8, 50, 0.3, mask=rutmask(38, 10, 124, 36) & (d.a < 12))

    # --- Nummervisare på väggen (ovanför kön) ---
    d.rekt(96, 42, 125, 53, 0)
    d.rekt(96, 42, 125, 43, 10)
    d.rekt(96, 52, 125, 53, 10)
    txt(d, 99, 45, "NR", 15)
    txt(d, 109, 45, "12", 13)
    fyll(d, 118, 45, 122, 49, 13)
    d.px(119, 46, 14)
    d.rekt(110, 53, 112, 56, 10)

    # --- Receptionisten ---
    with d.yta("receptionist"):
        rx = 64
        d.poly([(rx - 9, 62), (rx + 9, 62), (rx + 10, 80), (rx - 10, 80)], 2)   # grå dräkt
        d.rekt(rx - 9, 62, rx - 8, 80, 3)
        d.poly([(rx - 3, 62), (rx + 3, 62), (rx, 67)], 15)                  # blusens krage
        d.px(rx, 64, 10)                                                     # brosch
        d.rekt(rx - 1, 59, rx + 2, 62, 9)
        fyll(d, rx - 5, 47, rx + 5, 61, 10)
        # Håret: stramt bakåt i en knut
        d.rekt(rx - 5, 47, rx + 6, 51, 7)
        d.px(rx - 5, 52, 7)
        d.px(rx + 5, 52, 7)
        d.px(rx - 5, 53, 7)
        d.px(rx + 5, 53, 7)
        fyll(d, rx - 3, 42, rx + 4, 49, 7)
        d.px(rx - 1, 43, 8)
        d.px(rx, 43, 8)
        d.linje(rx + 3, 44, rx + 6, 42, 0)        # hårnålar
        d.linje(rx - 3, 44, rx - 6, 43, 0)
        d.linje(rx - 2, 48, rx + 2, 48, 8)
        # Glasögon och stränga ögonbryn
        d.linje(rx - 4, 52, rx - 1, 53, 0)
        d.linje(rx + 1, 53, rx + 4, 52, 0)
        d.rekt(rx - 4, 54, rx - 1, 56, 5)
        d.rekt(rx + 1, 54, rx + 4, 56, 5)
        d.px(rx - 3, 55, 0)
        d.px(rx + 2, 55, 0)
        d.px(rx, 54, 0)
        d.px(rx - 5, 54, 0)
        d.px(rx + 4, 54, 0)
        d.px(rx, 57, 9)
        d.rekt(rx - 2, 59, rx + 3, 60, 13)          # sammanbitna läppar
        d.radial(rx, 54, 9, 0.25, mask=(d.a == 10))

    # --- Disken ---
    with forgrund(d):
        d.rekt(36, 78, 90, 82, 15)
        d.rekt(36, 78, 90, 79, 11)
        d.rekt(38, 82, 88, 100, 5)
        d.rekt(38, 82, 88, 83, 15)
        for x in range(42, 86, 11):
            d.rekt(x, 85, x + 9, 97, 15)
            d.rekt(x, 85, x + 9, 86, 11)
            d.linje(x + 1, 96, x + 7, 87, 4)
        d.rekt(38, 98, 88, 100, 3)
        # INFO-skylt
        d.rekt(72, 70, 92, 78, 10)
        d.rekt(73, 71, 91, 77, 0)
        txt(d, 82 - bredd("INFO") // 2, 72, "INFO", 10)
        # Stämpelställ
        d.rekt(37, 73, 43, 78, 7)
        d.rekt(38, 70, 39, 73, 0)
        d.rekt(41, 71, 42, 73, 0)
        d.rekt(37, 69, 40, 70, 13)

    # Skrivmaskinen och händerna (en del av receptionistens klickyta)
    with d.yta("receptionist"):
        tx = 45 + [0, 1, 2, 3][skriv]
        d.poly([(44, 78), (62, 78), (60, 72), (46, 72)], 0)
        d.rekt(46, 72, 60, 73, 2)
        for kx in range(46, 61, 2):
            d.px(kx, 75, 5)
            d.px(kx + 1, 77, 5)
        if skriv % 2:
            d.px(49 + skriv, 74, 15)
        d.rekt(tx - 3, 69, tx + 13, 72, 0)       # vagnen
        d.rekt(tx - 4, 70, tx - 3, 71, 10)
        d.rekt(tx + 1, 63, tx + 9, 70, 15)       # papperet
        for y in (65, 67):
            d.linje(tx + 2, y, tx + 7, y, 4)
        d.rekt(55, 74 + (skriv % 2), 59, 76 + (skriv % 2), 10)       # händerna
        d.rekt(59, 73, 62, 75, 10)

    # --- Kön av sura medborgare ---
    with d.yta("koande"):
        def medborgare(x, h, hatt, rock, ansikte=10, nr="7"):
            fot = 106
            topp = fot - h
            kr = topp + 13
            d.poly([(x - 5, kr), (x + 5, kr), (x + 6, fot - 9), (x - 6, fot - 9)], rock)
            d.rekt(x - 5, kr, x - 4, fot - 9, LJUSARE[rock])
            d.rekt(x + 4, kr, x + 6, fot - 9, MORKARE[rock])
            d.rekt(x - 4, fot - 9, x - 1, fot, 0)
            d.rekt(x + 1, fot - 9, x + 4, fot, 0)
            d.rekt(x - 6, fot - 1, x - 1, fot + 1, 0)
            d.rekt(x, fot - 1, x + 4, fot + 1, 0)
            d.rekt(x - 1, kr - 2, x + 2, kr, ansikte)
            fyll(d, x - 4, topp + 3, x + 4, kr - 1, ansikte)
            d.px(x - 5, topp + 8, ansikte)                  # näsa (vänd åt vänster)
            d.px(x - 5, topp + 9, MORKARE[ansikte])
            d.px(x - 3, topp + 7, 0)                        # öga
            d.rekt(x - 4, topp + 6, x - 1, topp + 7, 0)     # rynkat bryn
            d.rekt(x - 4, topp + 11, x - 1, topp + 12, 6)   # sur mun
            d.px(x - 1, topp + 12, 6)
            d.px(x + 3, topp + 8, MORKARE[ansikte])         # öra
            if hatt == "fedora":
                d.rekt(x - 4, topp, x + 4, topp + 4, 0)
                d.rekt(x - 6, topp + 4, x + 6, topp + 5, 0)
                d.rekt(x - 4, topp + 3, x + 4, topp + 4, 7)
            elif hatt == "dam":
                d.rekt(x - 4, topp + 1, x + 5, topp + 4, 13)
                d.rekt(x - 7, topp + 4, x + 6, topp + 5, 13)
                d.px(x + 3, topp, 14)
                d.px(x + 4, topp - 1, 10)
                d.rekt(x + 2, topp + 5, x + 5, topp + 12, 7)
            elif hatt == "kal":
                d.rekt(x + 1, topp + 5, x + 5, topp + 9, 5)
                d.px(x - 1, topp + 4, 11)
                d.rekt(x - 4, topp + 10, x, topp + 11, 15)   # grå mustasch
            elif hatt == "keps":
                d.rekt(x - 4, topp + 1, x + 5, topp + 4, 3)
                d.rekt(x - 7, topp + 4, x - 2, topp + 5, 3)
            # Arm framåt med nummerlapp
            d.rekt(x - 6, kr + 6, x - 3, kr + 8, rock)
            d.rekt(x - 7, kr + 6, x - 5, kr + 8, ansikte)
            d.rekt(x - 11, kr + 2, x - 5, kr + 9, 15)
            d.rekt(x - 11, kr + 8, x - 5, kr + 9, 5)
            txt(d, x - 9, kr + 3, nr, 13)
        medborgare(97, 32, "dam", 13, nr="7")
        medborgare(113 + vikt, 40, "fedora", 7, nr="8")
        medborgare(129, 28, "kal", 2, nr="9")
        # Gubben längst bak har en käpp
        d.linje(134, 92, 135, 106, 6)
        d.rekt(131, 91, 135, 93, 6)

    # --- Den breda marmortrappan upp ---
    with d.yta("utgang:upp"):
        x0, x1 = 140, W
        for i in range(10):
            y = 98 - i * 6
            ins = i * 2
            d.rekt(x0 + ins, y - 6, x1, y, 4)
            d.rekt(x0 + ins, y - 6, x1, y - 4, 15)
            d.rekt(x0 + ins, y - 1, x1, y, 3)
            d.rekt(x0 + ins + 14, y - 6, x1 - 10, y, 13)      # röd löpare
            d.rekt(x0 + ins + 14, y - 6, x1 - 10, y - 4, 14)
            d.rekt(x0 + ins + 14, y - 5, x1 - 10, y - 4, 10)  # mässingsstång
        d.rekt(156, 30, W, 38, 3)
        d.rekt(156, 30, W, 31, 15)
        # Räcket med mässingsledstång
        d.linje(138, 72, 158, 22, 10)
        d.linje(138, 73, 158, 23, 9)
        for i in range(0, 10, 2):
            bx = 140 + i * 2
            by = 98 - i * 6
            d.rekt(bx, 72 - i * 5, bx + 1, by - 3, 15)
        d.rekt(136, 70, 141, 100, 15)
        d.rekt(136, 70, 141, 72, 11)
        fyll(d, 135, 64, 142, 71, 10)                       # glob
        d.px(137, 66, 11)
        d.radial(138, 67, 14, 0.4, mask=(d.a < 6))
        # Skylt
        d.rekt(166, 10, 190, 19, 0)
        d.rekt(166, 10, 190, 11, 10)
        txt(d, 178 - bredd("KONTOR") // 2, 12, "KONTOR", 10)
        d.rekt(176, 19, 178, 24, 10)
    d.markera("utgang:upp", 140, 26, W, 100)

    d.radial(96, 30, 110, 0.25)
    d.vinjett(0.35)
    return d


# ======================================================================
#  BORGMÄSTARENS KONTOR
# ======================================================================
def borgmastare(v=None):
    v = v or {}
    flagga = v.get("flagga", 0)   # 0..2
    torka = v.get("torka", 0)     # 0 armen nere, 1-2 torkar pannan
    rnd = random.Random(1946)
    d = Duk(6)

    # --- Väggar: mörkgrön tapet över träpanel ---
    dither(d, rutmask(0, 0, W, 58), 12, 6)
    for x in range(0, W, 10):
        d.rekt(x, 0, x + 1, 58, 6)
    d.rekt(0, 0, W, 5, 7)
    d.rekt(0, 4, W, 5, 9)
    d.rekt(0, 56, W, 86, 7)
    d.rekt(0, 56, W, 58, 9)
    for x in range(4, W, 22):
        d.rekt(x, 61, x + 18, 82, 8)
        d.rekt(x + 1, 62, x + 17, 81, 7)
    d.rekt(0, 84, W, 86, 6)
    # Golv: röd matta med mönsterbård
    d.rekt(0, 86, W, H, 13)
    d.ljus(rutmask(0, 86, W, H), 0.4, MORKARE)
    d.rekt(0, 90, W, 91, 10)
    for x in range(0, W, 6):
        d.px(x + 3, 92, 10)
    d.vgrad(0, 86, W, 90, [6, 13])

    # --- Fönstret med flaggstång och regnig stad ---
    with d.yta("fonster_rad"):
        fx0, fx1, fy0, fy1 = 142, 182, 8, 66
        d.rekt(fx0 - 2, fy0 - 2, fx1 + 2, fy1 + 3, 8)
        d.vgrad(fx0, fy0, fx1, fy1, [1, 2, 3, 3])
        # Stadssiluett
        x = fx0
        r2 = random.Random(7)
        while x < fx1:
            b = r2.randint(4, 8)
            t = r2.randint(36, 52)
            d.rekt(x, t, x + b, fy1, 1)
            for wy in range(t + 2, fy1, 3):
                for wx in range(x + 1, x + b - 1, 2):
                    if r2.random() < 0.2:
                        d.px(wx, wy, 9)
            x += b
        d.rekt(154, 26, 158, fy1, 0)      # torn med spira
        d.rekt(155, 20, 157, 26, 0)
        d.px(156, 18, 0)
        d.px(156, 19, 0)
        # Flaggstången och flaggan
        d.rekt(166, 14, 167, 60, 15)
        d.px(166, 13, 10)
        fl = [
            [(167, 16), (174, 15), (180, 17), (180, 23), (174, 21), (167, 22)],
            [(167, 16), (173, 17), (179, 15), (180, 21), (173, 23), (167, 22)],
            [(167, 16), (174, 16), (179, 18), (178, 24), (172, 22), (167, 22)],
        ][flagga]
        d.poly(fl, 13)
        m = d.mask_poly(fl)
        d.a[m & ((YY % 3) == 1)] = 15
        d.a[m & (XX < 172) & (YY < 20)] = 2
        d.px(168, 17, 15)
        d.px(170, 18, 15)
        # Regn på rutan
        for _ in range(30):
            x, y = r2.randint(fx0, fx1 - 1), r2.randint(fy0, fy1 - 2)
            d.px(x, y, 4)
            d.px(x, y + 1, 5)
        # Spröjsar och fönsterbräda
        d.rekt(161, fy0, 163, fy1, 8)
        d.rekt(fx0, 36, fx1, 38, 8)
        d.rekt(fx0 - 4, fy1 + 2, fx1 + 4, fy1 + 5, 9)
        d.rekt(fx0 - 4, fy1 + 2, fx1 + 4, fy1 + 3, 10)
        # Gardiner
        for (g0, g1) in ((134, 142), (182, 190)):
            d.rekt(g0, 4, g1, 76, 13)
            for x in range(g0 + 1, g1, 3):
                d.rekt(x, 6, x + 1, 76, 6)
            d.rekt(g0, 4, g1, 6, 10)
        d.rekt(132, 2, 192, 4, 9)

    # --- Dörren ner till trappan ---
    with d.yta("utgang:ner"):
        d.rekt(2, 22, 26, 86, 8)
        d.rekt(4, 24, 24, 86, 0)
        # Trappan ner, i det mörka trapphuset
        for i in range(6):
            y = 62 + i * 4
            d.rekt(4, y, 24, y + 1, 3)
            d.rekt(4, y + 1, 24, y + 4, 1)
        d.vgrad(4, 24, 24, 62, [0, 1, 2])
        d.linje(6, 50, 22, 82, 9)     # ledstång
        # Dörrbladet, uppslaget inåt
        d.poly([(24, 24), (30, 20), (30, 90), (24, 86)], 7)
        d.poly([(25, 28), (29, 25), (29, 52), (25, 54)], 8)
        d.px(28, 58, 10)
        # Skylt med pil
        d.rekt(6, 10, 22, 20, 0)
        d.rekt(6, 10, 22, 11, 10)
        pil_ner(d, 14, 15, 10)
        d.ljus(rutmask(2, 86, 28, 96), 0.3)

    # --- Valaffischer ---
    with d.yta("valaffisch"):
        for (ax, ay, s) in ((32, 10, 1), (61, 16, 0)):
            w, h = (27, 38) if s else (27, 34)
            d.rekt(ax, ay, ax + w, ay + h, 15)
            d.rekt(ax + 1, ay + 1, ax + w - 1, ay + h - 1, 2)
            d.rekt(ax + 1, ay + 1, ax + w - 1, ay + 4, 13)
            for x in range(ax + 2, ax + w - 1, 3):
                d.px(x, ay + 2, 15)
            # Borgmästarens leende ansikte
            cx, cy = ax + w // 2, ay + 6 + h // 4
            r = 5 if s else 4
            fyll(d, cx - r, cy - r, cx + r, cy + r, 9)
            d.rekt(cx - r + 1, cy + 1, cx + r, cy + 2, 15)
            d.px(cx - 2, cy - 2, 0)
            d.px(cx + 2, cy - 2, 0)
            d.px(cx - r + 1, cy, 13)
            d.px(cx + r - 1, cy, 13)
            d.px(cx, cy + 3, 13)
            d.rekt(ax + 1, ay + h - 13, ax + w - 1, ay + h - 1, 15)
            txt(d, cx - bredd("VOTE") // 2 + 1, ay + h - 12, "VOTE", 13)
            txt(d, cx - bredd("BIGSBY") // 2 + 1, ay + h - 6, "BIGSBY", 2)
        d.px(35, 11, 4)
        d.poly([(84, 50), (88, 50), (88, 46)], 6)   # ett hörn har släppt
        d.px(87, 49, 15)

    # --- Uppstoppad fisk på planka ---
    with d.yta("fisktrofe"):
        d.rekt(88, 5, 126, 21, 7)
        d.rekt(88, 5, 126, 6, 9)
        d.rekt(88, 20, 126, 21, 6)
        d.px(90, 7, 10)
        d.px(124, 7, 10)
        fyll(d, 94, 8, 118, 18, 4)
        d.a[d.mask_ellips(94, 12, 118, 18)] = 3
        d.a[d.mask_ellips(97, 9, 114, 13)] = 5
        d.poly([(117, 13), (124, 7), (122, 13), (124, 19)], 4)    # stjärtfena
        d.poly([(104, 8), (110, 6), (112, 9)], 3)                # ryggfena
        d.poly([(93, 11), (96, 13), (93, 15)], 0)                   # gapande mun
        d.px(98, 11, 15)
        d.px(98, 12, 0)
        for x in range(102, 116, 3):
            d.px(x, 14, 12)
        d.radial(106, 11, 14, 0.3, mask=(d.a == 4) | (d.a == 5))

    # --- Sekreteraren fröken Prim ---
    with d.yta("prim"):
        p = 46
        # Smala ben i nylon och små pumps
        d.rekt(p - 3, 86, p - 1, 99, 9)
        d.rekt(p + 1, 86, p + 3, 99, 9)
        d.px(p - 2, 92, 8)
        d.rekt(p - 4, 99, p, 101, 0)
        d.rekt(p + 1, 99, p + 5, 101, 0)
        # Grå kjol och dräktjacka, insvängd i midjan
        d.poly([(p - 4, 74), (p + 5, 74), (p + 6, 87), (p - 5, 87)], 3)
        d.rekt(p - 5, 86, p + 6, 87, 2)
        d.poly([(p - 4, 59), (p + 5, 59), (p + 4, 75), (p - 3, 75)], 4)
        d.rekt(p - 4, 59, p - 3, 75, 5)
        d.rekt(p - 3, 74, p + 4, 75, 3)
        d.poly([(p - 1, 59), (p + 2, 59), (p, 64)], 15)   # blusens krage
        d.px(p, 66, 3)
        d.px(p, 69, 3)
        d.rekt(p - 1, 56, p + 2, 59, 10)
        # Huvud med page i mörkbrunt
        fyll(d, p - 4, 45, p + 4, 57, 10)
        d.rekt(p - 5, 44, p + 5, 48, 7)
        d.rekt(p - 5, 44, p - 3, 56, 7)
        d.rekt(p + 3, 44, p + 5, 56, 7)
        d.px(p - 5, 56, 6)
        d.px(p + 4, 56, 6)
        d.rekt(p - 2, 47, p + 3, 48, 6)               # rak lugg
        d.px(p - 2, 45, 8)
        # Pennan bakom örat
        d.linje(p + 4, 51, p + 7, 46, 10)
        d.px(p + 7, 46, 13)
        d.px(p + 4, 51, 0)
        # Stora runda glasögon
        ring(d, p - 4, 49, p - 1, 52, 0)
        ring(d, p + 1, 49, p + 4, 52, 0)
        d.px(p - 2, 50, 15)
        d.px(p + 2, 50, 15)
        d.px(p - 3, 51, 0)
        d.px(p + 3, 51, 0)
        d.px(p, 50, 0)
        d.px(p, 53, 9)
        d.rekt(p - 1, 54, p + 2, 55, 13)              # liten nervös mun
        d.px(p - 2, 53, 9)                            # rodnad
        d.px(p + 3, 53, 13)
        d.px(p - 6, 48, 5)                            # svettdroppe
        d.px(p - 6, 49, 4)
        # Anteckningsblocket tryckt mot bröstet
        d.rekt(p + 3, 63, p + 10, 72, 15)
        d.rekt(p + 3, 63, p + 10, 64, 13)
        for y in (66, 68, 70):
            d.linje(p + 4, y, p + 9, y, 4)
        d.linje(p - 3, 61, p + 2, 69, 4)              # armar
        d.linje(p - 2, 61, p + 3, 69, 4)
        d.rekt(p + 1, 68, p + 4, 71, 10)
        d.rekt(p + 9, 64, p + 11, 67, 10)
        d.linje(p + 5, 60, p + 9, 63, 4)

    # --- Borgmästaren bakom skrivbordet ---
    mx = 106
    with d.yta("borgmastaren"):
        # Den runda kroppen
        fyll(d, mx - 18, 46, mx + 18, 88, 2)
        d.ljus(d.mask_ellips(mx - 18, 46, mx + 18, 88) & (XX > mx + 6), 0.5, MORKARE)
        d.poly([(mx - 4, 48), (mx + 4, 48), (mx + 3, 74), (mx - 3, 74)], 15)   # skjortbröst
        d.poly([(mx - 4, 48), (mx + 4, 48), (mx, 52)], 10)
        # Skärpet diagonalt
        d.poly([(mx - 15, 52), (mx - 11, 50), (mx + 16, 74), (mx + 12, 77)], 13)
        d.linje(mx - 13, 51, mx + 14, 75, 14)
        # Borgmästarkedjan
        for i in range(11):
            t = i / 10
            x = int(mx - 12 + 24 * t)
            y = int(49 + 12 * math.sin(t * math.pi))
            d.px(x, y, 10 if i % 2 else 11)
            d.px(x, y + 1, 9)
        fyll(d, mx - 3, 60, mx + 3, 66, 10)
        d.px(mx - 1, 62, 11)
        d.px(mx + 1, 64, 9)
        # Hals och huvud, rödbrusigt
        d.rekt(mx - 6, 42, mx + 6, 49, 9)
        fyll(d, mx - 9, 24, mx + 9, 46, 9)
        d.ljus(d.mask_ellips(mx - 9, 24, mx + 9, 46) & (XX > mx + 4), 0.4, MORKARE)
        for (kx, ky) in ((mx - 6, 38), (mx + 5, 38)):     # rödbrusiga kinder
            d.rekt(kx, ky, kx + 2, ky + 2, 13)
            d.px(kx, ky, 14)
        # Flint med hårtofsar
        d.rekt(mx - 10, 30, mx - 8, 35, 5)
        d.rekt(mx + 8, 30, mx + 10, 35, 5)
        d.px(mx - 3, 27, 10)
        d.px(mx - 2, 26, 11)
        # Öron
        d.rekt(mx - 11, 33, mx - 9, 38, 8)
        d.rekt(mx + 9, 33, mx + 11, 38, 8)
        # Ögon och buskiga bryn
        d.rekt(mx - 6, 31, mx - 1, 32, 5)
        d.rekt(mx + 2, 31, mx + 7, 32, 5)
        d.rekt(mx - 5, 33, mx - 2, 35, 15)
        d.rekt(mx + 3, 33, mx + 6, 35, 15)
        d.px(mx - 4, 34, 0)
        d.px(mx + 4, 34, 0)
        # Röd näsa
        fyll(d, mx - 2, 34, mx + 2, 39, 13)
        d.px(mx - 1, 35, 14)
        # Valrossmustasch
        d.poly([(mx - 10, 46), (mx - 3, 38), (mx + 3, 38), (mx + 10, 46), (mx + 6, 44), (mx, 42), (mx - 6, 44)], 15)
        d.poly([(mx - 10, 46), (mx - 7, 42), (mx - 6, 45)], 5)
        d.poly([(mx + 10, 46), (mx + 7, 42), (mx + 6, 45)], 5)
        for x in range(mx - 6, mx + 7, 2):
            d.px(x, 42, 5)
        # Svettpärlor
        d.px(mx + 7, 27, 5)
        d.px(mx + 8, 28, 4)
        d.px(mx - 7, 28, 5)
        # Armen som torkar pannan
        if torka:
            nx = mx + (2 if torka == 1 else -2)
            for k in range(3):
                d.linje(mx + 14 + k, 60, mx + 16 + k, 44, 2)
                d.linje(mx + 15 + k, 44, nx + 4 + k, 28, 2)
            d.rekt(nx - 5, 23, nx + 7, 29, 15)
            d.rekt(nx - 5, 28, nx + 7, 29, 5)
            d.px(nx - 6, 25, 15)
            d.rekt(nx + 4, 28, nx + 8, 31, 9)

    # --- Det stora skrivbordet ---
    with forgrund(d):
        d.rekt(64, 74, 146, 78, 12)
        d.rekt(64, 74, 146, 75, 4)
        d.rekt(62, 77, 148, 80, 7)
        d.rekt(62, 77, 148, 78, 9)
        d.rekt(64, 80, 146, 104, 6)
        for x0 in (68, 122):
            d.rekt(x0, 82, x0 + 20, 102, 7)
            for y in (86, 93, 100):
                d.rekt(x0 + 2, y - 4, x0 + 18, y - 3, 8)
                d.rekt(x0 + 9, y - 2, x0 + 11, y - 1, 10)
        d.rekt(90, 82, 120, 100, 7)
        d.rekt(91, 83, 119, 99, 6)
        d.rekt(64, 102, 146, 104, 0)
        # Saker på skrivbordet
        d.rekt(93, 69, 119, 76, 10)             # namnskylt
        d.rekt(94, 70, 118, 75, 0)
        txt(d, 106 - bredd("MAYOR") // 2, 70, "MAYOR", 10)
        d.rekt(68, 70, 78, 74, 15)              # pappershögar
        d.rekt(69, 68, 78, 70, 15)
        d.rekt(68, 72, 78, 73, 5)
        d.rekt(132, 69, 142, 74, 0)             # telefon
        d.rekt(131, 67, 143, 69, 0)
        d.px(137, 71, 15)
        d.rekt(124, 71, 129, 74, 9)             # bläckställ
        d.linje(126, 71, 128, 64, 15)
        # Skrivbordslampa med grön skärm
        d.rekt(81, 72, 87, 74, 10)
        d.rekt(83, 66, 85, 72, 10)
        d.poly([(77, 66), (91, 66), (89, 62), (79, 62)], 12)
        d.rekt(77, 66, 91, 67, 11)
    d.radial(84, 72, 30, 0.5, mask=(YY > 66) & (YY < 106) & ~rutmask(77, 62, 91, 67))

    # Borgmästarens händer på skrivbordet
    with d.yta("borgmastaren"):
        d.rekt(mx - 24, 70, mx - 14, 76, 2)
        d.rekt(mx - 26, 73, mx - 20, 77, 9)
        if not torka:
            d.rekt(mx + 14, 70, mx + 24, 76, 2)
            d.rekt(mx + 20, 73, mx + 26, 77, 9)
            d.rekt(mx + 24, 72, mx + 30, 75, 15)   # näsduken i handen
            d.px(mx + 28, 76, 15)

    # Varmt ljus i rummet, mörka hörn
    d.radial(100, 50, 70, 0.25, mask=~np.isin(d.a, (9, 10, 13, 15)))
    d.vinjett(0.4)
    return d


SCENER_B = {
    "hotell_lobby": (hotell_lobby, [
        ("concierge", "borta", [(False, 1000), (True, 1000)], 1),
        ("hiss", "hiss", [(0, 1600), (1, 500), (2, 500), (3, 500), (4, 500), (5, 1800),
                          (4, 500), (3, 500), (2, 500), (1, 500)]),
        ("palm", "palm", [(0, 700), (1, 600), (0, 700), (3, 600)]),
    ]),
    "hotell_bar": (hotell_bar, [
        ("shake", "shake", [(i, 110) for i in range(4)] * 3 + [(0, 1500)]),
        ("rok", "rok", [(i, 300) for i in range(6)]),
        ("flimmer", "flimmer", [(0, 2400), (3, 90), (0, 160), (3, 70), (0, 1800), (1, 600)]),
    ]),
    "radhus_hall": (radhus_hall, [
        ("skriv", "skriv", [(i, 150) for i in range(4)] + [(0, 900)]),
        ("vikt", "vikt", [(0, 2200), (1, 1600)]),
    ]),
    "borgmastare": (borgmastare, [
        ("flagga", "flagga", [(i, 260) for i in range(3)]),
        ("torka", "torka", [(0, 3000), (1, 300), (2, 300), (1, 300), (2, 300)]),
    ]),
}
