import os
from openai import OpenAI
from pinecone import Pinecone

_openai_client = None
_pinecone_index = None


def get_openai_client():
    global _openai_client
    if _openai_client is None:
        _openai_client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
    return _openai_client


def get_pinecone_index():
    global _pinecone_index
    if _pinecone_index is None:
        pc = Pinecone(api_key=os.environ["PINECONE_API_KEY"])
        _pinecone_index = pc.Index(os.environ.get("PINECONE_INDEX", "gasman-chatbot"))
    return _pinecone_index


def embed_text(text: str) -> list[float]:
    client = get_openai_client()
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=text,
    )
    return response.data[0].embedding


def upsert_vector(vector_id: str, embedding: list[float], metadata: dict):
    index = get_pinecone_index()
    namespace = os.environ.get("PINECONE_NAMESPACE", "gasman")
    index.upsert(vectors=[{"id": vector_id, "values": embedding, "metadata": metadata}], namespace=namespace)


def delete_vector(vector_id: str):
    index = get_pinecone_index()
    namespace = os.environ.get("PINECONE_NAMESPACE", "gasman")
    index.delete(ids=[vector_id], namespace=namespace)


def query_vectors(embedding: list[float], top_k: int = 6) -> list[dict]:
    index = get_pinecone_index()
    namespace = os.environ.get("PINECONE_NAMESPACE", "gasman")
    results = index.query(vector=embedding, top_k=top_k, include_metadata=True, namespace=namespace)
    return [
        {
            "id": match["id"],
            "score": match["score"],
            "category": match["metadata"].get("category", ""),
            "title": match["metadata"].get("title", ""),
            "content": match["metadata"].get("content", ""),
        }
        for match in results["matches"]
    ]
