#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Titel: WordPress Upload-Verzeichnis auf ungenutzte Dateien prüfen

Beschreibung:
Dieses Skript durchsucht das lokale Upload-Verzeichnis einer WordPress-Installation
nach Bilddateien und vergleicht diese mit den Inhalten aller Beiträge und Seiten,
die zuvor als JSON-Datei aus der Tabelle `wp_posts` exportiert wurden.
Dateien, die in keinem Beitrag referenziert sind, werden als potenziell ungenutzt gelistet.

Autor: Stefan Draeger
Webseite: https://draeger-it.blog

Disclaimer:
Die Ergebnisse dieses Skripts sollten manuell geprüft werden. Es kann vorkommen, dass Dateien
auf anderen Wegen (z. B. PageBuilder, Theme-Optionen, Custom Fields) verwendet werden, 
obwohl sie im Beitragstext nicht vorkommen. Lösche daher niemals Dateien ohne vorheriges Backup.
"""

import os
import json

# Konfiguration
UPLOADS_DIR = './wp-content/uploads'  # Lokaler Pfad zum Upload-Verzeichnis
JSON_FILE = './wp_posts.json'         # JSON-Datei mit den exportierten Beitragsdaten
IMAGE_EXTENSIONS = ('.jpg', '.jpeg', '.png', '.tiff', '.bmp')  # Zu prüfende Bildformate

# Lade die JSON-Datei mit den Beitragsinhalten (phpMyAdmin-Exportstruktur)
with open(JSON_FILE, 'r', encoding='utf-8') as file:
    raw_json = json.load(file)

# Finde das Datenobjekt mit den Inhalten der Tabelle "wp_posts"
entries = []
for obj in raw_json:
    if obj.get('type') == 'table' and obj.get('name') == 'wp_posts':
        entries = obj.get('data', [])
        break

# Fehler, falls keine Daten zur Tabelle gefunden wurden
if not entries:
    raise ValueError("Keine Daten zur Tabelle 'wp_posts' gefunden.")

# Extrahiere alle Beitragstexte (post_content) in eine Liste
content_list = [entry.get('Content', '') for entry in entries]

# Durchsuche Upload-Verzeichnis
unused_files = []     # Liste für nicht referenzierte Dateien
checked_count = 0     # Zähler für Statistik

for root, dirs, files in os.walk(UPLOADS_DIR):
    for file_name in files:
        # Filtere nur Bilddateien mit definierter Endung
        if file_name.lower().endswith(IMAGE_EXTENSIONS):
            # Erzeuge relativen Pfad mit normierten Slashes
            full_path = os.path.join(root, file_name)
            relative_path = os.path.relpath(full_path, '.').replace('\\', '/')

            checked_count += 1
            found = False

            # Suche die Datei in allen Content-Blöcken
            for i in range(len(content_list)):
                if relative_path in content_list[i]:
                    # Datei gefunden → aus Content entfernen
                    content_list[i] = content_list[i].replace(relative_path, '')
                    found = True

            # Entferne leere Inhalte ohne Upload-Referenz
            if found:
                content_list = [c for c in content_list if 'wp-content/uploads/' in c]
                print(f"✅ Verwendet:         {relative_path}")
            else:
                unused_files.append(relative_path)
                print(f"❌ Nicht verwendet:   {relative_path}")

# Zusammenfassung
print("\nAnalyse abgeschlossen.")
print(f"Geprüfte Dateien: {checked_count}")
print(f"Nicht referenzierte Dateien: {len(unused_files)}\n")

# Ausgabe nicht referenzierter Dateien
print("⚠️ Nicht referenzierte Bilddateien:")
for path in unused_files:
    print(path)

# Schreibe Liste in Datei
with open('unused_images.txt', 'w', encoding='utf-8') as f:
    for path in unused_files:
        f.write(path + '\n')
