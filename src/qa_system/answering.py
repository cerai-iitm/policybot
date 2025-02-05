from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama.llms import OllamaLLM
from ..config.settings import MODEL_NAME, QA_TEMPLATE, SYSTEM_INSTRUCTION
from ..utils.logging_utils import setup_logger, log_rag_interaction

model = OllamaLLM(model=MODEL_NAME)

def answer_question(question, documents, mode="regular_chat"):
    logger = setup_logger(mode)
    context = "\n\n".join([doc.page_content for doc in documents])
    prompt = ChatPromptTemplate.from_template(QA_TEMPLATE, system=SYSTEM_INSTRUCTION)
    chain = prompt | model
    answer = chain.invoke({"question": question, "context": context})
    
    log_rag_interaction(logger, question, documents, answer)
    return answer
