from thrift import Thrift
from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol

from schemas.commo import CommoServer
from schemas.commo.ttypes import Action
from schemas.commo.ttypes import ActionStatusCode
from schemas.commo.ttypes import ActionType
from schemas.commo.ttypes import Location


def main():
    # Make socket
    transport = TSocket.TSocket('localhost', 9090)
    transport = TTransport.TBufferedTransport(transport)
    protocol = TBinaryProtocol.TBinaryProtocol(transport)
    server = CommoServer.Client(protocol)

    # Connect!
    transport.open()

    server.ping()
    print('ping()')

    client_id = server.joinGame()
    print('Joined game with client id: %s' % client_id)

    initial_location = server.getInitialLocation(client_id)
    print('Initial location: %s' % initial_location)


if __name__ == '__main__':
    main()
