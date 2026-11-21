#!/usr/bin/env python3
"""
fanpatch_daten.py - Erzeugt aus den BUGFIXES.md-Aenderungslisten der drei Spiele
die Verlaufsdateien fanpatch_<spiel-id>.json (UTF-8) fuer den Starter 1.2:
  - Starter/fanpatch_<spiel-id>.json
  - Starter/trilogie/Nordlandtrilogie/_starter/fanpatch_<spiel-id>.json
  - Starter/release/fanpatch_<spiel-id>.json (falls Ordner existiert)
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

STARTER_DIR = Path(__file__).resolve().parent.parent
Q005_DIR = STARTER_DIR.parent
PROJEKTE_DIR = Q005_DIR.parent
Q004_DIR = PROJEKTE_DIR / "Q 004 DSA Sternenschweif"
Q006_DIR = PROJEKTE_DIR / "Q 006 DSA Schatten über Riva"


def clean_md(text: str, keep_newlines: bool = False) -> str:
    """Entfernt Markdown-Formatierungen (**, *, `, <br>, Links) fuer reinen Starter-Text."""
    if not text:
        return ""
    s = text
    if keep_newlines:
        s = re.sub(r"<br\s*/?>", "\n", s, flags=re.I)
    else:
        s = re.sub(r"<br\s*/?>", " ", s, flags=re.I)
    # Markdown-Links [Text](URL) -> Text
    s = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", s)
    # *(...)* Klammerzusatz entfernen
    s = re.sub(r"\*\([^)]*\)\*", "", s)
    # Fettdruck **...** und Kursiv *...*
    s = s.replace("**", "")
    s = re.sub(r"\*([^*]+)\*", r"\1", s)
    # Backticks `...`
    s = s.replace("`", "")
    # Zero-width spaces entfernen
    s = s.replace("\u200b", "")
    if keep_newlines:
        lines = [re.sub(r"[ \t]+", " ", ln).strip() for ln in s.splitlines()]
        return "\n".join(ln for ln in lines if ln)
    s = re.sub(r"\s+", " ", s).strip()
    return s


def extract_herkunft_and_clean(raw_text: str) -> tuple[str, str]:
    """Extrahiert Herkunftsangaben wie *(Bright-Eyes...)* oder Forumsnennungen aus dem Text."""
    herkunft_parts: list[str] = []

    for m in re.finditer(r"\*\(([^)]+)\)\*", raw_text):
        val = m.group(1).strip()
        if val.lower() == "teilweise":
            continue
        herkunft_parts.append(clean_md(val))

    # Auch explizite Nennungen im Satz erkennen, falls noch keine Herkunft vermerkt ist
    if not herkunft_parts:
        m_gem = re.search(
            r"(?:[Gg]emeldet|[Ee]ntdeckt)\s+von\s+([A-Za-z0-9_ÄÖÜäöüß\-]+(?:\s*\([^)]+\)|\s+im\s+Crystals-Forum)?)",
            raw_text,
        )
        if m_gem:
            herkunft_parts.append(clean_md(m_gem.group(0).rstrip(".")))

    cleaned = re.sub(r"\*\([^)]*\)\*", "", raw_text)
    cleaned = cleaned.replace("💰", "").replace("✅", "")
    cleaned = clean_md(cleaned)
    return cleaned, "; ".join(herkunft_parts)


def collect_belegte_daten(
    bugfixes_text: str,
    projekt_dir: Path,
    github_repo_dir: Path | None,
    starter_dir: Path,
) -> dict[str, str]:
    """
    Sammelt ausschliesslich belegte Versionsdaten aus BUGFIXES.md, LOG.md, PROJEKT.md,
    AENDERUNGEN.md und der Git-Historie der Upload-Ordner. Raet niemals.
    """
    dates: dict[str, str] = {}

    # 1. Aus Git-Historie von BUGFIXES.md im Upload-Ordner (älteste zuerst, damit erster Commit einer Version gewinnt)
    if github_repo_dir and (github_repo_dir / ".git").exists():
        try:
            out = subprocess.check_output(
                ["git", "-C", str(github_repo_dir), "log", "--reverse", "--format=%h", "--", "BUGFIXES.md"],
                text=True,
                stderr=subprocess.DEVNULL,
            )
            for h in out.strip().splitlines():
                h = h.strip()
                if not h:
                    continue
                bf = subprocess.check_output(
                    ["git", "-C", str(github_repo_dir), "show", f"{h}:BUGFIXES.md"],
                    text=True,
                    stderr=subprocess.DEVNULL,
                )
                m = re.search(r"\*\*Version\s+([0-9]+\.[0-9]+[a-z0-9.]*)\s+vom\s+(\d{2}\.\d{2}\.\d{4})\*\*", bf)
                if m:
                    ver, dt = m.group(1), m.group(2)
                    dates.setdefault(ver, dt)
        except Exception:
            pass

    # 2. Aus PROJEKT.md im Projektordner
    projekt_md = projekt_dir / "PROJEKT.md"
    if projekt_md.is_file():
        ptxt = projekt_md.read_text(encoding="utf-8", errors="replace")
        m10 = re.search(r"Veröffentlicht am (\d{2}\.\d{2}\.\d{4}):.*Bugfix-Fassung 1\.0", ptxt)
        if m10:
            dates.setdefault("1.0", m10.group(1))
        for m in re.finditer(
            r"^##\s+(?:Stand\s+)?(\d{2}\.\d{2}\.\d{4})[^\n]*?(?:Bugfix(?:-Fassung)?|–)\s*([0-9]+\.[0-9]+[a-z0-9.]*)",
            ptxt,
            re.M,
        ):
            dates.setdefault(m.group(2), m.group(1))

    # 3. Aus LOG.md im Projektordner
    log_md = projekt_dir / "LOG.md"
    if log_md.is_file():
        ltxt = log_md.read_text(encoding="utf-8", errors="replace")
        for m in re.finditer(
            r"\|\s*(\d{4})-(\d{2})-(\d{2})\s+\d{2}:\d{2}\s*\|[^\n]*?(?:Version\s+|`?bugfix-)([0-9]+\.[0-9]+[a-z0-9.]*)",
            ltxt,
        ):
            dt_str = f"{m.group(3)}.{m.group(2)}.{m.group(1)}"
            dates[m.group(4)] = dt_str

    # 4. Aus AENDERUNGEN.md im Trilogie-Paket
    aend_md = starter_dir / "trilogie" / "Nordlandtrilogie" / "AENDERUNGEN.md"
    if aend_md.is_file():
        atxt = aend_md.read_text(encoding="utf-8", errors="replace")
        for m in re.finditer(r"##\s+(\d{2}\.\d{2}\.\d{4})\b.*?\bFanpatch\s+v([0-9]+\.[0-9]+[a-z0-9.]*)", atxt, re.S):
            dates.setdefault(m.group(2), m.group(1))

    # 5. Direkt aus der Kopfzeile der aktuellen BUGFIXES.md
    m_head = re.search(r"\*\*Version\s+([0-9]+\.[0-9]+[a-z0-9.]*)\s+vom\s+(\d{2}\.\d{2}\.\d{4})\*\*", bugfixes_text)
    if m_head:
        dates[m_head.group(1)] = m_head.group(2)

    return dates


def shorten_version_title(ver: str, raw_title: str, body: str, spiel_id: str) -> str:
    """Erzeugt einen praegnanten einzeiligen Versionstitel aus der Ueberschrift bzw. dem Abschnitt."""
    t = clean_md(raw_title)
    if spiel_id == "schicksalsklinge":
        if ver == "1.5h":
            return "Geheimräume in Schwarzmagierruine und Drachenhort wieder erreichbar"
        if ver == "1.5g":
            return "Böser Blick ohne Hänger, Analüs/Odem-Abbruch, Sterbeschrei männlicher Gegner"
        if ver == "1.5f":
            return "Flüssiges Drehen, kein Zeigerflackern, keine Kopierschutzabfrage"
        if ver == "1.5e":
            return "Schneidzahn, Truhenschlösser, Drachenhort-Loch, Wasserfass; Probenlog erweitert"
        if ver == "1.5d":
            return "Probenlog zeigt Gegnerzahl, Lagerüberfall und Reisewürfe"
        if ver == "1.2.1":
            return "Unterstützung für Linux (patchen.sh, starten.sh) und Lizenzangabe"
        if ver == "1.2":
            return "Abgleich mit dem Osterpatch von NRS (29 neue Korrekturen und Datenpatch)"
        if ver == "1.1":
            return "Zauber laut Lösungsbuch: Visibili, Gardianum, Feuerbann und Große Gier"
        if ver == "1.0":
            return "Erste Veröffentlichung der Bugfix-Fassung (248 behobene Fehler)"
    elif spiel_id == "sternenschweif":
        if ver == "1.1.1":
            return "Unterstützung für Linux (patchen.sh, starten.sh)"
        if ver == "1.1":
            return "Zauber laut Lösungsbuch: Visibili für die ganze Gruppe und Gardianum"
        if ver == "1.0":
            return "Erste Veröffentlichung der Bugfix-Fassung (225 behobene Fehler)"
    elif spiel_id == "riva":
        if ver == "1.0":
            return "Erste Veröffentlichung der Bugfix-Edition (52 behobene Fehler und Live-Probenlog)"

    if t:
        return t
    first_line = clean_md(body.splitlines()[0]) if body.strip() else ""
    return first_line[:90]


def parse_table_bugfixes(
    bugfixes_text: str,
    spiel_id: str,
    spiel_name: str,
    github_url: str,
    dates: dict[str, str],
) -> dict:
    """Parst BUGFIXES.md im Tabellenformat (Schicksalsklinge und Sternenschweif)."""
    # 1. Alle Korrekturen aus "## Alle Änderungen nach Spielbereich"
    idx_bereiche = bugfixes_text.index("## Alle Änderungen nach Spielbereich")
    idx_ende = len(bugfixes_text)
    for end_marker in ("## Bewusst nicht geändert", "## Etwas gefunden?"):
        if end_marker in bugfixes_text[idx_bereiche:]:
            cand = idx_bereiche + bugfixes_text[idx_bereiche:].index(end_marker)
            if cand < idx_ende:
                idx_ende = cand
    bereiche_text = bugfixes_text[idx_bereiche:idx_ende]

    korrekturen: list[dict] = []
    korr_by_nr: dict[str, dict] = {}
    current_bereich = ""

    for line in bereiche_text.splitlines():
        m_ber = re.match(r"^###\s+(.+?)\s*$", line)
        if m_ber:
            current_bereich = clean_md(m_ber.group(1))
            continue
        m_row = re.match(r"^\|\s*(\d+)\s*\|\s*(.+?)\s*\|\s*([WA])\s*\|\s*$", line)
        if not m_row:
            continue
        nr = m_row.group(1).strip()
        cell = m_row.group(2).strip()
        stufe_code = m_row.group(3).strip()
        stufe = "Wichtig" if stufe_code == "W" else "nur Alle"
        exploit = "💰" in cell

        if "<br>*So prüfst du es:*" in cell:
            part_main, part_pruef = cell.split("<br>*So prüfst du es:*", 1)
        elif "*So prüfst du es:*" in cell:
            part_main, part_pruef = cell.split("*So prüfst du es:*", 1)
        else:
            part_main, part_pruef = cell, ""

        m_main = re.match(r"^\*\*(.+?)\*\*(.*?)\s+–\s+(.+)$", part_main.strip())
        if m_main:
            raw_titel = m_main.group(1)
            raw_was = m_main.group(3)
        else:
            raw_titel = part_main
            raw_was = ""

        titel = clean_md(raw_titel.replace("💰", "").replace("✅", ""))
        was_war_falsch, herkunft = extract_herkunft_and_clean(raw_was)
        so_pruefst_du_es = clean_md(part_pruef)

        entry = {
            "nr": nr,
            "titel": titel,
            "was_war_falsch": was_war_falsch,
            "so_pruefst_du_es": so_pruefst_du_es,
            "stufe": stufe,
            "exploit": exploit,
            "bereich": current_bereich,
            "herkunft": herkunft,
        }
        korrekturen.append(entry)
        korr_by_nr[nr] = entry

    # 2. Versionen aus "## Neu in Version ..."
    versionen_raw: list[tuple[str, str, str]] = []
    for m_ver in re.finditer(
        r"^## Neu in Version ([^\n:]+)(?::\s*([^\n]+))?\n(.*?)(?=\n## |\Z)",
        bugfixes_text,
        re.M | re.S,
    ):
        ver_num = m_ver.group(1).strip()
        ver_tit = (m_ver.group(2) or "").strip()
        ver_body = m_ver.group(3).strip()
        versionen_raw.append((ver_num, ver_tit, ver_body))

    # Bestimme, welche Korrekturen in 1.1..1.5h komplett neu hinzugekommen sind vs. nachgebessert
    # Wir werten die Versionen von alt nach neu aus:
    # Eine Korrektur ist "nachgebessert", wenn der Text "Nachbesserung", "ergänzt in Nr.", "zu Nr." oder
    # "Lücke in unserer Behebung" nennt.
    versionen: list[dict] = []
    neu_assigned: set[str] = set()

    # In 1.2 von Schicksalsklinge wurden laut PROJEKT.md / Text einige bereits in 1.0 vorhandene Nummern
    # aus dem NRS-Osterpatch erweitert (76, 86, 106, 341, 390). Prüfen wir, welche Nummern in "## Was ist neu"
    # oder der 1.0-Basis standen:
    for ver_num, ver_tit, ver_body in versionen_raw:
        ver_korr: list[dict] = []
        seen_in_ver: set[str] = set()
        for line in ver_body.splitlines():
            line_s = line.strip()
            if not line_s.startswith("- "):
                continue
            # Alle "Nr. X" in dieser Aufzaehlungszeile
            # Bevorzuge die Hauptnennung am Zeilenende "– Nr. X" oder "(Nachbesserung zu Nr. X)"
            nrs_in_line = re.findall(r"Nr\.\s*(\d+)", line_s)
            if not nrs_in_line:
                continue
            is_nachgebessert = bool(
                re.search(
                    r"Nachbesserung|nachgebessert|ergänzt in Nr\.|gemeldet von [^\n)]+ zu Nr\.|Lücke in unserer Behebung",
                    line_s,
                    re.I,
                )
            )
            # Falls Zeile mit "**Spieldaten (neu):**" beginnt, sind die dort in Klammern genannten Nr. unten nochmal einzeln aufgeführt
            if line_s.startswith("- **Spieldaten (neu):**"):
                continue
            target_nr = nrs_in_line[-1]
            if spiel_id == "schicksalsklinge" and ver_num == "1.2" and target_nr in ("76", "86", "106", "341", "390"):
                is_nachgebessert = True
            if target_nr in korr_by_nr and target_nr not in seen_in_ver:
                seen_in_ver.add(target_nr)
                art = "nachgebessert" if is_nachgebessert else "neu"
                ver_korr.append({"nr": target_nr, "art": art})
                if art == "neu":
                    neu_assigned.add(target_nr)

        cleaned_body = clean_md(ver_body, keep_newlines=True)
        versionen.append(
            {
                "version": f"v{ver_num}",
                "datum": dates.get(ver_num, ""),
                "titel": shorten_version_title(ver_num, ver_tit, ver_body, spiel_id),
                "text": cleaned_body,
                "korrekturen": ver_korr,
            }
        )

    # Basisversion v1.0 ("## Was ist neu" + alle initialen Korrekturen)
    was_ist_neu_body = ""
    m_win = re.search(r"^## Was ist neu\n(.*?)(?=\n## |\Z)", bugfixes_text, re.M | re.S)
    if m_win:
        was_ist_neu_body = m_win.group(1).strip()

    # Hervorgehobene Korrekturen aus "## Was ist neu" zuerst, danach die übrigen aus v1.0
    v10_korr: list[dict] = []
    v10_seen: set[str] = set()
    for nr in re.findall(r"Nr\.\s*(\d+)", was_ist_neu_body):
        if nr in korr_by_nr and nr not in neu_assigned and nr not in v10_seen:
            v10_seen.add(nr)
            v10_korr.append({"nr": nr, "art": "neu"})
    for k in korrekturen:
        nr = k["nr"]
        if nr not in neu_assigned and nr not in v10_seen:
            v10_seen.add(nr)
            v10_korr.append({"nr": nr, "art": "neu"})

    versionen.append(
        {
            "version": "v1.0",
            "datum": dates.get("1.0", ""),
            "titel": shorten_version_title("1.0", "", was_ist_neu_body, spiel_id),
            "text": clean_md(was_ist_neu_body, keep_newlines=True),
            "korrekturen": v10_korr,
        }
    )

    # 3. Zusatzfunktionen (Nicht-Fehlerbehebungen) aus den Versionsabschnitten extrahieren
    zusatzfunktionen: list[dict] = []
    if spiel_id == "schicksalsklinge":
        zusatzfunktionen = [
            {
                "titel": "Flüssiges Drehen (90°-Schwenk in Städten und Dungeons)",
                "version": "v1.5f",
                "stufe": "ab Wichtige (im Starter schaltbar)",
                "text": (
                    "Beim Drehen schwenkt die 3D-Ansicht in Städten und Dungeons weich anfahrend und abbremsend "
                    "statt hart um 90 Grad. Rahmen, Verzierungen (Drachen, Säulen), Kompass und Mauszeiger bleiben "
                    "dabei fest stehen. Standardmäßig eingeschaltet; im Starter über den Haken „Flüssig drehen“ "
                    "oder unter DOS mit DREHEN_AUS.bat / DREHEN_AN.bat (Linux: DREHEN=0) jederzeit umschaltbar."
                ),
            },
            {
                "titel": "Ruhiger Mauszeiger ohne Flackern beim Laufen und Drehen",
                "version": "v1.5f",
                "stufe": "ab Wichtige (alle Fassungen)",
                "text": (
                    "In den Fix-Fassungen verschwindet der Mauszeiger beim Neuzeichnen der Ansicht während Schritten, "
                    "Drehungen (inkl. Schwenk) sowie beim Betreten und Verlassen von Häusern nicht mehr. Unter DOS "
                    "wird er beim Kopieren der Ansicht lückenlos über den Bildpuffer mitgezeichnet, in den nativen "
                    "Port- und Browser-Fassungen werden Zwischenbilder während der Ausblend-Lücke nicht vorzeitig gezeigt."
                ),
            },
            {
                "titel": "Keine Kopierschutzabfrage in den DOS-Fix-Fassungen",
                "version": "v1.5f",
                "stufe": "ab Wichtige (wie Windows, Linux & Browser)",
                "text": (
                    "In den DOS-Fix-Fassungen (Wichtige und Alle) entfällt beim Spielstart nach der Wahl des "
                    "Schwierigkeitsgrads die Handbuch- und Kartenabfrage, sodass es direkt zur Auswahl "
                    "„Hauptprogramm“ / „Generierung“ weitergeht. Die Original-EXE fragt weiterhin."
                ),
            },
            {
                "titel": "Live-Probenlog (Talent-, Zauber-, Kampf- und Reisewürfe)",
                "version": "v1.3–v1.5e",
                "stufe": "ab Wichtige (Haken „Probenlog“)",
                "text": (
                    "Zeigt live in einem zweiten Fenster neben dem Spiel (sowie in PROBEN.CSV und der HTML-Auswertung) "
                    "alle Würfe des Spiels: Eigenschaftsproben, Talent- und Zauberproben mit jedem der drei W20 und "
                    "Restpunkten, Fernkampf, Attacke und Parade, alle Würfe beim Stufenanstieg (seit v1.5), "
                    "Gegnerzahl, Nachtlager-Überfallwürfe und tägliche Reisewürfe (seit v1.5d) sowie Kampf-IDs, "
                    "Seereise-Zufallswürfe und Krankheitsproben (seit v1.5e)."
                ),
            },
            {
                "titel": "Lebendiger Stadthimmel (Wolken, Sonne, Mond und Sterne)",
                "version": "v1.4 / v1.4a",
                "stufe": "Optional (HIMMEL_AN.bat / HIMMEL.AN)",
                "text": (
                    "Ersetzt das feste Wolkenbild über den Städten durch einen nahtlosen Rundum-Himmel mit ziehenden "
                    "Wolken (Menge, Tempo und Sturmfarbe nach dem Tageswind des Spiels), Sonne (7–20 Uhr), Mond "
                    "(21–5 Uhr) und Sternen in den Farben der originalen Himmelspalette. Seit v1.4a standardmäßig "
                    "ausgeschaltet; einschalten mit HIMMEL_AN.bat (Linux: HIMMEL=1)."
                ),
            },
            {
                "titel": "Speichern ohne AP-Verlust außerhalb von Tempeln",
                "version": "v1.4a",
                "stufe": "Optional (SPEICHERN_OHNE_AP_AN.bat / APFREI.AN)",
                "text": (
                    "Außerhalb eines Tempels kostet Speichern im Original jeden Helden 1 Abenteuerpunkt. "
                    "Mit SPEICHERN_OHNE_AP_AN.bat (Linux: SPEICHERN_OHNE_AP=1) entfällt dieser Abzug samt dem "
                    "Hinweis im Speicherfenster (nach der Idee des Extra-Patches NOAPLOSS von NRS). "
                    "Standardmäßig ausgeschaltet; zurück zum Originalverhalten mit SPEICHERN_OHNE_AP_AUS.bat."
                ),
            },
        ]
    elif spiel_id == "sternenschweif":
        zusatzfunktionen = [
            {
                "titel": "Live-Probenlog (inkl. Stufenanstieg seit v1.3)",
                "version": "v1.2 / v1.3",
                "stufe": "ab Wichtige (Haken „Probenlog“)",
                "text": (
                    "Zeigt live in einem zweiten Fenster neben dem Spiel (sowie in PROBEN.CSV und "
                    "Probenlog_Sternenschweif.html) jede Probe: Eigenschaftsproben mit Wert, Zuschlag, W20 und "
                    "Ergebnis, Talent- und Zauberproben mit allen drei Eigenschaften, jedem der drei W20 und "
                    "Restpunkten, Fernkampf sowie jede Attacke und Parade im Kampf. Seit v1.3 werden auch alle "
                    "Würfe beim Stufenanstieg (Talente, Zauber, Eigenschaften, LE/AE-Wurf und AE-Tausch) mitgeschrieben."
                ),
            },
            {
                "titel": "Angepasste DOSBox-Mausempfindlichkeit & Spielstands-Ablage",
                "version": "v1.1.1 / v1.2",
                "stufe": "Alle Fix-Stufen (Windows, DOSBox & Linux)",
                "text": (
                    "Verhindert das zu schnelle Rasen des Mauszeigers in der DOS-Fassung von Sternenschweif auf "
                    "großen Bildschirmen, lässt den Original-Spielordner komplett unangetastet und unterstützt "
                    "Windows (nativ & DOSBox), Linux (nativ & DOSBox/Staging) sowie den Browser."
                ),
            },
        ]

    akt_ver = versionen[0]["version"] if versionen else "v1.0"
    return {
        "spiel_id": spiel_id,
        "spiel_name": spiel_name,
        "aktuelle_version": akt_ver,
        "github_url": github_url,
        "versionen": versionen,
        "korrekturen": korrekturen,
        "zusatzfunktionen": zusatzfunktionen,
    }


def riva_bereich_fuer_nr(r_nr: str) -> str:
    """Ordnet eine Riva-Korrektur (R001..R092) ihrem Spielbereich zu."""
    n = int(r_nr[1:])
    if n in (1, 2, 3, 4, 5, 6, 7, 8):
        return "Technik, Grafik & Speicher"
    if n in (9, 10, 11, 27, 28, 37):
        return "Händler & Schmied"
    if n in (12, 13, 15, 21, 25, 26, 29, 33, 38, 53, 77):
        return "Helden, Gruppe & Inventar"
    if n in (14, 16, 17, 72, 84, 92):
        return "Oberfläche, Karte & Tagebuch"
    if n in (30, 39, 40):
        return "Kampf"
    if n in (41, 42, 43, 44, 45, 47, 49):
        return "Magie"
    return "Dungeons, Orte & Quests"


RIVA_BEREICH_ORDER = [
    "Dungeons, Orte & Quests",
    "Helden, Gruppe & Inventar",
    "Technik, Grafik & Speicher",
    "Magie",
    "Händler & Schmied",
    "Oberfläche, Karte & Tagebuch",
    "Kampf",
]


def parse_riva_bugfixes(
    bugfixes_text: str,
    spiel_id: str,
    spiel_name: str,
    github_url: str,
    dates: dict[str, str],
) -> dict:
    """Parst die Riva-BUGFIXES.md (Format: ### R001 — Titel)."""
    raw_entries: list[dict] = []
    for m in re.finditer(
        r"^###\s+(R\d+)\s+—\s+(.+?)\n(.*?)(?=\n---|\n## |\Z)",
        bugfixes_text,
        re.M | re.S,
    ):
        r_nr = m.group(1).strip()
        raw_tit = m.group(2).strip()
        body = m.group(3).strip()

        exploit = "💰" in raw_tit or bool(re.search(r"\*\*Spielervorteil \(Exploit\):\*\*\s*\*\*Ja", body))
        titel = clean_md(re.sub(r"💰\s*Exploit", "", raw_tit).replace("💰", ""))

        m_was = re.search(r"-\s+\*\*Was im Spiel passiert:\*\*\s*(.+?)(?=\n-\s+\*\*|\Z)", body, re.S)
        m_urs = re.search(r"-\s+\*\*Ursache im Code:\*\*\s*(.+?)(?=\n-\s+\*\*|\Z)", body, re.S)
        m_stf = re.search(r"-\s+\*\*Stufe:\*\*\s*([AB])", body)
        m_for = re.search(r"-\s+\*\*Forumsbezug:\*\*\s*(.+?)(?=\n-\s+\*\*|\Z)", body, re.S)

        was_war_falsch = clean_md(m_was.group(1)) if m_was else ""
        ursache = clean_md(m_urs.group(1)) if m_urs else ""
        # Die Riva-Liste hat keine Pruefanleitungen; die Ursache im Code ist Entwicklertext und gehoert nicht unter
        # "So prüfst du es" (sonst stuende dort Code statt einer Anleitung). Feld bleibt leer und wird nicht angezeigt.
        so_pruefst = ""

        stufe = "Wichtig" if (m_stf and m_stf.group(1) == "A") else "nur Alle"
        herkunft = ""
        if m_for:
            f_raw = m_for.group(1).strip()
            if not f_raw.startswith("—"):
                herkunft = clean_md(f_raw).lstrip("— ").strip()

        raw_entries.append(
            {
                "nr": r_nr,
                "titel": titel,
                "was_war_falsch": was_war_falsch,
                "so_pruefst_du_es": so_pruefst,
                "stufe": stufe,
                "exploit": exploit,
                "bereich_base": riva_bereich_fuer_nr(r_nr),
                "herkunft": herkunft,
            }
        )

    # Nach Bereich gruppieren und Bereichsnamen mit Anzahl versehen wie "Dungeons, Orte & Quests (11)"
    counts: dict[str, int] = {}
    for e in raw_entries:
        b = e["bereich_base"]
        counts[b] = counts.get(b, 0) + 1

    korrekturen: list[dict] = []
    for b_name in RIVA_BEREICH_ORDER:
        for e in raw_entries:
            if e["bereich_base"] == b_name:
                korrekturen.append(
                    {
                        "nr": e["nr"],
                        "titel": e["titel"],
                        "was_war_falsch": e["was_war_falsch"],
                        "so_pruefst_du_es": e["so_pruefst_du_es"],
                        "stufe": e["stufe"],
                        "exploit": e["exploit"],
                        "bereich": f"{b_name} ({counts[b_name]})",
                        "herkunft": e["herkunft"],
                    }
                )

    v10_korr = [{"nr": e["nr"], "art": "neu"} for e in raw_entries]
    versionen = [
        {
            "version": "v1.0",
            "datum": dates.get("1.0", "16.11.2026"),
            "titel": shorten_version_title("1.0", "", "", spiel_id),
            "text": (
                "Alle 52 Fehlerbehebungen (31 in Stufe Wichtig, 21 zusätzlich in Alle) wurden direkt am "
                "vollständig bytegleich rekonstruierten C++-Quelltext von Version 1.12 umgesetzt – darunter "
                "verschwundene Waffen beim Schmied (samt Schwert des Artherion), unheilbarer Dumpfschädel "
                "nach der Windsbraut, falsch angelegter Stirnreif beim Sternenschweif-Import, verlorene "
                "Gegenstände beim Destructibo und die feststeckende Lorenfahrt in der Zwergenbinge."
            ),
            "korrekturen": v10_korr,
        }
    ]

    zusatzfunktionen = [
        {
            "titel": "Live-Probenlog (Talent-, Zauber-, Eigenschafts- und Kampfproben)",
            "version": "v1.0",
            "stufe": "ab Wichtige (Haken „Probenlog“)",
            "text": (
                "Schreibt im Hintergrund jede Eigenschafts-, Talent-, Zauber- und Kampfprobe (Attacke, Parade, "
                "Fernkampf) in PROBEN.CSV und zeigt sie live im Begleitfenster neben dem Spiel an, ohne die "
                "Zufallsfolge oder das Spielstandsformat (.GAM) zu verändern."
            ),
        },
        {
            "titel": "Klassische Spielervorteile optional behalten (--exploits-lassen)",
            "version": "v1.0",
            "stufe": "Optional beim Selbstbauen",
            "text": (
                "Unter den 52 Korrekturen befinden sich 5 Fehler, die im Originalspiel von 1997 einen Vorteil "
                "für den Spieler darstellten (R025 Alchemie-Braudauer, R037 Laden-Rückerstattung, R041/R042/R043 "
                "Zaubern ohne ausreichende AE). Wer alle Absturz- und Logik-Fixes nutzen, aber diese 5 Tricks "
                "behalten möchte, kann mit --exploits-lassen bauen."
            ),
        },
    ]

    return {
        "spiel_id": spiel_id,
        "spiel_name": spiel_name,
        "aktuelle_version": "v1.0",
        "github_url": github_url,
        "versionen": versionen,
        "korrekturen": korrekturen,
        "zusatzfunktionen": zusatzfunktionen,
    }


def _nr_schluessel(nr) -> tuple:
    s = str(nr)
    m = re.match(r"([A-Za-z]*)(\d+)", s)
    return (m.group(1), int(m.group(2))) if m else (s, 0)


def sortiere_nach_stufe(data: dict) -> None:
    """Innerhalb jedes Bereichs und jeder Version: erst "Wichtig", dann "nur Alle", jeweils nach Nummer."""
    stufe = {str(k["nr"]): k["stufe"] for k in data["korrekturen"]}
    rang = lambda s: 0 if s == "Wichtig" else 1
    bereich_reihe = []
    for k in data["korrekturen"]:
        if k["bereich"] not in bereich_reihe:
            bereich_reihe.append(k["bereich"])
    data["korrekturen"].sort(key=lambda k: (bereich_reihe.index(k["bereich"]), rang(k["stufe"]), _nr_schluessel(k["nr"])))
    for v in data.get("versionen", []):
        v["korrekturen"].sort(key=lambda e: (rang(stufe.get(str(e["nr"]), "")), _nr_schluessel(e["nr"])))


def main() -> int:
    sources = [
        (
            "schicksalsklinge",
            "Die Schicksalsklinge",
            Q005_DIR / "BUGFIXES.md",
            Q005_DIR,
            Q005_DIR / "GitHub" / "schicksalsklinge",
            "https://github.com/MeowMuhMuhCow/schicksalsklinge/blob/main/BUGFIXES.md",
            "table",
        ),
        (
            "sternenschweif",
            "Sternenschweif",
            Q004_DIR / "BUGFIXES.md",
            Q004_DIR,
            Q004_DIR / "GitHub" / "sternenschweif",
            "https://github.com/MeowMuhMuhCow/sternenschweif/blob/main/BUGFIXES.md",
            "table",
        ),
        (
            "riva",
            "Schatten über Riva",
            Q006_DIR / "GitHub_Vorbereitung" / "riva" / "BUGFIXES.md",
            Q006_DIR,
            Q006_DIR / "GitHub_Vorbereitung" / "riva",
            "https://github.com/MeowMuhMuhCow/riva/blob/main/BUGFIXES.md",
            "riva",
        ),
    ]

    out_dirs = [
        STARTER_DIR,
        STARTER_DIR / "trilogie" / "Nordlandtrilogie" / "_starter",
    ]
    rel_dir = STARTER_DIR / "release"
    if rel_dir.is_dir():
        out_dirs.append(rel_dir)

    for spiel_id, spiel_name, bf_path, proj_dir, gh_dir, gh_url, fmt in sources:
        if not bf_path.is_file():
            print(f"FEHLER: BUGFIXES.md nicht gefunden: {bf_path}", file=sys.stderr)
            return 1
        txt = bf_path.read_text(encoding="utf-8")
        dates = collect_belegte_daten(txt, proj_dir, gh_dir, STARTER_DIR)
        if fmt == "table":
            data = parse_table_bugfixes(txt, spiel_id, spiel_name, gh_url, dates)
        else:
            data = parse_riva_bugfixes(txt, spiel_id, spiel_name, gh_url, dates)

        sortiere_nach_stufe(data)
        json_bytes = (json.dumps(data, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
        fname = f"fanpatch_{spiel_id}.json"
        for od in out_dirs:
            od.mkdir(parents=True, exist_ok=True)
            (od / fname).write_bytes(json_bytes)

        n_ver = len(data["versionen"])
        n_korr = len(data["korrekturen"])
        n_zus = len(data["zusatzfunktionen"])
        n_w = sum(1 for k in data["korrekturen"] if k["stufe"] == "Wichtig")
        n_a = sum(1 for k in data["korrekturen"] if k["stufe"] != "Wichtig")
        n_exp = sum(1 for k in data["korrekturen"] if k["exploit"])
        print(
            f"[fanpatch_daten] {spiel_name:22s} -> {fname:32s}: "
            f"{n_ver:2d} Versionen, {n_korr:3d} Korrekturen ({n_w:3d} Wichtig, {n_a:3d} nur Alle, {n_exp:2d} Exploits), "
            f"{n_zus} Zusatzfunktionen"
        )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
