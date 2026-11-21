# Spelmotor för textäventyr

En spelmotor för textäventyr på svenska i samma anda som 80-talets Magnetic Scrolls-spel (The Pawn, Guild of Thieves, Corruption): en ordtolkare som förstår korta svenska meningar, pixelbilder med animationer, musik, miljöljud och effekter, repliker som skrivs ut i takt med rösten och en startskärm.

Motorn är generisk. Varje äventyr är en konfiguration med egna bilder och ljud, och alla äventyr använder samma motor. En förbättring av motorn kommer alltså alla äventyr till del.

## Äventyr

| Äventyr | Mapp | Spela |
|---|---|---|
| Mopsen som försvann | [`aventyr/mopsen/`](aventyr/mopsen/) | [jukitor.github.io/the-game](https://jukitor.github.io/the-game/) |
| Mopsen som försvann, klickversionen | [`aventyr/mopsen-klick/`](aventyr/mopsen-klick/) | [jukitor.github.io/the-game/aventyr/mopsen-klick](https://jukitor.github.io/the-game/aventyr/mopsen-klick/) |
| Papegojan som visste för mycket (fall 2, klick) | [`aventyr/papegojan/`](aventyr/papegojan/) | [jukitor.github.io/the-game/aventyr/papegojan](https://jukitor.github.io/the-game/aventyr/papegojan/) |
| Papegojan som visste för mycket (fall 2, text) | [`aventyr/papegojan-text/`](aventyr/papegojan-text/) | [jukitor.github.io/the-game/aventyr/papegojan-text](https://jukitor.github.io/the-game/aventyr/papegojan-text/) |
| Borgmästarens långkalsonger (fall 3, klick) | [`aventyr/kalsongerna/`](aventyr/kalsongerna/) | [jukitor.github.io/the-game/aventyr/kalsongerna](https://jukitor.github.io/the-game/aventyr/kalsongerna/) |

Rotens `index.html` skickar vidare till Mopsen som försvann.

## Struktur

```
motor/                     spelmotorn, gemensam för alla äventyr
  motor.js                 ordtolkare, regler, bilder, animationer, ljud, repliker, startskärm
  motor.css                utseendet
  verktyg/
    bygg.py                bygger ett äventyr: data.js, index.html och spel.html
    pixelbild.py           bibliotek för pixelbilder (rityta, palett, dithering, typsnitt, export av animationer)
    ljudverktyg.py         bibliotek för ljud (MIDI och FluidSynth, signalbehandling, rumsklang, mp3, slingor)
aventyr/<namn>/            ett äventyr
  aventyr.js               konfigurationen (window.AVENTYR)
  bilder/  ljud/           bilder och ljud, med bilddata.json, slingor.json och texttider.json
  verktyg/                 äventyrets egna skript som ritar bilder och skapar ljud
  data.js, index.html, spel.html   byggs av motor/verktyg/bygg.py
```

## Bygga och spela

```
python3 motor/verktyg/bygg.py           # bygger alla äventyr
python3 motor/verktyg/bygg.py mopsen    # bygger ett äventyr
python3 -m http.server                  # öppna sedan http://localhost:8000/aventyr/mopsen/
```

`index.html` i äventyrets mapp laddar motorn direkt från `motor/`. Länkarna har ett versionsnummer (`?v=…`) som räknas ut från filernas innehåll, så att webbläsare och GitHub Pages inte visar en gammal motor ur cachen. Kör därför alltid `bygg.py` efter en ändring i motorn eller äventyret innan du pushar eller publicerar. `bygg.py` skapar också `spel.html`, där motor, äventyr och data är inbakade i en enda fil för publicering som Claude-artefakt.

Ljudfilerna hämtas från webbservern. Öppnar du `index.html` direkt från disken fungerar spelet, men utan ljud.

## Ett nytt äventyr

1. Skapa `aventyr/<namn>/aventyr.js` (utgå gärna från `aventyr/mopsen/aventyr.js`).
2. Rita bilder med `motor/verktyg/pixelbild.py` och skapa ljud med `motor/verktyg/ljudverktyg.py` från äventyrets egna skript i `aventyr/<namn>/verktyg/`. Bilder och ljud är valfria: en plats utan `bild` visar ingen bildruta, och utan `ljud` blir det tyst.
3. Kör `python3 motor/verktyg/bygg.py <namn>`.

## Konfigurationen

`aventyr.js` definierar `window.AVENTYR`. Ett minimalt äventyr:

```js
window.AVENTYR = {
  id: "fyren", titel: "Fyren", start: "strand",
  intro: [{ text: "Fyren", klass: "banner" }, "Du vaknar på en strand."],
  rum: {
    strand: { namn: "Stranden", beskrivning: "Sand, tång och en fyr i norr.", utgangar: { n: "fyr" } },
    fyr: { namn: "Fyren", beskrivning: "En låst dörr.", utgangar: { s: "strand" },
      passage: [{ om: { inteBar: "nyckel" }, stopp: true, gor: ["Dörren är låst."] }],
      vidIntrade: [{ gor: [{ poang: "fyr" }, { stampel: "Slut" }, { slutsummering: true }, { spelSlut: true }] }] },
  },
  objekt: {
    nyckel: { namn: ["nyckel", "nyckeln"], kort: "en rostig nyckel", plats: "strand", beskrivning: "Rostig men hel." },
  },
  regler: [],
  poang: { fyr: [10, "kommit in i fyren"] },
  ledtradar: [{ om: { inteBar: "nyckel" }, text: "Titta efter något på stranden." }, { text: "Gå norrut." }],
};
```

### Översikt

| Nyckel | Innehåll |
|---|---|
| `id` | Används för sparade spel och inställningar i webbläsaren |
| `titel`, `start` | Spelets namn och startplats |
| `lage` | `"text"` (standard: spelaren skriver kommandon) eller `"klick"` (peka och klicka, se nedan). Bestäms av den som gör spelet |
| `ljudmapp` | Låna ljud från en annan mapp, t.ex. `"../mopsen/ljud/"`, eller flera: `["../ett/ljud/", "../annat/ljud/"]` (den första går före). Äventyrets egna ljud i `ljud/` går före de lånade |
| `bildmapp` | Låna bilderna (och `bilddata.json`) från ett annat äventyr, t.ex. `"../papegojan/bilder/"`. Används av en textversion som delar bilder med en klickversion |
| `intro` | Texter när spelet börjar: strängar eller `{ text, klass }` där klass kan vara `banner` eller `sys` |
| `startskarm` | `{ bild, bildStaende, alt, ort, titel, under, regn }`. Utan den startar spelet direkt |
| `rum` | Platserna, se nedan |
| `objekt` | Föremål och personer, se nedan |
| `regler` | Pussel och särskilda svar, se nedan |
| `handlingar` | Namngivna listor med handlingar som flera regler kan köra med `{ kor: "namn" }` |
| `samtal` | Samtal där spelaren väljer vad hen svarar, se nedan |
| `passager` | Namngivna passageregler som flera rum kan dela (`passage: "namn"`) |
| `verb` | Egna verb: `{ köp: ["köp", "beställ"], dyrka: ["dyrka", "lås upp"] }`. Verb på två ord fungerar |
| `alias` | Kommandon som skrivs om: `{ betala: "köp korv" }` |
| `resor` | Resor mellan stationer, t.ex. tunnelbana: `{ verb, ljud, stationer: { rum: { namn, ord } }, resetexter, texter }` |
| `poang`, `maxPoang` | `{ nyckel: [poäng, "beskrivning i supinum"] }`. Max räknas ut om det saknas |
| `rangar` | `[[minsta poäng, "Rang"], ...]` från högst till lägst |
| `ledtradar` | `[{ om, text }]`. Den första vars villkor stämmer visas |
| `texter` | Byter ut motorns standardtexter, t.ex. `ingenUtgang`, `lyssna`, `vanta`, `hjalp`, `spelSlut` (se `TEXTER` i `motor.js`) |
| `snabbknappar` | `[["Titta", "titta"], ...]` under inmatningsfältet |
| `ljud` | `{ musik, effektvolym, forladda, miljo: { rum: { slingor: [[fil, volym]], handelser: [[fil, sekunder emellan, volym, villkor]], dampaMusik } } }` |

### Rum

```js
kontor: {
  namn: "Ditt kontor",
  beskrivning: ["Grundtext.", { om: { inteFlagga: "svarare" }, text: " Telefonsvararen blinkar." }],
  utgangar: { ner: "gata", ut: "gata" },      // n, s, ö, v, upp, ner, in, ut
  kortBeskrivning: [                           // valfri: visas när man kommer tillbaka hit (TITTA visar alltid hela)
    { om: { inteFlagga: "svarare" }, text: "Ditt kontor. Telefonsvararen blinkar fortfarande." },
    "Ditt kontor. Allt är som förut.",          // delar utan villkor växlar i tur och ordning
    "Tillbaka på kontoret. Räkningarna har inte betalat sig själva.",
  ],
  ord: ["kontor", "kontoret"],                 // för "gå till kontoret"
  grupp: "station",                            // valfri grupp, t.ex. för föremål som finns överallt i gruppen
  bild: "kontor",                              // bilder/kontor.png och dess animationer
  animationer: { lampa: [{ om: { flagga: "svarare" }, ram: 1 }] },   // lås en animation på en ruta
  lukt: "Kaffe och damm.",
  passage: [{ om, stopp, gor }],               // körs när spelaren försöker gå in hit; stopp: true hindrar
  vidIntrade: [{ om, gor }],                   // körs efter att spelaren kommit in (den första som passar)
}
```

Första gången spelaren kommer till en plats visas hela `beskrivning`. Vid senare besök visas `kortBeskrivning` om platsen har en. Delar med villkor som stämmer går före delar utan villkor, och bland dem som passar växlar motorn i tur och ordning, så att samma text inte kommer två gånger i rad. TITTA (och ett tryck på en tom del av bilden i klickläget) visar alltid hela beskrivningen.

### Föremål och personer

```js
lada: {
  namn: ["låda", "lådan"], kort: "en låda",    // orden spelaren kan använda, och hur föremålet nämns
  plats: "kontor",                             // rum, "spelare", ett annat föremål eller null (finns inte än)
  beskrivning: "...",                          // sträng eller lista med villkorade delar
  fast: true, person: true,                    // går inte att ta / är en person (ge, visa, prata)
  behallare: true, oppningsbar: true, oppen: false,
  oppnaText, oppnaLjud, redanOppenText, stangText, stangdText,
  lasbar: true, lasText: "...",                // läs visar beskrivningen eller lasText
  grupp: "station", plats: "överallt",          // finns i alla rum i gruppen
  vidTa: [{ poang: "kort" }],                  // handlingar när föremålet tas
}
```

### Regler

En regel ersätter motorns standardsvar när verb, föremål och villkor stämmer. Reglerna prövas i ordning och den första som passar används. `nar: "efter"` körs i stället efter standardsvaret.

```js
{ verb: "ge", objekt: "korv", mottagare: "bruno", om: { inteFlagga: "bruno" }, gor: [
  { flytta: ["korv", "bruno"] }, { satt: "bruno", ljud: "gulp" },
  "Bruno sväljer korven hel.", { poang: "bruno" },
] }
```

Motorns verb: `titta`, `undersök`, `sök`, `ta`, `ta på`, `släpp`, `inventarie`, `öppna`, `stäng`, `läs`, `lyssna`, `ge`, `mata`, `visa`, `prata`, `ät`, `klappa`, `vänta`, `lukta`, `gå` och (med `resor`) `åk`. Äventyrets egna verb från `verb` har inget standardsvar utöver "Det går inte.", så de styrs helt av regler.

**Villkor** (`om`, alla måste stämma): `flagga`, `inteFlagga`, `bar`, `inteBar`, `har` (finns här), `inteHar`, `inom` (här, buret eller i en öppen behållare), `inteInom`, `plats`, `intePlats`, `objektPa: [föremål, plats]`, `inteObjektPa`, `oppen`, `stangd`, `inventarieTom`, `objekt`, `mottagare`, `fras` (true om spelaren skrev något efter verbet), `ord` (ett av orden finns i frasen; `korv*` matchar delord), `inteOrd`, `franGrupp`, `inteFranGrupp`, `fran` (i passager), `poangMinst`, samt `alla`, `nagon` och `inte` för att kombinera.

**Handlingar** (`gor`): en sträng skrivs ut. Ett objekt kan ha `om` och någon av: `text` (kan vara villkorad), `texter` (en lista att växla mellan), `sys`, `stampel`, `flytta` + `till`, `satt`, `nollstall`, `oppna`, `stang`, `lista` (visa innehåll), `poang`, `ljud` + `fordrojning`, `ljudFordrojning` (väntar med poängljudet), `ledtrad`, `beskriv`, `flyttaSpelare`, `ga` (flytta och visa platsen), `utfor` (kör ett annat kommando, räknas inte som drag), `kor` (en namngiven handlingslista), `replik` + `sedan` (orden skrivs ut i takt med en inspelad röst, se nedan), `ejDrag`, `slutsummering` och `spelSlut`.

I texter ersätts `{objekt}`, `{Objekt}`, `{mottagare}`, `{poang}`, `{max}` och `{drag}`.

### Samtal

Ett samtal är ett träd av noder där spelaren väljer vad hen svarar. Svaren visas som knappar direkt efter texten. I textläget är knapparna numrerade, och spelaren kan också skriva siffran. Allt annat spelaren gör avslutar samtalet.

```js
samtal: {
  vakt: { start: "a", noder: {
    a: { text: "\"Lösenord?\"", val: [
      { text: "Sesam, öppna dig.", till: "fel" },
      { text: "Den gyllene draken sover aldrig.", till: "ratt" },
      { text: "Har du sett en man i röd uniform?", om: { flagga: "uniform" }, engang: true, till: "a" },
    ] },
    fel: { text: "Luckan smäller igen.", val: [] },
    ratt: { text: "Dörren går upp.", gor: [{ satt: "losen" }, { poang: "losen" }], val: [] },
  } },
},
```

En nod har `text` (kan vara villkorad), `gor` (handlingar) och `val`. Ett val har `text`, valfritt `om` (visas bara när villkoren stämmer), `engang` (försvinner när det har valts), `gor` och `till` (nästa nod). Ett val utan `till`, eller en nod utan val, avslutar samtalet. Handlingen `{ samtal: "vakt" }` startar ett samtal, `{ samtal: "vakt", nod: "ratt" }` börjar i en viss nod och `{ avslutaSamtal: true }` avslutar det.

### Bilder, animationer och ljud

Bilderna är 192 × 120 pixlar med 16 färger och ritas av äventyrets skript med `motor/verktyg/pixelbild.py`. Scenernas animationer sparas som pixeldiffar i `bilder/bilddata.json`. En animation kan ha en `slinga`, och då loopar bara de första rutorna medan resten väljs av rummets `animationer`.

Ljuden skapas med `motor/verktyg/ljudverktyg.py` och ligger som mp3 i `ljud/`. Slingornas exakta längd (`ljud/slingor.json`) gör att motorn kan loopa dem utan glapp. En replik behöver ljudfilen och tider per mening i `ljud/texttider.json` (`{ "svarare": [[start, slut, "mening"], ...] }`). Handlingen `{ replik: "svarare", sedan: [...] }` spelar ljudet och skriver ut orden i takt med det.

Spelet sparas automatiskt i webbläsaren (localStorage) efter varje drag, och när sidan laddas om fortsätter spelaren där hen var. När spelet är slut eller spelaren börjar om försvinner den automatiska sparningen. SPARA och LADDA är en separat sparning som spelaren själv styr över.

Ljudet startar när spelaren klickar på startskärmen eller gör något första gången, eftersom webbläsare inte tillåter ljud innan dess. Kommandona `ljud` och `musik` stänger av och slår på, och valet sparas.

### Klickläget

Med `lage: "klick"` finns inget inmatningsfält. Spelaren trycker i bilden och väljer i en meny, och varje val blir ett vanligt kommando ("öppna lådan", "ge dollarn till sal") som går genom ordtolkaren och reglerna. Pusslen fungerar alltså likadant i båda lägena. Menyn erbjuder bara allmänna verb för sorten av sak (undersök, ta, öppna, läs, prata med, ge, visa, använd), aldrig lösningen.

- Klickytorna ritas i bilderna: kod inuti `with d.yta("lada"):` blir klickytan för föremålet `lada`, och `d.markera("namn", x0, y0, x1, y1)` markerar en rektangel. `utgang:<riktning>` (t.ex. `utgang:ner`) gör en utgång klickbar. Ljus och skuggor räknas inte in.
- Varje utgång bör synas i bilden. De som inte gör det visas som knappar under texten, så att spelaren aldrig fastnar.
- Föremål kan ha `klicknamn` (namnet i menyn och i kommandot), `klickverb` (extra menyval, t.ex. `["lyssna på"]`) och `utgang` (föremålet är också en utgång, t.ex. en dörr med `utgang: "in"`, som ger menyvalet "Gå in").
- Med `resor.karta: "karta"` ger ett tryck på linjekartan "Åk till …".
- Verbet `använd` (`använd X på Y`) styrs helt av äventyrets regler, t.ex. `{ verb: "använd", objekt: "dyrk", mottagare: "dorr", gor: [{ utfor: "dyrka upp dörren" }] }`.
- En text i `texter` med namnet `<namn>Klick` ersätter `<namn>` i klickläget, t.ex. `spelSlutKlick`.

## Verktyg som behövs för bilder och ljud

```
sudo apt install fluidsynth sox espeak-ng ffmpeg
pip install pillow numpy scipy mido
```

Ljudbanken GeneralUser GS hämtas automatiskt till `.ljudcache/` första gången. Den får användas fritt i musikproduktion, även kommersiellt.
