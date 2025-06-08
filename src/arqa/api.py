"""
FastAPI Application for ARQA
Provides REST API endpoints for Arabic Question Answering system.
"""

from typing import List, Dict, Any, Optional
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

from .ingest import DocumentIngestor
from .retriever import DocumentRetriever
from .reader import QuestionAnswerer


# Pydantic models for request/response
class Document(BaseModel):
    content: str
    meta: Optional[Dict[str, Any]] = {}


class IngestRequest(BaseModel):
    documents: List[Document]


class QuestionRequest(BaseModel):
    question: str
    top_k: Optional[int] = 3


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


# Global instances (in production, use dependency injection)
document_ingestor = None
document_retriever = None
question_answerer = None


def get_ingestor() -> DocumentIngestor:
    """Dependency to get document ingestor instance."""
    global document_ingestor
    if document_ingestor is None:
        document_ingestor = DocumentIngestor()
    return document_ingestor


def get_retriever() -> DocumentRetriever:
    """Dependency to get document retriever instance."""
    global document_retriever
    if document_retriever is None:
        document_retriever = DocumentRetriever()
    return document_retriever


def get_reader() -> QuestionAnswerer:
    """Dependency to get question answerer instance."""
    global question_answerer
    if question_answerer is None:
        question_answerer = QuestionAnswerer()
    return question_answerer


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    
    app = FastAPI(
        title="ARQA - Arabic Question Answering API",
        description="REST API for Arabic text retrieval and question answering",
        version="0.1.0"
    )
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Configure appropriately for production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    @app.get("/")
    async def root():
        """Root endpoint with API information."""
        return {
            "message": "ARQA - Arabic Question Answering API",
            "version": "0.1.0",
            "endpoints": {
                "health": "/health",
                "ingest": "/ingest",
                "search": "/search", 
                "qa": "/qa"
            }
        }
    
    @app.get("/health")
    async def health_check():
        """Health check endpoint."""
        return {"status": "healthy", "service": "ARQA"}
    
    @app.post("/ingest")
    async def ingest_documents(
        request: IngestRequest,
        ingestor: DocumentIngestor = Depends(get_ingestor)
    ):
        """Ingest documents into the system."""
        try:
            # Convert Pydantic models to dictionaries
            documents = [doc.dict() for doc in request.documents]
            
            # Ingest documents
            ingestor.ingest_documents(documents)
            
            return {
                "message": f"Successfully ingested {len(documents)} documents",
                "count": len(documents)
            }
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Ingestion failed: {str(e)}")
    
    @app.post("/search")
    async def search_documents(
        request: QuestionRequest,
        retriever: DocumentRetriever = Depends(get_retriever)
    ):
        """Search for relevant documents."""
        try:
            results = retriever.retrieve(
                query=request.question,
                top_k=request.top_k
            )
            
            return {
                "query": request.question,
                "results": results,
                "count": len(results)
            }
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")
    
    @app.post("/qa", response_model=QuestionAnsweringResponse)
    async def question_answering(
        request: QuestionRequest,
        retriever: DocumentRetriever = Depends(get_retriever),
        reader: QuestionAnswerer = Depends(get_reader)
    ):
        """Answer a question using retrieval and reading comprehension."""
        import time
        
        start_time = time.time()
        
        try:
            # Retrieve relevant documents
            documents = retriever.retrieve(
                query=request.question,
                top_k=request.top_k * 2  # Retrieve more docs for better coverage
            )
            
            if not documents:
                raise HTTPException(status_code=404, detail="No relevant documents found")
            
            # Answer question using retrieved documents
            answers = reader.answer_with_documents(
                question=request.question,
                documents=documents,
                top_k=request.top_k
            )
            
            processing_time = time.time() - start_time
            
            # Convert to response format
            answer_responses = [AnswerResponse(**answer) for answer in answers]
            
            return QuestionAnsweringResponse(
                question=request.question,
                answers=answer_responses,
                processing_time=processing_time
            )
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"QA failed: {str(e)}")
    
    @app.post("/update-embeddings")
    async def update_embeddings(
        retriever: DocumentRetriever = Depends(get_retriever)
    ):
        """Update document embeddings."""
        try:
            retriever.update_embeddings()
            return {"message": "Embeddings updated successfully"}
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Update failed: {str(e)}")
    
    return app


# For running with uvicorn
app = create_app()

if __name__ == "__main__":
    uvicorn.run(
        "api:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
