"""
ARQA - Arabic Question Answering System
A comprehensive system for Arabic text processing, retrieval, and question answering.
"""

__version__ = "0.1.0"
__author__ = "ARQA Team"

# ✅ Working imports (no complex dependencies)
try:
    from .simple_ingest import SimpleDocumentIngestor
    __all__ = ['SimpleDocumentIngestor']
except ImportError:
    __all__ = []

# 🔄 Advanced imports (require complex dependencies)
# Uncomment when dependencies are installed:
# from .ingest import DocumentIngestor
# from .retriever import DocumentRetriever  
# from .reader import QuestionAnswerer
from .api import create_app

__all__ = [
    "DocumentIngestor",
    "DocumentRetriever", 
    "QuestionAnswerer",
    "create_app"
]
