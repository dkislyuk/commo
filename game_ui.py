import logging
import pygame
import time

from config import BACKGROUND, RANDOM_PLAYER_COLOR, PLAYER_RENDER_RADIUS, \
    PLAYER1_COLOR, PROXIMITY_COLOR, PROXIMITY_L2_THRESHOLD, INITIAL_HEALTH
from schemas.commo.ttypes import PlayerType
from sprites import Pokeball, Pikachu

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

    def draw_player(self, player_state, sprite):
        location = player_state.location

        #logger.debug('Rendering location: {}'.format(location))

        sprite.set_loc((location.x, location.y))

        self.screen.blit(sprite.image, sprite.rect)

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
            health = float(player_state.health) / self.player.world.initial_health
            if player_state.type == PlayerType.PLAYER1:
                sprite = Pokeball(health)
                self.draw_player(player_state, sprite)

                self.player_shapes.append((pid, sprite))

                if pid == self.player.id:
                    self.draw_proximity(player_state.location)

            elif player_state.type == PlayerType.RANDOM:
                sprite = Pikachu(health)

                self.draw_player(player_state, sprite)

                self.player_shapes.append((pid, sprite))
            else:
                raise Exception("Unsupported player type: {}".format(player_state.type))

        pygame.display.flip()

        logger.debug("Time to draw: {}".format(time.time() - start))

