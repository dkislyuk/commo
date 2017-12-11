import logging
import random

import numpy as np

from config import GAME_HEIGHT, PROXIMITY_THRESHOLD, INITIAL_HEALTH, NUM_PLAYERS_TO_START, ATTACK_STRENGTH, \
    HEAL_STRENGTH
from config import GAME_WIDTH
from schemas.commo.ttypes import Location, GameState, GameStatus, PlayerState, StatusCode

logger = logging.getLogger("commo-server")
logger.setLevel('INFO')


class Game(object):
    def __init__(self, width=GAME_WIDTH, height=GAME_HEIGHT):
        self.width = width
        self.height = height

        self.game_state = GameState(player_states={})
        self.game_status = GameStatus.WAITING_FOR_PLAYERS

    @property
    def status(self):
        """
        Returns: GameStatus state

        """
        return self.game_status

    @property
    def state(self):
        """
        Returns: GameState state
        """
        #TODO: perhaps only send updated states for players within proximity
        return self.game_state

    @state.setter
    def state(self, state):
        """
        states: GameState
        """
        self.game_state = state

    def _initialize_player(self, player_id, player_type):
        player_state = PlayerState(type=player_type,
                                   location=self.random_location(),
                                   health=INITIAL_HEALTH)
        self.game_state.player_states[player_id] = player_state


    def add_player(self, player_type):
        """
        Args:
            player_type: PlayerType
        Returns: Assigned player id
        """

        player_id = len(self.game_state.player_states)
        # Note: shared thread state updates ok since python is runs statements sequentially
        logger.info("Adding player %s of type %s" % (player_id, player_type))
        assert player_id not in self.game_state.player_states
        self._initialize_player(player_id, player_type)
        return player_id

    def start_game(self):
        """
        Returns: GameStatus

        """
        if len(self.game_state.player_states) >= NUM_PLAYERS_TO_START:
            logger.info('#################')
            logger.info('# Starting Game #')
            logger.info('#################')

            self.game_status = GameStatus.STARTED

        return self.game_status

    def random_location(self):
        x = random.randint(0, self.width - 1)
        y = random.randint(0, self.height - 1)

        return Location(x=x, y=y)

    def within_proximity(self, loc1, loc2):
        l2_dist = np.linalg.norm(np.array([loc1.x, loc1.y]) - np.array([loc2.x, loc2.y]))

        return l2_dist <= PROXIMITY_THRESHOLD


    ### ============== MAIN ACTION METHODS ======================
    def handle_move(self, player_id, target):
        """
        Args:
            player_id:
            target: Location for new location

        Returns:
            StatusCode
        """
        # TODO: determine what is an invalid move
        self.game_state.player_states[player_id].location = target

        logger.info("Player %s moved to %s" % (player_id, target))

        return StatusCode.SUCCESS


    def handle_attack(self, player_id, target_id):
        """
        Args:
            player_id:
            target: i32 player_id for target to attack

        Returns:
            StatusCode
        """
        # TODO: determine what is an invalid move better
        player = self.game_state.player_states[player_id]
        target = self.game_state.player_states[target_id]

        if self.within_proximity(player.location, target.location):
            logger.info("Player %s attack player %s" % (player_id, target_id))

            target.health = max(target.health - ATTACK_STRENGTH, 0)
            return StatusCode.SUCCESS

        return StatusCode.ILLEGAL_ACTION


    def handle_heal(self, player_id, target_id):
        """
        Args:
            player_id:
            target: i32 player_id for target to attack

        Returns:
            StatusCode
        """
        # TODO: determine what is an invalid move better
        player = self.game_state.player_states[player_id]
        target = self.game_state.player_states[target_id]

        if self.within_proximity(player.location, target.location):
            logger.info("Player %s heal player %s" % (player_id, target_id))

            target.health = min(target.health + HEAL_STRENGTH, INITIAL_HEALTH)
            return StatusCode.SUCCESS

        return StatusCode.ILLEGAL_ACTION
