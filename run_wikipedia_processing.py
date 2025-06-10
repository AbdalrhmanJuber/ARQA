#!/usr/bin/env python3
"""
Production Wikipedia Processing for ARQA System
Process the full Arabic Wikipedia dump in production
"""

import os
import sys
import json
import time
from datetime import datetime

# Add project root to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def main():
    """Main production processing function"""
    
    print("🚀 ARQA Wikipedia Production Processing")
    print("=" * 60)
    
    # Configuration
    dump_file = "arwiki-latest-pages-articles.xml.bz2"
    
    if not os.path.exists(dump_file):
        print(f"❌ Wikipedia dump file not found: {dump_file}")
        print(f"💡 Download from: https://dumps.wikimedia.org/arwiki/latest/")
        return
    
    # Get file size
    file_size = os.path.getsize(dump_file) / (1024 * 1024 * 1024)  # GB
    print(f"📁 File size: {file_size:.2f} GB")
    
    # Processing options
    print(f"\n📋 Processing Options:")
    print(f"1. Test run (1,000 articles)")
    print(f"2. Medium run (10,000 articles)")
    print(f"3. Large run (100,000 articles)")
    print(f"4. Full processing (ALL articles - may take hours)")
    
    choice = input(f"\nSelect option (1-4): ").strip()
    
    # Configure based on choice
    if choice == '1':
        max_articles = 1000
        output_dir = "wikipedia_test"
        batch_size = 50
        description = "Test run"
    elif choice == '2':
        max_articles = 10000
        output_dir = "wikipedia_medium"
        batch_size = 100
        description = "Medium run"
    elif choice == '3':
        max_articles = 100000
        output_dir = "wikipedia_large"
        batch_size = 200
        description = "Large run"
    elif choice == '4':
        max_articles = None
        output_dir = "wikipedia_full"
        batch_size = 500
        description = "FULL processing"
    else:
        print("❌ Invalid choice")
        return
    
    print(f"\n🎯 Configuration:")
    print(f"   📄 Max articles: {max_articles or 'ALL'}")
    print(f"   📂 Output directory: {output_dir}")
    print(f"   📦 Batch size: {batch_size}")
    print(f"   📊 Description: {description}")
    
    # Confirm before starting
    if choice in ['3', '4']:
        confirm = input(f"\n⚠️ This will process a large dataset. Continue? (y/n): ").lower().strip()
        if confirm != 'y':
            print("❌ Processing cancelled")
            return
    
    # Start processing
    print(f"\n🚀 Starting {description}...")
    print(f"⏰ Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        from process_wikipedia import WikipediaProcessor
        
        processor = WikipediaProcessor(output_dir=output_dir)
        start_time = time.time()
        
        processor.process_wikipedia_dump(
            dump_file=dump_file,
            max_articles=max_articles,
            batch_size=batch_size
        )
        
        end_time = time.time()
        total_time = end_time - start_time
        
        print(f"\n🎉 Processing Complete!")
        print(f"⏰ Total time: {total_time/3600:.2f} hours")
        print(f"📁 Results saved in: {output_dir}")
        
        # Show final statistics
        stats_file = os.path.join(output_dir, "wikipedia_processing_stats.json")
        if os.path.exists(stats_file):
            with open(stats_file, 'r', encoding='utf-8') as f:
                stats = json.load(f)
            
            print(f"\n📊 Final Statistics:")
            print(f"   ✅ Articles processed: {stats.get('articles_processed', 0):,}")
            print(f"   📄 Total chunks created: {stats.get('chunks_created', 0):,}")
            
            if stats.get('articles_processed', 0) > 0:
                avg_chunks = stats.get('chunks_created', 0) / stats.get('articles_processed', 1)
                print(f"   📈 Average chunks per article: {avg_chunks:.1f}")
        
        # Next steps
        print(f"\n🔥 Next Steps:")
        print(f"1. Test the processed data with ARQA API")
        print(f"2. Upload processed chunks to the question answering system")
        print(f"3. Test Arabic questions on Wikipedia content")
        
    except KeyboardInterrupt:
        print(f"\n⚠️ Processing interrupted by user")
    except Exception as e:
        print(f"\n❌ Error during processing: {e}")

if __name__ == "__main__":
    main()
