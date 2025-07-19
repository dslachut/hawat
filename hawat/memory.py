import psycopg

# Database connection details - TODO: Make this configurable (e.g., environment variables)
DB_NAME = "hawat"
DB_USER = "hawat"
DB_PASSWORD = "123456abcdef"
DB_HOST = "localhost"
DB_PORT = "5431"

def _get_db_connection():
    """Establishes and returns a database connection."""
    try:
        conn = psycopg.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD, host=DB_HOST, port=DB_PORT)
        return conn
    except Exception as e:
        print(f"Error connecting to database: {e}")
        return None

def _create_messages_table(conn):
    """Creates the messages table if it doesn\'t exist."""
    try:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS messages (
                    id SERIAL PRIMARY KEY,
                    content TEXT NOT NULL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
        conn.commit()
    except Exception as e:
        print(f"Error creating messages table: {e}")

def record_user_message(message: str):
    """Records a user message to the PostgreSQL database."""
    print(f"Attempting to record message: {message}")
    conn = None # Initialize conn to None
    try:
        conn = _get_db_connection()
        if conn:
            _create_messages_table(conn)
            with conn.cursor() as cur:
                cur.execute("INSERT INTO messages (content) VALUES (%s)", (message, ))
            conn.commit()
            print(f"Successfully recorded message: {message}")
    except Exception as e:
        print(f"Error recording message to database: {e}")
    finally:
        if conn:
            conn.close()
