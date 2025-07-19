import os
from openai import OpenAI

# Initialize the OpenAI client
# Assumes OPENAI_API_KEY and OPENAI_API_BASE are set as environment variables
client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY"),
    base_url=os.environ.get("OPENAI_API_BASE", "https://openrouter.ai/api/v1")
)

def get_embedding(text: str, model: str = "text-embedding-ada-002") -> list[float]:
    """Fetches a vector embedding for the given text from the OpenAI-compatible API."""
    try:
        response = client.embeddings.create(input=[text], model=model)
        return response.data[0].embedding
    except Exception as e:
        print(f"Error getting embedding: {e}")
        return []

def get_chat_completion(system_prompt: str, user_prompt: str, model: str = "deepseek/deepseek-r1-0528:free") -> str:
    """Fetches a chat completion from the OpenAI-compatible API."""
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Error getting chat completion: {e}")
        return ""
