import streamlit as st
import re
import os
import warnings
import logging
from src.document_processing.loader import upload_pdf, load_pdf, split_text
from src.qa_system.retriever import retrieve_docs, index_documents
from src.qa_system.answering import answer_question
from src.qa_system.single_pdf import process_single_pdf
from src.qa_system.direct_chat import get_direct_response
from src.utils.logging_utils import setup_logger, log_direct_interaction, configure_root_logger
from src.config.settings import PDFS_UPLOAD_DIR
from src.evaluation.simple_evaluator import SimpleEvaluator

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
    
    if uploaded_file:
        if not os.path.exists(PDFS_UPLOAD_DIR):
            os.makedirs(PDFS_UPLOAD_DIR)
            
        file_path = os.path.join(PDFS_UPLOAD_DIR, uploaded_file.name)
        
        if st.session_state.temp_pdf_docs is None:
            try:
                upload_pdf(uploaded_file)
                documents = load_pdf(file_path)
                st.session_state.temp_pdf_docs = split_text(documents)
                logger.info(f"Processed PDF: {uploaded_file.name} - {len(st.session_state.temp_pdf_docs)} chunks created")
                st.sidebar.success("PDF processed successfully!")
            except Exception as e:
                logger.error(f"Error processing PDF {uploaded_file.name}: {str(e)}")
                st.sidebar.error("Failed to process PDF.")

    if query := st.chat_input("Ask about the uploaded PDF"):
        st.session_state.messages.append({"role": "user", "content": query})
        with st.chat_message("user"):
            st.markdown(query)

        if st.session_state.temp_pdf_docs:
            with st.chat_message("assistant"):
                related_docs = process_single_pdf(st.session_state.temp_pdf_docs, query)
                response = answer_question(query, related_docs, mode="pdf_chat")
                st.markdown(response)
                st.session_state.messages.append({"role": "assistant", "content": response})

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
