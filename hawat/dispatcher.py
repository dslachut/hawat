import hawat.language as language
import hawat.memory as memory


def process_message(message):
    context = memory.get_formatted_context(message)
    memory.record_message(message, sender="User")
    response = language.get_conversation_response(message, context)
    memory.record_message(response, sender="Hawat")
    return response
