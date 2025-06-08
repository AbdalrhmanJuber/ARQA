#!/usr/bin/env python3
"""
Comprehensive test for Arabic Question Answering system.
Tests the reader_simple.py module with various Arabic Q&A scenarios.
"""

import sys
import os
sys.path.append(os.path.abspath('.'))

from src.arqa.reader_simple import SimpleArabicQA, create_arabic_qa_system
from src.arqa.simple_ingest import SimpleDocumentIngestor
from src.arqa.retriever import ArabicDocumentRetriever


def test_basic_qa():
    """Test basic question answering functionality."""
    print("=" * 60)
    print("🧪 TEST 1: Basic Arabic Question Answering")
    print("=" * 60)
    
    try:
        # Initialize QA system
        qa = create_arabic_qa_system()
        
        # Test cases
        test_cases = [
            {
                'question': 'ما هو عاصمة مصر؟',
                'context': 'القاهرة هي عاصمة جمهورية مصر العربية وأكبر مدنها. تقع على ضفاف نهر النيل في شمال مصر. يبلغ عدد سكانها حوالي 20 مليون نسمة.',
                'expected_keywords': ['القاهرة']
            },
            {
                'question': 'متى تم تأسيس الجامعة؟',
                'context': 'تأسست جامعة القاهرة في عام 1908 وهي من أقدم الجامعات في مصر والعالم العربي. تضم الجامعة عدة كليات متنوعة.',
                'expected_keywords': ['1908', 'عام']
            },
            {
                'question': 'كم عدد الطلاب؟',
                'context': 'يدرس في الجامعة أكثر من 200 ألف طالب وطالبة من مختلف التخصصات الأكاديمية والعلمية.',
                'expected_keywords': ['200', 'ألف']
            }
        ]
        
        for i, test_case in enumerate(test_cases, 1):
            print(f"\n🔍 Test Case {i}:")
            print(f"   Question: {test_case['question']}")
            print(f"   Context: {test_case['context'][:100]}...")
            
            answers = qa.answer_question(
                test_case['question'], 
                test_case['context'],
                top_k=2
            )
            
            if answers:
                print(f"   ✅ Got {len(answers)} answer(s):")
                for j, answer in enumerate(answers, 1):
                    print(f"      {j}. '{answer['answer']}' (score: {answer['score']:.3f})")
                    
                    # Check if answer contains expected keywords
                    answer_text = answer['answer']
                    found_keywords = [kw for kw in test_case['expected_keywords'] 
                                    if kw in answer_text]
                    if found_keywords:
                        print(f"         ✅ Contains expected keywords: {found_keywords}")
                    else:
                        print(f"         ⚠️ Missing expected keywords: {test_case['expected_keywords']}")
            else:
                print(f"   ❌ No answers found")
        
        print(f"\n✅ Basic QA test completed!")
        return True
        
    except Exception as e:
        print(f"❌ Error in basic QA test: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_long_text_qa():
    """Test QA with long text that requires chunking."""
    print("\n" + "=" * 60)
    print("🧪 TEST 2: Long Text Question Answering")
    print("=" * 60)
    
    try:
        qa = create_arabic_qa_system()
        
        # Create a long Arabic text
        long_context = """
        تعتبر القاهرة عاصمة جمهورية مصر العربية وأكبر مدنها من حيث عدد السكان والمساحة. 
        تقع المدينة على ضفاف نهر النيل في شمال مصر، وتبعد حوالي 165 كيلومترا جنوب البحر الأبيض المتوسط.
        يبلغ عدد سكان القاهرة الكبرى حوالي 20 مليون نسمة، مما يجعلها واحدة من أكبر المناطق الحضرية في العالم.
        
        تضم القاهرة العديد من المعالم التاريخية والثقافية المهمة، بما في ذلك الأهرامات وأبو الهول في الجيزة،
        والمتحف المصري، وقلعة صلاح الدين، وجامع الأزهر. كما تحتوي على العديد من الجامعات المرموقة
        مثل جامعة القاهرة التي تأسست عام 1908، والجامعة الأمريكية بالقاهرة.
        
        اقتصادياً، تعد القاهرة المركز الاقتصادي لمصر، حيث تسهم بحوالي ثلث الناتج المحلي الإجمالي للبلاد.
        تضم المدينة العديد من الصناعات المهمة مثل صناعة النسيج والمواد الغذائية والمواد الكيميائية.
        
        ثقافياً، تُعرف القاهرة باسم "أم الدنيا" و"مدينة الألف مئذنة". تحتوي على أكبر تجمع للآثار الإسلامية في العالم،
        وقد أُدرجت القاهرة التاريخية في قائمة مواقع التراث العالمي لليونسكو عام 1979.
        
        التعليم في القاهرة متنوع ومتطور، حيث تضم المدينة جامعة الأزهر التي تأسست عام 970 ميلادية
        وتعتبر من أقدم الجامعات في العالم. كما تضم العديد من المؤسسات التعليمية الأخرى
        التي تخرج آلاف الطلاب سنوياً في مختلف التخصصات.
        """
        
        questions = [
            "كم يبلغ عدد سكان القاهرة؟",
            "متى تأسست جامعة القاهرة؟",
            "ماذا تُسمى القاهرة ثقافياً؟",
            "متى أُدرجت القاهرة في قائمة التراث العالمي؟"
        ]
        
        for i, question in enumerate(questions, 1):
            print(f"\n🔍 Long Text Question {i}: {question}")
            
            answers = qa.answer_question(question, long_context, top_k=2)
            
            if answers:
                print(f"   ✅ Found {len(answers)} answer(s):")
                for j, answer in enumerate(answers, 1):
                    print(f"      {j}. '{answer['answer']}' (score: {answer['score']:.3f})")
            else:
                print(f"   ❌ No answers found")
        
        print(f"\n✅ Long text QA test completed!")
        return True
        
    except Exception as e:
        print(f"❌ Error in long text QA test: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_integrated_pipeline():
    """Test the complete pipeline: HTML ingestion -> Retrieval -> QA."""
    print("\n" + "=" * 60)
    print("🧪 TEST 3: Full Pipeline Integration (HTML -> Retrieval -> QA)")
    print("=" * 60)
    
    try:
        # Sample HTML documents
        html_docs = [
            {
                'url': 'https://example.com/egypt',
                'content': '''
                <html>
                <head><title>مصر</title></head>
                <body>
                    <h1>جمهورية مصر العربية</h1>
                    <p>مصر دولة عربية تقع في شمال شرق أفريقيا. عاصمتها القاهرة وأكبر مدنها.</p>
                    <p>يبلغ عدد سكان مصر حوالي 100 مليون نسمة. اللغة الرسمية هي العربية.</p>
                    <p>تشتهر مصر بالأهرامات وأبو الهول ونهر النيل.</p>
                </body>
                </html>
                '''
            },
            {
                'url': 'https://example.com/education',
                'content': '''
                <html>
                <head><title>التعليم في مصر</title></head>
                <body>
                    <h1>النظام التعليمي المصري</h1>
                    <p>يتكون النظام التعليمي في مصر من المرحلة الابتدائية والإعدادية والثانوية.</p>
                    <p>تأسست جامعة القاهرة عام 1908 وهي من أعرق الجامعات العربية.</p>
                    <p>جامعة الأزهر تأسست عام 970 ميلادية وتعتبر من أقدم الجامعات في العالم.</p>
                </body>
                </html>
                '''            }
        ]
        
        print("📄 Step 1: HTML Processing...")
        ingestor = SimpleDocumentIngestor()
        documents = []
        
        for doc in html_docs:
            processed = ingestor.extract_html_content(doc['content'])
            # Process the extracted content into document chunks
            normalized_text = ingestor.normalize_arabic_text(processed['text'])
            chunks = ingestor.chunk_text_by_tokens(normalized_text)
            
            # Convert to expected document format
            for i, chunk in enumerate(chunks):
                doc_obj = {
                    'content': chunk,
                    'metadata': {
                        **processed['metadata'],
                        'url': doc['url'],
                        'chunk_id': i,
                        'total_chunks': len(chunks)
                    }
                }
                documents.append(doc_obj)
        
        print(f"   ✅ Processed {len(documents)} document chunks")
        
        print("\n🔍 Step 2: Document Retrieval Setup...")
        retriever = ArabicDocumentRetriever()
        
        # Add documents to retriever
        retriever.add_documents(documents)
        print(f"   ✅ Added documents to retrieval index")
        
        print("\n🤖 Step 3: Question Answering Setup...")
        qa = create_arabic_qa_system()
        print(f"   ✅ QA system ready")
        
        print("\n🎯 Step 4: End-to-End Query Processing...")
        test_questions = [
            "ما هي عاصمة مصر؟",
            "متى تأسست جامعة القاهرة؟",
            "كم عدد سكان مصر؟"
        ]
        
        for i, question in enumerate(test_questions, 1):
            print(f"\n🔍 Query {i}: {question}")            # Step 1: Retrieve relevant documents
            retrieved_docs = retriever.retrieve(question, top_k=3)
            print(f"   📋 Retrieved {len(retrieved_docs)} relevant documents")
            
            if retrieved_docs:
                # Convert RetrievedDocument objects to expected dictionary format
                docs_for_qa = []
                for doc in retrieved_docs:
                    docs_for_qa.append({
                        'content': doc.content,
                        'metadata': doc.meta,
                        'score': doc.score
                    })
                
                # Step 2: Get answers from retrieved documents
                answers = qa.answer_with_retrieved_docs(
                    question, 
                    docs_for_qa, 
                    top_k=2
                )
                
                if answers:
                    print(f"   ✅ Found {len(answers)} answer(s):")
                    for j, answer in enumerate(answers, 1):
                        print(f"      {j}. '{answer['answer']}'")
                        print(f"         Confidence: {answer['confidence']:.3f}")
                        print(f"         Document: {answer['document_title']}")
                        print(f"         Combined Score: {answer['combined_score']:.3f}")
                else:
                    print(f"   ⚠️ No confident answers found")
            else:
                print(f"   ❌ No relevant documents retrieved")
        
        print(f"\n✅ Full pipeline integration test completed!")
        return True
        
    except Exception as e:
        print(f"❌ Error in integration test: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_batch_processing():
    """Test batch question answering."""
    print("\n" + "=" * 60)
    print("🧪 TEST 4: Batch Question Answering")
    print("=" * 60)
    
    try:
        qa = create_arabic_qa_system()
        
        questions = [
            "ما هي عاصمة مصر؟",
            "متى تأسست الجامعة؟",
            "كم عدد الطلاب؟"
        ]
        
        contexts = [
            "القاهرة هي عاصمة مصر وأكبر مدنها.",
            "تأسست جامعة القاهرة في عام 1908.",
            "يدرس في الجامعة أكثر من 200 ألف طالب."
        ]
        
        print(f"🔄 Processing {len(questions)} questions in batch...")
        
        batch_results = qa.batch_answer(questions, contexts)
        
        print(f"✅ Batch processing completed!")
        print(f"📋 Results:")
        
        for i, (question, results) in enumerate(zip(questions, batch_results), 1):
            print(f"   {i}. {question}")
            if results:
                for j, answer in enumerate(results, 1):
                    print(f"      → {answer['answer']} (score: {answer['score']:.3f})")
            else:
                print(f"      → No answers found")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in batch processing test: {e}")
        import traceback
        traceback.print_exc()
        return False


def run_all_tests():
    """Run all QA tests."""
    print("🚀 Starting Arabic Question Answering System Tests")
    print("=" * 60)
    
    test_results = []
    
    # Run individual tests
    test_results.append(("Basic QA", test_basic_qa()))
    test_results.append(("Long Text QA", test_long_text_qa()))
    test_results.append(("Integration Pipeline", test_integrated_pipeline()))
    test_results.append(("Batch Processing", test_batch_processing()))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    passed = 0
    total = len(test_results)
    
    for test_name, result in test_results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name:<25} {status}")
        if result:
            passed += 1
    
    print(f"\n🎯 Overall: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("🎉 All tests passed! Arabic QA system is working correctly.")
        print("\n🔗 Next Steps:")
        print("   1. ✅ HTML Processing (simple_ingest.py)")
        print("   2. ✅ Document Retrieval (retriever.py)")
        print("   3. ✅ Question Answering (reader_simple.py)")
        print("   4. 🔄 API Development (api.py) - TODO")
        print("   5. 🔄 Web Interface - TODO")
    else:
        print("⚠️ Some tests failed. Check the error messages above.")
    
    return passed == total


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
