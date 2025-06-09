#!/usr/bin/env python3
"""
Test script for the complete ARQA system
Tests document ingestion, retrieval, and question answering
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from arqa.simple_ingest import SimpleDocumentIngestor
from arqa.retriever import ArabicDocumentRetriever
from arqa.reader_simple import SimpleArabicQA

def test_complete_arqa_pipeline():
    """Test the complete ARQA pipeline"""
    print("🧪 Testing Complete ARQA Pipeline")
    print("=" * 50)
    
    # Step 1: Document Ingestion
    print("\n📄 Step 1: Document Ingestion")
    ingestor = SimpleDocumentIngestor()
    
    # Load test documents
    test_docs = [
        "test_html_articles/arabic_science.html",
        "test_html_articles/artificial_intelligence.html"
    ]
      all_documents = []
    for doc_path in test_docs:
        if os.path.exists(doc_path):
            print(f"   Processing: {doc_path}")
            documents = ingestor.process_html_file(doc_path)
            all_documents.extend(documents)
            print(f"   ✅ Extracted {len(documents)} chunks")
    
    print(f"📚 Total documents ingested: {len(all_documents)}")
    
    if not all_documents:
        print("❌ No documents to process. Check if test files exist.")
        return
    
    # Step 2: Retrieval System
    print("\n🔍 Step 2: Setting up Retrieval")
    retriever = ArabicDocumentRetriever()
    
    print("   Building document index...")
    retriever.add_documents(all_documents)
    print("   ✅ Index built successfully")
    
    # Step 3: Question Answering
    print("\n🤔 Step 3: Question Answering Setup")
    try:
        qa_system = SimpleArabicQA()
        print("   ✅ QA system initialized successfully")
    except Exception as e:
        print(f"   ❌ QA system initialization failed: {e}")
        return
    
    # Step 4: End-to-End Testing
    print("\n🎯 Step 4: End-to-End Question Answering")
    
    # Test questions in Arabic
    test_questions = [
        "ما هو الذكاء الاصطناعي؟",
        "كيف يعمل التعلم الآلي؟",
        "ما هي تطبيقات الذكاء الاصطناعي؟"
    ]
    
    for i, question in enumerate(test_questions, 1):
        print(f"\n--- Test Question {i} ---")
        print(f"❓ Question: {question}")        
        try:
            # Retrieve relevant documents
            retrieved_docs = retriever.retrieve(question, top_k=3)
            print(f"📖 Retrieved {len(retrieved_docs)} relevant documents")
            
            if retrieved_docs:
                # Convert RetrievedDocument objects to dict format for QA system
                docs_for_qa = []
                for doc in retrieved_docs:
                    docs_for_qa.append({
                        'content': doc.content,
                        'metadata': doc.meta,
                        'score': doc.score,
                        'id': doc.doc_id
                    })
                
                # Get answers using QA system
                answers = qa_system.answer_with_retrieved_docs(
                    question, 
                    docs_for_qa, 
                    top_k=2
                )
                
                if answers:
                    print("💡 Answers found:")
                    for j, answer in enumerate(answers, 1):
                        print(f"   {j}. {answer['answer']}")
                        print(f"      Confidence: {answer['confidence']:.3f}")
                        print(f"      Source: {answer['document_title']}")
                        print(f"      Combined Score: {answer['combined_score']:.3f}")
                else:
                    print("   ⚠️ No confident answers found")
            else:
                print("   ⚠️ No relevant documents retrieved")
                
        except Exception as e:
            print(f"   ❌ Error processing question: {e}")
    
    print("\n🎉 ARQA Pipeline Test Complete!")
    print("=" * 50)

if __name__ == "__main__":
    test_complete_arqa_pipeline()
