# Papegojan som visste för mycket

Fall nummer två för detektiven från [Mopsen som försvann](../mopsen/). Ett peka-och-klicka-äventyr på svenska. Spela på [jukitor.github.io/the-game/aventyr/papegojan](https://jukitor.github.io/the-game/aventyr/papegojan/).

Grand Harbor, 1947, tre veckor efter mopsfallet. Ett telegram under dörren, en nattklubbssångerska i nöd och en radiosändning klockan nio. Staden är densamma, kontoret också (nästan), och tunnelbanan har fått en ny station.

Tryck på saker i bilden för att få en meny med vad du kan göra. Det du bär visas under texten, och där kan du välja "Använd …" för att använda en sak på något annat. Under MENY finns hjälp, ledtrådar, poäng, sparning och ljud.

**Varning för spoilers:** `aventyr.js` och `verktyg/klicktest.js` innehåller lösningen.

- `aventyr.js`: konfigurationen (`lage: "klick"`).
- `bilder/`: bilderna med klickytor. Platserna från förra fallet ritas med `aventyr/mopsen-klick/verktyg/rita_bilder.py`, ibland med ändringar ovanpå, och de nya finns i `verktyg/scener_a.py`, `scener_b.py` och `scener_c.py`. Allt ritas av `verktyg/rita_bilder.py`.
- `ljud/`: de nya ljuden, skapade av `verktyg/skapa_ljud.py`. Musiken och övriga ljud lånas från `aventyr/mopsen/ljud/` (`ljudmapp` i `aventyr.js`).
- `verktyg/klicktest.js`: spelar hela spelet till full poäng på en simulerad iPhone med bara tryck (`node aventyr/papegojan/verktyg/klicktest.js`, kräver Playwright).

Det finns också en textversion i [`aventyr/papegojan-text/`](../papegojan-text/). Den genereras från den här mappens `aventyr.js` av `verktyg/gor_textversion.py`, så ändra alltid här och kör skriptet igen. `verktyg/texttest.js` spelar igenom textversionen.

Bygg med `python3 motor/verktyg/bygg.py papegojan papegojan-text`.
