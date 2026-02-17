import asyncio
from typing import AsyncGenerator, Dict, List, Optional

from langchain_classic.chains.llm import LLMChain
from langchain_classic.chains.summarize import load_summarize_chain
from langchain_core.documents import Document
from langchain_core.messages import BaseMessage
from langchain_core.prompts import (
    ChatPromptTemplate,
    MessagesPlaceholder,
    PromptTemplate,
)
from openai import AsyncOpenAI

from src.core import cfg, logger

from .chat_manager import ChatManager
from .external import External


class LLM_Interface:
    def __init__(self, model_name: str = cfg.MODEL_NAME) -> None:
        """
        Initialize LLM interface with optional model override.

        Args:
            model_name: Model ID to use. If None, uses backend default (cfg.MODEL_NAME).
        """
        effective_model = model_name or cfg.MODEL_NAME
        logger.info(f"Initializing LLM_Interface with model: {effective_model}")

        self.system_prompt = cfg.SYSTEM_PROMPT
        self.max_history_messages = cfg.MAX_HISTORY_MESSAGES
        self.model_name = effective_model
        self.llm = External.create_llm(effective_model)
        if self.llm is None:
            raise ValueError(
                "LLM initialization failed. Ensure LLM_PROVIDER is configured correctly."
            )
        self.chain = self._create_chain()
        self.chat_manager = ChatManager()

    async def _direct_chat_completion(
        self, messages: List[Dict], max_tokens: int = 1000, timeout: int = 60
    ) -> Optional[str]:
        """
        Perform a direct async chat completion using AsyncOpenAI client.
        Returns the text if successful, otherwise None on timeout/error.
        """
        try:
            client = AsyncOpenAI(
                api_key=cfg.VLLM_LLM_API_KEY, base_url=cfg.VLLM_LLM_URL
            )
            logger.info(
                f"LLM direct call to {self.model_name}",
                extra={
                    "model": self.model_name,
                    "max_tokens": max_tokens,
                    "timeout": timeout,
                    "num_messages": len(messages),
                },
            )
            # Debug: log first 200 chars of user message
            if messages and len(messages) > 1:
                user_msg = messages[-1].get("content", "")[:200]
                logger.debug(f"User message preview: {user_msg}...")

            resp = await asyncio.wait_for(
                client.chat.completions.create(
                    model=self.model_name,
                    messages=messages,
                    max_tokens=max_tokens,
                    temperature=cfg.TEMPERATURE,
                ),
                timeout=timeout,
            )

            # Extract content robustly
            logger.debug(f"Raw response object: {resp}")
            if hasattr(resp, "choices") and resp.choices:
                choice = resp.choices[0]
                logger.debug(f"First choice: {choice}")
                if hasattr(choice, "message"):
                    content = choice.message.content
                    logger.debug(
                        f"Message content type: {type(content)}, value: {content}"
                    )
                    if content and isinstance(content, str) and content.strip():
                        logger.info(f"LLM response received, length: {len(content)}")
                        return content
                    else:
                        logger.warning(f"LLM returned empty or whitespace-only content")
                        return None
                else:
                    logger.warning(f"Choice has no message attribute")
            else:
                logger.warning(f"Response has no choices or choices is empty")
            logger.warning("LLM returned no valid content")
            return None
        except asyncio.TimeoutError:
            logger.warning(f"LLM request timed out after {timeout}s")
            return None
        except Exception as e:
            logger.error(f"LLM direct call failed: {e}", exc_info=True)
            return None

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
            document = External.extract_llm_output(document)

            response = await asyncio.to_thread(
                self.llm.invoke,
                cfg.QUERY_REWRITE_SYSTEM_PROMPT.format(query=query, summary=summary),
            )
            response = External.extract_llm_output(response)
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

    async def generate_rewritten_queries_batched(
        self, query: str, summary: str
    ) -> List[str]:
        """Batched query generation - HyDE doc + query rewrite in single vLLM call.

        Uses OpenAI-compatible batching to send both prompts in one request,
        reducing API calls from 2 to 1 when using vLLM provider.
        """
        if cfg.LLM_PROVIDER != "vllm":
            # Fallback to sequential for non-vLLM providers
            return await self.generate_rewritten_queries(query, summary)

        try:
            from openai import AsyncOpenAI

            logger.info("Using batched vLLM query generation")

            # Stateless: fresh client per request
            client = AsyncOpenAI(
                api_key=cfg.VLLM_LLM_API_KEY, base_url=cfg.VLLM_LLM_URL
            )

            # Prepare both prompts
            doc_prompt = cfg.GENERATED_EXAMPLE_DOCUMENT_PROMPT.format(
                query=query, summary=summary
            )
            rewrite_prompt = cfg.QUERY_REWRITE_SYSTEM_PROMPT.format(
                query=query, summary=summary
            )

            # Make two parallel API calls (proper async batching)
            doc_task = client.chat.completions.create(
                model=cfg.VLLM_LLM_MODEL,
                messages=[{"role": "user", "content": doc_prompt}],
                temperature=cfg.VLLM_LLM_TEMPERATURE,
                max_tokens=1000,
            )

            rewrite_task = client.chat.completions.create(
                model=cfg.VLLM_LLM_MODEL,
                messages=[{"role": "user", "content": rewrite_prompt}],
                temperature=cfg.VLLM_LLM_TEMPERATURE,
                max_tokens=1000,
            )

            # Wait for both to complete in parallel
            doc_response, rewrite_response = await asyncio.gather(
                doc_task, rewrite_task
            )

            # Extract both responses
            document = doc_response.choices[0].message.content
            rewritten = rewrite_response.choices[0].message.content

            logger.info(f"Generated batched queries: {str(rewritten)[:30]}...")

            # Process as before
            rewritten_queries = str(rewritten).split("\n")
            rewritten_queries.append(str(document).strip())
            rewritten_queries = [q.strip() for q in rewritten_queries if q.strip()]
            rewritten_queries.append(query.strip())

            logger.info(f"Total queries generated: {len(rewritten_queries)}")
            return rewritten_queries

        except Exception as e:
            logger.error(f"Error in batched query generation: {e}")
            # Fallback to sequential method
            logger.info("Falling back to sequential query generation")
            return await self.generate_rewritten_queries(query, summary)

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
            if not query or not query.strip():
                raise ValueError("Query cannot be empty")

            logger.info(f"Generating response for query: {query[:30]}...")

            # Format context and history
            formatted_context = self._format_context(context_chunks)
            history = chat_manager.get_history(session_id)
            formatted_history = self._format_history(history)

            # Build prompt string
            user_prompt = (
                f"Context:\n\n{formatted_context}\n\nQuestion: {query.strip()}"
            )

            # Build messages
            messages = [
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": user_prompt},
                {"role": "assistant", "content": ""},
            ]

            # Run async function synchronously
            response = asyncio.run(
                self._direct_chat_completion(messages, max_tokens=1000, timeout=60)
            )

            if response:
                logger.info(f"Generated response: {str(response)[:30]}...")
                return response
            else:
                logger.warning("LLM returned no response")
                return "[LLM Error: No response generated]"

        except ValueError as ve:
            logger.error(f"Input validation error: {ve}")
            return f"Input Error: {ve}"
        except Exception as e:
            logger.error(f"LLM response generation failed: {e}")
            import traceback

            logger.error(f"Full traceback: {traceback.format_exc()}")
            return "[LLM Error: Could not generate response]"

    async def agenerate_response(
        self,
        session_id: str,
        chat_manager: ChatManager,
        context_chunks: List[str],
        query: str,
    ) -> str:
        """Async version of generate_response using direct AsyncOpenAI call."""
        try:
            if not query or not query.strip():
                raise ValueError("Query cannot be empty")

            logger.info(f"Async generating response for query: {query[:30]}...")

            # Format context and history
            formatted_context = self._format_context(context_chunks)
            history = chat_manager.get_history(session_id)
            formatted_history = self._format_history(history)

            # Build prompt string
            user_prompt = (
                f"Context:\n\n{formatted_context}\n\nQuestion: {query.strip()}"
            )

            # Build messages
            messages = [
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": user_prompt},
                {"role": "assistant", "content": ""},
            ]

            # Call direct async OpenAI
            response = await self._direct_chat_completion(
                messages, max_tokens=1000, timeout=60
            )

            if response:
                logger.info(f"Generated async response: {str(response)[:30]}...")
                return response
            else:
                logger.warning("LLM returned no async response")
                return "[LLM Error: No response generated]"

        except ValueError as ve:
            logger.error(f"Input validation error: {ve}")
            return f"Input Error: {ve}"
        except Exception as e:
            logger.error(f"LLM async response generation failed: {e}")
            import traceback

            logger.error(f"Full traceback: {traceback.format_exc()}")
            return "[LLM Error: Could not generate response asynchronously]"

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
                chunk = External.extract_llm_output(chunk)
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
        result = External.extract_llm_output(result)
        return result.strip()

    async def generate_suggested_queries(
        self, summary: str, session_id: str
    ) -> List[str]:
        history = self.chat_manager.get_history(session_id)
        logger.info("Generating suggested queries based on summary and history")
        formatted_history = self._format_history(history)

        prompt = PromptTemplate(
            input_variables=["summary", "history"],
            template=cfg.SUGGESTED_QUERIES_PROMPT,
        )
        chain = LLMChain(llm=self.llm, prompt=prompt)

        result = await chain.arun({"summary": summary, "history": formatted_history})

        queries = [q.strip() for q in result.split("\n") if q.strip()]
        return queries
