import streamlit as st
import re
import os
from src.document_processing.loader import upload_pdf, load_pdf, split_text
from src.qa_system.retriever import retrieve_docs, index_documents
from src.qa_system.answering import answer_question
from src.qa_system.single_pdf import process_single_pdf
from src.qa_system.direct_chat import get_direct_response
from src.utils.logging_utils import setup_logger, log_direct_interaction, configure_root_logger
from src.config.settings import PDFS_UPLOAD_DIR
from src.evaluation.simple_evaluator import SimpleEvaluator
import logging

# Configure root logger to only show warnings and errors in console
configure_root_logger(console_level=logging.WARNING)

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
    
    # NEW: Add human reference answer for evaluation in the sidebar
    human_ref = st.sidebar.text_area("Human Reference Answer for Evaluation", height=100, 
                                     placeholder="Enter human answer to compare...", key="human_ref")
    
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
            
            # Extract only the final answer
            final_answer = response_data.get("answer", "")
            
            # Display the final answer
            st.markdown(final_answer)
            
            # Show reasoning if available and enabled
            if response_data.get("reasoning") and st.session_state.show_reasoning:
                with st.expander("Show reasoning"):
                    st.markdown(response_data.get("reasoning"))
            
            # Save to chat history with only the final answer
            st.session_state.messages.append({
                "role": "assistant", 
                "content": final_answer,
                "reasoning": response_data.get("reasoning", ""),
                "full_response": final_answer
            })
            
            # If a human reference is provided, perform evaluation using SimpleEvaluator
            if human_ref.strip():
                evaluator = SimpleEvaluator(use_advanced_metrics=False)
                
                # Extract the answer content from JSON objects in the response if present
                final_answer_content = final_answer
                
                try:
                    # Try to find JSON-like objects in the text
                    import json
                    import re
                    
                    # Look for JSON objects using a safer regex pattern that matches JSON structure
                    json_pattern = r'(\{[^{}]*(\{[^{}]*\})*[^{}]*\})'
                    json_objects = re.findall(json_pattern, final_answer)
                    
                    if json_objects:
                        for json_str, _ in json_objects:
                            try:
                                # Try to parse as JSON (safer than eval)
                                parsed_obj = json.loads(json_str)
                                
                                # Check if this is a "Final Answer" object
                                if isinstance(parsed_obj, dict) and parsed_obj.get("title") == "Final Answer":
                                    final_answer_content = parsed_obj.get("content", "")
                                    break
                            except json.JSONDecodeError:
                                # If JSON parsing fails, continue with the next potential match
                                continue
                                
                except Exception as e:
                    # If any error occurs during parsing, fall back to using the full answer
                    st.warning(f"Error parsing structured response: {str(e)}")
                    
                # Evaluate using simple metrics (only basic ones)
                print("final_ans", final_answer_content)
                print("******************************")
                scores = evaluator.evaluate_answer(human_ref, final_answer_content, context, query)
                st.info(f"Evaluation - Final Score: {scores.get('final_score', 'N/A')}")
                
                # Log what was compared
                logger.info(f"Evaluation Comparison - Human Answer: {human_ref}")
                logger.info(f"Evaluation Comparison - LLM Answer: {final_answer_content}")
                logger.info(f"Evaluation Metrics: {scores}")
            
            # Also log the original response data for reference if needed
            log_direct_interaction(logger, query, context, {
                "answer": final_answer,
                "reasoning": response_data.get("reasoning", ""),
                "full_response": final_answer
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
