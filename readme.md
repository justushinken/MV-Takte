# MV-Takte

**Zählerstand-Erfassung und Bereitstellung per Modbus und Webserver**

Dieses Projekt zählt Takte (z.B. von einem Taster), speichert Tageswerte in einer CSV-Datei und stellt den aktuellen Stand über Modbus sowie einen HTTP-Webserver bereit.

---

## Hauptfunktionen

- **Taktzählung** per Hardware-Taster (GPIO) oder Simulation
- **Speicherung** der Tageswerte in einer CSV-Datei (`data/MV1.csv`)
- **Modbus-Server** zur Bereitstellung des aktuellen Zählerstands
- **HTTP-Webserver** für Webzugriff (Anzeige/Download der Daten, z.B. `data/index.html`)

---

## Voraussetzungen

- Python 3.11+
- Empfohlene Pakete (siehe `requirements.txt`):

  - `gpiozero` (nur für echte Hardware-Taster, auf Linux/Raspberry Pi)
  - `uvicorn`
  - `fastapi`
  - `pymodbus`

Installation aller Abhängigkeiten:
```sh
pip install -r requirements.txt
# Falls nötig: pip install --break-system-packages -r requirements.txt
```

---

## Projektstruktur

```
MV-Takte/
├── main.py                # Hauptprogramm (Taktzählung, Modbus, Webserver)
├── server_web.py          # FastAPI-Webserver (aktueller Stand, CSV, HTML)
├── server_modbus.py       # Modbus-Server-Logik
├── requirements.txt       # Python-Abhängigkeiten
├── data/ (wird erst erstellt durch setup_mv_takte.sh)
│   ├── MV1.csv            # CSV-Datei mit Tageswerten (wird automatisch angelegt)
│   └── index.html         # (Optional) HTML-Ansicht der Daten
├── deployment/
│   ├── mv-takte.service           # systemd-Service-Datei für Autostart (wird erst erstellt durch setup_mv_takte.sh)
│   ├── setup_mv_takte.sh          # Setup-Skript für Installation & Service
│   └── remove_mv_takte_service.sh # Skript zum Entfernen des Services
```

---

## Nutzung

### Starten des Programms

```sh
python main.py
```

- Der Webserver läuft standardmäßig auf Port 8000.
- Der Modbus-Server läuft parallel.
- Die Taktzählung erfolgt entweder simuliert oder über einen echten Taster (je nach Einstellung).

### Simulation aktivieren

Standardmäßig ist die Simulation **aus**.  
Du kannst die Simulation beim Start per Kommandozeilen-Parameter aktivieren:

```sh
python main.py --sim
```

Ohne `--sim` wird der echte Taster verwendet (sofern vorhanden).

---

### Web-API

- **Aktueller Stand (JSON):**  
  [http://localhost:8000/stand](http://localhost:8000/stand)
- **CSV-Download:**  
  [http://localhost:8000/csv](http://localhost:8000/csv)
- **HTML-Ansicht:**  
  [http://localhost:8000/](http://localhost:8000/)

### Modbus

- Der aktuelle Zählerstand kann per Modbus TCP abgefragt werden (siehe `server_modbus.py` für Details).

---

## Service-Installation (Autostart auf Raspberry Pi)

Im Ordner `deployment/` findest du alle nötigen Dateien:


- **Service einrichten und starten:**
  ```sh
  bash deployment/setup_mv_takte.sh
  ```
  Das Skript installiert alle Abhängigkeiten, legt den `data`-Ordner automatisch an, erstellt die Service-Datei im Ordner `deployment` und richtet den systemd-Service ein. Der Service läuft mit dem aktuellen Benutzer (User=`whoami`). Nach der Einrichtung werden direkt die Live-Logs (`journalctl`) angezeigt.

  **Hinweis:**
  - Bitte aus Projektverzeichnis die Bash Skripte ausführen
  - Die Service-Datei wird im Ordner `deployment` erstellt und nach `/etc/systemd/system/` kopiert.
  - Der Service läuft mit dem Benutzer, der das Setup-Skript ausführt. Python-Pakete sollten daher für diesen User installiert sein.
  - Falls Pakete fehlen, prüfe die Installation mit `pip3 install -r requirements.txt`.

- **Service entfernen:**
  ```sh
  bash deployment/remove_mv_takte_service.sh
  ```

---

## Konfiguration

- **Simulation aktivieren/deaktivieren:**  
  Per Kommandozeile:  
  - Simulation an: `python main.py --sim`
  - Simulation aus (Standard): `python main.py`

- **CSV/HTML-Dateinamen:**  
  In `main.py` über die Variablen `csv_datei` und `html_datei` anpassbar (jetzt im `data/`-Ordner).

- **Pfade:**  
  Die Pfade zu den Daten werden plattformübergreifend mit `os.path.join` oder `pathlib` gesetzt, damit alles unter Windows und Linux funktioniert.

---

## Hinweise

- Auf Windows funktioniert `gpiozero` nicht, daher nur Simulation nutzen.
- Der Webserver liest den aktuellen Stand immer aus der CSV-Datei, um Synchronisationsprobleme zu vermeiden.

### systemd und Python-Umgebung

- Der Service verwendet `/usr/bin/python3` und läuft mit dem aktuellen Benutzer. Stelle sicher, dass alle benötigten Pakete für diesen User installiert sind. Falls du ein venv verwendest, passe die Service-Datei entsprechend an (`ExecStart=/pfad/zum/venv/bin/python main.py`).

### Automatische Fehlerbehebung beim Start

- Falls beim ersten Start ein Fehler wegen fehlender Pakete auftritt, wird der Service automatisch neu gestartet. Nach erfolgreicher Installation funktioniert alles wie erwartet.

### Warum wird `time.sleep(10)` statt `input()` bzw. `pause()` verwendet?

Im Service-Betrieb (z.B. mit systemd auf dem Raspberry Pi) gibt es keine interaktive Konsole. Ein `input()` würde hier einen Fehler verursachen und das Programm beenden. Mit einer Endlosschleife und `time.sleep(10)` bleibt das Programm dauerhaft aktiv, ohne die CPU zu belasten. So kann der Service zuverlässig im Hintergrund laufen und alle Aufgaben (Taktzählung, Modbus, Webserver) ausführen.

---