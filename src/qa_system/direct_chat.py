from langchain_ollama.llms import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
from ..config.settings import MODEL_NAME, QA_TEMPLATE, SYSTEM_INSTRUCTION

model = OllamaLLM(model=MODEL_NAME)

def get_direct_response(query: str, context: str = "") -> str:
    try:
        prompt = ChatPromptTemplate.from_template(QA_TEMPLATE, system=SYSTEM_INSTRUCTION)
        chain = prompt | model
        response = chain.invoke({
            "question": query,
            "context": context if context else "No specific context provided."
        })
        return response
    except Exception as e:
        return f"Error generating response: {str(e)}"
