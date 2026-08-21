from gi.repository import Adw, Gtk


@Gtk.Template(
    resource_path="/eltonarodrigues/org/codeberg/panapidas/widget/rename_dialog.ui"
)
class RenameDialog(Adw.AlertDialog):
    __gtype_name__ = "RenameDialog"

    rename_entry = Gtk.Template.Child()

    def __init__(self, heading: str, body: str, name: str, **kwargs):
        super().__init__(heading=heading, body=body, **kwargs)
        self.rename_entry.set_text(name)
        self.new_name = name

    def get_new_name(self) -> str:
        return self.rename_entry.get_text()

    @Gtk.Template.Callback()
    def on_rename_change(self, widget: Gtk.Button):
        self.new_name = self.get_new_name()
