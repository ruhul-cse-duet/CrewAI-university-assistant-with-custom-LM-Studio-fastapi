import faiss
import numpy as np
import json
import os
from typing import List, Dict, Tuple, Optional
from datetime import datetime
import logging
from config import Config
from tools.embeddings import get_embedding_generator

logger = logging.getLogger(__name__)

class FAISSStore:
    """
    FAISS Vector Store for semantic search
    Uses HuggingFace multilingual sentence transformer for Bengali/English support
    """
    
    def __init__(self):
        self.config = Config
        self.index_path = Config.FAISS_INDEX_PATH
        self.metadata_path = Config.METADATA_PATH
        
        # Initialize embedding generator (lazy loading - won't load model yet)
        logger.info(f"Initializing FAISS store (embedding model will load on first use)")
        self.embedding_generator = get_embedding_generator()
        # Don't get dimension yet - it will load the model
        self.dimension = Config.EMBEDDING_DIMENSION  # Use default, will update on first use
        
        # Load or create index (without loading embedding model)
        self.index, self.metadata = self._load_or_create_index()
        
    def _load_or_create_index(self) -> Tuple[faiss.Index, List[Dict]]:
        """Load existing index or create new one"""
        os.makedirs(os.path.dirname(self.index_path), exist_ok=True)
        
        index_file = f"{self.index_path}/index.faiss"
        
        if os.path.exists(index_file) and os.path.exists(self.metadata_path):
            try:
                logger.info("Loading existing FAISS index...")
                index = faiss.read_index(index_file)
                
                with open(self.metadata_path, 'r', encoding='utf-8') as f:
                    metadata = json.load(f)
                
                # Update dimension from loaded index
                self.dimension = index.d
                logger.info(f"Loaded index with {index.ntotal} vectors (dimension: {self.dimension})")
                return index, metadata
                
            except Exception as e:
                logger.error(f"Error loading index: {e}")
                logger.info("Creating new index...")
        
        # Create new index (using Inner Product for cosine similarity)
        # Use default dimension from config - don't load model yet
        # Model will be loaded on first use (search/add_documents)
        logger.info(f"Creating new FAISS index with dimension {self.dimension} (model will load on first use)...")
        index = faiss.IndexFlatIP(self.dimension)
        metadata = []
        
        return index, metadata
    
    def add_documents(self, documents: List[Dict[str, str]]) -> int:
        """
        Add documents to FAISS index
        
        Args:
            documents: List of dicts with 'content', 'url', 'title', etc.
            
        Returns:
            Number of documents added
        """
        if not documents:
            return 0
        
        try:
            # Ensure embedding model is loaded and update dimension if needed
            actual_dimension = self.embedding_generator.get_dimension()
            if actual_dimension != self.dimension:
                logger.info(f"Updating FAISS index dimension from {self.dimension} to {actual_dimension}")
                self.dimension = actual_dimension
                # Recreate index with correct dimension
                self.index = faiss.IndexFlatIP(actual_dimension)
                # Re-add existing metadata if any
                if self.metadata:
                    logger.warning("Recreating index - existing documents will need to be re-added")
                    self.metadata = []
            
            # Extract content for embedding
            contents = [doc.get('content', '') for doc in documents]
            
            # Generate embeddings using HuggingFace multilingual model
            logger.info(f"Generating embeddings for {len(contents)} documents...")
            embeddings = self.embedding_generator.generate(contents)
            
            # Normalize for cosine similarity
            faiss.normalize_L2(embeddings)
            
            # Add to index
            self.index.add(embeddings.astype('float32'))
            
            # Add metadata
            for doc in documents:
                self.metadata.append({
                    'url': doc.get('url', ''),
                    'title': doc.get('title', ''),
                    'date': doc.get('date', ''),
                    'timestamp': datetime.now().isoformat(),
                    'preview': doc.get('content', '')[:200]
                })
            
            # Save index
            self._save_index()
            
            logger.info(f"Added {len(documents)} documents. Total: {self.index.ntotal}")
            return len(documents)
            
        except Exception as e:
            logger.error(f"Error adding documents: {str(e)}")
            return 0
    
    def search(
        self, 
        query: str, 
        top_k: int = 3,
        threshold: float = 0.5
    ) -> List[Dict]:
        """
        Semantic search in FAISS index
        
        Args:
            query: Search query
            top_k: Number of results to return
            threshold: Minimum similarity score (0-1)
            
        Returns:
            List of results with metadata and scores
        """
        if self.index.ntotal == 0:
            logger.warning("Index is empty")
            return []
        
        try:
            # Ensure embedding model is loaded and update dimension if needed
            actual_dimension = self.embedding_generator.get_dimension()
            if actual_dimension != self.dimension:
                logger.info(f"Updating dimension from {self.dimension} to {actual_dimension}")
                self.dimension = actual_dimension
                # If index exists but dimension mismatch, we need to handle it
                if self.index.ntotal > 0:
                    logger.warning("Dimension mismatch - search may fail. Consider recreating index.")
            
            # Generate query embedding using HuggingFace multilingual model
            query_embedding = self.embedding_generator.generate([query])
            faiss.normalize_L2(query_embedding)
            
            # Search
            scores, indices = self.index.search(
                query_embedding.astype('float32'), 
                min(top_k, self.index.ntotal)
            )
            
            # Filter by threshold and format results
            results = []
            for score, idx in zip(scores[0], indices[0]):
                if idx < len(self.metadata) and score >= threshold:
                    result = self.metadata[idx].copy()
                    result['score'] = float(score)
                    results.append(result)
            
            logger.info(f"Found {len(results)} results for query: {query[:50]}...")
            return results
            
        except Exception as e:
            logger.error(f"Search error: {str(e)}")
            return []
    
    def _save_index(self):
        """Save index and metadata to disk"""
        try:
            index_file = f"{self.index_path}/index.faiss"
            faiss.write_index(self.index, index_file)
            
            with open(self.metadata_path, 'w', encoding='utf-8') as f:
                json.dump(self.metadata, f, ensure_ascii=False, indent=2)
            
            logger.info("Index saved successfully")
            
        except Exception as e:
            logger.error(f"Error saving index: {str(e)}")
    
    def clear_index(self):
        """Clear all data from index"""
        self.index.reset()
        self.metadata = []
        self._save_index()
        logger.info("Index cleared")
    
    def get_stats(self) -> Dict:
        """Get index statistics (doesn't load embedding model)"""
        try:
            index_size = 0
            if os.path.exists(f"{self.index_path}/index.faiss"):
                index_size = os.path.getsize(f"{self.index_path}/index.faiss") / (1024 * 1024)
            
            return {
                'total_documents': self.index.ntotal if hasattr(self, 'index') and self.index else 0,
                'dimension': self.dimension,
                'index_size_mb': index_size
            }
        except Exception as e:
            logger.debug(f"Error getting stats: {str(e)}")
            return {
                'total_documents': 0,
                'dimension': self.dimension,
                'index_size_mb': 0
            }


# Example usage
if __name__ == "__main__":
    store = FAISSStore()
    
    # Add sample documents
    docs = [
        {
            'content': 'পরীক্ষার সময়সূচী প্রকাশিত হয়েছে',
            'title': 'Exam Notice',
            'url': 'https://university.edu/notice1'
        }
    ]
    
    store.add_documents(docs)
    
    # Search
    results = store.search('পরীক্ষা', top_k=3)
    for r in results:
        print(f"Score: {r['score']:.2f}, Title: {r['title']}")
