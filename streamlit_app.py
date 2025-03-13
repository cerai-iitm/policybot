import streamlit as st
import re
import os
import warnings
import logging
from src.document_processing.loader import upload_pdf
from src.qa_system.retriever import retrieve_docs
from src.qa_system.answering import answer_question
from src.qa_system.single_pdf import process_single_pdf, create_temp_store
from src.qa_system.direct_chat import get_direct_response
from src.utils.logging_utils import setup_logger, log_direct_interaction, configure_root_logger, log_rag_interaction
from src.config.settings import PDFS_UPLOAD_DIR
from src.evaluation.simple_evaluator import SimpleEvaluator
from src.single_pdf.pdf_loader import PDFLoader
from src.single_pdf.utils import chunk_text, is_readable
from langchain_ollama import OllamaEmbeddings
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_core.documents import Document

# Suppress torch warnings and progress bars
warnings.filterwarnings('ignore', message='.*Examining the path of torch.classes raised.*')
logging.getLogger('tqdm').setLevel(logging.WARNING)

# Configure root logger to only show warnings and errors in console
configure_root_logger(console_level=logging.WARNING)

st.set_page_config(page_title="AI Policy Chatbot", layout="wide")

def init_session_state():
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "temp_pdf_docs" not in st.session_state:
        st.session_state.temp_pdf_docs = None

def display_chat_messages():
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

def handle_regular_chat():
    if query := st.chat_input("What would you like to know?"):
        st.session_state.messages.append({"role": "user", "content": query})
        with st.chat_message("user"):
            st.markdown(query)

        with st.chat_message("assistant"):
            related_docs = retrieve_docs(query)
            response = answer_question(query, related_docs, mode="regular_chat")
            sources = "\n\nSources:\n" + "\n".join([f"- {doc.metadata.get('source', 'Unknown')}" for doc in related_docs])
            st.markdown(f"{response}{sources}")
            st.session_state.messages.append({"role": "assistant", "content": f"{response}{sources}"})

def handle_single_pdf_chat():
    logger = setup_logger("pdf_chat")
    uploaded_file = st.sidebar.file_uploader("Upload a PDF", type="pdf")

    model_template = st.sidebar.selectbox(
        "Select Model Template",
        ["Deepseek", "Mistral", "LLaMA", "Qwen", "Gemma"]
    )
    
    if uploaded_file:
        if not os.path.exists(PDFS_UPLOAD_DIR):
            os.makedirs(PDFS_UPLOAD_DIR)
            
        file_path = os.path.join(PDFS_UPLOAD_DIR, uploaded_file.name)
        
        if st.session_state.temp_pdf_docs is None:
            try:
                # Upload PDF to file system
                upload_pdf(uploaded_file)
                
                # Load PDF using PDFLoader
                pdf_loader = PDFLoader()
                pdf_content = pdf_loader.load(file_path)
                
                # Log PDF metadata
                logger.info(f"PDF loaded: {pdf_content['meta_data']['file_name']}, "
                           f"{pdf_content['meta_data']['total_pages']} pages, "
                           f"Doc ID: {pdf_content['meta_data']['doc_id']}")
                
                # Chunk the text using single_pdf utils
                chunks = chunk_text(pdf_content['content'], pdf_content['meta_data']['file_name'], 1000)
                
                # Convert chunks to LangChain documents
                documents = []
                for chunk in chunks:
                    if is_readable(chunk['properties']['content']):
                        doc = Document(
                            page_content=chunk['properties']['content'],
                            metadata={
                                'source': chunk['properties']['source'],
                                'chunk_number': chunk['properties']['chunk_number'],
                                'doc_id': pdf_content['meta_data']['doc_id']
                            }
                        )
                        documents.append(doc)

                total_text_length = len(pdf_content['content'])
                st.sidebar.markdown("### PDF Details")
                st.sidebar.markdown(f"- **Pages**: {pdf_content['meta_data']['total_pages']}")
                st.sidebar.markdown(f"- **Total text length**: {total_text_length} characters")
                st.sidebar.markdown(f"- **Chunks created**: {len(chunks)}")
                st.sidebar.markdown(f"- **Readable chunks**: {len(documents)}")
                
                # Select the embedding model based on user selection
                if model_template == "Deepseek":
                    embed_model = "deepseek-r1:latest"
                elif model_template == "Mistral":
                    embed_model = "mistral:latest"
                elif model_template == "LLaMA":
                    embed_model = "llama3.1:8b"
                elif model_template == "Qwen":
                    embed_model = "qwen2.5:7b"
                else:
                    embed_model = "gemma:7b"
                
                # Create embeddings and store in vector database
                print("Embedding model:", embed_model)
                embeddings = OllamaEmbeddings(model=embed_model)
                vector_store = InMemoryVectorStore(embeddings)
                vector_store.add_documents(documents)
                
                # Store in session state
                st.session_state.temp_pdf_docs = {
                    'documents': documents,
                    'vector_store': vector_store,
                    'metadata': pdf_content['meta_data']
                }
                
                logger.info(f"Processed PDF: {uploaded_file.name} - "
                           f"{len(documents)} chunks created and embedded with {embed_model}")
                st.sidebar.success("PDF processed successfully!")
                
            except Exception as e:
                logger.error(f"Error processing PDF {uploaded_file.name}", exc_info=True)
                st.sidebar.error("Failed to process PDF.")

    if query := st.chat_input("Ask about the uploaded PDF"):
        st.session_state.messages.append({"role": "user", "content": query})
        with st.chat_message("user"):
            st.markdown(query)

        if st.session_state.temp_pdf_docs:
            with st.chat_message("assistant"):
                # Retrieve relevant documents
                vector_store = st.session_state.temp_pdf_docs['vector_store']
                related_docs = vector_store.similarity_search(query, k=4)
                
                # Extract context from related documents
                context = "\n\n".join([doc.page_content for doc in related_docs])
                
                # Use get_direct_response to leverage the same template system
                response = get_direct_response(
                    query,
                    context,
                    model_name=model_template
                )
                
                # Display the response with sources
                sources_display = "\n\nSources:\n"
                for i, doc in enumerate(related_docs):
                    source = f"- {doc.metadata.get('source', 'Unknown')}"
                    chunk = f" (Chunk {doc.metadata.get('chunk_number', 'N/A')})"
                    sources_display += f"{source}{chunk}\n"
                
                full_response = f"{response}{sources_display}"
                st.markdown(full_response)
                st.session_state.messages.append({"role": "assistant", "content": full_response})
                
                # Log the interaction
                log_rag_interaction(logger, query, related_docs, response)
                
                # Additional detailed logging for PDF chat
                context_texts = []
                for doc in related_docs:
                    similarity_score = doc.metadata.get('similarity', 'Unknown') 
                    context_texts.append(f"[Chunk {doc.metadata.get('chunk_number')}]: {doc.page_content[:100]}...")
                
                logger.info(f"PDF Chat - Query: {query}")
                logger.info(f"PDF Chat - PDF: {st.session_state.temp_pdf_docs['metadata']['file_name']}")
                logger.info(f"PDF Chat - Model: {model_template}")
                logger.info(f"PDF Chat - Contexts: {', '.join(context_texts)}")
                logger.info(f"PDF Chat - Response: {response}")

def handle_direct_chat():
    logger = setup_logger("direct_chat")
    context = st.sidebar.text_area("Provide context (optional)", height=200)

    model_template = st.sidebar.selectbox(
        "Select Model Template",
        ["Deepseek", "Mistral", "LLaMA", "Qwen", "Gemma"]
    )
    
    # Add human reference answer for evaluation in the sidebar
    human_ref = st.sidebar.text_area("Human Reference Answer for Evaluation", height=100, 
                                     placeholder="Enter human answer to compare...", key="human_ref")
    
    if query := st.chat_input("Chat directly with the model"):
        st.session_state.messages.append({"role": "user", "content": query})
        with st.chat_message("user"):
            st.markdown(query)

        with st.chat_message("assistant"):
            response= get_direct_response(
                query, 
                context, 
                model_name=model_template,  
            )
            st.markdown(response)
            st.session_state.messages.append({
                "role": "assistant", 
                "content": response,
            })
            
            # If a human reference is provided, perform evaluation using SimpleEvaluator
            if human_ref.strip():
                evaluator = SimpleEvaluator()
                scores = evaluator.evaluate_answer(human_ref, response, context, query)
                st.info(f"Evaluation - Final Score: {scores.get('final_score', 0):.3f}")

                logger.info(f"Evaluation Comparison - Human Answer: {human_ref}")
                logger.info(f"Evaluation Comparison - LLM Answer: {response}")
                logger.info(f"Evaluation Metrics: {scores}")
            
            # log the original response data for reference if needed
            log_direct_interaction(logger, query, context, {
                "answer": response,
            })

def main():
    st.title("AI Policy Chatbot")
    init_session_state()

    chat_mode = st.sidebar.radio(
        "Select Chat Mode",
        ["Regular Chat", "Single PDF Chat", "Direct Chat"]
    )

    display_chat_messages()

    if chat_mode == "Regular Chat":
        handle_regular_chat()
    elif chat_mode == "Single PDF Chat":
        handle_single_pdf_chat()
    else:
        handle_direct_chat()

    st.sidebar.button("Clear Chat History", on_click=lambda: st.session_state.clear())

if __name__ == "__main__":
    main()
