# Plan for LLM / Embedding / Reranker Abstraction Layer

## 1. Goal
Create a **single public façade** that returns a *LangChain‑compatible* object for the requested provider (LLM, embedding, reranker). The rest of the code will simply call `providers.llm.get_llm()`, `providers.embeddings.get_embedding()`, `providers.rerankers.get_reranker()` and use the returned objects as normal LangChain models.

## 2. High‑level architecture
```
backend/
└─ src/
   └─ services/
        ├─ external/                     # public façade
        │   ├─ __init__.py                # re‑export llm/embeddings/rerankers
        │   └─ providers/                 # concrete implementations
        │       ├─ __init__.py
        │       ├─ llm/
        │       │   ├─ __init__.py        # get_llm() selector
        │       │   ├─ ollama.py          # returns langchain_ollama.OllamaLLM
        │       │   ├─ vllm.py            # returns openai.AsyncOpenAI (ChatOpenAI)
        │       │   └─ gemini.py          # returns ChatGoogleGenerativeAI
        │       ├─ embeddings/
        │       │   ├─ __init__.py        # get_embedding() selector
        │       │   ├─ vllm.py            # returns AsyncOpenAI client (embedding endpoint)
        │       │   └─ huggingface.py     # returns a custom class that mimics LangChain embeddings
        │       └─ rerankers/
        │           ├─ __init__.py        # get_reranker() selector
        │           ├─ tei.py            # thin wrapper around TEI HTTP service (LangChain‑compatible API)
        │           └─ huggingface.py    # optional CrossEncoder based reranker
        └─ … (existing services remain unchanged)
```

All three provider families expose **exactly the same public methods** that LangChain expects, so the downstream code never needs to know which back‑end is being used.

## 3. Public API (what the rest of the code will import)
```python
# backend/src/services/external/__init__.py
from .providers import llm, embeddings, rerankers

# Usage elsewhere
from backend.src.services.external import llm, embeddings, rerankers

my_llm = llm.get_llm()               # LangChain‑compatible chat model
response = my_llm.invoke([{"role": "user", "content": "Hello"}])

embedder = embeddings.get_embedding() # object with .embed_query(text)
vec = embedder.embed_query("some query")

reranker = rerankers.get_reranker()  # object with .rerank(query, candidates)
ranked = reranker.rerank(query, chunks)
```

## 4. Provider selection logic (configuration)
* Add three environment variables (already exist for LLM, but we add the others):*
```dotenv
LLM_PROVIDER=ollama          # or "vllm" or "gemini"
EMBEDDING_PROVIDER=vllm     # or "huggingface"
RERANKER_PROVIDER=tei       # or "huggingface"
DEV_PROXY_API_KEY=…          # optional – injected as a header by wrappers
```
*The selector modules (`llm/__init__.py`, `embeddings/__init__.py`, `rerankers/__init__.py`) read the env var and instantiate the matching concrete class.*

## 5. Concrete provider modules (what each file must contain)
### 5.1 LLM providers
| File | Class | Returns |
|------|-------|---------|
| `ollama.py` | `OllamaProvider` | `langchain_ollama.OllamaLLM` (with optional `client_kwargs` for `X‑API‑Key`) |
| `vllm.py`   | `VLLMProvider`   | `openai.ChatOpenAI` (async) |
| `gemini.py` | `GeminiProvider` | `langchain_google_genai.ChatGoogleGenerativeAI` |
*Each class implements a tiny ``get_llm()`` method that simply returns the instantiated LangChain object.*

### 5.2 Embedding providers
| File | Class | Returns |
|------|-------|---------|
| `vllm.py` | `VLLMEmbeddingProvider` | `openai.AsyncOpenAI` (embeddings endpoint) |
| `huggingface.py` | `HFEmbeddingProvider` | a custom class exposing ``embed_query``/``embed_documents`` that internally uses `sentence‑transformers` or `transformers` – **still LangChain‑compatible** because it follows the same method signatures. |

### 5.3 Reranker providers
| File | Class | Returns |
|------|-------|---------|
| `tei.py` | `TEIRerankerProvider` | a small wrapper exposing ``rerank(query, candidates)`` that internally calls the TEI HTTP API and returns the reordered list. |
| `huggingface.py` | `HFRerankerProvider` | a wrapper around a `CrossEncoder` pipeline (still LangChain‑compatible). |

## 6. Step‑by‑step implementation plan
1. **Create folder structure** (`backend/src/services/external/providers/...`).
2. **Add `base.py`** with abstract contracts (`BaseLLM`, `BaseEmbedding`, `BaseReranker`). *Optional – can be skipped if you rely on the concrete LangChain classes directly, but keeping the ABC makes future non‑LangChain providers trivial.*
3. **Implement concrete provider files** (`ollama.py`, `vllm.py`, `gemini.py`, etc.) – each should:
   - read the needed URL/IP/PORT variables from `cfg`
   - inject `DEV_PROXY_API_KEY` as a header when present
   - instantiate the appropriate LangChain class (or a thin wrapper for non‑LangChain services)
   - expose a ``get_*`` function (e.g., ``def get_llm() -> BaseLLM: return OllamaProvider()``)
4. **Write selector modules** (`providers/llm/__init__.py`, `providers/embeddings/__init__.py`, `providers/rerankers/__init__.py`):
   ```python
   from ..llm.ollama import OllamaProvider
   from ..llm.vllm   import VLLMProvider
   ...
   def get_llm():
       provider = cfg.LLM_PROVIDER.lower()
       if provider == "ollama":   return OllamaProvider()
       if provider == "vllm":     return VLLMProvider()
       if provider == "gemini":   return GeminiProvider()
       raise ValueError("Unsupported LLM provider")
   ```
5. **Expose the façade** in `external/__init__.py` (`from .providers import llm, embeddings, rerankers`).
6. **Update existing services** (if you want) to import from the façade instead of the old `External.create_llm`. – *this step is optional for the plan; you can migrate gradually.*
7. **Add the new environment variables** to `.env.example` and documentation.
8. **Write unit tests** for each selector to ensure the correct concrete class is returned based on env vars, and for each wrapper to verify the `X‑API‑Key` header is added when set.
9. **Run the full test suite** (`pytest` or the project’s test runner) to confirm nothing broke.
10. **Update CI / deployment scripts** to expose the new env vars.
11. **Document** the new architecture in `README.md` and add a short diagram.

## 7. Testing strategy
- **Unit test each selector** – mock `cfg.LLM_PROVIDER`/`EMBEDDING_PROVIDER`/`RERANKER_PROVIDER` and assert the returned object is an instance of the expected concrete class.
- **Integration test** – spin up the dev‑proxy stack (docker‑compose) and ensure a request through the selected provider succeeds (e.g., a simple `ollama.invoke` call returns a response).
- **Header propagation test** – set `DEV_PROXY_API_KEY` and verify the outgoing HTTP request (use `requests_mock` or `httpx_mock`) includes the header.

## 8. Future extensions
- Add **additional providers** (e.g., Anthropic, Cohere) by creating a new module inside the appropriate sub‑package and extending the selector.
- Support **multiple models per provider** (e.g., different Ollama models) by exposing a ``model_name`` argument to the selector functions.
- Introduce **caching** (e.g., `lru_cache` on the selector) if you want a singleton per process.
- Provide **async versions** for all selectors (simply add ``async def get_llm_async()`` that returns the same object because LangChain objects themselves are async‑compatible).

---
**Result:** A clean, configurable, LangChain‑compatible abstraction layer that lets the rest of the codebase call `get_llm()`, `get_embedding()`, `get_reranker()` without caring about which back‑end is actually in use.
