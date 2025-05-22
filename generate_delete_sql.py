with open('unused_images.txt', 'r', encoding='utf-8') as infile, open('delete_attachments.sql', 'w', encoding='utf-8') as outfile:
    paths = [line.strip() for line in infile if line.strip()]

    if paths:
        outfile.write("-- SQL-Befehl zum Löschen verwaister Medien aus wp_posts (Typ: attachment)\n\n")
        outfile.write("DELETE FROM wp_posts\n")
        outfile.write("WHERE post_type = 'attachment'\n")
        outfile.write("AND guid IN (\n")

        for i, path in enumerate(paths):
            end = ",\n" if i < len(paths) - 1 else "\n"
            outfile.write(f"    '{path}'{end}")

        outfile.write(");\n")
    else:
        outfile.write("-- Keine Pfade gefunden. Datei unused_images.txt ist leer oder ungültig.\n")
