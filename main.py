import os
import sys
import logging
from src.config.settings import PDFS_DIR
# from src.utils.logging_utils import setup_logging
from src.document_processing.loader import load_pdf, split_text
from src.qa_system.retriever import retrieve_docs, index_documents
from src.qa_system.answering import answer_question

def preprocess_pdfs():
    processed_count = 0
    error_count = 0
    
    if not os.path.exists(PDFS_DIR):
        print(f"Error: PDF directory not found at {PDFS_DIR}")
        return

    pdf_files = [f for f in os.listdir(PDFS_DIR) if f.endswith('.pdf')]
    if not pdf_files:
        print("No PDF files found in the directory.")
        return

    print(f"Found {len(pdf_files)} PDF files. Starting preprocessing...")
    
    for file_name in pdf_files:
        try:
            file_path = os.path.join(PDFS_DIR, file_name)
            print(f"Processing {file_name}...")
            
            documents = load_pdf(file_path)
            if not documents:
                error_count += 1
                continue
                
            chunked_documents = split_text(documents)
            index_documents(chunked_documents)
            processed_count += 1
            
        except Exception as e:
            error_count += 1
            print(f"Error processing {file_name}: {str(e)}")
    
    print(f"\nPreprocessing complete!")
    print(f"Successfully processed: {processed_count} files")
    print(f"Errors encountered: {error_count} files")

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