from langchain_ollama.llms import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
from ..config.settings import SYSTEM_INSTRUCTION, MISTRAL_SYSTEM_INSTRUCTION, LLAMA_SYSTEM_INSTRUCTION, GWEN_SYSTEM_INSTRUCTION, GEMMA_SYSTEM_INSTRUCTION
import re

# Function to extract reasoning steps and final answer
def extract_reasoning_and_answer(response):
    reasoning = ""
    answer = ""
    
    # Extract reasoning section
    reasoning_match = re.search(r'<reasoning>(.*?)</reasoning>', response, re.DOTALL)
    if reasoning_match:
        reasoning = reasoning_match.group(1).strip()
    
    # Extract answer section
    answer_match = re.search(r'<answer>(.*?)</answer>', response, re.DOTALL)
    if answer_match:
        answer = answer_match.group(1).strip()
    
    # If no structured format is found, use the entire response as the answer
    if not reasoning and not answer:
        answer = response.strip()
    
    return {
        "reasoning": reasoning,
        "answer": answer,
        "full_response": response
    }

def get_prompt_for_model(query: str, context: str = "", model_name: str = "Default") -> ChatPromptTemplate:
    """Get the appropriate prompt template for a given model"""
    if model_name == "Deepseek":
        return ChatPromptTemplate([
            ("system", SYSTEM_INSTRUCTION),
            ("user", f"<｜User｜> {query}"),
            ("system", f"Context: {context if context else 'No specific context provided.'}"),
        ])
    elif model_name == "Mistral":
        return ChatPromptTemplate.from_template(
            f"[INST] <<SYS>>\n{MISTRAL_SYSTEM_INSTRUCTION}\n<<SYS>>\nContext: {context if context else 'No specific context provided.'}\nQuestion: {query}\n[/INST]"
        )
    elif model_name == "LLaMA":
        return ChatPromptTemplate([
            ("system", "<|start_header_id|>system<|end_header_id|>\n" + LLAMA_SYSTEM_INSTRUCTION + "<|eot_id|>"),
            ("user", f"<|start_header_id|>user<|end_header_id|>\n{query}<|eot_id|>"),
            ("system", f"<|start_header_id|>system<|end_header_id|>\nContext: {context if context else 'No specific context provided.'}<|eot_id|>"),
        ])
    elif model_name == "Qwen":
        return ChatPromptTemplate([
            ("system", "<|im_start|>system\n" + GWEN_SYSTEM_INSTRUCTION + "<|im_end|>"),
            ("user", f"<|im_start|>user\n{query}<|im_end|>"),
            ("system", f"<|im_start|>system\nContext: {context if context else 'No specific context provided.'}<|im_end|>"),
            ("assistant", "instructionsassistant\nPlease provide your reasoning and answer:")
        ])
    elif model_name == "Gemma":
        return ChatPromptTemplate([
            ("system", GEMMA_SYSTEM_INSTRUCTION),
            ("user", f"<start_of_turn>user\nContext: {context if context else 'No specific context provided.'}\n\nQuery: {query}<end_of_turn>"),
        ])
    else:
        return ChatPromptTemplate([
            ("system", SYSTEM_INSTRUCTION),
            ("user", f"<｜User｜> {query}"),
            ("system", f"Context: {context if context else 'No specific context provided.'}"),
            ("assistant", "<｜Assistant｜> Please provide your reasoning and answer:")
        ])

def get_direct_response(query: str, context: str = "", model_name: str = "Default") -> dict:
    try:
        prompt = get_prompt_for_model(query, context, model_name)
        
        if model_name == "Deepseek":
            model_instance = OllamaLLM(model="deepseek-r1:latest")
        elif model_name == "Mistral":
            model_instance = OllamaLLM(model="mistral:latest")
        elif model_name == "LLaMA":
            model_instance = OllamaLLM(model="llama3.1:8b")
        elif model_name == "Qwen":
            model_instance = OllamaLLM(model="qwen2.5:7b")
        elif model_name == "Gemma":
            model_instance = OllamaLLM(model="gemma:7b")
        else:
            model_instance = OllamaLLM(model="deepseek-r1:latest")
        
        chain = prompt | model_instance
        response = chain.invoke({})
        
        # Parse the response to extract reasoning and answer
        parsed_response = extract_reasoning_and_answer(response)
        return parsed_response
        
    except Exception as e:
        error_message = f"Error generating response: {str(e)}"
        return {
            "reasoning": "",
            "answer": error_message,
            "full_response": error_message
        }
