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

# 🔄 Advanced imports (require transformers, torch, faiss)
try:
    from .retriever import ArabicDocumentRetriever, RetrievedDocument
    __all__.extend(['ArabicDocumentRetriever', 'RetrievedDocument'])
except ImportError:
    # Will be available when transformers, torch, faiss are installed
    pass

# 🔄 Advanced QA imports (require transformers + QA models)
try:
    from .reader_simple import SimpleArabicQA, create_arabic_qa_system
    __all__.extend(['SimpleArabicQA', 'create_arabic_qa_system'])
except ImportError:
    # Will be available when transformers and QA models are installed
    pass

# 🔄 Future imports (require additional dependencies)
# from .ingest import DocumentIngestor  # requires haystack
# from .reader import QuestionAnswerer   # requires transformers + QA models
try:
    from .api import create_app
    __all__.append('create_app')
except ImportError:
    pass

__all__ = [
    "DocumentIngestor",
    "DocumentRetriever", 
    "QuestionAnswerer",
    "create_app"
]
