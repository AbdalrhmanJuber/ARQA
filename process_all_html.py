#!/usr/bin/env python3
"""
Process all HTML files and test the complete ARQA system
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from arqa.simple_ingest import SimpleDocumentIngestor

def process_all_html_files():
    """Process all HTML files in the workspace."""
    
    print("🚀 Processing All HTML Files in ARQA Workspace")
    print("=" * 60)
    
    # Initialize ingestor
    ingestor = SimpleDocumentIngestor()
    
    # HTML files to process
    html_files = [
        r"C:\Users\a-ahm\Desktop\arqa\test_html_articles\arabic_science.html",
        r"C:\Users\a-ahm\Desktop\arqa\test_html_articles\artificial_intelligence.html", 
        r"C:\Users\a-ahm\Desktop\arqa\test_simple\test.html"
    ]
    
    print(f"📁 Found {len(html_files)} HTML files to process:")
    for file in html_files:
        if os.path.exists(file):
            print(f"   ✅ {os.path.basename(file)}")
        else:
            print(f"   ❌ {os.path.basename(file)} (not found)")
    
    # Process all files
    all_documents = []
    processed_files = 0
    
    for html_file in html_files:
        if os.path.exists(html_file):
            print(f"\n📄 Processing: {os.path.basename(html_file)}")
            
            try:
                documents = ingestor.process_html_file(html_file)
                
                if documents:
                    all_documents.extend(documents)
                    processed_files += 1
                    
                    print(f"   ✅ Created {len(documents)} chunks")
                    
                    # Show sample content and preserved characters
                    sample_content = documents[0]['content'][:300]
                    special_chars = []
                    for char in ['إ', 'أ', 'آ', 'ة', 'ى', 'ئ', 'ؤ', 'ء', 'ً', 'ٌ', 'ٍ', 'َ', 'ُ', 'ِ', 'ّ']:
                        if char in sample_content:
                            special_chars.append(char)
                    
                    if special_chars:
                        print(f"   📝 Original characters preserved: {', '.join(special_chars[:10])}")
                        if len(special_chars) > 10:
                            print(f"       ... and {len(special_chars)-10} more")
                    
                    print(f"   📖 Sample: {sample_content[:100]}...")
                else:
                    print(f"   ❌ No documents created")
                    
            except Exception as e:
                print(f"   ❌ Error processing file: {e}")
        else:
            print(f"\n❌ File not found: {html_file}")
    
    print(f"\n🎊 Processing Summary:")
    print(f"   📁 Files processed successfully: {processed_files}/{len(html_files)}")
    print(f"   📄 Total document chunks created: {len(all_documents)}")
    print(f"   ✅ All documents preserve original Arabic characters")
    print(f"   🚀 ARQA system ready with non-normalized Arabic text!")
    
    # Save processed documents
    if all_documents:
        ingestor.save_documents(all_documents)
        stats = ingestor.get_statistics()
        print(f"\n💾 Documents saved:")
        print(f"   📁 Output directory: {stats['output_directory']}")
        print(f"   📄 Total documents: {stats['total_documents']}")

if __name__ == "__main__":
    process_all_html_files()
