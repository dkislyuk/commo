import random

from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol
from thrift.server import TServer

from schemas.commo import CommoServer
from schemas.commo.ttypes import Location


class CommoServerHandler:
    client_count = 0

    def __init__(self):
        # initialize game here
        pass

    def ping(self):
        print('ping() success!')

    def joinGame(self):
        self.client_count += 1
        return self.client_count

    def getInitialLocation(self, client_id):
        return Location(x=0, y=0)

    def takeAction(self, client_id, action):
        pass


if __name__ == '__main__':
    handler = CommoServerHandler()
    processor = CommoServer.Processor(handler)
    transport = TSocket.TServerSocket(host='127.0.0.1', port=9090)
    tfactory = TTransport.TBufferedTransportFactory()
    pfactory = TBinaryProtocol.TBinaryProtocolFactory()

    server = TServer.TSimpleServer(processor, transport, tfactory, pfactory)

    print("Starting server")
    server.serve()
