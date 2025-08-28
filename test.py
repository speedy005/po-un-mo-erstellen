# -*- coding: utf-8 -*-
import polib
from deep_translator import GoogleTranslator
import os

# --- Konfiguration ---
base_path = r"C:\Plugin\locale"  # Basisordner mit .po-Dateien

# Sprachen, die übersetzt werden sollen
languages = {
    "en": "English",
    "tr": "Turkish",
    "es": "Spanish",
    "da": "Danish",
    "ar": "Arabic"
}

# --- Translator initialisieren ---
translator = GoogleTranslator(source='auto', target='en')  # Default auf Englisch, später je Sprache ändern

# --- Alle .po Dateien finden ---
po_files = []
for root, dirs, files in os.walk(base_path):
    for file in files:
        if file.endswith(".po"):
            po_files.append(os.path.join(root, file))

if not po_files:
    raise FileNotFoundError(f"Keine .po Dateien gefunden im Ordner: {base_path}")

# --- Übersetzen ---
for po_file in po_files:
    po = polib.pofile(po_file)
    print(f"Verarbeite: {po_file}")

    for lang_code, lang_name in languages.items():
        translated_po = polib.POFile()
        translated_po.metadata = po.metadata.copy()

        print(f"  Übersetze in {lang_name}...")

        for entry in po:
            translated_entry = polib.POEntry(
                msgid=entry.msgid,
                msgstr=GoogleTranslator(source='auto', target=lang_code).translate(entry.msgid)
            )
            translated_po.append(translated_entry)

        # Pfad für die übersetzte Datei
        lang_path = os.path.join(base_path, lang_code, "LC_MESSAGES")
        os.makedirs(lang_path, exist_ok=True)

        po_file_path = os.path.join(lang_path, os.path.basename(po_file))
        translated_po.save(po_file_path)

        mo_file_path = os.path.join(lang_path, os.path.splitext(os.path.basename(po_file))[0] + ".mo")
        translated_po.save_as_mofile(mo_file_path)

        print(f"    Fertig: {po_file_path} / {mo_file_path}")

print("Alle Übersetzungen abgeschlossen!")
