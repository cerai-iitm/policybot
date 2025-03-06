import streamlit as st
import pandas as pd
import os
import json
import time
from datetime import datetime
import matplotlib.pyplot as plt
import seaborn as sns
from src.qa_system.direct_chat import get_direct_response
from src.qa_system.answering import answer_question
from src.evaluation.simple_evaluator import SimpleEvaluator
from src.evaluation.pipeline import EvaluationPipeline
from langchain_core.documents import Document
from src.utils.logging_utils import setup_logger, log_evaluation

# Setup evaluation logger
eval_logger = setup_logger("evaluation")

# Initialize the evaluation pipeline
@st.cache_resource
def load_evaluation_pipeline():
    return EvaluationPipeline(
        output_dir=os.path.join('logs', 'evaluation_results'),
        use_advanced_metrics=True
    )

def save_evaluation_record(record):
    """Save evaluation record to a CSV file"""
    record_path = os.path.join('logs', 'evaluations.csv')
    os.makedirs(os.path.dirname(record_path), exist_ok=True)
    
    # Add timestamp
    record['timestamp'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # Check if file exists
    if os.path.exists(record_path):
        df = pd.read_csv(record_path)
        df = pd.concat([df, pd.DataFrame([record])], ignore_index=True)
    else:
        df = pd.DataFrame([record])
    
    df.to_csv(record_path, index=False)

st.set_page_config(page_title="LLM Response Evaluator", layout="wide")

# Add new sidebar option for advanced metrics
with st.sidebar:
    st.title("Settings")
    use_advanced_metrics = st.checkbox("Use Advanced Metrics", value=True, 
                                    help="Enable additional metrics like entity analysis and factual consistency")
    
    visualization_type = st.selectbox(
        "Visualization Type", 
        ["Basic", "Detailed", "None"],
        help="Choose how to visualize evaluation results"
    )

# Initialize evaluation pipeline with settings
if "evaluation_pipeline" not in st.session_state or st.session_state.use_advanced_metrics != use_advanced_metrics:
    st.session_state.evaluation_pipeline = EvaluationPipeline(use_advanced_metrics=use_advanced_metrics)
    st.session_state.use_advanced_metrics = use_advanced_metrics

st.title("Enhanced LLM Response Evaluator")
st.markdown("""
This tool helps you evaluate the quality of LLM-generated answers by comparing them with human reference answers.
1. Enter context and question to generate an LLM response
2. Provide your own reference answer
3. Get detailed evaluation metrics comparing the two
""")

# Initialize session state for tracking generated answers
if "llm_response" not in st.session_state:
    st.session_state.llm_response = None
if "evaluation_results" not in st.session_state:
    st.session_state.evaluation_results = None
if "evaluation_history" not in st.session_state:
    st.session_state.evaluation_history = []

# Create tabs for the application
tab1, tab2, tab3 = st.tabs(["Generate & Evaluate", "Evaluation History", "Batch Evaluation"])

with tab1:
    # Input section
    st.header("Input")
    col1, col2 = st.columns([3, 2])
    
    with col1:
        context = st.text_area("Context", height=200, placeholder="Enter the context information here...")
    
    with col2:
        question = st.text_area("Question", height=100, placeholder="Enter your question here...")
        response_mode = st.radio(
            "Response Generation Mode",
            ["Direct Chat (context as input)", "QA (context as retrieval)"]
        )
    
    # Generate LLM response
    if st.button("Generate LLM Response"):
        if not question.strip():
            st.error("Please enter a question")
        else:
            with st.spinner("Generating response..."):
                start_time = time.time()
                
                if response_mode == "Direct Chat (context as input)":
                    llm_response = get_direct_response(question, context)
                else:
                    doc = Document(page_content=context)
                    llm_response = answer_question(question, [doc], mode="evaluation")
                
                generation_time = time.time() - start_time
                
                st.session_state.llm_response = {
                    "text": llm_response,
                    "generation_time": f"{generation_time:.2f} seconds"
                }
    
    # Display the generated response
    if st.session_state.llm_response:
        st.header("LLM Response")
        st.info(st.session_state.llm_response["text"])
        st.caption(f"Generation time: {st.session_state.llm_response['generation_time']}")
        
        # Human reference answer input
        st.header("Human Reference Answer")
        human_answer = st.text_area("Enter your reference answer", height=150)
        
        # Evaluate button
        if st.button("Evaluate Response"):
            if not human_answer.strip():
                st.error("Please enter a reference answer")
            else:
                with st.spinner("Evaluating..."):
                    evaluation_pipeline = st.session_state.evaluation_pipeline
                    results = evaluation_pipeline.evaluate(
                        human_answer, 
                        st.session_state.llm_response["text"],
                        context,
                        question
                    )
                    
                    st.session_state.evaluation_results = results
                    
                    # Log the evaluation
                    eval_record = {
                        "question": question,
                        "context": context[:100] + "..." if len(context) > 100 else context,
                        "llm_answer": st.session_state.llm_response["text"],
                        "human_answer": human_answer,
                        **results
                    }
                    
                    # Log evaluation to file using the logger
                    log_evaluation(
                        eval_logger,
                        question,
                        context, 
                        st.session_state.llm_response["text"],
                        human_answer,
                        results
                    )
                    
                    # Add to history
                    st.session_state.evaluation_history.append(eval_record)
                    
                    # Save to CSV
                    save_evaluation_record(eval_record)
        
        # Display evaluation results
        if st.session_state.evaluation_results:
            st.header("Evaluation Results")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Overall Score", f"{st.session_state.evaluation_results['final_score']:.3f}")
                st.metric("Semantic Similarity", f"{st.session_state.evaluation_results['similarity']:.3f}")
            
            with col2:
                st.metric("ROUGE-L", f"{st.session_state.evaluation_results['rougeL']:.3f}")
                st.metric("ROUGE-1", f"{st.session_state.evaluation_results['rouge1']:.3f}")
                st.metric("ROUGE-2", f"{st.session_state.evaluation_results['rouge2']:.3f}")
            
            with col3:
                st.metric("Question Relevance", f"{st.session_state.evaluation_results['question_relevance']:.3f}")
                st.metric("Context Relevance", f"{st.session_state.evaluation_results['context_relevance']:.3f}")
            
            # Interpretation guide
            st.subheader("Score Interpretation")
            st.markdown("""
            - **Overall Score**: Weighted combination of all metrics (higher is better)
            - **Semantic Similarity**: How similar the meaning of the two answers is (0-1)
            - **ROUGE Scores**: Overlap of n-grams between answers (0-1)
            - **Relevance Scores**: How relevant the LLM answer is compared to the human answer (0-1)
            
            Typically, scores above 0.7 indicate good quality answers that align well with human references.
            """)

with tab2:
    st.header("Evaluation History")
    
    if not st.session_state.evaluation_history:
        st.info("No evaluations recorded yet. Generate and evaluate responses in the first tab.")
    else:
        # Convert history to DataFrame
        history_df = pd.DataFrame(st.session_state.evaluation_history)
        
        # Display summary statistics
        st.subheader("Summary Statistics")
        stats = history_df[['final_score', 'similarity', 'rougeL']].describe()
        st.dataframe(stats)
        
        # Display full history
        st.subheader("Full Evaluation History")
        st.dataframe(history_df)
        
        # Option to download history
        csv = history_df.to_csv(index=False)
        st.download_button(
            label="Download Evaluation History as CSV",
            data=csv,
            file_name=f"evaluation_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )
        
        # Clear history button
        if st.button("Clear History"):
            st.session_state.evaluation_history = []
            st.success("History cleared!")
            st.experimental_rerun()

with tab3:
    st.header("Batch Evaluation")
    
    st.markdown("""
    Upload a CSV file with the following columns:
    - `question`: The question to ask
    - `context`: The context to use (optional)
    - `human_answer`: The reference human answer
    """)
    
    uploaded_file = st.file_uploader("Upload CSV file", type="csv")
    
    if uploaded_file:
        data = pd.read_csv(uploaded_file)
        st.write("Preview of uploaded data:")
        st.dataframe(data.head())
        
        required_cols = ["question", "human_answer"]
        missing_cols = [col for col in required_cols if col not in data.columns]
        
        if missing_cols:
            st.error(f"Missing required columns: {', '.join(missing_cols)}")
        else:
            # Check if context column exists, if not add an empty one
            if "context" not in data.columns:
                data["context"] = ""
            
            st.write(f"File contains {len(data)} questions to evaluate.")
            
            if st.button("Run Batch Evaluation"):
                results = []
                
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                for i, row in enumerate(data.iterrows()):
                    row = row[1]  # Get the row data
                    status_text.text(f"Processing question {i+1}/{len(data)}")
                    
                    # Generate LLM response
                    if response_mode == "Direct Chat (context as input)":
                        llm_response = get_direct_response(row["question"], row["context"])
                    else:
                        doc = Document(page_content=row["context"])
                        llm_response = answer_question(row["question"], [doc], mode="evaluation")
                    
                    # Evaluate
                    evaluation_pipeline = st.session_state.evaluation_pipeline
                    scores = evaluation_pipeline.evaluate(
                        row["human_answer"], 
                        llm_response,
                        row["context"],
                        row["question"]
                    )
                    
                    # Store results
                    results.append({
                        "question": row["question"],
                        "context": row["context"],
                        "human_answer": row["human_answer"],
                        "llm_answer": llm_response,
                        **scores
                    })
                    
                    # Update progress
                    progress_bar.progress((i + 1) / len(data))
                
                # Convert results to DataFrame
                results_df = pd.DataFrame(results)
                
                # Display results
                st.subheader("Batch Evaluation Results")
                st.write(f"Average score: {results_df['final_score'].mean():.3f}")
                st.dataframe(results_df)
                
                # Option to download results
                csv = results_df.to_csv(index=False)
                st.download_button(
                    label="Download Results as CSV",
                    data=csv,
                    file_name=f"batch_evaluation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )

# Sidebar with instructions
st.sidebar.title("Instructions")
st.sidebar.info("""
### How to use this tool

1. Enter context information and a question
2. Generate an LLM response
3. Provide your own reference answer
4. Get detailed evaluation metrics

### Metrics Explained

- **Semantic Similarity**: Measures how similar the meanings are
- **ROUGE Scores**: Measures word overlap between answers
- **Relevance Scores**: Measures how well answers address the question and context
""")

# Add evaluation logs viewer in sidebar
st.sidebar.markdown("---")
st.sidebar.subheader("Recent Evaluation Logs")

log_path = os.path.join('logs', 'evaluation.log')
if os.path.exists(log_path):
    with open(log_path, 'r') as f:
        log_content = f.readlines()[-20:]  # Show last 20 lines
    
    log_text = ''.join(log_content)
    st.sidebar.text_area("Log entries (last 20 lines)", log_text, height=200)
else:
    st.sidebar.info("No evaluation logs found")
