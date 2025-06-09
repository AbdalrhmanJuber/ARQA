#!/usr/bin/env python3
"""
Simple test for Arabic QA system with proper model
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from arqa.reader_simple import SimpleArabicQA

def test_arabic_qa_model():
    """Test the Arabic QA system directly"""
    print("🧪 Testing Arabic QA System")
    print("=" * 40)
    
    # Test QA system initialization
    print("\n🤔 Step 1: QA System Setup")
    try:
        qa_system = SimpleArabicQA()
        print("   ✅ QA system initialized successfully")
        print(f"   📦 Model: {qa_system.model_name}")
    except Exception as e:
        print(f"   ❌ QA system initialization failed: {e}")
        return
    
    # Test Arabic question answering
    print("\n🎯 Step 2: Testing Arabic QA")
    
    # Test questions and contexts in Arabic
    test_cases = [
        {
            "question": "ما هو عاصمة مصر؟",
            "context": "القاهرة هي عاصمة جمهورية مصر العربية وأكبر مدنها. تقع على ضفاف نهر النيل في شمال مصر."
        },
        {
            "question": "ما هو الذكاء الاصطناعي؟",
            "context": "الذكاء الاصطناعي هو محاولة لتطوير أنظمة الحاسوب لتحاكي قدرات الذكاء البشري. يشمل التعلم الآلي والشبكات العصبية."
        },
        {
            "question": "كم عدد الكواكب في النظام الشمسي؟",
            "context": "النظام الشمسي يحتوي على ثمانية كواكب رئيسية وهي عطارد والزهرة والأرض والمريخ والمشتري وزحل وأورانوس ونبتون."
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n--- Test Case {i} ---")
        question = test_case["question"]
        context = test_case["context"]
        
        print(f"❓ Question: {question}")
        print(f"📖 Context: {context[:60]}...")
        
        try:
            answers = qa_system.answer_question(question, context, min_score=0.01)  # Lower threshold
            
            if answers:
                print("💡 Answers found:")
                for j, answer in enumerate(answers, 1):
                    print(f"   {j}. {answer['answer']}")
                    print(f"      Confidence: {answer['score']:.3f}")
                    if 'start' in answer and 'end' in answer:
                        print(f"      Position: {answer['start']}-{answer['end']}")
            else:
                print("   ⚠️ No confident answers found")
                
        except Exception as e:
            print(f"   ❌ Error processing question: {e}")
    
    # Test the factory function
    print(f"\n🏭 Step 3: Testing Factory Function")
    try:
        from arqa.reader_simple import create_arabic_qa_system
        qa_system2 = create_arabic_qa_system()
        print(f"   ✅ Factory function works: {qa_system2.model_name}")
    except Exception as e:
        print(f"   ❌ Factory function failed: {e}")
    
    print("\n🎉 Arabic QA Test Complete!")
    print("=" * 40)

if __name__ == "__main__":
    test_arabic_qa_model()
