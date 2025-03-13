import streamlit as st
import re
import os
import warnings
import logging
import unicodedata
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

from langchain.embeddings import HuggingFaceEmbeddings

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

def sanitize_text_for_logging(text):
    """
    Sanitize text to remove or replace problematic Unicode characters for logging.
    """
    if isinstance(text, str):
        # Replace special Unicode characters with ASCII equivalents
        # Replace bullet points and other special characters
        replacements = {
            '\u25aa': '*',  # Replace black small square with asterisk
            '\u2022': '*',  # Replace bullet with asterisk
            '\u25a0': '*',  # Replace black square with asterisk
            '\u25a1': '*',  # Replace white square with asterisk
            '\u25cf': '*',  # Replace black circle with asterisk
            '\u25cb': '*',  # Replace white circle with asterisk
            '\u25c6': '*',  # Replace black diamond with asterisk
            '\u25c7': '*',  # Replace white diamond with asterisk
            '\u2014': '-',  # Replace em dash with hyphen
            '\u2013': '-',  # Replace en dash with hyphen
            '\u2018': "'",  # Replace left single quote with apostrophe
            '\u2019': "'",  # Replace right single quote with apostrophe
            '\u201c': '"',  # Replace left double quote with quotation mark
            '\u201d': '"',  # Replace right double quote with quotation mark
            '\u2026': '...',  # Replace ellipsis with three dots
            '\u00a0': ' ',   # Replace non-breaking space with regular space
            '\u2212': '-',   # Replace minus sign with hyphen
            '\u25e6': 'o',   # Replace white bullet with lowercase 'o'
            '\u2610': '[]',  # Replace ballot box with brackets
            '\u2611': '[x]', # Replace ballot box with X with marked brackets
            '\u2612': '[x]', # Replace ballot box with X with marked brackets
            '\u25b6': '>',   # Replace right-pointing triangle with greater than
            '\u25b2': '^',   # Replace up-pointing triangle with caret
            '\u25bc': 'v',   # Replace down-pointing triangle with lowercase 'v'
            '\u25c0': '<',   # Replace left-pointing triangle with less than
            '\u00b7': '*',   # Replace middle dot with asterisk
            '\u2212': '-',   # Replace minus sign with hyphen
        }
        
        for unicode_char, replacement in replacements.items():
            text = text.replace(unicode_char, replacement)
        
        # Normalize to closest ASCII equivalent where possible
        text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('ascii')
    return text

def handle_single_pdf_chat():
    logger = setup_logger("pdf_chat")
    uploaded_file = st.sidebar.file_uploader("Upload a PDF", type="pdf")

    model_template = st.sidebar.selectbox(
        "Select Model Template",
        ["Deepseek", "Mistral", "LLaMA", "Qwen", "Gemma"]
    )
    
    # Add controls for chunk size and overlap
    chunk_size = st.sidebar.slider("Chunk Size (words)", 
                                  min_value=100, 
                                  max_value=1000, 
                                  value=500,
                                  help="Larger chunks include more context, smaller chunks are more focused")
    
    chunk_overlap = st.sidebar.slider("Chunk Overlap (words)", 
                                     min_value=0, 
                                     max_value=200, 
                                     value=100,
                                     help="Overlap prevents important context from being split between chunks")
    
    k_documents = st.sidebar.slider("Number of chunks to retrieve", 
                                  min_value=1, 
                                  max_value=10, 
                                  value=4,
                                  help="More chunks provide more context but may add noise")
    
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
                
                # Preprocess the text to improve quality
                cleaned_text = pdf_content['content'].replace('\n\n', ' ').replace('  ', ' ')
                
                # Chunk the text using updated parameters
                chunks = chunk_text(
                    cleaned_text, 
                    pdf_content['meta_data']['file_name'], 
                    chunk_size,
                    chunk_overlap
                )
                
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
                embeddings = HuggingFaceEmbeddings(model_name = "BAAI/bge-base-en")
                vector_store = InMemoryVectorStore(embeddings)
                vector_store.add_documents(documents)
                
                # Store in session state
                st.session_state.temp_pdf_docs = {
                    'documents': documents,
                    'vector_store': vector_store,
                    'metadata': pdf_content['meta_data']
                }
                
                logger.info(f"Processed PDF: {uploaded_file.name} - "
                           f"{len(documents)} chunks created and embedded with BAAI/bge-base-en")
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
                # Retrieve relevant documents with the user-specified k value
                vector_store = st.session_state.temp_pdf_docs['vector_store']
                # Modify to get scores along with documents
                retrieval_results = vector_store.similarity_search_with_score(query, k=k_documents)
                related_docs = []
                
                # Process results to include similarity scores in metadata
                for doc, score in retrieval_results:
                    # Convert score to similarity (higher is better)
                    similarity = round(float(score), 3)
                    doc.metadata['similarity'] = similarity
                    related_docs.append(doc)
                
                # Extract context from related documents
                context = "\n\n".join([doc.page_content for doc in related_docs])
                
                # Use get_direct_response to leverage the same template system
                response = get_direct_response(
                    query,
                    context,
                    model_name=model_template
                )
                
                # Display the response with sources and similarity scores
                sources_display = "\n\nSources:\n"
                for i, doc in enumerate(related_docs):
                    source = f"- {doc.metadata.get('source', 'Unknown')}"
                    chunk = f" (Chunk {doc.metadata.get('chunk_number', 'N/A')})"
                    similarity = f" [Similarity: {doc.metadata.get('similarity', 'N/A')}]"
                    sources_display += f"{source}{chunk}{similarity}\n"
                
                full_response = f"{response}{sources_display}"
                st.markdown(full_response)
                st.session_state.messages.append({"role": "assistant", "content": full_response})
                
                # Additional detailed logging for PDF chat
                context_texts = []
                for doc in related_docs:
                    similarity_score = doc.metadata.get('similarity', 'Unknown')
                    safe_content = sanitize_text_for_logging(doc.page_content)
                    context_texts.append(f"[Chunk {doc.metadata.get('chunk_number')}, Similarity: {similarity_score}]: {safe_content}")
                
                # Sanitize all data for logging
                safe_query = sanitize_text_for_logging(query)
                safe_response = sanitize_text_for_logging(response)
                
                # Log with sanitized text
                logger.info(f"PDF Chat - Query: {safe_query}")
                logger.info(f"PDF Chat - PDF: {st.session_state.temp_pdf_docs['metadata']['file_name']}")
                logger.info(f"PDF Chat - Model: {model_template}")
                
                # Log each context with its similarity score
                # for i, context in enumerate(context_texts):
                #     logger.info(f"PDF Chat - Context {i+1}: {context}")
                
                # Create sanitized copies of related docs for logging
                safe_related_docs = []
                for doc in related_docs:
                    safe_doc = Document(
                        page_content=sanitize_text_for_logging(doc.page_content),
                        metadata=doc.metadata
                    )
                    safe_related_docs.append(safe_doc)
                
                # Log with sanitized text
                log_rag_interaction(logger, safe_query, safe_related_docs, safe_response)

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
