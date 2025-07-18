
import hawat.memory as memory

def process_message(message):
    # Call the new memory function to record the message
    memory.record_user_message(message)
    return message
    
