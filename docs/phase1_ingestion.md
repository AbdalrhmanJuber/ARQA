# Phase 1: Document Ingestion

## Overview
The Document Ingestion phase is responsible for preprocessing raw Arabic text documents and preparing them for efficient retrieval. This phase ensures that Arabic text is properly normalized, tokenized, and indexed for semantic search.

## Key Components

### 1. Arabic Text Preprocessing
- **Farasa Segmentation**: Handles Arabic word segmentation and morphological analysis
- **CAMEL Tokenization**: Provides advanced Arabic linguistic processing
- **Text Normalization**: Standardizes Arabic text encoding and format

### 2. Document Processing Pipeline
```
Raw Arabic Text → Normalization → Segmentation → Tokenization → Embedding → FAISS Index
```

## Implementation Details

### DocumentIngestor Class
**Location**: `src/arqa/ingest.py`

#### Methods:

1. **`__init__(index_path)`**
   - Initializes FAISS document store
   - Sets up Farasa segmenter and CAMEL tokenizer
   - Configures index storage path

2. **`preprocess_arabic_text(text)`**
   - Applies Farasa segmentation for proper word boundaries
   - Uses CAMEL tokenization for linguistic analysis
   - Returns normalized, processed text

3. **`ingest_documents(documents)`**
   - Processes list of documents
   - Applies preprocessing pipeline
   - Creates Haystack Document objects
   - Stores in FAISS index

4. **`ingest_from_file(file_path)`**
   - Loads documents from file (JSON, CSV, etc.)
   - Batch processing for large datasets

## Arabic Language Considerations

### Challenges Addressed:
1. **Right-to-Left Text**: Proper handling of RTL text direction
2. **Diacritics**: Normalization of Arabic diacritical marks
3. **Word Segmentation**: Handling of attached pronouns and particles
4. **Morphological Complexity**: Rich morphological structure of Arabic

### Tools Used:
- **Farasa**: State-of-the-art Arabic segmenter
- **CAMEL-tools**: Comprehensive Arabic NLP toolkit
- **Unicode Normalization**: Proper character encoding handling

## Performance Considerations

### Optimization Strategies:
1. **Batch Processing**: Process multiple documents simultaneously
2. **Memory Management**: Efficient handling of large document collections
3. **Index Optimization**: FAISS configuration for fast retrieval
4. **Preprocessing Caching**: Cache processed text when possible

### Scalability:
- Supports incremental document addition
- Memory-efficient streaming for large files
- Parallel processing capabilities

## Usage Example

```python
from arqa.ingest import DocumentIngestor

# Initialize ingestor
ingestor = DocumentIngestor(index_path="./my_index")

# Prepare documents
documents = [
    {
        "content": "هذا نص عربي للمعالجة والفهرسة",
        "meta": {
            "title": "وثيقة تجريبية",
            "source": "مصدر الوثيقة",
            "date": "2025-06-08"
        }
    }
]

# Ingest documents
ingestor.ingest_documents(documents)
print("Documents successfully ingested!")
```

## Configuration Options

### FAISS Index Settings:
- **Index Type**: FAISS Flat (exact search) or IVF (approximate)
- **Vector Dimension**: Depends on embedding model (768 for BERT)
- **Distance Metric**: Cosine similarity or L2 distance

### Preprocessing Parameters:
- **Segmentation Level**: Word, subword, or character level
- **Normalization Options**: Diacritic handling, case normalization
- **Tokenization Strategy**: Linguistic vs. statistical tokenization

## Error Handling

### Common Issues:
1. **Encoding Problems**: UTF-8 encoding validation
2. **Empty Documents**: Skip or flag empty content
3. **Large Documents**: Chunking strategy for oversized texts
4. **Memory Limits**: Batch size optimization

### Validation:
- Content length validation
- Character encoding verification
- Metadata schema validation
- Index integrity checks

## Integration Points

### Input Sources:
- JSON document collections
- CSV files with text columns
- Plain text files
- Database connections
- Web scraping pipelines

### Output Format:
- FAISS vector index
- Document metadata store
- Processing statistics
- Error logs and reports

## Monitoring and Logging

### Metrics Tracked:
- Documents processed per minute
- Average processing time per document
- Memory usage during ingestion
- Index size and growth rate

### Logging Events:
- Document ingestion start/completion
- Preprocessing errors and warnings
- Index update operations
- Performance bottlenecks

## Best Practices

1. **Data Quality**: Ensure clean, well-formatted input text
2. **Batch Size**: Optimize batch size for available memory
3. **Index Maintenance**: Regular index optimization and cleanup
4. **Backup Strategy**: Regular backups of index and metadata
5. **Version Control**: Track document versions and updates

## Troubleshooting

### Common Problems:
- **Out of Memory**: Reduce batch size, increase system RAM
- **Slow Processing**: Check CPU usage, optimize preprocessing
- **Index Corruption**: Verify disk space, check file permissions
- **Encoding Errors**: Validate input text encoding

### Debug Mode:
Enable verbose logging to track processing steps and identify bottlenecks.
