from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol
from thrift.server import TServer

from schemas.commo import CommoServer


class CommoServerHandler:
    def __init__(self):
        pass

    def ping(self):
        print('ping() success!')


if __name__ == '__main__':
    handler = CommoServerHandler()
    processor = CommoServer.Processor(handler)
    transport = TSocket.TServerSocket(host='127.0.0.1', port=9090)
    tfactory = TTransport.TBufferedTransportFactory()
    pfactory = TBinaryProtocol.TBinaryProtocolFactory()

    server = TServer.TSimpleServer(processor, transport, tfactory, pfactory)

    print("Starting server")
    server.serve()

