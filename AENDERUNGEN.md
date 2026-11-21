# Nordlandtrilogie – Änderungen am Paket und am Starter

Hier steht, was sich am Gesamtpaket und am gemeinsamen Starter `NORDLANDTRILOGIE.EXE` geändert hat. Die Fehlerbehebungen der einzelnen Spiele stehen ausführlich in deren Änderungslisten:

- Die Schicksalsklinge: https://github.com/MeowMuhMuhCow/schicksalsklinge/blob/main/BUGFIXES.md
- Sternenschweif: https://github.com/MeowMuhMuhCow/sternenschweif/blob/main/BUGFIXES.md
- Schatten über Riva: https://github.com/MeowMuhMuhCow/riva/blob/main/BUGFIXES.md

Welche Fassung du gerade hast, zeigt der Starter oben neben dem Titel („Starter 1.2“) und auf jeder Spielkarte hinter dem Erscheinungsjahr („Fanpatch v1.5i“). Ein Klick auf „Fanpatch vX.Y“ öffnet den gesamten Verlauf und alle Fehlerkorrekturen direkt im Starter.

## 21.11.2026 (nachmittags) – Die Schicksalsklinge, Fanpatch v1.5i

- **Gegnerzauber im Probenlog:** Wenn ein Gegner im Kampf zaubert, zeigt das Probenlog jetzt Gegnername, Zauber, Ziel, die Dreifachprobe (Eigenschaften, Werte, Magieresistenz, alle drei W20, Ergebnis) und die Wirkung
- **Gardianum und Feuerbann im Probenlog:** Bei feindlichem *Fulminictus* und *Ignifaxius* ist im Probenlog jetzt sichtbar, wie viele Schadenspunkte *Feuerbann* und *Gardianum* der Helden abfangen, wie viel Schildstärke übrig bleibt und wie viel Endschaden durchkommt

## Starter 1.2 – 21.11.2026

- Fanpatch-Verlauf direkt im Starter: Ein Klick auf „Fanpatch vX.Y“ auf einer Spielkarte öffnet das Verlaufsfenster mit allen Versionen, allen einzelnen Fehlerkorrekturen (nach Spielbereich gruppiert, mit Volltext- und Nummernsuche sowie Filter nach „Alle“, „nur Wichtige“ und „Exploits“) und den Zusatzfunktionen des jeweiligen Spiels
- Jede Version und jede Korrektur lässt sich mit „+“ und „−“ auf- und zuklappen (inkl. „Was war falsch:“ und „So prüfst du es:“ sowie direktem Link auf die Änderungsliste bei GitHub)

## Starter 1.1 – 21.11.2026

- Versionsanzeige: Starter-Version oben im Kopf und im Fenstertitel, auf jeder Spielkarte die Version des Fanpatches
- Diese Änderungsliste liegt jetzt im Paket
- Enthält Die Schicksalsklinge mit Fanpatch v1.5h:
  - 1.5h: Giftflaschen-Raum in der Ruine des Schwarzmagiers und Truhenkammer im Drachenhort wieder rückwärts gehend erreichbar wie im Original
  - 1.5g: Böser Blick im Computerkampf ohne Hänger, Analüs/Odem Arcanum zeigen beim Abbruch wieder die Originalmeldung, männliche Gegner sterben nicht mehr mit Frauenschrei

## 20.11.2026 (abends)

- Sternenschweif in der DOS-Fassung: Maus nicht mehr zu schnell
- Browser: Jedes Spiel hat einen eigenen Spielstand-Speicher. Vorher konnten sich die drei Spiele im Browser gegenseitig Spielstände unterschieben. Alte Spielstände werden beim ersten Start automatisch dem richtigen Spiel zugeordnet
- Sternenschweif im Browser startet wieder (schwarzer Bildschirm behoben)

## 20.11.2026

- Die Schicksalsklinge, Fanpatch v1.5f:
  - Flüssiges Drehen: Die Ansicht schwenkt weich statt hart um 90 Grad (Windows, Linux, Browser und DOS). Im Starter abschaltbar mit dem Haken „Flüssig drehen“
  - Der Mauszeiger flackert beim Laufen nicht mehr (alle Fassungen)
  - Keine Kopierschutzabfrage mehr in den DOS-Fix-Fassungen
- DOS-Fassungen: Mausgeschwindigkeit in DOSBox passt sich der Bildgröße an
- Alle Programme im Paket enthalten keine Originalbytes mehr

## Starter 1.0 – 19.11.2026 (erste Testfassung)

- Ein gemeinsamer Starter für alle drei Teile
- Je Spiel drei Wege: Windows ohne DOSBox, DOS-Fassung patchen und in DOSBox spielen, im Browser spielen. Dazu Linux-Pakete auf der Release-Seite
- Je Spiel einstellbar: Original, Wichtige Fehlerkorrekturen oder Alle Fehlerkorrekturen, Fenster oder Vollbild, Intro, Live-Probenlog. Die Einstellungen gelten für Windows, DOS und, soweit möglich, den Browser
- Die GOG-Ordner werden automatisch gefunden, sonst Spielordner oder Zip ins Fenster ziehen
- Titelbilder der Spiele werden aus den eigenen Spieldaten gelesen
- Ist der GOG-Ordner schreibgeschützt, legt der Starter zum Patchen eine Kopie an. Die Originaldateien bleiben immer unverändert
- Spielstände bleiben im Format des Originals und laufen in allen Fassungen weiter
