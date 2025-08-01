from datetime import datetime

import numpy as np
from arrow import Arrow
from pgvector.psycopg import register_vector

from hawat.embeddings import get_embedding
from hawat.memory.conversations import get_current_conversation_id
from hawat.memory.schema import get_connection_pool


def format_message_log(messages: list[tuple[int, str, str, datetime, int]]) -> list[str]:
    # message_tuple[1] is the sender, message_tuple[4] is minutes ago, message_tuple[2] is the content
    return [
        f"- {message_tuple[1]} ({Arrow.fromdatetime(message_tuple[3]).humanize()}): {message_tuple[2]}"
        for message_tuple in messages
    ]


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
