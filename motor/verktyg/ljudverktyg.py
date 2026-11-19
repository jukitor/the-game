#!/usr/bin/env python3
"""Spelmotorns bibliotek för ljud: musik, miljöslingor och effekter som ljudfiler.

Musik komponeras som MIDI (klassen Lat) och renderas med samplade instrument från
ljudbanken GeneralUser GS i FluidSynth. Effekter och miljöljud byggs med
signalbehandling (NumPy/SciPy) och får rumsklang med SoX.

Ett äventyr sätter ljudverktyg.UT till sin ljudmapp och använder funktionerna här.
skriv_ljudlista() sparar slingornas exakta längd (ljud/slingor.json) och repliktider
(ljud/texttider.json); motor/verktyg/bygg.py lägger in dem i spelet.

Kräver:  fluidsynth, sox, espeak-ng, ffmpeg (apt)  och  mido, numpy, scipy (pip)
"""
import random
import subprocess
import sys
import urllib.request
from pathlib import Path

import mido
import numpy as np
from scipy import signal
from scipy.io import wavfile

ROT = Path(__file__).resolve().parent.parent.parent
UT = Path("ljud")            # sätts av äventyret: ljudverktyg.UT = <äventyrets ljudmapp>
CACHE = ROT / ".ljudcache"   # delad mellanlagring (ljudbanken, wav-filer); ingår inte i git
SF2 = CACHE / "GeneralUser-GS.sf2"
SF2_URL = "https://raw.githubusercontent.com/mrbumpy409/GeneralUser-GS/main/GeneralUser-GS.sf2"
SR = 44100


# ======================================================================
#  Hjälpfunktioner
# ======================================================================
def kor(*cmd):
    subprocess.run([str(c) for c in cmd], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def hamta_ljudbank():
    if not SF2.exists():
        CACHE.mkdir(exist_ok=True)
        print("Hämtar GeneralUser GS ...")
        urllib.request.urlretrieve(SF2_URL, SF2)


def spara_wav(namn, x):
    """x: (n,) eller (n, 2) float i [-1, 1]."""
    CACHE.mkdir(exist_ok=True)
    if x.ndim == 1:
        x = np.stack([x, x], axis=1)
    p = CACHE / f"{namn}.wav"
    wavfile.write(p, SR, (np.clip(x, -1, 1) * 32767).astype(np.int16))
    return p


def las_wav(p):
    sr, x = wavfile.read(p)
    x = x.astype(np.float32) / 32768.0
    if x.ndim == 1:
        x = np.stack([x, x], axis=1)
    return x


def till_mp3(wav, namn, kbps=128, normal=-1.0):
    """Normaliserar och kodar till mp3 i ljud/."""
    UT.mkdir(exist_ok=True)
    norm = CACHE / f"{namn}_norm.wav"
    kor("sox", wav, norm, "gain", "-n", normal)
    ut = UT / f"{namn}.mp3"
    kor("ffmpeg", "-y", "-loglevel", "error", "-i", norm, "-codec:a", "libmp3lame", "-b:a", f"{kbps}k", ut)
    print(f"  {ut}  ({ut.stat().st_size // 1024} kB)")
    return ut


def klang(wav, ut, rum=50, efterklang=50, torr=False, hp=None, lp=None):
    """Lägger rumsklang med SoX (stereo)."""
    effekter = []
    if hp:
        effekter += ["highpass", hp]
    if lp:
        effekter += ["lowpass", lp]
    effekter += ["reverb"] + (["-w"] if torr else []) + [efterklang, 50, rum, 100, 0, 0]
    kor("sox", wav, ut, *effekter)
    return ut


def brus(n, rnd=None):
    rnd = rnd or np.random.default_rng(1)
    return rnd.standard_normal(n).astype(np.float32)


def rosa(n, rnd=None):
    """Rosa brus (1/f) via filtrering i frekvensplanet."""
    x = np.fft.rfft(brus(n, rnd))
    f = np.arange(len(x)); f[0] = 1
    y = np.fft.irfft(x / np.sqrt(f), n)
    return (y / np.max(np.abs(y))).astype(np.float32)


def filt(x, typ, f, q=0.707, ordning=2):
    if typ == "band":
        lo, hi = f
        sos = signal.butter(ordning, [lo, hi], btype="bandpass", fs=SR, output="sos")
    else:
        sos = signal.butter(ordning, f, btype={"lp": "lowpass", "hp": "highpass"}[typ], fs=SR, output="sos")
    return signal.sosfilt(sos, x, axis=0).astype(np.float32)


def resonans(x, f, q):
    """Smal resonans (för metall, trä och liknande)."""
    b, a = signal.iirpeak(f, q, fs=SR)
    return signal.lfilter(b, a, x, axis=0).astype(np.float32)


def hylsa(n, att, slapp, sustain=1.0):
    """Amplitudkurva: attack i sekunder, exponentiell avklingning."""
    t = np.arange(n) / SR
    e = np.minimum(1, t / max(att, 1e-4))
    return (e * np.exp(-np.maximum(0, t - att) / max(slapp, 1e-4)) * sustain).astype(np.float32)


def tyst(sek):
    return np.zeros(int(sek * SR), dtype=np.float32)


def lagg(dst, src, vid, gain=1.0):
    i = int(vid * SR)
    n = min(len(src), len(dst) - i)
    if n > 0:
        dst[i:i + n] += src[:n] * gain
    return dst


def panorera(x, pan):
    """pan -1 (vänster) .. 1 (höger)"""
    v = np.cos((pan + 1) * np.pi / 4)
    h = np.sin((pan + 1) * np.pi / 4)
    return np.stack([x * v, x * h], axis=1)


def slinga_ur(x, n, overlapp=0.08):
    """Klipper ut andra varvet x[n:2n] ur en rendering med två identiska varv.
    Slutet tonas över till motsvarande ställe i första varvet, så att slingan blir helt sömlös."""
    k = int(overlapp * SR)
    ut = x[n:2 * n].copy()
    if len(ut) < n:
        ut = np.concatenate([ut, np.zeros((n - len(ut),) + ut.shape[1:], np.float32)])
    t = np.linspace(0, 1, k)[:, None] if x.ndim == 2 else np.linspace(0, 1, k)
    ut[-k:] = ut[-k:] * (1 - t) + x[n - k:n] * t
    return ut


def sommig_slinga(x, overlapp):
    """Gör en sömlös slinga genom att tona över slutet i början."""
    n = int(overlapp * SR)
    huvud, svans = x[:-n].copy(), x[-n:]
    t = np.linspace(0, 1, n)[:, None] if x.ndim == 2 else np.linspace(0, 1, n)
    huvud[:n] = huvud[:n] * np.sqrt(t) + svans * np.sqrt(1 - t)
    return huvud


# ======================================================================
#  MIDI och FluidSynth
# ======================================================================
class Lat:
    """Samlar noter och styrmeddelanden i sekunder och skriver en MIDI-fil."""

    def __init__(self, tempo):
        self.tempo = tempo
        self.handelser = []   # (sekund, ordning, meddelande)

    def sek(self, slag):
        return slag * 60.0 / self.tempo

    def program(self, kanal, prog, bank=0):
        self.handelser.append((0, 0, mido.Message("control_change", channel=kanal, control=0, value=bank)))
        self.handelser.append((0, 1, mido.Message("program_change", channel=kanal, program=prog)))

    def cc(self, kanal, kontroll, varde, slag=0):
        self.handelser.append((max(0.0, self.sek(slag)), 2, mido.Message("control_change", channel=kanal, control=kontroll, value=int(max(0, min(127, varde))))))

    def not_(self, kanal, ton, slag, langd, styrka, jitter=0.012):
        t0 = max(0, self.sek(slag) + random.uniform(-jitter, jitter))
        t1 = t0 + self.sek(langd) * 0.98
        styrka = int(max(1, min(127, styrka + random.randint(-6, 6))))
        self.handelser.append((t0, 3, mido.Message("note_on", channel=kanal, note=ton, velocity=styrka)))
        self.handelser.append((t1, 1, mido.Message("note_off", channel=kanal, note=ton, velocity=0)))

    def svall(self, kanal, slag, langd, fran=70, till=110, tillbaka=80):
        """Uttryck (CC11) som sväller under en lång ton, och vibrato (CC1) som kommer in."""
        steg = 12
        for i in range(steg + 1):
            f = i / steg
            v = fran + (till - fran) * min(1, f * 1.6) - (till - tillbaka) * max(0, f - 0.7) / 0.3
            self.cc(kanal, 11, v, slag + langd * f)
            self.cc(kanal, 1, min(70, f * 90) if langd >= 1.5 else 0, slag + langd * f)

    def spara(self, p):
        mid = mido.MidiFile(ticks_per_beat=960)
        spar = mido.MidiTrack()
        mid.tracks.append(spar)
        spar.append(mido.MetaMessage("set_tempo", tempo=1_000_000, time=0))   # 60 bpm: 1 slag = 1 s
        senast = 0
        for t, _, m in sorted(self.handelser, key=lambda h: (h[0], h[1])):
            tick = int(round(t * 960))
            spar.append(m.copy(time=tick - senast))
            senast = tick
        mid.save(p)


def rendera(midi, wav, gain=0.5, rumstorlek=0.75, klangniva=0.55):
    hamta_ljudbank()
    kor("fluidsynth", "-ni", "-q", "-g", gain, "-r", SR,
        "-o", f"synth.reverb.room-size={rumstorlek}", "-o", f"synth.reverb.level={klangniva}",
        "-o", "synth.reverb.width=1.0", "-o", "synth.reverb.damp=0.35",
        "-o", "synth.chorus.active=0",
        "-F", wav, SF2, midi)
    return wav


# ======================================================================
#  SYNTES-BYGGSTENAR FÖR EFFEKTER
# ======================================================================
RND = np.random.default_rng(1947)


def sinus(f0, sek, f1=None, fas=0.0):
    n = int(sek * SR)
    f = np.full(n, f0, np.float64) if f1 is None else np.geomspace(f0, f1, n)
    return np.sin(fas + 2 * np.pi * np.cumsum(f) / SR).astype(np.float32)


def frekvenskurva(punkter, sek):
    """Linjär frekvenskurva genom punkter [(tid, hz), ...]."""
    n = int(sek * SR)
    t = np.arange(n) / SR
    tt, ff = zip(*punkter)
    return np.interp(t, tt, ff)


def oscillator(f, form="sin", overtoner=8):
    fas = 2 * np.pi * np.cumsum(f) / SR
    if form == "sin":
        return np.sin(fas).astype(np.float32)
    ut = np.zeros_like(fas)
    for k in range(1, overtoner + 1):
        ut += np.sin(k * fas) / k
    return (ut / 1.5).astype(np.float32)


def klocka(f0, sek, delar=((1, 1, 1), (2.76, 0.5, 0.6), (5.4, 0.25, 0.35), (8.93, 0.12, 0.2)), vol=1.0):
    """Klockljud av ickeharmoniska deltoner: (förhållande, styrka, relativ avklingning)."""
    n = int(sek * SR)
    ut = np.zeros(n, np.float32)
    for (r, a, d) in delar:
        ut += a * sinus(f0 * r, sek) * hylsa(n, 0.002, sek * 0.35 * d)
    return ut * vol


def plus(*delar):
    """Summerar signaler av olika längd."""
    n = max(len(d) for d in delar)
    ut = np.zeros((n,) + delar[0].shape[1:], np.float32)
    for d in delar:
        ut[:len(d)] += d
    return ut


def knack(f, q, vol=1.0, sek=0.15, brusighet=1.0):
    """Ett kort slag mot något: impuls genom en resonans plus lite brus."""
    n = int(sek * SR)
    x = np.zeros(n, np.float32)
    x[0] = 1.0
    x += brus(n) * hylsa(n, 0.0005, 0.004) * 0.3 * brusighet
    return resonans(x, f, q) * vol * 8


def friktion(sek, takt_fran, takt_till, f_res, q=6, jitter=0.25, vol=1.0):
    """Stick-slip-friktion (knarr, gnissel): oregelbundna impulser genom resonanser."""
    n = int(sek * SR)
    x = np.zeros(n, np.float32)
    t = 0.0
    while t < sek:
        f = takt_fran + (takt_till - takt_fran) * t / sek
        i = int(t * SR)
        if i < n:
            x[i] = RND.uniform(0.5, 1.0)
        t += (1 / f) * RND.uniform(1 - jitter, 1 + jitter)
    ut = sum(resonans(x, fr, q) for fr in f_res)
    return ut * vol


def kornregn(sek, tathet, f_lo, f_hi, vol=1.0, rnd=None, stereo=True):
    """Regn av många små droppar: korta brusstötar genom slumpade resonanser."""
    rnd = rnd or np.random.default_rng(5)
    n = int(sek * SR)
    ut = np.zeros((n, 2), np.float32)
    antal = int(sek * tathet)
    mall = brus(int(0.012 * SR), rnd) * hylsa(int(0.012 * SR), 0.0003, 0.0025)
    for _ in range(antal):
        i = rnd.integers(0, n - len(mall))
        f = np.exp(rnd.uniform(np.log(f_lo), np.log(f_hi)))
        d = resonans(mall, f, rnd.uniform(2, 8)) * rnd.uniform(0.2, 1.0) ** 2
        pan = rnd.uniform(-1, 1) if stereo else 0
        ut[i:i + len(d)] += panorera(d, pan)
    return ut * vol


def stereo_brus(sek, lo, hi, rnd=None):
    rnd = rnd or np.random.default_rng(9)
    n = int(sek * SR)
    v = filt(rosa(n, rnd), "band", (lo, hi))
    h = filt(rosa(n, np.random.default_rng(rnd.integers(1e9))), "band", (lo, hi))
    return np.stack([v, h], axis=1)


def lfo(sek, hz, djup, bas=1.0, fas=0.0):
    t = np.arange(int(sek * SR)) / SR
    return (bas - djup + djup * (0.5 + 0.5 * np.sin(2 * np.pi * hz * t + fas))).astype(np.float32)


def mono(x):
    return x.mean(axis=1) if x.ndim == 2 else x


def gor_effekt(namn, x, rum=30, efterklang=40, kbps=128, normal=-3, hp=None):
    """Sparar en effekt med rumsklang som mp3."""
    if x.ndim == 1:
        x = np.stack([x, x], axis=1)
    x = np.concatenate([x, np.zeros((int(1.2 * SR), 2), np.float32)])   # plats för efterklang
    p = spara_wav(f"e_{namn}", x / max(1e-6, np.abs(x).max()) * 0.8)
    if rum:
        p = klang(p, CACHE / f"e_{namn}_k.wav", rum=rum, efterklang=efterklang, hp=hp)
    # Klipp bort tystnad i slutet
    t = CACHE / f"e_{namn}_t.wav"
    kor("sox", p, t, "reverse", "silence", "1", "0.01", "-60d", "reverse")
    return till_mp3(t, namn, kbps=kbps, normal=normal)


def gor_slinga(namn, x, overlapp=2.0, kbps=112, normal=-3):
    """Sparar en sömlös miljöslinga (stereo) som mp3. Returnerar antal samplingar."""
    x = sommig_slinga(x, overlapp)
    p = spara_wav(f"s_{namn}", x / max(1e-6, np.abs(x).max()) * 0.8)
    till_mp3(p, namn, kbps=kbps, normal=normal)
    return len(x)



# ======================================================================
#  Ljudlista till spelet
# ======================================================================
def skriv_ljudlista(nya):
    """Sparar slingornas exakta längd (i samplingar) i ljud/slingor.json och repliktider
    i ljud/texttider.json. Spelet behöver längderna för att loopa mp3-filerna utan glapp,
    och texttiderna för att visa orden i takt med rösten."""
    import json
    nya = dict(nya)
    texttider_nya = nya.pop("texttider", {})
    lista_p, text_p = UT / "slingor.json", UT / "texttider.json"
    langder = json.loads(lista_p.read_text()) if lista_p.exists() else {}
    texttider = json.loads(text_p.read_text()) if text_p.exists() else {}
    langder.update(nya)
    texttider.update(texttider_nya)
    lista_p.write_text(json.dumps(langder, indent=1, sort_keys=True) + "\n")
    text_p.write_text(json.dumps(texttider, indent=1, ensure_ascii=False) + "\n")


def kor_delar(delar, valda):
    """Kör valda delar av ett äventyrs ljudskript och sparar ljudlistan."""
    langder = {}
    for namn in valda or list(delar):
        res = delar[namn]()
        if isinstance(res, dict):
            langder.update(res)
    skriv_ljudlista(langder)
    print("Klart. Kör motor/verktyg/bygg.py för att bygga spelet.")
