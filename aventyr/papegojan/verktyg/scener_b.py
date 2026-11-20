import math, random, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "motor" / "verktyg"))
from pixelbild import *  # noqa

"""Scener B till Papegojan som visste för mycket: Boulevardens östra ände, nattklubben
Blå Ostronet (salongen och logen) samt urmakarens butik."""

# Egna extratecken (motorns typsnitt saknar dem). Å ritas som A med en ring ovanför.
EXTRA = {
    "X": ["101", "101", "010", "101", "101"],
    "<": ["001", "010", "100", "010", "001"],
    ">": ["100", "010", "001", "010", "100"],
}


def txt(d, x, y, s, c, spegel=False):
    """Som text(), men klarar även X, <, > och Å (A med ring). spegel=True skriver spegelvänt."""
    for ch in (s[::-1] if spegel else s):
        bas = "A" if ch == "Å" else ch
        glyf = EXTRA.get(bas) or TYPSNITT[bas]
        if spegel:
            glyf = [r[::-1] for r in glyf]
        for ry, rad in enumerate(glyf):
            for rx, bit in enumerate(rad):
                if bit == "1":
                    d.px(x + rx, y + ry, c)
        if ch == "Å":
            d.px(x + 1, y - 3, c)
            d.px(x, y - 2, c)
            d.px(x + 2, y - 2, c)
        x += len(glyf[0]) + 1


def bredd(s):
    return sum(len((EXTRA.get("A" if ch == "Å" else ch) or TYPSNITT["A" if ch == "Å" else ch])[0]) + 1 for ch in s) - 1


def ring(d, x0, y0, x1, y1, c, tjock=1):
    """Ellipskontur."""
    m = d.mask_ellips(x0, y0, x1, y1) & ~d.mask_ellips(x0 + tjock, y0 + tjock, x1 - tjock, y1 - tjock)
    d.a[m] = c


def fyll(d, x0, y0, x1, y1, c):
    d.a[d.mask_ellips(x0, y0, x1, y1)] = c


def gatlykta(d, x, ytop, ybot):
    d.rekt(x - 1, ytop, x + 1, ybot, 0)
    d.rekt(x - 2, ybot - 3, x + 2, ybot, 0)
    d.rekt(x - 4, ytop - 7, x + 4, ytop - 6, 0)
    d.poly([(x - 4, ytop - 6), (x + 4, ytop - 6), (x + 3, ytop), (x - 3, ytop)], 10)
    d.rekt(x - 2, ytop - 5, x + 2, ytop - 1, 11)
    d.rekt(x - 1, ytop - 9, x + 1, ytop - 7, 0)
    d.radial(x, ytop - 3, 12, 0.6, mask=d.a < 5)


def blank_gata(d, y0, reflexer):
    """Våt gata med spegelreflexer: reflexer = [(x0, x1, styrka), ...]."""
    for (x0, x1, f) in reflexer:
        for y in range(y0, H):
            s = f * (1 - (y - y0) / (H - y0))
            m = (XX >= x0) & (XX < x1) & (YY == y) & ((XX + y) % 2 == 0)
            d.ljus(m, s * 2)


# ======================================================================
#  BOULEVARDEN, ÖSTRA ÄNDEN: NATTKLUBBEN BLÅ OSTRONET
# ======================================================================
def blvd_o(v=None):
    v = v or {}
    regn = v.get("regn", 0)        # regnets fas 0..9
    neon = v.get("neon", 2)        # 0 släckt, 1 tänd och stängd, 2 tänd och öppen
    rnd = random.Random(1947)
    d = Duk(1)

    # --- Himmel och avlägsna hus ---
    d.vgrad(0, 0, W, 60, [0, 0, 1, 2])
    x = 0
    while x < W:
        b = rnd.randint(6, 12)
        topp = rnd.randint(10, 30)
        d.rekt(x, topp, x + b, 70, 1)
        for wy in range(topp + 2, 66, 3):
            for wx in range(x + 1, x + b - 1, 2):
                if rnd.random() < 0.12:
                    d.px(wx, wy, 9)
        x += b

    # --- Hamnen nedanför till höger: vatten och master ---
    with d.yta("utgang:ö"):
        d.vgrad(146, 50, W, 72, [2, 2, 3])
        d.rekt(146, 72, W, 96, 1)
        for y in range(73, 96, 2):
            for xx in range(146 + (y * 5) % 7, W, 9):
                d.rekt(xx, y, xx + 3, y + 1, 2 if y > 84 else 3)
        # Lagerbod på andra sidan
        d.rekt(176, 60, W, 72, 0)
        d.poly([(174, 60), (W, 52), (W, 60)], 0)
        d.px(182, 66, 10)
        d.px(186, 66, 10)
        for lx_ in (182, 186):
            for y in range(74, 92, 2):
                if (y + lx_) % 3:
                    d.px(lx_ + (y % 4) // 2, y, 10 if y < 82 else 9)
        # Båtar och master
        for (bx, mh, lang) in [(152, 30, 18), (172, 38, 14)]:
            d.poly([(bx - 2, 70), (bx + lang + 2, 70), (bx + lang - 1, 76), (bx + 1, 76)], 0)
            d.rekt(bx + 4, 66, bx + lang - 5, 70, 0)
            mx = bx + lang // 2
            d.rekt(mx, 70 - mh, mx + 1, 70, 0)
            d.rekt(mx - 5, 74 - mh, mx + 6, 75 - mh, 0)
            d.linje(mx, 71 - mh, bx - 1, 70, 2)
            d.linje(mx, 71 - mh, bx + lang + 1, 70, 2)
            d.px(mx, 69 - mh, 13)
            d.px(bx + 6, 68, 10)
            for y in range(77, 92, 2):
                if (y // 2) % 2:
                    d.px(bx + 6 + (y % 3), y, 9)
        d.px(162, 37, 11)
        d.radial(162, 38, 4, 0.5)
        # Kajkant och gatan som sluttar ner
        d.poly([(146, 86), (W, 93), (W, 98), (146, 98)], 3)
        d.vgrad(146, 93, W, 98, [3, 2])
        d.poly([(146, 86), (W, 93), (W, 95), (146, 88)], 4)
        # Pilskylt mot hamnen
        d.rekt(175, 58, 177, 96, 0)
        d.poly([(156, 48), (184, 48), (190, 53), (184, 58), (156, 58)], 15)
        d.poly([(157, 49), (184, 49), (189, 53), (184, 57), (157, 57)], 12)
        txt(d, 160, 51, "HARBOR", 15)
        d.radial(166, 50, 14, 0.3, mask=d.a > 11)
    d.markera("utgang:ö", 150, 30, W, 102)

    # --- Huset till vänster (tegel) ---
    d.rekt(0, 8, 22, 98, 7)
    d.ljus(d.mask_poly([(0, 8), (22, 8), (22, 98), (0, 98)]), 0.5, MORKARE)
    for y in range(10, 86, 3):
        off = 0 if (y // 3) % 2 else 3
        for xx in range(off, 22, 6):
            d.px(xx, y, 6)
    for fy in (14, 32, 50):
        d.rekt(4, fy, 16, fy + 11, 6)
        d.rekt(5, fy + 1, 15, fy + 10, 1 if fy != 32 else 9)
        if fy == 32:
            d.rekt(5, fy + 6, 15, fy + 10, 8)
        d.rekt(4, fy + 10, 17, fy + 11, 4)
    d.rekt(21, 8, 22, 98, 6)

    # --- Klubbhuset: art deco ---
    d.rekt(22, 6, 146, 98, 2)
    d.poly([(58, 6), (62, 2), (106, 2), (110, 6)], 2)
    d.rekt(64, 0, 104, 2, 2)
    for px_ in range(24, 146, 12):
        d.rekt(px_, 6, px_ + 2, 86, 3)
        d.rekt(px_, 6, px_ + 1, 86, 4)
    d.rekt(22, 6, 146, 8, 4)
    d.rekt(22, 50, 146, 52, 3)
    d.ljus(d.mask_poly([(22, 0), (146, 0), (146, 98), (22, 98)]), 0.35, MORKARE)
    # Fönster i övervåningen
    for fx in list(range(28, 60, 12)) + list(range(112, 144, 12)):
        for fy in (12, 30):
            d.rekt(fx, fy, fx + 6, fy + 12, 0)
            if rnd.random() < 0.35:
                d.rekt(fx + 1, fy + 1, fx + 5, fy + 12, 9)
                d.rekt(fx + 1, fy + 7, fx + 5, fy + 12, 8)
            else:
                d.rekt(fx + 1, fy + 1, fx + 5, fy + 12, 1)
                d.px(fx + 2, fy + 2, 3)
            d.rekt(fx - 1, fy + 12, fx + 7, fy + 13, 4)

    # --- Neonskylten: ett ostron med en pärla ---
    with d.yta("neonostron"):
        d.rekt(56, 10, 112, 53, 0)
        d.rekt(56, 10, 112, 11, 3)
        d.rekt(56, 52, 112, 53, 3)
        tand = neon > 0
        ror = 5 if tand else 3
        kärna = 15 if tand else 3
        oppen = 3 if neon == 2 else 0
        # Ostronet i sidovy, gångjärnet till höger. Övre skalet fälls upp.
        hx, hy = 104, 32
        theta = math.radians(22 if neon == 2 else 0)

        def skal(upp, vrid):
            pts = []
            for k in range(25):
                t = math.pi * k / 24
                bump = 1 if k % 3 == 1 else 0
                px_ = 84 - 20 * math.cos(t)
                py_ = hy + ((-8 - bump) if upp else (11 + bump)) * math.sin(t)
                dx, dy = px_ - hx, py_ - hy
                pts.append((hx + dx * math.cos(vrid) - dy * math.sin(vrid), hy + dx * math.sin(vrid) + dy * math.cos(vrid)))
            return pts

        undre = skal(False, 0)
        ovre = skal(True, theta)
        if theta:
            # Insidan och pärlan
            d.poly([(hx, hy), undre[0], ovre[0]], 1)
            d.poly([(hx, hy), undre[0], (ovre[0][0] + 2, ovre[0][1] + 2)], 13 if tand else 2)
            d.ljus(d.mask_poly([(hx, hy), undre[0], ovre[0]]), 0.5, MORKARE)
            fyll(d, 71, 24, 80, 33, 15 if tand else 4)
            fyll(d, 72, 25, 79, 32, 11 if tand else 4)
            d.rekt(73, 26, 75, 28, 15)
        for pts in (undre, ovre):
            d.poly(pts, 1)
            for k in range(2, 24, 2):
                d.linje(hx - 2, hy, int(pts[k][0]), int(pts[k][1]), 2)
            for a, b in zip(pts, pts[1:]):
                d.linje(int(round(a[0])), int(round(a[1])), int(round(b[0])), int(round(b[1])), ror)
            d.linje(int(round(pts[0][0])), int(round(pts[0][1])), hx, hy, ror)
            if tand:
                for k in (4, 10, 16):
                    d.px(int(round(pts[k][0])), int(round(pts[k][1])), kärna)
        # Text
        txt(d, 84 - bredd("BLÅ OSTRONET") // 2, 46, "BLÅ OSTRONET", 5 if tand else 3)
        if tand:
            d.radial(84, 32, 34, 0.35, mask=(d.a < 4) & ~((XX >= 56) & (XX < 112) & (YY >= 10) & (YY < 53)))
            d.radial(84, 34, 22, 0.25, mask=(d.a < 2))

    # --- Entrén med baldakin och mässingsdörrar ---
    with d.yta("utgang:in"):
        d.rekt(70, 58, 100, 88, 6)
        d.rekt(72, 60, 98, 88, 0)
        for (dx0, dx1) in [(72, 85), (85, 98)]:
            d.rekt(dx0, 60, dx1, 88, 9)
            d.rekt(dx0 + 1, 61, dx1 - 1, 88, 10)
            d.rekt(dx0 + 1, 61, dx0 + 2, 88, 11)
            d.rekt(dx0 + 2, 78, dx1 - 2, 86, 9)
            fyll(d, dx0 + 3, 64, dx1 - 3, 74, 8)
            fyll(d, dx0 + 4, 65, dx1 - 4, 73, 11)
            fyll(d, dx0 + 5, 66, dx1 - 5, 70, 15)
        d.rekt(84, 60, 86, 88, 8)
        d.px(82, 76, 6)
        d.px(87, 76, 6)
        # Baldakinen
        d.poly([(64, 52), (106, 52), (110, 58), (60, 58)], 13)
        d.rekt(60, 58, 110, 59, 6)
        for fx in range(61, 110, 2):
            d.px(fx, 59, 10)
        for fx in range(62, 110, 4):
            d.px(fx, 60, 10)
        d.rekt(64, 52, 106, 53, 14)
        txt(d, 76, 54, "CLUB", 15)
        # Trappsteg och röd matta över trottoaren
        d.rekt(68, 88, 102, 90, 4)
        d.poly([(74, 90), (96, 90), (100, 97), (70, 97)], 13)
        d.poly([(74, 90), (96, 90), (97, 91), (73, 91)], 14)
        d.radial(85, 74, 22, 0.5, mask=(YY > 52) & (YY < 98) & (d.a < 9) & ~((XX >= 72) & (XX < 98) & (YY < 88)))

    # --- Inglasad affisch med Lola LaRue ---
    with d.yta("lolaaffisch"):
        d.rekt(30, 56, 58, 88, 9)
        d.rekt(31, 57, 57, 87, 13)
        d.vgrad(31, 57, 57, 87, [6, 13, 13])
        txt(d, 44 - bredd("LOLA") // 2, 59, "LOLA", 15)
        # Sångerskan i siluett med spotlight
        fyll(d, 36, 66, 52, 86, 14)
        d.ljus(d.mask_ellips(36, 66, 52, 86), 0.5, MORKARE)
        fyll(d, 41, 65, 47, 71, 10)
        fyll(d, 40, 64, 48, 69, 13)
        d.px(42, 68, 0)
        d.px(45, 68, 0)
        d.poly([(41, 72), (47, 72), (46, 77), (49, 85), (39, 85), (42, 77)], 0)
        d.px(42, 74, 11)
        d.px(45, 79, 11)
        d.linje(47, 73, 51, 69, 10)
        d.rekt(38, 73, 41, 74, 15)
        d.rekt(47, 73, 50, 74, 15)
        d.rekt(31, 80, 57, 87, 0)
        txt(d, 44 - bredd("LARUE") // 2, 81, "LARUE", 10)
        # Glaset blänker
        for i in range(5):
            d.px(52 + i // 2, 58 + i, 5)
        d.rekt(29, 55, 59, 56, 4)
        d.rekt(29, 88, 59, 89, 4)

    # --- Trottoar och gata ---
    d.rekt(0, 88, 146, 98, 3)
    d.vgrad(0, 88, 146, 96, [2, 3])
    d.poly([(74, 90), (96, 90), (100, 97), (70, 97)], 13)
    d.poly([(74, 90), (96, 90), (97, 91), (73, 91)], 14)
    d.rekt(0, 96, 146, 98, 4)
    d.poly([(146, 96), (W, 101), (W, 103), (146, 98)], 4)
    d.rekt(0, 98, W, H, 1)
    d.poly([(146, 98), (W, 103), (W, 98)], 3)
    d.vgrad(0, 99, W, H, [0, 1, 1])
    for y in range(101, H, 4):
        for xx in range((y * 3) % 8, W, 8):
            d.px(xx, y, 2)
    for xx in range(0, W, 16):
        d.rekt(xx, 109, xx + 8, 110, 2)
    refl = [(72, 98, 0.55), (136, 144, 0.6)]
    if neon:
        refl.append((66, 104, 0.3))
    blank_gata(d, 99, refl)
    if neon:
        for y in range(100, H, 2):
            for xx in range(70, 100, 3):
                if (xx + y) % 5 == 0:
                    d.px(xx, y, 4 if y > 110 else 5)

    # --- Gatan fortsätter västerut ---
    with d.yta("utgang:v"):
        d.rekt(9, 62, 11, 98, 0)
        d.poly([(2, 66), (8, 60), (24, 60), (24, 72), (8, 72)], 15)
        d.poly([(3, 66), (8, 61), (23, 61), (23, 71), (8, 71)], 12)
        txt(d, 9, 63, "BLVD", 15)
        d.markera("utgang:v", 0, 98, 12, H)

    # --- Gatlykta ---
    gatlykta(d, 138, 40, 97)
    d.radial(138, 94, 24, 0.6, mask=(YY > 87) & (YY < 99))

    # --- Dörrvakten: en mycket stor man i smoking ---
    with d.yta("dorrvakt"):
        bx = 106
        # Ben och skor
        d.rekt(bx + 5, 76, bx + 11, 95, 0)
        d.rekt(bx + 13, 76, bx + 19, 95, 0)
        d.rekt(bx + 4, 94, bx + 12, 97, 0)
        d.rekt(bx + 12, 94, bx + 20, 97, 0)
        d.px(bx + 6, 95, 4)
        d.px(bx + 18, 95, 4)
        d.rekt(bx + 11, 82, bx + 13, 95, 1)
        # Bålen
        d.poly([(bx, 54), (bx + 24, 54), (bx + 23, 78), (bx + 1, 78)], 0)
        d.poly([(bx + 9, 54), (bx + 15, 54), (bx + 12, 64)], 15)
        d.poly([(bx + 6, 54), (bx + 9, 54), (bx + 12, 64), (bx + 10, 64)], 2)
        d.poly([(bx + 15, 54), (bx + 18, 54), (bx + 14, 64), (bx + 12, 64)], 2)
        d.rekt(bx + 10, 55, bx + 15, 57, 0)
        d.px(bx + 12, 56, 1)
        d.px(bx + 12, 60, 0)
        # Korslagda armar
        d.rekt(bx - 1, 64, bx + 25, 71, 0)
        d.rekt(bx - 1, 64, bx + 25, 65, 2)
        d.linje(bx + 2, 70, bx + 22, 65, 2)
        d.rekt(bx + 3, 66, bx + 6, 69, 9)
        d.rekt(bx + 19, 67, bx + 22, 70, 8)
        d.rekt(bx + 6, 66, bx + 7, 69, 15)
        d.rekt(bx + 18, 67, bx + 19, 70, 15)
        # Huvudet
        d.rekt(bx + 8, 50, bx + 16, 54, 8)
        fyll(d, bx + 6, 38, bx + 18, 52, 9)
        d.rekt(bx + 7, 38, bx + 17, 41, 0)
        d.rekt(bx + 6, 40, bx + 7, 44, 0)
        d.rekt(bx + 17, 40, bx + 18, 44, 0)
        d.px(bx + 5, 45, 8)
        d.px(bx + 18, 45, 8)
        d.rekt(bx + 8, 43, bx + 11, 44, 0)
        d.rekt(bx + 13, 43, bx + 16, 44, 0)
        d.px(bx + 9, 45, 0)
        d.px(bx + 14, 45, 0)
        d.rekt(bx + 11, 46, bx + 13, 48, 8)
        d.rekt(bx + 9, 49, bx + 15, 50, 7)
        d.px(bx + 8, 51, 8)
        d.radial(bx + 12, 44, 10, 0.3, mask=(d.a == 9))

    # --- Regn och stämning ---
    regn_over(d, random.Random(11), 95, regn)
    d.vinjett(0.4)
    return d


# ======================================================================
#  NATTKLUBBENS SALONG
# ======================================================================
def klubb(v=None):
    v = v or {}
    lagor = v.get("lagor", 0)      # ljuslågorna 0..3
    hander = v.get("hander", 0)    # pianistens händer 0..3
    torka = v.get("torka", 0)      # bartenderns trasa 0..3
    rnd = random.Random(1950)
    d = Duk(1)

    # Väggar i blå sammet med art deco-solfjädrar i guld
    d.vgrad(0, 0, W, 74, [0, 1, 1, 2])
    for x in range(0, W, 24):
        for k in range(-3, 4):
            d.linje(x + 12, 14, x + 12 + k * 3, 6, 9)
        d.rekt(x + 11, 14, x + 13, 74, 1)
    d.rekt(0, 14, W, 15, 9)
    d.rekt(0, 4, W, 5, 6)
    d.rekt(0, 72, W, 74, 6)
    d.rekt(0, 72, W, 73, 9)
    # Golvet: mörkt rutmönster
    d.rekt(0, 74, W, H, 6)
    for y in range(74, H):
        z = y - 74 + 10
        rad = int(260 / z)
        for x in range(W):
            kol = int((x - W // 2) * 1.6 / z + 100)
            if (kol + rad) % 2:
                d.a[y, x] = 7
    d.vgrad(0, 74, W, 84, [0, 6])
    d.ljus((YY >= 74) & (YY < 84) & (d.a == 7), 0.6, MORKARE)

    # --- Utgången mot gatan ---
    with d.yta("utgang:ut"):
        d.rekt(3, 24, 21, 74, 6)
        d.rekt(5, 26, 19, 74, 7)
        d.rekt(6, 28, 18, 46, 6)
        d.rekt(6, 50, 18, 70, 6)
        d.rekt(7, 29, 17, 45, 7)
        d.rekt(7, 51, 17, 69, 7)
        d.rekt(16, 48, 18, 51, 10)
        d.rekt(5, 16, 19, 23, 12)
        d.rekt(5, 16, 19, 17, 15)
        txt(d, 9, 18, "UT", 15)
        d.radial(12, 20, 12, 0.5, mask=d.a < 4)

    # --- Scenen: sammetsridå och spotlight ---
    with d.yta("scen"):
        d.rekt(66, 4, 128, 70, 13)
        for x in range(66, 128, 6):
            d.rekt(x, 12, x + 2, 70, 6)
            d.rekt(x + 3, 12, x + 4, 70, 14)
            d.ljus(d.mask_poly([(x, 12), (x + 2, 12), (x + 2, 70), (x, 70)]), 0.5, MORKARE)
        # Kappa upptill med guldfrans
        for i, x in enumerate(range(66, 128, 10)):
            d.a[d.mask_ellips(x - 1, 2, x + 11, 16) & (YY >= 6)] = 13
            d.a[d.mask_ellips(x, 10, x + 10, 17) & (YY >= 14)] = 10
        d.rekt(64, 2, 130, 6, 6)
        d.rekt(64, 6, 130, 8, 13)
        # Uppknutna sidor
        d.poly([(64, 6), (72, 6), (70, 40), (73, 70), (64, 70)], 13)
        d.poly([(130, 6), (122, 6), (124, 40), (121, 70), (130, 70)], 13)
        d.rekt(66, 8, 68, 70, 6)
        d.rekt(126, 8, 128, 70, 6)
        d.rekt(66, 40, 72, 42, 10)
        d.rekt(122, 40, 128, 42, 10)
        # Scengolvet
        d.rekt(60, 66, 134, 70, 8)
        d.rekt(60, 66, 134, 67, 9)
        d.rekt(60, 70, 134, 79, 6)
        d.rekt(60, 70, 134, 71, 10)
        for x in range(64, 134, 8):
            d.rekt(x, 74, x + 2, 76, 11)
        d.rekt(60, 79, 134, 80, 0)
        # Spotlight
        d.radial(97, 44, 30, 0.55, mask=(YY < 70) & (XX > 64) & (XX < 130))
        d.radial(97, 68, 22, 0.6, mask=(YY >= 66) & (YY < 71))

    # --- Radiomikrofonen ---
    with d.yta("mikrofon"):
        mx = 97
        d.rekt(mx, 40, mx + 1, 67, 0)
        d.rekt(mx - 4, 66, mx + 6, 68, 0)
        d.rekt(mx - 1, 40, mx + 3, 42, 4)
        # Huvudet (kapselformat)
        fyll(d, mx - 4, 22, mx + 5, 30, 4)
        d.rekt(mx - 4, 26, mx + 6, 38, 4)
        fyll(d, mx - 4, 34, mx + 5, 41, 4)
        for y in range(25, 39, 2):
            d.rekt(mx - 3, y, mx + 5, y + 1, 3)
        d.rekt(mx - 4, 30, mx + 6, 32, 2)
        d.rekt(mx - 3, 24, mx - 2, 38, 5)
        d.px(mx - 3, 24, 15)
        # Stationsskylten
        sx0, sx1 = mx - 11, mx + 12
        d.rekt(sx0 - 1, 43, sx1 + 1, 52, 10)
        d.rekt(sx0, 44, sx1, 51, 15)
        txt(d, mx + 1 - bredd("WGHR") // 2, 45, "WGHR", 13)

    # --- LOGE-dörren ---
    with d.yta("utgang:in"):
        d.rekt(132, 26, 150, 74, 6)
        d.rekt(134, 28, 148, 74, 13)
        d.rekt(135, 29, 147, 74, 6)
        d.ljus(d.mask_poly([(135, 29), (147, 29), (147, 74), (135, 74)]), 0.4)
        # Guldstjärna
        sx, sy = 141, 37
        pts = []
        for k in range(10):
            r = 5 if k % 2 == 0 else 2
            a = -math.pi / 2 + k * math.pi / 5
            pts.append((sx + r * math.cos(a), sy + r * math.sin(a)))
        d.poly(pts, 10)
        d.px(sx, sy - 1, 11)
        d.rekt(132, 44, 151, 53, 10)
        d.rekt(133, 45, 150, 52, 0)
        txt(d, 142 - bredd("LOGE") // 2, 46, "LOGE", 10)
        d.rekt(145, 58, 147, 61, 10)

    # --- Baren ---
    with d.yta("bartender"):
        # Bakvägg med speglar och flaskor
        d.rekt(152, 14, W, 62, 6)
        d.rekt(154, 16, W, 60, 3)
        d.vgrad(154, 16, W, 60, [4, 3, 2])
        for hy in (28, 42, 56):
            d.rekt(152, hy, W, hy + 2, 8)
            d.rekt(152, hy, W, hy + 1, 9)
            x = 155
            while x < W - 2:
                c = rnd.choice([12, 13, 10, 9, 5, 7, 12])
                hh = rnd.randint(6, 9)
                d.rekt(x, hy - hh + 2, x + 3, hy, c)
                d.rekt(x + 1, hy - hh, x + 2, hy - hh + 2, c)
                d.px(x, hy - hh + 3, 11 if c in (10, 5, 9) else LJUSARE[c])
                x += rnd.randint(4, 6)
        d.radial(174, 36, 26, 0.35, mask=(YY > 16) & (YY < 60))
        # Bartendern
        bx = 170
        d.rekt(bx - 6, 48, bx + 8, 66, 15)            # vit kavaj
        d.rekt(bx - 6, 48, bx - 5, 66, 5)
        d.poly([(bx - 1, 48), (bx + 3, 48), (bx + 1, 54)], 0)
        d.rekt(bx - 1, 48, bx + 3, 50, 13)            # fluga
        d.px(bx + 1, 49, 14)
        d.rekt(bx - 2, 46, bx + 4, 48, 9)             # hals
        fyll(d, bx - 4, 34, bx + 6, 47, 10)            # ansikte
        d.rekt(bx - 4, 34, bx + 6, 38, 0)              # slickat hår
        d.px(bx - 4, 39, 0)
        d.px(bx + 5, 39, 0)
        d.px(bx + 1, 35, 4)
        d.px(bx - 1, 40, 0)
        d.px(bx + 3, 40, 0)
        d.rekt(bx - 2, 43, bx + 5, 44, 0)              # mustasch
        d.px(bx + 1, 42, 9)
        # Glaset och trasan
        gx, gy = bx - 3, 56
        d.rekt(gx, gy, gx + 4, gy + 6, 5)
        d.rekt(gx + 1, gy + 1, gx + 3, gy + 5, 4)
        d.px(gx, gy, 15)
        d.rekt(gx + 1, gy + 6, gx + 3, gy + 7, 5)
        tx = [(-3, 54), (-2, 58), (1, 55), (-1, 59)][torka]
        d.rekt(gx + tx[0], tx[1], gx + tx[0] + 5, tx[1] + 4, 15)
        d.rekt(gx + tx[0], tx[1] + 3, gx + tx[0] + 5, tx[1] + 4, 5)
        d.rekt(gx - 3, 60, gx + 1, 62, 10)             # händer
        d.rekt(gx + 4, 58 + (torka % 2), gx + 7, 60 + (torka % 2), 10)
        # Bardisken
        d.rekt(150, 62, W, 67, 8)
        d.rekt(150, 62, W, 63, 9)
        d.rekt(150, 67, W, 100, 6)
        for x in range(154, W, 10):
            d.rekt(x, 70, x + 7, 92, 7)
            d.rekt(x, 70, x + 7, 71, 8)
        d.rekt(150, 94, W, 95, 10)
        d.rekt(150, 99, W, 100, 0)
        # Barstolar
        for sx in (160, 182):
            d.rekt(sx - 4, 82, sx + 5, 85, 13)
            d.rekt(sx - 4, 82, sx + 5, 83, 14)
            d.rekt(sx, 85, sx + 1, 102, 10)
            d.rekt(sx - 3, 101, sx + 4, 103, 10)

    # --- Flygeln och den nervösa pianisten ---
    with d.yta("pianist"):
        # Flygeln (sidovy, tangenterna till vänster)
        d.poly([(36, 72), (64, 72), (72, 76), (72, 84), (36, 84)], 0)
        d.poly([(38, 72), (68, 72), (46, 52)], 0)             # uppfällt lock
        d.linje(38, 71, 46, 53, 4)
        d.linje(46, 53, 68, 71, 3)
        d.linje(54, 71, 52, 60, 4)                             # lockstöd
        d.rekt(36, 72, 72, 73, 4)
        d.linje(64, 72, 72, 76, 4)
        d.rekt(38, 77, 70, 78, 2)
        d.rekt(36, 83, 72, 84, 2)
        d.rekt(32, 73, 38, 76, 15)                             # tangenter
        for kx in range(32, 38, 2):
            d.px(kx, 73, 0)
        d.rekt(36, 64, 40, 72, 15)                             # notställ med noter
        d.rekt(37, 65, 39, 66, 4)
        d.rekt(37, 67, 39, 68, 4)
        d.rekt(37, 69, 39, 70, 4)
        for lx in (38, 68):
            d.rekt(lx, 84, lx + 2, 100, 0)
            d.px(lx, 99, 10)
            d.px(lx, 85, 3)
        d.rekt(52, 84, 54, 96, 0)
        d.rekt(50, 96, 56, 97, 0)                              # pedaler
        d.px(51, 96, 10)
        d.px(54, 96, 10)
        # Pallen
        d.rekt(14, 84, 30, 87, 7)
        d.rekt(14, 84, 30, 85, 8)
        d.rekt(15, 87, 16, 100, 0)
        d.rekt(28, 87, 29, 100, 0)
        # Pianisten: lång, smal, mittbena, vita handskar
        p = 18
        d.rekt(p + 2, 63, p + 9, 85, 0)                       # frack
        d.rekt(p + 2, 63, p + 3, 85, 2)                       # kantljus
        d.poly([(p + 2, 80), (p + 5, 80), (p + 3, 90), (p + 1, 90)], 0)   # frackskört
        d.rekt(p + 6, 64, p + 9, 74, 15)                      # skjortbröst
        d.rekt(p + 6, 63, p + 10, 65, 0)                      # fluga
        d.px(p + 8, 64, 2)
        d.rekt(p + 7, 81, p + 18, 84, 0)                      # lår
        d.rekt(p + 15, 84, p + 17, 98, 0)                     # smalben
        d.rekt(p + 15, 98, p + 20, 100, 0)
        d.px(p + 18, 98, 3)
        d.rekt(p + 5, 59, p + 8, 63, 10)                      # lång hals
        d.px(p + 6, 61, 9)
        fyll(d, p + 2, 47, p + 12, 60, 10)                     # huvud
        d.rekt(p + 3, 47, p + 12, 50, 0)                      # hår, blankt och mittbenat
        d.px(p + 2, 50, 0)
        d.px(p + 2, 51, 0)
        d.px(p + 12, 50, 0)
        d.rekt(p + 7, 47, p + 8, 50, 10)                      # mittbenan
        d.px(p + 5, 48, 3)
        d.px(p + 10, 48, 3)
        d.px(p + 2, 54, 9)                                     # öra
        d.rekt(p + 6, 51, p + 8, 52, 0)                       # höjda ögonbryn
        d.rekt(p + 9, 51, p + 11, 52, 0)
        d.rekt(p + 6, 52, p + 8, 55, 15)                      # stora nervösa ögon
        d.rekt(p + 9, 52, p + 11, 55, 15)
        d.px(p + 6, 53, 0)                                     # som sneglar mot publiken
        d.px(p + 9, 53, 0)
        d.px(p + 11, 56, 9)                                    # näsa
        d.px(p + 7, 58, 8)                                     # darrig mun
        d.px(p + 8, 57, 8)
        d.px(p + 9, 58, 8)
        d.px(p + 10, 57, 8)
        d.px(p + 1, 52, 5)                                     # svettdroppar
        d.px(p + 0, 55, 5)
        d.px(p + 0, 56, 4)
        # Armar och vita handskar som springer över tangenterna
        h1, h2 = [(70, 71), (71, 69), (69, 70), (71, 71)][hander]
        d.linje(p + 6, 66, p + 10, 72, 0)
        d.linje(p + 10, 72, p + 14, 72, 0)
        d.rekt(p + 14, h1, p + 17, h1 + 2, 15)
        d.linje(p + 8, 66, p + 15, 70, 0)
        d.linje(p + 15, 70, p + 17, 70, 0)
        d.rekt(p + 17, h2, p + 20, h2 + 2, 15)
        # Noter som svävar
        d.px(44, 48 - hander, 15)
        d.rekt(45, 45 - hander, 46, 48 - hander, 15)


    # --- Runda bord med levande ljus ---
    with d.yta("bord"):
        for (tx, ty, tr) in [(84, 100, 13), (124, 108, 14)]:
            d.rekt(tx - tr + 2, ty + 2, tx + tr - 1, ty + 12, 15)
            d.rekt(tx - tr + 2, ty + 6, tx + tr - 1, ty + 12, 5)
            for fx in range(tx - tr + 3, tx + tr - 1, 4):
                d.rekt(fx, ty + 4, fx + 1, ty + 12, 4)
            fyll(d, tx - tr, ty - 3, tx + tr, ty + 5, 15)
            d.rekt(tx - 2, ty + 12, tx + 2, H, 0)
            # Ljuset
            d.rekt(tx - 1, ty - 4, tx + 2, ty + 1, 15)
            d.rekt(tx - 2, ty - 1, tx + 3, ty + 1, 13)
            f = [(0, 0), (1, -1), (0, 1), (-1, 0)][(lagor + tx) % 4]
            d.px(tx + f[0], ty - 6 + f[1], 10)
            d.px(tx, ty - 5, 11)
            d.px(tx + f[0] // 2, ty - 7 + f[1], 10 if f[1] < 1 else 11)
            d.radial(tx, ty - 3, 18, 0.45, mask=(d.a == 15) | (d.a == 5) | (d.a == 6) | (d.a == 0))
            # Champagneglas
            d.rekt(tx + 5, ty - 3, tx + 9, ty - 2, 10)
            d.px(tx + 7, ty - 2, 5)
            d.px(tx + 7, ty - 1, 5)
            d.rekt(tx + 6, ty, tx + 9, ty + 1, 5)
        # Askkopp
        d.rekt(76, 99, 80, 101, 4)
        d.px(78, 98, 5)

    # Rök under taket
    for i in range(30):
        x, y = rnd.randint(30, 150), rnd.randint(18, 40)
        if d.a[y, x] < 3:
            d.px(x, y, 2)

    d.vinjett(0.3)
    return d


# ======================================================================
#  LOLAS LOGE
# ======================================================================
def papegoja(d, x, y, huvud=0):
    """Färggrann ara. (x, y) = kroppens övre vänstra hörn. huvud 0 rakt, 1 på sned, 2 vänd."""
    # Lång stjärt
    d.poly([(x + 4, y + 16), (x + 10, y + 16), (x + 9, y + 34), (x + 6, y + 34)], 13)
    d.poly([(x + 7, y + 20), (x + 9, y + 20), (x + 8, y + 34)], 3)
    # Kropp
    fyll(d, x, y, x + 12, y + 20, 13)
    d.rekt(x + 1, y + 5, x + 3, y + 14, 14)
    # Vinge: gul, grön, blå
    d.poly([(x + 6, y + 3), (x + 13, y + 4), (x + 12, y + 20), (x + 8, y + 23)], 3)
    d.poly([(x + 6, y + 3), (x + 13, y + 4), (x + 12, y + 9), (x + 7, y + 8)], 10)
    d.rekt(x + 7, y + 9, x + 13, y + 12, 12)
    d.linje(x + 9, y + 13, x + 10, y + 21, 4)
    d.linje(x + 11, y + 13, x + 11, y + 19, 2)
    # Fötter på pinnen
    d.rekt(x + 3, y + 19, x + 5, y + 22, 0)
    d.rekt(x + 7, y + 19, x + 9, y + 22, 0)
    # Huvud
    hy = y - 8 + (1 if huvud == 1 else 0)
    hx = x + 1
    fyll(d, hx, hy, hx + 11, hy + 10, 13)
    d.px(hx + 5, hy, 14)
    d.px(hx + 6, hy + 1, 14)
    if huvud == 2:
        d.rekt(hx + 5, hy + 3, hx + 10, hy + 7, 15)    # vit kind, vänd åt höger
        d.px(hx + 6, hy + 4, 0)
        d.rekt(hx + 10, hy + 3, hx + 13, hy + 6, 15)   # krokig näbb
        d.px(hx + 13, hy + 4, 15)
        d.px(hx + 13, hy + 6, 0)
        d.rekt(hx + 10, hy + 6, hx + 12, hy + 7, 0)
    else:
        d.rekt(hx + 1, hy + 3, hx + 6, hy + 7, 15)
        d.px(hx + 4, hy + 4 - (1 if huvud == 1 else 0), 0)
        d.rekt(hx - 2, hy + 3, hx + 1, hy + 6, 15)
        d.px(hx - 3, hy + 4, 15)
        d.px(hx - 3, hy + 6, 0)
        d.rekt(hx - 1, hy + 6, hx + 1, hy + 7, 0)


def logen(v=None):
    v = v or {}
    huvud = v.get("huvud", 0)      # papegojans huvud 0..2
    lampor = v.get("lampor", 0)    # vilken lampa runt spegeln som blinkar 0..3
    tackt = v.get("tackt", False)  # buren övertäckt av trenchcoaten
    rnd = random.Random(1946)
    d = Duk(6)

    # Randiga tapeter i rosa och brunt
    d.vgrad(0, 0, W, 92, [6, 7, 7])
    d.rekt(0, 0, W, 92, 6)
    for x in range(0, W, 10):
        d.rekt(x, 0, x + 4, 92, 7)
        for y in range(0, 92, 2):
            d.px(x + 7, y + (x // 10) % 2, 13)
    for x in range(2, W, 10):
        for y in range(6, 84, 10):
            d.px(x, y, 8)
    d.ljus(YY < 92, np.clip((40 - YY) / 60, 0, 1), MORKARE)
    d.rekt(0, 84, W, 92, 6)
    d.rekt(0, 84, W, 85, 8)
    # Golv med matta
    d.rekt(0, 92, W, H, 7)
    d.vgrad(0, 92, W, H, [6, 7, 8])
    d.poly([(30, 100), (160, 100), (176, 118), (14, 118)], 13)
    d.poly([(33, 102), (157, 102), (171, 116), (19, 116)], 6)
    d.poly([(36, 104), (154, 104), (166, 114), (24, 114)], 13)

    # --- Dörren ut ---
    with d.yta("utgang:ut"):
        d.rekt(2, 20, 22, 92, 6)
        d.rekt(4, 22, 20, 92, 8)
        d.rekt(6, 26, 18, 52, 7)
        d.rekt(6, 58, 18, 88, 7)
        d.rekt(16, 54, 19, 57, 10)
        d.px(17, 55, 11)
        # Morgonrock på kroken
        d.rekt(7, 28, 15, 30, 10)
        d.poly([(6, 30), (16, 30), (17, 60), (5, 60)], 14)
        d.linje(11, 30, 11, 60, 13)
        d.rekt(5, 46, 17, 47, 13)

    # --- Vikskärmen ---
    with d.yta("skarm"):
        for i, (x0, x1) in enumerate([(24, 34), (34, 44), (44, 54)]):
            d.rekt(x0, 30, x1, 98, 6)
            d.rekt(x0 + 1, 32, x1 - 1, 96, 15)
            d.vgrad(x0 + 1, 32, x1 - 1, 96, [15, 15, 9])
            if i == 1:
                d.ljus(d.mask_poly([(x0, 30), (x1, 30), (x1, 98), (x0, 98)]), 0.35, MORKARE)
            # Körsbärsgren
            d.linje(x0 + 1, 50 + i * 6, x1 - 2, 40 + i * 4, 6)
            for k in range(4):
                bx_ = x0 + 2 + rnd.randint(0, x1 - x0 - 4)
                by_ = 38 + i * 4 + rnd.randint(0, 12)
                d.px(bx_, by_, 14)
                d.px(bx_ + 1, by_, 13)
            d.rekt(x0, 30, x1, 32, 8)
            d.rekt(x0 + 2, 96, x0 + 3, 100, 6)
            d.rekt(x1 - 3, 96, x1 - 2, 100, 6)
        # Strumpa över kanten
        d.linje(30, 30, 31, 44, 0)
        d.linje(31, 30, 32, 44, 0)
        d.rekt(31, 44, 34, 46, 0)
        d.linje(34, 30, 34, 31, 0)

    # --- Sminkbordet ---
    with d.yta("sminkbord"):
        d.rekt(70, 54, 126, 58, 9)
        d.rekt(70, 54, 126, 55, 10)
        d.rekt(72, 58, 124, 74, 8)
        d.rekt(74, 60, 96, 72, 7)
        d.rekt(100, 60, 122, 72, 7)
        d.rekt(84, 65, 87, 67, 10)
        d.rekt(110, 65, 113, 67, 10)
        d.rekt(73, 74, 75, 94, 8)
        d.rekt(121, 74, 123, 94, 8)
        # Burkar och flaskor
        d.rekt(78, 49, 82, 54, 12)
        d.rekt(78, 48, 82, 49, 10)
        d.rekt(84, 50, 88, 54, 13)
        d.rekt(84, 49, 88, 50, 15)
        d.rekt(90, 46, 92, 54, 5)
        d.rekt(90, 45, 92, 46, 10)
        d.rekt(104, 47, 108, 54, 14)
        d.rekt(105, 45, 107, 47, 10)
        fyll(d, 108, 44, 111, 47, 13)                  # parfympuff
        d.linje(107, 46, 108, 46, 0)
        # Puderdosa med puderkvast
        d.rekt(112, 51, 122, 54, 14)
        d.rekt(112, 51, 122, 52, 15)
        fyll(d, 113, 46, 121, 52, 15)
        for (fx, fy) in [(114, 47), (117, 46), (119, 48), (115, 50)]:
            d.px(fx, fy, 14)
        d.px(117, 45, 11)
        d.radial(116, 50, 7, 0.3, mask=d.a < 10)

    # --- Spegeln med glödlampor ---
    with d.yta("spegel"):
        d.rekt(76, 8, 122, 52, 8)
        d.rekt(78, 10, 120, 50, 9)
        d.rekt(80, 12, 118, 48, 3)
        d.vgrad(80, 12, 118, 48, [4, 3, 2])
        for k in range(3):
            d.linje(100 + k, 12, 90 + k, 48, 4)
        d.linje(112, 14, 106, 26, 5)
        # Ett fotografi instucket i ramen och en läppstiftshälsning
        d.rekt(81, 13, 87, 21, 15)
        d.rekt(82, 14, 86, 19, 4)
        d.px(84, 16, 10)
        txt(d, 106, 41, "L", 13)
        d.px(110, 42, 13)
        d.px(111, 43, 13)
        d.px(112, 42, 13)
        # Lampor
        lampor_xy = [(x, 9) for x in range(80, 120, 6)] + [(77, y) for y in range(16, 50, 7)] + [(121, y) for y in range(16, 50, 7)]
        for i, (lx, ly) in enumerate(lampor_xy):
            pa = (i + lampor) % 4 != 0
            fyll(d, lx - 1, ly - 1, lx + 2, ly + 2, 11 if pa else 10)
            d.px(lx, ly, 11 if pa else 9)
    for i, (lx, ly) in enumerate(lampor_xy):
        if (i + lampor) % 4 != 0:
            d.radial(lx, ly, 5, 0.45, mask=(d.a < 10) & ((XX < 76) | (XX > 122) | (YY < 8) | (YY > 52)))
    d.radial(99, 40, 46, 0.3, mask=(YY < 100) & (d.a != 11))

    # --- Klädställningen ---
    with d.yta("klader"):
        d.rekt(128, 22, 150, 24, 4)
        d.rekt(128, 22, 150, 23, 5)
        d.rekt(128, 22, 130, 96, 4)
        d.rekt(148, 22, 150, 96, 4)
        d.rekt(125, 96, 133, 98, 4)
        d.rekt(145, 96, 153, 98, 4)
        for i, (kx, c, lang) in enumerate([(131, 12, 54), (136, 13, 62), (141, 10, 46), (145, 14, 58)]):
            d.linje(kx + 2, 24, kx + 2, 26, 5)
            d.poly([(kx - 1, 27), (kx + 5, 27), (kx + 6, 27 + lang), (kx - 2, 27 + lang)], c)
            d.linje(kx - 1, 27, kx - 1, 27 + lang, MORKARE[c])
            for k in range(5):
                d.px(kx + rnd.randint(0, 4), 30 + rnd.randint(0, lang - 6), 11 if c != 10 else 15)
        # Hatt med fjäder på ställningen
        d.rekt(132, 18, 144, 20, 0)
        d.rekt(134, 13, 142, 18, 0)
        d.rekt(134, 16, 142, 17, 13)
        d.linje(142, 16, 148, 6, 15)
        d.linje(143, 16, 149, 8, 15)
        d.linje(144, 16, 149, 10, 14)

    # --- Fågelburen på stativ ---
    cx = 170
    with d.yta("papegoja"):
        # Stativet
        d.rekt(cx - 1, 68, cx + 2, 102, 9)
        d.rekt(cx, 68, cx + 1, 102, 10)
        d.poly([(cx - 10, 106), (cx, 100), (cx + 11, 106), (cx + 9, 107), (cx, 102), (cx - 8, 107)], 9)
        if not tackt:
            # Insidan av buren
            d.a[d.mask_ellips(cx - 16, 10, cx + 17, 40) & (YY < 26)] = 7
            d.rekt(cx - 16, 26, cx + 17, 64, 7)
            d.ljus(d.mask_poly([(cx - 16, 10), (cx + 17, 10), (cx + 17, 64), (cx - 16, 64)]), 0.5, MORKARE)
            # Pinne och skålar
            d.rekt(cx - 12, 47, cx + 13, 49, 8)
            d.rekt(cx - 1, 49, cx + 1, 62, 8)
            d.rekt(cx - 13, 56, cx - 8, 59, 15)
            d.rekt(cx + 9, 56, cx + 14, 59, 15)
            d.px(cx - 11, 56, 10)
            d.px(cx - 10, 56, 9)
            # Gallret
            for gx in range(cx - 15, cx + 17, 6):
                d.linje(gx, 64, gx, 26, 9)
                d.linje(gx, 26, cx + (gx - cx) // 3, 10, 9)
            ring(d, cx - 16, 10, cx + 17, 42, 10)
            d.rekt(cx - 17, 25, cx + 18, 27, 10)
            papegoja(d, cx - 5, 26, huvud)
            d.rekt(cx - 17, 40, cx + 18, 41, 9)
            d.rekt(cx - 18, 62, cx + 19, 67, 9)
            d.rekt(cx - 18, 62, cx + 19, 63, 10)
            d.rekt(cx - 14, 67, cx + 15, 69, 8)
            d.rekt(cx - 1, 6, cx + 2, 10, 10)
            fyll(d, cx - 2, 3, cx + 3, 8, 10)
        else:
            # Trenchcoaten slängd över buren
            d.poly([(cx - 4, 4), (cx + 5, 4), (cx + 16, 12), (cx + 18, 22), (cx + 19, 68), (cx + 21, 72),
                    (cx - 20, 72), (cx - 18, 68), (cx - 17, 22), (cx - 15, 12)], 9)
            d.poly([(cx - 15, 12), (cx - 8, 9), (cx - 12, 70), (cx - 18, 70), (cx - 17, 22)], 10)   # ljus sida
            for fx, ft, fb in [(cx - 6, 18, 70), (cx + 9, 16, 70), (cx + 14, 24, 70), (cx - 13, 30, 70)]:
                d.linje(fx, ft, fx + (fx - cx) // 8, fb, 8)
            d.poly([(cx - 8, 3), (cx + 9, 3), (cx + 12, 10), (cx + 3, 26), (cx - 2, 26), (cx - 11, 10)], 8)   # krage och slag
            d.poly([(cx - 5, 5), (cx + 6, 5), (cx + 8, 9), (cx + 1, 22), (cx - 8, 9)], 6)
            d.rekt(cx - 16, 11, cx - 8, 14, 8)                                                   # axelklaffar
            d.rekt(cx + 9, 11, cx + 17, 14, 8)
            for by_ in (30, 38, 56):
                d.rekt(cx - 4, by_, cx - 2, by_ + 2, 6)
                d.rekt(cx + 4, by_, cx + 6, by_ + 2, 6)
            d.rekt(cx - 18, 45, cx + 20, 49, 8)                                                  # bältet
            d.rekt(cx - 4, 44, cx + 3, 50, 10)
            d.rekt(cx - 2, 46, cx + 1, 48, 8)
            d.poly([(cx + 3, 47), (cx + 7, 47), (cx + 9, 64), (cx + 6, 65)], 8)                 # bältesände
            d.poly([(cx - 23, 14), (cx - 16, 13), (cx - 18, 62), (cx - 24, 62)], 9)            # hängande ärm
            d.linje(cx - 17, 16, cx - 19, 61, 8)
            d.rekt(cx - 24, 56, cx - 18, 58, 8)
            d.rekt(cx - 24, 62, cx - 18, 64, 8)
            d.linje(cx - 21, 72, cx + 20, 72, 8)                                                 # fållen
            d.rekt(cx - 18, 68, cx + 19, 70, 10)
    d.radial(cx, 36, 30, 0.25, mask=(d.a < 10) & (YY < 70))

    # --- Lola LaRue ---
    with d.yta("lola"):
        lx = 58
        # Klänningen: paljetter i djupblått, sjöjungfrusnitt
        d.poly([(lx + 2, 42), (lx + 12, 42), (lx + 11, 58), (lx + 13, 78), (lx + 18, 98), (lx - 4, 98), (lx + 1, 78), (lx + 3, 58)], 2)
        for y in range(42, 98):
            for x in range(lx - 4, lx + 18):
                if d.a[y, x] == 2:
                    t = TROSKEL[y, x]
                    if t < 0.25:
                        d.a[y, x] = 3
                    elif t > 0.9 and (x * 7 + y * 3) % 5 == 0:
                        d.a[y, x] = 11
                    elif t > 0.8:
                        d.a[y, x] = 5
        d.rekt(lx + 2, 42, lx + 12, 43, 4)
        # Bara axlar, hals och armar
        d.rekt(lx + 2, 38, lx + 12, 42, 10)
        d.rekt(lx + 5, 34, lx + 9, 38, 10)
        d.linje(lx + 1, 40, lx - 1, 52, 10)        # vänster arm mot höften
        d.linje(lx + 2, 40, lx, 52, 10)
        d.linje(lx - 1, 52, lx + 3, 58, 15)        # handske
        d.linje(lx, 52, lx + 4, 58, 15)
        d.linje(lx + 13, 40, lx + 18, 32, 10)      # höger arm upp mot håret
        d.linje(lx + 12, 40, lx + 17, 32, 10)
        d.rekt(lx + 16, 28, lx + 19, 33, 15)
        # Huvudet med röda vågor
        fyll(d, lx, 16, lx + 15, 32, 13)            # svallande hår
        fyll(d, lx - 1, 24, lx + 4, 38, 13)
        fyll(d, lx + 11, 24, lx + 16, 37, 13)
        for (hx_, hy_) in [(lx + 1, 26), (lx, 31), (lx + 13, 27), (lx + 14, 32), (lx + 4, 18), (lx + 9, 17)]:
            d.px(hx_, hy_, 14)
            d.px(hx_ + 1, hy_ + 1, 14)
        fyll(d, lx + 3, 21, lx + 12, 36, 10)        # ansikte
        d.linje(lx + 3, 22, lx + 8, 20, 13)          # lugg i en våg
        d.linje(lx + 3, 23, lx + 7, 21, 13)
        d.px(lx + 4, 21, 14)
        d.rekt(lx + 4, 26, lx + 7, 27, 0)          # ögonfransar
        d.rekt(lx + 9, 26, lx + 12, 27, 0)
        d.px(lx + 5, 27, 3)
        d.px(lx + 10, 27, 3)
        d.rekt(lx + 6, 31, lx + 10, 32, 13)        # röda läppar
        d.px(lx + 8, 32, 14)
        d.px(lx + 11, 29, 6)                        # skönhetsfläck
        d.rekt(lx + 4, 25, lx + 7, 26, 3)          # ögonskugga
        d.rekt(lx + 9, 25, lx + 12, 26, 3)
        d.rekt(lx + 5, 38, lx + 10, 39, 15)         # pärlhalsband
        d.px(lx + 7, 39, 15)
        # Fjäderboa
        boa = [(lx - 1, 42), (lx + 2, 40), (lx + 6, 41), (lx + 10, 41), (lx + 13, 40), (lx + 15, 43),
               (lx + 16, 48), (lx + 17, 54), (lx + 18, 60), (lx + 18, 66), (lx - 2, 46), (lx - 4, 52),
               (lx - 5, 58), (lx - 5, 64), (lx - 6, 70)]
        for (bx_, by_) in boa:
            fyll(d, bx_ - 2, by_ - 2, bx_ + 3, by_ + 3, 14)
        for (bx_, by_) in boa:
            d.px(bx_, by_ - 1, 15)
            d.px(bx_ - 1, by_ + 1, 13)
            d.px(bx_ + 2, by_, 15)
        # Klackar
        d.rekt(lx + 2, 98, lx + 6, 100, 13)
        d.rekt(lx + 9, 98, lx + 13, 100, 13)
        d.radial(lx + 7, 50, 26, 0.3, mask=(d.a > 1) & (d.a < 10))

    d.vinjett(0.4)
    return d


# ======================================================================
#  URMAKARENS BUTIK
# ======================================================================
def urtavla(d, cx, cy, r, ram, tavla=15, tid=None):
    fyll(d, cx - r - 1, cy - r - 1, cx + r + 1, cy + r + 1, ram)
    fyll(d, cx - r + 1, cy - r + 1, cx + r - 1, cy + r - 1, tavla)
    if r >= 4:
        for k in range(4):
            a = k * math.pi / 2
            d.px(int(round(cx + (r - 2) * math.cos(a))), int(round(cy + (r - 2) * math.sin(a))), 0)
    rnd = random.Random(cx * 31 + cy)
    tim, minut = tid if tid else (rnd.random() * 2 * math.pi, rnd.random() * 2 * math.pi)
    d.linje(cx, cy, int(round(cx + (r * 0.45) * math.sin(tim))), int(round(cy - (r * 0.45) * math.cos(tim))), 0)
    d.linje(cx, cy, int(round(cx + (r * 0.75) * math.sin(minut))), int(round(cy - (r * 0.75) * math.cos(minut))), 0)


def urmakare(v=None):
    v = v or {}
    pendel = v.get("pendel", 0)    # pendlarnas fas 0..7
    gok = v.get("gok", 0)          # 0 stängd lucka, 1 luckan öppen, 2 göken ute
    sek = v.get("sek", 0)          # sekundvisaren 0..11
    rnd = random.Random(1880)
    sving = math.sin(pendel / 8 * 2 * math.pi)
    d = Duk(6)

    # Väggar med panel
    d.vgrad(0, 0, W, 70, [0, 6, 6, 7])
    for x in range(0, W, 3):
        if x % 9 == 0:
            d.rekt(x, 0, x + 1, 70, 6)
    d.rekt(0, 66, W, 98, 7)
    for x in range(0, W, 14):
        d.rekt(x + 2, 70, x + 12, 94, 6)
        d.rekt(x + 3, 71, x + 11, 93, 7)
    d.rekt(0, 66, W, 68, 8)
    d.rekt(0, 98, W, H, 7)
    d.vgrad(0, 98, W, H, [6, 7, 7])
    for x in range(0, W, 12):
        d.linje(x, 98, x - 12, H, 6)

    # --- Dörren ut med en liten klocka ---
    with d.yta("utgang:ut"):
        d.rekt(3, 20, 27, 98, 6)
        d.rekt(5, 22, 25, 98, 8)
        d.rekt(7, 24, 23, 60, 2)
        d.vgrad(7, 24, 23, 60, [1, 2, 3])
        for y in range(26, 60, 5):
            d.px(9 + (y * 3) % 12, y, 5)
            d.px(9 + (y * 3) % 12, y + 1, 4)
        d.rekt(7, 24, 23, 25, 9)
        d.linje(10, 25, 15, 28, 10)
        d.linje(20, 25, 15, 28, 10)
        d.rekt(8, 28, 22, 36, 15)
        txt(d, 9, 30, "OPEN", 13, spegel=True)     # skylten sedd från insidan
        d.rekt(7, 64, 23, 94, 7)
        d.rekt(9, 66, 21, 92, 8)
        d.rekt(20, 66, 23, 69, 10)
        # Klockan ovanför
        d.rekt(14, 12, 16, 15, 0)
        d.linje(14, 12, 20, 12, 0)
        d.poly([(12, 19), (13, 15), (15, 14), (17, 15), (18, 19)], 10)
        d.rekt(12, 18, 19, 19, 9)
        d.px(14, 15, 11)
        d.px(15, 20, 8)

    # --- Väggen full av klockor ---
    with d.yta("klockor"):
        for (cx, cy, r, ram) in [(70, 14, 7, 8), (88, 10, 5, 10), (104, 16, 8, 9), (74, 32, 5, 10), (92, 28, 6, 7),
                                 (140, 12, 6, 8), (146, 30, 5, 10), (186, 50, 5, 9), (186, 72, 4, 10),
                                 (58, 52, 4, 9)]:
            urtavla(d, cx, cy, r, ram)
        # Fyrkantig väggklocka
        d.rekt(130, 22, 140, 34, 8)
        d.rekt(131, 23, 139, 33, 15)
        d.linje(135, 28, 135, 24, 0)
        d.linje(135, 28, 138, 29, 0)
        # Solfjäderklocka i guld
        for k in range(16):
            a = k * math.pi / 8
            d.linje(186, 22, int(186 + 10 * math.cos(a)), int(22 + 10 * math.sin(a)), 10)
        urtavla(d, 186, 22, 4, 9)
        # Väggregulator med pendel
        d.rekt(108, 26, 120, 46, 6)
        d.rekt(109, 27, 119, 45, 8)
        urtavla(d, 114, 31, 4, 10)
        d.rekt(110, 37, 118, 44, 0)
        pxp = 114 + int(round(sving * 2))
        d.linje(114, 37, pxp, 41, 10)
        fyll(d, pxp - 1, 41, pxp + 1, 43, 10)
        # Stor klocka med röd sekundvisare
        cx, cy, r = 124, 12, 9
        urtavla(d, cx, cy, r, 9, tid=(math.radians(300), math.radians(60)))
        a = sek * math.pi / 6
        d.linje(cx, cy, int(round(cx + (r - 1) * math.sin(a))), int(round(cy - (r - 1) * math.cos(a))), 13)
        d.px(cx, cy, 13)
        # Hylla med bordsur och väckarklockor
        d.rekt(56, 46, 150, 48, 8)
        d.rekt(56, 46, 150, 47, 9)
        d.rekt(64, 38, 74, 46, 7)                     # bordsur
        d.a[d.mask_ellips(64, 34, 74, 42) & (YY < 38)] = 7
        urtavla(d, 69, 40, 3, 9)
        for (ax, c) in [(80, 13), (128, 12), (140, 4)]:
            urtavla(d, ax, 42, 3, c)
            d.px(ax - 3, 37, 10)
            d.px(ax + 3, 37, 10)
            d.px(ax - 2, 46, 0)
            d.px(ax + 2, 46, 0)
        d.rekt(118, 40, 126, 46, 10)                  # liten bjällerklocka (fickur)
        fyll(d, 119, 39, 125, 45, 15)
        d.px(122, 42, 0)
        d.px(123, 41, 0)

    # --- Gökuret ---
    with d.yta("gok"):
        gx = 43
        d.poly([(gx - 14, 22), (gx, 8), (gx + 14, 22)], 6)
        d.poly([(gx - 12, 21), (gx, 10), (gx + 12, 21)], 7)
        for k in range(-12, 13, 4):
            d.px(gx + k, 22, 12)
            d.px(gx + k + 1, 23, 12)
        d.rekt(gx - 10, 22, gx + 11, 42, 7)
        d.rekt(gx - 10, 22, gx + 11, 23, 8)
        d.rekt(gx - 11, 40, gx + 12, 43, 6)
        urtavla(d, gx, 32, 5, 9, tavla=15)
        # Luckan och göken
        if gok == 0:
            d.rekt(gx - 2, 14, gx + 3, 19, 6)
            d.rekt(gx - 1, 15, gx + 2, 19, 8)
        else:
            d.rekt(gx - 2, 14, gx + 3, 19, 0)
            d.rekt(gx - 5, 14, gx - 2, 19, 8)
            if gok == 2:
                d.rekt(gx - 1, 17, gx + 1, 19, 8)
                fyll(d, gx - 2, 11, gx + 4, 17, 9)
                d.rekt(gx - 4, 13, gx - 1, 14, 10)
                d.px(gx, 13, 0)
                d.px(gx + 2, 15, 8)
                d.px(gx + 3, 12, 8)
            else:
                d.px(gx, 17, 9)
                d.px(gx + 1, 17, 9)
        # Kedjor med kottar och en liten pendel
        for (kx, ky) in [(gx - 6, 62), (gx + 5, 56)]:
            for y in range(43, ky, 2):
                d.px(kx, y, 10)
            fyll(d, kx - 2, ky, kx + 2, ky + 8, 8)
            for y in range(ky + 1, ky + 8, 2):
                d.px(kx - 1, y, 6)
                d.px(kx + 1, y + 1, 6)
        ppx = gx + int(round(sving * 3))
        d.linje(gx, 43, ppx, 54, 9)
        fyll(d, ppx - 2, 53, ppx + 2, 57, 10)
        d.px(gx, 6, 7)

    # --- Golvuret ---
    with d.yta("golvur"):
        ox = 168
        d.rekt(ox - 10, 12, ox + 11, 36, 7)
        d.poly([(ox - 12, 12), (ox - 6, 6), (ox + 7, 6), (ox + 13, 12)], 6)
        fyll(d, ox - 3, 2, ox + 4, 9, 6)
        d.rekt(ox - 1, 1, ox + 2, 3, 10)
        d.rekt(ox - 12, 11, ox + 13, 13, 8)
        urtavla(d, ox, 23, 7, 10, tid=(math.radians(330), math.radians(240)))
        d.rekt(ox - 11, 35, ox + 12, 37, 8)
        d.rekt(ox - 8, 37, ox + 9, 92, 7)
        d.rekt(ox - 8, 37, ox - 7, 92, 8)
        d.rekt(ox - 5, 42, ox + 6, 84, 0)
        d.rekt(ox - 6, 41, ox + 7, 42, 9)
        d.rekt(ox - 6, 84, ox + 7, 85, 9)
        # Vikter
        for wx in (ox - 3, ox + 4):
            d.linje(wx, 42, wx, 52, 9)
            d.rekt(wx - 1, 52, wx + 1, 60, 10)
        # Pendeln
        bx = ox + int(round(sving * 4))
        d.linje(ox, 42, bx, 74, 9)
        fyll(d, bx - 3, 72, bx + 3, 78, 10)
        fyll(d, bx - 2, 73, bx + 1, 76, 11)
        d.linje(ox + 5, 43, ox + 2, 50, 4)             # glasets blänk
        d.rekt(ox - 11, 92, ox + 12, 100, 6)
        d.rekt(ox - 11, 92, ox + 12, 93, 8)
        d.rekt(ox - 12, 100, ox + 13, 102, 0)

    # --- Disken och urmakaren ---
    with d.yta("urmakaren"):
        ux = 100
        # Liten gammal man
        d.rekt(ux - 9, 62, ux + 10, 78, 15)            # skjorta
        d.rekt(ux - 5, 64, ux + 6, 78, 9)              # skinnförkläde
        d.rekt(ux - 5, 64, ux + 6, 65, 8)
        d.linje(ux - 5, 64, ux - 3, 60, 8)
        d.linje(ux + 5, 64, ux + 3, 60, 8)
        d.rekt(ux - 2, 68, ux + 3, 71, 8)              # ficka
        d.px(ux + 1, 68, 10)
        fyll(d, ux - 7, 44, ux + 8, 61, 10)            # huvud
        d.rekt(ux - 6, 44, ux + 7, 46, 10)
        d.px(ux - 1, 45, 11)                            # flintskallen blänker
        d.px(ux, 45, 11)
        d.rekt(ux - 8, 49, ux - 5, 55, 15)              # vita tofsar
        d.rekt(ux + 6, 49, ux + 9, 55, 15)
        d.px(ux - 9, 50, 15)
        d.px(ux + 9, 50, 15)
        d.px(ux - 6, 54, 9)
        d.px(ux + 7, 54, 9)
        d.rekt(ux - 4, 48, ux - 1, 50, 15)              # buskiga ögonbryn
        d.rekt(ux + 2, 48, ux + 6, 49, 15)
        d.px(ux - 3, 51, 0)                             # öga
        # Lupp i ögat
        d.rekt(ux + 1, 50, ux + 6, 54, 0)
        d.rekt(ux + 2, 51, ux + 5, 53, 2)
        d.px(ux + 2, 51, 5)
        d.rekt(ux + 2, 54, ux + 6, 56, 0)
        d.rekt(ux - 1, 53, ux + 1, 56, 9)              # näsa
        # Stora vita valrossmustascher
        d.rekt(ux - 6, 56, ux + 7, 59, 15)
        d.px(ux - 7, 58, 15)
        d.px(ux + 7, 58, 15)
        d.px(ux - 7, 59, 15)
        d.px(ux + 7, 59, 15)
        d.px(ux - 8, 60, 15)
        d.px(ux + 8, 60, 15)
        d.rekt(ux - 4, 58, ux + 5, 59, 9)
        d.px(ux, 56, 9)
        # Armar på disken
        d.rekt(ux - 13, 70, ux - 6, 74, 15)
        d.rekt(ux + 7, 70, ux + 14, 74, 15)
        d.rekt(ux - 15, 72, ux - 11, 75, 10)
        d.rekt(ux + 12, 72, ux + 16, 75, 10)
        # Disken
        d.rekt(54, 74, 152, 78, 8)
        d.rekt(54, 74, 152, 75, 9)
        d.rekt(56, 78, 150, 112, 7)
        d.rekt(60, 82, 146, 100, 1)
        d.vgrad(60, 82, 146, 100, [2, 1])
        for (wx_, wy_) in [(68, 90), (80, 92), (94, 89), (108, 92), (122, 90), (136, 92)]:
            fyll(d, wx_ - 3, wy_ - 3, wx_ + 3, wy_ + 3, 10)
            fyll(d, wx_ - 2, wy_ - 2, wx_ + 2, wy_ + 2, 15)
            d.px(wx_, wy_ - 4, 10)
            d.linje(wx_ - 2, wy_ + 4, wx_ + 8, wy_ + 7, 9)
        d.linje(60, 82, 74, 100, 3)
        d.rekt(56, 100, 150, 102, 8)
        for x in range(60, 150, 18):
            d.rekt(x, 104, x + 14, 110, 6)
        # Verktyg och urdelar på disken
        fyll(d, ux + 13, 69, ux + 19, 74, 10)          # öppet fickur i handen
        fyll(d, ux + 14, 70, ux + 18, 73, 15)
        d.px(ux + 16, 71, 0)
        d.linje(ux - 22, 73, ux - 16, 72, 4)            # pincett
        for (dx_, dy_) in [(66, 73), (70, 72), (73, 73), (128, 73)]:
            d.px(dx_, dy_, 10)
    # Lampan med grön skärm
    with d.yta("urmakaren"):
        d.rekt(132, 70, 140, 74, 10)
        d.rekt(135, 62, 137, 70, 10)
        d.poly([(128, 62), (131, 57), (141, 57), (144, 62)], 12)
        d.rekt(128, 62, 144, 63, 10)
    gubbe = (XX >= 84) & (XX < 118) & (YY >= 42) & (YY < 76)
    d.radial(136, 74, 34, 0.6, mask=(YY < 112) & (YY > 40) & ~gubbe & (d.a != 15))
    d.radial(100, 52, 30, 0.3, mask=(YY < 74) & ~gubbe & (d.a < 9))

    # Damm i luften
    for i in range(26):
        x, y = rnd.randint(30, 160), rnd.randint(6, 66)
        if rnd.random() < 0.6:
            d.px(x, y, 15 if (x + y) % 3 else 10)
    d.ljus(~gubbe, 0.12, MORKARE)
    d.vinjett(0.45)
    return d


SCENER_B = {
    "blvd_o": (blvd_o, [
        ("regn", "regn", [(i, 90) for i in range(10)]),
        ("neon", "neon", [(2, 2400), (1, 900), (2, 1600), (0, 90), (2, 70), (0, 160), (2, 1800), (1, 700)]),
    ]),
    "klubb": (klubb, [
        ("lagor", "lagor", [(i, 160) for i in range(4)]),
        ("hander", "hander", [(i, 200) for i in range(4)]),
        ("torka", "torka", [(i, 350) for i in range(4)]),
    ]),
    "logen": (logen, [
        ("huvud", "huvud", [(0, 1600), (1, 500), (0, 800), (2, 1200), (1, 400)]),
        ("lampor", "lampor", [(i, 400) for i in range(4)]),
        ("tackt", "tackt", [(False, 1000), (True, 1000)], 1),
    ]),
    "urmakare": (urmakare, [
        ("pendel", "pendel", [(i, 160) for i in range(8)]),
        ("gok", "gok", [(0, 5000), (1, 150), (2, 1200), (1, 150)]),
        ("sek", "sek", [(i, 1000) for i in range(12)]),
    ]),
}
