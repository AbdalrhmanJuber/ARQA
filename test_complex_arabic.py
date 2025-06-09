#!/usr/bin/env python3
"""
Test script to force extraction of text with complex Arabic characters
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from arqa.reader_simple import SimpleArabicQA

def test_complex_arabic_extraction():
    """Test extraction of answers with complex Arabic characters."""
    
    print("🧪 Testing complex Arabic character extraction...")
    
    # Context designed to force extraction of text with complex characters
    test_context = """
    في دراسةٍ حديثةٍ أُجريت عام 2006، تبيّن أنّ عدد سكان القاهرة يبلغ تقريباً ستة عشر مليوناً.
    وقد أشارت الإحصائيّة إلى أنّ هذا الرقم قد ازداد بنسبةٍ كبيرةٍ منذ التسعينيّات.
    المدينة التي تُعرف باسم "أمّ الدنيا" تضمّ أحياءً متنوّعةً وأسواقاً شعبيّةً مميّزةً.
    """
    
    print(f"📖 Context contains complex characters:")
    complex_chars = ['ٍ', 'ُ', 'َ', 'ّ', 'ً', 'ٌ', 'أُ', 'إ', 'آ', 'ة', 'ى', 'ئ', 'ؤ']
    for char in complex_chars:
        count = test_context.count(char)
        if count > 0:
            print(f"   - {char}: {count} times")
    
    qa_system = SimpleArabicQA()
    
    # Questions designed to extract text with complex characters
    test_questions = [
        "كم عدد سكان القاهرة حسب الدراسة؟",
        "ماذا تُعرف القاهرة؟",
        "متى أُجريت الدراسة؟",
        "ما نوع الأحياء في المدينة؟"
    ]
    
    for question in test_questions:
        print(f"\n🤔 Question: {question}")
        
        try:
            answers = qa_system.answer_question(question, test_context)
            
            if answers:
                for i, answer in enumerate(answers, 1):
                    answer_text = answer['answer']
                    confidence = answer['score']
                    
                    print(f"   💡 Answer {i}: '{answer_text}'")
                    print(f"      Confidence: {confidence:.3f}")
                    
                    # Check for complex characters in the answer
                    found_complex_chars = []
                    for char in complex_chars:
                        if char in answer_text:
                            found_complex_chars.append(char)
                    
                    if found_complex_chars:
                        print(f"      ✅ Complex characters preserved: {', '.join(found_complex_chars)}")
                        print(f"      🎉 SUCCESS: Non-normalized answer with original Arabic text!")
                    else:
                        print(f"      ℹ️ Answer doesn't contain complex characters")
                        
                    # Show character-by-character analysis
                    print(f"      Character analysis: {[c for c in answer_text]}")
            else:
                print("   ❌ No answers found")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")

if __name__ == "__main__":
    test_complex_arabic_extraction()
