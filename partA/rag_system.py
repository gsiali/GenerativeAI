"""RAG System with OpenAI embeddings and sklearn similarity search."""

import json
import os
import hashlib
from typing import List, Dict
from openai import OpenAI
from dotenv import load_dotenv
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

load_dotenv()


class InMemoryRAG:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.kb_path = os.path.join(os.path.dirname(__file__), 'knowledge_base', 'functions.txt')
        self.emb_path = os.path.join(os.path.dirname(__file__), 'knowledge_base', 'embeddings.json')
        self.chunks: List[str] = []
        self.embeddings: List[List[float]] = []
        self.model = "text-embedding-3-small"
    
    def _compute_kb_hash(self) -> str:
        """Compute SHA256 hash of knowledge base file."""
        sha256_hash = hashlib.sha256()
        with open(self.kb_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    
    def _load_chunks(self):
        with open(self.kb_path, 'r', encoding='utf-8') as f:
            self.chunks = [chunk.strip() for chunk in f.read().split('---') if len(chunk.strip()) > 20]
    
    def _generate_embeddings(self):
        current_hash = self._compute_kb_hash()
        
        # Try to load cached embeddings
        if os.path.exists(self.emb_path):
            try:
                with open(self.emb_path, 'r') as f:
                    data = json.load(f)
                    if data.get("kb_hash") == current_hash:
                        self.embeddings = data["embeddings"]
                        return
            except (json.JSONDecodeError, KeyError):
                pass
        
        # Generate new embeddings
        print(f"Generating embeddings for {len(self.chunks)} chunks...")
        self.embeddings = [emb.embedding for emb in self.client.embeddings.create(
            model=self.model, input=self.chunks, encoding_format="float").data]
        
        os.makedirs(os.path.dirname(self.emb_path), exist_ok=True)
        with open(self.emb_path, 'w') as f:
            json.dump({
                "chunks": self.chunks, 
                "embeddings": self.embeddings, 
                "model": self.model,
                "kb_hash": current_hash
            }, f)
        print("Embeddings generated and cached.")
    
    def retrieve_relevant_functions(self, query: str, top_k: int = 3) -> List[Dict]:
        response = self.client.embeddings.create(model=self.model, input=query, encoding_format="float")
        query_vec = np.array(response.data[0].embedding).reshape(1, -1)
        similarities = cosine_similarity(query_vec, np.array(self.embeddings))[0]
        top_indices = np.argsort(similarities)[-top_k:][::-1]
        
        return [{"text": self.chunks[idx], "score": float(similarities[idx]), "rank": i} 
                for i, idx in enumerate(top_indices, 1)]
    
    def initialize(self):
        self._load_chunks()
        self._generate_embeddings()
