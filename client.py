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

class CommoClient(object):

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

    def main_loop(self):
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

        test_action = Action(type=ActionType.MOVE,
                             move_target=self.current_location)

        self.server.take_action(self.player_id, test_action)

        logger.info("Sanity check action OK")
        destination = self.game.random_location()

        while True:
            time.sleep(0.01)

            action = Action()
            action.type = ActionType.MOVE

            if self.current_location != destination:
                action.move_target = next_step(self.current_location, destination)
            else:
                action.move_target = self.current_location
                destination = self.game.random_location()

            response = self.server.take_action(self.player_id, action)
            self.game.state = response.updated_game_state

            if response.status == StatusCode.SUCCESS:
                self.current_location = self.game.state.player_states[self.player_id].location
                logger.info("Moved to %s" % self.current_location)

                for pid, player_state in self.game.state.player_states.iteritems():
                    if pid != self.player_id:
                        if self.game.within_proximity(self.current_location,
                                                      player_state.location):
                            logger.info("PROXIMITY WARNING with player %s" %
                                        pid)


if __name__ == '__main__':
    client = CommoClient()
    client.main_loop()
