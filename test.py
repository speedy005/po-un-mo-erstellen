# -*- coding: utf-8 -*-
import polib
from deep_translator import GoogleTranslator
import os

# --- Konfiguration ---
source_po_file = r"C:\Plugin\locale\messages.po"  # Pfad zu deiner Original-.po
output_dir = r"C:\Plugin\locale"                  # Basis-Ordner für Übersetzungen

# Sprachen, die übersetzt werden sollen
languages = {
    "en": "English",
    "tr": "Turkish",
    "es": "Spanish",
    "da": "Danish",
    "ar": "Arabic"
}

# Translator initialisieren
translator = GoogleTranslator(source='auto')

# .po Datei laden
po = polib.pofile(source_po_file)

for lang_code in languages.keys():
    # Erstelle Ordnerstruktur
    lang_path = os.path.join(output_dir, lang_code, "LC_MESSAGES")
    os.makedirs(lang_path, exist_ok=True)

    # Neues .po Objekt für die Übersetzung
    translated_po = polib.POFile()
    translated_po.metadata = po.metadata.copy()

    print(f"Übersetze in {languages[lang_code]}...")

    for entry in po:
        translated_entry = polib.POEntry(
            msgid=entry.msgid,
            msgstr=translator.translate(entry.msgid, target=lang_code)
        )
        translated_po.append(translated_entry)

    # .po Datei speichern
    po_file_path = os.path.join(lang_path, "speedyServiceScanUpdates.po")
    translated_po.save(po_file_path)

    # .mo Datei erstellen
    mo_file_path = os.path.join(lang_path, "speedyServiceScanUpdates.mo")
    translated_po.save_as_mofile(mo_file_path)

    print(f"{languages[lang_code]} fertig: {po_file_path} / {mo_file_path}")

print("Alle Übersetzungen abgeschlossen!")
