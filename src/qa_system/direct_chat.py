from langchain_ollama.llms import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
from ..config.settings import SYSTEM_INSTRUCTION, MISTRAL_SYSTEM_INSTRUCTION, LLAMA_SYSTEM_INSTRUCTION, GWEN_SYSTEM_INSTRUCTION, GEMMA_SYSTEM_INSTRUCTION

# Function to extract reasoning steps and final answer
def get_prompt_for_model(query: str, context: str = "", model_name: str = "Default") -> ChatPromptTemplate:
    """Get the appropriate prompt template for a given model"""
    if model_name == "Deepseek":
        return ChatPromptTemplate([
            ("system", SYSTEM_INSTRUCTION),
            ("user", f"<｜User｜> {query}"),
            ("system", f"Context: {context if context else 'No specific context provided.'}"),
            ("assistant", "<｜Assistant｜> Answer:"),
        ])
    elif model_name == "Mistral":
        return ChatPromptTemplate.from_template(
            f"""[INST] <<SYS>>
            {MISTRAL_SYSTEM_INSTRUCTION}
            <<SYS>>  
            Context: {context if context else "No specific context provided."}  
            Question: {query}  
            [/INST]  
            """
        )
    elif model_name == "LLaMA":
        return ChatPromptTemplate([
            ("system", "<|start_header_id|>system<|end_header_id|>\n" + LLAMA_SYSTEM_INSTRUCTION + "<|eot_id|>"),
            ("user", f"<|start_header_id|>user<|end_header_id|>\n{query}<|eot_id|>"),
            ("system", f"<|start_header_id|>system<|end_header_id|>\nContext: {context if context else 'No specific context provided.'}<|eot_id|>"),
            ("assistant", "<|start_header_id|>assistant<|end_header_id|>\nAnswer:")
        ])
    elif model_name == "Qwen":
        return ChatPromptTemplate([
            ("system", "<|im_start|>system\n" + GWEN_SYSTEM_INSTRUCTION + "<|im_end|>"),
            ("user", f"<|im_start|>user\n{query}<|im_end|>"),
            ("system", f"<|im_start|>system\nContext: {context if context else 'No specific context provided.'}<|im_end|>"),
            ("assistant", "<|im_start|>assistant\nAnswer:")
        ])
    elif model_name == "Gemma":
        return ChatPromptTemplate([
            ("system", GEMMA_SYSTEM_INSTRUCTION),
            ("user", f"<start_of_turn>user\nContext: {context if context else 'No specific context provided.'}\n\nQuery: {query}<end_of_turn>"),
        ])
    else:
        return  ChatPromptTemplate([
            ("system", f"{GEMMA_SYSTEM_INSTRUCTION}"),
            ("user", f"<start_of_turn>user\nContext: {context if context else 'No specific context provided.'}\n\nQuery: {query}<end_of_turn>"),
            ("assistant", "<start_of_turn>assistant\nAnswer:")
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

        return response
        
    except Exception as e:
         return f"Error generating response: {str(e)}"
