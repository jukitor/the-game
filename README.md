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
| `poäng`, `spara`, `ladda`, `omstart` | Övrigt |

Pil upp i inmatningsfältet hämtar förra kommandot.

## Platser

Ditt kontor, Main Street, Park Avenue, Pettigrews takvåning, Chinatown, restaurangen Golden Dragon, Pir 9 och Lager 13. Tunnelbanan har fyra stationer: Main Street, Park Avenue, Chinatown och Pir 9.

## Filer

- `index.html`: hela spelet i en fil (HTML, CSS och JavaScript).
- `spel.html`: samma spel utan `<head>`, för publicering som Claude-artefakt.

Spelvärlden (rum, föremål och poäng) ligger överst i skriptet i objekten `ROOMS`, `OBJ` och `SCORES`, så det är lätt att bygga ut med fler platser och pussel.
