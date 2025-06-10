#!/usr/bin/env python3
"""
Arabic Wikipedia Processor for ARQA System
Extracts and processes Arabic Wikipedia dump for question answering
"""

import os
import sys
import bz2
import json
import xml.etree.ElementTree as ET
from typing import Dict, List, Any, Iterator
import re
from datetime import datetime
import tempfile

# Add project root to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from arqa.simple_ingest import SimpleDocumentIngestor

class WikipediaProcessor:
    """🚀 Process Arabic Wikipedia dump for ARQA system"""
    
    def __init__(self, output_dir: str = "wikipedia_processed"):
        self.output_dir = output_dir
        self.ingestor = SimpleDocumentIngestor(output_dir=output_dir)
        self.stats = {
            'articles_processed': 0,
            'articles_skipped': 0,
            'chunks_created': 0,
            'start_time': None,
            'processing_errors': 0
        }
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
    
    def clean_wikitext(self, text: str) -> str:
        """
        🧹 Clean Wikipedia markup from text
        
        Args:
            text: Raw Wikipedia article text with markup
            
        Returns:
            Clean text without markup
        """
        # Remove common Wikipedia markup patterns
        # Remove templates {{ }}
        text = re.sub(r'\{\{[^}]*\}\}', '', text)
        
        # Remove internal links [[ ]] but keep the text
        text = re.sub(r'\[\[([^\]|]*\|)?([^\]]*)\]\]', r'\2', text)
        
        # Remove external links
        text = re.sub(r'\[http[^\]]*\]', '', text)
        
        # Remove references <ref>...</ref>
        text = re.sub(r'<ref[^>]*>.*?</ref>', '', text, flags=re.DOTALL)
        text = re.sub(r'<ref[^>]*/?>', '', text)
        
        # Remove HTML tags
        text = re.sub(r'<[^>]+>', '', text)
        
        # Remove file/image links
        text = re.sub(r'\[\[(File|Image|ملف|صورة):[^\]]*\]\]', '', text, flags=re.IGNORECASE)
        
        # Remove categories
        text = re.sub(r'\[\[(Category|تصنيف):[^\]]*\]\]', '', text, flags=re.IGNORECASE)
        
        # Clean up extra whitespace
        text = re.sub(r'\n+', '\n', text)
        text = re.sub(r' +', ' ', text)
        text = text.strip()
        
        return text
    
    def extract_article_from_xml(self, page_xml: str) -> Dict[str, Any]:
        """
        📄 Extract article content from Wikipedia XML page
        
        Args:
            page_xml: XML content of a single Wikipedia page
            
        Returns:
            Dictionary with article title and clean text
        """
        try:
            # Parse XML
            root = ET.fromstring(f"<root>{page_xml}</root>")
            
            # Extract title
            title_elem = root.find('.//title')
            title = title_elem.text if title_elem is not None else "Untitled"
            
            # Extract text content
            text_elem = root.find('.//text')
            if text_elem is None or not text_elem.text:
                return None
            
            raw_text = text_elem.text
            
            # Skip redirects
            if raw_text.strip().startswith('#تحويل') or raw_text.strip().startswith('#REDIRECT'):
                return None
            
            # Clean the text
            clean_text = self.clean_wikitext(raw_text)
            
            # Skip very short articles
            if len(clean_text.strip()) < 100:
                return None
            
            return {
                'title': title,
                'text': clean_text,
                'length': len(clean_text)
            }
            
        except Exception as e:
            print(f"❌ Error parsing article XML: {e}")
            return None
    
    def parse_wikipedia_dump(self, dump_file: str, max_articles: int = None) -> Iterator[Dict[str, Any]]:
        """
        📖 Parse Wikipedia dump file and yield articles
        
        Args:
            dump_file: Path to .bz2 Wikipedia dump file
            max_articles: Maximum number of articles to process (None for all)
            
        Yields:
            Dictionary with article data
        """
        print(f"🚀 Starting to parse Wikipedia dump: {dump_file}")
        
        article_count = 0
        current_page = []
        in_page = False
        
        # Open compressed file
        with bz2.open(dump_file, 'rt', encoding='utf-8') as f:
            for line_num, line in enumerate(f):
                line = line.strip()
                
                # Track pages
                if '<page>' in line:
                    in_page = True
                    current_page = ['<page>']
                elif '</page>' in line:
                    current_page.append('</page>')
                    
                    # Process complete page
                    page_xml = '\n'.join(current_page)
                    article = self.extract_article_from_xml(page_xml)
                    
                    if article:
                        article_count += 1
                        yield article
                        
                        if article_count % 1000 == 0:
                            print(f"📄 Processed {article_count} articles...")
                        
                        if max_articles and article_count >= max_articles:
                            print(f"🔚 Reached maximum articles limit: {max_articles}")
                            break
                    
                    in_page = False
                    current_page = []
                    
                elif in_page:
                    current_page.append(line)
                
                # Progress indicator for large files
                if line_num % 100000 == 0:
                    print(f"⚡ Processed {line_num:,} lines...")
    
    def process_wikipedia_dump(self, dump_file: str, max_articles: int = None, batch_size: int = 100):
        """
        🏭 Process entire Wikipedia dump and create ARQA documents
        
        Args:
            dump_file: Path to .bz2 Wikipedia dump file
            max_articles: Maximum number of articles to process
            batch_size: Number of articles to process in each batch
        """
        print(f"🚀 Processing Arabic Wikipedia Dump")
        print(f"📁 Input: {dump_file}")
        print(f"📂 Output: {self.output_dir}")
        print(f"🔢 Max articles: {max_articles or 'All'}")
        print("=" * 60)
        
        self.stats['start_time'] = datetime.now()
        
        # Process articles in batches
        batch_articles = []
        
        try:
            for article in self.parse_wikipedia_dump(dump_file, max_articles):
                batch_articles.append(article)
                
                # Process batch when full
                if len(batch_articles) >= batch_size:
                    self._process_article_batch(batch_articles)
                    batch_articles = []
            
            # Process remaining articles
            if batch_articles:
                self._process_article_batch(batch_articles)
                
        except KeyboardInterrupt:
            print(f"\n⚠️ Processing interrupted by user")
        except Exception as e:
            print(f"\n❌ Processing error: {e}")
            self.stats['processing_errors'] += 1
        
        # Save final statistics
        self._save_statistics()
        self._print_final_stats()
    
    def _process_article_batch(self, articles: List[Dict[str, Any]]):
        """Process a batch of articles"""
        all_documents = []
        
        for article in articles:
            try:
                # Create XML content for processing
                xml_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<article>
    <title>{article['title']}</title>
    <content>
        {article['text']}
    </content>
</article>"""
                
                # Process with ingestor
                documents = self.ingestor.process_xml_content(
                    xml_content, 
                    source_url=f"wikipedia:{article['title']}"
                )
                
                if documents:
                    all_documents.extend(documents)
                    self.stats['articles_processed'] += 1
                    self.stats['chunks_created'] += len(documents)
                else:
                    self.stats['articles_skipped'] += 1
                    
            except Exception as e:
                print(f"❌ Error processing article '{article['title']}': {e}")
                self.stats['articles_skipped'] += 1
                self.stats['processing_errors'] += 1
        
        # Save batch documents
        if all_documents:
            batch_filename = f"wikipedia_batch_{self.stats['articles_processed']//100:04d}.json"
            batch_path = os.path.join(self.output_dir, batch_filename)
            
            with open(batch_path, 'w', encoding='utf-8') as f:
                json.dump(all_documents, f, ensure_ascii=False, indent=2)
            
            print(f"💾 Saved batch: {len(all_documents)} chunks to {batch_filename}")
    
    def _save_statistics(self):
        """Save processing statistics"""
        if self.stats['start_time']:
            self.stats['total_time'] = (datetime.now() - self.stats['start_time']).total_seconds()
        
        stats_file = os.path.join(self.output_dir, "wikipedia_processing_stats.json")
        with open(stats_file, 'w', encoding='utf-8') as f:
            json.dump(self.stats, f, ensure_ascii=False, indent=2, default=str)
    
    def _print_final_stats(self):
        """Print final processing statistics"""
        print(f"\n🎉 Wikipedia Processing Complete!")
        print(f"📊 Final Statistics:")
        print(f"   ✅ Articles processed: {self.stats['articles_processed']:,}")
        print(f"   ⏭️ Articles skipped: {self.stats['articles_skipped']:,}")
        print(f"   📄 Total chunks created: {self.stats['chunks_created']:,}")
        print(f"   ❌ Processing errors: {self.stats['processing_errors']:,}")
        
        if self.stats.get('total_time'):
            total_time = self.stats['total_time']
            print(f"   ⏱️ Total processing time: {total_time:.2f} seconds")
            if self.stats['articles_processed'] > 0:
                avg_time = total_time / self.stats['articles_processed']
                print(f"   📈 Average time per article: {avg_time:.3f} seconds")
        
        print(f"📁 Output directory: {self.output_dir}")

def main():
    """Main function to process Wikipedia dump"""
    
    # Configuration
    dump_file = "arwiki-latest-pages-articles.xml.bz2"
    output_dir = "wikipedia_processed"
    max_articles = None  # Set to a number for testing, None for all articles
    
    # For testing, you might want to start with a smaller number
    test_mode = input("Test mode with 1000 articles? (y/n): ").lower().strip() == 'y'
    if test_mode:
        max_articles = 1000
        output_dir = "wikipedia_test"
    
    # Check if dump file exists
    if not os.path.exists(dump_file):
        print(f"❌ Wikipedia dump file not found: {dump_file}")
        print(f"💡 Make sure the file is in the current directory")
        return
    
    # Create processor and start
    processor = WikipediaProcessor(output_dir=output_dir)
    
    try:
        processor.process_wikipedia_dump(
            dump_file=dump_file,
            max_articles=max_articles,
            batch_size=50  # Smaller batches for better memory management
        )
    except KeyboardInterrupt:
        print(f"\n⚠️ Processing interrupted by user")
    except Exception as e:
        print(f"❌ Fatal error: {e}")

if __name__ == "__main__":
    main()
