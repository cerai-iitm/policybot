import os

from src.schema.db import SessionLocal


class Config:
    ALLOWED_EXTENSIONS = ["pdf"]

    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    DATA_DIR = os.path.join(BASE_DIR, "data")
    CHROMA_DIR = os.path.join(BASE_DIR, "chroma")

    DB_SESSION = SessionLocal()

    COLLECTION_NAME = "pdf_embeddings"

    EMBEDDING_MODEL_NAME = "Alibaba-NLP/gte-multilingual-base"
    EMBEDDING_MODEL_KWARGS = {"trust_remote_code": True}
    ENCODE_KWARGS = {"normalize_embeddings": True}
    BREAKPOINT_THRESHOLD_TYPE = "standard_deviation"
    BREAKPOINT_THRESHOLD_AMOUNT = 1.0
    MAX_HISTORY_MESSAGES = 3
    MODEL_NAME = "gemma3n:e4b"
    TEMPERATURE = 0.1
    MAX_CONTEXT_TOKENS = 32000

    RERANKING_MODEL_NAME = "BAAI/bge-reranker-base"
    TOP_K = 10
    TOP_P = 0.9
    RERANKER_TEMP = 1.3
    RRF_TEMP = 0.17

    CHUNK_SEPARATOR = "###$$$%%%^^^&&&***"
    CHUNK_PREFIX = "CHUNK_"
    RESPONSE_START = "RESPONSE_START" + CHUNK_SEPARATOR
    RESPONSE_END = CHUNK_SEPARATOR + "RESPONSE_END"
    OVERALL_SUMMARY_MAX_WORDS = 400

    FRONTEND_URL = "http://localhost:3000"
    OLLAMA_PORT = os.environ.get("OLLAMA_PORT", "11434")
    OLLAMA_IP = os.environ.get("OLLAMA_IP", "host.docker.internal")

    if os.environ.get("IN_DOCKER") == "1":
        OLLAMA_URL = f"http://{OLLAMA_IP}:{OLLAMA_PORT}"
    else:
        OLLAMA_URL = f"http://localhost:11434"

    TEMP_FILE_PATH = "/tmp/policybot_temp.txt"

    QUERY_REWRITE_SYSTEM_PROMPT = """
You are an advanced query rewriter designed to enhance retrieval performance for a RAG (Retrieval Augmented Generation) system. Your task is to generate four distinct, semantically varied reformulations of a given user query. These reformulations should aim to capture different facets, synonyms, and rephrasings of the original query, ensuring a broader and more effective document retrieval.

**Context Enhancement:**
You will be provided with a document summary that contains relevant background information. Use this summary to inform your query reformulations by:
- Incorporating domain-specific terminology and keywords present in the summary
- Understanding the broader context and scope of available information
- Leveraging technical terms, entities, and concepts mentioned in the summary
- Ensuring reformulations align with the knowledge base content

**Instructions:**
- Analyze the core intent and keywords of the provided query.
-  Review the provided summary to understand the relevant context and terminology.
- Generate four new queries that are highly relevant to the original, but offer diverse phrasing.
- Consider using synonyms, rephrasing the question, expanding on implicit concepts, or narrowing/broadening the scope slightly to explore different retrieval paths.
- Incorporate relevant terms and concepts from the summary where appropriate.
- Each generated query must be on a new line.
- Do not include any numbering, bullet points, introductory text, or concluding remarks.
- Your output must consist only of the four generated queries, each on a separate line.

**Example Input for Model Guidance:**
"What are the benefits of quantum computing?"

**Example Output for Model Guidance (Illustrative - your actual output will vary based on input):**
Advantages of quantum computation
How does quantum computing improve performance?
Applications and upsides of quantum computers
What are the positive impacts of quantum technology?

**Summary:** {summary}

Your Query (Generate results following the above for the query given below wrapped in ``): 
`{query}`
"""

    SYSTEM_PROMPT = """
You are a highly precise and factual AI assistant. Your function is to extract and present information SOLELY from the provided context. Your responses must be accurate, direct, and completely confined to the given text.

**Instructions:**
1.  **Context-Only Answers:** All information in your response MUST come directly from the provided text. Do not use any external knowledge, make assumptions, or add new details.
2.  **Factual Accuracy:** Ensure every piece of information is factually correct as per the context.
3.  **Direct Extraction Preferred:** Whenever possible, directly quote or extract the most relevant sentences or phrases from the context to answer the question. If rephrasing is necessary for clarity, it must perfectly preserve the original meaning and specific details from the text.
4.  **Complete within Context:** Provide a comprehensive answer based on all relevant details found in the provided text.
5.  **Concise and Direct:** Your answers should be straightforward and to the point. Avoid any conversational language, introductions, or extraneous information.
6.  **No Hallucination:** If the information required to answer the question is not explicitly present in the provided context, state clearly: "The provided context does not contain information on this topic."

**Output Format:**
* Present answers clearly and concisely.
* Use bullet points or numbered lists if the information from the context naturally lends itself to such organization.
* Use proper markdown formatting for the entire resposnse, including headings, bullet points, and emphasis where appropriate. Do not use any other styles like Latex or HTML. Use proper markdown syntax for generating the output. 

**Task Execution Steps:**
1.  **Read Question:** Understand the user's query precisely.
2.  **Scan Context:** Thoroughly search the provided text for all relevant information.
3.  **Identify Answer:** Locate the exact text segments that answer the question.
4.  **Construct Response:** Formulate your answer by extracting and presenting the identified information. Ensure it directly addresses the question and adheres to all instructions.
5.  **Verify:** Confirm that your answer is 100% accurate, derived *only* from the context, and meets all specified formatting.
"""

    GENERATED_EXAMPLE_DOCUMENT_PROMPT = """
You are an expert information retrieval system. Your goal is to generate a highly detailed and comprehensive hypothetical document that directly answers the given query, primarily using information from the provided summary. This hypothetical document should anticipate the kind of content a perfectly relevant document would contain.

Focus on extracting and synthesizing key facts, entities, definitions, processes, and relationships from the summary that are most pertinent to answering the query. If the summary does not contain enough information to fully answer the query, make logical inferences and add plausible, contextually relevant details to create a complete and coherent hypothetical answer. *Do not invent facts that contradict the summary.* The purpose is to create a rich, semantically similar document to aid in robust retrieval of actual documents.

Include a strong emphasis on **keywords** and **key phrases** that are highly relevant to the query and the summarized content. Think about different ways a user might search for this information.

---
**Summary:**
{summary}

---
**Query:**
{query}

---
**Hypothetical Document:**

    """

    APPLICATION_INSTRUCTIONS = """
    ## How to Use Policy Chatbot

    1. **Upload your PDF:** Use the *Upload a PDF file* button in the sidebar to upload your policy document (PDF only, max 200MB).
    2. **Process the PDF:** Click *Process PDF* to analyze your document. Wait for processing to complete.
    3. **Select the filename:** After uploading, ensure your correct filename is selected in the dropdown menu.
    4. **Ask questions:** Type your question in the chat input at the bottom of the screen. The chatbot will answer based on your document.
    5. **View context chunks:** For each answer, you can expand the *View Context Chunks* dropdown to see the exact document excerpts used to generate the response. These chunks show the specific parts of your document that were used.

    *Note: If your file doesn't appear, try refreshing the page or re-uploading.*
    """

    SUGGESTED_QUERIES_PROMPT = """
Given the following summary of the documents:

{summary}

And the following conversation history:

{history}

Based on this information, suggest 3 relevant follow-up questions a user might ask.
List each question on a separate line. Do not include any explanations or extra text—only the questions.
     """


cfg = Config()

if __name__ == "__main__":
    pass
