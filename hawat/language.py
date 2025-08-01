import json
import os

CONVERSATION_SYSTEM_PROMPT_TEMPLATE = """You are Hawat, a helpful, conversational AI.
Your purpose is to assist the user by providing effective advice and assistance.
Make your responses short and to the point. Let the user ask for more context if he wants it.
Do not use icons or emojis in your response unless the user asks for them.
Prefer sentences and paragraphs in your response. For structure, only use bullet points, numbered lists, and code blocks."""
CONVERSATION_USER_PROMPT_TEMPLATE = """You are having a conversation with the user.
For context, you are provided with summaries of some of your earlier conversations, a selection of earlier messages, the log of the ongoing conversation, and the User's most recent message.
Consider this context when replying to the User.

{context}
---
User (just now): {user_message}"""

SUMMARY_SYSTEM_PROMPT_TEMPLATE = """The following is a chat conversation between a human, User, and a conversational AI, Hawat. 
Summarize the conversation as briefly as possible.
You may use up to five bullet points.
Summarize the conversation in a single sentence if you can."""

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


def send_to_model(system_prompt: str, user_prompt: str) -> str:
    response = _client.chat.completions.create(
        model=_model,
        messages=[
            {"role": "system", "content": system_prompt},
            {
                "role": "user",
                "content": user_prompt,
            },
        ],
    )
    return response.choices[0].message.content


def get_conversation_response(user_message: str, context: str = "") -> str:
    """
    Gets a chat completion from an OpenAI-compatible API.

    Args:
        system_prompt (str): The system prompt for the chat.
        user_prompt (str): The user prompt for the chat.

    Returns:
        str: The completed chat response.
    """
    user_prompt = CONVERSATION_USER_PROMPT_TEMPLATE.format(context=context, user_message=user_message)
    print(user_prompt)
    return send_to_model(CONVERSATION_SYSTEM_PROMPT_TEMPLATE, user_prompt)


def get_conversation_summary(formatted_convo: str) -> str:
    """Gets a summary of the conversation between User and Hawat"""
    return send_to_model(SUMMARY_SYSTEM_PROMPT_TEMPLATE, formatted_convo)


def get_conversation_keys_names_subjects(formatted_convo: str) -> dict[str, list[str]] | None:
    """Gets subjects, named entities, and keywords from a conversation"""
    content = send_to_model(NER_SYSTEM_PROMPT_TEMPLATE, formatted_convo)
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
