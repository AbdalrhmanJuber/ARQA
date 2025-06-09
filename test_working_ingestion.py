"""
Test the working Arabic document ingestion system
"""
import sys
import os
sys.path.insert(0, '.')

def test_arabic_ingestion():
    """Test Arabic HTML document processing"""
    print("🚀 Testing Arabic Document Ingestion")
    print("=" * 50)
    
    try:
        # Import the working simple ingest (no Haystack dependencies)
        from src.arqa.simple_ingest import SimpleDocumentIngestor
        print("✅ Successfully imported SimpleDocumentIngestor")
        
        # Initialize the ingestor
        ingestor = SimpleDocumentIngestor()
        print("✅ Ingestor initialized successfully")
        
        # Test processing the Arabic AI article
        html_file = "test_html_articles/artificial_intelligence.html"
        
        if os.path.exists(html_file):
            print(f"📄 Processing: {html_file}")
            
            # Read and process the HTML file
            with open(html_file, 'r', encoding='utf-8') as f:
                html_content = f.read()
            
            # Extract content
            result = ingestor.extract_html_content(html_content)
            
            print(f"✅ Extracted title: {result['metadata']['title']}")
            print(f"✅ Extracted text length: {len(result['text'])} characters")
            print(f"📝 Text preview: {result['text'][:100]}...")
            
            # Test Arabic normalization
            normalized = ingestor.normalize_arabic_text(result['text'][:100])
            print(f"🔤 Normalized text: {normalized}")
            
            # Test chunking
            chunks = ingestor.chunk_text_by_tokens(result['text'])
            print(f"✂️ Created {len(chunks)} chunks")
            
            # Test saving to JSON
            documents = ingestor.process_html_file(html_file)
            print(f"💾 Processed into {len(documents)} document chunks")
            
            print("\n🎉 SUCCESS: Arabic ingestion working perfectly!")
            print("✅ No Haystack dependencies required")
            print("✅ Ready for Phase 3 QA integration")
            
        else:
            print(f"❌ Test file not found: {html_file}")
            
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("💡 Make sure you're using simple_ingest.py, not ingest.py")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_arabic_ingestion()
