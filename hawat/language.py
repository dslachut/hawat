import os

from openai import OpenAI


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
