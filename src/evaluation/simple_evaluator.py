from sentence_transformers import SentenceTransformer, util
from rouge_score import rouge_scorer
import nltk
from nltk.translate.bleu_score import sentence_bleu, SmoothingFunction
from nltk.translate.meteor_score import meteor_score
from bert_score import BERTScorer

class SimpleEvaluator:
    """A lightweight evaluator for LLM answers that uses only basic metrics"""
    
    def __init__(self):
        """Initialize the evaluator with necessary models"""
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.rouge_scorer = rouge_scorer.RougeScorer(['rouge1', 'rouge2', 'rougeL'], use_stemmer=True)
        # Initialize BERT scorer
        self.bert_scorer = BERTScorer(lang="en", rescale_with_baseline=True)
        # Make sure NLTK downloads are available - fixing the resource names
        nltk.download('punkt_tab')
        try:
            nltk.data.find('tokenizers/punkt')
        except LookupError:
            print("Downloading punkt tokenizer...")
            nltk.download('punkt')
        
        try:
            nltk.data.find('corpora/wordnet')
        except LookupError:
            print("Downloading wordnet...")
            nltk.download('wordnet')
        
        # Also download omw-1.4 which might be needed for meteor
        try:
            nltk.data.find('corpora/omw-1.4')
        except LookupError:
            print("Downloading Open Multilingual Wordnet...")
            nltk.download('omw-1.4')
    
    def evaluate_answer(self, human_answer, llm_answer, context=None, question=None):
        """Evaluate LLM response against human answer and return scores"""
        
        # Calculate all metrics
        metrics = self._get_basic_metrics(human_answer, llm_answer, context, question)
        
        # Add advanced metrics
        advanced_metrics = self._get_advanced_metrics(human_answer, llm_answer)
        metrics.update(advanced_metrics)
        
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
            question_relevance = (llm_question_rel / (human_question_rel + 1e-5)) ** 0.5
        
        # Context-based relevance (if context is provided)
        context_relevance = 0
        if context:
            context_emb = self.model.encode(context, convert_to_tensor=True)
            human_context_rel = util.pytorch_cos_sim(human_emb, context_emb).item()
            llm_context_rel = util.pytorch_cos_sim(llm_emb, context_emb).item()
            # Compare model's relevance to the context with human's relevance
            context_relevance = (llm_context_rel / (human_context_rel + 1e-5)) ** 0.5
        
        return {
            'similarity': round(similarity, 3),
            # 'rouge1': round(rouge1, 3),
            # 'rouge2': round(rouge2, 3), 
            'rougeL': round(rougeL, 3),
            # 'question_relevance': round(question_relevance, 3),
            # 'context_relevance': round(context_relevance, 3)
        }
    
    def _get_advanced_metrics(self, human_answer, llm_answer):
        """Calculate advanced NLP metrics like BLEU, METEOR, and BERT Score"""
        # Calculate BLEU score
        smoothie = SmoothingFunction().method1
        human_tokens = nltk.word_tokenize(human_answer.lower())
        llm_tokens = nltk.word_tokenize(llm_answer.lower())
        
        # Handle empty responses for BLEU
        if not human_tokens or not llm_tokens:
            bleu_score = 0
        else:
            try:
                bleu_score = sentence_bleu([human_tokens], llm_tokens, weights=(0.25, 0.25, 0.25, 0.25), smoothing_function=smoothie)
            except:
                bleu_score = 0
        
        # Calculate METEOR score
        try:
            meteor = meteor_score([human_tokens], llm_tokens)
        except:
            meteor = 0
        
        # Calculate BERTScore
        try:
            P, R, F1 = self.bert_scorer.score([llm_answer], [human_answer])
            bert_precision = P.item()
            bert_recall = R.item()
            bert_f1 = F1.item()
        except:
            bert_precision = 0
            bert_recall = 0
            bert_f1 = 0
            
        return {
            'bleu': round(bleu_score, 3),
            'meteor': round(meteor, 3),
            'bert_precision': round(bert_precision, 3),
            'bert_recall': round(bert_recall, 3),
            'bert_f1': round(bert_f1, 3)
        }
    
    def _calculate_final_score(self, metrics):
        """Return all individual metrics instead of calculating a final weighted score"""
        return metrics
