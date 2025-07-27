import os
from datetime import datetime, timedelta, timezone

import numpy as np
from pgvector.psycopg import register_vector

from hawat.embeddings import get_embedding
from hawat.memory.schema import get_connection_pool

CONTEXT_TIME_WINDOW_MINUTES = int(os.getenv("CONTEXT_TIME_WINDOW_MINUTES", "5"))  # Default to last 5 minutes
TOP_K_SIMILAR_MESSAGES = int(os.getenv("TOP_K_SIMILAR_MESSAGES", "3"))


def get_immediate_conversational_context() -> list[str]:
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


def get_relevant_messages_by_vector_similarity(query_string: str) -> list[str]:
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
