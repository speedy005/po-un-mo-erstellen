# -*- coding: utf-8 -*-
import os
import polib
from deep_translator import GoogleTranslator

# --- Konfiguration ---
source_dir = r"C:\Plugin\locale"  # Ordner mit allen Original-.po-Dateien
output_dir = r"C:\Plugin\locale"  # Ausgabeverzeichnis für die übersetzten Dateien

languages = {
    "en": "English",
    "tr": "Turkish",
    "es": "Spanish",
    "da": "Danish",
    "ar": "Arabic"
}

translator = GoogleTranslator(source='auto', target='en')  # default target, wird pro Sprache geändert

# --- Durchlaufe alle .po Dateien ---
for root, dirs, files in os.walk(source_dir):
    for file in files:
        if file.endswith(".po"):
            source_po_file = os.path.join(root, file)
            print(f"Verarbeite: {source_po_file}")
            po = polib.pofile(source_po_file)

            for lang_code, lang_name in languages.items():
                lang_path = os.path.join(output_dir, lang_code, "LC_MESSAGES")
                os.makedirs(lang_path, exist_ok=True)

                translated_po = polib.POFile()
                translated_po.metadata = po.metadata.copy()

                print(f"Übersetze in {lang_name}...")
                translator = GoogleTranslator(source='auto', target=lang_code)

                for entry in po:
                    translated_entry = polib.POEntry(
                        msgid=entry.msgid,
                        msgstr=translator.translate(entry.msgid)
                    )
                    translated_po.append(translated_entry)

                # Speichere mit festem Namen
                po_file_path = os.path.join(lang_path, "speedyServiceScanUpdates.po")
                translated_po.save(po_file_path)

                mo_file_path = os.path.join(lang_path, "speedyServiceScanUpdates.mo")
                translated_po.save_as_mofile(mo_file_path)

                print(f"{lang_name} fertig: {po_file_path} / {mo_file_path}")

print("Alle Übersetzungen abgeschlossen!")
