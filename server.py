from twisted.protocols import basic
from twisted.internet import protocol
from twisted.application import service, internet
from twisted.internet.protocol import Protocol, Factory
from twisted.internet import reactor, defer
from twisted.web import server
from autobahn.twisted.websocket import WebSocketServerProtocol, WebSocketServerFactory

import logging
import argparse
import traceback

import game_core
from http.root import HttpRoot


logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%m/%d %I:%M:%S %p', level=logging.DEBUG)
parser = argparse.ArgumentParser(description='Chess server.')
parser.add_argument("port", type=int, help="Port on which to listen for connections")
parser.add_argument("--http_port", type=int, default=8080, help="Serve details on the active games over http on this port")
parser.add_argument("--websocket_port", type=int, default=8081, help="Serve details on the active games over http on this port")

args = parser.parse_args()

manager = game_core.Manager()
manager.create_tournament("a", 2, 60*5, 0)


class LineReceiverPlayer(game_core.BasePlayer):
    def __init__(self, connection):
        super(LineReceiverPlayer, self).__init__()
        self.connection = connection

    def send_message(self, action, message):
        self.connection.transport.write(self.format_message(action, message).encode('utf8'))

    def force_disconnect(self):
        self.connection.transport.loseConnection()

class  WebSocketPlayer(game_core.BasePlayer):
    def __init__(self, connection):
        super(WebSocketPlayer, self).__init__()
        self.connection = connection

    def send_message(self, action, message):
        self.connection.sendMessage(self.format_message(action, message).encode('utf8'), False)

    def force_disconnect(self):
        self.connection.sendClose()

class ChessLineProtocol(basic.LineReceiver):

    delimiter = '\n'

    def __init__(self):
        pass

    def connectionMade(self):
        logging.info("Client connected: %s" % (self.transport.getPeer(),))
        self.player = LineReceiverPlayer(self)
        manager.player_connected(self.player)

    def connectionLost(self, reason):
        logging.info("Client disconnected: %s" % (self.transport.getPeer(),))
        manager.player_disconnected(self.player)

    def lineReceived(self, line):
        line = line.decode('utf8').strip()
        if len(line) != 0:
            try:
                action, message = self.player.parse_message(line)
                logging.info("Received message from socket %s %s" % (action, message))
                manager.message_recieved(self.player, action, message)

            except AssertionError, e:
                traceback.print_exc()
                self.player.send_message("INFO", " ".join(e.message.split("\n")))
                self.player.force_disconnect()



class ChessWebSocketsProtocol(WebSocketServerProtocol):

    def onConnect(self, request):
        pass

    def onOpen(self):
        logging.info("WebSocket client connected: %s" % (self.transport.getPeer(),))
        self.player = WebSocketPlayer(self)
        manager.player_connected(self.player)

    def onMessage(self, payload, isBinary):
        try:
            action, message = self.player.parse_message(payload.decode('utf8'))
            logging.info("Received message from websocket %s %s" % (action, message))
            manager.message_recieved(self.player, action, message)
        except AssertionError, e:
            traceback.print_exc()
            self.player.send_message("INFO", " ".join(e.message.split("\n")))
            self.player.force_disconnect()


    def onClose(self, wasClean, code, reason):
        logging.info("WebSocket client disconnected: %s" % (self.transport.getPeer(),))
        manager.player_disconnected(self.player)

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


# line server
factory = Factory()
factory.protocol = ChessLineProtocol
factory.clients = []
reactor.listenTCP(args.port, factory)

# websocket server
websocket_factory = WebSocketServerFactory()
websocket_factory.protocol = ChessWebSocketsProtocol
reactor.listenTCP(args.websocket_port, websocket_factory)

# HTTP server
reactor.listenTCP(args.http_port, server.Site(HttpRoot(manager)))

reactor.run()










