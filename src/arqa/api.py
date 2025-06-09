"""
ARQA API - FastAPI Web Interface for Arabic Question Answering
Phase 4: API Development

Provides REST endpoints for:
- Document upload and processing
- Arabic question answering
- System status and health checks
"""

from fastapi import FastAPI, HTTPException, UploadFile, File, Form, BackgroundTasks
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

# Add project root to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from src.arqa.simple_ingest import SimpleDocumentIngestor
from src.arqa.retriever import ArabicDocumentRetriever
from src.arqa.reader_simple import SimpleArabicQA

# Initialize FastAPI app
app = FastAPI(
    title="ARQA - Arabic Question Answering API",
    description="Arabic Question Answering system with document processing and semantic search",
    version="1.0.0",
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

# Global system components
class ARQASystem:
    def __init__(self):
        self.ingestor = None
        self.retriever = None
        self.qa_system = None
        self.initialized = False
        self.document_count = 0
        
    async def initialize(self):
        """Initialize all ARQA components"""
        if self.initialized:
            return
            
        try:
            print("🔧 Initializing ARQA System...")
            
            # Initialize components
            self.ingestor = SimpleDocumentIngestor()
            self.retriever = ArabicDocumentRetriever()
            self.qa_system = SimpleArabicQA()
            
            self.initialized = True
            print("✅ ARQA System initialized successfully!")
            
        except Exception as e:
            print(f"❌ Failed to initialize ARQA System: {e}")
            raise

# Global system instance
arqa = ARQASystem()

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
    chunks_created: int
    total_documents: int
    processing_time: float

class SystemStatus(BaseModel):
    status: str
    initialized: bool
    document_count: int
    components: Dict[str, bool]
    models: Dict[str, str]

# API Endpoints

@app.on_event("startup")
async def startup_event():
    """Initialize ARQA system on startup"""
    await arqa.initialize()

@app.get("/", response_class=HTMLResponse)
async def root():
    """Root endpoint with basic interface"""
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>ARQA - Arabic Question Answering</title>
        <meta charset="utf-8">
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
            .container { max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            h1 { color: #2c3e50; text-align: center; }
            .section { margin: 20px 0; padding: 20px; border: 1px solid #ddd; border-radius: 5px; }
            .endpoint { background: #ecf0f1; padding: 10px; margin: 10px 0; border-radius: 3px; }
            .arabic { direction: rtl; font-size: 18px; color: #27ae60; }
            .button { background: #3498db; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🌟 ARQA - Arabic Question Answering System</h1>
            <div class="arabic">نظام الإجابة على الأسئلة العربية</div>
            
            <div class="section">
                <h2>📚 System Features</h2>
                <ul>
                    <li>✅ Arabic HTML document processing</li>
                    <li>✅ Semantic search with AraDPR</li>
                    <li>✅ Multilingual question answering</li>
                    <li>✅ REST API interface</li>
                </ul>
            </div>
            
            <div class="section">
                <h2>🔗 API Endpoints</h2>
                <div class="endpoint"><strong>GET /status</strong> - System status</div>
                <div class="endpoint"><strong>POST /upload</strong> - Upload HTML document</div>
                <div class="endpoint"><strong>POST /ask</strong> - Ask Arabic question</div>
                <div class="endpoint"><strong>GET /docs</strong> - Interactive API documentation</div>
            </div>
            
            <div class="section">
                <h2>📖 Quick Start</h2>
                <p>1. Upload HTML documents via <code>/upload</code></p>
                <p>2. Ask questions in Arabic via <code>/ask</code></p>
                <p>3. View detailed docs at <a href="/docs" class="button">API Documentation</a></p>
            </div>
        </div>
    </body>
    </html>
    """
    return html_content

@app.get("/status", response_model=SystemStatus)
async def get_status():
    """Get system status and health"""
    if not arqa.initialized:
        await arqa.initialize()
    
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
            "retrieval": "abdoelsayed/AraDPR",
            "qa": "deepset/xlm-roberta-base-squad2"
        }
    )

@app.post("/upload", response_model=DocumentUploadResponse)
async def upload_document(file: UploadFile = File(...)):
    """Upload and process HTML document"""
    if not arqa.initialized:
        await arqa.initialize()
    
    start_time = datetime.now()
    
    try:
        # Validate file type
        if not file.filename.endswith(('.html', '.htm')):
            raise HTTPException(status_code=400, detail="Only HTML files are supported")
        
        # Read file content
        content = await file.read()
        html_content = content.decode('utf-8')
        
        # Process with ingestor
        documents = arqa.ingestor.process_html_content(html_content, source_url=file.filename)
        
        # Add to retriever
        arqa.retriever.add_documents(documents)
        arqa.document_count += len(documents)
        
        processing_time = (datetime.now() - start_time).total_seconds()
        
        return DocumentUploadResponse(
            filename=file.filename,
            chunks_created=len(documents),
            total_documents=arqa.document_count,
            processing_time=processing_time
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing document: {str(e)}")

@app.post("/ask", response_model=QuestionResponse)
async def ask_question(request: QuestionRequest):
    """Ask a question in Arabic"""
    if not arqa.initialized:
        await arqa.initialize()
    
    if arqa.document_count == 0:
        raise HTTPException(status_code=400, detail="No documents uploaded yet. Please upload documents first.")
    
    start_time = datetime.now()
    
    try:
        # Retrieve relevant documents
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

@app.get("/documents")
async def list_documents():
    """List all processed documents"""
    if not arqa.initialized:
        await arqa.initialize()
    
    return {
        "total_documents": arqa.document_count,
        "retriever_status": "ready" if arqa.retriever else "not_initialized"
    }

@app.delete("/documents")
async def clear_documents():
    """Clear all documents from the system"""
    if not arqa.initialized:
        await arqa.initialize()
    
    try:
        # Reinitialize retriever to clear documents
        arqa.retriever = ArabicDocumentRetriever()
        arqa.document_count = 0
        
        return {"message": "All documents cleared successfully", "document_count": 0}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error clearing documents: {str(e)}")

@app.get("/health")
async def health_check():
    """Simple health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "system": "ARQA v1.0.0"
    }

# Development server function
def run_server(host: str = "127.0.0.1", port: int = 8000):
    """Run the ARQA API server"""
    print("🚀 Starting ARQA API Server...")
    print(f"📍 Server will be available at: http://{host}:{port}")
    print(f"📖 API Documentation: http://{host}:{port}/docs")
    print(f"🔄 Interactive API: http://{host}:{port}/redoc")
    
    uvicorn.run(app, host=host, port=port, reload=False)

if __name__ == "__main__":
    # Run server if called directly
    run_server()
