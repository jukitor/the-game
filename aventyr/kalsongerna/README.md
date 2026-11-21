# Borgmästarens långkalsonger

Fall nummer tre för detektiven från [Mopsen som försvann](../mopsen/) och [Papegojan som visste för mycket](../papegojan/). Ett peka-och-klicka-äventyr på svenska. Spela på [jukitor.github.io/the-game/aventyr/kalsongerna](https://jukitor.github.io/the-game/aventyr/kalsongerna/).

Grand Harbor, 1947, i valtider. Staden har vuxit: fler gator, fler kvarter och fler figurer att prata med. Tryck på saker i bilden för att få en meny med vad du kan göra. När du pratar med någon trycker du på det du vill svara, och ibland spelar det roll vad du säger. Under MENY finns hjälp, ledtrådar, poäng, sparning och ljud.

**Varning för spoilers:** `aventyr.js` och `verktyg/klicktest.js` innehåller lösningen.

- `aventyr.js`: konfigurationen (`lage: "klick"`), med samtal (`samtal`).
- `bilder/`: bilderna med klickytor. Platser från tidigare fall ritas med `aventyr/papegojan/verktyg/rita_bilder.py` med nya utgångar ovanpå; de nya platserna finns i `verktyg/scener_a.py` till `scener_e.py`. Allt ritas av `verktyg/rita_bilder.py`.
- `ljud/`: de nya ljuden, skapade av `verktyg/skapa_ljud.py`. Övriga ljud lånas från `aventyr/papegojan/ljud/` och `aventyr/mopsen/ljud/`.
- `verktyg/klicktest.js`: spelar hela spelet till full poäng på en simulerad iPhone med bara tryck (kräver Playwright).

Bygg med `python3 motor/verktyg/bygg.py kalsongerna`.
