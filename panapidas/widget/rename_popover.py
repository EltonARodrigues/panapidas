import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Gio, GObject, GLib

from panapidas.model.requests import Request, RequestGroup, RequestItem

@Gtk.Template(
    resource_path="/eltonarodrigues/org/codeberg/panapidas/widget/rename_popover.ui"
)
class RenamePopover(Gtk.Popover):
    __gtype_name__ = "RenamePopover"

    save_new_name = Gtk.Template.Child()

    def __init__(self):
        super().__init__()

        self.set_position(Gtk.PositionType.RIGHT)
        self.save_new_name.set_action_name('app.rename-item')

    def set_rename_item(self, item: RequestItem):
        self.item = item

    @Gtk.Template.Callback()
    def on_rename_change(self, widget):
        self._rename = widget.get_text()
        item_id = GLib.Variant.new_string(self.item.id)
        new_name = GLib.Variant.new_string(self._rename)
        target = GLib.Variant.new_tuple(item_id, new_name)
        self.save_new_name.set_action_target_value(target)

