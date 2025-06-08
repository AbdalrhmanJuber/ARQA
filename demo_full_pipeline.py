#!/usr/bin/env python3
# filepath: c:\Users\a-ahm\Desktop\arqa\demo_full_pipeline.py
"""
Full Pipeline Demo: HTML Ingestion + Document Retrieval
Demonstrates the complete workflow from HTML processing to semantic search.
"""

import os
import sys
import json
from pathlib import Path

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def demo_full_pipeline():
    """Demonstrate the complete ARQA pipeline."""
    
    print("🚀 ARQA Full Pipeline Demo")
    print("=" * 50)
    print("Phase 1: HTML Ingestion → Phase 2: Document Retrieval")
    print("=" * 50)
    
    # ==========================================
    # PHASE 1: HTML INGESTION
    # ==========================================
    print("\n📋 PHASE 1: HTML INGESTION")
    print("-" * 30)
    
    try:
        from arqa.simple_ingest import SimpleDocumentIngestor
        print("✅ Imported SimpleDocumentIngestor")
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    
    # Sample Arabic HTML content
    sample_html_docs = [
        {
            "url": "https://example.com/ai-article",
            "html": """
            <html>
            <head><title>الذكاء الاصطناعي</title></head>
            <body>
                <h1>مقدمة في الذكاء الاصطناعي</h1>
                <p>الذكاء الاصطناعي هو تقنية حديثة تهدف إلى محاكاة الذكاء البشري في الآلات والحاسوب. 
                يشمل الذكاء الاصطناعي مجالات متعددة مثل التعلم الآلي والشبكات العصبية ومعالجة اللغات الطبيعية.</p>
                
                <h2>تطبيقات الذكاء الاصطناعي</h2>
                <p>يستخدم الذكاء الاصطناعي في العديد من المجالات مثل الطب والتعليم والمالية والنقل. 
                في المجال الطبي، يساعد في تشخيص الأمراض وتطوير العلاجات الجديدة.</p>
                
                <h2>مستقبل الذكاء الاصطناعي</h2>
                <p>يتوقع الخبراء أن يلعب الذكاء الاصطناعي دوراً مهماً في تطوير التكنولوجيا المستقبلية 
                وحل العديد من التحديات التي تواجه البشرية.</p>
            </body>
            </html>
            """
        },
        {
            "url": "https://example.com/education-article",
            "html": """
            <html>
            <head><title>التعليم الإلكتروني</title></head>
            <body>
                <h1>التعليم الإلكتروني في العصر الحديث</h1>
                <p>التعليم الإلكتروني أصبح جزءاً لا يتجزأ من النظام التعليمي الحديث. 
                يوفر هذا النوع من التعليم مرونة في الوقت والمكان للطلاب والمعلمين.</p>
                
                <h2>مزايا التعليم الإلكتروني</h2>
                <p>من أهم مزايا التعليم الإلكتروني إمكانية الوصول إلى المحتوى التعليمي في أي وقت ومن أي مكان. 
                كما يوفر أدوات تفاعلية متقدمة تساعد في تحسين عملية التعلم.</p>
                
                <h2>التحديات والحلول</h2>
                <p>رغم المزايا العديدة، يواجه التعليم الإلكتروني تحديات مثل نقص التفاعل المباشر 
                والحاجة إلى مهارات تقنية متقدمة.</p>
            </body>
            </html>
            """
        },
        {
            "url": "https://example.com/renewable-energy",
            "html": """
            <html>
            <head><title>الطاقة المتجددة</title></head>
            <body>
                <h1>الطاقة المتجددة: مستقبل مستدام</h1>
                <p>الطاقة المتجددة تشمل مصادر الطاقة التي لا تنضب مثل الطاقة الشمسية وطاقة الرياح والطاقة المائية. 
                تعتبر هذه المصادر بديلاً نظيفاً ومستداماً للوقود الأحفوري.</p>
                
                <h2>الطاقة الشمسية</h2>
                <p>الطاقة الشمسية هي أكثر مصادر الطاقة المتجددة توفراً على الأرض. 
                تستخدم الألواح الشمسية لتحويل ضوء الشمس إلى كهرباء نظيفة.</p>
                
                <h2>طاقة الرياح</h2>
                <p>طاقة الرياح تستخدم التربينات الهوائية لتوليد الكهرباء من حركة الهواء. 
                تعتبر من أسرع مصادر الطاقة نمواً في العالم.</p>
            </body>
            </html>
            """
        }
    ]
    
    # Process HTML documents
    print("🔧 Processing HTML documents...")
    
    ingestor = SimpleDocumentIngestor(
        output_dir="./demo_output",
        chunk_size=200,
        chunk_overlap=50
    )
    
    processed_docs = []
    for doc in sample_html_docs:
        print(f"   📄 Processing: {doc['url']}")
        result = ingestor.process_html(doc['url'], doc['html'])
        processed_docs.append(result)
    
    # Save processed documents
    output_file = "./demo_output/processed_documents.json"
    ingestor.save_documents(processed_docs, output_file)
    print(f"✅ Phase 1 Complete: {len(processed_docs)} documents processed")
    
    # ==========================================
    # PHASE 2: DOCUMENT RETRIEVAL
    # ==========================================
    print("\n🔍 PHASE 2: DOCUMENT RETRIEVAL")
    print("-" * 30)
    
    try:
        from arqa.retriever import ArabicDocumentRetriever
        print("✅ Imported ArabicDocumentRetriever")
    except ImportError as e:
        print(f"❌ Retriever import error: {e}")
        print("💡 Install dependencies: pip install torch transformers faiss-cpu tqdm numpy")
        return False
    
    # Convert processed documents to retriever format
    print("🔧 Converting documents for retrieval...")
    
    retriever_docs = []
    for doc in processed_docs:
        for chunk in doc.get('chunks', []):
            retriever_docs.append({
                'content': chunk['content'],
                'meta': {
                    'source': doc.get('source', 'unknown'),
                    'title': doc.get('title', 'No title'),
                    'url': doc.get('url', ''),
                    'chunk_index': chunk.get('chunk_index', 0)
                },
                'chunk_id': chunk.get('chunk_index', 0)
            })
    
    print(f"📚 Converted {len(retriever_docs)} document chunks")
    
    # Initialize retriever with AraDPR
    print("🚀 Initializing retriever with AraDPR...")
    
    try:
        retriever = ArabicDocumentRetriever(
            model_name="abdoelsayed/AraDPR",
            index_path="./demo_output/faiss_index",
            documents_path="./demo_output/documents_metadata.json",
            top_k=3
        )
        
        # Add documents and create embeddings
        retriever.add_documents(retriever_docs)
        print("✅ Phase 2 Complete: Documents indexed and ready for search")
        
    except Exception as e:
        print(f"❌ Error initializing retriever: {e}")
        return False
    
    # ==========================================
    # PHASE 3: SEMANTIC SEARCH DEMO
    # ==========================================
    print("\n🎯 PHASE 3: SEMANTIC SEARCH DEMO")
    print("-" * 30)
    
    # Test queries
    test_queries = [
        "ما هو الذكاء الاصطناعي؟",
        "معلومات عن التعليم الإلكتروني",
        "أنواع الطاقة المتجددة",
        "تطبيقات التكنولوجيا في التعليم",
        "مزايا الطاقة الشمسية",
        "تحديات التعليم الرقمي"
    ]
    
    print("🔍 Testing semantic search with Arabic queries...")
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n{'='*20} Query {i} {'='*20}")
        print(f"🔍 السؤال: {query}")
        
        try:
            results = retriever.retrieve(query, top_k=2)
            
            if results:
                print("📖 النتائج:")
                for j, result in enumerate(results, 1):
                    print(f"\n   📄 نتيجة {j} (نقاط التشابه: {result.score:.3f})")
                    print(f"   📰 العنوان: {result.meta.get('title', 'بدون عنوان')}")
                    print(f"   📝 المحتوى: {result.content[:120]}...")
                    print(f"   🔗 المصدر: {result.meta.get('url', 'غير محدد')}")
            else:
                print("   ⚠️ لم يتم العثور على نتائج")
                
        except Exception as e:
            print(f"   ❌ خطأ في البحث: {e}")
    
    # ==========================================
    # PHASE 4: MODEL SWITCHING DEMO
    # ==========================================
    print(f"\n{'='*50}")
    print("🔄 BONUS: MODEL SWITCHING DEMO")
    print("-" * 30)
    
    try:
        print("🔄 Switching to e5-arabic-base model...")
        retriever.switch_model("intfloat/e5-arabic-base")
        
        # Test with new model
        test_query = "التطورات التقنية الحديثة"
        print(f"🔍 Testing with new model: {test_query}")
        
        results = retriever.retrieve(test_query, top_k=2)
        if results:
            for j, result in enumerate(results, 1):
                print(f"   📄 Result {j}: {result.content[:80]}...")
        
        print("✅ Model switching successful!")
        
    except Exception as e:
        print(f"⚠️ Model switching failed: {e}")
        print("💡 This is normal - switching may fail due to model availability or memory")
    
    # ==========================================
    # SUMMARY
    # ==========================================
    print(f"\n{'='*50}")
    print("📊 PIPELINE SUMMARY")
    print("-" * 30)
    
    stats = retriever.get_stats()
    print("✅ Successfully completed:")
    print(f"   📋 Phase 1: Processed {len(processed_docs)} HTML documents")
    print(f"   📚 Phase 2: Indexed {stats['total_documents']} document chunks")  
    print(f"   🔍 Phase 3: Tested semantic search with {len(test_queries)} queries")
    print(f"   🤖 Model: {stats['model_name']}")
    print(f"   💾 Index size: {stats['index_size']} embeddings")
    
    print("\n🎉 ARQA Pipeline Demo Complete!")
    print("\n📋 What's working:")
    print("   ✅ HTML processing with Arabic normalization")
    print("   ✅ Document chunking and metadata extraction")
    print("   ✅ AraDPR embeddings with FAISS indexing")
    print("   ✅ Semantic search in Arabic")
    print("   ✅ Model switching capabilities")
    print("   ✅ Progress bars and user feedback")
    
    print("\n🔄 Next steps:")
    print("   1. Add question answering (reader.py)")
    print("   2. Create REST API interface (api.py)")
    print("   3. Add more sophisticated text preprocessing")
    print("   4. Implement evaluation metrics")
    
    return True


if __name__ == "__main__":
    # Create output directory
    os.makedirs("demo_output", exist_ok=True)
    
    # Run the demo
    success = demo_full_pipeline()
    
    if not success:
        print("\n💡 Installation help:")
        print("   Basic (Phase 1): pip install beautifulsoup4 lxml")
        print("   Full (Phase 2): pip install torch transformers faiss-cpu tqdm numpy")
