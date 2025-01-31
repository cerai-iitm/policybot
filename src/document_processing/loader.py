import os
from langchain_community.document_loaders import PDFPlumberLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from ..config.settings import CHUNK_SIZE, CHUNK_OVERLAP, PDFS_UPLOAD_DIR

def upload_pdf(file):
    file_path = os.path.join(PDFS_UPLOAD_DIR, file.name)
    with open(file_path, "wb") as f:
        f.write(file.getvalue())
    return file_path

def load_pdf(file_path):
    loader = PDFPlumberLoader(file_path)
    documents = loader.load()
    
    # Add metadata to each document
    filename = os.path.basename(file_path)
    for doc in documents:
        doc.metadata.update({
            'source': filename,
            'file_path': file_path,
            'type': 'pdf'
        })
    return documents

def split_text(documents):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        add_start_index=True
    )
    return text_splitter.split_documents(documents)
