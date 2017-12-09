import logging
import random
import time

from game import BoringGame

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

        initial_location = None

        # Wait until game begins
        while True:
            self.transport.open()
            response = self.server.initializeClient(self.client_id)
            self.transport.close()

            if response.status == StatusCode.GAME_NOT_STARTED:
                logger.info("...game not ready yet")
                time.sleep(1)
            elif response.status == StatusCode.SUCCESS:
                logger.info("...game has started!")
                initial_location = response.initialLocation
                break
            else:
                raise Exception("Invalid status code returned %s" % response.status)

        self.current_location = initial_location

        logger.info('Initial location: %s' % initial_location)

    def main_loop(self):
        time.sleep(2)
        logger.info("Entering main loop")

        test_action = Action()
        test_action.type = ActionType.MOVE
        test_action.moveTarget = self.current_location

        self.transport.open()
        self.server.takeAction(self.client_id, test_action)
        self.transport.close()

        logger.info("Sanity check action OK")

        destination = BoringGame().random_location()

        while True:
            time.sleep(1)

            action = Action()
            action.type = ActionType.MOVE
            action.moveTarget = self.current_location

            if self.current_location != destination:
                if destination[0] > self.current_location.x:
                    action.moveTarget.x += 1
                elif destination[0] < self.current_location.x:
                    action.moveTarget.x -= 1

                if destination[1] > self.current_location.y:
                    action.moveTarget.y += 1
                elif destination[1] < self.current_location.y:
                    action.moveTarget.y -= 1
            else:
                destination = BoringGame().random_location()

            self.transport.open()
            response = self.server.takeAction(self.client_id, action)
            self.transport.close()

            if response.status == StatusCode.SUCCESS:
                client_states = response.updatedGameState.clientStates
                self.current_location = client_states[self.client_id].location
                logger.info("Moved to %s" % self.current_location)


if __name__ == '__main__':
    client = CommoClient()
    client.main_loop()
