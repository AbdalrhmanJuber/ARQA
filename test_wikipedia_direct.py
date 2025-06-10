#!/usr/bin/env python3
"""
Direct Wikipedia Content Testing for ARQA
Test processed Wikipedia content without API server
"""

import os
import sys
import json
from typing import List, Dict, Any

# Add project root to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def load_wikipedia_data(data_dir: str = "wikipedia_test") -> List[Dict[str, Any]]:
    """Load processed Wikipedia data from batch files"""
    
    print(f"📁 Loading Wikipedia data from: {data_dir}")
    
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
                # Data is already a list of chunks, not a dict with 'chunks' key
                if isinstance(batch_data, list):
                    chunks = batch_data
                else:
                    chunks = batch_data.get('chunks', [])
                all_chunks.extend(chunks)
                print(f"   ✅ Loaded {len(chunks)} chunks from {batch_file}")
        except Exception as e:
            print(f"   ❌ Error loading {batch_file}: {e}")
    
    print(f"📄 Total chunks loaded: {len(all_chunks)}")
    return all_chunks

def test_wikipedia_content(chunks: List[Dict[str, Any]], max_samples: int = 10):
    """Test the content and structure of Wikipedia chunks"""
    
    print(f"\n🧪 Testing Wikipedia Content Structure")
    print("=" * 50)
    
    if not chunks:
        print("❌ No chunks to test")
        return
    
    # Test chunk structure
    sample_chunk = chunks[0]
    print(f"📋 Chunk Keys: {list(sample_chunk.keys())}")
    
    # Show sample content
    for i, chunk in enumerate(chunks[:max_samples]):
        print(f"\n📄 Sample {i+1}:")
        print(f"   Title: {chunk.get('title', 'N/A')[:50]}...")
        print(f"   Content: {chunk.get('content', 'N/A')[:100]}...")
        print(f"   Length: {len(chunk.get('content', ''))}")
    
    # Statistics
    total_content_length = sum(len(chunk.get('content', '')) for chunk in chunks)
    avg_chunk_length = total_content_length / len(chunks)
    
    print(f"\n📊 Content Statistics:")
    print(f"   📄 Total chunks: {len(chunks):,}")
    print(f"   📝 Total content length: {total_content_length:,} characters")
    print(f"   📈 Average chunk length: {avg_chunk_length:.1f} characters")
    
    # Test Arabic content
    arabic_chunks = [chunk for chunk in chunks if has_arabic_content(chunk.get('content', ''))]
    print(f"   🔤 Chunks with Arabic content: {len(arabic_chunks):,} ({len(arabic_chunks)/len(chunks)*100:.1f}%)")

def has_arabic_content(text: str) -> bool:
    """Check if text contains Arabic characters"""
    arabic_range = range(0x0600, 0x06FF + 1)  # Basic Arabic Unicode range
    return any(ord(char) in arabic_range for char in text)

def test_sample_queries(chunks: List[Dict[str, Any]]):
    """Test sample Arabic queries against the content"""
    
    print(f"\n🔍 Testing Sample Arabic Queries")
    print("=" * 50)
    
    # Sample queries
    test_queries = [
        "ما هو الذكاء الاصطناعي؟",  # What is artificial intelligence?
        "كيف يعمل التعلم الآلي؟",     # How does machine learning work?
        "ما هي العلوم؟",            # What is science?
        "تاريخ العرب",              # Arab history
        "الفيزياء الحديثة"           # Modern physics
    ]
    
    for query in test_queries:
        print(f"\n🔎 Query: {query}")
        
        # Simple keyword matching (basic search simulation)
        relevant_chunks = find_relevant_chunks(chunks, query, max_results=3)
        
        if relevant_chunks:
            print(f"   ✅ Found {len(relevant_chunks)} relevant chunks:")
            for i, chunk in enumerate(relevant_chunks, 1):
                title = chunk.get('title', 'N/A')[:40]
                content_preview = chunk.get('content', 'N/A')[:80]
                print(f"      {i}. {title}... | {content_preview}...")
        else:
            print(f"   ❌ No relevant chunks found")

def find_relevant_chunks(chunks: List[Dict[str, Any]], query: str, max_results: int = 5) -> List[Dict[str, Any]]:
    """Simple keyword-based search for relevant chunks"""
    
    query_terms = query.split()
    relevant_chunks = []
    
    for chunk in chunks:
        content = chunk.get('content', '').lower()
        title = chunk.get('title', '').lower()
        
        # Count matching terms
        matches = sum(1 for term in query_terms if term.lower() in content or term.lower() in title)
        
        if matches > 0:
            chunk_copy = chunk.copy()
            chunk_copy['relevance_score'] = matches
            relevant_chunks.append(chunk_copy)
    
    # Sort by relevance and return top results
    relevant_chunks.sort(key=lambda x: x['relevance_score'], reverse=True)
    return relevant_chunks[:max_results]

def main():
    """Main testing function"""
    
    print("🚀 ARQA Wikipedia Direct Testing")
    print("=" * 60)
    
    # Load Wikipedia data
    chunks = load_wikipedia_data("wikipedia_test")
    
    if not chunks:
        print("❌ No Wikipedia data loaded. Please run Wikipedia processing first.")
        return
    
    # Test content structure and quality
    test_wikipedia_content(chunks)
    
    # Test sample queries
    test_sample_queries(chunks)
    
    print(f"\n✅ Wikipedia content testing completed!")
    print(f"📄 Your Arabic Wikipedia dataset contains {len(chunks):,} processed chunks")
    print(f"🚀 Ready for integration with ARQA question answering system!")

if __name__ == "__main__":
    main()
