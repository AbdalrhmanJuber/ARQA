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
                 model_name: str = "zohaib99k/Bert_Arabic-SQuADv2-QA",
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
                self.model_name = "distilbert-base-cased-distilled-squad"
                self.qa_pipeline = pipeline(
                    "question-answering",
                    model=self.model_name,
                    device=0 if torch.cuda.is_available() else -1,
                    max_answer_len=max_answer_len
                )
                print(f"✅ Fallback model loaded: {self.model_name}")
                
            except Exception as fallback_error:
                print(f"❌ Fallback also failed: {fallback_error}")
                raise RuntimeError(f"Could not load any QA model. Original error: {e}")
    
    def normalize_arabic_text(self, text: str) -> str:
        """
        Basic Arabic text normalization.
        
        Args:
            text: Input Arabic text
            
        Returns:
            Normalized text
        """
        if not text:
            return ""
        
        # Basic Arabic text normalization
        # Remove diacritics (tashkeel)
        text = re.sub(r'[\u064B-\u065F\u0670\u0640]', '', text)
        
        # Normalize some Arabic characters
        text = re.sub(r'[أإآ]', 'ا', text)  # Normalize Alif
        text = re.sub(r'[ىئ]', 'ي', text)   # Normalize Ya
        text = re.sub(r'ة', 'ه', text)      # Normalize Ta Marbuta
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
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
        
        # Keep original context to preserve non-normalized answers
        # Only normalize question for better matching (optional)
        original_context = context
        normalized_question = self.normalize_arabic_text(question)
        
        try:
            # Process with the QA pipeline using original context
            result = self.qa_pipeline({
                'question': normalized_question,
                'context': original_context
            })
            
            # The pipeline returns a single dict, not a list
            if isinstance(result, dict) and result.get('score', 0) >= min_score:
                return [result]  # Return as list for consistency
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
            answers = self.answer_question(question, doc_content, top_k=2, min_score=0.01)
            
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
            "ZeyadAhmed/AraElectra-Arabic-SQuADv2-QA",
            "deepset/xlm-roberta-base-squad2",                   # Multilingual QA model (supports Arabic)
            "aubmindlab/bert-base-arabertv02",                   # AraBERT base model
            "asafaya/bert-base-arabic",                          # Arabic BERT alternative
            "distilbert-base-cased-distilled-squad",
            "zohaib99k/Bert_Arabic-SQuADv2-QA"
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
