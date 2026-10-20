from gi.repository import Adw, Gtk, GObject

from panapidas.widget.map_list_menu import MapListMenu
from panapidas.model.env_object import ActiveEnvs, EnvObject


@Gtk.Template(
    resource_path="/eltonarodrigues/org/codeberg/panapidas/page/env_config_page.ui"
)
class EnvConfigPage(Adw.NavigationPage):
    __gtype_name__ = "EnvConfigPage"

    __gsignals__ = {
        "env-saved": (GObject.SignalFlags.RUN_FIRST, None, ()),
    }

    env_list = Gtk.Template.Child()
    save_env_button = Gtk.Template.Child()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.params = None
        self.env_object = None

    def set_env(self, env_object: EnvObject):
        self.env_object = env_object
        self.params = MapListMenu(self.env_list, env_object.envs, None, False, False)
        self.params.connect("map-changed", self._on_map_change)

    def _on_map_change(self, widget: MapListMenu):
        self.env_object.envs = widget.get_map_entry()
        self.save_env_button.set_sensitive(True)

    @Gtk.Template.Callback()
    def on_env_save(self, _: Gtk.Button):
        active_envs = ActiveEnvs()
        if active_envs.id == self.env_object.id:
            active_envs.initialize(
                self.env_object.id, self.env_object.name, self.env_object.envs
            )
        self.emit("env-saved")
