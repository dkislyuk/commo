# Server
SERVER_PORT = "8010"
SERVER_HOST = "127.0.0.1"
# Enter the IP address of remote host you want. Do not record it since IP should be hidden (proprietary machine)
SERVER_THREADS = 1000

# Game
NUM_PLAYERS_TO_START = 3
PROXIMITY_L2_THRESHOLD = 250
GAME_WIDTH = 1000
GAME_HEIGHT = 1000
ATTACK_STRENGTH = 20
HEAL_STRENGTH = 20

FPS = 30

# Player
INITIAL_HEALTH = 100


# == RENDER OPTIONS ==
# Google colors instead of any custom ones because i have no sense of good color palettes.
RANDOM_PLAYER_COLOR = (72, 133, 237)  # blue
PLAYER1_COLOR = (60, 186, 84)     # green
PROXIMITY_COLOR = PLAYER1_COLOR
HACKER_PLAYER_COLOR = (219, 50, 54)   # red
BACKGROUND = (255, 236, 179)          # light yellow

PLAYER_RENDER_RADIUS = 10
