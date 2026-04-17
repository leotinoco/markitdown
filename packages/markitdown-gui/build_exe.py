import PyInstaller.__main__
import os
import sys
import shutil
from pathlib import Path

# Base paths
ROOT_DIR = Path(__file__).parent.parent.parent
GUI_DIR = Path(__file__).parent
MAIN_SCRIPT = GUI_DIR / "markitdown_gui.py"
OUTPUT_NAME = "MarkItDown"

# Find magika data
import magika
MAGIKA_DIR = Path(os.path.dirname(magika.__file__))
magika_data = [
    (str(MAGIKA_DIR / "models"), "magika/models"),
    (str(MAGIKA_DIR / "config"), "magika/config"),
]

# Find customtkinter data
import customtkinter
CTK_DIR = Path(os.path.dirname(customtkinter.__file__))
ctk_data = [
    (str(CTK_DIR), "customtkinter"),
]

# Find tkinterdnd2 data
import tkinterdnd2
TKDND_DIR = Path(os.path.dirname(tkinterdnd2.__file__))
tkdnd_data = [
    (str(TKDND_DIR), "tkinterdnd2"),
]

# Combine data files
data_args = []
for src, dst in magika_data + ctk_data + tkdnd_data:
    data_args.extend(["--add-data", f"{src}{os.pathsep}{dst}"])

# Build command parts
args = [
    str(MAIN_SCRIPT),
    "--name", OUTPUT_NAME,
    "--onefile",
    "--windowed",
    "--clean",
    # Hidden imports for markitdown and its many dependencies
    "--hidden-import", "markitdown",
    "--hidden-import", "magika",
    "--hidden-import", "pandas",
    "--hidden-import", "openpyxl",
    "--hidden-import", "pdfminer",
    "--hidden-import", "pdfplumber",
    "--hidden-import", "mammoth",
    "--hidden-import", "pptx",
    "--hidden-import", "pydub",
    "--hidden-import", "speech_recognition",
    "--hidden-import", "charset_normalizer",
    "--hidden-import", "beautifulsoup4",
    "--hidden-import", "markdownify",
    "--hidden-import", "defusedxml",
    "--hidden-import", "PIL.Image",
    "--hidden-import", "PIL.ImageTk",
    "--hidden-import", "tkinterdnd2",
    # Collect all for complex packages
    "--collect-all", "markitdown",
    "--collect-all", "magika",
    "--collect-all", "customtkinter",
]

# Add data files
args.extend(data_args)

print(f"Iniciando compilación de {OUTPUT_NAME}...")
print(f"Directorio de origen: {GUI_DIR}")

PyInstaller.__main__.run(args)

print("\n¡Compilación finalizada!")
print(f"El ejecutable se encuentra en: {GUI_DIR / 'dist' / (OUTPUT_NAME + '.exe')}")
