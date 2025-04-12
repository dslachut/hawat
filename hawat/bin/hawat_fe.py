from sys import stderr

import grpc

import hawat.proto.chat_pb2 as pb2
import hawat.proto.chat_pb2_grpc as pb2_grpc

_START_MSG = "Welcome to Hawat!\nType to begin chatting...\n\n"
_CLOSE_MSG = "---\nClosing. Have a nice day!"


def main() -> None:
    """Run the simple example Hawat client."""
    channel = grpc.insecure_channel("localhost:50051")
    stub = pb2_grpc.HawatChatStub(channel)
    print(_START_MSG)
    try:
        while True:
            client_msg = input("> ")
            client_chat = pb2.ClientChat(message=client_msg)  # pylint: disable=no-member
            server_chat = stub.send_chat(client_chat)
            print(">>", server_chat.message)
    except KeyboardInterrupt:
        print(_CLOSE_MSG)
    except Exception as e:
        print(e, file=stderr)
    finally:
        channel.close()


if __name__ == "__main__":
    main()
