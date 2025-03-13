from langchain_core.vectorstores import InMemoryVectorStore
from langchain_ollama import OllamaEmbeddings
from ..config.settings import MODEL_NAME, RETRIEVAL_K
import tempfile

def create_temp_db():
    embeddings = OllamaEmbeddings(model=MODEL_NAME)
    with tempfile.TemporaryDirectory() as temp_dir:
        return Chroma(embedding_function=embeddings, persist_directory=temp_dir)

def create_temp_store(model_name=MODEL_NAME):
    """Create a temporary vector store with the specified model"""
    embeddings = OllamaEmbeddings(model=model_name)
    return InMemoryVectorStore(embeddings)

def process_single_pdf(documents, query, model_name=MODEL_NAME):
    """Process documents for a single PDF and return relevant chunks"""
    temp_store = create_temp_store(model_name)
    temp_store.add_documents(documents)
    return temp_store.similarity_search(query, k=RETRIEVAL_K)
