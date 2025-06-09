#!/usr/bin/env python3
"""
Test HTML ingestion with non-normalized text preservation
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from arqa.simple_ingest import SimpleDocumentIngestor

def test_html_ingestion():
    """Test HTML ingestion preserves original Arabic characters."""
    
    print("📄 Testing HTML ingestion with non-normalized text...")
    
    # Initialize ingestor
    ingestor = SimpleDocumentIngestor()
    
    # Test with one of the HTML files
    html_file = r"C:\Users\a-ahm\Desktop\arqa\test_html_articles\arabic_science.html"
    
    if os.path.exists(html_file):
        print(f"📖 Processing: {html_file}")
        
        # Process the file
        documents = ingestor.process_html_file(html_file)
        
        if documents:
            print(f"✅ Created {len(documents)} document chunks")
            
            # Check first few chunks for original characters
            for i, doc in enumerate(documents[:3]):
                content = doc['content']
                print(f"\n📄 Chunk {i+1}:")
                print(f"   Length: {len(content)} characters")
                print(f"   Preview: {content[:100]}...")
                
                # Check for original Arabic characters
                special_chars = ['إ', 'أ', 'آ', 'ة', 'ى', 'ئ', 'ؤ', 'ء', 'ً', 'ٌ', 'ٍ', 'َ', 'ُ', 'ِ', 'ّ']
                found_chars = []
                for char in special_chars:
                    if char in content:
                        found_chars.append(char)
                
                if found_chars:
                    print(f"   ✅ Original characters preserved: {', '.join(found_chars[:10])}")
                    if len(found_chars) > 10:
                        print(f"   ... and {len(found_chars)-10} more")
                else:
                    print(f"   ⚠️ No special Arabic characters found")
        else:
            print("❌ No documents created")
    else:
        print(f"❌ File not found: {html_file}")

if __name__ == "__main__":
    test_html_ingestion()
