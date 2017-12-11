import logging
import pygame

from config import BACKGROUND, RANDOM_PLAYER_COLOR, USER_PLAYER_ID, USER_PLAYER_COLOR, PLAYER_RENDER_RADIUS

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

        logger.debug('Rendering location: {}'.format(location))

        pygame.draw.circle(self.screen,
                           (255, 0, 0),
                           [location.x, location.y],
                           PLAYER_RENDER_RADIUS)

    def update(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                raise Exception("Killed rendering. Disconnecting Player")

        # Clear the screen and set the screen background
        self.screen.fill(BACKGROUND)

        for pid, player_state in self.player.world.state.player_states.iteritems():
            if pid == USER_PLAYER_ID:
                self.draw_player(player_state, USER_PLAYER_COLOR)
            else:
                self.draw_player(player_state, RANDOM_PLAYER_COLOR)

        pygame.display.flip()


"""
    for event in pygame.event.get():  # User did something
        if event.type == pygame.QUIT:  # If user clicked close
            done = True  # Flag that we are done so we exit this loop
"""


