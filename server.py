import click
import logging

from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol
from thrift.server import TServer

from config import SERVER_PORT
from config import SERVER_THREADS
from game import Game

from schemas.commo import CommoServer
from schemas.commo.ttypes import ActionResponse
from schemas.commo.ttypes import ActionType
from schemas.commo.ttypes import GameStatus
from schemas.commo.ttypes import StartGameResponse
from schemas.commo.ttypes import StatusCode



logging.basicConfig()
logger = logging.getLogger("commo-server")
logger.setLevel('INFO')

class CommoServerHandler:
    client_count = 0

    def __init__(self):
        self.game = Game()

    def ping(self):
        logger.info('got ping()\'ed successfuly!')

    def join_game(self, player_type):
        player_id = self.game.add_player(player_type)
        return player_id

    def start_game(self):
        response = StartGameResponse()

        response.status = self.game.start_game()

        logger.info("Attempting to initialize, game state is %s" %
                    GameStatus._VALUES_TO_NAMES[response.status])

        if response.status == GameStatus.STARTED:
            response.updated_game_state = self.game.state

        return response

    def take_action(self, player_id, action):
        response = ActionResponse()

        if action.type == ActionType.MOVE:
            assert action.move_target
            response.status = self.game.handle_move(player_id, action.move_target)
        elif action.type == ActionType.ATTACK:
            response.status = self.game.handle_attack(player_id, action.attack_target)
        elif action.type == ActionType.HEAL:
            response.status = self.game.handle_heal(player_id, action.heal_target)

        response.updated_game_state = self.game.state

        return response

if __name__ == '__main__':
    handler = CommoServerHandler()
    processor = CommoServer.Processor(handler)
    transport = TSocket.TServerSocket(host='0.0.0.0', port=SERVER_PORT)
    tfactory = TTransport.TBufferedTransportFactory()
    pfactory = TBinaryProtocol.TBinaryProtocolFactory()

    server = TServer.TThreadPoolServer(processor, transport, tfactory, pfactory)
    server.setNumThreads(SERVER_THREADS)

    logger.info("Starting server!")
    server.serve()
