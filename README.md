# Mopsen som försvann

Ett humoristiskt textäventyr på svenska i samma anda som 80-talets Magnetic Scrolls-spel (The Pawn, Guild of Thieves, Corruption).

Grand Harbor, 1947. Du är en luggsliten privatdetektiv utan pengar och utan kaffe. Rikedomsänkan Cornelia Pettigrews prisbelönta mops Lord Waffles har blivit kidnappad strax före den stora hundutställningen. Leta ledtrådar, åk tunnelbana genom staden och få hem hunden.

## Spela

Öppna `index.html` i en webbläsare. Spelet behöver ingen server och ingen installation.

## Kommandon

| Exempel | Vad det gör |
|---|---|
| `titta` eller `l` | Beskriver platsen du är på |
| `undersök rocken` eller `x rock` | Tittar närmare på något |
| `ta kortet`, `ta allt` | Plockar upp saker |
| `släpp dyrken` | Lägger ner något |
| `i` eller `inventarie` | Visar vad du bär på |
| `upp`, `ner`, `in`, `ut` | Går åt ett håll |
| `åk till chinatown` | Åker tunnelbana (på en perrong) |
| `öppna lådan`, `läs brevet` | Öppnar och läser |
| `ge korven till bruno` | Ger något till någon |
| `visa fotot för benny` | Visar något för någon |
| `prata med portiern` | Pratar med någon |
| `ledtråd` | Ger en ledtråd om du kör fast |
| `bild` | Stänger av eller slår på bilderna |
| `poäng`, `spara`, `ladda`, `omstart` | Övrigt |

Pil upp i inmatningsfältet hämtar förra kommandot.

## Platser

Ditt kontor, Main Street, Park Avenue, Pettigrews takvåning, Chinatown, restaurangen Golden Dragon, Pir 9 och Lager 13. Tunnelbanan har fyra stationer: Main Street, Park Avenue, Chinatown och Pir 9.

## Bilder

Miljöerna illustreras med pixelbilder i retrostil: 192 × 120 pixlar, 16 färger och ordnad dithering. Bilderna ritas med kod i `verktyg/rita_bilder.py` (Python med Pillow och NumPy), en funktion per miljö. Alla bilder delar samma palett.

Hittills finns tre bilder:

- **Ditt kontor**: neonskylten HOTEL tänds bokstav för bokstav, regnet rinner, cigarettröken stiger och telefonsvararens lampa blinkar.
- **Main Street**: regn över gatan, ånga från Sals korvkastrull och en dinerskylt med ett glappande N.
- **Park Avenue**: Pettigrew Towers med snurrande karuselldörr, portiern Reginald, en pickande duva med fluga, ett fönster som tänds och släcks samt duggregn.

Texter i bilderna skrivs med ett litet pixeltypsnitt (`TYPSNITT` och `text()` i ritskriptet).

```
python3 verktyg/rita_bilder.py   # ritar om bilderna och animationerna
python3 verktyg/bygg.py          # bygger index.html
```

För att koppla en bild till en plats lägger du till `bild: "namn"` på rummet i `ROOMS`.

### Animationer

En bild kan ha enkla animationer, till exempel en neonskylt som tänds bokstav för bokstav eller regn som rinner på en ruta. Ritfunktionen tar emot ett läge (`v`), och i `SCENER` anger man vilka lägen som ska visas och hur länge. Skriptet ritar bilden en gång per läge och sparar bara de pixlar som skiljer sig från grundbilden. Datan skrivs in i `spel.html` mellan markörerna `BILDDATA-START` och `BILDDATA-SLUT`. Spelet ritar sedan grundbilden på en canvas och lägger på de ändrade pixlarna i takt.

Med `animStyr` på ett rum kan spelet låsa en animation på en viss ruta. Telefonsvararens lampa slutar till exempel blinka när man har lyssnat på meddelandet.

Den som har valt minskad rörelse i operativsystemet ser bara stillbilderna.

## Filer

- `spel.html`: källan till spelet (HTML, CSS och JavaScript), utan `<head>` så att den också kan publiceras som Claude-artefakt.
- `index.html`: den fristående sidan som GitHub Pages visar. Den byggs från `spel.html` med `python3 verktyg/bygg.py`. Redigera inte den direkt.
- `bilder/`: pixelbilderna.
- `verktyg/`: skripten som ritar bilderna och bygger `index.html`.

Spelvärlden (rum, föremål och poäng) ligger överst i skriptet i objekten `ROOMS`, `OBJ` och `SCORES`, så det är lätt att bygga ut med fler platser och pussel.
