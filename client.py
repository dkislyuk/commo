import copy
import logging
import time

from config import SERVER_HOST, SERVER_PORT
from game import Game

from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol

from schemas.commo import CommoServer
from schemas.commo.ttypes import Action, GameStatus, Location
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





# Base Class that defines player interface. UI will work as long as interface is defined.
# Decentralized players should be it's own Player type for simplicity.
class PlayerInterf(object):
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

    def __init__(self):
        self.game = Game()

        self.transport, self.server = connect_to_server()
        self.player_id = self.server.join_game()

        logger = logging.getLogger("commo-client-%s" % self.player_id)
        logger.setLevel('DEBUG')
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
    logger.info("Entering main loop")

    current_location = player.world.state.player_states[player.id].location

    status = player.move(current_location)
    assert status == StatusCode.SUCCESS

    logger.info("Sanity check action OK")
    destination = player.world.random_location()

    while True:
        time.sleep(0.01)

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
                        logger.info("PROXIMITY WARNING with player %s" %
                                    pid)


if __name__ == '__main__':
    player = CentralizedPlayer()
    random_move_agent(player)
