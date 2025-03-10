import pandas as pd
import numpy as np
import os
from typing import List, Dict, Any, Optional, Union
from datetime import datetime
import json
import matplotlib.pyplot as plt
import seaborn as sns
from .simple_evaluator import SimpleEvaluator

class EvaluationPipeline:
    """End-to-end pipeline for evaluating LLM responses"""
    
    def __init__(self, 
                use_advanced_metrics: bool = True,
                output_dir: str = 'evaluation_results'):
        """Initialize the evaluation pipeline"""
        self.evaluator = SimpleEvaluator(use_advanced_metrics=use_advanced_metrics)
        self.output_dir = output_dir
        self.results = []
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
    def add_evaluation(self, 
                      question: str,
                      human_answer: str,
                      llm_answer: str,
                      context: Optional[str] = None,
                      metadata: Optional[Dict] = None) -> Dict:
        """Evaluate a single answer pair and add to results"""
        # Run evaluation
        result = self.evaluator.evaluate_answer(
            human_answer=human_answer,
            llm_answer=llm_answer,
            context=context,
            question=question
        )
        
        # Add metadata
        evaluation_record = {
            'question': question,
            'context': context,
            'human_answer': human_answer,
            'llm_answer': llm_answer,
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            **result
        }
        
        if metadata:
            evaluation_record.update(metadata)
            
        self.results.append(evaluation_record)
        return result
        
    def process_dataset(self, 
                      data: Union[str, pd.DataFrame],
                      context_col: str = 'context',
                      question_col: str = 'question',
                      human_answer_col: str = 'human_answer',
                      llm_answer_col: str = 'llm_answer') -> pd.DataFrame:
        """Process an entire dataset of question-answer pairs"""
        # Load dataset if string path provided
        if isinstance(data, str):
            if data.endswith('.csv'):
                df = pd.read_csv(data)
            elif data.endswith(('.xls', '.xlsx')):
                df = pd.read_excel(data)
            elif data.endswith('.json'):
                df = pd.read_json(data)
            else:
                raise ValueError(f"Unsupported file format: {data}")
        else:
            df = data
            
        # Validate columns
        required_cols = [question_col, human_answer_col, llm_answer_col]
        missing_cols = [col for col in required_cols if col not in df.columns]
        
        if missing_cols:
            raise ValueError(f"Dataset missing columns: {missing_cols}")
            
        # Process each row
        
        for idx, row in df.iterrows():
            context = row.get(context_col, "") if context_col in df.columns else ""
            
            try:
                self.add_evaluation(
                    question=row[question_col],
                    human_answer=row[human_answer_col],
                    llm_answer=row[llm_answer_col],
                    context=context,
                    metadata={'source_row': idx}
                )
            except Exception as e:
                pass
                
        return self.get_results_df()
    
    def get_results_df(self) -> pd.DataFrame:
        """Convert results to DataFrame"""
        return pd.DataFrame(self.results)
    
    def save_results(self, format_type: str = 'csv') -> str:
        """Save evaluation results to file"""
        results_df = self.get_results_df()
        
        if not results_df.empty:
            if format_type == 'csv':
                filename = os.path.join(self.output_dir, f"eval_results_{self.timestamp}.csv")
                results_df.to_csv(filename, index=False)
            elif format_type == 'json':
                filename = os.path.join(self.output_dir, f"eval_results_{self.timestamp}.json")
                results_df.to_json(filename, orient='records', indent=2)
            elif format_type == 'excel':
                filename = os.path.join(self.output_dir, f"eval_results_{self.timestamp}.xlsx")
                results_df.to_excel(filename, index=False)
            else:
                raise ValueError(f"Unsupported format type: {format_type}")
                
            return filename
        else:
            return ""
    
    def generate_visualizations(self) -> None:
        """Generate visualizations from evaluation results"""
        if not self.results:
            return
            
        results_df = self.get_results_df()
        
        # 1. Score distribution
        plt.figure(figsize=(10, 6))
        sns.histplot(results_df['final_score'], kde=True)
        plt.title('Distribution of Evaluation Scores')
        plt.xlabel('Score')
        plt.ylabel('Count')
        plt.tight_layout()
        plt.savefig(os.path.join(self.output_dir, f"score_distribution_{self.timestamp}.png"))
        plt.close()
        
        # 2. Metrics comparison
        metric_cols = [col for col in results_df.columns if col not in 
                     ['question', 'context', 'human_answer', 'llm_answer', 'timestamp', 'source_row']]
        
        if len(metric_cols) > 10:
            # If too many metrics, select most important ones
            key_metrics = ['final_score', 'similarity', 'rougeL', 'fact_consistency', 
                         'entity_f1', 'context_relevance', 'question_relevance']
            metric_cols = [m for m in key_metrics if m in metric_cols]
        
        metrics_data = results_df[metric_cols].melt(var_name='Metric', value_name='Score')
        
        plt.figure(figsize=(12, 8))
        sns.boxplot(x='Metric', y='Score', data=metrics_data)
        plt.title('Performance Across Evaluation Metrics')
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig(os.path.join(self.output_dir, f"metrics_comparison_{self.timestamp}.png"))
        plt.close()
        
        # 3. Correlation heatmap
        plt.figure(figsize=(10, 8))
        correlation = results_df[metric_cols].corr()
        sns.heatmap(correlation, annot=True, cmap='coolwarm', fmt='.2f', linewidths=0.5)
        plt.title('Correlation Between Metrics')
        plt.tight_layout()
        plt.savefig(os.path.join(self.output_dir, f"correlation_heatmap_{self.timestamp}.png"))
        plt.close()
        
        # 4. Summary statistics table
        summary_stats = results_df[metric_cols].describe()
        summary_stats.to_csv(os.path.join(self.output_dir, f"summary_statistics_{self.timestamp}.csv"))
        