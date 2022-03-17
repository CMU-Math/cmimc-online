# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc

from . import coordinator_pb2 as coordinator__pb2


class CoordinatorStub(object):
    """Missing associated documentation comment in .proto file."""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.Serve = channel.stream_stream(
                '/Coordinator/Serve',
                request_serializer=coordinator__pb2.GradeResponse.SerializeToString,
                response_deserializer=coordinator__pb2.GradeRequest.FromString,
                )
        self.SetPassword = channel.unary_unary(
                '/Coordinator/SetPassword',
                request_serializer=coordinator__pb2.Password.SerializeToString,
                response_deserializer=coordinator__pb2.Empty.FromString,
                )


class CoordinatorServicer(object):
    """Missing associated documentation comment in .proto file."""

    def Serve(self, request_iterator, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def SetPassword(self, request, context):
        """this needs to be changed to a proper auth eventually 
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_CoordinatorServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'Serve': grpc.stream_stream_rpc_method_handler(
                    servicer.Serve,
                    request_deserializer=coordinator__pb2.GradeResponse.FromString,
                    response_serializer=coordinator__pb2.GradeRequest.SerializeToString,
            ),
            'SetPassword': grpc.unary_unary_rpc_method_handler(
                    servicer.SetPassword,
                    request_deserializer=coordinator__pb2.Password.FromString,
                    response_serializer=coordinator__pb2.Empty.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'Coordinator', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))


 # This class is part of an EXPERIMENTAL API.
class Coordinator(object):
    """Missing associated documentation comment in .proto file."""

    @staticmethod
    def Serve(request_iterator,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.stream_stream(request_iterator, target, '/Coordinator/Serve',
            coordinator__pb2.GradeResponse.SerializeToString,
            coordinator__pb2.GradeRequest.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def SetPassword(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/Coordinator/SetPassword',
            coordinator__pb2.Password.SerializeToString,
            coordinator__pb2.Empty.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)
