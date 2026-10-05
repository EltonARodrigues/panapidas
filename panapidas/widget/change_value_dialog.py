from gi.repository import Adw, Gtk


@Gtk.Template(
    resource_path="/eltonarodrigues/org/codeberg/panapidas/widget/change_value_dialog.ui"
)
class ChangeValueDialog(Adw.AlertDialog):
    __gtype_name__ = "ChangeValueDialog"

    value_entry = Gtk.Template.Child()

    def __init__(self, heading: str, body: str, value: str, **kwargs):
        super().__init__(heading=heading, body=body, **kwargs)
        self.value_entry.set_text(value or "")
        self._value = value

    def get_value(self) -> str:
        return self.value_entry.get_text()

    @Gtk.Template.Callback()
    def on_change_value(self, widget: Gtk.Button):
        self._value = self.get_value()
