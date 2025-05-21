# WP Unused Files Cleaner

This Python-based tool helps you identify unused image files in your WordPress installation – **without relying on plugins**.

WordPress media libraries can easily grow over time. After years of content creation, your `/wp-content/uploads/` folder may contain **thousands of unused images**, thumbnails, or outdated media. Plugins like Media Cleaner or DNUI try to help – but they often run directly on your WordPress instance, which may cause performance issues or accidentally delete still-used files (especially when using PageBuilders or custom fields).

**This script-based solution works externally**, giving you full control and transparency.

---

## 📖 More Information (German)

A full step-by-step tutorial is available on my blog, including screenshots, background, and alternative methods:

👉 [Zum vollständigen Blogbeitrag (Deutsch)](https://draeger-it.blog/wordpress-aufraeumen-so-entlarvst-du-ungenutzte-dateien-mit-python/)

---

## 🔍 What It Does

1. **Exports post content** from your WordPress database (`wp_posts`).
2. **Scans your upload folder** recursively for image files.
3. **Compares** both data sources to detect files that are no longer referenced.
4. **Generates a report** (`unused_images.txt`) and an optional SQL file for database cleanup.

---

## 📁 Project Structure

| File / Folder                      | Description |
|-----------------------------------|-------------|
| [`findunusedfiles.py`](./findunusedfiles.py) | Scans the local upload directory and compares it to post content in the JSON export. |
| [`generate_delete_sql.py`](./generate_delete_sql.py) | Creates SQL `DELETE` statements for unused media entries in the `wp_posts` table. |
| [`sql/export_statement_wp_posts.sql`](./sql/export_statement_wp_posts.sql) | Sample SQL to export ID, title, and content from WordPress. |
| [`sql/delete_unused_media_sample.sql`](./sql/delete_unused_media_sample.sql) | Sample output with generated SQL statements for deletion. |
| [`sample_output/unused_images.txt`](./sample_output/unused_images.txt) | Contains all unreferenced image paths. |
| [`images/Ausgabe-Suche-nach-nicht-benutzen-Bildern.png`](./images/Ausgabe-Suche-nach-nicht-benutzen-Bildern.png) | Example of console output from the scanner script. |

---

