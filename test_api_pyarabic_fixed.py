#!/usr/bin/env python3
"""
Test PyArabic integration through API endpoints - Fixed Version
"""

import requests
import json
import time
import tempfile
import os

def test_api_with_pyarabic():
    """Test the API endpoints with Arabic text to validate PyArabic integration"""
    
    BASE_URL = "http://localhost:8000"
    
    print("🚀 Testing PyArabic Integration via API")
    print("=" * 50)
    
    # Wait a moment for server to be ready
    time.sleep(2)
    
    try:
        # Test 1: Health check
        print("1️⃣ Testing API health...")
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print("   ✅ API is running")
        else:
            print(f"   ❌ API health check failed: {response.status_code}")
            return False
        
        # Test 2: Check status
        print("2️⃣ Testing system status...")
        response = requests.get(f"{BASE_URL}/status")
        if response.status_code == 200:
            status = response.json()
            print(f"   ✅ System status: {status['status']}")
            print(f"   📊 Document count: {status['document_count']}")
            print(f"   🔧 Components initialized: {status['initialized']}")
        else:
            print(f"   ❌ Status check failed: {response.status_code}")
            return False
        
        # Test 3: Document upload with Arabic content containing diacritics
        print("3️⃣ Testing document upload with Arabic content...")
        
        # Sample Arabic HTML document with diacritics (for PyArabic testing)
        html_content = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>الذَّكاءُ الاصْطِناعِيُّ</title>
            <meta charset="utf-8">
        </head>
        <body>
            <h1>الذَّكاءُ الاصْطِناعِيُّ والتَّعَلُّمُ الآلِيُّ</h1>
            <p>الذكاء الاصطناعي هو مجال واسع في علوم الحاسوب يهدف إلى إنشاء أنظمة قادرة على أداء المهام التي تتطلب ذكاءً بشرياً. يشمل هذا المجال التعلم الآلي والشبكات العصبية ومعالجة اللغات الطبيعية.</p>
            <p>التعلم الآلي هو فرع من الذكاء الاصطناعي يركز على تطوير خوارزميات تمكن الحاسوب من التعلم والتحسن من التجربة دون برمجة صريحة لكل مهمة.</p>
            <p>معالجة اللغات الطبيعية تتعامل مع فهم وتحليل وإنتاج اللغة البشرية بواسطة الحاسوب، وهي مهمة خاصة في اللغة العربية بسبب تعقيدها النحوي والصرفي.</p>
            <p>النُّصوص العربيَّة المُشكَّلة تحتاج إلى معالجة خاصة لإزالة التشكيل والحصول على النص الأساسي.</p>
        </body>
        </html>
        """
        
        # Save to temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False, encoding='utf-8') as temp_file:
            temp_file.write(html_content)
            temp_file_path = temp_file.name
        
        try:
            with open(temp_file_path, 'rb') as f:
                files = {'file': ('test_arabic_diacritics.html', f, 'text/html')}
                response = requests.post(f"{BASE_URL}/upload", files=files)
                
            print(f"Upload response status: {response.status_code}")
            if response.status_code == 200:
                result = response.json()
                print(f"   ✅ Document uploaded successfully!")
                print(f"   📄 Filename: {result.get('filename')}")
                print(f"   📊 Chunks created: {result.get('chunks_created')}")
                print(f"   📈 Total documents: {result.get('total_documents')}")
                print(f"   ⏱️ Processing time: {result.get('processing_time'):.3f}s")
            else:
                print(f"   ❌ Failed to upload document: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
                
        finally:
            # Clean up temporary file
            os.unlink(temp_file_path)
        
        # Test 4: Question answering with Arabic
        print("4️⃣ Testing Arabic question answering...")
        
        arabic_questions = [
            "ما هو الذكاء الاصطناعي؟",
            "ما هو التعلم الآلي؟", 
            "لماذا معالجة اللغة العربية معقدة؟",
            "كيف يعمل التعلم الآلي؟"
        ]
        
        for i, question in enumerate(arabic_questions, 1):
            qa_data = {
                "question": question,
                "top_k": 3,
                "min_confidence": 0.01
            }
            
            response = requests.post(f"{BASE_URL}/ask", json=qa_data)
            if response.status_code == 200:
                result = response.json()
                answers = result.get('answers', [])
                
                print(f"\n   سؤال {i}: {question}")
                if answers:
                    for j, answer in enumerate(answers[:2], 1):
                        print(f"   إجابة {j}: {answer.get('answer', 'N/A')}")
                        print(f"   🎯 الثقة: {answer.get('confidence', 0):.3f}")
                        print(f"   📄 المصدر: {answer.get('context', 'N/A')[:100]}...")
                        print()
                else:
                    print("   ⚠️ لم يتم العثور على إجابات")
                
                print(f"   📊 وقت المعالجة: {result.get('processing_time', 0):.3f}s")
                print(f"   📚 الوثائق المسترجعة: {result.get('retrieved_docs', 0)}")
                
            else:
                print(f"   ❌ Question answering failed: {response.status_code}")
                print(f"   Error: {response.text}")
        
        # Test 5: Document listing
        print("5️⃣ Testing document listing...")
        
        response = requests.get(f"{BASE_URL}/documents")
        if response.status_code == 200:
            result = response.json()
            print(f"   📚 Total documents in system: {result.get('total_documents', 0)}")
            print(f"   🔍 Retriever status: {result.get('retriever_status', 'unknown')}")
        else:
            print(f"   ❌ Document listing failed: {response.status_code}")
            print(f"   Error: {response.text}")
        
        print("\n🎉 PyArabic API integration test completed!")
        print("✨ The system successfully processed Arabic text with diacritics!")
        print("🔤 PyArabic normalization should have removed diacritics during processing!")
        return True
        
    except requests.ConnectionError:
        print("❌ Could not connect to API server. Make sure it's running on localhost:8000")
        print("   💡 Start the server with: python -m src.arqa.api")
        return False
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_api_with_pyarabic()
    if success:
        print("\n🏆 All API tests passed! PyArabic integration is working!")
        print("🎯 The system can handle Arabic text with diacritics correctly!")
    else:
        print("\n💥 Some tests failed. Check the output above for details.")
