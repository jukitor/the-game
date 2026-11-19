# Mopsen som försvann

Ett humoristiskt textäventyr på svenska i samma anda som 80-talets Magnetic Scrolls-spel (The Pawn, Guild of Thieves, Corruption).

Grand Harbor, 1947. Du är en luggsliten privatdetektiv utan pengar och utan kaffe. Rikedomsänkan Cornelia Pettigrews prisbelönta mops Lord Waffles har blivit kidnappad strax före den stora hundutställningen. Leta ledtrådar, åk tunnelbana genom staden och få hem hunden.

Det här är det första äventyret för spelmotorn i `motor/`. Allt som hör till fallet ligger i den här mappen:

- `aventyr.js`: konfigurationen med platser, föremål, personer, texter, pussel (regler), poäng, ledtrådar, startskärm och ljud.
- `bilder/`: pixelbilderna, startskärmens bild och `bilddata.json` (animationerna).
- `ljud/`: musik, miljöljud och effekter som mp3, plus `slingor.json` och `texttider.json`.
- `verktyg/`: skripten som ritar bilderna (`rita_bilder.py`, `rita_splash.py`) och skapar ljuden (`skapa_ljud.py`).
- `index.html`, `data.js`, `spel.html`: byggs av `motor/verktyg/bygg.py`. Redigera dem inte för hand.

## Kommandon

| Exempel | Vad det gör |
|---|---|
| `titta` eller `t` | Beskriver platsen du är på |
| `undersök rocken` eller `u rock` | Tittar närmare på något |
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

## Startskärm

Spelet börjar med en startskärm: en målerisk noir-illustration av en detektiv sedd bakifrån under en gatlykta i regnet, med loggan **Mopsen som försvann**. Ovanpå bilden faller animerat regn. Bilden ligger kvar tills man klickar eller trycker på den. Klicket startar spelet och jazzen.

Bilden ritas av `verktyg/rita_splash.py` (Python med Pillow och NumPy) i 3200 × 1800 pixlar, i lager med ljus, dimma, regn, spegelbilder i våt asfalt, filmkorn och vinjettering. Den sparas som `bilder/splash.jpg` (liggande) och `bilder/splash_staende.jpg` (stående, för mobil).

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

Texter i bilderna skrivs med motorns lilla pixeltypsnitt (`TYPSNITT` och `text()` i `motor/verktyg/pixelbild.py`).

```
python3 aventyr/mopsen/verktyg/rita_bilder.py   # ritar om bilderna och animationerna
python3 motor/verktyg/bygg.py mopsen             # bygger spelet
```

En plats får sin bild med `bild: "namn"` i `aventyr.js`.

### Animationer

En bild kan ha enkla animationer, till exempel en neonskylt som tänds bokstav för bokstav eller regn som rinner på en ruta. Ritfunktionen tar emot ett läge (`v`), och i `SCENER` anger man vilka lägen som ska visas och hur länge. Skriptet ritar bilden en gång per läge och sparar bara de pixlar som skiljer sig från grundbilden. Datan sparas i `bilder/bilddata.json` och byggs in i spelet av `motor/verktyg/bygg.py`. Spelet ritar sedan grundbilden på en canvas och lägger på de ändrade pixlarna i takt.

Med `animationer` på ett rum i `aventyr.js` kan spelet låsa en animation på en viss ruta. Telefonsvararens lampa slutar till exempel blinka när man har lyssnat på meddelandet. Om en animation i `SCENER` har ett fjärde värde (`slinga`) loopar bara de första rutorna, och de övriga visas bara när spelet väljer dem. Så visas till exempel Bruno, Lord Waffles och lagerdörren i rätt läge beroende på hur långt man kommit.

Animationsrutorna packas som base64 med tre byte per ändrad pixel, så att spelfilen hålls liten.

Den som har valt minskad rörelse i operativsystemet ser bara stillbilderna.

## Ljud och musik

Musiken och ljuden ligger som mp3-filer i `ljud/` och skapas av `verktyg/skapa_ljud.py`.

- **Musik:** en lugn deckarballad i c-moll, 56 slag per minut, där bara kompet spelar: flygel, kontrabas och visp. I andra varvet går basen i fjärdedelar. Melodier för tenorsax och dämpad trumpet finns kvar i skriptet och kan slås på med `SOLISTER = True`. Den är komponerad i skriptet och renderad med samplade instrument från ljudbanken [GeneralUser GS](https://www.schristiancollins.com/generaluser) i FluidSynth, med rumsklang. Stycket är knappt tre minuter långt och loopar sömlöst.
- **Fiolspelaren** på Park Avenues perrong spelar Bachs Preludium i C-dur (BWV 846) som brutna ackord på samplad fiol. Då tonas jazzen ner.
- **Miljöljud per plats:** regn mot kontorsfönstret, regn och bilhorn på Main Street, duggregn och duvor på Park Avenue, golvklocka i takvåningen, regn, sorl och cykelklockor i Chinatown, fräsande wok, sorl och porslin på Golden Dragon, vågor, måsar och mistlur vid Pir 9, knarr och en morrande mops i lagret, och tunnelbanebrus med passerande tåg, droppar och råttor på perrongerna.
- **Effekter:** telefonsvararen (klick, bandspolning, pip och fru Pettigrews meddelande genom en gammal högtalare; orden skrivs ut i takt med rösten, med tider från `ljud/texttider.json`), spärren, tunnelbaneresan, lådan, kassaapparaten, Brunos mage och klunk, mopsen som morrar och skäller, låset som dyrkas upp, lyckokakan, kexpåsen, hissen, poängljud (vibrafon) och en slutfanfar.

Miljöljuden och effekterna byggs med signalbehandling (NumPy och SciPy) och får rumsklang i SoX. Fru Pettigrews röst och sorlet läses in med espeak-ng och filtreras. Slingornas exakta längd sparas i `ljud/slingor.json` och byggs in i spelet, så att det kan loopa dem utan glapp.

Så här skapar du ljuden på nytt (Ubuntu/Debian):

```
sudo apt install fluidsynth sox espeak-ng ffmpeg
pip install mido numpy scipy
python3 aventyr/mopsen/verktyg/skapa_ljud.py   # allt, eller t.ex. bara: musik, fiol, poang, miljo, effekter
python3 motor/verktyg/bygg.py mopsen
```

Skriptet hämtar ljudbanken GeneralUser GS (cirka 30 MB) till `.ljudcache/` första gången.

Ljudet startar första gången man skriver eller trycker, eftersom webbläsare inte tillåter ljud innan dess. Kommandot `ljud` (eller knappen **Ljud**) stänger av och slår på allt ljud, och `musik` stänger av och slår på musiken. Valen sparas i webbläsaren. Ljudet pausas när fliken inte syns. 

### Licenser för ljud

- GeneralUser GS av S. Christian Collins får användas fritt i musikproduktion, även kommersiellt.
- Bachs Preludium i C-dur är fri från upphovsrätt.
- Övriga ljud är skapade från grunden i `verktyg/skapa_ljud.py`.

