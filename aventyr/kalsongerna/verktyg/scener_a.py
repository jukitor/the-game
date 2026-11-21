import math, random, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "motor" / "verktyg"))
from pixelbild import *  # noqa

"""Scener A: Main Streets västra del med polishuset och banken, polisstationens hall,
kommissariens kontor, Main Streets östra del med Hotel Majestic och biografen Rialto,
samt biografens foajé."""

# ======================================================================
#  EGNA TECKEN (utöver motorns TYPSNITT) och hjälpfunktioner
# ======================================================================
EXTRA = {
    "X": ["101", "101", "010", "101", "101"],
    "J": ["001", "001", "001", "101", "010"],
    "Q": ["010", "101", "101", "110", "011"],
    "0": ["010", "101", "101", "101", "010"],
    "2": ["110", "001", "010", "100", "111"],
    "4": ["101", "101", "111", "001", "001"],
    "5": ["111", "100", "110", "001", "110"],
    "6": ["011", "100", "110", "101", "010"],
    "7": ["111", "001", "010", "010", "010"],
    "8": ["010", "101", "010", "101", "010"],
    ".": ["0", "0", "0", "0", "1"],
    "!": ["1", "1", "1", "0", "1"],
    "'": ["1", "1", "0", "0", "0"],
    "$": ["011", "110", "010", "011", "110"],
    "-": ["00", "00", "11", "00", "00"],
}


def _glyf(ch):
    return EXTRA.get(ch) or TYPSNITT[ch]


def skriv(d, x, y, s, c, spegel=False):
    """Som text() men med de extra tecknen. spegel=True skriver spegelvänt (text sedd bakifrån)."""
    for ch in (s[::-1] if spegel else s):
        g = _glyf(ch)
        if spegel:
            g = [r[::-1] for r in g]
        for ry, rad in enumerate(g):
            for rx, bit in enumerate(rad):
                if bit == "1":
                    d.px(x + rx, y + ry, c)
        x += len(g[0]) + 1


def skriv_stor(d, x, y, s, c, skala):
    for ch in s:
        g = _glyf(ch)
        for ry, rad in enumerate(g):
            for rx, bit in enumerate(rad):
                if bit == "1":
                    d.rekt(x + rx * skala, y + ry * skala, x + (rx + 1) * skala, y + (ry + 1) * skala, c)
        x += (len(g[0]) + 1) * skala


def bredd(s, skala=1):
    return (sum(len(_glyf(ch)[0]) + 1 for ch in s) - 1) * skala


def _ellips(d, x0, y0, x1, y1, c):
    d.a[d.mask_ellips(x0, y0, x1, y1)] = c


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


def rektmask(x0, y0, x1, y1):
    return (XX >= x0) & (XX < x1) & (YY >= y0) & (YY < y1)


def sten(d, x0, y0, x1, y1, bas=3, fog=2, hojd=4, blockb=10, mork=0.3):
    """Fasad av huggen sten med fogar."""
    d.rekt(x0, y0, x1, y1, bas)
    for i, y in enumerate(range(y0 + hojd - 1, y1, hojd)):
        d.rekt(x0, y, x1, y + 1, fog)
        off = (i % 2) * (blockb // 2)
        for xx in range(x0 + off, x1, blockb):
            d.rekt(xx, y - hojd + 1, xx + 1, y, fog)
    if mork:
        d.ljus(rektmask(x0, y0, x1, y1), mork, MORKARE)


def gatubas(d, ytr=88, yk=96):
    """Trottoar, kantsten och blank asfalt."""
    d.vgrad(0, ytr, W, yk, [2, 3, 3])
    for xx in range(0, W, 12):
        d.rekt(xx, ytr, xx + 1, yk, 2)
    d.rekt(0, yk, W, yk + 1, 5)
    d.rekt(0, yk + 1, W, yk + 2, 4)
    d.rekt(0, yk + 2, W, yk + 3, 0)
    d.vgrad(0, yk + 3, W, H, [0, 1, 1, 2])
    # Vita streck och blanka stråk
    for xx in range(4, W, 22):
        d.rekt(xx, 110, xx + 10, 111, 4)


def spegel(d, x0, x1, f, y0=100, rutn=2):
    for y in range(y0, H):
        s = f * (1 - (y - y0) / (H - y0))
        m = (XX >= x0) & (XX < x1) & (YY == y) & ((XX + y) % rutn == 0)
        d.ljus(m, s * 2)


def gatlykta(d, x, ytop, ybas=92, glod=True):
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


def pilskylt(d, x, y, vanster, ybas=93):
    """Liten grön gatuskylt med pil på en stolpe, x = stolpens x."""
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


def regn(d, fas, antal=80, fro=7, **kw):
    regn_over(d, random.Random(fro), antal, fas, **kw)


def fonster(d, fx, fy, b, h, tand, gardin=True, ram=6):
    d.rekt(fx - 1, fy - 1, fx + b + 1, fy + h + 1, ram)
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


def kolonn(d, x, y0, y1, b=5, bas=4, ljus_=5, skugga=3):
    """Klassisk kolonn med kapitäl och bas."""
    d.rekt(x, y0, x + b, y1, bas)
    d.rekt(x, y0, x + 1, y1, ljus_)
    d.rekt(x + b - 1, y0, x + b, y1, skugga)
    for fx in range(x + 2, x + b - 1, 2):
        d.rekt(fx, y0 + 2, fx + 1, y1 - 2, skugga)
    d.rekt(x - 1, y0 - 2, x + b + 1, y0, ljus_)
    d.rekt(x - 1, y0 - 1, x + b + 1, y0, bas)
    d.rekt(x - 1, y1, x + b + 1, y1 + 2, bas)
    d.rekt(x - 1, y1, x + b + 1, y1 + 1, ljus_)


# ======================================================================
#  MAIN STREET, VÄSTRA DELEN: POLISHUSET OCH BANKEN
# ======================================================================
def trafikpolis(d, x, y, vift):
    """Trafikpolis på pall. (x, y) = mössans övre vänstra hörn. vift 0..2 = högerarmens läge."""
    t = Duk(16)
    # Ben och skor
    t.rekt(x + 1, y + 21, x + 4, y + 28, 1)
    t.rekt(x + 6, y + 21, x + 9, y + 28, 1)
    t.rekt(x + 4, y + 21, x + 6, y + 23, 1)
    t.rekt(x, y + 27, x + 4, y + 29, 0)
    t.rekt(x + 6, y + 27, x + 10, y + 29, 0)
    t.px(x + 2, y + 22, 2)
    t.px(x + 7, y + 22, 2)
    # Rocken
    t.rekt(x, y + 9, x + 10, y + 22, 2)
    t.rekt(x, y + 9, x + 1, y + 22, 3)
    t.rekt(x + 5, y + 10, x + 6, y + 22, 1)
    for by in (y + 12, y + 15, y + 19):
        t.px(x + 3, by, 10)
        t.px(x + 7, by, 10)
    t.rekt(x, y + 17, x + 10, y + 18, 0)          # bälte
    t.px(x + 5, y + 17, 10)
    t.linje(x + 1, y + 9, x + 9, y + 17, 15)      # vitt axelband
    t.rekt(x + 7, y + 11, x + 9, y + 13, 10)      # bricka
    t.px(x + 7, y + 11, 11)
    # Huvud
    t.rekt(x + 2, y + 4, x + 8, y + 9, 10)
    t.rekt(x + 2, y + 8, x + 8, y + 9, 9)
    t.px(x + 3, y + 6, 0)
    t.px(x + 6, y + 6, 0)
    t.px(x + 2, y + 7, 14)
    t.px(x + 7, y + 7, 14)
    t.rekt(x + 4, y + 8, x + 6, y + 9, 15)        # visselpipa
    t.px(x + 6, y + 9, 5)
    # Mössa med skärm och bricka
    t.rekt(x + 1, y, x + 9, y + 3, 1)
    t.rekt(x, y + 3, x + 10, y + 4, 0)
    t.rekt(x + 1, y, x + 9, y + 1, 2)
    t.px(x + 5, y + 1, 10)
    # Vänsterarm rakt ut åt vänster: STOPP
    t.rekt(x - 7, y + 10, x, y + 13, 2)
    t.rekt(x - 7, y + 10, x, y + 11, 3)
    t.rekt(x - 11, y + 8, x - 7, y + 13, 15)      # vit handske, handflatan ut
    t.rekt(x - 11, y + 7, x - 10, y + 8, 15)
    t.rekt(x - 9, y + 6, x - 8, y + 8, 15)
    t.px(x - 8, y + 12, 5)
    # Högerarmen viftar
    if vift == 0:
        t.linje(x + 10, y + 10, x + 15, y + 6, 2)
        t.linje(x + 10, y + 11, x + 15, y + 7, 2)
        t.linje(x + 10, y + 12, x + 15, y + 8, 2)
        t.rekt(x + 15, y + 3, x + 18, y + 8, 15)
    elif vift == 1:
        t.linje(x + 10, y + 10, x + 13, y + 2, 2)
        t.linje(x + 9, y + 10, x + 12, y + 2, 2)
        t.linje(x + 11, y + 10, x + 14, y + 2, 2)
        t.rekt(x + 12, y - 2, x + 16, y + 2, 15)
    else:
        t.rekt(x + 10, y + 10, x + 17, y + 13, 2)
        t.rekt(x + 10, y + 10, x + 17, y + 11, 3)
        t.rekt(x + 17, y + 9, x + 21, y + 13, 15)
        t.px(x + 21, y + 10, 15)
    kontur(d, t)


def mainst_v(v=None):
    v = v or {}
    regnfas = v.get("regn", 0)
    vift = v.get("vift", 0)
    rnd = random.Random(4101)
    d = Duk(1)

    # --- Himmel ---
    d.vgrad(0, 0, W, 50, [0, 0, 1, 1])

    # --- Tvärgatan mot norr mellan husen, med avlägsna hus ---
    for x0, b, topp in ((76, 10, 28), (85, 8, 36), (92, 9, 24), (100, 8, 34), (107, 9, 30)):
        d.rekt(x0, topp, x0 + b, 88, 1 + (x0 // 9) % 2)
        for wy in range(topp + 3, 80, 4):
            for wx in range(x0 + 2, x0 + b - 1, 3):
                if rnd.random() < 0.12:
                    d.rekt(wx, wy, wx + 2, wy + 2, 8)
    d.ljus(rektmask(76, 20, 116, 88), 0.35, MORKARE)
    d.poly([(84, 88), (108, 88), (100, 76), (92, 76)], 1)            # tvärgatan i perspektiv
    d.linje(96, 78, 96, 87, 3)
    d.rekt(93, 77, 95, 78, 11)                                        # avlägsna strålkastare
    d.rekt(97, 77, 99, 78, 11)
    d.radial(96, 77, 8, 0.5, mask=rektmask(84, 70, 108, 88))
    # Trafikljus på hörnet
    d.rekt(110, 54, 111, 88, 0)
    d.rekt(108, 46, 113, 56, 0)
    d.px(110, 48, 6)
    d.px(110, 51, 6)
    d.rekt(109, 53, 112, 55, 12)
    d.px(110, 53, 4)

    # --- Polishuset i grå sten ---
    sten(d, 0, 10, 80, 88, 3, 2, 4, 10, 0.25)
    d.rekt(0, 8, 80, 12, 4)                                           # takgesims
    d.rekt(0, 8, 80, 9, 5)
    for xx in range(1, 80, 4):
        d.rekt(xx, 12, xx + 2, 14, 4)
    d.rekt(4, 16, 76, 25, 2)                                          # fris med inhuggen text
    d.rekt(4, 16, 76, 17, 1)
    d.rekt(4, 24, 76, 25, 4)
    skriv(d, 40 - bredd("PRECINCT 9") // 2, 18, "PRECINCT 9", 4)
    d.rekt(0, 26, 80, 28, 4)
    d.rekt(0, 26, 80, 27, 5)
    # Fönster mellan kolonnerna (två våningar)
    for fx in (6, 64):
        fonster(d, fx, 32, 9, 12, fx == 6, ram=2)
        d.rekt(fx - 2, 30, fx + 11, 31, 4)
        d.rekt(fx - 1, 52, fx + 10, 70, 2)
        d.rekt(fx, 53, fx + 9, 69, 10 if fx == 64 else 1)
        if fx == 64:
            d.rekt(fx, 53, fx + 9, 55, 11)
            d.ljus(rektmask(fx, 60, fx + 9, 69), 0.5, MORKARE)
        for gx in range(fx + 1, fx + 9, 2):                           # galler
            d.rekt(gx, 53, gx + 1, 69, 0)
        d.rekt(fx - 2, 70, fx + 11, 72, 4)
        d.rekt(fx - 2, 70, fx + 11, 71, 5)
    d.radial(68, 61, 14, 0.4, mask=(YY > 50) & (YY < 88) & (d.a < 5))
    # Kolonner
    for kx in (22, 31, 46, 55):
        kolonn(d, kx, 32, 80, 4)
    d.rekt(20, 29, 61, 32, 5)
    d.rekt(20, 30, 61, 31, 4)

    # --- Entrén: dörr och trappa ---
    with d.yta("utgang:in"):
        d.rekt(34, 52, 46, 81, 0)
        _ellips(d, 34, 46, 45, 58, 0)
        _ellips(d, 35, 47, 44, 57, 10)                                # lysande överljus
        d.rekt(35, 52, 45, 54, 0)
        for k in range(3):
            d.linje(40, 53, 36 + k * 4, 48, 9)
        d.rekt(35, 54, 45, 81, 7)
        d.rekt(35, 54, 39, 81, 6)
        d.rekt(41, 54, 45, 81, 6)
        d.rekt(36, 56, 39, 66, 10)                                    # glasrutor med varmt ljus
        d.rekt(41, 56, 44, 66, 10)
        d.rekt(36, 56, 39, 57, 11)
        d.rekt(41, 56, 44, 57, 11)
        d.rekt(36, 70, 39, 79, 7)
        d.rekt(41, 70, 44, 79, 7)
        d.px(39, 68, 10)
        d.px(41, 68, 10)
        # Trappan
        for k, y in enumerate(range(81, 89, 2)):
            d.rekt(28 - k * 3, y, 52 + k * 3, y + 2, 4)
            d.rekt(28 - k * 3, y, 52 + k * 3, y + 1, 5)
    d.radial(40, 62, 20, 0.45, mask=(YY > 44) & (YY < 92) & (d.a < 9) & (XX > 22) & (XX < 60))

    # --- Den blå lyktan POLICE ---
    with d.yta("polisskylt"):
        d.rekt(39, 28, 41, 34, 0)                                     # konsol
        d.rekt(26, 33, 54, 35, 0)
        d.poly([(28, 33), (52, 33), (48, 30), (32, 30)], 1)            # tak
        d.rekt(32, 30, 48, 31, 3)
        d.rekt(39, 28, 41, 30, 0)
        d.rekt(26, 35, 54, 46, 0)
        d.vgrad(27, 36, 53, 45, [5, 5, 4])
        d.rekt(27, 44, 53, 45, 3)
        skriv(d, 40 - bredd("POLICE") // 2, 38, "POLICE", 1)
        d.rekt(30, 46, 50, 47, 0)
        d.rekt(39, 47, 41, 49, 0)
        d.px(40, 49, 5)
        # En duva sover på lyktans tak
        d.rekt(43, 27, 47, 30, 4)
        d.rekt(46, 26, 48, 28, 4)
        d.px(47, 27, 0)
        d.px(48, 27, 10)
        d.px(43, 29, 5)
    d.radial(40, 40, 22, 0.45, mask=(d.a < 4) & (YY < 60))

    # --- Banken ---
    sten(d, 114, 18, 182, 88, 4, 3, 4, 12, 0.3)
    d.poly([(112, 18), (184, 18), (148, 4)], 4)                       # tympanon
    d.poly([(117, 17), (179, 17), (148, 7)], 3)
    d.linje(112, 18, 148, 4, 5)
    d.linje(148, 4, 184, 18, 5)
    _ellips(d, 143, 9, 153, 16, 2)                                    # klocka i tympanon
    _ellips(d, 144, 10, 152, 15, 15)
    d.linje(148, 12, 148, 10, 0)
    d.linje(148, 12, 150, 13, 0)
    d.rekt(112, 18, 184, 21, 5)
    d.rekt(112, 20, 184, 21, 4)
    d.rekt(114, 21, 182, 33, 3)                                       # fris
    d.rekt(114, 32, 182, 33, 5)
    with d.yta("bank"):
        d.rekt(148 - bredd("BANK", 2) // 2 - 3, 22, 148 + bredd("BANK", 2) // 2 + 4, 33, 2)
        skriv_stor(d, 148 - bredd("BANK", 2) // 2 + 1, 23, "BANK", 11, 2)
        skriv_stor(d, 148 - bredd("BANK", 2) // 2, 22, "BANK", 10, 2)
    d.radial(148, 27, 26, 0.35, mask=(YY < 36) & (YY > 18) & (d.a < 5))
    d.markera("bank", 112, 4, 182, 88)
    for kx in (118, 130, 162, 174):
        kolonn(d, kx, 37, 84, 5, 5, 15, 4)
    d.rekt(114, 34, 182, 37, 5)
    d.rekt(114, 36, 182, 37, 4)
    # Bankfönster med galler
    for fx in (122, 166):
        d.rekt(fx - 1, 44, fx + 7, 74, 2)
        d.rekt(fx, 45, fx + 6, 73, 1)
        d.px(fx + 1, 46, 3)
        for gx in range(fx + 1, fx + 6, 2):
            d.rekt(gx, 45, gx + 1, 73, 4)
        d.rekt(fx, 58, fx + 6, 59, 4)
    # Mässingsdörrar
    d.rekt(140, 46, 157, 84, 2)
    d.rekt(141, 47, 156, 84, 9)
    d.rekt(141, 47, 156, 49, 10)
    d.rekt(148, 47, 149, 84, 7)
    for px_ in (143, 151):
        d.rekt(px_, 52, px_ + 4, 66, 8)
        d.rekt(px_, 70, px_ + 4, 82, 8)
        d.rekt(px_, 52, px_ + 4, 53, 10)
    d.rekt(146, 66, 148, 68, 11)
    d.rekt(149, 66, 151, 68, 11)
    d.ljus(rektmask(141, 47, 156, 84), 0.4, MORKARE)
    for k, y in enumerate(range(84, 89, 2)):
        d.rekt(136 - k * 2, y, 161 + k * 2, y + 2, 5)
        d.rekt(136 - k * 2, y + 1, 161 + k * 2, y + 2, 4)
    # Litet guldskylt: STÄNGT-tid
    d.rekt(158, 60, 161, 66, 10)
    d.px(159, 62, 7)
    d.px(159, 64, 7)

    # --- Gatan fortsätter österut ---
    d.rekt(182, 14, W, 88, 1)
    d.vgrad(182, 14, W, 88, [0, 1, 2])
    for wy in range(22, 80, 7):
        d.rekt(186, wy, 189, wy + 3, 9 if rnd.random() < 0.4 else 2)

    gatubas(d)
    # Tvärgatans korsning bryter trottoaren
    d.rekt(84, 88, 108, 99, 1)
    d.vgrad(84, 88, 108, 99, [1, 1, 0])
    for zx in range(86, 107, 4):                                      # övergångsställe
        d.rekt(zx, 92, zx + 2, 98, 4)
    d.rekt(0, 99, W, 100, 0)

    # Spegelreflexer i den våta gatan
    spegel(d, 26, 55, 0.6, 100, 3)          # den blå lyktan
    spegel(d, 140, 157, 0.35, 100, 3)
    spegel(d, 92, 100, 0.3, 100, 3)

    # --- Gatlyktor ---
    gatlykta(d, 78, 52, 92)
    gatlykta(d, 178, 52, 92)

    # --- Blå brevlåda på fot ---
    with d.yta("brevlada"):
        bx = 116
        d.rekt(bx + 1, 86, bx + 3, 94, 0)
        d.rekt(bx + 9, 86, bx + 11, 94, 0)
        d.rekt(bx, 93, bx + 4, 95, 0)
        d.rekt(bx + 8, 93, bx + 12, 95, 0)
        d.rekt(bx, 74, bx + 12, 87, 3)
        _ellips(d, bx, 69, bx + 11, 80, 3)
        d.rekt(bx, 74, bx + 1, 87, 4)
        d.rekt(bx + 11, 74, bx + 12, 87, 2)
        d.rekt(bx + 2, 75, bx + 10, 77, 0)                            # brevinkast
        d.rekt(bx + 2, 75, bx + 10, 76, 1)
        d.rekt(bx + 1, 80, bx + 11, 83, 15)                           # vit rand med röd linje
        d.rekt(bx + 1, 81, bx + 11, 82, 13)
        d.px(bx + 2, 71, 4)
        d.px(bx + 3, 70, 5)
    d.radial(122, 80, 10, 0.35, mask=(d.a == 3) & (YY < 90))

    # --- Trafikpolisen på sin pall ---
    with d.yta("trafikpolis"):
        _ellips(d, 85, 108, 107, 116, 0)
        d.rekt(86, 102, 106, 112, 15)
        for sx in range(86, 106, 6):                                  # röd-vita ränder
            d.rekt(sx, 102, sx + 3, 112, 13)
        d.ljus(rektmask(100, 102, 106, 112), 0.6, MORKARE)
        _ellips(d, 86, 107, 106, 116, 15)
        d.a[d.mask_ellips(86, 107, 106, 116) & (XX % 6 < 3)] = 13
        d.ljus(d.mask_ellips(86, 107, 106, 116) & (XX > 99), 0.6, MORKARE)
        _ellips(d, 86, 98, 106, 106, 5)
        _ellips(d, 88, 99, 104, 105, 4)
        trafikpolis(d, 91, 72, vift)
    d.markera("trafikpolis", 86, 72, 108, 114)

    # --- Pilskylten österut ---
    with d.yta("utgang:ö"):
        pilskylt(d, 186, 62, False)
    d.markera("utgang:ö", 182, 56, W, 100)

    regn(d, regnfas, 85, 21)
    d.vinjett(0.4)
    return d

# ======================================================================
#  POLISSTATIONENS HALL
# ======================================================================
def takflakt(d, cx, fas, y=6):
    """Takfläkt med fyra lägen på bladen."""
    d.rekt(cx - 1, 0, cx + 1, y, 0)
    _ellips(d, cx - 4, y - 1, cx + 4, y + 3, 7)
    blad = [[(cx - 20, y + 1), (cx + 20, y + 3)], [(cx - 14, y + 4), (cx + 14, y - 1)],
            [(cx - 6, y + 5), (cx + 8, y - 2)], [(cx + 14, y + 4), (cx - 14, y - 1)]][fas]
    for (bx, by) in blad:
        d.linje(cx, y + 1, bx, by, 8)
        d.linje(cx, y + 2, bx, by + 1, 6)
    d.rekt(cx - 1, y + 3, cx + 1, y + 6, 0)
    _ellips(d, cx - 4, y + 5, cx + 4, y + 10, 10)
    d.rekt(cx - 2, y + 9, cx + 2, y + 10, 11)


def polis(v=None):
    v = v or {}
    flakt = v.get("flakt", 0)
    zzz = v.get("zzz", 0)         # fyllbultens andning och zzz 0..3
    rnd = random.Random(4201)
    d = Duk(6)

    # --- Väggar: krämfärgad puts ovanför, grön panel nedtill ---
    d.rekt(0, 0, W, 64, 15)
    d.ljus(rektmask(0, 0, W, 64), 0.55, MORKARE)
    for _ in range(10):                                             # fuktfläckar
        sx, sy = rnd.randint(0, W - 10), rnd.randint(8, 50)
        d.ljus(d.mask_ellips(sx, sy, sx + rnd.randint(6, 14), sy + rnd.randint(4, 10)), 0.4, MORKARE)
    d.rekt(0, 0, W, 6, 6)
    d.rekt(0, 6, W, 7, 8)
    d.rekt(0, 62, W, 92, 12)
    d.rekt(0, 62, W, 64, 8)
    d.rekt(0, 62, W, 63, 9)
    for px_ in range(4, W, 14):
        d.rekt(px_, 67, px_ + 10, 88, 12)
        d.rekt(px_, 67, px_ + 10, 68, 6)
        d.rekt(px_, 67, px_ + 1, 88, 6)
    d.ljus(rektmask(0, 64, W, 92), 0.35, MORKARE)
    d.rekt(0, 88, W, 92, 6)
    d.rekt(0, 88, W, 89, 7)
    # Golv: rutigt linoleum i perspektiv
    for i, (y0, y1) in enumerate(((92, 96), (96, 101), (101, 107), (107, 113), (113, 120))):
        b = 8 + i * 2
        for k, xx in enumerate(range(-b, W + b, b)):
            off = (i % 2) * b // 2
            d.rekt(xx + off, y0, xx + off + b, y1, 3 if (k % 2) else 2)
    d.ljus(rektmask(0, 92, W, H), 0.35, MORKARE)

    # --- Väggklocka och en flagga ---
    _ellips(d, 140, 12, 154, 26, 6)
    _ellips(d, 141, 13, 153, 25, 15)
    d.linje(147, 19, 147, 14, 0)
    d.linje(147, 19, 151, 21, 0)
    d.px(147, 19, 13)

    # --- Entrédörren ut till gatan ---
    with d.yta("utgang:ut"):
        d.rekt(4, 22, 32, 92, 6)
        d.rekt(6, 24, 30, 92, 7)
        d.rekt(8, 26, 28, 54, 0)
        d.vgrad(9, 27, 27, 53, [1, 2, 3])
        regn_over(d, random.Random(9), 12, 0, 9, 27, 27, 53)
        d.rekt(9, 46, 27, 53, 1)                                    # gatlykta därute
        d.rekt(21, 33, 22, 53, 0)
        d.rekt(20, 30, 24, 33, 11)
        d.rekt(17, 27, 18, 53, 7)
        d.rekt(8, 56, 28, 70, 6)
        d.rekt(8, 56, 28, 57, 8)
        d.rekt(8, 74, 28, 88, 6)
        d.rekt(8, 74, 28, 75, 8)
        d.rekt(26, 70, 29, 73, 10)                                  # handtag
        # Röd EXIT-skylt över dörren
        d.rekt(8, 14, 28, 21, 0)
        d.rekt(9, 15, 27, 20, 13)
        skriv(d, 18 - bredd("EXIT") // 2, 15, "EXIT", 11)
    d.radial(18, 17, 12, 0.4, mask=(d.a == 15) | (d.a == 9) | (d.a == 6))

    # --- Anslagstavlan med efterlysningar ---
    with d.yta("efterlysningar"):
        d.rekt(38, 10, 88, 48, 6)
        d.rekt(39, 11, 87, 47, 8)
        d.a[rektmask(39, 11, 87, 47) & (TROSKEL < 0.35)] = 9
        # Stor WANTED-affisch
        d.rekt(41, 13, 70, 45, 15)
        d.ljus(rektmask(41, 13, 70, 45), 0.25, MORKARE)
        skriv(d, 56 - bredd("WANTED") // 2, 15, "WANTED", 0)
        d.rekt(48, 22, 63, 37, 9)                                   # skurkens porträtt
        d.rekt(49, 23, 62, 36, 15)
        _ellips(d, 51, 24, 60, 35, 9)
        d.rekt(50, 23, 61, 26, 0)                                   # hatt
        d.rekt(48, 26, 63, 27, 0)
        d.px(53, 29, 0)
        d.px(57, 29, 0)
        d.rekt(52, 28, 55, 29, 0)                                   # hopknipna ögonbryn
        d.rekt(56, 28, 59, 29, 0)
        d.rekt(53, 32, 58, 33, 0)
        d.linje(54, 33, 51, 35, 7)                                  # ärr
        d.rekt(51, 30, 52, 34, 8)
        skriv(d, 56 - bredd("$500") // 2, 39, "$500", 13)
        d.px(55, 14, 13)
        # Små lappar
        for (lx, ly, lb, lh) in ((73, 14, 12, 14), (72, 31, 13, 14)):
            d.rekt(lx, ly, lx + lb, ly + lh, 15)
            d.rekt(lx, ly + lh - 1, lx + lb, ly + lh, 9)
            for ry in range(ly + 3, ly + lh - 2, 2):
                d.rekt(lx + 2, ry, lx + lb - 2 - (ry % 3), ry + 1, 4)
            d.px(lx + lb // 2, ly + 1, 13)
        _ellips(d, 75, 17, 80, 22, 9)                               # liten bild på en hund
        d.px(76, 18, 0)
        d.px(79, 18, 0)
        skriv(d, 74, 23, "LOST", 13)

    # --- Bänken med den sovande fyllbulten ---
    d.rekt(36, 70, 92, 72, 7)                                       # ryggstöd
    d.rekt(36, 70, 92, 71, 8)
    d.rekt(36, 76, 92, 77, 7)
    for lx in (38, 64, 89):
        d.rekt(lx, 70, lx + 2, 82, 6)
    d.rekt(34, 82, 94, 85, 8)                                       # sits
    d.rekt(34, 82, 94, 83, 9)
    for lx in (36, 90):
        d.rekt(lx, 85, lx + 2, 96, 6)
    with d.yta("fyllo"):
        fx = 52
        andas = 1 if zzz in (1, 2) else 0
        # Ben utsträckta, skor på golvet
        d.rekt(fx + 8, 80, fx + 24, 85, 3)
        d.rekt(fx + 22, 85, fx + 26, 94, 3)
        d.rekt(fx + 17, 84, fx + 21, 94, 2)
        d.rekt(fx + 15, 93, fx + 22, 96, 0)
        d.rekt(fx + 22, 93, fx + 29, 96, 0)
        d.px(fx + 28, 93, 4)                                        # hål i sulan
        d.rekt(fx + 22, 90, fx + 26, 91, 15)                        # strumpa som hasat ner
        # Kroppen: sliten brun rock, magen höjer sig
        d.rekt(fx, 60 - andas, fx + 14, 84, 7)
        d.rekt(fx + 2, 66 - andas, fx + 15 + andas, 80, 8)
        d.rekt(fx, 60 - andas, fx + 2, 84, 6)
        d.rekt(fx + 6, 62, fx + 8, 70, 15)                          # skjortbröst
        d.rekt(fx + 7, 63, fx + 8, 70, 13)                          # lös slips
        d.px(fx + 10, 72, 10)
        d.rekt(fx + 4, 74, fx + 6, 76, 6)                           # lapp på rocken
        # Armen hänger ner med en flaska i papperspåse
        d.rekt(fx - 3, 66, fx + 1, 80, 7)
        d.rekt(fx - 4, 79, fx, 82, 10)
        d.rekt(fx - 5, 82, fx, 92, 9)
        d.rekt(fx - 5, 82, fx - 4, 92, 8)
        d.rekt(fx - 4, 79, fx - 1, 82, 12)                          # flaskhals
        d.px(fx - 3, 78, 12)
        # Huvudet lutat bakåt mot väggen, hatten över ögonen
        d.rekt(fx + 2, 52, fx + 12, 61, 10)
        d.rekt(fx + 3, 58, fx + 12, 61, 9)                          # skäggstubb
        d.a[rektmask(fx + 3, 58, fx + 12, 61) & (TROSKEL < 0.4)] = 3
        d.rekt(fx + 8, 56, fx + 11, 59, 13)                         # röd näsa
        d.px(fx + 9, 56, 14)
        d.rekt(fx + 5, 60, fx + 8, 61, 6 if andas else 0)           # öppen mun som snarkar
        d.rekt(fx - 1, 52, fx + 16, 55, 0)                          # hattbrätte
        d.rekt(fx - 1, 52, fx + 16, 53, 6)
        d.rekt(fx + 2, 45, fx + 13, 52, 6)
        d.rekt(fx + 2, 49, fx + 13, 50, 0)
        d.rekt(fx + 4, 45, fx + 9, 46, 7)
        d.px(fx + 12, 46, 6)                                        # buckla
        d.rekt(fx + 11, 44, fx + 13, 45, 15)                        # pantkvitto i bandet
    # Zzz
    zs = [(69, 50, 1), (73, 44, 1), (77, 34, 2)]
    for i, (zx, zy, sk) in enumerate(zs):
        if i <= zzz - 1 or (zzz == 0 and i == 0):
            skriv_stor(d, zx + 1, zy + 1, "Z", 0, sk)
            skriv_stor(d, zx, zy, "Z", 15, sk)

    # --- Den höga disken med sergeanten ---
    with d.yta("sergeant"):
        sx = 124
        # Kropp: blå uniform med axelklaffar, sergeantsvinklar
        _ellips(d, sx - 22, 38, sx + 22, 74, 2)
        d.rekt(sx - 22, 52, sx + 22, 62, 2)
        d.rekt(sx - 20, 46, sx - 15, 50, 3)                         # axelklaffar
        d.rekt(sx + 15, 46, sx + 20, 50, 3)
        d.ljus(d.mask_ellips(sx - 22, 38, sx + 22, 74) & (XX > sx + 8), 0.5, MORKARE)
        d.poly([(sx - 5, 42), (sx + 5, 42), (sx, 52)], 4)           # skjortkrage
        d.rekt(sx - 1, 44, sx + 1, 58, 0)                           # slips
        for by in (52, 56):
            d.px(sx - 4, by, 10)
            d.px(sx + 4, by, 10)
        d.rekt(sx - 12, 47, sx - 8, 50, 10)                         # bricka
        d.px(sx - 10, 48, 11)
        for k in range(3):                                          # sergeantsvinklar på armen
            d.linje(sx + 15, 52 + k * 2, sx + 18, 50 + k * 2, 10)
            d.linje(sx + 18, 50 + k * 2, sx + 21, 52 + k * 2, 10)
        # Huvud: tjockt och rött, dubbelhaka
        _ellips(d, sx - 10, 22, sx + 10, 46, 10)
        _ellips(d, sx - 9, 36, sx + 9, 47, 9)                       # dubbelhaka
        _ellips(d, sx - 8, 34, sx + 8, 44, 10)
        d.px(sx - 11, 32, 9)
        d.rekt(sx - 12, 30, sx - 10, 35, 9)                         # öron
        d.rekt(sx + 10, 30, sx + 12, 35, 9)
        d.rekt(sx - 7, 34, sx - 4, 36, 14)                          # röda kinder
        d.rekt(sx + 4, 34, sx + 7, 36, 14)
        d.px(sx - 4, 30, 0)                                         # små ögon
        d.px(sx + 3, 30, 0)
        d.rekt(sx - 6, 28, sx - 2, 29, 7)                           # buskiga ögonbryn
        d.rekt(sx + 2, 28, sx + 6, 29, 7)
        d.rekt(sx - 1, 30, sx + 1, 35, 9)                           # näsa
        d.px(sx, 34, 14)
        # Stor valrossmustasch
        d.rekt(sx - 6, 36, sx + 6, 38, 7)
        d.rekt(sx - 8, 37, sx - 5, 40, 7)
        d.rekt(sx + 5, 37, sx + 8, 40, 7)
        d.px(sx - 8, 40, 6)
        d.px(sx + 7, 40, 6)
        d.rekt(sx - 3, 38, sx + 3, 39, 6)
        # Polismössa
        d.rekt(sx - 10, 17, sx + 10, 24, 1)
        d.rekt(sx - 11, 16, sx + 11, 19, 2)
        d.rekt(sx - 11, 16, sx + 11, 17, 3)
        d.rekt(sx - 9, 24, sx + 9, 27, 0)                           # skärm
        d.rekt(sx - 8, 24, sx + 8, 25, 3)
        d.rekt(sx - 2, 19, sx + 2, 23, 10)
        d.px(sx, 20, 11)
        # Händer på disken, en munk i handen
        d.rekt(sx - 20, 58, sx - 12, 64, 10)
        d.rekt(sx + 12, 58, sx + 20, 64, 10)
        _ellips(d, sx + 14, 52, sx + 23, 60, 9)
        _ellips(d, sx + 15, 53, sx + 22, 59, 14)
        _ellips(d, sx + 17, 55, sx + 20, 58, 2)
        d.px(sx + 16, 54, 11)
        d.px(sx + 21, 56, 11)
    # Disken
    d.rekt(88, 62, 162, 100, 7)
    d.rekt(86, 60, 164, 65, 9)
    d.rekt(86, 60, 164, 61, 10)
    d.rekt(86, 65, 164, 66, 6)
    for px_ in range(92, 160, 17):
        d.rekt(px_, 70, px_ + 13, 94, 6)
        d.rekt(px_ + 1, 71, px_ + 13, 94, 8)
        d.rekt(px_ + 2, 72, px_ + 12, 93, 7)
    d.rekt(88, 96, 162, 100, 6)
    d.rekt(110, 74, 138, 82, 10)                                    # mässingsskylt
    d.rekt(111, 75, 137, 81, 9)
    skriv(d, 124 - bredd("DESK SGT") // 2, 76, "DESK SGT", 6)
    # Saker på disken: ringklocka, liggare, gröna lampan
    _ellips(d, 152, 54, 160, 61, 10)
    d.px(156, 53, 11)
    d.rekt(151, 60, 161, 61, 8)
    d.rekt(93, 51, 95, 60, 0)                                       # lampfot
    d.rekt(90, 59, 98, 61, 0)
    d.poly([(88, 52), (100, 52), (98, 47), (90, 47)], 12)
    d.rekt(89, 51, 99, 52, 11)
    d.radial(124, 62, 42, 0.45, mask=(YY > 58) & (YY < 100))
    d.radial(94, 52, 18, 0.35, mask=(YY > 59))

    # --- Kommissariens dörr ---
    with d.yta("utgang:in"):
        d.rekt(164, 22, 190, 92, 6)
        d.rekt(166, 24, 188, 92, 8)
        d.rekt(166, 24, 188, 25, 9)
        d.rekt(168, 27, 186, 56, 6)
        d.rekt(169, 28, 185, 55, 15)                                # frostat glas med ljus bakom
        d.vgrad(169, 28, 185, 55, [11, 15, 15, 9])
        # Skuggan av en bredaxlad man med cigarr bakom glaset
        _ellips(d, 172, 34, 180, 44, 9)
        d.a[d.mask_ellips(166, 42, 188, 64) & rektmask(169, 28, 185, 55)] = 9
        d.rekt(180, 39, 184, 40, 9)
        d.px(185, 38, 14)
        skriv(d, 177 - bredd("CHIEF") // 2, 47, "CHIEF", 0)
        d.rekt(168, 60, 186, 74, 7)
        d.rekt(168, 60, 186, 61, 9)
        d.rekt(168, 78, 186, 90, 7)
        d.rekt(168, 78, 186, 79, 9)
        d.rekt(168, 74, 171, 77, 10)                                # handtag
    d.radial(177, 40, 20, 0.35, mask=(YY < 64) & ((d.a == 6) | (d.a == 7) | (d.a == 15) | (d.a == 9)) & (XX > 150))

    # --- Spottkopp och papperskorg ---
    _ellips(d, 34, 92, 44, 98, 10)
    _ellips(d, 35, 92, 43, 95, 7)

    # --- Takfläkt och lampor ---
    takflakt(d, 76, flakt)
    d.radial(76, 18, 60, 0.4, mask=(YY > 14) & (XX < 100))
    d.rekt(123, 0, 125, 6, 0)

    d.vinjett(0.5)
    return d

# ======================================================================
#  KOMMISSARIENS KONTOR
# ======================================================================
ROK = {0: 1, 1: 2, 2: 3, 3: 4, 4: 5, 5: 5, 6: 3, 7: 4, 8: 4, 9: 5, 10: 15, 11: 11, 12: 4, 13: 14, 14: 14, 15: 11}


def rokpuff(d, cx, cy, r, styrka):
    """Rök eller ånga: gråblå dimma oavsett underlag."""
    puff = d.mask_ellips(cx - r * 1.3, cy - r, cx + r * 1.3, cy + r)
    d.ljus(puff, styrka, ROK)


def polis_kontor(v=None):
    v = v or {}
    rok = v.get("rok", 0)          # cigarröken 0..5
    anga = v.get("anga", 0)        # kaffeångan 0..3
    rnd = random.Random(4301)
    d = Duk(6)

    # --- Väggar: mörk tapet, träpanel nedtill ---
    d.vgrad(0, 0, W, 70, [0, 6, 7, 7])
    for x in range(3, W, 7):
        for y in range(2, 68, 3):
            if (x // 7 + y // 3) % 2 == 0:
                d.px(x, y, 6)
    d.rekt(0, 68, W, 100, 6)
    d.rekt(0, 68, W, 70, 8)
    d.rekt(0, 68, W, 69, 9)
    for px_ in range(2, W, 16):
        d.rekt(px_, 73, px_ + 12, 96, 7)
        d.rekt(px_, 73, px_ + 12, 74, 6)
    # Golv
    d.vgrad(0, 98, W, H, [6, 7, 6])
    for i in range(-10, 12):
        d.linje(96 + i * 7, 98, 96 + i * 22, H, 6)

    # --- Fönstret med persienner bakom skrivbordet ---
    fx0, fx1, fy0, fy1 = 64, 136, 6, 50
    d.rekt(fx0 - 3, fy0 - 3, fx1 + 3, fy1 + 4, 6)
    d.rekt(fx0 - 2, fy0 - 2, fx1 + 2, fy1 + 3, 8)
    d.vgrad(fx0, fy0, fx1, fy1, [0, 1, 1, 2])
    # Staden därute: silhuetter, upplysta fönster och en rosa neonglöd
    xx = fx0
    while xx < fx1:
        b = rnd.randint(6, 12)
        topp = rnd.randint(fy0 + 10, fy0 + 30)
        d.rekt(xx, topp, xx + b, fy1, 1 if (xx // 7) % 2 else 0)
        for wy in range(topp + 2, fy1, 3):
            for wx in range(xx + 1, xx + b - 1, 3):
                if rnd.random() < 0.25:
                    d.px(wx, wy, 10)
        xx += b
    d.radial(122, 40, 14, 0.6, tabell={**LJUSARE, 0: 13, 1: 13, 13: 14}, mask=rektmask(fx0, fy0, fx1, fy1) & (d.a < 2))
    # Persiennerna, halvöppna
    for y in range(fy0, fy1, 4):
        d.rekt(fx0, y, fx1, y + 2, 8)
        d.rekt(fx0, y, fx1, y + 1, 9)
    for sx in (fx0 + 18, fx1 - 18):
        d.rekt(sx, fy0, sx + 1, fy1, 15)                              # snören
    d.rekt(fx0 - 2, fy0 - 3, fx1 + 2, fy0 - 1, 9)
    d.rekt(fx1 - 6, fy0, fx1 - 5, fy1 + 10, 15)                       # dragsnöre
    d.rekt(fx1 - 7, fy1 + 10, fx1 - 4, fy1 + 12, 9)
    # Gatljuset faller in genom persiennerna i ränder på väggar och golv
    for k in range(0, 44, 4):
        rand = d.mask_poly([(fx0 - 4, fy0 + k), (fx0 - 4, fy0 + k + 2), (0, fy0 + k + 30), (0, fy0 + k + 27)])
        d.ljus(rand & (YY < 98), 0.45)
        rand = d.mask_poly([(fx1 + 4, fy0 + k), (fx1 + 4, fy0 + k + 2), (W, fy0 + k + 30), (W, fy0 + k + 27)])
        d.ljus(rand & (YY < 98), 0.45)

    # --- Stadskartan med nålar och snören ---
    with d.yta("stadskarta"):
        mx0, my0, mx1, my1 = 6, 8, 54, 40
        d.rekt(mx0 - 1, my0 - 1, mx1 + 1, my1 + 1, 0)
        d.rekt(mx0, my0, mx1, my1, 15)
        d.poly([(mx0, my1 - 9), (mx0 + 18, my1 - 6), (mx0 + 30, my1), (mx0, my1)], 4)   # hamnen
        d.poly([(mx1 - 10, my0), (mx1, my0), (mx1, my0 + 12)], 12)                       # parken
        for gx in range(mx0 + 4, mx1, 6):
            d.rekt(gx, my0, gx + 1, my1, 9)
        for gy in range(my0 + 4, my1, 5):
            d.rekt(mx0, gy, mx1, gy + 1, 9)
        d.linje(mx0, my0 + 26, mx1, my0 + 6, 13)                      # huvudgata
        nalar = [(14, 14), (26, 20), (44, 12), (36, 30), (20, 30), (48, 26)]
        for (ax, ay), (bx, by) in zip(nalar, nalar[1:] + nalar[:1]):
            if (ax, ay) != (48, 26):
                d.linje(ax, ay, bx, by, 13)
        d.linje(14, 14, 36, 30, 13)
        for (nx, ny) in nalar:
            d.rekt(nx - 1, ny - 1, nx + 1, ny + 1, 13 if nx != 44 else 10)
            d.px(nx - 1, ny - 1, 14)
        d.rekt(40, 33, 52, 38, 10)                                    # lapp med frågetecken
        d.px(45, 34, 0)
        d.px(46, 34, 0)
        d.px(47, 35, 0)
        d.px(46, 37, 0)
        d.ljus(rektmask(mx0, my0, mx1, my1), 0.3, MORKARE)

    # --- Arkivskåpet med kaffebryggaren ---
    d.rekt(6, 54, 32, 100, 3)
    d.rekt(6, 54, 32, 55, 4)
    d.rekt(30, 54, 32, 100, 2)
    for ly in (57, 72, 87):
        d.rekt(8, ly, 30, ly + 12, 2)
        d.rekt(9, ly + 1, 29, ly + 12, 3)
        d.rekt(15, ly + 3, 23, ly + 5, 15)
        d.rekt(17, ly + 7, 21, ly + 8, 5)
    d.rekt(9, 75, 29, 78, 15)                                         # en akt sticker ut
    d.rekt(26, 74, 29, 75, 13)
    with d.yta("kaffebryggare"):
        d.rekt(10, 51, 28, 54, 0)                                     # fot
        d.rekt(10, 36, 28, 40, 0)                                     # topp
        d.rekt(11, 36, 27, 37, 4)
        d.rekt(22, 40, 27, 51, 0)                                     # pelare
        d.rekt(23, 40, 24, 51, 3)
        _ellips(d, 10, 41, 22, 53, 5)                                 # glaskanna
        _ellips(d, 11, 45, 21, 53, 6)                                 # kaffe
        d.rekt(11, 45, 21, 46, 8)
        d.rekt(13, 40, 19, 43, 5)
        d.px(13, 46, 15)
        d.px(13, 47, 5)
        d.rekt(8, 46, 10, 50, 0)                                      # handtag
        d.rekt(25, 46, 27, 48, 13)                                    # röd lampa: på
        # Kaffekoppar med kaffe
        d.rekt(26, 49, 31, 54, 15)
        d.rekt(27, 49, 30, 50, 6)
    # Ånga från kaffet (loopar)
    for k in range(4):
        fas = (anga + k) % 4
        cy = 38 - fas * 5
        cx = 16 + [-1, 2, 0, 1][k] + (fas % 2)
        r = 2 + fas * 0.6
        rokpuff(d, cx, cy, r, 0.7 - fas * 0.13)

    # --- Dörren ut, med spegelvänd text på glaset ---
    with d.yta("utgang:ut"):
        d.rekt(160, 18, 190, 100, 6)
        d.rekt(162, 20, 188, 100, 7)
        d.rekt(164, 23, 186, 54, 6)
        d.rekt(165, 24, 185, 53, 3)
        d.vgrad(165, 24, 185, 53, [3, 4, 3])
        d.ljus(rektmask(165, 24, 185, 53) & (TROSKEL < 0.3), 0.6)
        skriv(d, 175 - bredd("CHIEF") // 2, 34, "CHIEF", 15, spegel=True)
        d.rekt(164, 58, 186, 74, 6)
        d.rekt(164, 58, 186, 59, 8)
        d.rekt(164, 78, 186, 96, 6)
        d.rekt(164, 78, 186, 79, 8)
        d.rekt(163, 72, 166, 75, 10)
        d.rekt(160, 98, 190, 100, 0)
    # Klädhängare med hatt och rock
    d.rekt(150, 24, 152, 100, 6)
    d.rekt(146, 98, 156, 100, 6)
    d.poly([(145, 32), (157, 32), (158, 66), (144, 66)], 9)           # trenchcoat
    d.linje(151, 32, 151, 66, 8)
    d.rekt(146, 46, 156, 48, 8)
    d.rekt(147, 24, 156, 28, 6)                                        # hatt
    d.rekt(145, 28, 158, 30, 6)
    d.rekt(147, 27, 156, 28, 13)
    d.ljus(d.mask_poly([(144, 24), (158, 24), (158, 66), (144, 66)]), 0.35, MORKARE)

    # --- Kommissarien O'Hara ---
    with d.yta("ohara"):
        ox = 100
        # Bred överkropp: skjorta med uppkavlade ärmar och hängslen
        d.poly([(ox - 30, 78), (ox - 26, 56), (ox - 16, 49), (ox + 16, 49), (ox + 26, 56), (ox + 30, 78)], 15)
        d.poly([(ox + 14, 49), (ox + 16, 49), (ox + 26, 56), (ox + 30, 78), (ox + 18, 78)], 9)
        d.linje(ox - 20, 60, ox - 18, 76, 9)                          # veck
        d.linje(ox + 17, 60, ox + 15, 76, 9)
        d.linje(ox - 10, 50, ox - 12, 78, 13)                         # hängslen
        d.linje(ox - 9, 50, ox - 11, 78, 13)
        d.linje(ox + 10, 50, ox + 12, 78, 13)
        d.linje(ox + 9, 50, ox + 11, 78, 13)
        # Uppknäppt krage och lös slips på sned
        d.poly([(ox - 6, 47), (ox, 54), (ox - 8, 52)], 15)
        d.poly([(ox + 6, 47), (ox, 54), (ox + 8, 52)], 15)
        d.rekt(ox - 1, 50, ox + 2, 54, 9)
        d.poly([(ox + 1, 54), (ox + 4, 54), (ox + 7, 68), (ox + 3, 70)], 12)
        d.linje(ox + 2, 56, ox + 5, 67, 10)
        d.rekt(ox, 52, ox + 4, 55, 12)
        # Armar: underarmarna vilar på skrivbordet
        d.rekt(ox - 34, 66, ox - 22, 76, 15)
        d.rekt(ox + 22, 66, ox + 34, 76, 9)
        d.rekt(ox - 34, 66, ox - 22, 68, 9)                           # uppkavlade ärmar
        d.rekt(ox + 22, 66, ox + 34, 68, 8)
        d.rekt(ox - 36, 72, ox - 20, 78, 10)                          # händer
        d.rekt(ox + 20, 72, ox + 36, 78, 9)
        d.rekt(ox - 36, 72, ox - 20, 73, 9)
        # Tjock hals och fyrkantigt huvud
        d.rekt(ox - 7, 42, ox + 7, 50, 9)
        d.rekt(ox - 11, 20, ox + 11, 44, 9)
        d.rekt(ox - 10, 20, ox + 10, 42, 10)
        d.rekt(ox - 11, 36, ox + 11, 44, 9)                           # käklinje
        d.a[rektmask(ox - 10, 37, ox + 10, 44) & (TROSKEL < 0.35)] = 7   # skäggstubb
        d.rekt(ox - 13, 28, ox - 10, 34, 9)                           # öron
        d.rekt(ox + 10, 28, ox + 13, 34, 9)
        # Grått bakåtkammat hår med tinningar
        d.rekt(ox - 11, 15, ox + 11, 22, 3)
        d.rekt(ox - 10, 14, ox + 9, 15, 3)
        d.rekt(ox - 12, 18, ox - 10, 28, 4)
        d.rekt(ox + 10, 18, ox + 12, 28, 4)
        for hx in range(ox - 9, ox + 10, 3):
            d.linje(hx, 15, hx + 2, 21, 2)
        d.linje(ox - 6, 15, ox - 4, 20, 4)
        d.rekt(ox - 10, 22, ox + 10, 23, 9)
        # Ansiktet: tunga ögonbryn, trötta ögon, stor näsa
        d.rekt(ox - 8, 25, ox - 2, 27, 0)
        d.rekt(ox + 2, 25, ox + 8, 27, 0)
        d.rekt(ox - 7, 28, ox - 3, 30, 15)
        d.rekt(ox + 3, 28, ox + 7, 30, 15)
        d.rekt(ox - 5, 28, ox - 3, 30, 0)
        d.rekt(ox + 3, 28, ox + 5, 30, 0)
        d.rekt(ox - 7, 28, ox - 3, 29, 9)                             # tunga ögonlock
        d.rekt(ox + 3, 28, ox + 7, 29, 9)
        d.rekt(ox - 7, 31, ox - 3, 32, 9)                             # påsar under ögonen
        d.rekt(ox + 3, 31, ox + 7, 32, 9)
        d.rekt(ox - 2, 28, ox + 2, 35, 9)
        d.rekt(ox - 2, 34, ox + 2, 35, 8)
        d.px(ox + 1, 33, 14)
        d.rekt(ox - 5, 38, ox + 4, 39, 7)                             # mun i mungipan
        # Cigarren
        d.rekt(ox + 3, 37, ox + 14, 40, 7)
        d.rekt(ox + 3, 37, ox + 14, 38, 8)
        d.rekt(ox + 6, 37, ox + 7, 40, 13)                            # band
        d.rekt(ox + 14, 37, ox + 16, 40, 4)                           # aska
        d.px(ox + 16, 38, 13)
        d.px(ox + 16, 39, 11)

    # --- Skrivbordet ---
    d.poly([(34, 76), (166, 76), (172, 84), (28, 84)], 8)
    d.linje(34, 76, 166, 76, 9)
    d.rekt(28, 84, 172, 87, 7)
    d.rekt(28, 84, 172, 85, 9)
    d.rekt(32, 87, 168, 112, 7)
    for px_ in (36, 128):
        d.rekt(px_, 90, px_ + 36, 108, 6)
        d.rekt(px_ + 1, 91, px_ + 36, 108, 8)
        d.rekt(px_ + 2, 92, px_ + 35, 107, 7)
        d.rekt(px_ + 16, 98, px_ + 20, 100, 10)
    d.rekt(72, 90, 128, 112, 6)
    d.rekt(32, 110, 168, 112, 6)
    # Namnskylt
    d.rekt(87, 77, 113, 85, 6)
    d.rekt(88, 77, 112, 84, 10)
    d.rekt(88, 77, 112, 78, 11)
    skriv(d, 100 - bredd("O'HARA") // 2, 79, "O'HARA", 6)
    # Askkopp full av fimpar och en telefon
    _ellips(d, 132, 77, 146, 82, 4)
    _ellips(d, 134, 78, 144, 81, 1)
    for (fx_, fy_) in ((136, 78), (139, 79), (142, 78), (138, 77)):
        d.rekt(fx_, fy_, fx_ + 3, fy_ + 1, 15)
        d.px(fx_, fy_, 9)
    d.rekt(150, 74, 162, 80, 0)
    d.rekt(149, 71, 163, 74, 0)
    d.rekt(149, 71, 163, 72, 2)
    _ellips(d, 153, 75, 159, 79, 2)
    d.px(156, 77, 15)

    # --- Högar med akter ---
    with d.yta("akter"):
        for i in range(8):
            y = 76 - i * 3
            off = rnd.randint(-2, 2)
            c = [9, 15, 8, 9, 13, 15, 9, 8][i]
            d.rekt(38 + off, y - 3, 62 + off, y, c)
            d.rekt(38 + off, y - 1, 62 + off, y, MORKARE[c])
            d.rekt(60 + off, y - 3, 62 + off, y - 2, 15)
        d.rekt(40, 50, 58, 52, 15)                                    # översta akten öppen
        d.rekt(40, 50, 49, 51, 9)
        d.linje(42, 51, 47, 51, 4)
        for i in range(4):
            y = 76 - i * 3
            c = [15, 9, 13, 8][i]
            d.rekt(118 + i, y - 3, 132 + i, y, c)
            d.rekt(118 + i, y - 1, 132 + i, y, MORKARE[c])
        d.rekt(121, 62, 127, 64, 13)                                  # stämpel: BRÅDSKANDE
    # Kaffekopp med ring på en akt
    d.rekt(66, 70, 72, 76, 15)
    d.rekt(67, 70, 71, 71, 6)
    d.rekt(72, 72, 73, 74, 15)

    # --- Skrivbordslampa ---
    d.rekt(165, 66, 167, 77, 10)
    d.rekt(162, 76, 170, 78, 9)
    d.poly([(158, 66), (172, 66), (170, 61), (160, 61)], 12)
    d.rekt(159, 65, 171, 66, 11)
    d.radial(140, 80, 50, 0.5, mask=(YY > 64) & (YY < 110))

    # --- Cigarrök som slingrar uppåt och ligger som en dimma i taket ---
    d.ljus(rektmask(0, 0, W, 14) & ((XX // 3 + YY // 2) % 5 == 0), 0.6, ROK)
    for k in range(6):
        fas = (rok + k) % 6
        cy = 34 - fas * 5
        cx = 117 + 4 * math.sin(fas * 1.1 + k * 0.3) + fas * 2
        r = 1.5 + fas * 0.9
        rokpuff(d, cx, cy, r, 0.75 - fas * 0.1)
    d.ljus(d.mask_ellips(100, -4, 170, 10), 0.3, ROK)

    d.vinjett(0.55)
    return d

# ======================================================================
#  MAIN STREET, ÖSTRA DELEN: HOTEL MAJESTIC OCH BIOGRAFEN RIALTO
# ======================================================================
def taxi(d, x, y):
    """Gul taxi i profil, nosen åt vänster. (x, y) = takets övre vänstra hörn ungefär."""
    t = Duk(16)
    t.poly([(x + 10, y), (x + 30, y), (x + 36, y + 7), (x + 6, y + 7)], 10)       # kupé
    t.rekt(x - 2, y + 7, x + 46, y + 16, 10)                                    # kaross
    t.poly([(x - 2, y + 7), (x + 6, y + 6), (x + 6, y + 8), (x - 3, y + 9)], 10)
    t.rekt(x - 3, y + 9, x + 46, y + 11, 10)
    t.rekt(x - 2, y + 7, x + 46, y + 8, 11)
    t.rekt(x - 3, y + 15, x + 47, y + 17, 15)                                   # krom
    t.rekt(x - 3, y + 16, x + 47, y + 17, 4)
    t.rekt(x + 11, y + 1, x + 19, y + 6, 1)                                     # rutor
    t.rekt(x + 21, y + 1, x + 29, y + 6, 1)
    t.poly([(x + 9, y + 6), (x + 11, y + 1), (x + 11, y + 6)], 1)
    t.poly([(x + 29, y + 1), (x + 34, y + 6), (x + 29, y + 6)], 1)
    t.px(x + 12, y + 2, 4)
    t.px(x + 22, y + 2, 4)
    t.rekt(x + 15, y + 2, x + 17, y + 6, 0)                                     # passagerare? nej, chauffören
    t.rekt(x + 14, y + 1, x + 18, y + 3, 0)
    t.rekt(x + 20, y + 7, x + 21, y + 15, 9)                                    # dörrspringa
    t.rekt(x + 23, y + 9, x + 26, y + 10, 15)                                   # handtag
    # Rutigt band
    for cx in range(x + 2, x + 44, 2):
        t.px(cx, y + 12, 0 if (cx // 2) % 2 else 15)
        t.px(cx + 1, y + 13, 0 if (cx // 2) % 2 else 15)
    t.rekt(x + 16, y - 3, x + 24, y, 15)                                        # taxiskylt
    t.rekt(x + 17, y - 2, x + 23, y - 1, 10)
    t.rekt(x - 3, y + 8, x, y + 11, 11)                                         # strålkastare
    t.rekt(x + 44, y + 9, x + 47, y + 11, 13)                                   # baklykta
    # Hjul med skärmar
    for hx in (x + 6, x + 36):
        t.rekt(hx - 5, y + 13, hx + 6, y + 15, 9)
        _ellips(t, hx - 4, y + 13, hx + 5, y + 22, 0)
        _ellips(t, hx - 2, y + 15, hx + 3, y + 20, 15)
        _ellips(t, hx - 1, y + 16, hx + 2, y + 19, 4)
    kontur(d, t)


def mainst_o(v=None):
    v = v or {}
    regnfas = v.get("regn", 0)
    neon = v.get("neon", 6)          # HOTEL tänds bokstav för bokstav: 0 släckt, 1..5 bokstäver, 6 allt + blink
    lampor = v.get("lampor", 0)      # markisens jagande glödlampor 0..2
    rnd = random.Random(4401)
    d = Duk(1)

    d.vgrad(0, 0, W, 40, [0, 0, 1, 1])

    # --- Gatan fortsätter västerut ---
    d.rekt(0, 16, 12, 88, 1)
    d.vgrad(0, 16, 12, 88, [2, 1, 0])
    for wy in range(22, 80, 7):
        d.rekt(3, wy, 6, wy + 3, 9 if rnd.random() < 0.4 else 2)

    # --- Hotel Majestic: hög art deco-fasad i tegel och sten ---
    hx0, hx1 = 12, 102
    d.rekt(hx0, 0, hx1, 88, 7)
    d.ljus(rektmask(hx0, 0, hx1, 88), 0.5, MORKARE)
    for y in range(1, 88, 3):
        off = 0 if (y // 3) % 2 else 3
        for xx in range(hx0 + off, hx1, 6):
            d.px(xx, y, 6)
    for px_ in (hx0, hx0 + 30, hx0 + 60, hx1 - 4):                     # stenlisener
        d.rekt(px_, 0, px_ + 4, 88, 3)
        d.rekt(px_, 0, px_ + 1, 88, 4)
        d.rekt(px_ + 3, 0, px_ + 4, 88, 2)
    for wy in (4, 20, 36):
        for wx in (hx0 + 7, hx0 + 18, hx0 + 37, hx0 + 48, hx0 + 67, hx0 + 78):
            fonster(d, wx, wy, 6, 10, rnd.random() < 0.5, ram=2)
    d.rekt(hx0, 50, hx1, 54, 4)                                        # gesims
    d.rekt(hx0, 50, hx1, 51, 5)
    for xx in range(hx0, hx1, 4):
        d.rekt(xx, 54, xx + 2, 55, 3)
    # Skyltfönster med palmer och varmt ljus
    for (wx, wb) in ((hx0 + 3, 16), (hx0 + 72, 14)):
        d.rekt(wx - 1, 65, wx + wb + 1, 88, 2)
        d.rekt(wx, 66, wx + wb, 86, 10)
        d.vgrad(wx, 66, wx + wb, 86, [11, 10, 9])
        d.rekt(wx + wb // 2, 74, wx + wb // 2 + 1, 86, 7)
        for k in range(-3, 4):
            d.linje(wx + wb // 2, 74, wx + wb // 2 + k * 2, 70 + abs(k), 12)
        d.rekt(wx + wb // 2 - 2, 83, wx + wb // 2 + 3, 86, 13)
        d.rekt(wx, 86, wx + wb, 88, 4)
    d.radial(hx0 + 10, 76, 18, 0.45, mask=(YY > 62) & (YY < 100) & (d.a < 9))
    d.radial(hx0 + 79, 76, 18, 0.45, mask=(YY > 62) & (YY < 100) & (d.a < 9))

    # --- Roterdörren i mässing (utgång in) ---
    with d.yta("utgang:in"):
        dx0, dx1 = 38, 70
        d.rekt(dx0, 66, dx1, 88, 9)
        d.rekt(dx0 + 1, 67, dx1 - 1, 88, 10)
        d.rekt(dx0 + 2, 68, dx1 - 2, 87, 11)
        d.vgrad(dx0 + 2, 68, dx1 - 2, 87, [11, 10, 10, 9])
        _ellips(d, dx0 + 4, 64, dx1 - 4, 70, 9)                        # trumman
        d.rekt(dx0 + 4, 66, dx1 - 4, 68, 8)
        for bx, c in ((dx0 + 8, 8), (dx0 + 16, 9), (dx0 + 23, 8)):      # vingar
            d.rekt(bx, 68, bx + 1, 87, c)
        d.rekt(dx0 + 9, 76, dx0 + 15, 77, 9)
        d.rekt(dx0 + 17, 76, dx0 + 22, 77, 9)
        d.rekt(dx0, 87, dx1, 88, 8)
        d.rekt(dx0 + 4, 87, dx1 - 4, 89, 13)                           # röd matta ut över trottoaren
        d.poly([(dx0 + 4, 88), (dx1 - 4, 88), (dx1 - 1, 96), (dx0 + 1, 96)], 13)
        d.ljus(d.mask_poly([(dx0 + 4, 88), (dx1 - 4, 88), (dx1 - 1, 96), (dx0 + 1, 96)]), 0.35, MORKARE)
    d.radial(54, 78, 24, 0.4, mask=(YY > 60) & (YY < 98) & ((d.a < 9) | (d.a == 13)))

    # --- Baldakinen ---
    d.poly([(30, 59), (70, 59), (75, 67), (25, 67)], 13)
    d.rekt(25, 66, 75, 68, 6)
    for sx in range(27, 74, 4):
        d.px(sx, 67, 10)
    d.linje(30, 59, 70, 59, 14)
    skriv(d, 50 - bredd("MAJESTIC") // 2, 61, "MAJESTIC", 10)
    for px_ in (26, 73):                                                # mässingsstänger till kantstenen
        d.rekt(px_, 67, px_ + 1, 95, 9)
        d.px(px_, 67, 11)

    # --- Den lodräta neonskylten HOTEL ---
    with d.yta("hotellneon"):
        sx0, sx1, sy0 = 86, 100, 4
        d.rekt(83, 10, sx0, 11, 0)                                     # konsoler
        d.rekt(83, 40, sx0, 41, 0)
        d.rekt(sx0, sy0, sx1, sy0 + 62, 0)
        d.rekt(sx0 + 1, sy0 + 1, sx1 - 1, sy0 + 61, 1)
        d.rekt(sx0 + 1, sy0 + 1, sx1 - 1, sy0 + 2, 13)
        d.rekt(sx0 + 1, sy0 + 60, sx1 - 1, sy0 + 61, 13)
        for i, ch in enumerate("HOTEL"):
            tand = (i < neon) if neon <= 5 else True
            ly = sy0 + 4 + i * 11
            if tand:
                skriv_stor(d, sx0 + 2, ly, ch, 13, 2)
                skriv_stor(d, sx0 + 2, ly, ch, 14, 2)
                g = _glyf(ch)
                for ry, rad in enumerate(g):
                    for rx, bit in enumerate(rad):
                        if bit == "1":
                            d.px(sx0 + 2 + rx * 2, ly + ry * 2, 11)
            else:
                skriv_stor(d, sx0 + 2, ly, ch, 2, 2)
        d.rekt(sx0 + 6, sy0 + 62, sx0 + 8, sy0 + 66, 0)
    if neon >= 5:
        n = 5
        d.radial(93, 4 + n * 6, 16 + n * 4, 0.55, tabell={**LJUSARE, 0: 13, 1: 13, 2: 13, 6: 13, 7: 13, 13: 14},
                 mask=(d.a < 8) & ~rektmask(86, 4, 100, 66) & (YY < 88))
    # --- Hotellportiern ---
    with d.yta("hotellportier"):
        px0 = 76
        d.rekt(px0 + 1, 82, px0 + 4, 92, 0)                            # byxor
        d.rekt(px0 + 5, 82, px0 + 8, 92, 0)
        d.rekt(px0 + 2, 82, px0 + 3, 92, 10)                            # guldrand
        d.rekt(px0, 91, px0 + 4, 93, 0)
        d.rekt(px0 + 5, 91, px0 + 9, 93, 0)
        d.rekt(px0, 70, px0 + 9, 84, 13)                                # röd uniformsrock
        d.rekt(px0 + 7, 70, px0 + 9, 84, 6)
        for by in (72, 75, 78, 81):
            d.px(px0 + 3, by, 10)
            d.px(px0 + 5, by, 10)
        d.rekt(px0, 70, px0 + 9, 71, 10)                                # epåletter
        d.rekt(px0 - 1, 70, px0 + 1, 72, 10)
        d.rekt(px0 + 8, 70, px0 + 10, 72, 10)
        d.rekt(px0 - 1, 72, px0 + 1, 82, 13)                            # arm som håller i paraply
        d.rekt(px0 - 2, 81, px0 + 1, 83, 15)
        d.rekt(px0 + 2, 64, px0 + 8, 70, 10)                            # ansikte
        d.px(px0 + 3, 66, 0)
        d.px(px0 + 6, 66, 0)
        d.rekt(px0 + 3, 68, px0 + 7, 69, 7)                             # mustasch
        d.rekt(px0 + 1, 59, px0 + 9, 64, 13)                            # mössa
        d.rekt(px0, 63, px0 + 10, 64, 0)
        d.rekt(px0 + 1, 61, px0 + 9, 62, 10)
        d.px(px0 + 5, 60, 11)
        # Hopfällt paraply han håller
        d.rekt(px0 - 2, 72, px0 - 1, 95, 0)
        d.poly([(px0 - 4, 92), (px0 - 1, 76), (px0 + 1, 92)], 2)
        d.rekt(px0 - 4, 70, px0 - 1, 72, 8)
    d.markera("hotellportier", 72, 58, 87, 94)

    # --- Biografen Rialto ---
    bx0, bx1 = 104, 180
    d.rekt(bx0, 0, bx1, 88, 3)
    d.ljus(rektmask(bx0, 0, bx1, 88), 0.4, MORKARE)
    for xx in range(bx0 + 4, bx1, 8):                                  # art deco-ränder
        d.rekt(xx, 0, xx + 2, 46, 2)
        d.rekt(xx, 0, xx + 1, 46, 4)
    d.poly([(bx0, 10), (142, 0), (bx1, 10), (bx1, 14), (142, 4), (bx0, 14)], 4)
    # Vertikal RIALTO-skylt ovanför markisen? Nej: kronan
    d.rekt(122, 14, 162, 30, 0)
    d.rekt(123, 15, 161, 29, 1)
    for k in range(3):
        d.poly([(126 + k * 12, 15), (132 + k * 12, 10), (138 + k * 12, 15)], 10)
    skriv_stor(d, 142 - bredd("RIALTO", 2) // 2, 17, "RIALTO", 13, 2)
    skriv_stor(d, 142 - bredd("RIALTO", 2) // 2, 17, "RIALTO", 14, 2)
    d.radial(142, 22, 26, 0.5, tabell={**LJUSARE, 0: 13, 1: 13, 2: 13, 3: 13, 13: 14}, mask=(YY < 46) & (d.a < 4) & ~rektmask(122, 14, 162, 30))
    # Affischskåp på fasaden
    for (ax, motiv) in ((108, 0), (166, 1)):
        d.rekt(ax - 1, 60, ax + 11, 84, 10)
        d.rekt(ax, 61, ax + 10, 83, 1)
        if motiv == 0:
            d.rekt(ax, 61, ax + 10, 83, 12)
            _ellips(d, ax + 2, 64, ax + 8, 72, 4)
            d.rekt(ax + 3, 72, ax + 7, 80, 4)
            d.px(ax + 4, 67, 13)
            d.px(ax + 6, 67, 13)
        else:
            d.rekt(ax, 61, ax + 10, 83, 13)
            _ellips(d, ax + 2, 64, ax + 6, 69, 10)
            _ellips(d, ax + 5, 65, ax + 9, 70, 10)
            d.rekt(ax + 3, 74, ax + 8, 78, 14)
            d.px(ax + 5, 76, 11)
    # Entrén: glasdörrar mot den upplysta foajén
    with d.yta("utgang:n"):
        ex0, ex1 = 122, 162
        d.rekt(ex0, 64, ex1, 88, 0)
        d.rekt(ex0 + 1, 65, ex1 - 1, 88, 10)
        d.vgrad(ex0 + 1, 65, ex1 - 1, 88, [11, 10, 13, 13])
        for xx in range(ex0 + 1, ex1, 10):
            d.rekt(xx, 65, xx + 1, 88, 9)
        for xx in range(ex0 + 4, ex1 - 2, 10):
            d.rekt(xx, 76, xx + 4, 77, 9)
        # Biljettluckan i mitten
        d.poly([(136, 88), (136, 70), (142, 66), (148, 70), (148, 88)], 9)
        d.poly([(137, 88), (137, 71), (142, 67), (147, 71), (147, 88)], 13)
        d.rekt(138, 72, 146, 78, 11)
        d.rekt(140, 75, 144, 78, 10)
        d.rekt(141, 73, 143, 75, 9)
        d.rekt(136, 80, 148, 81, 10)
        d.rekt(ex0 - 2, 87, ex1 + 2, 89, 4)
    d.radial(142, 80, 30, 0.5, mask=(YY > 62) & (YY < 104) & ((d.a < 9) | (d.a == 13)) & (XX > 100) & (XX < 184))

    # --- Markisen med jagande glödlampor ---
    with d.yta("biomarkis"):
        mx0, mx1, my0, my1 = 108, 176, 40, 62
        d.poly([(mx0, my1), (mx0 + 4, my0), (mx1 - 4, my0), (mx1, my1)], 0)
        d.rekt(mx0 + 1, my0 + 3, mx1 - 1, my1 - 1, 2)
        d.rekt(mx0 + 6, my0 + 4, mx1 - 6, my1 - 4, 15)                 # textfältet
        d.ljus(rektmask(mx0 + 6, my0 + 4, mx1 - 6, my1 - 4) & (YY > my1 - 9), 0.25, MORKARE)
        skriv(d, 142 - bredd("NOW SHOWING") // 2, my0 + 5, "NOW SHOWING", 13)
        skriv(d, 142 - bredd("THE GIANT APE") // 2, my0 + 12, "THE GIANT APE", 0)
        d.rekt(mx0, my1 - 1, mx1, my1 + 2, 9)
        d.rekt(mx0, my1, mx1, my1 + 1, 10)
        # Glödlampor runt kanten
        kant = []
        for xx in range(mx0 + 3, mx1 - 2, 3):
            kant.append((xx, my0 + 1))
        for yy in range(my0 + 4, my1 - 2, 3):
            kant.append((mx1 - 3, yy))
        for xx in range(mx1 - 4, mx0 + 2, -3):
            kant.append((xx, my1 - 2))
        for yy in range(my1 - 5, my0 + 3, -3):
            kant.append((mx0 + 2, yy))
        for i, (lx, ly) in enumerate(kant):
            d.px(lx, ly, 11 if (i + lampor) % 3 else 9)
    d.radial(142, 64, 40, 0.5, mask=(YY > 61) & (YY < 100) & ((d.a < 5) | (d.a == 7)))
    d.radial(142, 51, 40, 0.3, mask=(YY < 40) & (YY > 28) & (d.a < 4))

    # --- Grannhuset till höger ---
    d.rekt(180, 0, W, 88, 1)
    for wy in range(6, 80, 9):
        fonster(d, 184, wy, 5, 6, rnd.random() < 0.3, gardin=False, ram=0)

    gatubas(d)

    # Spegelreflexer i den våta gatan: neon, markis och hotell
    for (x0, x1, f) in ((86, 100, 0.6), (114, 170, 0.45), (40, 68, 0.4)):
        spegel(d, x0, x1, f, 100, 2)
    d.ljus(rektmask(86, 100, 100, H) & ((XX + YY) % 3 == 0), 0.5,
           {**LJUSARE, 0: 13, 1: 13, 2: 14, 13: 14})

    gatlykta(d, 106, 54, 92)

    # --- Den gula taxin vid trottoaren ---
    with d.yta("taxi2"):
        taxi(d, 18, 94)
    d.markera("taxi2", 15, 90, 64, 116)
    spegel(d, 14, 64, 0.2, 113, 2)

    # --- Pilskylten västerut ---
    with d.yta("utgang:v"):
        pilskylt(d, 6, 60, True)
    d.markera("utgang:v", 0, 56, 12, 92)

    regn(d, regnfas, 85, 23)
    d.vinjett(0.4)
    return d

# ======================================================================
#  BIOGRAFEN RIALTOS FOAJÉ
# ======================================================================
def bio(v=None):
    v = v or {}
    pop = v.get("pop", 0)            # popcornen poppar 0..3
    slinga = v.get("slinga", 0)      # ljusslingans jagande lampor 0..2
    rnd = random.Random(4501)
    d = Duk(6)

    # --- Väggar: mörkröd sammetstapet med guldlister ---
    d.rekt(0, 0, W, 90, 13)
    d.ljus(rektmask(0, 0, W, 90), 0.7, MORKARE)
    for x in range(0, W, 6):                                         # damastmönster
        for y in range(18, 86, 8):
            oy = (x // 6) % 2 * 4
            d.px(x + 3, y + oy, 13)
            d.px(x + 2, y + oy + 1, 6)
            d.px(x + 4, y + oy + 1, 6)
    d.rekt(0, 0, W, 16, 0)                                           # tak
    d.rekt(0, 15, W, 18, 9)
    d.rekt(0, 15, W, 16, 10)
    d.rekt(0, 17, W, 18, 6)
    d.rekt(0, 78, W, 90, 6)                                          # bröstpanel
    d.rekt(0, 78, W, 80, 9)
    d.rekt(0, 78, W, 79, 10)
    for px_ in range(4, W, 12):
        d.rekt(px_, 82, px_ + 8, 88, 7)
    # Golv: röd heltäckningsmatta med guldmönster
    d.vgrad(0, 90, W, H, [6, 13, 13, 6])
    d.ljus(rektmask(0, 90, W, H), 0.45, MORKARE)
    for i, y in enumerate(range(93, H, 6)):
        for x in range((i % 2) * 8, W, 16):
            d.px(x, y, 9)
            d.px(x - 1, y + 1, 9)
            d.px(x + 1, y + 1, 9)
            d.px(x, y + 2, 9)
    d.rekt(0, 90, W, 91, 0)
    # Popcorn på mattan
    for _ in range(9):
        d.px(rnd.randint(130, 186), rnd.randint(98, 118), 15)

    # --- Ljusslingan i taket ---
    for i, x in enumerate(range(0, W, 4)):
        y = 9 + int(3 * math.sin(x / 24 * math.pi) ** 2)
        d.px(x, y - 1, 2)
        d.px(x + 1, y - 1, 2)
        if i % 2 == 0:
            tand = (i // 2 + slinga) % 3 != 0
            d.px(x, y, 11 if tand else 8)
            d.px(x, y + 1, 10 if tand else 7)
            if tand:
                d.px(x - 1, y, 9)
                d.px(x + 1, y, 9)

    # --- Ytterdörrar ut till gatan ---
    with d.yta("utgang:ut"):
        d.rekt(2, 24, 36, 90, 9)
        d.rekt(3, 25, 35, 90, 10)
        for dx in (5, 20):
            d.rekt(dx, 27, dx + 13, 89, 8)
            d.rekt(dx + 1, 28, dx + 12, 78, 1)
            d.vgrad(dx + 1, 28, dx + 12, 78, [1, 2, 2, 3])
            regn_over(d, random.Random(dx), 8, 0, dx + 1, 28, dx + 12, 78)
            d.rekt(dx + 1, 72, dx + 12, 78, 2)
            d.px(dx + 2, 29, 4)
            d.rekt(dx + 1, 60, dx + 12, 62, 10)                      # mässingsräcke
            d.rekt(dx + 1, 60, dx + 12, 61, 11)
        d.rekt(18, 27, 20, 89, 9)
        d.rekt(6, 18, 32, 24, 0)                                     # EXIT-skylt
        d.rekt(7, 19, 31, 23, 13)
        skriv(d, 19 - bredd("EXIT") // 2, 19, "EXIT", 11)
        # Neonreflex från gatan i glaset
        d.ljus(rektmask(6, 64, 18, 72) & ((XX + YY) % 2 == 0), 0.7, {**LJUSARE, 1: 13, 2: 14, 3: 14})

    # --- Biljettluckan med galler ---
    with d.yta("biljettlucka"):
        d.rekt(40, 26, 74, 90, 9)
        d.rekt(41, 27, 73, 90, 7)
        d.rekt(40, 26, 74, 34, 6)
        d.rekt(41, 27, 73, 33, 0)
        skriv(d, 57 - bredd("TICKETS") // 2, 28, "TICKETS", 10)
        d.rekt(44, 38, 70, 64, 6)                                    # luckan
        d.rekt(45, 39, 69, 63, 10)
        d.vgrad(45, 39, 69, 63, [11, 10, 9])
        # Kassörskans silhuett bakom gallret: knut i håret, läser en tidning
        _ellips(d, 50, 42, 58, 50, 6)
        _ellips(d, 52, 40, 56, 44, 6)
        d.rekt(49, 50, 59, 60, 6)
        d.rekt(56, 50, 66, 58, 15)
        d.rekt(61, 50, 62, 58, 9)
        for gy in range(52, 57, 2):
            d.rekt(57, gy, 60, gy + 1, 4)
        for gx in range(45, 70, 3):                                  # mässingsgaller
            d.rekt(gx, 39, gx + 1, 63, 9)
        _ellips(d, 52, 54, 62, 66, 6)                                # talhål och myntränna
        d.rekt(50, 62, 64, 66, 9)
        d.rekt(51, 63, 63, 65, 0)
        d.rekt(42, 66, 72, 69, 10)                                   # disk
        d.rekt(42, 66, 72, 67, 11)
        d.rekt(44, 72, 70, 88, 6)
        d.rekt(45, 73, 69, 87, 8)
        d.rekt(54, 76, 60, 84, 10)                                   # emblem
        d.px(57, 80, 13)
        d.rekt(64, 64, 68, 66, 15)                                   # en biljettrulle
        d.px(66, 65, 13)
    d.radial(57, 52, 22, 0.4, mask=(d.a < 10) & ~rektmask(44, 38, 70, 64) & (YY < 92))

    # --- Inramade filmaffischer ---
    with d.yta("filmaffischer"):
        # Monsterfilmen
        ax0, ay0 = 77, 24
        d.rekt(ax0 - 2, ay0 - 2, ax0 + 18, ay0 + 34, 10)
        d.rekt(ax0 - 1, ay0 - 1, ax0 + 17, ay0 + 33, 9)
        d.vgrad(ax0, ay0, ax0 + 16, ay0 + 32, [1, 12, 12, 0])
        for (bx, bh) in ((ax0, 10), (ax0 + 3, 14), (ax0 + 11, 9), (ax0 + 13, 12)):   # skyskrapor
            d.rekt(bx, ay0 + 32 - bh, bx + 3, ay0 + 32, 0)
        _ellips(d, ax0 + 3, ay0 + 3, ax0 + 13, ay0 + 13, 7)          # apans huvud
        _ellips(d, ax0 + 5, ay0 + 7, ax0 + 11, ay0 + 13, 8)
        d.px(ax0 + 6, ay0 + 7, 13)
        d.px(ax0 + 10, ay0 + 7, 13)
        d.rekt(ax0 + 6, ay0 + 10, ax0 + 11, ay0 + 12, 0)              # gapet
        d.px(ax0 + 7, ay0 + 10, 15)
        d.px(ax0 + 10, ay0 + 10, 15)
        d.rekt(ax0 + 2, ay0 + 13, ax0 + 14, ay0 + 24, 7)             # kropp och armar
        d.rekt(ax0, ay0 + 12, ax0 + 2, ay0 + 18, 7)
        d.rekt(ax0 + 14, ay0 + 10, ax0 + 16, ay0 + 16, 7)
        d.rekt(ax0 + 13, ay0 + 9, ax0 + 16, ay0 + 11, 15)            # damen i handen
        d.px(ax0 + 14, ay0 + 8, 10)
        d.rekt(ax0, ay0 + 25, ax0 + 16, ay0 + 32, 13)
        skriv(d, ax0 + 8 - bredd("APE") // 2, ay0 + 26, "APE", 11)
        # Kärleksfilmen
        bx0, by0 = 99, 24
        d.rekt(bx0 - 2, by0 - 2, bx0 + 18, by0 + 34, 10)
        d.rekt(bx0 - 1, by0 - 1, bx0 + 17, by0 + 33, 9)
        d.vgrad(bx0, by0, bx0 + 16, by0 + 32, [14, 13, 13, 6])
        _ellips(d, bx0 + 1, by0 + 6, bx0 + 8, by0 + 14, 10)          # två profiler som kysser
        _ellips(d, bx0 + 8, by0 + 6, bx0 + 15, by0 + 14, 10)
        d.rekt(bx0 + 1, by0 + 4, bx0 + 7, by0 + 8, 0)                # hans hår
        d.rekt(bx0 + 9, by0 + 4, bx0 + 16, by0 + 9, 9)               # hennes hår
        d.rekt(bx0 + 14, by0 + 8, bx0 + 16, by0 + 16, 9)
        d.px(bx0 + 8, by0 + 11, 13)
        d.rekt(bx0 + 2, by0 + 14, bx0 + 7, by0 + 22, 1)
        d.rekt(bx0 + 9, by0 + 14, bx0 + 15, by0 + 22, 15)
        for (hx, hy) in ((bx0 + 3, by0 + 1), (bx0 + 11, by0 + 1)):   # hjärtan
            d.px(hx, hy, 11)
            d.px(hx + 2, hy, 11)
            d.rekt(hx, hy + 1, hx + 3, hy + 2, 11)
            d.px(hx + 1, hy + 2, 11)
        d.rekt(bx0, by0 + 25, bx0 + 16, by0 + 32, 6)
        skriv(d, bx0 + 8 - bredd("KISS") // 2, by0 + 26, "KISS", 14)
    for (lx) in (85, 107):                                           # små lampor över ramarna
        d.rekt(lx - 2, 19, lx + 3, 21, 10)
        d.radial(lx, 30, 16, 0.3, mask=(YY > 20) & (YY < 60))

    # --- Salongsdörrarna med draperier ---
    d.rekt(122, 22, 156, 90, 6)
    d.rekt(124, 26, 154, 90, 0)
    d.rekt(122, 22, 156, 26, 10)
    d.rekt(122, 22, 156, 23, 11)
    for dx in (125, 140):
        d.rekt(dx, 28, dx + 14, 90, 13)
        d.ljus(rektmask(dx, 28, dx + 14, 90), 0.4, MORKARE)
        for ky in range(32, 88, 6):                                  # knappad sammetsdyna
            for kx in range(dx + 2, dx + 13, 5):
                d.px(kx, ky, 10)
    # Draperier i guldkantad röd sammet
    for (cx0, cx1, rikt) in ((118, 128, 1), (151, 160, -1)):
        d.poly([(cx0, 20), (cx1, 20), (cx1 if rikt > 0 else cx0 + 4, 92), (cx0 if rikt > 0 else cx0, 92)] if False else
               [(cx0, 20), (cx1, 20), ((cx0 + cx1) // 2 + rikt * 2, 60), (cx1 - 2 if rikt < 0 else cx0 + 2, 92), (cx0 if rikt > 0 else cx1, 92)], 13)
        for fx in range(cx0 + 2, cx1, 3):
            d.linje(fx, 20, fx + rikt, 90, 6)
        d.rekt(cx0, 58, cx1, 61, 10)                                 # guldsnodd
        d.rekt(cx0, 20, cx1, 22, 10)
    # Sammetsrep på mässingsstolpar
    for sx in (104, 120):
        d.rekt(sx, 74, sx + 2, 94, 10)
        d.rekt(sx - 1, 93, sx + 3, 95, 9)
        _ellips(d, sx - 1, 71, sx + 3, 75, 11)
    for k in range(13):
        t = k / 12
        d.px(int(106 + t * 14), int(78 + 4 * math.sin(t * math.pi)), 13)
        d.px(int(106 + t * 14), int(79 + 4 * math.sin(t * math.pi)), 6)

    # --- Vaktmästaren som river biljetter ---
    with d.yta("vaktmastare"):
        vx = 139
        d.rekt(vx - 5, 80, vx - 1, 95, 1)                            # byxor med röd rand
        d.rekt(vx + 1, 80, vx + 5, 95, 1)
        d.rekt(vx - 4, 80, vx - 3, 95, 13)
        d.rekt(vx + 3, 80, vx + 4, 95, 13)
        d.rekt(vx - 6, 94, vx - 1, 97, 0)
        d.rekt(vx + 1, 94, vx + 6, 97, 0)
        d.rekt(vx - 7, 60, vx + 7, 82, 2)                            # uniformsjacka
        d.rekt(vx - 7, 60, vx - 6, 82, 3)
        d.rekt(vx + 5, 60, vx + 7, 82, 1)
        for by in (63, 67, 71, 75, 79):                              # mässingsknappar i två rader
            d.px(vx - 2, by, 11)
            d.px(vx + 2, by, 10)
        d.rekt(vx - 8, 60, vx - 4, 62, 10)                           # epåletter med frans
        d.rekt(vx + 4, 60, vx + 8, 62, 10)
        for fx in range(vx - 8, vx - 4, 2):
            d.px(fx, 62, 9)
        for fx in range(vx + 4, vx + 8, 2):
            d.px(fx, 62, 9)
        d.rekt(vx - 7, 76, vx + 7, 77, 10)                           # guldsnodd i midjan
        # Armar framför sig: river en biljett mitt itu
        d.rekt(vx - 10, 62, vx - 7, 72, 2)
        d.rekt(vx + 7, 62, vx + 10, 72, 2)
        d.rekt(vx - 10, 70, vx - 4, 73, 2)
        d.rekt(vx + 4, 70, vx + 10, 73, 2)
        d.rekt(vx - 5, 69, vx - 2, 73, 15)                           # vita handskar
        d.rekt(vx + 2, 69, vx + 5, 73, 15)
        d.poly([(vx - 3, 66), (vx, 67), (vx - 1, 71), (vx - 4, 70)], 10)   # biljetthalvor
        d.poly([(vx, 67), (vx + 3, 65), (vx + 4, 69), (vx + 1, 71)], 10)
        d.px(vx - 2, 68, 13)
        d.px(vx + 2, 67, 13)
        # Huvud: ung, uttråkad, fräknar
        d.rekt(vx - 2, 56, vx + 2, 60, 9)                            # hals
        d.rekt(vx - 5, 45, vx + 5, 57, 10)
        d.rekt(vx - 5, 55, vx + 5, 57, 9)
        d.rekt(vx - 6, 49, vx - 5, 53, 9)
        d.rekt(vx + 5, 49, vx + 6, 53, 9)
        d.rekt(vx - 4, 50, vx - 1, 51, 15)                           # halvslutna ögon
        d.rekt(vx + 1, 50, vx + 4, 51, 15)
        d.px(vx - 2, 50, 0)
        d.px(vx + 2, 50, 0)
        d.rekt(vx - 4, 49, vx - 1, 50, 9)
        d.rekt(vx + 1, 49, vx + 4, 50, 9)
        for (fx, fy) in ((vx - 3, 53), (vx - 4, 52), (vx + 3, 53), (vx + 4, 52)):
            d.px(fx, fy, 8)
        d.rekt(vx - 2, 55, vx + 2, 56, 7)                            # snett munläge
        d.px(vx + 2, 54, 7)
        d.rekt(vx - 5, 44, vx + 5, 46, 7)                            # hårlugg
        # Pillboxmössa på sned med hakband
        d.rekt(vx - 4, 39, vx + 5, 45, 2)
        d.rekt(vx - 4, 43, vx + 5, 45, 10)
        d.rekt(vx - 4, 39, vx + 5, 40, 3)
        d.px(vx, 41, 11)
        d.linje(vx - 5, 46, vx - 3, 56, 0)
    d.radial(139, 60, 26, 0.2, mask=(YY > 36) & (YY < 98) & ~((d.a == 13) | (d.a == 6)))

    # --- Popcornmaskinen ---
    with d.yta("popcornmaskin"):
        px0, px1 = 161, 190
        # Vagnen
        d.rekt(px0 + 1, 72, px1 - 1, 92, 13)
        d.rekt(px0 + 1, 72, px1 - 1, 74, 10)
        d.rekt(px1 - 4, 74, px1 - 1, 92, 6)
        d.rekt(px0 + 4, 77, px1 - 6, 88, 6)
        d.rekt(px0 + 5, 78, px1 - 7, 87, 13)
        skriv(d, (px0 + px1) // 2 - bredd("5$") // 2 - 1, 80, "5", 11)
        skriv(d, (px0 + px1) // 2 + 1, 80, "C", 11)
        for wx in (px0 + 4, px1 - 6):                                # hjul
            _ellips(d, wx - 3, 89, wx + 3, 95, 0)
            _ellips(d, wx - 1, 91, wx + 1, 93, 10)
        # Glasskåpet
        d.rekt(px0, 42, px1, 72, 10)
        d.rekt(px0 + 1, 43, px1 - 1, 71, 1)
        d.vgrad(px0 + 1, 43, px1 - 1, 71, [2, 1, 1, 10])
        # Högen med popcorn i botten
        for _ in range(140):
            hx = rnd.randint(px0 + 1, px1 - 2)
            hy = rnd.randint(60, 70)
            if hy > 70 - (6 - abs(hx - (px0 + px1) // 2) * 6 // 16) * 2 + 1:
                d.px(hx, hy, rnd.choice([15, 15, 11, 10]))
        d.rekt(px0 + 1, 66, px1 - 1, 71, 15)
        for hx in range(px0 + 1, px1 - 1):
            d.px(hx, 65 - (hx * 7 % 3), 15 if hx % 2 else 11)
            d.px(hx, 66, 10 if hx % 3 == 0 else 15)
        # Kitteln som hänger i taket
        d.rekt(175, 43, 176, 47, 4)
        _ellips(d, 170, 46, 181, 55, 4)
        d.rekt(170, 46, 181, 50, 4)
        _ellips(d, 170, 45, 181, 49, 5)
        d.rekt(170, 46, 181, 47, 15)
        d.rekt(181, 48, 185, 50, 9)
        # Glasreflex
        d.rekt(px0 + 2, 44, px0 + 3, 62, 5)
        d.px(px0 + 4, 45, 5)
        d.rekt(px0 + 15, 42, px0 + 16, 72, 10)
        # Toppen med skylt
        d.rekt(px0 - 1, 32, px1 + 1, 42, 13)
        d.rekt(px0 - 1, 32, px1 + 1, 33, 14)
        d.rekt(px0 - 1, 41, px1 + 1, 42, 10)
        skriv(d, (px0 + px1) // 2 - bredd("POPCORN") // 2, 35, "POPCORN", 11)
        d.poly([(px0 + 4, 32), (px1 - 4, 32), ((px0 + px1) // 2, 27)], 10)
        d.px((px0 + px1) // 2, 26, 11)
    # Popcorn som poppar ur kitteln (loopar)
    korn = [((171, 52), (167, 47), (165, 57)), ((180, 52), (185, 46), (187, 58)),
            ((173, 50), (171, 44), (168, 52)), ((178, 50), (181, 44), (184, 53))]
    for i, bana in enumerate(korn):
        steg = (pop + i) % 4
        if steg < 3:
            x_, y_ = bana[steg]
            d.px(x_, y_, 15)
            d.px(x_ + 1, y_, 11)
            d.px(x_, y_ + 1, 11)
    d.radial(173, 60, 22, 0.4, mask=(YY > 40) & (YY < 100) & ((d.a < 9) | (d.a == 13)) & ~rektmask(161, 42, 190, 72))

    d.vinjett(0.5)
    return d


SCENER_A = {
    "mainst_v": (mainst_v, [
        ("regn", "regn", [(i, 90) for i in range(10)]),
        ("vift", "vift", [(0, 380), (1, 320), (0, 380), (2, 320), (0, 600), (1, 320), (2, 300)]),
    ]),
    "polis": (polis, [
        ("flakt", "flakt", [(i, 110) for i in range(4)]),
        ("zzz", "zzz", [(0, 700), (1, 600), (2, 600), (3, 900)]),
    ]),
    "polis_kontor": (polis_kontor, [
        ("rok", "rok", [(i, 260) for i in range(6)]),
        ("anga", "anga", [(i, 220) for i in range(4)]),
    ]),
    "mainst_o": (mainst_o, [
        ("regn", "regn", [(i, 90) for i in range(10)]),
        ("neon", "neon", [(0, 500), (1, 220), (2, 220), (3, 220), (4, 220), (5, 1800), (0, 140), (6, 140), (0, 140), (6, 2400)]),
        ("lampor", "lampor", [(i, 160) for i in range(3)]),
    ]),
    "bio": (bio, [
        ("pop", "pop", [(i, 140) for i in range(4)]),
        ("slinga", "slinga", [(i, 240) for i in range(3)]),
    ]),
}
