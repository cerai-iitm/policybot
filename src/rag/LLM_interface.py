from typing import Dict, List

from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import BaseMessage
from langchain_ollama.llms import OllamaLLM

from src.config import cfg
from src.logger import logger

from .chat_manager import ChatManager


class LLM_Interface:
    def __init__(self) -> None:
        self.system_prompt = cfg.SYSTEM_PROMPT
        self.max_history_messages = cfg.MAX_HISTORY_MESSAGES
        self.llm = OllamaLLM(
            model=cfg.MODEL_NAME,
            temperature=cfg.TEMPERATURE,
            base_url=cfg.OLLAMA_URL,
            num_ctx=cfg.MAX_CONTEXT_TOKENS,
        )
        self.chain = self._create_chain()

    def _create_chain(self):
        prompt = ChatPromptTemplate(
            [
                ("system", self.system_prompt),
                MessagesPlaceholder(variable_name="history"),
                ("user", "Context: {context}\n\nQuestion: {query}"),
                ("assistant", ""),
            ]
        )

        chain = (
            {
                "context": lambda x: self._format_context(x["context_chunks"]),
                "history": lambda x: self._format_history(x["history"]),
                "query": lambda x: x["query"],
            }
            | prompt
            | self.llm
        )
        return chain

    def _format_context(self, context_chunks: List[str]) -> str:
        if not context_chunks:
            logger.info("No relevant context found for LLM prompt.")
            return "No relevant context available."

        formatted_chunks = []
        for i, chunk in enumerate(context_chunks):
            if chunk and chunk.strip():
                formatted_chunks.append(f"--- Source {i + 1} ---\n{chunk.strip()}\n")

        if not formatted_chunks:
            return "No relevant context available."

        context = "\n".join(formatted_chunks)
        logger.info(f"Formatted prompt with {len(formatted_chunks)} chunks for LLM")
        return f"Retrieved Information:\n{context}"

    def _format_history(self, history: List[BaseMessage]) -> List[BaseMessage]:
        if not history:
            return []

        recent_history = history[-self.max_history_messages :]

        if len(recent_history) % 2 == 1 and len(history) > len(recent_history):
            recent_history = recent_history[1:]

        return recent_history

    def generate_rewritten_queries(self, query: str, summary: str) -> List[str]:
        try:
            document = self.llm.invoke(
                cfg.GENERATED_EXAMPLE_DOCUMENT_PROMPT.format(
                    query=query, summary=summary
                )
            )

            response = self.llm.invoke(
                cfg.QUERY_REWRITE_SYSTEM_PROMPT.format(query=query, summary=summary)
            )

            rewritten_queries = response.split("\n")
            rewritten_queries.append(document.strip())
            rewritten_queries = [
                query.strip() for query in rewritten_queries if query.strip()
            ]
            rewritten_queries.append(query.strip())
            return rewritten_queries

        except Exception as e:
            logger.error(f"Error generating rewritten queries: {e}")
            return []

    def prepare_inputs(
        self,
        session_id: str,
        chat_manager: ChatManager,
        context_chunks: List[str],
        query: str,
    ) -> Dict:

        if not query or not query.strip():
            raise ValueError("Query cannot be empty")

        history = chat_manager.get_history(session_id)

        return {
            "context_chunks": context_chunks,
            "history": history,
            "query": query.strip(),
        }

    def generate_response(
        self,
        session_id: str,
        chat_manager: ChatManager,
        context_chunks: List[str],
        query: str,
    ) -> str:
        try:
            inputs = self.prepare_inputs(
                session_id, chat_manager, context_chunks, query
            )
            logger.info(f"Generating response for query: {query[:30]}...")
            response = self.chain.invoke(inputs)
            logger.info(f"Generated response: {response[:30]}...")
            return response
        except ValueError as ve:
            logger.error(f"Input validation error: {ve}")
            return f"Input Error: {ve}"
        except Exception as e:
            logger.error(f"LLM response generation failed: {e}")
            import traceback

            logger.error(f"Full traceback: {traceback.format_exc()}")
            return "[LLM Error: Could not generate response]"
