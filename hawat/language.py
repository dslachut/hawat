import os

CONVERSATION_SYSTEM_PROMPT_TEMPLATE = """You are Hawat, a helpful, conversational AI. Your purpose is to assist the user by providing effective advice and assistance."""
CONVERSATION_USER_PROMPT_TEMPLATE = """The following is a conversation with the user, followed by their most recent message.

{context}
User: {user_message}"""

SUMMARY_SYSTEM_PROMPT_TEMPLATE = """The following is a chat conversation between a human, User, and a conversational AI, Hawat. Summarize the conversation."""


from openai import OpenAI

_client = OpenAI(
    base_url=os.getenv("OPENAI_API_BASE", "https://openrouter.ai/api/v1"),
    api_key=os.getenv("OPENAI_API_KEY"),
)

def get_conversation_response(user_message: str, context: str = "") -> str:
    """
    Gets a chat completion from an OpenAI-compatible API.

    Args:
        system_prompt (str): The system prompt for the chat.
        user_prompt (str): The user prompt for the chat.

    Returns:
        str: The completed chat response.
    """
    response = _client.chat.completions.create(
        model=os.getenv("OPENAI_CHAT_MODEL", "deepseek/deepseek-r1-0528:free"),  # Default chat model
        messages=[
            {"role": "system", "content": CONVERSATION_SYSTEM_PROMPT_TEMPLATE},
            {"role": "user", "content": CONVERSATION_USER_PROMPT_TEMPLATE.format(context=context, user_message=user_message)},
        ],
    )
    return response.choices[0].message.content


def get_conversation_summary(formatted_convo: str):
    """Gets a summary of the conversation between User and Hawat"""
    response = _client.chat.completions.create(
        model=os.getenv("OPENAI_CHAT_MODEL", "deepseek/deepseek-r1-0528:free"),  # Default chat model
        messages=[
            {"role": "system", "content": SUMMARY_SYSTEM_PROMPT_TEMPLATE},
            {"role": "user", "content": formatted_convo},
        ],
    )
    return response.choices[0].message.content
