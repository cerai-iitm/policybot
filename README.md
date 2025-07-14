# PolicyBot

A Retrieval-Augmented Generation (RAG) application for extracting and answering questions from Policy documents using LLMs.

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
     ollama pull llama3.1:8b
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
   docker-compose up --build
   ```

   This will:

   - Build the Docker image.
   - Start the app at [http://localhost:8501](http://localhost:8501).

5. **Access the logs**

   - To enter the running Docker container and view logs:

     ```bash
     docker exec -it rag_app tail -f app.log
     ```

</details>
