from langchain_ollama.llms import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
from ..config.settings import MODEL_NAME, QA_TEMPLATE, SYSTEM_INSTRUCTION, MISTRAL_SYSTEM_INSTRUCTION, LLAMA_SYSTEM_INSTRUCTION, GWEN_SYSTEM_INSTRUCTION, GEMMA_SYSTEM_INSTRUCTION

model = OllamaLLM(model=MODEL_NAME)

def get_direct_response(query: str, context: str = "") -> str:
    # try:
    #     prompt = ChatPromptTemplate.from_template(QA_TEMPLATE, system=SYSTEM_INSTRUCTION)
    #     chain = prompt | model
    #     response = chain.invoke({
    #         "question": query,
    #         "context": context if context else "No specific context provided."
    #     })
    #     return response
    # except Exception as e:
    #     return f"Error generating response: {str(e)}"



    try:
        # DeepSeek-compatible prompt template
        prompt = ChatPromptTemplate([
            ("system", SYSTEM_INSTRUCTION),  
            ("user", f"<｜User｜> {query}"),  
            ("system", f"Context: {context if context else 'No specific context provided.'}"),  
            ("assistant", "<｜Assistant｜> Answer:")  
        ])

        # Create processing chain
        chain = prompt | model

        # Get response
        response = chain.invoke({})
        return response
    except Exception as e:
        return f"Error generating response: {str(e)}"


    # try:
    #     # Mistral-compatible prompt template
    #     prompt = ChatPromptTemplate.from_template(
    #         f"""[INST] <<SYS>>
    #         {MISTRAL_SYSTEM_INSTRUCTION}
    #         <<SYS>>  
    #         Context: {context if context else "No specific context provided."}  
    #         Question: {query}  
    #         [/INST]  
    #         """
    #     )

    #     # Create processing chain
    #     chain = prompt | model

    #     # Get response
    #     response = chain.invoke({})
    #     return response

    # except Exception as e:
    #     return f"Error generating response: {str(e)}"

    # try:
    #     # LLaMA-compatible prompt template
    #     prompt = ChatPromptTemplate([
    #         ("system", "<|start_header_id|>system<|end_header_id|>\n" + LLAMA_SYSTEM_INSTRUCTION + "<|eot_id|>"),
    #         ("user", f"<|start_header_id|>user<|end_header_id|>\n{query}<|eot_id|>"),
    #         ("system", f"<|start_header_id|>system<|end_header_id|>\nContext: {context if context else 'No specific context provided.'}<|eot_id|>"),
    #         ("assistant", "<|start_header_id|>assistant<|end_header_id|>\nAnswer:")
    #     ])

    #     # Create processing chain
    #     chain = prompt | model

    #     # Get response
    #     response = chain.invoke({})
    #     return response
    # except Exception as e:
    #     return f"Error generating response: {str(e)}"


    # try:
    #     # Qwen-compatible prompt template
    #     prompt = ChatPromptTemplate([
    #         ("system", "<|im_start|>system\n" + GWEN_SYSTEM_INSTRUCTION + "<|im_end|>"),
    #         ("user", f"<|im_start|>user\n{query}<|im_end|>"),
    #         ("system", f"<|im_start|>system\nContext: {context if context else 'No specific context provided.'}<|im_end|>"),
    #         ("assistant", "<|im_start|>assistant\nAnswer:")
    #     ])

    #     # Create processing chain
    #     chain = prompt | model

    #     # Get response
    #     response = chain.invoke({})
    #     return response
    # except Exception as e:
    #     return f"Error generating response: {str(e)}"


    # try:
    #     # Gemma-compatible prompt template with context handling
    #     prompt = ChatPromptTemplate([
    #         ("system", f"{GEMMA_SYSTEM_INSTRUCTION}"),
    #         ("user", f"<start_of_turn>user\nContext: {context if context else 'No specific context provided.'}\n\nQuery: {query}<end_of_turn>"),
    #         ("assistant", "<start_of_turn>assistant\nAnswer:")
    #     ])

    #     # Create processing chain
    #     chain = prompt | model

    #     # Get response
    #     response = chain.invoke({})
    #     return response
    # except Exception as e:
    #     return f"Error generating response: {str(e)}"
