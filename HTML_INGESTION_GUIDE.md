# 🚀 ARQA Enhanced HTML Ingestion Setup Guide

This guide explains how to set up and use the enhanced Arabic Question Answering (ARQA) system with HTML ingestion capabilities.

## 📋 Prerequisites

Make sure you have Python 3.8+ installed on your system.

## 🔧 Installation

1. **Clone or navigate to the ARQA directory:**
   ```bash
   cd c:\Users\a-ahm\Desktop\arqa
   ```

2. **Install required dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Install additional Arabic language dependencies:**
   ```bash
   # For CAMEL-tools Arabic processing
   pip install camel-tools[cli]
   
   # For Farasa Arabic segmentation
   pip install farasa==0.0.9
   ```

## 🎯 Enhanced HTML Ingestion Features

The enhanced `ingest.py` module now includes:

### ✨ Key Features:
- 🕸️ **HTML Content Extraction**: Smart extraction from HTML files with BeautifulSoup
- 🔤 **Arabic Text Normalization**: Comprehensive normalization of Hamza, Ta-marbuta, etc.
- ✂️ **Smart Chunking**: 200-token chunks with 25% overlap for optimal retrieval
- 💾 **Dual Storage**: FAISS for semantic search + SQLite for metadata queries
- 📊 **Rich Metadata**: Automatic extraction of titles, descriptions, keywords
- 🎙️ **Emoji Flow**: Clear emoji-commented methods for easy code reading

### 🏗️ Architecture:
```
DocumentIngestor
├── 🕸️ extract_html_content()     # Clean HTML → text + metadata
├── 🔤 normalize_arabic_text()    # Arabic text normalization
├── ✂️ chunk_text_by_tokens()     # Smart 200-token chunking
├── 📄 ingest_html_file()         # Process single HTML file
├── 📚 ingest_html_articles()     # Batch process multiple files
├── 📁 ingest_from_directory()    # Process directory of HTML files
└── 💾 save_index()               # Persist FAISS index
```

## 📚 Usage Examples

### 1. Basic HTML Directory Processing

```python
from src.arqa.ingest import DocumentIngestor

# Initialize ingestor
ingestor = DocumentIngestor(
    faiss_index_path="./indices/arabic_articles",
    sqlite_path="./data/articles.db"
)

# Process all HTML files in a directory
ingestor.ingest_from_directory("./path/to/html/articles")

# Save the index
ingestor.save_index()

# Get statistics
stats = ingestor.get_statistics()
print(f"Processed {stats['total_documents']} document chunks")
```

### 2. Single File Processing

```python
# Process a single HTML file
ingestor.ingest_html_file(
    "article.html", 
    metadata={"category": "technology", "source": "news_site"}
)
```

### 3. Batch Processing with Custom Metadata

```python
html_files = [
    "tech_article1.html",
    "tech_article2.html", 
    "science_article1.html"
]

ingestor.ingest_html_articles(html_files)
```

## 🧪 Testing the System

Run the included test script to verify everything works:

```bash
python test_html_ingestion.py
```

This will:
- Create sample Arabic HTML articles
- Process them through the ingestion pipeline
- Show statistics and results
- Demonstrate the full workflow

## 📊 Text Processing Pipeline

### Input HTML:
```html
<article>
    <h1>الذكاء الاصطناعي</h1>
    <p>يُعتبر الذكاء الاصطناعي من أهم التطورات...</p>
</article>
```

### Processing Steps:
1. **🕸️ HTML Extraction**: Remove tags, extract clean text
2. **🔤 Arabic Normalization**: 
   - `أإآ` → `ا` (Hamza normalization)
   - `ة` → `ه` (Ta-marbuta normalization)
   - Remove diacritics and extra whitespace
3. **✂️ Smart Chunking**: Split into 200-token chunks with 50-token overlap
4. **💾 Storage**: Save to FAISS (vectors) + SQLite (metadata)

### Output Structure:
```json
{
    "content": "الذكاء الاصطناعي يعتبر من اهم التطورات...",
    "metadata": {
        "title": "الذكاء الاصطناعي",
        "chunk_id": 0,
        "total_chunks": 3,
        "source_file": "article.html",
        "chunk_length": 187
    }
}
```

## 🎛️ Configuration Options

### DocumentIngestor Parameters:
- `faiss_index_path`: Path to store FAISS vector index
- `sqlite_path`: Path to SQLite metadata database  
- `embedding_dim`: Vector embedding dimensions (default: 768)

### Chunking Parameters:
- `chunk_size`: Tokens per chunk (default: 200)
- `overlap`: Overlap between chunks (default: 50 = 25%)

## 📁 Output Files

After processing, you'll have:
- `faiss_index/`: FAISS vector index files
- `documents.db`: SQLite database with metadata
- Processing logs showing statistics

## 🔍 Next Steps

Once ingestion is complete, you can:
1. **Phase 2**: Use `retriever.py` for semantic search
2. **Phase 3**: Use `reader.py` for question answering
3. **Phase 4**: Start the FastAPI service with `api.py`

## 🛠️ Troubleshooting

### Common Issues:

1. **Import Errors**: Make sure all dependencies are installed
   ```bash
   pip install -r requirements.txt
   ```

2. **Arabic Text Issues**: Ensure HTML files are UTF-8 encoded

3. **Memory Issues**: For large datasets, process in smaller batches

4. **FAISS Index Errors**: Delete existing index files and recreate

### Debug Mode:
Enable verbose logging by modifying the ingestor:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 📞 Support

For issues or questions:
- Check the documentation in `docs/` directory
- Review the phase-specific guides
- Examine the test script for usage examples

---
🎉 **Congratulations!** Your enhanced ARQA HTML ingestion system is ready to process Arabic web content with state-of-the-art normalization and chunking!
