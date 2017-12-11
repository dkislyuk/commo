import logging
import pygame
import time

from config import BACKGROUND, RANDOM_PLAYER_COLOR, PLAYER_RENDER_RADIUS, \
    PLAYER1_COLOR, PROXIMITY_COLOR, PROXIMITY_L2_THRESHOLD, INITIAL_HEALTH
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

        self.player_shapes = []

    @property
    def drawn_players(self):
        """
        Returns: returns player shapes so collision detection can be done
        """
        return self.player_shapes

    def draw_player(self, player_state, color):
        location = player_state.location

        health = float(player_state.health) / self.player.world.initial_health
        assert health <= 1.0 and health >= 0.0
        color = tuple([health * c for c in list(color)])

        #logger.debug('Rendering location: {}'.format(location))

        return pygame.draw.circle(self.screen,
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
        start = time.time()
        # Clear the screen and set the screen background
        self.screen.fill(BACKGROUND)

        self.player_shapes = []
        for pid, player_state in self.player.world.state.player_states.iteritems():
            if player_state.type == PlayerType.PLAYER1:
                shape = self.draw_player(player_state, PLAYER1_COLOR)

                self.player_shapes.append((pid, shape))

                if pid == self.player.id:
                    self.draw_proximity(player_state.location)

            elif player_state.type == PlayerType.RANDOM:
                shape = self.draw_player(player_state, RANDOM_PLAYER_COLOR)

                self.player_shapes.append((pid, shape))
            else:
                raise Exception("Unsupported player type: {}".format(player_state.type))

        pygame.display.flip()

        logger.debug("Time to draw: {}".format(time.time() - start))

