from concurrent.futures import ThreadPoolExecutor

import grpc

import hawat.dispatcher as dispatcher
import hawat.proto.chat_pb2 as pb2
import hawat.proto.chat_pb2_grpc as pb2_grpc


def serve():
    """Start a server to transact chat messages over gRPC."""
    server = grpc.server(ThreadPoolExecutor(max_workers=10))
    pb2_grpc.add_HawatChatServicer_to_server(ChatServer(), server)
    server.add_insecure_port("[::]:50051")
    server.start()
    server.wait_for_termination()


class ChatServer(pb2_grpc.HawatChatServicer):  # pylint: disable=too-few-public-methods
    """gRPC service for Hawat chats"""

    def send_chat(self, request, context):
        """Handle the `send_chat` rpc function

        Returns:
            ServerChat: server's response to chat message
        """
        response_message = dispatcher.process_message(request.message)
        return pb2.ServerChat(message=response_message)  # pylint: disable=no-member
