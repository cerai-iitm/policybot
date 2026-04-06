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
from .external_service import External


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

        # Create provider-specific LLM instance via External factory.
        # External.create_llm will initialize an Ollama/langchain LLM when
        # cfg.LLM_PROVIDER == "ollama", or other providers as configured.
        self.llm = External.create_llm(effective_model)
        if self.llm is None:
            raise ValueError(
                "LLM initialization failed. Ensure LLM_PROVIDER is configured correctly."
            )

        # Build the langchain chain for providers that support it (e.g. Ollama).
        self.chain = self._create_chain()
        self.chat_manager = ChatManager()

    def _extract_content_from_resp(self, resp) -> Optional[str]:
        """
        Robustly extract final content from various vLLM/OpenAI response shapes.
        Handles:
          - chat-style: choices[0].message.content
          - text-style: choices[0].text
          - delta-style fragments: choices[0].delta.content
          - dict-like responses (raw JSON)
        Returns None if no usable content found.
        """
        try:
            # 1) object-like response with .choices
            choices = getattr(resp, "choices", None)
            if choices:
                choice = choices[0]
                # chat-style: choice.message.content
                msg = getattr(choice, "message", None)
                if msg:
                    content = getattr(msg, "content", None)
                    if content and isinstance(content, str) and content.strip():
                        logger.debug("Extracted content from choice.message.content")
                        return content
                # text-style: choice.text (vLLM text-completion format)
                text = getattr(choice, "text", None)
                if text and isinstance(text, str) and text.strip():
                    logger.debug("Extracted content from choice.text")
                    return text
                # delta-style fragment (sometimes appears even non-streaming)
                delta = getattr(choice, "delta", None)
                if isinstance(delta, dict):
                    c = delta.get("content") or delta.get("text")
                    if c and isinstance(c, str) and c.strip():
                        logger.debug("Extracted content from choice.delta")
                        return c

            # 2) dict-like response (raw JSON)
            if isinstance(resp, dict):
                chs = resp.get("choices")
                if chs:
                    ch0 = chs[0]
                    if isinstance(ch0, dict):
                        # chat message
                        m = ch0.get("message")
                        if isinstance(m, dict):
                            c = m.get("content")
                            if c and isinstance(c, str) and c.strip():
                                logger.debug(
                                    "Extracted content from dict message.content"
                                )
                                return c
                        # text field
                        t = ch0.get("text")
                        if t and isinstance(t, str) and t.strip():
                            logger.debug("Extracted content from dict text field")
                            return t
                        # delta fragment
                        d = ch0.get("delta")
                        if isinstance(d, dict):
                            c = d.get("content") or d.get("text")
                            if c and isinstance(c, str) and c.strip():
                                logger.debug("Extracted content from dict delta")
                                return c
        except Exception:
            logger.debug("Exception while extracting response content", exc_info=True)
        return None

    async def _direct_chat_completion(
        self, prompt: str, max_tokens: int = 1000, timeout: int = 60
    ) -> Optional[str]:
        """
        Perform a direct async text completion using AsyncOpenAI client on /v1/completions endpoint.
        Returns the text if successful, otherwise None on timeout/error.
        """
        try:
            client_kwargs = {
                "api_key": cfg.VLLM_LLM_API_KEY,
                "base_url": cfg.VLLM_LLM_URL,
            }
            if cfg.DEV_PROXY_API_KEY:
                client_kwargs["default_headers"] = {"X-API-Key": cfg.DEV_PROXY_API_KEY}
            client = AsyncOpenAI(**client_kwargs)
            logger.info(
                f"LLM direct completion call to {self.model_name}",
                extra={
                    "model": self.model_name,
                    "max_tokens": max_tokens,
                    "timeout": timeout,
                    "prompt_length": len(prompt),
                },
            )
            # Debug: log first 200 chars of prompt
            logger.debug(f"Prompt preview: {prompt[:200]}...")

            resp = await asyncio.wait_for(
                client.completions.create(
                    model=self.model_name,
                    prompt=prompt,
                    max_tokens=max_tokens,
                    temperature=cfg.TEMPERATURE,
                    stream=False,  # ensure non-streaming
                ),
                timeout=timeout,
            )

            # Extract content from text completion response
            content = self._extract_content_from_resp(resp)
            if content:
                logger.info(f"LLM response received, length: {len(content)}")
                return content
            else:
                logger.warning("No usable content found in completion response")
                logger.debug(f"Raw response: {resp}")
                return None
        except asyncio.TimeoutError:
            logger.warning(f"LLM request timed out after {timeout}s")
            return None
        except Exception as e:
            logger.error(f"LLM direct completion failed: {e}", exc_info=True)
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
            client_kwargs = {
                "api_key": cfg.VLLM_LLM_API_KEY,
                "base_url": cfg.VLLM_LLM_URL,
            }
            if cfg.DEV_PROXY_API_KEY:
                client_kwargs["default_headers"] = {"X-API-Key": cfg.DEV_PROXY_API_KEY}
            client = AsyncOpenAI(**client_kwargs)

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

            # Branch by configured provider: vllm uses AsyncOpenAI path, others
            # (ollama, gemini) use the langchain chain.invoke logic provided.
            if cfg.LLM_PROVIDER == "vllm":
                logger.info(
                    f"Generating response for query (vllm path): {query[:30]}..."
                )
                # Format context and build OpenAI-compatible prompt
                formatted_context = self._format_context(context_chunks)
                prompt = (
                    f"{self.system_prompt}\n\n"
                    f"Context:\n\n{formatted_context}\n\n"
                    f"Question: {query.strip()}\n\n"
                    f"Answer:"
                )
                # Run async call synchronously
                response = asyncio.run(
                    self._direct_chat_completion(prompt, max_tokens=1000, timeout=60)
                )
                if response:
                    logger.info(f"Generated response: {str(response)[:30]}...")
                    return response
                else:
                    logger.warning("LLM returned no response")
                    return "[LLM Error: No response generated]"

            else:
                # Ollama/langchain path: use the chain.invoke logic you provided
                logger.info(
                    f"Generating response for query (ollama/langchain path): {query[:30]}..."
                )
                inputs = self.prepare_inputs(
                    session_id, chat_manager, context_chunks, query
                )
                response = self.chain.invoke(inputs)
                response = External.extract_llm_output(response)
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

    async def agenerate_response(
        self,
        session_id: str,
        chat_manager: ChatManager,
        context_chunks: List[str],
        query: str,
    ) -> str:
        """Async version of generate_response.

        Branches by provider:
        - If cfg.LLM_PROVIDER == 'vllm': use the AsyncOpenAI/_direct_chat_completion path.
        - Else (ollama, gemini): use the langchain chain async methods (arun/ainvoke/astream)
          and fall back to running chain.invoke in a thread.
        """
        try:
            if not query or not query.strip():
                raise ValueError("Query cannot be empty")

            # vLLM/OpenAI-compatible path
            if cfg.LLM_PROVIDER == "vllm":
                logger.info(
                    f"Async generating response for query (vllm path): {query[:30]}..."
                )
                formatted_context = self._format_context(context_chunks)
                prompt = (
                    f"{self.system_prompt}\n\n"
                    f"Context:\n\n{formatted_context}\n\n"
                    f"Question: {query.strip()}\n\n"
                    f"Answer:"
                )
                response = await self._direct_chat_completion(
                    prompt, max_tokens=1000, timeout=60
                )
                if response:
                    logger.info(f"Generated async response: {str(response)[:30]}...")
                    return response
                else:
                    logger.warning("LLM returned no async response")
                    return "[LLM Error: No response generated]"

            # Ollama / langchain path
            logger.info(
                f"Async generating response for query (ollama/langchain path): {query[:30]}..."
            )
            inputs = self.prepare_inputs(
                session_id, chat_manager, context_chunks, query
            )

            # 1) chain.arun
            if hasattr(self.chain, "arun"):
                result = await self.chain.arun(inputs)
                result = External.extract_llm_output(result)
                logger.info(f"Generated async response (arun): {str(result)[:30]}...")
                return result

            # 2) chain.ainvoke
            if hasattr(self.chain, "ainvoke"):
                result = await self.chain.ainvoke(inputs)
                result = External.extract_llm_output(result)
                logger.info(
                    f"Generated async response (ainvoke): {str(result)[:30]}..."
                )
                return result

            # 3) chain.astream
            if hasattr(self.chain, "astream"):
                pieces: List[str] = []
                async for chunk in self.chain.astream(inputs):
                    chunk = External.extract_llm_output(chunk)
                    pieces.append(str(chunk))
                result = "".join(pieces)
                logger.info(
                    f"Generated async response (astream): {str(result)[:30]}..."
                )
                return result

            # Fallback: run blocking invoke in thread
            result = await asyncio.to_thread(self.chain.invoke, inputs)
            result = External.extract_llm_output(result)
            logger.info(
                f"Generated async response (fallback invoke): {str(result)[:30]}..."
            )
            return result

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
