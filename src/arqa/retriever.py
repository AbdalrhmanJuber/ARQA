"""
Document Retrieval Module for ARQA
Handles semantic search and document retrieval from the indexed corpus.
"""

from typing import List, Dict, Any, Optional
from haystack.nodes import DensePassageRetriever, EmbeddingRetriever
from haystack.document_stores import FAISSDocumentStore
from transformers import AutoTokenizer, AutoModel
from camel_tools.tokenizers import WordTokenizer


class DocumentRetriever:
    """Handles document retrieval using dense passage retrieval."""
    
    def __init__(self, 
                 index_path: str = "./faiss_index",
                 model_name: str = "aubmindlab/bert-base-arabertv02",
                 top_k: int = 10):
        """
        Initialize the document retriever.
        
        Args:
            index_path: Path to the FAISS index
            model_name: Pretrained model for embeddings
            top_k: Number of top documents to retrieve
        """
        self.index_path = index_path
        self.top_k = top_k
        self.tokenizer = WordTokenizer()
        
        # Initialize document store
        self.document_store = FAISSDocumentStore(
            faiss_index_path=index_path,
            faiss_config_path=f"{index_path}.json"
        )
        
        # Initialize retriever
        self.retriever = EmbeddingRetriever(
            document_store=self.document_store,
            embedding_model=model_name,
            model_format="transformers"
        )
    
    def preprocess_query(self, query: str) -> str:
        """
        Preprocess the query using the same pipeline as documents.
        
        Args:
            query: Raw Arabic query
            
        Returns:
            Preprocessed query
        """
        # Apply same preprocessing as documents
        tokens = self.tokenizer.tokenize(query)
        return " ".join(tokens)
    
    def retrieve(self, query: str, top_k: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Retrieve relevant documents for a given query.
        
        Args:
            query: Question or search query in Arabic
            top_k: Number of documents to retrieve (uses default if None)
            
        Returns:
            List of retrieved documents with scores
        """
        if top_k is None:
            top_k = self.top_k
        
        # Preprocess query
        processed_query = self.preprocess_query(query)
        
        # Retrieve documents
        retrieved_docs = self.retriever.retrieve(
            query=processed_query,
            top_k=top_k
        )
        
        # Format results
        results = []
        for doc in retrieved_docs:
            results.append({
                'content': doc.content,
                'meta': doc.meta,
                'score': doc.score,
                'id': doc.id
            })
        
        return results
    
    def update_embeddings(self) -> None:
        """Update document embeddings in the document store."""
        self.document_store.update_embeddings(self.retriever)
        print("Document embeddings updated successfully")
