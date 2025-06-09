#!/usr/bin/env python3
"""
Final demonstration of the complete ARQA (Arabic Question Answering) system
Shows the full pipeline: HTML ingestion → Document retrieval → Arabic QA
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from arqa.simple_ingest import SimpleDocumentIngestor
from arqa.retriever import ArabicDocumentRetriever
from arqa.reader_simple import SimpleArabicQA

def demo_arqa_system():
    """Demonstrate the complete ARQA system capabilities"""
    print("🌟 ARQA - Arabic Question Answering System")
    print("=" * 60)
    print("📚 Complete Pipeline: HTML → Retrieval → Arabic QA")
    print("=" * 60)
    
    # Step 1: Initialize Components
    print("\n🔧 Initializing ARQA Components...")
    
    print("   📄 Document Ingestor")
    ingestor = SimpleDocumentIngestor()
    
    print("   🔍 Arabic Document Retriever")  
    retriever = ArabicDocumentRetriever()
    
    print("   🤔 Arabic Question Answering")
    qa_system = SimpleArabicQA()
    
    print("   ✅ All components initialized successfully!")
    
    # Step 2: Load and Process Documents
    print("\n📚 Loading Arabic Documents...")
    
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
            print(f"   ✅ Extracted {len(documents)} text chunks")
    
    print(f"\n📊 Total documents in knowledge base: {len(all_documents)}")
    
    # Step 3: Build Search Index
    print("\n🏗️ Building Search Index...")
    retriever.add_documents(all_documents)
    print("   ✅ FAISS vector index created successfully")
    
    # Step 4: Interactive QA Demo
    print("\n🎯 Arabic Question Answering Demo")
    print("-" * 40)
    
    demo_questions = [
        {
            "question": "ما هو الذكاء الاصطناعي؟",
            "english": "What is artificial intelligence?"
        },
        {
            "question": "ما هي تطبيقات الذكاء الاصطناعي؟", 
            "english": "What are the applications of artificial intelligence?"
        },
        {
            "question": "كيف يؤثر الذكاء الاصطناعي على المجتمع؟",
            "english": "How does artificial intelligence affect society?"
        }
    ]
    
    for i, qa_pair in enumerate(demo_questions, 1):
        print(f"\n🤔 Question {i}: {qa_pair['question']}")
        print(f"   ({qa_pair['english']})")
        
        # Retrieve relevant documents
        retrieved_docs = retriever.retrieve(qa_pair['question'], top_k=3)
        print(f"   📖 Found {len(retrieved_docs)} relevant documents")
        
        if retrieved_docs:
            # Convert to format expected by QA system
            docs_for_qa = []
            for doc in retrieved_docs:
                docs_for_qa.append({
                    'content': doc.content,
                    'metadata': doc.meta,
                    'score': doc.score,
                    'id': doc.doc_id
                })
            
            # Get answers
            answers = qa_system.answer_with_retrieved_docs(
                qa_pair['question'], 
                docs_for_qa, 
                top_k=1
            )
            
            if answers:
                best_answer = answers[0]
                print(f"   💡 Answer: {best_answer['answer']}")
                print(f"   📊 Confidence: {best_answer['confidence']:.1%}")
                print(f"   🔗 Combined Score: {best_answer['combined_score']:.3f}")
                
                # Show context snippet
                if best_answer.get('context_snippet'):
                    snippet = best_answer['context_snippet'][:200] + "..." if len(best_answer['context_snippet']) > 200 else best_answer['context_snippet']
                    print(f"   📝 Context: {snippet}")
            else:
                print("   ⚠️ No confident answer found")
        else:
            print("   ⚠️ No relevant documents found")
    
    print("\n🎉 ARQA Demo Complete!")
    print("=" * 60)
    print("✅ Successfully demonstrated:")
    print("   • HTML document processing and chunking")
    print("   • Arabic text retrieval using AraDPR")
    print("   • Multilingual question answering with XLM-RoBERTa")
    print("   • End-to-end Arabic Q&A pipeline")
    print("=" * 60)

if __name__ == "__main__":
    demo_arqa_system()
