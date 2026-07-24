import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk

@Gtk.Template(
    resource_path="/eltonarodrigues/org/codeberg/panapidas/widget/item_popover.ui"
)
class ItemPopover(Gtk.PopoverMenu):
    __gtype_name__ = "ItemPopover"

    def __init__(self):
        super().__init__()

        self.set_position(Gtk.PositionType.RIGHT)

