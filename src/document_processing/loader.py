import os
from langchain_community.document_loaders import PDFPlumberLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from ..config.settings import CHUNK_SIZE, CHUNK_OVERLAP

def load_pdf(file_path):
    loader = PDFPlumberLoader(file_path)
    documents = loader.load()
    for doc in documents:
        doc.metadata['source'] = os.path.basename(file_path)
    return documents

def split_text(documents):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        add_start_index=True
    )
    return text_splitter.split_documents(documents)
