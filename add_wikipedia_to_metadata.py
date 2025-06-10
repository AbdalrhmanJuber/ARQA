#!/usr/bin/env python3
"""
Add Wikipedia Content to ARQA Documents Metadata
Integrate processed Wikipedia chunks into the main documents_metadata.json file
"""

import os
import sys
import json
from typing import List, Dict, Any
from datetime import datetime

# Add project root to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def load_existing_metadata(metadata_file: str = "documents_metadata.json") -> Dict[str, Any]:
    """Load existing documents metadata"""
    
    print(f"📁 Loading existing metadata from: {metadata_file}")
    
    try:
        with open(metadata_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print(f"   ✅ Loaded {len(data.get('documents', []))} existing documents")
        return data
    except FileNotFoundError:
        print(f"   ⚠️ File not found, creating new metadata structure")
        return {
            "model_name": "abdoelsayed/AraDPR",
            "documents": []
        }
    except Exception as e:
        print(f"   ❌ Error loading metadata: {e}")
        return None

def load_wikipedia_chunks(data_dir: str = "wikipedia_test") -> List[Dict[str, Any]]:
    """Load processed Wikipedia chunks from batch files"""
    
    print(f"📁 Loading Wikipedia chunks from: {data_dir}")
    
    if not os.path.exists(data_dir):
        print(f"❌ Directory not found: {data_dir}")
        return []
    
    all_chunks = []
    batch_files = [f for f in os.listdir(data_dir) if f.startswith('wikipedia_batch_') and f.endswith('.json')]
    batch_files.sort()
    
    print(f"📦 Found {len(batch_files)} batch files")
    
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
    return all_chunks

def convert_wikipedia_to_metadata_format(wikipedia_chunks: List[Dict[str, Any]], start_id: int = 0) -> List[Dict[str, Any]]:
    """Convert Wikipedia chunks to the metadata format used by ARQA"""
    
    print(f"🔄 Converting {len(wikipedia_chunks)} Wikipedia chunks to metadata format")
    print(f"📊 Starting ID: {start_id}")
    
    converted_documents = []
    
    for i, chunk in enumerate(wikipedia_chunks):
        doc_id = start_id + i
        
        # Extract metadata
        metadata = chunk.get('metadata', {})
        title = metadata.get('title', 'Unknown')
        
        # Create the document in ARQA format
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
        
        converted_documents.append(document)
        
        # Progress indicator
        if (i + 1) % 1000 == 0:
            print(f"   📈 Converted {i + 1:,} chunks...")
    
    print(f"✅ Conversion complete: {len(converted_documents)} documents ready")
    return converted_documents

def merge_and_save_metadata(existing_data: Dict[str, Any], new_documents: List[Dict[str, Any]], 
                           output_file: str = "documents_metadata.json", 
                           backup: bool = True) -> bool:
    """Merge new Wikipedia documents with existing metadata and save"""
    
    print(f"🔗 Merging {len(new_documents)} new documents with existing metadata")
    
    # Create backup if requested
    if backup and os.path.exists(output_file):
        backup_file = f"{output_file}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        try:
            with open(output_file, 'r', encoding='utf-8') as src:
                with open(backup_file, 'w', encoding='utf-8') as dst:
                    dst.write(src.read())
            print(f"💾 Backup created: {backup_file}")
        except Exception as e:
            print(f"⚠️ Backup failed: {e}")
    
    # Merge documents
    merged_data = existing_data.copy()
    merged_data['documents'].extend(new_documents)
    
    print(f"📊 Total documents after merge: {len(merged_data['documents'])}")
    
    # Save merged data
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(merged_data, f, ensure_ascii=False, indent=2)
        
        print(f"✅ Successfully saved to: {output_file}")
        return True
    except Exception as e:
        print(f"❌ Error saving metadata: {e}")
        return False

def validate_merged_metadata(metadata_file: str = "documents_metadata.json") -> bool:
    """Validate the merged metadata file"""
    
    print(f"🔍 Validating merged metadata: {metadata_file}")
    
    try:
        with open(metadata_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        documents = data.get('documents', [])
        total_docs = len(documents)
        
        # Check for duplicates
        doc_ids = [doc['id'] for doc in documents]
        unique_ids = set(doc_ids)
        
        # Count Wikipedia documents
        wikipedia_docs = [doc for doc in documents if doc.get('meta', {}).get('source') == 'wikipedia']
        
        print(f"📊 Validation Results:")
        print(f"   📄 Total documents: {total_docs:,}")
        print(f"   🆔 Unique IDs: {len(unique_ids):,}")
        print(f"   📚 Wikipedia documents: {len(wikipedia_docs):,}")
        print(f"   ✅ No ID duplicates: {len(unique_ids) == total_docs}")
        
        # Check content validity
        empty_content = [doc for doc in documents if not doc.get('content', '').strip()]
        print(f"   📝 Documents with empty content: {len(empty_content)}")
        
        if len(unique_ids) == total_docs and len(empty_content) == 0:
            print("✅ Validation passed!")
            return True
        else:
            print("❌ Validation failed!")
            return False
            
    except Exception as e:
        print(f"❌ Validation error: {e}")
        return False

def show_statistics(metadata_file: str = "documents_metadata.json"):
    """Show statistics about the merged dataset"""
    
    print(f"\n📊 Dataset Statistics")
    print("=" * 50)
    
    try:
        with open(metadata_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        documents = data.get('documents', [])
        
        # Overall stats
        total_docs = len(documents)
        total_content_length = sum(len(doc.get('content', '')) for doc in documents)
        avg_length = total_content_length / total_docs if total_docs > 0 else 0
        
        print(f"📄 Total Documents: {total_docs:,}")
        print(f"📝 Total Content Length: {total_content_length:,} characters")
        print(f"📈 Average Document Length: {avg_length:.1f} characters")
        
        # Source breakdown
        sources = {}
        for doc in documents:
            source = doc.get('meta', {}).get('source', 'unknown')
            sources[source] = sources.get(source, 0) + 1
        
        print(f"\n📚 Documents by Source:")
        for source, count in sources.items():
            percentage = (count / total_docs) * 100
            print(f"   {source}: {count:,} ({percentage:.1f}%)")
        
        # Wikipedia-specific stats
        wikipedia_docs = [doc for doc in documents if doc.get('meta', {}).get('source') == 'wikipedia']
        if wikipedia_docs:
            wiki_titles = set(doc.get('meta', {}).get('title', 'Unknown') for doc in wikipedia_docs)
            print(f"\n📖 Wikipedia Statistics:")
            print(f"   📄 Total Wikipedia chunks: {len(wikipedia_docs):,}")
            print(f"   📚 Unique Wikipedia articles: {len(wiki_titles):,}")
            avg_chunks_per_article = len(wikipedia_docs) / len(wiki_titles) if wiki_titles else 0
            print(f"   📈 Average chunks per article: {avg_chunks_per_article:.1f}")
        
    except Exception as e:
        print(f"❌ Error generating statistics: {e}")

def main():
    """Main integration function"""
    
    print("🚀 ARQA Wikipedia Integration")
    print("=" * 60)
    
    # Load existing metadata
    existing_data = load_existing_metadata()
    if existing_data is None:
        print("❌ Failed to load existing metadata")
        return
    
    existing_count = len(existing_data.get('documents', []))
    
    # Load Wikipedia chunks
    wikipedia_chunks = load_wikipedia_chunks("wikipedia_test")
    if not wikipedia_chunks:
        print("❌ No Wikipedia chunks found")
        return
    
    # Convert to metadata format
    new_documents = convert_wikipedia_to_metadata_format(wikipedia_chunks, start_id=existing_count)
    
    # Confirm before merging
    print(f"\n🎯 Integration Plan:")
    print(f"   📄 Existing documents: {existing_count:,}")
    print(f"   📄 New Wikipedia documents: {len(new_documents):,}")
    print(f"   📄 Total after merge: {existing_count + len(new_documents):,}")
    
    confirm = input(f"\n✅ Proceed with integration? (y/n): ").lower().strip()
    if confirm != 'y':
        print("❌ Integration cancelled")
        return
    
    # Merge and save
    success = merge_and_save_metadata(existing_data, new_documents)
    
    if success:
        # Validate the result
        is_valid = validate_merged_metadata()
        
        if is_valid:
            # Show final statistics
            show_statistics()
            
            print(f"\n🎉 Wikipedia Integration Complete!")
            print(f"✅ {len(new_documents):,} Wikipedia documents added successfully")
            print(f"📄 Total dataset now contains {existing_count + len(new_documents):,} documents")
            print(f"🚀 Ready for enhanced Arabic question answering!")
        else:
            print(f"\n❌ Integration completed but validation failed")
    else:
        print(f"\n❌ Integration failed")

if __name__ == "__main__":
    main()
