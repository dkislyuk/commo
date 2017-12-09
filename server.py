import logging

from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol
from thrift.server import TServer

from game import BoringGame

from schemas.commo import CommoServer
from schemas.commo.ttypes import ActionResponse
from schemas.commo.ttypes import ActionType
from schemas.commo.ttypes import ClientState
from schemas.commo.ttypes import GameState
from schemas.commo.ttypes import GameStatus
from schemas.commo.ttypes import Location
from schemas.commo.ttypes import StartGameResponse
from schemas.commo.ttypes import StatusCode


logging.basicConfig()
logger = logging.getLogger("commo-server")
logger.setLevel('INFO')

NUM_PLAYERS_TO_START = 3
INITIAL_HEALTH = 100


class CommoServerHandler:
    client_count = 0

    def __init__(self):
        self.game_status = GameStatus.WAITING_FOR_PLAYERS
        self.game = BoringGame()
        self.game_state = GameState(clientStates={})

    def ping(self):
        logger.info('got ping()\'ed successfuly!')

    def joinGame(self):
        self.client_count += 1

        client_id = self.client_count

        # import ipdb; ipdb.set_trace()
        self.game_state.clientStates[client_id] = ClientState()

        logger.info("Adding client_id %s" % client_id)

        if self.client_count == NUM_PLAYERS_TO_START:
            self._start_game()

        return client_id

    def initializeClient(self, client_id):
        response = StartGameResponse()

        logger.info("Attempting to initialize, game state is %s" %
                    GameStatus._VALUES_TO_NAMES[self.game_status])

        if self.game_status == GameStatus.WAITING_FOR_PLAYERS:
            response.status = StatusCode.GAME_NOT_STARTED
        elif self.game_status == GameStatus.ENDED:
            response.status = StatusCode.GAME_ENDED
        elif self.game_status == GameStatus.STARTED:
            response.status = StatusCode.SUCCESS
            initial_location = self.game.random_location()

            self.game_state.clientStates[client_id].location = initial_location
            self.game_state.clientStates[client_id].health = INITIAL_HEALTH

            response.initialLocation = initial_location
        else:
            raise Exception("Unknown game status")

        return response

    def takeAction(self, client_id, action):
        response = ActionResponse()

        if action.type == ActionType.MOVE:
            self.game_state.clientStates[client_id].location = \
                    action.moveTarget

            logger.info("Client %s moved to %s" %
                        (client_id, action.moveTarget))
        elif action.type == ActionType.ATTACK:
            pass
        elif action.type == ActionType.HEAL:
            pass

        response.status = StatusCode.SUCCESS
        response.updatedGameState = self.game_state

        return response

    ####################
    # Internal helpers #
    ####################
    def _start_game(self):
        logger.info('#################')
        logger.info('# Starting Game #')
        logger.info('#################')

        self.game_status = GameStatus.STARTED


if __name__ == '__main__':
    handler = CommoServerHandler()
    processor = CommoServer.Processor(handler)
    transport = TSocket.TServerSocket(host='127.0.0.1', port=9090)
    tfactory = TTransport.TBufferedTransportFactory()
    pfactory = TBinaryProtocol.TBinaryProtocolFactory()

    server = TServer.TSimpleServer(processor, transport, tfactory, pfactory)

    logger.info("Starting server!")
    server.serve()
