enum ActionStatusCode {
    SUCCESS = 1
    ILLEGAL_TARGET = 2
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

struct Action {
    1: ActionType type,
    2: Location moveTarget,
    3: Location attackTarget,
    4: Location healTarget
}

service CommoServer {

   void ping(),
   i32 joinGame(),
   Location getInitialLocation(1: i32 clientId),
   ActionStatusCode takeAction(1: i32 clientId, 2: Action action),

}
