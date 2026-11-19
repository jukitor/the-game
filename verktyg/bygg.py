#!/usr/bin/env python3
"""Bygger index.html (fristående sida för GitHub Pages) från spel.html.

spel.html är källan. Den saknar <head>, eftersom den också publiceras som Claude-artefakt.
Kör:  python3 verktyg/bygg.py
"""
from pathlib import Path

rot = Path(__file__).resolve().parent.parent
s = (rot / "spel.html").read_text(encoding="utf-8")
huvud, rest = s.split("<style>", 1)
css, kropp = rest.split("</style>", 1)
html = (
    '<!doctype html>\n<html lang="sv">\n<head>\n<meta charset="utf-8">\n'
    '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
    + huvud + "<style>" + css + "</style>\n</head>\n<body>" + kropp + "</body>\n</html>\n"
)
(rot / "index.html").write_text(html, encoding="utf-8")
print("Byggde", rot / "index.html")
