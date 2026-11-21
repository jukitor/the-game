#!/usr/bin/env python3
"""Skapar de nya ljuden till Borgmästarens långkalsonger. Övriga ljud lånas från
aventyr/papegojan/ljud och aventyr/mopsen/ljud (ljudmapp i aventyr.js).

Kör:  python3 aventyr/kalsongerna/verktyg/skapa_ljud.py
      python3 motor/verktyg/bygg.py kalsongerna
"""
import sys
from pathlib import Path

MAPP = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(MAPP.parent.parent / "motor" / "verktyg"))
import ljudverktyg   # noqa: E402
from ljudverktyg import *   # noqa: E402,F401,F403
ljudverktyg.UT = MAPP / "ljud"

SLINGLANGD = 24.0


def miljo():
    print("Miljöslingor")
    # Karusellorgel: en enkel vals i dur med ett mekaniskt, lite falskt orgelljud. Exakt fyra varv
    # av en åtta takters melodi, så att slingan går jämnt ut.
    takt = 60 / 168 * 3                  # vals, 168 slag i minuten
    melodi = [(76, 1), (79, 1), (84, 1), (83, 2), (79, 1), (81, 1), (79, 1), (76, 1), (74, 2), (71, 1),
              (72, 1), (76, 1), (79, 1), (77, 2), (74, 1), (76, 1), (74, 1), (71, 1), (72, 3)]
    ackord = [(48, [64, 67]), (43, [62, 67]), (48, [64, 67]), (43, [62, 65]),
              (45, [64, 69]), (43, [62, 67]), (41, [65, 69]), (48, [64, 67])]
    slag = 60 / 168
    varv = 8 * takt
    antal = 4
    L = varv * antal
    n = int((L + 2) * SR)
    x = np.zeros(n, np.float32)

    def ton(midi, sek, vol):
        f = 440 * 2 ** ((midi - 69) / 12)
        t = np.arange(int(sek * SR)) / SR
        vib = 1 + 0.004 * np.sin(2 * np.pi * 5.5 * t)
        s = sum(np.sin(2 * np.pi * f * k * np.cumsum(vib) / SR) / k for k in (1, 2, 3, 4))
        return (s * hylsa(len(t), 0.01, sek * 0.9) * vol).astype(np.float32)

    for v in range(antal):
        t0 = v * varv
        t = t0
        for midi, langd in melodi:
            lagg(x, ton(midi, langd * slag * 0.95, 0.22), t)
            t += langd * slag
        for i, (bas, topp) in enumerate(ackord):
            tb = t0 + i * takt
            lagg(x, ton(bas, slag * 0.9, 0.3), tb)
            for k in (1, 2):
                for m in topp:
                    lagg(x, ton(m, slag * 0.6, 0.08), tb + k * slag)
            lagg(x, knack(2600, 6, 0.15, 0.03), tb)          # orgelns trumma
    x = filt(x, "band", (120, 6000))
    st = np.stack([x, x * 0.92], axis=1)
    p = spara_wav("karusell_r", st[: int(L * SR) + int(1.5 * SR)] / max(1e-6, np.abs(st).max()) * 0.8)
    p = klang(p, CACHE / "karusell_k.wav", rum=70, efterklang=50)
    y = las_wav(p)
    y = slinga_ur(np.concatenate([y, y]), int(L * SR)) if len(y) >= 2 * int(L * SR) else y[: int(L * SR)]
    till_mp3(spara_wav("karusell_s", y / max(1e-6, np.abs(y).max()) * 0.8), "karusell", kbps=112, normal=-3)
    return {"karusell": int(L * SR)}


def effekter():
    print("Effekter")
    # Gammal telefonsignal: dubbelringning med klockor
    x = tyst(3.2)
    for start in (0.0, 0.5):
        n = int(0.38 * SR)
        t = np.arange(n) / SR
        hammare = (np.sign(np.sin(2 * np.pi * 20 * t)) > 0).astype(np.float32)
        klang_ = klocka(1100, 0.38, vol=0.6) + klocka(1350, 0.38, vol=0.5)
        lagg(x, klang_[:n] * (0.6 + 0.4 * hammare), start)
    gor_effekt("telefon", x, rum=25, efterklang=30)

    # Spökstön: ett lågt, svajande uuuh med brus
    sek = 2.4
    n = int(sek * SR)
    f = frekvenskurva([(0, 180), (0.8, 260), (1.6, 200), (2.4, 150)], sek)
    s = oscillator(f, "sin", 3) * hylsa(n, 0.4, 1.6)
    s += filt(brus(n), "band", (300, 1200)) * 0.15 * hylsa(n, 0.3, 1.8)
    gor_effekt("spoke", s * 0.7, rum=100, efterklang=90, normal=-4)

    # Kommissariens hicka: ett kort, högt "hick"
    n = int(0.18 * SR)
    f = frekvenskurva([(0, 700), (0.05, 1100), (0.18, 500)], 0.18)
    h = oscillator(f, "saw", 8) * hylsa(n, 0.005, 0.12)
    h = filt(h, "band", (400, 3500)) + filt(brus(n), "band", (1500, 5000)) * 0.2 * hylsa(n, 0.002, 0.04)
    gor_effekt("hicka", np.tanh(h * 2) * 0.7, rum=25, efterklang=30)
    return {}


DELAR = {"miljo": miljo, "effekter": effekter}

if __name__ == "__main__":
    kor_delar(DELAR, sys.argv[1:])
