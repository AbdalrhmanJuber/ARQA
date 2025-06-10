#!/usr/bin/env python3
"""
Rebuild FAISS Index with Wikipedia Content
Update the FAISS index to include all documents from documents_metadata.json
"""

import os
import sys
import json
from typing import List, Dict, Any

# Add project root to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def main():
    print("🔧 ARQA FAISS Index Rebuild")
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
        
    except FileNotFoundError:
        print(f"❌ Metadata file not found: {metadata_file}")
        return
    except Exception as e:
        print(f"❌ Error loading metadata: {e}")
        return
    
    # Initialize retriever (this will create a fresh index)
    print(f"\n🔧 Initializing retriever...")
    try:
        retriever = OptimizedArabicRetriever(
            model_name=model_name,
            index_path="./faiss_index",
            documents_path="./documents_metadata.json",
            batch_size=64,  # Larger batch for faster processing
            device="auto"
        )
        print(f"✅ Retriever initialized")
        
    except Exception as e:
        print(f"❌ Error initializing retriever: {e}")
        return
    
    # Check current index status
    current_docs = len(retriever.documents) if hasattr(retriever, 'documents') else 0
    print(f"📊 Current index contains: {current_docs:,} documents")
    print(f"📊 Metadata contains: {len(documents):,} documents")
    
    if current_docs == len(documents):
        print("✅ Index is already up to date!")
        return
    
    # Confirm rebuild
    print(f"\n🎯 Rebuild Plan:")
    print(f"   📄 Documents to index: {len(documents):,}")
    print(f"   🤖 Model: {model_name}")
    print(f"   📁 Index path: ./faiss_index.faiss")
    
    # Clear existing index if it exists
    index_file = "./faiss_index.faiss"
    if os.path.exists(index_file):
        print(f"🗑️ Removing existing index file: {index_file}")
        try:
            os.remove(index_file)
        except Exception as e:
            print(f"⚠️ Could not remove existing index: {e}")
    
    # Reset retriever to clear any loaded data
    retriever.index = None
    retriever.documents = []
    retriever.id_to_doc = {}
    retriever.document_hashes = set()
    
    confirm = input(f"\n✅ Proceed with rebuilding the index? (y/n): ").lower().strip()
    if confirm != 'y':
        print("❌ Index rebuild cancelled")
        return
    
    # Add all documents
    print(f"\n🚀 Starting index rebuild...")
    try:
        result = retriever.add_documents_incremental(
            documents=documents,
            background=False,  # Process immediately
            force_reindex=True  # Force reindexing even if documents exist
        )
        
        print(f"\n🎉 Index Rebuild Complete!")
        print(f"✅ Processed documents: {result.get('new_documents', 0):,}")
        print(f"⏱️ Processing time: {result.get('processing_time', 0):.2f} seconds")
        
        # Verify the rebuilt index
        print(f"\n🔍 Verifying rebuilt index...")
        final_count = len(retriever.documents)
        index_size = retriever.index.ntotal if retriever.index else 0
        
        print(f"📊 Final Statistics:")
        print(f"   📄 Total documents: {final_count:,}")
        print(f"   📊 Index size: {index_size:,}")
        print(f"   ✅ Match: {final_count == index_size}")
        
        if final_count == len(documents):
            print(f"🎯 Success! Index contains all {len(documents):,} documents")
        else:
            print(f"⚠️ Warning: Expected {len(documents):,} documents, but index has {final_count:,}")
        
        # Test search functionality
        print(f"\n🧪 Testing search functionality...")
        try:
            test_query = "ما هو الماء؟"
            results = retriever.retrieve(test_query, top_k=3)
            
            print(f"✅ Search test successful! Found {len(results)} results for: {test_query}")
            for i, result in enumerate(results, 1):
                title = result.metadata.get('title', 'Unknown')
                score = result.score
                print(f"   {i}. [{title}] (Score: {score:.3f})")
                
        except Exception as e:
            print(f"⚠️ Search test failed: {e}")
        
    except Exception as e:
        print(f"❌ Error during index rebuild: {e}")
        import traceback
        traceback.print_exc()
        return
    
    print(f"\n🚀 FAISS Index Successfully Rebuilt!")
    print(f"📄 Your ARQA system now has access to all {len(documents):,} documents")
    print(f"🌟 Including {len([d for d in documents if d.get('meta', {}).get('source') == 'wikipedia']):,} Wikipedia articles!")

if __name__ == "__main__":
    main()
