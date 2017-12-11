import logging
import pygame

from config import BACKGROUND, RANDOM_PLAYER_COLOR, PLAYER_RENDER_RADIUS, \
    PLAYER1_COLOR
from schemas.commo.ttypes import PlayerType

logger = logging.getLogger("renderer")
logger.setLevel('DEBUG')

class GameRenderer(object):
    def __init__(self, player):
        """
        Args:
            player: PlayerInterf instance
        """

        pygame.init()

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

    def update(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                raise Exception("Killed rendering. Disconnecting Player")

        # Clear the screen and set the screen background
        self.screen.fill(BACKGROUND)

        for _, player_state in self.player.world.state.player_states.iteritems():

            logger.debug('Rendering player type: {}'.format(player_state.type))
            if player_state.type == PlayerType.PLAYER1:
                self.draw_player(player_state, PLAYER1_COLOR)
            elif player_state.type == PlayerType.RANDOM:
                self.draw_player(player_state, RANDOM_PLAYER_COLOR)
            else:
                raise Exception("Unsupported player type: {}".format(player_state.type))

        pygame.display.flip()

