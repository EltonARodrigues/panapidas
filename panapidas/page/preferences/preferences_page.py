
from gi.repository import Adw, Gtk, GObject

from panapidas.widget.map_list_menu import MapListMenu
from panapidas.model.env_object import EnvObject


@Gtk.Template(
    resource_path="/eltonarodrigues/org/codeberg/panapidas/page/preferences_page.ui"
)
class PreferencesPage(Adw.Dialog):
    __gtype_name__ = "PreferencesDialog"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
