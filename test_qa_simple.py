#!/usr/bin/env python3
"""
Simple test to verify Arabic QA functionality.
"""

import sys
import os
sys.path.append(os.path.abspath('.'))

def test_import():
    """Test if we can import the QA module."""
    try:
        from src.arqa.reader_simple import SimpleArabicQA, create_arabic_qa_system
        print("✅ Successfully imported Arabic QA modules")
        return True
    except Exception as e:
        print(f"❌ Error importing modules: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_basic_qa():
    """Test basic QA functionality."""
    try:
        from src.arqa.reader_simple import create_arabic_qa_system
        
        print("🔄 Loading Arabic QA model...")
        qa = create_arabic_qa_system()
        
        # Simple test
        question = "ما هو عاصمة مصر؟"
        context = "القاهرة هي عاصمة مصر وأكبر مدنها."
        
        print(f"🤔 Question: {question}")
        print(f"📖 Context: {context}")
        
        answers = qa.answer_question(question, context)
        
        if answers:
            print(f"✅ Got {len(answers)} answer(s):")
            for i, answer in enumerate(answers, 1):
                print(f"   {i}. '{answer['answer']}' (confidence: {answer['score']:.3f})")
            return True
        else:
            print("❌ No answers found")
            return False
            
    except Exception as e:
        print(f"❌ Error in QA test: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 Simple Arabic QA Test")
    print("=" * 40)
    
    # Test imports
    if not test_import():
        sys.exit(1)
    
    print("\n" + "=" * 40)
    
    # Test basic functionality
    if test_basic_qa():
        print("\n✅ Simple QA test passed!")
        sys.exit(0)
    else:
        print("\n❌ Simple QA test failed!")
        sys.exit(1)
