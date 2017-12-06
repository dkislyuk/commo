from thrift import Thrift
from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol

from schemas.commo import CommoServer


def main():
    # Make socket
    transport = TSocket.TSocket('localhost', 9090)
    transport = TTransport.TBufferedTransport(transport)
    protocol = TBinaryProtocol.TBinaryProtocol(transport)
    client = CommoServer.Client(protocol)

    # Connect!
    transport.open()

    client.ping()
    print('ping()')


if __name__ == '__main__':
    main()
