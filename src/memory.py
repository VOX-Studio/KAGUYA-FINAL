import chromadb
from chromadb.config import Settings
import logging
from datetime import datetime

class Memory:
    def __init__(self, config, logger):
        self.config = config
        self.logger = logger
        self.short_term = []  # liste de tuples (user, assistant)
        self.short_term_size = config['memory']['short_term_size']
        
        # Mémoire à long terme (vectorielle)
        self.long_term_enabled = config['memory']['long_term']
        if self.long_term_enabled:
            db_path = config['memory']['long_term_db_path']
            self.chroma_client = chromadb.PersistentClient(path=db_path)
            # Créer ou récupérer la collection
            self.collection = self.chroma_client.get_or_create_collection(
                name="conversations",
                metadata={"hnsw:space": "cosine"}
            )
            self.logger.info(f"Mémoire à long terme initialisée à {db_path}")
    
    def add_exchange(self, user_text, assistant_text):
        """Ajoute un échange à la mémoire court terme et long terme"""
        # Court terme
        self.short_term.append((user_text, assistant_text))
        if len(self.short_term) > self.short_term_size:
            self.short_term.pop(0)
        
        # Long terme
        if self.long_term_enabled:
            timestamp = datetime.now().isoformat()
            # Créer un document combiné
            doc = f"User: {user_text}\nKaguya: {assistant_text}"
            self.collection.add(
                documents=[doc],
                metadatas=[{"timestamp": timestamp}],
                ids=[f"conv_{timestamp}_{hash(doc)}"]
            )
            self.logger.debug("Échange ajouté à la mémoire long terme")
    
    def get_relevant_context(self, query, n_results=3):
        """Récupère les souvenirs pertinents depuis la mémoire long terme"""
        if not self.long_term_enabled:
            return []
        results = self.collection.query(query_texts=[query], n_results=n_results)
        if results['documents']:
            return results['documents'][0]
        return []
    
    def get_short_term_context(self):
        """Retourne le contexte de la mémoire court terme formaté pour le LLM"""
        context = ""
        for user, assistant in self.short_term:
            context += f"Utilisateur: {user}\nKaguya: {assistant}\n"
        return context