import sounddevice as sd
import numpy as np
import faster_whisper
import logging
import queue
import sys
import time
from pathlib import Path

class Listener:
    def __init__(self, config, logger):
        self.config = config
        self.logger = logger
        self.sample_rate = config['audio']['sample_rate']
        self.device = config['audio']['input_device_index']
        self.silence_threshold = config['audio']['silence_threshold']
        
        # Queue pour les segments audio
        self.audio_queue = queue.Queue()
        
        # Initialisation du modèle STT
        self.logger.info("Chargement du modèle STT...")
        model_size = config['models']['stt_model_size']
        self.model = faster_whisper.WhisperModel(model_size, device="cpu", compute_type="int8")
        self.logger.info("Modèle STT chargé.")
        
    def audio_callback(self, indata, frames, time_info, status):
        """Callback appelé pour chaque bloc audio"""
        if status:
            self.logger.warning(f"Statut audio: {status}")
        self.audio_queue.put(indata.copy())
        
    def listen(self):
        """Capture l'audio du microphone et retourne le texte transcrit"""
        self.logger.info("En écoute... Parlez.")
        
        # Paramètres d'enregistrement
        blocksize = 1024
        samplerate = self.sample_rate
        channels = 1  # mono
        
        # Détection de silence simple
        silent_chunks = 0
        max_silent_chunks = int(samplerate / blocksize * 1.5)  # 1.5 secondes de silence
        recording = []
        
        # Démarrer le flux
        with sd.InputStream(samplerate=samplerate, 
                           device=self.device,
                           channels=channels,
                           callback=self.audio_callback,
                           blocksize=blocksize):
            
            while True:
                # Récupérer le bloc audio
                try:
                    audio_chunk = self.audio_queue.get(timeout=0.5)
                except queue.Empty:
                    continue
                
                # Calculer le niveau sonore (RMS)
                rms = np.sqrt(np.mean(audio_chunk**2))
                
                if rms < self.silence_threshold:
                    silent_chunks += 1
                else:
                    silent_chunks = 0
                
                recording.append(audio_chunk)
                
                # Si assez de silence, arrêter l'enregistrement
                if silent_chunks > max_silent_chunks and len(recording) > max_silent_chunks:
                    break
        
        # Convertir l'enregistrement en un seul tableau
        if not recording:
            return ""
        audio_data = np.concatenate(recording, axis=0).flatten()
        audio_data = (audio_data * 32767).astype(np.int16)  # Conversion en int16 pour Whisper
        
        # Transcription
        self.logger.info("Transcription en cours...")
        segments, info = self.model.transcribe(audio_data, language="fr", beam_size=5)
        text = " ".join([segment.text for segment in segments])
        self.logger.info(f"Transcription: {text}")
        return text