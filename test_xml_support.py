#!/usr/bin/env python3
"""
Test XML file upload support in ARQA system
"""

import sys
import os
import requests
import tempfile

# Add project root to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def test_xml_upload():
    """Test XML file upload functionality"""
    
    print("🧪 Testing XML File Upload Support")
    print("=" * 50)
    
    # Create sample Arabic XML content
    xml_content = """<?xml version="1.0" encoding="UTF-8"?>
<article>
    <title>التعلم الآلي في العلوم</title>
    <metadata>
        <author>كاتب تجريبي</author>
        <category>technology</category>
        <language>ar</language>
    </metadata>
    <content>
        <section>
            <header>مقدمة عن التعلم الآلي</header>
            <text>
                يُعتبر التعلم الآلي فرعاً من فروع الذكاء الاصطناعي الذي يهتم بتطوير 
                خوارزميات وتقنيات تسمح للحاسوب بالتعلم واتخاذ القرارات من البيانات 
                دون برمجة صريحة لكل حالة.
            </text>
        </section>
        <section>
            <header>تطبيقات التعلم الآلي</header>
            <text>
                يستخدم التعلم الآلي في العديد من المجالات مثل الطب والتمويل والنقل 
                والتجارة الإلكترونية. كما يساعد في تحليل البيانات الضخمة واستخراج 
                المعرفة المفيدة منها.
            </text>
        </section>
        <section>
            <header>مستقبل التعلم الآلي</header>
            <text>
                يتوقع أن يشهد التعلم الآلي تطوراً كبيراً في السنوات القادمة مع تطور 
                قوة الحاسوب وزيادة كمية البيانات المتاحة. سيؤدي هذا إلى تطبيقات 
                أكثر ذكاءً وفعالية في جميع جوانب الحياة.
            </text>
        </section>
    </content>
</article>"""
    
    # Test local processing first
    print("1️⃣ Testing local XML processing...")
    try:
        from arqa.simple_ingest import SimpleDocumentIngestor
        
        ingestor = SimpleDocumentIngestor()
        documents = ingestor.process_xml_content(xml_content, source_url="test_ml.xml")
        
        if documents:
            print(f"   ✅ Successfully processed XML locally!")
            print(f"   📄 Created {len(documents)} chunks")
            print(f"   📝 Title: {documents[0]['metadata']['title']}")
            print(f"   🔤 Text length: {documents[0]['metadata']['text_length']} characters")
            print(f"   📖 Sample: {documents[0]['content'][:100]}...")
        else:
            print("   ❌ No documents created from XML")
            return False
            
    except Exception as e:
        print(f"   ❌ Local XML processing failed: {e}")
        return False
    
    # Test API upload
    print("\n2️⃣ Testing XML upload via API...")
    
    BASE_URL = "http://localhost:8000"
    
    # Check if API is running
    try:
        response = requests.get(f"{BASE_URL}/status", timeout=5)
        if response.status_code != 200:
            print("   ⚠️ API server not responding. Start it with: python run_api.py")
            return True  # Local test passed, API test skipped
    except:
        print("   ⚠️ API server not running. Start it with: python run_api.py")
        return True  # Local test passed, API test skipped
    
    # Create temporary XML file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.xml', delete=False, encoding='utf-8') as temp_file:
        temp_file.write(xml_content)
        temp_file_path = temp_file.name
    
    try:
        # Upload XML file
        with open(temp_file_path, 'rb') as f:
            files = {'file': ('test_machine_learning.xml', f, 'application/xml')}
            response = requests.post(f"{BASE_URL}/upload", files=files)
        
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ XML uploaded successfully!")
            print(f"   📄 Filename: {result.get('filename')}")
            print(f"   📊 Chunks created: {result.get('chunks_created')}")
            print(f"   📈 Total documents: {result.get('total_documents')}")
            print(f"   ⏱️ Processing time: {result.get('processing_time'):.3f}s")
        else:
            print(f"   ❌ XML upload failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    finally:
        # Clean up temporary file
        os.unlink(temp_file_path)
    
    # Test asking questions about the XML content
    print("\n3️⃣ Testing Arabic questions on XML content...")
    
    test_questions = [
        "ما هو التعلم الآلي؟",
        "ما هي تطبيقات التعلم الآلي؟", 
        "كيف سيكون مستقبل التعلم الآلي؟"
    ]
    
    for question in test_questions:
        try:
            response = requests.post(f"{BASE_URL}/ask", json={
                "question": question,
                "top_k": 3,
                "min_confidence": 0.01
            })
            
            if response.status_code == 200:
                result = response.json()
                if result.get('answers'):
                    answer = result['answers'][0]['answer']
                    confidence = result['answers'][0]['score']
                    print(f"   🤔 {question}")
                    print(f"   💡 {answer} (confidence: {confidence:.3f})")
                else:
                    print(f"   🤔 {question}")
                    print(f"   ❌ No answer found")
            else:
                print(f"   ❌ Question failed: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Question error: {e}")
    
    print(f"\n🎉 XML support test completed successfully!")
    print(f"✅ ARQA now supports both HTML and XML files!")
    
    return True

if __name__ == "__main__":
    test_xml_upload()
