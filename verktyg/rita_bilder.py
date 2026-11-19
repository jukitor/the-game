#!/usr/bin/env python3
"""Ritar spelets bilder i retrostil: låg upplösning, 16 färger och ordnad dithering.

Kör:  python3 verktyg/rita_bilder.py
Bilderna hamnar i mappen bilder/ som PNG med palett.
"""
import base64
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
    "L": ["100", "100", "100", "100", "111"], "F": ["111", "100", "110", "100", "100"],
    "K": ["101", "110", "100", "110", "101"], "3": ["111", "001", "011", "001", "111"],
    "M": ["10001", "11011", "10101", "10001", "10001"], "V": ["101", "101", "101", "101", "010"],
    "C": ["011", "100", "100", "100", "011"], "Z": ["111", "001", "010", "100", "111"],
    "9": ["111", "101", "111", "001", "111"],
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


# ======================================================================
#  SPRITAR (små figurer ritade som textrader)
# ======================================================================
SPRITFARG = {"k": 0, "f": 9, "d": 8, "w": 15, "p": 14, "c": 10, "r": 13, "n": 2, "g": 4, "s": 5, "b": 7}


def sprite(d, x, y, rader, farg=SPRITFARG):
    for ry, rad in enumerate(rader):
        for rx, ch in enumerate(rad):
            if ch != ".":
                d.px(x + rx, y + ry, farg[ch])


# Lord Waffles i olika humör (11 x 11 pixlar)
MOPS_ARG = ["kk.......kk", "kkfffffffkk", ".ffdfffdff.", ".fwkfffwkf.", ".ffkkkkkff.",
            ".fkkkkkkkf.", "..kwkwkwk..", "..ffcccff..", ".fffffffff.", ".fffffffff.", "ffkf...fkff"]
MOPS_ARG2 = MOPS_ARG[:6] + ["..kkwkwkk..", "..ffcccff..", ".fffffffff.", ".fffffffff.", "ffkf...fkff"]
MOPS_GLAD = MOPS_ARG[:5] + [".fkkkkkkkf.", "..kkpppkk..", "..ffcpcff..", ".fffffffff.", ".fffffffff.", "ffkf...fkff"]


def text_stor(d, x, y, s, c, skala):
    """Text med pixeltypsnittet, förstorad."""
    for ch in s:
        for ry, rad in enumerate(TYPSNITT[ch]):
            for rx, bit in enumerate(rad):
                if bit == "1":
                    d.rekt(x + rx * skala, y + ry * skala, x + (rx + 1) * skala, y + (ry + 1) * skala, c)
        x += (len(TYPSNITT[ch][0]) + 1) * skala


def lykta(d, x, y, sving=0):
    """Röd papperslykta som hänger i en punkt (x, y)."""
    x += sving
    d.rekt(x - 1, y, x + 2, y + 1, 10)
    d.a[d.mask_ellips(x - 3, y + 1, x + 4, y + 8)] = 13
    d.rekt(x - 2, y + 3, x + 3, y + 4, 14)
    d.px(x - 1, y + 2, 14)
    d.rekt(x - 1, y + 8, x + 2, y + 9, 10)
    d.px(x, y + 9, 10)
    d.px(x, y + 10, 13)


# ======================================================================
#  PETTIGREWS TAKVÅNING
# ======================================================================
def takvaning(v=None):
    v = v or {}
    fru = v.get("fru", 0)            # 0, 1 snyftar, 2 lycklig
    mops = v.get("mops", 0)          # 0 tom korg, 1 Lord Waffles i korgen
    kristall = v.get("kristall", 0)  # glittrets fas 0..3
    moln = v.get("moln", 0)          # inomhusregnets fas 0..5
    rnd = random.Random(1950)
    d = Duk(3)

    # Väggar med tapetränder och guldlister
    d.vgrad(0, 0, W, 84, [2, 3, 3])
    for x in range(2, W, 8):
        d.ljus((XX >= x) & (XX < x + 3) & (YY < 84), 0.35, MORKARE)
    d.rekt(0, 0, W, 4, 15)
    d.rekt(0, 4, W, 5, 10)
    d.rekt(0, 66, W, 67, 10)
    d.rekt(0, 67, W, 84, 2)
    for x in range(4, W, 20):
        d.rekt(x, 70, x + 14, 71, 10)
        d.rekt(x, 70, x + 1, 81, 10)
    # Parkettgolv
    d.rekt(0, 84, W, H, 8)
    for y in range(84, H):
        for x in range(0, W):
            if ((x + 2 * y) // 6) % 2:
                d.a[y, x] = 7
    d.vgrad(0, 84, W, 90, [6, 7])
    # Persisk matta
    d.poly([(44, 94), (152, 94), (164, 118), (32, 118)], 13)
    d.poly([(48, 96), (148, 96), (158, 116), (38, 116)], 6)
    d.poly([(52, 98), (144, 98), (152, 114), (44, 114)], 13)
    for x in range(54, 146, 6):
        for y in range(100, 113, 4):
            d.px(x + (y // 4) % 2 * 3, y, 10)
    d.a[d.mask_ellips(86, 101, 110, 111)] = 1
    d.a[d.mask_ellips(90, 103, 106, 109)] = 10

    # Hissen till vänster
    d.rekt(4, 20, 32, 86, 10)
    d.rekt(6, 24, 30, 86, 9)
    d.rekt(18, 24, 19, 86, 8)
    d.rekt(7, 25, 17, 85, 10)
    d.rekt(20, 25, 29, 85, 10)
    d.ljus(d.mask_poly([(7, 25), (29, 25), (29, 85), (7, 85)]), 0.4, MORKARE)
    d.a[d.mask_ellips(10, 10, 26, 22)] = 10
    d.a[d.mask_ellips(12, 12, 24, 22)] = 15
    d.rekt(10, 18, 27, 22, 2)
    d.linje(18, 18, 22, 13, 0)

    # Porträttet av Lord Waffles som amiral
    d.rekt(38, 10, 74, 52, 10)
    d.rekt(40, 12, 72, 50, 9)
    d.rekt(42, 14, 70, 48, 1)
    d.ljus(d.mask_poly([(42, 14), (70, 14), (70, 48), (42, 48)]), 0.3)
    d.rekt(46, 36, 66, 48, 2)          # uniform
    d.rekt(45, 36, 49, 38, 10)         # epåletter
    d.rekt(63, 36, 67, 38, 10)
    for by in (40, 43, 46):
        d.px(56, by, 10)
    sprite(d, 51, 25, MOPS_ARG2[:8])
    d.poly([(46, 25), (66, 25), (62, 20), (50, 20)], 0)   # tvåkantig hatt
    d.rekt(48, 23, 64, 24, 10)
    d.px(56, 21, 10)
    d.rekt(52, 51, 60, 53, 10)         # mässingsskylt

    # Hundkorgen i purpur
    if mops:
        sprite(d, 50, 62, MOPS_GLAD[:8])
    d.a[d.mask_ellips(42, 68, 70, 82)] = 13
    d.a[d.mask_ellips(45, 70, 67, 78)] = 6
    d.rekt(44, 70, 69, 72, 14)
    if mops:
        sprite(d, 50, 62, MOPS_GLAD[:8])
        d.rekt(51, 70, 61, 73, 9)

    # Kristallkrona
    d.rekt(103, 4, 104, 10, 10)
    d.poly([(92, 14), (115, 14), (110, 18), (97, 18)], 10)
    d.rekt(96, 10, 112, 11, 10)
    for i, kx in enumerate(range(92, 116, 3)):
        lang = 4 + (i % 3)
        for ky in range(18, 18 + lang):
            d.px(kx, ky, 5)
        glitter = (i + kristall) % 4 == 0
        d.px(kx, 18 + lang, 11 if glitter else 15)
    for kx in range(97, 111, 4):
        d.px(kx, 12, 11)
    d.radial(104, 16, 22, 0.45, mask=YY < 66)

    # Fönster mot staden långt där nere
    wx0, wy0, wx1, wy1 = 128, 10, 182, 74
    d.vgrad(wx0, wy0, wx1, wy1, [0, 1, 1, 2])
    for _ in range(40):
        hx, hy = rnd.randint(wx0, wx1 - 4), rnd.randint(46, wy1 - 2)
        d.rekt(hx, hy, hx + rnd.randint(3, 7), wy1, rnd.choice([0, 1]))
    for _ in range(90):
        d.px(rnd.randint(wx0, wx1 - 1), rnd.randint(50, wy1 - 1), rnd.choice([10, 9, 10, 14]))
    for _ in range(12):
        d.px(rnd.randint(wx0, wx1 - 1), rnd.randint(wy0, 40), 4)
    d.rekt(wx0 - 2, wy0 - 2, wx1 + 2, wy0, 15)
    d.rekt(wx0 - 2, wy1, wx1 + 2, wy1 + 2, 15)
    d.rekt(wx0 - 2, wy0, wx0, wy1, 15)
    d.rekt(wx1, wy0, wx1 + 2, wy1, 15)
    d.rekt(154, wy0, 156, wy1, 15)
    d.rekt(wx0, 40, wx1, 41, 15)
    # Draperier
    for (x0, x1) in [(120, 130), (180, 190)]:
        d.rekt(x0, 6, x1, 86, 13)
        for x in range(x0 + 1, x1, 3):
            d.rekt(x, 6, x + 1, 86, 14 if (x // 3) % 2 else 6)
    d.rekt(118, 5, 192, 7, 10)

    # Ett eget litet väder: moln som regnar på en palm
    for (cx, cy, rx, ry) in [(160, 8, 6, 3), (167, 6, 6, 4), (174, 9, 5, 3)]:
        d.a[d.mask_ellips(cx - rx, cy - ry, cx + rx, cy + ry)] = 4
    d.a[d.mask_ellips(158, 4, 170, 8)] = 5
    rrnd = random.Random(3)
    for _ in range(9):
        rx, ry = rrnd.randint(156, 178), rrnd.randint(13, 58)
        ry = 13 + (ry - 13 + moln * 8) % 48
        d.px(rx, ry, 5)
        d.px(rx, ry + 1, 15)
    # Palm i kruka
    d.rekt(162, 78, 174, 92, 15)
    d.rekt(162, 78, 174, 80, 10)
    d.rekt(167, 58, 169, 78, 7)
    for (ex, ey) in [(150, 66), (186, 64), (156, 56), (180, 55), (168, 52), (146, 72), (190, 72)]:
        d.linje(168, 58, ex, ey, 12)
        d.linje(168, 59, ex, ey + 1, 12)

    # Den vita soffan
    d.a[d.mask_ellips(74, 56, 126, 74)] = 15
    d.rekt(78, 64, 122, 84, 15)
    for tx in range(82, 120, 6):
        d.px(tx, 62, 5)
        d.px(tx + 3, 66, 5)
    d.rekt(76, 74, 124, 76, 5)
    d.a[d.mask_ellips(70, 66, 82, 86)] = 15
    d.a[d.mask_ellips(118, 66, 130, 86)] = 15
    d.ljus(d.mask_ellips(70, 76, 82, 86), 0.5, MORKARE)
    d.ljus(d.mask_ellips(118, 76, 130, 86), 0.5, MORKARE)
    for lx in (78, 120):
        d.rekt(lx, 84, lx + 2, 88, 10)

    # Fru Pettigrew
    fy = 1 if fru == 1 else 0
    d.rekt(92, 62 + fy, 108, 78, 2)                  # klänning
    d.rekt(90, 74, 110, 78, 2)
    d.a[d.mask_ellips(94, 46 + fy, 106, 58 + fy)] = 4   # hår
    d.a[d.mask_ellips(97, 42 + fy, 103, 48 + fy)] = 5   # knut
    d.rekt(96, 50 + fy, 105, 59 + fy, 10)            # ansikte
    d.rekt(96, 50 + fy, 105, 51 + fy, 4)
    for px_ in range(94, 107, 2):                    # pärlor
        d.px(px_, 61 + fy + (1 if 96 < px_ < 105 else 0), 15)
    if fru < 2:
        d.px(98, 53 + fy, 0)
        d.px(103, 53 + fy, 0)
        d.px(99 + fru * 3, 55 + fy, 5)               # tår
        d.rekt(99, 57 + fy, 103, 58 + fy, 13)
        hx = 104 if fru == 0 else 95
        d.rekt(hx, 52 + fy, hx + 5, 57 + fy, 15)     # spetsnäsduk
        d.px(hx + 1, 53 + fy, 5)
        d.px(hx + 3, 55 + fy, 5)
        d.rekt(hx + 1, 57 + fy, hx + 4, 62 + fy, 10)  # handen och armen
    else:
        d.px(98, 53, 0)
        d.px(103, 53, 0)
        d.rekt(98, 56, 104, 57, 13)
        d.px(97, 55, 13)
        d.px(104, 55, 13)
        d.rekt(86, 60, 92, 62, 10)                   # armarna utsträckta
        d.rekt(108, 60, 114, 62, 10)

    d.vinjett(0.35)
    return d


# ======================================================================
#  CHINATOWN
# ======================================================================
def chinatown(v=None):
    v = v or {}
    regn = v.get("regn", 0)
    sving = v.get("sving", 0)                       # lyktornas gungning 0..3
    neon = v.get("neon", 12)                        # hur många bokstäver i GOLDEN DRAGON som lyser
    anga = v.get("anga", 0)
    rnd = random.Random(1951)
    d = Duk(1)

    d.vgrad(0, 0, W, 30, [0, 0, 1])
    # Gatan som försvinner bort i mitten
    for i in range(6):
        x0 = 60 + i * 3
        x1 = 132 - i * 3
        top = 12 + i * 5
        for side in (0, 1):
            bx0, bx1 = (x0, x0 + 8) if side == 0 else (x1 - 8, x1)
            d.rekt(bx0, top, bx1, 90, [1, 1, 2, 2, 2, 3][i])
            for wy in range(top + 2, 84, 4):
                if rnd.random() < 0.5:
                    d.px(rnd.randint(bx0 + 1, bx1 - 2), wy, rnd.choice([13, 10, 14, 9]))
    d.vgrad(78, 40, 114, 90, [1, 2, 3])
    for _ in range(26):
        sx, sy = rnd.randint(78, 112), rnd.randint(44, 82)
        d.rekt(sx, sy, sx + rnd.randint(1, 3), sy + 1, rnd.choice([13, 14, 10, 12]))

    # Vänster husfasad i tegel med brandtrappor
    d.rekt(0, 0, 60, 92, 7)
    d.ljus(d.mask_poly([(0, 0), (60, 0), (60, 92), (0, 92)]), 0.5, MORKARE)
    for fy in (6, 26, 46):
        for fx in (6, 22, 38):
            d.rekt(fx, fy, fx + 9, fy + 11, 10 if rnd.random() < 0.5 else 1)
            d.rekt(fx, fy + 11, fx + 9, fy + 12, 6)
        d.rekt(2, fy + 14, 52, fy + 15, 0)
        for rx in range(2, 52, 3):
            d.px(rx, fy + 13, 0)
        d.linje(10, fy + 15, 18, fy + 33, 0)
    # Lodräta skyltar
    for (sx, c, t) in [(50, 13, 10), (40, 12, 15)]:
        d.rekt(sx, 18, sx + 7, 58 if c == 13 else 44, c)
        for yy in range(21, 56 if c == 13 else 42, 6):
            d.rekt(sx + 2, yy, sx + 5, yy + 1, t)
            d.rekt(sx + 3, yy + 1, sx + 4, yy + 4, t)
            d.px(sx + 2, yy + 3, t)

    # Höger husfasad med Golden Dragon
    d.rekt(132, 0, W, 92, 2)
    for fy in (6, 20):
        for fx in (138, 154, 170, 184):
            d.rekt(fx, fy, fx + 7, fy + 9, 10 if rnd.random() < 0.45 else 1)
    d.rekt(132, 32, W, 34, 0)
    # Neonskylten
    d.rekt(136, 36, 190, 56, 0)
    d.rekt(136, 36, 190, 37, 14)
    d.rekt(136, 55, 190, 56, 14)
    farger = [10 if i < neon else 1 for i in range(12)]
    text(d, 152, 39, "GOLDEN", 10, farger[:6])
    text(d, 150, 47, "DRAGON", 10, farger[6:])
    if neon:
        d.radial(163, 46, 30, 0.35 * min(neon, 12) / 12, mask=(d.a < 4) & ((YY < 36) | (YY > 56)))
    # Röd dörr med rund överdel
    d.rekt(148, 64, 178, 92, 13)
    d.a[d.mask_ellips(148, 56, 178, 74)] = 13
    d.rekt(152, 68, 174, 92, 10)
    d.a[d.mask_ellips(152, 61, 174, 77)] = 10
    d.vgrad(152, 70, 174, 92, [11, 10, 9])
    d.rekt(162, 64, 164, 92, 9)
    for lx in (142, 182):
        lykta(d, lx, 60, [0, 1, 0, -1][sving])

    # Lyktor på en lina tvärs över gatan
    pts = []
    for x in range(0, W):
        t = (x - 96) / 96
        pts.append((x, int(16 + 12 * (1 - t * t))))
    for x, y in pts:
        d.px(x, y, 0)
    gung = [0, 1, 0, -1][sving]
    for lx in range(14, W, 22):
        ly = pts[lx][1]
        lykta(d, lx, ly + 1, gung)
        d.radial(lx + gung, ly + 6, 9, 0.5, mask=(d.a < 5))

    # Stånd med torkad bläckfisk
    d.rekt(4, 60, 46, 62, 12)
    for i, x in enumerate(range(4, 46, 4)):
        d.poly([(x, 56), (x + 4, 56), (x + 4, 60), (x, 60)], 12 if i % 2 else 15)
    d.rekt(4, 62, 46, 63, 0)
    for bx in range(8, 44, 5):
        d.rekt(bx, 63, bx + 1, 64, 0)
        d.poly([(bx - 1, 64), (bx + 2, 64), (bx + 1, 70), (bx, 70)], 9)
        d.px(bx - 1, 71, 9)
        d.px(bx + 2, 71, 9)
    d.rekt(4, 78, 46, 92, 6)
    d.rekt(4, 78, 46, 80, 8)
    d.rekt(30, 72, 40, 78, 4)
    d.rekt(29, 72, 41, 73, 5)
    for spar in range(2):
        sx = 33 + spar * 4
        for y in range(71, 54, -1):
            sx += [0, 1, 0, -1][((y + 2 * anga + spar * 3) // 3) % 4]
            if (y + 2 * anga + spar) % 3:
                d.px(sx, y, 15 if y > 64 else 5)
    # Försäljaren
    d.rekt(14, 70, 22, 78, 1)
    d.a[d.mask_ellips(15, 64, 21, 71)] = 10
    d.poly([(12, 66), (24, 66), (18, 61)], 9)

    # Folk med paraplyer
    for (fx, c, paraply) in [(64, 0, 0), (74, 1, 13), (90, 0, 0), (104, 1, 12), (118, 0, 0)]:
        h = rnd.randint(14, 18)
        d.rekt(fx, 92 - h, fx + 6, 92, c)
        d.a[d.mask_ellips(fx + 1, 92 - h - 5, fx + 5, 92 - h + 1)] = c
        if paraply:
            d.poly([(fx - 5, 92 - h - 4), (fx + 11, 92 - h - 4), (fx + 3, 92 - h - 10)], paraply)
            d.rekt(fx + 3, 92 - h - 4, fx + 4, 92 - h + 2, 0)
    # Cykel
    for hx in (124, 138):
        d.a[d.mask_ellips(hx - 5, 84, hx + 5, 94)] = 0
        d.a[d.mask_ellips(hx - 3, 86, hx + 3, 92)] = 2
    d.linje(124, 89, 131, 84, 0)
    d.linje(131, 84, 138, 89, 0)
    d.linje(129, 83, 133, 83, 0)

    # Blöt gata med spegelbilder
    d.rekt(0, 92, W, H, 1)
    d.vgrad(0, 92, W, H, [2, 1, 0])
    for lx in range(14, W, 22):
        for y in range(95, H, 2):
            if (y // 2 + lx) % 3:
                d.px(lx + (y % 3) - 1, y, 13 if y < 110 else 6)
    for y in range(95, H, 2):
        for x in range(150, 176, 2):
            if (x + y) % 4 == 0 and neon:
                d.px(x, y, 10 if y < 106 else 9)

    regn_over(d, random.Random(11), 60, regn)
    d.vinjett(0.4)
    return d


# ======================================================================
#  GOLDEN DRAGON (restaurangen)
# ======================================================================
def golden_dragon(v=None):
    v = v or {}
    eld = v.get("eld", 0)        # wokens lågor 0..3
    karp = v.get("karp", 0)      # karpens läge 0..11
    katt = v.get("katt", 0)      # vinkande katt 0..1
    rnd = random.Random(1952)
    d = Duk(13)

    # Röda lackväggar med guldlister
    d.vgrad(0, 0, W, 70, [6, 13, 13])
    for x in range(0, W, 24):
        d.rekt(x, 8, x + 1, 70, 10)
    d.rekt(0, 6, W, 8, 10)
    d.rekt(0, 70, W, 72, 10)
    # Golv i schackmönster
    d.rekt(0, 72, W, H, 6)
    for y in range(72, H):
        for x in range(W):
            if ((x // 8) + (y // 6)) % 2:
                d.a[y, x] = 7
    d.vgrad(0, 72, W, 80, [0, 6])

    # Papperslyktor i taket
    for lx in (30, 160):
        d.rekt(lx, 0, lx + 1, 3, 0)
        d.a[d.mask_ellips(lx - 7, 3, lx + 8, 15)] = 14
        d.a[d.mask_ellips(lx - 5, 4, lx + 6, 14)] = 11
        for yy in (6, 9, 12):
            d.rekt(lx - 5, yy, lx + 6, yy + 1, 10)
        d.radial(lx, 10, 26, 0.5, mask=(YY < 70))

    # Köksluckan med Benny och wokpannan
    d.rekt(66, 20, 128, 58, 10)
    d.rekt(68, 22, 126, 56, 11)
    d.vgrad(68, 22, 126, 56, [11, 10, 9])
    d.rekt(66, 56, 128, 60, 8)
    d.rekt(66, 56, 128, 57, 9)
    # Kastruller på väggen därinne
    for kx in (110, 118):
        d.a[d.mask_ellips(kx - 3, 26, kx + 3, 32)] = 4
    # Benny
    d.rekt(96, 22, 104, 30, 15)            # kockmössa
    d.a[d.mask_ellips(94, 20, 106, 28)] = 15
    d.rekt(96, 30, 104, 37, 10)            # ansikte
    d.px(98, 33, 0)
    d.px(102, 33, 0)
    d.rekt(98, 35, 102, 36, 8)
    d.rekt(92, 37, 108, 56, 15)            # kockrock
    d.rekt(99, 38, 100, 56, 5)
    d.rekt(88, 42, 94, 45, 15)             # armen mot woken
    # Woken och lågorna
    d.a[d.mask_ellips(72, 46, 92, 54)] = 0
    d.rekt(72, 46, 92, 50, 11)
    d.a[d.mask_ellips(72, 46, 92, 54)] = 0
    d.rekt(70, 49, 94, 50, 0)
    d.linje(92, 49, 98, 46, 0)
    lagor = [[(76, 40), (80, 34), (84, 39), (88, 36)], [(75, 42), (79, 37), (83, 33), (88, 38)],
             [(77, 38), (81, 36), (85, 34), (88, 40)], [(76, 41), (80, 38), (83, 35), (87, 33)]][eld]
    for (fx, fy) in lagor:
        d.poly([(fx - 3, 47), (fx + 3, 47), (fx, fy)], 13)
        d.poly([(fx - 2, 47), (fx + 2, 47), (fx, fy + 3)], 10)
        d.poly([(fx - 1, 47), (fx + 1, 47), (fx, fy + 6)], 11)
    d.radial(82, 42, 16, 0.5, mask=(YY < 56))

    # Bås till vänster
    for bx in (0, 34):
        d.rekt(bx, 52, bx + 8, 100, 13)
        d.rekt(bx, 52, bx + 8, 54, 14)
        d.rekt(bx + 1, 54, bx + 2, 100, 14)
        d.rekt(bx + 8, 78, bx + 26, 86, 13)
        d.rekt(bx + 8, 78, bx + 26, 79, 14)
    d.rekt(56, 52, 64, 100, 13)
    d.rekt(56, 52, 64, 54, 14)
    for (tx0, tx1) in [(8, 34), (42, 56)]:
        d.rekt(tx0, 74, tx1, 77, 6)
        d.rekt(tx0, 74, tx1, 75, 8)
        d.rekt((tx0 + tx1) // 2, 77, (tx0 + tx1) // 2 + 2, 100, 0)
    d.a[d.mask_ellips(14, 66, 24, 75)] = 15       # tekanna
    d.rekt(22, 68, 26, 69, 15)
    d.rekt(17, 64, 21, 66, 15)
    d.a[d.mask_ellips(44, 70, 52, 75)] = 15       # skål
    d.rekt(48, 66, 49, 72, 9)                      # ätpinnar
    d.rekt(50, 66, 51, 72, 9)

    # Akvariet med den uttråkade karpen
    ax0, ay0, ax1, ay1 = 138, 30, 186, 64
    d.rekt(ax0 - 2, ay0 - 2, ax1 + 2, ay1 + 2, 0)
    d.vgrad(ax0, ay0, ax1, ay1, [4, 3, 3, 2])
    d.rekt(ax0, ay0, ax1, ay0 + 2, 5)
    d.rekt(ax0, ay1 - 4, ax1, ay1, 9)
    for gx in range(ax0, ax1, 3):
        d.px(gx, ay1 - 4, 8)
    for (px_, h) in [(144, 16), (148, 12), (178, 18), (182, 11)]:
        for y in range(ay1 - 4 - h, ay1 - 4):
            d.px(px_ + ((y // 3) % 2), y, 12)
    kx = [146, 149, 152, 155, 158, 161, 164, 167, 168, 165, 160, 152][karp]
    vanster = karp >= 9
    ky = 44 + [0, 1, 1, 0, 0, -1, -1, 0, 0, 1, 0, 0][karp]
    kropp = ["..ffff..", ".ffffdfk", "ffffffff", ".ffffff.", "..ff...."]
    if vanster:
        kropp = [r[::-1] for r in kropp]
        kx -= 4
    sprite(d, kx, ky, kropp)
    stjart_x = kx - 2 if not vanster else kx + 8
    d.px(stjart_x, ky + 1, 10)
    d.px(stjart_x, ky + 3, 10)
    d.px(stjart_x + (1 if not vanster else -1), ky + 2, 10)
    for i in range(3):
        bx = 150 + (karp * 5 + i * 13) % 30
        by = ay1 - 6 - ((karp * 3 + i * 11) % 28)
        d.px(bx, by, 5)
    d.rekt(ax0 - 4, ay1 + 2, ax1 + 4, 74, 6)
    d.rekt(ax0 - 4, ay1 + 2, ax1 + 4, 70, 7)

    # Kassadisken med lyckokakor och en vinkande katt
    d.rekt(118, 86, W, H, 7)
    d.rekt(118, 86, W, 89, 9)
    d.rekt(118, 89, W, 90, 6)
    for x in range(124, W, 14):
        d.rekt(x, 92, x + 10, 116, 6)
    d.rekt(166, 72, 186, 86, 4)                   # kassaapparat
    d.rekt(168, 70, 184, 74, 3)
    d.rekt(170, 76, 182, 80, 1)
    d.px(176, 77, 10)
    d.a[d.mask_ellips(140, 80, 160, 88)] = 15      # skål
    for (cx_, cy_) in [(144, 79), (149, 78), (154, 79), (147, 81), (152, 81)]:
        d.poly([(cx_, cy_ + 2), (cx_ + 2, cy_), (cx_ + 4, cy_ + 2), (cx_ + 2, cy_ + 3)], 10)
        d.px(cx_ + 2, cy_ + 1, 9)
    # Lyckokatt
    d.rekt(124, 76, 134, 86, 15)
    d.a[d.mask_ellips(123, 68, 135, 78)] = 15
    d.px(124, 68, 15)
    d.px(133, 68, 15)
    d.px(126, 72, 0)
    d.px(131, 72, 0)
    d.rekt(124, 77, 134, 78, 13)
    d.px(129, 78, 10)
    if katt:
        d.rekt(134, 70, 136, 76, 15)
    else:
        d.rekt(134, 74, 137, 77, 15)
        d.rekt(136, 72, 138, 75, 15)

    d.vinjett(0.35)
    return d


# ======================================================================
#  PIR 9
# ======================================================================
def pir9(v=None):
    import math
    v = v or {}
    dimma = v.get("dimma", 0)    # dimmans fas 0..5
    fyr = v.get("fyr", 0)        # fyrens ljuskägla 0..7
    lage = v.get("lage", 0)      # 0 Bruno vaktar, 1 Bruno har gått, 2 dörren är öppen
    vagor = v.get("vagor", 0)    # vattnets fas 0..3
    d = Duk(2)

    d.vgrad(0, 0, W, 64, [1, 2, 3, 3])
    # Fyren långt borta och ljuskäglan
    fx, fy = 172, 34
    d.rekt(fx - 1, fy, fx + 2, 62, 15)
    for y in range(fy + 3, 62, 6):
        d.rekt(fx - 1, y, fx + 2, y + 3, 13)
    d.rekt(fx - 2, fy - 3, fx + 3, fy, 1)
    d.px(fx, fy - 2, 11)
    d.px(fx + 1, fy - 2, 11)
    vinkel = [-2.6, -2.9, 2.9, 2.6, None, None, None, None][fyr]
    if vinkel is not None:
        for r in range(4, 90):
            for bredd in range(-r // 8, r // 8 + 1):
                x = int(fx + r * math.cos(vinkel) - bredd * math.sin(vinkel) * 0.2)
                y = int(fy - 2 + r * math.sin(vinkel) * 0.15 + bredd)
                if 0 <= x < W and 0 <= y < 64 and (x + y) % 2 == 0:
                    d.a[y, x] = LJUSARE[d.a[y, x]]
    else:
        d.px(fx, fy - 2, 10)
    # Ett fartyg i dimman
    d.poly([(118, 56), (162, 56), (158, 63), (122, 63)], 1)
    d.rekt(130, 50, 146, 56, 1)
    d.rekt(136, 44, 140, 50, 1)
    for px_ in range(126, 158, 6):
        d.px(px_, 59, 10)
    # Vattnet
    d.rekt(104, 62, W, 98, 1)
    for y in range(64, 98, 3):
        for x in range(104, W, 8):
            xx = x + ((y // 3 + vagor) % 4) * 2
            d.rekt(xx, y, xx + 3, y + 1, 3 if y < 80 else 2)

    # Lagerlokalen i korrugerad plåt
    d.rekt(0, 14, 108, 98, 3)
    for x in range(0, 108, 4):
        d.rekt(x, 14, x + 1, 98, 2)
        d.rekt(x + 2, 14, x + 3, 98, 4)
    d.poly([(0, 14), (108, 14), (100, 6), (0, 6)], 1)
    d.rekt(0, 13, 108, 14, 0)
    d.ljus(d.mask_poly([(0, 14), (108, 14), (108, 98), (0, 98)]), 0.3, MORKARE)
    # Skylten LAGER 13 med en stor etta och en ännu större trea
    text(d, 8, 22, "LAGER", 15)
    text_stor(d, 30, 19, "1", 15, 2)
    text_stor(d, 38, 17, "3", 15, 3)
    # Dörren
    dx0, dx1 = 54, 78
    d.rekt(dx0 - 2, 52, dx1 + 2, 98, 1)
    if lage == 2:
        d.rekt(dx0, 54, dx1, 98, 0)
        d.ljus(d.mask_poly([(dx0, 90), (dx1, 90), (dx1, 98), (dx0, 98)]), 0.4)
        d.poly([(dx0, 54), (dx0 + 6, 58), (dx0 + 6, 94), (dx0, 98)], 4)
        d.px(dx0 + 4, 76, 10)
        d.rekt(dx1 - 4, 74, dx1 - 2, 79, 10)
    else:
        d.rekt(dx0, 54, dx1, 98, 4)
        for y in range(58, 98, 8):
            d.rekt(dx0, y, dx1, y + 1, 3)
        d.rekt(dx1 - 6, 72, dx1 - 2, 76, 10)
        d.rekt(dx1 - 5, 69, dx1 - 3, 72, 9)
    # Lampa ovanför dörren
    d.rekt(62, 46, 70, 48, 0)
    d.rekt(63, 48, 69, 50, 11)
    d.radial(66, 60, 30, 0.5, mask=(XX < 108))

    # Lådor och en pollare
    for (bx, by, bw, bh) in [(84, 84, 14, 14), (86, 72, 12, 12), (20, 86, 16, 12)]:
        d.rekt(bx, by, bx + bw, by + bh, 8)
        d.rekt(bx, by, bx + bw, by + 1, 9)
        d.linje(bx, by, bx + bw - 1, by + bh - 1, 7)
        d.linje(bx + bw - 1, by, bx, by + bh - 1, 7)
        d.rekt(bx, by, bx + 1, by + bh, 7)
    d.rekt(122, 92, 130, 102, 0)
    d.rekt(120, 90, 132, 93, 0)
    d.linje(130, 95, 150, 103, 9)
    d.linje(130, 96, 150, 104, 8)

    # Bruno
    if lage == 0:
        bx = 72
        d.rekt(bx, 60, bx + 28, 98, 0)             # rock, axlar som kylskåp
        d.a[d.mask_ellips(bx - 2, 58, bx + 10, 70)] = 0
        d.a[d.mask_ellips(bx + 18, 58, bx + 30, 70)] = 0
        d.rekt(bx + 9, 50, bx + 19, 61, 9)         # huvud
        d.rekt(bx + 8, 48, bx + 20, 52, 1)         # keps
        d.rekt(bx + 6, 51, bx + 20, 52, 1)
        d.px(bx + 11, 55, 0)
        d.px(bx + 16, 55, 0)
        d.rekt(bx + 12, 58, bx + 17, 59, 7)        # bister mun
        d.rekt(bx + 4, 74, bx + 24, 80, 1)         # armar i kors
        d.rekt(bx + 3, 74, bx + 7, 79, 9)
        d.rekt(bx + 21, 75, bx + 25, 80, 9)
        d.rekt(bx + 10, 61, bx + 18, 64, 15)       # skjortkrage
        d.rekt(bx + 7, 98, bx + 12, 99, 0)

    # Bryggans plankor
    d.rekt(0, 98, W, H, 7)
    for y in range(98, H, 4):
        d.rekt(0, y, W, y + 1, 6)
        for x in range((y * 7) % 23, W, 23):
            d.rekt(x, y + 1, x + 1, y + 4, 6)
    d.vgrad(0, 98, W, 104, [6, 7])

    # Dimma som driver över vattnet och himlen
    s = 0.22 + 0.16 * np.sin(2 * np.pi * (XX + dimma * 16) / 96 + YY / 9.0)
    omr = (YY > 30) & (YY < 96) & ((XX > 100) | (YY < 50))
    d.ljus(omr, s)
    d.vinjett(0.4)
    return d


# ======================================================================
#  LAGER 13 (inuti)
# ======================================================================
def lager13(v=None):
    v = v or {}
    damm = v.get("damm", 0)    # dammkorn i ljuset 0..7
    mops = v.get("mops", 0)    # 0, 1 morrar i buren, 2 ute och glad, 3 borta
    rnd = random.Random(1953)
    d = Duk(6)

    # Plankväggar
    d.rekt(0, 0, W, 88, 6)
    for x in range(0, W, 7):
        d.rekt(x, 0, x + 6, 88, 7)
        d.rekt(x + 6, 0, x + 7, 88, 0)
        if rnd.random() < 0.4:
            d.px(x + 3, rnd.randint(4, 80), 6)
    d.rekt(0, 0, W, 6, 0)
    for x in range(10, W, 46):
        d.rekt(x, 6, x + 4, 88, 6)
    # Högt fönster med galler
    d.rekt(140, 10, 164, 24, 4)
    d.vgrad(140, 10, 164, 24, [5, 4])
    for x in range(144, 164, 5):
        d.rekt(x, 10, x + 1, 24, 0)
    d.rekt(138, 8, 166, 10, 0)
    d.rekt(138, 24, 166, 26, 0)
    # Betonggolv
    d.rekt(0, 88, W, H, 3)
    d.vgrad(0, 88, W, H, [2, 3, 3])
    for _ in range(14):
        sx, sy = rnd.randint(0, W - 10), rnd.randint(92, H - 3)
        d.ljus(d.mask_ellips(sx, sy, sx + rnd.randint(4, 12), sy + 3), 0.6, MORKARE)

    # Ljusstrimma från fönstret
    strale = d.mask_poly([(140, 24), (164, 24), (130, 112), (84, 112)])
    d.ljus(strale, 0.45)

    # Fruktlådor till vänster
    for (bx, by) in [(2, 70), (24, 70), (46, 70), (8, 52), (30, 52), (16, 34)]:
        d.rekt(bx, by, bx + 20, by + 18, 8)
        d.rekt(bx, by, bx + 20, by + 1, 9)
        d.rekt(bx, by + 17, bx + 20, by + 18, 7)
        d.rekt(bx, by, bx + 1, by + 18, 7)
        d.rekt(bx + 19, by, bx + 20, by + 18, 7)
        text(d, bx + 1, by + 7, "FRUKT", 6)

    # Hämtmatskartonger från Golden Dragon
    for (kx, ky, valt) in [(150, 96, 0), (162, 100, 1), (174, 94, 0), (140, 106, 1), (156, 110, 0), (176, 108, 0),
                           (66, 102, 1), (52, 108, 0), (186, 100, 1), (130, 98, 0), (78, 110, 0), (168, 86, 0)]:
        if valt:
            d.poly([(kx, ky + 5), (kx + 7, ky + 2), (kx + 9, ky + 6), (kx + 2, ky + 9)], 15)
            d.px(kx + 4, ky + 5, 13)
        else:
            d.poly([(kx, ky), (kx + 8, ky), (kx + 7, ky + 7), (kx + 1, ky + 7)], 15)
            d.rekt(kx + 1, ky + 2, kx + 7, ky + 3, 13)
            d.linje(kx + 2, ky, kx + 4, ky - 3, 4)
            d.linje(kx + 6, ky, kx + 4, ky - 3, 4)

    # Glödlampa över buren
    d.rekt(104, 0, 105, 30, 0)
    d.rekt(102, 30, 107, 32, 4)
    d.a[d.mask_ellips(102, 32, 107, 37)] = 11
    d.radial(104, 50, 34, 0.45, mask=(YY > 36))

    # Hundburen
    cx0, cy0, cx1, cy1 = 86, 64, 122, 96
    d.rekt(cx0, cy1 - 2, cx1, cy1 + 1, 4)          # botten
    if mops in (0, 1):
        sprite(d, 98, 82, (MOPS_ARG if mops == 0 else MOPS_ARG2)[:11])
        d.px(99, 81, 0)
        d.px(107, 81, 0)
    oppen = mops >= 2
    dorr0, dorr1 = cx0 + 9, cx1 - 8           # burdörrens bredd
    for x in range(cx0, cx1 + 1, 3):
        if oppen and dorr0 < x < dorr1:
            continue
        d.rekt(x, cy0, x + 1, cy1, 4)
    d.rekt(cx0, cy0, cx1 + 1, cy0 + 1, 5)
    mitt = (cy0 + cy1) // 2
    d.rekt(cx0, mitt, cx1 + 1, mitt + 1, 4)
    if oppen:
        # Dörren uppslagen åt höger: kortare galler i perspektiv
        d.rekt(dorr0, mitt, dorr1, mitt + 1, 0)
        d.ljus(d.mask_poly([(dorr0, cy0 + 1), (dorr1, cy0 + 1), (dorr1, cy1 - 2), (dorr0, cy1 - 2)]), 0.4, MORKARE)
        for k in range(5):
            x = cx1 + 2 + k * 2
            d.rekt(x, cy0 + 2 + k, x + 1, cy1 - 1 - k // 2, 4)
        d.linje(cx1 + 2, cy0 + 2, cx1 + 10, cy0 + 6, 5)
        d.linje(cx1 + 2, mitt, cx1 + 10, mitt + 2, 4)
    if mops == 2:
        sprite(d, 128, 92, MOPS_GLAD)
        d.px(139, 98, 9)
        d.px(140, 97, 9)

    # Dammkorn som svävar i ljuset
    drnd = random.Random(5)
    for _ in range(16):
        bx, by = drnd.randint(100, 160), drnd.randint(28, 100)
        by = 28 + (by - 28 - damm * 3) % 72
        bx += [0, 1, 1, 0, -1, -1, 0, 0][(by // 4 + damm) % 8]
        if strale[min(by, H - 1), min(bx, W - 1)]:
            d.px(bx, by, 15 if drnd.random() < 0.5 else 11)

    d.vinjett(0.45)
    return d


# ======================================================================
#  TUNNELBANEPERRONGER (gemensamma delar)
# ======================================================================
def textbredd(s):
    return sum(len(TYPSNITT[ch][0]) + 1 for ch in s) - 1


def skylt(d, cx, y, s, bg, fg, ram, pad=3):
    """Centrerad skylt med ram. Returnerar skyltens kanter."""
    b = textbredd(s)
    x0, x1 = cx - b // 2 - pad, cx + (b + 1) // 2 + pad
    d.rekt(x0 - 1, y - 1, x1 + 1, y + 5 + pad * 2 - 1, ram)
    d.rekt(x0, y, x1, y + 5 + pad * 2 - 2, bg)
    text(d, x0 + pad, y + pad - 1, s, fg)
    return x0, x1


def linjekarta(d, x, y, aktiv):
    """Liten linjekarta med fyra stationer. aktiv = 0..3 markerar var man är."""
    d.rekt(x - 1, y - 1, x + 33, y + 13, 0)
    d.rekt(x, y, x + 32, y + 12, 15)
    d.rekt(x + 3, y + 6, x + 29, y + 7, 13)
    for i in range(4):
        sx = x + 4 + i * 8
        d.rekt(sx - 1, y + 5, sx + 2, y + 8, 0)
        d.px(sx, y + 6, 11 if i == aktiv else 15)
        d.px(sx + 1, y + 6, 11 if i == aktiv else 15)
    for i in range(4):
        d.rekt(x + 3 + i * 8, y + 2, x + 7 + i * 8, y + 3, 4)
        d.rekt(x + 3 + i * 8, y + 9, x + 6 + i * 8, y + 10, 4)


def spar(d, rnd, y0=96, slipers=6, rals=4):
    """Spårgropen längst ner."""
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


# ======================================================================
#  PERRONGEN VID MAIN STREET
# ======================================================================
def perrong_main(v=None):
    v = v or {}
    zzz = v.get("zzz", 0)        # snarkningar 0..3
    lampa = v.get("lampa", 1)    # glappande glödlampa
    rnd = random.Random(2001)
    d = Duk(15)

    # Smutsvitt kakel
    d.rekt(0, 0, W, 76, 15)
    for y in range(8, 76, 4):
        d.rekt(0, y, W, y + 1, 4)
        for x in range(((y // 4) % 2) * 4, W, 8):
            d.rekt(x, y, x + 1, y + 4, 4)
    d.ljus(d.mask_poly([(0, 0), (W, 0), (W, 76), (0, 76)]), 0.35, MORKARE)
    for _ in range(18):
        sx, sy = rnd.randint(0, W - 8), rnd.randint(30, 70)
        d.ljus(d.mask_ellips(sx, sy, sx + rnd.randint(4, 10), sy + rnd.randint(6, 16)), 0.6, MORKARE)
    # Grönt kakelband och mosaikskylt
    d.rekt(0, 54, W, 60, 12)
    for x in range(0, W, 4):
        d.px(x, 56, 6)
    d.rekt(0, 0, W, 8, 1)
    skylt(d, 96, 18, "MAIN ST", 15, 0, 13, pad=4)
    for x in range(80, 114, 2):
        d.px(x, 17, 12)
        d.px(x + 1, 32, 12)
    # Stålbalkar med nitar
    for bx in (54, 140):
        d.rekt(bx, 0, bx + 6, 92, 2)
        d.rekt(bx + 1, 0, bx + 2, 92, 3)
        for ny in range(6, 92, 8):
            d.px(bx + 4, ny, 4)
    # Linjekarta
    linjekarta(d, 12, 30, 0)
    # Glödlampor i taket
    for i, lx in enumerate((28, 98, 168)):
        d.rekt(lx, 8, lx + 1, 12, 0)
        tand = lampa if i == 2 else 1
        d.rekt(lx - 1, 12, lx + 2, 15, 11 if tand else 4)
        if tand:
            d.radial(lx, 30, 30, 0.35, mask=(YY > 14) & (YY < 92))
    # Golv
    d.rekt(0, 76, W, 92, 3)
    d.vgrad(0, 76, W, 92, [2, 3, 4])
    for y in range(78, 92, 4):
        d.rekt(0, y, W, y + 1, 2)
    # Jordnötsskal och en tidning på golvet
    for _ in range(26):
        d.px(rnd.randint(4, W - 4), rnd.randint(80, 90), rnd.choice([9, 8, 10]))
    d.poly([(20, 86), (30, 84), (32, 88), (22, 90)], 15)
    plattformskant(d)
    spar(d, rnd)

    # Bänk med en sovande man under en tidning
    d.rekt(112, 72, 172, 76, 8)
    d.rekt(112, 72, 172, 73, 9)
    d.rekt(112, 64, 172, 66, 8)
    for lx in (116, 166):
        d.rekt(lx, 66, lx + 2, 90, 0)
    d.rekt(122, 65, 158, 72, 4)              # rocken
    d.rekt(122, 70, 158, 72, 3)
    d.rekt(124, 65, 156, 66, 5)
    d.rekt(140, 66, 141, 72, 3)
    d.rekt(158, 67, 166, 71, 0)              # skor
    d.rekt(114, 64, 124, 72, 15)             # tidningen över ansiktet
    d.linje(115, 66, 122, 66, 4)
    d.linje(115, 68, 121, 68, 4)
    d.rekt(110, 66, 114, 70, 10)             # hand som hänger ner
    d.rekt(108, 70, 111, 74, 10)
    # Zzz som stiger
    for i in range(3):
        steg = (zzz + i) % 4
        if steg == 3:
            continue
        zx, zy = 118 + steg * 4 + i, 58 - steg * 7
        text(d, zx, zy, "Z", 4 if steg == 2 else 5)

    d.vinjett(0.4)
    return d


# ======================================================================
#  PERRONGEN VID PARK AVENUE
# ======================================================================
NOT = ["..c", "..c", "ccc", "cc."]


def perrong_park(v=None):
    v = v or {}
    strake = v.get("strake", 0)   # fiolstråken 0..3
    noter = v.get("noter", 0)     # noter som svävar 0..5
    d = Duk(15)

    # Marmorväggar med ådring och mässingslister
    d.rekt(0, 0, W, 76, 15)
    rnd = random.Random(2002)
    for _ in range(26):
        x, y = rnd.randint(0, W), rnd.randint(10, 70)
        for k in range(rnd.randint(6, 16)):
            x += rnd.choice([-1, 0, 1])
            y += 1
            d.px(x, y, 5)
    d.rekt(0, 0, W, 8, 2)
    d.rekt(0, 8, W, 10, 10)
    d.rekt(0, 52, W, 54, 10)
    d.rekt(0, 54, W, 76, 5)
    for x in range(0, W, 16):
        d.rekt(x, 54, x + 1, 76, 4)
    # Väggarmaturer
    for lx in (20, 172):
        d.rekt(lx - 2, 30, lx + 3, 38, 10)
        d.a[d.mask_ellips(lx - 3, 22, lx + 4, 31)] = 11
        d.radial(lx, 30, 20, 0.5, mask=(d.a == 15) | (d.a == 5))
    # Emaljskylt i mässingsram
    skylt(d, 96, 16, "PARK AVE", 2, 15, 10, pad=4)
    linjekarta(d, 150, 60, 1)
    # Blankt golv med spegelbilder
    d.rekt(0, 76, W, 92, 5)
    d.vgrad(0, 76, W, 92, [4, 5, 5])
    for y in range(76, 92, 5):
        d.rekt(0, y, W, y + 1, 4)
    plattformskant(d)
    spar(d, rnd, slipers=6, rals=5)

    # Två torkade bänkar
    for bx in (26, 126):
        d.rekt(bx, 70, bx + 30, 74, 9)
        d.rekt(bx, 70, bx + 30, 71, 10)
        d.rekt(bx, 60, bx + 30, 63, 9)
        d.rekt(bx, 60, bx + 30, 61, 10)
        for lx in (bx + 2, bx + 26):
            d.rekt(lx, 63, lx + 2, 90, 10)
        d.ljus(d.mask_poly([(bx, 76), (bx + 30, 76), (bx + 30, 82), (bx, 82)]), 0.4)
    # Ormbunke i mässingskruka
    d.rekt(66, 78, 76, 90, 10)
    d.rekt(66, 78, 76, 79, 11)
    for (ex, ey) in [(58, 70), (84, 70), (62, 64), (80, 64), (71, 60)]:
        d.linje(71, 78, ex, ey, 12)

    # Fiolspelaren
    mx = 100
    d.rekt(mx, 50, mx + 10, 76, 0)           # frack
    d.rekt(mx + 4, 50, mx + 6, 60, 15)       # skjortbröst
    d.px(mx + 5, 51, 13)                     # fluga
    d.rekt(mx + 2, 76, mx + 4, 90, 0)
    d.rekt(mx + 6, 76, mx + 8, 90, 0)
    d.rekt(mx + 2, 40, mx + 9, 50, 10)       # huvud
    d.rekt(mx + 1, 38, mx + 10, 42, 7)       # hår
    d.px(mx + 4, 45, 0)
    d.px(mx + 4, 44, 0)                      # slutna ögon, njuter
    d.px(mx + 3, 45, 0)
    # Fiolen under hakan
    d.poly([(mx - 4, 50), (mx + 3, 48), (mx + 4, 52), (mx - 3, 55)], 8)
    d.linje(mx - 4, 51, mx - 12, 54, 6)
    d.px(mx - 1, 51, 9)
    # Stråken
    stx, sty = [(mx - 8, 44), (mx - 5, 45), (mx - 2, 46), (mx - 5, 45)][strake]
    d.linje(stx, sty, stx + 14, sty + 14, 15)
    d.rekt(stx + 13, sty + 13, stx + 16, sty + 16, 10)
    # Fiollådan med mynt
    d.poly([(110, 86), (134, 86), (136, 91), (108, 91)], 7)
    d.rekt(112, 87, 132, 90, 13)
    for cx in (116, 121, 127):
        d.px(cx, 88, 10)
    # Noter som svävar uppåt
    nrnd = random.Random(4)
    for i in range(4):
        nx0 = 86 + nrnd.randint(-10, 20)
        fas = (noter + i * 2) % 6
        if fas == 5:
            continue
        sprite(d, nx0 + fas * 2 - i, 42 - fas * 6, NOT)

    d.vinjett(0.35)
    return d


# ======================================================================
#  PERRONGEN VID CHINATOWN
# ======================================================================
def perrong_china(v=None):
    v = v or {}
    folk = v.get("folk", 0)     # folkmassan som rör sig 0..3
    sving = v.get("sving", 0)   # lyktor 0..3
    rnd = random.Random(2003)
    d = Duk(13)

    # Rött kakel med grönt band
    d.rekt(0, 0, W, 76, 13)
    for y in range(8, 76, 4):
        d.rekt(0, y, W, y + 1, 6)
        for x in range(((y // 4) % 2) * 4, W, 8):
            d.rekt(x, y, x + 1, y + 4, 6)
    d.ljus(d.mask_poly([(0, 0), (W, 0), (W, 76), (0, 76)]), 0.3, MORKARE)
    d.rekt(0, 0, W, 8, 1)
    d.rekt(0, 40, W, 46, 12)
    for x in range(0, W, 6):
        d.rekt(x, 42, x + 3, 44, 10)
    skylt(d, 52, 16, "CHINATOWN", 12, 15, 10, pad=3)
    linjekarta(d, 6, 50, 2)
    # Golv och kant
    d.rekt(0, 76, W, 92, 3)
    d.vgrad(0, 76, W, 92, [2, 3])
    plattformskant(d)
    spar(d, rnd)

    # Ett tåg står inne till höger
    d.rekt(104, 18, W, 98, 4)
    d.rekt(104, 18, W, 22, 5)
    d.rekt(104, 86, W, 98, 3)
    d.rekt(104, 60, W, 62, 13)
    for wx in (110, 140, 170):
        d.rekt(wx, 28, wx + 18, 48, 10)
        d.vgrad(wx, 28, wx + 18, 48, [11, 10])
        for px_ in range(wx + 2, wx + 16, 5):          # passagerare
            d.rekt(px_, 36, px_ + 3, 48, 7)
            d.rekt(px_, 33, px_ + 3, 36, 8)
        d.rekt(wx, 39, wx + 18, 40, 9)                  # handtag
    d.rekt(130, 26, 138, 86, 0)                         # öppen dörr
    d.rekt(131, 27, 137, 86, 9)
    d.rekt(160, 26, 162, 86, 3)
    d.rekt(104, 18, 106, 98, 3)

    # Lyktor i taket
    for lx in (16, 60, 96):
        d.rekt(lx, 8, lx + 1, 11, 0)
        lykta(d, lx, 11, [0, 1, 0, -1][(sving + lx // 20) % 4])
        d.radial(lx, 16, 14, 0.4, mask=(YY < 40) & (d.a != 10))

    # Folk med matkassar
    gestalter = [(10, 1, 15), (24, 0, 9), (38, 1, 15), (52, 0, 15), (66, 1, 9), (80, 0, 15), (92, 1, 9), (120, 0, 15)]
    for i, (fx, c, kasse) in enumerate(gestalter):
        hopp = 1 if (i + folk) % 4 == 0 else 0
        h = 18 + (i * 5) % 6
        topp = 92 - h - hopp
        d.rekt(fx, topp + 5, fx + 8, 92, c)
        d.a[d.mask_ellips(fx + 1, topp, fx + 7, topp + 6)] = c
        kx = fx + 8 if i % 2 else fx - 4
        d.rekt(kx, topp + 12, kx + 5, topp + 19, kasse)
        d.rekt(kx + 1, topp + 10, kx + 2, topp + 12, kasse)
        if kasse == 15:
            d.linje(kx + 2, topp + 12, kx + 4, topp + 3, 12)   # purjolök
            d.px(kx + 4, topp + 2, 12)
            d.px(kx + 5, topp + 3, 12)
        else:
            d.px(kx + 2, topp + 11, 10)                        # ingefära
            d.px(kx + 3, topp + 11, 9)
    d.vinjett(0.4)
    return d


# ======================================================================
#  PERRONGEN VID PIR 9 (slutstationen)
# ======================================================================
def perrong_pir(v=None):
    v = v or {}
    ror = v.get("ror", 1)        # lysröret som morsar: 1 tänt, 0 släckt
    dropp = v.get("dropp", 0)    # vattendroppen 0..5
    ratta = v.get("ratta", 0)    # råttans läge 0..7
    rnd = random.Random(2004)
    d = Duk(3)

    # Smutsigt kakel med hål och fuktfläckar
    d.rekt(0, 0, W, 76, 3)
    for y in range(8, 76, 4):
        d.rekt(0, y, W, y + 1, 2)
        for x in range(((y // 4) % 2) * 4, W, 8):
            d.rekt(x, y, x + 1, y + 4, 2)
    for _ in range(30):
        tx = rnd.randrange(0, W, 8) + ((rnd.randint(0, 17) // 4) % 2) * 4
        ty = rnd.randrange(8, 72, 4)
        d.rekt(tx + 1, ty + 1, tx + 8, ty + 4, 1)
    for _ in range(10):
        sx, sy = rnd.randint(0, W - 10), rnd.randint(8, 30)
        d.ljus(d.mask_poly([(sx, sy), (sx + 8, sy), (sx + 5, sy + rnd.randint(12, 26)), (sx + 2, sy + rnd.randint(8, 18))]), 0.6, MORKARE)
    d.rekt(0, 0, W, 8, 0)
    # Skylt med en lös skruv
    x0, x1 = skylt(d, 70, 18, "PIR 9", 1, 15, 6, pad=4)
    d.px(x0 + 1, 19, 9)
    linjekarta(d, 140, 40, 3)
    d.linje(141, 41, 150, 52, 0)                       # någon har ritat på kartan

    # Lysrör i taket
    for i, rx in enumerate((14, 84, 150)):
        tand = ror if i == 1 else (1 if i == 0 else 0)
        d.rekt(rx, 8, rx + 26, 10, 0)
        d.rekt(rx + 1, 10, rx + 25, 12, 15 if tand else 2)
        if tand:
            d.radial(rx + 13, 24, 34, 0.45, mask=(YY > 12) & (YY < 92))

    # Golv med pöl
    d.rekt(0, 76, W, 92, 2)
    d.vgrad(0, 76, W, 92, [1, 2, 3])
    d.a[d.mask_ellips(96, 82, 124, 90)] = 1
    d.ljus(d.mask_ellips(100, 83, 118, 88), 0.4)
    plattformskant(d)
    d.ljus(d.mask_poly([(0, 92), (W, 92), (W, 95), (0, 95)]), 0.5, MORKARE)
    spar(d, rnd)
    # Tunnelmynningen och stoppbocken där linjen tar slut
    d.a[d.mask_ellips(150, 70, 192, 130)] = 0
    d.rekt(156, 100, 186, 104, 13)
    for x in range(156, 186, 6):
        d.rekt(x, 100, x + 3, 104, 15)
    d.rekt(158, 104, 160, 112, 13)
    d.rekt(182, 104, 184, 112, 13)

    # Vattendropp från en spricka i taket
    d.linje(108, 8, 112, 14, 0)
    if dropp < 5:
        dy = [16, 30, 48, 66, 80][dropp]
        d.px(110, dy, 5)
        d.px(110, dy + 1, 4)
    else:
        d.rekt(104, 85, 117, 86, 5)
        d.px(102, 84, 4)
        d.px(118, 84, 4)

    # Råttan längs kanten
    rx = [10, 24, 38, 52, 66, 80, 200, 200][ratta]
    if rx < W:
        sprite(d, rx, 88, ["..gg..", "gggggk", ".g.g.."], {"g": 4, "k": 0})
        d.linje(rx - 6, 90, rx, 89, 4)

    d.vinjett(0.45)
    return d


# Morsekod för SOS: kort = 150 ms, lång = 450 ms
MORSE_SOS = []
for tecken in ("...", "---", "..."):
    for t in tecken:
        MORSE_SOS += [(1, 150 if t == "." else 450), (0, 150)]
    MORSE_SOS[-1] = (0, 450)
MORSE_SOS[-1] = (0, 1600)


# Animationer per bild: (namn, nyckel i v, [(värde, millisekunder), ...]).
# Spelet kan låsa en animation på en viss ruta, t.ex. släckt lampa.
# Ett fjärde värde anger att bara de första rutorna loopar; övriga rutor väljs av spelet (animStyr).
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
    "vaning": (takvaning, [
        ("fru", "fru", [(0, 900), (1, 700), (2, 0)], 2),
        ("mops", "mops", [(0, 1000), (1, 1000)], 1),
        ("kristall", "kristall", [(i, 300) for i in range(4)]),
        ("moln", "moln", [(i, 130) for i in range(6)]),
    ]),
    "china": (chinatown, [
        ("regn", "regn", [(i, 100) for i in range(10)]),
        ("sving", "sving", [(i, 450) for i in range(4)]),
        ("neon", "neon", [(0, 600)] + [(n, 180) for n in range(1, 12)] + [(12, 3000), (0, 150), (12, 1500)]),
        ("anga", "anga", [(i, 200) for i in range(4)]),
    ]),
    "restaurang": (golden_dragon, [
        ("eld", "eld", [(i, 110) for i in range(4)]),
        ("karp", "karp", [(i, 450) for i in range(12)]),
        ("katt", "katt", [(0, 500), (1, 500)]),
    ]),
    "pir": (pir9, [
        ("dimma", "dimma", [(i, 400) for i in range(6)]),
        ("fyr", "fyr", [(i, 260) for i in range(8)]),
        ("vagor", "vagor", [(i, 350) for i in range(4)]),
        ("lage", "lage", [(0, 1000), (1, 1000), (2, 1000)], 1),
    ]),
    "lager": (lager13, [
        ("damm", "damm", [(i, 300) for i in range(8)]),
        ("mops", "mops", [(0, 700), (1, 500), (2, 1000), (3, 1000)], 2),
    ]),
    "p_main": (perrong_main, [
        ("zzz", "zzz", [(i, 600) for i in range(4)]),
        ("lampa", "lampa", [(1, 2400), (0, 80), (1, 60), (0, 300), (1, 1500), (0, 120)]),
    ]),
    "p_park": (perrong_park, [
        ("strake", "strake", [(i, 180) for i in range(4)]),
        ("noter", "noter", [(i, 350) for i in range(6)]),
    ]),
    "p_china": (perrong_china, [
        ("folk", "folk", [(i, 260) for i in range(4)]),
        ("sving", "sving", [(i, 450) for i in range(4)]),
    ]),
    "p_pir": (perrong_pir, [
        ("ror", "ror", MORSE_SOS),
        ("dropp", "dropp", [(i, 160 if i < 5 else 400) for i in range(6)]),
        ("ratta", "ratta", [(i, 120) for i in range(6)] + [(6, 4000)]),
    ]),
}


def exportera(namn):
    """Sparar grundbilden som PNG och returnerar animationerna som pixeldiffar."""
    scen, animationer = SCENER[namn]
    bas = scen()
    bas.spara(namn)
    ut = []
    for anim_namn, nyckel, ramar, *rest in animationer:
        slinga = rest[0] if rest else None   # bara de första rutorna loopar, resten väljer spelet
        diffar, tider = [], []
        for varde, ms in ramar:
            a = scen({nyckel: varde}).a
            ys, xs = np.nonzero(a != bas.a)
            # Varje pixel packas i tre byte: position (y * bredd + x, två byte) och färg (en byte).
            buf = bytearray()
            for y, x in zip(ys.tolist(), xs.tolist()):
                pos = y * W + x
                buf += bytes((pos >> 8, pos & 255, int(a[y, x])))
            diffar.append(base64.b64encode(bytes(buf)).decode("ascii"))
            tider.append(ms)
        post = {"namn": anim_namn, "ms": tider, "ramar": diffar}
        if slinga:
            post["slinga"] = slinga
        ut.append(post)
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
