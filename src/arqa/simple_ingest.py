"""
Simplified HTML Ingestion Module for ARQA
Works without complex C++ dependencies like camel-kenlm
"""

from typing import List, Dict, Any, Optional
import os
import re
import json
from pathlib import Path
import unicodedata
from bs4 import BeautifulSoup


class SimpleDocumentIngestor:
    """🚀 Simplified Arabic HTML document preprocessing and ingestion."""
    
    def __init__(self, 
                 output_dir: str = "processed_documents",
                 chunk_size: int = 200):
        """
        🔧 Initialize the simplified document ingestor.
        
        Args:
            output_dir: Directory to store processed documents
            chunk_size: Target tokens per chunk
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.chunk_size = chunk_size
        
        # 📋 Arabic normalization patterns
        self.normalization_patterns = [
            # Hamza normalization
            (r'[أإآ]', 'ا'),  # Different alif forms to standard alif
            (r'ؤ', 'و'),      # Hamza on waw to waw
            (r'ئ', 'ي'),      # Hamza on yaa to yaa
            (r'ة', 'ه'),      # Ta marbuta to ha
            (r'ى', 'ي'),      # Alif maksura to yaa
            # Remove diacritics
            (r'[\u064B-\u0652\u0670\u0640]', ''),  # Tashkeel and tatweel
            # Normalize spaces
            (r'\s+', ' '),    # Multiple spaces to single
        ]
    
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
        for script in soup(["script", "style", "nav", "header", "footer"]):
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
            elif meta.get('name') == 'author':
                metadata['author'] = meta.get('content', '')
        
        return {
            'text': text,
            'metadata': metadata
        }
    
    def normalize_arabic_text(self, text: str) -> str:
        """
        🔤 Normalize Arabic text using simple patterns.
        
        Args:
            text: Raw Arabic text
            
        Returns:
            Normalized Arabic text
        """
        if not text:
            return ""
        
        # 📐 Apply Unicode normalization first
        normalized = unicodedata.normalize('NFKC', text)
        
        # 🔄 Apply Arabic-specific normalizations
        for pattern, replacement in self.normalization_patterns:
            normalized = re.sub(pattern, replacement, normalized)
        
        # 🧽 Clean extra whitespace
        normalized = re.sub(r'\s+', ' ', normalized).strip()
        
        return normalized
    
    def simple_tokenize(self, text: str) -> List[str]:
        """
        🔤 Simple Arabic-aware tokenization.
        
        Args:
            text: Input text
            
        Returns:
            List of tokens
        """
        # Split by whitespace and punctuation
        tokens = re.findall(r'\S+', text)
        return tokens
    
    def chunk_text_by_tokens(self, text: str, chunk_size: Optional[int] = None, overlap: int = 50) -> List[str]:
        """
        ✂️ Split text into overlapping token-based chunks.
        
        Args:
            text: Input text
            chunk_size: Target tokens per chunk
            overlap: Overlap tokens between chunks
            
        Returns:
            List of text chunks
        """
        if chunk_size is None:
            chunk_size = self.chunk_size
        
        tokens = self.simple_tokenize(text)
        
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
    
    def process_html_file(self, file_path: str) -> List[Dict[str, Any]]:
        """
        📄 Process a single HTML file.
        
        Args:
            file_path: Path to HTML file
            
        Returns:
            List of processed document chunks
        """
        try:
            # 📖 Read HTML file
            with open(file_path, 'r', encoding='utf-8') as f:
                html_content = f.read()
            
            # 🕸️ Extract content from HTML
            extracted = self.extract_html_content(html_content)
            
            # 🔤 Normalize Arabic text
            normalized_text = self.normalize_arabic_text(extracted['text'])
            
            # ✂️ Create chunks
            chunks = self.chunk_text_by_tokens(normalized_text)
            
            # 📦 Create document objects
            documents = []
            for i, chunk in enumerate(chunks):
                doc = {
                    'content': chunk,
                    'metadata': {
                        **extracted['metadata'],
                        'source_file': file_path,
                        'filename': os.path.basename(file_path),
                        'chunk_id': i,
                        'total_chunks': len(chunks),
                        'chunk_length': len(chunk.split())
                    }
                }
                documents.append(doc)
            
            print(f"✅ Processed {file_path}: {len(documents)} chunks")
            return documents
            
        except Exception as e:
            print(f"❌ Error processing {file_path}: {e}")
            return []
    
    def ingest_from_directory(self, directory_path: str, file_pattern: str = "*.html") -> List[Dict[str, Any]]:
        """
        📁 Process all HTML files from a directory.
        
        Args:
            directory_path: Path to directory containing HTML files
            file_pattern: Glob pattern for file matching
            
        Returns:
            List of all processed documents
        """
        directory = Path(directory_path)
        html_files = list(directory.glob(file_pattern))
        
        if not html_files:
            print(f"❌ No HTML files found in {directory_path}")
            return []
        
        print(f"📁 Found {len(html_files)} HTML files in {directory_path}")
        
        all_documents = []
        successful_files = 0
        
        for i, file_path in enumerate(html_files, 1):
            print(f"📄 Processing {i}/{len(html_files)}: {file_path.name}")
            
            documents = self.process_html_file(str(file_path))
            if documents:
                all_documents.extend(documents)
                successful_files += 1
        
        # 💾 Save processed documents
        self.save_documents(all_documents)
        
        print(f"🎉 Processing complete!")
        print(f"📊 Successfully processed: {successful_files}/{len(html_files)} files")
        print(f"📄 Total chunks created: {len(all_documents)}")
        
        return all_documents
    
    def save_documents(self, documents: List[Dict[str, Any]]) -> None:
        """
        💾 Save processed documents to JSON file.
        
        Args:
            documents: List of processed documents
        """
        output_file = self.output_dir / "processed_documents.json"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(documents, f, ensure_ascii=False, indent=2)
        
        print(f"💾 Saved {len(documents)} documents to {output_file}")
    
    def get_statistics(self) -> Dict[str, Any]:
        """📈 Get processing statistics."""
        output_file = self.output_dir / "processed_documents.json"
        
        if output_file.exists():
            with open(output_file, 'r', encoding='utf-8') as f:
                documents = json.load(f)
            
            return {
                'total_documents': len(documents),
                'output_directory': str(self.output_dir),
                'output_file': str(output_file)
            }
        else:
            return {
                'total_documents': 0,
                'output_directory': str(self.output_dir),
                'output_file': str(output_file)
            }


# Create an alias for compatibility
DocumentIngestor = SimpleDocumentIngestor


# 🎯 Example usage script
if __name__ == "__main__":
    # 🚀 Initialize simple ingestor
    ingestor = SimpleDocumentIngestor()
    
    # 📁 Process HTML files from directory
    html_directory = input("📁 Enter path to HTML files directory: ").strip()
    
    if os.path.exists(html_directory):
        print("🎙️ Starting simplified Arabic HTML ingestion...")
        documents = ingestor.ingest_from_directory(html_directory)
        
        # 📊 Show statistics
        stats = ingestor.get_statistics()
        print(f"📈 Final stats: {stats}")
    else:
        print("❌ Directory not found!")
