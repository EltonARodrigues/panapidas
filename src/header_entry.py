import gi
from gi.repository import Gtk, GObject


class HeaderEntry(Gtk.Entry):
    __gtype_name__ = "HeaderEntry"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._header_id = None
        self._is_header = True

    @GObject.Property(type=int)
    def header_id(self):
        return self._header_id

    @GObject.Property(type=bool)
    def is_header(self):
        return self._is_header

    @header_id.setter
    def header_id(self, value):
        self._header_id = value

