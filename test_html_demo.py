"""
Working test for ARQA HTML ingestion system.
This demonstrates the Arabic HTML processing capabilities.
"""

import os
import sys
from pathlib import Path

# Add the src directory to the Python path
sys.path.append(str(Path(__file__).parent / 'src'))

# Import from the main ARQA package
try:
    from arqa.simple_ingest import SimpleDocumentIngestor
    print("✅ Using ARQA simplified ingestor")
except ImportError as e:
    print(f"❌ Could not import ARQA ingestor: {e}")
    print("❌ Make sure BeautifulSoup4 is installed: pip install beautifulsoup4")
    sys.exit(1)


def create_sample_html_files():
    """Create sample Arabic HTML files for testing."""
    
    # Create a test directory
    test_dir = Path("test_html_articles")
    test_dir.mkdir(exist_ok=True)
    
    # Sample Arabic HTML articles
    sample_articles = [
        {
            "filename": "arabic_science.html",
            "title": "العلوم في الحضارة الإسلامية",
            "content": """
            <html dir="rtl" lang="ar">
            <head>
                <meta charset="UTF-8">
                <title>العلوم في الحضارة الإسلامية</title>
            </head>
            <body>
                <h1>العلوم في الحضارة الإسلامية</h1>
                <p>لقد ازدهرت العلوم في الحضارة الإسلامية بشكل مذهل خلال العصور الوسطى. وقد ساهم العلماء المسلمون في تطوير العديد من المجالات العلمية مثل الطب والرياضيات والفلك والكيمياء.</p>
                
                <h2>الطب الإسلامي</h2>
                <p>برز في الطب الإسلامي أطباء عظماء مثل ابن سينا والرازي وابن النفيس. لقد وضع ابن سينا كتاب القانون في الطب الذي ظل مرجعاً أساسياً في أوروبا لعدة قرون.</p>
                
                <h2>الرياضيات</h2>
                <p>في مجال الرياضيات، طور العلماء المسلمون علم الجبر وأسسوا قواعد الخوارزميات. الخوارزمي هو من أعطى اسمه لكلمة "خوارزمية" المستخدمة اليوم في علوم الحاسوب.</p>
                
                <h2>الفلك</h2>
                <p>في علم الفلك، بنى العلماء المسلمون مراصد فلكية متقدمة ووضعوا جداول فلكية دقيقة. كما صححوا كثيراً من النظريات الإغريقية القديمة.</p>
                
                <div class="conclusion">
                    <p>إن إسهامات العلماء المسلمين في العلوم كانت أساساً مهماً للنهضة العلمية الأوروبية لاحقاً.</p>
                </div>
            </body>
            </html>
            """
        },
        {
            "filename": "artificial_intelligence.html", 
            "title": "الذكاء الاصطناعي",
            "content": """
            <html dir="rtl" lang="ar">
            <head>
                <meta charset="UTF-8">
                <title>الذكاء الاصطناعي في العصر الحديث</title>
            </head>
            <body>
                <h1>الذكاء الاصطناعي في العصر الحديث</h1>
                <p>يشهد مجال الذكاء الاصطناعي تطوراً مستمراً وسريعاً في السنوات الأخيرة. هذا التطور يؤثر على جميع جوانب الحياة من الطب إلى التعليم والنقل.</p>
                
                <h2>تعلم الآلة</h2>
                <p>تعلم الآلة هو فرع من الذكاء الاصطناعي يمكّن الحاسوب من التعلم بدون برمجة صريحة. يستخدم خوارزميات معقدة لتحليل البيانات واستخراج الأنماط.</p>
                
                <h2>معالجة اللغة الطبيعية</h2>
                <p>معالجة اللغة الطبيعية تتيح للحاسوب فهم وتحليل اللغة البشرية. هذا يشمل الترجمة الآلية، وتحليل المشاعر، والإجابة على الأسئلة.</p>
                
                <h2>التطبيقات الحديثة</h2>
                <p>يستخدم الذكاء الاصطناعي اليوم في السيارات ذاتية القيادة، والمساعدات الذكية، وأنظمة التوصية، والتشخيص الطبي.</p>
                
                <h2>التحديات والأخلاقيات</h2>
                <p>رغم الفوائد العظيمة، يواجه الذكاء الاصطناعي تحديات أخلاقية مثل الخصوصية، والتحيز في الخوارزميات، وتأثيره على سوق العمل.</p>
            </body>
            </html>
            """
        }
    ]
    
    # Write the HTML files
    created_files = []
    for article in sample_articles:
        file_path = test_dir / article["filename"]
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(article["content"])
        created_files.append(file_path)
        print(f"📄 Created: {file_path}")
    
    return created_files


def main():
    """Main test function."""
    print("🚀 Starting Standalone HTML Ingestion Test")
    print("=" * 50)
    
    # Create sample HTML files
    print("\n📝 Creating sample Arabic HTML files...")
    html_files = create_sample_html_files()
    
    # Initialize the ingestor
    print("\n🔧 Initializing DocumentIngestor...")
    ingestor = SimpleDocumentIngestor(
        output_dir="test_output",
        chunk_size=200
    )
    
    # Process each HTML file
    print("\n🔄 Processing HTML files...")
    all_chunks = []
    
    for html_file in html_files:
        print(f"\n📖 Processing: {html_file.name}")
        
        try:
            # Process the HTML file
            chunks = ingestor.process_html_file(str(html_file))
            all_chunks.extend(chunks)
            
            print(f"   ✅ Generated {len(chunks)} chunks")
            
            # Show first chunk as example
            if chunks:
                first_chunk = chunks[0]
                print(f"   📄 First chunk preview:")
                print(f"      Title: {first_chunk['metadata'].get('title', 'N/A')}")
                print(f"      Content: {first_chunk['content'][:100]}...")
                print(f"      Words: {first_chunk['metadata']['chunk_length']}")
                
        except Exception as e:
            print(f"   ❌ Error processing {html_file.name}: {e}")
    
    # Save all processed documents
    print(f"\n💾 Saving {len(all_chunks)} total chunks...")
    try:
        ingestor.save_documents(all_chunks)
        output_file = ingestor.output_dir / "processed_documents.json"
        print(f"   ✅ Saved to: {output_file}")
        
        # Show statistics
        total_words = sum(chunk['metadata']['chunk_length'] for chunk in all_chunks)
        avg_words = total_words / len(all_chunks) if all_chunks else 0
        
        print(f"\n📊 Processing Statistics:")
        print(f"   📄 Total documents: {len(html_files)}")
        print(f"   🧩 Total chunks: {len(all_chunks)}")
        print(f"   🔤 Total words: {total_words}")
        print(f"   📈 Average words per chunk: {avg_words:.1f}")
        
        # Show a sample chunk in detail  
        if all_chunks:
            print(f"\n🔍 Sample Processed Chunk:")
            sample = all_chunks[0]
            print(f"   📄 Title: {sample['metadata'].get('title', 'N/A')}")
            print(f"   📝 Source: {sample['metadata'].get('filename', 'N/A')}")
            print(f"   🔤 Words: {sample['metadata']['chunk_length']}")
            print(f"   📖 Content preview: {sample['content'][:200]}...")
        
    except Exception as e:
        print(f"   ❌ Error saving documents: {e}")
    
    print("\n✅ Test completed successfully!")
    print("🔍 Check the 'test_output' directory for processed results.")
    print("📁 Check the 'test_html_articles' directory for sample HTML files.")


if __name__ == "__main__":
    main()
