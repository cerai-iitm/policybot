from langchain_ollama.llms import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
from ..config.settings import SYSTEM_INSTRUCTION, MISTRAL_SYSTEM_INSTRUCTION, LLAMA_SYSTEM_INSTRUCTION, GWEN_SYSTEM_INSTRUCTION, GEMMA_SYSTEM_INSTRUCTION

# ...existing code...

def get_direct_response(query: str, context: str = "", model_name: str = "Default") -> str:
    try:
        if model_name == "Deepseek":
            prompt = ChatPromptTemplate([
                ("system", SYSTEM_INSTRUCTION),
                ("user", f"<｜User｜> {query}"),
                ("system", f"Context: {context if context else 'No specific context provided.'}"),
                ("assistant", "<｜Assistant｜> Answer:")
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
                ("assistant", "<|start_header_id|>assistant<|end_header_id|>\nAnswer:")
            ])
            model_instance = OllamaLLM(model="llama3.1:8b")
        elif model_name == "Qwen":
            prompt = ChatPromptTemplate([
                ("system", "instructionsystem\n" + GWEN_SYSTEM_INSTRUCTION + "\ninstructionsystem"),
                ("user", f"instructionsuser\n{query}\ninstructionsuser"),
                ("system", f"instructionsystem\nContext: {context if context else 'No specific context provided.'}\ninstructionsystem"),
                ("assistant", "instructionsassistant\nAnswer:")
            ])
            model_instance = OllamaLLM(model="qwen2.5:7b")
        elif model_name == "Gemma":
            prompt = ChatPromptTemplate([
                ("system", GEMMA_SYSTEM_INSTRUCTION),
                ("user", f"<start_of_turn>user\nContext: {context if context else 'No specific context provided.'}\n\nQuery: {query}<end_of_turn>"),
                ("assistant", "<start_of_turn>assistant\nAnswer:")
            ])
            model_instance = OllamaLLM(model="gemma:7b")
        else:
            prompt = ChatPromptTemplate([
                ("system", SYSTEM_INSTRUCTION),
                ("user", f"<｜User｜> {query}"),
                ("system", f"Context: {context if context else 'No specific context provided.'}"),
                ("assistant", "<｜Assistant｜> Answer:")
            ])
            model_instance = OllamaLLM(model="deepseek-r1:latest")
        
        chain = prompt | model_instance
        response = chain.invoke({})
        return response
    except Exception as e:
        return f"Error generating response: {str(e)}"
