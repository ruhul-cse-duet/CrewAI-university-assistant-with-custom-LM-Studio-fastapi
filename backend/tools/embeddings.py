import numpy as np
from typing import Union, List
import logging
from config import Config

logger = logging.getLogger(__name__)

class EmbeddingGenerator:
    """
    Universal Embedding Generator
    Supports both LM Studio and Sentence Transformers
    """
    
    def __init__(self):
        # Always use HuggingFace multilingual sentence transformer
        self.provider = "sentence-transformers"
        self.dimension = Config.EMBEDDING_DIMENSION
        self.model = None
        self._model_loaded = False
        
        logger.info(f"Initializing HuggingFace multilingual embedding generator (lazy loading)")
        # Don't load model immediately - load on first use
    
    
    def _init_sentence_transformers(self):
        """Initialize Sentence Transformers (lazy loading with timeout)"""
        try:
            from sentence_transformers import SentenceTransformer
            import signal
            
            logger.info(f"Loading Sentence Transformer: {Config.EMBEDDING_MODEL}")
            logger.info("This may take 10-30 seconds on first load...")
            
            # Load model with progress indication
            self.model = SentenceTransformer(
                Config.EMBEDDING_MODEL,
                device='cpu',  # Use CPU to avoid GPU memory issues
                cache_folder=None  # Use default cache
            )
            self.dimension = self.model.get_sentence_embedding_dimension()
            
            logger.info(f"Sentence Transformers loaded successfully")
            logger.info(f"Model: {Config.EMBEDDING_MODEL}")
            logger.info(f"Dimension: {self.dimension}")
            
        except Exception as e:
            logger.error(f"Failed to load Sentence Transformers: {str(e)}")
            raise RuntimeError(f"Sentence Transformers initialization failed: {str(e)}")
    
    def _ensure_model_loaded(self):
        """Lazy load the model on first use"""
        if not self._model_loaded:
            logger.info("Loading embedding model on first use...")
            self._init_sentence_transformers()
            self._model_loaded = True
    
    def _generate_sentence_transformer_embedding(self, texts: List[str]) -> np.ndarray:
        """Generate embeddings using Sentence Transformers"""
        self._ensure_model_loaded()  # Load model if not already loaded
        try:
            embeddings = self.model.encode(
                texts,
                convert_to_numpy=True,
                show_progress_bar=False
            )
            return embeddings.astype(np.float32)
            
        except Exception as e:
            logger.error(f"Error generating Sentence Transformer embeddings: {str(e)}")
            raise
    
    def generate(self, texts: Union[str, List[str]]) -> np.ndarray:
        """
        Generate embeddings for given texts
        
        Args:
            texts: Single string or list of strings
            
        Returns:
            numpy array of embeddings (shape: [num_texts, dimension])
        """
        # Convert single string to list
        if isinstance(texts, str):
            texts = [texts]
        
        if not texts:
            raise ValueError("No texts provided for embedding")
        
        # Always use HuggingFace multilingual sentence transformer
        embeddings = self._generate_sentence_transformer_embedding(texts)
        
        return embeddings
    
    def get_dimension(self) -> int:
        """Get embedding dimension"""
        self._ensure_model_loaded()  # Load model to get actual dimension
        return self.dimension


# Global instance
_embedding_generator = None

def get_embedding_generator():
    """Get or create embedding generator instance"""
    global _embedding_generator
    if _embedding_generator is None:
        _embedding_generator = EmbeddingGenerator()
    return _embedding_generator

def embed_texts(texts: Union[str, List[str]]) -> np.ndarray:
    """
    Generate embeddings for texts
    
    Args:
        texts: Single string or list of strings
        
    Returns:
        numpy array of embeddings
    """
    generator = get_embedding_generator()
    return generator.generate(texts)

def get_embedding_dimension() -> int:
    """Get the dimension of embeddings"""
    generator = get_embedding_generator()
    return generator.get_dimension()


# Test function
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    print("\n" + "="*60)
    print("Testing Embedding Generator")
    print("="*60)
    
    # Test embedding generation
    test_texts = [
        "This is a test sentence in English",
        "এটি একটি বাংলা পরীক্ষা বাক্য"
    ]
    
    print(f"\nGenerating embeddings for {len(test_texts)} texts...")
    embeddings = embed_texts(test_texts)
    
    print(f"✅ Success!")
    print(f"Shape: {embeddings.shape}")
    print(f"Dimension: {get_embedding_dimension()}")
    print(f"Sample values: {embeddings[0][:5]}")
