import gi

gi.require_version("Gtk", "4.0")
from gi.repository import GObject

class Request(GObject.GObject):
    __gtype_name__ = 'Request'

    def __init__(self, name):
        super().__init__()
        self.name = name

class RequestGroup(GObject.GObject):
    __gtype_name__ = 'RequestGroup'

    def __init__(self, name, children=[]):

        super().__init__()
        self.name = name
        self.children = children
