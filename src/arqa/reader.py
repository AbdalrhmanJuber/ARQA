"""
Reading Comprehension Module for ARQA
Handles question answering using transformer models fine-tuned for Arabic.
"""

from typing import List, Dict, Any, Optional
import torch
from transformers import (
    AutoTokenizer, 
    AutoModelForQuestionAnswering,
    pipeline
)
from haystack.nodes import FARMReader, TransformersReader


class QuestionAnswerer:
    """Handles extractive question answering for Arabic texts."""
    
    def __init__(self, 
                 model_name: str = "aubmindlab/arabert-qa",
                 max_seq_len: int = 384,
                 doc_stride: int = 128):
        """
        Initialize the question answerer.
        
        Args:
            model_name: Pretrained QA model for Arabic
            max_seq_len: Maximum sequence length for the model
            doc_stride: Stride for sliding window when text is too long
        """
        self.model_name = model_name
        self.max_seq_len = max_seq_len
        self.doc_stride = doc_stride
        
        # Initialize the QA pipeline
        self.qa_pipeline = pipeline(
            "question-answering",
            model=model_name,
            tokenizer=model_name,
            return_multiple_spans=True,
            max_answer_len=50
        )
        
        # Alternative: Use Haystack's TransformersReader
        self.reader = TransformersReader(
            model_name_or_path=model_name,
            tokenizer=model_name,
            max_seq_len=max_seq_len,
            doc_stride=doc_stride,
            use_gpu=torch.cuda.is_available()
        )
    
    def answer_question(self, 
                       question: str, 
                       context: str,
                       top_k: int = 3) -> List[Dict[str, Any]]:
        """
        Answer a question given a context using the QA pipeline.
        
        Args:
            question: Question in Arabic
            context: Context text in Arabic
            top_k: Number of answer candidates to return
            
        Returns:
            List of answer candidates with scores
        """
        try:
            # Use the transformers pipeline
            results = self.qa_pipeline(
                question=question,
                context=context,
                top_k=top_k
            )
            
            # Ensure results is a list
            if not isinstance(results, list):
                results = [results]
            
            # Format results
            formatted_results = []
            for result in results:
                formatted_results.append({
                    'answer': result['answer'],
                    'score': result['score'],
                    'start': result['start'],
                    'end': result['end']
                })
            
            return formatted_results
            
        except Exception as e:
            print(f"Error in question answering: {e}")
            return []
    
    def answer_with_documents(self, 
                             question: str, 
                             documents: List[Dict[str, Any]],
                             top_k: int = 3) -> List[Dict[str, Any]]:
        """
        Answer a question using multiple retrieved documents.
        
        Args:
            question: Question in Arabic
            documents: List of retrieved documents
            top_k: Number of answer candidates to return
            
        Returns:
            List of answers with document information
        """
        all_answers = []
        
        for doc in documents:
            context = doc.get('content', '')
            doc_meta = doc.get('meta', {})
            
            # Get answers for this document
            answers = self.answer_question(question, context, top_k)
            
            # Add document information to answers
            for answer in answers:
                answer['document_id'] = doc.get('id')
                answer['document_meta'] = doc_meta
                answer['document_score'] = doc.get('score', 0.0)
                all_answers.append(answer)
        
        # Sort by answer confidence score
        all_answers.sort(key=lambda x: x['score'], reverse=True)
        
        return all_answers[:top_k]
    
    def get_answer_span(self, text: str, start: int, end: int) -> str:
        """
        Extract answer span from text.
        
        Args:
            text: Original text
            start: Start character position
            end: End character position
            
        Returns:
            Answer text span
        """
        return text[start:end]
