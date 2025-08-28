# -*- coding: utf-8 -*-
import os
import polib
from deep_translator import GoogleTranslator

# --- Konfiguration ---
source_po_file = r"C:\Plugin\locale\de\LC_MESSAGES\plugin.po"  # Originaldatei, beliebiger Name
output_dir = r"C:\Plugin\locale"

# Sprachen, die übersetzt werden sollen
languages = {
    "en": "English",
    "tr": "Turkish",
    "es": "Spanish",
    "da": "Danish",
    "ar": "Arabic"
}

# --- Translator initialisieren ---
translator = GoogleTranslator(source='auto')

# Prüfen, ob die Originaldatei existiert
if not os.path.exists(source_po_file):
    raise FileNotFoundError(f"Datei nicht gefunden: {source_po_file}")

# Lade die Original .po Datei
po = polib.pofile(source_po_file)

# Für jede Sprache übersetzen
for lang_code, lang_name in languages.items():
    lang_path = os.path.join(output_dir, lang_code, "LC_MESSAGES")
    os.makedirs(lang_path, exist_ok=True)

    translated_po = polib.POFile()
    translated_po.metadata = po.metadata.copy()

    print(f"Übersetze in {lang_name}...")

    for entry in po:
        translated_entry = polib.POEntry(
            msgid=entry.msgid,
            msgstr=translator.translate(entry.msgid, target=lang_code)
        )
        translated_po.append(translated_entry)

    # Nach der Übersetzung: feste Namen setzen
    po_file_path = os.path.join(lang_path, "speedyServiceScanUpdates.po")
    mo_file_path = os.path.join(lang_path, "speedyServiceScanUpdates.mo")

    translated_po.save(po_file_path)
    translated_po.save_as_mofile(mo_file_path)

    print(f"{lang_name} fertig: {po_file_path} / {mo_file_path}")

print("Alle Übersetzungen abgeschlossen!")
