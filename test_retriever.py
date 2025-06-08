#!/usr/bin/env python3
# filepath: c:\Users\a-ahm\Desktop\arqa\test_retriever.py
"""
Test script for Arabic Document Retriever with AraDPR
Demonstrates embedding creation, FAISS indexing, and semantic search.
"""

import os
import sys
import json
from pathlib import Path

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_retriever_with_sample_data():
    """Test the retriever with sample Arabic documents."""
    
    print("🚀 Testing Arabic Document Retriever with AraDPR")
    print("=" * 60)
    
    try:
        # Import the retriever
        from arqa.retriever import ArabicDocumentRetriever
        
        print("✅ Successfully imported ArabicDocumentRetriever")
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("\n💡 To use the retriever, install required dependencies:")
        print("pip install torch transformers faiss-cpu tqdm numpy")
        return False
    
    # Sample Arabic documents for testing
    sample_documents = [
        {
            "content": "الذكاء الاصطناعي هو تقنية حديثة تحاكي الذكاء البشري في الآلات والحاسوب",
            "meta": {"source": "tech_article_1", "title": "مقدمة في الذكاء الاصطناعي"},
            "chunk_id": 1
        },
        {
            "content": "الطب الحديث يستخدم التكنولوجيا المتقدمة لتشخيص الأمراض وعلاج المرضى",
            "meta": {"source": "medical_article_1", "title": "التكنولوجيا في الطب"},
            "chunk_id": 1
        },
        {
            "content": "اللغة العربية لها تاريخ عريق وثقافة غنية تمتد لآلاف السنين",
            "meta": {"source": "culture_article_1", "title": "تاريخ اللغة العربية"},
            "chunk_id": 1
        },
        {
            "content": "التعليم الإلكتروني أصبح جزءاً مهماً من النظام التعليمي في العصر الحديث",
            "meta": {"source": "education_article_1", "title": "التعليم الرقمي"},
            "chunk_id": 1
        },
        {
            "content": "الطاقة المتجددة مثل الطاقة الشمسية وطاقة الرياح هي مستقبل الطاقة",
            "meta": {"source": "energy_article_1", "title": "الطاقة البديلة"},
            "chunk_id": 1
        }
    ]
    
    # Test basic functionality
    print("\n1️⃣ Creating retriever with AraDPR...")
    try:
        retriever = ArabicDocumentRetriever(
            model_name="abdoelsayed/AraDPR",
            index_path="./test_output/faiss_index",
            documents_path="./test_output/documents_metadata.json",
            top_k=3
        )
        print("✅ Retriever created successfully")
    except Exception as e:
        print(f"❌ Error creating retriever: {e}")
        return False
    
    # Add documents
    print("\n2️⃣ Adding sample documents...")
    try:
        retriever.add_documents(sample_documents)
        print("✅ Documents added and indexed successfully")
    except Exception as e:
        print(f"❌ Error adding documents: {e}")
        return False
    
    # Test retrieval
    print("\n3️⃣ Testing retrieval with sample queries...")
    test_queries = [
        "ما هو الذكاء الاصطناعي؟",
        "كيف يستخدم الطب التكنولوجيا؟",
        "معلومات عن اللغة العربية",
        "التعليم الحديث",
        "الطاقة النظيفة"
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n🔍 Query {i}: {query}")
        try:
            results = retriever.retrieve(query, top_k=2)
            
            for j, result in enumerate(results, 1):
                print(f"   📄 Result {j} (Score: {result.score:.3f}):")
                print(f"      Content: {result.content[:80]}...")
                print(f"      Source: {result.meta.get('source', 'unknown')}")
                
        except Exception as e:
            print(f"   ❌ Error retrieving: {e}")
    
    # Test model switching
    print("\n4️⃣ Testing model switching...")
    try:
        print("🔄 Switching to e5-arabic-base model...")
        retriever.switch_model("intfloat/e5-arabic-base")
        
        # Test with new model
        test_query = "تقنيات حديثة"
        print(f"🔍 Testing with new model: {test_query}")
        results = retriever.retrieve(test_query, top_k=2)
        
        for j, result in enumerate(results, 1):
            print(f"   📄 Result {j} (Score: {result.score:.3f}):")
            print(f"      Content: {result.content[:80]}...")
            
        print("✅ Model switching works correctly")
        
    except Exception as e:
        print(f"❌ Error during model switching: {e}")
        print("💡 This might be due to model availability or memory constraints")
    
    # Display statistics
    print("\n5️⃣ Retriever Statistics:")
    stats = retriever.get_stats()
    for key, value in stats.items():
        print(f"   {key}: {value}")
    
    print("\n✅ All tests completed successfully!")
    print("💾 Index and metadata saved for future use")
    return True


def test_with_processed_documents():
    """Test retriever with previously processed documents if available."""
    
    # Check for existing processed documents
    processed_files = [
        "./test_output/processed_documents.json",
        "./test_simple_output/processed_documents.json"
    ]
    
    for file_path in processed_files:
        if os.path.exists(file_path):
            print(f"\n🔍 Found processed documents: {file_path}")
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                documents = data.get('documents', [])
                if documents:
                    print(f"📚 Loading {len(documents)} processed documents...")
                    
                    # Convert to retriever format
                    retriever_docs = []
                    for doc in documents:
                        for chunk in doc.get('chunks', []):
                            retriever_docs.append({
                                'content': chunk['content'],
                                'meta': {
                                    'source': doc.get('source', 'unknown'),
                                    'title': doc.get('title', 'No title'),
                                    'original_url': doc.get('url', ''),
                                    'chunk_index': chunk.get('chunk_index', 0)
                                },
                                'chunk_id': chunk.get('chunk_index', 0)
                            })
                    
                    if retriever_docs:
                        print(f"🚀 Testing retriever with {len(retriever_docs)} document chunks...")
                        
                        try:
                            from arqa.retriever import ArabicDocumentRetriever
                            
                            retriever = ArabicDocumentRetriever(
                                index_path="./test_output/real_docs_index",
                                documents_path="./test_output/real_docs_metadata.json"
                            )
                            
                            retriever.add_documents(retriever_docs[:10])  # Test with first 10 chunks
                            
                            # Test queries on real data
                            test_queries = [
                                "معلومات تقنية",
                                "الأمن والحماية",
                                "النظام والإدارة"
                            ]
                            
                            for query in test_queries:
                                print(f"\n🔍 Query: {query}")
                                results = retriever.retrieve(query, top_k=3)
                                
                                for i, result in enumerate(results, 1):
                                    print(f"   📄 Result {i}: {result.content[:100]}...")
                            
                            print("✅ Real documents test completed")
                            return True
                            
                        except ImportError:
                            print("⚠️ Retriever dependencies not available")
                            return False
                        except Exception as e:
                            print(f"❌ Error testing with real documents: {e}")
                            return False
            
            except Exception as e:
                print(f"❌ Error loading processed documents: {e}")
    
    return False


if __name__ == "__main__":
    print("🧪 Arabic Document Retriever Test Suite")
    print("=====================================")
    
    # Create output directory
    os.makedirs("test_output", exist_ok=True)
    
    # Run tests
    success = False
    
    # Test 1: Basic functionality with sample data
    success = test_retriever_with_sample_data()
    
    # Test 2: With real processed documents if available
    if success:
        print("\n" + "="*60)
        print("🔄 Testing with real processed documents...")
        test_with_processed_documents()
    
    if success:
        print("\n🎉 All retriever tests completed successfully!")
        print("\n📋 Next steps:")
        print("   1. ✅ HTML Ingestion (simple_ingest.py)")
        print("   2. ✅ Document Retrieval (retriever.py)")
        print("   3. 🔄 Question Answering (reader.py) - TODO")
        print("   4. 🔄 API Interface (api.py) - TODO")
    else:
        print("\n⚠️ Some tests failed. Check error messages above.")
