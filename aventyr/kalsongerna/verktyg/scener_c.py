import math, random, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "motor" / "verktyg"))
from pixelbild import *  # noqa

"""Scener C: stadsparkens entré, dammen, musikpaviljongen och fyren längst ut på piren."""

# ======================================================================
#  EGNA TECKEN (utöver motorns TYPSNITT) och hjälpfunktioner
# ======================================================================
EXTRA_C = {
    "J": ["001", "001", "001", "101", "010"],
    "X": ["101", "101", "010", "101", "101"],
    "Ä": ["101", "010", "101", "111", "101"],
    "Ö": ["101", "010", "101", "101", "010"],
    "2": ["110", "001", "010", "100", "111"],
    "4": ["101", "101", "111", "001", "001"],
    "5": ["111", "100", "110", "001", "110"],
    "0": ["010", "101", "101", "101", "010"],
    "7": ["111", "001", "010", "010", "010"],
    ".": ["0", "0", "0", "0", "1"],
    "-": ["00", "00", "11", "00", "00"],
    "<": ["001", "010", "100", "010", "001"],
    ">": ["100", "010", "001", "010", "100"],
}


def _glyf(ch):
    if ch in ("Å", "É"):
        return TYPSNITT["A" if ch == "Å" else "E"]
    return EXTRA_C.get(ch) or TYPSNITT[ch]


def skriv(d, x, y, s, c):
    """Som text() men med extratecknen. Å och É får ring/accent ovanför."""
    for ch in s:
        g = _glyf(ch)
        for ry, rad in enumerate(g):
            for rx, bit in enumerate(rad):
                if bit == "1":
                    d.px(x + rx, y + ry, c)
        if ch == "Å":
            d.px(x + 1, y - 2, c)
        if ch == "É":
            d.px(x + 2, y - 2, c)
        x += len(g[0]) + 1


def bredd(s):
    return sum(len(_glyf(ch)[0]) + 1 for ch in s) - 1


def fyll(d, x0, y0, x1, y1, c):
    d.a[d.mask_ellips(x0, y0, x1, y1)] = c


def ring(d, x0, y0, x1, y1, c, tjock=1):
    m = d.mask_ellips(x0, y0, x1, y1) & ~d.mask_ellips(x0 + tjock, y0 + tjock, x1 - tjock, y1 - tjock)
    d.a[m] = c


def kontur(d, t, c=0):
    """Kopierar det som ritats på hjälpduken t (bakgrund 16) till d med mörk kontur runt."""
    m = t.a != 16
    kant = m.copy()
    kant[1:, :] |= m[:-1, :]
    kant[:-1, :] |= m[1:, :]
    kant[:, 1:] |= m[:, :-1]
    kant[:, :-1] |= m[:, 1:]
    d.a[kant & ~m] = c
    d.a[m] = t.a[m]


def regn(d, fas, antal=80, fro=7, **kw):
    regn_over(d, random.Random(fro), antal, fas, **kw)


def pil(d, x, y, riktning, c):
    """Pil 7 x 5 (v, h) eller 5 x 7 (u, n) med spetsen åt riktning."""
    if riktning == "v":
        d.rekt(x + 2, y + 2, x + 7, y + 3, c)
        for k in range(3):
            d.rekt(x + k, y + 2 - k, x + k + 1, y + 3 + k, c)
    elif riktning == "h":
        d.rekt(x, y + 2, x + 5, y + 3, c)
        for k in range(3):
            d.rekt(x + 6 - k, y + 2 - k, x + 7 - k, y + 3 + k, c)
    elif riktning == "u":
        d.rekt(x + 2, y + 2, x + 3, y + 7, c)
        for k in range(3):
            d.rekt(x + 2 - k, y + k, x + 3 + k, y + k + 1, c)
    else:
        d.rekt(x + 2, y, x + 3, y + 5, c)
        for k in range(3):
            d.rekt(x + 2 - k, y + 6 - k, x + 3 + k, y + 7 - k, c)


def vagskylt(d, cx, y, s, riktning, ybas, pilfoerst=False, bg=12, fg=15):
    """Grön parkskylt med text och pil på en svart stolpe. cx = stolpens x, y = skyltens överkant."""
    d.rekt(cx, y, cx + 2, ybas, 0)
    d.rekt(cx - 1, ybas - 2, cx + 3, ybas, 0)
    lodrat = riktning in ("u", "n")
    pb = 5 if lodrat else 7
    b = bredd(s) + pb + 3
    x0 = cx + 1 - (b + 6) // 2
    x1 = x0 + b + 6
    hy = 11
    ty = y + 3
    d.rekt(x0 - 1, y - 1, x1 + 1, y + hy + 1, 0)
    d.rekt(x0, y, x1, y + hy, 15)
    d.rekt(x0 + 1, y + 1, x1 - 1, y + hy - 1, bg)
    if pilfoerst:
        pil(d, x0 + 3, y + (2 if lodrat else 3), riktning, fg)
        skriv(d, x0 + 6 + pb, ty, s, fg)
    else:
        skriv(d, x0 + 3, ty, s, fg)
        pil(d, x1 - 3 - pb, y + (2 if lodrat else 3), riktning, fg)
    return x0 - 1, x1 + 1


def kalt_trad(d, x, y, langd, vinkel, djup, rnd, c=0):
    """Kalt träd: grenar rekursivt."""
    if djup == 0 or langd < 2:
        return
    x2 = x + langd * math.cos(vinkel)
    y2 = y - langd * math.sin(vinkel)
    d.linje(int(x), int(y), int(x2), int(y2), c)
    if djup >= 4:
        d.linje(int(x) + 1, int(y), int(x2) + 1, int(y2), c)
    for _ in range(2 if djup > 1 else 3):
        kalt_trad(d, x2, y2, langd * rnd.uniform(0.62, 0.78),
                  vinkel + rnd.uniform(-0.65, 0.65), djup - 1, rnd, c)


def stam(d, x, ybot, ytop, b, c=0):
    d.rekt(x, ytop, x + b, ybot, c)
    d.rekt(x - 1, ybot - 2, x + b + 1, ybot, c)


def parklykta(d, x, ytop, ybas, glod=0.55):
    """Parklykta med glob i smide."""
    d.rekt(x, ytop, x + 2, ybas, 0)
    d.rekt(x - 1, ybas - 4, x + 3, ybas, 0)
    d.rekt(x - 1, ytop + 6, x + 3, ytop + 7, 0)
    fyll(d, x - 3, ytop - 9, x + 5, ytop - 1, 10)
    fyll(d, x - 2, ytop - 8, x + 3, ytop - 3, 11)
    d.rekt(x - 1, ytop - 11, x + 3, ytop - 9, 0)
    d.px(x + 1, ytop - 12, 0)
    d.rekt(x - 1, ytop - 1, x + 3, ytop, 0)
    d.radial(x + 1, ytop - 5, 26, glod, mask=(d.a < 10))


def vattenspegel(d, x0, x1, y0, y1, styrka):
    for y in range(y0, y1):
        s = styrka * (1 - (y - y0) / max(1, (y1 - y0)))
        m = (XX >= x0) & (XX < x1) & (YY == y) & ((XX + y) % 2 == 0)
        d.ljus(m, s * 2)


def gras(d, x0, y0, x1, y1, rnd, tät=0.08):
    """Mörkt vått gräs med små strån."""
    d.vgrad(x0, y0, x1, y1, [1, 12, 12])
    d.ljus(d.mask_poly([(x0, y0), (x1, y0), (x1, y1), (x0, y1)]), 0.45, MORKARE)
    for _ in range(int((x1 - x0) * (y1 - y0) * tät)):
        gx, gy = rnd.randint(x0, x1 - 1), rnd.randint(y0, y1 - 1)
        d.px(gx, gy, 12 if rnd.random() < 0.7 else 0)


# ======================================================================
#  STADSPARKEN – ENTRÉN
# ======================================================================
def _general(d):
    """Generalen till häst i ärgig brons, med en duva på huvudet. Ritas med kontur."""
    t = Duk(16)
    # Hästen (står, nosen åt höger)
    t.a[t.mask_ellips(26, 37, 58, 53)] = 7                 # bål
    t.a[t.mask_ellips(28, 38, 56, 46)] = 8
    t.poly([(50, 42), (56, 28), (61, 26), (62, 33), (57, 46)], 7)   # hals
    t.linje(53, 40, 57, 29, 8)
    t.poly([(58, 24), (64, 22), (70, 30), (68, 33), (63, 31), (60, 32)], 7)   # huvud
    t.linje(59, 25, 64, 23, 8)
    t.px(63, 26, 0)
    t.px(68, 31, 0)
    t.rekt(58, 21, 60, 24, 7)                              # öra
    t.linje(51, 30, 57, 23, 6)                             # man
    t.linje(52, 31, 58, 24, 6)
    # Ben: vänster fram lyft
    for (bx, lyft) in ((30, 0), (35, 0), (49, 0)):
        t.rekt(bx, 50, bx + 3, 63, 7)
        t.rekt(bx - 1, 62, bx + 3, 64, 6)
    t.poly([(53, 48), (57, 48), (62, 55), (60, 57), (55, 52)], 7)
    t.poly([(60, 55), (62, 54), (62, 60), (60, 60)], 7)
    t.rekt(59, 59, 63, 61, 6)
    # Svans
    t.poly([(27, 41), (22, 46), (20, 56), (23, 57), (25, 48), (29, 44)], 6)
    # Ryttaren: rock, ridstövel, epålett, sabel i luften
    t.poly([(38, 42), (48, 42), (47, 48), (39, 48)], 2)            # sadelfilt
    t.rekt(39, 47, 47, 48, 10)
    t.rekt(41, 40, 46, 53, 7)                              # ben/stövel
    t.rekt(41, 50, 47, 54, 6)
    t.poly([(38, 26), (47, 26), (48, 42), (37, 42)], 8)    # rocken
    t.linje(38, 27, 37, 41, 9)
    t.rekt(42, 28, 43, 41, 7)
    t.rekt(37, 34, 48, 35, 6)                              # bälte
    t.rekt(36, 25, 40, 27, 10)                             # epåletter
    t.rekt(45, 25, 49, 27, 10)
    t.rekt(40, 22, 45, 26, 7)                              # hals
    t.a[t.mask_ellips(39, 15, 46, 23)] = 8                 # huvud
    t.px(45, 18, 0)
    t.rekt(44, 20, 47, 21, 6)                              # mustasch
    t.rekt(46, 18, 47, 20, 9)
    t.poly([(37, 16), (48, 16), (46, 11), (39, 11)], 6)    # bicorne-hatt
    t.linje(37, 16, 48, 16, 7)
    t.rekt(41, 9, 43, 12, 13)                              # plym
    # Sabelarmen
    for off in range(2):
        t.linje(47, 27 + off, 53, 19 + off, 8)
    t.rekt(52, 17, 55, 20, 8)
    t.linje(54, 17, 62, 3, 5)
    t.linje(55, 17, 63, 3, 4)
    t.rekt(51, 17, 56, 18, 10)
    # Andra handen håller tyglarna
    t.linje(40, 34, 58, 30, 6)
    # Ärg i ränder
    for (gx, gy, n) in ((31, 44, 6), (44, 30, 8), (54, 32, 6), (37, 50, 7), (64, 25, 4), (50, 51, 8)):
        t.rekt(gx, gy, gx + 1, gy + n, 12)
    # Duvan på hatten
    t.a[t.mask_ellips(39, 6, 46, 11)] = 4
    t.rekt(44, 4, 47, 8, 4)
    t.px(46, 5, 0)
    t.px(47, 6, 10)
    t.rekt(38, 7, 40, 9, 3)
    t.rekt(41, 8, 44, 9, 5)
    for (sx, sy) in ((40, 12), (42, 13), (38, 17), (46, 13), (41, 24)):
        t.px(sx, sy, 15)
    kontur(d, t)


def _kastanjeman(d, rok):
    # Vagnen
    vx, vy = 146, 88
    d.rekt(vx, vy, vx + 40, vy + 18, 7)
    d.rekt(vx, vy, vx + 40, vy + 2, 9)
    d.rekt(vx, vy + 16, vx + 40, vy + 18, 6)
    for px_ in range(vx + 3, vx + 38, 6):
        d.rekt(px_, vy + 3, px_ + 1, vy + 16, 6)
    d.rekt(vx + 2, vy + 5, vx + 38, vy + 12, 13)
    d.rekt(vx + 2, vy + 5, vx + 38, vy + 6, 14)
    skriv(d, vx + 3, vy + 6, "CHESTNUTS", 15)
    # Hjul
    for hx in (vx + 4, vx + 26):
        ring(d, hx, vy + 12, hx + 12, vy + 24, 0, 2)
        d.linje(hx + 6, vy + 13, hx + 6, vy + 23, 0)
        d.linje(hx + 1, vy + 18, hx + 11, vy + 18, 0)
        d.px(hx + 6, vy + 18, 9)
        d.px(hx + 3, vy + 13, 8)
    # Handtag
    d.linje(vx + 40, vy + 4, vx + 48, vy + 2, 0)
    # Glödpanna och skorsten ovanpå
    d.rekt(vx + 8, vy - 6, vx + 28, vy, 0)
    d.rekt(vx + 9, vy - 5, vx + 27, vy - 1, 6)
    for kx in range(vx + 10, vx + 27, 3):
        d.px(kx, vy - 4, 13)
        d.px(kx + 1, vy - 3, 10)
        d.px(kx, vy - 2, 14)
    for kx in (vx + 11, vx + 16, vx + 21, vx + 25):        # kastanjer
        d.rekt(kx, vy - 7, kx + 2, vy - 5, 7)
        d.px(kx, vy - 7, 9)
    d.rekt(vx + 1, vy - 18, vx + 5, vy, 0)
    d.rekt(vx, vy - 20, vx + 6, vy - 18, 0)
    d.px(vx + 2, vy - 17, 3)
    d.radial(vx + 18, vy - 4, 18, 0.6, mask=(YY < vy + 6))
    # Röken (animerad), räknas till klickytan eftersom den ritas med färg
    for i in range(6):
        k = (i + rok) % 6
        ry = vy - 22 - k * 5
        rx = vx + 3 - int(3 * math.sin(k * 1.3)) - k
        r = 2 + k // 2
        m = d.mask_ellips(rx - r, ry - r, rx + r, ry + r)
        d.a[m & (TROSKEL < 0.8 - k * 0.1)] = 5 if k < 2 else (4 if k < 4 else 3)

    # Gubben bakom vagnen: rock, halsduk, keps, grå mustasch
    gx = 174
    oy = vy - 80
    d.rekt(gx - 7, oy + 60, gx + 7, oy + 82, 7)                      # rock
    d.rekt(gx - 7, oy + 60, gx - 5, oy + 82, 8)
    d.rekt(gx - 1, oy + 62, gx, oy + 80, 6)
    for by in (65, 70, 75):
        d.px(gx + 1, oy + by, 10)
    d.rekt(gx - 6, oy + 58, gx + 6, oy + 62, 13)                     # halsduk
    d.rekt(gx + 3, oy + 60, gx + 6, oy + 68, 13)
    d.rekt(gx + 4, oy + 66, gx + 6, oy + 68, 14)
    d.rekt(gx - 4, oy + 46, gx + 5, oy + 58, 9)                      # ansikte
    d.rekt(gx + 4, oy + 50, gx + 6, oy + 54, 9)                      # näsa
    d.px(gx + 5, oy + 52, 14)
    d.px(gx + 2, oy + 50, 0)
    d.rekt(gx, oy + 54, gx + 6, oy + 56, 5)                          # mustasch
    d.px(gx - 4, oy + 52, 8)
    d.rekt(gx - 5, oy + 42, gx + 6, oy + 47, 3)                      # keps
    d.rekt(gx - 5, oy + 42, gx + 6, oy + 43, 4)
    d.rekt(gx + 3, oy + 46, gx + 9, oy + 47, 2)
    d.rekt(gx - 6, oy + 46, gx - 3, oy + 50, 4)                      # grå hår i nacken
    # Arm som vänder kastanjer med en skopa
    d.rekt(gx - 14, oy + 66, gx - 5, oy + 70, 7)
    d.rekt(gx - 17, oy + 66, gx - 13, oy + 70, 2)                    # vante
    d.linje(gx - 16, oy + 68, gx - 20, oy + 76, 0)
    d.rekt(gx - 23, oy + 75, gx - 18, oy + 77, 4)


def stadspark(v=None):
    v = v or {}
    regnfas = v.get("regn", 0)
    rok = v.get("rok", 0)
    rnd = random.Random(1912)
    d = Duk(1)

    # --- Himmel med måne och avlägsna hus ovanför trädtopparna ---
    d.vgrad(0, 0, W, 56, [0, 0, 1, 1, 2, 2])
    fyll(d, 136, 4, 144, 12, 15)
    d.px(139, 7, 5)
    d.px(141, 9, 5)
    d.ljus(d.mask_ellips(128, -4, 152, 20), 0.35)
    d.poly([(118, 12), (150, 9), (170, 12), (130, 14)], 1)
    x = 0
    while x < W:
        b = rnd.randint(10, 18)
        topp = rnd.randint(24, 38)
        d.rekt(x, topp, x + b, 56, 1)
        for wy in range(topp + 3, 50, 5):
            for wx in range(x + 2, x + b - 2, 4):
                if rnd.random() < 0.18:
                    d.rekt(wx, wy, wx + 2, wy + 2, 9 if rnd.random() < 0.7 else 10)
        x += b + rnd.randint(0, 4)
    # Bortre trädrad, mörk massa, och kala träd
    for xx in range(W):
        topp = 44 + int(3 * math.sin(xx / 6.0) + 2 * math.sin(xx / 2.3))
        d.rekt(xx, topp, xx + 1, 58, 0)
    for (tx, ty, ln, dj) in ((8, 64, 16, 7), (100, 52, 9, 5), (128, 54, 11, 6), (184, 64, 16, 7), (76, 54, 9, 5)):
        kalt_trad(d, tx, ty, ln, math.pi / 2 + rnd.uniform(-0.1, 0.1), dj, rnd, 0)
    stam(d, 6, 70, 52, 3)
    stam(d, 182, 70, 50, 3)

    # --- Mark: gräs, gångar, grus ---
    gras(d, 0, 56, W, H, rnd)
    d.poly([(100, 68), (192, 56), (192, 70), (112, 80)], 3)        # gången österut
    d.linje(100, 68, 192, 56, 2)
    d.linje(112, 80, 192, 70, 4)
    d.poly([(90, 54), (100, 54), (116, 104), (76, 104)], 3)        # gången norrut
    d.linje(90, 54, 76, 104, 2)
    d.linje(100, 54, 116, 104, 2)
    d.a[d.mask_ellips(54, 92, 138, 130)] = 3                       # grusplanen innanför grinden
    ring(d, 54, 92, 138, 130, 2)
    grus = (d.a == 3)
    d.ljus(grus & ((XX * 7 + YY * 13) % 11 == 0), 1.0)
    d.ljus(grus & ((XX * 5 + YY * 3) % 17 == 0), 1.0, MORKARE)
    for (px0, py0, px1, py1) in ((84, 98, 104, 102), (104, 110, 118, 113), (150, 64, 160, 66), (88, 64, 94, 66)):
        fyll(d, px0, py0, px1, py1, 2)
        d.rekt((px0 + px1) // 2 - 2, (py0 + py1) // 2, (px0 + px1) // 2 + 2, (py0 + py1) // 2 + 1, 4)

    # --- Utgång norrut: gången mot dammen med skylt ---
    with d.yta("utgang:n"):
        d.markera("utgang:n", 86, 54, 106, 74)
        vagskylt(d, 84, 34, "DAMMEN", "u", 60)

    # --- Utgång österut: gången mot paviljongen med skylt ---
    with d.yta("utgang:ö"):
        d.markera("utgang:ö", 150, 56, W, 74)
        vagskylt(d, 164, 26, "PAVILJONG", "h", 62)

    # --- Parklyktor ---
    parklykta(d, 116, 52, 86)
    parklykta(d, 72, 56, 94, 0.45)
    vattenspegel(d, 84, 104, 100, 104, 0.6)

    # --- Statyn: generalen till häst, duvan på huvudet ---
    with d.yta("parkstaty"):
        d.rekt(26, 64, 66, 90, 3)
        d.rekt(26, 64, 29, 90, 4)
        d.rekt(63, 64, 66, 90, 2)
        d.rekt(23, 60, 69, 65, 4)
        d.rekt(23, 60, 69, 61, 5)
        d.rekt(22, 87, 70, 93, 4)
        d.rekt(22, 87, 70, 88, 5)
        d.rekt(35, 70, 57, 80, 9)
        d.rekt(36, 71, 56, 79, 7)
        for lx in range(38, 55, 2):
            d.px(lx, 73, 10)
            d.px(lx, 76, 10 if lx < 50 else 7)
        tt = Duk(16)
        _general(tt)
        ys, xs = np.nonzero(tt.a != 16)
        for y_, x_ in zip(ys, xs):
            d.px(x_ + 1, y_ - 3, tt.a[y_, x_])
    d.radial(46, 76, 30, 0.35, mask=(XX < 72) & (YY > 56))

    # --- Parkbänken med den kvarglömda hatten ---
    with d.yta("parkbank"):
        bx, by = 2, 104
        d.rekt(bx, by - 12, bx + 32, by - 10, 8)
        d.rekt(bx, by - 8, bx + 32, by - 6, 8)
        d.rekt(bx, by - 12, bx + 32, by - 11, 9)
        d.rekt(bx, by - 8, bx + 32, by - 7, 9)
        d.rekt(bx - 2, by - 3, bx + 34, by, 8)
        d.rekt(bx - 2, by - 3, bx + 34, by - 2, 9)
        d.rekt(bx - 2, by, bx + 34, by + 1, 6)
        for lx in (bx + 1, bx + 29):
            d.rekt(lx, by - 14, lx + 2, by + 10, 0)
            d.rekt(lx - 2, by + 8, lx + 4, by + 10, 0)
        hx = bx + 14
        d.rekt(hx - 3, by - 5, hx + 12, by - 3, 6)
        d.rekt(hx, by - 11, hx + 9, by - 5, 7)
        d.rekt(hx + 1, by - 12, hx + 8, by - 11, 7)
        d.rekt(hx + 3, by - 12, hx + 6, by - 10, 6)
        d.rekt(hx, by - 7, hx + 9, by - 5, 13)
        d.rekt(hx + 1, by - 11, hx + 2, by - 7, 8)
        d.rekt(hx - 3, by - 5, hx + 12, by - 4, 8)

    # --- Kastanjegubben med vagnen ---
    with d.yta("kastanjeman"):
        _kastanjeman(d, rok)

    # --- Utgång söderut: smidesjärnsgrinden i nederkanten ---
    with d.yta("utgang:s"):
        for (px0, px1) in ((50, 60), (132, 142)):
            d.rekt(px0, 100, px1, H, 3)
            d.rekt(px0, 100, px0 + 2, H, 4)
            d.rekt(px1 - 2, 100, px1, H, 2)
            for yy in range(104, H, 5):
                d.rekt(px0, yy, px1, yy + 1, 2)
            d.rekt(px0 - 2, 97, px1 + 2, 101, 4)
            d.rekt(px0 - 2, 97, px1 + 2, 98, 5)
            cx = (px0 + px1) // 2
            d.rekt(cx - 3, 86, cx + 3, 97, 0)
            d.rekt(cx - 2, 88, cx + 2, 96, 11)
            d.rekt(cx - 2, 94, cx + 2, 96, 10)
            d.rekt(cx - 4, 84, cx + 4, 86, 0)
            d.px(cx, 83, 0)
        # Uppslagna grindflyglar i smide
        for (gx0, gx1) in ((36, 50), (142, 156)):
            d.rekt(gx0, 104, gx1, 105, 0)
            d.rekt(gx0, 116, gx1, 117, 0)
            for xx in range(gx0, gx1, 3):
                d.rekt(xx, 102, xx + 1, H, 0)
                d.px(xx, 101, 9)
            ring(d, (gx0 + gx1) // 2 - 4, 106, (gx0 + gx1) // 2 + 4, 114, 0)
        d.markera("utgang:s", 60, 112, 132, H)
        d.rekt(78, 107, 116, 119, 0)
        d.rekt(79, 108, 115, 118, 15)
        d.rekt(80, 109, 114, 117, 12)
        skriv(d, 83, 111, "GATAN", 15)
        pil(d, 105, 109, "n", 15)
    for cx in (55, 137):
        d.radial(cx, 92, 18, 0.5, mask=(d.a < 10) & (YY > 78))

    regn(d, regnfas, 90, fro=31)
    d.vinjett(0.35)
    return d


# ======================================================================
#  DAMMEN
# ======================================================================
ANKA_HANE = [
    "..nn......",
    ".ynkn.....",
    "...w....d.",
    "..bgggggd.",
    "...gggggg.",
]
ANKA_HONA = [
    "..ee......",
    ".yeke.....",
    "...e....e.",
    "..eefeeee.",
    "...eeeeee.",
]
ANKFARG = {"n": 12, "y": 10, "k": 0, "w": 15, "b": 7, "g": 4, "d": 0, "e": 8, "f": 9}


def _anka(d, x, y, hane=True):
    t = Duk(16)
    sprite(t, x, y, ANKA_HANE if hane else ANKA_HONA, ANKFARG)
    kontur(d, t, 1)
    d.rekt(x + 3, y + 5, x + 10, y + 6, 3)                 # vattenlinje
    d.px(x + 11, y + 5, 3)
    d.px(x + 13, y + 5, 2)


def _svan(d, x, y, s=1.0, plats=8):
    """Uthyrningsbåt formad som svan, nosen åt vänster. (x, y) = skrovets vänstra överkant."""
    def p(px_, py_):
        return (int(x + px_ * s), int(y + py_ * s))
    t = Duk(16)
    t.poly([p(4, 0), p(36, 0), p(42, -9), p(41, 2), p(36, 10), p(8, 10)], 15)   # skrov och stjärt
    t.poly([p(8, 6), p(36, 6), p(36, 10), p(8, 10)], 5)
    t.poly([p(12, 1), p(32, 1), p(30, 4), p(14, 4)], 5)                       # vingfjädrar
    t.poly([p(10, -2), p(30, -2), p(30, 0), p(10, 0)], plats)                 # sätet
    # Hals och huvud
    for k in range(12):
        nx = 5 + 2.2 * math.sin(k / 11 * math.pi) - k * 0.12
        t.rekt(int(x + nx * s) - 1, int(y - k * 1.5 * s), int(x + (nx + 3) * s), int(y - k * 1.5 * s) + 2, 15)
    hx, hy = p(1, -20)
    t.a[t.mask_ellips(hx, hy, hx + int(7 * s), hy + int(5 * s))] = 15
    t.rekt(hx - int(4 * s), hy + int(2 * s), hx + 1, hy + int(3.5 * s), 9)   # näbb
    t.px(hx, hy + int(2 * s), 0)
    t.px(hx + int(3 * s), hy + 1, 0)
    kontur(d, t, 0)
    x0, x1 = p(4, 0)[0], p(40, 0)[0]
    d.rekt(x0 + 2, p(0, 10)[1] + 1, x1, p(0, 10)[1] + 2, 3)       # spegling


def dammen(v=None):
    v = v or {}
    ank = v.get("ankor", 0)
    rfas = v.get("ringar", 0)
    rnd = random.Random(4711)
    d = Duk(1)

    # --- Himmel och bortre stranden ---
    d.vgrad(0, 0, W, 38, [0, 0, 1, 1, 2])
    x = 0
    while x < 120:
        b = rnd.randint(9, 16)
        topp = rnd.randint(8, 22)
        d.rekt(x, topp, x + b, 34, 1)
        for wy in range(topp + 3, 30, 5):
            for wx in range(x + 2, x + b - 2, 4):
                if rnd.random() < 0.2:
                    d.rekt(wx, wy, wx + 2, wy + 2, 9)
        x += b + rnd.randint(0, 5)
    for xx in range(W):
        topp = 28 + int(3 * math.sin(xx / 5.0) + 2 * math.sin(xx / 1.9))
        d.rekt(xx, topp, xx + 1, 40, 0)
    for (tx, ty, ln, dj) in ((20, 32, 9, 6), (58, 32, 8, 5), (92, 32, 10, 6), (118, 32, 7, 5)):
        kalt_trad(d, tx, ty, ln, math.pi / 2, dj, rnd, 0)

    # --- Vattnet ---
    d.vgrad(0, 40, W, 104, [2, 1, 2, 1, 1])
    for y in range(42, 104, 3):
        for xx in range((y * 13) % 17, W, 17 + (y % 5)):
            d.rekt(xx, y, xx + 4 + (y - 40) // 12, y + 1, 3 if y < 70 else 2)
    # Lyktor på andra stranden och deras långa speglingar
    for lx in (34, 76):
        d.rekt(lx, 30, lx + 1, 40, 0)
        d.rekt(lx - 1, 27, lx + 2, 30, 11)
        d.radial(lx, 28, 10, 0.5, mask=(YY < 41))
        for y in range(41, 92):
            if (y // 2) % 2 == 0 or y < 50:
                w_ = 1 + (y - 40) // 18
                ox = int(2 * math.sin(y / 3.0))
                d.rekt(lx + ox - w_ // 2, y, lx + ox + w_ // 2 + 1, y + 1, 10 if y < 60 else 9)

    # --- Båthuset med skylt ---
    with d.yta("batshus"):
        hx0, hx1 = 130, 188
        d.rekt(hx0, 26, hx1, 60, 13)
        for xx in range(hx0, hx1, 3):
            d.rekt(xx, 26, xx + 1, 60, 6)
        d.ljus(d.mask_poly([(hx0, 26), (hx1, 26), (hx1, 60), (hx0, 60)]), 0.55, MORKARE)
        d.poly([(hx0 - 4, 27), (159, 6), (hx1 + 4, 27)], 2)          # tak
        d.poly([(hx0 + 2, 26), (159, 10), (hx1 - 2, 26)], 13)
        d.ljus(d.mask_poly([(hx0 + 2, 26), (159, 10), (hx1 - 2, 26)]), 0.5, MORKARE)
        d.linje(hx0 - 4, 27, 159, 6, 15)
        d.linje(159, 6, hx1 + 4, 27, 15)
        d.rekt(157, 3, 161, 7, 15)                                     # flaggstång med vimpel
        d.rekt(158, 0, 159, 4, 0)
        d.rekt(hx0, 26, hx0 + 2, 60, 15)
        d.rekt(hx1 - 2, 26, hx1, 60, 15)
        # Runt fönster i gaveln
        fyll(d, 154, 13, 164, 22, 15)
        fyll(d, 155, 14, 163, 21, 10)
        d.rekt(158, 14, 160, 21, 15)
        # Skylten
        d.rekt(hx0 + 8, 27, hx1 - 8, 38, 0)
        d.rekt(hx0 + 9, 28, hx1 - 9, 37, 15)
        skriv(d, 159 - bredd("BÅTAR 5C") // 2, 31, "BÅTAR 5C", 13)
        # Öppen port mot vattnet, varmt ljus inne
        d.rekt(160, 40, 184, 60, 15)
        d.rekt(161, 41, 183, 60, 6)
        d.vgrad(162, 42, 182, 60, [10, 9, 8])
        d.rekt(164, 52, 180, 60, 6)
        for kx in range(166, 180, 5):                                # åror på väggen
            d.rekt(kx, 43, kx + 1, 56, 7)
            d.rekt(kx - 1, 52, kx + 2, 56, 8)
        # Fönster och livboj
        d.rekt(136, 40, 152, 52, 15)
        d.rekt(137, 41, 151, 51, 10)
        d.rekt(137, 41, 151, 43, 11)
        d.rekt(144, 41, 145, 51, 15)
        d.rekt(137, 46, 151, 47, 15)
        ring(d, 137, 53, 145, 61, 15, 2)
        for (bx_, by_) in ((141, 53), (137, 57), (144, 57), (141, 60)):
            d.px(bx_, by_, 13)
        # Pålar ner i vattnet
        for px_ in range(hx0 + 2, hx1, 8):
            d.rekt(px_, 60, px_ + 2, 68, 0)
    d.radial(172, 54, 26, 0.45, mask=(YY > 40) & (d.a < 9))
    d.radial(144, 46, 16, 0.35, mask=(YY > 40) & (d.a < 9))
    vattenspegel(d, 160, 184, 68, 92, 0.55)

    # --- Ankorna (räknas som en yta, med lite marginal) ---
    d.markera("ankor", 4, 50, 46, 76)
    with d.yta("ankor"):
        for i, (ax, ay, hane) in enumerate(((10, 54, True), (26, 62, False), (14, 68, True))):
            t = (ank + i * 3) % 8
            dx = int(round(2.5 * math.cos(2 * math.pi * t / 8)))
            dy = int(round(0.8 * math.sin(2 * math.pi * t / 8)))
            _anka(d, ax + dx, ay + dy, hane)

    # --- Svanbåtarna vid bryggan ---
    with d.yta("svanbat"):
        _svan(d, 76, 62, 0.72, 7)
        _svan(d, 44, 82, 1.0, 8)
        d.linje(108, 70, 102, 62, 9)                                 # förtöjningar
        d.linje(108, 72, 84, 86, 9)

    # --- Bryggan ---
    d.poly([(96, 66), (W, 62), (W, 74), (100, 76)], 8)
    for xx in range(98, W, 5):
        d.linje(xx, 76 - (xx - 98) // 40, xx + 1, 66 - (xx - 98) // 24, 7)
    d.poly([(100, 76), (W, 74), (W, 78), (100, 80)], 6)
    for px_ in (101, 120, 140, 160, 180):
        d.rekt(px_, 78, px_ + 3, 88, 0)
        d.rekt(px_, 88, px_ + 3, 89, 3)
    d.rekt(104, 66, 108, 72, 6)                                     # pollare
    d.rekt(103, 65, 109, 66, 7)

    # --- Båtkarlen med pipa och sydväst ---
    with d.yta("batkarl"):
        bx = 118
        d.rekt(bx - 5, 64, bx - 1, 72, 0)                         # stövlar
        d.rekt(bx + 1, 64, bx + 5, 72, 0)
        d.rekt(bx - 6, 70, bx - 1, 72, 0)
        d.rekt(bx + 1, 70, bx + 6, 72, 0)
        d.px(bx - 4, 65, 3)
        d.px(bx + 2, 65, 3)
        d.poly([(bx - 7, 44), (bx + 7, 44), (bx + 8, 65), (bx - 8, 65)], 10)   # oljerock
        d.rekt(bx - 8, 46, bx - 6, 65, 9)
        d.rekt(bx, 48, bx + 1, 64, 9)
        for by_ in (50, 55, 60):
            d.px(bx - 2, by_, 6)
        d.rekt(bx + 6, 46, bx + 10, 60, 10)                       # arm
        d.rekt(bx + 6, 58, bx + 10, 61, 9)
        d.rekt(bx - 11, 47, bx - 6, 51, 10)                       # arm med pipan
        d.rekt(bx - 12, 45, bx - 9, 49, 9)
        d.rekt(bx - 5, 32, bx + 5, 42, 9)                         # ansikte
        d.rekt(bx - 7, 37, bx - 4, 40, 9)                         # näsa
        d.px(bx - 7, 38, 14)
        d.px(bx - 3, 35, 0)
        d.rekt(bx - 3, 34, bx, 35, 15)                            # vitt ögonbryn
        d.poly([(bx - 6, 40), (bx + 5, 40), (bx + 4, 47), (bx - 1, 49), (bx - 5, 46)], 15)   # skägg
        d.rekt(bx - 2, 44, bx + 3, 47, 5)
        d.rekt(bx - 12, 42, bx - 4, 43, 6)                        # pipa
        d.rekt(bx - 14, 38, bx - 10, 43, 7)
        d.px(bx - 13, 38, 13)
        d.rekt(bx - 6, 27, bx + 6, 33, 10)                        # sydväst
        d.rekt(bx - 8, 31, bx + 8, 33, 10)
        d.poly([(bx + 4, 31), (bx + 11, 33), (bx + 10, 39), (bx + 5, 36)], 10)
        d.rekt(bx - 8, 32, bx + 8, 33, 9)
        d.rekt(bx - 4, 28, bx + 2, 29, 11)
        d.rekt(bx + 4, 33, bx + 6, 40, 4)                         # grått hår
        for k in range(4):                                        # piprök
            d.px(bx - 13 - (k % 2), 35 - k * 2, 5 if k < 2 else 4)
    d.radial(118, 40, 22, 0.3, mask=(d.a < 8) & (XX < 128))

    # --- Ringar på vattnet (animerade) ---
    for i, (rx, ry) in enumerate(((60, 50), (96, 56), (30, 90), (136, 84), (112, 96), (8, 82))):
        k = (rfas + i) % 4
        r = 1 + k * 2
        ring(d, rx - r, ry - r // 2 - 1, rx + r, ry + r // 2 + 1, (4, 4, 3, 2)[k])

    # --- Närmaste stranden med vass och gång ---
    for xx in range(W):
        top = 102 + int(1.5 * math.sin(xx / 4.0))
        d.rekt(xx, top, xx + 1, H, 6)
    d.vgrad(0, 104, W, H, [6, 7, 6])
    for _ in range(40):
        sx, sy = rnd.randint(0, W - 4), rnd.randint(101, 106)
        d.rekt(sx, sy, sx + rnd.randint(3, 6), sy + 2, 3)
        d.px(sx + 1, sy, 4)
    gras(d, 120, 108, W, H, rnd)
    for k in range(26):                                             # vass och kaveldun
        vx_ = 132 + k * 2 + rnd.randint(-1, 1)
        vh = rnd.randint(10, 22)
        d.linje(vx_, 110, vx_ + rnd.randint(-2, 2), 110 - vh, 12 if k % 3 else 0)
        if k % 4 == 0:
            d.rekt(vx_ - 1, 110 - vh + 2, vx_ + 1, 110 - vh + 7, 7)
    for k in range(10):
        vx_ = 50 + k * 3
        d.linje(vx_, 110, vx_ + rnd.randint(-2, 2), 110 - rnd.randint(6, 12), 12 if k % 2 else 0)

    # --- Utgång söderut: gången tillbaka med skylt ---
    with d.yta("utgang:s"):
        d.poly([(0, 106), (40, 106), (54, H), (0, H)], 3)
        d.linje(40, 106, 54, H - 1, 2)
        d.ljus(d.mask_poly([(0, 106), (40, 106), (54, H), (0, H)]) & ((XX * 7 + YY * 13) % 11 == 0), 1.0)
        vagskylt(d, 22, 90, "ENTRÉ", "n", 112)
        d.markera("utgang:s", 0, 104, 52, H)
        vagskylt(d, 22, 90, "ENTRÉ", "n", 112)
    parklykta(d, 104, 86, 114, 0.5)

    d.vinjett(0.4)
    return d


# ======================================================================
#  MUSIKPAVILJONGEN
# ======================================================================
def _stol(d, x, y, s=1, vält=False):
    """Hopfällbar parkstol, (x, y) = vänster fot, s = storlek 1 eller 2."""
    if vält:
        d.rekt(x, y - 3, x + 9 * s, y - 1, 7)
        d.rekt(x, y - 3, x + 9 * s, y - 2, 8)
        d.linje(x + 2, y - 1, x + 6 * s, y - 5 * s, 0)
        d.linje(x + 6 * s, y - 1, x + 2, y - 5 * s, 0)
        return
    h = 6 * s + 3
    d.rekt(x, y - h, x + 1, y, 0)                          # bakben/ryggstöd
    d.rekt(x + 4 + s, y - h // 2, x + 5 + s, y, 0)         # framben
    d.rekt(x, y - h, x + 4, y - h + 2 + s, 8)              # ryggbräda
    d.rekt(x, y - h, x + 4, y - h + 1, 9)
    d.rekt(x, y - h // 2 - 1, x + 6 + s, y - h // 2 + 1, 8)   # sits
    d.rekt(x + 1, y - h // 2 - 1, x + 6 + s, y - h // 2, 9)
    d.px(x + 3, y - h // 2 - 1, 5)                         # regndroppe på sitsen


def _not(d, x, y, c, dubbel=False):
    d.rekt(x, y + 3, x + 2, y + 5, c)
    d.rekt(x + 2, y, x + 3, y + 4, c)
    d.px(x + 3, y, c)
    d.px(x + 4, y + 1, c)
    if dubbel:
        d.rekt(x + 4, y + 3, x + 6, y + 5, c)
        d.rekt(x + 6, y, x + 7, y + 4, c)
        d.rekt(x + 2, y, x + 7, y + 1, c)


def _tubaspelare(d, sving):
    tx = 108
    # Ben med röda revärer och blanka skor
    d.rekt(tx - 6, 66, tx - 1, 75, 2)
    d.rekt(tx + 1, 66, tx + 6, 75, 2)
    d.rekt(tx - 5, 66, tx - 4, 75, 13)
    d.rekt(tx + 4, 66, tx + 5, 75, 13)
    d.rekt(tx - 7, 74, tx - 1, 77, 0)
    d.rekt(tx + 1, 74, tx + 7, 77, 0)
    d.px(tx - 6, 74, 4)
    d.px(tx + 2, 74, 4)
    # Uniformsrock med guldknappar och epåletter, rundmagad
    d.a[d.mask_ellips(tx - 9, 48, tx + 9, 69)] = 2
    d.rekt(tx - 8, 50, tx + 8, 60, 2)
    d.rekt(tx - 8, 50, tx - 6, 66, 3)
    for by_ in (53, 57, 61, 65):
        d.px(tx + 2, by_, 10)
    d.rekt(tx - 9, 49, tx - 5, 51, 10)
    d.rekt(tx + 5, 49, tx + 9, 51, 10)
    d.rekt(tx - 3, 47, tx + 3, 50, 13)                     # krage
    # Huvud med uppblåsta kinder och mustasch
    d.rekt(tx - 4, 38, tx + 4, 47, 9)
    fyll(d, tx - 7, 40, tx - 2, 46, 14)                    # uppblåst kind
    fyll(d, tx - 7, 41, tx - 3, 45, 9)
    d.px(tx - 6, 42, 14)
    d.px(tx - 1, 40, 0)
    d.px(tx + 2, 40, 0)
    d.rekt(tx - 3, 43, tx + 3, 44, 7)                      # mustasch
    d.px(tx + 4, 42, 9)                                    # öra
    # Skärmmössa med guldband
    d.rekt(tx - 5, 33, tx + 5, 38, 2)
    d.rekt(tx - 5, 36, tx + 5, 38, 10)
    d.rekt(tx - 6, 38, tx + 1, 39, 0)
    d.px(tx, 34, 10)
    # Tuban: kropp framför magen, munstycke vid munnen, klockan upp till vänster (gungar)
    ox = (0, 1, 1, 0, -1, -1)[sving]
    oy = (0, 0, 1, 0, 0, 1)[sving]
    d.rekt(tx - 5, 44, tx - 2, 45, 10)                     # munstycke
    d.rekt(tx - 6, 44, tx - 5, 52, 9)
    d.a[d.mask_ellips(tx - 12, 52, tx + 2, 70)] = 9        # rör i ögla
    d.a[d.mask_ellips(tx - 10, 54, tx, 68)] = 10
    d.a[d.mask_ellips(tx - 8, 57, tx - 2, 65)] = 2
    d.rekt(tx - 7, 57, tx - 3, 61, 9)                      # ventiler
    for vx_ in (tx - 7, tx - 5, tx - 3):
        d.rekt(vx_, 54, vx_ + 1, 57, 11)
    d.poly([(tx - 11, 56), (tx - 14 + ox, 46 + oy), (tx - 17 + ox, 38 + oy), (tx - 10 + ox, 38 + oy), (tx - 8, 54)], 10)
    d.linje(tx - 11, 56, tx - 15 + ox, 40 + oy, 11)
    fyll(d, tx - 24 + ox, 30 + oy, tx - 5 + ox, 39 + oy, 9)          # klockan
    fyll(d, tx - 23 + ox, 31 + oy, tx - 6 + ox, 38 + oy, 10)
    fyll(d, tx - 20 + ox, 32 + oy, tx - 9 + ox, 36 + oy, 6)
    d.rekt(tx - 21 + ox, 31 + oy, tx - 16 + ox, 32 + oy, 11)
    d.rekt(tx - 3, 56, tx + 2, 60, 9)                      # händer
    d.rekt(tx - 13, 60, tx - 10, 64, 9)


def paviljong(v=None):
    v = v or {}
    regnfas = v.get("regn", 0)
    sving = v.get("tuba", 0)
    notfas = v.get("noter", None)
    rnd = random.Random(1890)
    d = Duk(1)

    # --- Himmel, avlägsna hus och kala träd ---
    d.vgrad(0, 0, W, 62, [0, 0, 1, 1, 2, 2])
    x = 0
    while x < W:
        b = rnd.randint(10, 18)
        topp = rnd.randint(28, 44)
        d.rekt(x, topp, x + b, 60, 1)
        for wy in range(topp + 3, 56, 5):
            for wx in range(x + 2, x + b - 2, 4):
                if rnd.random() < 0.16:
                    d.rekt(wx, wy, wx + 2, wy + 2, 9)
        x += b + rnd.randint(0, 6)
    for xx in range(W):
        topp = 50 + int(3 * math.sin(xx / 6.0) + 2 * math.sin(xx / 2.1))
        d.rekt(xx, topp, xx + 1, 64, 0)
    for (tx, ty, ln, dj) in ((14, 70, 16, 7), (176, 70, 16, 7), (40, 60, 9, 5), (158, 60, 9, 5)):
        kalt_trad(d, tx, ty, ln, math.pi / 2 + rnd.uniform(-0.15, 0.15), dj, rnd, 0)
    stam(d, 12, 74, 56, 3)
    stam(d, 174, 74, 56, 3)
    gras(d, 0, 62, W, H, rnd)

    # --- Gången västerut och grusplanen framför scenen ---
    d.a[d.mask_ellips(26, 84, 170, 124)] = 3
    ring(d, 26, 84, 170, 124, 2)
    grus = d.a == 3
    d.ljus(grus & ((XX * 7 + YY * 13) % 11 == 0), 1.0)
    d.ljus(grus & ((XX * 5 + YY * 3) % 17 == 0), 1.0, MORKARE)
    for (px0, py0, px1, py1) in ((60, 110, 78, 114), (120, 104, 136, 107), (92, 114, 104, 117)):
        fyll(d, px0, py0, px1, py1, 2)
        d.rekt((px0 + px1) // 2 - 2, (py0 + py1) // 2, (px0 + px1) // 2 + 2, (py0 + py1) // 2 + 1, 4)

    with d.yta("utgang:v"):
        d.poly([(0, 86), (40, 90), (40, 104), (0, 106)], 3)
        d.linje(0, 86, 40, 90, 2)
        d.linje(0, 106, 40, 104, 4)
        d.ljus(d.mask_poly([(0, 86), (40, 90), (40, 104), (0, 106)]) & ((XX * 7 + YY * 13) % 11 == 0), 1.0)
        d.markera("utgang:v", 0, 84, 30, 108)
        vagskylt(d, 16, 64, "ENTRÉ", "v", 92, pilfoerst=True)

    # --- Paviljongen ---
    with d.yta("paviljongen"):
        # Insidan: mörk, med bakre pelare
        d.rekt(46, 24, 148, 76, 1)
        d.vgrad(46, 24, 148, 76, [0, 1, 2])
        for bx_ in (60, 96, 134):
            d.rekt(bx_, 26, bx_ + 2, 72, 3)
        d.rekt(48, 58, 146, 60, 3)                         # bakre räcke
        for rx_ in range(50, 146, 4):
            d.rekt(rx_, 60, rx_ + 1, 72, 2)
        # Golv
        d.poly([(46, 72), (148, 72), (152, 78), (42, 78)], 8)
        for yy in (74, 76):
            d.rekt(44, yy, 150, yy + 1, 7)
        # Sockel med vitt spaljé
        d.rekt(66, 78, 128, 92, 15)
        d.poly([(42, 78), (66, 78), (66, 92), (44, 89)], 5)
        d.poly([(128, 78), (152, 78), (150, 89), (128, 92)], 4)
        for k in range(0, 40, 4):
            d.linje(66 + k, 80, 66 + k + 10, 90, 1)
            d.linje(66 + k + 10, 80, 66 + k, 90, 1)
        d.rekt(66, 78, 128, 80, 15)
        d.rekt(66, 90, 128, 92, 5)
        for k in range(0, 24, 4):
            d.linje(44 + k, 80, 44 + k + 4, 87, 2)
            d.linje(130 + k, 80, 130 + k + 4, 87, 1)
        # Trappan
        for i, sy in enumerate((80, 84, 88)):
            d.rekt(84 - i * 2, sy, 110 + i * 2, sy + 4, 4 if i % 2 else 5)
            d.rekt(84 - i * 2, sy, 110 + i * 2, sy + 1, 15)
        d.rekt(82, 78, 84, 92, 15)
        d.rekt(110, 78, 112, 92, 15)
        # Främre pelare
        for (cx, c1, c2) in ((44, 4, 3), (68, 15, 5), (124, 15, 5), (148, 4, 3)):
            d.rekt(cx, 24, cx + 3, 78, c1)
            d.rekt(cx + 2, 24, cx + 3, 78, c2)
            d.rekt(cx - 1, 30, cx + 4, 32, c1)
            d.rekt(cx - 1, 76, cx + 4, 78, c1)
        # Räcke på framsidan (öppet vid trappan)
        for (rx0, rx1) in ((47, 68), (71, 84), (110, 124), (127, 148)):
            d.rekt(rx0, 64, rx1, 66, 15)
            for rx_ in range(rx0 + 1, rx1, 3):
                d.rekt(rx_, 66, rx_ + 1, 74, 5)
        # Taket: åttakantigt, ärggrönt med ribbor
        d.poly([(40, 24), (66, 21), (97, 0), (128, 21), (154, 24), (128, 24), (66, 24)], 12)
        d.ljus(d.mask_poly([(40, 25), (66, 21), (97, 0)]), 0.5, MORKARE)
        d.ljus(d.mask_poly([(128, 21), (154, 25), (97, 0)]), 0.25, MORKARE)
        for (ax, ay) in ((66, 21), (128, 21)):
            d.linje(97, 0, ax, ay, 4)
        for k in range(1, 6):
            yy = k * 4
            d.linje(97 - int(k * 5.4), yy, 97 + int(k * 5.4), yy, 6)
        d.rekt(38, 22, 156, 25, 15)                        # takfot
        for sx in range(40, 156, 6):                       # spetskappa
            fyll(d, sx, 23, sx + 6, 29, 15)
        d.rekt(38, 22, 156, 24, 15)
        d.rekt(38, 24, 156, 25, 5)
        d.rekt(95, 0, 99, 2, 10)                           # spira
        # Girlanger: vimplar i rött, vitt och blått mellan pelarna
        for (gx0, gx1) in ((47, 68), (71, 124), (127, 148)):
            n = (gx1 - gx0) // 4
            for i in range(n + 1):
                t = i / max(1, n)
                gx = gx0 + int(t * (gx1 - gx0))
                gy = 29 + int(5 * math.sin(t * math.pi) * (gx1 - gx0) / 50)
                d.px(gx, gy, 0)
                if i < n:
                    c = (13, 15, 3)[i % 3]
                    d.poly([(gx, gy + 1), (gx + 3, gy + 1), (gx + 1, gy + 4)], c)
        # Glödlampor längs takfoten
        for lx in range(42, 154, 8):
            d.px(lx, 27, 11)
        # Lampan i taket
        d.rekt(96, 25, 98, 28, 0)
        fyll(d, 93, 28, 101, 33, 10)
        d.rekt(95, 29, 99, 32, 11)
        d.markera("paviljongen", 40, 24, 154, 28)
    d.radial(97, 46, 44, 0.5, mask=(YY > 26) & (YY < 80) & (XX > 44) & (XX < 150))
    d.radial(97, 90, 40, 0.3, mask=(YY > 80))

    # --- Notstället med noter som blåser ---
    with d.yta("notstall"):
        d.rekt(80, 52, 81, 76, 0)
        d.linje(80, 75, 76, 77, 0)
        d.linje(81, 75, 85, 77, 0)
        d.poly([(72, 44), (89, 44), (90, 53), (71, 53)], 0)
        d.poly([(73, 44), (80, 43), (80, 52), (72, 52)], 15)
        d.poly([(81, 43), (88, 44), (89, 52), (81, 52)], 15)
        for ly in (46, 48, 50):
            d.rekt(74, ly, 79, ly + 1, 4)
            d.rekt(82, ly, 88, ly + 1, 4)
        d.px(76, 47, 0)
        d.px(84, 49, 0)
        d.poly([(88, 42), (94, 38), (95, 44), (89, 46)], 15)    # ett blad lyfter
        d.linje(90, 42, 94, 40, 4)

    # --- Tubaspelaren ---
    with d.yta("tubaspelare"):
        _tubaspelare(d, sving)

    # --- Tomma stolar i regnet ---
    for (sx, sy, st) in ((40, 98, 1), (54, 98, 1), (68, 98, 1), (118, 98, 1), (132, 98, 1), (146, 98, 1),
                         (30, 112, 2), (48, 112, 2), (66, 112, 2), (122, 112, 2), (140, 112, 2)):
        _stol(d, sx, sy, st)
    _stol(d, 158, 113, 2, vält=True)

    parklykta(d, 170, 64, 100, 0.45)

    # --- Noter som svävar (animerade) ---
    if notfas is not None:
        for i in range(3):
            k = (notfas + i * 2) % 6
            nx = 82 - k * 6
            ny = 32 - k * 2 + (0, -1, -2, -1, 0, 1)[(k + i) % 6] + i * 4
            _not(d, nx, ny, (11, 11, 15, 10, 9, 4)[k], dubbel=(i == 1))

    regn(d, regnfas, 85, fro=19)
    d.vinjett(0.4)
    return d


# ======================================================================
#  FYREN LÄNGST UT PÅ PIREN
# ======================================================================
def _kagla(d, cx, cy, vinkel, langd, spridning):
    """Ljuskägla från fyren: en kil av ljus som bleknar utåt (räknas inte som klickyta)."""
    if langd <= 0:
        return
    a0, a1 = vinkel - spridning, vinkel + spridning
    pkt = [(cx, cy - 1), (cx + langd * math.cos(a0), cy + langd * math.sin(a0)),
           (cx + langd * math.cos(a1), cy + langd * math.sin(a1)), (cx, cy + 1)]
    m = d.mask_poly(pkt)
    dist = np.sqrt((XX - cx) ** 2 + (YY - cy) ** 2)
    s = np.clip(1 - dist / langd, 0, 1)
    d.ljus(m, 0.5 + 0.5 * s)
    d.ljus(m, 0.15 + 0.7 * s)
    a0, a1 = vinkel - spridning * 0.5, vinkel + spridning * 0.5
    pkt = [(cx, cy), (cx + langd * 0.8 * math.cos(a0), cy + langd * 0.8 * math.sin(a0)),
           (cx + langd * 0.8 * math.cos(a1), cy + langd * 0.8 * math.sin(a1))]
    karna = d.mask_poly(pkt) & (TROSKEL < s * 0.9)
    d.a[karna] = np.where(dist[karna] < 18, 11, np.where(dist[karna] < 40, 15, 5)).astype(np.uint8)


def fyr(v=None):
    v = v or {}
    kfas = v.get("kagla", 0)
    vfas = v.get("vagor", 0)
    rnd = random.Random(1888)
    d = Duk(1)

    # --- Himmel och hav ---
    d.vgrad(0, 0, W, 62, [0, 0, 0, 1, 1, 2])
    d.vgrad(0, 62, W, H, [1, 1, 0, 0])
    d.rekt(0, 61, W, 62, 3)
    d.ljus((YY >= 56) & (YY < 61), 0.5)
    for y in range(64, 98, 3):
        for xx in range((y * 11) % 13, W, 11 + (y % 4) * 2):
            ln = 2 + (y - 60) // 10
            xx2 = xx + ((vfas + y // 3) % 4) * 2 - 3
            d.rekt(xx2, y, xx2 + ln, y + 1, 3)
            if (xx + y) % 3 == 0:
                d.rekt(xx2 + 1, y - 1, xx2 + ln - 1, y, 4)
    # Staden långt bort, där piren börjar
    x = 0
    while x < 44:
        b = rnd.randint(4, 8)
        topp = rnd.randint(50, 57)
        d.rekt(x, topp, x + b, 62, 1)
        for wy in range(topp + 2, 61, 3):
            for wx in range(x + 1, x + b - 1, 2):
                if rnd.random() < 0.25:
                    d.px(wx, wy, 9)
        x += b
    # Klippor ute i havet
    for (kx0, kx1, ky) in ((54, 74, 64), (176, 192, 62)):
        d.poly([(kx0, ky + 4), (kx0 + 5, ky), (kx0 + 11, ky + 1), (kx1, ky + 4)], 0)
        d.linje(kx0 + 5, ky, kx0 + 11, ky + 1, 2)

    # --- Utgång norrut: piren tillbaka mot staden, med skylt ---
    with d.yta("utgang:n"):
        d.poly([(0, 98), (60, 98), (24, 61), (16, 61)], 3)
        d.poly([(0, 98), (0, 70), (16, 61)], 2)                 # pirens sida i skugga
        d.linje(16, 61, 0, 82, 1)
        for k in range(1, 9):                                   # stenblockens fogar
            t = (k / 9) ** 1.6
            yy = int(61 + 37 * t)
            x0 = int(16 - 16 * t)
            x1 = int(24 + 36 * t)
            d.linje(x0, yy, x1, yy, 2)
        d.linje(24, 61, 60, 98, 4)
        for k, t in enumerate((0.25, 0.55, 0.9)):               # små lyktor längs piren
            ly = int(61 + 37 * t * t)
            lx = int(24 + 36 * t * t) - 2
            h = 3 + int(14 * t * t)
            d.rekt(lx, ly - h, lx + 1, ly, 0)
            d.rekt(lx - 1, ly - h - 2, lx + 2, ly - h, 11)
            d.radial(lx, ly - h, 4 + 8 * t, 0.5, mask=d.a < 9)
        vagskylt(d, 48, 74, "TILL STAN", "u", 98)
        d.markera("utgang:n", 0, 80, 34, 98)
        vagskylt(d, 48, 74, "TILL STAN", "u", 98)

    # --- Fyren ---
    fx = 128
    with d.yta("fyrtorn"):
        topp_b, bas_b = 7, 15
        for y in range(24, 94):
            t = (y - 24) / 70
            hb = int(topp_b + (bas_b - topp_b) * t)
            band = ((y - 24) // 10) % 2
            d.rekt(fx - hb, y, fx + hb, y + 1, 13 if band == 0 else 15)
        d.ljus(d.mask_poly([(fx + 2, 24), (fx + 7, 24), (fx + 15, 94), (fx + 4, 94)]), 0.55, MORKARE)
        d.ljus(d.mask_poly([(fx - 7, 24), (fx - 5, 24), (fx - 13, 94), (fx - 15, 94)]), 0.3)
        # Dörr och fönster
        d.rekt(fx - 4, 80, fx + 4, 94, 0)
        d.rekt(fx - 3, 81, fx + 3, 94, 6)
        d.rekt(fx - 3, 81, fx + 3, 82, 7)
        d.px(fx + 2, 88, 10)
        for wy in (40, 60):
            d.rekt(fx - 2, wy, fx + 2, wy + 5, 0)
            d.rekt(fx - 1, wy + 1, fx + 1, wy + 4, 10)
        # Galleri med räcke
        d.rekt(fx - 12, 22, fx + 12, 25, 0)
        d.rekt(fx - 12, 22, fx + 12, 23, 4)
        d.rekt(fx - 11, 17, fx + 11, 18, 0)
        for rx_ in range(fx - 11, fx + 12, 3):
            d.rekt(rx_, 17, rx_ + 1, 22, 0)
        # Lyktrummet
        d.rekt(fx - 6, 8, fx + 6, 22, 0)
        d.rekt(fx - 5, 9, fx + 5, 21, 10)
        d.rekt(fx - 3, 10, fx + 3, 20, 11)
        for rx_ in (fx - 3, fx + 2):
            d.rekt(rx_, 9, rx_ + 1, 21, 9)
        # Kupol och spira
        d.poly([(fx - 8, 8), (fx + 8, 8), (fx + 3, 2), (fx - 3, 2)], 13)
        d.rekt(fx - 8, 7, fx + 8, 8, 6)
        d.rekt(fx - 1, 0, fx + 1, 3, 0)
        d.ljus(d.mask_poly([(fx + 1, 2), (fx + 3, 2), (fx + 8, 8), (fx + 3, 8)]), 0.5, MORKARE)
    d.radial(fx, 15, 22, 0.55, mask=(d.a < 9))

    # --- Plattformen där vi står (pirens ände) ---
    d.rekt(0, 98, W, H, 3)
    d.vgrad(0, 98, W, H, [4, 3, 3, 2])
    for y in range(102, H, 6):
        d.rekt(0, y, W, y + 1, 2)
        off = 0 if (y // 6) % 2 else 9
        for xx in range(off, W, 18):
            d.rekt(xx, y + 1, xx + 1, y + 6, 2)
    d.rekt(0, 98, W, 99, 5)
    d.ljus(d.mask_poly([(0, 99), (W, 99), (W, H), (0, H)]) & ((XX * 7 + YY * 3) % 13 == 0), 1.0)
    # Stenfot under fyren
    d.rekt(108, 92, 148, 98, 3)
    d.rekt(108, 92, 148, 93, 4)
    d.rekt(108, 97, 148, 98, 2)
    for xx in range(112, 148, 8):
        d.rekt(xx, 93, xx + 1, 97, 2)
    # Vågor som slår mot pirkanten (animeras)
    for i, sx in enumerate(range(66, W, 14)):
        k = (vfas + i) % 4
        h = (0, 2, 4, 1)[k]
        if h and not (100 < sx < 152):
            d.rekt(sx - h, 97 - h, sx + 4 + h, 98, 5)
            d.rekt(sx - h + 1, 96 - h, sx + 3 + h, 97 - h, 15)
            d.px(sx - h - 1, 95 - h, 5)
            d.px(sx + 5 + h, 94 - h, 15 if k == 2 else 5)
    # Pollare och tågvirke
    d.rekt(6, 102, 14, 112, 0)
    d.rekt(4, 101, 16, 103, 0)
    d.px(7, 104, 4)
    ring(d, 18, 108, 36, 116, 9, 2)
    ring(d, 21, 110, 33, 114, 8, 1)
    d.linje(14, 106, 22, 110, 9)
    t = Duk(16)                                                 # en mås på pollaren
    sprite(t, 4, 93, ["...ww...", "..wkwy..", "nnwwww..", ".nnwwww.", "...ww...", "...yy..."],
           {"w": 15, "k": 0, "y": 10, "n": 4})
    kontur(d, t, 0)

    # --- Fyrvaktaren med lykta ---
    with d.yta("fyrvaktare"):
        kx = 92
        d.rekt(kx - 6, 96, kx - 1, 108, 0)                       # gummistövlar
        d.rekt(kx + 1, 96, kx + 6, 108, 0)
        d.rekt(kx - 7, 106, kx - 1, 108, 0)
        d.rekt(kx + 1, 106, kx + 7, 108, 0)
        d.rekt(kx - 5, 97, kx - 4, 105, 4)
        d.rekt(kx + 2, 97, kx + 3, 105, 4)
        d.rekt(kx - 6, 92, kx + 6, 97, 2)                        # byxor
        d.poly([(kx - 8, 70), (kx + 8, 70), (kx + 9, 94), (kx - 9, 94)], 2)   # sjömanströja/rock
        d.rekt(kx - 8, 70, kx - 6, 94, 3)
        for by_ in (76, 82, 88):
            d.px(kx + 1, by_, 10)
        d.rekt(kx - 12, 72, kx - 7, 86, 2)                       # arm som håller lyktan
        d.rekt(kx - 12, 85, kx - 8, 88, 9)
        d.rekt(kx + 7, 72, kx + 11, 88, 2)                       # andra armen
        d.rekt(kx + 7, 87, kx + 11, 90, 9)
        # Stormlyktan
        d.rekt(kx - 11, 88, kx - 9, 90, 0)
        d.rekt(kx - 14, 90, kx - 6, 100, 0)
        d.rekt(kx - 13, 91, kx - 7, 99, 10)
        d.rekt(kx - 11, 93, kx - 9, 97, 11)
        # Huvud med stort buskigt skägg
        d.rekt(kx - 5, 58, kx + 5, 68, 9)
        d.px(kx - 2, 61, 0)
        d.px(kx + 2, 61, 0)
        d.rekt(kx - 3, 60, kx, 61, 7)
        d.rekt(kx + 1, 60, kx + 4, 61, 7)
        d.rekt(kx - 1, 62, kx + 1, 65, 14)                       # röd näsa
        d.poly([(kx - 7, 64), (kx + 7, 64), (kx + 6, 72), (kx, 76), (kx - 6, 72)], 7)
        d.rekt(kx - 4, 64, kx + 4, 65, 6)
        d.rekt(kx - 2, 67, kx + 2, 68, 6)                        # mun
        for (bx_, by_) in ((kx - 4, 69), (kx + 2, 70), (kx - 1, 73), (kx + 4, 67)):
            d.px(bx_, by_, 8)
        # Sydväst
        d.rekt(kx - 6, 52, kx + 6, 58, 10)
        d.rekt(kx - 8, 57, kx + 8, 59, 10)
        d.poly([(kx + 5, 57), (kx + 11, 59), (kx + 10, 65), (kx + 6, 62)], 10)
        d.rekt(kx - 8, 58, kx + 8, 59, 9)
        d.rekt(kx - 4, 53, kx + 2, 54, 11)
    d.radial(kx - 10, 95, 26, 0.6, mask=(d.a < 10))

    # --- Mistluren på stativ ---
    with d.yta("mistlur2"):
        # Stativ
        for (x0, x1) in ((172, 160), (174, 186), (173, 174)):
            d.linje(x0, 90, x1, 116, 0)
            d.linje(x0 + 1, 90, x1 + 1, 116, 0)
        d.rekt(158, 115, 164, 117, 0)
        d.rekt(184, 115, 190, 117, 0)
        # Hornet: mynning åt vänster, avsmalnar åt höger
        d.poly([(158, 72), (190, 82), (190, 88), (158, 98)], 9)
        d.poly([(158, 72), (190, 82), (190, 84), (158, 78)], 10)
        d.linje(160, 74, 190, 83, 11)
        fyll(d, 150, 70, 164, 100, 9)
        fyll(d, 151, 71, 163, 99, 10)
        fyll(d, 153, 74, 162, 96, 6)
        fyll(d, 155, 78, 161, 92, 0)
        d.rekt(152, 76, 154, 82, 11)
        # Bälgen och veven baktill
        d.rekt(178, 86, 192, 96, 7)
        for bx_ in range(179, 192, 3):
            d.rekt(bx_, 86, bx_ + 1, 96, 6)
        d.rekt(178, 86, 192, 87, 8)
        d.linje(184, 96, 188, 102, 0)
        d.rekt(187, 101, 191, 103, 13)
        d.rekt(166, 88, 176, 89, 0)
        d.rekt(170, 89, 176, 93, 0)
    # Skylt på stativet
    d.rekt(164, 106, 178, 111, 13)
    skriv(d, 165, 106, "FOG", 15)

    # --- Dimma som driver ---
    s = 0.10 + 0.10 * np.sin(2 * np.pi * XX / 80 + YY / 7.0)
    d.ljus((YY > 44) & (YY < 74) & (d.a < 6), s)

    # --- Ljuskäglan (animerad) ---
    lagen = [(math.pi, 130, 0.15), (math.pi + 0.05, 90, 0.2), (math.pi + 0.1, 40, 0.34), (None, 0, 0),
             (0.1, 40, 0.34), (0.05, 70, 0.2), (0.0, 70, 0.15), (None, -1, 0)]
    vinkel, langd, spr = lagen[kfas]
    if vinkel is not None:
        _kagla(d, fx, 15, vinkel, langd, spr)
    elif langd == 0:
        d.radial(fx, 15, 44, 1.0, mask=(YY < 80))
        d.radial(fx, 15, 20, 1.0, mask=(YY < 40) & (d.a < 9))
        d.rekt(fx - 5, 9, fx + 5, 21, 11)

    d.vinjett(0.4)
    return d


SCENER_C = {
    "stadspark": (stadspark, [
        ("regn", "regn", [(i, 90) for i in range(10)]),
        ("rok", "rok", [(i, 220) for i in range(6)]),
    ]),
    "dammen": (dammen, [
        ("ankor", "ankor", [(i, 260) for i in range(8)]),
        ("ringar", "ringar", [(i, 240) for i in range(4)]),
    ]),
    "paviljong": (paviljong, [
        ("regn", "regn", [(i, 90) for i in range(10)]),
        ("tuba", "tuba", [(i, 260) for i in range(6)]),
        ("noter", "noter", [(i, 300) for i in range(6)]),
    ]),
    "fyr": (fyr, [
        ("kagla", "kagla", [(i, 180) for i in range(8)]),
        ("vagor", "vagor", [(i, 300) for i in range(4)]),
    ]),
}
