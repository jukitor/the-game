#!/usr/bin/env python3
"""Bygger ett äventyr för spelmotorn.

  python3 motor/verktyg/bygg.py mopsen      (ett äventyr)
  python3 motor/verktyg/bygg.py             (alla äventyr i aventyr/)

För varje äventyr i aventyr/<namn>/ skapas:
  data.js     genererad data: bildanimationer (bilder/bilddata.json), ljudslingornas
              längd (ljud/slingor.json) och repliktider (ljud/texttider.json)
  index.html  sidan som laddar motorn (../../motor/) och äventyret. Används på GitHub Pages.
  spel.html   samma spel i en enda fil (motor, äventyr och data inbakade), utan <head>,
              för publicering som Claude-artefakt. Bilder och ljud ligger kvar i bilder/ och ljud/.
"""
import hashlib
import os
import re
import json
import sys
from pathlib import Path

ROT = Path(__file__).resolve().parent.parent.parent
MOTOR = ROT / "motor"
TYPSNITT = ('<link rel="preconnect" href="https://fonts.googleapis.com">\n'
            '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Courier+Prime:ital,wght@0,400;0,700;1,400&family=Oswald:wght@500;600&display=swap">\n')


def las_json(p, standard):
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else standard


def titel(mapp):
    """Läser äventyrets titel ur aventyr.js (raden titel: "...")."""
    for rad in (mapp / "aventyr.js").read_text(encoding="utf-8").splitlines():
        rad = rad.strip()
        if rad.startswith("titel:"):
            return rad.split('"')[1]
    return mapp.name


def mappar(mapp, nyckel):
    """Mappar som ett äventyr lånar från, t.ex. raden ljudmapp: "../annat/ljud/" eller
    ljudmapp: ["../ett/ljud/", "../annat/ljud/"] i aventyr.js. Den första går före de senare."""
    for rad in (mapp / "aventyr.js").read_text(encoding="utf-8").splitlines():
        rad = rad.strip()
        if rad.startswith(nyckel + ":"):
            return [(mapp / v).resolve() for v in re.findall(r'"([^"]+)"', rad.split("//")[0])]
    return []


def bygg(mapp):
    # Ljuden: äventyrets egna i ljud/ och de lånade i ljudmapp. Egna går före lånade med samma namn,
    # och en tidigare ljudmapp före en senare.
    egna = mapp / "ljud"
    kallor = [k for k in dict.fromkeys(list(reversed(mappar(mapp, "ljudmapp"))) + [egna]) if k.exists()]
    slingor, texttider, ljudfiler = {}, {}, {}
    for k in kallor:
        slingor.update(las_json(k / "slingor.json", {}))
        texttider.update(las_json(k / "texttider.json", {}))
        for f in sorted(k.glob("*.mp3")):
            if k == egna:
                ljudfiler.pop(f.stem, None)
            else:
                ljudfiler[f.stem] = os.path.relpath(f, mapp).replace(os.sep, "/")
    # Bilderna: äventyrets egna i bilder/, eller lånade från bildmapp
    bildmapp = (mappar(mapp, "bildmapp") or [mapp / "bilder"])[0]
    data = {
        "bilder": las_json(bildmapp / "bilddata.json", {"palett": [], "bilder": {}}),
        "slingor": slingor,
        "texttider": texttider,
        "ljudfiler": ljudfiler,   # lånade ljud: namn -> sökväg. Övriga ligger i ljud/
    }
    datajs = ("// Genererad av motor/verktyg/bygg.py. Redigera inte för hand.\n"
              "window.AVENTYRSDATA = " + json.dumps(data, separators=(",", ":"), ensure_ascii=False) + ";\n")
    (mapp / "data.js").write_text(datajs, encoding="utf-8")

    t = titel(mapp)
    # Versionsnummer efter innehållet, så att webbläsaren hämtar nya filer när något har ändrats
    v = lambda fil: hashlib.sha1(fil.read_bytes()).hexdigest()[:10]
    vcss, vmotor = v(MOTOR / "motor.css"), v(MOTOR / "motor.js")
    vdata, vaventyr = v(mapp / "data.js"), v(mapp / "aventyr.js")
    index = f"""<!doctype html>
<html lang="sv">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{t}</title>
{TYPSNITT}<link rel="stylesheet" href="../../motor/motor.css?v={vcss}">
</head>
<body>
<script src="data.js?v={vdata}"></script>
<script src="aventyr.js?v={vaventyr}"></script>
<script src="../../motor/motor.js?v={vmotor}"></script>
</body>
</html>
"""
    (mapp / "index.html").write_text(index, encoding="utf-8")

    css = (MOTOR / "motor.css").read_text(encoding="utf-8")
    motor = (MOTOR / "motor.js").read_text(encoding="utf-8")
    aventyr = (mapp / "aventyr.js").read_text(encoding="utf-8")
    spel = (f"<meta charset=\"utf-8\">\n<title>{t}</title>\n<meta name=\"claude:viewport-fit-sides\" content=\"cover\">\n{TYPSNITT}"
            f"<style>\n{css}</style>\n<script>\n{datajs}</script>\n<script>\n{aventyr}</script>\n"
            # I den inbakade filen ligger ljuden alltid i ljud/ bredvid sidan
            f"<script>window.AVENTYR && (delete window.AVENTYR.ljudmapp, delete window.AVENTYR.bildmapp); window.AVENTYRSDATA && delete window.AVENTYRSDATA.ljudfiler;</script>\n"
            f"<script>\n{motor}</script>\n")
    (mapp / "spel.html").write_text(spel, encoding="utf-8")
    print(f"Byggde {mapp.relative_to(ROT)}: data.js, index.html, spel.html ({len(spel) // 1024} kB)")


if __name__ == "__main__":
    namn = sys.argv[1:] or sorted(p.name for p in (ROT / "aventyr").iterdir() if (p / "aventyr.js").exists())
    for n in namn:
        bygg(ROT / "aventyr" / n)
