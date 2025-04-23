import os
import streamlit as st
import logging
from datetime import datetime
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from src.qa_system.single_pdf_app import SinglePDFApp
from src.config.settings import settings

st.set_page_config(
    page_title="AI Policy Chatbot",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .main {
        padding: 2rem;
    }
    .stApp {
        max-width: 1200px;
        margin: 0 auto;
    }
    .source-info {
        font-size: 0.8rem;
        color: #888;
        margin-top: 0.5rem;
    }
    .pdf-title {
        font-weight: bold;
        font-size: 1.2rem;
        margin-bottom: 1rem;
    }
    .answer-container {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #f8f9fa;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

if 'app' not in st.session_state:
    st.session_state.app = SinglePDFApp()
    
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

if 'current_pdf' not in st.session_state:
    st.session_state.current_pdf = None

def handle_pdf_upload():
    uploaded_file = st.session_state.pdf_uploader
    
    if uploaded_file is not None:
        with st.spinner(f"Processing {uploaded_file.name}..."):
            file_bytes = uploaded_file.getvalue()
            
            success = st.session_state.app.save_and_process_uploaded_pdf(
                file_bytes, uploaded_file.name
            )
            
            if success:
                st.session_state.current_pdf = uploaded_file.name
                st.session_state.chat_history = [] 
                st.success(f"Successfully processed {uploaded_file.name}")
            else:
                st.error(f"Failed to process {uploaded_file.name}")

def handle_question():
    question = st.session_state.question_input
    
    if not question:
        return
        
    if not st.session_state.current_pdf:
        st.warning("Please upload a PDF document first.")
        return
        
    st.session_state.chat_history.append({
        "role": "user",
        "content": question,
        "timestamp": datetime.now().strftime("%H:%M")
    })
    
    with st.spinner("Generating answer..."):
        result = st.session_state.app.answer_question(question)

    st.session_state.chat_history.append({
        "role": "assistant",
        "content": result["answer"],
        "sources": result["sources"],
        "timestamp": datetime.now().strftime("%H:%M")
    })
    
    st.session_state.question_input = ""

def main():
    st.title("AI Policy Chatbot")
    st.markdown("Upload an AI policy PDF document and ask questions about it.")
    
    with st.sidebar:
        st.header("Document Upload")
        st.file_uploader(
            "Upload a PDF document",
            type=["pdf"],
            key="pdf_uploader",
            on_change=handle_pdf_upload,
            label_visibility="collapsed"
        )
        
        if st.session_state.current_pdf:
            st.markdown(f"**Current document:** {st.session_state.current_pdf}")
        
        st.markdown("---")
        st.markdown("### About")
        st.markdown(
            "This chatbot uses RAG (Retrieval-Augmented Generation) to answer "
            "questions about AI policy documents. It retrieves relevant parts of "
            "the document and generates accurate answers using Google's Gemini model."
        )

    if st.session_state.current_pdf:
        for message in st.session_state.chat_history:
            if message["role"] == "user":
                st.chat_message("user").markdown(message["content"])
            else:
                with st.chat_message("assistant"):
                    st.markdown(message["content"])

                    if "sources" in message and message["sources"]:
                        sources_text = []
                        for source in message["sources"]:
                            sources_text.append(
                                f"**Document:** {source['title']}, "
                                f"**Page:** {source['page']}"
                            )
                        
                        st.markdown("**Sources:**")
                        for source in sources_text:
                            st.markdown(f"- {source}", unsafe_allow_html=True)

        st.chat_input(
            "Ask a question about the document...",
            key="question_input",
            on_submit=handle_question
        )
    else:
        st.info("👈 Please upload a PDF document to get started")

if __name__ == "__main__":
    main()
