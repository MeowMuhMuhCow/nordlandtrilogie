# Das Schwarze Auge: Die Nordlandtrilogie – Gemeinsames Paket

Alles an einem Ort für alle drei Teile der Nordlandtrilogie:
1. **Die Schicksalsklinge** (1992)
2. **Sternenschweif** (1994)
3. **Schatten über Riva** (1996)

> **Voraussetzung:** Du benötigst die **deutsche GOG-Fassung** des jeweiligen Spiels. Dieses Paket enthält **keine** Original-Spieldaten.

---

## Schnellstart

1. Doppelklicke auf **`NORDLANDTRILOGIE.EXE`**.
2. Falls deine GOG-Installationen nicht automatisch erkannt wurden, ziehe den jeweiligen Spielordner einfach mit der Maus ins Starter-Fenster (oder klicke auf **„Ordner wählen...“**).
3. Wähle direkt auf der Spielkarte einen der **drei Wege**:
   - **Spielen (Windows):** Startet die neue Windows-Fassung direkt ohne DOSBox im originalgetreuen 4:3-Bild (Vollbild oder 2x–5x-Fenster, mit CD-Musik, Vorspann und optionalem Live-Probenlog).
   - **DOS-Fassung patchen / In DOSBox spielen:** Erzeugt aus deiner deutschen GOG-Fassung fehlerbereinigte DOS-Programme (`Wichtige Fixes` und `Alle Fixes`), ohne deine Originaldateien zu verändern. Danach startet **„In DOSBox spielen“** die gewählte DOS-Fassung (`Original`, `Wichtige` oder `Alle`, inkl. Anzeige, Intro und Probenlog) direkt über deine GOG-DOSBox.
   - **Im Browser spielen:** Öffnet die Online-Fassung im Standardbrowser mit der gewählten Fix-Stufe (`?stufe=original|wichtig|alles`) und Intro-Einstellung.

### Welche Option gilt auf welchem Weg?

| Option auf der Karte | Spielen (Windows) | In DOSBox spielen (DOS) | Im Browser spielen |
|---|---|---|---|
| **Fixes** (`Original` / `Wichtige` / `Alle`) | Startet `*_ORIGINAL.EXE`, `*_FIX_WICHTIG.EXE` oder `*_FIX_ALLES.EXE` | Startet `SCHICKM.EXE` / `SCHWEIF.EXE` / `RIVA.EXE` (`Original`) bzw. `*_FIX_WICHTIG.EXE` / `*_FIX_ALLES.EXE` (bei DSA 1 inkl. Original- bzw. gepatchter `SCHICK.DAT`) | Übergibt `?stufe=original`, `?stufe=wichtig` oder `?stufe=alles` an die Web-Seite |
| **Anzeige** (`Vollbild` / `Fenster 2×..5×`) | Übergibt `--fenster=vollbild` bzw. `2..5` | Setzt in DOSBox `fullscreen=true` (`fullresolution=desktop`) bzw. `windowresolution=640x480..1600x1200` (4:3, `output=openglnb`, `aspect=true`) | Wird auf der Web-Seite selbst gesteuert (Vollbild-Schaltfläche im Browser) |
| **Intro** (`ein` / `aus`) | Übergibt `--intro` bzw. `--kein-intro` | Startet mit Vorspann (`INTRO.EXE`, `SCHWEIF.EXE -x`, `RIVA.EXE`) bzw. überspringt ihn (`SCHWEIF.EXE`, `RIVA.EXE LASTGAME`) | Übergibt bei ausgeschaltetem Intro `&intro=0&kein_intro=1` an die Web-Seite |
| **Flüssig drehen** (nur *Die Schicksalsklinge*, `ein` / `aus`) | Beim Drehen schwenkt die Ansicht weich statt hart um 90 Grad (ab `Wichtige`; bei `Original` nie) | Nicht möglich (Originalprogramm) | Immer an (ab `Wichtige`) |
| **Probenlog** (`ein` / `aus`) | Legt bei `Wichtige` / `Alle` `PROBEN.CSV` an und öffnet das Live-Probenlog-Fenster (bei `Original` gedimmt, da die unveränderte Original-Engine von 1992–1996 keinen Probenlog-Hook besitzt) | Legt bei `Wichtige` / `Alle` `PROBEN.CSV` an und öffnet das Live-Probenlog-Fenster (bei `Original` gedimmt) | Wird direkt über die Schaltfläche **„Probenlog“** oben auf der Web-Seite geöffnet |

---

## Ordnerübersicht

- `NORDLANDTRILOGIE.EXE` – Gemeinsamer Starter für alle drei Spiele (`F1` = Hilfe, `F5` = Schnellstart)
- `Schicksalsklinge/`, `Sternenschweif/`, `Riva/` – Jeweils aufgeteilt in:
  - `Nativ/` – Windows-Fassung (auch direkt per `*_starten_*.bat` startbar)
  - `DOS/` – Bugfix-Patcher (`PATCHEN.bat`) und DOSBox-Starter (`*_STARTEN.bat`)
  - `Browser/` – Link zur Online-Fassung
- `LIZENZEN.md` – Übersicht der Lizenzen aller Teile und verwendeten Bibliotheken

---

## Spielstände – wo liegen sie, und passen sie zueinander?

| Fassung | Ordner der Spielstände |
|---|---|
| Windows: Schicksalsklinge, Sternenschweif | Wie im Original im GOG-Spielordner. Ist der Ordner schreibgeschützt, im Ordner `Spielstaende` neben dem Programm (z. B. `Sternenschweif\Nativ\Spielstaende`). |
| Windows: Schatten über Riva | Immer im Ordner `Spielstaende` neben dem Programm: `Riva\Nativ\Spielstaende` (der GOG-Ordner wird nie verändert). |
| DOS (gepatcht) | Im Zielordner, den der Starter beim Patchen anzeigt – dort liegen die Spielstände wie im Original. |
| Browser | Im Browser selbst. Mit **„Spielstände sichern (Zip)“** und **„Spielstände einspielen“** oben auf der Seite lassen sie sich mitnehmen. |

**Alle Fassungen benutzen das unveränderte Original-Spielstandformat.** Ein Spielstand lässt sich zwischen GOG-Original, gepatchter DOS-Fassung, Windows-, Linux- und Browser-Fassung weiterspielen: einfach die Spielstand-Dateien (`*.GAM`, bei Sternenschweif und Riva im Unterordner `GAMES`) und, falls vorhanden, die Namensliste `GAMES.NAM` in den Spielstand-Ordner der anderen Fassung kopieren, im Browser über „Spielstände einspielen“. Auch die Fix-Stufe (Original, Wichtige, Alle) darf jederzeit gewechselt werden.

---

## Wichtige Tasten im Spiel (Windows-Fassung)

- **`Alt + Enter`** – Zwischen Vollbild und Fenster umschalten
- **`Tab`** – Fenstergröße durchschalten (*Schicksalsklinge* & *Sternenschweif*)
- **`F10`** – Musikmodus wechseln (*Schicksalsklinge* & *Sternenschweif*)
- **`F11` / `F12`** – Musik leiser / lauter

---

## Quelltext & Fehler melden

- **Gesamtpaket & Starter:** https://github.com/MeowMuhMuhCow/nordlandtrilogie
- **Teil 1 – Die Schicksalsklinge:** https://github.com/MeowMuhMuhCow/schicksalsklinge
- **Teil 2 – Sternenschweif:** https://github.com/MeowMuhMuhCow/sternenschweif
- **Teil 3 – Schatten über Riva:** https://github.com/MeowMuhMuhCow/riva
