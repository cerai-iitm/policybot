import os
import uuid

import streamlit as st

from src.config import cfg
from src.logger import logger
from src.rag import ChatManager, LLM_Interface
from src.util import (get_pdf_files_with_embeddings, read_pdf_processor_result,
                      read_retriever_result, run_pdf_processor,
                      run_retriever_subprocess)

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
    logger.debug(f"Created new session with id: {st.session_state['session_id']}")
if "messages" not in st.session_state:
    st.session_state["messages"] = []
if "current_query" not in st.session_state:
    st.session_state["current_query"] = None
if "pdf_files" not in st.session_state:
    st.session_state["pdf_files"] = get_pdf_files_with_embeddings()
if "selected_filename" not in st.session_state:
    st.session_state["selected_filename"] = (
        None
        if len(st.session_state["pdf_files"]) == 0
        else st.session_state["pdf_files"][0]
    )
if "test" not in st.session_state:
    st.session_state["test"] = 0
if "show_success_message" not in st.session_state:
    st.session_state["show_success_message"] = False
if "show_error_message" not in st.session_state:
    st.session_state["show_error_message"] = False
if "error_message" not in st.session_state:
    st.session_state["error_message"] = None


def update_session_state():
    st.session_state["selected_filename"] = st.session_state["pdf_file_selector"]
    st.success(f"Selected PDF file: {st.session_state['selected_filename']}")
    logger.info(
        f"Updated selected file using selector to: {st.session_state['selected_filename']}"
    )


st.sidebar.selectbox(
    "Select a PDF file",
    key="pdf_file_selector",
    options=st.session_state["pdf_files"],
    index=(
        0
        if st.session_state["pdf_files"] and not st.session_state["selected_filename"]
        else (
            st.session_state["pdf_files"].index(st.session_state["selected_filename"])
            if st.session_state["selected_filename"] in st.session_state["pdf_files"]
            else 0
        )
    ),
    help="Select a previously uploaded PDF file to use for querying.",
    on_change=update_session_state,
)

pdf_file = st.sidebar.file_uploader("Upload a PDF file", type=cfg.ALLOWED_EXTENSIONS)

if pdf_file is not None:
    if st.sidebar.button("Process PDF"):
        try:
            os.makedirs(cfg.DATA_DIR, exist_ok=True)
            pdf_path = os.path.join(cfg.DATA_DIR, pdf_file.name)

            with open(pdf_path, "wb") as f:
                f.write(pdf_file.getbuffer())
            logger.info(f"Uploaded PDF file saved to: {pdf_path}")

            with st.spinner("Processing PDF..."):
                progress_text = st.empty()
                temp_file_path = None
                returncode = None

                for update in run_pdf_processor(pdf_file.name):
                    if "progress" in update:
                        # Update the text inside the spinner
                        progress_text.info(update["progress"])
                    elif "temp_file_path" in update:
                        temp_file_path = update["temp_file_path"]
                        returncode = update["returncode"]

                progress_text.empty()

                if returncode == 0 and temp_file_path:
                    result = read_pdf_processor_result(temp_file_path)
                    if result.get("success"):
                        st.session_state["selected_filename"] = pdf_file.name
                        st.session_state["pdf_files"] = get_pdf_files_with_embeddings()
                        st.session_state["show_success_message"] = True
                        st.rerun()
                    else:
                        error_msg = result.get("error", "Unknown error occurred")
                        st.session_state["error_message"] = error_msg
                        st.session_state["show_error_message"] = True
                else:
                    st.session_state["error_message"] = "PDF processor failed to run."
                    st.session_state["show_error_message"] = True

        except Exception as e:
            st.session_state["error_message"] = str(e)
            st.session_state["show_error_message"] = True

if st.session_state["show_success_message"]:
    st.success(
        f"PDF file uploaded and processed successfully: {st.session_state['selected_filename']}"
    )
    st.session_state["show_success_message"] = False

if st.session_state["show_error_message"]:
    st.error(
        f"An error occured while processing PDF: {st.session_state['error_message']}"
    )
    st.session_state["show_error_message"] = False

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

    # Create a single placeholder at the top of your chat/response area
    spinner_placeholder = st.empty()

    try:
        # Retrieval spinner and progress
        with spinner_placeholder.container():
            with st.spinner("Retrieving chunks..."):
                progress_placeholder = st.empty()
                temp_file_path = None
                returncode = None
                for update in run_retriever_subprocess(
                    query=query,
                    file_name=st.session_state["selected_filename"],
                    top_k=cfg.TOP_K,
                ):
                    if "progress" in update:
                        progress_placeholder.info(update["progress"])
                    elif "temp_file_path" in update:
                        temp_file_path = update["temp_file_path"]
                        returncode = update["returncode"]

        # After retrieval, update the same placeholder for generation
        if returncode == 0 and temp_file_path:
            result = read_retriever_result(temp_file_path)
            if not result or not result.get("success"):
                response = (
                    "No relevant information found in the document for your query."
                )
                chunks = []
            else:
                chunks = result.get("chunks", [])
                if not isinstance(chunks, list):
                    chunks = [str(chunks)]
                else:
                    chunks = [str(chunk) for chunk in chunks]
                with spinner_placeholder.container():
                    with st.spinner("Generating result..."):
                        response = llm_interface.generate_response(
                            session_id=st.session_state["session_id"],
                            chat_manager=chat_manager,
                            context_chunks=chunks,
                            query=query,
                        )
        else:
            response = "Retriever failed to run."
            chunks = []

        spinner_placeholder.empty()  # Remove spinner/progress after done

        with st.chat_message("assistant"):
            st.markdown(response)
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
        st.rerun()
