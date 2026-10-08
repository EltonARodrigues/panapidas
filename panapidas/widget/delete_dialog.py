from gi.repository import Adw, Gtk


@Gtk.Template(
    resource_path="/eltonarodrigues/org/codeberg/panapidas/widget/delete_dialog.ui"
)
class DeleteDialog(Adw.AlertDialog):
    __gtype_name__ = "DeleteDialog"

    def __init__(self, body: str):
        super().__init__(body=body)