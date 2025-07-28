from datetime import datetime, timedelta, timezone

from pgvector.psycopg import register_vector

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
                        """INSERT INTO conversations (summary, embedding) VALUES (%s, %s)""",
                        (
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
