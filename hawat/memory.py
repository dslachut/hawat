import os
from datetime import datetime, timedelta

import numpy as np
import psycopg
from pgvector.psycopg import register_vector

from hawat.embeddings import get_embedding

# Database connection details - TODO: Make this configurable (e.g., environment variables)
DB_NAME = os.getenv("DB_NAME", "hawat")
DB_USER = os.getenv("DB_USER", "hawat")
DB_PASSWORD = os.getenv("DB_PASSWORD", "123456abcdef")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5431")


def _get_db_connection():
    """Establishes and returns a database connection."""
    try:
        conn = psycopg.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD, host=DB_HOST, port=DB_PORT)
        register_vector(conn)
        return conn
    except Exception as e:
        print(f"Error connecting to database: {e}")
        return None


def _create_messages_table(conn):
    """Creates the messages table if it doesn\'t exist."""
    try:
        with conn.cursor() as cur:
            cur.execute("""CREATE EXTENSION IF NOT EXISTS vector;""")
            conn.commit()
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS messages (
                    id SERIAL PRIMARY KEY,
                    content TEXT NOT NULL,
                    embedding VECTOR(384),
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """
            )
        conn.commit()
    except Exception as e:
        print(f"Error creating messages table: {e}")


def record_user_message(message: str):
    """Records a user message to the PostgreSQL database."""

    conn = None  # Initialize conn to None
    try:
        conn = _get_db_connection()
        if conn:
            _create_messages_table(conn)
            with conn.cursor() as cur:
                embedding = get_embedding(message)
                cur.execute("INSERT INTO messages (content, embedding) VALUES (%s, %s)", (message, np.array(embedding)))
            conn.commit()
            print(f"Successfully recorded message with embedding: {message}")
    except Exception as e:
        print(f"Error recording message to database: {e}")
    finally:
        if conn:
            conn.close()


CONTEXT_TIME_WINDOW_MINUTES = int(os.getenv("CONTEXT_TIME_WINDOW_MINUTES", "5"))  # Default to last 5 minutes


def get_immediate_conversational_context() -> list[str]:
    """Retrieves the most recent conversational context from the database within a specified time window."""
    conn = None
    messages = []
    try:
        conn = _get_db_connection()
        if conn:
            with conn.cursor() as cur:
                time_threshold = datetime.now() - timedelta(minutes=CONTEXT_TIME_WINDOW_MINUTES)
                cur.execute(
                    "SELECT content FROM messages WHERE timestamp >= %s ORDER BY timestamp ASC", (time_threshold,)
                )
                messages = [row[0] for row in cur.fetchall()]
    except Exception as e:
        print(f"Error retrieving conversational context: {e}")
    finally:
        if conn:
            conn.close()
    return messages


TOP_K_SIMILAR_MESSAGES = int(os.getenv("TOP_K_SIMILAR_MESSAGES", "3"))


def get_relevant_messages_by_vector_similarity(query_string: str) -> list[str]:
    """Retrieves messages most relevant to the query string using vector similarity."""
    conn = None
    messages = []
    try:
        conn = _get_db_connection()
        if conn:
            query_embedding = get_embedding(query_string)
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT content FROM messages ORDER BY embedding <-> %s LIMIT %s",
                    (np.array(query_embedding), TOP_K_SIMILAR_MESSAGES),
                )
                messages = [row[0] for row in cur.fetchall()]
    except Exception as e:
        print(f"Error retrieving relevant messages by vector similarity: {e}")
    finally:
        if conn:
            conn.close()
    return messages
