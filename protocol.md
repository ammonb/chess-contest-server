# Protocol

The Triplebyte chess server allows clients to connect over raw TCP or WebSockets, and take part in chess tournaments. The protocol consists entirely of utf-8 encoded text. Each message consists of a single line.

### Raw TCP
When connecting to the server over TCP, each message is sent as a single line, terminated with a newline character.

### WebSockets
When connecting over WebSockets, each message is sent a single WebSockets text (not binary) message.

### Message format
Each message consists of a single line, and starts with a white-space delimited "action" specifying the type of message. The content of the line following the action depend on the message type. Example messages include:

`INFO This is an important message from the server`
`RESIGN 0ca16ecaede711e7bb5048d705daa9ad`
`YOUR_MOVE 0ca16ecaede711e7bb5048d705daa9ad Ammon Computer 0.85 8.21 8/4P3/8/k7/8/8/3K4/8 b - - 60 157`

## Playing in a tournament
To play in a tournament, the first message a client must send the server is a JOIN message. This takes the form

`JOIN $tournament_name $player_name`

The tournament name must be a tournament already created on the server, while player_name can be any name of a player not already connected to the server.

After the client joins a tournament, the server will pair the client with an opponent for a game. When that happens, the client will receive a GAME_PAIRED message of the form

`GAME_PAIRED $game_id $white_player $black_player $time_limit $increment`

The game ID a GUID that identifies the game, and should be included in all future messages about the game. The other parameters are the details about the game. Time limit and increment are in seconds. After receiving a GAME_PAIRED message, both payers must acknowledge the game within 20 seconds by sending an ACK message ofthe form:

`ACK $game_id`

Once both players have sent ACK messages, the game will start. When the game starts, the server sends a GAME_STARTED message.

`GAME_STARTED $game_id $white_player $black_player $white_time_remaining $black_time_remaining $current_board_fen`

Note that the FEN string itself may contain multiple white spaces. When a new game is starting, the FEN string will simply encode the standard starting position.

The server will then ask players to make moves. It does this by sending a YOUR_MOVE message. The format of the YOUR_MOVE message is identical to the GAME_STARTED message.

`YOUR_MOVE $game_id $white_player $black_player $white_time_remaining $black_time_remaining $current_board_fen`

Clients should respond with a MOVE message, of the form

`MOVE $game_id $move`

The move itself is indicated in long-form algebraic notation, e.g. `d2-d4` or `f7-f8=Q`. Castling may be indicated either via the appropriate king move, or the special strings `O-O` and `O-O-O`. En passant is a regular pawn move. Checks, captures and checkmate are not indicated in the moves.

After any player moves, the server notifies all players of the move (including the player who made the move) by sending a PLAYER_MOVED message.

`PLAYER_MOVED $game_id $moving_player $move $white_player $black_player $white_time_remaining $black_time_remaining $resulting_board_fen`

The moves as reported by the server will be long-form algebraic notation, with castling indicated as a king move. The FEN included in the PLAYER_MOVED message is of the board resulting from the move.

If an illegal move attempted by a client, the server will send the client an INFO message explaining what is wrong, and resend them a YOUR_MOVE message. Clients may also send a `RESIGN $game_id` message at any time to resign a game.

Every few seconds during the game, the server will send all clients a CLOCK_UPDATE message. These messages have the same format as the GAME_STARTED and YOUR_MOVE messages.

When the game is over, the server will send a GAME_OVER message

`GAME_OVER $game_id $result $reason`

Result is either `0-1`, `1-0` or `0.5-0.5`, indicating the outcome of the game. Reason is an English description of who the game ended.

After a game is over, a connected client may be paired with another client for another game. When this happens, they will receive a  new GAME_PAIRED message with a new game ID.


## Observing a game

The protocol also support observing a game. To observe a game, simply send a WATCH command at any time.
`WATCH $game_id`. After sending a watch command, a client will receive one GAME_STATE message (identical in format to the GAME_STARTED message). After this they will receive all PLAYER_MOVED, CLOCK_UPDATE and GAME_OVER messages for that game.


