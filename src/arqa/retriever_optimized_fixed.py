"""
Optimized Document Retrieval Module for ARQA
High-performance retriever with incremental indexing and background processing.
"""

import os
import json
import pickle
import asyncio
import numpy as np
from typing import List, Dict, Any, Optional, Union, Set
from dataclasses import dataclass
from tqdm import tqdm
import torch
from transformers import AutoTokenizer, AutoModel
import faiss
import re
import hashlib
from concurrent.futures import ThreadPoolExecutor
import threading
import time


@dataclass
class RetrievedDocument:
    """Container for retrieved document with metadata."""
    content: str
    meta: Dict[str, Any]
    score: float
    doc_id: str
    chunk_id: int = 0


class OptimizedArabicRetriever:
    """
    High-Performance Arabic Document Retriever with:
    - Incremental indexing (only embed new documents)
    - Background processing support
    - GPU optimization
    - Batch embedding processing
    - Document deduplication
    """
    
    def __init__(self, 
                 model_name: str = "abdoelsayed/AraDPR",
                 index_path: str = "./faiss_index",
                 documents_path: str = "./documents_metadata.json",
                 top_k: int = 10,
                 device: str = "auto",
                 batch_size: int = 32,
                 use_fast_model: bool = False):
        """
        Initialize optimized retriever.
        
        Args:
            model_name: HuggingFace model for embeddings
            index_path: Path to save/load FAISS index
            documents_path: Path to save/load document metadata
            top_k: Default number of documents to retrieve
            device: Device to run model on ('auto', 'cpu', 'cuda')
            batch_size: Batch size for embedding processing
            use_fast_model: Whether to use a faster but less accurate model
        """
        self.model_name = model_name
        self.index_path = index_path
        self.documents_path = documents_path
        self.top_k = top_k
        self.batch_size = batch_size
        
        # Use faster model if requested
        if use_fast_model:
            self.model_name = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
            print("🚀 Using fast multilingual model for better performance")
        
        # Set device with GPU optimization
        if device == "auto":
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
        else:
            self.device = device
            
        # GPU optimization
        if self.device == "cuda":
            try:
                torch.backends.cudnn.benchmark = True
                gpu_name = torch.cuda.get_device_name(0)
                print(f"🔥 GPU acceleration enabled on {gpu_name}")
            except Exception as e:
                print(f"⚠️  GPU setup failed: {e}")
                self.device = "cpu"
        
        print(f"🔧 Initializing Optimized Retriever with {self.model_name} on {self.device}")
        
        # Initialize model and tokenizer
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        self.model = AutoModel.from_pretrained(self.model_name)
        
        # Move to device and optimize
        if self.device == "cuda":
            self.model = self.model.cuda()
            # Enable mixed precision for faster inference
            self.model = self.model.half()
        
        self.model.eval()
        
        # Initialize storage
        self.index = None
        self.documents = []
        self.id_to_doc = {}
        self.document_hashes = set()  # Track document hashes for deduplication
        self.embeddings_cache = {}    # Cache embeddings by document hash
        
        # Background processing
        self.indexing_queue = []
        self.indexing_in_progress = False
        self.indexing_lock = threading.Lock()
        
        # Load existing index if available
        self.load_index()
        
        print(f"✅ Optimized Retriever initialized with {len(self.documents)} documents")
    
    def _get_document_hash(self, content: str, meta: Optional[Dict[str, Any]] = None) -> str:
        """Generate hash for document deduplication including metadata."""
        # Include both content and source URL in hash to allow same content from different sources
        hash_content = content
        if meta and 'source_url' in meta:
            hash_content = f"{content}||SOURCE:{meta['source_url']}"
        return hashlib.md5(hash_content.encode('utf-8')).hexdigest()
    
    def normalize_arabic_text(self, text: str) -> str:
        """Optimized Arabic text normalization."""
        # Use compiled regex patterns for better performance
        if not hasattr(self, '_compiled_patterns'):
            self._compiled_patterns = [
                (re.compile(r'[أإآ]'), 'ا'),  # Alef normalization
                (re.compile(r'ة'), 'ه'),      # Ta Marbuta
                (re.compile(r'ى'), 'ي'),      # Alef Maksura
                (re.compile(r'\s+'), ' '),    # Whitespace
            ]
        
        for pattern, replacement in self._compiled_patterns:
            text = pattern.sub(replacement, text)
        
        return text.strip()
    
    def encode_text_batch(self, texts: List[str], 
                         is_query: bool = False, 
                         show_progress: bool = True) -> np.ndarray:
        """
        Optimized batch text encoding with GPU acceleration.
        
        Args:
            texts: List of texts to encode
            is_query: Whether encoding queries (vs passages)
            show_progress: Whether to show progress bar
            
        Returns:
            Numpy array of embeddings
        """
        if not texts:
            return np.array([])
        
        # Normalize texts
        texts = [self.normalize_arabic_text(text) for text in texts]
        
        embeddings = []
        
        # Create progress bar
        progress_desc = "🔍 Encoding queries" if is_query else "📝 Encoding passages"
        batches = [texts[i:i + self.batch_size] for i in range(0, len(texts), self.batch_size)]
        
        if show_progress:
            pbar = tqdm(batches, desc=progress_desc)
        else:
            pbar = batches
        
        with torch.no_grad():
            for batch_texts in pbar:
                # Tokenize batch
                inputs = self.tokenizer(
                    batch_texts,
                    padding=True,
                    truncation=True,
                    max_length=512,
                    return_tensors="pt"
                )
                
                # Move to device
                inputs = {k: v.to(self.device) for k, v in inputs.items()}
                
                # Get embeddings
                outputs = self.model(**inputs)
                
                # Use [CLS] token or mean pooling
                if hasattr(outputs, 'pooler_output') and outputs.pooler_output is not None:
                    batch_embeddings = outputs.pooler_output
                else:
                    # Mean pooling
                    attention_mask = inputs['attention_mask']
                    token_embeddings = outputs.last_hidden_state
                    input_mask_expanded = attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()
                    batch_embeddings = torch.sum(token_embeddings * input_mask_expanded, 1) / torch.clamp(input_mask_expanded.sum(1), min=1e-9)
                
                # Convert to CPU and proper precision
                if self.device == "cuda":
                    batch_embeddings = batch_embeddings.float().cpu().numpy()
                else:
                    batch_embeddings = batch_embeddings.cpu().numpy()
                
                embeddings.extend(batch_embeddings)
        
        return np.array(embeddings)
    
    def add_documents_incremental(self, documents: List[Dict[str, Any]], 
                                 background: bool = True, 
                                 force_reindex: bool = False) -> Dict[str, Any]:
        """
        Add documents with incremental indexing (only embed new documents).
        
        Args:
            documents: List of document dictionaries
            background: Whether to process in background
            force_reindex: If True, reindex even duplicate content
            
        Returns:
            Processing status and statistics
        """
        start_time = time.time()
        new_documents = []
        skipped_count = 0
        
        print(f"📚 Processing {len(documents)} documents for incremental indexing...")
        
        # Filter out duplicates (unless force_reindex is True)
        for doc in documents:
            content = doc['content']
            meta = doc.get('meta', {})
            doc_hash = self._get_document_hash(content, meta)
            
            if force_reindex or doc_hash not in self.document_hashes:
                doc_id = f"doc_{len(self.documents) + len(new_documents)}"
                new_doc = {
                    'id': doc_id,
                    'content': content,
                    'meta': doc.get('meta', {}),
                    'chunk_id': doc.get('chunk_id', 0),
                    'hash': doc_hash
                }
                new_documents.append(new_doc)
                self.document_hashes.add(doc_hash)
            else:
                skipped_count += 1
        
        print(f"📊 Found {len(new_documents)} new documents, skipped {skipped_count} duplicates")
        
        if not new_documents:
            return {
                'new_documents': 0,
                'skipped_duplicates': skipped_count,
                'total_documents': len(self.documents),
                'processing_time': time.time() - start_time,
                'background_processing': False
            }
        
        # Add documents to storage
        self.documents.extend(new_documents)
        for i, doc in enumerate(new_documents):
            self.id_to_doc[doc['id']] = len(self.documents) - len(new_documents) + i
        
        if background:
            # Queue for background processing
            with self.indexing_lock:
                self.indexing_queue.extend(new_documents)
            
            # Start background indexing if not already running
            if not self.indexing_in_progress:
                threading.Thread(target=self._background_indexing, daemon=True).start()
            
            return {
                'new_documents': len(new_documents),
                'skipped_duplicates': skipped_count,
                'total_documents': len(self.documents),
                'processing_time': time.time() - start_time,
                'background_processing': True,
                'status': 'queued_for_indexing'
            }
        else:
            # Process immediately
            self._update_embeddings_incremental(new_documents)
            
            return {
                'new_documents': len(new_documents),
                'skipped_duplicates': skipped_count,
                'total_documents': len(self.documents),
                'processing_time': time.time() - start_time,
                'background_processing': False,
                'status': 'indexed'
            }
    
    def _background_indexing(self):
        """Background thread for processing embedding queue."""
        with self.indexing_lock:
            if self.indexing_in_progress:
                return
            self.indexing_in_progress = True
        
        try:
            while True:
                with self.indexing_lock:
                    if not self.indexing_queue:
                        break
                    
                    # Process batch
                    batch_size = min(50, len(self.indexing_queue))  # Process in batches
                    batch = self.indexing_queue[:batch_size]
                    self.indexing_queue = self.indexing_queue[batch_size:]
                
                print(f"🔄 Background indexing {len(batch)} documents...")
                self._update_embeddings_incremental(batch)
                print(f"✅ Background indexed {len(batch)} documents")
                
        finally:
            with self.indexing_lock:
                self.indexing_in_progress = False
    
    def _update_embeddings_incremental(self, new_documents: List[Dict[str, Any]]):
        """Update embeddings only for new documents."""
        if not new_documents:
            return
        
        print(f"🔧 Embedding {len(new_documents)} new documents...")
        
        # Extract content for new documents
        new_contents = [doc['content'] for doc in new_documents]
        
        # Generate embeddings for new documents only
        new_embeddings = self.encode_text_batch(new_contents, is_query=False, show_progress=True)
        
        # Initialize index if needed
        if self.index is None:
            dimension = new_embeddings.shape[1]
            print(f"📊 Creating new FAISS index with dimension {dimension}")
            self.index = faiss.IndexFlatIP(dimension)
          # Normalize new embeddings for cosine similarity
        faiss.normalize_L2(new_embeddings)
        
        # Add only new embeddings to index
        self.index.add(new_embeddings.astype(np.float32))
        
        # Cache embeddings by hash
        for doc, embedding in zip(new_documents, new_embeddings):
            self.embeddings_cache[doc['hash']] = embedding
        
        # Save index and metadata
        self.save_index()
        
        print(f"✅ Incrementally added {len(new_documents)} documents. Total: {self.index.ntotal}")
    
    def get_indexing_status(self) -> Dict[str, Any]:
        """Get current indexing status."""
        with self.indexing_lock:
            return {
                'indexing_in_progress': self.indexing_in_progress,
                'queue_length': len(self.indexing_queue),
                'total_documents': len(self.documents),
                'indexed_documents': self.index.ntotal if self.index else 0
            }
    
    def retrieve(self, query: str, top_k: Optional[int] = None) -> List[RetrievedDocument]:
        """Fast document retrieval with optimized query processing."""
        if self.index is None:
            raise ValueError("No index available. Please add documents first.")
        
        if top_k is None:
            top_k = self.top_k
        
        # Ensure we don't retrieve more than available
        top_k = min(top_k, len(self.documents))
        
        # Fast query encoding
        query_embedding = self.encode_text_batch([query], is_query=True, show_progress=False)
          # Normalize for cosine similarity
        faiss.normalize_L2(query_embedding)
        
        # Search
        scores, indices = self.index.search(query_embedding.astype(np.float32), k=top_k)
        
        # Format results
        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx != -1:  # Valid result
                doc = self.documents[idx]
                results.append(RetrievedDocument(
                    content=doc['content'],
                    meta=doc['meta'],
                    score=float(score),
                    doc_id=doc['id'],
                    chunk_id=doc.get('chunk_id', 0)
                ))
        
        return results
    
    def save_index(self) -> None:
        """Save optimized index with caching."""
        os.makedirs(os.path.dirname(self.index_path) if os.path.dirname(self.index_path) else '.', exist_ok=True)
        
        if self.index is not None:
            faiss.write_index(self.index, f"{self.index_path}.faiss")
        
        # Save metadata with cache info
        metadata = {
            'model_name': self.model_name,
            'documents': self.documents,
            'id_to_doc': self.id_to_doc,
            'document_hashes': list(self.document_hashes),
            'total_documents': len(self.documents),
            'batch_size': self.batch_size,
            'device': self.device
        }
        
        with open(self.documents_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)
    
    def load_index(self) -> bool:
        """Load optimized index with caching."""
        try:
            # Load FAISS index
            if os.path.exists(f"{self.index_path}.faiss"):
                self.index = faiss.read_index(f"{self.index_path}.faiss")
                print(f"📖 Loaded FAISS index with {self.index.ntotal} documents")
            
            # Load metadata
            if os.path.exists(self.documents_path):
                with open(self.documents_path, 'r', encoding='utf-8') as f:
                    metadata = json.load(f)
                
                self.documents = metadata.get('documents', [])
                self.id_to_doc = metadata.get('id_to_doc', {})
                self.document_hashes = set(metadata.get('document_hashes', []))
                
                # Check if model changed
                saved_model = metadata.get('model_name', '')
                if saved_model and saved_model != self.model_name:
                    print(f"⚠️ Model changed from {saved_model} to {self.model_name}")
                    print("💡 Consider rebuilding index for optimal performance")
                
                return True
        
        except Exception as e:
            print(f"⚠️ Could not load existing index: {e}")
        
        return False
    
    def get_stats(self) -> Dict[str, Any]:
        """Get comprehensive retriever statistics."""
        indexing_status = self.get_indexing_status()
        
        return {
            'model_name': self.model_name,
            'total_documents': len(self.documents),
            'index_size': self.index.ntotal if self.index else 0,
            'device': self.device,
            'batch_size': self.batch_size,
            'cached_embeddings': len(self.embeddings_cache),
            'indexing_status': indexing_status,
            'index_path': self.index_path
        }
