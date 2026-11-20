#!/usr/bin/env python3
"""Ritar bilderna till Papegojan som visste för mycket.

Platser som finns kvar från förra fallet ritas med funktionerna i
aventyr/mopsen-klick/verktyg/rita_bilder.py, ibland med ändringar ovanpå.
De nya platserna finns i scener_a.py, scener_b.py och scener_c.py.

Kör:  python3 aventyr/papegojan/verktyg/rita_bilder.py
      python3 motor/verktyg/bygg.py papegojan
"""
import importlib.util
import sys
from pathlib import Path

MAPP = Path(__file__).resolve().parent.parent
VERKTYG = Path(__file__).resolve().parent
sys.path.insert(0, str(MAPP.parent.parent / "motor" / "verktyg"))
sys.path.insert(0, str(VERKTYG))
from pixelbild import *   # noqa: E402,F401,F403


def _ladda(namn, fil):
    spec = importlib.util.spec_from_file_location(namn, fil)
    modul = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modul)
    return modul


M = _ladda("mopsen_bilder", MAPP.parent / "mopsen-klick" / "verktyg" / "rita_bilder.py")


# ======================================================================
#  KONTORET, några veckor senare
# ======================================================================
def kontor(v=None):
    v = dict(v or {})
    telegram = v.get("telegram", True)    # telegrammet ligger på golvet
    check = v.get("check", True)          # den inramade checken hänger på väggen
    kniv = v.get("kniv", True)            # brevkniven ligger på skrivbordet
    d = M.kontor(v)

    # Den inramade checken från fru Pettigrew, som banken vägrade lösa in
    if check:
        with d.yta("check"):
            d.rekt(138, 13, 166, 29, 9)
            d.rekt(139, 14, 165, 28, 10)
            d.rekt(140, 15, 164, 27, 9)
            d.rekt(141, 16, 163, 26, 15)
            d.rekt(141, 16, 163, 18, 12)
            for x in range(143, 162, 2):
                d.px(x, 21, 2)              # alla nollorna
            d.linje(150, 24, 161, 24, 2)
            d.px(162, 23, 13)
    else:
        # En ljusare fläck på tapeten där checken hängde
        d.ljus(d.mask_poly([(139, 14), (166, 14), (166, 28), (139, 28)]), 0.35)

    # Porträtt av Lord Waffles med tassavtryck, en gåva
    with d.yta("mopsportratt"):
        d.a[d.mask_ellips(144, 31, 160, 47)] = 9
        d.a[d.mask_ellips(145, 32, 159, 46)] = 1
        d.a[d.mask_ellips(147, 35, 157, 45)] = 9       # mopsens huvud
        d.a[d.mask_ellips(149, 39, 155, 45)] = 8       # nosparti
        d.rekt(150, 40, 154, 42, 0)
        d.px(149, 37, 0)
        d.px(155, 37, 0)
        d.rekt(146, 35, 148, 38, 8)                    # öron
        d.rekt(156, 35, 158, 38, 8)
        d.px(158, 44, 13)                              # tassavtryck i rött
        d.px(157, 45, 13)
        d.px(159, 45, 13)

    # Brevkniven ligger på räkningarna
    if kniv:
        with d.yta("brevkniv"):
            d.linje(112, 65, 124, 63, 5)
            d.linje(112, 66, 124, 64, 15)
            d.rekt(124, 62, 129, 65, 9)
            d.rekt(125, 63, 128, 64, 10)

    # Ett telegram har stuckits in under dörren
    if telegram:
        with d.yta("telegram"):
            d.poly([(20, 99), (36, 97), (38, 104), (22, 106)], 11)
            d.poly([(21, 99), (35, 98), (36, 99), (22, 100)], 9)
            d.linje(24, 102, 33, 101, 8)
            d.rekt(23, 99, 26, 100, 13)
    return d


# ======================================================================
#  PIR 9, där det har hänt saker sedan sist
# ======================================================================
def pir9(v=None):
    v = dict(v or {})
    v["lage"] = 0
    d = M.pir9(v)

    # Polisens avspärrning över dörren till Lager 13
    with d.yta("dorr"):
        d.linje(54, 56, 78, 92, 10)
        d.linje(55, 56, 79, 92, 0)
        d.linje(78, 56, 54, 92, 10)
        d.linje(79, 56, 55, 92, 0)
        for t in range(0, 24, 6):
            d.px(56 + t, 59 + int(t * 1.5), 0)
            d.px(76 - t, 59 + int(t * 1.5), 0)

    # Brunos nya korvvagn framför honom
    with d.yta("korvvagn"):
        d.rekt(66, 78, 112, 96, 15)
        d.rekt(66, 78, 112, 80, 13)
        d.rekt(66, 94, 112, 96, 4)
        for x in range(68, 112, 6):
            d.rekt(x, 81, x + 3, 93, 13)
        d.rekt(70, 84, 108, 90, 15)
        text(d, 72, 84, "KORV", 13)
        d.rekt(68, 96, 72, 100, 0)                     # hjul
        d.rekt(104, 96, 108, 100, 0)
        d.rekt(108, 46, 110, 78, 4)                    # parasollets stång
        d.poly([(94, 48), (124, 48), (118, 40), (100, 40)], 13)
        d.poly([(99, 48), (104, 48), (105, 40), (102, 40)], 15)
        d.poly([(113, 48), (118, 48), (115, 40), (112, 40)], 15)

    # Skylt tillbaka mot Boulevarden vid vänsterkanten
    with d.yta("utgang:v"):
        d.rekt(9, 58, 11, 98, 4)
        d.poly([(1, 58), (22, 58), (22, 66), (1, 66), (-1, 62)], 12)
        d.poly([(2, 59), (21, 59), (21, 65), (2, 65), (0, 62)], 4)
        text(d, 6, 60, "BLVD", 15)
    return d


def _scener():
    s = {}
    for namn in ("mainst", "parkave", "china", "restaurang", "p_main", "p_park", "p_china", "p_pir"):
        s[namn] = M.SCENER[namn]
    kontor_anim = [a for a in M.SCENER["kontor"][1]]
    kontor_anim += [
        ("telegram", "telegram", [(True, 1000), (False, 1000)], 1),
        ("check", "check", [(True, 1000), (False, 1000)], 1),
        ("kniv", "kniv", [(True, 1000), (False, 1000)], 1),
    ]
    s["kontor"] = (kontor, kontor_anim)
    s["pir"] = (pir9, [a for a in M.SCENER["pir"][1] if a[0] != "lage"])
    for fil, namn in (("scener_a.py", "SCENER_A"), ("scener_b.py", "SCENER_B"), ("scener_c.py", "SCENER_C")):
        if (VERKTYG / fil).exists():
            s.update(getattr(_ladda(fil[:-3], VERKTYG / fil), namn))
    return s


SCENER = _scener()

if __name__ == "__main__":
    namn = sys.argv[1:]
    exportera_alla({k: v for k, v in SCENER.items() if not namn or k in namn} if namn else SCENER, MAPP / "bilder")
