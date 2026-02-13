from llama_cpp import Llama
import logging
from src.memory import Memory
from src.emotional_state import EmotionalState

class Brain:
    def __init__(self, config, logger):
        self.config = config
        self.logger = logger
        self.memory = Memory(config, logger)
        self.emotions = EmotionalState(config, logger)
        
        # Chargement du modèle LLM
        model_path = config['models']['llm_model_path']
        self.logger.info(f"Chargement du modèle LLM depuis {model_path}...")
        self.llm = Llama(
            model_path=model_path,
            n_ctx=2048,  # Contexte maximum
            n_threads=4,  # Ajuster selon CPU
            verbose=False
        )
        self.logger.info("Modèle LLM chargé.")
        
        self.name = config['personality']['name']
        self.system_prompt = config['personality']['system_prompt']
        
    def think(self, user_text):
        """Génère une réponse à partir du texte utilisateur"""
        # Récupérer le contexte de mémoire
        short_context = self.memory.get_short_term_context()
        long_context = self.memory.get_relevant_context(user_text)
        
        # Obtenir l'état émotionnel
        emotional_suffix = self.emotions.get_prompt_suffix()
        
        # Construire le prompt
        prompt = f"{self.system_prompt}\n\n"
        if emotional_suffix:
            prompt += f"État intérieur: {emotional_suffix}\n\n"
        if long_context:
            prompt += "Souvenirs pertinents:\n"
            for mem in long_context:
                prompt += f"- {mem}\n"
            prompt += "\n"
        if short_context:
            prompt += "Conversation récente:\n"
            prompt += short_context + "\n"
        prompt += f"Utilisateur: {user_text}\n"
        prompt += f"{self.name}:"
        
        self.logger.debug(f"Prompt envoyé au LLM:\n{prompt}")
        
        # Générer la réponse
        output = self.llm(
            prompt,
            max_tokens=256,
            temperature=0.7,
            top_p=0.95,
            stop=["Utilisateur:", f"{self.name}:"],
            echo=False
        )
        
        response = output['choices'][0]['text'].strip()
        self.logger.info(f"Réponse générée: {response}")
        
        # Mettre à jour la mémoire et les émotions
        self.memory.add_exchange(user_text, response)
        self.emotions.update(user_text, response)
        
        return response