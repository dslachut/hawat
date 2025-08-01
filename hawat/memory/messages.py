import numpy as np
from pgvector.psycopg import register_vector

from hawat.embeddings import get_embedding
from hawat.memory.conversations import get_current_conversation_id
from hawat.memory.schema import get_connection_pool


def record_message(message: str, sender: str = "user"):
    """Records a user message to the PostgreSQL database."""
    conversation_id = get_current_conversation_id()
    pool = get_connection_pool()
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
                    cur.execute("""SELECT id FROM messages ORDER BY id DESC LIMIT 1""")
                    msg_id = cur.fetchone()[0]
                    cur.execute(
                        """INSERT INTO conversations_messages (conversation_id, message_id) VALUES (%s, %s)""",
                        (
                            conversation_id,
                            msg_id,
                        ),
                    )
                conn.commit()
                print(f"Successfully recorded message with embedding: {message}")
        except Exception as e:
            print(f"Error recording message to database: {e}")
