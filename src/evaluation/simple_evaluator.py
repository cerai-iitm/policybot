import argparse
import json
import pandas as pd
from sentence_transformers import SentenceTransformer, util
from rouge_score import rouge_scorer
import torch
import os
import time
from datetime import datetime

# Import optional advanced metrics if available
try:
    from .advanced_metrics import AdvancedMetrics
    has_advanced_metrics = True
except ImportError:
    has_advanced_metrics = False

class SimpleEvaluator:
    """A lightweight evaluator for LLM answers that doesn't require external API calls"""
    
    def __init__(self, use_advanced_metrics=True):
        """Initialize the evaluator with necessary models"""
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.rouge_scorer = rouge_scorer.RougeScorer(['rouge1', 'rouge2', 'rougeL'], use_stemmer=True)
        
        # Initialize advanced metrics if available and requested
        self.advanced_metrics = None
        if use_advanced_metrics and has_advanced_metrics:
            self.advanced_metrics = AdvancedMetrics()
    
    def evaluate_answer(self, human_answer, llm_answer, context=None, question=None):
        """Evaluate LLM response against human answer and return scores"""
        
        # Basic metrics (always available)
        basic_metrics = self._get_basic_metrics(human_answer, llm_answer, context, question)
        
        # Advanced metrics (if available)
        advanced_metrics = {}
        if self.advanced_metrics:
            # Entity analysis
            advanced_metrics.update(self.advanced_metrics.entity_precision_recall(human_answer, llm_answer))
            
            # Numeric accuracy
            advanced_metrics.update(self.advanced_metrics.numeric_accuracy(human_answer, llm_answer))
            
            # BLEU score with smoothing
            advanced_metrics['bleu'] = self.advanced_metrics.calculate_bleu(human_answer, llm_answer)
            
            # Factual consistency (if context provided)
            if context:
                advanced_metrics.update(self.advanced_metrics.factual_consistency(context, human_answer, llm_answer))
                
            # BERTScore (more resource intensive)
            # Only use for important evaluations or set a flag to enable
            # advanced_metrics.update(self.advanced_metrics.get_bert_score(human_answer, llm_answer))
        
        # Combined metrics
        all_metrics = {**basic_metrics, **advanced_metrics}
        
        # Calculate final score
        final_score = self._calculate_final_score(all_metrics)
        all_metrics['final_score'] = final_score
        
        return all_metrics
    
    def _get_basic_metrics(self, human_answer, llm_answer, context=None, question=None):
        """Get basic evaluation metrics"""
        # Semantic Similarity Score (SBERT cosine similarity)
        human_emb = self.model.encode(human_answer, convert_to_tensor=True)
        llm_emb = self.model.encode(llm_answer, convert_to_tensor=True)
        similarity = util.pytorch_cos_sim(human_emb, llm_emb).item()
        
        # ROUGE Scores
        rouge_scores = self.rouge_scorer.score(human_answer, llm_answer)
        rouge1 = rouge_scores['rouge1'].fmeasure
        rouge2 = rouge_scores['rouge2'].fmeasure
        rougeL = rouge_scores['rougeL'].fmeasure
        
        # Question-based relevance (if question is provided)
        question_relevance = 0
        if question:
            question_emb = self.model.encode(question, convert_to_tensor=True)
            human_question_rel = util.pytorch_cos_sim(human_emb, question_emb).item()
            llm_question_rel = util.pytorch_cos_sim(llm_emb, question_emb).item()
            # Compare model's relevance to the question with human's relevance
            question_relevance = min(1.0, llm_question_rel / max(human_question_rel, 0.01))
        
        # Context-based relevance (if context is provided)
        context_relevance = 0
        if context:
            context_emb = self.model.encode(context, convert_to_tensor=True)
            human_context_rel = util.pytorch_cos_sim(human_emb, context_emb).item()
            llm_context_rel = util.pytorch_cos_sim(llm_emb, context_emb).item()
            # Compare model's relevance to the context with human's relevance
            context_relevance = min(1.0, llm_context_rel / max(human_context_rel, 0.01))
        
        return {
            'similarity': similarity,
            'rouge1': rouge1,
            'rouge2': rouge2, 
            'rougeL': rougeL,
            'question_relevance': question_relevance,
            'context_relevance': context_relevance
        }
    
    def _calculate_final_score(self, metrics):
        """Calculate final weighted score based on available metrics"""
        # Define weights for different metric groups
        weight_config = {
            # Basic metrics (always available)
            'basic': {
                'similarity': 0.40,  # Increased from 0.35
                'rougeL': 0.30,      # Increased from 0.25
                'rouge1': 0.05,
                'rouge2': 0.05,
                'question_relevance': 0.10,  # Increased from 0.05
                'context_relevance': 0.10     # Increased from 0.05
            },
            # Advanced metrics (if available)
            'advanced': {
                'entity_f1': 0.05,
                'numeric_precision': 0.025,
                'numeric_recall': 0.025,
                'bleu': 0.05,
                'fact_consistency': 0.05,
                # 'bert_f1': 0.05  # Optional if using BERTScore
            }
        }
        
        # Calculate weighted score
        score = 0.0
        total_weight = 0.0
        
        # Process all weights that have matching metrics
        for group, weights in weight_config.items():
            for metric, weight in weights.items():
                if metric in metrics:
                    score += metrics[metric] * weight
                    total_weight += weight
        
        # Normalize by actual weights used
        if total_weight > 0:
            return round(score / total_weight, 3)
        else:
            return 0.0
    
    def evaluate_from_file(self, file_path, output_path=None):
        """Evaluate answers from a CSV or JSON file with columns/keys for context, question, human_answer, llm_answer"""
        if file_path.endswith('.csv'):
            data = pd.read_csv(file_path)
        elif file_path.endswith('.json'):
            with open(file_path, 'r', encoding='utf-8') as f:
                data = pd.DataFrame(json.load(f))
        else:
            raise ValueError("File must be CSV or JSON")
        
        results = []
        for _, row in data.iterrows():
            context = row.get('context', '')
            question = row.get('question', '')
            human_answer = row['human_answer']
            llm_answer = row['llm_answer']
            
            scores = self.evaluate_answer(human_answer, llm_answer, context, question)
            results.append({
                'question': question,
                'human_answer': human_answer,
                'llm_answer': llm_answer,
                **scores
            })
        
        results_df = pd.DataFrame(results)
        
        if output_path:
            results_df.to_csv(output_path, index=False)
        
        return results_df

def main():
    parser = argparse.ArgumentParser(description='Evaluate LLM answers against human answers')
    parser.add_argument('--file', help='Path to CSV or JSON file with answers')
    parser.add_argument('--output', help='Path to save output results')
    parser.add_argument('--human', help='Human answer text')
    parser.add_argument('--llm', help='LLM answer text')
    parser.add_argument('--context', help='Context text (optional)')
    parser.add_argument('--question', help='Question text (optional)')
    
    args = parser.parse_args()
    evaluator = SimpleEvaluator()
    
    if args.file:
        results = evaluator.evaluate_from_file(args.file, args.output)
        print(f"Average score: {results['final_score'].mean()}")
        print(f"Results saved to {args.output}" if args.output else "")
    elif args.human and args.llm:
        scores = evaluator.evaluate_answer(args.human, args.llm, args.context, args.question)
        print(json.dumps(scores, indent=2))
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
