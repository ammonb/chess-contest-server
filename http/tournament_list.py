from twisted.web.resource import Resource
from twisted.web.resource import NoResource
from twisted.web.static import File
from twisted.web.util import redirectTo

from tournament import Tournament


class NewTournament(Resource):
    isLeaf = True
    def __init__(self, manager):
        self.children = []
        self.manager = manager

    def render_POST(self, request):
        message = ""
        try:
            name = request.args['name'][0].strip()
            time_limit = float(request.args['time_limit'][0])
            increment = float(request.args['increment'][0])
            games_per_pair = int(request.args['games_per_pair'][0])
            self.manager.create_tournament(name, games_per_pair, time_limit, increment)
            return redirectTo("/tournaments/%s" % (name,), request)

        except ValueError, e:
            message = "Error: bad values for games_per_pair, time_limit or increment"
        except AssertionError, e:
            message = "Error: " + e.message

        request.setResponseCode(400)
        return "<html><head><h2>%s</h2></head><body></body></html>" % (message,)


class TournamentList (Resource):
    def __init__(self, manager):
        self.children = []
        self.manager = manager

    def getChild(self, name, request):
        if name == '':
            return self
        elif name == 'new':
            return NewTournament(self.manager)
        elif self.manager.tournaments.get(name):
            return Tournament(self.manager, self.manager.tournaments.get(name))
        else:
            return NoResource()

    def render_GET(self, request):
        request.setHeader("Content-Type", "text/html; charset=utf-8")

        tournament_html = ""
        if len(self.manager.tournaments):
            tournaments = sorted(self.manager.tournaments.values(), key=lambda t:t.created_at, reverse=True)

            tournament_html = "<ul>"
            for t in tournaments:
                tournament_html += "<li><a href='/tournaments/%s'>%s</a> (%s games,  %s active players)</li>" % (t.name, t.name, len(t.all_games()), len(t.players))
            tournament_html += "</ul>"
        else:
            tournament_html = "<h2>No Tournaments :(</h2>"


        form_html = """
        <form action="/tournaments/new" method="post">
            Tournament name:
            <input type="text" name="name"><br>
            Time limit (seconds):
            <input type="text" name="time_limit"><br>
            Increment (seconds):
            <input type="text" name="increment"><br>
            Games per pairing:
            <input type="text" name="games_per_pair"><br>
            <input type="submit" value="Submit">
        </form>"""

        html = "<html><head><h1>Tournaments</h1></head><body>%s<h2>Create new tournament</h2>%s</body></html>" % (tournament_html, form_html)
        return html.encode('utf8')
