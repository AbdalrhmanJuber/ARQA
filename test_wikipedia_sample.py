#!/usr/bin/env python3
"""
Quick test of Wikipedia processing with a small sample
"""

import os
import sys
import bz2

# Add project root to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def test_wikipedia_sample():
    """Test Wikipedia processing with first few articles"""
    
    print("🧪 Testing Wikipedia Processing - Quick Sample")
    print("=" * 50)
    
    dump_file = "arwiki-latest-pages-articles.xml.bz2"
    
    if not os.path.exists(dump_file):
        print(f"❌ Wikipedia dump file not found: {dump_file}")
        return False
    
    print(f"📖 Reading first few lines from: {dump_file}")
    
    try:
        # Read first 1000 lines to see structure
        with bz2.open(dump_file, 'rt', encoding='utf-8') as f:
            line_count = 0
            found_articles = 0
            
            for line in f:
                line_count += 1
                line = line.strip()
                
                if '<title>' in line and '</title>' in line:
                    title = line.replace('<title>', '').replace('</title>', '').strip()
                    if not title.startswith('MediaWiki:') and not title.startswith('Template:'):
                        found_articles += 1
                        print(f"   📄 Article {found_articles}: {title}")
                        
                        if found_articles >= 10:  # Show first 10 articles
                            break
                
                if line_count >= 10000:  # Don't read too much
                    break
        
        print(f"✅ Successfully read {line_count:,} lines")
        print(f"📚 Found {found_articles} articles in sample")
        
        # Test the processor with a very small sample
        print(f"\n🔧 Testing processor with 5 articles...")
        
        from process_wikipedia import WikipediaProcessor
        
        processor = WikipediaProcessor(output_dir="wikipedia_test_sample")
        
        # Process just 5 articles for testing
        processor.process_wikipedia_dump(
            dump_file=dump_file,
            max_articles=5,
            batch_size=5
        )
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing Wikipedia file: {e}")
        return False

if __name__ == "__main__":
    test_wikipedia_sample()
