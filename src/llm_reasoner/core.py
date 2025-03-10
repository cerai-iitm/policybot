from langchain_ollama.llms import OllamaLLM
from typing import Dict, List, Optional, Tuple
from ..config.settings import MODEL_NAME
from .utils import extract_reasoning_steps, format_reasoning_prompt

class LLMReasoner:
    """
    A wrapper around LLM that encourages step-by-step reasoning through prompting.
    """
    
    def __init__(self, model_name: str = MODEL_NAME):
        """Initialize the reasoner with the specified model"""
        self.model = OllamaLLM(model=model_name)
    
    def generate_reasoned_response(self, 
                                  question: str, 
                                  context: str = "",
                                  extract_steps: bool = True) -> Dict:
        """
        Generates a response with explicit reasoning steps
        
        Args:
            question: The question to answer
            context: Optional context information
            extract_steps: Whether to extract and structure the reasoning steps
            
        Returns:
            Dict containing full_response, reasoning_text, reasoning_steps, and answer
        """
        # Format the prompt to encourage reasoning
        prompt = format_reasoning_prompt(question, context)
        
        # Get response from LLM
        full_response = self.model.invoke(prompt)
        
        # Process the response
        if extract_steps:
            reasoning_text, reasoning_steps, answer = extract_reasoning_steps(full_response)
        else:
            reasoning_text = ""
            reasoning_steps = []
            answer = full_response
        
        return {
            "full_response": full_response,
            "reasoning_text": reasoning_text,
            "reasoning_steps": reasoning_steps,
            "answer": answer
        }
    
    def evaluate_reasoning(self, reasoning_steps: List[str]) -> Dict:
        """
        Evaluates the quality of reasoning steps
        
        Args:
            reasoning_steps: List of reasoning step strings
            
        Returns:
            Dict with evaluation metrics
        """
        if not reasoning_steps:
            return {"coherence": 0, "relevance": 0, "logical_flow": 0}
            
        # Count steps as basic measure of thoroughness
        num_steps = len(reasoning_steps)
        
        # Simple heuristics for quality assessment
        avg_step_length = sum(len(step) for step in reasoning_steps) / max(num_steps, 1)
        has_logical_connectors = any(
            connector in " ".join(reasoning_steps).lower() 
            for connector in ["because", "therefore", "thus", "hence", "since", "as a result"]
        )
        
        # Simple scoring based on heuristics
        coherence = min(1.0, num_steps / 10) * 0.4 + (0.6 if has_logical_connectors else 0)
        logical_flow = min(1.0, avg_step_length / 100) * 0.7 + (0.3 if num_steps > 2 else 0)
        
        return {
            "num_steps": num_steps,
            "coherence": round(coherence, 2),
            "logical_flow": round(logical_flow, 2),
        }
