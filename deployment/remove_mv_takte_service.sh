#!/bin/bash

SERVICE_NAME="mv-takte.service"
SERVICE_PATH="/etc/systemd/system/$SERVICE_NAME"

echo "1. Stoppe den Service..."
sudo systemctl stop "$SERVICE_NAME"

echo "2. Deaktiviere den Service..."
sudo systemctl disable "$SERVICE_NAME"

echo "3. Entferne die Service-Datei..."
sudo rm -f "$SERVICE_PATH"

echo "4. Systemd neu laden..."
sudo systemctl daemon-reload

echo "5. Status prüfen..."
sudo systemctl status "$SERVICE_NAME" --no-pager || echo "Service wurde entfernt."

echo "Fertig! Der Autostart-Service ist entfernt."
