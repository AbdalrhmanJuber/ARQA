# Phase 4: API Service

## Overview
The API Service phase provides a RESTful web interface for the complete ARQA system. Built with FastAPI, it orchestrates all phases and offers a scalable, production-ready endpoint for Arabic question answering services.

## Key Components

### 1. Web Framework Architecture
- **FastAPI**: Modern, high-performance web framework
- **Pydantic Models**: Request/response validation and serialization
- **ASGI Server**: Asynchronous server gateway interface with Uvicorn
- **CORS Support**: Cross-origin resource sharing for web applications

### 2. API Endpoints Structure
```
HTTP Request → Route Handler → Pipeline Orchestration → Response Formation
```

## Implementation Details

### FastAPI Application
**Location**: `src/arqa/api.py`

#### Core Functions:

1. **`create_app()`**
   - Initializes FastAPI application
   - Configures middleware and CORS
   - Sets up route handlers
   - Returns configured app instance

2. **Dependency Injection System**
   - `get_ingestor()`: DocumentIngestor instance
   - `get_retriever()`: DocumentRetriever instance  
   - `get_reader()`: QuestionAnswerer instance

#### API Endpoints:

1. **`GET /`** - Root endpoint with API information
2. **`GET /health`** - Health check and system status
3. **`POST /ingest`** - Document ingestion endpoint
4. **`POST /search`** - Document retrieval endpoint
5. **`POST /qa`** - Complete question answering pipeline
6. **`POST /update-embeddings`** - Refresh document embeddings

## Request/Response Models

### Pydantic Schemas
**Location**: `src/arqa/api.py`

#### Input Models:
```python
class Document(BaseModel):
    content: str
    meta: Optional[Dict[str, Any]] = {}

class IngestRequest(BaseModel):
    documents: List[Document]

class QuestionRequest(BaseModel):
    question: str
    top_k: Optional[int] = 3
```

#### Output Models:
```python
class AnswerResponse(BaseModel):
    answer: str
    score: float
    start: int
    end: int
    document_id: Optional[str] = None
    document_meta: Optional[Dict[str, Any]] = {}
    document_score: Optional[float] = 0.0

class QuestionAnsweringResponse(BaseModel):
    question: str
    answers: List[AnswerResponse]
    processing_time: float
```

## API Endpoints Documentation

### 1. Document Ingestion
**Endpoint**: `POST /ingest`

**Purpose**: Add documents to the system for indexing and retrieval

**Request Body**:
```json
{
    "documents": [
        {
            "content": "النص العربي هنا",
            "meta": {
                "title": "عنوان الوثيقة",
                "source": "مصدر الوثيقة",
                "date": "2025-06-08"
            }
        }
    ]
}
```

**Response**:
```json
{
    "message": "Successfully ingested 1 documents",
    "count": 1
}
```

### 2. Document Search
**Endpoint**: `POST /search`

**Purpose**: Search for relevant documents without question answering

**Request Body**:
```json
{
    "question": "ما هو الذكاء الاصطناعي؟",
    "top_k": 5
}
```

**Response**:
```json
{
    "query": "ما هو الذكاء الاصطناعي؟",
    "results": [
        {
            "content": "محتوى الوثيقة...",
            "meta": {"title": "الذكاء الاصطناعي"},
            "score": 0.95,
            "id": "doc_1"
        }
    ],
    "count": 5
}
```

### 3. Question Answering
**Endpoint**: `POST /qa`

**Purpose**: Complete pipeline - retrieve documents and extract answers

**Request Body**:
```json
{
    "question": "ما هي فوائد الذكاء الاصطناعي؟",
    "top_k": 3
}
```

**Response**:
```json
{
    "question": "ما هي فوائد الذكاء الاصطناعي؟",
    "answers": [
        {
            "answer": "تحسين الكفاءة والإنتاجية",
            "score": 0.92,
            "start": 25,
            "end": 45,
            "document_id": "doc_1",
            "document_meta": {"title": "AI Benefits"},
            "document_score": 0.88
        }
    ],
    "processing_time": 1.23
}
```

### 4. Health Check
**Endpoint**: `GET /health`

**Purpose**: Monitor system health and status

**Response**:
```json
{
    "status": "healthy",
    "service": "ARQA"
}
```

## Pipeline Orchestration

### Complete QA Pipeline Process:
1. **Request Validation**: Pydantic model validation
2. **Query Preprocessing**: Arabic text normalization
3. **Document Retrieval**: Semantic search with FAISS
4. **Answer Extraction**: Question answering with BERT
5. **Response Formation**: Result aggregation and formatting
6. **Performance Tracking**: Timing and metrics collection

### Error Handling Strategy:
```python
try:
    # Pipeline execution
    results = process_request(request)
    return success_response(results)
except ValidationError:
    raise HTTPException(status_code=422, detail="Invalid input")
except ModelError:
    raise HTTPException(status_code=500, detail="Model processing failed")
except Exception as e:
    raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")
```

## Production Deployment

### Server Configuration
```python
# Development
uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)

# Production
uvicorn.run("api:app", host="0.0.0.0", port=8000, 
           workers=4, access_log=True, log_level="info")
```

### Environment Variables
```bash
ARQA_INDEX_PATH=./faiss_index
ARQA_MODEL_NAME=aubmindlab/bert-base-arabertv02
ARQA_QA_MODEL=aubmindlab/arabert-qa
ARQA_MAX_WORKERS=4
ARQA_LOG_LEVEL=info
```

### Docker Deployment
```dockerfile
FROM python:3.9

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY src/ ./src/
COPY main.py .

EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## Security Considerations

### Input Validation:
- Request size limits
- Content type validation
- SQL injection prevention
- XSS protection

### Authentication & Authorization:
```python
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer

security = HTTPBearer()

async def verify_token(token: str = Depends(security)):
    # Token validation logic
    if not is_valid_token(token):
        raise HTTPException(status_code=401, detail="Invalid token")
    return token
```

### Rate Limiting:
```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.post("/qa")
@limiter.limit("10/minute")
async def question_answering(request: Request, ...):
    # Endpoint logic
```

## Performance Optimization

### Async Processing:
```python
import asyncio

async def process_multiple_questions(questions: List[str]):
    tasks = [process_single_question(q) for q in questions]
    results = await asyncio.gather(*tasks)
    return results
```

### Caching Strategy:
```python
from functools import lru_cache
import redis

# In-memory caching
@lru_cache(maxsize=1000)
def cached_retrieval(query_hash: str):
    return retrieve_documents(query_hash)

# Redis caching
redis_client = redis.Redis(host='localhost', port=6379, db=0)

def cache_results(key: str, results: dict, ttl: int = 3600):
    redis_client.setex(key, ttl, json.dumps(results))
```

### Load Balancing:
- Multiple worker processes
- Request queuing
- Connection pooling
- Database connection management

## Monitoring and Observability

### Metrics Collection:
```python
from prometheus_client import Counter, Histogram, generate_latest

REQUEST_COUNT = Counter('arqa_requests_total', 'Total requests', ['endpoint'])
REQUEST_DURATION = Histogram('arqa_request_duration_seconds', 'Request duration')

@app.middleware("http")
async def add_metrics(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    REQUEST_DURATION.observe(time.time() - start_time)
    REQUEST_COUNT.labels(endpoint=request.url.path).inc()
    return response
```

### Logging Configuration:
```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('arqa.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("arqa")
```

### Health Monitoring:
```python
@app.get("/health/detailed")
async def detailed_health():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "0.1.0",
        "components": {
            "document_store": check_document_store(),
            "embedding_model": check_embedding_model(),
            "qa_model": check_qa_model()
        }
    }
```

## API Documentation

### Automatic Documentation:
- **Swagger UI**: Available at `/docs`
- **ReDoc**: Available at `/redoc`
- **OpenAPI Schema**: Available at `/openapi.json`

### Custom Documentation:
```python
app = FastAPI(
    title="ARQA - Arabic Question Answering API",
    description="Complete pipeline for Arabic text retrieval and QA",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc"
)
```

## Client Integration

### Python Client:
```python
import requests

class ARQAClient:
    def __init__(self, base_url: str):
        self.base_url = base_url
    
    def ask_question(self, question: str, top_k: int = 3):
        response = requests.post(
            f"{self.base_url}/qa",
            json={"question": question, "top_k": top_k}
        )
        return response.json()

# Usage
client = ARQAClient("http://localhost:8000")
result = client.ask_question("ما هو الذكاء الاصطناعي؟")
```

### JavaScript Client:
```javascript
class ARQAClient {
    constructor(baseUrl) {
        this.baseUrl = baseUrl;
    }
    
    async askQuestion(question, topK = 3) {
        const response = await fetch(`${this.baseUrl}/qa`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ question, top_k: topK })
        });
        return response.json();
    }
}

// Usage
const client = new ARQAClient('http://localhost:8000');
client.askQuestion('ما هو الذكاء الاصطناعي؟').then(console.log);
```

## Testing Strategy

### Unit Tests:
```python
import pytest
from fastapi.testclient import TestClient

def test_health_endpoint():
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
```

### Integration Tests:
```python
def test_complete_qa_pipeline():
    # Ingest test documents
    ingest_response = client.post("/ingest", json=test_documents)
    assert ingest_response.status_code == 200
    
    # Ask question
    qa_response = client.post("/qa", json={"question": "test question"})
    assert qa_response.status_code == 200
    assert "answers" in qa_response.json()
```

### Load Testing:
```python
import asyncio
import aiohttp

async def load_test():
    async with aiohttp.ClientSession() as session:
        tasks = []
        for _ in range(100):
            task = session.post(
                "http://localhost:8000/qa",
                json={"question": "test question"}
            )
            tasks.append(task)
        
        responses = await asyncio.gather(*tasks)
        return responses
```

## Best Practices

1. **API Design**: RESTful principles, consistent naming
2. **Error Handling**: Comprehensive error responses
3. **Documentation**: Detailed API documentation
4. **Testing**: Unit, integration, and load testing
5. **Security**: Authentication, input validation, rate limiting
6. **Monitoring**: Comprehensive logging and metrics
7. **Performance**: Caching, async processing, optimization

## Troubleshooting

### Common Issues:
- **Port conflicts**: Change port configuration
- **Model loading failures**: Check file permissions and paths
- **Memory errors**: Optimize model loading and caching
- **Slow responses**: Profile and optimize pipeline components

### Debug Mode:
```python
app = FastAPI(debug=True)  # Enable detailed error messages
uvicorn.run(app, debug=True, reload=True)  # Enable auto-reload
```
