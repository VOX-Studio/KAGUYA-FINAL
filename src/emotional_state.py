import copy
import logging

class EmotionalState:
    def __init__(self, config, logger):
        self.config = config
        self.logger = logger
        self.emotions = copy.deepcopy(config['personality']['initial_emotions'])
        self.decay = config['personality']['emotional_decay']
        
    def update(self, user_text, response_text):
        """Met à jour les émotions en fonction de l'interaction"""
        # Implémentation simple : les émotions évoluent aléatoirement ou selon des mots-clés
        # Ici on applique un facteur de décroissance et on ajoute de petites variations
        for emotion in self.emotions:
            # Décroissance
            self.emotions[emotion] *= self.decay
            
        # Mots-clés basiques
        user_lower = user_text.lower()
        if "triste" in user_lower or "mal" in user_lower:
            self.emotions['tristesse'] += 0.2
            self.emotions['joie'] -= 0.1
        elif "content" in user_lower or "heureux" in user_lower or "joie" in user_lower:
            self.emotions['joie'] += 0.2
            self.emotions['tristesse'] -= 0.1
        elif "colère" in user_lower or "énervé" in user_lower:
            self.emotions['colere'] += 0.2
            self.emotions['joie'] -= 0.1
        elif "surprise" in user_lower or "wow" in user_lower:
            self.emotions['surprise'] += 0.2
            
        # Clamper entre 0 et 1
        for emotion in self.emotions:
            self.emotions[emotion] = max(0.0, min(1.0, self.emotions[emotion]))
            
        self.logger.debug(f"Émotions mises à jour: {self.emotions}")
        
    def get_prompt_suffix(self):
        """Retourne une description textuelle de l'état émotionnel à ajouter au prompt"""
        # Trouver l'émotion dominante
        dominant = max(self.emotions, key=self.emotions.get)
        intensity = self.emotions[dominant]
        
        if intensity < 0.3:
            return ""
        
        descriptions = {
            'joie': "Tu te sens joyeuse et légère.",
            'tristesse': "Une vague de tristesse t'envahit.",
            'colere': "Tu ressens de la colère monter en toi.",
            'peur': "Tu as un peu peur, mais tu restes courageuse.",
            'surprise': "Tu es surprise par ce que tu viens d'entendre."
        }
        
        return descriptions.get(dominant, "")