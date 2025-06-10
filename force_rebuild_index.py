#!/usr/bin/env python3
"""
Force Rebuild FAISS Index
Completely rebuild the FAISS index from scratch
"""

import os
import sys
import json

# Add project root to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def main():
    print("🔥 FORCE REBUILD FAISS Index")
    print("=" * 60)
    
    # Import the retriever
    try:
        from arqa.retriever_optimized_fixed import OptimizedArabicRetriever
        print("✅ Successfully imported OptimizedArabicRetriever")
    except ImportError as e:
        print(f"❌ Error importing retriever: {e}")
        return
    
    # Load documents from metadata
    metadata_file = "documents_metadata.json"
    print(f"📁 Loading documents from: {metadata_file}")
    
    try:
        with open(metadata_file, 'r', encoding='utf-8') as f:
            metadata = json.load(f)
        
        documents = metadata.get('documents', [])
        model_name = metadata.get('model_name', 'abdoelsayed/AraDPR')
        
        print(f"✅ Loaded {len(documents):,} documents")
        print(f"🤖 Model: {model_name}")
        
        # Show breakdown by source
        sources = {}
        for doc in documents:
            source = doc.get('meta', {}).get('source', 'unknown')
            sources[source] = sources.get(source, 0) + 1
        
        print(f"📊 Document sources:")
        for source, count in sources.items():
            print(f"   {source}: {count:,}")
        
    except Exception as e:
        print(f"❌ Error loading metadata: {e}")
        return
    
    # Remove existing index files
    print(f"\n🗑️ Cleaning up existing index files...")
    index_files = ["./faiss_index.faiss", "./faiss_index"]
    for file_path in index_files:
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                print(f"   ✅ Removed: {file_path}")
            except Exception as e:
                print(f"   ⚠️ Could not remove {file_path}: {e}")
    
    # Initialize fresh retriever
    print(f"\n🔧 Initializing fresh retriever...")
    try:
        retriever = OptimizedArabicRetriever(
            model_name=model_name,
            index_path="./faiss_index",
            documents_path="./temp_metadata.json",  # Use temp file to avoid conflicts
            batch_size=32,
            device="auto"
        )
        print(f"✅ Fresh retriever initialized")
        
    except Exception as e:
        print(f"❌ Error initializing retriever: {e}")
        return
    
    # Verify retriever is empty
    print(f"📊 Retriever status: {len(retriever.documents)} documents")
    
    # Confirm rebuild
    print(f"\n🎯 Force Rebuild Plan:")
    print(f"   📄 Documents to index: {len(documents):,}")
    print(f"   🤖 Model: {model_name}")
    print(f"   📁 Fresh index: ./faiss_index.faiss")
    print(f"   ⚡ Batch size: 32")
    
    confirm = input(f"\n✅ Proceed with FORCE rebuilding the index? (y/n): ").lower().strip()
    if confirm != 'y':
        print("❌ Index rebuild cancelled")
        return
    
    # Add all documents in batches
    print(f"\n🚀 Starting FORCE index rebuild...")
    batch_size = 1000
    total_processed = 0
    
    try:
        for i in range(0, len(documents), batch_size):
            batch = documents[i:i + batch_size]
            batch_num = i // batch_size + 1
            total_batches = (len(documents) + batch_size - 1) // batch_size
            
            print(f"\n📦 Processing batch {batch_num}/{total_batches} ({len(batch)} documents)...")
            
            result = retriever.add_documents_incremental(
                documents=batch,
                background=False,
                force_reindex=True
            )
            
            total_processed += result.get('new_documents', 0)
            print(f"   ✅ Processed: {result.get('new_documents', 0)} documents")
            print(f"   📊 Total so far: {total_processed:,}/{len(documents):,}")
        
        print(f"\n🎉 FORCE Index Rebuild Complete!")
        print(f"✅ Total processed: {total_processed:,}")
        
        # Verify the rebuilt index
        print(f"\n🔍 Verifying rebuilt index...")
        final_count = len(retriever.documents)
        index_size = retriever.index.ntotal if retriever.index else 0
        
        print(f"📊 Final Statistics:")
        print(f"   📄 Document count: {final_count:,}")
        print(f"   📊 FAISS index size: {index_size:,}")
        print(f"   ✅ Match: {final_count == index_size}")
        
        # Save the final index with correct path
        print(f"\n💾 Saving final index...")
        retriever.documents_path = "./documents_metadata.json"
        retriever.save_index()
        print(f"✅ Index saved to ./faiss_index.faiss")
        
        # Test search functionality
        print(f"\n🧪 Testing search functionality...")
        try:
            test_queries = [
                "ما هو الماء؟",
                "الذكاء الاصطناعي",
                "العلوم"
            ]
            
            for query in test_queries:
                results = retriever.retrieve(query, top_k=2)
                print(f"✅ Query: '{query}' → {len(results)} results")
                for j, result in enumerate(results, 1):
                    title = result.metadata.get('title', 'Unknown')
                    score = result.score
                    source = result.metadata.get('source', 'unknown')
                    print(f"   {j}. [{source}] {title} (Score: {score:.3f})")
                
        except Exception as e:
            print(f"⚠️ Search test failed: {e}")
        
        # Clean up temp file
        temp_file = "./temp_metadata.json"
        if os.path.exists(temp_file):
            os.remove(temp_file)
        
    except Exception as e:
        print(f"❌ Error during index rebuild: {e}")
        import traceback
        traceback.print_exc()
        return
    
    print(f"\n🎉 FAISS Index Successfully FORCE Rebuilt!")
    print(f"📄 Your ARQA system now has access to all {len(documents):,} documents")
    print(f"🌟 Including Wikipedia content for enhanced Arabic QA!")

if __name__ == "__main__":
    main()
