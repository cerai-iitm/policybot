import asyncio
from typing import AsyncGenerator, Dict, List

from langchain.chains import LLMChain
from langchain.chains.summarize import load_summarize_chain
from langchain.prompts import (ChatPromptTemplate, MessagesPlaceholder,
                               PromptTemplate)
from langchain.schema import Document
from langchain_core.messages import BaseMessage

from src.config import cfg
from src.external import external
from src.logger import logger

from .chat_manager import ChatManager


class LLM_Interface:
    def __init__(self) -> None:
        self.system_prompt = cfg.SYSTEM_PROMPT
        self.max_history_messages = cfg.MAX_HISTORY_MESSAGES
        self.llm = external.get_llm()
        if self.llm is None:
            raise ValueError(
                "LLM initialization failed. Ensure LLM_PROVIDER is configured correctly."
            )
        self.chain = self._create_chain()
        self.chat_manager = ChatManager()

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
            logger.info("No relevant context found for given prompt.")
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

    async def generate_rewritten_queries(self, query: str, summary: str) -> List[str]:
        try:
            document = await asyncio.to_thread(
                self.llm.invoke,
                cfg.GENERATED_EXAMPLE_DOCUMENT_PROMPT.format(
                    query=query, summary=summary
                ),
            )
            document = external.extract_llm_output(document)

            response = await asyncio.to_thread(
                self.llm.invoke,
                cfg.QUERY_REWRITE_SYSTEM_PROMPT.format(query=query, summary=summary),
            )
            response = external.extract_llm_output(response)
            logger.info(f"Generated rewritten queries: {str(response)[:30]}...")

            rewritten_queries = str(response).split("\n")
            rewritten_queries.append(str(document).strip())
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

        logger.info(f"Preparing inputs for LLM with session_id: {session_id}")
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
            response = external.extract_llm_output(response)
            logger.info(f"Generated response: {str(response)[:30]}...")
            return response
        except ValueError as ve:
            logger.error(f"Input validation error: {ve}")
            return f"Input Error: {ve}"
        except Exception as e:
            logger.error(f"LLM response generation failed: {e}")
            import traceback

            logger.error(f"Full traceback: {traceback.format_exc()}")
            return "[LLM Error: Could not generate response]"

    async def generate_streaming_response(
        self,
        session_id: str,
        chat_manager: ChatManager,
        context_chunks: List[str],
        query: str,
    ) -> AsyncGenerator[str, None]:
        try:
            inputs = self.prepare_inputs(
                session_id, chat_manager, context_chunks, query
            )

            logger.info(f"Generating response for query: {query[:30]}...")

            async for chunk in self.chain.astream(inputs):
                chunk = external.extract_llm_output(chunk)
                logger.info(f"Streaming chunk: {str(chunk)[:30]}...")
                yield chunk
        except Exception as e:
            yield f"[Error: {str(e)}]"

    async def summarize_with_stuff_chain(
        self, summaries: List[Document], max_words: int = 200
    ) -> str:

        prompt = PromptTemplate(
            input_variables=["text"],
            template=f"Summarize the following content in approximately {max_words} words. Make sure to include all of the important information and keywords:\n\n{{text}}",
        )

        chain = load_summarize_chain(
            self.llm, chain_type="stuff", prompt=prompt, verbose=False
        )

        result = await chain.arun(summaries)
        result = external.extract_llm_output(result)
        return result.strip()

    async def generate_suggested_queries(
        self, summary: str, session_id: str
    ) -> List[str]:
        history = self.chat_manager.get_history(session_id)
        logger.info(f"Generating suggested queries based on summary and history")
        formatted_history = self._format_history(history)

        prompt = PromptTemplate(
            input_variables=["summary", "history"],
            template=cfg.SUGGESTED_QUERIES_PROMPT,
        )
        chain = LLMChain(llm=self.llm, prompt=prompt)

        result = await chain.arun({"summary": summary, "history": formatted_history})

        queries = [q.strip() for q in result.split("\n") if q.strip()]
        return queries
