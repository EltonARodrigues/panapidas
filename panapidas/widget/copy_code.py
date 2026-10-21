from gi.repository import GObject, Gdk, Gtk


@Gtk.Template(
    resource_path="/eltonarodrigues/org/codeberg/panapidas/widget/copy_code.ui"
)
class CopyCode(Gtk.Box):
    __gtype_name__ = "CopyCode"

    text_label = Gtk.Template.Child()

    _code_text = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    @GObject.Property(type=str, default="")
    def code_text(self):
        return self._code_text

    @code_text.setter
    def code_text(self, value):
        self.text_label.set_label(value)
        self._code_text = value

    @Gtk.Template.Callback()
    def copy_text(self, _widget: Gtk.Button):
        clipboard = self.get_clipboard()
        clipboard.set(self._code_text)
