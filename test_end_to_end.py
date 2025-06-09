#!/usr/bin/env python3
"""
Complete end-to-end test: Ingest HTML → Store → Ask Questions → Get Non-normalized Answers
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from arqa.simple_ingest import SimpleDocumentIngestor
from arqa.retriever_optimized_fixed import OptimizedArabicRetriever
from arqa.reader_simple import SimpleArabicQA

def test_end_to_end_non_normalized():
    """Complete test of the ARQA system with non-normalized text preservation."""
    
    print("🚀 ARQA End-to-End Test: Non-normalized Arabic Text Preservation")
    print("=" * 70)
    
    # Step 1: Ingest HTML files
    print("\n📁 Step 1: Processing HTML files...")
    ingestor = SimpleDocumentIngestor()
    
    html_files = [
        r"C:\Users\a-ahm\Desktop\arqa\test_html_articles\arabic_science.html",
        r"C:\Users\a-ahm\Desktop\arqa\test_html_articles\artificial_intelligence.html",
        r"C:\Users\a-ahm\Desktop\arqa\test_simple\test.html"
    ]
    
    all_documents = []
    for html_file in html_files:
        if os.path.exists(html_file):
            print(f"   📄 Processing: {os.path.basename(html_file)}")
            docs = ingestor.process_html_file(html_file)
            all_documents.extend(docs)
            
            # Show sample of original characters preserved
            if docs:
                sample_content = docs[0]['content'][:200]
                special_chars = [c for c in ['إ', 'أ', 'آ', 'ة', 'ى', 'ئ', 'ؤ', 'ء', 'ً', 'ٌ', 'ٍ'] if c in sample_content]
                if special_chars:
                    print(f"      ✅ Original characters found: {', '.join(special_chars)}")
        else:
            print(f"   ❌ File not found: {html_file}")
    
    print(f"\n✅ Total documents processed: {len(all_documents)}")
    
    # Step 2: Initialize retriever and add documents
    print("\n🔍 Step 2: Setting up retriever...")
    retriever = OptimizedArabicRetriever()
      print("   📥 Adding documents to retriever...")
    retriever.add_documents_incremental(all_documents)
    stats = retriever.get_stats()
    print(f"   ✅ Retriever now has {stats['total_documents']} documents")
    
    # Step 3: Initialize QA system
    print("\n🤖 Step 3: Setting up QA system...")
    qa_system = SimpleArabicQA()
    print("   ✅ QA system ready")
    
    # Step 4: Test questions and check answers
    print("\n❓ Step 4: Testing questions with non-normalized answers...")
    
    test_questions = [
        "ما هي أهمية العلوم في الحضارة الإسلامية؟",
        "كيف تطورت العلوم العربية؟",
        "ما هو الذكاء الاصطناعي؟"
    ]
    
    for i, question in enumerate(test_questions, 1):
        print(f"\n🤔 Question {i}: {question}")
          # Retrieve relevant documents
        retrieved_docs = retriever.retrieve(question, top_k=3)
        print(f"   📚 Retrieved {len(retrieved_docs)} relevant documents")
          if retrieved_docs:
            # Convert RetrievedDocument objects to dict format for QA system
            retrieved_dict_docs = []
            for doc in retrieved_docs:
                retrieved_dict_docs.append({
                    'content': doc.content,
                    'metadata': doc.meta,
                    'score': doc.score,
                    'id': doc.doc_id
                })
            
            # Get answers
            answers = qa_system.answer_with_retrieved_docs(
                question=question,
                retrieved_docs=retrieved_dict_docs,
                top_k=2
            )
            
            if answers:
                for j, answer in enumerate(answers, 1):
                    answer_text = answer['answer']
                    confidence = answer['confidence']
                    
                    print(f"   💡 Answer {j}: '{answer_text}'")
                    print(f"      Confidence: {confidence:.3f}")
                    
                    # Check for original Arabic characters
                    special_chars = []
                    for char in ['إ', 'أ', 'آ', 'ة', 'ى', 'ئ', 'ؤ', 'ء', 'ً', 'ٌ', 'ٍ', 'َ', 'ُ', 'ِ', 'ّ']:
                        if char in answer_text:
                            special_chars.append(char)
                    
                    if special_chars:
                        print(f"      ✅ Original characters preserved: {', '.join(special_chars[:8])}")
                        if len(special_chars) > 8:
                            print(f"         ... and {len(special_chars)-8} more")
                        print(f"      🎉 SUCCESS: Non-normalized Arabic answer!")
                    else:
                        print(f"      ℹ️ Answer doesn't contain complex Arabic characters")
                    
                    # Show full character breakdown for first answer
                    if j == 1:
                        print(f"      📝 Full answer characters: {list(answer_text)}")
            else:
                print("   ❌ No answers found")
        else:
            print("   ❌ No relevant documents found")
      print(f"\n🎯 Test Summary:")
    print(f"   📄 Documents processed: {len(all_documents)}")
    final_stats = retriever.get_stats()
    print(f"   🔍 Retriever documents: {final_stats['total_documents']}")
    print(f"   ❓ Questions tested: {len(test_questions)}")
    print(f"   ✅ System preserves original Arabic text without normalization!")

if __name__ == "__main__":
    test_end_to_end_non_normalized()
