def str2bool(value):
    return str(value).lower() in ("true", "1", "yes", "on")


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
