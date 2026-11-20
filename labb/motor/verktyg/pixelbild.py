#!/usr/bin/env python3
"""Spelmotorns bibliotek för pixelbilder i retrostil.

Låg upplösning (192 x 120), en palett med 16 färger och ordnad dithering.
Ett äventyr ritar sina scener med Duk och de här hjälpfunktionerna, och anropar
exportera_alla(scener, mapp) som sparar grundbilderna som PNG och animationerna som
pixeldiffar i <mapp>/bilddata.json. motor/verktyg/bygg.py lägger in datan i spelet.

En scen är en funktion scen(v) som returnerar en Duk. v anger animationernas läge.
scener = { "namn": (scen, [(animation, nyckel_i_v, [(värde, millisekunder), ...], slinga?), ...]) }
"slinga" (valfri) betyder att bara de första rutorna loopar; övriga väljs av spelet.
"""
import base64
from contextlib import contextmanager
import random
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

W, H = 192, 120
UT = Path("bilder")   # sätts av äventyret: pixelbild.UT = <äventyrets bildmapp>

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
        # Klickytor: ytkarta[y, x] = 1 + index i ytnamn, 0 = ingenting
        self.ytnamn = []
        self.ytkarta = np.zeros((H, W), dtype=np.uint8)

    # --- klickytor ---
    def _ytindex(self, namn):
        if namn not in self.ytnamn:
            self.ytnamn.append(namn)
        return self.ytnamn.index(namn) + 1

    @contextmanager
    def yta(self, namn):
        """Allt som ritas inuti blocket blir klickytan namn (ett föremål i äventyret eller "utgang:<riktning>").
        Senare ritat ligger överst, precis som i bilden."""
        fore = self.a.copy()
        yield
        self.ytkarta[self.a != fore] = self._ytindex(namn)

    def markera(self, namn, x0, y0, x1, y1):
        """Lägger till en rektangel som klickyta (för ytor som är svåra att rita fram)."""
        self.ytkarta[max(0, y0):max(0, y1), max(0, x0):max(0, x1)] = self._ytindex(namn)

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
#  SPRITAR (små figurer ritade som textrader)
# ======================================================================
SPRITFARG = {"k": 0, "f": 9, "d": 8, "w": 15, "p": 14, "c": 10, "r": 13, "n": 2, "g": 4, "s": 5, "b": 7}


def sprite(d, x, y, rader, farg=SPRITFARG):
    for ry, rad in enumerate(rader):
        for rx, ch in enumerate(rad):
            if ch != ".":
                d.px(x + rx, y + ry, farg[ch])



def text_stor(d, x, y, s, c, skala):
    """Text med pixeltypsnittet, förstorad."""
    for ch in s:
        for ry, rad in enumerate(TYPSNITT[ch]):
            for rx, bit in enumerate(rad):
                if bit == "1":
                    d.rekt(x + rx * skala, y + ry * skala, x + (rx + 1) * skala, y + (ry + 1) * skala, c)
        x += (len(TYPSNITT[ch][0]) + 1) * skala


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



# ======================================================================
#  EXPORT
# ======================================================================
def ytdata(duk, marginal=2):
    """Klickytorna som run-length-kodad karta. Ytorna växer med några pixlar
    (där inget annat ligger) så att små föremål blir lättare att träffa."""
    k = duk.ytkarta.copy()
    for _ in range(marginal):
        ny = k.copy()
        p = np.pad(k, 1)   # kanter utan omlindning
        for dy, dx in ((0, 1), (0, -1), (1, 0), (-1, 0)):
            flytt = p[1 + dy:1 + dy + k.shape[0], 1 + dx:1 + dx + k.shape[1]]
            ny = np.where((ny == 0) & (flytt > 0), flytt, ny)
        k = ny
    platt, buf, i = k.ravel(), bytearray(), 0
    while i < len(platt):
        v, n = platt[i], 1
        while i + n < len(platt) and platt[i + n] == v and n < 255:
            n += 1
        buf += bytes((int(v), n))
        i += n
    return {"namn": duk.ytnamn, "karta": base64.b64encode(bytes(buf)).decode("ascii")}


def exportera(scener, namn):
    """Sparar grundbilden som PNG. Returnerar animationerna som pixeldiffar och klickytorna."""
    scen, animationer = scener[namn]
    bas = scen()
    bas.spara(namn)
    ut = []
    for anim_namn, nyckel, ramar, *rest in animationer:
        slinga = rest[0] if rest else None
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
    return ut, (ytdata(bas) if bas.ytnamn else None)


def exportera_alla(scener, mapp, palett=None):
    """Ritar alla scener till mapp/ och skriver mapp/bilddata.json."""
    import json
    global UT
    UT = Path(mapp)
    data = {"palett": palett or PALETT, "bredd": W, "hojd": H, "bilder": {}, "ytor": {}}
    for namn in scener:
        data["bilder"][namn], ytor = exportera(scener, namn)
        if ytor:
            data["ytor"][namn] = ytor
        print("Ritade", UT / f"{namn}.png", "med", len(data["bilder"][namn]), "animationer")
    (UT / "bilddata.json").write_text(json.dumps(data, separators=(",", ":")), encoding="utf-8")
    print("Skrev", UT / "bilddata.json", "- kör motor/verktyg/bygg.py för att bygga spelet.")
