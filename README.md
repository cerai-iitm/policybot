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

## Notes
- Ensure Ollama is running before starting the chatbot.
- The preprocessing step is required every time new PDFs are added.

