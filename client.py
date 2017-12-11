import click
import copy
import logging
import time

import pygame
from pysyncobj import SyncObj, SyncObjConf

from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol

from config import SERVER_HOST, SERVER_PORT, FPS
from game import Game
from game_ui import GameRenderer

from schemas.commo import CommoServer
from schemas.commo.ttypes import Action, GameStatus, Location, PlayerType
from schemas.commo.ttypes import ActionType
from schemas.commo.ttypes import StatusCode


logging.basicConfig()


def connect_to_server():
    # Make socket
    socket = TSocket.TSocket(SERVER_HOST, SERVER_PORT)
    transport = TTransport.TBufferedTransport(socket)
    protocol = TBinaryProtocol.TBinaryProtocol(transport)
    server = CommoServer.Client(protocol)

    # Connect!
    transport.open()
    server.ping()

    return transport, server


def generate_cluster_serverport(client_id):
    return 'localhost:%s' % (9000 + client_id)


class SyncedGameStateWatcher(SyncObj):
    def __init__(self, client_id):
        conf = SyncObjConf(dynamicMembershipChange=True)
        serverport = generate_cluster_serverport(client_id)
        super(SyncedGameStateWatcher, self).__init__(serverport, [], conf=conf)
        self.__counter = 0


# def create_synced_obj(client_id):
#port = SERVER_PORT + client_id


# Base Class that defines player interface. UI will work as long as interface is defined.
# Decentralized players should be it's own Player type for simplicity.
class PlayerInterf(object):
    def __init__(self, player_type):
        """
        Args:
            player_type: PlayerType
        """
        pass

    @property
    def id(self):
        """
        Returns player id
        """
        raise NotImplementedError()

    @property
    def world(self):
        """
        Returns: Game
        """
        raise NotImplementedError()

    def move(self, location):
        """
        Args:
            location: Location to move to

        Returns:
            StatusCode
        """
        raise NotImplementedError()

    def attack(self, target_id):
        """
        Args:
            target_id: id of target

        Returns:
            StatusCode
        """
        raise NotImplementedError()

    def heal(self, target_id):
        """
        Args:
            target_id: id of target

        Returns:
            StatusCode
        """
        raise NotImplementedError()


class CentralizedPlayer(PlayerInterf):

    def __init__(self, player_type):
        super(CentralizedPlayer, self).__init__(player_type)

        self.game = Game()
        self.transport, self.server = connect_to_server()
        self.player_id = self.server.join_game(player_type)

        # Set up the decentralized watcher
        #self.cluster = SyncedGameStateWatcher(self.player_id)

        logger = logging.getLogger("commo-client-%s" % self.player_id)
        logger.setLevel('INFO')
        logger.info('Joined game with player id: %s' % self.player_id)
        global logger

        # Wait until game begins
        while True:
            response = self.server.start_game()

            if response.status == GameStatus.WAITING_FOR_PLAYERS:
                logger.info("...game not ready yet")
                time.sleep(1)
            elif response.status == GameStatus.STARTED:
                logger.info("...game has started!")
                self.game.state = response.updated_game_state
                break
            elif response.status == GameStatus.ENDED:
                raise Exception("Game already ended")
            else:
                raise Exception("Invalid status code returned %s" % response.status)

        self.current_location = self.game.state.player_states[self.player_id].location
        logger.info('Initial location: %s' % self.current_location)

    @property
    def id(self):
        return self.player_id

    @property
    def world(self):
        return self.game

    def move(self, location):
        action = Action(type=ActionType.MOVE,
                        move_target=location)

        response = self.server.take_action(self.player_id, action)
        self.game.state = response.updated_game_state
        return response.status


def take_step(current_location, move_events):
    """
    Args:
        current_location: Location
        move_events:  list containing possible [pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT]

    Returns:
        Location to move to

    """
    step = copy.deepcopy(current_location)

    if move_events[pygame.K_UP]:
        step.y -= 1
    if move_events[pygame.K_DOWN]:
        step.y += 1
    if move_events[pygame.K_LEFT]:
        step.x -= 1
    if move_events[pygame.K_RIGHT]:
        step.x += 1

    return step


def player_agent(player, renderer):
    assert renderer, "Must have rendering enabled for player agent"

    time.sleep(2)
    logger.info("Entering main loop")

    current_location = player.world.state.player_states[player.id].location

    status = player.move(current_location)
    assert status == StatusCode.SUCCESS

    logger.info("Sanity check action OK")

    clock = pygame.time.Clock()
    while True:
        # limit while loop to max FPS loops / second
        clock.tick(FPS)

        move_events = pygame.key.get_pressed()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                raise Exception("Killed rendering. Disconnecting Player")

        move_target = take_step(current_location, move_events)
        response_status = player.move(move_target)

        if response_status == StatusCode.SUCCESS:
            current_location = player.world.state.player_states[player.id].location
            logger.info("Moved to %s" % current_location)

        renderer.update()


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


def random_move_agent(player, renderer):
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

    time.sleep(2)
    logger.info("Entering main loop")

    current_location = player.world.state.player_states[player.id].location

    status = player.move(current_location)
    assert status == StatusCode.SUCCESS

    logger.info("Sanity check action OK")
    destination = player.world.random_location()

    clock = pygame.time.Clock()
    while True:
        # limit while loop to max FPS loops / second
        clock.tick(FPS)

        if renderer:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    raise Exception("Killed rendering. Disconnecting Player")


        if current_location != destination:
            move_target = next_step(current_location, destination)
        else:
            move_target = current_location
            destination = player.world.random_location()

        response_status = player.move(move_target)

        if response_status == StatusCode.SUCCESS:
            current_location = player.world.state.player_states[player.id].location
            logger.info("Moved to %s" % current_location)

        if renderer:
            renderer.update()

@click.command()
@click.option('--render/--no-render', default=False)
@click.option('--player-type', default="RANDOM", type=click.Choice(PlayerType._NAMES_TO_VALUES.keys()))
def main(render, player_type):
    player_type = PlayerType._NAMES_TO_VALUES[player_type]

    player = CentralizedPlayer(player_type)

    renderer = None
    if render:
        pygame.init()
        renderer = GameRenderer(player)

    if player_type == PlayerType.RANDOM:
        random_move_agent(player, renderer)
    elif player_type == PlayerType.PLAYER1:
        player_agent(player, renderer)


if __name__ == '__main__':
    main()
