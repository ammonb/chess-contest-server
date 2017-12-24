from twisted.web.resource import Resource
from twisted.web.resource import NoResource

class Tournament(Resource):
    isLeaf = True
    def __init__(self, manager, tournament):
        self.children = []
        self.manager = manager
        self.tournament = tournament

    def render_GET(self, request):
        return "<html><head><h1>This is a tournament named %s</h1></head></html>" % (self.tournament.name)


class TournamentsList (Resource):
    def __init__(self, manager):
        self.children = []
        self.manager = manager

    def getChild(self, name, request):
        if name == '':
            return self
        if self.manager.tournaments.get(name):
            return Tournament(self.manager, self.manager.tournaments.get(name))
        else:
            return NoResource()

    def render_GET(self, request):
        body = ""

        if len(self.manager.tournaments):
            body = "<ul>"
            for t in self.manager.tournaments.values():
                body += "<li><a href='/tournaments/%s'>%s</a></li>" % (t.name, t.name)
            body += "</ul>"
        else:
            body = "<h2>No Tournaments :(</h2>"

        return "<html><head><h1>Tournaments</h1></head>%s</html>" % (body,)


class HttpRoot(Resource):
    def __init__(self, manager):
        self.children = []
        self.manager = manager

    def getChild(self, name, request):
        if name == '':
            return self
        elif name == 'tournaments':
            return TournamentsList(self.manager)
        else:
            return NoResource()

    def render_GET(self, request):
        return "<html><h1>Triplebyte Chess Server!</h1><p>Tournaments are <a href='/tournaments'>here</a></p></html>"
