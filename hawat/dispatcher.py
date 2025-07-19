import hawat.memory as memory
from hawat.language import get_embedding


def process_message(message):
    # Call the new memory function to record the message
    embedding = get_embedding(message)
    memory.record_user_message(message, embedding)
    return message
