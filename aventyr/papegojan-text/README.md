# Papegojan som visste för mycket, textversionen

Samma fall som [`aventyr/papegojan`](../papegojan/), men du skriver kommandon i stället för att klicka. Spela på [jukitor.github.io/the-game/aventyr/papegojan-text](https://jukitor.github.io/the-game/aventyr/papegojan-text/).

Skriv korta meningar på svenska, till exempel `undersök skrivbordet`, `prata med bartendern` eller `använd paraplyet på stegen`. `hjälp` visar fler exempel och `ledtråd` hjälper dig om du kör fast.

`aventyr.js` här är **genererad** från klickversionens `aventyr/papegojan/aventyr.js` av `aventyr/papegojan/verktyg/gor_textversion.py`, som byter ut det som bara gäller klick (introt, hjälpen, ledtrådarnas formuleringar) och lägger till snabbknappar. Ändra alltid i klickversionen och kör skriptet igen. Bilder och ljud lånas från `aventyr/papegojan/` och `aventyr/mopsen/` (`bildmapp` och `ljudmapp`).

**Varning för spoilers:** `aventyr.js` och `aventyr/papegojan/verktyg/texttest.js` innehåller lösningen.

```
python3 aventyr/papegojan/verktyg/gor_textversion.py
python3 motor/verktyg/bygg.py papegojan-text
node aventyr/papegojan/verktyg/texttest.js     # spelar hela fallet genom att skriva (kräver Playwright)
```
