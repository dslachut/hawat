import hawat.language as language
import hawat.memory as memory


def process_message(message):
    # Call the new memory function to record the message
    memory.record_user_message(message)
    conversational_context = memory.get_immediate_conversational_context()
    relevant_messages = memory.get_relevant_messages_by_vector_similarity(message)

    formatted_conversational_context = [f"{m[0]} ({m[2]} minutes ago): {m[1]}" for m in conversational_context]
    formatted_relevant_messages = [f"{m[0]} ({m[2]} minutes ago): {m[1]}" for m in relevant_messages]

    context = "\n".join(formatted_conversational_context + formatted_relevant_messages)
    response = language.get_chat_completion(message, context)
    return response
