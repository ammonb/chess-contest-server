from twisted.web.resource import Resource
from twisted.web.resource import NoResource
from twisted.web.static import File



class GameResource(Resource):
    def __init__(self, game):
        self.game = game
        self.children = []

    def getChild(self, name, request):
        if name == '':
            return self
        elif name == 'static':
            return File('./static/')
        else:
            return NoResource()


    def render_GET(self, request):
        title = "%s (white) vs. (black) %s, game in %s:%s" % (self.game.players[0].name, self.game.players[1].name, self.game.time_limit, self.game.increment)
        html = """
            <html>
            <head>
            <base href="/static/">
            <title>{title}</title>
            <link rel="stylesheet" href="/static/css/chessboard-0.3.0.css" />
            </head>
            <body>
            <h2>{title}</h2>
            <div id="white_name"></div>
            <div id="black_name"></div>
            <div id="board" style="width: 400px"></div>
            <h3><div id="status_div">{game_status}</div></h3>
            <pre><div id="game_pgn" style="width: 400px">{game_pgn}</div></pre>
            <script src="js/jquery-3.2.1.js"></script>
            <script src="js/chessboard-0.3.0.js"></script>
            <script src="js/game_lib.js"></script>
            <script>
                window.onload = function() {{
                    var board = ChessBoard('board');
                    var status_div = document.getElementById("status_div");
                    var white_name_div = document.getElementById("white_name");
                    var black_name_div = document.getElementById("black_name");
                    var pgn_div = document.getElementById("game_pgn");
                    observe_game(board, "{game_id}", status_div, white_name_div, black_name_div, pgn_div);
                }}
            </script>
            </body>
            </html>
        """.format(title=title, game_id=self.game.id, game_pgn=str(self.game.pgn), game_status=self.game.outcome_str())

        return html.encode('utf8')



