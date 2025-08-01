import threading
import time
from datetime import datetime, timezone

import schedule
from arrow import Arrow

from hawat.language import get_conversation_summary
from hawat.memory.conversations import get_unsummarized_conversations, update_conversation_summary

# A lock to ensure only one instance of the task runs at a time
task_lock = threading.Lock()


def run_minutely_task():
    """
    This function will be run once every hour.
    It acquires a lock to ensure only one instance runs at a time.
    """
    # Attempt to acquire the lock without blocking
    if task_lock.acquire(blocking=False):
        try:
            # Add your minutely task logic here
            summarize_conversations()
        finally:
            task_lock.release()  # Release the lock whether the task succeeds or fails
    else:
        print("Skipping minutely task: another instance is already running.")


def start_reflection_thread():
    # Schedule the task to run every minute
    schedule.every().minute.at(":00").do(run_minutely_task)

    def run_scheduler():
        while True:
            schedule.run_pending()
            time.sleep(1)  # Check every second for pending jobs

    # Start the scheduler in a daemon thread
    thread = threading.Thread(target=run_scheduler, daemon=True)
    thread.start()
    return thread


def summarize_conversations() -> None:
    unsummarized_conversations, conversation_times = get_unsummarized_conversations()
    if len(unsummarized_conversations) == 0:
        return
    print(f"Found {len(unsummarized_conversations)} unsummarized conversations.")
    conversation_summaries = [
        [id, get_conversation_summary("\n".join(messages)), conversation_times[id]]
        for id, messages in unsummarized_conversations.items()
    ]
    _ = [update_conversation_summary(*convo) for convo in conversation_summaries]
    print(f"Updated {len(conversation_summaries)} conversation summaries")
