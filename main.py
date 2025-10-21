"""
MV-Takte: Zaehlersand-Erfassung und Bereitstellung per Modbus und Webserver

Dieses Programm zaehlt Takte (z.B. von einem Taster), speichert Tageswerte in einer CSV-Datei
und stellt den aktuellen Stand ueber Modbus sowie einen HTTP-Webserver bereit.

Hauptfunktionen:
- Taktzaehlung per Hardware-Taster oder Simulation
- Speicherung der Tageswerte in CSV
- Modbus-Server zur Bereitstellung des aktuellen Zaehlersands
- HTTP-Webserver fuer Webzugriff (z.B. Anzeige/Download der Daten)
"""
import argparse
import os
import csv
import threading
import time
from datetime import date
from gpiozero import Button
import server_modbus as modbus  # type: ignore[import-not-found]

SIMULIERE_TASTER = False  # Standard: Simulation aus
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DATA_DIR = os.path.join(BASE_DIR, "data")
os.makedirs(DATA_DIR, exist_ok=True)

csv_datei = os.path.join(DATA_DIR, "MV1.csv")
html_datei = os.path.join(DATA_DIR, "index.html")
csv_header = ["Datum", "Zaehlersand"]

global letzter_tag
letzter_tag = date.today().strftime("%Y-%m-%d")
global zaehler
zaehler = 0
global context

if not os.path.exists(csv_datei):
    with open(csv_datei, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f, delimiter=';')
        writer.writerow(csv_header)

def lade_zaehlersand_und_datum():
    """Laedt den letzten Zaehlersand und das Datum aus der CSV-Datei."""
    global zaehler, letzter_tag
    letzter_tag = None
    try:
        with open(csv_datei, mode='r', newline='', encoding='utf-8') as f:
            reader = list(csv.reader(f, delimiter=';'))
            if len(reader) > 1:
                letzter_eintrag = reader[-1]
                letzter_tag = letzter_eintrag[0]
                zaehler = int(letzter_eintrag[1])
                print(f"Letzter Zaehlersand vom {letzter_tag} geladen: {zaehler}")
            else:
                zaehler = 0
                letzter_tag = None
                print("CSV leer, starte bei 0")
    except Exception as e:
        print(f"Fehler beim Laden: {e}")
        zaehler = 0
        letzter_tag = None

def schreibe_gesamtstand(datum, wert):
    """Schreibt oder aktualisiert den Zaehlersand fuer das gegebene Datum in der CSV-Datei."""
    daten = []
    geaendert = False
    with open(csv_datei, mode='r', newline='', encoding='utf-8') as f:
        reader = list(csv.reader(f, delimiter=';'))
        daten = reader

    header = daten[0] if daten else csv_header
    zeilen = daten[1:] if len(daten) > 1 else []

    for i, zeile in enumerate(zeilen):
        if zeile[0] == datum:
            zeilen[i][1] = str(wert)
            geaendert = True
            break
    if not geaendert:
        zeilen.append([datum, str(wert)])

    with open(csv_datei, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f, delimiter=';')
        writer.writerow(header)
        writer.writerows(zeilen)

def zaehle_takt():
    """Erhoeht den Zaehlersand und speichert ihn, ggf. mit Tageswechsel."""
    global zaehler, letzter_tag
    heute = date.today()
    if letzter_tag != heute.strftime("%Y-%m-%d"):
        zaehler = 0
        letzter_tag = heute.strftime("%Y-%m-%d")
        print(f"Neuer Tag erkannt: {letzter_tag}, Zaehlersand neu gestartet")

    zaehler += 1
    datum_str = heute.strftime("%Y-%m-%d")
    print(f"Taktzahl {zaehler} am {datum_str}")
    schreibe_gesamtstand(datum_str, zaehler)
    # erzeuge_html_aus_csv()  # Wuerde ich hier nicht bei jedem Takt aufrufen, sondern nur bei Abruf im Webserver

    if context:
        modbus.update_values(context.context, zaehler)

def start_webserver():
    """Startet den HTTP-Webserver im eigenen Thread."""
    import uvicorn
    uvicorn.run("server_web:app", host="0.0.0.0", port=8000, reload=False)

def start_modbus_server(context):
    """Startet den Modbus-Server im eigenen Thread."""
    import asyncio
    asyncio.run(modbus.server_async.run_async_server(context), debug=True)

def simuliere_taster():
    """Simuliert Tasterdruck alle 2 Sekunden."""
    while True:
        zaehle_takt()
        time.sleep(2)

if __name__ == "__main__":
    # Argumente parsen
    parser = argparse.ArgumentParser(description="MV-Takte: Taktzaehlung und Bereitstellung")
    parser.add_argument("--sim", action="store_true", help="Taster-Simulation aktivieren")
    args = parser.parse_args()

    if args.sim:
        SIMULIERE_TASTER = True

    # Starte Webserver
    web_thread = threading.Thread(target=start_webserver, daemon=True)
    web_thread.start()

    # Starte Modbus-Server
    context = modbus.setup_server()
    modbus_thread = threading.Thread(target=start_modbus_server, args=(context,), daemon=True)
    modbus_thread.start()
    
    if SIMULIERE_TASTER:
        thread = threading.Thread(target=simuliere_taster, daemon=True)
        thread.start()
        print("Taster-Simulation: Takte werden periodisch gezaehlt.")

    else:
        taster = Button(24, bounce_time=0.1)
        taster.when_pressed = zaehle_takt
        print("Takte zaehlen gestartet. Tageswerte werden in CSV und HTML gespeichert.")
        while True:
            time.sleep(10)

    print("Takte zaehlen gestartet. Tageswerte werden in CSV und HTML gespeichert.")
    while True:
        time.sleep(10)