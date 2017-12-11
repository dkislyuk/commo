struct Location {
    1: i32 x,
    2: i32 y,
}

enum GameStatus {
    WAITING_FOR_PLAYERS = 1
    SHARD_LEADERS_ASSIGNED = 2

    STARTED = 3
    ENDED = 4
}

// Just used for rendering
enum PlayerType {
    RANDOM = 1
    HACKER = 2
    PLAYER1 = 3
}

struct PlayerState {
    3: PlayerType type,
    1: Location location,
    2: i32 health
}

struct GameState {
    1: map<i32, PlayerState> player_states,
    2: map<i32, i32> clusters
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

struct ServerPort {
    1: string server,
    2: i16 port,
    3: i32 player_id
}

struct StartGameResponse {
    1: GameStatus status,
    2: GameState updated_game_state
    3: map<i32, list<ServerPort>> shard_mapping
}

struct ActionResponse {
    1: StatusCode status,
    2: GameState updated_game_state
}

struct ClockSyncResponse {
    1: StatusCode status
    2: i64 timestamp
}

struct ShardLeaderAssignmentResponse {
    1: GameStatus status,
    2: map<i32, list<ServerPort>> shard_mapping
}

struct LeaveShardResponse {
    1: StatusCode status
}

struct JoinShardResponse {
    1: StatusCode status
}

service CommoServer {
   void ping(),
   i32 join_game(1: PlayerType type),

   ShardLeaderAssignmentResponse get_shard_assignments(),
   void confirm_shard_leader(1: i32 player_id, 2: i32 shard_id),

   StartGameResponse start_game(),
   ActionResponse take_action(1: i32 player_id, 2: Action action),

   LeaveShardResponse leave_shard(1: i32 player_id, 2: i32 shard_id),
   JoinShardResponse join_shard(1: i32 player_id,
                                2: i32 shard_id,
                                3: PlayerState player_state),

   # Decentralized COMMO
   ClockSyncResponse clock_sync(1: i32 client_id, 2: i64 timestamp),
}

