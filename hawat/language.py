import os

from langchain_community.embeddings import HuggingFaceEmbeddings
from openai import OpenAI


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


def get_chat_completion(system_prompt: str, user_prompt: str) -> str:
    """
    Gets a chat completion from an OpenAI-compatible API.

    Args:
        system_prompt (str): The system prompt for the chat.
        user_prompt (str): The user prompt for the chat.

    Returns:
        str: The completed chat response.
    """
    client = OpenAI(
        base_url=os.getenv("OPENAI_API_BASE", "https://openrouter.ai/api/v1"),
        api_key=os.getenv("OPENAI_API_KEY"),
    )
    response = client.chat.completions.create(
        model=os.getenv("OPENAI_CHAT_MODEL", "deepseek/deepseek-r1-0528:free"),  # Default chat model
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    )
    return response.choices[0].message.content
