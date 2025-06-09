#!/usr/bin/env python3
"""
Quick Arabic document processing demo
Using the working simple_ingest.py (no Haystack dependencies)
"""

import sys
import os
sys.path.insert(0, '.')

# Use the WORKING ingestion system
from src.arqa.simple_ingest import SimpleDocumentIngestor

def main():
    print("🚀 Arabic Document Processing - Working Version")
    print("=" * 50)
    
    # Initialize the working ingestor
    ingestor = SimpleDocumentIngestor()
    print("✅ SimpleDocumentIngestor initialized")
    
    # Process the Arabic AI article
    html_file = "test_html_articles/artificial_intelligence.html"
    
    if os.path.exists(html_file):
        print(f"\n📄 Processing: {html_file}")
        
        # Process the HTML file
        documents = ingestor.process_html_file(html_file)
        print(f"✅ Success! Created {len(documents)} document chunks")
        
        # Show results
        for i, doc in enumerate(documents):
            print(f"\n📝 Chunk {i+1}:")
            print(f"   Title: {doc['metadata']['title']}")
            print(f"   Length: {len(doc['content'])} chars")
            print(f"   Preview: {doc['content'][:100]}...")
        
        print(f"\n🎉 SUCCESS! Processed Arabic HTML without any errors")
        print("✅ No Haystack dependencies required")
        print("✅ No FAISS configuration files needed")
        
    else:
        print(f"❌ File not found: {html_file}")

if __name__ == "__main__":
    main()
