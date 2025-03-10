import streamlit as st
import tempfile
import os
from src.document_processing.loader import upload_pdf, load_pdf, split_text
from src.qa_system.retriever import retrieve_docs, index_documents
from src.qa_system.answering import answer_question
from src.qa_system.single_pdf import process_single_pdf
from src.qa_system.direct_chat import get_direct_response
from src.utils.logging_utils import setup_logger, log_direct_interaction
from src.config.settings import PDFS_UPLOAD_DIR

st.set_page_config(page_title="AI Policy Chatbot", layout="wide")

def init_session_state():
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "temp_pdf_docs" not in st.session_state:
        st.session_state.temp_pdf_docs = None
    if "show_reasoning" not in st.session_state:
        st.session_state.show_reasoning = False

def display_chat_messages():
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            
            # Display reasoning if available and enabled
            if st.session_state.show_reasoning and message.get("role") == "assistant" and message.get("reasoning"):
                with st.expander("Show reasoning"):
                    st.markdown(message["reasoning"])

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
    
    # Add toggle for showing reasoning steps
    st.session_state.show_reasoning = st.sidebar.checkbox("Show reasoning steps", value=st.session_state.show_reasoning)
    
    if query := st.chat_input("Chat directly with the model"):
        st.session_state.messages.append({"role": "user", "content": query})
        with st.chat_message("user"):
            st.markdown(query)

        with st.chat_message("assistant"):
            response_data = get_direct_response(
                query, 
                context, 
                model_name=model_template,  
            )
            
            # Extract components
            reasoning = response_data.get("reasoning", "")
            answer = response_data.get("answer", "")
            full_response = response_data.get("full_response", "")
            
            # Display the answer
            st.markdown(answer)
            
            # Show reasoning in an expander if available and enabled
            if reasoning and st.session_state.show_reasoning:
                with st.expander("Show reasoning"):
                    st.markdown(reasoning)
            
            # Save to chat history with reasoning included
            st.session_state.messages.append({
                "role": "assistant", 
                "content": answer,
                "reasoning": reasoning,
                "full_response": full_response
            })
            
            # Log the interaction
            log_direct_interaction(logger, query, context, response_data)

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
