import logging
import socket
import argparse
import random
import chess

logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%m/%d %I:%M:%S %p', level=logging.DEBUG)


def get_move(fen):
    # parse fen into python-chess object
    board = chess.Board(fen=fen)

    # all legal moves
    legal_moves = list(board.legal_moves)

    #return a random one
    return random.choice(legal_moves)

class Client(object):
    def __init__(self, host, port, tournament_name, player_name):
        self.host = host
        self.port = port
        self.tournament_name = tournament_name
        self.player_name = player_name
        self.socket = None
        self.game_id = None

    def connect(self):
        logging.info("Connecting to %s:%s" % (self.host, self.port))
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((self.host, self.port))
        self.send_message("JOIN", "%s %s" % (self.tournament_name, self.player_name))

    def wait_for_messages(self):
        for line in self.socket.makefile():
            line = line.strip()
            if " " in line:
                action, message = line.split(" ", 1)
            else:
                action, message = line, ""

            self.handle_message(action, message)


    def send_message(self, action, message):
        self.socket.send("%s %s\n" % (action, message))

    def handle_message(self, action, message):
        logging.info("Got message %s %s" % (action, message))
        parts = [p for p in message.split(" ") if len(p)]
        if action == "GAME_PAIRED":
            # We have been paired with a player for a game. We need to ack!
            self.game_id = parts[0]
            white_player = parts[1]
            black_player = parts[2]
            time_limit   = parts[3]
            increment    = parts[4]

            logging.info("game_id %s" % (self.game_id,))
            logging.info("white_player %s" % (white_player,))
            logging.info("black_player %s" % (black_player,))
            logging.info("time_limit %s" % (time_limit,))
            logging.info("increment %s" % (increment,))

            # tell server we're ready to play!
            self.send_message("ACK", self.game_id)

        if action == "GAME_STARTED":
            white_player = parts[1]
            black_player = parts[2]
            white_time   = parts[3]
            black_time   = parts[4]
            fen          = " ".join(parts[5:])
            logging.info("game_id %s" % (self.game_id,))
            logging.info("white_player %s" % (white_player,))
            logging.info("black_player %s" % (black_player,))
            logging.info("white_time %s" % (white_time,))
            logging.info("black_time %s" % (black_time,))
            logging.info("fen %s" % (fen,))

        elif action == "PLAYER_MOVED":
            # a player has moved. We might want to update our game state (this is sent after your moves too)
            game_id      = parts[0]
            moved_player = parts[1]
            move         = parts[2]
            white_player = parts[3]
            black_player = parts[4]
            white_time   = parts[5]
            black_time   = parts[6]
            fen          = " ".join(parts[7:])
        elif action == "CLOCK_UPDATE":
            # sent every few seconds with up to date clock and board state info. Message continence are identical to GAME_STARTED.
            pass

        elif action == "INFO":
            # info from the server we might want to display
            logging.info(message)

        elif action == "YOUR_MOVE":
            white_player = parts[1]
            black_player = parts[2]
            white_time   = parts[3]
            black_time   = parts[4]
            fen          = " ".join(parts[5:])

            move = get_move(fen)
            self.send_message("MOVE", "%s %s" % (self.game_id, str(move)))


        elif action == "GAME_OVER":
            logging.info("Game over: %s" % (message))

parser = argparse.ArgumentParser(description='Chess client.')
parser.add_argument("host", type=str, help="Host to connect to")
parser.add_argument("port", type=int, help="Port to connect to")
parser.add_argument("tournament", type=str, help="Tournament to play in")
parser.add_argument("player", type=str, help="Player name")
args = parser.parse_args()

client = Client(args.host, args.port, args.tournament, args.player)
client.connect()
client.wait_for_messages()


