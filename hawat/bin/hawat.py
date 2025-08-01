import threading

import hawat.grpc_server as h_serve
from hawat.reflection import start_reflection_thread


def main():
    """Run the full Hawat server and concurrent operations"""
    # Start the gRPC server in a separate thread
    grpc_thread = threading.Thread(target=h_serve.serve)
    grpc_thread.start()

    # Example of another concurrent task (replace with your actual task)
    # If the `concurrent_task` is CPU-bound, consider using `multiprocessing.Process` instead of `threading.Thread`
    # concurrent_thread = threading.Thread(target=your_concurrent_task_function, args=(arg1, arg2,))
    # concurrent_thread.start()
    start_reflection_thread()
    # Keep the main thread alive until all daemon threads terminate or explicitly joined
    grpc_thread.join()

    # If you started other threads, join them here as well, e.g., concurrent_thread.join()


if __name__ == "__main__":
    main()
