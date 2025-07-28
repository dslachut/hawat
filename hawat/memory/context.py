import os
from datetime import datetime, timedelta, timezone

import numpy as np
from pgvector.psycopg import register_vector

from hawat.embeddings import get_embedding

from hawat.memory.schema import get_connection_pool

CONTEXT_TIME_WINDOW_MINUTES = int(os.getenv("CONTEXT_TIME_WINDOW_MINUTES", "5"))  # Default to last 5 minutes
TOP_K_SIMILAR_MESSAGES = int(os.getenv("TOP_K_SIMILAR_MESSAGES", "3"))

CONVO_CONTEXT_TEMPLATE = """Related Prior Conversations
---
{convos}


Related Prior Messages
---
{messages}


Current Conversation
---
{current}
"""
NONE_AVAILABLE = ["None available"]

def _format_context_messages(messages: list[tuple[int, str, str, datetime, int]])->list[str]:
    # message_tuple[1] is the sender, message_tuple[4] is minutes ago, message_tuple[2] is the content
    return [
        f"{message_tuple[1]} ({message_tuple[4]} minutes ago): {message_tuple[2]}" for message_tuple in messages
    ]


def get_formatted_context(message):
    conversational_context = get_immediate_conversational_context()
    relevant_messages = get_relevant_messages_by_vector_similarity(message)
    related_convos = get_related_conversations_by_vector_similarity(message) or NONE_AVAILABLE

    # Remove "relevant messages" that are already in conversational context
    to_remove = {m[0] for m in conversational_context}.intersection({m[0] for m in relevant_messages})
    ready_relevant_messages = _format_context_messages(sorted([m for m in relevant_messages if m[0] not in to_remove], key=lambda m: m[3])) or NONE_AVAILABLE
    ready_conversational_context = _format_context_messages(conversational_context) or NONE_AVAILABLE

    # Format the deduplicated and sorted messages.
    context = CONVO_CONTEXT_TEMPLATE.format(
        convos="\n".join(related_convos),
        messages="\n".join(ready_relevant_messages),
        current = "\n".join(ready_conversational_context),
        )

    return context


def get_immediate_conversational_context() -> list[tuple[int, str, str, datetime, int]]:
    """Retrieves the most recent conversational context from the database within a specified time window."""
    pool = get_connection_pool()
    messages = []
    if pool:
        try:
            with pool.connection() as conn:
                register_vector(conn)
                with conn.cursor() as cur:
                    time_threshold = datetime.now(timezone.utc) - timedelta(minutes=CONTEXT_TIME_WINDOW_MINUTES)
                    cur.execute(
                        "SELECT id, sender, content, timestamp FROM messages WHERE timestamp >= %s ORDER BY timestamp ASC",
                        (time_threshold,),
                    )
                    current_time = datetime.now(timezone.utc)
                    messages = [
                        (
                            row[0],
                            row[1],
                            row[2],
                            row[3],
                            int((current_time - row[3].replace(tzinfo=timezone.utc)).total_seconds() / 60),
                        )
                        for row in cur.fetchall()
                    ]
        except Exception as e:
            print(f"Error retrieving immediate conversational context: {e}")
    return messages


def get_related_conversations_by_vector_similarity(query_string: str) -> list[str]:
    """Retrieves conversations most relevant to the query string using vector similarity"""
    pool = get_connection_pool()
    conversations = []
    if pool:
        try:
            with pool.connection() as conn:
                register_vector(conn)
                query_embedding = get_embedding(query_string)
                with conn.cursor() as cur:
                    cur.execute(
                        "SELECT id, summary FROM conversations WHERE summary IS NOT NULL ORDER BY embedding <-> %s LIMIT %s",
                        (np.array(query_embedding), TOP_K_SIMILAR_MESSAGES),
                    )
                    conversations = [f"Conversation ID: {row[0]}, Summary: {row[1]}" for row in cur.fetchall()]
        except Exception as e:
            print(f"Error retrieving related conversations by vector similarity: {e}")
    return conversations


def get_relevant_messages_by_vector_similarity(query_string: str) -> list[tuple[int, str, str, datetime, int]]:
    """Retrieves messages most relevant to the query string using vector similarity."""
    pool = get_connection_pool()
    messages = []
    if pool:
        try:
            with pool.connection() as conn:
                register_vector(conn)
                query_embedding = get_embedding(query_string)
                with conn.cursor() as cur:
                    cur.execute(
                        "SELECT id, sender, content, timestamp FROM messages ORDER BY embedding <-> %s LIMIT %s",
                        (np.array(query_embedding), TOP_K_SIMILAR_MESSAGES),
                    )
                    current_time = datetime.now(timezone.utc)
                    messages = [
                        (
                            row[0],
                            row[1],
                            row[2],
                            row[3],
                            int((current_time - row[3].replace(tzinfo=timezone.utc)).total_seconds() / 60),
                        )
                        for row in cur.fetchall()
                    ]
        except Exception as e:
            print(f"Error retrieving relevant messages by vector similarity: {e}")
    # Return the list of formatted messages (or an empty list if an error occurred)
    return messages
