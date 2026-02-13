import subprocess
import tempfile
import os
import logging
import sounddevice as sd
import soundfile as sf
from pathlib import Path

class Speaker:
    def __init__(self, config, logger):
        self.config = config
        self.logger = logger
        self.model_path = Path(config['models']['tts_model_path'])
        
        # Vérifier que le modèle TTS existe
        if not self.model_path.exists():
            self.logger.error(f"Modèle TTS introuvable à {self.model_path}")
            raise FileNotFoundError(f"Modèle TTS introuvable à {self.model_path}")
        
        # Ici, on suppose que GPT-SoVITS fournit un script d'inférence en ligne de commande
        # Exemple d'utilisation : python GPT_SoVITS/inference.py --model_dir path --text "Bonjour" --output tmp.wav
        # À adapter selon la structure réelle de GPT-SoVITS
        self.inference_script = self.model_path / "inference.py"  # À ajuster
        
        if not self.inference_script.exists():
            # Chercher dans le répertoire parent ou autre
            # Pour simplifier, on utilisera un TTS de fallback (espeak) si GPT-SoVITS n'est pas trouvé
            self.logger.warning("Script d'inférence GPT-SoVITS non trouvé. Utilisation de fallback (espeak).")
            self.use_fallback = True
        else:
            self.use_fallback = False
            
    def speak(self, text):
        """Convertit le texte en parole et le joue"""
        if self.use_fallback:
            self._fallback_speak(text)
        else:
            self._gpt_sovits_speak(text)
    
    def _gpt_sovits_speak(self, text):
        """Utilise GPT-SoVITS pour la synthèse"""
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            output_path = tmp.name
        
        try:
            cmd = [
                "python", str(self.inference_script),
                "--model_dir", str(self.model_path),
                "--text", text,
                "--output", output_path
            ]
            self.logger.debug(f"Exécution de la commande TTS: {' '.join(cmd)}")
            subprocess.run(cmd, check=True, capture_output=True)
            
            # Lire le fichier audio et le jouer
            data, samplerate = sf.read(output_path)
            sd.play(data, samplerate)
            sd.wait()  # Attendre la fin de la lecture
        except Exception as e:
            self.logger.error(f"Erreur TTS: {e}")
            self._fallback_speak(text)
        finally:
            os.unlink(output_path)
    
    def _fallback_speak(self, text):
        """Synthèse de secours avec espeak (si installé) ou simple print"""
        try:
            # Utiliser espeak (sous Linux) ou say (sous macOS) ou fallback print
            import platform
            system = platform.system()
            if system == "Linux":
                subprocess.run(["espeak", text], check=True)
            elif system == "Darwin":
                subprocess.run(["say", text], check=True)
            else:
                # Windows : essayer avec PowerShell
                ps_cmd = f"Add-Type -AssemblyName System.Speech; (New-Object System.Speech.Synthesis.SpeechSynthesizer).Speak('{text}')"
                subprocess.run(["powershell", "-Command", ps_cmd], check=True)
        except:
            self.logger.warning("Aucun TTS disponible. Impression du texte.")
            print(f"Kaguya dit: {text}")