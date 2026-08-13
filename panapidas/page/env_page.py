import threading
from concurrent.futures import ThreadPoolExecutor, Future

from gi.repository import Adw, GLib, Gtk, GObject

from panapidas.widget.map_list_menu import MapListMenu
from panapidas.widget.body_source_view import BodySourceView
from panapidas.request.http_request import request, Response
from panapidas.model.requests import Request


@Gtk.Template(
    resource_path="/eltonarodrigues/org/codeberg/panapidas/page/env_page.ui"
)
class EnvPage(Adw.NavigationPage):
    __gtype_name__ = "EnvPage"

    __gsignals__ = {
        "env-selected": (GObject.SignalFlags.RUN_FIRST, None, ()),
    }

    env_multi_layer_view = Gtk.Template.Child()
    list_env_view = Gtk.Template.Child()
    list_envs = Gtk.Template.Child()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.selected_env = "123"

        toggle_env = Gtk.ToggleButton(icon_name="go-next-symbolic", valign= "center")
        toggle_env.connect("clicked", self.on_select_env)
        env_row = Adw.ActionRow(title="Env 4", activatable_widget= toggle_env)
        env_row.add_suffix(toggle_env)
        self.list_envs.append(env_row)

    def get_selected_env(self):
        return self.selected_env

    def on_select_env(self, widget):
        self.emit("env-selected")
