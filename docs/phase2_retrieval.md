# Phase 2: Document Retrieval

## Overview
The Document Retrieval phase implements semantic search to find the most relevant documents for a given Arabic query. This phase uses dense passage retrieval with Arabic BERT embeddings to identify contextually similar content.

## Key Components

### 1. Semantic Search Engine
- **Dense Embeddings**: Vector representations of text using Arabic BERT
- **Similarity Matching**: Cosine similarity between query and document vectors
- **FAISS Index**: High-performance approximate nearest neighbor search
- **Ranking Algorithm**: Score-based document ranking

### 2. Query Processing Pipeline
```
Arabic Query → Preprocessing → Embedding → FAISS Search → Ranking → Top-K Results
```

## Implementation Details

### DocumentRetriever Class
**Location**: `src/arqa/retriever.py`

#### Methods:

1. **`__init__(index_path, model_name, top_k)`**
   - Loads FAISS document store
   - Initializes Arabic BERT embedding model
   - Configures retrieval parameters

2. **`preprocess_query(query)`**
   - Applies same preprocessing as documents
   - Ensures consistent query-document representation
   - Uses CAMEL tokenization

3. **`retrieve(query, top_k)`**
   - Converts query to embedding vector
   - Performs FAISS similarity search
   - Returns ranked list of relevant documents

4. **`update_embeddings()`**
   - Regenerates embeddings for all documents
   - Updates FAISS index with new vectors
   - Useful when changing embedding models

## Technical Architecture

### Embedding Model
- **Default Model**: `aubmindlab/bert-base-arabertv02`
- **Vector Dimension**: 768 dimensions
- **Language**: Optimized for Modern Standard Arabic
- **Fine-tuning**: Pre-trained on large Arabic corpora

### FAISS Configuration
- **Index Type**: FAISS Flat for exact search (small datasets) or IVF for approximate search (large datasets)
- **Distance Metric**: Cosine similarity (normalized dot product)
- **Memory Usage**: Configurable based on available RAM

## Retrieval Strategies

### 1. Dense Retrieval
**Advantages**:
- Captures semantic meaning beyond keyword matching
- Handles synonyms and paraphrases effectively
- Works well with Arabic morphological variations

**Process**:
1. Query encoding with BERT
2. Vector similarity computation
3. Top-K document selection

### 2. Ranking and Scoring
**Similarity Score**: Cosine similarity between query and document embeddings
**Range**: 0.0 (no similarity) to 1.0 (perfect match)
**Threshold**: Configurable minimum similarity score

## Arabic Language Considerations

### Morphological Variations
- **Root-based System**: Arabic words share common roots
- **Affixation**: Prefixes and suffixes modify meaning
- **Inflection**: Gender, number, and case variations

### Handling Strategies:
1. **Subword Tokenization**: BERT's WordPiece handles morphological variants
2. **Contextual Embeddings**: Dynamic representations based on context
3. **Preprocessing Consistency**: Same pipeline for queries and documents

## Performance Optimization

### Speed Improvements:
1. **GPU Acceleration**: CUDA support for embedding computation
2. **Batch Processing**: Multiple queries processed simultaneously
3. **Index Optimization**: FAISS parameter tuning
4. **Caching**: Store frequently accessed embeddings

### Memory Management:
- **Embedding Precision**: Float16 vs Float32 trade-offs
- **Index Sharding**: Split large indices across multiple files
- **Lazy Loading**: Load embeddings on-demand

## Usage Example

```python
from arqa.retriever import DocumentRetriever

# Initialize retriever
retriever = DocumentRetriever(
    index_path="./faiss_index",
    model_name="aubmindlab/bert-base-arabertv02",
    top_k=10
)

# Search for relevant documents
query = "ما هي فوائد الذكاء الاصطناعي؟"
results = retriever.retrieve(query, top_k=5)

for result in results:
    print(f"Score: {result['score']:.3f}")
    print(f"Content: {result['content'][:100]}...")
    print(f"Metadata: {result['meta']}")
    print("-" * 50)
```

## Evaluation Metrics

### Retrieval Quality:
1. **Precision@K**: Relevant documents in top-K results
2. **Recall@K**: Fraction of relevant documents retrieved
3. **MRR (Mean Reciprocal Rank)**: Average inverse rank of first relevant result
4. **NDCG (Normalized Discounted Cumulative Gain)**: Ranking quality measure

### Performance Metrics:
1. **Query Latency**: Time to retrieve results
2. **Throughput**: Queries processed per second
3. **Memory Usage**: RAM consumption during retrieval
4. **Index Size**: Storage requirements

## Configuration Parameters

### Model Settings:
```python
retriever_config = {
    "embedding_model": "aubmindlab/bert-base-arabertv02",
    "max_seq_length": 512,
    "batch_size": 32,
    "use_gpu": True
}
```

### FAISS Settings:
```python
faiss_config = {
    "index_type": "Flat",  # or "IVF"
    "nlist": 100,  # for IVF index
    "nprobe": 10,  # search parameter
    "distance_metric": "cosine"
}
```

## Error Handling

### Common Issues:
1. **Index Not Found**: Missing or corrupted FAISS index
2. **Model Loading Errors**: Network issues or missing models
3. **Memory Errors**: Insufficient RAM for large indices
4. **GPU Errors**: CUDA compatibility issues

### Fallback Strategies:
- Switch to CPU if GPU unavailable
- Use smaller batch sizes for memory constraints
- Rebuild index if corruption detected
- Download models with retry logic

## Integration with Other Phases

### Input from Phase 1 (Ingestion):
- FAISS document index
- Document metadata
- Embedding vectors

### Output to Phase 3 (Reading):
- Ranked document list
- Relevance scores
- Document content and metadata

## Advanced Features

### 1. Query Expansion
- Add synonyms and related terms
- Use Arabic thesaurus for expansion
- Morphological variations inclusion

### 2. Hybrid Retrieval
- Combine dense and sparse retrieval
- BM25 + Dense embedding fusion
- Weighted scoring combination

### 3. Filtering and Faceting
- Filter by document metadata
- Date range filtering
- Source-based restrictions
- Content type filtering

## Monitoring and Analytics

### Search Analytics:
- Popular query patterns
- Low-performing queries
- Retrieval success rates
- User satisfaction metrics

### System Monitoring:
- Index health checks
- Query response times
- Resource utilization
- Error rates and types

## Best Practices

1. **Index Maintenance**: Regular index optimization and updates
2. **Query Analysis**: Monitor and analyze search patterns
3. **Model Updates**: Periodically evaluate newer embedding models
4. **Relevance Tuning**: Adjust similarity thresholds based on domain
5. **Performance Testing**: Regular load testing and optimization

## Troubleshooting Guide

### Poor Retrieval Quality:
- Check query preprocessing consistency
- Verify embedding model appropriateness
- Analyze relevance scores distribution
- Consider domain-specific fine-tuning

### Performance Issues:
- Profile query execution times
- Check FAISS index configuration
- Monitor memory and GPU usage
- Optimize batch sizes

### Index Problems:
- Validate index integrity
- Check file permissions and disk space
- Verify document count consistency
- Test with sample queries
