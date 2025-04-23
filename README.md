# AI Policy Chatbot

This project is an AI-powered chatbot designed to answer questions about AI policy documents. It uses Streamlit for the user interface, LangChain for processing, and Google's Gemini models for generation and embeddings.

## Features

*   Upload individual AI policy PDF documents via the Streamlit interface.
*   Ask questions about the content of the uploaded PDF.
*   Utilizes Retrieval-Augmented Generation (RAG) to provide answers based *only* on the document's content.
*   Displays sources (document title and page number) for the generated answers.

## Project Structure (Simplified)

```
.
├── uploads/              # Directory where uploaded PDFs are temporarily stored
├── vector_store/         # Directory for storing the vector database for processed PDFs
├── src/
│   ├── config/           # Configuration (settings.py)
│   ├── qa_system/        # Question-answering logic (single_pdf_app.py)
│   └── ...               # Other source modules
├── .env                  # Environment variables (needs to be created by user)
├── README.md             # This file
├── requirements.txt      # Python dependencies
└── streamlit_app.py      # Main Streamlit application file
```

## Prerequisites

1.  **Python 3.8+**: Ensure you have Python installed.
2.  **Google API Key**: You need an API key from Google AI Studio (or Google Cloud) with access to the Gemini API (specifically `gemini-1.5-pro` and `models/embedding-001` as per default settings).
3.  **Dependencies**: Install the required Python packages listed in `requirements.txt`.

## Setup

1.  **Clone the repository:**
    ```bash
    git clone <repository-url>
    cd AI-Policy-Chatbot
    ```
2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
3.  **Create a `.env` file:**
    Create a file named `.env` in the project's root directory and add your Google API key:
    ```env
    GOOGLE_API_KEY="YOUR_GOOGLE_API_KEY"
    ```
    Replace `"YOUR_GOOGLE_API_KEY"` with your actual key.

## Usage

1.  **Run the Streamlit application:**
    ```bash
    streamlit run streamlit_app.py
    ```
2.  **Upload a PDF:**
    Use the sidebar in the application to upload an AI policy PDF document. The application will process the PDF upon upload (this may take a moment).
3.  **Ask Questions:**
    Once the PDF is successfully processed, you can ask questions about its content in the chat interface. The chatbot will retrieve relevant information and generate an answer based *only* on the uploaded document.

## Configuration

Key configurations can be adjusted in `src/config/settings.py`, including:
*   Model names (`GEMINI_MODEL_NAME`, `EMBEDDING_MODEL_NAME`)
*   Text splitting parameters (`CHUNK_SIZE`, `CHUNK_OVERLAP`)
*   Retrieval parameters (`TOP_K_RESULTS`, `SIMILARITY_THRESHOLD`)
*   System prompt used for the LLM (`SYSTEM_PROMPT`)

## Notes

*   The application currently focuses on processing and querying *single* uploaded PDFs at a time.
*   Each time a new PDF is uploaded via the interface, it is processed, and the chat context resets to focus solely on that document.
*   Ensure your `GOOGLE_API_KEY` is correctly set in the `.env` file for the application to function.

