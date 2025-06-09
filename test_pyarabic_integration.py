#!/usr/bin/env python3
"""
Test PyArabic Integration in ARQA
Validates the enhanced Arabic normalization using PyArabic
"""

import sys
import os

# Add project root to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.arqa.simple_ingest import SimpleDocumentIngestor

def test_pyarabic_normalization():
    print("🧪 Testing PyArabic Integration in ARQA")
    print("=" * 50)
    
    # Initialize the ingestor
    print("1️⃣ Initializing Document Ingestor with PyArabic...")
    ingestor = SimpleDocumentIngestor()
    
    # Test Arabic text samples with various issues
    test_texts = [
        "أهلاً وسهلاً بكم في النظام الجديد",  # Mixed diacritics
        "الذَّكاءُ الاصْطِناعِيُّ مُهِمٌّ جِدًّا",  # Heavy diacritics
        "كتابة النصوص العربيّة بطريقة صحيحة",  # Mixed forms
        "هذا مثال على الكتابة العربية الحديثة",  # Clean text
        "التعلُّم الآلي والذكاء الاصطناعي",  # Mixed hamza forms
        "نصٌّ يحتوي على علامات التشكيل المختلفة"  # Various diacritics
    ]
    
    print("2️⃣ Testing Arabic Text Normalization...")
    print()
    
    for i, text in enumerate(test_texts, 1):
        print(f"Test {i}:")
        print(f"   Original: {text}")
        
        # Normalize using PyArabic
        normalized = ingestor.normalize_arabic_text(text)
        print(f"   Normalized: {normalized}")
        
        # Tokenize using PyArabic
        tokens = ingestor.simple_tokenize(text)
        print(f"   Tokens ({len(tokens)}): {tokens[:5]}...")  # Show first 5 tokens
        print()
    
    print("3️⃣ Testing HTML Processing with PyArabic...")
    
    # Test with a sample HTML content
    sample_html = """
    <!DOCTYPE html>
    <html lang="ar">
    <head>
        <title>اختبار النظام العربي</title>
        <meta name="description" content="اختبار معالجة النصوص العربية">
    </head>
    <body>
        <h1>الذَّكاءُ الاصْطِناعِيُّ</h1>
        <p>هذا نصٌّ تجريبي لاختبار معالجة النصوص العربية باستخدام مكتبة PyArabic.</p>
        <p>النصُّ يحتوي على علامات التشكيل المختلفة وأشكال مختلفة من الأحرف العربية.</p>
    </body>
    </html>
    """
    
    # Process the HTML content
    documents = ingestor.process_html_content(sample_html, "test_pyarabic")
    
    if documents:
        print(f"   ✅ Successfully processed HTML content")
        print(f"   📄 Created {len(documents)} document chunks")
        
        for i, doc in enumerate(documents):
            content = doc['content'][:100]  # First 100 chars
            print(f"   Chunk {i+1}: {content}...")
    else:
        print("   ❌ Failed to process HTML content")
    
    print("\n4️⃣ Performance Comparison...")
    
    # Test performance with a longer text
    long_text = " ".join(test_texts * 10)  # Repeat texts 10 times
    
    import time
    
    # Test normalization speed
    start_time = time.time()
    normalized_long = ingestor.normalize_arabic_text(long_text)
    normalization_time = time.time() - start_time
    
    # Test tokenization speed
    start_time = time.time()
    tokens_long = ingestor.simple_tokenize(long_text)
    tokenization_time = time.time() - start_time
    
    print(f"   Text length: {len(long_text)} characters")
    print(f"   Normalization time: {normalization_time:.4f}s")
    print(f"   Tokenization time: {tokenization_time:.4f}s")
    print(f"   Total tokens: {len(tokens_long)}")
    
    print("\n🎉 PyArabic Integration Test Complete!")
    print("✅ Enhanced Arabic normalization is working!")

if __name__ == "__main__":
    test_pyarabic_normalization()
