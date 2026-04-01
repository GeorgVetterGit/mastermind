# 🎯 Mastermind

Ein klassisches Mastermind-Spiel, implementiert in Python mit Pygame – spielbar im Browser via WebAssembly (pygbag).

---

## Spielprinzip

Ein zufälliger **4-farbiger Geheimcode** wird generiert (aus 6 Farben, Wiederholungen erlaubt).  
Der Spieler hat **10 Versuche**, den Code zu knacken.

Nach jedem Versuch gibt es Feedback:

| Peg | Bedeutung |
|-----|-----------|
| ● Schwarz | Richtige Farbe, richtige Position |
| ○ Weiß | Richtige Farbe, falsche Position |

---

## Steuerung

| Aktion | Maus | Tastatur |
|--------|------|----------|
| Farbe auswählen | Palette anklicken | `1` – `6` |
| Farbe setzen | Linksklick auf Slot | — |
| Farbe löschen | Rechtsklick auf Slot | — |
| Raten bestätigen | **Submit**-Button | `Enter` |
| Neues Spiel | **New Game**-Button | `N` |
| Beenden | — | `Esc` |

---

## Lokal starten

### Voraussetzungen

- Python 3.8+
- pygame

```bash
pip install pygame
```

### Ausführen

```bash
python main.py
```

---

## Web-Build (WASM)

Das Spiel lässt sich mit [pygbag](https://pygame-web.github.io/) in eine WebAssembly-Anwendung umwandeln, die direkt im Browser läuft.

### Voraussetzungen

```bash
pip install pygbag
```

### Build erstellen

```bash
python -m pygbag --build --archive --width 620 --height 760 mastermind
```

Die Ausgabe landet in `build/`:

```
build/
├── web/
│   ├── index.html        # HTML-Shell mit Pygame-WASM-Loader
│   ├── mastermind.apk    # Gepacktes Python-App-Archiv
│   └── favicon.png       # App-Icon
└── web.zip               # Fertiges Archiv für itch.io
```

### Lokal im Browser testen

```bash
python -m pygbag mastermind
# → http://localhost:8000
```

### Auf itch.io veröffentlichen

1. Neues Projekt auf [itch.io](https://itch.io) erstellen
2. Art: **HTML**
3. `build/web.zip` hochladen
4. Option *„This file will be played in the browser"* aktivieren

> Beim ersten Laden lädt pygbag die Python/WASM-Runtime (~8 MB) einmalig aus dem Browser-Cache.

---

## Projektstruktur

```
mastermind/
├── main.py          # Gesamter Spielcode (Logik + Rendering)
├── build/
│   ├── web/         # Entpackte Web-Ausgabe
│   └── web.zip      # itch.io-Archiv
└── README.md
```

---

## Farben

| # | Farbe |
|---|-------|
| 1 | 🔴 Rot |
| 2 | 🟢 Grün |
| 3 | 🔵 Blau |
| 4 | 🟡 Gelb |
| 5 | 🟠 Orange |
| 6 | 🟣 Lila |

---

## Lizenz

MIT
