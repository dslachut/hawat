import os

SYSTEM_PROMPT_TEMPLATE = "You are Hawat, a helpful, conversational AI. Your purpose is to assist the user by providing effective advice and assistance.

{context}"
USER_PROMPT_TEMPLATE = "User: {user_message}"

from openai import OpenAI


def get_chat_completion(user_message: str, context: str = "") -> str:
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
            {"role": "system", "content": SYSTEM_PROMPT_TEMPLATE.format(context=context)},
            {"role": "user", "content": USER_PROMPT_TEMPLATE.format(user_message=user_message)},
        ],
    )
    return response.choices[0].message.content
