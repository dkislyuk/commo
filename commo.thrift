struct Location {
    1: i32 x,
    2: i32 y,
}

enum GameStatus {
    WAITING_FOR_PLAYERS = 1
    STARTED = 2
    ENDED = 3
}

struct PlayerState {
    1: Location location,
    2: i32 health
}

struct GameState {
    1: map<i32, PlayerState> player_states,
    2: map<i32, i32> clusters
}

struct StartGameResponse {
    1: GameStatus status,
    2: GameState updated_game_state
}

enum StatusCode {
    SUCCESS = 1
    ILLEGAL_ACTION = 2
    YOU_ARE_A_HACKER = 3
}

enum ActionType {
    MOVE = 1
    ATTACK = 2
    HEAL = 3
}


struct Action {
    1: ActionType type,
    2: Location move_target,
    3: i32 attack_target,
    4: i32 heal_target
}

struct ActionResponse {
    1: StatusCode status,
    2: GameState updated_game_state
}

struct ClockSyncResponse {
    1: StatusCode status
    2: i64 timestamp
}

service CommoServer {
   void ping(),
   i32 join_game(),
   StartGameResponse start_game(),
   ActionResponse take_action(1: i32 player_id, 2: Action action),

   ClockSyncResponse clockSync(1: i32 clientId, 2: i64 timestamp),
}

