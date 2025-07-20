import hawat.language as language
import hawat.memory as memory


def process_message(message):
    # Call the new memory function to record the message
    memory.record_message(message, sender="User")
    context = _get_formatted_context(message)
    response = language.get_chat_completion(message, context)
    memory.record_message(response, sender="Hawat")
    return response


def _get_formatted_context(message):
    conversational_context = memory.get_immediate_conversational_context()
    relevant_messages = memory.get_relevant_messages_by_vector_similarity(message)

    # Combine and deduplicate messages based on their unique ID (m[0])
    combined_messages = {m[0]: m for m in conversational_context + relevant_messages}.values()

    # Sort messages by their original timestamp (m[3]) to ensure chronological order in the context
    sorted_messages = sorted(combined_messages, key=lambda m: m[3])  # Use original timestamp for sorting

    # Format the deduplicated and sorted messages.
    # message_tuple[1] is the sender, message_tuple[4] is minutes ago, message_tuple[2] is the content
    formatted_context_messages = [
        f"{message_tuple[1]} ({message_tuple[4]} minutes ago): {message_tuple[2]}" for message_tuple in sorted_messages
    ]

    context = "\n".join(formatted_context_messages)
    return context
