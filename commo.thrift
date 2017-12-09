enum StatusCode {
    SUCCESS = 1
    ILLEGAL_TARGET = 2

    GAME_NOT_STARTED = 10
    GAME_ENDED = 11
}

enum ActionType {
    MOVE = 1
    ATTACK = 2
    HEAL = 3
}

struct Location {
    1: i32 x,
    2: i32 y,
}

struct StartGameResponse {
    1: StatusCode status,
    2: Location initialLocation
}

struct ClientState {
    1: Location location,
    2: i32 health
}

struct Action {
    1: ActionType type,
    2: Location moveTarget,
    3: i32 attackTarget,
    4: i32 healTarget
}

enum GameStatus {
    WAITING_FOR_PLAYERS = 1
    STARTED = 2
    ENDED = 3
}

struct GameState {
    1: map<i32, ClientState> clientStates,
    2: map<i32, i32> clusterAssignments
}

struct ActionResponse {
    1: StatusCode status,
    2: GameState updatedGameState
}

service CommoServer {

   void ping(),
   i32 joinGame(),
   StartGameResponse initializeClient(1: i32 clientId),
   ActionResponse takeAction(1: i32 clientId, 2: Action action),
}

