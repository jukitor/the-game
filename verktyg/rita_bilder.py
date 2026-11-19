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


# ======================================================================
#  LITET PIXELTYPSNITT (3 x 5)
# ======================================================================
TYPSNITT = {
    "A": ["010", "101", "111", "101", "101"], "B": ["110", "101", "110", "101", "110"],
    "D": ["110", "101", "101", "101", "110"], "E": ["111", "100", "110", "100", "111"],
    "G": ["011", "100", "101", "101", "011"], "H": ["101", "101", "111", "101", "101"],
    "I": ["111", "010", "010", "010", "111"], "N": ["1001", "1101", "1011", "1001", "1001"],
    "O": ["010", "101", "101", "101", "010"], "P": ["110", "101", "110", "100", "100"], "R": ["110", "101", "110", "101", "101"],
    "S": ["011", "100", "010", "001", "110"], "T": ["111", "010", "010", "010", "010"],
    "U": ["101", "101", "101", "101", "111"], "W": ["10001", "10001", "10101", "10101", "01010"],
    "Y": ["101", "101", "010", "010", "010"], "1": ["010", "110", "010", "010", "111"],
    " ": ["000"] * 5,
}


def text(d, x, y, s, c, farger=None):
    """Skriver text med pixeltypsnittet. farger kan ge varje tecken en egen färg."""
    for i, ch in enumerate(s):
        for ry, rad in enumerate(TYPSNITT[ch]):
            for rx, bit in enumerate(rad):
                if bit == "1":
                    d.px(x + rx, y + ry, farger[i] if farger else c)
        x += len(TYPSNITT[ch][0]) + 1


def regn_over(d, rnd, antal, fas, x0=0, y0=0, x1=W, y1=H, steg=6, faser=10):
    """Regnstrimmor som faller. fas 0..faser-1 ger en sömlös loop."""
    hojd = y1 - y0
    for _ in range(antal):
        rx, ry = rnd.randint(x0, x1 - 1), rnd.randint(y0, y1 - 1)
        ry = y0 + (ry - y0 + fas * hojd // faser) % hojd
        n = rnd.randint(2, 4)
        for k in range(n):
            if ry + k < y1:
                d.px(rx - k // 2, ry + k, 4 if k < n - 1 else 5)


# ======================================================================
#  MAIN STREET
# ======================================================================
def main_street(v=None):
    v = v or {}
    regn = v.get("regn", 0)                 # regnets fas 0..9
    anga = v.get("anga", 0)                 # ångans fas 0..5
    neon = v.get("neon", (1, 1, 1, 1, 1))   # vilka bokstäver i DINER som lyser
    rnd = random.Random(1948)
    d = Duk(1)

    # --- Himmel och avlägsen skyline ---
    d.vgrad(0, 0, W, 50, [0, 0, 1, 2])
    x = 50
    while x < 150:
        b = rnd.randint(6, 12)
        topp = rnd.randint(8, 26)
        d.rekt(x, topp, x + b, 60, 1)
        for wy in range(topp + 2, 58, 3):
            for wx in range(x + 1, x + b - 1, 2):
                if rnd.random() < 0.15:
                    d.px(wx, wy, 9)
        x += b

    # --- Hendersonhuset till vänster (tegel) ---
    d.rekt(0, 2, 60, 86, 7)
    d.ljus(d.mask_poly([(0, 2), (60, 2), (60, 86), (0, 86)]), 0.45, MORKARE)
    for y in range(4, 84, 3):
        off = 0 if (y // 3) % 2 else 3
        for xx in range(off, 60, 6):
            d.px(xx, y, 6)
    d.rekt(0, 2, 60, 4, 6)
    d.rekt(58, 2, 60, 86, 6)
    fonster_x = [5, 19, 33, 47]
    for rad, fy in enumerate([8, 22, 36, 50]):
        for kol, fx in enumerate(fonster_x):
            d.rekt(fx - 1, fy - 1, fx + 8, fy + 10, 6)
            if rad == 0 and kol == 1:
                # Ditt kontor på femte våningen: lampan lyser
                d.rekt(fx, fy, fx + 7, fy + 9, 10)
                for yy in range(fy, fy + 4, 2):
                    d.rekt(fx, yy, fx + 7, yy + 1, 9)
                d.rekt(fx + 2, fy + 6, fx + 5, fy + 7, 12)
                d.px(fx + 3, fy + 7, 11)
            elif rnd.random() < 0.3:
                d.rekt(fx, fy, fx + 7, fy + 9, 9)
                d.rekt(fx, fy + 6, fx + 7, fy + 9, 8)
            else:
                d.rekt(fx, fy, fx + 7, fy + 9, 1)
                d.px(fx + 1, fy + 1, 3)
            d.rekt(fx - 1, fy + 9, fx + 8, fy + 10, 4)
    # Entré med upplyst glasdörr
    d.rekt(18, 64, 40, 86, 6)
    d.rekt(21, 67, 37, 86, 9)
    d.rekt(22, 68, 36, 86, 10)
    d.rekt(29, 68, 30, 86, 8)
    d.rekt(16, 62, 42, 64, 4)

    # --- Dinern i mitten ---
    d.rekt(96, 18, 142, 86, 2)
    for fy in (22, 34):
        for fx in range(100, 140, 10):
            d.rekt(fx, fy, fx + 6, fy + 7, 1 if rnd.random() < 0.6 else 9)
    # Neonskylt DINER med glappande N
    d.rekt(104, 43, 130, 51, 0)
    farger = [14 if neon[i] else 2 for i in range(5)]
    text(d, 107, 45, "DINER", 14, farger)
    if sum(neon):
        d.radial(117, 47, 18, 0.45 * sum(neon) / 5, mask=(d.a < 4))
    # Markis med ränder
    for i, xx in enumerate(range(98, 142, 4)):
        d.poly([(xx, 54), (xx + 4, 54), (xx + 5, 61), (xx + 1, 61)], 13 if i % 2 == 0 else 15)
    d.rekt(98, 61, 143, 62, 6)
    # Upplyst fönster med gäster
    d.rekt(98, 62, 142, 84, 10)
    d.rekt(98, 62, 142, 63, 11)
    for gx in (104, 114, 128):
        d.rekt(gx, 70, gx + 5, 84, 7)
        d.rekt(gx + 1, 66, gx + 4, 70, 7)
    d.rekt(98, 76, 142, 78, 8)
    d.rekt(98, 84, 142, 86, 6)

    # --- Huset till höger ---
    d.rekt(142, 6, W, 86, 3)
    d.ljus(d.mask_poly([(142, 6), (W, 6), (W, 86), (142, 86)]), 0.5, MORKARE)
    for fy in range(10, 52, 12):
        for fx in range(148, 190, 11):
            d.rekt(fx, fy, fx + 6, fy + 8, 1 if rnd.random() < 0.7 else 10)

    # --- Trottoar och gata ---
    d.rekt(0, 86, W, 96, 3)
    d.vgrad(0, 86, W, 96, [2, 3])
    d.rekt(0, 96, W, 98, 4)
    d.rekt(0, 98, W, H, 1)
    d.vgrad(0, 98, W, H, [0, 1, 1])
    for xx in range(0, W, 16):
        d.rekt(xx, 108, xx + 8, 109, 2)
    # Spegelbilder i den blöta gatan
    for (x0, x1, f) in [(100, 142, 0.6), (104, 130, 0.35), (21, 37, 0.5), (126, 136, 0.7)]:
        for y in range(98, H):
            s = f * (1 - (y - 98) / (H - 98))
            m = (XX >= x0) & (XX < x1) & (YY == y) & ((XX + y) % 2 == 0)
            d.ljus(m, s * 2)
    for y in range(99, H, 2):
        for xx in range(106, 128, 3):
            if neon[2] and (xx + y) % 4 == 0:
                d.px(xx, y, 13 if y > 108 else 14)

    # --- Gatlykta ---
    d.rekt(131, 36, 133, 96, 0)
    d.rekt(127, 34, 137, 36, 0)
    d.rekt(128, 36, 136, 38, 11)
    d.radial(132, 92, 26, 0.7, mask=(YY > 86) & (YY < 96))
    d.radial(132, 40, 7, 0.6, mask=d.a < 4)

    # --- Tunnelbaneingången ---
    d.rekt(150, 78, 186, 96, 0)
    for y in range(80, 96, 3):
        d.rekt(152, y, 184, y + 1, 1)
    for px_ in (148, 186):
        d.rekt(px_, 56, px_ + 2, 96, 12)
        d.rekt(px_ - 1, 51, px_ + 3, 56, 10)
        d.rekt(px_, 50, px_ + 2, 51, 11)
        d.radial(px_ + 1, 53, 9, 0.6, mask=d.a < 5)
    d.rekt(148, 74, 188, 76, 12)
    for xx in range(150, 186, 4):
        d.rekt(xx, 76, xx + 1, 78, 12)
    d.rekt(150, 60, 186, 68, 3)
    d.rekt(150, 60, 186, 61, 5)
    d.rekt(150, 67, 186, 68, 2)
    text(d, 155, 62, "SUBWAY", 15)

    # --- Korvkiosken ---
    d.rekt(89, 52, 90, 72, 0)
    for i, xx in enumerate(range(70, 108, 4)):
        d.poly([(xx, 52 - (2 if 78 < xx < 100 else 0)), (xx + 4, 52 - (2 if 78 < xx < 100 else 0)), (xx + 4, 57), (xx, 57)], 13 if i % 2 == 0 else 15)
    d.rekt(70, 57, 108, 58, 6)
    # Sal
    d.rekt(80, 62, 87, 64, 15)
    d.rekt(81, 60, 86, 62, 15)
    d.rekt(81, 64, 86, 68, 9)
    d.rekt(81, 67, 86, 68, 0)
    d.px(82, 65, 0)
    d.px(85, 65, 0)
    d.rekt(79, 68, 88, 74, 15)
    # Vagnen
    d.rekt(64, 72, 100, 90, 15)
    d.rekt(64, 72, 100, 73, 11)
    d.rekt(64, 75, 100, 77, 13)
    text(d, 66, 80, "HOT DOGS", 13)
    d.rekt(64, 88, 100, 90, 9)
    for hx in (70, 93):
        d.poly([(hx - 3, 92), (hx, 89), (hx + 3, 92), (hx, 95)], 0)
        d.px(hx, 92, 4)
    # Kastrullen
    d.rekt(67, 68, 76, 72, 4)
    d.rekt(66, 68, 77, 69, 5)
    # Ånga som stiger
    for spar in range(3):
        sx = 69 + spar * 3
        for y in range(67, 46, -1):
            steg = ((y + 2 * anga + spar * 4) // 3) % 6
            sx += [0, 1, 0, 0, -1, 0][steg]
            if (y + 2 * anga + spar) % 3 == 0:
                continue
            d.px(sx, y, 15 if y > 60 else 5)

    # --- Tidningsstället ---
    d.rekt(103, 76, 113, 94, 12)
    d.rekt(104, 78, 112, 85, 15)
    for y in (80, 82):
        d.rekt(105, y, 111, y + 1, 4)
    d.rekt(103, 76, 113, 77, 4)

    # --- Bilen på gatan ---
    d.poly([(4, 108), (8, 102), (20, 101), (26, 95), (42, 95), (48, 101), (58, 103), (60, 108), (60, 113), (4, 113)], 0)
    d.poly([(27, 97), (34, 97), (34, 101), (23, 101)], 2)
    d.poly([(36, 97), (42, 97), (46, 101), (36, 101)], 2)
    d.linje(8, 102, 20, 101, 3)
    d.linje(26, 95, 42, 95, 3)
    d.linje(48, 101, 58, 103, 3)
    d.rekt(8, 104, 58, 105, 3)
    d.rekt(6, 113, 60, 114, 2)
    d.rekt(56, 106, 60, 109, 11)
    d.rekt(4, 106, 6, 108, 13)
    for hx in (16, 48):
        d.mask_ellips(hx - 4, 109, hx + 4, 117)
        d.a[d.mask_ellips(hx - 4, 109, hx + 4, 117)] = 0
        d.px(hx, 113, 3)
    d.ljus(d.mask_poly([(60, 105), (100, 100), (110, 118), (60, 112)]), 0.45)

    # --- Regn och stämning ---
    regn_over(d, random.Random(7), 95, regn)
    d.vinjett(0.4)
    return d


# ======================================================================
#  PARK AVENUE
# ======================================================================
def park_avenue(v=None):
    import math
    v = v or {}
    regn = v.get("regn", 0)        # duggregnets fas 0..9
    dorr = v.get("dorr", 0)        # karuselldörrens vinkel 0..5
    duva = v.get("duva", 0)        # duvans huvud: 0 uppe, 1 halvvägs, 2 pickar
    fonster = v.get("fonster", 1)  # ett fönster högt upp: 1 tänt, 0 släckt
    rnd = random.Random(1949)
    d = Duk(1)

    # --- Himmel ---
    d.vgrad(0, 0, W, 40, [0, 1, 1, 2])

    # --- Grannhusen i mörk sten ---
    for (x0, x1) in [(0, 48), (144, W)]:
        d.rekt(x0, 4, x1, 96, 2)
        for fy in range(8, 64, 11):
            for fx in range(x0 + 4, x1 - 6, 9):
                d.rekt(fx, fy, fx + 5, fy + 7, 10 if rnd.random() < 0.3 else 1)
                d.rekt(fx, fy + 7, fx + 5, fy + 8, 3)
        d.ljus(d.mask_poly([(x0, 4), (x1, 4), (x1, 96), (x0, 96)]), 0.35, MORKARE)

    # --- Pettigrew Towers: vit marmor och mässing ---
    tx0, tx1 = 48, 144
    d.rekt(tx0, 0, tx1, 96, 15)
    d.vgrad(tx0, 0, tx1, 60, [4, 5, 15])
    for px_ in range(tx0, tx1, 16):
        d.rekt(px_, 0, px_ + 2, 96, 5)
        d.rekt(px_ + 2, 0, px_ + 3, 96, 4)
    d.rekt(tx0, 0, tx0 + 2, 96, 4)
    d.rekt(tx1 - 2, 0, tx1, 96, 4)
    # Fönster med mässingsramar
    for rad, fy in enumerate([4, 18, 32]):
        for kol, fx in enumerate(range(tx0 + 6, tx1 - 8, 16)):
            d.rekt(fx - 1, fy - 1, fx + 9, fy + 11, 9)
            tant = rnd.random() < 0.45
            if rad == 0 and kol == 3:
                tant = bool(fonster)
            d.rekt(fx, fy, fx + 8, fy + 10, 10 if tant else 1)
            if tant:
                d.rekt(fx, fy, fx + 8, fy + 2, 11)
                d.rekt(fx + 1, fy + 3, fx + 2, fy + 10, 9)
                d.rekt(fx + 6, fy + 3, fx + 7, fy + 10, 9)
            else:
                d.px(fx + 1, fy + 1, 3)
            d.rekt(fx - 2, fy + 11, fx + 10, fy + 12, 15)
    # Gesims med mässingsband
    d.rekt(tx0, 46, tx1, 49, 15)
    d.rekt(tx0, 49, tx1, 50, 10)
    d.rekt(tx0, 50, tx1, 51, 9)
    # Lobbyfönster med kristallkronor
    for (lx0, lx1) in [(tx0 + 4, 76), (116, tx1 - 4)]:
        d.rekt(lx0 - 1, 57, lx1 + 1, 91, 9)
        d.rekt(lx0, 58, lx1, 90, 10)
        d.vgrad(lx0, 58, lx1, 90, [11, 10, 9])
        cx = (lx0 + lx1) // 2
        d.rekt(cx, 58, cx + 1, 62, 9)
        d.poly([(cx - 4, 62), (cx + 5, 62), (cx + 2, 66), (cx - 1, 66)], 11)
        for kx in range(cx - 4, cx + 6, 2):
            d.px(kx, 67, 10)
        d.rekt(lx0, 74, lx1, 75, 9)

    # --- Entrén ---
    d.rekt(80, 56, 112, 96, 9)
    d.rekt(82, 66, 110, 94, 9)
    d.vgrad(83, 69, 109, 94, [10, 9, 9])
    # Karuselldörr: fyra vingar som roterar
    cx, r = 96, 12
    d.rekt(cx - r - 1, 67, cx + r + 2, 69, 9)
    vinkel = dorr * (math.pi / 2) / 6
    for k in range(4):
        a = vinkel + k * math.pi / 2
        xx = int(round(cx + r * math.sin(a)))
        fram = math.cos(a) > 0
        if fram:
            d.rekt(xx, 69, xx + 2, 94, 6)
            d.rekt(xx, 69, xx + 1, 94, 11)
        else:
            d.rekt(xx, 69, xx + 1, 94, 8)
    d.rekt(cx, 69, cx + 1, 94, 6)
    d.rekt(82, 94, 110, 96, 9)
    # Baldakin med namnet
    d.poly([(74, 54), (118, 54), (122, 64), (70, 64)], 12)
    d.rekt(70, 64, 122, 65, 6)
    d.rekt(74, 54, 118, 55, 10)
    text(d, 78, 58, "PETTIGREW", 10)
    for sx in (72, 120):
        d.rekt(sx, 65, sx + 1, 98, 10)
        d.px(sx, 98, 9)
    # Mässingslyktor
    for lx in (77, 113):
        d.rekt(lx, 70, lx + 3, 76, 11)
        d.rekt(lx, 69, lx + 3, 70, 9)
        d.rekt(lx, 76, lx + 3, 77, 9)
        d.radial(lx + 1, 73, 8, 0.6, mask=(d.a == 15) | (d.a == 5) | (d.a == 4))

    # --- Trottoar, röd matta och gata ---
    d.rekt(0, 96, W, 104, 4)
    d.vgrad(0, 96, W, 104, [3, 4])
    for xx in range(0, W, 12):
        d.rekt(xx, 96, xx + 1, 104, 3)
    d.poly([(84, 96), (108, 96), (112, 105), (80, 105)], 13)
    d.rekt(84, 96, 108, 97, 14)
    d.rekt(0, 104, W, 106, 15)
    d.rekt(0, 106, W, H, 1)
    d.vgrad(0, 106, W, H, [0, 1])
    # Spegelbilder av lobbyn och lyktorna
    for (x0, x1, f) in [(52, 76, 0.5), (116, 140, 0.5), (84, 108, 0.7)]:
        for y in range(107, H):
            s = f * (1 - (y - 107) / (H - 107))
            m = (XX >= x0) & (XX < x1) & (YY == y) & ((XX + y) % 2 == 0)
            d.ljus(m, s * 2)

    # --- Portiern Reginald ---
    px0 = 62
    d.rekt(px0, 74, px0 + 8, 76, 12)         # mössa
    d.rekt(px0 + 1, 72, px0 + 7, 74, 12)
    d.rekt(px0 + 1, 75, px0 + 7, 76, 10)     # mässingsband
    d.rekt(px0 + 2, 76, px0 + 7, 80, 10)     # ansikte
    d.px(px0 + 6, 77, 0)                     # öga
    d.px(px0 + 7, 78, 9)                     # näsan i vädret
    d.rekt(px0, 80, px0 + 9, 93, 12)         # rock
    d.rekt(px0 + 4, 80, px0 + 5, 93, 6)
    for by in (82, 85, 88):
        d.px(px0 + 3, by, 10)
        d.px(px0 + 6, by, 10)
    d.rekt(px0, 80, px0 + 9, 81, 10)         # epåletter
    d.rekt(px0 - 1, 86, px0 + 1, 88, 15)     # vita handskar
    d.rekt(px0 + 8, 86, px0 + 10, 88, 15)
    d.rekt(px0 + 1, 93, px0 + 4, 97, 0)      # ben
    d.rekt(px0 + 5, 93, px0 + 8, 97, 0)

    # --- Tunnelbanan till vänster ---
    d.rekt(8, 90, 40, 104, 0)
    for y in range(92, 104, 3):
        d.rekt(10, y, 38, y + 1, 1)
    d.rekt(6, 86, 42, 88, 12)
    for xx in range(8, 41, 4):
        d.rekt(xx, 88, xx + 1, 90, 12)
    for gx in (6, 40):
        d.rekt(gx, 70, gx + 2, 104, 12)
        d.rekt(gx - 1, 65, gx + 3, 70, 10)
        d.rekt(gx, 64, gx + 2, 65, 11)
    d.rekt(9, 74, 39, 82, 3)
    d.rekt(9, 74, 39, 75, 5)
    text(d, 12, 76, "SUBWAY", 15)

    # --- Träd i krukor ---
    for (kx, ky) in [(152, 96), (180, 96)]:
        d.rekt(kx - 5, ky - 6, kx + 6, ky, 15)
        d.rekt(kx - 5, ky - 6, kx + 6, ky - 5, 5)
        d.rekt(kx, ky - 20, kx + 1, ky - 6, 6)
        d.a[d.mask_ellips(kx - 8, ky - 34, kx + 9, ky - 16)] = 12
        d.ljus(d.mask_ellips(kx - 6, ky - 33, kx + 4, ky - 22), 0.4, MORKARE)
        d.ljus(d.mask_ellips(kx - 2, ky - 30, kx + 8, ky - 18), 0.3)

    # --- Duvan med fluga ---
    dx, dy = 132, 99
    d.rekt(dx, dy, dx + 6, dy + 4, 4)          # kropp
    d.rekt(dx + 1, dy, dx + 5, dy + 1, 5)
    d.rekt(dx - 2, dy + 1, dx, dy + 3, 3)      # stjärt
    d.px(dx + 2, dy + 4, 13)
    d.px(dx + 4, dy + 4, 13)                   # fötter
    hy = [dy - 3, dy - 1, dy + 1][duva]        # huvudets höjd
    hx = dx + 6 + (duva > 0)
    d.rekt(hx, hy, hx + 3, hy + 3, 4)
    d.px(hx + 2, hy, 0)                        # öga
    d.px(hx + 3, hy + 1, 9)                    # näbb
    d.px(hx + 4, hy + 1 + (duva == 2), 9)
    d.px(dx + 6, dy, 0)                        # flugan
    d.px(dx + 6, dy + 1, 0)
    d.px(dx + 7, dy, 13)
    d.px(dx + 5, dy, 13)

    # --- Duggregn och stämning ---
    regn_over(d, random.Random(9), 45, regn)
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
    "mainst": (main_street, [
        ("regn", "regn", [(i, 80) for i in range(10)]),
        ("anga", "anga", [(i, 200) for i in range(6)]),
        ("neon", "neon", [((1, 1, 1, 1, 1), 2600), ((1, 1, 0, 1, 1), 90), ((1, 1, 1, 1, 1), 70), ((1, 1, 0, 1, 1), 400),
                          ((1, 1, 1, 1, 1), 1800), ((1, 1, 0, 1, 1), 120), ((1, 1, 1, 1, 1), 900)]),
    ]),
    "parkave": (park_avenue, [
        ("regn", "regn", [(i, 110) for i in range(10)]),
        ("dorr", "dorr", [(i, 140) for i in range(6)]),
        ("duva", "duva", [(0, 1400), (1, 120), (2, 220), (1, 120), (0, 500), (1, 120), (2, 220), (1, 120), (0, 2200)]),
        ("fonster", "fonster", [(1, 5200), (0, 3800)]),
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
