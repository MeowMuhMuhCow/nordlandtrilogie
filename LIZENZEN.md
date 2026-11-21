# Lizenzen & Herkunftshinweise – Gemeinsames Paket „Nordlandtrilogie“

Dieses Paket enthält **keine** urheberrechtlich geschützten Original-Spieldaten, **keine** Original-Programmdateien (`SCHICKM.EXE`, `SCHWEIF.EXE`, `RIVA.EXE`) und **keine** eingebetteten Original-Grafiken von Attic Entertainment Software (`0` übereinstimmende 64-Byte-Fenster zu den Original-EXEs und Original-Bildern). Zum Spielen wird die eigene deutsche GOG-Fassung des jeweiligen Teils benötigt.

Jeder Spiel-Unterordner behält seine eigene vollständige Lizenzdatei:
- **Teil 1 (*Die Schicksalsklinge*):** `Schicksalsklinge/COPYING` (und `Schicksalsklinge/Nativ/COPYING`)
- **Teil 2 (*Sternenschweif*):** `Sternenschweif/COPYING` und `Sternenschweif/LIZENZ.md` (sowie unter `Sternenschweif/Nativ/`)
- **Teil 3 (*Schatten über Riva*):** `Riva/LIZENZEN.md` (und `Riva/Nativ/LIZENZEN.md`)

---

## Übersicht der Komponenten und Lizenzen

### 1. Gemeinsamer Starter (`NORDLANDTRILOGIE.EXE`)
- **Lizenz:** GNU General Public License Version 3 (**GPLv3**)
- **Bibliotheken:**
  - **SDL2-Header (`SDL.h`) & Win32-Provider (`sdl2_win32_provider.c`):** **zlib-Lizenz** (Copyright Sam Lantinga). Nutzt direkt die Windows-Systembibliotheken (`user32`, `gdi32`, `winmm`, `shell32`), sodass keine externe `SDL2.dll` benötigt wird.

### 2. Teil 1 – Die Schicksalsklinge (`Schicksalsklinge/`)
- **Lizenz:** GNU General Public License Version 3 (**GPLv3**), Details in `Schicksalsklinge/COPYING`.
- **Quellen & Bibliotheken:**
  - **Bright-Eyes** (Decompilierung & Rekonstruktion von `SCHICKM.EXE` V3.02de & `NGEN`, https://github.com/shihan42/Bright-Eyes) – **GPLv3**
  - **MobileEyes** (CD-Audio-Steuerung, 8086-Intro-Interpreter & Portierungs-Referenz, Gero Ohrner / Kerygma83, https://github.com/Kerygma83/mobile-eyes) – **GPLv3**
  - **PowerPacker-2.0-Entpacker (`decomp_pp20`)** (Heikki Orsila) – **GPLv2+ / LGPL**
  - **DOSBox 0.74 OPL2/OPL3-Emulator (`DBOPL`)** (The DOSBox Team) – **GPLv2+** (kompatibel mit GPLv3)
  - **stb_vorbis** (Sean Barrett) – **Public Domain (Unlicense) / MIT-Lizenz**
  - **SDL2** (Sam Lantinga u. a.) – **zlib-Lizenz**

### 3. Teil 2 – Sternenschweif (`Sternenschweif/`)
- **Lizenz:** GNU General Public License Version 3 (**GPLv3**), Details in `Sternenschweif/COPYING` und `Sternenschweif/LIZENZ.md`.
- **Quellen & Bibliotheken:**
  - **Bright-Eyes** (Rekonstruierter C/C++-Quellcode `SEG002..OVL271` & Fehlerkorrekturen, https://github.com/shihan42/Bright-Eyes) – **GPLv3**
  - **BrightEyes-SDL2 / MobileEyes** (`ppDecrunch` PowerPacker-2.0-Entpacker & Portierungs-Referenz, Gero Ohrner / Hynek) – **GPLv3**
  - **stb_vorbis** (Sean Barrett) – **Public Domain (Unlicense) / MIT-Lizenz**
  - **SDL2** (Sam Lantinga u. a.) – **zlib-Lizenz**

### 4. Teil 3 – Schatten über Riva (`Riva/`)
- **Details:** siehe `Riva/LIZENZEN.md`.
- Das Datensegment (`DGROUP`) wird erst beim Spielstart zur Laufzeit direkt aus der eigenen `RIVA.EXE` (deutsche GOG-Fassung V1.12) des Nutzers geladen.
- **Verwendete freie Bibliotheken:**
  - **SDL2-Header & eingebauter Win32-Provider:** **zlib-Lizenz**
  - **stb_vorbis** (Sean Barrett): **Public Domain (Unlicense) / MIT-Lizenz**
  - **OPL2-FM-Synthesizer (YM3812-Emulation):** **LGPL v2.1+ / GPL v2+**
  - **BRender Software-Renderer-Strukturen:** **MIT-Lizenz** (Argonaut Software / BRender Open-Source-Release)

### 5. DOS-Bugfix-Patcher (`*/DOS/Patch/`)
- Die Differenz-Patches (`*.ndp`) und Patcher-Skripte (`patchen.ps1`, `patchen.py`) erzeugen die fehlerbereinigten DOS-Programme lokal aus der eigenen Original-EXE des Nutzers, ohne Originaldateien zu überschreiben.
