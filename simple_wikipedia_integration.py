#!/usr/bin/env python3
"""
Simple Wikipedia to Metadata Integration
Add Wikipedia content to documents_metadata.json
"""

import os
import json
from datetime import datetime

def main():
    print("🚀 ARQA Wikipedia Integration")
    print("=" * 60)
    
    # Load existing metadata
    print("📁 Loading existing metadata...")
    try:
        with open('documents_metadata.json', 'r', encoding='utf-8') as f:
            existing_data = json.load(f)
        existing_count = len(existing_data.get('documents', []))
        print(f"   ✅ Loaded {existing_count:,} existing documents")
    except Exception as e:
        print(f"   ❌ Error loading metadata: {e}")
        return
    
    # Load Wikipedia chunks
    print("📁 Loading Wikipedia chunks...")
    all_chunks = []
    data_dir = "wikipedia_test"
    
    if not os.path.exists(data_dir):
        print(f"❌ Directory not found: {data_dir}")
        return
    
    batch_files = [f for f in os.listdir(data_dir) if f.startswith('wikipedia_batch_') and f.endswith('.json')]
    batch_files.sort()
    
    for batch_file in batch_files:
        batch_path = os.path.join(data_dir, batch_file)
        try:
            with open(batch_path, 'r', encoding='utf-8') as f:
                batch_data = json.load(f)
                all_chunks.extend(batch_data)
                print(f"   ✅ Loaded {len(batch_data)} chunks from {batch_file}")
        except Exception as e:
            print(f"   ❌ Error loading {batch_file}: {e}")
    
    print(f"📄 Total Wikipedia chunks loaded: {len(all_chunks)}")
    
    # Convert to metadata format
    print("🔄 Converting Wikipedia chunks to metadata format...")
    new_documents = []
    
    for i, chunk in enumerate(all_chunks):
        doc_id = existing_count + i
        metadata = chunk.get('metadata', {})
        title = metadata.get('title', 'Unknown')
        
        document = {
            "id": f"doc_{doc_id}",
            "content": chunk.get('content', ''),
            "meta": {
                "source": "wikipedia",
                "title": title,
                "wikipedia_metadata": metadata,
                "added_date": datetime.now().isoformat(),
                "chunk_id": metadata.get('chunk_id', 0),
                "total_chunks": metadata.get('total_chunks', 1)
            },
            "chunk_id": metadata.get('chunk_id', 0)
        }
        
        new_documents.append(document)
        
        if (i + 1) % 1000 == 0:
            print(f"   📈 Converted {i + 1:,} chunks...")
    
    print(f"✅ Conversion complete: {len(new_documents)} documents ready")
    
    # Show integration plan
    total_after = existing_count + len(new_documents)
    print(f"\n🎯 Integration Plan:")
    print(f"   📄 Existing documents: {existing_count:,}")
    print(f"   📄 New Wikipedia documents: {len(new_documents):,}")
    print(f"   📄 Total after merge: {total_after:,}")
    
    # Confirm integration
    confirm = input(f"\n✅ Proceed with integration? (y/n): ").lower().strip()
    if confirm != 'y':
        print("❌ Integration cancelled")
        return
    
    # Create backup
    backup_file = f"documents_metadata.json.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    try:
        with open('documents_metadata.json', 'r', encoding='utf-8') as src:
            with open(backup_file, 'w', encoding='utf-8') as dst:
                dst.write(src.read())
        print(f"💾 Backup created: {backup_file}")
    except Exception as e:
        print(f"⚠️ Backup failed: {e}")
    
    # Merge and save
    print("🔗 Merging and saving...")
    merged_data = existing_data.copy()
    merged_data['documents'].extend(new_documents)
    
    try:
        with open('documents_metadata.json', 'w', encoding='utf-8') as f:
            json.dump(merged_data, f, ensure_ascii=False, indent=2)
        
        print(f"✅ Successfully saved {len(merged_data['documents']):,} documents")
        
        # Validation
        print("🔍 Validating integration...")
        doc_ids = [doc['id'] for doc in merged_data['documents']]
        unique_ids = set(doc_ids)
        wikipedia_docs = [doc for doc in merged_data['documents'] if doc.get('meta', {}).get('source') == 'wikipedia']
        
        print(f"📊 Validation Results:")
        print(f"   📄 Total documents: {len(merged_data['documents']):,}")
        print(f"   🆔 Unique IDs: {len(unique_ids):,}")
        print(f"   📚 Wikipedia documents: {len(wikipedia_docs):,}")
        print(f"   ✅ No ID duplicates: {len(unique_ids) == len(merged_data['documents'])}")
        
        if len(unique_ids) == len(merged_data['documents']):
            print(f"\n🎉 Wikipedia Integration Complete!")
            print(f"✅ {len(new_documents):,} Wikipedia documents added successfully")
            print(f"📄 Total dataset now contains {len(merged_data['documents']):,} documents")
            print(f"🚀 Ready for enhanced Arabic question answering!")
        else:
            print(f"\n❌ Integration completed but validation failed")
            
    except Exception as e:
        print(f"❌ Error saving metadata: {e}")

if __name__ == "__main__":
    main()
