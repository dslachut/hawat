import os

from langchain_huggingface import HuggingFaceEmbeddings


def get_embedding(text: str) -> list[float]:
    """
    Generates a vector embedding for the given text using a local HuggingFace Sentence Transformer.

    Args:
        text (str): The text to embed.

    Returns:
        list[float]: The embedding vector.
    """
    model_name = "sentence-transformers/all-MiniLM-L6-v2"
    model_kwargs = {"device": "cpu"}
    encode_kwargs = {"normalize_embeddings": False}
    hf = HuggingFaceEmbeddings(model_name=model_name, model_kwargs=model_kwargs, encode_kwargs=encode_kwargs)
    return hf.embed_query(text)
