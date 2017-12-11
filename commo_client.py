import copy
import logging
import time

from multiprocessing import Process

from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol
from thrift.server import TServer

from client import connect_to_master_server, PlayerInterf
from game import Game
from shard_server import ShardServer

from schemas.commo import CommoServer
from schemas.commo.ttypes import Action
from schemas.commo.ttypes import GameStatus
from schemas.commo.ttypes import ActionType
from schemas.commo.ttypes import StatusCode
from schemas.commo.ttypes import PlayerType


logging.basicConfig()


# def generate_cluster_serverport(player_id):
#     return 'localhost:%s' % (9000 + player_id)
#     self.action_log = {}
#     self.action_log[client_id] = []

# @replicated
# def broadcast_action(self, client_id, action):
#     logger.info("Writing to distributed action log: %s" % action)
#     assert client_id in self.action_log
#     self.action_log[client_id].append(action)

# def get_action_log(self, client_id):
#     # This needs to be versioned somehow
#     return self.action_log.get(client_id)

class ShardServerWrapper:
    server = None

    def __init__(self, shard_serverport):
        # Make socket
        # fix the offset hack
        socket = TSocket.TSocket(shard_serverport.server, shard_serverport.port + 1000)
        self.transport = TTransport.TBufferedTransport(socket)
        protocol = TBinaryProtocol.TBinaryProtocol(self.transport)
        self.server = CommoServer.Client(protocol)

        # Connect!
        self.transport.open()
        self.server.ping()

    def close(self):
        self.transport.close()


class DecentralizedPlayer(PlayerInterf):

    def __init__(self):
        self.game = Game()

        self.transport, self.server = connect_to_master_server()
        self.player_id = self.server.join_game(PlayerType.RANDOM)

        # By default, not responsible for running a shard server
        self.local_shard_server_object = None

        global logger

        logger = logging.getLogger("commo-client-%s" % self.player_id)
        logger.setLevel('DEBUG')
        logger.info('Joined game with player id: %s' % self.player_id)

        # # Set up the decentralized watcher
        # self.cluster = SyncedGameStateWatcher(self.player_id)

        # Wait for potential shard assignment
        waiting_for_shard_assignments = True
        while waiting_for_shard_assignments:
            response = self.server.get_shard_assignments()

            if response.status == GameStatus.WAITING_FOR_PLAYERS:
                logger.info("...not enough players yet")
                time.sleep(1)
            elif response.status == GameStatus.SHARD_LEADERS_ASSIGNED:
                waiting_for_shard_assignments = False
                mapping = response.shard_mapping
                for shard_id, assignments in mapping.iteritems():
                    for info in assignments:
                        if self.player_id == info.player_id:
                            self.handle_shard_leader_assignment(mapping, shard_id)
                            break
            else:
                break

        # Shards have been assigned, wait for game to start
        while True:
            response = self.server.start_game()

            if response.status == GameStatus.SHARD_LEADERS_ASSIGNED:
                logger.info("...waiting on shard leader confirmation")
                time.sleep(1)
            elif response.status == GameStatus.STARTED:
                logger.info("...game has started!")
                self.shard_mapping = response.shard_mapping
                self.game.state = response.updated_game_state
                break
            elif response.status == GameStatus.ENDED:
                raise Exception("Game already ended")
            else:
                raise Exception("Invalid status code returned %s" % response.status)

        logger.info("_____________________________________________")

    def handle_shard_leader_assignment(self, shard_mapping, assigned_shard_id):
        logger.info("Starting up local shard server")
        self.local_shard_server_object = ShardServer(shard_mapping,
                                                     assigned_shard_id,
                                                     self.player_id)
        if self.local_shard_server_object.initial_leader:
            self.server.confirm_shard_leader(self.player_id, assigned_shard_id)

    def initialize_location_and_shard(self):
        self.current_location = self.game.state.player_states[self.player_id].location
        logger.info('Initial location: %s' % self.current_location)

        # Connect to initial shard server
        initial_shard_id = self.game.location_to_shard_id(self.current_location)
        self.current_shard_id = initial_shard_id
        initial_shard_serverport = self.pick_shard_server(initial_shard_id)
        self.current_shard = ShardServerWrapper(initial_shard_serverport)
        logger.info('Connected to initial shard server: %s' % initial_shard_serverport)

        player_state = self.game.get_player_state(self.player_id)
        self.current_shard.server.join_shard(self.player_id, self.current_shard_id, player_state)
        logger.info('Entered player state to initial shard server')

    @property
    def id(self):
        return self.player_id

    @property
    def world(self):
        return self.game

    def attack(self, target_id):
        action = Action(type=ActionType.ATTACK,
                        attack_target=target_id)

        response = self.server.take_action(self.player_id, action)
        self.game.state = response.updated_game_state
        return response.status

    def heal(self, target_id):
        action = Action(type=ActionType.HEAL,
                        heal_target=target_id)

        response = self.server.take_action(self.player_id, action)

        self.game.state = response.updated_game_state
        return response.status

    def move(self, location):
        action = Action(type=ActionType.MOVE,
                        move_target=location)

        # # Write action to distributed log
        # self.cluster.broadcast_action(self.player_id, action)

        #response = self.server.take_action(self.player_id, action)
        self.assign_to_shard(location)

        response = self.current_shard.server.take_action(self.player_id, action)

        self.game.state = response.updated_game_state
        return response.status

    def pick_shard_server(self, shard_id):
        num_servers_in_shard = len(self.shard_mapping[shard_id])
        return self.shard_mapping[shard_id][self.player_id % num_servers_in_shard]

    def assign_to_shard(self, location):
        shard_id = self.game.location_to_shard_id(location)

        if shard_id == self.current_shard_id:
            return
        else:
            logger.info('Switching from shard %s to %s' % (self.current_shard_id, shard_id))
            self.current_shard.server.leave_shard(self.player_id, self.current_shard_id)
            self.current_shard.close()

            # Switch over to new shard server
            self.current_shard_id = shard_id
            new_shard_serverport = self.pick_shard_server(shard_id)
            self.current_shard = ShardServerWrapper(new_shard_serverport)
            logger.info('****************************************')
            logger.info('Connected to new shard server: %s' % new_shard_serverport)
            logger.info('****************************************')

            player_state = self.game.get_player_state(self.player_id)
            self.current_shard.server.join_shard(self.player_id, shard_id, player_state)


def random_move_agent(player):
    """
    TODO:
    Main loop should be outside of client.

    We need three types of players:
        - Random Players like what is implemented here
        - Hacker Players that try to do illegal moves
        - User Players which operators can control to manipulate the game manually

    Need to handle disconnects client wise. We should show if a client disconnects, game state will eventually
    remove him.

    Overall properties of game (we should show these via visualizations and they should hold for decentralized system):
        - Safety - be able to detect hackers (moving too fast or hitting/healing someone outside proximity)
        - Network Tolerance - if client loses connection, they are removed from game
        - Correctness - game actually works (we can move around a player in game and see actions make sense)
    """

    def next_step(current_location, destination):
        """
        Args:
            current_location: Location
            destination: Location

        Returns:
            Location for next step to take
        """
        step = copy.deepcopy(current_location)
        if destination.x > current_location.x:
            step.x += 1
        elif destination.x < current_location.x:
            step.x -= 1

        if destination.y > current_location.y:
            step.y += 1
        elif destination.y < current_location.y:
            step.y -= 1

        return step

    time.sleep(2)
    player.initialize_location_and_shard()

    current_location = player.world.state.player_states[player.id].location

    status = player.move(current_location)
    assert status == StatusCode.SUCCESS

    logger.info("Sanity check action OK")
    destination = player.world.random_location()

    logger.info("Entering main movement loop")

    while True:
        time.sleep(0.1)

        if current_location != destination:
            move_target = next_step(current_location, destination)
        else:
            move_target = current_location
            destination = player.world.random_location()

        response_status = player.move(move_target)

        if response_status == StatusCode.SUCCESS:
            current_location = player.world.state.player_states[player.id].location
            logger.info("Moved to %s" % current_location)

            for pid, player_state in player.world.state.player_states.iteritems():
                if pid != player.id:
                    if player.world.within_proximity(current_location,
                                                     player_state.location):
                        logger.info("PROXIMITY WARNING (to player %s)" % pid)

            #             proximity_serverport = generate_cluster_serverport(pid)

            #             # Will be a no-op if player already added
            #             player.cluster.addNodeToCluster(proximity_serverport)

            #             # Warning! This data may be stale, must check if you're
            #             # synced with pid before using it.
            #             action_log = player.cluster.get_action_log(pid)

            #             if action_log and len(action_log) > 0:
            #                 logger.info("have data from a neighbor")

            # # Warning! Leader is not garaunteed to be synchronized
            # # at this stage.
            # current_leader = player.cluster._getLeader()
            # if current_leader != player.cluster._getSelfNodeAddr():
            #     # Reporting to somebody else:
            #     logger.info("Reporting to another leader: %s" % current_leader)
            #     #import ipdb; ipdb.set_trace()

            #player.cluster

            # Warning! In this stage, there may be multiple group
            # leaders.

            # # Wait until cluster has been successfully formed
            # while True:
            #     if player.cluster._printStatus() is None:
            #         # need to refactor this since gameplay is
            #         # affected
            #         time.sleep(0.01)
            #     else:
            #         #assert player.cluster._getLeader() is not None
            #         break

            # # assert player.cluster._getLeader() is not None
            # import ipdb; ipdb.set_trace()


if __name__ == '__main__':
    player = DecentralizedPlayer()

    if player.local_shard_server_object is not None:
        # We are also responsible for running a shard server, run in background
        shard_server_thread = Process(target=player.local_shard_server_object.start_shard_server)
        shard_server_thread.start()

    agent_thread = Process(target=random_move_agent, args=(player,))
    agent_thread.start()

    agent_thread.join()
