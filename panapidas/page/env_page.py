from gi.repository import Adw, Gtk, GObject, Gio

from panapidas.model.env_object import EnvObject
from panapidas.widget.change_value_dialog import ChangeValueDialog

MOUSE_CLICK = 1


@Gtk.Template(resource_path="/eltonarodrigues/org/codeberg/panapidas/page/env_page.ui")
class EnvPage(Adw.NavigationPage):
    __gtype_name__ = "EnvPage"

    __gsignals__ = {
        "env-selected": (GObject.SignalFlags.RUN_FIRST, None, (EnvObject,)),
        "env-saved": (GObject.SignalFlags.RUN_FIRST, None, ()),
    }

    list_envs = Gtk.Template.Child()
    delete_env_dialog = Gtk.Template.Child()

    def __init__(self, env_store: Gio.ListStore = None, **kwargs):
        super().__init__(**kwargs)

        self.delete_env_dialog.signal_id = self.delete_env_dialog.connect(
            "response", self._on_deleted_row
        )

        self.env_store: Gio.ListStore = env_store

        self.selection = Gtk.SingleSelection.new(self.env_store)
        self.list_envs.set_model(self.selection)

    @Gtk.Template.Callback()
    def on_create_env(self, widget: Gtk.Button):
        self.env_store.append(EnvObject(name="New Environment"))
        self.emit("env-saved")

    @Gtk.Template.Callback()
    def on_setup_factory(self, _: Gtk.SignalListItemFactory, list_item: Gtk.ListItem):
        row = Gtk.CenterBox()
        row.set_start_widget(
            Gtk.Label(
                label="New Environment",
                margin_start=20,
                halign=Gtk.Align.FILL,
                hexpand=True,
                xalign=0,
            )
        )
        list_item.set_child(row)

    @Gtk.Template.Callback()
    def on_bind_factory(
        self, factory: Gtk.SignalListItemFactory, list_item: Gtk.ListItem
    ):
        row = list_item.get_child()
        env_object = list_item.get_item()

        toggle_env = Gtk.ToggleButton(icon_name="go-next-symbolic", valign="center")
        toggle_env.set_css_classes(["flat"])
        toggle_env.connect("clicked", self._on_select_env, None, None, None, env_object)

        delete_button = Gtk.Button(icon_name="user-trash-symbolic", valign="center")
        delete_button.set_css_classes(["flat"])
        delete_button.connect("clicked", self._on_delete_row, env_object)

        rename_button = Gtk.Button(icon_name="adw-entry-edit-symbolic", valign="center")
        rename_button.set_css_classes(["flat"])

        control_box = Gtk.Box(
            orientation=Gtk.Orientation.HORIZONTAL, spacing=6, margin_end=20
        )
        control_box.append(delete_button)
        control_box.append(rename_button)
        control_box.append(toggle_env)
        row.set_end_widget(control_box)

        label = row.get_first_child()
        label.set_text(env_object.name)

        gesture = Gtk.GestureClick()
        gesture.set_button(MOUSE_CLICK)
        gesture.connect("pressed", self._on_select_env, env_object)
        label.add_controller(gesture)

        env_object.connect(
            "notify::name",
            lambda env_object, _pspec, label: label.set_text(env_object.name),
            label,
        )
        list_item.control_box = control_box
        list_item.toggle_button = toggle_env
        list_item.rename_button = rename_button
        list_item.rename_handler = rename_button.connect(
            "clicked", self._on_rename_env, env_object
        )

    @Gtk.Template.Callback()
    def on_unbind_factory(self, _, list_item: Gtk.ListItem):
        control_box = getattr(list_item, "control_box", None)

        if control_box is None:
            return

        toggle_env = list_item.toggle_button
        rename_button = list_item.rename_button

        toggle_handler = getattr(list_item, "toggle_handler", None)

        if toggle_handler is not None:
            toggle_env.disconnect(toggle_handler)

        rename_handler = getattr(list_item, "rename_handler", None)
        if rename_handler is not None:
            rename_button.disconnect(rename_handler)

        row = list_item.get_child()
        row.set_end_widget(None)
        row.set_start_widget(None)
        list_item.control_box = None
        list_item.toggle_handler = None
        list_item.rename_handler = None

    def _on_deleted_row(self, widget: Gtk.AlertDialog, response_name: str):
        finded, position = self.env_store.find(self.delete_env_dialog.object)

        if response_name == "cancel":
            widget.disconnect(widget.signal_id)
            return

        if response_name != "delete":
            return

        if not finded:
            print("EnvObject not found in the store.")
            return

        self.env_store.remove(position)
        self.emit("env-saved")

    def _on_delete_row(self, widget: Gtk.Button, env_object: EnvObject):
        self.delete_env_dialog.object = env_object
        self.delete_env_dialog.present()

    def _on_rename_requested(
        self, widget: ChangeValueDialog, response_name: str, env_object: EnvObject
    ):
        if response_name != "save":
            return

        finded, position = self.env_store.find(env_object)

        if not finded:
            print("EnvObject not found in the store.")
            return

        env_group = self.env_store.get_item(position)
        env_group.name = widget.get_value()
        self.emit("env-saved")

    def _on_rename_env(self, widget: Gtk.Button, env_object: EnvObject):
        dialog = ChangeValueDialog(
            value=env_object.name,
            heading="Rename Environment",
            body="Change the name of the environment group.",
        )
        dialog.connect("response", self._on_rename_requested, env_object)
        dialog.present(self)

    def _on_select_env(
        self,
        _gesture: Gtk.GestureClick,
        _n_press: int,
        _x: float,
        _y: float,
        env_object: EnvObject,
    ):
        self.emit("env-selected", env_object)
