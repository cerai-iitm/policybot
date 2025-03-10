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

def get_direct_response(query: str, context: str = "", model_name: str = "Default") -> dict:
    try:
        if model_name == "Deepseek":
            prompt = ChatPromptTemplate([
                ("system", SYSTEM_INSTRUCTION),
                ("user", f"<｜User｜> {query}"),
                ("system", f"Context: {context if context else 'No specific context provided.'}"),
                ("assistant", "<｜Assistant｜> Please provide your reasoning and answer:")
            ])
            model_instance = OllamaLLM(model="deepseek-r1:latest")
        elif model_name == "Mistral":
            prompt = ChatPromptTemplate.from_template(
                f"[INST] <<SYS>>\n{MISTRAL_SYSTEM_INSTRUCTION}\n<<SYS>>\nContext: {context if context else 'No specific context provided.'}\nQuestion: {query}\n[/INST]"
            )
            model_instance = OllamaLLM(model="mistral:latest")
        elif model_name == "LLaMA":
            prompt = ChatPromptTemplate([
                ("system", "<|start_header_id|>system<|end_header_id|>\n" + LLAMA_SYSTEM_INSTRUCTION + "<|eot_id|>"),
                ("user", f"<|start_header_id|>user<|end_header_id|>\n{query}<|eot_id|>"),
                ("system", f"<|start_header_id|>system<|end_header_id|>\nContext: {context if context else 'No specific context provided.'}<|eot_id|>"),
                ("assistant", "<|start_header_id|>assistant<|end_header_id|>\nPlease provide your reasoning and answer:")
            ])
            model_instance = OllamaLLM(model="llama3.1:8b")
        elif model_name == "Qwen":
            prompt = ChatPromptTemplate([
                ("system", "instructionsystem\n" + GWEN_SYSTEM_INSTRUCTION + "\ninstructionsystem"),
                ("user", f"instructionsuser\n{query}\ninstructionsuser"),
                ("system", f"instructionsystem\nContext: {context if context else 'No specific context provided.'}\ninstructionsystem"),
                ("assistant", "instructionsassistant\nPlease provide your reasoning and answer:")
            ])
            model_instance = OllamaLLM(model="qwen2.5:7b")
        elif model_name == "Gemma":
            prompt = ChatPromptTemplate([
                ("system", GEMMA_SYSTEM_INSTRUCTION),
                ("user", f"<start_of_turn>user\nContext: {context if context else 'No specific context provided.'}\n\nQuery: {query}<end_of_turn>"),
                ("assistant", "<start_of_turn>assistant\nPlease provide your reasoning and answer:")
            ])
            model_instance = OllamaLLM(model="gemma:7b")
        else:
            prompt = ChatPromptTemplate([
                ("system", SYSTEM_INSTRUCTION),
                ("user", f"<｜User｜> {query}"),
                ("system", f"Context: {context if context else 'No specific context provided.'}"),
                ("assistant", "<｜Assistant｜> Please provide your reasoning and answer:")
            ])
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
