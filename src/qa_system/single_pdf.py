from langchain_core.vectorstores import InMemoryVectorStore
from langchain_ollama import OllamaEmbeddings
from ..config.settings import MODEL_NAME, RETRIEVAL_K
import tempfile

def create_temp_db():
    embeddings = OllamaEmbeddings(model=MODEL_NAME)
    with tempfile.TemporaryDirectory() as temp_dir:
        return Chroma(embedding_function=embeddings, persist_directory=temp_dir)

def create_temp_store():
    embeddings = OllamaEmbeddings(model=MODEL_NAME)
    return InMemoryVectorStore(embeddings)

def process_single_pdf(documents, query):
    temp_store = create_temp_store()
    temp_store.add_documents(documents)
    return temp_store.similarity_search(query, k=RETRIEVAL_K)
