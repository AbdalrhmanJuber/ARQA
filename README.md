# ARQA - Arabic Question Answering System

A comprehensive system for Arabic text processing, retrieval, and question answering using state-of-the-art NLP techniques.

## 🏗️ System Architecture

The ARQA system consists of four main phases, each with comprehensive documentation:

### Phase 1: Document Ingestion (`ingest.py`)
**Purpose**: Preprocess and index Arabic documents for efficient retrieval.

**Key Features**:
- Arabic text preprocessing with CAMEL-tools and Farasa
- Document normalization and vector indexing
- FAISS-based semantic search preparation

📖 **[Complete Phase 1 Documentation](docs/phase1_ingestion.md)**

### Phase 2: Document Retrieval (`retriever.py`)
**Purpose**: Find semantically relevant documents for a given Arabic query.

**Key Features**:
- Dense passage retrieval with Arabic BERT embeddings
- Query preprocessing and semantic similarity matching
- Configurable relevance scoring and ranking

📖 **[Complete Phase 2 Documentation](docs/phase2_retrieval.md)**

### Phase 3: Reading Comprehension (`reader.py`)
**Purpose**: Extract precise answers from retrieved documents using question answering models.

**Key Features**:
- Arabic QA models with confidence scoring
- Multi-document answer extraction and aggregation
- Support for various question types and answer patterns

📖 **[Complete Phase 3 Documentation](docs/phase3_reading.md)**

### Phase 4: API Service (`api.py`)
**Purpose**: Provide RESTful API endpoints for the complete QA pipeline.

**Key Features**:
- FastAPI framework with automatic documentation
- Complete pipeline orchestration and error handling
- Production-ready deployment with monitoring

📖 **[Complete Phase 4 Documentation](docs/phase4_api.md)**

## 📚 Complete Documentation

For comprehensive documentation covering implementation details, configuration options, performance optimization, and troubleshooting guides:

**[📖 Full Documentation Index](docs/README.md)**

### Available Endpoints:
- `POST /ingest` - Ingest documents into the system
- `POST /search` - Search for relevant documents  
- `POST /qa` - Complete question answering pipeline
- `GET /health` - System health check
- `POST /update-embeddings` - Refresh document embeddings

## 🚀 Quick Start

1. **Install Dependencies**:
```powershell
pip install -r requirements.txt
```

2. **Run the Server**:
```powershell
python main.py
```

3. **Access API Documentation**:
- Interactive docs: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 📊 Usage Examples

### Ingest Documents
```python
import requests

documents = [
    {
        "content": "النص العربي هنا",
        "meta": {"title": "Document 1", "source": "source1"}
    }
]

response = requests.post("http://localhost:8000/ingest", 
                        json={"documents": documents})
```

### Ask Questions
```python
response = requests.post("http://localhost:8000/qa", 
                        json={"question": "ما هو السؤال؟", "top_k": 3})
```

## 🔧 Configuration

- **Index Path**: Default FAISS index location: `./faiss_index`
- **Models**: Default Arabic BERT models for embeddings and QA
- **Server**: Default host: `0.0.0.0`, port: `8000`

## 📝 API Response Format

### Question Answering Response
```json
{
    "question": "السؤال المطروح",
    "answers": [
        {
            "answer": "الإجابة",
            "score": 0.95,
            "start": 10,
            "end": 25,
            "document_id": "doc_1",
            "document_meta": {},
            "document_score": 0.88
        }
    ],
    "processing_time": 1.23
}
```

## 🎯 Features

- ✅ Arabic text preprocessing with linguistic tools
- ✅ Semantic document retrieval with FAISS
- ✅ Extractive question answering with BERT
- ✅ RESTful API with comprehensive documentation
- ✅ Scalable architecture with modular design
- ✅ Error handling and logging
- ✅ CORS support for web applications

## 🔍 Technical Details

### Models Used
- **Embeddings**: `aubmindlab/bert-base-arabertv02`
- **Question Answering**: `aubmindlab/arabert-qa`
- **Preprocessing**: CAMEL-tools + Farasa

### Dependencies
- `camel-tools`: Arabic morphological analysis
- `farasa==0.0.9`: Arabic text segmentation  
- `transformers`: Hugging Face transformer models
- `haystack[faiss]`: Document store and retrieval
- `fastapi`: Web framework
- `uvicorn[standard]`: ASGI server
