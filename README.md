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
| `ljud`, `musik` | Stänger av eller slår på allt ljud, eller bara musiken |
| `poäng`, `spara`, `ladda`, `omstart` | Övrigt |

Pil upp i inmatningsfältet hämtar förra kommandot.

## Platser

Ditt kontor, Main Street, Park Avenue, Pettigrews takvåning, Chinatown, restaurangen Golden Dragon, Pir 9 och Lager 13. Tunnelbanan har fyra stationer: Main Street, Park Avenue, Chinatown och Pir 9.

## Bilder

Miljöerna illustreras med pixelbilder i retrostil: 192 × 120 pixlar, 16 färger och ordnad dithering. Bilderna ritas med kod i `verktyg/rita_bilder.py` (Python med Pillow och NumPy), en funktion per miljö. Alla bilder delar samma palett.

Alla platser har en egen bild:

- **Ditt kontor**: neonskylten HOTEL tänds bokstav för bokstav, regnet rinner, cigarettröken stiger och telefonsvararens lampa blinkar.
- **Main Street**: regn över gatan, ånga från Sals korvkastrull och en dinerskylt med ett glappande N.
- **Park Avenue**: Pettigrew Towers med snurrande karuselldörr, portiern Reginald, en pickande duva med fluga, ett fönster som tänds och släcks samt duggregn.
- **Pettigrews takvåning**: kristallkronan glittrar, fru Pettigrew snyftar i sin spetsnäsduk och ett litet moln regnar inomhus på en palm. När Lord Waffles är tillbaka sitter han i korgen och frun är lycklig.
- **Chinatown**: lyktor som gungar i vinden, GOLDEN DRAGON-skylten som tänds bokstav för bokstav, ånga från ett matstånd och regn.
- **Golden Dragon**: lågor från Bennys wokpanna, karpen som simmar uttråkad fram och tillbaka och en vinkande lyckokatt.
- **Pir 9**: dimma som driver, fyrens ljuskägla, vågor och fartyget i hamnen. Bruno försvinner när han fått sin korv, och dörren står öppen när den är dyrkad.
- **Lager 13**: dammkorn i ljusstrimman och Lord Waffles som morrar i buren. Han kommer ut när han fått kex och är borta när du tagit honom.
- **Perrongen vid Main Street**: smutsvitt kakel med mosaikskylt, jordnötsskal på golvet, en man som sover under en tidning och snarkar, och en glödlampa som glappar.
- **Perrongen vid Park Avenue**: marmor och mässing, blankt golv, en ormbunke och fiolspelaren som spelar Bach med noter som svävar uppåt.
- **Perrongen vid Chinatown**: rött kakel och papperslyktor, ett tåg med öppen dörr och folk med matkassar fulla av purjolök och ingefära.
- **Perrongen vid Pir 9**: slutstationen med trasigt kakel, en stoppbock vid tunneln, ett lysrör som blinkar SOS på morse, vatten som droppar i en pöl och en råtta som springer längs kanten.

Texter i bilderna skrivs med ett litet pixeltypsnitt (`TYPSNITT` och `text()` i ritskriptet).

```
python3 verktyg/rita_bilder.py   # ritar om bilderna och animationerna
python3 verktyg/bygg.py          # bygger index.html
```

För att koppla en bild till en plats lägger du till `bild: "namn"` på rummet i `ROOMS`.

### Animationer

En bild kan ha enkla animationer, till exempel en neonskylt som tänds bokstav för bokstav eller regn som rinner på en ruta. Ritfunktionen tar emot ett läge (`v`), och i `SCENER` anger man vilka lägen som ska visas och hur länge. Skriptet ritar bilden en gång per läge och sparar bara de pixlar som skiljer sig från grundbilden. Datan skrivs in i `spel.html` mellan markörerna `BILDDATA-START` och `BILDDATA-SLUT`. Spelet ritar sedan grundbilden på en canvas och lägger på de ändrade pixlarna i takt.

Med `animStyr` på ett rum kan spelet låsa en animation på en viss ruta. Telefonsvararens lampa slutar till exempel blinka när man har lyssnat på meddelandet. Om en animation i `SCENER` har ett fjärde värde (`slinga`) loopar bara de första rutorna, och de övriga visas bara när spelet väljer dem. Så visas till exempel Bruno, Lord Waffles och lagerdörren i rätt läge beroende på hur långt man kommit.

Animationsrutorna packas som base64 med tre byte per ändrad pixel, så att spelfilen hålls liten.

Den som har valt minskad rörelse i operativsystemet ser bara stillbilderna.

## Ljud och musik

Allt ljud skapas med kod i webbläsaren (Web Audio), så spelet behöver inga ljudfiler. Ljudmotorn ligger i `spel.html` i avsnittet `LJUD` (objektet `Ljud`).

- **Musik:** en långsam deckarjazz i c-moll med gående kontrabas, visp, ridecymbal, pianoackord och en dämpad trumpet. Varannan gång spelas en annan melodi.
- **Miljöljud per plats:** regn mot fönstret på kontoret, regn och bilar som tutar på Main Street, duvor på Park Avenue, en klocka som tickar i takvåningen, sorl och cykelklockor i Chinatown, fräsande wok och klirr på Golden Dragon, vågor, måsar och mistlurar vid Pir 9, knarr och en morrande mops i lagret och tunnelbanebrus på perrongerna. På Park Avenues perrong spelar fiolspelaren brutna ackord i Bachs anda, och då tonas jazzen ner.
- **Effekter:** telefonsvararen (klick, bandspolning, pip och en mumlande röst), spärren, tunnelbaneresan, lådan, kassaapparaten, Brunos mage, mopsen som morrar och skäller, låset som dyrkas upp, lyckokakan, hissen, poängljud och en slutfanfar.

Ljudet startar första gången man skriver eller trycker, eftersom webbläsare inte tillåter ljud innan dess. Kommandot `ljud` (eller knappen **Ljud**) stänger av och slår på allt ljud, och `musik` stänger av och slår på musiken. Valen sparas i webbläsaren. Ljudet pausas när fliken inte syns.

## Filer

- `spel.html`: källan till spelet (HTML, CSS och JavaScript), utan `<head>` så att den också kan publiceras som Claude-artefakt.
- `index.html`: den fristående sidan som GitHub Pages visar. Den byggs från `spel.html` med `python3 verktyg/bygg.py`. Redigera inte den direkt.
- `bilder/`: pixelbilderna.
- `verktyg/`: skripten som ritar bilderna och bygger `index.html`.

Spelvärlden (rum, föremål och poäng) ligger överst i skriptet i objekten `ROOMS`, `OBJ` och `SCORES`, så det är lätt att bygga ut med fler platser och pussel.
