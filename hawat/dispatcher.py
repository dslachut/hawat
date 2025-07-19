import hawat.language as language
import hawat.memory as memory


def process_message(message):
    # Call the new memory function to record the message
    memory.record_user_message(message)
    response = language.get_chat_completion(message)
    return response
