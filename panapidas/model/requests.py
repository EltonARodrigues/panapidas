import gi

gi.require_version("Gtk", "4.0")
from gi.repository import GObject

from panapidas.model.map_entry import MapEntry

class Request(GObject.GObject):
    __gtype_name__ = 'Request'

    def __init__(
        self,
        name: str,
        method: str,
        url: str,
        headers: MapEntry,
        body,
        params: MapEntry
    ):
        super().__init__()
        self.name = name
        self.url = url
        self.method = method
        self.headers = headers
        self.params = params
        self.body = body

class RequestGroup(GObject.GObject):
    __gtype_name__ = 'RequestGroup'

    def __init__(self, name, children=[]):

        super().__init__()
        self.name = name
        self.children = children
