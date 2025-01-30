import os
from langchain_community.document_loaders import PDFPlumberLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama.llms import OllamaLLM

template = """
You are an assistant for question-answering tasks. Use the following pieces of retrieved context to answer the question. If you don't know the answer, just say that you don't know. Use three sentences maximum and keep the answer concise.
Question: {question} 
Context: {context} 
Answer:
"""

pdfs_directory = 'pdfs/'
chroma_collection_name = 'pdf_documents'

embeddings = OllamaEmbeddings(model="deepseek-r1:1.5b")

persist_directory = "./chroma_db"

vector_store = Chroma(collection_name=chroma_collection_name, embedding_function=embeddings, 
persist_directory=persist_directory)

model = OllamaLLM(model="deepseek-r1:1.5b")

def preprocess_pdfs():
    for file_name in os.listdir(pdfs_directory):
        if file_name.endswith('.pdf'):
            file_path = os.path.join(pdfs_directory, file_name)
            documents = load_pdf(file_path)
            chunked_documents = split_text(documents)
            index_docs(chunked_documents)

def load_pdf(file_path):
    loader = PDFPlumberLoader(file_path)
    documents = loader.load()
    return documents

def split_text(documents):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        add_start_index=True
    )
    return text_splitter.split_documents(documents)

def index_docs(documents):
    vector_store.add_documents(documents)

def retrieve_docs(query):
    return vector_store.similarity_search(query, k=5)

def answer_question(question, documents):
    context = "\n\n".join([doc.page_content for doc in documents])
    prompt = ChatPromptTemplate.from_template(template)
    chain = prompt | model
    return chain.invoke({"question": question, "context": context})

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "preprocess":
        preprocess_pdfs()
        print("PDFs have been preprocessed and stored in the vector database.")
    else:
        question = input("Enter your question: ")
        related_documents = retrieve_docs(question)
        answer = answer_question(question, related_documents)
        print("Answer:", answer)
    # print(vector_store._collection.count())