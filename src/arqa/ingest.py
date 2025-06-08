"""
Document Ingestion Module for ARQA
Handles preprocessing and ingestion of Arabic documents into the system.
"""

import os
from typing import List, Dict, Any
from pathlib import Path
from camel_tools.tokenizers import WordTokenizer
from farasa.segmenter import FarasaSegmenter
from haystack import Document
from haystack.document_stores import FAISSDocumentStore


class DocumentIngestor:
    """Handles document preprocessing and ingestion for Arabic texts."""
    
    def __init__(self, index_path: str = "./faiss_index"):
        """
        Initialize the document ingestor.
        
        Args:
            index_path: Path to store the FAISS index
        """
        self.index_path = index_path
        self.tokenizer = WordTokenizer()
        self.segmenter = FarasaSegmenter(interactive=True)
        self.document_store = FAISSDocumentStore(
            faiss_index_path=index_path,
            faiss_config_path=f"{index_path}.json"
        )
    
    def preprocess_arabic_text(self, text: str) -> str:
        """
        Preprocess Arabic text using Farasa segmentation and CAMEL tokenization.
        
        Args:
            text: Raw Arabic text
            
        Returns:
            Preprocessed text
        """
        # Normalize and segment text
        segmented = self.segmenter.segment(text)
        
        # Tokenize
        tokens = self.tokenizer.tokenize(segmented)
        
        return " ".join(tokens)
    
    def ingest_documents(self, documents: List[Dict[str, Any]]) -> None:
        """
        Ingest a list of documents into the document store.
        
        Args:
            documents: List of document dictionaries with 'content' and 'meta' keys
        """
        processed_docs = []
        
        for i, doc in enumerate(documents):
            content = doc.get('content', '')
            meta = doc.get('meta', {})
            
            # Preprocess Arabic content
            processed_content = self.preprocess_arabic_text(content)
            
            # Create Haystack Document
            haystack_doc = Document(
                content=processed_content,
                meta=meta,
                id=str(i)
            )
            processed_docs.append(haystack_doc)
        
        # Write to document store
        self.document_store.write_documents(processed_docs)
        
        print(f"Successfully ingested {len(processed_docs)} documents")
    
    def ingest_from_file(self, file_path: str) -> None:
        """
        Ingest documents from a file.
        
        Args:
            file_path: Path to the file containing documents
        """
        # Implementation depends on file format (JSON, CSV, etc.)
        pass
