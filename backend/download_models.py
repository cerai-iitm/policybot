import warnings
import torch
from langchain_huggingface import HuggingFaceEmbeddings
from FlagEmbedding import FlagReranker

warnings.filterwarnings("ignore")

print("Downloading embedding model...")
embedding_model = HuggingFaceEmbeddings(
    model_name="Alibaba-NLP/gte-multilingual-base",
    model_kwargs={
        "device": "cuda" if torch.cuda.is_available() else "cpu",
        "trust_remote_code": True
    },
    encode_kwargs={"normalize_embeddings": True}
)
print("Embedding model downloaded")

print("Downloading reranker model...")
reranker = FlagReranker("BAAI/bge-reranker-base")
print("Reranker model downloaded")

print("All models downloaded successfully!")