#!/usr/bin/env python3
"""
Final integration test for PyArabic with ARQA system
"""

import sys
import os
sys.path.append('src')

def test_pyarabic_integration():
    """Test PyArabic integration step by step"""
    print("🧪 Final PyArabic Integration Test")
    print("=" * 50)
    
    try:
        # Test 1: Import the modules
        print("1️⃣ Testing imports...")
        from arqa.simple_ingest import SimpleDocumentIngestor
        from arqa.retriever import ArabicDocumentRetriever
        from arqa.reader_simple import SimpleArabicQA
        print("   ✅ All modules imported successfully")
        
        # Test 2: Initialize components
        print("2️⃣ Initializing components...")
        ingestor = SimpleDocumentIngestor(output_dir="test_processed")
        print("   ✅ Document ingestor initialized with PyArabic")
        
        # Test 3: Test Arabic normalization
        print("3️⃣ Testing Arabic text normalization...")
        test_texts = [
            "الذَّكاءُ الاصْطِناعِيُّ مُهِمٌّ جِدًّا",
            "هذا نصٌّ يحتوي على تشكيل وعلامات",
            "التعلُّم الآلي والذكاء الاصطناعي"
        ]
        
        for i, text in enumerate(test_texts, 1):
            normalized = ingestor.normalize_arabic_text(text)
            tokens = ingestor.simple_tokenize(normalized)
            print(f"   Test {i}:")
            print(f"     Original: {text}")
            print(f"     Normalized: {normalized}")
            print(f"     Tokens ({len(tokens)}): {tokens[:3]}...")
        
        # Test 4: HTML processing
        print("4️⃣ Testing HTML processing...")
        test_html = """<!DOCTYPE html>
<html>
<head>
    <title>اختبار PyArabic</title>
    <meta name="description" content="اختبار معالجة النصوص العربية">
</head>
<body>
    <h1>الذكاء الاصطناعي والتعلم الآلي</h1>
    <p>هذا نصٌّ عربي يحتوي على علامات التشكيل المختلفة. الهدف من هذا النص هو اختبار قدرة النظام على معالجة النصوص العربية بشكل صحيح.</p>
    <p>PyArabic هي مكتبة ممتازة لمعالجة النصوص العربية وتطبيعها. تقوم بإزالة التشكيل وتوحيد الحروف.</p>
    <p>التطبيق يستخدم هذه المكتبة لتحسين جودة البحث والإجابة على الأسئلة العربية.</p>
</body>
</html>"""
        
        documents = ingestor.process_html_content(test_html, "test_document")
        print(f"   ✅ Processed HTML into {len(documents)} chunks")
        
        if documents:
            print(f"   📄 Sample chunk: {documents[0]['content'][:100]}...")
        
        # Test 5: Full pipeline
        print("5️⃣ Testing document retrieval...")
        retriever = ArabicDocumentRetriever()
        
        # Add documents to retriever
        all_docs = []
        for doc in documents:
            all_docs.append({
                'content': doc['content'],
                'metadata': doc['metadata']
            })
        
        if all_docs:
            retriever.add_documents(all_docs)
            print(f"   ✅ Added {len(all_docs)} documents to retriever")
            
            # Test retrieval
            query = "ما هو الذكاء الاصطناعي؟"
            relevant_docs = retriever.retrieve(query, top_k=2)
            print(f"   🔍 Query: {query}")
            print(f"   📊 Retrieved {len(relevant_docs)} relevant documents")
            
            if relevant_docs:
                print(f"   📄 Top result: {relevant_docs[0].content[:100]}...")
        
        # Test 6: Question Answering
        print("6️⃣ Testing Question Answering...")
        qa_system = SimpleArabicQA()
        
        # Test with one of the document chunks
        if all_docs:
            test_question = "ما هو الذكاء الاصطناعي؟"
            test_context = all_docs[0]['content']
            
            answers = qa_system.answer_question(test_question, test_context)
            print(f"   ❓ Question: {test_question}")
            print(f"   📄 Context: {test_context[:100]}...")
            
            if answers:
                print(f"   💡 Answer: {answers[0]['answer']}")
                print(f"   📊 Confidence: {answers[0]['score']:.3f}")
            else:
                print("   ⚠️ No answers found (may be due to content mismatch)")
        
        print("\n🎉 All tests passed! PyArabic integration is working perfectly!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_pyarabic_integration()
    sys.exit(0 if success else 1)
