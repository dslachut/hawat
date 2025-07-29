import os

from pgvector.psycopg import register_vector
from psycopg_pool import ConnectionPool

# Database connection details - TODO: Make this configurable (e.g., environment variables)
DB_NAME = os.getenv("DB_NAME", "hawat")
DB_USER = os.getenv("DB_USER", "hawat")
DB_PASSWORD = os.getenv("DB_PASSWORD", "123456abcdef")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5431")

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
    """Creates the messages table if it doesn\'t exist."""
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
    """Creates the conversations table if it doesn\'t exist"""
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
    """Creates the conversations_messages table if it doesn\'t exist"""
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
