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


class CommoClient:

    def __init__(self):
        # Make socket
        socket = TSocket.TSocket('localhost', 9090)
        self.transport = TTransport.TBufferedTransport(socket)
        protocol = TBinaryProtocol.TBinaryProtocol(self.transport)
        self.server = CommoServer.Client(protocol)

        # Connect!
        self.transport.open()
        self.server.ping()

        self.client_id = self.server.joinGame()
        self.transport.close()

        logger = logging.getLogger("commo-client-%s" % self.client_id)
        logger.setLevel('DEBUG')
        logger.info('Joined game with client id: %s' % self.client_id)
        global logger

        self.initial_location = None

        # Wait until game begins
        while True:
            self.transport.open()
            response = self.server.initializeClient(self.client_id)
            self.transport.close()

            print response

            if response.status == StatusCode.GAME_NOT_STARTED:
                logger.info("...game not ready yet")
                time.sleep(1)
            elif response.status == StatusCode.SUCCESS:
                logger.info("...game has started!")
                self.initial_location = response.initialLocation
                break
            else:
                raise Exception("Invalid status code returned %s" % response.status)

        logger.info('Initial location: %s' % self.initial_location)

    def main_loop(self):
        time.sleep(2)
        logger.info("Entering main loop")

        test_action = Action()
        test_action.type = ActionType.MOVE
        test_action.moveTarget = self.initial_location

        self.transport.open()
        logger.info("taking test action")
        self.server.takeAction(self.client_id, test_action)
        self.transport.close()


if __name__ == '__main__':
    client = CommoClient()
    client.main_loop()
