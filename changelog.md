# Journal des modifications - Projet Kaguya

## [0.1.0] - 2026-02-13
### Ajouté
- Structure complète du projet avec dossiers : config, src, data, models
- Fichier de configuration `config/config.yaml`
- Module `src/listener.py` : capture audio et transcription avec faster-whisper
- Module `src/brain.py` : génération de réponse avec llama-cpp-python, intégration mémoire et émotions
- Module `src/speaker.py` : synthèse vocale avec GPT-SoVITS (fallback inclus)
- Module `src/memory.py` : mémoire court terme (liste) et long terme (ChromaDB)
- Module `src/emotional_state.py` : gestion des émotions et désirs
- Module `src/utils.py` : utilitaires (config, logging)
- Script principal `main.py` : boucle principale
- Script de build `build_exe.py` pour générer un exécutable avec PyInstaller
- `requirements.txt` : dépendances
- `README.md` : documentation
- `changelog.md` : ce fichier

### Notes
- Le module TTS nécessite un modèle GPT-SoVITS préalablement entraîné et placé dans `models/tts/`.
- Pour une première exécution sans TTS, le fallback utilisera la synthèse système (espeak, say, ou PowerShell).
- Les émotions évoluent selon des mots-clés simples ; à améliorer ultérieurement.