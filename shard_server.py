import logging
import time


from pysyncobj import SyncObj
from pysyncobj import SyncObjConf
from pysyncobj import replicated
from pysyncobj.batteries import ReplDict

from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol
from thrift.server import TServer

from client import connect_to_master_server, PlayerInterf
from config import SERVER_HOST, SERVER_PORT, SERVER_THREADS
from game import Game

from schemas.commo import CommoServer
from schemas.commo.ttypes import Action
from schemas.commo.ttypes import ActionResponse
from schemas.commo.ttypes import ActionType
from schemas.commo.ttypes import GameState
from schemas.commo.ttypes import GameStatus
from schemas.commo.ttypes import JoinShardResponse
from schemas.commo.ttypes import LeaveShardResponse
from schemas.commo.ttypes import Location
from schemas.commo.ttypes import PlayerState
from schemas.commo.ttypes import StatusCode

logging.basicConfig()


def generate_serverport(serverport_object):
    return '%s:%s' % (serverport_object.server, serverport_object.port)


class ShardSyncWatcher(SyncObj):
    def __init__(self, serverport, other_members):
        logger.info("Initializing SyncObj with serverport %s (others: %s)" %
                    (serverport, other_members))

        self.replicated_game_state = ReplDict()

        conf = SyncObjConf(dynamicMembershipChange=False)
        super(ShardSyncWatcher, self).__init__(
            serverport, other_members, conf=conf,
            consumers=[self.replicated_game_state])

        self.__action_clock = 0

    @replicated
    def register_action(self, action):
        self.__action_clock += 1


class ShardServerHandler:

    def __init__(self, replicated_storage, synced_obj):
        self.sharded_game = Game()
        # self.sharded_game.game_state = \
        #     GameState(player_states=replicated_storage)

        self.synced_obj = synced_obj
        self.replicated_storage = replicated_storage

    def ping(self):
        logger.info("Sanity check of shard server by a client")

    # Only valid action
    def take_action(self, player_id, action):
        response = ActionResponse()

        if action.type == ActionType.MOVE:
            assert action.move_target
            response.status = self.sharded_game.handle_move(player_id, action.move_target)
        elif action.type == ActionType.ATTACK:
            response.status = self.sharded_game.handle_attack(player_id, action.attack_target)
        elif action.type == ActionType.HEAL:
            response.status = self.sharded_game.handle_heal(player_id, action.heal_target)

        response.updated_game_state = self.sharded_game.state

        return response

    def join_shard(self, player_id, shard_id, player_state):
        response = JoinShardResponse()
        self.sharded_game.add_player(player_id, player_state)

        # logger.info("Setting synced state....")
        # self.replicated_storage.set(-1, player_state, sync=True)

        # while True:
        #     synced = (player_id in self.sharded_game.state.player_states.keys())
        #     if synced:
        #         break
        #     logger.info("Player %s not in game state yet, blocking... (available players %s)" %
        #                 (player_id, self.sharded_game.state.player_states.keys()))
        #     logger.info(self.replicated_storage)
        #     logger.info(self.replicated_storage.get(-1))
        #     logger.info(self.replicated_storage.keys())
        #     logger.info(self.synced_obj.isReady())
        #     logger.info(self.synced_obj._isLeader())

        #     time.sleep(1)

        return response

    def leave_shard(self, player_id, shard_id):
        response = LeaveShardResponse()
        self.sharded_game.remove_player(player_id)
        return response


class ShardServer:

    def __init__(self, shard_mapping, assigned_shard_id, owner_player_id):
        global logger
        logger = logging.getLogger("commo-shard-server-%s" % assigned_shard_id)
        logger.setLevel('DEBUG')

        self.shard_mapping = shard_mapping

        my_serverport_str = None
        self.my_serverport = None

        # others = copy.deepcopy(self.shard_mapping)
        others = []
        for info in shard_mapping[assigned_shard_id]:
            if info.player_id != owner_player_id:
                others.append(generate_serverport(info))
            else:
                self.my_serverport = info
                my_serverport_str = generate_serverport(info)

        # Set up RAFT with fellow shard leaders
        self.watcher = ShardSyncWatcher(my_serverport_str, others)

        while not self.watcher.isReady():
            time.sleep(0.05)

        self.initial_leader = self.watcher._isLeader()

        if self.initial_leader:
            logger.info('%s is the initial leader for shard id %s' %
                        (my_serverport_str, assigned_shard_id))

        host = self.my_serverport.server
        port = self.my_serverport.port

        handler = ShardServerHandler(replicated_storage=self.watcher.replicated_game_state,
                                     synced_obj=self.watcher)
        processor = CommoServer.Processor(handler)
        transport = TSocket.TServerSocket(host=host, port=port + 1000)
        tfactory = TTransport.TBufferedTransportFactory()
        pfactory = TBinaryProtocol.TBinaryProtocolFactory()

        self.server = TServer.TThreadPoolServer(processor, transport, tfactory, pfactory)
        self.server.setNumThreads(SERVER_THREADS)

        # Make the game state synchronized within the RAFT server

        #shared_game_state = GameState(player_states=self.watcher.replicated_game_state)

        # logger.info(self.watcher.replicated_game_state)

        # self.watcher.replicated_game_state[-1] = PlayerState(location=Location(x=20, y=20), health=100)

        # while True:
        #     state = self.watcher.replicated_game_state.get(-1)
        #     logger.info(state)

        #     if state:
        #         break

        #     time.sleep(1)

        # logger.info("REPLICATED STATE ****************")
        # logger.info(shared_game_state.player_states[-1])
        # logger.info("REPLICATED STATE ****************")

        #handler.sharded_game.state = shared_game_state

    def start_shard_server(self):
        logger.info("Starting shard server %s!" % self.my_serverport)
        self.server.serve()
