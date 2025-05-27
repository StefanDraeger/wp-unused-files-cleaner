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
"""

import os
import json
import sys

# Konfiguration
UPLOADS_DIR = './wp-content/uploads'
JSON_FILE = './wp_posts.json'
IMAGE_EXTENSIONS = ('.jpg', '.jpeg', '.png', '.tiff', '.bmp')


def format_size(bytes_value):
    if bytes_value < 1024:
        return f"{bytes_value} Bytes"
    elif bytes_value < 1024 ** 2:
        return f"{bytes_value / 1024:.2f} KB"
    elif bytes_value < 1024 ** 3:
        return f"{bytes_value / (1024 ** 2):.2f} MB"
    else:
        return f"{bytes_value / (1024 ** 3):.2f} GB"


def load_json_data(json_file):
    if not os.path.isfile(json_file):
        print(f"❌ Fehler: Datei '{json_file}' nicht gefunden.")
        sys.exit(1)
    try:
        with open(json_file, 'r', encoding='utf-8') as file:
            raw_json = json.load(file)
    except json.JSONDecodeError:
        print(f"❌ Fehler: Datei '{json_file}' ist kein gültiges JSON.")
        sys.exit(1)

    for obj in raw_json:
        if obj.get('type') == 'table' and obj.get('name') == 'wp_posts':
            return obj.get('data', [])
    print("❌ Fehler: Keine Daten zur Tabelle 'wp_posts' gefunden.")
    sys.exit(1)


def scan_uploads(content_list):
    if not os.path.isdir(UPLOADS_DIR):
        print(f"❌ Fehler: Upload-Verzeichnis '{UPLOADS_DIR}' nicht gefunden.")
        sys.exit(1)

    unused_files = []
    checked_count = 0

    for root, dirs, files in os.walk(UPLOADS_DIR):
        for file_name in files:
            if file_name.lower().endswith(IMAGE_EXTENSIONS):
                full_path = os.path.join(root, file_name)
                relative_path = os.path.relpath(full_path, '.').replace('\\', '/')
                checked_count += 1
                found = False

                for i in range(len(content_list)):
                    if relative_path in content_list[i]:
                        content_list[i] = content_list[i].replace(relative_path, '')
                        found = True

                if found:
                    content_list = [c for c in content_list if 'wp-content/uploads/' in c]
                    print(f"✅ Verwendet:         {relative_path}")
                else:
                    unused_files.append(relative_path)
                    print(f"❌ Nicht verwendet:   {relative_path}")
    return unused_files, checked_count


def write_unused_list(unused_files):
    with open('unused_images.txt', 'w', encoding='utf-8') as f:
        for path in unused_files:
            f.write(path + '\n')
    print("📝 Datei 'unused_images.txt' wurde erstellt.")


def write_sql_files(unused_files):
    with open('delete_attachments.sql', 'w', encoding='utf-8') as del_out:
        del_out.write("-- SQL-Befehl zum Löschen verwaister Medien aus wp_posts (Typ: attachment)\n\n")
        del_out.write("DELETE FROM wp_posts\nWHERE post_type = 'attachment'\nAND guid IN (\n")
        for i, path in enumerate(unused_files):
            end = ",\n" if i < len(unused_files) - 1 else "\n"
            del_out.write(f"    '{path}'{end}")
        del_out.write(");\n")
    print("🗑️  Datei 'delete_attachments.sql' wurde erzeugt.")

    with open('select_attachments.sql', 'w', encoding='utf-8') as sel_out:
        sel_out.write("-- SQL-Befehl zur Prüfung verwaister Medien aus wp_posts (Typ: attachment)\n\n")
        sel_out.write("SELECT ID, guid FROM wp_posts\nWHERE post_type = 'attachment'\nAND guid IN (\n")
        for i, path in enumerate(unused_files):
            end = ",\n" if i < len(unused_files) - 1 else "\n"
            sel_out.write(f"    '{path}'{end}")
        sel_out.write(");\n")
    print("🔍 Datei 'select_attachments.sql' wurde erzeugt.")


def write_log(unused_files, checked_count):
    total_size_bytes = sum(
        os.path.getsize(os.path.join('.', path)) for path in unused_files if os.path.isfile(os.path.join('.', path))
    )
    formatted_size = format_size(total_size_bytes)
    with open('cleanup_log.txt', 'w', encoding='utf-8') as log:
        log.write("📄 Ausführungsprotokoll – WordPress Dateiaufräumung\n")
        log.write("==================================================\n\n")
        log.write(f"📦 Verarbeitete Dateien:       {checked_count}\n")
        log.write(f"🗂️  Ungenutzte Dateien gefunden: {len(unused_files)}\n")
        log.write(f"💾 Speicherverbrauch (gesamt):  {formatted_size}\n\n")
        log.write("📝 Die folgenden Dateien wurden erstellt:\n")
        log.write("- unused_images.txt\n")
        log.write("- delete_attachments.sql\n")
        log.write("- select_attachments.sql\n")
    print("🧾 Logdatei 'cleanup_log.txt' wurde erstellt.")


def main():
    entries = load_json_data(JSON_FILE)
    content_list = [entry.get('Content', '') for entry in entries]
    unused_files, checked_count = scan_uploads(content_list)

    print("\nAnalyse abgeschlossen.")
    print(f"Geprüfte Dateien: {checked_count}")
    print(f"Nicht referenzierte Dateien: {len(unused_files)}\n")

    if unused_files:
        print("⚠️ Nicht referenzierte Bilddateien:")
        for path in unused_files:
            print(path)
        write_unused_list(unused_files)
        write_sql_files(unused_files)
        write_log(unused_files, checked_count)


if __name__ == "__main__":
    main()
