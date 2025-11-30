"""
In-Memory RAG System
Retrieval-Augmented Generation using OpenAI embeddings and file-based storage
No external vector databases required - uses numpy and scikit-learn for similarity search
"""

import json
import numpy as np
from openai import OpenAI
from sklearn.metrics.pairwise import cosine_similarity
from typing import List, Dict, Tuple, Optional, Any
import os
import logging
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

load_dotenv()


class InMemoryRAG:
    """
    In-memory RAG system using OpenAI embeddings and cosine similarity search
    Stores embeddings in JSON file for persistence
    """
    
    def __init__(self, knowledge_base_path: str, embeddings_path: str):
        """
        Initialize RAG system with file paths
        
        Args:
            knowledge_base_path: Path to functions.txt
            embeddings_path: Path to embeddings.json (will be created if doesn't exist)
        """
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables")
            
        self.client = OpenAI(api_key=api_key)
        self.kb_path = knowledge_base_path
        self.emb_path = embeddings_path
        self.chunks: List[str] = []  # List of text chunks
        self.embeddings: Optional[np.ndarray] = None  # Corresponding embeddings (numpy array)
        self.embedding_model = "text-embedding-3-small"
        
        logger.info(f"Initialized InMemoryRAG with KB: {knowledge_base_path}")
        
    def load_knowledge_base(self) -> None:
        """
        Load and chunk the functions.txt file
        Expected format:
        ---
        Function: function_name
        Input: description
        Processing: description
        Output: description
        Description: description
        Example: example
        ---
        
        Each function block (separated by ---) is a separate chunk
        """
        try:
            if not os.path.exists(self.kb_path):
                raise FileNotFoundError(f"Knowledge base file not found: {self.kb_path}")
            
            with open(self.kb_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Split by delimiter (---)
            raw_chunks = content.split('---')
            
            # Clean and filter chunks
            self.chunks = []
            for chunk in raw_chunks:
                cleaned = chunk.strip()
                # Only keep non-empty chunks with actual content
                if cleaned and len(cleaned) > 20:  # Minimum meaningful content
                    self.chunks.append(cleaned)
            
            if not self.chunks:
                raise ValueError("No valid chunks found in knowledge base")
            
            logger.info(f"Loaded {len(self.chunks)} chunks from knowledge base")
            
        except FileNotFoundError as e:
            logger.error(f"Knowledge base file not found: {e}")
            raise
        except Exception as e:
            logger.error(f"Error loading knowledge base: {e}")
            raise
        
    def generate_and_save_embeddings(self) -> None:
        """
        Generate embeddings for all chunks using text-embedding-3-small
        Save to embeddings.json as:
        {
            "model": "text-embedding-3-small",
            "chunks": ["text1", "text2", ...],
            "embeddings": [[0.1, 0.2, ...], [0.3, 0.4, ...], ...]
        }
        """
        if os.path.exists(self.emb_path):
            logger.info(f"Embeddings file already exists at {self.emb_path}")
            
            # Verify if embeddings match current chunks
            try:
                with open(self.emb_path, 'r') as f:
                    existing_data = json.load(f)
                
                if existing_data.get("chunks") == self.chunks:
                    logger.info("Embeddings are up-to-date with knowledge base")
                    return
                else:
                    logger.warning("Chunks have changed. Regenerating embeddings...")
            except Exception as e:
                logger.warning(f"Could not validate existing embeddings: {e}. Regenerating...")
        
        logger.info(f"Generating embeddings for {len(self.chunks)} chunks...")
        embeddings_list = []
        
        try:
            # Generate embeddings in batches for efficiency
            batch_size = 100  # OpenAI allows up to 2048 texts per request
            
            for i in range(0, len(self.chunks), batch_size):
                batch = self.chunks[i:i + batch_size]
                logger.info(f"Processing batch {i//batch_size + 1}/{(len(self.chunks)-1)//batch_size + 1}")
                
                response = self.client.embeddings.create(
                    model=self.embedding_model,
                    input=batch
                )
                
                # Extract embeddings from response
                for item in response.data:
                    embeddings_list.append(item.embedding)
            
            # Save to JSON
            data = {
                "model": self.embedding_model,
                "chunks": self.chunks,
                "embeddings": embeddings_list,
                "chunk_count": len(self.chunks),
                "embedding_dimension": len(embeddings_list[0]) if embeddings_list else 0
            }
            
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(self.emb_path), exist_ok=True)
            
            with open(self.emb_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
            
            logger.info(f"Successfully generated and saved {len(embeddings_list)} embeddings")
            logger.info(f"Embedding dimension: {data['embedding_dimension']}")
            
        except Exception as e:
            logger.error(f"Error generating embeddings: {e}")
            raise
        
    def load_embeddings_to_memory(self) -> None:
        """
        Load embeddings.json into memory
        Convert embeddings list to numpy array for fast computation
        Validates the file format and dimensions
        """
        try:
            if not os.path.exists(self.emb_path):
                raise FileNotFoundError(f"Embeddings file not found: {self.emb_path}")
            
            logger.info(f"Loading embeddings from {self.emb_path}")
            
            with open(self.emb_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Validate data format
            required_keys = ["chunks", "embeddings"]
            for key in required_keys:
                if key not in data:
                    raise ValueError(f"Invalid embeddings file: missing '{key}' field")
            
            self.chunks = data["chunks"]
            embeddings_list = data["embeddings"]
            
            # Validate dimensions
            if len(self.chunks) != len(embeddings_list):
                raise ValueError(
                    f"Mismatch: {len(self.chunks)} chunks but {len(embeddings_list)} embeddings"
                )
            
            if not embeddings_list:
                raise ValueError("Embeddings file contains no embeddings")
            
            # Convert to numpy array for efficient computation
            self.embeddings = np.array(embeddings_list, dtype=np.float32)
            
            logger.info(f"Loaded {len(self.chunks)} chunks into memory")
            logger.info(f"Embedding shape: {self.embeddings.shape}")
            
            # Log model info if available
            if "model" in data:
                logger.info(f"Embeddings model: {data['model']}")
            
        except FileNotFoundError as e:
            logger.error(f"Embeddings file not found: {e}")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in embeddings file: {e}")
            raise
        except Exception as e:
            logger.error(f"Error loading embeddings: {e}")
            raise
        
    def retrieve_relevant_functions(
        self, 
        query: str, 
        top_k: int = 3,
        min_score: float = 0.0
    ) -> List[Dict[str, Any]]:
        """
        Retrieve top-k most relevant function descriptions using cosine similarity
        
        Args:
            query: Natural language query
            top_k: Number of results to return
            min_score: Minimum similarity score threshold (0.0 to 1.0)
            
        Returns:
            List of dicts: [
                {"text": "function description", "score": 0.85, "rank": 1},
                ...
            ]
        """
        if self.embeddings is None or len(self.chunks) == 0:
            logger.warning("No embeddings loaded. Call initialize() first.")
            return []
        
        try:
            # Generate embedding for query
            logger.debug(f"Generating embedding for query: {query[:50]}...")
            response = self.client.embeddings.create(
                model=self.embedding_model,
                input=query
            )
            query_embedding = np.array([response.data[0].embedding], dtype=np.float32)
            
            # Compute cosine similarity with all stored embeddings
            similarities = cosine_similarity(query_embedding, self.embeddings)[0]
            
            # Filter by minimum score
            valid_indices = np.where(similarities >= min_score)[0]
            
            if len(valid_indices) == 0:
                logger.warning(f"No results found with score >= {min_score}")
                return []
            
            # Get top-k indices from valid results
            valid_similarities = similarities[valid_indices]
            top_k_among_valid = min(top_k, len(valid_indices))
            top_indices_in_valid = np.argsort(valid_similarities)[-top_k_among_valid:][::-1]
            top_indices = valid_indices[top_indices_in_valid]
            
            # Build results
            results = []
            for rank, idx in enumerate(top_indices, start=1):
                results.append({
                    "text": self.chunks[idx],
                    "score": float(similarities[idx]),
                    "rank": rank,
                    "index": int(idx)
                })
            
            logger.info(f"Retrieved {len(results)} relevant chunks for query")
            
            return results
            
        except Exception as e:
            logger.error(f"Error retrieving relevant functions: {e}")
            return []
    
    def retrieve_as_context(
        self, 
        query: str, 
        top_k: int = 3,
        min_score: float = 0.0
    ) -> str:
        """
        Retrieve relevant functions and format as context string for LLM
        
        Args:
            query: Natural language query
            top_k: Number of results to return
            min_score: Minimum similarity score threshold
            
        Returns:
            Formatted context string ready for LLM prompt
        """
        results = self.retrieve_relevant_functions(query, top_k, min_score)
        
        if not results:
            return "No relevant functions found in knowledge base."
        
        context = "Relevant functions from knowledge base:\n\n"
        for result in results:
            context += f"[Relevance Score: {result['score']:.3f}]\n"
            context += f"{result['text']}\n"
            context += "-" * 60 + "\n\n"
        
        return context
        
    def initialize(self, force_regenerate: bool = False) -> None:
        """
        Full initialization pipeline:
        1. Load knowledge base
        2. Generate embeddings if they don't exist (or force_regenerate=True)
        3. Load embeddings into memory
        
        Args:
            force_regenerate: If True, regenerate embeddings even if they exist
        """
        logger.info("Starting RAG system initialization...")
        
        try:
            # Step 1: Load knowledge base
            self.load_knowledge_base()
            
            # Step 2: Generate embeddings if needed
            needs_generation = force_regenerate
            
            if force_regenerate:
                logger.info("Force regenerating embeddings...")
                if os.path.exists(self.emb_path):
                    os.remove(self.emb_path)
            
            # Check if embeddings file exists and is valid
            if not force_regenerate and os.path.exists(self.emb_path):
                try:
                    with open(self.emb_path, 'r') as f:
                        data = json.load(f)
                    # Check if it has actual embeddings
                    if not data.get("embeddings") or len(data.get("embeddings", [])) == 0:
                        logger.info("Embeddings file is empty. Generating...")
                        needs_generation = True
                except:
                    logger.info("Embeddings file is invalid. Generating...")
                    needs_generation = True
            else:
                needs_generation = True
            
            if needs_generation:
                self.generate_and_save_embeddings()
            
            # Step 3: Load embeddings into memory
            self.load_embeddings_to_memory()
            
            logger.info("✅ RAG system initialized successfully!")
            
        except Exception as e:
            logger.error(f"Failed to initialize RAG system: {e}")
            raise
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the RAG system
        
        Returns:
            Dictionary with system statistics
        """
        return {
            "num_chunks": len(self.chunks),
            "embedding_dimension": self.embeddings.shape[1] if self.embeddings is not None else 0,
            "embeddings_loaded": self.embeddings is not None,
            "knowledge_base_path": self.kb_path,
            "embeddings_path": self.emb_path,
            "model": self.embedding_model
        }


# Usage example and testing
if __name__ == "__main__":
    # Setup paths (relative to script location)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    kb_path = os.path.join(script_dir, "knowledge_base/functions.txt")
    emb_path = os.path.join(script_dir, "knowledge_base/embeddings.json")
    
    try:
        # Initialize RAG system
        rag = InMemoryRAG(
            knowledge_base_path=kb_path,
            embeddings_path=emb_path
        )
        rag.initialize()
        
        # Display stats
        stats = rag.get_stats()
        print("\n" + "="*60)
        print("RAG System Statistics")
        print("="*60)
        for key, value in stats.items():
            print(f"{key}: {value}")
        print("="*60 + "\n")
        
        # Test queries
        test_queries = [
            "find the maximum number in a list",
            "sort an array efficiently",
            "check if a string is a palindrome",
            "calculate fibonacci sequence",
            "graph traversal algorithms"
        ]
        
        for query in test_queries:
            print(f"\n🔍 Query: '{query}'")
            print("-" * 60)
            results = rag.retrieve_relevant_functions(query, top_k=2)
            
            for r in results:
                print(f"\n[Rank {r['rank']}] Score: {r['score']:.3f}")
                # Print first 150 characters of text
                text_preview = r['text'].replace('\n', ' ')[:150]
                print(f"Text: {text_preview}...")
            print("-" * 60)
        
        # Test context formatting
        print("\n\n📝 Context Format Example:")
        print("="*60)
        context = rag.retrieve_as_context("sorting algorithms", top_k=2)
        print(context)
        
    except FileNotFoundError as e:
        logger.error(f"File not found: {e}")
        logger.info("Make sure knowledge_base/functions.txt exists")
    except Exception as e:
        logger.error(f"Error: {e}")
        raise
