import re
from typing import List, Dict, Tuple, Any, Optional

def extract_reasoning_steps(llm_response: str) -> Tuple[str, List[str], str]:
    """
    Extracts reasoning steps from LLM response that follows the format:
    
    REASONING:
    Step 1: ...
    Step 2: ...
    Step n: ...
    
    ANSWER: ...
    
    Returns a tuple of (full_reasoning_text, list_of_steps, final_answer)
    """
    # Extract reasoning section
    reasoning_pattern = r"REASONING:(.*?)(?:ANSWER:|$)"
    reasoning_match = re.search(reasoning_pattern, llm_response, re.DOTALL)
    reasoning_text = reasoning_match.group(1).strip() if reasoning_match else ""
    
    # Extract individual steps
    steps = []
    if reasoning_text:
        step_pattern = r"Step\s+\d+:\s*(.*?)(?:Step\s+\d+:|$)"
        step_matches = re.finditer(step_pattern, reasoning_text, re.DOTALL)
        steps = [match.group(1).strip() for match in step_matches]
        
        # If no structured steps found, try to split by newlines
        if not steps:
            steps = [s.strip() for s in reasoning_text.split('\n') if s.strip()]
    
    # Extract final answer
    answer_pattern = r"ANSWER:(.*?)$"
    answer_match = re.search(answer_pattern, llm_response, re.DOTALL)
    final_answer = answer_match.group(1).strip() if answer_match else llm_response
    
    return reasoning_text, steps, final_answer

def format_reasoning_prompt(question: str, context: str = "") -> str:
    """
    Creates a prompt that encourages step-by-step reasoning
    """
    context_part = f"\nContext: {context}" if context else ""
    
    prompt = f"""For the question below{context_part}, please:
1. Break down your thinking process into clear, logical steps
2. Consider relevant information and eliminate irrelevant details
3. Draw connections between concepts
4. Reach a well-supported conclusion

Format your response as:
REASONING:
Step 1: [First reasoning step]
Step 2: [Second reasoning step]
Step n: [Final reasoning step]

ANSWER: [Your final answer]

Question: {question}
"""
    return prompt
