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

## Installation & Usage

### Docker Installation

1. **Clone the repository**

   ```bash
   git clone https://github.com/cerai-iitm/policybot.git
   cd policybot
   ```

2. **Configure Environment Variables**

   ```bash
   cp backend/.env.example backend/.env
   ```

   Edit `backend/.env` and update the required variables:
   - `OLLAMA_IP`: Keep default `host.docker.internal` for local Ollama
   - `OLLAMA_PORT`: Keep default `11434`
   - Other variables as needed (see `backend/.env.example` for details)

3. **Install and Run Ollama**
   - If you don't have Ollama installed, follow instructions at [https://ollama.com/download](https://ollama.com/download).
   - Start Ollama:
     ```bash
     OLLAMA_HOST=0.0.0.0 ollama serve
     ```
   - Pull a model:
     ```bash
     ollama pull gemma3n:e4b
     ```

4. **(Optional) Enable GPU Access**
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

5. **Deploy the Application**

   **For Production:**

   ```bash
   make deploy
   ```

   This will build images, download models, and start all services. Visit the app at [http://localhost:80/policybot](http://localhost:80/policybot).

   **For Development:**

   ```bash
   make dev
   ```

   This will start services with hot-reload enabled. Access at [http://localhost:80/policybot](http://localhost:80/policybot).

6. **Access the logs**
   - To enter the running Docker container and view logs:

     ```bash
     docker exec -it backend tail -f logs/app.log
     ```

## v2.0.0 — Release Highlights

**Summary:** Major refactor and migration to a production-ready stack — backend moved to `FastAPI`, frontend rewritten in `Next.js`, retrieval moved to `Qdrant` with async RAG
flows, and improved concurrent query handling for multiple users.

**Notable changes you can find in the code:**

- `backend/main.py`: FastAPI entrypoint (replaces prior Streamlit app).
- `backend/src/routers/`: API routes such as `chat.py` and `pdf.py`.
- `backend/src/rag/`: RAG pipeline modules (`retriever.py`, `LLM_interface.py`, `chat_manager.py`, `pdf_processor.py`).
- `frontend/src/app/`: Complete Next.js frontend redesign.
- `docker-compose.yml` and `nginx.conf`: Updated to run backend and frontend services.
- `download_models.py` and `entrypoint.sh`: Model and startup updates.

**Notes:** If you used the old Streamlit UI, it's now replaced by the Next.js frontend. Start services with `docker compose up` and visit `http://localhost:80`.
