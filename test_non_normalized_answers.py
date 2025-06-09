#!/usr/bin/env python3
"""
Test script to verify that the system returns non-normalized Arabic answers
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from arqa.reader_simple import SimpleArabicQA

def test_non_normalized_answers():
    """Test that answers preserve original Arabic characters."""
    
    print("🧪 Testing non-normalized Arabic answers...")
    
    # Initialize QA system
    try:
        qa_system = SimpleArabicQA()
        print("✅ QA system loaded successfully")
    except Exception as e:
        print(f"❌ Failed to load QA system: {e}")
        return
    
    # Test context with original Arabic characters (including hamza, etc.)
    original_context = """
    القاهرة هي عاصمة جمهورية مصر العربية وأكبر مدنها. 
    يقطنها تقريباً ربع سكان مصر البالغ تعدادهم حسب إحصائية عام 2006 ما يقارب 78 مليوناً إذ يقترب عدد سكانها من 16 مليون مواطن.
    سكن منهم في القاهرة وضواحيها ما بين نصف مليون ومليون نسمة مما زاد من ازدحام المدينة.
    """
    
    # Test question
    question = "كم عدد سكان مدينة القاهرة؟"
    
    print(f"\n🤔 Question: {question}")
    print(f"📖 Context contains original characters like: إذ، مليوناً، إحصائية")
    
    # Get answer
    try:
        answers = qa_system.answer_question(question, original_context)
        
        if answers:
            for i, answer in enumerate(answers, 1):
                answer_text = answer['answer']
                confidence = answer['score']
                
                print(f"\n💡 Answer {i}: {answer_text}")
                print(f"   Confidence: {confidence:.3f}")
                
                # Check if answer contains original characters
                if 'إذ' in answer_text or 'مليوناً' in answer_text or 'إحصائية' in answer_text:
                    print("   ✅ Answer preserves original Arabic characters!")
                else:
                    print("   ⚠️ Answer may be normalized")
                
                # Show character analysis
                print(f"   Original characters found:")
                for char in ['إ', 'أ', 'آ', 'ة', 'ى', 'ئ', 'ؤ', 'ء']:
                    if char in answer_text:
                        print(f"     - {char} found in answer")
        else:
            print("❌ No answers found")
            
    except Exception as e:
        print(f"❌ Error during question answering: {e}")

if __name__ == "__main__":
    test_non_normalized_answers()
