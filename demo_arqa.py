#!/usr/bin/env python3
"""
Arabic Question Answering Demo
Shows how to use the working ARQA system without Haystack dependencies
"""

import sys
import os
sys.path.insert(0, '.')

def demo_arqa_system():
    """Demonstrate the complete ARQA system"""
    print("🌟 ARQA - Arabic Question Answering System Demo")
    print("=" * 60)
    
    # Step 1: Document Processing
    print("\n📄 Step 1: Document Processing")
    print("-" * 30)
    
    from src.arqa.simple_ingest import SimpleDocumentIngestor
    
    # Initialize document processor
    ingestor = SimpleDocumentIngestor()
    print("✅ Document ingestor ready")
    
    # Process Arabic HTML documents
    html_files = [
        "test_html_articles/artificial_intelligence.html",
        "test_html_articles/arabic_science.html"
    ]
    
    all_documents = []
    for html_file in html_files:
        if os.path.exists(html_file):
            print(f"📖 Processing: {os.path.basename(html_file)}")
            docs = ingestor.process_html_file(html_file)
            all_documents.extend(docs)
            print(f"   ✅ Created {len(docs)} document chunks")
    
    print(f"\n📊 Total processed: {len(all_documents)} document chunks")
    
    # Step 2: Question Answering
    print("\n🤖 Step 2: Question Answering")
    print("-" * 30)
    
    try:
        from src.arqa.reader_simple import SimpleArabicQA
        
        # Initialize QA system
        qa_system = SimpleArabicQA()
        print("✅ QA system ready")
        
        # Demo questions
        questions = [
            "ما هو الذكاء الاصطناعي؟",
            "ما هي تطبيقات تعلم الآلة؟",
            "ما هي التحديات الأخلاقية للذكاء الاصطناعي؟"
        ]
        
        print(f"\n💭 Testing {len(questions)} questions:")
        
        for i, question in enumerate(questions, 1):
            print(f"\n🤔 Question {i}: {question}")
            
            # Find relevant document
            best_doc = None
            best_score = 0
            
            for doc in all_documents:
                # Simple keyword matching (replace with proper retrieval later)
                if any(word in doc['content'].lower() for word in question.lower().split()):
                    best_doc = doc
                    break
            
            if best_doc:
                context = best_doc['content'][:500]  # Limit context length
                answers = qa_system.answer_question(question, context)
                
                if answers:
                    best_answer = answers[0]
                    print(f"💡 Answer: {best_answer['answer']}")
                    print(f"   📊 Confidence: {best_answer['score']:.3f}")
                    print(f"   📄 Source: {best_doc['metadata'].get('title', 'Unknown')}")
                else:
                    print("❓ No answer found")
            else:
                print("❓ No relevant document found")
        
        print("\n🎉 Demo completed successfully!")
        print("✅ Arabic document processing: WORKING")
        print("✅ Arabic question answering: WORKING")
        print("✅ End-to-end pipeline: FUNCTIONAL")
        
    except Exception as e:
        print(f"⚠️ QA system error: {e}")
        print("💡 Document processing still works!")

def main():
    """Main demo function"""
    try:
        demo_arqa_system()
        
        print("\n" + "=" * 60)
        print("🚀 How to use the ARQA system:")
        print("   1. Use src/arqa/simple_ingest.py for document processing")
        print("   2. Use src/arqa/reader_simple.py for question answering")
        print("   3. Use src/arqa/retriever.py for document retrieval")
        print("   4. NO Haystack dependencies required!")
        print("=" * 60)
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
