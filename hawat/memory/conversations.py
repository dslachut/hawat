from collections import defaultdict
from datetime import datetime, timedelta, timezone

import numpy as np
from pgvector.psycopg import register_vector

from hawat.embeddings import get_embedding
from hawat.memory.context import format_message_log
from hawat.memory.schema import get_connection_pool

CONVO_THRESHOLD = timedelta(minutes=30)


def _most_recent_message() -> datetime:
    """Retrieves the timestamp of the most recent message from the PostgreSQL database"""
    try:
        pool = get_connection_pool()
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


def _most_recent_conversation_id() -> int:
    """Retrieves the greatest ID value from the conversations table in the PostgreSQL database"""
    try:
        pool = get_connection_pool()
        if pool:
            with pool.connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT id FROM conversations ORDER BY id DESC LIMIT 1")
                    result = cur.fetchone()
                    if result:
                        return result[0]
        return None  # Return None if no conversation found or error
    except Exception as e:
        print(f"Error retrieving most recent conversation id: {e}")
        return None


def _record_new_conversation():
    pool = get_connection_pool()
    if pool:
        try:
            with pool.connection() as conn:
                register_vector(conn)
                with conn.cursor() as cur:
                    cur.execute(
                        """INSERT INTO conversations (summary, embedding, timestamp) VALUES (%s, %s, %s)""",
                        (
                            None,
                            None,
                            None,
                        ),
                    )
                conn.commit()
                print(f"Successfully created new conversation")
        except Exception as e:
            print(f"Error recording message to database: {e}")


def get_current_conversation_id() -> int:
    """Retrieves the ID of the current conversation from the database

    A conversation is current if the most recent message associated with that conversation is less than CONVO_THRESHOLD minutes old.
    If no conversation is current then a new conversation should be created and its ID returned.

    Returns:
        int: id of the current conversation
    """
    current_time = datetime.now(timezone.utc)
    most_recent_message = _most_recent_message()
    if most_recent_message and ((current_time - most_recent_message.replace(tzinfo=timezone.utc)) < CONVO_THRESHOLD):
        conversation_id = _most_recent_conversation_id()
        if conversation_id:
            return conversation_id
    _record_new_conversation()
    return _most_recent_conversation_id()


def get_unsummarized_conversations() -> tuple[dict[int, list[str]], dict[int, datetime]]:
    pool = get_connection_pool()
    messages = []
    if pool:
        try:
            with pool.connection() as conn, conn.cursor() as cur:
                cur.execute(
                    """SELECT m.id, m.sender, m.content, m.timestamp, c.id AS conversation_id FROM conversations_messages AS cm INNER JOIN conversations AS c ON cm.conversation_id = c.id INNER JOIN messages AS m ON cm.message_id = m.id WHERE c.summary IS NULL OR c.summary = '' OR c.timestamp < (SELECT Max(msg.timestamp) FROM messages AS msg INNER JOIN conversations_messages AS conmsg ON msg.id=conmsg.message_id WHERE conmsg.conversation_id = c.id) ORDER BY m.timestamp"""
                )
                current_time = datetime.now(timezone.utc)
                messages = [
                    (
                        row[0],
                        row[1],
                        row[2],
                        row[3],
                        int((current_time - row[3].replace(tzinfo=timezone.utc)).total_seconds() / 60),
                        row[4],
                    )
                    for row in cur.fetchall()
                ]
        except Exception as e:
            print(f"Error getting unsummarized conversations from database: {e}")
    conversations = defaultdict(list)
    _ = [conversations[m[5]].append(m[:5]) for m in messages]
    return {k: format_message_log(v) for k, v in conversations.items()}, {
        k: v[-1][3].replace(tzinfo=timezone.utc) for k, v in conversations.items()
    }


def update_conversation_summary(id: int, summary: str, timestamp: datetime) -> None:
    pool = get_connection_pool()
    if pool:
        try:
            embedding = np.array(get_embedding(summary))
            with pool.connection() as conn:
                register_vector(conn)
                with conn.cursor() as cur:
                    cur.execute(
                        """UPDATE conversations SET summary=%s, embedding=%s, timestamp=%s WHERE id=%s""",
                        (
                            summary,
                            embedding,
                            timestamp,
                            id,
                        ),
                    )
                conn.commit()
        except Exception as e:
            print(f"Error recording message to database: {e}")
