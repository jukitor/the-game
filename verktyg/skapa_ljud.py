#!/usr/bin/env python3
"""Skapar spelets musik, miljöljud och ljudeffekter som ljudfiler i ljud/.

Musiken och de musikaliska effekterna komponeras här som MIDI och renderas med
riktiga samplade instrument (ljudbanken GeneralUser GS) i FluidSynth.
Miljöljud och övriga effekter byggs med signalbehandling i NumPy/SciPy och får
rumsklang med SoX. Telefonsvararens röst läses in av espeak-ng och filtreras
så att den låter som en gammal högtalare.

Kräver:  fluidsynth, sox, espeak-ng, ffmpeg (apt)  och  mido, numpy, scipy (pip)
Kör:     python3 verktyg/skapa_ljud.py            (allt)
         python3 verktyg/skapa_ljud.py musik      (bara en del)
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

ROT = Path(__file__).resolve().parent.parent
UT = ROT / "ljud"
CACHE = ROT / ".ljudcache"
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
    print(f"  {ut.relative_to(ROT)}  ({ut.stat().st_size // 1024} kB)")
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
#  MUSIK: lugn deckarballad i c-moll
# ======================================================================
PIANO, BAS, SAX, TRUMPET, TRUMMOR = 0, 1, 2, 3, 9

# Ackord: (basnot, pianoröstning)
ACK = {
    "Cm":    (36, [51, 55, 60, 62]), "CmM7": (36, [51, 55, 59, 62]), "Cm7": (36, [51, 55, 58, 62]),
    "Cm6":   (36, [51, 55, 57, 62]), "Fm":   (41, [56, 60, 65, 67]), "FmM7": (41, [56, 60, 64, 67]),
    "Fm7":   (41, [56, 60, 63, 67]), "Fm6":  (41, [56, 60, 62, 67]), "Dm7b5": (38, [53, 56, 60, 65]),
    "G7b9":  (43, [53, 56, 59, 63]), "Ab7":  (44, [54, 60, 63, 65]), "Ebmaj7": (39, [55, 58, 62, 67]),
    "Abmaj7": (44, [55, 60, 63, 67]), "G7alt": (43, [53, 59, 63, 68]), "Cmadd9": (36, [51, 55, 62, 67]),
}
# Formen: intro 4, A 16, B 16, avslutning 4 takter. Varje takt: lista med (ackord, slag)
INTRO = [[("Cm", 4)], [("CmM7", 4)], [("Cm7", 4)], [("G7b9", 4)]]
A = [[("Cm", 4)], [("CmM7", 4)], [("Cm7", 4)], [("Cm6", 4)],
     [("Fm", 4)], [("FmM7", 4)], [("Fm7", 4)], [("Fm6", 4)],
     [("Dm7b5", 4)], [("G7b9", 4)], [("Cm7", 2), ("Ab7", 2)], [("Dm7b5", 2), ("G7b9", 2)],
     [("Ebmaj7", 4)], [("Abmaj7", 4)], [("Dm7b5", 4)], [("G7alt", 4)]]
OUTRO = [[("Dm7b5", 4)], [("G7b9", 4)], [("Cmadd9", 4)], [("G7alt", 4)]]
FORM = INTRO + A + A + OUTRO

# Melodin för tenorsaxen över A-delen: (takt 0-15, slag 0-3.5, ton, längd i slag)
MELODI = [
    (0, 1, 55, 0.5), (0, 1.5, 60, 0.5), (0, 2, 63, 2),
    (1, 0, 62, 3), (1, 3, 60, 0.5), (1, 3.5, 59, 0.5),
    (2, 0, 58, 2), (2, 2, 55, 1.5), (2, 3.5, 56, 0.5),
    (3, 0, 57, 3.5),
    (4, 1, 60, 0.5), (4, 1.5, 65, 0.5), (4, 2, 68, 2),
    (5, 0, 67, 3), (5, 3.5, 65, 0.5),
    (6, 0, 63, 2), (6, 2, 62, 1), (6, 3, 60, 1),
    (7, 0, 62, 3.5),
    (8, 0, 68, 1.5), (8, 1.5, 67, 0.5), (8, 2, 65, 1), (8, 3, 63, 1),
    (9, 0, 62, 1.5), (9, 1.5, 63, 0.5), (9, 2, 59, 2),
    (10, 0, 60, 2), (10, 2, 63, 0.5), (10, 2.5, 67, 0.5), (10, 3, 66, 1),
    (11, 0, 65, 1.5), (11, 1.5, 63, 0.5), (11, 2, 62, 1), (11, 3, 59, 1),
    (12, 0, 67, 1.5), (12, 1.5, 70, 0.5), (12, 2, 74, 2),
    (13, 0, 72, 2), (13, 2, 67, 1), (13, 3, 63, 1),
    (14, 0, 65, 1.5), (14, 1.5, 68, 0.5), (14, 2, 65, 0.5), (14, 2.5, 62, 0.5), (14, 3, 56, 1),
    (15, 0, 59, 2.5), (15, 2.5, 62, 0.5), (15, 3, 65, 1),
]
# Andra varvet: den dämpade trumpeten tar en variation, en oktav upp och lite efter takten
MELODI2 = [(t, s + (0.5 if s < 3.5 and l >= 1 else 0), n + 12, max(0.5, l - (0.5 if s < 3.5 and l >= 1 else 0)))
           for (t, s, n, l) in MELODI if t not in (3, 7)] + [
    (3, 0, 69, 1), (3, 1, 67, 1), (3, 2, 63, 2), (7, 0, 74, 1), (7, 1, 72, 1), (7, 2, 71, 2)]
AVSLUT = [(0, 1, 63, 1), (0, 2, 62, 1), (0, 3, 60, 1), (1, 0, 59, 3), (2, 0, 60, 3.5)]


SOLISTER = False


def swing(slag, grad=0.08):
    hel = int(slag)
    return hel + 0.5 + grad if abs(slag - hel - 0.5) < 1e-6 else slag


def komponera_jazz(varv=2):
    random.seed(1947)
    lat = Lat(tempo=56)
    lat.program(PIANO, 0)
    lat.program(BAS, 32)
    lat.program(SAX, 66)
    lat.program(TRUMPET, 59)
    lat.program(TRUMMOR, 40)  # kanal 10 är trumkanalen; program 40 = Brush Kit
    for k, (vol, pan, klang) in {PIANO: (104, 52, 70), BAS: (84, 60, 40), SAX: (124, 70, 85),
                                 TRUMPET: (122, 44, 90), TRUMMOR: (78, 64, 55)}.items():
        lat.cc(k, 7, vol); lat.cc(k, 10, pan); lat.cc(k, 91, klang); lat.cc(k, 93, 0)
    takter_per_varv = len(FORM)
    for v in range(varv):
        start = v * takter_per_varv * 4
        for i, takt in enumerate(FORM):
            t0 = start + i * 4
            del_ = "intro" if i < 4 else "A1" if i < 20 else "A2" if i < 36 else "outro"
            pos = 0
            for (namn, langd) in takt:
                rot, rost = ACK[namn]
                s = t0 + pos
                # Piano: mjukt ackord på ettan, ibland en föregripande upprepning
                lat.cc(PIANO, 64, 0, s - 0.02); lat.cc(PIANO, 64, 100, s + 0.03)
                for j, ton in enumerate(rost):
                    lat.not_(PIANO, ton, s + j * 0.03, langd, 56 if del_ != "intro" else 58)
                if langd == 4 and random.random() < 0.45:
                    for ton in rost[1:]:
                        lat.not_(PIANO, ton + 12, swing(s + 2.5), 1.4, 32)
                # Bas: halvnoter i två-känsla, gående fjärdedelar i andra A-delen
                if del_ == "A2" and langd == 4:
                    kvint = rot + 7
                    nasta = ACK[FORM[(i + 1) % len(FORM)][0][0]][0]
                    narmande = nasta - 1 if random.random() < 0.6 else nasta + 1
                    for k, ton in enumerate([rot, rot + 3 if random.random() < 0.5 else rot + 2, kvint, narmande]):
                        lat.not_(BAS, ton, s + k, 0.95, 84)
                else:
                    lat.not_(BAS, rot, s, min(2, langd) * 0.97, 86)
                    if langd >= 4:
                        lat.not_(BAS, rot + 7 if random.random() < 0.7 else rot - 5, s + 2, 1.95, 76)
                    elif langd == 2:
                        pass
                pos += langd
            # Trummor med visp: svep på varje slag, slag på 2 och 4, mjuk ride och hihat med foten
            for b in range(4):
                lat.not_(TRUMMOR, 40, t0 + b, 0.9, 34 if del_ == "intro" else 44, jitter=0.006)
                if b in (1, 3):
                    lat.not_(TRUMMOR, 38, t0 + b, 0.3, 40, jitter=0.006)
                    lat.not_(TRUMMOR, 44, t0 + b, 0.2, 30, jitter=0.004)
                if del_ in ("A1", "A2"):
                    lat.not_(TRUMMOR, 51, t0 + b, 0.5, 30 if b % 2 == 0 else 26, jitter=0.004)
                    if b in (1, 3):
                        lat.not_(TRUMMOR, 51, swing(t0 + b + 0.5, 0.12), 0.3, 20, jitter=0.004)
        # Melodier (avstängda: musiken är bara komp, sätt SOLISTER = True för sax och trumpet)
        if not SOLISTER:
            continue
        a1, a2, ut = start + 4 * 4, start + 20 * 4, start + 36 * 4
        for (t, s, n, l) in MELODI:
            slag = a1 + t * 4 + swing(s)
            lat.not_(SAX, n, slag, l, 92 if l < 1 else 100)
            if l >= 1.5:
                lat.svall(SAX, slag, l, 85, 120, 95)
        for (t, s, n, l) in MELODI2:
            slag = a2 + t * 4 + swing(s)
            lat.not_(TRUMPET, n, slag, l, 96 if l < 1 else 106)
            if l >= 1.5:
                lat.svall(TRUMPET, slag, l, 90, 125, 100)
        # Saxen lägger mjuka långa toner under trumpeten
        for t in range(16):
            namn = A[t][0][0]
            rost = ACK[namn][1]
            lat.not_(SAX, rost[1], a2 + t * 4 + 0.05, 3.8, 46)
            lat.svall(SAX, a2 + t * 4, 3.8, 50, 70, 55)
        for (t, s, n, l) in AVSLUT:
            slag = ut + t * 4 + swing(s)
            lat.not_(SAX, n, slag, l, 80)
            if l >= 1.5:
                lat.svall(SAX, slag, l, 70, 100, 50)
    return lat, takter_per_varv * 4 * 60.0 / lat.tempo


def musik():
    print("Musik: deckarjazz")
    lat, langd = komponera_jazz(varv=2)
    mid = CACHE / "jazz.mid"
    CACHE.mkdir(exist_ok=True)
    lat.spara(mid)
    wav = rendera(mid, CACHE / "jazz_full.wav", gain=0.45, rumstorlek=0.8, klangniva=0.6)
    x = las_wav(wav)
    # Ta andra varvet: där finns redan efterklangen från första varvet, så slingan blir sömlös.
    n = int(round(langd * SR))
    p = spara_wav("jazz_slinga", slinga_ur(x, n))
    p2 = CACHE / "jazz_eq.wav"
    kor("sox", p, p2, "bass", "-2", "100", "treble", "+2", "6000")
    till_mp3(p2, "jazz", kbps=160, normal=-1.5)
    return {"jazz": n}


# ======================================================================
#  FIOLSPELAREN: Bachs Preludium i C-dur (BWV 846), brutna ackord
# ======================================================================
PRELUDIUM = [
    [60, 64, 67, 72, 76], [60, 62, 69, 74, 77], [59, 62, 67, 74, 77], [60, 64, 67, 72, 76],
    [60, 64, 69, 76, 81], [60, 62, 66, 69, 74], [59, 62, 67, 74, 79], [59, 60, 64, 67, 72],
    [57, 60, 64, 67, 72], [50, 57, 62, 66, 72], [55, 59, 62, 67, 71], [55, 58, 64, 67, 73],
    [53, 57, 62, 69, 74], [53, 56, 62, 65, 71], [52, 55, 60, 67, 72], [52, 53, 57, 60, 65],
]


def fiol():
    print("Fiolspelaren")
    random.seed(846)
    lat = Lat(tempo=66)
    lat.program(0, 40)
    lat.cc(0, 7, 110); lat.cc(0, 91, 70); lat.cc(0, 10, 64)
    t = 0.0
    for takt in PRELUDIUM:
        for halv in range(2):
            figur = [takt[0], takt[1], takt[2], takt[3], takt[4], takt[2], takt[3], takt[4]]
            for k, ton in enumerate(figur):
                lat.not_(0, ton + 12 if ton < 55 else ton, t + k * 0.25, 0.32, 62 + (10 if k == 0 else 0), jitter=0.008)
            lat.cc(0, 11, 90 + 15 * np.sin(halv * np.pi), t)
            t += 2
    langd = t * 60 / lat.tempo
    mid = CACHE / "fiol.mid"
    lat.spara(mid)
    # Två varv efter varandra, ta det andra för en sömlös slinga
    lat2 = Lat(tempo=66)
    lat2.handelser = list(lat.handelser) + [(h[0] + langd, h[1], h[2]) for h in lat.handelser if h[2].type.startswith("note") or (h[2].type == "control_change" and h[2].control == 11)]
    lat2.spara(mid)
    wav = rendera(mid, CACHE / "fiol_full.wav", gain=0.55, rumstorlek=0.9, klangniva=0.75)
    # Tunnelklang och avstånd läggs på hela renderingen innan slingan klipps ut
    wav2 = klang(wav, CACHE / "fiol_klang.wav", rum=90, efterklang=60, hp=180)
    x = las_wav(wav2)
    n = int(round(langd * SR))
    p = spara_wav("fiol_slinga", slinga_ur(x, n))
    till_mp3(p, "fiol", kbps=128, normal=-3)
    return {"fiol": n}


# ======================================================================
#  MUSIKALISKA EFFEKTER: poäng och slutfanfar
# ======================================================================
def poang_och_fanfar():
    print("Poäng och fanfar")
    random.seed(7)
    lat = Lat(tempo=60)
    lat.program(0, 11)
    lat.cc(0, 91, 80)
    for k, ton in enumerate([72, 75, 79, 82]):
        lat.not_(0, ton, k * 0.09, 1.6, 70 + k * 6, jitter=0)
    mid = CACHE / "poang.mid"; lat.spara(mid)
    wav = rendera(mid, CACHE / "poang.wav", gain=0.6)
    x = las_wav(wav)[: int(2.4 * SR)]
    x[-int(0.4 * SR):] *= np.linspace(1, 0, int(0.4 * SR))[:, None]
    till_mp3(spara_wav("poang_k", x), "poang", kbps=128, normal=-3)

    random.seed(8)
    lat = Lat(tempo=60)
    for k, prog in [(PIANO, 0), (BAS, 32), (SAX, 66), (TRUMPET, 59)]:
        lat.program(k, prog)
        lat.cc(k, 91, 80)
    lat.program(TRUMMOR, 40)  # kanal 10 är trumkanalen; program 40 = Brush Kit
    for k, (s, ton, l) in enumerate([(0, 67, 0.3), (0.33, 72, 0.3), (0.66, 75, 0.3), (1.0, 79, 2.8)]):
        lat.not_(TRUMPET, ton, s, l, 92, jitter=0)
    lat.svall(TRUMPET, 1.0, 2.8, 80, 115, 70)
    for ton in [48, 52, 55, 59, 62]:
        lat.not_(PIANO, ton + 12, 1.0, 3, 70, jitter=0)
    for ton in [55, 59, 62]:
        lat.not_(SAX, ton, 1.0, 3, 60, jitter=0)
    lat.not_(BAS, 36, 1.0, 3, 100, jitter=0)
    lat.not_(TRUMMOR, 49, 1.0, 2, 80, jitter=0)
    lat.not_(TRUMMOR, 40, 0.0, 1, 50, jitter=0)
    mid = CACHE / "fanfar.mid"; lat.spara(mid)
    wav = rendera(mid, CACHE / "fanfar.wav", gain=0.55)
    x = las_wav(wav)[: int(5.5 * SR)]
    x[-int(1.0 * SR):] *= np.linspace(1, 0, int(1.0 * SR))[:, None]
    till_mp3(spara_wav("fanfar_k", x), "fanfar", kbps=160, normal=-1.5)




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
#  MILJÖSLINGOR
# ======================================================================
SLINGLANGD = 26.0


def miljo():
    print("Miljöslingor")
    L = SLINGLANGD + 2.0      # två sekunder extra för övertoningen
    n = int(L * SR)

    # Regn ute: tät dropp, sus och ett rännstensporl
    sus = stereo_brus(L, 900, 9000) * 0.25
    droppar = kornregn(L, 900, 1500, 7000, 0.5)
    porl = filt(rosa(n), "band", (180, 900)) * lfo(L, 0.7, 0.4)
    regn_ute = sus + droppar + panorera(porl * 0.18, -0.4)
    langder = {"regn_ute": gor_slinga("regn_ute", regn_ute)}

    # Regn mot kontorsfönstret: dämpat, med större droppar som knackar på glaset
    sus_inne = filt(stereo_brus(L, 200, 3000), "lp", 1800) * 0.35
    glas = kornregn(L, 140, 2500, 6000, 0.6, np.random.default_rng(6))
    tunga = kornregn(L, 25, 700, 1600, 1.0, np.random.default_rng(7))
    rum_ton = filt(stereo_brus(L, 40, 200), "lp", 120) * 0.15
    langder["regn_inne"] = gor_slinga("regn_inne", sus_inne + glas + tunga + rum_ton)

    # Duggregn på Park Avenue
    dugg = stereo_brus(L, 1500, 9000) * 0.12 + kornregn(L, 260, 2000, 8000, 0.35, np.random.default_rng(8))
    stad = filt(stereo_brus(L, 50, 400), "lp", 300) * 0.2
    langder["duggregn"] = gor_slinga("duggregn", dugg + stad)

    # Tunnelbanetunneln: dovt muller, ventilationssus och avlägset dunk
    mull = filt(stereo_brus(L, 25, 180), "lp", 140) * 0.9 * lfo(L, 0.08, 0.3)[:, None]
    vent = stereo_brus(L, 300, 1500) * 0.06
    dunk = np.zeros((n, 2), np.float32)
    for t in np.arange(1.5, L - 1, 3.7):
        lagg(dunk, panorera(knack(70, 3, 0.5, 0.6), RND.uniform(-0.6, 0.6)), t)
    langder["tunnel"] = gor_slinga("tunnel", mull + vent + dunk * 0.3)

    # Hamnen: vågor som slår mot pålar, vatten som klunkar och en svag vind
    vagor = np.zeros((n, 2), np.float32)
    t = 0.0
    while t < L - 3:
        d = RND.uniform(2.5, 4.5)
        k = int(d * SR)
        v = filt(rosa(k, np.random.default_rng(int(t * 100))), "band", (120, 2500))
        kurva = np.sin(np.linspace(0, np.pi, k)) ** 2
        lagg(vagor, panorera(v * kurva, RND.uniform(-0.7, 0.7)), t)
        t += d * RND.uniform(0.45, 0.75)
    klunk = np.zeros((n, 2), np.float32)
    for t in RND.uniform(0, L - 1, 30):
        f = RND.uniform(250, 600)
        b = sinus(f, 0.08, f * 1.6) * hylsa(int(0.08 * SR), 0.003, 0.02)
        lagg(klunk, panorera(b, RND.uniform(-0.8, 0.8)), t)
    vind = filt(stereo_brus(L, 200, 1200), "lp", 700) * 0.12 * lfo(L, 0.05, 0.6)[:, None]
    langder["hamn"] = gor_slinga("hamn", vagor * 0.6 + klunk * 0.25 + vind)

    # Lagret: tyst rumston, en surrande glödlampa och lite vind genom springor
    surr = (sinus(100, L) * 0.5 + sinus(200, L) * 0.25 + sinus(300, L) * 0.1) * 0.02
    springa = filt(stereo_brus(L, 400, 2000), "band", (500, 1400)) * 0.08 * lfo(L, 0.11, 0.8)[:, None]
    langder["lager"] = gor_slinga("lager", panorera(surr, 0.1) + springa + filt(stereo_brus(L, 30, 150), "lp", 100) * 0.12)

    # Wok som fräser
    fras = np.zeros((n, 2), np.float32)
    knaster = kornregn(L, 2500, 3000, 12000, 0.7, np.random.default_rng(12))
    fras += knaster * lfo(L, 0.17, 0.5)[:, None]
    fras += stereo_brus(L, 3000, 12000) * 0.15
    langder["wok"] = gor_slinga("wok", fras)

    # Takvåningen: en golvklocka som tickar varje sekund och mycket svagt inomhusregn
    tick = np.zeros((n, 2), np.float32)
    for s in range(int(L)):
        f = 2400 if s % 2 == 0 else 2000
        lagg(tick, panorera(plus(knack(f, 12, 0.35, 0.12), knack(f * 1.9, 18, 0.12, 0.12)), 0.35), s + 0.2)
    dugg_inne = kornregn(L, 60, 3000, 7000, 0.12, np.random.default_rng(13))
    langder["vaning"] = gor_slinga("vaning", tick + dugg_inne + filt(stereo_brus(L, 30, 200), "lp", 150) * 0.05)

    # Sorl: många otydliga röster (espeak-ng i olika språk och tonlägen) blandade och dämpade
    langder["sorl"] = gor_slinga("sorl", sorl(L), normal=-6)
    return langder


def sorl(L):
    n = int(L * SR)
    ut = np.zeros((n, 2), np.float32)
    sprak = ["sv", "cmn", "yue", "en", "it", "pl", "es", "de"]
    fraser = ["vad kostar den här idag", "jag tar två av dem tack", "har du sett min paraply",
              "regnet slutar aldrig i den här stan", "en kopp te och några dumplings", "nej nej det var i går"]
    r = random.Random(3)
    for i in range(22):
        wav = CACHE / f"sorl_{i}.wav"
        kor("espeak-ng", "-v", f"{r.choice(sprak)}+{r.choice(['m1', 'm3', 'f2', 'f3', 'm5', 'f4'])}",
            "-s", r.randint(140, 190), "-p", r.randint(25, 75), "-a", 80, "-w", wav, " ".join(r.sample(fraser, 3)))
        sr, x = wavfile.read(wav)
        x = signal.resample_poly(x.astype(np.float32) / 32768, SR, sr).astype(np.float32)
        x = filt(x, "lp", 2200)
        start = r.uniform(0, L - 1)
        y = np.zeros(n, np.float32)
        lagg(y, x, start)
        if start + len(x) / SR > L:
            lagg(y, x[int((L - start) * SR):], 0)
        ut += panorera(y * r.uniform(0.3, 1.0), r.uniform(-0.9, 0.9))
    ut = filt(ut, "lp", 1800)
    p = spara_wav("sorl_torr", ut / np.abs(ut).max() * 0.8)
    p2 = klang(p, CACHE / "sorl_k.wav", rum=100, efterklang=80)
    return las_wav(p2)[:n]


# ======================================================================
#  EFFEKTER
# ======================================================================
MEDDELANDE = [
    ("Det här är Cornelia Pettigrew i Pettigrew Towers på Park Avenue.", 0.45),
    ("Min älskade Lord Waffles har blivit kidnappad!", 0.4),
    ("Polisen säger att de inte letar efter hundar.", 0.45),
    ("Jag har hört att ni är billig.", 0.35),
    ("Jag menar, diskret.", 0.5),
    ("Kom genast!", 0.3),
    ("Jag betalar vad som helst!", 0.0),
]


def telefonrost():
    """Läser in meddelandet mening för mening. Returnerar ljudet och när varje mening
    börjar och slutar (sekunder), så att spelet kan skriva ut orden i takt med rösten."""
    delar, tider, t = [], [], 0.0
    for i, (mening, paus) in enumerate(MEDDELANDE):
        wav = CACHE / f"rost_{i}.wav"
        kor("espeak-ng", "-v", "sv+anika", "-s", 158, "-p", 72, "-g", 2, "-w", wav, mening)
        sr, y = wavfile.read(wav)
        y = signal.resample_poly(y.astype(np.float32) / 32768, SR, sr).astype(np.float32)
        aktiv = np.nonzero(np.abs(y) > 0.01)[0]
        y = y[max(0, aktiv[0] - 200):aktiv[-1] + 200]
        tider.append([round(t, 3), round(t + len(y) / SR, 3), mening])
        delar += [y, tyst(paus)]
        t += len(y) / SR + paus
    x = np.concatenate(delar)
    # Bandets svaj (wow och flutter): läs signalen med en långsamt varierande hastighet
    n = len(x)
    t = np.arange(n) / SR
    hast = 1 + 0.006 * np.sin(2 * np.pi * 0.7 * t) + 0.002 * np.sin(2 * np.pi * 6.3 * t)
    pos = np.clip(np.cumsum(hast) - hast[0], 0, n - 1)
    x = np.interp(pos, np.arange(n), x).astype(np.float32)
    # Liten högtalare: bandpass, lite distorsion och bandbrus
    x = filt(x, "band", (380, 3000), ordning=3)
    x = np.tanh(x * 3.5) / np.tanh(3.5)
    x += filt(brus(n), "band", (1500, 7000)) * 0.03
    return x, tider


def effekter():
    print("Effekter")
    # --- Telefonsvararen: klick, bandspolning, stopp, pip, röst, klick och pip ---
    klick = plus(knack(3200, 5, 1.0, 0.05), knack(900, 3, 0.6, 0.08))
    spola = frekvenskurva([(0, 180), (0.2, 900), (1.0, 1500), (1.15, 400)], 1.2)
    motor = oscillator(spola, "saw", 10) * hylsa(len(spola), 0.05, 2) * 0.12
    motor = filt(motor, "band", (300, 5000)) + filt(brus(len(spola)), "band", (2000, 8000)) * 0.08 * hylsa(len(spola), 0.05, 1)
    pip = sinus(1000, 0.35) * hylsa(int(0.35 * SR), 0.005, 2) * 0.35
    pip = np.tanh(pip * 2) * 0.4
    rost, rosttider = telefonrost()
    seq = tyst(1.9 + len(rost) / SR + 1.2)
    lagg(seq, klick, 0.0)
    lagg(seq, motor, 0.12)
    lagg(seq, knack(500, 3, 0.8, 0.1), 1.33)
    lagg(seq, pip, 1.5)
    lagg(seq, rost * 0.55, 2.0)
    slut = 2.0 + len(rost) / SR + 0.3
    lagg(seq, klick, slut)
    lagg(seq, pip, slut + 0.2)
    gor_effekt("svarare", seq, rum=20, efterklang=20, normal=-2)
    texttider = {"svarare": [[t0 + 2.0, t1 + 2.0, m] for t0, t1, m in rosttider]}

    # --- Spärren: polletten faller, vändkorset vrids med en spärrhake ---
    x = tyst(1.2)
    for i, t in enumerate([0.0, 0.05, 0.09]):
        lagg(x, knack(3800 - i * 300, 25, 0.5 - i * 0.12, 0.2), t)
    for i in range(6):
        lagg(x, plus(knack(1800, 10, 0.35, 0.06), knack(600, 4, 0.25, 0.08)), 0.35 + i * 0.07)
    lagg(x, knack(160, 3, 1.0, 0.3), 0.8)
    gor_effekt("blipp", x, rum=60, efterklang=50)

    # --- Spärren säger KLONK ---
    x = tyst(1.0)
    lagg(x, plus(knack(110, 2, 1.2, 0.6), knack(420, 8, 0.6, 0.4), knack(1250, 20, 0.3, 0.5)), 0)
    gor_effekt("klonk", x, rum=60, efterklang=50)

    # --- Tunnelbaneresan: dörrar stängs, tåget accelererar, skramlar, bromsar och dörrsignal ---
    L = 6.5
    n = int(L * SR)
    x = np.zeros((n, 2), np.float32)
    kurva = np.interp(np.arange(n) / SR, [0, 0.6, 2.0, 4.2, 5.4, 6.5], [0.2, 0.3, 1.0, 1.0, 0.5, 0.15])
    mull = filt(stereo_brus(L, 30, 400), "lp", 260) * kurva[:, None] * 1.2
    fart = np.interp(np.arange(n) / SR, [0, 0.8, 3.5, 4.3, 5.4], [0, 0.2, 1.0, 1.0, 0.1])
    motor_f = 55 + 140 * fart
    motor = filt(oscillator(motor_f, "saw", 12), "lp", 700) * 0.25 * kurva
    x += mull + panorera(motor, 0)
    # Hjulskarvar: dubbla slag som tätnar med farten
    t = 0.9
    while t < 5.0:
        v = np.interp(t, [0, 0.8, 3.5, 4.3, 5.4], [0, 0.2, 1.0, 1.0, 0.1])
        if v < 0.05:
            break
        for d in (0, 0.11):
            lagg(x, panorera(plus(knack(520, 4, 0.5, 0.12), knack(1700, 8, 0.2, 0.06)), RND.uniform(-0.3, 0.3)), t + d, v)
        t += 0.75 / max(v, 0.2) * 0.45
    # Bromsgnissel
    gn = sinus(2650, 1.2) * (1 + 0.3 * sinus(7, 1.2)) * hylsa(int(1.2 * SR), 0.15, 0.6) * 0.06
    gn += sinus(3970, 1.2) * hylsa(int(1.2 * SR), 0.2, 0.5) * 0.03
    lagg(x, panorera(gn, 0.2), 4.3)
    # Dörrsignal (två toner)
    for f, t in [(659.3, 5.7), (523.3, 6.05)]:
        lagg(x, panorera(klocka(f, 1.2, ((1, 1, 1), (2, 0.4, 0.5), (3, 0.15, 0.3)), 0.25), 0), t)
    gor_effekt("tunnelbana", x, rum=50, efterklang=40, normal=-2)

    # --- Skrivbordslådan kärvar ---
    x = tyst(1.2)
    lagg(x, friktion(0.55, 40, 90, [380, 950, 2100], 5, 0.4, 0.5), 0.05)
    lagg(x, filt(brus(int(0.55 * SR)), "band", (300, 1800)) * hylsa(int(0.55 * SR), 0.08, 0.3) * 0.25, 0.05)
    lagg(x, plus(knack(180, 3, 1.0, 0.25), knack(700, 6, 0.4, 0.2)), 0.62)
    lagg(x, plus(knack(2600, 30, 0.25, 0.3), knack(3400, 30, 0.2, 0.3)), 0.64)   # saker som skramlar i lådan
    gor_effekt("lada", x, rum=25, efterklang=30)

    # --- Kassaapparaten: knappar, vev, klocka och låda ---
    x = tyst(2.2)
    for i in range(3):
        lagg(x, plus(knack(1500, 10, 0.5, 0.08), knack(500, 4, 0.3, 0.1)), i * 0.11)
    lagg(x, friktion(0.25, 120, 60, [900, 2200], 6, 0.2, 0.25), 0.4)
    lagg(x, plus(klocka(2093, 1.6, vol=0.6), klocka(2637, 1.4, vol=0.35)), 0.65)
    lagg(x, filt(brus(int(0.25 * SR)), "band", (400, 2500)) * hylsa(int(0.25 * SR), 0.05, 0.1) * 0.3, 0.66)
    lagg(x, knack(150, 3, 0.9, 0.3), 0.92)
    gor_effekt("kassa", x, rum=30, efterklang=40)

    # --- Bruno sväljer korven ---
    x = tyst(1.0)
    for t, f in [(0.0, 260), (0.32, 210)]:
        k = int(0.18 * SR)
        g = filt(brus(k), "band", (f * 0.6, f * 2.2)) * hylsa(k, 0.01, 0.05)
        g += sinus(f, 0.18, f * 0.45) * hylsa(k, 0.005, 0.06) * 0.8
        lagg(x, g, t)
    gor_effekt("gulp", x, rum=15, efterklang=20)

    # --- Brunos mage kurrar ---
    L = 1.6
    f = frekvenskurva([(0, 75), (0.4, 95), (0.9, 60), (1.3, 85), (1.6, 70)], L)
    puls = oscillator(f, "saw", 20)
    mage = filt(puls, "band", (60, 700)) * hylsa(int(L * SR), 0.15, 0.8)
    mage += filt(kornregn(L, 80, 150, 600, 1.0, np.random.default_rng(21)).mean(1), "lp", 800) * 0.8
    gor_effekt("mage", mage, rum=10, efterklang=20)

    # --- Lord Waffles morrar: låga glottispulser genom munhålans formanter ---
    L = 1.3
    f = frekvenskurva([(0, 38), (0.3, 46), (0.8, 42), (1.3, 36)], L)
    puls = oscillator(f, "saw", 40) * (1 + 0.5 * sinus(13, L))
    morr = sum(resonans(puls, fr, q) * a for fr, q, a in [(350, 4, 1.0), (900, 5, 0.6), (2300, 6, 0.25)])
    morr += filt(brus(int(L * SR)), "band", (300, 2000)) * 0.15
    morr *= hylsa(int(L * SR), 0.12, 0.9)
    gor_effekt("morr", morr, rum=20, efterklang=30)

    # --- Lord Waffles skäller (gläfs) ---
    x = tyst(0.9)
    for t in (0.0, 0.28):
        k = int(0.14 * SR)
        f = frekvenskurva([(0, 520), (0.04, 780), (0.14, 430)], 0.14)
        p = oscillator(f, "saw", 14)
        g = sum(resonans(p, fr, q) * a for fr, q, a in [(1100, 5, 1.0), (2400, 6, 0.6), (3600, 7, 0.3)])
        g += filt(brus(k), "band", (1500, 5000)) * 0.15
        lagg(x, g * hylsa(k, 0.006, 0.05), t)
    gor_effekt("skall", x, rum=25, efterklang=35)

    # --- Låset dyrkas upp och dörren gnisslar ---
    x = tyst(3.2)
    for t in [0.0, 0.18, 0.31, 0.52, 0.66, 0.84]:
        lagg(x, knack(RND.uniform(3500, 5200), 30, RND.uniform(0.2, 0.4), 0.1), t)
        lagg(x, filt(brus(int(0.05 * SR)), "band", (3000, 9000)) * hylsa(int(0.05 * SR), 0.002, 0.02) * 0.2, t + 0.03)
    lagg(x, plus(knack(2200, 12, 1.0, 0.2), knack(800, 6, 0.6, 0.2)), 1.05)
    lagg(x, friktion(1.6, 25, 60, [420, 1150, 2600], 9, 0.3, 0.45), 1.35)
    gor_effekt("dyrk", x, rum=60, efterklang=55)

    # --- Lyckokakan knäcks ---
    x = tyst(0.5)
    for t in [0.0, 0.02, 0.05, 0.09]:
        k = int(0.04 * SR)
        lagg(x, filt(brus(k), "band", (1500, 9000)) * hylsa(k, 0.001, 0.01) * RND.uniform(0.5, 1), t)
    gor_effekt("krack", x, rum=15, efterklang=20)

    # --- Kexpåsen prasslar ---
    x = tyst(0.8)
    for t in RND.uniform(0, 0.6, 26):
        k = int(0.03 * SR)
        lagg(x, filt(brus(k), "band", (2500, 10000)) * hylsa(k, 0.002, 0.008) * RND.uniform(0.3, 1), t)
    gor_effekt("prassel", x, rum=15, efterklang=20)

    # --- Hissen: klocksignal och dörrar som glider upp ---
    x = tyst(2.6)
    lagg(x, plus(klocka(1319, 2.2, vol=0.5), klocka(1046.5, 2.2, vol=0.0)), 0)
    lagg(x, klocka(1046.5, 2.2, vol=0.45), 0.42)
    k = int(1.0 * SR)
    lagg(x, filt(brus(k), "band", (150, 1200)) * np.sin(np.linspace(0, np.pi, k)) * 0.15, 0.9)
    gor_effekt("hiss", x, rum=50, efterklang=50)

    # --- Händelser i miljöerna ---
    # Bilhorn från 40-talet
    x = tyst(1.3)
    for t, l in [(0.0, 0.28), (0.38, 0.5)]:
        k = int(l * SR)
        f = frekvenskurva([(0, 360), (0.05, 400), (l, 395)], l)
        h = oscillator(f, "saw", 18) + oscillator(f * 1.26, "saw", 14) * 0.7
        h = sum(resonans(h, fr, 4) for fr in (800, 1600, 2500))
        lagg(x, np.tanh(h * 1.5) * hylsa(k, 0.02, l * 2) * (np.arange(k) < k - 200), t)
    gor_effekt("tuta", x, rum=90, efterklang=70, hp=200)

    # Duva som kuttrar
    x = tyst(1.6)
    for i, t in enumerate([0.0, 0.42, 0.75]):
        l = 0.32 if i else 0.38
        f = frekvenskurva([(0, 520), (l * 0.4, 600), (l, 470)], l)
        p = oscillator(f, "saw", 6) * (0.7 + 0.3 * sinus(32, l))
        p = filt(p, "lp", 900)
        lagg(x, p * hylsa(int(l * SR), 0.06, l * 0.5), t)
    gor_effekt("duva", x, rum=40, efterklang=50)

    # Cykelklocka
    x = tyst(1.6)
    for t in (0.0, 0.16):
        lagg(x, klocka(2350, 1.3, ((1, 1, 1), (1.52, 0.6, 0.8), (2.48, 0.4, 0.5), (3.9, 0.2, 0.3)), 0.5), t)
    gor_effekt("cykelklocka", x, rum=70, efterklang=60)

    # Porslin som klirrar
    x = tyst(1.0)
    for t in [0.0, 0.07, 0.19, 0.24]:
        f = RND.uniform(2800, 4600)
        lagg(x, klocka(f, 0.6, ((1, 1, 1), (1.7, 0.5, 0.6), (2.9, 0.3, 0.4)), RND.uniform(0.2, 0.5)), t)
    gor_effekt("klirr", x, rum=50, efterklang=50)

    # Mistlur
    L = 3.8
    f = np.full(int(L * SR), 98.0)
    h = oscillator(f, "saw", 30) + oscillator(f * 1.012, "saw", 30) * 0.8 + oscillator(f * 0.5, "saw", 20) * 0.6
    h = filt(h, "lp", 650) * hylsa(int(L * SR), 0.6, 1.2) * np.clip(np.linspace(1.6, 0, int(L * SR)), 0, 1)
    gor_effekt("mistlur", h, rum=100, efterklang=95, normal=-4)

    # Måsar
    x = tyst(2.0)
    for t in [0.0, 0.35, 0.62, 1.1]:
        l = RND.uniform(0.22, 0.38)
        f = frekvenskurva([(0, 1700), (l * 0.25, 2300), (l, 1200)], l)
        p = oscillator(f, "saw", 8)
        p = sum(resonans(p, fr, 5) * a for fr, a in [(2200, 1), (3400, 0.5)])
        p += filt(brus(int(l * SR)), "band", (1500, 4000)) * 0.2
        lagg(x, p * hylsa(int(l * SR), 0.02, l * 0.35) * RND.uniform(0.5, 1), t)
    gor_effekt("masar", x, rum=100, efterklang=60, normal=-6)

    # Knarr i lagret
    x = tyst(1.6)
    lagg(x, friktion(1.2, 18, 35, [300, 780, 1900], 10, 0.35, 0.5), 0)
    gor_effekt("knarr", x, rum=70, efterklang=60, normal=-5)

    # Tåg som passerar på andra spåret
    L = 6.0
    n = int(L * SR)
    kurva = np.sin(np.linspace(0, np.pi, n)) ** 2
    x = filt(stereo_brus(L, 30, 2500), "lp", 900) * kurva[:, None] * 1.4
    t = 1.2
    while t < 4.8:
        v = np.sin(np.pi * t / L) ** 2
        for d in (0, 0.09):
            lagg(x, panorera(plus(knack(480, 4, 0.6, 0.1), knack(1500, 8, 0.25, 0.06)), -0.8 + 1.6 * t / L), t + d, v)
        t += 0.33
    gor_effekt("tagforbi", x, rum=90, efterklang=70, normal=-4)

    # Vattendroppe i en pöl
    x = tyst(0.6)
    k = int(0.09 * SR)
    lagg(x, sinus(900, 0.09, 2300) * hylsa(k, 0.001, 0.025), 0)
    lagg(x, filt(brus(k), "band", (2000, 7000)) * hylsa(k, 0.001, 0.01) * 0.3, 0)
    gor_effekt("dropp", x, rum=100, efterklang=80, normal=-6)

    # Råtta som piper
    x = tyst(0.8)
    for t in [0.0, 0.12, 0.3]:
        l = 0.07
        f = frekvenskurva([(0, 4200), (0.03, 5200), (l, 3900)], l)
        lagg(x, oscillator(f, "saw", 3) * hylsa(int(l * SR), 0.005, 0.02) * 0.5, t)
    gor_effekt("rattpip", x, rum=80, efterklang=60, normal=-8)
    return {"texttider": texttider}


# ======================================================================
#  Ljudlista till spelet
# ======================================================================
def skriv_ljudlista(nya):
    """Sparar slingornas exakta längd (i samplingar) och texttider för repliker,
    och skriver in dem i spel.html. Spelet behöver längderna för att loopa
    mp3-filerna utan glapp, och texttiderna för att visa orden i takt med rösten."""
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
    spel = ROT / "spel.html"
    s = spel.read_text(encoding="utf-8")
    start, slut = "/* LJUDDATA-START */", "/* LJUDDATA-SLUT */"
    i, j = s.index(start) + len(start), s.index(slut)
    kod = ("\nconst SLINGOR = " + json.dumps(langder, separators=(",", ":")) + ";\n"
           "const TEXTTIDER = " + json.dumps(texttider, separators=(",", ":"), ensure_ascii=False) + ";\n")
    spel.write_text(s[:i] + kod + s[j:], encoding="utf-8")


DELAR = {"musik": musik, "fiol": fiol, "poang": poang_och_fanfar, "miljo": miljo, "effekter": effekter}

if __name__ == "__main__":
    valda = sys.argv[1:] or list(DELAR)
    langder = {}
    for namn in valda:
        res = DELAR[namn]()
        if isinstance(res, dict):
            langder.update(res)
    skriv_ljudlista(langder)
    print("Klart. Kör verktyg/bygg.py för att bygga index.html.")
