with open('unused_images.txt', 'r', encoding='utf-8') as infile, open('delete_attachments.sql', 'w', encoding='utf-8') as outfile:
    outfile.write("-- SQL-Befehle zum Löschen verwaister Medien aus wp_posts (Typ: attachment)\n\n")
    for line in infile:
        path = line.strip()
        if path:
            outfile.write(f"DELETE FROM wp_posts WHERE post_type = 'attachment' AND guid LIKE '%{path}';\n")