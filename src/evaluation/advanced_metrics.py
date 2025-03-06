import numpy as np
from typing import Dict, List, Optional, Union
from nltk.translate.bleu_score import sentence_bleu, SmoothingFunction
from bert_score import score as bert_score
import torch
import spacy
from collections import Counter
import re

# Load language model for factual consistency metrics
try:
    nlp = spacy.load('en_core_web_sm')
except:
    print("Please install spaCy model: python -m spacy download en_core_web_sm")
    nlp = None

class AdvancedMetrics:
    """Advanced evaluation metrics beyond basic similarity"""
    
    def __init__(self):
        """Initialize advanced metrics components"""
        self.smoothing = SmoothingFunction().method1
        
    def entity_precision_recall(self, reference: str, candidate: str) -> Dict[str, float]:
        """Calculate precision and recall of named entities between reference and candidate"""
        if not nlp:
            return {'entity_precision': 0.0, 'entity_recall': 0.0, 'entity_f1': 0.0}
            
        ref_doc = nlp(reference)
        cand_doc = nlp(candidate)
        
        ref_entities = set([ent.text.lower() for ent in ref_doc.ents])
        cand_entities = set([ent.text.lower() for ent in cand_doc.ents])
        
        if not ref_entities and not cand_entities:
            return {'entity_precision': 1.0, 'entity_recall': 1.0, 'entity_f1': 1.0}
            
        if not cand_entities:
            return {'entity_precision': 0.0, 'entity_recall': 0.0, 'entity_f1': 0.0}
            
        if not ref_entities:
            return {'entity_precision': 0.0, 'entity_recall': 1.0, 'entity_f1': 0.0}
            
        common_entities = ref_entities.intersection(cand_entities)
        
        precision = len(common_entities) / len(cand_entities) if cand_entities else 0
        recall = len(common_entities) / len(ref_entities) if ref_entities else 0
        f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0
        
        return {'entity_precision': precision, 'entity_recall': recall, 'entity_f1': f1}
    
    def numeric_accuracy(self, reference: str, candidate: str) -> Dict[str, float]:
        """Check for numerical consistency between reference and candidate texts"""
        # Extract numbers from texts
        ref_nums = set(re.findall(r'\b\d+(?:\.\d+)?\b', reference))
        cand_nums = set(re.findall(r'\b\d+(?:\.\d+)?\b', candidate))
        
        if not ref_nums:
            return {'numeric_precision': 1.0 if not cand_nums else 0.0, 'numeric_recall': 1.0}
        
        if not cand_nums:
            return {'numeric_precision': 1.0, 'numeric_recall': 0.0}
        
        # Calculate precision and recall
        common_nums = ref_nums.intersection(cand_nums)
        precision = len(common_nums) / len(cand_nums) if cand_nums else 1.0
        recall = len(common_nums) / len(ref_nums) if ref_nums else 1.0
        
        return {'numeric_precision': precision, 'numeric_recall': recall}
    
    def calculate_bleu(self, reference: str, candidate: str) -> float:
        """Calculate BLEU score with smoothing for better handling of short texts"""
        ref_tokens = [reference.split()]  # BLEU expects list of references
        cand_tokens = candidate.split()
        
        if not cand_tokens or not ref_tokens[0]:
            return 0.0
            
        # Use smoothing for better results on short texts
        return sentence_bleu(ref_tokens, cand_tokens, smoothing_function=self.smoothing)
    
    def factual_consistency(self, context: str, reference: str, candidate: str) -> Dict[str, float]:
        """Evaluate factual consistency against the provided context"""
        if not nlp or not context.strip():
            return {'fact_consistency': 0.5}  # Neutral score if no context or spaCy
        
        context_doc = nlp(context)
        
        # Extract key facts (entities, numerical values, key phrases)
        context_entities = set([ent.text.lower() for ent in context_doc.ents])
        context_numbers = set(re.findall(r'\b\d+(?:\.\d+)?\b', context))
        context_noun_chunks = set([chunk.text.lower() for chunk in context_doc.noun_chunks])
        
        # Calculate how well candidate captures these compared to reference
        # First check reference against context
        ref_doc = nlp(reference)
        ref_entities = set([ent.text.lower() for ent in ref_doc.ents])
        ref_numbers = set(re.findall(r'\b\d+(?:\.\d+)?\b', reference))
        ref_noun_chunks = set([chunk.text.lower() for chunk in ref_doc.noun_chunks])
        
        # Then check candidate against context
        cand_doc = nlp(candidate)
        cand_entities = set([ent.text.lower() for ent in cand_doc.ents])
        cand_numbers = set(re.findall(r'\b\d+(?:\.\d+)?\b', candidate))
        cand_noun_chunks = set([chunk.text.lower() for chunk in cand_doc.noun_chunks])
        
        # Calculate overlap with context
        if context_entities:
            ref_entity_recall = len(ref_entities.intersection(context_entities)) / len(context_entities)
            cand_entity_recall = len(cand_entities.intersection(context_entities)) / len(context_entities)
        else:
            ref_entity_recall = cand_entity_recall = 1.0
            
        if context_numbers:
            ref_number_recall = len(ref_numbers.intersection(context_numbers)) / len(context_numbers)
            cand_number_recall = len(cand_numbers.intersection(context_numbers)) / len(context_numbers)
        else:
            ref_number_recall = cand_number_recall = 1.0
            
        if context_noun_chunks:
            ref_chunk_recall = len(ref_noun_chunks.intersection(context_noun_chunks)) / len(context_noun_chunks)
            cand_chunk_recall = len(cand_noun_chunks.intersection(context_noun_chunks)) / len(context_noun_chunks)
        else:
            ref_chunk_recall = cand_chunk_recall = 1.0
        
        # Compare candidate's performance to reference (as ratio)
        entity_consistency = min(1.0, cand_entity_recall / max(ref_entity_recall, 0.01))
        number_consistency = min(1.0, cand_number_recall / max(ref_number_recall, 0.01))
        chunk_consistency = min(1.0, cand_chunk_recall / max(ref_chunk_recall, 0.01))
        
        # Weighted factual consistency score
        fact_consistency = 0.4 * entity_consistency + 0.3 * number_consistency + 0.3 * chunk_consistency
        
        return {
            'fact_consistency': fact_consistency,
            'entity_consistency': entity_consistency, 
            'number_consistency': number_consistency,
            'context_coverage': chunk_consistency
        }
    
    def get_bert_score(self, reference: str, candidate: str) -> Dict[str, float]:
        """Get BERTScore metrics (requires the bert-score package)"""
        try:
            P, R, F1 = bert_score([candidate], [reference], lang="en", rescale_with_baseline=True)
            return {
                'bert_precision': P.item(),
                'bert_recall': R.item(),
                'bert_f1': F1.item()
            }
        except Exception as e:
            print(f"BERTScore calculation error: {str(e)}")
            return {
                'bert_precision': 0.0,
                'bert_recall': 0.0, 
                'bert_f1': 0.0
            }
