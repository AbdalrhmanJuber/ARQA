"""
Document Retrieval Module for ARQA
Handles semantic search and document retrieval using AraDPR and FAISS.
"""

import os
import json
import pickle
import numpy as np
from typing import List, Dict, Any, Optional, Union
from dataclasses import dataclass
from tqdm import tqdm
import torch
from transformers import AutoTokenizer, AutoModel
import faiss
import re


@dataclass
class RetrievedDocument:
    """Container for retrieved document with metadata."""
    content: str
    meta: Dict[str, Any]
    score: float
    doc_id: str
    chunk_id: int


class ArabicDocumentRetriever:
    """
    Arabic Document Retriever using AraDPR embeddings and FAISS for similarity search.
    
    This implementation uses:
    - abdoelsayed/AraDPR for both query and passage embeddings
    - FAISS for efficient similarity search
    - Progress bars for user feedback
    - Support for model switching (e.g., to intfloat/e5-arabic-base)
    """
    
    def __init__(self, 
                 model_name: str = "abdoelsayed/AraDPR",
                 index_path: str = "./faiss_index",
                 documents_path: str = "./documents_metadata.json",
                 top_k: int = 10,
                 device: str = "auto"):
        """
        Initialize the Arabic document retriever.
        
        Args:
            model_name: HuggingFace model for embeddings (supports switching)
            index_path: Path to save/load FAISS index
            documents_path: Path to save/load document metadata
            top_k: Default number of documents to retrieve
            device: Device to run model on ('auto', 'cpu', or 'cuda')
        """
        self.model_name = model_name
        self.index_path = index_path
        self.documents_path = documents_path
        self.top_k = top_k
        
        # Set device
        if device == "auto":
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
        else:
            self.device = device
        
        print(f"🔧 Initializing Arabic Retriever with {model_name} on {self.device}")
        
        # Initialize model and tokenizer
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModel.from_pretrained(model_name).to(self.device)
        self.model.eval()
        
        # Initialize storage
        self.index = None
        self.documents = []
        self.id_to_doc = {}
        
        # Load existing index if available
        self.load_index()
        
        print(f"✅ Retriever initialized with {len(self.documents)} documents")
    
    def switch_model(self, new_model_name: str) -> None:
        """
        Switch to a different embedding model and rebuild index.
        
        Args:
            new_model_name: New HuggingFace model name (e.g., 'intfloat/e5-arabic-base')
        """
        print(f"🔄 Switching from {self.model_name} to {new_model_name}")
        
        # Store current documents before switching
        current_docs = self.documents.copy()
        
        # Update model
        self.model_name = new_model_name
        self.tokenizer = AutoTokenizer.from_pretrained(new_model_name)
        self.model = AutoModel.from_pretrained(new_model_name).to(self.device)
        self.model.eval()
        
        # Rebuild index with new embeddings if we have documents
        if current_docs:
            print("🔧 Rebuilding index with new model...")
            self.documents = current_docs
            self.update_embeddings()
        
        print(f"✅ Successfully switched to {new_model_name}")
    
    def normalize_arabic_text(self, text: str) -> str:
        """
        Normalize Arabic text for consistent processing.
        
        Args:
            text: Raw Arabic text
            
        Returns:
            Normalized Arabic text
        """
        # Basic Arabic normalization
        text = re.sub(r'[أإآ]', 'ا', text)  # Normalize Alef
        text = re.sub(r'ة', 'ه', text)      # Normalize Ta Marbuta
        text = re.sub(r'ى', 'ي', text)      # Normalize Alef Maksura
        text = re.sub(r'\s+', ' ', text)    # Normalize whitespace
        text = text.strip()
        
        return text
    
    def encode_text(self, texts: Union[str, List[str]], 
                   is_query: bool = False, 
                   show_progress: bool = True) -> np.ndarray:
        """
        Encode texts into embeddings using the current model.
        
        Args:
            texts: Single text or list of texts to encode
            is_query: Whether encoding queries (vs passages)
            show_progress: Whether to show progress bar
            
        Returns:
            Numpy array of embeddings
        """
        if isinstance(texts, str):
            texts = [texts]
        
        # Normalize texts
        texts = [self.normalize_arabic_text(text) for text in texts]
        
        embeddings = []
        batch_size = 8  # Adjust based on your GPU memory
        
        # Create progress bar
        progress_desc = "🔍 Encoding queries" if is_query else "📝 Encoding passages"
        if show_progress:
            pbar = tqdm(range(0, len(texts), batch_size), desc=progress_desc)
        else:
            pbar = range(0, len(texts), batch_size)
        
        with torch.no_grad():
            for i in pbar:
                batch_texts = texts[i:i + batch_size]
                
                # Tokenize batch
                inputs = self.tokenizer(
                    batch_texts,
                    padding=True,
                    truncation=True,
                    max_length=512,
                    return_tensors="pt"
                ).to(self.device)
                
                # Get embeddings
                outputs = self.model(**inputs)
                
                # Use [CLS] token embeddings or mean pooling
                if hasattr(outputs, 'pooler_output') and outputs.pooler_output is not None:
                    batch_embeddings = outputs.pooler_output.cpu().numpy()
                else:
                    # Mean pooling
                    attention_mask = inputs['attention_mask']
                    token_embeddings = outputs.last_hidden_state
                    input_mask_expanded = attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()
                    batch_embeddings = torch.sum(token_embeddings * input_mask_expanded, 1) / torch.clamp(input_mask_expanded.sum(1), min=1e-9)
                    batch_embeddings = batch_embeddings.cpu().numpy()
                
                embeddings.extend(batch_embeddings)
        
        return np.array(embeddings)
    
    def add_documents(self, documents: List[Dict[str, Any]], 
                     update_index: bool = True) -> None:
        """
        Add documents to the retrieval index.
        
        Args:
            documents: List of document dictionaries with 'content' and 'meta' keys
            update_index: Whether to update the FAISS index immediately
        """
        print(f"📚 Adding {len(documents)} documents to index...")
        
        for doc in documents:
            doc_id = f"doc_{len(self.documents)}"
            self.documents.append({
                'id': doc_id,
                'content': doc['content'],
                'meta': doc.get('meta', {}),
                'chunk_id': doc.get('chunk_id', 0)
            })
            self.id_to_doc[doc_id] = len(self.documents) - 1
        
        if update_index:
            self.update_embeddings()
        
        print(f"✅ Added documents. Total: {len(self.documents)}")
    
    def update_embeddings(self) -> None:
        """Update document embeddings and rebuild FAISS index with progress bar."""
        if not self.documents:
            print("⚠️ No documents to embed")
            return
        
        print(f"🔧 Updating embeddings for {len(self.documents)} documents...")
        
        # Extract document contents
        doc_contents = [doc['content'] for doc in self.documents]
        
        # Generate embeddings with progress bar
        embeddings = self.encode_text(doc_contents, is_query=False, show_progress=True)
        
        # Create FAISS index
        dimension = embeddings.shape[1]
        print(f"📊 Creating FAISS index with dimension {dimension}")
        
        # Use IndexFlatIP for cosine similarity (after normalization)
        self.index = faiss.IndexFlatIP(dimension)
        
        # Normalize embeddings for cosine similarity
        faiss.normalize_L2(embeddings)
        
        # Add embeddings to index
        self.index.add(embeddings.astype(np.float32))
        
        # Save index and metadata
        self.save_index()
        
        print(f"✅ Index updated with {self.index.ntotal} documents")
    
    def retrieve(self, query: str, top_k: Optional[int] = None) -> List[RetrievedDocument]:
        """
        Retrieve relevant documents for a given query.
        
        Args:
            query: Question or search query in Arabic
            top_k: Number of documents to retrieve (uses default if None)
            
        Returns:
            List of retrieved documents with scores
        """
        if self.index is None:
            raise ValueError("No index available. Please add documents first.")
        
        if top_k is None:
            top_k = self.top_k
        
        # Ensure we don't retrieve more than available
        top_k = min(top_k, len(self.documents))
        
        print(f"🔍 Searching for: '{query[:50]}...' (top {top_k})")
        
        # Encode query
        query_embedding = self.encode_text(query, is_query=True, show_progress=False)
        
        # Normalize for cosine similarity
        faiss.normalize_L2(query_embedding)
        
        # Search
        scores, indices = self.index.search(query_embedding.astype(np.float32), top_k)
        
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
        
        print(f"📖 Retrieved {len(results)} documents")
        return results
    
    def save_index(self) -> None:
        """Save FAISS index and document metadata to disk."""
        os.makedirs(os.path.dirname(self.index_path) if os.path.dirname(self.index_path) else '.', exist_ok=True)
        
        if self.index is not None:
            faiss.write_index(self.index, f"{self.index_path}.faiss")
        
        # Save documents metadata
        metadata = {
            'model_name': self.model_name,
            'documents': self.documents,
            'id_to_doc': self.id_to_doc,
            'total_documents': len(self.documents)
        }
        
        with open(self.documents_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)
        
        print(f"💾 Index saved to {self.index_path}.faiss")
    
    def load_index(self) -> bool:
        """
        Load FAISS index and document metadata from disk.
        
        Returns:
            True if successfully loaded, False otherwise
        """
        try:
            # Load FAISS index
            if os.path.exists(f"{self.index_path}.faiss"):
                self.index = faiss.read_index(f"{self.index_path}.faiss")
            
            # Load metadata
            if os.path.exists(self.documents_path):
                with open(self.documents_path, 'r', encoding='utf-8') as f:
                    metadata = json.load(f)
                
                self.documents = metadata.get('documents', [])
                self.id_to_doc = metadata.get('id_to_doc', {})
                
                # Check if model changed
                saved_model = metadata.get('model_name', '')
                if saved_model and saved_model != self.model_name:
                    print(f"⚠️ Model changed from {saved_model} to {self.model_name}")
                    print("💡 Consider calling update_embeddings() to rebuild with new model")
                
                return True
        
        except Exception as e:
            print(f"⚠️ Could not load existing index: {e}")
        
        return False
    
    def get_stats(self) -> Dict[str, Any]:
        """Get retriever statistics."""
        return {
            'model_name': self.model_name,
            'total_documents': len(self.documents),
            'index_size': self.index.ntotal if self.index else 0,
            'device': self.device,
            'index_path': self.index_path
        }
