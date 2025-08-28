# -*- coding: utf-8 -*-
import os
import subprocess

# --- Konfiguration ---
PLUGIN_DIR = r"C:\Plugin"
OUTPUT_DIR = os.path.join(PLUGIN_DIR, "locale")
LANGUAGES = ["de", "en", "tr", "es", "da", "ar"]
POT_FILE = os.path.join(OUTPUT_DIR, "plugin.pot")

# Vollständiger Pfad zu gettext-Tools
GETTEXT_BIN = r"C:\gettext\bin"  # <--- anpassen
MSGFMT = os.path.join(GETTEXT_BIN, "msgfmt.exe")

def ensure_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)

# --- .mo-Dateien kompilieren ---
for lang in LANGUAGES:
    po_file = os.path.join(OUTPUT_DIR, lang, "LC_MESSAGES", "plugin.po")
    mo_file = os.path.join(OUTPUT_DIR, lang, "LC_MESSAGES", "plugin.mo")
    if os.path.exists(po_file):
        cmd = [MSGFMT, po_file, "-o", mo_file]
        print(f"Kompiliere {po_file} → {mo_file}...")
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"Fehler bei {lang}: {result.stderr}")
        else:
            print(f".mo erstellt: {mo_file}")
    else:
        print(f"PO-Datei fehlt: {po_file}")
