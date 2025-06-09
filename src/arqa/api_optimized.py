"""
ARQA Optimized API - High-Performance FastAPI Interface
Phase 4: Performance Optimized API Development

Provides REST endpoints with:
- Background processing for document uploads
- Incremental indexing (only embed new documents)  
- GPU acceleration when available
- Batch processing optimization
- Non-blocking upload responses
"""

from fastapi import FastAPI, HTTPException, UploadFile, File, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import uvicorn
import asyncio
import os
import sys
import json
import tempfile
from datetime import datetime
import threading
import time

# Add project root to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from src.arqa.simple_ingest import SimpleDocumentIngestor
from src.arqa.retriever_optimized_fixed import OptimizedArabicRetriever
from src.arqa.reader_simple import SimpleArabicQA

# Initialize FastAPI app
app = FastAPI(
    title="ARQA - Optimized Arabic Question Answering API",
    description="High-performance Arabic Question Answering system with background processing",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global system components with performance optimizations
class OptimizedARQASystem:
    def __init__(self):
        self.ingestor = None
        self.retriever = None
        self.qa_system = None
        self.initialized = False
        self.document_count = 0
        self.processing_queue = []
        self.processing_stats = {
            'total_uploads': 0,
            'successful_uploads': 0,
            'failed_uploads': 0,
            'background_tasks': 0,
            'avg_processing_time': 0.0
        }
        
    async def initialize(self, use_gpu: bool = True, fast_mode: bool = False):
        """Initialize all ARQA components with performance optimizations"""
        if self.initialized:
            return
            
        try:
            print("🚀 Initializing Optimized ARQA System...")
            
            # Initialize components with performance settings
            self.ingestor = SimpleDocumentIngestor()
            
            # Use optimized retriever with GPU support
            device = "cuda" if use_gpu else "cpu"
            batch_size = 64 if use_gpu else 32
            
            self.retriever = OptimizedArabicRetriever(
                device=device,
                batch_size=batch_size,
                use_fast_model=fast_mode
            )
              # Initialize QA system (SimpleArabicQA doesn't take device parameter)
            self.qa_system = SimpleArabicQA()
            
            self.initialized = True
            
            stats = self.retriever.get_stats()
            print(f"✅ Optimized ARQA System initialized!")
            print(f"🔥 Device: {stats['device']}")
            print(f"📊 Batch size: {stats['batch_size']}")
            print(f"📚 Existing documents: {stats['total_documents']}")
            
        except Exception as e:
            print(f"❌ Failed to initialize Optimized ARQA System: {e}")
            raise

# Global system instance
arqa = OptimizedARQASystem()

# Pydantic models for API
class QuestionRequest(BaseModel):
    question: str
    top_k: int = 3
    min_confidence: float = 0.01

class QuestionResponse(BaseModel):
    question: str
    answers: List[Dict[str, Any]]
    processing_time: float
    retrieved_docs: int

class DocumentUploadResponse(BaseModel):
    filename: str
    status: str
    chunks_created: int
    new_documents: int
    skipped_duplicates: int
    total_documents: int
    processing_time: float
    background_processing: bool

class SystemStatus(BaseModel):
    status: str
    initialized: bool
    document_count: int
    components: Dict[str, bool]
    models: Dict[str, str]
    performance: Dict[str, Any]
    indexing_status: Dict[str, Any]

class ProcessingStats(BaseModel):
    total_uploads: int
    successful_uploads: int
    failed_uploads: int
    background_tasks: int
    avg_processing_time: float
    queue_length: int

# Background processing functions
async def process_document_background(filename: str, html_content: str):
    """Background task for document processing."""
    start_time = time.time()
    
    try:
        print(f"🔄 Background processing: {filename}")
        
        # Process with ingestor
        documents = arqa.ingestor.process_html_content(html_content, source_url=filename)
        
        # Add to optimized retriever with background indexing
        result = arqa.retriever.add_documents_incremental(documents, background=True)
        
        arqa.document_count = result['total_documents']
        arqa.processing_stats['successful_uploads'] += 1
        arqa.processing_stats['background_tasks'] += 1
        
        processing_time = time.time() - start_time
        arqa.processing_stats['avg_processing_time'] = (
            (arqa.processing_stats['avg_processing_time'] * (arqa.processing_stats['successful_uploads'] - 1) + processing_time) / 
            arqa.processing_stats['successful_uploads']
        )
        
        print(f"✅ Background processed: {filename} ({processing_time:.2f}s)")
        
    except Exception as e:
        arqa.processing_stats['failed_uploads'] += 1
        print(f"❌ Background processing failed for {filename}: {e}")

# API Endpoints

@app.on_event("startup")
async def startup_event():
    """Initialize ARQA system on startup with performance optimization"""
    try:
        # Try GPU first, fall back to CPU if not available
        await arqa.initialize(use_gpu=True, fast_mode=False)
    except Exception as e:
        print(f"⚠️  GPU initialization failed: {e}")
        print("🔄 Falling back to CPU mode...")
        await arqa.initialize(use_gpu=False, fast_mode=False)

@app.get("/", response_class=HTMLResponse)
async def root():
    """Root endpoint with enhanced interface"""
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>ARQA - Optimized Arabic Question Answering</title>
        <meta charset="utf-8">
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
            .container { max-width: 900px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            h1 { color: #2c3e50; text-align: center; }
            .section { margin: 20px 0; padding: 20px; border: 1px solid #ddd; border-radius: 5px; }
            .endpoint { background: #ecf0f1; padding: 10px; margin: 10px 0; border-radius: 3px; }
            .arabic { direction: rtl; font-size: 18px; color: #27ae60; }
            .button { background: #3498db; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; }
            .performance { background: #e8f5e8; padding: 15px; border-radius: 5px; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🚀 ARQA - Optimized Arabic Question Answering System</h1>
            <div class="arabic">نظام الإجابة على الأسئلة العربية المُحسَّن</div>
            
            <div class="section performance">
                <h2>⚡ Performance Features</h2>
                <ul>
                    <li>🔥 <strong>GPU Acceleration</strong> - CUDA support for 10x faster processing</li>
                    <li>📦 <strong>Background Processing</strong> - Non-blocking document uploads</li>
                    <li>🔄 <strong>Incremental Indexing</strong> - Only embed new documents</li>
                    <li>⚡ <strong>Batch Processing</strong> - Optimized batch sizes for throughput</li>
                    <li>🚫 <strong>Deduplication</strong> - Automatic duplicate document detection</li>
                </ul>
            </div>
            
            <div class="section">
                <h2>📚 System Features</h2>
                <ul>
                    <li>✅ Arabic HTML document processing with PyArabic normalization</li>
                    <li>✅ High-performance semantic search with AraDPR</li>
                    <li>✅ Multilingual question answering</li>
                    <li>✅ REST API with OpenAPI documentation</li>
                    <li>✅ Real-time processing status monitoring</li>
                </ul>
            </div>
            
            <div class="section">
                <h2>🔗 API Endpoints</h2>
                <div class="endpoint"><strong>GET /status</strong> - System status with performance metrics</div>
                <div class="endpoint"><strong>POST /upload</strong> - Upload documents (returns immediately)</div>
                <div class="endpoint"><strong>POST /ask</strong> - Ask Arabic questions</div>
                <div class="endpoint"><strong>GET /processing-stats</strong> - Background processing statistics</div>
                <div class="endpoint"><strong>GET /indexing-status</strong> - Real-time indexing status</div>
                <div class="endpoint"><strong>GET /docs</strong> - Interactive API documentation</div>
            </div>
            
            <div class="section">
                <h2>📖 Quick Start</h2>
                <p>1. Upload HTML documents via <code>/upload</code> (returns immediately)</p>
                <p>2. Monitor processing via <code>/indexing-status</code></p>
                <p>3. Ask questions in Arabic via <code>/ask</code></p>
                <p>4. View detailed docs at <a href="/docs" class="button">API Documentation</a></p>
            </div>
        </div>
    </body>
    </html>
    """
    return html_content

@app.get("/status", response_model=SystemStatus)
async def get_status():
    """Get system status with performance metrics"""
    if not arqa.initialized:
        await arqa.initialize()
    
    # Get indexing status
    indexing_status = arqa.retriever.get_indexing_status() if arqa.retriever else {}
    
    # Get performance stats
    performance_stats = arqa.retriever.get_stats() if arqa.retriever else {}
    
    return SystemStatus(
        status="ready" if arqa.initialized else "initializing",
        initialized=arqa.initialized,
        document_count=arqa.document_count,
        components={
            "ingestor": arqa.ingestor is not None,
            "retriever": arqa.retriever is not None,
            "qa_system": arqa.qa_system is not None
        },
        models={
            "retrieval": arqa.retriever.model_name if arqa.retriever else "Not loaded",
            "qa": "deepset/xlm-roberta-base-squad2"
        },
        performance=performance_stats,
        indexing_status=indexing_status
    )

@app.post("/upload", response_model=DocumentUploadResponse)
async def upload_document(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    """Optimized document upload with background processing"""
    if not arqa.initialized:
        await arqa.initialize()
    
    start_time = datetime.now()
    
    try:
        # Validate file type
        if not file.filename.endswith(('.html', '.htm')):
            raise HTTPException(status_code=400, detail="Only HTML files are supported")
        
        # Read file content quickly
        content = await file.read()
        html_content = content.decode('utf-8')
        
        # Quick validation and preprocessing
        documents = arqa.ingestor.process_html_content(html_content, source_url=file.filename)
        
        if not documents:
            raise HTTPException(status_code=400, detail="No content could be extracted from the file")
        
        # Add documents with background processing
        result = arqa.retriever.add_documents_incremental(documents, background=True)
        
        arqa.document_count = result['total_documents']
        arqa.processing_stats['total_uploads'] += 1
        
        # If background processing, add to background tasks for monitoring
        if result['background_processing']:
            background_tasks.add_task(
                process_document_background, 
                file.filename, 
                html_content
            )
        
        processing_time = (datetime.now() - start_time).total_seconds()
        
        return DocumentUploadResponse(
            filename=file.filename,
            status="queued" if result['background_processing'] else "completed",
            chunks_created=len(documents),
            new_documents=result['new_documents'],
            skipped_duplicates=result['skipped_duplicates'],
            total_documents=result['total_documents'],
            processing_time=processing_time,
            background_processing=result['background_processing']
        )
        
    except Exception as e:
        arqa.processing_stats['failed_uploads'] += 1
        raise HTTPException(status_code=500, detail=f"Error processing document: {str(e)}")

@app.post("/ask", response_model=QuestionResponse)
async def ask_question(request: QuestionRequest):
    """Optimized Arabic question answering"""
    if not arqa.initialized:
        await arqa.initialize()
    
    if arqa.document_count == 0:
        raise HTTPException(status_code=400, detail="No documents uploaded yet. Please upload documents first.")
    
    start_time = datetime.now()
    
    try:
        # Fast retrieval with optimized retriever
        retrieved_docs = arqa.retriever.retrieve(request.question, top_k=request.top_k)
        
        if not retrieved_docs:
            return QuestionResponse(
                question=request.question,
                answers=[],
                processing_time=(datetime.now() - start_time).total_seconds(),
                retrieved_docs=0
            )
        
        # Convert to QA format
        docs_for_qa = []
        for doc in retrieved_docs:
            docs_for_qa.append({
                'content': doc.content,
                'metadata': doc.meta,
                'score': doc.score,
                'id': doc.doc_id
            })
        
        # Get answers
        answers = arqa.qa_system.answer_with_retrieved_docs(
            request.question, 
            docs_for_qa, 
            top_k=request.top_k
        )
        
        # Filter by confidence
        filtered_answers = [
            answer for answer in answers 
            if answer.get('confidence', 0) >= request.min_confidence
        ]
        
        processing_time = (datetime.now() - start_time).total_seconds()
        
        return QuestionResponse(
            question=request.question,
            answers=filtered_answers,
            processing_time=processing_time,
            retrieved_docs=len(retrieved_docs)
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing question: {str(e)}")

@app.get("/processing-stats", response_model=ProcessingStats)
async def get_processing_stats():
    """Get background processing statistics"""
    if not arqa.initialized:
        await arqa.initialize()
    
    indexing_status = arqa.retriever.get_indexing_status()
    
    return ProcessingStats(
        total_uploads=arqa.processing_stats['total_uploads'],
        successful_uploads=arqa.processing_stats['successful_uploads'],
        failed_uploads=arqa.processing_stats['failed_uploads'],
        background_tasks=arqa.processing_stats['background_tasks'],
        avg_processing_time=arqa.processing_stats['avg_processing_time'],
        queue_length=indexing_status.get('queue_length', 0)
    )

@app.get("/indexing-status")
async def get_indexing_status():
    """Get real-time indexing status"""
    if not arqa.initialized:
        await arqa.initialize()
    
    status = arqa.retriever.get_indexing_status()
    
    return {
        **status,
        "timestamp": datetime.now().isoformat(),
        "processing_stats": arqa.processing_stats
    }

@app.get("/documents")
async def list_documents():
    """List all processed documents with enhanced stats"""
    if not arqa.initialized:
        await arqa.initialize()
    
    stats = arqa.retriever.get_stats()
    
    return {
        "total_documents": arqa.document_count,
        "indexed_documents": stats.get('index_size', 0),
        "cached_embeddings": stats.get('cached_embeddings', 0),
        "retriever_status": "ready" if arqa.retriever else "not_initialized",
        "performance_stats": stats
    }

@app.delete("/documents")
async def clear_documents():
    """Clear all documents from the system"""
    if not arqa.initialized:
        await arqa.initialize()
    
    try:
        # Reinitialize retriever to clear documents
        arqa.retriever = OptimizedArabicRetriever(
            device=arqa.retriever.device,
            batch_size=arqa.retriever.batch_size
        )
        arqa.document_count = 0
        
        return {"message": "All documents cleared successfully", "document_count": 0}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error clearing documents: {str(e)}")

@app.get("/health")
async def health_check():
    """Enhanced health check with performance metrics"""
    if not arqa.initialized:
        await arqa.initialize()
    
    stats = arqa.retriever.get_stats() if arqa.retriever else {}
    
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "system": "ARQA Optimized v2.0.0",
        "performance": {
            "device": stats.get('device', 'unknown'),
            "batch_size": stats.get('batch_size', 'unknown'),
            "total_documents": stats.get('total_documents', 0),
            "index_size": stats.get('index_size', 0)
        }
    }

# Production-optimized server function
def run_optimized_server(host: str = "0.0.0.0", port: int = 8000, workers: int = 1):
    """Run the optimized ARQA API server"""
    print("🚀 Starting ARQA Optimized API Server...")
    print(f"📍 Server: http://{host}:{port}")
    print(f"📖 API Docs: http://{host}:{port}/docs")
    print(f"⚡ Workers: {workers}")
    print(f"🔥 GPU: {'Enabled' if os.environ.get('CUDA_VISIBLE_DEVICES') != '-1' else 'Disabled'}")
    
    # Production configuration without --reload
    uvicorn.run(
        app, 
        host=host, 
        port=port, 
        workers=workers,
        reload=False,  # Disable reload for production
        log_level="info"
    )

if __name__ == "__main__":
    # Check for GPU availability
    import torch
    if torch.cuda.is_available():
        print(f"🔥 GPU detected: {torch.cuda.get_device_name(0)}")
        workers = 1  # Single worker for GPU to avoid conflicts
    else:
        print("💻 Running on CPU")
        workers = 4  # Multiple workers for CPU
    
    run_optimized_server(workers=workers)
