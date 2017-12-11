import click
import logging
import pygame
import time

from multiprocessing import Process

from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol
from thrift.server import TServer

from client import connect_to_master_server, PlayerInterf, random_move_agent, player_agent
from game import Game
from game_ui import GameRenderer
from shard_server import ShardServer

from schemas.commo import CommoServer
from schemas.commo.ttypes import Action
from schemas.commo.ttypes import ActionType
from schemas.commo.ttypes import GameStatus
from schemas.commo.ttypes import PlayerType
from schemas.commo.ttypes import StatusCode


logging.basicConfig()


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

    def __init__(self, player_type):
        super(DecentralizedPlayer, self).__init__(player_type)

        self.game = Game()

        self.transport, self.server = connect_to_master_server()
        self.player_id = self.server.join_game(player_type)

        # By default, not responsible for running a shard server
        self.local_shard_server_object = None

        global logger
        logger = logging.getLogger("commo-client-%s" % self.player_id)
        logger.setLevel('DEBUG')
        logger.info('Joined game with player id: %s' % self.player_id)

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

        response = self.current_shard.server.take_action(self.player_id, action)
        self.game.state = response.updated_game_state
        return response.status

    def heal(self, target_id):
        action = Action(type=ActionType.HEAL,
                        heal_target=target_id)

        response = self.current_shard.server.take_action(self.player_id, action)

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


def start_agent(player, player_type, render):
    time.sleep(2)
    player.initialize_location_and_shard()

    renderer = None
    if render:
        pygame.init()
        renderer = GameRenderer(player)

    if player_type == PlayerType.RANDOM:
        random_move_agent(player, renderer)
    elif player_type == PlayerType.PLAYER1:
        player_agent(player, renderer)

@click.command()
@click.option('--render/--no-render', default=False)
@click.option('--player-type', default="RANDOM", type=click.Choice(PlayerType._NAMES_TO_VALUES.keys()))
def main(render, player_type):
    player_type = PlayerType._NAMES_TO_VALUES[player_type]

    player = DecentralizedPlayer(player_type)
    if player.local_shard_server_object is not None:
        # We are also responsible for running a shard server, run in background
        shard_server_thread = Process(target=player.local_shard_server_object.start_shard_server)
        shard_server_thread.start()

    start_agent(player, player_type, render)

if __name__ == '__main__':
    main()
