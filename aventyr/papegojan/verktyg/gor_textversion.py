#!/usr/bin/env python3
"""Skapar textversionen av Papegojan som visste för mycket (aventyr/papegojan-text/aventyr.js)
från klickversionen (aventyr/papegojan/aventyr.js). Klickversionen är originalet: ändra där och
kör det här skriptet igen. Textversionen lånar bilder och ljud från klickversionen.

Kör:  python3 aventyr/papegojan/verktyg/gor_textversion.py
      python3 motor/verktyg/bygg.py papegojan-text
"""
from pathlib import Path

KALLA = Path(__file__).resolve().parent.parent / "aventyr.js"
UT = KALLA.parent.parent / "papegojan-text" / "aventyr.js"

BYTEN = [
    # Huvudet och inställningarna
    ("   PAPEGOJAN SOM VISSTE FÖR MYCKET\n",
     "   PAPEGOJAN SOM VISSTE FÖR MYCKET (TEXTVERSIONEN)\n"
     "   GENERERAD av aventyr/papegojan/verktyg/gor_textversion.py från klickversionen.\n"
     "   Redigera inte här, utan i aventyr/papegojan/aventyr.js, och kör skriptet igen.\n"),
    ('  id: "papegojan",\n', '  id: "papegojan-text",\n'),
    ('  lage: "klick",\n', '  lage: "text",\n'),
    ('  ljudmapp: "../mopsen/ljud/",\n',
     '  ljudmapp: ["../papegojan/ljud/", "../mopsen/ljud/"],\n  bildmapp: "../papegojan/bilder/",\n'),
    # Introt
    ('    { text: "Tryck på saker i bilden, eller på det du bär, för att välja vad du vill göra. Tryck på en tom del av bilden för att se dig omkring. Under MENY finns hjälp, ledtrådar, sparning och ljud.", klass: "sys" },\n',
     '    { text: "Skriv HJÄLP om du inte vet vad du ska göra, eller LEDTRÅD om du kör fast.", klass: "sys" },\n'
     '    { text: "Spelet har musik och ljud. Det startar när du skriver eller trycker första gången. Skriv LJUD eller MUSIK för att stänga av.", klass: "sys" },\n'),
    # Texter som talar om knappar och menyer
    ('    spelSlut: "Fallet är redan löst. Välj Börja om i menyn för att spela igen.",\n',
     '    spelSlut: "Fallet är redan löst. Skriv OMSTART för att spela igen, eller POÄNG för att se hur det gick.",\n'
     '    hjalp: [\n'
     '      "Du styr detektiven genom att skriva vad du vill göra, med korta meningar på svenska. Oftast räcker ett verb, ibland följt av vad eller vem det gäller.",\n'
     '      "TITTA (eller T): se dig omkring\\nUNDERSÖK något (eller U): titta närmare på något\\nTA, SLÄPP, ÖPPNA, LÄS: hantera saker\\nPRATA MED, GE, VISA: ta kontakt med folk\\nANVÄND något PÅ något: använd en sak på en annan\\nN, S, Ö, V, UPP, NER, IN, UT: gå åt ett håll\\nÅK TILL: res med tunnelbanan från en perrong\\nINVENTARIE (eller I): se vad du bär på",\n'
     '      "Undersök det du ser och prata med dem du möter. Kör du fast kan du skriva LEDTRÅD.",\n'
     '    ],\n'),
    ('      vart: "Vart vill du åka? Tryck på linjekartan och välj en station.",\n',
     '      vart: "Vart vill du åka? Skriv till exempel ÅK TILL BOULEVARDEN.",\n'),
    ('Tryck på kartan och välj vart du vill åka." },', 'Skriv till exempel ÅK TILL BOULEVARDEN för att resa." },'),
    ('      { sys: "Välj Börja om i menyn för att spela igen." },\n', '      { sys: "Skriv OMSTART för att spela igen." },\n'),
    ('Titta på porttelefonen och ring på." },', 'Undersök porttelefonen och ring på, till exempel RING HOS OSTROWSKI." },'),
    ('text: "Klättra upp till tredje våningen på urmakarens brandstege." },',
     'text: "KLÄTTRA TILL TREDJE VÅNINGEN PÅ URMAKARENS BRANDSTEGE." },'),
    ('text: "Använd något stort och mörkt på buren, så tror Caruso att det är natt." },',
     'text: "Täck buren med något stort och mörkt, så tror Caruso att det är natt. Till exempel TÄCK BUREN MED ROCKEN." },'),
    ('text: "Lola sa att Caruso bara pratar i sömnen, när det är mörkt i buren. Har du något stort att täcka en bur med? Kanske hänger det på kontoret." },',
     'text: "Lola sa att Caruso bara pratar i sömnen, när det är mörkt i buren. Har du något stort att täcka en bur med? Kanske hänger det på kontoret." },'),
    ('text: "Köp paraplyet med kroken i pantbanken." },', 'text: "Köp paraplyet med kroken i pantbanken: KÖP PARAPLYET." },'),
    ('text: "Använd paraplyet på urmakarens brandstege i gränden." },',
     'text: "Haka ner urmakarens brandstege med paraplyet: ANVÄND PARAPLYET PÅ URMAKARENS BRANDSTEGE." },'),
    ('text: "Använd batterierna på ficklampan." },', 'text: "Sätt i batterierna: ANVÄND BATTERIERNA PÅ FICKLAMPAN." },'),
    ('text: "Gå in genom fönstret med ficklampan tänd." },', 'text: "Gå IN genom fönstret med ficklampan tänd." },'),
]

SNABB = ('  snabbknappar: [["Titta", "titta"], ["Ägodelar", "inventarie"], ["N", "n"], ["S", "s"], ["Ö", "ö"], ["V", "v"], '
         '["Upp", "upp"], ["Ner", "ner"], ["In", "in"], ["Ut", "ut"], ["Ledtråd", "ledtråd"], ["Ljud", "ljud"], ["Hjälp", "hjälp"]],\n\n')


def main():
    s = KALLA.read_text(encoding="utf-8")
    for a, b in BYTEN:
        n = s.count(a)
        if n != 1:
            raise SystemExit(f"Hittade texten {n} gånger (ska vara en): {a[:70]!r}")
        s = s.replace(a, b)
    s = s.replace("  verb: {\n", SNABB + "  verb: {\n", 1)
    if "Tryck på" in s or "menyn" in s:
        rester = [r.strip()[:90] for r in s.splitlines() if "Tryck på" in r or "menyn" in r]
        print("Obs, klicktexter kvar:\n  " + "\n  ".join(rester))
    UT.parent.mkdir(exist_ok=True)
    UT.write_text(s, encoding="utf-8")
    print(f"Skrev {UT}")


if __name__ == "__main__":
    main()
