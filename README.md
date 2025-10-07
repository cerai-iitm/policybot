# PolicyBot

A Retrieval-Augmented Generation (RAG) application for extracting and answering questions from Policy documents using LLMs.

### Key Features

- **Document Processing**: Automated extraction and chunking of text from PDF policy documents
- **Semantic Search**: Advanced retrieval using vector embeddings for finding relevant document sections
- **Conversational AI**: Natural language question-answering with context awareness
- **Chat History**: Persistent conversation management for continuous dialogue

### How It Works

1. **Document Ingestion**: Upload PDF policy documents which are processed and split into manageable chunks
2. **Vector Storage**: Text chunks are converted to embeddings and stored in a vector database for efficient retrieval
3. **Query Processing**: User questions are embedded and matched against the document corpus using semantic similarity
4. **Response Generation**: Retrieved context is combined with the user's question and fed to a Large Language Model (LLM) for generating accurate, contextual answers
5. **Interactive Chat**: Users can ask follow-up questions with maintained conversation context

---

## Project Structure

```
policybot/
├── src/
│   ├── config.py
│   ├── logger.py
│   ├── rag/
│   │   ├── __init__.py
│   │   ├── chat_manager.py
│   │   ├── LLM_interface.py
│   │   ├── pdf_processor.py
│   │   └── retriever.py
│   └── util/
│       ├── __init__.py
│       └── util.py
├── data/ (created at runtime)
├── db/ (created at runtime)
├── chroma/ (created at runtime)
├── logs/ (created at runtime)
├── streamlit_app.py
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── .gitignore
├── .dockerignore
└── README.md
```

---

## Installation & Usage

<details>
<summary><strong>Docker Installation </strong></summary>

1. **Clone the repository**

   ```bash
   git clone https://github.com/cerai-iitm/policybot.git
   cd policybot
   ```

2. **Host Ollama on Your Machine**
   - Ensure Ollama is running on your host at port `11434`.
   - If you don't have Ollama installed, follow instructions at [https://ollama.com/download](https://ollama.com/download).
   - Start Ollama with:
     ```bash
     OLLAMA_HOST=0.0.0.0 ollama serve
     ```
   - (Optional) Pull the model, e.g.:
     ```bash
     ollama pull gemma3n:e4b
     ```
   - The app inside Docker will connect to Ollama using the special host name `host.docker.internal:11434` (default in `docker-compose.yml`).

   - **Note:** If Ollama is running on a different IP or port (not on your localhost), update the `OLLAMA_IP` and `OLLAMA_PORT` environment variables in `docker-compose.yml` to point to the correct location.

3. **Enable GPU Access**
   - Install NVIDIA Container Toolkit (for GPU support):
     ```bash
     sudo apt-get install -y nvidia-container-toolkit
     sudo systemctl restart docker
     ```
   - Edit `/etc/docker/daemon.json` to include:
     ```json
     {
       "runtimes": {
         "nvidia": {
           "path": "nvidia-container-runtime",
           "runtimeArgs": []
         }
       }
     }
     ```
   - Restart Docker after editing:
     ```bash
     sudo systemctl restart docker
     ```

4. **Start and Build the App**

   ```bash
   docker-compose up
   ```

   This will:
   - Build the Docker image.
   - Visit the app at [http://localhost:3000](http://localhost:3000).

5. **Access the logs**
   - To enter the running Docker container and view logs:

     ```bash
     docker exec -it backend tail -f logs/app.log
     ```

</details>
