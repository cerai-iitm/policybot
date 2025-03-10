from sentence_transformers import SentenceTransformer, util
from rouge_score import rouge_scorer

class SimpleEvaluator:
    """A lightweight evaluator for LLM answers that uses only basic metrics"""
    
    def __init__(self):
        """Initialize the evaluator with necessary models"""
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.rouge_scorer = rouge_scorer.RougeScorer(['rouge1', 'rouge2', 'rougeL'], use_stemmer=True)
    
    def evaluate_answer(self, human_answer, llm_answer, context=None, question=None):
        """Evaluate LLM response against human answer and return scores"""
        
        # Calculate basic metrics
        metrics = self._get_basic_metrics(human_answer, llm_answer, context, question)
        
        # Calculate final score
        final_score = self._calculate_final_score(metrics)
        metrics['final_score'] = final_score
        
        return metrics
    
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
        # Define weights for different metrics
        weight_config = {
            'similarity': 0.40,
            'rougeL': 0.30,
            'rouge1': 0.05,
            'rouge2': 0.05,
            'question_relevance': 0.10,
            'context_relevance': 0.10,
        }
        
        # Calculate weighted score
        score = 0.0
        total_weight = 0.0
        
        # Process all weights that have matching metrics
        for metric, weight in weight_config.items():
            if metric in metrics:
                score += metrics[metric] * weight
                total_weight += weight
        
        # Normalize by actual weights used
        if total_weight > 0:
            return round(score / total_weight, 3)
        else:
            return 0.0
