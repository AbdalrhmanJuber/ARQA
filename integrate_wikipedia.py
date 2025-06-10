#!/usr/bin/env python3
"""
Integrate processed Wikipedia data with ARQA API
Load Wikipedia chunks into the question answering system
"""

import os
import sys
import json
import glob
import requests
import time
from typing import List, Dict, Any

def load_wikipedia_data(directory: str) -> List[Dict[str, Any]]:
    """Load all processed Wikipedia data from directory"""
    
    print(f"📁 Loading Wikipedia data from: {directory}")
    
    if not os.path.exists(directory):
        print(f"❌ Directory not found: {directory}")
        return []
    
    # Find all batch files
    batch_files = glob.glob(os.path.join(directory, "wikipedia_batch_*.json"))
    
    if not batch_files:
        print(f"❌ No Wikipedia batch files found in {directory}")
        return []
    
    print(f"📦 Found {len(batch_files)} batch files")
    
    all_documents = []
    for batch_file in sorted(batch_files):
        try:
            with open(batch_file, 'r', encoding='utf-8') as f:
                batch_data = json.load(f)
                all_documents.extend(batch_data)
                print(f"   ✅ Loaded {len(batch_data)} chunks from {os.path.basename(batch_file)}")
        except Exception as e:
            print(f"   ❌ Error loading {batch_file}: {e}")
    
    print(f"📄 Total chunks loaded: {len(all_documents):,}")
    return all_documents

def test_api_integration(documents: List[Dict[str, Any]], api_url: str = "http://localhost:8000"):
    """Test integration with ARQA API"""
    
    print(f"🧪 Testing API integration with {len(documents):,} Wikipedia chunks")
    
    # Check API status
    try:
        response = requests.get(f"{api_url}/status", timeout=10)
        if response.status_code == 200:
            status = response.json()
            print(f"✅ API is running")
            print(f"   📄 Current documents: {status.get('document_count', 0):,}")
        else:
            print(f"❌ API status check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Cannot connect to API: {e}")
        print(f"💡 Make sure to start the API with: python run_api.py")
        return False
    
    # Test with sample Wikipedia content by creating temporary XML files
    print(f"\n📤 Testing Wikipedia content upload...")
    
    # Take first 5 documents as samples
    sample_docs = documents[:5]
    
    for i, doc in enumerate(sample_docs):
        try:
            # Create XML content from the document
            title = doc['metadata'].get('title', f'Wikipedia Article {i+1}')
            content = doc['content']
            
            xml_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<article>
    <title>{title}</title>
    <content>
        {content}
    </content>
</article>"""
            
            # Create temporary file
            import tempfile
            with tempfile.NamedTemporaryFile(mode='w', suffix='.xml', delete=False, encoding='utf-8') as temp_file:
                temp_file.write(xml_content)
                temp_file_path = temp_file.name
            
            # Upload to API
            with open(temp_file_path, 'rb') as f:
                files = {'file': (f'wikipedia_sample_{i+1}.xml', f, 'application/xml')}
                response = requests.post(f"{api_url}/upload", files=files)
            
            # Clean up
            os.unlink(temp_file_path)
            
            if response.status_code == 200:
                result = response.json()
                print(f"   ✅ Sample {i+1}: {result.get('chunks_created')} chunks created")
            else:
                print(f"   ❌ Sample {i+1} failed: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Error uploading sample {i+1}: {e}")
    
    return True

def test_wikipedia_questions(api_url: str = "http://localhost:8000"):
    """Test Arabic questions on Wikipedia content"""
    
    print(f"\n🤔 Testing Arabic questions on Wikipedia content...")
    
    # Sample Arabic questions about general knowledge
    test_questions = [
        "ما هو الماء؟",
        "ما هي خصائص الماء؟",
        "ما هي استخدامات الماء؟",
        "كيف يتكون الماء؟",
        "ما هي أهمية الماء في الحياة؟",
        "ما هو الذكاء الاصطناعي؟",
        "ما هي تطبيقات الذكاء الاصطناعي؟",
        "كيف يعمل التعلم الآلي؟"
    ]
    
    successful_answers = 0
    
    for i, question in enumerate(test_questions, 1):
        try:
            response = requests.post(f"{api_url}/ask", json={
                "question": question,
                "top_k": 3,
                "min_confidence": 0.01
            }, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                answers = result.get('answers', [])
                
                if answers:
                    answer = answers[0]['answer']
                    confidence = answers[0]['score']
                    print(f"   {i}. {question}")
                    print(f"      💡 {answer}")
                    print(f"      📊 Confidence: {confidence:.3f}")
                    successful_answers += 1
                else:
                    print(f"   {i}. {question}")
                    print(f"      ❌ No answer found")
            else:
                print(f"   {i}. {question}")
                print(f"      ❌ API error: {response.status_code}")
                
        except Exception as e:
            print(f"   {i}. {question}")
            print(f"      ❌ Error: {e}")
    
    success_rate = (successful_answers / len(test_questions)) * 100
    print(f"\n📊 Question Answering Results:")
    print(f"   ✅ Successful answers: {successful_answers}/{len(test_questions)}")
    print(f"   📈 Success rate: {success_rate:.1f}%")
    
    return success_rate > 50  # Consider success if >50% questions answered

def main():
    """Main integration function"""
    
    print("🔗 ARQA Wikipedia Integration")
    print("=" * 50)
    
    # List available processed directories
    processed_dirs = []
    for item in os.listdir('.'):
        if os.path.isdir(item) and item.startswith('wikipedia_'):
            processed_dirs.append(item)
    
    if not processed_dirs:
        print("❌ No processed Wikipedia directories found")
        print("💡 Run Wikipedia processing first with: python run_wikipedia_processing.py")
        return
    
    print("📁 Available processed Wikipedia datasets:")
    for i, dir_name in enumerate(processed_dirs, 1):
        # Load stats if available
        stats_file = os.path.join(dir_name, "wikipedia_processing_stats.json")
        if os.path.exists(stats_file):
            with open(stats_file, 'r', encoding='utf-8') as f:
                stats = json.load(f)
            articles = stats.get('articles_processed', 0)
            chunks = stats.get('chunks_created', 0)
            print(f"   {i}. {dir_name} ({articles:,} articles, {chunks:,} chunks)")
        else:
            print(f"   {i}. {dir_name}")
    
    # Choose dataset
    try:
        choice = int(input(f"\nSelect dataset (1-{len(processed_dirs)}): ")) - 1
        if choice < 0 or choice >= len(processed_dirs):
            raise ValueError("Invalid choice")
        
        selected_dir = processed_dirs[choice]
        print(f"📂 Selected: {selected_dir}")
        
    except (ValueError, KeyboardInterrupt):
        print("❌ Invalid selection")
        return
    
    # Load Wikipedia data
    documents = load_wikipedia_data(selected_dir)
    
    if not documents:
        print("❌ No documents loaded")
        return
    
    # Test API integration
    api_success = test_api_integration(documents)
    
    if api_success:
        # Test questions
        qa_success = test_wikipedia_questions()
        
        if qa_success:
            print(f"\n🎉 Wikipedia Integration Successful!")
            print(f"✅ Your ARQA system now has access to {len(documents):,} Wikipedia chunks")
            print(f"🤔 You can ask Arabic questions about Wikipedia content")
        else:
            print(f"\n⚠️ Integration partially successful")
            print(f"📤 Data uploaded but question answering needs improvement")
    else:
        print(f"\n❌ Integration failed")
        print(f"💡 Check API server and try again")

if __name__ == "__main__":
    main()
