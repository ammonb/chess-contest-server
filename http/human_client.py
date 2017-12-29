from twisted.web.resource import Resource
from twisted.web.resource import NoResource
from twisted.web.static import File


class HumanClient(Resource):
    def __init__(self, tournament):
        self.tournament = tournament
        self.children = []

    def getChild(self, name, request):
        if name == '':
            return self
        else:
            return NoResource()

    def render_GET(self, request):
        html = """
            <html>
            <head>
            <base href="/static/">
            <title>Play in tournament {tournament_name}</title>
            <link rel="stylesheet" href="/static/css/chessboard-0.3.0.css" />
            </head>
            <body>
            <h2>Play in tournament {tournament_name}</h2>
            Player name:
            <input type="text" id="player_name"><br>
            <button type="button" id="join_button" onclick="join_tournament();">Join tournament</button><br><br>

            <div id="white_name"></div>
            <div id="black_name"></div>
            <div id="board" style="width: 400px"></div>
            <h3><div id="status_div">Not connected</div></h3>

            <script src="js/jquery-3.2.1.js"></script>
            <script src="js/chessboard-0.3.0.js"></script>
            <script src="js/game_lib.js"></script>
            <script>
                function join_tournament() {{
                    var status_div = document.getElementById("status_div");
                    var white_name_div = document.getElementById("white_name");
                    var black_name_div = document.getElementById("black_name");
                    var join_button = document.getElementById("join_button");
                    var player_name = document.getElementById("player_name").value;
                    play_games("{tournament_name}", player_name, join_button, status_div, white_name_div, black_name_div);
                }}
            </script>
            </body>
            </html>
        """.format(tournament_name=self.tournament.name)

        # var status_div = document.getElementById("status_div");
        # var white_name_div = document.getElementById("white_name");
        # var black_name_div = document.getElementById("black_name");
        # var pgn_div = document.getElementById("game_pgn");
        # observe_game(board, "{game_id}", status_div, white_name_div, black_name_div, pgn_div);

        return html.encode('utf8')
