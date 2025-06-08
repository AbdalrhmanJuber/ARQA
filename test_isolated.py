"""
Completely isolated test - imports the module directly without going through the package.
"""

import sys
from pathlib import Path

# Add the src/arqa directory directly to path
arqa_path = Path(__file__).parent / 'src' / 'arqa'
sys.path.insert(0, str(arqa_path))

# Import the module directly
try:
    import simple_ingest
    SimpleDocumentIngestor = simple_ingest.SimpleDocumentIngestor
    print("✅ Direct import successful!")
except ImportError as e:
    print(f"❌ Direct import failed: {e}")
    sys.exit(1)

def create_test_html():
    """Create a simple test HTML file."""
    test_dir = Path("test_simple")
    test_dir.mkdir(exist_ok=True)
    
    html_content = """
    <html>
    <head><title>اختبار بسيط</title></head>
    <body>
        <h1>اختبار النظام</h1>
        <p>هذا اختبار بسيط للنظام العربي.</p>
        <p>النظام يعمل بشكل جيد.</p>
    </body>
    </html>
    """
    
    test_file = test_dir / "test.html"
    with open(test_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    return test_file

def main():
    print("🚀 Isolated Test - Arabic HTML Processing")
    print("=" * 45)
    
    # Create test file
    html_file = create_test_html()
    print(f"📄 Created test file: {html_file}")
    
    # Initialize processor
    processor = SimpleDocumentIngestor(output_dir="test_simple_output")
    
    # Process the file
    print("\n🔄 Processing HTML file...")
    try:
        chunks = processor.process_html_file(str(html_file))
        print(f"✅ Success! Generated {len(chunks)} chunks")
        
        if chunks:
            chunk = chunks[0]
            print(f"\n📄 Result:")
            print(f"   Title: {chunk['metadata'].get('title', 'N/A')}")
            print(f"   Content: {chunk['content'][:100]}...")
            print(f"   Words: {chunk['metadata']['chunk_length']}")
            
        # Save results
        processor.save_documents(chunks)
        print(f"\n💾 Saved to: {processor.output_dir}/processed_documents.json")
        
    except Exception as e:
        print(f"❌ Processing failed: {e}")
        return
    
    print("\n✅ Isolated test completed successfully!")

if __name__ == "__main__":
    main()
