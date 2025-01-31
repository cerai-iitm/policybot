# AI-Policy-Chatbot

This project is an AI-powered chatbot that processes and answers questions based on uploaded PDFs using language models and vector search.

## Prerequisites

Ensure you have the following installed before running the project:

### 1. Set up Ollama  
Install and configure [Ollama](https://ollama.com) on your system.

### 2. Run the DeepSeek model  
Execute the following command to load and run the required model:
```sh
ollama run deepseek-r1:1.5b
```

### 3. Install Dependencies  
Install the required Python dependencies:
```sh
pip install -r requirements.txt
```

## Usage

### 1. Upload PDFs  
Place all the PDF documents inside the `pdfs` directory.

### 2. Preprocess the PDFs  
Run the following command to process and index the PDFs:
```sh
python main.py preprocess
```

### 3. Start the Chatbot  
Launch the Streamlit application:
```sh
streamlit run streamlit_app.py
```

## Features (Modes of Chat)
1. Regular Chat: A standard chat setup with RAG (Retrieval-Augmented Generation) enabled.

2. Single PDF Chat: Upload a PDF and ask questions specifically about its content (RAG is applied only to that PDF).

3. Direct Chat: No RAG; you can provide context manually within the chat itself.


## Notes
- Ensure Ollama is running before starting the chatbot.
- The preprocessing step is required every time new PDFs are added.

