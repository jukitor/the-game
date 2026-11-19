#!/usr/bin/env python3
"""Ritar spelets bilder i retrostil: låg upplösning, 16 färger och ordnad dithering.

Kör:  python3 verktyg/rita_bilder.py
Bilderna hamnar i mappen bilder/ som PNG med palett.
"""
import random
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

W, H = 192, 120
UT = Path(__file__).resolve().parent.parent / "bilder"

# 16 färger, samma i alla bilder.
PALETT = [
    (11, 13, 26),     # 0  nästan svart
    (26, 31, 58),     # 1  mörk marinblå
    (42, 47, 85),     # 2  marinblå
    (63, 74, 122),    # 3  skifferblå
    (106, 120, 168),  # 4  ljus skiffer
    (169, 184, 216),  # 5  blekblå (regn)
    (58, 36, 24),     # 6  mörkbrun
    (94, 58, 34),     # 7  brun
    (138, 90, 50),    # 8  ljust trä
    (192, 138, 74),   # 9  läderbrun/trenchcoat
    (232, 192, 112),  # 10 lampgult
    (255, 240, 176),  # 11 starkt ljus
    (31, 90, 58),     # 12 lampskärmsgrönt
    (192, 48, 42),    # 13 rött
    (255, 106, 138),  # 14 neonrosa
    (216, 200, 160),  # 15 papper
]

LJUSARE = {0: 1, 1: 2, 2: 3, 3: 4, 4: 5, 5: 5, 6: 7, 7: 8, 8: 9, 9: 10, 10: 11, 11: 11, 12: 12, 13: 14, 14: 14, 15: 11}
MORKARE = {0: 0, 1: 0, 2: 1, 3: 2, 4: 3, 5: 4, 6: 0, 7: 6, 8: 7, 9: 8, 10: 9, 11: 10, 12: 6, 13: 6, 14: 13, 15: 9}

BAYER = np.array([[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]) / 16.0
YY, XX = np.mgrid[0:H, 0:W]
TROSKEL = BAYER[YY % 4, XX % 4]


class Duk:
    def __init__(self, bas=0):
        self.a = np.full((H, W), bas, dtype=np.uint8)

    # --- grundformer ---
    def rekt(self, x0, y0, x1, y1, c):
        self.a[max(0, y0):max(0, y1), max(0, x0):max(0, x1)] = c

    def mask_poly(self, punkter):
        m = Image.new("L", (W, H), 0)
        ImageDraw.Draw(m).polygon(punkter, fill=1)
        return np.array(m, dtype=bool)

    def mask_ellips(self, x0, y0, x1, y1):
        m = Image.new("L", (W, H), 0)
        ImageDraw.Draw(m).ellipse([x0, y0, x1, y1], fill=1)
        return np.array(m, dtype=bool)

    def poly(self, punkter, c):
        self.a[self.mask_poly(punkter)] = c

    def linje(self, x0, y0, x1, y1, c):
        m = Image.new("L", (W, H), 0)
        ImageDraw.Draw(m).line([x0, y0, x1, y1], fill=1)
        self.a[np.array(m, dtype=bool)] = c

    def px(self, x, y, c):
        if 0 <= x < W and 0 <= y < H:
            self.a[y, x] = c

    # --- dithering ---
    def vgrad(self, x0, y0, x1, y1, ramp):
        """Vertikal övergång genom en lista färger, rastrerad."""
        for y in range(y0, y1):
            t = (y - y0) / max(1, (y1 - y0 - 1)) * (len(ramp) - 1)
            i = min(int(t), len(ramp) - 2)
            f = t - i
            rad = np.where(TROSKEL[y, x0:x1] < f, ramp[i + 1], ramp[i])
            self.a[y, x0:x1] = rad

    def ljus(self, mask, styrka, tabell=LJUSARE):
        """Ljusa upp (eller mörka ner) pixlar i masken. styrka 0..1 kan vara en matris."""
        trä = mask & (TROSKEL < styrka)
        lut = np.array([tabell[i] for i in range(16)], dtype=np.uint8)
        self.a[trä] = lut[self.a[trä]]

    def radial(self, cx, cy, r, max_styrka=1.0, tabell=LJUSARE, mask=None):
        d = np.sqrt((XX - cx) ** 2 + ((YY - cy) * 1.2) ** 2)
        s = np.clip(1 - d / r, 0, 1) * max_styrka
        m = d < r if mask is None else (mask & (d < r))
        self.ljus(m, s, tabell)

    def vinjett(self, styrka=0.55):
        dx = np.abs(XX - W / 2) / (W / 2)
        dy = np.abs(YY - H / 2) / (H / 2)
        d = np.clip(np.maximum(dx, dy) - 0.72, 0, 1) / 0.28 * styrka
        self.ljus(np.ones((H, W), bool), d, MORKARE)

    def spara(self, namn):
        img = Image.fromarray(self.a, mode="P")
        flat = [v for f in PALETT for v in f]
        img.putpalette(flat)
        UT.mkdir(exist_ok=True)
        img.save(UT / f"{namn}.png", optimize=True)
        return UT / f"{namn}.png"


# ======================================================================
#  DETEKTIVENS KONTOR
# ======================================================================
def kontor(v=None):
    """v anger animationernas läge. Utan v ritas grundbilden."""
    v = v or {}
    neon = v.get("neon", (1, 1, 1, 1, 1))   # vilka bokstäver i HOTEL som lyser
    regn = v.get("regn", 0)                 # regnets fas 0..9
    rok = v.get("rok", 0)                   # rökens fas 0..5
    lampa = v.get("lampa", True)            # telefonsvararens lampa
    rnd = random.Random(1947)
    d = Duk(2)

    # Vägg: mörkare upptill, list i taket
    d.vgrad(0, 0, W, 72, [1, 2, 2])
    d.rekt(0, 0, W, 4, 0)
    d.rekt(0, 4, W, 5, 1)
    # Bröstpanel i trä
    d.rekt(0, 72, W, 88, 6)
    d.rekt(0, 72, W, 73, 7)
    for x in range(6, W, 22):
        d.rekt(x, 75, x + 18, 76, 7)
        d.rekt(x, 75, x + 1, 86, 7)
        d.rekt(x, 86, x + 18, 87, 0)
    # Golv: plankor
    d.rekt(0, 88, W, H, 6)
    for i, y in enumerate(range(90, H, 5)):
        d.rekt(0, y, W, y + 1, 0)
        off = (i * 37) % 41
        for x in range(off, W, 41):
            d.rekt(x, y + 1, x + 1, y + 5, 0)
    d.vgrad(0, 88, W, 96, [0, 6])

    # --- Fönstret ---
    fx0, fy0, fx1, fy1 = 24, 9, 88, 63
    # Natthimmel med neonsken längst ner
    d.vgrad(fx0, fy0, fx1, fy1, [0, 1, 2, 3])
    d.radial(70, 66, 30, 0.6)
    # Skyline
    x = fx0
    hus = []
    while x < fx1:
        b = rnd.randint(6, 13)
        topp = rnd.randint(24, 48)
        hus.append((x, topp, b))
        d.rekt(x, topp, x + b, fy1, rnd.choice([0, 1]))
        x += b
    for (hx, topp, b) in hus:
        for wy in range(topp + 2, fy1 - 1, 3):
            for wx in range(hx + 1, hx + b - 1, 2):
                if rnd.random() < 0.28:
                    d.px(wx, wy, rnd.choice([10, 10, 9, 15]))
    # Vattentorn på ett tak
    d.rekt(40, 20, 46, 26, 0)
    d.rekt(41, 18, 45, 20, 0)
    d.linje(41, 26, 40, 30, 0)
    d.linje(45, 26, 46, 30, 0)
    # Regn på rutan
    for _ in range(70):
        rx, ry = rnd.randint(fx0, fx1 - 1), rnd.randint(fy0, fy1 - 4)
        ry = fy0 + (ry - fy0 + regn * 5) % (fy1 - 4 - fy0)
        n = rnd.randint(2, 4)
        for k in range(n):
            d.px(rx - k // 2, ry + k, 4 if k < n - 1 else 5)
    # Lodrät neonskylt: HOTEL
    nx = 74
    d.rekt(nx - 1, 39, nx + 4, 61, 0)
    bokstaver = {
        "H": ["101", "111", "101"], "O": ["111", "101", "111"], "T": ["111", "010", "010"],
        "E": ["111", "110", "111"], "L": ["100", "100", "111"],
    }
    for i, ch in enumerate("HOTEL"):
        for ry, rad in enumerate(bokstaver[ch]):
            for rx, bit in enumerate(rad):
                if bit == "1":
                    d.px(nx + rx, 41 + i * 4 + ry, 14 if neon[i] else 2)
    if sum(neon):
        d.radial(nx + 1, 50, 12, 0.5 * sum(neon) / 5, mask=d.a < 4)
    # Persienner upptill
    for y in range(fy0, fy0 + 13, 2):
        d.rekt(fx0, y, fx1, y + 1, 8)
        d.rekt(fx0, y + 1, fx1, y + 2, 7)
    d.rekt(fx0, fy0 + 13, fx1, fy0 + 14, 6)
    d.linje(60, fy0 + 14, 60, fy0 + 24, 9)
    d.px(60, fy0 + 25, 10)
    # Spröjsar och karm
    d.rekt(55, fy0, 57, fy1, 6)
    d.rekt(fx0, 36, fx1, 38, 6)
    d.rekt(fx0 - 3, fy0 - 3, fx1 + 3, fy0, 7)
    d.rekt(fx0 - 3, fy0, fx0, fy1, 7)
    d.rekt(fx1, fy0, fx1 + 3, fy1, 6)
    d.rekt(fx0 - 5, fy1, fx1 + 5, fy1 + 3, 8)
    d.rekt(fx0 - 5, fy1 + 3, fx1 + 5, fy1 + 4, 6)

    # Fönsterljus som faller in på golvet (fyra rutor, snett)
    for (ax0, ax1) in [(fx0, 55), (57, fx1)]:
        poly = [(ax0 - 18, 92), (ax1 - 18, 92), (ax1 - 34, H), (ax0 - 34, H)]
        d.ljus(d.mask_poly(poly), 0.85)

    # --- Dörren till vänster ---
    d.rekt(0, 12, 17, 88, 7)
    d.rekt(17, 12, 19, 88, 6)
    d.rekt(3, 18, 15, 50, 4)
    d.vgrad(3, 18, 15, 50, [5, 4, 3])
    # Spegelvänd text på frostat glas (oläsbara streck)
    for y, bredd in [(26, 10), (29, 8)]:
        for xx in range(4, 4 + bredd):
            if (xx + y) % 3:
                d.px(xx, y, 1)
    d.rekt(3, 54, 15, 84, 6)
    d.rekt(4, 55, 14, 83, 7)
    d.px(15, 60, 10)
    d.px(15, 61, 9)

    # --- Diplom och kalender på väggen ---
    d.rekt(98, 16, 114, 30, 8)
    d.rekt(99, 17, 113, 29, 15)
    for y in (19, 21, 23):
        d.rekt(101, y, 111, y + 1, 9)
    d.px(110, 26, 13)
    d.px(111, 26, 13)
    d.rekt(120, 18, 131, 33, 15)
    d.rekt(120, 18, 131, 22, 13)
    for y in range(24, 32, 2):
        for xx in range(121, 131, 2):
            d.px(xx, y, 4)
    d.px(127, 28, 13)

    # --- Stolen bakom skrivbordet ---
    d.poly([(116, 66), (116, 50), (119, 46), (133, 46), (136, 50), (136, 66)], 6)
    d.rekt(118, 49, 134, 51, 7)
    for y in range(52, 64, 3):
        d.rekt(118, y, 134, y + 1, 7)

    # --- Skrivbordet ---
    d.rekt(90, 66, 172, 70, 8)
    d.rekt(90, 66, 172, 67, 9)
    d.rekt(92, 70, 170, 97, 7)
    d.rekt(92, 70, 170, 72, 6)
    d.rekt(92, 95, 170, 97, 6)
    d.rekt(140, 75, 167, 84, 6)
    d.rekt(141, 76, 166, 83, 7)
    d.rekt(151, 79, 157, 80, 10)
    d.rekt(140, 86, 167, 94, 6)
    d.rekt(141, 87, 166, 93, 7)
    d.rekt(151, 89, 157, 90, 9)
    d.rekt(97, 75, 135, 92, 6)
    d.rekt(98, 76, 134, 91, 7)
    d.rekt(98, 76, 134, 77, 8)
    # Skugga under skrivbordet
    d.ljus(d.mask_poly([(86, 97), (174, 97), (178, 104), (82, 104)]), 0.7, MORKARE)

    # --- Bankirlampa med grön skärm ---
    d.radial(105, 56, 30, 0.6, mask=YY < 66)
    d.radial(104, 67, 18, 0.9, mask=(YY >= 66) & (YY < 70))
    d.rekt(99, 63, 111, 66, 9)
    d.rekt(99, 63, 111, 64, 10)
    d.rekt(104, 57, 106, 63, 9)
    d.poly([(96, 58), (114, 58), (111, 52), (99, 52)], 12)
    d.rekt(100, 52, 110, 53, 4)
    d.rekt(97, 58, 113, 59, 10)
    d.rekt(98, 59, 112, 60, 11)
    # Papper i ljuskäglan
    d.poly([(114, 67), (128, 66), (130, 69), (115, 70)], 15)
    d.linje(117, 68, 126, 67, 4)

    # --- Askkopp och rök ---
    d.rekt(131, 66, 137, 68, 4)
    d.px(136, 65, 15)
    d.px(137, 65, 13)
    sx = 137
    for y in range(64, 40, -1):
        sx += [0, 1, 1, 0, -1, -1][((y + 2 * rok) // 2) % 6]
        if (y + 2 * rok) % 3:
            d.px(sx, y, 4 if y > 52 else 3)

    # --- Telefonsvarare med röd lampa ---
    d.rekt(140, 61, 156, 66, 0)
    d.rekt(141, 62, 149, 65, 1)
    d.rekt(142, 63, 148, 64, 3)
    if lampa:
        d.px(153, 63, 13)
        d.px(154, 63, 14)
        d.radial(154, 63, 4, 0.6, mask=d.a < 4)
    else:
        d.px(153, 63, 6)
        d.px(154, 63, 6)

    # --- Telefon ---
    d.poly([(157, 66), (159, 61), (167, 61), (169, 66)], 0)
    d.rekt(156, 57, 170, 59, 0)
    d.rekt(155, 56, 158, 59, 0)
    d.rekt(168, 56, 171, 59, 0)
    d.px(163, 63, 3)

    # --- Whiskyflaska (tom) ---
    d.rekt(92, 58, 96, 66, 8)
    d.rekt(93, 55, 95, 58, 8)
    d.rekt(93, 54, 95, 55, 0)
    d.rekt(93, 59, 95, 64, 9)
    d.px(93, 59, 10)

    # --- Klädhängare med hatt och trenchcoat ---
    d.rekt(179, 18, 181, 99, 6)
    d.linje(180, 99, 174, 103, 6)
    d.linje(180, 99, 186, 103, 6)
    d.linje(180, 24, 175, 21, 7)
    d.linje(180, 24, 185, 21, 7)
    # Fedora
    d.rekt(172, 18, 189, 20, 7)
    d.poly([(174, 18), (176, 11), (185, 11), (187, 18)], 7)
    d.rekt(175, 15, 187, 17, 0)
    d.rekt(177, 11, 184, 12, 8)
    # Trenchcoat
    d.poly([(173, 26), (187, 26), (190, 72), (170, 72)], 9)
    d.poly([(176, 26), (180, 36), (184, 26)], 8)
    d.rekt(171, 46, 190, 48, 8)
    d.px(180, 47, 10)
    for xx in (175, 179, 184):
        d.linje(xx, 50, xx + (xx - 180) // 3, 71, 8)
    d.rekt(170, 72, 190, 73, 7)

    # --- Stämning ---
    d.vinjett(0.4)
    return d


# Animationer per bild: (namn, nyckel i v, [(värde, millisekunder), ...]).
# Spelet kan låsa en animation på en viss ruta, t.ex. släckt lampa.
HOTEL_UPP = [(tuple(1 if j < n else 0 for j in range(5)), 260) for n in range(6)]
SCENER = {
    "kontor": (kontor, [
        ("neon", "neon", [((0, 0, 0, 0, 0), 700)] + HOTEL_UPP[1:-1] + [((1, 1, 1, 1, 1), 3000),
                          ((0, 0, 0, 0, 0), 120), ((1, 1, 1, 1, 1), 160), ((0, 0, 0, 0, 0), 90), ((1, 1, 1, 1, 1), 2200)]),
        ("regn", "regn", [(i, 90) for i in range(10)]),
        ("rok", "rok", [(i, 220) for i in range(6)]),
        ("lampa", "lampa", [(True, 650), (False, 650)]),
    ]),
}


def exportera(namn):
    """Sparar grundbilden som PNG och returnerar animationerna som pixeldiffar."""
    scen, animationer = SCENER[namn]
    bas = scen()
    bas.spara(namn)
    ut = []
    for anim_namn, nyckel, ramar in animationer:
        diffar, tider = [], []
        for varde, ms in ramar:
            a = scen({nyckel: varde}).a
            ys, xs = np.nonzero(a != bas.a)
            platt = []
            for y, x in zip(ys.tolist(), xs.tolist()):
                platt += [x, y, int(a[y, x])]
            diffar.append(platt)
            tider.append(ms)
        ut.append({"namn": anim_namn, "ms": tider, "ramar": diffar})
    return ut


def skriv_in_i_spelet(data):
    """Lägger in animationsdatan i spel.html mellan markörerna."""
    import json
    spel = UT.parent / "spel.html"
    s = spel.read_text(encoding="utf-8")
    start, slut = "/* BILDDATA-START */", "/* BILDDATA-SLUT */"
    i, j = s.index(start) + len(start), s.index(slut)
    kod = "\nconst BILDDATA = " + json.dumps(data, separators=(",", ":")) + ";\n"
    spel.write_text(s[:i] + kod + s[j:], encoding="utf-8")


if __name__ == "__main__":
    data = {"palett": PALETT, "bilder": {}}
    for namn in SCENER:
        data["bilder"][namn] = exportera(namn)
        print("Ritade", UT / f"{namn}.png", "med", len(data["bilder"][namn]), "animationer")
    skriv_in_i_spelet(data)
    print("Uppdaterade spel.html. Kör verktyg/bygg.py för att bygga index.html.")
