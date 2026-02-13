#!/usr/bin/env python3
# Script pour construire un exécutable unique de Kaguya avec PyInstaller

import PyInstaller.__main__
import sys
from pathlib import Path

def build():
    # Déterminer le chemin du script principal
    main_script = Path(__file__).parent / "main.py"
    
    # Options de PyInstaller
    args = [
        str(main_script),
        "--name=Kaguya",
        "--onefile",          # Un seul fichier .exe
        "--console",          # Garder la console pour les logs
        "--add-data", f"config{Path.pathsep}config",  # Inclure le dossier config
        "--add-data", f"models{Path.pathsep}models",  # Inclure les modèles (attention à la taille)
        "--hidden-import", "llama_cpp",
        "--hidden-import", "faster_whisper",
        "--hidden-import", "chromadb",
        "--hidden-import", "sounddevice",
        "--hidden-import", "soundfile",
        "--hidden-import", "yaml",
        "--collect-all", "chromadb",  # Inclure toutes les données de chromadb
        "--collect-all", "faster_whisper",
    ]
    
    # Sur Windows, on peut ajouter une icône
    # icone = Path(__file__).parent / "icon.ico"
    # if icone.exists():
    #     args.append(f"--icon={icone}")
    
    print("Construction de l'exécutable Kaguya...")
    PyInstaller.__main__.run(args)
    print("Terminé. L'exécutable se trouve dans le dossier dist/")

if __name__ == "__main__":
    build()