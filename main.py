#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
from pathlib import Path

# Ajouter le répertoire parent au chemin pour les imports
sys.path.insert(0, str(Path(__file__).parent))

from src.utils import load_config, setup_logging
from src.listener import Listener
from src.brain import Brain
from src.speaker import Speaker

def main():
    # Charger la configuration
    config = load_config()
    
    # Configurer les logs
    logger = setup_logging(config)
    logger.info("Démarrage de Kaguya")
    
    # Initialiser les modules
    try:
        listener = Listener(config, logger)
        brain = Brain(config, logger)
        speaker = Speaker(config, logger)
    except Exception as e:
        logger.error(f"Erreur lors de l'initialisation : {e}")
        sys.exit(1)
    
    logger.info("Kaguya est prête. Parlez-lui dans le microphone.")
    print("\n" + "="*50)
    print("Kaguya est prête. Parlez-lui dans le microphone.")
    print("Appuyez sur Ctrl+C pour quitter.")
    print("="*50 + "\n")
    
    try:
        while True:
            # Écouter
            user_text = listener.listen()
            if not user_text:
                continue
            
            # Réfléchir
            response = brain.think(user_text)
            
            # Parler
            speaker.speak(response)
            
    except KeyboardInterrupt:
        logger.info("Arrêt demandé par l'utilisateur")
        print("\nAu revoir !")
    except Exception as e:
        logger.error(f"Erreur inattendue : {e}", exc_info=True)

if __name__ == "__main__":
    main()