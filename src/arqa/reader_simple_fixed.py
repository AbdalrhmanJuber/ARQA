"""
Simple Question Answering Module for ARQA
Handles Arabic question answering using transformers without Haystack dependency.
"""

from typing import List, Dict, Any, Optional, Tuple
import re
import torch
from transformers import pipeline
from tqdm import tqdm
import warnings

# Suppress some warnings for cleaner output
warnings.filterwarnings("ignore", category=UserWarning)


class SimpleArabicQA:
    """
    Simple Arabic Question Answering system using transformer models.
    Works without Haystack dependency.
    """
    
    def __init__(self, 
                 model_name: str = "deepset/xlm-roberta-large-squad2",
                 max_seq_len: int = 512,
                 doc_stride: int = 128,
                 max_answer_len: int = 100):
        """
        Initialize the Arabic QA system.
        
        Args:
            model_name: Pre-trained multilingual QA model (supports Arabic)
            max_seq_len: Maximum sequence length
            doc_stride: Stride for sliding window
            max_answer_len: Maximum answer length
        """
        self.model_name = model_name
        self.max_seq_len = max_seq_len
        self.doc_stride = doc_stride
        self.max_answer_len = max_answer_len
        
        print(f"🔄 Loading multilingual QA model: {model_name}")
        
        try:
            # Create QA pipeline directly (handles model and tokenizer loading)
            self.qa_pipeline = pipeline(
                "question-answering",
                model=model_name,
                device=0 if torch.cuda.is_available() else -1,
                max_answer_len=max_answer_len
            )
            
            print(f"✅ Model loaded successfully!")
            print(f"   Device: {'GPU' if torch.cuda.is_available() else 'CPU'}")
            print(f"   Model supports Arabic text processing")
            
        except Exception as e:
            print(f"❌ Error loading model: {e}")
            print("🔄 Falling back to a different model...")
            
            # Fallback to a smaller multilingual model
            try:
                self.model_name = "deepset/xlm-roberta-base-squad2"
                self.qa_pipeline = pipeline(
                    "question-answering",
                    model=self.model_name,
                    device=0 if torch.cuda.is_available() else -1,
                    max_answer_len=max_answer_len
                )
                print(f"✅ Fallback model loaded: {self.model_name}")
                
            except Exception as e2:
                print(f"❌ Error loading fallback model: {e2}")
                
                # Final fallback to basic distilbert
                try:
                    self.model_name = "distilbert-base-cased-distilled-squad"
                    self.qa_pipeline = pipeline(
                        "question-answering",
                        model=self.model_name,
                        device=0 if torch.cuda.is_available() else -1,
                        max_answer_len=max_answer_len
                    )
                    print(f"✅ Final fallback model loaded: {self.model_name}")
                    print(f"⚠️ Note: This model may have limited Arabic support")
                    
                except Exception as e3:
                    print(f"❌ Error loading final fallback: {e3}")
                    raise RuntimeError("Could not load any QA model")
    
    def normalize_arabic_text(self, text: str) -> str:
        """Normalize Arabic text for better processing."""
        if not text:
            return text
        
        # Basic Arabic normalization
        text = re.sub(r'[إأآا]', 'ا', text)  # Normalize Alef
        text = re.sub(r'ة', 'ه', text)       # Normalize Ta Marbuta
        text = re.sub(r'ئ', 'ي', text)       # Normalize Ya
        text = re.sub(r'ؤ', 'و', text)       # Normalize Waw
        
        # Remove extra whitespace
        text = ' '.join(text.split())
        
        return text
    
    def answer_question(self, 
                       question: str, 
                       context: str,
                       top_k: int = 3,
                       min_score: float = 0.1) -> List[Dict[str, Any]]:
        """
        Answer a question given context text.
        
        Args:
            question: Question in Arabic
            context: Context text in Arabic
            top_k: Number of answer candidates to return
            min_score: Minimum confidence score
            
        Returns:
            List of answer candidates with scores
        """
        if not question.strip() or not context.strip():
            return []
        
        # Normalize inputs
        question = self.normalize_arabic_text(question)
        context = self.normalize_arabic_text(context)
        
        try:
            # Process with the QA pipeline
            result = self.qa_pipeline(
                question=question,
                context=context
            )
            
            # Check if result meets minimum score requirement
            if isinstance(result, list):
                return [r for r in result if r.get('score', 0) >= min_score][:top_k]
            elif result.get('score', 0) >= min_score:
                return [result]
            else:
                return []
                    
        except Exception as e:
            print(f"❌ Error in question answering: {e}")
            return []
    
    def answer_with_retrieved_docs(self, 
                                  question: str, 
                                  retrieved_docs: List[Dict[str, Any]],
                                  top_k: int = 3,
                                  combine_scores: bool = True) -> List[Dict[str, Any]]:
        """
        Answer question using multiple retrieved documents.
        
        Args:
            question: Question in Arabic
            retrieved_docs: Documents from retriever
            top_k: Number of answers to return
            combine_scores: Whether to combine retrieval and QA scores
            
        Returns:
            List of answers with document information
        """
        all_answers = []
        
        print(f"🔍 Processing {len(retrieved_docs)} retrieved documents...")
        
        for i, doc in enumerate(tqdm(retrieved_docs, desc="Answering")):
            doc_content = doc.get('content', '')
            doc_meta = doc.get('metadata', {})
            retrieval_score = doc.get('score', 0.0)
            
            if not doc_content.strip():
                continue
            
            # Get answers from this document
            answers = self.answer_question(question, doc_content, top_k=2)
            
            # Add document information to answers
            for answer in answers:
                enhanced_answer = {
                    'answer': answer['answer'],
                    'confidence': answer['score'],
                    'retrieval_score': retrieval_score,
                    'document_id': doc.get('id', f'doc_{i}'),
                    'document_title': doc_meta.get('title', 'Unknown'),
                    'document_url': doc_meta.get('url', ''),
                    'answer_start': answer.get('start', 0),
                    'answer_end': answer.get('end', 0),
                    'context_snippet': self._get_context_snippet(
                        doc_content, 
                        answer.get('start', 0), 
                        answer.get('end', 0)
                    )
                }
                
                # Combine scores if requested
                if combine_scores:
                    enhanced_answer['combined_score'] = (
                        answer['score'] * 0.7 + retrieval_score * 0.3
                    )
                else:
                    enhanced_answer['combined_score'] = answer['score']
                
                all_answers.append(enhanced_answer)
        
        # Sort by combined score
        all_answers.sort(key=lambda x: x['combined_score'], reverse=True)
        
        return all_answers[:top_k]
    
    def _get_context_snippet(self, text: str, start: int, end: int, 
                           snippet_length: int = 200) -> str:
        """Get context snippet around the answer."""
        if not text or start < 0 or end <= start:
            return ""
        
        # Extend context around the answer
        context_start = max(0, start - snippet_length // 2)
        context_end = min(len(text), end + snippet_length // 2)
        
        snippet = text[context_start:context_end]
        
        # Add ellipsis if truncated
        if context_start > 0:
            snippet = "..." + snippet
        if context_end < len(text):
            snippet = snippet + "..."
        
        return snippet.strip()
    
    def batch_answer(self, 
                    questions: List[str], 
                    contexts: List[str]) -> List[List[Dict[str, Any]]]:
        """
        Answer multiple questions with their respective contexts.
        
        Args:
            questions: List of questions
            contexts: List of contexts (same length as questions)
            
        Returns:
            List of answer lists for each question
        """
        if len(questions) != len(contexts):
            raise ValueError("Questions and contexts must have same length")
        
        results = []
        
        for question, context in tqdm(zip(questions, contexts), 
                                    desc="Batch answering",
                                    total=len(questions)):
            answers = self.answer_question(question, context)
            results.append(answers)
        
        return results


def create_arabic_qa_system(model_name: Optional[str] = None) -> SimpleArabicQA:
    """
    Factory function to create Arabic QA system.
    
    Args:
        model_name: Optional model name override
        
    Returns:
        Initialized SimpleArabicQA instance
    """
    if model_name is None:
        # Try different models in order of preference for Arabic support
        models_to_try = [
            "deepset/xlm-roberta-large-squad2",    # Best multilingual QA model
            "deepset/xlm-roberta-base-squad2",     # Smaller multilingual QA model
            "distilbert-base-cased-distilled-squad"  # Basic fallback
        ]
        
        for model in models_to_try:
            try:
                return SimpleArabicQA(model_name=model)
            except Exception as e:
                print(f"⚠️ Failed to load {model}: {e}")
                continue
        
        raise RuntimeError("Could not load any QA model")
    else:
        return SimpleArabicQA(model_name=model_name)


# Example usage
if __name__ == "__main__":
    # Test the QA system
    qa = create_arabic_qa_system()
    
    # Test Arabic QA
    question = "ما هو عاصمة مصر؟"
    context = "القاهرة هي عاصمة جمهورية مصر العربية وأكبر مدنها. تقع على ضفاف نهر النيل في شمال مصر."
    
    answers = qa.answer_question(question, context)
    
    print(f"\n🤔 Question: {question}")
    print(f"📖 Context: {context}")
    print(f"\n💡 Answers:")
    
    for i, answer in enumerate(answers, 1):
        print(f"   {i}. {answer['answer']} (confidence: {answer['score']:.3f})")
