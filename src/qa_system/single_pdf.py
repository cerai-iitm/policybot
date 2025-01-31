from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings
from ..config.settings import MODEL_NAME
import tempfile

def create_temp_db():
    embeddings = OllamaEmbeddings(model=MODEL_NAME)
    with tempfile.TemporaryDirectory() as temp_dir:
        return Chroma(embedding_function=embeddings, persist_directory=temp_dir)

def process_single_pdf(documents, query):
    temp_db = create_temp_db()
    temp_db.add_documents(documents)
    return temp_db.similarity_search(query, k=5)
