#!/usr/bin/env python3
"""Ritar bilderna till Borgmästarens långkalsonger.

Platser från tidigare fall ritas med funktionerna i aventyr/papegojan/verktyg/rita_bilder.py
(och därigenom aventyr/mopsen-klick), med nya utgångar och ändringar ovanpå.
De nya platserna finns i scener_a.py till scener_e.py.

Kör:  python3 aventyr/kalsongerna/verktyg/rita_bilder.py
      python3 motor/verktyg/bygg.py kalsongerna
"""
import importlib.util
import sys
from pathlib import Path

MAPP = Path(__file__).resolve().parent.parent
VERKTYG = Path(__file__).resolve().parent
sys.path.insert(0, str(MAPP.parent.parent / "motor" / "verktyg"))
from pixelbild import *   # noqa: E402,F401,F403


def _ladda(namn, fil):
    spec = importlib.util.spec_from_file_location(namn, fil)
    modul = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modul)
    return modul


P = _ladda("papegojan_bilder", MAPP.parent / "papegojan" / "verktyg" / "rita_bilder.py")
M = P.M


def pil(d, x0, y0, x1, y1, riktning, etikett=None, bg=12, fg=15):
    """En liten gatuskylt med pil. riktning: 'v', 'ö', 'n' eller 's'."""
    d.rekt(x0, y0, x1, y1, 0)
    d.rekt(x0 + 1, y0 + 1, x1 - 1, y1 - 1, bg)
    cy, cx = (y0 + y1) // 2, (x0 + x1) // 2
    if riktning == "v":
        d.poly([(x0 + 2, cy), (x0 + 6, cy - 3), (x0 + 6, cy + 3)], fg)
    elif riktning == "ö":
        d.poly([(x1 - 2, cy), (x1 - 6, cy - 3), (x1 - 6, cy + 3)], fg)
    elif riktning == "n":
        d.poly([(x1 - 5, y0 + 2), (x1 - 8, y0 + 5), (x1 - 2, y0 + 5)], fg)
        d.rekt(x1 - 6, y0 + 5, x1 - 4, y1 - 2, fg)
    elif riktning == "s":
        d.poly([(x1 - 5, y1 - 2), (x1 - 8, y1 - 5), (x1 - 2, y1 - 5)], fg)
        d.rekt(x1 - 6, y0 + 2, x1 - 4, y1 - 5, fg)
    if etikett:
        tx = x0 + 8 if riktning == "v" else x0 + 3
        text(d, tx, y0 + 2, etikett, fg)


# ---------------------------------------------------------------- kontoret
def kontor(v=None):
    v = dict(v or {})
    lapp = v.get("tvattlapp", True)
    v.update({"telegram": False, "check": False, "kniv": False})
    d = P.kontor(v)
    # Signerat fotografi av papegojan där checken hängde
    with d.yta("papegojfoto"):
        d.rekt(141, 13, 163, 30, 9)
        d.rekt(142, 14, 162, 29, 10)
        d.rekt(143, 15, 161, 28, 1)
        d.rekt(149, 17, 155, 22, 13)                   # huvudet, rött
        d.rekt(147, 21, 157, 27, 13)                   # kroppen
        d.rekt(147, 24, 149, 28, 4)                    # blå vinge
        d.rekt(155, 24, 157, 28, 11)                   # gul stjärt
        d.px(150, 18, 15)
        d.rekt(154, 19, 156, 20, 15)                   # näbben
        d.px(159, 26, 0)                               # fågelavtrycket
        d.px(158, 27, 0)
        d.px(160, 27, 0)
    # Tvättlappen på skrivbordet
    if lapp:
        with d.yta("tvattlapp"):
            d.poly([(110, 64), (122, 62), (124, 67), (112, 69)], 15)
            d.linje(112, 65, 120, 64, 4)
            d.linje(113, 67, 119, 66, 4)
            d.rekt(121, 63, 123, 65, 13)
            d.linje(123, 64, 128, 61, 9)               # snöret
        d.markera("tvattlapp", 106, 58, 124, 72)
    return d


# ---------------------------------------------------------------- nya utgångar på gamla platser
def main_street(v=None):
    d = M.main_street(v)
    with d.yta("utgang:v"):
        pil(d, 0, 60, 22, 70, "v")
    with d.yta("utgang:ö"):
        pil(d, 170, 38, 192, 48, "ö")
    return d


def park_avenue(v=None):
    d = M.park_avenue(v)
    with d.yta("utgang:n"):
        d.rekt(166, 60, 168, 80, 4)
        pil(d, 150, 52, 184, 62, "n", "PARK")
    return d


def chinatown(v=None):
    d = M.chinatown(v)
    with d.yta("utgang:n"):
        d.rekt(96, 50, 98, 64, 4)
        pil(d, 76, 42, 118, 52, "n", "BAKGATA")
    return d


def torget(v=None):
    d = SA_TORGET(v)
    d.markera("utgang:n", 25, 49, 41, 88)               # rådhusets port
    return d


def blvd_o(v=None):
    d = SB_BLVD_O(v)
    # Lolas affisch har fått en lapp: på turné
    with d.yta("lolaaffisch"):
        d.rekt(27, 66, 62, 75, 0)
        d.rekt(28, 67, 61, 74, 11)
        d.rekt(28, 73, 61, 74, 9)
        text(d, 35, 68, "TURNE", 0)
    with d.yta("utgang:n"):
        pil(d, 2, 10, 30, 20, "n", "WGHR")
        d.rekt(14, 20, 16, 58, 4)
    return d


def perrong_blvd(v=None):
    """Lolas konsertaffisch har ersatts av en affisch för radiodebatten."""
    d = SA_PBLVD(v)
    with d.yta("affisch"):
        x0, y0, x1, y1 = 74, 37, 128, 73
        d.rekt(x0, y0, x1, y1, 0)
        d.rekt(x0 + 1, y0 + 1, x1 - 1, y1 - 1, 1)
        d.rekt(x0 + 1, y0 + 1, x1 - 1, y0 + 10, 13)
        text(d, x0 + 4, y0 + 3, "RADIODEBATT", 15)
        for cx, farg in ((x0 + 15, 9), (x1 - 15, 8)):     # två kandidater med mustasch
            d.a[d.mask_ellips(cx - 7, y0 + 13, cx + 7, y0 + 27)] = farg
            d.px(cx - 3, y0 + 18, 0)
            d.px(cx + 3, y0 + 18, 0)
            d.rekt(cx - 5, y0 + 22, cx + 5, y0 + 23, 0)
            d.rekt(cx - 6, y0 + 27, cx + 6, y0 + 31, 2)
        text(d, x0 + 23, y0 + 17, "MOT", 11)
        text(d, x0 + 6, y0 + 33, "BIGSBY", 15)
        text(d, x0 + 31, y0 + 33, "WGHR", 11)
    return d


def pantbank(v=None):
    """Fru Pettigrews check står nu i en glasmonter på disken."""
    d = SC_PANTBANK(v)
    with d.yta("checkmonter"):
        x0, y0, x1, y1 = 134, 44, 166, 68
        d.rekt(x0, y1 - 3, x1, y1, 7)                      # sockel i trä
        d.rekt(x0, y1 - 3, x1, y1 - 2, 9)
        d.rekt(x0 + 1, y0, x1 - 1, y1 - 3, 2)              # glaset
        d.rekt(x0 + 3, y0 + 5, x1 - 3, y1 - 6, 15)         # checken
        d.rekt(x0 + 3, y0 + 5, x1 - 3, y0 + 7, 12)
        for x in range(x0 + 5, x1 - 4, 2):
            d.px(x, y0 + 10, 2)                            # alla nollorna
        d.linje(x0 + 12, y0 + 13, x1 - 5, y0 + 13, 2)
        d.linje(x0 + 1, y0, x0 + 1, y1 - 3, 5)             # glasets kanter
        d.linje(x1 - 1, y0, x1 - 1, y1 - 3, 5)
        d.linje(x0 + 1, y0, x1 - 1, y0, 5)
        d.linje(x0 + 4, y0 + 2, x0 + 9, y0 + 2, 15)        # glans
    return d


def pir9(v=None):
    d = P.pir9(v)
    with d.yta("utgang:s"):
        d.rekt(136, 60, 138, 92, 4)
        pil(d, 122, 50, 152, 60, "s", "FISK")
    return d


def grand(v=None):
    d = SC_GRAND(v)
    d.markera("utgang:in", 103, 85, 121, 107)           # tvätteriets bakdörr
    return d


def _scener():
    s = {}
    for namn in ("p_main", "p_park", "p_china", "p_pir", "restaurang", "blvd_m", "blvd_v", "urmakare", "klubb"):
        s[namn] = P.SCENER[namn]
    kontor_anim = [a for a in P.SCENER["kontor"][1] if a[0] not in ("telegram", "check", "kniv")]
    kontor_anim.append(("tvattlapp", "tvattlapp", [(True, 1000), (False, 1000)], 1))
    s["kontor"] = (kontor, kontor_anim)
    s["mainst"] = (main_street, P.SCENER["mainst"][1])
    s["parkave"] = (park_avenue, P.SCENER["parkave"][1])
    s["china"] = (chinatown, P.SCENER["china"][1])
    s["torget"] = (torget, P.SCENER["torget"][1])
    s["blvd_o"] = (blvd_o, P.SCENER["blvd_o"][1])
    s["pir"] = (pir9, P.SCENER["pir"][1])
    s["p_blvd"] = (perrong_blvd, P.SCENER["p_blvd"][1])
    s["pantbank"] = (pantbank, P.SCENER["pantbank"][1])
    s["grand"] = (grand, P.SCENER["grand"][1])
    for bok in "abcde":
        fil = VERKTYG / f"scener_{bok}.py"
        if fil.exists():
            s.update(getattr(_ladda(f"scener_{bok}", fil), f"SCENER_{bok.upper()}"))
    return s


SA_TORGET = P.SCENER["torget"][0]
SB_BLVD_O = P.SCENER["blvd_o"][0]
SC_GRAND = P.SCENER["grand"][0]
SA_PBLVD = P.SCENER["p_blvd"][0]
SC_PANTBANK = P.SCENER["pantbank"][0]
SCENER = _scener()

if __name__ == "__main__":
    exportera_alla(SCENER, MAPP / "bilder")
