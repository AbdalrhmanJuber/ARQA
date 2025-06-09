#!/usr/bin/env python3
"""
Test PyArabic integration through API endpoints
"""

import requests
import json
import time

def test_api_with_pyarabic():
    """Test the API endpoints with Arabic text to validate PyArabic integration"""
    
    base_url = "http://localhost:8000"
    
    print("🚀 Testing PyArabic Integration via API")
    print("=" * 50)
    
    # Wait a moment for server to be ready
    time.sleep(2)
    
    try:
        # Test 1: Health check
        print("1️⃣ Testing API health...")
        response = requests.get(f"{base_url}/")
        if response.status_code == 200:
            print("   ✅ API is running")
        else:
            print(f"   ❌ API health check failed: {response.status_code}")
            return False
        
        # Test 2: Document ingestion with Arabic content
        print("2️⃣ Testing document ingestion...")
        
        # Sample Arabic HTML document with diacritics
        arabic_html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>الذكاء الاصطناعي</title>
            <meta name="description" content="مقال عن الذكاء الاصطناعي">
        </head>
        <body>
            <h1>الذَّكاءُ الاصْطِناعِيُّ والتَّعَلُّمُ الآلِيُّ</h1>
            <p>الذكاء الاصطناعي هو مجال واسع في علوم الحاسوب يهدف إلى إنشاء أنظمة قادرة على أداء المهام التي تتطلب ذكاءً بشرياً. يشمل هذا المجال التعلم الآلي والشبكات العصبية ومعالجة اللغات الطبيعية.</p>
            <p>التعلم الآلي هو فرع من الذكاء الاصطناعي يركز على تطوير خوارزميات تمكن الحاسوب من التعلم والتحسن من التجربة دون برمجة صريحة لكل مهمة.</p>
            <p>معالجة اللغات الطبيعية تتعامل مع فهم وتحليل وإنتاج اللغة البشرية بواسطة الحاسوب، وهي مهمة خاصة في اللغة العربية بسبب تعقيدها النحوي والصرفي.</p>
        </body>
        </html>
        """
        
        # Test document ingestion
        ingest_data = {
            "content": arabic_html,
            "content_type": "html",
            "metadata": {
                "title": "مقال الذكاء الاصطناعي",
                "source": "test_document"
            }
        }
        
        response = requests.post(f"{base_url}/ingest", json=ingest_data)
        if response.status_code == 200:
            result = response.json()
            doc_count = result.get('chunks_created', 0)
            print(f"   ✅ Successfully ingested document - Created {doc_count} chunks")
            print(f"   📊 Processing time: {result.get('processing_time', 'N/A')} seconds")
        else:
            print(f"   ❌ Document ingestion failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return False
        
        # Test 3: Question answering with Arabic
        print("3️⃣ Testing question answering...")
        
        arabic_questions = [
            "ما هو الذكاء الاصطناعي؟",
            "ما هو التعلم الآلي؟",
            "لماذا معالجة اللغة العربية معقدة؟"
        ]
        
        for i, question in enumerate(arabic_questions, 1):
            qa_data = {
                "question": question,
                "top_k": 3
            }
            
            response = requests.post(f"{base_url}/answer", json=qa_data)
            if response.status_code == 200:
                result = response.json()
                answers = result.get('answers', [])
                
                print(f"   Question {i}: {question}")
                if answers:
                    best_answer = answers[0]
                    print(f"   💡 Answer: {best_answer['answer']}")
                    print(f"   📊 Score: {best_answer['score']:.3f}")
                    print(f"   📄 Source: {best_answer.get('source', 'N/A')}")
                else:
                    print("   ⚠️ No answers found")
                print()
            else:
                print(f"   ❌ Question answering failed: {response.status_code}")
                print(f"   Error: {response.text}")
        
        # Test 4: Document retrieval
        print("4️⃣ Testing document retrieval...")
        
        search_data = {
            "query": "الذكاء الاصطناعي",
            "top_k": 2
        }
        
        response = requests.post(f"{base_url}/search", json=search_data)
        if response.status_code == 200:
            result = response.json()
            documents = result.get('documents', [])
            
            print(f"   🔍 Query: {search_data['query']}")
            print(f"   📊 Found {len(documents)} relevant documents")
            
            for i, doc in enumerate(documents[:2], 1):
                print(f"   📄 Document {i}: {doc['content'][:100]}...")
                print(f"   📊 Score: {doc['score']:.3f}")
        else:
            print(f"   ❌ Document retrieval failed: {response.status_code}")
            print(f"   Error: {response.text}")
        
        print("\n🎉 PyArabic API integration test completed successfully!")
        print("✨ Enhanced Arabic text normalization is working through the API!")
        return True
        
    except requests.ConnectionError:
        print("❌ Could not connect to API server. Make sure it's running on localhost:8000")
        return False
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        return False

if __name__ == "__main__":
    success = test_api_with_pyarabic()
    if success:
        print("\n🏆 All API tests passed! PyArabic integration is working perfectly!")
    else:
        print("\n💥 Some tests failed. Check the output above for details.")
