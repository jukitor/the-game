#!/usr/bin/env python3
"""Ritar startskärmens bild: en detektiv sedd bakifrån under en gatlykta i regnet.

En målerisk noir-illustration i hög upplösning, byggd i lager med mjuka masker,
ljus, dimma, regn, spegelbilder i våt asfalt, filmkorn och vinjettering.
Scenen ritas i 3200 x 1800 och sparas som en liggande (1920 x 1080) och en
stående bild (1012 x 1800) för mobil.

Kör:  python3 aventyr/mopsen/verktyg/rita_splash.py
"""
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

UT = Path(__file__).resolve().parent.parent / "bilder"
W, H = 3200, 1800
CX = W / 2
RNG = np.random.default_rng(1947)
YY, XX = np.mgrid[0:H, 0:W].astype(np.float32)


# ---------------------------------------------------------------- hjälp
def mask(ritare, blur=0, skala=1):
    """Ritar en mask (0..1) med PIL. ritare(draw, s) där s är skalfaktorn för kantutjämning."""
    s = 2 if skala else 1
    im = Image.new("L", (W * s, H * s), 0)
    ritare(ImageDraw.Draw(im), s)
    im = im.resize((W, H), Image.LANCZOS)
    if blur:
        im = im.filter(ImageFilter.GaussianBlur(blur))
    return np.asarray(im, dtype=np.float32) / 255.0


def suddig(a, r):
    im = Image.fromarray(np.clip(a * 255, 0, 255).astype(np.uint8))
    return np.asarray(im.filter(ImageFilter.GaussianBlur(r)), dtype=np.float32) / 255.0


def lagg_over(bild, m, farg, alfa=1.0):
    m = (m * alfa)[..., None]
    return bild * (1 - m) + np.array(farg, np.float32) * m


def ljus(bild, m, farg, styrka=1.0):
    return bild + m[..., None] * np.array(farg, np.float32) * styrka


def radial(cx, cy, r, form=2.0, sy=1.0):
    d = np.sqrt((XX - cx) ** 2 + ((YY - cy) / sy) ** 2) / r
    return np.exp(-d ** form)


def mjukt_brus(nx, ny, seed):
    rng = np.random.default_rng(seed)
    a = rng.random((ny, nx)).astype(np.float32)
    im = Image.fromarray((a * 255).astype(np.uint8)).resize((W, H), Image.BICUBIC)
    return np.asarray(im, dtype=np.float32) / 255.0


# ---------------------------------------------------------------- scenen
def rita():
    bild = np.zeros((H, W, 3), np.float32)
    horisont = 0.55 * H
    vp = (CX - 0.02 * H, horisont)

    # Himmel
    t = np.clip(YY / horisont, 0, 1)[..., None]
    bild[:] = np.array([0.012, 0.016, 0.03]) * (1 - t) + np.array([0.05, 0.06, 0.085]) * t

    # Avlägsna hus i dimman
    def skyline(d, s):
        x = CX - 0.55 * H
        rng = np.random.default_rng(3)
        while x < CX + 0.55 * H:
            b = rng.uniform(0.04, 0.09) * H
            topp = horisont - rng.uniform(0.08, 0.28) * H
            d.rectangle([x * s, topp * s, (x + b) * s, (horisont + 0.02 * H) * s], fill=255)
            x += b * rng.uniform(0.9, 1.2)
    m = mask(skyline, blur=3)
    mot_horisont = np.clip(1 - (horisont - YY) / (0.3 * H), 0, 1)
    bild = lagg_over(bild, m * (0.55 + 0.45 * mot_horisont), (0.06, 0.068, 0.09), 0.9)
    # Fönster i de avlägsna husen
    rng = np.random.default_rng(4)
    fon = np.zeros((H, W), np.float32)
    for _ in range(140):
        x = rng.uniform(CX - 0.5 * H, CX + 0.5 * H)
        y = rng.uniform(horisont - 0.26 * H, horisont - 0.01 * H)
        fon[int(y):int(y) + 4, int(x):int(x) + 3] = rng.uniform(0.3, 1.0)
    fon *= m
    bild = ljus(bild, suddig(fon, 2) * 2.5 + suddig(fon, 12) * 4, (1.0, 0.7, 0.35), 0.35)

    # Nära husväggar som löper mot gränden i fjärran (perspektiv)
    def fasader(d, s):
        for sida in (-1, 1):
            nara_x = CX + sida * 1.05 * H
            fjarran_x = vp[0] + sida * 0.30 * H
            d.polygon([(nara_x * s, -0.2 * H * s), (fjarran_x * s, (horisont - 0.36 * H) * s),
                       (fjarran_x * s, (horisont + 0.015 * H) * s), (nara_x * s, (0.86 * H) * s),
                       ((nara_x + sida * W) * s, 0.86 * H * s), ((nara_x + sida * W) * s, -0.2 * H * s)], fill=255)
    fas = mask(fasader, blur=2)
    bild = lagg_over(bild, fas, (0.02, 0.022, 0.032), 1.0)
    # Fönster på fasaderna, i perspektiv
    fon = np.zeros((H, W), np.float32)
    for sida in (-1, 1):
        nara_x, fjarran_x = CX + sida * 1.05 * H, vp[0] + sida * 0.30 * H
        for k in range(14):
            u = 1 - 1 / (1 + 0.35 * k)                 # djup
            x = nara_x + (fjarran_x - nara_x) * u
            topp = -0.2 * H + ((horisont - 0.36 * H) + 0.2 * H) * u
            botten = 0.86 * H + ((horisont + 0.015 * H) - 0.86 * H) * u
            bredd = 0.05 * H * (1 - u) + 0.006 * H
            for r in range(6):
                y = topp + (botten - topp) * (0.12 + r * 0.13)
                hojd = (botten - topp) * 0.07
                if rng.random() < 0.28:
                    fon[int(y):int(y + hojd), int(min(x, x + sida * bredd)):int(max(x, x + sida * bredd))] = rng.uniform(0.25, 0.9)
    fon *= fas
    bild = lagg_over(bild, suddig(fon, 2), (0.55, 0.38, 0.2), 0.8)
    bild = ljus(bild, suddig(fon, 18), (1.0, 0.65, 0.3), 0.5)

    # Gatan: våt asfalt
    t = np.clip((YY - horisont) / (H - horisont), 0, 1)[..., None]
    gata = np.array([0.04, 0.045, 0.06]) * (1 - t) + np.array([0.015, 0.017, 0.022]) * t
    bild = np.where((YY > horisont)[..., None], gata, bild).astype(np.float32)
    # Trottoarkanter mot gränden
    def kanter(d, s):
        for sida in (-1, 1):
            d.line([((CX + sida * 1.05 * H) * s, 0.86 * H * s), ((vp[0] + sida * 0.30 * H) * s, (horisont + 0.015 * H) * s)],
                   fill=255, width=int(6 * s))
    bild = ljus(bild, mask(kanter, blur=3), (0.4, 0.45, 0.55), 0.08)

    # Neonskylt på vänster vägg
    nx, ny0, ny1 = CX - 0.36 * H, 0.18 * H, 0.47 * H
    skylt = mask(lambda d, s: d.rectangle([(nx - 0.028 * H) * s, ny0 * s, (nx + 0.028 * H) * s, ny1 * s], fill=255), blur=2)
    bild = lagg_over(bild, skylt, (0.03, 0.01, 0.015), 1.0)
    try:
        font = ImageFont.load_default(size=int(0.042 * H * 2))
    except TypeError:
        font = ImageFont.load_default()

    def bokstaver(d, s):
        for i, ch in enumerate("HOTEL"):
            y = (ny0 + 0.012 * H + i * 0.054 * H) * s
            bb = d.textbbox((0, 0), ch, font=font)
            d.text((nx * s - (bb[2] - bb[0]) / 2, y), ch, fill=255, font=font)
    neon = mask(bokstaver)
    rod = (1.0, 0.16, 0.28)
    bild = lagg_over(bild, neon, (1.0, 0.75, 0.8), 1.0)
    bild = ljus(bild, suddig(neon, 6), rod, 1.4)
    bild = ljus(bild, suddig(neon, 40), rod, 1.6)
    bild = ljus(bild, radial(nx, (ny0 + ny1) / 2, 0.22 * H, 1.6, 1.6), rod, 0.12)

    # Gatlyktan till höger om detektiven
    lx, ly = CX + 0.2 * H, 0.2 * H
    def lykta(d, s):
        d.rectangle([(lx + 0.03 * H) * s, ly * s, (lx + 0.038 * H) * s, 0.9 * H * s], fill=255)          # stolpe
        d.arc([(lx - 0.01 * H) * s, (ly - 0.03 * H) * s, (lx + 0.07 * H) * s, (ly + 0.05 * H) * s], 180, 270, fill=255, width=int(0.007 * H * s))
        d.polygon([((lx - 0.035 * H) * s, (ly + 0.025 * H) * s), ((lx + 0.015 * H) * s, (ly + 0.025 * H) * s),
                   ((lx + 0.005 * H) * s, (ly - 0.005 * H) * s), ((lx - 0.025 * H) * s, (ly - 0.005 * H) * s)], fill=255)
        d.rectangle([(lx + 0.022 * H) * s, 0.86 * H * s, (lx + 0.046 * H) * s, 0.9 * H * s], fill=255)  # fot
    lyktmask = mask(lykta, blur=1)
    bild = lagg_over(bild, lyktmask, (0.01, 0.01, 0.012), 1.0)
    bild = ljus(bild, suddig(np.clip(lyktmask - np.roll(lyktmask, 4, axis=1), 0, 1), 1.5), (1.0, 0.72, 0.38), 0.5)
    glodx, glody = lx - 0.01 * H, ly + 0.03 * H
    amber = (1.0, 0.72, 0.38)
    # Ljuskägla ner mot gatan
    kagla = mask(lambda d, s: d.polygon([((glodx - 0.02 * H) * s, glody * s), ((glodx + 0.02 * H) * s, glody * s),
                                         ((glodx + 0.2 * H) * s, 0.95 * H * s), ((glodx - 0.24 * H) * s, 0.95 * H * s)], fill=255), blur=60)
    avtagande = np.clip(1 - (YY - glody) / (0.95 * H), 0.25, 1)
    dimma_brus = mjukt_brus(24, 14, 7)
    bild = ljus(bild, kagla * avtagande * (0.6 + 0.6 * dimma_brus), amber, 0.16)
    bild = ljus(bild, radial(glodx, glody, 0.32 * H, 1.3), amber, 0.22)
    bild = ljus(bild, radial(glodx, glody, 0.06 * H, 1.6), amber, 0.9)
    bild = ljus(bild, radial(glodx, glody, 0.012 * H, 2), (1, 0.95, 0.85), 3.0)
    # Ljuspöl på gatan
    bild = ljus(bild, radial(glodx - 0.03 * H, 0.9 * H, 0.22 * H, 2, 0.25), amber, 0.35)

    # Spegelbilder i den våta asfalten (långsträckta, darrande)
    def spegling(x, y0, bredd, langd, farg, styrka):
        nonlocal bild
        m = radial(x, y0 + langd / 2, bredd, 2, langd / bredd)
        m *= (YY > horisont) * (0.6 + 0.4 * mjukt_brus(60, 200, int(x)))
        bild = ljus(bild, m, farg, styrka)
    spegling(glodx, 0.62 * H, 0.025 * H, 0.42 * H, amber, 0.55)
    spegling(nx, 0.6 * H, 0.03 * H, 0.38 * H, rod, 0.5)
    spegling(CX + 0.02 * H, horisont + 0.03 * H, 0.08 * H, 0.1 * H, (0.9, 0.65, 0.4), 0.12)

    # Dimma över gatan och gränden
    fog = mjukt_brus(18, 10, 11) * 0.6 + mjukt_brus(40, 22, 12) * 0.4
    hojdfaktor = np.exp(-((YY - horisont) / (0.22 * H)) ** 2)
    bild = ljus(bild, fog * hojdfaktor, (0.35, 0.4, 0.5), 0.16)
    bild = ljus(bild, fog * radial(glodx, glody + 0.15 * H, 0.45 * H, 1.5), amber, 0.12)

    # Detektiven, bakifrån
    fot = 0.93 * H
    hojd = 0.64 * H
    dx = CX - 0.03 * H
    def y(p):  # p = andel av höjden från fötterna
        return fot - p * hojd

    def detektiv(d, s):
        P = lambda pts: [(x * s, yv * s) for x, yv in pts]
        # Ben och skor (rocken täcker dem till mitten av vaden)
        for sida in (-1, 1):
            mitt = dx + sida * 0.026 * H
            d.polygon(P([(mitt - 0.017 * H, y(0.27)), (mitt + 0.017 * H, y(0.27)),
                         (mitt + 0.014 * H, y(0.025)), (mitt - 0.014 * H, y(0.025))]), fill=255)
            d.ellipse(P([(mitt - 0.02 * H, y(0.04)), (mitt + 0.02 * H, y(-0.004))]), fill=255)
        # Rocken: breda axlar, rak rygg och en fåll som svänger ut lite nedanför knäna
        d.polygon(P([(dx - 0.098 * H, y(0.775)), (dx - 0.075 * H, y(0.802)), (dx - 0.03 * H, y(0.818)),
                     (dx + 0.03 * H, y(0.818)), (dx + 0.077 * H, y(0.8)), (dx + 0.1 * H, y(0.772)),
                     (dx + 0.104 * H, y(0.62)), (dx + 0.108 * H, y(0.45)), (dx + 0.122 * H, y(0.235)),
                     (dx + 0.05 * H, y(0.222)), (dx - 0.005 * H, y(0.23)), (dx - 0.06 * H, y(0.22)),
                     (dx - 0.124 * H, y(0.238)), (dx - 0.106 * H, y(0.45)), (dx - 0.1 * H, y(0.62))]), fill=255)
        # Ärmar, med händerna i fickorna
        for sida in (-1, 1):
            d.polygon(P([(dx + sida * 0.092 * H, y(0.78)), (dx + sida * 0.118 * H, y(0.73)), (dx + sida * 0.124 * H, y(0.6)),
                         (dx + sida * 0.114 * H, y(0.5)), (dx + sida * 0.092 * H, y(0.5)), (dx + sida * 0.088 * H, y(0.62))]), fill=255)
        # Uppfälld krage och nacke
        d.polygon(P([(dx - 0.048 * H, y(0.8)), (dx - 0.042 * H, y(0.862)), (dx + 0.042 * H, y(0.862)), (dx + 0.05 * H, y(0.8))]), fill=255)
        d.ellipse(P([(dx - 0.033 * H, y(0.915)), (dx + 0.033 * H, y(0.83))]), fill=255)
        # Hatten: brätte och kulle med intryck
        d.ellipse(P([(dx - 0.078 * H, y(0.905)), (dx + 0.08 * H, y(0.876))]), fill=255)
        d.polygon(P([(dx - 0.046 * H, y(0.89)), (dx - 0.041 * H, y(0.955)), (dx - 0.012 * H, y(0.97)), (dx + 0.004 * H, y(0.962)),
                     (dx + 0.02 * H, y(0.972)), (dx + 0.043 * H, y(0.957)), (dx + 0.049 * H, y(0.89))]), fill=255)

    figur = mask(detektiv, blur=1.2)
    # Skugga och spegling under fötterna
    bild = lagg_over(bild, radial(dx - 0.12 * H, fot + 0.005 * H, 0.2 * H, 2, 0.08), (0, 0, 0), 0.7)
    spegel = np.zeros_like(figur)
    yy0 = int(fot)
    n = min(H - yy0, yy0)
    spegel[yy0:yy0 + n] = figur[yy0 - 1:yy0 - 1 - n:-1] if n > 0 else 0
    bild = lagg_over(bild, suddig(spegel, 10) * 0.45, (0.0, 0.0, 0.0), 1.0)
    bild = lagg_over(bild, figur, (0.008, 0.009, 0.013), 1.0)
    # Kantljus från lyktan (höger) och neon (vänster)
    def kant(forskjut, r):
        im = np.roll(figur, forskjut, axis=1)
        return np.clip(figur - im, 0, 1) * figur
    hogersida = np.clip((XX - (dx + 0.02 * H)) / (0.08 * H), 0, 1)        # bara sidan mot lyktan
    bild = ljus(bild, suddig(kant(-4, 2), 1.2) * hogersida, amber, 1.6)
    bild = ljus(bild, suddig(kant(-14, 2), 6) * hogersida, amber, 0.35)
    vanstersida = np.clip(((dx - 0.02 * H) - XX) / (0.08 * H), 0, 1)
    bild = ljus(bild, suddig(kant(3, 2), 1.2) * vanstersida, rod, 0.25)
    # Tygets veck och lite ljus på ryggen från lyktan
    veck = mjukt_brus(260, 18, 31) - 0.5
    rygg = figur * np.clip((XX - dx) / (0.12 * H), 0, 1) * (YY < y(0.23)) * (YY > y(0.8))
    bild = ljus(bild, rygg * (0.5 + veck), amber, 0.035)
    bild = ljus(bild, figur * radial(dx + 0.06 * H, y(0.7), 0.12 * H, 1.5), amber, 0.03)
    # Hattbandet skymtar i kantljuset
    band = mask(lambda d, s: d.rectangle([(dx - 0.045 * H) * s, y(0.905) * s, (dx + 0.048 * H) * s, y(0.893) * s], fill=255), blur=1)
    bild = ljus(bild, band * figur * radial(dx + 0.05 * H, y(0.9), 0.05 * H, 1), amber, 0.25)

    # Regn: tunna strimmor, ljusare där lyktan lyser
    regn = Image.new("L", (W, H), 0)
    d = ImageDraw.Draw(regn)
    rng = np.random.default_rng(21)
    for _ in range(9000):
        x, yv = rng.uniform(0, W), rng.uniform(-0.05 * H, H)
        langd = rng.uniform(0.015, 0.05) * H
        d.line([(x, yv), (x - langd * 0.18, yv + langd)], fill=int(rng.uniform(40, 140)), width=1 if rng.random() < 0.8 else 2)
    regn = np.asarray(regn.filter(ImageFilter.GaussianBlur(0.8)), dtype=np.float32) / 255.0
    belysning = 0.15 + 1.8 * radial(glodx, glody + 0.12 * H, 0.35 * H, 1.4) + 0.6 * radial(nx, 0.35 * H, 0.25 * H, 1.5)
    bild = ljus(bild, regn * belysning, (0.75, 0.75, 0.8), 0.35)
    bild = ljus(bild, regn * radial(glodx, glody + 0.12 * H, 0.35 * H, 1.4), amber, 0.3)
    # Små stänk på gatan
    stank = np.zeros((H, W), np.float32)
    for _ in range(1500):
        x, yv = int(rng.uniform(0, W)), int(rng.uniform(horisont + 0.02 * H, H - 2))
        stank[yv, x:x + 2] = rng.uniform(0.3, 1)
    stank = suddig(stank, 1.2) * (0.2 + 2 * radial(glodx, 0.9 * H, 0.3 * H, 1.5, 0.4))
    bild = ljus(bild, stank, amber, 0.8)

    # Bloom: ljusa partier blöder ut
    ljust = np.clip(bild.max(axis=2) - 0.6, 0, None)
    for r, k in ((20, 0.35), (60, 0.25)):
        b = np.stack([suddig(np.clip(bild[..., c] * (ljust > 0), 0, 1), r) for c in range(3)], axis=2)
        bild = bild + b * k

    # Färgsättning: blågröna skuggor, varma högdagrar, filmisk tonkurva
    lum = bild.mean(axis=2, keepdims=True)
    bild = bild + (1 - np.clip(lum * 4, 0, 1)) * np.array([-0.004, 0.004, 0.014])
    bild = 1 - np.exp(-bild * 1.35)
    # Vinjett
    v = np.sqrt(((XX - CX) / (0.62 * W)) ** 2 + ((YY - 0.52 * H) / (0.7 * H)) ** 2)
    bild *= np.clip(1.15 - v ** 2 * 0.7, 0.25, 1)[..., None]
    # Filmkorn
    korn = RNG.normal(0, 0.022, (H, W, 1)).astype(np.float32)
    bild = bild + korn * (0.6 + 0.4 * (1 - lum))
    return np.clip(bild, 0, 1)


def spara(bild):
    UT.mkdir(exist_ok=True)
    im = Image.fromarray((bild * 255).astype(np.uint8))
    im.resize((1920, 1080), Image.LANCZOS).save(UT / "splash.jpg", quality=84, optimize=True, progressive=True)
    bredd = int(H * 9 / 16)
    x0 = int(CX - 0.03 * H - bredd / 2 + 0.04 * H)
    im.crop((x0, 0, x0 + bredd, H)).save(UT / "splash_staende.jpg", quality=84, optimize=True, progressive=True)
    for n in ("splash.jpg", "splash_staende.jpg"):
        print("Ritade", UT / n, (UT / n).stat().st_size // 1024, "kB")


if __name__ == "__main__":
    spara(rita())
