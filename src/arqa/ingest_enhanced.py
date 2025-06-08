"""
Document Ingestion Module for ARQA
Handles preprocessing and indexing of Arabic HTML documents.
"""

from typing import List, Dict, Any, Optional
import os
import re
import json
import sqlite3
import unicodedata
from pathlib import Path
import numpy as np
from bs4 import BeautifulSoup
from haystack.document_stores import FAISSDocumentStore, SQLDocumentStore
from haystack.nodes import PreProcessor
from haystack.schema import Document
from camel_tools.utils.normalize import normalize_unicode
from camel_tools.tokenizers.word import simple_word_tokenize
from farasa.segmenter import FarasaSegmenter


class DocumentIngestor:
    """🚀 Handles Arabic HTML document preprocessing and ingestion."""
    
    def __init__(self, 
                 faiss_index_path: str = "faiss_index",
                 sqlite_path: str = "documents.db",
                 embedding_dim: int = 768):
        """
        🔧 Initialize the document ingestor with dual storage.
        
        Args:
            faiss_index_path: Path to store FAISS index
            sqlite_path: Path to SQLite database
            embedding_dim: Dimension of document embeddings
        """
        self.faiss_index_path = faiss_index_path
        self.sqlite_path = sqlite_path
        self.embedding_dim = embedding_dim
        
        # 🗂️ Initialize FAISS document store
        self.document_store = FAISSDocumentStore(
            faiss_index_path=faiss_index_path,
            embedding_dim=embedding_dim
        )
        
        # 🗃️ Initialize SQLite store for metadata
        self.sql_store = SQLDocumentStore(url=f"sqlite:///{sqlite_path}")
        
        # 🔤 Initialize Arabic text processor
        self.farasa_segmenter = FarasaSegmenter(interactive=True)
        
        # ✂️ Initialize preprocessor with 200-token chunks
        self.preprocessor = PreProcessor(
            clean_empty_lines=True,
            clean_whitespace=True,
            clean_header_footer=False,
            split_by="word",
            split_length=200,  # 200-token chunks as requested
            split_respect_sentence_boundary=True,
            split_overlap=50   # 25% overlap (50/200)
        )
    
    def extract_html_content(self, html_content: str) -> Dict[str, Any]:
        """
        🕸️ Extract clean text and metadata from HTML.
        
        Args:
            html_content: Raw HTML string
            
        Returns:
            Dict with cleaned text and metadata
        """
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # 🗑️ Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
        
        # 📝 Extract title
        title = soup.find('title')
        title_text = title.get_text().strip() if title else "No Title"
        
        # 📄 Extract main content (prioritize article, main, or body)
        content_selectors = ['article', 'main', '.content', '.article', 'body']
        content = None
        
        for selector in content_selectors:
            content = soup.select_one(selector)
            if content:
                break
        
        if not content:
            content = soup
        
        # 🧹 Get clean text
        text = content.get_text(separator=' ', strip=True)
        
        # 🏷️ Extract metadata
        metadata = {
            'title': title_text,
            'html_length': len(html_content),
            'text_length': len(text)
        }
        
        # 📊 Try to extract meta tags
        meta_tags = soup.find_all('meta')
        for meta in meta_tags:
            if meta.get('name') == 'description':
                metadata['description'] = meta.get('content', '')
            elif meta.get('name') == 'keywords':
                metadata['keywords'] = meta.get('content', '')
            elif meta.get('property') == 'og:title':
                metadata['og_title'] = meta.get('content', '')
        
        return {
            'text': text,
            'metadata': metadata
        }
    
    def normalize_arabic_text(self, text: str) -> str:
        """
        🔤 Normalize Arabic text (hamza, ta-marbuta, etc.).
        
        Args:
            text: Raw Arabic text
            
        Returns:
            Normalized Arabic text
        """
        # 📐 Apply Unicode normalization first
        normalized_text = normalize_unicode(text)
        
        # 🔄 Arabic-specific normalizations
        # Normalize different types of Hamza
        hamza_patterns = [
            (r'[أإآ]', 'ا'),  # All Alef+Hamza variants → Alef
            (r'ؤ', 'و'),      # Waw+Hamza → Waw
            (r'ئ', 'ي'),      # Yeh+Hamza → Yeh
        ]
        
        for pattern, replacement in hamza_patterns:
            normalized_text = re.sub(pattern, replacement, normalized_text)
        
        # 🎯 Normalize Ta Marbuta
        normalized_text = re.sub(r'ة', 'ه', normalized_text)
        
        # 🧽 Clean extra whitespace
        normalized_text = re.sub(r'\s+', ' ', normalized_text).strip()
        
        return normalized_text
    
    def chunk_text_by_tokens(self, text: str, chunk_size: int = 200, overlap: int = 50) -> List[str]:
        """
        ✂️ Split text into overlapping token-based chunks.
        
        Args:
            text: Input text
            chunk_size: Target tokens per chunk
            overlap: Overlap tokens between chunks
            
        Returns:
            List of text chunks
        """
        # 🔤 Tokenize using simple word tokenization
        tokens = simple_word_tokenize(text)
        
        if len(tokens) <= chunk_size:
            return [text]
        
        chunks = []
        start_idx = 0
        
        while start_idx < len(tokens):
            # 📐 Calculate chunk boundaries
            end_idx = min(start_idx + chunk_size, len(tokens))
            chunk_tokens = tokens[start_idx:end_idx]
            
            # 🔗 Join tokens back to text
            chunk_text = ' '.join(chunk_tokens)
            chunks.append(chunk_text)
            
            # 📍 Move start position (with overlap)
            start_idx += chunk_size - overlap
            
            # 🛑 Break if we've covered all tokens
            if end_idx >= len(tokens):
                break
        
        return chunks
    
    def preprocess_document(self, text: str, metadata: Dict[str, Any] = None) -> List[Document]:
        """
        🔄 Preprocess a single document with Arabic normalization.
        
        Args:
            text: Document text
            metadata: Document metadata
            
        Returns:
            List of processed document chunks
        """
        # 🔤 Normalize Arabic text
        normalized_text = self.normalize_arabic_text(text)
        
        # ✂️ Create custom chunks
        chunks = self.chunk_text_by_tokens(normalized_text, chunk_size=200, overlap=50)
        
        # 📄 Create Haystack documents for each chunk
        documents = []
        for i, chunk in enumerate(chunks):
            chunk_metadata = (metadata or {}).copy()
            chunk_metadata.update({
                'chunk_id': i,
                'total_chunks': len(chunks),
                'chunk_length': len(chunk.split())
            })
            
            doc = Document(
                content=chunk,
                meta=chunk_metadata
            )
            documents.append(doc)
        
        return documents
    
    def ingest_html_file(self, file_path: str, metadata: Dict[str, Any] = None) -> None:
        """
        📄 Ingest a single HTML file.
        
        Args:
            file_path: Path to HTML file
            metadata: Additional metadata
        """
        try:
            # 📖 Read HTML file
            with open(file_path, 'r', encoding='utf-8') as f:
                html_content = f.read()
            
            # 🕸️ Extract content from HTML
            extracted = self.extract_html_content(html_content)
            
            # 🏷️ Prepare metadata
            if metadata is None:
                metadata = {}
            metadata.update(extracted['metadata'])
            metadata.update({
                'source_file': file_path,
                'filename': os.path.basename(file_path),
                'file_type': 'html'
            })
            
            # 🔄 Preprocess and create documents
            processed_docs = self.preprocess_document(extracted['text'], metadata)
            
            # 💾 Store documents
            self.ingest_documents(processed_docs)
            
            print(f"✅ Processed {file_path}: {len(processed_docs)} chunks")
            
        except Exception as e:
            print(f"❌ Error processing {file_path}: {e}")
    
    def ingest_html_articles(self, html_files: List[str]) -> None:
        """
        📚 Batch ingest multiple HTML articles.
        
        Args:
            html_files: List of HTML file paths
        """
        print(f"🚀 Starting ingestion of {len(html_files)} HTML files...")
        
        total_chunks = 0
        successful_files = 0
        
        for i, file_path in enumerate(html_files, 1):
            print(f"📄 Processing {i}/{len(html_files)}: {os.path.basename(file_path)}")
            
            try:
                self.ingest_html_file(file_path)
                successful_files += 1
            except Exception as e:
                print(f"❌ Failed to process {file_path}: {e}")
                continue
        
        total_chunks = self.get_document_count()
        print(f"🎉 Ingestion complete!")
        print(f"📊 Successfully processed: {successful_files}/{len(html_files)} files")
        print(f"📄 Total chunks created: {total_chunks}")
    
    def ingest_from_directory(self, directory_path: str, file_pattern: str = "*.html") -> None:
        """
        📁 Ingest all HTML files from a directory.
        
        Args:
            directory_path: Path to directory containing HTML files
            file_pattern: Glob pattern for file matching
        """
        directory = Path(directory_path)
        html_files = list(directory.glob(file_pattern))
        
        if not html_files:
            print(f"❌ No HTML files found in {directory_path}")
            return
        
        print(f"📁 Found {len(html_files)} HTML files in {directory_path}")
        self.ingest_html_articles([str(f) for f in html_files])
    
    def ingest_documents(self, documents: List[Document]) -> None:
        """
        💾 Ingest documents into both FAISS and SQLite stores.
        
        Args:
            documents: List of processed documents
        """
        try:
            # 🗂️ Write to FAISS store
            self.document_store.write_documents(documents)
            
            # 🗃️ Write to SQL store for metadata queries
            self.sql_store.write_documents(documents)
            
        except Exception as e:
            print(f"❌ Error ingesting documents: {e}")
    
    def save_index(self) -> None:
        """💾 Save the FAISS index to disk."""
        self.document_store.save(self.faiss_index_path)
        print(f"💾 FAISS index saved to {self.faiss_index_path}")
    
    def load_index(self) -> None:
        """📖 Load the FAISS index from disk."""
        try:
            print(f"📖 FAISS index loaded from {self.faiss_index_path}")
        except Exception as e:
            print(f"❌ Error loading index: {e}")
    
    def get_document_count(self) -> int:
        """📊 Get the total number of documents in the store."""
        return self.document_store.get_document_count()
    
    def get_statistics(self) -> Dict[str, Any]:
        """📈 Get ingestion statistics."""
        return {
            'total_documents': self.get_document_count(),
            'faiss_index_path': self.faiss_index_path,
            'sqlite_path': self.sqlite_path
        }


# 🎯 Example usage script
if __name__ == "__main__":
    # 🚀 Initialize ingestor
    ingestor = DocumentIngestor()
    
    # 📁 Process HTML files from directory
    html_directory = input("📁 Enter path to HTML files directory: ").strip()
    
    if os.path.exists(html_directory):
        print("🎙️ Starting Arabic HTML ingestion...")
        ingestor.ingest_from_directory(html_directory)
        
        # 💾 Save index
        ingestor.save_index()
        
        # 📊 Show statistics
        stats = ingestor.get_statistics()
        print(f"📈 Final stats: {stats}")
    else:
        print("❌ Directory not found!")
