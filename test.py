# -*- coding: utf-8 -*-
import os
import polib
from deep_translator import GoogleTranslator
from concurrent.futures import ThreadPoolExecutor, as_completed

# --- Konfiguration ---
source_dir = r"C:\Plugin\locale"   # Ordner mit Original-.po-Dateien
output_dir = r"C:\Plugin\locale"   # Ausgabeverzeichnis
languages = {
    "en": "English",
    "tr": "Turkish",
    "es": "Spanish",
    "da": "Danish",
    "ar": "Arabic"
}
max_threads = 5  # Anzahl paralleler Übersetzungen

# --- Funktionen ---
def translate_entry(entry, lang_code):
    translator = GoogleTranslator(source='auto', target=lang_code)
    return polib.POEntry(msgid=entry.msgid, msgstr=translator.translate(entry.msgid))

def translate_po(po_file, lang_code):
    po = polib.pofile(po_file)
    translated_po = polib.POFile()
    translated_po.metadata = po.metadata.copy()

    # Parallele Übersetzung
    with ThreadPoolExecutor(max_workers=max_threads) as executor:
        future_to_entry = {executor.submit(translate_entry, entry, lang_code): entry for entry in po}
        for future in as_completed(future_to_entry):
            translated_po.append(future.result())

    # Pfade für Ausgabe
    lang_path = os.path.join(output_dir, lang_code, "LC_MESSAGES")
    os.makedirs(lang_path, exist_ok=True)
    po_file_path = os.path.join(lang_path, "speedyServiceScanUpdates.po")
    mo_file_path = os.path.join(lang_path, "speedyServiceScanUpdates.mo")
    translated_po.save(po_file_path)
    translated_po.save_as_mofile(mo_file_path)
    print(f"[{languages[lang_code]}] Übersetzung fertig: {po_file_path} / {mo_file_path}")

# --- Hauptschleife ---
for root, dirs, files in os.walk(source_dir):
    for file in files:
        if file.endswith(".po"):
            source_po_file = os.path.join(root, file)
            print(f"Verarbeite: {source_po_file}")
            for lang_code in languages:
                translate_po(source_po_file, lang_code)

print("Alle Übersetzungen abgeschlossen!")
