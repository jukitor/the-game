#!/usr/bin/env python3
"""Skapar de nya ljuden till Papegojan som visste för mycket.
Musiken och de flesta miljöljud och effekter lånas från aventyr/mopsen/ljud (ljudmapp i aventyr.js).

Kör:  python3 aventyr/papegojan/verktyg/skapa_ljud.py            (allt)
      python3 aventyr/papegojan/verktyg/skapa_ljud.py effekter   (bara en del: miljo, effekter)
      python3 motor/verktyg/bygg.py papegojan
"""
import random
import sys
from pathlib import Path

MAPP = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(MAPP.parent.parent / "motor" / "verktyg"))
import ljudverktyg   # noqa: E402
from ljudverktyg import *   # noqa: E402,F401,F403
ljudverktyg.UT = MAPP / "ljud"

RND = random.Random(1947)
SLINGLANGD = 24.0


def miljo():
    print("Miljöslingor")
    L = SLINGLANGD + 2.0
    n = int(L * SR)
    # Urmakarens butik: dussintals klockor som tickar i olika takt, ett golvur och dovt rumssus
    tick = np.zeros((n, 2), np.float32)
    for i in range(14):
        takt = RND.choice([0.5, 0.5, 1.0, 0.4, 0.25, 0.75, 0.6])
        f = RND.uniform(1800, 5200)
        pan = RND.uniform(-0.8, 0.8)
        vol = RND.uniform(0.15, 0.45)
        t = RND.uniform(0, takt)
        while t < L - 0.2:
            lagg(tick, panorera(knack(f * (1.0 if int(t / takt) % 2 else 0.85), 18, vol, 0.04), pan), t)
            t += takt
    golvur = np.zeros((n, 2), np.float32)
    t = 0.3
    while t < L - 0.5:
        lagg(golvur, panorera(knack(900, 6, 0.9, 0.12), 0.3), t)
        lagg(golvur, panorera(knack(700, 6, 0.7, 0.12), 0.3), t + 1.0)
        t += 2.0
    rum = filt(stereo_brus(L, 60, 400), "lp", 300) * 0.05
    langder = {"tick": gor_slinga("tick", tick + golvur * 0.6 + rum)}
    return langder


PAPEGOJA = [
    ("Godnatt, Caruso. Godnatt.", 0.6),
    ("Tyst, fågel! Tyst!", 0.5),
    ("Vi ses där klockan slår tretton!", 0.5),
    ("Tre trappor upp! Tre trappor upp!", 0.0),
]


def papegojrost():
    """Papegojan härmar röster: ljus, snabb och lite skrovlig. Returnerar ljud och tider per mening."""
    delar, tider, t = [], [], 0.0
    roster = [("sv+f3", 175, 90), ("sv+m3", 190, 80), ("sv+m3", 185, 85), ("sv+f4", 200, 99)]
    for i, (mening, paus) in enumerate(PAPEGOJA):
        wav = CACHE / f"papegoja_{i}.wav"
        rost, fart, ton = roster[i]
        kor("espeak-ng", "-v", rost, "-s", fart, "-p", ton, "-g", 1, "-w", wav, mening)
        sr, y = wavfile.read(wav)
        y = signal.resample_poly(y.astype(np.float32) / 32768, SR, sr).astype(np.float32)
        aktiv = np.nonzero(np.abs(y) > 0.01)[0]
        y = y[max(0, aktiv[0] - 200):aktiv[-1] + 200]
        # Fågelröst: höj tonläget genom att spela upp lite snabbare och lägg till ett skrovligt surr
        y = signal.resample_poly(y, 4, 5).astype(np.float32)
        tt = np.arange(len(y)) / SR
        y = y * (1 + 0.35 * np.sin(2 * np.pi * 38 * tt))
        y = filt(y, "band", (500, 6000), ordning=2)
        y = np.tanh(y * 2.5) / np.tanh(2.5)
        tider.append([round(t, 3), round(t + len(y) / SR, 3), mening])
        delar += [y, tyst(paus)]
        t += len(y) / SR + paus
    return np.concatenate(delar), tider


def skri(langd=0.45, f0=1400, vol=1.0):
    """Ett papegojskri: en snabbt glidande, skrovlig ton."""
    n = int(langd * SR)
    f = frekvenskurva([(0, f0), (langd * 0.3, f0 * 1.6), (langd, f0 * 0.9)], langd)
    x = oscillator(f, "saw", 12) * hylsa(n, 0.01, langd * 0.8)
    x = filt(x, "band", (800, 5000)) + filt(brus(n), "band", (2000, 6000)) * 0.3 * hylsa(n, 0.01, langd * 0.5)
    return np.tanh(x * 2) * vol


def effekter():
    print("Effekter")
    # Papegojan pratar i sömnen: ett prassel, ett gäsp, rösterna och ett sömnigt skri på slutet
    rost, rosttider = papegojrost()
    x = tyst(1.2 + len(rost) / SR + 1.2)
    lagg(x, filt(brus(int(0.4 * SR)), "band", (1500, 6000)) * hylsa(int(0.4 * SR), 0.05, 0.3) * 0.2, 0.0)
    lagg(x, skri(0.3, 900, 0.3), 0.5)
    lagg(x, rost * 0.8, 1.2)
    lagg(x, skri(0.5, 1300, 0.5), 1.2 + len(rost) / SR + 0.3)
    gor_effekt("papegoja", x, rum=25, efterklang=30, normal=-2)
    texttider = {"papegoja": [[t0 + 1.2, t1 + 1.2, m] for t0, t1, m in rosttider]}

    # Ett vanligt papegojskri
    x = tyst(1.0)
    lagg(x, skri(0.35, 1500), 0.0)
    lagg(x, skri(0.25, 1800, 0.7), 0.4)
    gor_effekt("kvack", x, rum=30, efterklang=35)

    # Fasadklockan slår: djupa klockslag med lång efterklang
    x = tyst(5.0)
    for i in range(3):
        lagg(x, klocka(196, 3.0, vol=0.9), i * 1.2)
    gor_effekt("klockslag", x, rum=100, efterklang=90, normal=-3)

    # Göken i gökuret: ett träslag och två toner, två gånger
    x = tyst(1.8)
    for i in range(2):
        lagg(x, knack(1200, 8, 0.4, 0.05), i * 0.8)
        lagg(x, sinus(740, 0.18) * hylsa(int(0.18 * SR), 0.01, 0.12) * 0.6, i * 0.8 + 0.05)
        lagg(x, sinus(587, 0.28) * hylsa(int(0.28 * SR), 0.01, 0.2) * 0.6, i * 0.8 + 0.27)
    gor_effekt("gok", x, rum=40, efterklang=40)

    # Porttelefonens surr
    n = int(0.9 * SR)
    surr = oscillator(np.full(n, 120.0), "saw", 30) * hylsa(n, 0.01, 1.5)
    surr = filt(surr, "band", (300, 3000))
    gor_effekt("surr", np.tanh(surr * 3) * 0.6, rum=40, efterklang=40)

    # Brandstegen som fälls ner: gnissel och skrammel av järn
    x = tyst(2.0)
    lagg(x, friktion(0.7, 18, 40, (1400, 2300), 8, vol=0.5), 0.0)
    for i, t in enumerate([0.75, 0.83, 0.95, 1.1]):
        lagg(x, plus(knack(820 - i * 60, 14, 0.9 - i * 0.15, 0.4), knack(2300, 20, 0.4, 0.2)), t)
    gor_effekt("stege", x, rum=80, efterklang=60)

    # Ficklampans knapp
    x = tyst(0.3)
    lagg(x, plus(knack(4200, 10, 0.8, 0.03), knack(1600, 6, 0.5, 0.05)), 0.0)
    gor_effekt("klick", x, rum=15, efterklang=20)
    return {"texttider": texttider}


DELAR = {"miljo": miljo, "effekter": effekter}

if __name__ == "__main__":
    kor_delar(DELAR, sys.argv[1:])
