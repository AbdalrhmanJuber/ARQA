#!/usr/bin/env python3
"""
Detailed Arabic QA Test for ARQA API
Tests the complete Arabic question answering pipeline
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_arabic_qa():
    print("🧪 DETAILED ARABIC QA TEST")
    print("=" * 50)
    
    # Step 1: Check system status
    print("1️⃣ Checking system status...")
    status_response = requests.get(f"{BASE_URL}/status")
    if status_response.status_code == 200:
        status_data = status_response.json()
        print(f"   ✅ System initialized: {status_data.get('initialized')}")
        print(f"   📄 Document count: {status_data.get('document_count')}")
    else:
        print("   ❌ Failed to get system status")
        return
    
    # Step 2: Upload Arabic content if needed
    if status_data.get('document_count', 0) == 0:
        print("\n2️⃣ Uploading test document...")
        test_file = "test_html_articles/arabic_science.html"
        try:
            with open(test_file, 'rb') as f:
                files = {'file': ('arabic_science.html', f, 'text/html')}
                upload_response = requests.post(f"{BASE_URL}/upload", files=files)
                
            if upload_response.status_code == 200:
                upload_data = upload_response.json()
                print(f"   ✅ Uploaded successfully!")
                print(f"   📄 Chunks created: {upload_data.get('chunks_created')}")
                print(f"   🕒 Processing time: {upload_data.get('processing_time'):.2f}s")
            else:
                print(f"   ❌ Upload failed: {upload_response.text}")
                return
        except FileNotFoundError:
            print(f"   ⚠️  Test file {test_file} not found, using existing documents")
    
    # Step 3: Test Arabic questions
    print("\n3️⃣ Testing Arabic Questions...")
    
    arabic_questions = [
        {
            "question": "ما هو الذكاء الاصطناعي؟",
            "description": "What is artificial intelligence?"
        },
        {
            "question": "كيف يعمل التعلم الآلي؟", 
            "description": "How does machine learning work?"
        },
        {
            "question": "ما هي فوائد التكنولوجيا؟",
            "description": "What are the benefits of technology?"
        }
    ]
    
    for i, q in enumerate(arabic_questions, 1):
        print(f"\n   Question {i}: {q['question']}")
        print(f"   (English: {q['description']})")
        
        question_data = {
            "question": q["question"],
            "top_k": 3,
            "min_confidence": 0.01
        }
        
        qa_response = requests.post(
            f"{BASE_URL}/ask", 
            json=question_data,
            headers={"Content-Type": "application/json"}
        )
        
        if qa_response.status_code == 200:
            qa_data = qa_response.json()
            print(f"   ✅ Answer received!")
            print(f"   🕒 Processing time: {qa_data.get('processing_time', 0):.2f}s")
            print(f"   📄 Retrieved docs: {qa_data.get('retrieved_docs', 0)}")
            
            # Show top answer
            answers = qa_data.get('answers', [])
            if answers:
                top_answer = answers[0]
                print(f"   🎯 Top Answer (confidence: {top_answer.get('confidence', 0):.3f}):")
                print(f"      {top_answer.get('answer', 'No answer')[:100]}...")
            else:
                print("   ⚠️  No answers found")
        else:
            print(f"   ❌ QA failed: {qa_response.text}")
    
    # Step 4: Check documents
    print(f"\n4️⃣ Checking final document count...")
    docs_response = requests.get(f"{BASE_URL}/documents")
    if docs_response.status_code == 200:
        docs_data = docs_response.json()
        print(f"   📄 Total documents: {docs_data.get('document_count')}")
        print(f"   📊 Recent documents: {len(docs_data.get('recent_documents', []))}")
    
    print("\n🎉 Arabic QA Test Complete!")

if __name__ == "__main__":
    test_arabic_qa()
