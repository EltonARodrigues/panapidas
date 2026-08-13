from gi.repository import Adw, GLib, Gtk, GObject

from panapidas.widget.map_list_menu import MapListMenu
from panapidas.widget.body_source_view import BodySourceView
from panapidas.request.http_request import request, Response
from panapidas.model.requests import Request


@Gtk.Template(
    resource_path="/eltonarodrigues/org/codeberg/panapidas/page/env_config_page.ui"
)
class EnvConfigPage(Adw.NavigationPage):
    __gtype_name__ = "EnvConfigPage"

    env_list = Gtk.Template.Child()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.env_group = None

        self.params = MapListMenu(self.env_list, [])
        self.params.connect("map-changed", self._on_map_change)

    def _on_map_change(self, widget: MapListMenu):
        self.env_list = widget.get_map_entry()
