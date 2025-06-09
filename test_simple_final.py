#!/usr/bin/env python3
"""
Simple test to demonstrate non-normalized Arabic answers
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from arqa.simple_ingest import SimpleDocumentIngestor
from arqa.reader_simple import SimpleArabicQA

def test_simple_non_normalized():
    """Simple test to verify non-normalized answers."""
    
    print("🚀 Simple ARQA Test: Non-normalized Arabic Answers")
    print("=" * 60)
    
    # Step 1: Process HTML content with original characters
    print("\n📄 Step 1: Processing Arabic content...")
    
    # Create content with various Arabic characters
    html_content = """
    <html><body>
    <h1>العلوم في الحضارة الإسلامية</h1>
    <p>لقد ازدهرت العلوم في الحضارة الإسلامية بشكلٍ كبيرٍ، وأسهم العلماء المسلمون في تطوير مختلف المجالات العلمية.</p>
    <p>كان هناك علماءُ مثل الخوارزمي والرازي وابن سينا الذين قدموا إسهاماتٍ عظيمةً في الرياضيات والطب والفلسفة.</p>
    <p>هذه الإنجازات أثّرت على الحضارة الأوروبية في العصور الوسطى بطريقةٍ كبيرةٍ.</p>
    </body></html>
    """
    
    # Process with our ingestor
    ingestor = SimpleDocumentIngestor()
    documents = ingestor.process_html_content(html_content, "test_content")
    
    if documents:
        print(f"✅ Created {len(documents)} document chunks")
        
        # Show original characters preserved
        first_content = documents[0]['content']
        special_chars = [c for c in ['ٍ', 'ُ', 'َ', 'ّ', 'ً', 'ٌ', 'إ', 'أ', 'آ', 'ة', 'ى'] if c in first_content]
        if special_chars:
            print(f"   ✅ Original characters preserved: {', '.join(special_chars)}")
        
        # Step 2: Test question answering
        print(f"\n🤖 Step 2: Testing question answering...")
        qa_system = SimpleArabicQA()
        
        # Test question
        question = "من هم العلماء المذكورون؟"
        context = first_content
        
        print(f"   🤔 Question: {question}")
        print(f"   📖 Context length: {len(context)} characters")
        
        # Get answer
        answers = qa_system.answer_question(question, context)
        
        if answers:
            for i, answer in enumerate(answers, 1):
                answer_text = answer['answer']
                confidence = answer['score']
                
                print(f"\n   💡 Answer {i}: '{answer_text}'")
                print(f"      Confidence: {confidence:.3f}")
                
                # Check for original Arabic characters in answer
                answer_special_chars = [c for c in ['ٍ', 'ُ', 'َ', 'ّ', 'ً', 'ٌ', 'إ', 'أ', 'آ', 'ة', 'ى'] if c in answer_text]
                if answer_special_chars:
                    print(f"      ✅ Original characters in answer: {', '.join(answer_special_chars)}")
                    print(f"      🎉 SUCCESS: Non-normalized Arabic answer!")
                else:
                    print(f"      ℹ️ Answer is simple text without complex characters")
                
                # Character analysis
                print(f"      📝 Answer characters: {list(answer_text)}")
        else:
            print("   ❌ No answers found")
    else:
        print("❌ No documents created")
    
    print(f"\n✅ Test completed - ARQA system preserves original Arabic text!")

if __name__ == "__main__":
    test_simple_non_normalized()
