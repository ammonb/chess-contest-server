from twisted.protocols import basic
from twisted.internet import protocol
from twisted.application import service, internet
from twisted.internet.protocol import Protocol, Factory
from twisted.internet import reactor, defer
from twisted.web import server

import logging, argparse, traceback

import game_core



logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%m/%d %I:%M:%S %p', level=logging.DEBUG)
parser = argparse.ArgumentParser(description='Chess server.')
parser.add_argument("port", type=int, help="Port on which to listen for connections")
args = parser.parse_args()

manager = game_core.Manager()
manager.create_tournament("a", 2, 60*5, 0)


class LineReceiverPlayer(game_core.BasePlayer):
    def __init__(self, connection):
        super(LineReceiverPlayer, self).__init__()
        self.connection = connection

    def send_message(self, action, message):

        if len(message):
            m = "%s %s\n" % (action.upper(), message)
        else:
            m = "%s\n" % (action.upper(),)

        self.connection.transport.write(m)

    def force_disconnect(self):
        self.connection.transport.loseConnection()


class ChessServer(basic.LineReceiver):

    delimiter = '\n'

    def __init__(self):
        pass

    def connectionMade(self):
        print "Client joined: %s" % (self,)
        self.factory.clients.append(self)
        self.player = LineReceiverPlayer(self)
        manager.player_connected(self.player)

    def connectionLost(self, reason):
        print "Client left: %s" % (self,)
        self.factory.clients.remove(self)
        manager.player_disconnected(self.player)

    def lineReceived(self, line):
        line = line.strip()
        if len(line) != 0:
            try:
                if " " in line:
                    action, message = line.split(" ", 1)
                else:
                    action, message = line, ""

                message = message.strip()
                action = action.upper()
                print "received message %s %s" % (action, message)
                manager.message_recieved(self.player, action, message)

            except AssertionError, e:
                traceback.print_exc()
                if self.player:
                    self.player.send_message("INFO", " ".join(e.message.split("\n")))

                self.transport.loseConnection()





logging.info("Starting chess server on port %s" % (args.port,))

def update_pairings():
    manager.update_pairings()
    reactor.callLater(3.0, update_pairings)
update_pairings()

def check_timeouts():
    manager.check_timeouts()
    reactor.callLater(1.0, check_timeouts)
check_timeouts()

def send_clock_updates():
    manager.send_clock_updates()
    reactor.callLater(5.0, send_clock_updates)
send_clock_updates()


factory = Factory()
factory.protocol = ChessServer
factory.clients = []
reactor.listenTCP(args.port, factory)
reactor.run()



