import os
import streamlit as st
import logging
from datetime import datetime

os.environ["STREAMLIT_SERVER_ENABLE_FILE_WATCHER"] = "false"

from src.utils.log_utils import setup_app_logger

# Setup file logging for the whole application
logger = setup_app_logger()

from src.qa_system.single_pdf_app import SinglePDFApp

st.set_page_config(
    page_title="AI Policy Chatbot",
    page_icon="📄",
    layout="wide", 
    initial_sidebar_state="expanded"
)

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
                st.rerun()
            else:
                st.error(f"Failed to process {uploaded_file.name}")

def handle_question():
    question = st.session_state.question_input

    if not question:
        st.warning("Please enter a question.")
        return

    if not st.session_state.current_pdf:
        st.warning("Please upload and process a PDF document first.")
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

def main():
    st.title("📄 AI Policy Chatbot")

    with st.sidebar:
        st.header("Document Upload")
        st.file_uploader(
            "Upload an AI policy PDF document",
            type=["pdf"],
            key="pdf_uploader",
            on_change=handle_pdf_upload,
            label_visibility="collapsed" 
        )

        if st.session_state.current_pdf:
            st.success(f"**Current document:** {st.session_state.current_pdf}")
        else:
            st.info("Upload a PDF to begin.")

        st.divider() 

        st.subheader("About") 
        st.info( 
            "This chatbot uses RAG (Retrieval-Augmented Generation) to answer "
            "questions about AI policy documents. It retrieves relevant parts of "
            "the document and generates accurate answers using Google's Gemini model."
        )

    if st.session_state.current_pdf:
        st.header(f"Chat about: {st.session_state.current_pdf}")

        for message in st.session_state.chat_history:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
                if message["role"] == "assistant" and "sources" in message and message["sources"]:
                    sources_text = []
                    for source in message["sources"]:
                        page_num = source.get('page', 'N/A')
                        if isinstance(page_num, int):
                            page_num += 1 
                        sources_text.append(
                            f"**Page:** {page_num}"
                            # f"**Document:** {source.get('title', 'N/A')}, " 
                        )
                    st.caption("Sources: " + ", ".join(sources_text))

        st.chat_input(
            "Ask a question about " + st.session_state.current_pdf + "...", 
            key="question_input",
            on_submit=handle_question 
        )

    else:
        st.info("👈 Upload a PDF document using the sidebar to start chatting.")


if __name__ == "__main__":
    main()
