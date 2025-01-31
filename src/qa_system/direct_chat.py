from langchain_ollama.llms import OllamaLLM
from ..config.settings import MODEL_NAME

model = OllamaLLM(model=MODEL_NAME)

def get_direct_response(prompt, context=None):
    if context:
        full_prompt = f"Context: {context}\n\nQuestion: {prompt}"
    else:
        full_prompt = prompt
    return model.invoke(full_prompt)
