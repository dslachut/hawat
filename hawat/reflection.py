import threading
import time
import schedule

# A lock to ensure only one instance of the task runs at a time
task_lock = threading.Lock()

def run_hourly_task():
    """
    This function will be run once every hour.
    It acquires a lock to ensure only one instance runs at a time.
    """
    # Attempt to acquire the lock without blocking
    if task_lock.acquire(blocking=False):
        try:
            print("Hourly task running at {time.time()}...")
            # Add your hourly task logic here
            # For demonstration, let"s simulate some work
            from hawat.memory.reflection import get_unsummarized_conversations
            unsummarized_conversations = get_unsummarized_conversations()
            print(f"Found {len(unsummarized_conversations)} unsummarized conversations.")
            # Here, you would process these conversations for summarization or reflection
        finally:
            task_lock.release() # Release the lock whether the task succeeds or fails
    else:
        print("Skipping hourly task: another instance is already running.")

def start_reflection_thread():
    """
    Starts a daemon thread that schedules and runs run_hourly_task every hour, on the hour.
    """
    # Schedule the task to run every hour, on the hour
    schedule.every().hour.at(":00").do(run_hourly_task)

    def run_scheduler():
        while True:
            schedule.run_pending()
            time.sleep(1) # Check every second for pending jobs

    # Start the scheduler in a daemon thread
    thread = threading.Thread(target=run_scheduler, daemon=True)
    thread.start()
    return thread