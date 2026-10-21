from gi.repository import Adw, Gtk

from panapidas.widget.copy_code import CopyCode

@Gtk.Template(
    resource_path="/eltonarodrigues/org/codeberg/panapidas/page/script_info_page.ui"
)
class ScripInfoPage(Adw.PreferencesDialog):
    __gtype_name__ = "ScripInfoPage"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)