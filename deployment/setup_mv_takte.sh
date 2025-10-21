#!/bin/bash

# Dieses Skript richtet das MV-Takte-Projekt auf einem Raspberry Pi ein und aktiviert den Autostart-Service.

set -e

# Variablen
SERVICE_NAME="mv-takte.service"
SERVICE_PATH="/etc/systemd/system/$SERVICE_NAME"
PROJECT_DIR="$(pwd)"
DEPLOYMENT_DIR="$PROJECT_DIR/deployment"
USER_NAME="$(whoami)"
echo "Projektverzeichnis ist: $PROJECT_DIR"
echo "Deployment-Verzeichnis ist: $DEPLOYMENT_DIR"

echo "1. Data-Ordner erstellen, falls nicht vorhanden..."
DATA_DIR="$PROJECT_DIR/data"
mkdir -p "$DATA_DIR"

echo "2. Python-Abhaengigkeiten installieren..."
if pip3 install -r "$PROJECT_DIR/requirements.txt"; then
	echo "Pakete erfolgreich installiert."
else
	echo "Fehler oder Warnung bei der Installation!"
	read -p "Nochmal versuchen mit --break-system-packages? (j/n): " choice
	if [ "$choice" = "j" ]; then
		pip3 install --break-system-packages -r "$PROJECT_DIR/requirements.txt"
	else
		echo "Installation abgebrochen. Bitte pruefe die Umgebung oder nutze ein venv."
		exit 1
	fi
fi

echo "3. Systemd-Service-Datei erstellen..."
echo "Projektverzeichnis ist: $PROJECT_DIR"
echo "Deployment-Verzeichnis ist: $DEPLOYMENT_DIR"

cat > "$DEPLOYMENT_DIR/$SERVICE_NAME" <<EOL
[Unit]
Description=MV-Takte Python Service
After=network.target

[Service]
Type=simple
User=$USER_NAME
WorkingDirectory=$PROJECT_DIR
ExecStart=/usr/bin/python3 main.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOL

echo "4. Systemd-Service-Datei kopieren..."
sudo cp "$DEPLOYMENT_DIR/$SERVICE_NAME" "$SERVICE_PATH"

echo "5. Rechte setzen..."
sudo chown $USER_NAME:$USER_NAME -R "$PROJECT_DIR"
sudo chmod 644 "$SERVICE_PATH"

echo "6. Systemd neu laden..."
sudo systemctl daemon-reload

echo "7. Service aktivieren und starten..."
sudo systemctl enable "$SERVICE_NAME"
sudo systemctl restart "$SERVICE_NAME"

echo "Fertig! Status des Services:"
sudo systemctl status "$SERVICE_NAME" --no-pager

echo "Starte Live-Log-Ansicht des Services (mit STRG+C beenden):"
sudo journalctl -u "$SERVICE_NAME" -f