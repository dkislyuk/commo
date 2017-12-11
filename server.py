import logging

from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol
from thrift.server import TServer

from config import DECENTRALIZED
from config import SERVER_PORT
from config import SERVER_THREADS
from config import NUM_LEADERS_PER_SHARD
from config import NUM_SHARDS
from game import Game

from schemas.commo import CommoServer
from schemas.commo.ttypes import ActionResponse
from schemas.commo.ttypes import ActionType
from schemas.commo.ttypes import GameStatus
from schemas.commo.ttypes import ServerPort
from schemas.commo.ttypes import ShardLeaderAssignmentResponse
from schemas.commo.ttypes import StartGameResponse
from schemas.commo.ttypes import StatusCode


logging.basicConfig()
logger = logging.getLogger("commo-server")
logger.setLevel('INFO')


class CommoServerHandler:
    client_count = 0

    def __init__(self):
        self.game = Game(num_shards=NUM_SHARDS)
        self.shard_leaders_assigned = False
        self.shard_leaders_confirmed = False
        self.confirmed_initial_shard_leaders = {}

    def ping(self):
        logger.info('got ping()\'ed successfuly!')

    def join_game(self, player_type):
        player_id = self.game.create_player(player_type)
        return player_id

    def get_shard_assignments(self):
        response = ShardLeaderAssignmentResponse()
        response.status = GameStatus.WAITING_FOR_PLAYERS

        NUMBER_SHARD_LEADERS = NUM_LEADERS_PER_SHARD * NUM_SHARDS

        # need to clean this up
        if self.shard_leaders_assigned:
            response.status = GameStatus.SHARD_LEADERS_ASSIGNED
            response.shard_mapping = self.shard_mapping
        elif not self.shard_leaders_assigned and \
                self.game.num_players() >= NUMBER_SHARD_LEADERS:
            self.shard_leaders_assigned = True

            mapping = {i: [] for i in range(NUM_SHARDS)}
            current_shard = 0
            for player_id, state in self.game.state.player_states.items()[:NUMBER_SHARD_LEADERS]:
                serverport = ServerPort(server='localhost',
                                        port=9000+player_id,
                                        player_id=player_id)

                if len(mapping[current_shard]) == NUM_LEADERS_PER_SHARD:
                    current_shard += 1

                mapping[current_shard].append(serverport)

            response.status = GameStatus.SHARD_LEADERS_ASSIGNED
            response.shard_mapping = mapping
            self.shard_mapping = mapping

        return response

    def confirm_shard_leader(self, player_id, shard_id):
        # TODO: make sure valid assignment
        assert shard_id not in self.confirmed_initial_shard_leaders

        self.confirmed_initial_shard_leaders[shard_id] = player_id
        if len(self.confirmed_initial_shard_leaders) == NUM_SHARDS:
            self.shard_leaders_confirmed = True

    def start_game(self):
        response = StartGameResponse()

        if DECENTRALIZED and not self.shard_leaders_assigned:
            response.status = GameStatus.WAITING_FOR_PLAYERS
            return response

        if DECENTRALIZED and not self.shard_leaders_confirmed:
            response.status = GameStatus.SHARD_LEADERS_ASSIGNED
            return response

        response.status = self.game.start_game()

        logger.info("Attempting to initialize, game state is %s" %
                    GameStatus._VALUES_TO_NAMES[response.status])

        if response.status == GameStatus.STARTED:
            response.updated_game_state = self.game.state
            response.shard_mapping = self.shard_mapping

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

    def leave_shard(self):
        raise Exception("`leave_shard` not allowed on master server!")

    def join_shard(self):
        raise Exception("`join_shard` not allowed on master server!")

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
