import os
import sys
from src.config.settings import PDFS_DIR
# from src.utils.logging_utils import setup_logging
from src.document_processing.loader import load_pdf, split_text
from src.qa_system.retriever import retrieve_docs, index_documents
from src.qa_system.answering import answer_question

def preprocess_pdfs():
    for file_name in os.listdir(PDFS_DIR):
        if file_name.endswith('.pdf'):
            file_path = os.path.join(PDFS_DIR, file_name)
            documents = load_pdf(file_path)
            chunked_documents = split_text(documents)
            index_documents(chunked_documents)

def main():
    # setup_logging()
    
    if len(sys.argv) > 1 and sys.argv[1] == "preprocess":
        preprocess_pdfs()
        print("PDFs have been preprocessed and stored in the vector database.")
    else:
        question = input("Enter your question: ")
        related_documents = retrieve_docs(question)
        answer = answer_question(question, related_documents)
        print("Answer:", answer)
        print("\nSources used:")
        for doc in related_documents:
            print(f"- {doc.metadata.get('source', 'Unknown')}")

if __name__ == "__main__":
    main()