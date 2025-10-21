from fastapi import FastAPI, Response
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
import os
import csv
# Importiere die Variablen aus main.py
from main import csv_datei, html_datei

def erzeuge_html_aus_csv():
    try:
        with open(csv_datei, mode='r', newline='', encoding='utf-8') as f:
            reader = csv.reader(f, delimiter=';')
            zeilen = list(reader)
    except Exception as e:
        print(f"Fehler beim Lesen der CSV für HTML: {e}")
        zeilen = []

    if len(zeilen) > 1:
        header = zeilen[0]
        daten = zeilen[1:]
        daten.sort(key=lambda x: x[0], reverse=True)
    else:
        header = []
        daten = []

    with open(html_datei, mode='w', encoding='utf-8') as f:
        f.write("""<!DOCTYPE html>
<html lang="de">
<head>
<meta charset="UTF-8">
<title>Zählerdaten MV1</title>
<style>
    body {
        font-family: Arial, sans-serif;
        margin: 40px;
        background-color: #f9f9f9;
        color: #333;
    }
    h1 {
        color: #2c3e50;
    }
    table {
        border-collapse: collapse;
        width: 60%;
        max-width: 800px;
        margin-bottom: 20px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        background-color: #fff;
    }
    th, td {
        border: 1px solid #ddd;
        text-align: center;
        padding: 10px;
    }
    th {
        background-color: #2980b9;
        color: white;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    tr:nth-child(even) {
        background-color: #ecf0f1;
    }
    tr:hover {
        background-color: #d1e7fd;
    }
    a.download-link {
        display: inline-block;
        margin-bottom: 15px;
        padding: 8px 15px;
        background-color: #2980b9;
        color: white;
        text-decoration: none;
        border-radius: 4px;
    }
    a.download-link:hover {
        background-color: #2073b8;
    }
    p.version {
        font-size: 0.9em;
        color: #666;
        margin-top: 10px;
        font-style: italic;
    }
</style>
</head>
<body>
<h1>Zählerdaten - Tagesgesamtstand - MV1</h1>
<table>
""")
        if header:
            f.write("<tr>")
            for spalte in header:
                f.write(f"<th>{spalte}</th>")
            f.write("</tr>\n")
            for row in daten:
                f.write("<tr>")
                for wert in row:
                    f.write(f"<td>{wert}</td>")
                f.write("</tr>\n")
        else:
            f.write("<tr><td colspan='2'>Keine Daten vorhanden</td></tr>\n")
        f.write("""
</table>
<a href="MV1.csv" download class="download-link">CSV-Datei herunterladen</a>
<p class="version">MV Taktzähler Version 1.0</p>
</body>
</html>
""")

app = FastAPI()

@app.get("/stand")
def aktueller_stand():
    try:
        with open(csv_datei, mode='r', newline='', encoding='utf-8') as f:
            reader = list(csv.reader(f, delimiter=';'))
            if len(reader) > 1:
                letzter_eintrag = reader[-1]
                return JSONResponse(content={"zaehler": int(letzter_eintrag[1])})
    except Exception:
        pass
    return 0
    

@app.get("/csv")
def download_csv():
    if os.path.exists(csv_datei):
        return FileResponse(csv_datei, media_type="text/csv", filename=csv_datei)
    return Response(status_code=404)

@app.get("/")
def html_view():
    erzeuge_html_aus_csv()
    if os.path.exists(html_datei):
        with open(html_datei, encoding="utf-8") as f:
            html_content = f.read()
        return HTMLResponse(content=html_content)
    return Response(content="Keine HTML-Datei vorhanden.", status_code=404)

# Optional: Endpunkt für die aktuelle Tagesliste als JSON
@app.get("/tage")
def tage_liste():
    import csv
    daten = []
    if os.path.exists(csv_datei):
        with open(csv_datei, mode='r', encoding='utf-8') as f:
            reader = csv.reader(f, delimiter=';')
            for row in reader:
                daten.append(row)
    return JSONResponse(content={"daten": daten})

# Starten mit: uvicorn webserver:app --reload

