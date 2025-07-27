import os
from datetime import datetime, timedelta, timezone

import numpy as np
from pgvector.psycopg import register_vector
from psycopg_pool import ConnectionPool

from hawat.embeddings import get_embedding

# Database connection details - TODO: Make this configurable (e.g., environment variables)
DB_NAME = os.getenv("DB_NAME", "hawat")
DB_USER = os.getenv("DB_USER", "hawat")
DB_PASSWORD = os.getenv("DB_PASSWORD", "123456abcdef")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5431")

TEN_MINUTE_DELTA = timedelta(minutes=10)

# Global connection pool
_connection_pool = None


def get_connection_pool():
    """Initializes and returns a global connection pool."""
    global _connection_pool
    if _connection_pool is None:
        try:
            _connection_pool = ConnectionPool(
                f"dbname={DB_NAME} user={DB_USER} password={DB_PASSWORD} host={DB_HOST} port={DB_PORT}"
            )
            # Ensure the `vector` extension and `messages` table exist when the pool is first created
            with _connection_pool.connection() as conn:
                _create_tables(conn)
        except Exception as e:
            print(f"Error initializing connection pool or creating tables: {e}")
            _connection_pool = None  # Reset pool if initialization fails
    return _connection_pool


def _create_tables(conn):
    """Creates tables that must exist for system function"""
    _create_vector_extension(conn)
    _create_messages_table(conn)
    _create_conversations_table(conn)
    _create_conversations_messages_table(conn)


def _create_vector_extension(conn):
    """Initialize the pgvector extension in the database"""
    try:
        with conn.cursor() as cur:
            cur.execute("""CREATE EXTENSION IF NOT EXISTS vector;""")
            conn.commit()
    except Exception as e:
        print(f"Error initializing pgvector: {e}")


def _create_messages_table(conn):
    """Creates the messages table if it doesn't exist."""
    # This function should only be called once during connection pool initialization
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS messages (
                    id SERIAL PRIMARY KEY,
                    sender TEXT NOT NULL,
                    content TEXT NOT NULL,
                    embedding VECTOR(384),
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                CREATE INDEX IF NOT EXISTS messages_timestamp_idx ON messages (timestamp);
                CREATE INDEX IF NOT EXISTS messages_embedding_idx ON messages USING HNSW (embedding vector_cosine_ops);
            """
            )
        conn.commit()
    except Exception as e:
        print(f"Error creating messages table: {e}")


def _create_conversations_table(conn):
    """Creates the conversations table if it doesn't exist"""
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS conversations (
                    id SERIAL PRIMARY KEY,
                    summary TEXT,
                    embedding VECTOR(384)
                );
                CREATE INDEX IF NOT EXISTS conversations_embedding_idx ON conversations USING HNSW (embedding vector_cosine_ops);
            """
            )
        conn.commit()
    except Exception as e:
        print(f"Error creating conversations table: {e}")


def _create_conversations_messages_table(conn):
    """Creates the conversations_messages table if it doesn't exist"""
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS conversations_messages (
                    conversation_id INTEGER NOT NULL REFERENCES conversations (id) ON DELETE CASCADE,
                    message_id INTEGER NOT NULL REFERENCES messages (id) ON DELETE CASCADE,
                    PRIMARY KEY (conversation_id, message_id)
                );
                CREATE INDEX IF NOT EXISTS conversations_messages_conversation_id_idx ON conversations_messages (conversation_id);
                CREATE INDEX IF NOT EXISTS conversations_messages_message_id_idx ON conversations_messages (message_id);
            """
            )
        conn.commit()
    except Exception as e:
        print(f"Error creating conversations_messages table: {e}")


def _most_recent_message()->datetime:
    """Retrieves the timestamp of the most recent message from the PostgreSQL database"""
    try:
        pool = _get_connection_pool()
        if pool:
            with pool.connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT timestamp FROM messages ORDER BY id DESC LIMIT 1")
                    result = cur.fetchone()
                    if result:
                        return result[0]
        return None  # Return None if no message found or error
    except Exception as e:
        print(f"Error retrieving most recent message timestamp: {e}")
        return None


def _most_recent_conversation_id()->int:
    """Retrieves the greatest ID value from the conversations table in the PostgreSQL database"""


def _current_conversation_id()->int:
    """Retrieves the ID of the current conversation from the database

    A conversation is current if the most recent message associated with that conversation is less than 10 minutes old.
    If no conversation is current then a new conversation should be created and its ID returned.

    Returns:
        int: id of the current conversation
    """
    current_time = datetime.now(timezone.utc)
    most_recent_message = _most_recent_message().replace(tzinfo=timezone.utc)
    if (current_time - most_recent_message) < TEN_MINUTE_DELTA:
        return _most_recent_conversation_id()
    return _most_recent_conversation_id()
    

def record_message(message: str, sender: str = "user"):
    """Records a user message to the PostgreSQL database."""
    pool = _get_connection_pool()
    if pool:
        try:
            with pool.connection() as conn:
                register_vector(conn)
                with conn.cursor() as cur:
                    embedding = get_embedding(message)
                    cur.execute(
                        """INSERT INTO messages (sender, content, embedding) VALUES (%s, %s, %s)""",
                        (sender, message, np.array(embedding)),
                    )
                conn.commit()
                print(f"Successfully recorded message with embedding: {message}")
        except Exception as e:
            print(f"Error recording message to database: {e}")


CONTEXT_TIME_WINDOW_MINUTES = int(os.getenv("CONTEXT_TIME_WINDOW_MINUTES", "5"))  # Default to last 5 minutes


def get_immediate_conversational_context() -> list[str]:
    """Retrieves the most recent conversational context from the database within a specified time window."""
    pool = _get_connection_pool()
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


TOP_K_SIMILAR_MESSAGES = int(os.getenv("TOP_K_SIMILAR_MESSAGES", "3"))


def get_relevant_messages_by_vector_similarity(query_string: str) -> list[str]:
    """Retrieves messages most relevant to the query string using vector similarity."""
    pool = _get_connection_pool()
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
