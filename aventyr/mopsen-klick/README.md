# Mopsen som försvann, klickversionen

Samma fall som [`aventyr/mopsen`](../mopsen/), men spelet styrs genom att peka och klicka i bilderna i stället för att skriva. Spela på [jukitor.github.io/the-game/aventyr/mopsen-klick](https://jukitor.github.io/the-game/aventyr/mopsen-klick/).

Tryck på saker i bilden för att få en meny med vad du kan göra, till exempel undersöka, ta, öppna, prata med, ge eller visa. Det du bär visas under texten, och där kan du välja "Använd …" för att använda en sak på något annat. Tryck på en tom del av bilden för att se dig omkring. Under MENY finns hjälp, ledtrådar, poäng, sparning och ljud.

- `aventyr.js`: konfigurationen med `lage: "klick"`. Den bygger på textversionens konfiguration, med ett fyrtiotal extra föremål som bara finns för stämningens skull och texter anpassade för klick.
- `bilder/`: bilderna med klickytor och de utgångar som ritats in för klickläget.
- `verktyg/rita_bilder.py`: ritar bilderna och klickytorna.
- `verktyg/klicktest.js`: spelar hela spelet till 100/100 på en simulerad iPhone med bara tryck (`node aventyr/mopsen-klick/verktyg/klicktest.js`, kräver Playwright).
- Musik och ljud lånas från `aventyr/mopsen/ljud/` (`ljudmapp` i `aventyr.js`).

Bygg med `python3 motor/verktyg/bygg.py mopsen-klick`.
