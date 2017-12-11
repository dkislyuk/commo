import logging
import pygame

from config import BACKGROUND, RANDOM_PLAYER_COLOR, PLAYER_RENDER_RADIUS, \
    PLAYER1_COLOR, PROXIMITY_COLOR, PROXIMITY_L2_THRESHOLD
from schemas.commo.ttypes import PlayerType

logger = logging.getLogger("renderer")
logger.setLevel('DEBUG')

class GameRenderer(object):
    def __init__(self, player):
        """
        Args:
            player: PlayerInterf instance
        """
        self.player = player

        # Set the height and width of the screen
        size = [player.game.width, player.game.height]
        logger.info('Started game with size: {}'.format(size))
        self.screen = pygame.display.set_mode(size)

        pygame.display.set_caption("CS244b Game")

    def draw_player(self, player_state, color):
        location = player_state.location

        #logger.debug('Rendering location: {}'.format(location))

        pygame.draw.circle(self.screen,
                           color,
                           [location.x, location.y],
                           PLAYER_RENDER_RADIUS)

    def draw_proximity(self, location):
        pygame.draw.circle(self.screen,
                           PROXIMITY_COLOR,
                           [location.x, location.y],
                           PROXIMITY_L2_THRESHOLD,
                           1)

    def update(self):
        # Clear the screen and set the screen background
        self.screen.fill(BACKGROUND)

        for pid, player_state in self.player.world.state.player_states.iteritems():
            if player_state.type == PlayerType.PLAYER1:
                self.draw_player(player_state, PLAYER1_COLOR)

                if pid == self.player.id:
                    self.draw_proximity(player_state.location)

            elif player_state.type == PlayerType.RANDOM:
                self.draw_player(player_state, RANDOM_PLAYER_COLOR)
            else:
                raise Exception("Unsupported player type: {}".format(player_state.type))

        pygame.display.flip()

