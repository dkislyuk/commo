import logging
import time

from thrift import Thrift
from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol

from schemas.commo import CommoServer
from schemas.commo.ttypes import Action
from schemas.commo.ttypes import ActionType
from schemas.commo.ttypes import StatusCode
from schemas.commo.ttypes import Location


logging.basicConfig()


def run_client():
    # Make socket
    transport = TSocket.TSocket('localhost', 9090)
    transport = TTransport.TBufferedTransport(transport)
    protocol = TBinaryProtocol.TBinaryProtocol(transport)
    server = CommoServer.Client(protocol)

    # Connect!
    transport.open()

    server.ping()

    client_id = server.joinGame()
    transport.close()

    logger = logging.getLogger("commo-client-%s" % client_id)
    logger.setLevel('DEBUG')
    logger.info('Joined game with client id: %s' % client_id)

    initial_location = None

    # Wait until game begins
    while True:
        transport.open()
        response = server.initializeClient(client_id)
        transport.close()

        print response

        if response.status == StatusCode.GAME_NOT_STARTED:
            logger.info("...game not ready yet")
            time.sleep(1)
        elif response.status == StatusCode.SUCCESS:
            logger.info("...game has started!")
            initial_location = response.initialLocation
            break
        else:
            raise Exception("Invalid status code returned %s" % response.status)

    logger.info("moving to next stage")
    time.sleep(2)

    test_action = Action()
    test_action.type = ActionType.MOVE
    test_action.moveTarget = initial_location

    transport.open()
    logger.info("taking test action")
    server.takeAction(client_id, test_action)
    transport.close()

    logger.info('Initial location: %s' % initial_location)


if __name__ == '__main__':
    run_client()
