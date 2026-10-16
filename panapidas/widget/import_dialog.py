import json

from gi.repository import Adw, GObject, Gio, Gtk


@Gtk.Template(
    resource_path="/eltonarodrigues/org/codeberg/panapidas/widget/import_dialog.ui"
)
class ImportDialog(Adw.Dialog):
    __gtype_name__ = "ImportDialog"

    __gsignals__ = {
        "import-file-selected": (GObject.SignalFlags.RUN_FIRST, None, (str,)),
    }

    def __init__(self):
        super().__init__()

        self.file_dialog = Gtk.FileDialog()


    def _on_collection_opened(self, dialog: Gtk.FileDialog, result: Gio.AsyncResult):
        file = dialog.open_finish(result)
        import_path = file.get_path()
        self.emit("import-file-selected", import_path)

    @Gtk.Template.Callback()
    def on_import_collection(self, widget: Gtk.Button):
        self.file_dialog.open(self.get_root(), None, self._on_collection_opened)
