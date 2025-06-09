#!/usr/bin/env python3
"""
Comprehensive test script to verify non-normalized Arabic text handling
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from arqa.reader_simple import SimpleArabicQA

def test_context_preservation():
    """Test if the context is preserved without normalization."""
    
    print("🔍 Testing context preservation...")
    
    # Original context with various Arabic characters
    original_context = """
    القاهرة هي عاصمة جمهورية مصر العربية وأكبر مدنها. 
    يقطنها تقريباً ربع سكان مصر البالغ تعدادهم حسب إحصائية عام 2006 ما يقارب 78 مليوناً إذ يقترب عدد سكانها من 16 مليون مواطن.
    مدينة القاهرة وضواحيها وجهات مختلفة من مصر وسكن منهم في القاهرة وضواحيها ما بين نصف مليون ومليون نسمة مما زاد من ازدحام المدينة التي بلغ عدد سكانها آنذاك نحو خمسة ملايين نسمة.
    """
    
    print(f"📖 Original context characters:")
    special_chars = ['إ', 'أ', 'آ', 'ة', 'ى', 'ئ', 'ؤ', 'ء', 'ً', 'ٌ', 'ٍ', 'َ', 'ُ', 'ِ']
    for char in special_chars:
        count = original_context.count(char)
        if count > 0:
            print(f"   - {char}: {count} times")
    
    # Initialize QA system
    qa_system = SimpleArabicQA()
    
    # Test different questions to get different parts of the text
    questions = [
        "كم عدد سكان مدينة القاهرة؟",
        "ما هي عاصمة مصر؟",
        "متى كان الإحصاء؟"
    ]
    
    for question in questions:
        print(f"\n🤔 Question: {question}")
        
        try:
            answers = qa_system.answer_question(question, original_context)
            
            if answers:
                for i, answer in enumerate(answers, 1):
                    answer_text = answer['answer']
                    start_pos = answer.get('start', 0)
                    end_pos = answer.get('end', 0)
                    
                    print(f"   💡 Answer {i}: '{answer_text}'")
                    print(f"      Position: {start_pos}-{end_pos}")
                    print(f"      Confidence: {answer['score']:.3f}")
                    
                    # Check what's in the original context at this position
                    if start_pos < len(original_context) and end_pos <= len(original_context):
                        original_excerpt = original_context[start_pos:end_pos]
                        print(f"      Original text at position: '{original_excerpt}'")
                        
                        if original_excerpt != answer_text:
                            print(f"      ⚠️ Answer differs from original position!")
                        else:
                            print(f"      ✅ Answer matches original position exactly!")
                    
                    # Check for preservation of special characters
                    found_chars = []
                    for char in special_chars:
                        if char in answer_text:
                            found_chars.append(char)
                    
                    if found_chars:
                        print(f"      ✅ Special characters preserved: {', '.join(found_chars)}")
                    else:
                        print(f"      ⚠️ No special Arabic characters in answer")
            else:
                print("   ❌ No answers found")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")

if __name__ == "__main__":
    test_context_preservation()
