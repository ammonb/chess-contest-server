import cgi
import urllib

def html_escape(s):
    return cgi.escape(s).encode("utf-8")

def url_escape(s):
    return urllib.quote(s.encode("utf-8"),  safe='')


