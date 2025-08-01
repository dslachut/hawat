import json
import os

CONVERSATION_SYSTEM_PROMPT_TEMPLATE = """You are Hawat, a helpful, conversational AI. Your purpose is to assist the user by providing effective advice and assistance."""
CONVERSATION_USER_PROMPT_TEMPLATE = """The following is a conversation with the user, followed by their most recent message.

{context}
User (Just now): {user_message}"""

SUMMARY_SYSTEM_PROMPT_TEMPLATE = """The following is a chat conversation between a human, User, and a conversational AI, Hawat. Summarize the conversation."""

NER_SYSTEM_PROMPT_TEMPLATE = """The following is a chat conversation between a human, User, and a conversational AI, Hawat. Find the keywords, named entities, and the subjects of the conversation.
The response should be a JSON object formatted like this:
{
  "subjects": [],
  "entities": [],
  "keywords": []
}
"""

from openai import OpenAI

_client = OpenAI(
    base_url=os.getenv("OPENAI_API_BASE", "https://openrouter.ai/api/v1"),
    api_key=os.getenv("OPENAI_API_KEY"),
)
_model = os.getenv("OPENAI_CHAT_MODEL", "deepseek/deepseek-r1-0528:free")  # Default chat model
print(f"Using model: {_model}")


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
        model=_model,
        messages=[
            {"role": "system", "content": CONVERSATION_SYSTEM_PROMPT_TEMPLATE},
            {
                "role": "user",
                "content": CONVERSATION_USER_PROMPT_TEMPLATE.format(context=context, user_message=user_message),
            },
        ],
    )
    return response.choices[0].message.content


def get_conversation_summary(formatted_convo: str) -> str:
    """Gets a summary of the conversation between User and Hawat"""
    response = _client.chat.completions.create(
        model=_model,
        messages=[
            {"role": "system", "content": SUMMARY_SYSTEM_PROMPT_TEMPLATE},
            {"role": "user", "content": formatted_convo},
        ],
    )
    return response.choices[0].message.content


def get_conversation_keys_names_subjects(formatted_convo: str) -> dict[str, list[str]] | None:
    """Gets subjects, named entities, and keywords from a conversation"""
    response = _client.chat.completions.create(
        model=_model,
        messages=[
            {"role": "system", "content": NER_SYSTEM_PROMPT_TEMPLATE},
            {"role": "user", "content": formatted_convo},
        ],
    )
    content = response.choices[0].message.content
    try:
        output = json.loads(content)
        if not (
            isinstance(output["entities"], list)
            and isinstance(output["keywords"], list)
            and isinstance(output["subjects"], list)
        ):
            raise TypeError
        return output
    except Exception as e:
        print(f"Bad JSON response: {e}")
        print(f"Response: {content}")
        return None
