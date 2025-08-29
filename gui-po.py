# -*- coding: utf-8 -*-
import os, subprocess, shutil, datetime, threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import polib
from deep_translator import GoogleTranslator

# --- Gettext Tools ---
GETTEXT_BIN = r"C:\gettext\bin"
XGETTEXT = shutil.which("xgettext") or os.path.join(GETTEXT_BIN, "xgettext.exe")
MSGFMT = shutil.which("msgfmt") or os.path.join(GETTEXT_BIN, "msgfmt.exe")

def ensure_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)

def check_tools():
    missing = []
    if not shutil.which("xgettext") and not os.path.exists(XGETTEXT):
        missing.append("xgettext")
    if not shutil.which("msgfmt") and not os.path.exists(MSGFMT):
        missing.append("msgfmt")
    return missing

def create_pot(local_dir, output_dir, plugin_name, box_base_path):
    py_files = [os.path.join(root, f)
                for root, _, files in os.walk(local_dir)
                for f in files if f.endswith(".py")]
    if not py_files:
        raise RuntimeError("Keine .py-Dateien gefunden!")

    ensure_dir(output_dir)
    pot_file = os.path.join(output_dir, f"{plugin_name}.pot")
    relative_paths = [os.path.relpath(f, local_dir).replace("\\", "/") for f in py_files]

    cmd = [XGETTEXT, "--language=Python", "--keyword=_", "--output", pot_file, "--from-code=utf-8"] + relative_paths
    result = subprocess.run(cmd, cwd=local_dir, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"xgettext Fehler:\n{result.stderr}")

    # Pfade anpassen
    with open(pot_file, "r", encoding="utf-8") as f:
        content = f.read()
    for rel_path in relative_paths:
        virtual_path = f"{box_base_path}/{rel_path}"
        content = content.replace(rel_path, virtual_path)
    with open(pot_file, "w", encoding="utf-8") as f:
        f.write(content)

    return pot_file

# --- Übersetzung ---
def translate_text(msg, lang):
    try:
        if not msg.strip():
            return ""
        if lang == "en":  # Englisch bleibt Original
            return msg
        return GoogleTranslator(source="en", target=lang).translate(msg)
    except Exception as e:
        return f"[{lang.upper()}] {msg}"

def create_po_files(pot_file, output_dir, plugin_name, languages, progress_callback=None, log_callback=None):
    pot = polib.pofile(pot_file)

    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M%z")
    base_metadata = {
        "Project-Id-Version": plugin_name,
        "Report-Msgid-Bugs-To": "",
        "POT-Creation-Date": now,
        "PO-Revision-Date": "",
        "Last-Translator": "speedy005",
        "Language-Team": "speedy005",
        "Language": "en",
        "MIME-Version": "1.0",
        "Content-Type": "text/plain; charset=UTF-8",
        "Content-Transfer-Encoding": "8bit",
        "Plural-Forms": "nplurals=2; plural=(n != 1);",
        "X-Poedit-SourceCharset": "UTF-8",
        "X-Generator": "Poedit 3.6",
        "X-Poedit-Basepath": "../../..",
        "X-Poedit-SearchPath-0": os.path.basename(pot_file)
    }

    for lang in languages:
        lang_dir = os.path.join(output_dir, lang, "LC_MESSAGES")
        ensure_dir(lang_dir)
        po_file = os.path.join(lang_dir, f"{plugin_name}.po")
        new_po = polib.POFile()
        new_po.metadata = base_metadata.copy()
        new_po.metadata["Language"] = lang

        total_entries = len(pot)
        for idx, entry in enumerate(pot, 1):
            new_entry = polib.POEntry(msgid=entry.msgid,
                                      msgstr=translate_text(entry.msgid, lang))
            new_po.append(new_entry)
            if progress_callback:
                progress_callback(idx, total_entries)
        new_po.save(po_file)
        if log_callback:
            log_callback(lang, "Fertig")

def compile_mo(output_dir, plugin_name, languages):
    for lang in languages:
        po_file = os.path.join(output_dir, lang, "LC_MESSAGES", f"{plugin_name}.po")
        mo_file = os.path.join(output_dir, lang, "LC_MESSAGES", f"{plugin_name}.mo")
        if os.path.exists(po_file):
            subprocess.run([MSGFMT, po_file, "-o", mo_file])

# --- Sprachen ---
LANGS = {
    "de": "Deutsch", "en": "Englisch", "tr": "Türkisch", "es": "Spanisch",
    "da": "Dänisch", "ar": "Arabisch", "fr": "Französisch", "it": "Italienisch",
    "ru": "Russisch", "zh-cn": "Chinesisch (vereinfacht)", "zh-tw": "Chinesisch (traditionell)",
    "ja": "Japanisch", "pt": "Portugiesisch", "nl": "Niederländisch", "sv": "Schwedisch",
    "pl": "Polnisch", "uk": "Ukrainisch", "cs": "Tschechisch", "ro": "Rumänisch",
    "el": "Griechisch", "hu": "Ungarisch", "fi": "Finnisch", "no": "Norwegisch",
}

# --- GUI ---
class TranslationGUI:
    def __init__(self, root):
        self.root = root
        root.title("Po/Mo Generator by speedy005")
        root.geometry("1000x700")
        root.configure(bg="#2b2b2b")

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TLabel", background="#2b2b2b", foreground="white")
        style.configure("TButton", background="#444", foreground="white", padding=6)
        style.configure("TCheckbutton", background="#2b2b2b", foreground="white")
        style.configure("TEntry", fieldbackground="#3b3b3b", foreground="white")

        ttk.Label(root, text="Quellcode-Ordner").grid(row=0, column=0, sticky="w", padx=10, pady=5)
        self.local_dir_entry = ttk.Entry(root, width=70)
        self.local_dir_entry.grid(row=0, column=1, padx=5)
        ttk.Button(root, text="...", command=self.browse_local).grid(row=0, column=2, padx=5)

        ttk.Label(root, text="Box-Pfad").grid(row=1, column=0, sticky="w", padx=10, pady=5)
        self.box_base_entry = ttk.Entry(root, width=70)
        self.box_base_entry.insert(0, "usr/lib/enigma2/python/Plugins/Extensions")
        self.box_base_entry.grid(row=1, column=1, padx=5)

        ttk.Label(root, text="Sprachen").grid(row=2, column=0, sticky="nw", padx=10, pady=5)
        self.lang_vars = {}
        frame_langs = tk.Frame(root, bg="#2b2b2b")
        frame_langs.grid(row=2, column=1, columnspan=2, sticky="w")

        for i, (code, name) in enumerate(LANGS.items()):
            var = tk.BooleanVar(value=code in ["de", "en", "fr", "tr", "es"])
            cb = ttk.Checkbutton(frame_langs, text=f"{name} ({code})", variable=var)
            cb.grid(row=i // 4, column=i % 4, sticky="w", padx=5, pady=2)
            self.lang_vars[code] = var

        self.start_btn = ttk.Button(root, text="Start", command=self.start)
        self.start_btn.grid(row=3, column=0, columnspan=3, pady=10)

        self.log_listbox = tk.Listbox(root, width=120, height=20, bg="#1e1e1e", fg="white")
        self.log_listbox.grid(row=4, column=0, columnspan=3, padx=10, pady=10)

        self.progress = ttk.Progressbar(root, length=600)
        self.progress.grid(row=5, column=0, columnspan=3, pady=10)
        self.status_label = ttk.Label(root, text="")
        self.status_label.grid(row=6, column=0, columnspan=3)

    def browse_local(self):
        d = filedialog.askdirectory()
        if d:
            self.local_dir_entry.delete(0, tk.END)
            self.local_dir_entry.insert(0, d)

    def start(self):
        local_dir = self.local_dir_entry.get()
        if not os.path.isdir(local_dir):
            messagebox.showerror("Fehler", "Bitte gültigen Quellcode-Ordner wählen!")
            return

        plugin_name = os.path.basename(local_dir)
        output_dir = os.path.join(local_dir, "locale")

        selected = [l for l, v in self.lang_vars.items() if v.get()]
        config = {
            "LOCAL_DIR": local_dir,
            "BOX_BASE_PATH": self.box_base_entry.get(),
            "OUTPUT_DIR": output_dir,
            "PLUGIN_NAME": plugin_name,
            "LANGUAGES": selected
        }

        missing = check_tools()
        if missing:
            messagebox.showerror("Fehlende Tools", f"Bitte installieren: {', '.join(missing)}")
            return

        self.start_btn.config(state="disabled")
        threading.Thread(target=self.run_translation, args=(config,), daemon=True).start()

    def run_translation(self, config):
        try:
            self.log_listbox.insert(tk.END, "Erzeuge .pot...")
            pot_file = create_pot(config["LOCAL_DIR"], config["OUTPUT_DIR"], config["PLUGIN_NAME"], config["BOX_BASE_PATH"])
            self.log_listbox.insert(tk.END, f".pot erstellt: {pot_file}")

            def progress_callback(current, total):
                self.progress["maximum"] = total
                self.progress["value"] = current
                self.status_label.config(text=f"Übersetze Eintrag {current}/{total}")

            def log_callback(lang, msg):
                self.log_listbox.insert(tk.END, f"{LANGS.get(lang, lang)}: {msg}")

            create_po_files(pot_file, config["OUTPUT_DIR"], config["PLUGIN_NAME"], config["LANGUAGES"], progress_callback, log_callback)
            self.progress["value"] = 0
            self.status_label.config(text="Kompiliere .mo Dateien...")
            compile_mo(config["OUTPUT_DIR"], config["PLUGIN_NAME"], config["LANGUAGES"])
            self.status_label.config(text="Fertig")
            messagebox.showinfo("Fertig", "Übersetzung und Kompilierung abgeschlossen!")
        except Exception as e:
            messagebox.showerror("Fehler", str(e))
        finally:
            self.start_btn.config(state="normal")

if __name__ == "__main__":
    root = tk.Tk()
    app = TranslationGUI(root)
    root.mainloop()
