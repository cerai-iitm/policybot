import os
import uuid

import streamlit as st

from src.config import cfg
from src.logger import logger
from src.rag import ChatManager, LLM_Interface
from src.util import process_pdf, run_retriever

st.set_page_config(page_title="Policy Chatbot", layout="centered")


@st.cache_resource
def get_chat_manager():
    return ChatManager()


@st.cache_resource
def get_llm_interface():
    return LLM_Interface()


chat_manager = get_chat_manager()
llm_interface = get_llm_interface()


if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []
if "session_id" not in st.session_state:
    st.session_state["session_id"] = str(uuid.uuid4())
    logger.debug(f"Created new session with id: {st.session_state["session_id"]}")
if "messages" not in st.session_state:
    st.session_state["messages"] = []
if "current_query" not in st.session_state:
    st.session_state["current_query"] = None


pdf_file = st.sidebar.file_uploader("Upload a PDF file", type=cfg.ALLOWED_EXTENSIONS)

success_placeholder = st.sidebar.empty()
if pdf_file is not None:
    if st.sidebar.button("Process PDF"):
        try:
            os.makedirs(cfg.DATA_DIR, exist_ok=True)
            pdf_path = os.path.join(cfg.DATA_DIR, pdf_file.name)

            with open(pdf_path, "wb") as f:
                f.write(pdf_file.getbuffer())
            logger.info(f"PDF file saved to: {pdf_path}")

            with st.spinner("Processing PDF..."):
                result = process_pdf(file_name=pdf_file.name)

            if result.get("success", False):
                st.session_state["selected_filename"] = pdf_file.name
                success_placeholder.success(
                    "PDF file uploaded and processed successfully!"
                )
            else:
                error_msg = result.get("error", "Unknown error occurred")
                success_placeholder.error(
                    f"An error occurred while processing the PDF: {error_msg}"
                )

        except Exception as e:
            success_placeholder.error(
                f"An error occurred while processing the PDF: {e}"
            )

st.title("Policy Chatbot")

query = st.chat_input("Ask a question about the policy document...")
if query and query.strip():
    if "selected_filename" not in st.session_state:
        st.error("Please upload a PDF file first.")
    else:
        st.session_state["current_query"] = query

if "selected_filename" in st.session_state:
    try:
        chat_history = chat_manager.get_history(
            session_id=st.session_state["session_id"]
        )

        for message in chat_history:
            if hasattr(message, "type"):
                if message.type == "human":
                    role = "user"
                elif message.type == "ai":
                    role = "assistant"
                elif message.type == "system":
                    role = "system"
                else:
                    role = "assistant"
            else:
                role = "assistant"

            with st.chat_message(role):
                st.write(message.content)

                if role == "assistant" and hasattr(message, "additional_kwargs"):
                    chunks = message.additional_kwargs.get("chunks", [])
                    if chunks:
                        with st.expander("View Context Chunks"):
                            for i, chunk in enumerate(chunks):
                                st.markdown(f"**Chunk {i + 1}:**")
                                st.markdown(chunk)

    except Exception as e:
        st.error(f"Error loading chat history: {e}")
        logger.error(f"Error loading chat history: {e}")

if st.session_state.get("current_query") and "selected_filename" in st.session_state:
    query = st.session_state["current_query"]

    with st.chat_message("user"):
        st.write(query)

    chat_manager.add_message(
        session_id=st.session_state["session_id"], role="user", message=query
    )
    logger.info("User query received and processing initiated")

    try:
        with st.spinner("Retrieving chunks..."):
            chunks = run_retriever(
                query=query,
                file_name=st.session_state["selected_filename"],
                top_k=cfg.TOP_K,
            )

        if not chunks:
            response = "No relevant information found in the document for your query."
            chunks = []
        else:
            with st.spinner("Generating result..."):
                response = llm_interface.generate_response(
                    session_id=st.session_state["session_id"],
                    chat_manager=chat_manager,
                    context_chunks=chunks,
                    query=query,
                )

        with st.chat_message("assistant"):
            st.write(response)
            if chunks:
                with st.expander("View Context Chunks"):
                    for i, chunk in enumerate(chunks):
                        st.markdown(f"**Chunk {i + 1}:**")
                        st.markdown(chunk)

        chat_manager.add_message(
            session_id=st.session_state["session_id"],
            role="assistant",
            message=response,
            chunks=chunks,
        )

    except Exception as e:
        error_msg = f"Error occurred while generating answers: {e}"

        with st.chat_message("assistant"):
            st.error(error_msg)

        logger.error(error_msg)
        chat_manager.add_message(
            session_id=st.session_state["session_id"],
            role="assistant",
            message=error_msg,
        )

    finally:
        st.session_state["current_query"] = None
        st.rerun()
