from gi.repository import Adw, GLib, Gtk, GObject, Gio

from panapidas.model.env_object import EnvObject


@Gtk.Template(
    resource_path="/eltonarodrigues/org/codeberg/panapidas/page/env_page.ui"
)
class EnvPage(Adw.NavigationPage):
    __gtype_name__ = "EnvPage"

    __gsignals__ = {
        "env-selected": (GObject.SignalFlags.RUN_FIRST, None, (EnvObject,)),
    }

    list_envs = Gtk.Template.Child()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.selected_env = "123"

    def _on_create_list_row(self, env_object: EnvObject):
        toggle_env = Gtk.ToggleButton(icon_name="go-next-symbolic", valign= "center")
        toggle_env.set_css_classes(["flat"])
        toggle_env.connect("clicked", self.on_select_env, env_object)
        row = Adw.ActionRow(title=env_object.name, activatable_widget=toggle_env)
        row.add_suffix(toggle_env)
        return row


    def set_envs(self, env_store: Gio.ListStore):
        self.model = Gtk.SingleSelection(model=env_store)
        self.list_envs.bind_model(self.model, self._on_create_list_row)

    def get_selected_env(self):
        return self.selected_env

    def on_select_env(self, _: Gtk.ToggleButton, env_object: EnvObject):
        self.emit("env-selected", env_object)
